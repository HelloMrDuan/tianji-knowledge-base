"""Production chunks for reviewed Phase 1 entities, with resolved evidence."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from .knowledge import validate_knowledge


def _citation(ref: dict, model: dict) -> dict:
    source = model['sources'][ref['source_id']]
    section = model['entities'][ref['section_id']][1]
    chapter = model['entities'][section['chapter_id']][1]
    classic = model['entities'][section['classic_id']][1]
    return {
        **ref,
        'classic_id': classic['id'], 'classic_title': classic['name'],
        'chapter_id': chapter['id'], 'chapter_title': chapter['name'],
        'section_title': section['name'], 'locator': section['locator'],
        **{key: source[key] for key in ('repository', 'url', 'commit', 'path',
                                      'license', 'sha256', 'evidence_level', 'content_path')},
    }


def iter_phase1_chunks(root: Path, model: dict | None = None):
    """Read only registered Canonical bundles; evidence files are never indexed wholesale."""
    model = model or validate_knowledge(root)
    for bundle in model['bundles']:
        domain = bundle['domain']
        rel = model['domains'][domain]['knowledge_path']
        if not rel.startswith(f'data/canonical/{domain}/'):
            raise ValueError(f'Noncanonical production bundle: {rel}')
        for collection in ('sections', 'terms', 'rules', 'concepts'):
            for entity in bundle[collection]:
                refs = entity.get('source_refs') or [{
                    'source_id': entity['source_id'], 'section_id': entity['id'],
                    'original_text': entity['text'], 'role': 'classical',
                }]
                citations = [_citation(ref, model) for ref in refs]
                primary = citations[0]
                details = {key: entity[key] for key in (
                    'definition', 'aliases', 'attributes', 'conditions', 'inputs',
                    'operation', 'result', 'exceptions', 'difference',
                ) if key in entity}
                text = entity['name'] + '\n'
                if collection == 'sections':
                    text += entity['text']
                else:
                    text += json.dumps(details, ensure_ascii=False, sort_keys=True)
                    text += '\n原典证据：' + '\n'.join(c['original_text'] for c in citations)
                metadata = {
                    'model': 'phase1-knowledge', 'domain': domain,
                    'topic': f'knowledge_{collection[:-1]}', 'entity_id': entity['id'],
                    'name': entity['name'], 'canonical_path': rel,
                    'source_level': 'L0-public-domain-classic' if collection == 'sections' else 'L1-source-linked',
                    'repo': primary['repository'], 'path': primary['path'], 'commit': primary['commit'],
                    'license': primary['license'], 'corpus': primary['classic_title'],
                    'section_title': primary['section_title'], 'source_refs': citations,
                    'evidence_level': max((c['evidence_level'] for c in citations), key='ABCD'.index),
                    'confidence': entity.get('confidence', 'medium'),
                    'school': entity.get('school'), 'variant': entity.get('variant'),
                    'ruleset': entity.get('variant'), 'execution_status': entity.get('execution_status'),
                }
                implementation_id = entity.get('operation', {}).get('source_id')
                if implementation_id:
                    source = model['sources'][implementation_id]
                    metadata['implementation_source'] = {key: source[key] for key in (
                        'source_id', 'repository', 'commit', 'path', 'license', 'evidence_level',
                    )}
                yield {
                    'id': hashlib.sha256(f'{rel}::{entity["id"]}'.encode()).hexdigest()[:24],
                    'text': text, 'metadata': metadata,
                }
