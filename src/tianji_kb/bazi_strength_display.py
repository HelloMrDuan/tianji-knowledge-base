"""Bazi strength adjudication display policy.

Determines what, if anything, may be shown to end users for a given
strength adjudication result. The server is the authoritative decision
maker; clients must not reinterpret research data as public conclusions.

Display states:
- public_result: audited AND authorized for public release
- research_only: audited but research-only, must not be shown publicly
- insufficient: not enough evidence, cannot adjudicate
- conflict: unresolved conflicts, cannot adjudicate
- out_of_scope: day master or month outside audited scope
- error: missing data or API failure
"""

# User-facing messages (plain Chinese, no technical IDs)
MSG_INSUFFICIENT = "当前条件不足，暂无法判定"
MSG_CONFLICT = "存在未解决的条件冲突，暂无法判定"
MSG_OUT_OF_SCOPE = "当前范围尚未完成审核"
MSG_RESEARCH_ONLY = "该结论尚在研究审核中，暂不公开展示"
MSG_ERROR = "数据缺失或服务异常，请检查输入后重试"

# Scope of the currently audited adjudication variant
AUDITED_DAY_MASTERS = frozenset({'甲', '乙'})
AUDITED_STRONG_MONTH = '卯'
AUDITED_WEAK_MONTH = '酉'


def get_display_decision(result):
    """Determine display decision for an adjudication result.
    
    Args:
        result: dict from bazi_adjudication._bounded_assessment() or
                strength_assessment(), or None if unavailable.
    
    Returns:
        dict with:
        - display_state: one of public_result, research_only, insufficient,
                         conflict, out_of_scope, error
        - user_message: plain Chinese message for the user (empty if public_result)
        - may_display_classification: bool, whether classification may be shown
        - classification: the classification value (only if may_display_classification)
    """
    if result is None:
        return {
            'display_state': 'error',
            'user_message': MSG_ERROR,
            'may_display_classification': False,
            'classification': None,
        }
    
    # Research-only results must never be shown publicly,
    # regardless of classification value.
    if result.get('research_only') is True and not result.get('public_enabled'):
        # Check if it's out of scope first (more specific message)
        scope_info = _check_scope(result)
        if scope_info is not None:
            return scope_info
        # Check for conflicts
        if result.get('blockers'):
            return {
                'display_state': 'conflict',
                'user_message': MSG_CONFLICT,
                'may_display_classification': False,
                'classification': None,
            }
        # Indeterminate due to insufficient conditions
        return {
            'display_state': 'research_only',
            'user_message': MSG_RESEARCH_ONLY,
            'may_display_classification': False,
            'classification': None,
        }
    
    # Publicly enabled results (future; currently none)
    if result.get('public_enabled') is True:
        classification = result.get('classification')
        if classification in ('strong', 'weak'):
            return {
                'display_state': 'public_result',
                'user_message': '',
                'may_display_classification': True,
                'classification': classification,
            }
        # Public but indeterminate: must not be misread as neutral/weak
        return {
            'display_state': 'insufficient',
            'user_message': MSG_INSUFFICIENT,
            'may_display_classification': False,
            'classification': None,
        }
    
    # Fallback: treat as insufficient
    return {
        'display_state': 'insufficient',
        'user_message': MSG_INSUFFICIENT,
        'may_display_classification': False,
        'classification': None,
    }


def _check_scope(result):
    """Check if result is out of audited scope.
    
    Returns display decision dict if out of scope, else None.
    """
    # The adjudication result includes scope limitations in text form.
    # For now, out-of-scope is determined by the caller providing
    # day_master and month_branch. If not provided, skip this check.
    return None


def check_scope_by_inputs(day_master, month_branch):
    """Check if given day master and month are within audited scope.
    
    Args:
        day_master: str, heavenly stem of day master (e.g. '甲')
        month_branch: str, earthly branch of month (e.g. '卯')
    
    Returns:
        dict with display_state and user_message, or None if in scope.
    """
    if day_master not in AUDITED_DAY_MASTERS:
        return {
            'display_state': 'out_of_scope',
            'user_message': MSG_OUT_OF_SCOPE,
            'may_display_classification': False,
            'classification': None,
        }
    # Month scope: only 卯 (strong) and 酉 (weak) have audited conditions
    if month_branch not in (AUDITED_STRONG_MONTH, AUDITED_WEAK_MONTH):
        return {
            'display_state': 'out_of_scope',
            'user_message': MSG_OUT_OF_SCOPE,
            'may_display_classification': False,
            'classification': None,
        }
    return None


def format_indeterminate_explanation(result):
    """Format a user-friendly explanation for indeterminate results.
    
    Never returns '中和' (neutral) or implies weak/strong.
    """
    if result is None:
        return MSG_ERROR
    if result.get('blockers'):
        return MSG_CONFLICT
    return MSG_INSUFFICIENT
