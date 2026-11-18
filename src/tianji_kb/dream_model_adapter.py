"""Dream model adapter (Line C preparation, TJ-028.1).

Takes a dream narrative plus the audited retrieval from
``dream_knowledge.retrieve()`` and, ONLY when a real provider is
configured, asks the model to draft a cultural explanation grounded in
the audited evidence. The model is called ONLY through the controlled
provider transport; the reply is validated against the REAL evidence
before anything is returned.

Fail-closed contract:
- No provider configured -> status ``'not_configured'`` (no model call).
- Retrieval has no audited candidates -> status
  ``'abstained_no_reviewed_interpretation'`` (no model call).
- Provider failure / timeout / malformed reply / citation mismatch /
  diagnosis / personal prediction -> a refusal status, never model text.
- Every result carries ``ai_enabled=False`` and
  ``personal_prediction=False``: this adapter does NOT enable public
  AI. Its ``'explained'`` output is a research-stage draft for later
  human review (TJ-028.3), never a public answer.
- The lookup layer is untouched: ``retrieve()`` still runs first and
  its output is unchanged whenever the adapter abstains or refuses.

No fixed copy is presented as an AI answer: the only text this module
contains is the instruction given TO the model and the refusal reasons
returned to the caller. No end-to-end real-model verification is
possible here -- there is no vendor and no credential in the trusted
environment -- and this module never claims otherwise.
"""
import asyncio
import copy
import json
import re

from jsonschema import Draft202012Validator, ValidationError

from .ai_providers import provider_from_environment
from .dream_provider_config import load_dream_provider_config
from .model_client import sanitize_context

# The user narrative is truncated to the same 500 characters the public
# dream-research request already allows (api.AdminDreamResearchRequest).
MAX_NARRATIVE_CHARS = 500
# Audited candidate text is fixed reviewed content, not user data; the cap
# is a payload-brevity bound only, so one long reviewed entry cannot bloat
# a model call.
MAX_CANDIDATE_TEXT_CHARS = 1200

DREAM_INSTRUCTIONS = (
    "You explain a dream using ONLY the audited traditional entries given "
    "in this context. For every claim, cite only evidence_ids from the "
    "context and quote only the short quotes given, verbatim. Never invent "
    "a classical title, quotation, or source: any title you mention must "
    "appear in the provided evidence. Never diagnose a medical condition, "
    "a mental-health condition, or a pregnancy, and never predict the "
    "dreamer's future, fortune, health, or relationships. Describe what "
    "the classical text says about the scene; do not address the dreamer "
    "personally and do not repeat personal details from the narrative. "
    "If the narrative does not match any provided entry, say so and stop."
)

DREAM_REPLY_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "required": ["domain", "variant", "mode", "claims"],
    "properties": {
        "domain": {"type": "string"},
        "variant": {"type": "string"},
        "mode": {"enum": ["production", "research"]},
        "claims": {
            "type": "array",
            "minItems": 1,
            "maxItems": 6,
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["text", "evidence_ids", "quotes"],
                "properties": {
                    "text": {"type": "string", "minLength": 1, "maxLength": 2000},
                    "evidence_ids": {
                        "type": "array",
                        "minItems": 1,
                        "maxItems": 12,
                        "uniqueItems": True,
                        "items": {"type": "string"},
                    },
                    "quotes": {
                        "type": "array",
                        "maxItems": 6,
                        "items": {
                            "type": "object",
                            "additionalProperties": False,
                            "required": ["evidence_id", "text"],
                            "properties": {
                                "evidence_id": {"type": "string"},
                                "text": {"type": "string", "minLength": 1},
                            },
                        },
                    },
                },
            },
        },
    },
}

# Strong-form diagnosis markers. This is a best-effort guardrail on the
# reply text; the instruction above carries the broader prohibition.
# (Bare words such as the theme label for pregnancy are NOT banned: the
# theme itself is a legitimate dream topic, only an assertion about the
# dreamer is a diagnosis.)
_DIAGNOSIS_PATTERNS = [
    re.compile(r"诊断|确诊|患有"),
    re.compile(r"抑郁症|焦虑症|精神分裂|精神病|自闭症|躁郁症"),
    re.compile(r"你怀孕|已怀孕|会怀孕|将怀孕|流产|宫外孕"),
    re.compile(r"癌症|肿瘤|绝症"),
]

# Strong-form personal-prediction markers: assertions about the
# dreamer's own future. Describing what a classical text says in
# general terms does not match these patterns.
_PREDICTION_PATTERNS = [
    re.compile(r"预示你|预言你"),
    re.compile(r"你将会|你一定会|你必将|你将"),
    re.compile(r"必将发生|一定会发生"),
]


class DreamAdapterError(ValueError):
    """Typed adapter failure.

    code is one of: invalid_input, provider_not_configured,
    no_reviewed_interpretation, provider_failed, provider_timeout,
    invalid_model_response, citation_rejected, diagnosis_rejected,
    prediction_rejected. It is a ValueError so existing provider-failure
    handling keeps working.
    """

    def __init__(self, code, message=""):
        self.code = code
        super().__init__(message or code)


def _allowed_titles(candidates, evidence):
    """Titles a model reply may mention, taken from the real evidence.

    Collected from the evidence records' title fields and the
    candidates' ``source`` values (plus the part before '·', the way
    the generic citation validator does it). When the set is empty, any
    ``《...》`` title in a reply is rejected: an invented classical
    citation must never pass.
    """
    titles = set()
    for record in evidence.values():
        if not isinstance(record, dict):
            continue
        for field in ("classic_title", "source_title", "title"):
            value = record.get(field)
            if isinstance(value, str) and value.strip():
                titles.add(value.strip())
                titles.add(value.strip().split("·")[0])
    for candidate in candidates:
        if not isinstance(candidate, dict):
            continue
        source = candidate.get("source")
        if isinstance(source, str) and source.strip():
            titles.add(source.strip())
            titles.add(source.strip().split("·")[0])
    titles.discard("")
    return titles


def _check_diagnosis(text):
    for pattern in _DIAGNOSIS_PATTERNS:
        if pattern.search(text):
            raise DreamAdapterError(
                "diagnosis_rejected",
                "model reply contains a medical, mental-health, or "
                "pregnancy diagnosis",
            )


def _check_prediction(text):
    for pattern in _PREDICTION_PATTERNS:
        if pattern.search(text):
            raise DreamAdapterError(
                "prediction_rejected",
                "model reply predicts the dreamer's personal future",
            )


def build_dream_context(dream_text, retrieval, *, api_key=None):
    """Build the sanitized model context for one audited dream retrieval.

    The narrative is truncated to ``MAX_NARRATIVE_CHARS`` and placed
    under ``facts`` so the shared sanitizer redacts any birth instant
    in it; the top-level ``dream_narrative`` is then taken from that
    sanitized copy. Audited candidate text is capped at
    ``MAX_CANDIDATE_TEXT_CHARS`` per field. Evidence ``original_text``
    is capped at the 120-character public boundary by
    :func:`sanitize_context`, credential-named keys are dropped, and the
    call fails closed if the provider key appears anywhere in the
    payload. Birth data is never an input to the dream path at all.
    """
    if not isinstance(dream_text, str) or not dream_text.strip():
        raise DreamAdapterError(
            "invalid_input", "dream_text must be a non-empty string"
        )
    if not isinstance(retrieval, dict) or retrieval.get("domain") != "dream":
        raise DreamAdapterError(
            "invalid_input",
            "retrieval must be a dream_knowledge.retrieve() result",
        )
    candidates = retrieval.get("matched_interpretations") or []
    evidence = retrieval.get("evidence") or {}

    def _cap(value, limit):
        return value[:limit] if isinstance(value, str) else value

    safe_candidates = []
    for candidate in candidates:
        if not isinstance(candidate, dict):
            continue
        safe_candidates.append(
            {
                key: _cap(candidate.get(key), MAX_CANDIDATE_TEXT_CHARS)
                for key in (
                    "term_id",
                    "symbol",
                    "scene",
                    "source",
                    "locator",
                    "original_text_short_quote",
                    "interpretation",
                    "interpretation_type",
                    "limitations",
                    "confidence",
                    "cultural_context",
                )
                if key in candidate
            }
            | {"evidence_ids": list(candidate.get("evidence_ids") or [])}
        )
    context = {
        "domain": "dream",
        "variant": "traditional",
        "mode": "research",
        "facts": {
            "dream_narrative": dream_text.strip()[:MAX_NARRATIVE_CHARS],
        },
        "candidates": safe_candidates,
        "evidence": copy.deepcopy(evidence),
        "limitations": list(retrieval.get("limitations") or []),
        "instructions": DREAM_INSTRUCTIONS,
        "response_schema": DREAM_REPLY_SCHEMA,
    }
    clean = sanitize_context(context, api_key=api_key)
    # The model reads the narrative from the top level; take it from the
    # sanitized copy so any birth instant in it is already redacted.
    clean["dream_narrative"] = clean["facts"]["dream_narrative"]
    return clean


def validate_dream_reply(reply, context):
    """Validate a model reply against the REAL audited evidence.

    Checks, in order: the reply schema; domain/variant/mode match the
    context; every ``evidence_ids`` entry exists in the context
    evidence; every quote is a verbatim substring of the referenced
    evidence's ``original_text``; every ``《title》`` is a title the
    real evidence carries; no diagnosis; no personal prediction.
    Returns the validated claims (with their citations attached).
    Raises :class:`DreamAdapterError` on the first failure.
    """
    try:
        Draft202012Validator(context["response_schema"]).validate(reply)
    except ValidationError as error:
        raise DreamAdapterError(
            "invalid_model_response", "model reply does not match the schema"
        ) from error
    for key, expected in (
        ("domain", "dream"),
        ("variant", "traditional"),
        ("mode", "research"),
    ):
        if reply.get(key) != expected:
            raise DreamAdapterError(
                "invalid_model_response",
                f"model reply {key} does not match the context",
            )
    evidence = context.get("evidence") or {}
    candidates = context.get("candidates") or []
    allowed_titles = _allowed_titles(candidates, evidence)
    claims = []
    for claim in reply["claims"]:
        for eid in claim["evidence_ids"]:
            if eid not in evidence:
                raise DreamAdapterError(
                    "citation_rejected",
                    f"evidence_id {eid} is not in the audited evidence",
                )
        for quote in claim["quotes"]:
            record = evidence.get(quote["evidence_id"])
            if record is None or quote["evidence_id"] not in claim["evidence_ids"]:
                raise DreamAdapterError(
                    "citation_rejected",
                    "quote references evidence outside the claim",
                )
            original = record.get("original_text") if isinstance(record, dict) else None
            if not isinstance(original, str) or not quote["text"].strip():
                raise DreamAdapterError(
                    "citation_rejected", "quote has no audited source text"
                )
            if quote["text"] not in original:
                raise DreamAdapterError(
                    "citation_rejected",
                    "quote is not a verbatim substring of the audited text",
                )
        for title in re.findall(r"《([^》]+)》", claim["text"]):
            if title not in allowed_titles:
                raise DreamAdapterError(
                    "citation_rejected",
                    f"classical title {title} is not in the audited evidence",
                )
        _check_diagnosis(claim["text"])
        _check_prediction(claim["text"])
        claims.append(
            {
                **copy.deepcopy(claim),
                "citations": [
                    {
                        "evidence_id": eid,
                        "source_ref": copy.deepcopy(evidence[eid]),
                    }
                    for eid in claim["evidence_ids"]
                ],
            }
        )
    return claims


def _refusal(status, reason):
    """A fail-closed adapter result: no model text, AI stays off."""
    return {
        "status": status,
        "ai_enabled": False,
        "personal_prediction": False,
        "claims": [],
        "reason": reason,
    }


class DreamModelAdapter:
    """Dream explanation adapter over the controlled provider transport.

    ``provider`` is an object with ``async explain(context)``; when
    omitted it is resolved from the trusted environment at ``explain()``
    time (``provider_from_environment()``), so a deployment without
    credentials simply reports ``not_configured`` instead of calling
    anything. Tests inject an explicitly labelled test double.
    """

    def __init__(self, provider=None, *, config=None, timeout=None):
        self._provider = provider
        self._config = config
        # None means "use the provider config timeout (default 20s)".
        # An explicit value always wins over the config timeout.
        self._timeout = timeout

    async def explain(self, dream_text, retrieval):
        """Draft a cultural explanation for one audited dream retrieval.

        Returns a result dict. ``status`` is ``'explained'`` only when a
        model reply passed full validation; every other status is a
        refusal with no model text. ``ai_enabled`` is always False: this
        adapter never enables public AI.
        """
        if not isinstance(dream_text, str) or not dream_text.strip():
            raise DreamAdapterError(
                "invalid_input", "dream_text must be a non-empty string"
            )
        if not isinstance(retrieval, dict) or retrieval.get("domain") != "dream":
            raise DreamAdapterError(
                "invalid_input",
                "retrieval must be a dream_knowledge.retrieve() result",
            )
        candidates = retrieval.get("matched_interpretations") or []
        if retrieval.get("status") == "no_reviewed_interpretation" or not candidates:
            return _refusal(
                "abstained_no_reviewed_interpretation",
                "no audited scene matched this dream narrative",
            )
        config = (
            self._config
            if self._config is not None
            else load_dream_provider_config()
        )
        if not config.get("configured"):
            return _refusal(
                "not_configured",
                config.get("reason") or "no model provider is configured",
            )
        provider = self._provider
        if provider is None:
            provider = provider_from_environment()
        if provider is None:
            return _refusal(
                "not_configured", "no model provider is configured"
            )
        settings = config.get("settings") or {}
        try:
            context = build_dream_context(
                dream_text, retrieval, api_key=settings.get("key")
            )
        except DreamAdapterError as error:
            return _refusal(error.code, str(error))
        timeout = self._timeout
        if timeout is None:
            timeout = config.get("timeout") or 20
        try:
            reply = await asyncio.wait_for(
                provider.explain(copy.deepcopy(context)), timeout=timeout
            )
        except asyncio.TimeoutError:
            return _refusal("provider_timeout", "model call timed out")
        except Exception as error:  # noqa: BLE001 - provider failures are refusals
            return _refusal("provider_failed", f"model call failed: {error}")
        try:
            claims = validate_dream_reply(reply, context)
        except DreamAdapterError as error:
            return _refusal(error.code, str(error))
        evidence = context.get("evidence") or {}
        return {
            "status": "explained",
            "ai_enabled": False,
            "personal_prediction": False,
            "claims": claims,
            "evidence": {
                eid: copy.deepcopy(evidence[eid])
                for claim in claims
                for eid in claim["evidence_ids"]
                if eid in evidence
            },
            "limitations": list(retrieval.get("limitations") or []),
            "reason": None,
        }
