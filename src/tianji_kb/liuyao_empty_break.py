"""Liuyao xunkong (旬空) and yuepo (月破) minimum-calibre computation layer.

User adjudication 2026-11-25 Q15/Q16 (TJ-0424 batch 2, P1 liuyao).
This module is the callable layer for exactly the two approved minimum
calibres -- nothing more:

- Q15 (xunkong): approved minimum executable calibre from the verified
  rule ``liuyao.rule.r005`` + ``liuyao.phase2.empty``. Computes (a) the
  two empty branches for a day ganzhi and (b) a per-line empty flag
  (line branch in the empty branches). The empty-branch computation
  itself is NOT re-implemented here: it reuses the existing callable
  ``tianji_kb.operations.liuyao.xunkong`` (sixty-cycle derivation,
  already ``validated``); this module only adds the six-xun lock table
  and the per-line flag layer. No chukong / tianshi (出空/填实) efficacy:
  no registered section covers any post-empty handling, so none is
  computed.
- Q16 (yuepo): approved minimum executable calibre from
  ``liuyao.rule.r019`` + ``liuyao.phase2.month_break`` (Phase2
  ``validated``; Phase1 is only ``partially_structured`` -- the
  executable layer lives in Phase2, see the evidence pack). Computes
  (a) the broken branch for a month branch and (b) a per-line
  month-break flag (line branch clashes with the month branch under
  the ``liuyao.rule.r006`` six-clash table). The clash test reuses the
  existing callable ``tianji_kb.operations.liuyao.branch_relation``.
  No good/bad fortune, no moving/static distinction, no un-breaking,
  no yingqi (应期).

Registered classical excerpts quoted here (and only here) are the ones
already registered and verified in the evidence pack
(``~/workspace/tj-core-engine-batch2-liuyao-evidence/``):

- xunkong, ``liuyao.section.s019`` (卜筮正宗, chars [13706,13731)):
  「假如甲子日至癸酉十日為一旬，旬內無戍亥故曰戍亥空．」
- xunkong, ``liuyao.evidence.phase2.zs04`` (增删卜易, chars [29389,29434)):
  「何謂旬空？如甲子至癸酉日為一旬﹐此十日之內﹐並無戌亥﹐以爻逢戌亥為空亡﹐又名旬空﹐餘仿此。」
- yuepo, ``liuyao.section.s020`` (卜筮正宗, chars [13888,13900)):
  「凡月建所衝之爻名為月破．」
- yuepo, ``liuyao.evidence.phase2.zs05`` (增删卜易, chars [33044,33098)):
  「正申、二酉、三戌﹐四亥、五子、六丑、七寅、八卯、九辰﹐十巳、十一午、十二未﹐月建沖之為月破﹐逐月之破日是也。」
- six-clash basis, ``liuyao.section.s023`` (增删卜易, chars [25223,25253)):
  「子午相沖、丑未相沖、寅申相沖、卯酉相沖、辰戌相沖、巳亥相沖。」

Status: ``research_only=True``, ``public=False``, ``ai=False``.
Fail-closed: invalid day ganzhi / branch / line input raises
``ValueError``; nothing in this module outputs a verdict, a strength,
a useful god, or a date. The five other xun empty-branch rows exist in
卜筮正宗 lines 373-374 but are NOT individually registered sections;
the six-xun table below is locked against the sixty-cycle computation,
not against per-row citations, and the test suite records that gap.
"""

from .foundations import BRANCHES, CYCLE, ganzhi_index
from .operations.liuyao import branch_relation, xunkong

__all__ = [
    "CALIBRE",
    "GAPS",
    "MONTH_BRANCH_BY_LUNAR_MONTH",
    "MONTH_BREAK_BY_LUNAR_MONTH",
    "XUN_TABLE",
    "broken_branch_for_month",
    "empty_branches_for_day",
    "line_empty_flags",
    "empty_flags_for_day",
    "month_break_flags",
    "xun_head_for_day",
]

VARIANT = "jingfang-eight-palaces-v1"

CALIBRE = {
    "variant": VARIANT,
    "xunkong_rules": ["liuyao.rule.r005", "liuyao.phase2.empty"],
    "yuepo_rules": ["liuyao.rule.r019", "liuyao.phase2.month_break"],
    "clash_basis_rule": "liuyao.rule.r006",
    "research_only": True,
    "public": False,
    "ai": False,
    # What this layer computes, exactly (Q15/Q16 minimum calibre).
    "computes": (
        "empty_branches_for_day",
        "line_empty_flags",
        "broken_branch_for_month",
        "month_break_flags",
    ),
    # Explicitly NOT computed (no registered basis; see GAPS).
    "does_not_compute": (
        "chukong_or_tianshi_efficacy",
        "yuepo_fortune_or_severity",
        "yuepo_moving_vs_static",
        "yuepo_unbreaking",
        "yingqi",
        "ripo",
        "yongshen",
    ),
}

# Gaps that stay open after this batch (recorded, not implemented).
GAPS = {
    "chukong_tianshi": (
        "No registered section in the library covers 出空/填实/值日/合住/冲开 "
        "handling of an empty line; the approved xunkong calibre stops at "
        "the empty flag."
    ),
    "other_five_xun_rows_unregistered": (
        "The other five xun empty-branch rows exist in 卜筮正宗 lines 373-374 "
        "but are not individually registered sections; the six-xun table is "
        "locked against the sixty-cycle computation (see XUN_TABLE)."
    ),
    "yuepo_moving_static_and_unbreaking": (
        "r019 / zs05 say nothing about moving vs static lines or about "
        "un-breaking a month-break line; no such rule is computed."
    ),
    "yuepo_sealed_golden_positive": (
        "Sealed phase2_golden.json has no month-break positive case; "
        "proposed Golden B1-B3 are verified as real tests in "
        "tests/test_tj0424_liuyao_xunkong_yuepo.py, not yet admitted to "
        "the sealed Golden file (admission is a separate governance step)."
    ),
    "yuejian_richen_mappings": (
        "liuyao.rule.r008 (yuejian) and liuyao.rule.r009 (richen) are "
        "definition-only; no executable mapping exists. See "
        "tianji_kb.liuyao_yongshen.YUEJIAN_RICHEN_DEFINITIONS."
    ),
    "yongshen_yuanshen_jishen_choushen_yingqi": (
        "Useful god / yuan-shen / ji-shen / chou-shen and yingqi have no "
        "approved mapping in this batch; liuyao_yongshen.assess() still "
        "abstains for every question type."
    ),
    "ripo_not_parallel": (
        "ripo (liuyao.rule.r020) carries its own '衰而靜' precondition and "
        "is NOT parallel to yuepo; it must not be derived from month-break."
    ),
    "edition_caveat": (
        "zs04/zs05 independence_status is different_work_unverified_edition "
        "(different works, edition unverified); the two-book agreement is "
        "recorded with that caveat."
    ),
}

# Six-xun empty-branch table, keyed by xun head (the jia day starting
# each ten-day xun). Locked against the sixty-cycle computation
# (operations.liuyao.xunkong) for all 60 days in the test suite; the
# 甲子旬 row is the one with per-row classical registration (s019/zs04),
# the other five rows rest on the cycle derivation (see GAPS).
XUN_TABLE = {
    "甲子": ("戌", "亥"),
    "甲戌": ("申", "酉"),
    "甲申": ("午", "未"),
    "甲午": ("辰", "巳"),
    "甲辰": ("寅", "卯"),
    "甲寅": ("子", "丑"),
}

# Month-break table from the second source (zs05): lunar month number
# -> broken branch. 正月建寅破申, 二月建卯破酉, ..., 十二月建丑破未.
# MONTH_BRANCH_BY_LUNAR_MONTH is the corresponding month-branch table
# (正月建寅 ... 十二月建丑); the test suite checks the two tables agree
# with the six-clash table month by month (12/12).
MONTH_BRANCH_BY_LUNAR_MONTH = {
    1: "寅",
    2: "卯",
    3: "辰",
    4: "巳",
    5: "午",
    6: "未",
    7: "申",
    8: "酉",
    9: "戌",
    10: "亥",
    11: "子",
    12: "丑",
}

MONTH_BREAK_BY_LUNAR_MONTH = {
    1: "申",
    2: "酉",
    3: "戌",
    4: "亥",
    5: "子",
    6: "丑",
    7: "寅",
    8: "卯",
    9: "辰",
    10: "巳",
    11: "午",
    12: "未",
}


def _require_day_ganzhi(day_ganzhi):
    if not isinstance(day_ganzhi, str):
        raise ValueError("day_ganzhi must be a sixty-cycle ganzhi string")
    # ganzhi_index raises ValueError for anything outside the 60-cycle.
    ganzhi_index(day_ganzhi)
    return day_ganzhi


def _require_branch(branch):
    if not isinstance(branch, str) or branch not in list(BRANCHES):
        raise ValueError("expected one earthly branch: %r" % (branch,))
    return branch


def _require_six_branches(line_branches):
    if (
        not isinstance(line_branches, (list, tuple))
        or len(line_branches) != 6
        or any(not isinstance(b, str) or b not in list(BRANCHES) for b in line_branches)
    ):
        raise ValueError("line_branches must be six earthly branches, bottom to top")
    return list(line_branches)


def xun_head_for_day(day_ganzhi):
    """Return the xun head (jia day) of the ten-day xun containing a day.

    ``甲子`` .. ``癸酉`` -> ``甲子``; ``甲戌`` .. ``癸未`` -> ``甲戌``;
    and so on through the six xun. Raises ValueError outside the
    sixty-cycle.
    """
    index = ganzhi_index(_require_day_ganzhi(day_ganzhi))
    return CYCLE[index // 10 * 10]


def empty_branches_for_day(day_ganzhi):
    """Return the two empty branches for a day ganzhi, bottom-to-top order.

    Reuses the existing callable ``operations.liuyao.xunkong`` -- this
    layer adds no new empty-branch computation of its own. E.g.
    ``甲子`` -> ``["戌", "亥"]``; ``己丑`` -> ``["午", "未"]``.
    Raises ValueError for a day ganzhi outside the sixty-cycle.
    """
    return list(xunkong(_require_day_ganzhi(day_ganzhi)))


def line_empty_flags(line_branches, empty_branches):
    """Return per-line empty flags for six line branches, bottom to top.

    A line is empty exactly when its branch is one of the two empty
    branches ("以爻逢戌亥為空亡" -- the empty mark falls on the LINE
    branch, never on the day or month branch itself). ``empty_branches``
    must be the two branches for the day in question (see
    ``empty_branches_for_day``). Raises ValueError on malformed input.
    """
    branches = _require_six_branches(line_branches)
    if (
        not isinstance(empty_branches, (list, tuple))
        or len(empty_branches) != 2
        or any(not isinstance(b, str) or b not in list(BRANCHES) for b in empty_branches)
    ):
        raise ValueError("empty_branches must be two earthly branches")
    empty = set(empty_branches)
    return [b in empty for b in branches]


def empty_flags_for_day(line_branches, day_ganzhi):
    """Convenience: per-line empty flags for six line branches + a day."""
    return line_empty_flags(line_branches, empty_branches_for_day(day_ganzhi))


def broken_branch_for_month(month_branch):
    """Return the branch broken by a month branch (the clash partner).

    "凡月建所衝之爻名為月破" -- the broken branch is the branch that
    clashes with the month branch under the r006 six-clash table
    (子午/丑未/寅申/卯酉/辰戌/巳亥). E.g. ``午`` -> ``子``,
    ``子`` -> ``午``. Raises ValueError for a non-branch input.
    """
    index = BRANCHES.index(_require_branch(month_branch))
    return BRANCHES[(index + 6) % 12]


def month_break_flags(line_branches, month_branch):
    """Return per-line month-break flags for six line branches, bottom to top.

    A line is month-broken exactly when its branch clashes with the
    month branch (reuses ``operations.liuyao.branch_relation``). The
    month branch itself is never month-broken: a line whose branch
    equals the month branch is False. Raises ValueError on malformed
    input. No fortune, severity, or yingqi conclusion follows from
    these flags.
    """
    branches = _require_six_branches(line_branches)
    month = _require_branch(month_branch)
    return [branch_relation(b, month)["clash"] for b in branches]
