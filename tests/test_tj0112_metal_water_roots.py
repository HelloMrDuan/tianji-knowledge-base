"""TJ-011.2 S1 metal/water root grading: public structural contracts.

Adjudication + registration batch only: the register must stay pure
data (zero functions), every one of the 48 stem x branch cells must be
graded or explicitly pending, the Diwang positions must never be
per-stem listed (framework_derived for Geng/Ren, conflicted_pending
for Xin/Gui), the Xin/Gui Changsheng conflicts must stay unadjudicated
with branch readings matching the affected cells, the Lu positions
must be branch-independent heavy roots with dual attestation, all
eight light roots must carry conflict annotations, and the sealed
policy must be untouched (this batch adds no predicate code and does
not import the adjudication modules).

Verbatim quote equality against the sealed snapshots lives in
test_tj0112_metal_water_roots_sealed.py (offline acceptance only,
NOT public CI).
"""
import inspect
import unittest

from tianji_kb import bazi_metal_water_roots as M
from tianji_kb import bazi_fire_morphology as F
from tianji_kb import bazi_sanming_juan2_collation as C18

BRANCHES = ['子', '丑', '寅', '卯', '辰', '巳',
            '午', '未', '申', '酉', '戌', '亥']
STEMS = ['庚', '辛', '壬', '癸']
GRADES = {'per_stem_listed', 'framework_derived',
          'light_listed_conflicted', 'conflicted_pending', 'no_root'}


class PureDataTests(unittest.TestCase):
    def test_module_has_no_functions_or_classes(self):
        members = inspect.getmembers(M)
        bad = [n for n, v in members
               if (inspect.isfunction(v) or inspect.isclass(v))
               and getattr(v, '__module__', None) == M.__name__]
        self.assertEqual(bad, [])

    def test_register_identity(self):
        self.assertEqual(M.ROOT_REGISTER_ID,
                         'bazi-metal-water-root-grading-v1')
        self.assertEqual(M.ROOT_TASK, 'TJ-011.2')

    def test_no_predicate_code_imported(self):
        # This batch registers data only; it must not pull in (or be
        # pulled into) the adjudication runtime. The register module
        # has no import statements at all (the adjudication module
        # names appear only inside prose notes).
        import_lines = [ln for ln in inspect.getsource(M).splitlines()
                        if ln.startswith(('import ', 'from '))]
        self.assertEqual(import_lines, [])


class QuoteRegistrationTests(unittest.TestCase):
    def test_quotes_locator_self_consistent(self):
        chars = M.ROOT_SNAPSHOTS['sanming_tonghui.txt']['chars']
        self.assertEqual(len(M.ROOT_QUOTES), 10)
        for q in M.ROOT_QUOTES:
            loc = q['locator']
            self.assertEqual(loc['char_end'] - loc['char_start'],
                             len(q['quote']), q['id'])
            self.assertEqual(q['source_id'],
                             'bazi.source.sanmingtonghui')
            self.assertLessEqual(loc['char_end'], chars)
        # All quotes sit inside the TJ-018-A registered section window.
        for q in M.ROOT_QUOTES:
            self.assertGreaterEqual(q['locator']['char_start'], 38890)
            self.assertLessEqual(q['locator']['char_end'], 43082)

    def test_collated_quotes_carry_mapped_readings(self):
        by_id = {q['id']: q for q in M.ROOT_QUOTES}
        # Geng's two glyph-corrected quotes keep the snapshot glyphs in
        # the quote and put the reading in mapped_reading only.
        self.assertIn('已', by_id['sm.geng_shengsi']['quote'])
        self.assertIn('sm2-yi-40755',
                      by_id['sm.geng_shengsi']['collation_refs'])
        self.assertIn('己', by_id['sm.geng_sheng_frag']['quote'])
        self.assertIn('sm2-ji-40674',
                      by_id['sm.geng_sheng_frag']['collation_refs'])
        # Gui's quote keeps the variant glyph Mao (邜) verbatim.
        self.assertIn('邜', by_id['sm.gui_shengsi']['quote'])

    def test_quote_anchors_agree_with_018a_coverage(self):
        cov = {row['stem']: row for row in C18.STEM_COVERAGE}
        self.assertEqual(cov['庚']['lu']['locator']['char_start'], 40653)
        self.assertEqual(cov['庚']['si']['locator']['char_start'], 40750)
        self.assertEqual(cov['辛']['lu']['locator']['char_start'], 40936)
        self.assertEqual(cov['辛']['si']['locator']['char_start'], 41083)
        self.assertEqual(cov['壬']['lu']['locator']['char_start'], 41235)
        self.assertEqual(cov['壬']['si']['locator']['char_start'], 41327)
        self.assertEqual(cov['癸']['lu']['locator']['char_start'], 41535)
        self.assertEqual(cov['癸']['si']['locator']['char_start'], 41664)
        self.assertEqual(C18.ROOT_TABLE_ASSESSMENT['verdict'], 'partial')


class RootTableCompletenessTests(unittest.TestCase):
    def test_all_48_cells_present_in_branch_order(self):
        self.assertEqual(set(M.METAL_WATER_ROOT_TABLES), set(STEMS))
        for stem in STEMS:
            table = M.METAL_WATER_ROOT_TABLES[stem]
            self.assertEqual([c['branch'] for c in table], BRANCHES,
                             stem)

    def test_grade_counts_match_assessment(self):
        counts = {}
        for stem in STEMS:
            for cell in M.METAL_WATER_ROOT_TABLES[stem]:
                self.assertIn(cell['grade'], GRADES, (stem, cell))
                counts[cell['grade']] = counts.get(cell['grade'], 0) + 1
        a = M.ROOT_TABLE_ASSESSMENT_S1['counts']
        self.assertEqual(counts['per_stem_listed'],
                         a['heavy_per_stem_listed'])
        self.assertEqual(counts['framework_derived'],
                         a['heavy_framework_derived'])
        self.assertEqual(counts['conflicted_pending'],
                         a['conflicted_pending'])
        self.assertEqual(counts['light_listed_conflicted'],
                         a['light_listed_conflicted'])
        self.assertEqual(counts['no_root'], a['no_root'])
        self.assertEqual(sum(counts.values()), a['cells'])

    def test_heavy_pending_light_sets_agree_with_cells(self):
        for stem in STEMS:
            cells = {c['branch']: c
                     for c in M.METAL_WATER_ROOT_TABLES[stem]}
            heavy = {b for b, c in cells.items() if c['is_heavy']}
            pending = {b for b, c in cells.items()
                       if c['grade'] == 'conflicted_pending'}
            light = {b for b, c in cells.items()
                     if c['grade'] == 'light_listed_conflicted'}
            self.assertEqual(heavy, set(M.HEAVY_ROOT_BRANCHES[stem]),
                             stem)
            self.assertEqual(pending,
                             set(M.PENDING_ROOT_BRANCHES[stem]), stem)
            self.assertEqual(light, set(M.LIGHT_ROOT_BRANCHES[stem]),
                             stem)
            for b in pending:
                self.assertIsNone(cells[b]['is_heavy'], (stem, b))

    def test_is_heavy_consistency(self):
        for stem in STEMS:
            for cell in M.METAL_WATER_ROOT_TABLES[stem]:
                if cell['grade'] in ('per_stem_listed',
                                     'framework_derived'):
                    self.assertTrue(cell['is_heavy'], (stem, cell))
                elif cell['grade'] in ('light_listed_conflicted',
                                       'no_root'):
                    self.assertFalse(cell['is_heavy'], (stem, cell))


class LuDualAttestationTests(unittest.TestCase):
    def test_lu_positions_listed_and_branch_independent(self):
        expected = {'庚': '申', '辛': '酉', '壬': '亥', '癸': '子'}
        quotes18 = {q['id']: q for q in C18.COLLATION_QUOTES}
        self.assertIn('庚禄居申', quotes18['sf.lubiao']['quote'])
        self.assertIn('辛禄居酉', quotes18['sf.lubiao']['quote'])
        self.assertIn('壬禄居亥', quotes18['sf.lubiao']['quote'])
        self.assertIn('癸禄居子', quotes18['sf.lubiao']['quote'])
        for stem, branch in expected.items():
            cells = {c['branch']: c
                     for c in M.METAL_WATER_ROOT_TABLES[stem]}
            self.assertEqual(cells[branch]['grade'], 'per_stem_listed',
                             stem)
            self.assertTrue(cells[branch]['is_heavy'], stem)
            # Lu never sits in the pending set of its stem.
            self.assertNotIn(branch, M.PENDING_ROOT_BRANCHES[stem])


class DiwangDisciplineTests(unittest.TestCase):
    def test_diwang_never_per_stem_listed(self):
        cells = {}
        for stem in STEMS:
            for c in M.METAL_WATER_ROOT_TABLES[stem]:
                cells[(stem, c['branch'])] = c
        self.assertEqual(cells[('庚', '酉')]['grade'],
                         'framework_derived')
        self.assertEqual(cells[('壬', '子')]['grade'],
                         'framework_derived')
        self.assertEqual(cells[('辛', '申')]['grade'],
                         'conflicted_pending')
        self.assertEqual(cells[('癸', '亥')]['grade'],
                         'conflicted_pending')
        # No cell anywhere may carry position 帝旺 with a listed grade.
        for (stem, branch), c in cells.items():
            if '帝旺' in c['position_kind']:
                self.assertNotEqual(c['grade'], 'per_stem_listed',
                                    (stem, branch))

    def test_diwang_disposition_registered(self):
        d = M.DIWANG_DISPOSITION
        derived = {(p['stem'], p['branch'])
                   for p in d['derived_positions']}
        self.assertEqual(derived, {('庚', '酉'), ('壬', '子')})
        self.assertTrue(d['forbidden_phrasings'])
        self.assertIn('framework_derived', d['statement'])


class ChangshengConflictTests(unittest.TestCase):
    def test_conflicts_unadjudicated_and_same_genre_as_ding(self):
        for conf in (M.XIN_CHANGSHENG_CONFLICT,
                     M.GUI_CHANGSHENG_CONFLICT):
            self.assertEqual(conf['status'], 'conflict')
            self.assertIsNone(conf['adjudication'])
            self.assertTrue(conf['research_only'])
            self.assertEqual(len(conf['branches']), 2)
        self.assertEqual(C18.DING_CHANGSHENG_CONFLICT['status'],
                         'conflict')
        self.assertIsNone(C18.DING_CHANGSHENG_CONFLICT['adjudication'])

    def test_conflict_branch_readings(self):
        xin = {b['branch_id']: b['reading']
               for b in M.XIN_CHANGSHENG_CONFLICT['branches']}
        self.assertEqual(xin, {'xin-sheng-zi': '子',
                               'xin-sheng-si': '巳'})
        gui = {b['branch_id']: b['reading']
               for b in M.GUI_CHANGSHENG_CONFLICT['branches']}
        self.assertEqual(gui, {'gui-sheng-mao': '卯',
                               'gui-sheng-shen': '申'})

    def test_affected_cells_match_pending_cells(self):
        for conf, stem in ((M.XIN_CHANGSHENG_CONFLICT, '辛'),
                           (M.GUI_CHANGSHENG_CONFLICT, '癸')):
            affected = {row['branch'] for row in conf['affected_cells']}
            self.assertEqual(affected,
                             set(M.PENDING_ROOT_BRANCHES[stem]))
            cells = {c['branch']: c
                     for c in M.METAL_WATER_ROOT_TABLES[stem]}
            for b in affected:
                self.assertEqual(cells[b]['conflict_id'],
                                 conf['conflict_id'], (stem, b))
        # The uncontested yang stems have no pending cells at all.
        self.assertEqual(M.PENDING_ROOT_BRANCHES['庚'], [])
        self.assertEqual(M.PENDING_ROOT_BRANCHES['壬'], [])


class LightRootConflictTests(unittest.TestCase):
    def test_all_light_cells_conflicted_with_subtypes(self):
        subtypes = set()
        for stem in STEMS:
            for cell in M.METAL_WATER_ROOT_TABLES[stem]:
                if cell['grade'] == 'light_listed_conflicted':
                    self.assertEqual(
                        cell['conflict_id'],
                        'bazi.concept.conflict_root_type_readings')
                    subtypes.add(cell['conflict_subtype'])
        self.assertEqual(subtypes, {'dual_listed_mu_yuqi',
                                    'yuqi_copies_disagree'})

    def test_light_cells_match_listing_conflict_register(self):
        reg = M.LIGHT_ROOT_LISTING_CONFLICTS
        self.assertEqual(
            reg['conflict_id'],
            'bazi.concept.conflict_root_type_readings')
        registered = set()
        for sub in reg['subtypes']:
            registered |= set(sub['cells'])
        actual = {f"{stem}×{b}" for stem in STEMS
                  for b in M.LIGHT_ROOT_BRANCHES[stem]}
        self.assertEqual(registered, actual)

    def test_derived_palace_names_do_not_create_light_roots(self):
        # Xin at Chen / Gui at Wei are palace-cycle Mu positions under
        # branch A only; with no listing and no structural stem of
        # their element, they must stay no_root.
        xin = {c['branch']: c for c in M.XIN_ROOT_POSITIONS}
        gui = {c['branch']: c for c in M.GUI_ROOT_POSITIONS}
        self.assertEqual(xin['辰']['grade'], 'no_root')
        self.assertEqual(gui['未']['grade'], 'no_root')


class AlignmentAndScopeTests(unittest.TestCase):
    def test_policy_untouched_declaration(self):
        self.assertEqual(M.WOOD_TABLE_ALIGNMENT['policy_files_changed'],
                         [])
        self.assertIn('不改动密封政策',
                      M.WOOD_TABLE_ALIGNMENT['statement'])

    def test_fire_register_regression(self):
        # Cross-register consistency: the fire batch's registered
        # values this batch cites must be unchanged.
        self.assertEqual(F.BING_ALL_ROOT_BRANCHES,
                         ['寅', '巳', '午', '未', '戌'])
        xu = next(r for r in F.BING_ROOT_POSITIONS
                  if r['branch'] == '戌')
        self.assertEqual(xu['conflict_id'],
                         'bazi.concept.conflict_root_type_readings')
        cov = {row['stem']: row for row in C18.STEM_COVERAGE}
        self.assertEqual(cov['丙']['sheng']['reading'], '生寅')

    def test_s2_impact_scope(self):
        impact = M.S2_IMPACT
        self.assertTrue(impact['unlocked'])
        self.assertTrue(impact['still_blocked'])
        self.assertIn('不写任何谓词', impact['statement'])
        self.assertEqual(M.ROOT_TABLE_ASSESSMENT_S1['verdict'],
                         'graded_with_registered_conflicts')


if __name__ == '__main__':
    unittest.main()
