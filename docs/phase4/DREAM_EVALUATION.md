# Dream offline evaluation (TJ-028.2)

The fixed suite `evals/dream/cases-v1.json` has 35 cases over the 12
real audited dream scenes (term ids, symbols, scenes, verbatim short
quotes and locators taken from the reviewed canonical dream index).
It follows the Phase 4 explanation standard
(`docs/phase4/EVALUATION.md`) without changing any threshold:

- 12 positive explanation cases (one per scene), 10 refusal cases
  (forged evidence id, non-verbatim quote, fabricated classic title,
  empty quotes, missing claims, wrong types, quote outside its claim,
  diagnosis, pregnancy diagnosis, personal prediction), 7
  input-control cases (negation, hypothetical, retold, ambiguous,
  too short, too long, no audited scene), 5 transport-fault cases
  (timeout, 429, provider failure, non-JSON reply, not configured),
  1 isolation case (two sequential requests share no state).
- A positive case passes only with verdict `explained` and every
  deterministic check: contract shape, evidence ids exist, quotes
  verbatim and non-empty, no diagnosis, no personal prediction,
  result evidence exactly the cited ids, `ai_enabled` False.
- Refusal, input-control and transport cases are controls, reported
  separately as `control_pass_rate`; they can never inflate the
  positive pass rate.
- The only provider is the labelled scripted test double
  (`ScriptedDreamProvider` in `src/tianji_kb/dream_eval.py`). The
  runner never reads `TIANJI_AI_*` credentials and never contacts a
  network. `run_kind` is `test_provider`, `real_model_evaluation`
  is always False and `online_ready` stays False: a mock run never
  qualifies real-model quality. A real-model quality evaluation
  needs separate authorization and a different runner.
- `scripts/evaluate_dream.py --dry-run` validates the suite
  (fixtures plus the pure reply validator) with zero provider calls.

```bash
PYTHONPATH=src python scripts/evaluate_dream.py --dry-run
PYTHONPATH=src python scripts/evaluate_dream.py --output build/dream-evals
```

The report (`dream-eval-v1.json` + `dream-eval-v1.md`) carries the
suite digest, per-case PASS/FAIL with the failing check names, and
the separate positive/control rates. Human semantic review remains
required before any release claim: automatic bindings do not certify
free prose.
