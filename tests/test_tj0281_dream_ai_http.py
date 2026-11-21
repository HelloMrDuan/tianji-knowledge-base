"""TJ-028.1 sub-slice: admin AI-explain endpoint over a local mock model.

HTTP integration tests for POST /api/v1/admin/research/dream/ai-explain
against a local OpenAI-compatible mock server on 127.0.0.1 (stdlib
ThreadingHTTPServer, fake credentials). No real model is called and no
real AMD/DuanYan endpoint is contacted: the only network traffic is
the TestClient talking to the mock on localhost.

The audited retrieval is patched at the test boundary
(``tianji_kb.api.retrieve_dream_culture``) because the production
runtime cannot be built from the public checkout alone (the sealed
Canonical data is absent locally); the real retrieve() path is
covered by the existing dream API tests in private CI. The endpoint
code under test is real: auth, retrieval contract checks, the
business service, the controlled adapter and the real provider
transport all run.
"""
import json
import os
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from unittest.mock import patch

from fastapi.testclient import TestClient

from tianji_kb.admin_audit import AuditLog
from tianji_kb.admin_drafts import DraftStore
from tianji_kb.api import create_app

ENDPOINT = "/api/v1/admin/research/dream/ai-explain"
TOKEN = "test-admin-token"
HEADERS = {"Authorization": "Bearer test-admin-token"}

EVIDENCE_ID = "a1b2c3d4e5f6a7b8c9d0e1f2"
LONG_QUOTE = "见人死自死皆吉" + "，" + "古籍引文" * 60  # > 120 chars


def _retrieval_fixture():
    """A retrieval result in the real retrieve() shape (death scene)."""
    candidate = {
        "term_id": "dream.term.death",
        "symbol": "死",
        "scene": "见人死自死",
        "source": "周公解梦",
        "locator": "卷一·死生章",
        "original_text_short_quote": "见人死自死皆吉",
        "interpretation": "见人死自死皆吉",
        "interpretation_type": "traditional",
        "limitations": [],
        "confidence": "C",
        "cultural_context": "",
        "evidence_level": "C",
        "evidence_ids": [EVIDENCE_ID],
        "personal_prediction": False,
    }
    return {
        "domain": "dream",
        "variant": "traditional",
        "mode": "research",
        "status": "reviewed_interpretation_candidates",
        "entities": [],
        "matched_interpretations": [candidate],
        "interpretation_candidates": [candidate],
        "narrative_observations": [],
        "unreviewed_input_topics": [],
        "evidence": {
            EVIDENCE_ID: {
                "source_id": "dream.source.zhougong",
                "section_id": "dream.section.death",
                "original_text": LONG_QUOTE,
                "classic_id": "dream.classic.zhougong",
                "classic_title": "周公解梦",
                "chapter_title": "死生章",
                "locator": "卷一·死生章",
                "source_url": "https://example.invalid/zhougong",
                "commit": "abc123",
                "sha256": "def456",
                "evidence_level": "C",
            }
        },
        "retrieval": [],
        "retrieval_method": "bounded_scene_match_and_reviewed_rag",
        "chart_generated": False,
        "public_enabled": False,
        "ai_enabled": False,
        "limitations": ["仅审核 12 个具体传统梦场景；有限句式识别不是完整自然语言理解。"],
    }


def _valid_reply():
    return {
        "domain": "dream",
        "variant": "traditional",
        "mode": "research",
        "claims": [
            {
                "text": "《周公解梦》载“见人死自死皆吉”，此条仅言梦中见人死自死的传统说法，不作个人运势判断。",
                "evidence_ids": [EVIDENCE_ID],
                "quotes": [{"evidence_id": EVIDENCE_ID, "text": "见人死自死皆吉"}],
            }
        ],
    }


class _MockState:
    def __init__(self):
        self.mode = "valid"
        self.calls = 0
        self.sleep_seconds = 0


def _make_handler(state):
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass

        def do_POST(self):
            state.calls += 1
            length = int(self.headers.get("Content-Length") or 0)
            self.rfile.read(length)
            if self.path != "/chat/completions":
                self.send_response(404)
                self.end_headers()
                return
            if state.mode == "rate_limit":
                body = json.dumps({"error": {"message": "rate limited"}}).encode()
                self.send_response(429)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
                return
            if state.sleep_seconds:
                import time

                time.sleep(state.sleep_seconds)
            if state.mode == "non_json":
                content = "this is not json"
            elif state.mode == "invalid_schema":
                content = json.dumps({"nope": True})
            else:
                content = json.dumps(_valid_reply())
            body = json.dumps(
                {"choices": [{"message": {"role": "assistant", "content": content}}]}
            ).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

    return Handler


class AdminDreamAiExplainHttpTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.state = _MockState()
        cls.server = ThreadingHTTPServer(
            ("127.0.0.1", 0), _make_handler(cls.state)
        )
        cls.port = cls.server.server_address[1]
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()

    def setUp(self):
        self.state.mode = "valid"
        self.state.calls = 0
        self.state.sleep_seconds = 0
        self._retrieve_patch = patch(
            "tianji_kb.api.retrieve_dream_culture",
            return_value=_retrieval_fixture(),
        )
        self._retrieve_patch.start()

    def tearDown(self):
        self._retrieve_patch.stop()

    def _env(self, **overrides):
        # The mock lives on localhost: no proxy is needed. The sandbox
        # NO_PROXY carries bracketed IPv6 literals (``[::1]``) that
        # httpx's trust_env parsing rejects at client construction, so
        # proxy variables are stripped here; the transport under test
        # is unchanged.
        env = {
            k: v for k, v in os.environ.items()
            if not k.startswith("TIANJI_AI_") and "proxy" not in k.lower()
        }
        env.update(
            {
                "TIANJI_AI_PROVIDER": "openai-compatible",
                "TIANJI_AI_BASE_URL": f"http://127.0.0.1:{self.port}",
                "TIANJI_AI_API_KEY": "test-key-123",
                "TIANJI_AI_MODEL": "test-model",
            }
        )
        env.update(overrides)
        return env

    def _client(self):
        return TestClient(
            create_app(
                admin_read_token=TOKEN,
                admin_audit_log=AuditLog(),
                admin_draft_store=DraftStore(),
            )
        )

    def _post(self, client, payload=None):
        return client.post(
            ENDPOINT,
            json=payload if payload is not None else {"dream_text": "我梦见自己死了"},
            headers=HEADERS,
        )

    def test_explained_over_mock_model(self):
        with patch.dict(os.environ, self._env(), clear=True):
            response = self._post(self._client())
        self.assertEqual(response.status_code, 200, response.text)
        data = response.json()
        self.assertEqual(data["api_version"], "v1")
        self.assertTrue(data["read_only"])
        self.assertTrue(data["research_only"])
        self.assertFalse(data["public_release"])
        self.assertFalse(data["ai_enabled"])
        result = data["result"]
        self.assertEqual(result["verdict"], "explained")
        self.assertEqual(result["dream_text"], "我梦见自己死了")
        self.assertFalse(result["ai_enabled"])
        self.assertFalse(result["personal_prediction"])
        self.assertEqual(len(result["claims"]), 1)
        self.assertEqual(
            result["claims"][0]["citations"][0]["evidence_id"], EVIDENCE_ID
        )
        self.assertEqual(self.state.calls, 1)

    def test_rate_limit_is_distinct_refusal(self):
        self.state.mode = "rate_limit"
        with patch.dict(os.environ, self._env(), clear=True):
            response = self._post(self._client())
        self.assertEqual(response.status_code, 200, response.text)
        result = response.json()["result"]
        self.assertEqual(result["verdict"], "provider_rate_limited")
        self.assertEqual(result["claims"], [])
        # Bounded retry: one initial attempt plus two transient retries.
        self.assertEqual(self.state.calls, 3)

    def test_slow_model_is_timeout_refusal(self):
        self.state.sleep_seconds = 3
        with patch.dict(os.environ, self._env(TIANJI_AI_TIMEOUT_SECONDS="1"), clear=True):
            response = self._post(self._client())
        self.assertEqual(response.status_code, 200, response.text)
        result = response.json()["result"]
        self.assertEqual(result["verdict"], "provider_timeout")
        self.assertEqual(result["claims"], [])

    def test_non_json_content_is_invalid_response(self):
        self.state.mode = "non_json"
        with patch.dict(os.environ, self._env(), clear=True):
            response = self._post(self._client())
        self.assertEqual(response.status_code, 200, response.text)
        result = response.json()["result"]
        self.assertEqual(result["verdict"], "invalid_model_response")
        self.assertEqual(result["claims"], [])
        self.assertEqual(self.state.calls, 1)

    def test_invalid_schema_is_invalid_response(self):
        self.state.mode = "invalid_schema"
        with patch.dict(os.environ, self._env(), clear=True):
            response = self._post(self._client())
        self.assertEqual(response.status_code, 200, response.text)
        result = response.json()["result"]
        self.assertEqual(result["verdict"], "invalid_model_response")
        self.assertEqual(result["claims"], [])
        self.assertEqual(self.state.calls, 1)

    def test_not_configured_makes_no_model_call(self):
        env = {
            k: v for k, v in os.environ.items()
            if not k.startswith("TIANJI_AI_") and "proxy" not in k.lower()
        }
        with patch.dict(os.environ, env, clear=True):
            response = self._post(self._client())
        self.assertEqual(response.status_code, 200, response.text)
        result = response.json()["result"]
        self.assertEqual(result["verdict"], "not_configured")
        self.assertFalse(result["ai_enabled"])
        self.assertEqual(result["claims"], [])
        self.assertEqual(self.state.calls, 0)

    def test_admin_auth_is_enforced(self):
        with patch.dict(os.environ, self._env(), clear=True):
            client = self._client()
            for headers in ({}, {"Authorization": "Bearer wrong-token"},
                            {"Authorization": "Bearer "}):
                response = client.post(
                    ENDPOINT, json={"dream_text": "我梦见自己死了"}, headers=headers
                )
                self.assertEqual(response.status_code, 401, response.text)
                self.assertEqual(
                    response.json()["detail"]["code"], "admin_unauthorized"
                )
            unavailable = TestClient(
                create_app(
                    admin_read_token="",
                    admin_audit_log=AuditLog(),
                    admin_draft_store=DraftStore(),
                )
            )
            response = unavailable.post(
                ENDPOINT, json={"dream_text": "我梦见自己死了"}, headers=HEADERS
            )
            self.assertEqual(response.status_code, 503)
            self.assertEqual(
                response.json()["detail"]["code"], "admin_auth_not_configured"
            )
        self.assertEqual(self.state.calls, 0)

    def test_input_validation(self):
        with patch.dict(os.environ, self._env(), clear=True):
            client = self._client()
            for bad_text in ("", "梦", "梦" * 501):
                response = self._post(client, {"dream_text": bad_text})
                self.assertEqual(response.status_code, 422, response.text)
            response = self._post(client, {})
            self.assertEqual(response.status_code, 422)
        self.assertEqual(self.state.calls, 0)

    def test_unavailable_runtime_fails_closed(self):
        # Without the retrieval patch, the local public checkout has no
        # production runtime (sealed Canonical data is absent), so
        # retrieve() raises RuntimeUnavailable. The endpoint maps that
        # ValueError to 422, the same mapping the existing admin
        # research endpoint uses; it never reaches the adapter and
        # never calls a model.
        self._retrieve_patch.stop()
        try:
            with patch.dict(os.environ, self._env(), clear=True):
                response = self._post(self._client())
        finally:
            self._retrieve_patch.start()
        self.assertEqual(response.status_code, 422, response.text)
        self.assertEqual(
            response.json()["detail"]["code"], "invalid_dream_input"
        )
        self.assertEqual(self.state.calls, 0)


if __name__ == "__main__":
    unittest.main()
