"""Liuyao limited useful-god framework foundation tests.

Foundation only (user adjudication 2026-11-17, Liuyao ask = B): the
taxonomy, structured input, evidence binding and abstention contract
exist; the useful-god mapping registry is EMPTY and no verdict is ever
produced. These tests are pure stdlib + the framework module, so they
run locally and in public CI without the sealed runtime.
"""
import unittest

from tianji_kb.liuyao_yongshen import (
    QUESTION_TYPES,
    USEFUL_GOD_MAPPINGS,
    assess,
    get_useful_god_mapping,
    list_question_types,
    validate_question_input,
)

GOOD_INPUT = {
    "question_type": "career",
    "yao_values": [7, 8, 7, 9, 8, 6],
    "value": "2000-01-07T12:00:00+08:00",
}

EXPECTED_TYPES = {
    "career",
    "wealth",
    "marriage",
    "health",
    "examination",
    "legal",
    "travel",
    "lost_property",
}


class QuestionTypeTaxonomyTests(unittest.TestCase):
    def test_taxonomy_is_fixed_and_complete(self):
        self.assertEqual(set(QUESTION_TYPES), EXPECTED_TYPES)
        self.assertEqual(len(QUESTION_TYPES), 8)

    def test_each_type_has_evidence(self):
        for type_id, record in QUESTION_TYPES.items():
            self.assertEqual(record["id"], type_id)
            self.assertTrue(isinstance(record["name"], str) and record["name"].strip())
            self.assertTrue(
                isinstance(record["description"], str) and record["description"].strip()
            )
            evidence = record["evidence"]
            # The citation is the registered chart variant the type rests
            # on (the computation that produces the six relatives), not a
            # mapping. The per-type classical passage is pending
            # registration through the governance chain.
            self.assertEqual(evidence["source"], "liuyao/jingfang-eight-palaces-v1")
            self.assertEqual(evidence["source_title"], "京房八宫")
            self.assertEqual(evidence["version"], "v1")
            self.assertTrue(
                isinstance(evidence["locator"], str) and evidence["locator"].strip()
            )
            self.assertIsNone(evidence["classical_citation"])
            self.assertEqual(evidence["status"], "framework_only")

    def test_relative_category_is_pending_review_for_all_types(self):
        # ChatGPT HOLD 2026-11-18: no six-relative grouping is approved
        # for any type yet (each classical_citation is still None), so
        # every type's relative_category must be None and its note must
        # say the grouping awaits per-item evidence review + separate
        # approval. No unapproved association may be pinned as a
        # contract.
        for type_id, record in QUESTION_TYPES.items():
            self.assertIsNone(record["relative_category"], msg=type_id)
            note = record["relative_category_note"]
            self.assertTrue(isinstance(note, str) and note.strip(), msg=type_id)
            self.assertIn("须待逐项证据审核与另行批准", note, msg=type_id)
            self.assertNotIn("归入", note, msg=type_id)

    def test_list_returns_a_copy(self):
        listed = list_question_types()
        self.assertEqual(set(listed), EXPECTED_TYPES)
        listed["career"]["name"] = "MUTATED"
        self.assertNotEqual(QUESTION_TYPES["career"]["name"], "MUTATED")


class StructuredInputValidationTests(unittest.TestCase):
    def test_valid_input_normalizes(self):
        normalized = validate_question_input(dict(GOOD_INPUT))
        self.assertEqual(normalized["question_type"], "career")
        self.assertEqual(normalized["yao_values"], [7, 8, 7, 9, 8, 6])
        self.assertEqual(normalized["value"], "2000-01-07T12:00:00+08:00")
        self.assertNotIn("zone", normalized)
        self.assertNotIn("traditional_role", normalized)

    def test_valid_input_with_optional_fields(self):
        data = dict(GOOD_INPUT, zone="Asia/Shanghai", traditional_role="female")
        normalized = validate_question_input(data)
        self.assertEqual(normalized["zone"], "Asia/Shanghai")
        self.assertEqual(normalized["traditional_role"], "female")

    def test_rejects_non_object(self):
        for bad in (None, [], "career", 42):
            with self.assertRaises(ValueError):
                validate_question_input(bad)

    def test_rejects_missing_or_unknown_question_type(self):
        data = dict(GOOD_INPUT)
        del data["question_type"]
        with self.assertRaises(ValueError):
            validate_question_input(data)
        with self.assertRaises(ValueError):
            validate_question_input(dict(GOOD_INPUT, question_type="lottery"))
        with self.assertRaises(ValueError):
            validate_question_input(dict(GOOD_INPUT, question_type=""))

    def test_rejects_bad_yao_values(self):
        bad_values = (
            None,
            [7, 8, 7],
            [7, 8, 7, 9, 8, 6, 7],
            [7, 8, 7, 9, 8, 5],
            [7, 8, 7, 9, 8, 10],
            [7, 8, 7, 9, 8, "6"],
            [7, 8, 7, 9, 8, True],
            "777777",
        )
        for bad in bad_values:
            with self.assertRaises(ValueError, msg=repr(bad)):
                validate_question_input(dict(GOOD_INPUT, yao_values=bad))

    def test_rejects_missing_or_bad_value(self):
        data = dict(GOOD_INPUT)
        del data["value"]
        with self.assertRaises(ValueError):
            validate_question_input(data)
        for bad in ("", "not-a-date", "2000-13-40T99:99:99", 20000107, None):
            with self.assertRaises(ValueError, msg=repr(bad)):
                validate_question_input(dict(GOOD_INPUT, value=bad))

    def test_rejects_bad_optional_fields(self):
        with self.assertRaises(ValueError):
            validate_question_input(dict(GOOD_INPUT, zone=""))
        with self.assertRaises(ValueError):
            validate_question_input(dict(GOOD_INPUT, zone=8))
        with self.assertRaises(ValueError):
            validate_question_input(dict(GOOD_INPUT, traditional_role="other"))
        with self.assertRaises(ValueError):
            validate_question_input(dict(GOOD_INPUT, traditional_role=""))

    def test_rejects_unknown_keys(self):
        with self.assertRaises(ValueError):
            validate_question_input(dict(GOOD_INPUT, extra_field="x"))

    def test_rejects_free_text_question(self):
        # The question text is page context only and must never be sent
        # to the engine. Each free-text field name is rejected with the
        # boundary message, not silently dropped.
        for field in ("question_text", "question", "text", "query"):
            with self.assertRaises(ValueError, msg=field):
                validate_question_input(dict(GOOD_INPUT, **{field: "会升职吗"}))


class AbstentionContractTests(unittest.TestCase):
    def test_all_types_abstain_pending_review(self):
        # Every type abstains with "ambiguous_category": no grouping is
        # approved for any type yet, so assess() never reaches a mapping
        # decision. No verdict, no useful god, ever.
        for type_id in EXPECTED_TYPES:
            result = assess(dict(GOOD_INPUT, question_type=type_id))
            self.assertEqual(result["status"], "abstained")
            self.assertEqual(result["reason"], "ambiguous_category")
            self.assertEqual(result["question_type"], type_id)
            self.assertIsNone(result["verdict"])
            self.assertIsNone(result["useful_god"])
            self.assertEqual(result["evidence_status"], "framework_only")
            self.assertEqual(
                result["evidence"]["source"], "liuyao/jingfang-eight-palaces-v1"
            )

    def test_ambiguous_type_still_abstains_when_role_is_given(self):
        # Even with a traditional_role, the foundation does not resolve
        # a gender/focus-dependent grouping: resolving it is a mapping
        # decision that needs separate approval.
        result = assess(
            dict(GOOD_INPUT, question_type="marriage", traditional_role="female")
        )
        self.assertEqual(result["status"], "abstained")
        self.assertEqual(result["reason"], "ambiguous_category")
        self.assertIsNone(result["useful_god"])

    def test_assess_rejects_invalid_input_instead_of_abstaining(self):
        with self.assertRaises(ValueError):
            assess(dict(GOOD_INPUT, question_type="lottery"))
        with self.assertRaises(ValueError):
            assess(dict(GOOD_INPUT, yao_values=[7, 7, 7]))
        with self.assertRaises(ValueError):
            assess(dict(GOOD_INPUT, question_text="会升职吗"))

    def test_assess_result_contains_no_verdict_language(self):
        for type_id in EXPECTED_TYPES:
            result = assess(dict(GOOD_INPUT, question_type=type_id))
            self.assertIsNone(result["verdict"])
            self.assertIsNone(result["useful_god"])
            for forbidden in ("用神", "旺衰", "应期", "成败", "吉凶"):
                self.assertNotIn(forbidden, str(result))


class MappingRegistryTests(unittest.TestCase):
    def test_registry_is_empty(self):
        self.assertEqual(USEFUL_GOD_MAPPINGS, {})
        self.assertEqual(len(USEFUL_GOD_MAPPINGS), 0)

    def test_no_mapping_is_applied_for_any_type(self):
        for type_id in EXPECTED_TYPES:
            self.assertIsNone(get_useful_god_mapping(type_id))
        self.assertIsNone(get_useful_god_mapping("lottery"))


if __name__ == "__main__":
    unittest.main()
