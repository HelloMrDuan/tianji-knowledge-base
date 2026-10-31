"""Governance pending-8 audit first batch (E0342) public checks.

Public-side only (no sealed data): the batch record in
bazi_registration_governance is internally consistent, the
pattern-zaqi row flipped to registered with its rule/step IDs,
the maintained set shrank from 8 to 7, the statement's public
disclosure fields flipped with it (evidence_binding, quote and
case-ref section bindings, the registration lines in the
adjudication notes and limitations), the statement semantics are
unchanged (Wuji arm lists exposed renyuan in parallel, no-exposure
abstains, the general arm records the original text only with the
earth conversion unadjudicated, determination stays None), the
Ren-pattern D-1 block and the siling pilot stay pending, and the
batch governance document exists. Sealed-side behaviour (section
verbatim slices, resolver binding with conflict-branch roles,
Golden fire, forged-binding rejection, rollback) is pinned in
tests/test_phase2_bazizaiqi.py.
"""
import re
import unittest
from pathlib import Path

from tianji_kb import bazi_pattern as pattern
from tianji_kb import bazi_registration_governance as gov

ROOT = Path(__file__).resolve().parents[1]

CHOU_FOR_JI = [{'stem': '己', 'ten_god': '比肩'},
               {'stem': '癸', 'ten_god': '偏财'},
               {'stem': '辛', 'ten_god': '食神'}]


def _row(item):
    rows = [r for r in gov.REGISTRATION_INVENTORY if r['item'] == item]
    assert len(rows) == 1
    return rows[0]


class ZaqiPromotionPublicTests(unittest.TestCase):
    def test_record_entities(self):
        record = gov.GOVERNANCE_ZAQI_RECORD
        self.assertEqual(record['event'], 'E0342')
        self.assertEqual(record['canonical_sections_added'],
                         ['bazi.section.s065', 'bazi.section.s066',
                          'bazi.section.s067'])
        self.assertEqual(record['canonical_chapters_added'],
                         ['bazi.chapter.sanming_rilu_case',
                          'bazi.chapter.sanming_nvming_case'])
        self.assertEqual(record['canonical_terms_added'],
                         ['bazi.term.zaqi_selection'])
        self.assertEqual(record['phase1_rules_added'], ['bazi.rule.r036'])
        self.assertEqual(record['phase2_rules_added'],
                         ['bazi.phase2.pattern_zaqi'])
        self.assertEqual(len(record['golden_cases_added']), 6)

    def test_manifest_and_file_pins(self):
        record = gov.GOVERNANCE_ZAQI_RECORD
        self.assertEqual(record['snapshot_files_before'], 237)
        self.assertEqual(record['snapshot_files_after'], 237)
        self.assertEqual(record['snapshot_bytes_before'], 16001603)
        self.assertEqual(record['snapshot_bytes_after'], 16072121)
        self.assertEqual(
            record['manifest_sha256_before'],
            '15bd5a268d792c86072cf9ac51effb22ca5aefa004ea7ab44e7bbf44135682d5')
        self.assertEqual(
            record['manifest_sha256_after'],
            '6edcebc669e9b3de09856f353f6b1eafc22bff47a8dbfef3f35afdffacc1bfc0')
        self.assertEqual(sorted(record['sealed_files_changed']),
                         ['data/canonical/bazi/phase1_knowledge.json',
                          'data/canonical/bazi/phase2_execution.json',
                          'data/canonical/bazi/phase2_golden.json',
                          'data/coverage/phase1.json',
                          'data/product/knowledge_coverage.json'])
        self.assertEqual(sorted(record['sealed_file_sha256_after']),
                         sorted(record['sealed_files_changed']))
        for digest in record['sealed_file_sha256_after'].values():
            self.assertTrue(re.fullmatch(r'[0-9a-f]{64}', digest))

    def test_zaqi_row_registered(self):
        row = _row('pattern-zaqi')
        self.assertEqual(row['disposition'], 'registered')
        self.assertEqual(row['phase1_rule_id'], 'bazi.rule.r036')
        self.assertEqual(row['phase2_rule_id'], 'bazi.phase2.pattern_zaqi')
        self.assertIsNone(row['unlock_path'])
        self.assertNotIn('reason_class', row)
        for marker in ('bazi.section.s065', 'bazi.section.s066',
                       'bazi.section.s067'):
            self.assertIn(marker, row['reason'])

    def test_flipped_and_maintained_sets(self):
        # E0344: ren-pattern-yin-true-v1 flipped as well (six
        # maintained).
        self.assertEqual(sorted(gov.FLIPPED_ITEMS),
                         sorted(['commanding_visible_support',
                                 'lu_visible_support',
                                 'pattern-route-luren',
                                 'pattern-zaqi',
                                 'pure_generating_support',
                                 'pure_generating_support_water',
                                 'pure_support_metal',
                                 'ren-pattern-yin-true-v1',
                                 'sanxing-branch-fact-v1']))
        self.assertEqual(len(gov.MAINTAINED_ITEMS), 6)
        self.assertNotIn('pattern-zaqi', gov.MAINTAINED_ITEMS)

    def test_statement_disclosure_flipped(self):
        out = pattern.zaqi_selection_lookup(
            '己', '丑', CHOU_FOR_JI,
            [{'stem': '癸', 'ten_god': '偏财',
              'visible_pillars': ['month']}])
        self.assertEqual(out['evidence_binding'],
                         'registered_phase1_phase2')
        self.assertEqual(out['rule']['source_section_id'],
                         'bazi.section.s065')
        self.assertTrue(any('registered_phase1_phase2' in line
                            for line in out['scope_limits']))
        self.assertFalse(any('pending_phase1_rule_registration' in line
                             for line in out['scope_limits']))
        self.assertFalse(any('pending_phase1_rule_registration' in line
                             for line in out['adjudication_notes']))
        refs = {r['id']: r['source_section_id']
                for r in out['conflict']['case_refs']}
        self.assertEqual(refs, {'sanming.zaqi_case_rilu':
                                'bazi.section.s066',
                                'sanming.zaqi_poem_nvming':
                                'bazi.section.s067'})
        # Statement semantics unchanged by the flip.
        self.assertEqual(out['status'], 'stated')
        self.assertEqual(out['arm'], 'wuji_exposed_renyuan')
        self.assertEqual(
            [c['stem'] for c in out['selection']['selected_candidates']],
            ['癸'])
        self.assertTrue(out['conflict']['conflict_present'])
        self.assertEqual(out['determination']['status'], 'unresolved')
        self.assertIsNone(out['determination']['pattern'])
        self.assertIsNone(out['determination']['true_false'])

    def test_statement_arms_unchanged(self):
        abstained = pattern.zaqi_selection_lookup(
            '戊', '戌',
            [{'stem': '戊', 'ten_god': '比肩'},
             {'stem': '辛', 'ten_god': '伤官'},
             {'stem': '丁', 'ten_god': '正印'}], [])
        self.assertEqual(abstained['status'], 'abstained')
        self.assertEqual(abstained['abstention_reason'],
                         'no_exposed_renyuan')
        general = pattern.zaqi_selection_lookup(
            '壬', '戌',
            [{'stem': '戊', 'ten_god': '七杀'},
             {'stem': '辛', 'ten_god': '正印'},
             {'stem': '丁', 'ten_god': '正财'}], [])
        self.assertEqual(general['arm'], 'general_tu_unconverted')
        self.assertEqual(
            general['selection']['earth_conversion']['status'],
            'unadjudicated')
        self.assertIsNone(
            general['selection']['earth_conversion']
            ['converted_pattern_name'])

    def test_quote_section_bindings_completed(self):
        sections = {q['id']: q['source_section_id']
                    for q in pattern.ZAQI_QUOTES}
        self.assertEqual(sections, {
            'renshi.zaqi_passage': 'bazi.section.s065',
            'sanming.zaqi_case_rilu': 'bazi.section.s066',
            'sanming.zaqi_poem_nvming': 'bazi.section.s067'})
        # Registered quote texts and locators are untouched.
        sources = {q['id']: q['source_id'] for q in pattern.ZAQI_QUOTES}
        self.assertEqual(sources['sanming.zaqi_case_rilu'],
                         'bazi.source.sanmingtonghui')
        self.assertEqual(sources['renshi.zaqi_passage'],
                         'bazi.source.ditiansui-spouse')

    def test_out_of_scope_rows_unchanged(self):
        # E0344: ren-pattern-yin-true-v1 has since flipped in its
        # own batch; the siling pilot stays pending (user
        # adjudication pending), the route row stays registered.
        self.assertEqual(_row('ren-pattern-yin-true-v1')['disposition'],
                         'registered')
        self.assertEqual(_row('siling-yin-pilot')['disposition'],
                         'maintained_pending')
        self.assertEqual(_row('pattern-route-luren')['disposition'],
                         'registered')

    def test_governance_document_exists(self):
        doc = ROOT / 'docs/product/GOVERNANCE_ZAQI_PROMOTION.md'
        self.assertTrue(doc.is_file())
        text = doc.read_text(encoding='utf-8')
        for marker in ('E0342', 'bazi.rule.r036',
                       'bazi.phase2.pattern_zaqi', 'bazi.section.s065',
                       'bazi.section.s066', 'bazi.section.s067'):
            self.assertIn(marker, text)


if __name__ == '__main__':
    unittest.main()
