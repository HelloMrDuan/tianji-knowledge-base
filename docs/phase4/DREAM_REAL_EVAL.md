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
  default 384). The runner enforces the cap itself: it sends
  ``max_tokens`` equal to the smaller of the configured value and
  the run cap, so a forgotten ``TIANJI_AI_MAX_OUTPUT_TOKENS``
  cannot inflate the run. The dry-run against the local mock
  produced 9,648 reply tokens in total (~333 per call).
- Nominal total: ~0.0073 pts (dry-run actual: prompt 0.00458 +
  reply 0.00270). Worst case (every call at the effective output
  cap): ~0.0077 pts. The eval provider never retries, so the worst
  case is exactly the nominal 29 calls -- there is no retry
  allowance anymore.
- Budget: **0.01 pts, estimate-based** (the connector's per-record
  cap). Pts are estimated with a conservative tokenizer
  approximation and the vendor bills its own token count, so an
  estimate alone cannot strictly guarantee the billed total. The
  executable controls are: the pre-flight worst-case estimate must
  fit the budget; in real mode a live ``/usage`` quota read against
  the pinned gateway must show remaining pts covering the worst
  case, or the run is refused before any model call (and before the
  authorization is claimed, so a refused run never consumes it);
  the run stops before the next case if the running estimate plus
  the remaining worst case would exceed the budget; and the attempt
  cap (40 provider calls) bounds the number of billed calls. The
  summary records the basis as ``estimate`` and the quota-read
  remaining pts. That is 0.2% of the 5 pts daily allowance.
  Nominal request count: 29 POSTs; the attempt cap is 40 provider
  calls, and one counted attempt is exactly one HTTP request (the
  runner counts every call of its no-retry eval provider).
  Per-call timeout 20 s, wall-clock cap 600 s (enforced as a real
  deadline: each call's timeout is the smaller of 20 s and the time
  left).

The operator reconciles the actual spend with a live ``/usage``
quota read after the run (see the application below); the runner
already performs the same read before the run in real mode.

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
# The endpoint is the approved AMD gateway and nothing else.
TIANJI_AI_PROVIDER=openai-compatible \
TIANJI_AI_BASE_URL=https://developer.amd.com.cn/radeon/api/v1 \
TIANJI_AI_API_KEY=<from the trusted environment> \
TIANJI_AI_MODEL=DeepSeek-V4-Flash \
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
dry-run refuses a non-loopback endpoint; real mode requires the
approved AMD gateway only (HTTPS,
``developer.amd.com.cn``, request path
``/radeon/api/v1/chat/completions``), the pinned model, a
worst-case pts estimate inside the estimate-based budget, a live
``/usage`` quota read showing remaining pts covering the worst
case, and a valid single-use authorization record bound to the
fixed suite digest and case scope. The claim lives in a fixed
directory next to the authorization record; there is no override
for it. The runner builds its own eval provider with no automatic
retry and counts every attempt, and it clamps the output cap to
the run cap itself. A transport refusal (timeout / 429 / provider
failure / not configured) stops the run at once. Per-case
validation refusals do not stop the run: they are the evidence
being collected.

Scoring a real run: explanation cases use the mock checks
unchanged. Refusal and transport-fault cases are scored as
explanations when the model reply passes validation (the system
behaved correctly; the model simply did not forge), and with the
refusal checks otherwise -- with ``verdict_matches`` relaxed to
"any clean refusal", because a real model is not scripted to fail
in one specific way. The specific refusal code is NOT a pass/fail
gate: it is recorded on the audit row as diagnostic information
(``refusal_code`` and ``refusal_code_matches_expected``), so a
compliant refusal is never failed only because its code differs
from the mock expectation. Semantic review stays a separate human
step: ``semantic_*`` is ``None`` and ``online_ready`` is ``False``
in every report this runner writes.

## Dry-run evidence (2026-11-22, local mock, zero real calls)

Ran the CLI in dry-run mode against the local mock model server
(``mock_model.py`` on ``127.0.0.1:18099``), the same stub used for
the TJ-028.3 browser E2E. Exit 0, 35/35 cases ran, stopped: none,
provider calls 29, prompt tokens (est.) 32,726, reply tokens
(est.) 9,648, pts (est.) 0.007195, worst-case estimate 0.0077
against the 0.01 estimate-based budget, 1.1 s. Contract pass rate
1.0, control pass rate 1.0, failures none. Verdicts: 28 explained,
5 abstained (no audited scene), 2 input-rejected. The 10 refusal
cases resolved as valid explanations (the mock is not a forger),
which is the honest dry-run outcome: it proves the pipeline, the
caps, the scoring, and the audit records -- not the validator's
forgery detection (that is the mock evaluator's job, already
done) and not real-model quality. The run was repeated after the
2026-11-22 review fixes with ``TIANJI_AI_MAX_OUTPUT_TOKENS=4096``
deliberately set, to prove the runner clamps the output cap to
384 itself (summary ``effective_max_output_tokens`` 384).

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
4. **Budget**: estimate-based cap **0.01 pts** (nominal ~0.0073,
   worst case ~0.0077, measured as above). The estimate cannot
   strictly guarantee the vendor's billed total; the executable
   controls are the pre-flight worst-case estimate, the runner's
   live ``/usage`` quota read in real mode, the running estimate
   gate, and the 40-attempt cap. The operator reads the AMD
   ``/usage`` quota again after the run to reconcile the actual
   spend against the audit records.
5. **Pre-flight quota check**: performed by the runner in real mode
   (one GET ``/usage`` against the pinned gateway, before the
   authorization is claimed). The operator also reads the quota
   immediately before the run (remaining pts must cover 0.01). If
   the quota cannot be confirmed, the run is refused.
6. **Authorization record**: after the user approves items 1-5, the
   operator places a record naming platform ``amd-token-factory``,
   model ``DeepSeek-V4-Flash``, scope ``dream real-model
   evaluation``, approver ``user``, a plain authorization id, an
   issue time, an expiry within 24 hours, and ``budget_pts`` 0.01
   -- plus the binding to the fixed suite: ``suite_id``
   ``dream-eval-v1`` and the ``suite_sha256`` digest of
   ``evals/dream/cases-v1.json`` as loaded by the runner, and
   optionally ``case_ids`` for an exact subset (a record without
   ``case_ids`` allows a full-suite run only). The record is
   single-use; the claim lives in the fixed directory next to the
   record.
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
