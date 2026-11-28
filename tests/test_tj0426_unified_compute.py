"""Lane 6（TJ-0426，U-01/U-02/U-03）统一内部计算入口测试。

分两类，诚实区分：

* 纯本地测试（无密封数据可跑）：pin 常量 / pin 校验 / 各页裁剪
  allowlist / 研究输出隔离 / 逐页标注 / 晋升条件标注 / 输入校验 /
  缓存机制 / 接线 fail-safe（装配失败时页按原路走、pin 漂移 loud）。
  其中裁剪与隔离测试用合成装配夹具（明确标注为 plumbing 夹具，
  不是真实命盘，不作任何 Golden 断言）。
* 密封环境测试（``LiveAssemblyTests``）：同一真实盘 f2
  （2024-02-11T16:27:07+08:00，甲辰 / 丙寅 / 乙巳 / 甲申）的一次
  排盘多页复用与 life 四源一致性。公开检出无密封 ``data/`` 时整类
  SkipTest（不伪造通过）；装配环境下实跑。

五页公开输出的入口前后对照：本地无法执行 ``execute_scenario``
（公开检出无密封 ``data/``，``execute("bazi")`` 报
RuntimeUnavailable；改动前亦然——不是本 lane 引入的限制），故不
在此谎称跑过五页。对照依据为：(a) 场景 builder 仍直接调
``execute("bazi", ...)``（与 batch 4 之前一致；#598 修复把 batch 4
的 9 处 ``execute → cached_execute`` 换回去了，因为
``cached_execute`` 直调 ``engine.execute``，绕过了 fail-closed
测试所 patch 的 ``scenario_engine.execute`` 缝，使 6 处拒判测试
失效——见回报；统一入口自身仍用 ``cached_execute`` 做单次排盘）；
(b) 下面的缓存等值性机制测试；(c) 密封环境的正式验收复核五页
（见回报）。
"""

import copy
import unittest

from tianji_kb import unified_compute as uc
from tianji_kb.unified_compute import (
    UnifiedComputeInputError,
    UnifiedComputePinError,
    clear_unified_compute_cache,
    page_annotations,
    promotion_conditions,
    trim_for_bazi_profile,
    trim_for_career,
    trim_for_compatibility,
    trim_for_life,
    trim_for_romance,
    validate_engine_pins,
)

F2_BIRTH = '2024-02-11T16:27:07+08:00'
F2_GANZHI = ['甲辰', '丙寅', '乙巳', '甲申']

# 公开 presentation 的四个键：裁剪输出中永不得出现。
PUBLIC_PRESENTATION_KEYS = (
    'strength_presentation', 'pattern_presentation',
    'dayun_presentation', 'xiyong_presentation',
)


def _synthetic_assembly():
    """裁剪 plumbing 夹具：合成装配，不是真实命盘，不作 Golden 断言。"""
    pillars = [
        {'name': name, 'ganzhi': ganzhi,
         'stem': {'value': ganzhi[0], 'ten_god': '比肩'},
         'branch': {'value': ganzhi[1], 'hidden_stems': []}}
        for name, ganzhi in zip(('year', 'month', 'day', 'hour'),
                                F2_GANZHI)]
    return {
        'variant': uc.UNIFIED_COMPUTE_VARIANT,
        'birth_value': F2_BIRTH,
        'zone': None,
        'research_only': True,
        'public_enabled': False,
        'ai_enabled': False,
        'traditional_role': 'male',
        'target_year': 2025,
        'chart': {
            'pillars': pillars,
            'day_master': {'stem': '乙', 'element': '木',
                           'polarity': '阴'},
            'month_branch': '寅',
            'ganzhi': list(F2_GANZHI),
        },
        'natal_envelope': {'result': {'pillars': pillars}},
        'research': {
            'strength': {'variant': uc.PIN_STRENGTH_ENGINE_VARIANT,
                         'research_only': True, 'public_enabled': False,
                         'ai_enabled': False},
            'pattern': {'variant': uc.PIN_PATTERN_ENGINE_VARIANT,
                        'research_only': True, 'public_enabled': False,
                        'ai_enabled': False},
            'pattern_d1': {'attempted': False,
                           'status': 'not_attempted_here'},
            'xiyong': {'variant': uc.PIN_XIYONG_ENGINE_VARIANT,
                       'research_only': True, 'public_enabled': False,
                       'ai_enabled': False, 'unified_verdict': None},
            'tiaohou': {'variant': 'tiaohou-qiongtong-v1'},
            'bingyao': {'variant': 'bingyao-shenfeng-v1'},
            'pilots': {'yin_pilot': None, 'si_pilot': None,
                       'note': 'month_not_piloted'},
            'errors': [],
        },
        'flow_year': {'year': 2025, 'ganzhi': '乙巳', 'stem': '乙',
                      'branch': '巳', 'stem_ten_god': '比肩'},
        'annual_xiyong': {'variant': 'bazi-xiyong-annual-contract-v1'},
        'combination': {'variant': uc.PIN_COMBINATION_ENGINE_VARIANT,
                        'research_only': True, 'public_enabled': False,
                        'ai_enabled': False, 'overall_effect': None},
        'combination_status': 'assembled',
    }


class PinTests(unittest.TestCase):
    def test_pin_constants_are_the_documented_values(self):
        self.assertEqual(uc.PIN_PATTERN_ENGINE_VARIANT,
                         'bazi-pattern-engine-v2')
        self.assertEqual(uc.PIN_STRENGTH_ENGINE_VARIANT,
                         'bazi-strength-engine-v1')
        self.assertEqual(uc.PIN_XIYONG_ENGINE_VARIANT,
                         'bazi-xiyong-engine-v1')
        self.assertEqual(uc.PIN_COMBINATION_ENGINE_VARIANT,
                         'bazi-combination-engine-v1')
        self.assertEqual(uc.PIN_FLOW_BOUNDARY_VARIANT,
                         'bazi-annual-lichun-boundary-v1')
        self.assertEqual(uc.UNIFIED_COMPUTE_VARIANT,
                         'unified-compute-entry-v1')
        self.assertIs(uc.RESEARCH_ONLY, True)
        self.assertIs(uc.PUBLIC_ENABLED, False)
        self.assertIs(uc.AI_ENABLED, False)

    def test_pins_match_live_engine_constants_when_importable(self):
        try:
            from tianji_kb.bazi_combination_engine import (
                PATTERN_ENGINE_VARIANT_V2,
                STRENGTH_ENGINE_VARIANT,
                VARIANT as comb_variant,
                XIYONG_ENGINE_VARIANT,
            )
            from tianji_kb.bazi_pattern_engine import (
                PATTERN_ENGINE_VARIANT,
            )
            from tianji_kb.bazi_strength_engine import (
                ENGINE_VARIANT as strength_variant,
            )
            from tianji_kb.bazi_xiyong_engine import (
                XIYONG_ENGINE_VARIANT as xiyong_variant,
            )
        except Exception as error:  # noqa: BLE001 - 密封依赖缺失即跳过
            raise unittest.SkipTest(
                'live engine modules unavailable: %s' % error)
        self.assertEqual(uc.PIN_PATTERN_ENGINE_VARIANT,
                         PATTERN_ENGINE_VARIANT)
        self.assertEqual(uc.PIN_PATTERN_ENGINE_VARIANT,
                         PATTERN_ENGINE_VARIANT_V2)
        self.assertEqual(uc.PIN_STRENGTH_ENGINE_VARIANT,
                         strength_variant)
        self.assertEqual(uc.PIN_STRENGTH_ENGINE_VARIANT,
                         STRENGTH_ENGINE_VARIANT)
        self.assertEqual(uc.PIN_XIYONG_ENGINE_VARIANT, xiyong_variant)
        self.assertEqual(uc.PIN_XIYONG_ENGINE_VARIANT,
                         XIYONG_ENGINE_VARIANT)
        self.assertEqual(uc.PIN_COMBINATION_ENGINE_VARIANT,
                         comb_variant)

    def test_validate_accepts_correct_variants(self):
        assembly = _synthetic_assembly()
        self.assertTrue(validate_engine_pins(
            strength=assembly['research']['strength'],
            pattern=assembly['research']['pattern'],
            xiyong=assembly['research']['xiyong'],
            combination=assembly['combination']))

    def test_validate_rejects_wrong_pattern_variant(self):
        bad = {'variant': 'bazi-pattern-engine-v1',
               'research_only': True, 'public_enabled': False,
               'ai_enabled': False}
        with self.assertRaises(UnifiedComputePinError):
            validate_engine_pins(pattern=bad)

    def test_validate_rejects_wrong_strength_variant(self):
        bad = {'variant': 'bazi-strength-engine-v2',
               'research_only': True, 'public_enabled': False,
               'ai_enabled': False}
        with self.assertRaises(UnifiedComputePinError):
            validate_engine_pins(strength=bad)

    def test_validate_rejects_missing_variant(self):
        with self.assertRaises(UnifiedComputePinError):
            validate_engine_pins(xiyong={'research_only': True})

    def test_validate_rejects_flag_drift(self):
        bad = {'variant': uc.PIN_XIYONG_ENGINE_VARIANT,
               'research_only': True, 'public_enabled': True,
               'ai_enabled': False}
        with self.assertRaises(UnifiedComputePinError):
            validate_engine_pins(xiyong=bad)

    def test_validate_skips_unprovided_systems(self):
        self.assertTrue(validate_engine_pins())


class TrimTests(unittest.TestCase):
    def test_bazi_profile_trim_has_exactly_its_keys(self):
        trim = trim_for_bazi_profile(_synthetic_assembly())
        self.assertEqual(set(trim), {
            'variant', 'page', 'research_only', 'public_enabled',
            'ai_enabled', 'chart', 'research'})
        self.assertEqual(trim['page'], 'bazi-profile')
        self.assertNotIn('target_year', trim)
        self.assertNotIn('flow_year', trim)
        self.assertNotIn('combination', trim)
        self.assertNotIn('identity_anchor', trim)

    def test_career_romance_life_trims_carry_flow_year(self):
        for fn, page in ((trim_for_career, 'career'),
                         (trim_for_romance, 'romance'),
                         (trim_for_life, 'life')):
            trim = fn(_synthetic_assembly())
            self.assertEqual(trim['page'], page)
            self.assertEqual(trim['target_year'], 2025)
            self.assertEqual(trim['flow_year']['ganzhi'], '乙巳')

    def test_life_trim_identity_anchor_matches_chart(self):
        trim = trim_for_life(_synthetic_assembly())
        anchor = trim['identity_anchor']
        self.assertEqual(anchor['pillars'], trim['chart']['pillars'])
        self.assertEqual(anchor['day_master'],
                         trim['chart']['day_master'])
        self.assertEqual(anchor['target_year'], 2025)
        self.assertEqual(anchor['target_ganzhi'], '乙巳')
        self.assertEqual(anchor['target_branch'], '巳')

    def test_compatibility_trim_has_two_persons_no_flow_year(self):
        pair = {'person_a': _synthetic_assembly(),
                'person_b': _synthetic_assembly()}
        trim = trim_for_compatibility(pair)
        self.assertEqual(set(trim), {
            'variant', 'page', 'research_only', 'public_enabled',
            'ai_enabled', 'person_a', 'person_b'})
        self.assertEqual(trim['page'], 'compatibility')
        self.assertEqual(trim['person_a']['chart']['ganzhi'], F2_GANZHI)
        self.assertEqual(trim['person_b']['chart']['ganzhi'], F2_GANZHI)

    def test_no_trim_carries_any_public_presentation_key(self):
        assembly = _synthetic_assembly()
        trims = [trim_for_bazi_profile(assembly),
                 trim_for_career(assembly),
                 trim_for_romance(assembly),
                 trim_for_life(assembly)]
        pair = {'person_a': assembly, 'person_b': assembly}
        trims.append(trim_for_compatibility(pair))
        for trim in trims:
            self.assertFalse(
                any(key in trim for key in PUBLIC_PRESENTATION_KEYS),
                'trim must never carry a public presentation key')
            research = trim.get('research') or {}
            self.assertFalse(
                any(key in research for key in PUBLIC_PRESENTATION_KEYS))
            for person in (trim.get('person_a'), trim.get('person_b')):
                if person is not None:
                    self.assertFalse(any(
                        key in person for key in PUBLIC_PRESENTATION_KEYS))

    def test_research_blocks_stay_research_only_in_trims(self):
        trim = trim_for_bazi_profile(_synthetic_assembly())
        research = trim['research']
        self.assertIs(research['research_only'], True)
        self.assertIs(research['public_enabled'], False)
        self.assertIs(research['ai_enabled'], False)
        self.assertIsNone(research['xiyong']['unified_verdict'])
        self.assertIsNone(research['combination']['overall_effect'])
        self.assertEqual(research['pattern_d1']['status'],
                         'not_attempted_here')

    def test_trims_are_deep_copies(self):
        assembly = _synthetic_assembly()
        trim = trim_for_career(assembly)
        trim['chart']['pillars'][0]['ganzhi'] = ' forged'
        trim['research']['strength']['variant'] = 'forged'
        self.assertEqual(assembly['chart']['pillars'][0]['ganzhi'], '甲辰')
        self.assertEqual(
            assembly['research']['strength']['variant'],
            uc.PIN_STRENGTH_ENGINE_VARIANT)


class AnnotationTests(unittest.TestCase):
    def test_page_annotations_cover_five_pages(self):
        annotations = page_annotations()
        self.assertEqual(set(annotations), {
            'bazi-profile', 'career', 'romance', 'compatibility',
            'life'})
        for page, row in annotations.items():
            self.assertEqual(row['page'], page)
            self.assertIsInstance(row['attached_research'], list)
            self.assertIsInstance(row['structure_only'], list)
            self.assertTrue(row['note'])

    def test_romance_and_compatibility_attach_no_research(self):
        annotations = page_annotations()
        self.assertEqual(annotations['romance']['attached_research'], [])
        self.assertEqual(
            annotations['compatibility']['attached_research'], [])
        self.assertTrue(annotations['romance']['structure_only'])
        self.assertTrue(annotations['compatibility']['structure_only'])

    def test_bazi_profile_lists_four_gates(self):
        attached = page_annotations()['bazi-profile']['attached_research']
        joined = ' '.join(attached)
        for token in ('U1', 'D-1', '大运', '喜用'):
            self.assertIn(token, joined)

    def test_annotations_are_copies(self):
        first = page_annotations()
        first['romance']['attached_research'].append('forged')
        self.assertEqual(page_annotations()['romance']
                         ['attached_research'], [])


class PromotionTableTests(unittest.TestCase):
    def test_every_row_is_research_only_and_not_proposed(self):
        rows = promotion_conditions()
        self.assertGreaterEqual(len(rows), 10)
        for row in rows:
            self.assertEqual(row['current_status'], 'research_only')
            self.assertIs(row['promotion_proposed'], False)
            self.assertTrue(row['promotion_condition'])
            self.assertTrue(row['capability'])

    def test_table_names_the_blocked_promotions(self):
        joined = ' '.join(row['capability']
                          for row in promotion_conditions())
        for token in ('强度现代模型', '格局现代层', '扶抑现代层',
                      '组合跨层效力', '六爻用神映射', '分日司令',
                      '紫微', '格局用神'):
            self.assertIn(token, joined)

    def test_overall_effect_promotion_never_standalone(self):
        rows = {row['capability']: row for row in promotion_conditions()}
        row = rows['组合跨层效力（overall_effect；TJ-017.2 真定义）']
        self.assertIn('TJ-013.2', row['promotion_condition'])

    def test_table_is_a_copy(self):
        rows = promotion_conditions()
        rows[0]['promotion_proposed'] = True
        self.assertIs(promotion_conditions()[0]['promotion_proposed'],
                      False)


class InputValidationTests(unittest.TestCase):
    def test_rejects_naive_birth(self):
        with self.assertRaises(UnifiedComputeInputError):
            uc._validate_birth_value('2024-02-11T16:27:07')

    def test_rejects_subsecond_birth(self):
        with self.assertRaises(UnifiedComputeInputError):
            uc._validate_birth_value('2024-02-11T16:27:07.5+08:00')

    def test_rejects_unparseable_birth(self):
        with self.assertRaises(UnifiedComputeInputError):
            uc._validate_birth_value('not-a-date')

    def test_rejects_nonstring_birth(self):
        with self.assertRaises(UnifiedComputeInputError):
            uc._validate_birth_value(20240211)

    def test_accepts_f2_birth(self):
        self.assertEqual(uc._validate_birth_value(F2_BIRTH), F2_BIRTH)

    def test_rejects_bad_target_year(self):
        for bad in (1899, 2101, '2025', 2025.0, None.__class__):
            with self.assertRaises(UnifiedComputeInputError):
                uc._validate_target_year(bad)

    def test_accepts_target_year_bounds(self):
        self.assertEqual(uc._validate_target_year(1900), 1900)
        self.assertEqual(uc._validate_target_year(2100), 2100)
        self.assertIsNone(uc._validate_target_year(None))

    def test_rejects_bad_traditional_role(self):
        with self.assertRaises(UnifiedComputeInputError):
            uc._validate_traditional_role('unknown')

    def test_accepts_roles(self):
        self.assertEqual(uc._validate_traditional_role('male'), 'male')
        self.assertIsNone(uc._validate_traditional_role(None))


class CacheMechanismTests(unittest.TestCase):
    def setUp(self):
        clear_unified_compute_cache()

    def tearDown(self):
        clear_unified_compute_cache()

    def test_canonical_key_is_order_independent(self):
        self.assertEqual(
            uc._canonical_key({'b': 1, 'a': {'d': 4, 'c': 3}}),
            uc._canonical_key({'a': {'c': 3, 'd': 4}, 'b': 1}))

    def test_canonical_key_none_for_unserializable(self):
        self.assertIsNone(uc._canonical_key({'fn': object()}))

    def test_cache_put_evicts_oldest_past_max(self):
        for i in range(uc._CACHE_MAX_ENTRIES + 2):
            uc._cache_put(uc._CORE_CACHE, 'k%d' % i, {'i': i})
        self.assertEqual(len(uc._CORE_CACHE), uc._CACHE_MAX_ENTRIES)
        self.assertNotIn('k0', uc._CORE_CACHE)
        self.assertNotIn('k1', uc._CORE_CACHE)
        self.assertIn('k%d' % (uc._CACHE_MAX_ENTRIES + 1),
                      uc._CORE_CACHE)

    def test_cached_execute_dedupes_identical_inputs(self):
        import tianji_kb.engine as engine

        calls = []
        sentinel = {'result': {'pillars': [{'ganzhi': '甲辰'}]},
                    'trace': [], 'rule_matches': [], 'evidence': {}}
        real_execute = engine.execute

        def fake_execute(domain, inputs, allow_research=False):
            calls.append((domain, dict(inputs), allow_research))
            return copy.deepcopy(sentinel)

        engine.execute = fake_execute
        try:
            first = uc.cached_execute(
                'bazi', {'value': F2_BIRTH, 'include_relations': True})
            second = uc.cached_execute(
                'bazi', {'include_relations': True, 'value': F2_BIRTH})
            self.assertEqual(len(calls), 1)
            self.assertEqual(first, second)
            self.assertIsNot(first, second)
            first['result']['pillars'][0]['ganzhi'] = 'forged'
            third = uc.cached_execute(
                'bazi', {'value': F2_BIRTH, 'include_relations': True})
            self.assertEqual(third['result']['pillars'][0]['ganzhi'],
                             '甲辰')
            self.assertEqual(len(calls), 1)
        finally:
            engine.execute = real_execute

    def test_cached_execute_bypasses_cache_for_unserializable(self):
        import tianji_kb.engine as engine

        calls = []
        real_execute = engine.execute

        def fake_execute(domain, inputs, allow_research=False):
            calls.append(1)
            return {'ok': True}

        engine.execute = fake_execute
        try:
            uc.cached_execute('bazi', {'value': object()})
            uc.cached_execute('bazi', {'value': object()})
            self.assertEqual(len(calls), 2)
        finally:
            engine.execute = real_execute


class WiringFailSafeTests(unittest.TestCase):
    def test_unified_assembly_returns_none_when_entry_fails(self):
        import tianji_kb.scenario_engine as se

        real = se.assemble_birth

        def failing(*args, **kwargs):
            raise RuntimeError('sealed runtime unavailable')

        se.assemble_birth = failing
        try:
            self.assertIsNone(
                se._unified_assembly(F2_BIRTH, target_year=2025))
        finally:
            se.assemble_birth = real

    def test_unified_assembly_re_raises_pin_errors(self):
        import tianji_kb.scenario_engine as se

        real = se.assemble_birth

        def pin_drift(*args, **kwargs):
            raise UnifiedComputePinError('pattern variant drifted')

        se.assemble_birth = pin_drift
        try:
            with self.assertRaises(UnifiedComputePinError):
                se._unified_assembly(F2_BIRTH, target_year=2025)
        finally:
            se.assemble_birth = real

    def test_assert_chart_passes_on_match_and_fails_on_drift(self):
        import tianji_kb.scenario_engine as se

        trim = trim_for_career(_synthetic_assembly())
        pillars = _synthetic_assembly()['chart']['pillars']
        day_master = {'stem': '乙', 'element': '木', 'polarity': '阴'}
        se._assert_unified_chart(trim, pillars, day_master)
        drifted = copy.deepcopy(pillars)
        drifted[0] = dict(drifted[0], ganzhi='乙巳')
        with self.assertRaises(ValueError):
            se._assert_unified_chart(trim, drifted, day_master)
        with self.assertRaises(ValueError):
            se._assert_unified_chart(
                trim, pillars,
                {'stem': '甲', 'element': '木', 'polarity': '阳'})

    def test_assert_flow_year_passes_and_fails(self):
        import tianji_kb.scenario_engine as se

        trim = trim_for_career(_synthetic_assembly())
        se._assert_unified_flow_year(trim, '乙巳')
        with self.assertRaises(ValueError):
            se._assert_unified_flow_year(trim, '丙午')
        se._assert_unified_flow_year(None, '丙午')
        se._assert_unified_chart(None, [], {})

    def test_public_gate_modules_untouched_variants(self):
        # 四门控的公开 presentation Variant 常量必须仍是已批值：
        # 接线只改 execute 调用，不动任何 *_public.py。
        from tianji_kb import bazi_dayun_public as dayun_pub
        from tianji_kb import bazi_pattern_public as pattern_pub
        from tianji_kb import bazi_strength_public as strength_pub
        from tianji_kb import bazi_xiyong_public as xiyong_pub

        self.assertEqual(
            strength_pub.VARIANT, 'strength-public-presentation-v1')
        self.assertEqual(
            pattern_pub.VARIANT, 'bazi-pattern-public-presentation-v1')
        self.assertEqual(
            xiyong_pub.VARIANT, 'xiyong-public-presentation-v1')
        self.assertEqual(
            dayun_pub.VARIANT, 'dayun-public-presentation-v1')


class LiveAssemblyTests(unittest.TestCase):
    """密封环境：f2 真实盘一次排盘多页复用 + life 四源一致性。

    公开检出无密封 data/ 时整类跳过（setUpClass 探针失败即 Skip）。
    """

    @classmethod
    def setUpClass(cls):
        clear_unified_compute_cache()
        try:
            cls.assembly = uc.assemble_birth(
                F2_BIRTH, traditional_role='male', target_year=2025)
        except Exception as error:  # noqa: BLE001 - 密封依赖缺失即跳过
            raise unittest.SkipTest(
                'live unified assembly unavailable: %s' % error)
        cls.trims = {
            'bazi-profile': trim_for_bazi_profile(cls.assembly),
            'career': trim_for_career(cls.assembly),
            'romance': trim_for_romance(cls.assembly),
            'life': trim_for_life(cls.assembly),
        }

    @classmethod
    def tearDownClass(cls):
        clear_unified_compute_cache()

    def test_five_trims_share_one_chart(self):
        charts = [trim['chart'] for trim in self.trims.values()]
        for chart in charts[1:]:
            self.assertEqual(chart['ganzhi'], F2_GANZHI)
            self.assertEqual(chart['day_master']['stem'], '乙')
            self.assertEqual(chart['month_branch'], '寅')
        self.assertEqual(charts[0]['ganzhi'], charts[1]['ganzhi'])

    def test_flow_year_identical_across_pages(self):
        for page in ('career', 'romance', 'life'):
            flow = self.trims[page]['flow_year']
            self.assertEqual(flow['year'], 2025)
            self.assertEqual(flow['ganzhi'],
                             self.trims['career']['flow_year']['ganzhi'])

    def test_life_identity_anchor_matches_sections(self):
        anchor = self.trims['life']['identity_anchor']
        self.assertEqual(anchor['pillars'],
                         self.trims['life']['chart']['pillars'])
        self.assertEqual(anchor['target_ganzhi'],
                         self.trims['life']['flow_year']['ganzhi'])
        self.assertEqual(anchor['target_branch'],
                         self.trims['life']['flow_year']['branch'])

    def test_engine_variants_pinned(self):
        research = self.assembly['research']
        self.assertEqual(
            research['strength']['variant'],
            uc.PIN_STRENGTH_ENGINE_VARIANT)
        self.assertEqual(
            research['pattern']['variant'],
            uc.PIN_PATTERN_ENGINE_VARIANT)
        self.assertEqual(
            research['xiyong']['variant'],
            uc.PIN_XIYONG_ENGINE_VARIANT)
        self.assertIsNone(research['xiyong']['unified_verdict'])

    def test_pattern_d1_not_rederived_here(self):
        self.assertEqual(
            self.assembly['research']['pattern_d1']['status'],
            'not_attempted_here')

    def test_combination_overall_effect_stays_none(self):
        if self.assembly['combination'] is None:
            self.skipTest('combination not assembled: %s'
                          % self.assembly['research']['errors'])
        self.assertIsNone(
            self.assembly['combination']['overall_effect'])

    def test_no_trim_carries_public_presentation(self):
        for trim in self.trims.values():
            self.assertFalse(any(
                key in trim for key in PUBLIC_PRESENTATION_KEYS))


if __name__ == '__main__':
    unittest.main()
