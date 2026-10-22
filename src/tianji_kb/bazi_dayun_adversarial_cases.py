"""TJ-016.2: adversarial boundary cases for dayun research.

This is NOT a formal handover-date algorithm. It is a registry of the
hardest boundary cases — the instants most likely to be mis-computed by an
algorithm that silently fills gaps — each evaluated with REAL measurements
(pinned provider replay, exact Fraction arithmetic) and an explicit status.

HARD RULES (WBS TJ-016.2):
- A birth exactly at a Jie instant NEVER defaults the start age to zero.
  Zero distance returns `zero_jie_boundary_convention_unreviewed`.
- 虚岁 / 实岁 are never interconverted and never defaulted to one counting
  rule: there is no classical adjudication, so conversion is refused.
- Conflicting evidence / directions are recorded side by side, never merged
  into a single conclusion.
- Every case ends in `unresolved` (or fail-closed rejection) where no
  classical adjudication exists. No formal start age, no handover date,
  ever.

Reuses (never reimplements): bazi_dayun_jie.adjacent_jie_distance,
bazi_dayun_age_fraction.exact_three_day_ratio,
bazi_dayun_conversion_variants.convert_with_variant / research_convert,
bazi_calendar_precision_audit.audit_birth_instant, and the Phase4-frozen
calendar.py (untouched).
"""

from .bazi_calendar_precision_audit import audit_birth_instant
from .bazi_dayun_age_fraction import exact_three_day_ratio
from .bazi_dayun_conversion_variants import convert_with_variant, research_convert
from .bazi_dayun_jie import adjacent_jie_distance
from .calendar import calendar

# Canonical adversarial probes. birth_instant values are real instants
# verified against the pinned provider (lunar-python==1.4.8); the comments
# record the ACTUAL measured behaviour, not assumptions.
_ADVERSARIAL_CASES = (
    {
        "case_id": "ADV-001",
        "title": "birth exactly at the Jie instant, backward direction",
        "birth_instant": "2000-02-04T20:40:24+08:00",  # 立春
        "timezone": "Asia/Shanghai",
        "direction": "backward",
        "variant_id": "classical-three-day-symbolic-ratio-v1",
        # Real behaviour: previous Jie <= birth < next Jie selects 立春 as
        # previous_jie; elapsed == 0; zero_distance == True.
        "disputed_convention": "节令当秒是否自动将起运年龄设为零",
        "expected_status": "unresolved",
        "unresolved_reason": (
            "zero jie distance convention is unreviewed; "
            "age_conversion_status=zero_jie_boundary_convention_unreviewed; "
            "must NOT default the start age to zero"),
        "source_refs": [],
    },
    {
        "case_id": "ADV-002",
        "title": "birth exactly at the Jie instant, forward direction",
        "birth_instant": "2000-02-04T20:40:24+08:00",  # 立春
        "timezone": "Asia/Shanghai",
        "direction": "forward",
        "variant_id": "classical-three-day-symbolic-ratio-v1",
        # Real behaviour: forward from 立春 selects 惊蛰, elapsed=2570536s.
        # Same instant as ADV-001, different direction, different jie:
        # direction is a real fork, not a merged conclusion.
        "disputed_convention": "同一节界顺行与逆行的不同处理",
        "expected_status": "unresolved",
        "unresolved_reason": (
            "remainder 2570536 % 259200 != 0 has no classical remainder rule; "
            "direction fork at the boundary is recorded, not merged"),
        "source_refs": [],
    },
    {
        "case_id": "ADV-003",
        "title": "one second before the Jie instant, forward",
        "birth_instant": "2000-02-04T20:40:23+08:00",
        "timezone": "Asia/Shanghai",
        "direction": "forward",
        "variant_id": "classical-three-day-symbolic-ratio-v1",
        # Real behaviour: elapsed=1s to 立春; ratio 1/259200.
        "disputed_convention": "不足一日的余数（秒级）",
        "expected_status": "unresolved",
        "unresolved_reason": "the sealed text gives no remainder rule",
        "source_refs": [],
    },
    {
        "case_id": "ADV-004",
        "title": "one second after the Jie instant, backward",
        "birth_instant": "2000-02-04T20:40:25+08:00",
        "timezone": "Asia/Shanghai",
        "direction": "backward",
        "variant_id": "classical-three-day-symbolic-ratio-v1",
        # Real behaviour: elapsed=1s to 立春; ratio 1/259200.
        "disputed_convention": "不足一日的余数（秒级）",
        "expected_status": "unresolved",
        "unresolved_reason": "the sealed text gives no remainder rule",
        "source_refs": [],
    },
    {
        "case_id": "ADV-005",
        "title": "one second before the Jie instant, backward",
        "birth_instant": "2000-02-04T20:40:23+08:00",
        "timezone": "Asia/Shanghai",
        "direction": "backward",
        "variant_id": "classical-three-day-symbolic-ratio-v1",
        # Real behaviour: elapsed=2547581s to 小寒. Same instant as ADV-003,
        # different direction selects a different jie: conflict recorded.
        "disputed_convention": "同一时刻顺逆选择不同节令的冲突",
        "expected_status": "unresolved",
        "unresolved_reason": (
            "direction selects a different jie (小寒 vs 立春); "
            "conflicting selections are recorded side by side, never merged; "
            "no classical remainder rule"),
        "source_refs": [],
    },
    {
        "case_id": "ADV-006",
        "title": "sub-day remainder (12 hours before Jie)",
        "birth_instant": "2000-02-04T08:40:24+08:00",
        "timezone": "Asia/Shanghai",
        "direction": "forward",
        "variant_id": "classical-three-day-symbolic-ratio-v1",
        # Real behaviour: elapsed=43200s; ratio 1/6.
        "disputed_convention": "不足一日的余数（半日）",
        "expected_status": "unresolved",
        "unresolved_reason": "the sealed text gives no remainder rule",
        "source_refs": [],
    },
    {
        "case_id": "ADV-007",
        "title": "sub-shichen remainder (1 hour before Jie; 1 时辰 = 2h)",
        "birth_instant": "2000-02-04T19:40:24+08:00",
        "timezone": "Asia/Shanghai",
        "direction": "forward",
        "variant_id": "classical-three-day-symbolic-ratio-v1",
        # Real behaviour: elapsed=3600s; ratio 1/72.
        "disputed_convention": "不足一时辰的余数",
        "expected_status": "unresolved",
        "unresolved_reason": (
            "the sealed text gives no remainder rule; no classical "
            "sub-shichen carry rule exists"),
        "source_refs": [],
    },
    {
        "case_id": "ADV-008",
        "title": "xusui to shisui conversion is refused",
        "birth_instant": None,
        "timezone": "Asia/Shanghai",
        "direction": None,
        "variant_id": None,
        "disputed_convention": "虚岁与实岁的不同计数口径",
        "expected_status": "refused",
        "unresolved_reason": (
            "no classical adjudication for age-counting conversion; "
            "xusui and shisui must not be defaulted to one rule or "
            "interconverted without evidence"),
        "source_refs": [],
    },
    {
        "case_id": "ADV-009",
        "title": "civil age-expression confusion (立春 vs 春节 vs 公历新年)",
        "birth_instant": None,
        "timezone": "Asia/Shanghai",
        "direction": None,
        "variant_id": None,
        "disputed_convention": "跨公历新年、春节及立春时年龄表述的混淆",
        "expected_status": "refused",
        "unresolved_reason": (
            "no sealed-canon adjudication maps civil age expressions to a "
            "dayun start age; any such mapping is refused"),
        "source_refs": [],
    },
    {
        "case_id": "ADV-010",
        "title": "nonexistent civil time (1986 DST gap)",
        "birth_instant": "1986-05-04T02:30:00+08:00",
        "timezone": "Asia/Shanghai",
        "direction": None,
        "variant_id": None,
        "disputed_convention": "历史时区缺失时刻",
        "expected_status": "fail_closed",
        "unresolved_reason": (
            "civil time does not exist in tzdb (DST transition gap); "
            "refusing to guess a UTC instant"),
        "source_refs": [],
    },
    {
        "case_id": "ADV-011",
        "title": "ambiguous civil time with named zone (1986 fall-back)",
        "birth_instant": "1986-09-14T01:30:00",
        "timezone": "Asia/Shanghai",
        "direction": None,
        "variant_id": None,
        "disputed_convention": "历史时区重复时刻的隐式 fold",
        "expected_status": "fail_closed",
        "unresolved_reason": (
            "ambiguous civil time with a named zone input; "
            "fold would be a silent guess"),
        "source_refs": [],
    },
    {
        "case_id": "ADV-012",
        "title": "wrong historical UTC offset",
        "birth_instant": "1988-07-01T12:00:00+08:00",
        "timezone": "Asia/Shanghai",
        "direction": None,
        "variant_id": None,
        "disputed_convention": "历史偏移误用",
        "expected_status": "fail_closed",
        "unresolved_reason": (
            "claimed UTC offset contradicts tzdb for the civil time "
            "(1988-07-01 was +09:00); historical offset misuse is rejected"),
        "source_refs": [],
    },
)

_CASES_BY_ID = {c["case_id"]: c for c in _ADVERSARIAL_CASES}

_REQUIRED_FIELDS = ("case_id", "birth_instant", "timezone", "jie_boundary",
                    "direction", "variant_id", "arithmetic_fact", "source_refs",
                    "disputed_convention", "expected_status",
                    "unresolved_reason")


def list_adversarial_cases():
    """Return the adversarial case registry (metadata only)."""
    return [dict(c, source_refs=list(c["source_refs"]))
            for c in _ADVERSARIAL_CASES]


def get_adversarial_case(case_id):
    """Fetch one adversarial case; fail closed on unknown IDs."""
    try:
        case = _CASES_BY_ID[case_id]
    except KeyError:
        raise ValueError("unknown adversarial case %r" % (case_id,))
    return dict(case, source_refs=list(case["source_refs"]))


def refuse_age_counting_conversion(from_system, to_system):
    """Refuse xusui/shisui interconversion.

    There is no classical adjudication for age-counting conversion, so the
    two systems must not be defaulted to one rule or converted into each
    other. Always fail closed.
    """
    raise ValueError(
        "age-counting conversion %r -> %r is refused: no sealed-canon "
        "adjudication exists; xusui and shisui must not be defaulted to one "
        "counting rule" % (from_system, to_system))


def evaluate_adversarial_case(case_id, *, birth_instant=None, direction=None,
                              variant_id="classical-three-day-symbolic-ratio-v1",
                              evidence_bundle=None,
                              tz_name="Asia/Shanghai"):
    """Evaluate one adversarial case with real measurements.

    Pipeline (all real, all reused):
    1. audit_birth_instant: civil-time validation, fail-closed on
       nonexistent / ambiguous / wrong-offset instants.
    2. adjacent_jie_distance: pinned-provider jie measurement with the
       provider replay gate.
    3. exact_three_day_ratio: exact Fraction arithmetic; zero distance
       yields zero_jie_boundary_convention_unreviewed, never age zero.
    4. convert_with_variant (unbound) or research_convert (bound, only
       with a real evidence_bundle for classical variants).

    The returned result carries every required field and never contains a
    formal start age or handover datetime.
    """
    case = get_adversarial_case(case_id)
    birth = birth_instant or case["birth_instant"]
    if birth is None:
        raise ValueError(
            "case %r carries no birth instant; it documents a refusal "
            "(use refuse_age_counting_conversion or audit_birth_instant "
            "directly)" % (case_id,))
    d = direction or case["direction"]
    if d not in ("forward", "backward"):
        raise ValueError(
            "case %r requires an explicit forward/backward direction" % (case_id,))
    # 1. Civil-time truth, fail-closed.
    audited = audit_birth_instant(birth, tz_name=tz_name)
    # 2. Real jie measurement (provider replay gate inside).
    measured = adjacent_jie_distance(
        birth, d,
        expected_month_ganzhi=calendar(birth)["month_ganzhi"])
    # 3. Exact arithmetic (zero distance -> unreviewed, never age zero).
    ratio = exact_three_day_ratio(measured)
    # 4. Variant conversion: unbound by default; bound only with real evidence.
    if evidence_bundle is not None:
        converted = research_convert(
            variant_id=variant_id, measured_jie=measured,
            evidence_bundle=evidence_bundle)
    else:
        converted = convert_with_variant(variant_id, measured)
    result = {
        "case_id": case_id,
        "birth_instant": birth,
        "timezone": tz_name,
        "utc_instant": audited["utc_instant"],
        "civil_classification": audited["civil_classification"],
        "jie_boundary": {
            "name": measured["selected_jie"]["name"],
            "at": measured["selected_jie"]["at"],
        },
        "direction": d,
        "variant_id": variant_id,
        "arithmetic_fact": {
            "elapsed_seconds": ratio["elapsed_seconds"],
            "zero_distance": ratio["zero_distance"],
            "symbolic_three_day_year_ratio":
                ratio["symbolic_three_day_year_ratio"],
            "age_conversion_status": ratio["age_conversion_status"],
        },
        "source_refs": list(case["source_refs"]),
        "disputed_convention": case["disputed_convention"],
        "expected_status": case["expected_status"],
        "unresolved_reason": case["unresolved_reason"],
        "evidence_bound": converted.get("evidence_bound", False),
        "start_age": None,
        "handover_datetime": None,
        "research_only": True,
        "public_enabled": False,
        "ai_enabled": False,
    }
    for field in _REQUIRED_FIELDS:
        if field not in result:
            raise ValueError("adversarial result missing field %r" % (field,))
    return result


def evaluate_boundary_conflict(*, birth_instant, tz_name="Asia/Shanghai",
                               variant_id="classical-three-day-symbolic-ratio-v1"):
    """Evaluate forward AND backward at one boundary without merging.

    At an exact Jie instant the two directions select different jie with
    different elapsed distances (real fork). Both results are returned side
    by side; no merged conclusion is produced and no age is set.
    """
    forward = evaluate_adversarial_case(
        "ADV-002", birth_instant=birth_instant, direction="forward",
        variant_id=variant_id, tz_name=tz_name)
    backward = evaluate_adversarial_case(
        "ADV-001", birth_instant=birth_instant, direction="backward",
        variant_id=variant_id, tz_name=tz_name)
    return {
        "birth_instant": birth_instant,
        "forward": forward,
        "backward": backward,
        "merged_conclusion": None,
        "conflict_status": "unresolved",
        "conflict_reason": (
            "forward selects %s (%ss), backward selects %s (%ss); "
            "directional fork at the boundary is recorded, not merged; "
            "no classical adjudication" % (
                forward["jie_boundary"]["name"],
                forward["arithmetic_fact"]["elapsed_seconds"],
                backward["jie_boundary"]["name"],
                backward["arithmetic_fact"]["elapsed_seconds"])),
        "start_age": None,
        "handover_datetime": None,
        "research_only": True,
        "public_enabled": False,
        "ai_enabled": False,
    }
