"""TJ-018.3 batch 2 (E0335) public governance checks.

Public-side only (no sealed data): the batch record in
bazi_registration_governance is internally consistent, the three
inventory rows flipped to registered with their rule/step IDs, the
maintained set shrank from 12 to 9, the F3 form register's
evidence_binding flipped with them, and the batch governance
document exists. Sealed-side behaviour (resolver binding, Golden
fire, Ding/gap machine assertions) is pinned in
tests/test_phase2_baziganzhi.py.
"""
import re
import unittest
from pathlib import Path

from tianji_kb import bazi_fire_si_yin_morphology as fire_si_yin
from tianji_kb import bazi_registration_governance as gov

ROOT = Path(__file__).resolve().parents[1]

ROWS = {
    'lu_visible_support': ('bazi.rule.r032',
                           'bazi.phase2.strength_lu_visible_support'),
    'pure_support_metal': ('bazi.rule.r033',
                           'bazi.phase2.strength_pure_support_metal'),
    'pure_generating_support_water': (
        'bazi.rule.r034',
        'bazi.phase2.strength_pure_generating_support_water'),
}


def _row(item):
    rows = [r for r in gov.REGISTRATION_INVENTORY if r['item'] == item]
    assert len(rows) == 1
    return rows[0]


class GanzhiExecBindPublicTests(unittest.TestCase):
    def test_record_entities(self):
        record = gov.TJ0183_P2_RECORD
        self.assertEqual(record['event'], 'E0335')
        self.assertEqual(record['batch'], 'TJ-018.3 批二 卷二干支三规则实施批')
        self.assertEqual(record['canonical_sections_added'],
                         ['bazi.section.s061', 'bazi.section.s062'])
        self.assertEqual(record['canonical_chapters_added'],
                         ['bazi.chapter.sanming_tianganshengsi',
                          'bazi.chapter.sanming_wangxiangjisheng'])
        self.assertEqual(record['phase1_rules_added'],
                         ['bazi.rule.r032', 'bazi.rule.r033', 'bazi.rule.r034'])
        self.assertEqual(record['phase2_rules_added'],
                         [step for _, step in ROWS.values()])
        self.assertEqual(
            record['golden_cases_added'],
            ['bazi.strength-ganzhi-lu-positive',
             'bazi.strength-ganzhi-water-positive',
             'bazi.strength-ganzhi-metal-negative-xin-clashed-roots',
             'bazi.strength-ganzhi-metal-negative-geng-stem-combination'])

    def test_manifest_and_file_pins(self):
        record = gov.TJ0183_P2_RECORD
        self.assertEqual(record['snapshot_files_before'], 237)
        self.assertEqual(record['snapshot_files_after'], 237)
        self.assertEqual(record['snapshot_bytes_before'], 15922702)
        self.assertEqual(record['snapshot_bytes_after'], 15964218)
        self.assertEqual(
            record['manifest_sha256_before'],
            'b93e4b97830ff15aca1a9e77847796e5ddd5cb7e1f3cd6512db20a358c159622')
        self.assertEqual(
            record['manifest_sha256_after'],
            'c815dc4ed02a9b7d0bd1487c3e1ed4e39d0bc826659d4ff0fb7f8a37ff685cdf')
        self.assertEqual(sorted(record['sealed_files_changed']),
                         ['data/canonical/bazi/phase1_knowledge.json',
                          'data/canonical/bazi/phase2_execution.json',
                          'data/canonical/bazi/phase2_golden.json',
                          'data/coverage/phase1.json'])
        self.assertEqual(sorted(record['sealed_file_sha256_after']),
                         sorted(record['sealed_files_changed']))
        for digest in record['sealed_file_sha256_after'].values():
            self.assertTrue(re.fullmatch(r'[0-9a-f]{64}', digest))

    def test_three_rows_registered(self):
        for item, (rule_id, step_id) in ROWS.items():
            row = _row(item)
            self.assertEqual(row['disposition'], 'registered')
            self.assertEqual(row['phase1_rule_id'], rule_id)
            self.assertEqual(row['phase2_rule_id'], step_id)
            self.assertIsNone(row['unlock_path'])
            self.assertNotIn('reason_class', row)
            self.assertIn('bazi.section.s061', row['reason'])

    def test_flipped_and_maintained_sets(self):
        # E0339 (TJ-018.3 B-2): pattern-route-luren flipped as well.
        # E0342: pattern-zaqi flipped as well.
        # E0344: ren-pattern-yin-true-v1 flipped as well (six
        # maintained).
        # E0346: dayun-classical-variants flipped as well
        # (segmented; five maintained).
        # E0348: bingyao-shenfeng-v1 flipped too (four
        # maintained).
        self.assertEqual(sorted(gov.FLIPPED_ITEMS),
                         sorted(['bingyao-shenfeng-v1', 'commanding_visible_support',
                                 'dayun-classical-variants',
                                 'lu_visible_support',
                                 'pattern-route-luren',
                                 'pattern-zaqi',
                                 'pure_generating_support',
                                 'pure_generating_support_water',
                                 'pure_support_metal',
                                 'ren-pattern-yin-true-v1',
                                 'sanxing-branch-fact-v1', 'tiaohou-qiongtong-v1']))
        self.assertEqual(len(gov.MAINTAINED_ITEMS), 3)  # E0352: tiaohou flipped
        for item in ROWS:
            self.assertNotIn(item, gov.MAINTAINED_ITEMS)

    def test_form_register_binding_flipped(self):
        binding = fire_si_yin.FORM_BING_SI['evidence_binding']
        self.assertTrue(binding.startswith('registered_phase1_phase2'))
        self.assertIn('bazi.rule.r032', binding)
        # The F4 changsheng form stays pending (out of batch scope).
        self.assertEqual(fire_si_yin.FORM_BING_YIN['evidence_binding'],
                         'pending_phase1_rule_registration')

    def test_governance_document_exists(self):
        doc = ROOT / 'docs/product/TJ0183_GANZHI_EXECUTION_BINDING.md'
        self.assertTrue(doc.is_file())
        text = doc.read_text(encoding='utf-8')
        for marker in ('E0335', 'bazi.rule.r032', 'bazi.rule.r033',
                       'bazi.rule.r034', '负例见证集', 'framework_derived'):
            self.assertIn(marker, text)


if __name__ == '__main__':
    unittest.main()
