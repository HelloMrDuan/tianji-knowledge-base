#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.public_knowledge_boundary import refuse_public_knowledge_write
refuse_public_knowledge_write()
sys.path.insert(0, str(ROOT / "src"))

from tianji_kb.github import GitHubClient, GitHubError
from tianji_kb.normalize import content_hash, normalize_text

registry = {
    row["id"]: row
    for row in json.loads((ROOT / "config/source_registry.json").read_text(encoding="utf-8"))["sources"]
}
ingestion = json.loads((ROOT / "config/ingestion_manifest.json").read_text(encoding="utf-8"))
client = GitHubClient()
snapshot_root = ROOT / "data/quarantine/source_snapshots"
snapshot_root.mkdir(parents=True, exist_ok=True)

summary = {
    "generated_at": datetime.now(timezone.utc).isoformat(),
    "sources": {},
}
failures: list[str] = []

for entry in ingestion["sources"]:
    source_id = entry["source_id"]
    source = registry.get(source_id)
    if not source:
        failures.append(f"unknown source_id: {source_id}")
        continue
    if source["license_policy"] != "ALLOW":
        failures.append(
            f"blocked non-ALLOW source: {source_id} ({source['license_policy']})"
        )
        continue

    repo = source["repo"]
    try:
        meta = client.repo(repo)
        branch = meta.get("default_branch") or "main"
        commit = client.latest_commit(repo, branch)
        sha = commit["sha"]
    except GitHubError as exc:
        failures.append(f"{repo}: metadata error: {exc}")
        continue

    source_dir = snapshot_root / source_id
    source_dir.mkdir(parents=True, exist_ok=True)
    file_rows = []

    for source_path in entry.get("paths", []):
        try:
            raw = client.fetch_text_file(repo, source_path, ref=sha)
            clean = normalize_text(raw) + "\n"
        except (GitHubError, UnicodeDecodeError) as exc:
            failures.append(f"{repo}/{source_path}: {exc}")
            continue

        out_path = source_dir / source_path
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(clean, encoding="utf-8")

        file_rows.append({
            "source_path": source_path,
            "snapshot_path": out_path.relative_to(ROOT).as_posix(),
            "sha256": content_hash(clean),
            "bytes": len(clean.encode("utf-8")),
        })

    source_manifest = {
        "source_id": source_id,
        "repo": repo,
        "branch": branch,
        "commit": sha,
        "license_policy": source["license_policy"],
        "license_spdx": source.get("license_spdx"),
        "domains": source["domains"],
        "fetched_at": summary["generated_at"],
        "files": file_rows,
        "promotion_status": "QUARANTINE",
        "promotion_note": "Snapshots are upstream evidence only; Canonical promotion requires cleaning, conflict review and validation.",
    }
    (source_dir / "_snapshot_manifest.json").write_text(
        json.dumps(source_manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    summary["sources"][source_id] = {
        "repo": repo,
        "commit": sha,
        "file_count": len(file_rows),
        "status": "ok" if len(file_rows) == len(entry.get("paths", [])) else "partial",
    }

summary["failure_count"] = len(failures)
summary["failures"] = failures
(snapshot_root / "_sync_summary.json").write_text(
    json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
    encoding="utf-8",
)

print(json.dumps(summary, ensure_ascii=False, indent=2))
if failures:
    raise SystemExit(2)
