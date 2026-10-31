"""Governance pending-8 audit second batch (E0344) sealed
registration tests: Phase1 rule r037 and the ren_yin_true_pattern
Phase2 step binding the Slice D-1 Ren-branch 寅月 true-pattern
determination.

Pinned here:
- the registration contract triple (Phase1 rule + Phase2 step +
  Golden) resolves for the D-1 determination; the step is
  validated and fires on all fifteen real-chart Golden cases (the
  D-1 witness set, including the touchstone, the segment-boundary
  one-second flip pair and the route-precedence abstention)
  through the trace, via the minimally extended harness input
  contract (the gated chart kwarg ren_yin_pilot_result);
- NO new Canonical sections: the determination's anchors already
  exist (s053 definition / s054 procedure / s024 segment basis),
  and r037 binds exactly the three consumed citations, each
  verbatim inside its section;
- the gated chart block is byte-identical to the standalone
  composition function's block over the same executed facts (the
  whole-envelope equivalence capture is a batch artefact recorded
  in the governance document);
- the old contract is unchanged: without the gated input the
  envelope carries no ren block and the step does not fire;
- forged bindings are rejected by the resolver (altered
  definition glyph, procedure quote bound to the wrong section,
  altered segment quote, definition quote under a wrong source).
"""
import copy
import json
import unittest
from pathlib import Path

from tianji_kb import bazi_registration_governance as governance
from tianji_kb.bazi_pattern import ZHENGE_QUOTES, ren_yin_true_pattern
from tianji_kb.golden import run_cases
from tianji_kb.knowledge import read_json, validate_knowledge
from tianji_kb.operations.bazi_chart import chart
from tianji_kb.resolver import ROOT, EvidenceResolver

VARIANT = 'ziping-structural-v1'
DITIANSUI = 'bazi.source.ditiansui-spouse'
STEP = 'bazi.phase2.ren_yin_true_pattern'
RULE = 'bazi.rule.r037'
TERM = 'bazi.term.ren_true_pattern'
DEF_SECTION = 'bazi.section.s053'
PROC_SECTION = 'bazi.section.s054'
SEG_SECTION = 'bazi.section.s024'
GOLDEN_IDS = [
    'bazi.ren-yin-true-t1-wu-zhengcai',
    'bazi.ren-yin-true-n1-touchstone',
    'bazi.ren-yin-true-t2-bing-qisha',
    'bazi.ren-yin-true-f1-boundary-minus-1s',
    'bazi.ren-yin-true-f2-boundary-exact',
    'bazi.ren-yin-true-t3-jia-pianyin',
    'bazi.ren-yin-true-t4-jia-shishen',
    'bazi.ren-yin-true-s3-route-precedence',
    'bazi.ren-yin-true-a1-wu-daymaster-neg',
    'bazi.ren-yin-true-a2-wu-daymaster-pos',
    'bazi.ren-yin-true-a3-bing-daymaster-neg',
    'bazi.ren-yin-true-a4-bing-daymaster-pos',
    'bazi.ren-yin-true-n2-jia-not-visible-2025',
    'bazi.ren-yin-true-s1-non-yin',
    'bazi.ren-yin-true-s2-pilot-uncertain']
QUOTES = {q['id']: q for q in ZHENGE_QUOTES}
PATTERN_VARIANT = 'bazi-pattern-structure-candidates-v1'


def _bundle():
    model = validate_knowledge(ROOT)
    return next(x for x in model['bundles'] if x['domain'] == 'bazi')


def _golden_cases():
    path = ROOT / 'data/canonical/bazi/phase2_golden.json'
    rows = read_json(path)['cases']
    return {c['id']: c for c in rows}


class RenRegistrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.resolver = EvidenceResolver(ROOT)
        cls.bundle = _bundle()
        cls.sections = {s['id']: s for s in cls.bundle['sections']}
        cls.rules = {r['id']: r for r in cls.bundle['rules']}
        cls.terms = {t['id']: t for t in cls.bundle['terms']}
        cls.contract = cls.resolver.contracts['bazi']
        cls.steps = {r['id']: r for r in cls.contract['rules']}
        cls.cases = _golden_cases()

    def test_counts_and_registration(self):
        # No new sections or chapters in E0344: the anchors
        # pre-exist.
        # E0346: +3 sections (s068/s069/s070), +2 chapters,
        # +2 terms, +2 rules (r038/r039), +2 contract steps.
        # E0348: +1 classic (shenfeng), +4 sections
        # (s071/s072/s073/s074), +4 chapters, +2 terms, +2 rules
        # (r040/r041), +2 contract steps.
        self.assertEqual(len(self.bundle['sections']), 74)
        self.assertEqual(len(self.bundle['chapters']), 33)
        self.assertEqual(len(self.bundle['terms']), 38)
        self.assertEqual(len(self.bundle['rules']), 41)
        self.assertEqual(len(self.contract['rules']), 42)
        for section_id in (DEF_SECTION, PROC_SECTION, SEG_SECTION):
            self.assertEqual(self.sections[section_id]['source_id'],
                             DITIANSUI)
            self.assertEqual(
                self.sections[section_id]['review']['status'],
                'approved')
        self.assertEqual(self.sections[DEF_SECTION]['chapter_id'],
                         'bazi.chapter.pattern_bage')
        self.assertEqual(self.sections[PROC_SECTION]['chapter_id'],
                         'bazi.chapter.pattern_bage')
        self.assertEqual(self.sections[SEG_SECTION]['chapter_id'],
                         'bazi.chapter.strength_factors')
        self.assertIn(TERM, self.terms)
        self.assertEqual(self.rules[RULE]['term_refs'], [TERM])

    def test_registration_contract_triple_resolves(self):
        rule = self.rules[RULE]
        self.assertEqual(rule['execution_status'], 'executable')
        refs = self.resolver.resolve(RULE, VARIANT)
        self.assertEqual(len(refs), 3)
        self.assertTrue(all(r['rule_id'] == RULE for r in refs))
        self.assertEqual(
            {(r['source_id'], r['section_id'], r['role']) for r in refs},
            {(DITIANSUI, DEF_SECTION, 'classical'),
             (DITIANSUI, PROC_SECTION, 'classical'),
             (DITIANSUI, SEG_SECTION, 'classical')})
        step = self.steps[STEP]
        self.assertEqual(step['phase1_rule_refs'], [RULE])
        self.assertEqual(step['execution_status'], 'executable')
        self.assertEqual(step['validation_status'], 'validated')
        self.assertEqual(step['regression_test'],
                         'tests/test_phase2_bazirenyin.py')
        self.assertEqual(step['golden_case_ids'], GOLDEN_IDS)
        step_refs = self.resolver.resolve(STEP, VARIANT)
        self.assertTrue(all(r['rule_id'] == STEP for r in step_refs))
        self.assertEqual(len(step_refs), 3)

    def test_bound_quotes_are_the_consumed_subset(self):
        refs = self.rules[RULE]['source_refs']
        self.assertEqual(len(refs), 3)
        by_section = {r['section_id']: r['original_text'] for r in refs}
        # Definition and procedure sections are single-sentence
        # sections: the bound quote is the whole section text.
        self.assertEqual(by_section[DEF_SECTION],
                         self.sections[DEF_SECTION]['text'])
        self.assertEqual(by_section[PROC_SECTION],
                         self.sections[PROC_SECTION]['text'])
        # The segment quote sits verbatim inside s024.
        self.assertIn(by_section[SEG_SECTION],
                      self.sections[SEG_SECTION]['text'])
        # The bound definition/procedure quotes are the D-1 block's
        # own registered quotes (same citations, no new quote rows).
        self.assertEqual(
            by_section[DEF_SECTION],
            QUOTES['renshi.zhenge_definition']['quote'])
        self.assertEqual(
            by_section[PROC_SECTION],
            QUOTES['renshi.siling_true_false_procedure']['quote'])

    def test_golden_cases_fire_the_registered_step(self):
        results = {c['id']: c for c in run_cases(ROOT, 'bazi')}
        # E0348: +11 Shenfeng-expansion Golden cases (180 total).
        self.assertEqual(len(results), 180)
        for case_id in GOLDEN_IDS:
            self.assertIn(case_id, results)
            self.assertIn(STEP, results[case_id]['rule_ids'])
        # run_cases itself asserts each case's expected subset
        # against the execution result; the block contents of the
        # two anchor cases are additionally pinned here by direct
        # execution.
        for case_id, want in (
                ('bazi.ren-yin-true-n1-touchstone',
                 'commander_not_visible'),
                ('bazi.ren-yin-true-f2-boundary-exact', 'true')):
            inputs = self.cases[case_id]['input']
            envelope = chart(
                inputs['year_ganzhi'], inputs['month_ganzhi'],
                inputs['day_ganzhi'], inputs['hour_ganzhi'],
                pattern_variant=PATTERN_VARIANT,
                ren_yin_pilot_result=copy.deepcopy(
                    inputs['ren_yin_pilot_result']))
            block = envelope['result']['pattern_determination_ren_yin']
            self.assertEqual(block['determination']['true_false'],
                             want, case_id)

    def test_gated_block_equals_standalone_composition(self):
        # The registered-step block must be the composition
        # function's block over the same executed facts, verbatim.
        from tianji_kb.resolver import ExecutionTrace
        for case_id in ('bazi.ren-yin-true-n1-touchstone',
                        'bazi.ren-yin-true-t1-wu-zhengcai',
                        'bazi.ren-yin-true-s3-route-precedence'):
            case = self.cases[case_id]
            inputs = case['input']
            gated = chart(
                inputs['year_ganzhi'], inputs['month_ganzhi'],
                inputs['day_ganzhi'], inputs['hour_ganzhi'],
                pattern_variant=PATTERN_VARIANT,
                ren_yin_pilot_result=copy.deepcopy(
                    inputs['ren_yin_pilot_result']))
            baseline = chart(
                inputs['year_ganzhi'], inputs['month_ganzhi'],
                inputs['day_ganzhi'], inputs['hour_ganzhi'],
                pattern_variant=PATTERN_VARIANT)
            trace = ExecutionTrace('bazi', VARIANT, self.resolver)
            for step in baseline['trace']:
                trace.add(step['rule_id'], step['inputs'], step['output'])
            standalone = ren_yin_true_pattern(
                trace, copy.deepcopy(inputs['ren_yin_pilot_result']))
            self.assertEqual(
                gated['result']['pattern_determination_ren_yin'],
                standalone, case_id)

    def test_old_contract_unchanged_without_gated_input(self):
        case = self.cases['bazi.ren-yin-true-n1-touchstone']
        inputs = case['input']
        envelope = chart(
            inputs['year_ganzhi'], inputs['month_ganzhi'],
            inputs['day_ganzhi'], inputs['hour_ganzhi'],
            pattern_variant=PATTERN_VARIANT)
        self.assertNotIn('pattern_determination_ren_yin',
                         envelope['result'])
        rule_ids = {step['rule_id'] for step in envelope['trace']}
        self.assertNotIn(STEP, rule_ids)

    def test_forged_bindings_are_rejected(self):
        rule = self.resolver.entities[RULE][1]
        original_refs = rule['source_refs']
        definition = QUOTES['renshi.zhenge_definition']['quote']
        procedure = QUOTES['renshi.siling_true_false_procedure']['quote']
        segment = {r['section_id']: r['original_text']
                   for r in original_refs}[SEG_SECTION]
        def _alter(text):
            # Replace the first glyph: the altered string cannot
            # occur verbatim inside the (single-sentence) section.
            return ('伪' if text[0] != '伪' else '真') + text[1:]

        forged_variants = [
            # one glyph altered inside the definition quote
            {'source_id': DITIANSUI, 'section_id': DEF_SECTION,
             'original_text': _alter(definition),
             'role': 'classical'},
            # the procedure quote bound to the definition section
            # (its text is not present there)
            {'source_id': DITIANSUI, 'section_id': DEF_SECTION,
             'original_text': procedure, 'role': 'classical'},
            # one glyph altered inside the segment quote
            {'source_id': DITIANSUI, 'section_id': SEG_SECTION,
             'original_text': _alter(segment),
             'role': 'classical'},
            # the definition quote under a wrong source
            {'source_id': 'bazi.source.sanmingtonghui',
             'section_id': DEF_SECTION,
             'original_text': definition, 'role': 'classical'},
        ]
        for forged in forged_variants:
            rule['source_refs'] = original_refs + [forged]
            try:
                with self.assertRaises(ValueError):
                    self.resolver.resolve(RULE, VARIANT)
            finally:
                rule['source_refs'] = original_refs

    def test_governance_flip_consistency(self):
        self.assertIn('ren-pattern-yin-true-v1',
                      governance.FLIPPED_ITEMS)
        self.assertNotIn('ren-pattern-yin-true-v1',
                         governance.MAINTAINED_ITEMS)
        self.assertEqual(len(governance.MAINTAINED_ITEMS), 4)
        record = governance.GOVERNANCE_REN_RECORD
        self.assertEqual(record['event'], 'E0344')
        self.assertEqual(record['phase1_rules_added'], ['bazi.rule.r037'])
        self.assertEqual(record['canonical_sections_added'], [])
        self.assertEqual(record['snapshot_bytes_before'], 16072121)
        self.assertEqual(record['snapshot_bytes_after'], 16170283)
        self.assertEqual(
            record['manifest_sha256_before'],
            '6edcebc669e9b3de09856f353f6b1eafc22bff47a8dbfef3f35afdffacc1bfc0')
        self.assertEqual(
            record['manifest_sha256_after'],
            '2fdcfaec3ffd5f3ac5e991cb0da591df5dda57c3583bba4e431e7c098b4036b6')
        self.assertEqual(len(record['golden_cases_added']), 15)


if __name__ == '__main__':
    unittest.main()
