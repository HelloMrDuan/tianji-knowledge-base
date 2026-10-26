"""Public response boundary: preserve chart facts without internal knowledge IDs.

Identifiers in this projection are response-local display ordinals, not hashes,
persistent database keys, or stable pointers into the private knowledge graph.

TJ-011.3: Strength adjudication display policy is enforced here as the
last line of defense. Even if a research-only strength assessment somehow
reaches this layer, it will not be exposed publicly unless the variant is
in the server-side PUBLIC_STRENGTH_VARIANTS allowlist.
"""
import copy
from datetime import datetime
from zoneinfo import ZoneInfo

from .bazi_strength_display import get_display_decision

# B014: ziwei/qimen/fengshui join the public execution gate (connection only;
# engines already exist with real tests). Out-of-scope tools stay out.
PUBLIC_EXECUTION_DOMAINS = frozenset({'bazi', 'liuyao', 'yijing', 'liuren',
                                      'ziwei', 'qimen', 'fengshui'})
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
        title = str(ref.get('classic_title') or '')
        text = str(ref.get('original_text') or '')
        output[public_id] = {
            'classic_title': title[:120],
            'original_text': text[:120],
            'evidence_level': str(ref.get('evidence_level') or '')[:24],
            # TJ-031.5 (Track C LOW-1): the 120-char cap above is a
            # public-boundary size limit, not the complete citation.
            # Flag every truncated field explicitly so a projected
            # excerpt is never presented as the full original text.
            'classic_title_excerpt': len(title) > 120,
            'original_text_excerpt': len(text) > 120,
        }
    return output


# TJ-031.5 (Track C LOW-3): the liuyao 'judgment' field carries the
# verbatim Zhouyi hexagram text from the reviewed classic corpus, not
# an adjudicated verdict about the querent. The field name is kept
# (the public page and existing consumers read it), and its scope is
# stated explicitly beside it in the public projection.
_LIUYAO_JUDGMENT_SCOPE = 'verbatim_classical_hexagram_text_not_a_verdict'


def _annotate_judgment_scope(node):
    if isinstance(node, dict):
        classic = node.get('zhouyi_classic')
        if isinstance(classic, dict):
            for part in ('original', 'changed'):
                entry = classic.get(part)
                if isinstance(entry, dict) and isinstance(entry.get('judgment'), str):
                    entry['judgment_scope'] = _LIUYAO_JUDGMENT_SCOPE
        for item in node.values():
            _annotate_judgment_scope(item)
    elif isinstance(node, list):
        for item in node:
            _annotate_judgment_scope(item)


def _apply_strength_display_policy(chart):
    """Apply TJ-011.3 display policy to chart's strength assessment.
    
    This is the wiring point for bazi_strength_display.get_display_decision().
    The variant, day_master, and month_branch are extracted from the
    server-computed chart data, never from client input.
    
    If the assessment is not authorized for public display, the
    classification is removed and replaced with a display state indicator.
    The full assessment details (blockers, evidence) are already stripped
    by _public_facts; this ensures the verdict itself doesn't leak.
    
    TJ-011.3 final fix: Also handles strength_factor_graph.overall_strength,
    which is a second projection path for the research conclusion
    (set in bazi_chart.py when strength_variant == ADJUDICATION_VARIANT).
    """
    from .bazi_strength_display import PUBLIC_STRENGTH_VARIANTS
    
    assessment = chart.get('strength_assessment')
    if isinstance(assessment, dict):
        _apply_policy_to_assessment(chart, assessment)
    
    # Second leak path: strength_factor_graph.overall_strength
    # Set in operations/bazi_chart.py when adjudication variant runs.
    graph = chart.get('strength_factor_graph')
    if isinstance(graph, dict):
        _apply_policy_to_factor_graph(graph)


def _apply_policy_to_assessment(chart, assessment):
    """Apply display policy to the strength_assessment dict."""
    # Trusted sources: variant from assessment (server-generated),
    # day_master/month_branch from computed pillars.
    variant = assessment.get('variant')
    day_master = None
    month_branch = None
    try:
        pillars = chart.get('pillars') or []
        if len(pillars) >= 3:
            day_pillar = pillars[2] if isinstance(pillars[2], dict) else {}
            month_pillar = pillars[1] if isinstance(pillars[1], dict) else {}
            day_stem = day_pillar.get('stem')
            month_br = month_pillar.get('branch')
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
        assessment['display_state'] = 'public_result'
    else:
        assessment.pop('classification', None)
        assessment['display_state'] = decision['display_state']
        assessment['display_message'] = decision['user_message']
        for key in ('blockers', 'why_not_indeterminate', 'conflict_ids',
                    'unresolved_evidence', 'supported_classifications',
                    'decision_status'):
            assessment.pop(key, None)


def _apply_policy_to_factor_graph(graph):
    """Apply display policy to strength_factor_graph.
    
    TJ-011.3 final fix: The adjudication variant sets
    graph['overall_strength'] = assessment['classification'] in
    operations/bazi_chart.py. This is a second leak path that must
    be closed. When the graph's variant is not in the public allowlist,
    remove all adjudication-specific verdict fields.
    """
    from .bazi_strength_display import PUBLIC_STRENGTH_VARIANTS
    
    # Fail-closed: research verdict fields are removed unless the variant
    # is EXPLICITLY in the server-side public allowlist. A missing, empty,
    # or unknown variant must NOT bypass filtering.
    # Research verdict fields (set in operations/bazi_chart.py when
    # strength_variant == ADJUDICATION_VARIANT):
    _RESEARCH_GRAPH_FIELDS = ('overall_strength', 'variant_dependencies',
                              'adjudication_fact_ref')
    
    variant = graph.get('variant')
    
    # Explicitly authorized: leave untouched.
    if variant is not None and variant in PUBLIC_STRENGTH_VARIANTS:
        return
    
    # Check if any research verdict fields are present.
    has_research_fields = any(k in graph for k in _RESEARCH_GRAPH_FIELDS)
    if not has_research_fields:
        # Regular structural factor graph (root visibility, etc.):
        # no research verdicts to filter, pass through unchanged.
        return
    
    # Research fields present but not explicitly authorized:
    # strip them. This covers missing/empty/unknown/forged variants.
    for key in _RESEARCH_GRAPH_FIELDS:
        graph.pop(key, None)
    # Mark as research-filtered for transparency.
    # Structural factor data (root candidates, etc.) remains intact.
    graph['display_state'] = 'research_only'
    graph['display_message'] = "该结论尚在研究审核中，暂不公开展示"



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
    # TJ-031.5 (Track C LOW-3): state the liuyao judgment field's scope
    # beside the field wherever the Zhouyi classic reading is projected.
    _annotate_judgment_scope(result)
    # TJ-011.3: enforce strength display policy on the public chart.
    chart = result.get('chart')
    if isinstance(chart, dict):
        _apply_strength_display_policy(chart)
    return result


# TJ-031.7 (Track B evidence gap): backend calendar conversion for
# 1900-1948 has never been independently cross-checked, while the
# frontend already limits birth years to 1949-2099
# (web/visual-prototype/src/public/birthProfile.ts: MIN_YEAR = 1949,
# validateBirthInput rejects earlier years). The public production
# boundary therefore refuses that period explicitly instead of
# returning unverified results. These helpers only DECIDE; the public
# handlers in api.py enforce after a successful execution, so every
# pre-existing rejection (tz audit, range, contracts) keeps its exact
# original behaviour and the internal/eval paths never pass through
# here at all.
UNVERIFIED_PERIOD_MIN_YEAR = 1900
UNVERIFIED_PERIOD_MAX_YEAR = 1948
UNVERIFIED_PERIOD_CODE = 'unverified_birth_period'
UNVERIFIED_PERIOD_MESSAGE = (
    '1900–1948 年期间的历法换算未经独立核对，'
    '公开生产路径不提供该时段的计算结果。'
)


def unverified_period_year(year):
    """True when a local civil year falls in the unverified period."""
    return (isinstance(year, int)
            and UNVERIFIED_PERIOD_MIN_YEAR <= year <= UNVERIFIED_PERIOD_MAX_YEAR)


def calendar_local_year(calendar):
    """Local civil year from a calendar_for_zone result, or None."""
    if not isinstance(calendar, dict):
        return None
    local = calendar.get('local_datetime')
    if not isinstance(local, str):
        return None
    try:
        return datetime.fromisoformat(local).year
    except ValueError:
        return None


# Birth input fields per the reviewed scenario contracts in
# scenario_engine.py. The question scenario's 'value' is a divination
# instant, not a birth, and is deliberately absent here; the
# bazi-profile scenario's 'value' IS a birth instant and is added by
# scenario_birth_instants for that scenario only.
_SCENARIO_BIRTH_FIELDS = (
    ('birth_value', 'birth_zone'),
    ('person_a_birth_value', 'person_a_zone'),
    ('person_b_birth_value', 'person_b_zone'),
)


def scenario_birth_instants(inputs, scenario_id):
    """(value, zone) pairs for a scenario's birth inputs."""
    pairs = list(_SCENARIO_BIRTH_FIELDS)
    if scenario_id == 'bazi-profile':
        pairs.append(('value', 'zone'))
    found = []
    for value_key, zone_key in pairs:
        value = inputs.get(value_key)
        if isinstance(value, str):
            found.append((value, inputs.get(zone_key)))
    return found


def scenario_unverified_period_years(inputs, scenario_id):
    """Local years of a scenario's birth inputs inside 1900-1948.

    The local year uses the birth zone frame (missing zone defaults to
    Asia/Shanghai, exactly as calendar_for_zone resolves it). Inputs
    that cannot be parsed are skipped: this runs only after a
    successful execution, whose own validation already rejected any
    incoherent birth input.
    """
    years = []
    for value, zone in scenario_birth_instants(inputs, scenario_id):
        try:
            instant = datetime.fromisoformat(value)
            if instant.tzinfo is None:
                continue
            year = instant.astimezone(
                ZoneInfo(zone or 'Asia/Shanghai')).year
        except Exception:
            continue
        if unverified_period_year(year):
            years.append(year)
    return years
