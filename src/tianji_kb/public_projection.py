"""Public product projections: facts stay visible; internal evidence and traces do not.

Build response fields by allowlist. Never mutate the audited engine payload.
"""
import copy

PUBLIC_EXECUTION_DOMAINS = frozenset({'bazi', 'liuyao'})
PUBLIC_SCENARIO_STATES = frozenset({'production', 'production_limited'})


def project_evidence(evidence):
    output = {}
    for evidence_id, ref in evidence.items():
        quote = str(ref.get('original_text') or '')[:120]
        output[evidence_id] = {
            'classic_title': str(ref.get('classic_title') or ''),
            'original_text': quote,
            'evidence_level': str(ref.get('evidence_level') or ''),
        }
    return output


def project_execution(data):
    result = copy.deepcopy(data)
    result['evidence'] = project_evidence(data['evidence'])
    result['rule_matches'] = [
        {key: copy.deepcopy(row[key]) for key in ('rule_id','matched','kind','evidence_scope','evidence_ids')
         if key in row}
        for row in data['rule_matches']
    ]
    result['trace'] = [
        {'step': str(row.get('step') or row.get('rule_id') or 'calculation')}
        for row in data['trace']
    ]
    return result
