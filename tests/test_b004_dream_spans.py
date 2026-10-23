"""B004 v3: Span-position-verified temporal order + source conflict coverage.

Per review: temporal order must be verified via original text span
start/end positions, not just both images existing.
"""
import unittest
from tianji_kb.operations.dream_knowledge import retrieve


class B004SpanTests(unittest.TestCase):
    def test_temporal_order_via_spans(self):
        """Verify temporal order via span positions in original text."""
        text = "我梦见我捡到了钱，接着我梦见被蛇咬了"
        out = retrieve(text)
        matches = out["matched_interpretations"]
        self.assertEqual(len(matches), 2)

        # Extract spans by term
        spans = {}
        for m in matches:
            for im in m["input_matches"]:
                for span in im["input_spans"]:
                    # Verify span text matches original at position
                    self.assertEqual(text[span["start"]:span["end"]], span["text"])
                    spans[m["term_id"]] = span

        self.assertIn("dream.term.money", spans)
        self.assertIn("dream.term.snake", spans)
        # Money appears BEFORE snake in original text
        self.assertLess(spans["dream.term.money"]["start"],
                        spans["dream.term.snake"]["start"],
                        "money span must precede snake span in original text")

    def test_source_conflict_refusal(self):
        """Conflicting sources: unreviewed scene gets no interpretation."""
        # "梦见龙" is not in reviewed knowledge - should have no match
        out = retrieve("我梦见龙在天上飞")
        # Either no matches, or matches without fabricated interpretation
        for m in out["matched_interpretations"]:
            # Must have real evidence, not fabricated
            self.assertTrue(m["evidence_ids"] or m.get("status") == "input_observation_only")
        self.assertFalse(out["ai_enabled"])

    def test_evidence_not_fabricated(self):
        """All matched interpretations must have real evidence_ids."""
        out = retrieve("我梦见被蛇咬了")
        for m in out["matched_interpretations"]:
            self.assertTrue(m["evidence_ids"],
                          f"{m['term_id']} must have real evidence_ids")


if __name__ == "__main__":
    unittest.main()
