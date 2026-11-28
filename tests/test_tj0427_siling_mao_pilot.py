"""TJ-031.19 (E0427) Lane F: 卯月分日司令试点 Variant + 巳月 C1 标记升级
+ 六爻 career 映射未批准钉位 + 紫微大限/流年候选扩展 + 动爻结构事实钉位.

卯月 Golden expectations below were derived BY HAND from the proposal
(``~/workspace/tj-batch4-audit/siling-mao-pilot-proposal.md`` §5) and the
registered T1 segments (甲 7 日、乙 23 日): real elapsed seconds from
the provider-verified 惊蛰 instant t0, left-closed right-open segments
[t0, t0+7d) 甲 / [t0+7d, t0+30d) 乙, with the 乙 segment's effective
domain ending at 春分 (the ~15-day 惊蛰→春分 window, NOT the 30-day
registration). t0 provenance: pinned provider lunar-python==1.4.8 annual
jieqi table (2024 惊蛰 2024-03-05 10:22:45 / 春分 2024-03-20 11:06:25;
2025 惊蛰 2025-03-05 16:07:18 / 春分 2025-03-20 17:01:29; 2026 惊蛰
2026-03-05 21:59:00 / 春分 2026-03-20 22:45:59, Asia/Shanghai). No
expected value in the Golden was produced by running the implementation.

Covered here (public CI, no sealed assets): the 8 proposal Golden cases
(G1–G8: 甲段 2、乙段 2、交界 2、窗口外 2) plus at-t0, 春分-1s, a
past-春分 birth inside the registered 乙段 (never 乙), cross-year
2026, and cross-timezone same-instant consistency; fail-closed cases
(±1s boundaries, precision, provider mismatch, version gate,
registration tampering, no extrapolation); the 巳月 C1 approved marking
(user 2026-11-27 ②, option A); the liuyao career mapping NOT-approved
pins (registry stays empty, assess() abstains); the ziwei candidate
extensions (decade_for_age, annual_palaces_for_decade, period_disputes);
and the moving-line structure facts (efficacy stays abstain).
"""

from __future__ import annotations

import copy
import unittest
from datetime import datetime, timezone

from tianji_kb import bazi_siling_matrix as matrix
from tianji_kb import bazi_siling_mao_pilot as mao_pilot
from tianji_kb import bazi_siling_si_pilot as si_pilot
from tianji_kb.bazi_siling_mao_pilot import mao_siling_pilot
from tianji_kb.bazi_siling_si_pilot import si_siling_pilot
from tianji_kb.liuyao_moving_yao import (
    assess_moving_effect, changed_line_facts, dark_moving_structure,
    line_motion, moving_lines,
)
from tianji_kb.liuyao_yongshen import (
    USEFUL_GOD_MAPPINGS, assess, list_mapping_slots, mapping_slot,
)
from tianji_kb.operations.ziwei_periods import (
    RULE_STATUS, annual_palace, annual_palaces_for_decade, decade_for_age,
    decade_periods, period_disputes,
)

PROVIDER = {'name': 'lunar-python', 'version': '1.4.8',
            'identity_verified': True}

WINDOWS = {
    '2024': {'jingzhe': {'term': '惊蛰', 'at': '2024-03-05T10:22:45+08:00',
                         'precision': 'second'},
             'next_jie': {'term': '春分', 'at': '2024-03-20T11:06:25+08:00',
                          'precision': 'second'}},
    '2025': {'jingzhe': {'term': '惊蛰', 'at': '2025-03-05T16:07:18+08:00',
                         'precision': 'second'},
             'next_jie': {'term': '春分', 'at': '2025-03-20T17:01:29+08:00',
                          'precision': 'second'}},
    '2026': {'jingzhe': {'term': '惊蛰', 'at': '2026-03-05T21:59:00+08:00',
                         'precision': 'second'},
             'next_jie': {'term': '春分', 'at': '2026-03-20T22:45:59+08:00',
                          'precision': 'second'}},
    '1988': {'jingzhe': {'term': '惊蛰', 'at': '1988-03-05T16:46:32+08:00',
                         'precision': 'second'},
             'next_jie': {'term': '春分', 'at': '1988-03-20T17:38:35+08:00',
                          'precision': 'second'}},
}

# Hand-derived Golden: id, birth, window, expected status/reason/commander,
# expected elapsed seconds (None when not computed).
CASES = [
    # Proposal G1–G8.
    {'id': 'g01_jia_2024', 'birth': '2024-03-08T12:00:00+08:00',
     'window': '2024', 'expected_status': 'computed', 'expected_reason': None,
     'expected_commander': '甲', 'elapsed': 265035},
    {'id': 'g02_jia_2025', 'birth': '2025-03-08T09:30:00+08:00',
     'window': '2025', 'expected_status': 'computed', 'expected_reason': None,
     'expected_commander': '甲', 'elapsed': 235362},
    {'id': 'g03_yi_2024', 'birth': '2024-03-15T12:00:00+08:00',
     'window': '2024', 'expected_status': 'computed', 'expected_reason': None,
     'expected_commander': '乙', 'elapsed': 869835},
    {'id': 'g04_yi_2025', 'birth': '2025-03-15T12:00:00+08:00',
     'window': '2025', 'expected_status': 'computed', 'expected_reason': None,
     'expected_commander': '乙', 'elapsed': 849162},
    {'id': 'g05_boundary_yi', 'birth': '2024-03-12T10:22:45+08:00',
     'window': '2024', 'expected_status': 'computed', 'expected_reason': None,
     'expected_commander': '乙', 'elapsed': 604800},
    {'id': 'g06_boundary_minus_1s', 'birth': '2024-03-12T10:22:44+08:00',
     'window': '2024', 'expected_status': 'computed', 'expected_reason': None,
     'expected_commander': '甲', 'elapsed': 604799},
    {'id': 'g07_before_jingzhe', 'birth': '2024-03-05T10:22:44+08:00',
     'window': '2024', 'expected_status': 'not_applicable',
     'expected_reason': 'before_jingzhe', 'expected_commander': None,
     'elapsed': None},
    {'id': 'g08_at_chunfen', 'birth': '2024-03-20T11:06:25+08:00',
     'window': '2024', 'expected_status': 'not_applicable',
     'expected_reason': 'at_or_after_next_jie', 'expected_commander': None,
     'elapsed': None},
    # Extras: at t0, one second before 春分, past 春分 inside the
    # registered 乙段 (must NOT be 乙), cross-year 2026.
    {'id': 'g09_at_jingzhe', 'birth': '2024-03-05T10:22:45+08:00',
     'window': '2024', 'expected_status': 'computed', 'expected_reason': None,
     'expected_commander': '甲', 'elapsed': 0},
    {'id': 'g10_chunfen_minus_1s', 'birth': '2024-03-20T11:06:24+08:00',
     'window': '2024', 'expected_status': 'computed', 'expected_reason': None,
     'expected_commander': '乙', 'elapsed': 1298619},
    {'id': 'g11_past_chunfen_in_registered_yi',
     'birth': '2024-03-25T12:00:00+08:00',
     'window': '2024', 'expected_status': 'not_applicable',
     'expected_reason': 'at_or_after_next_jie', 'expected_commander': None,
     'elapsed': None},
    {'id': 'g12_jia_2026', 'birth': '2026-03-10T12:00:00+08:00',
     'window': '2026', 'expected_status': 'computed', 'expected_reason': None,
     'expected_commander': '甲', 'elapsed': 396060},
    {'id': 'g13_yi_2026', 'birth': '2026-03-18T12:00:00+08:00',
     'window': '2026', 'expected_status': 'computed', 'expected_reason': None,
     'expected_commander': '乙', 'elapsed': 1087260},
    # Cross-timezone: the G1 instant written in four zones (Honolulu
    # and New York local dates are already Mar 7 — same instant, same 甲).
    {'id': 'g14_g1_utc', 'birth': '2024-03-08T04:00:00+00:00',
     'window': '2024', 'expected_status': 'computed', 'expected_reason': None,
     'expected_commander': '甲', 'elapsed': 265035},
    {'id': 'g15_g1_tokyo', 'birth': '2024-03-08T13:00:00+09:00',
     'window': '2024', 'expected_status': 'computed', 'expected_reason': None,
     'expected_commander': '甲', 'elapsed': 265035},
    {'id': 'g16_g1_honolulu', 'birth': '2024-03-07T18:00:00-10:00',
     'window': '2024', 'expected_status': 'computed', 'expected_reason': None,
     'expected_commander': '甲', 'elapsed': 265035},
    {'id': 'g17_g1_new_york', 'birth': '2024-03-07T23:00:00-05:00',
     'window': '2024', 'expected_status': 'computed', 'expected_reason': None,
     'expected_commander': '甲', 'elapsed': 265035},
    # 1988: the same instant written with +08:00 and +09:00 offsets.
    {'id': 'g18_1988_plus08', 'birth': '1988-03-10T12:00:00+08:00',
     'window': '1988', 'expected_status': 'computed', 'expected_reason': None,
     'expected_commander': '甲', 'elapsed': 414808},
    {'id': 'g19_1988_plus09', 'birth': '1988-03-10T13:00:00+09:00',
     'window': '1988', 'expected_status': 'computed', 'expected_reason': None,
     'expected_commander': '甲', 'elapsed': 414808},
]

FORBIDDEN_KEYS = {
    'score', 'scores', 'rating', 'weight', 'weights', 'useful_god',
    'favorable', 'favourable', 'recommended', 'recommendation',
    'verdict', 'combined_verdict', 'final_verdict', 'resolution',
    'resolved_choice', 'preference', 'true_false', 'success_failure',
    'pattern_name',
    '喜用神', '用神', '喜神', '忌神', '吉凶', '评分', '推荐', '权重', '裁决',
    '真格', '假格', '成格', '破格',
}

C1_APPROVED_STATUS = '以任氏命例为准，戊段下限十日，与 T1 七日冲突不调和'


def _all_keys(node):
    if isinstance(node, dict):
        for key, value in node.items():
            yield key
            yield from _all_keys(value)
    elif isinstance(node, list):
        for item in node:
            yield from _all_keys(item)


def _jie_facts(case, override=None):
    window = WINDOWS[case['window']]
    facts = {
        'provider': dict(PROVIDER),
        'jingzhe': dict(window['jingzhe']),
        'next_jie': dict(window['next_jie']),
    }
    override = override or {}
    if override.get('drop_next_jie'):
        facts.pop('next_jie')
    if 'jingzhe_at' in override:
        facts['jingzhe']['at'] = override['jingzhe_at']
    if 'jingzhe_precision' in override:
        facts['jingzhe']['precision'] = override['jingzhe_precision']
    if 'provider_version' in override:
        facts['provider']['version'] = override['provider_version']
    if 'provider_identity_verified' in override:
        facts['provider']['identity_verified'] = \
            override['provider_identity_verified']
    if 'precision_warning' in override:
        facts['precision_warning'] = override['precision_warning']
    if 'source_ref' in override:
        facts['source_ref'] = override['source_ref']
    return facts


def _run(case, override=None):
    return mao_siling_pilot(
        case['birth'], version_id='sanming-t1',
        jie_facts=_jie_facts(case, override),
        birth_time_precision='second')


class MaoGoldenTest(unittest.TestCase):
    def test_all_golden_cases(self) -> None:
        self.assertEqual(len(CASES), 19)
        for case in CASES:
            with self.subTest(case=case['id']):
                out = _run(case)
                self.assertEqual(out['status'], case['expected_status'])
                self.assertEqual(out['reason'], case['expected_reason'])
                self.assertEqual(out['commander'],
                                 case['expected_commander'])
                self.assertIsNone(out['determination'])
                self.assertTrue(out['research_only'])
                self.assertFalse(out['public_enabled'])
                self.assertFalse(out['ai_enabled'])
                self.assertEqual(out['evidence_binding'],
                                 'pending_phase1_rule_registration')
                self.assertEqual(out['variant'],
                                 'bazi-siling-mao-pilot-v1')
                if case['expected_status'] == 'computed':
                    self.assertEqual(out['elapsed_seconds'], case['elapsed'])
                    self.assertEqual(out['month_branch'], '卯')
                else:
                    self.assertNotIn('segment', out)
                    self.assertIsNone(out['month_branch'])

    def test_computed_segment_boundaries_match_hand_derivation(self) -> None:
        case = next(c for c in CASES if c['id'] == 'g09_at_jingzhe')
        out = _run(case)
        self.assertEqual(out['segment']['index'], 1)
        self.assertEqual(out['segment']['start']['utc'],
                         '2024-03-05T02:22:45+00:00')
        self.assertEqual(out['segment']['end']['utc'],
                         '2024-03-12T02:22:45+00:00')
        self.assertEqual(out['segment']['start']['asia_shanghai'],
                         '2024-03-05T10:22:45+08:00')
        self.assertEqual(out['segment']['registered_day_span'], [1, 7])
        self.assertEqual(out['segment']['registered_basis'], '甲木用事七日')
        self.assertFalse(out['segment']['effective_end_capped_at_next_jie'])
        self.assertEqual(out['elapsed_seconds'], 0)
        self.assertAlmostEqual(out['window']['window_days'], 15.03, places=2)

    def test_yi_segment_effective_end_is_capped_at_chunfen(self) -> None:
        # The 乙 segment's REGISTERED end is t0+30d (2024-04-04), but
        # its EFFECTIVE end is 春分 (2024-03-20): the two must never be
        # conflated, and no birth past 春分 may be called 乙 (g11).
        case = next(c for c in CASES if c['id'] == 'g10_chunfen_minus_1s')
        out = _run(case)
        self.assertEqual(out['commander'], '乙')
        self.assertEqual(out['segment']['index'], 2)
        self.assertEqual(out['segment']['end']['utc'],
                         '2024-04-04T02:22:45+00:00')
        self.assertEqual(out['segment']['effective_end']['utc'],
                         '2024-03-20T03:06:25+00:00')
        self.assertTrue(out['segment']['effective_end_capped_at_next_jie'])
        self.assertIn('春分', out['segment']['effective_end_reason'])
        self.assertEqual(out['segment']['registered_day_span'], [8, 30])
        self.assertEqual(out['segment']['registered_basis'], '乙木二十三日')
        past = next(c for c in CASES
                    if c['id'] == 'g11_past_chunfen_in_registered_yi')
        out = _run(past)
        self.assertEqual(out['status'], 'not_applicable')
        self.assertIsNone(out['commander'])

    def test_cross_timezone_cases_are_the_same_instant(self) -> None:
        instants = {
            next(c for c in CASES if c['id'] == cid)['birth']
            for cid in ('g01_jia_2024', 'g14_g1_utc', 'g15_g1_tokyo',
                        'g16_g1_honolulu', 'g17_g1_new_york')}
        utc_values = {datetime.fromisoformat(b).astimezone(timezone.utc)
                      for b in instants}
        self.assertEqual(len(utc_values), 1)
        for cid in ('g14_g1_utc', 'g15_g1_tokyo', 'g16_g1_honolulu',
                    'g17_g1_new_york'):
            case = next(c for c in CASES if c['id'] == cid)
            self.assertEqual(_run(case)['commander'], '甲')

    def test_naive_date_reading_would_misclassify_the_boundary(self) -> None:
        # Fail-before pin: a naive local-date subtraction (Mar 12 - Mar 5
        # = 7 days -> "day 8") would land the t0+7d-1s birth in segment 2,
        # while real elapsed time (< 7 days) is segment 1. The pilot
        # must follow elapsed time, never the naive reading.
        case = next(c for c in CASES if c['id'] == 'g06_boundary_minus_1s')
        birth_local = datetime.fromisoformat(case['birth'])
        t0_local = datetime.fromisoformat(
            WINDOWS[case['window']]['jingzhe']['at'])
        naive_day_index = (birth_local.date() - t0_local.date()).days + 1
        self.assertEqual(naive_day_index, 8)  # naive reading: segment 2
        out = _run(case)
        self.assertEqual(out['commander'], '甲')  # elapsed reading: seg 1
        self.assertEqual(out['segment']['index'], 1)
        self.assertLess(out['elapsed_seconds'], 7 * 86400)


class MaoRegistrationConsumptionTest(unittest.TestCase):
    def test_segment_bounds_derived_from_registered_matrix_cell(self) -> None:
        derived, failure = mao_pilot._derive_registration()
        self.assertIsNone(failure)
        self.assertEqual(
            derived['bounds'],
            [('甲', 0, 7 * 86400), ('乙', 7 * 86400, 30 * 86400)])
        self.assertEqual(derived['day_spans'], [[1, 7], [8, 30]])
        self.assertEqual(derived['convention']['id'],
                         'siling-mao-calculation-convention')
        self.assertEqual(derived['convention']['version'], 'v1')
        self.assertEqual(derived['quote']['id'], 'sm.t1_table')
        self.assertIsNone(derived['quote']['layer'])
        self.assertEqual(derived['excerpt'],
                         '二月建卯卯中有甲木用事七日乙木二十三日')
        self.assertEqual(derived['excerpt_locator'],
                         {'char_start': 48008, 'char_end': 48027})

    def test_provenance_disclaimer_is_convention_verbatim(self) -> None:
        case = next(c for c in CASES if c['id'] == 'g09_at_jingzhe')
        out = _run(case)
        prov = out['provenance']
        self.assertEqual(
            prov['disclaimer'],
            mao_pilot.SILING_MAO_CALCULATION_CONVENTION['disclaimer'])
        self.assertIn('连续24小时计日', prov['disclaimer'])
        self.assertIn('不是已证实的传统文献唯一解释', prov['disclaimer'])
        self.assertIsNone(prov['text_layer'])
        self.assertEqual(prov['source_id'], 'bazi.source.sanmingtonghui')
        self.assertIsNone(prov['source_section_id'])
        self.assertEqual(prov['quote'],
                         '二月建卯卯中有甲木用事七日乙木二十三日')
        self.assertEqual(prov['quote_locator'],
                         {'char_start': 48008, 'char_end': 48027})
        self.assertEqual(prov['calculation_convention'],
                         {'id': 'siling-mao-calculation-convention',
                          'version': 'v1'})
        self.assertEqual(out['provider_verification']['provider'],
                         'lunar-python')
        self.assertTrue(out['provider_verification']['replay_verified'])
        # E0427: the convention is registered in the matrix and the
        # cell flipped to pilot_authorized_sanming_t1; the pilot
        # records what it observed.
        self.assertEqual(prov['matrix_adjudication_status'],
                         'pilot_authorized_sanming_t1')

    def test_conflict_markers_name_the_four_parallel_calibers(self) -> None:
        case = next(c for c in CASES if c['id'] == 'g09_at_jingzhe')
        out = _run(case)
        conflicts = {m['id']: m for m in out['conflicts']}
        self.assertEqual(set(conflicts), {'T2', '渊海', '神峰', '滴天髓'})
        t2 = conflicts['T2']
        self.assertEqual(t2['version_id'], 'sanming-t2')
        self.assertEqual(t2['status'], 'conflict')
        self.assertEqual([(s['stem'], s['days']) for s in t2['segments']],
                         [('乙', 18), ('甲', 9), ('癸', 3)])
        self.assertEqual(conflicts['渊海']['cell_status'], 'no_day_counts')
        self.assertEqual(conflicts['神峰']['cell_status'],
                         'diagram_unrecoverable')
        self.assertEqual(conflicts['滴天髓']['cell_status'], 'no_table')
        # Markers also ride on non-computed outputs.
        before = next(c for c in CASES if c['id'] == 'g07_before_jingzhe')
        self.assertEqual([m['id'] for m in _run(before)['conflicts']],
                         ['T2', '渊海', '神峰', '滴天髓'])

    def test_tampered_registration_fails_closed(self) -> None:
        case = next(c for c in CASES if c['id'] == 'g09_at_jingzhe')
        cell = matrix.SILING_MATRIX['sanming-t1']['卯']
        original = cell['segments'][0]['days']
        try:
            cell['segments'][0]['days'] = 8
            out = _run(case)
        finally:
            cell['segments'][0]['days'] = original
        self.assertEqual(out['status'], 'rejected')
        self.assertEqual(out['reason'], 'registration_integrity_failure')
        self.assertIsNone(out['commander'])

    def test_tampered_adjudication_status_fails_closed(self) -> None:
        case = next(c for c in CASES if c['id'] == 'g09_at_jingzhe')
        cell = matrix.SILING_MATRIX['sanming-t1']['卯']
        original = cell['adjudication_status']
        try:
            cell['adjudication_status'] = 'bogus_status'
            out = _run(case)
        finally:
            cell['adjudication_status'] = original
        self.assertEqual(out['status'], 'rejected')
        self.assertEqual(out['reason'], 'registration_integrity_failure')

    def test_registered_status_computes_and_conflict_now_fails_closed(self) -> None:
        # E0427: registration is complete (cell is
        # pilot_authorized_sanming_t1) and the status check is
        # tightened to that single value, mirroring the 巳 pilot:
        # the registered state computes with the same segments, and
        # a cell flipped back to 'conflict' now fails closed instead
        # of computing.
        case = next(c for c in CASES if c['id'] == 'g09_at_jingzhe')
        out = _run(case)
        self.assertEqual(out['status'], 'computed')
        self.assertEqual(out['commander'], '甲')
        self.assertEqual(out['provenance']['matrix_adjudication_status'],
                         'pilot_authorized_sanming_t1')
        cell = matrix.SILING_MATRIX['sanming-t1']['卯']
        original = cell['adjudication_status']
        try:
            cell['adjudication_status'] = 'conflict'
            out = _run(case)
        finally:
            cell['adjudication_status'] = original
        self.assertEqual(out['status'], 'rejected')
        self.assertEqual(out['reason'], 'registration_integrity_failure')
        self.assertIsNone(out['commander'])


class MaoFailClosedTest(unittest.TestCase):
    def _facts(self):
        case = next(c for c in CASES if c['id'] == 'g09_at_jingzhe')
        return case, _jie_facts(case)

    def test_non_pilot_versions_rejected(self) -> None:
        case, facts = self._facts()
        for version_id in ('sanming-t2', 'ditiansui-yuanshuo',
                           'yuanhai-zongjue', 'shenfeng-diagram'):
            with self.subTest(version_id=version_id):
                out = mao_siling_pilot(case['birth'],
                                       version_id=version_id,
                                       jie_facts=facts)
                self.assertEqual(out['status'], 'rejected')
                self.assertEqual(out['reason'], 'not_pilot_version')
                self.assertIsNone(out['commander'])

    def test_forged_jingzhe_rejected(self) -> None:
        case, facts = self._facts()
        facts['jingzhe']['at'] = '2024-03-05T10:23:45+08:00'  # +60s
        out = mao_siling_pilot(case['birth'], version_id='sanming-t1',
                               jie_facts=facts)
        self.assertEqual(out['status'], 'rejected')
        self.assertEqual(out['reason'], 'provider_replay_mismatch')
        self.assertIsNone(out['commander'])

    def test_wrong_provider_version_rejected(self) -> None:
        case, facts = self._facts()
        facts['provider']['version'] = '1.4.9'
        out = mao_siling_pilot(case['birth'], version_id='sanming-t1',
                               jie_facts=facts)
        self.assertEqual(out['status'], 'rejected')
        self.assertEqual(out['reason'], 'provider_identity_unverified')

    def test_unverified_provider_identity_rejected(self) -> None:
        case, facts = self._facts()
        facts['provider']['identity_verified'] = False
        out = mao_siling_pilot(case['birth'], version_id='sanming-t1',
                               jie_facts=facts)
        self.assertEqual(out['status'], 'rejected')
        self.assertEqual(out['reason'], 'provider_identity_unverified')

    def test_wrong_term_names_rejected(self) -> None:
        case, facts = self._facts()
        facts['next_jie']['term'] = '清明'
        out = mao_siling_pilot(case['birth'], version_id='sanming-t1',
                               jie_facts=facts)
        self.assertEqual(out['status'], 'rejected')
        self.assertEqual(out['reason'], 'jie_term_mismatch')

    def test_missing_next_jie_rejected(self) -> None:
        case, facts = self._facts()
        facts.pop('next_jie')
        out = mao_siling_pilot(case['birth'], version_id='sanming-t1',
                               jie_facts=facts)
        self.assertEqual(out['status'], 'rejected')
        self.assertEqual(out['reason'], 'jie_facts_incomplete')

    def test_jie_instant_with_microseconds_is_uncertain(self) -> None:
        case, facts = self._facts()
        facts['jingzhe']['at'] = '2024-03-05T10:22:45.500000+08:00'
        out = mao_siling_pilot(case['birth'], version_id='sanming-t1',
                               jie_facts=facts)
        self.assertEqual(out['status'], 'uncertain')
        self.assertEqual(out['reason'], 'jie_precision_insufficient')

    def test_missing_precision_declaration_is_uncertain(self) -> None:
        case, facts = self._facts()
        facts['jingzhe'].pop('precision')
        out = mao_siling_pilot(case['birth'], version_id='sanming-t1',
                               jie_facts=facts)
        self.assertEqual(out['status'], 'uncertain')
        self.assertEqual(out['reason'], 'jie_precision_insufficient')

    def test_birth_precision_not_second_is_uncertain(self) -> None:
        case, facts = self._facts()
        out = mao_siling_pilot(case['birth'], version_id='sanming-t1',
                               jie_facts=facts,
                               birth_time_precision='minute')
        self.assertEqual(out['status'], 'uncertain')
        self.assertEqual(out['reason'], 'birth_time_precision_insufficient')

    def test_precision_warning_interval_containing_birth(self) -> None:
        case, facts = self._facts()
        facts['precision_warning_interval'] = {
            'start': '2024-03-01T00:00:00+08:00',
            'end': '2024-04-01T00:00:00+08:00'}
        out = mao_siling_pilot(case['birth'], version_id='sanming-t1',
                               jie_facts=facts)
        self.assertEqual(out['status'], 'uncertain')
        self.assertEqual(out['reason'], 'precision_warning_interval')
        self.assertIsNone(out['commander'])

    def test_precision_warning_interval_outside_window_passes(self) -> None:
        case, facts = self._facts()
        facts['precision_warning_interval'] = {
            'start': '2024-05-01T00:00:00+08:00',
            'end': '2024-05-02T00:00:00+08:00'}
        out = mao_siling_pilot(case['birth'], version_id='sanming-t1',
                               jie_facts=facts)
        self.assertEqual(out['status'], 'computed')
        self.assertEqual(out['commander'], '甲')

    def test_naive_birth_raises(self) -> None:
        case, facts = self._facts()
        with self.assertRaises(ValueError):
            mao_siling_pilot('2024-03-05T10:22:45',
                             version_id='sanming-t1', jie_facts=facts)

    def test_subsecond_birth_raises(self) -> None:
        case, facts = self._facts()
        with self.assertRaises(ValueError):
            mao_siling_pilot('2024-03-05T10:22:45.1+08:00',
                             version_id='sanming-t1', jie_facts=facts)

    def test_forbidden_keys_absent_everywhere(self) -> None:
        for case in CASES:
            with self.subTest(case=case['id']):
                out = _run(case)
                self.assertEqual(set(_all_keys(out)) & FORBIDDEN_KEYS,
                                 set())

    def test_window_length_is_about_fifteen_days_not_thirty(self) -> None:
        # The ~15-day window is a measured fact of the 惊蛰→春分 replay,
        # never a hardcoded ~15.03-day constant: every window's replayed
        # length must sit in the 14–17 day envelope, far from 30 days.
        for case in CASES:
            if case['expected_status'] != 'computed':
                continue
            with self.subTest(case=case['id']):
                out = _run(case)
                self.assertGreater(out['window']['window_days'], 14.0)
                self.assertLess(out['window']['window_days'], 17.0)


class SiC1MarkingTest(unittest.TestCase):
    """巳月 C1 marking upgrade (user 2026-11-27 ②, option A).

    Only the C1 status marking changed: segments, Golden and Variant
    are untouched. The day-10 case must still compute 庚 (T1), while
    the C1 marker now states the approved wording.
    """

    def _si_facts(self):
        return {
            'provider': dict(PROVIDER),
            'lixia': {'term': '立夏', 'at': '2025-05-05T13:57:13+08:00',
                      'precision': 'second'},
            'next_jie': {'term': '芒种', 'at': '2025-06-05T17:56:32+08:00',
                         'precision': 'second'},
        }

    def test_c1_marker_carries_the_approved_wording(self) -> None:
        out = si_siling_pilot('2025-05-05T13:57:13+08:00',
                              version_id='sanming-t1',
                              jie_facts=self._si_facts())
        self.assertEqual(out['status'], 'computed')
        conflicts = {m['id']: m for m in out['conflicts']}
        self.assertEqual(conflicts['C1']['status'], C1_APPROVED_STATUS)
        self.assertIn('戊段下限十日', conflicts['C1']['summary'])
        self.assertIn('与 T1 七日冲突不调和', conflicts['C1']['summary'])
        self.assertEqual(conflicts['C1']['quote_id'], 'dt.case_si_wu')
        self.assertEqual(conflicts['C1']['locator'],
                         {'char_start': 108938, 'char_end': 108974})

    def test_c2_marker_still_pending_review(self) -> None:
        out = si_siling_pilot('2025-05-05T13:57:13+08:00',
                              version_id='sanming-t1',
                              jie_facts=self._si_facts())
        conflicts = {m['id']: m for m in out['conflicts']}
        self.assertEqual(conflicts['C2']['status'], 'pending_review')

    def test_day10_case_still_computes_geng_not_wu(self) -> None:
        # The C1 upgrade changes the MARKING only: the T1 computation
        # (戊 7 日) is untouched, so day 10 is still 庚, never 戊.
        out = si_siling_pilot('2025-05-15T05:57:13+00:00',
                              version_id='sanming-t1',
                              jie_facts=self._si_facts())
        self.assertEqual(out['commander'], '庚')
        self.assertEqual(out['elapsed_seconds'], 10 * 86400)
        derived, failure = si_pilot._derive_registration()
        self.assertIsNone(failure)
        self.assertEqual(
            derived['bounds'],
            [('戊', 0, 7 * 86400), ('庚', 7 * 86400, 12 * 86400),
             ('丙', 12 * 86400, 30 * 86400)])


class LiuyaoCareerNotApprovedTest(unittest.TestCase):
    """六爻 career 映射未批准钉位（证据注册已批，映射本身未批）.

    The registration package + mapping-submission draft live in
    ~/workspace/tj-batch5-liuyao-career/ (workspace files, NOT repo
    files). In the repo nothing is encoded as approved: the registry
    stays empty and assess() still abstains for career and all 7 other
    types.
    """

    def _input(self, question_type='career'):
        return {'question_type': question_type,
                'yao_values': [7, 8, 7, 7, 7, 9],
                'value': '2026-11-28T12:00:00+08:00'}

    def test_registry_stays_empty(self) -> None:
        self.assertEqual(USEFUL_GOD_MAPPINGS, {})

    def test_career_assess_still_abstains(self) -> None:
        out = assess(self._input('career'))
        self.assertEqual(out['status'], 'abstained')
        self.assertEqual(out['reason'], 'ambiguous_category')
        self.assertIsNone(out['verdict'])
        self.assertIsNone(out['useful_god'])

    def test_all_other_types_still_abstain(self) -> None:
        for question_type in ('wealth', 'marriage', 'health', 'examination',
                              'legal', 'travel', 'lost_property'):
            with self.subTest(question_type=question_type):
                out = assess(self._input(question_type))
                self.assertEqual(out['status'], 'abstained')
                self.assertIsNone(out['useful_god'])

    def test_career_mapping_slot_has_no_mapping(self) -> None:
        slot = mapping_slot('career')
        self.assertIsNone(slot['relative_role'])
        self.assertIsNone(slot['candidate_lines'])
        self.assertIsNone(slot['mapping'])
        self.assertEqual(slot['evidence_status'], 'no_approved_mapping')
        slots = {s['question_type']: s for s in list_mapping_slots()}
        self.assertEqual(len(slots), 8)
        self.assertTrue(all(s['mapping'] is None for s in slots.values()))


class ZiweiPeriodExtensionTest(unittest.TestCase):
    """紫微大限/流年候选扩展（research_only；分歧保持隔离）."""

    def test_decade_for_age_anchor_case(self) -> None:
        # Anchor: 火六局、命宫酉、甲子年（甲阳干）男命顺行，6-15 酉命宫。
        out = decade_for_age(bureau_number=6, life_palace_branch='酉',
                             year_stem='甲', sex='男', age=10)
        self.assertEqual(out['status'], 'computed')
        self.assertEqual(out['rule_status'], RULE_STATUS)
        self.assertTrue(out['research_only'])
        self.assertIsNone(out['determination'])
        self.assertIsNone(out['verdict'])
        self.assertEqual(out['decade'],
                         {'decade': 1, 'palace': '命宫', 'branch': '酉',
                          'age_start': 6, 'age_end': 15})
        self.assertEqual(decade_for_age(
            bureau_number=6, life_palace_branch='酉', year_stem='甲',
            sex='男', age=16)['decade']['palace'], '兄弟')
        self.assertEqual(decade_for_age(
            bureau_number=6, life_palace_branch='酉', year_stem='甲',
            sex='男', age=6)['decade']['decade'], 1)

    def test_decade_for_age_outside_covered_range_is_not_applicable(self) -> None:
        out = decade_for_age(bureau_number=6, life_palace_branch='酉',
                             year_stem='甲', sex='男', age=5)
        self.assertEqual(out['status'], 'not_applicable')
        self.assertEqual(out['reason'], 'age_outside_covered_decades')
        self.assertIsNone(out['decade'])
        self.assertEqual(out['covered_age_range'], [6, 125])
        out = decade_for_age(bureau_number=6, life_palace_branch='酉',
                             year_stem='甲', sex='男', age=126)
        self.assertEqual(out['status'], 'not_applicable')
        self.assertIsNone(out['decade'])

    def test_decade_for_age_rejects_bad_age(self) -> None:
        for bad in (-1, 10.5, '10', True, None):
            with self.subTest(bad=bad):
                with self.assertRaises(ValueError):
                    decade_for_age(bureau_number=6, life_palace_branch='酉',
                                   year_stem='甲', sex='男', age=bad)

    def test_annual_palaces_for_decade_matches_single_year_calls(self) -> None:
        out = annual_palaces_for_decade(
            life_palace_branch='酉', birth_year_branch='子',
            decade_start_year_branch='子', convention='branch_plus')
        self.assertEqual(out['rule_status'], RULE_STATUS)
        self.assertTrue(out['research_only'])
        self.assertIsNone(out['determination'])
        self.assertEqual(len(out['years']), 10)
        self.assertEqual(out['years'][0]['year_offset_in_decade'], 0)
        self.assertEqual(out['years'][0]['target_year_branch'], '子')
        self.assertEqual(out['years'][9]['target_year_branch'], '酉')
        for i, entry in enumerate(out['years']):
            one = annual_palace(
                life_palace_branch='酉', birth_year_branch='子',
                target_year_branch=entry['target_year_branch'],
                convention='branch_plus')
            self.assertEqual(entry['annual_palace'], one['annual_palace'])
            self.assertEqual(entry['annual_palace_branch'],
                             one['annual_palace_branch'])
            self.assertEqual(entry['year_offset'], i)

    def test_annual_step_direction_still_caller_specified(self) -> None:
        plus = annual_palaces_for_decade(
            life_palace_branch='酉', birth_year_branch='子',
            decade_start_year_branch='子', convention='branch_plus')
        minus = annual_palaces_for_decade(
            life_palace_branch='酉', birth_year_branch='子',
            decade_start_year_branch='子', convention='branch_minus')
        self.assertNotEqual(plus['years'][1]['annual_palace'],
                            minus['years'][1]['annual_palace'])
        self.assertEqual(plus['years'][0], minus['years'][0])
        for bad in ('forward', 'plus', None, ''):
            with self.subTest(bad=bad):
                with self.assertRaises(ValueError):
                    annual_palaces_for_decade(
                        life_palace_branch='酉', birth_year_branch='子',
                        decade_start_year_branch='子', convention=bad)

    def test_period_disputes_stay_unresolved_and_isolated(self) -> None:
        out = period_disputes()
        self.assertEqual(out['rule_status'], RULE_STATUS)
        self.assertTrue(out['research_only'])
        self.assertIsNone(out['determination'])
        ren = out['four_transformations_ren_year']
        self.assertEqual(ren['stem'], '壬')
        self.assertEqual(ren['status'], 'unresolved')
        self.assertIsNone(ren['determination'])
        self.assertEqual(ren['iztro_default_v2'], {'化科': '左辅'})
        self.assertEqual(ren['isolated_candidate']['stage'], 'quarantine')
        kuiyue = out['kuiyue_song']
        self.assertEqual(kuiyue['status'], 'unresolved')
        self.assertEqual(kuiyue['classical_reading'], '丙丁猪狗')
        self.assertEqual(kuiyue['modern_implementation_reading'], '丙丁猪鸡')
        self.assertIsNone(kuiyue['determination'])
        # No computation exists behind the registry entries.
        self.assertIsNone(out['computed_sihua'])
        self.assertIsNone(out['computed_kuiyue_palaces'])
        self.assertIsNone(out['verdict'])  # envelope default: no verdict
        for key in ('score', '庙旺', '吉凶'):
            self.assertNotIn(key, out)


class MovingYaoStructureTest(unittest.TestCase):
    """动爻/变爻结构事实钉位：效力层恒 abstain."""

    def test_moving_lines_from_yao_values(self) -> None:
        self.assertEqual(moving_lines([7, 8, 7, 7, 7, 9]), [6])
        self.assertEqual(moving_lines([8, 8, 6, 7, 7, 6]), [3, 6])
        self.assertEqual(moving_lines([7, 8, 7, 8, 7, 8]), [])
        motion = line_motion([7, 8, 7, 7, 7, 9])
        self.assertEqual([m['moving'] for m in motion],
                         [False, False, False, False, False, True])
        with self.assertRaises(ValueError):
            moving_lines([7, 8, 7, 7, 7, 5])

    def test_changed_line_facts_static_lines_can_change_branch(self) -> None:
        # Evidence-pack-05 case C1 (火天同人變革）: lines 4 and 5 are
        # static (7) yet their changed branches differ — branch change
        # is a whole-hexagram najia fact, never a motion verdict.
        out = changed_line_facts(
            [7, 8, 7, 7, 7, 9],
            ['卯', '丑', '亥', '午', '申', '戌'],
            ['卯', '丑', '亥', '亥', '酉', '未'])
        self.assertEqual(out['moving_lines'], [6])
        self.assertEqual(out['branch_changed_lines'], [4, 5, 6])
        self.assertFalse(out['lines'][3]['moving'])
        self.assertTrue(out['lines'][3]['branch_changed'])
        self.assertIsNone(out['effect'])
        self.assertIsNone(out['verdict'])

    def test_moving_effect_still_abstains(self) -> None:
        structure = changed_line_facts(
            [7, 8, 7, 7, 7, 9],
            ['卯', '丑', '亥', '午', '申', '戌'],
            ['卯', '丑', '亥', '亥', '酉', '未'])
        out = assess_moving_effect(structure)
        self.assertEqual(out['status'], 'insufficient_basis')
        self.assertIsNone(out['effect'])
        self.assertIsNone(out['verdict'])
        self.assertEqual(out['moving_lines'], [6])
        self.assertIn('registered_return_effect_rule',
                      out['unmet_conditions'])

    def test_dark_moving_strong_is_always_undetermined(self) -> None:
        # s010 needs 旺 (strong) — no registered wangshuai mapping (L-04),
        # so dark_moving is always None, never forced True/False.
        out = dark_moving_structure(['卯', '丑', '亥', '午', '申', '戌'],
                                    [7, 8, 7, 7, 7, 9], '未', '丁卯')
        for line in out['lines']:
            self.assertIsNone(line['strong'])
            self.assertIsNone(line['dark_moving'])


class PublicProjectionNoteTest(unittest.TestCase):
    """公开投影剥离（防御性剥离行在 public_projection.py，E0427 已补入）.

    The 卯月 pilot is a standalone research module, never wired into
    any chart or scenario; its output contract is research_only with
    public_enabled=false. The defensive projection strip for the
    ``siling_mao_pilot`` key is defense-in-depth, and this test pins
    both the contract and the strip itself.
    """

    def test_pilot_output_contract_is_research_only(self) -> None:
        case = next(c for c in CASES if c['id'] == 'g09_at_jingzhe')
        out = _run(case)
        self.assertTrue(out['research_only'])
        self.assertFalse(out['public_enabled'])
        self.assertFalse(out['ai_enabled'])
        self.assertEqual(out['variant'], 'bazi-siling-mao-pilot-v1')
        self.assertEqual(mao_pilot.SILING_MAO_PILOT_VARIANT,
                         'bazi-siling-mao-pilot-v1')

    def test_siling_mao_pilot_block_stripped_from_public_projection(self) -> None:
        from tianji_kb.public_projection import project_execution

        case = next(c for c in CASES if c['id'] == 'g09_at_jingzhe')
        block = _run(case)
        self.assertEqual(block['commander'], '甲')
        payload = {
            'evidence': {},
            'rule_matches': [],
            'trace': [],
            'chart': {'siling_mao_pilot': block},
            'result': {'siling_mao_pilot': block},
        }
        projected = project_execution(payload)
        self.assertNotIn('siling_mao_pilot', projected['chart'])
        self.assertNotIn('siling_mao_pilot', projected['result'])


if __name__ == '__main__':
    unittest.main()
