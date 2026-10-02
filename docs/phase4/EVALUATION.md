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
