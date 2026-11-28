"""TJ-0426 Lane 5 (O-04): Yijing reading layer — excerpts + abstain gate.

Local tests run WITHOUT data/: the reading functions take an injected
corpus, and the fixture corpus below uses clearly-labelled synthetic
texts (never presented as classical quotations). The data-gated tests
(skipUnless the sealed classic core exists) replay the 64-hexagram /
384-line inventory, the 用九·用六 special uses, and the 4096 change
masks against the real corpus. The 4096-mask reversibility check
itself is pure (transform only) and runs locally.
"""
import unittest
from itertools import product
from pathlib import Path

from tianji_kb.operations.yijing import transform
from tianji_kb.operations.yijing_reading import (
    READING_RULE_SLOTS, VARIANT, YIJING_GAPS, candidate_texts,
    corpus_inventory, load_classic_corpus, reading,
)

ROOT = Path(__file__).resolve().parents[1]
CORE_FILE = ROOT / 'data/canonical/yijing/zhouyi_classic_core.json'
RELATIONS_FILE = ROOT / 'data/canonical/yijing/hexagram_relations_v1.json'
HAS_DATA = CORE_FILE.exists() and RELATIONS_FILE.exists()

# Synthetic fixture corpus: obviously non-classical labels, so no
# fixture string can ever be mistaken for a classical quotation.
FIXTURE_CORPUS = {
    '111111': {'judgment': 'FIXTURE-JUDGMENT-QIAN',
               'lines': {i: 'FIXTURE-QIAN-LINE-%d' % i for i in range(1, 7)},
               'special_use': {'position': '用九', 'text': 'FIXTURE-YONGJIU'}},
    '011111': {'judgment': 'FIXTURE-JUDGMENT-GOU',
               'lines': {i: 'FIXTURE-GOU-LINE-%d' % i for i in range(1, 7)},
               'special_use': None},
}


class YijingReadingLocalTests(unittest.TestCase):
    def test_candidate_texts_select_judgment_and_moving_lines(self):
        excerpts = candidate_texts('111111', (1,), FIXTURE_CORPUS)
        self.assertEqual(excerpts['variant'], VARIANT)
        self.assertEqual(excerpts['kind'], '原文摘录，非占断结论')
        self.assertEqual(excerpts['original_judgment'], 'FIXTURE-JUDGMENT-QIAN')
        self.assertEqual(excerpts['moving_line_statements'], {1: 'FIXTURE-QIAN-LINE-1'})
        # 乾初爻动 -> 姤 (011111)。
        self.assertEqual(excerpts['changed_bits'], '011111')
        self.assertEqual(excerpts['changed_judgment'], 'FIXTURE-JUDGMENT-GOU')
        self.assertTrue(excerpts['special_use_present'])
        self.assertIsNone(excerpts['verdict'])
        self.assertIsNone(excerpts['determination'])

    def test_no_moving_line_returns_judgment_only(self):
        excerpts = candidate_texts('111111', (), FIXTURE_CORPUS)
        self.assertEqual(excerpts['moving_line_statements'], {})
        self.assertEqual(excerpts['changed_bits'], '111111')
        self.assertEqual(excerpts['changed_judgment'], 'FIXTURE-JUDGMENT-QIAN')

    def test_reading_always_abstains(self):
        for bits, lines in (('111111', (1,)), ('111111', ()), ('011111', (1,))):
            with self.subTest(bits=bits, lines=lines):
                result = reading(bits, lines, FIXTURE_CORPUS)
                self.assertEqual(result['status'], 'abstain_unregistered_reading_rule')
                self.assertIsNone(result['verdict'])
                self.assertIsNone(result['determination'])
                self.assertTrue(result['research_only'])
                self.assertFalse(result['public'])
                self.assertFalse(result['ai'])
                self.assertEqual(len(result['gaps']), len(READING_RULE_SLOTS))
                self.assertTrue(all(gap.startswith('O-04') for gap in result['gaps']))
                self.assertEqual(result['excerpts']['original_bits'], bits)

    def test_all_reading_rule_slots_are_unregistered(self):
        self.assertTrue(all(slot['status'] == 'unregistered'
                            for slot in READING_RULE_SLOTS.values()))
        self.assertEqual(set(READING_RULE_SLOTS),
                         {'no_moving_line', 'single_moving_line', 'multiple_moving_lines',
                          'all_lines_moving', 'qian_kun_special_use'})
        self.assertEqual(YIJING_GAPS['reading_rules']['status'], 'gap')

    def test_corpus_is_required_and_inputs_are_validated(self):
        with self.assertRaises(ValueError):
            candidate_texts('111111', (1,))
        with self.assertRaises(ValueError):
            candidate_texts('000000', (), FIXTURE_CORPUS)
        for bits, lines in [('11111', ()), ('11111x', ()), ('111111', (0,)),
                            ('111111', (1, 1)), ('111111', (True,)), ('111111', (7,))]:
            with self.assertRaises(ValueError, msg=(bits, lines)):
                candidate_texts(bits, lines, FIXTURE_CORPUS)

    def test_corpus_inventory_counts(self):
        inventory = corpus_inventory(FIXTURE_CORPUS)
        self.assertEqual(inventory['hexagrams'], 2)
        self.assertEqual(inventory['line_statements'], 12)
        self.assertEqual(inventory['special_use_hexagrams'], ['111111'])
        with self.assertRaises(ValueError):
            corpus_inventory({})

    def test_all_4096_change_masks_are_reversible(self):
        # Pure transform regression (no data needed): every 6-line
        # pattern under every change mask is reversible and flips
        # exactly the moving lines.
        for values in product('01', repeat=6):
            bits = ''.join(values)
            for mask in product((False, True), repeat=6):
                lines = [i + 1 for i, x in enumerate(mask) if x]
                changed = transform(bits, 'change', lines)
                self.assertEqual(transform(changed, 'change', lines), bits)
                self.assertEqual(sum(a != b for a, b in zip(bits, changed)), len(lines))


@unittest.skipUnless(HAS_DATA, 'sealed yijing classic core absent (public checkout)')
class YijingReadingSealedTests(unittest.TestCase):
    def test_classic_core_inventory_and_special_uses(self):
        corpus = load_classic_corpus()
        inventory = corpus_inventory(corpus)
        self.assertEqual(inventory['hexagrams'], 64)
        self.assertEqual(inventory['line_statements'], 384)
        self.assertEqual(set(inventory['special_use_hexagrams']), {'111111', '000000'})
        from tianji_kb.knowledge import read_json
        core = read_json(CORE_FILE)
        self.assertEqual(core['classic_statement_count'], 386)
        self.assertEqual(sum(len(x['lines']) for x in core['records']), 384)

    def test_real_corpus_excerpts_still_abstain(self):
        corpus = load_classic_corpus()
        excerpts = candidate_texts('111111', (1,), corpus)
        self.assertTrue(excerpts['original_judgment'])
        self.assertTrue(excerpts['moving_line_statements'][1])
        self.assertTrue(excerpts['changed_judgment'])
        result = reading('111111', (1,), corpus)
        self.assertEqual(result['status'], 'abstain_unregistered_reading_rule')
        self.assertIsNone(result['verdict'])

    def test_golden_numbers_against_real_relations(self):
        from tianji_kb.golden import run_cases
        self.assertEqual(len(run_cases(domain='yijing')), 3)


if __name__ == '__main__':
    unittest.main()
