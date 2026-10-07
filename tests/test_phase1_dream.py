import copy
from pathlib import Path
import unittest
from unittest.mock import patch

from tianji_kb.engine import PROVIDERS
from tianji_kb.knowledge import read_json, validate_knowledge
from tianji_kb.operations.dream_knowledge import retrieve
from tianji_kb.rag_context import RetrievalUnavailable

ROOT = Path(__file__).resolve().parents[1]


class DreamKnowledgeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.model = validate_knowledge(ROOT)
        cls.bundle = next(b for b in cls.model['bundles'] if b['domain'] == 'dream')

    def test_ten_reviewed_scenes_extend_existing_model_without_a_chart_engine(self):
        self.assertEqual(len(self.bundle['terms']), 10)
        self.assertEqual(len(self.bundle['rules']), 10)
        self.assertEqual(self.bundle['classics'][0]['body_stage'], 'quarantine')
        self.assertNotIn('dream', PROVIDERS)
        self.assertTrue(all(r['execution_status'] == 'partially_structured' for r in self.bundle['rules']))
        for term in self.bundle['terms']:
            attrs = term['attributes']
            for key in ('symbol', 'entity', 'source', 'locator', 'original_text_short_quote',
                        'interpretation', 'interpretation_type', 'limitations', 'confidence', 'cultural_context'):
                self.assertTrue(attrs[key], key)
            self.assertEqual(attrs['interpretation_type'], 'traditional_chinese_dream')
            self.assertFalse(attrs['ai_enabled'])
            self.assertFalse(attrs['public_enabled'])

    def test_five_fixed_positive_scenes_retrieve_exact_cultural_evidence(self):
        cases = [('我梦见被蛇咬了', '蛇', '蛇咬人主得大财'),
                 ('我梦见我在水中很自在', '水', '自在水中大吉利'),
                 ('我梦见我身在火中', '火', '身在火中贵人扶'),
                 ('我梦见我飞上天', '飞翔', '飞上天富贵大吉'),
                 ('我梦见我掉进井里', '坠落', '身坠井中疾病凶')]
        for text, symbol, quote in cases:
            with self.subTest(symbol=symbol):
                out = retrieve(text)
                self.assertEqual(out['status'], 'reviewed_interpretation_candidates')
                self.assertEqual(len(out['interpretation_candidates']), 1)
                candidate = out['interpretation_candidates'][0]
                self.assertEqual(candidate['symbol'], symbol)
                self.assertEqual(candidate['original_text_short_quote'], quote)
                self.assertEqual(candidate['evidence_level'], 'C')
                self.assertFalse(candidate['personal_prediction'])
                refs = [out['evidence'][eid] for eid in candidate['evidence_ids']]
                self.assertTrue(any(r['original_text'] == quote for r in refs))
                self.assertTrue(any('夜有纷纷梦' in r['original_text'] for r in refs))
                self.assertTrue(all(r['commit'] and r['sha256'] and r['locator'] for r in refs))
                self.assertEqual(out['retrieval'][0]['entity_id'], candidate['term_id'])
                self.assertFalse(out['chart_generated'])
                self.assertFalse(out['ai_enabled'])

    def test_symbols_other_subjects_and_missing_scenes_do_not_supply_meanings(self):
        for text in ('梦见蛇游走', '梦见洪水', '梦见大火', '梦见鸟飞上天',
                     '梦见龙飞上天', '梦见坐飞机', '梦见从山崖坠落',
                     '梦见杯子掉进井里', '梦见火车', '梦见怀孕', '梦见考试'):
            with self.subTest(text=text):
                out = retrieve(text)
                self.assertEqual(out['status'], 'no_reviewed_interpretation')
                self.assertEqual(out['interpretation_candidates'], [])
                self.assertEqual(out['evidence'], {})

    def test_negated_hypothetical_and_unclear_narration_abstains_per_clause(self):
        for text in ('梦见没有被蛇咬', '梦见差点被蛇咬', '梦见好像被蛇咬',
                     '梦见如果我飞上天', '梦见电影里我在火中', '梦见不是我掉进井里'):
            self.assertEqual(retrieve(text)['status'], 'no_reviewed_interpretation', text)
        out = retrieve('我没有被蛇咬，但我梦见我掉进井里')
        self.assertEqual([c['symbol'] for c in out['interpretation_candidates']], ['坠落'])

    def test_retrieval_has_no_raw_quarantine_network_or_model_dependency(self):
        original_bytes, original_text = Path.read_bytes, Path.read_text
        def guard(original):
            def wrapped(path, *args, **kwargs):
                if '/data/quarantine/' in path.as_posix() or '/data/raw/' in path.as_posix():
                    raise AssertionError('Runtime must not read source bodies')
                return original(path, *args, **kwargs)
            return wrapped
        with patch.object(Path, 'read_bytes', guard(original_bytes)), \
             patch.object(Path, 'read_text', guard(original_text)), \
             patch('socket.create_connection', side_effect=AssertionError('No network')):
            self.assertEqual(retrieve('我梦见我飞上天')['status'], 'reviewed_interpretation_candidates')

    def test_missing_or_forged_rag_evidence_cannot_create_a_candidate(self):
        class EmptyIndex:
            def search(self, *args, **kwargs): return []
        with patch('tianji_kb.operations.dream_knowledge.verified_reviewed_index', return_value=EmptyIndex()):
            out = retrieve('我梦见被蛇咬')
            self.assertEqual(out['status'], 'no_reviewed_interpretation')
            self.assertEqual(out['evidence'], {})
        from tianji_kb.knowledge_index import iter_phase1_chunks
        row = copy.deepcopy(next(r for r in iter_phase1_chunks(ROOT, self.model)
                                 if r['metadata']['entity_id'] == 'dream.term.snake'))
        row['text'] = '伪造自由解释'
        class ForgedIndex:
            def search(self, *args, **kwargs): return [row]
        with patch('tianji_kb.operations.dream_knowledge.verified_reviewed_index', return_value=ForgedIndex()):
            with self.assertRaises(RetrievalUnavailable):
                retrieve('我梦见被蛇咬')

    def test_modern_psychology_and_full_book_promotion_remain_closed(self):
        with self.assertRaises(ValueError): retrieve('梦见蛇', variant='modern_dream_psychology')
        with self.assertRaises(ValueError): retrieve('')
        manifest = read_json(ROOT / 'config/public_domain_manifest.json')
        book = next(w for s in manifest['sources'] for w in s.get('works', []) if w['id'] == 'zhougong_jiemeng')
        self.assertEqual(book['promotion'], 'quarantine_only')
        self.assertFalse(book['quality_blockers']['canonical_ready'])
        self.assertFalse((ROOT / book['planned_output']).exists())
        self.assertEqual(book['quality_blockers']['symbol_coverage']['confirmed_interpretations'], 10)

    def test_new_domain_cannot_displace_any_existing_core_domain(self):
        from jsonschema import ValidationError
        original = read_json
        def reader(path):
            obj = original(path)
            if path.name == 'domain_registry.json':
                obj['domains'] = [d for d in obj['domains'] if d['id'] != 'bazi']
            return obj
        with patch('tianji_kb.knowledge.read_json', side_effect=reader), self.assertRaises(ValidationError):
            validate_knowledge(ROOT)


if __name__ == '__main__':
    unittest.main()
