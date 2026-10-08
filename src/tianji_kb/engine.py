"""Six registered deterministic chart providers; no LLM or quarantine computation."""
import importlib
from .resolver import EvidenceResolver
from .calendar import calendar
from .foundations import CYCLE
from .bazi_adjudication import ADJUDICATION_VARIANT

PROVIDERS={domain:f'tianji_kb.operations.{domain}_chart.chart' for domain in ('liuyao','qimen','liuren','ziwei','fengshui','yijing','bazi')}

def prepare_inputs(domain,inputs):
    inputs=dict(inputs)
    if domain not in ('liuyao','liuren','ziwei','bazi') or 'value' not in inputs:
        return inputs,None
    value=inputs.pop('value')
    derived={'liuyao':{'day_ganzhi','month_branch'},'liuren':{'solar_term','day_ganzhi','hour_branch'},
             'ziwei':{'year_ganzhi','lunar_month','lunar_day','hour_branch'},
             'bazi':{'year_ganzhi','month_ganzhi','day_ganzhi','hour_ganzhi'}}[domain]
    if derived.intersection(inputs):raise ValueError('Datetime and manually supplied calendar pillars cannot be mixed')
    if domain=='ziwei' and inputs.pop('year_boundary',None)!='lunar-new-year':
        raise ValueError('Ziwei datetime input requires explicit year_boundary=lunar-new-year')
    cal=calendar(value)
    if domain=='liuyao':inputs.update(day_ganzhi=cal['day_ganzhi'],month_branch=cal['month_ganzhi'][1])
    elif domain=='bazi':inputs.update(year_ganzhi=cal['year_ganzhi'],month_ganzhi=cal['month_ganzhi'],day_ganzhi=cal['day_ganzhi'],hour_ganzhi=cal['hour_ganzhi'])
    elif domain=='liuren':inputs.update(solar_term=cal['solar_term'],day_ganzhi=cal['day_ganzhi'],hour_branch=cal['hour_ganzhi'][1])
    else:
        if cal['lunar_month']<0:raise ValueError('Leap-lunar-month convention is unresolved; datetime chart rejected')
        inputs.update(year_ganzhi=CYCLE[(cal['lunar_year']-4)%60],lunar_month=cal['lunar_month'],
                      lunar_day=cal['lunar_day'],hour_branch=cal['hour_ganzhi'][1])
        cal['ziwei_year_boundary']='lunar-new-year'
    return inputs,cal

def execute(domain,inputs,variant=None,*,allow_research=False):
    if domain not in PROVIDERS or not isinstance(inputs,dict):
        raise ValueError('Expected a registered Phase 2 domain and JSON object inputs')
    if type(allow_research) is not bool:raise ValueError('allow_research must be boolean')
    if domain == 'bazi' and inputs.get('strength_variant') == ADJUDICATION_VARIANT and not allow_research:
        raise ValueError('Bounded strength adjudication requires explicit research mode')
    if domain == 'bazi' and inputs.get('pattern_variant') is not None and not allow_research:
        raise ValueError('Pattern candidate observations require explicit research mode')
    if domain == 'bazi' and inputs.get('annual_reference_years') is not None and not allow_research:
        raise ValueError('Annual calendar references require explicit research mode')
    if domain == 'bazi' and inputs.get('annual_boundary_years') is not None and not allow_research:
        raise ValueError('Li Chun annual boundaries require explicit research mode')
    if domain == 'bazi' and (inputs.get('dayun_sequence_direction') is not None or 'dayun_sequence_count' in inputs) and not allow_research:
        raise ValueError('Dayun sequence candidates require explicit research mode')
    contract=EvidenceResolver().contracts[domain]
    if contract['provider']!=PROVIDERS[domain]:raise ValueError('Provider differs from reviewed allowlist')
    selected=variant if variant is not None else contract['variant']
    if selected!=contract['variant']:raise ValueError('Unsupported chart variant')
    if 'variant' in inputs:raise ValueError('Specify variant separately from inputs')
    if domain=='fengshui' and (inputs.get('year') is not None or inputs.get('research')) and not allow_research:
        raise ValueError('Absolute period epochs are unavailable through the production gateway')
    prepared,cal=prepare_inputs(domain,inputs)
    module,name=PROVIDERS[domain].rsplit('.',1)
    result=getattr(importlib.import_module(module),name)(**prepared,variant=selected)
    if result['variant']!=selected or not result['deterministic']:
        raise ValueError('Execution contract mismatch')
    if cal is not None:result['input_calendar']=cal
    result['scope']=contract.get('scope','')
    result['unresolved']=contract.get('unresolved',[])
    result['mode']='research' if allow_research else 'production'
    return result
