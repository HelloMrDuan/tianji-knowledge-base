"""TJ-014.1: Dayun direction school matrix, evidence assessment, anti-forgery gate.

The four-quadrant direction table is a modern restoration candidate
(support class B). These tests verify, against the real frozen collation
constants in bazi_dayun_source_audit, that:
- the four quadrants still compute as research candidates;
- every matrix record is honestly classified and nothing is Phase2-allowed;
- collated classical fragments are never presented as direction proof;
- a candidate forged as classically approved / rule-matched / public is
  rejected by the fail-closed gate;
- the research direction feeding the month-pillar candidate sequence does
  not fabricate dates, handover ages, or fortune judgements.
"""
import copy
import unittest

from tianji_kb.bazi_dayun_direction import (
    COLLATION_ID,
    SUPPORT_CLASS_MODERN,
    VARIANT,
    school_matrix,
    traditional_direction,
    validate_direction_candidate,
)
from tianji_kb.bazi_dayun_sequence import candidate_sequence
from tianji_kb.bazi_dayun_source_audit import (
    EXPECTED_CLAIMS,
    REVIEW_STATUS,
    ROLE_APPENDIX_ID,
)


class QuadrantEvidenceTests(unittest.TestCase):
    """Four quadrants: real candidates, honestly labelled class B."""

    CASES = [
        ("庚辰", "male", "yang", "forward"),
        ("庚辰", "female", "yang", "backward"),
        ("辛巳", "male", "yin", "backward"),
        ("辛巳", "female", "yin", "forward"),
    ]

    def test_four_quadrants_with_evidence_assessment(self):
        for year, role, polarity, direction in self.CASES:
            with self.subTest(year=year, role=role):
                out = traditional_direction(year, traditional_role=role)
                self.assertEqual(out["variant"], VARIANT)
                self.assertEqual(out["year_stem_polarity"], polarity)
                self.assertEqual(out["direction"], direction)
                self.assertEqual(
                    out["traditional_role_selection"],
                    "explicit_historical_category_not_inferred_identity")
                self.assertFalse(out["classical_direction_evidence_approved"])
                self.assertIsNone(out["direction_rule_match"])
                self.assertIsNone(out["natal_year_stem_rule_id"])
                self.assertTrue(out["research_only"])
                self.assertFalse(out["public_enabled"])
                self.assertFalse(out["ai_enabled"])
                assessment = out["evidence_assessment"]
                self.assertEqual(assessment["support_class"], SUPPORT_CLASS_MODERN)
                self.assertEqual(
                    assessment["direction_rule_classical_collation"], "not_collated")
                self.assertEqual(assessment["collation_id"], COLLATION_ID)
                self.assertEqual(
                    assessment["collation_review_status"], REVIEW_STATUS)
                self.assertEqual(
                    assessment["related_collated_claim_ids"],
                    sorted(EXPECTED_CLAIMS))
                self.assertFalse(assessment["related_claims_prove_direction"])
                self.assertEqual(
                    assessment["role_terminology_appendix_id"], ROLE_APPENDIX_ID)
                self.assertIn(
                    "sanming_tonghui_full_text_quarantine_no_canonical_dayun_section",
                    assessment["unresolved_disputes"])
                self.assertTrue(validate_direction_candidate(out))

    def test_missing_or_illegal_role_rejected(self):
        for bad_role in (None, "", "other", "未知", True, 1, [], {}):
            with self.subTest(role=bad_role):
                with self.assertRaises(ValueError):
                    traditional_direction("庚辰", traditional_role=bad_role)

    def test_invalid_ganzhi_rejected(self):
        for bad_year in ("甲丑", "bad", "", None, 123):
            with self.subTest(year=bad_year):
                with self.assertRaises(ValueError):
                    traditional_direction(bad_year, traditional_role="male")


class SchoolMatrixTests(unittest.TestCase):
    """The matrix mirrors the real frozen collation; nothing is promoted."""

    def setUp(self):
        self.records = school_matrix()
        self.by_id = {r["record_id"]: r for r in self.records}

    def test_matrix_covers_all_real_sources(self):
        expected_ids = {
            "collated-month-pillar-origin",
            "collated-nominal-ten-year",
            "collated-three-day-year",
            "collated-no-universal-fortune",
            "collated-role-terminology-appendix",
            "modern-four-quadrant-candidate",
            "external-witness-lun-qi-dayun-fa",
            "sanming-tonghui-quarantine",
        }
        self.assertEqual(set(self.by_id), expected_ids)

    def test_no_record_is_phase2_allowed(self):
        for record in self.records:
            with self.subTest(record=record["record_id"]):
                self.assertFalse(record["phase2_allowed"])

    def test_collated_fragments_match_frozen_collation(self):
        for claim_id, (section_id, title) in EXPECTED_CLAIMS.items():
            record = next(
                r for r in self.records if r.get("claim_id") == claim_id)
            with self.subTest(claim=claim_id):
                self.assertEqual(record["section_id"], section_id)
                self.assertEqual(record["section_title"], title)
                self.assertEqual(record["source_id"], "bazi.source.yuanhai")
                self.assertEqual(
                    record["support_class"], "A_classical_collated_fragment")
                self.assertEqual(record["direction_support"], "none")
                self.assertIsNone(record["direction_candidate"])
                self.assertEqual(record["collation_id"], COLLATION_ID)

    def test_role_terminology_record_is_not_direction_proof(self):
        record = self.by_id["collated-role-terminology-appendix"]
        self.assertEqual(
            record["claim_id"], "bazi.dayun.source.traditional-role-categories")
        self.assertEqual(record["appendix_id"], ROLE_APPENDIX_ID)
        self.assertEqual(
            record["direction_support"], "terminology_only_not_direction_proof")
        self.assertIsNone(record["direction_candidate"])

    def test_modern_candidate_record_is_class_b(self):
        record = self.by_id["modern-four-quadrant-candidate"]
        self.assertEqual(record["support_class"], SUPPORT_CLASS_MODERN)
        self.assertIsNone(record["source_id"])
        self.assertIsNone(record["claim_id"])
        self.assertEqual(record["direction_candidate"], {
            "yang_male": "forward", "yang_female": "backward",
            "yin_male": "backward", "yin_female": "forward",
        })
        self.assertIn(
            "direction_wording_conflict_unresolved", record["conflicts"])

    def test_low_grade_records_cannot_adjudicate(self):
        witness = self.by_id["external-witness-lun-qi-dayun-fa"]
        self.assertEqual(
            witness["support_class"], "D_external_transcription_located_only")
        self.assertEqual(witness["direction_support"], "none")
        sanming = self.by_id["sanming-tonghui-quarantine"]
        self.assertEqual(sanming["source_id"], "bazi.source.sanming-xianchi-niutrans")
        self.assertEqual(sanming["direction_support"], "none")
        self.assertIsNone(sanming["section_id"])


class AntiForgeryGateTests(unittest.TestCase):
    """Forged promotions and tampered candidates must fail the gate."""

    def setUp(self):
        self.real = traditional_direction("庚辰", traditional_role="male")

    def test_real_candidate_passes(self):
        self.assertTrue(validate_direction_candidate(copy.deepcopy(self.real)))

    def test_forged_classical_approval_rejected(self):
        forged = copy.deepcopy(self.real)
        forged["classical_direction_evidence_approved"] = True
        with self.assertRaises(ValueError):
            validate_direction_candidate(forged)

    def test_forged_rule_match_rejected(self):
        forged = copy.deepcopy(self.real)
        forged["direction_rule_match"] = "bazi.phase2.dayun_direction"
        with self.assertRaises(ValueError):
            validate_direction_candidate(forged)

    def test_forged_rule_id_rejected(self):
        forged = copy.deepcopy(self.real)
        forged["natal_year_stem_rule_id"] = "bazi.rule.r999"
        with self.assertRaises(ValueError):
            validate_direction_candidate(forged)

    def test_upgraded_support_class_rejected(self):
        forged = copy.deepcopy(self.real)
        forged["evidence_assessment"]["support_class"] = "A_classical_collated"
        with self.assertRaises(ValueError):
            validate_direction_candidate(forged)

    def test_forged_collation_status_rejected(self):
        forged = copy.deepcopy(self.real)
        forged["evidence_assessment"]["direction_rule_classical_collation"] = "collated"
        with self.assertRaises(ValueError):
            validate_direction_candidate(forged)

    def test_claims_presented_as_direction_proof_rejected(self):
        forged = copy.deepcopy(self.real)
        forged["evidence_assessment"]["related_claims_prove_direction"] = True
        with self.assertRaises(ValueError):
            validate_direction_candidate(forged)

    def test_tampered_direction_rejected(self):
        forged = copy.deepcopy(self.real)
        forged["direction"] = "backward"
        with self.assertRaises(ValueError):
            validate_direction_candidate(forged)

    def test_tampered_polarity_rejected(self):
        forged = copy.deepcopy(self.real)
        forged["year_stem_polarity"] = "yin"
        with self.assertRaises(ValueError):
            validate_direction_candidate(forged)

    def test_public_or_ai_enablement_rejected(self):
        for field in ("public_enabled", "ai_enabled"):
            forged = copy.deepcopy(self.real)
            forged[field] = True
            with self.subTest(field=field):
                with self.assertRaises(ValueError):
                    validate_direction_candidate(forged)

    def test_unknown_variant_rejected(self):
        forged = copy.deepcopy(self.real)
        forged["variant"] = "bazi-dayun-approved-v9"
        with self.assertRaises(ValueError):
            validate_direction_candidate(forged)

    def test_upgraded_source_level_rejected(self):
        forged = copy.deepcopy(self.real)
        forged["source_reference"]["level"] = "classical_evidence"
        with self.assertRaises(ValueError):
            validate_direction_candidate(forged)


class SequenceAssociationTests(unittest.TestCase):
    """Research direction in the candidate sequence: no dates, no fortune."""

    def test_sequence_keeps_research_boundaries(self):
        direction = traditional_direction("庚辰", traditional_role="male")
        self.assertEqual(direction["direction"], "forward")
        seq = candidate_sequence("己丑", "甲", direction="forward", periods=3)
        self.assertEqual(
            seq["direction_origin"], "explicit_caller_selection_only")
        self.assertFalse(seq["direction_from_natal_attributes_calculated"])
        self.assertFalse(seq["start_age_calculated"])
        self.assertFalse(seq["handover_dates_calculated"])
        self.assertTrue(seq["research_only"])
        self.assertFalse(seq["public_enabled"])
        self.assertFalse(seq["ai_enabled"])
        self.assertEqual(len(seq["rows"]), 3)
        for row in seq["rows"]:
            self.assertIsNone(row["start_date"])
            self.assertIsNone(row["end_date"])
            self.assertIsNone(row["start_age"])
            self.assertIsNone(row["end_age"])
            self.assertIsNone(row["luck_assessment"])
            self.assertIsNone(row["natal_interaction"])
        ganzhi_seq = [row["candidate_ganzhi"] for row in seq["rows"]]
        self.assertEqual(ganzhi_seq, ["庚寅", "辛卯", "壬辰"])

    def test_sequence_rejects_invalid_direction(self):
        for bad in ("auto", "", None, True, "FORWARD"):
            with self.subTest(direction=bad):
                with self.assertRaises(ValueError):
                    candidate_sequence("己丑", "甲", direction=bad, periods=3)


if __name__ == "__main__":
    unittest.main()
