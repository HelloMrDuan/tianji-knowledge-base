"""Public-data-safe B004 dream narrative parser regression.

Uses synthetic, non-classical scene aliases only to exercise parsing.
Does not assert EvidenceResolver, private Canonical, or actual interpretations:
those still require separate controlled knowledge acceptance.
"""
import unittest

from tianji_kb.operations.dream_knowledge import (
    _affirmed,
    _narrative_clauses,
    _scene_matches,
)

SNAKE = {"scene_aliases": ["被蛇咬"]}
MONEY = {"scene_aliases": ["捡到了钱"]}


def matched(text, term_id, attrs):
    return _scene_matches(term_id, attrs, _narrative_clauses(text))


class DreamPublicParserTests(unittest.TestCase):
    def test_self_report_bite_has_precise_span(self):
        text = "我梦见被蛇咬了"
        found = matched(text, "dream.term.snake", SNAKE)
        self.assertEqual(len(found), 1)
        span = found[0]["input_spans"][0]
        self.assertEqual(text[span["start"]:span["end"]], "被蛇咬")

    def test_negated_self_report_never_matches(self):
        for text in ("我没有梦见被蛇咬", "昨晚没梦见被蛇咬"):
            with self.subTest(text=text):
                self.assertEqual(matched(text, "dream.term.snake", SNAKE), [])

    def test_hypothetical_never_matches(self):
        for text in ("如果梦见被蛇咬了怎么办", "假如梦见被蛇咬"):
            with self.subTest(text=text):
                self.assertEqual(matched(text, "dream.term.snake", SNAKE), [])

    def test_reported_other_person_never_matches(self):
        for text in ("朋友说他梦见被蛇咬了", "听说别人梦见被蛇咬"):
            with self.subTest(text=text):
                self.assertEqual(matched(text, "dream.term.snake", SNAKE), [])

    def test_awakened_denial_invalidates_prior_scene(self):
        text = "我梦见被蛇咬了，醒来才发现没有发生"
        clauses = _narrative_clauses(text)
        self.assertGreaterEqual(len(clauses), 2)
        self.assertFalse(_affirmed(clauses, 0))
        self.assertEqual(_scene_matches("dream.term.snake", SNAKE, clauses), [])

    def test_two_independent_scenes_preserve_input_order(self):
        text = "我梦见我捡到了钱，接着我梦见被蛇咬了"
        clauses = _narrative_clauses(text)
        money = _scene_matches("dream.term.money", MONEY, clauses)
        snake = _scene_matches("dream.term.snake", SNAKE, clauses)
        self.assertEqual(len(money), 1)
        self.assertEqual(len(snake), 1)
        a = money[0]["input_spans"][0]
        b = snake[0]["input_spans"][0]
        self.assertLess(a["start"], b["start"])
        self.assertEqual(text[a["start"]:a["end"]], a["text"])
        self.assertEqual(text[b["start"]:b["end"]], b["text"])

    def test_temporal_connector_before_new_dream_is_accepted(self):
        text = "我梦见我捡到了钱，然后我梦见被蛇咬了"
        found = matched(text, "dream.term.snake", SNAKE)
        self.assertEqual(len(found), 1)
        self.assertEqual(found[0]["input_spans"][0]["text"], "被蛇咬")

    def test_entity_without_reviewed_scene_not_a_match(self):
        self.assertEqual(matched("我梦见蛇在走", "dream.term.snake", SNAKE), [])
        self.assertEqual(matched("我梦见龙在天上飞", "dream.term.snake", SNAKE), [])


if __name__ == "__main__":
    unittest.main()
