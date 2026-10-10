"""Independent first-person dreams may be recognized without leaking negation."""
import unittest
from tianji_kb.operations.dream_knowledge import retrieve


class DreamIndependentClauseTests(unittest.TestCase):
    def test_separate_temporal_new_dream_and_provenance(self):
        cases = (
            ("我梦见没有被蛇咬后来我梦见我捡到了钱",
             ["dream.term.money"]),
            ("我梦见被蛇咬了然后我梦见我没有捡到钱",
             ["dream.term.snake"]),
            ("我梦见我捡到了钱接着我又梦见我掉进井里",
             ["dream.term.falling", "dream.term.money"]),
            ("听说别人被蛇咬随后我梦见我飞向天空",
             ["dream.term.flying"]),
        )
        for narrative, terms in cases:
            with self.subTest(narrative=narrative):
                out = retrieve(narrative)
                matches = out["matched_interpretations"]
                self.assertEqual(sorted(m["term_id"] for m in matches), terms)
                for item in matches:
                    self.assertTrue(item["evidence_ids"])
                    self.assertTrue(all(eid in out["evidence"]
                                        for eid in item["evidence_ids"]))
                    for match in item["input_matches"]:
                        for span in match["input_spans"]:
                            self.assertEqual(narrative[span["start"]:span["end"]],
                                             span["text"])
                self.assertFalse(out["ai_enabled"])

    def test_explicit_another_dream_survives_contrast_with_denied_second_scene(self):
        cases = (
            ("我梦见被蛇咬了但是我又梦见我没有捡到钱",
             ["dream.term.snake"]),
            ("我梦见我捡到了钱可是我也梦见没有被蛇咬",
             ["dream.term.money"]),
            ("我梦见被蛇咬了但我梦见没有被蛇咬",
             []),
        )
        for narrative, expected in cases:
            with self.subTest(narrative=narrative):
                out = retrieve(narrative)
                self.assertEqual([m["term_id"] for m in out["matched_interpretations"]],
                                 expected)
                for item in out["matched_interpretations"]:
                    for match in item["input_matches"]:
                        for span in match["input_spans"]:
                            self.assertEqual(narrative[span["start"]:span["end"]],
                                             span["text"])
                self.assertFalse(out["ai_enabled"])

    def test_independent_self_dream_after_reported_context_resets_scope(self):
        cases = (
            ("听说别人被蛇咬随后我也梦见我捡到了钱", ["dream.term.money"]),
            ("听说别人被蛇咬然后梦见我飞向天空", ["dream.term.flying"]),
            ("听说别人被蛇咬不过我又梦见我捡到了钱", ["dream.term.money"]),
            ("听说别人被蛇咬随后我也梦见我没有捡到钱", []),
        )
        for narrative, expected in cases:
            with self.subTest(narrative=narrative):
                output = retrieve(narrative)
                self.assertEqual([row["term_id"] for row in output["matched_interpretations"]],
                                 expected)
                for row in output["matched_interpretations"]:
                    self.assertTrue(row["evidence_ids"])
                    for entry in row["input_matches"]:
                        for span in entry["input_spans"]:
                            self.assertEqual(narrative[span["start"]:span["end"]],
                                             span["text"])
                self.assertFalse(output["ai_enabled"])

    def test_explicit_mengdao_transition_is_independent_with_exact_span(self):
        cases = (
            ("听说别人被蛇咬随后我梦到我飞向天空", ["dream.term.flying"]),
            ("我梦到我没有被蛇咬后来我梦到我捡到了钱", ["dream.term.money"]),
            ("我梦见被蛇咬了但是我又梦到我没有捡到钱", ["dream.term.snake"]),
            ("我梦到我捡到了钱但我梦到没有捡到钱", []),
        )
        for narrative, expected in cases:
            with self.subTest(narrative=narrative):
                output = retrieve(narrative)
                self.assertEqual([m["term_id"] for m in output["matched_interpretations"]], expected)
                for item in output["matched_interpretations"]:
                    self.assertTrue(item["evidence_ids"])
                    for eid in item["evidence_ids"]:
                        self.assertIn(eid, output["evidence"])
                    for match in item["input_matches"]:
                        for span in match["input_spans"]:
                            self.assertEqual(narrative[span["start"]:span["end"]], span["text"])
                self.assertFalse(output["ai_enabled"])

    def test_mengdao_unreviewed_topic_after_reported_clause_has_no_interpretation(self):
        output = retrieve("听说别人被蛇咬随后我梦到我参加考试")
        self.assertEqual(output["matched_interpretations"], [])
        self.assertEqual(output["evidence"], {})
        self.assertEqual([t["label"] for t in output["unreviewed_input_topics"]], ["考试"])
        self.assertEqual(output["unreviewed_input_topics"][0]["evidence_ids"], [])
        self.assertFalse(output["ai_enabled"])

    def test_retractions_are_not_separate_new_dreams(self):
        for narrative in (
            "我梦见被蛇咬了然后发现其实没有发生",
            "我梦见我捡到了钱后来发现只是想象",
            "我梦见我捡到了钱其实是假的",
            "听说别人被蛇咬随后其实没有发生",
        ):
            with self.subTest(narrative=narrative):
                output = retrieve(narrative)
                self.assertEqual(output["matched_interpretations"], [])
                self.assertEqual(output["evidence"], {})


if __name__ == "__main__":
    unittest.main()
