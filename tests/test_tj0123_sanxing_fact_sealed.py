"""TJ-012.3 三刑组表事实层设计审定：密封验证。

Runs in the offline assembled acceptance only (NOT public CI, same
partition rule as the earlier batches). Pins:

- snapshot integrity for the Sanming snapshot the adjudication pins
  (sha256 + char counts, identical to the 018-B register pin);
- every quote reference in bazi_sanxing_fact_adjudication resolves to
  its home register and the home register's slice re-verifies
  byte-for-byte against the sealed snapshot (slice at the registered
  locator equals the registered quote; for quotes carrying a
  mapped_reading, the differing positions are exactly the registered
  collation-note offsets with the registered readings);
- the two Canonical section pins (s020/s021) match the assembled
  phase1 bundle byte-for-byte, and the three-punishments concept in
  the bundle still carries the pinned status / production policy /
  executable policy (the adjudication changes no concept semantics);
- the assembled foundations branch-relation tables are exactly the
  five pinned families (no punishments key) and the coverage
  matrix's three overlap pairs really sit in the named tables;
- the assembled phase2 execution bundle still contains no punish
  rule surface and still states the school-divergence exclusion;
- current behaviour regression: real-chart relation facts produced
  by the production structural functions contain no punishment
  fact of any kind (the adjudication batch wires nothing).
"""
import hashlib
import json
from pathlib import Path
import unittest

from tianji_kb import bazi_sanming_juan2_sanxing_collation as cj
from tianji_kb import bazi_sanxing_fact_adjudication as adj
from tianji_kb import bazi_yuanhai_zhengguan as yh
from tianji_kb.bazi_core import (branch_relations, chart_from_datetime,
                                 reviewed_relations)

ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT_DIR = (ROOT / 'data' / 'quarantine' / 'public_domain_snapshots'
                / 'daizhigev20')
CANONICAL_BAZI = ROOT / 'data' / 'canonical' / 'bazi'

SANMING_QUOTES = {q['id']: q for q in cj.COLLATION_QUOTES}
YUANHAI_QUOTES = {q['id']: q for q in yh.YUANHAI_ZHENGGUAN_QUOTES}
NOTES = {n['id']: n for n in cj.COLLATION_NOTES}
HOME = {'bazi_sanming_juan2_sanxing_collation': (SANMING_QUOTES,
                                                  'sanming_tonghui.txt'),
        'bazi_yuanhai_zhengguan': (YUANHAI_QUOTES, 'yuanhai_ziping.txt')}


def _text(filename):
    return (SNAPSHOT_DIR / filename).read_bytes().decode('utf-8')


class SnapshotIntegrityTest(unittest.TestCase):
    def test_sanming_pin_matches_018b_and_snapshot(self):
        meta = cj.COLLATION_SNAPSHOTS['sanming_tonghui.txt']
        raw = (SNAPSHOT_DIR / 'sanming_tonghui.txt').read_bytes()
        self.assertEqual(hashlib.sha256(raw).hexdigest(), meta['sha256'])
        self.assertEqual(len(raw.decode('utf-8')), meta['chars'])
        pin = adj.SANXING_ADJUDICATION_REGISTER['source_snapshot']
        self.assertEqual(pin['sanming_sha256'], meta['sha256'])
        self.assertEqual(pin['sanming_chars'], meta['chars'])


class QuoteSliceTest(unittest.TestCase):
    def test_all_referenced_quotes_verify_byte_for_byte(self):
        texts = {}
        for ref in adj.QUOTE_REFERENCES:
            quotes, filename = HOME[ref['register']]
            quote = quotes[ref['quote_id']]
            if filename not in texts:
                texts[filename] = _text(filename)
            text = texts[filename]
            loc = quote['locator']
            self.assertEqual(text[loc['char_start']:loc['char_end']],
                             quote['quote'], ref['quote_id'])
            mapped = quote.get('mapped_reading')
            if mapped is not None:
                self._verify_mapped(quote, mapped)

    def _verify_mapped(self, quote, mapped):
        raw = quote['quote']
        self.assertEqual(len(raw), len(mapped), quote['id'])
        start = quote['locator']['char_start']
        expected = {}
        for ref_id in quote.get('collation_refs', []):
            note = NOTES[ref_id]
            expected[note['char_offset'] - start] = note['reading']
        for i, (a, b) in enumerate(zip(raw, mapped)):
            if a != b:
                self.assertIn(i, expected, (quote['id'], i))
                self.assertEqual(b, expected[i], (quote['id'], i))


class CanonicalPinTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bundle = json.loads(
            (CANONICAL_BAZI / 'phase1_knowledge.json').read_text('utf-8'))

    def _sections(self):
        found = {}
        def walk(o):
            if isinstance(o, dict):
                sid = o.get('section_id')
                if sid and 'original_text' in o:
                    found[sid] = o
                for v in o.values():
                    walk(v)
            elif isinstance(o, list):
                for v in o:
                    walk(v)
        walk(self.bundle)
        return found

    def test_section_pins_match_bundle(self):
        sections = self._sections()
        for pin in adj.SEALED_SECTION_PINS:
            sec = sections[pin['section_id']]
            self.assertEqual(sec['original_text'], pin['original_text'],
                             pin['section_id'])
            self.assertEqual(sec['source_id'], pin['source_id'])

    def test_bazi_sections_mentioning_punishment_are_pinned(self):
        # E0329 (TJ-018.3 P1): the Canonical build of Sanming
        # 《论三刑》 added bazi.section.s060, whose text mentions
        # 刑 by subject; the pinned set grows by exactly that one
        # section (s020/s021 unchanged).
        sections = self._sections()
        hits = {sid for sid, s in sections.items()
                if '刑' in s['original_text']}
        self.assertEqual(
            hits,
            {'bazi.section.s020', 'bazi.section.s021',
             'bazi.section.s060'})

    def test_concept_semantics_unchanged(self):
        concept = next(c for c in self.bundle['concepts']
                       if c['id'] == 'bazi.concept.conflict_three_punishments')
        attrs = concept['attributes']
        self.assertEqual(attrs['status'], 'unresolved')
        self.assertEqual(attrs['production_policy'],
                         adj.CONCEPT_LINKAGE['production_policy'])
        self.assertEqual(attrs['executable_policy'],
                         'blocked_pending_school_resolution')
        positions = {p['id']: p['section_ids'] for p in attrs['positions']}
        self.assertEqual(positions['yuanhai-uses-punishment'],
                         ['bazi.section.s020'])
        self.assertEqual(
            positions['ditiansui-rejects-mechanical-punishment'],
            ['bazi.section.s021'])


class ExecutionSurfaceTest(unittest.TestCase):
    def test_foundations_tables_and_overlaps(self):
        foundations = json.loads(
            (CANONICAL_BAZI / 'foundations_v1.json').read_text('utf-8'))
        rel = foundations['earthly_branch_relations']
        self.assertEqual(set(rel), {'clashes', 'triple_harmonies',
                                    'directional_meetings', 'six_harmonies',
                                    'harms'})
        tables = {'clash': {frozenset(r) for r in rel['clashes']},
                  'six_harmony': {frozenset(r[:2])
                                  for r in rel['six_harmonies']},
                  'harm': {frozenset(r) for r in rel['harms']}}
        overlaps = adj.COVERAGE_MATRIX[
            'overlap_with_existing_relations']['pair_overlaps']
        self.assertEqual(len(overlaps), 3)
        for row in overlaps:
            self.assertIn(frozenset(row['pair']),
                          tables[row['existing_kind']], row['pair'])

    def test_phase2_has_no_punishment_surface(self):
        bundle = json.loads(
            (CANONICAL_BAZI / 'phase2_execution.json').read_text('utf-8'))
        dump = json.dumps(bundle, ensure_ascii=False)
        self.assertNotIn('punish', dump)
        self.assertIn('三刑存在明确流派分歧，当前不进入统一 executable 规则',
                      dump)


class CurrentBehaviourRegressionTest(unittest.TestCase):
    def test_real_chart_relations_have_no_punishment_facts(self):
        # real birth datetime through the production calendar chain;
        # the pin is on the relation surface, not on this chart.
        chart = chart_from_datetime('1990-05-17T12:00:00+08:00')
        stems = [p['stem']['value'] for p in chart['pillars']]
        branches = [p['branch']['value'] for p in chart['pillars']]
        for output in (reviewed_relations(stems, branches),
                       branch_relations(branches),
                       chart['branch_relations']):
            dump = json.dumps(output, ensure_ascii=False)
            self.assertNotIn('punish', dump)
            self.assertNotIn('三刑', dump)
            self.assertNotIn('sanxing', dump)

    def test_discriminating_branch_sets_have_no_punishment_facts(self):
        for branches in (['寅', '巳', '申', '辰'],
                         ['丑', '未', '戌', '午'],
                         ['子', '卯', '辰', '辰']):
            output = branch_relations(branches)
            kinds = {row['kind'] for row in output['pairs']}
            self.assertTrue(kinds <= {'clash', 'six_harmony', 'harm'})
            dump = json.dumps(output, ensure_ascii=False)
            self.assertNotIn('punish', dump)


if __name__ == '__main__':
    unittest.main()
