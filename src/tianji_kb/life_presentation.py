"""TJ-031.19 / E0427 Lane E: life-overview presentation (life-presentation-v1).

The life overview reuses the four sibling modules' actual computation
results and never computes a second set of algorithms:

* bazi  -> :func:`bazi_profile_presentation.build_bazi_profile_presentation`
  over the unified life trim;
* career -> :func:`career_presentation.build_career_presentation` over
  the life envelope's own career result, the unified-compute
  combination block and the validated full dayun presentation;
* romance -> a pre-built romance presentation (the romance builder
  needs the full romance envelope, which the life envelope does not
  carry; the live wrapper builds it from the same birth instant);
* compatibility -> a pre-built compatibility presentation, only when
  a partner birth is given; a single-person overview reports it as
  not applicable, never computes a pair reading for one person.

Dayun (Q3=A, 2026-11-28): the full 8-period timeline is presented on
this page. Periods are reused verbatim from the career theme's
dayun_timeline section when it is presented, else from the bazi
theme's dayun periods; the two sources are cross-checked on ganzhi
when both are present. Life stages are one stage per sanming period,
each carrying that period's already-computed facts (bazi ten-god and
hidden stems, career natal linkage, liunian query entry). The target
year's yearly/romance facts ride on the stage whose interval contains
the target year, determined only from the already-computed start
intervals; when the target year falls in no period (e.g. before the
first period starts) that is stated plainly.

No numeric age is ever shown: the registered timeline view declares
``age_presentation='not_presented'`` and the public dayun object bans
age fields (bazi_dayun_public.py §4.5/§6.2(f)). The handover interval
itself is the period's time range. Lifting that ban needs a user
decision; this module does not ask for it and does not block on it.

``interpretation_allowed`` is False everywhere: the overview aggregates
reviewed structural facts only. No strength score or fuyi candidate is
converted into a life judgement, no wealth/marriage/health/lifespan
conclusion is drawn, no score of any kind is produced.
"""

import copy
import json

from .bazi_profile_presentation import (
    VARIANT as BAZI_VARIANT,
)
from .bazi_profile_presentation import (
    build_bazi_profile_presentation,
    is_valid_bazi_profile_presentation,
)
from .career_presentation import VARIANT as CAREER_VARIANT
from .career_presentation import (
    build_career_presentation,
    is_valid_career_presentation,
)
from .compatibility_presentation import (
    PRESENTATION_VERSION as COMPAT_VERSION,
)
from .compatibility_presentation import (
    _SECTION_IDS as COMPAT_SECTION_IDS,
)
from .romance_presentation import VARIANT as ROMANCE_VARIANT
from .romance_presentation import (
    _SECTION_IDS as ROMANCE_SECTION_IDS,
)

VARIANT = "life-presentation-v1"

_TOP_KEYS = {
    "variant", "page", "public_enabled", "ai_enabled",
    "interpretation_allowed", "unified", "themes", "dayun", "stages",
    "boundary", "scope_statement", "limitations", "undecided",
}

SCOPE_STATEMENT = (
    "本总览只聚合已审公开内容与确定性结构事实；各主题内容复用八字、"
    "事业、桃花、合盘四个模块的实际计算结果，不另算一套；研究模型"
    "内容只作明确标注的研究参考，不作公开判断；暂不可判的部分如实"
    "写明，不补结论，不作人生大事的发生时间与结果推断。"
)

LIMITATIONS = (
    "人生总览只聚合已经通过校验的结构事实，不新增任何事业、收入、"
    "婚恋或人生事件推断。",
    "八字旺衰、喜用、格局与大运真实起运仍未获得生产审核，报告不得"
    "给出这些结论。",
    "大运只呈现已注册的方向与交运区间，不折算起运岁数、不给单点日期。",
    "合盘只在提供对方出生资料时呈现；单人总览不作合盘推断。",
    "AI 不参与本总览计算。",
)

# Tokens that must never appear in any string this module itself
# writes. Embedded sibling presentations are NOT swept: they passed
# their own builders' sweeps, and the bazi scope statement legitimately
# carries boundary wording this list would otherwise catch.
_BANNED_SUBSTRINGS = (
    "评分", "分数", "打分", "percent", "%", "％", "预测", "吉凶",
    "婚期", "正缘", "脱单", "注定", "桃花指数", "缘分指数",
    "财富预测", "寿命", "统一喜用", "unified_verdict",
)

_BANNED_KEYS = ("start_age", "end_age")

_CALIBER_LABELS = {"male": "传统男命口径", "female": "传统女命口径"}


def _fail(message):
    raise ValueError("Life presentation rejected: " + message)


def _require(condition, message):
    if not condition:
        _fail(message)


def _require_str(mapping, key, label):
    value = mapping.get(key) if isinstance(mapping, dict) else None
    if not isinstance(value, str) or not value:
        _fail(label + " must be a non-empty string")
    return value


def _pillars_ganzhi(pillars):
    """Return the four ganzhi strings from scenario pillar dicts."""
    if not isinstance(pillars, list) or len(pillars) != 4:
        _fail("pillars must be the four chart pillars")
    out = []
    for pillar in pillars:
        if not isinstance(pillar, dict):
            _fail("pillar must be a mapping")
        ganzhi = pillar.get("ganzhi")
        if not isinstance(ganzhi, str) or len(ganzhi) != 2:
            _fail("pillar lacks a two-character ganzhi")
        out.append(ganzhi)
    return out


def _day_master_stem(day_master):
    if isinstance(day_master, dict):
        stem = day_master.get("stem")
    elif isinstance(day_master, str):
        stem = day_master
    else:
        _fail("day master must be a mapping or a stem string")
    if not isinstance(stem, str) or len(stem) != 1:
        _fail("day master stem must be a single character")
    return stem


def _check_no_age_keys(value, where):
    """Fail closed on banned age keys anywhere; age_presentation must
    always be exactly 'not_presented'."""
    if isinstance(value, dict):
        for key, item in value.items():
            if key in _BANNED_KEYS:
                _fail("banned age key in " + where + ": " + key)
            if key == "age_presentation" and item != "not_presented":
                _fail("age_presentation must be not_presented in " + where)
            _check_no_age_keys(item, where)
    elif isinstance(value, list):
        for item in value:
            _check_no_age_keys(item, where)


def _sweep_own_strings(value):
    """Banned-token sweep over strings this module itself writes."""
    if isinstance(value, str):
        for token in _BANNED_SUBSTRINGS:
            if token in value:
                _fail("life presentation carries banned wording: " + token)
    elif isinstance(value, dict):
        for item in value.values():
            _sweep_own_strings(item)
    elif isinstance(value, list):
        for item in value:
            _sweep_own_strings(item)


def _section_ids(sections, label):
    if not isinstance(sections, list):
        _fail(label + " sections must be a list")
    ids = []
    for section in sections:
        if not isinstance(section, dict) or not isinstance(
                section.get("id"), str):
            _fail(label + " section lacks an id")
        ids.append(section["id"])
    return ids


def _find_section(presentation, section_id):
    for section in presentation.get("sections") or []:
        if isinstance(section, dict) and section.get("id") == section_id:
            return section
    return None


def _validate_identity(envelope_result, life_trim):
    """Re-verify the four-source identity the life scenario itself
    enforces, from the envelope's own sub-results. Any drift fails
    closed here too, so a presentation can never be built over a
    mismatched composition."""
    profile = envelope_result.get("profile")
    if not isinstance(profile, dict):
        _fail("life result lacks a profile section")
    pillars = _pillars_ganzhi(profile.get("pillars"))
    day_master = _day_master_stem(profile.get("day_master"))
    target_year = envelope_result.get("target_year")
    if type(target_year) is not int:
        _fail("life target year must be an integer")
    yearly = envelope_result.get("yearly")
    romance = envelope_result.get("romance")
    career = envelope_result.get("career")
    for label, section in (("yearly", yearly), ("romance", romance),
                           ("career", career)):
        if not isinstance(section, dict):
            _fail("life result lacks a " + label + " section")
        natal = section.get("natal")
        if not isinstance(natal, dict):
            _fail(label + " section lacks a natal chart")
        if _pillars_ganzhi(natal.get("pillars")) != pillars:
            _fail("cross-scenario natal chart identity mismatch: " + label)
        if _day_master_stem(natal.get("day_master")) != day_master:
            _fail("cross-scenario day master mismatch: " + label)
        annual = section.get("target_year")
        if not isinstance(annual, dict):
            _fail(label + " section lacks a target year")
        if annual.get("year") != target_year:
            _fail("cross-scenario target year mismatch: " + label)
    target = yearly.get("target_year")
    if not isinstance(target, dict):
        _fail("yearly section lacks a target year")
    target_ganzhi = _require_str(target, "ganzhi", "target year ganzhi")
    target_branch = _require_str(target, "branch", "target year branch")
    for label, section in (("romance", romance), ("career", career)):
        annual = section.get("target_year")
        if annual.get("ganzhi") != target_ganzhi:
            _fail("cross-scenario target ganzhi mismatch: " + label)
        if annual.get("branch") != target_branch:
            _fail("cross-scenario target branch mismatch: " + label)
    if life_trim is not None:
        if not isinstance(life_trim, dict):
            _fail("life trim must be a mapping")
        anchor = life_trim.get("identity_anchor")
        if not isinstance(anchor, dict):
            _fail("life trim lacks an identity anchor")
        if _pillars_ganzhi(anchor.get("pillars")) != pillars:
            _fail("unified assembly pillar drift")
        if _day_master_stem(anchor.get("day_master")) != day_master:
            _fail("unified assembly day master drift")
        if anchor.get("target_year") != target_year:
            _fail("unified assembly target year drift")
        if anchor.get("target_ganzhi") != target_ganzhi:
            _fail("unified assembly target ganzhi drift")
        if anchor.get("target_branch") != target_branch:
            _fail("unified assembly target branch drift")
    return {
        "pillars": pillars,
        "day_master": day_master,
        "target_year": target_year,
        "target_ganzhi": target_ganzhi,
        "target_branch": target_branch,
    }


def _check_romance_theme(presentation, identity):
    """Light identity check for a pre-built romance presentation.

    The romance builder already validated the full closed shape at
    build time; here only the variant, the section ids and the
    identity binding to this life overview are re-checked, so a
    presentation built for another chart or year can never be
    embedded here."""
    if not isinstance(presentation, dict):
        _fail("romance theme must be a mapping")
    if presentation.get("variant") != ROMANCE_VARIANT:
        _fail("romance theme variant mismatch")
    if presentation.get("scenario_id") != "romance":
        _fail("romance theme is not a romance presentation")
    if presentation.get("target_year") != identity["target_year"]:
        _fail("romance theme target year drift")
    natal = presentation.get("natal")
    if not isinstance(natal, dict):
        _fail("romance theme lacks a natal chart")
    if _pillars_ganzhi(natal.get("pillars")) != identity["pillars"]:
        _fail("romance theme pillar drift")
    if natal.get("day_master") != identity["day_master"]:
        _fail("romance theme day master drift")
    if _section_ids(presentation.get("sections"), "romance") != list(
            ROMANCE_SECTION_IDS):
        _fail("romance theme section ids drifted")


def _check_compatibility_theme(presentation, identity):
    """Light identity check for a pre-built compatibility
    presentation (same reasoning as the romance check)."""
    if not isinstance(presentation, dict):
        _fail("compatibility theme must be a mapping")
    if presentation.get("presentation_version") != COMPAT_VERSION:
        _fail("compatibility theme variant mismatch")
    if presentation.get("scenario_id") != "compatibility":
        _fail("compatibility theme is not a compatibility presentation")
    if presentation.get("interpretation_allowed") is not False:
        _fail("compatibility theme must not allow interpretation")
    if presentation.get("unified_verdict") is not None:
        _fail("compatibility theme carries a unified verdict")
    if _section_ids(presentation.get("sections"),
                    "compatibility") != list(COMPAT_SECTION_IDS):
        _fail("compatibility theme section ids drifted")
    charts = _find_section(presentation, "charts")
    if charts is None:
        _fail("compatibility theme lacks a charts section")
    content = charts.get("content")
    if not isinstance(content, dict):
        _fail("compatibility charts section lacks content")
    person_a = content.get("person_a")
    if not isinstance(person_a, dict):
        _fail("compatibility charts lack person_a")
    if _pillars_ganzhi(person_a.get("pillars")) != identity["pillars"]:
        _fail("compatibility theme person_a pillar drift")


def _project_dayun(bazi_theme, career_theme):
    """Return (methods, source) for the life dayun section.

    Primary source: the career theme's dayun_timeline section
    (already fully validated and cross-checked against the combination
    candidate sequence). Fallback: the bazi theme's dayun periods.
    The two sources are cross-checked on ganzhi when both are
    present. No numeric age is ever projected."""
    career_methods = None
    bazi_periods = None
    if isinstance(career_theme, dict):
        section = _find_section(career_theme, "dayun_timeline")
        if section is not None:
            content = section.get("content")
            if isinstance(content, dict) and content.get(
                    "traditional_role_selected") is True:
                methods = content.get("methods")
                # Only a full timeline counts: the first-period-only
                # degradation carries methods without an entries list.
                if isinstance(methods, dict) and isinstance(
                        methods.get("sanming"), dict) and isinstance(
                        methods["sanming"].get("entries"), list):
                    career_methods = methods
    if isinstance(bazi_theme, dict):
        section = _find_section(bazi_theme, "dayun")
        if section is not None:
            periods = section.get("periods")
            if isinstance(periods, dict) and periods.get("sanming"):
                bazi_periods = periods
    if career_methods is None and bazi_periods is None:
        return None, "not_presented"
    if career_methods is not None and bazi_periods is not None:
        career_ganzhi = [
            entry.get("ganzhi")
            for entry in career_methods["sanming"].get("entries") or []
        ]
        bazi_ganzhi = [
            entry.get("ganzhi") for entry in bazi_periods["sanming"]
        ]
        if career_ganzhi != bazi_ganzhi:
            _fail("career and bazi dayun timelines disagree on ganzhi")
    if career_methods is not None:
        return copy.deepcopy(career_methods), "career"
    # Bazi fallback: normalise the periods summary into the same
    # methods shape the career section uses.
    methods = {}
    for method, entries in bazi_periods.items():
        if not isinstance(entries, list):
            _fail("bazi dayun periods must be a list: " + str(method))
        normalised = []
        for position, entry in enumerate(entries, start=1):
            if not isinstance(entry, dict):
                _fail("bazi dayun period must be a mapping")
            ganzhi = _require_str(entry, "ganzhi", "dayun period ganzhi")
            normalised.append({
                "period_index": entry.get("period_index", position),
                "ganzhi": ganzhi,
                "stem": entry.get("stem", ganzhi[0]),
                "branch": entry.get("branch", ganzhi[1]),
                "stem_ten_god": entry.get("ten_god"),
                "state": "interval" if entry.get(
                    "start_interval") is not None else "not_provided",
                "start_interval": copy.deepcopy(
                    entry.get("start_interval")),
                "start_interval_status": entry.get("start_interval_status"),
                "age_presentation": "not_presented",
                "hidden_stems": copy.deepcopy(
                    entry.get("branch_hidden_stems")),
                "hidden_stems_status": (
                    "available" if entry.get("branch_hidden_stems")
                    is not None else "not_available"),
                "natal_relations": None,
                "liunian_query": (
                    {"has_entry": bool(entry.get("liunian_entry"))}
                    if entry.get("liunian_entry") is not None else None),
            })
        methods[method] = {"entries": normalised}
    return methods, "bazi"


def _interval_start_year(start_interval):
    """Year prefix of a start interval's earliest bound, or None."""
    if not isinstance(start_interval, dict):
        return None
    earliest = start_interval.get("earliest")
    if not isinstance(earliest, str) or len(earliest) < 4:
        return None
    prefix = earliest[:4]
    if not prefix.isdigit():
        return None
    return int(prefix)


def _build_stages(methods, identity, envelope_result, romance_theme):
    """One life stage per sanming period, each carrying that period's
    already-computed facts. The target year's yearly/romance facts
    ride on the stage whose interval contains the target year; when
    the target year falls in no period that is stated, not forced."""
    sanming = methods.get("sanming")
    if not isinstance(sanming, dict):
        _fail("dayun methods lack a sanming view")
    entries = sanming.get("entries")
    if not isinstance(entries, list) or len(entries) != 8:
        _fail("dayun timeline must carry 8 sanming periods")
    start_years = [_interval_start_year(entry.get("start_interval"))
                   for entry in entries]
    target_year = identity["target_year"]
    yearly_target = envelope_result["yearly"]["target_year"]
    romance_facts = None
    if isinstance(romance_theme, dict):
        linkage = _find_section(romance_theme, "dayun_liunian_linkage")
        if linkage is not None:
            romance_facts = copy.deepcopy(linkage.get("facts"))
    stages = []
    for position, entry in enumerate(entries, start=1):
        if not isinstance(entry, dict):
            _fail("dayun period must be a mapping")
        if entry.get("period_index", position) != position:
            _fail("dayun period_index drifted")
        start_year = start_years[position - 1]
        next_year = (start_years[position]
                     if position < 8 else None)
        if start_year is None or (position < 8 and next_year is None):
            contains = "unknown"
        elif next_year is None:
            contains = ("within" if target_year >= start_year
                        else "not_within")
        else:
            contains = ("within" if start_year <= target_year < next_year
                        else "not_within")
        stage = {
            "period_index": position,
            "ganzhi": _require_str(entry, "ganzhi", "stage ganzhi"),
            "stem": entry.get("stem"),
            "branch": entry.get("branch"),
            "stem_ten_god": entry.get("stem_ten_god"),
            "state": entry.get("state"),
            "start_interval": copy.deepcopy(entry.get("start_interval")),
            "start_interval_status": entry.get("start_interval_status"),
            "age_presentation": "not_presented",
            "hidden_stems": copy.deepcopy(entry.get("hidden_stems")),
            "hidden_stems_status": entry.get("hidden_stems_status"),
            "natal_relations": copy.deepcopy(entry.get("natal_relations")),
            "liunian_query": copy.deepcopy(entry.get("liunian_query")),
            "target_year_here": contains == "within",
            "target_year_containment": contains,
            "target_year_facts": None,
        }
        if contains == "within":
            stage["target_year_facts"] = {
                "yearly": copy.deepcopy(yearly_target),
                "romance_linkage_facts": romance_facts,
            }
        stages.append(stage)
    return stages


def build_life_presentation(life_envelope, *, life_trim=None,
                            combination=None,
                            full_dayun_presentation=None,
                            romance=None, compatibility=None):
    """Build the plain-language life-overview presentation.

    ``life_envelope`` is the executed ``_life`` envelope of the same
    request. ``life_trim`` is the ``trim_for_life`` output for the
    same birth instant and target year (needed for the bazi theme and
    the unified identity anchor). ``combination`` is the unified
    combination block (or None). ``full_dayun_presentation`` is the
    validated full dayun public presentation for the same birth
    instant and role (or None, in which case the career theme
    degrades per its own documented rule). ``romance`` /
    ``compatibility`` are pre-built sibling presentations (or None).
    Returns a JSON-able dict. Raises ``ValueError`` on any drift,
    forgery or ungrounded input -- the caller must fail the request,
    never return a partial presentation.
    """
    if not isinstance(life_envelope, dict):
        _fail("life envelope must be a mapping")
    if life_envelope.get("scenario_id") != "life":
        _fail("envelope is not a life scenario")
    envelope_result = life_envelope.get("result")
    if not isinstance(envelope_result, dict):
        _fail("life envelope lacks a result")
    identity = _validate_identity(envelope_result, life_trim)
    profile = envelope_result["profile"]
    day_master = profile.get("day_master")
    day_master_element = (day_master.get("element")
                          if isinstance(day_master, dict) else None)
    day_master_polarity = (day_master.get("polarity")
                           if isinstance(day_master, dict) else None)

    # --- themes: reuse, never recompute -------------------------------
    themes = {}
    if life_trim is not None:
        bazi_source = life_trim
        if full_dayun_presentation is not None:
            # The bazi theme's dayun section lifts the validated
            # presentation from the trim ("dayun_presentation"); the
            # trim itself does not carry it, so attach this request's
            # full presentation. A trim lift that disagrees with the
            # full presentation is drift and fails closed.
            existing = life_trim.get("dayun_presentation")
            if existing is None:
                bazi_source = dict(life_trim)
                bazi_source["dayun_presentation"] = copy.deepcopy(
                    full_dayun_presentation)
            elif existing != full_dayun_presentation:
                _fail("dayun presentation drift between trim and "
                      "full presentation")
        bazi_theme = build_bazi_profile_presentation(bazi_source)
        if not is_valid_bazi_profile_presentation(bazi_theme):
            _fail("built bazi theme failed its own validation")
        if bazi_theme["chart"]["ganzhi"] != identity["pillars"]:
            _fail("bazi theme chart drift")
        themes["bazi"] = bazi_theme
    else:
        themes["bazi"] = {
            "status": "not_presented",
            "reason": "未提供统一装配：八字详批主题未附带。",
        }
    career_theme = build_career_presentation(
        envelope_result["career"], combination=combination,
        full_dayun_presentation=full_dayun_presentation)
    if not is_valid_career_presentation(career_theme):
        _fail("built career theme failed its own validation")
    if career_theme.get("day_master") != identity["day_master"]:
        _fail("career theme day master drift")
    if career_theme.get("target_year") != identity["target_year"]:
        _fail("career theme target year drift")
    themes["career"] = career_theme
    if romance is not None:
        _check_romance_theme(romance, identity)
        themes["romance"] = copy.deepcopy(romance)
    else:
        themes["romance"] = {
            "status": "not_presented",
            "reason": "未提供已构建的桃花呈现：桃花主题未附带。",
        }
    if compatibility is not None:
        _check_compatibility_theme(compatibility, identity)
        themes["compatibility"] = copy.deepcopy(compatibility)
    else:
        themes["compatibility"] = {
            "status": "not_applicable",
            "reason": "单人总览不作合盘：合盘需对方出生资料，请到缘分合盘页查看。",
        }

    # --- dayun + stages (Q3=A) ---------------------------------------
    methods, dayun_source = _project_dayun(
        themes.get("bazi") if isinstance(themes.get("bazi"), dict)
        and themes["bazi"].get("variant") == BAZI_VARIANT else None,
        themes["career"])
    if methods is not None:
        stages = _build_stages(methods, identity, envelope_result,
                               themes["romance"] if isinstance(
                                   themes["romance"], dict) and themes[
                                       "romance"].get("variant") == \
                                   ROMANCE_VARIANT
                               else None)
        dayun = {
            "status": "presented",
            "source": dayun_source,
            "methods": methods,
            "note": ("完整 8 运时间线已呈现；每运只给交运区间，不折算"
                     "起运岁数，不给单点日期。"),
        }
    else:
        stages = {
            "status": "not_presented",
            "reason": "未选择传统大运口径：无口径即无大运方向，"
                      "不默认、不推断口径。",
        }
        dayun = {
            "status": "not_presented",
            "reason": "未选择传统大运口径：无口径即无大运方向，"
                      "不默认、不推断口径。",
        }

    # --- unified birth data + caliber ---------------------------------
    traditional_role = None
    if isinstance(life_trim, dict) and isinstance(
            life_trim.get("dayun"), dict):
        dayun_block = life_trim["dayun"]
        role_block = dayun_block.get("role")
        if isinstance(role_block, dict):
            traditional_role = role_block.get("traditional_role")
        if traditional_role is None:
            traditional_role = dayun_block.get("traditional_role")
    if traditional_role is None and isinstance(
            full_dayun_presentation, dict):
        role = full_dayun_presentation.get("role")
        if isinstance(role, dict):
            traditional_role = role.get("traditional_role")
    if traditional_role is not None and traditional_role not in (
            "male", "female"):
        _fail("traditional role must be male, female or absent")
    caliber = (_CALIBER_LABELS[traditional_role]
               if traditional_role in _CALIBER_LABELS
               else "未提供传统口径：大运未呈现")
    unified = {
        "pillars": list(identity["pillars"]),
        "day_master": {
            "stem": identity["day_master"],
            "element": day_master_element,
            "polarity": day_master_polarity,
        },
        "target_year": identity["target_year"],
        "target_year_ganzhi": identity["target_ganzhi"],
        "target_year_branch": identity["target_branch"],
        "traditional_role": traditional_role,
        "caliber": caliber,
        "four_source_consistent": True,
        "source_scenarios": ["profile", "yearly", "romance", "career"],
        "note": ("四路来源（命盘基础、流年结构、桃花结构、事业财运）"
                 "已核对同一出生盘与同一目标年份，无农历漂移。"),
    }

    boundary = (
        "本总览只聚合已审结构事实，不作综合判断；八字、事业、桃花、"
        "合盘四个主题各自的边界见各主题；大运与原局、流年的相互作用"
        "效力未裁定；研究模型内容只作标注的研究参考。"
    )
    undecided = [
        {"item": "人生综合判断",
         "reason": "尚无证据将四个主题合成为事业、收入、婚恋或人生定论。"},
        {"item": "起运岁数",
         "reason": "不折算、不呈现：已注册时间线视图声明 age_presentation 恒为 "
                   "not_presented，无原典口径。"},
    ]
    presentation = {
        "variant": VARIANT,
        "page": "life-overview",
        "public_enabled": True,
        "ai_enabled": False,
        "interpretation_allowed": False,
        "unified": unified,
        "themes": themes,
        "dayun": dayun,
        "stages": stages,
        "boundary": boundary,
        "scope_statement": SCOPE_STATEMENT,
        "limitations": list(LIMITATIONS),
        "undecided": undecided,
    }
    # Sweeps: own strings only (embedded sibling presentations passed
    # their own builders' sweeps); age keys across the whole object.
    _sweep_own_strings({
        "unified": unified, "dayun": dayun, "stages": stages,
        "boundary": boundary, "scope_statement": SCOPE_STATEMENT,
        "limitations": list(LIMITATIONS), "undecided": undecided,
    })
    _check_no_age_keys(presentation, "life presentation")
    if not is_valid_life_presentation(presentation):
        _fail("built life presentation failed its own validation")
    return presentation


def is_valid_life_presentation(obj):
    """Closed-shape validator for the life presentation object."""
    if not isinstance(obj, dict) or set(obj) != _TOP_KEYS:
        return False
    if obj.get("variant") != VARIANT or obj.get("page") != "life-overview":
        return False
    if obj.get("public_enabled") is not True:
        return False
    if obj.get("ai_enabled") is not False:
        return False
    if obj.get("interpretation_allowed") is not False:
        return False
    if obj.get("scope_statement") != SCOPE_STATEMENT:
        return False
    if obj.get("limitations") != list(LIMITATIONS):
        return False
    unified = obj.get("unified")
    if not isinstance(unified, dict):
        return False
    if set(unified) != {"pillars", "day_master", "target_year",
                        "target_year_ganzhi", "target_year_branch",
                        "traditional_role", "caliber",
                        "four_source_consistent", "source_scenarios",
                        "note"}:
        return False
    if unified.get("four_source_consistent") is not True:
        return False
    if unified.get("source_scenarios") != ["profile", "yearly",
                                            "romance", "career"]:
        return False
    if not isinstance(unified.get("pillars"), list) \
            or len(unified["pillars"]) != 4:
        return False
    themes = obj.get("themes")
    if not isinstance(themes, dict) or set(themes) != {
            "bazi", "career", "romance", "compatibility"}:
        return False
    dayun = obj.get("dayun")
    if not isinstance(dayun, dict) or dayun.get("status") not in (
            "presented", "not_presented"):
        return False
    if dayun["status"] == "presented":
        methods = dayun.get("methods")
        if not isinstance(methods, dict) or "sanming" not in methods:
            return False
        entries = methods["sanming"].get("entries")
        if not isinstance(entries, list) or len(entries) != 8:
            return False
    stages = obj.get("stages")
    if isinstance(stages, dict):
        if stages.get("status") != "not_presented":
            return False
    elif isinstance(stages, list):
        if len(stages) != 8:
            return False
        for stage in stages:
            if not isinstance(stage, dict):
                return False
            if set(stage) != {"period_index", "ganzhi", "stem", "branch",
                              "stem_ten_god", "state", "start_interval",
                              "start_interval_status", "age_presentation",
                              "hidden_stems", "hidden_stems_status",
                              "natal_relations", "liunian_query",
                              "target_year_here",
                              "target_year_containment",
                              "target_year_facts"}:
                return False
            if stage.get("age_presentation") != "not_presented":
                return False
    else:
        return False
    if not isinstance(obj.get("boundary"), str) or not obj["boundary"]:
        return False
    if not isinstance(obj.get("undecided"), list):
        return False
    try:
        _check_no_age_keys(obj, "life presentation")
    except ValueError:
        return False
    return True


def to_public_life_presentation(obj):
    """Allowlist projection for the life presentation.

    The object is public-safe by construction (research lives only
    inside the embedded bazi theme's explicitly labelled research
    sections, which passed their own builder). The projection is the
    final gate: exact top-level keys, validator pass, deep copy.
    """
    if not is_valid_life_presentation(obj):
        _fail("not a valid life presentation")
    return copy.deepcopy(obj)


def build_life_presentation_for(birth_value, target_year, *,
                                birth_zone=None, traditional_role=None,
                                partner_birth_value=None,
                                partner_zone=None,
                                partner_traditional_role=None):
    """Live wrapper: execute the life scenario, assemble the unified
    entry, build the sibling presentations and present them.

    Lazy engine imports keep this module importable without the
    sealed runtime. A sealed-runtime failure propagates (the caller
    decides whether it is a skip or a failure); a presentation
    rejection raises ``ValueError``.
    """
    from .scenario_engine import _dayun_public_gate, execute_scenario
    from .unified_compute import assemble_birth, trim_for_life

    from .compatibility_presentation import (
        build_compatibility_presentation_for_births,
    )
    from .romance_presentation import build_romance_presentation

    life_inputs = {"birth_value": birth_value, "target_year": target_year}
    if birth_zone is not None:
        life_inputs["birth_zone"] = birth_zone
    if traditional_role is not None:
        life_inputs["traditional_role"] = traditional_role
    life_envelope = execute_scenario("life", life_inputs)
    assembly = assemble_birth(birth_value, zone=birth_zone,
                              traditional_role=traditional_role,
                              target_year=target_year)
    life_trim = trim_for_life(assembly)
    combination = assembly.get("combination")
    full_dayun = None
    if traditional_role is not None:
        full_dayun = _dayun_public_gate(
            birth_value, zone=birth_zone, traditional_role=traditional_role)
    romance_inputs = {"birth_value": birth_value,
                      "target_year": target_year}
    if birth_zone is not None:
        romance_inputs["birth_zone"] = birth_zone
    if traditional_role is not None:
        romance_inputs["traditional_role"] = traditional_role
    romance_envelope = execute_scenario("romance", romance_inputs)
    romance_theme = build_romance_presentation(romance_envelope)
    compatibility_theme = None
    if partner_birth_value is not None:
        compatibility_theme = build_compatibility_presentation_for_births(
            birth_value, partner_birth_value,
            person_a_zone=birth_zone, person_b_zone=partner_zone,
            person_a_traditional_role=traditional_role,
            person_b_traditional_role=partner_traditional_role)
    return build_life_presentation(
        life_envelope, life_trim=life_trim, combination=combination,
        full_dayun_presentation=full_dayun, romance=romance_theme,
        compatibility=compatibility_theme)
