import copy
import json
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from jsonschema import ValidationError
from tianji_kb.coverage import build_coverage, markdown_coverage
from tianji_kb.evidence import build_bundle
from tianji_kb.knowledge import read_json, validate_knowledge
from tianji_kb.knowledge_index import iter_phase1_chunks

ROOT = Path(__file__).resolve().parents[1]

class CrossDomainTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.model = validate_knowledge(ROOT)

    def reject(self, mutate, message):
        bundles = copy.deepcopy(self.model['bundles'])
        mutate(bundles)
        with self.assertRaisesRegex(ValueError, message):
            validate_knowledge(ROOT, bundles)

    def test_wrong_domain_unknown_sources_and_changed_quote_rejected(self):
        self.reject(lambda b: b[0]['terms'][0].update(domain='liuyao'), 'Wrong entity domain')
        self.reject(lambda b: b[0]['terms'][0]['source_refs'][0].update(source_id='missing.source'), 'Unknown citation source')
        self.reject(lambda b: b[0]['terms'][0]['source_refs'][0].update(original_text='不存在的伪造古籍句子'), 'Quote/section mismatch')

    def test_broken_hierarchy_and_duplicates_rejected(self):
        self.reject(lambda b: b[0]['sections'][0].update(chapter_id='yijing.chapter.no_such_chapter'), 'Dangling')
        self.reject(lambda b: b[0]['terms'][1].update(name=b[0]['terms'][0]['name']), 'Duplicate terms')
        self.reject(lambda b: b[0]['rules'][0].update(term_refs=['qimen.term.dangling']), 'Dangling')

    def test_executable_provider_and_auxiliary_sources_resolve(self):
        self.reject(lambda b: b[0]['rules'][0]['operation'].update(provider='tianji_kb.operations.yijing.nonexistent'), 'Unresolvable provider')
        self.reject(lambda b: b[0]['rules'][0]['operation']['parameters'].update(calendar_source_id='missing.calendar'), 'Unknown auxiliary source')
        self.reject(lambda b: b[0]['rules'][0]['operation'].pop('provider'), 'no provider')

    def test_D_evidence_cannot_enter_canonical(self):
        original = read_json
        def read(path):
            obj = original(path)
            if path.name == 'knowledge_sources.json':
                for source in obj['sources']:
                    if source['kind'] == 'classical':
                        source['evidence_level'] = 'D'
            return obj
        with patch('tianji_kb.knowledge.read_json', side_effect=read):
            with self.assertRaisesRegex(ValueError, 'Unreviewed source in canonical section'):
                validate_knowledge(ROOT)

    def test_registry_rejects_quarantine_production_path(self):
        original = read_json
        def read(path):
            obj = original(path)
            if path.name == 'domain_registry.json':
                obj['domains'][0]['knowledge_path'] = 'data/quarantine/phase1/yijing/candidate.json'
            return obj
        with patch('tianji_kb.knowledge.read_json', side_effect=read), self.assertRaises(ValidationError):
            validate_knowledge(ROOT)

    def test_production_index_ignores_quarantine_canary_and_preserves_all_entity_counts(self):
        # Real reviewed bundles; isolated filesystem holds an unmistakable unreviewed body.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            marker = root / 'data/quarantine/phase1/research.json'
            marker.parent.mkdir(parents=True)
            marker.write_text(json.dumps({'text':'UNREVIEWED_CANARY_7259'}))
            names = {s['content_path'] for s in self.model['sources'].values()}
            names.update(d['knowledge_path'] for d in self.model['domains'].values())
            names.update(['config/knowledge_sources.json', 'config/domain_registry.json'])
            names.update(str(p.relative_to(ROOT)) for p in (ROOT/'schemas/knowledge').glob('*.json'))
            for name in names:
                destination = root/name
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT/name,destination)
            chunks = list(iter_phase1_chunks(root))
        self.assertEqual(len(chunks),sum(len(b[k]) for b in self.model['bundles'] for k in ('sections','terms','rules','concepts')))
        self.assertEqual(len({c['id'] for c in chunks}),len(chunks))
        for chunk in chunks:
            meta = chunk['metadata']
            self.assertTrue(meta['canonical_path'].startswith('data/canonical/'))
            self.assertNotIn('UNREVIEWED_CANARY_7259',chunk['text'])
            self.assertNotIn('"start_year":',chunk['text'])  # D nine-period numeric research rows.
            self.assertNotIn('壬梁紫府武',chunk['text'])  # Unreviewed Ziwei glyph variant.
            self.assertTrue(all(ref['classic_id'] and ref['chapter_id'] and ref['section_id'] for ref in meta['source_refs']))
            self.assertEqual(meta['evidence_level'],'C')

    def test_exact_term_retrieval_beats_incidental_mentions_in_evidence(self):
        from tianji_kb.retrieval import RagIndex
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp)/'entities.jsonl'
            path.write_text(''.join(json.dumps(c,ensure_ascii=False)+'\n' for c in iter_phase1_chunks(ROOT,self.model)))
            index = RagIndex(path)
            for domain,term in [('yijing','阴爻'),('liuyao','用神'),('qimen','值符'),('ziwei','化禄'),('fengshui','明堂'),('liuren','月将')]:
                rows = index.search(term,domain=domain,topic='knowledge_term',limit=1)
                self.assertEqual(rows[0]['metadata']['name'],term)

    def test_context_preserves_variant_execution_status_and_classical_refs(self):
        chunk = next(c for c in iter_phase1_chunks(ROOT,self.model) if c['metadata']['domain']=='liuren' and c['metadata']['execution_status']=='partially_structured')
        evidence = build_bundle('初传',[chunk])['evidence'][0]
        self.assertEqual(evidence['citation']['execution_status'],'partially_structured')
        self.assertEqual(evidence['citation']['source_refs'],chunk['metadata']['source_refs'])
        self.assertEqual(evidence['citation']['variant'],chunk['metadata']['variant'])
        self.assertEqual(evidence['citation']['evidence_level'],'C')

    def test_coverage_artifact_and_docs_match_actual_entities(self):
        report = build_coverage(ROOT)
        self.assertEqual(report,read_json(ROOT/'data/coverage/phase1.json'))
        self.assertIn(markdown_coverage(report).strip(),(ROOT/'docs/COVERAGE.md').read_text())
        self.assertEqual(len(report['domains']),7)
        self.assertTrue(all(d['status']=='phase1_complete' and all(d['completion_criteria'].values()) for d in report['domains']))
        for domain in report['domains']:
            self.assertEqual(domain['sources']['A']+domain['sources']['B'],0)
            self.assertGreater(domain['sources']['C'],0)

    def test_approved_sections_are_original_and_implementation_evidence_is_frozen(self):
        for bundle in self.model['bundles']:
            for section in bundle['sections']:
                self.assertFalse(any(0xE000<=ord(c)<=0xF8FF for c in section['text']))
                self.assertNotIn('原劍按',section['text'])
        for source in self.model['sources'].values():
            if source['kind']=='implementation':
                self.assertNotIn('/source_snapshots/',source['content_path'])
                self.assertTrue((ROOT/source['content_path']).parent.joinpath('LICENSE').exists())
