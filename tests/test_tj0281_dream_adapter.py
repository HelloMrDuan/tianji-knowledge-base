"""TJ-028.1 Line C: dream model adapter preparation (config, context, validation).

All model calls in this file go through an explicitly labelled local
test double (``LabelledTestDoubleDreamProvider``). They are NOT
real-model acceptance: no model vendor is configured and no
``TIANJI_AI_*`` credential exists in the trusted environment, so
end-to-end real-model verification is BLOCKED pending a vendor decision
and credentials. The retrieval fixture below matches the real
``dream_knowledge.retrieve()`` output shape (verified against
``tests/test_tj0192_dream_batch03.py``: candidate fields, evidence
records carrying ``original_text`` / ``classic_title`` / ``source_url`` /
``commit`` / ``sha256`` / ``locator``, ``personal_prediction`` False);
it is a shape fixture, not a model result.
"""
import asyncio
import copy
import json
import os
import unittest
from unittest.mock import patch

from tianji_kb.dream_model_adapter import (
    DreamAdapterError,
    DreamModelAdapter,
    build_dream_context,
    validate_dream_reply,
)
from tianji_kb.dream_provider_config import (
    describe,
    load_dream_provider_config,
    provider_configured,
)
from tianji_kb.model_client import ModelClientError

EVIDENCE_ID = "a1b2c3d4e5f6a7b8c9d0e1f2"
LONG_QUOTE = "见人死自死皆吉" + "，" + "古籍引文" * 60  # > 120 chars


def _retrieval_fixture():
    """A retrieval result in the real retrieve() shape (death scene)."""
    candidate = {
        "term_id": "dream.term.death",
        "symbol": "死",
        "scene": "见人死自死",
        "scene_alias_hits": ["见人死"],
        "input_matches": [],
        "rule_id": "dream.phase2.death",
        "match_kind": "reviewed_cultural_scene_retrieval",
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


def _configured_env():
    return {
        "TIANJI_AI_PROVIDER": "json-http",
        "TIANJI_AI_BASE_URL": "https://example.invalid/v1",
        "TIANJI_AI_API_KEY": "test-key-123",
        "TIANJI_AI_MODEL": "test-model",
    }


def _clear_ai_env():
    return {k: v for k, v in os.environ.items() if not k.startswith("TIANJI_AI_")}


class LabelledTestDoubleDreamProvider:
    """Explicitly labelled local test double. NOT a real model.

    Returns a canned reply and records the contexts it receives. It
    must never be presented as real-model acceptance.
    """

    def __init__(self, reply=None):
        self.reply = reply if reply is not None else _valid_reply()
        self.calls = 0
        self.contexts = []

    async def explain(self, context):
        self.calls += 1
        self.contexts.append(copy.deepcopy(context))
        if isinstance(self.reply, Exception):
            raise self.reply
        return copy.deepcopy(self.reply)


class ConfigTests(unittest.TestCase):
    def test_no_env_is_not_configured(self):
        with patch.dict(os.environ, _clear_ai_env(), clear=True):
            config = load_dream_provider_config()
        self.assertFalse(config["configured"])
        self.assertEqual(config["reason"], "not_configured")
        self.assertIsNone(config["settings"])
        self.assertFalse(provider_configured())

    def test_invalid_driver_is_invalid_configuration(self):
        env = _clear_ai_env()
        env["TIANJI_AI_PROVIDER"] = "bogus-driver"
        with patch.dict(os.environ, env, clear=True):
            config = load_dream_provider_config()
        self.assertFalse(config["configured"])
        self.assertEqual(config["reason"], "invalid_configuration")

    def test_valid_env_is_configured_and_describe_has_no_key(self):
        env = _clear_ai_env()
        env.update(_configured_env())
        with patch.dict(os.environ, env, clear=True):
            config = load_dream_provider_config()
            self.assertTrue(config["configured"])
            self.assertEqual(config["driver"], "json-http")
            self.assertEqual(config["model"], "test-model")
            self.assertTrue(provider_configured())
            description = describe(config)
        blob = json.dumps(description, ensure_ascii=False)
        self.assertNotIn("test-key-123", blob)
        self.assertNotIn("key", [k.lower() for k in description])
        self.assertEqual(description["endpoint_host"], "https://example.invalid")
        self.assertNotIn("/v1", description["endpoint_host"])

    def test_missing_key_is_invalid_configuration(self):
        env = _clear_ai_env()
        env.update(_configured_env())
        del env["TIANJI_AI_API_KEY"]
        with patch.dict(os.environ, env, clear=True):
            config = load_dream_provider_config()
        self.assertFalse(config["configured"])
        self.assertEqual(config["reason"], "invalid_configuration")


class ContextTests(unittest.TestCase):
    def test_context_truncates_narrative_and_caps_evidence(self):
        context = build_dream_context("我梦见" + "很长的梦" * 200, _retrieval_fixture())
        self.assertEqual(len(context["dream_narrative"]), 500)
        self.assertEqual(len(context["evidence"][EVIDENCE_ID]["original_text"]), 120)

    def test_context_strips_birth_instant_and_credentials(self):
        retrieval = _retrieval_fixture()
        retrieval["evidence"][EVIDENCE_ID]["api_key"] = "should-be-dropped"
        context = build_dream_context(
            "我梦见自己死了，出生于1990-05-06T14:30:00+08:00",
            retrieval,
            api_key="test-key-123",
        )
        blob = json.dumps(context, ensure_ascii=False)
        self.assertNotIn("1990-05-06T14:30:00+08:00", blob)
        self.assertIn("[REDACTED]", blob)
        self.assertNotIn("should-be-dropped", blob)
        self.assertNotIn("test-key-123", blob)

    def test_context_fails_closed_when_key_leaks_into_payload(self):
        retrieval = _retrieval_fixture()
        retrieval["evidence"][EVIDENCE_ID]["original_text"] = "test-key-123"
        with self.assertRaises(ModelClientError):
            build_dream_context("我梦见自己死了", retrieval, api_key="test-key-123")

    def test_context_rejects_bad_inputs(self):
        with self.assertRaises(DreamAdapterError) as caught:
            build_dream_context("", _retrieval_fixture())
        self.assertEqual(caught.exception.code, "invalid_input")
        with self.assertRaises(DreamAdapterError) as caught:
            build_dream_context("我梦见自己死了", {"domain": "bazi"})
        self.assertEqual(caught.exception.code, "invalid_input")


class AdapterTests(unittest.IsolatedAsyncioTestCase):
    def _configured(self):
        env = _clear_ai_env()
        env.update(_configured_env())
        return env

    async def test_abstains_without_reviewed_candidates(self):
        retrieval = _retrieval_fixture()
        retrieval["status"] = "no_reviewed_interpretation"
        retrieval["matched_interpretations"] = []
        retrieval["interpretation_candidates"] = []
        provider = LabelledTestDoubleDreamProvider()
        adapter = DreamModelAdapter(provider)
        result = await adapter.explain("我梦见考试", retrieval)
        self.assertEqual(result["status"], "abstained_no_reviewed_interpretation")
        self.assertFalse(result["ai_enabled"])
        self.assertFalse(result["personal_prediction"])
        self.assertEqual(result["claims"], [])
        self.assertEqual(provider.calls, 0)

    async def test_not_configured_without_provider(self):
        provider = LabelledTestDoubleDreamProvider()
        adapter = DreamModelAdapter(provider)
        with patch.dict(os.environ, _clear_ai_env(), clear=True):
            result = await adapter.explain("我梦见自己死了", _retrieval_fixture())
        self.assertEqual(result["status"], "not_configured")
        self.assertFalse(result["ai_enabled"])
        self.assertEqual(result["claims"], [])
        self.assertEqual(provider.calls, 0)

    async def test_explained_happy_path(self):
        provider = LabelledTestDoubleDreamProvider()
        with patch.dict(os.environ, self._configured(), clear=True):
            config = load_dream_provider_config()
            adapter = DreamModelAdapter(provider, config=config)
            result = await adapter.explain("我梦见自己死了", _retrieval_fixture())
        self.assertEqual(result["status"], "explained")
        self.assertFalse(result["ai_enabled"])
        self.assertFalse(result["personal_prediction"])
        self.assertEqual(len(result["claims"]), 1)
        self.assertEqual(
            result["claims"][0]["citations"][0]["evidence_id"], EVIDENCE_ID
        )
        self.assertEqual(provider.calls, 1)

    async def test_citation_rejected_unknown_evidence_id(self):
        reply = _valid_reply()
        reply["claims"][0]["evidence_ids"] = ["deadbeef" * 3]
        provider = LabelledTestDoubleDreamProvider(reply)
        with patch.dict(os.environ, self._configured(), clear=True):
            adapter = DreamModelAdapter(
                provider, config=load_dream_provider_config()
            )
            result = await adapter.explain("我梦见自己死了", _retrieval_fixture())
        self.assertEqual(result["status"], "citation_rejected")
        self.assertEqual(result["claims"], [])

    async def test_citation_rejected_quote_not_verbatim(self):
        reply = _valid_reply()
        reply["claims"][0]["quotes"] = [
            {"evidence_id": EVIDENCE_ID, "text": "见人死自死皆大吉大利"}
        ]
        provider = LabelledTestDoubleDreamProvider(reply)
        with patch.dict(os.environ, self._configured(), clear=True):
            adapter = DreamModelAdapter(
                provider, config=load_dream_provider_config()
            )
            result = await adapter.explain("我梦见自己死了", _retrieval_fixture())
        self.assertEqual(result["status"], "citation_rejected")
        self.assertEqual(result["claims"], [])

    async def test_citation_rejected_invented_title(self):
        reply = _valid_reply()
        reply["claims"][0]["text"] = "《不存在的古籍》载“见人死自死皆吉”。"
        provider = LabelledTestDoubleDreamProvider(reply)
        with patch.dict(os.environ, self._configured(), clear=True):
            adapter = DreamModelAdapter(
                provider, config=load_dream_provider_config()
            )
            result = await adapter.explain("我梦见自己死了", _retrieval_fixture())
        self.assertEqual(result["status"], "citation_rejected")
        self.assertEqual(result["claims"], [])

    async def test_diagnosis_rejected(self):
        for text in (
            "此梦显示你已被确诊抑郁症。",
            "此梦说明你怀孕了。",
        ):
            reply = _valid_reply()
            reply["claims"][0]["text"] = text
            provider = LabelledTestDoubleDreamProvider(reply)
            with patch.dict(os.environ, self._configured(), clear=True):
                adapter = DreamModelAdapter(
                    provider, config=load_dream_provider_config()
                )
                result = await adapter.explain(
                    "我梦见自己死了", _retrieval_fixture()
                )
            self.assertEqual(
                result["status"], "diagnosis_rejected", msg=text
            )
            self.assertEqual(result["claims"], [])

    async def test_prediction_rejected(self):
        for text in (
            "此梦预示你将会发财。",
            "你一定会升职。",
        ):
            reply = _valid_reply()
            reply["claims"][0]["text"] = text
            provider = LabelledTestDoubleDreamProvider(reply)
            with patch.dict(os.environ, self._configured(), clear=True):
                adapter = DreamModelAdapter(
                    provider, config=load_dream_provider_config()
                )
                result = await adapter.explain(
                    "我梦见自己死了", _retrieval_fixture()
                )
            self.assertEqual(
                result["status"], "prediction_rejected", msg=text
            )
            self.assertEqual(result["claims"], [])

    async def test_provider_failure_is_refusal(self):
        provider = LabelledTestDoubleDreamProvider(RuntimeError("boom"))
        with patch.dict(os.environ, self._configured(), clear=True):
            adapter = DreamModelAdapter(
                provider, config=load_dream_provider_config()
            )
            result = await adapter.explain("我梦见自己死了", _retrieval_fixture())
        self.assertEqual(result["status"], "provider_failed")
        self.assertEqual(result["claims"], [])

    async def test_provider_exception_text_never_leaks(self):
        # Simulated secrets only: the provider exception carries a fake
        # key and a full URL. Neither fragment may reach the returned
        # object, which must carry the fixed non-sensitive reason.
        for message in (
            "request failed: api_key=sk-test-9f8e7d6c5b4a",
            "request to https://provider.example.com/v1/chat"
            "?api_key=sk-test-9f8e7d6c5b4a failed",
        ):
            provider = LabelledTestDoubleDreamProvider(RuntimeError(message))
            with patch.dict(os.environ, self._configured(), clear=True):
                adapter = DreamModelAdapter(
                    provider, config=load_dream_provider_config()
                )
                result = await adapter.explain(
                    "我梦见自己死了", _retrieval_fixture()
                )
            self.assertEqual(result["status"], "provider_failed", msg=message)
            self.assertFalse(result["ai_enabled"])
            self.assertEqual(result["claims"], [])
            self.assertEqual(
                result["reason"], "model provider request failed"
            )
            blob = json.dumps(result, ensure_ascii=False)
            self.assertNotIn("sk-test-9f8e7d6c5b4a", blob)
            self.assertNotIn("provider.example.com", blob)
            self.assertEqual(provider.calls, 1)

    async def test_explain_refuses_when_key_leaks_into_context(self):
        # The simulated provider key is embedded in the retrieval payload,
        # so sanitize_context raises ModelClientError while the context is
        # built. The full explain() call must close into a safe refusal
        # with zero provider calls, not let the exception escape.
        retrieval = _retrieval_fixture()
        retrieval["evidence"][EVIDENCE_ID]["original_text"] = "test-key-123"
        provider = LabelledTestDoubleDreamProvider()
        with patch.dict(os.environ, self._configured(), clear=True):
            adapter = DreamModelAdapter(
                provider, config=load_dream_provider_config()
            )
            result = await adapter.explain("我梦见自己死了", retrieval)
        self.assertEqual(result["status"], "context_rejected")
        self.assertFalse(result["ai_enabled"])
        self.assertFalse(result["personal_prediction"])
        self.assertEqual(result["claims"], [])
        self.assertEqual(
            result["reason"], "the dream context could not be prepared safely"
        )
        self.assertEqual(provider.calls, 0)
        blob = json.dumps(result, ensure_ascii=False)
        self.assertNotIn("test-key-123", blob)

    async def test_malformed_reply_is_refusal(self):
        provider = LabelledTestDoubleDreamProvider({"nope": True})
        with patch.dict(os.environ, self._configured(), clear=True):
            adapter = DreamModelAdapter(
                provider, config=load_dream_provider_config()
            )
            result = await adapter.explain("我梦见自己死了", _retrieval_fixture())
        self.assertEqual(result["status"], "invalid_model_response")
        self.assertEqual(result["claims"], [])

    async def test_provider_timeout_is_refusal(self):
        class SlowTestDouble:
            async def explain(self, context):
                await asyncio.sleep(10)

        with patch.dict(os.environ, self._configured(), clear=True):
            adapter = DreamModelAdapter(
                SlowTestDouble(),
                config=load_dream_provider_config(),
                timeout=0.05,
            )
            result = await adapter.explain("我梦见自己死了", _retrieval_fixture())
        self.assertEqual(result["status"], "provider_timeout")
        self.assertEqual(result["claims"], [])

    async def test_invalid_inputs_raise(self):
        adapter = DreamModelAdapter(LabelledTestDoubleDreamProvider())
        with self.assertRaises(DreamAdapterError) as caught:
            await adapter.explain("", _retrieval_fixture())
        self.assertEqual(caught.exception.code, "invalid_input")
        with self.assertRaises(DreamAdapterError) as caught:
            await adapter.explain("我梦见自己死了", {"domain": "bazi"})
        self.assertEqual(caught.exception.code, "invalid_input")

    async def test_privacy_boundary_on_sent_context(self):
        provider = LabelledTestDoubleDreamProvider()
        with patch.dict(os.environ, self._configured(), clear=True):
            adapter = DreamModelAdapter(
                provider, config=load_dream_provider_config()
            )
            await adapter.explain(
                "我梦见自己死了，出生于1990-05-06T14:30:00+08:00",
                _retrieval_fixture(),
            )
        self.assertEqual(provider.calls, 1)
        sent = provider.contexts[0]
        blob = json.dumps(sent, ensure_ascii=False)
        self.assertNotIn("1990-05-06T14:30:00+08:00", blob)
        self.assertNotIn("test-key-123", blob)
        self.assertNotIn("api_key", [k.lower() for k in sent])
        self.assertEqual(len(sent["evidence"][EVIDENCE_ID]["original_text"]), 120)
        self.assertEqual(sent["domain"], "dream")
        self.assertEqual(sent["mode"], "research")


class ValidateReplyTests(unittest.TestCase):
    def test_validate_reply_accepts_valid_claims(self):
        context = build_dream_context("我梦见自己死了", _retrieval_fixture())
        claims = validate_dream_reply(_valid_reply(), context)
        self.assertEqual(len(claims), 1)
        self.assertEqual(claims[0]["citations"][0]["evidence_id"], EVIDENCE_ID)

    def test_validate_reply_rejects_domain_mismatch(self):
        reply = _valid_reply()
        reply["domain"] = "bazi"
        context = build_dream_context("我梦见自己死了", _retrieval_fixture())
        with self.assertRaises(DreamAdapterError) as caught:
            validate_dream_reply(reply, context)
        self.assertEqual(caught.exception.code, "invalid_model_response")


if __name__ == "__main__":
    unittest.main()
