from __future__ import annotations
import csv, json, math, hashlib, pathlib, platform, sys, datetime
from itertools import product
import numpy as np
import pandas as pd
from scipy import optimize, special, stats
import matplotlib.pyplot as plt

ROOT = pathlib.Path(__file__).resolve().parents[1]
PROTOCOL = ROOT / 'protocol'
OUT = ROOT / 'results' / 'source_data'
TABLES = ROOT / 'results' / 'tables'
FIGS = ROOT / 'results' / 'figures'
for d in [OUT, TABLES, FIGS]: d.mkdir(parents=True, exist_ok=True)

# Fixed PDF metadata prevents run-time timestamps from changing the archived files.
_PDF_DATE = datetime.datetime(2026, 9, 6, tzinfo=datetime.timezone.utc)
_PDF_METADATA = {
    'Author': 'Joseph B. Babigumira',
    'Creator': 'living-review-maintenance-frontiers v1.0.0',
    'Producer': 'Matplotlib 3.10.8',
    'CreationDate': _PDF_DATE,
    'ModDate': _PDF_DATE,
}

def save_figure(stem):
    plt.tight_layout()
    plt.savefig(FIGS/f'{stem}.png', dpi=300)
    plt.savefig(FIGS/f'{stem}.pdf', metadata=_PDF_METADATA)
    plt.close()

with open(PROTOCOL/'seeds.json', encoding='utf-8') as f: SEEDS=json.load(f)['seeds']
with open(PROTOCOL/'architectures.json', encoding='utf-8') as f: ARCH=json.load(f)['architectures']
with open(PROTOCOL/'figure_constants.json', encoding='utf-8') as f: FIGC=json.load(f)

TIE=1e-12

# ---------- exact base model, vectorized ----------
def g_exp(z):
    z=np.asarray(z,dtype=float)
    out=np.empty_like(z)
    small=z<1e-6
    zz=z[small]
    out[small]=zz/2-zz**2/6+zz**3/24-zz**4/120+zz**5/720
    zz=z[~small]
    out[~small]=1+np.expm1(-zz)/zz
    return out

def x_star_exp(rho):
    rho=np.asarray(rho,dtype=float)
    z=-(1-rho)/math.e
    w=special.lambertw(z,k=-1).real
    return -1-w

def m_exp(rho):
    return -np.expm1(-x_star_exp(rho))

def classify(adv):
    adv=np.asarray(adv)
    out=np.full(adv.shape,'tie',dtype=object)
    out[adv>TIE]='living'; out[adv<-TIE]='scheduled'
    return out

def rho_be_from_c(c):
    c=np.asarray(c,dtype=float)
    out=np.empty_like(c)
    out[c<=0]=0.0; out[c>=1]=1.0
    mid=(c>0)&(c<1)
    cm=c[mid]
    out[mid]=cm+(1-cm)*np.log1p(-cm)
    return out

def cadence_root_from_target(target):
    if target<=0: return 0.0
    if target>=1: return math.inf
    hi=1.0
    while float(g_exp(np.array([hi]))[0])<=target: hi*=2
    return optimize.brentq(lambda d: float(g_exp(np.array([d]))[0])-target,0.0,hi,xtol=5e-14,rtol=1e-13)

# ---------- Weibull structural extension ----------
def weibull_mean(k): return float(special.gamma(1+1/k))
def weibull_surv(x,k): return math.exp(-(x**k))
def weibull_int(x,k): return weibull_mean(k)*float(special.gammainc(1/k,x**k))
def weibull_char(x,k): return weibull_int(x,k)-x*weibull_surv(x,k)
def weibull_x(rho,k):
    cap=weibull_mean(k)
    if rho<=0: return 0.0
    if rho>=cap: return math.inf
    hi=1.0
    while weibull_char(hi,k)<=rho: hi*=2
    return optimize.brentq(lambda x: weibull_char(x,k)-rho,0.0,hi,xtol=5e-14,rtol=1e-13)
def weibull_min(rho,k):
    x=weibull_x(rho,k)
    if math.isinf(x): return 1.0
    return 1-weibull_surv(x,k)
def weibull_g(d,k):
    if d==0: return 0.0
    return 1-weibull_int(d,k)/d

# ---------- design transforms ----------
def lhs_design(n, seed, rho_hi=.999):
    sampler=stats.qmc.LatinHypercube(d=7,scramble=True,seed=int(seed))
    u=sampler.random(n)
    logit=lambda p: math.log(p/(1-p))
    lo,hi=logit(1e-4),logit(rho_hi)
    rho=special.expit(lo+(hi-lo)*u[:,0])
    d=10**(-4+5*u[:,1])
    nport=np.rint(2**(8*u[:,2])).astype(int); nport=np.clip(nport,1,256)
    alpha=u[:,3]
    omega=10**(-3+4*u[:,4])
    eta=0.5*u[:,5]
    dc=-0.5+u[:,6]
    return pd.DataFrame({'rho':rho,'d':d,'n':nport,'alpha':alpha,'omega_F_over_Q':omega,'eta':eta,'delta_c':dc})

def evaluate_base(df, psi=0.0):
    rho=df.rho.to_numpy(); d=df.d.to_numpy(); n=df.n.to_numpy(); a=df.alpha.to_numpy(); om=df.omega_F_over_Q.to_numpy(); eta=df.eta.to_numpy(); dc=df.delta_c.to_numpy()
    xs=x_star_exp(rho); m=m_exp(rho); gst=g_exp(d); phi=a*om/n
    if psi == 0.0:
        release=np.zeros_like(d,dtype=float)
    else:
        release=np.where(d>0,psi/d,np.inf)
    live=gst+phi+eta+dc+release
    adv=m-live
    B=m-gst-eta-dc-release
    nbe=np.where(B>0,a*om/B,np.inf)
    abe=np.full(B.shape,np.inf,dtype=float)
    abe[B<=0]=0.0
    mask_abe=(om>0)&(B>0)
    abe[mask_abe]=n[mask_abe]*B[mask_abe]/om[mask_abe]
    c=gst+phi+eta+dc+release
    rhobe=rho_be_from_c(c)
    out=df.copy()
    out['x_star']=xs; out['m_rho']=m; out['g_d']=gst; out['phi']=phi; out['living_burden_relative']=live; out['living_advantage']=adv; out['policy']=classify(adv); out['n_BE']=nbe; out['alpha_BE']=abe; out['rho_BE']=rhobe
    return out

# 1) Primary LHS and independent replicate
primary=evaluate_base(lhs_design(32768,SEEDS['primary_lhs']))
replicate=evaluate_base(lhs_design(32768,SEEDS['resolution_check']))
primary.to_csv(OUT/'primary_lhs.csv',index=False)
replicate[['rho','d','n','alpha','omega_F_over_Q','eta','delta_c','living_advantage','policy']].to_csv(OUT/'primary_lhs_replication.csv',index=False)

def coverage(df):
    counts=df.policy.value_counts()
    return {k:int(counts.get(k,0)) for k in ['living','scheduled','tie']} | {
        'living_fraction':float((df.policy=='living').mean()),
        'scheduled_fraction':float((df.policy=='scheduled').mean()),
        'tie_fraction':float((df.policy=='tie').mean())}
cover1=coverage(primary); cover2=coverage(replicate)
coverage_diff=abs(cover1['living_fraction']-cover2['living_fraction'])

# 2) Deterministic boundary Cartesian design
vals={
 'rho':[1e-6,1e-4,.01,.1,.5,.9,.99,.999999],
 'd':[0,1e-4,.01,.1,1,10],
 'n':[1,2,8,32,128,256],
 'alpha':[0,.5,1],
 'omega_F_over_Q':[0,1e-3,.1,1,10],
 'eta':[0,.1,.5],
 'delta_c':[-.5,0,.5]
}
boundary=pd.DataFrame(product(*vals.values()),columns=vals.keys())
# d=0 needs no psi, safe in base evaluation
boundary=evaluate_base(boundary)
boundary.to_csv(OUT/'boundary_design.csv',index=False)

# 3) Approximation experiment
rho_approx=np.unique(np.r_[np.geomspace(1e-6,.1,6000),np.linspace(.1,.999,4001)])
xex=x_star_exp(rho_approx); xap=np.sqrt(2*rho_approx)
rel=(xex-xap)/xex
exact_cost=m_exp(rho_approx)
approx_cost=rho_approx/xap+g_exp(xap)
regret=approx_cost-exact_cost
approx_df=pd.DataFrame({'rho':rho_approx,'x_exact':xex,'x_sqrt':xap,'interval_relative_underestimate':rel,'exact_min_variable':exact_cost,'approx_variable_cost':approx_cost,'normalized_cost_regret':regret})
approx_df.to_csv(OUT/'approximation_curve.csv',index=False)
threshold_rows=[]
for t in [.01,.05,.10,.25]:
    r=optimize.brentq(lambda rr: float((x_star_exp(np.array([rr]))[0]-math.sqrt(2*rr))/x_star_exp(np.array([rr]))[0])-t,1e-8,.999999,xtol=1e-14)
    threshold_rows.append({'interval_relative_error_threshold':t,'rho_first_exceedance':r,'x_exact_at_threshold':float(x_star_exp(np.array([r]))[0])})
approx_thresholds=pd.DataFrame(threshold_rows)
approx_thresholds.to_csv(TABLES/'Table2A_approximation_thresholds.csv',index=False)

# 4) Architecture curves and exact thresholds
rho_curve=np.linspace(1e-4,.999,2000); mcurve=m_exp(rho_curve)
arch_rows=[]; arch_curve_rows=[]
for a in ARCH:
    phi=a['alpha']*a['omega_F_over_Q']/a['n']
    c=float(g_exp(np.array([a['d']]))[0])+phi+a['eta']+a['delta_c']
    rbe=float(rho_be_from_c(np.array([c]))[0])
    arch_rows.append({**a,'phi':phi,'non_scheduled_burden_c':c,'rho_BE':rbe})
    adv=mcurve-c
    for r,v in zip(rho_curve,adv): arch_curve_rows.append({'architecture_id':a['id'],'rho':r,'living_advantage':v})
pd.DataFrame(arch_rows).to_csv(TABLES/'Table2B_architecture_frontiers.csv',index=False)
pd.DataFrame(arch_curve_rows).to_csv(OUT/'architecture_frontier_curves.csv',index=False)

# 5) Exact policy frontier curves for fixed b
policy_rows=[]
for b in FIGC['figure_2_policy_frontier']['fixed_non_timeliness_b']:
    for r,mv in zip(rho_curve,mcurve):
        target=mv-b
        dbe=cadence_root_from_target(float(target))
        policy_rows.append({'fixed_non_timeliness_b':b,'rho':r,'d_BE':dbe})
pd.DataFrame(policy_rows).to_csv(OUT/'policy_frontier_curves.csv',index=False)

# 6) Portfolio break-even surface and curves
fc=FIGC['figure_3_portfolio_frontier']; d0=fc['d']; eta0=fc['eta']; dc0=fc['delta_c']; g0=float(g_exp(np.array([d0]))[0])
attr_grid=np.linspace(.001,1.0,300); rho_surface=np.linspace(1e-4,.999,400); M=m_exp(rho_surface); B=M-g0-eta0-dc0
surf_rows=[]
for av in attr_grid:
    nbe=np.where(B>0,av/B,np.inf)
    for r,nv in zip(rho_surface,nbe): surf_rows.append({'rho':r,'attributable_shared_ratio':av,'n_BE':nv})
pd.DataFrame(surf_rows).to_csv(OUT/'portfolio_break_even_surface.csv',index=False)
curve_rows=[]
for av in fc['attributable_shared_ratio_alpha_times_omega']:
    nbe=np.where(B>0,av/B,np.inf)
    for r,nv in zip(rho_surface,nbe): curve_rows.append({'rho':r,'attributable_shared_ratio':av,'n_BE':nv})
pd.DataFrame(curve_rows).to_csv(OUT/'portfolio_frontier_curves.csv',index=False)

# 7) Structural sample: common-rho Weibull
struct_base=lhs_design(8192,SEEDS['weibull_lhs'],rho_hi=.85)
# Re-map rho exactly into [1e-4,.85] linearly on logit domain already done by lhs_design.
# k=1 exponential reference using same inputs.
base_common=evaluate_base(struct_base)
base_pol=base_common.policy.to_numpy()
weib_rows=[]; struct_summary=[]
for k in [.5,.75,1.0,1.5,2.0]:
    adv=[]; pol=[]
    for row in struct_base.itertuples(index=False):
        minv=weibull_min(float(row.rho),k)
        gd=weibull_g(float(row.d),k)
        phi=float(row.alpha*row.omega_F_over_Q/row.n)
        aa=minv-(gd+phi+float(row.eta)+float(row.delta_c))
        adv.append(aa); pol.append('living' if aa>TIE else ('scheduled' if aa<-TIE else 'tie'))
    pol=np.array(pol,dtype=object); adv=np.array(adv)
    switches=float(np.mean(pol!=base_pol)) if k!=1 else 0.0
    struct_summary.append({'scenario_type':'weibull_common_rho','level':k,'living_coverage_fraction':float(np.mean(pol=='living')),'switch_fraction_vs_exponential':switches})
    for idx,(r,aadv,pp) in enumerate(zip(struct_base.rho.to_numpy(),adv,pol)):
        weib_rows.append({'design_row':idx,'k':k,'rho':r,'living_advantage':aadv,'policy':pp})
pd.DataFrame(weib_rows).to_csv(OUT/'weibull_common_rho.csv',index=False)

# boundary-scaled Weibull comparison: same q design coordinate inferred by mapping rho/.85 into quantile is not valid,
# so create a second 8192-point LHS only for q using frozen same seed stream deterministically.
sampler=stats.qmc.LatinHypercube(d=7,scramble=True,seed=int(SEEDS['weibull_lhs']))
u=sampler.random(8192)
q=special.expit(math.log(1e-4/(1-1e-4))+(math.log(.999/(1-.999))-math.log(1e-4/(1-1e-4)))*u[:,0])
d2=10**(-4+5*u[:,1]); n2=np.clip(np.rint(2**(8*u[:,2])).astype(int),1,256); al2=u[:,3]; om2=10**(-3+4*u[:,4]); et2=.5*u[:,5]; dc2=-.5+u[:,6]
scaled_rows=[]; scaled_summary=[]
for k in [.5,.75,1.0,1.5,2.0]:
    cap=weibull_mean(k); pol=[]
    for i in range(len(q)):
        rr=float(q[i]*cap); minv=weibull_min(rr,k); gd=weibull_g(float(d2[i]),k); phi=float(al2[i]*om2[i]/n2[i]); aa=minv-(gd+phi+float(et2[i])+float(dc2[i])); pp='living' if aa>TIE else ('scheduled' if aa<-TIE else 'tie'); pol.append(pp)
        scaled_rows.append({'design_row':i,'k':k,'q_rho_over_boundary':q[i],'rho':rr,'living_advantage':aa,'policy':pp})
    pol=np.array(pol,dtype=object)
    scaled_summary.append({'scenario_type':'weibull_boundary_scaled','level':k,'living_coverage_fraction':float(np.mean(pol=='living'))})
pd.DataFrame(scaled_rows).to_csv(OUT/'weibull_boundary_scaled.csv',index=False)

# 8) Automation symmetry, release overhead, attribution on common structural sample
neutral=struct_base.copy(); neutral['delta_c']=0.0
ref_neutral=evaluate_base(neutral); refp=ref_neutral.policy.to_numpy()
auto_summary=[]
for dc in [0,-.05,.05,-.15,.15,-.30,.30]:
    x=neutral.copy(); x['delta_c']=dc; ev=evaluate_base(x); p=ev.policy.to_numpy(); auto_summary.append({'scenario_type':'automation_delta_c','level':dc,'living_coverage_fraction':float(np.mean(p=='living')),'switch_fraction_vs_delta_c_0':float(np.mean(p!=refp))})
psi_summary=[]
for psi in [0,.0025,.01,.04]:
    ev=evaluate_base(neutral,psi=psi); p=ev.policy.to_numpy(); psi_summary.append({'scenario_type':'release_overhead_psi','level':psi,'living_coverage_fraction':float(np.mean(p=='living')),'switch_fraction_vs_psi_0':float(np.mean(p!=refp))})
alpha_summary=[]
for al in [0,.25,.5,.75,1.0]:
    x=neutral.copy(); x['alpha']=al; ev=evaluate_base(x); p=ev.policy.to_numpy(); alpha_summary.append({'scenario_type':'fixed_alpha','level':al,'living_coverage_fraction':float(np.mean(p=='living'))})
struct_table=pd.DataFrame(struct_summary+scaled_summary+auto_summary+psi_summary+alpha_summary)
struct_table.to_csv(TABLES/'Table3_structural_sensitivity.csv',index=False)

# 9) Resolution checks for fixed-b policy surfaces; 256 vs 512 cells => 257 vs 513 nodes.
def extract_frontier(rhos, ds, b):
    m=m_exp(rhos); gd=g_exp(ds)
    vals=[]
    for mv in m:
        A=mv-b-gd
        if A[0] <= 0: vals.append(0.0); continue
        if A[-1] > 0: vals.append(math.inf); continue
        j=np.where(A<=0)[0][0]
        x0,x1=ds[j-1],ds[j]; y0,y1=A[j-1],A[j]
        vals.append(float(x0+(0-y0)*(x1-x0)/(y1-y0)))
    return np.array(vals)
res_rows=[]; res_pass=True; max_frac=0.0
for b in FIGC['figure_2_policy_frontier']['fixed_non_timeliness_b']:
    r256=np.linspace(1e-4,.999,257); d256=np.linspace(0,10,257)
    r512=np.linspace(1e-4,.999,513); d512=np.linspace(0,10,513)
    f256=extract_frontier(r256,d256,b); f512=extract_frontier(r512,d512,b)[::2]
    finite=np.isfinite(f256)&np.isfinite(f512)
    dif=np.abs(f256[finite]-f512[finite]) if finite.any() else np.array([0.0])
    frac=float(dif.max()/10.0) if len(dif) else 0.0
    max_frac=max(max_frac,frac)
    ok=frac<=.0025
    res_pass=res_pass and ok
    res_rows.append({'fixed_b':b,'finite_shared_frontier_points':int(finite.sum()),'max_abs_d_frontier_difference':float(dif.max()),'fraction_of_d_axis_span':frac,'pass':ok})
pd.DataFrame(res_rows).to_csv(OUT/'surface_resolution_check.csv',index=False)

# 10) Summary tables
finite_nbe=primary.loc[np.isfinite(primary.n_BE),'n_BE']
summary_rows=[
 {'metric':'primary_lhs_n','value':len(primary),'note':'design points'},
 {'metric':'living_coverage_fraction','value':cover1['living_fraction'],'note':'descriptive design-space coverage, not probability'},
 {'metric':'scheduled_coverage_fraction','value':cover1['scheduled_fraction'],'note':'descriptive design-space coverage, not probability'},
 {'metric':'tie_coverage_fraction','value':cover1['tie_fraction'],'note':'|advantage|<=1e-12'},
 {'metric':'replicate_living_coverage_fraction','value':cover2['living_fraction'],'note':'independent LHS replicate'},
 {'metric':'coverage_fraction_abs_difference','value':coverage_diff,'note':'prespecified <=0.01'},
 {'metric':'finite_n_BE_fraction','value':float(np.isfinite(primary.n_BE).mean()),'note':'B>0'},
 {'metric':'finite_n_BE_median','value':float(finite_nbe.median()) if len(finite_nbe) else math.nan,'note':'continuous frontier'},
 {'metric':'finite_n_BE_p90','value':float(finite_nbe.quantile(.9)) if len(finite_nbe) else math.nan,'note':'continuous frontier'},
 {'metric':'sqrt_rel_error_max_domain','value':float(rel.max()),'note':'rho 1e-6 to 0.999'},
 {'metric':'sqrt_cost_regret_max_domain','value':float(regret.max()),'note':'normalized variable burden'},
 {'metric':'surface_resolution_max_axis_fraction','value':max_frac,'note':'prespecified <=0.0025'}
]
pd.DataFrame(summary_rows).to_csv(TABLES/'Table2_exact_frontier_summary.csv',index=False)

# 11) Figures - one axes per file, default matplotlib colors/styles only.
# Fig 1a exact vs sqrt
plt.figure(figsize=(7.2,5.0)); plt.plot(rho_approx,xex,label='Exact $x^*$'); plt.plot(rho_approx,xap,label=r'$\sqrt{2\rho}$'); plt.xlabel(r'$\rho$'); plt.ylabel('Dimensionless scheduled interval'); plt.legend(); save_figure('Fig1a_exact_vs_sqrt')
plt.figure(figsize=(7.2,5.0)); plt.plot(rho_approx,100*rel); plt.xlabel(r'$\rho$'); plt.ylabel('Interval underestimation (%)'); save_figure('Fig1b_sqrt_relative_error')

# Fig 2 frontier curves
pf=pd.read_csv(OUT/'policy_frontier_curves.csv')
plt.figure(figsize=(7.2,5.0))
for b in FIGC['figure_2_policy_frontier']['fixed_non_timeliness_b']:
    sub=pf[pf.fixed_non_timeliness_b==b]; y=np.minimum(sub.d_BE.to_numpy(),10.0); plt.plot(sub.rho,y,label=f'b={b:g}')
plt.xlabel(r'$\rho$'); plt.ylabel(r'Break-even living cadence $d_{BE}$ (clipped at 10)'); plt.legend(); save_figure('Fig2_policy_frontiers')

# Fig 3 surface
surf=pd.read_csv(OUT/'portfolio_break_even_surface.csv'); pivot=surf.pivot(index='attributable_shared_ratio',columns='rho',values='n_BE'); Z=np.log10(np.clip(pivot.to_numpy(),1e-3,1e4)); X,Y=np.meshgrid(pivot.columns.to_numpy(),pivot.index.to_numpy())
plt.figure(figsize=(7.2,5.0)); mesh=plt.pcolormesh(X,Y,Z,shading='auto'); plt.colorbar(mesh,label=r'$\log_{10}(n_{BE})$'); plt.xlabel(r'$\rho$'); plt.ylabel(r'Attributable shared burden $\alpha F/Q$'); save_figure('Fig3_portfolio_break_even_surface')

# Fig 4 architectures
ac=pd.read_csv(OUT/'architecture_frontier_curves.csv')
plt.figure(figsize=(7.2,5.0))
labels={a['id']:a['label'].replace('_',' ') for a in ARCH}
for aid in labels:
    sub=ac[ac.architecture_id==aid]; plt.plot(sub.rho,sub.living_advantage,label=labels[aid])
plt.axhline(0,linewidth=1); plt.xlabel(r'$\rho$'); plt.ylabel('Living advantage (normalized burden)'); plt.legend(); save_figure('Fig4_architecture_frontiers')

# Fig 5a architecture B hazard
barch=[a for a in ARCH if a['id']=='ARCH_B'][0]
rh=np.linspace(1e-4,.85,800)
plt.figure(figsize=(7.2,5.0))
for k in [.5,.75,1,1.5,2]:
    vals=[]
    for rr in rh:
        minv=weibull_min(float(rr),float(k)); gd=weibull_g(float(barch['d']),float(k)); c=gd+barch['alpha']*barch['omega_F_over_Q']/barch['n']+barch['eta']+barch['delta_c']; vals.append(minv-c)
    plt.plot(rh,vals,label=f'k={k:g}')
plt.axhline(0,linewidth=1); plt.xlabel(r'$\rho$'); plt.ylabel('Living advantage'); plt.legend(); save_figure('Fig5a_weibull_hazard_sensitivity')

# Fig 5b architecture B release overhead
plt.figure(figsize=(7.2,5.0))
for psi in FIGC['figure_5_structural_reference']['release_overhead_psi']:
    c=float(g_exp(np.array([barch['d']]))[0])+barch['alpha']*barch['omega_F_over_Q']/barch['n']+barch['eta']+barch['delta_c']+psi/barch['d']; plt.plot(rho_curve,mcurve-c,label=f'psi={psi:g}')
plt.axhline(0,linewidth=1); plt.xlabel(r'$\rho$'); plt.ylabel('Living advantage'); plt.legend(); save_figure('Fig5b_release_overhead_sensitivity')

# 12) Validation and environment
validation={
 'execution_date':'2026-09-06','primary_lhs_n':len(primary),'replicate_lhs_n':len(replicate),
 'primary_coverage':cover1,'replicate_coverage':cover2,'coverage_fraction_abs_difference':coverage_diff,'coverage_replication_pass':coverage_diff<=.01,
 'surface_resolution':res_rows,'surface_resolution_pass':bool(res_pass),
 'approximation':{'square_root_is_lower_everywhere':bool(np.all(xap<xex)),'max_interval_relative_underestimate':float(rel.max()),'max_normalized_cost_regret':float(regret.max())},
 'structural_rows':{'weibull_common':len(weib_rows),'weibull_boundary_scaled':len(scaled_rows)},
 'architecture_count':len(ARCH)
}
VALDIR=ROOT/'validation'; VALDIR.mkdir(parents=True,exist_ok=True)
with open(VALDIR/'simulation_validation.json','w',encoding='utf-8') as f: json.dump(validation,f,indent=2); f.write('\n')

summary={
 'status':'PASS' if (coverage_diff<=.01 and res_pass) else 'FAIL',
 'analysis_date':'2026-09-06','primary_coverage':cover1,'replicate_coverage':cover2,'coverage_difference':coverage_diff,
 'approximation_thresholds':approx_thresholds.to_dict(orient='records'),
 'architectures':pd.DataFrame(arch_rows).to_dict(orient='records'),
 'structural_sensitivity_table':'results/tables/Table3_structural_sensitivity.csv',
 'results_are_design_space_not_empirical_probability':True
}
with open(ROOT/'results'/'numerical_summary.json','w',encoding='utf-8') as f:
    json.dump(summary,f,indent=2,allow_nan=False); f.write('\n')

ENVDIR=ROOT/'environment'; ENVDIR.mkdir(parents=True,exist_ok=True)
with open(ENVDIR/'reproduction_environment.json','w',encoding='utf-8') as f:
    json.dump({'python':sys.version,'platform':platform.platform(),'numpy':np.__version__,'pandas':pd.__version__,'scipy':__import__('scipy').__version__,'matplotlib':__import__('matplotlib').__version__},f,indent=2); f.write('\n')

if coverage_diff>.01 or not res_pass:
    raise SystemExit('Prespecified convergence checks failed')
print(json.dumps({'status':'PASS','coverage_difference':coverage_diff,'surface_resolution_max_axis_fraction':max_frac,'living_coverage_fraction':cover1['living_fraction']},indent=2))
