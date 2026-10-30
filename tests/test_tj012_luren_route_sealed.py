"""TJ-012.3 Slice A （禄刃路线负向裁定） SEALED tests.

Offline acceptance ONLY (machine-assembled sealed data tree),
following the test_tj013_bingyao_sealed precedent. This file is
deliberately NOT named in .github/workflows/validate.yml: real-chart
pattern candidates need the sealed Canonical foundations, which a
public checkout does not contain, and the verbatim quote checks need
the pinned snapshot texts themselves.

What is verified here and nowhere else:
- every registered quote (the Ren s054 route sentence and the three
  三命 table sentences) equals the pinned snapshot slice byte for
  byte and occurs exactly once in its snapshot; every per-stem
  禄/刃 fragment equals its recorded snapshot slice (fragments are
  short and recur elsewhere in the books, so no uniqueness is claimed
  for them);
- the eight Golden cases recompute their pillars from source_birth
  through the reviewed calendar path and produce exactly the
  hand-derived route through the real chart() pattern path;
- the pre-existing candidates() determination stays byte-identical
  in shape (status unresolved, every verdict field None) on the same
  real charts — Slice A must not move any existing determination.
"""
import hashlib
import json
from pathlib import Path
import unittest

from tianji_kb.bazi_pattern import PATTERN_VARIANT
from tianji_kb.calendar_tz import calendar_for_zone
from tianji_kb.operations.bazi_chart import chart

ROOT = Path(__file__).resolve().parents[1]
GOLDEN = json.loads(
    (ROOT / 'tests/golden_tj012_luren_route.json').read_text('utf-8'))
SNAPSHOT_ROOT = (ROOT / 'data/quarantine/public_domain_snapshots/daizhigev20')


def _snapshot_text(source):
    path = SNAPSHOT_ROOT / Path(source['snapshot_path']).name
    raw = path.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == source['snapshot_sha256']
    assert len(raw) == source['snapshot_bytes']
    text = raw.decode('utf-8')
    assert len(text) == source['snapshot_chars']
    return text


class QuoteVerbatimTests(unittest.TestCase):
    def test_sentence_quotes_equal_snapshot_slices_uniquely(self):
        texts = {}
        for source in (GOLDEN['table_source'], GOLDEN['rule_source']):
            texts[source['source_id']] = _snapshot_text(source)
        for quote in GOLDEN['quotes']:
            with self.subTest(quote=quote['id']):
                text = texts[quote['source_id']]
                loc = quote['locator']
                self.assertEqual(
                    text[loc['char_start']:loc['char_end']], quote['quote'])
                self.assertEqual(text.count(quote['quote']), 1,
                                 'sentence quotes must occur exactly once')

    def test_per_stem_fragments_equal_snapshot_slices(self):
        text = _snapshot_text(GOLDEN['table_source'])
        for row in GOLDEN['table']:
            with self.subTest(stem=row['stem']):
                frag = row['lu_fragment']
                self.assertEqual(
                    text[frag['char_start']:frag['char_end']], frag['quote'])
                if row['ren_fragment'] is not None:
                    rfrag = row['ren_fragment']
                    self.assertEqual(
                        text[rfrag['char_start']:rfrag['char_end']],
                        rfrag['quote'])

    def test_registered_sections_inside_expanded_review_scope(self):
        sources = json.loads(
            (ROOT / 'config/knowledge_sources.json').read_text('utf-8'))
        entries = {s['source_id']: s for s in sources['sources']}
        self.assertEqual(len(entries), 102, 'census count must not change')
        from collections import Counter
        self.assertEqual(
            Counter(s['evidence_level'] for s in entries.values()),
        # TJ-018.3 P1 普查同步：登记 bazi.source.
        # sanmingtonghui-applied（C 级）后 C:95 变 C:96
        # （登记表共 102 条），非放宽断言。
            Counter({'C': 96, 'D': 6}), 'census grades must not change')
        sanming = entries['bazi.source.sanmingtonghui']
        self.assertIn('论十干禄', sanming['review_scope'])
        self.assertIn('75008', sanming['review_scope'])
        self.assertIn('论阳刃', sanming['review_scope'])
        self.assertIn('180961', sanming['review_scope'])
        self.assertIn('quarantine_only', sanming['review_scope'])


class RealChartRouteTests(unittest.TestCase):
    def test_source_birth_recomputes_the_recorded_pillars(self):
        for case in GOLDEN['cases']:
            with self.subTest(case=case['id']):
                birth = case['source_birth']
                cal = calendar_for_zone(birth['value'], birth['zone'])
                self.assertEqual(
                    [cal['year_ganzhi'], cal['month_ganzhi'],
                     cal['day_ganzhi'], cal['hour_ganzhi']],
                    case['pillars'])

    def test_golden_cases_through_real_chart(self):
        for case in GOLDEN['cases']:
            with self.subTest(case=case['id']):
                out = chart(*case['pillars'],
                            pattern_variant=PATTERN_VARIANT)
                route = out['result']['pattern_route']
                want = case['expected']
                self.assertEqual(route['route'], want['route'])
                self.assertEqual(route['matched_via'], want['matched_via'])
                self.assertEqual(route['lu_branch'], want['lu_branch'])
                self.assertEqual(route['ren_branch'], want['ren_branch'])
                self.assertEqual(route['miscellaneous_month'],
                                 want['miscellaneous_month'])
                self.assertEqual(route['day_stem'], case['day_stem'])
                self.assertEqual(route['month_branch'], case['month_branch'])
                self.assertEqual(route['borrowed_route']['status'],
                                 'undetermined')
                det = route['determination']
                self.assertIsNone(det['pattern'])
                self.assertIsNone(det['true_false'])
                self.assertIsNone(det['success_failure'])
                self.assertIsNone(det['useful_god'])

    def test_existing_candidates_determination_unchanged(self):
        # Regression pin: on the same real charts, both families keep
        # the pre-Slice-A determination shape exactly.
        for case in GOLDEN['cases']:
            with self.subTest(case=case['id']):
                out = chart(*case['pillars'],
                            pattern_variant=PATTERN_VARIANT)
                for family in ('official', 'resource'):
                    det = out['result']['pattern_candidates'][family][
                        'determination']
                    self.assertEqual(det, {
                        'status': 'unresolved', 'pattern': None,
                        'true_false': None, 'success_failure': None,
                        'useful_god': None})


if __name__ == '__main__':
    unittest.main()
