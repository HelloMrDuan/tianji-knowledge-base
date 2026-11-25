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
  of time, an instant whose converted value lands within the
  provisional 2-minute window of any jieqi moment is flagged
  ``within_precision_budget``: its month-pillar attribution is NOT
  treated as settled by this entry. T1 (2026-11-25): the 2-minute
  window is PROVISIONAL (NOAA +/-1 min budget + 1 min margin) --
  it is a research working window, explicitly NOT a proven maximum
  error, and near-boundary cases are verified in the tests.
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

Batch 3 (TJ-0424) adds the research-only pillar adapter
(:func:`pillar_comparison` / :func:`compare_pillars`). The adapter
reuses the two real charts' deterministic derivations -- the four
pillars, the day master, the hidden stems (藏干) and the ten gods
(十神) -- without recomputing any of them and without touching the
existing charting code. For each pillar it states, side by side,
the standard-time reading and the true-solar-time reading, whether
it changed, and WHY: the governing boundary for that pillar
(立春 for the year pillar, the nearest jieqi for the month pillar,
the Shanghai day boundary for the day pillar, the shichen boundary
for the hour pillar), the distance to that boundary, and what
crossing it did or did not do. A month pillar changes only when a
节 (jie) term is crossed: crossing a 中气 (qi) term changes the
solar term but leaves the month pillar unchanged, and the adapter
says so explicitly instead of implying a month change. When the day
pillar changes, the day master changes with it, so the ten-god
reading of every stem and hidden stem is recomputed against the new
day master by the existing charting code; the adapter surfaces that
cascade rather than hiding it. A converted instant inside the
stated jieqi precision window keeps the status quo: the month
attribution is flagged 月令归属未定 (not settled). The window is
2 minutes, PROVISIONAL per T1 adjudication 2026-11-25 (NOAA +/-1
min budget + 1 min margin) -- not a proven maximum error.

Batch 3, T4 (adjudicated 2026-11-25): the research-only research
API entry :func:`research_dual_time_chart` charts one birth instant
under BOTH conventions (standard time and true solar time) in a
single call, resolves or validates the time-zone offset against
IANA tzdb where a zone name is given (T3), and attaches the pillar
adapter (:func:`compare_pillars`, the comparison function intended
for admin-backend consumption). It is function-level only: no
public page, no public execution endpoint, and the existing public
default charting convention is untouched. Representation
invariance: the same physical instant always carries the same
solar term whatever time representation it is written in -- a term
changes between the two charts only when a jieqi moment lies
strictly between the standard instant and the converted instant,
never because the time was re-expressed.
"""

from datetime import datetime, timedelta, timezone

from lunar_python import Solar

from .bazi_core import chart_from_datetime
from .bazi_true_solar_time import (
    ASTRONOMICAL_BASIS,
    METHOD_ID as CONVERSION_METHOD_ID,
    _is_whole_minutes,
    _offset_label,
    apparent_solar_time,
    tzdb_offset_hours,
    tzdb_version,
    validate_tz_offset,
)

__all__ = [
    "true_solar_chart",
    "compare_standard_vs_true_solar",
    "pillar_comparison",
    "compare_pillars",
    "research_dual_time_chart",
    "RESEARCH_ONLY",
    "PUBLIC",
    "AI",
    "METHOD",
    "ENTRY_ID",
    "ADAPTER_ID",
    "RESEARCH_API_ID",
    "CONVERSION_METHOD_ID",
    "JIEQI_UNCERTAINTY_WINDOW_MINUTES",
    "JIEQI_WINDOW_STATUS",
    "JIEQI_WINDOW_ADJUDICATION",
]

#: Module status flags (B7: optional conversion, research only).
RESEARCH_ONLY = True
PUBLIC = False
AI = False

#: This entry is a modern-engineering construction, not a classical rule.
METHOD = "modern_engineering"

#: Entry identifier carried in every result dict.
ENTRY_ID = "true-solar-chart-research-v1"

#: Adapter identifier carried in every pillar-comparison result.
ADAPTER_ID = "true-solar-pillar-adapter-v1"

#: Research API entry identifier (T4, adjudicated 2026-11-25).
RESEARCH_API_ID = "true-solar-research-api-v1"

#: The twelve 节 (jie) terms. The month pillar (month commander)
#: changes only at these boundaries; the other twelve terms are 中气
#: (qi) terms, whose crossing changes the solar term but not the
#: month pillar. This is the traditional calendrical division the
#: pinned provider's month computation follows; it is stated here
#: only to label which kind of term was crossed, never to compute a
#: pillar -- the pillars always come from ``chart_from_datetime``.
_JIE_TERMS = frozenset((
    "立春", "惊蛰", "清明", "立夏", "芒种", "小暑",
    "立秋", "白露", "寒露", "立冬", "大雪", "小寒",
))

#: Shichen (two-hour) branches in order, starting at 子时 23:00-00:59.
_SHICHEN_BRANCHES = "子丑寅卯辰巳午未申酉戌亥"

#: Jieqi-uncertainty window in minutes. The NOAA equation-of-time
#: approximation carries a stated +/-1 minute budget; a converted
#: instant within this window of a jieqi moment is flagged as not
#: settled (window = budget + 1 minute of margin, stated here).
#: T1 (2026-11-25): the 2-minute window is PROVISIONAL -- a
#: research working window, explicitly NOT a proven maximum error.
#: Near-boundary cases are verified in the tests.
JIEQI_UNCERTAINTY_WINDOW_MINUTES = 2.0

#: Status of the jieqi uncertainty window (T1, adjudicated 2026-11-25).
JIEQI_WINDOW_STATUS = "provisional"

#: Adjudication record for the jieqi uncertainty window (T1).
JIEQI_WINDOW_ADJUDICATION = (
    "T1 (2026-11-25): 2-minute provisional research window "
    "(NOAA +/-1 min equation-of-time budget + 1 min margin); "
    "provisional, not a proven maximum error")

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
        "uncertainty_window_status": JIEQI_WINDOW_STATUS,
        "uncertainty_window_adjudication": JIEQI_WINDOW_ADJUDICATION,
        "note": (
            "A crossed jieqi changes the month pillar (and, across "
            "立春, the year pillar): the two charts below show the "
            "actual pillars for each instant. When "
            "within_precision_budget is true, the converted instant "
            "lies within the provisional 2-minute window "
            "(T1, 2026-11-25; NOAA +/-1 min budget + 1 min margin) "
            "of a jieqi moment, so the month-pillar attribution of "
            "the true-solar chart is NOT settled by this entry and "
            "must not be presented as a definite month commander. "
            "The window is provisional, not a proven maximum error."
            if within_budget else
            "No jieqi moment lies within the provisional 2-minute "
            "window (T1, 2026-11-25) of the converted instant; the "
            "window is provisional, not a proven maximum error."
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


# ======================================================================
# Batch 3 (TJ-0424): research-only pillar adapter.
#
# The adapter reuses the two real charts' deterministic derivations
# (four pillars, day master, hidden stems, ten gods) -- it reads them
# out of the comparison result and never recomputes them, and it
# never touches the existing charting code. For each pillar it states
# the standard-time reading and the true-solar-time reading side by
# side, whether it changed, and why: the governing boundary, the
# distance to it, and what crossing it did or did not do.
# ======================================================================


def _shanghai_wall(chart):
    """Shanghai wall-clock datetime of a chart (aware, +08:00)."""
    return datetime.fromisoformat(chart["calendar"]["local_datetime"])


def _minutes_between(earlier, later):
    return (later - earlier).total_seconds() / 60.0


def _next_shichen_boundary(wall):
    """Next shichen boundary strictly after ``wall`` (Shanghai time).

    Shichen boundaries fall on odd hours (23, 01, 03, ..., 21).
    Returns (boundary_datetime, boundary_hour).
    """
    base = wall.replace(minute=0, second=0, microsecond=0)
    hour = wall.hour
    if wall.minute == 0 and wall.second == 0 and wall.microsecond == 0 \
            and hour % 2 == 1:
        # Exactly on a boundary: the next one is two hours on.
        nxt = base + timedelta(hours=2)
        return nxt, nxt.hour
    # Next odd hour at or after the current hour, strictly in the future.
    candidate = base
    if candidate.hour % 2 == 0:
        candidate = candidate + timedelta(hours=1)
    if candidate <= wall:
        candidate = candidate + timedelta(hours=2)
    return candidate, candidate.hour


def _next_day_boundary(wall, day_boundary):
    """Next day boundary strictly after ``wall`` (Shanghai time).

    ``midnight``: next 00:00. ``zi-start``: next 23:00 (the day
    starts at 23:00 under the zi-start convention).
    Returns (boundary_datetime, label).
    """
    if day_boundary == "zi-start":
        candidate = wall.replace(hour=23, minute=0, second=0, microsecond=0)
        if candidate <= wall:
            candidate = candidate + timedelta(days=1)
        return candidate, "23:00"
    candidate = wall.replace(hour=0, minute=0, second=0, microsecond=0)
    if candidate <= wall:
        candidate = candidate + timedelta(days=1)
    return candidate, "00:00"


def _lichun_near(utc_instant):
    """立春 instants (aware UTC) bracketing ``utc_instant``.

    Probed from the same pinned provider as the jieqi analysis:
    4 February of the Shanghai year of the instant and its two
    neighbours. Duplicates are removed; the result is sorted.
    """
    shanghai_year = utc_instant.astimezone(_SHANGHAI).year
    found = {}
    for year in (shanghai_year - 1, shanghai_year, shanghai_year + 1):
        lunar = Solar.fromYmdHms(year, 2, 4, 12, 0, 0).getLunar()
        for term in (lunar.getPrevJieQi(False), lunar.getNextJieQi()):
            if term.getName() == "立春":
                wall = datetime.strptime(
                    term.getSolar().toYmdHms(), "%Y-%m-%d %H:%M:%S")
                moment = wall.replace(tzinfo=_SHANGHAI).astimezone(
                    timezone.utc)
                found[moment.isoformat()] = moment
    return sorted(found.values())


def _ten_god_reading(pillar):
    """Comparable ten-god reading of one pillar dict.

    The stem's ten god plus every hidden stem's ten god, in order.
    The reading is always taken against that chart's own day master,
    because it is read out of the chart, not computed here.
    """
    reading = [pillar["stem"]["ten_god"]]
    reading.extend(
        item["ten_god"] for item in pillar["branch"]["hidden_stems"])
    return tuple(reading)


def _year_reason(std_wall, sol_wall, std_utc, app_utc, jieqi, changed):
    """Reason annotation for the year pillar (governed by 立春)."""
    lichun_list = _lichun_near(std_utc)
    nearest = None
    nearest_signed = None
    for moment in lichun_list:
        signed = _minutes_between(moment, app_utc)
        if nearest_signed is None or abs(signed) < abs(nearest_signed):
            nearest = moment
            nearest_signed = signed
    within_window = (
        nearest_signed is not None
        and abs(nearest_signed) < JIEQI_UNCERTAINTY_WINDOW_MINUTES)
    detail = {
        "governing_boundary": "lichun",
        "nearest_lichun_utc": (
            nearest.isoformat() if nearest is not None else None),
        "minutes_from_converted_instant_to_nearest_lichun": nearest_signed,
        "attribution_settled": not within_window,
    }
    if changed:
        crossed_at = jieqi["crossed_at_utc"]
        if jieqi["crossed_term"] == "立春" and crossed_at is not None:
            minutes = jieqi["minutes_from_input_to_boundary"]
            if minutes is None:
                distance = "an unrecorded distance from that boundary"
            elif minutes <= 0:
                distance = "%.1f minutes after that boundary" % (-minutes,)
            else:
                distance = "%.1f minutes before that boundary" % (minutes,)
            reason = (
                "The year pillar changed because the conversion crossed "
                "立春 at %s (UTC): the year pillar changes only at 立春. "
                "The input instant was %s."
                % (crossed_at, distance))
        else:
            reason = (
                "The year pillar changed, but the crossed term is %r, "
                "not 立春: this is unexpected against the calendar "
                "provider's year computation and is flagged, not "
                "explained away." % (jieqi["crossed_term"],))
        if within_window:
            reason += (
                " The converted instant lies within the stated "
                "precision window of 立春, so the year attribution is "
                "NOT settled.")
    else:
        if nearest is None:
            reason = (
                "立春 was not crossed, so the year pillar is unchanged; "
                "no 立春 instant was found near the birth instant.")
        else:
            side = "after" if nearest_signed >= 0 else "before"
            reason = (
                "立春 was not crossed, so the year pillar is unchanged: "
                "the nearest 立春 (%s UTC) is %.1f minutes %s the "
                "converted instant."
                % (nearest.isoformat(), abs(nearest_signed), side))
        if within_window:
            reason += (
                " The converted instant lies within the stated "
                "precision window of 立春, so the year attribution is "
                "NOT settled.")
    return reason, detail


def _month_reason(jieqi, changed):
    """Reason annotation for the month pillar (governed by jieqi)."""
    detail = {
        "governing_boundary": "jieqi",
        "crossed_term": jieqi["crossed_term"],
        "crossed_term_kind": (
            "节" if jieqi["crossed_term"] in _JIE_TERMS else
            ("气" if jieqi["crossed_term"] is not None else None)),
        "crossed_at_utc": jieqi["crossed_at_utc"],
        "nearest_boundary_term": jieqi["nearest_boundary_term"],
        "nearest_boundary_minutes": jieqi["nearest_boundary_minutes"],
        "attribution_settled": not jieqi["within_precision_budget"],
    }
    if changed:
        if jieqi["crossed_term"] in _JIE_TERMS:
            reason = (
                "The month pillar changed because the conversion "
                "crossed %s at %s (UTC): %s is a 节 term, and the "
                "month pillar changes at 节 boundaries."
                % (jieqi["crossed_term"], jieqi["crossed_at_utc"],
                   jieqi["crossed_term"]))
        elif jieqi["crossed_term"] is not None:
            reason = (
                "The month pillar changed while the crossed term is "
                "%s, a 中气 term: a month-pillar change across a 中气 "
                "crossing is not expected from the calendar provider "
                "and is flagged, not explained away."
                % (jieqi["crossed_term"],))
        else:
            reason = (
                "The month pillar changed, but no crossed term was "
                "recorded: flagged, not explained away.")
        if jieqi["within_precision_budget"]:
            reason += (
                " The converted instant lies within the stated "
                "precision window of a jieqi moment, so the month "
                "attribution is NOT settled (月令归属未定).")
    elif jieqi["crossed"]:
        if jieqi["crossed_term"] in _JIE_TERMS:
            reason = (
                "The conversion crossed %s at %s (UTC), a 节 term, "
                "but the month pillar is unchanged: flagged as "
                "unexpected against the calendar provider's month "
                "computation, not explained away."
                % (jieqi["crossed_term"], jieqi["crossed_at_utc"]))
        else:
            reason = (
                "The conversion crossed %s at %s (UTC), a 中气 term: "
                "the solar term changed, but the month pillar changes "
                "only at 节 boundaries, so the month pillar is "
                "unchanged."
                % (jieqi["crossed_term"], jieqi["crossed_at_utc"]))
        if jieqi["within_precision_budget"]:
            reason += (
                " The converted instant lies within the stated "
                "precision window of a jieqi moment, so the month "
                "attribution is NOT settled (月令归属未定).")
    else:
        reason = (
            "No jieqi was crossed, so the month pillar is unchanged: "
            "the nearest boundary, %s, is %.1f minutes from the "
            "converted instant."
            % (jieqi["nearest_boundary_term"],
               jieqi["nearest_boundary_minutes"]))
        if jieqi["within_precision_budget"]:
            reason += (
                " The converted instant lies within the stated "
                "precision window of a jieqi moment, so the month "
                "attribution is NOT settled (月令归属未定).")
    return reason, detail


def _day_reason(std_wall, sol_wall, day_boundary, changed,
                std_ganzhi, sol_ganzhi):
    """Reason annotation for the day pillar (Shanghai day boundary)."""
    next_std, label = _next_day_boundary(std_wall, day_boundary)
    next_sol, _ = _next_day_boundary(sol_wall, day_boundary)
    detail = {
        "governing_boundary": (
            "shanghai_zi_start_23h" if day_boundary == "zi-start"
            else "shanghai_midnight"),
        "day_boundary": day_boundary,
        "boundary_label": label,
        "standard_shanghai_date": std_wall.date().isoformat(),
        "true_solar_shanghai_date": sol_wall.date().isoformat(),
        "minutes_from_standard_instant_to_next_boundary":
            _minutes_between(std_wall, next_std),
        "minutes_from_converted_instant_to_next_boundary":
            _minutes_between(sol_wall, next_sol),
    }
    if changed:
        reason = (
            "The Shanghai date changed %s -> %s: the %s day boundary "
            "was crossed, so the day pillar changed %s -> %s. The "
            "day pillar follows the Shanghai date under the %s "
            "convention."
            % (detail["standard_shanghai_date"],
               detail["true_solar_shanghai_date"], label,
               std_ganzhi, sol_ganzhi, day_boundary))
    else:
        reason = (
            "The Shanghai date is unchanged (%s), so the day pillar "
            "is unchanged: the next %s day boundary is %.1f minutes "
            "after the converted instant (%.1f minutes after the "
            "standard instant)."
            % (detail["standard_shanghai_date"], label,
               detail["minutes_from_converted_instant_to_next_boundary"],
               detail["minutes_from_standard_instant_to_next_boundary"]))
    return reason, detail


def _hour_reason(std_wall, sol_wall, changed,
                 std_branch, sol_branch, std_ganzhi, sol_ganzhi):
    """Reason annotation for the hour pillar (shichen boundary)."""
    next_std, hour_std = _next_shichen_boundary(std_wall)
    next_sol, hour_sol = _next_shichen_boundary(sol_wall)
    detail = {
        "governing_boundary": "shichen",
        "standard_shichen_branch": std_branch,
        "true_solar_shichen_branch": sol_branch,
        "minutes_from_standard_instant_to_next_shichen_boundary":
            _minutes_between(std_wall, next_std),
        "minutes_from_converted_instant_to_next_shichen_boundary":
            _minutes_between(sol_wall, next_sol),
        "next_shichen_boundary_local": next_sol.isoformat(),
    }
    if changed:
        reason = (
            "The shichen changed %s时 -> %s时: a shichen boundary "
            "was crossed, so the hour pillar changed %s -> %s."
            % (std_branch, sol_branch, std_ganzhi, sol_ganzhi))
    else:
        reason = (
            "The shichen is unchanged (%s时), so the hour pillar is "
            "unchanged: the next shichen boundary (%02d:00) is %.1f "
            "minutes after the converted instant (%.1f minutes after "
            "the standard instant)."
            % (std_branch, hour_sol,
               detail["minutes_from_converted_instant_to_next_shichen_boundary"],
               detail["minutes_from_standard_instant_to_next_shichen_boundary"]))
    return reason, detail


def pillar_comparison(comparison):
    """Per-pillar standard-vs-true-solar comparison with reasons.

    ``comparison`` is the result dict of
    :func:`compare_standard_vs_true_solar` (or :func:`true_solar_chart`
    / :func:`compare_pillars`). The adapter reads the two real charts
    out of it -- four pillars, day master, hidden stems, ten gods,
    branch relations, taohua -- and states, for each pillar, the
    standard-time reading and the true-solar-time reading side by
    side, whether it changed, and why (governing boundary, distance
    to it, what crossing it did or did not do). Nothing is recomputed
    here: every stem, branch, hidden stem and ten god is copied
    verbatim from the chart that computed it.

    The result is research_only / public=False / ai=False, exactly
    like the entry it adapts. It adds no public field and changes no
    production computation.
    """
    for key in ("standard_time_chart", "true_solar_time_chart",
                "jieqi", "differences", "input"):
        if key not in comparison:
            raise ValueError(
                "pillar_comparison requires a compare_standard_vs_true_"
                "solar result dict (missing %r)" % (key,))
    std_chart = comparison["standard_time_chart"]
    sol_chart = comparison["true_solar_time_chart"]
    jieqi = comparison["jieqi"]
    day_boundary = comparison["input"]["day_boundary"]
    std_pillars = _pillar_map(std_chart)
    sol_pillars = _pillar_map(sol_chart)
    std_rows = {item["name"]: item for item in std_chart["pillars"]}
    sol_rows = {item["name"]: item for item in sol_chart["pillars"]}
    std_wall = _shanghai_wall(std_chart)
    sol_wall = _shanghai_wall(sol_chart)
    std_utc = std_wall.astimezone(timezone.utc)
    app_utc = sol_wall.astimezone(timezone.utc)

    std_dm = std_chart["day_master"]
    sol_dm = sol_chart["day_master"]
    day_master_changed = std_dm["stem"] != sol_dm["stem"]

    rows = []
    for name in _PILLAR_NAMES:
        changed = std_pillars[name] != sol_pillars[name]
        ten_god_changed = (
            _ten_god_reading(std_rows[name])
            != _ten_god_reading(sol_rows[name]))
        if name == "year":
            reason, detail = _year_reason(
                std_wall, sol_wall, std_utc, app_utc, jieqi, changed)
        elif name == "month":
            reason, detail = _month_reason(jieqi, changed)
        elif name == "day":
            reason, detail = _day_reason(
                std_wall, sol_wall, day_boundary, changed,
                std_pillars[name], sol_pillars[name])
        else:
            reason, detail = _hour_reason(
                std_wall, sol_wall, changed,
                std_rows[name]["branch"]["value"],
                sol_rows[name]["branch"]["value"],
                std_pillars[name], sol_pillars[name])
        rows.append({
            "name": name,
            "standard": std_rows[name],
            "true_solar": sol_rows[name],
            "changed": changed,
            "ten_god_reading_changed": ten_god_changed,
            "reason": reason,
            "detail": detail,
        })

    year_changed = rows[0]["changed"]
    month_changed = rows[1]["changed"]
    together = year_changed and month_changed
    month_settled = not jieqi["within_precision_budget"]
    derived_note_parts = []
    if day_master_changed:
        derived_note_parts.append(
            "The day master changed %s -> %s, so the ten-god reading "
            "of every stem and hidden stem was recomputed by the "
            "existing charting code against the new day master; the "
            "pillar rows above show both readings side by side."
            % (std_dm["stem"], sol_dm["stem"]))
    else:
        derived_note_parts.append(
            "The day master is unchanged (%s), so the ten-god "
            "readings are taken against the same day master on both "
            "sides; any ten-god difference comes from a changed stem "
            "or branch, not from a changed day master."
            % (std_dm["stem"],))
    if together:
        derived_note_parts.append(
            "The year pillar and the month pillar changed together: "
            "the crossed term is 立春, which governs both.")
    if not month_settled:
        derived_note_parts.append(
            "月令归属未定: the converted instant lies within the "
            "stated jieqi precision window, so the month-pillar "
            "attribution is NOT settled by this entry (status quo; "
            "the window is provisional per T1 (2026-11-25), not a "
            "proven maximum error).")

    return {
        "adapter": ADAPTER_ID,
        "entry": ENTRY_ID,
        "method": METHOD,
        "research_only": RESEARCH_ONLY,
        "public": PUBLIC,
        "ai": AI,
        "status": "ok",
        "day_master": {
            "standard": std_dm,
            "true_solar": sol_dm,
            "changed": day_master_changed,
        },
        "pillars": rows,
        "year_and_month_changed_together": together,
        "month_attribution": (
            "settled" if month_settled else "undetermined"),
        "month_attribution_settled": month_settled,
        "derived": {
            "branch_relations_changed": (
                std_chart["branch_relations"]
                != sol_chart["branch_relations"]),
            "taohua_changed": (
                std_chart["auxiliary"]["taohua"]
                != sol_chart["auxiliary"]["taohua"]),
        },
        "note": " ".join(derived_note_parts),
        "reuse_note": (
            "Every stem, branch, hidden stem and ten god above is "
            "copied verbatim from the two real charts produced by "
            "chart_from_datetime; this adapter recomputes nothing "
            "and changes no production computation."),
    }


def compare_pillars(birth, longitude_deg, tz_offset, *,
                    standard_meridian_deg=None, day_boundary="midnight"):
    """Chart one birth instant BOTH ways, plus the pillar adapter.

    This is :func:`compare_standard_vs_true_solar` with the
    research-only pillar adapter attached under the
    ``"pillar_comparison"`` key: per-pillar standard-vs-true-solar
    readings (four pillars, hidden stems, ten gods) with a stated
    reason for each change or non-change. Calling it is itself the
    explicit opt-in to computing the true-solar variant for
    comparison. Nothing is merged; the standard-time chart is
    identical to ``chart_from_datetime(birth)``.

    T4 (adjudicated 2026-11-25): this is the comparison function
    intended for admin-backend consumption -- the admin backend
    calls this (or :func:`research_dual_time_chart`, which wraps
    it) to show the standard-time / true-solar-time对照; it is
    function-level only and is never wired to a public page or a
    public execution endpoint.
    """
    result = _build(
        birth, longitude_deg, tz_offset,
        standard_meridian_deg=standard_meridian_deg,
        day_boundary=day_boundary)
    result["pillar_comparison"] = pillar_comparison(result)
    return result


def research_dual_time_chart(birth, longitude_deg, *, tz_name=None,
                             tz_offset=None, standard_meridian_deg=None,
                             day_boundary="midnight"):
    """Research API entry (T4, adjudicated 2026-11-25): dual-time chart.

    Function-level only: this is the research API entry for the
    independent, controlled research API and the admin backend. It
    charts one birth instant under BOTH conventions (standard time
    and true solar time), attaches the pillar adapter, and resolves
    or validates the time-zone offset against IANA tzdb (T3) when a
    zone name is given. No public page, no public execution
    endpoint, no change to the existing public default charting
    convention: the standard-time chart inside is identical to
    ``chart_from_datetime(birth)``.

    Time-zone handling (exactly one source is required):

    * ``tz_name`` alone -- the offset is resolved from IANA tzdb
      for the birth instant. If the tzdb offset at that instant is
      local mean time (non-whole-minute, pre-standard-time era),
      this raises ValueError: an LMT value must never be rounded
      into a ``tz_offset``; the caller must supply an explicit
      whole-minute offset instead.
    * ``tz_offset`` alone -- used as before, exactly as in
      :func:`compare_pillars`; no tzdb check is performed and the
      validation record says so (``status: "not_requested"``).
    * both -- the supplied offset is validated against tzdb for the
      instant; a mismatch raises ValueError with both values
      stated (fail-closed: an ambiguous offset must not silently
      pick a side).
    * neither -- ValueError.

    The result is :func:`compare_pillars` output plus a
    ``"tz_validation"`` record and a ``"provenance"`` record
    (tzdb version, jieqi window status, method ids). It is
    research_only / public=False / ai=False throughout.
    """
    instant = _normalize_birth(birth)
    if tz_name is None and tz_offset is None:
        raise ValueError(
            "research_dual_time_chart requires exactly one time-zone "
            "source: tz_name (IANA zone, resolved via tzdb) or "
            "tz_offset (explicit hours); neither was given")
    if tz_name is not None:
        tzdb_hours = tzdb_offset_hours(tz_name, instant)
        if not _is_whole_minutes(tzdb_hours):
            raise ValueError(
                "IANA zone %r at %s resolves to local mean time "
                "(%s), a pre-standard-time era: no civil offset "
                "exists to use as tz_offset; supply an explicit "
                "whole-minute tz_offset instead (see T3)"
                % (tz_name, instant.isoformat(),
                   _offset_label(tzdb_hours)))
        if tz_offset is None:
            validation = dict(
                validate_tz_offset(tz_name, instant, tzdb_hours))
            validation["status"] = "resolved_from_tzdb"
            validation["supplied_offset_hours"] = None
            validation["supplied_offset"] = None
            validation["uncertainty"] = (
                "Offset resolved from IANA tzdb at this instant; "
                "resolution is a lookup, not proof of historical "
                "correctness (tzdb version %s)."
                % validation["tzdb_version"])
            resolved_offset = tzdb_hours
        else:
            validation = validate_tz_offset(tz_name, instant, tz_offset)
            if validation["status"] == "lmt_era":
                raise ValueError(
                    "IANA zone %r at %s is in a local-mean-time era "
                    "(tzdb offset %s): no civil offset exists to "
                    "validate the supplied offset against; supply the "
                    "offset from another source (see T3)"
                    % (tz_name, instant.isoformat(),
                       validation["tzdb_offset"]))
            if validation["status"] == "mismatch":
                raise ValueError(
                    "tz_offset mismatch for IANA zone %r at %s: "
                    "supplied %s, tzdb gives %s (version %s); "
                    "refusing rather than silently picking a side"
                    % (tz_name, instant.isoformat(),
                       validation["supplied_offset"],
                       validation["tzdb_offset"],
                       validation["tzdb_version"]))
            resolved_offset = validation["supplied_offset_hours"]
    else:
        resolved_offset = tz_offset
        validation = {
            "tz_name": None,
            "instant": instant.astimezone(timezone.utc).isoformat(),
            "tzdb_offset_hours": None,
            "tzdb_offset": None,
            "tzdb_offset_is_whole_minutes": None,
            "supplied_offset_hours": None,
            "supplied_offset": None,
            "matches": None,
            "status": "not_requested",
            "tzdb_version": tzdb_version(),
            "coverage": (
                "No tzdb check was requested: the caller supplied an "
                "explicit tz_offset, used as given (see "
                "bazi_true_solar_time.TZDB_COVERAGE_NOTE for the "
                "coverage limits of a check)."),
            "uncertainty": (
                "No tzdb validation was performed for this call."),
            "method": "iana-tzdb-validation-v1",
            "research_only": RESEARCH_ONLY,
            "public": PUBLIC,
            "ai": AI,
        }

    result = compare_pillars(
        instant, longitude_deg, resolved_offset,
        standard_meridian_deg=standard_meridian_deg,
        day_boundary=day_boundary)
    result["research_api"] = RESEARCH_API_ID
    result["tz_validation"] = validation
    result["provenance"] = {
        "research_api": RESEARCH_API_ID,
        "entry": ENTRY_ID,
        "adapter": ADAPTER_ID,
        "conversion_method": CONVERSION_METHOD_ID,
        "tzdb_version": tzdb_version(),
        "jieqi_window_minutes": JIEQI_UNCERTAINTY_WINDOW_MINUTES,
        "jieqi_window_status": JIEQI_WINDOW_STATUS,
        "jieqi_window_adjudication": JIEQI_WINDOW_ADJUDICATION,
        "note": (
            "Research entry only (T4): standard-time chart identical "
            "to chart_from_datetime(birth); true-solar chart is a "
            "modern-engineering research variant; no public page, no "
            "public execution endpoint, no change to the public "
            "default charting convention."),
    }
    return result


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
