"""TJ-018.3 P1 三刑 Canonical 建节：公开侧治理登记钉值。

Public CI (no sealed snapshot needed). The sealed-side section
building itself is verified in the assembled acceptance by
tests/test_tj0183_p1_sanxing_promotion_sealed.py; this suite pins
the public governance record and the fact layer's unchanged
disclosure:

- TJ0183_P1_RECORD is internally consistent (built entities, the
  11 bound quote ids mirrored against the 018-B collation
  register, manifest pins, the four changed sealed files);
- the sanxing slice entered the registration inventory as
  maintained_pending / execution_binding_structure, and the
  flipped set is unchanged (no silent registration) -- as of
  P1; E0333 (execution-binding batch 1) later flipped the row
  and the slice registration, pinned in the updated tests
  below and in test_tj0183_sanxing_execbind_public.py;
- the fact layer's SLICE_REGISTRATION and the adjudication
  register's SLICE_SPEC.registration are verbatim unchanged
  (evidence_binding pending, phase2_rule / sufficient_rule None)
  -- as of P1; E0333 flipped only the implementation module's
  SLICE_REGISTRATION, the adjudicated SLICE_SPEC stays verbatim;
- the governance document exists and names the built entities,
  both manifest pins and the structural gap;
- no sealed Canonical section text leaks into the public record
  files (a distinctive 24-character string from the built
  section's exposition appears in neither the governance
  register nor the governance document).
"""
import re
import unittest
from pathlib import Path

from tianji_kb import bazi_registration_governance as gov
from tianji_kb import bazi_sanming_juan2_sanxing_collation as cj
from tianji_kb import bazi_sanxing_fact_adjudication as adj
from tianji_kb import bazi_sanxing_facts as impl

ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / 'docs' / 'product' / 'TJ0183_P1_SANXING_CANONICAL_PROMOTION.md'
LEAK_PROBE = '无礼生旺主人威肃靣无和气气强性暴'


def _sanxing_row():
    rows = [r for r in gov.REGISTRATION_INVENTORY
            if r['item'] == 'sanxing-branch-fact-v1']
    assert len(rows) == 1
    return rows[0]


class RecordConsistencyTests(unittest.TestCase):
    def test_record_entities(self):
        record = gov.TJ0183_P1_RECORD
        self.assertEqual(record['event'], 'E0329')
        self.assertEqual(record['canonical_chapters_added'],
                         ['bazi.chapter.sanming_sanxing'])
        self.assertEqual(record['canonical_sections_added'],
                         ['bazi.section.s060'])
        self.assertEqual(record['canonical_terms_added'],
                         ['bazi.term.branch_punishments'])
        self.assertEqual(record['classic_source_ids_added'],
                         {'bazi.classic.sanming_tonghui':
                          ['bazi.source.sanmingtonghui',
                           'bazi.source.sanmingtonghui-applied']})
        self.assertEqual(len(record['public_config_registrations']),
                         2)
        self.assertEqual(record['phase1_rules_added'], [])
        self.assertEqual(record['phase2_rules_added'], [])
        self.assertEqual(record['golden_cases_added'], [])

    def test_quotes_verified_mirror_collation_register(self):
        self.assertEqual(
            gov.TJ0183_P1_RECORD['quotes_verified'],
            [q['id'] for q in cj.COLLATION_QUOTES])
        self.assertEqual(len(gov.TJ0183_P1_RECORD['quotes_verified']),
                         11)

    def test_manifest_and_file_pins(self):
        record = gov.TJ0183_P1_RECORD
        self.assertEqual(record['snapshot_files_before'], 237)
        self.assertEqual(record['snapshot_files_after'], 237)
        self.assertEqual(record['snapshot_bytes_before'], 15883200)
        self.assertEqual(record['snapshot_bytes_after'], 15902169)
        self.assertEqual(
            record['manifest_sha256_before'],
            '5ea551f5ffe3e3abbe42f4edf03dfe9d973fd7bc49ab7207180dc454ea874cbc')
        self.assertEqual(
            record['manifest_sha256_after'],
            '305e20be96a38b614495236f8c3252cf7e21c6d1635a5a29bce1c299b746526c')
        self.assertEqual(len(record['sealed_files_changed']), 4)
        self.assertEqual(sorted(record['sealed_file_sha256_after']),
                         sorted(record['sealed_files_changed']))
        for digest in record['sealed_file_sha256_after'].values():
            self.assertTrue(re.fullmatch(r'[0-9a-f]{64}', digest))


class InventoryDispositionTests(unittest.TestCase):
    def test_sanxing_row_maintained_pending_structural(self):
        # Batch transition (E0333): at P1 this row was
        # maintained_pending / execution_binding_structure (the
        # assertions this method originally pinned). The
        # execution-binding batch flipped it to registered; the
        # method name is kept for traceability and the pinned
        # posture is now the registered one.
        row = _sanxing_row()
        self.assertEqual(row['disposition'], 'registered')
        self.assertEqual(row['phase1_rule_id'], 'bazi.rule.r031')
        self.assertEqual(row['phase2_rule_id'],
                         'bazi.phase2.branch_punishment_facts')
        self.assertEqual(row['disclosure_sites'],
                         ['src/tianji_kb/bazi_sanxing_facts.py'])
        self.assertIn('bazi.section.s060', row['reason'])
        self.assertIsNone(row['unlock_path'])

    def test_flipped_set_unchanged(self):
        # E0333: the flipped set grew by the sanxing slice (the
        # P1-era pin of exactly two flipped items is superseded).
        # E0335: the ganzhi batch flipped the three remaining
        # bounded-strength predicates as well (six flipped, nine
        # maintained).
        # E0339: the luren batch flipped pattern-route-luren too
        # (seven flipped, eight maintained).
        # E0342: the zaqi batch flipped pattern-zaqi too
        # (eight flipped, seven maintained).
        # E0344: the ren batch flipped ren-pattern-yin-true-v1 too
        # (nine flipped, six maintained).
        # E0346: the dayun batch flipped dayun-classical-variants
        # too (segmented; ten flipped, five maintained).
        self.assertEqual(sorted(gov.FLIPPED_ITEMS),
                         ['commanding_visible_support',
                          'dayun-classical-variants',
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
        self.assertEqual(len(gov.MAINTAINED_ITEMS), 5)


class ConfigRegistrationTests(unittest.TestCase):
    def test_applied_source_registered_and_audited(self):
        import json
        sources = json.loads((ROOT / 'config'
                              / 'knowledge_sources.json').read_text(
                                  encoding='utf-8'))['sources']
        by_id = {x['source_id']: x for x in sources}
        applied = by_id['bazi.source.sanmingtonghui-applied']
        self.assertEqual(
            applied['sha256'],
            'a89c0b5da16ea4e07dc85180c49135ed280875318059f923ff'
            '7154f2c217662f')
        self.assertTrue(applied['content_path'].endswith(
            'sanming_tonghui_applied_v1.txt'))
        self.assertEqual(applied['evidence_level'], 'C')
        audit = json.loads((ROOT / 'config'
                            / 'phase2_source_audit.json').read_text(
                                encoding='utf-8'))
        rows = {r['source_id']: r for r in audit['lineages']}
        row = rows['bazi.source.sanmingtonghui-applied']
        # Same lineage as the snapshot original: the applied text
        # must never count as an independent witness.
        self.assertEqual(row['lineage_group'],
                         rows['bazi.source.sanmingtonghui']
                         ['lineage_group'])
        self.assertEqual(row['edition_status'], 'unverified')
        self.assertEqual(row['authority_status'], 'unverified')
        self.assertEqual(row['grade_ceiling'], 'C')

    def test_governance_register_references_data_only(self):
        # Compensation for the confinement exemption in
        # test_tj0123_sanxing_fact.py: the governance register may
        # NAME the slice (it is its disclosure ledger) but must
        # never import or call the implementation.
        text = (ROOT / 'src' / 'tianji_kb'
                / 'bazi_registration_governance.py').read_text(
                    encoding='utf-8')
        self.assertNotIn('import bazi_sanxing', text)
        self.assertNotIn('from .bazi_sanxing', text)
        self.assertNotIn('reviewed_branch_punishment_facts(', text)


class DisclosureUnchangedTests(unittest.TestCase):
    def test_slice_registration_verbatim(self):
        # Batch transition (E0333): the implementation module's
        # registration flipped (evidence_binding registered,
        # phase2_rule filled); sufficient_rule and the research /
        # public / ai posture are verbatim unchanged, and the
        # adjudication register below stays fully verbatim.
        reg = impl.SLICE_REGISTRATION
        self.assertEqual(reg['evidence_binding'],
                         'registered_phase1_phase2')
        self.assertEqual(reg['phase2_rule'],
                         'bazi.phase2.branch_punishment_facts')
        self.assertIsNone(reg['sufficient_rule'])
        self.assertTrue(reg['research_only'])
        self.assertFalse(reg['public_enabled'])
        self.assertFalse(reg['ai_enabled'])
        self.assertFalse(reg['concept_semantics_changed'])

    def test_adjudication_registration_verbatim(self):
        reg = adj.SLICE_SPEC['registration']
        self.assertTrue(
            reg['evidence_binding'].startswith(
                'pending_phase1_registration'))
        self.assertIsNone(reg['sufficient_rule'])
        self.assertIn('不建 Phase2 规则',
                      adj.SLICE_SPEC['consumption_boundaries'][0])


class DocumentAndLeakTests(unittest.TestCase):
    def test_document_names_entities_pins_and_gap(self):
        text = DOC.read_text(encoding='utf-8')
        for needle in ('bazi.chapter.sanming_sanxing',
                       'bazi.section.s060',
                       'bazi.term.branch_punishments',
                       'bazi.source.sanmingtonghui-applied',
                       '5ea551f5', '305e20be',
                       'execution_binding_structure',
                       'pending_phase1_registration'):
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
