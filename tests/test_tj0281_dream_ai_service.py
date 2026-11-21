"""TJ-028.1 sub-slice: dream AI business service acceptance.

The service layer (dream_ai_service.explain_dream) over the controlled
adapter, tested with an explicitly labelled local test double and
fixture retrievals in the real retrieve() shape. No real model is
called: every provider interaction in this file is the labelled test
double. Cases follow the task's twelve acceptance items: normal input,
missing fields, wrong JSON types, business-invalid content, forged
evidence ids, quote/source mismatch, insufficient evidence, timeout
and 429, non-JSON output, request isolation, frontend-facing error
shape (verdict + reason, no model text on refusal), and
ai_enabled=False with zero model calls when unconfigured.
"""
import asyncio
import copy
import json
import os
import unittest
from unittest.mock import patch

from tianji_kb.dream_ai_service import explain_dream
from tianji_kb.dream_model_adapter import DreamAdapterError
from tianji_kb.model_client import ModelClientError

EVIDENCE_ID = "a1b2c3d4e5f6a7b8c9d0e1f2"
SNAKE_EVIDENCE_ID = "b2c3d4e5f6a7b8c9d0e1f2a3"
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


def _snake_retrieval_fixture():
    """A second, distinct retrieval (snake scene) for isolation tests."""
    retrieval = _retrieval_fixture()
    candidate = {
        "term_id": "dream.term.snake",
        "symbol": "蛇",
        "scene": "蛇咬人",
        "source": "周公解梦",
        "locator": "卷一·蛇章",
        "original_text_short_quote": "蛇咬人主得大财",
        "interpretation": "蛇咬人主得大财",
        "interpretation_type": "traditional",
        "limitations": [],
        "confidence": "C",
        "cultural_context": "",
        "evidence_level": "C",
        "evidence_ids": [SNAKE_EVIDENCE_ID],
        "personal_prediction": False,
    }
    retrieval["matched_interpretations"] = [candidate]
    retrieval["interpretation_candidates"] = [candidate]
    retrieval["evidence"] = {
        SNAKE_EVIDENCE_ID: {
            "source_id": "dream.source.zhougong",
            "section_id": "dream.section.snake",
            "original_text": "蛇咬人主得大财",
            "classic_id": "dream.classic.zhougong",
            "classic_title": "周公解梦",
            "chapter_title": "蛇章",
            "locator": "卷一·蛇章",
            "source_url": "https://example.invalid/zhougong",
            "commit": "abc123",
            "sha256": "def456",
            "evidence_level": "C",
        }
    }
    return retrieval


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
    """Explicitly labelled local test double. NOT a real model."""

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


class ServiceTests(unittest.IsolatedAsyncioTestCase):
    def _configured(self):
        env = _clear_ai_env()
        env.update(_configured_env())
        return env

    async def _run(self, dream_text, retrieval, provider=None):
        provider = provider if provider is not None else LabelledTestDoubleDreamProvider()
        with patch.dict(os.environ, self._configured(), clear=True):
            from tianji_kb.dream_provider_config import load_dream_provider_config

            config = load_dream_provider_config()
            result = await explain_dream(
                dream_text, retrieval, provider=provider, config=config
            )
        return result, provider

    async def test_happy_path_explained(self):
        # Case 1: normal dream input + valid JSON.
        result, provider = await self._run("我梦见自己死了", _retrieval_fixture())
        self.assertEqual(result["verdict"], "explained")
        self.assertEqual(result["dream_text"], "我梦见自己死了")
        self.assertFalse(result["ai_enabled"])
        self.assertFalse(result["personal_prediction"])
        self.assertEqual(len(result["elements"]), 1)
        self.assertEqual(result["elements"][0]["term_id"], "dream.term.death")
        self.assertEqual(result["elements"][0]["symbol"], "死")
        self.assertEqual(result["elements"][0]["evidence_ids"], [EVIDENCE_ID])
        self.assertEqual(len(result["claims"]), 1)
        self.assertEqual(
            result["claims"][0]["citations"][0]["evidence_id"], EVIDENCE_ID
        )
        self.assertIn(EVIDENCE_ID, result["evidence"])
        self.assertIsNone(result["reason"])
        self.assertEqual(provider.calls, 1)

    async def test_evidence_covers_all_element_ids(self):
        # E0417 (TJ-028.3 gate): a matched scene's rule may resolve to
        # more than one reviewed source ref, while the model cites only
        # one of them. The result evidence must still carry every id
        # the elements cite, so the result is self-traceable.
        second_id = "c3d4e5f6a7b8c9d0e1f2a3b4"
        retrieval = _retrieval_fixture()
        retrieval["matched_interpretations"][0]["evidence_ids"] = [
            EVIDENCE_ID,
            second_id,
        ]
        retrieval["evidence"][second_id] = {
            **retrieval["evidence"][EVIDENCE_ID],
            "section_id": "dream.section.death-2",
            "original_text": "见人死自死皆吉，死人复活主有信",
        }
        result, _ = await self._run("我梦见自己死了", retrieval)
        self.assertEqual(result["verdict"], "explained")
        self.assertEqual(
            result["elements"][0]["evidence_ids"], [EVIDENCE_ID, second_id]
        )
        self.assertIn(EVIDENCE_ID, result["evidence"])
        self.assertIn(second_id, result["evidence"])

    async def test_element_id_without_retrieval_record_is_dropped(self):
        # E0417: an element id with no record in the retrieval evidence
        # is never presented untraceable.
        retrieval = _retrieval_fixture()
        retrieval["matched_interpretations"][0]["evidence_ids"] = [
            EVIDENCE_ID,
            "deadbeef" * 3,
        ]
        result, _ = await self._run("我梦见自己死了", retrieval)
        self.assertEqual(result["verdict"], "explained")
        self.assertEqual(result["elements"][0]["evidence_ids"], [EVIDENCE_ID])
        self.assertIn(EVIDENCE_ID, result["evidence"])
        self.assertNotIn("deadbeef" * 3, result["evidence"])

    async def test_missing_required_fields(self):
        # Case 2: the reply omits the required claims field.
        reply = {"domain": "dream", "variant": "traditional", "mode": "research"}
        result, _ = await self._run(
            "我梦见自己死了", _retrieval_fixture(),
            LabelledTestDoubleDreamProvider(reply),
        )
        self.assertEqual(result["verdict"], "invalid_model_response")
        self.assertEqual(result["claims"], [])
        self.assertEqual(result["evidence"], {})

    async def test_wrong_json_types(self):
        # Case 3: structurally present but wrongly typed fields.
        for reply in (
            {**_valid_reply(), "claims": {"text": "not an array"}},
            {**_valid_reply(), "claims": [
                {**_valid_reply()["claims"][0], "evidence_ids": EVIDENCE_ID}]},
            {**_valid_reply(), "claims": [
                {**_valid_reply()["claims"][0], "text": 42}]},
        ):
            result, _ = await self._run(
                "我梦见自己死了", _retrieval_fixture(),
                LabelledTestDoubleDreamProvider(reply),
            )
            self.assertEqual(
                result["verdict"], "invalid_model_response", msg=repr(reply)
            )
            self.assertEqual(result["claims"], [])

    async def test_structurally_valid_but_business_invalid(self):
        # Case 4: the reply passes the schema but breaks business rules.
        for text, verdict in (
            ("此梦显示你已被确诊抑郁症。", "diagnosis_rejected"),
            ("此梦预示你将会发财。", "prediction_rejected"),
        ):
            reply = _valid_reply()
            reply["claims"][0]["text"] = text
            result, _ = await self._run(
                "我梦见自己死了", _retrieval_fixture(),
                LabelledTestDoubleDreamProvider(reply),
            )
            self.assertEqual(result["verdict"], verdict, msg=text)
            self.assertEqual(result["claims"], [])
            self.assertEqual(result["evidence"], {})

    async def test_forged_evidence_id(self):
        # Case 5: the reply cites an evidence id that does not exist.
        reply = _valid_reply()
        reply["claims"][0]["evidence_ids"] = ["deadbeef" * 3]
        result, _ = await self._run(
            "我梦见自己死了", _retrieval_fixture(),
            LabelledTestDoubleDreamProvider(reply),
        )
        self.assertEqual(result["verdict"], "citation_rejected")
        self.assertEqual(result["claims"], [])

    async def test_quote_source_mismatch(self):
        # Case 6: the quote is not a verbatim substring of the source.
        reply = _valid_reply()
        reply["claims"][0]["quotes"] = [
            {"evidence_id": EVIDENCE_ID, "text": "见人死自死皆大吉大利"}
        ]
        result, _ = await self._run(
            "我梦见自己死了", _retrieval_fixture(),
            LabelledTestDoubleDreamProvider(reply),
        )
        self.assertEqual(result["verdict"], "citation_rejected")
        self.assertEqual(result["claims"], [])

    async def test_empty_quotes_refused(self):
        # Closeout (ChatGPT review of PR #588): a claim with no quote
        # must not pass. Every passing claim needs at least one real
        # verbatim quote (schema minItems: 1 on claims[].quotes); an
        # empty quotes array is an invalid model response and the
        # refusal carries no claims and no evidence.
        reply = _valid_reply()
        reply["claims"][0]["quotes"] = []
        provider = LabelledTestDoubleDreamProvider(reply)
        result, provider = await self._run(
            "我梦见自己死了", _retrieval_fixture(), provider
        )
        self.assertEqual(result["verdict"], "invalid_model_response")
        self.assertEqual(result["claims"], [])
        self.assertEqual(result["evidence"], {})
        self.assertEqual(provider.calls, 1)
        blob = json.dumps(result, ensure_ascii=False)
        self.assertNotIn("此条仅言梦中见人死自死的传统说法", blob)

    async def test_insufficient_evidence_abstains(self):
        # Case 7: no audited candidates -> abstain, zero model calls.
        retrieval = _retrieval_fixture()
        retrieval["status"] = "no_reviewed_interpretation"
        retrieval["matched_interpretations"] = []
        retrieval["interpretation_candidates"] = []
        result, provider = await self._run("我梦见考试", retrieval)
        self.assertEqual(
            result["verdict"], "abstained_no_reviewed_interpretation"
        )
        self.assertEqual(result["elements"], [])
        self.assertEqual(result["claims"], [])
        self.assertEqual(provider.calls, 0)

    async def test_provider_timeout(self):
        # Case 8a: a slow provider hits the adapter timeout.
        class SlowTestDouble:
            async def explain(self, context):
                await asyncio.sleep(10)

        with patch.dict(os.environ, self._configured(), clear=True):
            from tianji_kb.dream_provider_config import load_dream_provider_config

            result = await explain_dream(
                "我梦见自己死了", _retrieval_fixture(),
                provider=SlowTestDouble(),
                config=load_dream_provider_config(), timeout=0.05,
            )
        self.assertEqual(result["verdict"], "provider_timeout")
        self.assertEqual(result["claims"], [])

    async def test_provider_rate_limited(self):
        # Case 8b: a 429 from the transport is a distinct refusal.
        provider = LabelledTestDoubleDreamProvider(
            ModelClientError("rate_limit", "HTTP 429")
        )
        result, _ = await self._run(
            "我梦见自己死了", _retrieval_fixture(), provider
        )
        self.assertEqual(result["verdict"], "provider_rate_limited")
        self.assertEqual(result["claims"], [])

    async def test_non_json_output(self):
        # Case 9a: the provider answers with non-JSON content.
        provider = LabelledTestDoubleDreamProvider(
            json.JSONDecodeError("Expecting value", "this is not json", 0)
        )
        result, _ = await self._run(
            "我梦见自己死了", _retrieval_fixture(), provider
        )
        self.assertEqual(result["verdict"], "invalid_model_response")
        self.assertEqual(result["claims"], [])

    async def test_provider_returns_string_not_object(self):
        # Case 9b: the provider returns a JSON string, not an object.
        provider = LabelledTestDoubleDreamProvider("just a string")
        result, _ = await self._run(
            "我梦见自己死了", _retrieval_fixture(), provider
        )
        self.assertEqual(result["verdict"], "invalid_model_response")
        self.assertEqual(result["claims"], [])

    async def test_provider_failure_is_refusal(self):
        provider = LabelledTestDoubleDreamProvider(RuntimeError("boom"))
        result, _ = await self._run(
            "我梦见自己死了", _retrieval_fixture(), provider
        )
        self.assertEqual(result["verdict"], "provider_failed")
        self.assertEqual(result["claims"], [])

    async def test_requests_are_isolated(self):
        # Case 10: two sequential requests never share state.
        class RoutingTestDouble:
            """Returns the reply matching each call's own narrative."""

            def __init__(self):
                self.calls = 0
                self.contexts = []

            async def explain(self, context):
                self.calls += 1
                self.contexts.append(copy.deepcopy(context))
                if "蛇" in context["dream_narrative"]:
                    return {
                        "domain": "dream",
                        "variant": "traditional",
                        "mode": "research",
                        "claims": [
                            {
                                "text": "《周公解梦》载“蛇咬人主得大财”，此条仅言梦中蛇咬人的传统说法，不作个人运势判断。",
                                "evidence_ids": [SNAKE_EVIDENCE_ID],
                                "quotes": [
                                    {
                                        "evidence_id": SNAKE_EVIDENCE_ID,
                                        "text": "蛇咬人主得大财",
                                    }
                                ],
                            }
                        ],
                    }
                return copy.deepcopy(_valid_reply())

        provider = RoutingTestDouble()
        with patch.dict(os.environ, self._configured(), clear=True):
            from tianji_kb.dream_provider_config import load_dream_provider_config

            config = load_dream_provider_config()
            first = await explain_dream(
                "我梦见自己死了", _retrieval_fixture(),
                provider=provider, config=config,
            )
            second = await explain_dream(
                "我梦见被蛇咬了", _snake_retrieval_fixture(),
                provider=provider, config=config,
            )
        self.assertEqual(first["dream_text"], "我梦见自己死了")
        self.assertEqual(second["dream_text"], "我梦见被蛇咬了")
        self.assertEqual(first["elements"][0]["symbol"], "死")
        self.assertEqual(second["elements"][0]["symbol"], "蛇")
        self.assertEqual(first["verdict"], "explained")
        self.assertEqual(second["verdict"], "explained")
        self.assertEqual(provider.calls, 2)
        self.assertNotEqual(
            provider.contexts[0]["dream_narrative"],
            provider.contexts[1]["dream_narrative"],
        )
        self.assertEqual(
            second["claims"][0]["citations"][0]["evidence_id"],
            SNAKE_EVIDENCE_ID,
        )
        # Mutating the first result must not touch the second.
        first["elements"][0]["symbol"] = "MUTATED"
        first["claims"][0]["text"] = "MUTATED"
        self.assertEqual(second["elements"][0]["symbol"], "蛇")
        self.assertNotIn("MUTATED", second["claims"][0]["text"])

    async def test_invalid_inputs_raise(self):
        # Case 11 (input side): bad narratives and bad retrievals raise.
        provider = LabelledTestDoubleDreamProvider()
        with patch.dict(os.environ, self._configured(), clear=True):
            from tianji_kb.dream_provider_config import load_dream_provider_config

            config = load_dream_provider_config()
            for bad_text in ("", " ", "梦", "梦" * 501, 42, None):
                with self.assertRaises(DreamAdapterError) as caught:
                    await explain_dream(
                        bad_text, _retrieval_fixture(),
                        provider=provider, config=config,
                    )
                self.assertEqual(caught.exception.code, "invalid_input")
            with self.assertRaises(DreamAdapterError) as caught:
                await explain_dream(
                    "我梦见自己死了", {"domain": "bazi"},
                    provider=provider, config=config,
                )
            self.assertEqual(caught.exception.code, "invalid_input")
        self.assertEqual(provider.calls, 0)

    async def test_ai_enabled_false_and_no_call_when_unconfigured(self):
        # Case 12: no provider configured -> refusal, zero model calls.
        provider = LabelledTestDoubleDreamProvider()
        with patch.dict(os.environ, _clear_ai_env(), clear=True):
            result = await explain_dream(
                "我梦见自己死了", _retrieval_fixture(), provider=provider
            )
        self.assertEqual(result["verdict"], "not_configured")
        self.assertFalse(result["ai_enabled"])
        self.assertFalse(result["personal_prediction"])
        self.assertEqual(result["claims"], [])
        self.assertEqual(provider.calls, 0)

    async def test_elements_drop_candidates_without_evidence(self):
        retrieval = _retrieval_fixture()
        retrieval["matched_interpretations"][0]["evidence_ids"] = []
        result, _ = await self._run("我梦见自己死了", retrieval)
        self.assertEqual(result["elements"], [])
        self.assertEqual(result["verdict"], "explained")

    async def test_refusal_carries_no_affirmative_conclusion(self):
        reply = _valid_reply()
        reply["claims"][0]["evidence_ids"] = ["deadbeef" * 3]
        result, _ = await self._run(
            "我梦见自己死了", _retrieval_fixture(),
            LabelledTestDoubleDreamProvider(reply),
        )
        self.assertNotEqual(result["verdict"], "explained")
        self.assertEqual(result["claims"], [])
        self.assertEqual(result["evidence"], {})
        # The refused model text never appears; the audited elements
        # (retrieval data, not model text) are still shown.
        blob = json.dumps(result, ensure_ascii=False)
        self.assertNotIn("此条仅言梦中见人死自死的传统说法", blob)
        self.assertIn("见人死自死皆吉", blob)


if __name__ == "__main__":
    unittest.main()
