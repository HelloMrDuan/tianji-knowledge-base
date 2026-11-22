"""TJ-028.1 user slice: public dream-interpret endpoint for the new user page.

POST /api/v1/dream/interpret reuses the reviewed retrieval behind the
public cultural lookup and projects it for the user page: typed symbols,
deterministic same-source relations, explicit boundaries, and a typed
AI-interpretation slot that stays not_enabled while ai_enabled is False.

Two classes, following the repo's partition rule:

* ``PatchedInterpretTests`` patches ``tianji_kb.api.retrieve_dream_culture``
  with a fixture in the real retrieve() shape, so it runs anywhere
  (public CI included). The endpoint code under test is real: input
  validation, retrieval contract checks, the projection, the AI gate
  and the admin auth gate all run.
* ``RealInterpretTests`` uses the real app and the real retrieve() with
  no patching, so it runs in the sealed offline acceptance only (the
  reviewed Canonical data is absent from the public checkout).
"""
import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

from tianji_kb.api import create_app
from tianji_kb.rag_context import RetrievalUnavailable

ENDPOINT = "/api/v1/dream/interpret"
ADMIN_RESEARCH = "/api/v1/admin/research/dream"
ADMIN_AI_EXPLAIN = "/api/v1/admin/research/dream/ai-explain"
ADMIN_REVIEW_DRAFTS = "/api/v1/admin/research/dream/review-drafts"

EVIDENCE_SNAKE = "a1b2c3d4e5f6a7b8c9d0e1f2"
EVIDENCE_MONEY = "b2c3d4e5f6a7b8c9d0e1f2a3"


def _span(dream_text, quote):
    start = dream_text.index(quote)
    return {"start": start, "end": start + len(quote), "text": quote}


def _candidate(*, symbol, scene, quote, span_text, interpretation,
               evidence_id, classic_title):
    return {
        "term_id": "dream.term.fixture",
        "symbol": symbol,
        "scene": scene,
        "source": "周公解梦",
        "locator": "卷一",
        "original_text_short_quote": quote,
        "interpretation": interpretation,
        "interpretation_type": "traditional",
        "limitations": [],
        "confidence": "C",
        "cultural_context": "",
        "evidence_level": "C",
        "evidence_ids": [evidence_id],
        "personal_prediction": False,
        "match_kind": "reviewed_cultural_scene_retrieval",
        "input_matches": [{"input_spans": []}],
        "_span_text": span_text,
    }


def _retrieval_fixture(dream_text, candidates, unreviewed_topics=None):
    evidence = {}
    matched = []
    for candidate in candidates:
        span_text = candidate.pop("_span_text")
        candidate["input_matches"] = [
            {"input_spans": [_span(dream_text, span_text)]}
        ]
        evidence[candidate["evidence_ids"][0]] = {
            "classic_title": candidate["_classic_title"],
            "evidence_level": "C",
        }
        matched.append(candidate)
    return {
        "domain": "dream",
        "variant": "traditional",
        "mode": "research",
        "status": "reviewed_interpretation_candidates" if matched else "no_reviewed_interpretation",
        "entities": [],
        "matched_interpretations": matched,
        "interpretation_candidates": matched,
        "narrative_observations": [],
        "unreviewed_input_topics": unreviewed_topics or [],
        "evidence": evidence,
        "retrieval": [],
        "retrieval_method": "bounded_scene_match_and_reviewed_rag",
        "chart_generated": False,
        "public_enabled": False,
        "ai_enabled": False,
        "limitations": ["仅审核 12 个具体传统梦场景；有限句式识别不是完整自然语言理解。"],
    }


def _two_scene_fixture(dream_text):
    snake = _candidate(
        symbol="蛇", scene="蛇咬人", quote="蛇咬人主得大财",
        span_text="被蛇咬", interpretation="蛇咬人主得大财",
        evidence_id=EVIDENCE_SNAKE, classic_title="周公解梦")
    snake["_classic_title"] = "周公解梦"
    money = _candidate(
        symbol="钱财", scene="拾得钱物", quote="拾得钱物皆大吉",
        span_text="捡到了钱", interpretation="拾得钱物皆大吉",
        evidence_id=EVIDENCE_MONEY, classic_title="周公解梦")
    money["_classic_title"] = "周公解梦"
    return _retrieval_fixture(dream_text, [snake, money])


class PatchedInterpretTests(unittest.TestCase):
    def setUp(self):
        # Role tokens configured so the role-gated review-drafts
        # endpoint answers 401 (not 503 not-configured) to a caller
        # without credentials, like the read-token endpoints.
        self.client = TestClient(create_app(
            admin_read_token="t", admin_role_tokens={"t": "editor"}))

    def _post(self, dream_text):
        return self.client.post(ENDPOINT, json={"dream_text": dream_text})

    def test_two_symbols_shape_relations_and_ai_not_enabled(self):
        dream = "我梦见被蛇咬了，我梦见我捡到了钱"
        with patch("tianji_kb.api.retrieve_dream_culture",
                   return_value=_two_scene_fixture(dream)):
            response = self._post(dream)
        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(response.headers["cache-control"], "no-store")
        data = response.json()
        self.assertEqual(data["status"], "reviewed_cultural_matches")
        self.assertTrue(data["public_release"])
        self.assertTrue(data["cultural_reference_only"])
        self.assertFalse(data["ai_enabled"])
        self.assertFalse(data["personal_prediction"])
        self.assertEqual(
            set(data),
            {"api_version", "status", "public_release",
             "cultural_reference_only", "ai_enabled", "personal_prediction",
             "symbols", "relations", "unreviewed_topics", "boundaries",
             "notice", "ai_interpretation"})
        self.assertEqual([s["symbol"] for s in data["symbols"]], ["蛇", "钱财"])
        self.assertEqual([s["scene"] for s in data["symbols"]], ["蛇咬人", "拾得钱物"])
        self.assertEqual(data["symbols"][0]["matched_texts"], ["被蛇咬"])
        self.assertEqual(data["symbols"][1]["matched_texts"], ["捡到了钱"])
        self.assertEqual(data["symbols"][0]["short_quote"], "蛇咬人主得大财")
        self.assertEqual(data["symbols"][0]["source_title"], "周公解梦")
        self.assertEqual(data["symbols"][0]["evidence_level"], "C")
        self.assertEqual(len(data["relations"]), 1)
        relation = data["relations"][0]
        self.assertEqual(relation["kind"], "same_source")
        self.assertEqual(relation["source_title"], "周公解梦")
        self.assertEqual(relation["scenes"], ["蛇咬人", "拾得钱物"])
        self.assertIn("出处相同，含义各自独立", relation["note"])
        self.assertEqual(data["unreviewed_topics"], [])
        self.assertTrue(data["boundaries"])
        self.assertIn("仅审核 12 个具体传统梦场景", data["boundaries"][0])
        self.assertEqual(data["ai_interpretation"]["status"], "not_enabled")
        self.assertFalse(data["ai_interpretation"]["enabled"])
        self.assertIn("AI 解读尚未启用", data["ai_interpretation"]["message"])
        # The caller's narrative is never echoed back and never stored.
        self.assertNotIn("dream_text", data)
        # Never leak internal RAG traces, repository paths or privileged
        # metadata. "evidence" is checked as a key (not a substring:
        # the public "evidence_level" field legitimately contains it).
        self.assertNotIn("evidence", data)
        for symbol in data["symbols"]:
            self.assertNotIn("evidence", symbol)
        for forbidden in ("rule_id", "term_id", "canonical_path", "input_spans",
                          "retrieval", "trace", "token"):
            self.assertNotIn(forbidden, response.text)
        self.assertNotIn("data/canonical/", response.text)

    def test_relations_empty_for_distinct_sources(self):
        dream = "我梦见被蛇咬了，我梦见我捡到了钱"
        fixture = _two_scene_fixture(dream)
        fixture["evidence"][EVIDENCE_MONEY]["classic_title"] = "另一典籍"
        with patch("tianji_kb.api.retrieve_dream_culture", return_value=fixture):
            response = self._post(dream)
        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(response.json()["relations"], [])

    def test_no_match_returns_no_interpretation_with_ai_not_enabled(self):
        dream = "梦见考试"
        topic = {"label": "考试", "status": "input_observation_only",
                 "reviewed_interpretation_available": False, "evidence_ids": [],
                 "input_spans": [_span(dream, "梦见考试")]}
        fixture = _retrieval_fixture(dream, [], unreviewed_topics=[topic])
        with patch("tianji_kb.api.retrieve_dream_culture", return_value=fixture):
            response = self._post(dream)
        self.assertEqual(response.status_code, 200, response.text)
        data = response.json()
        self.assertEqual(data["status"], "no_reviewed_interpretation")
        self.assertEqual(data["symbols"], [])
        self.assertEqual(data["relations"], [])
        self.assertEqual(data["unreviewed_topics"],
                         [{"label": "考试", "matched_texts": ["梦见考试"]}])
        self.assertEqual(data["ai_interpretation"]["status"], "not_enabled")
        self.assertFalse(data["ai_interpretation"]["enabled"])

    def test_invalid_and_overlong_inputs_are_rejected(self):
        for bad in ("", "梦", "   ", "梦" * 501, 123, None):
            with self.subTest(bad=bad):
                response = self.client.post(ENDPOINT, json={"dream_text": bad})
                self.assertEqual(response.status_code, 422, response.text)
        response = self.client.post(ENDPOINT, json={})
        self.assertEqual(response.status_code, 422)

    def test_retrieval_unavailable_fails_closed(self):
        with patch("tianji_kb.api.retrieve_dream_culture",
                   side_effect=RetrievalUnavailable("index unavailable")):
            response = self._post("我梦见被蛇咬了")
        self.assertEqual(response.status_code, 503, response.text)
        self.assertEqual(response.json()["detail"]["code"],
                         "reviewed_retrieval_unavailable")

    def test_admin_endpoints_unreachable_without_token(self):
        for path, payload in (
                (ADMIN_RESEARCH, {"dream_text": "我梦见被蛇咬了"}),
                (ADMIN_AI_EXPLAIN, {"dream_text": "我梦见被蛇咬了"}),
                (ADMIN_REVIEW_DRAFTS, {})):
            with self.subTest(path=path):
                response = self.client.post(path, json=payload)
                self.assertEqual(response.status_code, 401, response.text)
                self.assertEqual(response.json()["detail"]["code"],
                                 "admin_unauthorized")


class RealInterpretTests(unittest.TestCase):
    """Real retrieval, sealed offline acceptance only (no sealed data in
    the public checkout). Mirrors test_public_dream_culture_api.py."""

    def setUp(self):
        self.client = TestClient(create_app(admin_read_token="t"))

    def test_real_single_scene_symbol_and_source(self):
        response = self.client.post(ENDPOINT, json={"dream_text": "我梦见被蛇咬了"})
        self.assertEqual(response.status_code, 200, response.text)
        data = response.json()
        self.assertEqual(data["status"], "reviewed_cultural_matches")
        self.assertEqual(len(data["symbols"]), 1)
        symbol = data["symbols"][0]
        self.assertEqual(symbol["symbol"], "蛇")
        self.assertEqual(symbol["scene"], "蛇咬人")
        self.assertIn("蛇咬人主得大财", symbol["short_quote"])
        self.assertEqual(symbol["evidence_level"], "C")
        self.assertEqual(data["relations"], [])
        self.assertEqual(data["ai_interpretation"]["status"], "not_enabled")
        self.assertFalse(data["ai_enabled"])

    def test_real_two_symbols_share_one_source_relation(self):
        dream = "我梦见被蛇咬了，我梦见我捡到了钱"
        response = self.client.post(ENDPOINT, json={"dream_text": dream})
        self.assertEqual(response.status_code, 200, response.text)
        data = response.json()
        self.assertEqual(data["status"], "reviewed_cultural_matches")
        self.assertEqual([s["scene"] for s in data["symbols"]],
                         ["蛇咬人", "拾得钱物"])
        self.assertEqual(len(data["relations"]), 1)
        relation = data["relations"][0]
        self.assertEqual(relation["kind"], "same_source")
        self.assertEqual(relation["scenes"], ["蛇咬人", "拾得钱物"])
        self.assertIn("出处相同，含义各自独立", relation["note"])

    def test_real_no_interpretation_and_unreviewed_topic(self):
        for dream, expected_topics in (
                ("梦见考试", ["考试"]),
                ("我梦见自己怀孕", ["怀孕"])):
            with self.subTest(dream=dream):
                response = self.client.post(ENDPOINT, json={"dream_text": dream})
                self.assertEqual(response.status_code, 200, response.text)
                data = response.json()
                self.assertEqual(data["status"], "no_reviewed_interpretation")
                self.assertEqual(data["symbols"], [])
                self.assertEqual([t["label"] for t in data["unreviewed_topics"]],
                                 expected_topics)
                self.assertEqual(data["ai_interpretation"]["status"], "not_enabled")
