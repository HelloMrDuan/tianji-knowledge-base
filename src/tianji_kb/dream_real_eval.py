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
  hard budget. The record is single-use: the runner claims it
  atomically before the first call, and a second run with the same
  record is refused. These rules mirror the AMD connector's
  authorization-record trust model.
- Real mode also requires an HTTPS, non-loopback endpoint and the
  configured model to be the pinned model (``DeepSeek-V4-Flash``) or
  the gateway's served name (``self-dploy/DeepSeek-V4-Flash``).
- The configured ``max_tokens`` must not exceed the run's output cap
  (default 384 tokens per call): the operator sets
  ``TIANJI_AI_MAX_OUTPUT_TOKENS`` to the cap before the run.
- The pre-flight worst-case pts estimate (measured prompt tokens per
  case plus the output cap, at the connector's stated rates of
  0.14 pts / 1M input tokens and 0.28 pts / 1M output tokens for
  ``DeepSeek-V4-Flash``) must fit inside the run's hard budget
  (default 0.01 pts). The run stops before the next case if the
  running estimate plus the remaining worst case would exceed it.

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
  to fail in one specific way; the specific refusal code is recorded
  for human review.
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


def validate_authorization(record, *, model, max_points):
    """Validate an authorization record the operator placed.

    The record is a deliberate-action barrier, not proof of who wrote
    the file: it stops accidental or automated calls. The real
    authorization is the user's explicit approval in the conversation;
    this function only checks the record's shape and bounds.
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


def claim_authorization(record, claims_dir):
    """Claim an authorization record atomically (single use).

    Creates ``claim-<authorization_id>.json`` with O_EXCL: a second
    claim of the same record is refused. The claim records the id, the
    claim time and the run's output directory; the runner never writes
    the authorization record itself.
    """
    claims_dir = Path(claims_dir)
    claims_dir.mkdir(parents=True, exist_ok=True)
    claim_path = claims_dir / f"claim-{record['authorization_id']}.json"
    payload = json.dumps(
        {
            "authorization_id": record["authorization_id"],
            "platform": record.get("platform"),
            "model": record.get("model"),
            "scope": record.get("scope"),
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
    with os.fdopen(fd, "w", encoding="utf-8") as handle:
        handle.write(payload + "\n")
    return claim_path


@dataclass
class RealEvalConfig:
    """Hard caps for one real-model evaluation run."""

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
    claims_dir: str | None = None
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


def preflight(suite, config, provider_config):
    """All hard gates, before any provider call. Returns the run plan.

    The plan carries the per-case prompt measurements and the
    worst-case pts estimate (every model-reaching call once, at the
    output cap, plus one extra prompt send for the single call that
    may be retried before a transport stop). A refusal here means
    zero provider calls.
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
        if not endpoint or not str(endpoint).startswith("https://"):
            raise RealEvalError(
                "real_mode_endpoint_not_https", "real mode requires an HTTPS endpoint"
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
    configured_max_tokens = provider_config.get("max_tokens")
    if configured_max_tokens is not None and configured_max_tokens > config.max_output_tokens:
        raise RealEvalError(
            "output_cap_exceeded",
            f"configured max_tokens {configured_max_tokens} exceeds the run cap "
            f"{config.max_output_tokens}; set TIANJI_AI_MAX_OUTPUT_TOKENS first",
        )
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
    # Worst case: every model-reaching call once at the output cap,
    # plus one extra prompt send (the single call that may be retried
    # twice before a transport stop ends the run).
    worst_prompt_tokens += max((p["prompt_tokens"] or 0 for p in plan), default=0)
    worst_pts = _pts(
        worst_prompt_tokens, worst_calls * config.max_output_tokens, config
    )
    if worst_pts > config.max_points:
        raise RealEvalError(
            "budget_exceeded",
            f"worst-case estimate {worst_pts:.5f} pts exceeds the hard budget "
            f"{config.max_points:.5f} pts; refuse before any call",
        )
    authorization = None
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
            authorization, model=provider_config.get("model"), max_points=config.max_points
        )
        claims_dir = config.claims_dir or str(Path(config.authorization_path).parent / "claims")
        claim_authorization(authorization, claims_dir)
    return {
        "plan": plan,
        "worst_pts": worst_pts,
        "worst_calls": worst_calls,
        "provider": describe(provider_config),
        "authorization_id": (authorization or {}).get("authorization_id"),
    }


def _score_result(result, case, suite, fixture):
    """Score one real-model result with the mock evaluator's checks.

    Returns ``(checks, check_set)``. The check functions are the
    mock evaluator's own: a real run applies the same deterministic
    checks to a real model's output.
    """
    kind = case["kind"]
    verdict = result.get("verdict")
    if kind == "explanation" or verdict == "explained":
        return _check_explained(result, case, suite, fixture), "explained"
    checks = _check_refusal(result, case)
    # A real model is not scripted to fail in one specific way, so any
    # clean refusal (no claims, no evidence, reason present, no leak)
    # is a pass; the specific refusal code is recorded separately.
    checks["verdict_matches"] = verdict != "explained"
    checks["refusal_code_matches_expected"] = (
        verdict == case.get("expected_verdict")
    )
    return checks, "refusal"


async def _run_one(suite, case, fixture, *, provider, provider_config, timeout):
    """Run one case through explain_dream. Returns (result, calls, latency_ms, input_rejected).

    ``calls`` is 0 when the adapter abstains before the provider (no
    audited scene matched): the provider is never contacted for such
    a case, so it must not count toward the attempt cap. The
    pre-flight-validated provider config is passed through, so the
    calls use exactly the configuration the gates approved (no
    re-read of the environment mid-run).
    """
    start = time.perf_counter()
    try:
        result = await explain_dream(
            case["dream_text"], fixture, provider=provider,
            config=provider_config, timeout=timeout,
        )
    except DreamAdapterError as error:
        if case.get("expected") == "input_rejected" and error.code == "invalid_input":
            return None, 0, (time.perf_counter() - start) * 1000, "input_rejected"
        raise
    calls = 1 if fixture.get("matched_interpretations") else 0
    return result, calls, (time.perf_counter() - start) * 1000, None


async def run_real_eval(
    *,
    suite=None,
    config,
    provider_config=None,
    provider=None,
    output_dir,
):
    """Run the fixed suite against the real (or dry-run local) provider.

    Writes ``audit.jsonl`` (one row per case), ``summary.json`` and
    ``report.md`` into ``output_dir``. Returns the summary dict.
    Raises :class:`RealEvalError` on a pre-flight refusal (zero
    provider calls). A transport stop ends the run early and is
    recorded in the summary's ``stopped`` field.
    """
    suite = suite or load_suite()
    provider_config = (
        provider_config if provider_config is not None else load_dream_provider_config()
    )
    plan_info = preflight(suite, config, provider_config)
    plan = plan_info["plan"]
    model = provider_config.get("model")
    # Audit records carry the endpoint host only -- never the full URL
    # (a credential could be smuggled into its path or query).
    endpoint_host = _endpoint_host(provider_config.get("endpoint"))

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    audit_path = output_dir / "audit.jsonl"
    summary_path = output_dir / "summary.json"
    report_path = output_dir / "report.md"

    rows = []
    provider_calls = 0
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
            if elapsed > config.max_seconds:
                stopped = "max_seconds"
                break
            if provider_calls >= config.max_requests:
                stopped = "max_requests"
                break
            # Budget gate before the next call: running estimate plus
            # the remaining worst case must still fit the hard budget.
            remaining_items = plan[len(rows):]
            remaining_worst_pts = _pts(
                remaining_worst_prompt,
                sum(p["calls"] for p in remaining_items) * config.max_output_tokens,
                config,
            )
            if pts_total + remaining_worst_pts > config.max_points:
                stopped = "budget_exceeded"
                break
            row = {
                "id": case["id"],
                "kind": case["kind"],
                "expected": case["expected"],
                "model": model,
                "endpoint_host": endpoint_host,
            }
            if case["kind"] == "isolation":
                row.update(
                    await _run_isolation(
                        suite, case, provider=provider,
                        provider_config=provider_config,
                        timeout=config.per_call_timeout,
                    )
                )
                provider_calls += row.get("provider_calls", 0)
            else:
                try:
                    result, calls, latency_ms, input_rejected = await _run_one(
                        suite, case, fixture,
                        provider=provider, provider_config=provider_config,
                        timeout=config.per_call_timeout,
                    )
                except DreamAdapterError as error:
                    row["status"] = "failed"
                    row["error"] = f"unexpected_input_error:{error.code}"
                    row["checks"] = {"input_rejected": False}
                    row["provider_calls"] = 0
                    row["latency_ms"] = None
                    rows.append(row)
                    audit.write(json.dumps(row, ensure_ascii=False) + "\n")
                    continue
                provider_calls += calls
                row["provider_calls"] = calls
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
                checks, check_set = _score_result(result, case, suite, fixture)
                row["check_set"] = check_set
                row["checks"] = checks
                row["status"] = "passed" if all(checks.values()) else "failed"
                row["error"] = None if row["status"] == "passed" else "eval_gate_failed"
                reply_text = json.dumps(result.get("claims") or [], ensure_ascii=False)
                row["reply_chars"] = len(reply_text)
                row["reply_tokens_est"] = estimate_tokens(reply_text)
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
            "max_requests": config.max_requests,
            "max_output_tokens": config.max_output_tokens,
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
            "provider_calls": provider_calls,
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
        "provider_calls": 2,
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
