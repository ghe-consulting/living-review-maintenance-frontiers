from __future__ import annotations
import csv, json, sys
if len(sys.argv)!=3:
    raise SystemExit("usage: compare_outputs.py r_grid.csv python_grid.csv")

def read(p):
    with open(p,newline="") as f:
        return list(csv.DictReader(f))

# Order-invariant alignment is necessary because base R unique() preserves
# insertion order while NumPy unique() sorts. The prespecified scientific
# rho set is unchanged; rows are aligned by rho before output comparison.
r=sorted(read(sys.argv[1]), key=lambda row: float(row["rho"]))
p=sorted(read(sys.argv[2]), key=lambda row: float(row["rho"]))
if len(r)!=len(p):
    raise SystemExit("grid length mismatch")

fields=["rho","x_star","x_root","min_variable","foc_residual"]
max_abs={k:0.0 for k in fields}; max_rel={k:0.0 for k in fields}
for rr,pp in zip(r,p):
    if abs(float(rr["rho"])-float(pp["rho"]))>1e-14:
        raise SystemExit("rho grid mismatch after order-invariant alignment")
    for k in fields:
        a=float(rr[k]); b=float(pp[k]); diff=abs(a-b); den=max(1.0,abs(a),abs(b))
        max_abs[k]=max(max_abs[k],diff); max_rel[k]=max(max_rel[k],diff/den)

tol_abs=2e-9; tol_rel=2e-9
passed=max(max_abs.values())<=tol_abs and max(max_rel.values())<=tol_rel
res={
    "status":"PASS" if passed else "FAIL",
    "n_rows":len(r),
    "alignment":"sort_by_rho",
    "rho_match_tolerance":1e-14,
    "absolute_tolerance":tol_abs,
    "relative_scaled_tolerance":tol_rel,
    "max_abs":max_abs,
    "max_scaled_relative":max_rel
}
print(json.dumps(res,indent=2))
if not passed:
    raise SystemExit(1)
