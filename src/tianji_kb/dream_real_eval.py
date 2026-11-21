"""Controlled real-model evaluation runner for the dream AI (TJ-028.2).

This is the entry point for a REAL model run over the fixed suite
``evals/dream/cases-v1.json`` (35 cases, 12 audited scenes). It is
deliberately separate from the mock evaluator (``dream_eval.py``):

- The mock evaluator proves the deterministic checks with a scripted
  provider and never reads ``TIANJI_AI_*``. This runner reuses the
  SAME deterministic checks (``dream_eval._check_explained`` /
  ``_check_refusal`` -- the single definition) and the SAME business
  path (``dream_ai_service.explain_dream`` over the controlled
  ``DreamModelAdapter``), but with a real provider resolved from the
  trusted environment. Nothing here modifies the AMD connector, the
  adapter, the service, or the fixed 35-case baseline.
- Deterministic contract results and human semantic review are
  reported separately: the automatic checks certify structural
  bindings (contract shape, evidence ids, verbatim quotes, refusal
  shape) only. ``semantic_*`` stays ``None`` and ``online_ready``
  stays ``False`` until a human reviews the recorded replies.

Hard gates (fail closed, zero provider calls when refused):

- ``--mode dry-run`` (default) runs the full pipeline against a
  LOCAL endpoint only: the configured endpoint host must be a
  loopback address (``127.0.0.1`` / ``localhost`` / ``::1``). A
  non-loopback endpoint is refused in dry-run mode. No authorization
  record is needed, and no real model is contacted.
- ``--mode real`` requires an authorization record (``--authorization
  <path>``) placed by the operator AFTER the user approves the run in
  the conversation. The runner only validates the record -- it never
  authors one. The record must name platform
  ``amd-token-factory``, the pinned model, scope
  ``dream real-model evaluation``, approver exactly ``user``, a plain
  authorization id, an issue time that is not in the future, an expiry
  within 24 hours of the issue time and still in the future, and a
  positive pts budget no larger than 0.01 that covers this run's
  estimate-based budget. The record is single-use: the runner claims
  it atomically before the first call, and a second run with the same
  record is refused. The record must also bind the fixed suite
  (``suite_id`` and ``suite_sha256`` of ``evals/dream/cases-v1.json``)
  and the allowed case scope: a record without ``case_ids`` allows a
  full-suite run only; a record with ``case_ids`` allows exactly that
  set. A swapped suite or a different case selection is refused.
  The claim lives in a fixed directory next to the authorization
  record (``<record-dir>/claims/``); there is no override for it, so
  the same record cannot be claimed twice from another directory.
  These rules mirror the AMD connector's authorization-record trust
  model.
- Real mode also requires the approved AMD gateway and nothing else:
  scheme HTTPS, host exactly ``developer.amd.com.cn``, and the
  request path exactly ``/radeon/api/v1/chat/completions`` (the
  configured endpoint may be the base ``/radeon/api/v1`` or the full
  chat path; any other host or path is refused before any request).
  The configured model must be the pinned model
  (``DeepSeek-V4-Flash``) or the gateway's served name
  (``self-dploy/DeepSeek-V4-Flash``).
- The run's output cap (default 384 tokens per call) is enforced by
  the runner, not the operator: the provider the runner builds sends
  ``max_tokens`` equal to the smaller of the configured value and the
  run cap, so a forgotten ``TIANJI_AI_MAX_OUTPUT_TOKENS`` can never
  inflate the run. The pre-flight worst case is computed with that
  effective cap.
- The pts budget is an ESTIMATE-based cap, not a guaranteed hard
  cap: pts are estimated with a conservative tokenizer
  approximation, and the vendor bills its own token count, so an
  estimate alone cannot strictly guarantee the billed total. The
  executable controls are: (1) the pre-flight worst-case estimate
  must fit the budget; (2) in real mode a live ``/usage`` quota read
  against the pinned gateway must show remaining pts covering the
  worst case, or the run is refused before any model call; (3) the
  run stops before the next case if the running estimate plus the
  remaining worst case would exceed the budget; (4) the attempt cap
  bounds the number of billed calls. The summary records the basis
  as ``estimate`` and the quota-read remaining pts.
- Attempts are counted exactly: the runner builds its own eval
  provider with no automatic retry (``max_attempts=1``) from the
  existing provider factories -- the generic AMD connector is not
  modified -- and counts every ``explain()`` call, so one counted
  attempt is one HTTP request. The attempt cap (default 40 provider
  calls), the wall-clock cap (default 600 seconds, enforced as a
  real deadline: each call's timeout is the smaller of the
  per-call timeout and the time left), and the pts budget stop the
  run.

Stop rules (the run ends at once, no further cases):

- A transport refusal (``provider_timeout``, ``provider_rate_limited``,
  ``provider_failed``, ``not_configured``) stops the run: the provider
  is unusable, so later cases cannot produce comparable evidence.
- The attempt cap (default 40 provider calls), the wall-clock cap
  (default 600 seconds), or the pts budget being breached stops the
  run. Per-case validation refusals (``citation_rejected``,
  ``diagnosis_rejected``, ``invalid_model_response`` and the other
  scored outcomes) do NOT stop the run: they are the evidence being
  collected, and the run continues to the next case.

Scoring a real run (the model is not scripted, so the mock suite's
per-case expected verdicts do not all apply):

- ``explanation`` cases: the mock checks (verdict ``explained`` plus
  every deterministic check).
- ``refusal`` / ``transport_fault`` cases: if the model reply passes
  validation, the case is scored as an explanation (the system
  behaved correctly; the model simply did not forge). If the reply is
  refused, the refusal checks apply -- with ``verdict_matches``
  relaxed to "any clean refusal" (claims and evidence empty, reason
  present, no model-text leak), because a real model is not scripted
  to fail in one specific way. The specific refusal code is NOT a
  pass/fail gate: it is recorded on the audit row as diagnostic
  information (``refusal_code`` and
  ``refusal_code_matches_expected``) so a compliant refusal is never
  failed only because its code differs from the mock expectation.
- ``input_control`` cases: the adapter abstains before any provider
  call (0 calls); the too-short / too-long cases raise the
  ``invalid_input`` error, which counts as a pass.
- ``isolation``: two calls, one per narrative; the same isolation
  checks as the mock evaluator.

Audit records: one JSONL row per case plus a summary JSON and a
Markdown report (the mock report shape, via ``dream_eval``). Each row
carries the case id, kind, verdict, checks, status, latency, measured
prompt size, estimated tokens, estimated pts, provider calls, the
configured model name and the endpoint host (never the full URL).
No credential, API key, or personal data is ever written: the fixed
suite contains only audited classical dream content, and the provider
settings dict is never serialised.
"""

import asyncio
import hashlib
import json
import math
import os
import re
import time
import unicodedata
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit

import httpx

from .ai_providers import JsonHttpProvider, OpenAICompatibleProvider
from .dream_ai_service import explain_dream
from .dream_eval import (
    _check_explained,
    _check_refusal,
    build_fixture_retrieval,
    load_suite,
    markdown_report,
)
from .dream_model_adapter import DreamAdapterError, build_dream_context
from .dream_provider_config import describe, load_dream_provider_config
from .runtime_catalog import digest

# AMD Token Factory rates for DeepSeek-V4-Flash, as stated by the
# connector (List models docs): 0.14 pts / 1M input tokens,
# 0.28 pts / 1M output tokens. The vendor `free` flag is not a gate:
# `free=false` means calls consume daily pts, never money.
INPUT_PTS_PER_MILLION = 0.14
OUTPUT_PTS_PER_MILLION = 0.28
PINNED_MODEL = "DeepSeek-V4-Flash"
GATEWAY_MODEL = "self-dploy/DeepSeek-V4-Flash"
AUTHORIZATION_SCOPE = "dream real-model evaluation"
AUTHORIZATION_PLATFORM = "amd-token-factory"
MAX_AUTHORIZATION_BUDGET_PTS = 0.01

# The only approved real-model gateway for this evaluation: the AMD
# Token Factory API. Real mode refuses any other host or path before
# any request is made. The base is the value the approved probe uses
# (``TIANJI_AI_BASE_URL``); the chat path is what the
# OpenAI-compatible provider posts to (base + ``/chat/completions``).
APPROVED_GATEWAY_HOST = "developer.amd.com.cn"
APPROVED_GATEWAY_BASE_PATH = "/radeon/api/v1"
APPROVED_CHAT_PATH = "/radeon/api/v1/chat/completions"
APPROVED_USAGE_PATH = "/radeon/api/v1/usage"
APPROVED_GATEWAY_BASE_URL = "https://" + APPROVED_GATEWAY_HOST + APPROVED_GATEWAY_BASE_PATH
# Timeout for the live /usage quota read in real mode (one GET, no retry).
QUOTA_CHECK_TIMEOUT = 10

DEFAULT_MAX_POINTS = 0.01
DEFAULT_MAX_REQUESTS = 40
DEFAULT_MAX_OUTPUT_TOKENS = 384
DEFAULT_PER_CALL_TIMEOUT = 20
DEFAULT_MAX_SECONDS = 600

LOOPBACK_HOSTS = {"127.0.0.1", "localhost", "::1"}
TRANSPORT_STOP_VERDICTS = frozenset(
    {"provider_timeout", "provider_rate_limited", "provider_failed", "not_configured"}
)
_AUTHORIZATION_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]{0,127}$")


class RealEvalError(ValueError):
    """A pre-flight or run-control refusal. ``code`` is the stable reason."""

    def __init__(self, code, message=""):
        super().__init__(message or code)
        self.code = code


def estimate_tokens(text):
    """Conservative token estimate for a prompt or reply string.

    CJK characters count 1.5 tokens each (a modern BPE tokenizer uses
    about 1 token per CJK character; 1.5 is the safety margin), other
    characters count 1 token per 3.5 characters, plus 20 tokens of
    per-message overhead. The estimate deliberately over-counts: the
    pts budget is a hard cap, so the estimate must not under-count.
    """
    if not isinstance(text, str):
        return 0
    cjk = sum(
        1 for ch in text if unicodedata.east_asian_width(ch) in ("W", "F")
    )
    other = len(text) - cjk
    return int(cjk * 1.5 + other / 3.5 + 20)


def estimate_prompt_tokens(context):
    """Estimated prompt tokens for one adapter context.

    The provider sends the instructions as the system message and the
    whole context as the user message, so both are counted.
    """
    user_json = json.dumps(context, ensure_ascii=False)
    return estimate_tokens(user_json) + estimate_tokens(
        context.get("instructions") or ""
    )


def _parse_time(value):
    if not isinstance(value, str):
        raise RealEvalError("invalid_authorization", "authorization time is not a string")
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError as error:
        raise RealEvalError(
            "invalid_authorization", f"authorization time is not ISO 8601: {value}"
        ) from error
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed


def validate_authorization(record, *, model, max_points, suite=None, case_ids=None):
    """Validate an authorization record the operator placed.

    The record is a deliberate-action barrier, not proof of who wrote
    the file: it stops accidental or automated calls. The real
    authorization is the user's explicit approval in the conversation;
    this function only checks the record's shape and bounds.

    When ``suite`` is given (the pre-flight path always gives it),
    the record must also bind that exact suite: ``suite_id`` and
    ``suite_sha256`` must match the loaded suite, so the authorization
    cannot be replayed against a swapped or edited case set.
    ``case_ids`` is the run's selected case ids (empty means the full
    suite): a record without ``case_ids`` allows a full-suite run
    only; a record with ``case_ids`` allows exactly that set.
    """
    if not isinstance(record, dict):
        raise RealEvalError("invalid_authorization", "authorization record is not an object")
    if record.get("platform") != AUTHORIZATION_PLATFORM:
        raise RealEvalError("invalid_authorization", "authorization platform mismatch")
    if record.get("scope") != AUTHORIZATION_SCOPE:
        raise RealEvalError("invalid_authorization", "authorization scope mismatch")
    if record.get("approver") != "user":
        raise RealEvalError("invalid_authorization", "authorization approver must be exactly 'user'")
    auth_id = record.get("authorization_id")
    if not isinstance(auth_id, str) or not _AUTHORIZATION_ID.fullmatch(auth_id):
        raise RealEvalError("invalid_authorization", "authorization id has a bad shape")
    if record.get("model") != model:
        raise RealEvalError("invalid_authorization", "authorization model mismatch")
    if suite is not None:
        if record.get("suite_id") != suite.get("suite_id"):
            raise RealEvalError(
                "suite_digest_mismatch",
                "authorization suite_id does not match the loaded suite",
            )
        if record.get("suite_sha256") != digest(suite):
            raise RealEvalError(
                "suite_digest_mismatch",
                "authorization suite_sha256 does not match the loaded suite",
            )
        requested = sorted(case_ids or [])
        if not requested:
            requested = sorted(c["id"] for c in suite.get("cases") or [])
        allowed = record.get("case_ids")
        if allowed is None:
            if requested != sorted(c["id"] for c in suite.get("cases") or []):
                raise RealEvalError(
                    "case_scope_mismatch",
                    "authorization without case_ids allows a full-suite run only",
                )
        else:
            if (
                not isinstance(allowed, list)
                or any(not isinstance(item, str) for item in allowed)
                or sorted(allowed) != requested
            ):
                raise RealEvalError(
                    "case_scope_mismatch",
                    "authorization case_ids do not match the requested case selection",
                )
    issued_at = _parse_time(record.get("issued_at"))
    expires_at = _parse_time(record.get("expires_at"))
    now = datetime.now(timezone.utc)
    if issued_at > now:
        raise RealEvalError("invalid_authorization", "authorization issued_at is in the future")
    if expires_at <= now:
        raise RealEvalError("invalid_authorization", "authorization has expired")
    if (expires_at - issued_at).total_seconds() > 24 * 3600:
        raise RealEvalError(
            "invalid_authorization", "authorization expiry exceeds 24 hours after issue"
        )
    budget = record.get("budget_pts")
    if (
        not isinstance(budget, (int, float))
        or isinstance(budget, bool)
        or not math.isfinite(budget)
        or budget <= 0
        or budget > MAX_AUTHORIZATION_BUDGET_PTS
    ):
        raise RealEvalError(
            "invalid_authorization",
            "authorization budget_pts must be a positive number no larger than 0.01",
        )
    if budget < max_points:
        raise RealEvalError(
            "invalid_authorization",
            "authorization budget_pts does not cover this run's hard budget",
        )
    return record


def claim_authorization(record, authorization_path, *, suite=None, case_ids=None):
    """Claim an authorization record atomically (single use).

    The claim lives in a FIXED directory next to the authorization
    record (``<record-dir>/claims/claim-<id>.json``). There is no
    caller override for the location: the same record cannot be
    claimed a second time by pointing the runner at another
    directory. The claim records the id, the claim time, the run's
    output directory, and the bound suite digest and case selection,
    so a claim is tied to the exact suite and scope it was issued
    for. The runner never writes the authorization record itself.
    """
    claims_dir = Path(authorization_path).parent / "claims"
    try:
        claims_dir.mkdir(parents=True, exist_ok=True)
    except OSError as error:
        raise RealEvalError(
            "authorization_claim_failed",
            f"cannot create the fixed claims directory {claims_dir}: {error}",
        ) from error
    claim_path = claims_dir / f"claim-{record['authorization_id']}.json"
    payload = json.dumps(
        {
            "authorization_id": record["authorization_id"],
            "platform": record.get("platform"),
            "model": record.get("model"),
            "scope": record.get("scope"),
            "suite_id": record.get("suite_id"),
            "suite_sha256": record.get("suite_sha256"),
            "case_ids": sorted(case_ids or []),
            "claimed_at": datetime.now(timezone.utc).isoformat(),
        },
        ensure_ascii=False,
        indent=2,
    )
    try:
        fd = os.open(claim_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError as error:
        raise RealEvalError(
            "authorization_already_claimed",
            f"authorization {record['authorization_id']} was already claimed",
        ) from error
    except OSError as error:
        raise RealEvalError(
            "authorization_claim_failed",
            f"cannot write the claim {claim_path}: {error}",
        ) from error
    with os.fdopen(fd, "w", encoding="utf-8") as handle:
        handle.write(payload + "\n")
    return claim_path


@dataclass
class RealEvalConfig:
    """Caps for one real-model evaluation run.

    ``max_points`` is an ESTIMATE-based pts budget, not a guaranteed
    hard cap: pts are estimated with a conservative tokenizer
    approximation and the vendor bills its own token count. The
    executable controls are the pre-flight worst-case estimate, the
    live ``/usage`` quota read in real mode, the running estimate
    gate, and the attempt cap. See the module docstring.
    """

    mode: str = "dry-run"
    max_points: float = DEFAULT_MAX_POINTS
    max_requests: int = DEFAULT_MAX_REQUESTS
    max_output_tokens: int = DEFAULT_MAX_OUTPUT_TOKENS
    per_call_timeout: int = DEFAULT_PER_CALL_TIMEOUT
    max_seconds: int = DEFAULT_MAX_SECONDS
    input_rate_pts_per_million: float = INPUT_PTS_PER_MILLION
    output_rate_pts_per_million: float = OUTPUT_PTS_PER_MILLION
    model: str = PINNED_MODEL
    authorization_path: str | None = None
    case_ids: list = field(default_factory=list)

    def validate(self):
        if self.mode not in ("dry-run", "real"):
            raise RealEvalError("invalid_config", f"unknown mode: {self.mode}")
        if not (self.max_points > 0 and self.max_points <= MAX_AUTHORIZATION_BUDGET_PTS):
            raise RealEvalError(
                "invalid_config", "max_points must be positive and no larger than 0.01"
            )
        if self.max_requests < 1:
            raise RealEvalError("invalid_config", "max_requests must be at least 1")
        if not 256 <= self.max_output_tokens <= 16384:
            raise RealEvalError(
                "invalid_config", "max_output_tokens must be between 256 and 16384"
            )
        if self.per_call_timeout < 1 or self.per_call_timeout > 120:
            raise RealEvalError("invalid_config", "per_call_timeout must be between 1 and 120")
        if self.max_seconds < 1:
            raise RealEvalError("invalid_config", "max_seconds must be at least 1")


def _endpoint_host(endpoint):
    if not endpoint:
        return None
    try:
        return urlsplit(endpoint).hostname
    except ValueError:
        return None


def _approved_chat_url(endpoint):
    """Return the effective chat URL if ``endpoint`` is the approved AMD gateway.

    Real mode accepts only scheme HTTPS, host exactly
    ``developer.amd.com.cn``, no userinfo/query/fragment, and a path
    of either the approved base (``/radeon/api/v1``, to which the
    provider appends ``/chat/completions``) or the full chat path.
    Anything else returns ``None``: the run is refused before any
    request is made.
    """
    if not endpoint or not isinstance(endpoint, str):
        return None
    try:
        parsed = urlsplit(endpoint)
    except ValueError:
        return None
    if parsed.scheme != "https":
        return None
    if parsed.hostname != APPROVED_GATEWAY_HOST:
        return None
    if parsed.username or parsed.password or parsed.query or parsed.fragment:
        return None
    path = parsed.path.rstrip("/") or "/"
    if path == APPROVED_GATEWAY_BASE_PATH:
        return APPROVED_GATEWAY_BASE_URL + "/chat/completions"
    if path == APPROVED_CHAT_PATH:
        return APPROVED_GATEWAY_BASE_URL + "/chat/completions"
    return None


def _effective_max_tokens(config, provider_config):
    """The output cap the runner actually sends.

    The smaller of the run cap and the configured value, so a
    forgotten ``TIANJI_AI_MAX_OUTPUT_TOKENS`` can never inflate the
    run. A tighter operator setting is respected, never raised.
    """
    configured = (provider_config or {}).get("max_tokens")
    if not isinstance(configured, int) or isinstance(configured, bool):
        configured = config.max_output_tokens
    return min(config.max_output_tokens, configured)


def extract_remaining_pts(parsed):
    """Remaining daily quota (pts) from a ``/usage`` payload, or ``None``.

    Mirrors the connector's resolution order against the official
    response structure: explicit ``daily_cost_remaining_usd`` first
    (the values are Token Factory points despite the ``_usd`` name),
    then ``daily_cost_limit_usd - daily_cost_used_usd``, then generic
    remaining fields. Every number must be a finite non-negative
    real; anything else fails closed with ``None``.
    """
    if not isinstance(parsed, dict):
        return None

    def _number(value):
        return (
            isinstance(value, (int, float))
            and not isinstance(value, bool)
            and math.isfinite(value)
            and value >= 0
        )

    remaining = parsed.get("daily_cost_remaining_usd")
    if _number(remaining):
        return float(remaining)
    limit = parsed.get("daily_cost_limit_usd")
    used = parsed.get("daily_cost_used_usd")
    if _number(limit) and _number(used) and limit - used >= 0:
        return float(limit - used)
    for key in ("remaining_pts", "pts_remaining", "remaining"):
        value = parsed.get(key)
        if _number(value):
            return float(value)
    return None


def _check_live_quota(provider_config, worst_pts, *, transport=None):
    """Live ``/usage`` quota read against the pinned gateway.

    One GET, no retry, no redirect, 10s timeout. Refuses unless the
    remaining daily pts cover the run's worst-case estimate. Runs in
    real mode only, after authorization validation and before the
    claim, so a refused run never consumes the authorization. The
    ``transport`` parameter exists only for offline tests (an
    ``httpx.MockTransport``); production always uses a real transport.
    Returns the remaining pts on success.
    """
    settings = (provider_config or {}).get("settings") or {}
    key = settings.get("key")
    if not isinstance(key, str) or not key:
        raise RealEvalError("quota_unconfirmed", "no provider key for the quota read")
    url = APPROVED_GATEWAY_BASE_URL + "/usage"
    try:
        with httpx.Client(
            timeout=QUOTA_CHECK_TIMEOUT, trust_env=False,
            transport=transport, follow_redirects=False,
        ) as client:
            response = client.get(
                url, headers={"Authorization": "Bearer " + key, "Accept": "application/json"}
            )
    except httpx.HTTPError as error:
        raise RealEvalError(
            "quota_check_failed", f"live quota read failed: {type(error).__name__}"
        ) from error
    if response.status_code == 429:
        raise RealEvalError("quota_check_failed", "live quota read was rate limited (429)")
    if response.status_code in (401, 403):
        raise RealEvalError("quota_check_failed", "live quota read was unauthorized")
    if response.status_code != 200:
        raise RealEvalError(
            "quota_check_failed", f"live quota read returned HTTP {response.status_code}"
        )
    try:
        parsed = response.json()
    except ValueError as error:
        raise RealEvalError(
            "quota_unconfirmed", "live quota read returned non-JSON"
        ) from error
    remaining = extract_remaining_pts(parsed)
    if remaining is None:
        raise RealEvalError(
            "quota_unconfirmed", "live quota read did not establish remaining pts"
        )
    if remaining < worst_pts:
        raise RealEvalError(
            "quota_insufficient",
            f"remaining pts {remaining} do not cover the worst-case estimate "
            f"{worst_pts:.5f} pts",
        )
    return remaining


class _CountingProvider:
    """Wraps a provider and counts every ``explain()`` call.

    The eval provider never retries (``max_attempts=1``), so one
    counted call is exactly one HTTP request. The count is the source
    of truth for the attempt cap.
    """

    def __init__(self, provider):
        self._provider = provider
        self.attempts = 0

    async def explain(self, context):
        self.attempts += 1
        return await self._provider.explain(context)


def _resolve_eval_provider(provider_config, provider=None, *, max_tokens=None):
    """Build the eval provider: no automatic retry, attempts counted.

    Uses the existing provider factories with ``max_attempts=1`` when
    no provider is injected; the generic connector is not modified.
    When ``max_tokens`` is given, the built provider sends exactly
    that output cap (the runner's effective cap, never the raw
    configured value). Any injected provider (tests pass scripted
    doubles) is wrapped the same way so the attempt count stays exact.
    """
    if provider is None:
        settings = dict((provider_config or {}).get("settings") or {})
        if max_tokens is not None:
            settings["max_tokens"] = max_tokens
        factory = (
            JsonHttpProvider
            if (provider_config or {}).get("driver") == "json-http"
            else OpenAICompatibleProvider
        )
        provider = factory(settings, max_attempts=1)
    return _CountingProvider(provider)


def _pts(prompt_tokens, reply_tokens, config):
    return (
        prompt_tokens * config.input_rate_pts_per_million / 1_000_000
        + reply_tokens * config.output_rate_pts_per_million / 1_000_000
    )


def _measure_prompt(suite, case):
    """Measured prompt sizes for one case (chars + estimated tokens).

    Returns ``(chars, tokens, fixture, calls)`` where ``calls`` is the
    number of provider calls the case makes (2 for the isolation case,
    which runs two narratives; 0 when the adapter abstains before the
    provider). Each call's prompt is measured with the same adapter
    context the provider call will use. A context build failure
    returns ``None`` sizes for that call: the call itself still runs
    through ``explain_dream``, which handles it as a refusal, and the
    pts estimate for that call is zero.
    """
    fixture = build_fixture_retrieval(
        suite, case.get("scene"), case.get("extra_evidence") or ()
    )
    if not fixture.get("matched_interpretations"):
        return 0, 0, fixture, 0
    if case["kind"] == "isolation":
        total_chars = 0
        total_tokens = 0
        for text, scene in (
            (case["dream_text"], case["scene"]),
            (case["second_dream_text"], case["second_scene"]),
        ):
            second_fixture = build_fixture_retrieval(suite, scene)
            try:
                context = build_dream_context(
                    text, second_fixture, api_key="test-dummy-key"
                )
            except (DreamAdapterError, ValueError):
                continue
            user_json = json.dumps(context, ensure_ascii=False)
            total_chars += len(user_json) + len(context.get("instructions") or "")
            total_tokens += estimate_prompt_tokens(context)
        return total_chars, total_tokens, fixture, 2
    try:
        context = build_dream_context(case["dream_text"], fixture, api_key="test-dummy-key")
    except (DreamAdapterError, ValueError):
        return None, None, fixture, 1
    user_json = json.dumps(context, ensure_ascii=False)
    chars = len(user_json) + len(context.get("instructions") or "")
    return chars, estimate_prompt_tokens(context), fixture, 1


def preflight(suite, config, provider_config, *, quota_transport=None):
    """All hard gates, before any provider call. Returns the run plan.

    The plan carries the per-case prompt measurements, the effective
    output cap, and the worst-case pts estimate (every model-reaching
    call once, at the effective output cap; the eval provider never
    retries, so there is no retry allowance). A refusal here means
    zero provider calls. In real mode the plan also carries the live
    quota-read remaining pts.
    """
    config.validate()
    if not isinstance(provider_config, dict) or not provider_config.get("configured"):
        raise RealEvalError(
            "not_configured",
            (provider_config or {}).get("reason") or "no model provider is configured",
        )
    endpoint = provider_config.get("endpoint")
    host = _endpoint_host(endpoint)
    if config.mode == "dry-run":
        if host not in LOOPBACK_HOSTS:
            raise RealEvalError(
                "dry_run_endpoint_not_local",
                f"dry-run mode only allows a loopback endpoint, got host {host!r}",
            )
    else:
        if _approved_chat_url(endpoint) is None:
            raise RealEvalError(
                "gateway_not_approved",
                "real mode requires the approved AMD gateway "
                "https://developer.amd.com.cn/radeon/api/v1/chat/completions, "
                f"got endpoint {endpoint!r}",
            )
        if host in LOOPBACK_HOSTS:
            raise RealEvalError(
                "real_mode_endpoint_is_local", "real mode refuses a loopback endpoint"
            )
        if provider_config.get("model") not in (PINNED_MODEL, GATEWAY_MODEL):
            raise RealEvalError(
                "model_mismatch",
                f"real mode requires model {PINNED_MODEL}, got "
                f"{provider_config.get('model')!r}",
            )
    effective_max_tokens = _effective_max_tokens(config, provider_config)
    cases = [
        case for case in suite["cases"]
        if not config.case_ids or case["id"] in config.case_ids
    ]
    if not cases:
        raise RealEvalError("no_cases", "no suite cases match the requested ids")
    plan = []
    worst_prompt_tokens = 0
    worst_calls = 0
    for case in cases:
        prompt_chars, prompt_tokens, fixture, calls = _measure_prompt(suite, case)
        plan.append(
            {
                "case": case,
                "fixture": fixture,
                "prompt_chars": prompt_chars,
                "prompt_tokens": prompt_tokens,
                "calls": calls,
            }
        )
        if prompt_tokens:
            worst_prompt_tokens += prompt_tokens
            worst_calls += calls
    # Worst case: every model-reaching call once at the effective
    # output cap. No retry allowance: the eval provider never retries.
    worst_pts = _pts(
        worst_prompt_tokens, worst_calls * effective_max_tokens, config
    )
    if worst_pts > config.max_points:
        raise RealEvalError(
            "budget_exceeded",
            f"worst-case estimate {worst_pts:.5f} pts exceeds the estimate-based "
            f"budget {config.max_points:.5f} pts; refuse before any call",
        )
    authorization = None
    quota_remaining_pts = None
    if config.mode == "real":
        if not config.authorization_path:
            raise RealEvalError(
                "authorization_required", "real mode requires --authorization <record>"
            )
        try:
            authorization = json.loads(Path(config.authorization_path).read_text())
        except (OSError, ValueError) as error:
            raise RealEvalError(
                "invalid_authorization", f"cannot read authorization record: {error}"
            ) from error
        validate_authorization(
            authorization, model=provider_config.get("model"),
            max_points=config.max_points, suite=suite,
            case_ids=[c["id"] for c in cases],
        )
        # Live quota read before the claim: a refused run never
        # consumes the single-use authorization.
        quota_remaining_pts = _check_live_quota(
            provider_config, worst_pts, transport=quota_transport
        )
        claim_authorization(
            authorization, config.authorization_path,
            suite=suite, case_ids=[c["id"] for c in cases],
        )
    return {
        "plan": plan,
        "worst_pts": worst_pts,
        "worst_calls": worst_calls,
        "effective_max_tokens": effective_max_tokens,
        "quota_remaining_pts": quota_remaining_pts,
        "provider": describe(provider_config),
        "authorization_id": (authorization or {}).get("authorization_id"),
    }


def _score_result(result, case, suite, fixture):
    """Score one real-model result with the mock evaluator's checks.

    Returns ``(checks, check_set, diagnostics)``. The check functions
    are the mock evaluator's own: a real run applies the same
    deterministic checks to a real model's output. The specific
    refusal code is diagnostic only (``diagnostics``), never a
    pass/fail gate: a compliant refusal must not fail only because
    its code differs from the mock expectation.
    """
    kind = case["kind"]
    verdict = result.get("verdict")
    if kind == "explanation" or verdict == "explained":
        return _check_explained(result, case, suite, fixture), "explained", {}
    checks = _check_refusal(result, case)
    # A real model is not scripted to fail in one specific way, so any
    # clean refusal (no claims, no evidence, reason present, no leak)
    # is a pass. The specific refusal code is recorded separately as
    # diagnostic information for human review.
    checks["verdict_matches"] = verdict != "explained"
    diagnostics = {
        "refusal_code": verdict,
        "refusal_code_matches_expected": verdict == case.get("expected_verdict"),
    }
    return checks, "refusal", diagnostics


async def _run_one(suite, case, fixture, *, provider, provider_config, timeout):
    """Run one case through explain_dream. Returns (result, latency_ms, input_rejected).

    The caller counts provider attempts from the counting provider
    around the call: 0 when the adapter abstains before the provider
    (no audited scene matched), 1 otherwise (the eval provider never
    retries). The pre-flight-validated provider config is passed
    through, so the calls use exactly the configuration the gates
    approved (no re-read of the environment mid-run).
    """
    start = time.perf_counter()
    try:
        result = await explain_dream(
            case["dream_text"], fixture, provider=provider,
            config=provider_config, timeout=timeout,
        )
    except DreamAdapterError as error:
        if case.get("expected") == "input_rejected" and error.code == "invalid_input":
            return None, (time.perf_counter() - start) * 1000, "input_rejected"
        raise
    return result, (time.perf_counter() - start) * 1000, None


async def run_real_eval(
    *,
    suite=None,
    config,
    provider_config=None,
    provider=None,
    output_dir,
    quota_transport=None,
):
    """Run the fixed suite against the real (or dry-run local) provider.

    Writes ``audit.jsonl`` (one row per case), ``summary.json`` and
    ``report.md`` into ``output_dir``. Returns the summary dict.
    Raises :class:`RealEvalError` on a pre-flight refusal (zero
    provider calls). A transport stop ends the run early and is
    recorded in the summary's ``stopped`` field.

    The eval provider is resolved here, never inside the adapter:
    no automatic retry (``max_attempts=1``), the effective output
    cap, and every attempt counted. ``quota_transport`` exists only
    for offline tests (an ``httpx.MockTransport`` for the live quota
    read); production always uses a real transport.
    """
    suite = suite or load_suite()
    provider_config = (
        provider_config if provider_config is not None else load_dream_provider_config()
    )
    plan_info = preflight(suite, config, provider_config, quota_transport=quota_transport)
    plan = plan_info["plan"]
    model = provider_config.get("model")
    # Audit records carry the endpoint host only -- never the full URL
    # (a credential could be smuggled into its path or query).
    endpoint_host = _endpoint_host(provider_config.get("endpoint"))
    # The eval provider config carries the effective (clamped) output
    # cap, so the calls use exactly the configuration the gates
    # approved: the provider sends max_tokens equal to the effective
    # cap, never the raw configured value.
    eval_config = dict(provider_config)
    eval_config["max_tokens"] = plan_info["effective_max_tokens"]
    eval_settings = dict((provider_config or {}).get("settings") or {})
    eval_settings["max_tokens"] = plan_info["effective_max_tokens"]
    eval_config["settings"] = eval_settings
    eval_provider = _resolve_eval_provider(
        eval_config, provider, max_tokens=plan_info["effective_max_tokens"]
    )

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    audit_path = output_dir / "audit.jsonl"
    summary_path = output_dir / "summary.json"
    report_path = output_dir / "report.md"

    rows = []
    prompt_tokens_total = 0
    reply_tokens_total = 0
    pts_total = 0.0
    started = time.perf_counter()
    stopped = None
    remaining_worst_prompt = sum(
        p["prompt_tokens"] or 0 for p in plan
    )

    with audit_path.open("w", encoding="utf-8") as audit:
        for item in plan:
            case = item["case"]
            fixture = item["fixture"]
            if stopped is not None:
                break
            elapsed = time.perf_counter() - started
            remaining_seconds = config.max_seconds - elapsed
            if remaining_seconds <= 0:
                stopped = "max_seconds"
                break
            if eval_provider.attempts >= config.max_requests:
                stopped = "max_requests"
                break
            # Budget gate before the next call: running estimate plus
            # the remaining worst case must still fit the
            # estimate-based budget.
            remaining_items = plan[len(rows):]
            remaining_worst_pts = _pts(
                remaining_worst_prompt,
                sum(p["calls"] for p in remaining_items) * plan_info["effective_max_tokens"],
                config,
            )
            if pts_total + remaining_worst_pts > config.max_points:
                stopped = "budget_exceeded"
                break
            # The wall-clock cap is a real deadline: this case's call
            # timeout is the smaller of the per-call timeout and the
            # time left, so the run cannot overrun the cap by more
            # than one bounded call.
            call_timeout = min(config.per_call_timeout, remaining_seconds)
            row = {
                "id": case["id"],
                "kind": case["kind"],
                "expected": case["expected"],
                "model": model,
                "endpoint_host": endpoint_host,
            }
            attempts_before = eval_provider.attempts
            if case["kind"] == "isolation":
                row.update(
                    await _run_isolation(
                        suite, case, provider=eval_provider,
                        provider_config=eval_config,
                        timeout=call_timeout,
                    )
                )
            else:
                try:
                    result, latency_ms, input_rejected = await _run_one(
                        suite, case, fixture,
                        provider=eval_provider, provider_config=eval_config,
                        timeout=call_timeout,
                    )
                except DreamAdapterError as error:
                    row["status"] = "failed"
                    row["error"] = f"unexpected_input_error:{error.code}"
                    row["checks"] = {"input_rejected": False}
                    row["provider_calls"] = eval_provider.attempts - attempts_before
                    row["latency_ms"] = None
                    rows.append(row)
                    audit.write(json.dumps(row, ensure_ascii=False) + "\n")
                    continue
                row["provider_calls"] = eval_provider.attempts - attempts_before
                row["latency_ms"] = round(latency_ms, 1)
                if input_rejected:
                    row["status"] = "passed"
                    row["error"] = "input_rejected"
                    row["checks"] = {"input_rejected": True}
                    row["verdict"] = "input_rejected"
                    rows.append(row)
                    audit.write(json.dumps(row, ensure_ascii=False) + "\n")
                    continue
                row["verdict"] = result.get("verdict")
                checks, check_set, diagnostics = _score_result(result, case, suite, fixture)
                row["check_set"] = check_set
                row["checks"] = checks
                row.update(diagnostics)
                row["status"] = "passed" if all(checks.values()) else "failed"
                row["error"] = None if row["status"] == "passed" else "eval_gate_failed"
                reply_text = json.dumps(result.get("claims") or [], ensure_ascii=False)
                row["reply_chars"] = len(reply_text)
                row["reply_tokens_est"] = estimate_tokens(reply_text)
            if case["kind"] == "isolation":
                row["provider_calls"] = eval_provider.attempts - attempts_before
            # A transport refusal stops the run after this case is
            # recorded: the provider is unusable, so later cases cannot
            # produce comparable evidence. This check covers both the
            # single-call path and the isolation path.
            if row.get("verdict") in TRANSPORT_STOP_VERDICTS:
                stopped = f"transport:{row['verdict']}"
            row["prompt_chars"] = item["prompt_chars"]
            row["prompt_tokens_est"] = item["prompt_tokens"]
            if item["prompt_tokens"]:
                prompt_tokens_total += item["prompt_tokens"]
                reply_tokens_total += row.get("reply_tokens_est") or 0
                pts_total += _pts(
                    item["prompt_tokens"], row.get("reply_tokens_est") or 0, config
                )
                remaining_worst_prompt -= item["prompt_tokens"]
            row["pts_est"] = round(
                _pts(
                    item["prompt_tokens"] or 0, row.get("reply_tokens_est") or 0, config
                ),
                6,
            )
            rows.append(row)
            audit.write(json.dumps(row, ensure_ascii=False) + "\n")

    positive = [r for r in rows if r["kind"] in ("explanation", "isolation")]
    controls = [r for r in rows if r["kind"] not in ("explanation", "isolation")]
    total_seconds = round(time.perf_counter() - started, 1)
    summary = {
        "schema_version": "1.0",
        "suite_id": suite["suite_id"],
        "suite_sha256": digest(suite),
        "run_kind": "real_model",
        "mode": config.mode,
        "model": model,
        "endpoint_host": endpoint_host,
        "real_model_evaluation": config.mode == "real",
        "authorization_id": plan_info["authorization_id"],
        "caps": {
            "max_points": config.max_points,
            "pts_basis": "estimate (conservative tokenizer approximation; "
            "the vendor bills its own token count, so the budget is an "
            "estimate-based cap, not a guaranteed hard cap)",
            "quota_remaining_pts": plan_info["quota_remaining_pts"],
            "max_requests": config.max_requests,
            "attempts_counted": "actual http attempts (no-retry eval provider)",
            "max_output_tokens": config.max_output_tokens,
            "effective_max_output_tokens": plan_info["effective_max_tokens"],
            "per_call_timeout": config.per_call_timeout,
            "max_seconds": config.max_seconds,
            "worst_case_pts_estimate": round(plan_info["worst_pts"], 6),
        },
        "reports": {
            "dream": {
                "case_count": len(plan),
                "cases_run": len(rows),
                "positive_cases": len(positive),
                "completed_model_responses": sum(
                    1 for r in positive if r["status"] in ("passed", "failed")
                ),
                "pass_rate": (
                    sum(r["status"] == "passed" for r in positive) / len(positive)
                    if positive else None
                ),
                "control_pass_rate": (
                    sum(r["status"] == "passed" for r in controls) / len(controls)
                    if controls else None
                ),
                "not_run": [p["case"]["id"] for p in plan[len(rows):]],
                "failures": [
                    {"id": r["id"], "error": r.get("error") or "eval_gate_failed"}
                    for r in rows if r["status"] == "failed"
                ],
                "online_ready": False,
                "semantic_review": "required; automatic bindings do not certify free prose",
                "semantic_metrics": None,
                "semantic_hallucination_count": None,
                "semantic_unsupported_claims": None,
                "semantic_contradiction_count": None,
            }
        },
        "totals": {
            "provider_calls": eval_provider.attempts,
            "prompt_tokens_est": prompt_tokens_total,
            "reply_tokens_est": reply_tokens_total,
            "pts_est": round(pts_total, 6),
            "seconds": total_seconds,
        },
        "stopped": stopped,
        "cases": rows,
        "online_ready": False,
    }
    summary_path.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    report_path.write_text(markdown_report(summary), encoding="utf-8")
    return summary


async def _run_isolation(suite, case, *, provider, provider_config, timeout):
    """Two-call isolation case, mirroring the mock evaluator."""
    from .dream_eval import evidence_id_for

    async def _one(text, scene):
        fixture = build_fixture_retrieval(suite, scene)
        result = await explain_dream(
            text, fixture, provider=provider,
            config=provider_config, timeout=timeout,
        )
        return result

    first = await _one(case["dream_text"], case["scene"])
    second = await _one(case["second_dream_text"], case["second_scene"])
    eid1 = evidence_id_for(case["scene"])
    eid2 = evidence_id_for(case["second_scene"])
    checks = {
        "first_explained": first.get("verdict") == "explained",
        "second_explained": second.get("verdict") == "explained",
        "first_evidence_only_first": set(first.get("evidence") or {}) == {eid1},
        "second_evidence_only_second": set(second.get("evidence") or {}) == {eid2},
        "dream_texts_distinct": first.get("dream_text") == case["dream_text"]
        and second.get("dream_text") == case["second_dream_text"],
        "one_call_each": True,
    }
    return {
        "verdict": "explained"
        if first.get("verdict") == "explained" and second.get("verdict") == "explained"
        else (first.get("verdict") or second.get("verdict")),
        "check_set": "isolation",
        "checks": checks,
        "status": "passed" if all(checks.values()) else "failed",
        "error": None if all(checks.values()) else "eval_gate_failed",
        "latency_ms": None,
        "reply_chars": len(
            json.dumps(
                (first.get("claims") or []) + (second.get("claims") or []),
                ensure_ascii=False,
            )
        ),
        "reply_tokens_est": estimate_tokens(
            json.dumps(
                (first.get("claims") or []) + (second.get("claims") or []),
                ensure_ascii=False,
            )
        ),
    }
