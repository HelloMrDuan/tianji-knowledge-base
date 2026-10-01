"""Jing Fang eight-palace chart; no auspiciousness or strength judgement."""
from ..foundations import hexagram, seed, branch_element, ganzhi_index, BRANCHES
from ..resolver import ExecutionTrace
from .liuyao import assign_najia, six_relative, six_spirits, shi_ying, xunkong

VARIANT='jingfang-eight-palaces-v1'
SEQUENCES=['本宫','一世','二世','三世','四世','五世','游魂','归魂']
MASKS=['000000','100000','110000','111000','111100','111110','111010','000010']


def palace_for(bits):
    hexagram(bits)
    for trigram in seed()['trigrams']:
        pure=trigram['binary_bottom_to_top']*2
        for sequence,mask in zip(SEQUENCES,MASKS):
            candidate=''.join(str(int(a)^int(b)) for a,b in zip(pure,mask))
            if candidate==bits:
                return {'palace':trigram['name'],'element':trigram['element'],'sequence':sequence,**shi_ying(sequence)}
    raise ValueError('Incomplete palace mapping')


def chart(yao_values,day_ganzhi,month_branch,variant=VARIANT):
    if variant!=VARIANT:
        raise ValueError('Unsupported Liuyao variant')
    if not isinstance(yao_values,(list,tuple)) or len(yao_values)!=6 or any(type(v) is not int or v not in (6,7,8,9) for v in yao_values):
        raise ValueError('Expected six integer yao values 6/7/8/9, bottom to top')
    ganzhi_index(day_ganzhi)
    if month_branch not in list(BRANCHES):
        raise ValueError('Expected one month branch')
    trace=ExecutionTrace('liuyao',variant)
    bits=''.join('1' if v in (7,9) else '0' for v in yao_values)
    changed=''.join('1' if v in (6,7) else '0' for v in yao_values)
    movement=trace.add('liuyao.phase2.motion',{'yao_values':list(yao_values)},
        {'original':hexagram(bits),'changed':hexagram(changed),'changing_lines':[i+1 for i,v in enumerate(yao_values) if v in (6,9)]})
    palace=trace.add('liuyao.phase2.palace',{'binary':bits},palace_for(bits))
    changed_palace=palace_for(changed)
    najia=trace.add('liuyao.phase2.najia',{'lower':movement['original']['lower'],'upper':movement['original']['upper']},assign_najia(movement['original']['lower'],movement['original']['upper']))
    changed_najia=assign_najia(movement['changed']['lower'],movement['changed']['upper'])
    spirits=trace.add('liuyao.phase2.spirits',{'day_stem':day_ganzhi[0]},six_spirits(day_ganzhi[0]))
    empty=trace.add('liuyao.phase2.empty',{'day_ganzhi':day_ganzhi},xunkong(day_ganzhi))
    relative=trace.add('liuyao.phase2.relatives',{'palace_element':palace['element'],'branches':[g[1] for g in najia]},[six_relative(palace['element'],branch_element(g[1])) for g in najia])
    broken=trace.add('liuyao.phase2.month_break',{'month_branch':month_branch},[i+1 for i,g in enumerate(najia) if (BRANCHES.index(g[1])-BRANCHES.index(month_branch))%12==6])
    lines=[{'position':i+1,'value':v,'moving':v in (6,9),'najia':najia[i],'element':branch_element(najia[i][1]),
            'relative':relative[i],'spirit':spirits[i],'empty':najia[i][1] in empty,'month_break':i+1 in broken,
            'changed_najia':changed_najia[i],
            'changed_relative_to_original_palace':six_relative(palace['element'],branch_element(changed_najia[i][1]))} for i,v in enumerate(yao_values)]
    return trace.finish({**movement,'palace':palace,'changed_palace':changed_palace,'lines':lines,'empty_branches':empty},
        [{'rule_id':'liuyao.phase2.month_break','line':position,'matched':True} for position in broken])
