"""Assemble private backend code and verified private data without Git or public fallback.

Run by a trusted PRIVATE runner only after the complete snapshot was transferred
to restricted storage. The public CI exercises the *same assembly* with real
repository data but cannot attest a remote private repository.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shutil
import tempfile

from scripts.private_data_snapshot import stage_private_data, verify_private_data

CODE_DIRECTORIES = ("config", "src", "scripts", "tests", "schemas", "evals", "docs")
CODE_FILES = ("pyproject.toml",)
EXCLUDED_CACHE_DIRECTORIES = frozenset({
    "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache",
    ".cache", "node_modules", "dist", "build", ".venv",
})


def _copy_code(checkout: Path, output: Path) -> int:
    count = 0
    for relative in CODE_DIRECTORIES:
        source = checkout / relative
        if not source.is_dir() or source.is_symlink():
            raise ValueError("Missing or unsafe application code directory: " + relative)
        destination = output / relative
        destination.mkdir(mode=0o700)
        for current, folders, files in os.walk(source, followlinks=False):
            directory = Path(current)
            folders.sort()
            for folder in list(folders):
                src_dir = directory / folder
                if src_dir.is_symlink():
                    raise ValueError("Application code symlink directory rejected")
                if folder in EXCLUDED_CACHE_DIRECTORIES:
                    folders.remove(folder)
            target_dir = destination / directory.relative_to(source)
            target_dir.mkdir(parents=True, exist_ok=True, mode=0o700)
            target_dir.chmod(0o700)
            for file in sorted(files):
                node = directory / file
                if node.is_symlink() or not node.is_file():
                    raise ValueError("Unsafe application code file")
                if (file.startswith(".env") or file.endswith((".pyc", ".pyo"))
                        or file in (".DS_Store",)):
                    raise ValueError("Secret or generated file in application source")
                target = target_dir / file
                with node.open("rb") as reader, target.open("xb") as writer:
                    shutil.copyfileobj(reader, writer, length=1024 * 1024)
                target.chmod(0o600)
                count += 1
    for rel in CODE_FILES:
        source = checkout / rel
        if source.is_symlink() or not source.is_file():
            raise ValueError("Missing or unsafe code file: " + rel)
        target = output / rel
        with source.open("rb") as reader, target.open("xb") as writer:
            shutil.copyfileobj(reader, writer, length=1024 * 1024)
        target.chmod(0o600)
        count += 1
    return count


def assemble_private_backend(checkout: Path, snapshot: Path, destination: Path) -> dict:
    """Create-only staging: code only from checkout, all data only from snapshot."""
    if not checkout.is_dir() or checkout.is_symlink():
        raise ValueError("Source checkout must be a real directory")
    checkout = checkout.resolve(strict=True)
    snapshot = snapshot.resolve(strict=True)
    manifest = verify_private_data(snapshot)
    if not destination.is_absolute() or destination.exists() or destination.is_symlink():
        raise ValueError("Destination must be absolute and must not exist")
    parent = destination.parent.resolve(strict=True)
    destination = parent / destination.name
    if (destination.is_relative_to(checkout) or checkout.is_relative_to(destination)
            or destination.is_relative_to(snapshot) or snapshot.is_relative_to(destination)):
        raise ValueError("Output, code checkout and private snapshot must be separated")
    if any((ancestor / ".git").exists() or (ancestor / ".git").is_symlink()
           for ancestor in (parent, *parent.parents)):
        raise ValueError("Cannot assemble private data inside a Git checkout")

    stage = Path(tempfile.mkdtemp(prefix=".private-backend-", dir=parent))
    try:
        stage.chmod(0o700)
        copied_code = _copy_code(checkout, stage)
        imported = stage_private_data(snapshot, stage)
        if imported["file_count"] != manifest["file_count"]:
            raise ValueError("Incomplete imported private knowledge")
        if (stage / ".git").exists() or not (stage / "data").is_dir():
            raise ValueError("Unsafe assembled private backend")
        if destination.exists() or destination.is_symlink():
            raise ValueError("Private backend destination changed during assembly")
        stage.rename(destination)
    except Exception:
        shutil.rmtree(stage, ignore_errors=True)
        raise
    return {"code_files": copied_code,
            "knowledge_files": imported["file_count"],
            "knowledge_bytes": imported["total_bytes"]}


def main() -> None:
    parser = argparse.ArgumentParser(description="Assemble an isolated private backend workspace")
    parser.add_argument("--snapshot", type=Path, required=True)
    parser.add_argument("--destination", type=Path, required=True)
    args = parser.parse_args()
    result = assemble_private_backend(Path(__file__).resolve().parents[1],
                                      args.snapshot, args.destination)
    print(json.dumps(result))


if __name__ == "__main__":
    main()
