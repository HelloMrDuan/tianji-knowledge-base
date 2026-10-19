"""Public response boundary: preserve chart facts without internal knowledge IDs.

Identifiers in this projection are response-local display ordinals, not hashes,
persistent database keys, or stable pointers into the private knowledge graph.

TJ-011.3: Strength adjudication display policy is enforced here as the
last line of defense. Even if a research-only strength assessment somehow
reaches this layer, it will not be exposed publicly unless the variant is
in the server-side PUBLIC_STRENGTH_VARIANTS allowlist.
"""
import copy

from .bazi_strength_display import get_display_decision

PUBLIC_EXECUTION_DOMAINS = frozenset({'bazi', 'liuyao'})
PUBLIC_SCENARIO_STATES = frozenset({'production', 'production_limited'})

_PRIVATE_KEYS = frozenset({
    'canonical_path', 'canonical_paths', 'source_path', 'source_paths',
    'content_path', 'file_path', 'repository', 'repository_url', 'repo_url',
    'commit', 'commit_sha', 'sha256', 'manifest', 'source_refs', 'source_ref',
    'source_url', 'source_id', 'source_ids', 'source_file', 'source_record_id',
    'locator', 'provenance', 'archive_path', 'path', 'retrieval',
    'retrieved_chunks', 'raw_evidence', 'evidence', 'trace', 'rule_matches',
})
_RULE_KEYS = frozenset({'rule_id', 'derived_from_rule_id', 'source_rule_id', 'gate_rule_id'})
_RULE_LIST_KEYS = frozenset({'rule_ids', 'derived_from_rule_ids', 'execution_rule_ids', 'source_rule_ids'})
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


def _apply_strength_display_policy(chart):
    """Apply TJ-011.3 display policy to chart's strength assessment.
    
    This is the wiring point for bazi_strength_display.get_display_decision().
    The variant, day_master, and month_branch are extracted from the
    server-computed chart data, never from client input.
    
    If the assessment is not authorized for public display, the
    classification is removed and a display notice is added instead.
    The full assessment details (blockers, evidence) are already stripped
    by _public_facts; this ensures the verdict itself doesn't leak.
    """
    assessment = chart.get('strength_assessment')
    if not isinstance(assessment, dict):
        return
    
    # Trusted sources: variant from assessment (server-generated),
    # day_master/month_branch from computed pillars.
    variant = assessment.get('variant')
    day_master = None
    month_branch = None
    try:
        pillars = chart.get('pillars') or []
        if len(pillars) >= 3:
            # pillars[2] is day pillar, pillars[1] is month pillar
            day_pillar = pillars[2] if isinstance(pillars[2], dict) else {}
            month_pillar = pillars[1] if isinstance(pillars[1], dict) else {}
            day_stem = day_pillar.get('stem')
            month_br = month_pillar.get('branch')
            # Handle both dict and string forms
            if isinstance(day_stem, dict):
                day_master = day_stem.get('value')
            elif isinstance(day_stem, str):
                day_master = day_stem
            if isinstance(month_br, dict):
                month_branch = month_br.get('value')
            elif isinstance(month_br, str):
                month_branch = month_br
    except (IndexError, AttributeError, TypeError):
        pass
    
    decision = get_display_decision(
        assessment,
        variant=variant,
        day_master=day_master,
        month_branch=month_branch,
    )
    
    if decision['may_display_classification']:
        # Authorized: keep classification, add scope note
        assessment['display_state'] = 'public_result'
    else:
        # Not authorized: remove the verdict, keep only the display notice.
        # This prevents research conclusions from reaching public clients
        # even if the engine-level block were somehow bypassed.
        assessment.pop('classification', None)
        assessment['display_state'] = decision['display_state']
        assessment['display_message'] = decision['user_message']
        # Strip detailed internals that _public_facts might have missed
        for key in ('blockers', 'why_not_indeterminate', 'conflict_ids',
                    'unresolved_evidence', 'supported_classifications'):
            assessment.pop(key, None)


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
    # TJ-011.3: enforce strength display policy on the public chart.
    chart = result.get('chart')
    if isinstance(chart, dict):
        _apply_strength_display_policy(chart)
    return result
