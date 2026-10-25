#!/usr/bin/env python3
"""R13 presentation addendum: an explanatory balance chart, not a new simulation.

Uses unchanged synthetic inputs and equations from the R12 reconstruction.
Run: python explain_workflows.py --output generated
No network, model fitting, R execution or re-estimation of frozen results occurs.
"""
from __future__ import annotations
import argparse, csv, json, math, platform
from pathlib import Path
import numpy as np
import scipy
from scipy.integrate import quad
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from reconstruct_displays_and_checks import ARCHITECTURES, g, optimum, minimum


def run(out: Path) -> dict:
    out.mkdir(parents=True, exist_ok=True)
    rho=0.01
    benchmark=minimum(rho)
    rows=[]
    for a in ARCHITECTURES:
        shared=a['alpha']*a['omega']/a['n']
        nonshared=a['eta']+a['dc']+g(a['d'])
        margin=benchmark-nonshared
        total=nonshared+shared
        threshold=None if margin<=0 else a['alpha']*a['omega']/margin
        rows.append(dict(configuration=a['id'],n=a['n'],rho=rho,readiness=a['eta'],
            processing_difference=a['dc'],staleness=g(a['d']),non_shared_subtotal=nonshared,
            infrastructure_margin=margin,shared_charge=shared,total_incremental_living_burden=total,
            optimized_scheduled_burden=benchmark,living_advantage=benchmark-total,
            continuous_portfolio_threshold=threshold,
            minimum_integer_portfolio=None if threshold is None else max(1,math.floor(threshold)+1),
            archived_total=a['reported_c'],difference_from_archived=total-a['reported_c']))
    with (out/'Figure_1_balance_source.csv').open('w',newline='',encoding='utf-8') as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)

    fig,ax=plt.subplots(figsize=(7.4,4.7))
    x=np.arange(3);w=.33
    margins=np.array([r['infrastructure_margin'] for r in rows])
    charges=np.array([r['shared_charge'] for r in rows])
    bars1=ax.bar(x-w/2,margins,w,label='Margin available for infrastructure (B)')
    bars2=ax.bar(x+w/2,charges,w,label='Actual shared charge (φ)',hatch='//')
    ax.axhline(0,linewidth=.8,linestyle=':')
    for bars in [bars1,bars2]:
        for rect in bars:
            h=rect.get_height()
            ax.annotate(f'{h:.4f}',(rect.get_x()+rect.get_width()/2,h),
                        xytext=(0,5 if h>=0 else -5),textcoords='offset points',
                        ha='center',va='bottom' if h>=0 else 'top',fontsize=10)
    ax.set_xticks(x,['A: small/manual\n2 reviews','B: shared/balanced\n24 reviews','C: processing saving\n128 reviews'])
    ax.set_ylabel('Burden per unit time, relative to Q')
    ax.set_ylim(-.255,.30)
    ax.tick_params(labelsize=10)
    ax.legend(loc='upper left',frameon=False,fontsize=10)
    fig.tight_layout()
    fig.savefig(out/'Figure_1_balance.png',dpi=450)
    fig.savefig(out/'Figure_1_balance.pdf')
    plt.close(fig)

    # Separate quadrature checks the stale-probability expression at diverse intervals.
    intervals=np.geomspace(1e-7,100,301)
    quad_error=max(abs(g(float(t))-quad(lambda u:-math.expm1(-u),0,float(t),epsabs=1e-12)[0]/float(t)) for t in intervals)
    # Physical-unit calculation must agree with the normalized objective.
    # Q and mu are arbitrary scaling choices, not programme estimates.
    Q,mu,baseline=1000.,.5,400.
    dimensional_error=0.
    T=optimum(rho)/mu
    S=rho*Q/mu
    physical_scheduled=S/T+baseline+Q*g(mu*T)
    for a,r in zip(ARCHITECTURES,rows):
        physical_living=a['alpha']*(a['omega']*Q)/a['n']+a['eta']*Q+baseline+a['dc']*Q+Q*g(a['d'])
        dimensional_error=max(dimensional_error,abs((physical_scheduled-physical_living)/Q-r['living_advantage']))
    report=dict(status='PASS',date='2026-10-24',scope='Explanatory presentation checks only; no primary or structural simulation rerun and no R execution.',
        worked_examples=rows,
        calendar_mapping=dict(mu_per_year=.5,mean_material_change_years=2.,living_B_months=.1/.5*12,
                              scheduled_months=T*12,source='mu=0.5 is an existing synthetic interpretive mapping, not an empirical input.'),
        maximum_archived_configuration_difference=max(abs(r['difference_from_archived']) for r in rows),
        stale_probability_quadrature=dict(intervals=301,max_absolute_difference=quad_error,tolerance=2e-9),
        dimensional_identity=dict(max_absolute_difference=dimensional_error,tolerance=2e-9),
        runtime=dict(python=platform.python_version(),numpy=np.__version__,scipy=scipy.__version__,matplotlib=matplotlib.__version__))
    assert report['maximum_archived_configuration_difference']<2e-9
    assert quad_error<2e-9 and dimensional_error<2e-9
    assert rows[1]['minimum_integer_portfolio']==13
    assert rows[0]['infrastructure_margin']<0
    assert rows[2]['infrastructure_margin']>rows[2]['shared_charge']
    (out/'R13_explanatory_checks.json').write_text(json.dumps(report,indent=2,allow_nan=False),encoding='utf-8')
    return report

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,default=Path(__file__).parent/'generated')
    args=parser.parse_args()
    print(json.dumps(run(args.output),indent=2))
