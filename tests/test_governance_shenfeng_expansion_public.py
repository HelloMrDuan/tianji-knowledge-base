"""Governance Shenfeng Canonical expansion (E0348), public side.

One Canonical expansion serving two pending items: the new
classic bazi.classic.shenfeng carries the bingyao definition
section (s071), the zhengguan tension window (s072) and the
《起大运法》 section (s073); the existing Ditiansui classic gains
the zhonghe counterweight window (s074). bingyao-shenfeng-v1
flips to registered (r040 / bazi.phase2.bingyao_assessment) and
the dayun-classical-variants Shenfeng segment flips inside its
row (additional r041 / bazi.phase2.dayun_shenfeng_conversion),
leaving the maintained inventory at four: tiaohou, siling and
the two inherited rows in terminal inherited form
(inherited_registered_phase1_phase2 -- the layers register
nothing themselves, and the governance exact-equality invariant
forbids both reusing the underlying rule ids and minting empty
ones; see GOVERNANCE_SHENFENG_RECORD).

These tests pin the public (no-sealed-data) side: the governance
record and inventory, the flipped module disclosures, the chart
signature / engine gate, and the governance document. The sealed
side lives in tests/test_phase2_bazishenfeng.py.
"""
import re
import unittest
from pathlib import Path

from tianji_kb import bazi_bingyao as by
from tianji_kb import bazi_dayun_classical as dc
from tianji_kb import bazi_dayun_compose as compose
from tianji_kb import bazi_dayun_timeline_view as view
from tianji_kb import bazi_registration_governance as gov

ROOT = Path(__file__).resolve().parents[1]
RECORD = gov.GOVERNANCE_SHENFENG_RECORD


def _row(item):
    return next(r for r in gov.REGISTRATION_INVENTORY
                if r['item'] == item)


class ShenfengExpansionPublicTests(unittest.TestCase):
    def test_record_entities(self):
        self.assertEqual(RECORD['event'], 'E0348')
        self.assertEqual(RECORD['canonical_classics_added'],
                         ['bazi.classic.shenfeng'])
        self.assertEqual(RECORD['canonical_chapters_added'],
                         ['bazi.chapter.shenfeng_bingyao',
                          'bazi.chapter.shenfeng_zhengguan',
                          'bazi.chapter.shenfeng_qi_dayun_fa',
                          'bazi.chapter.ditiansui_zhonghe'])
        self.assertEqual(RECORD['canonical_sections_added'],
                         ['bazi.section.s071', 'bazi.section.s072',
                          'bazi.section.s073', 'bazi.section.s074'])
        self.assertEqual(RECORD['canonical_terms_added'],
                         ['bazi.term.bingyao',
                          'bazi.term.dayun_shenfeng_conversion'])
        self.assertEqual(RECORD['phase1_rules_added'],
                         ['bazi.rule.r040', 'bazi.rule.r041'])
        self.assertEqual(RECORD['phase2_rules_added'],
                         ['bazi.phase2.bingyao_assessment',
                          'bazi.phase2.dayun_shenfeng_conversion'])
        self.assertEqual(len(RECORD['golden_cases_added']), 11)
        self.assertEqual(len(RECORD['source_refs_subset']), 7)

    def test_record_snapshot_pins(self):
        self.assertEqual(RECORD['snapshot_files_before'], 237)
        self.assertEqual(RECORD['snapshot_files_after'], 237)
        self.assertEqual(RECORD['snapshot_bytes_before'], 16221036)
        self.assertEqual(RECORD['snapshot_bytes_after'], 16272294)
        self.assertEqual(
            RECORD['manifest_sha256_before'],
            '97e211c4582f7cf4d890c2bf8071573fbaced193d740c185d2'
            'c891a3f2e51324')
        for key in ('manifest_sha256_before',
                    'manifest_sha256_after'):
            self.assertTrue(
                re.fullmatch(r'[0-9a-f]{64}', RECORD[key]), key)
        self.assertNotEqual(RECORD['manifest_sha256_before'],
                            RECORD['manifest_sha256_after'])
        for digest in RECORD['sealed_file_sha256_after'].values():
            self.assertTrue(re.fullmatch(r'[0-9a-f]{64}', digest))

    def test_bingyao_row_flip(self):
        row = _row('bingyao-shenfeng-v1')
        self.assertEqual(row['disposition'], 'registered')
        self.assertEqual(row['phase1_rule_id'], 'bazi.rule.r040')
        self.assertEqual(row['phase2_rule_id'],
                         'bazi.phase2.bingyao_assessment')
        self.assertIsNone(row['unlock_path'])
        self.assertNotIn('reason_class', row)
        for marker in ('bazi.classic.shenfeng', 'bazi.section.s071',
                       'bazi.section.s072', 'bazi.section.s074',
                       'bazi.rule.r040'):
            self.assertIn(marker, row['reason'])

    def test_dayun_row_fully_registered(self):
        row = _row('dayun-classical-variants')
        self.assertEqual(row['disposition'], 'registered')
        self.assertEqual(row['additional_phase1_rule_ids'],
                         ['bazi.rule.r039', 'bazi.rule.r041'])
        self.assertEqual(
            row['additional_phase2_rule_ids'],
            ['bazi.phase2.dayun_sanming_conversion',
             'bazi.phase2.dayun_shenfeng_conversion'])
        self.assertIn('registered', row['segments']['shenfeng'])
        self.assertNotIn('maintained_pending',
                         row['segments']['shenfeng'])
        for marker in ('bazi.section.s073', 'bazi.rule.r041'):
            self.assertIn(marker, row['reason'])

    def test_inherited_rows_terminal_form(self):
        for item in ('dayun-compose', 'dayun-timeline-view'):
            row = _row(item)
            self.assertEqual(row['disposition'],
                             'maintained_pending')
            self.assertEqual(row['reason_class'],
                             'inherited_pending')
            self.assertIn('inherited_registered_phase1_phase2',
                          row['reason'])
            self.assertIn('神峰分段注册（E0348）',
                          row['unlock_path'])

    def test_flipped_and_maintained_sets(self):
        # E0352: tiaohou-qiongtong-v1 flipped as well (flipped
        # 12; maintained three).
        self.assertEqual(len(gov.FLIPPED_ITEMS), 12)
        self.assertIn('bingyao-shenfeng-v1', gov.FLIPPED_ITEMS)
        self.assertEqual(len(gov.MAINTAINED_ITEMS), 3)
        self.assertEqual(sorted(gov.MAINTAINED_ITEMS),
                         sorted(['dayun-compose',
                                 'dayun-timeline-view',
                                 'siling-yin-pilot']))

    def test_bingyao_disclosure_flipped(self):
        out = by.bingyao_lookup('甲', [
            {'pillar': 'year', 'stem': '戊', 'ten_god': '偏财'},
            {'pillar': 'month', 'stem': '庚', 'ten_god': '七杀'},
            {'pillar': 'hour', 'stem': '甲', 'ten_god': '比肩'}])
        self.assertEqual(out['evidence_binding'],
                         'registered_phase1_phase2')
        self.assertIsNone(out['determination'])
        sections = {q['id']: q['section_id'] for q in by.QUOTES}
        self.assertEqual(sections['disease_definition'],
                         'bazi.section.s071')
        self.assertEqual(sections['zhengguan_tension'],
                         'bazi.section.s072')
        self.assertEqual(sections['ditiansui_counterweight'],
                         'bazi.section.s074')
        self.assertTrue(any('bazi.rule.r040' in line
                            for line in out['scope_limits']))

    def test_shenfeng_disclosure_flipped(self):
        converted = dc.shenfeng_convert_days(30, direction='forward')
        self.assertEqual(converted['evidence_binding'],
                         'registered_phase1_phase2')
        self.assertEqual(
            [q['source_section_id']
             for q in converted['evidence_quotes']],
            ['bazi.section.s073'] * 3)
        # The zero-day branch historically reported through the
        # default (Sanming) flags call; the flip unifies every
        # branch on the registered value.
        zero_day = dc.shenfeng_convert_days(0, direction='forward')
        self.assertEqual(zero_day['evidence_binding'],
                         'registered_phase1_phase2')
        direction = dc.classical_direction(
            '甲子', traditional_role='male')
        for quote in direction['evidence_quotes']:
            if quote['id'].startswith('sf_'):
                self.assertEqual(quote['source_section_id'],
                                 'bazi.section.s073')

    def test_compose_view_terminal_binding(self):
        self.assertEqual(compose._flags()['evidence_binding'],
                         'inherited_registered_phase1_phase2')
        self.assertEqual(view._flags()['evidence_binding'],
                         'inherited_registered_phase1_phase2')

    def test_harness_contract_extension_minimal(self):
        import inspect
        from tianji_kb import engine
        from tianji_kb import golden
        from tianji_kb.operations import bazi_chart
        params = inspect.signature(bazi_chart.chart).parameters
        self.assertIn('dayun_shenfeng_measurement', params)
        self.assertIsNone(params['dayun_shenfeng_measurement']
                          .default)
        source = Path(golden.__file__).read_text(encoding='utf-8')
        self.assertIn("provider!=PROVIDERS[obj['domain']]", source)
        self.assertIn("provider!=contract['provider']", source)
        self.assertIn("provider.startswith('tianji_kb.operations.')",
                      source)
        with self.assertRaises(ValueError):
            engine.execute('bazi', {
                'value': '1958-08-15T19:30:00+08:00',
                'zone': 'Asia/Shanghai',
                'dayun_shenfeng_measurement': {'variant': 'x'}})
        with self.assertRaises(ValueError):
            bazi_chart.chart('戊戌', '庚申', '甲子', '甲戌',
                             dayun_shenfeng_measurement='not-a-dict')

    def test_governance_document_exists(self):
        doc = (ROOT / 'docs/product/'
               'GOVERNANCE_SHENFENG_EXPANSION.md')
        text = doc.read_text(encoding='utf-8')
        for header in ('## 0', '## 1', '## 2', '## 3', '## 4',
                       '## 5', '## 6', '## 7', '## 8'):
            self.assertIn(header, text)


if __name__ == '__main__':
    unittest.main()
