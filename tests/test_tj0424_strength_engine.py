"""TJ-0424 旺衰引擎测试：古典 7 谓词（因素层）＋现代工程化模型。

Offline assembled acceptance only (NOT public CI): chart-based cases
execute real births through the production calendar chain and the
canonical tables, which exist only in the assembled environment; the
bare worktree has no data/canonical. Run in the worktree with
``PYTHONPATH=src python -m unittest tests.test_tj0424_strength_engine``.

Coverage:
- the 7 classical predicates reproduce their public Golden verdicts
  (51-case sweep over the six Golden files: wood Hai, Bing-Wu,
  S2 metal/water, Bing-Si lu, F4 design, fire morphology);
- the lu scope conditions equal the Golden expected_conditions verbatim;
- the metal predicate is wired but validation pending: it never fires
  on a real chart and its entry always carries the pending disclosure;
- the modern model pins exact scores and components for 6 real births
  (strong 105 / 103 / 97 / 95 / 70-with-pilot, weak -35, balanced 36);
- all four modern abstention screens (earth UNBUILDABLE, Si pilot gate,
  transformation, cong) with reasons, on real births where possible
  and on labelled synthetic pillars otherwise;
- counter-proof tests: shifting MODERN_THRESHOLDS flips the verdict,
  and stubbing out factors() breaks the engine (no stub can pass);
- parallel-output discipline: classical and modern verdicts are never
  unified; conflicts and abstentions are presented explicitly.
- second batch (P0-1 completeness, Q1–Q9): the 8 new callables —
  coverage_matrix (120 cells), explain_components (per-component
  sources/conditions), Q6 tomb-month and Q5 earth/Ding provisional
  status, identify_cong_candidates (incl. the Q4 cong_cai expansion
  and the reviewed-predicate guard, Q2), interaction_conditions
  (Q3-A record-only), sensitivity_analysis, divergence_explanation,
  audit_component_counts / validate_assessment (bounds, no double
  counting, boundary thresholds, tamper detection, and validity of
  the engine's own results under documented weight overrides).
"""
import copy
import json
import unittest
from pathlib import Path
from unittest import mock

from tianji_kb.bazi_core import chart_from_datetime
from tianji_kb.bazi_siling_si_pilot import (
    _provider_jie_instant, si_siling_pilot)
from tianji_kb.bazi_strength_engine import (
    ENGINE_VARIANT, MODERN_MODEL_ID, MODERN_SCORE_RANGE, MODERN_THRESHOLDS,
    MODERN_WEIGHTS, PREDICATES, assess_strength, audit_component_counts,
    coverage_matrix, default_coverage_template, divergence_explanation,
    explain_components, identify_cong_candidates, interaction_conditions,
    sensitivity_analysis, validate_assessment)
from tianji_kb.calendar_provider_guard import provider_identity
from tianji_kb.foundations import BRANCHES, STEMS

ROOT = Path(__file__).resolve().parents[1]

GOLDEN_FILES = [
    'tests/golden_tj0112_wood_hai.json',
    'tests/golden_tj0112_bing_wu_commanding.json',
    'tests/golden_tj0112_s2_metal_water.json',
    'tests/golden_tj0112_bing_si_lu.json',
    'tests/golden_tj0112_f34_si_yin.json',
    'tests/golden_tj0112_fire_morphology.json',
]

BIRTHS = {
    # Golden-anchored real births (source_birth in the public Golden files).
    'lu_positive': '1927-05-12T12:00:00+08:00',
    'lu_near_miss': '2017-05-19T12:00:00+08:00',
    'water_positive': '1981-12-21T00:30:00+08:00',
    'water_near_miss_ren': '1921-12-15T00:30:00+08:00',
    'metal_near_miss_xin': '1981-09-10T00:30:00+08:00',
    'metal_near_miss_geng': '1981-09-09T00:30:00+08:00',
    'wood_mao_positive': '1963-03-22T22:00:00+08:00',
    'wood_you_weak': '1978-09-20T10:00:00+08:00',
    'wood_hai_positive': '1983-12-02T00:30:00+08:00',
    'bingwu_positive': '1966-07-06T12:00:00+08:00',
    'bingwu_counter': '2011-06-20T15:30:00+08:00',
    'balanced': '1995-11-11T09:00:00+08:00',
    'earth_unbuildable': '2025-05-09T12:00:00+08:00',
    'f4_positive': '2034-02-19T12:00:00+08:00',
    'f4_first_segment': '2014-02-04T12:00:00+08:00',
    # Q6 tomb-month real births (month branch 辰/未/戌/丑, modern computed).
    'tomb_wei': '2024-07-15T12:00:00+08:00',   # 庚×未 weak 0 uncertain
    'tomb_xu': '2024-10-15T12:00:00+08:00',    # 壬×戌 weak 8 uncertain
    'tomb_chou': '2025-01-15T12:00:00+08:00',  # 甲×丑 weak 5 uncertain
    # Q5 provisional real births (earth / Ding de_di uncalibrated).
    'ding_you': '2025-09-15T12:00:00+08:00',   # 丁×酉 balanced 41
    'ding_xu': '2025-10-15T12:00:00+08:00',    # 丁×戌 balanced 39 (both flags)
    'earth_mao': '2024-03-15T12:00:00+08:00',  # 戊×卯 balanced 20
    'earth_hai': '2025-11-15T12:00:00+08:00',  # 戊×亥 balanced 33
}


def run_birth(birth, **kwargs):
    chart = chart_from_datetime(birth)
    out = assess_strength(chart['pillars'], chart['day_master']['stem'],
                          **kwargs)
    pillars = [p['stem']['value'] + p['branch']['value']
               for p in chart['pillars']]
    return out, pillars


def si_pilot_for_1927():
    ident = provider_identity()
    lixia = _provider_jie_instant(1927, '立夏')
    mangzhong = _provider_jie_instant(1927, '芒种')
    facts = {
        'provider': {'name': ident['provider'],
                     'version': ident['installed_version'],
                     'identity_verified': True},
        'lixia': {'term': '立夏', 'at': lixia.isoformat(),
                  'precision': 'second'},
        'next_jie': {'term': '芒种', 'at': mangzhong.isoformat(),
                     'precision': 'second'}}
    return si_siling_pilot('1927-05-12T12:00:00+08:00',
                           version_id='sanming-t1', jie_facts=facts)


def synthetic_pillars(ganzhi):
    """Hand-built pillar dicts (factor-level only, never a real chart)."""
    names = ('year', 'month', 'day', 'hour')
    return [{'name': name, 'stem': {'value': gz[0]},
             'branch': {'value': gz[1]}} for name, gz in zip(names, ganzhi)]


class EngineShapeTests(unittest.TestCase):
    def test_variant_and_predicate_register(self):
        self.assertEqual(ENGINE_VARIANT, 'bazi-strength-engine-v1')
        self.assertEqual(len(PREDICATES), 7)
        self.assertEqual(
            [p['predicate_id'] for p in PREDICATES],
            ['pure_support', 'isolated_control',
             'pure_generating_support', 'commanding_visible_support',
             'lu_visible_support', 'pure_support_metal',
             'pure_generating_support_water'])
        # Sealed validation states as verified on the trusted machine
        # 2026-11-25 (sealed phase2_execution.json): only metal pending.
        states = {p['predicate_id']: p['sealed_validation']
                  for p in PREDICATES}
        self.assertEqual(states['pure_support_metal'], 'pending')
        for pid, state in states.items():
            if pid != 'pure_support_metal':
                self.assertEqual(state, 'validated', pid)
        for spec in PREDICATES:
            self.assertTrue(spec['sealed_golden_ids'], spec)
            self.assertTrue(spec['public_golden_refs'], spec)
            self.assertTrue(spec['phase1_rule_id'], spec)
            self.assertTrue(spec['phase2_step_id'], spec)

    def test_modern_thresholds_and_weights_pinned(self):
        self.assertEqual(MODERN_THRESHOLDS,
                         {'strong_at_least': 60, 'weak_at_most': 15,
                          'balanced_between': (16, 59)})
        self.assertEqual(MODERN_WEIGHTS['de_ling']['same_element'], 30)
        self.assertEqual(MODERN_WEIGHTS['de_ling']['generates_me'], 20)
        self.assertEqual(MODERN_WEIGHTS['de_ling']['controls_me'], -15)
        self.assertEqual(MODERN_WEIGHTS['de_di']['heavy_root_each'], 15)
        self.assertEqual(MODERN_WEIGHTS['de_di']['cap'], 35)
        self.assertEqual(MODERN_WEIGHTS['de_shi']['visible_support_each'], 10)
        self.assertEqual(
            MODERN_WEIGHTS['shengfu_hidden']['hidden_support_each'], 2)
        self.assertEqual(MODERN_WEIGHTS['kexiehao']['opposing_each'], -2)
        self.assertEqual(MODERN_WEIGHTS['kexiehao']['floor'], -20)

    def test_input_validation_before_any_factor_work(self):
        pillars = synthetic_pillars(['丁卯', '乙巳', '丙午', '甲午'])
        with self.assertRaises(ValueError):
            assess_strength(pillars, '丁')  # day stem mismatch
        with self.assertRaises(ValueError):
            assess_strength(pillars[:3], '丙')  # not four pillars
        with self.assertRaises(ValueError):
            assess_strength(pillars, '子')  # not a stem
        bad = copy.deepcopy(pillars)
        bad[1]['branch']['value'] = 'X'
        with self.assertRaises(ValueError):
            assess_strength(bad, '丙')

    def test_closed_output_shape_and_governance_flags(self):
        out, _ = run_birth(BIRTHS['water_positive'])
        self.assertEqual(set(out), {
            'variant', 'day_master', 'month_branch', 'pillars', 'factors',
            'classical', 'modern', 'agreement', 'evidence_chain',
            'research_only', 'public_enabled', 'ai_enabled',
            'limitations'})
        self.assertTrue(out['research_only'])
        self.assertFalse(out['public_enabled'])
        self.assertFalse(out['ai_enabled'])
        self.assertTrue(out['classical']['research_only'])
        self.assertFalse(out['classical']['public_enabled'])
        self.assertFalse(out['classical']['ai_enabled'])
        self.assertEqual(out['modern']['model_id'], MODERN_MODEL_ID)
        self.assertEqual(out['modern']['model_kind'], 'modern_engineering')
        self.assertTrue(out['modern']['research_only'])
        self.assertFalse(out['modern']['public_enabled'])
        self.assertFalse(out['modern']['ai_enabled'])
        self.assertEqual(len(out['evidence_chain']), 8)  # 7 + modern


class ClassicalGoldenTests(unittest.TestCase):
    def predicate(self, out, predicate_id):
        for entry in out['classical']['predicates']:
            if entry['predicate_id'] == predicate_id:
                return entry
        self.fail('missing predicate ' + predicate_id)

    def test_lu_positive_conditions_match_golden_verbatim(self):
        golden = json.loads(
            (ROOT / 'tests/golden_tj0112_bing_si_lu.json').read_text('utf-8'))
        case = next(c for c in golden['cases']
                    if c['id'] == 'tj0112-bingsi-positive')
        out, pillars = run_birth(BIRTHS['lu_positive'])
        self.assertEqual(pillars, case['expected_pillars'])
        entry = self.predicate(out, 'lu_visible_support')
        self.assertTrue(entry['met'])
        self.assertEqual(entry['conditions'], case['expected_conditions'])
        self.assertEqual(out['classical']['classification'], 'strong')
        self.assertEqual(
            out['classical']['matched_predicate']['predicate_id'],
            'lu_visible_support')
        self.assertEqual(entry['sealed_validation'], 'validated')
        self.assertEqual(entry['sealed_golden_ids'],
                         ['bazi.strength-ganzhi-lu-positive'])
        self.assertEqual(entry['phase1_rule_id'], 'bazi.rule.r032')
        self.assertEqual(entry['phase2_step_id'],
                         'bazi.phase2.strength_lu_visible_support')

    def test_wood_and_fire_positives(self):
        checks = [
            ('wood_mao_positive', 'pure_support', 'strong'),
            ('wood_you_weak', 'isolated_control', 'weak'),
            ('wood_hai_positive', 'pure_generating_support', 'strong'),
            ('bingwu_positive', 'commanding_visible_support', 'strong'),
            ('water_positive', 'pure_generating_support_water', 'strong'),
        ]
        for birth_key, predicate_id, classification in checks:
            out, _ = run_birth(BIRTHS[birth_key])
            self.assertEqual(out['classical']['classification'],
                             classification, birth_key)
            entry = self.predicate(out, predicate_id)
            self.assertTrue(entry['met'], birth_key)
            self.assertTrue(all(entry['conditions'].values()), birth_key)
            self.assertEqual(entry['verification'], 'factor_level_only')

    def test_metal_pending_never_fires_on_real_charts(self):
        for birth_key in ('metal_near_miss_xin', 'metal_near_miss_geng'):
            out, _ = run_birth(BIRTHS[birth_key])
            entry = self.predicate(out, 'pure_support_metal')
            self.assertFalse(entry['met'], birth_key)
            self.assertEqual(entry['sealed_validation'], 'pending')
            self.assertIn('pending', entry['notes'])
            self.assertIn('构造性不可满足', entry['notes'])
            self.assertEqual(out['classical']['classification'],
                             'indeterminate', birth_key)

    def test_near_misses_are_indeterminate(self):
        for birth_key in ('lu_near_miss', 'water_near_miss_ren',
                          'bingwu_counter'):
            out, _ = run_birth(BIRTHS[birth_key])
            self.assertEqual(out['classical']['classification'],
                             'indeterminate', birth_key)
            self.assertIsNone(out['classical']['matched_predicate'])

    def test_changsheng_not_wired(self):
        # 丙×寅长生形态待注册、无段门：因素层九条件纵满足也不触发。
        for birth_key in ('f4_positive', 'f4_first_segment'):
            out, _ = run_birth(BIRTHS[birth_key])
            self.assertEqual(out['classical']['classification'],
                             'indeterminate', birth_key)
            self.assertNotIn(
                'changsheng_visible_support',
                [e['predicate_id']
                 for e in out['classical']['predicates']])

    def test_whole_golden_sweep(self):
        """All 51 public Golden cases reproduce their verdicts."""
        total = 0
        mismatches = []
        for name in GOLDEN_FILES:
            data = json.loads((ROOT / name).read_text('utf-8'))
            for case in data['cases']:
                birth = case.get('source_birth')
                expect = case.get('expect', {})
                want = expect.get('classification') \
                    or expect.get('current_implementation_classification') \
                    or expect.get('current_engine')
                if birth is None or want is None:
                    continue
                total += 1
                out, _ = run_birth(birth)
                got = out['classical']['classification']
                if got != want:
                    mismatches.append((case['id'], want, got))
        self.assertEqual(total, 51)
        self.assertEqual(mismatches, [])


class ModernModelTests(unittest.TestCase):
    def components(self, out):
        return {k: v['score'] for k, v in out['modern']['components'].items()}

    def test_exact_scores_and_components(self):
        checks = [
            ('wood_mao_positive', 'strong', 105,
             {'de_ling': 30, 'de_di': 35, 'de_shi': 30,
              'shengfu_hidden': 10, 'kexiehao': 0}),
            ('water_positive', 'strong', 103,
             {'de_ling': 30, 'de_di': 35, 'de_shi': 30,
              'shengfu_hidden': 8, 'kexiehao': 0}),
            ('bingwu_positive', 'strong', 97,
             {'de_ling': 30, 'de_di': 35, 'de_shi': 30,
              'shengfu_hidden': 10, 'kexiehao': -8}),
            ('wood_hai_positive', 'strong', 95,
             {'de_ling': 20, 'de_di': 35, 'de_shi': 30,
              'shengfu_hidden': 10, 'kexiehao': 0}),
            ('wood_you_weak', 'weak', -35,
             {'de_ling': -15, 'de_di': 0, 'de_shi': 0,
              'shengfu_hidden': 0, 'kexiehao': -20}),
            ('balanced', 'balanced', 36,
             {'de_ling': -15, 'de_di': 35, 'de_shi': 20,
              'shengfu_hidden': 8, 'kexiehao': -12}),
        ]
        for birth_key, verdict, score, components in checks:
            out, _ = run_birth(BIRTHS[birth_key])
            self.assertEqual(out['modern']['verdict'], verdict, birth_key)
            self.assertEqual(out['modern']['score'], score, birth_key)
            self.assertEqual(self.components(out), components, birth_key)
            self.assertIsNone(out['modern']['abstain_reason'])

    def test_si_pilot_gate(self):
        pilot = si_pilot_for_1927()
        self.assertEqual(pilot['status'], 'computed')
        self.assertEqual(pilot['commander'], '戊')
        # Without the pilot the modern model abstains, classical stays strong.
        out, _ = run_birth(BIRTHS['lu_positive'])
        self.assertEqual(out['modern']['verdict'], 'abstain')
        self.assertEqual(out['modern']['abstain_reason'],
                         'siling_si_pilot_not_verified')
        self.assertIsNone(out['modern']['score'])
        self.assertEqual(out['classical']['classification'], 'strong')
        # With the verified pilot (戊段, i_generate) de_ling is 5, total 70.
        out, _ = run_birth(BIRTHS['lu_positive'], siling_si_pilot=pilot)
        self.assertEqual(out['modern']['verdict'], 'strong')
        self.assertEqual(out['modern']['score'], 70)
        self.assertEqual(self.components(out),
                         {'de_ling': 5, 'de_di': 35, 'de_shi': 30,
                          'shengfu_hidden': 8, 'kexiehao': -8})
        self.assertIn('戊', out['modern']['components']['de_ling']['basis'])

    def test_si_pilot_invalid_shape_abstains(self):
        out, _ = run_birth(BIRTHS['lu_positive'],
                           siling_si_pilot={'variant': 'not-a-pilot'})
        self.assertEqual(out['modern']['abstain_reason'],
                         'siling_si_pilot_invalid')
        uncertain = dict(si_pilot_for_1927())
        uncertain['status'] = 'uncertain'
        out, _ = run_birth(BIRTHS['lu_positive'], siling_si_pilot=uncertain)
        self.assertEqual(out['modern']['abstain_reason'],
                         'siling_si_pilot_not_verified')

    def test_earth_unbuildable_abstains(self):
        out, pillars = run_birth(BIRTHS['earth_unbuildable'])
        self.assertEqual(pillars, ['乙巳', '辛巳', '戊寅', '戊午'])
        self.assertEqual(out['modern']['verdict'], 'abstain')
        self.assertEqual(out['modern']['abstain_reason'],
                         'earth_form_unbuildable_tj0112')
        self.assertEqual(out['classical']['classification'], 'indeterminate')
        self.assertIn('earth_form_unbuildable_tj0112',
                      out['classical']['blockers'])

    def test_transformation_abstains(self):
        # 丙辛合在场（显干丙/辛）：化气候选无依据。
        out, _ = run_birth(BIRTHS['metal_near_miss_geng'])
        self.assertEqual(out['modern']['verdict'], 'abstain')
        self.assertEqual(out['modern']['abstain_reason'],
                         'transformation_candidate_unresolved')

    def test_cong_screen_abstains_on_synthetic_pillars(self):
        # Factor-level synthetic case (never a real chart): no roots,
        # no visible support, visible stems all controls_me.
        pillars = synthetic_pillars(['庚申', '庚申', '甲子', '辛酉'])
        out = assess_strength(pillars, '甲')
        self.assertEqual(out['classical']['classification'], 'indeterminate')
        self.assertEqual(out['modern']['verdict'], 'abstain')
        self.assertEqual(out['modern']['abstain_reason'],
                         'cong_candidate_unresolved')

    def test_cong_screen_does_not_block_reviewed_weak(self):
        # 已审弱谓词命中的盘（木月酉孤立）不是从格候选：现代层照常评弱。
        out, _ = run_birth(BIRTHS['wood_you_weak'])
        self.assertEqual(out['classical']['matched_predicate']['predicate_id'],
                         'isolated_control')
        self.assertEqual(out['modern']['verdict'], 'weak')

    def test_include_modern_false(self):
        out, _ = run_birth(BIRTHS['water_positive'], include_modern=False)
        self.assertIsNone(out['modern'])
        self.assertEqual(out['agreement']['relationship'], 'not_comparable')
        self.assertEqual(len(out['evidence_chain']), 7)


class CounterProofTests(unittest.TestCase):
    """反证：改阈值或换 stub 即失败。"""

    def test_threshold_shift_flips_verdict(self):
        pilot = si_pilot_for_1927()
        with mock.patch.dict(MODERN_THRESHOLDS, {'strong_at_least': 71}):
            out, _ = run_birth(BIRTHS['lu_positive'], siling_si_pilot=pilot)
            self.assertEqual(out['modern']['score'], 70)
            self.assertEqual(out['modern']['verdict'], 'balanced')
        with mock.patch.dict(MODERN_THRESHOLDS, {'strong_at_least': 70}):
            out, _ = run_birth(BIRTHS['lu_positive'], siling_si_pilot=pilot)
            self.assertEqual(out['modern']['verdict'], 'strong')
        # Unpatched: the pinned threshold still holds.
        out, _ = run_birth(BIRTHS['lu_positive'], siling_si_pilot=pilot)
        self.assertEqual(out['modern']['verdict'], 'strong')

    def test_engine_consumes_factors_not_a_stub(self):
        import tianji_kb.bazi_strength_engine as engine
        with mock.patch.object(engine, 'factors',
                               side_effect=RuntimeError('stubbed out')):
            with self.assertRaises(RuntimeError):
                run_birth(BIRTHS['water_positive'])

    def test_weight_change_moves_score(self):
        with mock.patch.dict(MODERN_WEIGHTS['de_ling'],
                             {'same_element': 0}):
            out, _ = run_birth(BIRTHS['water_positive'])
            self.assertEqual(out['modern']['score'], 73)
            self.assertEqual(out['modern']['verdict'], 'strong')
        out, _ = run_birth(BIRTHS['water_positive'])
        self.assertEqual(out['modern']['score'], 103)


class AgreementTests(unittest.TestCase):
    def test_lu_without_pilot_is_modern_abstain_not_conflict(self):
        out, _ = run_birth(BIRTHS['lu_positive'])
        self.assertEqual(out['agreement']['relationship'], 'modern_abstains')
        self.assertEqual(out['agreement']['classical'], 'strong')
        self.assertEqual(out['agreement']['modern'], 'abstain')

    def test_lu_with_pilot_agrees(self):
        out, _ = run_birth(BIRTHS['lu_positive'],
                           siling_si_pilot=si_pilot_for_1927())
        self.assertEqual(out['agreement']['relationship'], 'agree')
        self.assertEqual(out['agreement']['classical'], 'strong')
        self.assertEqual(out['agreement']['modern'], 'strong')

    def test_classical_indeterminate_modern_strong_is_presented(self):
        # 水近 miss 壬盘：古典层无谓词命中，现代层 strong 98——并列呈现，
        # 不以现代结论补古典缺口。
        out, _ = run_birth(BIRTHS['water_near_miss_ren'])
        self.assertEqual(out['classical']['classification'], 'indeterminate')
        self.assertEqual(out['modern']['verdict'], 'strong')
        self.assertEqual(out['modern']['score'], 98)
        self.assertEqual(out['agreement']['relationship'],
                         'classical_indeterminate')
        # 金近 miss 辛盘：现代层无视卯酉冲得 83，古典层因子冲未决——
        # 分歧点在裁定说明与现代局限中均有记录。
        out, _ = run_birth(BIRTHS['metal_near_miss_xin'])
        self.assertEqual(out['classical']['classification'], 'indeterminate')
        self.assertEqual(out['modern']['score'], 83)
        self.assertTrue(any('冲' in line
                            for line in out['modern']['limitations']))

    def test_f4_positive_diverges(self):
        # F4 设计正例：古典层因长生命题未接线而暂不可判，现代层 strong 87。
        out, _ = run_birth(BIRTHS['f4_positive'])
        self.assertEqual(out['classical']['classification'], 'indeterminate')
        self.assertEqual(out['modern']['verdict'], 'strong')
        self.assertEqual(out['modern']['score'], 87)


class EvidenceChainTests(unittest.TestCase):
    def test_every_predicate_carries_rule_and_golden_refs(self):
        out, _ = run_birth(BIRTHS['lu_positive'])
        for entry in out['evidence_chain']:
            if entry['decision'] == 'classical_predicate':
                self.assertTrue(entry['phase1_rule_id'])
                self.assertTrue(entry['phase2_step_id'])
                self.assertTrue(entry['sealed_golden_ids'])
                self.assertTrue(entry['public_golden_refs'])
                self.assertTrue(entry['conditions'])
                self.assertIn('month_branch', entry['factor_refs'])
                self.assertIn('root_positions', entry['factor_refs'])
        modern_entry = out['evidence_chain'][-1]
        self.assertEqual(modern_entry['decision'], 'modern_model')
        self.assertEqual(modern_entry['model_kind'], 'modern_engineering')

    def test_matched_predicate_conditions_all_met(self):
        out, _ = run_birth(BIRTHS['bingwu_positive'])
        matched = out['classical']['matched_predicate']
        self.assertEqual(matched['predicate_id'],
                         'commanding_visible_support')
        self.assertTrue(all(matched['conditions'].values()))
        self.assertEqual(matched['phase1_rule_id'], 'bazi.rule.r030')


# ---------------------------------------------------------------------------
# Second batch (P0-1 completeness): coverage matrix, component explanation,
# Q5/Q6 status, cong candidates, interactions, sensitivity, divergence,
# audit / validation. All expectations below were measured on the trusted
# machine (repro scratch tj0425-strength-verify), not hand-computed.
# ---------------------------------------------------------------------------

def _matrix_cells(matrix):
    return {(c['day_master'], c['month_branch']): c
            for c in matrix['cells']}


def _components(out):
    return {k: v['score'] for k, v in out['modern']['components'].items()}


def _counted_sum(component):
    return sum(s['contribution'] for s in component['sources']
               if s.get('counted'))


class CoverageMatrixTests(unittest.TestCase):
    def test_no_pilot_counts(self):
        # 109 computed / 11 abstain, not 108/12: 戊×巳 belongs to BOTH
        # gates (earth UNBUILDABLE and the Si pilot gate) but is one
        # cell, and the earth gate fires first, so the Si-gate reason
        # counts 9, not 10. The overlap is asserted explicitly below.
        matrix = coverage_matrix()
        self.assertEqual(matrix['total_cells'], 120)
        self.assertEqual(matrix['computed'], 109)
        self.assertEqual(matrix['abstained'], 11)
        self.assertEqual(matrix['errors'], 0)
        self.assertEqual(matrix['uncovered'], [])
        self.assertEqual(matrix['by_abstain_reason'], {
            'siling_si_pilot_not_verified': 9,
            'earth_form_unbuildable_tj0112': 2})
        self.assertEqual(matrix['score_range'], [7, 103])
        cells = _matrix_cells(matrix)
        self.assertEqual(
            cells[('戊', '巳')]['abstain_reason'],
            'earth_form_unbuildable_tj0112')
        self.assertEqual(
            cells[('己', '午')]['abstain_reason'],
            'earth_form_unbuildable_tj0112')
        for day_master in STEMS:
            if day_master == '戊':
                continue
            self.assertEqual(
                cells[(day_master, '巳')]['abstain_reason'],
                'siling_si_pilot_not_verified', day_master)
        self.assertEqual(matrix['model_kind'], 'modern_engineering')
        self.assertTrue(matrix['research_only'])
        self.assertFalse(matrix['public_enabled'])
        self.assertFalse(matrix['ai_enabled'])
        self.assertEqual(matrix['template'],
                         'uniform_day_master_month_branch_probe')

    def test_with_pilot_counts(self):
        matrix = coverage_matrix(siling_si_pilot=si_pilot_for_1927())
        self.assertEqual(matrix['total_cells'], 120)
        self.assertEqual(matrix['computed'], 118)
        self.assertEqual(matrix['abstained'], 2)
        self.assertEqual(matrix['errors'], 0)
        self.assertEqual(matrix['uncovered'], [])
        self.assertEqual(matrix['by_abstain_reason'], {
            'earth_form_unbuildable_tj0112': 2})
        self.assertEqual(matrix['score_range'], [7, 103])
        cells = _matrix_cells(matrix)
        self.assertEqual(
            sorted(c['day_master'] + c['month_branch']
                   for c in matrix['cells'] if c['status'] == 'abstain'),
            ['己午', '戊巳'])
        # Only the two TJ-011.2 cells stay abstained; every Si cell
        # except 戊巳 is now computed.
        for day_master in STEMS:
            if day_master != '戊':
                self.assertEqual(cells[(day_master, '巳')]['status'],
                                 'computed', day_master)

    def test_status_breakdown_with_pilot(self):
        matrix = coverage_matrix(siling_si_pilot=si_pilot_for_1927())
        computed = [c for c in matrix['cells'] if c['status'] == 'computed']
        by_status = {}
        for cell in computed:
            by_status[cell['classification_status']] = \
                by_status.get(cell['classification_status'], 0) + 1
        self.assertEqual(by_status, {
            'definite': 56, 'provisional_incomplete': 34, 'uncertain': 28})
        for cell in computed:
            if cell['classification_status'] == 'definite':
                self.assertEqual(cell['definite_classification'],
                                 cell['score_band'], cell)
            else:
                self.assertIsNone(cell['definite_classification'], cell)
            low, high = MODERN_SCORE_RANGE
            self.assertTrue(low <= cell['score'] <= high, cell)

    def test_si_cells_with_pilot(self):
        cells = _matrix_cells(
            coverage_matrix(siling_si_pilot=si_pilot_for_1927()))
        checks = [
            (('甲', '巳'), 'weak', 10, 'definite',
             {'de_ling': 0, 'de_di': 0, 'de_shi': 30,
              'shengfu_hidden': 0, 'kexiehao': -20}),
            (('丙', '巳'), 'strong', 62, 'definite',
             {'de_ling': 5, 'de_di': 35, 'de_shi': 30,
              'shengfu_hidden': 8, 'kexiehao': -16}),
            (('丁', '巳'), 'balanced', 37, 'provisional_incomplete',
             {'de_ling': 5, 'de_di': 10, 'de_shi': 30,
              'shengfu_hidden': 8, 'kexiehao': -16}),
            (('己', '巳'), 'strong', 72, 'provisional_incomplete',
             {'de_ling': 30, 'de_di': 10, 'de_shi': 30,
              'shengfu_hidden': 10, 'kexiehao': -8}),
            (('壬', '巳'), 'weak', 7, 'definite',
             {'de_ling': -15, 'de_di': 0, 'de_shi': 30,
              'shengfu_hidden': 8, 'kexiehao': -16}),
        ]
        for key, band, score, status, components in checks:
            cell = cells[key]
            self.assertEqual(cell['status'], 'computed', key)
            self.assertEqual(cell['score_band'], band, key)
            self.assertEqual(cell['score'], score, key)
            self.assertEqual(cell['classification_status'], status, key)
            self.assertEqual(cell['components'], components, key)

    def test_tomb_cells_all_four_branches(self):
        cells = _matrix_cells(
            coverage_matrix(siling_si_pilot=si_pilot_for_1927()))
        # All four tomb branches, across several day masters: de_ling
        # is always the provisional 0, status uncertain, no definite class.
        for key, score in ((('甲', '丑'), 22), (('甲', '辰'), 42),
                           (('甲', '未'), 32), (('甲', '戌'), 10),
                           (('乙', '辰'), 47), (('庚', '戌'), 42),
                           (('癸', '丑'), 47), (('辛', '未'), 22)):
            cell = cells[key]
            self.assertEqual(cell['status'], 'computed', key)
            self.assertEqual(cell['score'], score, key)
            self.assertEqual(cell['components']['de_ling'], 0, key)
            self.assertEqual(cell['classification_status'], 'uncertain', key)
            self.assertIsNone(cell['definite_classification'], key)
            self.assertEqual(cell['uncertainty_flags'],
                             ['tomb_de_ling_zero_provisional'], key)

    def test_error_template_records_errors_not_silence(self):
        def bad_template(day_master, month_branch):
            return [{'name': name, 'stem': {'value': day_master},
                     'branch': {'value': month_branch}}
                    for name in ('year', 'month', 'day')]

        matrix = coverage_matrix(pillar_template=bad_template)
        self.assertEqual(matrix['total_cells'], 120)
        self.assertEqual(matrix['computed'], 0)
        self.assertEqual(matrix['errors'], 120)
        self.assertEqual(matrix['uncovered'], [])
        cell = matrix['cells'][0]
        self.assertEqual(cell['status'], 'error')
        self.assertEqual(cell['classification_status'], 'error')
        self.assertIsNone(cell['score'])
        self.assertIn('Expected four ordered pillars', cell['error'])

    def test_custom_template_is_honoured(self):
        def hour_wu_template(day_master, month_branch):
            pillars = default_coverage_template(day_master, month_branch)
            pillars[3]['branch']['value'] = '午'
            return pillars

        matrix = coverage_matrix(pillar_template=hour_wu_template)
        cells = _matrix_cells(matrix)
        self.assertEqual(cells[('甲', '子')]['pillars'],
                         ['甲子', '甲子', '甲子', '甲午'])

    def test_every_cell_validates_and_audits(self):
        pilot = si_pilot_for_1927()
        for with_pilot in (True, False):
            matrix = coverage_matrix(
                siling_si_pilot=pilot if with_pilot else None)
            for cell in matrix['cells']:
                pillars = default_coverage_template(
                    cell['day_master'], cell['month_branch'])
                audit = audit_component_counts(
                    pillars, cell['day_master'],
                    siling_si_pilot=pilot if with_pilot else None)
                self.assertTrue(audit['all_passed'], (with_pilot, cell,
                                 [c for c in audit['checks']
                                  if not c['passed']]))
                out = assess_strength(
                    pillars, cell['day_master'],
                    siling_si_pilot=pilot if with_pilot else None)
                result = validate_assessment(out)
                self.assertTrue(result['valid'], (with_pilot, cell,
                                 [c for c in result['checks']
                                  if not c['passed']]))


class ComponentExplanationTests(unittest.TestCase):
    def test_wood_mao_sources_sum_and_caps(self):
        out, _ = run_birth(BIRTHS['wood_mao_positive'])
        explained = explain_components(
            chart_from_datetime(
                BIRTHS['wood_mao_positive'])['pillars'], '甲')
        self.assertEqual(explained['score'], 105)
        self.assertEqual(explained['components'], out['modern']['components'])
        for name, component in explained['components'].items():
            self.assertEqual(_counted_sum(component), component['score'],
                             name)
            self.assertTrue(component['conditions'], name)
        de_di = explained['components']['de_di']
        # Count cap: only 2 heavy roots counted; the 3rd heavy root
        # (hour 亥) is present but not counted, the same-stem bonus is.
        roots = [s for s in de_di['sources'] if s['kind'] == 'root']
        self.assertEqual(
            [(s['branch'], s['grade'], s['counted'], s['contribution'])
             for s in roots],
            [('卯', 'heavy', True, 15), ('卯', 'heavy', True, 15),
             ('亥', 'heavy', False, 0)])
        bonus = [s for s in de_di['sources']
                 if s['kind'] == 'same_stem_root_bonus'][0]
        self.assertEqual((bonus['contribution'], bonus['counted']), (5, True))
        de_shi = explained['components']['de_shi']
        self.assertEqual(len(de_shi['sources']), 3)
        self.assertTrue(all(s['counted'] for s in de_shi['sources']))
        hidden = explained['components']['shengfu_hidden']
        self.assertEqual(len(hidden['sources']), 5)  # cap 10 = 5 x 2
        self.assertTrue(all(s['counted'] for s in hidden['sources']))
        self.assertEqual(
            explained['components']['kexiehao']['sources'], [])
        self.assertEqual(explained['classification_status'], 'definite')
        self.assertEqual(explained['definite_classification'], 'strong')

    def test_balanced_sources_counted_counts(self):
        explained = explain_components(
            chart_from_datetime(BIRTHS['balanced'])['pillars'], '丙')
        self.assertEqual(explained['score'], 36)
        de_shi = explained['components']['de_shi']
        self.assertEqual(de_shi['score'], 20)
        self.assertEqual(sum(1 for s in de_shi['sources'] if s['counted']),
                         2)
        hidden = explained['components']['shengfu_hidden']
        self.assertEqual(hidden['score'], 8)
        self.assertEqual(sum(1 for s in hidden['sources'] if s['counted']),
                         4)
        kexiehao = explained['components']['kexiehao']
        self.assertEqual(kexiehao['score'], -12)
        self.assertEqual(
            sum(1 for s in kexiehao['sources'] if s['counted']), 6)

    def test_kexiehao_floor_sources(self):
        # Weak -35: opposing stems hit the -20 floor; exactly 10 counted.
        explained = explain_components(
            chart_from_datetime(BIRTHS['wood_you_weak'])['pillars'], '乙')
        self.assertEqual(explained['score'], -35)
        kexiehao = explained['components']['kexiehao']
        self.assertEqual(kexiehao['score'], -20)
        self.assertEqual(_counted_sum(kexiehao), -20)
        self.assertEqual(sum(1 for s in kexiehao['sources'] if s['counted']),
                         10)
        self.assertTrue(all(s['contribution'] == 0
                            for s in kexiehao['sources']
                            if not s['counted']))

    def test_explain_abstain_and_invalid(self):
        chart = chart_from_datetime(BIRTHS['earth_unbuildable'])
        explained = explain_components(chart['pillars'], '戊')
        self.assertEqual(explained['verdict'], 'abstain')
        self.assertIsNone(explained['score'])
        self.assertIsNone(explained['components'])
        self.assertEqual(explained['abstain_reason'],
                         'earth_form_unbuildable_tj0112')
        self.assertEqual(explained['classification_status'], 'abstain')
        self.assertIsNone(explained['definite_classification'])
        with self.assertRaises(ValueError):
            explain_components(synthetic_pillars(
                ['丁卯', '乙巳', '丙午', '甲午']), '丁')

    def test_explain_governance_flags(self):
        explained = explain_components(
            chart_from_datetime(BIRTHS['water_positive'])['pillars'], '癸')
        self.assertEqual(explained['model_kind'], 'modern_engineering')
        self.assertTrue(explained['research_only'])
        self.assertFalse(explained['public_enabled'])
        self.assertFalse(explained['ai_enabled'])


class TombAndProvisionalTests(unittest.TestCase):
    def test_tomb_months_real_births(self):
        checks = [
            ('tomb_wei', '庚', '未', '己', 0, 'weak'),
            ('tomb_xu', '壬', '戌', '戊', 8, 'weak'),
            ('tomb_chou', '甲', '丑', '己', 5, 'weak'),
        ]
        for birth_key, day_master, month_branch, principal, score, verdict \
                in checks:
            out, pillars = run_birth(BIRTHS[birth_key])
            modern = out['modern']
            self.assertEqual(out['month_branch'], month_branch, birth_key)
            self.assertEqual(modern['verdict'], verdict, birth_key)
            self.assertEqual(modern['score'], score, birth_key)
            self.assertEqual(modern['classification_status'], 'uncertain',
                             birth_key)
            self.assertIsNone(modern['definite_classification'], birth_key)
            self.assertEqual(modern['uncertainty_flags'],
                             ['tomb_de_ling_zero_provisional'], birth_key)
            self.assertEqual(out['agreement']['relationship'],
                             'modern_uncertain', birth_key)
            de_ling = modern['components']['de_ling']
            self.assertEqual(de_ling['score'], 0, birth_key)
            self.assertEqual(de_ling['sources'], [{
                'kind': 'tomb_principal_unreviewed',
                'branch': month_branch, 'stem': principal,
                'relation': 'unreviewed', 'weight': 0, 'contribution': 0,
                'counted': True}], birth_key)
            self.assertIn('四库月本气未审：得令分恒记 0（Q6）',
                          de_ling['conditions'], birth_key)
            self.assertTrue(validate_assessment(out)['valid'], birth_key)
            chart = chart_from_datetime(BIRTHS[birth_key])
            self.assertTrue(
                audit_component_counts(chart['pillars'],
                                       day_master)['all_passed'], birth_key)

    def test_earth_provisional_real_births(self):
        for birth_key, score in (('earth_mao', 20), ('earth_hai', 33)):
            out, _ = run_birth(BIRTHS[birth_key])
            modern = out['modern']
            self.assertEqual(modern['verdict'], 'balanced', birth_key)
            self.assertEqual(modern['score'], score, birth_key)
            self.assertEqual(modern['classification_status'],
                             'provisional_incomplete', birth_key)
            self.assertIsNone(modern['definite_classification'], birth_key)
            self.assertEqual(modern['uncertainty_flags'],
                             ['earth_de_di_uncalibrated'], birth_key)
            self.assertEqual(out['agreement']['relationship'],
                             'modern_provisional', birth_key)
            self.assertIn('Q5：土日主得地未校准，只计余根；分数为研究性暂定分，'
                          '不输出确定旺衰分类。',
                          modern['components']['de_di']['conditions'],
                          birth_key)
            self.assertTrue(validate_assessment(out)['valid'], birth_key)

    def test_ding_provisional_real_births(self):
        out, _ = run_birth(BIRTHS['ding_you'])
        modern = out['modern']
        self.assertEqual((modern['verdict'], modern['score']), ('balanced', 41))
        self.assertEqual(modern['classification_status'],
                         'provisional_incomplete')
        self.assertIsNone(modern['definite_classification'])
        self.assertEqual(modern['uncertainty_flags'],
                         ['ding_de_di_uncalibrated'])
        # 丁×酉 is not a tomb month: de_ling is a real principal-qi score.
        self.assertEqual(
            modern['components']['de_ling']['sources'][0]['kind'],
            'principal_qi')
        self.assertIn('Q5：丁日主得地未校准，只计余根；分数为研究性暂定分，'
                      '不输出确定旺衰分类。',
                      modern['components']['de_di']['conditions'])
        self.assertTrue(validate_assessment(out)['valid'])

    def test_ding_and_tomb_flags_combine_q5_dominates(self):
        # 丁×戌 carries both gaps; status is provisional_incomplete
        # (Q5), not uncertain (Q6 alone), and both flags are listed.
        out, _ = run_birth(BIRTHS['ding_xu'])
        modern = out['modern']
        self.assertEqual((modern['verdict'], modern['score']), ('balanced', 39))
        self.assertEqual(modern['classification_status'],
                         'provisional_incomplete')
        self.assertIsNone(modern['definite_classification'])
        self.assertEqual(modern['uncertainty_flags'], [
            'ding_de_di_uncalibrated', 'tomb_de_ling_zero_provisional'])
        self.assertEqual(modern['components']['de_ling']['score'], 0)
        self.assertEqual(out['agreement']['relationship'],
                         'modern_provisional')
        self.assertTrue(validate_assessment(out)['valid'])

    def test_q5_q6_status_precedence_in_matrix(self):
        cells = _matrix_cells(
            coverage_matrix(siling_si_pilot=si_pilot_for_1927()))
        ding_chou = cells[('丁', '丑')]
        self.assertEqual(ding_chou['classification_status'],
                         'provisional_incomplete')
        self.assertEqual(ding_chou['uncertainty_flags'], [
            'ding_de_di_uncalibrated', 'tomb_de_ling_zero_provisional'])
        jia_chou = cells[('甲', '丑')]
        self.assertEqual(jia_chou['classification_status'], 'uncertain')
        self.assertEqual(jia_chou['uncertainty_flags'],
                         ['tomb_de_ling_zero_provisional'])


class CongCandidateTests(unittest.TestCase):
    def test_cong_cai_synthetic_expanded_screen(self):
        # Visible stems 庚/戊/辛 vs day 甲: controls_me / i_control /
        # controls_me — all opposing only under the Q4-expanded screen
        # (the narrow weak screen would NOT fire: i_control is 财).
        pillars = synthetic_pillars(['庚申', '戊戌', '甲子', '辛酉'])
        result = identify_cong_candidates(pillars, '甲')
        self.assertTrue(result['screen_triggered'])
        self.assertEqual(result['screen_kinds'], ['cong_cai'])
        self.assertEqual(result['screen_reason'], 'cong_candidate_unresolved')
        self.assertEqual(len(result['candidates']), 1)
        candidate = result['candidates'][0]
        self.assertEqual(candidate['kind'], 'cong_cai')
        self.assertEqual(candidate['name_cn'], '从财候选')
        self.assertEqual(candidate['establishment'], 'not_judged')
        self.assertIsNone(candidate['verdict'])
        self.assertTrue(candidate['trigger_conditions']['no_roots'])
        self.assertTrue(candidate['trigger_conditions']['no_visible_support'])
        self.assertTrue(candidate['trigger_conditions']
                        ['visible_all_opposing_expanded'])
        self.assertFalse(candidate['trigger_conditions']
                         ['visible_all_opposing_weak_narrow'])
        self.assertTrue(candidate['trigger_conditions']
                        ['has_i_control_direction'])
        self.assertEqual(candidate['evidence']['visible_relations'],
                         ['controls_me', 'i_control', 'controls_me'])
        out = assess_strength(pillars, '甲')
        self.assertEqual(out['classical']['classification'], 'indeterminate')
        self.assertEqual(out['modern']['verdict'], 'abstain')
        self.assertEqual(out['modern']['abstain_reason'],
                         'cong_candidate_unresolved')
        self.assertTrue(audit_component_counts(pillars, '甲')['all_passed'])
        self.assertTrue(validate_assessment(out)['valid'])

    def test_cong_ruo_narrow_synthetic(self):
        pillars = synthetic_pillars(['庚申', '庚申', '甲子', '辛酉'])
        result = identify_cong_candidates(pillars, '甲')
        self.assertTrue(result['screen_triggered'])
        self.assertEqual(result['screen_kinds'], ['cong_ruo'])
        candidate = result['candidates'][0]
        self.assertEqual(candidate['kind'], 'cong_ruo')
        self.assertFalse(candidate['trigger_conditions']
                         ['has_i_control_direction'])
        self.assertTrue(candidate['trigger_conditions']
                        ['visible_all_opposing_weak_narrow'])
        self.assertEqual(candidate['establishment'], 'not_judged')
        self.assertIsNone(candidate['verdict'])

    def test_cong_qiang_identified_but_never_abstains(self):
        pillars = synthetic_pillars(['壬子', '乙亥', '甲寅', '癸亥'])
        result = identify_cong_candidates(pillars, '甲')
        self.assertFalse(result['screen_triggered'])
        self.assertEqual(result['screen_kinds'], [])
        self.assertIsNone(result['screen_reason'])
        self.assertEqual(len(result['candidates']), 1)
        candidate = result['candidates'][0]
        self.assertEqual(candidate['kind'], 'cong_qiang')
        self.assertEqual(candidate['establishment'], 'not_judged')
        self.assertIsNone(candidate['verdict'])
        out = assess_strength(pillars, '甲')
        self.assertEqual(out['modern']['verdict'], 'strong')
        self.assertEqual(out['modern']['score'], 91)
        self.assertEqual(_components(out),
                         {'de_ling': 20, 'de_di': 35, 'de_shi': 30,
                          'shengfu_hidden': 10, 'kexiehao': -4})
        self.assertTrue(validate_assessment(out)['valid'])

    def test_cong_guard_reviewed_weak_still_scores(self):
        # Q2 lock (2026-11-25): the 1978-09-20 乙酉 chart DOES trigger
        # the cong_cai screen (visible 戊/辛/辛 = i_control /
        # controls_me / controls_me, no roots) AND matches the reviewed
        # isolated_control predicate — the guard (abstain 4 applies
        # only when no reviewed predicate matched) keeps the modern
        # layer scoring weak -35 instead of abstaining.
        out, pillars = run_birth(BIRTHS['wood_you_weak'])
        self.assertEqual(pillars, ['戊午', '辛酉', '乙酉', '辛巳'])
        self.assertEqual(
            out['classical']['matched_predicate']['predicate_id'],
            'isolated_control')
        result = identify_cong_candidates(
            chart_from_datetime(BIRTHS['wood_you_weak'])['pillars'], '乙')
        self.assertTrue(result['screen_triggered'])
        self.assertEqual(result['screen_kinds'], ['cong_cai'])
        self.assertEqual(result['candidates'][0]['establishment'],
                         'not_judged')
        self.assertEqual(out['modern']['verdict'], 'weak')
        self.assertEqual(out['modern']['score'], -35)
        self.assertIsNone(out['modern']['abstain_reason'])
        self.assertEqual(out['modern']['cong_candidates'], result)

    def test_cong_candidates_never_establish_across_matrix(self):
        pilot = si_pilot_for_1927()
        for day_master in STEMS:
            for month_branch in BRANCHES:
                pillars = default_coverage_template(day_master, month_branch)
                out = assess_strength(pillars, day_master,
                                      siling_si_pilot=pilot)
                for candidate in out['modern']['cong_candidates'][
                        'candidates']:
                    self.assertEqual(candidate['establishment'],
                                     'not_judged',
                                     (day_master, month_branch))
                    self.assertIsNone(candidate['verdict'],
                                      (day_master, month_branch))

    def test_cong_invalid_input(self):
        with self.assertRaises(ValueError):
            identify_cong_candidates(
                synthetic_pillars(['庚申', '庚申', '甲子', '辛酉']), '乙')


class InteractionConditionTests(unittest.TestCase):
    def test_clash_recorded_only_no_deduction_no_abstain(self):
        # 金近 miss 辛盘 carries two 卯酉冲 records and still scores
        # modern strong 83: Q3-A records the clash, never deducts.
        out, _ = run_birth(BIRTHS['metal_near_miss_xin'])
        effects = interaction_conditions(
            chart_from_datetime(
                BIRTHS['metal_near_miss_xin'])['pillars'], '辛')
        self.assertTrue(effects['has_interactions'])
        self.assertEqual(effects['score_adjustment_total'], 0)
        self.assertEqual(len(effects['records']), 2)
        for record in effects['records']:
            self.assertEqual(record['kind'], 'branch_six_clash')
            self.assertEqual(record['score_adjustment'], 0)
            self.assertEqual(record['effect_on_strength'],
                             'recorded_only_no_score_adjustment')
            self.assertTrue(record['conditions'])
            self.assertIn('Q3-A', record['limitation'])
        self.assertEqual(out['modern']['verdict'], 'strong')
        self.assertEqual(out['modern']['score'], 83)
        self.assertEqual(
            out['modern']['interaction_effects']['score_adjustment_total'], 0)
        self.assertEqual(out['modern']['interaction_effects'], effects)

    def test_harm_and_harmony_synthetic_recorded_only(self):
        pillars = synthetic_pillars(['甲申', '乙亥', '丙子', '丁丑'])
        effects = interaction_conditions(pillars, '丙')
        kinds = sorted(r['kind'] for r in effects['records'])
        self.assertEqual(kinds, ['branch_six_harm', 'branch_six_harmony'])
        self.assertEqual(effects['score_adjustment_total'], 0)
        for record in effects['records']:
            self.assertEqual(record['score_adjustment'], 0)
            self.assertEqual(record['effect_on_strength'],
                             'recorded_only_no_score_adjustment')
        out = assess_strength(pillars, '丙')
        self.assertEqual((out['modern']['verdict'], out['modern']['score']),
                         ('weak', 1))

    def test_transformation_records_abstain_not_deduction(self):
        # 丙辛合: the record is an abstention marker, not a deduction —
        # score_adjustment is None (not 0), yet the total stays 0.
        effects = interaction_conditions(
            chart_from_datetime(
                BIRTHS['metal_near_miss_geng'])['pillars'], '庚')
        self.assertEqual(len(effects['records']), 1)
        record = effects['records'][0]
        self.assertEqual(record['kind'], 'stem_five_combination')
        self.assertEqual(record['effect_on_strength'],
                         'abstain_transformation_unresolved')
        self.assertIsNone(record['score_adjustment'])
        self.assertEqual(effects['score_adjustment_total'], 0)
        out, _ = run_birth(BIRTHS['metal_near_miss_geng'])
        self.assertEqual(out['modern']['verdict'], 'abstain')
        self.assertEqual(out['modern']['abstain_reason'],
                         'transformation_candidate_unresolved')

    def test_no_interaction_chart(self):
        effects = interaction_conditions(
            chart_from_datetime(
                BIRTHS['wood_mao_positive'])['pillars'], '甲')
        self.assertFalse(effects['has_interactions'])
        self.assertEqual(effects['records'], [])
        self.assertEqual(effects['score_adjustment_total'], 0)

    def test_interaction_governance_flags(self):
        effects = interaction_conditions(
            chart_from_datetime(
                BIRTHS['metal_near_miss_xin'])['pillars'], '辛')
        self.assertEqual(effects['model_kind'], 'modern_engineering')
        self.assertTrue(effects['research_only'])
        self.assertFalse(effects['public_enabled'])
        self.assertFalse(effects['ai_enabled'])


class SensitivityTests(unittest.TestCase):
    def _chart(self, birth_key):
        chart = chart_from_datetime(BIRTHS[birth_key])
        return chart['pillars'], chart['day_master']['stem']

    def test_balanced_chart_single_flip(self):
        pillars, day_master = self._chart('balanced')
        result = sensitivity_analysis(pillars, day_master)
        self.assertEqual(result['base_score'], 36)
        self.assertEqual(result['base_band'], 'balanced')
        self.assertEqual(result['perturbation_count'], 28)
        self.assertEqual(result['flip_count'], 1)
        self.assertFalse(result['verdict_stable'])
        self.assertEqual(result['nearest_boundary_distance'], 21)
        self.assertEqual(
            [(f['parameter'], f['delta'], f['score'], f['band'])
             for f in result['flips']],
            [('weight.kexiehao.opposing_each', 5, 66, 'strong')])
        self.assertEqual(result['model_kind'], 'modern_engineering')
        self.assertTrue(result['research_only'])

    def test_stable_extremes_have_no_flips(self):
        for birth_key, score, nearest in (
                ('wood_mao_positive', 105, 45), ('wood_you_weak', -35, 50)):
            pillars, day_master = self._chart(birth_key)
            result = sensitivity_analysis(pillars, day_master)
            self.assertEqual(result['base_score'], score, birth_key)
            self.assertEqual(result['perturbation_count'], 28, birth_key)
            self.assertEqual(result['flip_count'], 0, birth_key)
            self.assertTrue(result['verdict_stable'], birth_key)
            self.assertEqual(result['nearest_boundary_distance'], nearest,
                             birth_key)

    def test_tomb_weak_chart_single_flip(self):
        pillars, day_master = self._chart('tomb_wei')
        result = sensitivity_analysis(pillars, day_master)
        self.assertEqual(result['base_score'], 0)
        self.assertEqual(result['base_band'], 'weak')
        self.assertEqual(result['nearest_boundary_distance'], 15)
        self.assertEqual(
            [(f['parameter'], f['delta'], f['score'], f['band'])
             for f in result['flips']],
            [('weight.kexiehao.opposing_each', 5, 45, 'balanced')])

    def test_lu_pilot_chart_three_flips(self):
        chart = chart_from_datetime(BIRTHS['lu_positive'])
        result = sensitivity_analysis(chart['pillars'], '丙',
                                      siling_si_pilot=si_pilot_for_1927())
        self.assertEqual(result['base_score'], 70)
        self.assertEqual(result['base_band'], 'strong')
        self.assertEqual(result['perturbation_count'], 28)
        self.assertEqual(result['flip_count'], 3)
        self.assertFalse(result['verdict_stable'])
        self.assertEqual(result['nearest_boundary_distance'], 10)
        self.assertEqual(
            [(f['parameter'], f['delta'], f['score'], f['band'])
             for f in result['flips']],
            [('weight.de_shi.visible_support_each', -5, 55, 'balanced'),
             ('weight.shengfu_hidden.hidden_support_each', -5, 50,
              'balanced'),
             ('weight.kexiehao.opposing_each', -5, 58, 'balanced')])

    def test_custom_steps_and_empty_steps(self):
        pillars, day_master = self._chart('balanced')
        custom = sensitivity_analysis(pillars, day_master,
                                      threshold_steps=(5,), weight_steps=(1,))
        self.assertEqual(custom['perturbation_count'], 24)
        self.assertEqual(custom['flip_count'], 0)
        self.assertTrue(custom['verdict_stable'])
        empty = sensitivity_analysis(pillars, day_master,
                                     threshold_steps=(), weight_steps=())
        self.assertEqual(empty['perturbation_count'], 0)
        self.assertEqual(empty['flip_count'], 0)
        self.assertTrue(empty['verdict_stable'])
        self.assertEqual(empty['nearest_boundary_distance'], 21)
        # A 50-point threshold step skips the two moves that would
        # invert the threshold order; only 2 threshold perturbations run.
        wide = sensitivity_analysis(pillars, day_master,
                                    threshold_steps=(50,))
        self.assertEqual(wide['perturbation_count'], 22)
        threshold_params = sorted(
            p['parameter'] for p in wide['perturbations']
            if p['parameter'].startswith('threshold.'))
        self.assertEqual(threshold_params, ['threshold.strong_at_least',
                                            'threshold.weak_at_most'])

    def test_abstain_chart_has_no_perturbations(self):
        pillars, day_master = self._chart('earth_unbuildable')
        result = sensitivity_analysis(pillars, day_master)
        self.assertIsNone(result['base_score'])
        self.assertIsNone(result['base_band'])
        self.assertEqual(result['perturbations'], [])
        self.assertEqual(result['flips'], [])
        self.assertIsNone(result['verdict_stable'])
        self.assertIsNone(result['nearest_boundary_distance'])
        self.assertIn('弃判', result['note'])

    def test_perturbations_are_real_recomputations(self):
        # Every reported perturbation score/band equals an independent
        # assess_strength run with the same override — sensitivity is a
        # real recomputation, not a hand calculation.
        pillars, day_master = self._chart('balanced')
        result = sensitivity_analysis(pillars, day_master)
        for entry in result['perturbations']:
            parameter, delta = entry['parameter'], entry['delta']
            if parameter.startswith('threshold.'):
                key = parameter.split('.', 1)[1]
                rerun = assess_strength(
                    pillars, day_master,
                    modern_thresholds={key: MODERN_THRESHOLDS[key] + delta})
            else:
                _, section, key = parameter.split('.')
                rerun = assess_strength(
                    pillars, day_master,
                    modern_weights={section: {
                        key: MODERN_WEIGHTS[section][key] + delta}})
            self.assertEqual(rerun['modern']['score'], entry['score'],
                             parameter)
            self.assertEqual(rerun['modern']['score_band'], entry['band'],
                             parameter)
        # Spot-check the one flip directly.
        rerun = assess_strength(
            pillars, day_master,
            modern_weights={'kexiehao': {'opposing_each': 3}})
        self.assertEqual((rerun['modern']['score'],
                          rerun['modern']['verdict']), (66, 'strong'))

    def test_sensitivity_does_not_mutate_pinned_tables(self):
        weights_before = copy.deepcopy(MODERN_WEIGHTS)
        thresholds_before = dict(MODERN_THRESHOLDS)
        pillars, day_master = self._chart('balanced')
        sensitivity_analysis(pillars, day_master)
        self.assertEqual(MODERN_WEIGHTS, weights_before)
        self.assertEqual(MODERN_THRESHOLDS, thresholds_before)


class DivergenceTests(unittest.TestCase):
    def test_agree_case(self):
        out, _ = run_birth(BIRTHS['water_positive'])
        explained = divergence_explanation(out)
        self.assertEqual(explained['classical'], 'strong')
        self.assertEqual(explained['modern'], 'strong')
        self.assertEqual(explained['relationship'], 'agree')
        self.assertEqual(explained['closest_predicates'], [])
        self.assertEqual(explained['reasons'], [
            '两层结论一致（strong），但依据不同：古典谓词 vs 工程评分，'
            '仍并列报告。'])
        self.assertEqual(explained['summary_lines'][0],
                         '古典层：strong；现代层：strong（agree）。')
        self.assertEqual(explained['modern_evidence']['score'], 103)

    def test_modern_abstains_case(self):
        out, _ = run_birth(BIRTHS['lu_positive'])
        explained = divergence_explanation(out)
        self.assertEqual(explained['classical'], 'strong')
        self.assertEqual(explained['modern'], 'abstain')
        self.assertEqual(explained['relationship'], 'modern_abstains')
        self.assertEqual(explained['closest_predicates'], [])
        self.assertIn('弃判不是弱判', explained['reasons'][0])
        self.assertEqual(explained['modern_evidence']['abstain_reason'],
                         'siling_si_pilot_not_verified')
        self.assertEqual(explained['summary_lines'][0],
                         '古典层：strong；现代层：abstain（modern_abstains）。')

    def test_classical_indeterminate_names_closest_predicate(self):
        out, _ = run_birth(BIRTHS['water_near_miss_ren'])
        explained = divergence_explanation(out)
        self.assertEqual(explained['classical'], 'indeterminate')
        self.assertEqual(explained['modern'], 'strong')
        self.assertEqual(explained['relationship'], 'classical_indeterminate')
        closest = explained['closest_predicates']
        self.assertEqual(len(closest), 7)
        counts = [c['failed_condition_count'] for c in closest]
        self.assertEqual(counts, sorted(counts))
        self.assertEqual(closest[0]['predicate_id'],
                         'pure_generating_support_water')
        self.assertEqual(closest[0]['failed_condition_count'], 1)
        self.assertEqual(closest[0]['failed_conditions'], ['visible比_present'])
        self.assertIn('最接近的谓词 pure_generating_support_water',
                      explained['reasons'][0])
        self.assertIn('工程近似', explained['reasons'][1])
        self.assertEqual(explained['classical_evidence'], {
            'matched_predicate': None,
            'blockers': ['outside_reviewed_sufficient_conditions']})

    def test_tomb_uncertain_divergence(self):
        out, _ = run_birth(BIRTHS['tomb_wei'])
        explained = divergence_explanation(out)
        self.assertEqual(explained['relationship'], 'modern_uncertain')
        closest = explained['closest_predicates']
        self.assertEqual(closest[0]['predicate_id'], 'isolated_control')
        self.assertEqual(closest[0]['failed_condition_count'], 6)
        self.assertEqual(closest[0]['failed_conditions'], [
            'wood_day_master', 'reviewed_control_month',
            'no_support_in_any_position', 'visible_earth_metal_only',
            'month_principal_exposed_with_root',
            'no_unresolved_interactions'])

    def test_provisional_divergence(self):
        out, _ = run_birth(BIRTHS['ding_you'])
        explained = divergence_explanation(out)
        self.assertEqual(explained['relationship'], 'modern_provisional')
        self.assertEqual(explained['modern_evidence']['score'], 41)
        self.assertEqual(
            explained['modern_evidence']['classification_status'],
            'provisional_incomplete')
        self.assertIsNone(
            explained['modern_evidence']['definite_classification'])
        self.assertEqual(explained['closest_predicates'][0]['predicate_id'],
                         'commanding_visible_support')
        self.assertEqual(
            explained['closest_predicates'][0]['failed_condition_count'], 3)

    def test_modern_disabled_divergence(self):
        out, _ = run_birth(BIRTHS['water_positive'], include_modern=False)
        explained = divergence_explanation(out)
        self.assertEqual(explained['classical'], 'strong')
        self.assertIsNone(explained['modern'])
        self.assertEqual(explained['relationship'], 'not_comparable')
        self.assertEqual(explained['reasons'], ['现代模型未启用，无从比较。'])
        self.assertEqual(explained['modern_evidence'],
                         {'verdict': None, 'note': '现代模型未启用。'})

    def test_divergence_invalid_input(self):
        with self.assertRaises(ValueError):
            divergence_explanation({})
        with self.assertRaises(ValueError):
            divergence_explanation(None)

    def test_divergence_mirrors_agreement_block(self):
        for birth_key in ('wood_mao_positive', 'lu_positive',
                          'water_near_miss_ren', 'tomb_wei', 'ding_you',
                          'earth_unbuildable', 'f4_positive'):
            out, _ = run_birth(BIRTHS[birth_key])
            explained = divergence_explanation(out)
            block = out['agreement']['divergence']
            self.assertEqual(explained['classical'], block['classical'],
                             birth_key)
            self.assertEqual(explained['modern'], block['modern'], birth_key)
            self.assertEqual(explained['reasons'], block['reasons'],
                             birth_key)
            self.assertEqual(explained['classical_evidence'],
                             block['classical_evidence'], birth_key)
            self.assertEqual(explained['modern_evidence'],
                             block['modern_evidence'], birth_key)
            self.assertEqual(explained['model_kind'], 'modern_engineering')
            self.assertTrue(explained['research_only'])


class AuditValidateTests(unittest.TestCase):
    def _chart(self, birth_key):
        chart = chart_from_datetime(BIRTHS[birth_key])
        return chart['pillars'], chart['day_master']['stem']

    def test_audit_all_pinned_births(self):
        for birth_key in ('wood_mao_positive', 'water_positive',
                          'bingwu_positive', 'wood_hai_positive',
                          'wood_you_weak', 'balanced',
                          'metal_near_miss_xin', 'metal_near_miss_geng',
                          'earth_unbuildable'):
            pillars, day_master = self._chart(birth_key)
            audit = audit_component_counts(pillars, day_master)
            self.assertTrue(audit['all_passed'], birth_key)
            self.assertEqual(audit['model_kind'], 'modern_engineering')
            self.assertTrue(audit['research_only'])

    def test_audit_abstain_has_no_score(self):
        pillars, day_master = self._chart('earth_unbuildable')
        audit = audit_component_counts(pillars, day_master)
        self.assertTrue(audit['all_passed'])
        self.assertEqual(audit['verdict'], 'abstain')
        self.assertEqual(audit['abstain_reason'],
                         'earth_form_unbuildable_tj0112')
        names = {c['name'] for c in audit['checks']}
        self.assertIn('abstain_has_no_score', names)
        self.assertIn('stem_partition_no_double_count', names)
        self.assertIn('root_partition_no_double_count', names)

    def test_audit_detects_weight_drift(self):
        # Counter-proof: audit recomputes from the factor layer with the
        # pinned v1 weights, so moving a weight must fail the audit.
        pillars, day_master = self._chart('water_positive')
        with mock.patch.dict(MODERN_WEIGHTS['de_shi'],
                             {'visible_support_each': 0}):
            audit = audit_component_counts(pillars, day_master)
        self.assertFalse(audit['all_passed'])
        failed = [c['name'] for c in audit['checks'] if not c['passed']]
        self.assertIn('de_shi_recomputed', failed)

    def test_validate_all_pinned_births(self):
        for birth_key in ('wood_mao_positive', 'water_positive',
                          'bingwu_positive', 'wood_hai_positive',
                          'wood_you_weak', 'balanced',
                          'metal_near_miss_xin', 'metal_near_miss_geng',
                          'earth_unbuildable', 'tomb_wei', 'tomb_xu',
                          'tomb_chou', 'ding_you', 'ding_xu', 'earth_mao',
                          'earth_hai'):
            out, _ = run_birth(BIRTHS[birth_key])
            result = validate_assessment(out)
            self.assertTrue(result['valid'], birth_key)

    def test_validate_abstain_and_disabled(self):
        out, _ = run_birth(BIRTHS['earth_unbuildable'])
        self.assertTrue(validate_assessment(out)['valid'])
        out, _ = run_birth(BIRTHS['water_positive'], include_modern=False)
        result = validate_assessment(out)
        self.assertTrue(result['valid'])
        self.assertEqual(
            [c['name'] for c in result['checks']],
            ['governance_flags', 'modern_disabled'])

    def test_validate_tamper_detection(self):
        # Tampered total: score no longer equals the component sum.
        out, _ = run_birth(BIRTHS['water_positive'])
        tampered = copy.deepcopy(out)
        tampered['modern']['score'] += 1
        result = validate_assessment(tampered)
        self.assertFalse(result['valid'])
        failed = [c['name'] for c in result['checks'] if not c['passed']]
        # 103 -> 104 stays in the strong band, so only the sum check fails.
        self.assertEqual(failed, ['total_equals_component_sum'])
        # Tampered governance flag.
        tampered = copy.deepcopy(out)
        tampered['research_only'] = False
        result = validate_assessment(tampered)
        self.assertFalse(result['valid'])
        self.assertIn('governance_flags',
                      [c['name'] for c in result['checks']
                       if not c['passed']])
        # Definite classification smuggled into a provisional result.
        out, _ = run_birth(BIRTHS['ding_you'])
        tampered = copy.deepcopy(out)
        tampered['modern']['definite_classification'] = 'balanced'
        result = validate_assessment(tampered)
        self.assertFalse(result['valid'])
        self.assertIn('no_definite_classification_when_not_definite',
                      [c['name'] for c in result['checks']
                       if not c['passed']])
        # Component pushed out of its documented range.
        out, _ = run_birth(BIRTHS['water_positive'])
        tampered = copy.deepcopy(out)
        tampered['modern']['components']['de_ling']['score'] = 31
        result = validate_assessment(tampered)
        self.assertFalse(result['valid'])
        self.assertIn('component_range_de_ling',
                      [c['name'] for c in result['checks']
                       if not c['passed']])
        # A cong candidate claiming establishment — on an abstain result
        # and on a computed result alike.
        pillars = synthetic_pillars(['庚申', '戊戌', '甲子', '辛酉'])
        out = assess_strength(pillars, '甲')
        tampered = copy.deepcopy(out)
        # Abstain results carry cong candidates; flip one to established.
        tampered['modern']['cong_candidates']['candidates'][0][
            'establishment'] = 'established'
        result = validate_assessment(tampered)
        self.assertFalse(result['valid'])
        self.assertIn('cong_candidates_never_establish',
                      [c['name'] for c in result['checks']
                       if not c['passed']])
        pillars = synthetic_pillars(['壬子', '乙亥', '甲寅', '癸亥'])
        out = assess_strength(pillars, '甲')
        tampered = copy.deepcopy(out)
        tampered['modern']['cong_candidates']['candidates'][0][
            'establishment'] = 'established'
        result = validate_assessment(tampered)
        self.assertFalse(result['valid'])
        self.assertIn('cong_candidates_never_establish',
                      [c['name'] for c in result['checks']
                       if not c['passed']])

    def test_validate_boundary_thresholds_exact(self):
        # Boundary-exact: score == strong_at_least is strong, score ==
        # weak_at_most is weak; one point inside stays balanced.
        pillars, day_master = self._chart('balanced')  # score 36
        for thresholds, verdict in (
                ({'strong_at_least': 36}, 'strong'),
                ({'weak_at_most': 36}, 'weak'),
                ({'strong_at_least': 37}, 'balanced'),
                ({'weak_at_most': 35}, 'balanced')):
            out = assess_strength(pillars, day_master,
                                  modern_thresholds=thresholds)
            self.assertEqual(out['modern']['verdict'], verdict, thresholds)
            self.assertEqual(out['modern']['score_band'], verdict, thresholds)
            self.assertTrue(validate_assessment(out)['valid'], thresholds)

    def test_validate_rejects_bad_overrides(self):
        pillars, day_master = self._chart('balanced')
        with self.assertRaises(ValueError):
            assess_strength(pillars, day_master,
                            modern_weights={'no_such_section': {'x': 1}})
        with self.assertRaises(ValueError):
            assess_strength(pillars, day_master,
                            modern_thresholds={'strong_at_least': 10,
                                               'weak_at_most': 20})
        with self.assertRaises(ValueError):
            assess_strength(pillars, day_master,
                            modern_thresholds={'no_such_threshold': 1})

    def test_score_range_constant(self):
        self.assertEqual(MODERN_SCORE_RANGE, (-35, 105))

    def test_override_results_stay_valid_within_weight_domain(self):
        # In-domain weight overrides (signs kept): the engine's own
        # validator must accept every result it produces, and every
        # component's counted sources must sum to its score.
        pillars_by_key = {
            key: self._chart(key)
            for key in ('wood_mao_positive', 'balanced', 'wood_you_weak',
                        'tomb_wei')}
        overrides = [
            {'de_shi': {'visible_support_each': 15}},
            {'de_shi': {'visible_support_each': 20}},
            {'de_shi': {'visible_support_each': 5}},
            {'shengfu_hidden': {'hidden_support_each': 3}},
            {'shengfu_hidden': {'hidden_support_each': 1}},
            {'kexiehao': {'opposing_each': -3}},
            {'kexiehao': {'opposing_each': -1}},
            {'de_di': {'heavy_root_each': 20}},
            {'de_di': {'other_root_each': 10}},
            {'de_ling': {'same_element': 25}},
        ]
        for key, (pillars, day_master) in pillars_by_key.items():
            for override in overrides:
                out = assess_strength(pillars, day_master,
                                      modern_weights=override)
                modern = out['modern']
                self.assertNotEqual(modern['verdict'], 'abstain',
                                    (key, override))
                result = validate_assessment(out)
                self.assertTrue(result['valid'], (key, override,
                                 [c for c in result['checks']
                                  if not c['passed']]))
                low, high = MODERN_SCORE_RANGE
                self.assertTrue(low <= modern['score'] <= high,
                                (key, override))

    def test_override_cap_truncation_pins_scores(self):
        # Caps still bind under overrides: the capped component score is
        # unchanged, only the marginal source's contribution is truncated.
        pillars, day_master = self._chart('wood_mao_positive')
        out = assess_strength(
            pillars, day_master,
            modern_weights={'de_shi': {'visible_support_each': 20}})
        self.assertEqual(out['modern']['components']['de_shi']['score'], 30)
        self.assertEqual(out['modern']['score'], 105)
        self.assertTrue(validate_assessment(out)['valid'])
        out = assess_strength(
            pillars, day_master,
            modern_weights={'shengfu_hidden': {'hidden_support_each': 3}})
        self.assertEqual(
            out['modern']['components']['shengfu_hidden']['score'], 10)
        self.assertEqual(out['modern']['score'], 105)
        self.assertTrue(validate_assessment(out)['valid'])
        pillars, day_master = self._chart('wood_you_weak')
        out = assess_strength(
            pillars, day_master,
            modern_weights={'kexiehao': {'opposing_each': -3}})
        self.assertEqual(out['modern']['components']['kexiehao']['score'],
                         -20)
        self.assertEqual(out['modern']['score'], -35)
        self.assertTrue(validate_assessment(out)['valid'])
        pillars, day_master = self._chart('wood_mao_positive')
        out = assess_strength(
            pillars, day_master,
            modern_weights={'de_di': {'heavy_root_each': 20}})
        self.assertEqual(out['modern']['components']['de_di']['score'], 35)
        self.assertEqual(out['modern']['score'], 105)
        self.assertTrue(validate_assessment(out)['valid'])

    def test_overrides_do_not_mutate_pinned_tables(self):
        weights_before = copy.deepcopy(MODERN_WEIGHTS)
        thresholds_before = dict(MODERN_THRESHOLDS)
        pillars, day_master = self._chart('balanced')
        assess_strength(pillars, day_master,
                        modern_weights={'de_shi': {'visible_support_each': 1}},
                        modern_thresholds={'strong_at_least': 99})
        self.assertEqual(MODERN_WEIGHTS, weights_before)
        self.assertEqual(MODERN_THRESHOLDS, thresholds_before)


if __name__ == '__main__':
    unittest.main()
