"""Replayed derived factors cannot be forged into a strength verdict."""
import copy
from types import SimpleNamespace
import unittest

from tianji_kb.bazi_adjudication import ADJUDICATION_VARIANT, strength_assessment
from tianji_kb.operations.bazi_chart import chart


class BoundedReplayedFactorTests(unittest.TestCase):
    def original(self):
        out = chart("癸卯", "乙卯", "甲子", "乙亥",
                    strength_variant=ADJUDICATION_VARIANT)
        self.assertFalse(out["result"]["strength_assessment"]["ai_enabled"])
        return out

    def replay(self, original, modify):
        steps = copy.deepcopy(original["trace"])
        observed = {s["rule_id"]: s for s in steps}
        modify(observed)
        trace = SimpleNamespace(
            steps=steps,
            evidence=copy.deepcopy(original["evidence"]),
            add=lambda *args, **kwargs: None,
        )
        return strength_assessment(trace, strength_variant=ADJUDICATION_VARIANT)

    def test_forged_month_relation_is_rejected_with_existing_evidence(self):
        source = self.original()
        assessed = self.replay(source, lambda rows: rows[
            "bazi.phase2.principal_month"]["output"].__setitem__(
                "relation", "controls_me"))
        self.assertEqual(assessed["classification"], "indeterminate")
        self.assertIn("derived_principal_replay_mismatch",
                      {b["reason"] for b in assessed["blockers"]})
        self.assertFalse(assessed["public_enabled"])
        self.assertFalse(assessed["ai_enabled"])

    def test_forged_root_availability_cannot_be_counted_as_effective(self):
        source = self.original()
        self.assertTrue(source["result"]["root_availability"]["roots"])

        def forged(rows):
            root = rows["bazi.phase2.root_availability"]["output"]["roots"][0]
            root["root_availability"] = (
                "conditional" if root["root_availability"] == "effective"
                else "effective")

        assessed = self.replay(source, forged)
        self.assertEqual(assessed["classification"], "indeterminate")
        self.assertIn("derived_root_availability_replay_mismatch",
                      {b["reason"] for b in assessed["blockers"]})
        self.assertFalse(assessed["full_strength_classifier_ready"])

    def test_unmodified_research_result_remains_evidence_bound(self):
        original = self.original()
        assessed = self.replay(original, lambda _: None)
        self.assertNotIn("derived_principal_replay_mismatch",
                         {b["reason"] for b in assessed["blockers"]})
        self.assertNotIn("derived_root_availability_replay_mismatch",
                         {b["reason"] for b in assessed["blockers"]})
        self.assertTrue(assessed["evidence_ids"])
        self.assertTrue(set(assessed["evidence_ids"]) <= set(original["evidence"]))
        self.assertFalse(assessed["public_enabled"])
        self.assertFalse(assessed["ai_enabled"])


if __name__ == "__main__":
    unittest.main()
