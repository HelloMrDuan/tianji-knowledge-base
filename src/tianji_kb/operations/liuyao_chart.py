"""Jing Fang eight-palace chart; no auspiciousness or strength judgement."""
import json
from functools import lru_cache
from pathlib import Path

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


@lru_cache(maxsize=1)
def _reviewed_zhouyi_core():
    """Protected 64-hexagram classical text, never a generated fortune reading."""
    path = Path(__file__).resolve().parents[3] / 'data/canonical/yijing/zhouyi_classic_core.json'
    document = json.loads(path.read_text(encoding='utf-8'))
    if (document.get('domain') != 'yijing' or document.get('corpus') != 'zhouyi_classic_core'
            or document.get('source_level') != 'L0-public-domain-classic'
            or document.get('record_count') != 64
            or len(document.get('records', [])) != 64):
        raise ValueError('Reviewed Zhouyi classic corpus is incomplete')
    records = {}
    for item in document['records']:
        number = item.get('number')
        if (type(number) is not int or not 1 <= number <= 64 or number in records
                or not isinstance(item.get('full_name'), str) or not item['full_name'].strip()
                or not isinstance(item.get('judgment'), str) or not item['judgment'].strip()
                or not isinstance(item.get('image'), str) or not item['image'].strip()
                or len(item.get('lines', [])) != 6
                or any(not isinstance(line.get('position'), str)
                       or not isinstance(line.get('text'), str)
                       or not line['text'].strip() for line in item['lines'])):
            raise ValueError('Reviewed Zhouyi classic excerpt structure is invalid')
        records[number] = item
    if len(records) != 64:
        raise ValueError('A complete, unique sixty-four-hexagram corpus is required')
    return records


def _classical_reading(original, changed, changing_lines):
    """Return exact historical excerpts linked to this calculated hexagram."""
    corpus = _reviewed_zhouyi_core()
    source = corpus[original['number']]
    target = corpus[changed['number']]
    # Arrays in the audited classic core run from initial line to top line.
    if any(type(pos) is not int or pos not in range(1, 7) for pos in changing_lines):
        raise ValueError('Invalid moving line for reviewed Zhouyi text')
    return {
        'title': '《周易》卦辞与爻辞',
        'source_level': 'L0-public-domain-classic',
        'original': {
            'number': source['number'],
            'name': source['full_name'],
            'judgment': source['judgment'],
            'image': source['image'],
            'moving_line_texts': [
                {'line': pos, 'position': source['lines'][pos - 1]['position'],
                 'text': source['lines'][pos - 1]['text']}
                for pos in changing_lines
            ],
        },
        'changed': {
            'number': target['number'],
            'name': target['full_name'],
            'judgment': target['judgment'],
        },
        'scope': 'verbatim_classical_excerpts_only',
        'personal_prediction': False,
        'limitations': '仅供查阅传世《周易》卦辞、象辞及本卦动爻原文；不代表已审核的事件断语。',
    }


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
    classic = _classical_reading(movement['original'], movement['changed'], movement['changing_lines'])
    return trace.finish({**movement,'palace':palace,'changed_palace':changed_palace,'lines':lines,
                         'empty_branches':empty,'zhouyi_classic':classic},
        [{'rule_id':'liuyao.phase2.month_break','line':position,'matched':True} for position in broken])
