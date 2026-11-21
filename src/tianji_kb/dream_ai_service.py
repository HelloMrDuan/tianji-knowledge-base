"""Dream AI business service (TJ-028.1 sub-slice, E0415).

Business layer between the audited dream lookup and the controlled
model adapter. It turns one dream narrative plus its audited
retrieval into the business result the research endpoint returns:

- ``dream_text``: the caller's narrative, stripped, 2-500 characters.
  This is the input association: the result is always about exactly
  this narrative, never about another request's input.
- ``elements``: the retrieval-matched dream elements (symbol, scene,
  source, evidence ids) for this narrative. They come from the
  audited retrieval, never from the model.
- ``verdict``: the adapter outcome. ``'explained'`` only when a model
  reply passed full validation; every other value is an abstention or
  a refusal (``'abstained_no_reviewed_interpretation'``,
  ``'not_configured'``, ``'provider_timeout'``,
  ``'provider_rate_limited'``, ``'provider_failed'``,
  ``'invalid_model_response'``, ``'citation_rejected'``,
  ``'diagnosis_rejected'``, ``'prediction_rejected'``,
  ``'context_rejected'``). A refusal carries no model text and no
  affirmative conclusion: a refused result never also claims an
  explanation.
- ``claims`` / ``evidence``: validated model claims with their
  citations, present only when the verdict is ``'explained'``.
- ``ai_enabled`` is always False and ``personal_prediction`` is
  always False: this service never enables public AI and never
  returns a personal prediction. An ``'explained'`` result is a
  research-stage draft for later human review (TJ-028.3), never a
  public answer.

Contract note: the model-reply contract is the adapter's
``DREAM_REPLY_SCHEMA`` (``{domain, variant, mode, claims[]}`` with
``evidence_ids`` and verbatim ``quotes``). The connector probe's
synthetic fixture shape (``{dream_text, elements, verdict}``) is a
transport-level JSON-output check, not the business contract; the
business result reuses those three field names for the input
association (``dream_text``), the matched elements (``elements``)
and the outcome (``verdict``), while the model reply itself stays
on the repository's claims contract. No second parallel contract is
created.

The service never calls ``retrieve()`` itself: the caller (the admin
endpoint) runs the audited lookup first and passes the retrieval in,
so lookup failures keep their own handling and the service stays
unit-testable with fixture retrievals. The service never touches a
real model directly: it only runs ``DreamModelAdapter`` over the
controlled provider transport, and only when a provider is
configured. With no provider configured it returns the
``'not_configured'`` refusal with zero provider calls.

Data isolation: the returned result is built from deep copies of the
retrieval and the adapter output. Mutating one call's result never
affects another call's input or output, and the input retrieval is
never modified.
"""
import copy

from .dream_model_adapter import DreamAdapterError, DreamModelAdapter

MAX_DREAM_TEXT_CHARS = 500
MIN_DREAM_TEXT_CHARS = 2

_ELEMENT_KEYS = (
    "term_id",
    "symbol",
    "scene",
    "source",
    "evidence_ids",
    "interpretation",
    "original_text_short_quote",
    "evidence_level",
)


def _elements_from_retrieval(retrieval):
    """Matched dream elements for this narrative, deep-copied.

    Only the business fields are projected: no raw source bodies, no
    internal rule ids, no trace. An element without evidence ids is
    dropped: an element the retrieval cannot trace is not presented
    as a grounded element.
    """
    elements = []
    for candidate in retrieval.get("matched_interpretations") or []:
        if not isinstance(candidate, dict):
            continue
        evidence_ids = candidate.get("evidence_ids") or []
        if not evidence_ids:
            continue
        element = {
            key: copy.deepcopy(candidate.get(key))
            for key in _ELEMENT_KEYS
            if key in candidate
        }
        element["evidence_ids"] = list(evidence_ids)
        elements.append(element)
    return elements


async def explain_dream(dream_text, retrieval, *, provider=None, config=None,
                        timeout=None):
    """Explain one dream through the controlled adapter.

    ``dream_text`` must be a string of 2-500 characters after
    stripping; ``retrieval`` must be a ``dream_knowledge.retrieve()``
    result (``domain == 'dream'``). Both violations raise
    :class:`DreamAdapterError` with code ``'invalid_input'``.

    Returns the business result dict (see the module docstring). The
    result always carries ``ai_enabled=False`` and
    ``personal_prediction=False``. Refusals carry empty ``claims``
    and empty ``evidence``.
    """
    if not isinstance(dream_text, str) or not dream_text.strip():
        raise DreamAdapterError(
            "invalid_input", "dream_text must be a non-empty string"
        )
    narrative = dream_text.strip()
    if len(narrative) < MIN_DREAM_TEXT_CHARS:
        raise DreamAdapterError(
            "invalid_input", "dream_text must be at least 2 characters"
        )
    if len(narrative) > MAX_DREAM_TEXT_CHARS:
        raise DreamAdapterError(
            "invalid_input", "dream_text must be at most 500 characters"
        )
    if not isinstance(retrieval, dict) or retrieval.get("domain") != "dream":
        raise DreamAdapterError(
            "invalid_input",
            "retrieval must be a dream_knowledge.retrieve() result",
        )
    elements = _elements_from_retrieval(retrieval)
    adapter = DreamModelAdapter(provider, config=config, timeout=timeout)
    outcome = await adapter.explain(narrative, retrieval)
    explained = outcome.get("status") == "explained"
    return {
        "dream_text": narrative,
        "elements": elements,
        "verdict": outcome.get("status"),
        "ai_enabled": False,
        "personal_prediction": False,
        "claims": copy.deepcopy(outcome.get("claims") or []) if explained else [],
        "evidence": copy.deepcopy(outcome.get("evidence") or {}) if explained else {},
        "limitations": list(retrieval.get("limitations") or []),
        "reason": outcome.get("reason"),
    }
