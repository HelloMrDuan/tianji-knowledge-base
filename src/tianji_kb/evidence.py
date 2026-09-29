from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any


@dataclass(frozen=True)
class Citation:
    canonical_path: str | None
    repo: str | None
    source_path: str | None
    commit: str | None
    corpus: str | None = None
    section_title: str | None = None
    ruleset: str | None = None
    school: str | None = None
    license: str | None = None

    @classmethod
    def from_metadata(cls, metadata: dict[str, Any]) -> "Citation":
        return cls(
            canonical_path=metadata.get("canonical_path"),
            repo=metadata.get("repo"),
            source_path=metadata.get("path"),
            commit=metadata.get("commit"),
            corpus=metadata.get("corpus"),
            section_title=metadata.get("section_title"),
            ruleset=metadata.get("ruleset"),
            school=metadata.get("school"),
            license=metadata.get("license"),
        )

    def label(self) -> str:
        parts = []
        if self.corpus:
            parts.append(self.corpus)
        if self.section_title:
            parts.append(self.section_title)
        if not parts and self.ruleset:
            parts.append(self.ruleset)
        if not parts and self.canonical_path:
            parts.append(self.canonical_path)
        return " · ".join(parts) or "Tianji KB"

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["label"] = self.label()
        return data


def evidence_item(row: dict[str, Any], max_chars: int = 3000) -> dict[str, Any]:
    metadata = row.get("metadata") or {}
    text = str(row.get("text") or "")
    truncated = len(text) > max_chars
    if truncated:
        text = text[:max_chars].rstrip() + "…"
    return {
        "id": row.get("id"),
        "score": row.get("score"),
        "text": text,
        "truncated": truncated,
        "citation": Citation.from_metadata(metadata).to_dict(),
        "metadata": {
            "domain": metadata.get("domain"),
            "topic": metadata.get("topic"),
            "source_level": metadata.get("source_level"),
        },
    }


def build_bundle(query: str, rows: list[dict[str, Any]], max_chars: int = 3000) -> dict[str, Any]:
    return {
        "query": query,
        "evidence_count": len(rows),
        "evidence": [evidence_item(row, max_chars=max_chars) for row in rows],
        "generation_contract": {
            "must_ground_claims_in_evidence": True,
            "must_preserve_school_and_ruleset": True,
            "must_not_invent_classical_quotes": True,
            "must_not_recompute_deterministic_chart_results_with_llm": True,
            "when_evidence_missing": "明确说明知识库未检索到足够依据，不补造古籍、规则、出处或断语。",
            "interpretation_scope": "传统文化/术数知识解释；不得包装为科学验证的未来预测。",
        },
    }
