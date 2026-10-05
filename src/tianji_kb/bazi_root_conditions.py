"""Conditional root observations: structure survives unresolved interaction effects."""
from .bazi_core import PILLAR_NAMES, foundations
from .foundations import stem_element
from .resolver import EvidenceResolver

STRENGTH_VARIANT = 'bazi-strength-conditions-v1'
ROOT_VARIANT = 'ditiansui-root-conditions-v1'
AVAILABILITY_VARIANT = 'ditiansui-wood-root-availability-v1'


def root_availability(observed, *, root_variant=AVAILABILITY_VARIANT):
    """Qualitative participation of reviewed wood roots in the selected school."""
    if root_variant != AVAILABILITY_VARIANT:
        raise ValueError('Unsupported root availability variant')
    policy = EvidenceResolver().entities['bazi.concept.root_availability_v1'][1]['attributes']
    rows = []
    for index, root in enumerate(observed['roots']):
        fact = root['fact']
        reviewed = observed['element'] == policy['element'] and fact['branch'] in policy['branches']
        reasons = []
        if not reviewed:
            reasons.append('root_type_not_in_reviewed_scope')
        if root['type_source_conflict']:
            reasons.append('root_type_source_conflict')
        if root['conditions']['branch_relations']:
            reasons.append('branch_interaction_effect_unresolved')
        status = 'effective' if not reasons else ('conditional' if reviewed or root['type_source_conflict'] else 'unresolved')
        rows.append({'root_index': index, 'root_presence': dict(fact),
                     'root_availability': status,
                     'root_effect': 'same_element_support' if status == 'effective' else None,
                     'availability_status': status, 'effective_strength': None,
                     'same_stem': fact['same_stem'], 'polarity_equivalence_assumed': False,
                     'blockers': reasons,
                     'branch_relations': root['conditions']['branch_relations'],
                     'type_source_conflict': root['type_source_conflict'],
                     'punishment_policy': 'not_applied_in_selected_ren_school',
                     'reported_school_conflicts': ['bazi.concept.conflict_three_punishments']})
    return {'root_variant': root_variant, 'day_master': observed['day_master'],
            'roots': rows, 'root_presence': observed['present_structurally'],
            'root_effect': None, 'root_erasure_applied': False, 'weights_available': False,
            'position_weights_available': False, 'overall_strength': None,
            'scope': '仅木根亥寅卯、无未解冲合害条件的定性可用性；刑依显式任氏口径不机械消根，跨流派争议仍未解；无根不等于弱。'}


def root_conditions(pillars, day_master, *, relations, month_command,
                    root_variant=ROOT_VARIANT):
    if root_variant != ROOT_VARIANT:
        raise ValueError('Unsupported conditional root variant')
    if len(pillars) != 4 or tuple(p['name'] for p in pillars) != PILLAR_NAMES:
        raise ValueError('Expected ordered year/month/day/hour pillars')
    policy = EvidenceResolver().entities['bazi.concept.root_conditions_variant_v1'][1]['attributes']
    element = stem_element(day_master)
    roots = []
    for i, pillar in enumerate(pillars):
        branch = pillar['branch']['value']
        for hidden in foundations()['hidden_stems'][branch]:
            if stem_element(hidden) != element:
                continue
            principal = policy['principal_qi'].get(branch)
            exposures = [p['name'] for p in pillars if p['name'] != 'day'
                         and p['stem']['value'] == hidden]
            kinds = []
            for item in policy['reviewed_type_candidates']:
                if element == item['element'] and branch in item['branches']:
                    kinds.append({'kind': item['kind'], 'section_ids': item['section_ids'],
                                  'status': 'candidate_only'})
            interactions = [{'kind': key, **row} for key in (
                'branch_six_clashes', 'branch_six_harmonies',
                'branch_six_harms', 'branch_triple_harmonies')
                for row in relations[key] if pillar['name'] in row['pillars']]
            roots.append({
                'fact': {'pillar': PILLAR_NAMES[i], 'branch': branch, 'hidden_stem': hidden,
                         'same_stem': hidden == day_master, 'present_structurally': True,
                         'is_month_position': i == 1, 'tomb_branch': branch in policy['tomb_branches'],
                         'principal_qi_match': hidden == principal['stem'] if principal else None,
                         'exposed_visible_pillars': exposures},
                'interpretation_candidates': kinds,
                'type_source_conflict': policy['type_conflict'] if any(
                    k['kind'] == 'residual_qi_candidate' for k in kinds) else None,
                'conditions': {'branch_relations': interactions,
                               'month_commander_status': month_command['commander_status'],
                               'branch_relation_effect': 'unresolved',
                               'punishment_status': 'unresolved',
                               'punishment_conflict': 'bazi.concept.conflict_three_punishments',
                               'position_effect': 'unresolved'},
                'availability_status': 'unresolved', 'effective_strength': None,
            })
    return {'root_variant': root_variant, 'day_master': day_master, 'element': element,
            'roots': roots, 'present_structurally': bool(roots),
            'root_erasure_applied': False, 'weights_available': False,
            'overall_strength': None,
            'scope': '结构根、原典类型候选与作用条件分层；冲合害不自动消根或成化，刑未裁定；柱位不赋权重。'}


def conditional_factor_graph(trace):
    factors = []
    keys = ('month_command_variant', 'root_conditions', 'action_conditions')
    for i, step in enumerate(trace.steps):
        key = step['rule_id'].removeprefix('bazi.phase2.')
        if key not in keys:
            continue
        factors.append({'id': key, 'fact_ref': f'#/trace/{i}/output',
                        'rule_id': step['rule_id'],
                        'evidence_id': step['evidence_ids'][0],
                        'evidence_ids': list(step['evidence_ids']),
                        'variant': step['output'].get('command_variant', step['output'].get('root_variant', step['output'].get('action_variant'))),
                        'status': 'structural_and_conditional',
                        'interpretation_status': 'unresolved', 'effect': None})
    edges = []
    for i, step in enumerate(trace.steps):
        if step['rule_id'] != 'bazi.phase2.action_conditions':
            continue
        for visibility in ('visible', 'hidden'):
            for j, row in enumerate(step['output'][visibility + '_relations']):
                fact = row['fact']
                position = visibility + ':' + fact['pillar'] + ':' + fact['stem']
                outward = fact['relation'] in ('i_generate', 'i_control')
                edges.append({'from': 'day_master' if outward else position,
                              'to': position if outward else 'day_master', 'relation': fact['relation'],
                              'visibility': visibility,
                              'fact_ref': f'#/trace/{i}/output/{visibility}_relations/{j}/fact',
                              'rule_id': step['rule_id'], 'evidence_id': step['evidence_ids'][0],
                              'evidence_ids': list(step['evidence_ids']),
                              'variant': step['output']['action_variant'],
                              'status': 'direction_only', 'effect': None})
    return {'variant': STRENGTH_VARIANT, 'factors': factors, 'edges': edges,
            'overall_strength': 'indeterminate', 'weights_available': False,
            'maturity': 'PARTIAL', 'full_strength_classifier_ready': False}
