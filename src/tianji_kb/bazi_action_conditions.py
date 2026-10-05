"""Relation direction and its observed conditions, without assumed efficacy."""
from .bazi_core import PILLAR_NAMES, foundations
from .foundations import stem_element
from .resolver import EvidenceResolver

ACTION_VARIANT = 'ditiansui-action-conditions-v1'
EFFECT_VARIANT = 'ditiansui-bounded-action-effects-v1'


def action_effects(pillars, *, observed, relations, principal, availability,
                   action_variant=EFFECT_VARIANT):
    """Reviewed sufficient contexts; this is not a general effect classifier."""
    if action_variant != EFFECT_VARIANT:
        raise ValueError('Unsupported action effect variant')
    if tuple(p['name'] for p in pillars) != PILLAR_NAMES or pillars[2]['stem']['value'] != observed['day_master']:
        raise ValueError('Expected matching ordered pillars and observed day master')
    policy = EvidenceResolver().entities['bazi.concept.action_effects_v1'][1]['attributes']
    supports = tuple(policy['support_relations'])
    visible, hidden = observed['visible_relations'], observed['hidden_relations']
    interaction_kinds = [key for key in policy['unresolved_interactions'] if relations[key]]
    eligible = []
    for row in visible:
        fact = row['fact']
        roots = [r for r in fact['root_positions']
                 if r['branch'] in policy['reviewed_root_branches'].get(fact['element'], [])]
        eligible.append(roots)
    wood = stem_element(observed['day_master']) == policy['day_master_element']
    no_interactions = not interaction_kinds
    pure_conditions = {
        'wood_day_master': wood,
        'reviewed_same_element_month': principal['month_branch'] in policy['pure_months']
            and principal['status'] == 'reviewed_relation' and principal['relation'] == 'same_element',
        'all_positions_support_only': all(r['fact']['relation'] in supports for r in visible + hidden),
        'visible印_present': any(r['fact']['relation'] == 'generates_me' for r in visible),
        'visible比_present': any(r['fact']['relation'] == 'same_element' for r in visible),
        'effective_day_roots': availability['root_presence']
            and all(r['root_availability'] == 'effective' for r in availability['roots']),
        'all_visible_have_reviewed_roots': all(eligible),
        'no_unresolved_interactions': no_interactions,
    }
    isolated_conditions = {
        'wood_day_master': wood,
        'reviewed_control_month': principal['month_branch'] in policy['isolated_months']
            and principal['status'] == 'reviewed_relation' and principal['relation'] == 'controls_me',
        'day_has_no_structural_root': not availability['root_presence'],
        'no_support_in_any_position': all(r['fact']['relation'] not in supports for r in visible + hidden),
        'visible_earth_metal_only': all(r['fact']['element'] in ('土', '金') for r in visible),
        'month_principal_exposed_with_root': any(r['fact']['pillar'] == 'month'
            and r['fact']['stem'] == principal['principal_qi'] and eligible[i]
            for i, r in enumerate(visible)),
        'no_unresolved_interactions': no_interactions,
    }
    pure, isolated = all(pure_conditions.values()), all(isolated_conditions.values())
    visible_effects = []
    for i, row in enumerate(visible):
        proved = pure or (isolated and row['fact']['pillar'] == 'month')
        visible_effects.append({'action_index': i, 'fact': dict(row['fact']),
            'eligible_root_positions': eligible[i], 'conditions': row['conditions'],
            'effective_action': row['fact']['relation'] if proved else None,
            'effect_status': 'effective_in_reviewed_context' if proved else 'unresolved',
            'context': 'pure_support' if pure else ('isolated_control' if proved else None),
            'polarity_equivalence_assumed': False, 'distance_weight': None})
    hidden_effects = []
    for i, row in enumerate(hidden):
        root_indexes = [j for j, r in enumerate(availability['roots'])
            if r['root_presence']['pillar'] == row['fact']['pillar']
            and r['root_presence']['hidden_stem'] == row['fact']['stem']
            and r['root_availability'] == 'effective']
        hidden_effects.append({'action_index': i, 'fact': dict(row['fact']),
            'effective_action': 'root_support' if pure and root_indexes else None,
            'effect_status': 'root_participation_only' if pure and root_indexes else 'unresolved',
            'root_indexes': root_indexes, 'equivalent_to_visible': False})
    return {'action_variant': action_variant, 'day_master': observed['day_master'],
            'pure_support_scope_conditions': pure_conditions, 'pure_support_scope_met': pure,
            'isolated_control_scope_conditions': isolated_conditions, 'isolated_control_scope_met': isolated,
            'visible_relations': visible_effects, 'hidden_relations': hidden_effects,
            'unresolved_interaction_kinds': interaction_kinds,
            'transformation_status': 'unresolved' if any(relations[k] for k in (
                'stem_five_combinations', 'branch_six_harmonies', 'branch_triple_harmonies')) else 'not_present',
            'stem_erasure_applied': False, 'hidden_visible_equivalence_applied': False,
            'weights_available': False, 'overall_strength': None,
            'scope': '仅已审木日主纯印比月卯生扶、或无根无扶月酉透辛的条件作用；其他效力未裁定，不推从格、喜用或吉凶。'}


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
