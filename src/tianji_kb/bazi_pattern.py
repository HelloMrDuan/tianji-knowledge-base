"""Research observations from executed month/ten-god/visibility facts, never 定格."""

PATTERN_VARIANT = 'bazi-pattern-structure-candidates-v1'


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
    return {'variant': pattern_variant, 'family': family,
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
