"""TJ-0424 Yijing wiring lock-in: the remaining 4 derived-transform rules.

Determination (by execution evidence, 2026-11-25): the adjudication list
calls for "the remaining 4 Yijing rules" without naming them. The registered
phase2 contract maps its 5 rules to phase1 twins 1:1 (structure<->r001
compose, change<->r002, opposite<->r003, inverse<->r004, nuclear<->r005),
so the remaining 4 are the four derived transforms -- change, opposite,
inverse, nuclear -- beyond the base structure/composition that a chart
already establishes. All 4 fire on every chart() call through the same
dynamic rule-ID construction ('yijing.phase2.'+rule in yijing_chart.py)
that literal grep cannot see: only 'yijing.phase2.structure' occurs
literally in src (1x); the other four IDs occur 0x literally.

Scope: deterministic six-line structure only. No interpretation is
compiled; r006 (descriptive_only textual exception) is not implemented
and not wired -- the chart still computes the structural nuclear for
Qian/Kun and records the exception as a scope note only.
"""
import unittest

from tianji_kb.engine import execute
from tianji_kb.golden import run_cases
from tianji_kb.operations.yijing import transform
from tianji_kb.operations.yijing_chart import chart
from tianji_kb.resolver import EvidenceResolver

# Exact trace order of a chart() call: structure first, then the loop
# order opposite / inverse / nuclear / change (yijing_chart.py).
PHASE2_RULES = [
    'yijing.phase2.structure',
    'yijing.phase2.opposite',
    'yijing.phase2.inverse',
    'yijing.phase2.nuclear',
    'yijing.phase2.change',
]

# Independent pin of the operation -> phase2 rule mapping (NOT imported
# from operations.yijing_chart, so the test does not merely agree with
# itself). 'structure' has no transform operation: it is the base
# hexagram lookup.
OPERATION_RULES = {
    'change': 'yijing.phase2.change',
    'opposite': 'yijing.phase2.opposite',
    'inverse': 'yijing.phase2.inverse',
    'nuclear': 'yijing.phase2.nuclear',
}

# Independent pin of the phase1 <-> phase2 twin mapping (registered
# contract phase1_rule_refs; the phase1 rule IDs never occur in a trace).
PHASE1_TWINS = {
    'yijing.rule.r001': 'yijing.phase2.structure',
    'yijing.rule.r002': 'yijing.phase2.change',
    'yijing.rule.r003': 'yijing.phase2.opposite',
    'yijing.rule.r004': 'yijing.phase2.inverse',
    'yijing.rule.r005': 'yijing.phase2.nuclear',
}

# Hand-derived hexagram numbers for the three Golden inputs (checked
# against the independent relations table, not copied from expectations):
# Qian 111111 L1 -> Gou 44; Tai 111000 L1 -> Sheng 46; Zhun 100010.
GOLDEN_NUMBERS = {
    'yijing.qian-first-change': {'original': 1, 'opposite': 2, 'inverse': 1,
                                 'nuclear': 1, 'change': 44},
    'yijing.tai-relations': {'original': 11, 'opposite': 12, 'inverse': 12,
                             'nuclear': 54, 'change': 46},
    'yijing.zhun-nuclear': {'original': 3, 'opposite': 50, 'inverse': 4,
                            'nuclear': 23, 'change': 3},
}


class YijingFourDerivedRulesTests(unittest.TestCase):
    def test_all_five_phase2_rules_fire_in_every_golden_case(self):
        cases = run_cases(domain='yijing')
        self.assertEqual(len(cases), 3)
        self.assertEqual({c['id'] for c in cases}, set(GOLDEN_NUMBERS))
        for case in cases:
            self.assertEqual(case['rule_ids'], PHASE2_RULES, case['id'])

    def test_chart_trace_order_and_golden_numbers(self):
        inputs = {
            'yijing.qian-first-change': ('111111', (1,)),
            'yijing.tai-relations': ('111000', (1,)),
            'yijing.zhun-nuclear': ('100010', ()),
        }
        for case_id, (bits, lines) in inputs.items():
            with self.subTest(case=case_id):
                output = chart(bits, lines)
                self.assertEqual(output['variant'],
                                 'bottom-up-six-lines-v1')
                self.assertTrue(output['deterministic'])
                self.assertEqual([s['rule_id'] for s in output['trace']],
                                 PHASE2_RULES)
                for key, number in GOLDEN_NUMBERS[case_id].items():
                    self.assertEqual(output['result'][key]['number'],
                                     number, (case_id, key))

    def test_engine_public_path_fires_all_five_rules(self):
        raw = execute('yijing', {'bits': '111000', 'changing_lines': [1]})
        self.assertEqual(raw['variant'], 'bottom-up-six-lines-v1')
        self.assertTrue(raw['deterministic'])
        self.assertEqual(raw['mode'], 'production')
        self.assertEqual([s['rule_id'] for s in raw['trace']], PHASE2_RULES)
        self.assertEqual(raw['result']['original']['number'], 11)
        self.assertEqual(raw['result']['change']['number'], 46)

    def test_registered_contract_binds_each_phase2_rule_to_its_phase1_twin(self):
        resolver = EvidenceResolver()
        for phase1_id, phase2_id in PHASE1_TWINS.items():
            with self.subTest(rule=phase2_id):
                rule = resolver.rule(phase2_id)
                self.assertEqual(rule['phase1_rule_refs'], [phase1_id])
                self.assertEqual(rule['execution_status'], 'executable')
                self.assertEqual(rule['validation_status'], 'validated')
                self.assertEqual(rule['golden_case_ids'],
                                 ['yijing.qian-first-change',
                                  'yijing.tai-relations',
                                  'yijing.zhun-nuclear'])

    def test_each_derived_operation_matches_its_rule_id(self):
        # Tai 111000 hand-derived bit strings; the trace step for each
        # operation carries the result of that exact transform.
        bits = '111000'
        expected_bits = {
            'opposite': '000111',
            'inverse': '000111',
            'nuclear': '110100',
            'change': '011000',
        }
        output = chart(bits, (1,))
        for operation, rule_id in OPERATION_RULES.items():
            with self.subTest(operation=operation):
                self.assertEqual(transform(bits, operation)
                                 if operation != 'change' else
                                 transform(bits, operation, [1]),
                                 expected_bits[operation])
                step = next(s for s in output['trace']
                            if s['rule_id'] == rule_id)
                self.assertEqual(step['output']['binary'],
                                 expected_bits[operation])

    def test_transform_involutions_and_nuclear_slice(self):
        for bits in ('111000', '100010', '111111', '000000', '010101'):
            with self.subTest(bits=bits):
                self.assertEqual(transform(transform(bits, 'opposite'),
                                          'opposite'), bits)
                self.assertEqual(transform(transform(bits, 'inverse'),
                                          'inverse'), bits)
                self.assertEqual(transform(bits, 'nuclear'),
                                 bits[1:4] + bits[2:5])
                self.assertEqual(transform(transform(bits, 'change', [1, 3]),
                                          'change', [1, 3]), bits)


class YijingCompositionAndExceptionTests(unittest.TestCase):
    def test_composition_is_the_trigram_lookup_not_a_separate_step(self):
        # r001 (compose): the two trigrams are split out of the bit
        # string by foundations.hexagram and looked up -- Tai 111000 is
        # lower Qian + upper Kun. transform('compose') itself is the
        # identity on the already-concatenated bit string, so there is
        # no separate composition computation to dispatch; the rule's
        # computation is the structure trace step.
        output = chart('111000', (1,))
        self.assertEqual(output['result']['original']['lower'], '乾')
        self.assertEqual(output['result']['original']['upper'], '坤')
        self.assertEqual(transform('111000', 'compose'), '111000')
        self.assertEqual([s['rule_id'] for s in output['trace']],
                         PHASE2_RULES)

    def test_qian_kun_exception_is_a_scope_note_not_a_suppressed_rule(self):
        # r006 is descriptive_only: no rule ID for it ever fires, and
        # the structural nuclear is still computed for Qian and Kun --
        # the textual exception does not rewrite six-line mathematics.
        for bits, number in (('111111', 1), ('000000', 2)):
            with self.subTest(bits=bits):
                output = chart(bits)
                self.assertEqual([s['rule_id'] for s in output['trace']],
                                 PHASE2_RULES)
                self.assertEqual(output['result']['nuclear']['number'],
                                 number)
                self.assertIn('乾坤无互', output['result']['nuclear_scope'])

    def test_no_interpretation_rides_on_the_chart(self):
        output = chart('111000', (1,))
        self.assertEqual(sorted(output['result']),
                         ['change', 'inverse', 'nuclear', 'nuclear_scope',
                          'opposite', 'original'])
        self.assertNotIn('吉凶', str(output['result']))
        self.assertNotIn('断语', str(output['result']))


if __name__ == '__main__':
    unittest.main()
