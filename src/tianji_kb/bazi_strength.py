"""Bounded month/root/visibility observations, before overall strength judgement.

The reviewed classical material expressly rejects seasonal shortcuts and stem
counts. This v1 records inspectable factors, never invents weights or classifies
an entire chart as strong/weak. Its scope is narrower than a completed strength
classifier; keep that missing dependency visible.
"""
from .bazi_core import PILLAR_NAMES, foundations
from .foundations import stem_element

FACTOR_VARIANT = 'ditiansui-root-visibility-v1'


def factors(pillars, day_master, *, variant=FACTOR_VARIANT):
    if variant != FACTOR_VARIANT:
        raise ValueError('Unsupported strength factor variant')
    stems = [p['stem']['value'] for p in pillars]
    branches = [p['branch']['value'] for p in pillars]
    if len(pillars) != 4 or tuple(p['name'] for p in pillars) != PILLAR_NAMES:
        raise ValueError('Expected ordered year/month/day/hour pillars')
    element = stem_element(day_master)
    table = foundations()['hidden_stems']
    month_hidden = list(table[branches[1]])
    month = {'month_branch': branches[1], 'hidden_stems': month_hidden,
             'same_element_hidden_stems': [s for s in month_hidden if stem_element(s) == element],
             'siling_by_days': None, 'de_ling': None,
             'scope': '月支及藏干事实，不把藏干有日主同类当成司令或得令'}
    root_positions = []
    visible_positions = []
    for i, branch in enumerate(branches):
        for hidden in table[branch]:
            if stem_element(hidden) == element:
                root_positions.append({'pillar': PILLAR_NAMES[i], 'branch': branch,
                                       'hidden_stem': hidden, 'same_stem': hidden == day_master})
            # Day stem is the reference, not an independent exposed useful god.
            targets = [PILLAR_NAMES[j] for j, stem in enumerate(stems) if j != 2 and stem == hidden]
            if targets:
                visible_positions.append({'hidden_pillar': PILLAR_NAMES[i], 'branch': branch,
                                          'hidden_stem': hidden, 'visible_pillars': targets})
    roots = {'day_master': day_master, 'element': element, 'positions': root_positions,
             'present_structurally': bool(root_positions), 'effective_strength': None,
             'scope': '只核同五行藏干通根候选；不赋本气中气余气权重，不以冲刑自动消根'}
    visible = {'positions': visible_positions, 'day_stem_excluded': True,
               'siling_proven': False, 'scope': '支中藏干与年/月/时干同字显现，不等于取格、取用或得势'}
    return {'factor_variant': variant, 'month_command': month, 'root_candidates': roots,
            'hidden_to_visible': visible, 'overall_strength': None,
            'maturity': 'PARTIAL', 'full_strength_classifier_ready': False,
            'unresolved': ['司令分日有原典口径差异，未裁定。',
                           '季节旺相休囚与得令不等于整局强弱。',
                           '尚未定量或裁定得地、得势、生扶与克泄耗的实际效力。',
                           '成化、根受损、从格、旺极衰极与阴阳十二长生尚未纳入。',
                           '不能据本结果选喜用神、格局或断婚恋事业财富。']}
