from __future__ import annotations

import argparse
import json
import math
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

import numpy as np
import pandas as pd

ATOL = 2e-9
RTOL = 2e-9
ROOT = Path(__file__).resolve().parents[1]
FROZEN_MANIFEST = ROOT / "checksums" / "frozen_results.sha256"


def fail(msg: str) -> None:
    raise AssertionError(msg)


def close_float(a: float, b: float) -> bool:
    if math.isnan(a) or math.isnan(b):
        return math.isnan(a) and math.isnan(b)
    if math.isinf(a) or math.isinf(b):
        return a == b
    scale = max(1.0, abs(a), abs(b))
    return abs(a - b) <= ATOL + RTOL * scale


def compare_csv(ref: Path, cand: Path, rel: str) -> tuple[float, float]:
    a = pd.read_csv(ref)
    b = pd.read_csv(cand)
    if list(a.columns) != list(b.columns):
        fail(f"{rel}: column mismatch")
    if a.shape != b.shape:
        fail(f"{rel}: shape mismatch {a.shape} != {b.shape}")
    max_abs = 0.0
    max_scaled = 0.0
    for col in a.columns:
        an = pd.api.types.is_numeric_dtype(a[col])
        bn = pd.api.types.is_numeric_dtype(b[col])
        if an != bn:
            fail(f"{rel}:{col}: numeric/non-numeric type mismatch")
        if not an:
            av = a[col].astype("string").fillna("<NA>").to_numpy()
            bv = b[col].astype("string").fillna("<NA>").to_numpy()
            if not np.array_equal(av, bv):
                fail(f"{rel}:{col}: text/order mismatch")
            continue
        if pd.api.types.is_integer_dtype(a[col]) and pd.api.types.is_integer_dtype(b[col]):
            if not np.array_equal(a[col].to_numpy(), b[col].to_numpy()):
                fail(f"{rel}:{col}: integer mismatch")
            continue
        av = a[col].to_numpy(dtype=float)
        bv = b[col].to_numpy(dtype=float)
        if not np.array_equal(np.isnan(av), np.isnan(bv)):
            fail(f"{rel}:{col}: NaN pattern mismatch")
        if not np.array_equal(np.isposinf(av), np.isposinf(bv)) or not np.array_equal(np.isneginf(av), np.isneginf(bv)):
            fail(f"{rel}:{col}: infinity pattern mismatch")
        finite = np.isfinite(av) & np.isfinite(bv)
        if finite.any():
            diff = np.abs(av[finite] - bv[finite])
            scale = np.maximum(1.0, np.maximum(np.abs(av[finite]), np.abs(bv[finite])))
            max_abs = max(max_abs, float(diff.max()))
            max_scaled = max(max_scaled, float((diff / scale).max()))
            if not np.all(diff <= ATOL + RTOL * scale):
                idx_local = int(np.argmax(diff - (ATOL + RTOL * scale)))
                fail(
                    f"{rel}:{col}: numerical mismatch; "
                    f"a={av[finite][idx_local]!r}, b={bv[finite][idx_local]!r}, "
                    f"abs={diff[idx_local]:.3g}, scaled={diff[idx_local]/scale[idx_local]:.3g}"
                )
    return max_abs, max_scaled


def compare_json_value(a, b, path: str, stats: dict[str, float]) -> None:
    if isinstance(a, bool) or isinstance(b, bool) or a is None or b is None:
        if a != b:
            fail(f"{path}: value mismatch {a!r} != {b!r}")
        return
    if isinstance(a, int) and isinstance(b, int):
        if a != b:
            fail(f"{path}: integer mismatch {a} != {b}")
        return
    if isinstance(a, (int, float)) and isinstance(b, (int, float)):
        af, bf = float(a), float(b)
        if not close_float(af, bf):
            fail(f"{path}: numerical mismatch {af!r} != {bf!r}")
        if math.isfinite(af) and math.isfinite(bf):
            diff = abs(af - bf)
            scale = max(1.0, abs(af), abs(bf))
            stats["max_abs"] = max(stats["max_abs"], diff)
            stats["max_scaled"] = max(stats["max_scaled"], diff / scale)
        return
    if isinstance(a, str) and isinstance(b, str):
        if a != b:
            fail(f"{path}: string mismatch")
        return
    if isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b):
            fail(f"{path}: list length mismatch")
        for i, (x, y) in enumerate(zip(a, b)):
            compare_json_value(x, y, f"{path}[{i}]", stats)
        return
    if isinstance(a, dict) and isinstance(b, dict):
        if list(a.keys()) != list(b.keys()):
            fail(f"{path}: key/order mismatch")
        for k in a:
            compare_json_value(a[k], b[k], f"{path}.{k}", stats)
        return
    fail(f"{path}: type mismatch {type(a).__name__} != {type(b).__name__}")


def compare_json(ref: Path, cand: Path, rel: str) -> tuple[float, float]:
    a = json.loads(ref.read_text(encoding="utf-8"))
    b = json.loads(cand.read_text(encoding="utf-8"))
    stats = {"max_abs": 0.0, "max_scaled": 0.0}
    compare_json_value(a, b, rel, stats)
    return stats["max_abs"], stats["max_scaled"]


def frozen_relpaths() -> list[str]:
    rels = []
    for line in FROZEN_MANIFEST.read_text(encoding="utf-8").splitlines():
        if line.strip():
            _, rel = line.split("  ", 1)
            rels.append(rel)
    return rels


def compare_tree(reference: Path, candidate: Path) -> None:
    worst_abs = (0.0, "")
    worst_scaled = (0.0, "")
    structured = 0
    rendered = 0
    for rel in frozen_relpaths():
        ref = reference / rel
        cand = candidate / rel
        if not cand.is_file():
            fail(f"MISSING regenerated file: {rel}")
        ext = ref.suffix.lower()
        if ext == ".csv":
            ma, ms = compare_csv(ref, cand, rel)
            structured += 1
        elif ext == ".json":
            ma, ms = compare_json(ref, cand, rel)
            structured += 1
        elif ext in {".png", ".pdf"}:
            if cand.stat().st_size <= 0:
                fail(f"{rel}: regenerated figure is empty")
            rendered += 1
            continue
        else:
            fail(f"Unsupported frozen-result type in comparator: {rel}")
        if ma > worst_abs[0]:
            worst_abs = (ma, rel)
        if ms > worst_scaled[0]:
            worst_scaled = (ms, rel)
    print("Regenerated-result verification: PASS")
    print(f"Structured outputs compared: {structured}")
    print(f"Rendered figures regenerated/non-empty: {rendered}")
    print(f"Tolerance: atol={ATOL:g}, rtol={RTOL:g} with scale=max(1,|a|,|b|)")
    print(f"Maximum absolute numerical difference: {worst_abs[0]:.17g} ({worst_abs[1] or 'none'})")
    print(f"Maximum scaled numerical difference: {worst_scaled[0]:.17g} ({worst_scaled[1] or 'none'})")


def reproduce_and_compare() -> None:
    with tempfile.TemporaryDirectory(prefix="living-review-repro-") as td:
        dst = Path(td) / "repo"
        shutil.copytree(ROOT, dst, ignore=shutil.ignore_patterns(".git", "__pycache__"))
        subprocess.run([sys.executable, "model/verify_symbolic.py"], cwd=dst, check=True)
        subprocess.run([sys.executable, "analysis/run_analysis.py"], cwd=dst, check=True)
        compare_tree(ROOT, dst)


def main() -> None:
    parser = argparse.ArgumentParser(description="Regenerate the frozen analysis in isolation and compare scientifically meaningful outputs.")
    parser.add_argument("--candidate", type=Path, help="Compare an already-regenerated repository tree instead of running the analysis.")
    args = parser.parse_args()
    if args.candidate:
        compare_tree(ROOT, args.candidate.resolve())
    else:
        reproduce_and_compare()


if __name__ == "__main__":
    main()
