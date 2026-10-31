"""E0346 stage 1 (sealed): snapshot-byte verification of the
《论大运》 collation register against the real S0/S3 texts.

Every registered quote must reproduce at its S0 locator, its S3
text form must reproduce at the S3 locator (shift −1) and be
contained in the planned Canonical window; the section windows
must show the registered PUA/防/□ counts on both baselines; every
collation note must pin to the snapshot glyph at its offset and,
where a reading was applied, to the applied glyph in S3.
"""
import hashlib
import unittest
from pathlib import Path

from tianji_kb import bazi_sanming_juan2_dayun_collation as reg

ROOT = Path(__file__).resolve().parents[1]
SNAP_DIR = (ROOT / 'data' / 'quarantine' / 'public_domain_snapshots'
            / 'daizhigev20')
RAW0 = (SNAP_DIR / 'sanming_tonghui.txt').read_bytes()
RAW3 = (SNAP_DIR / 'sanming_tonghui_applied_v1.txt').read_bytes()
S0 = RAW0.decode('utf-8')
S3 = RAW3.decode('utf-8')

PUA_ED92 = chr(0xED92)
PUA_EA20 = chr(0xEA20)

WINDOWS_S3 = {
    'bazi.section.s068': S3[58456:59197],
    'bazi.section.s069': S3[396897:397158],
    'bazi.section.s070': S3[408770:408794],
}


class SnapshotIdentityTest(unittest.TestCase):
    def test_s0_s3_pins(self) -> None:
        self.assertEqual(hashlib.sha256(RAW0).hexdigest(),
                         reg.COLLATION_SNAPSHOTS[
                             'sanming_tonghui.txt']['sha256'])
        self.assertEqual(hashlib.sha256(RAW3).hexdigest(),
                         reg.COLLATION_SNAPSHOTS[
                             'sanming_tonghui_applied_v1.txt']['sha256'])
        self.assertEqual(len(S0), 461157)
        self.assertEqual(len(S3), 461156)


class SectionWindowTest(unittest.TestCase):
    def test_lun_dayun_window_counts(self) -> None:
        s0 = S0[58457:59198]
        s3 = S3[58456:59197]
        self.assertEqual(len(s0), 741)
        self.assertEqual(len(s3), 741)
        self.assertTrue(s0.startswith('论大运'))
        self.assertTrue(s3.startswith('论大运'))
        self.assertEqual(s0.count(PUA_ED92), 3)
        self.assertEqual(s0.count(PUA_EA20), 0)
        self.assertNotIn('□', s0)
        self.assertNotIn('□', s3)
        for ch in s3:
            self.assertFalse(0xE000 <= ord(ch) <= 0xF8FF,
                             'PUA in S3 window: %r' % ch)
        # The single residual 防 survives into S3 at the aligned
        # position S3 58541 (register note ldy-fang-58542).
        self.assertEqual(S0[58542], '防')
        self.assertEqual(S3[58541], '防')
        self.assertEqual(s3.count('防'), 1)

    def test_witness_window_counts(self) -> None:
        a0 = S0[396898:397159]
        a3 = S3[396897:397158]
        self.assertEqual(a0.count(PUA_EA20), 1)
        self.assertEqual(a0.count('防'), 2)
        self.assertEqual(a3.count('㑹'), 2)
        self.assertNotIn('防', a3)
        self.assertNotIn('□', a3)
        for ch in a3:
            self.assertFalse(0xE000 <= ord(ch) <= 0xF8FF)
        b0 = S0[408771:408795]
        b3 = S3[408770:408794]
        self.assertEqual(b0, b3)
        self.assertEqual(len(b3), 24)


class QuoteSliceTest(unittest.TestCase):
    def test_quotes_reproduce_on_both_baselines(self) -> None:
        for row in reg.COLLATION_QUOTES:
            loc = row['locator']
            self.assertEqual(
                S0[loc['char_start']:loc['char_end']], row['quote'],
                row['id'])
            s3loc = row['s3_locator']
            self.assertEqual(
                S3[s3loc['char_start']:s3loc['char_end']],
                row['s3_quote'], row['id'])
            self.assertIn(row['s3_quote'],
                          WINDOWS_S3[row['canonical_section_id']],
                          row['id'])


class NotePinTest(unittest.TestCase):
    def test_notes_pin_to_snapshot(self) -> None:
        for note in reg.COLLATION_NOTES:
            off = note['char_offset']
            glyph = note['snapshot_glyph']
            if glyph == 'PUA':
                expected = (PUA_ED92 if note['snapshot_codepoint']
                            == 'U+ED92' else PUA_EA20)
                self.assertEqual(S0[off], expected, note['id'])
            else:
                self.assertEqual(S0[off], glyph, note['id'])
            if note['disposition'] == 'corrected' \
                    and note['reading'] is not None:
                self.assertEqual(S3[off - 1], note['reading'],
                                 note['id'])
            if note['disposition'] == 'genuine':
                self.assertEqual(S3[off - 1], note['reading'],
                                 note['id'])

    def test_unresolved_fang_is_residual_in_s3(self) -> None:
        note = {n['id']: n for n in reg.COLLATION_NOTES}['ldy-fang-58542']
        self.assertEqual(S3[note['char_offset'] - 1], '防')


if __name__ == '__main__':
    unittest.main()
