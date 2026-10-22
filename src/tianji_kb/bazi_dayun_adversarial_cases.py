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

IDENTITY BINDING (remediation):
- Each fixed case (ADV-001..ADV-012) binds its identity: case_id,
  birth_instant, direction, variant_id. Caller overrides are strictly
  validated — a supplied value that disagrees with the registered value is
  REJECTED, never silently replaced (no `or`-fallback, no empty-string
  substitution).
- Ad-hoc research at arbitrary instants uses the separate
  evaluate_custom_probe() entry and never reuses a fixed ADV identity.
- evaluate_boundary_conflict() first verifies from the pinned provider
  that the input is EXACTLY a Jie instant; anything else is rejected as
  boundary impersonation.

EXECUTION CATEGORIES (every case has a real callable verification path):
- "measurement": real audit -> jie measurement -> exact ratio -> variant.
- "refusal": age-counting refusal; the refusal itself is executed and its
  error category verified.
- "tz_fail_closed": audit_birth_instant must raise with the expected
  trigger; the trigger text is verified, never catch-all PASS.

Reuses (never reimplements): bazi_dayun_jie.adjacent_jie_distance,
bazi_dayun_age_fraction.exact_three_day_ratio,
bazi_dayun_conversion_variants.convert_with_variant / research_convert,
bazi_calendar_precision_audit.audit_birth_instant, and the Phase4-frozen
calendar.py (untouched).
"""

from datetime import datetime
from zoneinfo import ZoneInfo

from .bazi_calendar_precision_audit import audit_birth_instant
from .bazi_dayun_age_fraction import exact_three_day_ratio
from .bazi_dayun_conversion_variants import (
    convert_with_variant,
    get_variant,
    research_convert,
)
from .bazi_dayun_jie import adjacent_jie_distance
from .calendar import calendar

_UNSET = object()  # sentinel: distinguishes "not supplied" from None/""


# Canonical adversarial probes. birth_instant values are real instants
# verified against the pinned provider (lunar-python==1.4.8); the comments
# record the ACTUAL measured behaviour, not assumptions.
_ADVERSARIAL_CASES = (
    {
        "case_id": "ADV-001",
        "title": "birth exactly at the Jie instant, backward direction",
        "execution_category": "measurement",
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
        "execution_category": "measurement",
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
        "execution_category": "measurement",
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
        "execution_category": "measurement",
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
        "execution_category": "measurement",
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
        "execution_category": "measurement",
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
        "execution_category": "measurement",
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
        "execution_category": "refusal",
        "birth_instant": None,
        "timezone": "Asia/Shanghai",
        "direction": None,
        "variant_id": None,
        "refusal_args": ("xusui", "shisui"),
        "error_must_contain": "no sealed-canon",
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
        "execution_category": "refusal",
        "birth_instant": None,
        "timezone": "Asia/Shanghai",
        "direction": None,
        "variant_id": None,
        "refusal_args": ("lichun-based", "chunjie-based"),
        "error_must_contain": "no sealed-canon",
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
        "execution_category": "tz_fail_closed",
        "birth_instant": "1986-05-04T02:30:00+08:00",
        "probe_kind": "iso",
        "timezone": "Asia/Shanghai",
        "direction": None,
        "variant_id": None,
        "error_must_contain": "does not exist",
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
        "execution_category": "tz_fail_closed",
        "birth_instant": "1986-09-14T01:30:00",
        "probe_kind": "named_zone",
        "timezone": "Asia/Shanghai",
        "direction": None,
        "variant_id": None,
        "error_must_contain": "silent guess",
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
        "execution_category": "tz_fail_closed",
        "birth_instant": "1988-07-01T12:00:00+08:00",
        "probe_kind": "iso",
        "timezone": "Asia/Shanghai",
        "direction": None,
        "variant_id": None,
        "error_must_contain": "contradicts tzdb",
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


def _resolve_identity_field(case_id, field, registered, supplied):
    """Strict identity binding for fixed cases.

    - Not supplied (_UNSET): the registered value is used; a case with no
      registered value for this field cannot be evaluated on the
      measurement path.
    - Supplied: must be a non-empty string and, when the case registers a
      value, must equal it. Anything else is REJECTED — never silently
      replaced via `or`-fallback.
    """
    if supplied is _UNSET:
        if registered is None:
            raise ValueError(
                "case %r registers no %s; measurement evaluation is not "
                "applicable (use execute_adversarial_case for the case's "
                "own execution category)" % (case_id, field))
        return registered
    if not isinstance(supplied, str) or not supplied:
        raise ValueError(
            "case %r: invalid override for %s (%r); refusing silent "
            "fallback to the registered value" % (case_id, field, supplied))
    if registered is not None and supplied != registered:
        raise ValueError(
            "case %r: %s override %r disagrees with the registered %r; "
            "fixed case identity must stay consistent" % (
                case_id, field, supplied, registered))
    return supplied


def _verified_status_from_arithmetic(ratio, evidence_bound):
    """Derive the actual status from the computed arithmetic fact."""
    if ratio["zero_distance"]:
        return "unresolved"
    if ratio["elapsed_seconds"] % 259200 != 0:
        return "unresolved"
    return "unresolved"  # exact multiples still lack a classical age rule


def evaluate_adversarial_case(case_id, *, birth_instant=_UNSET,
                              direction=_UNSET, variant_id=_UNSET,
                              evidence_bundle=None, expected_source_refs=None,
                              tz_name="Asia/Shanghai"):
    """Evaluate one measurement-category adversarial case.

    Identity is strictly bound: birth_instant, direction and variant_id
    must match the registered case (or be omitted). Overrides that
    disagree are rejected, never silently replaced.

    source_refs in the result come ONLY from actually-verified Evidence
    (the bound bundle). Unbound arithmetic explicitly reports
    evidence_bound=False with empty source_refs and never claims verified
    classical sources. If expected_source_refs is supplied and the bound
    evidence's source IDs disagree, evaluation is rejected.
    """
    case = get_adversarial_case(case_id)
    if case["execution_category"] != "measurement":
        raise ValueError(
            "case %r is a %r case, not a measurement case; use "
            "execute_adversarial_case() for its own execution category"
            % (case_id, case["execution_category"]))
    birth = _resolve_identity_field(
        case_id, "birth_instant", case["birth_instant"], birth_instant)
    d = _resolve_identity_field(
        case_id, "direction", case["direction"], direction)
    vid = _resolve_identity_field(
        case_id, "variant_id", case["variant_id"], variant_id)
    if d not in ("forward", "backward"):
        raise ValueError(
            "case %r requires an explicit forward/backward direction" % (case_id,))
    get_variant(vid)  # fail closed on unknown variant IDs
    # 1. Civil-time truth, fail-closed.
    audited = audit_birth_instant(birth, tz_name=tz_name)
    # 2. Real jie measurement (provider replay gate inside).
    measured = adjacent_jie_distance(
        birth, d,
        expected_month_ganzhi=calendar(birth)["month_ganzhi"])
    # 3. Exact arithmetic (zero distance -> unreviewed, never age zero).
    ratio = exact_three_day_ratio(measured)
    # 4. Variant conversion: unbound by default; bound only with real evidence.
    bound_source_ids = []
    if evidence_bundle is not None:
        converted = research_convert(
            variant_id=vid, measured_jie=measured,
            evidence_bundle=evidence_bundle)
        for bound in converted["evidence_binding"]["evidence_bound"]:
            bound_source_ids.append(bound["source_id"])
        if expected_source_refs is not None and (
                set(bound_source_ids) != set(expected_source_refs)):
            raise ValueError(
                "case %r: bound evidence source IDs %r disagree with the "
                "expected %r; source tracing is rejected"
                % (case_id, bound_source_ids, expected_source_refs))
    else:
        converted = convert_with_variant(vid, measured)
    evidence_bound = converted.get("evidence_bound", False)
    verified_status = _verified_status_from_arithmetic(ratio, evidence_bound)
    result = {
        "case_id": case_id,
        "execution_category": "measurement",
        "birth_instant": birth,
        "timezone": tz_name,
        "utc_instant": audited["utc_instant"],
        "civil_classification": audited["civil_classification"],
        "jie_boundary": {
            "name": measured["selected_jie"]["name"],
            "at": measured["selected_jie"]["at"],
        },
        "direction": d,
        "variant_id": vid,
        "arithmetic_fact": {
            "elapsed_seconds": ratio["elapsed_seconds"],
            "zero_distance": ratio["zero_distance"],
            "symbolic_three_day_year_ratio":
                ratio["symbolic_three_day_year_ratio"],
            "age_conversion_status": ratio["age_conversion_status"],
        },
        # Source tracing: ONLY from actually-verified Evidence.
        "source_refs": bound_source_ids,
        "evidence_bound": evidence_bound,
        "disputed_convention": case["disputed_convention"],
        "expected_status": case["expected_status"],
        "verified_status": verified_status,
        "status_consistent": verified_status == case["expected_status"],
        "unresolved_reason": case["unresolved_reason"],
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


def _verify_error_category(case, error):
    """The caught error must match the case's expected trigger.

    A mismatched error is re-raised: errors are never catch-all marked PASS.
    """
    must_contain = case.get("error_must_contain", "")
    if must_contain and must_contain not in str(error):
        raise ValueError(
            "case %r raised an unexpected error category: %r does not "
            "contain the expected trigger %r"
            % (case["case_id"], str(error)[:120], must_contain)) from error


def _execute_refusal_case(case):
    """Execute an age-counting refusal case; the refusal IS the execution."""
    try:
        refuse_age_counting_conversion(*case["refusal_args"])
    except ValueError as error:
        _verify_error_category(case, error)
        return {
            "case_id": case["case_id"],
            "execution_category": "refusal",
            "birth_instant": None,
            "timezone": case["timezone"],
            "direction": None,
            "variant_id": None,
            "arithmetic_fact": None,
            "source_refs": [],
            "evidence_bound": False,
            "disputed_convention": case["disputed_convention"],
            "expected_status": "refused",
            "verified_status": "refused",
            "status_consistent": True,
            "error_category": "age_counting_refused",
            "trigger": str(error)[:200],
            "unresolved_reason": case["unresolved_reason"],
            "start_age": None,
            "handover_datetime": None,
            "research_only": True,
            "public_enabled": False,
            "ai_enabled": False,
        }
    raise ValueError(
        "case %r did NOT refuse as required; silent pass is forbidden"
        % (case["case_id"],))


def _execute_tz_case(case, *, tz_name="Asia/Shanghai"):
    """Execute a timezone fail-closed case; the rejection IS the execution."""
    probe = case["birth_instant"]
    if case.get("probe_kind") == "named_zone":
        naive = datetime.fromisoformat(probe)
        probe = naive.replace(tzinfo=ZoneInfo(case["timezone"]))
    try:
        audit_birth_instant(probe, tz_name=tz_name)
    except ValueError as error:
        _verify_error_category(case, error)
        return {
            "case_id": case["case_id"],
            "execution_category": "tz_fail_closed",
            "birth_instant": case["birth_instant"],
            "timezone": case["timezone"],
            "direction": None,
            "variant_id": None,
            "arithmetic_fact": None,
            "source_refs": [],
            "evidence_bound": False,
            "disputed_convention": case["disputed_convention"],
            "expected_status": "fail_closed",
            "verified_status": "fail_closed",
            "status_consistent": True,
            "error_category": "tz_fail_closed",
            "trigger": str(error)[:200],
            "unresolved_reason": case["unresolved_reason"],
            "start_age": None,
            "handover_datetime": None,
            "research_only": True,
            "public_enabled": False,
            "ai_enabled": False,
        }
    raise ValueError(
        "case %r did NOT fail closed as required; silent pass is forbidden"
        % (case["case_id"],))


def execute_adversarial_case(case_id, **kwargs):
    """Unified entry: every one of the 12 cases has a real callable path.

    Dispatches on the case's execution_category and returns a structured,
    honestly-labeled result. Measurement cases accept the strict identity
    overrides of evaluate_adversarial_case(); refusal/tz cases take no
    measurement parameters.
    """
    case = get_adversarial_case(case_id)
    category = case["execution_category"]
    if category == "measurement":
        return evaluate_adversarial_case(case_id, **kwargs)
    if kwargs:
        raise ValueError(
            "case %r is a %r case and takes no measurement parameters"
            % (case_id, category))
    if category == "refusal":
        return _execute_refusal_case(case)
    if category == "tz_fail_closed":
        return _execute_tz_case(case)
    raise ValueError("unknown execution category %r" % (category,))


def evaluate_custom_probe(*, birth_instant, direction, variant_id,
                          tz_name="Asia/Shanghai"):
    """Ad-hoc research probe at an arbitrary instant.

    This entry does NOT reuse any fixed ADV case identity: it carries no
    case_id, no registered dispute text, and no expected_status. Use it
    for arbitrary-time research instead of overriding a fixed case.
    """
    if not isinstance(birth_instant, str) or not birth_instant:
        raise ValueError("birth_instant is required")
    if direction not in ("forward", "backward"):
        raise ValueError("direction must be forward or backward")
    get_variant(variant_id)
    audited = audit_birth_instant(birth_instant, tz_name=tz_name)
    measured = adjacent_jie_distance(
        birth_instant, direction,
        expected_month_ganzhi=calendar(birth_instant)["month_ganzhi"])
    ratio = exact_three_day_ratio(measured)
    converted = convert_with_variant(variant_id, measured)
    return {
        "entry": "custom_probe",
        "case_id": None,
        "birth_instant": birth_instant,
        "timezone": tz_name,
        "utc_instant": audited["utc_instant"],
        "jie_boundary": {
            "name": measured["selected_jie"]["name"],
            "at": measured["selected_jie"]["at"],
        },
        "direction": direction,
        "variant_id": variant_id,
        "arithmetic_fact": {
            "elapsed_seconds": ratio["elapsed_seconds"],
            "zero_distance": ratio["zero_distance"],
            "symbolic_three_day_year_ratio":
                ratio["symbolic_three_day_year_ratio"],
            "age_conversion_status": ratio["age_conversion_status"],
        },
        "source_refs": [],
        "evidence_bound": False,
        "expected_status": None,
        "verified_status": _verified_status_from_arithmetic(
            ratio, converted.get("evidence_bound", False)),
        "start_age": None,
        "handover_datetime": None,
        "research_only": True,
        "public_enabled": False,
        "ai_enabled": False,
    }


def _is_exact_jie_instant(birth_instant, *, tz_name="Asia/Shanghai"):
    """Verify from the pinned provider that the instant is exactly a Jie.

    Returns the matched jie (name, at) or None. The adjacent measurement's
    previous/next jie instants come from the pinned lunar-python==1.4.8
    provider (provider_identity enforced inside adjacent_jie_distance).
    """
    birth_dt = datetime.fromisoformat(birth_instant)
    measured = adjacent_jie_distance(
        birth_instant, "forward",
        expected_month_ganzhi=calendar(birth_instant)["month_ganzhi"])
    for key in ("previous_jie", "next_jie"):
        jie = measured[key]
        if birth_dt == datetime.fromisoformat(jie["at"]):
            return {"name": jie["name"], "at": jie["at"]}
    return None


def evaluate_boundary_conflict(*, birth_instant, tz_name="Asia/Shanghai",
                               variant_id="classical-three-day-symbolic-ratio-v1"):
    """Evaluate forward AND backward at one TRUE Jie instant.

    Identity is strictly verified FIRST: the input must be exactly a Jie
    instant per the pinned provider, otherwise boundary-conflict semantics
    are refused (no impersonation by ordinary birth times). Both directions
    are computed separately and kept; no merged conclusion is produced and
    zero distance stays unresolved, never age zero.
    """
    if not isinstance(birth_instant, str) or not birth_instant:
        raise ValueError("birth_instant is required")
    get_variant(variant_id)  # fail closed on unknown variant IDs
    audited = audit_birth_instant(birth_instant, tz_name=tz_name)
    matched = _is_exact_jie_instant(birth_instant, tz_name=tz_name)
    if matched is None:
        raise ValueError(
            "birth_instant %r is not exactly a Jie instant per the pinned "
            "provider; boundary-conflict semantics are refused (no "
            "impersonation)" % (birth_instant,))
    # Ad-hoc probes: a verified Jie instant is not necessarily the
    # registered 立春 probe, so the fixed ADV-001/ADV-002 identities are
    # not reused here (identity binding forbids it).
    forward = evaluate_custom_probe(
        birth_instant=birth_instant, direction="forward",
        variant_id=variant_id, tz_name=tz_name)
    backward = evaluate_custom_probe(
        birth_instant=birth_instant, direction="backward",
        variant_id=variant_id, tz_name=tz_name)
    if not backward["arithmetic_fact"]["zero_distance"]:
        raise ValueError(
            "backward measurement at the verified Jie instant is not zero "
            "distance; refusing to manufacture a conflict")
    return {
        "birth_instant": birth_instant,
        "verified_jie": matched,
        "utc_instant": audited["utc_instant"],
        "forward": forward,
        "backward": backward,
        "merged_conclusion": None,
        "conflict_status": "unresolved",
        "conflict_reason": (
            "verified Jie instant %s (%s): forward selects %s (%ss), "
            "backward is zero distance; directional fork at the boundary is "
            "recorded, not merged; zero distance stays unresolved, never "
            "age zero" % (
                matched["name"], matched["at"],
                forward["jie_boundary"]["name"],
                forward["arithmetic_fact"]["elapsed_seconds"])),
        "start_age": None,
        "handover_datetime": None,
        "research_only": True,
        "public_enabled": False,
        "ai_enabled": False,
    }
