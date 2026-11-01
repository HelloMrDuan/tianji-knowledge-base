"""TJ-017.3 staged-opening phase 2: the public 大运 presentation builder.

Adjudicated in docs/product/TJ0173_STAGED_OPENING_PHASE2.md (E0374)
under the user's 2026-11-01 staged-opening decision, phase 2. The
independence review found the timeline face (direction, the Sanming
conversion, the Shenfeng conversion limited to its first period, the
sequence facts and method choice) fully independent of TJ-017.2
cross-rule invocation and of the deferred U1/U3 decisions: every
user-visible fact traces to the registered Phase1 rules
``bazi.rule.r038`` / ``bazi.rule.r039`` / ``bazi.rule.r041`` and their
Phase2 steps, the sealed Golden cases and provider calendar facts.

This module derives the public presentation object (Variant
``dayun-public-presentation-v1``) exclusively from the two method
views of one request and that request's own composition result
(``execution['composition']``). The builder never trusts the views'
self-report: it re-validates both views against the composition
(adjudication §6.2) — governance flag sets, cross-method natal /
direction / counting identity, per-entry interval fidelity against
the composition's sequence alignment, exact registered citation
sets, and a recomputation pass of the direction block — and projects
only the adjudicated §4 fields. Any drift fails closed with
``ValueError``; the scenario layer turns that into a failed request
rather than a partial presentation.

The builder recomputes nothing: no direction, no conversion, no
interval endpoint is derived here, and the scope/limitations texts
are the adjudicated §4.4 constants. Source Variants and governance
flags are never flipped by this module.
"""

import copy

from .bazi_dayun_classical import (
    CONVERSION_VARIANT,
    DIRECTION_VARIANT,
    SANMING_SOURCE_ID,
    SHENFENG_CONVERSION_VARIANT,
    SHENFENG_SOURCE_ID,
    validate_classical_direction,
)
from .bazi_dayun_compose import COMPOSE_VARIANT, MEASUREMENT_VARIANT
from .bazi_dayun_sequence import VARIANT as SEQUENCE_VARIANT
from .bazi_dayun_timeline_view import (
    SANMING_APPLIED_SOURCE_ID,
    SHENFENG_CONVERSION_QUOTE_IDS,
    VIEW_VARIANT,
)
from .bazi_dayun_timeline_view import (
    _NOTICE_APPROXIMATE,
    _NOTICE_METHODS_SEPARATE,
    _NOTICE_SHENFENG_NO_DECADES,
    _NOTICE_SHENFENG_ZERO_DAY,
    _NOTICE_ZERO_JIE,
)

VARIANT = "dayun-public-presentation-v1"
ROLE_SELECTION = "explicit_historical_category_not_inferred_identity"
TEN_GOD_RULE_ID = "bazi.phase2.ten_gods"

EXPECTED_CHAIN = [
    DIRECTION_VARIANT, MEASUREMENT_VARIANT, CONVERSION_VARIANT,
    SEQUENCE_VARIANT,
]

RULES = (
    {"phase1_rule_id": "bazi.rule.r038",
     "phase2_step_id": "bazi.phase2.dayun_classical_direction",
     "variant": DIRECTION_VARIANT, "source_id": SANMING_APPLIED_SOURCE_ID},
    {"phase1_rule_id": "bazi.rule.r039",
     "phase2_step_id": "bazi.phase2.dayun_sanming_conversion",
     "variant": CONVERSION_VARIANT, "source_id": SANMING_APPLIED_SOURCE_ID},
    {"phase1_rule_id": "bazi.rule.r041",
     "phase2_step_id": "bazi.phase2.dayun_shenfeng_conversion",
     "variant": SHENFENG_CONVERSION_VARIANT, "source_id": SHENFENG_SOURCE_ID},
)

SEQUENCE_DISCLOSURE = {
    "variant": SEQUENCE_VARIANT,
    "ten_god_rule_id": TEN_GOD_RULE_ID,
}

VALIDATION_RECORD = {
    "direction_self_validated": True,
    "interval_fidelity": "verbatim_from_composition",
    "quote_sets": "exact_registered_citation_sets",
}

# Adjudication §4.4: the scope statement and limitations, finalized
# here verbatim and pinned by tests. The scope text is the one
# registered negation context (it names the unbuilt faces once,
# inside an explicit negation); the wording scan below exempts these
# two constants exactly, as in the phase-1 builder.
SCOPE = (
    "本呈现只包含已注册古典规则算出的大运方向、起运换算与逐运干支序列事实；"
    "三命时级与神峰日级为两套分立注册口径、并列呈现、永不合并；"
    "交运时间只给出区间。",
    "本呈现与调候、病药取用依据呈现相互独立，任一不构成对另一的结论；"
    "本呈现不含旺衰、喜用、格局或调候、病药结论。",
)
LIMITATIONS = (
    "不呈现任何年龄数值：古典起运为实历时长，年龄折算无原典口径。",
    "神峰口径逐运起始区间只提供首运，第二运起为空态，不以十年平移拟制。",
    "出生时刻恰逢节气交界时，交运时间呈暂不可判空态，不以近似值填充。",
    "本呈现不是吉凶判断，不预测任何现实事件。",
)

_METHOD_OPTIONS = [
    {"id": "sanming", "label": "三命时级", "variant": CONVERSION_VARIANT,
     "source_id": SANMING_SOURCE_ID, "selectable": True},
    {"id": "shenfeng", "label": "神峰日级",
     "variant": SHENFENG_CONVERSION_VARIANT,
     "source_id": SHENFENG_SOURCE_ID, "selectable": True},
]

_NOTICE_TEXTS = {
    notice["code"]: notice["text"]
    for notice in (
        _NOTICE_METHODS_SEPARATE, _NOTICE_ZERO_JIE, _NOTICE_APPROXIMATE,
        _NOTICE_SHENFENG_NO_DECADES, _NOTICE_SHENFENG_ZERO_DAY)
}

_TOP_KEYS = {
    "variant", "status", "role", "methods", "method_options",
    "evidence", "scope", "limitations",
}

# Adjudication §4.5 / §6.2(f): no single-point date field and no age
# field may exist anywhere in the public object, and no efficacy,
# fortune, prediction or unopened-system wording may appear in any
# builder-projected string. Verbatim registered quotes (sources and
# the direction rule quote) and the two pinned §4.4 constants are
# exempt from the wording scan: quotes are pinned verbatim against
# the composition instead, and the constants are the registered
# negation context.
_BANNED_KEY_PARTS = ("age", "score", "percent", "verdict", "prediction",
                     "efficacy")
_BANNED_KEYS = {"start_date", "end_date", "start_age", "end_age",
                "handover_datetime", "conversion_to_start_age"}
_BANNED_TEXTS = (
    "效力", "运势", "吉凶", "旺衰", "喜用", "扶抑", "格局", "岁数",
    "年龄", "预测", "婚期", "灾祸", "评分", "百分比", "应期", "流年",
)
_SCAN_EXEMPT_KEYS = {"quotes", "rule_quote", "scope", "limitations"}


def _fail(message):
    raise ValueError(message)


def _require(condition, message):
    if not condition:
        _fail(message)


def _banned_scan(value, *, exempt=False):
    if isinstance(value, dict):
        for key, item in value.items():
            _require(isinstance(key, str), "presentation key malformed")
            _require(key not in _BANNED_KEYS
                     and not any(part in key
                                 for part in _BANNED_KEY_PARTS),
                     f"banned field name in presentation: {key}")
            _banned_scan(item, exempt=exempt or key in _SCAN_EXEMPT_KEYS)
    elif isinstance(value, list):
        for item in value:
            _banned_scan(item, exempt=exempt)
    elif isinstance(value, str) and not exempt:
        for banned in _BANNED_TEXTS:
            _require(banned not in value,
                     f"banned wording in presentation: {banned}")


def _execution_composition(execution):
    _require(isinstance(execution, dict), "execution view must be an object")
    _require("composition" in execution, "execution view is missing composition")
    composition = execution["composition"]
    _require(isinstance(composition, dict), "composition must be an object")
    return composition


def _validate_composition_shell(composition):
    _require(composition.get("variant") == COMPOSE_VARIANT,
             "composition variant drifted")
    _require(composition.get("research_only") is True
             and composition.get("public_enabled") is False
             and composition.get("ai_enabled") is False,
             "composition release flags drifted")
    _require(composition.get("evidence_binding")
             == "inherited_registered_phase1_phase2",
             "composition lost its inherited evidence binding")
    _require(composition.get("composition_chain") == EXPECTED_CHAIN,
             "composition chain drifted")
    _require(composition.get("status") in ("converted", "unresolved"),
             "composition status drifted")
    _require(composition.get("traditional_role") in ("male", "female"),
             "composition role drifted")
    _require(composition.get("traditional_role_selection") == ROLE_SELECTION,
             "composition role selection drifted")
    for key in ("birth", "pillars", "direction", "counting",
                "sanming_conversion", "sequence",
                "sequence_time_alignment", "parallel_variants"):
        _require(key in composition, f"composition is missing {key}")
    parallel = composition["parallel_variants"]
    _require(isinstance(parallel, dict)
             and isinstance(parallel.get("shenfeng_day_level"), dict),
             "composition carries no Shenfeng parallel block")


def _validate_view_shell(view, method, composition):
    label = f"{method} view"
    _require(isinstance(view, dict), f"{label} must be an object")
    _require(view.get("variant") == VIEW_VARIANT, f"{label} variant drifted")
    _require(view.get("view_of_variant") == COMPOSE_VARIANT,
             f"{label} view-of drifted")
    _require(view.get("method") == method, f"{label} method drifted")
    _require(view.get("composition_chain")
             == composition["composition_chain"],
             f"{label} composition chain drifted")
    _require(view.get("research_only") is True
             and view.get("public_enabled") is False
             and view.get("ai_enabled") is False,
             f"{label} release flags drifted")
    _require(view.get("evidence_binding")
             == "inherited_registered_phase1_phase2",
             f"{label} lost its inherited evidence binding")
    _require(view.get("age_presentation") == "not_presented",
             f"{label} age presentation drifted")


def _validate_view_facts(view, composition):
    """Natal / direction / counting of one view against the composition."""
    natal = view.get("natal")
    _require(isinstance(natal, dict), "view natal malformed")
    birth = composition["birth"]
    _require(natal.get("birth") == {
        "input_value": birth["input_value"], "zone": birth["zone"],
        "local_datetime": birth["local_datetime"]},
        "view natal birth does not equal the composition birth")
    pillars = composition["pillars"]
    _require(natal.get("pillars") == {
        "year": pillars["year_ganzhi"], "month": pillars["month_ganzhi"],
        "day": pillars["day_ganzhi"], "hour": pillars["hour_ganzhi"],
        "day_master": pillars["day_master"]},
        "view natal pillars do not equal the composition pillars")
    _require(natal.get("traditional_role")
             == composition["traditional_role"],
             "view natal role drifted")
    _require(natal.get("traditional_role_selection") == ROLE_SELECTION,
             "view natal role selection drifted")
    direction = view.get("direction")
    source = composition["direction"]
    _require(isinstance(direction, dict), "view direction malformed")
    _require(direction.get("value") == source["direction"],
             "view direction value drifted")
    _require(direction.get("label")
             == ("顺行" if source["direction"] == "forward" else "逆行"),
             "view direction label drifted")
    _require(direction.get("counting_target") == source["counting_target"],
             "view direction counting target drifted")
    _require(direction.get("counted_jie")
             == composition["sanming_conversion"].get("counted_jie"),
             "view counted jie drifted")
    _require(direction.get("rule_quote") == source["rule_quote"],
             "view rule quote drifted")
    _require(view.get("counting") == composition["counting"],
             "view counting does not equal the composition counting")


def _validate_notices(view, method, composition):
    notices = view.get("notices")
    _require(isinstance(notices, list) and notices,
             "view notices malformed")
    codes = []
    for notice in notices:
        _require(isinstance(notice, dict)
                 and set(notice) == {"code", "text"},
                 "view notice malformed")
        _require(notice["code"] in _NOTICE_TEXTS,
                 "view notice code outside the closed set")
        _require(notice["text"] == _NOTICE_TEXTS[notice["code"]],
                 "view notice text drifted")
        codes.append(notice["code"])
    _require(codes[0] == "methods_presented_separately",
             "view notices lost the separateness notice")
    _require(len(codes) == len(set(codes)), "view notices duplicated")
    if composition["status"] != "converted":
        _require("zero_jie_boundary" in codes,
                 "unresolved composition lost the zero-jie notice")
    if method == "shenfeng":
        _require("shenfeng_decade_shifts_not_provided" in codes,
                 "shenfeng view lost the decade-shift notice")
        block = composition["parallel_variants"]["shenfeng_day_level"]
        if block["status"] != "converted":
            _require("shenfeng_zero_day_count" in codes,
                     "unresolved shenfeng view lost the zero-day notice")


def _expected_sources(composition, method):
    direction = composition["direction"]
    quotes = direction["evidence_quotes"]
    if method == "sanming":
        selected = [q for q in quotes
                    if q.get("source_id") == SANMING_APPLIED_SOURCE_ID]
        _require([q["id"] for q in selected]
                 == ["direction_rule", "vol11_direction_witness"],
                 "composition direction quotes lost the Sanming set")
        blocks = [{"method": "sanming", "role": "direction_rule",
                   "variant": DIRECTION_VARIANT,
                   "source_id": SANMING_APPLIED_SOURCE_ID,
                   "quotes": selected}]
        conversion = composition["sanming_conversion"]
        if "handover_basis_quote" in conversion:
            blocks.append(
                {"method": "sanming", "role": "handover_basis",
                 "variant": CONVERSION_VARIANT,
                 "source_id": SANMING_APPLIED_SOURCE_ID,
                 "quotes": [conversion["handover_basis_quote"]]})
        return blocks
    wanted = list(SHENFENG_CONVERSION_QUOTE_IDS)
    selected = [q for q in quotes
                if q.get("source_id") == SHENFENG_SOURCE_ID
                and q.get("id") in wanted]
    _require([q["id"] for q in selected] == wanted,
             "composition direction quotes lost the Shenfeng set")
    return [{"method": "shenfeng", "role": "conversion_examples",
             "variant": SHENFENG_CONVERSION_VARIANT,
             "source_id": SHENFENG_SOURCE_ID, "quotes": selected}]


def _validate_sources(view, composition, method):
    _require(view.get("sources") == _expected_sources(composition, method),
             f"{method} view sources do not equal the registered "
             "citation sets carried by the composition")


def _base_entry_matches(entry, row, ganzhi_key):
    return (
        entry.get("period_index") == row["period_index"]
        and entry.get("ganzhi") == row[ganzhi_key]
        and entry.get("stem") == row["stem"]
        and entry.get("branch") == row["branch"]
        and entry.get("ten_god_relative_to_natal_day_stem")
        == row["ten_god_relative_to_natal_day_stem"])


def _validate_sanming(view, composition):
    conversion = composition["sanming_conversion"]
    _require(view.get("status") == composition["status"],
             "sanming view status drifted")
    duration = view.get("duration")
    _require(isinstance(duration, dict), "sanming duration malformed")
    _require(duration.get("method") == "sanming_shichen_level"
             and duration.get("variant") == CONVERSION_VARIANT,
             "sanming duration method drifted")
    _require(duration.get("status") == conversion["status"],
             "sanming duration status drifted")
    _require(duration.get("interval_days")
             == conversion.get("duration_interval_days"),
             "sanming duration interval drifted")
    _require(duration.get("decomposition")
             == conversion.get("duration_decomposition"),
             "sanming duration decomposition drifted")
    _require(duration.get("counting") == conversion.get("counting"),
             "sanming duration counting drifted")
    _require(duration.get("approximate")
             == conversion.get("approximate", False),
             "sanming duration approximate drifted")
    _require(duration.get("rounding_applied") is False
             and duration.get("rounding_policy")
             == "refused_classical_text_prohibits_rounding",
             "sanming duration rounding record drifted")
    _require(("approximation_basis" in duration)
             == ("approximation_basis" in conversion),
             "sanming duration approximation basis drifted")
    if "approximation_basis" in conversion:
        _require(duration["approximation_basis"]
                 == conversion["approximation_basis"],
                 "sanming duration approximation basis drifted")
    entries = view.get("entries")
    alignment = composition["sequence_time_alignment"]
    _require(isinstance(entries, list) and len(entries) == len(alignment),
             "sanming entries do not match the composition alignment")
    for entry, row in zip(entries, alignment):
        _require(_base_entry_matches(entry, row, "candidate_ganzhi"),
                 "sanming entry facts drifted")
        if composition["status"] == "converted":
            _require(entry.get("state") == "interval"
                     and entry.get("start_interval")
                     == row["start_interval"],
                     "sanming entry interval drifted")
        else:
            _require(entry.get("state") == "unresolved"
                     and entry.get("start_interval") is None
                     and entry.get("start_interval_status")
                     == row.get("start_interval_status"),
                     "sanming unresolved entry drifted")
    if composition["status"] != "converted":
        _require(duration.get("reason") == conversion.get("reason")
                 and view.get("reason") == conversion.get("reason"),
                 "sanming unresolved reason drifted")


def _validate_shenfeng(view, composition):
    block = composition["parallel_variants"]["shenfeng_day_level"]
    _require(view.get("status") == block["status"],
             "shenfeng view status drifted")
    duration = view.get("duration")
    _require(isinstance(duration, dict), "shenfeng duration malformed")
    _require(duration.get("method") == "shenfeng_day_level"
             and duration.get("variant")
             == SHENFENG_CONVERSION_VARIANT,
             "shenfeng duration method drifted")
    _require(duration.get("status") == block["status"],
             "shenfeng duration status drifted")
    _require(duration.get("interval_days")
             == block.get("duration_interval_days"),
             "shenfeng duration interval drifted")
    _require(duration.get("text_result_days")
             == block.get("text_result_days"),
             "shenfeng text result drifted")
    _require(duration.get("counting") == {
        "whole_days": (block.get("input") or {}).get("whole_days"),
        "counting_target": block.get("counting_target")},
        "shenfeng duration counting drifted")
    _require(duration.get("granularity_note")
             == block.get("granularity_note"),
             "shenfeng granularity note drifted")
    _require(duration.get("approximate") is False,
             "shenfeng duration approximate drifted")
    rows = composition["sequence"]["rows"]
    entries = view.get("entries")
    _require(isinstance(entries, list) and len(entries) == len(rows),
             "shenfeng entries do not match the composition sequence")
    for entry, row in zip(entries, rows):
        _require(_base_entry_matches(entry, row, "candidate_ganzhi"),
                 "shenfeng entry facts drifted")
        if block["status"] != "converted":
            _require(entry.get("state") == "unresolved"
                     and entry.get("start_interval") is None
                     and entry.get("start_interval_status")
                     == "unresolved: " + str(block.get("reason")),
                     "shenfeng unresolved entry drifted")
        elif row["period_index"] == 1:
            interval = block["first_period_start_interval"]
            expected = {
                "earliest": interval["earliest"],
                "latest": interval["latest"],
                "max_inclusive": interval["max_inclusive"],
                "derivation": interval["derivation"],
                "decade_shifts": interval["decade_shifts"],
                "method": "shenfeng_day_level",
                "variant": SHENFENG_CONVERSION_VARIANT,
            }
            _require(entry.get("state") == "interval"
                     and entry.get("start_interval") == expected,
                     "shenfeng first-period interval drifted")
        else:
            _require(entry.get("state") == "not_provided"
                     and entry.get("start_interval") is None
                     and entry.get("start_interval_status")
                     == ("not_provided: shenfeng day-level decade "
                         "shifts are not derived at composition level"),
                     "shenfeng not-provided entry drifted")
    if block["status"] != "converted":
        _require(duration.get("reason") == block.get("reason")
                 and view.get("reason") == block.get("reason"),
                 "shenfeng unresolved reason drifted")


def _project_duration(duration, method):
    if method == "sanming":
        keys = ("method", "variant", "status", "interval_days",
                "decomposition", "counting", "approximate",
                "rounding_applied", "rounding_policy")
    else:
        keys = ("method", "variant", "status", "interval_days",
                "text_result_days", "counting", "granularity_note",
                "approximate")
    projected = {key: copy.deepcopy(duration[key]) for key in keys
                 if key in duration}
    if "approximation_basis" in duration:
        projected["approximation_basis"] = copy.deepcopy(
            duration["approximation_basis"])
    if duration.get("status") != "converted":
        projected["reason"] = duration["reason"]
    return projected


def _project_entry(entry):
    projected = {
        "period_index": entry["period_index"],
        "ganzhi": entry["ganzhi"],
        "stem": entry["stem"],
        "branch": entry["branch"],
        "ten_god_relative_to_natal_day_stem":
            entry["ten_god_relative_to_natal_day_stem"],
        "state": entry["state"],
        "start_interval": copy.deepcopy(entry["start_interval"]),
    }
    if "start_interval_status" in entry:
        projected["start_interval_status"] = entry["start_interval_status"]
    return projected


def _project_method(view, method):
    projected = {
        "method": method,
        "status": view["status"],
        "natal": {"pillars": copy.deepcopy(view["natal"]["pillars"])},
        "direction": copy.deepcopy(view["direction"]),
        "duration": _project_duration(view["duration"], method),
        "entries": [_project_entry(entry) for entry in view["entries"]],
        "notices": [{"code": notice["code"], "text": notice["text"]}
                    for notice in view["notices"]],
        "sources": copy.deepcopy(view["sources"]),
    }
    if view["status"] != "converted":
        projected["reason"] = view["reason"]
    return projected


def public_dayun_presentation(sanming_view, shenfeng_view, *, execution):
    """Build the phase-2 public presentation from one request's records.

    ``sanming_view``/``shenfeng_view`` are the two method views derived
    from the same composition; ``execution['composition']`` is that
    composition result, held as the request's execution record. Any
    drift between the views and the composition fails closed
    (ValueError); the scenario layer fails the whole request.
    """
    composition = _execution_composition(execution)
    _validate_composition_shell(composition)
    # §6.2(e): the direction block passes the registered
    # self-validation recomputation inside this request.
    validate_classical_direction(composition["direction"])
    _require(composition["direction"].get("traditional_role")
             == composition["traditional_role"],
             "composition direction role drifted")
    for view, method in ((sanming_view, "sanming"),
                         (shenfeng_view, "shenfeng")):
        _validate_view_shell(view, method, composition)
        _validate_view_facts(view, composition)
        _validate_notices(view, method, composition)
        _validate_sources(view, composition, method)
    _validate_sanming(sanming_view, composition)
    _validate_shenfeng(shenfeng_view, composition)
    # §6.2(b): the two methods are views of one composition, so their
    # natal, direction and counting blocks are identical by
    # construction; any cross-method drift is tampering.
    for key in ("natal", "direction", "counting"):
        _require(sanming_view[key] == shenfeng_view[key],
                 f"the two method views disagree on {key}")
    _require(sanming_view.get("method_options")
             == shenfeng_view.get("method_options")
             == _METHOD_OPTIONS,
             "method options drifted")
    presentation = {
        "variant": VARIANT,
        "status": ("presented" if composition["status"] == "converted"
                   else "unresolved"),
        "role": {
            "traditional_role": composition["traditional_role"],
            "selection": ROLE_SELECTION,
        },
        "methods": {
            "sanming": _project_method(sanming_view, "sanming"),
            "shenfeng": _project_method(shenfeng_view, "shenfeng"),
        },
        "method_options": copy.deepcopy(_METHOD_OPTIONS),
        "evidence": {
            "composition_chain": list(composition["composition_chain"]),
            "rules": [dict(rule) for rule in RULES],
            "sequence_disclosure": dict(SEQUENCE_DISCLOSURE),
            "validation": dict(VALIDATION_RECORD),
        },
        "scope": list(SCOPE),
        "limitations": list(LIMITATIONS),
    }
    _banned_scan(presentation)
    return presentation


# ------------------------------------------------------- projection check

_SANMING_INTERVAL_KEYS = {"earliest", "latest", "max_inclusive", "basis",
                          "method", "variant"}
_SHENFENG_INTERVAL_KEYS = {"earliest", "latest", "max_inclusive",
                           "derivation", "decade_shifts", "method",
                           "variant"}
_ENTRY_KEYS = {"period_index", "ganzhi", "stem", "branch",
               "ten_god_relative_to_natal_day_stem", "state",
               "start_interval"}
_NOTICE_CODES = set(_NOTICE_TEXTS)


def _is_valid_interval(interval, method, state):
    if state != "interval":
        return interval is None
    if not isinstance(interval, dict):
        return False
    expected = (_SANMING_INTERVAL_KEYS if method == "sanming"
                else _SHENFENG_INTERVAL_KEYS)
    if set(interval) != expected:
        return False
    if interval.get("method") != ("sanming_shichen_level"
                                  if method == "sanming"
                                  else "shenfeng_day_level"):
        return False
    expected_variant = (CONVERSION_VARIANT if method == "sanming"
                        else SHENFENG_CONVERSION_VARIANT)
    return interval.get("variant") == expected_variant


def _is_valid_method(block, method):
    if not isinstance(block, dict):
        return False
    expected_keys = {"method", "status", "natal", "direction",
                     "duration", "entries", "notices", "sources"}
    status = block.get("status")
    if status not in ("converted", "unresolved"):
        return False
    if status != "converted":
        expected_keys.add("reason")
        if not isinstance(block.get("reason"), str):
            return False
    if set(block) != expected_keys or block.get("method") != method:
        return False
    natal = block.get("natal")
    if not isinstance(natal, dict) or set(natal) != {"pillars"}:
        return False
    pillars = natal["pillars"]
    if not isinstance(pillars, dict) or set(pillars) != {
            "year", "month", "day", "hour", "day_master"}:
        return False
    direction = block.get("direction")
    if not isinstance(direction, dict) or set(direction) != {
            "value", "label", "counting_target", "counted_jie",
            "rule_quote"}:
        return False
    if direction.get("value") not in ("forward", "backward"):
        return False
    if direction.get("label") != (
            "顺行" if direction["value"] == "forward" else "逆行"):
        return False
    duration = block.get("duration")
    if not isinstance(duration, dict) \
            or duration.get("status") != status \
            or duration.get("variant") != (
                CONVERSION_VARIANT if method == "sanming"
                else SHENFENG_CONVERSION_VARIANT):
        return False
    if status != "converted" and duration.get("reason") != block["reason"]:
        return False
    entries = block.get("entries")
    if not isinstance(entries, list) or not entries:
        return False
    for index, entry in enumerate(entries, start=1):
        if not isinstance(entry, dict) \
                or entry.get("period_index") != index:
            return False
        expected_entry_keys = set(_ENTRY_KEYS)
        if entry.get("state") != "interval":
            expected_entry_keys.add("start_interval_status")
        if set(entry) != expected_entry_keys:
            return False
        if entry.get("state") not in ("interval", "unresolved",
                                      "not_provided"):
            return False
        if method == "sanming" and entry["state"] == "not_provided":
            return False
        if not _is_valid_interval(entry["start_interval"], method,
                                   entry["state"]):
            return False
    notices = block.get("notices")
    if not isinstance(notices, list) or not notices:
        return False
    for notice in notices:
        if not isinstance(notice, dict) or set(notice) != {"code", "text"}:
            return False
        if notice["code"] not in _NOTICE_CODES \
                or notice["text"] != _NOTICE_TEXTS[notice["code"]]:
            return False
    sources = block.get("sources")
    if not isinstance(sources, list) or not sources:
        return False
    for source in sources:
        if not isinstance(source, dict) or set(source) != {
                "method", "role", "variant", "source_id", "quotes"}:
            return False
        if source["method"] != method:
            return False
        if not isinstance(source["quotes"], list) \
                or not source["quotes"]:
            return False
    return True


def is_valid_public_dayun_presentation(candidate):
    """Structural check used by the public projection's scoped release.

    Only an object with exactly the adjudicated §4 shape, the exact
    registered evidence records and the pinned §4.4 constants may pass
    the projection under the ``dayun_presentation`` key; anything
    else is stripped like every other research object.
    """
    try:
        if not isinstance(candidate, dict) or set(candidate) != _TOP_KEYS:
            return False
        if candidate.get("variant") != VARIANT:
            return False
        if candidate.get("status") not in ("presented", "unresolved"):
            return False
        if candidate.get("role") != {
                "traditional_role": candidate["role"].get(
                    "traditional_role"),
                "selection": ROLE_SELECTION}:
            return False
        if candidate["role"].get("traditional_role") not in (
                "male", "female"):
            return False
        if candidate.get("scope") != list(SCOPE):
            return False
        if candidate.get("limitations") != list(LIMITATIONS):
            return False
        if candidate.get("method_options") != _METHOD_OPTIONS:
            return False
        evidence = candidate.get("evidence")
        if not isinstance(evidence, dict) or set(evidence) != {
                "composition_chain", "rules", "sequence_disclosure",
                "validation"}:
            return False
        if evidence.get("composition_chain") != EXPECTED_CHAIN:
            return False
        if evidence.get("rules") != [dict(rule) for rule in RULES]:
            return False
        if evidence.get("sequence_disclosure") != SEQUENCE_DISCLOSURE:
            return False
        if evidence.get("validation") != VALIDATION_RECORD:
            return False
        methods = candidate.get("methods")
        if not isinstance(methods, dict) or set(methods) != {
                "sanming", "shenfeng"}:
            return False
        sanming = methods["sanming"]
        shenfeng = methods["shenfeng"]
        if not _is_valid_method(sanming, "sanming"):
            return False
        if not _is_valid_method(shenfeng, "shenfeng"):
            return False
        if candidate["status"] == "unresolved" \
                and sanming.get("status") != "unresolved":
            return False
        if candidate["status"] == "presented" \
                and sanming.get("status") != "converted":
            return False
        _banned_scan(candidate)
        return True
    except Exception:
        return False
