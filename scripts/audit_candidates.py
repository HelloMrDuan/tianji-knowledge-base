#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CANDIDATES = ROOT / "data/registry/discovered_candidates.json"
PERMISSIVE = {"MIT", "Apache-2.0", "BSD-2-Clause", "BSD-3-Clause", "ISC", "CC0-1.0", "Unlicense"}
COPYLEFT = {"GPL-2.0", "GPL-3.0", "AGPL-3.0", "LGPL-2.1", "LGPL-3.0", "MPL-2.0"}

parser = argparse.ArgumentParser()
parser.add_argument("--limit", type=int, default=80)
args = parser.parse_args()

payload = json.loads(CANDIDATES.read_text(encoding="utf-8"))
token = os.getenv("GITHUB_TOKEN")
headers = {
    "Accept": "application/vnd.github+json",
    "User-Agent": "tianji-knowledge-base/0.1",
    "X-GitHub-Api-Version": "2022-11-28",
}
if token:
    headers["Authorization"] = f"Bearer {token}"

def get(url):
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            return None
        raise

pending = [x for x in payload["candidates"] if not x.get("license_audit_at")][:args.limit]
for i, item in enumerate(pending, 1):
    repo = item["repo"]
    enc = "/".join(urllib.parse.quote(p, safe="") for p in repo.split("/"))
    meta = get(f"https://api.github.com/repos/{enc}") or {}
    lic = get(f"https://api.github.com/repos/{enc}/license")
    spdx = ((lic or {}).get("license") or {}).get("spdx_id")
    if spdx == "NOASSERTION":
        spdx = None

    item.update({
        "license_spdx": spdx,
        "default_branch": meta.get("default_branch"),
        "archived": meta.get("archived"),
        "fork": meta.get("fork"),
        "pushed_at": meta.get("pushed_at"),
        "stars": meta.get("stargazers_count", item.get("stars", 0)),
        "forks_count": meta.get("forks_count"),
        "open_issues_count": meta.get("open_issues_count"),
        "license_audit_at": datetime.now(timezone.utc).isoformat(),
    })

    if spdx in PERMISSIVE:
        item["audit_status"] = "ELIGIBLE_PERMISSIVE"
    elif spdx in COPYLEFT:
        item["audit_status"] = "COPYLEFT_REVIEW"
    elif spdx:
        item["audit_status"] = "LICENSE_REVIEW"
    else:
        item["audit_status"] = "NO_LICENSE_REFERENCE_ONLY"

    if meta.get("archived"):
        item["audit_status"] += "_ARCHIVED"

    if i % 20 == 0:
        time.sleep(1)

payload["license_audit_generated_at"] = datetime.now(timezone.utc).isoformat()
payload["license_audited_count"] = sum(bool(x.get("license_audit_at")) for x in payload["candidates"])
CANDIDATES.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(f"audited {len(pending)} candidates; total audited={payload['license_audited_count']}")
