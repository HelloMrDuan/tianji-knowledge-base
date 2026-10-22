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
        # Configure a test admin token so auth is active:
        # - no token -> 401, wrong token -> 401, correct token -> 200
        # (Without a configured token, API returns 503 fail-closed.)
        cls.client = TestClient(create_app(admin_read_token="test-token-123"))
        cls.admin_client = TestClient(create_app())  # no token -> 503

    def test_health_smoke(self):
        r = self.client.get("/health")
        self.assertEqual(r.status_code, 200)
        data = r.json()
        self.assertIn("status", data)

    def test_capabilities_smoke(self):
        r = self.client.get("/api/v1/capabilities")
        self.assertEqual(r.status_code, 200)
        data = r.json()
        # /api/v1/capabilities returns domains (not scenarios).
        self.assertIn("domains", data)

    def test_scenarios_smoke(self):
        r = self.client.get("/api/v1/scenarios")
        self.assertEqual(r.status_code, 200)
        data = r.json()
        # Must list the 11 scenarios (product plan, not 4 functions).
        self.assertIn("scenarios", data)
        self.assertEqual(len(data["scenarios"]), 11)

    def test_public_execute_bazi_smoke(self):
        # Real user chain: input birth data -> real API -> limited result.
        r = self.client.post(
            "/api/v1/public/execute",
            json={"domain": "bazi",
                  "input": {"value": "2000-01-07T12:00:00+08:00"}})
        self.assertEqual(r.status_code, 200, r.text[:300])
        data = r.json()
        # Must return a chart with evidence, not an empty shell.
        # (ExecuteResponse has chart/evidence, not a "result" field.)
        self.assertIn("chart", data)
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
        # With token configured: 401. Without: 503 fail-closed.
        r = self.client.get("/api/v1/admin/governance/rules")
        self.assertEqual(r.status_code, 401)
        r2 = self.admin_client.get("/api/v1/admin/governance/rules")
        self.assertEqual(r2.status_code, 503)

    def test_admin_with_wrong_token_refused(self):
        r = self.client.get(
            "/api/v1/admin/governance/rules",
            headers={"Authorization": "Bearer wrong-token"})
        self.assertIn(r.status_code, (401, 403))

    def test_dream_culture_lookup_smoke(self):
        # Dream lookup must work without inventing AI predictions.
        # API uses dream_text (not keyword).
        r = self.client.post(
            "/api/v1/dream/culture",
            json={"dream_text": "梦见蛇"})
        # Must return 200 with real lookup result (not 422 as success).
        self.assertEqual(r.status_code, 200, r.text[:300])
        data = r.json()
        # Response must contain lookup results, not be empty.
        self.assertTrue(data)


if __name__ == "__main__":
    unittest.main()
