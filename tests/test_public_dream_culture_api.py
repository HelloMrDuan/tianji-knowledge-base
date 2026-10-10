"""Public cultural dream lookup: real reviewed knowledge, minimal projection, no mocks."""
import unittest

from fastapi.testclient import TestClient

from tianji_kb.api import create_app

PUBLIC = "/api/v1/dream/culture"
ADMIN = "/api/v1/admin/research/dream"


class PublicDreamCultureTests(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(create_app(admin_read_token="private-review-secret"))

    def test_reviewed_scene_is_public_and_safely_projected(self):
        response = self.client.post(PUBLIC, json={"dream_text": "我梦见被蛇咬了"})
        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(response.headers["cache-control"], "no-store")
        data = response.json()
        self.assertEqual(data["status"], "reviewed_cultural_matches")
        self.assertTrue(data["public_release"])
        self.assertTrue(data["cultural_reference_only"])
        self.assertFalse(data["ai_enabled"])
        self.assertFalse(data["personal_prediction"])
        self.assertEqual(len(data["matches"]), 1)
        match = data["matches"][0]
        self.assertIn("蛇咬人", match["short_quote"])
        self.assertEqual(match["evidence_level"], "C")
        self.assertEqual(set(match), {"scene", "matched_texts", "cultural_reading", "short_quote",
                                      "source_title", "evidence_level"})
        # Never leak internal RAG traces, repository paths or privileged metadata.
        for key in ("evidence", "retrieval", "canonical_path", "rule_id", "term_id",
                    "input_spans", "entities", "trace", "token", "dream_text"):
            self.assertNotIn(key, data)
            self.assertNotIn(key, match)
        self.assertNotIn("data/canonical/", response.text)
        self.assertNotIn("private-review-secret", response.text)

    def test_no_interpretation_when_absent_negated_reported_or_hypothetical(self):
        for dream in ("梦见考试", "梦见没有被蛇咬", "梦见电影里被蛇咬了",
                      "我担心会被蛇咬"):
            with self.subTest(dream=dream):
                response = self.client.post(PUBLIC, json={"dream_text": dream})
                self.assertEqual(response.status_code, 200, response.text)
                data = response.json()
                self.assertEqual(data["status"], "no_reviewed_interpretation")
                self.assertEqual(data["matches"], [])
                self.assertFalse(data["ai_enabled"])

    def test_public_mixed_dream_only_displays_new_affirmed_reviewed_scene(self):
        narrative = '我梦见没有被蛇咬但我梦见我捡到了钱'
        response = self.client.post(PUBLIC, json={'dream_text': narrative})
        self.assertEqual(response.status_code, 200, response.text)
        payload = response.json()
        self.assertEqual(payload['status'], 'reviewed_cultural_matches')
        self.assertEqual(len(payload['matches']), 1)
        self.assertIn('拾得钱物皆大吉', payload['matches'][0]['short_quote'])
        self.assertNotIn('蛇咬人主得大财', response.text)
        for forbidden in ('rule_id', 'term_id', 'canonical_path', 'input_spans', 'retrieval'):
            self.assertNotIn(forbidden, response.text)
        self.assertFalse(payload['ai_enabled'])

    def test_unreviewed_subjects_and_reviewed_scene_are_distinct_in_real_api(self):
        cases = (
            ("梦见考试", [], [("考试", "梦见考试")]),
            ("我梦见自己怀孕", [], [("怀孕", "梦见自己怀孕")]),
            ("梦见我结婚", [], [("结婚", "梦见我结婚")]),
            ("梦到我去参加面试", [], [("工作", "梦到我去参加面试")]),
            ("我梦见我捡到了钱，后来梦见考试",
             ["拾得钱物皆大吉"], [("考试", "梦见考试")]),
            ("听说别人梦见考试", [], []),
            ("梦见没有参加考试", [], []),
        )
        for narrative, excerpts, expected_topics in cases:
            with self.subTest(narrative=narrative):
                response = self.client.post(PUBLIC, json={"dream_text": narrative})
                self.assertEqual(response.status_code, 200, response.text)
                data = response.json()
                self.assertEqual([x["short_quote"] for x in data["matches"]], excerpts)
                self.assertEqual(
                    [(x["label"], x["matched_texts"][0]) for x in data["unreviewed_topics"]],
                    expected_topics)
                self.assertFalse(data["ai_enabled"])
                self.assertFalse(data["personal_prediction"])
                self.assertNotIn("raw_unicode_offset", response.text)
                self.assertNotIn("related_only", response.text)
                self.assertNotIn("source_ref", response.text)
                self.assertNotIn("input_spans", response.text)
                if not excerpts:
                    self.assertEqual(data["status"], "no_reviewed_interpretation")

    def test_three_sensitive_pending_topics_are_only_user_text_not_classical_readings(self):
        positives = (
            ("梦见我被追赶", "被追", "梦见我被追赶"),
            ("梦见陌生人追我", "被追", "梦见陌生人追我"),
            ("我梦见故人", "故人", "梦见故人"),
            ("我梦见已故的亲人", "故人", "梦见已故的亲人"),
            ("我梦见自己死了", "死亡", "梦见自己死了"),
            ("梦见我死亡", "死亡", "梦见我死亡"),
        )
        for narrative, label, quote in positives:
            with self.subTest(narrative=narrative):
                response = self.client.post(PUBLIC, json={"dream_text": narrative})
                self.assertEqual(response.status_code, 200, response.text)
                payload = response.json()
                self.assertEqual(payload["matches"], [])
                self.assertEqual(payload["status"], "no_reviewed_interpretation")
                self.assertEqual(payload["unreviewed_topics"],
                                 [{"label": label, "matched_texts": [quote]}])
                self.assertFalse(payload["ai_enabled"])
                self.assertFalse(payload["personal_prediction"])
                for forbidden in ("source_ref", "input_spans", "rule_id", "canonical_path",
                                  "raw_unicode_offset", "interpretation_candidate"):
                    self.assertNotIn(forbidden, response.text)

    def test_sensitive_topics_are_never_inferred_from_retractions_or_reporting(self):
        for narrative in (
            "梦见我没有被追赶",
            "听说别人梦见我被追赶",
            "梦见有人追我",
            "梦见我追别人",
            "电影里有人梦见故人",
            "如果梦见自己死了",
            "我梦见自己死了但是醒来发现只是幻想",
            "我梦见故人但其实并没有做梦",
        ):
            with self.subTest(narrative=narrative):
                response = self.client.post(PUBLIC, json={"dream_text": narrative})
                self.assertEqual(response.status_code, 200, response.text)
                payload = response.json()
                self.assertEqual(payload["matches"], [])
                self.assertEqual(payload["unreviewed_topics"], [])
                self.assertFalse(payload["ai_enabled"])

    def test_mixed_reviewed_money_and_unreviewed_death_do_not_create_combined_meaning(self):
        narrative = "我梦见我捡到了钱，后来梦见自己死了"
        response = self.client.post(PUBLIC, json={"dream_text": narrative})
        self.assertEqual(response.status_code, 200, response.text)
        payload = response.json()
        self.assertEqual([x["short_quote"] for x in payload["matches"]],
                         ["拾得钱物皆大吉"])
        self.assertEqual(payload["unreviewed_topics"],
                         [{"label": "死亡", "matched_texts": ["梦见自己死了"]}])
        self.assertNotIn("combined_interpretation", response.text)
        self.assertFalse(payload["personal_prediction"])

    def test_reviewed_paraphrases_have_exact_input_provenance(self):
        cases = (
            ("我梦见我拾起一枚硬币", "拾得钱物皆大吉", "我拾起一枚硬币"),
            ("我梦见一群鱼儿在湖里游来游去", "群鱼游水主有财", "一群鱼儿在湖里游来游去"),
            ("我梦见我家房屋正在重新翻修", "屋宅更新主大吉", "我家房屋正在重新翻修"),
        )
        for narrative, classic, matched in cases:
            with self.subTest(narrative=narrative):
                response = self.client.post(PUBLIC, json={"dream_text": narrative})
                self.assertEqual(response.status_code, 200, response.text)
                matches = response.json()["matches"]
                self.assertEqual(len(matches), 1)
                self.assertEqual(matches[0]["short_quote"], classic)
                self.assertEqual(matches[0]["matched_texts"], [matched])
                self.assertNotIn("input_spans", response.text)
                self.assertFalse(response.json()["ai_enabled"])

    def test_negations_other_people_and_wrong_actions_remain_unmatched(self):
        for narrative in (
            "我梦见没有拾起一枚硬币",
            "我梦见朋友拾起一枚硬币",
            "我梦见我扔掉一枚硬币",
            "我梦见没有一群鱼儿在湖里游",
            "我梦见别人家的房屋正在重新翻修",
        ):
            with self.subTest(narrative=narrative):
                response = self.client.post(PUBLIC, json={"dream_text": narrative})
                self.assertEqual(response.status_code, 200, response.text)
                self.assertEqual(response.json()["matches"], [])

    def test_strict_request_contract_and_private_route_still_protected(self):
        for payload in ({}, {"dream_text": ""}, {"dream_text": "  "},
                        {"dream_text": 7}, {"dream_text": "梦"*501},
                        {"dream_text": "我梦见被蛇咬了", "mode": "production"},
                        {"dream_text": "我梦见被蛇咬了", "explain": True}):
            with self.subTest(payload=payload):
                response = self.client.post(PUBLIC, json=payload)
                self.assertEqual(response.status_code, 422, response.text)
        private = self.client.post(ADMIN, json={"dream_text": "我梦见被蛇咬了"})
        self.assertEqual(private.status_code, 401)
        self.assertEqual(private.json()["detail"]["code"], "admin_unauthorized")


if __name__ == "__main__":
    unittest.main()
