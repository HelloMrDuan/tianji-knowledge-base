# Phase 4 quality status

The explanation evaluation and safeguards are implemented. **Real-model calibration remains incomplete. The earlier cloud attempt to reach https://api.qnaigc.com/v1 returned proxy403 before authentication; that was a historical cloud restriction. On 2026-10-04 the user privately entered a key in the local calibration process, and `qwen/qwen3.5-plus` passed the authenticated JSON chat probe on its first attempt (81 advertised chat candidates). The v1/v2 fixed-suite evaluation is running; complete live scores and human semantic reviews are not available yet.** The key is not persisted or bound to the production API. Probe success is not an explanation-quality result or a model recommendation. N/A does not mean zero failures. See [local readiness and private-key calibration](LOCAL_READINESS.md).

| Domain | Fixed explanation cases | Guard cases | Real pass rate | Citation accuracy | Chart fidelity | Unsupported claims | Hallucinations | AI release status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| liuyao | 12 | 5 | N/A | N/A | N/A | N/A | N/A | Not qualified; live run + human review required |
| qimen | 12 | 5 | N/A | N/A | N/A | N/A | N/A | Not qualified; live run + human review required |
| liuren | 12 | 5 | N/A | N/A | N/A | N/A | N/A | Not qualified; live run + human review required |
| ziwei | 12 | 5 | N/A | N/A | N/A | N/A | N/A | Not qualified; live run + human review required |
| fengshui | 12 | 5 | N/A | N/A | N/A | N/A | N/A | Not qualified; live run + human review required |
| yijing | 12 | 5 | N/A | N/A | N/A | N/A | N/A | Not qualified; live run + human review required |

All 28 existing Golden Cases are reused unchanged. The same 102-case suite runs both prompt versions in tests with a deliberately mechanical fixture: v2 satisfies the stricter structural/refusal contract; legacy v1 does not cover the required categories/rules. These are protocol fixtures, not actual model-quality comparisons. The real local HTTP compatible-provider loop exercises all six domains and validates the selected system instruction. No fixture results qualify a model for release.

Failure controls include unknown/unsupported variants, invalid input, calendar/school boundaries, insufficient evidence and unresolved source conflicts. Adversarial responses cover wrong chart values and explicit chart prose contradictions in each domain, invented rules/citations, unrelated real citations, fake quotes/titles, foreign variant, omitted key facts/rules/limitations and C/D overstatement. See generated `build/phase4-protocol-regression` reports for precise test-provider failures; real-model failure cases remain unobserved.

Trial default prompt: `explanation-prompt-v2`. Frozen v1 remains an internal/research baseline and is blocked by production HTTP. No real model ID is recommended without same-suite evaluation. For production, retain `explain=false`/AI disabled; configure `openai-compatible` for calibration via environment only, then run the same suite and human review workflow in EVALUATION.md. Credentials must never enter source control or chat.

The largest remaining quality risk is semantic overreach with a real citation: matching an ID/quote does not prove the surrounding prose follows from it. Explicit contradiction/certainty checks are conservative and cannot recognize every paraphrase. A/B independent-source counts remain zero. Precise Qimen/calendar implementation evidence and Ziwei four-transformation tables retain D scope; absolute Fengshui epochs remain research-only; schools are not merged or silently switched. No Canonical/source/algorithm upgrade was made.

Formal frontend development and deterministic API integration can proceed. Render five explanation categories, exact source citations, source strength, warnings and review/degraded state. Automatic public AI explanation release remains blocked until genuine model evaluation and human review qualify the particular model/prompt/domain scope.
