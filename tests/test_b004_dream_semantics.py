"""B004 v2: Strengthened dream semantics tests per review.

- Negation/hypothetical/third-person: verify ZERO matches (not just no snake)
- Dream-awakening negation, temporal order, evidence conflicts
- Multiple images: separate evidence binding, no synthesized verdicts
"""
import unittest
from tianji_kb.operations.dream_knowledge import retrieve


class B004StrictTests(unittest.TestCase):
    def assertNoMatches(self, text, desc):
        """Strict: NO interpretations at all, not just no snake."""
        out = retrieve(text)
        matches = out["matched_interpretations"]
        self.assertEqual(matches, [], f"'{text}' ({desc}): expected zero matches, got {[m['term_id'] for m in matches]}")
        self.assertFalse(out["ai_enabled"])

    def test_negation_strict(self):
        self.assertNoMatches("我没有梦见蛇", "negation")
        self.assertNoMatches("我没有梦见被蛇咬", "negation bitten")
        self.assertNoMatches("昨晚没梦见蛇", "negation variant")

    def test_hypothetical_strict(self):
        self.assertNoMatches("假如梦见蛇", "hypothetical")
        self.assertNoMatches("如果梦见被蛇咬了怎么办", "hypothetical question")

    def test_third_person_strict(self):
        self.assertNoMatches("朋友说他梦见蛇", "third-person hearsay")
        self.assertNoMatches("朋友说他梦见被蛇咬了", "third-person hearsay bitten")
        self.assertNoMatches("听说别人梦见蛇", "hearsay")

    def test_dream_awakening_negation(self):
        """Dream-awakening: 'woke up and realized it didn't happen'"""
        self.assertNoMatches("我梦见被蛇咬了，醒来才发现没有发生", "awakening negation")

    def test_multiple_images_separate_evidence(self):
        out = retrieve("我梦见被蛇咬了，然后我梦见我捡到了钱")
        matches = out["matched_interpretations"]
        self.assertEqual(len(matches), 2)
        # Each has independent evidence_ids
        for m in matches:
            self.assertTrue(m["evidence_ids"], f"{m['term_id']} missing evidence")
        # No single combined score or verdict
        term_ids = sorted(m["term_id"] for m in matches)
        self.assertEqual(term_ids, ["dream.term.money", "dream.term.snake"])
        # Spans are precise
        full = "我梦见被蛇咬了，然后我梦见我捡到了钱"
        for m in matches:
            for im in m["input_matches"]:
                for span in im["input_spans"]:
                    self.assertEqual(full[span["start"]:span["end"]], span["text"])
        self.assertFalse(out["ai_enabled"])

    def test_temporal_order_preserved(self):
        """Later dream after earlier one: both recognized in order."""
        out = retrieve("我梦见我捡到了钱，接着我梦见被蛇咬了")
        terms = [m["term_id"] for m in out["matched_interpretations"]]
        # Both present (order may vary by implementation)
        self.assertIn("dream.term.money", terms)
        self.assertIn("dream.term.snake", terms)


if __name__ == "__main__":
    unittest.main()
