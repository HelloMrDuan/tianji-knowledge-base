"""TJ-013.1 SEALED tests: verbatim quotes vs the pinned snapshot + real chart.

Offline acceptance ONLY (machine-assembled sealed data tree), following
the test_phase2_liuyao precedent. This file is deliberately NOT named
in .github/workflows/validate.yml: the public repository contains no
data/ tree, so these tests can only run where the sealed snapshot and
Canonical foundations exist. Do not cite a public CI run of the public
companion file (test_tj0131_tiaohou.py) as evidence for this file.
"""
import hashlib
import json
from pathlib import Path
import unittest

from tianji_kb.bazi_tiaohou import SNAPSHOT_SHA256, VARIANT
from tianji_kb.engine import execute
from tianji_kb.operations.bazi_chart import chart

ROOT = Path(__file__).resolve().parents[1]
GOLDEN = json.loads((ROOT / 'tests/golden_tj0131_tiaohou.json').read_text('utf-8'))
SNAPSHOT = ROOT / GOLDEN['source']['snapshot_path']


def _all_quotes():
    for entry in GOLDEN['entries']:
        key = (entry['day_master'], entry['month_branch'])
        yield key, entry['quote'], entry['quote_locator']
        for branch in entry['branches']:
            yield key, branch['quote'], branch['locator']
        for item in entry['unencoded_branches']:
            yield key, item['quote'], item['locator']
        for item in entry['related']:
            yield key, item['quote'], item['locator']


class SnapshotVerbatimTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw = SNAPSHOT.read_bytes()
        cls.text = cls.raw.decode('utf-8')

    def test_snapshot_identity_matches_registration(self):
        self.assertEqual(hashlib.sha256(self.raw).hexdigest(), SNAPSHOT_SHA256)
        self.assertEqual(len(self.raw), GOLDEN['source']['snapshot_bytes'])
        self.assertEqual(len(self.text), GOLDEN['source']['snapshot_chars'])

    def test_every_quote_is_verbatim_at_its_locator_and_unique(self):
        checked = 0
        for key, quote, locator in _all_quotes():
            with self.subTest(entry=key, start=locator['char_start']):
                start, end = locator['char_start'], locator['char_end']
                self.assertEqual(self.text[start:end], quote)
                self.assertEqual(self.text.count(quote), 1)
                self.assertEqual(self.text.count('\n', 0, start) + 1,
                                 locator['line'])
                checked += 1
        # 119 entries + 10 encoded branches + 24 unencoded + 17 related.
        self.assertEqual(checked, 170)


class RealChartEndToEndTests(unittest.TestCase):
    def test_golden_cases_through_real_chart(self):
        for case in GOLDEN['cases']:
            with self.subTest(case=case['id']):
                out = chart(*case['pillars'], tiaohou_variant=VARIANT)
                assessment = out['result']['tiaohou_assessment']
                expected = case['expected']
                self.assertEqual(assessment['status'], expected['status'])
                self.assertTrue(out['research_only'])
                self.assertFalse(
                    out['interpretation_contract']['ai_may_explain'])
                if expected['status'] != 'matched':
                    continue
                self.assertEqual(
                    [(s['stem'], s['order'], s['presence'])
                     for s in assessment['sequence']],
                    [(s['stem'], s['order'], s['presence'])
                     for s in expected['sequence']])
                self.assertEqual(
                    [(b['id'], b['applied']) for b in assessment['branches']],
                    [(b['id'], b['applied']) for b in expected['branches']])

    def test_default_chart_has_no_tiaohou(self):
        out = chart('甲寅', '丙寅', '甲子', '戊辰')
        self.assertNotIn('tiaohou_assessment', out['result'])

    def test_engine_research_mode_end_to_end(self):
        out = execute('bazi', {'tiaohou_variant': VARIANT,
                               'year_ganzhi': '戊辰', 'month_ganzhi': '庚辰',
                               'day_ganzhi': '甲寅', 'hour_ganzhi': '甲申'},
                      allow_research=True)
        assessment = out['result']['tiaohou_assessment']
        self.assertEqual(assessment['status'], 'matched')
        self.assertEqual([s['stem'] for s in assessment['sequence']],
                         ['庚', '壬'])
        self.assertEqual(out['mode'], 'research')


if __name__ == '__main__':
    unittest.main()
