"""Compass mappings; absolute period epochs stay behind the explicit research gate."""
from .fengshui import mountain_at
from ..resolver import ExecutionTrace
VARIANT='compass-half-open-explicit-epoch-v1'
DIRECTIONS={'北':('坎','水'),'东北':('艮','土'),'东':('震','木'),'东南':('巽','木'),'南':('离','火'),'西南':('坤','土'),'西':('兑','金'),'西北':('乾','金')}

def relative_period(year,epoch_year):
    if type(year) is not int or type(epoch_year) is not int:
        raise ValueError('Integer year and caller-supplied upper-yuan epoch required')
    slot=(year-epoch_year)//20
    start=epoch_year+slot*20
    return {'yuan':['上元','中元','下元'][(slot%9)//3],'period':slot%9+1,
        'start_year':start,'end_year':start+19,'production_eligible':False,
        'epoch_year':epoch_year,'epoch_evidence_level':'D',
        'boundary_policy':'caller-supplied integer years; no verified solar-term epoch'}

def chart(degrees,year=None,epoch_year=None,research=False,variant=VARIANT):
    if variant!=VARIANT:raise ValueError('Unsupported Fengshui variant')
    if type(research) is not bool:raise ValueError('research must be boolean')
    if year is None and epoch_year is not None:raise ValueError('Epoch requires year')
    if year is not None and (not research or epoch_year is None):
        raise ValueError('Unverified absolute period requires research=True and explicit epoch_year')
    mountain=mountain_at(degrees)
    trigram,element=DIRECTIONS[mountain['direction']]
    result={'degrees':degrees%360,'mountain':mountain['mountain'],'mountain_element':mountain['element'],
        'trigram':trigram,'trigram_element':element,'opposite':mountain['opposite']['mountain'],'period':None}
    trace=ExecutionTrace('fengshui',variant)
    trace.add('fengshui.phase2.compass',{'degrees':degrees},result)
    if year is not None:
        result['period']=relative_period(year,epoch_year)
        trace.add('fengshui.phase2.relative_period',{'year':year,'epoch_year':epoch_year,'research':True},result['period'])
    return trace.finish(result)
