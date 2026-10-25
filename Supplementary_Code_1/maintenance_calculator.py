#!/usr/bin/env python3
"""Implement the manuscript's exponential maintenance model in dimensional units.

This is a revision-stage implementation, not a new empirical model or a replacement
for the original R/Python archive. Only the Python standard library is required.
Run: python maintenance_calculator.py example_B_base.json --output result.json
"""
from __future__ import annotations
import argparse
import json
import math
from pathlib import Path
from typing import Any


def stale_average(x: float) -> float:
    """Average stale fraction for a dimensionless fixed interval x >= 0."""
    if not math.isfinite(x) or x < 0:
        raise ValueError("The interval must be finite and nonnegative.")
    if x < 1e-4:
        # Stable expansion of 1 - (1 - exp(-x))/x, including its limit at zero.
        return x * (0.5 + x * (-1/6 + x * (1/24 + x * (-1/120 + x/720))))
    return 1.0 + math.expm1(-x) / x


def checking_equation(x: float) -> float:
    """h(x) = 1 - (1+x)exp(-x), evaluated without small-x cancellation."""
    if not math.isfinite(x) or x < 0:
        raise ValueError("The interval must be finite and nonnegative.")
    if x < 1e-3:
        return x*x * (0.5 + x * (-1/3 + x * (1/8 + x * (-1/30 + x * (1/144 - x/840)))))
    return -math.expm1(-x) - x * math.exp(-x)


def optimum(ratio: float) -> dict[str, Any]:
    """Return the exact-objective infimum and whether a finite interval attains it.

    Boundary infima are not operational recommendations to update instantly or stop.
    Bisection solves the monotone equation in the finite-optimum domain.
    """
    if not math.isfinite(ratio) or ratio < 0:
        raise ValueError("The fixed-cost ratio must be finite and nonnegative.")
    if ratio == 0:
        return {"status": "unattained_zero_interval_limit", "interval": None, "minimum": 0.0}
    if ratio >= 1:
        return {"status": "unattained_infinite_interval_limit", "interval": None, "minimum": 1.0}
    lo, hi = 0.0, 1.0
    while checking_equation(hi) < ratio:
        hi *= 2.0
    for _ in range(160):
        mid = (lo + hi) / 2.0
        if mid == lo or mid == hi:
            break
        if checking_equation(mid) < ratio:
            lo = mid
        else:
            hi = mid
    x = (lo + hi) / 2.0
    return {"status": "finite_optimum", "interval": x, "minimum": -math.expm1(-x)}


def numeric(p: dict[str, Any], name: str, *, positive: bool = False) -> float:
    value = p.get(name)
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{name} must be a number, not a missing value or boolean.")
    value = float(value)
    if not math.isfinite(value) or (value <= 0 if positive else value < 0):
        raise ValueError(f"{name} must be finite and {'positive' if positive else 'nonnegative'}.")
    return value


def classify(advantage: float) -> str:
    # This display tolerance is not the mathematical strict-inequality rule.
    if abs(advantage) <= 1e-12:
        return "numerically_indistinguishable_at_1e-12_normalized_tolerance"
    return "living_lower_burden" if advantage > 0 else "scheduled_lower_burden"


def calculate(payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, dict) or not isinstance(payload.get("parameters"), dict):
        raise ValueError("Input must contain a parameters object.")
    p = payload["parameters"]
    mu = numeric(p, "mu", positive=True)
    S = numeric(p, "scheduled_reset")
    F = numeric(p, "shared_rate")
    alpha = numeric(p, "attributable_fraction")
    if alpha > 1:
        raise ValueError("attributable_fraction must be at most one.")
    n = p.get("portfolio_size")
    if isinstance(n, bool) or not isinstance(n, int) or n < 1:
        raise ValueError("portfolio_size must be a positive integer.")
    f = numeric(p, "readiness_rate")
    CS = numeric(p, "processing_scheduled")
    CL = numeric(p, "processing_living")
    D = numeric(p, "decision_rate", positive=True)
    H = numeric(p, "loss_per_stale_decision", positive=True)
    delta = numeric(p, "living_interval", positive=True)
    RL = numeric(p, "living_release")
    individual = p.get("incremental_shared_rate") is not None
    shared = numeric(p, "incremental_shared_rate") if individual else alpha * F / n
    Q = D * H
    rho, d, phi, eta, dc, psi = S*mu/Q, mu*delta, shared/Q, f/Q, (CL-CS)/Q, RL*mu/Q
    if not all(map(math.isfinite, [Q, rho, d, phi, eta, dc, psi])) or Q <= 0 or d <= 0:
        raise ValueError("Input scale causes overflow or underflow; rescale the common burden/time units.")
    scheduled = optimum(rho)
    living = optimum(psi)
    scheduled["calendar_interval"] = None if scheduled["interval"] is None else scheduled["interval"] / mu
    scheduled["total_burden_infimum_rate"] = CS + Q * scheduled["minimum"]
    living["calendar_interval"] = None if living["interval"] is None else living["interval"] / mu
    b = phi + eta + dc
    fixed_incremental = b + stale_average(d) + psi/d
    fixed_advantage = scheduled["minimum"] - fixed_incremental
    margin = scheduled["minimum"] - eta - dc - stale_average(d) - psi/d
    optimized_advantage = scheduled["minimum"] - (b + living["minimum"])
    fixed_status = classify(fixed_advantage) if scheduled["status"] == "finite_optimum" else "no_attained_scheduled_optimum_compare_infima_only"
    optimized_status = classify(optimized_advantage) if scheduled["status"] == living["status"] == "finite_optimum" else "one_or_both_optima_unattained_compare_infima_only"
    frontier = {"applicable": not individual and scheduled["status"] == "finite_optimum", "continuous": None, "minimum_integer": None}
    if frontier["applicable"] and margin > 0:
        threshold = alpha*F/(Q*margin)
        frontier.update(continuous=threshold, minimum_integer=max(1, math.floor(threshold)+1))
    elif frontier["applicable"]:
        frontier["reason"] = "no_positive_margin_for_strict_advantage"
    else:
        frontier["reason"] = "single_review_increment_or_boundary_comparison"
    return {
        "model": "exponential stationary operating model; same resource/consequence scale",
        "units": payload.get("units", {}),
        "input_kind": payload.get("input_kind", "user-specified; empirical status not inferred"),
        "unit_of_decision": "single_review_actual_increment" if individual else "equal_sharing_comparable_portfolio",
        "normalized": {"Q": Q, "rho": rho, "d": d, "phi": phi, "eta": eta, "delta_c": dc, "psi": psi},
        "scheduled": scheduled,
        "fixed_living": {"total_burden_rate": CS+Q*fixed_incremental, "incremental_normalized_burden": fixed_incremental,
            "available_infrastructure_margin": margin, "normalized_advantage": fixed_advantage, "comparison": fixed_status},
        "optimized_living": {**living, "total_burden_infimum_rate": CS+Q*(b+living["minimum"]),
            "normalized_advantage": optimized_advantage, "comparison": optimized_status},
        "fixed_interval_portfolio_frontier": frontier,
        "cautions": ["No empirical default, budget feasibility or quality validation is implied.",
                     "Count economic opportunity costs, not only changed cash spending; avoid duplicate costs and overlapping portfolio consequences.",
                     "Complete freshness at release, stationary inputs and a common loss scale are model assumptions.",
                     "A boundary infimum is not a recommended implementable update policy.",
                     "Scenario grids describe checked points only, not continuous-range robustness or probabilities."]}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--sweep-loss", type=float, nargs="+", help="Evaluate discrete loss-per-stale-decision values, recomputing all normalized ratios.")
    args = parser.parse_args()
    try:
        payload = json.loads(args.input.read_text(encoding="utf-8"))
        if args.sweep_loss:
            results=[]
            for value in args.sweep_loss:
                scenario={**payload,"parameters":{**payload["parameters"],"loss_per_stale_decision":value}}
                results.append({"loss_per_stale_decision":value,"result":calculate(scenario)})
            result={"scope":"Discrete scenarios only; no probability or continuous-range robustness claim.","scenarios":results}
        else:
            result=calculate(payload)
        text=json.dumps(result, indent=2, allow_nan=False)
        if args.output:
            args.output.parent.mkdir(parents=True,exist_ok=True)
            args.output.write_text(text+"\n",encoding="utf-8")
        else:
            print(text)
    except (OSError, ValueError, TypeError, KeyError, OverflowError, ZeroDivisionError) as error:
        parser.exit(2, f"Input/calculation error: {error}\n")

if __name__ == "__main__":
    main()
