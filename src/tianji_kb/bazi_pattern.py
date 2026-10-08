"""Research observations from executed month/ten-god/visibility facts, never 定格."""

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
    result['qualification'] = qualification(trace, family=family, observation=result)
    return result
