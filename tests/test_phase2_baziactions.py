from pathlib import Path
import unittest

from tianji_kb.golden import run_cases
from tianji_kb.operations.bazi_chart import chart
from tianji_kb.bazi_root_conditions import STRENGTH_VARIANT
from tianji_kb.scenario_engine import execute_scenario

ROOT = Path(__file__).resolve().parents[1]


class ActionConditionTests(unittest.TestCase):
    def test_four_fixed_goldens_cover_rooted_unrooted_clashed_and_yin_reference(self):
        cases = [c for c in run_cases(ROOT, 'bazi') if c['id'].startswith('bazi.actions-')]
        self.assertEqual(len(cases), 4)
        self.assertTrue(all('bazi.phase2.action_conditions' in c['rule_ids'] for c in cases))

    def test_visible_hidden_and_rooted_visible_are_not_equivalent_effects(self):
        out = chart('甲寅', '丙寅', '甲子', '戊辰', strength_variant=STRENGTH_VARIANT)
        actions = out['result']['action_conditions']
        self.assertEqual(len(actions['visible_relations']), 3)
        self.assertEqual(len(actions['hidden_relations']), 10)
        self.assertTrue(all(r['fact']['visibility'] == 'visible' for r in actions['visible_relations']))
        self.assertTrue(all(r['fact']['visibility'] == 'hidden' and not r['equivalent_to_visible']
                            for r in actions['hidden_relations']))
        self.assertTrue(all(r['effective_action'] is None
                            for r in actions['visible_relations'] + actions['hidden_relations']))
        self.assertFalse(actions['hidden_visible_equivalence_applied'])
        self.assertFalse(actions['weights_available'])
        self.assertIsNone(actions['de_shi'])

    def test_rooted_visible_and_clash_condition_do_not_confirm_actual_action(self):
        out = chart('甲寅', '庚申', '甲子', '辛酉', strength_variant=STRENGTH_VARIANT)
        row = out['result']['action_conditions']['visible_relations'][0]
        self.assertTrue(row['fact']['rooted_visible_candidate'])
        self.assertEqual(row['fact']['hidden_same_stem_positions'], [
            {'pillar': 'year', 'branch': '寅', 'hidden_stem': '甲', 'same_stem': True}])
        self.assertEqual(row['conditions']['root_branch_relations'][0]['kind'], 'branch_six_clashes')
        self.assertEqual(row['conditions']['root_availability'], 'unresolved')
        self.assertEqual(row['effect_status'], 'unresolved')

    def test_graph_edges_bind_direction_facts_and_follow_day_master_perspective(self):
        out = chart('甲寅', '丙寅', '甲子', '戊辰', strength_variant=STRENGTH_VARIANT)
        graph = out['result']['strength_factor_graph']
        for edge in graph['edges']:
            tokens = edge['fact_ref'].split('/')[2:]
            value = out['trace'][int(tokens[0])]
            for token in tokens[1:]:
                value = value[int(token)] if isinstance(value, list) else value[token]
            self.assertEqual(value['relation'], edge['relation'])
            self.assertIn(edge['evidence_id'], out['evidence'])
            self.assertIsNone(edge['effect'])
            if edge['relation'] in ('i_generate', 'i_control'):
                self.assertEqual(edge['from'], 'day_master')
            else:
                self.assertEqual(edge['to'], 'day_master')
        self.assertEqual(graph['overall_strength'], 'indeterminate')
        self.assertFalse(graph['full_strength_classifier_ready'])

    def test_actual_scenario_supports_explicit_conditions_without_prediction_or_ai(self):
        out = execute_scenario('bazi-profile', {'value': '2026-02-10T12:00:00+08:00',
                                                'strength_variant': STRENGTH_VARIANT})
        actions = out['result']['action_conditions']
        self.assertTrue(actions['visible_relations'])
        self.assertTrue(out['evidence'])
        self.assertTrue(out['rule_matches'])
        self.assertIsNone(actions['overall_strength'])
        self.assertFalse(out['result']['strength_factor_graph']['full_strength_classifier_ready'])
        self.assertNotIn('action_conditions', execute_scenario(
            'bazi-profile', {'value': '2026-02-10T12:00:00+08:00'})['result'])


if __name__ == '__main__':
    unittest.main()
