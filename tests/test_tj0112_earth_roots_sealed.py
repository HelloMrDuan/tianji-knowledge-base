"""TJ-011.2 earth (Wu/Ji) root grading: sealed verification.

Runs in the offline assembled acceptance only (NOT public CI, same
partition rule as the earlier batches). Pins:

- snapshot integrity for the three source books the register pins
  (sha256 + bytes + char counts in EARTH_SNAPSHOTS);
- the six newly registered Sanming quotes verify byte-for-byte
  against the sealed snapshot (slice equality + full-text count == 1)
  and their locators agree with the TJ-018-A STEM_COVERAGE anchors
  for Wu/Ji;
- every cross-register quote reference used by the root tables and
  the Tu Changsheng conflict resolves to a real registered quote in
  its home register (TJ-018-A collation register, fire morphology
  register, Slice A pattern register) and re-verifies verbatim;
- the light-root gap claim itself: the Ditiansui root-listing segment
  (chars 39967-40119) contains no earth stem pair, and the snapshot
  full text has zero occurrences of the earth listing pattern;
- the sealed policy is untouched (reviewed root branches byte-sized
  identical, still no earth set - the standing registration gap this
  batch fills at register level only, without wiring).
"""

import hashlib
import unittest
from pathlib import Path

from tianji_kb import bazi_earth_roots as E
from tianji_kb import bazi_fire_morphology as F
from tianji_kb import bazi_pattern as P
from tianji_kb import bazi_sanming_juan2_collation as C18
from tianji_kb.resolver import EvidenceResolver

ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT_DIR = (ROOT / 'data' / 'quarantine' / 'public_domain_snapshots'
                / 'daizhigev20')

SOURCE_FILE = {
    'bazi.source.sanmingtonghui': 'sanming_tonghui.txt',
    'bazi.source.shenfeng': 'shenfeng_tongkao.txt',
    'bazi.source.ditiansui-spouse': 'ditiansui_chanwei.txt',
}
REGISTER_QUOTES = {
    'bazi_sanming_juan2_collation':
        {q['id']: q for q in C18.COLLATION_QUOTES},
    'bazi_fire_morphology':
        {q['id']: q for q in F.MORPHOLOGY_QUOTES},
    'bazi_pattern':
        {q['id']: q for q in P.LUREN_QUOTES},
}


def _text(filename):
    return (SNAPSHOT_DIR / filename).read_bytes().decode('utf-8')


class SnapshotIntegrityTests(unittest.TestCase):
    def test_snapshots_match_registry(self):
        for filename, meta in E.EARTH_SNAPSHOTS.items():
            raw = (SNAPSHOT_DIR / filename).read_bytes()
            self.assertEqual(len(raw), meta['bytes'], filename)
            self.assertEqual(hashlib.sha256(raw).hexdigest(),
                             meta['sha256'], filename)
            self.assertEqual(len(raw.decode('utf-8')), meta['chars'],
                             filename)


class EarthQuoteSliceTests(unittest.TestCase):
    def test_quotes_verbatim_and_unique(self):
        text = _text('sanming_tonghui.txt')
        self.assertEqual(len(E.EARTH_QUOTES), 6)
        for q in E.EARTH_QUOTES:
            loc = q['locator']
            self.assertEqual(text[loc['char_start']:loc['char_end']],
                             q['quote'], q['id'])
            self.assertEqual(text.count(q['quote']), 1, q['id'])

    def test_quote_locators_agree_with_018a_coverage(self):
        cov = {row['stem']: row for row in C18.STEM_COVERAGE}
        by_id = {q['id']: q for q in E.EARTH_QUOTES}
        pairs = [('sm.wu_lu', cov['戊']['lu']),
                 ('sm.wu_shengsi', cov['戊']['si']),
                 ('sm.ji_lu', cov['己']['lu']),
                 ('sm.ji_shengsi', cov['己']['si'])]
        for qid, anchor in pairs:
            self.assertEqual(by_id[qid]['locator']['char_start'],
                             anchor['locator']['char_start'], qid)

    def test_wu_lu_collation_note_resolves(self):
        notes = {n['id']: n for n in C18.COLLATION_NOTES}
        self.assertIn('sm2-ji-40135', notes)
        self.assertEqual(notes['sm2-ji-40135']['reading'], '巳')


class CrossRegisterEvidenceTests(unittest.TestCase):
    def _resolve(self, quotes, ref, texts):
        self.assertIn(ref, quotes, ref)
        q = quotes[ref]
        text = texts[q['source_id']]
        loc = q['locator']
        self.assertEqual(text[loc['char_start']:loc['char_end']],
                         q['quote'], ref)
        self.assertEqual(text.count(q['quote']), 1, ref)

    def test_all_cross_refs_resolve_verbatim(self):
        texts = {sid: _text(fn) for sid, fn in SOURCE_FILE.items()}
        used = {name: set() for name in REGISTER_QUOTES}
        holders = list(E.EARTH_ROOT_TABLES.values())
        evidence_lists = []
        for table in holders:
            for cell in table:
                evidence_lists.append(cell['evidence'])
        for branch in E.TU_CHANGSHENG_CONFLICT['branches']:
            evidence_lists.append(branch['evidence'])
        for ev_list in evidence_lists:
            for ev in ev_list:
                ref = ev.get('quote_ref')
                if not ref:
                    continue
                register = ev.get('register')
                if register == 'self':
                    continue
                self.assertIn(register, REGISTER_QUOTES, ref)
                self._resolve(REGISTER_QUOTES[register], ref, texts)
                used[register].add(ref)
        # The corroboration spine must actually be exercised.
        self.assertTrue({'sf.lubiao', 'sf.sisheng', 'sf.siguan',
                         'sf.siku', 'sf.sijue', 'sm2.summary_tu',
                         'sm2.sida_archive'}
                        <= used['bazi_sanming_juan2_collation'])
        self.assertIn('sanming.lu_sentence', used['bazi_pattern'])

    def test_self_refs_resolve_to_registered_quotes(self):
        own = {q['id'] for q in E.EARTH_QUOTES}
        for table in E.EARTH_ROOT_TABLES.values():
            for cell in table:
                for ev in cell['evidence']:
                    if ev.get('register') == 'self':
                        self.assertIn(ev['quote_ref'], own)
        for branch in E.TU_CHANGSHENG_CONFLICT['branches']:
            for ev in branch['evidence']:
                if ev.get('register') == 'self':
                    self.assertIn(ev['quote_ref'], own)


class LightRootGapEvidenceTests(unittest.TestCase):
    def test_ditiansui_listings_have_no_earth_pair(self):
        text = _text('ditiansui_chanwei.txt')
        segment = text[39967:40119]
        # The listing segment enumerates wood/fire/metal/water pairs
        # only; no earth stem appears in it at all.
        self.assertNotIn('戊', segment)
        self.assertNotIn('己', segment)
        self.assertIn('丙丁逢戌', segment)
        self.assertEqual(text.count('戊己逢'), 0)
        quotes_f = REGISTER_QUOTES['bazi_fire_morphology']
        for qid in ('dt.root_mu', 'dt.root_yuqi_1', 'dt.root_yuqi_2',
                    'dt.root_heavy_light'):
            self._resolve(quotes_f, qid,
                          {'bazi.source.ditiansui-spouse': text})


class SealedPolicyUntouchedTests(unittest.TestCase):
    def test_policy_zero_change_and_no_earth_set(self):
        policy = EvidenceResolver().entities[
            'bazi.concept.action_effects_v1'][1]['attributes']
        self.assertEqual(policy['pure_months'], ['卯'])
        self.assertEqual(policy['isolated_months'], ['酉'])
        self.assertEqual(policy['reviewed_root_branches'],
                         {'木': ['亥', '寅', '卯'], '水': ['亥', '子'],
                          '金': ['酉']})
        self.assertNotIn('土', policy['reviewed_root_branches'])


if __name__ == '__main__':
    unittest.main()
