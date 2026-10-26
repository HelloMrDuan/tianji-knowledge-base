"""TJ-017.1 dayun classical-evidence SEALED tests: verbatim quotes vs the
pinned snapshots + real pinned-provider measurements end to end.

Offline acceptance ONLY (machine-assembled sealed data tree), following
the TJ-013 bingyao/tiaohou sealed precedents. This file is deliberately
NOT named in .github/workflows/validate.yml: the public repository
contains no data/ tree, so these tests can only run where the sealed
snapshots exist. Do not cite a public CI run of the public companion
file (test_tj0171_dayun_classical.py) as evidence for this file.

Hand-derived expectations: the two real births below were derived by
hand (year/month pillars via the five-tiger rule and the solar-term
calendar, directions via the classical rule sentence) and cross-checked
against the reviewed calendar path; elapsed seconds are TJ-015 pinned-
provider measurements (facts), and every conversion expectation is
recomputed in-test from those measured seconds, never copied from the
implementation's own output.
"""
import hashlib
import json
from datetime import datetime, timedelta
from pathlib import Path
import unittest

from tianji_kb.bazi_dayun_adversarial_cases import (
    execute_adversarial_case, refuse_age_counting_conversion)
from tianji_kb.bazi_dayun_classical import (
    QUOTES, EXCLUDED_SPANS, classical_direction,
    sanming_convert_measurement)
from tianji_kb.bazi_dayun_jie import adjacent_jie_distance
from tianji_kb.calendar_tz import calendar_for_zone
from tianji_kb.operations.bazi_chart import chart

ROOT = Path(__file__).resolve().parents[1]
GOLDEN = json.loads(
    (ROOT / 'tests/golden_tj0171_dayun_classical.json').read_text('utf-8'))
SNAPSHOTS = {s['source_id']: ROOT / s['snapshot_path']
             for s in GOLDEN['sources']}
REGISTRATIONS = {s['source_id']: s for s in GOLDEN['sources']}


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
        # The repository registration itself must carry the same digest.
        sources = json.loads((ROOT / 'config/knowledge_sources.json')
                             .read_text('utf-8'))['sources']
        entry = next(s for s in sources
                     if s['source_id'] == 'bazi.source.sanmingtonghui')
        sanming = REGISTRATIONS['bazi.source.sanmingtonghui']
        self.assertEqual(entry['sha256'], sanming['snapshot_sha256'])
        self.assertEqual(entry['blob_sha'], sanming['snapshot_blob_sha'])

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
        # 15 sanming quotes (ratio x2, direction rule, worked example x2,
        # anti-rounding, zero/borrow x2, handover x3, vol-11 witnesses x4)
        # plus 6 shenfeng quotes (2 headings, 4 examples).
        self.assertEqual(checked, 21)

    def test_excluded_spans_are_verbatim_too(self):
        for span in GOLDEN['excluded_spans']:
            text = self.texts[span['source_id']][1]
            loc = span['locator']
            with self.subTest(span=span['id']):
                self.assertEqual(text[loc['char_start']:loc['char_end']],
                                 span['quote'])

    def test_pua_positions_hold_the_unmapped_glyph(self):
        text = self.texts['bazi.source.sanmingtonghui'][1]
        # Exactly three U+ED92 occur inside the whole registered window.
        window = text[58457:59198]
        self.assertEqual(
            [58457 + i for i, c in enumerate(window) if c == ''],
            [59080, 59123, 59162])
        entries = list(GOLDEN['quotes']) + list(GOLDEN['excluded_spans'])
        for entry in entries:
            for note in entry.get('pua_annotations', []):
                offset = note['char_offset']
                with self.subTest(entry=entry['id'], offset=offset):
                    self.assertEqual(text[offset], '')
                    self.assertEqual(note['mapped_reading'], '算')
                    self.assertEqual(note['mapping_status'], 'confirmed')
                    # The mapped reading text equals the verbatim slice
                    # with exactly the annotated positions read as 算.
                    chars = list(entry['quote'])
                    base = entry['locator']['char_start']
                    for other in entry['pua_annotations']:
                        chars[other['char_offset'] - base] = '算'
                    self.assertEqual(''.join(chars),
                                     entry['mapped_reading_text'])

    def test_registered_window_core_is_pua_free(self):
        text = self.texts['bazi.source.sanmingtonghui'][1]
        core = text[58594:59060]
        self.assertFalse(any(0xE000 <= ord(c) <= 0xF8FF for c in core),
                         'the rule core (ratio/direction/example/'
                         'zero-borrow) must stay PUA-free as audited')


class RealMeasurementEndToEndTests(unittest.TestCase):
    # Hand-derived: 1958-08-15 is 戊戌 year (yang stem 戊), 庚申 month
    # (five-tiger: 戊癸之年甲作首 -> 寅甲卯乙辰丙巳丁午戊未己申庚);
    # yang + male -> forward to the future jie (白露).
    BIRTH_A = {'value': '1958-08-15T19:30:00+08:00', 'zone': 'Asia/Shanghai',
               'pillars': ['戊戌', '庚申', '甲子', '甲戌'],
               'role': 'male', 'direction': 'forward',
               'counting_target': 'future_jie', 'jie_name': '白露'}
    # Hand-derived: 1949-01-04 is still 戊子 year (before 立春), 甲子
    # month (子月; 戊年寅甲起, 子为第十一月甲子); yang + female ->
    # backward to the past jie (大雪).
    BIRTH_B = {'value': '1949-01-04T09:30:00+08:00', 'zone': 'Asia/Shanghai',
               'pillars': ['戊子', '甲子', '甲午', '己巳'],
               'role': 'female', 'direction': 'backward',
               'counting_target': 'past_jie', 'jie_name': '大雪'}

    def _run_case(self, case):
        cal = calendar_for_zone(case['value'], case['zone'])
        self.assertEqual(
            [cal['year_ganzhi'], cal['month_ganzhi'], cal['day_ganzhi'],
             cal['hour_ganzhi']], case['pillars'],
            'reviewed calendar path must reproduce the hand-derived '
            'pillars')
        direction = classical_direction(cal['year_ganzhi'],
                                        traditional_role=case['role'])
        self.assertEqual(direction['direction'], case['direction'])
        self.assertEqual(direction['counting_target'],
                         case['counting_target'])
        measured = adjacent_jie_distance(
            case['value'], case['direction'],
            expected_month_ganzhi=case['pillars'][1])
        self.assertEqual(measured['selected_jie']['name'],
                         case['jie_name'])
        out = sanming_convert_measurement(measured, periods=2)
        self.assertEqual(out['status'], 'converted')
        self.assertEqual(out['counted_jie']['name'], case['jie_name'])
        # Conversion expectations recomputed from the measured fact.
        whole, rem = divmod(measured['elapsed_seconds'], 7200)
        self.assertEqual(out['duration_interval_days']['min_days'],
                         whole * 10)
        self.assertEqual(out['duration_interval_days']['max_days'],
                         whole * 10 + (10 if rem else 0))
        birth = datetime.fromisoformat(case['value'])
        first = out['handover_intervals'][0]
        self.assertEqual(datetime.fromisoformat(first['earliest']),
                         birth + timedelta(days=whole * 10))
        self.assertEqual(
            datetime.fromisoformat(first['latest']),
            birth + timedelta(days=whole * 10 + (10 if rem else 0)))
        second = out['handover_intervals'][1]
        first_earliest = datetime.fromisoformat(first['earliest'])
        self.assertEqual(datetime.fromisoformat(second['earliest']).year,
                         first_earliest.year + 10)
        self.assertTrue(out['research_only'])
        self.assertFalse(out['public_enabled'])
        self.assertFalse(out['ai_enabled'])

    def test_forward_case(self):
        self._run_case(self.BIRTH_A)

    def test_backward_case(self):
        self._run_case(self.BIRTH_B)

    def test_default_chart_carries_no_classical_dayun_output(self):
        out = chart('戊戌', '庚申', '甲子', '甲戌')
        payload = json.dumps(out, ensure_ascii=False)
        self.assertNotIn('handover_intervals', payload)
        self.assertNotIn('dayun-direction-classical-v1', payload)
        self.assertNotIn('dayun-conversion-sanming-v1', payload)


class AdversarialRegressionTests(unittest.TestCase):
    def test_zero_jie_adversarial_case_still_unresolved(self):
        # TJ-016.2 ADV-001 (birth exactly at 立春, backward): the
        # classical evidence of this batch must NOT lift the refusal.
        result = execute_adversarial_case('ADV-001')
        self.assertIsNone(result.get('start_age'))
        measured = adjacent_jie_distance(
            '2000-02-04T20:40:24+08:00', 'backward',
            expected_month_ganzhi='戊寅')
        out = sanming_convert_measurement(measured)
        self.assertEqual(out['status'], 'unresolved')
        self.assertEqual(out['reason'],
                         'zero_jie_boundary_convention_unreviewed')

    def test_age_counting_conversion_still_refused(self):
        # 虚岁/实岁 have no classical source (five-book full-text search,
        # zero hits): the refusal stands unchanged after this batch.
        with self.assertRaises(ValueError):
            refuse_age_counting_conversion('xusui', 'shisui')
        with self.assertRaises(ValueError):
            refuse_age_counting_conversion('shisui', 'xusui')


if __name__ == '__main__':
    unittest.main()
