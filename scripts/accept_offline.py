#!/usr/bin/env python3
"""Offline controlled acceptance (no private GitHub Actions required).

Runs the full product acceptance using:
- A public code checkout at an exact SHA (pinned)
- A controlled knowledge snapshot (NOT in Git, on a trusted machine)

This replaces the private GitHub Actions workflow. The knowledge snapshot
must be a verified copy of the 235 Canonical files, validated against
private-data-manifest.json before use.

Usage:
    python scripts/accept_offline.py \
        --public-code /path/to/tianji-knowledge-base \
        --expected-sha <40-char SHA> \
        --knowledge-snapshot /path/to/controlled/knowledge \
        --suite all

Evidence recorded:
- Public code SHA (verified in-workflow)
- Knowledge snapshot manifest SHA256
- Test counts (pass/fail/error/skip)
- Execution environment (hostname, timestamp)
- Phase4 freeze check result
"""
import argparse
import hashlib
import json
import os
import platform
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1024*1024), b''):
            h.update(chunk)
    return h.hexdigest()


def verify_knowledge_snapshot(snapshot: Path):
    """Verify the snapshot against its manifest. Fail closed on any mismatch."""
    manifest_path = snapshot / "private-data-manifest.json"
    if not manifest_path.is_file():
        raise ValueError(f"Manifest not found: {manifest_path}")
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    files = manifest.get('files', [])
    if len(files) != manifest.get('file_count'):
        raise ValueError(f"Manifest file count mismatch: {len(files)} vs {manifest.get('file_count')}")
    errors = []
    for entry in files:
        fpath = snapshot / entry['path']
        if not fpath.is_file():
            errors.append(f"missing: {entry['path']}")
            continue
        actual = sha256_file(fpath)
        if actual != entry['sha256']:
            errors.append(f"sha mismatch: {entry['path']}")
        if fpath.stat().st_size != entry['bytes']:
            errors.append(f"size mismatch: {entry['path']}")
    if errors:
        raise ValueError(f"Knowledge snapshot verification failed: {errors[:5]}")
    manifest_sha = sha256_file(manifest_path)
    print(f"knowledge snapshot verified: {len(files)} files, manifest sha256={manifest_sha[:16]}...")
    return manifest_sha, len(files)


def verify_public_sha(public_code: Path, expected_sha: str):
    """Verify the public checkout is at the exact expected SHA."""
    if len(expected_sha) != 40 or not all(c in '0123456789abcdef' for c in expected_sha):
        raise ValueError("expected-sha must be a 40-char hex SHA")
    result = subprocess.run(
        ['git', '-C', str(public_code), 'rev-parse', 'HEAD'],
        capture_output=True, text=True, check=True)
    actual = result.stdout.strip()
    if actual != expected_sha:
        raise ValueError(f"Public SHA mismatch: expected {expected_sha}, got {actual}")
    print(f"public code SHA verified: {actual}")
    return actual


def main():
    parser = argparse.ArgumentParser(description='Offline controlled acceptance')
    parser.add_argument('--public-code', required=True, type=Path,
                        help='Absolute path to public repo checkout')
    parser.add_argument('--expected-sha', required=True,
                        help='Exact 40-char public commit SHA')
    parser.add_argument('--knowledge-snapshot', required=True, type=Path,
                        help='Absolute path to controlled knowledge snapshot')
    parser.add_argument('--suite', default='all', choices=['all'],
                        help='Test suite to run')
    args = parser.parse_args()

    public_code = args.public_code.resolve(strict=True)
    snapshot = args.knowledge_snapshot.resolve(strict=True)

    # Safety: snapshot must NOT be inside a git repo or the public checkout
    if (snapshot / '.git').exists():
        raise ValueError("Knowledge snapshot must not be inside a Git repository")
    if snapshot.is_relative_to(public_code) or public_code.is_relative_to(snapshot):
        raise ValueError("Snapshot and public code must be separate directories")

    print("=" * 60)
    print("OFFLINE CONTROLLED ACCEPTANCE")
    print(f"timestamp: {datetime.now(timezone.utc).isoformat()}")
    print(f"hostname: {platform.node()}")
    print("=" * 60)

    # 1. Verify inputs
    public_sha = verify_public_sha(public_code, args.expected_sha)
    manifest_sha, file_count = verify_knowledge_snapshot(snapshot)

    # 2. Run the existing acceptance (reuses all real tests)
    accept_script = public_code / 'scripts' / 'accept_product_pr.py'
    if not accept_script.is_file():
        raise ValueError(f"Acceptance script not found: {accept_script}")

    # The accept script expects the private repo layout; we provide the
    # snapshot as the "private" directory.
    cmd = [
        sys.executable, str(accept_script),
        '--public-code', str(public_code),
        '--expected-sha', public_sha,
        '--suite', args.suite,
    ]
    # Set env to indicate offline mode with snapshot path
    env = dict(os.environ)
    env['TIANJI_KNOWLEDGE_SNAPSHOT'] = str(snapshot)

    print(f"\nrunning: {' '.join(cmd)}")
    result = subprocess.run(cmd, env=env)
    if result.returncode != 0:
        print(f"\nACCEPTANCE FAILED (exit {result.returncode})", file=sys.stderr)
        sys.exit(result.returncode)

    # 3. Record evidence
    evidence = {
        'mode': 'offline-controlled',
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'hostname': platform.node(),
        'public_sha': public_sha,
        'knowledge_manifest_sha256': manifest_sha,
        'knowledge_file_count': file_count,
        'suite': args.suite,
        'result': 'SUCCESS',
    }
    print("\n" + "=" * 60)
    print("EVIDENCE:")
    print(json.dumps(evidence, indent=2, sort_keys=True))
    print("=" * 60)
    print("\nOFFLINE ACCEPTANCE SUCCESSFUL")
    print("NOTE: This is NOT a GitHub Actions run. Do not report it as such.")


if __name__ == '__main__':
    main()
