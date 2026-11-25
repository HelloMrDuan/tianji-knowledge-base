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
    ENGINE_VARIANT, MODERN_MODEL_ID, MODERN_THRESHOLDS, MODERN_WEIGHTS,
    PREDICATES, assess_strength)
from tianji_kb.calendar_provider_guard import provider_identity

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


if __name__ == '__main__':
    unittest.main()
