# Phase 4 explanation evaluation

The fixed suite `evals/explanations/cases-v1.json` has 102 cases: 12 explanation cases and 5 refusal/input controls per domain. It reuses every one of the 28 Phase 2 Golden Cases unchanged. Additional cases pin existing chart snapshots; they are explanation regression oracles, not newly verified independent algorithm evidence. Cases include boundary inputs, C/D evidence, school/calendar restrictions, insufficient evidence and injected unresolved source conflicts. Refusal controls are reported separately so they cannot inflate normal explanation pass rate.

`explanation-prompt-v1` freezes the Phase 3 instruction and hash. Prompt changes require a new version, with regression on this identical suite. Unknown versions are rejected. All provider/model/key settings remain environment-only.

```bash
pip install -e '.[validation,calendar,api]'
PYTHONPATH=src python scripts/build_production_runtime.py
# No model calls, no quality score or certification:
PYTHONPATH=src python scripts/evaluate_explanations.py --dry-run
# Configured model: all six domains and registered prompt versions:
PYTHONPATH=src python scripts/evaluate_explanations.py --output build/live-evals
# Domain subset; run in separately configured environments to compare model IDs:
PYTHONPATH=src python scripts/evaluate_explanations.py --domains liuyao qimen --prompts explanation-prompt-v1
```

Each prompt generates JSON, a domain Markdown report and `comparison.json`, all bound to the same suite digest and prompt digest. Model calls are sequential and occur only when the internal tool is explicitly run without `--dry-run`. Configure `TIANJI_AI_PROVIDER=openai-compatible`, `TIANJI_AI_BASE_URL`, `TIANJI_AI_MODEL`, `TIANJI_AI_API_KEY`, optionally timeout, through secure process/cloud settings; never put keys in arguments/files/source control. No public bulk-evaluation endpoint is required.

Nine automatic dimensions measure chart values, hit rule/evidence binding, real citations/literal quotes, domain/variant and five explanation kinds. Detected hallucination/contradiction/unsupported rates cover structured references, not all possible assertions in free prose. Valid citations do not prove semantic entailment. Missing responses give N/A; service failures are not credited as evidence-based refusal. A dry run, injected test provider or local HTTP stub never qualifies a domain as production-ready. All reports require human semantic review; `online_ready` remains false until genuine model and semantic review evidence exists. A model is not recommended from fabricated or unrun scores.

If engine snapshots or Golden provenance drift, the tool records `engine_oracle_drift` rather than changing chart algorithms to improve explanation scores. Investigate such a drift as a separate engine issue.

## Human semantic review and qualification

Observed responses include the exact raw `model_reply`, public chart/rules/evidence `review_context` and both SHA256 digests. Semantic metrics remain N/A until an identified reviewer completes per-claim judgments across all nine dimensions. No automatic LLM judge is used to award itself a passing score.

```bash
PYTHONPATH=src python scripts/review_explanations.py \
  --report build/live-evals/explanation-prompt-v2.json \
  --export-template --output build/live-evals/human-review.json
# A reviewer reads review_context and model_reply; template nulls are unscored.
PYTHONPATH=src python scripts/review_explanations.py \
  --report build/live-evals/explanation-prompt-v2.json \
  --reviews build/live-evals/human-review.json \
  --output build/live-evals/reviewed-report.json
```

Review binds to the exact evaluation, suite, prompt, model, case, reply and context. Missing judgments, duplicate cases/claim indexes, changed response/context, mismatched provenance and failed judgments without specific notes are rejected. Test providers/local HTTP services never qualify even with synthetic perfect reviews. A genuine configured external run can qualify a domain for supervised beta only when the full fixed domain case set is present, every normal/refusal control passes, every normal case receives complete human review, and all semantic dimensions pass with zero detected hallucination/unsupported/contradiction claims. This qualification is model/prompt/fixture scoped, not a proof for arbitrary new inputs. API responses still require semantic review and never grant automatic release approval.

`engine-baseline-v1.json` pins 17 Phase 3 deterministic calculation/resolver files at main `73cccbd…`. Tests confirm Phase 4 has not changed them; a future engine change needs separate issue/review and explicit oracle updates. No algorithm drift was observed during this phase.
