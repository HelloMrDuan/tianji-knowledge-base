# Private knowledge CI cutover — staged contract (batch 173)

**Current state:** the public repository still includes `data/canonical` and
`data/quarantine`. This document is a preparation contract, **not a completed
migration**. The public Git history stays public.

## What is implemented and verifiable

- `scripts/export_private_knowledge.py` produces a restricted export with
  `private-export-manifest.json`, file-level SHA256, and size metadata.
- `scripts/restore_private_knowledge.py` checks the *entire* declared export,
  rejects missing/extra/tampered files, symlinks, duplicate/unsafe paths, and
  refuses to merge into existing knowledge directories.
- A consumer can stage only into a **clean workspace outside any Git checkout**.
  The tool has no network or token handling. No fallback to checkout-supplied
  canonical/quarantine data is permitted.
- Public CI checks this behavior with deterministic byte-level tests **and a
  real export/re-import of the current tracked assets**. It does not contact or
  verify the future private repository.

## Private infrastructure still required

1. Independently provision a **PRIVATE** owner-controlled repository or encrypted
   private storage, restrict collaborators and Actions, and determine which
   published source texts may legally be mirrored. Do not add private credentials
   to workflows triggered by PRs in this public repository.
2. Export from a trusted local checkout into a new path **outside that checkout**:
   `python -m scripts.export_private_knowledge --destination /secure/new-export`
3. Privately transfer the exported tree and its manifest. From a **private runner**
   verify: `python -m scripts.restore_private_knowledge --source /secure/export --verify-only`
4. In the private runner, create a fresh *non-Git* application workspace with
   code copied from an audited public commit. Exclude `.git`,
   `data/canonical` and `data/quarantine` from that copy. Then run
   `python -m scripts.restore_private_knowledge --source /secure/export --workspace /secure/clean-app`
   from a location where this package is on PYTHONPATH. The import refuses
   pre-existing knowledge dirs. Run the real backend/test suite there; inspect
   logs and build artifacts for confidential content.
5. Only after the private tests, provenance review and integrity checks are
   successful: remove owned private datasets from public **HEAD**, remove
   knowledge-updating commits from public scheduled workflows, and change public
   CI to code-only checks. Run full knowledge validation exclusively in private
   CI. Public index, reference, research, snapshots, audit, coverage, evaluation
   fixtures, generated bundles and web assets must be separately classified for
   possible knowledge leakage; canonical/quarantine alone are not a full audit.
6. Existing public commits remain retrievable. A fresh private repository
   does not undo previous publication. Treat any prior disclosure, licenses,
   third-party origins and Git history remediation as a separate review.

**Hard stop:** do not delete public assets, break public CI, add PATs to public
PR jobs, or claim private hosting until a real private storage destination and
its successful full-content CI run can be confirmed.


## Public automated-write freeze (batch 174)

Until a private destination is provisioned, this PUBLIC repository must NOT
automatically refresh or commit new canonical, quarantine or derivative texts.

- The `KB Source Sync` workflow becomes `KB Source Metadata Sync`.
  It still checks public upstream commit and license metadata, but stages only
  `data/state/source_state.json`. A staged-path allowlist rejects other files.
- The `Refresh Audited Knowledge Files` workflow is retired from public HEAD.
  New full-text source refresh and derived-index writes must move to private
  infrastructure, with its own authenticated private CI.
- The legacy raw-text ingestion commands fail closed if invoked in GitHub
  Actions under `HelloMrDuan/tianji-knowledge-base`. Local/manual use outside
  that precise public automation context does **not** mean that a destination is
  secured; operators must still choose restricted storage.
- Existing Actions runs that were queued **before** these changes, other
  privileged writers, forks and the public Git history are not neutralized by
  this change; inspect and cancel any old in-flight content-writing jobs when
  operationally possible.

This is a **write freeze, not a data migration**. Public HEAD continues to
contain substantial knowledge-bearing surfaces outside the two export roots,
including `data/index`, `data/product`, `data/upstream`,
`data/reference`, `data/audit`, `data/coverage` and
`data/research`. Review provenance and confidentiality file by file before
removal or re-publication. Do not resume public content sync after this step.

Once private CI runs against a verified private snapshot, replace public
Knowledge Base validation with code-only tests and a non-sensitive synthetic
contract suite. Do not configure private repository credentials in public
pull_request workflows.


## Complete-data snapshot contract (batch 176)

The original v1 exporter remains supported for older restricted canonical/quarantine
copies. Its scope is **not sufficient** for private infrastructure cutover.

New v2 workflow copies **all 11 current `data/` areas** (including index,
product, upstream, provenance, state and registry), with a separate SHA256
manifest and exact directory/file-membership verification. Only file metadata,
not contents, is printed by the CLI.

Run from the **trusted public code checkout** to a new external absolute path:

```bash
python scripts/private_data_snapshot.py --export /secure/new-complete-bundle
python scripts/private_data_snapshot.py --verify /secure/new-complete-bundle
```

After privately transferring the bundle to the future private runner, create
a **non-Git** workspace containing the audited application code but **no
`data/` directory** (and no `.git` anywhere in its ancestor chain). Then:

```bash
python scripts/private_data_snapshot.py --import-from /secure/new-complete-bundle --workspace /secure/clean-application
```

The private runner must verify file hashes and execute full real knowledge,
API and product tests against the imported data before public code-only CI is
enabled. This repository's public CI exercises an **actual full-tree local
export/import roundtrip**, but does not access or attest a private repository.

Do not upload this bundle to public GitHub, public Actions artifacts,
public build logs, a frontend static directory or an accessible object-store
URL. No private remote was created by this change, and the preexisting
public Git history remains readable.


## Offline private backend assembly (batch 177)

The `scripts/assemble_private_backend.py` command constructs a new backend
workspace **outside all Git checkouts**. It copies only audited code directories
(`config`, `src`, `scripts`, `tests`, `schemas`, `evals` and
`pyproject.toml`) from the checkout, and obtains the complete `data/`
directory **exclusively from a verified v2 snapshot**. It refuses preexisting
destination paths, symlinks, unsafe source files and Git workspaces. No
`.git`, public-checkout data folder, private token or static web distribution
is copied into the assembled backend.

After transferring a confidential snapshot into your future private runner:

```bash
python scripts/assemble_private_backend.py \
  --snapshot /secure/new-complete-bundle \
  --destination /secure/new-backend
cd /secure/new-backend
PYTHONPATH=src python scripts/validate_kb.py
```

The public consumer CI runs the same local assembly against **real current
knowledge assets** and invokes the actual canonical validator from inside the
isolated backend. This is a packaging proof only; real private storage, private
CI authentication, full regression and deployment have not occurred.
