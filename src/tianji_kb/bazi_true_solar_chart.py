"""Optional research-grade charting entry using apparent (true) solar time.

TJ-0424 batch 2, P1 (B7 adjudication 2026-11-25, approved with
conditions): this module wires the pure conversion in
``bazi_true_solar_time`` to the existing standard-time charting entry
``bazi_core.chart_from_datetime`` -- WITHOUT modifying that entry or
any other existing charting/engines file. It is a separate, explicitly
opt-in research entry point:

* ``true_solar_chart(...)`` -- one birth instant, charted from the
  apparent-solar-time-converted instant. It is OFF by default: the
  caller must pass ``use_true_solar_time=True`` explicitly, otherwise
  it raises ``ValueError``. The existing standard-time charting
  convention is never substituted, re-wired, or re-defaulted.
* ``compare_standard_vs_true_solar(...)`` -- the same birth instant
  charted BOTH ways, side by side, with every difference stated
  explicitly. Calling it is itself the explicit opt-in to computing
  the solar variant for comparison. The two charts are kept in
  separate keys and are never merged and never overwrite each other.

Status: research_only=True, public=False, ai=False,
method="modern_engineering". No adjudicated classical rule is claimed:
true solar time is a modern astronomical conversion (NOAA Solar
Calculator equations implementing Meeus, see
``bazi_true_solar_time.ASTRONOMICAL_BASIS``), not a classical-text
verdict. No public API field is added by this module and no existing
default is changed.

What the entry states explicitly (fail-closed, never silent)
-----------------------------------------------------------
* Longitude / time-zone handling: longitude and ``tz_offset`` are
  caller-supplied and explicit, exactly as in
  ``bazi_true_solar_time``. Historical time zones are NEVER guessed:
  a historical zone is passed as ``tz_offset`` plus, where the
  historical standard meridian differs from 15 * tz_offset, as
  ``standard_meridian_deg``. Daylight saving must already be
  reflected in the supplied ``tz_offset``.
* Date shift: the conversion may move the charted instant onto the
  previous or the next calendar date (e.g. Urumqi moves back a day,
  New York moves forward a day). Both dates and the shift in days
  are reported, and any day/hour pillar change is listed.
* Jieqi (solar-term) boundary: if the standard-time instant and the
  converted instant fall on different sides of a jieqi moment, the
  crossed term, its exact instant, and the signed distance from the
  input instant to that boundary are reported, together with the
  resulting month-pillar (month-commander) change. Because the NOAA
  approximation carries a stated +/-1 minute budget in the equation
  of time, an instant whose converted value lands within 2 minutes
  of any jieqi moment is flagged ``within_precision_budget``: its
  month-pillar attribution is NOT treated as settled by this entry.
* Precision: see ``bazi_true_solar_time.PRECISION_LIMITS``. The
  entry adds no precision of its own; it only surfaces the
  conversion's stated limits next to the chart it produces.

Jieqi instants used here come from the same pinned provider the
existing calendar adapter uses (lunar-python==1.4.8,
``Solar``/``Lunar.getPrevJieQi``/``getNextJieQi``), read through the
same +08:00 wall-clock convention as ``tianji_kb.calendar``. The
month pillar itself is never computed here: it is whatever
``chart_from_datetime`` returns for each instant, so a jieqi
crossing is observed as a difference between the two real charts,
never asserted from a term table in this module.
"""

from datetime import datetime, timedelta, timezone

from lunar_python import Solar

from .bazi_core import chart_from_datetime
from .bazi_true_solar_time import (
    ASTRONOMICAL_BASIS,
    METHOD_ID as CONVERSION_METHOD_ID,
    apparent_solar_time,
)

__all__ = [
    "true_solar_chart",
    "compare_standard_vs_true_solar",
    "RESEARCH_ONLY",
    "PUBLIC",
    "AI",
    "METHOD",
    "ENTRY_ID",
    "CONVERSION_METHOD_ID",
    "JIEQI_UNCERTAINTY_WINDOW_MINUTES",
]

#: Module status flags (B7: optional conversion, research only).
RESEARCH_ONLY = True
PUBLIC = False
AI = False

#: This entry is a modern-engineering construction, not a classical rule.
METHOD = "modern_engineering"

#: Entry identifier carried in every result dict.
ENTRY_ID = "true-solar-chart-research-v1"

#: Jieqi-uncertainty window in minutes. The NOAA equation-of-time
#: approximation carries a stated +/-1 minute budget; a converted
#: instant within this window of a jieqi moment is flagged as not
#: settled (window = budget + 1 minute of margin, stated here).
JIEQI_UNCERTAINTY_WINDOW_MINUTES = 2.0

_SHANGHAI = timezone(timedelta(hours=8))
_PILLAR_NAMES = ("year", "month", "day", "hour")


def _normalize_birth(value, name="birth"):
    """Accept the same birth input as ``chart_from_datetime``.

    An aware datetime, or an ISO-8601 string with a numeric offset.
    Naive inputs are refused: a wall-clock reading without a zone is
    ambiguous, and this entry must not guess one.
    """
    instant = datetime.fromisoformat(value) if isinstance(value, str) else value
    if not isinstance(instant, datetime) or instant.tzinfo is None:
        raise ValueError(
            "%s must be a timezone-aware datetime or an ISO-8601 string "
            "with a numeric offset; naive inputs are refused" % (name,))
    return instant


def _jieqi_neighbours(utc_instant):
    """(previous, next) jieqi as (name, aware-UTC-datetime) pairs.

    Mirrors ``tianji_kb.calendar``: the instant is read in Asia/Shanghai
    wall-clock fields and the provider's jieqi solar times are +08:00.
    """
    shanghai = utc_instant.astimezone(_SHANGHAI)
    lunar = Solar.fromYmdHms(
        shanghai.year, shanghai.month, shanghai.day,
        shanghai.hour, shanghai.minute, shanghai.second).getLunar()
    out = []
    for term in (lunar.getPrevJieQi(False), lunar.getNextJieQi()):
        wall = datetime.strptime(term.getSolar().toYmdHms(), "%Y-%m-%d %H:%M:%S")
        out.append((term.getName(), wall.replace(tzinfo=_SHANGHAI).astimezone(timezone.utc)))
    return out


def _pillar_map(chart):
    return {item["name"]: item["ganzhi"]
            for item in chart["pillars"]}


def _jieqi_analysis(standard_instant, apparent_instant,
                    standard_chart, solar_chart):
    """Explicit jieqi-boundary analysis for the two charted instants.

    Returns a dict stating whether a jieqi moment was crossed, which
    term and when, the signed distance from the input instant to the
    crossed boundary, and whether the converted instant lands within
    the stated precision budget of any jieqi moment.
    """
    std_term = standard_chart["calendar"]["solar_term"]
    sol_term = solar_chart["calendar"]["solar_term"]
    std_utc = standard_instant.astimezone(timezone.utc)
    app_utc = apparent_instant.astimezone(timezone.utc)

    neighbours = {}
    for name, moment in (_jieqi_neighbours(std_utc)
                         + _jieqi_neighbours(app_utc)):
        neighbours.setdefault(name, moment)

    crossed = std_term != sol_term
    crossed_term = None
    crossed_at_utc = None
    minutes_from_input_to_boundary = None
    if crossed:
        # The term that started between the two instants is the one
        # whose start lies strictly between them; equivalently it is
        # the later term's start when moving forward, the earlier
        # term's start when moving backward.
        if app_utc > std_utc:
            crossed_term = sol_term
        else:
            crossed_term = std_term
        crossed_at_utc = neighbours.get(crossed_term)
        if crossed_at_utc is not None:
            minutes_from_input_to_boundary = (
                (crossed_at_utc - std_utc).total_seconds() / 60.0)

    nearest_term = None
    nearest_minutes = None
    for name, moment in neighbours.items():
        distance = abs((app_utc - moment).total_seconds()) / 60.0
        if nearest_minutes is None or distance < nearest_minutes:
            nearest_minutes = distance
            nearest_term = name
    within_budget = (
        nearest_minutes is not None
        and nearest_minutes < JIEQI_UNCERTAINTY_WINDOW_MINUTES)

    return {
        "crossed": crossed,
        "crossed_term": crossed_term,
        "crossed_at_utc": (
            crossed_at_utc.isoformat() if crossed_at_utc is not None
            else None),
        "crossed_at_local": (
            crossed_at_utc.astimezone(_SHANGHAI).isoformat()
            if crossed_at_utc is not None else None),
        "minutes_from_input_to_boundary": minutes_from_input_to_boundary,
        "standard_solar_term": std_term,
        "true_solar_solar_term": sol_term,
        "nearest_boundary_term": nearest_term,
        "nearest_boundary_minutes": nearest_minutes,
        "within_precision_budget": within_budget,
        "uncertainty_window_minutes": JIEQI_UNCERTAINTY_WINDOW_MINUTES,
        "note": (
            "A crossed jieqi changes the month pillar (and, across "
            "立春, the year pillar): the two charts below show the "
            "actual pillars for each instant. When "
            "within_precision_budget is true, the converted instant "
            "lies within the NOAA +/-1 minute equation-of-time budget "
            "of a jieqi moment, so the month-pillar attribution of "
            "the true-solar chart is NOT settled by this entry and "
            "must not be presented as a definite month commander."
            if within_budget else
            "No jieqi moment lies within the NOAA +/-1 minute "
            "equation-of-time budget of the converted instant."
        ),
    }


def _build(birth, longitude_deg, tz_offset, *,
           standard_meridian_deg=None, day_boundary="midnight"):
    instant = _normalize_birth(birth)
    conversion = apparent_solar_time(
        instant, longitude_deg, tz_offset,
        standard_meridian_deg=standard_meridian_deg)
    apparent = conversion["apparent_solar_time"]

    standard_chart = chart_from_datetime(
        instant, day_boundary=day_boundary)
    try:
        solar_chart = chart_from_datetime(
            apparent, day_boundary=day_boundary)
    except ValueError as exc:
        raise ValueError(
            "true-solar converted instant %s is outside the supported "
            "calendar range (1900..2099) or otherwise unchartable: %s; "
            "the standard-time chart is unaffected and no chart is "
            "returned" % (apparent.isoformat(), exc)) from exc

    std_pillars = _pillar_map(standard_chart)
    sol_pillars = _pillar_map(solar_chart)
    pillar_differences = {
        name: {
            "standard": std_pillars[name],
            "true_solar": sol_pillars[name],
            "changed": std_pillars[name] != sol_pillars[name],
        }
        for name in _PILLAR_NAMES
    }
    jieqi = _jieqi_analysis(
        instant, apparent, standard_chart, solar_chart)
    differences = {
        "pillars": pillar_differences,
        "solar_term": {
            "standard": jieqi["standard_solar_term"],
            "true_solar": jieqi["true_solar_solar_term"],
            "changed": jieqi["crossed"],
        },
        "chart_date": {
            "standard": standard_chart["calendar"]["local_datetime"][:10],
            "true_solar": solar_chart["calendar"]["local_datetime"][:10],
            "changed": (
                standard_chart["calendar"]["local_datetime"][:10]
                != solar_chart["calendar"]["local_datetime"][:10]),
        },
        "any_pillar_changed": any(
            pillar_differences[name]["changed"] for name in _PILLAR_NAMES),
        "month_pillar_changed": pillar_differences["month"]["changed"],
        "year_pillar_changed": pillar_differences["year"]["changed"],
        "day_pillar_changed": pillar_differences["day"]["changed"],
        "hour_pillar_changed": pillar_differences["hour"]["changed"],
    }

    return {
        "entry": ENTRY_ID,
        "method": METHOD,
        "conversion_method": CONVERSION_METHOD_ID,
        "astronomical_basis": ASTRONOMICAL_BASIS,
        "research_only": RESEARCH_ONLY,
        "public": PUBLIC,
        "ai": AI,
        "status": "ok",
        "input": {
            "birth_local_time": instant.isoformat(),
            "longitude_deg": float(longitude_deg),
            "tz_offset_hours": conversion["tz_offset_hours"],
            "standard_meridian_deg": conversion["standard_meridian_deg"],
            "day_boundary": day_boundary,
            "use_true_solar_time": True,
        },
        "conversion": conversion,
        "standard_time_chart": standard_chart,
        "true_solar_time_chart": solar_chart,
        "differences": differences,
        "jieqi": jieqi,
        "comparison_note": (
            "The standard-time chart and the true-solar-time chart are "
            "two separate results for the same birth instant under two "
            "different, explicitly labelled conventions. Neither "
            "overwrites the other, and the standard-time chart is "
            "identical to chart_from_datetime(birth): the existing "
            "standard-time charting convention is unchanged. The "
            "true-solar chart is a modern-engineering research variant "
            "only; it carries no classical verdict and must not be "
            "presented as the birth chart."
        ),
        "standard_time_convention_unchanged": True,
    }


def true_solar_chart(birth, longitude_deg, tz_offset, *,
                     standard_meridian_deg=None, day_boundary="midnight",
                     use_true_solar_time=False):
    """Chart one birth instant from its apparent (true) solar time.

    Parameters are the same as :func:`bazi_core.chart_from_datetime`
    for the birth instant, plus the explicit conversion parameters of
    :func:`bazi_true_solar_time.apparent_solar_time` (``longitude_deg``,
    ``tz_offset`` and, where the historical standard meridian differs
    from 15 * tz_offset, ``standard_meridian_deg``).

    OFF BY DEFAULT: ``use_true_solar_time`` defaults to False, and
    with False this function raises ``ValueError`` instead of
    returning a chart. Pass ``use_true_solar_time=True`` to opt in
    explicitly. The standard-time chart is always included alongside
    for comparison; see :func:`compare_standard_vs_true_solar`.
    """
    if not use_true_solar_time:
        raise ValueError(
            "true_solar_chart is OFF by default: pass "
            "use_true_solar_time=True to opt in explicitly. The "
            "standard-time charting convention is unchanged and no "
            "chart is returned without that explicit opt-in.")
    return _build(
        birth, longitude_deg, tz_offset,
        standard_meridian_deg=standard_meridian_deg,
        day_boundary=day_boundary)


def compare_standard_vs_true_solar(birth, longitude_deg, tz_offset, *,
                                   standard_meridian_deg=None,
                                   day_boundary="midnight"):
    """Chart one birth instant BOTH ways and state every difference.

    Calling this function is itself the explicit opt-in to computing
    the true-solar variant for comparison. The result carries the
    standard-time chart and the true-solar-time chart under separate
    keys, a per-pillar/per-term difference table, the full conversion
    record, and the jieqi-boundary analysis. Nothing is merged.
    """
    return _build(
        birth, longitude_deg, tz_offset,
        standard_meridian_deg=standard_meridian_deg,
        day_boundary=day_boundary)
