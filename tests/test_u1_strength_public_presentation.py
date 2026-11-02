"""U1 Batch B: public strength-presentation builder tests (public CI).

These tests run in public CI without any sealed data. They exercise
the builder ``public_strength_presentation`` and the validator
``is_valid_public_strength_presentation`` over SYNTHETIC execution
views (marked as such below): the trace steps, rule matches and
evidence records are fabricated in the registered shapes, exactly like
the phase-1 xiyong public presentation test's synthetic view. Real
execution coverage -- Golden charts through the production calendar
chain, the F4 pilot segment gate on real Jie windows, near misses,
conflict charts and equivalence/leakage against the live scenario --
lives in the sealed companion ``test_u1_strength_public_sealed.py``,
which runs only in the offline acceptance, never in public CI.

What is pinned here: the closed key sets per status, the verbatim
statement/scope/limitations, the predicate-scope table, the four
statuses (presented / not_judgeable / conflict / builder failure),
the tamper classes that must fail closed, the projection scoped
release (bazi-profile verbatim, everything else stripped), and the
client contract gate (a client-supplied strength_variant keeps the
baseline refusal verbatim).
"""

import copy
import unittest

from tianji_kb.bazi_strength_public import (
    LIMITATIONS,
    PREDICATES,
    SCOPE_STATEMENT,
    STATEMENT,
    VARIANT,
    is_valid_public_strength_presentation,
    public_strength_presentation,
)
from tianji_kb.public_projection import project_execution
from tianji_kb.scenario_engine import execute_scenario

ADJUDICATION_VARIANT = "bazi-strength-adjudication-v1"
PILOT_VARIANT = "bazi-siling-yin-pilot-v1"
REGISTERED_INTERVAL = "[t0+14d, next jie)"

# Predicate -> (day master, month branch, relation, root presence,
# classification) for the synthetic presented views.
PRESENTED_CASES = {
    "pure_support": ("甲", "卯", "same_element", True, "strong"),
    "pure_generating_support": ("甲", "亥", "generates_me", True, "strong"),
    "isolated_control": ("乙", "酉", "controls_me", False, "weak"),
    "commanding_visible_support": ("丙", "午", "same_element", True, "strong"),
    "lu_visible_support": ("丙", "巳", "same_element", True, "strong"),
    "changsheng_visible_support": ("丙", "寅", "generates_me", True, "strong"),
    "pure_generating_support_water": ("癸", "子", "same_element", True, "strong"),
}

BANNED_KEYS = ("useful_god", "fuyi", "pattern", "direction", "verdict")
BANNED_VALUES = ("身旺", "身弱")


def _scan_banned(obj, path=""):
    if isinstance(obj, dict):
        for key, value in obj.items():
            if key in BANNED_KEYS:
                raise AssertionError("banned key %s at %s" % (key, path))
            _scan_banned(value, path + "/" + str(key))
    elif isinstance(obj, list):
        for index, value in enumerate(obj):
            _scan_banned(value, "%s[%d]" % (path, index))
    elif isinstance(obj, str):
        for banned in BANNED_VALUES:
            if banned in obj:
                raise AssertionError(
                    "banned value %s at %s" % (banned, path))


def _synthetic_view(day_master, month_branch, *, predicate_id=None,
                    classification=None, relation=None,
                    root_presence=True, scope_conditions=None,
                    scope_met=True, blockers=None, conflict_ids=None,
                    gate=None, why_gate=None, drop_match=None,
                    drop_evidence=None, scope_key_present=True):
    """Fabricate an execution view in the registered shapes.

    SYNTHETIC: no calendar, no sealed bundle, no real chart. The
    trace steps carry the factor outputs the builder cross-checks
    (pillars day master / month branch, principal relation, root
    presence, action-effects scope conditions); the assessment carries
    the verdict the builder must verify against them.
    """
    evidence = {}
    trace = []
    matches = []

    def add_step(rule_id, output):
        evidence_id = rule_id + "#0"
        evidence[evidence_id] = {
            "source_id": "bazi.source.synthetic", "section_id": "s",
            "chapter_id": "c", "chapter_title": "t",
            "original_text": "fact", "rule_id": rule_id}
        trace.append({"rule_id": rule_id, "evidence_scope": "registered",
                      "inputs": {}, "output": output,
                      "evidence_ids": [evidence_id]})
        matches.append({"rule_id": rule_id, "matched": True,
                        "kind": "executed_calculation",
                        "evidence_scope": "registered",
                        "evidence_ids": [evidence_id]})
        return evidence_id

    add_step("bazi.phase2.pillars", {
        "ganzhi": [["甲", "子"], ["乙", month_branch],
                   [day_master, "子"], ["丙", "子"]],
        "day_master": {"stem": day_master, "branch": "子"}})
    add_step("bazi.phase2.principal_month", {
        "day_master": day_master, "month_branch": month_branch,
        "relation": relation, "status": "reviewed_relation",
        "principal_qi": "synthetic"})
    add_step("bazi.phase2.root_availability", {
        "root_presence": root_presence, "roots": []})
    effects = {}
    if predicate_id is not None and scope_key_present:
        effects[predicate_id + "_scope_conditions"] = scope_conditions
        effects[predicate_id + "_scope_met"] = scope_met
    effects_id = add_step("bazi.phase2.action_effects", effects)
    assessment = {
        "classification": classification or "indeterminate",
        "variant": ADJUDICATION_VARIANT,
        "decision_status": "reviewed_sufficient_rule_matched"
        if predicate_id is not None else "insufficient_reviewed_rules",
        "matched_rule_ids": [step["rule_id"] for step in trace],
        "fact_refs": ["#/trace/%d/output" % i for i in range(len(trace))],
        "evidence_ids": [step["evidence_ids"][0] for step in trace],
        "source_ids": ["bazi.source.synthetic"],
        "conflict_checks": [],
        "conflict_ids": list(conflict_ids or []),
        "blockers": list(blockers or []),
        "unresolved_evidence": [],
        "why_not_indeterminate": None,
        "supported_classifications": ["strong", "weak", "indeterminate"],
        "variant_dependencies": {
            "dated_commander": False, "principal_qi": True,
            "root_availability": True, "bounded_visible_effects": True,
            "independent_hidden_effect_scores": False},
        "maturity": "PARTIAL", "research_only": True,
        "public_enabled": False, "ai_enabled": False,
        "weights_available": False, "source_case_lookup_used": False,
        "full_strength_classifier_ready": False,
        "limitations": [],
    }
    if predicate_id is not None:
        scope_key = predicate_id + "_scope_conditions"
        why = {
            "conditions": [
                {"condition": name, "met": True,
                 "fact_ref": "#/trace/3/output/%s/%s" % (scope_key, name),
                 "rule_id": "bazi.phase2.action_effects",
                 "evidence_ids": [effects_id]}
                for name in scope_conditions],
            "all_required_conditions_verified": True,
            "excluded_dependencies": ["dated_commander",
                                      "independent_hidden_effect_scores"],
        }
        if predicate_id == "changsheng_visible_support":
            why["sufficient_rule"] = None
            why["sufficient_predicate"] = predicate_id
            why["predicate_rule_registration"] = \
                "pending_phase1_rule_registration"
            why["month_condition_reading"] = "segment_tightened"
            why["segment_gate"] = why_gate
        else:
            why["sufficient_rule"] = PREDICATES[predicate_id][4]
        assessment["why_not_indeterminate"] = why
    if gate is not None:
        assessment["changsheng_segment_gate"] = gate
    gate_evidence_id = add_step(
        "bazi.phase2.strength_bounded_adjudication", assessment)
    assessment["matched_rule_ids"].append(
        "bazi.phase2.strength_bounded_adjudication")
    assessment["evidence_ids"].append(gate_evidence_id)
    view = {"trace": trace, "rule_matches": matches, "evidence": evidence}
    if drop_match is not None:
        view["rule_matches"] = [
            m for m in matches if m["rule_id"] != drop_match]
    if drop_evidence is not None:
        for step in view["trace"]:
            if step["rule_id"] == drop_evidence:
                step["evidence_ids"] = []
    return assessment, view


def _presented_view(predicate_id):
    day_master, month_branch, relation, root_presence, classification = \
        PRESENTED_CASES[predicate_id]
    scope_conditions = {"scope_condition_a": True, "scope_condition_b": True}
    gate = None
    why_gate = None
    if predicate_id == "changsheng_visible_support":
        gate = {
            "pilot_variant": PILOT_VARIANT, "reading": "segment_tightened",
            "claim_verifiable": True, "pilot_status": "computed",
            "segment_stem": "甲", "segment_index": 3,
            "registered_interval": REGISTERED_INTERVAL,
            "required_segment_stem": "甲", "gate_passed": True,
            "gate_outcome": "segment_jia"}
        why_gate = {"met": True, "segment_stem": "甲",
                    "registered_interval": REGISTERED_INTERVAL}
    assessment, view = _synthetic_view(
        day_master, month_branch, predicate_id=predicate_id,
        classification=classification, relation=relation,
        root_presence=root_presence, scope_conditions=scope_conditions,
        gate=gate, why_gate=why_gate)
    return assessment, view


class PresentedTests(unittest.TestCase):
    def test_all_triggerable_predicates_present(self):
        for predicate_id in PRESENTED_CASES:
            assessment, view = _presented_view(predicate_id)
            result = public_strength_presentation(assessment, view)
            self.assertTrue(
                is_valid_public_strength_presentation(result),
                predicate_id)
            self.assertEqual(result["variant"], VARIANT)
            self.assertEqual(result["status"], "presented")
            self.assertEqual(result["statement"], STATEMENT)
            self.assertEqual(result["predicate_id"], predicate_id)
            self.assertEqual(
                result["classification"],
                PRESENTED_CASES[predicate_id][4])
            self.assertEqual(result["day_master"],
                             PRESENTED_CASES[predicate_id][0])
            self.assertEqual(result["month_branch"],
                             PRESENTED_CASES[predicate_id][1])
            self.assertEqual(result["phase1_rule_id"],
                             PREDICATES[predicate_id][3])
            self.assertEqual(result["phase2_step_id"],
                             PREDICATES[predicate_id][4])
            self.assertEqual(result["rule_registration"],
                             PREDICATES[predicate_id][5])
            self.assertEqual(result["scope_statement"], SCOPE_STATEMENT)
            self.assertEqual(result["limitations"], list(LIMITATIONS))
            self.assertEqual(len(result["conditions"]), 2)
            self.assertTrue(all(c["met"] for c in result["conditions"]))
            _scan_banned(result)

    def test_changsheng_carries_segment_gate(self):
        assessment, view = _presented_view("changsheng_visible_support")
        result = public_strength_presentation(assessment, view)
        self.assertEqual(result["segment_gate"]["segment_stem"], "甲")
        self.assertEqual(result["segment_gate"]["segment_index"], 3)
        self.assertEqual(result["segment_gate"]["gate_outcome"],
                         "segment_jia")
        self.assertEqual(result["segment_gate"]["registered_interval"],
                         REGISTERED_INTERVAL)

    def test_non_changsheng_must_not_carry_segment_gate(self):
        assessment, view = _presented_view("pure_support")
        result = public_strength_presentation(assessment, view)
        self.assertNotIn("segment_gate", result)

    def test_deterministic_rebuild(self):
        assessment, view = _presented_view("lu_visible_support")
        first = public_strength_presentation(assessment, view)
        second = public_strength_presentation(
            copy.deepcopy(assessment), copy.deepcopy(view))
        self.assertEqual(first, second)


class NotJudgeableAndConflictTests(unittest.TestCase):
    def test_near_miss_inside_scope(self):
        # 甲×卯 in scope, but the factor layer reports the predicate
        # scope conditions present and unmet -- modeled by a view
        # whose assessment has no why while the scope key exists.
        assessment, view = _synthetic_view(
            "甲", "卯", relation="same_element", root_presence=True,
            predicate_id=None)
        view["trace"][3]["output"]["pure_support_scope_conditions"] = {
            "scope_condition_a": False}
        view["trace"][3]["output"]["pure_support_scope_met"] = False
        result = public_strength_presentation(assessment, view)
        self.assertEqual(result["status"], "not_judgeable")
        self.assertEqual(result["reason"], "no_predicate_matched")

    def test_insufficient_evidence_inside_scope(self):
        assessment, view = _synthetic_view(
            "甲", "卯", relation="same_element", root_presence=True,
            predicate_id=None, scope_key_present=False)
        # No scope key at all for the in-scope predicate.
        result = public_strength_presentation(assessment, view)
        self.assertEqual(result["status"], "not_judgeable")
        self.assertEqual(result["reason"], "insufficient_evidence")

    def test_no_match_marker_alone_is_not_judgeable(self):
        # Real no-match verdicts always carry the assessment's
        # outside_reviewed_sufficient_conditions marker; it is the
        # no-match signal, not a conflict.
        assessment, view = _synthetic_view(
            "甲", "卯", relation="same_element", root_presence=True,
            predicate_id=None,
            blockers=[{"reason": "outside_reviewed_sufficient_conditions"}])
        result = public_strength_presentation(assessment, view)
        self.assertEqual(result["status"], "not_judgeable")
        self.assertEqual(result["reason"], "insufficient_evidence")

    def test_effectiveness_gap_alone_is_not_judgeable(self):
        # A lone root_availability_not_effective blocker (e.g. a
        # fire-form chart whose segment gate did not pass) is a
        # predicate condition not satisfied, not a conflict.
        assessment, view = _synthetic_view(
            "丙", "寅", relation="generates_me", root_presence=True,
            predicate_id=None,
            blockers=[{"reason": "root_availability_not_effective"},
                      {"reason": "outside_reviewed_sufficient_conditions"}])
        result = public_strength_presentation(assessment, view)
        self.assertEqual(result["status"], "not_judgeable")

    def test_unresolved_interaction_alone_is_not_judgeable(self):
        assessment, view = _synthetic_view(
            "丙", "午", relation="same_element", root_presence=True,
            predicate_id=None,
            blockers=[{"reason": "interaction_effect_unresolved"},
                      {"reason": "outside_reviewed_sufficient_conditions"}])
        result = public_strength_presentation(assessment, view)
        self.assertEqual(result["status"], "not_judgeable")

    def test_out_of_scope_day_month(self):
        assessment, view = _synthetic_view(
            "甲", "子", relation="same_element", root_presence=True,
            predicate_id=None)
        result = public_strength_presentation(assessment, view)
        self.assertEqual(result["status"], "not_judgeable")
        self.assertEqual(result["reason"], "out_of_scope")

    def test_conflict_carries_ids_and_no_classification(self):
        assessment, view = _synthetic_view(
            "丁", "巳", relation="same_element", root_presence=True,
            predicate_id=None,
            blockers=[{"reason": "root_type_source_conflict"}],
            conflict_ids=["sanming-juan2.ding-changsheng"])
        result = public_strength_presentation(assessment, view)
        self.assertEqual(result["status"], "conflict")
        self.assertEqual(result["conflict_ids"],
                         ["sanming-juan2.ding-changsheng"])
        self.assertEqual(result["blocker_reasons"],
                         ["root_type_source_conflict"])
        self.assertNotIn("classification", result)
        self.assertNotIn("predicate_id", result)
        self.assertTrue(is_valid_public_strength_presentation(result))


class TamperTests(unittest.TestCase):
    def test_forged_predicate_day_month_mismatch(self):
        # Sufficient rule says pure (甲×卯） but the pillars say 丙×午.
        assessment, view = _presented_view("pure_support")
        view["trace"][0]["output"]["day_master"] = {"stem": "丙"}
        view["trace"][0]["output"]["ganzhi"][1][1] = "午"
        view["trace"][1]["output"]["day_master"] = "丙"
        view["trace"][1]["output"]["month_branch"] = "午"
        with self.assertRaises(ValueError):
            public_strength_presentation(assessment, view)

    def test_principal_month_drift(self):
        assessment, view = _presented_view("pure_support")
        view["trace"][1]["output"]["month_branch"] = "亥"
        with self.assertRaises(ValueError):
            public_strength_presentation(assessment, view)

    def test_rule_match_not_in_trace(self):
        assessment, view = _synthetic_view(
            "甲", "卯", predicate_id="pure_support",
            classification="strong", relation="same_element",
            root_presence=True,
            scope_conditions={"scope_condition_a": True},
            drop_match="bazi.phase2.principal_month")
        with self.assertRaises(ValueError):
            public_strength_presentation(assessment, view)

    def test_evidence_id_mismatch(self):
        assessment, view = _presented_view("pure_support")
        assessment["evidence_ids"] = assessment["evidence_ids"] + ["forged"]
        with self.assertRaises(ValueError):
            public_strength_presentation(assessment, view)

    def test_blocked_yet_classified(self):
        assessment, view = _presented_view("pure_support")
        assessment["blockers"] = [{"reason": "root_type_source_conflict"}]
        assessment["conflict_ids"] = ["some-conflict"]
        with self.assertRaises(ValueError):
            public_strength_presentation(assessment, view)

    def test_changsheng_without_pilot_gate(self):
        assessment, view = _presented_view("changsheng_visible_support")
        del assessment["changsheng_segment_gate"]
        assessment["why_not_indeterminate"]["segment_gate"] = None
        with self.assertRaises(ValueError):
            public_strength_presentation(assessment, view)

    def test_changsheng_gate_not_jia(self):
        assessment, view = _presented_view("changsheng_visible_support")
        assessment["changsheng_segment_gate"]["gate_passed"] = False
        assessment["changsheng_segment_gate"]["gate_outcome"] = \
            "segment_not_jia"
        assessment["changsheng_segment_gate"]["segment_stem"] = "丙"
        assessment["changsheng_segment_gate"]["segment_index"] = 2
        with self.assertRaises(ValueError):
            public_strength_presentation(assessment, view)

    def test_metal_presented_is_forgery_by_construction(self):
        assessment, view = _synthetic_view(
            "庚", "酉", predicate_id="pure_support_metal",
            classification="strong", relation="same_element",
            root_presence=True,
            scope_conditions={"scope_condition_a": True})
        with self.assertRaises(ValueError):
            public_strength_presentation(assessment, view)

    def test_classification_flipped(self):
        assessment, view = _presented_view("isolated_control")
        assessment["classification"] = "strong"
        with self.assertRaises(ValueError):
            public_strength_presentation(assessment, view)

    def test_condition_fact_ref_outside_trace(self):
        assessment, view = _presented_view("pure_support")
        why = assessment["why_not_indeterminate"]
        why["conditions"][0]["fact_ref"] = "#/trace/9/output/x/y"
        with self.assertRaises(ValueError):
            public_strength_presentation(assessment, view)

    def test_scope_condition_false_in_effects(self):
        assessment, view = _presented_view("pure_support")
        view["trace"][3]["output"]["pure_support_scope_conditions"][
            "scope_condition_a"] = False
        view["trace"][3]["output"]["pure_support_scope_met"] = False
        with self.assertRaises(ValueError):
            public_strength_presentation(assessment, view)

    def test_research_flags_flipped(self):
        assessment, view = _presented_view("pure_support")
        assessment["public_enabled"] = True
        with self.assertRaises(ValueError):
            public_strength_presentation(assessment, view)

    def test_step_without_evidence(self):
        assessment, view = _synthetic_view(
            "甲", "卯", predicate_id="pure_support",
            classification="strong", relation="same_element",
            root_presence=True,
            scope_conditions={"scope_condition_a": True},
            drop_evidence="bazi.phase2.principal_month")
        with self.assertRaises(ValueError):
            public_strength_presentation(assessment, view)


class ValidatorTests(unittest.TestCase):
    def setUp(self):
        assessment, view = _presented_view("pure_support")
        self.valid = public_strength_presentation(assessment, view)

    def test_valid_passes(self):
        self.assertTrue(
            is_valid_public_strength_presentation(self.valid))

    def test_extra_key_fails(self):
        forged = copy.deepcopy(self.valid)
        forged["useful_god"] = "甲"
        self.assertFalse(is_valid_public_strength_presentation(forged))

    def test_statement_tampered_fails(self):
        forged = copy.deepcopy(self.valid)
        forged["statement"] = "身旺"
        self.assertFalse(is_valid_public_strength_presentation(forged))

    def test_segment_gate_on_non_changsheng_fails(self):
        forged = copy.deepcopy(self.valid)
        forged["segment_gate"] = {"pilot_variant": PILOT_VARIANT}
        self.assertFalse(is_valid_public_strength_presentation(forged))

    def test_metal_presented_fails(self):
        forged = copy.deepcopy(self.valid)
        forged["predicate_id"] = "pure_support_metal"
        self.assertFalse(is_valid_public_strength_presentation(forged))

    def test_not_judgeable_with_classification_fails(self):
        forged = {"variant": VARIANT, "status": "not_judgeable",
                  "day_master": "甲", "month_branch": "卯",
                  "scope_statement": SCOPE_STATEMENT,
                  "limitations": list(LIMITATIONS),
                  "reason": "no_predicate_matched",
                  "classification": "strong"}
        self.assertFalse(is_valid_public_strength_presentation(forged))

    def test_conflict_with_classification_fails(self):
        forged = {"variant": VARIANT, "status": "conflict",
                  "day_master": "丁", "month_branch": "巳",
                  "scope_statement": SCOPE_STATEMENT,
                  "limitations": list(LIMITATIONS),
                  "conflict_ids": ["x"], "blocker_reasons": ["y"],
                  "classification": "weak"}
        self.assertFalse(is_valid_public_strength_presentation(forged))


class ProjectionScopeTests(unittest.TestCase):
    def _envelope(self, scenario_id, presentation, container="result"):
        envelope = {
            "scenario_id": scenario_id,
            "status": "ok",
            "result": {},
            "evidence": {},
            "rule_matches": [],
            "trace": [],
        }
        envelope[container] = {
            "strength_presentation": presentation,
            "strength_assessment": {"variant": ADJUDICATION_VARIANT},
        }
        return envelope

    def setUp(self):
        assessment, view = _presented_view("pure_support")
        self.presentation = public_strength_presentation(assessment, view)
        self.assertTrue(
            is_valid_public_strength_presentation(self.presentation))

    def test_bazi_profile_release_is_verbatim(self):
        projected = project_execution(
            self._envelope("bazi-profile", self.presentation))
        self.assertEqual(projected["result"]["strength_presentation"],
                         self.presentation)
        # Projection does not strip assessment objects from result
        # containers (pinned main behavior, changsheng isolation
        # test); the Batch B guarantee is gate-side instead -- the
        # scenario gate never attaches strength_assessment to a
        # scenario result, pinned by the sealed equivalence test.
        self.assertEqual(projected["result"]["strength_assessment"],
                         {"variant": ADJUDICATION_VARIANT})

    def test_other_scenario_carrier_is_stripped(self):
        projected = project_execution(
            self._envelope("life-overview", self.presentation))
        self.assertNotIn("strength_presentation", projected["result"])

    def test_domain_chart_carrier_is_stripped(self):
        envelope = self._envelope("bazi-profile", self.presentation,
                                  container="chart")
        del envelope["scenario_id"]
        projected = project_execution(envelope)
        self.assertNotIn("strength_presentation", projected["chart"])
        self.assertNotIn("strength_presentation", projected["result"])

    def test_malformed_presentation_is_stripped(self):
        forged = copy.deepcopy(self.presentation)
        forged["statement"] = "身旺"
        projected = project_execution(
            self._envelope("bazi-profile", forged))
        self.assertNotIn("strength_presentation", projected["result"])


class ClientGateTests(unittest.TestCase):
    BIRTH = "1960-03-07T01:30:00+08:00"

    def test_strength_variant_keeps_baseline_refusal(self):
        with self.assertRaises(ValueError) as caught:
            execute_scenario("bazi-profile", {
                "value": self.BIRTH,
                "strength_variant": "bazi-strength-adjudication-v1"})
        self.assertEqual(
            str(caught.exception),
            "Bounded strength adjudication requires explicit research mode")

    def test_gate_is_server_side_only_by_source(self):
        # The gate builds its own inputs from the birth value alone;
        # no client-supplied strength_variant reaches it (the client
        # key is refused above before any gate runs).
        from pathlib import Path
        source = (Path(__file__).resolve().parents[1] / "src"
                  / "tianji_kb" / "scenario_engine.py").read_text(
                      encoding="utf-8")
        self.assertIn("_strength_public_gate", source)
        self.assertIn(
            'gate_inputs = {"value": value, "strength_variant": '
            "ADJUDICATION_VARIANT}",
            source)


if __name__ == "__main__":
    unittest.main()
