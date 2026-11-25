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

Batch 3 stage 2 (TJ-0424, L1-L5 DECIDED 2026-11-25):
- L2 APPROVED the sixty-cycle derivation of xunkong: the five derived
  rows keep their source annotation (1 registered / 5 cycle derivations)
  and are now validated for all six xun and all sixty days (see the
  test suite); per-row registration is not required.
- L5 APPROVED ripo evidence + implementation (``day_break_assessment``):
  strictly conditional on the r020 preconditions (clash with the day
  branch AND static AND weak); ripo is never derived from yuepo.
- L3 APPROVED evidence construction for chukong / tianshi / yuepo
  un-breaking: ``EMPTY_HANDLING_EVIDENCE`` records the evidence
  calibre (no registered basis found -- see there); nothing is
  implemented from it, and no efficacy is inferred from a definition.
- L1 (sealed Golden admission of B1-B3/E1/E2) was APPROVED but is a
  sealed-governance step outside the public repo; it is recorded in
  GAPS, not executed here.
- L4 (yuejian/richen/wangshuai) lives in ``liuyao_yongshen``: structure
  rules there, efficacy in a separate abstaining layer.
"""

from copy import deepcopy

from .foundations import BRANCHES, CYCLE, ganzhi_index
from .operations.liuyao import branch_relation, xunkong

__all__ = [
    "CALIBRE",
    "GAPS",
    "MONTH_BRANCH_BY_LUNAR_MONTH",
    "MONTH_BREAK_BY_LUNAR_MONTH",
    "XUN_TABLE",
    "XUN_TABLE_PROVENANCE",
    "broken_branch_for_month",
    "day_break_assessment",
    "day_clash_flags",
    "empty_branches_for_day",
    "empty_handling_evidence",
    "line_empty_flags",
    "empty_flags_for_day",
    "month_break_flags",
    "xun_head_for_day",
    "xun_table_with_provenance",
    "yao_is_static",
]

VARIANT = "jingfang-eight-palaces-v1"

CALIBRE = {
    "variant": VARIANT,
    "xunkong_rules": ["liuyao.rule.r005", "liuyao.phase2.empty"],
    "yuepo_rules": ["liuyao.rule.r019", "liuyao.phase2.month_break"],
    "ripo_rules": ["liuyao.rule.r020"],
    "clash_basis_rule": "liuyao.rule.r006",
    "research_only": True,
    "public": False,
    "ai": False,
    # What this layer computes, exactly (Q15/Q16 minimum calibre +
    # stage-2 L2/L5 additions).
    "computes": (
        "empty_branches_for_day",
        "line_empty_flags",
        "broken_branch_for_month",
        "month_break_flags",
        "day_clash_flags",
        "day_break_assessment",
    ),
    # Explicitly NOT computed (no registered basis; see GAPS).
    "does_not_compute": (
        "chukong_or_tianshi_efficacy",
        "yuepo_fortune_or_severity",
        "yuepo_moving_vs_static",
        "yuepo_unbreaking",
        "yingqi",
        "ripo_weakness_verdict",
        "yongshen",
    ),
}

# Gaps that stay open after this batch (recorded, not implemented).
GAPS = {
    "chukong_tianshi": (
        "L3 decided 2026-11-25 (evidence construction approved): "
        "EMPTY_HANDLING_EVIDENCE records the calibre -- no registered "
        "section in the library covers 出空/填实/值日/合住/冲开 "
        "handling of an empty line, so no such rule is implemented and "
        "no efficacy is inferred from the definition of emptiness."
    ),
    "other_five_xun_rows_unregistered": (
        "L2 decided 2026-11-25: the sixty-cycle derivation of the five "
        "non-甲子旬 rows is APPROVED as the method; per-row classical "
        "registration is not required. The rows keep their source "
        "annotation (1 registered / 5 cycle derivations) and are "
        "validated for all six xun and all sixty days."
    ),
    "yuepo_moving_static_and_unbreaking": (
        "r019 / zs05 say nothing about moving vs static lines or about "
        "un-breaking a month-break line; L3 evidence construction "
        "found no registered basis (see EMPTY_HANDLING_EVIDENCE); "
        "no such rule is computed."
    ),
    "yuepo_sealed_golden_positive": (
        "L1 decided 2026-11-25: admitting proposed Golden B1-B3/E1-E2 "
        "to the sealed phase2_golden.json is APPROVED, but admission "
        "itself is a sealed-governance step outside the public repo "
        "and is NOT executed here; the cases stay verified only as "
        "public tests until the sealed process runs."
    ),
    "yuejian_richen_mappings": (
        "L4 decided 2026-11-25: month/day STRUCTURE rules are now "
        "implemented in tianji_kb.liuyao_yongshen (month_day_structure, "
        "line_month_day_structure); the wangshuai EFFICACY layer "
        "abstains (insufficient basis) until a registered 四時旺相 "
        "mapping exists. See liuyao_yongshen.YUEJIAN_RICHEN_DEFINITIONS."
    ),
    "yongshen_yuanshen_jishen_choushen_yingqi": (
        "Useful god / yuan-shen / ji-shen / chou-shen and yingqi have no "
        "approved mapping in this batch; liuyao_yongshen.assess() still "
        "abstains for every question type. A roles STRUCTURE framework "
        "(element relations only, no efficacy) now exists in "
        "liuyao_yongshen.roles_for_element."
    ),
    "ripo_not_parallel": (
        "L5 decided 2026-11-25: ripo (liuyao.rule.r020) is implemented "
        "as a CONDITIONAL rule (day_break_assessment) with its own "
        "'衰而靜' preconditions, strictly separate from yuepo -- never "
        "derived from month-break. The '衰' (weak) precondition has no "
        "computable calibre yet (no wangshuai mapping), so a clashed "
        "static line with unknown weakness is reported undetermined, "
        "never forced to broken or not-broken."
    ),
    "ripo_weak_precondition": (
        "The '衰' half of ripo's '衰而靜' precondition cannot be "
        "computed: no registered 四時旺相 table turns a line's element "
        "relations into a weak/strong verdict (L4 efficacy layer "
        "abstains). day_break_assessment therefore takes an explicit "
        "caller-supplied weak flag, or reports undetermined."
    ),
    "edition_caveat": (
        "zs04/zs05 independence_status is different_work_unverified_edition "
        "(different works, edition unverified); the two-book agreement is "
        "recorded with that caveat."
    ),
}

# --- L5: ripo (日破) rule record --------------------------------------
# User adjudication 2026-11-25 L5: ripo evidence gathering + implementation
# APPROVED, strictly distinguished from yuepo. Registered basis:
# liuyao.rule.r020「日破基础关系」(partially_structured),
# liuyao.section.s021 (增删卜易, chars [21469,21482), line 592 col 111):
# 「爻之衰而靜者﹐沖之則為日破」. The definition carries its own
# preconditions -- the line must be 衰 (weak) AND 靜 (static) -- and is
# NOT parallel to yuepo (whose definition has no such preconditions);
# the two must never be derived from each other. "靜" is computable
# from the yao value (7/8 static, 6/9 moving); "衰" is NOT computable
# yet (no registered wangshuai calibre), so the conditional rule takes
# weakness as an explicit caller-supplied input or reports undetermined.
RIPO_RULE = {
    "rule_id": "liuyao.rule.r020",
    "name": "日破",
    "section_id": "liuyao.section.s021",
    "locator": "增删卜易 chars [21469,21482), 第 592 行第 111 列起",
    "definition": "爻之衰而靜者﹐沖之則為日破",
    "execution_status": "partially_structured",
    "preconditions": (
        "day_clash",
        "line_static",
        "line_weak",
    ),
    "precondition_notes": {
        "day_clash": "爻支与日支构成 r006 六冲对（结构事实，可计算）。",
        "line_static": "爻静：爻值 7/8 为静，6/9 为动（可计算）。",
        "line_weak": (
            "爻衰：无已登记旺衰口径可计算；须由调用方显式提供已确立的"
            "衰事实，或判为未定（undetermined），不得默认衰或不衰。"
        ),
    },
    "not_parallel_to": "liuyao.rule.r019 (yuepo)",
    "research_only": True,
    "public": False,
    "ai": False,
}

# --- L3: chukong / tianshi / un-breaking evidence calibre -------------
# User adjudication 2026-11-25 L3: evidence construction for 出空,
# 填实 and 月破解破 APPROVED; a conditional rule may only be implemented
# once sufficient basis exists, never by inferring efficacy from a
# definition. Construction result (evidence pack 03 §7 / 04 §7, re-checked
# this batch): among the 38 registered sections in the library, NONE
# mentions 出空 / 填实 / 值日 / 合住 / 冲开 handling of an empty line,
# and NONE covers un-breaking a month-break line (合住/冲开解破).
# Every candidate below therefore stays at "no_registered_basis":
# recorded as a gap, NOT implemented. "needed" states what evidence
# would be required before any conditional rule could be built.
EMPTY_HANDLING_EVIDENCE = {
    "chukong": {
        "name": "出空",
        "status": "no_registered_basis",
        "searched": "38 registered sections, keyword search (evidence pack 03 §7)",
        "needed": (
            "A registered classical passage stating under which condition "
            "an empty line counts as having come out of emptiness, with "
            "its own section id and locatable text."
        ),
    },
    "tianshi": {
        "name": "填实",
        "status": "no_registered_basis",
        "searched": "38 registered sections, keyword search (evidence pack 03 §7)",
        "needed": (
            "A registered classical passage stating under which condition "
            "an empty line counts as filled, with its own section id and "
            "locatable text."
        ),
    },
    "zhiri": {
        "name": "值日",
        "status": "no_registered_basis",
        "searched": "38 registered sections, keyword search (evidence pack 03 §7)",
        "needed": (
            "A registered classical passage stating what a day branch "
            "coinciding with an empty branch does to the empty line, "
            "with its own section id and locatable text."
        ),
    },
    "hezhu_chongkai_empty": {
        "name": "合住/冲开（空爻）",
        "status": "no_registered_basis",
        "searched": "38 registered sections, keyword search (evidence pack 03 §7)",
        "needed": (
            "A registered classical passage stating whether combining or "
            "clashing an empty line changes its empty status, with its "
            "own section id and locatable text."
        ),
    },
    "yuepo_unbreaking": {
        "name": "月破解破（合住/冲开解破）",
        "status": "no_registered_basis",
        "searched": "38 registered sections (evidence pack 04 §7)",
        "needed": (
            "A registered classical passage stating whether combining or "
            "clashing a month-break line un-breaks it, with its own "
            "section id and locatable text."
        ),
    },
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

# Provenance for each six-xun row (TJ-0424 batch 3, L2 DECIDED 2026-11-25).
# Exactly ONE row has per-row classical registration: 甲子旬, via
# liuyao.section.s019 (卜筮正宗, chars [13706,13731)) and
# liuyao.evidence.phase2.zs04 (增删卜易, chars [29389,29434)), the
# latter adding 「餘仿此」 for the remaining xun. The other FIVE rows
# are EXPLICIT CYCLE DERIVATIONS: their empty branches come from the
# sixty-cycle computation (operations.liuyao.xunkong), and the
# 卜筮正宗 lines 373-374 six-xun table that lists them is NOT
# individually registered as sections (evidence pack 03 §2/§7) -- the
# pack quotes none of its text, only its line numbers, for re-checking.
# Each derived row is therefore labelled derivation
# "sixty_cycle_derivation" and registration "unregistered_per_row",
# with the note "循环派生、未逐条登记". L2 DECIDED 2026-11-25:
# the cycle derivation is the approved method, so per-row registration
# is not required; this table does NOT present the
# derived rows as registered. research_only: this table is a
# provenance record, not a new computation -- the values are locked
# against XUN_TABLE and against xunkong() for all 60 days.
XUN_TABLE_PROVENANCE = {
    "甲子": {
        "xun_head": "甲子",
        "empty_branches": ("戌", "亥"),
        "derivation": "registered_per_row",
        "registration": "registered_per_row",
        "evidence": (
            "liuyao.section.s019 (卜筮正宗 chars [13706,13731)); "
            "liuyao.evidence.phase2.zs04 (增删卜易 chars [29389,29434))"
        ),
        "note": "逐条登记：甲子旬戌亥空，两部古籍同证。",
    },
    "甲戌": {
        "xun_head": "甲戌",
        "empty_branches": ("申", "酉"),
        "derivation": "sixty_cycle_derivation",
        "registration": "unregistered_per_row",
        "evidence": (
            "六十甲子循环推导；卜筮正宗.txt 第 373-374 行六旬表（未逐条登记，"
            "原文不引用，仅行号定位供复核）；增删卜易 zs04「餘仿此」"
        ),
        "derivation_status": "approved_L2_2026-11-25",
        "note": "循环派生、未逐条登记；L2 已批准（2026-11-25）："
        "六十甲子循环推导获批，保留来源标注。",
    },
    "甲申": {
        "xun_head": "甲申",
        "empty_branches": ("午", "未"),
        "derivation": "sixty_cycle_derivation",
        "registration": "unregistered_per_row",
        "evidence": (
            "六十甲子循环推导；卜筮正宗.txt 第 373-374 行六旬表（未逐条登记，"
            "原文不引用，仅行号定位供复核）；增删卜易 zs04「餘仿此」"
        ),
        "derivation_status": "approved_L2_2026-11-25",
        "note": "循环派生、未逐条登记；L2 已批准（2026-11-25）："
        "六十甲子循环推导获批，保留来源标注。",
    },
    "甲午": {
        "xun_head": "甲午",
        "empty_branches": ("辰", "巳"),
        "derivation": "sixty_cycle_derivation",
        "registration": "unregistered_per_row",
        "evidence": (
            "六十甲子循环推导；卜筮正宗.txt 第 373-374 行六旬表（未逐条登记，"
            "原文不引用，仅行号定位供复核）；增删卜易 zs04「餘仿此」"
        ),
        "derivation_status": "approved_L2_2026-11-25",
        "note": "循环派生、未逐条登记；L2 已批准（2026-11-25）："
        "六十甲子循环推导获批，保留来源标注。",
    },
    "甲辰": {
        "xun_head": "甲辰",
        "empty_branches": ("寅", "卯"),
        "derivation": "sixty_cycle_derivation",
        "registration": "unregistered_per_row",
        "evidence": (
            "六十甲子循环推导；卜筮正宗.txt 第 373-374 行六旬表（未逐条登记，"
            "原文不引用，仅行号定位供复核）；增删卜易 zs04「餘仿此」"
        ),
        "derivation_status": "approved_L2_2026-11-25",
        "note": "循环派生、未逐条登记；L2 已批准（2026-11-25）："
        "六十甲子循环推导获批，保留来源标注。",
    },
    "甲寅": {
        "xun_head": "甲寅",
        "empty_branches": ("子", "丑"),
        "derivation": "sixty_cycle_derivation",
        "registration": "unregistered_per_row",
        "evidence": (
            "六十甲子循环推导；卜筮正宗.txt 第 373-374 行六旬表（未逐条登记，"
            "原文不引用，仅行号定位供复核）；增删卜易 zs04「餘仿此」"
        ),
        "derivation_status": "approved_L2_2026-11-25",
        "note": "循环派生、未逐条登记；L2 已批准（2026-11-25）："
        "六十甲子循环推导获批，保留来源标注。",
    },
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


def xun_table_with_provenance():
    """Return a deep copy of the six-xun table with per-row provenance.

    Each row carries its empty branches plus ``derivation`` and
    ``registration``: exactly one row (甲子旬) is
    ``registered_per_row``; the other five are
    ``sixty_cycle_derivation`` / ``unregistered_per_row`` -- cycle
    derivations explicitly labelled "循环派生、未逐条登记", never
    presented as registered rows. L2 DECIDED 2026-11-25: the cycle
    derivation is the approved method, so per-row registration is not
    required. The values are locked against
    ``XUN_TABLE`` and ``xunkong()`` in the test suite.
    """
    return deepcopy(XUN_TABLE_PROVENANCE)


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


def empty_handling_evidence():
    """Return a deep copy of the L3 evidence-calibre record.

    For each candidate post-empty / un-breaking handling (chukong,
    tianshi, zhiri, hezhu/chongkai on empty lines, yuepo un-breaking)
    the record states the search performed and that NO registered basis
    was found (``status`` is ``no_registered_basis`` for every entry).
    This is evidence construction only: no handling rule is implemented
    and no efficacy is inferred from any definition.
    """
    return deepcopy(EMPTY_HANDLING_EVIDENCE)


def yao_is_static(yao_value):
    """Return True when a yao value is a static (non-moving) line.

    Yao values 7 (少阳) and 8 (少阴) are static; 6 (老阴) and 9
    (老阳) are moving. Raises ValueError outside {6, 7, 8, 9}.
    """
    if type(yao_value) is not int or yao_value not in (6, 7, 8, 9):
        raise ValueError("yao_value must be one of 6/7/8/9")
    return yao_value in (7, 8)


def _require_yao_values(yao_values):
    if (
        not isinstance(yao_values, (list, tuple))
        or len(yao_values) != 6
        or any(type(v) is not int or v not in (6, 7, 8, 9) for v in yao_values)
    ):
        raise ValueError("yao_values must be six integer yao values 6/7/8/9, bottom to top")
    return list(yao_values)


def day_clash_flags(line_branches, day_ganzhi):
    """Return per-line day-clash flags for six line branches, bottom to top.

    A line day-clashes exactly when its branch clashes with the DAY
    branch (reuses ``operations.liuyao.branch_relation``). This is a
    STRUCTURAL fact only: a day-clashed line is NOT automatically a
    day-break (ripo) line -- ripo additionally requires the line to be
    static AND weak (``liuyao.rule.r020``), and must never be derived
    from the month-break flags. Raises ValueError on malformed input.
    """
    branches = _require_six_branches(line_branches)
    day_branch = _require_day_ganzhi(day_ganzhi)[1]
    return [branch_relation(b, day_branch)["clash"] for b in branches]


def day_break_assessment(line_branches, day_ganzhi, yao_values,
                         line_weak_flags=None):
    """Assess per-line day-break (ripo, ``liuyao.rule.r020``), conditionally.

    r020: 「爻之衰而靜者﹐沖之則為日破」 -- a line is day-broken only
    when ALL THREE preconditions hold: (a) its branch clashes with the
    day branch, (b) the line is static (yao value 7/8), (c) the line is
    weak (衰). Preconditions (a) and (b) are computed here from the
    inputs. Precondition (c) has NO computable calibre yet (no
    registered wangshuai mapping), so it must be supplied explicitly
    via ``line_weak_flags`` -- a six-item list of True/False/None,
    bottom to top, stating a separately established weak fact per
    line -- or left as None.

    Per line the result carries ``day_break`` as True / False / None:
    - True: clashed AND static AND weak (the r020 conditions are met).
    - False: not clashed, or moving, or (clashed and static but)
      explicitly not weak.
    - None (undetermined): clashed AND static AND weakness unknown --
      the rule CANNOT decide this line yet; it is reported as
      ``undetermined_weak_unknown``, never forced to True or False.

    ``verdict`` is always None: day-break is a structural condition
    record, not a fortune conclusion. The assessment is strictly
    separate from yuepo: it reads only the DAY branch, never the month
    branch, and shares no derivation with ``month_break_flags``.
    Raises ValueError on malformed input.
    """
    branches = _require_six_branches(line_branches)
    day = _require_day_ganzhi(day_ganzhi)
    day_branch = day[1]
    values = _require_yao_values(yao_values)
    if line_weak_flags is None:
        weak_flags = [None] * 6
    else:
        if (
            not isinstance(line_weak_flags, (list, tuple))
            or len(line_weak_flags) != 6
            or any(v is not None and type(v) is not bool for v in line_weak_flags)
        ):
            raise ValueError(
                "line_weak_flags must be six True/False/None values, bottom to top"
            )
        weak_flags = list(line_weak_flags)
    clashes = day_clash_flags(branches, day)
    lines = []
    for position, (branch, clash, yao_value, weak) in enumerate(
        zip(branches, clashes, values, weak_flags), start=1
    ):
        static = yao_is_static(yao_value)
        if not clash:
            day_break, status = False, "not_day_break"
        elif not static:
            day_break, status = False, "not_day_break_moving"
        elif weak is True:
            day_break, status = True, "day_break"
        elif weak is False:
            day_break, status = False, "not_day_break_not_weak"
        else:
            day_break, status = None, "undetermined_weak_unknown"
        lines.append(
            {
                "position": position,
                "line_branch": branch,
                "day_branch": day_branch,
                "day_ganzhi": day,
                "day_clash": clash,
                "is_static": static,
                "yao_value": yao_value,
                "weak": weak,
                "day_break": day_break,
                "status": status,
            }
        )
    return {
        "day_ganzhi": day,
        "day_branch": day_branch,
        "line_branches": branches,
        "rule": deepcopy(RIPO_RULE),
        "lines": lines,
        "day_break_lines": [ln["position"] for ln in lines if ln["day_break"] is True],
        "undetermined_lines": [ln["position"] for ln in lines if ln["day_break"] is None],
        "verdict": None,
        "note": (
            "日破条件规则（r020）：冲日支且静且衰方为日破；衰未确立时判未定，"
            "不与月破互相推导，不推出吉凶。"
        ),
    }
