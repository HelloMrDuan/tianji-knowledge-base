"""TJ-028.2: offline dream eval suite acceptance.

The suite runs entirely on fixtures and the labelled scripted test
double: no real model, no network, no credentials. The tests pin the
report contract (fixed suite digest, separate control rates,
online_ready False, real_model_evaluation False) and prove the
scorer can actually detect a forgery (a mutated positive case must
fail), so a green run is not vacuous.
"""

import copy
import json
import os
import subprocess
import sys
import unittest
from pathlib import Path

from tianji_kb.dream_eval import (
    _run_single,
    digest,
    evaluate_dream_suite,
    load_suite,
    validate_suite,
)

ROOT = Path(__file__).resolve().parents[1]


class SuiteTests(unittest.TestCase):
    def test_suite_loads_with_twelve_audited_scenes(self):
        suite = load_suite()
        self.assertEqual(suite["suite_id"], "dream-eval-v1")
        self.assertEqual(len(suite["scenes"]), 12)
        self.assertEqual(len({s["term_id"] for s in suite["scenes"]}), 12)
        self.assertEqual(len(suite["cases"]), 35)
        self.assertEqual(len({c["id"] for c in suite["cases"]}), 35)
        for scene in suite["scenes"]:
            self.assertTrue(scene["quote"])
            self.assertTrue(scene["locator"])
            self.assertEqual(scene["classic_title"], "周公解梦（电子本题名）")

    def test_suite_digest_is_stable(self):
        self.assertEqual(digest(load_suite()), digest(load_suite()))

    def test_dry_run_validates_without_provider_calls(self):
        checked = validate_suite()
        self.assertEqual(checked["provider_calls"], 0)
        self.assertGreaterEqual(checked["cases_checked"], 22)


class EvalRunTests(unittest.IsolatedAsyncioTestCase):
    async def test_full_suite_passes(self):
        report = await evaluate_dream_suite()
        self.assertEqual(report["suite_id"], "dream-eval-v1")
        self.assertEqual(report["run_kind"], "test_provider")
        self.assertEqual(report["model"], "mock-dream-eval-v1")
        self.assertFalse(report["real_model_evaluation"])
        self.assertFalse(report["online_ready"])
        row = report["reports"]["dream"]
        self.assertEqual(row["case_count"], 35)
        self.assertEqual(row["positive_cases"], 13)
        self.assertEqual(row["pass_rate"], 1.0)
        self.assertEqual(row["control_pass_rate"], 1.0)
        self.assertEqual(row["failures"], [])
        self.assertFalse(row["online_ready"])
        self.assertTrue(all(c["status"] == "passed" for c in report["cases"]))

    async def test_two_runs_are_deterministic(self):
        first = await evaluate_dream_suite()
        second = await evaluate_dream_suite()
        self.assertEqual(first["suite_sha256"], second["suite_sha256"])
        self.assertEqual(
            [c["status"] for c in first["cases"]],
            [c["status"] for c in second["cases"]],
        )

    async def test_scorer_detects_a_forged_evidence_id(self):
        # A positive case whose reply cites an unknown evidence id
        # must fail: the scorer is not vacuous.
        suite = load_suite()
        case = copy.deepcopy(
            next(c for c in suite["cases"] if c["id"] == "dream.eval-death-positive")
        )
        case["mock"] = {
            "reply": "valid",
            "mutate": {"claims[0].evidence_ids": ["deadbeef" * 3]},
        }
        row, _ = await _run_single(suite, case)
        self.assertEqual(row["status"], "failed")
        self.assertEqual(row["verdict"], "citation_rejected")
        self.assertFalse(row["checks"]["verdict_explained"])

    async def test_not_configured_case_makes_zero_calls(self):
        suite = load_suite()
        case = next(
            c for c in suite["cases"] if c["id"] == "dream.eval-not-configured"
        )
        row, provider = await _run_single(suite, case)
        self.assertEqual(row["status"], "passed")
        self.assertEqual(row["verdict"], "not_configured")
        self.assertIsNone(provider)


class CliTests(unittest.TestCase):
    def test_cli_dry_run_exits_zero(self):
        env = dict(os.environ)
        env["PYTHONPATH"] = "src"
        result = subprocess.run(
            [sys.executable, "scripts/evaluate_dream.py", "--dry-run"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            env=env,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("provider_calls 0", result.stdout)


if __name__ == "__main__":
    unittest.main()
