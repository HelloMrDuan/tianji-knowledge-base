# Grounded explanation contract

All providers implement `async explain(context: dict) -> dict`. `create_app(provider=...)` injects a replacement provider; the application always runs the same retrieval and reply validation around it. Providers cannot supply chart/rule/evidence replacements.

The explicit runtime build generates `build/production_rag.jsonl`: 692 existing reviewed Phase 1 chunks plus 23 reviewed Phase 2 excerpts, using the existing knowledge-index adapter and `RagIndex`. No whole quarantine text or modern implementation code enters this corpus. Its digest is pinned in the runtime artifact. Missing or changed RAG artifacts cause explanation failure, not chart failure.

Retrieval is restricted by domain, selected execution variant, actually executed rule IDs, their approved legacy rule/section references, and real evidence/source_ref tuples. Phase 1 excerpt labels are retained as `source_variant`; they do not select a different execution algorithm. Results are reconstituted from reviewed Canonical data, so index text cannot inject instructions or extra operations. The model receives classical quotations, not old incomplete operation skeletons.

A provider receives chart, its digest, explicit immutable fact pointers/values, executed rules, trace, source-backed evidence, retrieved context, limitations and a JSON response schema. Reply must preserve domain, variant, mode and digest; every claim binds an unchanged chart fact and real evidence IDs. Quoted original text must be an exact substring of that evidence. Unknown references, unsupported book titles/URLs, altered facts or chart replacement fields reject the entire explanation. Server-generated citation objects bind each ID to the original source_ref, commit, locator and SHA256.

The service uses copies across the provider boundary and a bounded timeout. Provider errors, malformed replies, rejected citations, timeout or missing retrieval produce `explanation_status=failed` and a stable non-secret error code; chart/rules/trace/evidence remain unchanged. `explain=false` skips retrieval and provider invocation entirely.

These checks validate structured facts, quotations and citation identity. Natural-language commentary still requires appropriate evidence review: valid citation IDs do not prove that every interpretive sentence logically follows from the quotation. AI instructions prohibit inventing ancient books, recomputation, source-grade upgrades and filling unresolved schools; source limits remain visible in output.
