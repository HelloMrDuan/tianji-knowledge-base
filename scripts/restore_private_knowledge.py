"""Verify and stage a restricted knowledge export in a clean, non-Git workspace.

Designed for a future PRIVATE CI runner. Never downloads assets, invokes
GitHub credentials, or permits fallback to data already in a public checkout.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import tempfile

from scripts.export_private_knowledge import SOURCE_DIRS

MANIFEST_NAME = "private-export-manifest.json"
DIGEST_PATTERN = re.compile(r"[0-9a-f]{64}\Z")


def _digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as reader:
        for chunk in iter(lambda: reader.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _relative_file(value: object) -> str:
    if not isinstance(value, str) or not value or "\\" in value:
        raise ValueError("Unsafe manifest file path")
    path = PurePosixPath(value)
    if (path.is_absolute() or str(path) != value
            or any(part in ("", ".", "..") for part in value.split("/"))
            or len(path.parts) < 3
            or "/".join(path.parts[:2]) not in SOURCE_DIRS):
        raise ValueError("Unsafe manifest file path")
    return value


def verify_private_export(source: Path) -> dict:
    """Verify exact membership, size and SHA256 before trusting any content."""
    if not source.is_absolute() or source.is_symlink():
        raise ValueError("Private source must be an absolute, real directory")
    source = source.resolve(strict=True)
    if not source.is_dir():
        raise ValueError("Private source must be a directory")
    manifest_path = source / MANIFEST_NAME
    if manifest_path.is_symlink() or not manifest_path.is_file():
        raise ValueError("Missing or unsafe private export manifest")
    data_root = source / "data"
    if data_root.is_symlink() or not data_root.is_dir():
        raise ValueError("Missing or unsafe private data directory")
    if {p.name for p in source.iterdir()} != {"data", MANIFEST_NAME}:
        raise ValueError("Unexpected private export root contents")
    if {p.name for p in data_root.iterdir()} != {area.split("/")[1] for area in SOURCE_DIRS}:
        raise ValueError("Unexpected private data directories")

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if not isinstance(manifest, dict) or manifest.get("schema_version") != "private-knowledge-export-v1":
        raise ValueError("Unsupported private export manifest")
    if manifest.get("contains") != list(SOURCE_DIRS):
        raise ValueError("Private export must contain both knowledge areas")
    rows = manifest.get("files")
    if not isinstance(rows, list) or not rows:
        raise ValueError("Private manifest has no files")

    expected = {}
    for row in rows:
        if not isinstance(row, dict):
            raise ValueError("Malformed manifest entry")
        rel = _relative_file(row.get("path"))
        size, sha = row.get("bytes"), row.get("sha256")
        if (rel in expected or type(size) is not int or size < 0
                or not isinstance(sha, str) or not DIGEST_PATTERN.fullmatch(sha)):
            raise ValueError("Invalid, duplicated, or unverified manifest entry")
        expected[rel] = (size, sha)

    if any(not any(path.startswith(area + "/") for path in expected) for area in SOURCE_DIRS):
        raise ValueError("Private manifest omitted a knowledge area")
    if (type(manifest.get("file_count")) is not int or manifest["file_count"] != len(expected)
            or type(manifest.get("total_bytes")) is not int
            or manifest["total_bytes"] != sum(row[0] for row in expected.values())):
        raise ValueError("Private manifest totals do not match")

    observed = set()
    for area in SOURCE_DIRS:
        root = source / area
        if root.is_symlink() or not root.is_dir():
            raise ValueError("Unsafe private knowledge directory")
        for dir_name, dirs, files in os.walk(root, followlinks=False):
            folder = Path(dir_name)
            for name in dirs:
                if (folder / name).is_symlink():
                    raise ValueError("Private knowledge symlink directory rejected")
            for name in files:
                item = folder / name
                if item.is_symlink() or not item.is_file():
                    raise ValueError("Private knowledge symlink or special file rejected")
                rel = item.relative_to(source).as_posix()
                observed.add(rel)
                if rel not in expected:
                    raise ValueError("Unmanifested private knowledge file")
                size, sha = expected[rel]
                if item.stat().st_size != size or _digest(item) != sha:
                    raise ValueError("Private knowledge SHA256/size mismatch")
    if observed != set(expected):
        raise ValueError("Private knowledge export is incomplete")
    return manifest


def stage_private_knowledge(source: Path, workspace: Path) -> dict:
    """Create-only import into an empty knowledge area of an untracked workspace.

    The workspace must have NO .git ancestor and NO existing knowledge dirs:
    a tracked public checkout or a partial previous import is never accepted.
    """
    manifest = verify_private_export(source)
    source = source.resolve(strict=True)
    if not workspace.is_absolute() or workspace.is_symlink():
        raise ValueError("Workspace must be an absolute, real directory")
    workspace = workspace.resolve(strict=True)
    if not workspace.is_dir():
        raise ValueError("Workspace must be a directory")
    if workspace.is_relative_to(source) or source.is_relative_to(workspace):
        raise ValueError("Workspace and private source must be separate")
    if any((ancestor / ".git").exists() or (ancestor / ".git").is_symlink()
           for ancestor in (workspace, *workspace.parents)):
        raise ValueError("Private assets must never be staged inside a Git checkout")

    data_dir = workspace / "data"
    if data_dir.is_symlink() or (data_dir.exists() and not data_dir.is_dir()):
        raise ValueError("Unsafe target data directory")
    for area in SOURCE_DIRS:
        target = workspace / area
        if target.exists() or target.is_symlink():
            raise ValueError("Knowledge destination is not empty (public fallback denied)")

    # Copy into an isolated temporary tree; publish neither area until every
    # output file has been rechecked. If an install fails, roll back both areas.
    stage_root = Path(tempfile.mkdtemp(prefix=".private-knowledge-stage-", dir=workspace))
    installed = []
    try:
        stage_root.chmod(0o700)
        for row in manifest["files"]:
            relative = Path(row["path"])
            src = source / relative
            target = stage_root / relative
            target.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
            target.parent.chmod(0o700)
            with src.open("rb") as reader, target.open("xb") as writer:
                while chunk := reader.read(1024 * 1024):
                    writer.write(chunk)
            target.chmod(0o600)
            if target.stat().st_size != row["bytes"] or _digest(target) != row["sha256"]:
                raise ValueError("Private knowledge source changed during import")

        data_dir.mkdir(mode=0o700, exist_ok=True)
        for area in SOURCE_DIRS:
            target = workspace / area
            if target.exists() or target.is_symlink():
                raise ValueError("Knowledge destination changed during import")
            (stage_root / area).rename(target)
            installed.append(target)
    except Exception:
        for target in installed:
            shutil.rmtree(target)
        raise
    finally:
        shutil.rmtree(stage_root, ignore_errors=True)

    return {"file_count": manifest["file_count"], "total_bytes": manifest["total_bytes"]}


def main() -> None:
    parser = argparse.ArgumentParser(description="Verify or create-only stage private knowledge")
    parser.add_argument("--source", type=Path, required=True, help="Absolute private export path")
    parser.add_argument("--workspace", type=Path, help="Clean non-Git workspace (required to stage)")
    parser.add_argument("--verify-only", action="store_true")
    args = parser.parse_args()
    if args.verify_only:
        manifest = verify_private_export(args.source)
        result = {"verified": True, "file_count": manifest["file_count"],
                  "total_bytes": manifest["total_bytes"]}
    else:
        if args.workspace is None:
            parser.error("--workspace is required unless --verify-only is used")
        result = stage_private_knowledge(args.source, args.workspace)
        result["staged"] = True
    print(json.dumps(result))


if __name__ == "__main__":
    main()
