from __future__ import annotations
import json, math, pathlib, sys, unittest
import numpy as np
from scipy import optimize
ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "model" / "python"))
import routeb_reference as m

class RouteBReferenceTests(unittest.TestCase):
    def test_lambert_matches_independent_root_dense(self):
        for rho in np.linspace(1e-5, 0.999, 900):
            a=m.x_opt_lambert(float(rho)); b=m.x_opt_brent(float(rho))
            self.assertLess(abs(a-b), 2e-10)
            self.assertLess(abs(m.exp_characteristic(a)-rho), 2e-12)

    def test_minimum_identity_and_direct_minimization(self):
        for rho in np.linspace(1e-4, 0.995, 300):
            rho=float(rho); x=m.x_opt_lambert(rho)
            identity=m.schedule_minimum(rho)
            direct=rho/x + m.exp_staleness(x)
            self.assertLess(abs(identity-direct), 2e-12)
            opt=optimize.minimize_scalar(lambda z: rho/z+m.exp_staleness(z),
                                         bounds=(1e-8, max(20.0,3*x)), method="bounded",
                                         options={"xatol":1e-12})
            self.assertLess(abs(identity-opt.fun), 5e-10)

    def test_boundaries_and_monotonicity(self):
        self.assertEqual(m.schedule_minimum(0),0)
        self.assertEqual(m.schedule_minimum(1),1)
        xs=[m.x_opt_lambert(r) for r in np.linspace(0.001,0.999,400)]
        self.assertTrue(np.all(np.diff(xs)>0))
        gs=[m.exp_staleness(x) for x in np.linspace(0,20,500)]
        self.assertTrue(np.all(np.diff(gs)>=0))

    def test_sqrt_is_lower_bound(self):
        for rho in np.linspace(1e-6,0.999,500):
            self.assertGreater(m.x_opt_lambert(float(rho)), math.sqrt(2*float(rho)))

    def test_cadence_exact_inverse(self):
        for rho in np.linspace(0.01,0.95,150):
            # choose overhead fraction safely inside the feasible region
            phi=0.2*m.schedule_minimum(float(rho))
            d1=m.cadence_frontier(float(rho), phi=phi)
            d2=m.cadence_frontier_brent(float(rho), phi=phi)
            self.assertLess(abs(d1-d2), 3e-10)
            self.assertLess(abs(m.exp_staleness(d1)-(m.schedule_minimum(float(rho))-phi)), 2e-11)

    def test_frontier_equalities(self):
        for rho,d in [(0.1,0.05),(0.4,0.15),(0.8,0.25)]:
            eta,dc=0.01,0.005
            B=m.schedule_minimum(rho)-m.exp_staleness(d)-eta-dc
            if B<=0: continue
            alpha, fq = 0.4, 0.3
            n=m.portfolio_frontier(rho,d,alpha,fq,eta,dc)
            phi=alpha*fq/n
            self.assertLess(abs(m.advantage_living(rho,d,phi,eta,dc)),1e-12)
            a=m.attribution_frontier(rho,d,n,fq,eta,dc)
            self.assertLess(abs(a-alpha),1e-12)

    def test_topic_frontier(self):
        for d in [0.01,0.05,0.2,0.8]:
            rho=m.reset_topic_frontier(d)
            self.assertLess(abs(m.schedule_minimum(rho)-m.exp_staleness(d)),3e-11)

    def test_weibull_extension(self):
        for shape in [0.6,0.8,1.0,1.5,2.0,3.0]:
            cap=m.weibull_mean_survival(shape)
            for frac in [0.01,0.1,0.4,0.8,0.98]:
                rho=frac*cap; x=m.weibull_x_opt(rho,shape)
                self.assertLess(abs(m.weibull_characteristic(x,shape)-rho),3e-11)
                minid=m.weibull_minimum(rho,shape)
                direct=rho/x+m.weibull_staleness(x,shape)
                self.assertLess(abs(minid-direct),3e-11)
        for rho in [0.01,0.2,0.7,0.95]:
            self.assertLess(abs(m.weibull_x_opt(rho,1.0)-m.x_opt_brent(rho)),3e-10)

if __name__ == "__main__":
    unittest.main(verbosity=2)
