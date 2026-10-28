"""TJ-011.2 F4 implementation, sealed replay (offline acceptance
only, NOT public CI): the segment-gated changsheng_visible_support
predicate (form bing-yin-changsheng-visible-support-v1, reading (乙)
segment_tightened, user adjudication 2026-10-28).

The predicate fires ONLY through the combination function
strength_assessment_changsheng(envelope, pilot_result): the plain
bounded assessment stays indeterminate for every F4 chart, because
chart() carries no birth instant and the effects layer must not
assert effectiveness for a segment-gated form. This module pins,
over real births executed through the production engine: the
positive 甲段 charts (combined strong, predicate
changsheng_visible_support, r026 bounded-exit shape, sufficient_rule
None, pending registration disclosure, nine why conditions each with
the register's anchor_type and anchor registration, segment gate
carried on the verdict); the gate-excluded 戊/丙段 charts (nine
conditions true, pilot computed, yet neither the plain nor the
combined path fires - the segment is the SOLE gate, additionally
proven at factor level by injecting a 甲 claim into the bounded
assessment of the 戊段 envelope); the near-miss / abstain /
conflict / wrong-month / 丁-not-applicable families driven by the
Golden; the §五 boundary and fail-closed battery at pilot and gate
level (segment switches ±1s on the registered windows, next-jie
boundary, cross-timezone same-instant equivalence, the 1987 DST-era
discriminator, provider identity mismatch, insufficient precision,
precision-warning interval, non-pilot versions T1/T2, forged pilot
blocks unverifiable); envelope idempotence; public projection /
display isolation; and verbatim regression of the existing
predicates' witness charts.
"""
import copy
import json
from datetime import datetime, timedelta
from pathlib import Path
import unittest
from zoneinfo import ZoneInfo

from tianji_kb import bazi_fire_si_yin_morphology as f34
from tianji_kb.bazi_adjudication import (
    ADJUDICATION_VARIANT, CHANGSHENG_ANCHOR_REGISTRATION,
    _bounded_assessment, _changsheng_trace_view,
    strength_assessment_changsheng)
from tianji_kb.bazi_siling_pilot import yin_siling_pilot
from tianji_kb.bazi_strength_display import get_display_decision
from tianji_kb.engine import execute
from tianji_kb.resolver import EvidenceResolver

ROOT = Path(__file__).resolve().parents[1]
GOLDEN = json.loads(
    (ROOT / 'tests' / 'golden_tj0112_bing_yin_changsheng.json')
    .read_text('utf-8'))
CASES = GOLDEN['cases']
BY_ID = {c['id']: c for c in CASES}
REGISTER_KEYS = [c['key'] for c in f34.FORM_BING_YIN['conditions']]
_VERSION = GOLDEN['meta']['pilot_version_id']


def _jie_facts(window, **overrides):
    w = GOLDEN['jie_windows'][window]
    facts = {'provider': dict(GOLDEN['provider']),
             'lichun': dict(w['lichun']),
             'next_jie': dict(w['next_jie'])}
    facts.update(overrides)
    return facts


def _pilot(birth, window, **kwargs):
    return yin_siling_pilot(birth, version_id=_VERSION,
                            jie_facts=_jie_facts(window), **kwargs)


def _predicate(assessment):
    why = assessment['why_not_indeterminate']
    return None if why is None else why['sufficient_predicate']


class ChangshengSealedTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cache = {}

    def bundle(self, case):
        cid = case['id']
        if cid not in self.cache:
            envelope = execute(
                'bazi', {'value': case['source_birth'],
                         'strength_variant': ADJUDICATION_VARIANT},
                allow_research=True)
            result = envelope['result']
            pilot = _pilot(case['source_birth'], case['window'])
            self.cache[cid] = {
                'envelope': envelope, 'result': result,
                'plain': result['strength_assessment'],
                'effects': result['action_effects'],
                'pilot': pilot,
                'combined': strength_assessment_changsheng(
                    envelope, pilot),
                'pillars': [p['stem']['value'] + p['branch']['value']
                            for p in result['pillars']]}
        return self.cache[cid]

    # -- chart sanity --------------------------------------------------
    def test_pillars_match_golden(self):
        for case in CASES:
            b = self.bundle(case)
            self.assertEqual(b['pillars'], case['expected_pillars'],
                             case['id'])

    def test_scope_condition_tables_match_golden(self):
        for case in CASES:
            b = self.bundle(case)
            scope = b['effects'][
                'changsheng_visible_support_scope_conditions']
            self.assertEqual(list(scope), REGISTER_KEYS, case['id'])
            self.assertEqual(scope, case['expected_conditions'],
                             case['id'])
            self.assertEqual(
                b['effects']['changsheng_visible_support_scope_met'],
                all(scope.values()), case['id'])

    def test_sealed_policy_not_edited(self):
        policy = EvidenceResolver().entities[
            'bazi.concept.action_effects_v1'][1]['attributes']
        self.assertEqual(policy['pure_months'], ['卯'])
        self.assertEqual(policy['isolated_months'], ['酉'])
        self.assertEqual(policy['reviewed_root_branches'],
                         {'木': ['亥', '寅', '卯'], '水': ['亥', '子'],
                          '金': ['酉']})
        self.assertNotIn('火', policy['reviewed_root_branches'])
        self.assertNotIn('土', policy['reviewed_root_branches'])

    # -- positives ------------------------------------------------------
    def test_positive_combined_verdicts(self):
        positives = [c for c in CASES
                     if c['category'] == 'positive_strong']
        self.assertTrue(positives)
        register = {c['key']: c['anchor_type']
                    for c in f34.FORM_BING_YIN['conditions']}
        for case in positives:
            b = self.bundle(case)
            self.assertEqual(b['pilot']['status'], 'computed',
                             case['id'])
            self.assertEqual(b['pilot']['segment']['stem'], '甲',
                             case['id'])
            self.assertEqual(b['plain']['classification'],
                             'indeterminate', case['id'])
            self.assertIsNone(b['plain']['why_not_indeterminate'],
                              case['id'])
            a = b['combined']
            self.assertEqual(a['classification'], 'strong', case['id'])
            self.assertEqual(a['decision_status'],
                             'reviewed_sufficient_rule_matched',
                             case['id'])
            why = a['why_not_indeterminate']
            self.assertIsNotNone(why, case['id'])
            self.assertEqual(why['sufficient_predicate'],
                             'changsheng_visible_support', case['id'])
            self.assertIsNone(why['sufficient_rule'], case['id'])
            self.assertEqual(why['predicate_rule_registration'],
                             'pending_phase1_rule_registration',
                             case['id'])
            self.assertEqual(a['blockers'], [], case['id'])
            self.assertEqual([c['condition'] for c in why['conditions']],
                             REGISTER_KEYS, case['id'])
            for cond in why['conditions']:
                self.assertIs(cond['met'], True, case['id'])
                self.assertEqual(cond['anchor_type'],
                                 register[cond['condition']], case['id'])
                self.assertEqual(cond['anchor_registration'],
                                 CHANGSHENG_ANCHOR_REGISTRATION,
                                 case['id'])
            self.assertEqual(why['month_condition_reading'],
                             'segment_tightened', case['id'])
            gate_why = why['segment_gate']
            self.assertEqual(gate_why['pilot_variant'],
                             'bazi-siling-yin-pilot-v1', case['id'])
            self.assertEqual(gate_why['segment_stem'], '甲', case['id'])
            self.assertEqual(gate_why['segment_index'], 3, case['id'])
            self.assertEqual(gate_why['registered_interval'],
                             '[t0+14*24h, next_jie)', case['id'])
            self.assertEqual(gate_why['required_segment_stem'], '甲',
                             case['id'])
            self.assertIs(gate_why['met'], True, case['id'])
            self.assertEqual(gate_why['calculation_convention'],
                             {'id': 'siling-calculation-convention',
                              'version': 'v1'}, case['id'])
            gate = a['changsheng_segment_gate']
            self.assertEqual(gate['reading'], 'segment_tightened',
                             case['id'])
            self.assertEqual(gate['gate_outcome'], 'segment_jia',
                             case['id'])
            self.assertIs(gate['gate_passed'], True, case['id'])
            self.assertIs(gate['claim_verifiable'], True, case['id'])
            self.assertEqual(gate['pilot_status'], 'computed',
                             case['id'])

    def test_positive_governance_flags_and_limitations(self):
        for case in CASES:
            if case['category'] != 'positive_strong':
                continue
            a = self.bundle(case)['combined']
            self.assertIs(a['research_only'], True, case['id'])
            self.assertIs(a['public_enabled'], False, case['id'])
            self.assertIs(a['ai_enabled'], False, case['id'])
            joined = ''.join(a['limitations'])
            self.assertIn('寅月丙日主分支谓词尚待密封', joined)
            self.assertIn('segment-tightened', joined)
            self.assertIn('司令甲段', joined)

    # -- gate exclusions --------------------------------------------------
    def test_gate_excluded_segments_never_fire(self):
        excluded = [c for c in CASES
                    if c['category'] == 'gate_excluded_segment']
        self.assertTrue(excluded)
        seen = set()
        for case in excluded:
            b = self.bundle(case)
            seen.add(case['expect']['segment'])
            self.assertTrue(all(case['expected_conditions'].values()),
                            case['id'])
            self.assertEqual(b['pilot']['status'], 'computed',
                             case['id'])
            self.assertEqual(b['pilot']['segment']['stem'],
                             case['expect']['segment'], case['id'])
            for a in (b['plain'], b['combined']):
                self.assertEqual(a['classification'], 'indeterminate',
                                 case['id'])
                self.assertNotEqual(
                    _predicate(a), 'changsheng_visible_support',
                    case['id'])
            gate = b['combined']['changsheng_segment_gate']
            self.assertEqual(gate['gate_outcome'], 'segment_not_jia',
                             case['id'])
            self.assertIs(gate['gate_passed'], False, case['id'])
        self.assertEqual(seen, {'戊', '丙'})

    def test_segment_is_the_sole_gate_factor_level(self):
        """Factor-level: injecting a verifiable 甲 claim into the
        bounded assessment of the 戊段 design chart flips it to
        strong/changsheng - the nine conditions already hold there,
        so the segment gate is provably the only missing input.
        (The claim dict is hand-built at factor level; real-claim
        behaviour is covered by the pilot-driven tests.)"""
        case = BY_ID['tj0112-bingyin-gate-excluded-wu-segment']
        b = self.bundle(case)
        fake_claim = {
            'verifiable': True, 'status': 'computed', 'reason': None,
            'commander': '甲', 'segment_stem': '甲', 'segment_index': 3,
            'registered_interval': '[t0+14*24h, next_jie)',
            'calculation_convention': {
                'id': 'siling-calculation-convention', 'version': 'v1'}}
        view = _changsheng_trace_view(b['envelope'])
        a = _bounded_assessment(view, _segment_claim=fake_claim)
        self.assertEqual(a['classification'], 'strong')
        self.assertEqual(_predicate(a), 'changsheng_visible_support')

    # -- near-miss / abstain / conflict families ---------------------------
    def test_condition_failure_families(self):
        families = {'near_miss', 'abstain', 'conflict_blocked',
                    'ding_not_applicable'}
        for case in CASES:
            if case['category'] not in families:
                continue
            b = self.bundle(case)
            self.assertEqual(b['combined']['classification'],
                             case['expect']['combined_classification'],
                             case['id'])
            self.assertEqual(b['plain']['classification'],
                             case['expect']['plain_classification'],
                             case['id'])
            self.assertNotEqual(_predicate(b['combined']),
                                'changsheng_visible_support', case['id'])
            for cid in case['expect'].get('expect_conflict_ids', []):
                self.assertIn(cid, b['combined']['conflict_ids'],
                              case['id'])

    def test_wrong_month_fires_commanding_not_changsheng(self):
        for case in CASES:
            if case['category'] != 'wrong_month':
                continue
            b = self.bundle(case)
            self.assertEqual(b['combined']['classification'], 'strong',
                             case['id'])
            self.assertEqual(_predicate(b['combined']),
                             'commanding_visible_support', case['id'])
            scope = b['effects'][
                'changsheng_visible_support_scope_conditions']
            self.assertIs(scope['reviewed_generating_changsheng_month'],
                          False, case['id'])

    # -- pilot boundary battery on the registered windows ------------------
    def test_segment_boundaries_plus_minus_one_second(self):
        sh = ZoneInfo('Asia/Shanghai')
        for label, window in GOLDEN['jie_windows'].items():
            t0 = datetime.fromisoformat(window['lichun']['at'])
            nxt = datetime.fromisoformat(window['next_jie']['at'])
            day = timedelta(days=1)

            def at(instant):
                return _pilot(instant.astimezone(sh).isoformat(),
                              label)

            self.assertEqual(at(t0 - timedelta(seconds=1))['status'],
                             'not_applicable', label)
            self.assertEqual(at(t0)['segment']['stem'], '戊', label)
            self.assertEqual(
                at(t0 + 7 * day - timedelta(seconds=1))['segment']
                ['stem'], '戊', label)
            self.assertEqual(at(t0 + 7 * day)['segment']['stem'], '丙',
                             label)
            self.assertEqual(
                at(t0 + 14 * day - timedelta(seconds=1))['segment']
                ['stem'], '丙', label)
            self.assertEqual(at(t0 + 14 * day)['segment']['stem'],
                             '甲', label)
            self.assertEqual(
                at(nxt - timedelta(seconds=1))['segment']['stem'],
                '甲', label)
            self.assertEqual(at(nxt)['status'], 'not_applicable',
                             label)

    def test_cross_timezone_same_instant_same_segment(self):
        case = BY_ID['tj0112-bingyin-positive-jia-segment']
        b = self.bundle(case)
        instant = datetime.fromisoformat(case['source_birth'])
        for zone in ('Asia/Tokyo', 'UTC', 'America/New_York'):
            alt = instant.astimezone(ZoneInfo(zone)).isoformat()
            pilot = _pilot(alt, case['window'])
            self.assertEqual(pilot['status'], 'computed', zone)
            self.assertEqual(pilot['segment']['stem'], '甲', zone)
            combined = strength_assessment_changsheng(
                b['envelope'], pilot)
            self.assertEqual(combined['classification'], 'strong',
                             zone)

    def test_dst_era_elapsed_time_discriminator(self):
        # 1987 window (China DST era): local date subtraction would
        # read day 8 (丙段); real elapsed time is 6d7h38m20s < 7d, so
        # the segment stays 戊 - the pilot must not use date diffs.
        # The 1987 window is registered in the Slice C pilot Golden.
        pilot_golden = json.loads(
            (ROOT / 'tests' / 'golden_tj012_siling_pilot.json')
            .read_text('utf-8'))
        w = pilot_golden['jie_windows']['1987']
        facts = {'provider': dict(pilot_golden['provider']),
                 'lichun': dict(w['lichun']),
                 'next_jie': dict(w['next_jie'])}
        pilot = yin_siling_pilot('1987-02-11T00:30:00+08:00',
                                 version_id=_VERSION, jie_facts=facts)
        self.assertEqual(pilot['status'], 'computed')
        self.assertEqual(pilot['segment']['stem'], '戊')
        same = yin_siling_pilot('1987-02-11T01:30:00+09:00',
                                version_id=_VERSION, jie_facts=facts)
        self.assertEqual(same['segment']['stem'], '戊')

    # -- fail-closed gate battery -------------------------------------------
    def _positive_bundle(self):
        return self.bundle(BY_ID['tj0112-bingyin-positive-jia-segment'])

    def test_gate_fails_closed_on_noncomputed_pilot(self):
        case = BY_ID['tj0112-bingyin-positive-jia-segment']
        b = self._positive_bundle()
        birth = case['source_birth']
        facts = _jie_facts(case['window'])
        facts['provider'] = {'name': 'lunar-python', 'version': '1.4.7',
                             'identity_verified': True}
        facts_warn = _jie_facts(case['window'])
        facts_warn['precision_warning'] = True
        # The pilot's precision warning is an EXPLICIT input
        # declaration under its registered contract (jie_facts
        # 'precision_warning_interval'), never an interval the
        # pilot derives around a segment boundary: declare an
        # interval covering a birth 30 s into the Jia segment.
        _lichun = datetime.fromisoformat(
            GOLDEN['jie_windows'][case['window']]['lichun']['at'])
        _warn_birth = (_lichun + timedelta(days=14, seconds=30))
        facts_warn_interval = _jie_facts(
            case['window'],
            precision_warning_interval={
                'start': (_lichun + timedelta(days=14)).isoformat(),
                'end': (_lichun + timedelta(
                    days=14, seconds=90)).isoformat()})
        variants = {
            'provider_missing': yin_siling_pilot(
                birth, version_id=_VERSION, jie_facts={}),
            'provider_identity': yin_siling_pilot(
                birth, version_id=_VERSION, jie_facts=facts),
            't1_version': yin_siling_pilot(
                birth, version_id='sanming-t1',
                jie_facts=_jie_facts(case['window'])),
            't2_version': yin_siling_pilot(
                birth, version_id='sanming-t2',
                jie_facts=_jie_facts(case['window'])),
            'warning_flag': yin_siling_pilot(
                birth, version_id=_VERSION, jie_facts=facts_warn),
            'warning_interval': yin_siling_pilot(
                _warn_birth.isoformat(), version_id=_VERSION,
                jie_facts=facts_warn_interval),
            'minute_precision': _pilot(
                birth, case['window'], birth_time_precision='minute'),
        }
        self.assertEqual(variants['provider_identity']['status'],
                         'rejected')
        self.assertEqual(variants['t1_version']['reason'],
                         'not_pilot_version')
        self.assertEqual(variants['warning_interval']['status'],
                         'uncertain')
        for name, pilot in variants.items():
            self.assertNotEqual(pilot['status'], 'computed', name)
            combined = strength_assessment_changsheng(
                b['envelope'], pilot)
            self.assertEqual(combined['classification'],
                             'indeterminate', name)
            self.assertEqual(
                combined['changsheng_segment_gate']['gate_outcome'],
                'pilot_not_computed', name)
            self.assertIs(
                combined['changsheng_segment_gate']['gate_passed'],
                False, name)

    def test_gate_fails_closed_on_forged_pilot_block(self):
        b = self._positive_bundle()
        forged = copy.deepcopy(b['pilot'])
        forged['segment']['stem'] = '戊'
        forged['commander'] = '戊'
        combined = strength_assessment_changsheng(b['envelope'], forged)
        self.assertEqual(combined['classification'], 'indeterminate')
        self.assertEqual(
            combined['changsheng_segment_gate']['gate_outcome'],
            'pilot_claim_unverifiable')
        forged = copy.deepcopy(b['pilot'])
        forged['provenance']['calculation_convention'] = {
            'id': 'siling-calculation-convention', 'version': 'v9'}
        combined = strength_assessment_changsheng(b['envelope'], forged)
        self.assertEqual(combined['classification'], 'indeterminate')
        self.assertEqual(
            combined['changsheng_segment_gate']['gate_outcome'],
            'pilot_claim_unverifiable')
        combined = strength_assessment_changsheng(b['envelope'], None)
        self.assertEqual(combined['classification'], 'indeterminate')
        self.assertEqual(
            combined['changsheng_segment_gate']['gate_outcome'],
            'pilot_claim_unverifiable')

    def test_envelope_round_trip_idempotent(self):
        b = self._positive_bundle()
        first = strength_assessment_changsheng(b['envelope'],
                                               b['pilot'])
        second = strength_assessment_changsheng(b['envelope'],
                                                b['pilot'])
        for a in (first, second):
            self.assertEqual(a['classification'], 'strong')
            self.assertEqual(_predicate(a),
                             'changsheng_visible_support')

    # -- public isolation ------------------------------------------------------
    def test_public_projection_and_display_isolation(self):
        from tianji_kb.bazi_strength_display import (
            PUBLIC_STRENGTH_VARIANTS)
        from tianji_kb.public_projection import project_execution
        b = self._positive_bundle()
        self.assertEqual(PUBLIC_STRENGTH_VARIANTS, frozenset())
        projected = project_execution(b['envelope'])
        bounded = projected['result']['strength_assessment']
        self.assertEqual(bounded['classification'], 'indeterminate')
        self.assertNotIn('changsheng_segment_gate',
                         json.dumps(projected['result'],
                                    ensure_ascii=False))
        decision = get_display_decision(
            b['combined'], variant=ADJUDICATION_VARIANT,
            day_master='丙', month_branch='寅')
        self.assertFalse(decision['may_display_classification'])
        self.assertIsNone(decision['classification'])

    # -- regression: existing predicate witnesses verbatim ----------------------
    def test_existing_predicate_witnesses_unchanged(self):
        # Identity of the firing sufficiency: unregistered
        # predicates report why['sufficient_predicate'] (r026
        # exit); the S5-registered commanding predicate reports
        # why['sufficient_rule'] with its Phase2 rule ID.
        def identity(a):
            why = a['why_not_indeterminate'] or {}
            return (why.get('sufficient_predicate')
                    or why.get('sufficient_rule'))

        witnesses = [
            ('1927-05-12T12:00:00+08:00', 'strong',
             'lu_visible_support'),
            ('1981-12-21T23:00:00+08:00', 'strong',
             'pure_generating_support_water'),
            ('1966-07-06T12:00:00+08:00', 'strong',
             'bazi.phase2.strength_commanding_visible_support'),
        ]
        for birth, classification, fired in witnesses:
            envelope = execute(
                'bazi', {'value': birth,
                         'strength_variant': ADJUDICATION_VARIANT},
                allow_research=True)
            a = envelope['result']['strength_assessment']
            self.assertEqual(a['classification'], classification,
                             birth)
            self.assertEqual(identity(a), fired, birth)
            pilot = yin_siling_pilot(
                birth, version_id=_VERSION,
                jie_facts=_jie_facts('2014'))
            combined = strength_assessment_changsheng(envelope, pilot)
            self.assertEqual(combined['classification'],
                             classification, birth)
            self.assertEqual(identity(combined), fired, birth)


if __name__ == '__main__':
    unittest.main()
