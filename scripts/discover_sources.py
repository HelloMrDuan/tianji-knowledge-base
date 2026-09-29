#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from tianji_kb.github import GitHubClient, GitHubError

parser = argparse.ArgumentParser()
parser.add_argument("--limit", type=int, default=20)
args = parser.parse_args()

queries = json.loads((ROOT / "config/discovery_queries.json").read_text(encoding="utf-8"))["queries"]
known = {x["repo"] for x in json.loads((ROOT / "config/source_registry.json").read_text(encoding="utf-8"))["sources"]}
client = GitHubClient()
found = {}

for query in queries:
    try:
        items = client.search_repositories(query, per_page=args.limit)
    except GitHubError as exc:
        print(f"WARN {query}: {exc}")
        continue
    for item in items:
        repo = item.get("full_name")
        if not repo or repo in known:
            continue
        row = found.setdefault(repo, {
            "repo": repo,
            "html_url": item.get("html_url"),
            "description": item.get("description"),
            "stars": item.get("stargazers_count", 0),
            "updated_at": item.get("updated_at"),
            "language": item.get("language"),
            "matched_queries": [],
            "status": "candidate",
            "license_policy": "QUARANTINE",
        })
        row["matched_queries"].append(query)

out = ROOT / "data/registry/discovered_candidates.json"
out.parent.mkdir(parents=True, exist_ok=True)
rows = sorted(found.values(), key=lambda x: (-int(x.get("stars") or 0), x["repo"]))
out.write_text(json.dumps({"candidates": rows}, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
print(f"discovered {len(rows)} candidate repositories")
