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
