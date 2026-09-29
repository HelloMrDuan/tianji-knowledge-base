from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class KnowledgeBase:
    def __init__(self, root: str | Path):
        self.root = Path(root)
        self.canonical = self.root / "data/canonical"

    def _load_json(self, relative: str) -> Any:
        return json.loads((self.canonical / relative).read_text(encoding="utf-8"))

    def get_hexagram(self, query: str | int) -> dict | None:
        corpus = self._load_json("yijing/zhouyi_classic_core.json")
        q = str(query).strip()
        for record in corpus["records"]:
            if q == str(record["number"]) or q in {record["full_name"], record["judgment"].split("。", 1)[0]}:
                return record
        return None

    def search(self, query: str, domain: str | None = None, limit: int = 20) -> list[dict]:
        q = query.strip().lower()
        results: list[dict] = []
        for path in self.canonical.rglob("*.json"):
            if "/batches/" in path.as_posix():
                continue
            obj = json.loads(path.read_text(encoding="utf-8"))
            obj_domain = obj.get("domain") or path.parent.name
            if domain and obj_domain != domain:
                continue
            text = json.dumps(obj, ensure_ascii=False).lower()
            if q not in text:
                continue
            score = text.count(q)
            results.append({
                "path": path.relative_to(self.root).as_posix(),
                "domain": obj_domain,
                "score": score,
            })
        return sorted(results, key=lambda x: (-x["score"], x["path"]))[:limit]
