"""Dayun source collation: real fixed RAW and canonical, no invented source rules."""
import copy
import hashlib
import json
import unittest

from tianji_kb.bazi_dayun_source_audit import (
    ROOT, AUDIT_PATH, RAW_PATH, CANONICAL_PATH,
    validate_source_collation, verify_fixed_source_collation,
)


class FixedDayunSourceCollationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.audit = json.loads((ROOT / AUDIT_PATH).read_text(encoding="utf-8"))
        cls.raw = (ROOT / RAW_PATH).read_bytes()
        cls.canonical = (ROOT / CANONICAL_PATH).read_bytes()

    def test_real_fixed_source_and_canonical_unique_excerpt_alignment(self):
        outcome = verify_fixed_source_collation()
        self.assertEqual(outcome["verified_claim_count"], 5)
        self.assertEqual(outcome["review_status"],
                         "snapshot_collated_not_classical_method_adjudicated")
        self.assertEqual(outcome["source_sha256"], hashlib.sha256(self.raw).hexdigest())
        self.assertEqual(outcome["canonical_sha256"],
                         hashlib.sha256(self.canonical).hexdigest())
        self.assertFalse(outcome["canonical_method_adjudicated"])
        self.assertFalse(outcome["public_enabled"])
        self.assertFalse(outcome["ai_enabled"])
        self.assertEqual(outcome, validate_source_collation(
            self.audit, self.raw, self.canonical))

    def test_each_quote_is_in_actual_unmodified_raw_and_correct_canonical_section(self):
        raw = self.raw.decode("utf-8")
        sections = {s["id"]: s for s in json.loads(self.canonical)["sections"]}
        for claim in self.audit["claims"]:
            with self.subTest(claim=claim["claim_id"]):
                quote = claim["exact_excerpt"]
                at = claim["raw_char_offset"]
                self.assertEqual(raw[at:at+len(quote)], quote)
                self.assertEqual(raw.count(quote), 1)
                section = sections[claim["canonical_section_id"]]
                self.assertEqual(section["title"], claim["canonical_section_title"])
                self.assertEqual(section["text"].count(quote), 1)

    def test_any_modified_raw_or_canonical_bytes_fail_closed(self):
        for raw, canonical in (
            (self.raw + b" ", self.canonical),
            (self.raw, self.canonical + b" "),
            (self.raw.replace("今运就月上起".encode("utf-8"), b"invalid"), self.canonical),
        ):
            with self.subTest(raw_len=len(raw), canonical_len=len(canonical)):
                with self.assertRaisesRegex(ValueError, "digest drift"):
                    validate_source_collation(self.audit, raw, canonical)

    def test_reject_excerpt_fabrication_wrong_offset_and_section(self):
        for field, value in (
            ("exact_excerpt", "臆造三日折岁古文"),
            ("raw_char_offset", 0),
            ("canonical_section_id", 188),
            ("claim_id", "bazi.dayun.unreviewed_fake_promotion"),
        ):
            bad = copy.deepcopy(self.audit)
            bad["claims"][0][field] = value
            with self.subTest(field=field), self.assertRaisesRegex(ValueError, "integrity error"):
                validate_source_collation(bad, self.raw, self.canonical)

    def test_collation_cannot_promote_phase2_golden_ai_or_public_api(self):
        forbidden_changes = (
            ("phase1_rule_promotions", 1),
            ("phase2_rule_promotions", 1),
            ("new_golden_promotions", 1),
            ("public_enabled", True),
            ("ai_enabled", True),
            ("source_quotations_exposed_by_api", True),
        )
        for field, value in forbidden_changes:
            bad = copy.deepcopy(self.audit)
            bad["changes_to_release"][field] = value
            with self.subTest(field=field), self.assertRaisesRegex(ValueError, "cannot authorize release"):
                validate_source_collation(bad, self.raw, self.canonical)

    def test_baseline_source_and_rights_cannot_be_substituted(self):
        for field, value in (
            ("repository", "another/source"),
            ("commit", "latest"),
            ("license_policy", "UNREVIEWED"),
            ("raw_path", "../../secret.txt"),
            ("canonical_path", "fake.json"),
            ("raw_sha256", "0" * 64),
        ):
            bad = copy.deepcopy(self.audit)
            bad["baseline"][field] = value
            with self.subTest(field=field), self.assertRaises(ValueError):
                validate_source_collation(bad, self.raw, self.canonical)

    def test_traditional_role_phrase_is_grounded_but_cannot_authorize_direction(self):
        item = next(claim for claim in self.audit["claims"]
                    if claim["claim_id"] == "bazi.dayun.source.traditional-role-categories")
        self.assertEqual(item["canonical_section_id"], 188)
        self.assertIn("阴男阳女", item["exact_excerpt"])
        self.assertIn("阴女阳男", item["exact_excerpt"])
        self.assertIn("不独立证明大运顺逆", item["scope"])
        changed = copy.deepcopy(self.audit)
        target = next(x for x in changed["claims"]
                      if x["claim_id"] == "bazi.dayun.source.traditional-role-categories")
        target["scope"] = "这足以证明四种方向已经可以自动推断，不需要补充审校。"
        with self.assertRaisesRegex(ValueError, "direction inference"):
            validate_source_collation(changed, self.raw, self.canonical)

    def test_current_source_only_supports_bounded_method_facts(self):
        audit = self.audit
        self.assertEqual(audit["record_kind"], "source_fragment_alignment_not_executable_rule")
        self.assertGreaterEqual(len(audit["adjudication_gaps"]), 5)
        ids = {v["claim_id"] for v in audit["claims"]}
        self.assertEqual(ids, {
            "bazi.dayun.source.month-pillar-origin",
            "bazi.dayun.source.nominal-ten-year",
            "bazi.dayun.source.three-day-year",
            "bazi.dayun.source.no-universal-fortune",
            "bazi.dayun.source.traditional-role-categories",
        })
        self.assertIn("珞琭子", audit["inherited_source_distinction"])
        self.assertEqual(audit["changes_to_release"]["phase2_rule_promotions"], 0)


if __name__ == "__main__":
    unittest.main()
