"""Governance tiaohou Canonical construction (E0352), public side.

The tiaohou-qiongtong-v1 Canonical construction designed in
E0350/E0351 is implemented: classic bazi.classic.qiongtong
(body_stage=quarantine) with 11 chapters and 110 sections (anchor
s075 + entry sections s076-s184 by ascending span; the Bing-Mao
entry's section s099 is the adjudicated window section
[8668,8852), its tail [8853,9025) registered unbuilt), term
bazi.term.tiaohou anchored on the zonglun climate sentence, ten
per-stem Phase1 rules r042-r051 whose source_refs are exactly the
111 deduped main quotes plus the 9 deduped encoded branch quotes
(120 total), and the single Phase2 step
bazi.phase2.tiaohou_assessment, validated by 30 Golden cases
covering G1-G6. The registry row flipped to registered; the
lookup semantics and every computed value are unchanged apart
from the registration disclosures.

These tests pin the public (no-sealed-data) side of that flip:
the registry row and the implementation record, the flipped /
maintained sets, and the module's flipped disclosures. The
sealed side is pinned by tests/test_phase2_bazitiaohou.py.
"""
import unittest
from pathlib import Path

from tianji_kb import bazi_registration_governance as gov
from tianji_kb import bazi_tiaohou as th

ROOT = Path(__file__).resolve().parents[1]
RECORD = gov.GOVERNANCE_TIAOHOU_RECORD


def _row(item):
    return next(r for r in gov.REGISTRATION_INVENTORY
                if r['item'] == item)


class TiaohouPromotionPublicTests(unittest.TestCase):
    def test_registry_row_flipped(self):
        row = _row('tiaohou-qiongtong-v1')
        self.assertEqual(row['disposition'], 'registered')
        self.assertEqual(row['phase1_rule_id'], 'bazi.rule.r042')
        self.assertEqual(row['additional_phase1_rule_ids'],
                         [f'bazi.rule.r{i:03d}' for i in range(43, 52)])
        self.assertEqual(row['phase2_rule_id'],
                         'bazi.phase2.tiaohou_assessment')
        self.assertNotIn('reason_class', row)
        self.assertIsNone(row['unlock_path'])
        for marker in ('bazi.classic.qiongtong', 'bazi.section.s075',
                       'bazi.section.s099', 'bazi.term.tiaohou',
                       '120', 'GOVERNANCE_TIAOHOU_RECORD'):
            self.assertIn(marker, row['reason'])

    def test_flipped_and_maintained_sets(self):
        self.assertIn('tiaohou-qiongtong-v1', gov.FLIPPED_ITEMS)
        self.assertEqual(len(gov.FLIPPED_ITEMS), 12)
        self.assertEqual(gov.MAINTAINED_ITEMS,
                         ['dayun-compose', 'dayun-timeline-view',
                          'siling-yin-pilot'])

    def test_implementation_record(self):
        self.assertEqual(RECORD['event'], 'E0352')
        self.assertEqual(RECORD['date'], '2026-11-01')
        self.assertEqual(RECORD['document'],
                         'docs/product/GOVERNANCE_TIAOHOU_PROMOTION.md')
        self.assertEqual(RECORD['canonical_classics_added'],
                         ['bazi.classic.qiongtong'])
        self.assertEqual(len(RECORD['canonical_chapters_added']),
                         11)
        self.assertEqual(RECORD['canonical_chapters_added'][0],
                         'bazi.chapter.qiongtong_zonglun')
        self.assertEqual(RECORD['canonical_sections_added'],
                         [f'bazi.section.s{i:03d}'
                          for i in range(75, 185)])
        self.assertEqual(RECORD['canonical_terms_added'],
                         ['bazi.term.tiaohou'])
        self.assertEqual(RECORD['phase1_rules_added'],
                         [f'bazi.rule.r{i:03d}' for i in range(42, 52)])
        self.assertEqual(RECORD['phase2_rules_added'],
                         ['bazi.phase2.tiaohou_assessment'])
        self.assertEqual(len(RECORD['golden_cases_added']), 30)
        self.assertTrue(RECORD['harness_contract_extension']
                        .startswith('none'))
        self.assertEqual(
            RECORD['sealed_files_changed'],
            ['data/canonical/bazi/phase1_knowledge.json',
             'data/canonical/bazi/phase2_execution.json',
             'data/canonical/bazi/phase2_golden.json',
             'data/coverage/phase1.json',
             'data/product/knowledge_coverage.json'])
        self.assertEqual(RECORD['snapshot_files_before'], 237)
        self.assertEqual(RECORD['snapshot_files_after'], 237)
        self.assertEqual(
            RECORD['manifest_sha256_before'],
            '380bb73e34babc30bcc80e5ad7f296175f6be206af6a77f1abb4a07b94da654b')

    def test_design_record_stays_a_design_record(self):
        # The E0350/E0351 design record is a historical
        # adjudication record; the implementation does not
        # rewrite it.
        design = gov.TIAOHOU_DESIGN_RECORD
        self.assertEqual(design['implementation_status'],
                         'design_only_not_implemented')
        self.assertEqual(design['implementation_event_planned'],
                         'E0352')
        self.assertEqual(design['closeout_event_planned'],
                         'E0353')

    def test_module_disclosure_flipped(self):
        text = (ROOT / 'src' / 'tianji_kb' / 'bazi_tiaohou.py'
                ).read_text('utf-8')
        self.assertNotIn('pending_phase1_rule_registration', text)
        self.assertIn('registered_phase1_phase2', text)
        self.assertIn('bazi.rule.r042', th.LIMITATIONS[-1])
        visible = ('甲', '丙', '甲', '戊')
        hidden = (('戊', '丙', '甲'), (), (), ())
        matched = th.tiaohou_lookup('甲', '寅', visible, hidden)
        self.assertEqual(matched['evidence_binding'],
                         'registered_phase1_phase2')
        absent = th.tiaohou_lookup('乙', '丑', visible, hidden)
        self.assertEqual(absent['evidence_binding'],
                         'registered_phase1_phase2')
        self.assertEqual(absent['reason'],
                         'entry_absent_in_source')

    def test_entries_carry_section_bindings(self):
        self.assertEqual(len(th.ENTRIES), 119)
        ids = [e['source_section_id'] for e in th.ENTRIES]
        self.assertTrue(all(i.startswith('bazi.section.s')
                            for i in ids))
        # 109 distinct sections for 119 entries (shared spans).
        self.assertEqual(len(set(ids)), 109)
        bing_mao = next(e for e in th.ENTRIES
                        if e['day_master'] == '丙'
                        and e['month_branch'] == '卯')
        self.assertEqual(bing_mao['source_section_id'],
                         'bazi.section.s099')
        spans = [(e['section']['char_start'],
                  e['section']['char_end']) for e in th.ENTRIES]
        ordered = list(dict.fromkeys(
            e['source_section_id'] for e in
            sorted(th.ENTRIES,
                   key=lambda e: (e['section']['char_start'],
                                  e['section']['char_end']))))
        self.assertEqual(ordered,
                         [f'bazi.section.s{i:03d}'
                          for i in range(76, 185)])
        self.assertEqual(spans[0], (1300, 1362))


if __name__ == '__main__':
    unittest.main()
