"""TJ-003.3: public API / bundle / error / log leak redlines.

Every test asserts a REAL negative: responses must not carry tracebacks,
filesystem paths, private-data markers, or unauthenticated admin access.
Fail-closed is verified, not assumed.
"""
import unittest
from fastapi.testclient import TestClient
from tianji_kb.api import create_app


def _body_text(response):
    try:
        return response.text
    except Exception:
        return ""


class LeakRedlineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = cls.enterClassContext(TestClient(create_app()))

    def assert_no_leak(self, text, where):
        lowered = text.lower()
        for marker in ("traceback", "file \"/", "tianji-private",
                       "private-knowledge", "/root/", "/home/",
                       "secret", "api_key", "apikey"):
            self.assertNotIn(marker, lowered,
                             f"leak marker {marker!r} in {where}")
        return text

    def test_health_has_no_internals(self):
        r = self.client.get("/health")
        self.assertEqual(r.status_code, 200)
        self.assert_no_leak(_body_text(r), "GET /health")

    def test_404_has_no_internals(self):
        r = self.client.get("/api/v1/does-not-exist")
        self.assertEqual(r.status_code, 404)
        self.assert_no_leak(_body_text(r), "404 response")

    def test_422_validation_has_no_internals(self):
        r = self.client.post("/api/v1/public/execute", json={"bogus": 1})
        self.assertIn(r.status_code, (400, 422))
        self.assert_no_leak(_body_text(r), "422 response")

    def test_admin_endpoints_require_token(self):
        paths = [
            "/api/v1/admin/governance/conflicts",
            "/api/v1/admin/governance/rules",
            "/api/v1/admin/system/provider",
        ]
        for path in paths:
            with self.subTest(path=path):
                r = self.client.get(path)
                # 401/403 = token required; 503 = auth not configured
                # (fail-closed). 200 with data would be a leak.
                self.assertIn(r.status_code, (401, 403, 503),
                              f"{path} must not serve without a token")
                self.assert_no_leak(_body_text(r), f"unauth {path}")

    def test_admin_wrong_token_rejected(self):
        r = self.client.get(
            "/api/v1/admin/governance/rules",
            headers={"Authorization": "Bearer wrong-token"})
        self.assertIn(r.status_code, (401, 403, 503))
        self.assert_no_leak(_body_text(r), "wrong token response")

    def test_public_capabilities_has_no_private_markers(self):
        r = self.client.get("/api/v1/capabilities")
        self.assertEqual(r.status_code, 200)
        self.assert_no_leak(_body_text(r), "capabilities")

    def test_public_dream_culture_rejects_empty(self):
        r = self.client.post("/api/v1/dream/culture",
                             json={"dream_text": "x"})
        self.assertIn(r.status_code, (400, 422))
        self.assert_no_leak(_body_text(r), "dream validation")

    def test_method_not_allowed_has_no_internals(self):
        r = self.client.post("/health")
        self.assertIn(r.status_code, (404, 405))
        self.assert_no_leak(_body_text(r), "POST /health")


if __name__ == "__main__":
    unittest.main()
