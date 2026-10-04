from pathlib import Path
import unittest

from tianji_kb.engine import execute
from tianji_kb.golden import run_cases
from tianji_kb.knowledge import read_json
from tianji_kb.operations.bazi_chart import chart
from tianji_kb.bazi_commander import COMMAND_VARIANT

ROOT = Path(__file__).resolve().parents[1]


class MonthCommanderTests(unittest.TestCase):
    def test_fixed_goldens_include_conflict_unique_hidden_and_unreviewed_principal(self):
        cases = [c for c in run_cases(ROOT, 'bazi') if c['id'].startswith('bazi.commander-')]
        self.assertEqual(len(cases), 4)
        self.assertTrue(all('bazi.phase2.month_command_variant' in c['rule_ids'] for c in cases))

    def test_source_candidates_are_distinct_and_do_not_parse_ambiguous_days(self):
        out = chart('甲子', '丙寅', '甲子', '乙丑', month_command_variant=COMMAND_VARIANT)
        command = out['result']['month_command_variant']
        self.assertEqual(command['principal_qi'], '甲')
        self.assertEqual([p['candidates'] for p in command['commander_candidates']],
                         [['戊', '丙', '甲'], ['丙', '甲']])
        self.assertEqual(command['source_conflict'], ['bazi.concept.conflict_siling_days'])
        self.assertIsNone(command['commander'])
        self.assertIsNone(command['de_ling'])
        for p in command['commander_candidates']:
            self.assertIsNone(p['exact_day_commander'])
        self.assertTrue(any('立春念三' in e['original_text'] for e in out['evidence'].values()))

    def test_no_first_hidden_shortcut_or_false_agreement_for_unreviewed_month(self):
        command = chart('甲子', '己丑', '甲子', '乙丑',
                        month_command_variant=COMMAND_VARIANT)['result']['month_command_variant']
        self.assertTrue(command['hidden_stems'])
        self.assertIsNone(command['principal_qi'])
        self.assertEqual(command['principal_qi_status'], 'not_reviewed')
        self.assertEqual(command['source_comparison_status'], 'not_reviewed')
        self.assertTrue(all(p['status'] == 'not_reviewed' for p in command['commander_candidates']))

    def test_datetime_adapter_does_not_claim_day_resolution_and_graph_is_evidence_bound(self):
        out = execute('bazi', {'value': '2026-02-10T12:00:00+08:00',
                               'month_command_variant': COMMAND_VARIANT})
        self.assertEqual(out['result']['month_command_variant']['commander_status'], 'unresolved')
        graph = out['result']['strength_factor_graph']
        for f in graph['factors']:
            index = int(f['fact_ref'].split('/')[2])
            self.assertEqual(out['trace'][index]['rule_id'], f['rule_id'])
            self.assertEqual(f['evidence_ids'], out['trace'][index]['evidence_ids'])
            self.assertIn(f['evidence_id'], out['evidence'])
            self.assertEqual(f['variant'], COMMAND_VARIANT)
            self.assertIsNone(f['effect'])
        self.assertEqual(graph['overall_strength'], 'indeterminate')
        self.assertFalse(graph['full_strength_classifier_ready'])

    def test_quotes_match_immutable_sources_and_default_execution_remains_opt_in(self):
        b = read_json(ROOT / 'data/canonical/bazi/phase1_knowledge.json')
        sources = {s['source_id']: s for s in read_json(ROOT / 'config/knowledge_sources.json')['sources']}
        for section in b['sections'][-4:]:
            source = sources[section['source_id']]
            self.assertIn(section['text'], (ROOT / source['content_path']).read_text(encoding='utf-8'))
            self.assertEqual(source['evidence_level'], 'C')
        plain = chart('甲子', '丙寅', '甲子', '乙丑')
        self.assertNotIn('month_command_variant', plain['result'])
        with self.assertRaises(ValueError):
            chart('甲子', '丙寅', '甲子', '乙丑', month_command_variant='global-siling-truth')
        with self.assertRaises(TypeError):
            chart('甲子', '丙寅', '甲子', '乙丑', month_command_variant=COMMAND_VARIANT,
                  days_since_solar_term=9)


if __name__ == '__main__':
    unittest.main()
