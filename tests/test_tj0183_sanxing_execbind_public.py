"""TJ-018.3 batch 1 (E0333) sanxing execution binding: public pins.

Public CI (no sealed snapshot needed). The sealed-side registration
and execution are verified in the assembled acceptance by
tests/test_phase2_bazisanxing.py; this suite pins the
public record of the batch:

- TJ0183_EXECBIND_RECORD is internally consistent (rule / step /
  golden ids, the six-quote definitional subset mirrored against
  the adjudication register's group-table citation union, sealed
  files changed, manifest pins before/after);
- the sanxing inventory row flipped to registered with the r031 /
  branch_punishment_facts ids, the flipped set grows to three and
  the maintained set shrinks to twelve (status migration, pinned
  here and in the S5 / P1 suites);
- the implementation module's SLICE_REGISTRATION flipped
  (evidence_binding registered, phase2_rule filled) while
  sufficient_rule stays None and research_only / public / ai stay
  closed; the E0267 adjudicated SLICE_SPEC stays verbatim --
  the batch's takeover is an append-only record
  (EXECUTION_BINDING_TAKEOVER), never an edit of the adjudication;
- the engine gate rejects the flag without research mode and the
  chart provider rejects a non-boolean flag (both fail before any
  sealed data is touched);
- the governance document exists and names the registration, the
  subset and both manifest pins; no sealed section text leaks
  into the public record files.
"""
import re
import unittest
from pathlib import Path

from tianji_kb import bazi_registration_governance as gov
from tianji_kb import bazi_sanxing_fact_adjudication as adj
from tianji_kb import bazi_sanxing_facts as impl
from tianji_kb.engine import execute
from tianji_kb.operations.bazi_chart import chart

ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / 'docs' / 'product' / 'TJ0183_SANXING_EXECUTION_BINDING.md'
LEAK_PROBE = '无礼生旺主人威肃靣无和气气强性暴'
CASE_IDS = [
    'bazi.sanxing-fact-chou-wei-partial-no-edges',
    'bazi.sanxing-fact-yin-shen-only',
    'bazi.sanxing-fact-group2-full',
    'bazi.sanxing-fact-group3-full',
    'bazi.sanxing-fact-zi-mao-bidirectional',
    'bazi.sanxing-fact-self-chen-double',
    'bazi.sanxing-fact-g6b-self-you-triple',
    'bazi.sanxing-fact-empty-self-singles',
    'bazi.sanxing-fact-zi-mao-multi-pillar',
    'bazi.sanxing-fact-group2-partial-with-edge',
]
SUBSET = ['sm3.enum_opening', 'sm3.enum_group4_partial',
          'sm3.summary_groups', 'sm3.counting_method',
          'sm3.wuen_core', 'sm3.zixing_definition']


def _sanxing_row():
    rows = [r for r in gov.REGISTRATION_INVENTORY
            if r['item'] == 'sanxing-branch-fact-v1']
    assert len(rows) == 1
    return rows[0]


class RecordConsistencyTests(unittest.TestCase):
    def test_record_entities(self):
        record = gov.TJ0183_EXECBIND_RECORD
        self.assertEqual(record['event'], 'E0333')
        self.assertEqual(record['phase1_rules_added'],
                         ['bazi.rule.r031'])
        self.assertEqual(record['phase2_rules_added'],
                         ['bazi.phase2.branch_punishment_facts'])
        self.assertEqual(record['golden_cases_added'], CASE_IDS)
        self.assertEqual(record['source_refs_subset'], SUBSET)

    def test_subset_is_group_table_citation_union(self):
        union = set()
        for group in adj.GROUP_TABLE['groups']:
            union.update(group['evidence_refs'])
        union.update(adj.GROUP_TABLE['self_punishment']
                     ['evidence_refs'])
        self.assertEqual(union, set(SUBSET))

    def test_manifest_and_file_pins(self):
        record = gov.TJ0183_EXECBIND_RECORD
        self.assertEqual(record['snapshot_files_before'], 237)
        self.assertEqual(record['snapshot_files_after'], 237)
        self.assertEqual(record['snapshot_bytes_before'], 15902169)
        self.assertEqual(record['snapshot_bytes_after'], 15922702)
        self.assertEqual(
            record['manifest_sha256_before'],
            '305e20be96a38b614495236f8c3252cf7e21c6d1635a5a29bce1c299b746526c')
        self.assertEqual(
            record['manifest_sha256_after'],
            'b93e4b97830ff15aca1a9e77847796e5ddd5cb7e1f3cd6512db20a358c159622')
        self.assertEqual(sorted(record['sealed_files_changed']),
                         ['data/canonical/bazi/phase1_knowledge.json',
                          'data/canonical/bazi/phase2_execution.json',
                          'data/canonical/bazi/phase2_golden.json',
                          'data/coverage/phase1.json'])
        self.assertEqual(sorted(record['sealed_file_sha256_after']),
                         sorted(record['sealed_files_changed']))
        for digest in record['sealed_file_sha256_after'].values():
            self.assertTrue(re.fullmatch(r'[0-9a-f]{64}', digest))


class InventoryFlipTests(unittest.TestCase):
    def test_sanxing_row_registered(self):
        row = _sanxing_row()
        self.assertEqual(row['disposition'], 'registered')
        self.assertEqual(row['phase1_rule_id'], 'bazi.rule.r031')
        self.assertEqual(row['phase2_rule_id'],
                         'bazi.phase2.branch_punishment_facts')
        self.assertIsNone(row['unlock_path'])
        self.assertIn('bazi.section.s060', row['reason'])

    def test_flipped_and_maintained_sets(self):
        # E0335 (TJ-018.3 batch 2): lu / metal / water flipped as
        # well; the sanxing row's own state is unchanged.
        # E0339 (TJ-018.3 B-2): pattern-route-luren flipped too.
        # E0342: pattern-zaqi flipped too (seven maintained).
        # E0344: ren-pattern-yin-true-v1 flipped too (six
        # maintained).
        self.assertEqual(sorted(gov.FLIPPED_ITEMS),
                         ['commanding_visible_support',
                          'lu_visible_support',
                          'pattern-route-luren',
                          'pattern-zaqi',
                          'pure_generating_support',
                          'pure_generating_support_water',
                          'pure_support_metal',
                          'ren-pattern-yin-true-v1',
                          'sanxing-branch-fact-v1'])
        self.assertNotIn('sanxing-branch-fact-v1',
                         gov.MAINTAINED_ITEMS)
        self.assertEqual(len(gov.MAINTAINED_ITEMS), 6)


class DisclosureFlipTests(unittest.TestCase):
    def test_slice_registration_flipped(self):
        reg = impl.SLICE_REGISTRATION
        self.assertEqual(reg['evidence_binding'],
                         'registered_phase1_phase2')
        self.assertEqual(reg['phase2_rule'],
                         'bazi.phase2.branch_punishment_facts')
        self.assertIsNone(reg['sufficient_rule'])
        self.assertIsNone(reg['scenario_wiring'])
        self.assertTrue(reg['research_only'])
        self.assertFalse(reg['public_enabled'])
        self.assertFalse(reg['ai_enabled'])
        self.assertFalse(reg['concept_semantics_changed'])

    def test_adjudication_spec_verbatim_takeover_appended(self):
        # E0267's adjudicated record is history: not one field moves.
        reg = adj.SLICE_SPEC['registration']
        self.assertTrue(reg['evidence_binding'].startswith(
            'pending_phase1_registration'))
        self.assertIsNone(reg['sufficient_rule'])
        self.assertIn('不建 Phase2 规则',
                      adj.SLICE_SPEC['consumption_boundaries'][0])
        self.assertIn('独立函数', adj.SLICE_SPEC['placement_decision'])
        # The batch's takeover is a separate append-only record.
        take = adj.EXECUTION_BINDING_TAKEOVER
        self.assertEqual(take['takeover_event'], 'E0333')
        self.assertEqual(take['adjudication_event'], 'E0267')
        self.assertIn('bazi.phase2.branch_punishment_facts',
                      take['placement'])
        self.assertEqual(len(take['consumption_boundaries_takeover']),
                         4)


class GateTests(unittest.TestCase):
    PILLARS = {'year_ganzhi': '丙寅', 'month_ganzhi': '癸巳',
               'day_ganzhi': '戊午', 'hour_ganzhi': '庚申'}

    def test_engine_gate_rejects_without_research_mode(self):
        with self.assertRaises(ValueError):
            execute('bazi', dict(self.PILLARS,
                                 include_punishment_facts=True))

    def test_chart_rejects_non_bool_flag(self):
        with self.assertRaises(ValueError):
            chart(**self.PILLARS, include_punishment_facts='yes')


class DocumentAndLeakTests(unittest.TestCase):
    def test_document_names_registration_subset_and_pins(self):
        text = DOC.read_text(encoding='utf-8')
        for needle in ('bazi.rule.r031',
                       'bazi.phase2.branch_punishment_facts',
                       'sm3.enum_opening', 'sm3.zixing_definition',
                       '305e20be', 'b93e4b97',
                       'registered_phase1_phase2'):
            self.assertIn(needle, text)

    def test_no_sealed_section_text_in_public_records(self):
        gov_text = (ROOT / 'src' / 'tianji_kb'
                    / 'bazi_registration_governance.py').read_text(
                        encoding='utf-8')
        doc_text = DOC.read_text(encoding='utf-8')
        self.assertNotIn(LEAK_PROBE, gov_text)
        self.assertNotIn(LEAK_PROBE, doc_text)


if __name__ == '__main__':
    unittest.main()
