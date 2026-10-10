import unittest
from itertools import product
from pathlib import Path
from tianji_kb.foundations import hexagram
from tianji_kb.golden import run_cases
from tianji_kb.operations.liuyao_chart import chart, palace_for, MASKS
from tianji_kb.resolver import EvidenceResolver

ROOT=Path(__file__).resolve().parents[1]
class LiuyaoExecutionTests(unittest.TestCase):
    def test_fixed_goldens(self):
        self.assertEqual(len(run_cases(domain='liuyao')),3)

    def test_all_palaces_and_all_moving_states(self):
        palaces=set()
        for digits in product('01',repeat=6):
            bits=''.join(digits);p=palace_for(bits)
            palaces.add((p['palace'],p['sequence']))
            self.assertEqual((p['ying']-p['shi'])%6,3)
        self.assertEqual(len(palaces),64)
        # Every 6/7/8/9 configuration has a well-defined original and changed binary.
        for values in product((6,7,8,9),repeat=6):
            bits=''.join(str(v%2) for v in values)
            changed=''.join('1' if v in (6,7) else '0' for v in values)
            self.assertIn(hexagram(bits)['number'],range(1,65))
            self.assertIn(hexagram(changed)['number'],range(1,65))

    def test_line_facts_and_month_break(self):
        result=chart([7]*6,'己丑','午')['result']
        self.assertEqual([x['spirit'] for x in result['lines']],['螣蛇','白虎','玄武','青龙','朱雀','勾陈'])
        self.assertEqual([x['relative'] for x in result['lines']],['子孙','妻财','父母','官鬼','兄弟','父母'])
        self.assertEqual([x['position'] for x in result['lines'] if x['month_break']],[1])
        self.assertEqual([x['position'] for x in result['lines'] if x['empty']],[4])

    def test_actual_traditional_text_follows_calculated_hexagrams_and_moving_lines(self):
        import json
        records = json.loads((ROOT / 'data/canonical/yijing/zhouyi_classic_core.json')
                             .read_text(encoding='utf-8'))['records']
        expected = {row['number']: row for row in records}
        samples = ([9, 7, 7, 7, 7, 7], [7, 7, 7, 7, 7, 7],
                   [6, 6, 6, 6, 6, 6], [6, 7, 8, 9, 7, 8])
        for yao in samples:
            with self.subTest(yao=yao):
                chart_result = chart(list(yao), '甲子', '午')['result']
                classical = chart_result['zhouyi_classic']
                original, changed = chart_result['original'], chart_result['changed']
                row, destination = expected[original['number']], expected[changed['number']]
                self.assertEqual(classical['original']['number'], original['number'])
                self.assertEqual(classical['original']['name'], row['full_name'])
                self.assertEqual(classical['original']['judgment'], row['judgment'])
                self.assertEqual(classical['original']['image'], row['image'])
                self.assertEqual(classical['changed']['number'], changed['number'])
                self.assertEqual(classical['changed']['judgment'], destination['judgment'])
                moving = classical['original']['moving_line_texts']
                self.assertEqual([x['line'] for x in moving],
                                 chart_result['changing_lines'])
                for item in moving:
                    source = row['lines'][item['line'] - 1]
                    self.assertEqual(item['position'], source['position'])
                    self.assertEqual(item['text'], source['text'])
                self.assertFalse(classical['personal_prediction'])
                self.assertEqual(classical['scope'], 'verbatim_classical_excerpts_only')
                self.assertNotIn('provenance', str(classical))
                self.assertNotIn('docs/', str(classical))

    def test_public_api_delivers_real_short_classics_with_no_private_source_paths(self):
        import json
        from fastapi.testclient import TestClient
        from tianji_kb.api import create_app
        with TestClient(create_app()) as client:
            response = client.post('/api/v1/public/execute', json={
                'domain': 'liuyao', 'variant': 'jingfang-eight-palaces-v1',
                'input': {'value': '2026-10-09T17:30:00+08:00',
                          'yao_values': [9, 7, 7, 7, 7, 7]},
                'mode': 'production', 'explain': False,
            })
        self.assertEqual(response.status_code, 200, response.text)
        payload = response.json()
        classic = payload['chart']['zhouyi_classic']
        self.assertEqual(classic['original']['name'], '乾为天')
        self.assertEqual(classic['original']['moving_line_texts'][0]['position'], '初九')
        self.assertTrue(classic['original']['moving_line_texts'][0]['text'])
        self.assertTrue(classic['changed']['judgment'])
        text = json.dumps(payload, ensure_ascii=False)
        self.assertNotIn('data/canonical', text)
        self.assertNotIn('upstream_commit', text)
        self.assertNotIn('source_path', text)

    def test_reject_invalid_input_or_variant(self):
        for args in [([True]*6,'甲子','子'),([7]*5,'甲子','子'),([7]*6,'甲丑','子'),([7]*6,'甲子','午子')]:
            with self.assertRaises(ValueError):chart(*args)
        with self.assertRaises(ValueError):chart([7]*6,'甲子','子',variant='unreviewed')

    def test_repeatable_trace_rule_match_and_resolver_guards(self):
        args=([7]*6,'甲子','午')
        self.assertEqual(chart(*args),chart(*args))
        output=chart(*args)
        month_matches=[m for m in output['rule_matches'] if m['rule_id']=='liuyao.phase2.month_break' and m['kind']=='algorithm_selection']
        self.assertEqual(month_matches[0]['line'],1)
        self.assertFalse(output['interpretation_contract']['ai_may_compute_chart'])
        resolver=EvidenceResolver()
        with self.assertRaises(ValueError):resolver.resolve('liuyao.phase2.najia','other')
        with self.assertRaises(ValueError):resolver.resolve('made.up','jingfang-eight-palaces-v1')
        self.assertTrue(all(ref['original_text'] and ref['classic_id'] for ref in output['evidence'].values()))
