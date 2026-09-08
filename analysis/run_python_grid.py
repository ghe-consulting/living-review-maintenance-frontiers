from __future__ import annotations
import csv, pathlib, sys
import numpy as np
ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'model' / 'python'))
from routeb_reference import x_opt_lambert, x_opt_brent, schedule_minimum, exp_characteristic

out = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else pathlib.Path("python_grid.csv")
rhos = np.unique(np.r_[np.linspace(0.0001, 0.99, 600), [0.001,0.01,0.1,0.5,0.9,0.999]])
with out.open("w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["rho","x_star","x_root","min_variable","foc_residual"])
    for rho in rhos:
        rho=float(rho)
        xl=x_opt_lambert(rho); xr=x_opt_brent(rho)
        w.writerow([format(rho,'.17g'),format(xl,'.17g'),format(xr,'.17g'),
                    format(schedule_minimum(rho),'.17g'),format(exp_characteristic(xl)-rho,'.17g')])
