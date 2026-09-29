#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from tianji_kb.github import GitHubClient, GitHubError
from tianji_kb.normalize import content_hash, normalize_text

registry = {
    row["id"]: row
    for row in json.loads((ROOT / "config/source_registry.json").read_text(encoding="utf-8"))["sources"]
}
manifest = json.loads((ROOT / "config/public_domain_manifest.json").read_text(encoding="utf-8"))
client = GitHubClient()
snapshot_root = ROOT / "data/quarantine/public_domain_snapshots"
snapshot_root.mkdir(parents=True, exist_ok=True)

summary = {
    "generated_at": datetime.now(timezone.utc).isoformat(),
    "works": {},
    "failures": [],
}

for group in manifest["sources"]:
    source_id = group["source_id"]
    source = registry.get(source_id)
    if not source:
        summary["failures"].append(f"unknown source_id: {source_id}")
        continue
    if source["license_policy"] != "PUBLIC_DOMAIN_EXTRACT_ONLY":
        summary["failures"].append(
            f"source must be PUBLIC_DOMAIN_EXTRACT_ONLY: {source_id}={source['license_policy']}"
        )
        continue

    repo = source["repo"]
    try:
        meta = client.repo(repo)
        branch = meta.get("default_branch") or "main"
        commit = client.latest_commit(repo, branch)["sha"]
    except GitHubError as exc:
        summary["failures"].append(f"{repo}: metadata error: {exc}")
        continue

    for work in group.get("works", []):
        work_id = work["id"]
        source_path = work["path"]
        try:
            raw = client.fetch_text_file(repo, source_path, ref=commit)
            clean = normalize_text(raw) + "\n"
        except (GitHubError, UnicodeDecodeError) as exc:
            summary["failures"].append(f"{repo}/{source_path}: {exc}")
            continue

        out = snapshot_root / source_id / f"{work_id}.txt"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(clean, encoding="utf-8")
        summary["works"][work_id] = {
            "title": work["title"],
            "domain": work["domain"],
            "repo": repo,
            "source_path": source_path,
            "snapshot_path": out.relative_to(ROOT).as_posix(),
            "commit": commit,
            "sha256": content_hash(clean),
            "bytes": len(clean.encode("utf-8")),
            "promotion": work.get("promotion"),
            "status": "ok",
        }

(summary_path := snapshot_root / "_sync_summary.json").write_text(
    json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
    encoding="utf-8",
)
print(json.dumps(summary, ensure_ascii=False, indent=2))
if summary["failures"]:
    raise SystemExit(2)
