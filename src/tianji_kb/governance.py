"""Read-only governance views over reviewed Canonical knowledge assets."""
from __future__ import annotations

import copy

from .resolver import EvidenceResolver


def school_conflicts(resolver: EvidenceResolver | None = None) -> list[dict]:
    """Return reviewed school-conflict concepts with only their cited short excerpts."""
    resolver = resolver or EvidenceResolver()
    rows = []
    for entity_id, pair in sorted(resolver.entities.items()):
        collection, entity = pair
        if collection != "concepts" or entity.get("kind") != "school_conflict":
            continue

        evidence = []
        for ref in entity.get("source_refs", []):
            source = resolver.sources[ref["source_id"]]
            section = resolver.entities[ref["section_id"]][1]
            chapter = resolver.entities[section["chapter_id"]][1]
            classic = resolver.entities[section["classic_id"]][1]
            evidence.append({
                "source_id": ref["source_id"],
                "section_id": ref["section_id"],
                "classic_id": classic["id"],
                "classic_title": classic["name"],
                "chapter_id": chapter["id"],
                "chapter_title": chapter["name"],
                "locator": section["locator"],
                "original_text": ref["original_text"],
                "evidence_level": source["evidence_level"],
                "source_url": source["url"],
                "commit": source["commit"],
            })

        rows.append({
            "id": entity_id,
            "domain": entity["domain"],
            "name": entity["name"],
            "kind": entity["kind"],
            "status": entity.get("attributes", {}).get("status", "unresolved"),
            "dimension": entity.get("attributes", {}).get("dimension", ""),
            "positions": copy.deepcopy(entity.get("attributes", {}).get("positions", [])),
            "production_policy": entity.get("attributes", {}).get("production_policy", ""),
            "executable_policy": entity.get("attributes", {}).get("executable_policy", ""),
            "confidence": entity["confidence"],
            "evidence": evidence,
        })
    return rows
