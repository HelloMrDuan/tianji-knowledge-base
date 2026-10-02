"""Exact-term qfdk rotating-plate variant, with coherent midnight day/hour pillars."""
from ..calendar import calendar
from ..resolver import ExecutionTrace
from .qimen import chart_from_calendar, bureau, earth_plate, ORDER, STARS, DOORS

VARIANT='qfdk-exact-term-midnight-v2'

def named_stars(stars):
    result={}
    for palace,name in stars.items():
        if not name:continue
        for star in ('天禽','天芮') if name=='禽芮' else (name,):
            if star in result:raise ValueError('Duplicate star placement')
            result[star]=palace
    if set(result)!={'天蓬','天任','天冲','天辅','天英','天禽','天芮','天柱','天心'}:
        raise ValueError('Expected all nine stars in the registered rotating-plate variant')
    return result

def chart(value,variant=VARIANT):
    if variant!=VARIANT:
        raise ValueError('Unsupported Qimen variant; no school fallback')
    trace=ExecutionTrace('qimen',variant)
    cal=trace.add('qimen.phase2.calendar',{'datetime':str(value),'day_boundary':'midnight'},calendar(value))
    info=trace.add('qimen.phase2.bureau',{'solar_term':cal['solar_term'],'day_ganzhi':cal['day_ganzhi']},bureau(cal['solar_term'],cal['day_ganzhi']))
    earth=trace.add('qimen.phase2.earth',{'dun':info['dun'],'bureau':info['bureau']},earth_plate(info['dun'],info['bureau']))
    result=chart_from_calendar(cal['solar_term'],cal['day_ganzhi'],cal['hour_ganzhi'])
    result['star_positions']=named_stars(result['stars'])
    result['door_positions']={name:palace for palace,name in result['doors'].items() if name}
    result['deity_positions']={name:palace for palace,name in result['deities'].items() if name}
    result['center_star_policy']='天禽随天芮同宫（禽芮）；保留所选qfdk转盘约定'
    origin=result['chief_star_origin']
    chiefs={'chief_star':{'name':STARS[ORDER.index(origin)],'names':['天禽','天芮'] if STARS[ORDER.index(origin)]=='禽芮' else [STARS[ORDER.index(origin)]],'origin':origin,'palace':result['chief_star_palace']},
        'chief_door':{'name':DOORS[ORDER.index(origin)],'palace':result['chief_door_palace']}}
    trace.add('qimen.phase2.chiefs',{'hour_ganzhi':cal['hour_ganzhi'],'earth_plate':earth},chiefs)
    trace.add('qimen.phase2.plates',{'chiefs':chiefs,'dun':info['dun']},{k:result[k] for k in ('sky_plate','stars','doors','deities','star_positions','door_positions','deity_positions','center_star_policy')})
    result.update(chiefs,calendar=cal,variant=variant,ruleset=variant)
    return trace.finish(result,[{'rule_id':'qimen.phase2.bureau','matched':True,'dun':info['dun'],'yuan':info['yuan']}])
