"""Lane G（TJ-0427，TJ-031.19）统一计算入口工程硬化测试。

只测本 lane 的范围：缓存生命周期、并发/跨请求数据隔离、缓存 key
维度隔离、正式投影 allowlist、pin 漂移 loud 失败、公开输出等价。
不改任何引擎 pin、不改任何公开 presentation allowlist、不晋升
任何研究字段、不调用 AI。

分三类，诚实区分：

* 纯本地测试（无密封数据可跑）：缓存机制 / key 维度 / 投影 /
  pin 校验 / 等价快照。装配级测试用 stub 引擎（在
  ``setUp`` 里 patch 真实引擎函数的模块属性与入口自身的
  ``cached_execute`` / ``_live_pilot``，只替换计算，不替换入口
  的缓存 / key / 投影代码）；夹具装配明确标注为 plumbing 夹具，
  不是真实命盘，不作任何 Golden 断言。
* 目标年层测试用真实 ``calendar``（本地可用，2025-07-01 口径
  ``乙巳``已核实）+ 真实 ``evaluate_annual_xiyong`` /
  ``classical_dayun_timeline`` / ``combine`` 调用链：这些步骤
  本身按入口设计 fail-soft（失败只记入 errors），测试只断言
  缓存 key 维度与隔离，不依赖它们本地成功。唯一例外是
  ``bazi_core.ten_god``：它在年层是 try 块之外的密封数据查找，
  本地无 ``data/`` 即 raise，故 stub 为固定值（F2 流年干乙对日
  主乙为比肩）；不 stub 则任何带目标年的装配本地都无法跑到
  年层缓存断言——这是环境限制，不是入口行为。
* 密封环境测试不在此文件：真实盘装配仍由
  ``test_tj0426_unified_compute.LiveAssemblyTests`` 覆盖，本地
  SkipTest；五页公开输出的入口前后对照以本文件的等价快照
  （``test_tj0426`` 夹具的逐字段 SHA-256，改动前已取）为准，
  正式密封验收复核五页。
* Q3=A（用户裁定 2026-11-28 09:56）：统一入口向八字 / 事业 /
  人生总览三页服务完整 8 运大运序列，向各页服务流年查询数据
  （流年干支 + 立春边界区间）。等价口径随之改为：全部既有字段
  byte-identical、新块只 additive、无研究字段泄漏进正式投影。
  本地无密封 ``data/``，``classical_dayun_timeline`` /
  ``annual_lichun_boundaries`` 均须 stub（见
  ``_stub_engine_patchers``），只替换计算，不替换入口代码。
"""

import copy
import hashlib
import json
import unittest
from unittest import mock

from tianji_kb import unified_compute as uc
from tianji_kb.unified_compute import (
    UnifiedComputeInputError,
    UnifiedComputePinError,
    clear_unified_compute_cache,
    invalidate_unified_compute_cache,
    project_formal,
    project_formal_pair,
    unified_compute_cache_info,
    validate_engine_pins,
)

F2_BIRTH = '2024-02-11T16:27:07+08:00'
F2B_BIRTH = '2024-03-11T10:00:00+08:00'
F2_GANZHI = ['甲辰', '丙寅', '乙巳', '甲申']
F2B_GANZHI = ['乙巳', '丁卯', '丙午', '丁酉']

PUBLIC_PRESENTATION_KEYS = (
    'strength_presentation', 'pattern_presentation',
    'dayun_presentation', 'xiyong_presentation',
)

# 改动前（2026-11-28，基线 main 8c4e754c）对
# test_tj0426_unified_compute._synthetic_assembly() 的五份裁剪输出
# 逐顶层字段取的 SHA-256（json.dumps(sort_keys=True,
# ensure_ascii=False)）。Q3=A 后裁剪新增 additive 字段（见
# ALLOWED_NEW_TRIM_KEYS），既有字段必须逐字段 byte-identical；
# page_annotations / promotion_conditions 未动，仍整份 hash 对照。
PRE_CHANGE_FIELD_HASHES = {
    'bazi-profile': {
        'ai_enabled': 'fcbcf165908dd18a9e49f7ff27810176db8e9f63b4352213741664245224f8aa',
        'chart': 'ba0e13586bec65427e7a8c8d862f3bb937c34703f15b47ed35555f93f6150fc2',
        'page': 'b683fa6f6f90f85edcb08db46db17a30fb6049344cd88a1b58a9f1dacbba2d0b',
        'public_enabled': 'fcbcf165908dd18a9e49f7ff27810176db8e9f63b4352213741664245224f8aa',
        'research': 'e144a628933f6b651163e08544ab8a19de75e84a9b232e23e6a685f985dd9c26',
        'research_only': 'b5bea41b6c623f7c09f1bf24dcae58ebab3c0cdd90ad966bc43a45b44867e12b',
        'variant': '1614363234a48a240904f03c7dcadcd3280525fdc2203e66e97c4520371f661c',
    },
    'career': {
        'ai_enabled': 'fcbcf165908dd18a9e49f7ff27810176db8e9f63b4352213741664245224f8aa',
        'chart': 'ba0e13586bec65427e7a8c8d862f3bb937c34703f15b47ed35555f93f6150fc2',
        'flow_year': '552aa705bc1bc5f2b62d700f6f86ffd32db0d66b89fdb61d6f24d710dbfadc80',
        'page': '9ecd5d4bd0afaadb20d57a8536aafebfd0b22314cc9293a4ac26d46c07abb6e7',
        'public_enabled': 'fcbcf165908dd18a9e49f7ff27810176db8e9f63b4352213741664245224f8aa',
        'research': 'e144a628933f6b651163e08544ab8a19de75e84a9b232e23e6a685f985dd9c26',
        'research_only': 'b5bea41b6c623f7c09f1bf24dcae58ebab3c0cdd90ad966bc43a45b44867e12b',
        'target_year': 'b2b2f104d32c638903e151a9b20d6e27b41d8c0c84cf8458738f83ca2f1dd744',
        'variant': '1614363234a48a240904f03c7dcadcd3280525fdc2203e66e97c4520371f661c',
    },
    'romance': {
        'ai_enabled': 'fcbcf165908dd18a9e49f7ff27810176db8e9f63b4352213741664245224f8aa',
        'chart': 'ba0e13586bec65427e7a8c8d862f3bb937c34703f15b47ed35555f93f6150fc2',
        'flow_year': '552aa705bc1bc5f2b62d700f6f86ffd32db0d66b89fdb61d6f24d710dbfadc80',
        'page': '4778f9fe9c445587329f6029ef55dd29d4a2fe957cace1a79a4cb4f1a7c76c9a',
        'public_enabled': 'fcbcf165908dd18a9e49f7ff27810176db8e9f63b4352213741664245224f8aa',
        'research': 'e144a628933f6b651163e08544ab8a19de75e84a9b232e23e6a685f985dd9c26',
        'research_only': 'b5bea41b6c623f7c09f1bf24dcae58ebab3c0cdd90ad966bc43a45b44867e12b',
        'target_year': 'b2b2f104d32c638903e151a9b20d6e27b41d8c0c84cf8458738f83ca2f1dd744',
        'variant': '1614363234a48a240904f03c7dcadcd3280525fdc2203e66e97c4520371f661c',
    },
    'life': {
        'ai_enabled': 'fcbcf165908dd18a9e49f7ff27810176db8e9f63b4352213741664245224f8aa',
        'chart': 'ba0e13586bec65427e7a8c8d862f3bb937c34703f15b47ed35555f93f6150fc2',
        'flow_year': '552aa705bc1bc5f2b62d700f6f86ffd32db0d66b89fdb61d6f24d710dbfadc80',
        'identity_anchor': '327f154f84499d0b3710e9c6261fbb0f2140491f9bd40e2345becf963a0820aa',
        'page': '633836d01096ff547c7e101e10abf4bf3d4d9b83f5928231f5ad40ca1a388887',
        'public_enabled': 'fcbcf165908dd18a9e49f7ff27810176db8e9f63b4352213741664245224f8aa',
        'research': 'e144a628933f6b651163e08544ab8a19de75e84a9b232e23e6a685f985dd9c26',
        'research_only': 'b5bea41b6c623f7c09f1bf24dcae58ebab3c0cdd90ad966bc43a45b44867e12b',
        'target_year': 'b2b2f104d32c638903e151a9b20d6e27b41d8c0c84cf8458738f83ca2f1dd744',
        'variant': '1614363234a48a240904f03c7dcadcd3280525fdc2203e66e97c4520371f661c',
    },
    'compatibility': {
        'ai_enabled': 'fcbcf165908dd18a9e49f7ff27810176db8e9f63b4352213741664245224f8aa',
        'page': '318ea11c2fddbd4a17430c585c30a6093248e55200d0f85c7ac2f1d27f010b61',
        'person_a': 'bc660db80e89830b963079cc0de977628c260b20eded298f88ac414642b10ad0',
        'person_b': '63885ad5a425eb131b4394ddb562b462d01cc5c137f9e1856b8a0d3b1083a746',
        'public_enabled': 'fcbcf165908dd18a9e49f7ff27810176db8e9f63b4352213741664245224f8aa',
        'research_only': 'b5bea41b6c623f7c09f1bf24dcae58ebab3c0cdd90ad966bc43a45b44867e12b',
        'variant': '1614363234a48a240904f03c7dcadcd3280525fdc2203e66e97c4520371f661c',
    },
}
PRE_CHANGE_TABLE_HASHES = {
    'page_annotations': (
        'c00da59d0510c78811a28d65ffe8eea145d261aca176b0d3d4515a2bee7fba19'),
    'promotion_conditions': (
        'ec7c3943d56bb1f6c09232b837a485328e4adf652a5f6a42761ccb1581b2c9c7'),
}
# Q3=A 之后各裁剪允许新增的顶层字段（additive only；超出即回归）。
ALLOWED_NEW_TRIM_KEYS = {
    'bazi-profile': {'dayun', 'dayun_status'},
    'career': {'dayun', 'dayun_status', 'flow_boundary'},
    'romance': {'flow_boundary'},
    'life': {'dayun', 'dayun_status', 'flow_boundary'},
    'compatibility': set(),
}


def _fake_dayun_timeline():
    """8 运大运组合夹具：candidate_sequence(periods=8) 形态 + 逐运区间。"""
    ganzhi_cycle = ['丁卯', '戊辰', '己巳', '庚午',
                    '辛未', '壬申', '癸酉', '甲戌']
    rows = [{'period_index': i + 1, 'candidate_ganzhi': ganzhi,
             'stem': ganzhi[0], 'branch': ganzhi[1],
             'ten_god_relative_to_natal_day_stem': '比肩'}
            for i, ganzhi in enumerate(ganzhi_cycle)]
    return {
        'variant': 'dayun-classical-composition-v1',
        'status': 'converted',
        'traditional_role': 'male',
        'sequence': {'rows': rows},
        'sequence_time_alignment': [
            {'period_index': row['period_index'],
             'candidate_ganzhi': row['candidate_ganzhi'],
             'stem': row['stem'], 'branch': row['branch'],
             'ten_god_relative_to_natal_day_stem': '比肩',
             'start_interval': {
                 'earliest': '2030-01-01T00:00:00+08:00',
                 'latest': '2030-01-02T00:00:00+08:00',
                 'max_inclusive': True,
                 'basis': 'sanming_shichen_level',
                 'method': 'sanming_shichen_level',
                 'variant': 'bazi-dayun-adjacent-jie-research-v1'}}
            for row in rows],
    }


def _fake_flow_boundary():
    """流年立春边界夹具：annual_lichun_boundaries 原样输出形态。"""
    return {
        'variant': 'bazi-annual-lichun-boundary-v1',
        'day_master': '乙',
        'rows': [{'gregorian_lichun_year': 2025,
                  'start_inclusive': '2025-02-03T22:10:00+08:00',
                  'end_exclusive': '2026-02-04T04:00:00+08:00',
                  'ganzhi_in_interval': '乙巳',
                  'year_stem': '乙', 'year_branch': '巳'}],
    }


def _synthetic_assembly():
    """裁剪 / 投影 plumbing 夹具：合成装配，不是真实命盘。"""
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
        'dayun': {'status': 'assembled', 'periods': 8,
                  'traditional_role': 'male',
                  'timeline': _fake_dayun_timeline()},
        'dayun_status': 'assembled',
        'flow_boundary': _fake_flow_boundary(),
        'annual_xiyong': {'variant': 'bazi-xiyong-annual-contract-v1'},
        'combination': {'variant': uc.PIN_COMBINATION_ENGINE_VARIANT,
                        'research_only': True, 'public_enabled': False,
                        'ai_enabled': False, 'overall_effect': None},
        'combination_status': 'assembled',
    }


def _pillars_for(ganzhi_list, day_stem):
    return [
        {'name': name, 'ganzhi': ganzhi,
         'stem': {'value': ganzhi[0], 'ten_god': '比肩'},
         'branch': {'value': ganzhi[1], 'hidden_stems': []}}
        for name, ganzhi in zip(('year', 'month', 'day', 'hour'),
                                ganzhi_list)]


def _research_block(variant):
    return {'variant': variant, 'research_only': True,
            'public_enabled': False, 'ai_enabled': False}


def _walk_keys(obj, seen):
    """递归收集一个嵌套对象中出现过的所有 dict key。"""
    if isinstance(obj, dict):
        for key, value in obj.items():
            seen.add(key)
            _walk_keys(value, seen)
    elif isinstance(obj, (list, tuple)):
        for item in obj:
            _walk_keys(item, seen)


class CacheLifecycleTests(unittest.TestCase):
    def setUp(self):
        clear_unified_compute_cache()

    def tearDown(self):
        clear_unified_compute_cache()

    def test_clear_clears_all_three_layers(self):
        for cache in (uc._CORE_CACHE, uc._YEAR_CACHE, uc._EXECUTE_CACHE):
            uc._cache_put(cache, 'k', {'v': 1})
        self.assertEqual(unified_compute_cache_info()['core_entries'], 1)
        self.assertEqual(unified_compute_cache_info()['year_entries'], 1)
        self.assertEqual(
            unified_compute_cache_info()['execute_entries'], 1)
        clear_unified_compute_cache()
        self.assertEqual(unified_compute_cache_info(), {
            'core_entries': 0, 'year_entries': 0, 'execute_entries': 0,
            'max_entries_per_cache': 8, 'max_entries_total': 24})

    def test_each_cache_capped_at_eight_and_total_bounded(self):
        for cache in (uc._CORE_CACHE, uc._YEAR_CACHE, uc._EXECUTE_CACHE):
            for i in range(10):
                uc._cache_put(cache, 'k%d' % i, {'i': i})
            self.assertEqual(len(cache), 8)
        info = unified_compute_cache_info()
        self.assertEqual(info['max_entries_per_cache'], 8)
        self.assertEqual(info['max_entries_total'], 24)
        self.assertLessEqual(
            info['core_entries'] + info['year_entries']
            + info['execute_entries'], 24)

    def test_fifo_evicts_oldest_in_year_cache(self):
        for i in range(uc._CACHE_MAX_ENTRIES + 1):
            uc._cache_put(uc._YEAR_CACHE, 'y%d' % i, {'i': i})
        self.assertEqual(len(uc._YEAR_CACHE), uc._CACHE_MAX_ENTRIES)
        self.assertNotIn('y0', uc._YEAR_CACHE)
        self.assertIn('y%d' % uc._CACHE_MAX_ENTRIES, uc._YEAR_CACHE)

    def test_invalidate_removes_core_year_and_execute_entries(self):
        core_key = uc._canonical_key([F2_BIRTH, None])
        year_key = uc._canonical_key(
            [F2_BIRTH, None, 'male', 2025])
        exec_key = uc._canonical_key(['bazi', {
            'value': F2_BIRTH, 'include_relations': True,
            'include_xianchi': True}, False])
        uc._cache_put(uc._CORE_CACHE, core_key, {'core': True})
        uc._cache_put(uc._YEAR_CACHE, year_key, {'year': True})
        uc._cache_put(uc._EXECUTE_CACHE, exec_key, {'exec': True})
        removed = invalidate_unified_compute_cache(F2_BIRTH)
        self.assertEqual(removed, 3)
        self.assertEqual(unified_compute_cache_info()['core_entries'], 0)
        self.assertEqual(unified_compute_cache_info()['year_entries'], 0)
        self.assertEqual(
            unified_compute_cache_info()['execute_entries'], 0)

    def test_invalidate_scoped_to_one_role_and_year(self):
        core_key = uc._canonical_key([F2_BIRTH, None])
        male_key = uc._canonical_key(
            [F2_BIRTH, None, 'male', 2025])
        female_key = uc._canonical_key(
            [F2_BIRTH, None, 'female', 2025])
        other_year_key = uc._canonical_key(
            [F2_BIRTH, None, 'male', 2026])
        uc._cache_put(uc._CORE_CACHE, core_key, {'core': True})
        for key in (male_key, female_key, other_year_key):
            uc._cache_put(uc._YEAR_CACHE, key, {'year': True})
        removed = invalidate_unified_compute_cache(
            F2_BIRTH, traditional_role='male', target_year=2025)
        # 出生层（同一 birth/zone）+ 仅 male/2025 年层被删。
        self.assertEqual(removed, 2)
        self.assertNotIn(male_key, uc._YEAR_CACHE)
        self.assertIn(female_key, uc._YEAR_CACHE)
        self.assertIn(other_year_key, uc._YEAR_CACHE)

    def test_invalidate_unknown_key_returns_zero(self):
        self.assertEqual(invalidate_unified_compute_cache(F2_BIRTH), 0)

    def test_invalidate_rejects_bad_birth(self):
        with self.assertRaises(UnifiedComputeInputError):
            invalidate_unified_compute_cache('2024-02-11T16:27:07')

    def test_cache_info_is_read_only_snapshot(self):
        uc._cache_put(uc._CORE_CACHE, 'k', {'v': 1})
        info = unified_compute_cache_info()
        info['core_entries'] = 999
        self.assertEqual(
            unified_compute_cache_info()['core_entries'], 1)


class CacheKeyIsolationTests(unittest.TestCase):
    def test_core_key_dimensions(self):
        base = uc._canonical_key([F2_BIRTH, None])
        self.assertEqual(base, uc._canonical_key([F2_BIRTH, None]))
        self.assertNotEqual(
            base, uc._canonical_key([F2_BIRTH, 'Asia/Shanghai']))
        self.assertNotEqual(
            base, uc._canonical_key([F2B_BIRTH, None]))
        # 同一瞬时、不同时区写法：不同 key（安全 miss，不会串缓存）。
        self.assertNotEqual(
            base,
            uc._canonical_key(['2024-02-11T08:27:07+00:00', None]))

    def test_year_key_dimensions(self):
        def key(role, year, zone=None, birth=F2_BIRTH):
            return uc._canonical_key([birth, zone, role, year])

        base = key('male', 2025)
        self.assertEqual(base, key('male', 2025))
        self.assertNotEqual(base, key('female', 2025))
        self.assertNotEqual(base, key('male', 2026))
        self.assertNotEqual(base, key(None, 2025))
        self.assertNotEqual(base, key('male', None))
        self.assertNotEqual(base, key('male', 2025, 'Asia/Shanghai'))
        self.assertNotEqual(base, key('male', 2025, birth=F2B_BIRTH))

    def test_execute_key_dimensions(self):
        key_a = uc._canonical_key(['bazi', {'value': F2_BIRTH}, False])
        self.assertEqual(
            key_a, uc._canonical_key(['bazi', {'value': F2_BIRTH},
                                      False]))
        self.assertNotEqual(
            key_a, uc._canonical_key(['bazi', {'value': F2_BIRTH},
                                      True]))
        self.assertNotEqual(
            key_a, uc._canonical_key(['bazi', {'value': F2B_BIRTH},
                                      False]))
        # 输入 dict 的键顺序不影响 key（同一输入命中缓存）。
        self.assertEqual(
            uc._canonical_key(['bazi', {'a': 1, 'b': 2}, False]),
            uc._canonical_key(['bazi', {'b': 2, 'a': 1}, False]))


def _stub_engine_patchers(natal_calls):
    """Stub 计算层 patcher 清单（只替换计算，不替换入口代码）。

    覆盖：排盘（``cached_execute``，按出生瞬时返回不同四柱并计数）、
    司令试点、十神密封查找（``ten_god``，见文件头说明）、强度 /
    格局 / 调候 / 病药 / 喜用引擎、大运组合（``classical_dayun_timeline``，
    8 运 converted）、立春边界（``annual_lichun_boundaries``）、
    组合引擎（``combine``，恒返回合法 variant）。年层其余步骤
    （``calendar``、``evaluate_annual_xiyong``）走真实代码。
    """

    def fake_cached_execute(domain, inputs, allow_research=False):
        natal_calls.append((domain, dict(inputs), allow_research))
        birth = inputs['value']
        ganzhi = F2_GANZHI if birth == F2_BIRTH else F2B_GANZHI
        day_stem = '乙' if birth == F2_BIRTH else '丙'
        return {
            'result': {
                'pillars': _pillars_for(ganzhi, day_stem),
                'day_master': {'stem': day_stem, 'element': '木',
                               'polarity': '阴'},
            },
            'trace': [], 'rule_matches': [], 'evidence': {},
        }

    return [
        mock.patch.object(uc, 'cached_execute',
                          side_effect=fake_cached_execute),
        mock.patch.object(uc, '_live_pilot',
                          return_value=(None, 'month_not_piloted')),
        # 密封数据查找（见文件头说明）：F2 流年干乙对日主乙为比肩。
        mock.patch('tianji_kb.bazi_core.ten_god',
                   return_value='比肩'),
        mock.patch(
            'tianji_kb.bazi_strength_engine.assess_strength',
            side_effect=lambda *a, **k: dict(
                _research_block(uc.PIN_STRENGTH_ENGINE_VARIANT),
                marker='strength')),
        mock.patch(
            'tianji_kb.bazi_pattern_engine.evaluate_all',
            side_effect=lambda *a, **k: dict(
                _research_block(uc.PIN_PATTERN_ENGINE_VARIANT),
                marker='pattern')),
        mock.patch(
            'tianji_kb.bazi_tiaohou.tiaohou_lookup',
            return_value={'variant': 'tiaohou-qiongtong-v1'}),
        mock.patch(
            'tianji_kb.bazi_bingyao.bingyao_lookup',
            return_value={'variant': 'bingyao-shenfeng-v1'}),
        mock.patch(
            'tianji_kb.bazi_xiyong_engine.evaluate_xiyong',
            side_effect=lambda *a, **k: dict(
                _research_block(uc.PIN_XIYONG_ENGINE_VARIANT),
                unified_verdict=None, systems={})),
        mock.patch(
            'tianji_kb.bazi_dayun_compose.classical_dayun_timeline',
            side_effect=lambda *a, **k: copy.deepcopy(
                _fake_dayun_timeline())),
        mock.patch(
            'tianji_kb.bazi_annual_reference'
            '.annual_lichun_boundaries',
            side_effect=lambda *a, **k: copy.deepcopy(
                _fake_flow_boundary())),
        mock.patch(
            'tianji_kb.bazi_combination_engine.combine',
            side_effect=lambda *a, **k: dict(
                _research_block(uc.PIN_COMBINATION_ENGINE_VARIANT),
                overall_effect=None)),
    ]


class StubEngineAssemblyTests(unittest.TestCase):
    """stub 引擎下的装配级隔离测试：只替换计算，不替换入口代码。"""

    def setUp(self):
        clear_unified_compute_cache()
        self.natal_calls = []
        self.patchers = _stub_engine_patchers(self.natal_calls)
        for patcher in self.patchers:
            patcher.start()

    def tearDown(self):
        for patcher in reversed(self.patchers):
            patcher.stop()
        clear_unified_compute_cache()

    def test_same_inputs_hit_cache_second_call_free(self):
        first = uc.assemble_birth(F2_BIRTH)
        second = uc.assemble_birth(F2_BIRTH)
        self.assertEqual(len(self.natal_calls), 1)
        self.assertEqual(first, second)
        self.assertIsNot(first, second)
        self.assertIsNot(first['chart'], second['chart'])

    def test_different_zone_recomputes_core(self):
        uc.assemble_birth(F2_BIRTH, zone=None)
        uc.assemble_birth(F2_BIRTH, zone='Asia/Shanghai')
        self.assertEqual(len(self.natal_calls), 2)
        self.assertEqual(
            self.natal_calls[0][1].get('zone'), None)
        self.assertEqual(
            self.natal_calls[1][1].get('zone'), 'Asia/Shanghai')

    def test_different_birth_recomputes_core(self):
        uc.assemble_birth(F2_BIRTH)
        uc.assemble_birth(F2B_BIRTH)
        self.assertEqual(len(self.natal_calls), 2)

    def test_role_and_year_do_not_recompute_core_but_add_year_entries(
            self):
        uc.assemble_birth(F2_BIRTH, traditional_role='male',
                          target_year=2025)
        uc.assemble_birth(F2_BIRTH, traditional_role='female',
                          target_year=2025)
        uc.assemble_birth(F2_BIRTH, traditional_role='male',
                          target_year=2026)
        self.assertEqual(len(self.natal_calls), 1)
        self.assertEqual(len(uc._YEAR_CACHE), 3)
        # 同一 (role, year) 再调一次：年层命中，不再增长。
        uc.assemble_birth(F2_BIRTH, traditional_role='male',
                          target_year=2025)
        self.assertEqual(len(uc._YEAR_CACHE), 3)
        self.assertEqual(len(self.natal_calls), 1)

    def test_mutating_returned_assembly_does_not_pollute_cache(self):
        first = uc.assemble_birth(F2_BIRTH, traditional_role='male',
                                  target_year=2025)
        first['chart']['pillars'][0]['ganzhi'] = 'forged'
        first['chart']['day_master']['stem'] = 'forged'
        first['research']['strength']['variant'] = 'forged'
        first['research']['xiyong']['unified_verdict'] = 'forged'
        first['flow_year']['ganzhi'] = 'forged'
        first['research']['errors'].append(
            {'block': 'forged', 'reason': 'forged'})
        second = uc.assemble_birth(F2_BIRTH, traditional_role='male',
                                   target_year=2025)
        self.assertEqual(second['chart']['pillars'][0]['ganzhi'], '甲辰')
        self.assertEqual(second['chart']['day_master']['stem'], '乙')
        self.assertEqual(second['research']['strength']['variant'],
                         uc.PIN_STRENGTH_ENGINE_VARIANT)
        self.assertIsNone(
            second['research']['xiyong']['unified_verdict'])
        self.assertEqual(second['flow_year']['ganzhi'], '乙巳')
        self.assertNotIn({'block': 'forged', 'reason': 'forged'},
                         second['research']['errors'])

    def test_two_sequential_calls_do_not_cross_contaminate(self):
        first_a = uc.assemble_birth(F2_BIRTH)
        uc.assemble_birth(F2B_BIRTH)
        again_a = uc.assemble_birth(F2_BIRTH)
        self.assertEqual(first_a, again_a)
        self.assertEqual(again_a['chart']['ganzhi'], F2_GANZHI)
        b = uc.assemble_birth(F2B_BIRTH)
        self.assertEqual(b['chart']['ganzhi'], F2B_GANZHI)
        self.assertEqual(b['chart']['day_master']['stem'], '丙')

    def test_year_layer_errors_not_shared_with_core_cache(self):
        first = uc.assemble_birth(F2_BIRTH, traditional_role='male',
                                  target_year=2025)
        first['research']['errors'].append(
            {'block': 'forged', 'reason': 'forged'})
        second = uc.assemble_birth(F2_BIRTH, traditional_role='male',
                                   target_year=2025)
        self.assertNotIn({'block': 'forged', 'reason': 'forged'},
                         second['research']['errors'])
        # 无目标年的装配也不带年层 errors。
        plain = uc.assemble_birth(F2_BIRTH)
        self.assertNotIn({'block': 'forged', 'reason': 'forged'},
                         plain['research']['errors'])

    def test_pair_assemblies_are_independent(self):
        pair = uc.assemble_pair(F2_BIRTH, F2B_BIRTH)
        pair['person_a']['chart']['pillars'][0]['ganzhi'] = 'forged'
        self.assertEqual(
            pair['person_b']['chart']['pillars'][0]['ganzhi'], '乙巳')
        fresh = uc.assemble_pair(F2_BIRTH, F2B_BIRTH)
        self.assertEqual(
            fresh['person_a']['chart']['pillars'][0]['ganzhi'], '甲辰')
        self.assertEqual(
            fresh['person_b']['chart']['pillars'][0]['ganzhi'], '乙巳')

    def test_invalidate_forces_recompute(self):
        uc.assemble_birth(F2_BIRTH, traditional_role='male',
                          target_year=2025)
        self.assertEqual(len(self.natal_calls), 1)
        removed = invalidate_unified_compute_cache(
            F2_BIRTH, traditional_role='male', target_year=2025)
        self.assertGreaterEqual(removed, 2)  # 出生层 + 年层
        uc.assemble_birth(F2_BIRTH, traditional_role='male',
                          target_year=2025)
        self.assertEqual(len(self.natal_calls), 2)

    def test_dayun_served_with_role_and_year(self):
        assembly = uc.assemble_birth(
            F2_BIRTH, traditional_role='male', target_year=2025)
        self.assertEqual(assembly['dayun_status'], 'assembled')
        dayun = assembly['dayun']
        self.assertEqual(dayun['periods'], 8)
        self.assertEqual(dayun['traditional_role'], 'male')
        self.assertEqual(dayun['timeline']['variant'],
                         'dayun-classical-composition-v1')
        self.assertEqual(dayun['timeline']['status'], 'converted')
        rows = dayun['timeline']['sequence']['rows']
        self.assertEqual(len(rows), 8)
        self.assertEqual([row['period_index'] for row in rows],
                         list(range(1, 9)))
        for row in rows:
            self.assertTrue(row['candidate_ganzhi'])
            self.assertTrue(row['stem'])
            self.assertTrue(row['branch'])
        alignment = dayun['timeline']['sequence_time_alignment']
        self.assertEqual(len(alignment), 8)
        self.assertEqual(
            [entry['period_index'] for entry in alignment],
            list(range(1, 9)))
        for entry in alignment:
            self.assertIsNotNone(entry['start_interval'])
        # 组合仍用同一条 8 运序列装配，大运本身无错误记录。
        self.assertEqual(assembly['combination_status'], 'assembled')
        self.assertFalse(any(
            error['block'] == 'dayun'
            for error in assembly['research']['errors']))

    def test_dayun_served_with_role_but_no_target_year(self):
        # 八字页形态：无目标年，有口径即有 8 运；组合仍需目标年。
        assembly = uc.assemble_birth(F2_BIRTH, traditional_role='male')
        self.assertEqual(assembly['dayun_status'], 'assembled')
        self.assertEqual(
            len(assembly['dayun']['timeline']['sequence']['rows']), 8)
        self.assertIsNone(assembly['flow_year'])
        self.assertIsNone(assembly['flow_boundary'])
        self.assertIsNone(assembly['combination'])
        self.assertIn('target_year_not_given',
                      assembly['combination_note'])

    def test_dayun_absent_without_role_and_no_dayun_error(self):
        # 无口径是具名缺失，不是故障：不记 dayun 错误，不抛异常。
        assembly = uc.assemble_birth(F2_BIRTH, target_year=2025)
        self.assertIsNone(assembly['dayun'])
        self.assertEqual(assembly['dayun_status'], 'not_assembled')
        self.assertFalse(any(
            error['block'] == 'dayun'
            for error in assembly['research']['errors']))
        self.assertIsNotNone(assembly['flow_boundary'])

    def test_flow_boundary_served_with_target_year(self):
        assembly = uc.assemble_birth(F2_BIRTH, target_year=2025)
        boundary = assembly['flow_boundary']
        self.assertEqual(
            boundary['variant'], 'bazi-annual-lichun-boundary-v1')
        self.assertEqual(
            boundary['rows'][0]['ganzhi_in_interval'], '乙巳')
        plain = uc.assemble_birth(F2_BIRTH)
        self.assertIsNone(plain['flow_boundary'])

    def test_dayun_and_boundary_mutation_does_not_pollute_cache(self):
        first = uc.assemble_birth(
            F2_BIRTH, traditional_role='male', target_year=2025)
        first['dayun']['timeline']['sequence']['rows'][0][
            'candidate_ganzhi'] = 'forged'
        first['flow_boundary']['rows'][0][
            'ganzhi_in_interval'] = 'forged'
        second = uc.assemble_birth(
            F2_BIRTH, traditional_role='male', target_year=2025)
        self.assertEqual(
            second['dayun']['timeline']['sequence']['rows'][0][
                'candidate_ganzhi'], '丁卯')
        self.assertEqual(
            second['flow_boundary']['rows'][0]['ganzhi_in_interval'],
            '乙巳')

    def test_trims_carry_dayun_and_flow_boundary(self):
        assembly = uc.assemble_birth(
            F2_BIRTH, traditional_role='male', target_year=2025)
        bazi_trim = uc.trim_for_bazi_profile(assembly)
        self.assertEqual(
            len(bazi_trim['dayun']['timeline']['sequence']['rows']), 8)
        self.assertEqual(bazi_trim['dayun_status'], 'assembled')
        self.assertNotIn('flow_boundary', bazi_trim)
        self.assertNotIn('target_year', bazi_trim)
        for fn in (uc.trim_for_career, uc.trim_for_life):
            trim = fn(assembly)
            self.assertEqual(
                len(trim['dayun']['timeline']['sequence']['rows']), 8)
            self.assertEqual(trim['dayun_status'], 'assembled')
            self.assertEqual(
                trim['flow_boundary']['rows'][0]['ganzhi_in_interval'],
                '乙巳')
        romance_trim = uc.trim_for_romance(assembly)
        self.assertEqual(
            romance_trim['flow_boundary']['rows'][0][
                'ganzhi_in_interval'], '乙巳')
        self.assertNotIn('dayun', romance_trim)
        self.assertNotIn('dayun_status', romance_trim)
        pair_trim = uc.trim_for_compatibility(
            uc.assemble_pair(F2_BIRTH, F2B_BIRTH))
        self.assertNotIn('dayun', pair_trim)
        self.assertNotIn('flow_boundary', pair_trim)
        self.assertNotIn('dayun', pair_trim['person_a'])
        self.assertNotIn('flow_boundary', pair_trim['person_a'])

    def test_projection_excludes_dayun_and_flow_boundary(self):
        assembly = uc.assemble_birth(
            F2_BIRTH, traditional_role='male', target_year=2025)
        formal = project_formal(assembly)
        seen = set()
        _walk_keys(formal, seen)
        self.assertFalse(
            seen & {'dayun', 'dayun_status', 'flow_boundary'})
        self.assertTrue(
            {'dayun', 'dayun_status', 'flow_boundary'}
            <= set(uc.RESEARCH_FIELD_NAMES))


class DayunFailureTests(unittest.TestCase):
    """大运 / 边界失败只记入 errors，不拖垮装配。"""

    def setUp(self):
        clear_unified_compute_cache()
        self.natal_calls = []
        self.patchers = _stub_engine_patchers(self.natal_calls)
        for patcher in self.patchers:
            patcher.start()

    def tearDown(self):
        for patcher in reversed(self.patchers):
            patcher.stop()
        clear_unified_compute_cache()

    def _override(self, patcher):
        """后启动的同目标 patcher 覆盖先启动的（恢复按逆序）。"""
        patcher.start()
        self.patchers.append(patcher)

    def test_timeline_exception_is_soft(self):
        self._override(mock.patch(
            'tianji_kb.bazi_dayun_compose.classical_dayun_timeline',
            side_effect=RuntimeError('sealed runtime unavailable')))
        assembly = uc.assemble_birth(
            F2_BIRTH, traditional_role='male', target_year=2025)
        self.assertIsNone(assembly['dayun'])
        self.assertEqual(assembly['dayun_status'], 'not_assembled')
        self.assertTrue(any(
            error['block'] == 'dayun'
            for error in assembly['research']['errors']))
        # 组合因无大运序列而未装配，但装配本身不抛异常，流年仍在。
        self.assertIsNone(assembly['combination'])
        self.assertTrue(any(
            error['block'] == 'combination'
            for error in assembly['research']['errors']))
        self.assertEqual(assembly['flow_year']['ganzhi'], '乙巳')

    def test_timeline_unresolved_status_is_recorded(self):
        bad = copy.deepcopy(_fake_dayun_timeline())
        bad['status'] = 'unresolved'
        bad['reason'] = 'zero jie distance'
        self._override(mock.patch(
            'tianji_kb.bazi_dayun_compose.classical_dayun_timeline',
            return_value=bad))
        assembly = uc.assemble_birth(
            F2_BIRTH, traditional_role='male', target_year=2025)
        self.assertIsNone(assembly['dayun'])
        self.assertTrue(any(
            error['block'] == 'dayun'
            and 'dayun_timeline_unresolved' in error['reason']
            for error in assembly['research']['errors']))

    def test_boundary_exception_is_soft(self):
        self._override(mock.patch(
            'tianji_kb.bazi_annual_reference'
            '.annual_lichun_boundaries',
            side_effect=RuntimeError('sealed runtime unavailable')))
        assembly = uc.assemble_birth(
            F2_BIRTH, traditional_role='male', target_year=2025)
        self.assertIsNone(assembly['flow_boundary'])
        self.assertTrue(any(
            error['block'] == 'flow_boundary'
            for error in assembly['research']['errors']))
        self.assertIsNotNone(assembly['dayun'])
        self.assertIsNone(assembly['combination'])


class PinDriftTests(unittest.TestCase):
    def setUp(self):
        clear_unified_compute_cache()

    def tearDown(self):
        clear_unified_compute_cache()

    def test_validate_rejects_combination_drift(self):
        bad = dict(_research_block('bazi-combination-engine-v2'))
        with self.assertRaises(UnifiedComputePinError):
            validate_engine_pins(combination=bad)

    def test_validate_rejects_non_dict_block(self):
        with self.assertRaises(UnifiedComputePinError):
            validate_engine_pins(pattern='not-a-dict')

    def test_validate_rejects_combination_flag_drift(self):
        bad = dict(
            _research_block(uc.PIN_COMBINATION_ENGINE_VARIANT),
            ai_enabled=True)
        with self.assertRaises(UnifiedComputePinError):
            validate_engine_pins(combination=bad)

    def test_core_pin_drift_raises_and_does_not_pollute_cache(self):
        with mock.patch.object(
                uc, 'cached_execute',
                return_value={
                    'result': {
                        'pillars': _pillars_for(F2_GANZHI, '乙'),
                        'day_master': {'stem': '乙'},
                    }}), \
            mock.patch.object(
                uc, '_live_pilot',
                return_value=(None, 'month_not_piloted')), \
            mock.patch(
                'tianji_kb.bazi_strength_engine.assess_strength',
                return_value=_research_block(
                    uc.PIN_STRENGTH_ENGINE_VARIANT)), \
            mock.patch(
                'tianji_kb.bazi_pattern_engine.evaluate_all',
                return_value=_research_block(
                    'bazi-pattern-engine-v1')), \
            mock.patch(
                'tianji_kb.bazi_tiaohou.tiaohou_lookup',
                return_value={'variant': 'tiaohou-qiongtong-v1'}), \
            mock.patch(
                'tianji_kb.bazi_bingyao.bingyao_lookup',
                return_value={'variant': 'bingyao-shenfeng-v1'}), \
            mock.patch(
                'tianji_kb.bazi_xiyong_engine.evaluate_xiyong',
                return_value=dict(
                    _research_block(uc.PIN_XIYONG_ENGINE_VARIANT),
                    unified_verdict=None)):
            with self.assertRaises(UnifiedComputePinError):
                uc.assemble_birth(F2_BIRTH)
            self.assertEqual(len(uc._CORE_CACHE), 0)
            self.assertEqual(len(uc._YEAR_CACHE), 0)

    def test_combination_pin_drift_raises_and_year_cache_unpolluted(
            self):
        try:
            from tianji_kb.bazi_annual_reference import (
                annual_lichun_boundaries)  # noqa: F401
            from tianji_kb.bazi_combination_engine import combine  # noqa
            from tianji_kb.bazi_dayun_compose import (
                classical_dayun_timeline)  # noqa: F401
        except Exception as error:  # noqa: BLE001 - 密封依赖缺失即跳过
            raise unittest.SkipTest(
                'combination modules unavailable: %s' % error)
        with mock.patch.object(
                uc, 'cached_execute',
                return_value={
                    'result': {
                        'pillars': _pillars_for(F2_GANZHI, '乙'),
                        'day_master': {'stem': '乙'},
                    }}), \
            mock.patch.object(
                uc, '_live_pilot',
                return_value=(None, 'month_not_piloted')), \
            mock.patch(
                'tianji_kb.bazi_strength_engine.assess_strength',
                return_value=_research_block(
                    uc.PIN_STRENGTH_ENGINE_VARIANT)), \
            mock.patch(
                'tianji_kb.bazi_pattern_engine.evaluate_all',
                return_value=_research_block(
                    uc.PIN_PATTERN_ENGINE_VARIANT)), \
            mock.patch(
                'tianji_kb.bazi_tiaohou.tiaohou_lookup',
                return_value={'variant': 'tiaohou-qiongtong-v1'}), \
            mock.patch(
                'tianji_kb.bazi_bingyao.bingyao_lookup',
                return_value={'variant': 'bingyao-shenfeng-v1'}), \
            mock.patch(
                'tianji_kb.bazi_xiyong_engine.evaluate_xiyong',
                return_value=dict(
                    _research_block(uc.PIN_XIYONG_ENGINE_VARIANT),
                    unified_verdict=None, systems={})), \
            mock.patch('tianji_kb.bazi_core.ten_god',
                       return_value='比肩'), \
            mock.patch(
                'tianji_kb.bazi_dayun_compose.classical_dayun_timeline',
                return_value={'status': 'converted',
                              'sequence': {'rows': []}}), \
            mock.patch(
                'tianji_kb.bazi_annual_reference'
                '.annual_lichun_boundaries',
                return_value={'variant': uc.PIN_FLOW_BOUNDARY_VARIANT}), \
            mock.patch(
                'tianji_kb.bazi_combination_engine.combine',
                return_value=_research_block(
                    'bazi-combination-engine-v2')):
            with self.assertRaises(UnifiedComputePinError):
                uc.assemble_birth(F2_BIRTH, traditional_role='male',
                                  target_year=2025)
            year_key = uc._canonical_key(
                [F2_BIRTH, None, 'male', 2025])
            self.assertNotIn(year_key, uc._YEAR_CACHE)


class ProjectionTests(unittest.TestCase):
    def test_projection_has_exactly_allowlisted_keys(self):
        formal = project_formal(_synthetic_assembly())
        self.assertEqual(set(formal), set(uc.FORMAL_PROJECTION_TOP_KEYS))
        self.assertEqual(set(formal['chart']),
                         set(uc.FORMAL_PROJECTION_CHART_KEYS))
        self.assertEqual(set(formal['flow_year']),
                         set(uc.FORMAL_PROJECTION_FLOW_YEAR_KEYS))

    def test_projection_values_match_assembly(self):
        assembly = _synthetic_assembly()
        # 流年层内部口径说明（真实装配里有）不在 allowlist 内。
        assembly['flow_year']['calendar_provider'] = 'provider-stub'
        assembly['flow_year']['year_boundary'] = 'solar-term year'
        formal = project_formal(assembly)
        self.assertEqual(formal['birth_value'], F2_BIRTH)
        self.assertIsNone(formal['zone'])
        self.assertEqual(formal['target_year'], 2025)
        self.assertEqual(formal['chart']['ganzhi'], F2_GANZHI)
        self.assertEqual(formal['chart']['day_master']['stem'], '乙')
        self.assertEqual(formal['chart']['month_branch'], '寅')
        self.assertEqual(formal['flow_year']['ganzhi'], '乙巳')
        self.assertEqual(formal['flow_year']['year'], 2025)
        self.assertEqual(formal['flow_year']['stem_ten_god'], '比肩')
        # 流年层内部口径说明不在 allowlist 内。
        self.assertNotIn('calendar_provider', formal['flow_year'])
        self.assertNotIn('year_boundary', formal['flow_year'])

    def test_no_research_field_anywhere_in_projection(self):
        assembly = _synthetic_assembly()
        # 研究字段枚举来源：裁剪的研究块键 + 装配 research 字典键 +
        # 装配容器 + 公开 presentation 键（纵深防御）。
        forbidden = set(uc._research_trim(assembly))
        forbidden |= set(assembly['research'])
        forbidden |= {'research', 'natal_envelope'}
        forbidden |= set(PUBLIC_PRESENTATION_KEYS)
        formal = project_formal(assembly)
        seen = set()
        _walk_keys(formal, seen)
        self.assertFalse(seen & forbidden,
                         'formal projection carries research fields: %s'
                         % sorted(seen & forbidden))
        self.assertFalse(seen & set(uc.RESEARCH_FIELD_NAMES))
        # 逐字面值也不得出现：研究变体串 / 试点 / 统一裁决。
        dumped = json.dumps(formal, sort_keys=True, ensure_ascii=False)
        for token in (uc.PIN_STRENGTH_ENGINE_VARIANT,
                      uc.PIN_PATTERN_ENGINE_VARIANT,
                      uc.PIN_XIYONG_ENGINE_VARIANT,
                      uc.PIN_COMBINATION_ENGINE_VARIANT,
                      'yin_pilot', 'si_pilot', 'overall_effect',
                      'unified_verdict', 'tiaohou', 'bingyao'):
            self.assertNotIn(token, dumped)

    def test_research_field_names_covers_trim_and_research_keys(self):
        assembly = _synthetic_assembly()
        self.assertTrue(set(uc._research_trim(assembly))
                        <= set(uc.RESEARCH_FIELD_NAMES))
        self.assertTrue(set(assembly['research'])
                        <= set(uc.RESEARCH_FIELD_NAMES))

    def test_projection_is_deep_copy(self):
        assembly = _synthetic_assembly()
        formal = project_formal(assembly)
        formal['chart']['pillars'][0]['ganzhi'] = 'forged'
        formal['flow_year']['ganzhi'] = 'forged'
        self.assertEqual(assembly['chart']['pillars'][0]['ganzhi'],
                         '甲辰')
        self.assertEqual(assembly['flow_year']['ganzhi'], '乙巳')
        assembly['chart']['pillars'][0]['ganzhi'] = 'forged2'
        # 投影仍保持它自己此前的 'forged' 值：装配侧的修改未透传。
        self.assertEqual(formal['chart']['pillars'][0]['ganzhi'],
                         'forged')

    def test_projection_without_flow_year(self):
        assembly = _synthetic_assembly()
        assembly['target_year'] = None
        assembly['flow_year'] = None
        formal = project_formal(assembly)
        self.assertIsNone(formal['target_year'])
        self.assertIsNone(formal['flow_year'])
        self.assertEqual(formal['chart']['ganzhi'], F2_GANZHI)

    def test_projection_rejects_malformed_assemblies(self):
        for bad in (None, {}, {'chart': {}},
                    {'birth_value': F2_BIRTH, 'chart': {'pillars': []}},
                    {'birth_value': 'not-a-date',
                     'chart': _synthetic_assembly()['chart']},
                    {'birth_value': F2_BIRTH,
                     'chart': _synthetic_assembly()['chart'],
                     'flow_year': {'year': 2025}}):
            with self.assertRaises(UnifiedComputeInputError):
                project_formal(bad)

    def test_pair_projection(self):
        assembly = _synthetic_assembly()
        pair = project_formal_pair(
            {'person_a': assembly, 'person_b': assembly})
        self.assertEqual(set(pair), {'person_a', 'person_b'})
        for person in pair.values():
            self.assertEqual(set(person),
                             set(uc.FORMAL_PROJECTION_TOP_KEYS))
            seen = set()
            _walk_keys(person, seen)
            self.assertFalse(seen & set(uc.RESEARCH_FIELD_NAMES))
        with self.assertRaises(UnifiedComputeInputError):
            project_formal_pair({'person_a': assembly})
        with self.assertRaises(UnifiedComputeInputError):
            project_formal_pair(None)

    def test_projection_covers_all_five_trims_research_fields(self):
        # 五个裁剪的研究块键全集都必须被 RESEARCH_FIELD_NAMES 覆盖，
        # 否则新增研究字段可能漏进投影。
        assembly = _synthetic_assembly()
        trims = [uc.trim_for_bazi_profile(assembly),
                 uc.trim_for_career(assembly),
                 uc.trim_for_romance(assembly),
                 uc.trim_for_life(assembly)]
        pair = {'person_a': assembly, 'person_b': assembly}
        trims.append(uc.trim_for_compatibility(pair))
        for trim in trims:
            research = trim.get('research') or {}
            self.assertTrue(set(research) <= set(uc.RESEARCH_FIELD_NAMES),
                            'trim research keys not covered: %s'
                            % sorted(set(research)
                                     - set(uc.RESEARCH_FIELD_NAMES)))


class EquivalenceTests(unittest.TestCase):
    def test_pre_existing_trim_fields_byte_identical_new_keys_additive(
            self):
        """等价口径（Q3=A 后）：既有字段逐字段 byte-identical；
        新增顶层键只允许 ALLOWED_NEW_TRIM_KEYS 中的 additive 块；
        compatibility 未动（无新增键）。"""
        assembly = _synthetic_assembly()
        outs = {
            'bazi-profile': uc.trim_for_bazi_profile(assembly),
            'career': uc.trim_for_career(assembly),
            'romance': uc.trim_for_romance(assembly),
            'life': uc.trim_for_life(assembly),
            'compatibility': uc.trim_for_compatibility(
                {'person_a': assembly, 'person_b': assembly}),
        }
        for name, trim in outs.items():
            expected = PRE_CHANGE_FIELD_HASHES[name]
            self.assertTrue(
                set(expected) <= set(trim),
                '%s lost pre-existing fields: %s'
                % (name, sorted(set(expected) - set(trim))))
            new_keys = set(trim) - set(expected)
            self.assertTrue(
                new_keys <= ALLOWED_NEW_TRIM_KEYS[name],
                '%s gained unexpected keys: %s'
                % (name, sorted(new_keys)))
            for key, digest in expected.items():
                dumped = json.dumps(trim[key], sort_keys=True,
                                    ensure_ascii=False)
                self.assertEqual(
                    hashlib.sha256(dumped.encode()).hexdigest(), digest,
                    '%s field %r changed vs pre-change snapshot' % (name,
                                                                    key))
        # compatibility 两人用 _base_trim：无新增键，内容仍为旧形。
        pair = outs['compatibility']
        for person in (pair['person_a'], pair['person_b']):
            self.assertNotIn('dayun', person)
            self.assertNotIn('flow_boundary', person)

    def test_new_trim_blocks_carry_real_dayun_and_boundary_values(self):
        """新增块不是空壳：夹具里的 8 运序列与边界原样进裁剪。"""
        assembly = _synthetic_assembly()
        bazi_trim = uc.trim_for_bazi_profile(assembly)
        self.assertEqual(
            len(bazi_trim['dayun']['timeline']['sequence']['rows']), 8)
        self.assertEqual(
            bazi_trim['dayun']['timeline']['sequence']['rows'][0][
                'candidate_ganzhi'], '丁卯')
        self.assertEqual(bazi_trim['dayun_status'], 'assembled')
        life_trim = uc.trim_for_life(assembly)
        self.assertEqual(
            life_trim['flow_boundary']['rows'][0]['ganzhi_in_interval'],
            '乙巳')

    def test_annotation_and_promotion_tables_byte_identical(self):
        for name, fn in (
                ('page_annotations', uc.page_annotations),
                ('promotion_conditions', uc.promotion_conditions)):
            dumped = json.dumps(fn(), sort_keys=True, ensure_ascii=False)
            self.assertEqual(
                hashlib.sha256(dumped.encode()).hexdigest(),
                PRE_CHANGE_TABLE_HASHES[name],
                '%s changed vs pre-change snapshot' % name)

    def test_public_gate_variants_unchanged(self):
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

    def test_engine_pins_and_cache_limit_unchanged(self):
        self.assertEqual(uc.PIN_PATTERN_ENGINE_VARIANT,
                         'bazi-pattern-engine-v2')
        self.assertEqual(uc.PIN_STRENGTH_ENGINE_VARIANT,
                         'bazi-strength-engine-v1')
        self.assertEqual(uc.PIN_XIYONG_ENGINE_VARIANT,
                         'bazi-xiyong-engine-v1')
        self.assertEqual(uc.PIN_COMBINATION_ENGINE_VARIANT,
                         'bazi-combination-engine-v1')
        self.assertEqual(uc.UNIFIED_COMPUTE_VARIANT,
                         'unified-compute-entry-v1')
        self.assertEqual(uc._CACHE_MAX_ENTRIES, 8)
        self.assertIs(uc.RESEARCH_ONLY, True)
        self.assertIs(uc.PUBLIC_ENABLED, False)
        self.assertIs(uc.AI_ENABLED, False)


if __name__ == '__main__':
    unittest.main()
