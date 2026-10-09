"""Fail-closed public GitHub Actions boundary for knowledge-content automation.

This guard does NOT remove historic public data or grant trust to the runner.
It stops accidental raw knowledge refreshes in this repository's public CI.
"""
from __future__ import annotations

import os
from pathlib import Path
import subprocess

PUBLIC_REPOSITORY = "hellomrduan/tianji-knowledge-base"
METADATA_ONLY_PATHS = frozenset({"data/state/source_state.json"})


def refuse_public_knowledge_write(environ=None) -> None:
    env = os.environ if environ is None else environ
    if (str(env.get("GITHUB_ACTIONS", "")).lower() == "true"
            and str(env.get("GITHUB_REPOSITORY", "")).lower() == PUBLIC_REPOSITORY):
        raise RuntimeError(
            "Public automated knowledge content writes are disabled; "
            "run ingestion only in provisioned private infrastructure."
        )


def validate_metadata_only_paths(paths) -> tuple[str, ...]:
    names = tuple(paths)
    if any(not isinstance(name, str) or name not in METADATA_ONLY_PATHS for name in names):
        raise ValueError("Refusing to commit non-metadata files in public sync")
    if len(names) != len(set(names)):
        raise ValueError("Duplicated staged metadata paths")
    return names


def main() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    raw = subprocess.check_output(
        ["git", "diff", "--cached", "--name-only", "-z"], cwd=repo_root,
    )
    paths = [os.fsdecode(path) for path in raw.split(b"\0") if path]
    validate_metadata_only_paths(paths)
    print(f"Public automation staged metadata-only files: {len(paths)}")


if __name__ == "__main__":
    main()
