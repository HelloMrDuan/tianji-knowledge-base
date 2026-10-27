"""TJ-012.3 Slice C step 2 public contracts: 寅月分日司令试点 Variant.

Golden expectations in ``golden_tj012_siling_pilot.json`` are derived
BY HAND from the registered calculation_convention
(siling-calculation-convention v1): real elapsed seconds from the
provider-verified 立春 instant t0, left-closed right-open segments
[t0, t0+7d) 戊 / [t0+7d, t0+14d) 丙 / [t0+14d, next_jie) 甲.
t0 provenance is documented in the Golden meta block (pinned provider
lunar-python==1.4.8 annual jieqi table; TJ-015.2 frozen JPL-cited
minute reference agrees at minute precision). No expected value in the
Golden was produced by running the implementation.

Covered here (public CI, no sealed assets): the nine-item user
checklist — ±1s boundaries at t0 / day-7 / day-14 / next jie,
cross-timezone same-instant consistency, historical-DST-era window
(elapsed time discriminates against naive local-date subtraction),
illegal provider, missing citations, non-pilot versions and
non-寅月 inputs never masquerading as pilot results, forged source /
conflicting version / uncertain input failing closed — plus
registration-consumption pins (segment bounds derived from the
registered convention, disclaimer verbatim from the registration),
determination-None and forbidden-key sweeps, and the public
projection strip. Snapshot-verbatim quote checks and assembled-env
replay live in test_tj012_siling_pilot_sealed.py (offline acceptance
only, NOT public CI).
"""

from __future__ import annotations

import copy
import json
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from tianji_kb import bazi_siling_matrix as matrix
from tianji_kb import bazi_siling_pilot as pilot
from tianji_kb.bazi_siling_pilot import yin_siling_pilot
from tianji_kb.public_projection import project_execution

ROOT = Path(__file__).resolve().parents[1]
GOLDEN = json.loads(
    (ROOT / 'tests/golden_tj012_siling_pilot.json').read_text('utf-8'))
CASES = GOLDEN['cases']

FORBIDDEN_KEYS = {
    'score', 'scores', 'rating', 'weight', 'weights', 'useful_god',
    'favorable', 'favourable', 'recommended', 'recommendation',
    'verdict', 'combined_verdict', 'final_verdict', 'resolution',
    'resolved_choice', 'preference', 'true_false', 'success_failure',
    'pattern_name',
    '喜用神', '用神', '喜神', '忌神', '吉凶', '评分', '推荐', '权重', '裁决',
    '真格', '假格', '成格', '破格',
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
    facts = {
        'provider': dict(GOLDEN['provider']),
        'lichun': dict(window['lichun']),
        'next_jie': dict(window['next_jie']),
    }
    override = case.get('jie_override') or {}
    if override.get('drop_next_jie'):
        facts.pop('next_jie')
    if 'lichun_at' in override:
        facts['lichun']['at'] = override['lichun_at']
    if 'lichun_precision' in override:
        facts['lichun']['precision'] = override['lichun_precision']
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


def _run(case):
    return yin_siling_pilot(
        case['birth'], version_id=case['version_id'],
        jie_facts=_jie_facts(case),
        birth_time_precision=case.get('birth_time_precision', 'second'))


class GoldenBoundaryTest(unittest.TestCase):
    def test_all_golden_cases(self) -> None:
        self.assertEqual(len(CASES), 29)
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
                if case['expected_status'] != 'computed':
                    self.assertNotIn('segment', out)
                    self.assertIsNone(out['month_branch'])

    def test_computed_segment_boundaries_match_hand_derivation(self) -> None:
        # 2024 window, birth exactly at t0: segment 1 spans the whole
        # hand-derived [t0, t0+7d) in both UTC and Asia/Shanghai forms.
        case = next(c for c in CASES if c['id'] == 'g02_at_lichun')
        out = _run(case)
        self.assertEqual(out['segment']['index'], 1)
        self.assertEqual(out['segment']['start']['utc'],
                         '2024-02-04T08:27:07+00:00')
        self.assertEqual(out['segment']['end']['utc'],
                         '2024-02-11T08:27:07+00:00')
        self.assertEqual(out['segment']['start']['asia_shanghai'],
                         '2024-02-04T16:27:07+08:00')
        self.assertEqual(out['elapsed_seconds'], 0)
        last = next(c for c in CASES if c['id'] == 'g09_next_jie_minus_1s')
        out = _run(last)
        self.assertEqual(out['segment']['index'], 3)
        self.assertEqual(out['segment']['end']['utc'],
                         '2024-03-05T02:22:45+00:00')
        self.assertEqual(out['window']['next_jie']['term'], '惊蛰')

    def test_dst_case_discriminates_against_naive_date_subtraction(self):
        # The 1987 case must actually discriminate: naive local-date
        # subtraction (Feb 11 - Feb 4 = 7 days -> "day 8") would land
        # in segment 2, while real elapsed time (< 7 days) is segment 1.
        case = next(c for c in CASES
                    if c['id'] == 'g13_dst_era_1987_elapsed_not_date_diff')
        birth_local = datetime.fromisoformat(case['birth'])
        lichun_local = datetime.fromisoformat(
            GOLDEN['jie_windows']['1987']['lichun']['at'])
        naive_day_index = (birth_local.date()
                           - lichun_local.date()).days + 1
        self.assertEqual(naive_day_index, 8)  # naive reading: segment 2
        out = _run(case)
        self.assertEqual(out['commander'], '戊')  # elapsed reading: seg 1
        self.assertEqual(out['segment']['index'], 1)
        self.assertLess(out['elapsed_seconds'], 7 * 86400)


class RegistrationConsumptionTest(unittest.TestCase):
    def test_segment_bounds_derived_from_registered_convention(self) -> None:
        derived, failure = pilot._derive_registration()
        self.assertIsNone(failure)
        self.assertEqual(
            derived['bounds'],
            [('戊', 0, 7 * 86400), ('丙', 7 * 86400, 14 * 86400),
             ('甲', 14 * 86400, None)])
        self.assertEqual(derived['convention']['id'],
                         'siling-calculation-convention')
        self.assertEqual(derived['convention']['version'], 'v1')
        self.assertEqual(derived['quote']['id'], 'dt.s024_yinyue')
        self.assertEqual(derived['quote']['layer'], '原注')

    def test_provenance_disclaimer_is_registration_verbatim(self) -> None:
        case = next(c for c in CASES if c['id'] == 'g02_at_lichun')
        out = _run(case)
        prov = out['provenance']
        self.assertEqual(prov['disclaimer'],
                         matrix.SILING_CALCULATION_CONVENTION['disclaimer'])
        self.assertIn('连续24小时计日', prov['disclaimer'])
        self.assertIn('不是已证实的传统文献唯一解释', prov['disclaimer'])
        self.assertEqual(prov['text_layer'], '原注')
        self.assertEqual(prov['source_id'], 'bazi.source.ditiansui-spouse')
        self.assertEqual(prov['source_section_id'], 'bazi.section.s024')
        self.assertEqual(prov['quote'],
                         '如寅月生人,立春后七日前,皆值戊土用事;八日后十四日前者,'
                         '丙火用事 ;十五日后,甲木用事。')
        self.assertEqual(prov['calculation_convention'],
                         {'id': 'siling-calculation-convention',
                          'version': 'v1'})
        self.assertEqual(out['provider_verification']['provider'],
                         'lunar-python')
        self.assertTrue(out['provider_verification']['replay_verified'])

    def test_tampered_registration_fails_closed(self) -> None:
        case = next(c for c in CASES if c['id'] == 'g02_at_lichun')
        original = matrix.SILING_CALCULATION_CONVENTION
        tampered = copy.deepcopy(original)
        tampered['segments'][1]['interval'] = '[t0+7*24h, t0+13*24h)'
        try:
            matrix.SILING_CALCULATION_CONVENTION = tampered
            out = _run(case)
        finally:
            matrix.SILING_CALCULATION_CONVENTION = original
        self.assertEqual(out['status'], 'rejected')
        self.assertEqual(out['reason'], 'registration_integrity_failure')
        self.assertIsNone(out['commander'])

    def test_tampered_adjudication_status_fails_closed(self) -> None:
        case = next(c for c in CASES if c['id'] == 'g02_at_lichun')
        cell = matrix.SILING_MATRIX['ditiansui-yuanshuo']['寅']
        original = cell['adjudication_status']
        try:
            cell['adjudication_status'] = 'conflict'
            out = _run(case)
        finally:
            cell['adjudication_status'] = original
        self.assertEqual(out['status'], 'rejected')
        self.assertEqual(out['reason'], 'registration_integrity_failure')
        self.assertIsNone(out['commander'])


class FailClosedTest(unittest.TestCase):
    def _facts(self):
        case = next(c for c in CASES if c['id'] == 'g02_at_lichun')
        return case, _jie_facts(case)

    def test_precision_warning_interval_containing_birth(self) -> None:
        case, facts = self._facts()
        facts['precision_warning_interval'] = {
            'start': '2024-02-01T00:00:00+08:00',
            'end': '2024-03-01T00:00:00+08:00'}
        out = yin_siling_pilot(case['birth'],
                               version_id='ditiansui-yuanshuo',
                               jie_facts=facts)
        self.assertEqual(out['status'], 'uncertain')
        self.assertEqual(out['reason'], 'precision_warning_interval')
        self.assertIsNone(out['commander'])

    def test_precision_warning_interval_outside_window_passes(self) -> None:
        case, facts = self._facts()
        facts['precision_warning_interval'] = {
            'start': '2024-06-01T00:00:00+08:00',
            'end': '2024-06-02T00:00:00+08:00'}
        out = yin_siling_pilot(case['birth'],
                               version_id='ditiansui-yuanshuo',
                               jie_facts=facts)
        self.assertEqual(out['status'], 'computed')
        self.assertEqual(out['commander'], '戊')

    def test_forged_next_jie_rejected(self) -> None:
        case, facts = self._facts()
        facts['next_jie']['at'] = '2024-03-05T10:23:45+08:00'  # +60s
        out = yin_siling_pilot(case['birth'],
                               version_id='ditiansui-yuanshuo',
                               jie_facts=facts)
        self.assertEqual(out['status'], 'rejected')
        self.assertEqual(out['reason'], 'provider_replay_mismatch')
        self.assertIsNone(out['commander'])

    def test_jie_instant_with_microseconds_is_uncertain(self) -> None:
        case, facts = self._facts()
        facts['lichun']['at'] = '2024-02-04T16:27:07.500000+08:00'
        out = yin_siling_pilot(case['birth'],
                               version_id='ditiansui-yuanshuo',
                               jie_facts=facts)
        self.assertEqual(out['status'], 'uncertain')
        self.assertEqual(out['reason'], 'jie_precision_insufficient')

    def test_missing_precision_declaration_is_uncertain(self) -> None:
        case, facts = self._facts()
        facts['lichun'].pop('precision')
        out = yin_siling_pilot(case['birth'],
                               version_id='ditiansui-yuanshuo',
                               jie_facts=facts)
        self.assertEqual(out['status'], 'uncertain')
        self.assertEqual(out['reason'], 'jie_precision_insufficient')

    def test_wrong_term_names_rejected(self) -> None:
        case, facts = self._facts()
        facts['next_jie']['term'] = '雨水'
        out = yin_siling_pilot(case['birth'],
                               version_id='ditiansui-yuanshuo',
                               jie_facts=facts)
        self.assertEqual(out['status'], 'rejected')
        self.assertEqual(out['reason'], 'jie_term_mismatch')

    def test_naive_birth_raises(self) -> None:
        case, facts = self._facts()
        with self.assertRaises(ValueError):
            yin_siling_pilot('2024-02-04T16:27:07',
                             version_id='ditiansui-yuanshuo',
                             jie_facts=facts)

    def test_subsecond_birth_raises(self) -> None:
        case, facts = self._facts()
        with self.assertRaises(ValueError):
            yin_siling_pilot('2024-02-04T16:27:07.1+08:00',
                             version_id='ditiansui-yuanshuo',
                             jie_facts=facts)

    def test_forbidden_keys_absent_everywhere(self) -> None:
        for case in CASES:
            with self.subTest(case=case['id']):
                out = _run(case)
                self.assertEqual(set(_all_keys(out)) & FORBIDDEN_KEYS,
                                 set())


class ProjectionStripTest(unittest.TestCase):
    def test_siling_pilot_block_stripped_from_public_projection(self) -> None:
        case = next(c for c in CASES if c['id'] == 'g02_at_lichun')
        block = _run(case)
        self.assertEqual(block['commander'], '戊')
        payload = {
            'evidence': {},
            'rule_matches': [],
            'trace': [],
            'chart': {'siling_pilot': block},
            'result': {'siling_pilot': block},
        }
        projected = project_execution(payload)
        self.assertNotIn('siling_pilot', projected['chart'])
        self.assertNotIn('siling_pilot', projected['result'])


if __name__ == '__main__':
    unittest.main()
