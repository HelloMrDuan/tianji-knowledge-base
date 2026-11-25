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
  / ``operations.liuyao``). This module is pure stdlib Python and imports
  nothing from the sealed-data-dependent parts of the package, so its
  tests run locally and in public CI.

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

__all__ = [
    "QUESTION_TYPES",
    "USEFUL_GOD_MAPPINGS",
    "YUEJIAN_RICHEN_DEFINITIONS",
    "list_question_types",
    "get_useful_god_mapping",
    "record_month_day_context",
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
    if not isinstance(month_branch, str) or month_branch not in _YUEJIAN_RICHEN_BRANCHES:
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
