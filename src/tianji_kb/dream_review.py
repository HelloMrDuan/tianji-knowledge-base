"""Human review for AI dream research drafts (TJ-028.3).

A dream review draft is an ordinary draft in the existing draft
store (``admin_drafts`` / ``admin_storage``): the same state machine
(draft -> submitted -> approved -> published, rejected terminal,
rollback -> draft), the same role operations, the same append-only
audit log, the same SQLite persistence. This module only defines
what may *become* a dream review draft and what may *pass* review:

- Only an ``explained`` business result (``dream_ai_service``) can
  become a draft. Refusals (abstained, not configured, provider
  errors, invalid model response, citation/diagnosis/prediction
  rejections) can never enter the review flow.
- The draft body is JSON ``{"kind": "dream_ai_review", "result":
  <business result>}``. The embedded result carries its own
  evidence snapshot, so validation is self-contained: every claim's
  evidence ids must exist in the embedded evidence, every quote
  must be a verbatim substring of the referenced audited text, every
  quote's evidence id must belong to its claim, every claim must
  have at least one quote, and no diagnosis or personal prediction
  may appear. Validation reuses the adapter's own
  ``validate_dream_reply`` (plus the schema's ``minItems: 1`` on
  quotes), so the review gate can never be weaker than the adapter.
- Editing a draft is only legal in ``draft`` status (the store
  enforces this): any content change after approval requires a
  rollback to ``draft`` and a fresh submit/approve cycle, so
  modified content is always re-reviewed before it can publish.
- The API layer re-validates the body at approve and publish time
  for dream-kind drafts, so even a body edited while in ``draft``
  status cannot reach ``approved`` or ``published`` with broken
  evidence or invalid citations.

Trust model (ChatGPT final review, 2026-11-21): client-submitted
evidence is NEVER trusted on its own. Every entry and gate below
takes the server-side audited retrieval (``operations.
dream_knowledge.retrieve`` for the result's dream text) and
verifies the submitted result against it:

- every element's term, scene, source and evidence ids must match
  the retrieval's matched interpretation for that term;
- every submitted evidence record must match the retrieval's
  record for the same id field for field (source, original text,
  classic title, locator);
- every claim is checked against the TRUSTED evidence (not the
  submitted copy), so a quote that is verbatim only against a
  forged record fails.
A fully forged but internally consistent payload therefore fails:
its ids, records or quotes do not exist in the audited retrieval.
When no audited retrieval is available the draft is refused
(``trusted_retrieval_unavailable``); the gate never downgrades to
client self-attestation. Approve and publish re-run the same
verification against a fresh server-side retrieval, so no frozen
snapshot has to be trusted either.

Draft identity (same review): whether a draft IS an AI dream draft
is decided by the server-persisted immutable marker
``DREAM_REVIEW_MARKER`` on the draft record (see ``admin_drafts``
/ ``admin_storage`` ``review_kind``), never by the editable body's
``kind`` field. ``is_dream_review_body`` below is only a structural
reader for display; it establishes no trust and must never gate an
approval.

Publishing a reviewed draft marks the *research draft* published;
it never enables public AI and never opens any domain: public
``ai_enabled`` stays False by design (per-domain opening is a
separate task).
"""

import copy
import json

from .dream_model_adapter import DREAM_REPLY_SCHEMA, validate_dream_reply
from .dream_model_adapter import DreamAdapterError

DREAM_REVIEW_KIND = "dream_ai_review"
# Server-persisted immutable draft-type marker (stored on the draft
# record as ``review_kind`` by the draft stores, set only at
# creation through the review-drafts endpoint). The API layer
# treats a draft as an AI dream draft exactly when its record
# carries this marker; the body's editable ``kind`` field is never
# consulted for that decision.
DREAM_REVIEW_MARKER = "dream_ai"
MAX_REVIEW_REASON_CHARS = 500


class DreamReviewError(ValueError):
    """A dream result or draft body cannot enter / pass review.

    code is one of: invalid_review_body, refusal_not_reviewable,
    incomplete_evidence, invalid_citation, untrusted_evidence,
    trusted_retrieval_unavailable.
    """

    def __init__(self, code, message=""):
        self.code = code
        super().__init__(message or code)


def _is_explained(result):
    return isinstance(result, dict) and result.get("verdict") == "explained"


def build_dream_review_draft(result, *, retrieval):
    """Build (title, body) for a review draft from an ai-explain result.

    ``retrieval`` is the server-side audited retrieval for the
    result's dream text (``dream_knowledge.retrieve``); it is
    required and the submitted result is verified against it (see
    ``validate_result_against_retrieval``). Raises DreamReviewError
    unless the result is an explained result whose claims and
    evidence pass full validation against that retrieval.
    """
    if not isinstance(result, dict):
        raise DreamReviewError(
            "invalid_review_body", "review draft needs an ai-explain result object"
        )
    if not _is_explained(result):
        raise DreamReviewError(
            "refusal_not_reviewable",
            f"only an explained result can enter review (verdict: {result.get('verdict')!r})",
        )
    _validate_explained_result(result)
    validate_result_against_retrieval(result, retrieval)
    title = f"AI 解梦研究草稿：{str(result.get('dream_text') or '')[:30]}"
    body = json.dumps(
        {"kind": DREAM_REVIEW_KIND, "result": copy.deepcopy(result)},
        ensure_ascii=False,
    )
    return title, body


def validate_result_against_retrieval(result, retrieval):
    """Verify an explained result against the audited retrieval.

    The submitted evidence is treated as an untrusted claim: every
    element, every evidence record and every claim quote must match
    the server-side audited retrieval for the same dream text.
    Raises DreamReviewError (``untrusted_evidence`` for a mismatch,
    ``invalid_citation`` for a claim/quote failure,
    ``trusted_retrieval_unavailable`` when there is no usable
    retrieval to check against).
    """
    if not isinstance(retrieval, dict) or retrieval.get("domain") != "dream":
        raise DreamReviewError(
            "trusted_retrieval_unavailable",
            "no audited dream retrieval available to verify against",
        )
    trusted_evidence = retrieval.get("evidence")
    if not isinstance(trusted_evidence, dict) or not trusted_evidence:
        raise DreamReviewError(
            "trusted_retrieval_unavailable",
            "audited retrieval carries no evidence",
        )
    candidates = retrieval.get("matched_interpretations")
    if not isinstance(candidates, list):
        raise DreamReviewError(
            "trusted_retrieval_unavailable",
            "audited retrieval has no interpretation candidates",
        )
    by_term = {
        candidate.get("term_id"): candidate
        for candidate in candidates
        if isinstance(candidate, dict)
    }
    for element in result.get("elements") or []:
        candidate = by_term.get(element.get("term_id"))
        if candidate is None:
            raise DreamReviewError(
                "untrusted_evidence",
                f"element term {element.get('term_id')!r} is not in the audited retrieval",
            )
        if (
            element.get("scene") != candidate.get("scene")
            or element.get("source") != candidate.get("source")
        ):
            raise DreamReviewError(
                "untrusted_evidence",
                "element scene/source does not match the audited retrieval",
            )
        if set(element.get("evidence_ids") or []) != set(
            candidate.get("evidence_ids") or []
        ):
            raise DreamReviewError(
                "untrusted_evidence",
                "element evidence ids do not match the audited retrieval",
            )
    submitted = result.get("evidence") or {}
    for evidence_id, record in submitted.items():
        trusted = trusted_evidence.get(evidence_id)
        if trusted is None:
            raise DreamReviewError(
                "untrusted_evidence",
                f"evidence {evidence_id!r} is not in the audited retrieval",
            )
        if not isinstance(record, dict):
            raise DreamReviewError(
                "untrusted_evidence", f"evidence {evidence_id!r} is not a record"
            )
        for key, value in trusted.items():
            if record.get(key) != value:
                raise DreamReviewError(
                    "untrusted_evidence",
                    f"evidence {evidence_id!r} field {key!r} does not match the audited record",
                )
    claims = result.get("claims") or []
    reply = {
        "domain": "dream",
        "variant": "traditional",
        "mode": "research",
        "claims": [
            {
                "text": claim.get("text"),
                "evidence_ids": claim.get("evidence_ids"),
                "quotes": claim.get("quotes"),
            }
            for claim in claims
            if isinstance(claim, dict)
        ],
    }
    if len(reply["claims"]) != len(claims):
        raise DreamReviewError("invalid_citation", "a claim is not an object")
    # Claims are checked against the TRUSTED evidence, never the
    # submitted copy: a quote that is verbatim only against a forged
    # record fails here.
    context = {
        "response_schema": DREAM_REPLY_SCHEMA,
        "evidence": trusted_evidence,
        "candidates": [
            {"source": candidate.get("source")} for candidate in candidates
        ],
    }
    try:
        validate_dream_reply(reply, context)
    except DreamAdapterError as error:
        raise DreamReviewError("invalid_citation", str(error)) from error


def _validate_explained_result(result):
    """Validate an explained result's claims against its own evidence.

    Self-consistency only: this proves the stored draft is
    displayable, never that its evidence is real. Callers must
    still run ``validate_result_against_retrieval`` before trusting
    the result.
    """
    claims = result.get("claims")
    evidence = result.get("evidence")
    elements = result.get("elements")
    if not isinstance(claims, list) or not claims:
        raise DreamReviewError("incomplete_evidence", "explained result has no claims")
    if not isinstance(evidence, dict) or not evidence:
        raise DreamReviewError(
            "incomplete_evidence", "explained result has no evidence"
        )
    if not isinstance(elements, list) or not elements:
        raise DreamReviewError(
            "incomplete_evidence", "explained result has no elements"
        )
    for element in elements:
        for eid in element.get("evidence_ids") or []:
            if eid not in evidence:
                raise DreamReviewError(
                    "incomplete_evidence",
                    "element cites evidence not in the result",
                )
    reply = {
        "domain": "dream",
        "variant": "traditional",
        "mode": "research",
        "claims": [
            {
                "text": claim.get("text"),
                "evidence_ids": claim.get("evidence_ids"),
                "quotes": claim.get("quotes"),
            }
            for claim in claims
            if isinstance(claim, dict)
        ],
    }
    if len(reply["claims"]) != len(claims):
        raise DreamReviewError("invalid_citation", "a claim is not an object")
    context = {
        "response_schema": DREAM_REPLY_SCHEMA,
        "evidence": evidence,
        "candidates": [
            {"source": element.get("source")} for element in elements
        ],
    }
    try:
        validate_dream_reply(reply, context)
    except DreamAdapterError as error:
        raise DreamReviewError("invalid_citation", str(error)) from error


def is_dream_review_body(body):
    """Whether a draft body claims the dream review kind (never raises).

    Structural only: a body that claims the kind but fails
    validation is still a dream draft (rejectable, but never
    approvable or publishable). This establishes NO trust and must
    never gate an approval; the server-persisted marker on the
    draft record (``DREAM_REVIEW_MARKER``) decides that.
    """
    if not isinstance(body, str):
        return False
    try:
        parsed = json.loads(body)
    except (json.JSONDecodeError, TypeError):
        return False
    return isinstance(parsed, dict) and parsed.get("kind") == DREAM_REVIEW_KIND


def extract_dream_review_result(body):
    """Parse a draft body into its embedded result (structural only).

    Returns the embedded result, or None when the body is not a
    dream review body at all (plain-text drafts are untouched by the
    dream gate). Raises DreamReviewError when the body claims the
    dream kind but is malformed or fails self-validation.

    This establishes NO trust: the returned result must still be
    verified with ``validate_result_against_retrieval`` against a
    fresh server-side audited retrieval before any approval or
    publish decision.
    """
    if not isinstance(body, str):
        raise DreamReviewError("invalid_review_body", "draft body must be text")
    try:
        parsed = json.loads(body)
    except (json.JSONDecodeError, TypeError):
        return None
    if not isinstance(parsed, dict) or parsed.get("kind") != DREAM_REVIEW_KIND:
        return None
    result = parsed.get("result")
    if not _is_explained(result):
        raise DreamReviewError(
            "refusal_not_reviewable",
            "dream review draft must carry an explained result",
        )
    _validate_explained_result(result)
    return copy.deepcopy(result)


def parse_dream_review_body(body, *, retrieval):
    """Parse a draft body and verify it against the audited retrieval.

    Returns the embedded result, or None when the body is not a
    dream review body at all. Raises DreamReviewError when the body
    claims the dream kind but is malformed, fails self-validation,
    or does not match the server-side audited retrieval.
    """
    result = extract_dream_review_result(body)
    if result is None:
        return None
    validate_result_against_retrieval(result, retrieval)
    return result


def validate_review_reason(reason):
    """A review reason: non-empty string, at most 500 characters."""
    if not isinstance(reason, str) or not reason.strip():
        raise DreamReviewError(
            "invalid_review_body", "review actions need a non-empty reason"
        )
    if len(reason) > MAX_REVIEW_REASON_CHARS:
        raise DreamReviewError(
            "invalid_review_body", "review reason is too long (max 500 characters)"
        )
    return reason.strip()
