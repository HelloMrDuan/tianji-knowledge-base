"""TJ-018.3 batch 3 B-2 (E0339) public governance checks.

Public-side only (no sealed data): the batch record in
bazi_registration_governance is internally consistent, the
pattern-route-luren row flipped to registered with its rule/step
IDs, the maintained set shrank from 9 to 8, the route's public
disclosure fields flipped with it (evidence_binding, quote section
bindings, the registration limitation line), the zaqi and D-1
blocks stay pending, and the batch governance document exists.
Sealed-side behaviour (resolver binding, Golden fire, residue
carriage, forged-binding rejection) is pinned in
tests/test_phase2_baziluren.py.
"""
import re
import unittest
from pathlib import Path

from tianji_kb import bazi_pattern as pattern
from tianji_kb import bazi_registration_governance as gov
from tianji_kb import bazi_sanming_juan3_collation as juan3

ROOT = Path(__file__).resolve().parents[1]


def _row(item):
    rows = [r for r in gov.REGISTRATION_INVENTORY if r['item'] == item]
    assert len(rows) == 1
    return rows[0]


class LurenPromotionPublicTests(unittest.TestCase):
    def test_record_entities(self):
        record = gov.TJ0183_B2_RECORD
        self.assertEqual(record['event'], 'E0339')
        self.assertEqual(record['canonical_sections_added'],
                         ['bazi.section.s063', 'bazi.section.s064'])
        self.assertEqual(record['canonical_chapters_added'],
                         ['bazi.chapter.sanming_shiganlu',
                          'bazi.chapter.sanming_yangren'])
        self.assertEqual(record['canonical_terms_added'],
                         ['bazi.term.luren_route'])
        self.assertEqual(record['phase1_rules_added'], ['bazi.rule.r035'])
        self.assertEqual(record['phase2_rules_added'],
                         ['bazi.phase2.pattern_route'])
        self.assertEqual(len(record['golden_cases_added']), 9)

    def test_manifest_and_file_pins(self):
        record = gov.TJ0183_B2_RECORD
        self.assertEqual(record['snapshot_files_before'], 237)
        self.assertEqual(record['snapshot_files_after'], 237)
        self.assertEqual(record['snapshot_bytes_before'], 15964218)
        self.assertEqual(record['snapshot_bytes_after'], 16001603)
        self.assertEqual(
            record['manifest_sha256_before'],
            'c815dc4ed02a9b7d0bd1487c3e1ed4e39d0bc826659d4ff0fb7f8a37ff685cdf')
        self.assertEqual(
            record['manifest_sha256_after'],
            '15bd5a268d792c86072cf9ac51effb22ca5aefa004ea7ab44e7bbf44135682d5')
        self.assertEqual(sorted(record['sealed_files_changed']),
                         ['data/canonical/bazi/phase1_knowledge.json',
                          'data/canonical/bazi/phase2_execution.json',
                          'data/canonical/bazi/phase2_golden.json',
                          'data/coverage/phase1.json'])
        self.assertEqual(sorted(record['sealed_file_sha256_after']),
                         sorted(record['sealed_files_changed']))
        for digest in record['sealed_file_sha256_after'].values():
            self.assertTrue(re.fullmatch(r'[0-9a-f]{64}', digest))

    def test_route_row_registered(self):
        row = _row('pattern-route-luren')
        self.assertEqual(row['disposition'], 'registered')
        self.assertEqual(row['phase1_rule_id'], 'bazi.rule.r035')
        self.assertEqual(row['phase2_rule_id'], 'bazi.phase2.pattern_route')
        self.assertIsNone(row['unlock_path'])
        self.assertNotIn('reason_class', row)
        self.assertIn('bazi.section.s063', row['reason'])
        self.assertIn('bazi.section.s064', row['reason'])

    def test_flipped_and_maintained_sets(self):
        self.assertEqual(sorted(gov.FLIPPED_ITEMS),
                         sorted(['commanding_visible_support',
                                 'lu_visible_support',
                                 'pattern-route-luren',
                                 'pure_generating_support',
                                 'pure_generating_support_water',
                                 'pure_support_metal',
                                 'sanxing-branch-fact-v1']))
        self.assertEqual(len(gov.MAINTAINED_ITEMS), 8)
        self.assertNotIn('pattern-route-luren', gov.MAINTAINED_ITEMS)

    def test_route_disclosure_flipped(self):
        out = pattern.luren_route_lookup('甲', '寅')
        self.assertEqual(out['evidence_binding'],
                         'registered_phase1_phase2')
        self.assertTrue(any('registered_phase1_phase2' in line
                            for line in out['scope_limits']))
        self.assertFalse(any('pending_phase1_rule_registration' in line
                             for line in out['scope_limits']))
        # Route semantics unchanged by the flip.
        self.assertEqual(out['route'], 'luren_no_month_pattern')
        self.assertEqual(out['matched_via'], 'lu')
        self.assertEqual(out['determination']['status'], 'unresolved')
        self.assertIsNone(out['determination']['pattern'])
        self.assertEqual(out['borrowed_route']['status'], 'undetermined')

    def test_quote_section_bindings_completed(self):
        sections = {q['id']: q['source_section_id']
                    for q in pattern.LUREN_QUOTES}
        self.assertEqual(sections['renshi.luren_route_exclusion'],
                         'bazi.section.s054')
        self.assertEqual(sections['sanming.lu_sentence'],
                         'bazi.section.s063')
        self.assertEqual(sections['sanming.ren_doctrine'],
                         'bazi.section.s064')
        self.assertEqual(sections['sanming.ren_positions'],
                         'bazi.section.s064')

    def test_out_of_scope_blocks_stay_pending(self):
        self.assertEqual(_row('pattern-zaqi')['disposition'],
                         'maintained_pending')
        self.assertEqual(_row('ren-pattern-yin-true-v1')['disposition'],
                         'maintained_pending')
        self.assertEqual(_row('siling-yin-pilot')['disposition'],
                         'maintained_pending')

    def test_juan3_takeover_note(self):
        note = juan3.LUREN_PROMOTION_TAKEOVER
        self.assertEqual(note['event'], 'E0339')
        self.assertIn('bazi.section.s063', note['statement'])

    def test_governance_document_exists(self):
        doc = ROOT / 'docs/product/TJ0183_LUREN_PROMOTION.md'
        self.assertTrue(doc.is_file())
        text = doc.read_text(encoding='utf-8')
        for marker in ('E0339', 'bazi.rule.r035',
                       'bazi.phase2.pattern_route', 'bazi.section.s063',
                       'bazi.section.s064', 'seq 450'):
            self.assertIn(marker, text)


if __name__ == '__main__':
    unittest.main()
