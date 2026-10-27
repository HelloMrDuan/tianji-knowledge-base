"""TJ-013.2 phase 1 (conflict presentation) SEALED tests: real chart end to end.

Offline acceptance ONLY (machine-assembled sealed data tree), following
the test_tj013_bingyao_sealed precedent. This file is deliberately NOT
named in .github/workflows/validate.yml: the bounded strength
adjudication needs the sealed Canonical foundations, which a public
checkout does not contain. The public companion file
(test_tj0132_conflict_presentation.py) feeds the presenter synthetic
strength statements and must never be cited as evidence for the real
strength verdicts verified here.
"""
import json
from pathlib import Path
import unittest

from tianji_kb.bazi_adjudication import ADJUDICATION_VARIANT
from tianji_kb.bazi_bingyao import VARIANT as BINGYAO_VARIANT
from tianji_kb.bazi_conflict_presentation import VARIANT
from tianji_kb.bazi_tiaohou import VARIANT as TIAOHOU_VARIANT
from tianji_kb.calendar_tz import calendar_for_zone
from tianji_kb.engine import execute
from tianji_kb.operations.bazi_chart import chart

ROOT = Path(__file__).resolve().parents[1]
GOLDEN = json.loads(
    (ROOT / 'tests/golden_tj0132_conflict_presentation.json').read_text('utf-8'))
CASES = {case['id']: case for case in GOLDEN['cases']}

ALL_VARIANTS = dict(strength_variant=ADJUDICATION_VARIANT,
                    tiaohou_variant=TIAOHOU_VARIANT,
                    bingyao_variant=BINGYAO_VARIANT,
                    conflict_variant=VARIANT)


def _run(case):
    return chart(*case['pillars'], **ALL_VARIANTS)


class RealChartEndToEndTests(unittest.TestCase):
    def test_source_birth_recomputes_the_recorded_pillars(self):
        # Every golden case binds a real birth instant to its pillars
        # through the reviewed calendar path; no hand-built pillars.
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
                # Strength: the REAL bounded adjudication verdict.
                strength = result['strength_assessment']
                self.assertEqual(strength['classification'],
                                 case['expected_strength']['classification'])
                self.assertEqual(strength['decision_status'],
                                 case['expected_strength']['decision_status'])
                # Tiaohou / bingyao statements against the golden.
                tiaohou = result['tiaohou_assessment']
                expected_t = case['expected_tiaohou']
                self.assertEqual(tiaohou['status'], expected_t['status'])
                if expected_t['status'] == 'matched':
                    self.assertEqual(
                        [{'stem': s['stem'], 'order': s['order'],
                          'presence': s['presence']}
                         for s in tiaohou['sequence']],
                        expected_t['sequence'])
                else:
                    self.assertEqual(tiaohou['reason'], expected_t['reason'])
                bingyao = result['bingyao_assessment']
                expected_b = case['expected_bingyao']
                self.assertEqual(bingyao['status'], expected_b['status'])
                self.assertIsNone(bingyao['determination'])
                self.assertEqual(bingyao['medicine_effect_status'],
                                 'unadjudicated')
                if expected_b['status'] == 'triggered':
                    for key in ('subject', 'disease_candidate',
                                'medicine_candidate'):
                        self.assertEqual(bingyao[key]['gods'], expected_b[key])
                else:
                    self.assertEqual(bingyao['not_triggered_reason'],
                                     expected_b['not_triggered_reason'])
                # The presentation over the REAL statements.
                presentation = result['conflict_presentation']
                expected_p = case['expected_presentation']
                self.assertEqual(presentation['variant'], VARIANT)
                self.assertIsNone(presentation['determination'])
                self.assertEqual(presentation['status'], expected_p['status'])
                systems = {r['system']: r for r in presentation['systems']}
                for system, status in expected_p['systems'].items():
                    self.assertEqual(systems[system]['status'], status,
                                     f'{case["id"]}:{system}')
                # Carried statements are the executed ones, verbatim.
                self.assertEqual(systems['tiaohou']['statement'], tiaohou)
                self.assertEqual(systems['bingyao']['statement'], bingyao)
                self.assertEqual(systems['strength']['statement'], strength)
                relations = {r['stem']: r['kind']
                             for r in presentation['relations']
                             if r['stem'] is not None}
                self.assertEqual(relations, expected_p['relations'])
                pair_map = {r['stem']: r['pair_id']
                            for r in presentation['relations']
                            if r['stem'] is not None}
                self.assertEqual(pair_map, expected_p['relation_pairs'])
                context = [r for r in presentation['relations']
                           if r['kind'] == 'incomparable']
                self.assertEqual(len(context), 1)
                self.assertEqual(context[0]['classification'],
                                 case['expected_strength']['classification'])
                self.assertTrue(out['research_only'])
                self.assertFalse(
                    out['interpretation_contract']['ai_may_explain'])

    def test_default_chart_has_no_presentation(self):
        out = chart('戊戌', '庚申', '甲子', '甲戌')
        for key in ('tiaohou_assessment', 'bingyao_assessment',
                    'conflict_presentation'):
            self.assertNotIn(key, out['result'])

    def test_partial_variant_requests_have_no_presentation(self):
        out = chart('庚子', '己卯', '甲午', '乙丑',
                    tiaohou_variant=TIAOHOU_VARIANT,
                    bingyao_variant=BINGYAO_VARIANT)
        self.assertIn('tiaohou_assessment', out['result'])
        self.assertNotIn('conflict_presentation', out['result'])

    def test_engine_research_mode_end_to_end(self):
        case = CASES['conflict-first-pick-is-disease']
        inputs = {'year_ganzhi': case['pillars'][0],
                  'month_ganzhi': case['pillars'][1],
                  'day_ganzhi': case['pillars'][2],
                  'hour_ganzhi': case['pillars'][3], **ALL_VARIANTS}
        out = execute('bazi', inputs, allow_research=True)
        presentation = out['result']['conflict_presentation']
        self.assertEqual(presentation['status'], 'presented_with_conflicts')
        self.assertEqual(out['mode'], 'research')


if __name__ == '__main__':
    unittest.main()
