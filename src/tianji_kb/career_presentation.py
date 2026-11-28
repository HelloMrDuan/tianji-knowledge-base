"""TJ-0427 Lane B (career): plain-language career/wealth presentation.

Builds ``career-presentation-v1`` -- a JSON-able, closed-shape
presentation assembled ONLY from already-computed, already-approved
material for the same birth instant:

* the career scene's own Ten-God structure facts (``structure_groups``
  / ``interpretation_cards`` / ``annual_reading`` from
  ``scenario_engine._career`` -- rules ``bazi.phase2.ten_gods`` and
  ``bazi.phase2.hidden_stems``);
* the three already-open public presentations lifted by ``_career``
  (U1 strength ``strength-public-presentation-v1``, D-1 pattern
  ``bazi-pattern-public-presentation-v1``, xiyong phase-1
  ``xiyong-public-presentation-v1``), each re-validated here with its
  own closed-shape validator -- an invalid lift fails closed;
* the FULL 8-period dayun timeline (Q3=A, user adjudication
  2026-11-28, superseding the earlier first-period-only limit D7):
  the validated full dayun public presentation
  (``dayun-public-presentation-v1``, same object the bazi-profile
  gate builds for the same birth instant and role), cross-checked
  against the unified-compute combination block's
  ``candidate_sequence(periods=8)`` rows (ganzhi + stem ten-god must
  agree, fail-closed on drift). Per period only already-grounded
  content: dayun stems, start/end interval, stem ten-god, branch
  hidden stems (the existing ``bazi_core.hidden_stems`` lookup, same
  table as the natal hidden stems), reviewed structural relations
  with the natal chart (from the combination engine's
  ``structural_relations``, scope ``dayun_x_natal``), and a liunian
  query entry (the year of the interval's earliest bound). Ages are
  NEVER computed or presented: the registered timeline view itself
  declares ``age_presentation='not_presented'`` and the dayun
  presentation bans age fields, so the "age interval" in the brief
  is the handover interval itself -- no numeric start age, exact or
  ranged, is fabricated. Shenfeng periods 2-8 are ``not_provided``
  by registered design (day-level decade shifts are not derived),
  not withheld by this scene.
* the unified-compute combination block (``trim_for_career`` research
  ``combination``), consumed as condition conclusions ONLY:
  ``overall_effect`` must be None on both the top level and the
  efficacy block, the cross-layer efficacy registry must be empty,
  and every carried conclusion keeps the engine's own
  "not an efficacy verdict" wording.

Q2 constraint (same adjudication): strength scores and fuyi
candidates are NEVER converted into career/wealth fortune
judgments. This builder carries no modern strength score and no
fuyi candidate-stem list at all; the only fuyi-adjacent content is
the combination engine's own conditional conclusions (existence
facts with the engine's "not an efficacy verdict" wording), and the
lifted U1 strength presentation carries only its adjudicated
status/predicate, never a score.

The builder computes NOTHING new: no strength classification, no
pattern verdict, no useful god, no dayun age or single handover date,
no wealth/income prediction, no score, no industry mapping, no
liuyao career mapping (B3: ``USEFUL_GOD_MAPPINGS`` is still ``{}``,
unapproved). Anything it cannot ground is stated plainly in Chinese
as undecided, per section (each section carries its own
``basis`` / ``caliber`` / ``undecided_conditions``).

Wiring note: this module is intentionally NOT imported by
``scenario_engine.py`` (another lane owns that file). The coordinator
wires ``build_career_presentation`` into the career envelope and the
public projection allowlist; until then the frontend renders the same
four sections from the envelope fields this builder consumes.
"""

import copy

from .bazi_combination_engine import (
    CONDITIONAL_VERDICTS,
    VARIANT as COMBINATION_VARIANT,
)
from .bazi_core import hidden_stems as _hidden_stems_for_branch
from .bazi_dayun_public import is_valid_public_dayun_presentation
from .bazi_pattern_public import is_valid_public_pattern_presentation
from .bazi_strength_public import is_valid_public_strength_presentation
from .bazi_xiyong_public import is_valid_public_presentation as \
    is_valid_public_xiyong_presentation

VARIANT = "career-presentation-v1"

SCOPE_STATEMENT = (
    "本呈现只并列已算的事业财运结构事实：原局十神位置、已开放的"
    "旺衰/格局/喜用呈现、大运 8 运时间线（区间口径）、原局与大运"
    "流年的条件结论。不作任何事业、财运、收入或吉凶判断。")
LIMITATIONS = (
    "不输出事业指数、财运指数、收入金额或投资建议。",
    "大运呈现全部 8 运（Q3=A，2026-11-28）；交运时间只给区间，"
    "起运岁数不折算、不呈现（age_presentation 恒 not_presented）；"
    "神峰口径第 2–8 运区间未提供（已注册设计，非本场景扣留）。",
    "原局与大运流年的跨层效力无已审规则，overall_effect 恒为 None。",
    "六爻事业用神映射未获批，不作问占口径呈现。")

_GROUP_ORDER = ("wealth", "authority", "output", "resource", "peers")
_GROUP_LABELS = {
    "wealth": "财星",
    "authority": "官杀",
    "output": "食伤",
    "resource": "印星",
    "peers": "比劫",
}
# Keys that must never appear anywhere in the output (age/date/score/
# prediction surface). Checked recursively over the finished dict.
_BANNED_KEYS = frozenset((
    "start_age", "end_age", "start_date", "end_date",
    "handover_datetime", "conversion_to_start_age",
    "score", "wealth_score", "career_score", "fortune_score",
    "strength_score", "modern_score",
    "income", "salary", "prediction", "investment_advice",
    "industry_recommendation", "useful_god", "overall_strength",
    "fuyi_candidate_stems", "candidate_stems",
))
# Conditional conclusions carried at most this many (verbatim, with
# the engine's own reason strings); the total count is always kept.
_MAX_CONDITIONAL_CARRIED = 12

_NOT_CLAIMED = (
    "不预测收入、财富多少、升迁、跳槽或投资结果。",
    "不输出事业指数、财运指数或任何分数。",
    "不推荐行业、职业方向或具体岗位。",
    "不判定大运、流年对原局的实际作用效力（无已审跨层效力规则）。",
    "不作流年喜用推演（TJ-023.3 阻塞）与统一喜用裁决（TJ-013.2 裁决 A，恒拒判）。",
    "六爻事业官职用神映射未获批，不作问占口径呈现。",
)


def _fail(message):
    raise ValueError("Career presentation rejected: " + message)


def _banned_scan(value):
    if isinstance(value, dict):
        for key, item in value.items():
            if key in _BANNED_KEYS:
                _fail("banned key in presentation: " + str(key))
            _banned_scan(item)
    elif isinstance(value, list):
        for item in value:
            _banned_scan(item)


def _require_str(mapping, key, label):
    value = mapping.get(key)
    if not isinstance(value, str) or not value:
        _fail(label + " must be a non-empty string")
    return value


def _section(section_id, title, basis, caliber, status, content,
             undecided_conditions):
    return {
        "id": section_id,
        "title": title,
        "basis": basis,
        "caliber": caliber,
        "status": status,
        "content": content,
        "undecided_conditions": list(undecided_conditions),
    }


def _natal_section(result):
    """Section 1: natal Ten-God structure + lifted public gates."""
    natal = result.get("natal")
    if not isinstance(natal, dict):
        _fail("career result lacks natal")
    day_master = natal.get("day_master")
    if not isinstance(day_master, dict):
        _fail("career result lacks natal day_master")
    day_stem = _require_str(day_master, "stem", "day master stem")
    pillars = natal.get("pillars")
    if not isinstance(pillars, list) or len(pillars) != 4:
        _fail("career result natal must carry four pillars")
    month_branch = None
    for pillar in pillars:
        if isinstance(pillar, dict) and pillar.get("name") == "month":
            branch = pillar.get("branch")
            if isinstance(branch, dict):
                month_branch = branch.get("value")
    if not isinstance(month_branch, str) or not month_branch:
        _fail("career result lacks month branch")

    groups_in = result.get("structure_groups")
    if not isinstance(groups_in, dict):
        _fail("career result lacks structure_groups")
    cards_in = result.get("interpretation_cards")
    if not isinstance(cards_in, list):
        _fail("career result lacks interpretation_cards")
    cards = {}
    for card in cards_in:
        if not isinstance(card, dict) or "group_id" not in card:
            _fail("interpretation card must carry group_id")
        cards[card["group_id"]] = card

    groups = []
    for group_id in _GROUP_ORDER:
        group = groups_in.get(group_id)
        if not isinstance(group, dict):
            _fail("structure_groups lacks " + group_id)
        card = cards.get(group_id)
        if card is None:
            _fail("interpretation_cards lacks " + group_id)
        occurrences = group.get("occurrences")
        if not isinstance(occurrences, list):
            _fail("structure group occurrences must be a list")
        clean_occurrences = []
        for item in occurrences:
            if not isinstance(item, dict):
                _fail("occurrence must be a mapping")
            for key in ("pillar", "layer", "stem", "ten_god"):
                if not isinstance(item.get(key), str) or not item[key]:
                    _fail("occurrence lacks " + key)
            clean_occurrences.append({
                "pillar": item["pillar"],
                "layer": item["layer"],
                "stem": item["stem"],
                "ten_god": item["ten_god"],
            })
        visible = group.get("visible_count")
        hidden = group.get("hidden_count")
        if type(visible) is not int or type(hidden) is not int:
            _fail("structure group counts must be integers")
        if len(clean_occurrences) != visible + hidden:
            _fail("structure group occurrence count drifted from counts")
        if card.get("interpretation_level") != \
                "reviewed_structural_relation_only":
            _fail("interpretation card level drifted")
        if card.get("personal_prediction") is not False:
            _fail("interpretation card must not carry a prediction")
        groups.append({
            "group_id": group_id,
            "label": _require_str(group, "label", "group label"),
            "ten_gods": list(group.get("ten_gods") or []),
            "five_element_relation": _require_str(
                card, "five_element_relation", "five element relation"),
            "visible_count": visible,
            "hidden_count": hidden,
            "occurrences": clean_occurrences,
            "observation": _require_str(
                card, "observation", "group observation"),
            "target_year_stem_matches_group": bool(
                card.get("target_year_stem_matches_group")),
        })

    target = result.get("target_year")
    if not isinstance(target, dict):
        _fail("career result lacks target_year")
    target_year = target.get("year")
    if type(target_year) is not int:
        _fail("target year must be an integer")
    flow_year = {
        "year": target_year,
        "ganzhi": _require_str(target, "ganzhi", "flow year ganzhi"),
        "stem": _require_str(target, "stem", "flow year stem"),
        "branch": _require_str(target, "branch", "flow year branch"),
        "stem_ten_god": _require_str(
            target, "stem_ten_god", "flow year stem ten god"),
        "structure_group": _require_str(
            target, "structure_group", "flow year structure group"),
    }

    # Lifted public gates: re-validate each with its own closed-shape
    # validator; an invalid or missing lift fails the whole build.
    strength = result.get("strength_presentation")
    if not is_valid_public_strength_presentation(strength):
        _fail("strength presentation lift is not valid")
    pattern = result.get("pattern_presentation")
    if not is_valid_public_pattern_presentation(pattern):
        _fail("pattern presentation lift is not valid")
    xiyong = result.get("xiyong_presentation")
    if not is_valid_public_xiyong_presentation(xiyong):
        _fail("xiyong presentation lift is not valid")
    if xiyong.get("unified_verdict") is not None:
        _fail("xiyong unified verdict must stay None (TJ-013.2 A)")
    lifted = {
        "strength": {
            "variant": strength["variant"],
            "status": strength["status"],
            "classification": strength.get("classification"),
            "predicate_id": strength.get("predicate_id"),
            "reason": strength.get("reason"),
        },
        "pattern": {
            "variant": pattern["variant"],
            "status": pattern["status"],
            "outcome": pattern.get("outcome"),
            "pattern": pattern.get("pattern"),
            "reason": pattern.get("reason"),
        },
        "xiyong": {
            "variant": xiyong["variant"],
            "unified_verdict": None,
            "presentation_scope": xiyong.get("presentation_scope"),
        },
    }
    content = {
        "day_master": day_stem,
        "month_branch": month_branch,
        "groups": groups,
        "flow_year": flow_year,
        "lifted_presentations": lifted,
        "computed_relations": (
            "十神映射（bazi.phase2.ten_gods）",
            "藏干映射（bazi.phase2.hidden_stems）",
            "流年天干十神（同一十神映射）",
        ),
    }
    return _section(
        "natal_ten_gods", "原局十神位置",
        "bazi.phase2.ten_gods / bazi.phase2.hidden_stems；"
        "已开放门控 U1（旺衰）/ D-1（寅月真格）/ 喜用 phase-1（调候+病药）",
        "结构事实：只陈述十神在天干/藏干的位置与已开放呈现，"
        "不比较旺衰、月令权重，不作全局强弱、格局成立或喜用判断",
        "presented", content,
        (
            "全盘旺衰：除已审谓词命中外暂不可判（未命中不等于弱）。",
            "格局：除 D-1 任氏寅月局部真格外，逐格成立与破格暂不可判；"
            "比肩/劫财格不在公开白名单内。",
            "格局用神：14 格全部待证据审查，useful_god 恒未审。",
            "扶抑古典方向：十行全部含量化词且未阈值化，已裁定关闭，不重提。",
            "从格/化气成立：无已审规则，只有候选屏，暂不可判。",
        ))


def _check_trimmed_dayun(dayun):
    """Validate the career envelope's first-period-trimmed dayun.

    The envelope field stays first-period-only by the trim contract
    (``_first_period_dayun_for_career_life``): any interval on
    periods 2-8 there is a wiring leak and fails closed. The full
    timeline comes from the separate full presentation, never by
    un-trimming this field.
    """
    if dayun is None:
        return
    if not is_valid_public_dayun_presentation(dayun):
        _fail("trimmed dayun presentation is not valid")
    methods_in = dayun.get("methods")
    if not isinstance(methods_in, dict):
        _fail("trimmed dayun presentation lacks methods")
    for method in ("sanming", "shenfeng"):
        view = methods_in.get(method)
        if not isinstance(view, dict):
            _fail("trimmed dayun presentation lacks method: " + method)
        entries = view.get("entries")
        if not isinstance(entries, list) or len(entries) != 8:
            _fail("trimmed dayun method must carry 8 entries: " + method)
        for entry in entries[1:]:
            if not isinstance(entry, dict):
                _fail("trimmed dayun entry must be a mapping: " + method)
            if entry.get("start_interval") is not None:
                _fail("trimmed dayun periods 2-8 must not carry "
                      "an interval: " + method)


def _first_period_entry(method_view, method):
    entries = method_view.get("entries")
    if not isinstance(entries, list) or not entries:
        _fail("dayun method lacks entries: " + method)
    first = entries[0]
    if not isinstance(first, dict) or first.get("period_index") != 1:
        _fail("dayun first entry must be period 1: " + method)
    interval = first.get("start_interval")
    if interval is not None:
        if not isinstance(interval, dict):
            _fail("dayun first interval must be a mapping: " + method)
        earliest = interval.get("earliest")
        latest = interval.get("latest")
        if not isinstance(earliest, str) or not earliest \
                or not isinstance(latest, str) or not latest:
            _fail("dayun first interval lacks bounds: " + method)
        interval = {"earliest": earliest, "latest": latest}
    return {
        "period_index": 1,
        "ganzhi": _require_str(first, "ganzhi", "first period ganzhi"),
        "ten_god": _require_str(
            first, "ten_god_relative_to_natal_day_stem",
            "first period ten god"),
        "state": _require_str(first, "state", "first period state"),
        "start_interval": interval,
    }


def _interval_bounds(entry, method):
    interval = entry.get("start_interval")
    if interval is None:
        return None
    if not isinstance(interval, dict):
        _fail("dayun interval must be a mapping: " + method)
    earliest = interval.get("earliest")
    latest = interval.get("latest")
    if not isinstance(earliest, str) or not earliest \
            or not isinstance(latest, str) or not latest:
        _fail("dayun interval lacks bounds: " + method)
    return {"earliest": earliest, "latest": latest}


def _liunian_query(interval):
    """Liunian query entry for one period: the year of the interval's
    earliest bound, nothing more. No period membership is asserted
    for the whole year, and no dayun x liunian efficacy is implied;
    the query only opens the year's own flow-year facts.
    """
    if interval is None:
        return {
            "available": False,
            "query_year": None,
            "note": "本运无交运区间，未提供流年查询入口。",
        }
    earliest = interval["earliest"]
    year_text = earliest[:4]
    if len(year_text) != 4 or not year_text.isdigit():
        _fail("dayun interval earliest is not an ISO datetime")
    return {
        "available": True,
        "query_year": int(year_text),
        "note": "查询该运起始年（区间下限所在年）的流年干支；"
                "流年与大运的相互作用效力暂不可判。",
    }


def _timeline_periods(method_view, method, day_master,
                      natal_relations_by_period,
                      conditional_by_period, combo_periods):
    entries_in = method_view.get("entries")
    if not isinstance(entries_in, list) or len(entries_in) != 8:
        _fail("dayun method must carry 8 entries: " + method)
    combo_by_index = None
    if combo_periods is not None:
        combo_by_index = {}
        for row in combo_periods:
            if not isinstance(row, dict) \
                    or type(row.get("period_index")) is not int:
                _fail("combination dayun period lacks period_index")
            combo_by_index[row["period_index"]] = row
        if sorted(combo_by_index) != list(range(1, 9)):
            _fail("combination dayun must carry periods 1-8")
    periods = []
    for position, entry in enumerate(entries_in, start=1):
        if not isinstance(entry, dict) \
                or entry.get("period_index") != position:
            _fail("dayun entry period_index drifted: " + method)
        ganzhi = _require_str(entry, "ganzhi", "dayun period ganzhi")
        stem = _require_str(entry, "stem", "dayun period stem")
        branch = _require_str(entry, "branch", "dayun period branch")
        if ganzhi != stem + branch:
            _fail("dayun period ganzhi drifted from stem+branch: "
                  + method)
        ten_god = _require_str(
            entry, "ten_god_relative_to_natal_day_stem",
            "dayun period ten god")
        state = _require_str(entry, "state", "dayun period state")
        if state not in ("interval", "unresolved", "not_provided"):
            _fail("dayun period state unknown: " + method)
        interval = _interval_bounds(entry, method)
        if state == "interval" and interval is None:
            _fail("dayun interval state without an interval: " + method)
        if state != "interval" and interval is not None:
            _fail("dayun non-interval state carrying an interval: "
                  + method)
        if method == "shenfeng" and position > 1 \
                and state != "not_provided":
            _fail("shenfeng periods 2-8 are not_provided by "
                  "registered design: " + method)
        if method == "sanming" and state == "not_provided":
            _fail("sanming periods are never not_provided: " + method)
        if combo_by_index is not None:
            combo = combo_by_index[position]
            if combo.get("candidate_ganzhi") != ganzhi \
                    or combo.get("stem_ten_god") != ten_god:
                _fail("dayun presentation drifted from the "
                      "combination candidate sequence: " + method)
        # Branch hidden stems reuse the existing reviewed lookup
        # (same foundations table as the natal hidden stems). The
        # table lives in the sealed canonical store: when it is
        # unavailable (public checkout) the period degrades
        # EXPLICITLY (hidden_stems None + not_available status),
        # never with invented stems; the sealed run carries them.
        try:
            hidden = _hidden_stems_for_branch(branch, day_master)
        except (FileNotFoundError, OSError):
            hidden = None
        if hidden is None:
            hidden_clean = None
            hidden_status = "not_available"
        else:
            hidden_clean = []
            for item in hidden:
                if not isinstance(item, dict) \
                        or not isinstance(item.get("stem"), str) \
                        or not isinstance(item.get("ten_god"), str):
                    _fail("hidden stem shape drifted: " + branch)
                hidden_clean.append({"stem": item["stem"],
                                     "ten_god": item["ten_god"]})
            hidden_status = "available"
        relations = natal_relations_by_period.get(position, [])
        counts_by_kind = {}
        for relation in relations:
            kind = relation.get("kind")
            if not isinstance(kind, str) or not kind:
                _fail("natal relation lacks a kind")
            counts_by_kind[kind] = counts_by_kind.get(kind, 0) + 1
        periods.append({
            "period_index": position,
            "ganzhi": ganzhi,
            "stem": stem,
            "branch": branch,
            "stem_ten_god": ten_god,
            "state": state,
            "start_interval": interval,
            "start_interval_status": entry.get("start_interval_status"),
            # No numeric age, ever: the registered timeline view
            # declares age_presentation='not_presented'; the
            # handover interval itself is the period's time range.
            "age_presentation": "not_presented",
            "hidden_stems": hidden_clean,
            "hidden_stems_status": hidden_status,
            "natal_relations": {
                "total": len(relations),
                "counts_by_kind": counts_by_kind,
                "conditional_conclusions":
                    copy.deepcopy(conditional_by_period.get(
                        position, [])),
                "note": ("已审地支关系（六合/六害/六冲）与天干五行方向"
                         "事实；生克方向事实不等于效力。"),
            },
            "liunian_query": _liunian_query(interval),
        })
    return periods


def _dayun_section(result, full_dayun, combination):
    """Section 2: full 8-period dayun timeline (Q3=A, 2026-11-28).

    Sources, in order: the validated full dayun presentation for
    intervals + direction (same birth instant and role as the career
    envelope), cross-checked against the combination block's
    ``candidate_sequence(periods=8)`` rows; branch hidden stems from
    the existing ``bazi_core.hidden_stems`` lookup; reviewed natal
    relations from the combination engine. No age is computed: the
    handover interval is the only time range shown.
    """
    day_master = result["natal"]["day_master"]["stem"]
    undecided = (
        "起运岁数不折算、不呈现（age_presentation 恒 not_presented，"
        "无原典口径）；交运时间只给区间，不给单点日期。",
        "神峰口径第 2–8 运区间未提供：日级十年平移未推导，"
        "属已注册设计，非本场景扣留。",
        "当期运未显式指定时记为未确定，不由本呈现推导。",
        "大运与原局、流年的相互作用效力未裁定，见第三节。",
    )
    trimmed = result.get("dayun_presentation")
    _check_trimmed_dayun(trimmed)
    if full_dayun is None:
        if trimmed is None:
            return _section(
                "dayun_timeline", "大运 8 运时间线",
                "未启用：未选择传统大运口径（male/female）",
                "未呈现：无传统口径即无大运，不默认、不推断口径",
                "not_presented",
                {"traditional_role_selected": False,
                 "methods": None,
                 "note": "未选择传统大运口径，因此不呈现大运。"
                         "如需查看 8 运时间线，请选择口径后重新计算。"},
                undecided)
        methods_in = trimmed["methods"]
        methods = {}
        for method in ("sanming", "shenfeng"):
            methods[method] = {
                "status": _require_str(
                    methods_in[method], "status", "dayun method status"),
                "direction_label": (
                    methods_in[method].get("direction") or {}).get("label"),
                "first_period": _first_period_entry(
                    methods_in[method], method),
                "full_timeline": "not_attached",
            }
        return _section(
            "dayun_timeline", "大运 8 运时间线",
            "bazi_dayun_public（dayun-public-presentation-v1）经首运裁剪；"
            "三命/神峰两口径并列",
            "区间口径：首运只给交运区间（左闭右开），不折算起运岁数或单点日期",
            "first_period_only",
            {"traditional_role_selected": True, "methods": methods,
             "note": "完整 8 运时间线未附带：本信封只含首运裁剪；"
                     "需同瞬时完整大运呈现才可呈现 8 运。"},
            undecided)
    if not is_valid_public_dayun_presentation(full_dayun):
        _fail("full dayun presentation is not valid")
    methods_in = full_dayun.get("methods")
    if not isinstance(methods_in, dict):
        _fail("full dayun presentation lacks methods")
    # Combination inputs for cross-check + natal relations.
    combo_periods = None
    natal_relations_by_period = {}
    conditional_by_period = {}
    if combination is not None:
        if not isinstance(combination, dict):
            _fail("combination must be a mapping")
        dayun_block = combination.get("dayun")
        if not isinstance(dayun_block, dict):
            _fail("combination lacks dayun block")
        combo_periods = dayun_block.get("periods")
        if not isinstance(combo_periods, list) \
                or len(combo_periods) != 8:
            _fail("combination dayun must carry 8 periods")
        relations = combination.get("structural_relations")
        if not isinstance(relations, list):
            _fail("combination lacks structural_relations")
        relation_period = {}
        for relation in relations:
            if not isinstance(relation, dict):
                _fail("structural relation must be a mapping")
            if relation.get("scope") != "dayun_x_natal":
                continue
            period_index = relation.get("period_index")
            if type(period_index) is not int:
                _fail("natal relation lacks a period_index")
            natal_relations_by_period.setdefault(
                period_index, []).append(relation)
            relation_period[relation.get("id")] = period_index
        effects = combination.get("effects") or {}
        for entry in effects.get("conditional_effects") or []:
            if not isinstance(entry, dict):
                _fail("conditional effect entry must be a mapping")
            period_index = relation_period.get(entry.get("relation_id"))
            if period_index is None:
                continue
            conclusions = entry.get("conclusions")
            if not isinstance(conclusions, list):
                _fail("conditional effect entry lacks conclusions")
            for conclusion in conclusions:
                if not isinstance(conclusion, dict) \
                        or conclusion.get("verdict") \
                        not in CONDITIONAL_VERDICTS:
                    _fail("unknown conditional conclusion verdict")
                conditional_by_period.setdefault(
                    period_index, []).append({
                        "verdict": conclusion["verdict"],
                        "side": conclusion.get("side"),
                        "stem": conclusion.get("stem"),
                        "ten_god": conclusion.get("ten_god"),
                        "reason": _require_str(
                            conclusion, "reason",
                            "conditional conclusion reason"),
                    })
    methods = {}
    for method in ("sanming", "shenfeng"):
        view = methods_in.get(method)
        if not isinstance(view, dict):
            _fail("full dayun presentation lacks method: " + method)
        methods[method] = {
            "status": _require_str(view, "status", "dayun method status"),
            "direction_label": (
                view.get("direction") or {}).get("label"),
            "entries": _timeline_periods(
                view, method, day_master, natal_relations_by_period,
                conditional_by_period, combo_periods),
        }
    return _section(
        "dayun_timeline", "大运 8 运时间线",
        "bazi_dayun_public（dayun-public-presentation-v1）完整呈现；"
        "三命/神峰两口径并列；干支与十神经组合引擎 "
        "candidate_sequence(periods=8) 逐运核对",
        "区间口径：每运只给交运区间（左闭右开），不折算起运岁数或单点日期",
        "presented",
        {"traditional_role_selected": True, "methods": methods,
         "interval_note": "起运岁数不折算、不呈现：已注册时间线视图本身"
                     "声明 age_presentation='not_presented'；"
                     "交运区间即本运的时间范围。"},
        undecided)


def _linkage_section(combination, combination_note):
    """Section 3: natal-luck linkage -- condition conclusions only."""
    undecided = (
        "跨层效力（原局＋大运＋流年跨规则调用，TJ-017.2 真定义）："
        "无已审规则，注册表恒为空，overall_effect 恒为 None。",
        "流年喜用推演（TJ-023.3）：4 项推演全部待立项，暂不可判。",
        "地支刑：刑表不存在，不评估。",
        "大运×流年期位映射：除非调用方显式指定当期运及其依据，"
        "否则记为未确定。",
    )
    if combination is None:
        return _section(
            "natal_luck_linkage", "原局与大运流年的关联",
            "未装配：统一入口未给出组合块",
            "未呈现：无组合装配即无条件结论，不补推",
            "not_assembled",
            {"overall_effect": None,
             "rules_registered": [],
             "conditional_count": None,
             "conditional_conclusions": [],
             "note": combination_note
                     or "组合块未装配：无传统口径或无目标年时组合不装配。"},
            undecided)
    if not isinstance(combination, dict):
        _fail("combination must be a mapping")
    if combination.get("variant") != COMBINATION_VARIANT:
        _fail("combination variant drifted")
    if combination.get("research_only") is not True \
            or combination.get("public_enabled") is not False \
            or combination.get("ai_enabled") is not False:
        _fail("combination governance flags drifted")
    if combination.get("overall_effect") is not None:
        _fail("combination overall_effect must stay None")
    effects = combination.get("effects")
    if not isinstance(effects, dict):
        _fail("combination lacks effects")
    if effects.get("overall_effect") is not None:
        _fail("combination effects overall_effect must stay None")
    efficacy = effects.get("cross_layer_efficacy")
    if not isinstance(efficacy, dict):
        _fail("combination lacks cross_layer_efficacy")
    if efficacy.get("status") != "no_reviewed_rules" \
            or efficacy.get("rules_registered") != [] \
            or efficacy.get("overall_effect") is not None:
        _fail("cross-layer efficacy registry must stay empty")
    conditional = effects.get("conditional_effects")
    if not isinstance(conditional, list):
        _fail("combination lacks conditional_effects")
    conditional_count = effects.get("conditional_count")
    if type(conditional_count) is not int \
            or conditional_count != len(conditional):
        _fail("combination conditional count drifted")
    verdict_rows = efficacy.get("conditional_verdicts")
    if not isinstance(verdict_rows, list):
        _fail("combination lacks conditional verdict rows")
    counts_by_verdict = {}
    for row in verdict_rows:
        if not isinstance(row, dict):
            _fail("conditional verdict row must be a mapping")
        verdict = row.get("verdict")
        if verdict not in CONDITIONAL_VERDICTS:
            _fail("unknown conditional verdict: " + str(verdict))
        if row.get("treated_as_efficacy") is not False:
            _fail("conditional verdict must not be treated as efficacy")
        counts_by_verdict[verdict] = row.get("occurrences")
    carried = []
    for entry in conditional[:_MAX_CONDITIONAL_CARRIED]:
        if not isinstance(entry, dict):
            _fail("conditional effect entry must be a mapping")
        conclusions = entry.get("conclusions")
        if not isinstance(conclusions, list):
            _fail("conditional effect entry lacks conclusions")
        clean_conclusions = []
        for conclusion in conclusions:
            if not isinstance(conclusion, dict):
                _fail("conditional conclusion must be a mapping")
            verdict = conclusion.get("verdict")
            if verdict not in CONDITIONAL_VERDICTS:
                _fail("unknown conditional conclusion verdict")
            clean_conclusions.append({
                "verdict": verdict,
                "side": conclusion.get("side"),
                "stem": conclusion.get("stem"),
                "ten_god": conclusion.get("ten_god"),
                "reason": _require_str(
                    conclusion, "reason", "conditional conclusion reason"),
            })
        carried.append({
            "relation_id": entry.get("relation_id"),
            "scope": _require_str(entry, "scope", "relation scope"),
            "kind": _require_str(entry, "kind", "relation kind"),
            "verdicts": list(entry.get("verdicts") or []),
            "conclusions": clean_conclusions,
        })
    summary = combination.get("relation_summary")
    total_relations = None
    if isinstance(summary, dict):
        total_relations = summary.get("total")
    content = {
        "overall_effect": None,
        "rules_registered": [],
        "efficacy_status": "no_reviewed_rules",
        "total_relations": total_relations,
        "conditional_count": conditional_count,
        "conditional_carried": len(carried),
        "counts_by_verdict": counts_by_verdict,
        "conditional_conclusions": carried,
        "abstain_gaps": list(efficacy.get("abstain_gaps") or []),
        "note": ("条件结论只记存在性事实或现代工程模型的处理口径，"
                 "不是跨层效力断言；无依据者仍 abstain。"),
    }
    return _section(
        "natal_luck_linkage", "原局与大运流年的关联",
        "bazi-combination-engine-v1（组合引擎条件结论层）；"
        "TJ-017.2 真定义仍阻塞，效力层注册表恒为空",
        "存在性事实：只陈述大运/流年干与原局引用干的同字/同十神"
        "等存在性事实，不作效力断言",
        "assembled", content, undecided)


def _boundaries_section():
    """Section 4: grounded traditional analysis only -- what is not said."""
    return _section(
        "grounded_boundaries", "不能下的结论",
        "用户裁定与产品边界：TJ-013.2 裁决 A、TJ-017.2 真定义阻塞、"
        "TJ-023.3 阻塞、D7（B15）未裁定、B3 六爻映射未获批",
        "白话边界：凡未算出的，一律明说暂不可判，不以近似值、"
        "分数或预测填补",
        "presented",
        {"not_claimed": list(_NOT_CLAIMED)},
        (
            "行业映射、紫微交叉判断：无已审规则，暂不可判。",
            "应期推演：无已审应期条件，暂不可判。",
            "出空/填实/解破：无已登记依据，不建。",
        ))


def build_career_presentation(career_result, combination=None,
                              combination_note=None,
                              full_dayun_presentation=None):
    """Build the plain-language career presentation for one career result.

    ``career_result`` is the ``result`` dict of a ``_career`` envelope
    (same birth instant, same target year). ``combination`` is the
    unified-compute combination block for the same inputs
    (``trim_for_career`` research ``combination``), or None when the
    entry did not assemble one. ``full_dayun_presentation`` is the
    validated FULL dayun public presentation for the same birth
    instant and role (the bazi-profile gate's object, 8 periods);
    without it the timeline section degrades to first-period-only
    (the envelope's own trimmed field) or not-presented. Returns a
    JSON-able dict. Raises ``ValueError`` on any drift, forgery or
    ungrounded input -- the caller must fail the request, never
    return a partial presentation.
    """
    if not isinstance(career_result, dict):
        _fail("career result must be a mapping")
    sections = [
        _natal_section(career_result),
        _dayun_section(career_result, full_dayun_presentation,
                       combination),
        _linkage_section(combination, combination_note),
        _boundaries_section(),
    ]
    natal = career_result["natal"]
    day_master = natal["day_master"]["stem"]
    month_branch = None
    for pillar in natal["pillars"]:
        if pillar.get("name") == "month":
            month_branch = pillar["branch"]["value"]
    presentation = {
        "variant": VARIANT,
        "public_enabled": True,
        "ai_enabled": False,
        "day_master": day_master,
        "month_branch": month_branch,
        "target_year": career_result["target_year"]["year"],
        "sections": sections,
        "scope_statement": SCOPE_STATEMENT,
        "limitations": list(LIMITATIONS),
    }
    _banned_scan(presentation)
    return presentation


_SECTION_IDS = ("natal_ten_gods", "dayun_timeline",
                "natal_luck_linkage", "grounded_boundaries")


def is_valid_career_presentation(obj):
    """Closed-shape validator for the projection's scoped release.

    Exact top-level key set, verbatim variant/scope/limitations, the
    four sections in order with exact per-section keys, overall_effect
    None wherever it appears, no banned keys, and the full 8-period
    timeline: 8 entries per method when presented, interval-only
    precision, age_presentation always not_presented, and no numeric
    age anywhere.
    """
    if not isinstance(obj, dict):
        return False
    if set(obj) != {"variant", "public_enabled", "ai_enabled",
                    "day_master", "month_branch", "target_year",
                    "sections", "scope_statement", "limitations"}:
        return False
    if obj.get("variant") != VARIANT:
        return False
    if obj.get("public_enabled") is not True \
            or obj.get("ai_enabled") is not False:
        return False
    if obj.get("scope_statement") != SCOPE_STATEMENT:
        return False
    if obj.get("limitations") != list(LIMITATIONS):
        return False
    if not isinstance(obj.get("day_master"), str) or not obj["day_master"]:
        return False
    if not isinstance(obj.get("month_branch"), str) \
            or not obj["month_branch"]:
        return False
    if type(obj.get("target_year")) is not int:
        return False
    sections = obj.get("sections")
    if not isinstance(sections, list) \
            or [s.get("id") for s in sections if isinstance(s, dict)] \
            != list(_SECTION_IDS):
        return False
    for section in sections:
        if not isinstance(section, dict):
            return False
        if set(section) != {"id", "title", "basis", "caliber", "status",
                            "content", "undecided_conditions"}:
            return False
        if not isinstance(section.get("content"), dict):
            return False
        if not isinstance(section.get("undecided_conditions"), list) \
                or not section["undecided_conditions"]:
            return False
        if not all(isinstance(c, str) and c
                   for c in section["undecided_conditions"]):
            return False
    try:
        _banned_scan(obj)
    except ValueError:
        return False
    dayun = sections[1]["content"]
    dayun_status = sections[1]["status"]
    if dayun_status not in ("presented", "first_period_only",
                            "not_presented"):
        return False
    if dayun_status == "presented":
        methods = dayun.get("methods")
        if not isinstance(methods, dict):
            return False
        for method in ("sanming", "shenfeng"):
            view = methods.get(method)
            if not isinstance(view, dict):
                return False
            entries = view.get("entries")
            if not isinstance(entries, list) or len(entries) != 8:
                return False
            for position, entry in enumerate(entries, start=1):
                if not isinstance(entry, dict):
                    return False
                if set(entry) != {
                        "period_index", "ganzhi", "stem", "branch",
                        "stem_ten_god", "state", "start_interval",
                        "start_interval_status", "age_presentation",
                        "hidden_stems", "hidden_stems_status",
                        "natal_relations", "liunian_query"}:
                    return False
                if entry.get("period_index") != position:
                    return False
                if entry.get("age_presentation") != "not_presented":
                    return False
                hidden = entry.get("hidden_stems")
                hidden_status = entry.get("hidden_stems_status")
                if hidden_status == "available":
                    if not isinstance(hidden, list) or not hidden:
                        return False
                    for item in hidden:
                        if not isinstance(item, dict) \
                                or set(item) != {"stem", "ten_god"}:
                            return False
                elif hidden_status == "not_available":
                    if hidden is not None:
                        return False
                else:
                    return False
                if entry.get("ganzhi") != entry.get("stem") \
                        + entry.get("branch"):
                    return False
                interval = entry.get("start_interval")
                if entry.get("state") == "interval":
                    if not isinstance(interval, dict) \
                            or set(interval) != {"earliest", "latest"}:
                        return False
                elif interval is not None:
                    return False
                query = entry.get("liunian_query")
                if not isinstance(query, dict) \
                        or set(query) != {"available", "query_year",
                                          "note"}:
                    return False
                if query.get("available") is True:
                    if type(query.get("query_year")) is not int:
                        return False
                elif query.get("query_year") is not None:
                    return False
                relations = entry.get("natal_relations")
                if not isinstance(relations, dict) \
                        or set(relations) != {
                            "total", "counts_by_kind",
                            "conditional_conclusions", "note"}:
                    return False
                counts = relations.get("counts_by_kind")
                if not isinstance(counts, dict) \
                        or not all(isinstance(v, int)
                                   for v in counts.values()) \
                        or relations.get("total") != sum(counts.values()):
                    return False
                for conclusion in relations.get(
                        "conditional_conclusions", []):
                    if not isinstance(conclusion, dict) \
                            or conclusion.get("verdict") \
                            not in CONDITIONAL_VERDICTS:
                        return False
    elif dayun_status == "first_period_only":
        methods = dayun.get("methods")
        if not isinstance(methods, dict):
            return False
        for method in ("sanming", "shenfeng"):
            view = methods.get(method)
            if not isinstance(view, dict):
                return False
            first = view.get("first_period")
            if not isinstance(first, dict) \
                    or first.get("period_index") != 1:
                return False
            if view.get("full_timeline") != "not_attached":
                return False
    elif dayun.get("methods") is not None:
        return False
    linkage = sections[2]["content"]
    if linkage.get("overall_effect") is not None:
        return False
    if linkage.get("rules_registered") != []:
        return False
    return True


def to_public_career_presentation(candidate):
    """Allowlist projection of a validated career presentation.

    Returns a fresh dict containing ONLY the validated keys, built key
    by key -- never a verbatim copy. An invalid candidate raises
    ``ValueError``; the projection layer treats that as "strip the
    field", never as a partial release.
    """
    if not is_valid_career_presentation(candidate):
        _fail("candidate is not a valid career presentation")
    projected = {
        "variant": candidate["variant"],
        "public_enabled": True,
        "ai_enabled": False,
        "day_master": candidate["day_master"],
        "month_branch": candidate["month_branch"],
        "target_year": candidate["target_year"],
        "sections": copy.deepcopy(candidate["sections"]),
        "scope_statement": candidate["scope_statement"],
        "limitations": list(candidate["limitations"]),
    }
    _banned_scan(projected)
    return projected
