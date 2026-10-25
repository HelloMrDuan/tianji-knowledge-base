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
audit which frame produced the pillars. solar_term_started_at carries the
zone offset at the jieqi moment (calendar() historically hardcodes '+08:00'
even in DST; this module labels correctly for every zone).
"""

from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from lunar_python import Solar

from .bazi_calendar_precision_audit import audit_birth_instant
from .calendar import PROVIDER, hour_pillar
from .foundations import BRANCHES

DEFAULT_ZONE = "Asia/Shanghai"


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


def _offset_suffix(naive_wall, zone):
    """Format the zone offset at a naive wall time as +HH:MM (round-trip safe)."""
    tz = ZoneInfo(zone)
    for fold in (0, 1):
        candidate = naive_wall.replace(tzinfo=tz, fold=fold)
        if candidate.astimezone(timezone.utc).astimezone(tz).replace(
            tzinfo=None
        ) == naive_wall:
            offset = candidate.utcoffset()
            break
    else:  # pragma: no cover - jieqi moments do not fall in DST gaps
        offset = naive_wall.replace(tzinfo=tz, fold=0).utcoffset()
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
    lunar = Solar.fromYmdHms(
        local.year, local.month, local.day, local.hour, local.minute, local.second
    ).getLunar()
    day = (
        lunar.getDayInGanZhiExact2()
        if day_boundary == "midnight"
        else lunar.getDayInGanZhiExact()
    )
    hour = hour_pillar(day[0], BRANCHES[((local.hour + 1) // 2) % 12])
    previous = lunar.getPrevJieQi(False)
    jieqi_wall = previous.getSolar().toYmdHms()
    jieqi_naive = datetime.strptime(jieqi_wall, "%Y-%m-%d %H:%M:%S")
    return {
        "local_datetime": local.isoformat(),
        "solar_term": previous.getName(),
        "solar_term_started_at": jieqi_wall + _offset_suffix(jieqi_naive, zone),
        "year_ganzhi": lunar.getYearInGanZhiExact(),
        "month_ganzhi": lunar.getMonthInGanZhiExact(),
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
    }
