"""Timezone-aware production calendar: civil-time validation + birthplace-frame pillars.

This module does NOT modify Phase4-frozen calendar.py (SHA256 pinned in
evals/explanations/engine-baseline-v1.json). It mirrors calendar()'s algorithm
(lunar-python provider, midnight/zi-start day boundaries) but computes in the
birthplace wall-time frame instead of unconditionally converting every instant
to Asia/Shanghai, and it validates the civil time against tzdb BEFORE computing:

- nonexistent civil time (DST gap) -> ValueError, refuses to guess;
- claimed fixed offset contradicting tzdb for that civil time -> ValueError;
- ambiguous civil time with a fixed offset -> accepted ONLY because the offset
  explicitly selects the occurrence (same rule as audit_birth_instant);
  a named-zone ambiguous input (a ZoneInfo datetime, with no fixed offset to
  disambiguate) -> ValueError, fold is never guessed silently.
  JSON API inputs always carry fixed offsets, so the fold-guess case cannot
  arise through the API; it is refused for direct datetime callers.
- unknown zone name -> ValueError; missing zone defaults to Asia/Shanghai
  (documented; preserves China and legacy callers, whose offsets already agree
  with Shanghai; a non-Shanghai offset without a zone is rejected as a
  contradiction instead of silently miscomputed).

Validation reuses bazi_calendar_precision_audit.audit_birth_instant (pure
zoneinfo/tzdb logic, no private data) so production and the research audit
cannot drift apart. The returned dict carries the same keys as calendar()
plus tz_name / civil_classification / offset_disambiguation, so callers can
audit which frame produced the pillars.

Frame split (TJ-031.6): the lunar date and the day/hour pillars follow the
birthplace wall-time frame (local civil day and clock). The solar-term
attribution fields (solar_term, year_ganzhi, month_ganzhi) and
solar_term_started_at are INSTANT-frame: lunar-python's jieqi table is a
China-baseline (UTC+08:00) wall-time table, so term attribution is read
from a Lunar object built from the instant's Asia/Shanghai wall time --
comparing the birthplace clock against China term clocks instead would
shift every attribution boundary by (8h - birthplace offset).
solar_term_started_at renders the term's absolute instant (provider wall
reading minus 8h) in the birthplace zone, so every zone labels the same
term with the same instant; splicing the birthplace offset onto the China
wall reading (the pre-TJ-031.6 behaviour) mislabelled it by exactly
(8h - birthplace offset).
"""

from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

from lunar_python import Solar

from .bazi_calendar_precision_audit import audit_birth_instant
from .calendar import PROVIDER, hour_pillar
from .foundations import BRANCHES

DEFAULT_ZONE = "Asia/Shanghai"

# Precision window (TJ-031.7): independent solar-term sources diverge
# by up to ~14 seconds (2024 Lichun: lunar-python 08:27:07Z, sxtwl
# 08:26:53Z, JPL Horizons 08:27:00Z). The 60-second window covers the
# largest measured divergence with margin, so a birth this close to a
# term instant is flagged in the result instead of being presented as
# exactly attributed; outside the window the note is None.
SOLAR_TERM_PRECISION_WINDOW_SECONDS = 60


def _solar_term_precision_note(distance_seconds):
    if distance_seconds > SOLAR_TERM_PRECISION_WINDOW_SECONDS:
        return None
    return (
        "节气精度提示：本出生时刻距最近的节气时刻仅约 %d 秒。"
        "节气时刻在不同来源之间存在秒级差异（2024 年立春：lunar-python "
        "08:27:07Z、sxtwl 08:26:53Z、JPL Horizons 08:27:00Z，相差约 14 "
        "秒以内），落在此精度窗口内的年柱、月柱归属存在源间不确定性，"
        "不应当作绝对精确。"
    ) % int(round(distance_seconds))


def resolve_zone(zone):
    """Return the IANA zone to use, defaulting missing zones to Shanghai."""
    if zone is None:
        return DEFAULT_ZONE
    if not isinstance(zone, str) or not zone:
        raise ValueError("Birth zone must be a non-empty IANA timezone name")
    try:
        ZoneInfo(zone)
    except Exception as exc:
        raise ValueError(
            "Unknown birth timezone: %r (pass an IANA name such as "
            "Asia/Shanghai or Europe/London)" % (zone,)
        ) from exc
    return zone


def _format_offset(offset):
    """Format a utcoffset timedelta as +HH:MM (with :SS when nonzero)."""
    total = int(offset.total_seconds())
    sign = "+" if total >= 0 else "-"
    total = abs(total)
    suffix = "%s%02d:%02d" % (sign, total // 3600, (total % 3600) // 60)
    if total % 60:
        suffix += ":%02d" % (total % 60)
    return suffix


def calendar_for_zone(value, zone=None, day_boundary="midnight"):
    """Mirror of calendar() computed in the birthplace wall-time frame.

    value: ISO datetime string or aware datetime, exactly as calendar()
    accepts. zone: IANA name (None -> Asia/Shanghai, documented default).
    Raises ValueError with the original input and the zone on any civil-time
    incoherence (gap, offset contradiction, ambiguous named zone, unknown
    zone, out-of-range year, naive input).
    """
    if day_boundary not in ("midnight", "zi-start"):
        raise ValueError("Unsupported day boundary")
    zone = resolve_zone(zone)
    try:
        audit = audit_birth_instant(value, tz_name=zone)
    except ValueError as exc:
        raise ValueError(
            "Birth value %r rejected in zone %s: %s" % (value, zone, exc)
        ) from exc
    instant = datetime.fromisoformat(value) if isinstance(value, str) else value
    local = instant.astimezone(ZoneInfo(zone))
    if not 1900 <= local.year <= 2099:
        raise ValueError("Supported calendar range is 1900..2099")
    # Local frame (birthplace wall time): the lunar date and the day/hour
    # pillars follow the birthplace civil day and clock (F-1 semantics,
    # verified 144/144 against independent references; do not move these
    # to another frame).
    lunar = Solar.fromYmdHms(
        local.year, local.month, local.day, local.hour, local.minute, local.second
    ).getLunar()
    day = (
        lunar.getDayInGanZhiExact2()
        if day_boundary == "midnight"
        else lunar.getDayInGanZhiExact()
    )
    hour = hour_pillar(day[0], BRANCHES[((local.hour + 1) // 2) % 12])
    # Instant frame (TJ-031.6): year/month attribution is decided by where
    # the instant falls relative to the jieqi instants. The provider's
    # jieqi table is a China-baseline wall-time table, so attribution is
    # read from a Lunar object fed the instant's Asia/Shanghai wall time --
    # exactly the fields the frozen calendar() feeds. For zone ==
    # Asia/Shanghai this object is field-identical to the local one, so
    # Shanghai output is unchanged.
    china = instant.astimezone(ZoneInfo("Asia/Shanghai"))
    china_lunar = Solar.fromYmdHms(
        china.year, china.month, china.day, china.hour, china.minute, china.second
    ).getLunar()
    previous = china_lunar.getPrevJieQi(False)
    jieqi_wall = previous.getSolar().toYmdHms()
    jieqi_naive = datetime.strptime(jieqi_wall, "%Y-%m-%d %H:%M:%S")
    # jieqi_wall is a UTC+08:00-baseline reading of an absolute instant
    # (the provider baseline, independent of historical China DST), so
    # the term instant is wall - 8h. solar_term_started_at renders that
    # instant in the birthplace zone: every zone's label reads back to
    # the same UTC instant, equal to the provider term instant the
    # pillars were attributed with.
    jieqi_instant = jieqi_naive.replace(
        tzinfo=timezone(timedelta(hours=8))
    ).astimezone(ZoneInfo(zone))
    # Nearest-term distance for the precision note: the attribution
    # above used the provider's term instants, so the distance is
    # measured against the provider's previous AND next term instants
    # (a birth just before a term is as exposed to the inter-source
    # divergence as one just after it).
    next_wall = china_lunar.getNextJieQi(False).getSolar().toYmdHms()
    next_naive = datetime.strptime(next_wall, "%Y-%m-%d %H:%M:%S")
    next_instant = next_naive.replace(tzinfo=timezone(timedelta(hours=8)))
    term_distance = min(
        abs((instant - jieqi_instant).total_seconds()),
        abs((next_instant - instant).total_seconds()),
    )
    return {
        "local_datetime": local.isoformat(),
        "solar_term": previous.getName(),
        "solar_term_started_at": jieqi_instant.strftime("%Y-%m-%d %H:%M:%S")
        + _format_offset(jieqi_instant.utcoffset()),
        "year_ganzhi": china_lunar.getYearInGanZhiExact(),
        "month_ganzhi": china_lunar.getMonthInGanZhiExact(),
        "day_ganzhi": day,
        "hour_ganzhi": hour,
        "day_boundary": day_boundary,
        "calendar_provider": PROVIDER,
        "lunar_year": lunar.getYear(),
        "lunar_month": lunar.getMonth(),
        "lunar_day": lunar.getDay(),
        "tz_name": zone,
        "civil_classification": audit["civil_classification"],
        "offset_disambiguation": audit["offset_disambiguation"],
        "solar_term_precision_note": _solar_term_precision_note(term_distance),
    }


def precision_note_for(value, zone=None):
    """Solar-term precision note for an instant, or None.

    Convenience over calendar_for_zone for public-boundary callers
    (scenario responses) whose executed result does not carry the
    input calendar. Raises exactly what calendar_for_zone raises for
    incoherent civil times; intended for inputs that already executed
    successfully.
    """
    return calendar_for_zone(value, zone)["solar_term_precision_note"]
