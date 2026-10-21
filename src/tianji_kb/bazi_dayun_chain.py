"""Fact-tracking chain for Dayun candidate sequences (TJ-014.2).

This module does not invent a new Dayun method. It *verifies an existing*
candidate-sequence artefact against its declared sources:

  natal pillars (real Trace)  ->  month pillar resolved by rule_id
                             ->  direction from one explicit source only
                             ->  60-cycle candidate rows recomputed independently
                             ->  ten gods recomputed against the natal day stem
                             ->  research evidence boundary restated

Every link is checked by value; any mismatch, missing Trace step, dangling
Evidence reference, forged direction candidate, or promoted research flag
raises ValueError. The chain never approves the Dayun method itself: the
direction rule remains a B-class modern restoration candidate and the
sequence stays research_only / unreviewed.
"""
from .bazi_core import ten_god
from .bazi_dayun_direction import (
    VARIANT as DAYUN_DIRECTION_VARIANT,
    validate_direction_candidate,
)
from .foundations import CYCLE, ganzhi_index

CHAIN_VARIANT = "bazi-dayun-fact-chain-v1"
PILLARS_RULE_ID = "bazi.phase2.pillars"
TEN_GODS_RULE_ID = "bazi.phase2.ten_gods"


def _fail(message):
    raise ValueError("Dayun fact chain rejected: " + message)


def _resolve_pillars_step(trace):
    """Find the real pillars Trace step by rule_id, never by fixed index."""
    if not isinstance(trace, list):
        _fail("trace is not a list")
    for index, step in enumerate(trace):
        if isinstance(step, dict) and step.get("rule_id") == PILLARS_RULE_ID:
            return index, step
    _fail("trace has no %s step" % PILLARS_RULE_ID)


def build_dayun_candidate_chain(chart_output, sequence_result, *,
                                direction, traditional_role=None,
                                direction_candidate=None, periods=None):
    """Verify a candidate-sequence artefact against its declared sources.

    chart_output: full bazi chart output dict with 'trace' (list) and
        'evidence' (dict).
    sequence_result: an existing candidate_sequence() output to verify.
    direction: the direction the sequence claims ('forward'/'backward').
    traditional_role: only the explicitly selected historical role, or None.
    direction_candidate: the traditional_direction() result when the
        research-role mode was used; None for caller-explicit direction.
    periods: expected row count; defaults to len(sequence_result['rows']).
    """
    # ---- 1. Resolve the natal month pillar from the real Trace ----
    trace = chart_output.get("trace") if isinstance(chart_output, dict) else None
    pillar_index, pillar_step = _resolve_pillars_step(trace)
    pillar_output = pillar_step.get("output") or {}
    ganzhi = pillar_output.get("ganzhi")
    if not isinstance(ganzhi, list) or len(ganzhi) != 4:
        _fail("pillars step output has no valid ganzhi")
    year_ganzhi, month_ganzhi, day_ganzhi = ganzhi[0], ganzhi[1], ganzhi[2]
    day_stem = day_ganzhi[0]
    # Evidence references of the pillars step must resolve.
    evidence = chart_output.get("evidence") if isinstance(chart_output, dict) else None
    if not isinstance(evidence, dict):
        _fail("chart output has no evidence map")
    for evidence_id in pillar_step.get("evidence_ids", []):
        if evidence_id not in evidence:
            _fail("dangling evidence reference %r on pillars step" % evidence_id)

    # ---- 2. Exactly one direction source, verified ----
    if direction_candidate is not None:
        # Fail-closed: the research candidate must pass the TJ-014.1 gate.
        validate_direction_candidate(direction_candidate)
        if direction_candidate["direction"] != direction:
            _fail("direction candidate disagrees with sequence direction")
        if traditional_role != direction_candidate["traditional_role"]:
            _fail("traditional role disagrees with direction candidate")
        if direction_candidate["year_ganzhi"] != year_ganzhi:
            _fail("direction candidate year pillar disagrees with trace")
        direction_source = "opt_in_traditional_year_stem_role_candidate"
        direction_validated = True
        classical_approved = direction_candidate["classical_direction_evidence_approved"]
    else:
        if traditional_role is not None and direction is None:
            _fail("traditional role without an explicit direction")
        if type(direction) is not str or direction not in ("forward", "backward"):
            _fail("direction must be forward or backward")
        direction_source = "explicit_caller_selection_only"
        direction_validated = False
        classical_approved = False
    if classical_approved is not False:
        _fail("direction method claims classical approval it does not have")

    # ---- 3. The sequence artefact must agree with the resolved facts ----
    if not isinstance(sequence_result, dict):
        _fail("sequence result is not an object")
    if sequence_result.get("source_month_ganzhi") != month_ganzhi:
        _fail("sequence month pillar disagrees with trace month pillar")
    if sequence_result.get("natal_day_master") != day_stem:
        _fail("sequence day master disagrees with trace day pillar")
    if sequence_result.get("direction") != direction:
        _fail("sequence direction disagrees with declared direction")
    rows = sequence_result.get("rows")
    if not isinstance(rows, list) or not rows:
        _fail("sequence has no rows")
    expected_periods = len(rows) if periods is None else periods
    if len(rows) != expected_periods:
        _fail("row count %d != expected %d" % (len(rows), expected_periods))

    # ---- 4. Recompute every row independently ----
    month_index = ganzhi_index(month_ganzhi)
    sign = 1 if direction == "forward" else -1
    seen = set()
    row_lineage = []
    for step_number, row in enumerate(rows, start=1):
        expected_ganzhi = CYCLE[(month_index + sign * step_number) % 60]
        candidate = row.get("candidate_ganzhi")
        if candidate != expected_ganzhi:
            _fail("row %d cycle drift: %r != %r"
                  % (step_number, candidate, expected_ganzhi))
        if candidate == month_ganzhi:
            _fail("row %d repeats the natal month pillar" % step_number)
        if candidate in seen:
            _fail("duplicate candidate ganzhi %r" % candidate)
        seen.add(candidate)
        expected_ten_god = ten_god(day_stem, row.get("stem"))
        if row.get("ten_god_relative_to_natal_day_stem") != expected_ten_god:
            _fail("row %d ten god contradicts natal day stem" % step_number)
        row_lineage.append({
            "period_index": step_number,
            "candidate_ganzhi": candidate,
            "cycle_index": (month_index + sign * step_number) % 60,
            "ten_god": expected_ten_god,
            "month_pillar_trace_index": pillar_index,
        })

    # ---- 5. Research evidence boundary restated, never promoted ----
    for field in ("research_only",):
        if sequence_result.get(field) is not True:
            _fail("sequence %s must remain true" % field)
    for field in ("public_enabled", "ai_enabled",
                  "classical_evidence_for_dayun_sequence_approved"):
        if sequence_result.get(field) is not False:
            _fail("sequence %s must remain false" % field)
    if sequence_result.get("dayun_sequence_policy_review_status") != "unreviewed":
        _fail("sequence policy review status must remain unreviewed")

    chain_verification = {
        "chain_variant": CHAIN_VARIANT,
        "month_pillar": month_ganzhi,
        "month_pillar_trace_index": pillar_index,
        "month_pillar_rule_id": PILLARS_RULE_ID,
        "month_pillar_evidence_verified": True,
        "year_ganzhi": year_ganzhi,
        "day_stem": day_stem,
        "direction": direction,
        "direction_source": direction_source,
        "direction_candidate_validated": direction_validated,
        "direction_method_classical_approval": False,
        "periods": expected_periods,
        "row_checks": {
            "first_excludes_month_pillar": True,
            "no_duplicate_candidates": True,
            "cycle_continuity_verified": True,
            "ten_gods_match_natal_day_stem": True,
        },
        "ten_gods_rule_id": TEN_GODS_RULE_ID,
        "research_only": True,
        "public_enabled": False,
        "ai_enabled": False,
        "scope": "月柱、方向来源、六十甲子索引、十神均已按真实 Trace 与重算核验；顺逆取法与排运方法仍未获古籍审核，不宣布起运岁数、交运日期或吉凶。",
    }
    return {
        "variant": CHAIN_VARIANT,
        "chain_verification": chain_verification,
        "row_lineage": row_lineage,
        "research_only": True,
        "public_enabled": False,
        "ai_enabled": False,
    }
