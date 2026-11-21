"""TJ-028.2: controlled real-model dream evaluation runner.

All tests run offline with injected scripted providers or a local
stub HTTP server: no real model, no network beyond localhost, no
credentials. The tests pin the hard gates (dry-run loopback-only,
real-mode authorization, single-use claims, output cap, budget
pre-flight), the stop-on-transport-error rule, the same deterministic
checks as the mock evaluator, and the audit records carrying no
credential material.
"""

import copy
import json
import os
import subprocess
import sys
import threading
import unittest
from datetime import datetime, timedelta, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from tianji_kb.dream_eval import (  # noqa: E402
    load_suite,
    valid_reply_for,
)
from tianji_kb.dream_real_eval import (  # noqa: E402
    DEFAULT_MAX_POINTS,
    RealEvalConfig,
    RealEvalError,
    claim_authorization,
    estimate_tokens,
    preflight,
    run_real_eval,
    validate_authorization,
)
from tianji_kb.model_client import ModelClientError  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]

LOOPBACK_CONFIG = {
    "configured": True,
    "driver": "openai-compatible",
    "endpoint": "http://127.0.0.1:18099",
    "model": "mock",
    "timeout": 20,
    "max_tokens": 384,
    "reason": None,
    "settings": {"key": "test-key"},
}
REAL_CONFIG = {
    "configured": True,
    "driver": "openai-compatible",
    "endpoint": "https://api.example.invalid/v1",
    "model": "DeepSeek-V4-Flash",
    "timeout": 20,
    "max_tokens": 384,
    "reason": None,
    "settings": {"key": "test-key"},
}


def _valid_record(**overrides):
    now = datetime.now(timezone.utc)
    record = {
        "platform": "amd-token-factory",
        "model": "DeepSeek-V4-Flash",
        "scope": "dream real-model evaluation",
        "approver": "user",
        "authorization_id": "auth-test-001",
        "issued_at": (now - timedelta(minutes=5)).isoformat(),
        "expires_at": (now + timedelta(hours=2)).isoformat(),
        "budget_pts": 0.01,
    }
    record.update(overrides)
    return record


class SceneReplyProvider:
    """Test double: returns the valid reply for the case's own scene.

    Reads the scene from the adapter context's candidates, so each
    call is scored against its own case -- the same way a real model
    would answer the narrative it was given.
    """

    def __init__(self, suite, error_at=None, error=None):
        self.suite = suite
        self.calls = 0
        self.error_at = error_at
        self.error = error

    async def explain(self, context):
        self.calls += 1
        if self.error_at is not None and self.calls == self.error_at:
            raise self.error
        candidates = context.get("candidates") or []
        term_id = candidates[0]["term_id"] if candidates else None
        return copy.deepcopy(valid_reply_for(self.suite, term_id))


class EstimatorTests(unittest.TestCase):
    def test_estimate_is_deterministic_and_conservative(self):
        text = "梦见蛇咬人" + "abc" * 100
        first = estimate_tokens(text)
        self.assertEqual(first, estimate_tokens(text))
        self.assertGreater(first, len(text) // 4)
        self.assertEqual(estimate_tokens(""), 20)


class AuthorizationTests(unittest.TestCase):
    def test_valid_record_passes(self):
        record = validate_authorization(
            _valid_record(), model="DeepSeek-V4-Flash", max_points=0.01
        )
        self.assertEqual(record["authorization_id"], "auth-test-001")

    def test_wrong_approver_scope_model_and_platform_refuse(self):
        for overrides in (
            {"approver": "agent"},
            {"scope": "ad-hoc chat completion"},
            {"model": "other-model"},
            {"platform": "other-platform"},
        ):
            with self.assertRaises(RealEvalError, msg=str(overrides)):
                validate_authorization(
                    _valid_record(**overrides),
                    model="DeepSeek-V4-Flash",
                    max_points=0.01,
                )

    def test_expired_future_and_overlong_records_refuse(self):
        now = datetime.now(timezone.utc)
        cases = [
            {"expires_at": (now - timedelta(minutes=1)).isoformat()},
            {"issued_at": (now + timedelta(minutes=1)).isoformat()},
            {"expires_at": (now + timedelta(hours=25)).isoformat()},
            {"authorization_id": "bad id!"},
            {"budget_pts": 0.02},
            {"budget_pts": 0},
            {"budget_pts": "0.01"},
        ]
        for overrides in cases:
            with self.assertRaises(RealEvalError, msg=str(overrides)):
                validate_authorization(
                    _valid_record(**overrides),
                    model="DeepSeek-V4-Flash",
                    max_points=0.01,
                )

    def test_budget_below_run_cap_refuses(self):
        with self.assertRaises(RealEvalError):
            validate_authorization(
                _valid_record(budget_pts=0.005),
                model="DeepSeek-V4-Flash",
                max_points=0.01,
            )

    def test_claim_is_single_use(self):
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            record = _valid_record()
            claim_authorization(record, tmp)
            self.assertTrue((Path(tmp) / "claim-auth-test-001.json").exists())
            with self.assertRaises(RealEvalError) as ctx:
                claim_authorization(record, tmp)
            self.assertEqual(ctx.exception.code, "authorization_already_claimed")


class PreflightTests(unittest.TestCase):
    def test_dry_run_requires_loopback(self):
        suite = load_suite()
        config = RealEvalConfig(mode="dry-run")
        with self.assertRaises(RealEvalError) as ctx:
            preflight(suite, config, {**REAL_CONFIG, "endpoint": "https://api.example.invalid/v1"})
        self.assertEqual(ctx.exception.code, "dry_run_endpoint_not_local")

    def test_real_mode_requires_https_non_loopback_and_pinned_model(self):
        suite = load_suite()
        config = RealEvalConfig(mode="real")
        for provider_config, code in (
            ({**REAL_CONFIG, "endpoint": "http://api.example.invalid/v1"}, "real_mode_endpoint_not_https"),
            ({**REAL_CONFIG, "endpoint": "https://127.0.0.1:8443/v1"}, "real_mode_endpoint_is_local"),
            ({**REAL_CONFIG, "model": "other-model"}, "model_mismatch"),
        ):
            with self.assertRaises(RealEvalError, msg=code) as ctx:
                preflight(suite, config, provider_config)
            self.assertEqual(ctx.exception.code, code)

    def test_real_mode_without_authorization_refuses(self):
        suite = load_suite()
        config = RealEvalConfig(mode="real")
        with self.assertRaises(RealEvalError) as ctx:
            preflight(suite, config, REAL_CONFIG)
        self.assertEqual(ctx.exception.code, "authorization_required")

    def test_output_cap_and_budget_preflight(self):
        suite = load_suite()
        with self.assertRaises(RealEvalError) as ctx:
            preflight(
                suite,
                RealEvalConfig(mode="dry-run"),
                {**LOOPBACK_CONFIG, "max_tokens": 4096},
            )
        self.assertEqual(ctx.exception.code, "output_cap_exceeded")
        with self.assertRaises(RealEvalError) as ctx:
            preflight(
                suite, RealEvalConfig(mode="dry-run", max_points=0.0001), LOOPBACK_CONFIG
            )
        self.assertEqual(ctx.exception.code, "budget_exceeded")

    def test_not_configured_refuses_with_zero_calls(self):
        suite = load_suite()
        with self.assertRaises(RealEvalError) as ctx:
            preflight(
                suite,
                RealEvalConfig(mode="dry-run"),
                {"configured": False, "reason": "not_configured"},
            )
        self.assertEqual(ctx.exception.code, "not_configured")

    def test_dry_run_preflight_passes_and_fits_budget(self):
        suite = load_suite()
        plan = preflight(suite, RealEvalConfig(mode="dry-run"), LOOPBACK_CONFIG)
        self.assertEqual(plan["worst_calls"], 29)
        self.assertLessEqual(plan["worst_pts"], DEFAULT_MAX_POINTS)
        self.assertGreater(plan["worst_pts"], 0)


class RunTests(unittest.IsolatedAsyncioTestCase):
    def _provider(self):
        return SceneReplyProvider(load_suite())

    async def test_full_dry_run_with_scripted_provider(self):
        import tempfile

        suite = load_suite()
        with tempfile.TemporaryDirectory() as tmp:
            summary = await run_real_eval(
                suite=suite,
                config=RealEvalConfig(mode="dry-run"),
                provider_config=LOOPBACK_CONFIG,
                provider=self._provider(),
                output_dir=tmp,
            )
            self.assertEqual(summary["run_kind"], "real_model")
            self.assertEqual(summary["mode"], "dry-run")
            self.assertFalse(summary["real_model_evaluation"])
            self.assertFalse(summary["online_ready"])
            self.assertIsNone(summary["stopped"])
            self.assertEqual(summary["reports"]["dream"]["cases_run"], 35)
            self.assertEqual(summary["totals"]["provider_calls"], 29)
            self.assertLess(summary["totals"]["pts_est"], DEFAULT_MAX_POINTS)
            self.assertEqual(summary["reports"]["dream"]["pass_rate"], 1.0)
            self.assertEqual(summary["reports"]["dream"]["control_pass_rate"], 1.0)
            rows = [
                json.loads(line)
                for line in (Path(tmp) / "audit.jsonl").read_text().splitlines()
            ]
            self.assertEqual(len(rows), 35)
            self.assertTrue((Path(tmp) / "summary.json").exists())
            self.assertTrue((Path(tmp) / "report.md").exists())
            for row in rows:
                self.assertEqual(row["endpoint_host"], "127.0.0.1")
                self.assertEqual(row["model"], "mock")
            rejected = [r for r in rows if r["id"] in (
                "dream.eval-too-short", "dream.eval-too-long")]
            self.assertEqual(len(rejected), 2)
            self.assertTrue(all(r["status"] == "passed" for r in rejected))
            refused = [r for r in rows if r["kind"] == "refusal"]
            self.assertEqual(len(refused), 10)
            self.assertTrue(all(r["check_set"] == "explained" for r in refused))
            blob = (Path(tmp) / "audit.jsonl").read_text() + (Path(tmp) / "summary.json").read_text()
            for secret in ("test-key", "Bearer", "api_key", "TIANJI_AI_API_KEY"):
                self.assertNotIn(secret, blob)

    async def test_transport_error_stops_the_run(self):
        import tempfile

        suite = load_suite()
        provider = SceneReplyProvider(
            suite, error_at=2, error=ModelClientError("rate_limit", "mock 429")
        )
        with tempfile.TemporaryDirectory() as tmp:
            summary = await run_real_eval(
                suite=suite,
                config=RealEvalConfig(mode="dry-run"),
                provider_config=LOOPBACK_CONFIG,
                provider=provider,
                output_dir=tmp,
            )
            self.assertEqual(summary["stopped"], "transport:provider_rate_limited")
            self.assertGreater(len(summary["reports"]["dream"]["not_run"]), 0)
            rows = [
                json.loads(line)
                for line in (Path(tmp) / "audit.jsonl").read_text().splitlines()
            ]
            self.assertEqual(rows[-1]["verdict"], "provider_rate_limited")
            self.assertEqual(summary["totals"]["provider_calls"], 2)

    async def test_max_requests_stops_the_run(self):
        import tempfile

        suite = load_suite()
        with tempfile.TemporaryDirectory() as tmp:
            summary = await run_real_eval(
                suite=suite,
                config=RealEvalConfig(mode="dry-run", max_requests=5),
                provider_config=LOOPBACK_CONFIG,
                provider=self._provider(),
                output_dir=tmp,
            )
            self.assertEqual(summary["stopped"], "max_requests")
            self.assertEqual(summary["totals"]["provider_calls"], 5)


class LocalStubServerTests(unittest.IsolatedAsyncioTestCase):
    """The CLI end-to-end against a local stub OpenAI-compatible server."""

    def _make_handler(self, suite):
        class Handler(BaseHTTPRequestHandler):
            def log_message(self, *args):
                pass

            def do_POST(self):
                length = int(self.headers.get("Content-Length") or 0)
                body = json.loads(self.rfile.read(length) or b"{}")
                user_json = json.loads(body["messages"][1]["content"])
                candidates = user_json.get("candidates") or []
                term_id = candidates[0]["term_id"] if candidates else None
                reply = valid_reply_for(suite, term_id) if term_id else {
                    "domain": "dream", "variant": "traditional",
                    "mode": "research", "claims": [],
                }
                payload = json.dumps(
                    {"choices": [{"message": {"role": "assistant", "content": json.dumps(reply, ensure_ascii=False)}}]}
                ).encode()
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(payload)))
                self.end_headers()
                self.wfile.write(payload)

        return Handler

    async def test_cli_dry_run_against_local_stub(self):
        import tempfile

        suite = load_suite()
        server = ThreadingHTTPServer(("127.0.0.1", 0), self._make_handler(suite))
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            port = server.server_address[1]
            with tempfile.TemporaryDirectory() as tmp:
                # The stub lives on localhost: no proxy is needed. The
                # sandbox NO_PROXY carries bracketed IPv6 literals that
                # httpx's trust_env parsing rejects at client
                # construction, so proxy variables are stripped here;
                # the transport under test is unchanged.
                env = {
                    k: v for k, v in os.environ.items()
                    if "proxy" not in k.lower()
                }
                env.update(
                    {
                        "TIANJI_AI_PROVIDER": "openai-compatible",
                        "TIANJI_AI_BASE_URL": f"http://127.0.0.1:{port}",
                        "TIANJI_AI_API_KEY": "test-key",
                        "TIANJI_AI_MODEL": "mock",
                        "TIANJI_AI_MAX_OUTPUT_TOKENS": "384",
                        "TIANJI_AI_TIMEOUT_SECONDS": "20",
                    }
                )
                result = subprocess.run(
                    [
                        sys.executable,
                        str(ROOT / "scripts" / "evaluate_dream_real.py"),
                        "--mode", "dry-run",
                        "--output-dir", tmp,
                    ],
                    capture_output=True, text=True, env=env, cwd=ROOT,
                )
                self.assertEqual(result.returncode, 0, result.stderr[-2000:])
                summary = json.loads((Path(tmp) / "summary.json").read_text())
                self.assertEqual(summary["reports"]["dream"]["cases_run"], 35)
                self.assertEqual(summary["totals"]["provider_calls"], 29)
                self.assertIsNone(summary["stopped"])
        finally:
            server.shutdown()
            server.server_close()

    def test_cli_real_mode_without_authorization_exits_1(self):
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            env = {
                k: v for k, v in os.environ.items()
                if "proxy" not in k.lower()
            }
            env.update(
                {
                    "TIANJI_AI_PROVIDER": "openai-compatible",
                    "TIANJI_AI_BASE_URL": "https://api.example.invalid/v1",
                    "TIANJI_AI_API_KEY": "test-key",
                    "TIANJI_AI_MODEL": "DeepSeek-V4-Flash",
                    "TIANJI_AI_MAX_OUTPUT_TOKENS": "384",
                }
            )
            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "evaluate_dream_real.py"),
                    "--mode", "real",
                    "--output-dir", tmp,
                ],
                capture_output=True, text=True, env=env, cwd=ROOT,
            )
            self.assertEqual(result.returncode, 1)
            self.assertIn("authorization_required", result.stderr)
            self.assertFalse((Path(tmp) / "audit.jsonl").exists())


if __name__ == "__main__":
    unittest.main()
