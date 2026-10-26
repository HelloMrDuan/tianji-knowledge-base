"""TJ-013.3 phase 1 (xiyong readable hints) SEALED tests: real chart end to end.

Offline acceptance ONLY (machine-assembled sealed data tree), following
the test_tj0132_conflict_presentation_sealed precedent. This file is
deliberately NOT named in .github/workflows/validate.yml: the bounded
strength adjudication needs the sealed Canonical foundations, which a
public checkout does not contain. The public companion file
(test_tj0133_readable_hints.py) feeds the renderer synthetic strength
statements and must never be cited as evidence for the real strength
verdicts verified here.
"""
import json
from pathlib import Path
import unittest

from tianji_kb.bazi_adjudication import ADJUDICATION_VARIANT
from tianji_kb.bazi_bingyao import VARIANT as BINGYAO_VARIANT
from tianji_kb.bazi_conflict_presentation import (
    VARIANT as CONFLICT_VARIANT)
from tianji_kb.bazi_tiaohou import VARIANT as TIAOHOU_VARIANT
from tianji_kb.bazi_xiyong_readable import VARIANT
from tianji_kb.calendar_tz import calendar_for_zone
from tianji_kb.engine import execute
from tianji_kb.operations.bazi_chart import chart

ROOT = Path(__file__).resolve().parents[1]
GOLDEN = json.loads(
    (ROOT / 'tests/golden_tj0133_readable_hints.json').read_text('utf-8'))
CASES = {case['id']: case for case in GOLDEN['cases']}

ALL_VARIANTS = dict(strength_variant=ADJUDICATION_VARIANT,
                    tiaohou_variant=TIAOHOU_VARIANT,
                    bingyao_variant=BINGYAO_VARIANT,
                    conflict_variant=CONFLICT_VARIANT,
                    readable_variant=VARIANT)

STEMS = set('甲乙丙丁戊己庚辛壬癸')


def _run(case):
    return chart(*case['pillars'], **ALL_VARIANTS)


class RealChartEndToEndTests(unittest.TestCase):
    def test_source_birth_recomputes_the_recorded_pillars(self):
        for case in GOLDEN['cases']:
            with self.subTest(case=case['id']):
                birth = case['source_birth']
                cal = calendar_for_zone(birth['value'], birth['zone'])
                self.assertEqual(
                    [cal['year_ganzhi'], cal['month_ganzhi'],
                     cal['day_ganzhi'], cal['hour_ganzhi']],
                    case['pillars'])

    def test_golden_cases_through_real_chart(self):
        for case in GOLDEN['cases']:
            with self.subTest(case=case['id']):
                out = _run(case)
                result = out['result']
                # The engine's own ten-god facts must equal the golden
                # transcription (hand-derived from the pillars).
                engine_gods = [
                    {'pillar': row['pillar'], 'stem': row['stem'],
                     'ten_god': row['ten_god']}
                    for row in result['stem_ten_gods']
                    if row['pillar'] != 'day']
                self.assertEqual(
                    engine_gods, case['facts']['bingyao']['visible_gods'])
                # Strength: the REAL bounded adjudication verdict,
                # including the matched predicate and its condition keys.
                strength = result['strength_assessment']
                expected_s = case['expected_strength']
                self.assertEqual(strength['classification'],
                                 expected_s['classification'])
                self.assertEqual(strength['decision_status'],
                                 expected_s['decision_status'])
                if expected_s['sufficient_predicate'] is not None:
                    why = strength['why_not_indeterminate']
                    self.assertEqual(why.get('sufficient_rule'),
                                     expected_s['sufficient_rule'])
                    if expected_s['sufficient_rule'] is None:
                        self.assertEqual(
                            why.get('sufficient_predicate'),
                            expected_s['sufficient_predicate'])
                    self.assertEqual(
                        [row['condition'] for row in why['conditions']],
                        expected_s['conditions'])
                    self.assertTrue(
                        all(row['met'] for row in why['conditions']))
                else:
                    self.assertIsNone(strength['why_not_indeterminate'])
                # The presentation over the REAL statements.
                presentation = result['conflict_presentation']
                self.assertEqual(presentation['status'],
                                 case['expected_presentation_status'])
                # The readable hints over the REAL four objects must
                # equal the hand-written golden text exactly.
                hints = result['readable_hints']
                self.assertEqual(hints['variant'], VARIANT)
                self.assertEqual(hints['day_master'], case['day_master'])
                sections = {s['system']: s for s in hints['sections']}
                for system, expected in \
                        case['expected_sections'].items():
                    self.assertEqual(sections[system]['status'],
                                     expected['status'],
                                     f"{case['id']}:{system}")
                    self.assertEqual(
                        sections[system]['lines'],
                        [line['text'] for line in expected['lines']],
                        f"{case['id']}:{system}")
                # Text-vs-facts closure over the REAL input objects:
                # every stem named in any line comes from this chart's
                # stems or from the tiaohou entry statement itself
                # (an entry pick is a fact of the reviewed entry even
                # when the chart does not contain the stem).
                chart_stems = {g[0] for g in case['pillars']}
                for pillar in result['pillars']:
                    chart_stems.update(
                        item['stem']
                        for item in pillar['branch']['hidden_stems'])
                real_tiaohou = result['tiaohou_assessment']
                for item in real_tiaohou.get('sequence') or []:
                    chart_stems.add(item['stem'])
                for branch in real_tiaohou.get('branches') or []:
                    for item in branch.get('sequence') or []:
                        chart_stems.add(item['stem'])
                for section in hints['sections']:
                    for line in section['lines']:
                        self.assertLessEqual(set(line) & STEMS,
                                             chart_stems,
                                             f"{case['id']}: {line}")
                self.assertTrue(out['research_only'])
                self.assertFalse(
                    out['interpretation_contract']['ai_may_explain'])

    def test_default_chart_has_no_hints(self):
        out = chart('戊戌', '庚申', '甲子', '甲戌')
        for key in ('tiaohou_assessment', 'bingyao_assessment',
                    'conflict_presentation', 'readable_hints'):
            self.assertNotIn(key, out['result'])

    def test_presentation_without_readable_request_has_no_hints(self):
        case = CASES['support-first-pick-is-medicine']
        variants = dict(ALL_VARIANTS)
        del variants['readable_variant']
        out = chart(*case['pillars'], **variants)
        self.assertIn('conflict_presentation', out['result'])
        self.assertNotIn('readable_hints', out['result'])

    def test_engine_research_mode_end_to_end(self):
        case = CASES['conflict-first-pick-is-disease']
        inputs = {'year_ganzhi': case['pillars'][0],
                  'month_ganzhi': case['pillars'][1],
                  'day_ganzhi': case['pillars'][2],
                  'hour_ganzhi': case['pillars'][3], **ALL_VARIANTS}
        out = execute('bazi', inputs, allow_research=True)
        hints = out['result']['readable_hints']
        sections = {s['system']: s for s in hints['sections']}
        self.assertEqual(
            sections['conflict_presentation']['status'],
            'presented_with_conflicts')
        self.assertEqual(out['mode'], 'research')


if __name__ == '__main__':
    unittest.main()
