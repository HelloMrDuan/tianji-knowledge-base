"""TJ-018.3 batch 3 B-2 (E0339) sealed registration tests: Sanming
juan-3 lu section s063 and juan-5 yangren section s064, Phase1 rule
r035 and the pattern_route Phase2 step.

Pinned here:
- the registration contract triple (Phase1 rule + Phase2 step +
  Golden) resolves for the luren route; the step is validated and
  fires on all nine real-chart Golden cases through the trace;
- the two new Canonical sections are verbatim slices of the official
  applied text (S3) with zero PUA / zero box, and every registered
  citation of both sections (22 yr.* + 30 sgl.*) is present in the
  section text at its registered position after the S0->S3 shift;
- r035 binds exactly the four consumed quotes (Ren exclusion at
  s054, lu sentence at s063, ren doctrine + ren positions at s064);
  none of the bound quotes contains a residual 防, and the
  seq-450 example citation yr.moli_hulu is NOT bound;
- residue carriage: s064 scope carries the 14 residual-防 site list
  and the RD-12 seq-450 parallel record verbatim (UD-1=A), s063
  scope carries the seq-47 unresolved site; no disposition changes;
- forged bindings are rejected by the resolver (altered quote text,
  quote bound to the wrong section, unknown section).
"""
import unittest
from pathlib import Path

from tianji_kb import bazi_registration_governance as governance
from tianji_kb import bazi_sanming_juan3_collation as juan3
from tianji_kb import bazi_sanming_juan5_zaqi_yangren_collation as juan5
from tianji_kb.bazi_pattern import LUREN_QUOTES
from tianji_kb.golden import run_cases
from tianji_kb.knowledge import read_json, validate_knowledge
from tianji_kb.resolver import ROOT, EvidenceResolver

VARIANT = 'ziping-structural-v1'
APPLIED = 'bazi.source.sanmingtonghui-applied'
STEP = 'bazi.phase2.pattern_route'
RULE = 'bazi.rule.r035'
LU_SECTION = 'bazi.section.s063'
YR_SECTION = 'bazi.section.s064'
GOLDEN_IDS = [
    'bazi.luren-route-lu-jia-yin', 'bazi.luren-route-ren-geng-you',
    'bazi.luren-route-ren-not-lu-jia-mao',
    'bazi.luren-route-ordinary-jia-wu',
    'bazi.luren-route-other-lu-yi-yin', 'bazi.luren-route-misc-wu-xu',
    'bazi.luren-route-yin-noblade-xin-xu', 'bazi.luren-route-lu-gui-zi',
    'bazi.luren-route-precedence-jia-yin']
YR_FANG_S3 = [180885, 182492, 182678, 182821, 183538, 183539, 183677,
              183916, 183982, 184102, 184158, 184164, 184186, 184317]


def _bundle():
    model = validate_knowledge(ROOT)
    return next(x for x in model['bundles'] if x['domain'] == 'bazi')


class LurenRegistrationTests(unittest.TestCase):
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
        self.assertEqual(len(self.bundle['sections']), 64)
        self.assertEqual(len(self.bundle['chapters']), 25)
        self.assertEqual(len(self.bundle['terms']), 32)
        self.assertEqual(len(self.bundle['rules']), 35)
        self.assertEqual(len(self.contract['rules']), 36)
        for section_id in (LU_SECTION, YR_SECTION):
            self.assertIn(section_id, self.sections)
            self.assertEqual(self.sections[section_id]['source_id'],
                             APPLIED)
            self.assertEqual(
                self.sections[section_id]['review']['status'],
                'approved')
        chapter_ids = {c['id'] for c in self.bundle['chapters']}
        self.assertIn('bazi.chapter.sanming_shiganlu', chapter_ids)
        self.assertIn('bazi.chapter.sanming_yangren', chapter_ids)
        self.assertIn('bazi.term.luren_route', self.terms)
        self.assertEqual(self.rules[RULE]['term_refs'],
                         ['bazi.term.luren_route'])

    def test_sections_are_verbatim_applied_text_slices(self):
        applied = (ROOT / 'data/quarantine/public_domain_snapshots'
                   '/daizhigev20/sanming_tonghui_applied_v1.txt'
                   ).read_text(encoding='utf-8')
        self.assertEqual(self.sections[LU_SECTION]['text'],
                         applied[74910:77453])
        self.assertEqual(self.sections[YR_SECTION]['text'],
                         applied[180873:184327])
        for section_id in (LU_SECTION, YR_SECTION):
            text = self.sections[section_id]['text']
            self.assertFalse(any(
                0xE000 <= ord(c) <= 0xF8FF or 0xF0000 <= ord(c) <= 0xFFFFD
                for c in text), section_id)
            self.assertNotIn('□', text)

    def test_all_registered_quotes_present_at_registered_positions(self):
        # Every registered citation of both sections must sit in the
        # S3 section text at its registered position: S0 locator
        # shifted by the section's uniform S0->S3 displacement (-1),
        # in its applied (mapped) form where a collation reading was
        # formally applied.
        yr_quotes = [q for q in juan5.COLLATION_QUOTES
                     if q['source_section_id'] == 'sanming.juan5.yangren']
        self.assertEqual(len(yr_quotes), 22)
        self.assertEqual(len(juan3.COLLATION_QUOTES), 30)
        checks = (
            (juan3.COLLATION_QUOTES, 74911, self.sections[LU_SECTION]),
            (yr_quotes, 180874, self.sections[YR_SECTION]))
        total = 0
        for quotes, s0_start, section in checks:
            for quote in quotes:
                total += 1
                form = quote['mapped_reading'] or quote['quote']
                start = quote['locator']['char_start'] - s0_start
                self.assertEqual(
                    section['text'][start:start + len(form)], form,
                    quote['id'])
        self.assertEqual(total, 52)

    def test_registration_contract_triple_resolves(self):
        rule = self.rules[RULE]
        self.assertEqual(rule['execution_status'], 'executable')
        refs = self.resolver.resolve(RULE, VARIANT)
        self.assertEqual(len(refs), 4)
        self.assertTrue(all(r['rule_id'] == RULE for r in refs))
        self.assertEqual(
            {(r['source_id'], r['section_id']) for r in refs},
            {('bazi.source.ditiansui-spouse', 'bazi.section.s054'),
             (APPLIED, LU_SECTION), (APPLIED, YR_SECTION)})
        step = self.steps[STEP]
        self.assertEqual(step['phase1_rule_refs'], [RULE])
        self.assertEqual(step['execution_status'], 'executable')
        self.assertEqual(step['validation_status'], 'validated')
        self.assertEqual(step['regression_test'],
                         'tests/test_phase2_baziluren.py')
        self.assertEqual(step['golden_case_ids'], GOLDEN_IDS)
        step_refs = self.resolver.resolve(STEP, VARIANT)
        self.assertTrue(all(r['rule_id'] == STEP for r in step_refs))
        self.assertEqual(len(step_refs), 4)

    def test_bound_quotes_are_the_consumed_subset(self):
        public = {q['id']: q for q in LUREN_QUOTES}
        bound = {r['original_text'] for r in self.rules[RULE]['source_refs']}
        consumed = {public[k]['quote'] for k in (
            'renshi.luren_route_exclusion', 'sanming.lu_sentence',
            'sanming.ren_doctrine', 'sanming.ren_positions')}
        self.assertEqual(bound, consumed)
        for text in bound:
            self.assertNotIn('防', text)
        moli = next(q for q in juan5.COLLATION_QUOTES
                    if q['id'] == 'yr.moli_hulu')
        self.assertNotIn(moli['quote'], bound)
        self.assertNotIn(moli['mapped_reading'] or moli['quote'], bound)
        sections = {q['id']: q.get('source_section_id')
                    for q in LUREN_QUOTES}
        self.assertEqual(sections['sanming.lu_sentence'], LU_SECTION)
        self.assertEqual(sections['sanming.ren_doctrine'], YR_SECTION)
        self.assertEqual(sections['sanming.ren_positions'], YR_SECTION)

    def test_residue_and_seq450_carriage(self):
        yr = self.sections[YR_SECTION]
        fang_at = [180873 + i for i, c in enumerate(yr['text'])
                   if c == '防']
        self.assertEqual(fang_at, YR_FANG_S3)
        scope = yr['review']['scope']
        self.assertIn('seq 450', scope)
        self.assertIn('parallel_registered', scope)
        self.assertIn('UD-1=A', scope)
        self.assertIn('䕶', scope)
        self.assertIn('獲', scope)
        self.assertIn('deferred_no_witness 10', scope)
        lu = self.sections[LU_SECTION]
        self.assertEqual([74910 + i for i, c in enumerate(lu['text'])
                          if c == '防'], [76987])
        lu_scope = lu['review']['scope']
        self.assertIn('seq 47', lu_scope)
        self.assertIn('deferred_no_witness', lu_scope)
        self.assertIn('unresolved', lu_scope)

    def test_golden_cases_fire_the_registered_step(self):
        results = {c['id']: c for c in run_cases(ROOT, 'bazi')}
        self.assertEqual(len(results), 142)
        for case_id in GOLDEN_IDS:
            self.assertIn(case_id, results)
            self.assertIn(STEP, results[case_id]['rule_ids'])

    def test_forged_bindings_are_rejected(self):
        rule = self.resolver.entities[RULE][1]
        original_refs = rule['source_refs']
        lu_sentence = next(q['quote'] for q in LUREN_QUOTES
                           if q['id'] == 'sanming.lu_sentence')
        forged_variants = [
            # one glyph altered inside the lu definition sentence
            {'source_id': APPLIED, 'section_id': LU_SECTION,
             'original_text': lu_sentence.replace('甲禄寅', '甲禄卯', 1),
             'role': 'classical'},
            # the verbatim lu sentence bound to the wrong section
            {'source_id': APPLIED, 'section_id': YR_SECTION,
             'original_text': lu_sentence, 'role': 'classical'},
            # a reading proposed for an unresolved residue site
            {'source_id': APPLIED, 'section_id': LU_SECTION,
             'original_text': '市㕓态', 'role': 'classical'},
        ]
        for forged in forged_variants:
            rule['source_refs'] = original_refs + [forged]
            try:
                with self.assertRaises(ValueError):
                    self.resolver.resolve(RULE, VARIANT)
            finally:
                rule['source_refs'] = original_refs

    def test_governance_flip_consistency(self):
        self.assertIn('pattern-route-luren', governance.FLIPPED_ITEMS)
        self.assertNotIn('pattern-route-luren',
                         governance.MAINTAINED_ITEMS)
        self.assertEqual(len(governance.MAINTAINED_ITEMS), 8)
        record = governance.TJ0183_B2_RECORD
        self.assertEqual(record['event'], 'E0339')
        self.assertEqual(record['phase1_rules_added'], ['bazi.rule.r035'])
        self.assertEqual(record['canonical_sections_added'],
                         ['bazi.section.s063', 'bazi.section.s064'])
        self.assertEqual(record['snapshot_bytes_before'], 15964218)
        self.assertEqual(record['snapshot_bytes_after'], 16001603)
        self.assertEqual(
            record['manifest_sha256_before'],
            'c815dc4ed02a9b7d0bd1487c3e1ed4e39d0bc826659d4ff0fb7f8a37ff685cdf')
        self.assertEqual(
            record['manifest_sha256_after'],
            '15bd5a268d792c86072cf9ac51effb22ca5aefa004ea7ab44e7bbf44135682d5')
        self.assertEqual(juan3.LUREN_PROMOTION_TAKEOVER['event'], 'E0339')


if __name__ == '__main__':
    unittest.main()
