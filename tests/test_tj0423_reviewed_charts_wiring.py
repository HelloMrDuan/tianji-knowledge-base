"""TJ-031.15 [E0423] Reviewed-chart wiring lock-in: Ziwei 6 + Liuren 9 methods.

Audit finding (2026-11-25, sealed assembly, runtime SHA 8d19d18b...):
the 15 reviewed deterministic chart rules were ALREADY wired at main
b76d60ef -- the earlier "zero literal references" count missed the
dynamic rule-ID construction (ziwei_chart builds 'ziwei.phase2.'+stage;
liuren_chart maps method name -> rule suffix). No algorithm was rebuilt
here. These tests pin the wiring with execution evidence so a future
change cannot silently unwire a rule: every one of the 15 rule IDs must
fire in a trace, against the sealed Golden cases, through engine.execute.

Scope (per adjudication list A/C): deterministic charting only.
Ziwei: no dayun/brightness/fortune. Liuren: no noble generals / fortune.
"""
import unittest

from tianji_kb.engine import execute
from tianji_kb.golden import run_cases
from tianji_kb.operations.ziwei_chart import chart as ziwei_chart

ZIWEI_RULES = [
    'ziwei.phase2.life_body',
    'ziwei.phase2.bureau',
    'ziwei.phase2.palaces',
    'ziwei.phase2.major_stars',
    'ziwei.phase2.auxiliary_stars',
    'ziwei.phase2.mutagens',
]

# Independent pin of the method -> rule-suffix mapping (NOT imported from
# operations.liuren_chart, so the test does not merely agree with itself).
LIUREN_METHOD_RULES = {
    '贼克': 'liuren.phase2.zeike',
    '比用': 'liuren.phase2.biyong',
    '涉害': 'liuren.phase2.shehai',
    '遥克': 'liuren.phase2.yaoke',
    '昴星': 'liuren.phase2.maoxing',
    '别责': 'liuren.phase2.bieze',
    '八专': 'liuren.phase2.bazhuan',
    '伏吟': 'liuren.phase2.fuyin',
    '返吟': 'liuren.phase2.fanyin',
}

LIUREN_STRUCTURAL_RULES = [
    'liuren.phase2.month_general',
    'liuren.phase2.plates',
    'liuren.phase2.lessons',
]


class ZiweiSixRulesTests(unittest.TestCase):
    def test_all_six_rules_fire_in_every_golden_case(self):
        cases = run_cases(domain='ziwei')
        self.assertEqual(len(cases), 3)
        for case in cases:
            self.assertEqual(case['rule_ids'], ZIWEI_RULES, case['id'])

    def test_chart_trace_and_result_carry_all_six_stages(self):
        for args in (('甲子', 1, 1, '子'), ('甲子', 1, 1, '丑'),
                     ('壬申', 1, 30, '子')):
            output = ziwei_chart(*args)
            self.assertEqual([s['rule_id'] for s in output['trace']],
                             ZIWEI_RULES)
            result = output['result']
            for key in ('life_palace', 'body_palace', 'life_ganzhi',
                        'bureau', 'palaces', 'major_stars',
                        'auxiliary_stars', 'four_transformations'):
                self.assertIn(key, result)
            self.assertEqual(len(result['palaces']), 12)
            self.assertEqual(len(result['major_stars']), 14)

    def test_engine_datetime_path_fires_all_six_rules(self):
        raw = execute('ziwei', {'value': '1999-02-16T00:00:00+08:00',
                                'year_boundary': 'lunar-new-year'})
        self.assertEqual(raw['variant'], 'quanshu-lunar-iztro-mutagen-v1')
        self.assertTrue(raw['deterministic'])
        self.assertEqual([s['rule_id'] for s in raw['trace']], ZIWEI_RULES)

    def test_no_advanced_content_rides_on_the_basic_chart(self):
        result = ziwei_chart('甲子', 1, 1, '子')['result']
        self.assertNotIn('dayun', result)
        self.assertNotIn('大限', result)
        self.assertFalse(any('亮度' in key for key in result))
        self.assertIn('无大限流年', result['input_scope'])


class LiurenNineMethodsTests(unittest.TestCase):
    def test_all_nine_method_rules_fire_across_golden_cases(self):
        cases = run_cases(domain='liuren')
        self.assertEqual(len(cases), 11)
        seen = set()
        for case in cases:
            rules = case['rule_ids']
            self.assertEqual(rules[:3], LIUREN_STRUCTURAL_RULES, case['id'])
            self.assertEqual(len(rules), 4, case['id'])
            self.assertIn(rules[3], set(LIUREN_METHOD_RULES.values()),
                          case['id'])
            seen.add(rules[3])
        self.assertEqual(seen, set(LIUREN_METHOD_RULES.values()))

    def test_each_golden_method_matches_its_rule_id(self):
        from tianji_kb.operations.liuren_chart import chart as liuren_chart
        cases = {
            'liuren.zeike': ('雨水', '甲子', '丑', '贼克'),
            'liuren.biyong': ('雨水', '甲子', '子', '比用'),
            'liuren.shehai': ('雨水', '丁卯', '丑', '涉害'),
            'liuren.yaoke': ('雨水', '丙寅', '寅', '遥克'),
            'liuren.maoxing': ('雨水', '己巳', '戌', '昴星'),
            'liuren.bieze': ('雨水', '戊辰', '戌', '别责'),
            'liuren.bazhuan': ('雨水', '丁未', '子', '八专'),
            'liuren.fuyin': ('雨水', '甲子', '亥', '伏吟'),
            'liuren.fanyin': ('雨水', '甲子', '巳', '返吟'),
        }
        for case_id, (term, day, hour, method) in cases.items():
            output = liuren_chart(term, day, hour)
            self.assertEqual(output['result']['method'], method, case_id)
            self.assertEqual(len(output['result']['transmissions']), 3,
                             case_id)
            self.assertEqual(output['trace'][-1]['rule_id'],
                             LIUREN_METHOD_RULES[method], case_id)

    def test_engine_datetime_path_fires_a_method_rule(self):
        raw = execute('liuren', {'value': '2000-01-07T12:00:00+08:00'})
        self.assertEqual(raw['variant'],
                         'daquan-nine-methods-lodged-stems-v1')
        self.assertTrue(raw['deterministic'])
        self.assertEqual([s['rule_id'] for s in raw['trace']][:3],
                         LIUREN_STRUCTURAL_RULES)
        self.assertIn(raw['trace'][-1]['rule_id'],
                      set(LIUREN_METHOD_RULES.values()))
        self.assertEqual(raw['trace'][-1]['rule_id'],
                         LIUREN_METHOD_RULES[raw['result']['method']])
        self.assertEqual(len(raw['result']['transmissions']), 3)

    def test_no_noble_generals_or_fortune_ride_on_transmissions(self):
        raw = execute('liuren', {'value': '2000-01-07T12:00:00+08:00'})
        chart = raw['result']
        keys = {k for k, _ in _walk(chart)}
        self.assertNotIn('noble', keys)
        self.assertNotIn('天将', keys)
        self.assertTrue(any('天将未实现' in line
                            for line in chart['limitations']))


def _walk(value):
    if isinstance(value, dict):
        for key, item in value.items():
            yield key, item
            yield from _walk(item)
    elif isinstance(value, list):
        for item in value:
            yield from _walk(item)


if __name__ == '__main__':
    unittest.main()
