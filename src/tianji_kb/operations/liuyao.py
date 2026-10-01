import json
from pathlib import Path

STEMS = '甲乙丙丁戊己庚辛壬癸'
BRANCHES = '子丑寅卯辰巳午未申酉戌亥'
ELEMENTS = '木火土金水'
GENERATES = dict(zip(ELEMENTS, '火土金水木'))
CONTROLS = dict(zip(ELEMENTS, '土金水木火'))


def base():
    return json.loads((Path(__file__).resolve().parents[3] / 'data/canonical/liuyao/najia_v1.json').read_text())


def assign_najia(lower: str, upper: str):
    table = base()['najia']
    if lower not in table or upper not in table:
        raise ValueError('Unknown trigram')
    return table[lower][:3] + table[upper][3:]


def element_relation(a: str, b: str):
    if a not in GENERATES or b not in GENERATES:
        raise ValueError('Unknown element')
    if a == b:
        return '同我'
    if GENERATES[a] == b:
        return '我生'
    if GENERATES[b] == a:
        return '生我'
    if CONTROLS[a] == b:
        return '我克'
    return '克我'


def six_relative(palace_element: str, line_element: str):
    return base()['six_relatives'][element_relation(palace_element, line_element)]


def six_spirits(day_stem: str):
    starts = base()['six_spirits_start']
    if day_stem not in starts:
        raise ValueError('Unknown day stem')
    order = ['青龙', '朱雀', '勾陈', '螣蛇', '白虎', '玄武']
    start = order.index(starts[day_stem])
    return [order[(start + i) % 6] for i in range(6)]


def shi_ying(sequence: str):
    table = base()['shiying']['palace_sequence']
    if sequence not in table:
        raise ValueError('Unknown palace sequence')
    shi = table[sequence]
    return {'shi': shi, 'ying': (shi + 2) % 6 + 1}


def xunkong(day_ganzhi: str):
    cycle = [STEMS[i % 10] + BRANCHES[i % 12] for i in range(60)]
    if day_ganzhi not in cycle:
        raise ValueError('Invalid sexagenary day')
    start = cycle.index(day_ganzhi) // 10 * 10
    return [BRANCHES[(start + 10) % 12], BRANCHES[(start + 11) % 12]]


def branch_relation(a: str, b: str):
    if a not in list(BRANCHES) or b not in list(BRANCHES):
        raise ValueError('Unknown branch')
    combine = dict(zip(BRANCHES, '丑子亥戌酉申未午巳辰卯寅'))
    return {'combine': combine[a] == b, 'clash': (BRANCHES.index(a) - BRANCHES.index(b)) % 12 == 6}
