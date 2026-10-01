"""Additive, citation-first model; never promotes or rewrites upstream data."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

COLLECTIONS = ('classics', 'chapters', 'sections', 'terms', 'rules', 'concepts')


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding='utf-8'))


def local_path(root: Path, name: str) -> Path:
    path = (root / name).resolve()
    if not path.is_relative_to(root.resolve()) or not name.startswith(('data/canonical/', 'data/quarantine/')):
        raise ValueError(f'Unsafe evidence path: {name}')
    return path


def source_text(root: Path, source: dict) -> str:
    path = local_path(root, source['content_path'])
    if source['content_format'] == 'text':
        return path.read_text(encoding='utf-8')
    # JSON strings are decoded, so source quotes are checked without escape artifacts.
    def strings(obj):
        if isinstance(obj, str):
            yield obj
        elif isinstance(obj, list):
            for item in obj:
                yield from strings(item)
        elif isinstance(obj, dict):
            for item in obj.values():
                yield from strings(item)
    return '\n'.join(strings(read_json(path)))


def validate_knowledge(root: Path, bundles: list[dict] | None = None) -> dict:
    """Validate schemas, provenance, citations and all model relationships."""
    registry = read_json(root / 'config/domain_registry.json')['domains']
    domains = {x['id']: x for x in registry}
    if len(domains) != len(registry):
        raise ValueError('Duplicate domain IDs')
    sources_obj = read_json(root / 'config/knowledge_sources.json')
    Draft202012Validator(read_json(root / 'schemas/knowledge/sources.schema.json')).validate(sources_obj)
    sources = {x['source_id']: x for x in sources_obj['sources']}
    if len(sources) != len(sources_obj['sources']):
        raise ValueError('Duplicate source IDs')
    texts = {}
    for sid, source in sources.items():
        path = local_path(root, source['content_path'])
        if hashlib.sha256(path.read_bytes()).hexdigest() != source['sha256']:
            raise ValueError(f'Source checksum drift: {sid}')
        if source['kind'] == 'classical' and not source['public_domain']:
            raise ValueError(f'Classical source lacks public-domain review: {sid}')
        if source['kind'] == 'implementation' and source['evidence_level'] != 'D':
            raise ValueError(f'Implementation evidence must remain D: {sid}')
        texts[sid] = source_text(root, source)
    if bundles is None:
        bundles = [read_json(root / x['knowledge_path']) for x in registry if (root / x['knowledge_path']).exists()]
    validator = Draft202012Validator(read_json(root / 'schemas/knowledge/bundle.schema.json'))
    entities = {}
    for bundle in bundles:
        validator.validate(bundle)
        for collection in COLLECTIONS:
            seen_names = set()
            for entity in bundle[collection]:
                eid = entity['id']
                if eid in entities:
                    raise ValueError(f'Duplicate entity ID: {eid}')
                if entity['domain'] != bundle['domain'] or not eid.startswith(bundle['domain'] + '.'):
                    raise ValueError(f'Wrong entity domain: {eid}')
                signature = (entity['name'], entity.get('school'), entity.get('variant'), entity.get('classic_id'), entity.get('chapter_id'))
                if signature in seen_names:
                    raise ValueError(f'Duplicate {collection} name/variant: {signature}')
                seen_names.add(signature)
                entities[eid] = (collection, entity)
    def require(eid, collection):
        if eid not in entities or entities[eid][0] != collection:
            raise ValueError(f'Dangling {collection} reference: {eid}')
        return entities[eid][1]
    for collection, entity in entities.values():
        eid = entity['id']
        if collection == 'classics':
            if any(sid not in sources for sid in [entity['source_id']] + entity.get('source_ids', [])):
                raise ValueError(f'Unknown classic source: {eid}')
        if collection in ('chapters', 'sections'):
            classic = require(entity['classic_id'], 'classics')
            if classic['domain'] != entity['domain']:
                raise ValueError(f'Cross-domain classic reference: {eid}')
        if collection == 'sections':
            chapter = require(entity['chapter_id'], 'chapters')
            if chapter['classic_id'] != entity['classic_id']:
                raise ValueError(f'Chapter/classic mismatch: {eid}')
            sid = entity['source_id']
            if sid not in [classic['source_id']] + classic.get('source_ids', []) or entity['text'] not in texts.get(sid, ''):
                raise ValueError(f'Unverifiable classical section: {eid}')
            if sources[sid]['kind'] != 'classical' or sources[sid]['evidence_level'] == 'D':
                raise ValueError(f'Unreviewed source in canonical section: {eid}')
        for tid in entity.get('term_refs', []) + entity.get('related_terms', []):
            require(tid, 'terms')
        implementation_id = entity.get('operation', {}).get('source_id')
        if implementation_id and implementation_id not in sources:
            raise ValueError(f'Unknown implementation source: {implementation_id}')
        refs = entity.get('source_refs', [])
        if collection in ('terms', 'rules', 'concepts'):
            if not any(ref['role'] == 'classical' for ref in refs):
                raise ValueError(f'Canonical knowledge lacks classical evidence: {eid}')
        for ref in refs:
            sid = ref['source_id']
            if sid not in sources:
                raise ValueError(f'Unknown citation source: {sid}')
            section = require(ref['section_id'], 'sections')
            if section['source_id'] != sid or ref['original_text'] not in section['text']:
                raise ValueError(f'Quote/section mismatch: {eid}')
            if sources[sid]['evidence_level'] == 'D':
                raise ValueError(f'D evidence cannot be promoted: {eid}')
    return {'domains': domains, 'sources': sources, 'bundles': bundles, 'entities': entities}


def validate_protected_files(root: Path) -> None:
    for name, checksum in read_json(root / 'config/phase1_protected_files.json')['sha256'].items():
        path = root / name
        if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != checksum:
            raise ValueError(f'Protected pre-Phase-1 artifact changed: {name}')
