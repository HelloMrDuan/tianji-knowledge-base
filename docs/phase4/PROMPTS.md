# Versioned explanation contract

`explanation-prompt-v1` is the frozen Phase 3 baseline. `explanation-prompt-v2` is the stricter trial default. Registry hashes are pinned in tests; instruction changes require a new version. Protocol/schema or binding changes must also rerun the same 102-case suite. The actual OpenAI-compatible system message uses the selected context instruction; it is not a fixed vendor-specific prompt.

V2 requires five kinds: `deterministic_fact`, `rule_match`, `classical_evidence`, `synthesis`, `uncertainty`. The server supplies domain-specific key fact pointers and bindings to the executed RuleMatch IDs. All required key facts, all executed rules and all uncertainty notes must be covered. The schema accepts only typed facts, existing rules, real rule-bound evidence and literal quotations. Server-produced `sections` indexes the five kinds; quotations/citations are not generated from invented books.

Each claim declares `strength`: computed program facts, conditional C relationships, or unverified D/software/research assumptions. D scopes are taken from executed rules as well as citation metadata; a C quote cannot launder a D implementation table into a classical conclusion. Research claims and uncertainty claims are unverified. Model declarations contrary to server policy are rejected.

Missing evidence, an explicit unresolved source conflict or a mismatched evidence variant stops retrieval/model calls. Missing categories/rules/key facts/limitations, chart mutations, fictitious references, unrelated real citations, overconfident wording and explicit numeric/named contradictions reject the entire explanation while the HTTP execution result retains chart/rules/trace/evidence. In-scope unresolved conventions return `degraded_requires_review` with all limitations, rather than silently choosing another school.

Automatic checks do not prove all free-prose entailment. V2 returns `semantic_review_required=true` and `automatic_release_allowed=false`; the frontend must show uncertainty and review state. V1 is for internal comparison or explicit research; production HTTP explanations reject it. API keys, provider, model and `TIANJI_EXPLANATION_PROMPT_VERSION` are environment-only. The compatible adapter's `TIANJI_AI_MAX_OUTPUT_TOKENS` defaults to4096, configurable256..16384; timeout remains20s by default.

Both versions are run on the identical suite in CI with a deliberately mechanical test provider. This proves contract/refusal regression, not actual model quality or superiority of v2. Real configured models must run the CLI on the same suite and receive human semantic review before any release recommendation. No commercial model has been configured in this cloud environment.


## Internal admin registry view

The internal read-only endpoint `GET /api/v1/admin/system/prompts` exposes the actual immutable registry entries for review: version, exact instruction, server-computed SHA256, current environment selection, whether that selection is registered, default status and production eligibility. The admin UI does not edit Prompt text in browser state. A Prompt change requires a new version in code plus the fixed evaluation suite and review process described above.
