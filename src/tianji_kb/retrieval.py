from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Iterable


class RagIndex:
    """Dependency-free lexical retrieval over build/rag_chunks.jsonl.

    This is the stable interface the platform can call before pgvector is added.
    Metadata filtering is intentionally first-class so different schools/rulesets and
    licenses are never silently mixed.
    """

    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.rows = self._load()

    def _load(self) -> list[dict]:
        if not self.path.exists():
            raise FileNotFoundError(
                f"{self.path} does not exist; run scripts/build_rag_chunks.py first"
            )
        rows = []
        with self.path.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    rows.append(json.loads(line))
        return rows

    @staticmethod
    def _tokens(query: str) -> list[str]:
        q = query.strip().lower()
        # Keep CJK runs and alphanumeric tokens; exact full-query match also gets a boost.
        return [x for x in re.findall(r"[\u3400-\u9fff]+|[a-z0-9_+-]+", q) if x]

    def search(
        self,
        query: str,
        *,
        domain: str | None = None,
        topic: str | None = None,
        school: str | None = None,
        ruleset: str | None = None,
        license_allow: Iterable[str] | None = None,
        limit: int = 10,
    ) -> list[dict]:
        q = query.strip().lower()
        tokens = self._tokens(query)
        allowed = set(license_allow or [])

        scored: list[tuple[float, dict]] = []
        for row in self.rows:
            meta = row.get("metadata") or {}
            if domain and meta.get("domain") != domain:
                continue
            if topic and meta.get("topic") != topic:
                continue
            if school and meta.get("school") != school:
                continue
            if ruleset and meta.get("ruleset") != ruleset:
                continue
            if allowed and meta.get("license") not in allowed:
                continue

            text = str(row.get("text") or "")
            hay = text.lower()
            score = 0.0
            # Prefer an exact entity name over incidental mentions in long evidence quotes.
            if q and str(meta.get("name") or "").lower() == q:
                score += 20.0
            if q and q in hay:
                score += 8.0 + hay.count(q)
            for tok in tokens:
                if tok in hay:
                    score += 1.0 + min(hay.count(tok), 5) * 0.25
            # Small provenance preference: a pinned upstream commit is better than none.
            if meta.get("commit"):
                score += 0.1
            if score > 0:
                result = dict(row)
                result["score"] = round(score, 4)
                scored.append((score, result))

        scored.sort(key=lambda x: (-x[0], x[1]["id"]))
        return [row for _, row in scored[:limit]]
