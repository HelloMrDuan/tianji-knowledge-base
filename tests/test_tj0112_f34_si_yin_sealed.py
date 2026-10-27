"""TJ-011.2 F3/F4 adjudication register: sealed verification.

Runs in the offline assembled acceptance only (NOT public CI, same
partition rule as the earlier batches). Pins:

- snapshot integrity for the two source books the register pins
  (sha256 + char counts in F34_ADJUDICATION_REGISTER);
- every cross-register quote reference in
  bazi_fire_si_yin_morphology.QUOTE_REFERENCES resolves to a real
  registered quote in its home register, and the home register's
  slice re-verifies byte-for-byte against the sealed snapshot
  (quote text occurs exactly once);
- the seven Golden designs replay EXACTLY through the production
  calendar chain (engine.execute) from their real birth datetimes -
  no pillar is hand-assembled;
- the executed verdicts match the flipped Golden expectations: the
  F3 implementation batch (E0248) landed the lu_visible_support
  predicate, so the F3 scan-witness positive classifies 'strong'
  through it (bounded exit, pending registration) and the other four
  F3 charts stay 'indeterminate' with executed lu condition tables
  identical to the design tables; F4 remains unimplemented (its
  changsheng scope key exists nowhere in the executed output) pending
  the siling expansion adjudication;
- regression spot-checks: the F1 positive (Bing x Wu) still fires
  commanding_visible_support -> strong, and the S2 witness (Gui x
  Zi) still fires pure_generating_support_water -> strong;
- the sealed policy is untouched (pure/isolated months and reviewed
  root branches byte-identical; still no earth or fire set - the
  standing earth-root gap the register audits against).
"""
import hashlib
import json
from pathlib import Path
import unittest

from tianji_kb import bazi_fire_morphology as f1
from tianji_kb import bazi_fire_si_yin_morphology as f34
from tianji_kb import bazi_sanming_juan2_collation as c18
from tianji_kb import bazi_siling_matrix as siling
from tianji_kb.bazi_adjudication import ADJUDICATION_VARIANT
from tianji_kb.engine import execute
from tianji_kb.resolver import EvidenceResolver

ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT_DIR = (ROOT / 'data' / 'quarantine' / 'public_domain_snapshots'
                / 'daizhigev20')
GOLDEN = json.loads(
    (ROOT / 'tests' / 'golden_tj0112_f34_si_yin.json')
    .read_text('utf-8'))
CASES = {c['id']: c for c in GOLDEN['cases']}
BING = {c['id']: c for c in json.loads(
    (ROOT / 'tests' / 'golden_tj0112_bing_wu_commanding.json')
    .read_text('utf-8'))['cases']}
S2G = {c['id']: c for c in json.loads(
    (ROOT / 'tests' / 'golden_tj0112_s2_metal_water.json')
    .read_text('utf-8'))['cases']}

SOURCE_FILE = {
    'bazi.source.sanmingtonghui': 'sanming_tonghui.txt',
    'bazi.source.shenfeng': 'shenfeng_tongkao.txt',
    'bazi.source.yuanhai': 'yuanhai_ziping.txt',
    'bazi.source.ditiansui-spouse': 'ditiansui_chanwei.txt',
}
REGISTER_QUOTES = {
    'bazi_fire_morphology': {q['id']: q for q in f1.MORPHOLOGY_QUOTES},
    'bazi_sanming_juan2_collation': {q['id']: q
                                     for q in c18.COLLATION_QUOTES},
    'bazi_siling_matrix': {q['id']: q for q in siling.SILING_QUOTES},
}


def _text(filename):
    return (SNAPSHOT_DIR / filename).read_bytes().decode('utf-8')


def run_birth(birth):
    out = execute('bazi', {'value': birth,
                           'strength_variant': ADJUDICATION_VARIANT},
                  allow_research=True)
    result = out['result']
    pillars = [p['stem']['value'] + p['branch']['value']
               for p in result['pillars']]
    return result, pillars


class SnapshotIntegrityTests(unittest.TestCase):
    def test_pinned_snapshots_match(self):
        snap = f34.F34_ADJUDICATION_REGISTER['source_snapshot']
        raw = (SNAPSHOT_DIR / 'ditiansui_chanwei.txt').read_bytes()
        self.assertEqual(hashlib.sha256(raw).hexdigest(),
                         snap['ditiansui_sha256'])
        self.assertEqual(len(raw.decode('utf-8')),
                         snap['ditiansui_chars'])
        raw = (SNAPSHOT_DIR / 'sanming_tonghui.txt').read_bytes()
        self.assertEqual(hashlib.sha256(raw).hexdigest(),
                         snap['sanming_sha256'])
        self.assertEqual(len(raw.decode('utf-8')),
                         snap['sanming_chars'])


class QuoteReferenceResolutionTests(unittest.TestCase):
    def test_every_reference_resolves_and_reverifies(self):
        texts = {}
        resolved = 0
        for ref, entry in f34.QUOTE_REFERENCES.items():
            register = entry['register']
            self.assertIn(register, REGISTER_QUOTES, ref)
            quotes = REGISTER_QUOTES[register]
            self.assertIn(ref, quotes,
                          f'{ref} not registered in {register}')
            quote = quotes[ref]
            filename = SOURCE_FILE[quote['source_id']]
            if filename not in texts:
                texts[filename] = _text(filename)
            text = texts[filename]
            loc = quote['locator']
            self.assertEqual(text[loc['char_start']:loc['char_end']],
                             quote['quote'], ref)
            self.assertEqual(text.count(quote['quote']), 1, ref)
            resolved += 1
        # Every registered reference resolved (13 at this batch).
        self.assertEqual(resolved, len(f34.QUOTE_REFERENCES))
        self.assertEqual(resolved, 13)

    def test_lu_and_changsheng_positions_are_per_stem_listed(self):
        quotes = REGISTER_QUOTES['bazi_sanming_juan2_collation']
        self.assertIn('巳', quotes['sm2.bing_lu']['quote'])
        self.assertIn('寅', quotes['sm2.bing_sheng']['quote'])
        self.assertIn('寅', quotes['sm2.renyuan_bing']['quote'])
        siling_quotes = REGISTER_QUOTES['bazi_siling_matrix']
        self.assertIn('戊土用事',
                      siling_quotes['dt.s024_yinyue']['quote'])


class GoldenReplayTests(unittest.TestCase):
    def test_seven_cases_replay_exactly(self):
        self.assertEqual(len(CASES), 7)
        for case in CASES.values():
            _, pillars = run_birth(case['source_birth'])
            self.assertEqual(pillars, case['expected_pillars'],
                             case['id'])

    def test_f3_implemented_f4_still_gated(self):
        # Updated by the F3 implementation batch (E0248): the F3
        # lu_visible_support predicate is implemented, so the design
        # witness earns its strong verdict and the executed F3
        # condition tables equal the design tables verbatim; the
        # other F3 charts stay indeterminate for their registered
        # reasons. F4 is still NOT implemented: no changsheng scope
        # key exists in the executed output and both F4 charts stay
        # indeterminate until the siling expansion adjudication.
        for case in CASES.values():
            result, _ = run_birth(case['source_birth'])
            assessment = result['strength_assessment']
            effects = result['action_effects']
            self.assertEqual(assessment['classification'],
                             case['expect']['current_engine'],
                             case['id'])
            for key in effects:
                self.assertNotIn('changsheng_visible_support', key,
                                 case['id'])
            if case['form'] == 'F4':
                self.assertEqual(assessment['classification'],
                                 'indeterminate', case['id'])
                self.assertIsNone(
                    assessment['why_not_indeterminate'], case['id'])
                continue
            self.assertEqual(
                effects['lu_visible_support_scope_conditions'],
                case['expected_conditions'], case['id'])
            if case['id'] == 'tj0112-f3-positive-scan-witness':
                why = assessment['why_not_indeterminate']
                self.assertIsNotNone(why, case['id'])
                self.assertEqual(why['sufficient_predicate'],
                                 'lu_visible_support', case['id'])
                self.assertIsNone(why['sufficient_rule'], case['id'])
                self.assertEqual(why['predicate_rule_registration'],
                                 'pending_phase1_rule_registration',
                                 case['id'])
            else:
                self.assertEqual(assessment['classification'],
                                 'indeterminate', case['id'])
                self.assertIsNone(
                    assessment['why_not_indeterminate'], case['id'])
            if case['category'] == 'abstain_unknown':
                self.assertIn(
                    'interaction_effect_unresolved',
                    {b['reason'] for b in assessment['blockers']},
                    case['id'])
            if case['category'] == 'conflict_registered':
                checks = {c['conflict_id']: c
                          for c in assessment['conflict_checks']}
                self.assertIn(
                    'bazi.concept.conflict_root_type_readings',
                    checks, case['id'])
                self.assertTrue(
                    checks['bazi.concept.conflict_root_type_readings']
                    ['blocking'], case['id'])


class RegressionSpotCheckTests(unittest.TestCase):
    def test_f1_positive_still_strong(self):
        # F1 Golden positive (Bing Wu / Jia Wu / Bing Yin / Jia Wu)
        # fires commanding_visible_support.
        case = BING['tj0112-bingwu-positive']
        result, pillars = run_birth(case['source_birth'])
        self.assertEqual(pillars, case['expected_pillars'])
        assessment = result['strength_assessment']
        self.assertEqual(assessment['classification'], 'strong')
        # S5 (E0254): commanding is registered; the verdict binds
        # via the registered Phase2 rule, no predicate alias remains.
        self.assertEqual(
            assessment['why_not_indeterminate']['sufficient_rule'],
            'bazi.phase2.strength_commanding_visible_support')
        self.assertNotIn(
            'sufficient_predicate',
            assessment['why_not_indeterminate'])

    def test_s2_witness_still_strong(self):
        # S2 Golden witness (Xin You / Geng Zi / Gui You / Ren Zi)
        # fires pure_generating_support_water.
        case = S2G['tj0112-s2-water-positive-gui']
        result, pillars = run_birth(case['source_birth'])
        self.assertEqual(pillars, case['expected_pillars'])
        assessment = result['strength_assessment']
        self.assertEqual(assessment['classification'], 'strong')
        self.assertEqual(
            assessment['why_not_indeterminate']['sufficient_predicate'],
            'pure_generating_support_water')


class SealedPolicyUntouchedTests(unittest.TestCase):
    def test_policy_zero_change(self):
        policy = EvidenceResolver().entities[
            'bazi.concept.action_effects_v1'][1]['attributes']
        self.assertEqual(policy['pure_months'], ['卯'])
        self.assertEqual(policy['isolated_months'], ['酉'])
        self.assertEqual(policy['reviewed_root_branches'],
                         {'木': ['亥', '寅', '卯'], '水': ['亥', '子'],
                          '金': ['酉']})
        self.assertNotIn('土', policy['reviewed_root_branches'])
        self.assertNotIn('火', policy['reviewed_root_branches'])


if __name__ == '__main__':
    unittest.main()
