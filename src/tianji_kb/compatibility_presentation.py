"""Compatibility presentation builder (TJ-0427, Lane D, TJ-031.19).

Plain-language presentation for the compatibility (缘分合盘) scene,
built ONLY from already-reviewed outputs:

* the existing ``_compatibility`` scenario result (both charts side by
  side, mutual ten-god views, xianchi crossover, five-combinations,
  day-branch relations, natal triple harmonies, cross-pillar matrix);
* each person's WITHIN-chart relations (``reviewed_relations``: stem
  five-combinations, branch six-harmonies / harms / clashes) -- the
  same reviewed computation the bazi chart builder already runs for
  each chart. The pure builder takes them as an input (the caller
  passes each person's chart ``reviewed_relations`` through); the
  end-to-end builder reads them from a plain ``execute("bazi")``
  call with ``include_relations`` and fails closed if that chart's
  pillars drift from the compatibility result's pillars. Triple
  harmonies and the spouse palace are NOT repeated here -- they are
  already carried in the scenario result's own blocks.
* each person's already-approved public presentations, lifted from
  the bazi-profile envelope exactly as ``_career`` lifts them
  (U1 strength, D-1 pattern whitelist, xiyong phase-1);
* each person's first-period dayun only, trimmed with the shared
  career/life helper ``_first_period_dayun_for_career_life``
  (periods 2-8 stay unopened; D7 undecided).

HARD RULES (fail-closed, enforced by the builder and the validator):

* NO match score, NO percentage, NO "compatibility %" of any kind.
  There is no scoring function anywhere in this module, and the
  builder self-scans its output for scoring tokens before returning.
* XING (刑): ``PUNISHMENT_TABLE`` is None -- no punishment table
  exists in the canon -- so 刑 is reported ``not_evaluated``. This
  module NEVER invents a punishment table or any punishment-based
  conclusion. If a table is ever registered, the builder raises
  instead of silently presenting stale "not evaluated" text.
* There is currently NO approved compatibility inference output.
  The presentation says so explicitly (``compatibility_inference``
  is ``not_available`` and ``unified_verdict`` stays None); structure
  facts are never dressed up as conclusions.
* Everything outside the D-1 whitelist and the xiyong phase-1 is
  shown only as candidate / conflict / not_judgeable, exactly as
  the source presentations already state it.

This module does NOT touch ``scenario_engine.py``: the end-to-end
convenience builder calls ``execute_scenario`` (the public entry)
and reuses the shared gates, it never re-implements charting,
strength, pattern, xiyong or dayun computation.
"""

import copy
import json

from .bazi_branch_punishment import PUNISHMENT_TABLE

PRESENTATION_VERSION = "compatibility-presentation-v1"

# Tokens that must never appear anywhere in a presentation object.
# (The wording below is chosen so the honest disclaimers themselves
# never need these words: "no number is derived from the structure"
# is said without the words for score / percentage / match rate.)
_BANNED_TOKENS = (
    "%", "％", "percent", "score",
    "评分", "分数", "打分", "适配度", "匹配度", "契合度",
    "缘分指数", "缘分值", "compatibility score",
)

_PRESENTATION_TOP_KEYS = frozenset((
    "presentation_version", "scenario_id", "sections",
    "compatibility_inference", "unified_verdict",
    "interpretation_allowed", "limitations",
))

_SECTION_KEYS = frozenset((
    "id", "title", "basis", "caliber", "undecided_conditions", "facts",
))

_SECTION_IDS = (
    "charts", "relations", "patterns_and_xiyong", "dayun",
    "inference_boundary",
)

_LIMITATIONS = [
    "双方日主互看十神只表示五行生克与阴阳关系，不等于感情适合或不适合。",
    "对方年支或日支落入咸池目标，只表示固定查表结构对照，不等于吸引力、正缘或婚姻结果。",
    "五合或六合命中不代表化气成立，也不代表适合；六害或六冲命中不等于现实关系受害、分手、争执或凶断。",
    "地支刑未评估：刑表不存在，不自造刑表，不作任何刑相关结论。",
    "三合只按各自原局呈现；跨两张命盘拼接三合的口径尚未定义。",
    "跨柱矩阵的层级只用于阅读，不表示权重或重要性；命中数量不能换算成缘分高低。",
    "格局只呈现 D-1 白名单内的寅月真格；其余格只作候选、冲突或暂不可判。",
    "喜用只呈现调候与病药 phase-1；统一喜用裁决恒为无结论。",
    "大运只呈现首运；第 2–8 运在本页未展开，是否展开尚未决定。",
    "本呈现不输出缘分高低、正缘结论、结婚时间或分手风险。",
    "AI 不参与本场景计算。",
]

_NO_INFERENCE_REASON = (
    "目前没有已批准的合盘推理输出；本呈现只并列双方结构事实与"
    "已批准的有限呈现，不作综合结论。"
)

_NOT_PROVIDED_REASON = "本次调用未传入该人的公开呈现。"


def _fail(message):
    raise ValueError(
        "Compatibility presentation rejected: " + message)


def _banned_scan(value):
    """Fail-closed: no scoring token anywhere in the presentation."""
    text = json.dumps(value, ensure_ascii=False)
    for token in _BANNED_TOKENS:
        if token in text:
            _fail("banned scoring token in presentation: " + token)


def _section(section_id, title, basis, caliber, undecided, facts):
    return {
        "id": section_id,
        "title": title,
        "basis": basis,
        "caliber": caliber,
        "undecided_conditions": list(undecided),
        "facts": copy.deepcopy(facts),
    }


def _person_charts(compatibility_result, key):
    person = compatibility_result.get(key)
    if not isinstance(person, dict):
        _fail("compatibility result without " + key)
    pillars = person.get("pillars")
    day_master = person.get("day_master")
    if not isinstance(pillars, list) or len(pillars) != 4 \
            or not isinstance(day_master, dict):
        _fail(key + " without four pillars and a day master")
    return {
        "pillars": copy.deepcopy(pillars),
        "day_master": copy.deepcopy(day_master),
    }


_NATAL_RELATION_KEYS = (
    "stem_five_combinations", "branch_six_harmonies",
    "branch_six_harms", "branch_six_clashes",
)


def _natal_relations_block(reviewed, key):
    """Within-chart relations for one person, or an honest absence.

    ``reviewed`` is the person's bazi chart ``reviewed_relations``
    dict (or None when the caller did not pass it). Only the four
    lists not already carried elsewhere are kept: triple harmonies
    and the spouse palace already have their own blocks.
    """
    if reviewed is None:
        return {"status": "not_provided",
                "reason": _NOT_PROVIDED_REASON}
    if not isinstance(reviewed, dict):
        _fail(key + " natal relations must be a mapping")
    for name in _NATAL_RELATION_KEYS:
        if not isinstance(reviewed.get(name), list):
            _fail(key + " natal relations without " + name)
    return {name: copy.deepcopy(reviewed[name])
            for name in _NATAL_RELATION_KEYS}


def _relations_facts(compatibility_result, natal_relations=None):
    """Structure facts only, copied from the scenario result.

    Nothing here is recomputed and nothing is interpreted: the ten-god
    views, five-combinations, day-branch relations, xianchi crossover,
    natal triple harmonies and the cross-pillar matrix are the
    scenario's own outputs, verbatim. The within-chart relations
    come from each person's own chart ``reviewed_relations`` (passed
    in, never re-derived here -- see ``_natal_relations_block``).
    """
    for key in ("day_master_relations", "xianchi_cross_matches",
                "reviewed_cross_relations", "cross_relation_matrix"):
        if key not in compatibility_result:
            _fail("compatibility result without " + key)
    relations = compatibility_result["day_master_relations"]
    reviewed = compatibility_result["reviewed_cross_relations"]
    matrix = compatibility_result["cross_relation_matrix"]
    cross = compatibility_result["xianchi_cross_matches"]
    if natal_relations is not None \
            and not isinstance(natal_relations, dict):
        _fail("natal relations must be a mapping")
    natal = natal_relations or {}
    if PUNISHMENT_TABLE is not None:
        # A registered table changes the 刑 boundary: stop and let a
        # human re-review instead of presenting stale "not evaluated".
        _fail("punishment table is now registered; the 刑 boundary "
              "needs re-review before any presentation")
    return {
        "mutual_ten_gods": copy.deepcopy(relations),
        "day_master_five_combination": copy.deepcopy(
            reviewed.get("day_master_five_combination")),
        "spouse_palace_day_branch_relation": copy.deepcopy(
            reviewed.get("spouse_palace_relation")),
        "xianchi_cross_matches": copy.deepcopy(cross),
        "natal_triple_harmonies": {
            "person_a": copy.deepcopy(
                compatibility_result["person_a"].get(
                    "natal_triple_harmonies")),
            "person_b": copy.deepcopy(
                compatibility_result["person_b"].get(
                    "natal_triple_harmonies")),
        },
        "natal_relations": {
            "person_a": _natal_relations_block(
                natal.get("person_a"), "person_a"),
            "person_b": _natal_relations_block(
                natal.get("person_b"), "person_b"),
        },
        "cross_pillar_relation_matrix": {
            "hits": copy.deepcopy(matrix.get("hits")),
            "summary": copy.deepcopy(matrix.get("summary")),
            "tier_policy": copy.deepcopy(matrix.get("tier_policy")),
        },
        "punishment": {
            "status": "not_evaluated",
            "reason": ("刑表不存在（PUNISHMENT_TABLE 为 None）；"
                       "不自造刑表，不作任何刑相关结论。"),
        },
    }


def _person_presentations(bundle, key):
    """Per-person reviewed presentations, or an honest absence.

    ``bundle`` is the person's lift bundle: ``profile_result`` is
    the bazi-profile result dict (strength / pattern / xiyong
    presentations as built by the approved gates), and
    ``dayun_first_period`` is the first-period-trimmed dayun
    presentation (or None when no traditional role was given).
    A missing bundle is reported as not provided, never filled in.
    """
    if bundle is None:
        return {
            "strength": {"status": "not_provided",
                         "reason": _NOT_PROVIDED_REASON},
            "pattern": {"status": "not_provided",
                        "reason": _NOT_PROVIDED_REASON},
            "xiyong": {"status": "not_provided",
                       "reason": _NOT_PROVIDED_REASON},
            "dayun_first_period": {"status": "not_provided",
                                   "reason": _NOT_PROVIDED_REASON},
        }
    if not isinstance(bundle, dict):
        _fail(key + " bundle must be a mapping")
    profile = bundle.get("profile_result")
    if profile is not None and not isinstance(profile, dict):
        _fail(key + " profile_result must be a mapping")
    profile = profile or {}
    out = {}
    for name in ("strength_presentation", "pattern_presentation",
                 "xiyong_presentation"):
        short = name.replace("_presentation", "")
        presentation = profile.get(name)
        if presentation is None:
            out[short] = {"status": "not_provided",
                          "reason": _NOT_PROVIDED_REASON}
        elif not isinstance(presentation, dict):
            _fail(key + " " + name + " must be a mapping")
        else:
            out[short] = copy.deepcopy(presentation)
    xiyong = out["xiyong"]
    if xiyong.get("status") != "not_provided":
        # TJ-013.2 adjudication A: the unified verdict is always
        # refused. A non-None value here is a forgery, never shown.
        if xiyong.get("unified_verdict") is not None:
            _fail(key + " xiyong presentation carries a unified "
                  "verdict")
    dayun = bundle.get("dayun_first_period")
    if dayun is None:
        out["dayun_first_period"] = {
            "status": "not_available",
            "reason": "未选择传统口径，大运未计算。",
        }
    elif not isinstance(dayun, dict):
        _fail(key + " dayun_first_period must be a mapping")
    else:
        out["dayun_first_period"] = copy.deepcopy(dayun)
    return out


def build_compatibility_presentation(compatibility_result, *,
                                     person_a=None, person_b=None,
                                     natal_relations=None):
    """Build the plain-language compatibility presentation.

    ``compatibility_result`` is the ``result`` dict of a compatibility
    scenario envelope (an envelope carrying it under ``"result"`` is
    also accepted). ``person_a`` / ``person_b`` are optional lift
    bundles (see ``_person_presentations``); without them the
    pattern / xiyong / dayun sections honestly report not provided.
    ``natal_relations`` is an optional mapping with ``person_a`` /
    ``person_b`` each carrying that person's bazi chart
    ``reviewed_relations`` dict (or None); without it the
    within-chart relations report not provided. Returns a JSON-able
    dict. Raises ``ValueError`` on any drift, forgery or banned
    token -- the caller must fail the whole request, never return a
    partial object.
    """
    if not isinstance(compatibility_result, dict):
        _fail("compatibility result must be a mapping")
    if "person_a" not in compatibility_result \
            and isinstance(compatibility_result.get("result"), dict):
        compatibility_result = compatibility_result["result"]
    if "person_a" not in compatibility_result \
            or "person_b" not in compatibility_result:
        _fail("compatibility result without both persons")

    charts_a = _person_charts(compatibility_result, "person_a")
    charts_b = _person_charts(compatibility_result, "person_b")
    relations = _relations_facts(compatibility_result, natal_relations)
    pres_a = _person_presentations(person_a, "person_a")
    pres_b = _person_presentations(person_b, "person_b")

    sections = [
        _section(
            "charts", "双方四柱对照",
            "双方真实四柱（bazi/ziping-structural-v1 排盘）",
            "structure_fact",
            ["四柱本身不作任何关系结论；对照只是并列呈现。"],
            {"person_a": charts_a, "person_b": charts_b},
        ),
        _section(
            "relations", "双方结构关系",
            "已审核结构规则：十神、咸池、五合、六合、六害、六冲、"
            "三合（bazi.phase2.*）",
            "structure_fact",
            ["地支刑未评估（刑表不存在）；跨盘拼接三合口径未定义；"
             "合、害、冲只表示固定结构命中，不作感情结论；原局内部"
             "关系只列在场结构，不作旺衰或喜忌判断。"],
            relations,
        ),
        _section(
            "patterns_and_xiyong", "双方格局与喜用（已批准的有限呈现）",
            "各自八字命理页的已批准公开呈现：U1 最小公开旺衰、"
            "D-1 任氏寅月真格白名单、调候与病药 phase-1",
            "reviewed_public_presentation",
            ["除 D-1 外各格的古典成立与破格未立，只作候选、冲突或"
             "暂不可判；格局用神逐格规则待证据审查；扶抑古典方向"
             "零行可建；统一喜用裁决恒为无结论。"],
            {
                "person_a": {
                    "strength": pres_a["strength"],
                    "pattern": pres_a["pattern"],
                    "xiyong": pres_a["xiyong"],
                },
                "person_b": {
                    "strength": pres_b["strength"],
                    "pattern": pres_b["pattern"],
                    "xiyong": pres_b["xiyong"],
                },
                "relations_between_persons": {
                    "unified_verdict": None,
                    "note": ("双方格局与喜用只并列呈现，不作综合结论；"
                             "目前没有已批准的合盘推理输出。"),
                },
            },
        ),
        _section(
            "dayun", "双方大运（只看首运）",
            "各自大运公开呈现的首运裁剪（与事业、总览页同一口径）",
            "reviewed_public_presentation",
            ["第 2–8 运在本页未展开，是否展开尚未决定（D7）；"
             "只输出区间，永不输出单点日期或起运岁数。"],
            {
                "person_a": pres_a["dayun_first_period"],
                "person_b": pres_b["dayun_first_period"],
                "periods_opened": "first_only",
                "periods_2_to_8": ("not_opened_in_this_scene: "
                                   "D7 undecided"),
            },
        ),
        _section(
            "inference_boundary", "合盘推理边界",
            "产品开放方案 §2.2：合盘只接内部装配，不接任何推理引擎输出",
            "boundary_statement",
            ["合盘推理的公开口径须先有可公开的推理输出，目前无；"
             "须逐项提请晋升，本呈现不提请。"],
            {
                "compatibility_inference": {
                    "status": "not_available",
                    "reason": _NO_INFERENCE_REASON,
                },
                "unified_verdict": None,
            },
        ),
    ]

    presentation = {
        "presentation_version": PRESENTATION_VERSION,
        "scenario_id": "compatibility",
        "sections": sections,
        "compatibility_inference": {
            "status": "not_available",
            "reason": _NO_INFERENCE_REASON,
        },
        "unified_verdict": None,
        "interpretation_allowed": False,
        "limitations": list(_LIMITATIONS),
    }
    _banned_scan(presentation)
    if not is_valid_compatibility_presentation(presentation):
        _fail("built presentation failed its own validation")
    return presentation


def build_compatibility_presentation_for_births(
        person_a_birth_value, person_b_birth_value, *,
        person_a_zone=None, person_b_zone=None,
        person_a_traditional_role=None, person_b_traditional_role=None):
    """End-to-end builder from two birth instants.

    Runs the existing compatibility scenario, lifts each person's
    three approved presentations from a bazi-profile envelope
    (exactly as ``_career`` lifts them: no role is passed to the
    profile gate, so no dayun is computed there), trims each
    person's dayun to the first period with the shared career/life
    helper when a traditional role was given, and reads each
    person's within-chart relations from a plain ``execute("bazi")``
    call with ``include_relations`` (failing closed if that chart's
    pillars drift from the compatibility result's pillars). Any
    gate failure raises and fails the whole request -- no partial
    presentation.
    """
    from .engine import execute as _execute_bazi
    from .scenario_engine import (
        _dayun_public_gate,
        _first_period_dayun_for_career_life,
        execute_scenario,
    )

    for role in (person_a_traditional_role, person_b_traditional_role):
        if role is not None and role not in ("male", "female"):
            raise ValueError("traditional role must be male or female")
    for value in (person_a_birth_value, person_b_birth_value):
        if not isinstance(value, str):
            raise ValueError("birth values must be ISO datetime strings")

    compat_inputs = {
        "person_a_birth_value": person_a_birth_value,
        "person_b_birth_value": person_b_birth_value,
    }
    if person_a_zone is not None:
        compat_inputs["person_a_zone"] = person_a_zone
    if person_b_zone is not None:
        compat_inputs["person_b_zone"] = person_b_zone
    if person_a_traditional_role is not None:
        compat_inputs["person_a_traditional_role"] = \
            person_a_traditional_role
    if person_b_traditional_role is not None:
        compat_inputs["person_b_traditional_role"] = \
            person_b_traditional_role
    compatibility = execute_scenario("compatibility", compat_inputs)

    natal_relations = {}
    for key, value, zone in (
            ("person_a", person_a_birth_value, person_a_zone),
            ("person_b", person_b_birth_value, person_b_zone)):
        natal_inputs = {"value": value, "include_xianchi": True,
                        "include_relations": True}
        if zone is not None:
            natal_inputs["zone"] = zone
        natal = _execute_bazi("bazi", natal_inputs)
        natal_pillars = natal["result"]["pillars"]
        compat_pillars = compatibility["result"][key]["pillars"]
        if [p["ganzhi"] for p in natal_pillars] != \
                [p["ganzhi"] for p in compat_pillars]:
            raise ValueError(
                "natal chart pillars drifted from the compatibility "
                "result for " + key)
        natal_relations[key] = natal["result"]["reviewed_relations"]

    bundles = {}
    for key, value, zone, role in (
            ("person_a", person_a_birth_value, person_a_zone,
             person_a_traditional_role),
            ("person_b", person_b_birth_value, person_b_zone,
             person_b_traditional_role)):
        profile_inputs = {
            "value": value,
            # Same strength variant ``_career`` passes to the
            # profile gate; the profile gate must not compute a
            # dayun here (this builder gates its own first-period
            # dayun below), so no role is passed to it.
            "strength_variant": "ditiansui-root-visibility-v1",
        }
        if zone is not None:
            profile_inputs["zone"] = zone
        profile = execute_scenario("bazi-profile", profile_inputs)
        dayun_first = None
        if role is not None:
            dayun_first = _first_period_dayun_for_career_life(
                _dayun_public_gate(value, zone, role))
        bundles[key] = {
            "birth_value": value,
            "zone": zone,
            "traditional_role": role,
            "profile_result": profile["result"],
            "dayun_first_period": dayun_first,
        }
    return build_compatibility_presentation(
        compatibility["result"],
        person_a=bundles["person_a"], person_b=bundles["person_b"],
        natal_relations=natal_relations)


def is_valid_compatibility_presentation(obj):
    """Closed-shape validator for the presentation's scoped release.

    Exact top-level key set, the five sections in order with their
    own basis / caliber / undecided-conditions, no scoring token
    anywhere, unified verdict None, interpretation closed, and 刑
    reported not_evaluated. Returns a bool, never raises.
    """
    try:
        if not isinstance(obj, dict):
            return False
        if set(obj) != _PRESENTATION_TOP_KEYS:
            return False
        if obj["presentation_version"] != PRESENTATION_VERSION:
            return False
        if obj["scenario_id"] != "compatibility":
            return False
        if obj["interpretation_allowed"] is not False:
            return False
        if obj["unified_verdict"] is not None:
            return False
        inference = obj["compatibility_inference"]
        if not isinstance(inference, dict) \
                or inference.get("status") != "not_available" \
                or not isinstance(inference.get("reason"), str) \
                or not inference["reason"]:
            return False
        if not isinstance(obj["limitations"], list) \
                or not obj["limitations"] \
                or not all(isinstance(item, str) and item
                           for item in obj["limitations"]):
            return False
        sections = obj["sections"]
        if not isinstance(sections, list) \
                or [s.get("id") for s in sections] != list(_SECTION_IDS):
            return False
        for section in sections:
            if not isinstance(section, dict) \
                    or set(section) != _SECTION_KEYS:
                return False
            if not isinstance(section["title"], str) \
                    or not section["title"]:
                return False
            if not isinstance(section["basis"], str) \
                    or not section["basis"]:
                return False
            if section["caliber"] not in (
                    "structure_fact", "reviewed_public_presentation",
                    "boundary_statement"):
                return False
            if not isinstance(section["undecided_conditions"], list) \
                    or not section["undecided_conditions"] \
                    or not all(isinstance(item, str) and item
                               for item in section["undecided_conditions"]):
                return False
            if not isinstance(section["facts"], dict):
                return False
        relations = sections[1]["facts"]
        punishment = relations.get("punishment")
        if not isinstance(punishment, dict) \
                or punishment.get("status") != "not_evaluated":
            return False
        natal = relations.get("natal_relations")
        if not isinstance(natal, dict):
            return False
        for key in ("person_a", "person_b"):
            block = natal.get(key)
            if not isinstance(block, dict):
                return False
            if block.get("status") == "not_provided":
                continue
            if not all(isinstance(block.get(name), list)
                       for name in _NATAL_RELATION_KEYS):
                return False
        boundary = sections[4]["facts"]
        if boundary.get("unified_verdict") is not None:
            return False
        if boundary.get("compatibility_inference", {}).get("status") \
                != "not_available":
            return False
        dayun = sections[3]["facts"]
        if dayun.get("periods_opened") != "first_only":
            return False
        _banned_scan(obj)
        return True
    except Exception:  # noqa: BLE001 - validator never raises
        return False


def to_public_compatibility_presentation(candidate):
    """Allowlist projection of a validated compatibility presentation.

    The object is public-safe by construction (the validator enforces
    the exact top-level key set, the five sections in order, no
    scoring token, unified verdict None and 刑 not_evaluated). The
    projection is the final gate: validator pass, then a deep copy.
    An invalid candidate raises ``ValueError``; the projection layer
    treats that as "strip the field", never as a partial release.
    """
    if not is_valid_compatibility_presentation(candidate):
        _fail("candidate is not a valid compatibility presentation")
    return copy.deepcopy(candidate)
