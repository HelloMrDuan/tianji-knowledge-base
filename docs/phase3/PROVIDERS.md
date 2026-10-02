# RAG/AI provider configuration

Default is `TIANJI_AI_PROVIDER=disabled`. Deterministic execution, evidence and retrieval readiness need no model key. Configure only process/cloud environment variables; request bodies cannot select endpoints, providers or keys.

| Variable | Meaning |
| --- | --- |
| `TIANJI_AI_PROVIDER` | `disabled`, `json-http`, or `openai-compatible` |
| `TIANJI_AI_BASE_URL` | JSON protocol: complete explanation endpoint; compatible protocol: API base or complete `/chat/completions` endpoint |
| `TIANJI_AI_MODEL` | Required compatible model ID; optional JSON protocol model label |
| `TIANJI_AI_API_KEY` | Bearer credential, only from environment |
| `TIANJI_AI_TIMEOUT_SECONDS` | Explanation budget, default20s, positive finite value ≤120s |
| `TIANJI_CORS_ORIGINS` | Optional comma-separated allowed frontend origins; unset keeps same-origin access |

Use HTTPS for external providers; HTTP is accepted only for loopback development/test servers. Credential-bearing URL user info, query and fragment are rejected. HTTP transport preserves inherited TLS CA and proxy settings, bounds response size and does not follow credential redirects. The configured provider hostname must be allowed by the hosting environment's network policy.

The JSON HTTP adapter posts `{context, instruction, response_schema, model}` and expects the structured reply described in [EXPLANATION.md](EXPLANATION.md). The compatible adapter posts standard chat-completion messages with JSON-object response formatting; it uses no vendor SDK. Both go through the same immutable-fact and citation validator. Other protocols can implement `ExplanationProvider` and be injected through `create_app(provider=...)`; this does not bypass validation.

`explain=false` does not instantiate providers, retrieve context or contact a model. `explain=true` retrieves reviewed Canonical context first, then calls the configured provider once. Configuration/provider/network/timeout/retrieval/citation failures return HTTP200 with `explanation_status=failed`, a stable non-secret `explanation_error` and unchanged chart/rules/trace/evidence. Failed or rejected model text is not returned.

Provider availability in `/health` means configuration is complete; it is not a live model or network readiness claim. Six-domain real HTTP adapter loops were verified against a local test model service; no commercial model key, live model quality or external connectivity was verified in this environment.
