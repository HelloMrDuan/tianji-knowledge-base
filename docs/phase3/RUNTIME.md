# Production runtime

Phase 3 starts at remote main `58f065f`. Phase 2 evidence was filtered before output, but resolver startup still read quarantine for provenance checks. Production now reads an explicitly built reviewed snapshot.

Build with `PYTHONPATH=src python scripts/build_production_runtime.py`. This offline review command verifies source checksums, quotations, schemas and source independence without changing Canonical or source grades. It may read quarantine for auditing; serving requests never invokes it.

`build/production_runtime.json` contains registered Canonical entities, execution contracts, reviewed excerpt records and source metadata, not quarantine bodies or implementation source code. Runtime checks the artifact digest and hashes of Canonical/config/schema/code release inputs. Missing, changed or damaged artifacts fail closed and require an explicit rebuild. The snapshot is a repository release artifact, not a cryptographic signature from an external authority.

Production EvidenceResolver resolves reviewed quotations directly from the snapshot. Source `content_path` may retain a quarantine location as audit provenance; it is not an instruction to load that file. Research calculations continue to require the explicit existing engine gate and cannot promote unreviewed content.
