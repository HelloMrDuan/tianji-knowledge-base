"""Exact, opt-in symbolic Jie/three-day ratio; NOT an adjudicated start age.

An authenticated pinned-provider distance can support rational arithmetic.
It cannot decide which classical age method, calendar or boundary convention
to use. In particular an exact-Jie birth is NOT silently assigned age zero.
"""
from datetime import datetime, timedelta, timezone
from decimal import Decimal, ROUND_HALF_UP
from fractions import Fraction
from zoneinfo import ZoneInfo

from .bazi_dayun_jie import JIE_NAMES, SECONDS_PER_DAY
from .calendar import PROVIDER
from .foundations import ganzhi_index

VARIANT = "bazi-dayun-exact-three-day-ratio-research-v1"
THREE_DAYS = 3 * SECONDS_PER_DAY
CHINA = ZoneInfo("Asia/Shanghai")


def _utc_second(value):
    if type(value) is not str:
        raise ValueError("Measured Jie timestamps must be ISO seconds")
    try:
        moment = datetime.fromisoformat(value)
    except ValueError as error:
        raise ValueError("Measured Jie timestamps must be ISO seconds") from error
    if moment.tzinfo is None or moment.utcoffset() is None or moment.microsecond:
        raise ValueError("Measured Jie timestamps must be timezone-aware whole seconds")
    return moment.astimezone(timezone.utc)


def exact_three_day_ratio(measure):
    """Return symbolic age *arithmetic*, without any actual Dayun start age."""
    if (type(measure) is not dict or
            measure.get("variant") != "bazi-dayun-adjacent-jie-research-v1" or
            measure.get("calendar_provider") != PROVIDER or
            measure.get("research_only") is not True or
            measure.get("dayun_conversion_rule_review_status") != "unreviewed"):
        raise ValueError("Ratio requires a pinned unreviewed Jie measurement")
    direction = measure.get("direction")
    if type(direction) is not str or direction not in ("forward", "backward"):
        raise ValueError("Ratio requires an explicit direction")
    birth_value = measure.get("birth_local_datetime")
    birth = _utc_second(birth_value)
    if birth.astimezone(CHINA).isoformat() != birth_value:
        raise ValueError("Birth must use pinned Asia/Shanghai time")
    month = measure.get("birth_month_ganzhi")
    if type(month) is not str:
        raise ValueError("Missing source month Ganzhi")
    ganzhi_index(month)

    previous, following, selected = (
        measure.get("previous_jie"), measure.get("next_jie"),
        measure.get("selected_jie"))
    if any(type(row) is not dict or row.get("name") not in JIE_NAMES
           for row in (previous, following, selected)):
        raise ValueError("Invalid adjacent Jie entries")
    prev = _utc_second(previous.get("at"))
    nxt = _utc_second(following.get("at"))
    if not (prev <= birth < nxt and timedelta(0) < nxt-prev <= timedelta(days=40)):
        raise ValueError("Invalid adjacent Jie interval")
    if selected != (following if direction == "forward" else previous):
        raise ValueError("Selected Jie disagrees with direction")
    seconds = measure.get("elapsed_seconds")
    expected = int(((nxt-birth) if direction == "forward" else
                    (birth-prev)).total_seconds())
    if (type(seconds) is not int or seconds != expected or
            measure.get("zero_distance") is not (seconds == 0) or
            type(measure.get("elapsed_whole_days")) is not int or
            type(measure.get("remaining_seconds_after_whole_days")) is not int or
            measure["elapsed_whole_days"] != seconds // SECONDS_PER_DAY or
            measure["remaining_seconds_after_whole_days"] != seconds % SECONDS_PER_DAY):
        raise ValueError("Inconsistent Jie interval arithmetic")

    parts = {"days": seconds // SECONDS_PER_DAY,
             "hours": (seconds % SECONDS_PER_DAY) // 3600,
             "minutes": (seconds % 3600) // 60,
             "seconds": seconds % 60}
    zero = seconds == 0
    fraction = Fraction(seconds, THREE_DAYS) if not zero else None
    return {
        "variant": VARIANT,
        "direction": direction,
        "selected_jie": {"name": selected["name"], "at": selected["at"]},
        "elapsed_seconds": seconds,
        "distance_components": parts,
        "symbolic_three_day_year_ratio": (
            {"numerator": fraction.numerator, "denominator": fraction.denominator}
            if fraction is not None else None),
        "symbolic_ratio_decimal_8_places": (
            str((Decimal(fraction.numerator) / Decimal(fraction.denominator))
                .quantize(Decimal("0.00000001"), rounding=ROUND_HALF_UP))
            if fraction is not None else None),
        "three_days_seconds": THREE_DAYS,
        "zero_distance": zero,
        "age_conversion_status": (
            "zero_jie_boundary_convention_unreviewed" if zero
            else "symbolic_fraction_only_not_adjudicated_start_age"),
        "start_age": None,
        "handover_datetime": None,
        "classical_direction_evidence_approved": False,
        "classical_conversion_method_adjudicated": False,
        "calendar_provider_independently_verified": False,
        "research_only": True,
        "public_enabled": False,
        "ai_enabled": False,
        "scope": "以节气实测秒差除三日的精确数学比值；未审核起运年龄的传统折算、节气零距离约定或真实交运日期。",
    }
