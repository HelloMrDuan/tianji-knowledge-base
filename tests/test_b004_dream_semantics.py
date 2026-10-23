"""B004: Lock in user-specified dream semantics cases (TJ-020.1/020.2/020.3).

These are the exact phrasings from the product requirements. The implementation
already handles them; these tests prevent regression.
"""
import unittest
from tianji_kb.operations.dream_knowledge import retrieve


class B004DreamSemanticsTests(unittest.TestCase):
    def assertSnake(self, text, should_match):
        out = retrieve(text)
        matches = [m["term_id"] for m in out["matched_interpretations"]]
        has_snake = "dream.term.snake" in matches
        self.assertEqual(has_snake, should_match,
                         f"'{text}': snake={has_snake}, expected {should_match}")
        # Spans must precisely match input
        for m in out["matched_interpretations"]:
            for im in m["input_matches"]:
                for span in im["input_spans"]:
                    self.assertEqual(text[span["start"]:span["end"]], span["text"])
        # AI must never be enabled
        self.assertFalse(out["ai_enabled"])

    def test_first_person_affirmed(self):
        """我梦见被蛇咬了 -> match (TJ-020.1)"""
        self.assertSnake("我梦见被蛇咬了", True)

    def test_third_person_hearsay_rejected(self):
        """朋友说他梦见蛇 -> no match (TJ-020.1: subject distinction)"""
        self.assertSnake("朋友说他梦见蛇", False)
        self.assertSnake("朋友说他梦见被蛇咬了", False)

    def test_negation_rejected(self):
        """我没有梦见蛇 -> no match (TJ-020.2)"""
        self.assertSnake("我没有梦见蛇", False)
        self.assertSnake("我没有梦见被蛇咬", False)

    def test_hypothetical_rejected(self):
        """假如梦见蛇 -> no match (TJ-020.2)"""
        self.assertSnake("假如梦见蛇", False)
        self.assertSnake("如果梦见被蛇咬", False)

    def test_multiple_images_separated(self):
        """Multiple images recognized separately, no synthesized verdict (TJ-020.3)"""
        out = retrieve("我梦见被蛇咬了，然后我梦见我捡到了钱")
        terms = sorted(m["term_id"] for m in out["matched_interpretations"])
        self.assertEqual(terms, ["dream.term.money", "dream.term.snake"])
        # Each match must have independent evidence, not a combined score
        for m in out["matched_interpretations"]:
            self.assertTrue(m["evidence_ids"])
        self.assertFalse(out["ai_enabled"])


if __name__ == "__main__":
    unittest.main()
