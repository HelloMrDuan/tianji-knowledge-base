"""TJ-012.3 Slice B （杂气选格陈述） public contract tests.

Public-safe by design: the registered quotes vs Golden transcription,
the pure selection lookup over synthetic fact inputs, forged-trace
rejection and the public-projection strip need no sealed data.
Verbatim equality of every registered quote against the pinned
snapshot texts themselves, and real-chart coverage of the Golden
cases, live only in the sealed companion
test_tj012_zaqi_selection_sealed.py (offline acceptance, NOT public
CI), following the test_tj012_luren_route precedent.

The statement is a branch-level selection statement only: for
miscellaneous months （辰戌丑未） it states the Ren （原注） branch
procedure outcome and juxtaposes the registered Sanming 杂气格 school
conflict; it never names a pattern, and every other determination
field stays None, which these tests sweep across the constructed
domain.
"""
import copy
import json
from pathlib import Path
import unittest

from tianji_kb.bazi_pattern import (
    MISCELLANEOUS_BRANCHES, PATTERN_VARIANT, ZAQI_ADJUDICATION_NOTES,
    ZAQI_CONFLICT_POINTS, ZAQI_LIMITATIONS, ZAQI_QUOTES,
    ZAQI_SELECTION_VARIANT, month_pattern_zaqi, zaqi_selection_lookup,
)
from tianji_kb.engine import execute
from tianji_kb.public_projection import project_execution

ROOT = Path(__file__).resolve().parents[1]
GOLDEN = json.loads(
    (ROOT / 'tests/golden_tj012_zaqi_selection.json').read_text('utf-8'))
STEMS = '甲乙丙丁戊己庚辛壬癸'
BRANCHES = '子丑寅卯辰巳午未申酉戌亥'
VERDICT_KEYS = {'score', 'rating', 'fortune', 'fortune_verdict',
                'auspicious', 'inauspicious', 'luck', '吉凶', '评分',
                '喜用神', '用神', 'useful_god', 'favorable_god',
                'pattern_name', 'true_false', 'success_failure'}

# Executed-fact shapes, hand-written for the pure lookup: the month
# branch hidden stems in canonical order with their ten gods relative
# to the stated day master (the same facts the sealed tests recompute
# on real charts).
CHOU_FOR_JI = [{'stem': '己', 'ten_god': '比肩'},
               {'stem': '癸', 'ten_god': '偏财'},
               {'stem': '辛', 'ten_god': '食神'}]
XU_FOR_WU = [{'stem': '戊', 'ten_god': '比肩'},
             {'stem': '辛', 'ten_god': '伤官'},
             {'stem': '丁', 'ten_god': '正印'}]
XU_FOR_REN = [{'stem': '戊', 'ten_god': '七杀'},
              {'stem': '辛', 'ten_god': '正印'},
              {'stem': '丁', 'ten_god': '正财'}]
WEI_FOR_JI = [{'stem': '己', 'ten_god': '比肩'},
              {'stem': '丁', 'ten_god': '偏印'},
              {'stem': '乙', 'ten_god': '七杀'}]


def _keys(node):
    if isinstance(node, dict):
        for key, value in node.items():
            yield key
            yield from _keys(value)
    elif isinstance(node, list):
        for item in node:
            yield from _keys(item)


class TranscriptionTests(unittest.TestCase):
    def test_quotes_match_golden_transcription(self):
        self.assertEqual(ZAQI_SELECTION_VARIANT, GOLDEN['variant'])
        golden_quotes = {q['id']: q for q in GOLDEN['quotes']}
        self.assertEqual({q['id'] for q in ZAQI_QUOTES}, set(golden_quotes))
        for quote in ZAQI_QUOTES:
            want = golden_quotes[quote['id']]
            self.assertEqual(quote['quote'], want['quote'])
            self.assertEqual(quote['locator'], want['locator'])
            self.assertEqual(quote['source_id'], want['source_id'])
            self.assertEqual(quote['layer'], want['layer'])
            loc = quote['locator']
            self.assertEqual(loc['char_end'] - loc['char_start'],
                             len(quote['quote']),
                             'locator span must equal the verbatim quote')

    def test_notes_and_conflict_points_match_golden(self):
        self.assertEqual(list(ZAQI_ADJUDICATION_NOTES),
                         GOLDEN['adjudication_notes'])
        self.assertEqual(list(ZAQI_CONFLICT_POINTS),
                         GOLDEN['conflict_points'])


class LookupTests(unittest.TestCase):
    def test_wuji_exposed_single(self):
        out = zaqi_selection_lookup(
            '己', '丑', CHOU_FOR_JI,
            [{'stem': '癸', 'ten_god': '偏财', 'visible_pillars': ['month']}])
        self.assertEqual(out['status'], 'stated')
        self.assertEqual(out['arm'], 'wuji_exposed_renyuan')
        self.assertIsNone(out['abstention_reason'])
        self.assertEqual(
            [c['stem'] for c in out['selection']['selected_candidates']],
            ['癸'])
        self.assertEqual(out['selection']['basis'], 'exposed_renyuan')
        self.assertIsNone(out['selection']['pattern_determination'])
        self.assertTrue(out['conflict']['conflict_present'])

    def test_wuji_two_exposed_kept_in_hidden_order(self):
        out = zaqi_selection_lookup(
            '己', '未', WEI_FOR_JI,
            [{'stem': '乙', 'ten_god': '七杀', 'visible_pillars': ['month']},
             {'stem': '丁', 'ten_god': '偏印', 'visible_pillars': ['hour']}])
        self.assertEqual(out['status'], 'stated')
        self.assertEqual([c['stem'] for c in out['exposed_renyuan']],
                         ['丁', '乙'], 'hidden order, not input order')
        self.assertEqual(
            [c['stem'] for c in out['selection']['selected_candidates']],
            ['丁', '乙'], 'both listed, never one chosen over the other')

    def test_wuji_no_exposed_abstains(self):
        out = zaqi_selection_lookup('戊', '戌', XU_FOR_WU, [])
        self.assertEqual(out['status'], 'abstained')
        self.assertEqual(out['abstention_reason'], 'no_exposed_renyuan')
        self.assertEqual(out['arm'], 'wuji_exposed_renyuan')
        self.assertIsNone(out['selection'])
        self.assertTrue(out['conflict']['conflict_present'])

    def test_general_arm_ignores_exposure(self):
        with_exposure = zaqi_selection_lookup(
            '壬', '戌', XU_FOR_REN,
            [{'stem': '丁', 'ten_god': '正财', 'visible_pillars': ['hour']}])
        without = zaqi_selection_lookup('壬', '戌', XU_FOR_REN, [])
        for out in (with_exposure, without):
            self.assertEqual(out['status'], 'stated')
            self.assertEqual(out['arm'], 'general_tu_unconverted')
            self.assertEqual(out['selection']['basis'], 'original_text_only')
            self.assertEqual(out['selection']['selected_candidates'], [])
            self.assertEqual(
                out['selection']['earth_conversion']['status'],
                'unadjudicated')
            self.assertIsNone(
                out['selection']['earth_conversion']
                ['converted_pattern_name'])
            self.assertIsNone(
                out['selection']['earth_conversion']['converted_ten_god'])
        self.assertEqual(len(with_exposure['exposed_renyuan']), 1)
        self.assertEqual(without['exposed_renyuan'], [])

    def test_non_miscellaneous_not_applicable(self):
        for branch in BRANCHES:
            if branch in MISCELLANEOUS_BRANCHES:
                continue
            with self.subTest(branch=branch):
                out = zaqi_selection_lookup('甲', branch, [], [])
                self.assertEqual(out['status'], 'not_applicable')
                self.assertFalse(out['miscellaneous_month'])
                self.assertIsNone(out['arm'])
                self.assertIsNone(out['selection'])
                self.assertFalse(out['conflict']['conflict_present'])
                self.assertEqual(out['conflict']['case_refs'], [])

    def test_conflict_block_shape_on_miscellaneous(self):
        out = zaqi_selection_lookup('戊', '戌', XU_FOR_WU, [])
        conflict = out['conflict']
        self.assertEqual(conflict['branch'], 'sanming_zaqi_pattern')
        self.assertEqual([r['id'] for r in conflict['case_refs']],
                         ['sanming.zaqi_case_rilu',
                          'sanming.zaqi_poem_nvming'])
        self.assertEqual(conflict['points'], list(ZAQI_CONFLICT_POINTS))

    def test_determination_stays_none_across_domain(self):
        inputs = [('己', '丑', CHOU_FOR_JI), ('戊', '戌', XU_FOR_WU),
                  ('壬', '戌', XU_FOR_REN), ('己', '未', WEI_FOR_JI)]
        for day, branch, hidden in inputs:
            variants = [[], [{'stem': hidden[1]['stem'],
                               'ten_god': hidden[1]['ten_god'],
                               'visible_pillars': ['year']}]]
            for exposed in variants:
                out = zaqi_selection_lookup(day, branch, hidden, exposed)
                det = out['determination']
                self.assertEqual(det['status'], 'unresolved')
                self.assertIsNone(det['pattern'])
                self.assertIsNone(det['true_false'])
                self.assertIsNone(det['success_failure'])
                self.assertIsNone(det['useful_god'])
                self.assertFalse(out['qualified_for_determination'])
                self.assertTrue(out['research_only'])
                self.assertFalse(out['public_enabled'])
                self.assertFalse(out['ai_enabled'])
                self.assertEqual(out['evidence_binding'],
                                 'pending_phase1_rule_registration')
                self.assertEqual(out['adjudication_notes'],
                                 list(ZAQI_ADJUDICATION_NOTES))
                self.assertEqual(out['scope_limits'],
                                 list(ZAQI_LIMITATIONS))
                leaked = VERDICT_KEYS & set(_keys(out))
                self.assertLessEqual(
                    leaked, {'true_false', 'success_failure', 'useful_god'},
                    'no verdict/score/useful-god key may appear beyond '
                    'the pinned-None determination fields')
        for stem in STEMS:
            out = zaqi_selection_lookup(stem, '寅', [], [])
            self.assertEqual(out['status'], 'not_applicable')

    def test_lookup_fails_closed(self):
        with self.assertRaises(ValueError):
            zaqi_selection_lookup('猫', '丑', CHOU_FOR_JI, [])
        with self.assertRaises(ValueError):
            zaqi_selection_lookup('己', '猫', CHOU_FOR_JI, [])
        with self.assertRaises(ValueError):
            zaqi_selection_lookup('己', '丑', [], [])  # misc needs facts
        with self.assertRaises(ValueError):
            zaqi_selection_lookup(  # exposed stem is not a hidden stem
                '己', '丑', CHOU_FOR_JI,
                [{'stem': '庚', 'ten_god': '伤官', 'visible_pillars': ['year']}])
        with self.assertRaises(ValueError):
            zaqi_selection_lookup(  # ten god disagrees with hidden fact
                '己', '丑', CHOU_FOR_JI,
                [{'stem': '癸', 'ten_god': '正财', 'visible_pillars': ['year']}])
        with self.assertRaises(ValueError):
            zaqi_selection_lookup(  # day pillar never counts as exposure
                '己', '丑', CHOU_FOR_JI,
                [{'stem': '癸', 'ten_god': '偏财', 'visible_pillars': ['day']}])
        with self.assertRaises(ValueError):
            zaqi_selection_lookup(  # duplicated hidden stem
                '己', '丑', CHOU_FOR_JI + [CHOU_FOR_JI[0]], [])


class _StubTrace:
    def __init__(self, steps, evidence):
        self.steps = steps
        self.evidence = evidence


def _c1_steps(evidence_ids=('e1', 'e2', 'e3', 'e4')):
    return [
        {'rule_id': 'bazi.phase2.pillars', 'evidence_ids': [evidence_ids[0]],
         'output': {'ganzhi': [['壬', '辰'], ['癸', '丑'], ['己', '未'],
                               ['庚', '午']],
                    'day_master': {'stem': '己'}}},
        {'rule_id': 'bazi.phase2.ten_gods', 'evidence_ids': [evidence_ids[1]],
         'output': [{'pillar': 'year', 'stem': '壬', 'ten_god': '正财'},
                    {'pillar': 'month', 'stem': '癸', 'ten_god': '偏财'},
                    {'pillar': 'day', 'stem': '己', 'ten_god': '日主'},
                    {'pillar': 'hour', 'stem': '庚', 'ten_god': '伤官'}]},
        {'rule_id': 'bazi.phase2.hidden_stems',
         'evidence_ids': [evidence_ids[2]],
         'output': [
             {'pillar': 'year', 'branch': '辰', 'hidden_stems': []},
             {'pillar': 'month', 'branch': '丑',
              'hidden_stems': [{'stem': '己', 'ten_god': '比肩'},
                               {'stem': '癸', 'ten_god': '偏财'},
                               {'stem': '辛', 'ten_god': '食神'}]},
             {'pillar': 'day', 'branch': '未', 'hidden_stems': []},
             {'pillar': 'hour', 'branch': '午', 'hidden_stems': []}]},
        {'rule_id': 'bazi.phase2.hidden_to_visible',
         'evidence_ids': [evidence_ids[3]],
         'output': {'positions': [
             {'hidden_pillar': 'month', 'hidden_stem': '癸',
              'visible_pillars': ['month']}], 'day_stem_excluded': True}},
    ]


class TraceWrapperTests(unittest.TestCase):
    def test_wrapper_consumes_executed_facts(self):
        evidence = {e: object() for e in ('e1', 'e2', 'e3', 'e4')}
        out = month_pattern_zaqi(_StubTrace(_c1_steps(), evidence))
        self.assertEqual(out['status'], 'stated')
        self.assertEqual(out['arm'], 'wuji_exposed_renyuan')
        self.assertEqual([c['stem'] for c in out['exposed_renyuan']], ['癸'])
        self.assertEqual(out['consumed_rule_ids'], [
            'bazi.phase2.pillars', 'bazi.phase2.ten_gods',
            'bazi.phase2.hidden_stems', 'bazi.phase2.hidden_to_visible'])
        self.assertIn('/output/ganzhi/1', out['fact_refs']['month_branch'])

    def test_forged_or_missing_facts_fail_closed(self):
        evidence = {e: object() for e in ('e1', 'e2', 'e3', 'e4')}
        with self.assertRaises(ValueError):
            month_pattern_zaqi(_StubTrace([], {}))
        with self.assertRaises(ValueError):
            month_pattern_zaqi(_StubTrace(_c1_steps(), {}))
        steps = _c1_steps()
        steps[2]['output'][1]['branch'] = '戌'  # hidden vs pillars disagree
        with self.assertRaises(ValueError):
            month_pattern_zaqi(_StubTrace(steps, evidence))
        steps = _c1_steps()
        steps[1]['output'][1]['ten_god'] = '正财'  # ten-god fact disagrees
        with self.assertRaises(ValueError):
            month_pattern_zaqi(_StubTrace(steps, evidence))


class EngineAndProjectionTests(unittest.TestCase):
    def test_engine_requires_explicit_research_mode(self):
        with self.assertRaisesRegex(ValueError, 'research mode'):
            execute('bazi', {'pattern_variant': PATTERN_VARIANT,
                             'year_ganzhi': '壬辰', 'month_ganzhi': '癸丑',
                             'day_ganzhi': '己未', 'hour_ganzhi': '庚午'})

    def test_public_projection_strips_pattern_zaqi(self):
        payload = {
            'domain': 'bazi', 'variant': 'ziping-structural-v1',
            'deterministic': True,
            'result': {'pillars': [],
                       'pattern_zaqi': {'status': 'stated'}},
            'chart': {'pattern_zaqi': {'status': 'abstained'}},
            'evidence': {}, 'rule_matches': [], 'trace': [],
        }
        out = project_execution(copy.deepcopy(payload))
        self.assertNotIn('pattern_zaqi', out['chart'])
        self.assertNotIn('pattern_zaqi', out['result'])


if __name__ == '__main__':
    unittest.main()
