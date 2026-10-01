"""Explicit, versioned RAW acquisition and metadata-only review candidates."""
from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path


def git_blob_sha(content: bytes) -> str:
    return hashlib.sha1(f'blob {len(content)}\0'.encode() + content).hexdigest()


def stage_candidate(root: Path, source: dict, commit: str, content: bytes,
                    upstream_blob: str, baseline_blob: str | None = None) -> dict:
    sid = source['source_id']
    if not re.fullmatch(r'[a-z][a-z0-9_.-]*', sid) or not re.fullmatch(r'[0-9a-f]{40}', commit):
        raise ValueError('Invalid source ID or commit')
    classical = source['kind'] == 'classical' and source['public_domain']
    implementation = source['kind'] == 'implementation' and source['license'] == 'MIT'
    if not (classical or implementation):
        raise ValueError('Source lacks approved acquisition rights')
    actual_blob = git_blob_sha(content)
    expected = source.get('blob_sha') if commit == source['commit'] else None
    if actual_blob != upstream_blob or (expected and actual_blob != expected):
        raise ValueError('Upstream blob checksum mismatch')
    content.decode('utf-8')  # Do not normalize bytes before verifying the Git blob.
    raw = root / 'data/raw/phase1_candidates' / sid / commit / f'{actual_blob}.raw'
    candidate = root / 'data/quarantine/phase1_candidates' / sid / commit / f'{actual_blob}.json'
    for path in (raw, candidate):
        if not path.resolve().is_relative_to(root.resolve()):
            raise ValueError('Candidate path escapes repository')
    if candidate.exists():
        old = json.loads(candidate.read_text())
        if not raw.exists() or raw.read_bytes() != content:
            raise ValueError('Existing candidate RAW bytes drifted or are missing')
        return old
    raw.parent.mkdir(parents=True, exist_ok=True)
    raw.write_bytes(content)
    metadata = {
        'source_id': sid, 'repository': source['repository'], 'source_path': source['path'],
        'pinned_commit': source['commit'], 'candidate_commit': commit,
        'baseline_blob_sha': baseline_blob or source.get('blob_sha'), 'blob_sha': actual_blob,
        'sha256': hashlib.sha256(content).hexdigest(), 'bytes': len(content),
        'raw_path': raw.relative_to(root).as_posix(),
        'stage': 'quarantine', 'evidence_level': 'D', 'review_status': 'pending',
        'promotion_allowed': False, 'body_saved_to_quarantine': False,
        'file_changed': (baseline_blob or source.get('blob_sha')) != actual_blob if (baseline_blob or source.get('blob_sha')) else None,
        'rights_scope': source['rights_basis'],
        'rights_status': 'requires_review_at_new_commit' if commit != source['commit'] else 'approved_acquisition_scope_only',
        'retrieved_at': datetime.now(timezone.utc).isoformat(),
        'review_note': 'RAW 忽略缓存；这里只存来源与差异元数据。正文、版权、异文均须另开审核 PR；不写 Canonical 或已审核证据。',
    }
    candidate.parent.mkdir(parents=True, exist_ok=True)
    candidate.write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + '\n')
    return metadata
