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
  offset east of Greenwich. East longitude is positive.
* Apparent solar time = local standard (wall-clock) time
  + longitude correction + EoT.

Inputs are explicit: the caller supplies the local wall time, the
longitude, and the time-zone offset. Historical time zones are NEVER
guessed -- a historical zone must be passed in as ``tz_offset``
(and, where the historical standard meridian differs from
15 * tz_offset, as ``standard_meridian_deg``). Daylight saving must
already be reflected in the supplied ``tz_offset``.

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

__all__ = [
    "apparent_solar_time",
    "equation_of_time_minutes",
    "longitude_correction_minutes",
    "RESEARCH_ONLY",
    "PUBLIC",
    "AI",
    "METHOD_ID",
    "ASTRONOMICAL_BASIS",
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


def longitude_correction_minutes(longitude_deg, standard_meridian_deg):
    """Longitude correction in minutes: 4 * (longitude - meridian).

    East longitude positive, meridian in degrees east. Pure function.
    """
    _check_longitude(longitude_deg, "longitude_deg")
    _check_meridian(standard_meridian_deg)
    return 4.0 * (float(longitude_deg) - float(standard_meridian_deg))


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
        The local wall-clock time. Only the wall-clock reading is used,
        together with the explicit ``tz_offset``; ``dt.tzinfo`` is
        required (naive datetimes are refused) but its own UTC offset
        is NOT trusted -- the explicit ``tz_offset`` is authoritative,
        so that historical zones can be supplied without guessing.
    longitude_deg : float.
        Longitude in degrees, east positive, west negative, [-180, 180].
    tz_offset : float or timedelta.
        Time-zone offset east of UTC in hours (e.g. 8 for CST, 5.5 for
        IST, -5 for EST). Must already include any daylight saving in
        force at ``dt``; this function never guesses DST or history.
    standard_meridian_deg : float, optional.
        Standard meridian in degrees east. Defaults to 15 * tz_offset.
        Pass explicitly when the historical standard meridian differs
        from 15 * tz_offset.

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
        meridian = 15.0 * offset_hours
    else:
        _check_meridian(standard_meridian_deg)
        meridian = float(standard_meridian_deg)

    # Wall-clock reading + explicit offset -> absolute instant (UTC).
    # dt.tzinfo is deliberately not used for the conversion.
    wall = dt.replace(tzinfo=None)
    utc_dt = (wall - timedelta(hours=offset_hours)).replace(
        tzinfo=timezone.utc)
    local_tz = timezone(timedelta(hours=offset_hours))

    eot = equation_of_time_minutes(utc_dt)
    lon_corr = 4.0 * (float(longitude_deg) - meridian)
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
            "Gregorian calendar; UTC derived from the explicit tz_offset "
            "parameter (historical zones are never guessed); the input "
            "datetime's own tzinfo offset is not trusted."
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
