# Phase 4 quality status

The explanation evaluation and safeguards are implemented. **Real-model calibration remains incomplete. On 2026-10-04 `qwen/qwen3.5-plus` passed the authenticated Qiniu JSON probe on its first attempt (81 advertised chat candidates). The complete v1 live run then failed: 77 provider timeouts and one other provider failure, with zero scoreable replies across all 72 normal cases.** Its profile was 20 seconds / 4096 output tokens. Of 30 controls, 24 passed; the six source-conflict controls failed in the legacy v1 path. The continuing v2 batch was stopped after this transport/configuration failure pattern was established; no full v2 score exists. A private-session, 90-second / 8192-token smoke diagnostic is the next step, not a release qualification. No completed human semantic review exists. N/A does not mean zero hallucinations. The key is not persisted or bound to the production API. See [local readiness and private-key calibration](LOCAL_READINESS.md).

The subsequent v2 single-positive Yijing diagnostic also timed out at 90 seconds / 8192 output tokens. All five deterministic refusal controls passed; there was still no scoreable model explanation. Lightweight-model comparisons use the identical fixed case and evidence, with advertised-model validation and job-bound selection records; these diagnostics do not grant release qualification or establish a model's parameter size.

Three same-case Qiniu comparisons completed on 2026-10-04, also at 90 seconds / 8192 tokens:

| Advertised candidate | Positive reply elapsed | Automatic positive validation | Five deterministic controls |
| --- | --- | --- | --- |
| `qwen/qwen3.7-flash` | 77.88 seconds | Failed: absent rule-match claims and invented fact pointers | 5/5 |
| `qwen-turbo` | 54.56 seconds | Failed: absent synthesis, one omitted uncertainty note and unbound uncertainty claim | 5/5 |
| `qwen3-30b-a3b-instruct-2507` | 35.34 seconds | Failed: book/chapter names differ from registered citation title and uncertainty claims lack required bindings | 5/5 |

These are **one positive case per model**, not population accuracy estimates or evidence that smaller models cannot work. Registered-title mismatches do not by themselves establish fabricated books or false prose; automatic hallucination counters include such policy failures and must not be described as human semantic findings. Each reply finished with `stop`; no reply was marked qualified. The Flash response included 16,212 reasoning characters, but this does not establish the root cause of the Plus timeouts. No complete six-domain v2 evaluation or human semantic review exists for these candidates. Diagnostic reports remain in ignored local build artifacts; all production AI remains disabled.

The table below records **v1 delivery/validation pass rates**, not a finding that model content is 0% accurate: no usable content was scored. Do not compare this failed transport profile with test-provider fixtures or claim v2 superiority from an unfinished run. The earlier cloud proxy403 restriction is historical; current local authentication and the small JSON probe succeeded.

| Domain | Fixed explanation cases | Guard cases | Real pass rate | Citation accuracy | Chart fidelity | Unsupported claims | Hallucinations | AI release status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| liuyao | 12 | 5 | 0/12 | N/A | N/A | N/A | N/A | Not qualified; transport/configuration diagnostic required |
| qimen | 12 | 5 | 0/12 | N/A | N/A | N/A | N/A | Not qualified; transport/configuration diagnostic required |
| liuren | 12 | 5 | 0/12 | N/A | N/A | N/A | N/A | Not qualified; transport/configuration diagnostic required |
| ziwei | 12 | 5 | 0/12 | N/A | N/A | N/A | N/A | Not qualified; transport/configuration diagnostic required |
| fengshui | 12 | 5 | 0/12 | N/A | N/A | N/A | N/A | Not qualified; transport/configuration diagnostic required |
| yijing | 12 | 5 | 0/12 | N/A | N/A | N/A | N/A | Not qualified; transport/configuration diagnostic required |

All 28 existing Golden Cases are reused unchanged. The same 102-case suite runs both prompt versions in tests with a deliberately mechanical fixture: v2 satisfies the stricter structural/refusal contract; legacy v1 does not cover the required categories/rules. These are protocol fixtures, not actual model-quality comparisons. The real local HTTP compatible-provider loop exercises all six domains and validates the selected system instruction. No fixture results qualify a model for release.

Failure controls include unknown/unsupported variants, invalid input, calendar/school boundaries, insufficient evidence and unresolved source conflicts. Adversarial responses cover wrong chart values and explicit chart prose contradictions in each domain, invented rules/citations, unrelated real citations, fake quotes/titles, foreign variant, omitted key facts/rules/limitations and C/D overstatement. See generated `build/phase4-protocol-regression` reports for precise test-provider failures; real-model failure cases remain unobserved.

Trial default prompt: `explanation-prompt-v2`. Frozen v1 remains an internal/research baseline and is blocked by production HTTP. No real model ID is recommended without same-suite evaluation. For production, retain `explain=false`/AI disabled; configure `openai-compatible` for calibration via environment only, then run the same suite and human review workflow in EVALUATION.md. Credentials must never enter source control or chat.

The largest remaining quality risk is semantic overreach with a real citation: matching an ID/quote does not prove the surrounding prose follows from it. Explicit contradiction/certainty checks are conservative and cannot recognize every paraphrase. A/B independent-source counts remain zero. Precise Qimen/calendar implementation evidence and Ziwei four-transformation tables retain D scope; absolute Fengshui epochs remain research-only; schools are not merged or silently switched. No Canonical/source/algorithm upgrade was made.

Formal frontend development and deterministic API integration can proceed. Render five explanation categories, exact source citations, source strength, warnings and review/degraded state. Automatic public AI explanation release remains blocked until genuine model evaluation and human review qualify the particular model/prompt/domain scope.
