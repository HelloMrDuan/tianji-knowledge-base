"""Governance tiaohou Canonical design adjudication (E0350),
public side.

DESIGN ONLY batch: the tiaohou-qiongtong-v1 Canonical build-out
(new classic bazi.classic.qiongtong, 11 chapters, 110 sections,
one term, ten per-stem Phase1 rules, one Phase2 step) is designed
and adjudicated in docs/product/TIAOHOU_CANONICAL_DESIGN.md
(D-T1..D-T6) and recorded as TIAOHOU_DESIGN_RECORD, but NOTHING is
implemented: the registry row stays maintained_pending /
canonical_evidence_absent, no Canonical entity exists, and the
tiaohou module still reports
evidence_binding=pending_phase1_rule_registration.

These tests pin exactly that public (no-sealed-data) side: the
design record on file with its planned designations, the registry
state unchanged, and the design document on file carrying the
adjudicated headings and identifiers. Implementation belongs to a
later batch; if a future change flips the row or implements the
design, this test must be migrated by that batch, not loosened.

E0351 design revision (append-only section 10 of the design
document): the implementation batch's stage-1 review stopped on a
hard conflict -- the 丙×卯 entry span [8668,9025), built verbatim
under D-T2, carries 「从化格」 at snapshot char 8863 (a
case-discussion sentence, not a bound citation), which the sealed
hehua section keyword invariant bars from every section text.
The parent adjudication adopted remedy A (window section): the
entry's planned section bazi.section.s099 takes the window
[8668,8852), the remainder [8853,9025) is registered as unbuilt
text, refs exactness (丙 16, total 120) is unchanged, and the
implementation/closeout events were reallocated to E0352/E0353.
The revision changes no registry state either; the pins below
cover the revised planned fields on top of the E0350 pins.

E0352 migration (implementation batch): the design above is now
implemented exactly as adjudicated -- the registry row flipped
to registered (Phase1 bazi.rule.r042 + additional r043-r051,
Phase2 bazi.phase2.tiaohou_assessment) and the module reports
evidence_binding=registered_phase1_phase2. Per this file's own
instruction, the two state pins below were MIGRATED to the
post-implementation state (not loosened): the design record
itself is a historical adjudication record and stays pinned
verbatim, and the design document remains on file unchanged.
The implementation-side pins live in
tests/test_governance_tiaohou_promotion_public.py.
"""
import unittest
from pathlib import Path

from tianji_kb import bazi_registration_governance as gov
from tianji_kb import bazi_tiaohou as th

ROOT = Path(__file__).resolve().parents[1]
RECORD = gov.TIAOHOU_DESIGN_RECORD
DOC = ROOT / 'docs' / 'product' / 'TIAOHOU_CANONICAL_DESIGN.md'


def _row(item):
    return next(r for r in gov.REGISTRATION_INVENTORY
                if r['item'] == item)


class TiaohouDesignPublicTests(unittest.TestCase):
    def test_design_record_identity(self):
        self.assertEqual(RECORD['event'], 'E0350')
        self.assertEqual(RECORD['date'], '2026-11-01')
        self.assertEqual(RECORD['variant'], 'tiaohou-qiongtong-v1')
        self.assertEqual(RECORD['document'],
                         'docs/product/TIAOHOU_CANONICAL_DESIGN.md')
        self.assertEqual(RECORD['implementation_status'],
                         'design_only_not_implemented')
        self.assertEqual(RECORD['design_decisions'],
                         ['D-T1', 'D-T2', 'D-T3', 'D-T4', 'D-T5',
                          'D-T6'])

    def test_design_record_planned_designations(self):
        self.assertEqual(RECORD['planned_classic_id'],
                         'bazi.classic.qiongtong')
        self.assertEqual(RECORD['planned_classic_body_stage'],
                         'quarantine')
        self.assertEqual(RECORD['planned_chapter_count'], 11)
        self.assertEqual(RECORD['planned_section_count'], 110)
        self.assertEqual(RECORD['planned_entry_section_count'],
                         109)
        self.assertEqual(RECORD['planned_anchor_section_count'],
                         1)
        self.assertEqual(RECORD['planned_first_section_id'],
                         'bazi.section.s075')
        self.assertEqual(RECORD['planned_last_section_id'],
                         'bazi.section.s184')
        self.assertEqual(RECORD['planned_term_id'],
                         'bazi.term.tiaohou')
        self.assertEqual(RECORD['planned_phase1_rule_count'], 10)
        self.assertEqual(RECORD['planned_first_phase1_rule_id'],
                         'bazi.rule.r042')
        self.assertEqual(RECORD['planned_last_phase1_rule_id'],
                         'bazi.rule.r051')
        self.assertEqual(RECORD['planned_phase1_refs_total'], 120)
        self.assertEqual(RECORD['planned_phase2_step_id'],
                         'bazi.phase2.tiaohou_assessment')
        self.assertEqual(RECORD['measured_entry_count'], 119)
        self.assertEqual(RECORD['measured_distinct_span_count'],
                         109)
        self.assertEqual(RECORD['measured_distinct_refs'], 120)
        self.assertEqual(RECORD['measured_absent_grid'], ['乙×丑'])
        self.assertEqual(RECORD['golden_criteria_planned'],
                         ['G1', 'G2', 'G3', 'G4', 'G5', 'G6'])

    def test_design_revision_e0351_on_file(self):
        self.assertEqual(RECORD['design_revision_event'], 'E0351')
        self.assertEqual(RECORD['design_revision_date'],
                         '2026-11-01')
        self.assertEqual(RECORD['design_revision_document_section'],
                         '10')
        self.assertEqual(RECORD['planned_window_section_count'], 1)
        self.assertEqual(len(RECORD['planned_window_sections']), 1)
        win = RECORD['planned_window_sections'][0]
        self.assertEqual(win['entry'], '丙×卯')
        self.assertEqual(win['section_id'], 'bazi.section.s099')
        self.assertEqual(win['form'], 'window')
        self.assertEqual(win['entry_span'], [8668, 9025])
        self.assertEqual(win['window_span'], [8668, 8852])
        self.assertEqual(win['excluded_span'], [8853, 9025])
        self.assertEqual(win['hit_char'], 8863)
        self.assertEqual(win['hit_keyword'], '化格')
        # The revision leaves the planned totals untouched.
        self.assertEqual(RECORD['planned_section_count'], 110)
        self.assertEqual(RECORD['planned_entry_section_count'],
                         109)
        self.assertEqual(RECORD['planned_phase1_refs_total'], 120)
        self.assertEqual(RECORD['measured_unconsumed_gap_chars'],
                         4744)
        self.assertEqual(
            RECORD['measured_unconsumed_gap_chars_naive_sum'],
            4884)
        self.assertEqual(RECORD['implementation_event_planned'],
                         'E0352')
        self.assertEqual(RECORD['closeout_event_planned'],
                         'E0353')
        text = DOC.read_text(encoding='utf-8')
        self.assertIn('## 10 设计修订（E0351，append-only 补记）',
                      text)
        for marker in ('bazi.section.s099', '[8668,8852)',
                       '[8853,9025)', '从化格', '解法 A',
                       'E0352', 'E0353', '4,744'):
            self.assertIn(marker, text)

    def test_registry_row_flipped_by_e0352(self):
        # Migrated by the E0352 implementation batch (see module
        # docstring): the design is implemented, so the row is
        # registered with the design's planned designations.
        row = _row('tiaohou-qiongtong-v1')
        self.assertEqual(row['disposition'], 'registered')
        self.assertNotIn('reason_class', row)
        self.assertEqual(row['phase1_rule_id'], 'bazi.rule.r042')
        self.assertEqual(row['additional_phase1_rule_ids'],
                         ['bazi.rule.r043', 'bazi.rule.r044',
                          'bazi.rule.r045', 'bazi.rule.r046',
                          'bazi.rule.r047', 'bazi.rule.r048',
                          'bazi.rule.r049', 'bazi.rule.r050',
                          'bazi.rule.r051'])
        self.assertEqual(row['phase2_rule_id'],
                         'bazi.phase2.tiaohou_assessment')
        self.assertIsNone(row['unlock_path'])
        self.assertIn('tiaohou-qiongtong-v1', gov.FLIPPED_ITEMS)
        self.assertEqual(
            gov.MAINTAINED_ITEMS,
            ['dayun-compose', 'dayun-timeline-view',
             'siling-yin-pilot'])

    def test_module_semantics_unchanged(self):
        self.assertEqual(th.VARIANT, 'tiaohou-qiongtong-v1')
        self.assertEqual(len(th.ENTRIES), 119)
        self.assertEqual(th.ABSENT_IN_SOURCE,
                         frozenset({('乙', '丑')}))
        visible = ('甲', '丙', '甲', '戊')
        hidden = (('戊', '丙', '甲'), (), (), ())
        absent = th.tiaohou_lookup('乙', '丑', visible, hidden)
        self.assertEqual(absent['status'], 'not_applicable')
        self.assertEqual(absent['reason'],
                         'entry_absent_in_source')
        # E0352: the binding disclosure flipped with the
        # registration; lookup semantics are unchanged.
        self.assertEqual(absent['evidence_binding'],
                         'registered_phase1_phase2')
        matched = th.tiaohou_lookup('甲', '寅', visible, hidden)
        self.assertEqual(matched['status'], 'matched')
        self.assertEqual(matched['evidence_binding'],
                         'registered_phase1_phase2')

    def test_design_document_on_file(self):
        text = DOC.read_text(encoding='utf-8')
        for heading in ('## 0 授权与范围',
                        '## 1 现状追踪结果（只读实测）',
                        '## 2 经典建制形态定稿',
                        '## 3 建节计划定稿',
                        '## 4 绑定设计定稿',
                        '## 5 Golden 设计定稿（validated 证据形态，D-T6）',
                        '## 6 注册翻转判据定稿',
                        '## 7 实施批切分与硬验收清单',
                        '## 8 风险、未决项与用户裁定界限',
                        '## 9 本批产出与未实施声明'):
            self.assertIn(heading, text)
        for marker in ('bazi.classic.qiongtong',
                       'bazi.section.s075', 'bazi.section.s184',
                       'bazi.rule.r042', 'bazi.rule.r051',
                       'bazi.term.tiaohou',
                       'bazi.phase2.tiaohou_assessment',
                       'D-T1', 'D-T6', 'G1', 'G6'):
            self.assertIn(marker, text)
        self.assertIn('未实施', text)


if __name__ == '__main__':
    unittest.main()
