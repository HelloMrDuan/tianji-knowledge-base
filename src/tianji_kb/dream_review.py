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
MAX_REVIEW_REASON_CHARS = 500


class DreamReviewError(ValueError):
    """A dream result or draft body cannot enter / pass review.

    code is one of: invalid_review_body, refusal_not_reviewable,
    incomplete_evidence, invalid_citation.
    """

    def __init__(self, code, message=""):
        self.code = code
        super().__init__(message or code)


def _is_explained(result):
    return isinstance(result, dict) and result.get("verdict") == "explained"


def build_dream_review_draft(result):
    """Build (title, body) for a review draft from an ai-explain result.

    Raises DreamReviewError unless the result is an explained result
    whose claims and evidence pass full validation.
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
    title = f"AI 解梦研究草稿：{str(result.get('dream_text') or '')[:30]}"
    body = json.dumps(
        {"kind": DREAM_REVIEW_KIND, "result": copy.deepcopy(result)},
        ensure_ascii=False,
    )
    return title, body


def _validate_explained_result(result):
    """Validate an explained result's claims against its own evidence."""
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

    Only the kind marker is checked here: a body that claims the kind
    but fails validation is still a dream draft (rejectable, but never
    approvable or publishable).
    """
    if not isinstance(body, str):
        return False
    try:
        parsed = json.loads(body)
    except (json.JSONDecodeError, TypeError):
        return False
    return isinstance(parsed, dict) and parsed.get("kind") == DREAM_REVIEW_KIND


def parse_dream_review_body(body):
    """Parse a draft body; return the embedded result, or None.

    Returns None when the body is not a dream review draft at all
    (plain-text drafts are untouched by the dream gate). Raises
    DreamReviewError when the body claims the dream kind but is
    malformed or fails validation.
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
