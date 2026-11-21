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

import httpx

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from tianji_kb.dream_eval import (  # noqa: E402
    build_fixture_retrieval,
    load_suite,
    valid_reply_for,
)
from tianji_kb.dream_real_eval import (  # noqa: E402
    DEFAULT_MAX_POINTS,
    RealEvalConfig,
    RealEvalError,
    _check_live_quota,
    _score_result,
    claim_authorization,
    estimate_tokens,
    extract_remaining_pts,
    preflight,
    run_real_eval,
    validate_authorization,
)
from tianji_kb.model_client import ModelClientError  # noqa: E402
from tianji_kb.runtime_catalog import digest  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]

# The approved AMD gateway base (see dream_real_eval: real mode pins
# this host and the /radeon/api/v1/chat/completions request path).
APPROVED_BASE_URL = "https://developer.amd.com.cn/radeon/api/v1"

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
    "endpoint": APPROVED_BASE_URL,
    "model": "DeepSeek-V4-Flash",
    "timeout": 20,
    "max_tokens": 384,
    "reason": None,
    "settings": {"key": "test-key"},
}


def _valid_record(**overrides):
    now = datetime.now(timezone.utc)
    suite = load_suite()
    record = {
        "platform": "amd-token-factory",
        "model": "DeepSeek-V4-Flash",
        "scope": "dream real-model evaluation",
        "approver": "user",
        "authorization_id": "auth-test-001",
        "issued_at": (now - timedelta(minutes=5)).isoformat(),
        "expires_at": (now + timedelta(hours=2)).isoformat(),
        "budget_pts": 0.01,
        "suite_id": suite["suite_id"],
        "suite_sha256": digest(suite),
    }
    record.update(overrides)
    return record


def _quota_transport(remaining_pts=5.0, status=200, payload=None):
    """httpx.MockTransport answering GET /usage with a canned quota."""

    def handler(request):
        assert request.url.path == "/radeon/api/v1/usage"
        assert request.headers.get("Authorization") == "Bearer test-key"
        body = (
            payload
            if payload is not None
            else {"daily_cost_remaining_usd": remaining_pts}
        )
        return httpx.Response(status, json=body)

    return httpx.MockTransport(handler)


def _write_record(tmp, record):
    path = Path(tmp) / "authorization.json"
    path.write_text(json.dumps(record, ensure_ascii=False), encoding="utf-8")
    return str(path)


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

    def test_claim_is_single_use_and_location_is_fixed(self):
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            record = _valid_record()
            auth_path = _write_record(tmp, record)
            claim_path = claim_authorization(record, auth_path)
            # The claim lives next to the record, never elsewhere.
            self.assertEqual(
                claim_path, Path(tmp) / "claims" / "claim-auth-test-001.json"
            )
            self.assertTrue(claim_path.exists())
            with self.assertRaises(RealEvalError) as ctx:
                claim_authorization(record, auth_path)
            self.assertEqual(ctx.exception.code, "authorization_already_claimed")

    def test_authorization_binds_suite_digest(self):
        suite = load_suite()
        record = _valid_record()
        validate_authorization(
            record, model="DeepSeek-V4-Flash", max_points=0.01,
            suite=suite, case_ids=[],
        )
        for overrides in (
            {"suite_sha256": "0" * 64},
            {"suite_id": "other-suite"},
        ):
            with self.assertRaises(RealEvalError) as ctx:
                validate_authorization(
                    _valid_record(**overrides),
                    model="DeepSeek-V4-Flash", max_points=0.01,
                    suite=suite, case_ids=[],
                )
            self.assertEqual(ctx.exception.code, "suite_digest_mismatch")
        # A record without suite fields cannot authorize a suite-bound run.
        bare = _valid_record()
        del bare["suite_id"]
        del bare["suite_sha256"]
        with self.assertRaises(RealEvalError) as ctx:
            validate_authorization(
                bare, model="DeepSeek-V4-Flash", max_points=0.01,
                suite=suite, case_ids=[],
            )
        self.assertEqual(ctx.exception.code, "suite_digest_mismatch")

    def test_authorization_binds_case_scope(self):
        suite = load_suite()
        subset = ["dream.eval-snake-positive"]
        # No case_ids in the record: full suite only.
        record = _valid_record()
        validate_authorization(
            record, model="DeepSeek-V4-Flash", max_points=0.01,
            suite=suite, case_ids=[],
        )
        with self.assertRaises(RealEvalError) as ctx:
            validate_authorization(
                record, model="DeepSeek-V4-Flash", max_points=0.01,
                suite=suite, case_ids=subset,
            )
        self.assertEqual(ctx.exception.code, "case_scope_mismatch")
        # An explicit case_ids list allows exactly that set.
        scoped = _valid_record(case_ids=subset)
        validate_authorization(
            scoped, model="DeepSeek-V4-Flash", max_points=0.01,
            suite=suite, case_ids=subset,
        )
        with self.assertRaises(RealEvalError) as ctx:
            validate_authorization(
                scoped, model="DeepSeek-V4-Flash", max_points=0.01,
                suite=suite, case_ids=[],
            )
        self.assertEqual(ctx.exception.code, "case_scope_mismatch")
        with self.assertRaises(RealEvalError) as ctx:
            validate_authorization(
                _valid_record(case_ids="dream.eval-snake-positive"),
                model="DeepSeek-V4-Flash", max_points=0.01,
                suite=suite, case_ids=subset,
            )
        self.assertEqual(ctx.exception.code, "case_scope_mismatch")


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
            ({**REAL_CONFIG, "endpoint": "http://developer.amd.com.cn/radeon/api/v1"}, "gateway_not_approved"),
            ({**REAL_CONFIG, "endpoint": "https://127.0.0.1:8443/v1"}, "gateway_not_approved"),
            ({**REAL_CONFIG, "model": "other-model"}, "model_mismatch"),
        ):
            with self.assertRaises(RealEvalError, msg=code) as ctx:
                preflight(suite, config, provider_config)
            self.assertEqual(ctx.exception.code, code)

    def test_real_mode_pins_approved_gateway_host_and_path(self):
        suite = load_suite()
        config = RealEvalConfig(mode="real")
        for endpoint in (
            "https://api.example.invalid/v1",
            "https://developer.amd.com.cn.evil.example/v1",
            "https://developer.amd.com.cn/other/v1",
            "https://developer.amd.com.cn/radeon/api/v1/chat/completions/extra",
            "https://developer.amd.com.cn/radeon/api/v1?x=1",
            "https://user:pass@developer.amd.com.cn/radeon/api/v1",
        ):
            with self.assertRaises(RealEvalError, msg=endpoint) as ctx:
                preflight(suite, config, {**REAL_CONFIG, "endpoint": endpoint})
            self.assertEqual(ctx.exception.code, "gateway_not_approved")
        # Both the approved base and the full chat path are accepted
        # (the provider appends /chat/completions to the base).
        for endpoint in (
            APPROVED_BASE_URL,
            APPROVED_BASE_URL + "/chat/completions",
        ):
            with self.assertRaises(RealEvalError, msg=endpoint) as ctx:
                preflight(suite, config, {**REAL_CONFIG, "endpoint": endpoint})
            # The gateway passes; the next gate (authorization) fires.
            self.assertEqual(ctx.exception.code, "authorization_required")

    def test_real_mode_without_authorization_refuses(self):
        suite = load_suite()
        config = RealEvalConfig(mode="real")
        with self.assertRaises(RealEvalError) as ctx:
            preflight(suite, config, REAL_CONFIG)
        self.assertEqual(ctx.exception.code, "authorization_required")

    def test_output_cap_is_clamped_not_refused(self):
        suite = load_suite()
        plan = preflight(
            suite,
            RealEvalConfig(mode="dry-run"),
            {**LOOPBACK_CONFIG, "max_tokens": 4096},
        )
        # A forgotten TIANJI_AI_MAX_OUTPUT_TOKENS can never inflate
        # the run: the runner sends the run cap, not the raw value.
        self.assertEqual(plan["effective_max_tokens"], 384)
        plan = preflight(
            suite,
            RealEvalConfig(mode="dry-run"),
            {**LOOPBACK_CONFIG, "max_tokens": 256},
        )
        # A tighter operator setting is respected, never raised.
        self.assertEqual(plan["effective_max_tokens"], 256)

    def test_budget_preflight(self):
        suite = load_suite()
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

    async def test_refusal_with_different_code_passes_end_to_end(self):
        import tempfile

        suite = load_suite()
        with tempfile.TemporaryDirectory() as tmp:
            summary = await run_real_eval(
                suite=suite,
                config=RealEvalConfig(
                    mode="dry-run", case_ids=["dream.eval-diagnosis-mental"]
                ),
                provider_config=LOOPBACK_CONFIG,
                provider=ForgedEvidenceProvider(suite),
                output_dir=tmp,
            )
            self.assertEqual(summary["reports"]["dream"]["cases_run"], 1)
            row = summary["cases"][0]
            self.assertEqual(row["status"], "passed")
            self.assertEqual(row["check_set"], "refusal")
            self.assertEqual(row["verdict"], "citation_rejected")
            self.assertEqual(row["refusal_code"], "citation_rejected")
            self.assertFalse(row["refusal_code_matches_expected"])
            self.assertNotIn("refusal_code_matches_expected", row["checks"])

    async def test_wall_clock_deadline_bounds_slow_calls(self):
        import asyncio
        import tempfile

        suite = load_suite()

        class SlowProvider(SceneReplyProvider):
            async def explain(self, context):
                await asyncio.sleep(5)
                return await super().explain(context)

        with tempfile.TemporaryDirectory() as tmp:
            summary = await run_real_eval(
                suite=suite,
                config=RealEvalConfig(mode="dry-run", max_seconds=1),
                provider_config=LOOPBACK_CONFIG,
                provider=SlowProvider(suite),
                output_dir=tmp,
            )
            self.assertEqual(summary["stopped"], "transport:provider_timeout")
            self.assertLess(summary["totals"]["seconds"], 5)

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

    async def test_cli_dry_run_provider_never_retries(self):
        import tempfile

        suite = load_suite()
        counter = {"posts": 0}

        class FailingHandler(BaseHTTPRequestHandler):
            def log_message(self, *args):
                pass

            def do_POST(self):
                counter["posts"] += 1
                length = int(self.headers.get("Content-Length") or 0)
                self.rfile.read(length)
                payload = json.dumps(
                    {"error": {"message": "transient failure", "type": "server_error"}}
                ).encode()
                self.send_response(500)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(payload)))
                self.end_headers()
                self.wfile.write(payload)

        server = ThreadingHTTPServer(("127.0.0.1", 0), FailingHandler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            port = server.server_address[1]
            with tempfile.TemporaryDirectory() as tmp:
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
                        "--case", "dream.eval-snake-positive",
                    ],
                    capture_output=True, text=True, env=env, cwd=ROOT,
                )
                # A transport stop ends the run: exit 2.
                self.assertEqual(result.returncode, 2, result.stderr[-2000:])
                summary = json.loads((Path(tmp) / "summary.json").read_text())
                self.assertEqual(summary["stopped"], "transport:provider_failed")
                # One counted attempt is one HTTP request: a retrying
                # provider would have posted three times for this case.
                self.assertEqual(counter["posts"], 1)
                self.assertEqual(summary["totals"]["provider_calls"], 1)
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
                    "TIANJI_AI_BASE_URL": APPROVED_BASE_URL,
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

    def test_cli_rejects_claims_dir_override(self):
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "evaluate_dream_real.py"),
                    "--mode", "dry-run",
                    "--output-dir", tmp,
                    "--claims-dir", tmp,
                ],
                capture_output=True, text=True, cwd=ROOT,
            )
            # The claim location is fixed next to the authorization
            # record; there is no override that could re-consume it.
            self.assertEqual(result.returncode, 2)
            self.assertIn("unrecognized arguments", result.stderr)


class QuotaTests(unittest.TestCase):
    def test_extract_remaining_pts_resolution_order(self):
        self.assertEqual(
            extract_remaining_pts({"daily_cost_remaining_usd": 3.5}), 3.5
        )
        self.assertEqual(
            extract_remaining_pts(
                {"daily_cost_limit_usd": 5.0, "daily_cost_used_usd": 1.25}
            ),
            3.75,
        )
        self.assertEqual(
            extract_remaining_pts({"remaining_pts": 2.0}), 2.0
        )
        for bad in (
            {},
            {"daily_cost_remaining_usd": "3.5"},
            {"daily_cost_remaining_usd": float("nan")},
            {"daily_cost_remaining_usd": -1},
            {"daily_cost_remaining_usd": True},
            {"daily_cost_limit_usd": 1.0, "daily_cost_used_usd": 2.0},
            "not a dict",
        ):
            self.assertIsNone(extract_remaining_pts(bad), msg=str(bad))

    def test_live_quota_check_accepts_sufficient_remaining(self):
        remaining = _check_live_quota(
            REAL_CONFIG, 0.008, transport=_quota_transport(remaining_pts=5.0)
        )
        self.assertEqual(remaining, 5.0)

    def test_live_quota_check_refuses_insufficient_and_unconfirmed(self):
        for transport, code in (
            (_quota_transport(remaining_pts=0.001), "quota_insufficient"),
            (_quota_transport(payload={}), "quota_unconfirmed"),
            (_quota_transport(payload={"daily_cost_remaining_usd": "lots"}), "quota_unconfirmed"),
            (_quota_transport(status=429), "quota_check_failed"),
            (_quota_transport(status=401), "quota_check_failed"),
            (_quota_transport(status=500), "quota_check_failed"),
        ):
            with self.assertRaises(RealEvalError, msg=code) as ctx:
                _check_live_quota(REAL_CONFIG, 0.008, transport=transport)
            self.assertEqual(ctx.exception.code, code)


class RealModePreflightTests(unittest.IsolatedAsyncioTestCase):
    def _provider(self):
        return SceneReplyProvider(load_suite())

    async def test_non_whitelist_gateway_refuses_with_zero_requests(self):
        suite = load_suite()
        provider = self._provider()
        with self.assertRaises(RealEvalError) as ctx:
            await run_real_eval(
                suite=suite,
                config=RealEvalConfig(mode="real"),
                provider_config={
                    **REAL_CONFIG, "endpoint": "https://api.example.invalid/v1"
                },
                provider=provider,
                output_dir="/tmp/never-created-by-refusal",
            )
        self.assertEqual(ctx.exception.code, "gateway_not_approved")
        self.assertEqual(provider.calls, 0)

    def test_approved_gateway_preflight_passes_and_claims(self):
        import tempfile

        suite = load_suite()
        with tempfile.TemporaryDirectory() as tmp:
            auth_path = _write_record(tmp, _valid_record())
            config = RealEvalConfig(mode="real", authorization_path=auth_path)
            plan = preflight(
                suite, config, REAL_CONFIG,
                quota_transport=_quota_transport(remaining_pts=5.0),
            )
            self.assertEqual(plan["worst_calls"], 29)
            self.assertEqual(plan["quota_remaining_pts"], 5.0)
            self.assertEqual(plan["authorization_id"], "auth-test-001")
            self.assertTrue(
                (Path(tmp) / "claims" / "claim-auth-test-001.json").exists()
            )

    def test_duplicate_claim_refused_across_runs(self):
        import tempfile

        suite = load_suite()
        with tempfile.TemporaryDirectory() as tmp:
            auth_path = _write_record(tmp, _valid_record())
            config = RealEvalConfig(mode="real", authorization_path=auth_path)
            preflight(
                suite, config, REAL_CONFIG,
                quota_transport=_quota_transport(remaining_pts=5.0),
            )
            # A second run with the same record -- even from another
            # output directory -- hits the fixed claim location.
            with self.assertRaises(RealEvalError) as ctx:
                preflight(
                    suite, config, REAL_CONFIG,
                    quota_transport=_quota_transport(remaining_pts=5.0),
                )
            self.assertEqual(ctx.exception.code, "authorization_already_claimed")

    def test_swapped_suite_refuses_before_claim(self):
        import copy
        import tempfile

        suite = load_suite()
        swapped = copy.deepcopy(suite)
        swapped["cases"][0]["dream_text"] = "a completely different dream"
        with tempfile.TemporaryDirectory() as tmp:
            auth_path = _write_record(tmp, _valid_record())
            config = RealEvalConfig(mode="real", authorization_path=auth_path)
            with self.assertRaises(RealEvalError) as ctx:
                preflight(
                    swapped, config, REAL_CONFIG,
                    quota_transport=_quota_transport(remaining_pts=5.0),
                )
            self.assertEqual(ctx.exception.code, "suite_digest_mismatch")
            # Refused before the quota read and the claim: no claim file.
            self.assertFalse((Path(tmp) / "claims").exists())

    def test_insufficient_quota_refuses_before_claim(self):
        import tempfile

        suite = load_suite()
        with tempfile.TemporaryDirectory() as tmp:
            auth_path = _write_record(tmp, _valid_record())
            config = RealEvalConfig(mode="real", authorization_path=auth_path)
            with self.assertRaises(RealEvalError) as ctx:
                preflight(
                    suite, config, REAL_CONFIG,
                    quota_transport=_quota_transport(remaining_pts=0.001),
                )
            self.assertEqual(ctx.exception.code, "quota_insufficient")
            # A quota refusal never consumes the authorization.
            self.assertFalse((Path(tmp) / "claims").exists())


class RefusalScoringTests(unittest.TestCase):
    def _case(self, case_id):
        suite = load_suite()
        case = next(c for c in suite["cases"] if c["id"] == case_id)
        return suite, case, build_fixture_retrieval(suite, case["scene"])

    def _clean_refusal(self, verdict, reason="model reply cites evidence not in the audited evidence"):
        return {
            "verdict": verdict,
            "claims": [],
            "evidence": {},
            "ai_enabled": False,
            "personal_prediction": False,
            "reason": reason,
        }

    def test_different_clean_refusal_code_passes(self):
        suite, case, fixture = self._case("dream.eval-diagnosis-mental")
        self.assertEqual(case["expected_verdict"], "diagnosis_rejected")
        checks, check_set, diagnostics = _score_result(
            self._clean_refusal("citation_rejected"), case, suite, fixture
        )
        self.assertEqual(check_set, "refusal")
        self.assertTrue(all(checks.values()), checks)
        # The specific code is diagnostic only, never a gate.
        self.assertNotIn("refusal_code_matches_expected", checks)
        self.assertEqual(diagnostics["refusal_code"], "citation_rejected")
        self.assertFalse(diagnostics["refusal_code_matches_expected"])

    def test_matching_refusal_code_passes_with_diagnostic_true(self):
        suite, case, fixture = self._case("dream.eval-diagnosis-mental")
        checks, _, diagnostics = _score_result(
            self._clean_refusal(
                "diagnosis_rejected", "the reply contains a diagnosis"
            ),
            case, suite, fixture,
        )
        self.assertTrue(all(checks.values()), checks)
        self.assertTrue(diagnostics["refusal_code_matches_expected"])

    def test_leaked_refusal_still_fails(self):
        suite, case, fixture = self._case("dream.eval-diagnosis-mental")
        checks, _, _ = _score_result(
            self._clean_refusal("citation_rejected", "模型说你怀孕了，需要治疗。"),
            case, suite, fixture,
        )
        self.assertFalse(checks["no_model_text_leak"])
        self.assertFalse(all(checks.values()))


class ForgedEvidenceProvider:
    """Test double: valid reply, but the claim cites a forged evidence id.

    The adapter rejects it with ``citation_rejected`` -- a clean
    refusal whose code differs from the diagnosis cases' expectation.
    """

    def __init__(self, suite):
        self.suite = suite
        self.calls = 0

    async def explain(self, context):
        self.calls += 1
        candidates = context.get("candidates") or []
        term_id = candidates[0]["term_id"] if candidates else None
        reply = copy.deepcopy(valid_reply_for(self.suite, term_id))
        reply["claims"][0]["evidence_ids"] = ["deadbeefdeadbeefdeadbeef"]
        return reply


if __name__ == "__main__":
    unittest.main()
