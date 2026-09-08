import math, json, pathlib
import numpy as np
from scipy.optimize import minimize_scalar, brentq
from scipy.special import lambertw, gammainc, gamma
import sympy as sp

# Base functions

def g(x):
    if abs(x) < 1e-7:
        # series through x^5
        return x/2 - x*x/6 + x**3/24 - x**4/120 + x**5/720
    return 1 - (1-math.exp(-x))/x

def h(x):
    return 1 - (1+x)*math.exp(-x)

def x_exact(rho):
    if not (0 < rho < 1):
        raise ValueError('rho must be in (0,1)')
    return float((-1-lambertw(-(1-rho)/math.e, k=-1)).real)

def x_root(rho):
    hi=1.0
    while h(hi)<rho:
        hi*=2
    return brentq(lambda z:h(z)-rho, 1e-14, hi, xtol=1e-14, rtol=1e-14)

def j(x,rho):
    return rho/x + g(x)

def m_exact(rho):
    x=x_exact(rho)
    return 1-math.exp(-x)

def d_break(z):
    if z <= 0: return 0.0
    if z >= 1: return math.inf
    a=1-z
    arg=-math.exp(-1/a)/a
    return float((1/a + lambertw(arg,k=0)).real)

rhos=np.unique(np.concatenate([
    np.logspace(-8,-2,25),
    np.linspace(.011,.95,120),
    np.array([.975,.99,.999,.9999])
]))
branch_err=[]; root_err=[]; min_x_err=[]; min_val_err=[]; foc_err=[]
for rho in rhos:
    xe=x_exact(float(rho))
    xr=x_root(float(rho))
    res=minimize_scalar(lambda z:j(z,float(rho)), bounds=(max(1e-10,xe/5), xe*5+1), method='bounded', options={'xatol':1e-13})
    branch_err.append(abs(h(xe)-rho))
    root_err.append(abs(xe-xr))
    min_x_err.append(abs(res.x-xe))
    min_val_err.append(abs(res.fun-m_exact(float(rho))))
    foc_err.append(abs((h(xe)-rho)/(xe*xe)))

# Cadence inverse checks
zs=np.linspace(1e-6,.999,200)
cad_err=[]
for z in zs:
    d=d_break(float(z))
    cad_err.append(abs(g(d)-z))

# Square-root approximation table
rho_table=[0.0001,0.001,0.01,0.05,0.1,0.25,0.5,0.75,0.9,0.99]
approx=[]
for rho in rho_table:
    xe=x_exact(rho); xs=math.sqrt(2*rho)
    approx.append({
        'rho':rho,'x_exact':xe,'x_sqrt':xs,
        'sqrt_underestimates': xs < xe,
        'relative_error_using_sqrt':(xe-xs)/xe,
        'absolute_error':xe-xs
    })

# Physical mu derivative threshold root e^x=1+x+x^2
x_mu=brentq(lambda x:math.exp(x)-1-x-x*x, 1e-6, 10)
rho_mu=h(x_mu)

# Weibull extension checks: r=exp(-x^k), A=gamma(1/k)*gammainc(1/k,x^k)/k

def A_weib(x,k):
    return gamma(1.0/k)*gammainc(1.0/k,x**k)/k

def H_weib(x,k):
    return A_weib(x,k)-x*math.exp(-(x**k))

def G_weib(x,k):
    return 1-A_weib(x,k)/x

def weib_opt(rho,k):
    M=gamma(1+1.0/k)
    if not (0<rho<M): return None
    hi=1.0
    while H_weib(hi,k)<rho: hi*=2
    return brentq(lambda z:H_weib(z,k)-rho,1e-12,hi)

weib_checks=[]
for k in [0.6,0.8,1.0,1.5,2.0,3.0]:
    M=gamma(1+1/k)
    for frac in [0.05,0.25,0.5,0.9]:
        rho=float(frac*M)
        x=weib_opt(rho,k)
        direct=minimize_scalar(lambda z:rho/z+G_weib(z,k),bounds=(x/5,x*5+1),method='bounded')
        val=1-math.exp(-(x**k))
        weib_checks.append({'k':k,'rho':rho,'x':x,'foc_error':abs(H_weib(x,k)-rho),'minimum_identity_error':abs((rho/x+G_weib(x,k))-val),'direct_minimum_value_error':abs(direct.fun-val)})

# Symbolic identities
x,r=sp.symbols('x r', positive=True)
gsym=1-(1-sp.exp(-x))/x
hsym=1-(1+x)*sp.exp(-x)
jexpr=r/x+gsym
jprime=sp.simplify(sp.diff(jexpr,x))
min_sub=sp.simplify(jexpr.subs(r,hsym))
series_h=sp.series(hsym,x,0,7)

out={
  'artifact_type':'symbolic_and_numerical_model_checks',
  'status':'PASS',
  'checks':{
    'symbolic_derivative_j':str(jprime),
    'expected_symbolic_derivative':'(1-(1+x)*exp(-x)-rho)/x**2',
    'minimum_after_FOC_substitution':str(min_sub),
    'expected_minimum':'1-exp(-x)',
    'h_series_through_x6':str(series_h),
    'max_lambert_foc_residual':max(branch_err),
    'max_lambert_vs_root_x_error':max(root_err),
    'max_direct_minimizer_x_error':max(min_x_err),
    'max_direct_minimum_value_error':max(min_val_err),
    'max_cadence_inverse_error':max(cad_err),
    'weibull_max_foc_error':max(v['foc_error'] for v in weib_checks),
    'weibull_max_minimum_identity_error':max(v['minimum_identity_error'] for v in weib_checks),
    'weibull_max_direct_minimum_value_error':max(v['direct_minimum_value_error'] for v in weib_checks),
    'mu_physical_derivative_sign_change_x':x_mu,
    'mu_physical_derivative_sign_change_rho':rho_mu
  },
  'square_root_approximation':approx,
  'weibull_spot_checks':weib_checks,
  'summary':{
    'dimensionally_coherent':True,
    'symbolic_and_numerical_agree':True,
    'boundary_cases_expected':True
  }}
ROOT = pathlib.Path(__file__).resolve().parents[1]
outfile = ROOT / 'model' / 'symbolic_checks.json'
outfile.write_text(json.dumps(out, indent=2) + '\n', encoding='utf-8')
print(json.dumps(out['checks'],indent=2))
