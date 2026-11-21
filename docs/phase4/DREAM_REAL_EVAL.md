# Dream real-model evaluation (TJ-028.2)

Controlled real-model runs over the fixed suite
``evals/dream/cases-v1.json`` (35 cases, 12 audited scenes). This
document is the runner's manual and the real-call application. The
mock evaluator (``docs/phase4/DREAM_EVALUATION.md``) is unchanged:
it proves the deterministic checks with a scripted provider and
never reads ``TIANJI_AI_*``. This runner reuses the SAME checks and
the SAME business path (``dream_ai_service.explain_dream`` over the
controlled ``DreamModelAdapter``) with a real provider.

## What was verified about the model (AMD DeepSeek-V4-Flash)

- Interface: OpenAI-compatible ``/chat/completions`` with
  ``response_format: {"type": "json_object"}``, temperature 0. The
  connector's two-level probe passed on 2026-11-21
  (``BASIC_PROBE_PASS``): the model is listed, declares JSON output,
  and answers with the gateway served name
  ``self-dploy/DeepSeek-V4-Flash``.
- Pricing (connector, from the official List models docs):
  0.14 pts / 1M input tokens, 0.28 pts / 1M output tokens for
  ``DeepSeek-V4-Flash``. ``free=false`` means calls consume the daily
  pts allowance, never money. Daily allowance: 5 pts.
- Allowed use: Token Factory is a trial and development service.
  Real-model evaluation is trial/development use and is allowed;
  a production workload behind it is barred (no SLA, no availability
  promise). The service logs prompts and outputs and keeps content
  for a 2 day rolling window. The fixed suite contains only audited
  classical dream content (no personal, health, or financial data),
  so nothing sensitive is sent.
- Contract compatibility: the model reply contract is the adapter's
  ``DREAM_REPLY_SCHEMA`` (``{domain, variant, mode, claims[]}`` with
  ``evidence_ids`` and verbatim ``quotes``). The probe proved the
  transport and the JSON shape; whether a real model fills the
  contract correctly on all 35 cases is exactly what this run
  measures.
- Credentials: the AMD key is already in the trusted environment's
  secure vault (placed 2026-11-20). The runner never reads, prints,
  or writes it: it reaches the transport only through the repo's own
  ``TIANJI_AI_*`` settings, exactly like the admin endpoint.

DuanYan is NOT a substitute: its ``deepseek-v4-flash-0731`` model is
offline and the candidate ``deepseek-v4.1-flash-1017`` is unpriced
and unverified for Chat Completions. No DuanYan call is authorized
by this document.

## Measured cost (no real call was made to measure this)

Prompt sizes were measured offline by building the exact adapter
context for every case (``build_dream_context``):

- 28 of 35 cases reach the model (12 explanation + 10 refusal +
  5 transport-fault + 1 isolation with 2 calls = 29 provider calls
  nominal). The 7 input-control cases abstain before any call.
- Prompt: ~3,250 characters per call, ~1,125-1,145 estimated tokens
  each (conservative estimator: CJK 1.5 tokens/char, other text 1
  token per 3.5 chars, +20 per message). Total prompt tokens
  ~32,726 (measured in the dry-run).
- Reply: capped at 384 tokens per call (``--max-output-tokens``,
  default 384; the operator sets ``TIANJI_AI_MAX_OUTPUT_TOKENS``
  to the cap before the run). The dry-run against the local mock
  produced 9,648 reply tokens in total (~333 per call).
- Nominal total: ~0.0073 pts (dry-run actual: prompt 0.00458 +
  reply 0.00270). Worst case (every call at the output cap, plus
  one call retried twice before a transport stop): ~0.0080 pts.
- Hard budget: **0.01 pts** (the connector's per-record cap; the run
  stops before the next case if the running estimate plus the
  remaining worst case would exceed it). That is 0.2% of the 5 pts
  daily allowance. Nominal request count: 29 POSTs; worst case 31
  POSTs (one call retried twice before the run stops); the attempt
  cap is 40 provider calls. Per-call timeout 20 s, wall-clock cap
  600 s.

The runner cannot observe transport-level retries (the adapter does
not report attempt counts), so the budget assumes one attempt per
call; the headroom between the worst case (0.0080) and the hard
budget (0.01) covers about 12 extra prompt sends. The operator
reconciles the actual spend with a live ``/usage`` quota read after
the run (see the application below).

## How to run it

```sh
# Dry-run (default): full pipeline against a LOCAL endpoint only.
# The configured endpoint host must be loopback; no authorization
# record is needed; zero real model calls.
TIANJI_AI_PROVIDER=openai-compatible \
TIANJI_AI_BASE_URL=http://127.0.0.1:18099 \
TIANJI_AI_API_KEY=test-mock-key TIANJI_AI_MODEL=mock \
TIANJI_AI_MAX_OUTPUT_TOKENS=384 \
python3 scripts/evaluate_dream_real.py --mode dry-run \
  --output-dir /tmp/dream-real-dryrun

# Real run (requires the authorization record, see below).
TIANJI_AI_PROVIDER=openai-compatible \
TIANJI_AI_BASE_URL=<amd chat endpoint> \
TIANJI_AI_API_KEY=<from the trusted environment> \
TIANJI_AI_MODEL=DeepSeek-V4-Flash \
TIANJI_AI_MAX_OUTPUT_TOKENS=384 \
python3 scripts/evaluate_dream_real.py --mode real \
  --authorization /path/to/authorization.json \
  --output-dir /path/to/run-output
```

Exit codes: 0 = every case ran (case pass/fail is in the report);
2 = the run stopped early (transport refusal, attempt cap,
wall-clock cap, or pts budget); 1 = a pre-flight refusal (zero
provider calls) or a usage error.

Outputs (``--output-dir``): ``audit.jsonl`` (one row per case:
case id, kind, verdict, checks, status, latency, measured prompt
size, estimated tokens, estimated pts, provider calls, model,
endpoint host), ``summary.json`` (caps, totals, pass rates, stop
reason), ``report.md`` (the mock report shape). No credential, API
key, full URL, or personal data is ever written.

Hard gates (all fail closed, zero provider calls when refused):
dry-run refuses a non-loopback endpoint; real mode requires an
HTTPS non-loopback endpoint, the pinned model, the configured
``max_tokens`` at or below the run cap, a worst-case pts estimate
inside the hard budget, and a valid single-use authorization
record. A transport refusal (timeout / 429 / provider failure /
not configured) stops the run at once. Per-case validation
refusals do not stop the run: they are the evidence being
collected.

Scoring a real run: explanation cases use the mock checks
unchanged. Refusal and transport-fault cases are scored as
explanations when the model reply passes validation (the system
behaved correctly; the model simply did not forge), and with the
refusal checks otherwise -- with ``verdict_matches`` relaxed to
"any clean refusal", because a real model is not scripted to fail
in one specific way; the specific refusal code is recorded for
human review. Semantic review stays a separate human step:
``semantic_*`` is ``None`` and ``online_ready`` is ``False`` in
every report this runner writes.

## Dry-run evidence (2026-11-21, local mock, zero real calls)

Ran the CLI in dry-run mode against the local mock model server
(``mock_model.py`` on ``127.0.0.1:18099``), the same stub used for
the TJ-028.3 browser E2E. Exit 0, 35/35 cases ran, stopped: none,
provider calls 29, prompt tokens (est.) 32,726, reply tokens
(est.) 9,648, pts (est.) 0.007283, worst-case estimate 0.008016
against the 0.01 hard budget, 1.1 s. Contract pass rate 1.0,
control pass rate 1.0, failures none. Verdicts: 28 explained, 5
abstained (no audited scene), 2 input-rejected. The 10 refusal
cases resolved as valid explanations (the mock is not a forger),
which is the honest dry-run outcome: it proves the pipeline, the
caps, the scoring, and the audit records -- not the validator's
forgery detection (that is the mock evaluator's job, already
done) and not real-model quality.

## Real-call application (awaits the user's separate approval)

The runner is prepared. No real model POST is authorized by this
document. Before any real call, the user must approve each item;
the operator then places the authorization record and the runner
validates and single-use-claims it (the agent never authors it).

1. **Model**: AMD ``DeepSeek-V4-Flash`` (gateway served name
   ``self-dploy/DeepSeek-V4-Flash``), the model that passed the
   two-level probe. No model substitution.
2. **Scope**: the fixed 35-case suite only (``evals/dream/cases-v1.json``,
   suite digest recorded in the summary). No other prompts, no
   production traffic, no public AI.
3. **Calls**: 29 provider calls nominal (max 40 attempts), output
   cap 384 tokens per call, per-call timeout 20 s, wall-clock cap
   600 s. The run stops at once on any transport refusal.
4. **Budget**: hard cap **0.01 pts** (nominal ~0.0073, worst case
   ~0.0080, measured as above). The operator sets
   ``TIANJI_AI_MAX_OUTPUT_TOKENS=384`` before the run.
5. **Pre-flight quota check**: the operator reads the AMD ``/usage``
   quota immediately before the run (remaining pts must cover 0.01)
   and again after the run to reconcile the actual spend against
   the audit records. If the quota cannot be confirmed, the run is
   refused.
6. **Authorization record**: after the user approves items 1-5, the
   operator places a record naming platform ``amd-token-factory``,
   model ``DeepSeek-V4-Flash``, scope ``dream real-model
   evaluation``, approver ``user``, a plain authorization id, an
   issue time, an expiry within 24 hours, and ``budget_pts`` 0.01.
   The record is single-use.
7. **After the run**: the audit records go to human semantic review
   (the automatic checks do not certify free prose). The run's
   results never flip ``ai_enabled`` and never publish anything.

## What this runner does not do

- It does not modify the AMD connector, the adapter, the service,
  or the fixed 35-case baseline.
- It does not make a real call without a valid authorization
  record, and it never authors one.
- It does not certify real-model quality: a 1.0 contract pass rate
  means the structural bindings held, not that the prose is
  correct. Semantic review is still required before any release
  claim.
- It does not open public AI, deploy anything, or change any
  budget or credential.
