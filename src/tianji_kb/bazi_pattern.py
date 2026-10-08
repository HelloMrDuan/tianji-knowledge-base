"""Research observations from executed month/ten-god/visibility facts, never 定格."""

from .foundations import CONTROLS, GENERATES, stem_element

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
    return {
        'variant': PATTERN_VARIANT, 'school_branch': 'yuanhai-甲辛-酉月不透地支官局例',
        'status': 'reviewed_structural_candidate' if all(c['observed'] for c in conditions)
                  else 'not_observed',
        'conditions': conditions, 'full_metal_group': list(match[1]['branches']) if complete else [],
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
                # These blocks are evidence-scoped missing prerequisites, not
                # negative judgments about the strength or activation of a stem.
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
    provenance = sorted(set(steps['bazi.phase2.ten_gods'][1]['evidence_ids'])
                        | set(steps['bazi.phase2.hidden_stems'][1]['evidence_ids']))
    causal = resource_elemental_causal_gate({
        'positions': groups, 'observed_interactions': interactions,
        'evidence_ids': provenance, 'exact_stem_sites': exact_stem_sites,
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
