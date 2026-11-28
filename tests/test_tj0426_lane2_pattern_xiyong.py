"""TJ-0426 Lane 2（八字格局 + 四体系）专项测试。

本 lane 的可编码增量（其余缺口因证据未备而只登记、不编码）：
- P-05：新登记 ``bazi_hehua_rules``（合化成立规则登记先行；恒
  unresolved，P-D1 待裁定）——转录核对、原始转写中立性、恒拒判。
- P-02：``BROKEN_GAPS`` 标注补齐（财多化官 ×2、伤尽标尺 ×1 得
  ``modern_flag_only``；伤官见官条目补现代旗标说明）——表级计数与
  现代旗标／标尺一致性；古典破格通道仍唯一（伤官见官）。
- X-03：病药已登记未编码两对的逐项处置（均 cannot_encode）——处置表
  与输出携带；已编码对子仍为 2 对。
- X-05：流年 pending 5 项逐项就绪度（前 4 项 derivation 恒 None，
  第 5 项统一裁决永不立）——就绪表与输出携带。
- P-06/X-04：格局用神 14 格逐格规则就绪度（``useful_god`` 恒 None）。
- X-01：现代扶抑 balanced 档推导 trace 完备性（4 步推导在场、方向恒空）。
- X-02：乙×丑快照缺失与戊土正二月缺字处理复核（只登记不入序列）。
- P-01/P-04/P-07：无 D-1 即无成立（密封）；杂气三 Variant 并列（密封）；
  比肩／劫财无 D-1 即不可判（密封）。

分工：纯常量／转录／契约测试本地可跑（只依赖标准库、
``bazi_xiyong_engine`` 与 ``bazi_hehua_rules``）；需历法 provider 与
密封 canonical 数据的测试（格局引擎、f2 全链）在密封装配环境运行，
公开检出整类跳过，不伪造通过。f2 全链与
``test_tj0424_broken_integration.F2EndToEndTests`` 有意重叠：该文件是
集成契约，本文件是本 lane 自有引擎（格局／喜用）的回归。
"""
import copy
import json
from pathlib import Path
import unittest

from tianji_kb.bazi_hehua_rules import (
    HEHUA_CONFLICTS,
    HEHUA_DETAIL_DIFFERENCES,
    HEHUA_ESTABLISHMENT_STATUS,
    HEHUA_FORMULATIONS,
    HEHUA_PAIRS,
    HEHUA_PENDING_ITEMS,
    HEHUA_PROPOSITIONS,
    HEHUA_RULES_VARIANT,
    ESTABLISHMENT_RULES,
    hehua_establishment,
    pair_presence,
    raw_transcription,
)
from tianji_kb.bazi_xiyong_engine import (
    ANNUAL_PENDING,
    ANNUAL_PENDING_DETAIL,
    ANNUAL_PENDING_READINESS,
    BINGYAO_REGISTERED_NOT_ENCODED_PAIRS,
    BINGYAO_UNENCODED_DISPOSITIONS,
    PATTERN_YONGSHEN_RULE_READINESS,
    evaluate_annual_xiyong,
    evaluate_bingyao_xiyong,
    evaluate_fuyi,
    evaluate_pattern_xiyong,
    evaluate_tiaohou_xiyong,
)

ROOT = Path(__file__).resolve().parents[1]
REN_YIN_GOLDEN = json.loads(
    (ROOT / 'tests/golden_tj012_ren_yin_true.json').read_text('utf-8'))

F2_BIRTH = '2024-02-11T16:27:07+08:00'
F2_PILLARS = ['甲辰', '丙寅', '乙巳', '甲申']
F2_DAY_MASTER = '乙'
F2_TARGET_YEAR = 2026


# --- 本地夹具（沿用 test_tj0424_xiyong_engine 的夹具形制）--------------
def _components(de_ling, de_di, de_shi, hidden, kexiehao):
    return {
        'de_ling': {'score': de_ling}, 'de_di': {'score': de_di},
        'de_shi': {'score': de_shi},
        'shengfu_hidden': {'score': hidden},
        'kexiehao': {'score': kexiehao}}


def _modern_fixture(verdict, score, components, limitations=()):
    return {
        'model_id': 'strength_model_modern_v1',
        'model_kind': 'modern_engineering',
        'research_only': True, 'public_enabled': False, 'ai_enabled': False,
        'verdict': verdict, 'score': score,
        'thresholds': {'strong_at_least': 60, 'weak_at_most': 15,
                       'balanced_between': [16, 59]},
        'components': components,
        'abstain_reason': None, 'abstain_detail': None,
        'limitations': list(limitations)}


def _strength_fixture(day_master, month_branch, classification, modern):
    return {
        'variant': 'bazi-strength-engine-v1',
        'day_master': day_master, 'month_branch': month_branch,
        'classical': {'classification': classification,
                      'matched_predicate': None,
                      'research_only': True, 'public_enabled': False,
                      'ai_enabled': False},
        'modern': modern,
        'agreement': {},
        'research_only': True, 'public_enabled': False, 'ai_enabled': False}


_BALANCED_STRENGTH = _strength_fixture(
    '戊', '午', 'indeterminate',
    _modern_fixture('balanced', 53, _components(20, 15, 20, 10, -12),
                    limitations=('土日主无已审重根集：得地分只计余根，未校准。',)))

_BALANCED_PILLARS = ['己亥', '庚午', '戊辰', '丁巳']

_PATTERN_NAMES = {
    'zhengguan': '正官', 'qisha': '七杀', 'zhengyin': '正印',
    'pianyin': '偏印', 'zhengcai': '正财', 'piancai': '偏财',
    'shishen': '食神', 'shangguan': '伤官', 'jianlu': '建禄',
    'yangren': '阳刃', 'zaqi': '杂气', 'special': '特殊格局'}


def _pattern_result(key, state, day_stem, month_branch, rule_ids=(),
                    evidence_ids=(), broken_gaps=()):
    return {
        'pattern': _PATTERN_NAMES[key], 'pattern_key': key, 'state': state,
        'evidence': [{'id': eid, 'detail': ''} for eid in evidence_ids],
        'limitations': [], 'rule_ids': list(rule_ids),
        'broken_gaps': list(broken_gaps),
        'research_only': True, 'public': False, 'ai': False,
        'variant': 'bazi-pattern-engine-v2',
        'day_stem': day_stem, 'month_branch': month_branch}


def _pattern_fixture(day_stem, month_branch, states):
    results = {}
    for key in _PATTERN_NAMES:
        state, rule_ids, evidence_ids = states.get(
            key, ('not_judgeable', (), ('no_basis',)))
        results[key] = _pattern_result(key, state, day_stem, month_branch,
                                       rule_ids, evidence_ids)
    return {
        'variant': 'bazi-pattern-engine-v2', 'day_stem': day_stem,
        'month_branch': month_branch, 'results': results,
        'pattern_variant': 'bazi-pattern-structure-candidates-v1',
        'ren_yin_determination_variant': 'ren-pattern-yin-true-v1',
        'luren_route_variant': 'bazi-pattern-luren-route-v1',
        'strength_overall': None,
        'research_only': True, 'public': False, 'ai': False}


def _hand_broken_pattern():
    """手构 broken 输入（伤官见官唯一已审通道；沿用 broken_integration 契约）。"""
    result = _pattern_result(
        'shangguan', 'broken', '乙', '寅',
        ('bazi.phase2.ren_yin_true_pattern',),
        ('ren_yin_true_pattern', 'shangguan_sees_officer_broken',
         'ren_yin_rule'),
        ('bg-food-shangguan-sees-officer',))
    result.update({
        'broken_condition': 'shangguan_sees_officer',
        'broken_evidence_ids': ['shangguan_sees_officer_broken'],
        'original_state': 'established',
        'original_pattern': '伤官',
    })
    fixture = _pattern_fixture('乙', '寅', {})
    fixture['results']['shangguan'] = result
    return fixture


def _live_modules():
    """真实引擎模块（仅密封装配环境可导入）；公开检出返回 None。"""
    try:
        from tianji_kb import bazi_bingyao as _by  # noqa: F401
        from tianji_kb import bazi_core as _bc  # noqa: F401
        from tianji_kb import bazi_tiaohou as _th  # noqa: F401
        from tianji_kb.bazi_dayun_sequence import (  # noqa: F401
            candidate_sequence as _cs)
        from tianji_kb.bazi_pattern import (  # noqa: F401
            PATTERN_VARIANT as _pv)
        from tianji_kb.bazi_pattern_engine import (  # noqa: F401
            BROKEN_GAPS as _bg,
            evaluate_all as _ea,
            evaluate_patterns_from_trace as _ept)
        from tianji_kb.bazi_siling_pilot import (  # noqa: F401
            yin_siling_pilot as _pilot)
        from tianji_kb.bazi_strength_engine import (  # noqa: F401
            assess_strength as _assess)
        from tianji_kb.bazi_xiyong_engine import (  # noqa: F401
            evaluate_xiyong as _ex)
        from tianji_kb.bazi_combination_engine import (  # noqa: F401
            combine as _combine)
        from tianji_kb.operations.bazi_chart import (  # noqa: F401
            chart as _chart_op)
    except Exception:
        return None
    return {'core': _bc, 'strength': _assess, 'tiaohou': _th,
            'bingyao': _by, 'dayun': _cs, 'pattern_variant': _pv,
            'broken_gaps': _bg, 'evaluate_all': _ea,
            'evaluate_from_trace': _ept, 'pilot': _pilot,
            'xiyong': _ex, 'combine': _combine, 'chart_op': _chart_op}


def _sealed_modules(test_case):
    """密封探针：模块缺失或 canonical 数据缺失即整类跳过。"""
    live = _live_modules()
    if live is None:
        raise unittest.SkipTest('live engine modules unavailable')
    try:
        probe = live['core'].chart_from_datetime(F2_BIRTH)
    except FileNotFoundError as error:
        raise unittest.SkipTest(
            'sealed canonical data unavailable: %s' % error)
    if [p['ganzhi'] for p in probe['pillars']] != F2_PILLARS:
        raise unittest.SkipTest('probe chart pillars drifted from Golden f2')
    return live


class HehuaRegistryTests(unittest.TestCase):
    """P-05：合化登记转录核对（本地可跑；审定登记为唯一底本）。"""

    def test_variant_and_governance(self):
        self.assertEqual(HEHUA_RULES_VARIANT, 'bazi-hehua-rules-v1')
        self.assertEqual(HEHUA_ESTABLISHMENT_STATUS, 'unresolved')
        self.assertEqual(ESTABLISHMENT_RULES, ())

    def test_pairs_match_adjudication_table(self):
        from tianji_kb import bazi_hehua_fact_adjudication as adj
        source = adj.PAIR_CONDITION_TABLE
        self.assertEqual(len(HEHUA_PAIRS), 5)
        self.assertEqual(len(source), 5)
        for mine, theirs in zip(HEHUA_PAIRS, source):
            self.assertEqual(mine['pair'], theirs['pair'])
            self.assertEqual(mine['element'], theirs['element'])
            self.assertEqual(tuple(mine['primary_months']),
                             tuple(theirs['primary_months']))
            self.assertEqual(tuple(mine['secondary_months']),
                             tuple(theirs['secondary_months']))
            self.assertEqual(mine['blocker_stem_f1'],
                             theirs['blocker_stem_f1'])
            self.assertEqual(mine['blocker_stem_f3_duhua'],
                             theirs['blocker_stem_f3_duhua'])
            self.assertEqual(mine['condition_quote'],
                             theirs['condition_quote'])
        # 名册化元素与审定批的执行表钉值一致。
        self.assertEqual(
            [[p['stems'][0], p['stems'][1], p['element']]
             for p in HEHUA_PAIRS],
            adj.SEALED_MEASUREMENTS['foundations_stem_combinations'])
        # 戊癸本局月集的未审记号原样保留，不补全。
        wugui = HEHUA_PAIRS[-1]
        self.assertEqual(wugui['pair'], '戊癸')
        self.assertEqual(wugui['primary_as_transmitted'], '丙午戌')
        self.assertEqual(wugui['primary_unresolved_token'], '丙')

    def test_formulations_match_adjudication_register(self):
        from tianji_kb import bazi_hehua_fact_adjudication as adj
        source = {f['id']: f for f in adj.FORMULATION_REGISTER}
        self.assertEqual({f['id'] for f in HEHUA_FORMULATIONS},
                         {'F1', 'F2', 'F3', 'F4', 'F5', 'F6', 'HX'})
        for mine in HEHUA_FORMULATIONS:
            theirs = source[mine['id']]
            self.assertEqual(mine['registered'], theirs['registered'])
            self.assertEqual(mine['status'], theirs['status'])
            self.assertEqual(mine['name'], theirs['name'])
        registered = {f['id'] for f in HEHUA_FORMULATIONS
                      if f['registered']}
        self.assertEqual(registered, {'F1', 'F2', 'F3', 'F4', 'HX'})
        # F5/F6 未登记：只有审计条目，不得据以设计判定。
        self.assertEqual(
            {f['id'] for f in HEHUA_FORMULATIONS
             if not f['registered']},
            {'F5', 'F6'})

    def test_conflicts_match_adjudication_analysis(self):
        from tianji_kb import bazi_hehua_fact_adjudication as adj
        source = {c['id']: c for c in adj.CONFLICT_ANALYSIS['true_conflicts']}
        mine = {c['id']: c for c in HEHUA_CONFLICTS}
        self.assertEqual(set(source), {'C1', 'C2', 'C3', 'C4', 'C5'})
        for conflict_id in ('C1', 'C2', 'C3', 'C4'):
            self.assertEqual(mine[conflict_id]['title'],
                             source[conflict_id]['title'])
            self.assertEqual(mine[conflict_id]['detail'],
                             source[conflict_id]['detail'])
            self.assertTrue(mine[conflict_id]['registered'])
        # C5 不计入四项真冲突：未登记的章内张力，只作结构登记。
        self.assertFalse(mine['C5']['registered'])
        self.assertEqual(
            {c['id'] for c in HEHUA_CONFLICTS if c['registered']},
            {'C1', 'C2', 'C3', 'C4'})
        self.assertEqual({d['id'] for d in HEHUA_DETAIL_DIFFERENCES},
                         {'D1', 'D2', 'D3', 'D4', 'D5'})

    def test_propositions_and_pending_match_adjudication(self):
        from tianji_kb import bazi_hehua_fact_adjudication as adj
        source_verdicts = {p['id']: p['verdict']
                           for p in adj.PROPOSITION_AUDIT}
        mine_verdicts = {p['id']: p['verdict']
                         for p in HEHUA_PROPOSITIONS}
        self.assertEqual(mine_verdicts, source_verdicts)
        self.assertEqual(
            {p['id'] for p in HEHUA_PROPOSITIONS},
            {'P%d' % n for n in range(1, 19)})
        # 化气成立（P16）须裁定；吉凶结论（P18）永禁。
        self.assertEqual(mine_verdicts['P16'], 'adjudication_required')
        self.assertEqual(mine_verdicts['P18'], 'prohibited')
        self.assertEqual(mine_verdicts['P14'], 'registered_absence')
        source_pending = {b['id']: b for b in adj.PENDING_ITEMS}
        mine_pending = {b['id']: b for b in HEHUA_PENDING_ITEMS}
        self.assertEqual(set(mine_pending), set(source_pending))
        for item_id, mine in mine_pending.items():
            self.assertEqual(mine['needs_user_adjudication'],
                             source_pending[item_id]['needs_user_adjudication'],
                             item_id)
        self.assertEqual(
            {b['id'] for b in HEHUA_PENDING_ITEMS
             if b['needs_user_adjudication']},
            {'B1', 'B5'})

    def test_pair_presence_is_name_list_fact_only(self):
        present = pair_presence(['甲', '己', '丙', '丁'])
        self.assertEqual(len(present), 1)
        self.assertEqual(present[0]['pair'], '甲己')
        self.assertEqual(present[0]['element'], '土')
        self.assertEqual(present[0]['pillars'], ['year', 'month'])
        # 四干至多两对；无合对时为空。
        self.assertEqual(pair_presence(['甲', '乙', '丙', '丁']), [])
        two = pair_presence(['甲', '己', '乙', '庚'])
        self.assertEqual({p['pair'] for p in two}, {'甲己', '乙庚'})
        with self.assertRaises(ValueError):
            pair_presence(['甲', '己', '丙'])
        with self.assertRaises(ValueError):
            pair_presence(['甲', '己', '丙', '子'])

    def test_raw_transcription_is_formulation_neutral(self):
        out = raw_transcription(['甲', '己', '乙', '庚'],
                                ['辰', '寅', '卯', '申'], '乙')
        self.assertEqual(out['variant'], HEHUA_RULES_VARIANT)
        self.assertEqual(out['transcription_kind'],
                         'formulation_neutral_raw')
        self.assertEqual(out['month_branch'], '寅')
        self.assertEqual(out['stem_counts'], {'甲': 1, '己': 1, '乙': 1, '庚': 1})
        self.assertTrue(out['chen_present'])
        self.assertEqual(out['chen_pillars'], ['year'])
        self.assertEqual({p['pair'] for p in out['pair_presence']},
                         {'甲己', '乙庚'})
        # 不含任何表述的月集／阻字集／状态归一化，不含旺气／根气：
        # 断言键集合（note 的否定性描述词不在此列）。
        forbidden_keys = {'month_set', 'blocker', 'multiplicity', 'wangqi',
                          'root_qi', 'establishment'}
        self.assertFalse(forbidden_keys & set(out.keys()))
        for pair in out['pair_presence']:
            self.assertFalse(forbidden_keys & set(pair.keys()))
        with self.assertRaises(ValueError):
            raw_transcription(['甲', '己', '乙', '庚'],
                              ['辰', '寅', '卯', '申'], '丁')

    def test_establishment_always_unresolved(self):
        # 无输入、甲己合在场、五合全无：恒 unresolved。
        for transcription in (
                None,
                raw_transcription(['甲', '己', '丙', '丁'],
                                  ['辰', '寅', '卯', '申'], '丙'),
                raw_transcription(['甲', '乙', '丙', '丁'],
                                  ['子', '寅', '卯', '申'], '丙')):
            out = hehua_establishment(transcription)
            self.assertEqual(out['establishment'], 'unresolved')
            self.assertEqual(out['transformation_status'], 'unresolved')
            self.assertEqual(out['pending_decision'], 'P-D1')
            self.assertEqual(out['formulations_in_conflict'],
                             ['F1', 'F2', 'F3', 'F4'])
        with self.assertRaises(ValueError):
            hehua_establishment({'variant': 'other-variant'})


class BrokenGapAnnotationTests(unittest.TestCase):
    """P-02：BROKEN_GAPS 表级计数与标注（本地可跑，纯表核对）。"""

    def test_gap_counts_and_status_breakdown(self):
        from tianji_kb.bazi_pattern_engine import BROKEN_GAPS
        expected_counts = {
            'zhengguan': 4, 'qisha': 3, 'zhengyin': 2, 'pianyin': 4,
            'zhengcai': 3, 'piancai': 3, 'shishen': 2, 'shangguan': 2,
            'jianlu': 1, 'yangren': 2, 'zaqi': 1, 'special': 1,
            'bijian': 1, 'jiecai': 1}
        self.assertEqual({k: len(v) for k, v in BROKEN_GAPS.items()},
                         expected_counts)
        total = sum(len(v) for v in BROKEN_GAPS.values())
        self.assertEqual(total, 30)
        ids = [g['id'] for gaps in BROKEN_GAPS.values() for g in gaps]
        # 同一 id 在不同格复用（如 bg-wealth-robbery）是按格登记，id 在
        # 同一格内唯一；全表 30 条逐条有缺失依据与缺失 Golden。
        for key, gaps in BROKEN_GAPS.items():
            self.assertEqual(len({g['id'] for g in gaps}), len(gaps), key)
            for gap in gaps:
                self.assertTrue(gap['missing_basis'], (key, gap['id']))
                self.assertTrue(gap['missing_golden'], (key, gap['id']))
                if 'status' in gap:
                    self.assertIn(gap['status'], (
                        'partially_resolved', 'modern_flag_only'),
                        (key, gap['id']))
        statuses = [g.get('status') for gaps in BROKEN_GAPS.values()
                    for g in gaps]
        self.assertEqual(statuses.count('partially_resolved'), 1)
        self.assertEqual(statuses.count('modern_flag_only'), 9)
        self.assertEqual(statuses.count(None), 20)

    def test_newly_annotated_gaps_name_their_modern_scale(self):
        from tianji_kb.bazi_pattern_engine import BROKEN_GAPS
        by_key = {key: {g['id']: g for g in gaps}
                  for key, gaps in BROKEN_GAPS.items()}
        # 财多化官（正财／偏财）：现代旗标 wealth_turns_officer_modern。
        for key in ('zhengcai', 'piancai'):
            gap = by_key[key]['bg-wealth-many-officer']
            self.assertEqual(gap['status'], 'modern_flag_only')
            self.assertIn('wealth_turns_officer_modern', gap['modern_flag'])
        # 伤尽标尺：现代标尺在 modern_assessment，不替古典标尺裁决。
        gap = by_key['shangguan']['bg-food-shangjin-scale']
        self.assertEqual(gap['status'], 'modern_flag_only')
        self.assertIn('exhausted_modern', gap['modern_flag'])
        self.assertIn('not_exhausted_modern', gap['modern_flag'])
        # 伤官见官：仍为唯一部分解决的古典通道；现代旗标说明为附加说明。
        gap = by_key['shangguan']['bg-food-shangguan-sees-officer']
        self.assertEqual(gap['status'], 'partially_resolved')
        self.assertIn('resolved_channel', gap)
        self.assertIn('shangguan_sees_officer_modern', gap['modern_flag'])
        # 刑冲破害事实层缺失的条目仍无状态、无旗标：不借现代旗标冒充古典 broken。
        gap = by_key['zhengguan']['bg-zhengguan-xingchong-fact-layer']
        self.assertNotIn('status', gap)
        self.assertNotIn('modern_flag', gap)


class BingyaoDispositionTests(unittest.TestCase):
    """X-03：已登记未编码两对的逐项处置（本地可跑）。"""

    def test_dispositions_cover_both_registered_pairs(self):
        self.assertEqual(
            [d['pair_id'] for d in BINGYAO_UNENCODED_DISPOSITIONS],
            [p['pair_id']
             for p in BINGYAO_REGISTERED_NOT_ENCODED_PAIRS])
        for disposition in BINGYAO_UNENCODED_DISPOSITIONS:
            self.assertEqual(disposition['disposition'], 'cannot_encode')
            self.assertTrue(disposition['blocker'])
            self.assertTrue(disposition['unlock'])
            self.assertEqual(disposition['reviewed_in'], 'TJ-0426-Lane2')
        by_id = {d['pair_id']: d
                 for d in BINGYAO_UNENCODED_DISPOSITIONS}
        self.assertIn('四柱纯土水', by_id['earth_heavy_unencoded']['detail'])
        self.assertIn('太弱太旺', by_id['officer_strength_tension']['detail'])

    def test_encoded_pairs_still_exactly_two(self):
        from tianji_kb import bazi_bingyao as bingyao_mod
        self.assertEqual(len(bingyao_mod.RULES), 2)
        self.assertEqual([r['pair_id'] for r in bingyao_mod.RULES],
                         ['wealth_peer_officer', 'foodwound_seal_wealth'])
        # 处置表不改已编码规则：两对语义不变。
        self.assertEqual(bingyao_mod.RULES[0]['quote'],
                         '如用财见比肩为病,喜见官杀为药也')

    def test_dispositions_carried_in_output(self):
        out = evaluate_bingyao_xiyong(None)
        self.assertEqual(out['registered_not_encoded_dispositions'],
                         [dict(d) for d in BINGYAO_UNENCODED_DISPOSITIONS])
        self.assertEqual(len(out['registered_not_encoded_pairs']), 2)


class AnnualReadinessTests(unittest.TestCase):
    """X-05：流年 pending 逐项就绪度（本地可跑）。"""

    def test_readiness_covers_all_pending_in_order(self):
        self.assertEqual(
            [r['item'] for r in ANNUAL_PENDING_READINESS],
            list(ANNUAL_PENDING))
        self.assertEqual(
            [r['item'] for r in ANNUAL_PENDING_DETAIL],
            list(ANNUAL_PENDING))
        for item in ANNUAL_PENDING_READINESS:
            self.assertIsNone(item['derivation'], item['item'])
            self.assertTrue(item['prerequisite'], item['item'])
        by_item = {r['item']: r for r in ANNUAL_PENDING_READINESS}
        self.assertEqual(by_item['unified_annual_verdict']
                         ['prerequisite_status'], 'never')
        self.assertIsNone(by_item['unified_annual_verdict']['unlock'])
        self.assertEqual(by_item['annual_tiaohou_derivation']
                         ['prerequisite_status'], 'missing')
        self.assertEqual(by_item['annual_bingyao_derivation']
                         ['prerequisite_status'],
                         'blocked_by_unadjudicated_effect')
        self.assertEqual(by_item['annual_pattern_yongshen_derivation']
                         ['prerequisite_status'], 'blocked_by_unreviewed_rules')

    def test_annual_output_carries_readiness_and_no_verdict(self):
        systems = {'fuyi': None, 'tiaohou': None, 'bingyao': None,
                   'pattern_yongshen': None}
        out = evaluate_annual_xiyong(systems, 2026, day_master='甲')
        self.assertEqual(out['pending_readiness'],
                         [dict(r) for r in ANNUAL_PENDING_READINESS])
        self.assertEqual(out['pending'], list(ANNUAL_PENDING))
        self.assertIsNone(out['derivation'])
        self.assertIsNone(out['unified_verdict'])
        self.assertEqual(out['status'], 'contract_only_pending_rules')


class PatternYongshenReadinessTests(unittest.TestCase):
    """P-06/X-04：格局用神 14 格逐格规则就绪度（本地可跑）。"""

    def test_readiness_covers_all_fourteen_patterns(self):
        keys = [r['pattern_key'] for r in PATTERN_YONGSHEN_RULE_READINESS]
        self.assertEqual(keys, ['zhengguan', 'qisha', 'zhengyin', 'pianyin',
                                'zhengcai', 'piancai', 'shishen', 'shangguan',
                                'jianlu', 'yangren', 'zaqi', 'special',
                                'bijian', 'jiecai'])
        for row in PATTERN_YONGSHEN_RULE_READINESS:
            self.assertEqual(row['rule_status'], 'pending_evidence_review')
            self.assertIsNone(row['useful_god'])
            self.assertTrue(row['evidence_needed'])

    def test_eligible_patterns_still_yield_no_yongshen(self):
        fixture = _pattern_fixture('甲', '申', {
            'pianyin': ('candidate',
                        ('bazi.phase2.resource_pattern_candidates',),
                        ('month_hidden_god',
                         'bazi.phase2.resource_pattern_candidates')),
        })
        out = evaluate_pattern_xiyong(fixture, day_master='甲')
        self.assertEqual(out['yongshen_rule_readiness'],
                         [dict(r)
                          for r in PATTERN_YONGSHEN_RULE_READINESS])
        self.assertEqual(len(out['eligible']), 1)
        self.assertIsNone(out['eligible'][0]['useful_god'])
        self.assertEqual(out['eligible'][0]['useful_god_status'],
                         'no_reviewed_yongshen_rule')
        # 未传入格局输出时就绪表同样携带。
        self.assertEqual(
            evaluate_pattern_xiyong(None)['yongshen_rule_readiness'],
            [dict(r) for r in PATTERN_YONGSHEN_RULE_READINESS])

    def test_broken_pattern_stays_ineligible_with_readiness(self):
        out = evaluate_pattern_xiyong(_hand_broken_pattern(),
                                      day_master='乙')
        self.assertEqual(out['eligible'], [])
        self.assertEqual(len(out['ineligible']), 12)
        record = {e['pattern_key']: e for e in out['ineligible']}['shangguan']
        self.assertEqual(record['state'], 'broken')
        self.assertEqual(record['broken_condition'], 'shangguan_sees_officer')
        self.assertNotIn('useful_god', record)
        self.assertEqual(len(out['yongshen_rule_readiness']), 14)


class FuyiBalancedDerivationTests(unittest.TestCase):
    """X-01：现代扶抑 balanced 档推导 trace 完备性（本地可跑）。"""

    def test_balanced_derivation_trace_present_no_direction(self):
        out = evaluate_fuyi(_BALANCED_STRENGTH, pillars=_BALANCED_PILLARS)
        modern = out['modern']
        self.assertEqual(modern['rule_id'], 'fuyi-modern-balanced')
        self.assertIsNone(modern['direction'])
        self.assertEqual(modern['status'], 'indeterminate_direction')
        self.assertEqual(
            [step['step'] for step in modern['direction_derivation']],
            ['input', 'rule_match', 'element_resolution',
             'candidate_stems'])
        self.assertEqual(
            modern['direction_derivation'][0]['thresholds'],
            {'strong_at_least': 60, 'weak_at_most': 15,
             'balanced_between': [16, 59]})
        self.assertEqual(
            modern['direction_derivation'][0]['score_range'], [-35, 105])
        # balanced 只是中间分数带：不给方向，但推导过程完整可复核。
        self.assertEqual(modern['input_verdict'], 'balanced')
        self.assertEqual(modern['input_score'], 53)
        self.assertEqual(
            modern['direction_derivation'][1]['ten_god_classes'], [])


class TiaohouMissingEntryTests(unittest.TestCase):
    """X-02：乙×丑缺失与戊土正二月缺字处理复核（本地可跑）。"""

    def test_yi_chou_absent_in_source(self):
        try:
            from tianji_kb.bazi_tiaohou import (
                ABSENT_IN_SOURCE, entry_for, tiaohou_lookup)
        except Exception as error:  # noqa: BLE001 - 历法依赖缺失即跳过
            raise unittest.SkipTest('tiaohou module unavailable: %s' % error)
        self.assertEqual(ABSENT_IN_SOURCE, {('乙', '丑')})
        self.assertIsNone(entry_for('乙', '丑'))
        out = tiaohou_lookup('乙', '丑',
                             ['甲', '乙', '丙', '丁'],
                             [[], [], [], []])
        self.assertEqual(out['status'], 'not_applicable')
        self.assertEqual(out['reason'], 'entry_absent_in_source')
        # 缺失组合只返回未审定：不借他月条目补齐。
        evaluated = evaluate_tiaohou_xiyong(out)
        self.assertEqual(evaluated['status'], 'not_judgeable')
        self.assertEqual(evaluated['gaps'][0]['gap_id'],
                         'entry_absent_in_source')

    def test_wu_first_two_months_encode_only_bing(self):
        try:
            from tianji_kb.bazi_tiaohou import entry_for
        except Exception as error:  # noqa: BLE001 - 历法依赖缺失即跳过
            raise unittest.SkipTest('tiaohou module unavailable: %s' % error)
        entry_yin = entry_for('戊', '寅')
        self.assertIsNotNone(entry_yin)
        # 快照第二位干名缺字：只编码丙，癸「又次之」只登记不入序列。
        self.assertEqual([item['stem'] for item in entry_yin['sequence']],
                         ['丙'])
        notes_yin = ' '.join(entry_yin['notes'])
        self.assertIn('缺字', notes_yin)
        self.assertIn('不据推测补字或定序', notes_yin)
        # 正二月合论：戊卯无分月条目，与戊寅共享节区与引文，序列同样只
        # 编码丙；缺字说明记在戊寅条目，不在戊卯重复登记。
        entry_mao = entry_for('戊', '卯')
        self.assertIsNotNone(entry_mao)
        self.assertEqual([item['stem'] for item in entry_mao['sequence']],
                         ['丙'])
        notes_mao = ' '.join(entry_mao['notes'])
        self.assertIn('与戊寅共享节区与引文', notes_mao)


class _SealedBase(unittest.TestCase):
    """密封测试基类：模块与 canonical 数据缺失时整类跳过。"""

    @classmethod
    def setUpClass(cls):
        cls.live = _sealed_modules(cls)
        cls.evaluate_all = staticmethod(cls.live['evaluate_all'])
        cls.chart = staticmethod(cls.live['core'].chart_from_pillars)

    def _chart(self, *pillars):
        return self.chart(*pillars)


class BrokenGapModernFlagConsistencyTests(_SealedBase):
    """P-02（密封）：每枚已发射的现代旗标／标尺必有缺口标注对应。

    探针盘沿用 test_tj0424_pattern_engine 的结构探针（非 Golden）；
    断言为全称性质：无论哪张盘发射何枚旗标，(pattern, flag_id) 必映射
    到 BROKEN_GAPS 中一条 modern_flag_only（伤官见官旗标映射到
    partially_resolved 条目）或伤尽标尺标注；反之，带 modern_flag_only
    标注的缺口其旗标 id 必为引擎可发射的旗标之一。
    """

    # (pattern_key, flag_id) -> gap_id；偏印夺食旗标注记在偏印格缺口上，
    # 但引擎只在食神格结果上发射该旗标（跨格注记，第三批原有形态）。
    FLAG_TO_GAP = {
        ('qisha', 'control_moderation_modern'):
            'bg-qisha-control-moderation',
        ('zhengyin', 'wealth_breaks_seal_modern'):
            'bg-resource-wealth-breaks-seal',
        ('pianyin', 'wealth_breaks_seal_modern'):
            'bg-resource-wealth-breaks-seal',
        ('shishen', 'seal_seizes_food_modern'):
            'bg-food-seized-by-seal',
        ('zhengcai', 'robbery_divides_wealth_modern'):
            'bg-wealth-robbery',
        ('piancai', 'robbery_divides_wealth_modern'):
            'bg-wealth-robbery',
        ('zhengcai', 'wealth_turns_officer_modern'):
            'bg-wealth-many-officer',
        ('piancai', 'wealth_turns_officer_modern'):
            'bg-wealth-many-officer',
        ('shangguan', 'shangguan_sees_officer_modern'):
            'bg-food-shangguan-sees-officer',
    }
    PROBE_CHARTS = (
        ('戊午', '辛酉', '甲午', '丙午'),
        ('戊子', '壬申', '丙午', '己丑'),
        ('戊午', '癸亥', '甲子', '乙丑'),
        ('丙寅', '辛酉', '甲午', '庚申'),
        ('甲寅', '丙午', '乙巳', '戊戌'),
        ('癸酉', '庚子', '丁酉', '庚子'),
        ('甲子', '戊辰', '乙丑', '丙子'),
        ('壬辰', '癸丑', '己未', '庚午'),
        ('己丑', '癸卯', '甲寅', '丙戌'),
        ('丙子', '癸酉', '庚戌', '丁丑'),
        ('丁卯', '癸亥', '丙子', '丁酉'),
        ('甲辰', '丙寅', '乙巳', '甲申'),
    )

    def test_every_emitted_modern_flag_has_gap_annotation(self):
        broken_gaps = self.live['broken_gaps']
        fired = set()
        for pillars in self.PROBE_CHARTS:
            out = self.evaluate_all(self._chart(*pillars))
            for key, result in out['results'].items():
                modern = result.get('modern_assessment')
                if not modern:
                    continue
                broken = modern.get('broken_assessment')
                if broken:
                    for flag in broken.get('flags') or []:
                        if flag['verdict'] == 'flagged_modern':
                            fired.add((key, flag['flag_id']))
                if key == 'shangguan' and modern.get('shangjin_scale'):
                    gap = {g['id']: g
                           for g in broken_gaps['shangguan']}
                    self.assertEqual(
                        gap['bg-food-shangjin-scale']['status'],
                        'modern_flag_only', pillars)
        self.assertTrue(fired, 'no modern flag fired on probe charts')
        for key, flag_id in sorted(fired):
            gap_id = self.FLAG_TO_GAP[(key, flag_id)]
            gap = {g['id']: g for g in broken_gaps[key]}[gap_id]
            self.assertIn(gap['status'],
                          ('modern_flag_only', 'partially_resolved'),
                          (key, flag_id, gap_id))
            self.assertIn(flag_id, gap.get('modern_flag', ''),
                          (key, flag_id, gap_id))

    def test_annotated_flags_are_emittable(self):
        # 已标注 modern_flag_only 的缺口，其 modern_flag 文本所点名的旗标
        # 必为 _modern_broken 可发射的旗标 id 之一（伤尽标尺另以等级名核对）。
        known_flags = {
            'control_moderation_modern', 'wealth_breaks_seal_modern',
            'seal_seizes_food_modern', 'robbery_divides_wealth_modern',
            'wealth_turns_officer_modern', 'shangguan_sees_officer_modern'}
        broken_gaps = self.live['broken_gaps']
        for key, gaps in broken_gaps.items():
            for gap in gaps:
                if gap.get('status') != 'modern_flag_only':
                    continue
                text = gap.get('modern_flag', '')
                named = {flag for flag in known_flags if flag in text}
                if key == 'shangguan' \
                        and gap['id'] == 'bg-food-shangjin-scale':
                    self.assertIn('exhausted_modern', text, gap['id'])
                    continue
                self.assertEqual(len(named), 1, gap['id'])
                self.assertIn((key, next(iter(named))),
                              self.FLAG_TO_GAP, gap['id'])


class NoEstablishmentWithoutD1Tests(_SealedBase):
    """P-01/P-07（密封）：无 D-1 输入时，14 格一律不得成立。"""

    PROBE_CHARTS = (
        ('戊午', '辛酉', '甲午', '丙午'),
        ('戊子', '壬申', '丙午', '己丑'),
        ('甲子', '戊辰', '乙丑', '丙子'),
        ('壬辰', '癸丑', '己未', '庚午'),
        ('丙寅', '辛酉', '甲午', '庚申'),
        ('丁卯', '癸亥', '丙子', '丁酉'),
        ('甲辰', '丙寅', '乙巳', '甲申'),
    )

    def test_no_established_without_ren_yin_block(self):
        for pillars in self.PROBE_CHARTS:
            out = self.evaluate_all(self._chart(*pillars))
            self.assertNotIn('established', out['counts'], pillars)
            for key, result in out['results'].items():
                self.assertIn(result['state'],
                              ('candidate', 'conflict', 'not_judgeable'),
                              (pillars, key))

    def test_bijian_jiecai_stay_not_judgeable_without_d1(self):
        for pillars in self.PROBE_CHARTS:
            out = self.evaluate_all(self._chart(*pillars))
            self.assertEqual(out['results']['bijian']['state'],
                             'not_judgeable', pillars)
            self.assertEqual(out['results']['jiecai']['state'],
                             'not_judgeable', pillars)

    def test_zaqi_three_variants_stay_parallel(self):
        out = self.evaluate_all(
            self._chart('甲子', '戊辰', '乙丑', '丙子'))
        self.assertEqual(out['results']['zaqi']['state'], 'conflict')
        ids = {e['id'] for e in out['results']['zaqi']['evidence']}
        self.assertIn('zaqi_variant_yuanzhu', ids)
        self.assertIn('zaqi_variant_sanming', ids)
        self.assertIn('zaqi_variant_ziping', ids)
        self.assertIn('zaqi_earth_conversion_unadjudicated', ids)


class F2ChainTests(_SealedBase):
    """f2 真实命盘全链复核（密封）：2024-02-11T16:27:07+08:00，
    四柱 甲辰/丙寅/乙巳/甲申。D-1 伤官格成立、伤官见官破格、格局用神
    分支拒判、组合层 established_patterns==[] / broken_patterns==['伤官']
    在本 lane 改动后不得翻转；本 lane 新增的就绪表随输出携带。
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        live = cls.live
        cls.assess = staticmethod(live['strength'])
        cls.evaluate_from_trace = staticmethod(live['evaluate_from_trace'])
        cls.pilot_fn = staticmethod(live['pilot'])
        cls.chart_op = staticmethod(live['chart_op'])
        cls.tiaohou_fn = staticmethod(live['tiaohou'].tiaohou_lookup)
        cls.bingyao_fn = staticmethod(live['bingyao'].bingyao_lookup)
        cls.dayun_fn = staticmethod(live['dayun'])
        cls.xiyong_fn = staticmethod(live['xiyong'])
        cls.combine = staticmethod(live['combine'])
        cls.pattern_variant = live['pattern_variant']
        chart = live['core'].chart_from_datetime(F2_BIRTH)
        if [p['ganzhi'] for p in chart['pillars']] != F2_PILLARS:
            raise unittest.SkipTest(
                'probe chart pillars drifted from Golden f2')

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
        chart = self.live['core'].chart_from_datetime(birth)
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
        combined = self.combine(pillars, day_master, dayun, target_year,
                                strength=strength, tiaohou=tiaohou,
                                bingyao=bingyao, pattern=pattern,
                                xiyong=xiyong)
        return {'chart': chart, 'ganzhi': ganzhi,
                'day_master': day_master, 'strength': strength,
                'pattern': pattern, 'tiaohou': tiaohou,
                'bingyao': bingyao, 'dayun': dayun, 'xiyong': xiyong,
                'combined': combined}

    def test_f2_chain_unchanged(self):
        chart = self.live['core'].chart_from_datetime(F2_BIRTH)
        self.assertEqual([p['ganzhi'] for p in chart['pillars']],
                         F2_PILLARS)
        self.assertEqual(chart['day_master']['stem'], F2_DAY_MASTER)
        built = self._build(F2_BIRTH, F2_TARGET_YEAR)
        pattern = built['pattern']
        self.assertEqual(pattern['counts'].get('broken'), 1)
        self.assertNotIn('established', pattern['counts'])
        result = pattern['results']['shangguan']
        self.assertEqual(result['state'], 'broken')
        self.assertEqual(result['broken_condition'], 'shangguan_sees_officer')
        self.assertEqual(result['original_state'], 'established')
        # 格局用神分支拒判：破格不进 eligible，全部 eligible 皆无用神。
        system = built['xiyong']['systems']['pattern_yongshen']
        self.assertNotIn('shangguan',
                         [e['pattern_key'] for e in system['eligible']])
        self.assertTrue(all(e.get('useful_god') is None
                            for e in system['eligible']))
        self.assertEqual(len(system['yongshen_rule_readiness']), 14)
        # 病药处置表与流年就绪表随真实盘输出携带。
        bingyao_system = built['xiyong']['systems']['bingyao']
        self.assertEqual(
            [d['pair_id'] for d in
             bingyao_system['registered_not_encoded_dispositions']],
            ['earth_heavy_unencoded', 'officer_strength_tension'])
        annual = built['xiyong']['annual_xiyong']
        self.assertEqual(len(annual['pending_readiness']), 5)
        self.assertIsNone(annual['unified_verdict'])
        self.assertIsNone(built['xiyong']['unified_verdict'])
        # 组合层：established 为空，broken 只有伤官。
        out = built['combined']
        self.assertEqual(out['pattern']['established'], [])
        self.assertEqual([b['pattern'] for b in out['pattern']['broken']],
                         ['伤官'])
        refs = out['xiyong']['annual_xiyong']['flow_references'][
            'pattern_yongshen']
        self.assertEqual(refs['established_patterns'], [])
        self.assertEqual(refs['broken_patterns'], ['伤官'])


if __name__ == '__main__':
    unittest.main()
