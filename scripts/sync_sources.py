#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from tianji_kb.github import GitHubClient, GitHubError

sources = json.loads((ROOT / "config/source_registry.json").read_text(encoding="utf-8"))["sources"]
state_path = ROOT / "data/state/source_state.json"
old = {}
if state_path.exists():
    old = json.loads(state_path.read_text(encoding="utf-8")).get("sources", {})

client = GitHubClient()
state = {}
changed = 0

for source in sources:
    if not source.get("auto_sync", True):
        continue
    try:
        meta = client.repo(source["repo"])
        branch = meta.get("default_branch") or "main"
        commit = client.latest_commit(source["repo"], branch)
        sha = commit.get("sha")
        detected_license = client.license(source["repo"])
        detected_spdx = ((detected_license or {}).get("license") or {}).get("spdx_id")
        previous = (old.get(source["id"]) or {}).get("head_sha")
        is_changed = bool(previous and previous != sha)
        changed += int(is_changed)
        state[source["id"]] = {
            "repo": source["repo"],
            "branch": branch,
            "head_sha": sha,
            "previous_sha": previous,
            "changed": is_changed,
            "updated_at": meta.get("updated_at"),
            "detected_license_spdx": detected_spdx,
            "registry_license_spdx": source.get("license_spdx"),
            "license_policy": source["license_policy"],
            "domains": source["domains"],
            "sync_status": "ok",
        }
    except GitHubError as exc:
        state[source["id"]] = {
            "repo": source["repo"],
            "license_policy": source["license_policy"],
            "domains": source["domains"],
            "sync_status": "error",
            "error": str(exc),
        }

state_path.parent.mkdir(parents=True, exist_ok=True)
state_path.write_text(json.dumps({
    "generated_at": datetime.now(timezone.utc).isoformat(),
    "changed_sources": changed,
    "sources": state,
}, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
print(f"synced {len(state)} registered sources; changed={changed}")
