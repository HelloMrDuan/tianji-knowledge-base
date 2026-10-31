"""TJ-011.2 S5 registration governance: public-side consistency pins.

Public CI (no sealed snapshot needed). The sealed-side registration
itself is verified in the assembled acceptance by
tests/test_phase2_baziregistration.py; this suite pins that the
public governance register (bazi_registration_governance) and the
live code disclosures agree:

- every source file that still emits a
  'pending_phase1_rule_registration' disclosure is covered by the
  register's inventory (no undisclosed pending item, no stale site);
- the two flipped predicates are wired to their registered rule IDs
  (readable-layer mapping + adjudication limitations text + the F1
  morphology register's evidence_binding);
- the still-pending predicates keep their pending disclosure in the
  adjudication source (registration was not silently extended);
- the conflict-presentation limitations text states the current
  seven-predicate surface (the stale "3 predicates" wording is gone);
- the S5 registration record is internally consistent.
"""
import re
import unittest
from pathlib import Path

from tianji_kb import bazi_registration_governance as gov
from tianji_kb.bazi_fire_morphology import FORM_BING_WU
from tianji_kb.bazi_xiyong_readable import RULE_TO_PREDICATE

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / 'src' / 'tianji_kb'
PENDING = 'pending_phase1_rule_registration'


def _site_files():
    files = set()
    for row in gov.REGISTRATION_INVENTORY:
        for site in row['disclosure_sites']:
            files.add(Path(site).name)
    return files


class InventoryCoverageTests(unittest.TestCase):
    def test_every_pending_disclosure_file_is_inventoried(self):
        covered = _site_files()
        for path in sorted(SRC.glob('*.py')):
            if path.name == 'bazi_registration_governance.py':
                continue
            if PENDING in path.read_text('utf-8'):
                self.assertIn(path.name, covered,
                              f'{path.name} discloses pending registration '
                              'but is missing from the S5 inventory')

    def test_dispositions_are_well_formed(self):
        for row in gov.REGISTRATION_INVENTORY:
            self.assertIn(row['disposition'],
                          ('registered', 'maintained_pending',
                           'not_a_candidate'), row['item'])
            self.assertTrue(row['reason'], row['item'])
            if row['disposition'] == 'registered':
                self.assertTrue(row['phase1_rule_id'], row['item'])
                self.assertTrue(row['phase2_rule_id'], row['item'])
            if row['disposition'] == 'maintained_pending':
                self.assertIn(row['reason_class'], gov.REASON_CLASSES,
                              row['item'])
                self.assertTrue(row['unlock_path'], row['item'])

    def test_flipped_and_maintained_sets(self):
        # E0333 (TJ-018.3 execution-binding batch 1): the sanxing
        # fact-layer slice flipped to registered (r031 + the
        # gated fact step), leaving the flipped set at three and
        # the maintained-pending inventory at twelve.
        # E0335 (TJ-018.3 batch 2): the three ganzhi strength
        # predicates (lu / metal / water) flipped to registered
        # (r032/r033/r034 + their own steps), leaving the flipped
        # set at six and the maintained-pending inventory at nine.
        # E0339 (TJ-018.3 B-2): pattern-route-luren flipped as well
        # (r035 + bazi.phase2.pattern_route), leaving the flipped
        # set at seven and the maintained-pending inventory at eight.
        # E0342 (governance zaqi promotion): pattern-zaqi flipped
        # (r036 + bazi.phase2.pattern_zaqi), leaving the flipped set
        # at eight and the maintained-pending inventory at seven.
        # E0344 (governance ren promotion): ren-pattern-yin-true-v1
        # flipped (r037 + bazi.phase2.ren_yin_true_pattern),
        # leaving the flipped set at nine and the maintained-pending
        # inventory at six.
        # E0346 (governance dayun Sanming-segment promotion):
        # dayun-classical-variants flipped segmented (r038 + r039 /
        # dayun_classical_direction + dayun_sanming_conversion;
        # the Shenfeng segment stays pending inside the row),
        # leaving the flipped set at ten and the maintained-pending
        # inventory at five.
        # E0348 (governance Shenfeng Canonical expansion):
        # bingyao-shenfeng-v1 flipped (r040 /
        # bazi.phase2.bingyao_assessment) and the dayun row's
        # Shenfeng segment flipped inside the already-registered
        # row (additional ids r041 /
        # bazi.phase2.dayun_shenfeng_conversion), leaving the
        # flipped set at eleven and the maintained-pending
        # inventory at four (the two inherited rows remain in
        # terminal inherited form).
        # E0352 (governance tiaohou Canonical construction):
        # tiaohou-qiongtong-v1 flipped (r042 + additional
        # r043-r051 / bazi.phase2.tiaohou_assessment), leaving the
        # flipped set at twelve and the maintained-pending
        # inventory at three (siling-yin-pilot and the two
        # inherited dayun rows).
        self.assertEqual(sorted(gov.FLIPPED_ITEMS),
                         ['bingyao-shenfeng-v1',
                          'commanding_visible_support',
                          'dayun-classical-variants',
                          'lu_visible_support',
                          'pattern-route-luren',
                          'pattern-zaqi',
                          'pure_generating_support',
                          'pure_generating_support_water',
                          'pure_support_metal',
                          'ren-pattern-yin-true-v1',
                          'sanxing-branch-fact-v1',
                          'tiaohou-qiongtong-v1'])
        self.assertEqual(len(gov.MAINTAINED_ITEMS), 3)


class FuyiRegisterStaysUnwiredTests(unittest.TestCase):
    def test_no_module_imports_the_fuyi_slice_register(self):
        # The S4 discipline (zero runtime wiring of the unbuilt fuyi
        # slice) is preserved: the governance register names the file
        # as data, but nothing may import the module.
        for path in sorted(SRC.glob('*.py')):
            if path.name == 'bazi_fuyi_slice_adjudication.py':
                continue
            for line in path.read_text('utf-8').splitlines():
                stripped = line.strip()
                if stripped.startswith(('import ', 'from ')):
                    self.assertNotIn('bazi_fuyi_slice_adjudication',
                                     stripped, path.name)


class FlippedWiringTests(unittest.TestCase):
    def test_readable_layer_maps_registered_rules(self):
        self.assertEqual(
            RULE_TO_PREDICATE[
                'bazi.phase2.strength_pure_generating_support'],
            'pure_generating_support')
        self.assertEqual(
            RULE_TO_PREDICATE[
                'bazi.phase2.strength_commanding_visible_support'],
            'commanding_visible_support')

    def test_f1_register_binding_is_registered(self):
        self.assertTrue(
            FORM_BING_WU['evidence_binding'].startswith(
                'registered_phase1_phase2'))
        self.assertIn('bazi.rule.r030', FORM_BING_WU['evidence_binding'])

    def test_adjudication_limitations_name_registered_rules(self):
        text = (SRC / 'bazi_adjudication.py').read_text('utf-8')
        self.assertIn('bazi.rule.r029', text)
        self.assertIn('bazi.rule.r030', text)
        self.assertNotIn('亥月分支谓词尚待密封', text)
        self.assertNotIn('午月丙日主分支谓词尚待密封', text)
        # E0335 (TJ-018.3 batch 2): lu / metal / water limitations
        # now name their registered rules; no pending sentence for
        # the three predicates remains.
        self.assertIn('bazi.rule.r032', text)
        self.assertIn('bazi.rule.r033', text)
        self.assertIn('bazi.rule.r034', text)
        self.assertNotIn('巳月丙日主分支谓词尚待密封', text)
        self.assertNotIn('酉月金日主与子月水日主分支谓词尚待密封', text)

    def test_pending_predicates_keep_pending_disclosure(self):
        text = (SRC / 'bazi_adjudication.py').read_text('utf-8')
        # Since TJ-018.3 batch 2 (E0335) registered lu / metal /
        # water, only the changsheng verdict shape (F4, E0262)
        # still discloses a pending registration in the adjudication
        # source (one 'predicate_rule_registration' site), plus one
        # further quoted occurrence: the F4 combination's
        # pilot-claim binding check, which requires the Slice C
        # pilot block itself to carry the pending binding.
        self.assertEqual(
            text.count(f"'predicate_rule_registration':'{PENDING}'"), 1)
        self.assertEqual(text.count(f"'{PENDING}'"), 2)
        # E0348 (governance Shenfeng Canonical expansion):
        # bingyao-shenfeng-v1 and the dayun Shenfeng segment are
        # registered, so bazi_bingyao.py no longer carries the
        # pending disclosure anywhere and leaves this site list;
        # bazi_dayun_classical.py keeps one historical occurrence
        # in its TJ-017.1 docstring layer (superseded in place by
        # the E0346/E0348 paragraphs) and stays listed.
        # E0352 (governance tiaohou Canonical construction):
        # tiaohou-qiongtong-v1 is registered, so bazi_tiaohou.py
        # no longer carries the pending disclosure anywhere and
        # leaves this site list (same migration form as E0348).
        for site in ('bazi_dayun_classical.py', 'bazi_pattern.py',
                     'bazi_siling_pilot.py',
                     'bazi_fire_si_yin_morphology.py'):
            self.assertIn(PENDING, (SRC / site).read_text('utf-8'), site)


class PresentationTextTests(unittest.TestCase):
    def test_conflict_presentation_limitations_current(self):
        text = (SRC / 'bazi_conflict_presentation.py').read_text('utf-8')
        # E0262: the F4 changsheng predicate takes the count to 8
        # (segment-gated, combination-path only; the presentation
        # layer's bounded surface still abstains on its charts).
        self.assertIn('8 条已审充分谓词', text)
        self.assertNotIn('仅 3 条木日主充分谓词', text)


class RecordConsistencyTests(unittest.TestCase):
    def test_record_matches_flipped_items(self):
        # Batch transition (E0333): at S5 the S5 record was the
        # only registration record, so it alone matched the flipped
        # inventory. The sanxing execution-binding batch added its
        # own record (TJ0183_EXECBIND_RECORD; the P1 record added
        # no rules), and batch 2 (E0335) added TJ0183_P2_RECORD,
        # so the invariant is now over the union of all batch
        # records -- still an exact equality, no slack.
        # B-2 (E0339) added TJ0183_B2_RECORD (r035 / pattern_route).
        # E0342 added GOVERNANCE_ZAQI_RECORD (r036 / pattern_zaqi).
        # E0344 added GOVERNANCE_REN_RECORD (r037 /
        # ren_yin_true_pattern).
        # E0346 added GOVERNANCE_DAYUN_SANMING_RECORD (r038 + r039 /
        # dayun_classical_direction + dayun_sanming_conversion):
        # the dayun-classical-variants row is a segmented
        # registration carrying a primary rule/step pair plus
        # additional_* pairs, so the collection below unions the
        # additional ids in -- a structural extension of the
        # collection expression; the exact-equality invariant is
        # unchanged.
        # E0348 added GOVERNANCE_SHENFENG_RECORD (r040 + r041 /
        # bingyao_assessment + dayun_shenfeng_conversion): r040 is
        # carried by the newly flipped bingyao row, r041 joins the
        # dayun row's additional ids.
        # E0352 added GOVERNANCE_TIAOHOU_RECORD (r042 + additional
        # r043-r051 / tiaohou_assessment): the tiaohou row carries
        # a primary rule plus nine additional ids, unioned by the
        # same collection expression; the exact-equality
        # invariant is unchanged.
        records = [gov.S5_REGISTRATION_RECORD,
                   gov.TJ0183_P1_RECORD,
                   gov.TJ0183_EXECBIND_RECORD,
                   gov.TJ0183_P2_RECORD,
                   gov.TJ0183_B2_RECORD,
                   gov.GOVERNANCE_ZAQI_RECORD,
                   gov.GOVERNANCE_REN_RECORD,
                   gov.GOVERNANCE_DAYUN_SANMING_RECORD,
                   gov.GOVERNANCE_SHENFENG_RECORD,
                   gov.GOVERNANCE_TIAOHOU_RECORD]
        flipped_phase1 = sorted(
            rule_id for row in gov.REGISTRATION_INVENTORY
            if row['disposition'] == 'registered'
            for rule_id in
            [row['phase1_rule_id'],
             *row.get('additional_phase1_rule_ids', [])])
        flipped_phase2 = sorted(
            rule_id for row in gov.REGISTRATION_INVENTORY
            if row['disposition'] == 'registered'
            for rule_id in
            [row['phase2_rule_id'],
             *row.get('additional_phase2_rule_ids', [])])
        self.assertEqual(
            sorted(r for record in records
                   for r in record['phase1_rules_added']),
            flipped_phase1)
        self.assertEqual(
            sorted(r for record in records
                   for r in record['phase2_rules_added']),
            flipped_phase2)

    def test_manifest_pins(self):
        record = gov.S5_REGISTRATION_RECORD
        for key in ('manifest_sha256_before', 'manifest_sha256_after'):
            self.assertTrue(
                re.fullmatch(r'[0-9a-f]{64}', record[key]), key)
        self.assertNotEqual(record['manifest_sha256_before'],
                            record['manifest_sha256_after'])
        self.assertEqual(record['snapshot_files_before'],
                         record['snapshot_files_after'])
        self.assertGreater(record['snapshot_bytes_after'],
                           record['snapshot_bytes_before'])
        for digest in record['sealed_file_sha256_after'].values():
            self.assertTrue(re.fullmatch(r'[0-9a-f]{64}', digest))


if __name__ == '__main__':
    unittest.main()
