"""Lunar-input Ziwei skeleton; named iztro mutagen convention is retained explicitly."""
from ..foundations import STEMS,BRANCHES,ganzhi_index
from ..resolver import ExecutionTrace
from .ziwei import lucun,tianma,four_transformations

VARIANT='quanshu-lunar-iztro-mutagen-v1'
PALACES=['命宫','兄弟','夫妻','子女','财帛','疾厄','迁移','仆役','官禄','田宅','福德','父母']


def branch(i):return BRANCHES[i%12]
def bureau_for(stem,br):
    # Formalized Na Yin pair table, not a literal ancient arithmetic quotation.
    index=((STEMS.index(stem)//2+1)+(BRANCHES.index(br)%6//2+1)-1)%5
    element=['木','金','水','火','土'][index]
    return {'element':element,'number':{'木':3,'金':4,'水':2,'火':6,'土':5}[element]}


def ziwei_position(day,number):
    offset=(-day)%number
    relative=((day+offset)//number-1+(offset if offset%2==0 else -offset))%12
    return (relative+2)%12


def compute(year_ganzhi,lunar_month,lunar_day,hour_branch):
    ganzhi_index(year_ganzhi)
    if type(lunar_month) is not int or not 1<=lunar_month<=12 or type(lunar_day) is not int or not 1<=lunar_day<=30 or hour_branch not in list(BRANCHES):
        raise ValueError('Expected non-leap lunar month 1..12, day 1..30 and hour branch')
    hour=BRANCHES.index(hour_branch)
    life=(lunar_month+1-hour)%12;body=(lunar_month+1+hour)%12
    stem_index=(STEMS.index(year_ganzhi[0])%5*2+2+(life-2)%12)%10
    life_stem=STEMS[stem_index]
    bureau=bureau_for(life_stem,branch(life))
    z=ziwei_position(lunar_day,bureau['number']);f=(4-z)%12
    major={name:branch(z+offset) for name,offset in [('紫微',0),('天机',-1),('太阳',-3),('武曲',-4),('天同',-5),('廉贞',-8)]}
    major.update({name:branch(f+offset) for name,offset in [('天府',0),('太阴',1),('贪狼',2),('巨门',3),('天相',4),('天梁',5),('七杀',6),('破军',10)]})
    l=BRANCHES.index(lucun(year_ganzhi[0]))
    aux={'左辅':branch(4+lunar_month-1),'右弼':branch(10-lunar_month+1),'文昌':branch(10-hour),'文曲':branch(4+hour),'禄存':branch(l),'擎羊':branch(l+1),'陀罗':branch(l-1),'天马':tianma(year_ganzhi[1]),'地劫':branch(11+hour),'地空':branch(11-hour)}
    return {'life_palace':branch(life),'body_palace':branch(body),'life_ganzhi':life_stem+branch(life),
        'bureau':bureau,'palaces':{name:branch(life-i) for i,name in enumerate(PALACES)},
        'major_stars':major,'auxiliary_stars':aux,'four_transformations':four_transformations(year_ganzhi[0],'iztro-default-v2'),
        'mutagen_variant':'iztro-default-v2','mutagen_evidence':'D implementation table; classical types are C; 壬府/辅 unresolved',
        'input_scope':'显式非闰月农历；年干支由调用方按约定年界提供；无大限流年或庙旺吉凶'}


def chart(year_ganzhi,lunar_month,lunar_day,hour_branch,variant=VARIANT):
    if variant!=VARIANT:raise ValueError('Unsupported Ziwei variant')
    result=compute(year_ganzhi,lunar_month,lunar_day,hour_branch)
    trace=ExecutionTrace('ziwei',variant)
    inputs={'year_ganzhi':year_ganzhi,'lunar_month':lunar_month,'lunar_day':lunar_day,'hour_branch':hour_branch}
    for stage,keys in [('life_body',['life_palace','body_palace']),('bureau',['life_ganzhi','bureau']),('palaces',['palaces']),('major_stars',['major_stars']),('auxiliary_stars',['auxiliary_stars']),('mutagens',['four_transformations','mutagen_variant','mutagen_evidence'])]:
        trace.add('ziwei.phase2.'+stage,inputs,{key:result[key] for key in keys})
    return trace.finish(result)
