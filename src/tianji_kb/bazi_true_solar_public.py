"""Public allowlist projection for the true-solar comparison record.

TJ-031.19 (E0427): the ``true-solar`` scenario returns the research
record of :func:`tianji_kb.bazi_true_solar_chart.research_dual_time_chart`
-- one birth instant charted under standard time and under true
(apparent) solar time, with the per-pillar comparison. That record is
a research-only object (``research_only=True``, ``public=False``,
``ai=False``) and must never reach a public response verbatim: it
carries internal identifiers (``provenance``, ``research_api``,
``conversion_method``, ``astronomical_basis``), full chart internals
(``branch_relations``, ``auxiliary``, ``limitations``) and long
generated prose (``jieqi.note``, the adapter ``note`` /
``reuse_note``) that no public consumer reads.

This module is the scoped-release gate for that record, mirroring
``bazi_strength_public`` / ``bazi_pattern_public`` (closed-shape
validator + allowlist converter, never a verbatim copy):

* :func:`is_valid_public_true_solar_comparison` -- closed-shape
  validator for the RAW research record. It pins the exact key sets
  the research entry produces today and the research-only flags;
  a record carrying any other top-level key, a wrong entry id, or
  ``research_only`` anything but ``True`` is not valid, and the
  projection layer strips it instead of releasing it.
* :func:`to_public_true_solar_comparison` -- allowlist projection
  of a validated record. It builds a fresh dict containing ONLY the
  fields the frontend validator
  (``web/visual-prototype/src/public/api.ts`` :
  ``assertTrueSolarComparison``) and the bazi-profile page
  (``BaziProfilePage.tsx`` : the ``.bazi-true-solar-result`` block)
  read:

  - top level: ``entry``, ``research_only``, ``public``, ``ai``,
    ``status``, ``method``, ``input``, ``conversion``,
    ``standard_time_chart``, ``true_solar_time_chart``,
    ``differences``, ``jieqi``, ``pillar_comparison``,
    ``tz_validation``, ``comparison_note``;
  - ``conversion``: the twelve numeric / date fields the page
    renders (apparent / input times, date shift, longitude,
    offsets, meridian, the three correction components);
  - each chart: ``pillars`` (name / ganzhi / stem / branch /
    hidden stems), ``day_master``, ``calendar.local_datetime``
    only -- no ``branch_relations``, no ``auxiliary`` (taohua),
    no ``domain`` / ``variant`` / ``limitations``;
  - ``differences`` / ``jieqi`` (minus the long ``note``) /
    ``pillar_comparison`` (minus ``derived`` / ``note`` /
    ``reuse_note``) / ``tz_validation`` (minus the long
    ``coverage`` / ``uncertainty`` prose);
  - each pillar row: ``name``, ``standard``, ``true_solar``,
    ``changed``, ``reason`` only -- no ``detail`` block and no
    ``ten_god_reading_changed`` flag (the reason string already
    states the governing boundary and the distances).

Dropped, by design: ``provenance``, ``research_api``,
``conversion_method``, ``astronomical_basis``,
``standard_time_convention_unchanged`` (internal identifiers /
bibliographic strings the frontend never reads).

The projected record keeps ``research_only=True`` so the frontend
validator (which requires it) and any later reader can see the
research caliber at a glance; it carries no sealed text, no
internal identifiers and no raw research statements.
"""

from datetime import datetime

__all__ = [
    "is_valid_public_true_solar_comparison",
    "to_public_true_solar_comparison",
]

_PILLAR_NAMES = ("year", "month", "day", "hour")

# Exact top-level key set of research_dual_time_chart output.
_RAW_KEYS = frozenset((
    "entry", "method", "conversion_method", "astronomical_basis",
    "research_only", "public", "ai", "status", "input", "conversion",
    "standard_time_chart", "true_solar_time_chart", "differences",
    "jieqi", "comparison_note", "standard_time_convention_unchanged",
    "pillar_comparison", "research_api", "tz_validation", "provenance",
))

# Exact top-level key set of the projected (public) record.
_PUBLIC_KEYS = frozenset((
    "entry", "research_only", "public", "ai", "status", "method",
    "input", "conversion", "standard_time_chart",
    "true_solar_time_chart", "differences", "jieqi",
    "pillar_comparison", "tz_validation", "comparison_note",
))

_INPUT_KEYS = frozenset((
    "birth_local_time", "longitude_deg", "tz_offset_hours",
    "standard_meridian_deg", "day_boundary", "use_true_solar_time",
))

_CONVERSION_RAW_KEYS = frozenset((
    "apparent_solar_time", "input_local_time", "input_date",
    "apparent_date", "date_shifted", "date_shift_days",
    "longitude_deg", "tz_offset_hours", "standard_meridian_deg",
    "longitude_correction_minutes", "equation_of_time_minutes",
    "total_correction_minutes", "optional_conversion",
    "current_standard_time_convention_unchanged", "research_only",
    "public", "ai", "status", "method", "astronomical_basis",
    "calendar_basis", "julian_day", "method_note",
    "precision_limits",
))

_CONVERSION_PUBLIC_KEYS = frozenset((
    "apparent_solar_time", "input_local_time", "input_date",
    "apparent_date", "date_shifted", "date_shift_days",
    "longitude_deg", "tz_offset_hours", "standard_meridian_deg",
    "longitude_correction_minutes", "equation_of_time_minutes",
    "total_correction_minutes",
))

_DIFFERENCES_KEYS = frozenset((
    "pillars", "solar_term", "chart_date", "any_pillar_changed",
    "month_pillar_changed", "year_pillar_changed",
    "day_pillar_changed", "hour_pillar_changed",
))

_JIEQI_RAW_KEYS = frozenset((
    "crossed", "crossed_term", "crossed_at_utc", "crossed_at_local",
    "minutes_from_input_to_boundary", "standard_solar_term",
    "true_solar_solar_term", "nearest_boundary_term",
    "nearest_boundary_minutes", "within_precision_budget",
    "uncertainty_window_minutes", "uncertainty_window_status",
    "uncertainty_window_adjudication", "note",
))

_JIEQI_PUBLIC_KEYS = _JIEQI_RAW_KEYS - {"note"}

_TZ_VALIDATION_RAW_KEYS = frozenset((
    "tz_name", "instant", "tzdb_offset_hours", "tzdb_offset",
    "tzdb_offset_is_whole_minutes", "supplied_offset_hours",
    "supplied_offset", "matches", "status", "tzdb_version",
    "coverage", "uncertainty", "method", "research_only",
    "public", "ai",
))

_TZ_VALIDATION_PUBLIC_KEYS = frozenset((
    "tz_name", "instant", "tzdb_offset_hours", "tzdb_offset",
    "tzdb_offset_is_whole_minutes", "supplied_offset_hours",
    "supplied_offset", "matches", "status", "tzdb_version",
))

_PILLAR_COMPARISON_RAW_KEYS = frozenset((
    "adapter", "entry", "method", "research_only", "public", "ai",
    "status", "day_master", "pillars",
    "year_and_month_changed_together", "month_attribution",
    "month_attribution_settled", "derived", "note", "reuse_note",
))

_PILLAR_COMPARISON_PUBLIC_KEYS = frozenset((
    "adapter", "entry", "method", "research_only", "public", "ai",
    "status", "day_master", "pillars",
    "year_and_month_changed_together", "month_attribution",
    "month_attribution_settled",
))

_ROW_RAW_KEYS = frozenset((
    "name", "standard", "true_solar", "changed",
    "ten_god_reading_changed", "reason", "detail",
))

_ROW_PUBLIC_KEYS = frozenset((
    "name", "standard", "true_solar", "changed", "reason",
))

# Exact per-pillar detail key sets of the raw adapter rows. The
# detail block is validated (shape only) and dropped by the
# projection: the reason string already states the governing
# boundary and the distances.
_DETAIL_KEYS = {
    "year": frozenset((
        "governing_boundary", "nearest_lichun_utc",
        "minutes_from_true_instant_to_nearest_lichun",
        "attribution_settled",
    )),
    "month": frozenset((
        "governing_boundary", "crossed_term", "crossed_term_kind",
        "crossed_at_utc", "nearest_boundary_term",
        "nearest_boundary_term_kind", "nearest_boundary_minutes",
        "attribution_settled",
    )),
    "day": frozenset((
        "standard_basis", "true_solar_basis", "standard_day_date",
        "true_solar_day_date", "day_boundary", "boundary_label",
        "minutes_from_standard_instant_to_next_shanghai_boundary",
        "minutes_from_apparent_solar_time_to_next_local_boundary",
    )),
    "hour": frozenset((
        "governing_boundary", "standard_shichen_branch",
        "true_solar_shichen_branch",
        "minutes_from_standard_instant_to_next_shichen_boundary",
        "minutes_from_apparent_solar_time_to_next_shichen_boundary",
        "next_shichen_boundary_local",
    )),
}

_STEM_KEYS = frozenset(("value", "element", "polarity", "ten_god"))
_BRANCH_KEYS = frozenset(("value", "hidden_stems"))
_HIDDEN_STEM_KEYS = frozenset(("stem", "ten_god"))
_PILLAR_KEYS = frozenset(("name", "ganzhi", "stem", "branch"))
_DAY_MASTER_KEYS = frozenset(("stem", "element", "polarity"))


def _fail(message):
    raise ValueError(message)


def _is_num(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _is_scalar_or_none(value):
    return value is None or isinstance(value, (str, int, float, bool))


def _is_time_value(value):
    """ISO-8601 string, or a datetime the converter normalises."""
    return isinstance(value, str) or isinstance(value, datetime)


def _as_iso(value):
    if isinstance(value, datetime):
        return value.isoformat()
    return value


def _check_pillar(pillar):
    """True when ``pillar`` is a chart pillar in the real shape."""
    if not isinstance(pillar, dict) or set(pillar) != _PILLAR_KEYS:
        return False
    if pillar["name"] not in _PILLAR_NAMES \
            or not isinstance(pillar["ganzhi"], str):
        return False
    stem = pillar["stem"]
    if not isinstance(stem, dict) or set(stem) != _STEM_KEYS \
            or not all(isinstance(stem[key], str)
                       for key in _STEM_KEYS):
        return False
    branch = pillar["branch"]
    if not isinstance(branch, dict) or set(branch) != _BRANCH_KEYS \
            or not isinstance(branch["value"], str):
        return False
    hidden = branch["hidden_stems"]
    if not isinstance(hidden, list):
        return False
    for item in hidden:
        if not isinstance(item, dict) or set(item) != _HIDDEN_STEM_KEYS \
                or not isinstance(item["stem"], str) \
                or not isinstance(item["ten_god"], str):
            return False
    return True


def _project_pillar(pillar):
    return {
        "name": pillar["name"],
        "ganzhi": pillar["ganzhi"],
        "stem": {key: pillar["stem"][key] for key in _STEM_KEYS},
        "branch": {
            "value": pillar["branch"]["value"],
            "hidden_stems": [
                {key: item[key] for key in _HIDDEN_STEM_KEYS}
                for item in pillar["branch"]["hidden_stems"]],
        },
    }


def _check_chart(chart):
    """True when ``chart`` carries the fields the projection reads.

    The standard chart and the research chart differ in their
    ``calendar`` block by design (the research calendar overrides
    the local reading with the apparent solar time), so only the
    keys the converter reads are pinned here: four pillars in
    order, the day master, and a calendar with a local datetime.
    """
    if not isinstance(chart, dict):
        return False
    if not {"pillars", "day_master", "calendar"}.issubset(chart):
        return False
    pillars = chart["pillars"]
    if not isinstance(pillars, list) or len(pillars) != 4:
        return False
    for name, pillar in zip(_PILLAR_NAMES, pillars):
        if not _check_pillar(pillar) or pillar["name"] != name:
            return False
    day_master = chart["day_master"]
    if not isinstance(day_master, dict) \
            or set(day_master) != _DAY_MASTER_KEYS \
            or not all(isinstance(day_master[key], str)
                       for key in _DAY_MASTER_KEYS):
        return False
    calendar = chart["calendar"]
    if not isinstance(calendar, dict) \
            or not isinstance(calendar.get("local_datetime"), str):
        return False
    return True


def _project_chart(chart):
    return {
        "pillars": [_project_pillar(item) for item in chart["pillars"]],
        "day_master": {key: chart["day_master"][key]
                       for key in _DAY_MASTER_KEYS},
        "calendar": {
            "local_datetime": chart["calendar"]["local_datetime"],
        },
    }


def _check_differences(differences, rows):
    if not isinstance(differences, dict) \
            or set(differences) != _DIFFERENCES_KEYS:
        return False
    pillars = differences["pillars"]
    if not isinstance(pillars, dict) or set(pillars) != set(_PILLAR_NAMES):
        return False
    any_changed = False
    for name in _PILLAR_NAMES:
        entry = pillars[name]
        if not isinstance(entry, dict) \
                or set(entry) != {"standard", "true_solar", "changed"} \
                or not isinstance(entry["standard"], str) \
                or not isinstance(entry["true_solar"], str) \
                or not isinstance(entry["changed"], bool):
            return False
        if entry["changed"] != (entry["standard"] != entry["true_solar"]):
            return False
        # The adapter row must agree with the differences table.
        if rows is not None:
            row = rows[name]
            if row["changed"] != entry["changed"] \
                    or row["standard"]["ganzhi"] != entry["standard"] \
                    or row["true_solar"]["ganzhi"] != entry["true_solar"]:
                return False
        any_changed = any_changed or entry["changed"]
    for key in ("solar_term", "chart_date"):
        entry = differences[key]
        if not isinstance(entry, dict) \
                or set(entry) != {"standard", "true_solar", "changed"} \
                or not isinstance(entry["standard"], str) \
                or not isinstance(entry["true_solar"], str) \
                or not isinstance(entry["changed"], bool):
            return False
    for key in ("any_pillar_changed", "month_pillar_changed",
                "year_pillar_changed", "day_pillar_changed",
                "hour_pillar_changed"):
        if not isinstance(differences[key], bool):
            return False
    if differences["any_pillar_changed"] != any_changed:
        return False
    if differences["year_pillar_changed"] != pillars["year"]["changed"]:
        return False
    if differences["month_pillar_changed"] != pillars["month"]["changed"]:
        return False
    if differences["day_pillar_changed"] != pillars["day"]["changed"]:
        return False
    if differences["hour_pillar_changed"] != pillars["hour"]["changed"]:
        return False
    return True


def is_valid_public_true_solar_comparison(candidate):
    """Closed-shape validator for the raw research comparison record.

    The candidate must be a ``research_dual_time_chart`` result in
    exactly the shape that entry produces today: the research-only
    flags, the four pillar rows in order with reasons, the
    differences table agreeing with those rows, and no key outside
    the known raw sets. Anything else is not a valid public
    comparison; the projection strips it instead of releasing it.
    """
    # Imported here, not at module level: this module is imported by
    # the public projection, whose import surface must not widen to
    # the calendar module (lunar_python) for non-scenario payloads.
    from .bazi_true_solar_chart import ADAPTER_ID, ENTRY_ID, METHOD
    if not isinstance(candidate, dict):
        return False
    if set(candidate) != _RAW_KEYS:
        return False
    if candidate.get("entry") != ENTRY_ID:
        return False
    if candidate.get("research_only") is not True:
        return False
    if candidate.get("public") is not False:
        return False
    if candidate.get("ai") is not False:
        return False
    if candidate.get("status") != "ok":
        return False
    if candidate.get("method") != METHOD:
        return False
    if not isinstance(candidate.get("comparison_note"), str):
        return False
    if candidate.get("standard_time_convention_unchanged") is not True:
        return False
    if not isinstance(candidate.get("conversion_method"), str) \
            or not candidate["conversion_method"]:
        return False
    if not isinstance(candidate.get("astronomical_basis"), str) \
            or not candidate["astronomical_basis"]:
        return False
    if not isinstance(candidate.get("research_api"), str) \
            or not candidate["research_api"]:
        return False
    if not isinstance(candidate.get("provenance"), dict):
        return False

    input_block = candidate.get("input")
    if not isinstance(input_block, dict) \
            or set(input_block) != _INPUT_KEYS:
        return False
    if not isinstance(input_block["birth_local_time"], str) \
            or not _is_num(input_block["longitude_deg"]) \
            or not _is_num(input_block["tz_offset_hours"]) \
            or not _is_num(input_block["standard_meridian_deg"]) \
            or not isinstance(input_block["day_boundary"], str) \
            or input_block["use_true_solar_time"] is not True:
        return False

    conversion = candidate.get("conversion")
    if not isinstance(conversion, dict) \
            or set(conversion) != _CONVERSION_RAW_KEYS:
        return False
    for key in ("apparent_solar_time", "input_local_time"):
        if not _is_time_value(conversion[key]):
            return False
    for key in ("input_date", "apparent_date"):
        if not isinstance(conversion[key], str):
            return False
    if not isinstance(conversion["date_shifted"], bool) \
            or not isinstance(conversion["date_shift_days"], int):
        return False
    for key in ("longitude_deg", "tz_offset_hours",
                "standard_meridian_deg", "longitude_correction_minutes",
                "equation_of_time_minutes", "total_correction_minutes"):
        if not _is_num(conversion[key]):
            return False

    if not _check_chart(candidate.get("standard_time_chart")):
        return False
    if not _check_chart(candidate.get("true_solar_time_chart")):
        return False

    comparison = candidate.get("pillar_comparison")
    if not isinstance(comparison, dict) \
            or set(comparison) != _PILLAR_COMPARISON_RAW_KEYS:
        return False
    if comparison.get("adapter") != ADAPTER_ID:
        return False
    if comparison.get("entry") != ENTRY_ID:
        return False
    if comparison.get("method") != METHOD:
        return False
    if comparison.get("research_only") is not True:
        return False
    if comparison.get("public") is not False:
        return False
    if comparison.get("ai") is not False:
        return False
    if comparison.get("status") != "ok":
        return False
    if comparison.get("month_attribution") not in (
            "settled", "undetermined"):
        return False
    if comparison.get("month_attribution_settled") is not (
            comparison["month_attribution"] == "settled"):
        return False
    if not isinstance(
            comparison.get("year_and_month_changed_together"), bool):
        return False
    day_master = comparison.get("day_master")
    if not isinstance(day_master, dict) \
            or set(day_master) != {"standard", "true_solar", "changed"} \
            or not isinstance(day_master["changed"], bool):
        return False
    for side in ("standard", "true_solar"):
        entry = day_master[side]
        if not isinstance(entry, dict) \
                or set(entry) != _DAY_MASTER_KEYS \
                or not all(isinstance(entry[key], str)
                           for key in _DAY_MASTER_KEYS):
            return False
    if day_master["changed"] != (
            day_master["standard"]["stem"]
            != day_master["true_solar"]["stem"]):
        return False
    rows = comparison.get("pillars")
    if not isinstance(rows, list) or len(rows) != 4:
        return False
    rows_by_name = {}
    for name, row in zip(_PILLAR_NAMES, rows):
        if not isinstance(row, dict) or set(row) != _ROW_RAW_KEYS:
            return False
        if row["name"] != name:
            return False
        if not _check_pillar(row["standard"]) \
                or not _check_pillar(row["true_solar"]):
            return False
        if row["standard"]["name"] != name \
                or row["true_solar"]["name"] != name:
            return False
        if not isinstance(row["changed"], bool) \
                or not isinstance(row["ten_god_reading_changed"], bool) \
                or not isinstance(row["reason"], str) \
                or not row["reason"]:
            return False
        if row["changed"] != (
                row["standard"]["ganzhi"]
                != row["true_solar"]["ganzhi"]):
            return False
        detail = row["detail"]
        if not isinstance(detail, dict) \
                or set(detail) != _DETAIL_KEYS[name] \
                or not all(_is_scalar_or_none(item)
                           for item in detail.values()):
            return False
        rows_by_name[name] = row
    if comparison["year_and_month_changed_together"] != (
            rows_by_name["year"]["changed"]
            and rows_by_name["month"]["changed"]):
        return False
    derived = comparison.get("derived")
    if not isinstance(derived, dict) \
            or set(derived) != {"branch_relations_changed",
                                "taohua_changed"} \
            or not isinstance(derived["branch_relations_changed"], bool) \
            or not isinstance(derived["taohua_changed"], bool):
        return False
    if not isinstance(comparison.get("note"), str) \
            or not isinstance(comparison.get("reuse_note"), str):
        return False

    if not _check_differences(candidate.get("differences"),
                              rows_by_name):
        return False

    jieqi = candidate.get("jieqi")
    if not isinstance(jieqi, dict) or set(jieqi) != _JIEQI_RAW_KEYS:
        return False
    if not isinstance(jieqi["crossed"], bool) \
            or not isinstance(jieqi["within_precision_budget"], bool) \
            or not isinstance(jieqi["standard_solar_term"], str) \
            or not isinstance(jieqi["true_solar_solar_term"], str) \
            or not isinstance(jieqi["nearest_boundary_term"], str) \
            or not isinstance(jieqi["uncertainty_window_status"], str) \
            or not isinstance(jieqi["uncertainty_window_adjudication"],
                             str) \
            or not isinstance(jieqi["note"], str):
        return False
    for key in ("crossed_term", "crossed_at_utc", "crossed_at_local"):
        if jieqi[key] is not None and not isinstance(jieqi[key], str):
            return False
    for key in ("minutes_from_input_to_boundary",
                "nearest_boundary_minutes",
                "uncertainty_window_minutes"):
        if not _is_num(jieqi[key]) and jieqi[key] is not None:
            return False

    tz_validation = candidate.get("tz_validation")
    if not isinstance(tz_validation, dict) \
            or set(tz_validation) != _TZ_VALIDATION_RAW_KEYS:
        return False
    if not isinstance(tz_validation["status"], str) \
            or not tz_validation["status"]:
        return False
    if not isinstance(tz_validation["tzdb_version"], str) \
            or not tz_validation["tzdb_version"]:
        return False
    return True


def to_public_true_solar_comparison(candidate):
    """Allowlist projection of a validated comparison record.

    Returns a fresh dict containing ONLY the keys the frontend
    validator and the bazi-profile page read (see the module
    docstring). A candidate that fails the closed-shape validator
    raises ``ValueError``; the projection layer treats that as
    "strip the key", never as a partial release. Mirrors
    ``to_public_strength_presentation`` (TJ-011.3) and
    ``to_public_pattern_presentation`` (TJ-012.3 Stage B).
    """
    if not is_valid_public_true_solar_comparison(candidate):
        _fail("candidate is not a valid public true-solar comparison")
    conversion = candidate["conversion"]
    jieqi = candidate["jieqi"]
    comparison = candidate["pillar_comparison"]
    tz_validation = candidate["tz_validation"]
    return {
        "entry": candidate["entry"],
        "research_only": True,
        "public": False,
        "ai": False,
        "status": "ok",
        "method": candidate["method"],
        "input": {key: candidate["input"][key] for key in _INPUT_KEYS},
        "conversion": {
            key: (_as_iso(conversion[key])
                  if key in ("apparent_solar_time", "input_local_time")
                  else conversion[key])
            for key in _CONVERSION_PUBLIC_KEYS
        },
        "standard_time_chart": _project_chart(
            candidate["standard_time_chart"]),
        "true_solar_time_chart": _project_chart(
            candidate["true_solar_time_chart"]),
        "differences": {
            "pillars": {
                name: {
                    key: candidate["differences"]["pillars"][name][key]
                    for key in ("standard", "true_solar", "changed")
                }
                for name in _PILLAR_NAMES
            },
            "solar_term": {
                key: candidate["differences"]["solar_term"][key]
                for key in ("standard", "true_solar", "changed")
            },
            "chart_date": {
                key: candidate["differences"]["chart_date"][key]
                for key in ("standard", "true_solar", "changed")
            },
            "any_pillar_changed":
                candidate["differences"]["any_pillar_changed"],
            "month_pillar_changed":
                candidate["differences"]["month_pillar_changed"],
            "year_pillar_changed":
                candidate["differences"]["year_pillar_changed"],
            "day_pillar_changed":
                candidate["differences"]["day_pillar_changed"],
            "hour_pillar_changed":
                candidate["differences"]["hour_pillar_changed"],
        },
        "jieqi": {key: jieqi[key] for key in _JIEQI_PUBLIC_KEYS},
        "pillar_comparison": {
            "adapter": comparison["adapter"],
            "entry": comparison["entry"],
            "method": comparison["method"],
            "research_only": True,
            "public": False,
            "ai": False,
            "status": "ok",
            "day_master": {
                "standard": {
                    key: comparison["day_master"]["standard"][key]
                    for key in _DAY_MASTER_KEYS
                },
                "true_solar": {
                    key: comparison["day_master"]["true_solar"][key]
                    for key in _DAY_MASTER_KEYS
                },
                "changed": comparison["day_master"]["changed"],
            },
            "pillars": [
                {
                    "name": row["name"],
                    "standard": _project_pillar(row["standard"]),
                    "true_solar": _project_pillar(row["true_solar"]),
                    "changed": row["changed"],
                    "reason": row["reason"],
                }
                for row in comparison["pillars"]
            ],
            "year_and_month_changed_together":
                comparison["year_and_month_changed_together"],
            "month_attribution": comparison["month_attribution"],
            "month_attribution_settled":
                comparison["month_attribution_settled"],
        },
        "tz_validation": {
            key: tz_validation[key]
            for key in _TZ_VALIDATION_PUBLIC_KEYS
        },
        "comparison_note": candidate["comparison_note"],
    }
