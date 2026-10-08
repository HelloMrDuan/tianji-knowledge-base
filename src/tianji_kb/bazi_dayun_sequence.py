"""Research-only sexagenary sequence adjacent to the natal month pillar.

This module deliberately does NOT implement or approve the traditional
direction-by-sex/year rule, Qi Yun age, Jie-based conversion, or luck readings.
The provenance of the source month pillar and Ten Gods is validated elsewhere;
the use of its adjacent sexagenary cycles *as Dayun* remains unreviewed.
"""
from .bazi_core import ten_god
from .foundations import CYCLE, STEMS, ganzhi_index

VARIANT = "bazi-dayun-month-sequence-research-v1"
MAX_PERIODS = 12


def candidate_sequence(month_ganzhi, day_master, *, direction, periods=8):
    """Explicit-direction candidate cycles, with no invented starting dates."""
    if direction not in ("forward", "backward") or type(direction) is not str:
        raise ValueError("dayun_sequence_direction must be forward or backward")
    if type(periods) is not int or not 1 <= periods <= MAX_PERIODS:
        raise ValueError("dayun_sequence_count must be an integer from 1 to 12")
    if type(day_master) is not str or day_master not in STEMS:
        raise ValueError("Expected a valid natal day stem")
    month_index = ganzhi_index(month_ganzhi)
    sign = 1 if direction == "forward" else -1
    rows = []
    for step in range(1, periods + 1):
        ganzhi = CYCLE[(month_index + sign * step) % 60]
        rows.append({
            "period_index": step,
            "candidate_ganzhi": ganzhi,
            "stem": ganzhi[0],
            "branch": ganzhi[1],
            "ten_god_relative_to_natal_day_stem": ten_god(day_master, ganzhi[0]),
            "start_date": None,
            "end_date": None,
            "start_age": None,
            "end_age": None,
            "natal_interaction": None,
            "luck_assessment": None,
        })
    return {
        "variant": VARIANT,
        "source_month_ganzhi": month_ganzhi,
        "natal_day_master": day_master,
        "direction": direction,
        "direction_origin": "explicit_caller_selection_only",
        "direction_from_natal_attributes_calculated": False,
        "sequence_policy": "60-Jiazi adjacent cycles from natal month pillar; first candidate excludes natal month",
        "dayun_sequence_policy_review_status": "unreviewed",
        "source_fact_ref": "#/trace/0/output/ganzhi/1",
        "source_rule_id": "bazi.phase2.pillars",
        "ten_god_rule_id": "bazi.phase2.ten_gods",
        "classical_evidence_for_dayun_sequence_approved": False,
        "nominal_period_years": 10,
        "nominal_period_years_review_status": "legacy_unreviewed",
        "rows": rows,
        "start_age_calculated": False,
        "handover_dates_calculated": False,
        "birth_datetime_required_for_dated_timeline": True,
        "jie_boundary_method_adjudicated": False,
        "start_age_conversion_adjudicated": False,
        "astronomical_precision_independently_verified": False,
        "research_only": True,
        "public_enabled": False,
        "ai_enabled": False,
        "scope": "月柱相邻六十甲子候选序列和日主十神；顺逆由调用方显式指定且未审核，不计算起运岁数、交运日期、岁运作用或吉凶。"
    }
