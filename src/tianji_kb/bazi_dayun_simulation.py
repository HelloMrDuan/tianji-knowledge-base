"""Opt-in research-only *simulation* of three-days-per-year Dayun conversion.

Classical rule and calendar-year interpolation have NOT been adjudicated into
Canonical Phase2. These arithmetic candidates must not become dated Dayun facts.
"""
from datetime import datetime, timedelta, timezone
from decimal import Decimal, ROUND_HALF_UP
from fractions import Fraction
from zoneinfo import ZoneInfo

from .foundations import CYCLE

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


def simulate_dayun_age_and_timeline(birth_iso, measured_jie, rows):
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
    if type(elapsed) is not int or elapsed <= 0 or elapsed > 40 * 86400:
        # Zero-distance resolution remains a separate classical convention.
        raise ValueError("Zero or invalid Jie distance has unresolved start-age handling")
    if not isinstance(rows, list) or not 1 <= len(rows) <= 12:
        raise ValueError("Expected 1..12 deterministic Dayun candidate rows")
    try:
        birth = datetime.fromisoformat(birth_iso)
    except (TypeError, ValueError) as error:
        raise ValueError("Expected local timezone-aware whole-second birth") from error
    if birth.tzinfo is None or birth.utcoffset() is None or birth.microsecond:
        raise ValueError("Expected local timezone-aware whole-second birth")
    age = Fraction(elapsed, THREE_DAYS_SECONDS)
    offset = age * GREGORIAN_MEAN_YEAR_SECONDS
    first = birth.astimezone(timezone.utc) + timedelta(seconds=_half_up_fraction(offset))
    period_seconds = DAYUN_NOMINAL_YEARS * GREGORIAN_MEAN_YEAR_SECONDS
    expected_ganzhi = [r.get("candidate_ganzhi") for r in rows]
    if len(set(expected_ganzhi)) != len(rows) or any(
        type(r.get("period_index")) is not int or r["period_index"] != i + 1
        or r.get("candidate_ganzhi") not in CYCLE
        or r.get("start_date") is not None or r.get("end_date") is not None
        for i, r in enumerate(rows)
    ):
        raise ValueError("Simulation cannot transform unverified or dated candidate rows")
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
