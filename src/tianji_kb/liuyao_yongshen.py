"""Liuyao limited useful-god framework — FOUNDATION ONLY.

Adjudication basis (user decision 2026-11-17, Liuyao ask = B): the LIMITED
useful-god rule-system development direction is APPROVED. Specific
useful-god mappings need per-item evidence review + SEPARATE approval and
must NEVER be implemented without that approval. This module builds ONLY
the framework foundation. Every other unadjudicated doctrine rule
continues to abstain (fail-closed).

What this module DOES:
- A fixed taxonomy of neutral question-type categories (``QUESTION_TYPES``),
  each with a name, a description, and an evidence record. The taxonomy
  does NOT group any type under a six-relative (六亲) category yet: the
  ``relative_category`` field is a pending-review slot, None for every
  type in this foundation, and may only be set after per-item classical
  evidence is registered through the governance chain and separately
  approved. A grouping, even if approved later, is a category for
  structured input, NOT a useful-god mapping.
- A validated structured-input schema (``validate_question_input``).
- An abstention contract (``assess``): the framework MUST refuse — return
  an explicit abstention, never a verdict — whenever no approved
  useful-god mapping exists, evidence is insufficient, or the input is
  incomplete. In this foundation the mapping registry is EMPTY, so every
  assessment abstains.
- The useful-god mapping registry (``USEFUL_GOD_MAPPINGS``), which exists
  as a data structure but is EMPTY. No mapping is applied anywhere.
- A definition-only registry for yuejian / richen
  (``YUEJIAN_RICHEN_DEFINITIONS``) plus ``record_month_day_context``:
  user adjudication 2026-11-25 Q14 keeps r008/r009 as definitions with
  no executable mapping; the only calibre is recording the month branch
  and day ganzhi verbatim, with ``derived_conclusions`` always None.

What this module NEVER does (hard limits):
- Implement ZERO specific useful-god mappings (never "for a career
  question, the useful god is X").
- Output any 用神 / 旺衰 / 应期 / 成败 verdict anywhere.
- Send the free-text question to the liuyao engine. The free-text
  question is page context only (the ask page already keeps it local);
  ``validate_question_input`` REJECTS any free-text question field.
- Change the existing liuyao chart computation (``operations.liuyao_chart``
  / ``operations.liuyao``). This module is stdlib Python plus the
  constant-only ``operations.liuyao.element_relation`` callable (which
  reads no sealed data), so its tests run locally and in public CI.

Batch 3 stage 2 (TJ-0424, L1-L5 DECIDED 2026-11-25 -- nothing here
decides any of them; the decisions only lift the blocks):
- L4: yuejian/richen STRUCTURE rules are now implemented
  (``month_day_structure``, ``line_month_day_structure``): month/day
  elements and per-line same-as / clash-against month and day facts,
  all computable from registered tables. The wangshuai EFFICACY layer
  is separate (``assess_wangshuai``): it abstains with explicit unmet
  conditions, because no registered 四時旺相 mapping exists and the
  efficacy must never be read off a structure hit.
- L5: ripo's conditional rule lives in ``liuyao_empty_break``; this
  module records the split (see OUT_OF_SCOPE).
- L3: chukong/tianshi/un-breaking evidence calibre lives in
  ``liuyao_empty_break.EMPTY_HANDLING_EVIDENCE`` (no basis found,
  nothing implemented).
- L1: sealed-Golden admission is approved but is a sealed-governance
  step outside this batch's file boundary; recorded, not executed.
- Yuan-shen / ji-shen / chou-shen STRUCTURE framework
  (``roles_for_element``, ``line_roles_relative_to_element``): five-element
  role facts relative to a caller-supplied useful-god ELEMENT only.
  No mapping (which line IS the useful god) and no efficacy: per-item
  classical evidence for these roles (r013-r018) is still unreviewed,
  so every role record carries status ``framework_only``.
- Useful-god framework STRUCTURE (``MAPPING_SLOT_SCHEMA``,
  ``mapping_slot`` / ``list_mapping_slots``, ``framework_status``):
  the shape question type -> six-relative role -> candidate lines,
  with every slot's evidence status made explicit. The registry stays
  EMPTY and ``assess()`` still abstains for all 8 types; the framework
  must never be reported as implemented useful-god selection.
- Strength/weakness STRUCTURAL FACTS
  (``line_relations_to_month_day``): per-line element vs month-branch
  and day-branch element relations (生克比和), enumerated as facts
  only -- no 旺衰 verdict, no 吉凶, ``conclusion`` / ``wangshuai`` /
  ``verdict`` always None. Yuejian/richen stay definition-only
  (``record_month_day_context`` unchanged); the four-season wang/xiang
  chapter is unregistered and the xing/hai/earth disputes are
  unadjudicated (L4), so no per-item evidence gathering is started.
- Explicit out-of-scope record (``OUT_OF_SCOPE``): chukong / tianshi
  and yuepo un-breaking (L3), ripo r020 (L5 -- its own "衰而靜"
  precondition, never derived from yuepo), yongshen / yuan-shen /
  ji-shen / chou-shen / yingqi (per-item approval), and sealed-Golden
  admission of proposed B1-B3/E1/E2 (L1, a sealed-governance step
  outside this batch's file boundary). None of these is implemented.

Evidence model: each question type carries ``source`` / ``version`` /
``locator`` pointing at the registered chart variant
(``liuyao/jingfang-eight-palaces-v1``) that computes the six relatives,
plus a ``classical_citation`` slot. The per-type classical passage must
be registered through the governance chain
(Source -> RAW -> Quarantine -> Review -> Canonical -> Terms/Rules ->
Evidence) before any mapping for that type can be approved; until then
``classical_citation`` is None and the type's ``status`` is
``framework_only``. A type without verified evidence cannot be used for
a mapping, and a type without an approved mapping always abstains.
"""

from copy import deepcopy
from datetime import datetime

from .operations.liuyao import branch_relation as _branch_relation
from .operations.liuyao import element_relation as _element_relation

__all__ = [
    "BRANCH_ELEMENTS",
    "MAPPING_SLOT_SCHEMA",
    "OUT_OF_SCOPE",
    "QUESTION_TYPES",
    "SIX_RELATIVE_ROLES",
    "USEFUL_GOD_MAPPINGS",
    "YUEJIAN_RICHEN_DEFINITIONS",
    "element_of_branch",
    "element_relation_between",
    "framework_status",
    "get_useful_god_mapping",
    "line_month_day_structure",
    "line_relations_to_month_day",
    "line_roles_relative_to_element",
    "list_mapping_slots",
    "list_question_types",
    "mapping_slot",
    "month_day_structure",
    "record_month_day_context",
    "assess_wangshuai",
    "roles_for_element",
    "validate_question_input",
    "assess",
]

# The registered chart variant this framework builds on. The chart
# (jingfang-eight-palaces-v1) computes the six relatives per line; the
# question taxonomy groups questions by that same six-relative system.
CHART_VARIANT = "liuyao/jingfang-eight-palaces-v1"
CHART_VARIANT_TITLE = "京房八宫"

# Free-text question fields are NEVER part of the structured input: the
# question text is page context only and must not reach the engine.
_FORBIDDEN_TEXT_FIELDS = ("question_text", "question", "text", "query")

# Allowed structured-input fields (mirrors the ask scenario contract:
# value + yao_values, optional zone; plus the framework's own fields).
_ALLOWED_FIELDS = frozenset(
    ("question_type", "yao_values", "value", "zone", "traditional_role")
)

# The six-relative grouping of a question type, if any. In this
# foundation EVERY type is None: no grouping has been approved for any
# type, because each type's classical_citation is still None and the
# user approved only the framework direction, not any per-item
# six-relative association. A grouping may only be set after per-item
# evidence review + SEPARATE approval; until then a None category means
# the grouping is pending review, and such a type always abstains with
# reason "ambiguous_category". A grouping, even if approved later, is a
# CATEGORY for structured input, not a useful-god mapping: it never says
# which line is the useful god for a specific question, and never what
# verdict follows.
QUESTION_TYPES = {
    "career": {
        "id": "career",
        "name": "事业官职",
        "description": "求官、升职、事业发展类问题。",
        "relative_category": None,
        "relative_category_note": (
            "事业官职类问题的六亲归属尚未审定，基础层不预设；"
            "须待逐项证据审核与另行批准后方可确定。"
        ),
        "evidence": {
            "source": CHART_VARIANT,
            "source_title": CHART_VARIANT_TITLE,
            "version": "v1",
            "locator": "六亲·未定（待审核）",
            "classical_citation": None,
            "status": "framework_only",
        },
    },
    "wealth": {
        "id": "wealth",
        "name": "求财经营",
        "description": "求财、生意、投资经营类问题。",
        "relative_category": None,
        "relative_category_note": (
            "求财经营类问题的六亲归属尚未审定，基础层不预设；"
            "须待逐项证据审核与另行批准后方可确定。"
        ),
        "evidence": {
            "source": CHART_VARIANT,
            "source_title": CHART_VARIANT_TITLE,
            "version": "v1",
            "locator": "六亲·未定（待审核）",
            "classical_citation": None,
            "status": "framework_only",
        },
    },
    "marriage": {
        "id": "marriage",
        "name": "婚姻感情",
        "description": "婚姻、感情、婚恋类问题。",
        "relative_category": None,
        "relative_category_note": (
            "婚姻感情的六亲归属取决于问者传统口径（男问妻取妻财，女问夫取官鬼），"
            "基础层不预设；须待逐项证据审核与另行批准后方可确定。"
        ),
        "evidence": {
            "source": CHART_VARIANT,
            "source_title": CHART_VARIANT_TITLE,
            "version": "v1",
            "locator": "六亲·未定（待传统口径）",
            "classical_citation": None,
            "status": "framework_only",
        },
    },
    "health": {
        "id": "health",
        "name": "疾病健康",
        "description": "疾病、健康、医药类问题。",
        "relative_category": None,
        "relative_category_note": (
            "疾病健康的六亲归属取决于所问焦点（疾病本身与医药取向不同），"
            "基础层不预设；须待逐项证据审核与另行批准后方可确定。"
        ),
        "evidence": {
            "source": CHART_VARIANT,
            "source_title": CHART_VARIANT_TITLE,
            "version": "v1",
            "locator": "六亲·未定（待所问焦点）",
            "classical_citation": None,
            "status": "framework_only",
        },
    },
    "examination": {
        "id": "examination",
        "name": "考试求学",
        "description": "考试、升学、文书成绩类问题。",
        "relative_category": None,
        "relative_category_note": (
            "考试求学类问题的六亲归属尚未审定，基础层不预设；"
            "须待逐项证据审核与另行批准后方可确定。"
        ),
        "evidence": {
            "source": CHART_VARIANT,
            "source_title": CHART_VARIANT_TITLE,
            "version": "v1",
            "locator": "六亲·未定（待审核）",
            "classical_citation": None,
            "status": "framework_only",
        },
    },
    "legal": {
        "id": "legal",
        "name": "官司诉讼",
        "description": "官司、诉讼、纠纷类问题。",
        "relative_category": None,
        "relative_category_note": (
            "官司诉讼类问题的六亲归属尚未审定，基础层不预设；"
            "须待逐项证据审核与另行批准后方可确定。"
        ),
        "evidence": {
            "source": CHART_VARIANT,
            "source_title": CHART_VARIANT_TITLE,
            "version": "v1",
            "locator": "六亲·未定（待审核）",
            "classical_citation": None,
            "status": "framework_only",
        },
    },
    "travel": {
        "id": "travel",
        "name": "出行远行",
        "description": "出行、远行、迁徙类问题。",
        "relative_category": None,
        "relative_category_note": (
            "出行远行以世爻/应爻为体，非六亲单类，基础层不预设；"
            "须待逐项证据审核与另行批准后方可确定。"
        ),
        "evidence": {
            "source": CHART_VARIANT,
            "source_title": CHART_VARIANT_TITLE,
            "version": "v1",
            "locator": "六亲·未定（世爻/应爻为体）",
            "classical_citation": None,
            "status": "framework_only",
        },
    },
    "lost_property": {
        "id": "lost_property",
        "name": "失物寻物",
        "description": "失物、寻物类问题。",
        "relative_category": None,
        "relative_category_note": (
            "失物寻物类问题的六亲归属尚未审定，基础层不预设；"
            "须待逐项证据审核与另行批准后方可确定。"
        ),
        "evidence": {
            "source": CHART_VARIANT,
            "source_title": CHART_VARIANT_TITLE,
            "version": "v1",
            "locator": "六亲·未定（待审核）",
            "classical_citation": None,
            "status": "framework_only",
        },
    },
}

# Useful-god mapping registry. EMPTY by design: every specific mapping
# (question type -> useful god) needs per-item evidence review + SEPARATE
# approval and must NEVER be added without that approval. Nothing in
# this module reads a mapping, and assess() never returns one.
USEFUL_GOD_MAPPINGS = {}

# --- Yuejian / richen: definition registration ONLY (Q14) -------------
# User adjudication 2026-11-25 Q14 (TJ-0424 batch 2, P1 liuyao):
# liuyao.rule.r008 (yuejian / 月建) and liuyao.rule.r009 (richen / 日辰)
# keep their current definitions while the search for an executable
# basis continues; they are NOT permanently closed, but they have NO
# executable calibre today, so NO mapping is built from them. The
# minimum calibre is recording the inputs verbatim -- nothing is
# derived from them. The two definition sentences below are the
# registered excerpts, quoted from the evidence pack:
# - r008 / liuyao.section.s008 (增删卜易, chars [19189,19212)):
#   「月將卽是月建又為月令。掌一月之權﹐司三旬之令。」
# - r009 / liuyao.section.s009 (增删卜易, chars [21358,21374)):
#   「日辰為六爻之主宰﹐司四時之旺相。」
# Both rules are partially_structured with EMPTY operation parameters,
# no Phase2 rule, no Phase2 evidence record, and no Golden. The only
# registered yuejian effect sentence (s012, on fei/fu shen) belongs to
# r011/r012 (a later batch), and the richen-adjacent ripo sentence
# (s021) belongs to r020 (a later batch); neither is used here.
YUEJIAN_RICHEN_DEFINITIONS = {
    "yuejian": {
        "rule_id": "liuyao.rule.r008",
        "term": "liuyao.term.t008",
        "name": "月建",
        "definition": "月將卽是月建又為月令。掌一月之權﹐司三旬之令。",
        "section_id": "liuyao.section.s008",
        "locator": "增删卜易 chars [19189,19212)",
        "execution_status": "partially_structured",
        "status": "definition_only",
        "mapping": None,
    },
    "richen": {
        "rule_id": "liuyao.rule.r009",
        "term": "liuyao.term.t009",
        "name": "日辰",
        "definition": "日辰為六爻之主宰﹐司四時之旺相。",
        "section_id": "liuyao.section.s009",
        "locator": "增删卜易 chars [21358,21374)",
        "execution_status": "partially_structured",
        "status": "definition_only",
        "mapping": None,
    },
}

# Local sixty-cycle tables (stdlib only, no data file): this module stays
# pure stdlib so its tests run locally and in public CI. The strings
# below are the same fixed traditional symbols as foundations.CYCLE.
_YUEJIAN_RICHEN_STEMS = "甲乙丙丁戊己庚辛壬癸"
_YUEJIAN_RICHEN_BRANCHES = "子丑寅卯辰巳午未申酉戌亥"
_YUEJIAN_RICHEN_CYCLE = tuple(
    _YUEJIAN_RICHEN_STEMS[i % 10] + _YUEJIAN_RICHEN_BRANCHES[i % 12]
    for i in range(60)
)


def record_month_day_context(month_branch, day_ganzhi):
    """Record the month-branch / day-ganzhi context verbatim (Q14).

    Minimum calibre for yuejian/richen: the inputs are recorded exactly
    as given, with their definition records attached, and NO conclusion
    is derived -- ``derived_conclusions`` is always None. There is no
    wang/shuai (旺衰), sheng/ke (生克), or yongshen conclusion here,
    because no registered calibre exists for one. Changing the month
    branch changes only the recorded ``month_branch`` field; no line
    fact changes (cf. evidence-pack proposed Golden M1/M2, D1/D2).
    Raises ValueError for a month branch outside the twelve branches
    or a day ganzhi outside the sixty-cycle.
    """
    # Exact single-branch check: ``in`` on the branches string is a
    # substring test, so "" and contiguous pairs ("寅卯", "子丑") would
    # wrongly pass. Only exactly one legal branch character is accepted.
    if (not isinstance(month_branch, str) or len(month_branch) != 1
            or month_branch not in _YUEJIAN_RICHEN_BRANCHES):
        raise ValueError("month_branch must be one earthly branch")
    if not isinstance(day_ganzhi, str) or day_ganzhi not in _YUEJIAN_RICHEN_CYCLE:
        raise ValueError("day_ganzhi must be a sixty-cycle ganzhi string")
    return {
        "month_branch": month_branch,
        "day_ganzhi": day_ganzhi,
        "yuejian": deepcopy(YUEJIAN_RICHEN_DEFINITIONS["yuejian"]),
        "richen": deepcopy(YUEJIAN_RICHEN_DEFINITIONS["richen"]),
        "derived_conclusions": None,
        "note": (
            "月建/日辰仅作定义登记与原样记录；无旺衰、生克、用神结论。"
            "可执行依据仍在寻找中，不作为永久关闭事项。"
        ),
    }


def list_question_types():
    """Return a deep copy of the question-type taxonomy."""
    return deepcopy(QUESTION_TYPES)


def get_useful_god_mapping(question_type):
    """Return the approved useful-god mapping for a question type.

    Always None in this foundation: the registry is empty. A mapping
    may only be added after per-item evidence review + separate
    approval; until then no mapping is applied to any type.
    """
    return USEFUL_GOD_MAPPINGS.get(question_type)


def _require_iso_datetime(value):
    if not isinstance(value, str) or not value.strip():
        raise ValueError("value must be a non-empty ISO datetime string")
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError:
        raise ValueError("value must be a valid ISO datetime string") from None
    return parsed


def validate_question_input(data):
    """Validate structured liuyao question input; return a normalized copy.

    Required: ``question_type`` (in the taxonomy), ``yao_values`` (six
    ints in {6,7,8,9}, bottom to top), ``value`` (ISO datetime string).
    Optional: ``zone`` (string), ``traditional_role`` ("male"/"female").

    Raises ValueError for missing/invalid fields, for any unknown key,
    and — explicitly — for any free-text question field: the question
    text is page context only and must never be sent to the engine.
    """
    if not isinstance(data, dict):
        raise ValueError("question input must be a JSON object")
    for field in _FORBIDDEN_TEXT_FIELDS:
        if field in data:
            raise ValueError(
                "free-text question must not be sent to the liuyao engine; "
                "the question text is page context only"
            )
    unknown = sorted(set(data) - _ALLOWED_FIELDS)
    if unknown:
        raise ValueError(
            "question input fields do not match the reviewed contract: "
            + ", ".join(unknown)
        )
    question_type = data.get("question_type")
    if not isinstance(question_type, str) or not question_type:
        raise ValueError("question_type is required")
    if question_type not in QUESTION_TYPES:
        raise ValueError("unknown question_type: %s" % question_type)
    yao_values = data.get("yao_values")
    if (
        not isinstance(yao_values, (list, tuple))
        or len(yao_values) != 6
        or any(type(v) is not int or v not in (6, 7, 8, 9) for v in yao_values)
    ):
        raise ValueError("yao_values must be six integer yao values 6/7/8/9, bottom to top")
    _require_iso_datetime(data.get("value"))
    zone = data.get("zone")
    if zone is not None and (not isinstance(zone, str) or not zone.strip()):
        raise ValueError("zone must be a non-empty string when present")
    traditional_role = data.get("traditional_role")
    if traditional_role is not None and traditional_role not in ("male", "female"):
        raise ValueError("traditional_role must be 'male' or 'female' when present")
    normalized = {
        "question_type": question_type,
        "yao_values": list(yao_values),
        "value": data["value"],
    }
    if zone is not None:
        normalized["zone"] = zone
    if traditional_role is not None:
        normalized["traditional_role"] = traditional_role
    return normalized


def assess(data):
    """Assess a structured liuyao question. FOUNDATION: always abstains.

    The input is validated first (invalid input raises ValueError — an
    input error, not an abstention). A valid input always returns an
    explicit abstention: ``status`` is "abstained", ``verdict`` and
    ``useful_god`` are None. No 用神 / 旺衰 / 应期 / 成败 verdict is
    ever produced, because the mapping registry is empty and no
    question type has a verified classical citation plus an approved
    mapping yet.

    Abstention reasons (first match wins):
    - "unknown_question_type": the type is not in the taxonomy
      (unreachable after validation; kept for defence in depth).
    - "ambiguous_category": the type's six-relative grouping is
      unresolved in the foundation — in this foundation every type
      abstains with this reason, because no grouping has been approved
      for any type yet (each type's classical citation is still None).
    - "no_approved_mapping": retained for the future state where a
      type's grouping has been approved but no useful-god mapping has;
      unreachable in this foundation because no grouping is approved.
    """
    normalized = validate_question_input(data)
    question_type = normalized["question_type"]
    type_record = QUESTION_TYPES.get(question_type)
    if type_record is None:
        reason = "unknown_question_type"
        evidence = None
    elif type_record["relative_category"] is None:
        reason = "ambiguous_category"
        evidence = deepcopy(type_record["evidence"])
    else:
        reason = "no_approved_mapping"
        evidence = deepcopy(type_record["evidence"])
    return {
        "status": "abstained",
        "reason": reason,
        "question_type": question_type,
        "verdict": None,
        "useful_god": None,
        "evidence": evidence,
        "evidence_status": (
            evidence["status"] if evidence is not None else "unknown_question_type"
        ),
    }

# --- Batch 3: useful-god framework structure (slots, not mappings) ---
# The framework shape is question type -> six-relative role ->
# candidate lines. In this batch every slot is EMPTY: no grouping is
# approved for any type and no mapping exists, so every slot reports
# its evidence status explicitly instead of silently implying a
# mapping. The schema below is the contract a FUTURE approved mapping
# entry must satisfy (per-item evidence review + separate approval);
# it is a declaration, not an implementation of any mapping.

# The six-relative roles the chart variant computes (najia_v1
# six_relatives). Listed here as structural slots only: no question
# type is assigned to any role in this batch.
SIX_RELATIVE_ROLES = ("父母", "兄弟", "子孙", "妻财", "官鬼")

# Required fields of a useful-god mapping entry, IF one is ever
# approved. "candidate_lines" names line positions 1-6 (bottom to
# top) that hold the useful god's role; it stays None until a mapping
# is approved. No entry exists today, so nothing in this module
# constructs one.
MAPPING_SLOT_SCHEMA = {
    "question_type": "one of QUESTION_TYPES (8 types)",
    "relative_role": "one of SIX_RELATIVE_ROLES, or 'shi_ying' for 世/应-bodied types",
    "candidate_lines": "line positions 1-6 (bottom to top) holding the role; None until approved",
    "evidence": {
        "source": "registered chart variant or classical source",
        "version": "source version",
        "locator": "locatable text position",
        "classical_citation": "registered classical passage (None until registered)",
        "status": "'approved' only after per-item evidence review + separate approval",
    },
    "approval": {
        "approved_by": "user adjudication reference",
        "adjudication_ref": "e.g. round-2 L-number or Q-number",
    },
}


def mapping_slot(question_type):
    """Return the useful-god mapping slot for a question type.

    The slot is the pure structural mapping question type ->
    six-relative role -> candidate lines, WITH its evidence status.
    In this batch every slot has ``relative_role`` None,
    ``candidate_lines`` None, ``mapping`` None and evidence status
    ``no_approved_mapping``: no grouping and no mapping has been
    approved for any type. Raises ValueError for an unknown type.
    """
    if not isinstance(question_type, str) or question_type not in QUESTION_TYPES:
        raise ValueError("unknown question_type: %r" % (question_type,))
    type_record = QUESTION_TYPES[question_type]
    return {
        "question_type": question_type,
        "name": type_record["name"],
        "relative_role": type_record["relative_category"],
        "candidate_lines": None,
        "mapping": USEFUL_GOD_MAPPINGS.get(question_type),
        "evidence_status": "no_approved_mapping",
        "evidence": deepcopy(type_record["evidence"]),
        "adjudication": (
            "Per-item evidence review + separate approval required; "
            "no mapping approved. L1-L5 decided 2026-11-25; per-item "
            "mapping approval still required."
        ),
    }


def list_mapping_slots():
    """Return the mapping slot for every question type (8 slots)."""
    return [mapping_slot(type_id) for type_id in QUESTION_TYPES]


def framework_status():
    """Return a summary of the useful-god framework state.

    Counts only what exists: 8 question types, 0 approved groupings,
    0 approved mappings. The framework is structure, not selection --
    ``assess()`` still abstains for every type.
    """
    grouped = sum(
        1
        for record in QUESTION_TYPES.values()
        if record["relative_category"] is not None
    )
    return {
        "question_types": len(QUESTION_TYPES),
        "six_relative_roles": list(SIX_RELATIVE_ROLES),
        "types_with_approved_grouping": grouped,
        "approved_mappings": len(USEFUL_GOD_MAPPINGS),
        "mapping_registry_empty": len(USEFUL_GOD_MAPPINGS) == 0,
        "assess_behavior": "always_abstains",
        "research_only": True,
        "public": False,
        "ai": False,
        "decided_adjudications": ("L1", "L2", "L3", "L4", "L5"),
        "decided_adjudications_date": "2026-11-25",
        "pending_adjudications": ("per-item mapping approval",),
    }


# --- Batch 3: explicitly out of scope (recorded, NOT implemented) ----
# Each entry names the adjudication that gates it. "implemented" is
# False for every entry; the test suite locks that no callable for any
# of these exists in this module.
OUT_OF_SCOPE = {
    "chukong_tianshi": {
        "adjudication": "L3 — decided 2026-11-25",
        "implemented": False,
        "reason": (
            "出空/填实/值日/合住/冲开 handling of an empty line has no "
            "registered section in the library; L3 evidence construction "
            "(tianji_kb.liuyao_empty_break.EMPTY_HANDLING_EVIDENCE) "
            "found no basis, so nothing is implemented and no efficacy "
            "is inferred from the definition of emptiness."
        ),
    },
    "yuepo_unbreaking": {
        "adjudication": "L3 — decided 2026-11-25",
        "implemented": False,
        "reason": (
            "r019 / zs05 say nothing about un-breaking a month-break "
            "line, and L3 evidence construction found no registered "
            "basis; no such rule is computed."
        ),
    },
    "ripo": {
        "adjudication": "L5 — decided 2026-11-25",
        "rule": "liuyao.rule.r020",
        "implemented": False,
        "conditional_rule": (
            "tianji_kb.liuyao_empty_break.day_break_assessment"
        ),
        "reason": (
            "日破 definition carries its own '衰而靜' precondition and "
            "is NOT parallel to yuepo; it must not be derived from "
            "month-break. The CONDITIONAL rule is implemented in "
            "liuyao_empty_break (clash + static + explicitly supplied "
            "weak, else undetermined); this module implements no ripo "
            "rule of its own."
        ),
    },
    "yuejian_richen_executable_mapping": {
        "adjudication": "L4 (Q14) — decided 2026-11-25",
        "implemented": False,
        "reason": (
            "月建/日辰 stay definition-only for EFFICACY: the 四時旺相 "
            "chapter text is unregistered and the xing/hai/earth "
            "disputes are unadjudicated, so no旺衰 verdict is built "
            "from them (assess_wangshuai abstains). The STRUCTURE rules "
            "(month_day_structure, line_month_day_structure) ARE "
            "implemented, separately from efficacy."
        ),
    },
    "yongshen_yuanshen_jishen_choushen_yingqi": {
        "adjudication": "per-item approval; L4/L5 decided 2026-11-25",
        "implemented": False,
        "reason": (
            "Useful god / yuan-shen / ji-shen / chou-shen and yingqi "
            "have no approved mapping; assess() still abstains for "
            "every question type. A roles STRUCTURE framework "
            "(roles_for_element: element relations only, no efficacy) "
            "now exists; which line IS the useful god, and any effect "
            "of a role, remain unapproved."
        ),
    },
    "sealed_golden_admission_b1_b2_b3_e1_e2": {
        "adjudication": "L1 — decided 2026-11-25",
        "implemented": False,
        "reason": (
            "Admitting proposed Golden B1-B3/E1/E2 to the sealed "
            "phase2_golden.json is APPROVED, but admission itself is a "
            "sealed-governance step outside this batch's file boundary "
            "and is NOT executed here; the cases stay verified only as "
            "public tests until the sealed process runs."
        ),
    },
}


# --- Batch 3: line element vs month/day branch structural facts -----
# Branch -> element table (fixed traditional symbols; stdlib only, no
# data file -- same pattern as the local sixty-cycle tables above).
# The machine test suite locks this table against
# foundations.branch_element (seed.json earthly_branches) for all 12
# branches; the two must agree exactly.
BRANCH_ELEMENTS = {
    "子": "水",
    "丑": "土",
    "寅": "木",
    "卯": "木",
    "辰": "土",
    "巳": "火",
    "午": "火",
    "未": "土",
    "申": "金",
    "酉": "金",
    "戌": "土",
    "亥": "水",
}


def _require_branch(value, name):
    if not isinstance(value, str) or value not in BRANCH_ELEMENTS:
        raise ValueError("%s must be one earthly branch" % name)
    return value


def _require_six_line_branches(line_branches):
    if (
        not isinstance(line_branches, (list, tuple))
        or len(line_branches) != 6
        or any(not isinstance(b, str) or b not in BRANCH_ELEMENTS
               for b in line_branches)
    ):
        raise ValueError("line_branches must be six earthly branches, bottom to top")
    return list(line_branches)


def _require_day_ganzhi(day_ganzhi):
    if not isinstance(day_ganzhi, str) or day_ganzhi not in _YUEJIAN_RICHEN_CYCLE:
        raise ValueError("day_ganzhi must be a sixty-cycle ganzhi string")
    return day_ganzhi


def element_of_branch(branch):
    """Return the five-element of an earthly branch (子水 ... 亥水)."""
    return BRANCH_ELEMENTS[_require_branch(branch, "branch")]


def element_relation_between(line_branch, reference_branch):
    """Return the element relation of a line branch to a reference branch.

    The relation is read FROM the line: ``同我`` (same element),
    ``我生`` (line element generates the reference element), ``生我``
    (reference element generates the line element), ``我克`` (line
    element controls the reference element), ``克我`` (reference
    element controls the line element). Reuses the reviewed callable
    ``operations.liuyao.element_relation``; this function only maps
    branches to elements. A fact, not a verdict: it says nothing about
    旺衰, strength, or fortune.
    """
    line_element = element_of_branch(line_branch)
    reference_element = element_of_branch(reference_branch)
    return {
        "line_branch": line_branch,
        "line_element": line_element,
        "reference_branch": reference_branch,
        "reference_element": reference_element,
        "relation": _element_relation(line_element, reference_element),
    }


def line_relations_to_month_day(line_branches, month_branch, day_ganzhi):
    """Enumerate per-line element relations to the month and day branches.

    For each of the six lines (bottom to top) this records the line
    branch and its element, the month branch and its element with the
    line's relation to it (``relation_to_month``), and the day branch
    (from ``day_ganzhi``) and its element with the line's relation to
    it (``relation_to_day``). Relations are the five 生克比和 facts
    (同我/我生/生我/我克/克我) -- structure only.

    No 旺衰 verdict is produced: ``conclusion``, ``wangshuai`` and
    ``verdict`` are always None, because no registered calibre turns
    these relations into a strength judgment (L4: the 四時旺相 chapter
    is unregistered, the xing/hai/earth disputes unadjudicated).
    Changing the month branch changes only the ``relation_to_month``
    facts; changing the day changes only the ``relation_to_day`` facts.
    Raises ValueError on malformed input.
    """
    branches = _require_six_line_branches(line_branches)
    month = _require_branch(month_branch, "month_branch")
    day = _require_day_ganzhi(day_ganzhi)
    day_branch = day[1]
    lines = []
    for position, line_branch in enumerate(branches, start=1):
        to_month = element_relation_between(line_branch, month)
        to_day = element_relation_between(line_branch, day_branch)
        lines.append(
            {
                "position": position,
                "line_branch": line_branch,
                "line_element": to_month["line_element"],
                "month_branch": month,
                "month_element": to_month["reference_element"],
                "relation_to_month": to_month["relation"],
                "day_branch": day_branch,
                "day_element": to_day["reference_element"],
                "relation_to_day": to_day["relation"],
            }
        )
    return {
        "line_branches": branches,
        "month_branch": month,
        "day_branch": day_branch,
        "day_ganzhi": day,
        "lines": lines,
        "conclusion": None,
        "wangshuai": None,
        "verdict": None,
        "note": (
            "逐爻五行与月建/日辰的生克比和结构事实枚举；不作旺衰裁决、"
            "不推出吉凶。月建/日辰只原样记录定义，可执行依据仍在寻找中（L4）。"
        ),
    }


# --- Batch 3 stage 2 (L4 DECIDED 2026-11-25): yuejian/richen STRUCTURE
# Structure and efficacy are implemented as TWO SEPARATE layers.
# The structure layer below computes only what registered tables
# already determine: month/day elements and per-line same-as / clash
# facts against the month and day branches. The efficacy layer
# (assess_wangshuai) is separate and abstains: no registered 四時旺相
# mapping turns these structure facts into a wangshuai verdict, and
# none is read off a structure hit.

_STEM_ELEMENTS = {
    "甲": "木", "乙": "木", "丙": "火", "丁": "火", "戊": "土",
    "己": "土", "庚": "金", "辛": "金", "壬": "水", "癸": "水",
}

# Five-element generating order (木生火生土生金生水生木).
_ELEMENT_GENERATES = {"木": "火", "火": "土", "土": "金", "金": "水", "水": "木"}
_ELEMENT_CONTROLS = {"木": "土", "土": "水", "水": "火", "火": "金", "金": "木"}
_ELEMENT_GENERATED_BY = {v: k for k, v in _ELEMENT_GENERATES.items()}
_ELEMENT_CONTROLLED_BY = {v: k for k, v in _ELEMENT_CONTROLS.items()}


def month_day_structure(month_branch, day_ganzhi):
    """Return the month/day structural context (L4 structure layer).

    Computes only registered-table facts: the month branch's element,
    the day stem and its element, and the day branch and its element.
    The yuejian/richen definitions stay attached as definitions; NO
    wangshuai, sheng/ke verdict, or yongshen conclusion is derived --
    ``wangshuai`` and ``verdict`` are always None. Raises ValueError
    for a month branch outside the twelve branches or a day ganzhi
    outside the sixty-cycle.
    """
    month = _require_branch(month_branch, "month_branch")
    day = _require_day_ganzhi(day_ganzhi)
    return {
        "month_branch": month,
        "month_element": BRANCH_ELEMENTS[month],
        "day_ganzhi": day,
        "day_stem": day[0],
        "day_stem_element": _STEM_ELEMENTS[day[0]],
        "day_branch": day[1],
        "day_branch_element": BRANCH_ELEMENTS[day[1]],
        "yuejian_rule": YUEJIAN_RICHEN_DEFINITIONS["yuejian"]["rule_id"],
        "richen_rule": YUEJIAN_RICHEN_DEFINITIONS["richen"]["rule_id"],
        "wangshuai": None,
        "verdict": None,
        "note": (
            "月建/日辰结构事实：月支五行、日干日支五行；仅记录定义与"
            "结构，不作旺衰裁决、不推出吉凶（L4：结构与效力分层）。"
        ),
    }


def line_month_day_structure(line_branches, month_branch, day_ganzhi):
    """Enrich per-line month/day relations with same-as / clash facts.

    Builds on ``line_relations_to_month_day`` (the five 生克比和 facts)
    and adds, per line, four pure structural booleans: ``same_as_month``
    (line branch equals the month branch), ``same_as_day`` (line branch
    equals the day branch), ``clashes_month`` (line branch clashes with
    the month branch -- the month-break structure fact, same value as
    the month-break flag) and ``clashes_day`` (line branch clashes with
    the day branch -- a structural fact only, NOT a ripo verdict: ripo
    additionally requires the line to be static AND weak, see
    ``liuyao_empty_break.day_break_assessment``).

    No doctrine label is attached to the same-as facts: no "临月建" /
    "临日辰" term is registered (evidence pack 04 §3.2), so the facts
    are reported as equalities, not as named states. ``conclusion`` /
    ``wangshuai`` / ``verdict`` are always None. Raises ValueError on
    malformed input.
    """
    base = line_relations_to_month_day(line_branches, month_branch, day_ganzhi)
    month = base["month_branch"]
    day_branch = base["day_branch"]
    enriched = []
    for line in base["lines"]:
        branch = line["line_branch"]
        enriched.append(
            dict(
                line,
                same_as_month=(branch == month),
                same_as_day=(branch == day_branch),
                clashes_month=_branch_relation(branch, month)["clash"],
                clashes_day=_branch_relation(branch, day_branch)["clash"],
            )
        )
    return dict(
        base,
        lines=enriched,
        month_day=month_day_structure(month, day_ganzhi),
    )


# --- Batch 3 stage 2 (L4): wangshuai efficacy layer (abstains) -------
# Evidence calibre for the 四時旺相 chapter (evidence pack 01 §3):
# the chapter TITLE exists in 增删卜易 (line 532, 「四時旺相章第又十五」),
# but its main text has NO registered section, so no month -> 旺/相/
# 休/囚/死 mapping table exists in the library. Until such a mapping is
# registered and the disputes below are adjudicated, no wangshuai
# verdict can be computed from any structure fact.
SISH_WANGXIANG_EVIDENCE = {
    "chapter": "四時旺相章第十五",
    "source": "增删卜易",
    "locator": "第 532 行章题（仅章题存在性，未登记正文）",
    "text_registered": False,
    "mapping_table": None,
    "status": "no_registered_basis",
    "note": (
        "四時旺相章正文未登记：无月建到旺/相/休/囚/死的映射表，"
        "故任何旺衰效力结论目前无依据。"
    ),
}

WANGSHUAI_EFFICACY_CONDITIONS = (
    {
        "id": "registered_sishi_wangxiang_table",
        "condition": "A registered 四時旺相 mapping table (month -> 旺/相/休/囚/死 per element).",
        "status": "unmet",
        "evidence": "Chapter text unregistered (see SISH_WANGXIANG_EVIDENCE).",
    },
    {
        "id": "xing_hai_earth_disputes_adjudicated",
        "condition": "The 刑/害 and 土之生旺墓绝 disputes in r008/r009 `difference` adjudicated into one algorithm.",
        "status": "unmet",
        "evidence": "r008/r009 difference: disputes unmerged, no single algorithm.",
    },
    {
        "id": "month_day_weighting",
        "condition": "A registered rule for weighing month against day when they pull a line in opposite directions.",
        "status": "unmet",
        "evidence": "Evidence pack 02 §4.1: no registered month-day weighting rule.",
    },
    {
        "id": "line_weak_strong_criterion",
        "condition": "A registered criterion turning a line's element relations into a weak/strong verdict.",
        "status": "unmet",
        "evidence": "r008/r009 inputs.missing: 旺衰 must be judged separately; no criterion registered.",
    },
)


def assess_wangshuai(structure):
    """Assess wangshuai (旺衰) from month/day structure facts. ABSTAINS.

    This is the EFFICACY layer, deliberately separate from the structure
    layer: it takes a ``line_month_day_structure`` (or
    ``line_relations_to_month_day``) result and returns an explicit
    abstention, never a wangshuai verdict. A structure hit -- e.g. every
    line 生我 against the month -- is a relation fact, not a strength
    verdict, and no registered 四時旺相 mapping exists that could turn
    it into one. ``wangshuai`` and ``verdict`` are always None;
    ``status`` is always ``insufficient_basis`` and the unmet conditions
    are listed. Raises ValueError when the input is not a structure
    result (missing ``lines``).
    """
    if not isinstance(structure, dict) or "lines" not in structure:
        raise ValueError("assess_wangshuai requires a line month/day structure result")
    return {
        "status": "insufficient_basis",
        "wangshuai": None,
        "verdict": None,
        "month_branch": structure.get("month_branch"),
        "day_ganzhi": structure.get("day_ganzhi"),
        "unmet_conditions": [c["id"] for c in WANGSHUAI_EFFICACY_CONDITIONS],
        "conditions": deepcopy(WANGSHUAI_EFFICACY_CONDITIONS),
        "note": (
            "旺衰效力层：结构事实不直接推旺衰；四時旺相映射未登记、"
            "刑害/土争议未裁定、月日权衡口径未登记，故暂不可判。"
        ),
    }


# --- Batch 3 stage 2: yuan-shen / ji-shen / chou-shen STRUCTURE ------
# Framework definitions only (status framework_only, no classical
# citation registered): the roles are five-element relations to the
# useful god's ELEMENT. The caller supplies that element; this framework
# never decides WHICH line is the useful god (no approved mapping) and
# never states any effect of a role. Per-item classical evidence for
# these roles (r013-r018) is still unreviewed.
RELATIVE_ROLE_DEFINITIONS = {
    "yuanshen": {
        "name": "原神",
        "definition": "生用神者：五行生用神之行的行。",
        "evidence_status": "framework_only",
        "classical_citation": None,
    },
    "jishen": {
        "name": "忌神",
        "definition": "克用神者：五行克用神之行的行。",
        "evidence_status": "framework_only",
        "classical_citation": None,
    },
    "choushen": {
        "name": "仇神",
        "definition": "克原神者：五行克原神之行的行。",
        "evidence_status": "framework_only",
        "classical_citation": None,
    },
    "yongshen_element": {
        "name": "用神同行",
        "definition": "与用神同行的行（结构同类，非用神爻本身）。",
        "evidence_status": "framework_only",
        "classical_citation": None,
    },
    "generated_by_yongshen": {
        "name": "用神所生",
        "definition": "用神之行所生的行。",
        "evidence_status": "framework_only",
        "classical_citation": None,
    },
}


def _require_element(element):
    if not isinstance(element, str) or element not in _ELEMENT_GENERATES:
        raise ValueError("element must be one of 木火土金水")
    return element


def roles_for_element(yongshen_element):
    """Return the five-element role partition relative to a yongshen element.

    Given the useful god's ELEMENT (supplied by the caller -- this
    function never selects a useful-god line), the five elements split
    exactly into five roles: the element itself (``yongshen_element``),
    the element generating it (``yuanshen``), the element it generates
    (``generated_by_yongshen``), the element controlling it (``jishen``)
    and the element controlling the yuan-shen (``choushen``). The last
    of these is also the element the useful god controls, which the test
    suite locks for all five elements. Role facts only: ``verdict`` and
    ``effect`` are always None -- no line is named useful god, and no
    role implies any fortune or efficacy.
    """
    element = _require_element(yongshen_element)
    yuanshen = _ELEMENT_GENERATED_BY[element]
    generated = _ELEMENT_GENERATES[element]
    jishen = _ELEMENT_CONTROLLED_BY[element]
    choushen = _ELEMENT_CONTROLLED_BY[yuanshen]
    roles = {
        element: "yongshen_element",
        yuanshen: "yuanshen",
        generated: "generated_by_yongshen",
        jishen: "jishen",
        choushen: "choushen",
    }
    return {
        "yongshen_element": element,
        "yuanshen_element": yuanshen,
        "jishen_element": jishen,
        "choushen_element": choushen,
        "generated_by_yongshen_element": generated,
        "roles": roles,
        "role_definitions": deepcopy(RELATIVE_ROLE_DEFINITIONS),
        "verdict": None,
        "effect": None,
        "evidence_status": "framework_only",
        "note": (
            "原神/忌神/仇神结构框架：相对用神之行的五行角色事实；"
            "不指定用神爻，不立效力规则。"
        ),
    }


def line_roles_relative_to_element(line_branches, yongshen_element):
    """Label each line's element role relative to a yongshen element.

    For each of the six lines (bottom to top) this records the line
    branch, its element, and its role from ``roles_for_element``:
    ``yongshen_element`` / ``yuanshen`` / ``jishen`` / ``choushen`` /
    ``generated_by_yongshen``. A line labelled ``yongshen_element``
    merely shares the useful god's element; it is NOT thereby the
    useful god (no mapping is approved). ``verdict`` and ``effect``
    are always None. Raises ValueError on malformed input.
    """
    branches = _require_six_line_branches(line_branches)
    partition = roles_for_element(yongshen_element)
    lines = [
        {
            "position": position,
            "line_branch": branch,
            "line_element": BRANCH_ELEMENTS[branch],
            "role": partition["roles"][BRANCH_ELEMENTS[branch]],
        }
        for position, branch in enumerate(branches, start=1)
    ]
    return {
        "yongshen_element": partition["yongshen_element"],
        "line_branches": branches,
        "lines": lines,
        "roles": dict(partition["roles"]),
        "verdict": None,
        "effect": None,
        "evidence_status": "framework_only",
        "note": (
            "逐爻相对用神之行的角色事实；同行爻不是用神爻，"
            "角色不推出吉凶与效力。"
        ),
    }
