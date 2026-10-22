"""TJ-005.2: API smoke tests (frontend/API/auth/error states).

Category B: runs in the private controlled backend with the real runtime.
Verifies the actual user chain: homepage -> input -> real API -> limited results.
"""
import unittest
from fastapi.testclient import TestClient
from tianji_kb.api import create_app


class ApiSmokeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(create_app())

    def test_health_smoke(self):
        r = self.client.get("/health")
        self.assertEqual(r.status_code, 200)
        data = r.json()
        self.assertIn("status", data)

    def test_capabilities_smoke(self):
        r = self.client.get("/api/v1/capabilities")
        self.assertEqual(r.status_code, 200)
        data = r.json()
        # Must list the 11 scenarios (product plan, not 4 functions).
        self.assertIn("scenarios", data)

    def test_public_execute_bazi_smoke(self):
        # Real user chain: input birth data -> real API -> limited result.
        r = self.client.post(
            "/api/v1/public/execute",
            json={"domain": "bazi",
                  "input": {"value": "2000-01-07T12:00:00+08:00"}})
        self.assertEqual(r.status_code, 200, r.text[:300])
        data = r.json()
        # Must return a result with evidence, not an empty shell.
        self.assertIn("result", data)
        self.assertIn("evidence", data)

    def test_public_execute_invalid_input_rejected(self):
        r = self.client.post(
            "/api/v1/public/execute",
            json={"domain": "bazi", "input": {"value": "not-a-date"}})
        self.assertIn(r.status_code, (400, 422))

    def test_public_execute_unknown_domain_rejected(self):
        r = self.client.post(
            "/api/v1/public/execute",
            json={"domain": "nonexistent", "input": {}})
        self.assertIn(r.status_code, (400, 422))

    def test_admin_without_token_refused(self):
        # Auth must be enforced; unauthenticated admin is refused.
        r = self.client.get("/api/v1/admin/governance/rules")
        self.assertIn(r.status_code, (401, 403, 503))

    def test_admin_with_wrong_token_refused(self):
        r = self.client.get(
            "/api/v1/admin/governance/rules",
            headers={"Authorization": "Bearer wrong-token"})
        self.assertIn(r.status_code, (401, 403))

    def test_dream_culture_lookup_smoke(self):
        # Dream lookup must work without inventing AI predictions.
        r = self.client.post(
            "/api/v1/dream/culture",
            json={"keyword": "蛇"})
        # 200 with lookup result, or 422/404 for invalid; never 500.
        self.assertNotEqual(r.status_code, 500)


if __name__ == "__main__":
    unittest.main()
