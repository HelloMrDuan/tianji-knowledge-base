"""TJ-012.3 D-1 寅月 research-execution link public contract tests (E0385).

Public-safe by design: the gate's trigger / non-entry conditions, the
live 寅月 pilot step, the Jie replay rejection, the silent-drop input
contract (which the chart validation preamble enforces before any
sealed-data load), the composition-level abstentions for uncertain /
non-寅月 pilot results, and the public-projection strip need no sealed
data. Real-chart end-to-end coverage -- the full gate through
research-mode execute("bazi") over all fifteen Golden cases, byte
equality with direct chart composition, the sealed silent-drop
regressions on real charts, the F4 non-contamination check and the
production-API no-leak check -- lives only in the sealed companion
test_tj012_d1_yin_research_link_sealed.py (offline acceptance, NOT
public CI: pattern candidates need the sealed Canonical foundations).

Golden expectations in golden_tj012_d1_yin_research_link.json are
hand-derived from golden_tj012_ren_yin_true.json and
golden_tj012_siling_si_pilot.json (see that file's meta block). No
expected value here was produced by running the implementation.
"""
import copy
import json
import unittest
from pathlib import Path

from tianji_kb import bazi_siling_matrix as matrix
from tianji_kb.bazi_pattern import PATTERN_VARIANT, ren_yin_true_pattern
from tianji_kb.bazi_siling_pilot import yin_siling_pilot
from tianji_kb.bazi_siling_si_pilot import si_siling_pilot
from tianji_kb.operations.bazi_chart import chart
from tianji_kb.public_projection import project_execution
from tianji_kb.scenario_engine import (
    _ren_yin_research_pilot,
    execute_scenario,
    registry,
    ren_yin_research_execution,
)

ROOT = Path(__file__).resolve().parents[1]
GOLDEN = json.loads(
    (ROOT / 'tests/golden_tj012_d1_yin_research_link.json').read_text('utf-8'))
REN_GOLDEN = json.loads(
    (ROOT / 'tests/golden_tj012_ren_yin_true.json').read_text('utf-8'))
SI_GOLDEN = json.loads(
    (ROOT / 'tests/golden_tj012_siling_si_pilot.json').read_text('utf-8'))
CASES = {case['id']: case for case in GOLDEN['cases']}
FORBIDDEN_KEYS = {
    'score', 'scores', 'rating', 'weight', 'weights', 'useful_god',
    'favorable', 'favourable', 'recommended', 'recommendation',
    'verdict', 'combined_verdict', 'final_verdict', 'resolution',
    'resolved_choice', 'preference', 'true_false', 'success_failure',
    'pattern_name', '喜用神', '用神', '喜神', '忌神', '吉凶', '评分',
    '推荐', '权重', '裁决', '真格', '假格', '成格', '破格',
}


def _all_keys(node):
    if isinstance(node, dict):
        for key, value in node.items():
            yield key
            yield from _all_keys(value)
    elif isinstance(node, list):
        for item in node:
            yield from _all_keys(item)


def _jie_facts(case):
    window = GOLDEN['jie_windows'][case['window']]
    facts = {'provider': dict(GOLDEN['provider']),
             'lichun': dict(window['lichun']),
             'next_jie': dict(window['next_jie'])}
    override = case.get('jie_override') or {}
    if override.get('precision_warning'):
        facts['precision_warning'] = True
    return facts


def _pilot_block(status='computed', commander='戊', **over):
    conv = matrix.SILING_CALCULATION_CONVENTION
    version_id = conv['scope']['version_id']
    cell = matrix.SILING_MATRIX[version_id]['寅']
    quote = {row['id']: row for row in matrix.SILING_QUOTES}[
        cell['quotes'][0]]
    block = {
        'variant': 'bazi-siling-yin-pilot-v1',
        'status': status,
        'reason': None,
        'commander': commander if status == 'computed' else None,
        'scope_month_branch': '寅',
        'month_branch': '寅' if status == 'computed' else None,
        'research_only': True, 'public_enabled': False, 'ai_enabled': False,
        'provenance': {
            'source_id': quote['source_id'],
            'source_section_id': quote['source_section_id'],
            'version_id': version_id,
            'calculation_convention': {'id': conv['id'],
                                       'version': conv['version']},
        },
    }
    block.update(over)
    return block


class _StubTrace:
    def __init__(self, steps, evidence):
        self.steps = steps
        self.evidence = evidence


def _yin_steps():
    """Fact-shape fixture for the touchstone chart 甲辰/丙寅/庚子/丙子.

    Shape only, copied from test_tj012_ren_yin_true.py: real-chart
    verification of the same pillars lives in the sealed companion.
    Ten-gods are relative to the 庚 day master; 寅 hidden stems are
    甲（偏财）/丙（七杀）/戊（偏印）.
    """
    return [
        {'rule_id': 'bazi.phase2.pillars', 'evidence_ids': ['e1'],
         'output': {'ganzhi': [['甲', '辰'], ['丙', '寅'], ['庚', '子'],
                               ['丙', '子']],
                    'day_master': {'stem': '庚'}}},
        {'rule_id': 'bazi.phase2.ten_gods', 'evidence_ids': ['e2'],
         'output': [{'pillar': 'year', 'stem': '甲', 'ten_god': '偏财'},
                    {'pillar': 'month', 'stem': '丙', 'ten_god': '七杀'},
                    {'pillar': 'day', 'stem': '庚', 'ten_god': '日主'},
                    {'pillar': 'hour', 'stem': '丙', 'ten_god': '七杀'}]},
        {'rule_id': 'bazi.phase2.hidden_stems',
         'evidence_ids': ['e3'],
         'output': [
             {'pillar': 'year', 'branch': '辰', 'hidden_stems': []},
             {'pillar': 'month', 'branch': '寅',
              'hidden_stems': [{'stem': '甲', 'ten_god': '偏财'},
                               {'stem': '丙', 'ten_god': '七杀'},
                               {'stem': '戊', 'ten_god': '偏印'}]},
             {'pillar': 'day', 'branch': '子', 'hidden_stems': []},
             {'pillar': 'hour', 'branch': '子', 'hidden_stems': []}]},
        {'rule_id': 'bazi.phase2.hidden_to_visible',
         'evidence_ids': ['e4'],
         'output': {'positions': [
             {'hidden_pillar': 'month', 'hidden_stem': '甲',
              'visible_pillars': ['year']},
             {'hidden_pillar': 'month', 'hidden_stem': '丙',
              'visible_pillars': ['month', 'hour']}],
                    'day_stem_excluded': True}},
    ]


def _evidence():
    return {i: object() for i in ('e1', 'e2', 'e3', 'e4')}


class GateTriggerTests(unittest.TestCase):
    def test_non_yin_birth_never_enters_gate(self):
        case = CASES['link-non-yin']
        birth = case['source_birth']
        record = ren_yin_research_execution(
            birth['value'], birth['zone'])
        self.assertFalse(record['entered'])
        self.assertEqual(record['reason'], 'month_not_yin')
        self.assertEqual(record['month_branch'], '午')
        self.assertIsNone(record['pilot'])
        self.assertIsNone(record['envelope'])
        self.assertIsNone(record['determination'])
        self.assertTrue(record['research_only'])
        self.assertFalse(record['public_enabled'])
        self.assertFalse(record['ai_enabled'])
        self.assertEqual(
            set(_all_keys(record)) & FORBIDDEN_KEYS, set(),
            'a non-entry record carries no verdict-shaped key')

    def test_second_non_yin_month_never_enters_gate(self):
        # July birth (month 未): same non-entry, zone defaulted.
        record = ren_yin_research_execution('2024-07-15T12:00:00+08:00')
        self.assertFalse(record['entered'])
        self.assertEqual(record['reason'], 'month_not_yin')
        self.assertEqual(record['month_branch'], '未')
        self.assertIsNone(record['pilot'])

    def test_si_month_birth_never_enters_gate(self):
        # 巳月 birth: the gate itself never enters (month_not_yin);
        # the 巳月 pilot is never consulted as a D-1 input.
        case = CASES['link-si']
        birth = case['source_birth']
        record = ren_yin_research_execution(
            birth['value'], birth['zone'])
        self.assertFalse(record['entered'])
        self.assertEqual(record['reason'], 'month_not_yin')
        self.assertEqual(record['month_branch'], '巳')
        self.assertIsNone(record['pilot'])

    def test_naive_birth_fails_closed(self):
        with self.assertRaises(ValueError):
            ren_yin_research_execution('2024-02-11T04:00:00')

    def test_non_string_value_fails_closed(self):
        with self.assertRaises(ValueError):
            ren_yin_research_execution(20240211)


class GateOptInTests(unittest.TestCase):
    def test_gate_is_not_a_registered_scenario(self):
        ids = {item['id'] for item in registry()}
        self.assertNotIn('ren-yin-research', ids)
        self.assertNotIn('ren_yin_research', ids)
        with self.assertRaises(ValueError):
            execute_scenario('ren-yin-research', {'value': '2024-02-11T04:00:00+08:00'})

    def test_production_bazi_profile_does_not_call_gate(self):
        # Source-shape pin, in the F4 precedent: the production
        # scenario function must not invoke the research gate
        # directly -- no raw research record reaches _bazi_profile.
        # TJ-012.3 Stage B (user 2026-11-10, limited exception to
        # the U1 pattern-field ban) adds exactly one authorized
        # indirection: _bazi_profile calls _pattern_public_gate,
        # which consumes the research gate server-side and attaches
        # only the validated presentation object.
        source = (ROOT / 'src' / 'tianji_kb' / 'scenario_engine.py'
                  ).read_text(encoding='utf-8')
        profile = source.split('def _bazi_profile')[1].split(
            'def _question')[0]
        self.assertNotIn('ren_yin_research_execution', profile)
        self.assertNotIn('_ren_yin_research_pilot', profile)
        self.assertNotIn('pattern_determination_ren_yin', profile)
        self.assertEqual(profile.count('_pattern_public_gate('), 1)
        gate = source.split('def _pattern_public_gate')[1].split(
            '\ndef ')[0]
        self.assertIn('ren_yin_research_execution', gate)
        self.assertIn('public_pattern_presentation', gate)


class LivePilotStepTests(unittest.TestCase):
    def test_yin_birth_live_pilot_computes(self):
        case = CASES['link-t1']
        month_branch, pilot = _ren_yin_research_pilot(
            case['source_birth']['value'], case['source_birth']['zone'])
        self.assertEqual(month_branch, '寅')
        self.assertEqual(pilot['status'], 'computed')
        self.assertEqual(pilot['commander'], '戊')
        self.assertEqual(pilot['segment']['index'], 1)
        self.assertEqual(pilot['variant'],
                         GOLDEN['pilot_variant'])
        self.assertIsNone(pilot['determination'])

    def test_boundary_flip_pair_via_live_pilot(self):
        # f1/f2: the same ±1s pair as the D-1 Golden, through the
        # gate's own pilot step (not a hand-written pilot dict).
        before_month, before = _ren_yin_research_pilot(
            CASES['link-f1']['source_birth']['value'], 'Asia/Shanghai')
        at_month, at = _ren_yin_research_pilot(
            CASES['link-f2']['source_birth']['value'], 'Asia/Shanghai')
        self.assertEqual((before_month, at_month), ('寅', '寅'))
        self.assertEqual(before['commander'], '戊')
        self.assertEqual(at['commander'], '丙')
        self.assertEqual(before['segment']['index'], 1)
        self.assertEqual(at['segment']['index'], 2)

    def test_jie_replay_mismatch_rejected(self):
        # The gate derives Jie facts itself, so a tampered claim is
        # checked at the pilot layer: lichun +1s vs the provider
        # replay must reject, never compute.
        case = CASES['link-t1']
        facts = _jie_facts(case)
        facts['lichun']['at'] = '2024-02-04T16:27:08+08:00'
        pilot = yin_siling_pilot(
            case['source_birth']['value'],
            version_id='ditiansui-yuanshuo', jie_facts=facts)
        self.assertEqual(pilot['status'], 'rejected')
        self.assertEqual(pilot['reason'], 'provider_replay_mismatch')
        self.assertIsNone(pilot['commander'])

    def test_uncertain_pilot_yields_no_valid_determination(self):
        # Real uncertain pilot (precision_warning declaration) through
        # the composition layer: abstained, no valid D-1 determination.
        case = CASES['link-s2-uncertain']
        pilot = yin_siling_pilot(
            case['source_birth']['value'],
            version_id='ditiansui-yuanshuo',
            jie_facts=_jie_facts(case))
        self.assertEqual(pilot['status'], 'uncertain')
        out = ren_yin_true_pattern(
            _StubTrace(_yin_steps(), _evidence()), pilot)
        self.assertEqual(out['abstention_reason'], 'pilot_not_computed')
        self.assertEqual(out['decision_step'], 3)
        self.assertEqual(out['determination']['true_false'], 'abstained')
        self.assertIsNone(out['determination']['pattern'])

    def test_si_pilot_result_must_not_serve_as_d1_input(self):
        # A real, computed 巳月 pilot block is not a Ren D-1 input:
        # wrong variant -> the composition abstains as unverifiable.
        case = CASES['link-si']
        window = GOLDEN['jie_windows']['2025-si']
        facts = {'provider': dict(GOLDEN['provider']),
                 'lixia': dict(window['lixia']),
                 'next_jie': dict(window['next_jie'])}
        pilot = si_siling_pilot(
            case['source_birth']['value'], version_id='sanming-t1',
            jie_facts=facts)
        self.assertEqual(pilot['status'], 'computed')
        self.assertEqual(pilot['variant'], GOLDEN['si_pilot_variant'])
        self.assertEqual(pilot['commander'], '戊')
        out = ren_yin_true_pattern(
            _StubTrace(_yin_steps(), _evidence()), pilot)
        self.assertEqual(out['abstention_reason'],
                         'pilot_result_unverifiable')
        self.assertEqual(out['determination']['true_false'], 'abstained')

    def test_forged_pilot_variant_abstains(self):
        out = ren_yin_true_pattern(
            _StubTrace(_yin_steps(), _evidence()),
            _pilot_block(variant='forged'))
        self.assertEqual(out['abstention_reason'],
                         'pilot_result_unverifiable')
        self.assertEqual(out['determination']['true_false'], 'abstained')


class SilentDropFixTests(unittest.TestCase):
    def test_pilot_without_variant_fails_closed(self):
        cx = next(c for c in GOLDEN['counterexamples']
                  if c['id'] == 'cx-pilot-without-variant')
        with self.assertRaises(ValueError) as caught:
            chart('甲辰', '丙寅', '乙巳', '戊寅',
                  ren_yin_pilot_result={'variant': 'bazi-siling-yin-pilot-v1'})
        self.assertEqual(str(caught.exception), cx['expected']['message'])

    def test_pilot_with_wrong_variant_fails_closed(self):
        cx = next(c for c in GOLDEN['counterexamples']
                  if c['id'] == 'cx-pilot-with-wrong-variant')
        with self.assertRaises(ValueError) as caught:
            chart('甲辰', '丙寅', '乙巳', '戊寅',
                  pattern_variant='bogus-variant',
                  ren_yin_pilot_result={'variant': 'bazi-siling-yin-pilot-v1'})
        self.assertEqual(str(caught.exception), cx['expected']['message'])

    def test_non_dict_pilot_still_rejected(self):
        with self.assertRaises(ValueError):
            chart('甲辰', '丙寅', '乙巳', '戊寅',
                  ren_yin_pilot_result='not-a-dict')

    def test_pattern_variant_constant_matches_golden(self):
        self.assertEqual(PATTERN_VARIANT, GOLDEN['pattern_variant'])


class ProjectionTests(unittest.TestCase):
    def test_public_projection_strips_d1_block(self):
        payload = {
            'domain': 'bazi', 'variant': 'ziping-structural-v1',
            'deterministic': True,
            'result': {'pillars': [],
                       'pattern_determination_ren_yin': {'x': 1}},
            'chart': {'pattern_determination_ren_yin': {'x': 2}},
            'evidence': {}, 'rule_matches': [], 'trace': [],
        }
        out = project_execution(copy.deepcopy(payload))
        self.assertNotIn('pattern_determination_ren_yin', out['chart'])
        self.assertNotIn('pattern_determination_ren_yin', out['result'])


if __name__ == '__main__':
    unittest.main()
