"""TJ-012.3 Slice D-1 （任氏分支寅月真格，非对称） SEALED tests.

Offline acceptance ONLY (machine-assembled sealed data tree),
following the test_tj012_luren_route_sealed precedent. This file is
deliberately NOT named in .github/workflows/validate.yml: real-chart
pattern candidates need the sealed Canonical foundations, which a
public checkout does not contain, and the verbatim quote checks need
the pinned snapshot text itself.

What is verified here and nowhere else:
- the two registered quotes (s053 真格 definition, original-note
  layer; s054 Ren procedure sentence) equal the pinned snapshot
  slices byte for byte and occur exactly once in the snapshot;
- every Golden case recomputes its pillars from source_birth through
  the reviewed calendar path, calls the REAL Slice C pilot with the
  case's declared Jie window, and produces exactly the hand-derived
  determination through ren_yin_true_pattern over the real chart
  envelope — including the day-stem-excluded adjudication quartet
  (D2), the touchstone, and the ±1s segment-boundary flip pair;
- on the same real charts, the Slice A route block and Slice B zaqi
  block equal their direct computations byte for byte and the
  pre-existing candidates() determination keeps its exact pinned
  shape — Slice D-1 must not move any existing output.
"""
import hashlib
import json
from pathlib import Path
from types import SimpleNamespace
import unittest

from tianji_kb.bazi_pattern import (
    PATTERN_VARIANT, month_pattern_route, month_pattern_zaqi,
    ren_yin_true_pattern,
)
from tianji_kb.bazi_siling_pilot import yin_siling_pilot
from tianji_kb.calendar_tz import calendar_for_zone
from tianji_kb.operations.bazi_chart import chart

ROOT = Path(__file__).resolve().parents[1]
GOLDEN = json.loads(
    (ROOT / 'tests/golden_tj012_ren_yin_true.json').read_text('utf-8'))
SNAPSHOT_ROOT = (ROOT / 'data/quarantine/public_domain_snapshots/daizhigev20')
CANDIDATES_DETERMINATION = {
    'status': 'unresolved', 'pattern': None, 'true_false': None,
    'success_failure': None, 'useful_god': None}


def _snapshot_text():
    source = GOLDEN['rule_source']
    path = SNAPSHOT_ROOT / Path(source['snapshot_path']).name
    raw = path.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == source['snapshot_sha256']
    assert len(raw) == source['snapshot_bytes']
    text = raw.decode('utf-8')
    assert len(text) == source['snapshot_chars']
    return text


def _jie_facts(case):
    window = GOLDEN['jie_windows'][case['window']]
    facts = {'provider': dict(GOLDEN['provider']),
             'lichun': dict(window['lichun']),
             'next_jie': dict(window['next_jie'])}
    override = case.get('jie_override') or {}
    if override.get('precision_warning'):
        facts['precision_warning'] = True
    return facts


class QuoteVerbatimTests(unittest.TestCase):
    def test_quotes_equal_snapshot_slices_uniquely(self):
        text = _snapshot_text()
        for quote in GOLDEN['quotes']:
            with self.subTest(quote=quote['id']):
                loc = quote['locator']
                self.assertEqual(
                    text[loc['char_start']:loc['char_end']], quote['quote'])
                self.assertEqual(text.count(quote['quote']), 1,
                                 'sentence quotes must occur exactly once')


class RealChartDeterminationTests(unittest.TestCase):
    def test_source_birth_recomputes_the_recorded_pillars(self):
        for case in GOLDEN['cases']:
            with self.subTest(case=case['id']):
                birth = case['source_birth']
                cal = calendar_for_zone(birth['value'], birth['zone'])
                self.assertEqual(
                    [cal['year_ganzhi'], cal['month_ganzhi'],
                     cal['day_ganzhi'], cal['hour_ganzhi']],
                    case['pillars'])

    def test_golden_cases_end_to_end(self):
        for case in GOLDEN['cases']:
            with self.subTest(case=case['id']):
                envelope = chart(*case['pillars'],
                                 pattern_variant=PATTERN_VARIANT)
                pilot = yin_siling_pilot(
                    case['source_birth']['value'],
                    version_id='ditiansui-yuanshuo',
                    jie_facts=_jie_facts(case))
                want_pilot = case['pilot_expectation']
                self.assertEqual(pilot['status'], want_pilot['status'])
                self.assertEqual(pilot['commander'],
                                 want_pilot['commander'])
                if want_pilot.get('reason') is not None:
                    self.assertEqual(pilot['reason'], want_pilot['reason'])
                if want_pilot['status'] == 'computed':
                    self.assertEqual(pilot['segment']['index'],
                                     want_pilot['segment_index'])

                out = ren_yin_true_pattern(envelope, pilot)
                want = case['expected']
                self.assertEqual(out['status'], want['status'])
                self.assertEqual(out['decision_step'], want['decision_step'])
                self.assertEqual(out['abstention_reason'],
                                 want['abstention_reason'])
                det = out['determination']
                self.assertEqual(det['true_false'], want['true_false'])
                self.assertEqual(det['pattern'], want['pattern'])
                self.assertIsNone(det['success_failure'])
                self.assertIsNone(det['purity'])
                self.assertIsNone(det['useful_god'])
                for field in ('success_failure', 'purity', 'useful_god'):
                    self.assertIn('unreviewed', out['unreviewed'][field])
                if want['commander_visible_pillars'] is None:
                    self.assertIsNone(out['commander'])
                else:
                    self.assertEqual(out['commander']['stem'],
                                     want_pilot['commander'])
                    self.assertEqual(out['commander']['visible_pillars'],
                                     want['commander_visible_pillars'])
                    self.assertFalse(
                        out['commander']['day_stem_counts_as_exposure'])
                self.assertEqual(out['day_stem'], case['day_stem'])
                self.assertEqual(out['month_branch'], case['month_branch'])

    def test_slice_ab_blocks_byte_identical_on_same_charts(self):
        for case in GOLDEN['cases']:
            with self.subTest(case=case['id']):
                envelope = chart(*case['pillars'],
                                 pattern_variant=PATTERN_VARIANT)
                view = SimpleNamespace(steps=envelope['trace'],
                                       evidence=envelope['evidence'])
                result = envelope['result']
                self.assertEqual(result['pattern_route'],
                                 month_pattern_route(view))
                self.assertEqual(result['pattern_zaqi'],
                                 month_pattern_zaqi(view))
                self.assertEqual(result['pattern_route']['route'],
                                 case['route_expectation'])
                for family in ('official', 'resource'):
                    self.assertEqual(
                        result['pattern_candidates'][family]
                        ['determination'],
                        CANDIDATES_DETERMINATION)


if __name__ == '__main__':
    unittest.main()
