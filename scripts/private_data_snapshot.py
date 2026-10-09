"""Create and verify an *entire* private data snapshot, not merely canonical/quarantine.

V2 preserves every file from the reviewed data areas, including derived indexes,
product knowledge, upstream source text and provenance. It does not publish or
upload the resulting snapshot and cannot erase public Git history.
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

ROOT = Path(__file__).resolve().parents[1]
AREAS = (
    "audit", "canonical", "coverage", "index", "product", "quarantine",
    "reference", "registry", "research", "state", "upstream",
)
MANIFEST = "private-data-manifest.json"
SCHEMA = "private-data-snapshot-v2"
DIGEST = re.compile(r"[0-9a-f]{64}\Z")


def _hash(path: Path) -> str:
    sha = hashlib.sha256()
    with path.open("rb") as reader:
        for chunk in iter(lambda: reader.read(1024 * 1024), b""):
            sha.update(chunk)
    return sha.hexdigest()


def _safe_relative(value: object) -> str:
    if not isinstance(value, str) or not value or "\\" in value or "\x00" in value:
        raise ValueError("Unsafe data snapshot path")
    parts = value.split("/")
    if (len(parts) < 3 or parts[0] != "data" or parts[1] not in AREAS
            or any(p in ("", ".", "..") for p in parts)
            or PurePosixPath(value).as_posix() != value):
        raise ValueError("Unsafe data snapshot path")
    return value


def _scan_data(root: Path) -> list[dict]:
    data_root = root / "data"
    if data_root.is_symlink() or not data_root.is_dir():
        raise ValueError("Missing or unsafe data directory")
    if {p.name for p in data_root.iterdir()} != set(AREAS):
        raise ValueError("Unexpected or missing data areas: full snapshot required")

    result = []
    for area in AREAS:
        source = data_root / area
        if source.is_symlink() or not source.is_dir():
            raise ValueError("Unsafe data area")
        found = 0
        for current, directories, files in os.walk(source, followlinks=False):
            directory = Path(current)
            for name in directories:
                node = directory / name
                if node.is_symlink() or not node.is_dir():
                    raise ValueError("Unsafe data directory node")
            for name in sorted(files):
                node = directory / name
                if node.is_symlink() or not node.is_file():
                    raise ValueError("Unsafe data file node")
                rel = _safe_relative(node.relative_to(root).as_posix())
                result.append({"path": rel, "bytes": node.stat().st_size,
                               "sha256": _hash(node)})
                found += 1
        if not found:
            raise ValueError("Snapshot omitted a required data area")
    return sorted(result, key=lambda row: row["path"])


def export_private_data(root: Path, destination: Path) -> dict:
    if not root.is_dir():
        raise ValueError("Expected a source directory")
    root = root.resolve(strict=True)
    if not destination.is_absolute() or destination.exists() or destination.is_symlink():
        raise ValueError("Expected an absolute, new export destination")
    parent = destination.parent.resolve(strict=True)
    destination = parent / destination.name
    if destination.is_relative_to(root) or root.is_relative_to(destination):
        raise ValueError("Private export must be outside the public checkout")

    rows = _scan_data(root)
    manifest = {
        "schema_version": SCHEMA, "areas": list(AREAS),
        "file_count": len(rows),
        "total_bytes": sum(row["bytes"] for row in rows),
        "files": rows,
        "warning": "Confidential copy only; existing public Git history is unchanged",
    }

    destination.mkdir(mode=0o700, exist_ok=False)
    try:
        destination.chmod(0o700)
        for row in rows:
            source = root / row["path"]
            target = destination / row["path"]
            target.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
            target.parent.chmod(0o700)
            sha = hashlib.sha256()
            count = 0
            with source.open("rb") as reader, target.open("xb") as writer:
                while chunk := reader.read(1024 * 1024):
                    writer.write(chunk)
                    sha.update(chunk)
                    count += len(chunk)
            target.chmod(0o600)
            if count != row["bytes"] or sha.hexdigest() != row["sha256"]:
                raise ValueError("Source changed during export")
        path = destination / MANIFEST
        with path.open("x", encoding="utf-8") as handle:
            json.dump(manifest, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
        path.chmod(0o600)
    except Exception:
        shutil.rmtree(destination)
        raise
    return manifest


def verify_private_data(source: Path) -> dict:
    if not source.is_absolute() or source.is_symlink():
        raise ValueError("Private snapshot must be an absolute real directory")
    source = source.resolve(strict=True)
    if not source.is_dir() or {p.name for p in source.iterdir()} != {"data", MANIFEST}:
        raise ValueError("Unexpected private snapshot root contents")
    manifest_path = source / MANIFEST
    if manifest_path.is_symlink() or not manifest_path.is_file():
        raise ValueError("Missing or unsafe snapshot manifest")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if not isinstance(manifest, dict) or manifest.get("schema_version") != SCHEMA:
        raise ValueError("Unsupported data snapshot schema")
    if manifest.get("areas") != list(AREAS):
        raise ValueError("Incomplete declared data areas")
    rows = manifest.get("files")
    if not isinstance(rows, list) or not rows:
        raise ValueError("Empty private snapshot manifest")
    expected = {}
    for row in rows:
        if not isinstance(row, dict):
            raise ValueError("Invalid manifest entry")
        rel = _safe_relative(row.get("path"))
        size, sha = row.get("bytes"), row.get("sha256")
        if (rel in expected or type(size) is not int or size < 0
                or not isinstance(sha, str) or not DIGEST.fullmatch(sha)):
            raise ValueError("Duplicate or invalid data manifest entry")
        expected[rel] = (size, sha)
    if (type(manifest.get("file_count")) is not int
            or manifest["file_count"] != len(expected)
            or type(manifest.get("total_bytes")) is not int
            or manifest["total_bytes"] != sum(size for size, _ in expected.values())):
        raise ValueError("Data snapshot manifest totals mismatch")
    if not all(any(p.startswith(f"data/{area}/") for p in expected) for area in AREAS):
        raise ValueError("Incomplete snapshot area coverage")
    real_rows = _scan_data(source)
    if set(row["path"] for row in real_rows) != set(expected):
        raise ValueError("Snapshot contains undeclared or missing files")
    for row in real_rows:
        if (row["bytes"], row["sha256"]) != expected[row["path"]]:
            raise ValueError("Private data SHA256 or size mismatch")
    return manifest


def stage_private_data(source: Path, workspace: Path) -> dict:
    """Import create-only into a clean non-Git application workspace."""
    manifest = verify_private_data(source)
    source = source.resolve(strict=True)
    if not workspace.is_absolute() or workspace.is_symlink() or not workspace.is_dir():
        raise ValueError("Workspace must be an absolute, real directory")
    workspace = workspace.resolve(strict=True)
    if workspace.is_relative_to(source) or source.is_relative_to(workspace):
        raise ValueError("Private snapshot and workspace must be separate")
    if any((parent / ".git").exists() or (parent / ".git").is_symlink()
           for parent in (workspace, *workspace.parents)):
        raise ValueError("Private data must never be imported into a Git checkout")
    destination = workspace / "data"
    if destination.exists() or destination.is_symlink():
        raise ValueError("Destination already contains data; public fallback rejected")

    stage = Path(tempfile.mkdtemp(prefix=".private-data-", dir=workspace))
    try:
        stage.chmod(0o700)
        data = stage / "data"
        data.mkdir(mode=0o700)
        for row in manifest["files"]:
            source_path = source / row["path"]
            target = stage / row["path"]
            target.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
            target.parent.chmod(0o700)
            with source_path.open("rb") as reader, target.open("xb") as writer:
                while chunk := reader.read(1024 * 1024):
                    writer.write(chunk)
            target.chmod(0o600)
            if target.stat().st_size != row["bytes"] or _hash(target) != row["sha256"]:
                raise ValueError("Snapshot changed during import")
        for area in AREAS:
            (data / area).mkdir(parents=True, exist_ok=True, mode=0o700)
        if destination.exists() or destination.is_symlink():
            raise ValueError("Destination appeared during import")
        data.rename(destination)
    finally:
        shutil.rmtree(stage, ignore_errors=True)
    return {"file_count": manifest["file_count"], "total_bytes": manifest["total_bytes"]}


def main() -> None:
    parser = argparse.ArgumentParser(description="Full private data snapshot: export/verify/import")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--export", type=Path, help="New absolute restricted export destination")
    group.add_argument("--verify", type=Path, help="Existing private snapshot")
    group.add_argument("--import-from", type=Path, help="Private snapshot to import")
    parser.add_argument("--workspace", type=Path, help="Required for --import-from; must not be a Git checkout")
    args = parser.parse_args()
    if args.export:
        result = export_private_data(ROOT, args.export)
    elif args.verify:
        result = verify_private_data(args.verify)
    else:
        if not args.workspace:
            parser.error("--workspace is required with --import-from")
        result = stage_private_data(args.import_from, args.workspace)
    print(json.dumps({"schema_version": SCHEMA,
                      "file_count": result["file_count"],
                      "total_bytes": result["total_bytes"]}))


if __name__ == "__main__":
    main()
