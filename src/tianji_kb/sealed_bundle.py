"""Build a source-free, server-only runtime bundle from an audited checkout.

The output contains reviewed knowledge in derived form: it is confidential
server material, NOT a public frontend artifact or a substitute for a private
source repository. Do not commit or deploy it under a static web root.
"""
from __future__ import annotations

import hashlib
import os
from pathlib import Path

from .runtime_catalog import load_catalog


ARTIFACTS = ('production_runtime.json', 'production_rag.jsonl')


def export_sealed_bundle(source_root: Path, destination: Path) -> dict[str, str]:
    source_root = Path(source_root).resolve()
    destination = Path(destination).resolve()
    # Prevent accidental publication into the public repo, and never overwrite
    # an existing destination (including a previous deploy's trusted bundle).
    if destination == source_root or destination.is_relative_to(source_root):
        raise ValueError('Sealed bundles must be exported outside the repository')
    if destination.exists():
        raise ValueError('Sealed bundle destination must not already exist')
    # Source mode verifies every audited Canonical/config/schema/code checksum.
    if os.environ.get('TIANJI_RUNTIME_MODE', 'source-verified') != 'source-verified':
        raise ValueError('Sealed bundle export requires the source-verified build environment')
    payload = load_catalog(source_root)
    source_files = [source_root/'build'/name for name in ARTIFACTS]
    if hashlib.sha256(source_files[1].read_bytes()).hexdigest() != payload['retrieval_index_sha256']:
        raise ValueError('Reviewed RAG artifact does not match the audited runtime')
    destination.mkdir(mode=0o700, parents=True, exist_ok=False)
    output = destination/'build'
    output.mkdir(mode=0o700)
    hashes = {}
    for src in source_files:
        data = src.read_bytes()
        dest = output/src.name
        with dest.open('xb') as handle:
            handle.write(data)
        dest.chmod(0o600)
        hashes[src.name] = hashlib.sha256(data).hexdigest()
    return hashes
