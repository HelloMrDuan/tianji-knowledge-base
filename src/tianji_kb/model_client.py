"""Controlled model client (TJ-028.1): bounded retry, typed errors, privacy-bounded payloads.

Infrastructure only. This module is used by the existing provider transport
(`ai_providers.HttpProvider`) and by `ExplanationService` to sanitize the
context before it reaches a model. It does NOT enable user-facing AI: the
public API still rejects `explain`, `ai_enabled` stays False, and nothing
here is wired into any scenario. No real model is configured yet (no
TIANJI_AI_* credentials in the trusted environment); the client is verified
against an explicitly labelled local test double, never claimed as
real-model acceptance.
"""
import asyncio
import copy
import json
import logging
import re

import httpx

logger = logging.getLogger(__name__)

# Public-boundary quote length: sealed evidence text sent to a model is capped
# at the same 120 characters the public presentation allows per quote.
MAX_QUOTE_CHARS = 120
MAX_RAG_TEXT_CHARS = 120
MAX_RESPONSE_BYTES = 262144  # matches the existing provider cap
MAX_ATTEMPTS = 3  # one initial attempt plus two retries, transient failures only
RETRYABLE_CODES = frozenset({"network", "timeout", "rate_limit", "server"})

# A full birth instant: ISO date + time + UTC offset. Historical dates such
# as "1925-08" (a book edition) do not match and are left alone.
_BIRTH_INSTANT_RE = re.compile(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}(:\d{2})?(\.\d+)?([+-]\d{2}:?\d{2}|Z)")
_CREDENTIAL_KEY_RE = re.compile(
    r"api[-_]?key|apikey|secret|password|passwd|authorization|token",
    re.IGNORECASE,
)


class ModelClientError(ValueError):
    """Typed model-call failure.

    code is one of: network, timeout, auth, rate_limit, server,
    invalid_response. It is a ValueError so existing provider-failure
    handling (which catches ValueError/Exception) keeps working.
    """

    def __init__(self, code, message=""):
        self.code = code
        super().__init__(message or code)


def classify_status(status):
    """Map an HTTP status to a ModelClientError code (None means success)."""
    if 200 <= status < 300:
        return None
    if status in (401, 403):
        return "auth"
    if status == 429:
        return "rate_limit"
    if 500 <= status < 600:
        return "server"
    return "invalid_response"


def classify_exception(error):
    """Map a transport/parse exception to a ModelClientError code."""
    if isinstance(error, (httpx.TimeoutException, asyncio.TimeoutError)):
        return "timeout"
    if isinstance(error, (httpx.ConnectError, httpx.TransportError)):
        return "network"
    if isinstance(error, httpx.HTTPError):
        return "network"
    if isinstance(error, (json.JSONDecodeError, UnicodeDecodeError, ValueError)):
        return "invalid_response"
    # Unknown failure: fail closed, never retried.
    return "invalid_response"


def is_retryable(code):
    return code in RETRYABLE_CODES


def _redact_string(value):
    """Redact birth instants inside a single string (defense in depth)."""
    return _BIRTH_INSTANT_RE.sub("[REDACTED]", value)


def _walk_redact_birth(value, _seen=None):
    if isinstance(value, str):
        return _redact_string(value)
    if isinstance(value, dict):
        return {k: _walk_redact_birth(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_walk_redact_birth(v) for v in value]
    return value


def sanitize_context(context, *, api_key=None):
    """Return a privacy-bounded copy of an explanation context.

    - Evidence ``original_text`` (sealed canonical text) is capped at the
      public-boundary 120 characters per entry.
    - RAG ``text`` (joined sealed text) is capped at 120 characters per row.
    - Birth-instant strings and credential-named keys are removed.
    - If ``api_key`` is supplied, fail closed when it appears anywhere in
      the sanitized payload.
    Chart facts, rules, trace, metadata and the reply schema are untouched,
    so citation validation against the sanitized context stays consistent.
    """
    clean = copy.deepcopy(context)
    evidence = clean.get("evidence")
    if isinstance(evidence, dict):
        for entry in evidence.values():
            if isinstance(entry, dict) and isinstance(entry.get("original_text"), str):
                entry["original_text"] = entry["original_text"][:MAX_QUOTE_CHARS]
    rag = clean.get("rag")
    if isinstance(rag, list):
        for row in rag:
            if isinstance(row, dict) and isinstance(row.get("text"), str):
                row["text"] = row["text"][:MAX_RAG_TEXT_CHARS]
    # Defensive birth-instant redaction over the data sections only; the
    # static instruction/schema text is left alone.
    for key in ("chart", "facts", "rules", "trace", "evidence", "rag", "limitations"):
        if key in clean:
            clean[key] = _walk_redact_birth(clean[key])

    def drop_credentials(value):
        if isinstance(value, dict):
            return {
                k: drop_credentials(v)
                for k, v in value.items()
                if not _CREDENTIAL_KEY_RE.search(str(k))
            }
        if isinstance(value, list):
            return [drop_credentials(v) for v in value]
        return value

    clean = drop_credentials(clean)
    if api_key:
        blob = json.dumps(clean, ensure_ascii=False, default=str)
        if api_key in blob:
            raise ModelClientError(
                "invalid_response", "credential present in model payload"
            )
    return clean


def redact_for_log(obj, *, api_key=None, max_string=80):
    """Return a log-safe copy: credentials replaced, long strings cut.

    Safe to pass to logging. Never returns a credential value or a birth
    instant, and never returns more than a short preview of any string.
    """
    if isinstance(obj, dict):
        out = {}
        for key, value in obj.items():
            if _CREDENTIAL_KEY_RE.search(str(key)):
                out[key] = "[REDACTED]"
            else:
                out[key] = redact_for_log(value, api_key=api_key, max_string=max_string)
        return out
    if isinstance(obj, list):
        return [redact_for_log(v, api_key=api_key, max_string=max_string) for v in obj]
    if isinstance(obj, str):
        text = _redact_string(obj)
        if api_key and api_key in text:
            text = text.replace(api_key, "[REDACTED]")
        if len(text) > max_string:
            text = text[:max_string] + "…"
        return text
    return obj


class ControlledModelClient:
    """HTTP transport with bounded retry, typed errors and redacted logs.

    Retries only transient failures (network, timeout, 429, 5xx), at most
    ``max_attempts`` attempts in total. Auth failures, other 4xx, redirects
    and malformed responses are never retried. The API key is sent only as a
    Bearer header and is never written to a log or a request body.
    """

    def __init__(self, settings, *, transport=None, max_attempts=MAX_ATTEMPTS,
                 backoff_base=0.1, sleep=None):
        if type(max_attempts) is not int or max_attempts < 1:
            raise ValueError("max_attempts must be a positive integer")
        self.settings = settings
        self.transport = transport
        self.max_attempts = max_attempts
        self.backoff_base = backoff_base
        self._sleep = sleep or asyncio.sleep

    async def request(self, method, url, body=None):
        attempts = 0
        last_error = None
        while attempts < self.max_attempts:
            attempts += 1
            try:
                async with httpx.AsyncClient(
                    timeout=self.settings["timeout"], trust_env=True,
                    transport=self.transport, follow_redirects=False,
                ) as client:
                    async with client.stream(
                        method, url, json=body,
                        headers={
                            "Authorization": "Bearer " + self.settings["key"],
                            "Accept": "application/json",
                        },
                    ) as response:
                        code = classify_status(response.status_code)
                        if code is not None:
                            logger.warning(
                                "model call %s %s attempt %d/%d -> %s",
                                method, _safe_url(url), attempts,
                                self.max_attempts, code,
                            )
                            if is_retryable(code) and attempts < self.max_attempts:
                                await self._sleep(self.backoff_base * (2 ** (attempts - 1)))
                                continue
                            raise ModelClientError(code, f"HTTP {response.status_code}")
                        parts = []
                        size = 0
                        async for block in response.aiter_bytes():
                            size += len(block)
                            if size > MAX_RESPONSE_BYTES:
                                raise ModelClientError(
                                    "invalid_response", "response exceeds allowed size"
                                )
                            parts.append(block)
                        try:
                            return json.loads(b"".join(parts))
                        except (json.JSONDecodeError, UnicodeDecodeError) as error:
                            raise ModelClientError(
                                "invalid_response", "response is not valid JSON"
                            ) from error
            except ModelClientError as error:
                last_error = error
                if not is_retryable(error.code) or attempts >= self.max_attempts:
                    raise
                await self._sleep(self.backoff_base * (2 ** (attempts - 1)))
            except (httpx.TimeoutException, asyncio.TimeoutError) as error:
                last_error = ModelClientError("timeout", "model call timed out")
                logger.warning(
                    "model call %s %s attempt %d/%d -> timeout",
                    method, _safe_url(url), attempts, self.max_attempts,
                )
                if attempts >= self.max_attempts:
                    raise last_error from error
                await self._sleep(self.backoff_base * (2 ** (attempts - 1)))
            except httpx.HTTPError as error:
                last_error = ModelClientError("network", "model transport failure")
                logger.warning(
                    "model call %s %s attempt %d/%d -> network",
                    method, _safe_url(url), attempts, self.max_attempts,
                )
                if attempts >= self.max_attempts:
                    raise last_error from error
                await self._sleep(self.backoff_base * (2 ** (attempts - 1)))
        raise last_error  # pragma: no cover - loop always raises first

    async def post(self, url, body):
        return await self.request("POST", url, body)

    async def get(self, url):
        return await self.request("GET", url)


def _safe_url(url):
    """URL host/path for logs, without any query string or userinfo."""
    from urllib.parse import urlsplit

    parts = urlsplit(str(url))
    return f"{parts.scheme}://{parts.hostname or ''}{parts.path}"
