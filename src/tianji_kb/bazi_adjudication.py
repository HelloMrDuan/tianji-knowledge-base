"""Evidence-bound abstention gate; source case verdicts are never lookup predictions."""

from .bazi_root_conditions import STRENGTH_VARIANT


def strength_assessment(trace, *, strength_variant=STRENGTH_VARIANT):
    if strength_variant != STRENGTH_VARIANT:
        raise ValueError('Unsupported strength adjudication variant')
    steps = {s['rule_id']: (i, s) for i, s in enumerate(trace.steps)}
    required = ('month_command_variant', 'root_conditions', 'action_conditions')
    if any('bazi.phase2.' + key not in steps for key in required):
        raise ValueError('Strength adjudication requires executed conditional factors')
    blockers = []

    def add(key, suffix, reason, conflicts=()):
        i, step = steps['bazi.phase2.' + key]
        output = step['output']
        blockers.append({'reason': reason, 'fact_ref': f'#/trace/{i}/output' + suffix,
                         'rule_id': step['rule_id'], 'evidence_id': step['evidence_ids'][0],
                         'evidence_ids': list(step['evidence_ids']),
                         'variant': output.get('command_variant', output.get('root_variant',
                                                output.get('action_variant'))),
                         'status': 'unresolved', 'conflict_ids': list(conflicts)})

    command = steps['bazi.phase2.month_command_variant'][1]['output']
    add('month_command_variant', '/commander_status', 'dated_commander_unresolved',
        command['source_conflict'])
    if command['principal_qi_status'] == 'not_reviewed':
        add('month_command_variant', '/principal_qi_status', 'principal_qi_not_reviewed')
    roots = steps['bazi.phase2.root_conditions'][1]['output']['roots']
    for j, root in enumerate(roots):
        add('root_conditions', f'/roots/{j}/availability_status', 'root_availability_unresolved')
        if root['type_source_conflict']:
            add('root_conditions', f'/roots/{j}/type_source_conflict',
                'root_type_source_conflict', [root['type_source_conflict']])
        if root['conditions']['branch_relations']:
            add('root_conditions', f'/roots/{j}/conditions/branch_relations',
                'root_interaction_effect_unresolved')
    actions = steps['bazi.phase2.action_conditions'][1]['output']
    for visibility in ('visible', 'hidden'):
        for j, _ in enumerate(actions[visibility + '_relations']):
            add('action_conditions', f'/{visibility}_relations/{j}/effect_status',
                visibility + '_action_effect_unresolved')
    return {'variant': strength_variant, 'classification': 'indeterminate',
            'decision_status': 'insufficient_reviewed_rules',
            'blockers': blockers, 'supported_classifications': [],
            'weights_available': False, 'maturity': 'PARTIAL',
            'full_strength_classifier_ready': False,
            'source_case_lookup_used': False, 'ai_enabled': False,
            'scope': '真实执行条件的判定出口；尚无可复算的通用强弱或平衡 Rule。'
                     '古例裁语仅供独立复核，不能查表当作算法预测。'}
