"""Read-only governance views over reviewed Canonical knowledge assets."""
from __future__ import annotations

import copy
import os
from urllib.parse import urlsplit

from .resolver import EvidenceResolver
from .knowledge import read_json
from .ai_providers import DRIVERS, settings_from_environment
from .explanation import ExplanationFailure
from .prompts import PROMPTS, DEFAULT_PROMPT, get_prompt


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


def reviewed_sources(resolver: EvidenceResolver | None = None) -> list[dict]:
    """Return reviewed source provenance and usage metadata without internal file paths."""
    resolver = resolver or EvidenceResolver()

    usage: dict[str, dict[str, set[str]]] = {
        source_id: {
            "domains": set(),
            "classic_ids": set(),
            "chapter_ids": set(),
            "section_ids": set(),
            "entity_ids": set(),
        }
        for source_id in resolver.sources
    }

    for entity_id, pair in resolver.entities.items():
        collection, entity = pair
        domain = entity.get("domain")
        source_ids: set[str] = set()
        if collection == "classics" and entity.get("source_id"):
            source_ids.add(entity["source_id"])
            usage.setdefault(entity["source_id"], {
                "domains": set(), "classic_ids": set(), "chapter_ids": set(),
                "section_ids": set(), "entity_ids": set(),
            })["classic_ids"].add(entity_id)
        if collection == "sections" and entity.get("source_id"):
            source_ids.add(entity["source_id"])
            item = usage.setdefault(entity["source_id"], {
                "domains": set(), "classic_ids": set(), "chapter_ids": set(),
                "section_ids": set(), "entity_ids": set(),
            })
            item["section_ids"].add(entity_id)
            item["chapter_ids"].add(entity["chapter_id"])
            item["classic_ids"].add(entity["classic_id"])
        for ref in entity.get("source_refs", []):
            source_ids.add(ref["source_id"])
        for source_id in source_ids:
            item = usage.setdefault(source_id, {
                "domains": set(), "classic_ids": set(), "chapter_ids": set(),
                "section_ids": set(), "entity_ids": set(),
            })
            if domain:
                item["domains"].add(domain)
            item["entity_ids"].add(entity_id)

    rows = []
    for source_id, source in sorted(resolver.sources.items()):
        item = usage.get(source_id, {})
        rows.append({
            "id": source_id,
            "title": source["title"],
            "author": source.get("author"),
            "era": source.get("era"),
            "repository": source.get("repository"),
            "url": source["url"],
            "commit": source["commit"],
            "license": source.get("license"),
            "public_domain": source.get("public_domain"),
            "retrieved_at": source.get("retrieved_at"),
            "evidence_level": source["evidence_level"],
            "kind": source["kind"],
            "rights_basis": source.get("rights_basis", ""),
            "review_scope": source.get("review_scope", ""),
            "domains": sorted(item.get("domains", set())),
            "classic_ids": sorted(item.get("classic_ids", set())),
            "chapter_ids": sorted(item.get("chapter_ids", set())),
            "section_count": len(item.get("section_ids", set())),
            "entity_count": len(item.get("entity_ids", set())),
        })
    return rows


def reviewed_layers(resolver: EvidenceResolver | None = None) -> list[dict]:
    """Return aggregate RAW/Quarantine/Canonical governance state without asset paths or bodies."""
    resolver = resolver or EvidenceResolver()
    root = resolver.root

    def tracked_file_count(relative: str) -> int:
        base = root / relative
        if not base.is_dir():
            return 0
        return sum(1 for path in base.rglob("*") if path.is_file())

    source_file_manifest = read_json(root / "config/source_file_manifest.json")
    ingestion_manifest = read_json(root / "config/ingestion_manifest.json")
    protected_manifest = read_json(root / "config/phase1_protected_files.json")

    ingestion_modes: dict[str, int] = {}
    for item in source_file_manifest.get("files", []):
        mode = item.get("ingestion", "UNSPECIFIED")
        ingestion_modes[mode] = ingestion_modes.get(mode, 0) + 1

    classic_counts = {"canonical": 0, "quarantine": 0}
    stage_domains: dict[str, set[str]] = {"canonical": set(), "quarantine": set()}
    for _, pair in resolver.entities.items():
        collection, entity = pair
        if collection != "classics":
            continue
        stage = entity.get("body_stage", "canonical")
        if stage in classic_counts:
            classic_counts[stage] += 1
            stage_domains[stage].add(entity["domain"])

    canonical_domains = sorted({
        entity.get("domain")
        for _, entity in resolver.entities.values()
        if entity.get("domain")
    })

    return [
        {
            "id": "raw",
            "name": "RAW",
            "tracked_file_count": tracked_file_count("data/raw"),
            "classic_count": 0,
            "entity_count": 0,
            "domain_count": 0,
            "domains": [],
            "protected_file_count": 0,
            "registered_ingestion_sources": len(ingestion_manifest.get("sources", [])),
            "ingestion_modes": copy.deepcopy(ingestion_modes),
            "production_queryable": False,
            "promotion_policy": "原始抓取缓存只做来源保全；默认不提交 Git，不直接进入检索。",
            "release_policy": "禁止直接发布；必须先形成可审计快照并进入 Quarantine/独立审核。",
        },
        {
            "id": "quarantine",
            "name": "QUARANTINE",
            "tracked_file_count": tracked_file_count("data/quarantine"),
            "classic_count": classic_counts["quarantine"],
            "entity_count": 0,
            "domain_count": len(stage_domains["quarantine"]),
            "domains": sorted(stage_domains["quarantine"]),
            "protected_file_count": 0,
            "registered_ingestion_sources": 0,
            "ingestion_modes": {},
            "production_queryable": False,
            "promotion_policy": "来源、许可、文本、冲突与规则边界必须独立复核；候选资料不得自动晋级。",
            "release_policy": "生产模式不读取 Quarantine；研究使用也不得自动写回 Canonical。",
        },
        {
            "id": "canonical",
            "name": "CANONICAL",
            "tracked_file_count": tracked_file_count("data/canonical"),
            "classic_count": classic_counts["canonical"],
            "entity_count": len(resolver.entities),
            "domain_count": len(canonical_domains),
            "domains": canonical_domains,
            "protected_file_count": len(protected_manifest.get("sha256", {})),
            "registered_ingestion_sources": 0,
            "ingestion_modes": {},
            "production_queryable": True,
            "promotion_policy": "只有通过来源、许可、结构、冲突与测试审核的资产才可进入 Canonical。",
            "release_policy": "可进入生产检索，但仍受具体领域、Variant、Evidence 与产品发布边界约束。",
        },
    ]


def reviewed_algorithms(resolver: EvidenceResolver | None = None) -> list[dict]:
    """Return the real reviewed execution contracts used by the deterministic engine."""
    resolver = resolver or EvidenceResolver()
    rows = []
    for domain, contract in sorted(resolver.contracts.items()):
        rules = contract.get("rules", [])
        golden_case_ids = sorted({
            case_id
            for rule in rules
            for case_id in rule.get("golden_case_ids", [])
        })
        phase1_rule_ids = sorted({
            rule_id
            for rule in rules
            for rule_id in rule.get("phase1_rule_refs", [])
        })
        executable_count = sum(1 for rule in rules if rule.get("execution_status") == "executable")
        validated_count = sum(1 for rule in rules if rule.get("validation_status") == "validated")
        rows.append({
            "id": f"{domain}:{contract['variant']}",
            "domain": domain,
            "variant": contract["variant"],
            "provider": contract.get("provider", ""),
            "scope": contract.get("scope", ""),
            "unresolved": copy.deepcopy(contract.get("unresolved", [])),
            "rule_count": len(rules),
            "executable_rule_count": executable_count,
            "validated_rule_count": validated_count,
            "golden_case_ids": golden_case_ids,
            "phase1_rule_ids": phase1_rule_ids,
            "production_ready": bool(rules) and executable_count == len(rules) and validated_count == len(rules),
            "deterministic": True,
            "ai_may_compute_chart": False,
        })
    return rows


def provider_configuration() -> list[dict]:
    """Return non-secret explanation-provider configuration metadata without probing the network."""
    driver = os.environ.get("TIANJI_AI_PROVIDER", "disabled")
    endpoint = os.environ.get("TIANJI_AI_BASE_URL", "")
    model = os.environ.get("TIANJI_AI_MODEL", "")
    key_present = bool(os.environ.get("TIANJI_AI_API_KEY", ""))
    prompt_version = os.environ.get("TIANJI_EXPLANATION_PROMPT_VERSION", "explanation-prompt-v2")
    endpoint_origin = ""
    endpoint_host = ""
    if endpoint:
        try:
            parsed = urlsplit(endpoint)
            endpoint_host = parsed.hostname or ""
            if parsed.scheme and endpoint_host:
                port = parsed.port
                endpoint_origin = f"{parsed.scheme}://{endpoint_host}" + (f":{port}" if port else "")
        except ValueError:
            endpoint_origin = ""
            endpoint_host = ""

    configured = False
    status = "disabled" if driver == "disabled" else "incomplete"
    timeout_seconds = None
    max_output_tokens = None
    if driver != "disabled":
        if driver not in DRIVERS:
            status = "invalid"
        else:
            try:
                settings = settings_from_environment()
                configured = settings is not None
                if settings is not None:
                    status = "configured"
                    timeout_seconds = settings["timeout"]
                    max_output_tokens = settings["max_tokens"]
                    model = settings["model"]
            except ExplanationFailure as error:
                status = "incomplete" if error.code == "provider_not_configured" else "invalid"

    if timeout_seconds is None:
        try:
            timeout_seconds = float(os.environ.get("TIANJI_AI_TIMEOUT_SECONDS", "20"))
        except ValueError:
            timeout_seconds = None
    if max_output_tokens is None:
        try:
            max_output_tokens = int(os.environ.get("TIANJI_AI_MAX_OUTPUT_TOKENS", "4096"))
        except ValueError:
            max_output_tokens = None

    return [{
        "id": "explanation-provider",
        "driver": driver,
        "allowed_drivers": list(DRIVERS),
        "status": status,
        "configured": configured,
        "endpoint_origin": endpoint_origin,
        "endpoint_host": endpoint_host,
        "model": model,
        "api_key_present": key_present,
        "api_key_exposed": False,
        "timeout_seconds": timeout_seconds,
        "max_output_tokens": max_output_tokens,
        "prompt_version": prompt_version,
        "live_connectivity_verified": False,
        "automatic_release_allowed": False,
    }]


def prompt_registry() -> list[dict]:
    """Return immutable explanation prompt registry metadata and text for internal review."""
    selected = os.environ.get("TIANJI_EXPLANATION_PROMPT_VERSION", DEFAULT_PROMPT)
    rows = []
    for version in PROMPTS:
        prompt = get_prompt(version)
        rows.append({
            "id": version,
            "version": version,
            "sha256": prompt["sha256"],
            "instruction": prompt["instruction"],
            "instruction_length": len(prompt["instruction"]),
            "selected": version == selected,
            "configured_selection": selected,
            "selection_registered": selected in PROMPTS,
            "default": version == DEFAULT_PROMPT,
            "production_eligible": version == "explanation-prompt-v2",
            "immutable": True,
            "automatic_release_allowed": False,
        })
    return rows


def evaluation_registry(resolver: EvidenceResolver | None = None) -> list[dict]:
    """Return tracked evaluation fixtures and Golden Case coverage without inventing live-model scores."""
    resolver = resolver or EvidenceResolver()
    root = resolver.root
    suite = read_json(root / "evals/explanations/cases-v1.json")
    baseline = read_json(root / "evals/explanations/engine-baseline-v1.json")

    cases_by_domain: dict[str, list[dict]] = {}
    for case in suite.get("cases", []):
        cases_by_domain.setdefault(case["domain"], []).append(case)

    golden_by_domain: dict[str, dict] = {}
    for path in sorted((root / "data/canonical").glob("*/phase2_golden.json")):
        payload = read_json(path)
        golden_by_domain[payload["domain"]] = payload

    domains = sorted(set(resolver.contracts) | set(cases_by_domain) | set(golden_by_domain))
    rows = []
    for domain in domains:
        cases = cases_by_domain.get(domain, [])
        golden = golden_by_domain.get(domain, {})
        tags: dict[str, int] = {}
        for case in cases:
            for tag in case.get("tags", []):
                tags[tag] = tags.get(tag, 0) + 1
        variants = sorted({
            case.get("variant")
            for case in cases
            if case.get("variant")
        })
        contract = resolver.contracts.get(domain)
        if contract and contract.get("variant") not in variants:
            variants.append(contract["variant"])
            variants.sort()
        golden_cases = golden.get("cases", [])
        rows.append({
            "id": domain,
            "domain": domain,
            "suite_id": suite.get("suite_id", ""),
            "variants": variants,
            "eval_case_count": len(cases),
            "explanation_case_count": sum(1 for case in cases if case.get("expected") == "explanation"),
            "refusal_control_count": sum(1 for case in cases if case.get("expected") != "explanation"),
            "suite_golden_ref_count": sum(1 for case in cases if case.get("golden_ref")),
            "phase2_golden_count": len(golden_cases),
            "phase2_golden_ids": [case["id"] for case in golden_cases],
            "eval_case_ids": [case["id"] for case in cases],
            "tag_counts": tags,
            "engine_baseline_main_sha": baseline.get("baseline_main_sha", ""),
            "engine_baseline_file_count": len(baseline.get("algorithm_files", {})),
            "fixed_suite": True,
            "tracked_status": "fixture_only",
            "live_model_quality_verified": False,
            "human_semantic_review_required": True,
            "automatic_release_allowed": False,
            "online_ready": False,
        })
    return rows
