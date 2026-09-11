from __future__ import annotations
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
manifest = ROOT / 'checksums' / 'release.sha256'
errors=[]
listed=set()
for line in manifest.read_text(encoding='utf-8').splitlines():
    if not line.strip():
        continue
    expected, rel = line.split('  ',1)
    listed.add(rel)
    p=ROOT/rel
    if not p.is_file():
        errors.append(f'MISSING  {rel}')
        continue
    actual=hashlib.sha256(p.read_bytes()).hexdigest()
    if actual != expected:
        errors.append(f'HASH_MISMATCH  {rel}\n  expected {expected}\n  actual   {actual}')
actual_files={str(p.relative_to(ROOT)).replace('\\','/') for p in ROOT.rglob('*') if p.is_file() and '.git' not in p.parts}
expected_files=listed | {'checksums/release.sha256'}
for rel in sorted(actual_files-expected_files):
    errors.append(f'UNEXPECTED_FILE  {rel}')
for rel in sorted(expected_files-actual_files):
    errors.append(f'MISSING_FROM_TREE  {rel}')
if errors:
    print('Release verification: FAIL')
    print('\n'.join(errors))
    raise SystemExit(1)
print('Release verification: PASS')
