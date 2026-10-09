"""Audit public data exposure and reject *new* knowledge payload changes.

Inventory reads tracked file metadata, not text contents. A PR gate can block
new protected data modifications, but cannot undo publication or stop direct
pushes to an unprotected branch.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
import json
import os
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
PUBLIC_METADATA_ALLOWLIST = frozenset({
    "data/state/source_state.json",
    "data/registry/discovered_candidates.json",
})
CONFIDENTIAL_CANDIDATE_AREAS = frozenset({
    "canonical", "quarantine", "index", "product", "upstream",
    "reference", "research", "audit", "coverage",
})


def _git(*args: str, root: Path = ROOT) -> bytes:
    return subprocess.check_output(["git", *args], cwd=root)


def inventory(root: Path = ROOT) -> dict:
    """Inventory only tracked data files (paths/counts/byte sizes)."""
    areas: dict[str, dict] = defaultdict(lambda: {"files": 0, "bytes": 0})
    paths = [os.fsdecode(x) for x in _git("ls-files", "-z", "--", "data/", root=root).split(b"\0") if x]
    for rel in paths:
        file = root / rel
        if not file.is_file() or file.is_symlink():
            raise ValueError(f"Unsafe or missing tracked data node: {rel}")
        parts = rel.split("/")
        area = parts[1] if len(parts) >= 3 else "unclassified"
        areas[area]["files"] += 1
        areas[area]["bytes"] += file.stat().st_size
    summary = {
        "schema": "public-data-surface-v1",
        "repository_visibility": "public-assumed-not-attested",
        "tracked_files": len(paths),
        "tracked_bytes": sum(row["bytes"] for row in areas.values()),
        "areas": {
            key: {**value, "classification": (
                "review-content-before-publication" if key in CONFIDENTIAL_CANDIDATE_AREAS
                else "metadata-needs-review" if key in {"state", "registry"}
                else "unclassified-fail-closed"
            )}
            for key, value in sorted(areas.items())
        },
    }
    return summary


def check_change_rows(rows: list[tuple[str, str]]) -> list[str]:
    """D is permitted for migration; public content A/M/T/U is not permitted."""
    violations = []
    for status, path in rows:
        if not isinstance(status, str) or not isinstance(path, str):
            raise ValueError("Invalid git change row")
        if not path.startswith("data/"):
            continue
        if status == "D":
            continue
        if path in PUBLIC_METADATA_ALLOWLIST and status in {"A", "M"}:
            continue
        violations.append(f"{status} {path}")
    return violations


def diff_rows(base: str, root: Path = ROOT) -> list[tuple[str, str]]:
    if not base or base.startswith("-") or not all(c in "0123456789abcdefABCDEF" for c in base):
        raise ValueError("Expected a commit SHA as base")
    raw = _git("diff", "--name-status", "--no-renames", "-z", base, "HEAD", root=root)
    parts = raw.split(b"\0")
    if parts[-1] != b"":
        raise ValueError("Incomplete git diff output")
    parts.pop()
    if len(parts) % 2:
        raise ValueError("Invalid git diff name-status encoding")
    return [(os.fsdecode(parts[i]), os.fsdecode(parts[i + 1]))
            for i in range(0, len(parts), 2)]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--inventory", action="store_true", help="Counts/bytes only; never print file contents")
    parser.add_argument("--base", help="Commit SHA to compare with HEAD; block new public data payloads")
    args = parser.parse_args()
    if args.inventory:
        print(json.dumps(inventory(), ensure_ascii=False, sort_keys=True))
    if args.base:
        rows = diff_rows(args.base)
        bad = check_change_rows(rows)
        if bad:
            print("BLOCKED: new knowledge-like files must go to a private repository:")
            for entry in bad:
                print("  " + entry)
            raise SystemExit(2)
        print(f"Public data change gate passed: {len(rows)} changed files inspected")
    if not args.inventory and not args.base:
        parser.error("Supply --inventory and/or --base")


if __name__ == "__main__":
    main()
