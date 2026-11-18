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
    "list_question_types",
    "get_useful_god_mapping",
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
