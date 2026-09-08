from __future__ import annotations
import hashlib
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
manifest = ROOT / 'checksums' / 'release.sha256'
errors=[]
for line in manifest.read_text(encoding='utf-8').splitlines():
    if not line.strip():
        continue
    expected, rel = line.split('  ',1)
    p=ROOT/rel
    if not p.is_file():
        errors.append(f'MISSING  {rel}')
        continue
    actual=hashlib.sha256(p.read_bytes()).hexdigest()
    if actual != expected:
        errors.append(f'HASH_MISMATCH  {rel}\n  expected {expected}\n  actual   {actual}')
if errors:
    print('Release verification: FAIL')
    print('\n'.join(errors))
    raise SystemExit(1)
print('Release verification: PASS')
