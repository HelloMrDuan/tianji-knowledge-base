"""Reviewed direction facts must not imply force, favourable gods or fate."""
from pathlib import Path
import unittest

from tianji_kb.golden import run_cases
from tianji_kb.knowledge import read_json
from tianji_kb.operations.bazi_chart import chart
from tianji_kb.product_claims import authorize_structural_claim
from tianji_kb.scenario_engine import execute_scenario

ROOT = Path(__file__).resolve().parents[1]
OPTION = 'ditiansui-root-visibility-v1'


class BaziSupportTests(unittest.TestCase):
    def test_fixed_goldens_cover_all_five_directions_and_limits(self):
        cases = [r for r in run_cases(ROOT, 'bazi') if r['id'].startswith('bazi.support-')]
        self.assertEqual(len(cases), 4)
        self.assertTrue(all('bazi.phase2.support_relations' in r['rule_ids'] for r in cases))
        out = chart('甲寅', '丙寅', '甲子', '戊辰', strength_variant=OPTION)
        positions = out['result']['strength_factors']['support_relations']
        self.assertEqual(positions['hidden_positions'][6], {
            'pillar': 'day', 'branch': '子', 'stem': '癸', 'element': '水',
            'polarity': '阴', 'relation': 'generates_me', 'ten_god': '正印'})

    def test_all_ten_stem_categories_match_literal_classical_classification(self):
        # Literal categories, independent of the executable lookup ordering.
        expected = {'甲': ('木', '阳'), '乙': ('木', '阴'),
                    '丙': ('火', '阳'), '丁': ('火', '阴'),
                    '戊': ('土', '阳'), '己': ('土', '阴'),
                    '庚': ('金', '阳'), '辛': ('金', '阴'),
                    '壬': ('水', '阳'), '癸': ('水', '阴')}
        for day in ('甲子', '乙丑', '丙寅', '丁卯', '戊辰', '己巳', '庚午', '辛未', '壬申', '癸酉'):
            with self.subTest(day=day):
                out = chart('甲辰', '丙寅', day, '甲子', strength_variant=OPTION)
                master = out['result']['strength_factors']['support_relations']['day_master']
                self.assertEqual((master['element'], master['polarity']), expected[day[0]])

    def test_visible_peers_and_control_positions_never_become_strength_or_bad_luck(self):
        for pillars in [('甲申', '甲子', '甲申', '甲戌'), ('甲寅', '庚申', '甲子', '辛酉')]:
            out = chart(*pillars, include_relations=True, strength_variant=OPTION)
            obs = out['result']['strength_factors']
            support = obs['support_relations']
            self.assertIsNone(support['effective_support'])
            self.assertIsNone(support['de_shi'])
            self.assertIsNone(support['overall_strength'])
            self.assertIsNone(obs['overall_strength'])
            self.assertFalse(obs['full_strength_classifier_ready'])
            self.assertFalse(any(p['pillar'] == 'day' for p in support['visible_positions']))
            self.assertNotIn('score', str(support))
            self.assertNotIn('weights', support)
            self.assertNotIn('yongshen', out['result'])

    def test_real_scenario_claim_requires_fired_rule_and_returns_fact_not_prediction(self):
        plain = execute_scenario('bazi-profile', {'value': '2000-01-01T12:00:00+08:00'})
        with self.assertRaisesRegex(ValueError, 'claim_rule_not_fired'):
            authorize_structural_claim(ROOT, 'bazi-reading', plain, 'bazi.support_relations')
        raw = execute_scenario('bazi-profile', {'value': '2000-01-01T12:00:00+08:00', 'strength_variant': OPTION})
        claim = authorize_structural_claim(ROOT, 'bazi-reading', raw, 'bazi.support_relations')
        self.assertEqual(claim['fact_value'], raw['result']['strength_factors']['support_relations'])
        self.assertTrue(claim['evidence'])
        with self.assertRaisesRegex(ValueError, 'claim_unavailable'):
            authorize_structural_claim(ROOT, 'bazi-reading', raw, 'bazi.yongshen')

    def test_short_quotes_keep_conditional_text_original_spelling_and_single_source_grade(self):
        sources = {s['source_id']: s for s in read_json(ROOT / 'config/knowledge_sources.json')['sources']}
        b = read_json(ROOT / 'data/canonical/bazi/phase1_knowledge.json')
        sections = {s['id']: s for s in b['sections']}
        for n in range(30, 34):
            s = sections[f'bazi.section.s{n:03d}']
            source = sources[s['source_id']]
            self.assertIn(s['text'], (ROOT / source['content_path']).read_text(encoding='utf-8'))
            self.assertEqual(source['evidence_level'], 'C')
        self.assertIn('水多木漂', (ROOT / sources['bazi.source.yuanhai']['content_path']).read_text(encoding='utf-8'))
        self.assertIn('木坚金缺', sections['bazi.section.s031']['text'])
        self.assertIn('剋', sections['bazi.section.s031']['text'])
