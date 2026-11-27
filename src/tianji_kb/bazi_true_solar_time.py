"""Optional apparent (true) solar time conversion -- B7, research only.

TJ-0424 (B7 adjudication 2026-11-25, approved with conditions): an
OPTIONAL true-solar-time conversion for bazi charting. This module is a
pure function only. It does NOT replace, modify, or re-wire any existing
charting logic: the current standard-time charting convention
(``bazi_core.py`` and friends) is unchanged, and no public API field is
added by this module. A caller that wants the optional conversion calls
:func:`apparent_solar_time` explicitly and decides itself what to do
with the result.

Status: research_only=True, public=False, ai=False. No adjudicated
classical rule is claimed: true solar time is a modern astronomical
conversion, not a classical-text verdict.

Astronomical basis (verifiable modern formulae, no invented constants)
----------------------------------------------------------------------
Equation of time and the solar position follow the standard
approximation published by the NOAA Global Monitoring Laboratory Solar
Calculator:

* NOAA GML, "Solar Calculator" equations,
  https://gml.noaa.gov/grad/solcalc/solareqns.PDF
  (also https://gml.noaa.gov/grad/solcalc/ ; the same equations are
  reproduced in the Solar Calculator source, ``solcalc.js``).
* The equations are the low-precision solar-position algorithm of
  Jean Meeus, *Astronomical Algorithms*, 2nd ed. (1998), ch. 25
  (solar coordinates) and ch. 28 (equation of time), as implemented
  by NOAA. All constants below are copied verbatim from the NOAA
  publication; none is invented here.

Definitions (NOAA sign convention):

* ``EoT`` (minutes) = apparent solar time - mean solar time, i.e. the
  amount added to mean (clock) solar time to get apparent solar time.
  EoT is about -14.2 min near 11 Feb and about +16.4 min near 3 Nov.
* Longitude correction (minutes) = 4 * (longitude - standard meridian),
  where the standard meridian is 15 degrees per hour of time-zone
  offset east of Greenwich. East longitude is positive. The
  longitude difference is wrapped to [-180, 180), so the correction
  is continuous across the dateline (+180 and -180 are one meridian).
  T2 (2026-11-25): the wrap is approved as the formal dateline
  convention; local date, time-zone and cross-day results are
  verified in tests/test_tj0424_true_solar_time.py (dateline
  continuity, +/-180 extremes, +14/-12 zones, cross-day pairs).
* Apparent solar time = local standard (wall-clock) time
  + longitude correction + EoT.

Inputs are explicit: the caller supplies the birth instant (a
timezone-aware datetime, which defines the absolute instant), the
longitude, and the time-zone offset. Historical time zones are NEVER
guessed -- a historical zone must be passed in as ``tz_offset``
(and, where the historical standard meridian differs from
15 * tz_offset, as ``standard_meridian_deg``). Daylight saving must
already be reflected in the supplied ``tz_offset``. The equation
of time is always evaluated at the input instant itself, so the
same physical instant gives the same result whatever time
representation it was written in.

IANA tzdb validation (T3, approved 2026-11-25)
-----------------------------------------------
:func:`validate_tz_offset` cross-checks a caller-supplied offset
against the IANA time-zone database (``zoneinfo``, system tzdata) for
the same instant. It never supplies an offset by itself and never
overrides the caller: it reports match / mismatch / LMT-era, the
tzdb version in use, and the coverage limits. Coverage differs per
zone: most zones record transitions only from the late 19th / early
20th century, and before a zone's first recorded transition the
tzdb offset is local mean time (LMT) -- derived from longitude,
approximate, and not a civil standard. An LMT offset is recognised
here by its non-whole-minute value (e.g. Asia/Shanghai before 1901
is +08:05:43); such an offset can never serve as a ``tz_offset``
(this module requires whole minutes) and is reported as
``lmt_era`` rather than silently rounded. Agreement with tzdb is a
consistency check, not proof that an offset is historically
correct: tzdb is itself a compiled, versioned secondary source and
historical offsets are revised between versions.

Precision limits (stated, not hidden)
-------------------------------------
* The NOAA approximation is good to roughly +/-0.5 arc-minute in solar
  position for 1900-2100, which maps to roughly +/-1 minute in the
  equation of time; cross-checked here against the JPL DE421 ephemeris
  via Skyfield (see tests/test_tj0424_true_solar_time.py). It is NOT
  ephemeris-grade: for sub-minute work use a real ephemeris.
* Delta-T (TT minus UTC, ~69 s in 2026) is not modelled; its effect on
  the equation of time is below 0.01 min and is absorbed in the
  +/-1 min budget above.
* Longitude must be supplied by the caller; a wrong longitude is a
  wrong result (4 minutes per degree). This module performs no
  geocoding and no place-name lookup.
* The conversion is defined on the Gregorian calendar only.
"""

import math
from datetime import datetime, timedelta, timezone

try:
    from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
except ImportError:  # pragma: no cover - Python >= 3.9 always has it
    ZoneInfo = None
    ZoneInfoNotFoundError = LookupError

__all__ = [
    "apparent_solar_time",
    "equation_of_time_minutes",
    "longitude_correction_minutes",
    "tzdb_offset_hours",
    "tzdb_version",
    "validate_tz_offset",
    "RESEARCH_ONLY",
    "PUBLIC",
    "AI",
    "METHOD_ID",
    "ASTRONOMICAL_BASIS",
    "TZDB_COVERAGE_NOTE",
]

#: Module status flags (B7: optional conversion, research only).
RESEARCH_ONLY = True
PUBLIC = False
AI = False

#: Method identifier carried in every result dict.
METHOD_ID = "noaa-solar-calculator-approx-v1"

#: Human-readable statement of the astronomical basis.
ASTRONOMICAL_BASIS = (
    "NOAA Global Monitoring Laboratory Solar Calculator equations "
    "(gml.noaa.gov/grad/solcalc/solareqns.PDF), implementing the "
    "low-precision solar-position algorithm of Jean Meeus, "
    "Astronomical Algorithms, 2nd ed., ch. 25 and ch. 28. "
    "Equation of time uses the NOAA sign convention "
    "(apparent minus mean solar time)."
)

#: Stated precision of the approximation (see module docstring).
PRECISION_LIMITS = (
    "NOAA approximation, accurate to about +/-1 minute in the equation "
    "of time for 1900-2100 (cross-checked against JPL DE421 via Skyfield; "
    "see tests/test_tj0424_true_solar_time.py); not ephemeris-grade, "
    "unsuitable for sub-minute work. Delta-T is not modelled (effect "
    "below 0.01 min). Longitude is caller-supplied (4 min per degree); "
    "no geocoding is performed. Gregorian calendar only. Historical "
    "time zones are never guessed: tz_offset (and, where applicable, "
    "standard_meridian_deg) must be supplied explicitly, already "
    "including any daylight saving in force."
)

#: What this module does NOT do (carried in every result).
METHOD_NOTE = (
    "Optional conversion only. The current standard-time charting "
    "convention is unchanged: this result must not be silently "
    "substituted for the standard-time input of any existing charting "
    "function. No classical rule is claimed; true solar time is a "
    "modern astronomical conversion, not a classical-text verdict."
)

#: IANA tzdb coverage and uncertainty (T3, approved 2026-11-25).
#: Stated here once and carried in every validation result.
TZDB_COVERAGE_NOTE = (
    "IANA time-zone database (zoneinfo, system tzdata) as shipped "
    "with this runtime; the exact version is reported per call by "
    "tzdb_version(). Coverage differs per zone: most zones record "
    "transitions only from the late 19th / early 20th century, and "
    "before a zone's first recorded transition the tzdb offset is "
    "local mean time (LMT), derived from longitude, approximate, and "
    "not a civil standard. tzdb is a compiled, versioned secondary "
    "source: historical offsets are revised between versions, so "
    "agreement with tzdb is a consistency check, not proof that an "
    "offset is historically correct."
)

# --- NOAA constants (verbatim from the NOAA Solar Calculator) -----------
_J2000_JD = 2451545.0
_DAYS_PER_JULIAN_CENTURY = 36525.0
_UNIX_EPOCH_JD = 2440587.5


def _julian_day(utc_dt):
    """Julian Day for an aware UTC datetime."""
    timestamp = utc_dt.timestamp()
    return timestamp / 86400.0 + _UNIX_EPOCH_JD


def _julian_century(utc_dt):
    return (_julian_day(utc_dt) - _J2000_JD) / _DAYS_PER_JULIAN_CENTURY


def equation_of_time_minutes(utc_dt):
    """Equation of time in minutes (NOAA sign: apparent minus mean).

    ``utc_dt`` must be a timezone-aware datetime; it is read as an
    absolute instant (converted to UTC internally). Pure function.
    """
    if not isinstance(utc_dt, datetime) or utc_dt.tzinfo is None:
        raise ValueError(
            "equation_of_time_minutes requires a timezone-aware datetime")
    t = _julian_century(utc_dt.astimezone(timezone.utc))
    # Geometric mean longitude of the Sun (degrees).
    l0 = (280.46646 + t * (36000.76983 + 0.0003032 * t)) % 360.0
    # Geometric mean anomaly of the Sun (degrees).
    m = 357.52911 + t * (35999.05029 - 0.0001537 * t)
    # Eccentricity of Earth's orbit.
    ecc = 0.016708634 - t * (0.000042037 + 0.0000001267 * t)
    # Longitude of the ascending node of the Moon's mean orbit (degrees).
    # Needed below for the corrected obliquity; the equation of centre /
    # apparent longitude chain of the full NOAA solar-position
    # computation is NOT needed for the equation of time and is
    # deliberately not computed here (no dead arithmetic).
    omega = 125.04 - 1934.136 * t
    # Mean obliquity of the ecliptic (degrees), then corrected obliquity.
    eps0 = 23.0 + (
        26.0
        + ((21.448 - t * (46.815 + t * (0.00059 - t * 0.001813))) / 60.0)
    ) / 60.0
    eps = eps0 + 0.00256 * math.cos(math.radians(omega))
    # Equation of time (minutes). y = tan^2(eps/2); NOAA's published form.
    m_rad = math.radians(m)
    y = math.tan(math.radians(eps / 2.0)) ** 2
    l0_rad = math.radians(l0)
    eot = 4.0 * math.degrees(
        y * math.sin(2.0 * l0_rad)
        - 2.0 * ecc * math.sin(m_rad)
        + 4.0 * ecc * y * math.sin(m_rad) * math.cos(2.0 * l0_rad)
        - 0.5 * y * y * math.sin(4.0 * l0_rad)
        - 1.25 * ecc * ecc * math.sin(2.0 * m_rad)
    )
    return eot


def _longitude_difference_deg(longitude_deg, meridian_deg):
    """Signed longitude difference in degrees, wrapped to [-180, 180).

    Longitude is circular: +180 and -180 are the same meridian, so a
    plain subtraction has a 1440-minute discontinuity at the dateline
    (lon 179.9 vs -179.9 would differ by a full day). Wrapping the
    difference keeps the correction continuous across the dateline.
    T2 (2026-11-25): this wrap is approved as the formal dateline
    convention.
    """
    return ((float(longitude_deg) - float(meridian_deg) + 180.0) % 360.0) - 180.0


def longitude_correction_minutes(longitude_deg, standard_meridian_deg):
    """Longitude correction in minutes: 4 * (longitude - meridian).

    East longitude positive, meridian in degrees east. The difference
    is wrapped to [-180, 180) so the correction is continuous across
    the dateline (+180 and -180 are the same meridian). Pure function.
    """
    _check_longitude(longitude_deg, "longitude_deg")
    _check_meridian(standard_meridian_deg)
    return 4.0 * _longitude_difference_deg(
        longitude_deg, standard_meridian_deg)


def _check_longitude(value, name):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError("%s must be a number of degrees" % (name,))
    if math.isnan(value) or math.isinf(value):
        raise ValueError("%s must be finite" % (name,))
    if not -180.0 <= float(value) <= 180.0:
        raise ValueError(
            "%s %r out of range [-180, 180] degrees" % (name, value))


def _check_meridian(value):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError("standard_meridian_deg must be a number of degrees")
    if math.isnan(value) or math.isinf(value):
        raise ValueError("standard_meridian_deg must be finite")
    if not -180.0 <= float(value) <= 180.0:
        raise ValueError(
            "standard_meridian_deg %r out of range [-180, 180] degrees"
            % (value,))


def _tz_offset_hours(tz_offset):
    """Normalise a tz offset (hours as number, or timedelta) to float hours."""
    if isinstance(tz_offset, timedelta):
        hours = tz_offset.total_seconds() / 3600.0
    elif isinstance(tz_offset, bool) or not isinstance(tz_offset, (int, float)):
        raise ValueError(
            "tz_offset must be hours as a number, or a timedelta")
    else:
        hours = float(tz_offset)
    if math.isnan(hours) or math.isinf(hours):
        raise ValueError("tz_offset must be finite")
    if not -12.0 <= hours <= 14.0:
        raise ValueError(
            "tz_offset %r out of range [-12, +14] hours" % (hours,))
    # Offsets are whole minutes in every real civil zone; reject
    # sub-minute values rather than silently rounding them.
    if abs(hours * 60.0 - round(hours * 60.0)) > 1e-9:
        raise ValueError(
            "tz_offset %r is not a whole number of minutes" % (hours,))
    return hours


def apparent_solar_time(dt, longitude_deg, tz_offset, *,
                        standard_meridian_deg=None):
    """Convert a local standard time to apparent (true) solar time.

    Parameters
    ----------
    dt : datetime, timezone-aware.
        The birth instant. ``dt`` defines the absolute instant;
        ``tz_offset`` names the civil zone whose wall reading the
        conversion is expressed in (the wall reading is ``dt``
        expressed in that zone). Naive datetimes are refused (a
        wall-clock reading without a zone is ambiguous). Historical
        zones are supplied as ``tz_offset`` (and
        ``standard_meridian_deg`` where it differs from
        15 * tz_offset), never guessed.
    longitude_deg : float.
        Longitude in degrees, east positive, west negative, [-180, 180].
    tz_offset : float or timedelta.
        Time-zone offset east of UTC in hours (e.g. 8 for CST, 5.5 for
        IST, -5 for EST). Must already include any daylight saving in
        force at ``dt``; this function never guesses DST or history.
    standard_meridian_deg : float, optional.
        Standard meridian in degrees east. Defaults to 15 * tz_offset,
        wrapped into [-180, 180] (so tz_offset=+14 gives -150, the
        same meridian as +210). Pass explicitly when the historical
        standard meridian differs from 15 * tz_offset.

    Returns a structured dict (see module docstring). The apparent
    solar time is an aware datetime in a fixed-offset zone of
    ``tz_offset``. ``date_shifted`` / ``date_shift_days`` state
    explicitly whether the correction moved the result onto another
    calendar date.
    """
    if not isinstance(dt, datetime) or dt.tzinfo is None:
        raise ValueError(
            "dt must be a timezone-aware datetime; naive datetimes are "
            "refused (a wall-clock reading without a zone is ambiguous)")
    _check_longitude(longitude_deg, "longitude_deg")
    offset_hours = _tz_offset_hours(tz_offset)
    if standard_meridian_deg is None:
        # 15 degrees per hour, wrapped into [-180, 180]: tz_offset=+14
        # names the same meridian as +210 degrees, i.e. -150.
        meridian = ((15.0 * offset_hours + 180.0) % 360.0) - 180.0
    else:
        _check_meridian(standard_meridian_deg)
        meridian = float(standard_meridian_deg)

    # The absolute instant is dt itself: an aware datetime IS its
    # instant, whatever representation it was written in. Every
    # quantity below is derived from this one instant, so the same
    # physical instant gives the same result in any representation
    # (T4 invariant: one physical instant, one solar term).
    # The previous code evaluated the equation of time at
    # wall-minus-offset while applying the shift to dt's own
    # instant, so the EoT sat away from the true instant by the
    # representation gap (up to ~30 s of solar time) whenever
    # dt's own offset differed from tz_offset -- and the same
    # birth could land on either side of a jieqi moment depending
    # on how it was written. tz_offset still names the civil
    # zone: the wall reading is dt expressed in that zone, and
    # the apparent time is returned in that zone.
    utc_dt = dt.astimezone(timezone.utc)
    local_tz = timezone(timedelta(hours=offset_hours))
    wall = utc_dt.astimezone(local_tz).replace(tzinfo=None)

    eot = equation_of_time_minutes(utc_dt)
    lon_corr = 4.0 * _longitude_difference_deg(longitude_deg, meridian)
    total = lon_corr + eot
    apparent = dt.astimezone(local_tz) + timedelta(minutes=total)
    # Re-anchor the fixed-offset zone (astimezone already yields it;
    # this keeps the returned tz exactly the stated offset).
    apparent = apparent.astimezone(local_tz)

    input_date = wall.date()
    apparent_date = apparent.date()
    shift_days = (apparent_date - input_date).days
    return {
        "apparent_solar_time": apparent,
        "input_local_time": dt,
        "input_date": input_date.isoformat(),
        "apparent_date": apparent_date.isoformat(),
        "date_shifted": shift_days != 0,
        "date_shift_days": shift_days,
        "longitude_deg": float(longitude_deg),
        "tz_offset_hours": offset_hours,
        "standard_meridian_deg": meridian,
        "longitude_correction_minutes": lon_corr,
        "equation_of_time_minutes": eot,
        "total_correction_minutes": total,
        "julian_day": _julian_day(utc_dt),
        "method": METHOD_ID,
        "astronomical_basis": ASTRONOMICAL_BASIS,
        "calendar_basis": (
            "Gregorian calendar; the UTC instant is the input "
            "datetime's own instant (the same physical instant in "
            "any representation); historical zones are never guessed "
            "-- tz_offset must be supplied explicitly."
        ),
        "precision_limits": PRECISION_LIMITS,
        "method_note": METHOD_NOTE,
        "optional_conversion": True,
        "current_standard_time_convention_unchanged": True,
        "research_only": RESEARCH_ONLY,
        "public": PUBLIC,
        "ai": AI,
        "status": "ok",
    }


# ======================================================================
# IANA tzdb validation (T3, approved 2026-11-25).
#
# These functions only READ the database and REPORT a verdict. They
# never supply an offset on their own and never override the caller:
# the conversion above keeps taking its explicit ``tz_offset``.
# ======================================================================

_TZDB_VERSION_CACHE = None


def _tzdata_zi_version():
    """Version string from a system tzdata.zi file, or None.

    System tzdata ships ``tzdata.zi`` whose first line is
    ``# version <version>``. The file location varies by platform;
    every ``zoneinfo.TZPATH`` entry is tried.
    """
    import os
    import re

    candidates = []
    try:
        import zoneinfo as _zoneinfo

        candidates.extend(_zoneinfo.TZPATH)
    except Exception:
        pass
    candidates.extend(("/usr/share/zoneinfo", "/usr/lib/zoneinfo",
                        "/etc/zoneinfo"))
    seen = set()
    for base in candidates:
        if base in seen:
            continue
        seen.add(base)
        path = os.path.join(base, "tzdata.zi")
        try:
            with open(path, "r", encoding="utf-8") as handle:
                first = handle.readline()
        except (OSError, UnicodeDecodeError):
            continue
        match = re.search(r"#\s*version\s+(\S+)", first)
        if match:
            return match.group(1)
    return None


def tzdb_version():
    """IANA tzdb version in use, as a string.

    Prefers the ``tzdata`` package version when installed, else the
    system tzdata version from ``tzdata.zi``; if neither is readable
    the result states that the version is not exposed (the offsets
    themselves are still read from the database). Pure function.
    """
    global _TZDB_VERSION_CACHE
    if _TZDB_VERSION_CACHE is not None:
        return _TZDB_VERSION_CACHE
    version = None
    try:
        from importlib.metadata import version as _pkg_version

        version = _pkg_version("tzdata")
    except Exception:
        version = None
    if version is None:
        version = _tzdata_zi_version()
    if version is None:
        version = "system tzdata (version not exposed)"
    _TZDB_VERSION_CACHE = version
    return version


def _tzdb_zone(tz_name):
    """ZoneInfo for ``tz_name`` or a fail-closed ValueError."""
    if ZoneInfo is None:
        raise ValueError(
            "IANA tzdb validation is unavailable: zoneinfo is not "
            "present in this runtime")
    if not isinstance(tz_name, str) or not tz_name:
        raise ValueError("tz_name must be a non-empty IANA zone name")
    try:
        return ZoneInfo(tz_name)
    except ZoneInfoNotFoundError:
        raise ValueError(
            "unknown IANA time zone %r" % (tz_name,)) from None


def tzdb_offset_hours(tz_name, dt):
    """UTC offset in hours for ``tz_name`` at aware datetime ``dt``.

    Read straight from the IANA database via ``zoneinfo``. The value
    may carry seconds (local mean time, e.g. Asia/Shanghai before
    1901 is +08:05:43): callers that need a whole-minute ``tz_offset``
    must treat such a value as unusable, never round it. Raises
    ValueError on an unknown zone or a naive datetime.
    """
    if not isinstance(dt, datetime) or dt.tzinfo is None:
        raise ValueError(
            "tzdb_offset_hours requires a timezone-aware datetime")
    zone = _tzdb_zone(tz_name)
    offset = dt.astimezone(zone).utcoffset()
    if offset is None:
        raise ValueError(
            "IANA zone %r has no UTC offset at %s"
            % (tz_name, dt.isoformat()))
    return offset.total_seconds() / 3600.0


def _is_whole_minutes(hours):
    return abs(hours * 60.0 - round(hours * 60.0)) < 1e-9


def _offset_label(hours):
    """'+08:00' / '-05:00' / '+08:05:43' rendering of an offset in hours."""
    total_seconds = int(round(hours * 3600.0))
    sign = "+" if total_seconds >= 0 else "-"
    total_seconds = abs(total_seconds)
    hh, rem = divmod(total_seconds, 3600)
    mm, ss = divmod(rem, 60)
    if ss:
        return "%s%02d:%02d:%02d" % (sign, hh, mm, ss)
    return "%s%02d:%02d" % (sign, hh, mm)


def validate_tz_offset(tz_name, dt, tz_offset):
    """Cross-check a caller-supplied offset against IANA tzdb.

    Parameters
    ----------
    tz_name : str
        IANA zone name, e.g. ``"Asia/Shanghai"``.
    dt : datetime, timezone-aware.
        The instant the offset is claimed for (read as an absolute
        instant; its own tzinfo is not trusted beyond that).
    tz_offset : float or timedelta.
        The caller-supplied offset in hours, already normalised by
        the same rules as :func:`apparent_solar_time` (whole minutes,
        [-12, +14]).

    Returns a verdict dict; it never raises on a mismatch -- a
    mismatch is a verdict, not an exception. ``status`` is one of:

    * ``"match"`` -- tzdb agrees with the supplied offset exactly,
      and the tzdb offset is a whole number of minutes.
    * ``"mismatch"`` -- tzdb gives a different whole-minute offset
      (wrong offset, DST state, or a historical change the caller
      did not account for).
    * ``"lmt_era"`` -- the tzdb offset at this instant is local mean
      time (non-whole-minute, e.g. +08:05:43): a pre-standard-time
      era in which no civil offset exists to agree with. The
      supplied offset can neither match nor be validated; it must
      be supplied from another source, never derived by rounding
      the LMT value.

    Unknown zones and naive datetimes raise ValueError (fail-closed
    inputs). Agreement is a consistency check, not proof of
    historical correctness (see ``TZDB_COVERAGE_NOTE``).
    """
    if not isinstance(dt, datetime) or dt.tzinfo is None:
        raise ValueError(
            "validate_tz_offset requires a timezone-aware datetime")
    supplied_hours = _tz_offset_hours(tz_offset)
    tzdb_hours = tzdb_offset_hours(tz_name, dt)
    whole = _is_whole_minutes(tzdb_hours)
    matches = whole and abs(
        tzdb_hours - supplied_hours) < 1e-9
    if not whole:
        status = "lmt_era"
        uncertainty = (
            "The tzdb offset at this instant is local mean time "
            "(%s), not a civil standard offset: this is a "
            "pre-standard-time era for %s. The value is derived "
            "from longitude, approximate, and must never be rounded "
            "into a tz_offset; supply the offset from another source."
            % (_offset_label(tzdb_hours), tz_name))
    elif matches:
        status = "match"
        uncertainty = (
            "tzdb agrees with the supplied offset at this instant. "
            "Agreement is a consistency check, not proof that the "
            "offset is historically correct: tzdb is a compiled, "
            "versioned secondary source (version %s)."
            % tzdb_version())
    else:
        status = "mismatch"
        uncertainty = (
            "tzdb gives %s at this instant, not the supplied %s. "
            "Check the offset, the DST state in force, and whether "
            "the zone's offset changed historically (tzdb version "
            "%s)."
            % (_offset_label(tzdb_hours),
               _offset_label(supplied_hours), tzdb_version()))
    return {
        "tz_name": tz_name,
        "instant": dt.astimezone(timezone.utc).isoformat(),
        "tzdb_offset_hours": tzdb_hours,
        "tzdb_offset": _offset_label(tzdb_hours),
        "tzdb_offset_is_whole_minutes": whole,
        "supplied_offset_hours": supplied_hours,
        "supplied_offset": _offset_label(supplied_hours),
        "matches": matches,
        "status": status,
        "tzdb_version": tzdb_version(),
        "coverage": TZDB_COVERAGE_NOTE,
        "uncertainty": uncertainty,
        "method": "iana-tzdb-validation-v1",
        "research_only": RESEARCH_ONLY,
        "public": PUBLIC,
        "ai": AI,
    }
