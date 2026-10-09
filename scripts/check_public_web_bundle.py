#!/usr/bin/env python3
"""Deny deploying backend knowledge, secrets, sources or sourcemaps as public static files.

This checks the FINAL static distribution, not source-level string mentions.
It is a fail-closed allowlist, not a replacement for separate server storage.
"""
from pathlib import Path
import argparse


ALLOWED_ASSET_SUFFIXES = {".js", ".css", ".svg", ".png", ".jpg", ".jpeg",
                          ".webp", ".gif", ".ico", ".woff", ".woff2"}


def check_public_bundle(root: Path) -> list[str]:
    root = Path(root)
    if not root.is_dir() or root.is_symlink():
        raise ValueError("Missing or unsafe public distribution directory")
    checked = []
    for node in root.rglob("*"):
        rel = node.relative_to(root).as_posix()
        if node.is_symlink():
            raise ValueError(f"Symlink forbidden in public distribution: {rel}")
        if node.is_dir():
            if rel not in ("assets", "music"):
                raise ValueError(f"Unexpected public directory: {rel}")
            continue
        if not node.is_file():
            raise ValueError(f"Unsupported public node: {rel}")
        allowed = (
            rel == "index.html"
            or (node.parent == root / "assets" and node.suffix.lower() in ALLOWED_ASSET_SUFFIXES)
            or rel == "music/quiet-waters.ogg"
        )
        if not allowed or node.name.startswith("."):
            raise ValueError(f"Non-public artifact or source file blocked: {rel}")
        checked.append(rel)
    if "index.html" not in checked or not any(p.startswith("assets/") and p.endswith(".js") for p in checked):
        raise ValueError("Public distribution is incomplete")
    return sorted(checked)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("dist", type=Path)
    args = parser.parse_args()
    files = check_public_bundle(args.dist)
    print(f"Public web asset boundary passed: {len(files)} static files, no backend artifacts")


if __name__ == "__main__":
    main()
