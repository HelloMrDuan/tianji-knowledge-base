import copy
from pathlib import Path
import unittest

from tianji_kb.engine import execute
from tianji_kb.golden import run_cases
from tianji_kb.knowledge import read_json
from tianji_kb.operations.bazi_chart import chart
from tianji_kb.product_claims import authorize_structural_claim
from tianji_kb.resolver import EvidenceResolver
from tianji_kb.scenario_engine import execute_scenario
from tianji_kb.runtime_catalog import build_catalog, load_catalog, release_paths, RuntimeUnavailable, digest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
VARIANT = 'ditiansui-root-visibility-v1'


class BaziStrengthFactorTests(unittest.TestCase):
    def test_six_fixed_goldens_cover_positive_boundary_counterexamples_and_conflicts(self):
        cases = [c for c in run_cases(ROOT, 'bazi') if c['id'].startswith('bazi.factors-')]
        self.assertEqual(len(cases), 6)
        for case in cases:
            self.assertTrue({'bazi.phase2.month_command_factors', 'bazi.phase2.root_candidates', 'bazi.phase2.hidden_to_visible'} <= set(case['rule_ids']))

    def test_numerous_visible_wood_stems_do_not_manufacture_root_or_strength(self):
        out = chart('甲申', '甲子', '甲申', '甲戌', strength_variant=VARIANT)
        obs = out['result']['strength_factors']
        self.assertEqual(obs['root_candidates']['positions'], [])
        self.assertIsNone(obs['overall_strength'])
        self.assertFalse(obs['full_strength_classifier_ready'])
        self.assertTrue(all(v['evidence_level'] == 'C' for v in out['evidence'].values()))
        self.assertNotIn('score', str(obs))

    def test_yin_day_master_can_have_same_element_root_without_same_stem(self):
        out = chart('庚申', '壬寅', '乙酉', '庚子', strength_variant=VARIANT)
        obs = out['result']['strength_factors']
        self.assertEqual(obs['root_candidates']['positions'], [
            {'pillar': 'month', 'branch': '寅', 'hidden_stem': '甲', 'same_stem': False}])
        self.assertTrue(obs['root_candidates']['present_structurally'])
        self.assertEqual(obs['month_command']['same_element_hidden_stems'], ['甲'])
        self.assertIsNone(obs['month_command']['de_ling'])

    def test_day_master_is_not_automatically_counted_as_exposed_useful_god(self):
        out = chart('庚申', '辛酉', '甲寅', '壬子', strength_variant=VARIANT)
        obs = out['result']['strength_factors']
        self.assertTrue(obs['root_candidates']['present_structurally'])
        self.assertFalse(any(r['hidden_stem'] == '甲' for r in obs['hidden_to_visible']['positions']))
        self.assertFalse(obs['hidden_to_visible']['siling_proven'])

    def test_explicit_option_actual_scenario_and_claim_binding_no_prediction(self):
        plain = execute_scenario('bazi-profile', {'value': '2000-01-01T12:00:00+08:00'})
        self.assertNotIn('strength_factors', plain['result'])
        out = execute_scenario('bazi-profile', {'value': '2000-01-01T12:00:00+08:00', 'strength_variant': VARIANT})
        claim = authorize_structural_claim(ROOT, 'bazi-reading', out, 'bazi.root_candidates')
        self.assertEqual(claim['fact_value'], out['result']['strength_factors']['root_candidates'])
        self.assertTrue(claim['evidence'])
        with self.assertRaises(ValueError):
            execute('bazi', {'value': '2000-01-01T12:00:00+08:00', 'strength_variant': 'universal-weights'})
        for unsupported in ('strength', 'useful_god', 'pattern', 'fortune_score'):
            self.assertNotIn(unsupported, out['result'])

    def test_primary_quotes_and_conflict_preserve_original_readings_and_scope(self):
        b = read_json(ROOT / 'data/canonical/bazi/phase1_knowledge.json')
        sources = {s['source_id']: s for s in read_json(ROOT / 'config/knowledge_sources.json')['sources']}
        for s in b['sections']:
            if s['id'] in {f'bazi.section.s{i:03d}' for i in range(23, 30)}:
                self.assertIn(s['text'], (ROOT / sources[s['source_id']]['content_path']).read_text(encoding='utf-8'))
                self.assertNotIn('若思', s['text'])
                self.assertEqual(sources[s['source_id']]['evidence_level'], 'C')
        conflict = next(c for c in b['concepts'] if c['id'] == 'bazi.concept.conflict_siling_days')
        self.assertEqual(conflict['attributes']['status'], 'unresolved')
        self.assertIn('立春念三', conflict['source_refs'][1]['original_text'])
        self.assertEqual(conflict['attributes']['executable_policy'], 'month_branch_and_hidden_stems_only')

    def test_runtime_uses_portable_posix_manifest_and_refuses_backslash_aliases(self):
        artifact = build_catalog(ROOT)
        self.assertTrue(all('\\' not in name for name in artifact['manifest']))
        names = [p.relative_to(ROOT).as_posix() for p in release_paths(ROOT)]
        self.assertEqual(names, sorted(names))
        self.assertIn('bazi', load_catalog(ROOT)['contracts'])
        # A signed-by-digest alias cannot bypass path identity or safety checks.
        altered = copy.deepcopy(artifact)
        name = next(iter(altered['manifest']))
        altered['manifest'][name.replace('/', '\\')] = altered['manifest'].pop(name)
        altered['manifest_sha256'] = digest(altered['manifest'])
        with patch('tianji_kb.runtime_catalog.read_json', return_value=altered):
            with self.assertRaises(RuntimeUnavailable):
                load_catalog(ROOT)


if __name__ == '__main__':
    unittest.main()
