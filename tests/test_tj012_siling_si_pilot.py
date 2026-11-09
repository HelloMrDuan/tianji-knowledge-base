"""TJ-012.3 Slice C 巳月试点 public contracts: 巳月分日司令试点 Variant.

Golden expectations in ``golden_tj012_siling_si_pilot.json`` are derived
BY HAND from the registered calculation_convention
(siling-si-calculation-convention v1): real elapsed seconds from the
provider-verified 立夏 instant t0, left-closed right-open segments
[t0, t0+7d) 戊 / [t0+7d, t0+12d) 庚 / [t0+12d, t0+30d) 丙, with the
[t0+30d, 芒种) tail outside the registered thirty days (uncertain,
never extrapolated). t0 provenance is documented in the Golden meta
block (pinned provider lunar-python==1.4.8 annual jieqi table). No
expected value in the Golden was produced by running the
implementation.

Covered here (public CI, no sealed assets): the user checklist —
±1s boundaries at t0 / day-7 / day-12 / day-30 / next jie, the pinned
day-10 conflict case (C1 noted, never smoothed over), cross-year
2025+2026, cross-timezone same-instant consistency in the 1988 DST
era, illegal provider, missing citations, non-pilot versions and
non-巳月 inputs never masquerading as pilot results, forged source /
conflicting version / uncertain input failing closed — plus
registration-consumption pins (segment bounds derived from the
registered convention, disclaimer verbatim, tampered registration
fails closed), the top-level C1/C2 conflict markers, determination-None
and forbidden-key sweeps, and the public projection strip.
Snapshot-verbatim quote checks and assembled-env replay live in
test_tj012_siling_si_pilot_sealed.py (offline acceptance only, NOT
public CI).
"""

from __future__ import annotations

import copy
import json
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from tianji_kb import bazi_siling_matrix as matrix
from tianji_kb import bazi_siling_si_pilot as pilot
from tianji_kb.bazi_siling_si_pilot import si_siling_pilot
from tianji_kb.public_projection import project_execution

ROOT = Path(__file__).resolve().parents[1]
GOLDEN = json.loads(
    (ROOT / 'tests/golden_tj012_siling_si_pilot.json').read_text('utf-8'))
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
        'lixia': dict(window['lixia']),
        'next_jie': dict(window['next_jie']),
    }
    override = case.get('jie_override') or {}
    if override.get('drop_next_jie'):
        facts.pop('next_jie')
    if 'lixia_at' in override:
        facts['lixia']['at'] = override['lixia_at']
    if 'lixia_precision' in override:
        facts['lixia']['precision'] = override['lixia_precision']
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
    return si_siling_pilot(
        case['birth'], version_id=case['version_id'],
        jie_facts=_jie_facts(case),
        birth_time_precision=case.get('birth_time_precision', 'second'))


class GoldenBoundaryTest(unittest.TestCase):
    def test_all_golden_cases(self) -> None:
        self.assertEqual(len(CASES), 32)
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
        # 2025 window, birth exactly at t0: segment 1 spans the whole
        # hand-derived [t0, t0+7d) in both UTC and Asia/Shanghai forms.
        case = next(c for c in CASES if c['id'] == 'g02_at_lixia')
        out = _run(case)
        self.assertEqual(out['segment']['index'], 1)
        self.assertEqual(out['segment']['start']['utc'],
                         '2025-05-05T05:57:13+00:00')
        self.assertEqual(out['segment']['end']['utc'],
                         '2025-05-12T05:57:13+00:00')
        self.assertEqual(out['segment']['start']['asia_shanghai'],
                         '2025-05-05T13:57:13+08:00')
        self.assertEqual(out['elapsed_seconds'], 0)
        last = next(c for c in CASES if c['id'] == 'g08_day30_minus_1s')
        out = _run(last)
        self.assertEqual(out['segment']['index'], 3)
        self.assertEqual(out['segment']['end']['utc'],
                         '2025-06-04T05:57:13+00:00')
        self.assertEqual(out['segment']['registered_day_span'], [13, 30])
        self.assertEqual(out['segment']['registered_basis'], '丙火一十八日')
        self.assertEqual(out['window']['next_jie']['term'], '芒种')

    def test_pinned_day10_conflict_case_is_not_smoothed_over(self) -> None:
        # The day-10 case is the C1 conflict pin: Ren's case says 戊
        # still commands ten days after 立夏, while T1 gives 戊 only
        # seven days. The pilot follows the registered T1 segments
        # (庚 on day 10) AND carries the conflict marker; the case
        # must never be re-derived as 戊 to hide the conflict.
        case = next(c for c in CASES
                    if c['id'] == 'g05_day10_pinned_conflict')
        out = _run(case)
        self.assertEqual(out['commander'], '庚')
        self.assertEqual(out['elapsed_seconds'], 10 * 86400)
        conflicts = {m['id']: m for m in out['conflicts']}
        self.assertEqual(conflicts['C1']['status'], 'pending_review')
        self.assertIn('立夏后十天', conflicts['C1']['summary'])

    def test_dst_cases_are_the_same_instant(self) -> None:
        # 1988 is a China DST year (1986-1991): May carries +09:00.
        # The same absolute instant written with a claimed +08:00
        # offset and with the correct +09:00 offset must agree (庚),
        # because the pilot compares UTC instants, never the claimed
        # offset string.
        first = next(c for c in CASES
                     if c['id'] == 'g16_dst_era_1988_plus08')
        second = next(c for c in CASES
                      if c['id'] == 'g17_dst_era_1988_same_instant_plus09')
        self.assertEqual(
            datetime.fromisoformat(first['birth']).astimezone(timezone.utc),
            datetime.fromisoformat(second['birth']).astimezone(timezone.utc))
        self.assertEqual(_run(first)['commander'], '庚')
        self.assertEqual(_run(second)['commander'], '庚')

    def test_dst_case_discriminates_against_naive_date_subtraction(self):
        # 1988 window, birth at t0+7d-1s: naive local-date subtraction
        # (May 12 - May 5 = 7 days -> "day 8") would land in segment
        # 2, while real elapsed time (< 7 days) is segment 1.
        window = GOLDEN['jie_windows']['1988']
        facts = {'provider': dict(GOLDEN['provider']),
                 'lixia': dict(window['lixia']),
                 'next_jie': dict(window['next_jie'])}
        birth = '1988-05-12T15:01:42+09:00'
        birth_local = datetime.fromisoformat(birth)
        lixia_local = datetime.fromisoformat(window['lixia']['at'])
        naive_day_index = (birth_local.date()
                           - lixia_local.date()).days + 1
        self.assertEqual(naive_day_index, 8)  # naive reading: segment 2
        out = si_siling_pilot(birth, version_id='sanming-t1',
                              jie_facts=facts)
        self.assertEqual(out['commander'], '戊')  # elapsed reading: seg 1
        self.assertEqual(out['segment']['index'], 1)
        self.assertLess(out['elapsed_seconds'], 7 * 86400)


class RegistrationConsumptionTest(unittest.TestCase):
    def test_segment_bounds_derived_from_registered_convention(self) -> None:
        derived, failure = pilot._derive_registration()
        self.assertIsNone(failure)
        self.assertEqual(
            derived['bounds'],
            [('戊', 0, 7 * 86400), ('庚', 7 * 86400, 12 * 86400),
             ('丙', 12 * 86400, 30 * 86400)])
        self.assertEqual(derived['convention']['id'],
                         'siling-si-calculation-convention')
        self.assertEqual(derived['convention']['version'], 'v1')
        self.assertEqual(derived['quote']['id'], 'sm.t1_table')
        self.assertIsNone(derived['quote']['layer'])
        self.assertEqual(derived['excerpt'],
                         '巳中有戊土七日庚金长生五日丙火一十八日')
        self.assertEqual(derived['excerpt_locator'],
                         {'char_start': 48056, 'char_end': 48075})

    def test_provenance_disclaimer_is_registration_verbatim(self) -> None:
        case = next(c for c in CASES if c['id'] == 'g02_at_lixia')
        out = _run(case)
        prov = out['provenance']
        self.assertEqual(
            prov['disclaimer'],
            matrix.SILING_SI_CALCULATION_CONVENTION['disclaimer'])
        self.assertIn('连续24小时计日', prov['disclaimer'])
        self.assertIn('不是已证实的传统文献唯一解释', prov['disclaimer'])
        self.assertIsNone(prov['text_layer'])
        self.assertEqual(prov['source_id'], 'bazi.source.sanmingtonghui')
        self.assertIsNone(prov['source_section_id'])
        self.assertEqual(prov['quote'],
                         '巳中有戊土七日庚金长生五日丙火一十八日')
        self.assertEqual(prov['quote_locator'],
                         {'char_start': 48056, 'char_end': 48075})
        self.assertEqual(prov['calculation_convention'],
                         {'id': 'siling-si-calculation-convention',
                          'version': 'v1'})
        self.assertEqual(out['provider_verification']['provider'],
                         'lunar-python')
        self.assertTrue(out['provider_verification']['replay_verified'])

    def test_conflict_markers_name_c1_and_c2_with_locators(self) -> None:
        case = next(c for c in CASES if c['id'] == 'g02_at_lixia')
        out = _run(case)
        conflicts = {m['id']: m for m in out['conflicts']}
        self.assertEqual(set(conflicts), {'C1', 'C2'})
        c1 = conflicts['C1']
        self.assertEqual(c1['quote_id'], 'dt.case_si_wu')
        self.assertEqual(c1['source_id'], 'bazi.source.ditiansui-spouse')
        self.assertEqual(c1['layer'], '任氏曰')
        self.assertEqual(c1['locator'],
                         {'char_start': 108938, 'char_end': 108974})
        self.assertEqual(c1['status'], 'pending_review')
        c2 = conflicts['C2']
        self.assertEqual(c2['quote_id'], 'sf.geduan_song')
        self.assertEqual(c2['source_id'], 'bazi.source.shenfeng')
        self.assertEqual(c2['locator'],
                         {'char_start': 94774, 'char_end': 95004})
        self.assertEqual(c2['status'], 'pending_review')

    def test_conflict_markers_present_on_non_computed_outputs(self) -> None:
        # The Option B ruling requires the markers on the output, not
        # only on computed results: rejected / uncertain / not_applicable
        # outputs carry the same top-level conflicts field.
        for case_id in ('g01_before_lixia_1s', 'g09_day30_exact',
                        'g18_version_sanming_t2'):
            case = next(c for c in CASES if c['id'] == case_id)
            out = _run(case)
            self.assertEqual([m['id'] for m in out['conflicts']],
                             ['C1', 'C2'])
            self.assertTrue(all(m['status'] == 'pending_review'
                                for m in out['conflicts']))

    def test_tail_states_the_registration_gap(self) -> None:
        # The 30-day registration vs the ~31.17-day replayed window
        # must be explicit in the output, never silently extended.
        case = next(c for c in CASES if c['id'] == 'g09_day30_exact')
        out = _run(case)
        self.assertEqual(out['status'], 'uncertain')
        self.assertEqual(out['reason'], 'beyond_registered_segments')
        self.assertIn('31.17', out['note'])
        self.assertIn('三十日', out['note'])
        self.assertTrue(any('31.17' in line
                            for line in out['limitations']))

    def test_tampered_registration_fails_closed(self) -> None:
        case = next(c for c in CASES if c['id'] == 'g02_at_lixia')
        original = matrix.SILING_SI_CALCULATION_CONVENTION
        tampered = copy.deepcopy(original)
        tampered['segments'][1]['interval'] = '[t0+7*24h, t0+13*24h)'
        try:
            matrix.SILING_SI_CALCULATION_CONVENTION = tampered
            out = _run(case)
        finally:
            matrix.SILING_SI_CALCULATION_CONVENTION = original
        self.assertEqual(out['status'], 'rejected')
        self.assertEqual(out['reason'], 'registration_integrity_failure')
        self.assertIsNone(out['commander'])

    def test_tampered_adjudication_status_fails_closed(self) -> None:
        case = next(c for c in CASES if c['id'] == 'g02_at_lixia')
        cell = matrix.SILING_MATRIX['sanming-t1']['巳']
        original = cell['adjudication_status']
        try:
            cell['adjudication_status'] = 'conflict'
            out = _run(case)
        finally:
            cell['adjudication_status'] = original
        self.assertEqual(out['status'], 'rejected')
        self.assertEqual(out['reason'], 'registration_integrity_failure')
        self.assertIsNone(out['commander'])

    def test_tampered_excerpt_fails_closed(self) -> None:
        case = next(c for c in CASES if c['id'] == 'g02_at_lixia')
        cell = matrix.SILING_MATRIX['sanming-t1']['巳']
        original = cell['quote_excerpt']
        try:
            cell['quote_excerpt'] = '巳中有戊土八日庚金长生五日丙火一十八日'
            out = _run(case)
        finally:
            cell['quote_excerpt'] = original
        self.assertEqual(out['status'], 'rejected')
        self.assertEqual(out['reason'], 'registration_integrity_failure')
        self.assertIsNone(out['commander'])


class FailClosedTest(unittest.TestCase):
    def _facts(self):
        case = next(c for c in CASES if c['id'] == 'g02_at_lixia')
        return case, _jie_facts(case)

    def test_precision_warning_interval_containing_birth(self) -> None:
        case, facts = self._facts()
        facts['precision_warning_interval'] = {
            'start': '2025-05-01T00:00:00+08:00',
            'end': '2025-06-01T00:00:00+08:00'}
        out = si_siling_pilot(case['birth'],
                              version_id='sanming-t1',
                              jie_facts=facts)
        self.assertEqual(out['status'], 'uncertain')
        self.assertEqual(out['reason'], 'precision_warning_interval')
        self.assertIsNone(out['commander'])

    def test_precision_warning_interval_outside_window_passes(self) -> None:
        case, facts = self._facts()
        facts['precision_warning_interval'] = {
            'start': '2025-07-01T00:00:00+08:00',
            'end': '2025-07-02T00:00:00+08:00'}
        out = si_siling_pilot(case['birth'],
                              version_id='sanming-t1',
                              jie_facts=facts)
        self.assertEqual(out['status'], 'computed')
        self.assertEqual(out['commander'], '戊')

    def test_forged_next_jie_rejected(self) -> None:
        case, facts = self._facts()
        facts['next_jie']['at'] = '2025-06-05T17:57:32+08:00'  # +60s
        out = si_siling_pilot(case['birth'],
                              version_id='sanming-t1',
                              jie_facts=facts)
        self.assertEqual(out['status'], 'rejected')
        self.assertEqual(out['reason'], 'provider_replay_mismatch')
        self.assertIsNone(out['commander'])

    def test_jie_instant_with_microseconds_is_uncertain(self) -> None:
        case, facts = self._facts()
        facts['lixia']['at'] = '2025-05-05T13:57:13.500000+08:00'
        out = si_siling_pilot(case['birth'],
                              version_id='sanming-t1',
                              jie_facts=facts)
        self.assertEqual(out['status'], 'uncertain')
        self.assertEqual(out['reason'], 'jie_precision_insufficient')

    def test_missing_precision_declaration_is_uncertain(self) -> None:
        case, facts = self._facts()
        facts['lixia'].pop('precision')
        out = si_siling_pilot(case['birth'],
                              version_id='sanming-t1',
                              jie_facts=facts)
        self.assertEqual(out['status'], 'uncertain')
        self.assertEqual(out['reason'], 'jie_precision_insufficient')

    def test_wrong_term_names_rejected(self) -> None:
        case, facts = self._facts()
        facts['next_jie']['term'] = '小满'
        out = si_siling_pilot(case['birth'],
                              version_id='sanming-t1',
                              jie_facts=facts)
        self.assertEqual(out['status'], 'rejected')
        self.assertEqual(out['reason'], 'jie_term_mismatch')

    def test_naive_birth_raises(self) -> None:
        case, facts = self._facts()
        with self.assertRaises(ValueError):
            si_siling_pilot('2025-05-05T13:57:13',
                            version_id='sanming-t1',
                            jie_facts=facts)

    def test_subsecond_birth_raises(self) -> None:
        case, facts = self._facts()
        with self.assertRaises(ValueError):
            si_siling_pilot('2025-05-05T13:57:13.1+08:00',
                            version_id='sanming-t1',
                            jie_facts=facts)

    def test_forbidden_keys_absent_everywhere(self) -> None:
        for case in CASES:
            with self.subTest(case=case['id']):
                out = _run(case)
                self.assertEqual(set(_all_keys(out)) & FORBIDDEN_KEYS,
                                 set())


class ProjectionStripTest(unittest.TestCase):
    def test_siling_si_pilot_block_stripped_from_public_projection(self) -> None:
        case = next(c for c in CASES if c['id'] == 'g02_at_lixia')
        block = _run(case)
        self.assertEqual(block['commander'], '戊')
        payload = {
            'evidence': {},
            'rule_matches': [],
            'trace': [],
            'chart': {'siling_si_pilot': block},
            'result': {'siling_si_pilot': block},
        }
        projected = project_execution(payload)
        self.assertNotIn('siling_si_pilot', projected['chart'])
        self.assertNotIn('siling_si_pilot', projected['result'])


if __name__ == '__main__':
    unittest.main()
