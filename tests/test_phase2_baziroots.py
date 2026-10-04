from pathlib import Path
import unittest

from tianji_kb.engine import execute
from tianji_kb.golden import run_cases
from tianji_kb.operations.bazi_chart import chart
from tianji_kb.bazi_root_conditions import STRENGTH_VARIANT

ROOT = Path(__file__).resolve().parents[1]


class ConditionalRootTests(unittest.TestCase):
    def test_five_goldens_cover_root_types_absence_and_interaction_boundaries(self):
        cases = [c for c in run_cases(ROOT, 'bazi') if c['id'].startswith('bazi.roots-')]
        self.assertEqual(len(cases), 5)
        self.assertTrue(all('bazi.phase2.root_conditions' in c['rule_ids'] for c in cases))

    def test_clash_remains_condition_and_does_not_delete_structural_root(self):
        out = chart('甲寅', '庚申', '甲子', '辛酉', strength_variant=STRENGTH_VARIANT)
        row = out['result']['root_conditions']['roots'][0]
        self.assertEqual(row['fact']['pillar'], 'year')
        self.assertTrue(row['fact']['present_structurally'])
        self.assertEqual(row['conditions']['branch_relations'], [
            {'kind': 'branch_six_clashes', 'pillars': ['year', 'month'], 'branches': ['寅', '申']}])
        self.assertEqual(row['availability_status'], 'unresolved')
        self.assertIsNone(row['effective_strength'])
        self.assertFalse(out['result']['root_conditions']['root_erasure_applied'])

    def test_residual_type_reading_conflict_is_visible_without_rank(self):
        out = chart('庚申', '辛酉', '乙未', '壬辰', strength_variant=STRENGTH_VARIANT)
        roots = out['result']['root_conditions']['roots']
        self.assertIsNone(roots[0]['fact']['principal_qi_match'])
        self.assertTrue(roots[0]['fact']['tomb_branch'])
        self.assertEqual(roots[1]['type_source_conflict'], 'bazi.concept.conflict_root_type_readings')
        self.assertEqual(roots[1]['interpretation_candidates'][0]['status'], 'candidate_only')
        self.assertNotIn('rank', roots[1])
        self.assertTrue(any('余气者,如丙丁逢未,丙丁逢戌' in e['original_text'] for e in out['evidence'].values()))

    def test_month_position_and_exposure_are_facts_without_position_weight(self):
        out = chart('甲寅', '丙寅', '甲子', '乙丑', strength_variant=STRENGTH_VARIANT)
        roots = out['result']['root_conditions']['roots']
        self.assertEqual([r['fact']['is_month_position'] for r in roots], [False, True])
        self.assertEqual(roots[1]['fact']['exposed_visible_pillars'], ['year'])
        self.assertTrue(roots[1]['fact']['principal_qi_match'])
        self.assertTrue(all(r['availability_status'] == 'unresolved' for r in roots))
        self.assertFalse(out['result']['root_conditions']['weights_available'])

    def test_new_option_runs_actual_engine_with_bound_graph_and_keeps_interpretations_unresolved(self):
        out = execute('bazi', {'value': '2026-02-10T12:00:00+08:00', 'strength_variant': STRENGTH_VARIANT})
        graph = out['result']['strength_factor_graph']
        self.assertEqual(graph['variant'], STRENGTH_VARIANT)
        self.assertEqual({f['id'] for f in graph['factors']}, {'month_command_variant', 'root_conditions', 'action_conditions'})
        for f in graph['factors']:
            step = out['trace'][int(f['fact_ref'].split('/')[2])]
            self.assertEqual(step['rule_id'], f['rule_id'])
            self.assertEqual(step['evidence_ids'], f['evidence_ids'])
            self.assertTrue(all(e in out['evidence'] for e in f['evidence_ids']))
            self.assertIsNone(f['effect'])
        self.assertEqual(graph['overall_strength'], 'indeterminate')
        self.assertFalse(graph['full_strength_classifier_ready'])
        from tianji_kb.product_coverage import build_product_coverage
        audit = build_product_coverage(ROOT)['_audit']['conditional_strength_variants']
        self.assertEqual(audit['bazi.concept.root_conditions_variant_v1']['maturity'], 'PARTIAL')
        self.assertFalse(audit['bazi.concept.root_conditions_variant_v1']['weights_available'])
        self.assertNotIn('root_conditions', chart('甲寅', '丙寅', '甲子', '乙丑')['result'])


if __name__ == '__main__':
    unittest.main()
