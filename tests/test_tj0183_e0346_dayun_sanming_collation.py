"""E0346 stage 1 (public form): the 《论大运》 018-form collation
register (sanming-juan2-dayun-collation-register-v1).

Pins the register module against its transcription golden, the
TJ-017.1 classical register it succeeds (quotes verbatim, locators
identical), the S0/S3 dual-baseline coordinates, the per-point
collation notes, and the stage-1 hard gate: the single unresolved
point (residual 防 S0 58542, P2 seq 35) falls inside NO consumed
quote, no quote contains □, and every quote's S3 text form is
PUA-free. Snapshot-byte assertions live in the sealed twin.
"""
import json
import unittest
from pathlib import Path

from tianji_kb import bazi_dayun_classical as classical
from tianji_kb import bazi_dayun_collation as dayun_register
from tianji_kb import bazi_sanming_juan2_dayun_collation as reg

GOLDEN = json.loads(
    (Path(__file__).parent
     / 'golden_tj0183_e0346_dayun_sanming_collation.json')
    .read_text(encoding='utf-8'))

PUA = chr(0xED92)


class ModuleFormTest(unittest.TestCase):
    def test_module_matches_golden(self) -> None:
        self.assertEqual(reg.COLLATION_REGISTER_ID, GOLDEN['register_id'])
        self.assertEqual(reg.COLLATION_SNAPSHOTS, GOLDEN['snapshots'])
        self.assertEqual(reg.COLLATION_SECTIONS, GOLDEN['sections'])
        self.assertEqual(reg.COLLATION_QUOTES, GOLDEN['quotes'])
        self.assertEqual(reg.COLLATION_NOTES, GOLDEN['collation_notes'])
        self.assertEqual(reg.DAYUN_SANMING_LINKAGE, GOLDEN['fact_linkage'])

    def test_snapshot_pins_are_the_tj0183_stage_values(self) -> None:
        s0 = reg.COLLATION_SNAPSHOTS['sanming_tonghui.txt']
        s3 = reg.COLLATION_SNAPSHOTS['sanming_tonghui_applied_v1.txt']
        self.assertTrue(s0['sha256'].startswith('00e2a7db8bb59b25'))
        self.assertEqual(s0['chars'], 461157)
        self.assertTrue(s3['sha256'].startswith('a89c0b5da16ea4e0'))
        self.assertEqual(s3['chars'], 461156)

    def test_module_is_pure_data(self) -> None:
        callables = [name for name in vars(reg)
                     if callable(getattr(reg, name))
                     and not name.startswith('__')]
        self.assertEqual(callables, [])


class SectionFormTest(unittest.TestCase):
    def test_two_sections_with_dual_baselines(self) -> None:
        self.assertEqual(
            [s['section_id'] for s in reg.COLLATION_SECTIONS],
            ['sanming.juan2.lun_dayun',
             'sanming.juan11.luoluozi_dayun_witness'])
        for section in reg.COLLATION_SECTIONS:
            loc, s3 = section['locator'], section['s3_locator']
            self.assertEqual(s3['char_start'], loc['char_start'] - 1)
            self.assertEqual(s3['char_end'], loc['char_end'] - 1)
            self.assertEqual(section['s3_pua_count'], 0)
            self.assertEqual(section['s3_box_count'], 0)
            self.assertEqual(section['box_count'], 0)

    def test_lun_dayun_facts(self) -> None:
        section = reg.COLLATION_SECTIONS[0]
        self.assertEqual(section['locator'],
                         {'char_start': 58457, 'char_end': 59198})
        self.assertEqual(section['pua_count'], 3)
        self.assertEqual(section['fang_count'], 1)
        self.assertEqual(section['canonical_section_id'],
                         'bazi.section.s068')

    def test_witness_windows(self) -> None:
        section = reg.COLLATION_SECTIONS[1]
        parts = {p['part_id']: p for p in section['parts']}
        self.assertEqual(parts['witness_window_a']['locator'],
                         {'char_start': 396898, 'char_end': 397159})
        self.assertEqual(parts['witness_window_b']['locator'],
                         {'char_start': 408771, 'char_end': 408795})
        self.assertEqual(
            parts['witness_window_b']['canonical_section_id'],
            'bazi.section.s070')


class QuoteFormTest(unittest.TestCase):
    def test_sixteen_rows_fifteen_quotes_one_excluded_span(self) -> None:
        self.assertEqual(len(reg.COLLATION_QUOTES), 16)
        spans = [q for q in reg.COLLATION_QUOTES
                 if q['role'] == 'excluded_span']
        self.assertEqual([q['id'] for q in spans],
                         ['ldy.leap_clause_excluded_span'])

    def test_quotes_verbatim_against_classical_register(self) -> None:
        by_id = {q['id']: q for q in classical.QUOTES}
        for row in reg.COLLATION_QUOTES:
            if row['role'] == 'excluded_span':
                continue
            src = by_id[row['classical_quote_id']]
            self.assertEqual(row['quote'], src['quote'], row['id'])
            self.assertEqual(row['locator'], src['locator'], row['id'])
            self.assertEqual(row['role'], src['role'], row['id'])
        span = classical.EXCLUDED_SPANS[0]
        row = reg.COLLATION_QUOTES[-1]
        self.assertEqual(row['quote'], span['quote'])
        self.assertEqual(row['locator'], span['locator'])

    def test_locator_lengths_and_window_containment(self) -> None:
        windows = {
            'bazi.section.s068': (58457, 59198),
            'bazi.section.s069': (396898, 397159),
            'bazi.section.s070': (408771, 408795),
        }
        for row in reg.COLLATION_QUOTES:
            loc = row['locator']
            self.assertEqual(len(row['quote']),
                             loc['char_end'] - loc['char_start'], row['id'])
            start, end = windows[row['canonical_section_id']]
            self.assertGreaterEqual(loc['char_start'], start, row['id'])
            self.assertLessEqual(loc['char_end'], end, row['id'])
            self.assertEqual(row['s3_locator']['char_start'],
                             loc['char_start'] - 1, row['id'])

    def test_s3_forms(self) -> None:
        for row in reg.COLLATION_QUOTES:
            self.assertNotIn(PUA, row['s3_quote'], row['id'])
            self.assertNotIn('□', row['quote'], row['id'])
            self.assertNotIn('□', row['s3_quote'], row['id'])
            if row['s3_text_form'] == 'verbatim':
                self.assertEqual(row['s3_quote'], row['quote'], row['id'])
            else:
                self.assertEqual(
                    row['s3_quote'], row['quote'].replace(PUA, '算'),
                    row['id'])

    def test_rule_bindings_partition(self) -> None:
        r038 = {q['classical_quote_id'] for q in reg.COLLATION_QUOTES
                if q['phase1_rule_binding'] == 'bazi.rule.r038'}
        r039 = {q['classical_quote_id'] for q in reg.COLLATION_QUOTES
                if q['phase1_rule_binding'] == 'bazi.rule.r039'}
        unbound = {q['classical_quote_id'] for q in reg.COLLATION_QUOTES
                   if q['phase1_rule_binding'] is None}
        self.assertEqual(r038, {'direction_rule',
                                'vol11_direction_witness'})
        self.assertEqual(r039, {'ratio_statement', 'ratio_derivation',
                                'worked_example', 'anti_rounding',
                                'zero_borrow_definition',
                                'zero_borrow_example', 'handover_decade',
                                'handover_approx'})
        self.assertEqual(unbound, {'worked_example_check',
                                   'handover_example',
                                   'vol11_ratio_witness',
                                   'vol11_counting_divergence',
                                   'vol11_direction_witness2',
                                   'leap_clause_excluded_span'})
        linkage = reg.DAYUN_SANMING_LINKAGE
        self.assertEqual(set(linkage['phase1_rule_bindings']
                             ['bazi.rule.r038']),
                         {'ldy.' + q for q in r038})
        self.assertEqual(set(linkage['phase1_rule_bindings']
                             ['bazi.rule.r039']),
                         {'ldy.' + q for q in r039})


class NoteFormTest(unittest.TestCase):
    def test_ten_notes_counts_by_class(self) -> None:
        notes = reg.COLLATION_NOTES
        self.assertEqual(len(notes), 10)
        pua = [n for n in notes if n['snapshot_glyph'] == 'PUA']
        fang = [n for n in notes if n['snapshot_glyph'] == '防']
        genuine = [n for n in notes if n['disposition'] == 'genuine']
        self.assertEqual(len(pua), 4)
        self.assertEqual(len(fang), 3)
        self.assertEqual(len(genuine), 3)
        self.assertEqual({n['reading'] for n in pua}, {'算', '玄'})
        unresolved = [n for n in notes
                      if n['reading_status'] == 'unresolved']
        self.assertEqual([n['id'] for n in unresolved],
                         ['ldy-fang-58542'])

    def test_every_note_has_basis_and_fields(self) -> None:
        for note in reg.COLLATION_NOTES:
            for key in ('id', 'section_id', 'char_offset',
                        'context_short', 'snapshot_glyph', 'reading',
                        'reading_status', 'disposition', 'basis',
                        'usable_grade', 'note'):
                self.assertIn(key, note, note['id'])
            self.assertTrue(note['basis'], note['id'])
            if note['reading'] is not None:
                self.assertNotIn(PUA, note['reading'], note['id'])

    def test_hard_gate_unresolved_point_outside_all_quotes(self) -> None:
        # Stage-1 hard gate: the one unresolved point (residual 防
        # S0 58542, P2 seq 35) must not fall inside any quote span.
        for row in reg.COLLATION_QUOTES:
            loc = row['locator']
            self.assertFalse(
                loc['char_start'] <= 58542 < loc['char_end'], row['id'])


class PreviousRegistersRegressionTest(unittest.TestCase):
    def test_dayun_register_untouched(self) -> None:
        self.assertEqual(len(dayun_register.COLLATION_SECTIONS), 3)
        self.assertEqual(len(dayun_register.COLLATION_QUOTES), 8)
        self.assertEqual(len(dayun_register.COLLATION_NOTES), 13)

    def test_note_and_quote_ids_unique_across_registers(self) -> None:
        mine = ({n['id'] for n in reg.COLLATION_NOTES}
                | {q['id'] for q in reg.COLLATION_QUOTES})
        theirs = ({n['id'] for n in dayun_register.COLLATION_NOTES}
                  | {q['id'] for q in dayun_register.COLLATION_QUOTES})
        self.assertFalse(mine & theirs)


if __name__ == '__main__':
    unittest.main()
