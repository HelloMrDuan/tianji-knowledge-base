# Public data surface and private migration gate (batch 175)

This repository is **PUBLIC**. Its current contents, including previous Git
objects, should be treated as already published. Do not assume that exporting
canonical and quarantine has removed knowledge-derived data from public view.

## Observed tracked data snapshot

At the reviewed main tree `18e0d9822e4837ee0288c7444ac18909775afc16`:

| Data area | Tracked files | Approx bytes | Assessment |
| --- | ---: | ---: | --- |
| `data/canonical` | 78 | 3,379,529 | Knowledge source body / review |
| `data/quarantine` | 121 | 7,280,701 | Text snapshots and review materials / review |
| `data/index` | 8 | 1,203,454 | Derived retrieval text / review |
| `data/product` | 2 | 1,060,711 | Product knowledge/coverage records / review |
| `data/upstream` | 19 | 322,102 | Pinned upstream texts / review |

Other existing areas include `data/reference`, `data/audit`,
`data/research`, `data/coverage`, `data/state`, and `data/registry`.
The inventory tool reports their current counts and byte sizes without
reprinting source contents. This list is a **review queue**, not a claim that
every file constitutes a trade secret or that third-party text can be
relicensed. Legal and provenance obligations still apply.

## Automated gate

`scripts/audit_public_asset_changes.py --inventory` audits the current
tracked tree without printing file bodies.

`scripts/audit_public_asset_changes.py --base <COMMIT_SHA>` examines the real
Git diff from the given base to HEAD:

- Public `data/` **additions/modifications/type changes** are blocked except
  the exact upstream metadata files `data/state/source_state.json` and
  `data/registry/discovered_candidates.json`.
- Deleting legacy data from public HEAD is allowed for an eventual cutover.
- Adding/editing application code outside `data/` is not blocked by this
  particular guard; separate bundle-leakage checks and code review still apply.
- The workflow runs this gate on pull requests and main pushes. A push check
  reports the problem **after publication**; only server-side branch rules and
  restricted write permissions can prevent a direct unreviewed push.

## Cutover prerequisites

1. Owner must provision private repository/storage and grant the private
   runner least-privilege access, keeping credentials out of public PR CI.
2. Verify real private export/import, full backend regression, knowledge
   provenance and reproducible derived artifact generation inside private CI.
3. Move raw texts, derived index, product knowledge data and source snapshots
   according to a file-by-file reviewed migration manifest.
4. Rebuild public CI as code-only/no-sensitive-source tests and keep public
   API/bundle response projection checks.
5. Remove publicly tracked sensitive files from public HEAD, with an explicit
   decision on historical exposure. Git history is not erased by a deletion
   commit. Configure branch protection on `main` before relying on PR checks.

No private repository creation, upload or historical cleanup is claimed by this
batch.
