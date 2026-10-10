"""Bounded evidence rules and legacy abstention; no source-case lookup predictions."""

from .bazi_core import VARIANT as BAZI_VARIANT
from .bazi_root_conditions import STRENGTH_VARIANT, AVAILABILITY_VARIANT, root_availability
from .bazi_commander import PRINCIPAL_VARIANT, principal_month
from .bazi_action_conditions import EFFECT_VARIANT

ADJUDICATION_VARIANT = 'bazi-strength-adjudication-v1'


def _bounded_assessment(trace):
    # Check trace identity and uniqueness before indexing executed evidence.
    # A repeated rule ID would otherwise silently overwrite an earlier
    # observation, even if both rows carried individually valid citations.
    if trace.domain != 'bazi' or trace.variant != BAZI_VARIANT:
        raise ValueError('Bounded strength requires the Bazi execution variant')
    rule_ids = [step['rule_id'] for step in trace.steps]
    if len(set(rule_ids)) != len(rule_ids):
        raise ValueError('Duplicate rule ID in bounded strength trace')
    steps = {s['rule_id']: (i, s) for i, s in enumerate(trace.steps)}
    keys = ('principal_month', 'root_availability', 'action_effects')
    # A research verdict also requires its upstream observed facts. Evidence IDs
    # alone cannot prove that outputs belong to the same executed chart.
    required = keys + ('pillars', 'month_command_variant', 'root_conditions',
                       'action_conditions')
    if any('bazi.phase2.' + key not in steps for key in required):
        raise ValueError('Bounded strength requires executed principal, availability and effect rules')
    for _, step in steps.values():
        if not step['evidence_ids'] or any(e not in trace.evidence for e in step['evidence_ids']):
            raise ValueError('Strength factors lack executed evidence')
    blockers, checks = [], []

    def pointer(key, suffix=''):
        return f"#/trace/{steps['bazi.phase2.' + key][0]}/output" + suffix

    def block(key, suffix, reason, conflicts=()):
        step = steps['bazi.phase2.' + key][1]
        blockers.append({'reason': reason, 'fact_ref': pointer(key, suffix),
            'rule_id': step['rule_id'], 'variant': ADJUDICATION_VARIANT,
            'status': 'unresolved', 'evidence_ids': list(step['evidence_ids']),
            'evidence_id': step['evidence_ids'][0], 'conflict_ids': list(conflicts)})

    command = steps['bazi.phase2.principal_month'][1]['output']
    roots = steps['bazi.phase2.root_availability'][1]['output']
    effects = steps['bazi.phase2.action_effects'][1]['output']
    # Fail closed when a downstream factor contradicts its actual upstream
    # source. This checks computation identity, NOT a new classical school,
    # strength threshold, effective root weight, or useful-god selection.
    pillar_facts = steps['bazi.phase2.pillars'][1]['output']
    command_facts = steps['bazi.phase2.month_command_variant'][1]['output']
    root_facts = steps['bazi.phase2.root_conditions'][1]['output']
    action_facts = steps['bazi.phase2.action_conditions'][1]['output']
    day_master = pillar_facts['day_master']['stem']
    month_branch = pillar_facts['ganzhi'][1][1]
    for key, facts in (
        ('month_command_variant', command_facts),
        ('principal_month', command),
        ('root_conditions', root_facts),
        ('root_availability', roots),
        ('action_conditions', action_facts),
        ('action_effects', effects),
    ):
        if facts.get('day_master') != day_master:
            block(key, '/day_master', 'factor_chain_inconsistent')
    if command_facts.get('month_branch') != month_branch:
        block('month_command_variant', '/month_branch', 'factor_chain_inconsistent')
    if (command.get('month_branch') != month_branch or
            command.get('principal_qi') != command_facts.get('principal_qi')):
        block('principal_month', '/month_branch', 'factor_chain_inconsistent')
    if roots.get('root_presence') != root_facts.get('present_structurally'):
        block('root_availability', '/root_presence', 'factor_chain_inconsistent')
    if len(roots['roots']) != len(root_facts['roots']):
        block('root_availability', '/roots', 'factor_chain_inconsistent')
    else:
        for i, (raw, reviewed) in enumerate(zip(root_facts['roots'], roots['roots'])):
            if reviewed.get('root_index') != i or reviewed.get('root_presence') != raw.get('fact'):
                block('root_availability', f'/roots/{i}', 'factor_chain_inconsistent')
    for kind in ('visible', 'hidden'):
        observed = action_facts[kind + '_relations']
        adjudicated = effects[kind + '_relations']
        if len(observed) != len(adjudicated):
            block('action_effects', '/' + kind + '_relations', 'factor_chain_inconsistent')
        else:
            for i, (raw, reviewed) in enumerate(zip(observed, adjudicated)):
                if (reviewed.get('action_index') != i or
                        reviewed.get('fact') != raw.get('fact')):
                    block('action_effects',
                          f'/{kind}_relations/{i}', 'factor_chain_inconsistent')
    # Reconstruct both reviewed derived factors directly from their actual
    # upstream facts, not merely by comparing a subset of output fields.
    # Forged "effective" roots or a forged month relation otherwise preserve
    # the evidence IDs and might incorrectly satisfy a sufficient predicate.
    if command != principal_month(command_facts, day_master):
        block('principal_month', '/status', 'derived_principal_replay_mismatch')
    if roots != root_availability(root_facts):
        block('root_availability', '/root_presence',
              'derived_root_availability_replay_mismatch')
    for key, field, expected in [('principal_month','command_variant',PRINCIPAL_VARIANT),
                                 ('root_availability','root_variant',AVAILABILITY_VARIANT),
                                 ('action_effects','action_variant',EFFECT_VARIANT)]:
        if steps['bazi.phase2.' + key][1]['output'][field] != expected:
            block(key, '/' + field, 'factor_variant_mismatch')
    for cid in command['dated_source_conflicts']:
        checks.append({'conflict_id':cid,'status':'unresolved','blocking':False,
                       'reason':'dated_commander_not_a_dependency',
                       'fact_ref':pointer('principal_month','/dated_source_conflicts'),
                       'evidence_ids':list(steps['bazi.phase2.month_command_variant'][1]['evidence_ids'])})
    checks.append({'conflict_id':'bazi.concept.conflict_three_punishments',
                   'status':'unresolved','blocking':False,
                   'reason':'not_applied_in_explicit_ren_school',
                   'fact_ref':pointer('root_availability'),
                   'evidence_ids':list(steps['bazi.phase2.root_availability'][1]['evidence_ids'])})
    for i, root in enumerate(roots['roots']):
        if root['type_source_conflict']:
            cid=root['type_source_conflict']
            checks.append({'conflict_id':cid,'status':'unresolved','blocking':True,
                           'reason':'root_type_source_conflict',
                           'fact_ref':pointer('root_availability',f'/roots/{i}/type_source_conflict'),
                           'evidence_ids':list(steps['bazi.phase2.root_availability'][1]['evidence_ids'])})
            block('root_availability',f'/roots/{i}/type_source_conflict','root_type_source_conflict',[cid])
        if root['root_availability'] != 'effective':
            block('root_availability',f'/roots/{i}/root_availability','root_availability_not_effective')
    if command['status'] != 'reviewed_relation':
        block('principal_month','/status','principal_qi_not_reviewed')
    if effects['unresolved_interaction_kinds']:
        block('action_effects','/unresolved_interaction_kinds','interaction_effect_unresolved')

    # Sufficient predicates are conjunctions, not votes or count thresholds.
    pure = (effects['pure_support_scope_met']
        and all(effects['pure_support_scope_conditions'].values())
        and command['month_branch'] == '卯' and command['relation'] == 'same_element'
        and roots['root_presence']
        and all(r['root_availability'] == 'effective' for r in roots['roots'])
        and all(r['effect_status'] == 'effective_in_reviewed_context' for r in effects['visible_relations']))
    isolated = (effects['isolated_control_scope_met']
        and all(effects['isolated_control_scope_conditions'].values())
        and command['month_branch'] == '酉' and command['relation'] == 'controls_me'
        and not roots['root_presence']
        and any(r['fact']['pillar'] == 'month' and r['effective_action'] == 'controls_me'
                and r['effect_status'] == 'effective_in_reviewed_context' for r in effects['visible_relations']))
    classification, why, conditions = 'indeterminate', None, []
    if not blockers and (pure or isolated):
        classification = 'strong' if pure else 'weak'
        predicate = 'pure_support' if pure else 'isolated_control'
        rule_id = 'bazi.phase2.strength_' + predicate
        for key, met in effects[predicate + '_scope_conditions'].items():
            conditions.append({'condition':key,'met':met,
                'fact_ref':pointer('action_effects','/' + predicate + '_scope_conditions/' + key),
                'rule_id':'bazi.phase2.action_effects',
                'evidence_ids':list(steps['bazi.phase2.action_effects'][1]['evidence_ids'])})
        trace.add(rule_id, {'strength_variant':ADJUDICATION_VARIANT,
                  'factor_refs':[pointer(k) for k in keys]},
                  {'classification':classification,'variant':ADJUDICATION_VARIANT,'conditions':conditions})
        why = {'sufficient_rule':rule_id,'conditions':conditions,
               'all_required_conditions_verified':True,
               'excluded_dependencies':['dated_commander','independent_hidden_effect_scores']}
    else:
        block('action_effects','/pure_support_scope_conditions','outside_reviewed_sufficient_conditions')
    relevant = {'bazi.phase2.' + k for k in ('pillars','hidden_stems','support_relations',
        'stem_five_combinations','branch_six_harmonies','branch_six_harms','branch_six_clashes',
        'branch_triple_harmonies','month_command_variant','principal_month','root_conditions','root_availability',
        'action_conditions','action_effects','strength_pure_support','strength_isolated_control')}
    matched = [s['rule_id'] for s in trace.steps if s['rule_id'] in relevant]
    evidence_ids = sorted({e for s in trace.steps if s['rule_id'] in relevant for e in s['evidence_ids']}
                          | {e for c in checks for e in c['evidence_ids']})
    return {'classification':classification,'variant':ADJUDICATION_VARIANT,
        'decision_status':'reviewed_sufficient_rule_matched' if why else 'insufficient_reviewed_rules',
        'matched_rule_ids':matched,'fact_refs':[f'#/trace/{i}/output' for i,s in enumerate(trace.steps) if s['rule_id'] in relevant],
        'evidence_ids':evidence_ids,'source_ids':sorted({trace.evidence[e]['source_id'] for e in evidence_ids}),
        'conflict_checks':checks,'conflict_ids':sorted({c['conflict_id'] for c in checks if c['blocking']}),
        'blockers':blockers,'unresolved_evidence':sorted({e for b in blockers for e in b['evidence_ids']}),
        'why_not_indeterminate':why,'supported_classifications':['strong','weak','indeterminate'],
        'variant_dependencies':{'dated_commander':False,'principal_qi':True,
            'root_availability':True,'bounded_visible_effects':True,'independent_hidden_effect_scores':False},
        'maturity':'PARTIAL','research_only':True,'public_enabled':False,'ai_enabled':False,
        'weights_available':False,'source_case_lookup_used':False,'full_strength_classifier_ready':False,
        'limitations':['仅显式任氏木日主：纯印比月卯，或无根无扶透辛月酉；其余未裁定。',
            '来源仍为 C 级单一电子版本，未宣称独立底本一致；强不等于吉，弱不等于凶。',
            '不处理 balanced、数字力度、从格、喜用、行运，暗合、半合拱夹与其他学派刑法不在范围。',
            '分日冲突与其他学派刑法仍 unresolved，但不是此明确 Variant 的依赖；不自动开放产品或 AI。']}


def strength_assessment(trace, *, strength_variant=STRENGTH_VARIANT):
    if strength_variant == ADJUDICATION_VARIANT:
        return _bounded_assessment(trace)
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
