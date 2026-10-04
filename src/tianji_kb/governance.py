"""Read-only governance views over reviewed Canonical knowledge assets."""
from __future__ import annotations

import copy

from .resolver import EvidenceResolver


def _evidence_from_ref(resolver: EvidenceResolver, ref: dict) -> dict:
    source = resolver.sources[ref["source_id"]]
    section = resolver.entities[ref["section_id"]][1]
    chapter = resolver.entities[section["chapter_id"]][1]
    classic = resolver.entities[section["classic_id"]][1]
    return {
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
    }


def school_conflicts(resolver: EvidenceResolver | None = None) -> list[dict]:
    """Return reviewed school-conflict concepts with only their cited short excerpts."""
    resolver = resolver or EvidenceResolver()
    rows = []
    for entity_id, pair in sorted(resolver.entities.items()):
        collection, entity = pair
        if collection != "concepts" or entity.get("kind") != "school_conflict":
            continue
        evidence = [_evidence_from_ref(resolver, ref) for ref in entity.get("source_refs", [])]
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


def reviewed_rules(resolver: EvidenceResolver | None = None) -> list[dict]:
    """Return Canonical rules with execution bindings and reviewed short Evidence."""
    resolver = resolver or EvidenceResolver()
    phase2_by_phase1: dict[str, list[dict]] = {}
    for contract in resolver.contracts.values():
        for rule in contract.get("rules", []):
            summary = {
                "id": rule["id"],
                "domain": rule["domain"],
                "name": rule["name"],
                "variant": rule["variant"],
                "execution_status": rule["execution_status"],
                "validation_status": rule["validation_status"],
                "golden_case_ids": copy.deepcopy(rule.get("golden_case_ids", [])),
                "evidence_scope": rule.get("evidence_scope", ""),
            }
            for phase1_id in rule.get("phase1_rule_refs", []):
                phase2_by_phase1.setdefault(phase1_id, []).append(summary)

    rows = []
    for entity_id, pair in sorted(resolver.entities.items()):
        collection, entity = pair
        if collection != "rules":
            continue
        evidence = [_evidence_from_ref(resolver, ref) for ref in entity.get("source_refs", [])]
        rows.append({
            "id": entity_id,
            "domain": entity["domain"],
            "name": entity["name"],
            "execution_status": entity["execution_status"],
            "school": entity["school"],
            "variant": entity["variant"],
            "difference": entity.get("difference", ""),
            "exceptions": copy.deepcopy(entity.get("exceptions", [])),
            "confidence": entity["confidence"],
            "phase2_bindings": copy.deepcopy(phase2_by_phase1.get(entity_id, [])),
            "evidence": evidence,
        })
    return rows


def reviewed_evidence(resolver: EvidenceResolver | None = None) -> list[dict]:
    """Return approved Canonical short excerpts and the entities that cite them."""
    resolver = resolver or EvidenceResolver()
    used_by: dict[str, list[str]] = {}
    phase2_by_phase1: dict[str, list[str]] = {}

    for contract in resolver.contracts.values():
        for rule in contract.get("rules", []):
            for phase1_id in rule.get("phase1_rule_refs", []):
                phase2_by_phase1.setdefault(phase1_id, []).append(rule["id"])

    for entity_id, pair in resolver.entities.items():
        collection, entity = pair
        if collection not in ("terms", "rules", "concepts"):
            continue
        for ref in entity.get("source_refs", []):
            used_by.setdefault(ref["section_id"], []).append(entity_id)

    rows = []
    for entity_id, pair in sorted(resolver.entities.items()):
        collection, section = pair
        if collection != "sections":
            continue
        source = resolver.sources[section["source_id"]]
        chapter = resolver.entities[section["chapter_id"]][1]
        classic = resolver.entities[section["classic_id"]][1]
        users = sorted(set(used_by.get(entity_id, [])))
        phase2_ids = sorted({
            phase2_id
            for user_id in users
            for phase2_id in phase2_by_phase1.get(user_id, [])
        })
        rows.append({
            "id": entity_id,
            "domain": section["domain"],
            "name": section["name"],
            "classic_id": classic["id"],
            "classic_title": classic["name"],
            "chapter_id": chapter["id"],
            "chapter_title": chapter["name"],
            "source_id": section["source_id"],
            "locator": section["locator"],
            "original_text": section["text"],
            "evidence_level": source["evidence_level"],
            "source_url": source["url"],
            "commit": source["commit"],
            "review": copy.deepcopy(section["review"]),
            "used_by_entity_ids": users,
            "phase2_rule_ids": phase2_ids,
        })
    return rows


def reviewed_classics(resolver: EvidenceResolver | None = None) -> list[dict]:
    """Return Canonical book/chapter metadata without exposing full book bodies."""
    resolver = resolver or EvidenceResolver()

    sections_by_classic: dict[str, list[dict]] = {}
    chapters_by_classic: dict[str, list[dict]] = {}
    used_by_section: dict[str, list[str]] = {}
    phase2_by_phase1: dict[str, list[str]] = {}

    for contract in resolver.contracts.values():
        for rule in contract.get("rules", []):
            for phase1_id in rule.get("phase1_rule_refs", []):
                phase2_by_phase1.setdefault(phase1_id, []).append(rule["id"])

    for entity_id, pair in resolver.entities.items():
        collection, entity = pair
        if collection == "sections":
            sections_by_classic.setdefault(entity["classic_id"], []).append(entity)
        elif collection == "chapters":
            chapters_by_classic.setdefault(entity["classic_id"], []).append(entity)
        elif collection in ("terms", "rules", "concepts"):
            for ref in entity.get("source_refs", []):
                used_by_section.setdefault(ref["section_id"], []).append(entity_id)

    rows = []
    for entity_id, pair in sorted(resolver.entities.items()):
        collection, classic = pair
        if collection != "classics":
            continue
        source = resolver.sources[classic["source_id"]]
        sections = sections_by_classic.get(entity_id, [])
        chapters = chapters_by_classic.get(entity_id, [])
        phase2_ids = sorted({
            phase2_id
            for section in sections
            for user_id in used_by_section.get(section["id"], [])
            for phase2_id in phase2_by_phase1.get(user_id, [])
        })
        chapter_rows = []
        for chapter in sorted(chapters, key=lambda item: item["id"]):
            chapter_sections = [section for section in sections if section["chapter_id"] == chapter["id"]]
            chapter_rows.append({
                "id": chapter["id"],
                "name": chapter["name"],
                "locator": chapter.get("locator", ""),
                "reviewed_section_count": len(chapter_sections),
                "section_ids": sorted(section["id"] for section in chapter_sections),
            })
        rows.append({
            "id": entity_id,
            "domain": classic["domain"],
            "name": classic["name"],
            "body_stage": classic.get("body_stage", "canonical"),
            "source_id": classic["source_id"],
            "source_title": source["title"],
            "evidence_level": source["evidence_level"],
            "source_url": source["url"],
            "commit": source["commit"],
            "rights_basis": source.get("rights_basis", ""),
            "review_scope": source.get("review_scope", ""),
            "chapter_count": len(chapter_rows),
            "reviewed_section_count": len(sections),
            "phase2_rule_ids": phase2_ids,
            "chapters": chapter_rows,
        })
    return rows


def reviewed_chapters(resolver: EvidenceResolver | None = None) -> list[dict]:
    """Return Canonical chapter metadata and review coverage without chapter bodies."""
    resolver = resolver or EvidenceResolver()

    sections_by_chapter: dict[str, list[dict]] = {}
    used_by_section: dict[str, list[str]] = {}
    phase2_by_phase1: dict[str, list[str]] = {}

    for contract in resolver.contracts.values():
        for rule in contract.get("rules", []):
            for phase1_id in rule.get("phase1_rule_refs", []):
                phase2_by_phase1.setdefault(phase1_id, []).append(rule["id"])

    for entity_id, pair in resolver.entities.items():
        collection, entity = pair
        if collection == "sections":
            sections_by_chapter.setdefault(entity["chapter_id"], []).append(entity)
        elif collection in ("terms", "rules", "concepts"):
            for ref in entity.get("source_refs", []):
                used_by_section.setdefault(ref["section_id"], []).append(entity_id)

    rows = []
    for entity_id, pair in sorted(resolver.entities.items()):
        collection, chapter = pair
        if collection != "chapters":
            continue
        classic = resolver.entities[chapter["classic_id"]][1]
        source = resolver.sources[classic["source_id"]]
        sections = sections_by_chapter.get(entity_id, [])
        used_entities = sorted({
            used_id
            for section in sections
            for used_id in used_by_section.get(section["id"], [])
        })
        phase2_ids = sorted({
            phase2_id
            for used_id in used_entities
            for phase2_id in phase2_by_phase1.get(used_id, [])
        })
        rows.append({
            "id": entity_id,
            "domain": chapter["domain"],
            "name": chapter["name"],
            "locator": chapter.get("locator", ""),
            "classic_id": classic["id"],
            "classic_title": classic["name"],
            "body_stage": classic.get("body_stage", "canonical"),
            "source_id": classic["source_id"],
            "source_title": source["title"],
            "evidence_level": source["evidence_level"],
            "source_url": source["url"],
            "commit": source["commit"],
            "rights_basis": source.get("rights_basis", ""),
            "review_scope": source.get("review_scope", ""),
            "reviewed_section_count": len(sections),
            "section_ids": sorted(section["id"] for section in sections),
            "used_by_entity_ids": used_entities,
            "phase2_rule_ids": phase2_ids,
        })
    return rows


def reviewed_terms(resolver: EvidenceResolver | None = None) -> list[dict]:
    """Return Canonical term definitions and provenance metadata without source bodies."""
    resolver = resolver or EvidenceResolver()

    rule_ids_by_section: dict[str, list[str]] = {}
    phase2_by_phase1: dict[str, list[str]] = {}
    for contract in resolver.contracts.values():
        for rule in contract.get("rules", []):
            for phase1_id in rule.get("phase1_rule_refs", []):
                phase2_by_phase1.setdefault(phase1_id, []).append(rule["id"])

    for entity_id, pair in resolver.entities.items():
        collection, entity = pair
        if collection != "rules":
            continue
        for ref in entity.get("source_refs", []):
            rule_ids_by_section.setdefault(ref["section_id"], []).append(entity_id)

    rows = []
    for entity_id, pair in sorted(resolver.entities.items()):
        collection, term = pair
        if collection != "terms":
            continue
        evidence = []
        related_rule_ids: set[str] = set()
        for ref in term.get("source_refs", []):
            source = resolver.sources[ref["source_id"]]
            section = resolver.entities[ref["section_id"]][1]
            chapter = resolver.entities[section["chapter_id"]][1]
            classic = resolver.entities[section["classic_id"]][1]
            related_rule_ids.update(rule_ids_by_section.get(ref["section_id"], []))
            evidence.append({
                "source_id": ref["source_id"],
                "section_id": ref["section_id"],
                "classic_id": classic["id"],
                "classic_title": classic["name"],
                "chapter_id": chapter["id"],
                "chapter_title": chapter["name"],
                "locator": section["locator"],
                "evidence_level": source["evidence_level"],
            })
        phase2_ids = sorted({
            phase2_id
            for rule_id in related_rule_ids
            for phase2_id in phase2_by_phase1.get(rule_id, [])
        })
        rows.append({
            "id": entity_id,
            "domain": term["domain"],
            "name": term["name"],
            "aliases": copy.deepcopy(term.get("aliases", [])),
            "definition": term.get("definition", ""),
            "confidence": term["confidence"],
            "definition_kind": term.get("attributes", {}).get("definition_kind", ""),
            "production_interpretation": term.get("attributes", {}).get("production_interpretation"),
            "related_terms": copy.deepcopy(term.get("related_terms", [])),
            "related_rule_ids": sorted(related_rule_ids),
            "phase2_rule_ids": phase2_ids,
            "evidence": evidence,
        })
    return rows
