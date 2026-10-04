# HTTP API v1

Install `pip install -e '.[validation,calendar,api]'`; explicitly build the runtime with `PYTHONPATH=src python scripts/build_production_runtime.py`; start `PYTHONPATH=src uvicorn tianji_kb.api:app --host 127.0.0.1 --port 8000`.

`POST /api/v1/execute` accepts `{domain, variant?, input, explain=false, mode="production"}`. The seven registered domain IDs and variants are returned by `GET /api/v1/capabilities` with complete runnable examples. Unknown domains, variants, arguments and invalid values return 422, without selecting a fallback school. Missing/stale runtime returns 503.

All domains call the same `engine.execute` through the transport. Response contains `domain/variant/mode/deterministic`, `chart`, `rule_matches`, `trace`, `evidence`, `warnings`, `limitations`, `explanation`, `explanation_status`, `explanation_error` and optional `calendar`. An omitted variant selects the registered default and returns it explicitly throughout rules/trace/evidence.

`explain=false` invokes no model and returns `explanation=null`, `explanation_status=disabled`. Until a provider is configured, `explain=true` returns HTTP 200 with unchanged chart/rules/evidence and `explanation_status=failed`, `explanation_error=provider_not_configured`.

Production does not open quarantine. To evaluate Fengshui absolute-period assumptions use `mode=research`, an explicit `year` and `epoch_year` in input; the API supplies the internal research flag and returns warnings/D epoch evidence. `input.research` is rejected; mode cannot be bypassed through nested input. Research mode does not automatically ingest or promote quarantine sources.

`GET /health` checks the reviewed runtime. OpenAPI is at `/openapi.json`, interactive documentation at `/docs` and `/redoc`. The seventh registered production domain is Bazi (`bazi`) with the deliberately narrow `ziping-structural-v1` scope: four pillars, day master, Ten-God relations and hidden stems only; it does not expose strength, useful-god, pattern or fortune judgements.

Configure AI/CORS using [PROVIDERS.md](PROVIDERS.md) and the variable names in `.env.api.example`. Explanation claims, quotations and server-generated source citations are represented in OpenAPI. The `deterministic` flag applies to chart/rules/trace/evidence, not to byte-identical AI prose.

## Protected Admin governance read API

Internal knowledge governance is not exposed through the public product API. The protected read-only endpoints are `GET /api/v1/admin/governance/conflicts`, `GET /api/v1/admin/governance/rules`, and `GET /api/v1/admin/governance/evidence`. They return reviewed conflict concepts, Canonical rule metadata with Phase 2 bindings, and approved short Evidence excerpts respectively, and only when the server has `TIANJI_ADMIN_READ_TOKEN` configured and the request carries `Authorization: Bearer <token>`.

If the server token is not configured the endpoint fails closed with HTTP 503. Missing or incorrect credentials return HTTP 401. These endpoints are read-only, never return full book bodies, RAW/Quarantine corpora, prompts or unrestricted unreviewed Evidence, and do not provide mutation operations. The web admin keeps the manually entered token in `sessionStorage` only for the current browser session; it is not bundled into frontend assets or committed to the repository. This token gate is an interim internal access boundary, not a replacement for the future user/role authentication service.

For a live service readiness check run `python scripts/check_api.py`. It checks health, reviewed RAG, all registered capability examples, deterministic repeats and OpenAPI without invoking a model. Deploy by stopping the old service, rebuilding release artifacts and starting the new process; do not change code or artifacts underneath a running release.

Phase 4 explanations add versioned prompt hashes, five typed claim categories, rule-to-fact/evidence bindings, source-strength checks, server-generated section indexes and review metadata. See [Phase 4 contract](../phase4/PROMPTS.md) and [batch evaluation](../phase4/EVALUATION.md). V2 is the trial default; production blocks legacy v1. Structural success is not an automatic AI release approval.
