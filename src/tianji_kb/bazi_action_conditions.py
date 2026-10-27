"""Relation direction and its observed conditions, without assumed efficacy."""
from .bazi_core import PILLAR_NAMES, foundations
from .bazi_fire_morphology import BING_ALL_ROOT_BRANCHES, BING_HEAVY_ROOT_BRANCHES
from .foundations import stem_element
from .resolver import EvidenceResolver

ACTION_VARIANT = 'ditiansui-action-conditions-v1'
EFFECT_VARIANT = 'ditiansui-bounded-action-effects-v1'

# TJ-011.2: generating-month extension of the bounded pure-support scope.
# Reviewed within the SAME Source as the existing scope
# (bazi.source.ditiansui-spouse, C-grade single electronic lineage,
# daizhigev20 snapshot SHA256
# 6a875a317c7ba1012285ed12d3bfa5577b50c9fdfd568ece323a12feafe38795):
# Ren's Congwang definition (char 96521 / line 4905: "从旺者，四柱皆
# 比劫，无官杀之制，有印绶之生，旺之极者") requires peer stems with
# resource generation and no controlling force; unlike the Congqiang
# definition (char 96605) it does NOT require the month to be the day
# master's own element or season. The root table (chars 39967-40222 /
# line 1613) lists 亥 first among the heavy roots for Jia/Yi wood
# ("如甲乙逢亥寅卯之类是也"), and 亥's reviewed principal qi is 壬
# (section s034), whose relation to a wood day master is generates_me
# (Golden bazi.principal-generate). 亥's hidden stems are exactly 壬
# (generating) and 甲 (same element), so a support-only composition is
# satisfiable in this month, as it is in single-qi 卯. The sealed
# policy concept cannot be extended from public code, so this reviewed
# month set is declared here and cross-checked in the adjudication
# layer, mirroring how the 卯/酉 scope is already hardcoded beside the
# sealed pure_months / isolated_months policy values.
PURE_GENERATING_MONTHS = ('亥',)


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
    # TJ-011.2: the generating-month (亥) scope mirrors the pure scope
    # condition by condition; only the month condition differs (reviewed
    # principal relation generates_me in a PURE_GENERATING_MONTHS month
    # instead of same_element in a policy pure_months month). Every other
    # key reuses the pure scope's computed fact, so the two scopes can
    # never diverge on a shared condition.
    generating_conditions = {
        'wood_day_master': pure_conditions['wood_day_master'],
        'reviewed_generating_month': principal['month_branch'] in PURE_GENERATING_MONTHS
            and principal['status'] == 'reviewed_relation' and principal['relation'] == 'generates_me',
        'all_positions_support_only': pure_conditions['all_positions_support_only'],
        'visible印_present': pure_conditions['visible印_present'],
        'visible比_present': pure_conditions['visible比_present'],
        'effective_day_roots': pure_conditions['effective_day_roots'],
        'all_visible_have_reviewed_roots': pure_conditions['all_visible_have_reviewed_roots'],
        'no_unresolved_interactions': pure_conditions['no_unresolved_interactions'],
    }
    # TJ-011.2: commanding visible-support scope (Bing day master, Wu
    # month, same-element command), per the adjudicated fire morphology
    # register (bazi_fire_morphology.FORM_BING_WU, nine conditions). This
    # is a NEW form, not a widening of the pure scope: its quantitative
    # layer is the VISIBLE stems only. Hidden stems enter solely as root
    # facts (existence and availability) under the registered governance
    # convention fire-morph.hidden-layer-root-facts-only -- a Variant
    # governance convention, NOT original text -- so a non-support hidden
    # stem (e.g. Ji in Wu) is recorded but never vetoes, and a support
    # hidden stem never counts as support. Fire's reviewed root branches
    # come from the public morphology register (BING_ALL_ROOT_BRANCHES);
    # every other element keeps the sealed policy set. Root
    # effectiveness for this form is read off the executed root facts
    # themselves (no root-type source conflict, no unresolved branch
    # interaction touching the root), exactly as the register's
    # effective_heavy_day_roots condition defines it; the sealed
    # availability variant remains wood-scoped and is not edited.
    commanding_reviewed_roots = dict(policy['reviewed_root_branches'])
    commanding_reviewed_roots['火'] = list(BING_ALL_ROOT_BRANCHES)
    eligible_commanding = []
    for row in visible:
        fact = row['fact']
        roots = [r for r in fact['root_positions']
                 if r['branch'] in commanding_reviewed_roots.get(fact['element'], [])]
        eligible_commanding.append(roots)
    day_roots = availability['roots']
    commanding_conditions = {
        'fire_day_master_bing': observed['day_master'] == '丙',
        'reviewed_same_element_command_month': principal['month_branch'] == '午'
            and principal['status'] == 'reviewed_relation' and principal['relation'] == 'same_element',
        'visible_positions_support_only': all(r['fact']['relation'] in supports for r in visible),
        'visible_resource_present': any(r['fact']['relation'] == 'generates_me' for r in visible),
        'visible_peer_present': any(r['fact']['relation'] == 'same_element' for r in visible),
        'effective_heavy_day_roots': bool(day_roots)
            and any(r['root_presence']['branch'] in BING_HEAVY_ROOT_BRANCHES for r in day_roots)
            and all(not r['type_source_conflict'] and not r['branch_relations'] for r in day_roots),
        'all_visible_have_reviewed_roots': all(eligible_commanding),
        'no_unresolved_interactions': no_interactions,
        # Governance convention condition: true by the construction of
        # this scope (the hidden layer IS handled root-facts-only here);
        # the register lists it as a condition of the form and it is
        # annotated as governance_convention, never original_text, in
        # the adjudication conditions output.
        'hidden_layer_convention_applied': True,
    }
    pure, generating, commanding, isolated = (all(pure_conditions.values()),
        all(generating_conditions.values()), all(commanding_conditions.values()),
        all(isolated_conditions.values()))
    visible_effects = []
    for i, row in enumerate(visible):
        proved = pure or generating or commanding or (isolated and row['fact']['pillar'] == 'month')
        visible_effects.append({'action_index': i, 'fact': dict(row['fact']),
            'eligible_root_positions': eligible[i], 'conditions': row['conditions'],
            'effective_action': row['fact']['relation'] if proved else None,
            'effect_status': 'effective_in_reviewed_context' if proved else 'unresolved',
            'context': 'pure_support' if pure else (
                'pure_generating_support' if generating else (
                    'commanding_visible_support' if commanding else (
                        'isolated_control' if proved else None))),
            'polarity_equivalence_assumed': False, 'distance_weight': None})
    hidden_effects = []
    for i, row in enumerate(hidden):
        root_indexes = [j for j, r in enumerate(availability['roots'])
            if r['root_presence']['pillar'] == row['fact']['pillar']
            and r['root_presence']['hidden_stem'] == row['fact']['stem']
            and r['root_availability'] == 'effective']
        hidden_effects.append({'action_index': i, 'fact': dict(row['fact']),
            'effective_action': 'root_support' if (pure or generating) and root_indexes else None,
            'effect_status': 'root_participation_only' if (pure or generating) and root_indexes else 'unresolved',
            'root_indexes': root_indexes, 'equivalent_to_visible': False})
    return {'action_variant': action_variant, 'day_master': observed['day_master'],
            'pure_support_scope_conditions': pure_conditions, 'pure_support_scope_met': pure,
            'pure_generating_support_scope_conditions': generating_conditions,
            'pure_generating_support_scope_met': generating,
            'commanding_visible_support_scope_conditions': commanding_conditions,
            'commanding_visible_support_scope_met': commanding,
            'isolated_control_scope_conditions': isolated_conditions, 'isolated_control_scope_met': isolated,
            'visible_relations': visible_effects, 'hidden_relations': hidden_effects,
            'unresolved_interaction_kinds': interaction_kinds,
            'transformation_status': 'unresolved' if any(relations[k] for k in (
                'stem_five_combinations', 'branch_six_harmonies', 'branch_triple_harmonies')) else 'not_present',
            'stem_erasure_applied': False, 'hidden_visible_equivalence_applied': False,
            'weights_available': False, 'overall_strength': None,
            'scope': '仅已审木日主纯印比月卯生扶、亥月印比生扶（从旺口径）、或无根无扶月酉透辛的条件作用；丙日主午月同类当令显纯生扶（从强主锚，藏干仅作根位事实——治理约定非原文）；其他效力未裁定，不推从格、喜用或吉凶。'}


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
