# Dream release gap audit (TJ-028.3, pre-launch)

Audit of the full AI dream chain as merged on main ``1e311aa3``
(#588 + #589 + #590): user dream input -> audited dream retrieval
-> controlled model -> claims/evidence validation -> research draft
-> human review -> publish control. Verified 2026-11-21 by reading
the merged code, the deploy records, and the production health
endpoint. Nothing in this document re-implements the research or
review modules: it only names the real gaps and the follow-up task
each one needs.

## What already runs for real

- **Audited dream lookup**: the public ``POST /api/v1/dream/culture``
  and the admin research lookup run against the reviewed canonical
  dream index (12 audited scenes in the eval fixture; the sealed
  registry behind the retrieval). Lookup-only, no AI.
- **Controlled model path**: ``dream_ai_service.explain_dream`` over
  ``DreamModelAdapter`` with the controlled transport (bounded
  retries, typed errors, redacted logs), the ``DREAM_REPLY_SCHEMA``
  contract, verbatim-quote validation, diagnosis/prediction
  rejection, and refusal-without-model-text. The path is real code
  exercised end-to-end in the browser E2E with a local mock model.
- **Claims/evidence validation**: the adapter validates every reply
  (evidence ids exist, quotes verbatim and non-empty, classic title
  in the audited set); the review gate re-verifies against the
  server-side trusted retrieval at creation and at approve/publish
  (no retrieval -> 503, forged-but-consistent -> 422
  ``untrusted_evidence``).
- **Research draft + human review**: create / submit / approve /
  reject / publish / rollback with reviewer, time, reason (required
  for approve and reject), and draft version; edits force rollback
  and re-review; unreviewed drafts and refusals cannot publish;
  the AI draft type is a server-persisted immutable ``review_kind``
  (``dream_ai``) that no PATCH, transition, or rollback can clear.
  Browser E2E 3/3 plus restart persistence verified on the merged
  code (PR #590).
- **Persistence**: admin drafts and transitions persist in SQLite
  (``draft_transitions.reason`` migration is guarded); the
  production container bind-mounts the admin data directory from
  the machine, so the data survives container restarts.
- **Audit**: every admin mutation appends to the audit log with the
  actor, the action, and the draft id (never the draft content).

## What was only verified with a mock

- **The model call itself**: every end-to-end run so far used a
  local mock model (the E2E stub and the real-eval dry-run). The
  transport, the JSON contract shape, and the refusal mapping were
  proven against the real AMD endpoint only by the two-level probe
  (``BASIC_PROBE_PASS``) with fixed synthetic data -- not by a
  dream explanation call.
- **Real-model claims quality**: no real model has ever answered a
  dream case. Whether ``DeepSeek-V4-Flash`` fills the claims
  contract correctly, quotes verbatim, and abstains where it should
  is unmeasured. The runner for it is prepared
  (``docs/phase4/DREAM_REAL_EVAL.md``); the run itself awaits the
  user's separate approval.
- **Real-model latency and cost**: only estimated (nominal ~0.0073
  pts for 29 calls, worst case ~0.0080 against the 0.01 hard
  budget). No real spend has been observed.

## What needs real-model quality evaluation

- TJ-028.2's real-model run (the runner above) plus human semantic
  review of every recorded reply: the automatic checks certify
  structural bindings only, never the prose. Until a real run and
  its semantic review exist, no quality claim about the model may
  be made and no public AI may open.
- The 35 fixed cases cover 12 audited scenes. Real user narratives
  (negation, hypothesis, retelling, ambiguity, multi-scene dreams)
  are outside the fixed suite: the input-control cases prove the
  abstention paths, not the model's behaviour on unseen phrasing.

## What needs human semantic review

- Every real-model reply in the eval audit records (claims text,
  quote choice, whether the explanation stays inside the audited
  statement) before any release claim.
- Every explained research draft before publish (the workflow
  already enforces this; the review itself is a human act, not a
  checklist the code can complete).
- The 12 audited scenes' public wording: the eval fixture's short
  quotes are the reviewed registry, but the exact public display
  wording for explained results has not been human-reviewed as a
  user-facing text.

## What ordinary users are missing (public surface)

- **There is no public AI entry at all.** The public dream page
  (``/dream-culture``) is lookup-only by design ("不调用 AI，也不
  预测现实吉凶"). The AI explain endpoint is admin-only
  (``POST /api/v1/admin/research/dream/ai-explain``). No public
  endpoint serves published AI drafts, and no public page renders
  one: publishing a draft only marks it ``published`` in the admin
  backend. A launch therefore needs a deliberate public-surface
  decision (a gated user-facing explain entry with research-mode
  labelling, or a curated published-explanations page), not just a
  switch flip.
- **No user-facing explanation display**: the explained result's
  four-layer plain-Chinese presentation, the research-mode marker,
  and the explicit limits have no public component yet.
- **No user history, feedback, or correction path** for AI
  explanations.
- **No rate limiting on the AI path**: the admin ai-explain
  endpoint has no rate limit, no per-user quota, and no abuse
  control (verified: no rate-limit code in ``api.py``). Any public
  entry must add it before launch.

## Per-domain AI opening: not built

- ``ai_enabled`` is a literal ``False`` in the public response
  model (``api.py:77``) and is asserted ``False`` in every retrieval
  and result path. There is no flag, config, endpoint, or role
  that can open AI for the dream domain (or any domain). The WBS
  item "按域开 AI" was explicitly excluded from the TJ-028.3 batch
  and remains a separate task: it needs a permission model (who may
  open it), a switch mechanism (per-domain, auditable, reversible),
  and a public-surface decision (above) before it can be used.

## Production supplier, cost, and terms: not satisfied

- AMD Token Factory is a trial and development service: real-model
  evaluation is allowed, a production workload is barred, there is
  no SLA. It cannot be the production supplier.
- DuanYan is unverified: ``deepseek-v4-flash-0731`` is offline, the
  candidate ``deepseek-v4.1-flash-1017`` is unpriced and unverified
  for Chat Completions, and its balance and limits still need the
  user's console check.
- GLM-4.7-Flash (the J2 first choice) is blocked on a missing key.
- No production supplier, cost model, or terms review exists yet.
  Launch needs a supplier decision first; the eval run does not
  answer it.

## Post-publish monitoring, throttling, pause, rollback

- **Monitoring**: the admin audit log records actions; there is no
  metrics endpoint, no alerting, and no dashboard for the AI path
  (call counts, refusal rates, cost, latency). A launch needs at
  least cost/latency/refusal observability.
- **Throttling**: none on the AI path (see above).
- **Pause**: there is no kill-switch for published AI content.
  Rolling a published draft back to ``draft`` (the state machine
  allows rollback from ``published``) removes it from the published
  set, but there is no distinct "unpublish/takedown" action and no
  public-content takedown flow -- the admin-drafts module notes
  that a separate public-facing unpublish is explicitly a later
  task.
- **Rollback**: draft rollback (to a version snapshot, then
  re-review before re-publish) is implemented and tested. It covers
  drafts, not a live public surface (which does not exist yet).

## Admin SQLite data in production: persisted, not backed up

- The production API container bind-mounts the host directory
  ``/data/workspace/platform-deploy/data/tianji-admin`` to
  ``/var/lib/tianji`` (read-write); the admin database
  (``tianji_admin.db``, 36 KB) lives there and survives container
  restarts. The default path is ``tianji_admin.db`` unless
  ``TIANJI_ADMIN_DB_PATH`` is set.
- There is NO off-machine backup of this data: TJ-005.3 (off-machine
  backup) is paused by the user's 2026-11-16 decision, and a second
  copy on the same machine does not count as off-machine backup
  under the user's own criterion. A launch that accumulates real
  review records needs a backup decision before the records become
  load-bearing.

## Production public AI: still off (verified)

- Production is still ``f444ff5b`` (#587): the deploy agent's
  offline acceptance failed for ``522fe5eb`` (#588, 7 attempts),
  ``4e784353`` (#589, 4 attempts), and ``1e311aa3`` (#590, failed
  2026-11-21 15:10 UTC) -- three merges in a row, none deployed.
  The running service is untouched by those failures
  (fail-closed).
- ``/health`` on the production backend returns 200 with
  ``explanation_configured: false``; ``ai_enabled`` is a literal
  ``False`` in the merged code. Public AI is off.

## Follow-up tasks (gaps only, no rework of the merged modules)

1. **TJ-028.2 real-model run + semantic review** (prepared; awaits
   the user's approval of the application in
   ``docs/phase4/DREAM_REAL_EVAL.md``).
2. **Deploy-acceptance failure**: find why the offline acceptance
   unittest step fails for ``522fe5eb`` / ``4e784353`` / ``1e311aa3``
   (GitHub CI is green for the same SHAs) and clear it, or
   production stays on ``f444ff5b``. A full-partition repro is
   running on the trusted machine to identify the failing test;
   the failure is a new regression (it starts at ``522fe5eb``,
   the first SHA after the passing ``f444ff5b`` baseline), not a
   baseline problem. Do not deploy by hand.
3. **Public-surface decision**: gated user-facing AI explain entry
   or curated published-explanations page, with research-mode
   labelling and the four-layer plain-Chinese presentation.
4. **Per-domain AI opening**: permission model + auditable,
   reversible switch (WBS item, separate task).
5. **Production supplier decision**: AMD is eval-only; DuanYan and
   GLM need console/key verification before any production choice.
6. **Rate limiting + monitoring for the AI path** (call counts,
   refusal rates, cost, latency, alerting) before any public entry.
7. **Publish takedown**: a distinct unpublish/pause action for
   published AI content.
8. **Admin data backup**: an off-machine backup decision for the
   admin SQLite data (TJ-005.3 is paused; this is its unblock
   condition, not a new backup implementation).
9. **TJ-028.1 closeout**: its row still reads "已提交PR" although
   PR #588 merged (``522fe5eb``); it needs its own closeout event
   in a later batch (out of scope for the [B035] batch, which
   closes E0416/E0417 only).
