"""Research observations from executed month/ten-god/visibility facts, never 定格."""

from . import bazi_siling_matrix as _siling_matrix
from .foundations import BRANCHES, CONTROLS, GENERATES, STEMS, stem_element
from .resolver import EvidenceResolver

PATTERN_VARIANT = 'bazi-pattern-structure-candidates-v1'


def yuanhai_unexposed_official(trace):
    """Read the already-reviewed Yuanhai 甲辛/巳酉丑 example as structure only.

    This is a *single source example*, not a general algorithm for 官格 or
    an alternative to 任氏 dated commander requirements.
    """
    steps = {row['rule_id']: (i, row) for i, row in enumerate(trace.steps)}
    required = ('pillars', 'ten_gods', 'branch_triple_harmonies')
    if any('bazi.phase2.' + name not in steps for name in required):
        raise ValueError('Yuanhai branch observation requires executed pillar, stem and harmony facts')
    for name in required:
        step = steps['bazi.phase2.' + name][1]
        if not step['evidence_ids'] or any(e not in trace.evidence for e in step['evidence_ids']):
            raise ValueError('Yuanhai branch observation lacks executed evidence')

    def fact_ref(name, suffix=''):
        return f"#/trace/{steps['bazi.phase2.' + name][0]}/output" + suffix

    pillars = steps['bazi.phase2.pillars'][1]['output']
    stems = steps['bazi.phase2.ten_gods'][1]['output']
    groups = steps['bazi.phase2.branch_triple_harmonies'][1]['output']
    day_wood = pillars['day_master']['stem'] == '甲'
    month_you = pillars['ganzhi'][1][1] == '酉'
    unexposed_xin = all(row['stem'] != '辛' for row in stems)
    match = next(((i, group) for i, group in enumerate(groups)
                  if set(group['branches']) == {'巳', '酉', '丑'}
                  and group['traditional_result_element'] == '金'), None)
    complete = match is not None
    conditions = [
        {'id': 'jia_day', 'observed': day_wood, 'fact_ref': fact_ref('pillars', '/day_master/stem')},
        {'id': 'you_month', 'observed': month_you, 'fact_ref': fact_ref('pillars', '/ganzhi/1')},
        {'id': 'no_visible_xin', 'observed': unexposed_xin, 'fact_ref': fact_ref('ten_gods'),
         'visible_xin_positions': [row['pillar'] for row in stems if row['stem'] == '辛']},
        {'id': 'complete_si_you_chou', 'observed': complete,
         'fact_ref': fact_ref('branch_triple_harmonies', f'/{match[0]}') if complete
         else fact_ref('branch_triple_harmonies')},
    ]
    # TJ-012.2: Explicit counterexample marking.
    # A counterexample is a condition that is actively contradicted,
    # not merely unobserved. This prevents misreading 'not_observed'
    # as 'possibly applicable'.
    counterexamples = []
    # Xin visible contradicts the 'unexposed' requirement (s056 core)
    if not unexposed_xin:
        counterexamples.append({
            'id': 'xin_exposed_contradicts_unexposed_branch',
            'fact_ref': fact_ref('ten_gods'),
            'visible_xin_positions': [row['pillar'] for row in stems if row['stem'] == '辛'],
            'note': '辛已透干，与“不透”例直接矛盾；不得套用此分支',
        })
    # Non-Jia day contradicts the 甲日 requirement
    if not day_wood:
        counterexamples.append({
            'id': 'non_jia_day_contradicts_jia_branch',
            'fact_ref': fact_ref('pillars', '/day_master/stem'),
            'actual_day_stem': pillars['day_master']['stem'],
            'note': '非甲日，不得套用甲辛官局例',
        })
    # Non-You month contradicts the 酉月 requirement
    if not month_you:
        counterexamples.append({
            'id': 'non_you_month_contradicts_you_branch',
            'fact_ref': fact_ref('pillars', '/ganzhi/1'),
            'actual_month_branch': pillars['ganzhi'][1][1],
            'note': '非酉月，不得套用此分支',
        })
    return {
        'variant': PATTERN_VARIANT, 'school_branch': 'yuanhai-甲辛-酉月不透地支官局例',
        'status': 'reviewed_structural_candidate' if all(c['observed'] for c in conditions)
                  else 'not_observed',
        'conditions': conditions, 'full_metal_group': list(match[1]['branches']) if complete else [],
        'counterexamples': counterexamples,
        'counterexample_ids': [c['id'] for c in counterexamples],
        'source_section_id': 'bazi.section.s056', 'source_level': 'C',
        'source_scope': '《渊海子平》甲日辛官、酉月不透辛而有巳酉丑的单例观察',
        'unresolved': ['general_strength', 'hour_branch_wood_strength',
                       'source_scope_generalization', 'dated_month_boundary',
                       'official_killing_selection', 'actual_harmony_transformation'],
        'determination': None, 'qualified_for_determination': False,
        'research_only': True, 'public_enabled': False, 'ai_enabled': False,
        'scope': '仅完整巳酉丑三合成员结构，不据此认定合化、身旺、正官格、真假成败、吉凶或喜用；其他日主/月令不外推。',
    }


# Five finite birth-month groups explicitly recorded in reviewed Yuanhai s059.
# These are textual examples of 月令生我, NOT a dated-commander or 印格 table.
YUANHAI_RESOURCE_MONTHS = {
    '甲': ('亥', '子'), '乙': ('亥', '子'),
    '丙': ('寅', '卯'), '丁': ('寅', '卯'),
    '戊': ('巳', '午'), '己': ('巳', '午'),
    '庚': ('辰', '戌', '丑', '未'), '辛': ('辰', '戌', '丑', '未'),
    '壬': ('申', '酉'), '癸': ('申', '酉'),
}


def yuanhai_resource_month_example(trace):
    """Observe one bounded Yuanhai 月令生我 textual example; never determine 印格."""
    steps = {row['rule_id']: (i, row) for i, row in enumerate(trace.steps)}
    required = ('pillars', 'hidden_stems')
    if any('bazi.phase2.' + name not in steps for name in required):
        raise ValueError('Yuanhai resource month requires executed pillars and month hidden stems')
    for name in required:
        step = steps['bazi.phase2.' + name][1]
        if not step['evidence_ids'] or any(e not in trace.evidence for e in step['evidence_ids']):
            raise ValueError('Yuanhai resource month lacks executed evidence')

    def fact_ref(name, suffix=''):
        return f"#/trace/{steps['bazi.phase2.' + name][0]}/output" + suffix

    pillars = steps['bazi.phase2.pillars'][1]['output']
    hidden = steps['bazi.phase2.hidden_stems'][1]['output']
    day_stem = pillars['day_master']['stem']
    month_branch = pillars['ganzhi'][1][1]
    expected = YUANHAI_RESOURCE_MONTHS[day_stem]
    month_index, month_row = next((i, row) for i, row in enumerate(hidden)
                                   if row['pillar'] == 'month')
    if month_row['branch'] != month_branch:
        raise ValueError('Yuanhai resource month evidence is inconsistent')
    resource_positions = [
        {'ten_god': item['ten_god'], 'stem': item['stem'],
         'fact_ref': fact_ref('hidden_stems', f'/{month_index}/hidden_stems/{i}')}
        for i, item in enumerate(month_row['hidden_stems'])
        if item['ten_god'] in ('正印', '偏印')
    ]
    month_matches = month_branch in expected
    observed = month_matches and bool(resource_positions)
    return {
        'variant': PATTERN_VARIANT,
        'school_branch': 'yuanhai-印绶月份生我列举',
        'status': 'reviewed_month_example' if observed else 'not_observed',
        'day_stem': day_stem, 'month_branch': month_branch,
        'reviewed_example_months': list(expected),
        'month_resource_positions': resource_positions,
        'conditions': [
            {'id': 'reviewed_day_stem_month_group', 'observed': month_matches,
             'fact_ref': fact_ref('pillars', '/ganzhi/1')},
            {'id': 'reviewed_month_hidden_resource', 'observed': bool(resource_positions),
             'fact_ref': fact_ref('hidden_stems', f'/{month_index}')},
        ],
        'source_section_id': 'bazi.section.s059',
        'source_level': 'C',
        'unresolved': ['dated_commander', 'root_and_strength',
                       'wealth_damages_resource_conditions', 'many_officials_and_other_patterns',
                       'special_tomb_month_exceptions', 'pattern_selection_school'],
        'determination': None, 'qualified_for_determination': False,
        'research_only': True, 'public_enabled': False, 'ai_enabled': False,
        'scope': '仅复算渊海正偏印所属日干与月支的生我例；不推定印格、司令、旺衰、财旺破印、真假成败、吉凶或喜用。',
    }


def yuanhai_hour_killing_restriction(trace):
    """Review only the Yuanhai s055 hour-pillar exception to month 正官.

    The traditional text cautions against directly calling this 正官; it does
    NOT prove 官杀混杂、破格、伤害, or decide any pattern.
    """
    steps = {row['rule_id']: (i, row) for i, row in enumerate(trace.steps)}
    needed = ('ten_gods', 'hidden_stems')
    if any('bazi.phase2.' + name not in steps for name in needed):
        raise ValueError('Hour killing restriction requires executed ten gods and hidden stems')
    for name in needed:
        step = steps['bazi.phase2.' + name][1]
        if not step['evidence_ids'] or any(k not in trace.evidence for k in step['evidence_ids']):
            raise ValueError('Hour killing restriction lacks executed evidence')

    def fact_ref(name, suffix=''):
        return f"#/trace/{steps['bazi.phase2.' + name][0]}/output" + suffix

    visible = steps['bazi.phase2.ten_gods'][1]['output']
    hidden = steps['bazi.phase2.hidden_stems'][1]['output']
    mi, month = next((i, r) for i, r in enumerate(hidden) if r['pillar'] == 'month')
    hi, hour = next((i, r) for i, r in enumerate(hidden) if r['pillar'] == 'hour')
    month_official = [
        {'stem': row['stem'], 'fact_ref': fact_ref('hidden_stems', f'/{mi}/hidden_stems/{i}')}
        for i, row in enumerate(month['hidden_stems']) if row['ten_god'] == '正官'
    ]
    hour_stem = [
        {'stem': row['stem'], 'fact_ref': fact_ref('ten_gods', f'/{i}')}
        for i, row in enumerate(visible) if row['pillar'] == 'hour' and row['ten_god'] == '七杀'
    ]
    hour_branch = [
        {'stem': row['stem'], 'fact_ref': fact_ref('hidden_stems', f'/{hi}/hidden_stems/{i}')}
        for i, row in enumerate(hour['hidden_stems']) if row['ten_god'] == '七杀'
    ]
    applies = bool(month_official and (hour_stem or hour_branch))
    return {
        'variant': PATTERN_VARIANT, 'school_branch': 'yuanhai-月令正官时干支偏官限制',
        'status': 'restriction_observed' if applies else 'not_observed',
        'month_official_positions': month_official,
        'hour_visible_killing_positions': hour_stem,
        'hour_hidden_killing_positions': hour_branch,
        'conditions': [
            {'id': 'month_hidden_official', 'observed': bool(month_official),
             'fact_ref': fact_ref('hidden_stems', f'/{mi}')},
            {'id': 'hour_visible_seven_killing', 'observed': bool(hour_stem),
             'fact_ref': fact_ref('ten_gods')},
            {'id': 'hour_hidden_seven_killing', 'observed': bool(hour_branch),
             'fact_ref': fact_ref('hidden_stems', f'/{hi}')},
        ],
        # TJ-012.2: Explicit counterexample marking.
        # If month has NO hidden official, the s055 restriction branch
        # does not apply at all (counterexample to trigger condition).
        'counterexamples': [] if month_official else [{
            'id': 'no_month_hidden_official_contradicts_restriction_branch',
            'fact_ref': fact_ref('hidden_stems', f'/{mi}'),
            'note': '月支无藏正官，s055限制分支不适用；不得据此否定其他取格',
        }],
        'source_section_id': 'bazi.section.s055', 'source_level': 'C',
        'selection_status': 'additional_source_review_required' if applies else 'not_observed',
        'unresolved': ['official_killing_selection', 'removal_or_retention',
                       'dated_commander', 'actual_strength_and_effects',
                       'pattern_branch_comparison'],
        'determination': None, 'qualified_for_determination': False,
        'research_only': True, 'public_enabled': False, 'ai_enabled': False,
        'scope': '仅限月藏正官且时干显七杀或时支藏七杀；时支藏干不是透干。不得直接定官杀混杂、破格、正官格、婚恋/事业吉凶或喜用。',
    }


def resource_elemental_causal_gate(context):
    """Audit five-element DIRECTION between observed 财/官 and 月藏印.

    An elemental control/generation relationship is a necessary structural
    candidate, never evidence that either actor is strong/available or acts.
    Hidden actors are not silently promoted to exposed heavenly stems.
    """
    positions = context['positions']
    targets = positions['month_resource']
    sources = (('visible_wealth', 'wealth_controls_resource_element'),
               ('hidden_wealth', 'wealth_controls_resource_element'),
               ('visible_official', 'official_generates_resource_element'),
               ('hidden_official', 'official_generates_resource_element'),
               ('visible_killing', 'killing_generates_resource_element_only'),
               ('hidden_killing', 'killing_generates_resource_element_only'))
    candidates = []
    # Structural co-occurrence is a reproducible fact, not a root-strength
    # rating or proof of effective action. Sites retain original trace refs.
    stem_sites = context['exact_stem_sites']
    element_root_sites = context['element_root_sites']
    branch_root_interactions = context['branch_root_interactions']
    def candidates_for(stem):
        element = stem_element(stem)
        return [
            {**site, 'same_stem': site['stem'] == stem,
             'match_type': 'same_stem' if site['stem'] == stem else 'same_element_only',
             'root_effect_status': 'indeterminate',
             'branch_interactions': [dict(interaction) for interaction in
                                     branch_root_interactions
                                     if site['pillar'] in interaction['pillars']]}
            for site in element_root_sites[element]
        ]
    summary = {'wealth_element_controls_resource': False,
               'visible_wealth_direction': False,
               'hidden_wealth_direction': False,
               'official_element_generates_resource': False,
               'visible_official_direction': False,
               'hidden_official_direction': False,
               'killing_element_generates_resource_only': False}
    for category, kind in sources:
        for source in positions[category]:
            for target in targets:
                actor_element = stem_element(source['stem'])
                target_element = stem_element(target['stem'])
                holds = ((CONTROLS[actor_element] == target_element)
                         if 'wealth' in category else
                         (GENERATES[actor_element] == target_element))
                # Ten-god direction must agree with the independently executed
                # seed element table; a mismatch is a data defect, not a verdict.
                if not holds:
                    raise ValueError('Ten-god elemental relation contradicts reviewed seed')
                # Same-element hidden sites are root *candidates* only.
                # A same-stem site is not a strength/effect decision.
                actor_roots = candidates_for(source['stem'])
                target_roots = candidates_for(target['stem'])
                fact_refs = [source['fact_ref'], target['fact_ref']]
                blocker_ids = (
                    'actor_effective_strength_unresolved',
                    'resource_effective_strength_unresolved',
                    'dated_commander_unresolved',
                    'pairwise_effect_rule_not_reviewed',
                    'school_scope_unresolved',
                )
                blockers = [{'id': reason, 'fact_refs': list(fact_refs)}
                            for reason in blocker_ids]
                if category.startswith('hidden'):
                    blockers.append({
                        'id': 'hidden_stem_activation_not_proven',
                        'fact_refs': [source['fact_ref']],
                    })
                if context.get('observed_interactions'):
                    blockers.append({
                        'id': 'observed_interaction_effect_unresolved',
                        'fact_refs': [r['fact_ref'] for r in context['observed_interactions']],
                        'rule_ids': [r['rule_id'] for r in context['observed_interactions']],
                        'evidence_ids': sorted({e for r in context['observed_interactions']
                                                for e in r['evidence_ids']}),
                    })
                candidate = {
                    'kind': kind,
                    'actor_category': category,
                    'actor_visibility': 'visible' if category.startswith('visible') else 'hidden',
                    'actor': dict(source), 'target': dict(target),
                    'actor_element': actor_element, 'target_element': target_element,
                    'actor_exact_stem_sites': {
                        'visible': list(stem_sites[source['stem']]['visible']),
                        'hidden': list(stem_sites[source['stem']]['hidden']),
                    },
                    'resource_exact_stem_sites': {
                        'visible': list(stem_sites[target['stem']]['visible']),
                        'hidden': list(stem_sites[target['stem']]['hidden']),
                    },
                    'same_stem_presence_is_not_effective_root': True,
                    'actor_element_root_candidates': actor_roots,
                    'resource_element_root_candidates': target_roots,
                    'root_candidate_comparison': {
                        'actor_has_same_stem_site': any(x['same_stem'] for x in actor_roots),
                        'actor_has_other_stem_same_element_site': any(
                            not x['same_stem'] for x in actor_roots),
                        'resource_has_same_stem_site': any(x['same_stem'] for x in target_roots),
                        'resource_has_other_stem_same_element_site': any(
                            not x['same_stem'] for x in target_roots),
                        'root_effect_status': 'indeterminate',
                        'root_loss_inferred_from_clash': False,
                        'pairwise_effect_proved_by_root_sites': False,
                    },
                    'reviewed_root_type_comparison': {
                        'actor_reviewed_examples': any(
                            site['reviewed_root_type_examples'] or site['alternative_root_type_examples']
                            for site in actor_roots),
                        'resource_reviewed_examples': any(
                            site['reviewed_root_type_examples'] or site['alternative_root_type_examples']
                            for site in target_roots),
                        'residual_type_conflict_present': any(
                            site['residual_type_conflict']['conflict_id']
                            for site in actor_roots + target_roots),
                        'unreviewed_principal_qi_sites': any(
                            site['principal_qi_review']['status'] == 'unreviewed'
                            for site in actor_roots + target_roots),
                        'actor_effective_root_strength': None,
                        'resource_effective_root_strength': None,
                        'actual_pairwise_effect': None,
                    },
                    'actual_root_strength_status': 'indeterminate',
                    'elemental_direction_observed': True,
                    'effective_interaction': None,
                    'effective_interaction_status': 'indeterminate',
                    'actor_strength': None, 'target_strength': None,
                    'stem_or_hidden_equivalence_assumed': False,
                    'structural_presence': True,
                    'elemental_relation_direction': kind,
                    'effect_status': 'indeterminate',
                    'effect_blockers': blockers,
                    'fact_refs': fact_refs,
                    'evidence_ids': context.get('evidence_ids', []),
                    'source_refs': ['bazi.section.s057', 'bazi.section.s058'],
                    'variant': PATTERN_VARIANT,
                    'adjudication': 'indeterminate',
                }
                candidates.append(candidate)
                if category in ('visible_wealth', 'hidden_wealth'):
                    summary['wealth_element_controls_resource'] = True
                    summary[category + '_direction'] = True
                elif category in ('visible_official', 'hidden_official'):
                    summary['official_element_generates_resource'] = True
                    summary[category + '_direction'] = True
                else:
                    summary['killing_element_generates_resource_only'] = True
    status = ('outside_month_resource_branch' if not targets
              else 'direction_observed_effect_unresolved' if candidates
              else 'no_relevant_elemental_pair')
    return {
        'status': status,
        'relation_candidates': candidates,
        'relation_summary': summary,
        'reviewed_root_type_summary': {
            'actor_reviewed_examples_observed': any(
                p['reviewed_root_type_comparison']['actor_reviewed_examples']
                for p in candidates),
            'resource_reviewed_examples_observed': any(
                p['reviewed_root_type_comparison']['resource_reviewed_examples']
                for p in candidates),
            'residual_source_conflict_observed': any(
                p['reviewed_root_type_comparison']['residual_type_conflict_present']
                for p in candidates),
            'unreviewed_principal_qi_observed': any(
                p['reviewed_root_type_comparison']['unreviewed_principal_qi_sites']
                for p in candidates),
            'effective_strength_established': False,
            'effective_pairwise_action_established': False,
        },
        'element_root_candidate_summary': {
            'actor_candidate_observed': any(p['actor_element_root_candidates'] for p in candidates),
            'resource_candidate_observed': any(p['resource_element_root_candidates'] for p in candidates),
            'other_stem_same_element_observed': any(
                p['root_candidate_comparison']['actor_has_other_stem_same_element_site']
                or p['root_candidate_comparison']['resource_has_other_stem_same_element_site']
                for p in candidates),
            'root_branch_interaction_observed': any(
                site['branch_interactions']
                for p in candidates
                for site in p['actor_element_root_candidates']
            ) or any(
                site['branch_interactions']
                for p in candidates
                for site in p['resource_element_root_candidates']
            ),
            'actual_root_strength_inferred': False,
            'actual_effect_inferred': False,
        },
        'exact_stem_site_summary': {
            'visible_actor_with_same_stem_hidden_site': any(
                p['actor_visibility'] == 'visible' and p['actor_exact_stem_sites']['hidden']
                for p in candidates),
            'month_resource_with_same_stem_visible_site': any(
                p['resource_exact_stem_sites']['visible'] for p in candidates),
            'effective_root_inferred': False,
            'numeric_root_weight_applied': False,
        },
        'effect_gate': {
            'status': 'not_applicable_without_month_resource' if not targets
                      else 'indeterminate',
            'required_unresolved_factors': [
                'actor_effective_strength',
                'resource_effective_strength',
                'visible_hidden_participation',
                'pairwise_interaction_conditions',
                'source_school_scope',
                'other_pattern_competition',
            ] if targets and candidates else [],
            'wealth_damages_resource': None,
            'official_actually_generates_resource': None,
            'killing_equivalent_to_official_in_source': None,
            'general_day_master_action_effects_reused': False,
            'numeric_weights_applied': False,
            'source_case_lookup_used': False,
        },
        'source_section_ids': ['bazi.section.s057', 'bazi.section.s058'],
        'source_level': 'C',
        'research_only': True, 'public_enabled': False, 'ai_enabled': False,
        'scope': '只检查已执行十神/藏干与五行生克方向。显财/藏财、显官/藏官及七杀分别保留；方向不证明有效克印、生印、财旺、官鬼多、破格或喜用。',
    }


def yuanhai_resource_competing_context(trace):
    """Bounded co-presence facts for Yuanhai s057/s058, never 财旺破印 or 官印相生.

    A visible 十神 and an unexposed hidden 十神 are different observations.
    Neither occurrence nor frequency establishes strength, activation, or effect.
    """
    steps = {row['rule_id']: (i, row) for i, row in enumerate(trace.steps)}
    if len(steps) != len(trace.steps):
        raise ValueError('Resource competition has duplicate executed rule identifiers')
    required = ('ten_gods', 'hidden_stems')
    if any('bazi.phase2.' + rule not in steps for rule in required):
        raise ValueError('Resource competition requires executed ten-god and hidden-stem facts')
    for rule in required:
        step = steps['bazi.phase2.' + rule][1]
        if not step['evidence_ids'] or any(ref not in trace.evidence for ref in step['evidence_ids']):
            raise ValueError('Resource competition lacks executed evidence')

    def pointer(rule, suffix=''):
        return f"#/trace/{steps['bazi.phase2.' + rule][0]}/output" + suffix

    visible = steps['bazi.phase2.ten_gods'][1]['output']
    hidden = steps['bazi.phase2.hidden_stems'][1]['output']
    # Inventory exact-stem visibility and hidden sites from the two already
    # executed facts; exclude the day-master as an exposed competing actor.
    # This has a different meaning from effective rooting or dated commander.
    exact_stem_sites = {}
    def site_bucket(stem):
        return exact_stem_sites.setdefault(stem, {'visible': [], 'hidden': []})
    for vi, row in enumerate(visible):
        if row['pillar'] != 'day':
            site_bucket(row['stem'])['visible'].append({
                'pillar': row['pillar'],
                'fact_ref': pointer('ten_gods', f'/{vi}'),
            })
    for pi, row in enumerate(hidden):
        for hi, hidden_row in enumerate(row['hidden_stems']):
            site_bucket(hidden_row['stem'])['hidden'].append({
                'pillar': row['pillar'],
                'branch': row['branch'],
                'fact_ref': pointer('hidden_stems', f'/{pi}/hidden_stems/{hi}'),
            })
    root_policy = EvidenceResolver().entities[
        'bazi.concept.root_conditions_variant_v1'][1]['attributes']
    element_root_sites = {element: [] for element in ('木', '火', '土', '金', '水')}
    for pi, pillar in enumerate(hidden):
        for hi, stem_row in enumerate(pillar['hidden_stems']):
            stem = stem_row['stem']
            element = stem_element(stem)
            branch = pillar['branch']
            principal = root_policy['principal_qi'].get(branch)
            examples = [
                {'kind': candidate['kind'],
                 'source_section_ids': list(candidate['section_ids']),
                 'status': 'reviewed_type_example_only'}
                for candidate in root_policy['reviewed_type_candidates']
                if candidate['element'] == element and branch in candidate['branches']
            ]
            alternatives = [
                {'kind': candidate['kind'],
                 'source_section_ids': list(candidate['section_ids']),
                 'variant': candidate['variant'],
                 'status': 'alternative_source_example_only'}
                for candidate in root_policy['alternative_residual_type_candidates']
                if candidate['element'] == element and branch in candidate['branches']
            ]
            residual_example = any(
                candidate['kind'] == 'residual_qi_candidate'
                for candidate in examples + alternatives)
            element_root_sites[element].append({
                'pillar': pillar['pillar'], 'branch': branch,
                'stem': stem, 'element': element,
                'fact_ref': pointer('hidden_stems', f'/{pi}/hidden_stems/{hi}'),
                'structural_candidate_only': True,
                'reviewed_root_type_examples': examples,
                'alternative_root_type_examples': alternatives,
                'root_type_review_status': 'example_only' if examples or alternatives
                                           else 'not_covered_by_reviewed_examples',
                'principal_qi_review': {
                    'status': 'reviewed' if principal else 'unreviewed',
                    'stem': principal['stem'] if principal else None,
                    'same_stem': stem == principal['stem'] if principal else None,
                    'source_section_ids': list(principal['section_ids']) if principal else [],
                },
                'residual_type_conflict': {
                    'status': 'unresolved_source_variant' if residual_example
                              else 'not_applicable_to_reviewed_example',
                    'conflict_id': root_policy['type_conflict'] if residual_example else None,
                    'competing_section_id': 'bazi.section.s041' if residual_example else None,
                    'source_variant_examples_separated': True,
                },
                'effective_root_strength': None,
                'root_type_is_not_root_effect': True,
            })
    groups = {'month_resource': [], 'visible_wealth': [], 'hidden_wealth': [],
              'visible_official': [], 'hidden_official': [],
              'visible_killing': [], 'hidden_killing': []}
    # Do not treat the day-master as a separate competing visible stem.
    for i, row in enumerate(visible):
        if row['pillar'] == 'day':
            continue
        category = {'正财': 'visible_wealth', '偏财': 'visible_wealth',
                    '正官': 'visible_official', '七杀': 'visible_killing'}.get(row['ten_god'])
        if category:
            groups[category].append({'pillar': row['pillar'], 'stem': row['stem'],
                                     'ten_god': row['ten_god'], 'fact_ref': pointer('ten_gods', f'/{i}')})
    for pi, pillar in enumerate(hidden):
        for hi, row in enumerate(pillar['hidden_stems']):
            category = {'正财': 'hidden_wealth', '偏财': 'hidden_wealth',
                        '正官': 'hidden_official', '七杀': 'hidden_killing'}.get(row['ten_god'])
            if pillar['pillar'] == 'month' and row['ten_god'] in ('正印', '偏印'):
                groups['month_resource'].append({
                    'pillar': 'month', 'stem': row['stem'], 'ten_god': row['ten_god'],
                    'fact_ref': pointer('hidden_stems', f'/{pi}/hidden_stems/{hi}')})
            if category:
                groups[category].append({
                    'pillar': pillar['pillar'], 'stem': row['stem'], 'ten_god': row['ten_god'],
                    'fact_ref': pointer('hidden_stems', f'/{pi}/hidden_stems/{hi}')})
    related = ('visible_wealth', 'hidden_wealth', 'visible_official',
               'hidden_official', 'visible_killing', 'hidden_killing')
    if not groups['month_resource']:
        status = 'outside_month_resource_branch'
    elif any(groups[key] for key in related):
        status = 'related_facts_observed'
    else:
        status = 'no_related_facts_observed'
    relation_rules = ('stem_five_combinations', 'branch_six_harmonies',
                      'branch_six_clashes', 'branch_triple_harmonies')
    interactions = []
    for key in relation_rules:
        rule_id = 'bazi.phase2.' + key
        if rule_id not in steps or not steps[rule_id][1]['output']:
            continue
        # An observed interaction is admissible only with executed, resolvable
        # evidence. Unverified interactions must never enter effect blockers.
        evidence_ids = steps[rule_id][1].get('evidence_ids', [])
        if not evidence_ids or any(eid not in trace.evidence for eid in evidence_ids):
            raise ValueError('Resource interaction lacks executed evidence: ' + rule_id)
        interactions.append({
            'rule_id': rule_id,
            'fact_ref': pointer(key),
            'evidence_ids': list(evidence_ids),
        })
    branch_root_interactions = []
    for key in ('branch_six_clashes', 'branch_six_harmonies',
                'branch_triple_harmonies'):
        rule_id = 'bazi.phase2.' + key
        if rule_id not in steps:
            continue
        step = steps[rule_id][1]
        if step['output'] and (
            not step['evidence_ids'] or
            any(e not in trace.evidence for e in step['evidence_ids'])
        ):
            raise ValueError('Resource root interaction lacks executed evidence: ' + rule_id)
        for index, item in enumerate(step['output']):
            if not item.get('pillars'):
                raise ValueError('Resource root interaction lacks pillar positions: ' + rule_id)
            branch_root_interactions.append({
                'rule_id': rule_id,
                'pillars': list(item['pillars']),
                'fact_ref': pointer(key, f'/{index}'),
                'evidence_ids': list(step['evidence_ids']),
                'effect_status': 'indeterminate',
            })
    provenance = sorted(set(steps['bazi.phase2.ten_gods'][1]['evidence_ids'])
                        | set(steps['bazi.phase2.hidden_stems'][1]['evidence_ids']))
    causal = resource_elemental_causal_gate({
        'positions': groups, 'observed_interactions': interactions,
        'evidence_ids': provenance, 'exact_stem_sites': exact_stem_sites,
        'element_root_sites': element_root_sites,
        'branch_root_interactions': branch_root_interactions,
    })
    return {
        'variant': PATTERN_VARIANT,
        'school_branch': 'yuanhai-印绶官财条件未裁决',
        'status': status,
        'positions': groups,
        'elemental_causal_gate': causal,
        'conditions': [
            {'id': key, 'observed': bool(groups[key]),
             'fact_refs': [position['fact_ref'] for position in groups[key]]}
            for key in ('month_resource',) + related
        ],
        'source_section_ids': ['bazi.section.s057', 'bazi.section.s058'],
        'source_level': 'C',
        'adjudications': {
            'wealth_strong_enough_to_damage_resource': 'indeterminate',
            'official_actually_generates_resource': 'indeterminate',
            'many_officials_or_competing_pattern': 'indeterminate',
        },
        'unresolved': ['strength_definition', 'effective_action', 'official_resource_generation',
                       'wealth_resource_conflict', 'dated_commander', 'other_pattern_selection'],
        'qualified_for_determination': False,
        'determination': None,
        'research_only': True, 'public_enabled': False, 'ai_enabled': False,
        'scope': '月藏印及各柱官财显干/藏干的共现事实；不按数量推财旺、官鬼多、破印、官印相生、成格、吉凶或喜用。',
    }


def qualification(trace, *, family, observation):
    """Evidence-linked pre-determination checklist, NOT a final pattern verdict.

    Disqualification only means this particular monthly hidden-stem observation
    route found no candidate; it never excludes other classical selection routes.
    """
    if family not in ('official', 'resource'):
        raise ValueError('Unknown pattern family')
    month = observation['month_branch']
    candidates = observation['observations']
    commander = observation['dated_commander']
    refs = [row['hidden_fact_ref'] for row in candidates]
    refs.extend(p['fact_ref'] for row in candidates for p in row['visible_positions'])
    context = observation['context_positions']
    related = ('正官', '七杀') if family == 'official' else ('正财', '偏财', '正官', '七杀')
    relevant = [row for row in context if row['ten_god'] in related]
    steps = {s['rule_id']: s for s in trace.steps}
    prereqs = ('pillars', 'ten_gods', 'hidden_stems', 'hidden_to_visible', 'month_command_variant')
    evidence = sorted({e for name in prereqs
                       for e in steps['bazi.phase2.' + name]['evidence_ids']})
    if not evidence or any(e not in trace.evidence for e in evidence):
        raise ValueError('Pattern qualification lacks executed evidence')

    requirements = [
        {'id': 'monthly_hidden_stem_candidate', 'status': 'observed' if candidates else 'not_observed',
         'fact_refs': refs, 'note': '仅此月藏候选支路；不否定地支官局或其他取格法'},
        {'id': 'literal_exposure', 'status': 'observed' if any(r['exposed'] for r in candidates) else 'not_observed',
         'fact_refs': [p['fact_ref'] for r in candidates for p in r['visible_positions']],
         'note': '透出是结构事实；未透不能自动排除别支取格'},
        {'id': 'dated_commander', 'status': 'source_conflict' if commander['conflict_ids'] else 'unresolved',
         'fact_refs': [commander['fact_ref']],
         'note': '本气及无冲突登记都不能取代实际分日司令'},
        {'id': 'luren_miscellaneous_month_exceptions', 'status': 'unresolved',
         'fact_refs': [observation['month_fact_ref']],
         'known_miscellaneous_branch': month in ('辰', '戌', '丑', '未'),
         'note': '禄刃须结合日主专项审查；杂气月不得套普通月令捷径'},
        {'id': 'family_specific_competing_conditions', 'status': 'unresolved',
         'fact_refs': [row['fact_ref'] for row in relevant],
         'note': '官杀去留/混杂' if family == 'official' else '财旺破印/别格/官鬼多'},
        {'id': 'general_strength_and_effects', 'status': 'unresolved',
         'fact_refs': [], 'note': '有限强弱强/弱不自动授予定格资格'},
        {'id': 'classical_branch_selection', 'status': 'unresolved', 'fact_refs': [],
         'note': '任氏及渊海口径不可合并成无差别判断'},
    ]
    for req in requirements:
        for pointer in req['fact_refs']:
            if not pointer.startswith('#/trace/'):
                raise ValueError('Qualification contains an invalid fact reference')
    return {
        'variant': observation['variant'],
        'family': family,
        'branch': 'monthly_hidden_stem_observation_only',
        'qualification_status': 'indeterminate' if candidates else 'disqualified_for_this_branch',
        'family_determination_status': 'unresolved',
        'requirements': requirements,
        'evidence_ids': evidence,
        'evidence_scope': 'executed_structural_dependencies_only',
        'conflict_ids': list(commander['conflict_ids']),
        'research_only': True, 'public_enabled': False, 'ai_enabled': False,
        'scope': '仅审已实现的月藏十神候选路线；资格未完成，不定真假、成败、喜用或任何其他取格支路。',
    }


def candidates(trace, *, family, pattern_variant=PATTERN_VARIANT):
    if pattern_variant != PATTERN_VARIANT or family not in ('official', 'resource'):
        raise ValueError('Unsupported pattern candidate variant or family')
    steps = {s['rule_id']: (i, s) for i, s in enumerate(trace.steps)}
    required = ('pillars', 'ten_gods', 'hidden_stems', 'hidden_to_visible', 'month_command_variant')
    if any('bazi.phase2.' + key not in steps for key in required):
        raise ValueError('Pattern observations require executed structural dependencies')
    for key in required:
        step = steps['bazi.phase2.' + key][1]
        if not step['evidence_ids'] or any(e not in trace.evidence for e in step['evidence_ids']):
            raise ValueError('Pattern dependencies lack executed evidence')

    def output(key):
        return steps['bazi.phase2.' + key][1]['output']

    def pointer(key, suffix=''):
        return f"#/trace/{steps['bazi.phase2.' + key][0]}/output" + suffix

    hidden = output('hidden_stems')
    visible = output('ten_gods')
    month = next((i, row) for i, row in enumerate(hidden) if row['pillar'] == 'month')
    mi, month_row = month
    gods = ('正官',) if family == 'official' else ('正印', '偏印')
    observations = []
    for hi, row in enumerate(month_row['hidden_stems']):
        if row['ten_god'] not in gods:
            continue
        exposure = next(((i, r) for i, r in enumerate(output('hidden_to_visible')['positions'])
                         if r['hidden_pillar'] == 'month' and r['hidden_stem'] == row['stem']), None)
        positions = []
        if exposure:
            for pillar in exposure[1]['visible_pillars']:
                vi, value = next((i, r) for i, r in enumerate(visible) if r['pillar'] == pillar)
                if value['stem'] != row['stem'] or value['ten_god'] != row['ten_god']:
                    raise ValueError('Executed visibility and ten-god facts disagree')
                positions.append({**value, 'fact_ref': pointer('ten_gods', f'/{vi}')})
        observations.append({'stem': row['stem'], 'ten_god': row['ten_god'],
            'hidden_fact_ref': pointer('hidden_stems', f'/{mi}/hidden_stems/{hi}'),
            'visibility_fact_ref': pointer('hidden_to_visible', f'/positions/{exposure[0]}') if exposure else None,
            'visible_positions': positions, 'exposed': bool(positions)})

    # Presence is reported with positions; it is not 官杀混杂, 制杀 or 财旺破印 adjudication.
    context_gods = ('正官', '七杀') if family == 'official' else ('正印', '偏印', '正财', '偏财', '正官', '七杀')
    context = []
    for vi, row in enumerate(visible):
        if row['pillar'] != 'day' and row['ten_god'] in context_gods:
            context.append({**row, 'visibility': 'visible', 'fact_ref': pointer('ten_gods', f'/{vi}')})
    for pi, pillar in enumerate(hidden):
        for hi, row in enumerate(pillar['hidden_stems']):
            if row['ten_god'] in context_gods:
                context.append({'pillar': pillar['pillar'], 'branch': pillar['branch'],
                    'stem': row['stem'], 'ten_god': row['ten_god'], 'visibility': 'hidden',
                    'fact_ref': pointer('hidden_stems', f'/{pi}/hidden_stems/{hi}')})
    command = output('month_command_variant')
    result = {'variant': pattern_variant, 'family': family,
        'status': 'structural_observation_only' if observations else 'no_month_candidate',
        'month_branch': month_row['branch'], 'month_fact_ref': pointer('hidden_stems', f'/{mi}'),
        'observations': observations, 'context_positions': context,
        'dated_commander': {'status': command['commander_status'], 'value': command['commander'],
            'fact_ref': pointer('month_command_variant'), 'conflict_ids': list(command['source_conflict']),
            'required_for_ren_pattern_determination': True, 'blocks_structural_observation': False},
        'special_month_conditions_reviewed': False,
        'determination': {'status': 'unresolved', 'pattern': None, 'true_false': None,
            'success_failure': None, 'useful_god': None},
        'unresolved_conditions': ['dated_commander', 'luren_and_miscellaneous_month_exceptions',
            'official_killing_selection' if family == 'official' else 'resource_damage_and_other_pattern',
            'general_strength_and_actual_effects', 'source_branch_selection'],
        'research_only': True, 'public_enabled': False, 'ai_enabled': False,
        'scope': '现代形式化的月藏十神与逐字透干位置观察；不覆盖地支官局等另支取官，不定格、不取用、不判断成败吉凶。'}
    if family == 'official':
        result['yuanhai_unexposed_official_branch'] = yuanhai_unexposed_official(trace)
        result['yuanhai_hour_killing_restriction'] = yuanhai_hour_killing_restriction(trace)
    if family == 'resource':
        result['yuanhai_resource_month_example'] = yuanhai_resource_month_example(trace)
        result['yuanhai_resource_competing_context'] = yuanhai_resource_competing_context(trace)
    result['qualification'] = qualification(trace, family=family, observation=result)
    return result


# ---------------------------------------------------------------------------
# TJ-012.3 Slice A：任氏禄刃选格路线负向裁定（月逢禄刃，无格可取）。
#
# 治理定位：这是格局模块的第一条 determination 类裁定，但只裁定一件事——
# 任氏（《滴天髓阐微》八格章，s054 已登记批准）取格程序中「若月逢禄刃，
# 无格可取」对月令正格路线的先置排除。输出是路线状态
# （luren_no_month_pattern / not_luren），不是任何格的成立、真假、成败
# 或用神判断；candidates() 的 determination 字典逐字不变，本节任何字段
# 不得让格名/真假/成败/清浊/用神出现非空值（审源报告
# tj012-pattern-determination-scout §7 的 determination=None 范围声明
# 在本切片后继续逐项有效）。
#
# 审定点（先行审计逐项留痕）：
# - A1 句序读法：s054 程序为「先观月令所得何支，次看天干透出何神，
#   再究司令以定真假，然后取用，以分清浊」，禄刃句以「若」领起置于其
#   后，是对月令取格路线本身的关闭：月支即日干禄/刃支时，月令正格路线
#   在进入透干、司令、真假诸步之前已经无格可取，其后「须审日主之喜忌
#   另寻别支透出天干者，借以为用」已是另一条（借用）路线。故本裁定只
#   消费月支与日干两项结构事实，不消费司令；司令未裁定不阻塞本排除，
#   正与原句句序相合。若改读为「禄刃排除也须先究司令」，则「无格可
#   取」四字在程序上无落点（司令所定者为真假，而禄刃月根本不进入真
#   假判断），此读法不成立。
# - A2 表源裁定：十干禄/刃支表取《三命通会》——卷三《论十干禄》定义
#   句十干禄位逐一明列（字符 75008–75053），同节逐干分论复核；卷五
#   《论阳刃》纲句明定五阳干有刃、五阴干无刃（字符 180961–180982），
#   五阳刃位在同节以「戊刃午/壬刃子/庚刃酉/甲刃卯/丙刃午」逐一明列
#   （字符 181644–181689），两节互证。渊海禄节只有散见用例、无十干逐
#   一定义句，文本自足性不及三命，不取为表源。按 TJ-017.1 扩神峰
#   review_scope 先例，本表两节经本批扩登记 bazi.source.sanmingtonghui
#   的 review_scope（同一 Source，普查计数不变）。
# - A3 字形校勘：快照在禄定义句内己/巳互讹——「丙禄己」之己读作巳
#   （丙禄巳）、「戊寄己」之己读作巳（戊寄巳）、「巳寄午」之巳读作己
#   （己寄午），以同节逐干分论（丙禄巳见巳巳、戊禄巳、己禄午）与
#   《论建禄》十干月例的干序及柱例互证读定；表中逐项标 glyph_note，
#   引文逐字保留快照原字，不静默改字。
# - A4 阴干无刃与异说登记：本表阴干 ren=None 是三命《论阳刃》纲句的
#   如实转写。通行另有为阴干配刃位之说，但已登记来源中无逐字依据
#   （《子平真诠》不在密封树内，全文检索 0 命中，见审源报告 §3.1），
#   不登记、不采用、不用口诀补齐；日后有来源登记者另立 school 分支，
#   不得静默改表。
# - A5 杂气分界：登记表禄支集 {寅卯巳午申酉亥子}、刃支集 {卯午酉子}
#   与四季月支集 {辰戌丑未} 均不相交（由表本身可证，测试钉住），故
#   「杂气月与禄刃重合」在本表下不存在；派单预设的戊日戌月重合例经逐
#   项核对证伪（戊禄巳、戊刃午，戌皆非之）。杂气月一律按表直判（其月
#   支必非禄刃，路线不落入本裁定），本结论只及于本负向裁定；杂气如
#   何选格（任氏杂气句与三命杂气格的流派冲突）属 Slice B，本切片不
#   处理、不作杂气例外。
# - A6 借用路线未定：s054 只言「另寻别支透出天干者，借以为用」，给
#   出借用路线的存在与方向，未给借神定名规则（多透干取谁、喜忌如何
#   审定均无已审规则）；建禄/羊刃等借用名目本身是否成格不在本切片裁
#   定范围。故 borrowed_route.status 恒 undetermined，本切片不替原文
#   选神。
#
# 执行链接入：本路线原无密封 Phase1 bundle / Phase2 contract 的
# rule 注册，由 operations.bazi_chart.chart 在 pattern_variant 开启
# 时附于 result['pattern_route']、不进 RuleMatch 与 Evidence（历史
# 姿态见 Slice A 审定）。TJ-018.3 B-2（E0339）完成注册：三命禄/刃
# 两节建成 Canonical sections s063/s064、表源三引文完成绑定，
# Phase1 规则 bazi.rule.r035 与 Phase2 步 bazi.phase2.pattern_route
# 登记入密封契约；chart 在 pattern_variant 开启时以 trace.add 执行
# 注册步（与同块正官/印绶候选步同形），路线块进入 RuleMatch 与
# Evidence，evidence_binding 翻转为 registered_phase1_phase2。
# 恒 research_only，公开投影整体剥离。month_pattern_route 只消费
# 已执行的 pillars 步骤（要求 evidence 已绑定），伪造或缺失事实
# 一律 fail-closed。
LUREN_ROUTE_VARIANT = 'bazi-pattern-luren-route-v1'
LUREN_TABLE_SOURCE_ID = 'bazi.source.sanmingtonghui'
LUREN_TABLE_SNAPSHOT_PATH = ('data/quarantine/public_domain_snapshots/'
                             'daizhigev20/sanming_tonghui.txt')
LUREN_TABLE_SNAPSHOT_SHA256 = ('00e2a7db8bb59b259b99938033bb1bb77947'
                               'e04a15dafc111e62b59378010c86')
LUREN_RULE_SOURCE_ID = 'bazi.source.ditiansui-spouse'

# 十干禄支（《三命通会》卷三《论十干禄》定义句逐一明列）。
LU_BRANCH = {
    '甲': '寅', '乙': '卯', '丙': '巳', '丁': '午', '戊': '巳',
    '己': '午', '庚': '申', '辛': '酉', '壬': '亥', '癸': '子',
}
# 十干刃支（《三命通会》卷五《论阳刃》）：只有五阳干有刃，五阴干无刃，
# 故阴干不入表（ren=None 由查表方显式给出，不是漏登）。
REN_BRANCH = {
    '甲': '卯', '丙': '午', '戊': '午', '庚': '酉', '壬': '子',
}
YANG_STEMS = ('甲', '丙', '戊', '庚', '壬')
YIN_STEMS = ('乙', '丁', '己', '辛', '癸')
MISCELLANEOUS_BRANCHES = ('辰', '戌', '丑', '未')

LUREN_QUOTES = (
    {
        'id': 'renshi.luren_route_exclusion',
        'source_id': LUREN_RULE_SOURCE_ID,
        'source_section_id': 'bazi.section.s054',
        'quote': ('任氏曰:八格者,命中之正理也。先观月令所得何支,次看天干透出何神,'
                  '再究司令以定真假,然后取用,以分清浊,此实依经顺理,若月逢禄刃,'
                  '无格可取,须审日主之喜忌另寻别支透出天干者,借以为用。'),
        'locator': {'char_start': 31681, 'char_end': 31773},
    },
    {
        'id': 'sanming.lu_sentence',
        'source_id': LUREN_TABLE_SOURCE_ID,
        'source_section_id': 'bazi.section.s063',
        'quote': ('甲禄寅乙禄卯庚禄申辛禄酉壬禄亥癸禄子丙禄己丁禄午戊寄己巳寄午'
                  '谓己午乃火旺之乡子随母得禄之义'),
        'locator': {'char_start': 75008, 'char_end': 75053},
    },
    {
        'id': 'sanming.ren_doctrine',
        'source_id': LUREN_TABLE_SOURCE_ID,
        'source_section_id': 'bazi.section.s064',
        'quote': '惟甲丙戊庚壬五阳干有刃乙丁己辛癸五阴干无刃',
        'locator': {'char_start': 180961, 'char_end': 180982},
    },
    {
        'id': 'sanming.ren_positions',
        'source_id': LUREN_TABLE_SOURCE_ID,
        'source_section_id': 'bazi.section.s064',
        'quote': ('戊刃午见子财壬刃子见午财庚刃酉见卯财皆冲之财故忌之至甲刃卯'
                  '不忌戊巳己午之财且忌酉官矣丙刃午'),
        'locator': {'char_start': 181644, 'char_end': 181689},
    },
)

LUREN_ADJUDICATION_NOTES = (
    'A1 句序：s054 禄刃句是对月令取格路线的先置排除（先于透干/司令/真假诸步），本裁定只消费月支与日干，不消费司令。',
    'A2 表源：禄/刃支表取《三命通会》卷三《论十干禄》与卷五《论阳刃》（逐一明列、两节互证）；渊海禄节无十干逐一定义句，自足性不及，不取为表源。',
    'A3 字形：禄定义句快照己/巳互讹（丙禄巳、戊寄巳、己寄午），以同节逐干分论与《论建禄》月例互证读定，引文保留原字。',
    'A4 阴干：阴干无刃是三命纲句的如实转写；阴干配刃的通行异说在已登记来源中无逐字依据，不登记、不采用。',
    'A5 杂气：禄支集与刃支集均与四季月支集不相交，杂气月与禄刃重合在本表下不存在；杂气月按表直判，杂气选格属 Slice B。',
    'A6 借用：借用路线（借以为用）的借神定名规则未审，borrowed_route 恒 undetermined，不替原文选神。',
)

LUREN_LIMITATIONS = (
    '本裁定只关闭或不关闭月令正格路线：luren_no_month_pattern 不表示借用格成立，not_luren 不表示任何正格成立。',
    'determination 其余一切（格名、真假、成败、清浊、用神、喜忌）保持未裁定；审源报告的 determination=None 范围声明继续有效。',
    '禄刃表为三命单一来源口径（C 级、单一电子谱系）；阴干刃位异说未登记，表外推断（以五行/长生类推未列之位）一律禁止。',
    '本路线已完成密封 Phase1/Phase2 注册（bazi.rule.r035 / bazi.phase2.pattern_route，evidence_binding=registered_phase1_phase2，TJ-018.3 B-2 E0339）；注册只补齐证据绑定，路线语义与判定面不变。',
)


def luren_route_lookup(day_stem, month_branch):
    """Pure 禄刃 route lookup over two structural facts (day stem, month branch).

    Fails closed on any stem/branch outside the registered tables. The
    route values are exactly 'luren_no_month_pattern' (month branch is
    the day stem's 禄 or 刃 branch per the registered 三命 table: the
    Ren route exclusion fires) and 'not_luren' (the exclusion does not
    fire; this asserts nothing about any pattern being established).
    """
    if day_stem not in LU_BRANCH:
        raise ValueError('Luren route lookup requires a registered day stem')
    if month_branch not in BRANCHES:
        raise ValueError('Luren route lookup requires a valid month branch')
    lu = LU_BRANCH[day_stem]
    ren = REN_BRANCH.get(day_stem)
    if month_branch == lu:
        route, matched_via = 'luren_no_month_pattern', 'lu'
    elif ren is not None and month_branch == ren:
        route, matched_via = 'luren_no_month_pattern', 'ren'
    else:
        route, matched_via = 'not_luren', None
    return {
        'variant': PATTERN_VARIANT,
        'route_variant': LUREN_ROUTE_VARIANT,
        'rule': {
            'id': 'renshi.luren_route_exclusion',
            'source_id': LUREN_RULE_SOURCE_ID,
            'source_section_id': 'bazi.section.s054',
            'quote_locator': {'char_start': 31681, 'char_end': 31773},
        },
        'route': route,
        'matched_via': matched_via,
        'day_stem': day_stem,
        'month_branch': month_branch,
        'lu_branch': lu,
        'ren_branch': ren,
        'stem_polarity': 'yang' if day_stem in YANG_STEMS else 'yin',
        'miscellaneous_month': month_branch in MISCELLANEOUS_BRANCHES,
        'table': {
            'source_id': LUREN_TABLE_SOURCE_ID,
            'lu_quote_locator': {'char_start': 75008, 'char_end': 75053},
            'ren_doctrine_locator': {'char_start': 180961, 'char_end': 180982},
            'ren_positions_locator': {'char_start': 181644, 'char_end': 181689},
        },
        'borrowed_route': {
            'status': 'undetermined',
            'borrowed_pattern_determination': None,
            'note': ('s054 言「另寻别支透出天干者，借以为用」只给出借用路线'
                     '的存在与方向；借神定名规则未审，建禄/羊刃等借用名目'
                     '本身是否成格不在本切片裁定范围。'),
        },
        'determination': {'status': 'unresolved', 'pattern': None,
                          'true_false': None, 'success_failure': None,
                          'useful_god': None},
        'qualified_for_determination': False,
        'research_only': True, 'public_enabled': False, 'ai_enabled': False,
        'evidence_binding': 'registered_phase1_phase2',
        'adjudication_notes': list(LUREN_ADJUDICATION_NOTES),
        'scope_limits': list(LUREN_LIMITATIONS),
        'scope': ('只裁定任氏月令正格路线在月逢禄刃时关闭（无格可取）；'
                  'not_luren 仅表示不落入此负向裁定，不表示任何格成立；'
                  '不定格名、真假、成败、清浊、用神或吉凶。'),
    }


def month_pattern_route(trace):
    """Consume the executed pillars step and apply the 禄刃 route exclusion.

    Mirrors the module's fail-closed discipline: the pillars step must
    exist and carry executed, resolvable evidence; only the day-master
    stem and the month branch are read.
    """
    steps = {row['rule_id']: (i, row) for i, row in enumerate(trace.steps)}
    if 'bazi.phase2.pillars' not in steps:
        raise ValueError('Luren route requires executed pillar facts')
    index, step = steps['bazi.phase2.pillars']
    if not step['evidence_ids'] or any(e not in trace.evidence for e in step['evidence_ids']):
        raise ValueError('Luren route lacks executed evidence')
    pillars = step['output']
    day_stem = pillars['day_master']['stem']
    month_branch = pillars['ganzhi'][1][1]
    result = luren_route_lookup(day_stem, month_branch)
    result['fact_refs'] = {
        'day_master': f'#/trace/{index}/output/day_master/stem',
        'month_branch': f'#/trace/{index}/output/ganzhi/1',
    }
    result['consumed_rule_ids'] = ['bazi.phase2.pillars']
    return result


# ---------------------------------------------------------------------------
# TJ-012.3 Slice B：杂气月选格陈述（《滴天髓阐微》原注分支＋三命杂气格
# 流派冲突并列）。
#
# 治理定位：本切片只在四季月（辰戌丑未）给出「选格陈述」级别的输出，
# 不是定格：任氏分支陈述止于原文程序所及之处（戊己日看人元透出者并列
# 为选格对象；一般日主只录「只当取土为格」原文而不换算格名），三命
# 杂气格两案只登记为冲突分支证据、并列呈现、不裁定。determination
# 其余一切字段（格名、真假、成败、清浊、用神、喜忌）全域保持 None，
# 审源报告 tj012-pattern-determination-scout §7 的 determination=None
# 范围声明在本切片后继续逐项有效。
#
# 审定点（先行审计逐项留痕）：
# - B1 句读与作者层：注册节为八格章「影响遥系」子题原注段（字符
#   33161–33313，题句 33144–33160「影响遥系既为虚，杂气财官不可拘」），
#   作者层是原注而非任氏曰（任氏曰在本段之后另论暗冲暗合）；本模块
#   通称「任氏分支」沿审源与模块既有口径，指《滴天髓阐微》一家之说
#   与三命分支对举，层归属以登记为准，不以任氏之名改原注之实。段内
#   三臂分界：(i) 四季月生人「只当取土为格，不可言杂气财官」；
#   (ii) 戊己日生于四季月者「当看人元透出天干者取格」；(iii) 建禄/
#   月刃「亦当看月令中人元透于天干者取格，若不合气象形局，则又无格
#   矣」。(iii) 非四季月臂且其「气象形局」未审，不在本切片执行范围，
#   只随段登记；段首飞天合禄语与段末「只取用神」数句是飞天合禄语境，
#   不外推为杂气通则。字形校勘：「建禄月动羊无能为刃」一句字形讹乱
#   （「羊」疑为羊刃省称、「月动」语序存疑），逐字保留原字存疑登记，
#   该臂不执行，故讹乱不入任何输出。
# - B2 人元透出的结构读法：「人元」即月支藏干（已执行 hidden_stems
#   事实，含其自带十神）；「透出天干者」即该藏干与年/月/时干同字显现
#   （已执行 hidden_to_visible 事实）——日干除外：日干是日主参照本身，
#   事实层 day_stem_excluded 口径与全模块一致，本切片不另设位置过滤、
#   不自创透出口径。可执行部分止于：透出人元的逐项清单（藏干序、十神、
#   显现柱位）。不可执行部分：多个人元透出时原文不予定序、不予定名，
#   本切片逐项并列、不代选；透出本身不等于成格（determination 恒
#   None），「取格」在本切片只落实为选格对象清单这一陈述级别。
# - B3 土格换算未审：臂 (i) 的「取土为格」若换算为格名，须先定「土」
#   指月支本气之土（辰戌丑未本气皆戊/己土，快照本气事实可核），再对
#   日干作十神换算——此换算链原文未明言，属解释风险（审源 §5.6），
#   本批不输出换算后的格名或十神：臂 (i) 陈述只并列原文与
#   conversion_status=unadjudicated。一般日主（非戊己）四季月一律走
#   臂 (i)，与该月人元透出与否无关（臂 (i) 不以透出为条件）。
# - B4 戊己臂弃判：戊己日四季月无人元透出时，臂 (ii) 程序无对象可
#   取，陈述 abstained（abstention_reason=no_exposed_renyuan）。段内
#   (iii) 的「若不合气象形局，则又无格矣」不移用于臂 (ii) 作「无格」
#   断言——那是建禄/月刃臂的文本，且「气象形局」未审；本弃判只陈述
#   程序无对象，不说该盘无格、不关闭其他取格路线。
# - B5 流派冲突并列：三命两案只登记为冲突分支证据，不作规则。案一
#   卷六《日禄归时》七法「青云得路」实案句（字符 192131–192174）：
#   壬日戌月造直称「作杂气格论尤是」；案二女命章诗句（字符
#   245030–245081）：「杂气格中禄最佳」并自注甲乙丑月之例。冲突点：
#   (1) 杂气格名目本身——原注句明言「不可言杂气财官」，三命以杂气
#   格为正式选格名目并许之；(2) 非戊己日盘面——原注只给「取土为格」
#   （换算未审），案二即以甲乙（非戊己）丑月立杂气格例，两说对同类
#   盘面的选格名目不同；(3) 戊己臂——两案日主均非戊己，无戊己臂的
#   直接反例在案，冲突在此臂只及杂气格名目的框架层，如实标注、不
#   夸大。冲突以 conflict_present＋案引并列呈现，任一四季月盘面均标
#   记（冲突是选格框架之争，不系于个盘构成），不裁定、不以一说压
#   一说。案一造为明代进士造，出生时刻无考、不可复现，引文只作流派
#   立场证据；Golden 以同型结构对照例（壬日戌月、月藏正财透出）替代
#   并如实标注。
# - B6 与 Slice A 共存：pattern_zaqi 与 pattern_route 并列附于研究
#   结果、互不改写；两者的月支域不相交（禄/刃支集与四季月支集不相
#   交，Slice A 的 A5 已证、测试钉住），但本函数不依赖该不相交性，
#   各自独立判定。本陈述尚无密封 Phase1 bundle / Phase2 contract 的
#   rule 注册，故不新增 trace rule、不进 RuleMatch 与 Evidence，
#   evidence_binding=pending_phase1_rule_registration；恒 research_only，
#   公开投影整体剥离。month_pattern_zaqi 只消费已执行的 pillars /
#   ten_gods / hidden_stems / hidden_to_visible 步骤（要求 evidence 已
#   绑定），伪造、缺失或自相矛盾的事实一律 fail-closed。
#
# 注册接入（治理 pending 8 项审计推荐批，E0342）：本陈述原无密封
# Phase1 bundle / Phase2 contract 的 rule 注册（历史姿态见上 B6），
# E0342 完成注册：滴天髓杂气段建成 Canonical section s065
# （bazi.chapter.pattern_bage 既有章）、三命两例证以 S3 窗口建成
# sections s066/s067，3 条引文完成绑定（原注段为规则引文、两例证
# 为 conflict_branch_evidence，沿 r031/r035 子集先例）；Phase1
# 规则 bazi.rule.r036 与 Phase2 步 bazi.phase2.pattern_zaqi 登记
# 入密封契约；chart 在 pattern_variant 开启时以 trace.add 执行
# 注册步，陈述块进入 RuleMatch 与 Evidence，evidence_binding
# 翻转为 registered_phase1_phase2。陈述语义逐字不变：戊己臂多人元
# 透出并列、无透 abstain、一般臂只录「取土为格」原文且土格换算
# 恒 unadjudicated、三命两案恒只作冲突分支证据（B5 不裁定）。
ZAQI_SELECTION_VARIANT = 'bazi-pattern-zaqi-selection-v1'
ZAQI_RULE_SOURCE_ID = 'bazi.source.ditiansui-spouse'
ZAQI_RULE_SNAPSHOT_PATH = ('data/quarantine/public_domain_snapshots/'
                           'daizhigev20/ditiansui_chanwei.txt')
ZAQI_RULE_SNAPSHOT_SHA256 = ('6a875a317c7ba1012285ed12d3bfa5577b50c9f'
                             'dfd568ece323a12feafe38795')
ZAQI_CONFLICT_SOURCE_ID = 'bazi.source.sanmingtonghui'
ZAQI_CONFLICT_SNAPSHOT_PATH = ('data/quarantine/public_domain_snapshots/'
                               'daizhigev20/sanming_tonghui.txt')
ZAQI_CONFLICT_SNAPSHOT_SHA256 = ('00e2a7db8bb59b259b99938033bb1bb77947'
                                 'e04a15dafc111e62b59378010c86')
WUJI_STEMS = ('戊', '己')
EXPOSABLE_PILLARS = ('year', 'month', 'hour')

ZAQI_QUOTES = (
    {
        'id': 'renshi.zaqi_passage',
        'source_id': ZAQI_RULE_SOURCE_ID,
        'source_section_id': 'bazi.section.s065',
        'layer': '原注',
        'quote': ('原注:飞天合禄之类,固为影响遥系而非格矣。如四季月生人,'
                  '只当取土为格,不可言杂气财官;戊己日生于四季月者,当看人元'
                  '透出天干者取格,不可概以杂气财官论之;至于建禄月动羊无能'
                  '为刃,亦当看月令中人元透于天干者取格,若不合气象形局,则又'
                  '无格矣。只取用神,用神又无所取,只得看其大势,以皮面上断其'
                  '穷通。不可执格论也'),
        'locator': {'char_start': 33161, 'char_end': 33313},
    },
    {
        'id': 'sanming.zaqi_case_rilu',
        'source_id': ZAQI_CONFLICT_SOURCE_ID,
        'source_section_id': 'bazi.section.s066',
        'layer': '实案评语',
        'quote': ('又壬午庾戌壬子辛亥身旺印助登戊辰进士为刑部郎中作杂气格'
                  '论尤是故丁丑运戊辰科丑刑辰冲故也'),
        'locator': {'char_start': 192131, 'char_end': 192174},
    },
    {
        'id': 'sanming.zaqi_poem_nvming',
        'source_id': ZAQI_CONFLICT_SOURCE_ID,
        'source_section_id': 'bazi.section.s067',
        'layer': '女命章诗句及自注',
        'quote': ('杂气格中禄最佳干头便混也堪夸运行财地无伤刼嫁得才郎享福'
                  '遐【甲乙丑月之例俱藏夫星干头不忌混杂此以月言也】'),
        'locator': {'char_start': 245030, 'char_end': 245081},
    },
)

ZAQI_CONFLICT_POINTS = (
    '名目框架：原注句明言四季月「不可言杂气财官」，三命两案以「杂气格」为正式选格名目并许之（案一「作杂气格论尤是」、案二「杂气格中禄最佳」）。',
    '非戊己日盘面：原注对非戊己日四季月只给「只当取土为格」一句（土格换算未审），案二即以甲乙（非戊己）丑月立杂气格例，两说对同类盘面的选格名目不同。',
    '戊己臂：两案日主均非戊己，无戊己臂的直接反例在案；冲突在此臂只及杂气格名目的框架层，不夸大为程序之争。',
)

ZAQI_ADJUDICATION_NOTES = (
    'B1 句读与层：注册节为八格章「影响遥系」子题原注段（33161–33313），作者层为原注；三臂分界——(i) 四季月取土，(ii) 戊己日看人元透出，(iii) 建禄/月刃臂不在本切片执行范围。「建禄月动羊无能为刃」字形讹乱存疑登记，该臂不执行。',
    'B2 人元透出：人元即月支藏干，透出以已执行 hidden_to_visible 事实为准（日干除外，与事实层 day_stem_excluded 口径一致）；可执行止于透出清单，多透并列不代选，透出不等于成格。',
    'B3 土格换算：「只当取土为格」的格名/十神换算链原文未明言，本批不换算，陈述只并列原文与 conversion_status=unadjudicated。',
    'B4 戊己弃判：戊己日四季月无人元透出 → abstained（程序无对象）；段内 (iii) 的「则又无格矣」不移用为本盘无格断言。',
    'B5 冲突并列：三命两案只登记为冲突分支证据（案一 192131–192174、案二 245030–245081），conflict_present 与案引并列呈现，不裁定；案一造出生时刻无考、不可复现。',
    'B6 共存：pattern_zaqi 与 Slice A 的 pattern_route 并列、互不改写，各自独立判定；本陈述已完成 Phase1/Phase2 rule 注册（bazi.rule.r036 / bazi.phase2.pattern_zaqi，evidence_binding=registered_phase1_phase2，E0342），注册只补齐证据绑定，陈述语义不变。',
)

ZAQI_LIMITATIONS = (
    '本陈述是选格陈述/分支级别，不是定格：不给格名、真假、成败、清浊、用神或喜忌；determination 其余字段全域保持 None，审源报告的 determination=None 范围声明继续有效。',
    '原注段 (iii) 建禄/月刃臂与「气象形局」未执行；「取土为格」的土格换算未审；分日司令未裁定不因本切片而解，选格陈述不等于真假裁定。',
    '三命两案只作冲突分支证据登记，不作规则；不得以任氏分支压过三命，亦不得以三命实案消解任氏句。',
    '本陈述已完成密封 Phase1/Phase2 rule 注册（bazi.rule.r036 / bazi.phase2.pattern_zaqi，evidence_binding=registered_phase1_phase2，治理 pending 8 项审计推荐批 E0342）；注册只补齐证据绑定，陈述语义与判定面不变；透出事实以既有 hidden_to_visible 为准（日干除外）。',
)


def zaqi_selection_lookup(day_stem, month_branch, month_hidden_stems,
                          exposed_renyuan):
    """Pure 杂气 selection statement over executed structural facts.

    month_hidden_stems is the month branch's hidden stems in executed
    fact order as {'stem', 'ten_god'} rows; exposed_renyuan is the
    subset of those stems that are visible on the year/month/hour
    stems, as {'stem', 'ten_god', 'visible_pillars'} rows (the day stem
    is the day-master reference itself and never counts as exposure,
    mirroring the executed hidden_to_visible fact). Fails closed on
    any input inconsistent with those fact shapes. The statement is a
    branch-level selection statement only: it never names a pattern.
    """
    if day_stem not in STEMS:
        raise ValueError('Zaqi selection requires a valid day stem')
    if month_branch not in BRANCHES:
        raise ValueError('Zaqi selection requires a valid month branch')
    hidden = []
    seen = set()
    for row in month_hidden_stems or []:
        stem, ten_god = row.get('stem'), row.get('ten_god')
        if stem not in STEMS or not isinstance(ten_god, str) or not ten_god:
            raise ValueError('Zaqi selection requires valid hidden stem facts')
        if stem in seen:
            raise ValueError('Zaqi selection hidden stems must be unique')
        seen.add(stem)
        hidden.append({'stem': stem, 'ten_god': ten_god})
    hidden_by_stem = {row['stem']: row for row in hidden}
    exposed = []
    exposed_seen = set()
    for row in exposed_renyuan or []:
        stem, ten_god = row.get('stem'), row.get('ten_god')
        pillars = row.get('visible_pillars')
        if stem not in hidden_by_stem or hidden_by_stem[stem]['ten_god'] != ten_god:
            raise ValueError('Exposed renyuan must be month hidden stems')
        if stem in exposed_seen:
            raise ValueError('Exposed renyuan must be unique')
        if (not pillars or len(set(pillars)) != len(pillars)
                or any(p not in EXPOSABLE_PILLARS for p in pillars)):
            raise ValueError('Exposed renyuan needs year/month/hour pillars only')
        exposed_seen.add(stem)
        exposed.append({'stem': stem, 'ten_god': ten_god,
                        'visible_pillars': list(pillars)})
    exposed.sort(key=lambda row: [h['stem'] for h in hidden].index(row['stem']))

    miscellaneous = month_branch in MISCELLANEOUS_BRANCHES
    result = {
        'variant': PATTERN_VARIANT,
        'selection_variant': ZAQI_SELECTION_VARIANT,
        'rule': {
            'id': 'renshi.zaqi_selection',
            'source_id': ZAQI_RULE_SOURCE_ID,
            'source_section_id': 'bazi.section.s065',
            'layer': '原注',
            'quote_locator': {'char_start': 33161, 'char_end': 33313},
        },
        'status': 'not_applicable',
        'abstention_reason': None,
        'day_stem': day_stem,
        'month_branch': month_branch,
        'miscellaneous_month': miscellaneous,
        'arm': None,
        'month_hidden_renyuan': [],
        'exposed_renyuan': [],
        'selection': None,
        'conflict': {'conflict_present': False,
                     'branch': 'sanming_zaqi_pattern',
                     'case_refs': [], 'points': []},
        'determination': {'status': 'unresolved', 'pattern': None,
                          'true_false': None, 'success_failure': None,
                          'useful_god': None},
        'qualified_for_determination': False,
        'research_only': True, 'public_enabled': False, 'ai_enabled': False,
        'evidence_binding': 'registered_phase1_phase2',
        'adjudication_notes': list(ZAQI_ADJUDICATION_NOTES),
        'scope_limits': list(ZAQI_LIMITATIONS),
        'scope': ('只在四季月（辰戌丑未）给出任氏（原注）分支的选格陈述与'
                  '三命杂气格流派冲突并列；不定格名、真假、成败、清浊、'
                  '用神或吉凶。'),
    }
    if not miscellaneous:
        return result
    if not hidden:
        raise ValueError('A miscellaneous month must carry hidden stem facts')
    result['month_hidden_renyuan'] = hidden
    result['exposed_renyuan'] = exposed
    result['conflict'] = {
        'conflict_present': True,
        'branch': 'sanming_zaqi_pattern',
        'case_refs': [
            {'id': 'sanming.zaqi_case_rilu',
             'source_id': ZAQI_CONFLICT_SOURCE_ID,
             'source_section_id': 'bazi.section.s066',
             'locator': {'char_start': 192131, 'char_end': 192174},
             'note': '卷六《日禄归时》实案：壬日戌月造「作杂气格论尤是」；只登记为冲突证据，不作规则。'},
            {'id': 'sanming.zaqi_poem_nvming',
             'source_id': ZAQI_CONFLICT_SOURCE_ID,
             'source_section_id': 'bazi.section.s067',
             'locator': {'char_start': 245030, 'char_end': 245081},
             'note': '女命章诗句「杂气格中禄最佳」及甲乙丑月自注；只登记为冲突证据，不作规则。'},
        ],
        'points': list(ZAQI_CONFLICT_POINTS),
    }
    if day_stem in WUJI_STEMS:
        result['arm'] = 'wuji_exposed_renyuan'
        if not exposed:
            result['status'] = 'abstained'
            result['abstention_reason'] = 'no_exposed_renyuan'
            return result
        result['status'] = 'stated'
        result['selection'] = {
            'level': 'branch_selection_statement',
            'basis': 'exposed_renyuan',
            'original_phrase': '当看人元透出天干者取格',
            'selected_candidates': exposed,
            'earth_conversion': None,
            'pattern_determination': None,
            'note': ('依原注戊己臂程序：选格对象为月支人元中透出天干者，'
                     '逐项并列；原文不予定序定名，本陈述不代选、不定格。'),
        }
        return result
    result['arm'] = 'general_tu_unconverted'
    result['status'] = 'stated'
    result['selection'] = {
        'level': 'branch_selection_statement',
        'basis': 'original_text_only',
        'original_phrase': '只当取土为格,不可言杂气财官',
        'selected_candidates': [],
        'earth_conversion': {
            'status': 'unadjudicated',
            'converted_pattern_name': None,
            'converted_ten_god': None,
            'note': ('「土」是否指月支本气之土、再对日干作十神换算，原文'
                     '未明言；本批不换算，只录原文。'),
        },
        'pattern_determination': None,
        'note': ('依原注一般臂：四季月只当取土为格、不可言杂气财官；该臂'
                 '不以人元透出为条件，透出清单只作事实并列。'),
    }
    return result


def month_pattern_zaqi(trace):
    """Consume executed facts and state the 杂气 selection branch statement.

    Mirrors the module's fail-closed discipline: the pillars, ten_gods,
    hidden_stems and hidden_to_visible steps must exist, carry executed
    resolvable evidence, and agree with each other; only then is the
    pure lookup applied. Exposure follows the executed
    hidden_to_visible positions (day stem excluded by that fact's own
    definition).
    """
    steps = {row['rule_id']: (i, row) for i, row in enumerate(trace.steps)}
    required = ('pillars', 'ten_gods', 'hidden_stems', 'hidden_to_visible')
    if any('bazi.phase2.' + name not in steps for name in required):
        raise ValueError('Zaqi selection requires executed structural facts')
    for name in required:
        step = steps['bazi.phase2.' + name][1]
        if not step['evidence_ids'] or any(e not in trace.evidence for e in step['evidence_ids']):
            raise ValueError('Zaqi selection lacks executed evidence')

    def fact_ref(name, suffix=''):
        return f"#/trace/{steps['bazi.phase2.' + name][0]}/output" + suffix

    pillars = steps['bazi.phase2.pillars'][1]['output']
    visible = steps['bazi.phase2.ten_gods'][1]['output']
    hidden = steps['bazi.phase2.hidden_stems'][1]['output']
    visibility = steps['bazi.phase2.hidden_to_visible'][1]['output']
    day_stem = pillars['day_master']['stem']
    month_branch = pillars['ganzhi'][1][1]
    mi, month_row = next((i, row) for i, row in enumerate(hidden)
                         if row['pillar'] == 'month')
    if month_row['branch'] != month_branch:
        raise ValueError('Zaqi selection evidence is inconsistent')
    exposed = []
    for row in month_row['hidden_stems']:
        position = next((p for p in visibility['positions']
                         if p['hidden_pillar'] == 'month'
                         and p['hidden_stem'] == row['stem']), None)
        if position is None:
            continue
        for pillar in position['visible_pillars']:
            value = next(r for r in visible if r['pillar'] == pillar)
            if value['stem'] != row['stem'] or value['ten_god'] != row['ten_god']:
                raise ValueError('Executed visibility and ten-god facts disagree')
        exposed.append({'stem': row['stem'], 'ten_god': row['ten_god'],
                        'visible_pillars': list(position['visible_pillars'])})
    result = zaqi_selection_lookup(
        day_stem, month_branch,
        [{'stem': row['stem'], 'ten_god': row['ten_god']}
         for row in month_row['hidden_stems']],
        exposed)
    result['fact_refs'] = {
        'day_master': fact_ref('pillars', '/day_master/stem'),
        'month_branch': fact_ref('pillars', '/ganzhi/1'),
        'month_hidden_stems': fact_ref('hidden_stems', f'/{mi}/hidden_stems'),
        'hidden_to_visible': fact_ref('hidden_to_visible', '/positions'),
    }
    result['consumed_rule_ids'] = ['bazi.phase2.' + name for name in required]
    return result


# ---------------------------------------------------------------------------
# TJ-012.3 Slice D-1：任氏分支寅月真格判定（非对称）。
#
# 治理定位：格局 determination 的首个肯定面切片，但严格非对称——只裁定
# 任氏（《滴天髓阐微》八格章）分支、寅月、真格成立与否一件事。成立链
# 全部已登记：s053（原注）真格定义句「格之真者，月支之神，透于天干也」
# ＋负句「以散乱之天干，而寻其得所附于提纲，非格也」；s054（任氏曰）
# 程序句「再究司令以定真假」；司令事实由 Slice C 试点 Variant
# bazi-siling-yin-pilot-v1 在其 computed 时供给；透干事实由已执行
# hidden_stems / hidden_to_visible / ten_gods 供给；禄刃路线优先序由
# Slice A 审定 A1 供给。破格/成败/清浊/用神在本块恒 None 并逐字段标
# unreviewed——八格章无逐格破格条件句，破格审定材料（渊海分神专论）
# 尚未逐节登记且多依赖未裁定的旺衰与三刑事实。「破格恒未审」以字段级
# 状态呈现，不是一句总注脚。candidates() 与 Slice A/B 两块的任何字段
# 逐字不变，本块并列添加。
#
# 审定点（先行审计与父级裁定逐项留痕）：
# - D1 保守读法（父级裁定一）：commander_not_visible 取 s053 定义的
#   否定面——司令不透即不满足「格之真者」的定义，结论止于「司令不
#   透、无真格」，永不使用「假格」标签、永不取 true_false='false'。
#   若连否定面也不得输出，本切片将退化为仅肯定面；本裁定采保守读法
#   输出否定面，但不越界到假格名目。
# - D2 日干不计透（父级裁定二）：D-1 的「透」与事实层
#   day_stem_excluded 既有口径同义——日干是日主参照本身，不计入透
#   干。分层依据如实登记：s053/s054 原文对柱位沉默，此为审定、非原文
#   结论；事实层 hidden_to_visible 与 Slice A/B 全部透干消费均以日干
#   除外为准，determination 层不另立异义。Slice B 审定 B2 的陈述级口
#   径经本裁定升格为 determination 级（B2 口径升格，明示在册，可经
#   后续订正事件推翻）。后果钉死于 Golden：戊日主×戊段、丙日主×丙段
#   在无其他同干显干时一律 commander_not_visible，同干透于年/月/时
#   任一柱则 true；甲段×甲日主被 Slice A 路线优先序先行关闭
#   （abstained），不达本步。
# - D3 判定序：(1) 月支域门——非寅即 abstained，不外推；(2) 禄刃路
#   线优先序——Slice A 审定 A1（排除先于透干/司令/真假诸步），路线
#   关闭时 abstained 并注明 precedence；(3) 试点在位且 status 为
#   computed——rejected/uncertain/not_applicable 或结构不可核验一律
#   abstained 并原样携带试点状态与理由；(4) 司令透干核对——司令须为
#   月支藏干（已执行事实），透于年/月/时干（日干除外）则真格成立，
#   格名由司令干对日主的已执行十神换算；不透则
#   commander_not_visible。
# - D4 落地形态（先行审计审定）：operations.bazi_chart.chart() 不携
#   带出生瞬时与 jie 声明，试点不能在 chart 内调用，故本块落为独立
#   组合函数（trace 消费＋显式传入试点结果），不附 chart、不新增
#   trace rule、不进 RuleMatch 与 Evidence；公开投影对
#   pattern_determination_ren_yin 键防御性整体剥离（与 Slice A/B/C
#   剥离点同形）。
# - D5 格名换算：格名是 s053 定义内的机械换算名（司令干对日主十神
#   ＋「格」）。司令与日主同干且透于他柱时（D2 裁定专项的对照例）
#   十神为比肩，换算名「比肩格」如实记录；本块只主张该盘面满足
#   s053 定义，不就该名目是否属通行八格名目清单另行裁定。
# - D6 试点信任界：试点结果是显式输入声明而非已执行证据。本块核验
#   其身份钉值（Variant 名、calculation_convention 的 id/version、
#   口径 version_id、s024 来源节、research 旗标），并以已执行事实交
#   叉核对司令：司令须为月支藏干，透干位置须经 hidden_to_visible 与
#   ten_gods 双事实一致。任一不符即 abstained（调用方自报司令与事实
#   复算不符的 fail-closed 落点）。司令本身的独立复算（provider 身
#   份、节气回放、登记完整性）属试点自身契约，本块不重复执行。
REN_YIN_TRUE_VARIANT = 'ren-pattern-yin-true-v1'
REN_YIN_RULE_SOURCE_ID = 'bazi.source.ditiansui-spouse'
REN_YIN_SNAPSHOT_PATH = ZAQI_RULE_SNAPSHOT_PATH
REN_YIN_SNAPSHOT_SHA256 = ZAQI_RULE_SNAPSHOT_SHA256
REN_YIN_PILOT_VARIANT = 'bazi-siling-yin-pilot-v1'

ZHENGE_QUOTES = (
    {
        'id': 'renshi.zhenge_definition',
        'source_id': REN_YIN_RULE_SOURCE_ID,
        'source_section_id': 'bazi.section.s053',
        'layer': '原注',
        'quote': ('格之真者,月支之神,透于天干也。以散乱之天干,而寻其得所附于'
                  '提纲,非格也。'),
        'locator': {'char_start': 31580, 'char_end': 31617},
    },
    {
        'id': 'renshi.siling_true_false_procedure',
        'source_id': REN_YIN_RULE_SOURCE_ID,
        'source_section_id': 'bazi.section.s054',
        'layer': '任氏曰',
        'quote': ('任氏曰:八格者,命中之正理也。先观月令所得何支,次看天干透出何神,'
                  '再究司令以定真假,然后取用,以分清浊,此实依经顺理,若月逢禄刃,'
                  '无格可取,须审日主之喜忌另寻别支透出天干者,借以为用。'),
        'locator': {'char_start': 31681, 'char_end': 31773},
        'note': ('与 Slice A 的 renshi.luren_route_exclusion 为同一 s054 引文；'
                 '本块消费其中的「再究司令以定真假」程序句与禄刃排除句（优先序）。'),
    },
)

REN_YIN_ADJUDICATION_NOTES = (
    'D1 保守读法（父级裁定）：commander_not_visible 是 s053 定义的否定面，结论止于「司令不透、无真格」，永不使用「假格」标签；破格/成败/清浊/用神恒 None 并逐字段标 unreviewed。',
    'D2 日干不计透（父级裁定）：「透」与事实层 day_stem_excluded 及 Slice A/B 全部透干消费同义，日干不计入透干；原文对柱位沉默，此为审定而非原文结论；Slice B 的 B2 陈述级口径经本裁定升格为 determination 级（B2 口径升格），可经后续订正事件推翻。',
    'D3 判定序：月支域门（寅）→ 禄刃路线优先序（Slice A 审定 A1：排除先于司令/真假步）→ 试点 computed → 司令透干核对；任一步不满足即 abstained 并注明步号与原因。',
    'D4 落地形态：独立组合函数（trace 消费＋显式传入试点结果）；chart() 不携带出生瞬时与 jie 声明，试点不能在 chart 内调用，故不附 chart、不新增 trace rule；公开投影对 pattern_determination_ren_yin 键防御性整体剥离。',
    'D5 格名换算：格名 = 司令干对日主的已执行十神＋「格」的机械换算名（s053 定义内读法）；司令与日主同干且透于他柱时十神为比肩，换算名「比肩格」如实记录，本块不就该名目是否属通行八格名目清单另行裁定。',
    'D6 试点信任界：试点结果为显式输入声明，本块核验其 Variant/约定身份钉值，并以已执行事实交叉核对司令（须为月支藏干、透干位置经 hidden_to_visible 与 ten_gods 双事实一致）；不符即 abstained。司令的独立复算属试点自身契约，本块不重复。',
)

REN_YIN_LIMITATIONS = (
    '本块只裁定任氏分支寅月真格成立与否一件事，不构成任氏八格真假判断体系；不得据此宣称已经判定假格、喜用神或吉凶（用户 Slice C 裁定第五节边界）。',
    '破格未审：八格章无逐格破格条件句，破格审定材料（渊海分神专论）尚未逐节登记且多依赖未裁定的旺衰与三刑事实；success_failure/purity/useful_god 恒 None 并逐字段标 unreviewed。',
    '不外推其他月份：分日司令冲突矩阵其余月份仍 conflict/research_only，司令扩月须新的用户级流派裁定，不在本切片权力内。',
    '本块尚无密封 Phase1/Phase2 rule 注册（evidence_binding=pending_phase1_rule_registration），不进 RuleMatch 与 Evidence；恒 research_only，公开投影整体剥离。',
)

REN_YIN_UNREVIEWED = {
    'success_failure': ('unreviewed：八格章无逐格成败（破格）条件句，破格审定'
                        '材料尚未逐节登记；本块不裁定成败。'),
    'purity': ('unreviewed：清浊之分在 s054 程序中后于真假步，本块未审；'
               '本块不裁定清浊。'),
    'useful_god': ('unreviewed：取用以分清浊属真假步之后的程序，本块未审；'
                   '本块不裁定用神。'),
}


def _ren_yin_pilot_claim(pilot_result):
    """Validate the structural identity pins of an explicit pilot block.

    Returns (status, reason, commander) where status is None when the
    block is not a verifiable pilot result at all. The pilot block is
    a caller-supplied claim, not executed evidence: identity pins are
    checked against the live Slice C registration, and the claimed
    commander is cross-checked against executed facts by the caller.
    """
    if not isinstance(pilot_result, dict):
        return None, 'pilot_result_missing', None
    if pilot_result.get('variant') != REN_YIN_PILOT_VARIANT:
        return None, 'pilot_variant_mismatch', None
    if pilot_result.get('research_only') is not True \
            or pilot_result.get('public_enabled') is not False \
            or pilot_result.get('ai_enabled') is not False:
        return None, 'pilot_governance_flags_mismatch', None
    status = pilot_result.get('status')
    if status not in ('computed', 'not_applicable', 'rejected', 'uncertain'):
        return None, 'pilot_status_unknown', None
    if status != 'computed':
        return status, pilot_result.get('reason'), None
    commander = pilot_result.get('commander')
    if commander not in STEMS:
        return None, 'pilot_commander_invalid', None
    provenance = pilot_result.get('provenance')
    if not isinstance(provenance, dict):
        return None, 'pilot_provenance_missing', None
    try:
        conv = _siling_matrix.SILING_CALCULATION_CONVENTION
        version_id = conv['scope']['version_id']
        cell = _siling_matrix.SILING_MATRIX[version_id]['寅']
        quote = {row['id']: row for row in _siling_matrix.SILING_QUOTES}[
            cell['quotes'][0]]
    except (KeyError, IndexError, TypeError):
        return None, 'pilot_registration_unreadable', None
    if provenance.get('calculation_convention') != {
            'id': conv['id'], 'version': conv['version']} \
            or provenance.get('version_id') != version_id \
            or provenance.get('source_id') != quote['source_id'] \
            or provenance.get('source_section_id') != quote['source_section_id']:
        return None, 'pilot_provenance_mismatch', None
    if pilot_result.get('scope_month_branch') != '寅' \
            or pilot_result.get('month_branch') != '寅':
        return None, 'pilot_scope_mismatch', None
    return status, pilot_result.get('reason'), commander


def ren_yin_true_false_lookup(day_stem, month_branch, *, route, pilot_status,
                              pilot_reason, pilot_commander,
                              month_hidden_stems, commander_ten_god,
                              commander_visible_pillars):
    """Pure Ren-branch 寅月 true-pattern determination over checked facts.

    All inputs are pre-validated facts or claims: ``route`` is the
    Slice A route value; ``pilot_status``/``pilot_commander`` are the
    structurally validated pilot claim (status None when the pilot
    block is unverifiable); ``month_hidden_stems`` are the executed
    month hidden stems; ``commander_ten_god`` is the executed ten-god
    of the claimed commander (None when it is not a month hidden
    stem); ``commander_visible_pillars`` is the cross-checked list of
    year/month/hour pillars exposing the commander (day stem never
    counts, adjudication D2). The judgement order is adjudication D3.
    """
    if day_stem not in STEMS:
        raise ValueError('Ren yin determination requires a valid day stem')
    if month_branch not in BRANCHES:
        raise ValueError('Ren yin determination requires a valid month branch')
    if route not in ('luren_no_month_pattern', 'not_luren'):
        raise ValueError('Ren yin determination requires the Slice A route')
    hidden = list(month_hidden_stems or [])
    if any(stem not in STEMS for stem in hidden) \
            or len(set(hidden)) != len(hidden):
        raise ValueError('Ren yin determination requires valid hidden stems')
    visible = list(commander_visible_pillars or [])
    if any(p not in EXPOSABLE_PILLARS for p in visible) \
            or len(set(visible)) != len(visible):
        raise ValueError('Commander visibility must be year/month/hour only')

    result = {
        'variant': PATTERN_VARIANT,
        'determination_variant': REN_YIN_TRUE_VARIANT,
        'rule': {
            'id': 'renshi.zhenge_definition',
            'source_id': REN_YIN_RULE_SOURCE_ID,
            'source_section_id': 'bazi.section.s053',
            'layer': '原注',
            'quote_locator': {'char_start': 31580, 'char_end': 31617},
        },
        'procedure_rule': {
            'id': 'renshi.siling_true_false_procedure',
            'source_id': REN_YIN_RULE_SOURCE_ID,
            'source_section_id': 'bazi.section.s054',
            'layer': '任氏曰',
            'quote_locator': {'char_start': 31681, 'char_end': 31773},
        },
        'status': 'abstained',
        'decision_step': None,
        'abstention_reason': None,
        'determination_scope': 'ren_branch_yin_month_true_pattern_only',
        'day_stem': day_stem,
        'month_branch': month_branch,
        'route': route,
        'pilot': {'variant': REN_YIN_PILOT_VARIANT, 'status': pilot_status,
                  'reason': pilot_reason, 'commander': pilot_commander},
        'commander': None,
        'determination': {'status': 'unresolved', 'pattern': None,
                          'true_false': 'abstained', 'success_failure': None,
                          'purity': None, 'useful_god': None},
        'unreviewed': dict(REN_YIN_UNREVIEWED),
        'qualified_for_determination': False,
        'research_only': True, 'public_enabled': False, 'ai_enabled': False,
        'evidence_binding': 'pending_phase1_rule_registration',
        'adjudication_notes': list(REN_YIN_ADJUDICATION_NOTES),
        'scope_limits': list(REN_YIN_LIMITATIONS),
        'scope': ('只裁定任氏（滴天髓阐微）分支、寅月、真格成立与否：司令之神'
                  '透于年/月/时干（日干不计）则真格成立，司令不透则无真格'
                  '（commander_not_visible）；不输出假格、破格、成败、清浊、'
                  '用神或吉凶，不外推其他月份与流派。'),
    }

    def abstain(step, reason):
        result['decision_step'] = step
        result['abstention_reason'] = reason
        return result

    # Step 1: month domain gate — the pilot and this block cover 寅 only.
    if month_branch != '寅':
        return abstain(1, 'month_not_yin')
    # Step 2: Slice A route precedence (adjudication A1/D3): a 禄刃 month
    # closes the month-pattern route before the commander step is reached.
    if route == 'luren_no_month_pattern':
        return abstain(2, 'luren_route_precedence')
    # Step 3: the pilot must be present, verifiable and computed.
    if pilot_status is None:
        return abstain(3, 'pilot_result_unverifiable')
    if pilot_status != 'computed':
        return abstain(3, 'pilot_not_computed')
    # Step 4: commander visibility against executed facts.
    if pilot_commander not in hidden:
        return abstain(4, 'commander_not_month_hidden')
    result['commander'] = {
        'stem': pilot_commander,
        'ten_god': commander_ten_god,
        'visible_pillars': visible,
        'day_stem_counts_as_exposure': False,
    }
    result['decision_step'] = 4
    if not visible:
        result['status'] = 'determined'
        result['determination'] = {
            'status': 'determined', 'pattern': None,
            'true_false': 'commander_not_visible', 'success_failure': None,
            'purity': None, 'useful_god': None}
        return result
    if commander_ten_god not in ('正官', '七杀', '正财', '偏财', '正印',
                                 '偏印', '食神', '伤官', '比肩', '劫财'):
        raise ValueError('Commander ten-god fact is missing or invalid')
    result['status'] = 'determined'
    result['determination'] = {
        'status': 'determined', 'pattern': commander_ten_god + '格',
        'true_false': 'true', 'success_failure': None,
        'purity': None, 'useful_god': None}
    return result


class _TraceView:
    """Minimal steps/evidence view over a live trace or a chart envelope."""

    def __init__(self, steps, evidence):
        self.steps = steps
        self.evidence = evidence


def _ren_yin_trace_view(trace):
    if hasattr(trace, 'steps') and hasattr(trace, 'evidence'):
        return trace
    if isinstance(trace, dict) and 'trace' in trace and 'evidence' in trace:
        return _TraceView(trace['trace'], trace['evidence'])
    raise ValueError('Ren yin determination requires an executed trace')


def ren_yin_true_pattern(trace, pilot_result):
    """Compose the Ren-branch 寅月 true-pattern block from executed facts.

    ``trace`` is an executed bazi trace (live ExecutionTrace or the
    chart() envelope mapping); ``pilot_result`` is the explicit
    Slice C pilot block for the same birth instant. Executed-fact
    inconsistencies raise ValueError (house fail-closed discipline,
    mirroring month_pattern_zaqi); pilot-side problems abstain.
    """
    view = _ren_yin_trace_view(trace)
    steps = {row['rule_id']: (i, row) for i, row in enumerate(view.steps)}
    required = ('pillars', 'ten_gods', 'hidden_stems', 'hidden_to_visible')
    if any('bazi.phase2.' + name not in steps for name in required):
        raise ValueError('Ren yin determination requires executed structural facts')
    for name in required:
        step = steps['bazi.phase2.' + name][1]
        if not step['evidence_ids'] or any(e not in view.evidence for e in step['evidence_ids']):
            raise ValueError('Ren yin determination lacks executed evidence')
    route_block = month_pattern_route(view)

    def fact_ref(name, suffix=''):
        return f"#/trace/{steps['bazi.phase2.' + name][0]}/output" + suffix

    pillars = steps['bazi.phase2.pillars'][1]['output']
    visible = steps['bazi.phase2.ten_gods'][1]['output']
    hidden = steps['bazi.phase2.hidden_stems'][1]['output']
    visibility = steps['bazi.phase2.hidden_to_visible'][1]['output']
    day_stem = pillars['day_master']['stem']
    month_branch = pillars['ganzhi'][1][1]
    mi, month_row = next((i, row) for i, row in enumerate(hidden)
                         if row['pillar'] == 'month')
    if month_row['branch'] != month_branch:
        raise ValueError('Ren yin determination evidence is inconsistent')
    month_hidden = [row['stem'] for row in month_row['hidden_stems']]
    hidden_ten_god = {row['stem']: row['ten_god']
                      for row in month_row['hidden_stems']}

    pilot_status, pilot_reason, pilot_commander = _ren_yin_pilot_claim(
        pilot_result)
    commander_ten_god = None
    commander_visible = []
    if pilot_status == 'computed' and pilot_commander in hidden_ten_god:
        commander_ten_god = hidden_ten_god[pilot_commander]
        # Cross-check the two independent executed visibility facts:
        # the raw ten-god stems (day pillar excluded, adjudication D2)
        # and the month hidden_to_visible positions must agree.
        from_stems = [row['pillar'] for row in visible
                      if row['pillar'] in EXPOSABLE_PILLARS
                      and row['stem'] == pilot_commander]
        for row in visible:
            if row['stem'] == pilot_commander \
                    and row['pillar'] in EXPOSABLE_PILLARS \
                    and row['ten_god'] != commander_ten_god:
                raise ValueError('Executed ten-god facts disagree on the commander')
        position = next((p for p in visibility['positions']
                         if p['hidden_pillar'] == 'month'
                         and p['hidden_stem'] == pilot_commander), None)
        from_positions = [] if position is None else [
            p for p in position['visible_pillars'] if p in EXPOSABLE_PILLARS]
        if set(from_positions) != set(from_stems):
            raise ValueError('Executed visibility and ten-god facts disagree')
        commander_visible = [p for p in EXPOSABLE_PILLARS
                             if p in set(from_stems)]

    result = ren_yin_true_false_lookup(
        day_stem, month_branch, route=route_block['route'],
        pilot_status=pilot_status, pilot_reason=pilot_reason,
        pilot_commander=pilot_commander, month_hidden_stems=month_hidden,
        commander_ten_god=commander_ten_god,
        commander_visible_pillars=commander_visible)
    if isinstance(pilot_result, dict) and isinstance(
            pilot_result.get('segment'), dict):
        segment = pilot_result['segment']
        result['pilot']['segment'] = {
            'index': segment.get('index'), 'stem': segment.get('stem'),
            'registered_interval': segment.get('registered_interval'),
        }
    result['fact_refs'] = {
        'day_master': fact_ref('pillars', '/day_master/stem'),
        'month_branch': fact_ref('pillars', '/ganzhi/1'),
        'month_hidden_stems': fact_ref('hidden_stems', f'/{mi}/hidden_stems'),
        'hidden_to_visible': fact_ref('hidden_to_visible', '/positions'),
        'route': '#/result/pattern_route',
    }
    result['consumed_rule_ids'] = ['bazi.phase2.' + name for name in required]
    return result
