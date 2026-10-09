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
