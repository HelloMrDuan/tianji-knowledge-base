"""TJ-0426 Lane 1 (S-01~S-07) 旺衰 + 长生测试。

Offline assembled acceptance only (NOT public CI): chart-based cases
execute real births through the production calendar chain and the
canonical tables, which exist only in the assembled environment; the
bare worktree has no data/canonical. Run in the worktree with
``PYTHONPATH=src python -m unittest tests.test_tj0426_lane1_strength``.

Coverage:
- S-01/S-02: the 8th classical predicate changsheng_visible_support
  (F4 丙×寅, register bazi_fire_si_yin_morphology.FORM_BING_YIN),
  evaluated at factor level with the nine registered conditions plus
  the user-adjudicated segment gate (reading 乙 segment-tightened):
  it fires ONLY with a verified computed 寅月 pilot whose segment is
  甲. Positive (2034-02-19), 戊段 (2014-02-04) and 丙段 (2014-02-14)
  real births; no-pilot / forged / non-computed pilot fail-closed
  battery; ±1s segment-boundary sole-gate proof; 丁×寅 never applies.
  Every predicate hit reports verification="factor_level_only".
- S-01: the blocked classical forms (F2/F5/F6/F7) stay unregistered,
  with their blocking reasons on record.
- S-03: the changsheng conflict table draft is pure registration:
  10 stems, settled 丙/庚/壬, conflicts 丁/戊/己/辛/癸, unregistered
  甲/乙; it exposes no computation and the engine never consumes it.
- S-04: modern-layer calibration completeness is output-only (scores
  unchanged): tomb-month de_ling carries the canonical first hidden
  stem marked unreviewed; 土/丁 de_di carries the contract / conflict
  reference; no definite classification is ever washed out of a
  provisional score.
- S-05: cong establishment rules are all unregistered; candidates
  never establish (matrix sweep); 从杀/从儿 have no screen at all.
- S-06: no punishment table exists; interaction_conditions never
  emits a punishment record; Q3-A record-only still holds.
- S-07: MODERN_WEIGHTS / MODERN_THRESHOLDS pinned by full deep
  equality (read-only).
- Regression pins: f2 real chart (2024-02-11T16:27:07+08:00) unchanged,
  120-cell coverage matrix counts unchanged, 51-case Golden sweep
  unchanged.
"""
import copy
import json
import unittest
from datetime import datetime, timedelta
from pathlib import Path

from tianji_kb.bazi_core import chart_from_datetime
from tianji_kb.bazi_siling_pilot import yin_siling_pilot
from tianji_kb.bazi_strength_engine import (
    CONG_ESTABLISHMENT_GAPS, ENGINE_VARIANT, MODERN_MODEL_ID,
    MODERN_THRESHOLDS, MODERN_WEIGHTS, PREDICATES,
    UNREGISTERED_CLASSICAL_FORMS, assess_strength, coverage_matrix,
    default_coverage_template, identify_cong_candidates,
    interaction_conditions, validate_assessment)
from tianji_kb import bazi_branch_punishment as punishment_reg
from tianji_kb import bazi_changsheng_table as changsheng_reg
from tianji_kb.foundations import BRANCHES, STEMS

ROOT = Path(__file__).resolve().parents[1]

F4_GOLDEN = json.loads(
    (ROOT / 'tests' / 'golden_tj0112_f34_si_yin.json').read_text('utf-8'))
F4_CASES = {c['id']: c for c in F4_GOLDEN['cases']}
F4_GOLDEN_BINGYIN = json.loads(
    (ROOT / 'tests' / 'golden_tj0112_bing_yin_changsheng.json')
    .read_text('utf-8'))
F4_WINDOWS = F4_GOLDEN_BINGYIN['jie_windows']
F4_PROVIDER = F4_GOLDEN_BINGYIN['provider']
F4_VERSION = F4_GOLDEN_BINGYIN['meta']['pilot_version_id']

GOLDEN_FILES = [
    'tests/golden_tj0112_wood_hai.json',
    'tests/golden_tj0112_bing_wu_commanding.json',
    'tests/golden_tj0112_s2_metal_water.json',
    'tests/golden_tj0112_bing_si_lu.json',
    'tests/golden_tj0112_f34_si_yin.json',
    'tests/golden_tj0112_fire_morphology.json',
]

F2_BIRTH = '2024-02-11T16:27:07+08:00'  # 甲辰/丙寅/乙巳/甲申
F4_POSITIVE_BIRTH = '2034-02-19T12:00:00+08:00'
F4_WU_BIRTH = '2014-02-04T12:00:00+08:00'
F4_BING_BIRTH = '2014-02-14T12:00:00+08:00'
DING_YIN_BIRTH = '2025-02-07T12:00:00+08:00'  # 乙巳/戊寅/丁未/丙午


def run_birth(birth, **kwargs):
    chart = chart_from_datetime(birth)
    out = assess_strength(chart['pillars'], chart['day_master']['stem'],
                          **kwargs)
    pillars = [p['stem']['value'] + p['branch']['value']
               for p in chart['pillars']]
    return out, pillars


def yin_pilot_for(birth, window):
    w = F4_WINDOWS[window]
    facts = {'provider': dict(F4_PROVIDER),
             'lichun': dict(w['lichun']),
             'next_jie': dict(w['next_jie'])}
    return yin_siling_pilot(birth, version_id=F4_VERSION, jie_facts=facts)


def predicate_entry(out, predicate_id):
    for entry in out['classical']['predicates']:
        if entry['predicate_id'] == predicate_id:
            return entry
    raise AssertionError('missing predicate ' + predicate_id)


class F4PredicateTests(unittest.TestCase):
    def test_f4_predicate_registered(self):
        self.assertEqual(len(PREDICATES), 8)
        ids = [p['predicate_id'] for p in PREDICATES]
        self.assertEqual(ids[-1], 'changsheng_visible_support')
        spec = PREDICATES[-1]
        self.assertEqual(spec['name_cn'], '丙寅长生印月显纯生扶强')
        self.assertEqual(spec['classification'], 'strong')
        self.assertEqual(spec['sealed_validation'], 'pending')
        self.assertIsNone(spec['phase1_rule_id'])
        self.assertIsNone(spec['phase2_step_id'])
        self.assertEqual(spec['registration_status'],
                         'pending_phase1_rule_registration')
        self.assertEqual(spec['anchor_registration'],
                         'bazi_fire_si_yin_morphology.FORM_BING_YIN')
        self.assertTrue(spec['segment_gated'])
        self.assertEqual(spec['sealed_golden_ids'], [])
        self.assertIn(
            'tests/golden_tj0112_f34_si_yin.json'
            '#tj0112-f4-positive-both-readings',
            spec['public_golden_refs'])
        self.assertIn(
            'tests/golden_tj0112_bing_yin_changsheng.json'
            '#tj0112-bingyin-positive-jia-segment',
            spec['public_golden_refs'])
        self.assertEqual(spec['condition_keys'], [
            'fire_day_master_bing',
            'reviewed_generating_changsheng_month',
            'visible_positions_support_only',
            'visible_resource_present', 'visible_peer_present',
            'effective_heavy_day_roots',
            'all_visible_have_reviewed_roots',
            'no_unresolved_interactions',
            'hidden_layer_convention_applied'])

    def test_f4_positive_fires_with_jia_pilot(self):
        pilot = yin_pilot_for(F4_POSITIVE_BIRTH, '2034')
        self.assertEqual(pilot['status'], 'computed')
        self.assertEqual(pilot['segment']['stem'], '甲')
        out, pillars = run_birth(F4_POSITIVE_BIRTH,
                                 siling_yin_pilot=pilot)
        self.assertEqual(pillars, ['甲寅', '丙寅', '丙午', '甲午'])
        self.assertEqual(out['classical']['classification'], 'strong')
        matched = out['classical']['matched_predicate']
        self.assertEqual(matched['predicate_id'],
                         'changsheng_visible_support')
        self.assertEqual(matched['verification'], 'factor_level_only')
        self.assertTrue(all(matched['conditions'].values()))
        self.assertEqual(
            matched['conditions'],
            F4_CASES['tj0112-f4-positive-both-readings']
            ['expected_conditions'])
        gate = matched['segment_gate']
        self.assertEqual(gate['pilot_variant'],
                         'bazi-siling-yin-pilot-v1')
        self.assertEqual(gate['reading'], 'segment_tightened')
        self.assertEqual(gate['gate_outcome'], 'segment_jia')
        self.assertIs(gate['gate_passed'], True)
        self.assertEqual(gate['segment_stem'], '甲')
        self.assertEqual(gate['segment_index'], 3)
        self.assertEqual(gate['registered_interval'],
                         '[t0+14*24h, next_jie)')
        self.assertEqual(out['classical']['changsheng_segment_gate'],
                         gate)
        # Modern layer untouched by the wiring: still strong 87.
        self.assertEqual(out['modern']['verdict'], 'strong')
        self.assertEqual(out['modern']['score'], 87)
        self.assertEqual(out['agreement']['relationship'], 'agree')

    def test_f4_wu_segment_blocked(self):
        pilot = yin_pilot_for(F4_WU_BIRTH, '2014')
        self.assertEqual(pilot['status'], 'computed')
        self.assertEqual(pilot['segment']['stem'], '戊')
        out, pillars = run_birth(F4_WU_BIRTH, siling_yin_pilot=pilot)
        self.assertEqual(pillars, ['甲午', '丙寅', '丙午', '甲午'])
        entry = predicate_entry(out, 'changsheng_visible_support')
        self.assertTrue(all(entry['conditions'].values()))
        self.assertEqual(
            entry['conditions'],
            F4_CASES['tj0112-f4-gate-sensitivity-first-segment']
            ['expected_conditions'])
        self.assertFalse(entry['met'])
        self.assertEqual(entry['segment_gate']['gate_outcome'],
                         'segment_not_jia')
        self.assertIs(entry['segment_gate']['gate_passed'], False)
        self.assertEqual(out['classical']['classification'],
                         'indeterminate')
        self.assertIsNone(out['classical']['matched_predicate'])
        self.assertIn('changsheng_segment_gate_not_passed',
                      out['classical']['blockers'])

    def test_f4_bing_segment_blocked(self):
        pilot = yin_pilot_for(F4_BING_BIRTH, '2014')
        self.assertEqual(pilot['status'], 'computed')
        self.assertEqual(pilot['segment']['stem'], '丙')
        out, pillars = run_birth(F4_BING_BIRTH, siling_yin_pilot=pilot)
        self.assertEqual(pillars, ['甲午', '丙寅', '丙辰', '甲午'])
        entry = predicate_entry(out, 'changsheng_visible_support')
        self.assertTrue(all(entry['conditions'].values()))
        self.assertFalse(entry['met'])
        self.assertEqual(entry['segment_gate']['gate_outcome'],
                         'segment_not_jia')
        self.assertEqual(out['classical']['classification'],
                         'indeterminate')

    def test_f4_no_pilot_never_fires(self):
        # Fail-closed default: without an explicit pilot the factor
        # layer must not fire F4 even when all nine conditions hold.
        for birth in (F4_POSITIVE_BIRTH, F4_WU_BIRTH, F4_BING_BIRTH):
            out, _ = run_birth(birth)
            entry = predicate_entry(out, 'changsheng_visible_support')
            self.assertTrue(all(entry['conditions'].values()), birth)
            self.assertFalse(entry['met'], birth)
            self.assertEqual(entry['segment_gate']['gate_outcome'],
                             'pilot_claim_unverifiable', birth)
            self.assertIs(entry['segment_gate']['gate_passed'], False,
                          birth)
            self.assertEqual(out['classical']['classification'],
                             'indeterminate', birth)
            self.assertIsNone(out['classical']['matched_predicate'],
                              birth)

    def test_f4_forged_pilot_unverifiable(self):
        pilot = yin_pilot_for(F4_POSITIVE_BIRTH, '2034')
        forged = copy.deepcopy(pilot)
        forged['segment']['stem'] = '戊'
        forged['commander'] = '戊'
        out, _ = run_birth(F4_POSITIVE_BIRTH, siling_yin_pilot=forged)
        entry = predicate_entry(out, 'changsheng_visible_support')
        self.assertFalse(entry['met'])
        self.assertEqual(entry['segment_gate']['gate_outcome'],
                         'pilot_claim_unverifiable')
        forged = copy.deepcopy(pilot)
        forged['provenance']['calculation_convention'] = {
            'id': 'siling-calculation-convention', 'version': 'v9'}
        out, _ = run_birth(F4_POSITIVE_BIRTH, siling_yin_pilot=forged)
        entry = predicate_entry(out, 'changsheng_visible_support')
        self.assertFalse(entry['met'])
        self.assertEqual(entry['segment_gate']['gate_outcome'],
                         'pilot_claim_unverifiable')
        out, _ = run_birth(F4_POSITIVE_BIRTH, siling_yin_pilot=None)
        self.assertFalse(
            predicate_entry(out, 'changsheng_visible_support')['met'])

    def test_f4_noncomputed_and_wrong_version_pilots_block(self):
        # Birth before 立春 in the same window: pilot not_applicable.
        pre = yin_pilot_for('2034-02-03T12:00:00+08:00', '2034')
        self.assertEqual(pre['status'], 'not_applicable')
        out, _ = run_birth(F4_POSITIVE_BIRTH, siling_yin_pilot=pre)
        entry = predicate_entry(out, 'changsheng_visible_support')
        self.assertFalse(entry['met'])
        self.assertEqual(entry['segment_gate']['gate_outcome'],
                         'pilot_not_computed')
        # Wrong pilot version (T1): identity pins reject it.
        w = F4_WINDOWS['2034']
        facts = {'provider': dict(F4_PROVIDER),
                 'lichun': dict(w['lichun']),
                 'next_jie': dict(w['next_jie'])}
        t1 = yin_siling_pilot(F4_POSITIVE_BIRTH, version_id='sanming-t1',
                              jie_facts=facts)
        self.assertNotEqual(t1['status'], 'computed')
        out, _ = run_birth(F4_POSITIVE_BIRTH, siling_yin_pilot=t1)
        self.assertFalse(
            predicate_entry(out, 'changsheng_visible_support')['met'])

    def test_f4_segment_boundary_one_second_is_the_sole_gate(self):
        # (a) Pilot level: the segment switches exactly at t0+14d
        # (±1s), as the pilot module's own battery pins.
        t0 = datetime.fromisoformat(
            F4_WINDOWS['2034']['lichun']['at'])
        before = (t0 + timedelta(days=14, seconds=-1))
        at = t0 + timedelta(days=14)
        pilot_before = yin_pilot_for(before.isoformat(), '2034')
        pilot_at = yin_pilot_for(at.isoformat(), '2034')
        self.assertEqual(pilot_before['segment']['stem'], '丙')
        self.assertEqual(pilot_at['segment']['stem'], '甲')
        # (b) Factor level: the segment is the SOLE gate. Same birth
        # (same pillars, nine conditions all true), two consistent
        # claims differing only in the segment: the real 甲 claim
        # fires, a consistent 丙 claim (same shape, registered
        # interval of segment 2, commander 丙) validates but blocks.
        # The claim dict is hand-built at factor level, mirroring the
        # adjudication's test_segment_is_the_sole_gate_factor_level;
        # real-claim behaviour is covered by the pilot-driven tests.
        pilot = yin_pilot_for(F4_POSITIVE_BIRTH, '2034')
        out, _ = run_birth(F4_POSITIVE_BIRTH, siling_yin_pilot=pilot)
        entry = predicate_entry(out, 'changsheng_visible_support')
        self.assertTrue(all(entry['conditions'].values()))
        self.assertTrue(entry['met'])
        bing_claim = copy.deepcopy(pilot)
        bing_claim['commander'] = '丙'
        bing_claim['segment'] = dict(bing_claim['segment'])
        bing_claim['segment']['stem'] = '丙'
        bing_claim['segment']['index'] = 2
        bing_claim['segment']['registered_interval'] = \
            '[t0+7*24h, t0+14*24h)'
        out2, pillars2 = run_birth(F4_POSITIVE_BIRTH,
                                   siling_yin_pilot=bing_claim)
        entry2 = predicate_entry(out2, 'changsheng_visible_support')
        self.assertEqual(pillars2, ['甲寅', '丙寅', '丙午', '甲午'])
        self.assertEqual(entry2['conditions'], entry['conditions'])
        self.assertTrue(all(entry2['conditions'].values()))
        self.assertFalse(entry2['met'])
        self.assertEqual(entry2['segment_gate']['gate_outcome'],
                         'segment_not_jia')
        self.assertIs(entry2['segment_gate']['claim_verifiable'], True)
        self.assertEqual(out2['classical']['classification'],
                         'indeterminate')

    def test_f4_ding_never_applies(self):
        # Real 丁×寅 birth: the day-master condition alone excludes it.
        out, pillars = run_birth(DING_YIN_BIRTH)
        self.assertEqual(pillars, ['乙巳', '戊寅', '丁未', '丙午'])
        entry = predicate_entry(out, 'changsheng_visible_support')
        self.assertIs(entry['conditions']['fire_day_master_bing'],
                      False)
        self.assertFalse(entry['met'])
        self.assertEqual(out['classical']['classification'],
                         'indeterminate')

    def test_f4_evidence_chain_carries_pending_registration(self):
        pilot = yin_pilot_for(F4_POSITIVE_BIRTH, '2034')
        out, _ = run_birth(F4_POSITIVE_BIRTH, siling_yin_pilot=pilot)
        chain = [e for e in out['evidence_chain']
                 if e.get('predicate_id') == 'changsheng_visible_support']
        self.assertEqual(len(chain), 1)
        self.assertIsNone(chain[0]['phase1_rule_id'])
        self.assertIsNone(chain[0]['phase2_step_id'])
        self.assertEqual(chain[0]['sealed_golden_ids'], [])
        self.assertEqual(chain[0]['predicate_rule_registration'],
                         'pending_phase1_rule_registration')
        self.assertTrue(chain[0]['public_golden_refs'])
        self.assertTrue(chain[0]['met'])


class UnregisteredFormsTests(unittest.TestCase):
    def test_blocked_fire_forms_stay_unregistered(self):
        ids = [p['predicate_id'] for p in PREDICATES]
        for form_id in ('F2', 'F5', 'F6', 'F7'):
            self.assertNotIn(form_id, ids)
        by_id = {f['form_id']: f for f in UNREGISTERED_CLASSICAL_FORMS}
        self.assertEqual(set(by_id), {'F2', 'F5', 'F6', 'F7'})
        self.assertEqual(by_id['F2']['status'], 'blocked_by_conflict')
        self.assertEqual(by_id['F2']['conflict_id'],
                         'sanming-juan2.ding-changsheng')
        self.assertEqual(by_id['F5']['status'], 'not_buildable')
        self.assertEqual(by_id['F6']['status'],
                         'not_buildable_no_definition')
        self.assertEqual(by_id['F7']['status'], 'not_standalone')
        for form in UNREGISTERED_CLASSICAL_FORMS:
            self.assertIsNone(form['predicate_id'])
            self.assertTrue(form['register_ref'])
            self.assertTrue(form['blocking_reason'])


class ChangshengTableTests(unittest.TestCase):
    def test_table_covers_ten_stems_with_statuses(self):
        table = changsheng_reg.CHANGSHENG_TABLE
        self.assertEqual(set(table), set(STEMS))
        settled = {s: c['changsheng_branch'] for s, c in table.items()
                   if c['status'] == 'settled'}
        self.assertEqual(settled, {'丙': '寅', '庚': '巳', '壬': '申'})
        for stem, branch in settled.items():
            self.assertTrue(table[stem]['anchors'], stem)
            self.assertTrue(table[stem]['register_ref'], stem)
        conflicts = {s: c for s, c in table.items()
                     if c['status'] == 'conflict'}
        self.assertEqual(
            {s: sorted(b['branch'] for b in c['branches'])
             for s, c in conflicts.items()},
            {'丁': ['寅', '酉'], '戊': ['寅', '申'], '己': ['申', '酉'],
             '辛': ['子', '巳'], '癸': ['卯', '申']})
        self.assertEqual(
            {s: c['conflict_id'] for s, c in conflicts.items()},
            {'丁': 'sanming-juan2.ding-changsheng',
             '戊': 'sanming-juan2.tu-changsheng',
             '己': 'sanming-juan2.tu-changsheng',
             '辛': 'sanming-juan2.xin-changsheng',
             '癸': 'sanming-juan2.gui-changsheng'})
        unregistered = [s for s, c in table.items()
                        if c['status'] == 'unregistered']
        self.assertEqual(sorted(unregistered), ['乙', '甲'])
        for stem in unregistered:
            self.assertTrue(table[stem]['gap'], stem)
            self.assertIsNone(table[stem]['changsheng_branch'], stem)

    def test_table_is_registration_only_no_computation(self):
        self.assertEqual(changsheng_reg.CHANGSHENG_TABLE_ID,
                         'bazi-changsheng-conflict-table-v1')
        self.assertTrue(changsheng_reg.CHANGSHENG_TABLE_RESEARCH_ONLY)
        self.assertIsNone(changsheng_reg.CHANGSHENG_TABLE_COMPUTATION)
        self.assertFalse(hasattr(changsheng_reg, 'changsheng_branch'))
        self.assertFalse(hasattr(changsheng_reg, 'lookup'))
        self.assertFalse(hasattr(changsheng_reg, 'changsheng_of'))
        result = changsheng_reg.validate_changsheng_table()
        self.assertTrue(result['valid'])
        self.assertEqual(result['checks']['stems_covered'], 10)
        # The engine source never references the table module: no
        # computation path can consume an unapproved table.
        engine_src = (ROOT / 'src' / 'tianji_kb'
                      / 'bazi_strength_engine.py').read_text('utf-8')
        self.assertNotIn('bazi_changsheng_table', engine_src)
        self.assertNotIn('CHANGSHENG_TABLE', engine_src)


class CalibrationCompletenessTests(unittest.TestCase):
    def test_tomb_month_de_ling_reports_unreviewed_principal(self):
        # Canonical first hidden stem per tomb branch (verified
        # against foundations()['hidden_stems'], not hand-assumed):
        # 辰→戊, 未→己, 戌→戊, 丑→己. Score stays 0 (provisional).
        cases = {
            '2024-07-15T12:00:00+08:00': ('未', '己', 0),
            '2024-10-15T12:00:00+08:00': ('戌', '戊', 8),
            '2025-01-15T12:00:00+08:00': ('丑', '己', 5),
        }
        for birth, (branch, principal, score) in cases.items():
            out, _ = run_birth(birth)
            self.assertEqual(out['modern']['verdict'], 'weak', birth)
            self.assertEqual(out['modern']['score'], score, birth)
            self.assertEqual(out['modern']['classification_status'],
                             'uncertain', birth)
            self.assertIsNone(out['modern']['definite_classification'],
                              birth)
            tomb = out['modern']['components']['de_ling'][
                'tomb_principal_qi']
            self.assertEqual(tomb, {
                'branch': branch,
                'canonical_first_hidden_stem': principal,
                'status': 'unreviewed',
                'note': '四库本气未审：得令分记 0 是缺失条件的暂定处理，'
                        '不代表已证明月令无作用。'}, birth)

    def test_ding_de_di_calibration_names_conflict(self):
        for birth, score in (('2025-09-15T12:00:00+08:00', 41),
                             ('2025-10-15T12:00:00+08:00', 39)):
            out, _ = run_birth(birth)
            self.assertEqual(out['modern']['verdict'], 'balanced', birth)
            self.assertEqual(out['modern']['score'], score, birth)
            self.assertEqual(out['modern']['classification_status'],
                             'provisional_incomplete', birth)
            self.assertIsNone(out['modern']['definite_classification'],
                              birth)
            cal = out['modern']['components']['de_di']['calibration']
            self.assertEqual(cal['heavy_root_set'], 'unreviewed')
            self.assertEqual(cal['counted'], 'other_roots_only')
            self.assertEqual(cal['conflict_id'],
                             'sanming-juan2.ding-changsheng')

    def test_earth_de_di_calibration_names_contract(self):
        for birth, score in (('2024-03-15T12:00:00+08:00', 20),
                             ('2025-11-15T12:00:00+08:00', 33)):
            out, _ = run_birth(birth)
            self.assertEqual(out['modern']['verdict'], 'balanced', birth)
            self.assertEqual(out['modern']['score'], score, birth)
            self.assertEqual(out['modern']['classification_status'],
                             'provisional_incomplete', birth)
            self.assertIsNone(out['modern']['definite_classification'],
                              birth)
            cal = out['modern']['components']['de_di']['calibration']
            self.assertEqual(cal['heavy_root_set'], 'unreviewed')
            self.assertEqual(cal['counted'], 'other_roots_only')
            self.assertEqual(
                cal['contract'],
                'bazi-earth-root-consumption-contract-v1')
            self.assertEqual(cal['eligible_visible_cells'],
                             ['戊×巳', '己×午'])
            self.assertEqual(cal['day_root_effectiveness'], 'unreviewed')

    def test_reviewed_heavy_sets_are_reported_not_unreviewed(self):
        out, _ = run_birth('1966-07-06T12:00:00+08:00')  # 丙×午
        cal = out['modern']['components']['de_di']['calibration']
        self.assertEqual(cal['heavy_root_set'], ['午', '寅', '巳'])
        self.assertEqual(cal['counted'], 'heavy_and_other')


class CongEstablishmentGapTests(unittest.TestCase):
    def test_establishment_rules_all_unregistered(self):
        by_kind = {g['kind']: g for g in CONG_ESTABLISHMENT_GAPS}
        self.assertEqual(set(by_kind), {
            'cong_qiang', 'cong_ruo', 'cong_cai', 'cong_sha', 'cong_er'})
        for kind, gap in by_kind.items():
            self.assertEqual(gap['status'], 'unregistered', kind)
            self.assertIsNone(gap['establishment_rule'], kind)
            self.assertTrue(gap['evidence_needed'], kind)
        self.assertEqual(by_kind['cong_sha']['screen'], 'absent')
        self.assertEqual(by_kind['cong_er']['screen'], 'absent')
        self.assertEqual(by_kind['cong_cai']['screen'], 'present')

    def test_screen_kinds_never_include_sha_or_er(self):
        matrix = coverage_matrix()
        for cell in matrix['cells']:
            pillars = default_coverage_template(
                cell['day_master'], cell['month_branch'])
            cong = identify_cong_candidates(pillars, cell['day_master'])
            for candidate in cong['candidates']:
                self.assertIn(candidate['kind'],
                              ('cong_qiang', 'cong_ruo', 'cong_cai'))
                self.assertEqual(candidate['establishment'], 'not_judged')
                self.assertIsNone(candidate['verdict'])
            self.assertEqual(
                sorted(g['kind'] for g in cong['establishment_gaps']),
                ['cong_cai', 'cong_er', 'cong_qiang', 'cong_ruo',
                 'cong_sha'])


class PunishmentTableTests(unittest.TestCase):
    def test_no_punishment_table_registered(self):
        self.assertEqual(punishment_reg.PUNISHMENT_TABLE_ID,
                         'bazi-branch-punishment-table-v1')
        self.assertEqual(punishment_reg.PUNISHMENT_TABLE_STATUS,
                         'unregistered')
        self.assertIsNone(punishment_reg.PUNISHMENT_TABLE)
        gaps = punishment_reg.PUNISHMENT_GAPS
        self.assertIn('earthly_branch_relations', gaps['canonical_table'])
        self.assertIn('bazi.concept.conflict_three_punishments',
                      gaps['registered_conflict'])
        self.assertTrue(gaps['evidence_needed'])

    def test_interactions_never_emit_punishment_records(self):
        for day_master in STEMS:
            for month_branch in BRANCHES:
                pillars = default_coverage_template(
                    day_master, month_branch)
                effects = interaction_conditions(pillars, day_master)
                kinds = [r['kind'] for r in effects['records']]
                self.assertNotIn('branch_punishment', kinds)
                self.assertNotIn('branch_three_punishments', kinds)
                self.assertEqual(effects['score_adjustment_total'], 0)


class ModernWeightsReadOnlyTests(unittest.TestCase):
    def test_weights_and_thresholds_fully_pinned(self):
        self.assertEqual(MODERN_WEIGHTS, {
            'de_ling': {
                'same_element': 30, 'generates_me': 20, 'i_generate': 5,
                'i_control': 0, 'controls_me': -15,
                'tomb_principal_unreviewed': 0,
                'range': [-15, 30]},
            'de_di': {
                'heavy_root_each': 15, 'heavy_root_max_count': 2,
                'other_root_each': 5, 'other_root_max_count': 2,
                'same_stem_root_bonus': 5, 'cap': 35, 'range': [0, 35]},
            'de_shi': {
                'visible_support_each': 10, 'cap': 30,
                'range': [0, 30]},
            'shengfu_hidden': {
                'hidden_support_each': 2, 'cap': 10,
                'range': [0, 10]},
            'kexiehao': {
                'opposing_each': -2, 'floor': -20,
                'range': [-20, 0]},
        })
        self.assertEqual(MODERN_THRESHOLDS, {
            'strong_at_least': 60, 'weak_at_most': 15,
            'balanced_between': (16, 59)})


class RegressionTests(unittest.TestCase):
    def test_f2_chart_unchanged(self):
        out, pillars = run_birth(F2_BIRTH)
        self.assertEqual(pillars, ['甲辰', '丙寅', '乙巳', '甲申'])
        self.assertEqual(out['classical']['classification'],
                         'indeterminate')
        self.assertIsNone(out['classical']['matched_predicate'])
        self.assertEqual(out['modern']['verdict'], 'strong')
        self.assertEqual(out['modern']['score'], 65)
        self.assertEqual(out['modern']['classification_status'],
                         'definite')
        self.assertEqual(out['modern']['definite_classification'],
                         'strong')
        self.assertEqual(out['agreement']['relationship'],
                         'classical_indeterminate')
        self.assertTrue(validate_assessment(out)['valid'])

    def test_coverage_matrix_counts_unchanged(self):
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

    def test_whole_golden_sweep_unchanged(self):
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
                if out['classical']['classification'] != want:
                    mismatches.append((case['id'], want,
                                       out['classical']['classification']))
        self.assertEqual(total, 51)
        self.assertEqual(mismatches, [])

    def test_every_cell_validates(self):
        from tianji_kb.bazi_siling_si_pilot import (
            _provider_jie_instant, si_siling_pilot)
        from tianji_kb.calendar_provider_guard import provider_identity
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
        pilot = si_siling_pilot('1927-05-12T12:00:00+08:00',
                                version_id='sanming-t1', jie_facts=facts)
        matrix = coverage_matrix(siling_si_pilot=pilot)
        self.assertEqual(matrix['computed'], 118)
        self.assertEqual(matrix['abstained'], 2)
        for cell in matrix['cells']:
            if cell['status'] != 'computed':
                continue
            pillars = default_coverage_template(
                cell['day_master'], cell['month_branch'])
            out = assess_strength(pillars, cell['day_master'],
                                  siling_si_pilot=pilot)
            self.assertTrue(validate_assessment(out)['valid'], cell)


if __name__ == '__main__':
    unittest.main()
