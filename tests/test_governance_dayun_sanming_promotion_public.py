"""Governance pending-8 audit third batch (E0346) public checks.

Public-side only (no sealed data): the batch record in
bazi_registration_governance is internally consistent, the
dayun-classical-variants row flipped to registered SEGMENTED
(Sanming segment r038/r039 with both Phase2 steps; the Shenfeng
segment stays pending inside the same row), the two inherited
rows were re-marked segmented_inherited_pending, the maintained
set shrank from 6 to 5, the classical module's public disclosure
fields flipped per segment (Sanming outputs registered, Shenfeng
conversion still pending), the fifteen Sanming quotes were
re-pointed to the applied-text source with Canonical section ids
(quote texts byte-identical), the output contract is unchanged
(intervals only, no age keys, zero-jie refusal), the chart
harness input contract extension is minimal (two gated kwargs,
defaults off, engine research gates and cross-check rejections
pinned, golden.py provider pinning source strings unchanged),
and the batch governance document exists. Sealed-side behaviour
(Canonical sections s068/s069/s070, rule quote binding, Golden
fire of the registered steps, forged-quote rejection, rollback)
is pinned in tests/test_phase2_bazidayunsanming.py; the stage-1
collation register is pinned in
tests/test_tj0183_e0346_dayun_sanming_collation.py.
"""
import re
import unittest
from pathlib import Path

from tianji_kb import bazi_dayun_classical as dc
from tianji_kb import bazi_dayun_compose as compose
from tianji_kb import bazi_dayun_timeline_view as view
from tianji_kb import bazi_registration_governance as gov

ROOT = Path(__file__).resolve().parents[1]

SANMING_QUOTE_SECTIONS = {
    'ratio_statement': 'bazi.section.s068',
    'ratio_derivation': 'bazi.section.s068',
    'direction_rule': 'bazi.section.s068',
    'worked_example': 'bazi.section.s068',
    'worked_example_check': 'bazi.section.s068',
    'anti_rounding': 'bazi.section.s068',
    'zero_borrow_definition': 'bazi.section.s068',
    'zero_borrow_example': 'bazi.section.s068',
    'handover_example': 'bazi.section.s068',
    'handover_decade': 'bazi.section.s068',
    'handover_approx': 'bazi.section.s068',
    'vol11_direction_witness': 'bazi.section.s069',
    'vol11_ratio_witness': 'bazi.section.s069',
    'vol11_counting_divergence': 'bazi.section.s069',
    'vol11_direction_witness2': 'bazi.section.s070',
}
SHENFENG_QUOTE_IDS = {'sf_heading_yang', 'sf_ex1', 'sf_ex2',
                      'sf_heading_yin', 'sf_ex3', 'sf_ex4'}


def _row(item):
    rows = [r for r in gov.REGISTRATION_INVENTORY if r['item'] == item]
    assert len(rows) == 1
    return rows[0]


class DayunSanmingPromotionPublicTests(unittest.TestCase):
    def test_record_entities(self):
        record = gov.GOVERNANCE_DAYUN_SANMING_RECORD
        self.assertEqual(record['event'], 'E0346')
        self.assertEqual(record['canonical_chapters_added'],
                         ['bazi.chapter.sanming_lun_dayun',
                          'bazi.chapter.sanming_luoluozi_dayun_witness'])
        self.assertEqual(record['canonical_sections_added'],
                         ['bazi.section.s068', 'bazi.section.s069',
                          'bazi.section.s070'])
        self.assertEqual(record['canonical_terms_added'],
                         ['bazi.term.dayun_direction',
                          'bazi.term.dayun_handover'])
        self.assertEqual(record['phase1_rules_added'],
                         ['bazi.rule.r038', 'bazi.rule.r039'])
        self.assertEqual(record['phase2_rules_added'],
                         ['bazi.phase2.dayun_classical_direction',
                          'bazi.phase2.dayun_sanming_conversion'])
        self.assertEqual(len(record['golden_cases_added']), 6)
        self.assertEqual(len(record['source_refs_subset']), 10)

    def test_record_snapshot_pins(self):
        record = gov.GOVERNANCE_DAYUN_SANMING_RECORD
        for value in (record['manifest_sha256_before'],
                      record['manifest_sha256_after']):
            self.assertTrue(re.fullmatch(r'[0-9a-f]{64}', value))
        self.assertNotEqual(record['manifest_sha256_before'],
                            record['manifest_sha256_after'])
        self.assertTrue(record['manifest_sha256_before'].startswith(
            '2fdcfaec3ffd5f3a'))
        self.assertEqual(record['snapshot_files_before'], 237)
        self.assertEqual(record['snapshot_files_after'], 237)
        self.assertGreater(record['snapshot_bytes_after'],
                           record['snapshot_bytes_before'])
        for digest in record['sealed_file_sha256_after'].values():
            self.assertTrue(re.fullmatch(r'[0-9a-f]{64}', digest))

    def test_segmented_row_flip(self):
        row = _row('dayun-classical-variants')
        self.assertEqual(row['disposition'], 'registered')
        self.assertEqual(row['phase1_rule_id'], 'bazi.rule.r038')
        self.assertEqual(row['phase2_rule_id'],
                         'bazi.phase2.dayun_classical_direction')
        self.assertEqual(row['additional_phase1_rule_ids'],
                         ['bazi.rule.r039'])
        self.assertEqual(row['additional_phase2_rule_ids'],
                         ['bazi.phase2.dayun_sanming_conversion'])
        self.assertIsNone(row['unlock_path'])
        self.assertNotIn('reason_class', row)
        self.assertIn('registered', row['segments']['sanming'])
        self.assertIn('maintained_pending', row['segments']['shenfeng'])
        for marker in ('bazi.section.s068', 'bazi.section.s069',
                       'bazi.section.s070', 'bazi.rule.r038',
                       'bazi.rule.r039'):
            self.assertIn(marker, row['reason'])

    def test_inherited_rows_remarked(self):
        for item in ('dayun-compose', 'dayun-timeline-view'):
            row = _row(item)
            self.assertEqual(row['disposition'], 'maintained_pending')
            self.assertEqual(row['reason_class'], 'inherited_pending')
            self.assertIn('segmented_inherited_pending', row['reason'])
            self.assertIn('神峰', row['unlock_path'])

    def test_flipped_and_maintained_sets(self):
        self.assertIn('dayun-classical-variants', gov.FLIPPED_ITEMS)
        self.assertEqual(len(gov.FLIPPED_ITEMS), 10)
        self.assertEqual(len(gov.MAINTAINED_ITEMS), 5)
        self.assertEqual(sorted(gov.MAINTAINED_ITEMS),
                         sorted(['tiaohou-qiongtong-v1', 'dayun-compose',
                                 'dayun-timeline-view',
                                 'bingyao-shenfeng-v1',
                                 'siling-yin-pilot']))

    def test_segment_disclosure_flips(self):
        direction = dc.classical_direction('甲子',
                                           traditional_role='male')
        self.assertEqual(direction['evidence_binding'],
                         'registered_phase1_phase2')
        self.assertTrue(dc.validate_classical_direction(direction))
        self.assertIsNone(direction['direction_rule_match'])
        self.assertFalse(direction['phase2_allowed'])
        converted = dc.sanming_convert_elapsed(453600)
        self.assertEqual(converted['evidence_binding'],
                         'registered_phase1_phase2')
        shenfeng = dc.shenfeng_convert_days(30, direction='forward')
        self.assertEqual(shenfeng['evidence_binding'],
                         'pending_phase1_rule_registration')

    def test_quote_repointing(self):
        by_id = {q['id']: q for q in dc.QUOTES}
        self.assertEqual(len(by_id), 21)
        for quote_id, section_id in SANMING_QUOTE_SECTIONS.items():
            quote = by_id[quote_id]
            self.assertEqual(quote['source_id'],
                             'bazi.source.sanmingtonghui-applied')
            self.assertEqual(quote['source_section_id'], section_id)
        for quote_id in SHENFENG_QUOTE_IDS:
            quote = by_id[quote_id]
            self.assertEqual(quote['source_id'], 'bazi.source.shenfeng')
            self.assertNotIn('source_section_id', quote)
        # The two PUA quotes keep their snapshot glyph and their
        # confirmed mapped reading (registration binds the applied
        # form held by the Canonical section, not a rewritten
        # public quote).
        for quote_id in ('handover_example', 'handover_decade'):
            quote = by_id[quote_id]
            self.assertIn(chr(0xED92), quote['quote'])
            self.assertIn('算', quote['mapped_reading_text'])
            self.assertNotIn(chr(0xED92),
                             quote['mapped_reading_text'])

    def test_output_contract_unchanged(self):
        direction = dc.classical_direction('甲子',
                                           traditional_role='female')
        self.assertEqual(direction['direction'], 'backward')
        converted = dc.sanming_convert_elapsed(0)
        self.assertEqual(converted['status'], 'unresolved')
        self.assertEqual(converted['reason'],
                         'zero_jie_boundary_convention_unreviewed')
        for out in (direction, converted):
            for key in out:
                self.assertNotIn('age', key)
        # Rounding is refused as an unresolved result carrying the
        # anti-rounding quote (now bound to the applied source).
        refused = dc.sanming_convert_elapsed(7200, rounding='year')
        self.assertEqual(refused['status'], 'unresolved')
        self.assertTrue(refused['reason'].startswith(
            "rounding 'year' refused"))
        self.assertEqual(refused['anti_rounding_quote']['source_id'],
                         'bazi.source.sanmingtonghui-applied')
        self.assertEqual(
            refused['anti_rounding_quote']['source_section_id'],
            'bazi.section.s068')
        zero_day = dc.shenfeng_convert_days(0, direction='forward')
        self.assertEqual(zero_day['status'], 'unresolved')
        self.assertEqual(zero_day['reason'],
                         'zero_day_count_not_exemplified_in_text')

    def test_compose_view_binding_remarked(self):
        self.assertEqual(compose._flags()['evidence_binding'],
                         'segmented_inherited_pending')
        self.assertEqual(view._flags()['evidence_binding'],
                         'segmented_inherited_pending')
        self.assertTrue(compose._flags()['research_only'])
        self.assertTrue(view._flags()['research_only'])

    def test_harness_contract_extension_minimal(self):
        import inspect
        from tianji_kb import engine
        from tianji_kb import golden
        from tianji_kb.operations import bazi_chart
        params = inspect.signature(bazi_chart.chart).parameters
        self.assertIn('dayun_classical_role', params)
        self.assertIsNone(params['dayun_classical_role'].default)
        self.assertIn('dayun_sanming_measurement', params)
        self.assertIsNone(params['dayun_sanming_measurement'].default)
        source = Path(golden.__file__).read_text(encoding='utf-8')
        self.assertIn("provider!=PROVIDERS[obj['domain']]", source)
        self.assertIn("provider!=contract['provider']", source)
        self.assertIn("provider.startswith('tianji_kb.operations.')",
                      source)
        with self.assertRaises(ValueError):
            engine.execute('bazi', {
                'value': '1958-08-15T19:30:00+08:00',
                'zone': 'Asia/Shanghai',
                'dayun_classical_role': 'male'})
        with self.assertRaises(ValueError):
            engine.execute('bazi', {
                'value': '1958-08-15T19:30:00+08:00',
                'zone': 'Asia/Shanghai',
                'dayun_sanming_measurement': {'variant': 'x'}})
        with self.assertRaises(ValueError):
            bazi_chart.chart('戊戌', '庚申', '甲子', '甲戌',
                             dayun_classical_role='other')
        with self.assertRaises(ValueError):
            bazi_chart.chart('戊戌', '庚申', '甲子', '甲戌',
                             dayun_sanming_measurement='not-a-dict')
        # The month/direction cross-checks run after the base
        # chart computation (which needs the sealed foundations),
        # so they are pinned in the sealed twin
        # (tests/test_phase2_bazidayunsanming.py).

    def test_governance_document_exists(self):
        doc = ROOT / 'docs' / 'product' / \
            'GOVERNANCE_DAYUN_SANMING_PROMOTION.md'
        self.assertTrue(doc.exists())


if __name__ == '__main__':
    unittest.main()
