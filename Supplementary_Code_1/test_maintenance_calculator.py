#!/usr/bin/env python3
"""Fresh revision-stage numerical checks; does not execute original R or simulations."""
from pathlib import Path
from copy import deepcopy
import json, math, platform, sys
import numpy as np
import scipy
from scipy.integrate import quad
from scipy.optimize import minimize_scalar
from maintenance_calculator import calculate, optimum, stale_average, checking_equation
TOL=2e-9
HERE=Path(__file__).resolve().parent

def run() -> dict:
    p=json.loads((HERE/'example_B_base.json').read_text())
    b=calculate(p)
    expected={'m':0.138047177636743,'living':0.119207513692929,'margin':0.039672997277147,'n':12.6030306333324}
    b_errors=[abs(b['scheduled']['minimum']-expected['m']),abs(b['fixed_living']['incremental_normalized_burden']-expected['living']),abs(b['fixed_living']['available_infrastructure_margin']-expected['margin']),abs(b['fixed_interval_portfolio_frontier']['continuous']-expected['n'])]
    assert max(b_errors)<TOL
    assert b['fixed_interval_portfolio_frontier']['minimum_integer']==13
    n12=deepcopy(p);n12['parameters']['portfolio_size']=12
    n13=deepcopy(p);n13['parameters']['portfolio_size']=13
    assert calculate(n12)['fixed_living']['normalized_advantage']<0
    assert calculate(n13)['fixed_living']['normalized_advantage']>0
    configurations=[('A',2,.9,.3,.1,.3,.3,.471060735605726),('B',24,.5,1.,.05,.2,.1,.119207513692929),('C',128,.2,3.,.02,.1,.03,-.060461381716394)]
    config_errors=[]
    for name,n,alpha,F,f,cl,d,total in configurations:
        case=deepcopy(p);case['parameters'].update(portfolio_size=n,attributable_fraction=alpha,shared_rate=F,readiness_rate=f,processing_living=cl,living_interval=d/.5)
        result=calculate(case);config_errors.append(abs(result['fixed_living']['incremental_normalized_burden']-total))
    assert max(config_errors)<TOL
    grid=np.unique(np.r_[np.geomspace(1e-10,0.1,140),np.linspace(.1,.999999,160)])
    root_errors=[];objective_errors=[];minimum_errors=[]
    for r in grid:
        opt=optimum(float(r));x=opt['interval'];m=opt['minimum']
        root_errors.append(abs(checking_equation(x)-r))
        objective_errors.append(abs(r/x+stale_average(x)-m))
        numeric=minimize_scalar(lambda y:r/math.exp(y)+stale_average(math.exp(y)),bounds=(math.log(x)-2,math.log(x)+2),method='bounded',options={'xatol':1e-12})
        minimum_errors.append(abs(numeric.fun-m))
    assert max(root_errors+objective_errors+minimum_errors)<TOL
    intervals=np.geomspace(1e-10,100,301)
    integral_errors=[]
    for x in intervals:
        # Different formulation: integrate age over the unit cycle.
        numerical=quad(lambda a:-math.expm1(-float(x)*a),0,1,epsabs=1e-13)[0]
        integral_errors.append(abs(numerical-stale_average(float(x))))
    assert max(integral_errors)<TOL
    units=deepcopy(p)
    for key in ['scheduled_reset','shared_rate','readiness_rate','processing_scheduled','processing_living','loss_per_stale_decision','living_release']:
        units['parameters'][key]*=137
    ub=calculate(units)
    currency_error=max(abs(ub['normalized'][k]-b['normalized'][k]) for k in ['rho','d','phi','eta','delta_c','psi'])
    months=deepcopy(p)
    for key in ['mu','shared_rate','readiness_rate','processing_scheduled','processing_living','decision_rate']:
        months['parameters'][key]/=12
    months['parameters']['living_interval']*=12
    mb=calculate(months)
    time_error=max(abs(mb['normalized'][k]-b['normalized'][k]) for k in ['rho','d','phi','eta','delta_c','psi'])
    assert max(currency_error,time_error)<TOL
    individual=deepcopy(p);individual['parameters']['incremental_shared_rate']=0
    ir=calculate(individual)
    assert ir['normalized']['phi']==0 and not ir['fixed_interval_portfolio_frontier']['applicable']
    same=deepcopy(p);same['parameters']['living_release']=same['parameters']['scheduled_reset']
    sr=calculate(same)
    assert sr['optimized_living']['comparison']=='scheduled_lower_burden'
    same['parameters']['processing_living']=.1
    assert calculate(same)['optimized_living']['comparison']=='living_lower_burden'
    assert optimum(0)['status']=='unattained_zero_interval_limit'
    assert optimum(1)['status']=='unattained_infinite_interval_limit'
    assert optimum(2)['status']=='unattained_infinite_interval_limit'
    boundary=deepcopy(p);boundary['parameters']['scheduled_reset']=2
    assert calculate(boundary)['fixed_living']['comparison']=='no_attained_scheduled_optimum_compare_infima_only'
    assert b['optimized_living']['comparison']=='one_or_both_optima_unattained_compare_infima_only'
    invalid=[('mu',0),('loss_per_stale_decision',0),('decision_rate',-1),('portfolio_size',1.5),('portfolio_size',True),('attributable_fraction',1.1),('living_interval',0),('living_release',-1),('shared_rate',float('nan')),('readiness_rate',float('inf'))]
    for key,value in invalid:
        bad=deepcopy(p);bad['parameters'][key]=value
        try:calculate(bad)
        except ValueError:pass
        else:raise AssertionError(f'Invalid {key} accepted')
    variants=[]
    for loss in [.5,1.,2.]:
        v=deepcopy(p);v['parameters']['loss_per_stale_decision']=loss
        z=calculate(v)
        assert abs(z['normalized']['rho']-.01/loss)<TOL
        assert abs(z['normalized']['phi']-b['normalized']['phi']/loss)<TOL
        variants.append({'H':loss,'rho':z['normalized']['rho'],'phi':z['normalized']['phi'],'eta':z['normalized']['eta'],'advantage':z['fixed_living']['normalized_advantage']})
    report={'status':'PASS','checked_on':'2026-10-25','scope':'Fresh Python checks of a dimensional implementation and existing results; no new R execution, no rerun of original primary/structural simulations and no empirical validation.',
    'tolerance':TOL,'configuration_total_max_abs_error':float(max(config_errors)),
    'configuration_B_reported_value_max_abs_error':float(max(b_errors)),
    'root_and_optimization_grid_size':int(len(grid)),
    'maximum_first_order_residual':float(max(root_errors)),
    'maximum_objective_identity_error':float(max(objective_errors)),
    'maximum_separate_numerical_minimization_error':float(max(minimum_errors)),
    'integration_grid_size':len(intervals),'maximum_staleness_quadrature_error':float(max(integral_errors)),
    'currency_normalization_error':float(currency_error),'time_unit_normalization_error':float(time_error),
    'integer_threshold_12_versus_13':'PASS','single_review_zero_actual_increment':'PASS',
    'same_release_and_reset_cost_with_and_without_processing_saving':'PASS',
    'unattained_boundary_handling':'PASS','invalid_input_tests':len(invalid),
    'dimensional_H_scenarios':variants,'scenario_scope':'Finite checked points only; not a proof over a continuous range.',
    'environment':{'Python':platform.python_version(),'NumPy':np.__version__,'SciPy':scipy.__version__}}
    out=HERE/'generated'/'r16_calculator_checks.json';out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(report,indent=2,allow_nan=False)+'\n')
    for source in ['example_B_base','example_B_release']:
        result=calculate(json.loads((HERE/(source+'.json')).read_text()))
        (HERE/'generated'/(source+'_result.json')).write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    return report
if __name__=='__main__':
    print(json.dumps(run(),indent=2))
