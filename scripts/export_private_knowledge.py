"""Export an auditable private copy of approved repository knowledge assets.

The repository is currently PUBLIC: exporting cannot revoke previously published
Git objects. This tool only prepares a restricted, external destination for
private-repository or encrypted-storage ingestion by the owner.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIRS = ("data/canonical", "data/quarantine")


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def export_private_knowledge(source_root: Path, destination: Path) -> dict:
    source_root = source_root.resolve(strict=True)
    if not source_root.is_dir():
        raise ValueError("Source must be a repository directory")
    if not destination.is_absolute():
        raise ValueError("Private export destination must be absolute")
    # Do not resolve an existing export path into some other location; exports
    # are intentionally create-only and refuse symlinks, links and collisions.
    if destination.exists() or destination.is_symlink():
        raise ValueError("Destination must not already exist")
    parent = destination.parent.resolve()
    destination = parent / destination.name
    if destination == source_root or destination.is_relative_to(source_root):
        raise ValueError("Private assets cannot be exported into a public checkout")
    if source_root.is_relative_to(destination):
        raise ValueError("Export destination cannot contain the source checkout")
    if not destination.name or destination.name in (".", ".."):
        raise ValueError("Expected a new destination directory")

    files = []
    for area in SOURCE_DIRS:
        source = source_root / area
        if not source.is_dir() or source.is_symlink():
            raise ValueError("Missing or unsafe source directory: " + area)
        for item in sorted(source.rglob("*")):
            if item.is_symlink():
                raise ValueError("Knowledge asset symlink is not permitted")
            if not item.is_file():
                if not item.is_dir():
                    raise ValueError("Unsupported knowledge source node")
                continue
            relative = item.relative_to(source_root).as_posix()
            files.append({"path": relative, "sha256": _sha256(item),
                          "bytes": item.stat().st_size})
    if not files:
        raise ValueError("No knowledge files to export")

    destination.mkdir(mode=0o700, exist_ok=False)
    destination.chmod(0o700)
    for row in files:
        src = source_root / row["path"]
        target = destination / row["path"]
        target.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
        target.parent.chmod(0o700)
        # Re-check source digest during copy, rejecting mid-export changes.
        with src.open("rb") as reader, target.open("xb") as writer:
            digest = hashlib.sha256()
            total = 0
            while chunk := reader.read(1024 * 1024):
                writer.write(chunk)
                digest.update(chunk)
                total += len(chunk)
        target.chmod(0o600)
        if total != row["bytes"] or digest.hexdigest() != row["sha256"]:
            raise ValueError("Source changed during private knowledge export")
    manifest = {
        "schema_version": "private-knowledge-export-v1",
        "repository_visibility_at_export": "not_asserted",
        "contains": list(SOURCE_DIRS),
        "file_count": len(files),
        "total_bytes": sum(row["bytes"] for row in files),
        "files": files,
        "important": "Copy is confidential. Existing public Git history is NOT removed.",
    }
    path = destination / "private-export-manifest.json"
    with path.open("x", encoding="utf-8") as stream:
        json.dump(manifest, stream, ensure_ascii=False, indent=2)
        stream.write("\n")
    path.chmod(0o600)
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description="Create a source-preserving private export outside the public repository")
    parser.add_argument("--destination", type=Path, required=True,
                        help="Absolute, new, private directory outside the source checkout")
    args = parser.parse_args()
    manifest = export_private_knowledge(ROOT, args.destination)
    print(json.dumps({"file_count": manifest["file_count"],
                      "total_bytes": manifest["total_bytes"],
                      "destination": str(args.destination),
                      "warning": "This does not hide previously public source history."},
                     ensure_ascii=False))


if __name__ == "__main__":
    main()
