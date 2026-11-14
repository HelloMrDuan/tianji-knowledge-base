"""TJ-028.1 controlled model client: retry, classification, privacy boundary.

All tests use an explicitly labelled local test double (httpx MockTransport /
a capturing provider). They are NOT real-model acceptance: no model service
is configured in the trusted environment (no TIANJI_AI_* credentials), so
end-to-end real-model verification is BLOCKED pending credentials.
"""
import asyncio
import copy
import json
import logging
import os
import unittest
from unittest.mock import patch

import httpx
from fastapi.testclient import TestClient

from tianji_kb.ai_providers import provider_configured, provider_from_environment
from tianji_kb.api import EXAMPLES, create_app
from tianji_kb.explanation import ExplanationService, validate_reply
from tianji_kb.model_client import (
    MAX_ATTEMPTS,
    ControlledModelClient,
    ModelClientError,
    _safe_url,
    classify_exception,
    classify_status,
    is_retryable,
    redact_for_log,
    sanitize_context,
)

from phase4_helpers import valid_reply

SETTINGS = {
    "driver": "json-http",
    "endpoint": "https://model.example.test/explain",
    "key": "test-only-key",
    "model": "test-model",
    "timeout": 5,
    "max_tokens": 4096,
}
ENV = {
    "TIANJI_AI_PROVIDER": "json-http",
    "TIANJI_AI_BASE_URL": "https://model.example.test/explain",
    "TIANJI_AI_API_KEY": "test-only-key",
    "TIANJI_AI_MODEL": "test-model",
    "TIANJI_AI_TIMEOUT_SECONDS": "5",
}
BIRTH = "2000-01-07T12:00:00+08:00"


def run(coro):
    return asyncio.run(coro)


def client_with(handler, max_attempts=MAX_ATTEMPTS):
    return ControlledModelClient(
        SETTINGS, transport=httpx.MockTransport(handler),
        max_attempts=max_attempts, backoff_base=0.0,
        sleep=lambda seconds: asyncio.sleep(0),
    )


def synthetic_context():
    return {
        "domain": "yijing",
        "variant": "test-variant",
        "mode": "production",
        "chart_digest": "digest-1",
        "chart": {
            "pillars": {"year": "庚辰", "month": "己丑", "day": "丙午", "hour": "甲午"},
            "note": "born " + BIRTH,
        },
        "facts": {
            "/chart/pillars/year": "庚辰",
            "/chart/note": "born " + BIRTH,
        },
        "rules": [],
        "trace": [],
        "evidence": {
            "E001": {
                "original_text": "x" * 177,
                "classic_title": "Test Classic",
                "source_url": "https://example.test/classic",
            },
            "E002": {"original_text": "short text", "classic_title": "Test Classic"},
        },
        "rag": [
            {"id": "r1", "text": "y" * 483, "evidence_ids": ["E001"]},
        ],
        "limitations": ["edition 1925-08"],
        "instructions": "test instruction",
        "prompt_version": "explanation-prompt-v1",
        "prompt_sha256": "sha-1",
        "response_schema": {"type": "object"},
    }


class ClassificationTests(unittest.TestCase):
    def test_classify_status(self):
        self.assertIsNone(classify_status(200))
        self.assertEqual(classify_status(401), "auth")
        self.assertEqual(classify_status(403), "auth")
        self.assertEqual(classify_status(429), "rate_limit")
        self.assertEqual(classify_status(500), "server")
        self.assertEqual(classify_status(503), "server")
        self.assertEqual(classify_status(400), "invalid_response")
        self.assertEqual(classify_status(302), "invalid_response")

    def test_classify_exception(self):
        self.assertEqual(classify_exception(httpx.TimeoutException("t")), "timeout")
        self.assertEqual(classify_exception(httpx.ConnectError("c")), "network")
        self.assertEqual(
            classify_exception(json.JSONDecodeError("bad", "doc", 0)), "invalid_response"
        )
        self.assertEqual(classify_exception(ValueError("v")), "invalid_response")

    def test_is_retryable(self):
        for code in ("network", "timeout", "rate_limit", "server"):
            self.assertTrue(is_retryable(code), code)
        for code in ("auth", "invalid_response"):
            self.assertFalse(is_retryable(code), code)


class RetryTests(unittest.TestCase):
    def test_auth_failure_never_retried(self):
        calls = []
        client = client_with(lambda request: (calls.append(request), httpx.Response(401, json={"error": "nope"}))[1])
        with self.assertRaises(ModelClientError) as error:
            run(client.post(SETTINGS["endpoint"], {"a": 1}))
        self.assertEqual(error.exception.code, "auth")
        self.assertEqual(len(calls), 1)

    def test_rate_limit_retried_then_raises(self):
        calls = []
        client = client_with(lambda request: (calls.append(request), httpx.Response(429, json={"error": "slow"}))[1])
        with self.assertRaises(ModelClientError) as error:
            run(client.post(SETTINGS["endpoint"], {"a": 1}))
        self.assertEqual(error.exception.code, "rate_limit")
        self.assertEqual(len(calls), MAX_ATTEMPTS)

    def test_server_error_retried_then_raises(self):
        calls = []
        client = client_with(lambda request: (calls.append(request), httpx.Response(503, json={"error": "down"}))[1])
        with self.assertRaises(ModelClientError) as error:
            run(client.post(SETTINGS["endpoint"], {"a": 1}))
        self.assertEqual(error.exception.code, "server")
        self.assertEqual(len(calls), MAX_ATTEMPTS)

    def test_transient_then_success(self):
        calls = []
        attempts = {"n": 0}

        def handler(request):
            calls.append(request)
            attempts["n"] += 1
            if attempts["n"] < 3:
                return httpx.Response(503, json={"error": "down"})
            return httpx.Response(200, json={"ok": True, "value": 7})

        client = client_with(handler)
        self.assertEqual(run(client.post(SETTINGS["endpoint"], {"a": 1})), {"ok": True, "value": 7})
        self.assertEqual(len(calls), 3)

    def test_network_error_retried(self):
        calls = []

        def handler(request):
            calls.append(request)
            raise httpx.ConnectError("unreachable", request=request)

        client = client_with(handler)
        with self.assertRaises(ModelClientError) as error:
            run(client.post(SETTINGS["endpoint"], {"a": 1}))
        self.assertEqual(error.exception.code, "network")
        self.assertEqual(len(calls), MAX_ATTEMPTS)

    def test_timeout_retried(self):
        calls = []

        def handler(request):
            calls.append(request)
            raise httpx.TimeoutException("slow", request=request)

        client = client_with(handler)
        with self.assertRaises(ModelClientError) as error:
            run(client.post(SETTINGS["endpoint"], {"a": 1}))
        self.assertEqual(error.exception.code, "timeout")
        self.assertEqual(len(calls), MAX_ATTEMPTS)

    def test_invalid_json_not_retried(self):
        calls = []
        client = client_with(lambda request: (calls.append(request), httpx.Response(200, content=b"not json"))[1])
        with self.assertRaises(ModelClientError) as error:
            run(client.post(SETTINGS["endpoint"], {"a": 1}))
        self.assertEqual(error.exception.code, "invalid_response")
        self.assertEqual(len(calls), 1)

    def test_oversized_response_not_retried(self):
        calls = []
        client = client_with(lambda request: (calls.append(request), httpx.Response(200, content=b"x" * 262145))[1])
        with self.assertRaises(ModelClientError) as error:
            run(client.post(SETTINGS["endpoint"], {"a": 1}))
        self.assertEqual(error.exception.code, "invalid_response")
        self.assertEqual(len(calls), 1)

    def test_redirect_not_retried(self):
        calls = []
        client = client_with(
            lambda request: (calls.append(request), httpx.Response(302, headers={"location": "https://other.example"}))[1]
        )
        with self.assertRaises(ModelClientError) as error:
            run(client.post(SETTINGS["endpoint"], {"a": 1}))
        self.assertEqual(error.exception.code, "invalid_response")
        self.assertEqual(len(calls), 1)

    def test_max_attempts_one_never_retries(self):
        # Discovery contract: one list/probe failure stops, no HTTP retry.
        calls = []
        client = client_with(
            lambda request: (calls.append(request), httpx.Response(503, json={"error": "down"}))[1],
            max_attempts=1,
        )
        with self.assertRaises(ModelClientError) as error:
            run(client.post(SETTINGS["endpoint"], {"a": 1}))
        self.assertEqual(error.exception.code, "server")
        self.assertEqual(len(calls), 1)

    def test_invalid_max_attempts_rejected(self):
        # max_attempts <= 0 would leave the request loop unentered and
        # `raise last_error` would raise None (TypeError) instead of a
        # typed model error. Reject it at construction, fail closed.
        for bad in (0, -1):
            with self.assertRaises(ValueError):
                ControlledModelClient(SETTINGS, max_attempts=bad)
        client = ControlledModelClient(SETTINGS, max_attempts=1)
        self.assertEqual(client.max_attempts, 1)


class PrivacyTests(unittest.TestCase):
    def test_sanitize_truncates_evidence_to_120(self):
        clean = sanitize_context(synthetic_context())
        self.assertEqual(len(clean["evidence"]["E001"]["original_text"]), 120)
        self.assertEqual(clean["evidence"]["E001"]["original_text"], "x" * 120)
        self.assertEqual(clean["evidence"]["E002"]["original_text"], "short text")
        # Metadata survives.
        self.assertEqual(clean["evidence"]["E001"]["classic_title"], "Test Classic")

    def test_sanitize_truncates_rag_text_to_120(self):
        clean = sanitize_context(synthetic_context())
        self.assertEqual(len(clean["rag"][0]["text"]), 120)
        self.assertEqual(clean["rag"][0]["evidence_ids"], ["E001"])

    def test_sanitize_handles_real_retriever_row_shape(self):
        # Exact row shape CanonicalRetriever.retrieve produces
        # (rag_context.py): text is the only sealed text; the other
        # fields are ids/metadata and must survive untouched.
        context = synthetic_context()
        context["rag"] = [{
            "id": "row-1",
            "entity_id": "entity-1",
            "domain": "yijing",
            "variant": "test-variant",
            "source_variant": None,
            "text": "y" * 483,
            "evidence_ids": ["E001"],
            "scope": "contextual classical quotation; not permission to recompute the chart",
        }]
        clean = sanitize_context(context)
        self.assertEqual(len(clean["rag"][0]["text"]), 120)
        self.assertEqual(clean["rag"][0]["entity_id"], "entity-1")
        self.assertEqual(clean["rag"][0]["domain"], "yijing")
        self.assertEqual(clean["rag"][0]["evidence_ids"], ["E001"])
        self.assertEqual(
            clean["rag"][0]["scope"],
            "contextual classical quotation; not permission to recompute the chart",
        )

    def test_sanitize_removes_birth_instant(self):
        clean = sanitize_context(synthetic_context())
        blob = json.dumps(clean, ensure_ascii=False)
        self.assertNotIn(BIRTH, blob)
        self.assertIn("[REDACTED]", blob)
        # Chart facts survive (pillars are the legitimate content).
        self.assertEqual(clean["chart"]["pillars"]["year"], "庚辰")
        self.assertEqual(clean["facts"]["/chart/pillars/year"], "庚辰")

    def test_sanitize_preserves_historical_dates(self):
        clean = sanitize_context(synthetic_context())
        self.assertEqual(clean["limitations"], ["edition 1925-08"])

    def test_sanitize_drops_credential_keys(self):
        context = synthetic_context()
        context["chart"]["api_key"] = "should-not-be-here"
        context["chart"]["token"] = "should-not-be-here"
        clean = sanitize_context(context)
        blob = json.dumps(clean, ensure_ascii=False)
        self.assertNotIn("should-not-be-here", blob)
        self.assertNotIn("api_key", clean["chart"])
        self.assertNotIn("token", clean["chart"])

    def test_sanitize_raises_when_api_key_in_payload(self):
        context = synthetic_context()
        context["chart"]["note"] = "key is test-only-key here"
        with self.assertRaises(ModelClientError) as error:
            sanitize_context(context, api_key="test-only-key")
        self.assertEqual(error.exception.code, "invalid_response")

    def test_sanitized_context_still_validates_replies(self):
        clean = sanitize_context(synthetic_context())
        reply = valid_reply(clean)
        validated = validate_reply(reply, clean)
        self.assertTrue(validated["claims"])

    def test_redact_for_log(self):
        payload = {
            "api_key": "test-only-key",
            "note": "born " + BIRTH,
            "long": "z" * 200,
            "nested": {"secret": "shh", "ok": "fine"},
        }
        redacted = redact_for_log(payload, api_key="test-only-key")
        blob = json.dumps(redacted, ensure_ascii=False)
        self.assertNotIn("test-only-key", blob)
        self.assertNotIn(BIRTH, blob)
        self.assertNotIn("shh", blob)
        self.assertEqual(redacted["api_key"], "[REDACTED]")
        self.assertEqual(redacted["nested"]["secret"], "[REDACTED]")
        self.assertEqual(redacted["nested"]["ok"], "fine")
        self.assertTrue(len(redacted["long"]) <= 81)
        self.assertTrue(redacted["long"].endswith("…"))


class LogSafetyTests(unittest.TestCase):
    def test_safe_url_strips_query_and_userinfo(self):
        # Log lines carry only scheme + hostname (+ a safe numeric port):
        # a credential smuggled into a URL path, query or userinfo must
        # never reach a log record. The path is dropped entirely, not
        # allow-listed — settings_from_environment allows arbitrary paths.
        self.assertEqual(
            _safe_url("https://user:secret@model.example.test/v1/explain?api_key=abc&x=1"),
            "https://model.example.test",
        )
        self.assertEqual(
            _safe_url("https://model.example.test/v1/explain"),
            "https://model.example.test",
        )
        self.assertEqual(_safe_url("https://model.example.test/v1/explain?k=v"), "https://model.example.test")
        # A port is purely numeric and cannot contain a key, so it is kept.
        self.assertEqual(
            _safe_url("https://model.example.test:8443/v1/explain"),
            "https://model.example.test:8443",
        )
        self.assertEqual(
            _safe_url("https://user:pw@model.example.test:8443/v1/k?api_key=abc#frag"),
            "https://model.example.test:8443",
        )


class LogPathLeakTests(unittest.TestCase):
    """Negative tests for the _safe_url path leak (PR #567 HOLD).

    A test-only fake key is placed SIMULTANEOUSLY in settings["key"], the
    URL path, the URL query and the URL userinfo. The URL path also carries
    a second distinct secret fragment, and the request body carries a
    private string plus a birth instant. On a 401, a retried 503 and a
    network exception, the captured logs must contain NONE of them — only
    the safe scheme://host[:port] form. These tests FAIL against the old
    _safe_url (which kept the path) and PASS against the new one.
    """

    FAKE_KEY = "test-only-key-9f3a7b"
    SECRET_FRAGMENT = "secret-fragment-xyz"
    BODY_SECRET = "secret-body-xyz"
    LEAKY_URL = (
        "https://leakuser:test-only-key-9f3a7b@model.example.test:8443"
        "/v1/secret-fragment-xyz/test-only-key-9f3a7b/explain"
        "?api_key=test-only-key-9f3a7b&trace=secret-fragment-xyz"
    )
    SAFE_HOST = "https://model.example.test:8443"

    def _leaky_client(self, handler, max_attempts=MAX_ATTEMPTS):
        settings = dict(SETTINGS)
        settings["endpoint"] = self.LEAKY_URL
        settings["key"] = self.FAKE_KEY
        return ControlledModelClient(
            settings, transport=httpx.MockTransport(handler),
            max_attempts=max_attempts, backoff_base=0.0,
            sleep=lambda seconds: asyncio.sleep(0),
        )

    def _leaky_body(self):
        return {
            "a": 1,
            "private_note": self.BODY_SECRET,
            "note": "born " + BIRTH,
        }

    def _assert_logs_clean(self, joined):
        # Leak assertions FIRST: on the old _safe_url these fail because the
        # log line carries the path (which holds the fake key and the secret
        # fragment). Then the safe-host assertion proves a log line WAS
        # emitted, so the absence assertions above are not vacuous.
        self.assertNotIn(self.FAKE_KEY, joined)
        self.assertNotIn(self.SECRET_FRAGMENT, joined)
        self.assertNotIn(self.BODY_SECRET, joined)
        self.assertNotIn(BIRTH, joined)
        self.assertNotIn("leakuser", joined)
        self.assertNotIn("api_key", joined)
        self.assertNotIn("/v1/", joined)
        # The log line WAS emitted (safe host present).
        self.assertIn(self.SAFE_HOST, joined)

    def test_auth_failure_logs_never_contain_key_in_path(self):
        client = self._leaky_client(
            lambda request: httpx.Response(401, json={"error": "nope"})
        )
        with self.assertLogs("tianji_kb.model_client", level="WARNING") as logs:
            with self.assertRaises(ModelClientError) as error:
                run(client.post(self.LEAKY_URL, self._leaky_body()))
        self.assertEqual(error.exception.code, "auth")
        joined = "\n".join(logs.output)
        self.assertIn("auth", joined)
        self._assert_logs_clean(joined)

    def test_server_error_retry_logs_never_contain_key_in_path(self):
        calls = []
        client = self._leaky_client(
            lambda request: (calls.append(request), httpx.Response(503, json={"error": "down"}))[1]
        )
        with self.assertLogs("tianji_kb.model_client", level="WARNING") as logs:
            with self.assertRaises(ModelClientError) as error:
                run(client.post(self.LEAKY_URL, self._leaky_body()))
        self.assertEqual(error.exception.code, "server")
        self.assertEqual(len(calls), MAX_ATTEMPTS)
        joined = "\n".join(logs.output)
        self.assertIn("server", joined)
        self._assert_logs_clean(joined)

    def test_network_error_logs_never_contain_key_in_path(self):
        calls = []

        def handler(request):
            calls.append(request)
            raise httpx.ConnectError("unreachable", request=request)

        client = self._leaky_client(handler)
        with self.assertLogs("tianji_kb.model_client", level="WARNING") as logs:
            with self.assertRaises(ModelClientError) as error:
                run(client.post(self.LEAKY_URL, self._leaky_body()))
        self.assertEqual(error.exception.code, "network")
        self.assertEqual(len(calls), MAX_ATTEMPTS)
        joined = "\n".join(logs.output)
        self.assertIn("network", joined)
        self._assert_logs_clean(joined)


class BlockedWithoutCredentialsTests(unittest.TestCase):
    def test_provider_from_environment_returns_none_without_credentials(self):
        ai_keys = [key for key in os.environ if key.startswith("TIANJI_AI_")]
        with patch.dict(os.environ, {}, clear=False):
            for key in ai_keys:
                os.environ.pop(key, None)
            os.environ["TIANJI_AI_PROVIDER"] = "disabled"
            self.assertIsNone(provider_from_environment())
            self.assertFalse(provider_configured())

    def test_explain_without_credentials_returns_provider_not_configured(self):
        # The explain path must return a clear BLOCKED, never a simulated
        # success, and must not change the deterministic chart. This needs
        # the built production runtime, so it runs in sealed acceptance
        # and skips (honestly, not as a pass) in a plain public checkout.
        ai_keys = [key for key in os.environ if key.startswith("TIANJI_AI_")]
        with patch.dict(os.environ, {}, clear=False):
            for key in ai_keys:
                os.environ.pop(key, None)
            os.environ["TIANJI_AI_PROVIDER"] = "disabled"
            client = TestClient(create_app())
            plain = client.post(
                "/api/v1/execute",
                json={"domain": "yijing", "input": EXAMPLES["yijing"]},
            )
            if plain.status_code == 503 and plain.json().get("detail", {}).get("code") == "runtime_unavailable":
                self.skipTest("production runtime not built in this checkout; sealed acceptance covers this path")
            self.assertEqual(plain.status_code, 200)
            plain = plain.json()
            explained = client.post(
                "/api/v1/execute",
                json={"domain": "yijing", "input": EXAMPLES["yijing"], "explain": True},
            )
            self.assertEqual(explained.status_code, 200)
            data = explained.json()
            self.assertEqual(data["explanation_status"], "failed")
            self.assertEqual(data["explanation_error"], "provider_not_configured")
            self.assertIsNone(data["explanation"])
            for key in ["chart", "trace", "evidence", "rule_matches"]:
                self.assertEqual(data[key], plain[key])


class WiringTests(unittest.TestCase):
    def test_explanation_service_sanitizes_before_provider(self):
        seen = []

        class CapturingProvider:
            async def explain(self, context):
                seen.append(copy.deepcopy(context))
                return valid_reply(context)

        class FakeRetriever:
            def retrieve(self, raw):
                return [{"id": "r1", "text": "y" * 483, "evidence_ids": ["E001"]}]

        raw = {
            "domain": "yijing",
            "variant": "test-variant",
            "mode": "production",
            "result": {
                "pillars": {"year": "庚辰", "month": "己丑", "day": "丙午", "hour": "甲午"},
                "note": "born " + BIRTH,
            },
            "rule_matches": [],
            "trace": [],
            "evidence": {
                "E001": {
                    "original_text": "x" * 177,
                    "classic_title": "Test Classic",
                    "source_url": "https://example.test/classic",
                },
            },
            "scope": "test scope",
            "unresolved": [],
            "interpretation_contract": {},
        }
        service = ExplanationService(
            CapturingProvider(), retriever=FakeRetriever(),
            prompt_version="explanation-prompt-v1",
        )
        result = run(service.explain(raw))
        self.assertTrue(result["claims"])
        self.assertEqual(len(seen), 1)
        received = seen[0]
        self.assertEqual(len(received["evidence"]["E001"]["original_text"]), 120)
        self.assertEqual(len(received["rag"][0]["text"]), 120)
        blob = json.dumps(received, ensure_ascii=False)
        self.assertNotIn(BIRTH, blob)
        self.assertIn("[REDACTED]", blob)
        # The reply is validated against the REAL context, so the citation
        # still binds to the full real evidence (not the truncated copy the
        # model saw).
        citation = result["claims"][0]["citations"][0]
        self.assertEqual(citation["evidence_id"], "E001")
        self.assertEqual(len(citation["source_ref"]["original_text"]), 177)

    def test_provider_from_environment_enables_bounded_retry(self):
        calls = []
        attempts = {"n": 0}

        def handler(request):
            calls.append(request)
            attempts["n"] += 1
            if attempts["n"] < 3:
                return httpx.Response(503, json={"error": "down"})
            context = json.loads(request.content)["context"]
            return httpx.Response(200, json=valid_reply(context))

        with patch.dict(os.environ, ENV):
            provider = provider_from_environment()
        self.assertEqual(provider.max_attempts, MAX_ATTEMPTS)
        provider.transport = httpx.MockTransport(handler)
        context = synthetic_context()
        reply = run(provider.explain(copy.deepcopy(context)))
        self.assertTrue(validate_reply(reply, context)["claims"])
        self.assertEqual(len(calls), 3)
        # The key is a header only; it never appears in the request body.
        for request in calls:
            self.assertNotIn("test-only-key", request.content.decode())

    def test_no_credential_in_logs(self):
        client = client_with(
            lambda request: httpx.Response(401, json={"error": "nope"})
        )
        with self.assertLogs("tianji_kb.model_client", level="WARNING") as logs:
            with self.assertRaises(ModelClientError):
                run(client.post(SETTINGS["endpoint"], {"a": 1}))
        joined = "\n".join(logs.output)
        self.assertNotIn("test-only-key", joined)
        self.assertIn("auth", joined)


if __name__ == "__main__":
    unittest.main()
