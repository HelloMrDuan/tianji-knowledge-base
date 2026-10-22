"""TJ-016.1: dayun conversion variants -- evidence-bound, independently
registered methods. Real pinned-provider measurements, real sealed evidence
(in private CI), real forgery rejections. No formal start ages, ever."""
import copy
import json
import os
import unittest
from datetime import datetime, timedelta
from pathlib import Path

from tianji_kb.bazi_dayun_age_fraction import THREE_DAYS
from tianji_kb.bazi_dayun_conversion_variants import (
    bind_variant_evidence,
    check_variant_evidence_match,
    convert_with_variant,
    get_variant,
    list_variants,
    release_variant,
    research_convert,
)
from tianji_kb.bazi_dayun_jie import adjacent_jie_distance
from tianji_kb.calendar import calendar

V1 = "classical-three-day-symbolic-ratio-v1"
V2 = "modern-mean-year-simulation-v1"


def _measure(days=0, hours=0, seconds=0):
    """Real pinned-provider jie measurement with an exact elapsed distance."""
    probe = adjacent_jie_distance(
        "2000-01-07T12:00:00+08:00", "forward",
        expected_month_ganzhi=calendar("2000-01-07T12:00:00+08:00")["month_ganzhi"])
    nxt = datetime.fromisoformat(probe["next_jie"]["at"])
    birth = (nxt - timedelta(days=days, hours=hours, seconds=seconds)).isoformat()
    return adjacent_jie_distance(
        birth, "forward",
        expected_month_ganzhi=calendar(birth)["month_ganzhi"])


def _real_bundle():
    from tianji_kb.bazi_dayun_source_audit import (
        ROOT, AUDIT_PATH, RAW_PATH, CANONICAL_PATH)
    base = Path(os.environ.get("TIANJI_TEST_ROOT", str(ROOT)))
    collation = json.loads((base / AUDIT_PATH).read_text(encoding="utf-8"))
    raw = (base / RAW_PATH).read_bytes()
    canonical = (base / CANONICAL_PATH).read_bytes()
    return collation, raw, canonical


class VariantRegistryTests(unittest.TestCase):
    REQUIRED_FIELDS = ("variant_id", "method_name", "source_refs",
                       "evidence_refs", "review_status", "input_unit",
                       "remainder_policy", "rounding_policy", "calendar_basis",
                       "applicable_scope", "unresolved_dependencies",
                       "public_enabled", "ai_enabled")

    def test_two_variants_registered_with_required_fields(self):
        variants = list_variants()
        self.assertEqual(len(variants), 2)
        ids = [v["variant_id"] for v in variants]
        self.assertEqual(ids, [V1, V2])
        for v in variants:
            for field in self.REQUIRED_FIELDS:
                self.assertIn(field, v, field)
            self.assertFalse(v["public_enabled"])
            self.assertFalse(v["ai_enabled"])
        # No fuzzy shared traditional_method label.
        names = [v["method_name"] for v in variants]
        self.assertNotIn("traditional_method", names)
        self.assertTrue(all(n != names[0] for n in names[1:]))

    def test_unknown_variant_rejected(self):
        with self.assertRaisesRegex(ValueError, "unknown conversion variant"):
            get_variant("classical-three-day-fantasy-v9")

    def test_classical_variant_evidence_points_to_sealed_quote(self):
        v1 = get_variant(V1)
        self.assertEqual(v1["evidence_refs"], ["bazi.dayun.source.three-day-year"])
        self.assertEqual(v1["review_status"], "research_candidate")
        self.assertEqual(v1["remainder_policy"], "unresolved")
        self.assertEqual(v1["rounding_policy"], "unresolved")
        self.assertIn("余日取整规则", " ".join(v1["unresolved_dependencies"]))

    def test_modern_variant_explicitly_not_classical(self):
        v2 = get_variant(V2)
        self.assertEqual(v2["review_status"], "modern_research_only_not_classical")
        self.assertEqual(v2["evidence_refs"], [])


class EvidenceBindingTests(unittest.TestCase):
    def test_real_evidence_binds_classical_variant(self):
        collation, raw, canonical = _real_bundle()
        bound = bind_variant_evidence(V1, collation=collation,
                                      raw_bytes=raw, canonical_bytes=canonical)
        self.assertEqual(bound["variant_id"], V1)
        self.assertEqual(len(bound["evidence_bound"]), 1)
        ev = bound["evidence_bound"][0]
        self.assertEqual(ev["claim_id"], "bazi.dayun.source.three-day-year")
        self.assertEqual(ev["source_id"], "yuanhai_ziping_v1")
        self.assertEqual(ev["canonical_section_id"], 188)
        self.assertEqual(ev["canonical_section_title"], "珞琭子消息赋")
        self.assertEqual(ev["exact_excerpt"], "折除乃三日为年")
        self.assertEqual(ev["raw_char_offset"], 55863)
        self.assertEqual(bound["collation_verified_claims"], 4)
        self.assertFalse(bound["canonical_method_adjudicated"])
        self.assertFalse(bound["public_enabled"])
        self.assertFalse(bound["ai_enabled"])
        self.assertIn("不规定余时舍入", ev["scope"])

    def test_forged_source_id_rejected(self):
        collation, raw, canonical = _real_bundle()
        forged = copy.deepcopy(collation)
        forged["claims"][2]["claim_id"] = "bazi.dayun.forged-source"
        with self.assertRaisesRegex(ValueError, "unknown or duplicated claim"):
            bind_variant_evidence(V1, collation=forged,
                                  raw_bytes=raw, canonical_bytes=canonical)

    def test_forged_section_id_rejected(self):
        collation, raw, canonical = _real_bundle()
        forged = copy.deepcopy(collation)
        forged["claims"][2]["canonical_section_id"] = 999
        with self.assertRaisesRegex(ValueError, "section locator drift"):
            bind_variant_evidence(V1, collation=forged,
                                  raw_bytes=raw, canonical_bytes=canonical)

    def test_forged_excerpt_rejected(self):
        collation, raw, canonical = _real_bundle()
        forged = copy.deepcopy(collation)
        forged["claims"][2]["exact_excerpt"] = "臆造三日折岁古文"
        with self.assertRaisesRegex(ValueError, "moved or altered"):
            bind_variant_evidence(V1, collation=forged,
                                  raw_bytes=raw, canonical_bytes=canonical)

    def test_tampered_source_sha_rejected(self):
        collation, raw, canonical = _real_bundle()
        with self.assertRaisesRegex(ValueError, "digest drift"):
            bind_variant_evidence(V1, collation=collation,
                                  raw_bytes=raw + b" ",
                                  canonical_bytes=canonical)

    def test_variant_evidence_mismatch_rejected(self):
        collation, raw, canonical = _real_bundle()
        month_claim = next(
            c for c in collation["claims"]
            if c["claim_id"] == "bazi.dayun.source.month-pillar-origin")
        with self.assertRaisesRegex(ValueError, "not evidence for variant"):
            check_variant_evidence_match(V1, month_claim)


class ConversionTests(unittest.TestCase):
    def test_exactly_three_days_precise_fraction(self):
        result = convert_with_variant(V1, _measure(days=3))
        self.assertEqual(result["elapsed_seconds"], THREE_DAYS)
        self.assertEqual(result["symbolic_years"], {"numerator": 1, "denominator": 1})
        self.assertEqual(result["remainder_seconds"], 0)
        self.assertEqual(result["remainder_resolution"]["status"], "no_remainder")
        self.assertIsNone(result["start_age"])
        self.assertIsNone(result["handover_datetime"])
        self.assertEqual(result["candidate_kind"], "symbolic_ratio")

    def test_sub_three_day_remainder_unresolved(self):
        result = convert_with_variant(V1, _measure(days=1))
        self.assertEqual(result["symbolic_years"], {"numerator": 1, "denominator": 3})
        self.assertEqual(result["remainder_seconds"], 86400)
        res = result["remainder_resolution"]
        self.assertEqual(res["status"], "unresolved")
        self.assertIn("gives no remainder rule", res["reason"])
        self.assertIsNone(result["start_age"])

    def test_sub_one_day_remainder_unresolved(self):
        result = convert_with_variant(V1, _measure(hours=12))
        self.assertEqual(result["symbolic_years"], {"numerator": 1, "denominator": 6})
        self.assertEqual(result["remainder_seconds"], 43200)
        self.assertEqual(result["remainder_resolution"]["status"], "unresolved")
        self.assertIsNone(result["start_age"])

    def test_one_second_remainder_unresolved(self):
        result = convert_with_variant(V1, _measure(seconds=1))
        self.assertEqual(result["symbolic_years"],
                         {"numerator": 1, "denominator": THREE_DAYS})
        self.assertEqual(result["remainder_seconds"], 1)
        self.assertEqual(result["remainder_resolution"]["status"], "unresolved")
        self.assertIsNone(result["start_age"])
        self.assertIsNone(result["handover_datetime"])

    def test_different_variants_preserve_difference(self):
        m = _measure(days=4)
        r1 = convert_with_variant(V1, m)
        r2 = convert_with_variant(V2, m)
        self.assertEqual(r1["candidate_kind"], "symbolic_ratio")
        self.assertEqual(r2["candidate_kind"], "modern_mean_year_interpretation")
        self.assertTrue(r1["classical_basis"])
        self.assertFalse(r2["classical_basis"])
        # Same arithmetic, different honest interpretations; kept distinct.
        self.assertEqual(r1["symbolic_years"], {"numerator": 4, "denominator": 3})
        self.assertEqual(r2["modern_years"], {"numerator": 4, "denominator": 3})
        self.assertNotEqual(r1["variant_id"], r2["variant_id"])
        combined = {"variants": [r1, r2]}
        self.assertEqual(len(combined["variants"]), 2)
        self.assertIsNone(r1["start_age"])
        self.assertIsNone(r2["start_age"])

    def test_unclear_rounding_returns_unresolved(self):
        for policy in ("half_up", "truncate", "ceil"):
            with self.subTest(policy=policy):
                result = convert_with_variant(V1, _measure(days=1), rounding=policy)
                self.assertEqual(result["status"], "unresolved")
                self.assertIn("no classical rounding rule", result["reason"])
                self.assertIsNone(result["start_age"])

    def test_tampered_jie_distance_rejected_by_replay(self):
        tampered = dict(_measure(days=1))
        tampered["elapsed_seconds"] = tampered["elapsed_seconds"] + 100
        with self.assertRaisesRegex(
                ValueError, "differs from pinned provider"):
            convert_with_variant(V1, tampered)

    def test_no_formal_start_age_or_handover(self):
        for variant_id in (V1, V2):
            with self.subTest(variant=variant_id):
                result = convert_with_variant(variant_id, _measure(days=2))
                self.assertIsNone(result["start_age"])
                self.assertIsNone(result["handover_datetime"])
                blob = json.dumps(result, ensure_ascii=False)
                self.assertNotIn("交运日期", blob)

    def test_no_modern_mean_year_in_classical_variant(self):
        r1 = convert_with_variant(V1, _measure(days=4))
        blob1 = json.dumps(r1, ensure_ascii=False)
        self.assertNotIn("365.2425", blob1)
        self.assertNotIn("mean_gregorian_year", blob1)
        self.assertNotIn("GREGORIAN_MEAN_YEAR", blob1)
        r2 = convert_with_variant(V2, _measure(days=4))
        self.assertFalse(r2["classical_basis"])
        self.assertIn("365.2425", r2["modern_model"])


class ResearchEntryTests(unittest.TestCase):
    def test_research_convert_requires_explicit_variant(self):
        with self.assertRaisesRegex(ValueError, "explicit variant_id is required"):
            research_convert(variant_id=None, measured_jie=_measure(days=1))
        with self.assertRaisesRegex(ValueError, "explicit variant_id is required"):
            research_convert(variant_id="", measured_jie=_measure(days=1))

    def test_research_rule_cannot_impersonate_adjudicated(self):
        with self.assertRaisesRegex(ValueError, "cannot be promoted"):
            release_variant(V1)
        with self.assertRaisesRegex(ValueError, "cannot be promoted"):
            release_variant(V2)
        self.assertNotEqual(get_variant(V1)["review_status"], "adjudicated")

    def test_research_convert_with_evidence_bundle(self):
        collation, raw, canonical = _real_bundle()
        result = research_convert(
            variant_id=V1, measured_jie=_measure(days=3),
            evidence_bundle={"collation": collation, "raw_bytes": raw,
                             "canonical_bytes": canonical})
        self.assertEqual(result["symbolic_years"], {"numerator": 1, "denominator": 1})
        self.assertIsNotNone(result["evidence_binding"])
        self.assertEqual(
            result["evidence_binding"]["evidence_bound"][0]["exact_excerpt"],
            "折除乃三日为年")
        self.assertTrue(result["research_only"])
        self.assertFalse(result["public_enabled"])
        self.assertFalse(result["ai_enabled"])
        self.assertIsNone(result["start_age"])

    def test_research_convert_unknown_variant_rejected(self):
        with self.assertRaisesRegex(ValueError, "unknown conversion variant"):
            research_convert(variant_id="made-up", measured_jie=_measure(days=1))


if __name__ == "__main__":
    unittest.main()
