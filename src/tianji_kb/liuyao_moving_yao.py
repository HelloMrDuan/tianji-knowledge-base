"""Liuyao moving / changed lines (L-05) and month-break motion (L-07) -- STRUCTURE ONLY.

Batch 4 (TJ-0426 Lane 4, 2026-11-27). This module computes ONLY what
is already determined by registered structure: which lines move (yao
values 6/9, the same rule the chart layer uses), which changed branches
differ from the original branches, and the four-way month-break x
motion classification of each line. It builds NO efficacy: no moving
line is said to generate / control / help / harm any other line, no
changed line is said to "return-generate" (回头生) or "return-control"
(回头克) anything, and no month-break line is said to be un-broken.

Why efficacy stays out (evidence first):
- L-05: the registered definitions are s001 ("六爻不動則不變﹐動則必變"),
  s011 ("變出之爻安六親者仍照正卦而推") and s010 ("爻之旺而靜者沖之則為
  暗動" -- 暗動 itself needs 旺, i.e. the unbuilt L-04 wangshuai layer).
  The 回头生/回头克 efficacy sentences (增删卜易 lines 852-853,
  "用神化吉/化凶") are LOCATED but NOT registered sections; they are
  recorded in MOVING_YAO_EVIDENCE as candidates for future governance
  registration, never as rules. ``assess_moving_effect`` therefore
  abstains with explicit unmet conditions.
- L-07: r019 / zs05 say nothing about moving vs static month-break
  lines or about un-breaking one (evidence pack 04 §3.4). Located but
  unregistered discussions exist (卜筮正宗 lines 998/1060/2749, 增删卜易
  lines 1251/1977/2307), including an explicit dispute (張星元言月破無可解,
  卜筮正宗 line 1060). ``yuepo_motion_structure`` therefore reports the
  four motion classes as facts only; ``distinction_verdict`` and
  ``unbreaking`` are always None with status "no_registered_basis".
- L-06 (chukong / tianshi / un-breaking of empty lines) is NOT built
  here either: EMPTY_HANDLING_EVIDENCE still records no registered
  basis for every candidate, and this module adds no post-empty handling.
  Located unregistered discussions (增删卜易 lines 968/1402, 卜筮正宗
  lines 2629/2832) are recorded in the evidence pack (05 §8.4) only.

The chart layer (``operations.liuyao_chart.chart``) is NOT touched and
NOT re-implemented here: this module never derives a changed hexagram
and never calls the chart. Callers supply the original and changed
branch lists (e.g. from a chart result); this module only classifies
them. A changed branch differing from the original branch does NOT by
itself imply the line moved: when a whole trigram flips, the changed
hexagram's najia is recomputed for all its lines (evidence-pack-05 case
C1: lines 4 and 5 show different changed branches while static).

Status: ``research_only=True``, ``public=False``, ``ai=False``.
Fail-closed: malformed input raises ``ValueError``; every efficacy
question returns an explicit abstention, never a verdict, strength,
useful god, or date. Free-text questions never enter this module: it
takes only structured line data.
"""

from copy import deepcopy

from .liuyao_empty_break import day_clash_flags, month_break_flags, yao_is_static
from .liuyao_yongshen import BRANCH_ELEMENTS

__all__ = [
    "CALIBRE",
    "DARK_MOVING_CONDITIONS",
    "MOVING_YAO_EVIDENCE",
    "YUEPO_MOTION_EVIDENCE",
    "assess_moving_effect",
    "changed_line_facts",
    "dark_moving_structure",
    "line_motion",
    "moving_lines",
    "moving_yao_evidence",
    "yuepo_motion_evidence",
    "yuepo_motion_structure",
]

CALIBRE = {
    "variant": "jingfang-eight-palaces-v1",
    "research_only": True,
    "public": False,
    "ai": False,
    "computes": (
        "moving_lines",
        "line_motion",
        "changed_line_facts",
        "dark_moving_structure",
        "yuepo_motion_structure",
    ),
    "does_not_compute": (
        "moving_line_efficacy",
        "changed_line_return_effect",
        "dark_moving_verdict",
        "yuepo_motion_distinction",
        "yuepo_unbreaking",
        "chukong_or_tianshi_efficacy",
        "yingqi",
        "yongshen",
    ),
}

# --- L-05 evidence: what is registered vs merely located --------------
# Registered definitions only (verified 2026-11-27 against the sealed
# registry + classical text files; see evidence pack 05 §8.3). The
# "candidate" entries are LOCATED unregistered text: recorded so a
# future governance registration knows where to look, never used as a
# rule. "status" is "registered" only for the first three entries.
MOVING_YAO_EVIDENCE = {
    "motion_definition": {
        "rule_id": "liuyao.rule.r001",
        "term": "liuyao.term.t001/t010",
        "section_id": "liuyao.section.s001",
        "locator": "增删卜易 chars [14908,14920)",
        "definition": "六爻不動則不變﹐動則必變",
        "status": "registered",
        "note": "动爻定义：不动则不变，动则必变（爻值 6/9 为动，排盘层已实现）。",
    },
    "changed_line_relatives": {
        "rule_id": "liuyao.rule.r001",
        "term": "liuyao.term.t012",
        "section_id": "liuyao.section.s011",
        "locator": "增删卜易 chars [14788,14802)",
        "definition": "變出之爻安六親者仍照正卦而推",
        "status": "registered",
        "note": "变爻六亲仍照正卦推（排盘层 changed_relative_to_original_palace 已实现）。",
    },
    "dark_moving_definition": {
        "rule_id": None,
        "term": "liuyao.term.t011",
        "section_id": "liuyao.section.s010",
        "locator": "增删卜易 chars [21451,21463)",
        "definition": "爻之旺而靜者沖之則為暗動",
        "status": "registered",
        "note": (
            "暗動定义本身已登记，但其“旺”前提依赖未建的 L-04 旺衰层，"
            "故暗動不可算，只记结构条件（见 DARK_MOVING_CONDITIONS）。"
        ),
    },
    "return_effect_candidates": {
        "rule_id": None,
        "term": None,
        "section_id": None,
        "locator": "增删卜易 lines 852-853, chars [31594,31630) / [31631,31667)",
        "definition": (
            "用神化吉：凡用神元神動化回頭生、化長生、化帝旺、化扶助、化日月皆為化吉。"
            "用神化凶：凡用神元神動化回頭克、化絕、化墓、化空、化鬼、化退神皆為化凶。"
        ),
        "status": "located_unregistered",
        "note": (
            "回头生/回头克效力候选：未登记为 section，须先注册再立规则；"
            "本次不立效力，assess_moving_effect 恒 abstain。"
        ),
    },
    "moving_notation": {
        "rule_id": None,
        "term": None,
        "section_id": None,
        "locator": "增删卜易 line 356, chars [13666,13760)",
        "definition": (
            "卦有「○」變出﹐「○」為重重為陽﹐陽動變陰。"
            "卦有「ㄨ」變出﹐「ㄨ」為交﹐交為陰﹐陰動變陽。"
        ),
        "status": "located_unregistered",
        "note": "○ = 老阳（9，动），ㄨ = 老阴（6，动）；符号与爻值的对应，供案例推导核对。",
    },
}

# --- L-05: 暗動 (s010) conditions -------------------------------------
# "爻之旺而靜者沖之則為暗動": a line is dark-moving only when it is
# strong (旺) AND static AND clashed. Static and clashed are computable
# structure facts; strong is NOT (no registered wangshuai mapping, L-04).
DARK_MOVING_CONDITIONS = (
    {
        "id": "line_static",
        "condition": "The line is static (yao value 7/8).",
        "status": "computable",
        "evidence": "Yao value itself; see yao_is_static.",
    },
    {
        "id": "line_clashed",
        "condition": "The line branch is clashed by the day or month branch.",
        "status": "computable",
        "evidence": "r006 six-clash table (branch_relation).",
    },
    {
        "id": "line_strong",
        "condition": "The line is strong (旺).",
        "status": "unmet",
        "evidence": (
            "No registered 四時旺相 mapping turns a line's element "
            "relations into a weak/strong verdict (L-04); "
            "assess_wangshuai abstains."
        ),
    },
)

# --- L-07 evidence: month-break motion / un-breaking ------------------
# No registered basis for either a moving/static distinction in
# month-break severity or any un-breaking rule (evidence pack 04 §3.4,
# re-checked this batch). Located but unregistered discussions exist;
# they are recorded here as candidates with their dispute noted, never
# as rules.
YUEPO_MOTION_EVIDENCE = {
    "moving_static_distinction": {
        "status": "no_registered_basis",
        "searched": "38 registered sections (evidence pack 04 §3.4, re-checked 2026-11-27)",
        "needed": (
            "A registered classical passage stating whether a moving "
            "month-break line is treated differently from a static one, "
            "with its own section id and locatable text."
        ),
        "located_candidates": (
            "卜筮正宗 line 998 [28875,28985): 月破之爻动者亦能生克他爻；"
            "增删卜易 line 1251: 鬼臨月破﹐不動者不驗；"
            "增删卜易 line 2307: 惟世與官星空破而動者，勿以此斷；"
            "增删卜易 line 1977: 動而破者亦應實破之日。"
            "All located_unregistered; none is a registered section."
        ),
    },
    "yuepo_unbreaking": {
        "status": "no_registered_basis",
        "searched": "38 registered sections (evidence pack 04 §7, re-checked 2026-11-27)",
        "needed": (
            "A registered classical passage stating whether combining or "
            "clashing a month-break line un-breaks it (出月/值日/合可解), "
            "with its own section id and locatable text."
        ),
        "located_candidates": (
            "卜筮正宗 line 998 [28875,28985): 目下雖破出月不破矣，值日不破矣，"
            "月破最喜逢合填實；line 1060 [33112,33179): 出月值日合補亦能吉能兇，"
            "with the dispute 張星元言月破無可解，概以凶推；"
            "line 2749 [78523,78577): 破爻有出破填實合破之法。"
            "All located_unregistered; the dispute is unadjudicated."
        ),
    },
}


def moving_yao_evidence():
    """Return a deep copy of the L-05 evidence record."""
    return deepcopy(MOVING_YAO_EVIDENCE)


def yuepo_motion_evidence():
    """Return a deep copy of the L-07 evidence record."""
    return deepcopy(YUEPO_MOTION_EVIDENCE)


def _require_yao_values(yao_values):
    if (
        not isinstance(yao_values, (list, tuple))
        or len(yao_values) != 6
        or any(type(v) is not int or v not in (6, 7, 8, 9) for v in yao_values)
    ):
        raise ValueError("yao_values must be six integer yao values 6/7/8/9, bottom to top")
    return list(yao_values)


def _require_six_branches(line_branches, name="line_branches"):
    if (
        not isinstance(line_branches, (list, tuple))
        or len(line_branches) != 6
        or any(not isinstance(b, str) or b not in BRANCH_ELEMENTS for b in line_branches)
    ):
        raise ValueError("%s must be six earthly branches, bottom to top" % name)
    return list(line_branches)


def _require_branch(branch, name="branch"):
    if not isinstance(branch, str) or branch not in BRANCH_ELEMENTS:
        raise ValueError("%s must be one earthly branch" % name)
    return branch


def _require_day_ganzhi(day_ganzhi):
    from .liuyao_yongshen import _YUEJIAN_RICHEN_CYCLE

    if not isinstance(day_ganzhi, str) or day_ganzhi not in _YUEJIAN_RICHEN_CYCLE:
        raise ValueError("day_ganzhi must be a sixty-cycle ganzhi string")
    return day_ganzhi


def moving_lines(yao_values):
    """Return the positions (1-6, bottom to top) of the moving lines.

    A line moves exactly when its yao value is 6 (老阴) or 9 (老阳) --
    the same rule the chart layer uses ("六爻不動則不變﹐動則必變", s001).
    Raises ValueError on malformed input.
    """
    values = _require_yao_values(yao_values)
    return [i + 1 for i, v in enumerate(values) if v in (6, 9)]


def line_motion(yao_values):
    """Return per-line motion facts for six yao values, bottom to top.

    Each line carries its value and ``moving`` (True for 6/9, False for
    7/8). Structure only: no effect is attached to a moving line.
    Raises ValueError on malformed input.
    """
    values = _require_yao_values(yao_values)
    return [
        {"position": i + 1, "value": v, "moving": v in (6, 9)}
        for i, v in enumerate(values)
    ]


def changed_line_facts(yao_values, original_branches, changed_branches):
    """Compare original vs changed line branches, per line, bottom to top.

    ``original_branches`` / ``changed_branches`` are the six line
    branches of the original / changed hexagrams as computed by the
    chart layer (the caller supplies them; this module never derives a
    changed hexagram). Each line records ``moving`` (from the yao
    value), ``original_branch``, ``changed_branch`` and ``branch_changed``
    (whether the two branches differ).

    A branch difference does NOT by itself imply the line moved: when a
    whole trigram flips, the changed hexagram's najia is recomputed for
    all its lines, so static lines can show a different changed branch
    (evidence-pack-05 case C1: lines 4 and 5 are static yet their
    changed branches differ). ``branch_changed`` is a fact, not a
    motion verdict. ``effect`` and ``verdict`` are always None.
    Raises ValueError on malformed input.
    """
    values = _require_yao_values(yao_values)
    original = _require_six_branches(original_branches, "original_branches")
    changed = _require_six_branches(changed_branches, "changed_branches")
    lines = [
        {
            "position": i + 1,
            "value": v,
            "moving": v in (6, 9),
            "original_branch": o,
            "changed_branch": c,
            "branch_changed": o != c,
        }
        for i, (v, o, c) in enumerate(zip(values, original, changed))
    ]
    return {
        "yao_values": values,
        "lines": lines,
        "moving_lines": [ln["position"] for ln in lines if ln["moving"]],
        "branch_changed_lines": [ln["position"] for ln in lines if ln["branch_changed"]],
        "effect": None,
        "verdict": None,
        "note": (
            "动爻与变爻结构事实：动静由爻值定（6/9 动）；变爻支变与否是"
            "整卦纳甲重排的事实，支变不等于爻动；不立回头生克效力。"
        ),
    }


def assess_moving_effect(structure):
    """Assess the effect of moving / changed lines. ABSTAINS.

    This is the EFFICACY layer for L-05, deliberately separate from the
    structure layer: it takes a ``changed_line_facts`` (or
    ``line_motion``) result and returns an explicit abstention, never
    an effect verdict. No registered rule turns a moving line into a
    generating / controlling effect on another line, and the 回头生/
    回头克 sentences (增删卜易 lines 852-853) are located but
    unregistered. ``effect`` and ``verdict`` are always None; ``status``
    is always ``insufficient_basis`` and the unmet conditions are
    listed. Raises ValueError when the input is not a structure result.
    """
    if not isinstance(structure, dict) or "lines" not in structure:
        raise ValueError("assess_moving_effect requires a line motion structure result")
    return {
        "status": "insufficient_basis",
        "effect": None,
        "verdict": None,
        "moving_lines": (
            structure.get("moving_lines")
            if "moving_lines" in structure
            else [ln["position"] for ln in structure["lines"] if ln.get("moving")]
        ),
        "unmet_conditions": (
            "registered_moving_line_efficacy_rule",
            "registered_return_effect_rule",
            "approved_useful_god_mapping",
        ),
        "note": (
            "动爻效力层：动静与变爻支变只是结构事实；回头生克效力规则"
            "未登记、用神映射未批准，故暂不可判。"
        ),
    }


def dark_moving_structure(line_branches, yao_values, month_branch, day_ganzhi):
    """Report the 暗動 (s010) structure conditions per line, bottom to top.

    s010: "爻之旺而靜者沖之則為暗動" -- a line is dark-moving only when
    it is strong (旺) AND static AND clashed. This function reports the
    three conditions as facts: ``is_static`` (from the yao value),
    ``clashes_day`` / ``clashes_month`` (r006 clash facts) and
    ``strong`` (always None: no registered wangshuai mapping can decide
    it, L-04). ``dark_moving`` is therefore always None (undetermined),
    never forced to True or False. Raises ValueError on malformed input.
    """
    branches = _require_six_branches(line_branches)
    values = _require_yao_values(yao_values)
    month = _require_branch(month_branch, "month_branch")
    day = _require_day_ganzhi(day_ganzhi)
    day_clashes = day_clash_flags(branches, day)
    month_clashes = month_break_flags(branches, month)
    lines = []
    for position, (branch, value, dc, mc) in enumerate(
        zip(branches, values, day_clashes, month_clashes), start=1
    ):
        lines.append(
            {
                "position": position,
                "line_branch": branch,
                "yao_value": value,
                "is_static": yao_is_static(value),
                "clashes_day": dc,
                "clashes_month": mc,
                "strong": None,
                "dark_moving": None,
                "status": "undetermined_strong_unknown",
            }
        )
    return {
        "line_branches": branches,
        "month_branch": month,
        "day_ganzhi": day,
        "lines": lines,
        "dark_moving_lines": [],
        "undetermined_lines": [ln["position"] for ln in lines],
        "verdict": None,
        "note": (
            "暗動结构条件：静与冲可算，旺不可算（依赖未建的 L-04 旺衰层）；"
            "旺未知时暗動判未定，不强行判定。"
        ),
    }


def yuepo_motion_structure(line_branches, month_branch, yao_values):
    """Classify each line by month-break x motion, bottom to top.

    Each line records its month-break flag (r019 + r006 clash fact),
    its motion (yao value 6/9), and ``motion_class``: one of
    "broken_moving" / "broken_static" / "unbroken_moving" /
    "unbroken_static". These classes are STRUCTURE facts only: no
    severity distinction between a moving and a static broken line is
    asserted, and no un-breaking is computed -- both lack any
    registered basis (see YUEPO_MOTION_EVIDENCE).
    ``distinction_verdict`` and ``unbreaking`` are always None.
    Raises ValueError on malformed input.
    """
    branches = _require_six_branches(line_branches)
    month = _require_branch(month_branch, "month_branch")
    values = _require_yao_values(yao_values)
    breaks = month_break_flags(branches, month)
    lines = []
    for position, (branch, broken, value) in enumerate(
        zip(branches, breaks, values), start=1
    ):
        moving = not yao_is_static(value)
        if broken and moving:
            motion_class = "broken_moving"
        elif broken:
            motion_class = "broken_static"
        elif moving:
            motion_class = "unbroken_moving"
        else:
            motion_class = "unbroken_static"
        lines.append(
            {
                "position": position,
                "line_branch": branch,
                "yao_value": value,
                "month_break": broken,
                "moving": moving,
                "motion_class": motion_class,
            }
        )
    return {
        "line_branches": branches,
        "month_branch": month,
        "lines": lines,
        "broken_moving_lines": [ln["position"] for ln in lines if ln["motion_class"] == "broken_moving"],
        "broken_static_lines": [ln["position"] for ln in lines if ln["motion_class"] == "broken_static"],
        "distinction_verdict": None,
        "unbreaking": None,
        "unbreaking_status": "no_registered_basis",
        "verdict": None,
        "note": (
            "月破动静结构区分：破×动四类只作事实分类；动静轻重区别与"
            "解破条件均无已登记依据，不立效力、不算解破。"
        ),
    }
