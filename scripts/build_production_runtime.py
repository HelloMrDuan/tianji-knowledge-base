#!/usr/bin/env python3
"""Explicit build-time audit; never called automatically by a production request."""
from pathlib import Path
from tianji_kb.runtime_catalog import build_catalog
root=Path(__file__).resolve().parents[1]
artifact=build_catalog(root)
print(f"Reviewed production runtime built: {len(artifact['payload']['contracts'])} domains; SHA256={artifact['payload_sha256']}")
