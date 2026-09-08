"""Independent Python reference for the living-review maintenance model.

This implementation was written separately from the R code and uses SciPy's
Lambert W plus independent numerical root/minimization checks.
"""
from __future__ import annotations
import math
from dataclasses import dataclass
from scipy import optimize, special


def exp_staleness(z: float) -> float:
    if z < 0 or not math.isfinite(z):
        raise ValueError("z must be finite and nonnegative")
    if z < 1e-6:
        return z/2 - z*z/6 + z**3/24 - z**4/120 + z**5/720
    return 1.0 + math.expm1(-z)/z


def exp_characteristic(x: float) -> float:
    if x < 0 or not math.isfinite(x):
        raise ValueError("x must be finite and nonnegative")
    return 1.0 - (1.0 + x)*math.exp(-x)


def x_opt_lambert(rho: float) -> float:
    if rho < 0 or not math.isfinite(rho):
        raise ValueError("rho must be nonnegative")
    if rho == 0:
        return 0.0
    if rho >= 1:
        return math.inf
    w = special.lambertw(-(1.0-rho)/math.e, k=-1)
    if abs(w.imag) > 2e-13:
        raise ArithmeticError("unexpected complex Lambert-W value")
    return -1.0 - float(w.real)


def x_opt_brent(rho: float) -> float:
    if rho < 0 or not math.isfinite(rho):
        raise ValueError("rho must be nonnegative")
    if rho == 0:
        return 0.0
    if rho >= 1:
        return math.inf
    hi = max(1.0, math.sqrt(2*rho)+1.0)
    while exp_characteristic(hi) <= rho:
        hi *= 2.0
    return optimize.brentq(lambda z: exp_characteristic(z)-rho, 0.0, hi,
                           xtol=5e-15, rtol=1e-14)


def schedule_minimum(rho: float) -> float:
    if rho == 0:
        return 0.0
    if rho >= 1:
        return 1.0
    return -math.expm1(-x_opt_lambert(rho))


def scheduled_normalized(x: float, rho: float, c_s: float = 0.0) -> float:
    if x <= 0 or not math.isfinite(x):
        raise ValueError("x must be finite and positive")
    return c_s + rho/x + exp_staleness(x)


def living_normalized(d: float, phi: float = 0.0, eta: float = 0.0,
                      delta_c: float = 0.0, c_s: float = 0.0) -> float:
    if d < 0 or not math.isfinite(d):
        raise ValueError("d must be finite and nonnegative")
    return c_s + phi + eta + delta_c + exp_staleness(d)


def advantage_living(rho: float, d: float, phi: float = 0.0,
                     eta: float = 0.0, delta_c: float = 0.0) -> float:
    return schedule_minimum(rho) - (phi + eta + delta_c + exp_staleness(d))


def portfolio_frontier(rho: float, d: float, alpha: float, f_over_q: float,
                       eta: float = 0.0, delta_c: float = 0.0) -> float:
    if not 0 <= alpha <= 1 or f_over_q < 0:
        raise ValueError("invalid alpha or shared-cost ratio")
    margin = schedule_minimum(rho)-exp_staleness(d)-eta-delta_c
    return math.inf if margin <= 0 else alpha*f_over_q/margin


def attribution_frontier(rho: float, d: float, n: float, f_over_q: float,
                         eta: float = 0.0, delta_c: float = 0.0) -> float:
    if n <= 0 or f_over_q <= 0:
        raise ValueError("n and shared-cost ratio must be positive")
    margin = schedule_minimum(rho)-exp_staleness(d)-eta-delta_c
    return 0.0 if margin <= 0 else n*margin/f_over_q


def cadence_frontier(rho: float, phi: float = 0.0, eta: float = 0.0,
                     delta_c: float = 0.0) -> float:
    target = schedule_minimum(rho)-phi-eta-delta_c
    if target <= 0:
        return 0.0
    if target >= 1:
        return math.inf
    a = 1.0-target
    arg = -math.exp(-1.0/a)/a
    # Principal branch is the positive-d solution; W_{-1} maps to d=0.
    w0 = special.lambertw(arg, k=0)
    if abs(w0.imag) > 2e-13:
        raise ArithmeticError("unexpected complex cadence inversion")
    return 1.0/a + float(w0.real)


def cadence_frontier_brent(rho: float, phi: float = 0.0, eta: float = 0.0,
                           delta_c: float = 0.0) -> float:
    target = schedule_minimum(rho)-phi-eta-delta_c
    if target <= 0:
        return 0.0
    if target >= 1:
        return math.inf
    hi = 1.0
    while exp_staleness(hi) <= target:
        hi *= 2
    return optimize.brentq(lambda z: exp_staleness(z)-target, 0.0, hi,
                           xtol=5e-15, rtol=1e-14)


def reset_topic_frontier(d: float, phi: float = 0.0, eta: float = 0.0,
                         delta_c: float = 0.0) -> float:
    c = exp_staleness(d)+phi+eta+delta_c
    if c <= 0:
        return 0.0
    if c >= 1:
        return 1.0
    return c + (1-c)*math.log1p(-c)


def weibull_mean_survival(shape: float) -> float:
    if shape <= 0:
        raise ValueError("shape must be positive")
    return float(special.gamma(1.0+1.0/shape))


def weibull_survival(x: float, shape: float) -> float:
    if x < 0 or shape <= 0:
        raise ValueError("x >= 0 and shape > 0 required")
    return math.exp(-(x**shape))


def weibull_integrated_survival(x: float, shape: float) -> float:
    if x < 0 or shape <= 0:
        raise ValueError("x >= 0 and shape > 0 required")
    return weibull_mean_survival(shape)*float(special.gammainc(1.0/shape, x**shape))


def weibull_staleness(x: float, shape: float) -> float:
    return 0.0 if x == 0 else 1.0-weibull_integrated_survival(x, shape)/x


def weibull_characteristic(x: float, shape: float) -> float:
    return weibull_integrated_survival(x, shape)-x*weibull_survival(x, shape)


def weibull_x_opt(rho: float, shape: float) -> float:
    if rho < 0 or shape <= 0:
        raise ValueError("rho >= 0 and shape > 0 required")
    ceiling = weibull_mean_survival(shape)
    if rho == 0:
        return 0.0
    if rho >= ceiling:
        return math.inf
    hi = 1.0
    while weibull_characteristic(hi, shape) <= rho:
        hi *= 2
    return optimize.brentq(lambda x: weibull_characteristic(x, shape)-rho,
                           0.0, hi, xtol=5e-14, rtol=1e-13)


def weibull_minimum(rho: float, shape: float) -> float:
    if rho == 0:
        return 0.0
    if rho >= weibull_mean_survival(shape):
        return 1.0
    return 1.0-weibull_survival(weibull_x_opt(rho, shape), shape)
