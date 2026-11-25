"""TJ-0424 第三批集成：格局 broken 状态打通喜用与组合。

只做这一处集成缺口：格局引擎 v2 的 broken（唯一古典通道：任氏
D-1 成立伤官格＋正官在场 → 伤官见官）能被喜用
``evaluate_xiyong`` 与组合 ``combine()`` 按契约消费。

契约（两路同口径，见各引擎 ``_validate_broken_pattern_result``）：
格键须为 ``shangguan``；rule_ids 须含
``bazi.phase2.ren_yin_true_pattern``；证据须含原成立身份
``ren_yin_true_pattern`` 与破格证据
``shangguan_sees_officer_broken``；additive 结构化字段须在场且与
证据一致（``broken_condition='shangguan_sees_officer'``、
``broken_evidence_ids`` 含破格证据 id、
``original_state='established'``、
``original_pattern`` 与本格 pattern 名一致）。任一项漂移即
fail-closed。broken 永不进入 established / eligible，格局用神分支
按条件拒判（ineligible，原因明写破格）。

两部分：``BrokenContractTests`` 只用手构 broken 输入（不依赖密封
数据与历法 provider，本地可跑）；``F2EndToEndTests`` 用真实 f2 命盘
（Golden f2-boundary-exact：出生 2024-02-11T16:27:07+08:00，
Asia/Shanghai；四柱 甲辰/丙寅/乙巳/甲申；D-1 成立伤官格，申/巳藏庚
正官）走真实 chart → evaluate_all（broken）→ evaluate_xiyong
（格局用神分支按条件拒判）→ combine（消费 broken 且不误读为
established）的全链路，复用 test_tj0424_pattern_engine 的 f2
harness 构造方式（chart_from_datetime 真实排盘＋ren_yin pilot 结果
传入 chart() trace 路径）与 test_tj0424_combination_engine
LiveEngineInputsTests 的 _build 取法（assess_strength /
tiaohou_lookup / bingyao_lookup / candidate_sequence forward 前 3 运；
大运期位为输入夹具，不冒充出生数据）。无密封模块时整类跳过，
不伪造通过。
"""
import copy
import json
from pathlib import Path
import unittest

from tianji_kb.bazi_combination_engine import combine
from tianji_kb.bazi_xiyong_engine import evaluate_pattern_xiyong

ROOT = Path(__file__).resolve().parents[1]
REN_YIN_GOLDEN = json.loads(
    (ROOT / 'tests/golden_tj012_ren_yin_true.json').read_text('utf-8'))

F2_BIRTH = '2024-02-11T16:27:07+08:00'
F1_BIRTH = '2024-02-11T16:27:06+08:00'
F2_PILLARS = ['甲辰', '丙寅', '乙巳', '甲申']
F2_DAY_MASTER = '乙'
F2_MONTH_BRANCH = '寅'
F2_TARGET_YEAR = 2026


def _hand_result(key, pattern, state, evidence_ids, rule_ids):
    return {
        'pattern': pattern, 'pattern_key': key, 'state': state,
        'evidence': [{'id': eid, 'detail': 'detail-%s' % eid}
                     for eid in evidence_ids],
        'limitations': ['破格缺口（其余）：伤尽程度标尺仍未裁定。'],
        'rule_ids': list(rule_ids),
        'broken_gaps': ['bg-shangguan-sees-officer'],
        'research_only': True, 'public': False, 'ai': False,
        'variant': 'bazi-pattern-engine-v2',
        'day_stem': F2_DAY_MASTER, 'month_branch': F2_MONTH_BRANCH}


def _hand_broken_statement():
    """按契约手构的 broken 输入（伤官格，唯一已审通道）。"""
    broken = _hand_result(
        'shangguan', '伤官', 'broken',
        ['ren_yin_true_pattern', 'shangguan_sees_officer_broken',
         'ren_yin_rule'],
        ['bazi.phase2.ren_yin_true_pattern'])
    broken.update({
        'broken_condition': 'shangguan_sees_officer',
        'broken_evidence_ids': ['shangguan_sees_officer_broken'],
        'original_state': 'established',
        'original_pattern': '伤官',
    })
    return {
        'variant': 'bazi-pattern-engine-v2',
        'day_stem': F2_DAY_MASTER, 'month_branch': F2_MONTH_BRANCH,
        'research_only': True, 'public': False, 'ai': False,
        'pattern_variant': 'bazi-pattern-structure-candidates-v1',
        'ren_yin_determination_variant': 'ren-pattern-yin-true-v1',
        'luren_route_variant': 'bazi-pattern-luren-route-v1',
        'strength_overall': None,
        'counts': {'broken': 1, 'not_judgeable': 1},
        'results': {
            'shangguan': broken,
            'zhengcai': _hand_result(
                'zhengcai', '正财', 'not_judgeable', ['no_basis'], []),
        },
    }


def _hand_dayun():
    return [{'candidate_ganzhi': '丙辰', 'period_index': 1,
             'ten_god': '伤官'}]


class BrokenContractTests(unittest.TestCase):
    def test_hand_broken_accepted_by_xiyong_as_ineligible(self):
        out = evaluate_pattern_xiyong(
            _hand_broken_statement(), pillars=F2_PILLARS,
            day_master=F2_DAY_MASTER)
        self.assertEqual(out['counts_by_state'],
                         {'broken': 1, 'not_judgeable': 1})
        self.assertEqual(out['counts'],
                         {'eligible': 0, 'ineligible': 2, 'total': 2})
        # 破格绝不进入 eligible 格局用神。
        self.assertEqual(
            [e['pattern_key'] for e in out['eligible']], [])
        self.assertNotIn('shangguan',
                         [e['pattern_key'] for e in out['eligible']])
        ineligible = {e['pattern_key']: e for e in out['ineligible']}
        record = ineligible['shangguan']
        self.assertEqual(record['state'], 'broken')
        # 破格依据与原成立身份随记录携带，不得丢弃。
        self.assertEqual(record['broken_condition'],
                         'shangguan_sees_officer')
        self.assertEqual(record['broken_evidence_ids'],
                         ['shangguan_sees_officer_broken'])
        self.assertEqual(record['original_state'], 'established')
        self.assertEqual(record['original_pattern'], '伤官')
        self.assertIn('ren_yin_true_pattern', record['evidence_ids'])
        self.assertIn('shangguan_sees_officer_broken',
                      record['evidence_ids'])
        # 拒判原因明写破格，不得用笼统的“无已审依据”。
        self.assertIn('已破格', record['reason'])
        self.assertIn('成立前提不再满足', record['reason'])
        self.assertNotIn('无已审依据', record['reason'])

    def test_hand_broken_never_established_in_combine(self):
        out = combine(F2_PILLARS, F2_DAY_MASTER, _hand_dayun(),
                      F2_TARGET_YEAR,
                      pattern=_hand_broken_statement())
        pattern_block = out['pattern']
        self.assertEqual(pattern_block['counts'],
                         {'broken': 1, 'not_judgeable': 1})
        self.assertNotIn('established', pattern_block['counts'])
        self.assertEqual(pattern_block['established'], [])
        self.assertEqual(len(pattern_block['broken']), 1)
        record = pattern_block['broken'][0]
        self.assertEqual(record['pattern_key'], 'shangguan')
        self.assertEqual(record['pattern'], '伤官')
        self.assertEqual(record['state'], 'broken')
        self.assertEqual(record['broken_condition'],
                         'shangguan_sees_officer')
        self.assertEqual(record['broken_evidence_ids'],
                         ['shangguan_sees_officer_broken'])
        self.assertEqual(record['original_state'], 'established')
        self.assertEqual(record['original_pattern'], '伤官')
        self.assertIn('ren_yin_true_pattern', record['evidence_ids'])
        self.assertIn('shangguan_sees_officer_broken',
                      record['evidence_ids'])
        # 组合的格局用神体系同样单列 broken，不输出用神。
        system = out['xiyong']['systems']['pattern_yongshen']
        self.assertEqual(system['established'], [])
        self.assertEqual(len(system['broken']), 1)
        sys_record = system['broken'][0]
        self.assertEqual(sys_record['pattern'], '伤官')
        self.assertEqual(sys_record['broken_condition'],
                         'shangguan_sees_officer')
        self.assertEqual(sys_record['original_state'], 'established')
        self.assertEqual(sys_record['original_pattern'], '伤官')
        self.assertIsNone(sys_record['useful_god'])
        self.assertIn('已破格', sys_record['reason'])
        self.assertNotIn('伤官', system['established'])
        refs = out['xiyong']['annual_xiyong']['flow_references'][
            'pattern_yongshen']
        self.assertEqual(refs['established_patterns'], [])
        self.assertEqual(refs['broken_patterns'], ['伤官'])
        # 结构关系不受 broken 输入影响（除 pattern block 外）。
        plain = combine(F2_PILLARS, F2_DAY_MASTER, _hand_dayun(),
                        F2_TARGET_YEAR)
        self.assertEqual(out['structural_relations'],
                         plain['structural_relations'])
        self.assertEqual(out['relation_summary'],
                         plain['relation_summary'])

    def test_hand_broken_tampered_refused_by_both(self):
        mutations = {
            # 通道外：七杀格破格无已审通道。
            'wrong-channel': lambda s: (
                s['results'].__setitem__(
                    'qisha', s['results'].pop('shangguan')),
                s['results']['qisha'].__setitem__('pattern', '七杀'),
                s['results']['qisha'].__setitem__('pattern_key', 'qisha'),
                s['results']['qisha'].__setitem__(
                    'original_pattern', '七杀')),
            # 缺破格证据。
            'missing-breaking-evidence': lambda s: (
                s['results']['shangguan'].__setitem__(
                    'evidence',
                    [e for e in s['results']['shangguan']['evidence']
                     if e['id'] != 'shangguan_sees_officer_broken'])),
            # 缺原成立身份证据。
            'missing-establishment-evidence': lambda s: (
                s['results']['shangguan'].__setitem__(
                    'evidence',
                    [e for e in s['results']['shangguan']['evidence']
                     if e['id'] != 'ren_yin_true_pattern'])),
            # 缺 additive 结构化字段。
            'missing-additive-field': lambda s: (
                s['results']['shangguan'].pop('broken_condition')),
            # 原身份不是 established。
            'original-not-established': lambda s: (
                s['results']['shangguan'].__setitem__(
                    'original_state', 'candidate')),
            # 原身份与本格名不一致。
            'original-pattern-mismatch': lambda s: (
                s['results']['shangguan'].__setitem__(
                    'original_pattern', '正官')),
            # 缺 Ren D-1 规则。
            'rule-missing': lambda s: (
                s['results']['shangguan'].__setitem__('rule_ids', [])),
        }
        for name, mutate in mutations.items():
            bad = _hand_broken_statement()
            mutate(bad)
            with self.assertRaises(ValueError, msg=name):
                evaluate_pattern_xiyong(
                    copy.deepcopy(bad), pillars=F2_PILLARS,
                    day_master=F2_DAY_MASTER)
            with self.assertRaises(ValueError, msg=name):
                combine(F2_PILLARS, F2_DAY_MASTER, _hand_dayun(),
                        F2_TARGET_YEAR, pattern=copy.deepcopy(bad))


class F2EndToEndTests(unittest.TestCase):
    """真实 f2 命盘全链路：只在密封模块可导入时运行，否则跳过。"""

    @classmethod
    def setUpClass(cls):
        try:
            from tianji_kb import bazi_bingyao as _by  # noqa: F401
            from tianji_kb import bazi_core as _bc  # noqa: F401
            from tianji_kb import bazi_tiaohou as _th  # noqa: F401
            from tianji_kb.bazi_dayun_sequence import (  # noqa: F401
                candidate_sequence as _cs)
            from tianji_kb.bazi_pattern import (  # noqa: F401
                PATTERN_VARIANT as _pv)
            from tianji_kb.bazi_pattern_engine import (  # noqa: F401
                evaluate_patterns_from_trace as _ept)
            from tianji_kb.bazi_siling_pilot import (  # noqa: F401
                yin_siling_pilot as _pilot)
            from tianji_kb.bazi_strength_engine import (  # noqa: F401
                assess_strength as _assess)
            from tianji_kb.bazi_xiyong_engine import (  # noqa: F401
                evaluate_xiyong as _ex)
            from tianji_kb.operations.bazi_chart import (  # noqa: F401
                chart as _chart_op)
        except Exception as error:  # noqa: BLE001 - 密封依赖缺失即跳过
            raise unittest.SkipTest(
                'live engine modules unavailable: %s' % error)
        cls.core = _bc
        # 数据可用性探针：公开检出无密封数据时，排盘即缺文件——
        # 整类跳过（不伪造通过）；机上有数据时探针通过，照常执行。
        try:
            _probe = _bc.chart_from_datetime(F2_BIRTH)
        except FileNotFoundError as error:
            raise unittest.SkipTest(
                'sealed canonical data unavailable: %s' % error)
        if [p['ganzhi'] for p in _probe['pillars']] != F2_PILLARS:
            raise unittest.SkipTest(
                'probe chart pillars drifted from Golden f2')
        cls.assess = staticmethod(_assess)
        cls.evaluate_from_trace = staticmethod(_ept)
        cls.pattern_variant = _pv
        cls.pilot_fn = staticmethod(_pilot)
        cls.chart_op = staticmethod(_chart_op)
        cls.tiaohou_fn = staticmethod(_th.tiaohou_lookup)
        cls.bingyao_fn = staticmethod(_by.bingyao_lookup)
        cls.dayun_fn = staticmethod(_cs)
        cls.xiyong_fn = staticmethod(_ex)

    def _pilot_for(self, birth_value):
        window = REN_YIN_GOLDEN['jie_windows'][birth_value[:4]]
        return self.pilot_fn(
            birth_value, version_id='ditiansui-yuanshuo',
            jie_facts={'provider': dict(REN_YIN_GOLDEN['provider']),
                       'lichun': dict(window['lichun']),
                       'next_jie': dict(window['next_jie'])})

    def _trace_engine(self, pillars, birth_value):
        pilot = self._pilot_for(birth_value)
        out = self.chart_op(
            *pillars, pattern_variant=self.pattern_variant,
            ren_yin_pilot_result=pilot)
        return self.evaluate_from_trace(
            {'trace': out['trace'], 'evidence': out['evidence']},
            pilot_result=pilot)

    def _build(self, birth, target_year):
        chart = self.core.chart_from_datetime(birth)
        pillars = chart['pillars']
        day_master = chart['day_master']['stem']
        ganzhi = [p['ganzhi'] for p in pillars]
        strength = self.assess(pillars, day_master)
        pattern = self._trace_engine(tuple(ganzhi), birth)
        visible = [p['stem']['value'] for p in pillars]
        hidden = [[h['stem'] for h in p['branch']['hidden_stems']]
                 for p in pillars]
        tiaohou = self.tiaohou_fn(
            day_master, pillars[1]['branch']['value'], visible, hidden)
        visible_gods = [
            {'pillar': name, 'stem': pillars[i]['stem']['value'],
             'ten_god': pillars[i]['stem']['ten_god']}
            for i, name in ((0, 'year'), (1, 'month'), (3, 'hour'))]
        bingyao = self.bingyao_fn(day_master, visible_gods)
        sequence = self.dayun_fn(
            pillars[1]['ganzhi'], day_master, direction='forward',
            periods=3)
        dayun = [{'candidate_ganzhi': r['candidate_ganzhi'],
                  'period_index': r['period_index'],
                  'ten_god': r['ten_god_relative_to_natal_day_stem']}
                 for r in sequence['rows']]
        xiyong = self.xiyong_fn(
            day_master=day_master,
            month_branch=pillars[1]['branch']['value'],
            pillars=ganzhi, strength=strength, tiaohou=tiaohou,
            bingyao=bingyao, pattern=pattern, flow_year=target_year)
        combined = combine(pillars, day_master, dayun, target_year,
                           strength=strength, tiaohou=tiaohou,
                           bingyao=bingyao, pattern=pattern,
                           xiyong=xiyong)
        return {'chart': chart, 'ganzhi': ganzhi,
                'day_master': day_master, 'strength': strength,
                'pattern': pattern, 'tiaohou': tiaohou,
                'bingyao': bingyao, 'dayun': dayun, 'xiyong': xiyong,
                'combined': combined}

    def _xiyong_without_pattern(self, built, target_year):
        return self.xiyong_fn(
            day_master=built['day_master'],
            month_branch=built['chart']['pillars'][1]['branch']['value'],
            pillars=built['ganzhi'], strength=built['strength'],
            tiaohou=built['tiaohou'], bingyao=built['bingyao'],
            pattern=None, flow_year=target_year)

    def test_f2_end_to_end_broken_chain(self):
        # 真实出生排盘：四柱须与 Golden f2-boundary-exact 一致。
        chart = self.core.chart_from_datetime(F2_BIRTH)
        ganzhi = [p['ganzhi'] for p in chart['pillars']]
        self.assertEqual(ganzhi, F2_PILLARS)
        self.assertEqual(chart['day_master']['stem'], F2_DAY_MASTER)
        built = self._build(F2_BIRTH, F2_TARGET_YEAR)
        pattern = built['pattern']
        # 格局：伤官格 broken（非 established），破格依据与原身份在场。
        self.assertEqual(pattern['counts'].get('broken'), 1)
        self.assertNotIn('established', pattern['counts'])
        result = pattern['results']['shangguan']
        self.assertEqual(result['state'], 'broken')
        self.assertEqual(result['pattern'], '伤官')
        self.assertEqual(
            result['rule_ids'], ['bazi.phase2.ren_yin_true_pattern'])
        ids = {e['id'] for e in result['evidence']}
        self.assertIn('ren_yin_true_pattern', ids)
        self.assertIn('shangguan_sees_officer_broken', ids)
        self.assertEqual(result['broken_condition'],
                         'shangguan_sees_officer')
        self.assertEqual(result['broken_evidence_ids'],
                         ['shangguan_sees_officer_broken'])
        self.assertEqual(result['original_state'], 'established')
        self.assertEqual(result['original_pattern'], '伤官')
        # 喜用：格局用神分支按条件拒判，破格不进 eligible。
        system = built['xiyong']['systems']['pattern_yongshen']
        self.assertEqual(system['counts_by_state'].get('broken'), 1)
        self.assertNotIn('shangguan',
                         [e['pattern_key'] for e in system['eligible']])
        self.assertTrue(all(e['state'] != 'broken'
                            for e in system['eligible']))
        ineligible = {e['pattern_key']: e for e in system['ineligible']}
        record = ineligible['shangguan']
        self.assertEqual(record['state'], 'broken')
        self.assertEqual(record['broken_condition'],
                         'shangguan_sees_officer')
        self.assertEqual(record['broken_evidence_ids'],
                         ['shangguan_sees_officer_broken'])
        self.assertEqual(record['original_state'], 'established')
        self.assertEqual(record['original_pattern'], '伤官')
        self.assertIn('已破格', record['reason'])
        self.assertIn('成立前提不再满足', record['reason'])
        # 组合：消费 broken 且不误读为 established。
        out = built['combined']
        pattern_block = out['pattern']
        self.assertEqual(pattern_block['counts'].get('broken'), 1)
        self.assertNotIn('established', pattern_block['counts'])
        self.assertEqual(pattern_block['established'], [])
        self.assertEqual(len(pattern_block['broken']), 1)
        self.assertEqual(pattern_block['broken'][0]['pattern'], '伤官')
        self.assertEqual(
            pattern_block['broken'][0]['broken_condition'],
            'shangguan_sees_officer')
        self.assertEqual(
            pattern_block['broken'][0]['original_pattern'], '伤官')
        # 传入 xiyong 时组合直通喜用输出：格局用神体系与喜用侧一致。
        combined_system = out['xiyong']['systems']['pattern_yongshen']
        self.assertEqual(combined_system, system)
        # 不传 xiyong 时走本地旧契约：格局用神体系单列 broken，
        # 流年对照亦单列 broken_patterns。
        local = combine(built['chart']['pillars'], built['day_master'],
                        built['dayun'], F2_TARGET_YEAR,
                        strength=built['strength'],
                        tiaohou=built['tiaohou'],
                        bingyao=built['bingyao'], pattern=pattern)
        local_system = local['xiyong']['systems']['pattern_yongshen']
        self.assertEqual(local_system['established'], [])
        self.assertEqual(len(local_system['broken']), 1)
        self.assertEqual(local_system['broken'][0]['pattern'], '伤官')
        self.assertIsNone(local_system['broken'][0]['useful_god'])
        refs = local['xiyong']['annual_xiyong']['flow_references'][
            'pattern_yongshen']
        self.assertEqual(refs['established_patterns'], [])
        self.assertEqual(refs['broken_patterns'], ['伤官'])
        # 效力层：无已成立格神结论（broken 不产生格神同十神结论）。
        verdicts = [v for entry in out['effects']['conditional_effects']
                    for v in entry['verdicts']]
        self.assertNotIn('stem_matches_established_pattern_god', verdicts)

    def test_f2_independent_systems_unchanged(self):
        built = self._build(F2_BIRTH, F2_TARGET_YEAR)
        xiyong_f2 = built['xiyong']
        xiyong_none = self._xiyong_without_pattern(
            built, F2_TARGET_YEAR)
        # 同一盘去掉 pattern 输入：扶抑 / 调候 / 病药三体系结构一致。
        for key in ('fuyi', 'tiaohou', 'bingyao'):
            self.assertEqual(xiyong_f2['systems'][key],
                             xiyong_none['systems'][key], key)
        # 对照盘 f1（同柱、早 1 秒）：三体系亦一致，唯格局体系不同。
        built_f1 = self._build(F1_BIRTH, F2_TARGET_YEAR)
        self.assertEqual(built_f1['ganzhi'], F2_PILLARS)
        self.assertNotIn('broken', built_f1['pattern']['counts'])
        self.assertEqual(
            built_f1['pattern']['results']['zhengcai']['state'],
            'candidate')
        for key in ('fuyi', 'tiaohou', 'bingyao'):
            self.assertEqual(xiyong_f2['systems'][key],
                             built_f1['xiyong']['systems'][key], key)
        system_f1 = built_f1['xiyong']['systems']['pattern_yongshen']
        self.assertNotIn('broken', system_f1['counts_by_state'])
        ineligible_f1 = {e['pattern_key']: e
                         for e in system_f1['ineligible']}
        self.assertNotIn('已破格', ineligible_f1['shangguan']['reason'])

    def test_f2_combine_relations_unchanged(self):
        built = self._build(F2_BIRTH, F2_TARGET_YEAR)
        xiyong_none = self._xiyong_without_pattern(
            built, F2_TARGET_YEAR)
        combined_none = combine(
            built['chart']['pillars'], built['day_master'],
            built['dayun'], F2_TARGET_YEAR, strength=built['strength'],
            tiaohou=built['tiaohou'], bingyao=built['bingyao'],
            pattern=None, xiyong=xiyong_none)
        out = built['combined']
        # 结构关系（数量 / 内容）不受 broken 输入影响。
        self.assertEqual(out['structural_relations'],
                         combined_none['structural_relations'])
        self.assertEqual(out['relation_summary'],
                         combined_none['relation_summary'])
        # 对照盘 f1（同柱同运同流年）：结构关系亦一致。
        built_f1 = self._build(F1_BIRTH, F2_TARGET_YEAR)
        self.assertEqual(built_f1['dayun'], built['dayun'])
        self.assertEqual(out['structural_relations'],
                         built_f1['combined']['structural_relations'])


if __name__ == '__main__':
    unittest.main()
