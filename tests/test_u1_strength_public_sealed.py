"""U1 Batch B: real-execution strength-presentation tests (SEALED ONLY).

This file runs ONLY in the offline acceptance (assembled backend with
the sealed bundle), NEVER in public CI: it executes real bazi charts
through the production calendar chain, the real bounded assessment and
the real F4 pilot, and it must not be added to
.github/workflows/validate.yml. The public companion
``test_u1_strength_public_presentation.py`` covers the builder over
synthetic views in public CI; this file covers what only real
execution can prove.

Every chart below is replayed from its Golden ``source_birth`` through
``engine.execute`` and checked against the Golden ``expected_pillars``
-- no hand-built pillars anywhere. Two Golden expectation fields
predate the E0335 registration flips and are NOT asserted verbatim:
``golden_tj0112_bing_si_lu.json`` and
``golden_tj0112_s2_metal_water.json`` still record
``predicate_rule_registration: pending_phase1_rule_registration`` for
the lu and water predicates, while the live governance
(``bazi_registration_governance``) and the adjudication limitations
text record r032 / r034 as registered. This test asserts the CURRENT
registered state (r032 / r034), and notes the stale Golden field
rather than copying it.

Status mapping pinned here (see the builder docstring): a verdict
with no why and only the assessment's no-match marker
``outside_reviewed_sufficient_conditions`` is ``not_judgeable``; a
verdict with a blocking conflict id or any other blocker is
``conflict``; neither ever carries a classification.
"""

import copy
import json
import unittest
from pathlib import Path

from tianji_kb.bazi_adjudication import (
    ADJUDICATION_VARIANT,
    strength_assessment_changsheng,
)
from tianji_kb.bazi_siling_pilot import yin_siling_pilot
from tianji_kb.bazi_strength_public import (
    SCOPE_STATEMENT,
    STATEMENT,
    VARIANT,
    is_valid_public_strength_presentation,
    public_strength_presentation,
)
from tianji_kb.engine import execute
from tianji_kb.public_projection import project_execution
from tianji_kb.scenario_engine import (
    _strength_jie_facts,
    execute_scenario,
)

ROOT = Path(__file__).resolve().parents[1]
ZONE = "Asia/Shanghai"


def _golden(filename):
    return json.loads(
        (ROOT / "tests" / filename).read_text(encoding="utf-8"))


def _cases(filename):
    data = _golden(filename)
    cases = data["cases"]
    if isinstance(cases, dict):
        cases = list(cases.values())
    return {case["id"]: case for case in cases}


BING_WU = _cases("golden_tj0112_bing_wu_commanding.json")
BING_SI = _cases("golden_tj0112_bing_si_lu.json")
WOOD_HAI = _cases("golden_tj0112_wood_hai.json")
S2 = _cases("golden_tj0112_s2_metal_water.json")
BING_YIN = _cases("golden_tj0112_bing_yin_changsheng.json")
YIN_META = _golden("golden_tj0112_bing_yin_changsheng.json")["meta"]
YIN_WINDOWS = _golden("golden_tj0112_bing_yin_changsheng.json")["jie_windows"]
YIN_PROVIDER = _golden("golden_tj0112_bing_yin_changsheng.json")["provider"]

# (golden cases, predicate, classification, phase1 rule, phase2 step)
PRESENTED = [
    (WOOD_HAI["tj0112-regression-mao-pure-support"], "pure_support",
     "strong", None, "bazi.phase2.strength_pure_support"),
    (WOOD_HAI["tj0112-hai-positive-zhongqi-root"],
     "pure_generating_support", "strong", "bazi.rule.r029",
     "bazi.phase2.strength_pure_generating_support"),
    (WOOD_HAI["tj0112-regression-you-isolated-control"],
     "isolated_control", "weak", None,
     "bazi.phase2.strength_isolated_control"),
    (BING_WU["tj0112-bingwu-positive"], "commanding_visible_support",
     "strong", "bazi.rule.r030",
     "bazi.phase2.strength_commanding_visible_support"),
    (BING_SI["tj0112-bingsi-positive"], "lu_visible_support",
     "strong", "bazi.rule.r032",
     "bazi.phase2.strength_lu_visible_support"),
    (S2["tj0112-s2-water-positive-gui"],
     "pure_generating_support_water", "strong", "bazi.rule.r034",
     "bazi.phase2.strength_pure_generating_support_water"),
]


def _pillars(result):
    return [p["stem"]["value"] + p["branch"]["value"]
            for p in result["pillars"]]


def _gate_envelope(birth):
    return execute(
        "bazi", {"value": birth, "zone": ZONE,
                 "strength_variant": ADJUDICATION_VARIANT},
        allow_research=True)


def _presentation(envelope, assessment=None):
    if assessment is None:
        assessment = envelope["result"]["strength_assessment"]
    return public_strength_presentation(
        assessment,
        execution={
            "trace": envelope["trace"],
            "rule_matches": envelope["rule_matches"],
            "evidence": envelope["evidence"],
        })


def _scenario_presentation(birth, **extra):
    inputs = {"value": birth, "zone": ZONE}
    inputs.update(extra)
    envelope = execute_scenario("bazi-profile", inputs)
    return envelope, envelope["result"]["strength_presentation"]


def _jie_facts(window, **overrides):
    window_data = YIN_WINDOWS[window]
    facts = {"provider": dict(YIN_PROVIDER),
             "lichun": dict(window_data["lichun"]),
             "next_jie": dict(window_data["next_jie"])}
    facts.update(overrides)
    return facts


def _scan_no_research(obj, path=""):
    if isinstance(obj, dict):
        for key, value in obj.items():
            if key in ("strength_assessment", "useful_god",
                       "strength_factor_graph"):
                raise AssertionError("leaked key %s at %s" % (key, path))
            _scan_no_research(value, path + "/" + str(key))
    elif isinstance(obj, list):
        for index, value in enumerate(obj):
            _scan_no_research(value, "%s[%d]" % (path, index))
    elif isinstance(obj, str):
        for banned in ("身旺", "身弱"):
            if banned in obj:
                raise AssertionError(
                    "leaked value %s at %s" % (banned, path))


class PresentedSealedTests(unittest.TestCase):
    def test_all_triggerable_predicates_on_real_charts(self):
        for case, predicate_id, classification, phase1, phase2 in PRESENTED:
            with self.subTest(case=case["id"]):
                envelope = _gate_envelope(case["source_birth"])
                self.assertEqual(_pillars(envelope["result"]),
                                 case["expected_pillars"], case["id"])
                result = _presentation(envelope)
                self.assertTrue(
                    is_valid_public_strength_presentation(result),
                    case["id"])
                self.assertEqual(result["status"], "presented")
                self.assertEqual(result["statement"], STATEMENT)
                self.assertEqual(result["predicate_id"], predicate_id)
                self.assertEqual(result["classification"], classification)
                self.assertEqual(result["phase1_rule_id"], phase1)
                self.assertEqual(result["phase2_step_id"], phase2)
                self.assertEqual(result["scope_statement"], SCOPE_STATEMENT)
                self.assertTrue(all(c["met"] for c in result["conditions"]))
                self.assertTrue(result["evidence_ids"])
                self.assertTrue(result["source_ids"])

    def test_scenario_gate_presents_the_same_facts(self):
        for case, predicate_id, classification, _, _ in PRESENTED:
            with self.subTest(case=case["id"]):
                envelope, result = _scenario_presentation(
                    case["source_birth"])
                self.assertEqual(result["status"], "presented")
                self.assertEqual(result["predicate_id"], predicate_id)
                self.assertEqual(result["classification"], classification)
                self.assertTrue(
                    is_valid_public_strength_presentation(result))
                projected = project_execution(envelope)
                self.assertEqual(
                    projected["result"]["strength_presentation"], result)
                _scan_no_research(projected)

    def test_role_does_not_change_the_strength_fact(self):
        case = BING_WU["tj0112-bingwu-positive"]
        _, plain = _scenario_presentation(case["source_birth"])
        _, roled = _scenario_presentation(
            case["source_birth"], traditional_role="male")
        self.assertEqual(roled, plain)
        self.assertIn("dayun_presentation",
                      execute_scenario(
                          "bazi-profile",
                          {"value": case["source_birth"], "zone": ZONE,
                           "traditional_role": "male"})["result"])
        self.assertNotIn(
            "dayun_presentation",
            execute_scenario(
                "bazi-profile",
                {"value": case["source_birth"], "zone": ZONE})["result"])


class NearMissSealedTests(unittest.TestCase):
    def test_visible_wealth_veto_no_classification(self):
        case = BING_WU["tj0112-bingwu-counter-visible-wealth"]
        result = _presentation(_gate_envelope(case["source_birth"]))
        self.assertNotEqual(result["status"], "presented")
        self.assertNotIn("classification", result)
        self.assertTrue(is_valid_public_strength_presentation(result))

    def test_clashed_root_interaction_is_conflict(self):
        case = BING_WU["tj0112-bingwu-abstain-clashed-root"]
        result = _presentation(_gate_envelope(case["source_birth"]))
        self.assertEqual(result["status"], "conflict")
        self.assertIn("interaction_effect_unresolved",
                      result["blocker_reasons"])
        self.assertNotIn("classification", result)

    def test_month_not_hai_and_nonwood_day_master_no_classification(self):
        for case in (WOOD_HAI["tj0112-hai-counter-month-not-hai"],
                     WOOD_HAI["tj0112-hai-counter-nonwood-day-master"]):
            with self.subTest(case=case["id"]):
                result = _presentation(_gate_envelope(case["source_birth"]))
                self.assertNotEqual(result["status"], "presented")
                self.assertNotIn("classification", result)
                self.assertTrue(
                    is_valid_public_strength_presentation(result))

    def test_visible_drain_counter_no_classification(self):
        case = WOOD_HAI["tj0112-hai-counter-visible-drain"]
        result = _presentation(_gate_envelope(case["source_birth"]))
        self.assertNotEqual(result["status"], "presented")
        self.assertNotIn("classification", result)


class ConflictSealedTests(unittest.TestCase):
    def test_gui_hai_conflict_root_chart_is_conflict(self):
        case = S2["tj0112-s2-water-near-miss-gui-hai-pending-root"]
        self.assertEqual(case["source_birth"], "1981-12-21T22:30:00+08:00")
        result = _presentation(_gate_envelope(case["source_birth"]))
        self.assertEqual(result["status"], "conflict")
        self.assertIn("sanming-juan2.gui-changsheng",
                      result["conflict_ids"])
        self.assertNotIn("classification", result)

    def test_root_type_conflict_charts_are_conflict(self):
        for case in (WOOD_HAI["tj0112-hai-conflict-root-type-readings"],
                     BING_WU["tj0112-bingwu-conflict-xu-root-type"],
                     BING_SI["tj0112-bingsi-conflict-xu-root"]):
            with self.subTest(case=case["id"]):
                result = _presentation(_gate_envelope(case["source_birth"]))
                self.assertEqual(result["status"], "conflict")
                self.assertIn("bazi.concept.conflict_root_type_readings",
                              result["conflict_ids"])
                self.assertNotIn("classification", result)

    def test_ding_line_charts_never_present(self):
        for case in (BING_SI["tj0112-bingsi-ding-not-applicable"],
                     BING_WU["tj0112-bingwu-ding-not-applicable"]):
            with self.subTest(case=case["id"]):
                result = _presentation(_gate_envelope(case["source_birth"]))
                self.assertNotEqual(result["status"], "presented")
                self.assertNotIn("classification", result)
                self.assertTrue(
                    is_valid_public_strength_presentation(result))


class MetalSealedTests(unittest.TestCase):
    def test_no_metal_case_presents(self):
        metal_cases = [case for case in S2.values()
                       if "metal" in case["id"]]
        self.assertTrue(len(metal_cases) >= 2)
        for case in metal_cases:
            with self.subTest(case=case["id"]):
                envelope = _gate_envelope(case["source_birth"])
                self.assertEqual(
                    envelope["result"]["strength_assessment"]
                    ["classification"], "indeterminate", case["id"])
                result = _presentation(envelope)
                self.assertNotEqual(result["status"], "presented")
                self.assertNotIn("classification", result)

    def test_forged_metal_presentation_fails_closed(self):
        case = S2["tj0112-s2-metal-near-miss-xin-clashed-roots"]
        envelope = _gate_envelope(case["source_birth"])
        assessment = copy.deepcopy(
            envelope["result"]["strength_assessment"])
        effects = next(step["output"] for step in envelope["trace"]
                       if step["rule_id"] == "bazi.phase2.action_effects")
        effects_index = next(i for i, step in enumerate(envelope["trace"])
                             if step["rule_id"]
                             == "bazi.phase2.action_effects")
        scope_key = "pure_support_metal_scope_conditions"
        conditions = effects[scope_key]
        assessment["why_not_indeterminate"] = {
            "sufficient_rule": "bazi.phase2.strength_pure_support_metal",
            "conditions": [
                {"condition": name, "met": True,
                 "fact_ref": "#/trace/%d/output/%s/%s"
                 % (effects_index, scope_key, name),
                 "rule_id": "bazi.phase2.action_effects",
                 "evidence_ids": []}
                for name in conditions],
            "all_required_conditions_verified": True,
            "excluded_dependencies": ["dated_commander",
                                      "independent_hidden_effect_scores"],
        }
        assessment["classification"] = "strong"
        assessment["decision_status"] = "reviewed_sufficient_rule_matched"
        assessment["blockers"] = []
        assessment["conflict_ids"] = []
        with self.assertRaises(ValueError):
            public_strength_presentation(
                assessment,
                execution={
                    "trace": envelope["trace"],
                    "rule_matches": envelope["rule_matches"],
                    "evidence": envelope["evidence"],
                })


class F4SealedTests(unittest.TestCase):
    def test_jia_segment_presents_through_combined_path(self):
        case = BING_YIN["tj0112-bingyin-positive-jia-segment"]
        envelope = _gate_envelope(case["source_birth"])
        self.assertEqual(_pillars(envelope["result"]),
                         case["expected_pillars"])
        plain = envelope["result"]["strength_assessment"]
        self.assertEqual(plain["classification"], "indeterminate")
        pilot = yin_siling_pilot(
            case["source_birth"], version_id=YIN_META["pilot_version_id"],
            jie_facts=_jie_facts(case["window"]))
        self.assertEqual(pilot["status"], "computed")
        self.assertEqual(pilot["segment"]["stem"], "甲")
        combined = strength_assessment_changsheng(envelope, pilot)
        self.assertEqual(combined["classification"], "strong")
        self.assertEqual(combined["changsheng_segment_gate"]["gate_outcome"],
                         "segment_jia")
        result = _presentation(envelope, combined)
        self.assertEqual(result["status"], "presented")
        self.assertEqual(result["predicate_id"],
                         "changsheng_visible_support")
        self.assertIsNone(result["phase1_rule_id"])
        self.assertEqual(result["rule_registration"],
                         "pending_phase1_rule_registration")
        self.assertEqual(result["segment_gate"]["segment_stem"], "甲")
        self.assertTrue(is_valid_public_strength_presentation(result))

    def test_jia_segment_presents_through_scenario_gate(self):
        case = BING_YIN["tj0112-bingyin-positive-jia-segment"]
        _, result = _scenario_presentation(case["source_birth"])
        self.assertEqual(result["status"], "presented")
        self.assertEqual(result["predicate_id"],
                         "changsheng_visible_support")
        self.assertEqual(result["segment_gate"]["gate_outcome"],
                         "segment_jia")

    def test_wu_and_bing_segments_do_not_present(self):
        for case_id in ("tj0112-bingyin-gate-excluded-wu-segment",
                        "tj0112-bingyin-gate-excluded-bing-segment"):
            case = BING_YIN[case_id]
            with self.subTest(case=case_id):
                _, result = _scenario_presentation(case["source_birth"])
                self.assertEqual(result["status"], "not_judgeable")
                self.assertNotIn("classification", result)

    def test_missing_pilot_does_not_present(self):
        case = BING_YIN["tj0112-bingyin-positive-jia-segment"]
        envelope = _gate_envelope(case["source_birth"])
        combined = strength_assessment_changsheng(envelope, None)
        self.assertEqual(combined["classification"], "indeterminate")
        result = _presentation(envelope, combined)
        self.assertEqual(result["status"], "not_judgeable")

    def test_precision_warning_pilot_does_not_present(self):
        case = BING_YIN["tj0112-bingyin-positive-jia-segment"]
        envelope = _gate_envelope(case["source_birth"])
        facts = _jie_facts(case["window"], precision_warning=True)
        pilot = yin_siling_pilot(
            case["source_birth"], version_id=YIN_META["pilot_version_id"],
            jie_facts=facts)
        self.assertEqual(pilot["status"], "uncertain")
        combined = strength_assessment_changsheng(envelope, pilot)
        self.assertEqual(combined["classification"], "indeterminate")
        result = _presentation(envelope, combined)
        self.assertEqual(result["status"], "not_judgeable")


class TamperSealedTests(unittest.TestCase):
    def test_real_envelope_tamper_classes_fail_closed(self):
        case = BING_WU["tj0112-bingwu-positive"]
        envelope = _gate_envelope(case["source_birth"])
        execution = {
            "trace": envelope["trace"],
            "rule_matches": envelope["rule_matches"],
            "evidence": envelope["evidence"],
        }
        assessment = envelope["result"]["strength_assessment"]

        flipped = copy.deepcopy(assessment)
        flipped["classification"] = "weak"
        with self.assertRaises(ValueError):
            public_strength_presentation(flipped, copy.deepcopy(execution))

        drifted = copy.deepcopy(execution)
        drifted["trace"][0]["output"]["day_master"] = {"stem": "乙"}
        with self.assertRaises(ValueError):
            public_strength_presentation(
                copy.deepcopy(assessment), drifted)

        unmatched = copy.deepcopy(execution)
        unmatched["rule_matches"] = [
            m for m in unmatched["rule_matches"]
            if m["rule_id"] != "bazi.phase2.principal_month"]
        with self.assertRaises(ValueError):
            public_strength_presentation(
                copy.deepcopy(assessment), unmatched)

        ref_forged = copy.deepcopy(assessment)
        why = ref_forged["why_not_indeterminate"]
        why["conditions"][0]["fact_ref"] = "#/trace/0/output/forged"
        with self.assertRaises(ValueError):
            public_strength_presentation(
                ref_forged, copy.deepcopy(execution))


class EquivalenceAndLeakageSealedTests(unittest.TestCase):
    def test_xiyong_dayun_keys_unchanged_by_strength_gate(self):
        from tianji_kb.bazi_xiyong_public import public_xiyong_presentation
        from tianji_kb.scenario_engine import _xiyong_phase1_refs

        birth = BING_WU["tj0112-bingwu-positive"]["source_birth"]
        envelope = execute_scenario(
            "bazi-profile", {"value": birth, "zone": ZONE})
        result = envelope["result"]
        rebuilt = public_xiyong_presentation(
            result["tiaohou_assessment"], result["bingyao_assessment"],
            execution={
                "trace": envelope["trace"],
                "rule_matches": envelope["rule_matches"],
                "evidence": envelope["evidence"],
                "phase1_rule_refs": _xiyong_phase1_refs(),
            })
        self.assertEqual(result["xiyong_presentation"], rebuilt)
        self.assertNotIn("strength_assessment", result)
        self.assertNotIn("strength_factor_graph", result)

    def test_other_scenario_carries_no_strength_key(self):
        birth = BING_WU["tj0112-bingwu-positive"]["source_birth"]
        envelope = execute_scenario(
            "daily", {"birth_value": birth, "target_date": "2026-03-07"})
        self.assertNotIn("strength_presentation", envelope["result"])
        projected = project_execution(envelope)
        self.assertNotIn("strength_presentation",
                         json.dumps(projected, ensure_ascii=False))

    def test_jie_derivation_winter_offsets(self):
        # Winter Jie instants in the 1986-1991 DST window carry
        # +08:00 (no DST in February/March windows); summer +08:00
        # claims in that window are rejected by tzdb upstream and are
        # never derived here -- the gate only derives provider-table
        # winter instants.
        for birth in ("1988-02-10T12:00:00+08:00",
                      "1991-02-10T12:00:00+08:00"):
            facts = _strength_jie_facts(birth)
            self.assertTrue(facts["lichun"]["at"].endswith("+08:00"))
            self.assertTrue(facts["next_jie"]["at"].endswith("+08:00"))
            self.assertEqual(facts["lichun"]["term"], "立春")
            self.assertEqual(facts["next_jie"]["term"], "惊蛰")

    def test_public_files_carry_no_sealed_original_text(self):
        # The new public modules never embed classical original text:
        # the builder carries no original_text field, and the public
        # test's synthetic records use the placeholder 'fact'.
        builder = (ROOT / "src" / "tianji_kb"
                   / "bazi_strength_public.py").read_text(encoding="utf-8")
        self.assertNotIn("original_text", builder)
        public_test = (ROOT / "tests"
                       / "test_u1_strength_public_presentation.py"
                       ).read_text(encoding="utf-8")
        self.assertIn("SYNTHETIC", public_test)


if __name__ == "__main__":
    unittest.main()
