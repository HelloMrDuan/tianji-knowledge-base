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
from tianji_kb.bazi_xiyong_readable import (
    PRESENTATION_STATUS_LABELS,
    STRENGTH_SCOPE_LINE,
    VARIANT)
from tianji_kb.calendar_tz import calendar_for_zone
from tianji_kb.engine import execute
from tianji_kb.operations.bazi_chart import chart
from tianji_kb.public_projection import project_execution
from tianji_kb.scenario_engine import execute_scenario

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

# HOLD-1 (E0398 review): the two real-chart witnesses for the newly
# registered lu/water predicates. Each entry is a REAL birth instant
# (not a synthetic strength statement): the pillars below are the
# hand-verified recomputation of that instant (lu: 1927 is a 丁卯
# year, 立夏已过 so the month is 乙巳, day 丙午, 丙日午时甲午;
# water: 1981 is a 辛酉 year, 大雪已过 so the month is 庚子, day
# 癸酉, 癸日子时壬子) and are asserted against a fresh
# calendar_for_zone recomputation in the test, never trusted blind.
# The condition keys are in register order (FORM_BING_SI /
# S2_FORM_REGISTERS); the expected strength lines are hand-derived
# from those keys plus the renderer's CONDITION_LABELS and line
# format — the same hand-written lines the public renderer test
# pins — never copied from a run's output. Metal has no real-chart
# witness (constructively unsatisfiable, per the S2 register) and
# stays renderer-shape-only in the public test; it is deliberately
# absent here and must not be fabricated.
REAL_WITNESSES = {
    'lu': {
        'birth': '1927-05-12T12:00:00+08:00',
        'zone': 'Asia/Shanghai',
        'pillars': ['丁卯', '乙巳', '丙午', '甲午'],
        'day_master': '丙',
        'sufficient_rule': 'bazi.phase2.strength_lu_visible_support',
        'conditions': ['fire_day_master_bing',
                       'reviewed_lu_command_month',
                       'visible_positions_support_only',
                       'visible_resource_present',
                       'visible_peer_present',
                       'effective_heavy_day_roots',
                       'all_visible_have_reviewed_roots',
                       'no_unresolved_interactions',
                       'hidden_layer_convention_applied'],
        'expected_strength_lines': [
            '旺衰裁定体系：本盘日主旺衰裁定为「强」。',
            '裁定命中的已审充分谓词为「禄月显纯生扶」，其条件全部成立：'
            '日主为火、月支巳为日主禄位、显干位置的作用均为生扶、显干见印、'
            '显干见比劫、日主根均为重根位有效根、显干各有已审根位、'
            '无未决的作用关系、藏干仅作根位事实（治理约定）。',
            STRENGTH_SCOPE_LINE],
    },
    'water': {
        'birth': '1981-12-21T00:30:00+08:00',
        'zone': 'Asia/Shanghai',
        'pillars': ['辛酉', '庚子', '癸酉', '壬子'],
        'day_master': '癸',
        'sufficient_rule':
            'bazi.phase2.strength_pure_generating_support_water',
        'conditions': ['water_day_master',
                       'reviewed_same_element_month_zi',
                       'all_positions_support_only',
                       'visible印_present',
                       'visible比_present',
                       'effective_day_roots_registered',
                       'all_visible_have_registered_roots',
                       'no_unresolved_interactions'],
        'expected_strength_lines': [
            '旺衰裁定体系：本盘日主旺衰裁定为「强」。',
            '裁定命中的已审充分谓词为「水纯生扶」，其条件全部成立：'
            '日主为水、月支子本气与日主同行、全部位置的作用均为生扶、'
            '显干见印、显干见比劫、日主根均为已登记有效根、'
            '显干各有已登记根位、无未决的作用关系。',
            STRENGTH_SCOPE_LINE],
    },
}


def _scan_no_readable_hints(obj, path=''):
    """No readable-hints key or readable strength line anywhere."""
    if isinstance(obj, dict):
        for key, value in obj.items():
            if key == 'readable_hints':
                raise AssertionError('leaked key readable_hints at %s'
                                     % path)
            _scan_no_readable_hints(value, path + '/' + str(key))
    elif isinstance(obj, list):
        for index, value in enumerate(obj):
            _scan_no_readable_hints(value, '%s[%d]' % (path, index))
    elif isinstance(obj, str):
        if '旺衰裁定体系' in obj:
            raise AssertionError('leaked readable line at %s' % path)


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

    def test_real_witness_lu_and_water_end_to_end(self):
        # HOLD-1: the two newly registered predicates (lu r032, water
        # r034) must be proven on REAL charts, not on the synthetic
        # strength statements the public renderer test uses. Each
        # witness runs the full research chain: calendar recomputation
        # -> real chart(ALL_VARIANTS) -> bounded adjudication ->
        # conflict_presentation -> readable_hints, plus the research /
        # public / AI boundary and the no-leak checks.
        for name, witness in REAL_WITNESSES.items():
            with self.subTest(witness=name):
                # 1. The real calendar recomputes the recorded pillars.
                cal = calendar_for_zone(witness['birth'], witness['zone'])
                pillars = [cal['year_ganzhi'], cal['month_ganzhi'],
                           cal['day_ganzhi'], cal['hour_ganzhi']]
                self.assertEqual(pillars, witness['pillars'])
                # 2. The real chart, no injected strength.
                out = chart(*pillars, **ALL_VARIANTS)
                result = out['result']
                # 3. The real bounded adjudication verdict.
                strength = result['strength_assessment']
                self.assertEqual(strength['classification'], 'strong')
                self.assertEqual(
                    strength['decision_status'],
                    'reviewed_sufficient_rule_matched')
                why = strength['why_not_indeterminate']
                self.assertEqual(why.get('sufficient_rule'),
                                 witness['sufficient_rule'])
                # 4. The real conditions, keys in register order, all met.
                self.assertEqual(
                    [row['condition'] for row in why['conditions']],
                    witness['conditions'])
                self.assertTrue(
                    all(row['met'] for row in why['conditions']))
                # 5. The presentation and the readable hints assemble.
                presentation = result['conflict_presentation']
                self.assertIn(presentation['status'],
                              PRESENTATION_STATUS_LABELS)
                hints = result['readable_hints']
                self.assertEqual(hints['variant'], VARIANT)
                self.assertEqual(hints['day_master'],
                                 witness['day_master'])
                sections = {s['system']: s for s in hints['sections']}
                self.assertEqual(
                    sections['strength']['lines'],
                    witness['expected_strength_lines'])
                # 6. Research-only boundary: research on, public/AI off.
                self.assertTrue(out['research_only'])
                self.assertFalse(
                    out['interpretation_contract']['ai_may_explain'])
                self.assertIs(strength.get('research_only'), True)
                self.assertIs(strength.get('public_enabled'), False)
                self.assertIs(strength.get('ai_enabled'), False)
                self.assertIs(hints.get('research_only'), True)
                self.assertIs(hints.get('public_enabled'), False)
                self.assertIs(hints.get('ai_enabled'), False)
                # 7. The default chart path carries no readable hints.
                default_out = chart(*pillars)
                self.assertNotIn('readable_hints',
                                 default_out['result'])
                variants = dict(ALL_VARIANTS)
                del variants['readable_variant']
                out_no_readable = chart(*pillars, **variants)
                self.assertIn('conflict_presentation',
                              out_no_readable['result'])
                self.assertNotIn('readable_hints',
                                 out_no_readable['result'])
                # 8. The public projection never leaks readable hints.
                envelope = execute_scenario(
                    'bazi-profile',
                    {'value': witness['birth'], 'zone': witness['zone']})
                projected = project_execution(envelope)
                _scan_no_readable_hints(projected)

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
