"""Private authenticated dream research: uses real reviewed RAG, no mocks."""
import unittest

from fastapi.testclient import TestClient

from tianji_kb.api import create_app


ENDPOINT = "/api/v1/admin/research/dream"
INPUT = {"dream_text": "我梦见被蛇咬了"}


class AdminDreamResearchAPITests(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(create_app(admin_read_token="local-review-token"))
        self.headers = {"Authorization": "Bearer local-review-token"}

    def test_no_token_configured_or_invalid_caller_never_gets_evidence(self):
        unavailable = TestClient(create_app(admin_read_token=""))
        result = unavailable.post(ENDPOINT, json=INPUT)
        self.assertEqual(result.status_code, 503)
        self.assertEqual(result.json()["detail"]["code"], "admin_auth_not_configured")
        for headers in ({}, {"Authorization": "Bearer wrong"},
                        {"Authorization": "local-review-token"},
                        {"Authorization": "Bearer "}):
            response = self.client.post(ENDPOINT, json=INPUT, headers=headers)
            self.assertEqual(response.status_code, 401, response.text)
            self.assertEqual(response.json()["detail"]["code"], "admin_unauthorized")
            self.assertNotIn("蛇咬人主得大财", response.text)
            self.assertNotIn("review-token", response.text)
        self.assertEqual(self.client.get(ENDPOINT, headers=self.headers).status_code, 405)

    def test_real_reviewed_snake_scene_with_pinned_evidence_and_restrictions(self):
        response = self.client.post(ENDPOINT, json=INPUT, headers=self.headers)
        self.assertEqual(response.status_code, 200, response.text)
        data = response.json()
        self.assertEqual(data["api_version"], "v1")
        self.assertTrue(data["read_only"])
        self.assertTrue(data["research_only"])
        self.assertFalse(data["public_release"])
        result = data["result"]
        self.assertEqual(result["domain"], "dream")
        self.assertEqual(result["mode"], "research")
        self.assertFalse(result["public_enabled"])
        self.assertFalse(result["ai_enabled"])
        self.assertFalse(result["chart_generated"])
        self.assertEqual(result["status"], "reviewed_interpretation_candidates")
        self.assertEqual(len(result["matched_interpretations"]), 1)
        match = result["matched_interpretations"][0]
        self.assertEqual(match["term_id"], "dream.term.snake")
        self.assertEqual(match["evidence_level"], "C")
        self.assertEqual(match["original_text_short_quote"], "蛇咬人主得大财")
        self.assertFalse(match["personal_prediction"])
        self.assertTrue(match["evidence_ids"])
        self.assertTrue(result["retrieval"])
        self.assertTrue(all(eid in result["evidence"] for eid in match["evidence_ids"]))
        self.assertEqual(response.json(),
                         self.client.post(ENDPOINT, json=INPUT, headers=self.headers).json())

    def test_real_unreviewed_and_negated_narrative_does_not_fabricate(self):
        for text in ("梦见考试", "梦见没有被蛇咬", "梦见电影里被蛇咬了"):
            with self.subTest(text=text):
                response = self.client.post(ENDPOINT, json={"dream_text": text}, headers=self.headers)
                self.assertEqual(response.status_code, 200, response.text)
                result = response.json()["result"]
                self.assertEqual(result["status"], "no_reviewed_interpretation")
                self.assertEqual(result["matched_interpretations"], [])
                self.assertEqual(result["evidence"], {})
                self.assertFalse(result["ai_enabled"])

    def test_forbid_unsupported_or_oversize_payloads(self):
        invalid = [
            {}, {"dream_text": ""}, {"dream_text": "梦"},
            {"dream_text": "梦见蛇" * 200},
            {"dream_text": ["梦见蛇"]}, {"dream_text": 123},
            {"dream_text": "梦见蛇", "mode": "production"},
            {"dream_text": "梦见蛇", "explain": True},
        ]
        for payload in invalid:
            with self.subTest(payload_keys=list(payload)), self.assertEqual(
                self.client.post(ENDPOINT, json=payload, headers=self.headers).status_code, 422
            ):
                pass


if __name__ == "__main__":
    unittest.main()
