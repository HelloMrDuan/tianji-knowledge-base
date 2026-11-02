"""U1 最小公开能力（Batch B）: the public strength-presentation builder.

Authorized by the user's 2026-11-02 adjudication (Q1=A, Q2=B, Q3=B;
recorded in docs/product/U1U3_ADJUDICATION_2026-11-02.md). This module
derives the public presentation object (Variant
``strength-public-presentation-v1``) exclusively from one executed
bounded strength assessment of the same request
(``bazi-strength-adjudication-v1``) plus that request's own execution
records (trace steps, rule matches, evidence records). It is the same
discipline as the phase-1 xiyong builder: the builder is pure and
deterministic, calls no model and no ExplanationService, and never
looks anything up statically -- every rule id, condition and evidence
reference is checked mechanically against the same request's executed
factors. Any forged, drifted or incompletely bound input fails closed
with ``ValueError``; the scenario layer turns that into a failed
request rather than a partial presentation.

What the object is and is not. It states exactly one fact: that this
chart satisfies every conjunctive condition of one reviewed sufficient
predicate. Its wording is fixed to ``已审强弱形态事实`` and it never
writes 身旺/身弱， never carries a useful_god, a 扶抑 direction, a
格局 verdict, a 吉凶 verdict or a prediction. A chart that matches no
predicate yields ``not_judgeable`` (never weak) -- including when the
verdict carries only the assessment's no-match marker
``outside_reviewed_sufficient_conditions``; a chart barred by a
blocking conflict id or any other blocker yields ``conflict`` (never
a classification); a builder failure yields no object at all (never
an empty success).

Predicate surface (existing eight families only; nothing here registers,
modifies or re-derives a predicate -- the bounded assessment remains the
sole adjudication, and this builder only verifies its claimed
conditions against the executed factor steps of the same request):

* ``pure_support`` 木×卯， strong, Phase2 step
  ``bazi.phase2.strength_pure_support``;
* ``pure_generating_support`` 木×亥， strong, r029 /
  ``bazi.phase2.strength_pure_generating_support``;
* ``isolated_control`` 木×酉， weak (the only weak family), Phase2 step
  ``bazi.phase2.strength_isolated_control``;
* ``commanding_visible_support`` 丙×午， strong, r030 /
  ``bazi.phase2.strength_commanding_visible_support``;
* ``lu_visible_support`` 丙×巳， strong, r032 /
  ``bazi.phase2.strength_lu_visible_support``;
* ``changsheng_visible_support`` 丙×寅， strong, pending Phase1/Phase2
  rule registration: the verdict issues through the registered bounded
  adjudication exit, and additionally requires the user-adjudicated
  segment gate (reading 乙 segment-tightened) to have passed on the
  same request's authorized pilot result (segment 甲） -- without a
  passed gate a changsheng claim is a forgery and fails closed;
* ``pure_support_metal`` 金×酉， strong in name only: registered
  (r033) but constructively unsatisfiable on a real calendar chart
  (proof on record), so a presented metal verdict is by construction
  a forgery and fails closed -- the family stays registered, it never
  gains a positive sample from this module;
* ``pure_generating_support_water`` 水×子， strong, r034 /
  ``bazi.phase2.strength_pure_generating_support_water``.

The research assessment itself (``strength_assessment``) stays
research_only / public_enabled=False / ai_enabled=False and is never
released; only the validated presentation object is lifted by the
projection, and only for the bazi-profile envelope.
"""

import copy
import re

from .bazi_adjudication import ADJUDICATION_VARIANT

VARIANT = "strength-public-presentation-v1"
STATEMENT = "已审强弱形态事实"
SCOPE_STATEMENT = (
    "本呈现仅陈述已审充分谓词的命中事实；不是全盘旺衰判断，"
    "不意味着喜用神或吉凶；未命中不等于弱。")
LIMITATIONS = (
    "仅限已审的八个充分谓词家族；其余命盘形态暂不可判。",
    "金×酉谓词已注册但在真实历法命盘上构造性不可满足，不声称正例。")

_ACTION_EFFECTS_STEP = "bazi.phase2.action_effects"
_PRINCIPAL_STEP = "bazi.phase2.principal_month"
_ROOTS_STEP = "bazi.phase2.root_availability"
_PILLARS_STEP = "bazi.phase2.pillars"
_GATE_STEP = "bazi.phase2.strength_bounded_adjudication"
_NON_GATE_STEP = "bazi.phase2.strength_adjudication"
_PILOT_VARIANT = "bazi-siling-yin-pilot-v1"
_SEGMENT_READING = "segment_tightened"
_REQUIRED_SEGMENT_STEM = "甲"

# predicate_id -> (day-master stems, month branches, classification,
#                   phase1 rule id or None, phase2 step id or None for
#                   the bounded-exit predicate, rule registration note).
# The changsheng family has no predicate trace step: its phase2 step is
# the bounded adjudication exit itself, and its registration note is
# the pending disclosure carried on the verdict.
PREDICATES = {
    "pure_support": (
        ("甲", "乙"), ("卯",), "strong", None,
        "bazi.phase2.strength_pure_support", "registered"),
    "pure_generating_support": (
        ("甲", "乙"), ("亥",), "strong", "bazi.rule.r029",
        "bazi.phase2.strength_pure_generating_support", "registered"),
    "isolated_control": (
        ("甲", "乙"), ("酉",), "weak", None,
        "bazi.phase2.strength_isolated_control", "registered"),
    "commanding_visible_support": (
        ("丙",), ("午",), "strong", "bazi.rule.r030",
        "bazi.phase2.strength_commanding_visible_support", "registered"),
    "lu_visible_support": (
        ("丙",), ("巳",), "strong", "bazi.rule.r032",
        "bazi.phase2.strength_lu_visible_support", "registered"),
    "changsheng_visible_support": (
        ("丙",), ("寅",), "strong", None,
        "bazi.phase2.strength_bounded_adjudication",
        "pending_phase1_rule_registration"),
    "pure_support_metal": (
        ("庚", "辛"), ("酉",), "strong", "bazi.rule.r033",
        "bazi.phase2.strength_pure_support_metal", "registered"),
    "pure_generating_support_water": (
        ("壬", "癸"), ("子",), "strong", "bazi.rule.r034",
        "bazi.phase2.strength_pure_generating_support_water",
        "registered"),
}

_COMMON_KEYS = frozenset((
    "variant", "status", "day_master", "month_branch",
    "scope_statement", "limitations"))
_PRESENTED_KEYS = _COMMON_KEYS | frozenset((
    "statement", "classification", "predicate_id", "phase1_rule_id",
    "phase2_step_id", "rule_registration", "conditions",
    "evidence_ids", "source_ids"))
_PRESENTED_CHANGSHENG_KEYS = _PRESENTED_KEYS | frozenset(("segment_gate",))
_NOT_JUDGEABLE_KEYS = _COMMON_KEYS | frozenset(("reason",))
_CONFLICT_KEYS = _COMMON_KEYS | frozenset(("conflict_ids", "blocker_reasons"))
_NOT_JUDGEABLE_REASONS = frozenset((
    "no_predicate_matched", "out_of_scope", "insufficient_evidence"))
_FACT_REF_RE = re.compile(
    r"^#/trace/\d+/output/[a-z_]+_scope_conditions/[a-z_0-9]+$")


def _fail(message):
    raise ValueError("Strength public presentation rejected: " + message)


def _steps_by_id(trace):
    if not isinstance(trace, list):
        _fail("execution trace must be a list")
    steps = {}
    for index, step in enumerate(trace):
        if not isinstance(step, dict) or not isinstance(
                step.get("rule_id"), str):
            _fail("execution trace step must carry a rule_id")
        if step["rule_id"] in steps:
            _fail("duplicate rule_id in execution trace")
        steps[step["rule_id"]] = (index, step)
    return steps


def _require_step(steps, rule_id):
    if rule_id not in steps:
        _fail("missing executed step " + rule_id)
    return steps[rule_id]


def _require_match(rule_matches, rule_id):
    if not isinstance(rule_matches, list):
        _fail("execution rule_matches must be a list")
    for match in rule_matches:
        if isinstance(match, dict) and match.get("rule_id") == rule_id \
                and match.get("matched") is True:
            return
    _fail("no executed rule match for " + rule_id)


def _require_evidence(evidence, evidence_ids):
    if not isinstance(evidence, dict):
        _fail("execution evidence must be a mapping")
    for evidence_id in evidence_ids or []:
        record = evidence.get(evidence_id)
        if not isinstance(record, dict) \
                or not isinstance(record.get("source_id"), str) \
                or not record["source_id"]:
            _fail("evidence id without a bound source record: "
                  + str(evidence_id))


def _base(day_master, month_branch, status):
    return {
        "variant": VARIANT,
        "status": status,
        "day_master": day_master,
        "month_branch": month_branch,
        "scope_statement": SCOPE_STATEMENT,
        "limitations": list(LIMITATIONS),
    }


def public_strength_presentation(assessment, execution):
    """Build the public strength presentation for one executed verdict.

    ``assessment`` is the bounded strength assessment dict of the same
    request; ``execution`` is ``{"trace", "rule_matches", "evidence"}``
    from the same gate execution. Returns the presentation dict. Raises
    ``ValueError`` on any drift, forgery or incomplete binding -- the
    caller must fail the whole request, never return a partial object.
    """
    if not isinstance(assessment, dict):
        _fail("assessment must be a mapping")
    if not isinstance(execution, dict):
        _fail("execution must be a mapping")
    # The research verdict's own governance flags are part of the
    # binding: only a verdict that is still research_only, still not
    # public and still not AI-enabled may be presented through this
    # scoped object (the flags themselves are never flipped).
    if assessment.get("variant") != ADJUDICATION_VARIANT:
        _fail("assessment variant mismatch")
    if assessment.get("research_only") is not True \
            or assessment.get("public_enabled") is not False \
            or assessment.get("ai_enabled") is not False:
        _fail("assessment governance flags mismatch")
    if assessment.get("maturity") != "PARTIAL" \
            or assessment.get("weights_available") is not False \
            or assessment.get("full_strength_classifier_ready") is not False:
        _fail("assessment maturity/weight flags mismatch")
    if assessment.get("supported_classifications") != [
            "strong", "weak", "indeterminate"]:
        _fail("assessment supported classifications mismatch")

    trace = execution.get("trace")
    rule_matches = execution.get("rule_matches")
    evidence = execution.get("evidence")
    steps = _steps_by_id(trace)
    pillars_index, pillars_step = _require_step(steps, _PILLARS_STEP)
    principal_index, principal_step = _require_step(steps, _PRINCIPAL_STEP)
    roots_index, roots_step = _require_step(steps, _ROOTS_STEP)
    effects_index, effects_step = _require_step(steps, _ACTION_EFFECTS_STEP)
    gate_index = None
    for gate_id in (_GATE_STEP, _NON_GATE_STEP):
        if gate_id in steps:
            gate_index = steps[gate_id][0]
            break
    if gate_index is None:
        _fail("missing executed strength gate step")
    for step_id in (_PILLARS_STEP, _PRINCIPAL_STEP, _ROOTS_STEP,
                    _ACTION_EFFECTS_STEP):
        _require_match(rule_matches, step_id)
        step = steps[step_id][1]
        if not step.get("evidence_ids"):
            _fail("executed step without evidence: " + step_id)
        _require_evidence(evidence, step["evidence_ids"])
    matched_ids = assessment.get("matched_rule_ids")
    if not isinstance(matched_ids, list) or not all(
            rule_id in steps for rule_id in matched_ids):
        _fail("assessment matched_rule_ids outside the executed trace")

    pillars = pillars_step.get("output")
    principal = principal_step.get("output")
    roots = roots_step.get("output")
    effects = effects_step.get("output")
    if not isinstance(pillars, dict) or not isinstance(principal, dict) \
            or not isinstance(roots, dict) or not isinstance(effects, dict):
        _fail("executed factor outputs must be mappings")
    day_master_raw = pillars.get("day_master")
    if isinstance(day_master_raw, dict):
        day_master = day_master_raw.get("stem")
    elif isinstance(day_master_raw, str):
        day_master = day_master_raw
    else:
        day_master = None
    ganzhi = pillars.get("ganzhi")
    try:
        month_branch = ganzhi[1][1]
    except (TypeError, IndexError, KeyError):
        month_branch = None
    if not isinstance(day_master, str) or not day_master \
            or not isinstance(month_branch, str) or not month_branch:
        _fail("pillars step lacks day master or month branch")
    if principal.get("month_branch") != month_branch:
        _fail("principal month branch drifted from pillars")
    if principal.get("day_master") != day_master:
        _fail("principal month day master drifted from pillars")

    why = assessment.get("why_not_indeterminate")
    blockers = assessment.get("blockers")
    conflict_ids = assessment.get("conflict_ids")
    if not isinstance(blockers, list) or not isinstance(conflict_ids, list):
        _fail("assessment blockers/conflict_ids must be lists")
    _require_evidence(evidence, assessment.get("evidence_ids"))
    evidence_ids = sorted(assessment.get("evidence_ids") or [])
    source_ids = sorted({evidence[e]["source_id"]
                         for e in evidence_ids})
    if assessment.get("source_ids") is not None \
            and sorted(assessment["source_ids"]) != source_ids:
        _fail("assessment source_ids drifted from bound evidence")

    # A verdict that is both presented and blocked is inconsistent:
    # fail closed rather than choosing a side. A presented verdict
    # with no bound evidence at all is likewise unverifiable.
    if why is not None and (blockers or conflict_ids):
        _fail("presented verdict carries blockers or conflicts")
    if why is not None and not evidence_ids:
        _fail("presented verdict without bound evidence")
    # The bounded assessment appends the marker
    # ``outside_reviewed_sufficient_conditions`` to every verdict
    # that matches no predicate: it is the no-match signal, not a
    # conflict. Only a blocking conflict id or a blocker with any
    # other reason makes the state a conflict; the marker alone (or
    # no blockers at all) is not_judgeable.
    real_blockers = [b for b in blockers if isinstance(b, dict)
                     and b.get("reason") not in (
                         None, "outside_reviewed_sufficient_conditions")]
    if why is None and (conflict_ids or real_blockers):
        blocker_reasons = sorted({b["reason"] for b in real_blockers
                                  if isinstance(b.get("reason"), str)})
        result = _base(day_master, month_branch, "conflict")
        result["conflict_ids"] = list(conflict_ids)
        result["blocker_reasons"] = blocker_reasons
        return result

    if why is None:
        # No predicate matched and nothing blocks: distinguish an
        # out-of-scope day x month from a near miss inside the scope,
        # and from a scope whose factor conditions never arrived.
        in_scope = any(day_master in days and month_branch in months
                       for days, months, _, _, _, _ in PREDICATES.values())
        if not in_scope:
            reason = "out_of_scope"
        else:
            reason = "no_predicate_matched"
            for predicate_id, (days, months, _, _, _, _) in \
                    PREDICATES.items():
                if day_master in days and month_branch in months:
                    scope_key = predicate_id + "_scope_conditions"
                    conditions = effects.get(scope_key)
                    if not isinstance(conditions, dict) or not conditions:
                        reason = "insufficient_evidence"
                    break
        result = _base(day_master, month_branch, "not_judgeable")
        result["reason"] = reason
        return result

    # Presented: the verdict's claimed conditions must be exactly the
    # executed factor conditions of the same request.
    if not isinstance(why, dict):
        _fail("why_not_indeterminate must be a mapping")
    if why.get("all_required_conditions_verified") is not True:
        _fail("verdict conditions not all verified")
    if why.get("excluded_dependencies") != [
            "dated_commander", "independent_hidden_effect_scores"]:
        _fail("verdict excluded dependencies mismatch")
    classification = assessment.get("classification")
    if classification not in ("strong", "weak"):
        _fail("presented verdict without a strong/weak classification")
    if assessment.get("decision_status") != "reviewed_sufficient_rule_matched":
        _fail("presented verdict decision status mismatch")
    if why.get("sufficient_rule") is not None:
        predicate_id = None
        for candidate, spec in PREDICATES.items():
            if spec[4] == why["sufficient_rule"]:
                predicate_id = candidate
                break
        if predicate_id is None:
            _fail("verdict sufficient rule is not a known predicate step")
        if predicate_id == "changsheng_visible_support":
            _fail("changsheng verdict must not carry a predicate rule id")
    else:
        predicate_id = why.get("sufficient_predicate")
        if predicate_id != "changsheng_visible_support":
            _fail("verdict without a sufficient rule must be changsheng")
        if why.get("predicate_rule_registration") != \
                "pending_phase1_rule_registration":
            _fail("changsheng verdict registration disclosure mismatch")
        if why.get("month_condition_reading") != _SEGMENT_READING:
            _fail("changsheng verdict month reading mismatch")
    days, months, expected_class, phase1_rule_id, phase2_step_id, \
        registration = PREDICATES[predicate_id]
    if day_master not in days or month_branch not in months:
        _fail("verdict predicate outside its day x month scope")
    if classification != expected_class:
        _fail("verdict classification outside its predicate scope")
    if predicate_id == "pure_support_metal":
        # Registered but constructively unsatisfiable on a real chart
        # (proof on record): a presented metal verdict cannot come
        # from a real execution, so it is a forgery by construction.
        _fail("metal predicate has no real-chart positive by proof")

    scope_key = predicate_id + "_scope_conditions"
    scope_conditions = effects.get(scope_key)
    scope_met = effects.get(predicate_id + "_scope_met")
    if not isinstance(scope_conditions, dict) or not scope_conditions:
        _fail("executed factor layer lacks the predicate scope conditions")
    if scope_met is not True or not all(scope_conditions.values()):
        _fail("executed factor conditions do not all hold")
    relation = principal.get("relation")
    if predicate_id in ("pure_generating_support",
                        "changsheng_visible_support"):
        if relation != "generates_me":
            _fail("predicate month relation mismatch")
    elif relation != "same_element" and predicate_id != "isolated_control":
        _fail("predicate month relation mismatch")
    if predicate_id == "isolated_control":
        if relation != "controls_me" or roots.get("root_presence") is not False:
            _fail("isolated predicate requires no root and a control month")
    elif roots.get("root_presence") is not True:
        _fail("predicate requires a present root")

    why_conditions = why.get("conditions")
    if not isinstance(why_conditions, list) or not why_conditions:
        _fail("verdict without bound conditions")
    if {c.get("condition") for c in why_conditions} != set(scope_conditions):
        _fail("verdict conditions drifted from executed scope conditions")
    conditions = []
    for condition in why_conditions:
        if not isinstance(condition, dict) \
                or condition.get("met") is not True \
                or condition.get("rule_id") != _ACTION_EFFECTS_STEP:
            _fail("verdict condition binding mismatch")
        expected_ref = ("#/trace/%d/output/%s/%s"
                        % (effects_index, scope_key,
                           condition.get("condition")))
        if condition.get("fact_ref") != expected_ref:
            _fail("verdict condition fact_ref outside the executed trace")
        _require_evidence(evidence, condition.get("evidence_ids"))
        conditions.append({
            "condition": condition["condition"],
            "met": True,
            "fact_ref": condition["fact_ref"],
            "rule_id": _ACTION_EFFECTS_STEP,
        })
    conditions.sort(key=lambda c: c["condition"])

    result = _base(day_master, month_branch, "presented")
    result["statement"] = STATEMENT
    result["classification"] = classification
    result["predicate_id"] = predicate_id
    result["phase1_rule_id"] = phase1_rule_id
    result["phase2_step_id"] = phase2_step_id
    result["rule_registration"] = registration
    result["conditions"] = conditions
    result["evidence_ids"] = evidence_ids
    result["source_ids"] = source_ids
    if predicate_id == "changsheng_visible_support":
        # The segment gate is not a trace fact: it enters only through
        # the combination function's validated pilot claim on the same
        # request. A changsheng claim without a passed Jia gate -- no
        # gate block, a non-computed pilot, a non-Jia segment, or an
        # unverifiable claim -- is a forgery and fails closed; it is
        # never rewritten as weak.
        gate = assessment.get("changsheng_segment_gate")
        why_gate = why.get("segment_gate")
        if not isinstance(gate, dict) or not isinstance(why_gate, dict):
            _fail("changsheng verdict without a segment gate")
        if gate.get("pilot_variant") != _PILOT_VARIANT \
                or gate.get("reading") != _SEGMENT_READING \
                or gate.get("claim_verifiable") is not True \
                or gate.get("pilot_status") != "computed" \
                or gate.get("segment_stem") != _REQUIRED_SEGMENT_STEM \
                or gate.get("segment_index") != 3 \
                or gate.get("required_segment_stem") != _REQUIRED_SEGMENT_STEM \
                or gate.get("gate_passed") is not True \
                or gate.get("gate_outcome") != "segment_jia":
            _fail("changsheng segment gate did not pass the Jia segment")
        if why_gate.get("met") is not True \
                or why_gate.get("segment_stem") != _REQUIRED_SEGMENT_STEM \
                or why_gate.get("registered_interval") != \
                gate.get("registered_interval"):
            _fail("changsheng verdict gate binding mismatch")
        result["segment_gate"] = {
            "pilot_variant": _PILOT_VARIANT,
            "reading": _SEGMENT_READING,
            "segment_stem": _REQUIRED_SEGMENT_STEM,
            "segment_index": 3,
            "registered_interval": gate["registered_interval"],
            "gate_outcome": "segment_jia",
        }
    return result


def is_valid_public_strength_presentation(obj):
    """Closed-shape validator for the projection's scoped release.

    Mirrors the xiyong/dayun validators: exact top-level key set per
    status, verbatim variant/statement/scope/limitations, and the
    predicate-scope and gate consistency that can be checked without
    the execution record. Anything else is stripped by the projection.
    """
    if not isinstance(obj, dict):
        return False
    status = obj.get("status")
    if status == "presented":
        keys = _PRESENTED_KEYS
        if obj.get("predicate_id") == "changsheng_visible_support":
            keys = _PRESENTED_CHANGSHENG_KEYS
        elif "segment_gate" in obj:
            return False
    elif status == "not_judgeable":
        keys = _NOT_JUDGEABLE_KEYS
    elif status == "conflict":
        keys = _CONFLICT_KEYS
    else:
        return False
    if set(obj) != set(keys):
        return False
    if obj.get("variant") != VARIANT:
        return False
    if obj.get("scope_statement") != SCOPE_STATEMENT:
        return False
    if obj.get("limitations") != list(LIMITATIONS):
        return False
    if not isinstance(obj.get("day_master"), str) \
            or not obj["day_master"] \
            or not isinstance(obj.get("month_branch"), str) \
            or not obj["month_branch"]:
        return False
    if status == "presented":
        if obj.get("statement") != STATEMENT:
            return False
        predicate_id = obj.get("predicate_id")
        spec = PREDICATES.get(predicate_id)
        if spec is None:
            return False
        days, months, expected_class, phase1_rule_id, phase2_step_id, \
            registration = spec
        if obj.get("classification") != expected_class:
            return False
        if obj.get("day_master") not in days \
                or obj.get("month_branch") not in months:
            return False
        if obj.get("phase1_rule_id") != phase1_rule_id \
                or obj.get("phase2_step_id") != phase2_step_id \
                or obj.get("rule_registration") != registration:
            return False
        if predicate_id == "pure_support_metal":
            return False
        conditions = obj.get("conditions")
        if not isinstance(conditions, list) or not conditions:
            return False
        for condition in conditions:
            if not isinstance(condition, dict) \
                    or set(condition) != {"condition", "met", "fact_ref",
                                          "rule_id"} \
                    or condition.get("met") is not True \
                    or condition.get("rule_id") != _ACTION_EFFECTS_STEP \
                    or not isinstance(condition.get("fact_ref"), str) \
                    or not _FACT_REF_RE.match(condition["fact_ref"]):
                return False
        if not isinstance(obj.get("evidence_ids"), list) \
                or not obj["evidence_ids"] \
                or not isinstance(obj.get("source_ids"), list) \
                or not obj["source_ids"]:
            return False
        if predicate_id == "changsheng_visible_support":
            gate = obj.get("segment_gate")
            if not isinstance(gate, dict) \
                    or set(gate) != {"pilot_variant", "reading",
                                     "segment_stem", "segment_index",
                                     "registered_interval", "gate_outcome"} \
                    or gate.get("pilot_variant") != _PILOT_VARIANT \
                    or gate.get("reading") != _SEGMENT_READING \
                    or gate.get("segment_stem") != _REQUIRED_SEGMENT_STEM \
                    or gate.get("segment_index") != 3 \
                    or gate.get("gate_outcome") != "segment_jia" \
                    or not isinstance(gate.get("registered_interval"), str):
                return False
    elif status == "not_judgeable":
        if obj.get("reason") not in _NOT_JUDGEABLE_REASONS:
            return False
        if "classification" in obj or "predicate_id" in obj:
            return False
    elif status == "conflict":
        # Factor-inconsistency blockers carry no conflict id, so a
        # conflict object is valid when either list is non-empty.
        if not isinstance(obj.get("conflict_ids"), list) \
                or not all(isinstance(c, str) for c in obj["conflict_ids"]):
            return False
        if not isinstance(obj.get("blocker_reasons"), list) \
                or not all(isinstance(r, str) for r in obj["blocker_reasons"]):
            return False
        if not obj["conflict_ids"] and not obj["blocker_reasons"]:
            return False
        if "classification" in obj or "predicate_id" in obj:
            return False
    return True
