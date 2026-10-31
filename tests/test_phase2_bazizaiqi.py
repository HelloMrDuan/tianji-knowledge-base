"""Governance pending-8 audit first batch (E0342) sealed
registration tests: Ditiansui bage zaqi passage section s065,
Sanming zaqi witness window sections s066/s067, Phase1 rule r036
and the pattern_zaqi Phase2 step.

Pinned here:
- the registration contract triple (Phase1 rule + Phase2 step +
  Golden) resolves for the zaqi selection statement; the step is
  validated and fires on all six real-chart Golden cases (the
  Slice B witness charts) through the trace;
- the three new Canonical sections are verbatim slices (s065 of
  the pinned Ditiansui snapshot passage, s066/s067 of the official
  applied text S3) with zero PUA / zero box; every statement quote
  sits verbatim inside its bound section;
- r036 binds exactly one rule citation: the Ren passage itself
  (s065, classical). The two Sanming cases are NOT rule citations
  (Slice B B5: they evidence the rival school position, never a
  rule) — their evidence standing is carried by the window
  sections s066/s067 (review scope states the conflict-branch
  role) and by the statement's conflict.case_refs disclosure;
- the statement semantics stay byte-identical apart from the
  registration disclosure fields (the equivalence capture is a
  batch artefact recorded in the governance document);
- forged bindings are rejected by the resolver (altered passage
  text, case quote bound to the wrong window, case quote cited
  under the S0 register source instead of the applied source).
"""
import unittest
from pathlib import Path

from tianji_kb import bazi_registration_governance as governance
from tianji_kb.bazi_pattern import ZAQI_QUOTES
from tianji_kb.golden import run_cases
from tianji_kb.knowledge import read_json, validate_knowledge
from tianji_kb.resolver import ROOT, EvidenceResolver

VARIANT = 'ziping-structural-v1'
APPLIED = 'bazi.source.sanmingtonghui-applied'
DITIANSUI = 'bazi.source.ditiansui-spouse'
STEP = 'bazi.phase2.pattern_zaqi'
RULE = 'bazi.rule.r036'
ZAQI_SECTION = 'bazi.section.s065'
CASE1_SECTION = 'bazi.section.s066'
CASE2_SECTION = 'bazi.section.s067'
GOLDEN_IDS = [
    'bazi.zaqi-selection-wuji-chou-single-exposed',
    'bazi.zaqi-selection-wuji-xu-no-exposed-abstained',
    'bazi.zaqi-selection-general-xu-sanming-type',
    'bazi.zaqi-selection-non-misc-yin-not-applicable',
    'bazi.zaqi-selection-general-chen-no-exposed',
    'bazi.zaqi-selection-wuji-wei-two-exposed']
QUOTES = {q['id']: q for q in ZAQI_QUOTES}


def _bundle():
    model = validate_knowledge(ROOT)
    return next(x for x in model['bundles'] if x['domain'] == 'bazi')


class ZaqiRegistrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.resolver = EvidenceResolver(ROOT)
        cls.bundle = _bundle()
        cls.sections = {s['id']: s for s in cls.bundle['sections']}
        cls.rules = {r['id']: r for r in cls.bundle['rules']}
        cls.terms = {t['id']: t for t in cls.bundle['terms']}
        cls.contract = cls.resolver.contracts['bazi']
        cls.steps = {r['id']: r for r in cls.contract['rules']}

    def test_counts_and_registration(self):
        self.assertEqual(len(self.bundle['sections']), 67)
        self.assertEqual(len(self.bundle['chapters']), 27)
        self.assertEqual(len(self.bundle['terms']), 33)
        self.assertEqual(len(self.bundle['rules']), 36)
        self.assertEqual(len(self.contract['rules']), 37)
        self.assertEqual(self.sections[ZAQI_SECTION]['source_id'],
                         DITIANSUI)
        self.assertEqual(self.sections[ZAQI_SECTION]['chapter_id'],
                         'bazi.chapter.pattern_bage')
        for section_id in (CASE1_SECTION, CASE2_SECTION):
            self.assertEqual(self.sections[section_id]['source_id'],
                             APPLIED)
        for section_id in (ZAQI_SECTION, CASE1_SECTION, CASE2_SECTION):
            self.assertEqual(
                self.sections[section_id]['review']['status'],
                'approved')
        chapter_ids = {c['id'] for c in self.bundle['chapters']}
        self.assertIn('bazi.chapter.sanming_rilu_case', chapter_ids)
        self.assertIn('bazi.chapter.sanming_nvming_case', chapter_ids)
        self.assertIn('bazi.term.zaqi_selection', self.terms)
        self.assertEqual(self.rules[RULE]['term_refs'],
                         ['bazi.term.zaqi_selection'])

    def test_sections_are_verbatim_slices(self):
        snap = (ROOT / 'data/quarantine/public_domain_snapshots'
                '/daizhigev20')
        ditiansui = (snap / 'ditiansui_chanwei.txt').read_text(
            encoding='utf-8')
        applied = (snap / 'sanming_tonghui_applied_v1.txt').read_text(
            encoding='utf-8')
        self.assertEqual(self.sections[ZAQI_SECTION]['text'],
                         ditiansui[33161:33313])
        self.assertEqual(self.sections[CASE1_SECTION]['text'],
                         applied[192089:192173])
        self.assertEqual(self.sections[CASE2_SECTION]['text'],
                         applied[245029:245080])
        for section_id in (ZAQI_SECTION, CASE1_SECTION, CASE2_SECTION):
            text = self.sections[section_id]['text']
            self.assertFalse(any(
                0xE000 <= ord(c) <= 0xF8FF or 0xF0000 <= ord(c) <= 0xFFFFD
                for c in text), section_id)
            self.assertNotIn('□', text)

    def test_quotes_verbatim_inside_bound_sections(self):
        self.assertEqual(self.sections[ZAQI_SECTION]['text'],
                         QUOTES['renshi.zaqi_passage']['quote'])
        self.assertIn(QUOTES['sanming.zaqi_case_rilu']['quote'],
                      self.sections[CASE1_SECTION]['text'])
        self.assertIn(QUOTES['sanming.zaqi_poem_nvming']['quote'],
                      self.sections[CASE2_SECTION]['text'])
        # The case-1 window is the whole first method entry; the
        # registered case quote is its second half verbatim.
        window = self.sections[CASE1_SECTION]['text']
        self.assertTrue(window.startswith('一曰青云得路'))
        self.assertTrue(window.endswith(
            QUOTES['sanming.zaqi_case_rilu']['quote']))
        # The case-2 window is exactly the poem entry itself.
        self.assertEqual(self.sections[CASE2_SECTION]['text'],
                         QUOTES['sanming.zaqi_poem_nvming']['quote'])

    def test_registration_contract_triple_resolves(self):
        rule = self.rules[RULE]
        self.assertEqual(rule['execution_status'], 'executable')
        refs = self.resolver.resolve(RULE, VARIANT)
        self.assertEqual(len(refs), 1)
        self.assertTrue(all(r['rule_id'] == RULE for r in refs))
        self.assertEqual(
            {(r['source_id'], r['section_id'], r['role']) for r in refs},
            {(DITIANSUI, ZAQI_SECTION, 'classical')})
        step = self.steps[STEP]
        self.assertEqual(step['phase1_rule_refs'], [RULE])
        self.assertEqual(step['execution_status'], 'executable')
        self.assertEqual(step['validation_status'], 'validated')
        self.assertEqual(step['regression_test'],
                         'tests/test_phase2_bazizaiqi.py')
        self.assertEqual(step['golden_case_ids'], GOLDEN_IDS)
        step_refs = self.resolver.resolve(STEP, VARIANT)
        self.assertTrue(all(r['rule_id'] == STEP for r in step_refs))
        self.assertEqual(len(step_refs), 1)

    def test_bound_quotes_are_the_consumed_subset(self):
        # The rule binds exactly its adjudication basis: the Ren
        # passage alone. The two Sanming cases are not rule
        # citations; they sit verbatim inside their window sections
        # and the public register points at those sections.
        bound = {r['original_text']
                 for r in self.rules[RULE]['source_refs']}
        self.assertEqual(bound,
                         {QUOTES['renshi.zaqi_passage']['quote']})
        for quote_id, section_id in (
                ('sanming.zaqi_case_rilu', CASE1_SECTION),
                ('sanming.zaqi_poem_nvming', CASE2_SECTION)):
            self.assertNotIn(QUOTES[quote_id]['quote'], bound)
            self.assertIn(QUOTES[quote_id]['quote'],
                          self.sections[section_id]['text'])
        sections = {q['id']: q.get('source_section_id')
                    for q in ZAQI_QUOTES}
        self.assertEqual(sections['renshi.zaqi_passage'], ZAQI_SECTION)
        self.assertEqual(sections['sanming.zaqi_case_rilu'],
                         CASE1_SECTION)
        self.assertEqual(sections['sanming.zaqi_poem_nvming'],
                         CASE2_SECTION)

    def test_golden_cases_fire_the_registered_step(self):
        results = {c['id']: c for c in run_cases(ROOT, 'bazi')}
        self.assertEqual(len(results), 148)
        for case_id in GOLDEN_IDS:
            self.assertIn(case_id, results)
            self.assertIn(STEP, results[case_id]['rule_ids'])

    def test_forged_bindings_are_rejected(self):
        rule = self.resolver.entities[RULE][1]
        original_refs = rule['source_refs']
        passage = QUOTES['renshi.zaqi_passage']['quote']
        case1 = QUOTES['sanming.zaqi_case_rilu']['quote']
        forged_variants = [
            # one glyph altered inside the Ren passage
            {'source_id': DITIANSUI, 'section_id': ZAQI_SECTION,
             'original_text': passage.replace('只当取土为格',
                                              '只当取金为格', 1),
             'role': 'classical'},
            # the case-1 quote forged as a rule citation bound to
            # the case-2 window (text not present there)
            {'source_id': APPLIED, 'section_id': CASE2_SECTION,
             'original_text': case1, 'role': 'classical'},
            # the case-1 quote forged as a rule citation under the
            # S0 register source instead of the applied-text source
            # of its window
            {'source_id': 'bazi.source.sanmingtonghui',
             'section_id': CASE1_SECTION,
             'original_text': case1, 'role': 'classical'},
        ]
        for forged in forged_variants:
            rule['source_refs'] = original_refs + [forged]
            try:
                with self.assertRaises(ValueError):
                    self.resolver.resolve(RULE, VARIANT)
            finally:
                rule['source_refs'] = original_refs

    def test_governance_flip_consistency(self):
        self.assertIn('pattern-zaqi', governance.FLIPPED_ITEMS)
        self.assertNotIn('pattern-zaqi', governance.MAINTAINED_ITEMS)
        self.assertEqual(len(governance.MAINTAINED_ITEMS), 7)
        record = governance.GOVERNANCE_ZAQI_RECORD
        self.assertEqual(record['event'], 'E0342')
        self.assertEqual(record['phase1_rules_added'], ['bazi.rule.r036'])
        self.assertEqual(record['canonical_sections_added'],
                         [ZAQI_SECTION, CASE1_SECTION, CASE2_SECTION])
        self.assertEqual(record['snapshot_bytes_before'], 16001603)
        self.assertEqual(record['snapshot_bytes_after'], 16072121)
        self.assertEqual(
            record['manifest_sha256_before'],
            '15bd5a268d792c86072cf9ac51effb22ca5aefa004ea7ab44e7bbf44135682d5')
        self.assertEqual(
            record['manifest_sha256_after'],
            '6edcebc669e9b3de09856f353f6b1eafc22bff47a8dbfef3f35afdffacc1bfc0')


if __name__ == '__main__':
    unittest.main()
