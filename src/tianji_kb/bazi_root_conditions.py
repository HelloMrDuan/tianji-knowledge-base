"""Conditional root observations: structure survives unresolved interaction effects."""
from .bazi_core import PILLAR_NAMES, foundations
from .foundations import stem_element
from .resolver import EvidenceResolver

STRENGTH_VARIANT = 'bazi-strength-conditions-v1'
ROOT_VARIANT = 'ditiansui-root-conditions-v1'


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
