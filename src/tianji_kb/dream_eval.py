"""Fixed-suite offline evaluation for the dream AI adapter (TJ-028.2).

The suite ``evals/dream/cases-v1.json`` pins 12 real audited dream
scenes (term ids, symbols, scenes, verbatim short quotes, locators —
taken from the reviewed canonical dream index) plus fixed forgery,
refusal-content, input-control, transport-fault and isolation cases.

Rules inherited from the Phase 4 explanation standard
(``docs/phase4/EVALUATION.md``), unchanged:

- A positive case passes only when the verdict is ``explained`` and
  every deterministic check holds (contract shape, evidence ids
  exist, quotes verbatim, quotes non-empty, no diagnosis, no
  personal prediction, result evidence matches the cited ids).
- Refusal, input-control and transport cases are controls: they are
  reported separately (``control_pass_rate``) and can never inflate
  the positive pass rate.
- The provider here is always the labelled scripted test double
  (``ScriptedDreamProvider``). ``run_kind`` is ``test_provider`` and
  ``real_model_evaluation`` is always False: a mock run never
  qualifies real-model quality, and ``online_ready`` stays False.
  A real-model run needs separate authorization and a different
  runner; this module never reads ``TIANJI_AI_*`` credentials and
  never contacts a network.
- ``--dry-run`` (``validate_suite``) builds every fixture and runs
  the pure reply validator against the positive fixtures: it proves
  the suite is self-consistent without any provider call.
"""

import asyncio
import copy
import hashlib
import json
from pathlib import Path

from .dream_ai_service import explain_dream
from .dream_model_adapter import (
    DreamAdapterError,
    build_dream_context,
    validate_dream_reply,
)
from .model_client import ModelClientError
from .resolver import ROOT
from .runtime_catalog import digest

SUITE_PATH = ROOT / "evals" / "dream" / "cases-v1.json"
MOCK_MODEL = "mock-dream-eval-v1"

# The mock run uses a synthetic configured config because the provider
# is the scripted test double, injected directly: no real credentials
# are involved and no environment variable is read.
MOCK_CONFIG = {
    "configured": True,
    "driver": "mock",
    "endpoint": "mock://dream-eval",
    "model": MOCK_MODEL,
    "timeout": 20,
    "max_tokens": None,
    "reason": None,
    "settings": {},
}
NOT_CONFIGURED_CONFIG = {
    "configured": False,
    "driver": None,
    "endpoint": None,
    "model": None,
    "timeout": None,
    "max_tokens": None,
    "reason": "no model provider is configured",
    "settings": None,
}

# Model-invented strings that must never appear in a refusal reason.
LEAK_PROBES = ("焦虑症", "你怀孕", "你将会发财", "皆大吉大利", "伪造古籍")

EXPECTED_VERDICTS = frozenset(
    {
        "explained",
        "abstained_no_reviewed_interpretation",
        "not_configured",
        "provider_timeout",
        "provider_rate_limited",
        "provider_failed",
        "invalid_model_response",
        "citation_rejected",
        "diagnosis_rejected",
        "prediction_rejected",
        "context_rejected",
        "input_rejected",
    }
)


def load_suite(path=SUITE_PATH):
    """Load and validate the fixed suite (duplicate ids and bad verdicts fail)."""
    suite = json.loads(Path(path).read_text())
    if suite.get("suite_id") != "dream-eval-v1":
        raise ValueError("dream eval suite id mismatch")
    scene_ids = set()
    for scene in suite["scenes"]:
        if scene["term_id"] in scene_ids:
            raise ValueError("Duplicate dream eval scene")
        scene_ids.add(scene["term_id"])
    if len(suite["scenes"]) != 12:
        raise ValueError("dream eval suite must pin exactly 12 audited scenes")
    ids = set()
    for case in suite["cases"]:
        if case["id"] in ids:
            raise ValueError("Duplicate dream eval case ID")
        ids.add(case["id"])
        if case["expected_verdict"] not in EXPECTED_VERDICTS:
            raise ValueError(f"unknown expected verdict: {case['expected_verdict']}")
        if case["kind"] not in (
            "explanation",
            "refusal",
            "input_control",
            "transport_fault",
            "isolation",
        ):
            raise ValueError(f"unknown case kind: {case['kind']}")
        if case.get("scene") is not None and case["scene"] not in scene_ids:
            raise ValueError(f"case {case['id']} references an unknown scene")
    return suite


def evidence_id_for(term_id):
    """Deterministic fixture evidence id for one audited scene."""
    return hashlib.sha256(f"dream-eval-evidence:{term_id}".encode()).hexdigest()[:24]


def scene_by_id(suite, term_id):
    return next(s for s in suite["scenes"] if s["term_id"] == term_id)


def build_fixture_retrieval(suite, scene_id, extra_scene_ids=()):
    """A retrieval in the real retrieve() shape for one audited scene.

    Evidence ids are deterministic fixture ids; the scene metadata
    (term id, symbol, scene, verbatim short quote, locator, audited
    classic title) is the real reviewed registry from the suite.
    ``original_text`` holds only the short verbatim quote: the full
    audited text stays sealed and is never needed to exercise the
    adapter's verbatim check.
    """
    term_ids = ([scene_id] if scene_id else []) + list(extra_scene_ids)
    candidates = []
    evidence = {}
    for term_id in term_ids:
        scene = scene_by_id(suite, term_id)
        eid = evidence_id_for(term_id)
        candidates.append(
            {
                "term_id": term_id,
                "symbol": scene["symbol"],
                "scene": scene["scene"],
                "source": scene["source"],
                "locator": scene["locator"],
                "original_text_short_quote": scene["quote"],
                "interpretation": scene["quote"],
                "interpretation_type": "traditional",
                "limitations": [],
                "confidence": "C",
                "cultural_context": "",
                "evidence_level": "C",
                "evidence_ids": [eid],
                "personal_prediction": False,
            }
        )
        evidence[eid] = {
            "source_id": "dream.source.zhougong-scenes",
            "section_id": f"dream.section.{term_id.split('.')[-1]}",
            "original_text": scene["quote"],
            "classic_id": "dream.classic.zhougong",
            "classic_title": scene["classic_title"],
            "chapter_title": scene["locator"].split("；")[0],
            "locator": scene["locator"],
            "source_url": "https://example.invalid/zhougong",
            "commit": "eval-fixture",
            "sha256": "eval-fixture",
            "evidence_level": "C",
        }
    matched = candidates[:1] if scene_id else []
    return {
        "domain": "dream",
        "variant": "traditional",
        "mode": "research",
        "status": "reviewed_interpretation_candidates"
        if matched
        else "no_reviewed_interpretation",
        "entities": [],
        "matched_interpretations": matched,
        "interpretation_candidates": candidates,
        "narrative_observations": [],
        "unreviewed_input_topics": [],
        "evidence": evidence,
        "retrieval": [],
        "retrieval_method": "bounded_scene_match_and_reviewed_rag",
        "chart_generated": False,
        "public_enabled": False,
        "ai_enabled": False,
        "limitations": ["仅审核 12 个具体传统梦场景；有限句式识别不是完整自然语言理解。"],
    }


def valid_reply_for(suite, scene_id):
    """The valid model reply for one audited scene."""
    scene = scene_by_id(suite, scene_id)
    eid = evidence_id_for(scene_id)
    return {
        "domain": "dream",
        "variant": "traditional",
        "mode": "research",
        "claims": [
            {
                "text": f"《周公解梦》载“{scene['quote']}”，此条仅言梦中{scene['scene']}的传统说法，不作个人运势判断。",
                "evidence_ids": [eid],
                "quotes": [{"evidence_id": eid, "text": scene["quote"]}],
            }
        ],
    }


class ScriptedDreamProvider:
    """Explicitly labelled local test double. NOT a real model."""

    def __init__(self, reply=None, error=None):
        self.reply = reply
        self.error = error
        self.calls = 0
        self.contexts = []

    async def explain(self, context):
        self.calls += 1
        self.contexts.append(copy.deepcopy(context))
        if self.error is not None:
            raise self.error
        return copy.deepcopy(self.reply)


def _resolve_sentinels(value, suite):
    """Replace EVIDENCE_OF_<slug> sentinels with deterministic fixture ids."""
    if isinstance(value, str) and value.startswith("EVIDENCE_OF_"):
        return evidence_id_for("dream.term." + value[len("EVIDENCE_OF_"):].lower())
    if isinstance(value, dict):
        return {k: _resolve_sentinels(v, suite) for k, v in value.items()}
    if isinstance(value, list):
        return [_resolve_sentinels(v, suite) for v in value]
    return value


def _apply_mutation(reply, mutate, suite):
    """Apply one path mutation (``claims[0].evidence_ids``) to a reply."""
    import re

    reply = copy.deepcopy(reply)
    for path, value in (mutate or {}).items():
        value = _resolve_sentinels(value, suite)
        parts = re.findall(r"([A-Za-z_]+)|\[(\d+)\]", path)
        target = reply
        for name, index in parts[:-1]:
            target = target[name] if name else target[int(index)]
        name, index = parts[-1]
        if name:
            target[name] = value
        else:
            target[int(index)] = value
    return reply


def _error_for(name):
    if name == "timeout":
        return ModelClientError("timeout", "mock timeout")
    if name == "rate_limit":
        return ModelClientError("rate_limit", "mock HTTP 429")
    if name == "connection_failed":
        return ModelClientError("network", "mock connection failure")
    if name == "non_json":
        return json.JSONDecodeError("mock non-JSON reply", "", 0)
    raise ValueError(f"unknown mock error: {name}")


def _reply_for_case(suite, case):
    """Build the scripted reply (or raise for transport faults)."""
    mock = case.get("mock") or {}
    if "error" in mock:
        if mock["error"] == "not_configured":
            # The adapter refuses before any provider call; no reply
            # and no error object are needed.
            return None, None
        return None, _error_for(mock["error"])
    kind = mock.get("reply") or "valid"
    if case.get("scene") is None:
        # No audited scene: the adapter abstains before any provider
        # call, so this reply is never used. Keep it fail-closed
        # (empty claims) in case the abstention path ever changes.
        return {"domain": "dream", "variant": "traditional",
                "mode": "research", "claims": []}, None
    if kind == "valid":
        reply = valid_reply_for(suite, case["scene"])
    elif kind == "no-claims":
        reply = {"domain": "dream", "variant": "traditional", "mode": "research"}
    elif kind == "claims-string":
        reply = {
            "domain": "dream",
            "variant": "traditional",
            "mode": "research",
            "claims": "not a list",
        }
    else:
        raise ValueError(f"unknown mock reply kind: {kind}")
    return _apply_mutation(reply, mock.get("mutate"), suite), None


def _check_explained(result, case, suite, fixture):
    """Deterministic checks for a positive case; returns {name: bool}."""
    eid = evidence_id_for(case["scene"])
    claims = result.get("claims") or []
    evidence = result.get("evidence") or {}
    checks = {
        "verdict_explained": result.get("verdict") == "explained",
        "ai_stays_off": result.get("ai_enabled") is False,
        "no_personal_prediction": result.get("personal_prediction") is False,
        "dream_text_echoed": result.get("dream_text") == case["dream_text"].strip(),
        "element_matches_scene": bool(result.get("elements"))
        and result["elements"][0].get("term_id") == case["scene"],
        "claims_present": bool(claims),
        "every_claim_has_quote": bool(claims)
        and all(isinstance(c, dict) and c.get("quotes") for c in claims),
        "evidence_ids_exist": all(
            isinstance(e, str) and e in fixture["evidence"]
            for c in claims
            for e in (c.get("evidence_ids") or [])
        ),
        "quotes_verbatim": all(
            isinstance(q, dict)
            and q.get("text") in fixture["evidence"].get(q.get("evidence_id"), {}).get("original_text", "")
            for c in claims
            for q in (c.get("quotes") or [])
        ),
        "result_evidence_matches_claims": set(evidence)
        == {e for c in claims for e in (c.get("evidence_ids") or [])}
        and set(evidence) == {eid},
        "reason_is_none": result.get("reason") is None,
    }
    return checks


def _check_refusal(result, case):
    """A refusal must carry no claims, no evidence, and no model text."""
    reason = result.get("reason") or ""
    return {
        "verdict_matches": result.get("verdict") == case["expected_verdict"],
        "claims_empty": result.get("claims") == [],
        "evidence_empty": result.get("evidence") == {},
        "ai_stays_off": result.get("ai_enabled") is False,
        "no_personal_prediction": result.get("personal_prediction") is False,
        "reason_present": bool(reason.strip()),
        "no_model_text_leak": not any(p in reason for p in LEAK_PROBES),
    }


async def _run_single(suite, case):
    """Run one case through explain_dream with the scripted provider."""
    row = {"id": case["id"], "kind": case["kind"], "expected": case["expected"],
           "tags": case.get("tags", [])}
    fixture = build_fixture_retrieval(
        suite, case.get("scene"), case.get("extra_evidence") or ()
    )
    if case["kind"] == "isolation":
        async def _one(text, scene):
            fixture = build_fixture_retrieval(suite, scene)
            provider = ScriptedDreamProvider(reply=valid_reply_for(suite, scene))
            result = await explain_dream(text, fixture, provider=provider, config=MOCK_CONFIG)
            return result, provider

        first, provider1 = await _one(case["dream_text"], case["scene"])
        second, provider2 = await _one(case["second_dream_text"], case["second_scene"])
        eid1 = evidence_id_for(case["scene"])
        eid2 = evidence_id_for(case["second_scene"])
        checks = {
            "first_explained": first.get("verdict") == "explained",
            "second_explained": second.get("verdict") == "explained",
            "first_evidence_only_first": set(first.get("evidence") or {}) == {eid1},
            "second_evidence_only_second": set(second.get("evidence") or {}) == {eid2},
            "dream_texts_distinct": first.get("dream_text") == case["dream_text"]
            and second.get("dream_text") == case["second_dream_text"],
            "one_call_each": provider1.calls == 1 and provider2.calls == 1,
        }
        row["checks"] = checks
        row["status"] = "passed" if all(checks.values()) else "failed"
        row["error"] = None if row["status"] == "passed" else "isolation_leak"
        return row, None
    reply, error = _reply_for_case(suite, case)
    provider = ScriptedDreamProvider(reply=reply, error=error)
    config = NOT_CONFIGURED_CONFIG if (case.get("mock") or {}).get("error") == "not_configured" else MOCK_CONFIG
    if config is NOT_CONFIGURED_CONFIG:
        provider = None
    try:
        result = await explain_dream(
            case["dream_text"], fixture, provider=provider, config=config
        )
    except DreamAdapterError as exc:
        if case["expected"] == "input_rejected" and exc.code == "invalid_input":
            row["status"] = "passed"
            row["error"] = "input_rejected"
            row["checks"] = {"input_rejected": True}
            return row, provider
        row["status"] = "failed"
        row["error"] = f"unexpected_input_error:{exc.code}"
        row["checks"] = {"input_rejected": False}
        return row, provider
    if case["expected"] == "input_rejected":
        row["status"] = "failed"
        row["error"] = "unexpected_input_acceptance"
        row["checks"] = {"input_rejected": False}
        return row, provider
    if case["expected"] == "explanation":
        checks = _check_explained(result, case, suite, fixture)
    else:
        checks = _check_refusal(result, case)
    calls = provider.calls if provider is not None else 0
    # No provider call happens when the adapter abstains before the
    # model (no audited scene) or when nothing is configured.
    if config is NOT_CONFIGURED_CONFIG or not fixture.get("matched_interpretations"):
        expected_calls = 0
    else:
        expected_calls = 1
    checks["provider_calls_match"] = calls == expected_calls
    row["verdict"] = result.get("verdict")
    row["checks"] = checks
    row["status"] = "passed" if all(checks.values()) else "failed"
    row["error"] = None if row["status"] == "passed" else "eval_gate_failed"
    return row, provider


async def evaluate_dream_suite(suite=None, *, run_kind="test_provider",
                               model=MOCK_MODEL):
    """Run the whole fixed suite with the scripted provider (mock only)."""
    suite = suite or load_suite()
    results = []
    for case in suite["cases"]:
        row, _ = await _run_single(suite, case)
        results.append(row)
    positive = [r for r in results if r["kind"] in ("explanation", "isolation")]
    controls = [r for r in results if r["kind"] not in ("explanation", "isolation")]
    reports = {
        "dream": {
            "case_count": len(results),
            "positive_cases": len(positive),
            "completed_model_responses": sum(
                1 for r in positive if r["status"] in ("passed", "failed")
            ),
            "pass_rate": (sum(r["status"] == "passed" for r in positive) / len(positive)
                          if positive else None),
            "control_pass_rate": (sum(r["status"] == "passed" for r in controls) / len(controls)
                                  if controls else None),
            "not_run": [r["id"] for r in results if r["status"] == "not_run"],
            "failures": [
                {"id": r["id"], "error": r.get("error") or "eval_gate_failed"}
                for r in results if r["status"] == "failed"
            ],
            "online_ready": False,
            "semantic_review": "required; automatic bindings do not certify free prose",
            "semantic_metrics": None,
            "semantic_hallucination_count": None,
            "semantic_unsupported_claims": None,
            "semantic_contradiction_count": None,
        }
    }
    return {
        "schema_version": "1.0",
        "suite_id": suite["suite_id"],
        "suite_sha256": digest(suite),
        "run_kind": run_kind,
        "model": model,
        "real_model_evaluation": False,
        "reports": reports,
        "cases": results,
        "online_ready": False,
    }


def validate_suite(suite=None):
    """Dry run: prove the suite is self-consistent with no provider call.

    Builds every fixture and runs the pure reply validator over the
    positive fixtures; refusal fixtures must fail validation with the
    expected adapter code. No provider object is created.
    """
    suite = suite or load_suite()
    checked = 0
    for case in suite["cases"]:
        if case["kind"] == "isolation":
            for text, scene in (
                (case["dream_text"], case["scene"]),
                (case["second_dream_text"], case["second_scene"]),
            ):
                fixture = build_fixture_retrieval(suite, scene)
                context = build_dream_context(text, fixture)
                validate_dream_reply(valid_reply_for(suite, scene), context)
                checked += 1
            continue
        fixture = build_fixture_retrieval(
            suite, case.get("scene"), case.get("extra_evidence") or ()
        )
        if case["kind"] in ("explanation",):
            context = build_dream_context(case["dream_text"], fixture)
            validate_dream_reply(valid_reply_for(suite, case["scene"]), context)
            checked += 1
        elif case["kind"] == "refusal":
            mock = case.get("mock") or {}
            if mock.get("reply") in ("valid",):
                reply, _ = _reply_for_case(suite, case)
                context = build_dream_context(case["dream_text"], fixture)
                try:
                    validate_dream_reply(reply, context)
                except DreamAdapterError as error:
                    if error.code != case["expected_verdict"]:
                        raise ValueError(
                            f"{case['id']}: dry-run refusal code {error.code} "
                            f"!= expected {case['expected_verdict']}"
                        ) from error
                    checked += 1
                else:
                    raise ValueError(f"{case['id']}: dry-run refusal did not fail")
    return {"suite_id": suite["suite_id"], "suite_sha256": digest(suite),
            "cases_checked": checked, "provider_calls": 0}


def markdown_report(report):
    """Render the report as Markdown (Phase 4 report shape)."""
    row = report["reports"]["dream"]
    lines = [
        "# Dream evaluation report",
        "",
        f"Suite `{report['suite_id']}` / `{report['suite_sha256']}`",
        "",
        f"Model `{report['model']}`; run `{report['run_kind']}`; "
        f"real model evaluation: `{report['real_model_evaluation']}`.",
        "",
        "Automatic scores measure structural bindings (contract shape, "
        "evidence ids, verbatim quotes, refusal shape), not semantic "
        "entailment. A mock run never qualifies real-model quality. "
        "All cases require human review before any release claim.",
        "",
        f"- Positive cases: {row['positive_cases']}; pass rate: {row['pass_rate']}",
        f"- Control cases: {row['case_count'] - row['positive_cases']}; "
        f"control pass rate: {row['control_pass_rate']}",
        f"- Online ready: {row['online_ready']}",
        "",
        "## Failures",
        "",
    ]
    if row["failures"]:
        lines.extend(f"- {f['id']}: {f['error']}" for f in row["failures"])
    else:
        lines.append("- No automatically detected failure; semantic review remains required.")
    lines.append(f"- Semantic review: {row['semantic_review']}; online readiness: {row['online_ready']}")
    return "\n".join(lines) + "\n"
