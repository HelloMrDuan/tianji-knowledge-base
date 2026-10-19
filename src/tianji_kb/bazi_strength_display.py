"""Bazi strength adjudication display policy (TJ-011.3 review fix).

Server-side authoritative display decisions for strength adjudication
results. This module is wired into public_projection.project_execution(),
the last line of defense before data reaches clients.

Security model:
- The `variant` MUST come from the server-side execution trace/metadata,
  never from client input or from fields inside the result dict.
- Public authorization is determined by a server-side allowlist
  (PUBLIC_STRENGTH_VARIANTS), never by a boolean flag in the result.
- Currently NO strength adjudication variant is authorized for public
  display. All adjudication results are research-only.

Display states:
- public_result: variant in allowlist AND classification is strong/weak
- research_only: audited but not in public allowlist
- insufficient: not enough evidence to adjudicate
- conflict: genuine unresolved conflicts (not mere missing evidence)
- out_of_scope: day master or month outside audited scope
- error: missing data or invalid input
"""

# Server-side allowlist of strength variants authorized for public display.
# EMPTY: no strength adjudication variant is currently authorized.
# To authorize a variant in the future, add its variant string here AND
# complete the full audit (Source/Section/Rule/Evidence/Phase2/Golden).
PUBLIC_STRENGTH_VARIANTS = frozenset()

# Audited scope for bazi-strength-adjudication-v1
AUDITED_DAY_MASTERS = frozenset({'甲', '乙'})
AUDITED_MONTHS = frozenset({'卯', '酉'})  # 卯=strong candidate, 酉=weak candidate

# User-facing messages (plain Chinese, no technical IDs)
MSG_INSUFFICIENT = "当前条件不足，暂无法判定"
MSG_CONFLICT = "存在未解决的条件冲突，暂无法判定"
MSG_OUT_OF_SCOPE = "当前范围尚未完成审核"
MSG_RESEARCH_ONLY = "该结论尚在研究审核中，暂不公开展示"
MSG_ERROR = "数据缺失或服务异常，请检查输入后重试"

# Blocker reasons that indicate GENUINE conflicts (vs missing evidence)
# Based on real blocker reasons in bazi_adjudication._bounded_assessment()
CONFLICT_REASONS = frozenset({
    'root_type_source_conflict',  # Source texts disagree on root type
})

# Blocker reasons that indicate out-of-scope (vs insufficient evidence)
OUT_OF_SCOPE_REASONS = frozenset({
    'outside_reviewed_sufficient_conditions',
})


def get_display_decision(result, *, variant=None, day_master=None, month_branch=None):
    """Determine display decision for an adjudication result.
    
    Args:
        result: dict from bazi_adjudication, or None.
        variant: str, the strength variant from SERVER-SIDE execution
            metadata (trace step input or execution record). MUST NOT
            come from client input or from fields inside result.
        day_master: str, day master stem from server-side chart
            computation (e.g. '甲'). None if unavailable.
        month_branch: str, month branch from server-side chart
            computation (e.g. '卯'). None if unavailable.
    
    Returns:
        dict with display_state, user_message, may_display_classification,
        classification (only if may_display_classification is True).
    
    Security: A forged result dict with public_enabled=True can NEVER
    produce may_display_classification=True, because authorization is
    checked against the server-side PUBLIC_STRENGTH_VARIANTS allowlist
    using the trusted variant parameter, not result contents.
    """
    if result is None or variant is None:
        return _error()
    
    # Step 1: Scope check (from trusted server-side inputs)
    # Non-wood day masters or unaudited months can never produce
    # public conclusions, regardless of what the result claims.
    if day_master is not None and day_master not in AUDITED_DAY_MASTERS:
        return _out_of_scope()
    if month_branch is not None and month_branch not in AUDITED_MONTHS:
        return _out_of_scope()
    
    # Step 2: Blocker analysis - distinguish conflict vs insufficient
    # vs out-of-scope based on real blocker reasons.
    blockers = result.get('blockers') or []
    blocker_state = _classify_blockers(blockers)
    if blocker_state is not None:
        return blocker_state
    
    # Step 3: Authorization check against server-side allowlist.
    # The variant parameter comes from trusted execution metadata.
    # A forged result dict cannot bypass this.
    if variant not in PUBLIC_STRENGTH_VARIANTS:
        return _research_only()
    
    # Step 4: Public variant - check classification.
    # Even authorized variants must not misrepresent indeterminate.
    classification = result.get('classification')
    if classification in ('strong', 'weak'):
        return {
            'display_state': 'public_result',
            'user_message': '',
            'may_display_classification': True,
            'classification': classification,
        }
    # indeterminate (or unknown) is never a public verdict
    return _insufficient()


def _classify_blockers(blockers):
    """Classify blockers into conflict/out_of_scope/insufficient.
    
    Returns display decision dict, or None if no blockers.
    """
    if not blockers:
        return None
    
    has_conflict = False
    has_out_of_scope = False
    
    for b in blockers:
        reason = b.get('reason', '')
        # Non-empty conflict_ids indicates a genuine conflict
        if b.get('conflict_ids'):
            has_conflict = True
        elif reason in CONFLICT_REASONS:
            has_conflict = True
        elif reason in OUT_OF_SCOPE_REASONS:
            has_out_of_scope = True
    
    if has_conflict:
        return {
            'display_state': 'conflict',
            'user_message': MSG_CONFLICT,
            'may_display_classification': False,
            'classification': None,
        }
    if has_out_of_scope:
        return _out_of_scope()
    # All other blockers (missing evidence, unreviewed, etc.)
    return _insufficient()


def _research_only():
    return {
        'display_state': 'research_only',
        'user_message': MSG_RESEARCH_ONLY,
        'may_display_classification': False,
        'classification': None,
    }


def _insufficient():
    return {
        'display_state': 'insufficient',
        'user_message': MSG_INSUFFICIENT,
        'may_display_classification': False,
        'classification': None,
    }


def _out_of_scope():
    return {
        'display_state': 'out_of_scope',
        'user_message': MSG_OUT_OF_SCOPE,
        'may_display_classification': False,
        'classification': None,
    }


def _error():
    return {
        'display_state': 'error',
        'user_message': MSG_ERROR,
        'may_display_classification': False,
        'classification': None,
    }


def check_scope_by_inputs(day_master, month_branch):
    """Check if given day master and month are within audited scope.
    
    This is a helper for callers that have trusted server-side chart data.
    Returns display decision dict if out of scope, else None.
    """
    if day_master is not None and day_master not in AUDITED_DAY_MASTERS:
        return _out_of_scope()
    if month_branch is not None and month_branch not in AUDITED_MONTHS:
        return _out_of_scope()
    return None


def format_indeterminate_explanation(result):
    """Format user-friendly explanation for indeterminate results.
    
    Never returns '中和' (neutral) or implies weak/strong.
    """
    if result is None:
        return MSG_ERROR
    blockers = result.get('blockers') or []
    decision = _classify_blockers(blockers)
    if decision is not None:
        return decision['user_message']
    return MSG_INSUFFICIENT


def apply_to_public_response(data, *, variant=None, day_master=None, month_branch=None):
    """Apply display policy to a public API response dict.
    
    This is the wiring point called by public_projection.project_execution().
    If the response contains strength adjudication data that is not
    authorized for public display, the classification is removed and
    replaced with a display state indicator.
    
    Args:
        data: dict, the execution output (before projection).
        variant: str, trusted variant from execution metadata.
        day_master: str, trusted day master from chart.
        month_branch: str, trusted month branch from chart.
    
    Returns:
        The display decision dict. Callers should use it to decide
        whether to include strength_assessment in the public response.
    """
    assessment = data.get('strength_assessment')
    if assessment is None:
        return None
    return get_display_decision(
        assessment,
        variant=variant,
        day_master=day_master,
        month_branch=month_branch,
    )
