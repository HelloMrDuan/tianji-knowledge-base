"""TJ-012.3 Slice B （杂气选格陈述） SEALED tests.

Offline acceptance ONLY (machine-assembled sealed data tree),
following the test_tj012_luren_route_sealed precedent. This file is
deliberately NOT named in .github/workflows/validate.yml: real-chart
pattern candidates need the sealed Canonical foundations, which a
public checkout does not contain, and the verbatim quote checks need
the pinned snapshot texts themselves.

What is verified here and nowhere else:
- every registered quote （原注杂气段 and the two Sanming conflict
  witnesses) equals the pinned snapshot slice byte for byte and
  occurs exactly once in its snapshot, with no PUA inside any quote
  window;
- the six Golden cases recompute their pillars from source_birth
  through the reviewed calendar path and produce exactly the
  hand-derived selection statement through the real chart() pattern
  path, while the Slice A pattern_route and the pre-existing
  candidates() determination stay untouched on the same charts;
- the two Slice A miscellaneous-month Golden charts keep their Slice
  A route verdicts and gain the hand-derived zaqi statements
  (coexistence pin in the other direction).
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
    (ROOT / 'tests/golden_tj012_zaqi_selection.json').read_text('utf-8'))
SLICE_A_GOLDEN = json.loads(
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
    def test_quotes_equal_snapshot_slices_uniquely(self):
        texts = {}
        for source in (GOLDEN['rule_source'], GOLDEN['conflict_source']):
            texts[source['source_id']] = _snapshot_text(source)
        for quote in GOLDEN['quotes']:
            with self.subTest(quote=quote['id']):
                text = texts[quote['source_id']]
                loc = quote['locator']
                self.assertEqual(
                    text[loc['char_start']:loc['char_end']], quote['quote'])
                self.assertEqual(text.count(quote['quote']), 1,
                                 'sentence quotes must occur exactly once')
                self.assertFalse(
                    any(0xE000 <= ord(c) <= 0xF8FF for c in quote['quote']),
                    'no PUA may sit inside a registered quote window')

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
        ditiansui = entries['bazi.source.ditiansui-spouse']
        self.assertIn('影响遥系', ditiansui['review_scope'])
        self.assertIn('33161', ditiansui['review_scope'])
        self.assertIn('33313', ditiansui['review_scope'])
        sanming = entries['bazi.source.sanmingtonghui']
        self.assertIn('192131', sanming['review_scope'])
        self.assertIn('245030', sanming['review_scope'])
        self.assertIn('冲突分支证据', sanming['review_scope'])
        self.assertIn('quarantine_only', sanming['review_scope'])


class RealChartZaqiTests(unittest.TestCase):
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
                zaqi = out['result']['pattern_zaqi']
                want = case['expected']
                self.assertEqual(zaqi['status'], want['status'])
                self.assertEqual(zaqi['arm'], want['arm'])
                self.assertEqual(zaqi['abstention_reason'],
                                 want['abstention_reason'])
                self.assertEqual(zaqi['miscellaneous_month'],
                                 want['miscellaneous_month'])
                self.assertEqual(zaqi['day_stem'], case['day_stem'])
                self.assertEqual(zaqi['month_branch'],
                                 case['month_branch'])
                self.assertEqual(
                    [(r['stem'], r['ten_god'])
                     for r in zaqi['month_hidden_renyuan']],
                    [(r['stem'], r['ten_god'])
                     for r in want['month_hidden_renyuan']])
                self.assertEqual(
                    [(r['stem'], r['ten_god'], r['visible_pillars'])
                     for r in zaqi['exposed_renyuan']],
                    [(r['stem'], r['ten_god'], r['visible_pillars'])
                     for r in want['exposed_renyuan']])
                self.assertEqual(zaqi['conflict']['conflict_present'],
                                 want['conflict_present'])
                if want['conflict_present']:
                    self.assertEqual(
                        [r['id'] for r in zaqi['conflict']['case_refs']],
                        ['sanming.zaqi_case_rilu',
                         'sanming.zaqi_poem_nvming'])
                if want['selection_basis'] is None:
                    self.assertIsNone(zaqi['selection'])
                else:
                    self.assertEqual(zaqi['selection']['basis'],
                                     want['selection_basis'])
                    self.assertEqual(
                        [c['stem'] for c in
                         zaqi['selection']['selected_candidates']],
                        want['selected_candidate_stems'])
                    self.assertIsNone(
                        zaqi['selection']['pattern_determination'])
                    conversion = zaqi['selection']['earth_conversion']
                    if want['earth_conversion_status'] is None:
                        self.assertIsNone(conversion)
                    else:
                        self.assertEqual(conversion['status'],
                                         want['earth_conversion_status'])
                        self.assertIsNone(
                            conversion['converted_pattern_name'])
                        self.assertIsNone(conversion['converted_ten_god'])
                det = zaqi['determination']
                self.assertIsNone(det['pattern'])
                self.assertIsNone(det['true_false'])
                self.assertIsNone(det['success_failure'])
                self.assertIsNone(det['useful_god'])
                # Slice A coexistence on the same chart: the route is
                # attached and keeps its own verdict domain.
                self.assertIn('pattern_route', out['result'])

    def test_existing_candidates_determination_unchanged(self):
        # Regression pin: on the same real charts, both families keep
        # the pre-existing determination shape exactly, and Slice B
        # must not move the Slice A route on its own Golden chart.
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
        slice_a_case = next(c for c in SLICE_A_GOLDEN['cases']
                            if c['id'] == 'lu-jia-yin')
        out = chart(*slice_a_case['pillars'],
                    pattern_variant=PATTERN_VARIANT)
        route = out['result']['pattern_route']
        self.assertEqual(route['route'],
                         slice_a_case['expected']['route'])
        self.assertEqual(route['matched_via'],
                         slice_a_case['expected']['matched_via'])
        self.assertEqual(out['result']['pattern_zaqi']['status'],
                         'not_applicable')

    def test_slice_a_miscellaneous_charts_gain_zaqi_statements(self):
        # The two Slice A Golden charts born in a miscellaneous month:
        # hand-derived zaqi expectations from their recorded pillars
        # and the executed hidden/exposure facts.
        expectations = {
            # 戊日戌月： 人元戊辛丁，年月时干己甲乙无透 → 戊己臂弃判。
            'misc-wu-xu': {'status': 'abstained',
                           'arm': 'wuji_exposed_renyuan',
                           'abstention_reason': 'no_exposed_renyuan',
                           'exposed': []},
            # 辛日戌月： 人元戊辛丁，年月时干己甲己无透 → 一般臂陈述。
            'yin-noblade-xin-xu': {'status': 'stated',
                                   'arm': 'general_tu_unconverted',
                                   'abstention_reason': None,
                                   'exposed': []},
        }
        for case_id, want in expectations.items():
            with self.subTest(case=case_id):
                case = next(c for c in SLICE_A_GOLDEN['cases']
                            if c['id'] == case_id)
                out = chart(*case['pillars'],
                            pattern_variant=PATTERN_VARIANT)
                route = out['result']['pattern_route']
                self.assertEqual(route['route'],
                                 case['expected']['route'])
                zaqi = out['result']['pattern_zaqi']
                self.assertEqual(zaqi['status'], want['status'])
                self.assertEqual(zaqi['arm'], want['arm'])
                self.assertEqual(zaqi['abstention_reason'],
                                 want['abstention_reason'])
                self.assertEqual(
                    [r['stem'] for r in zaqi['exposed_renyuan']],
                    want['exposed'])
                self.assertTrue(zaqi['conflict']['conflict_present'])


if __name__ == '__main__':
    unittest.main()
