"""Reviewed month policies: principal qi is not a dated commander or strength."""
from .bazi_core import PILLAR_NAMES, foundations
from .resolver import EvidenceResolver
from .foundations import CONTROLS, GENERATES, stem_element

COMMAND_VARIANT = 'bazi-strength-month-command-v1'
PRINCIPAL_VARIANT = 'month-command-principal-qi-v1'
POLICY_CONCEPT = 'bazi.concept.month_command_variant_v1'


def principal_month(observed, day_master, *, command_variant=PRINCIPAL_VARIANT):
    """An independent principal-qi relation, never a resolved day commander."""
    if command_variant != PRINCIPAL_VARIANT:
        raise ValueError('Unsupported principal month variant')
    stem = observed['principal_qi']
    relation = None
    if stem is not None:
        target, reference = stem_element(stem), stem_element(day_master)
        if target == reference:
            relation = 'same_element'
        elif GENERATES[target] == reference:
            relation = 'generates_me'
        elif GENERATES[reference] == target:
            relation = 'i_generate'
        elif CONTROLS[target] == reference:
            relation = 'controls_me'
        else:
            relation = 'i_control'
    return {'command_variant': command_variant, 'month_branch': observed['month_branch'],
            'principal_qi': stem, 'principal_qi_section_ids': observed['principal_qi_section_ids'],
            'day_master': day_master, 'relation': relation,
            'status': 'reviewed_relation' if stem else 'not_reviewed',
            'dated_commander_required': False, 'commander': None, 'de_ling': None,
            'overall_strength': None, 'dated_source_conflicts': list(observed['source_conflict']),
            'scope': '任氏已审本气关系；独立于分日口径，关系不单独证明旺衰，四库本气未审。'}


MONTH_BRANCHES = ('寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥', '子', '丑')


def commander_review_matrix(*, policy=None):
    """Twelve independently scoped review states, not a day-command lookup table.

    A reviewed principal qi or absence of recorded disagreement NEVER resolves
    a dated commander. This is derived from the existing audited Concept only.
    """
    if policy is None:
        policy = EvidenceResolver().entities[POLICY_CONCEPT][1]['attributes']
    rows = []
    for branch in MONTH_BRANCHES:
        principal = policy['principal_qi'].get(branch)
        profiles = [
            {'variant': p['variant'], 'section_ids': list(p['months'][branch]['section_ids'])}
            for p in policy['commander_profiles'] if branch in p['months']
        ]
        conflicts = [c['id'] for c in policy['conflicts'] if branch in c['month_branches']]
        rows.append({
            'month_branch': branch,
            'principal_qi': principal['stem'] if principal else None,
            'principal_qi_status': 'reviewed_structural' if principal else 'not_reviewed',
            'candidate_profiles': profiles,
            'candidate_review_status': 'reviewed_candidates' if profiles else 'not_reviewed',
            'source_comparison_status': 'source_conflict' if conflicts else 'not_reviewed',
            'dated_boundary_status': 'insufficient_text' if profiles else 'not_reviewed',
            'exact_day_commander': None,
            'commander_status': 'unresolved',
            'conflict_ids': conflicts,
        })
    return rows


def month_command(pillars, day_master, *, command_variant=COMMAND_VARIANT):
    if command_variant != COMMAND_VARIANT:
        raise ValueError('Unsupported month command variant')
    if len(pillars) != 4 or tuple(p['name'] for p in pillars) != PILLAR_NAMES:
        raise ValueError('Expected ordered year/month/day/hour pillars')
    policy = EvidenceResolver().entities[POLICY_CONCEPT][1]['attributes']
    branch = pillars[1]['branch']['value']
    hidden = list(foundations()['hidden_stems'][branch])
    principal = policy['principal_qi'].get(branch)
    profiles = []
    for profile in policy['commander_profiles']:
        row = profile['months'].get(branch)
        profiles.append({'variant': profile['variant'], 'basis': profile['basis'],
                         'candidates': list(row['candidates']) if row else [],
                         'section_ids': list(row['section_ids']) if row else [],
                         'status': 'candidates_only' if row else 'not_reviewed',
                         'exact_day_commander': None})
    conflicts = [c['id'] for c in policy['conflicts'] if branch in c['month_branches']]
    dated_review = next(row for row in commander_review_matrix(policy=policy)
                        if row['month_branch'] == branch)
    return {
        'command_variant': command_variant, 'month_branch': branch,
        'hidden_stems': hidden,
        'principal_qi': principal['stem'] if principal else None,
        'principal_qi_status': 'reviewed_structural' if principal else 'not_reviewed',
        'principal_qi_section_ids': list(principal['section_ids']) if principal else [],
        'commander_candidates': profiles, 'source_conflict': conflicts,
        'source_comparison_status': 'unresolved' if conflicts else 'not_reviewed',
        'dated_review': dated_review,
        'commander': None, 'commander_status': 'unresolved',
        'determinacy': 'structural_only', 'day_master': day_master,
        'de_ling': None, 'overall_strength': None,
        'scope': '本气仅作已审核结构口径；分日/节气分别列候选，不把本气、唯一藏干或候选换成具体日司令、得令或旺衰。',
    }


def month_factor_graph(trace, observed):
    """Bind the observation to the actual trace/evidence, without extra rulings."""
    index = next(i for i, s in enumerate(trace.steps)
                 if s['rule_id'] == 'bazi.phase2.month_command_variant')
    step = trace.steps[index]
    return {'variant': observed['command_variant'], 'layer': 'FACT',
            'factors': [{'id': 'month_command', 'fact_ref': f'#/trace/{index}/output',
                         'rule_id': step['rule_id'],
                         'evidence_id': step['evidence_ids'][0],
                         'evidence_ids': list(step['evidence_ids']),
                         'variant': observed['command_variant'],
                         'status': 'structural_only',
                         'interpretation_status': 'unresolved', 'effect': None}],
            'overall_strength': 'indeterminate', 'weights_available': False,
            'maturity': 'PARTIAL', 'full_strength_classifier_ready': False}
