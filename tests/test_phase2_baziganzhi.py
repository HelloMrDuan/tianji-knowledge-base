"""TJ-018.3 batch 2 (E0335) sealed registration tests: Sanming juan-2
ganzhi sections s061/s062, Phase1 rules r032/r033/r034 and the three
strength Phase2 steps (lu / metal / water).

Pinned here:
- the registration contract triple (Phase1 rule + Phase2 step +
  Golden) resolves for all three predicates, independently;
- the two new Canonical sections are verbatim slices of the official
  applied text (S3) with zero PUA;
- lu and water fire on their real-chart Golden positives through
  their own registered steps; metal's step NEVER fires (constructive
  unsatisfiability on real charts) and stays validation_status
  'pending' with golden_case_ids pointing at its negative witness
  set (parent adjudication recorded in the batch governance doc);
- Ding isolation at the binding layer: no source_ref of the three
  new rules binds a Ding quote, and the Ding blocked_by_conflict
  registers are byte-identical in status after registration;
- the sm2-gap-42148 exclusion: no bound citation covers S0/S3 42148
  in either coordinate system, a forged gap-covering binding is
  rejected by the binding-coverage check, the proposed reading is
  rejected by the resolver, and the gap stays disposition
  'unresolved';
- the diwang substitution wording travels verbatim with the
  framework_derived grade and none of the eight forbidden phrasings
  appears in the new sealed entries.
"""
import json
import unittest
from pathlib import Path

from tianji_kb import bazi_fire_morphology as fire_morphology
from tianji_kb import bazi_fire_si_yin_morphology as fire_si_yin
from tianji_kb import bazi_metal_water_roots as metal_water
from tianji_kb import bazi_registration_governance as governance
from tianji_kb import bazi_sanming_juan2_collation as juan2
from tianji_kb.golden import run_cases
from tianji_kb.knowledge import read_json, validate_knowledge
from tianji_kb.operations.bazi_chart import chart
from tianji_kb.resolver import ROOT, EvidenceResolver

VARIANT = 'ziping-structural-v1'
APPLIED = 'bazi.source.sanmingtonghui-applied'
LU_STEP = 'bazi.phase2.strength_lu_visible_support'
METAL_STEP = 'bazi.phase2.strength_pure_support_metal'
WATER_STEP = 'bazi.phase2.strength_pure_generating_support_water'
RULES = {'bazi.rule.r032': LU_STEP, 'bazi.rule.r033': METAL_STEP,
         'bazi.rule.r034': WATER_STEP}
DIWANG_WORDING = (
    '帝旺位（推步）：本位无逐干逐字句，系由该干逐干明句之长生位 + '
    '《论五行旺相休囚死并寄生十二宫》十二宫次序 + 阴阳顺逆推步得出，'
    '证据等级 framework_derived（推论级），与 per_stem_listed'
    '（逐干明句级）分级并列、永不混同。')
FORBIDDEN_PHRASINGS = [
    '庚帝旺在酉（原文）', '三命明言庚旺于酉',
    '壬帝旺在子（原文）', '三命明言壬旺于子',
    '辛帝旺在申（原文）', '癸帝旺在亥（原文）',
    '丙帝旺在午（原文）', '三命明言丙旺于午']
GAP_S0 = 42148
TAIL_EXCLUDED = (42116, 42151)


def _bundle():
    model = validate_knowledge(ROOT)
    return next(x for x in model['bundles'] if x['domain'] == 'bazi')


def _quotes_by_id():
    return {q['id']: q for q in juan2.COLLATION_QUOTES
            if q['source_section_id'] in (
                'sanming.juan2.tiangan_yinyang_shengsi',
                'sanming.juan2.wuxing_wangxiang_jisheng')}


def _binding_quote_ids(original_text, quotes):
    """Register quotes a bound citation belongs to (exact or segment)."""
    return {qid for qid, q in quotes.items()
            if original_text == q['quote'] or original_text in q['quote']
            or q['quote'] in original_text}


def assert_binding_exclusions(test, rules, sections, quotes):
    """The batch binding-coverage check (Ding isolation + gap).

    Raises AssertionError on any violation; used positively on the
    registered rules and negatively on forged bindings below.
    """
    s61 = sections['bazi.section.s061']
    ding_ids = {'sm2.ding_sheng', 'sm2.ding_shengsi'}
    for rule in rules:
        for ref in rule['source_refs']:
            ids = _binding_quote_ids(ref['original_text'], quotes)
            test.assertFalse(
                ids & ding_ids,
                f"{rule['id']} binds a Ding quote: {ids & ding_ids}")
            if ref['section_id'] != 'bazi.section.s061':
                continue
            # S3 coordinates: section S3 range starts at 38891.
            start = s61['text'].index(ref['original_text'])
            s3_lo, s3_hi = 38891 + start, 38891 + start + len(ref['original_text'])
            test.assertFalse(
                s3_lo <= GAP_S0 < s3_hi,
                f"{rule['id']} ref covers the gap in S3 coordinates")
            # S0 coordinates via the register locator of the quote
            # the citation belongs to (segment citations resolve to
            # their parent quote's registered range).
            for qid in ids:
                q = quotes[qid]
                lo, hi = q['locator']['char_start'], q['locator']['char_end']
                test.assertFalse(
                    lo <= GAP_S0 < hi,
                    f"{rule['id']} ref covers the gap in S0 coordinates")
                test.assertTrue(
                    hi <= TAIL_EXCLUDED[0] or lo >= TAIL_EXCLUDED[1],
                    f"{rule['id']} ref intersects the excluded tail")


class GanzhiRegistrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.resolver = EvidenceResolver(ROOT)
        cls.bundle = _bundle()
        cls.sections = {s['id']: s for s in cls.bundle['sections']}
        cls.rules = {r['id']: r for r in cls.bundle['rules']}
        cls.contract = cls.resolver.contracts['bazi']
        cls.steps = {r['id']: r for r in cls.contract['rules']}
        cls.quotes = _quotes_by_id()

    def test_sections_and_chapters_registered(self):
        # E0339 (TJ-018.3 B-2): +2 chapters, +2 sections (s063/s064)
        # and +1 rule (r035) for the luren promotion.
        # E0342 (zaqi promotion): +2 chapters, +3 sections
        # (s065/s066/s067) and +1 rule (r036).
        # E0344 (ren promotion): no new sections/chapters, +1 rule
        # (r037).
        # E0346 (dayun Sanming-segment promotion): +2 chapters,
        # +3 sections (s068/s069/s070), +2 rules (r038/r039).
        # E0348 (Shenfeng Canonical expansion): +4 chapters,
        # +4 sections (s071/s072/s073/s074), +2 rules (r040/r041).
        self.assertEqual(len(self.bundle['sections']), 74)
        self.assertEqual(len(self.bundle['chapters']), 33)
        self.assertEqual(len(self.bundle['rules']), 41)
        for section_id in ('bazi.section.s061', 'bazi.section.s062'):
            self.assertIn(section_id, self.sections)
            self.assertEqual(self.sections[section_id]['source_id'], APPLIED)
            self.assertEqual(
                self.sections[section_id]['review']['status'], 'approved')
        chapter_ids = {c['id'] for c in self.bundle['chapters']}
        self.assertIn('bazi.chapter.sanming_tianganshengsi', chapter_ids)
        self.assertIn('bazi.chapter.sanming_wangxiangjisheng', chapter_ids)

    def test_sections_are_verbatim_applied_text_slices(self):
        applied = (ROOT / 'data/quarantine/public_domain_snapshots'
                   '/daizhigev20/sanming_tonghui_applied_v1.txt'
                   ).read_text(encoding='utf-8')
        self.assertEqual(self.sections['bazi.section.s061']['text'],
                         applied[38891:43082])
        self.assertEqual(self.sections['bazi.section.s062']['text'],
                         applied[54894:55672])
        for section_id in ('bazi.section.s061', 'bazi.section.s062'):
            text = self.sections[section_id]['text']
            self.assertFalse(any(
                0xE000 <= ord(c) <= 0xF8FF or 0xF0000 <= ord(c) <= 0xFFFFD
                for c in text), section_id)

    def test_registration_contract_triple_resolves(self):
        for rule_id, step_id in RULES.items():
            self.assertEqual(self.rules[rule_id]['execution_status'],
                             'executable')
            # resolve() verifies every source_ref verbatim against
            # its Canonical section and returns the evidence list.
            refs = self.resolver.resolve(rule_id, VARIANT)
            self.assertEqual(len(refs), len(self.rules[rule_id]['source_refs']))
            self.assertTrue(all(r['rule_id'] == rule_id for r in refs))
            step = self.steps[step_id]
            self.assertEqual(step['phase1_rule_refs'], [rule_id])
            self.assertEqual(step['execution_status'], 'executable')
            self.assertEqual(step['regression_test'],
                             'tests/test_phase2_baziganzhi.py')
            self.assertTrue(step['golden_case_ids'])
            step_refs = self.resolver.resolve(step_id, VARIANT)
            self.assertTrue(all(r['rule_id'] == step_id for r in step_refs))
            self.assertEqual(len(step_refs), len(refs))

    def test_lu_and_water_steps_validated_metal_pending(self):
        self.assertEqual(self.steps[LU_STEP]['validation_status'], 'validated')
        self.assertEqual(self.steps[WATER_STEP]['validation_status'],
                         'validated')
        metal = self.steps[METAL_STEP]
        self.assertEqual(metal['validation_status'], 'pending')
        self.assertEqual(
            metal['golden_case_ids'],
            ['bazi.strength-ganzhi-metal-negative-xin-clashed-roots',
             'bazi.strength-ganzhi-metal-negative-geng-stem-combination'])
        self.assertIn('构造性不可满足', metal['evidence_scope'])
        self.assertIn('负例见证集', metal['evidence_scope'])

    def test_golden_positives_fire_and_metal_never_fires(self):
        results = {c['id']: c for c in run_cases(ROOT, 'bazi')}
        self.assertIn(LU_STEP,
                      results['bazi.strength-ganzhi-lu-positive']['rule_ids'])
        self.assertIn(
            WATER_STEP,
            results['bazi.strength-ganzhi-water-positive']['rule_ids'])
        for case_id in ('bazi.strength-ganzhi-metal-negative-xin-clashed-roots',
                        'bazi.strength-ganzhi-metal-negative-geng-stem-combination'):
            self.assertIn(case_id, results)
            self.assertNotIn(METAL_STEP, results[case_id]['rule_ids'])
        for case in results.values():
            self.assertNotIn(METAL_STEP, case['rule_ids'])

    def _adjudication(self, pillars):
        y, m, d, h = pillars
        execution = chart(year_ganzhi=y, month_ganzhi=m, day_ganzhi=d,
                          hour_ganzhi=h,
                          strength_variant='bazi-strength-adjudication-v1')
        return execution['result']['strength_assessment']

    def test_witness_adjudications_use_registered_exits(self):
        lu = self._adjudication(('丁卯', '乙巳', '丙午', '甲午'))
        self.assertEqual(lu['classification'], 'strong')
        why = lu['why_not_indeterminate']
        self.assertEqual(why['sufficient_rule'], LU_STEP)
        self.assertNotIn('sufficient_predicate', why)
        self.assertNotIn('predicate_rule_registration', why)
        self.assertEqual(len(why['conditions']), 9)
        self.assertTrue(all(c['met'] for c in why['conditions']))
        self.assertIn(LU_STEP, lu['matched_rule_ids'])
        self.assertEqual(lu['blockers'], [])

        water = self._adjudication(('辛酉', '庚子', '癸酉', '壬子'))
        self.assertEqual(water['classification'], 'strong')
        why = water['why_not_indeterminate']
        self.assertEqual(why['sufficient_rule'], WATER_STEP)
        self.assertNotIn('sufficient_predicate', why)
        self.assertNotIn('predicate_rule_registration', why)
        self.assertEqual(len(why['conditions']), 8)
        self.assertTrue(all(c['met'] for c in why['conditions']))
        month_cond = next(c for c in why['conditions']
                          if c['condition'] == 'reviewed_same_element_month_zi')
        self.assertEqual(month_cond['month_root_grade'], 'per_stem_listed')
        self.assertIn(WATER_STEP, water['matched_rule_ids'])

        ren = self._adjudication(('辛酉', '庚子', '壬子', '庚子'))
        self.assertEqual(ren['classification'], 'indeterminate')
        self.assertIsNone(ren['why_not_indeterminate'])

    def test_metal_negative_witnesses_stay_indeterminate(self):
        for pillars in (('辛酉', '丁酉', '辛卯', '戊子'),
                        ('辛酉', '丁酉', '庚寅', '丙子')):
            assessment = self._adjudication(pillars)
            self.assertEqual(assessment['classification'], 'indeterminate')
            self.assertIsNone(assessment['why_not_indeterminate'])
            self.assertNotIn(METAL_STEP, assessment['matched_rule_ids'])

    def test_ding_isolation_and_registers_unchanged(self):
        assert_binding_exclusions(
            self, [self.rules[r] for r in RULES], self.sections, self.quotes)
        self.assertEqual(fire_morphology.DING_BLOCK['status'],
                         'blocked_by_conflict')
        self.assertEqual(fire_morphology.DING_BLOCK['conflict_id'],
                         'sanming-juan2.ding-changsheng')
        self.assertEqual(fire_si_yin.DING_SI_DISPOSITION['verdict'],
                         'blocked_by_conflict')
        self.assertEqual(fire_si_yin.DING_YIN_DISPOSITION['verdict'],
                         'blocked_by_conflict')
        scope = self.sections['bazi.section.s061']['review']['scope']
        for conflict_id in ('sanming-juan2.ding-changsheng',
                            'sanming-juan2.xin-changsheng',
                            'sanming-juan2.gui-changsheng'):
            self.assertIn(conflict_id, scope)

    def test_gap_exclusion_assertions(self):
        # (a) is exercised by assert_binding_exclusions above; the
        # section still carries the gap verbatim and unresolved.
        s61 = self.sections['bazi.section.s061']
        self.assertEqual(s61['text'].count('□'), 1)
        scope = s61['review']['scope']
        self.assertIn('sm2-gap-42148', scope)
        self.assertIn('reading=None', scope)
        self.assertIn('disposition=unresolved', scope)
        # (b) forged gap-covering binding is rejected by the
        # binding-coverage check.
        i = s61['text'].index('□')
        forged_text = s61['text'][i - 15:i + 16]
        forged_rule = {'id': 'bazi.rule.forged',
                       'source_refs': [{'source_id': APPLIED,
                                        'section_id': 'bazi.section.s061',
                                        'original_text': forged_text,
                                        'role': 'classical'}]}
        with self.assertRaises(AssertionError):
            assert_binding_exclusions(
                self, [forged_rule], self.sections, self.quotes)
        # (b2) the proposed reading of the gap is not in the text:
        # a binding attempt carrying it is rejected by the resolver
        # as an unverifiable quote (in-memory forged ref, restored
        # immediately).
        rule = self.resolver.entities['bazi.rule.r032'][1]
        original_refs = rule['source_refs']
        rule['source_refs'] = original_refs + [{
            'source_id': APPLIED, 'section_id': 'bazi.section.s061',
            'original_text': '谬误甚矣', 'role': 'classical'}]
        try:
            with self.assertRaises(ValueError):
                self.resolver.resolve('bazi.rule.r032', VARIANT)
        finally:
            rule['source_refs'] = original_refs

    def test_diwang_wording_grades_and_forbidden_phrasings(self):
        for section_id in ('bazi.section.s061', 'bazi.section.s062'):
            scope = self.sections[section_id]['review']['scope']
            self.assertIn(DIWANG_WORDING, scope)
        for rule_id in ('bazi.rule.r033', 'bazi.rule.r034'):
            self.assertIn(DIWANG_WORDING, self.rules[rule_id]['difference'])
            self.assertIn('framework_derived',
                          self.rules[rule_id]['difference'])
        entries = [self.sections[s] for s in ('bazi.section.s061',
                                              'bazi.section.s062')]
        entries += [self.rules[r] for r in RULES]
        blob = json.dumps(entries, ensure_ascii=False)
        for phrase in FORBIDDEN_PHRASINGS:
            self.assertNotIn(phrase, blob)
        # Register-level root grades: derived positions stay derived.
        geng_you = next(p for p in metal_water.GENG_ROOT_POSITIONS
                        if p['branch'] == '酉')
        self.assertEqual(geng_you['grade'], 'framework_derived')
        xin_you = next(p for p in metal_water.XIN_ROOT_POSITIONS
                       if p['branch'] == '酉')
        self.assertEqual(xin_you['grade'], 'per_stem_listed')
        ren_zi = next(p for p in metal_water.REN_ROOT_POSITIONS
                      if p['branch'] == '子')
        self.assertEqual(ren_zi['grade'], 'framework_derived')
        gui_zi = next(p for p in metal_water.GUI_ROOT_POSITIONS
                      if p['branch'] == '子')
        self.assertEqual(gui_zi['grade'], 'per_stem_listed')

    def test_governance_flip_consistency(self):
        for item in ('lu_visible_support', 'pure_support_metal',
                     'pure_generating_support_water'):
            self.assertIn(item, governance.FLIPPED_ITEMS)
            self.assertNotIn(item, governance.MAINTAINED_ITEMS)
        # E0339 (TJ-018.3 B-2): pattern-route-luren flipped too.
        # E0342: pattern-zaqi flipped too (seven maintained).
        # E0344: ren-pattern-yin-true-v1 flipped too (six
        # maintained).
        self.assertEqual(len(governance.MAINTAINED_ITEMS), 4)
        record = governance.TJ0183_P2_RECORD
        self.assertEqual(record['event'], 'E0335')
        self.assertEqual(record['phase1_rules_added'],
                         ['bazi.rule.r032', 'bazi.rule.r033', 'bazi.rule.r034'])
        self.assertEqual(record['snapshot_bytes_before'], 15922702)
        self.assertEqual(record['snapshot_bytes_after'], 15964218)
        self.assertEqual(
            record['manifest_sha256_before'],
            'b93e4b97830ff15aca1a9e77847796e5ddd5cb7e1f3cd6512db20a358c159622')
        self.assertEqual(
            record['manifest_sha256_after'],
            'c815dc4ed02a9b7d0bd1487c3e1ed4e39d0bc826659d4ff0fb7f8a37ff685cdf')


if __name__ == '__main__':
    unittest.main()
