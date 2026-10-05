"""An acquired dream book must never become a reviewed claim implicitly."""
import copy
from pathlib import Path
import unittest
from unittest.mock import patch

from tianji_kb.engine import PROVIDERS
from tianji_kb.knowledge import read_json, validate_knowledge
from tianji_kb.product_coverage import build_product_coverage
from tianji_kb.scenario_engine import registry, _EXECUTORS

ROOT = Path(__file__).resolve().parents[1]


class DreamSourceReviewTests(unittest.TestCase):
    def test_quarantine_does_not_create_engine_evidence_or_ready_claims(self):
        report = build_product_coverage(ROOT)
        dream = report['dream']
        self.assertEqual(dream['status'], 'NOT_BUILT')
        self.assertEqual(dream['knowledge_stage'], 'PARTIAL')
        self.assertEqual(report['_audit']['reviewed_dream_retrieval']['reviewed_scene_count'], 5)
        self.assertTrue(report['_audit']['reviewed_dream_retrieval']['helper_available'])
        self.assertEqual(dream['ready_claims'], [])
        self.assertFalse(dream['public_enabled'])
        self.assertFalse(dream['ai_enabled'])
        self.assertNotIn('dream', PROVIDERS)
        self.assertNotIn('dream', _EXECUTORS)
        self.assertFalse(next(s for s in registry() if s['id'] == 'dream')['public_release'])
        self.assertEqual(report['_audit']['source_grades'], {'C': 92, 'D': 6})
        self.assertTrue((ROOT / 'data/canonical/dream/phase1_knowledge.json').exists())
        candidate = next(c for c in report['_audit']['staged_source_candidates']
                         if c['source_path'] == '易藏/术数/周公解梦.txt')
        self.assertEqual(candidate['evidence_level'], 'D')
        self.assertEqual(candidate['review_status'], 'pending')
        self.assertFalse(candidate['promotion_allowed'])
        self.assertFalse(candidate['body_saved_to_quarantine'])

    def test_related_symbols_and_absence_do_not_masquerade_as_coverage(self):
        audit = read_json(ROOT / 'data/quarantine/public_domain_snapshots/daizhigev20/zhougong_dream_candidates.json')
        by_id = {r['id']: r for r in audit['candidates']}
        self.assertEqual(len(by_id), 17)
        for key in ('deceased', 'pregnancy', 'marriage', 'work', 'exam'):
            self.assertEqual(by_id[key]['match_scope'], 'related_only')
        self.assertEqual(by_id['chased']['match_scope'], 'not_found')
        self.assertIsNone(by_id['chased']['exact_anchor'])
        self.assertIsNone(by_id['chased']['raw_unicode_offset'])
        for item in by_id.values():
            self.assertFalse(item['production_allowed'])
            if item['id'] in {'snake','water','fire','flying','falling'}:
                self.assertTrue(item['interpretation'])
                self.assertEqual(item['confidence'], 'medium')
                self.assertEqual(item['review_status'], 'approved_cultural_excerpt')
                self.assertEqual(item['evidence_level'], 'C')
            else:
                self.assertIsNone(item['interpretation'])
                self.assertEqual(item['confidence'], 'unconfirmed')
        self.assertEqual(audit['summary']['confirmed_interpretations'], 5)

    def test_existing_validator_rejects_candidate_metadata_as_classical_evidence(self):
        # Pretend to promote the D metadata and cite a metadata string as a
        # classical Section. The existing validator must still stop this.
        source_file = ROOT / 'config/knowledge_sources.json'
        sources = read_json(source_file)
        sid = 'bazi.source.dream-candidate-forgery'
        path = 'data/quarantine/phase1_candidates/daizhigev20/4a6d6f2088825f132521d848c2ea86cf9c9a7620/0c7b0823265c4ff00465f833e0be28f1bf0f2175.json'
        import hashlib
        source = copy.deepcopy(sources['sources'][0])
        source.update(source_id=sid, content_path=path, content_format='json',
                      sha256=hashlib.sha256((ROOT / path).read_bytes()).hexdigest(),
                      evidence_level='D')
        sources['sources'].append(source)
        bundle = copy.deepcopy(read_json(ROOT / 'data/canonical/bazi/phase1_knowledge.json'))
        classic = bundle['classics'][0]
        classic['source_ids'] = classic.get('source_ids', []) + [sid]
        section = next(s for s in bundle['sections'] if s['classic_id'] == classic['id'])
        section.update(source_id=sid, text='易藏/术数/周公解梦.txt')
        original = read_json
        with patch('tianji_kb.knowledge.read_json', side_effect=lambda p: sources if p == source_file else original(p)):
            with self.assertRaisesRegex(ValueError, 'Unreviewed source in canonical section'):
                validate_knowledge(ROOT, [bundle])
