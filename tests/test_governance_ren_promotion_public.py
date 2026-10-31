"""Governance pending-8 audit second batch (E0344) public checks.

Public-side only (no sealed data): the batch record in
bazi_registration_governance is internally consistent, the
ren-pattern-yin-true-v1 row flipped to registered with its
rule/step IDs, the maintained set shrank from 7 to 6, the D-1
block's public disclosure fields flipped with it
(evidence_binding, the D4 adjudication note landing form and the
registration scope limit), the determination semantics are
unchanged (three-state true_false, never a false-pattern label,
success_failure/purity/useful_god None + unreviewed, D1/D2
adjudications and the Slice A route precedence intact), the
chart harness input contract extension is minimal (gated kwarg,
default envelope unchanged, engine research gate and kwarg type
rejections pinned, golden.py provider pinning source strings
unchanged), the siling pilot stays pending (user adjudication),
and the batch governance document exists. Sealed-side behaviour
(Canonical quote binding, resolver evidence chain, Golden fire
of the registered step, forged-quote rejection, rollback) is
pinned in tests/test_phase2_bazirenyin.py.
"""
import re
import unittest
from pathlib import Path

from tianji_kb import bazi_pattern as pattern
from tianji_kb import bazi_registration_governance as gov

ROOT = Path(__file__).resolve().parents[1]


def _row(item):
    rows = [r for r in gov.REGISTRATION_INVENTORY if r['item'] == item]
    assert len(rows) == 1
    return rows[0]


def _touchstone_lookup():
    # The D-1 touchstone shape as a pure lookup: 庚 day master, 寅
    # month, commander 戊 (segment 1) exposed on no pillar.
    return pattern.ren_yin_true_false_lookup(
        '庚', '寅', route='not_luren', pilot_status='computed',
        pilot_reason=None, pilot_commander='戊',
        month_hidden_stems=['甲', '丙', '戊'],
        commander_ten_god='偏印', commander_visible_pillars=[])


class RenPromotionPublicTests(unittest.TestCase):
    def test_record_entities(self):
        record = gov.GOVERNANCE_REN_RECORD
        self.assertEqual(record['event'], 'E0344')
        self.assertEqual(record['canonical_sections_added'], [])
        self.assertEqual(record['canonical_chapters_added'], [])
        self.assertEqual(record['canonical_terms_added'],
                         ['bazi.term.ren_true_pattern'])
        self.assertEqual(record['phase1_rules_added'],
                         ['bazi.rule.r037'])
        self.assertEqual(record['phase2_rules_added'],
                         ['bazi.phase2.ren_yin_true_pattern'])
        self.assertEqual(len(record['golden_cases_added']), 15)
        self.assertIn('bazi.ren-yin-true-n1-touchstone',
                      record['golden_cases_added'])
        self.assertEqual(len(record['source_refs_subset']), 3)

    def test_manifest_and_file_pins(self):
        record = gov.GOVERNANCE_REN_RECORD
        self.assertEqual(record['snapshot_files_before'], 237)
        self.assertEqual(record['snapshot_files_after'], 237)
        self.assertEqual(record['snapshot_bytes_before'], 16072121)
        self.assertEqual(
            record['manifest_sha256_before'],
            '6edcebc669e9b3de09856f353f6b1eafc22bff47a8dbfef3f35afdffacc1bfc0')
        self.assertEqual(record['snapshot_bytes_after'], 16170283)
        self.assertEqual(
            record['manifest_sha256_after'],
            '2fdcfaec3ffd5f3ac5e991cb0da591df5dda57c3583bba4e431e7c098b4036b6')
        self.assertGreater(record['snapshot_bytes_after'],
                           record['snapshot_bytes_before'])
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

    def test_ren_row_registered(self):
        row = _row('ren-pattern-yin-true-v1')
        self.assertEqual(row['disposition'], 'registered')
        self.assertEqual(row['phase1_rule_id'], 'bazi.rule.r037')
        self.assertEqual(row['phase2_rule_id'],
                         'bazi.phase2.ren_yin_true_pattern')
        self.assertIsNone(row['unlock_path'])
        self.assertNotIn('reason_class', row)
        for marker in ('bazi.section.s053', 'bazi.section.s054',
                       'bazi.section.s024', 'ren_yin_pilot_result'):
            self.assertIn(marker, row['reason'])

    def test_flipped_and_maintained_sets(self):
        # E0346: dayun-classical-variants flipped (segmented;
        # five maintained).
        # E0348: bingyao-shenfeng-v1 flipped as well (eleven
        # flipped; four maintained -- the two inherited rows
        # remain in terminal inherited form).
        self.assertEqual(sorted(gov.FLIPPED_ITEMS),
                         sorted(['bingyao-shenfeng-v1',
                                 'commanding_visible_support',
                                 'dayun-classical-variants',
                                 'lu_visible_support',
                                 'pattern-route-luren',
                                 'pattern-zaqi',
                                 'pure_generating_support',
                                 'pure_generating_support_water',
                                 'pure_support_metal',
                                 'ren-pattern-yin-true-v1',
                                 'sanxing-branch-fact-v1',
                                 'tiaohou-qiongtong-v1']))
        # E0352: tiaohou-qiongtong-v1 flipped as well (twelve
        # flipped; three maintained -- siling-yin-pilot and the
        # two inherited rows).
        self.assertEqual(len(gov.MAINTAINED_ITEMS), 3)
        self.assertNotIn('ren-pattern-yin-true-v1',
                         gov.MAINTAINED_ITEMS)

    def test_block_disclosure_flipped(self):
        out = _touchstone_lookup()
        self.assertEqual(out['evidence_binding'],
                         'registered_phase1_phase2')
        self.assertEqual(out['rule']['source_section_id'],
                         'bazi.section.s053')
        self.assertEqual(out['procedure_rule']['source_section_id'],
                         'bazi.section.s054')
        self.assertTrue(any('registered_phase1_phase2' in line
                            for line in out['scope_limits']))
        self.assertFalse(any('pending_phase1_rule_registration' in line
                             for line in out['scope_limits']))
        self.assertFalse(any('pending_phase1_rule_registration' in line
                             for line in out['adjudication_notes']))
        self.assertTrue(any('bazi.phase2.ren_yin_true_pattern' in line
                            for line in out['adjudication_notes']))

    def test_semantics_unchanged(self):
        out = _touchstone_lookup()
        self.assertEqual(out['status'], 'determined')
        self.assertEqual(out['decision_step'], 4)
        self.assertEqual(out['determination']['true_false'],
                         'commander_not_visible')
        self.assertIsNone(out['determination']['pattern'])
        # Unreviewed dimensions stay None; no verdict upgrade.
        for key in ('success_failure', 'purity', 'useful_god'):
            self.assertIsNone(out['determination'][key])
        self.assertEqual(sorted(out['unreviewed']),
                         ['purity', 'success_failure', 'useful_god'])
        for value in out['unreviewed'].values():
            self.assertTrue(value.startswith('unreviewed'))
        self.assertFalse(out['qualified_for_determination'])
        self.assertTrue(out['research_only'])
        self.assertFalse(out['public_enabled'])
        self.assertFalse(out['ai_enabled'])
        # D2: a day-master stem never counts as exposed.
        day_only = pattern.ren_yin_true_false_lookup(
            '戊', '寅', route='not_luren', pilot_status='computed',
            pilot_reason=None, pilot_commander='戊',
            month_hidden_stems=['甲', '丙', '戊'],
            commander_ten_god='比肩', commander_visible_pillars=[])
        self.assertEqual(day_only['determination']['true_false'],
                         'commander_not_visible')
        # Route precedence (step 2) still abstains before the pilot.
        routed = pattern.ren_yin_true_false_lookup(
            '甲', '寅', route='luren_no_month_pattern',
            pilot_status='computed', pilot_reason=None,
            pilot_commander='甲',
            month_hidden_stems=['甲', '丙', '戊'],
            commander_ten_god='比肩',
            commander_visible_pillars=['year', 'month'])
        self.assertEqual(routed['status'], 'abstained')
        self.assertEqual(routed['abstention_reason'],
                         'luren_route_precedence')

    def test_harness_contract_extension_minimal(self):
        import inspect
        from tianji_kb import engine
        from tianji_kb import golden
        from tianji_kb.operations import bazi_chart
        # The extension is exactly one gated kwarg on the pinned
        # provider, defaulting to off.
        params = inspect.signature(bazi_chart.chart).parameters
        self.assertIn('ren_yin_pilot_result', params)
        self.assertIsNone(params['ren_yin_pilot_result'].default)
        # golden.py provider pinning is byte-unchanged in source:
        # the triple check (domain/provider/contract) and the
        # operations-prefix requirement are all still in place.
        source = Path(golden.__file__).read_text(encoding='utf-8')
        self.assertIn("provider!=PROVIDERS[obj['domain']]", source)
        self.assertIn("provider!=contract['provider']", source)
        self.assertIn("provider.startswith('tianji_kb.operations.')",
                      source)
        # The engine refuses the gated input outside research mode.
        with self.assertRaises(ValueError):
            engine.execute('bazi', {
                'value': '2024-02-06T00:30:00+08:00',
                'zone': 'Asia/Shanghai',
                'ren_yin_pilot_result': {'variant': 'x'}})
        # chart rejects a non-dict gated input before any work.
        with self.assertRaises(ValueError):
            bazi_chart.chart('甲辰', '丙寅', '庚子', '丙子',
                             ren_yin_pilot_result='not-a-dict')

    def test_out_of_scope_rows_unchanged(self):
        self.assertEqual(_row('siling-yin-pilot')['disposition'],
                         'maintained_pending')
        self.assertEqual(_row('pattern-zaqi')['disposition'],
                         'registered')
        # E0352 supersedes this row's E0344-era state: the
        # tiaohou row has since flipped to registered.
        self.assertEqual(_row('tiaohou-qiongtong-v1')['disposition'],
                         'registered')

    def test_no_sealed_text_leak(self):
        # The public lookup carries quote IDs/locators only; the
        # Canonical section texts never enter the public repo.
        out = _touchstone_lookup()
        self.assertNotIn('司令之神透出天干', str(out['rule']))
        self.assertNotIn('如寅月生人', str(out))

    def test_governance_document_exists(self):
        doc = ROOT / 'docs/product/GOVERNANCE_REN_PROMOTION.md'
        self.assertTrue(doc.is_file())
        text = doc.read_text(encoding='utf-8')
        for marker in ('E0344', 'bazi.rule.r037',
                       'bazi.phase2.ren_yin_true_pattern',
                       'bazi.section.s053', 'bazi.section.s054',
                       'bazi.section.s024', 'ren_yin_pilot_result'):
            self.assertIn(marker, text)


if __name__ == '__main__':
    unittest.main()
