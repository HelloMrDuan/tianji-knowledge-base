"""Opt-in research-only *simulation* of three-days-per-year Dayun conversion.

Classical rule and calendar-year interpolation have NOT been adjudicated into
Canonical Phase2. These arithmetic candidates must not become dated Dayun facts.
"""
from datetime import datetime, timedelta, timezone
from decimal import Decimal, ROUND_HALF_UP
from fractions import Fraction
from zoneinfo import ZoneInfo

from .bazi_core import ten_god
from .bazi_dayun_jie import JIE_NAMES, SECONDS_PER_DAY
from .foundations import CYCLE, STEMS, ganzhi_index

VARIANT = "bazi-dayun-three-days-mean-year-research-v1"
GREGORIAN_MEAN_YEAR_SECONDS = 31_556_952  # 365.2425 * 86400, exact.
THREE_DAYS_SECONDS = 3 * 86400
DAYUN_NOMINAL_YEARS = 10
CHINA = ZoneInfo("Asia/Shanghai")


def _half_up_fraction(value):
    """Round nonnegative rational seconds, ties upward, without floats."""
    if value < 0:
        raise ValueError("Synthetic time offset must be nonnegative")
    return (value.numerator * 2 + value.denominator) // (2 * value.denominator)


def simulate_dayun_age_and_timeline(birth_iso, measured_jie, rows, *, natal_day_master):
    """Return a distinctly labelled, non-authoritative arithmetic demonstration.

    The 365.2425-day Gregorian mean year is a MODERN interpolation convention,
    not an audited traditional procedure for true start dates. Input must be
    from the real pinned 12-Jie provider and current sequence generator.
    """
    if not isinstance(measured_jie, dict) or measured_jie.get("variant") != "bazi-dayun-adjacent-jie-research-v1":
        raise ValueError("Simulation requires measured adjacent Jie research result")
    if measured_jie.get("calendar_provider") != "lunar-python==1.4.8":
        raise ValueError("Simulation requires pinned calendar provider")
    if (measured_jie.get("research_only") is not True or
            measured_jie.get("dayun_conversion_rule_review_status") != "unreviewed" or
            measured_jie.get("birth_local_datetime") != birth_iso):
        raise ValueError("Simulation requires matching unreviewed Jie measurement")
    elapsed = measured_jie.get("elapsed_seconds")
    if type(elapsed) is not int or elapsed <= 0 or elapsed > 40 * SECONDS_PER_DAY:
        # Zero-distance resolution remains a separate classical convention.
        raise ValueError("Zero or invalid Jie distance has unresolved start-age handling")
    if not isinstance(rows, list) or not 1 <= len(rows) <= 12:
        raise ValueError("Expected 1..12 deterministic Dayun candidate rows")

    def as_utc_second(value):
        if type(value) is not str:
            raise ValueError("Expected timezone-aware whole-second Jie timestamp")
        try:
            instant = datetime.fromisoformat(value)
        except ValueError as error:
            raise ValueError("Expected timezone-aware whole-second Jie timestamp") from error
        if instant.tzinfo is None or instant.utcoffset() is None or instant.microsecond:
            raise ValueError("Expected timezone-aware whole-second Jie timestamp")
        return instant.astimezone(timezone.utc)

    birth_utc = as_utc_second(birth_iso)
    if birth_utc.astimezone(CHINA).isoformat() != birth_iso:
        raise ValueError("Measured Jie birth must use local Asia/Shanghai time")
    direction = measured_jie.get("direction")
    if direction not in ("forward", "backward") or type(direction) is not str:
        raise ValueError("Measured Jie direction must be explicit")
    previous, following, selected = (
        measured_jie.get("previous_jie"), measured_jie.get("next_jie"),
        measured_jie.get("selected_jie"))
    if any(type(item) is not dict or item.get("name") not in JIE_NAMES
           for item in (previous, following, selected)):
        raise ValueError("Measured Jie boundary names are invalid")
    prev_utc, next_utc = as_utc_second(previous.get("at")), as_utc_second(following.get("at"))
    if not (prev_utc <= birth_utc < next_utc
            and timedelta(0) < next_utc - prev_utc <= timedelta(days=40)):
        raise ValueError("Measured Jie birth and adjacent boundaries disagree")
    expected_selected = following if direction == "forward" else previous
    if selected != expected_selected:
        raise ValueError("Measured Jie selection disagrees with direction")
    expected_elapsed = int(((next_utc - birth_utc) if direction == "forward"
                            else (birth_utc - prev_utc)).total_seconds())
    if (expected_elapsed != elapsed or measured_jie.get("zero_distance") is not False
            or measured_jie.get("elapsed_whole_days") != elapsed // SECONDS_PER_DAY
            or measured_jie.get("remaining_seconds_after_whole_days")
               != elapsed % SECONDS_PER_DAY):
        raise ValueError("Measured Jie distance arithmetic is inconsistent")
    month_ganzhi = measured_jie.get("birth_month_ganzhi")
    if type(month_ganzhi) is not str:
        raise ValueError("Measured Jie requires source month pillar")
    month_index = ganzhi_index(month_ganzhi)
    if type(natal_day_master) is not str or natal_day_master not in STEMS:
        raise ValueError("Expected validated natal day master for Ten Gods")
    sign = 1 if direction == "forward" else -1
    for index, row in enumerate(rows):
        expected = CYCLE[(month_index + sign * (index + 1)) % 60]
        if (type(row) is not dict or type(row.get("period_index")) is not int
                or row["period_index"] != index + 1
                or row.get("candidate_ganzhi") != expected
                or row.get("stem") != expected[0]
                or row.get("branch") != expected[1]
                or row.get("ten_god_relative_to_natal_day_stem")
                   != ten_god(natal_day_master, expected[0])
                or any(row.get(key) is not None for key in
                       ("start_date", "end_date", "start_age", "end_age",
                        "luck_assessment", "natal_interaction"))):
            raise ValueError("Dayun candidates do not match measured month/direction/Ten Gods")
    age = Fraction(elapsed, THREE_DAYS_SECONDS)
    offset = age * GREGORIAN_MEAN_YEAR_SECONDS
    first = birth_utc + timedelta(seconds=_half_up_fraction(offset))
    period_seconds = DAYUN_NOMINAL_YEARS * GREGORIAN_MEAN_YEAR_SECONDS
    timeline = []
    for i, row in enumerate(rows):
        start = first + timedelta(seconds=i * period_seconds)
        end = start + timedelta(seconds=period_seconds)
        timeline.append({
            "period_index": i + 1,
            "candidate_ganzhi": row["candidate_ganzhi"],
            "ten_god_relative_to_natal_day_stem": row["ten_god_relative_to_natal_day_stem"],
            "simulated_start": start.astimezone(CHINA).isoformat(),
            "simulated_end_exclusive": end.astimezone(CHINA).isoformat(),
            "is_verified_handover_date": False,
            "luck_assessment": None,
        })
    return {
        "variant": VARIANT,
        "reference_technique": "three_days_per_one_year",
        "technique_review_status": "unreviewed_original_variant",
        "elapsed_seconds": elapsed,
        "measured_jie_arithmetic_verified": True,
        "candidate_sequence_crosschecked": True,
        "provider_boundary_independently_verified": False,
        "age_years_exact": {
            "numerator": age.numerator,
            "denominator": age.denominator,
        },
        "age_years_decimal_6_places": str((Decimal(age.numerator) / Decimal(age.denominator)).quantize(
            Decimal("0.000001"), rounding=ROUND_HALF_UP)),
        "mean_gregorian_year_seconds": GREGORIAN_MEAN_YEAR_SECONDS,
        "nominal_cycle_years": DAYUN_NOMINAL_YEARS,
        "simulated_first_offset_seconds": _half_up_fraction(offset),
        "rounding": "rational_fraction_to_nearest_second_half_up",
        "simulation_basis": "3 Jie-distance days per one symbolic year, mapped to exact Gregorian mean year (365.2425 days); every next nominal cycle is 10 mean years",
        "timeline": timeline,
        "actual_start_age_adjudicated": False,
        "verified_handover_dates_calculated": False,
        "birth_direction_inferred": False,
        "astronomical_precision_independently_verified": False,
        "classical_method_reviewed": False,
        "research_only": True,
        "public_enabled": False,
        "ai_enabled": False,
        "scope": "近似数学模拟，不是古法已审核交运日期、虚实岁裁定、十年实历分段或事业财运断语。",
    }
