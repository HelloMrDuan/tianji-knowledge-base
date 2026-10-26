"""TJ-013 bingyao SEALED tests: verbatim quotes vs the pinned snapshots + real chart.

Offline acceptance ONLY (machine-assembled sealed data tree), following
the test_tj0131_tiaohou_sealed precedent. This file is deliberately NOT
named in .github/workflows/validate.yml: the public repository contains
no data/ tree, so these tests can only run where the sealed snapshots
and Canonical foundations exist. Do not cite a public CI run of the
public companion file (test_tj013_bingyao.py) as evidence for this file.
"""
import hashlib
import json
from pathlib import Path
import unittest

from tianji_kb.bazi_bingyao import SNAPSHOT_SHA256, VARIANT
from tianji_kb.calendar_tz import calendar_for_zone
from tianji_kb.engine import execute
from tianji_kb.operations.bazi_chart import chart

ROOT = Path(__file__).resolve().parents[1]
GOLDEN = json.loads((ROOT / 'tests/golden_tj013_bingyao.json').read_text('utf-8'))
SNAPSHOTS = {
    GOLDEN['source']['source_id']:
        ROOT / GOLDEN['source']['snapshot_path'],
    GOLDEN['counterweight_source']['source_id']:
        ROOT / GOLDEN['counterweight_source']['snapshot_path'],
}
REGISTRATIONS = {
    GOLDEN['source']['source_id']: GOLDEN['source'],
    GOLDEN['counterweight_source']['source_id']: GOLDEN['counterweight_source'],
}


class SnapshotVerbatimTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.texts = {}
        for source_id, path in SNAPSHOTS.items():
            raw = path.read_bytes()
            cls.texts[source_id] = (raw, raw.decode('utf-8'))

    def test_snapshot_identities_match_registration(self):
        for source_id, registration in REGISTRATIONS.items():
            raw, text = self.texts[source_id]
            with self.subTest(source=source_id):
                self.assertEqual(hashlib.sha256(raw).hexdigest(),
                                 registration['snapshot_sha256'])
                self.assertEqual(len(raw), registration['snapshot_bytes'])
                self.assertEqual(len(text), registration['snapshot_chars'])
        self.assertEqual(
            hashlib.sha256(self.texts[GOLDEN['source']['source_id']][0])
            .hexdigest(), SNAPSHOT_SHA256)

    def test_every_quote_is_verbatim_at_its_locator_and_unique(self):
        checked = 0
        for quote in GOLDEN['quotes']:
            text = self.texts[quote['source_id']][1]
            loc = quote['locator']
            with self.subTest(quote=quote['id']):
                start, end = loc['char_start'], loc['char_end']
                self.assertEqual(text[start:end], quote['quote'])
                self.assertEqual(text.count(quote['quote']), 1)
                self.assertEqual(text.count('\n', 0, start) + 1, loc['line'])
                checked += 1
        # 8 shenfeng quotes (disease/medicine definitions, the encoded
        # wealth pair, the registered food pair and earth example, the
        # procedure sentence, the no-disease clause, the zhengguan
        # cross-section tension) plus 1 ditiansui counterweight quote.
        self.assertEqual(checked, 9)
        rule = GOLDEN['rule']
        text = self.texts[GOLDEN['source']['source_id']][1]
        loc = rule['quote_locator']
        self.assertEqual(text[loc['char_start']:loc['char_end']], rule['quote'])
        section = rule['section']
        self.assertLessEqual(section['char_start'], loc['char_start'])
        self.assertLessEqual(loc['char_end'], section['char_end'])


class RealChartEndToEndTests(unittest.TestCase):
    def test_golden_cases_through_real_chart(self):
        for case in GOLDEN['cases']:
            with self.subTest(case=case['id']):
                out = chart(*case['pillars'], bingyao_variant=VARIANT)
                result = out['result']
                assessment = result['bingyao_assessment']
                expected = case['expected']
                # The engine's own ten-god facts must equal the Golden
                # transcription (which was derived by hand from the
                # pillars, not copied from any implementation output).
                engine_gods = [
                    {'pillar': row['pillar'], 'stem': row['stem'],
                     'ten_god': row['ten_god']}
                    for row in result['stem_ten_gods']
                    if row['pillar'] != 'day']
                self.assertEqual(engine_gods, case['visible_gods'])
                self.assertEqual(assessment['status'], expected['status'])
                self.assertIsNone(assessment['determination'])
                self.assertEqual(assessment['medicine_effect_status'],
                                 'unadjudicated')
                self.assertTrue(out['research_only'])
                self.assertFalse(
                    out['interpretation_contract']['ai_may_explain'])
                if expected['status'] == 'not_triggered':
                    self.assertEqual(assessment['not_triggered_reason'],
                                     expected['not_triggered_reason'])
                    self.assertIsNone(assessment['disease_candidate'])
                    self.assertIsNone(assessment['medicine_candidate'])
                else:
                    self.assertEqual(assessment['disease_candidate']['gods'],
                                     expected['disease_gods'])
                    self.assertEqual(assessment['medicine_status'],
                                     expected['medicine_status'])
                    if expected['medicine_status'] == 'candidate_present':
                        self.assertEqual(
                            assessment['medicine_candidate']['gods'],
                            expected['medicine_gods'])
                if 'boundary_fact' in case:
                    fact = case['boundary_fact']
                    day_hidden = next(
                        row for row in result['hidden_stems']
                        if row['pillar'] == fact['pillar'])
                    hidden = {h['stem']: h['ten_god']
                              for h in day_hidden['hidden_stems']}
                    self.assertEqual(hidden.get(fact['hidden_stem']),
                                     fact['hidden_ten_god'],
                                     'boundary premise: the god is attested '
                                     'only in hidden stems')

    def test_source_birth_recomputes_the_recorded_pillars(self):
        # Every Golden case binds a real birth instant to its pillars
        # through the reviewed calendar path; no hand-built pillars.
        for case in GOLDEN['cases']:
            with self.subTest(case=case['id']):
                birth = case['source_birth']
                cal = calendar_for_zone(birth['value'], birth['zone'])
                self.assertEqual(
                    [cal['year_ganzhi'], cal['month_ganzhi'],
                     cal['day_ganzhi'], cal['hour_ganzhi']],
                    case['pillars'])

    def test_default_chart_has_no_bingyao(self):
        out = chart('戊戌', '庚申', '甲子', '甲戌')
        self.assertNotIn('bingyao_assessment', out['result'])

    def test_engine_research_mode_end_to_end(self):
        out = execute('bazi', {'bingyao_variant': VARIANT,
                               'year_ganzhi': '戊戌', 'month_ganzhi': '庚申',
                               'day_ganzhi': '甲子', 'hour_ganzhi': '甲戌'},
                      allow_research=True)
        assessment = out['result']['bingyao_assessment']
        self.assertEqual(assessment['status'], 'triggered')
        self.assertEqual(assessment['medicine_status'], 'candidate_present')
        self.assertEqual(out['mode'], 'research')


if __name__ == '__main__':
    unittest.main()
