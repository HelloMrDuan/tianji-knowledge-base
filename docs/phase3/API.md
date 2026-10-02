# HTTP API v1

Install `pip install -e '.[validation,calendar,api]'`; explicitly build the runtime with `PYTHONPATH=src python scripts/build_production_runtime.py`; start `PYTHONPATH=src uvicorn tianji_kb.api:app --host 127.0.0.1 --port 8000`.

`POST /api/v1/execute` accepts `{domain, variant?, input, explain=false, mode="production"}`. The six registered domain IDs and variants are returned by `GET /api/v1/capabilities` with complete runnable examples. Unknown domains, variants, arguments and invalid values return 422, without selecting a fallback school. Missing/stale runtime returns 503.

All domains call the same `engine.execute` through the transport. Response contains `domain/variant/mode/deterministic`, `chart`, `rule_matches`, `trace`, `evidence`, `warnings`, `limitations`, `explanation`, `explanation_status`, `explanation_error` and optional `calendar`. An omitted variant selects the registered default and returns it explicitly throughout rules/trace/evidence.

`explain=false` invokes no model and returns `explanation=null`, `explanation_status=disabled`. Until a provider is configured, `explain=true` returns HTTP 200 with unchanged chart/rules/evidence and `explanation_status=failed`, `explanation_error=provider_not_configured`.

Production does not open quarantine. To evaluate Fengshui absolute-period assumptions use `mode=research`, an explicit `year` and `epoch_year` in input; the API supplies the internal research flag and returns warnings/D epoch evidence. `input.research` is rejected; mode cannot be bypassed through nested input. Research mode does not automatically ingest or promote quarantine sources.

`GET /health` checks the reviewed runtime. OpenAPI is at `/openapi.json`, interactive documentation at `/docs` and `/redoc`. This adds no frontend, account/payment subsystem or seventh domain.

Configure AI/CORS using [PROVIDERS.md](PROVIDERS.md) and the variable names in `.env.api.example`. Explanation claims, quotations and server-generated source citations are represented in OpenAPI. The `deterministic` flag applies to chart/rules/trace/evidence, not to byte-identical AI prose.

For a live service readiness check run `python scripts/check_api.py`. It checks health, reviewed RAG, all six capability examples, deterministic repeats and OpenAPI without invoking a model. Deploy by stopping the old service, rebuilding release artifacts and starting the new process; do not change code or artifacts underneath a running release.
