"""Pinned-provider Jie interval facts for optional Dayun *research*.

These are measured time distances, not an approved starting-age convention,
start date, direction inference, or ten-year Dayun timeline.
"""
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

from lunar_python import Solar

from .calendar import PROVIDER, calendar

JIE_NAMES = frozenset(("立春", "惊蛰", "清明", "立夏", "芒种", "小暑",
                       "立秋", "白露", "寒露", "立冬", "大雪", "小寒"))
CHINA = ZoneInfo("Asia/Shanghai")
SECONDS_PER_DAY = 24 * 60 * 60


def _term(term):
    if term is None or term.getName() not in JIE_NAMES:
        raise ValueError("Pinned calendar did not return one of the twelve Jie")
    solar = term.getSolar()
    instant = datetime.strptime(solar.toYmdHms(), "%Y-%m-%d %H:%M:%S").replace(tzinfo=CHINA)
    return {"name": term.getName(), "at": instant.isoformat(), "instant": instant}


def adjacent_jie_distance(value, direction, *, expected_month_ganzhi):
    """Measure exact elapsed seconds between a birth and adjacent 12 Jie.

    The birth timestamp is mandatory. Manual four pillars, calendar dates
    without offset, sub-second times, and provider disputes are rejected.
    """
    if type(direction) is not str or direction not in ("forward", "backward"):
        raise ValueError("Explicit forward/backward Dayun research direction required")
    if type(value) is str:
        try:
            birth = datetime.fromisoformat(value)
        except ValueError as exc:
            raise ValueError("Expected timezone-aware birth ISO datetime") from exc
    elif type(value) is datetime:
        birth = value
    else:
        raise ValueError("Expected timezone-aware birth ISO datetime")
    if birth.tzinfo is None or birth.utcoffset() is None or birth.microsecond != 0:
        raise ValueError("Birth must be timezone-aware at whole-second precision")
    local = birth.astimezone(CHINA)
    # Prevent adjacent boundary verification from crossing the existing
    # pinned 1900..2099 runtime calendar validation envelope.
    if not 1901 <= local.year <= 2098:
        raise ValueError("Adjacent Jie research birth range is 1901..2098")
    cal = calendar(local)
    if cal["month_ganzhi"] != expected_month_ganzhi:
        raise ValueError("Birth-derived month pillar disagrees with chart")
    lunar = Solar.fromYmdHms(local.year, local.month, local.day,
                             local.hour, local.minute, local.second).getLunar()
    prev_jie = _term(lunar.getPrevJie(False))
    next_jie = _term(lunar.getNextJie(False))
    prev_at, next_at = prev_jie.pop("instant"), next_jie.pop("instant")
    if not prev_at <= local < next_at or next_at - prev_at > timedelta(days=40):
        raise ValueError("Pinned provider adjacent Jie chronology invalid")
    # Independent calls to the *same* pinned provider's month-pillar API.
    # They cross-check internal consistency, not astronomical accuracy.
    if (calendar(prev_at - timedelta(seconds=1))["month_ganzhi"] == cal["month_ganzhi"]
            or calendar(prev_at)["month_ganzhi"] != cal["month_ganzhi"]
            or calendar(next_at - timedelta(seconds=1))["month_ganzhi"] != cal["month_ganzhi"]
            or calendar(next_at)["month_ganzhi"] == cal["month_ganzhi"]):
        raise ValueError("Pinned Jie does not match provider's month-pillar boundary")
    # UTC subtraction accounts for historical offset/DST transitions.\n    offset = ((next_at.astimezone(timezone.utc) - local.astimezone(timezone.utc))\n              if direction == "forward" else\n              (local.astimezone(timezone.utc) - prev_at.astimezone(timezone.utc)))
    elapsed_seconds = int(offset.total_seconds())
    if elapsed_seconds < 0:
        raise ValueError("Negative distance to adjacent Jie")
    selected = next_jie if direction == "forward" else prev_jie
    return {
        "variant": "bazi-dayun-adjacent-jie-research-v1",
        "birth_local_datetime": local.isoformat(),
        "birth_month_ganzhi": cal["month_ganzhi"],
        "previous_jie": prev_jie,
        "next_jie": next_jie,
        "selected_jie": selected,
        "direction": direction,
        "direction_origin": "explicit_caller_selection_only",
        "elapsed_seconds": elapsed_seconds,
        "elapsed_whole_days": elapsed_seconds // SECONDS_PER_DAY,
        "remaining_seconds_after_whole_days": elapsed_seconds % SECONDS_PER_DAY,
        "zero_distance": elapsed_seconds == 0,
        "boundary_policy": "previous Jie <= birth < next Jie; provider-second precision",
        "conversion_to_start_age": None,
        "start_age": None,
        "handover_datetime": None,
        "astronomical_precision_independently_verified": False,
        "historical_timezone_independently_verified": False,
        "dayun_conversion_rule_review_status": "unreviewed",
        "calendar_provider": PROVIDER,
        "research_only": True,
        "public_enabled": False,
        "ai_enabled": False,
        "scope": "仅公历出生时间至相邻十二节的真实历法库秒级间隔；不推断顺逆、不折算岁数或交运日期、不预测吉凶。",
    }
