"""TJ-003.3: public-boundary red-line tests over real execution (SEALED ONLY).

This file runs ONLY in the offline acceptance (assembled backend with
the sealed bundle), NEVER in public CI: it executes the four
production-baseline probe charts through the real public scenario
endpoint and runs the shared boundary check over the whole projected
envelope. It must not be added to .github/workflows/validate.yml.
The public companion ``test_tj0033_public_boundary.py`` covers the
shared check over synthetic envelopes and the shipped fixtures in
public CI; this file covers what only real execution can prove --
that a real presented strength object, and a real projected
envelope, carry no raw internal identifier.

Probe charts (the production baseline probes, Asia/Shanghai):
c1 1966-07-06T12:00 (presented commanding, 107 raw ids pre-fix),
c2 1978-09-20T10:00 (presented, 106 raw ids pre-fix),
c3 2007-06-11T12:00 (not_judgeable), c4 1981-12-21T22:30 (conflict).

Known gap, stated not claimed: runtime log leakage cannot be
verified from a response alone. Log hygiene is covered at deploy
time by the boundary-logs workflow (b024-boundary-logs.yml), not by
this file; a log-leak red-line over a live server log is still
unverified.
"""

import unittest

from fastapi.testclient import TestClient

from tianji_kb.api import create_app
from tianji_kb.bazi_strength_public import (
    is_valid_public_strength_presentation,
)
from tianji_kb.public_boundary import find_public_boundary_violations

PROBES = {
    # chart id -> (birth value, expected strength status)
    "c1": ("1966-07-06T12:00:00+08:00", "presented"),
    "c2": ("1978-09-20T10:00:00+08:00", "presented"),
    "c3": ("2007-06-11T12:00:00+08:00", "not_judgeable"),
    "c4": ("1981-12-21T22:30:00+08:00", "conflict"),
}


class RealEnvelopeBoundaryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = cls.enterClassContext(
            TestClient(create_app(), raise_server_exceptions=False))

    def _public_profile(self, birth):
        response = self.client.post(
            "/api/v1/scenarios/public",
            json={"scenario_id": "bazi-profile",
                  "input": {"value": birth, "zone": "Asia/Shanghai",
                            "traditional_role": "male"}})
        self.assertEqual(response.status_code, 200, response.text)
        return response.json()

    def test_real_projected_envelopes_carry_no_raw_identifiers(self):
        for chart_id, (birth, status) in PROBES.items():
            with self.subTest(chart=chart_id):
                envelope = self._public_profile(birth)
                strength = envelope["result"]["strength_presentation"]
                self.assertEqual(strength["status"], status, chart_id)
                self.assertTrue(
                    is_valid_public_strength_presentation(strength),
                    chart_id)
                self.assertNotIn("evidence_ids", strength, chart_id)
                self.assertNotIn("source_ids", strength, chart_id)
                self.assertEqual(
                    find_public_boundary_violations(envelope), [],
                    chart_id)

    def test_real_presented_strength_has_the_new_key_shape(self):
        # c1/c2 presented: exactly 13 keys, no reference fields.
        for chart_id in ("c1", "c2"):
            with self.subTest(chart=chart_id):
                envelope = self._public_profile(PROBES[chart_id][0])
                strength = envelope["result"]["strength_presentation"]
                self.assertEqual(len(strength), 13, chart_id)
                self.assertEqual(
                    find_public_boundary_violations(strength), [],
                    chart_id)


if __name__ == "__main__":
    unittest.main()
