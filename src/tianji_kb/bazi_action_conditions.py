"""Relation direction and its observed conditions, without assumed efficacy."""
from .bazi_core import PILLAR_NAMES, foundations
from .foundations import stem_element

ACTION_VARIANT = 'ditiansui-action-conditions-v1'


def action_conditions(pillars, day_master, *, support, relations, month_command,
                      action_variant=ACTION_VARIANT):
    if action_variant != ACTION_VARIANT:
        raise ValueError('Unsupported conditional action variant')
    if len(pillars) != 4 or tuple(p['name'] for p in pillars) != PILLAR_NAMES:
        raise ValueError('Expected ordered year/month/day/hour pillars')
    table = foundations()['hidden_stems']
    visible = []
    for row in support['visible_positions']:
        pillar = row['pillar']
        index = PILLAR_NAMES.index(pillar)
        root_positions = [{'pillar': p['name'], 'branch': p['branch']['value'], 'hidden_stem': h,
                           'same_stem': h == row['stem']}
                          for p in pillars for h in table[p['branch']['value']]
                          if stem_element(h) == row['element']]
        exposures = [r for r in root_positions if r['same_stem']]
        stem_combinations = [r for r in relations['stem_five_combinations'] if pillar in r['pillars']]
        branch_relations = [{'kind': k, **r} for k in ('branch_six_clashes', 'branch_six_harmonies',
                             'branch_six_harms', 'branch_triple_harmonies') for r in relations[k]
                            if any(p['pillar'] in r['pillars'] for p in root_positions)]
        visible.append({
            'fact': {**row, 'visibility': 'visible', 'pillar_distance_to_day': abs(index - 2),
                     'adjacent_to_day': abs(index - 2) == 1,
                     'root_positions': root_positions, 'rooted_visible_candidate': bool(root_positions),
                     'hidden_same_stem_positions': exposures},
            'conditions': {'month_commander_status': month_command['commander_status'],
                           'stem_combinations': stem_combinations, 'root_branch_relations': branch_relations,
                           'season_effect': 'unresolved', 'root_availability': 'unresolved',
                           'proximity_effect': 'unresolved', 'combination_effect': 'unresolved',
                           'favorable_or_unfavorable': 'unresolved'},
            'effective_action': None, 'effect_status': 'unresolved',
        })
    hidden = []
    for row in support['hidden_positions']:
        targets = [p['name'] for p in pillars if p['name'] != 'day' and p['stem']['value'] == row['stem']]
        hidden.append({'fact': {**row, 'visibility': 'hidden', 'visible_same_stem_pillars': targets},
                       'effective_action': None, 'effect_status': 'unresolved',
                       'equivalent_to_visible': False})
    return {'action_variant': action_variant, 'day_master': day_master,
            'visible_relations': visible, 'hidden_relations': hidden,
            'hidden_visible_equivalence_applied': False, 'weights_available': False,
            'de_shi': None, 'overall_strength': None,
            'scope': '仅记录方向与显藏、有根、柱位距离、合冲条件；方向、邻近或有根均不自动证明效力或得势。'}
