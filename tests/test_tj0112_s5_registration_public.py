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
        self.assertEqual(sorted(gov.FLIPPED_ITEMS),
                         ['commanding_visible_support',
                          'pure_generating_support'])
        self.assertEqual(len(gov.MAINTAINED_ITEMS), 12)


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

    def test_pending_predicates_keep_pending_disclosure(self):
        text = (SRC / 'bazi_adjudication.py').read_text('utf-8')
        # Exactly the lu, S2 (metal/water) and - since the F4
        # implementation batch (E0262) - changsheng verdict shapes
        # still disclose a pending registration in the adjudication
        # source (three 'predicate_rule_registration' sites), plus
        # one further quoted occurrence: the F4 combination's
        # pilot-claim binding check, which requires the Slice C
        # pilot block itself to carry the pending binding.
        self.assertEqual(
            text.count(f"'predicate_rule_registration':'{PENDING}'"), 3)
        self.assertEqual(text.count(f"'{PENDING}'"), 4)
        for site in ('bazi_tiaohou.py', 'bazi_bingyao.py',
                     'bazi_dayun_classical.py', 'bazi_pattern.py',
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
        record = gov.S5_REGISTRATION_RECORD
        flipped_phase1 = sorted(
            row['phase1_rule_id'] for row in gov.REGISTRATION_INVENTORY
            if row['disposition'] == 'registered')
        flipped_phase2 = sorted(
            row['phase2_rule_id'] for row in gov.REGISTRATION_INVENTORY
            if row['disposition'] == 'registered')
        self.assertEqual(sorted(record['phase1_rules_added']),
                         flipped_phase1)
        self.assertEqual(sorted(record['phase2_rules_added']),
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
