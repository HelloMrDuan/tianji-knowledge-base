"""Public response boundary: preserve chart facts without internal knowledge IDs.

Identifiers in this projection are response-local display ordinals, not hashes,
persistent database keys, or stable pointers into the private knowledge graph.
"""
import copy

PUBLIC_EXECUTION_DOMAINS = frozenset({'bazi', 'liuyao'})
PUBLIC_SCENARIO_STATES = frozenset({'production', 'production_limited'})

_PRIVATE_KEYS = frozenset({
    'canonical_path', 'canonical_paths', 'source_path', 'source_paths',
    'content_path', 'file_path', 'repository', 'repository_url', 'repo_url',
    'commit', 'commit_sha', 'sha256', 'manifest', 'source_refs', 'source_ref',
    'source_url', 'retrieval', 'retrieved_chunks', 'raw_evidence',
})
_RULE_KEYS = frozenset({'rule_id', 'derived_from_rule_id', 'gate_rule_id'})
_RULE_LIST_KEYS = frozenset({'rule_ids', 'derived_from_rule_ids', 'execution_rule_ids'})
_EVIDENCE_LIST_KEYS = frozenset({'evidence_ids'})


class _Aliases:
    def __init__(self, evidence):
        self.evidence = {str(key): f'E{index:02d}' for index, key in enumerate(evidence, 1)}
        self.rules = {}

    def rule(self, value):
        if not isinstance(value, str):
            return None
        if value not in self.rules:
            self.rules[value] = f'R{len(self.rules) + 1:02d}'
        return self.rules[value]

    def evidence_id(self, value):
        # Unbound evidence IDs must not reach a public JSON response.
        return self.evidence.get(str(value))


def _public_facts(value, aliases):
    """Recursively remove private provenance without changing calculated facts."""
    if isinstance(value, list):
        return [_public_facts(item, aliases) for item in value]
    if isinstance(value, dict):
        output = {}
        for key, item in value.items():
            if key in _PRIVATE_KEYS:
                continue
            if key in _RULE_KEYS:
                output[key] = aliases.rule(item)
            elif key in _RULE_LIST_KEYS and isinstance(item, list):
                output[key] = [aliases.rule(x) for x in item if isinstance(x, str)]
            elif key in _EVIDENCE_LIST_KEYS and isinstance(item, list):
                output[key] = [aliases.evidence_id(x) for x in item
                               if aliases.evidence_id(x) is not None]
            else:
                output[key] = _public_facts(item, aliases)
        return output
    return copy.deepcopy(value)


def project_evidence(evidence, aliases):
    output = {}
    for original_id, ref in evidence.items():
        public_id = aliases.evidence_id(original_id)
        output[public_id] = {
            'classic_title': str(ref.get('classic_title') or '')[:120],
            'original_text': str(ref.get('original_text') or '')[:120],
            'evidence_level': str(ref.get('evidence_level') or '')[:24],
        }
    return output


def project_execution(data):
    aliases = _Aliases(data['evidence'])
    result = {key: _public_facts(value, aliases)
              for key, value in data.items()
              if key not in ('evidence', 'rule_matches', 'trace')}
    result['evidence'] = project_evidence(data['evidence'], aliases)
    result['rule_matches'] = [
        _public_facts(
            {key: row[key] for key in
             ('rule_id', 'matched', 'kind', 'evidence_scope', 'evidence_ids')
             if key in row},
            aliases,
        ) for row in data['rule_matches']
    ]
    result['trace'] = [{'step': f'计算步骤 {index:02d}'}
                       for index, _ in enumerate(data['trace'], 1)]
    return result
