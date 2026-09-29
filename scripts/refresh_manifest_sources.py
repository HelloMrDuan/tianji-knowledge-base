#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = json.loads((ROOT / "config/source_file_manifest.json").read_text(encoding="utf-8"))["files"]
REGISTRY = {x["id"]: x for x in json.loads((ROOT / "config/source_registry.json").read_text(encoding="utf-8"))["sources"]}
STATE_PATH = ROOT / "data/state/file_refresh_state.json"

token = os.getenv("GITHUB_TOKEN")
headers = {"User-Agent": "tianji-knowledge-base/0.1"}
if token:
    headers["Authorization"] = f"Bearer {token}"

def request_json(url: str):
    req = urllib.request.Request(url, headers={**headers, "Accept": "application/vnd.github+json"})
    with urllib.request.urlopen(req, timeout=45) as r:
        return json.loads(r.read().decode("utf-8"))

def request_text(url: str) -> str:
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=60) as r:
        raw = r.read()
    return raw.decode("utf-8")

state = {"generated_at": datetime.now(timezone.utc).isoformat(), "files": {}}
changed = 0

for item in MANIFEST:
    source = REGISTRY[item["source_id"]]
    scope_override = bool(item.get("scope_license_verified"))
    if source["license_policy"] not in {"ALLOW", "PUBLIC_DOMAIN_EXTRACT_ONLY"} and not scope_override:
        state["files"][item["target"]] = {"status": "skipped_policy", "repo": item["repo"]}
        continue
    if not item.get("auto_refresh", False):
        continue

    repo = item["repo"]
    meta = request_json(f"https://api.github.com/repos/{repo}")
    branch = meta.get("default_branch") or "main"
    commit = request_json(f"https://api.github.com/repos/{repo}/commits/{urllib.parse.quote(branch, safe='')}")
    sha = commit["sha"]
    path_q = "/".join(urllib.parse.quote(p, safe="") for p in item["path"].split("/"))
    raw_url = f"https://raw.githubusercontent.com/{repo}/{sha}/{path_q}"

    try:
        content = request_text(raw_url).replace("\r\n", "\n").replace("\r", "\n")
    except (urllib.error.URLError, UnicodeDecodeError) as exc:
        state["files"][item["target"]] = {"status": "error", "repo": repo, "error": str(exc)}
        continue

    target = ROOT / item["target"]
    target.parent.mkdir(parents=True, exist_ok=True)
    old = target.read_text(encoding="utf-8") if target.exists() else None
    if old != content:
        target.write_text(content, encoding="utf-8")
        changed += 1

    state["files"][item["target"]] = {
        "status": "updated" if old != content else "unchanged",
        "repo": repo,
        "source_path": item["path"],
        "source_commit": sha,
        "license": item["license"],
        "scope_license_verified": scope_override,
        "ingestion": item["ingestion"],
        "sha256": hashlib.sha256(content.encode("utf-8")).hexdigest(),
        "chars": len(content),
    }

STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
STATE_PATH.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(f"manifest refresh complete: tracked={len(state['files'])}, changed={changed}")
