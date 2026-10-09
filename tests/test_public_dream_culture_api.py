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
        self.assertEqual(set(match), {"scene", "cultural_reading", "short_quote",
                                      "source_title", "evidence_level"})
        # Never leak internal RAG traces, repository paths or privileged metadata.
        for key in ("evidence", "retrieval", "canonical_path", "rule_id", "term_id",
                    "input_spans", "entities", "trace", "token", "dream_text"):
            self.assertNotIn(key, response.text)
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
