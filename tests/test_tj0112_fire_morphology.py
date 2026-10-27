"""TJ-011.2 fire-line morphology adjudication: public structural contracts.

Design batch only: the registration module must stay pure data (zero
functions), the form definition must carry complete, honestly labeled
anchors (original text vs governance convention vs scope construction),
the Wu root position must stay framework_derived (never per-stem
listed), the Zi weak form must stay not_buildable with its Wuhudun
proof intact, the Ding line must stay blocked by the SAME conflict id
registered in TJ-018-A, and the four Golden design cases must be
structurally self-consistent (legal pillars, Bing day master, Wu month,
condition tables covering exactly the form's nine conditions, design
expectations consistent with their own tables).

Verbatim quote equality against the sealed snapshots and real-calendar
pillar verification live in test_tj0112_fire_morphology_sealed.py
(offline acceptance only, NOT public CI).
"""
import inspect
import json
from pathlib import Path
import unittest

from tianji_kb import bazi_fire_morphology as M
from tianji_kb import bazi_sanming_juan2_collation as C18

ROOT = Path(__file__).resolve().parents[1]
GOLDEN = json.loads(
    (ROOT / 'tests/golden_tj0112_fire_morphology.json').read_text('utf-8'))

STEMS = '甲乙丙丁戊己庚辛壬癸'
BRANCHES = '子丑寅卯辰巳午未申酉戌亥'
GRADES = {'per_stem_listed', 'framework_derived', 'light_listed',
          'light_listed_conflicted'}
ANCHOR_TYPES = {'original_text', 'governance_convention',
                'scope_construction'}


class PureDataTests(unittest.TestCase):
    def test_module_has_no_functions_or_classes(self):
        members = inspect.getmembers(M)
        bad = [n for n, v in members
               if (inspect.isfunction(v) or inspect.isclass(v))
               and getattr(v, '__module__', None) == M.__name__]
        self.assertEqual(bad, [])

    def test_register_identity(self):
        self.assertEqual(M.MORPHOLOGY_REGISTER_ID,
                         'bazi-fire-morphology-adjudication-v1')
        self.assertEqual(M.MORPHOLOGY_TASK, 'TJ-011.2')
        self.assertTrue(M.FORM_BING_WU['research_only'])
        self.assertFalse(M.FORM_BING_WU['public_enabled'])
        self.assertFalse(M.FORM_BING_WU['ai_enabled'])


class QuoteRegistrationTests(unittest.TestCase):
    def test_quotes_locator_self_consistent(self):
        chars = M.MORPHOLOGY_SNAPSHOTS['ditiansui_chanwei.txt']['chars']
        self.assertEqual(len(M.MORPHOLOGY_QUOTES), 10)
        for q in M.MORPHOLOGY_QUOTES:
            loc = q['locator']
            self.assertEqual(loc['char_end'] - loc['char_start'],
                             len(q['quote']), q['id'])
            self.assertGreaterEqual(loc['char_start'], 0)
            self.assertLessEqual(loc['char_end'], chars)
            self.assertEqual(q['source_id'], 'bazi.source.ditiansui-spouse')

    def test_definition_layers(self):
        layers = {q['id']: q['layer'] for q in M.MORPHOLOGY_QUOTES}
        # The isolated (weak) definition is the original commentary;
        # the strong definitions and root enumeration are Ren's.
        self.assertEqual(layers['dt.guli_def'], '原注')
        for qid in ('dt.congwang_def', 'dt.congqiang_def',
                    'dt.root_heavy_light'):
            self.assertEqual(layers[qid], '任氏曰', qid)

    def test_anchor_offsets_match_prior_audits(self):
        by_id = {q['id']: q for q in M.MORPHOLOGY_QUOTES}
        self.assertEqual(by_id['dt.guli_def']['locator']['char_start'], 96219)
        self.assertEqual(by_id['dt.congwang_def']['locator']['char_start'], 96521)
        self.assertEqual(by_id['dt.congqiang_def']['locator']['char_start'], 96605)
        self.assertEqual(by_id['dt.root_heavy_light']['locator']['char_start'],
                         39967)


class RootPositionTests(unittest.TestCase):
    def test_branch_set_and_heavy_set(self):
        self.assertEqual([r['branch'] for r in M.BING_ROOT_POSITIONS],
                         ['寅', '巳', '午', '未', '戌'])
        self.assertEqual(M.BING_HEAVY_ROOT_BRANCHES, ['寅', '巳', '午'])
        self.assertEqual(M.BING_ALL_ROOT_BRANCHES,
                         ['寅', '巳', '午', '未', '戌'])
        heavy = {r['branch'] for r in M.BING_ROOT_POSITIONS if r['is_heavy']}
        self.assertEqual(heavy, set(M.BING_HEAVY_ROOT_BRANCHES))

    def test_grades_pinned(self):
        grades = {r['branch']: r['grade'] for r in M.BING_ROOT_POSITIONS}
        self.assertEqual(grades['寅'], 'per_stem_listed')
        self.assertEqual(grades['巳'], 'per_stem_listed')
        # The whole point of adjudication two: Wu is DERIVED, never listed.
        self.assertEqual(grades['午'], 'framework_derived')
        self.assertEqual(grades['未'], 'light_listed')
        self.assertEqual(grades['戌'], 'light_listed_conflicted')
        self.assertTrue(set(grades.values()) <= GRADES)

    def test_xu_conflict_link(self):
        xu = next(r for r in M.BING_ROOT_POSITIONS if r['branch'] == '戌')
        self.assertEqual(xu['conflict_id'],
                         'bazi.concept.conflict_root_type_readings')

    def test_positions_agree_with_018a_registration(self):
        cov = {row['stem']: row for row in C18.STEM_COVERAGE}
        self.assertEqual(cov['丙']['sheng']['reading'], '生寅')
        self.assertIn('禄巳', cov['丙']['lu']['reading'])
        self.assertEqual(cov['丙']['si']['reading'], '死酉')
        self.assertEqual(C18.ROOT_TABLE_ASSESSMENT['verdict'], 'partial')
        self.assertIn('帝旺', C18.ROOT_TABLE_ASSESSMENT['derived_positions'])

    def test_diwang_disposition_registered(self):
        d = M.DIWANG_DISPOSITION
        self.assertEqual(
            d['verdict'],
            'substituted_by_framework_derivation_with_grade_disclosure')
        self.assertTrue(d['forbidden_phrasings'])


class FormDefinitionTests(unittest.TestCase):
    def test_form_identity_and_status(self):
        f = M.FORM_BING_WU
        self.assertEqual(f['form_id'], 'bing-wu-commanding-visible-support-v1')
        self.assertEqual(f['status'], 'adjudicated_design_not_implemented')
        self.assertEqual(f['day_master'], '丙')
        self.assertEqual(f['month_branch'], '午')
        self.assertEqual(f['classification_if_matched'], 'strong')
        self.assertEqual(f['never_yields'], ['weak'])
        # Must not reuse the v1 name: hidden-layer scope semantics differ.
        self.assertEqual(f['predicate_name_candidate'],
                         'commanding_visible_support')

    def test_nine_conditions_complete_and_labeled(self):
        conds = M.FORM_BING_WU['conditions']
        self.assertEqual(len(conds), 9)
        keys = [c['key'] for c in conds]
        self.assertEqual(len(set(keys)), 9)
        for c in conds:
            self.assertIn(c['anchor_type'], ANCHOR_TYPES, c['key'])
            self.assertTrue(c['statement'], c['key'])
            self.assertTrue(c['anchors'], c['key'])
        by_key = {c['key']: c for c in conds}
        # The hidden-layer condition is the governance convention and
        # must be labeled as such, never as original text.
        self.assertEqual(by_key['hidden_layer_convention_applied']
                         ['anchor_type'], 'governance_convention')
        # Definition-quantified conditions are original-text anchored.
        for key in ('visible_positions_support_only',
                    'visible_resource_present', 'visible_peer_present',
                    'reviewed_same_element_command_month'):
            self.assertEqual(by_key[key]['anchor_type'], 'original_text', key)

    def test_conventions_labeled_non_original(self):
        self.assertEqual(len(M.GOVERNANCE_CONVENTIONS), 2)
        for conv in M.GOVERNANCE_CONVENTIONS:
            self.assertIn('非原文', conv['label'])
        ji = next(c for c in M.GOVERNANCE_CONVENTIONS
                  if c['id'] == 'fire-morph.ji-in-wu-non-veto')
        self.assertIn('不否决', ji['statement'])
        self.assertIn('非原文', ji['anchor_status'])
        hidden = next(c for c in M.GOVERNANCE_CONVENTIONS
                      if c['id'].endswith('hidden-layer-root-facts-only'))
        self.assertIn('pure_support', hidden['divergence_from_v1'])

    def test_control_break_exclusions_cover_four_targets(self):
        targets = [e['target'] for e in
                   M.FORM_BING_WU['control_break_exclusions']]
        self.assertEqual(len(targets), 5)
        joined = ' '.join(targets)
        for needle in ('官杀', '财', '食伤', '藏干'):
            self.assertIn(needle, joined)

    def test_counterexamples_and_abstains_present(self):
        self.assertGreaterEqual(len(M.FORM_BING_WU['counterexamples']), 4)
        self.assertGreaterEqual(
            len(M.FORM_BING_WU['abstain_and_conflict_conditions']), 4)


class ZiWeakReviewTests(unittest.TestCase):
    def test_not_buildable_with_single_unsatisfiable(self):
        r = M.F5_ZI_WEAK_REVIEW
        self.assertEqual(r['verdict'], 'not_buildable')
        scope = {c['key']: c['satisfiable']
                 for c in r['scope_conditions_review']}
        self.assertEqual(len(scope), 7)
        unsat = [k for k, v in scope.items() if not v]
        self.assertEqual(unsat, ['month_principal_exposed_with_root'])
        defs = r['definition_requirements_review']
        self.assertEqual(len(defs), 4)
        self.assertTrue(all(d['satisfiable_in_zi_month'] for d in defs))

    def test_wuhudun_proof(self):
        p = M.F5_ZI_WEAK_REVIEW['wuhudun_proof']
        self.assertEqual(set(p['zi_month_stems']),
                         {'甲', '丙', '戊', '庚', '壬'})
        self.assertEqual(p['zi_principal_qi'], '癸')
        self.assertNotIn('癸', p['zi_month_stems'])

    def test_alternatives_rejected(self):
        verdicts = {a['verdict'] for a in
                    M.F5_ZI_WEAK_REVIEW['candidate_alternatives_reviewed']}
        self.assertEqual(verdicts,
                         {'rejected_no_anchor', 'rejected_widening'})


class DingBlockTests(unittest.TestCase):
    def test_block_matches_018a_conflict(self):
        self.assertEqual(M.DING_BLOCK['status'], 'blocked_by_conflict')
        self.assertEqual(M.DING_BLOCK['conflict_id'],
                         C18.DING_CHANGSHENG_CONFLICT['conflict_id'])
        self.assertIsNone(C18.DING_CHANGSHENG_CONFLICT['adjudication'])
        branches = {b['reading'] for b in
                    C18.DING_CHANGSHENG_CONFLICT['branches']}
        self.assertEqual(branches, {'酉', '寅'})

    def test_dispositions_cover_f1_to_f7(self):
        d = {row['id']: row['status'] for row in M.F_DISPOSITIONS}
        self.assertEqual(d, {
            'F1': 'adjudicated_design_not_implemented',
            'F2': 'blocked_by_conflict',
            'F3': 'not_adjudicated',
            'F4': 'deferred_not_adjudicated',
            'F5': 'not_buildable',
            'F6': 'not_buildable_no_definition',
            'F7': 'not_standalone'})


def _legal_gz(gz):
    return (len(gz) == 2 and gz[0] in STEMS and gz[1] in BRANCHES
            and STEMS.index(gz[0]) % 2 == BRANCHES.index(gz[1]) % 2)


class GoldenDesignTests(unittest.TestCase):
    def test_four_categories(self):
        cats = [c['category'] for c in GOLDEN['cases']]
        self.assertEqual(cats, ['positive_strong',
                                'outside_form_counterexample',
                                'abstain_unknown',
                                'conflict_presentation'])

    def test_cases_structurally_valid(self):
        form_keys = {c['key'] for c in M.FORM_BING_WU['conditions']}
        for case in GOLDEN['cases']:
            pillars = case['expected_pillars']
            self.assertEqual(len(pillars), 4, case['id'])
            for gz in pillars:
                self.assertTrue(_legal_gz(gz), (case['id'], gz))
            self.assertEqual(pillars[2][0], '丙', case['id'])   # day master
            self.assertEqual(pillars[1][1], '午', case['id'])   # Wu month
            table = {row['condition']: row['met']
                     for row in case['condition_table']}
            self.assertEqual(set(table), form_keys, case['id'])
            self.assertTrue(case['derivation'], case['id'])
            # Design expectation must agree with its own condition table.
            design = case['expect']['design_classification']
            if case['category'] == 'positive_strong':
                self.assertTrue(all(table.values()), case['id'])
                self.assertEqual(design, 'strong', case['id'])
            else:
                self.assertTrue(any(not v for v in table.values()),
                                case['id'])
                self.assertEqual(design, 'indeterminate', case['id'])
            # Nothing is implemented yet: current classification of every
            # design case must be recorded as indeterminate.
            self.assertEqual(case['expect']
                             ['current_implementation_classification'],
                             'indeterminate', case['id'])
            failed = {k for k, v in table.items() if not v}
            self.assertEqual(
                set(case['expect'].get('failed_conditions', [])), failed,
                case['id'])

    def test_conflict_case_names_registered_conflict(self):
        case = next(c for c in GOLDEN['cases']
                    if c['category'] == 'conflict_presentation')
        self.assertEqual(case['expect']['conflict_ids'],
                         ['bazi.concept.conflict_root_type_readings'])
        self.assertTrue(case['expect']['conflict_blocking'])


if __name__ == '__main__':
    unittest.main()
