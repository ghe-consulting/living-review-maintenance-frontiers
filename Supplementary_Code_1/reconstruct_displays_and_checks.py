#!/usr/bin/env python3
"""Revision-stage display reconstruction and analytical checks.

This ADDENDUM is not a replacement for the original v1.0.1 R/Python archive.
It uses the original mathematical model and frozen display constants, preserves
reported synthetic summaries, and checks a newly stated analytical corollary.
No primary simulation is reclassified or re-estimated by this script.

Usage: python reconstruct_displays_and_checks.py --output ./generated
Requires Python 3.10+, NumPy, SciPy, matplotlib. No network access is required.
"""
from __future__ import annotations
import argparse
import csv
import json
import math
import platform
from pathlib import Path
import numpy as np
import scipy
from scipy.optimize import brentq, minimize_scalar
from scipy.special import gammainc, gamma
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ARCHITECTURES = [
    dict(id='A', label='A: small isolated/manual', n=2, alpha=.9, omega=.3,
         eta=.1, dc=.1, d=.3, reported_c=.47106073560572614,
         reported_rho_be=.13418901577838122),
    dict(id='B', label='B: shared balanced', n=24, alpha=.5, omega=1.,
         eta=.05, dc=0., d=.1, reported_c=.11920751369292906,
         reported_rho_be=.007405683605534855),
    dict(id='C', label='C: large automation-assisted', n=128, alpha=.2, omega=3.,
         eta=.02, dc=-.1, d=.03, reported_c=-.060461381716394036,
         reported_rho_be=0.),
]


def g(x: float) -> float:
    if not math.isfinite(x) or x < 0:
        raise ValueError('The interval must be finite and nonnegative.')
    if x < 1e-5:
        return x/2-x*x/6+x**3/24-x**4/120+x**5/720
    return 1+math.expm1(-x)/x


def h(x: float) -> float:
    if x < 1e-4:
        return x*x/2-x**3/3+x**4/8-x**5/30+x**6/144
    return -math.expm1(-x)-x*math.exp(-x)


def optimum(q: float) -> float:
    if not 0 < q < 1:
        raise ValueError('A finite positive optimum requires 0 < q < 1.')
    hi = 1.
    while h(hi) < q:
        hi *= 2
    return float(brentq(lambda x: h(x)-q, 0, hi, xtol=5e-15, rtol=1e-14))


def minimum(q: float) -> float:
    return -math.expm1(-optimum(q))


def cadence(target: float) -> float:
    if target <= 0:
        return math.nan
    if target >= 1:
        return math.inf
    hi = 1.
    while g(hi) < target:
        hi *= 2
    return float(brentq(lambda x: g(x)-target, 0, hi, xtol=1e-12))


def weibull_integral(x: float, shape: float) -> float:
    return float(gamma(1+1/shape)*gammainc(1/shape, x**shape))


def weibull_minimum(q: float, shape: float) -> float:
    M = float(gamma(1+1/shape))
    if not 0 < q < M:
        raise ValueError('Outside the finite Weibull optimum domain.')
    def characteristic(x):
        return weibull_integral(x, shape)-x*math.exp(-x**shape)
    hi=1.
    while characteristic(hi) < q:
        hi *= 2
    x=brentq(lambda z: characteristic(z)-q, 0, hi, xtol=5e-13)
    return -math.expm1(-x**shape)


def save_csv(path, header, rows):
    with path.open('w', newline='', encoding='utf-8') as f:
        writer=csv.writer(f); writer.writerow(header); writer.writerows(rows)


def save_plot(fig, out, stem):
    fig.tight_layout()
    fig.savefig(out/f'{stem}.png', dpi=350)
    fig.savefig(out/f'{stem}.pdf')
    plt.close(fig)


def axes():
    fig, ax = plt.subplots(figsize=(7.1, 4.55))
    ax.tick_params(labelsize=11)
    return fig, ax


def run(out: Path):
    out.mkdir(parents=True, exist_ok=True)
    rho=np.linspace(.0001,.999,1000)
    m=np.array([minimum(float(q)) for q in rho])
    xs=np.array([optimum(float(q)) for q in rho])
    styles=['-', '--', '-.', ':', (0,(5,2,1,2,1,2))]
    reports={}
    worked=[]
    max_arch_error=0.
    for a in ARCHITECTURES:
        phi=a['alpha']*a['omega']/a['n']
        c=phi+a['eta']+a['dc']+g(a['d'])
        be=0. if c <= 0 else c+(1-c)*math.log1p(-c)
        max_arch_error=max(max_arch_error, abs(c-a['reported_c']), abs(be-a['reported_rho_be']))
        B=minimum(.01)-g(a['d'])-a['eta']-a['dc']
        worked.append(dict(id=a['id'], n=a['n'], phi=phi, eta=a['eta'],
                           dc=a['dc'], staleness=g(a['d']), total_incremental=c,
                           rho_be=be, m_at_rho_001=minimum(.01),
                           advantage_at_rho_001=minimum(.01)-c,
                           margin_B_at_rho_001=B,
                           n_be_at_rho_001=None if B<=0 else a['alpha']*a['omega']/B))
    reports['architecture_reconciliation']={'max_absolute_difference':max_arch_error,
        'tolerance':2e-12,'pass':max_arch_error<2e-12}
    reports['worked_example']=worked
    reports['worked_example_status']='Revision-stage calculation at a previously prespecified boundary value; not a new simulation.'

    fig,ax=axes()
    for i,a in enumerate(ARCHITECTURES):
        ax.plot(rho,m-a['reported_c'], linestyle=styles[i], linewidth=2,
                label=a['label'])
    ax.axhline(0, linewidth=.9, linestyle=':')
    ax.set(xlabel=r'Reset-to-consequence ratio, $\rho$',
           ylabel='Living advantage (normalised burden)', xlim=(0,1))
    ax.legend(loc='lower right', fontsize=10, frameon=False)
    save_plot(fig,out,'Figure_1_architectures')
    save_csv(out/'Figure_1_source.csv',['rho','advantage_A','advantage_B','advantage_C'],
             zip(rho,*[m-a['reported_c'] for a in ARCHITECTURES]))

    fig,ax=axes(); crows=[]
    bs=[0.,.05,.15,.3]
    for i,b in enumerate(bs):
        dvals=np.array([cadence(float(mm)-b) for mm in m])
        ax.plot(rho,dvals,linestyle=styles[i],linewidth=2,label=f'b = {b:g}')
        crows.extend(zip(rho,[b]*len(rho),dvals))
    ax.set(xlabel=r'Reset-to-consequence ratio, $\rho$',
           ylabel=r'Break-even living interval, $d_{BE}$',xlim=(0,1),ylim=(0,10))
    ax.legend(fontsize=11,frameon=False,loc='upper left')
    ax.text(.98,.03,'Living below each frontier',transform=ax.transAxes,
            ha='right',fontsize=11)
    save_plot(fig,out,'Figure_2_cadence')
    save_csv(out/'Figure_2_source.csv',['rho','b','d_be'],crows)

    fig,ax=axes(); prows=[]
    B=m-g(.1)-.05
    for i,cost in enumerate([.05,.2,.5,1.]):
        values=np.where(B>0,cost/np.where(B>0,B,np.nan),np.nan)
        ax.plot(rho,values,linestyle=styles[i],linewidth=2,
                label=rf'$\alpha F/Q$ = {cost:g}')
        prows.extend(zip(rho,[cost]*len(rho),values))
    threshold=(g(.1)+.05)+(1-g(.1)-.05)*math.log1p(-(g(.1)+.05))
    ax.axvline(threshold,linestyle=':',linewidth=1)
    ax.axhline(1,linestyle=':',linewidth=1)
    ax.set(xlabel=r'Reset-to-consequence ratio, $\rho$',
           ylabel=r'Continuous portfolio threshold, $n_{BE}$',
           xlim=(0,1),ylim=(.04,2000),yscale='log')
    ax.legend(fontsize=10,frameon=False,loc='upper right')
    save_plot(fig,out,'Figure_3_portfolio')
    save_csv(out/'Figure_3_source.csv',['rho','alpha_F_over_Q','n_be'],prows)

    fig,ax=axes()
    ax.plot(rho,xs,linewidth=2,label='Exact optimum')
    ax.plot(rho,np.sqrt(2*rho),linestyle='--',linewidth=2,label='Square-root approximation')
    ax.set(xlabel=r'Reset-to-consequence ratio, $\rho$',ylabel=r'Scheduled interval, $x$',xlim=(0,1))
    ax.legend(fontsize=11,frameon=False)
    save_plot(fig,out,'Figure_S1_exact_interval')

    fig,ax=axes()
    ax.plot(rho,100*(xs-np.sqrt(2*rho))/xs,linewidth=2)
    ax.set(xlabel=r'Reset-to-consequence ratio, $\rho$',
           ylabel='Relative interval error (%)',xlim=(0,1))
    save_plot(fig,out,'Figure_S2_approximation_error')
    save_csv(out/'Figures_S1_S2_source.csv',['rho','x_exact','x_sqrt','relative_interval_error'],
             zip(rho,xs,np.sqrt(2*rho),(xs-np.sqrt(2*rho))/xs))

    rs=np.linspace(.0001,.85,650)
    phi=ARCHITECTURES[1]['alpha']/ARCHITECTURES[1]['n']; eta=.05; d=.1
    fig,ax=axes(); wrows=[]
    for i,k in enumerate([.5,.75,1.,1.5,2.]):
        mk=np.array([weibull_minimum(float(q),k) for q in rs])
        gk=1-weibull_integral(d,k)/d
        av=mk-phi-eta-gk
        ax.plot(rs,av,linestyle=styles[i],linewidth=2,label=f'k = {k:g}')
        wrows.extend(zip(rs,[k]*len(rs),av))
    ax.axhline(0,linewidth=.9,linestyle=':')
    ax.set(xlabel=r'Reset-to-consequence ratio, $\rho$',
           ylabel='Living advantage (normalised burden)',xlim=(0,.85))
    ax.legend(fontsize=10,frameon=False,loc='lower right')
    save_plot(fig,out,'Figure_S3_Weibull')
    save_csv(out/'Figure_S3_source.csv',['rho','k','advantage'],wrows)

    fig,ax=axes(); rrows=[]
    for i,psi in enumerate([0.,.0025,.01,.04]):
        av=m-ARCHITECTURES[1]['reported_c']-psi/.1
        ax.plot(rho,av,linestyle=styles[i],linewidth=2,label=rf'$\psi$ = {psi:g}')
        rrows.extend(zip(rho,[psi]*len(rho),av))
    ax.axhline(0,linewidth=.9,linestyle=':')
    ax.set(xlabel=r'Reset-to-consequence ratio, $\rho$',
           ylabel='Living advantage (normalised burden)',xlim=(0,1))
    ax.legend(fontsize=10,frameon=False,loc='lower right')
    save_plot(fig,out,'Figure_S4_release_overhead')
    save_csv(out/'Figure_S4_source.csv',['rho','psi','advantage_fixed_d_01'],rrows)

    # Independent check: minimise on log interval rather than solve the analytic FOC.
    qgrid=np.unique(np.r_[np.geomspace(1e-6,.1,80),np.linspace(.1,.999,160)])
    max_min_error=0.; max_stationarity=0.; max_identity=0.; checks=[]
    for q in qgrid:
        x=optimum(float(q)); exact=minimum(float(q))
        fit=minimize_scalar(lambda u:q/math.exp(u)+g(math.exp(u)),
                            bounds=(-16,6),method='bounded',
                            options={'xatol':1e-12})
        error=abs(float(fit.fun)-exact)
        max_min_error=max(max_min_error,error)
        max_stationarity=max(max_stationarity,abs(h(x)-q))
        max_identity=max(max_identity,abs(q/x+g(x)-exact))
        checks.append((q,x,exact,fit.fun,error))
    reports['scheduled_and_release_corollary_checks']={
        'q_values':len(qgrid),'method':'Brent root versus separate bounded minimisation on log interval',
        'maximum_minimum_value_difference':max_min_error,
        'maximum_first_order_residual':max_stationarity,
        'maximum_minimum_identity_residual':max_identity,
        'tolerance':2e-9,'pass':bool(max_min_error<2e-9 and max_identity<2e-9),
        'status':'New revision-stage numerical check; does not assert re-execution of archived R validation.'}
    save_csv(out/'corollary_checks.csv',['q','optimum','exact_minimum','numerical_minimum','abs_difference'],checks)
    reports['executable_context']={'python':platform.python_version(),'numpy':np.__version__,
        'scipy':scipy.__version__,'matplotlib':matplotlib.__version__,'R_executed':False}
    reports['original_scientific_results_changed']=False
    reports['original_repository_release']='v1.0.1'
    reports['display_parameters_source']='protocol/figure_constants.json, blob dd5a007fce93e4221ed0675683a9abb4861c1b45'
    reports['architecture_source']='results/numerical_summary.json, blob 07f790c4fe0456b52173f0c4b67c32daf3c05b5e'
    reports['display_changes']='Figures reordered, individual panels separated, unbounded cadence curves not flattened at plot limit, portfolio surface shown as curves at frozen shared-burden constants.'
    (out/'revision_verification.json').write_text(json.dumps(reports,indent=2,allow_nan=False),encoding='utf-8')
    assert reports['architecture_reconciliation']['pass']
    assert reports['scheduled_and_release_corollary_checks']['pass']
    return reports

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output',type=Path,default=Path(__file__).parent/'generated')
    args=p.parse_args()
    result=run(args.output)
    print(json.dumps({'status':'PASS','output':str(args.output),
                      'architecture_max_error':result['architecture_reconciliation']['max_absolute_difference'],
                      'minimum_max_error':result['scheduled_and_release_corollary_checks']['maximum_minimum_value_difference']},indent=2))
