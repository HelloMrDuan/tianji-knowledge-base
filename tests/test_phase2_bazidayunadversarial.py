"""TJ-016.2: adversarial boundary cases -- real measurements, explicit
unresolved/refused statuses. No formal start age is ever produced, and a
birth exactly at a Jie instant never defaults the age to zero."""
import unittest
from datetime import datetime
from zoneinfo import ZoneInfo

import copy
import json
import os
from pathlib import Path

from tianji_kb.bazi_dayun_adversarial_cases import (
    _execute_tz_case,
    evaluate_adversarial_case,
    evaluate_boundary_conflict,
    evaluate_custom_probe,
    execute_adversarial_case,
    get_adversarial_case,
    list_adversarial_cases,
    refuse_age_counting_conversion,
)
from tianji_kb.bazi_calendar_precision_audit import audit_birth_instant

JIE = "2000-02-04T20:40:24+08:00"  # 立春, pinned provider instant


class RegistryTests(unittest.TestCase):
    def test_twelve_cases_registered_with_metadata(self):
        cases = list_adversarial_cases()
        self.assertEqual(len(cases), 12)
        ids = [c["case_id"] for c in cases]
        self.assertEqual(ids, ["ADV-%03d" % i for i in range(1, 13)])
        for c in cases:
            for field in ("case_id", "title", "timezone", "disputed_convention",
                          "expected_status", "unresolved_reason"):
                self.assertIn(field, c, field)
            self.assertIn(c["expected_status"],
                          ("unresolved", "refused", "fail_closed"))

    def test_unknown_case_rejected(self):
        with self.assertRaisesRegex(ValueError, "unknown adversarial case"):
            get_adversarial_case("ADV-999")


class ZeroDistanceTests(unittest.TestCase):
    def test_zero_distance_never_defaults_age_to_zero(self):
        # THE hard rule: birth exactly at the Jie instant, backward.
        r = evaluate_adversarial_case("ADV-001")
        self.assertEqual(r["arithmetic_fact"]["elapsed_seconds"], 0)
        self.assertTrue(r["arithmetic_fact"]["zero_distance"])
        self.assertIsNone(
            r["arithmetic_fact"]["symbolic_three_day_year_ratio"])
        self.assertEqual(r["arithmetic_fact"]["age_conversion_status"],
                         "zero_jie_boundary_convention_unreviewed")
        self.assertIsNone(r["start_age"])
        self.assertIsNone(r["handover_datetime"])
        self.assertEqual(r["jie_boundary"]["name"], "立春")
        self.assertEqual(r["expected_status"], "unresolved")

    def test_exact_jie_forward_selects_next_jie(self):
        r = evaluate_adversarial_case("ADV-002")
        self.assertEqual(r["arithmetic_fact"]["elapsed_seconds"], 2570536)
        self.assertFalse(r["arithmetic_fact"]["zero_distance"])
        self.assertEqual(r["jie_boundary"]["name"], "惊蛰")
        self.assertEqual(r["arithmetic_fact"]["symbolic_three_day_year_ratio"],
                         {"numerator": 321317, "denominator": 32400})
        self.assertIsNone(r["start_age"])

    def test_boundary_conflict_is_recorded_not_merged(self):
        c = evaluate_boundary_conflict(birth_instant=JIE)
        self.assertEqual(
            c["forward"]["arithmetic_fact"]["elapsed_seconds"], 2570536)
        self.assertEqual(
            c["backward"]["arithmetic_fact"]["elapsed_seconds"], 0)
        self.assertNotEqual(c["forward"]["jie_boundary"]["name"],
                            c["backward"]["jie_boundary"]["name"])
        self.assertIsNone(c["merged_conclusion"])
        self.assertEqual(c["conflict_status"], "unresolved")
        self.assertIsNone(c["start_age"])
        self.assertIsNone(c["handover_datetime"])


class SecondBoundaryTests(unittest.TestCase):
    def test_one_second_before_jie_forward(self):
        r = evaluate_adversarial_case("ADV-003")
        self.assertEqual(r["arithmetic_fact"]["elapsed_seconds"], 1)
        self.assertEqual(r["arithmetic_fact"]["symbolic_three_day_year_ratio"],
                         {"numerator": 1, "denominator": 259200})
        self.assertEqual(r["jie_boundary"]["name"], "立春")
        self.assertIsNone(r["start_age"])

    def test_one_second_after_jie_backward(self):
        r = evaluate_adversarial_case("ADV-004")
        self.assertEqual(r["arithmetic_fact"]["elapsed_seconds"], 1)
        self.assertEqual(r["jie_boundary"]["name"], "立春")
        self.assertIsNone(r["start_age"])

    def test_same_instant_direction_selects_different_jie(self):
        # 立春-1s: forward -> 立春 (1s); backward -> 小寒 (2547581s).
        fwd = evaluate_adversarial_case("ADV-003")
        bwd = evaluate_adversarial_case("ADV-005")
        self.assertEqual(fwd["birth_instant"], bwd["birth_instant"])
        self.assertNotEqual(fwd["jie_boundary"]["name"],
                            bwd["jie_boundary"]["name"])
        self.assertEqual(bwd["jie_boundary"]["name"], "小寒")
        self.assertEqual(bwd["arithmetic_fact"]["elapsed_seconds"], 2547581)
        self.assertIsNone(bwd["start_age"])


class RemainderTests(unittest.TestCase):
    def test_sub_day_remainder_unresolved(self):
        r = evaluate_adversarial_case("ADV-006")
        self.assertEqual(r["arithmetic_fact"]["elapsed_seconds"], 43200)
        self.assertEqual(r["arithmetic_fact"]["symbolic_three_day_year_ratio"],
                         {"numerator": 1, "denominator": 6})
        self.assertEqual(r["expected_status"], "unresolved")
        self.assertIsNone(r["start_age"])

    def test_sub_shichen_remainder_unresolved(self):
        # 1 hour < 1 时辰 (2h): no classical sub-shichen carry rule.
        r = evaluate_adversarial_case("ADV-007")
        self.assertEqual(r["arithmetic_fact"]["elapsed_seconds"], 3600)
        self.assertEqual(r["arithmetic_fact"]["symbolic_three_day_year_ratio"],
                         {"numerator": 1, "denominator": 72})
        self.assertEqual(r["expected_status"], "unresolved")
        self.assertIsNone(r["start_age"])


class AgeCountingTests(unittest.TestCase):
    def test_xusui_to_shisui_refused(self):
        with self.assertRaisesRegex(ValueError, "no sealed-canon"):
            refuse_age_counting_conversion("xusui", "shisui")

    def test_shisui_to_xusui_refused(self):
        with self.assertRaisesRegex(ValueError, "must not be defaulted"):
            refuse_age_counting_conversion("shisui", "xusui")

    def test_age_expression_confusion_refused(self):
        case = get_adversarial_case("ADV-009")
        self.assertEqual(case["expected_status"], "refused")
        with self.assertRaises(ValueError):
            refuse_age_counting_conversion("lichun-based", "chunjie-based")


class TimezoneAdversarialTests(unittest.TestCase):
    def test_nonexistent_civil_time_fail_closed(self):
        with self.assertRaisesRegex(ValueError, "does not exist"):
            audit_birth_instant("1986-05-04T02:30:00+08:00")

    def test_ambiguous_civil_time_named_zone_fail_closed(self):
        ambiguous = datetime(1986, 9, 14, 1, 30,
                             tzinfo=ZoneInfo("Asia/Shanghai"))
        with self.assertRaisesRegex(ValueError, "silent guess"):
            audit_birth_instant(ambiguous)

    def test_wrong_historical_offset_fail_closed(self):
        with self.assertRaisesRegex(ValueError, "contradicts tzdb"):
            audit_birth_instant("1988-07-01T12:00:00+08:00")


class ResultHonestyTests(unittest.TestCase):
    def test_measurement_cases_carry_all_required_fields(self):
        required = ("case_id", "birth_instant", "timezone", "jie_boundary",
                    "direction", "variant_id", "arithmetic_fact", "source_refs",
                    "disputed_convention", "expected_status",
                    "unresolved_reason")
        for case_id in ("ADV-001", "ADV-002", "ADV-003", "ADV-004",
                        "ADV-005", "ADV-006", "ADV-007"):
            with self.subTest(case=case_id):
                r = evaluate_adversarial_case(case_id)
                for field in required:
                    self.assertIn(field, r, field)
                self.assertIsNone(r["start_age"])
                self.assertIsNone(r["handover_datetime"])
                self.assertTrue(r["research_only"])
                self.assertFalse(r["public_enabled"])
                self.assertFalse(r["ai_enabled"])

    def test_evaluate_rejects_non_measurement_category(self):
        with self.assertRaisesRegex(ValueError, "not a measurement case"):
            evaluate_adversarial_case("ADV-008")
        with self.assertRaisesRegex(ValueError, "not a measurement case"):
            evaluate_adversarial_case("ADV-010")

    def test_unbound_classical_case_claims_no_verified_basis(self):
        r = evaluate_adversarial_case("ADV-003")
        self.assertFalse(r["evidence_bound"])
        self.assertEqual(r["variant_id"],
                         "classical-three-day-symbolic-ratio-v1")




def _real_bundle():
    from tianji_kb.bazi_dayun_source_audit import (
        ROOT, AUDIT_PATH, RAW_PATH, CANONICAL_PATH)
    base = Path(os.environ.get("TIANJI_TEST_ROOT", str(ROOT)))
    collation = json.loads((base / AUDIT_PATH).read_text(encoding="utf-8"))
    raw = (base / RAW_PATH).read_bytes()
    canonical = (base / CANONICAL_PATH).read_bytes()
    return {"collation": collation, "raw_bytes": raw,
            "canonical_bytes": canonical}


class IdentityBindingTests(unittest.TestCase):
    def test_adv001_direction_override_rejected(self):
        with self.assertRaisesRegex(ValueError, "disagrees with the registered"):
            execute_adversarial_case("ADV-001", direction="forward")

    def test_adv001_birth_override_rejected(self):
        with self.assertRaisesRegex(ValueError, "disagrees with the registered"):
            execute_adversarial_case("ADV-001",
                                     birth_instant="2000-02-04T20:40:23+08:00")

    def test_adv001_empty_birth_rejected_not_silently_replaced(self):
        with self.assertRaisesRegex(ValueError, "invalid override"):
            execute_adversarial_case("ADV-001", birth_instant="")

    def test_adv001_variant_override_rejected(self):
        with self.assertRaisesRegex(ValueError, "disagrees with the registered"):
            execute_adversarial_case(
                "ADV-001", variant_id="modern-mean-year-simulation-v1")

    def test_adv001_matching_override_allowed(self):
        r = execute_adversarial_case(
            "ADV-001", birth_instant=JIE, direction="backward",
            variant_id="classical-three-day-symbolic-ratio-v1")
        self.assertTrue(r["arithmetic_fact"]["zero_distance"])
        self.assertTrue(r["status_consistent"])

    def test_custom_probe_carries_no_case_identity(self):
        r = evaluate_custom_probe(birth_instant="2000-02-05T12:00:00+08:00",
                                  direction="forward",
                                  variant_id="classical-three-day-symbolic-ratio-v1")
        self.assertIsNone(r["case_id"])
        self.assertIsNone(r["expected_status"])
        self.assertEqual(r["entry"], "custom_probe")
        self.assertIsNone(r["start_age"])


class BoundaryImpersonationTests(unittest.TestCase):
    def test_non_jie_birth_cannot_impersonate_conflict(self):
        with self.assertRaisesRegex(ValueError, "not exactly a Jie instant"):
            evaluate_boundary_conflict(
                birth_instant="2000-02-05T12:00:00+08:00")

    def test_empty_birth_rejected(self):
        with self.assertRaisesRegex(ValueError, "birth_instant is required"):
            evaluate_boundary_conflict(birth_instant="")

    def test_true_jie_conflict_still_passes(self):
        c = evaluate_boundary_conflict(birth_instant=JIE)
        self.assertEqual(c["verified_jie"]["name"], "立春")
        self.assertEqual(c["verified_jie"]["at"], JIE)
        self.assertTrue(c["backward"]["arithmetic_fact"]["zero_distance"])
        self.assertIsNone(c["merged_conclusion"])
        self.assertEqual(c["conflict_status"], "unresolved")


class ExecutionCategoryTests(unittest.TestCase):
    def test_all_twelve_cases_have_real_execution_paths(self):
        expected = {
            "ADV-001": "measurement", "ADV-002": "measurement",
            "ADV-003": "measurement", "ADV-004": "measurement",
            "ADV-005": "measurement", "ADV-006": "measurement",
            "ADV-007": "measurement", "ADV-008": "refusal",
            "ADV-009": "refusal", "ADV-010": "tz_fail_closed",
            "ADV-011": "tz_fail_closed", "ADV-012": "tz_fail_closed",
        }
        for case_id, category in expected.items():
            with self.subTest(case=case_id):
                r = execute_adversarial_case(case_id)
                self.assertEqual(r["execution_category"], category)
                self.assertEqual(r["expected_status"], r["verified_status"])
                self.assertTrue(r["status_consistent"])
                self.assertIsNone(r["start_age"])
                self.assertIsNone(r["handover_datetime"])

    def test_refusal_results_carry_verified_trigger(self):
        for case_id in ("ADV-008", "ADV-009"):
            with self.subTest(case=case_id):
                r = execute_adversarial_case(case_id)
                self.assertEqual(r["error_category"], "age_counting_refused")
                self.assertIn("no sealed-canon", r["trigger"])

    def test_tz_results_carry_verified_trigger(self):
        triggers = {"ADV-010": "does not exist",
                    "ADV-011": "silent guess",
                    "ADV-012": "contradicts tzdb"}
        for case_id, trigger in triggers.items():
            with self.subTest(case=case_id):
                r = execute_adversarial_case(case_id)
                self.assertEqual(r["error_category"], "tz_fail_closed")
                self.assertIn(trigger, r["trigger"])

    def test_error_category_mismatch_is_not_swallowed(self):
        forged = dict(get_adversarial_case("ADV-010"))
        forged["error_must_contain"] = "this string is not in any error"
        with self.assertRaisesRegex(ValueError, "unexpected error category"):
            _execute_tz_case(forged)


class SourceTracingTests(unittest.TestCase):
    def test_unbound_result_source_refs_empty(self):
        r = execute_adversarial_case("ADV-003")
        self.assertFalse(r["evidence_bound"])
        self.assertEqual(r["source_refs"], [])

    def test_bound_source_refs_from_verified_evidence(self):
        r = execute_adversarial_case("ADV-003",
                                     evidence_bundle=_real_bundle())
        self.assertTrue(r["evidence_bound"])
        self.assertEqual(r["source_refs"], ["yuanhai_ziping_v1"])
        self.assertTrue(r["status_consistent"])

    def test_source_id_mismatch_rejected(self):
        with self.assertRaisesRegex(ValueError, "disagree"):
            execute_adversarial_case(
                "ADV-003", evidence_bundle=_real_bundle(),
                expected_source_refs=["forged-source"])

    def test_expected_source_match_accepted(self):
        r = execute_adversarial_case(
            "ADV-003", evidence_bundle=_real_bundle(),
            expected_source_refs=["yuanhai_ziping_v1"])
        self.assertEqual(r["source_refs"], ["yuanhai_ziping_v1"])


if __name__ == "__main__":
    unittest.main()
