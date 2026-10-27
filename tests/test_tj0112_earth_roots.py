"""TJ-011.2 earth (Wu/Ji) root grading: public structural contracts.

Adjudication + registration batch only: the register must stay pure
data (zero functions), every one of the 24 stem x branch cells must be
graded or explicitly pending/ungraded, the only heavy roots must be
the two Lu positions (per-stem listed, triple stem-level attestation),
no Diwang cell may be graded (all four branch Diwang cells stay
conflicted_pending and framework_derived count is zero), the Tu
Changsheng conflict must stay unadjudicated with branch readings
matching the affected cells, the light-root layer must stay empty
(the Ditiansui listings enumerate no earth pair), the ungraded
structural cells must all carry a hidden-stem presence fact, and no
runtime module may import this register (zero consumption wiring in
this batch).

Verbatim quote equality against the sealed snapshots lives in
test_tj0112_earth_roots_sealed.py (offline acceptance only,
NOT public CI).
"""
import inspect
import unittest
from pathlib import Path

from tianji_kb import bazi_earth_roots as E
from tianji_kb import bazi_metal_water_roots as M
from tianji_kb import bazi_fire_morphology as F
from tianji_kb import bazi_sanming_juan2_collation as C18
from tianji_kb import bazi_pattern as P

BRANCHES = ['子', '丑', '寅', '卯', '辰', '巳',
            '午', '未', '申', '酉', '戌', '亥']
STEMS = ['戊', '己']
GRADES = {'per_stem_listed', 'framework_derived',
          'light_listed_conflicted', 'conflicted_pending',
          'structural_present_ungraded', 'no_root'}
SRC = Path(__file__).resolve().parents[1] / 'src' / 'tianji_kb'


class PureDataTests(unittest.TestCase):
    def test_module_has_no_functions_or_classes(self):
        members = inspect.getmembers(E)
        bad = [n for n, v in members
               if (inspect.isfunction(v) or inspect.isclass(v))
               and getattr(v, '__module__', None) == E.__name__]
        self.assertEqual(bad, [])

    def test_register_identity(self):
        self.assertEqual(E.EARTH_REGISTER_ID,
                         'bazi-earth-root-grading-v1')
        self.assertEqual(E.EARTH_TASK, 'TJ-011.2')

    def test_no_imports_at_all(self):
        import_lines = [ln for ln in inspect.getsource(E).splitlines()
                        if ln.startswith(('import ', 'from '))]
        self.assertEqual(import_lines, [])


class QuoteRegistrationTests(unittest.TestCase):
    def test_quotes_locator_self_consistent(self):
        chars = E.EARTH_SNAPSHOTS['sanming_tonghui.txt']['chars']
        self.assertEqual(len(E.EARTH_QUOTES), 6)
        for q in E.EARTH_QUOTES:
            loc = q['locator']
            self.assertEqual(loc['char_end'] - loc['char_start'],
                             len(q['quote']), q['id'])
            self.assertEqual(q['source_id'],
                             'bazi.source.sanmingtonghui')
            self.assertLessEqual(loc['char_end'], chars)
        # All quotes sit inside the TJ-018-A registered section window.
        for q in E.EARTH_QUOTES:
            self.assertGreaterEqual(q['locator']['char_start'], 38890)
            self.assertLessEqual(q['locator']['char_end'], 43082)

    def test_collated_quote_carries_mapped_reading(self):
        by_id = {q['id']: q for q in E.EARTH_QUOTES}
        # Wu's Lu quote keeps the snapshot glyph Ji (read Si) in the
        # quote text; the reading lives in mapped_reading only.
        self.assertIn('己', by_id['sm.wu_lu']['quote'])
        self.assertIn('爲', by_id['sm.wu_lu']['quote'])
        self.assertIn('sm2-ji-40135',
                      by_id['sm.wu_lu']['collation_refs'])
        self.assertIn('读巳', by_id['sm.wu_lu']['mapped_reading'])

    def test_quote_anchors_agree_with_018a_coverage(self):
        cov = {row['stem']: row for row in C18.STEM_COVERAGE}
        self.assertEqual(cov['戊']['lu']['locator']['char_start'],
                         40132)
        self.assertEqual(cov['戊']['si']['locator']['char_start'],
                         40230)
        self.assertEqual(cov['己']['lu']['locator']['char_start'],
                         40448)
        self.assertEqual(cov['己']['si']['locator']['char_start'],
                         40515)
        by_id = {q['id']: q for q in E.EARTH_QUOTES}
        self.assertEqual(by_id['sm.wu_lu']['locator']['char_start'],
                         cov['戊']['lu']['locator']['char_start'])
        self.assertEqual(by_id['sm.wu_shengsi']['locator']
                         ['char_start'],
                         cov['戊']['si']['locator']['char_start'])
        self.assertEqual(by_id['sm.ji_lu']['locator']['char_start'],
                         cov['己']['lu']['locator']['char_start'])
        self.assertEqual(by_id['sm.ji_shengsi']['locator']
                         ['char_start'],
                         cov['己']['si']['locator']['char_start'])
        self.assertEqual(C18.ROOT_TABLE_ASSESSMENT['verdict'],
                         'partial')


class RootTableCompletenessTests(unittest.TestCase):
    def test_all_24_cells_present_in_branch_order(self):
        self.assertEqual(set(E.EARTH_ROOT_TABLES), set(STEMS))
        for stem in STEMS:
            table = E.EARTH_ROOT_TABLES[stem]
            self.assertEqual([c['branch'] for c in table], BRANCHES,
                             stem)

    def test_grade_counts_match_assessment(self):
        counts = {}
        for stem in STEMS:
            for cell in E.EARTH_ROOT_TABLES[stem]:
                self.assertIn(cell['grade'], GRADES, (stem, cell))
                counts[cell['grade']] = counts.get(cell['grade'], 0) + 1
        a = E.ROOT_TABLE_ASSESSMENT_EARTH['counts']
        self.assertEqual(counts.get('per_stem_listed', 0),
                         a['heavy_per_stem_listed'])
        self.assertEqual(counts.get('framework_derived', 0),
                         a['heavy_framework_derived'])
        self.assertEqual(counts.get('conflicted_pending', 0),
                         a['conflicted_pending'])
        self.assertEqual(counts.get('structural_present_ungraded', 0),
                         a['structural_present_ungraded'])
        self.assertEqual(counts.get('light_listed_conflicted', 0),
                         a['light_listed'])
        self.assertEqual(counts.get('no_root', 0), a['no_root'])
        self.assertEqual(sum(counts.values()), a['cells'])
        # The honest headline: derived heavy count is zero and the
        # light layer is empty for earth.
        self.assertEqual(a['heavy_framework_derived'], 0)
        self.assertEqual(a['light_listed'], 0)

    def test_grade_sets_agree_with_cells(self):
        for stem in STEMS:
            cells = {c['branch']: c
                     for c in E.EARTH_ROOT_TABLES[stem]}
            heavy = {b for b, c in cells.items() if c['is_heavy']}
            pending = {b for b, c in cells.items()
                       if c['grade'] == 'conflicted_pending'}
            ungraded = {b for b, c in cells.items()
                        if c['grade'] ==
                        'structural_present_ungraded'}
            light = {b for b, c in cells.items()
                     if c['grade'] == 'light_listed_conflicted'}
            self.assertEqual(heavy,
                             set(E.HEAVY_ROOT_BRANCHES[stem]), stem)
            self.assertEqual(pending,
                             set(E.PENDING_ROOT_BRANCHES[stem]), stem)
            self.assertEqual(ungraded,
                             set(E.UNGRADED_STRUCTURAL_BRANCHES[stem]),
                             stem)
            self.assertEqual(light,
                             set(E.LIGHT_ROOT_BRANCHES[stem]), stem)
            for b in pending | ungraded:
                self.assertIsNone(cells[b]['is_heavy'], (stem, b))

    def test_is_heavy_consistency(self):
        for stem in STEMS:
            for cell in E.EARTH_ROOT_TABLES[stem]:
                if cell['grade'] == 'per_stem_listed':
                    self.assertTrue(cell['is_heavy'], (stem, cell))
                elif cell['grade'] == 'no_root':
                    self.assertFalse(cell['is_heavy'], (stem, cell))

    def test_palace_sequences_self_consistent(self):
        # Branch A must agree with the per-stem sentences: its Linguan
        # is the Lu branch and its Si is the per-stem death branch.
        deaths = {'戊': '酉', '己': '寅'}
        for stem in STEMS:
            seq = E.PALACE_SEQUENCES[stem]
            self.assertEqual(set(seq['branch_a']), set(BRANCHES))
            self.assertEqual(set(seq['branch_b']), set(BRANCHES))
            lu = E.HEAVY_ROOT_BRANCHES[stem][0]
            a = seq['branch_a']
            self.assertEqual(a[lu], '临官', stem)
            self.assertEqual(a[deaths[stem]], '死', stem)
            # Branch B is the shared water/earth sequence for both
            # stems and agrees with the Shenfeng element tables.
            b = seq['branch_b']
            self.assertEqual(b['申'], '长生', stem)
            self.assertEqual(b['亥'], '临官', stem)
            self.assertEqual(b['辰'], '墓', stem)
            self.assertEqual(b['巳'], '绝', stem)
        self.assertEqual(E.PALACE_SEQUENCES['戊']['branch_b'],
                         E.PALACE_SEQUENCES['己']['branch_b'])


class LuAttestationTests(unittest.TestCase):
    def test_lu_positions_listed_and_branch_independent(self):
        expected = {'戊': '巳', '己': '午'}
        quotes18 = {q['id']: q for q in C18.COLLATION_QUOTES}
        self.assertIn('丙戊禄在巳', quotes18['sf.lubiao']['quote'])
        self.assertIn('丁己禄居午', quotes18['sf.lubiao']['quote'])
        # Sanming juan3 Lu sentences (Slice A register) agree.
        self.assertEqual(P.LU_BRANCH['戊'], '巳')
        self.assertEqual(P.LU_BRANCH['己'], '午')
        for stem, branch in expected.items():
            cells = {c['branch']: c
                     for c in E.EARTH_ROOT_TABLES[stem]}
            self.assertEqual(cells[branch]['grade'],
                             'per_stem_listed', stem)
            self.assertTrue(cells[branch]['is_heavy'], stem)
            self.assertNotIn(branch, E.PENDING_ROOT_BRANCHES[stem])
            self.assertNotIn(branch,
                             E.UNGRADED_STRUCTURAL_BRANCHES[stem])


class DiwangDisciplineTests(unittest.TestCase):
    def test_diwang_never_graded(self):
        cells = {}
        for stem in STEMS:
            for c in E.EARTH_ROOT_TABLES[stem]:
                cells[(stem, c['branch'])] = c
        # All four branch-Diwang cells are conflicted_pending.
        for key in (('戊', '午'), ('戊', '子'),
                    ('己', '巳'), ('己', '子')):
            self.assertEqual(cells[key]['grade'],
                             'conflicted_pending', key)
            self.assertIn('帝旺', cells[key]['position_kind'], key)
        # No cell anywhere is framework_derived, and no Diwang cell
        # may carry a listed grade.
        for (stem, branch), c in cells.items():
            self.assertNotEqual(c['grade'], 'framework_derived',
                                (stem, branch))
            if '帝旺' in c['position_kind']:
                self.assertNotEqual(c['grade'], 'per_stem_listed',
                                    (stem, branch))

    def test_diwang_disposition_registered(self):
        d = E.DIWANG_DISPOSITION
        self.assertEqual(
            d['verdict'],
            'branch_pending_for_both_stems_no_uncontested_cell')
        derived = {(p['stem'], p['branch'], p['under_branch'])
                   for p in d['derived_positions']}
        self.assertEqual(derived,
                         {('戊', '午', 'branch_a'),
                          ('戊', '子', 'branch_b'),
                          ('己', '巳', 'branch_a'),
                          ('己', '子', 'branch_b')})
        self.assertEqual(len(d['forbidden_phrasings']), 8)


class TuChangshengConflictTests(unittest.TestCase):
    def test_conflict_unadjudicated_same_genre_as_others(self):
        conf = E.TU_CHANGSHENG_CONFLICT
        self.assertEqual(conf['conflict_id'],
                         'sanming-juan2.tu-changsheng')
        self.assertEqual(conf['status'], 'conflict')
        self.assertIsNone(conf['adjudication'])
        self.assertTrue(conf['research_only'])
        self.assertEqual(len(conf['branches']), 2)
        # The other Changsheng conflicts stay untouched.
        self.assertIsNone(C18.DING_CHANGSHENG_CONFLICT
                          ['adjudication'])
        self.assertIsNone(M.XIN_CHANGSHENG_CONFLICT['adjudication'])
        self.assertIsNone(M.GUI_CHANGSHENG_CONFLICT['adjudication'])

    def test_conflict_branch_readings(self):
        branches = {b['branch_id']: b['reading']
                    for b in E.TU_CHANGSHENG_CONFLICT['branches']}
        self.assertEqual(branches,
                         {'tu-sheng-yin-you': {'戊': '寅', '己': '酉'},
                          'tu-sheng-shen': {'戊': '申', '己': '申'}})

    def test_affected_cells_match_pending_cells(self):
        conf = E.TU_CHANGSHENG_CONFLICT
        affected = {(row['stem'], row['branch'])
                    for row in conf['affected_cells']}
        pending = {(stem, b) for stem in STEMS
                   for b in E.PENDING_ROOT_BRANCHES[stem]}
        self.assertEqual(affected, pending)
        for stem, branch in affected:
            cells = {c['branch']: c
                     for c in E.EARTH_ROOT_TABLES[stem]}
            self.assertEqual(cells[branch]['conflict_id'],
                             conf['conflict_id'], (stem, branch))
        # Both stems are affected (unlike metal/water, where only
        # the yin stems were).
        self.assertEqual({s for s, _ in affected}, {'戊', '己'})


class LightRootGapTests(unittest.TestCase):
    def test_no_light_cells_and_status_registered(self):
        status = E.EARTH_LIGHT_ROOT_STATUS
        self.assertEqual(status['status'],
                         'no_listing_basis_registered_gap')
        self.assertEqual(len(status['candidate_bases_not_adopted']),
                         2)
        for stem in STEMS:
            for cell in E.EARTH_ROOT_TABLES[stem]:
                self.assertNotIn('light', cell['grade'],
                                 (stem, cell))

    def test_ditiansui_listings_enumerate_no_earth_pair(self):
        quotes_f = {q['id']: q for q in F.MORPHOLOGY_QUOTES}
        for qid in ('dt.root_mu', 'dt.root_yuqi_1', 'dt.root_yuqi_2'):
            quote = quotes_f[qid]['quote']
            self.assertNotIn('戊己', quote, qid)
            self.assertNotIn('戊逢', quote, qid)
            self.assertNotIn('己逢', quote, qid)
        # The heavy/light framework sentence itself is element-free.
        self.assertIn('长生禄旺,根之重者也',
                      quotes_f['dt.root_heavy_light']['quote'])

    def test_ungraded_cells_carry_structural_presence(self):
        for stem in STEMS:
            cells = {c['branch']: c
                     for c in E.EARTH_ROOT_TABLES[stem]}
            for branch in E.UNGRADED_STRUCTURAL_BRANCHES[stem]:
                cell = cells[branch]
                notes = ' '.join(ev.get('note', '')
                                 for ev in cell['evidence'])
                self.assertIn('藏', notes, (stem, branch))
                self.assertIn('结构', cell['position_kind'],
                              (stem, branch))
        # The ungraded set is exactly the four earth branches for
        # both stems, and every earth branch hides an earth stem.
        for stem in STEMS:
            self.assertEqual(
                set(E.UNGRADED_STRUCTURAL_BRANCHES[stem]),
                {'丑', '辰', '未', '戌'})
        self.assertEqual(set(E.ELEMENT_STRUCTURAL_BRANCHES),
                         {'丑', '寅', '辰', '巳', '午', '未', '申',
                          '戌'})
        for stem in STEMS:
            for branch in E.STRUCTURAL_ROOT_BRANCHES[stem]:
                self.assertIn(branch, E.ELEMENT_STRUCTURAL_BRANCHES)


class InterfaceAndScopeTests(unittest.TestCase):
    def test_policy_untouched_declaration(self):
        self.assertEqual(E.POLICY_ALIGNMENT['policy_files_changed'],
                         [])
        self.assertIn('无土集', E.POLICY_ALIGNMENT['reference'])

    def test_consumption_audit_surfaces(self):
        audit = E.CONSUMPTION_AUDIT
        surfaces = [s['surface'] for s in audit['surfaces']]
        self.assertEqual(len(surfaces), 5)
        joined = ' '.join(surfaces)
        self.assertIn('通道三', joined)
        self.assertIn('EARTH_ROOT_INTERFACE', joined)
        self.assertIn('土日主', joined)
        self.assertIn('不改 bazi_action_conditions.py',
                      audit['surfaces'][0]['still_pending'][0])
        self.assertIn('零', audit['statement'])

    def test_no_runtime_wiring(self):
        # This batch registers data only: no runtime module may
        # reference the earth register yet (consumption is a later
        # batch with its own adjudication preconditions).
        for name in ('bazi_action_conditions.py',
                     'bazi_adjudication.py', 'bazi_strength.py'):
            text = (SRC / name).read_text('utf-8')
            self.assertNotIn('bazi_earth_roots', text, name)
            self.assertNotIn('EARTH_ROOT_TABLES', text, name)

    def test_prior_registers_regression(self):
        # Values this batch cites from earlier registers must be
        # unchanged: S1 counts, the metal unsatisfiability channel
        # three text (its correction belongs to the consumption
        # batch, not this one), the fire register sets, and the F34
        # earth interface registration.
        self.assertEqual(
            M.ROOT_TABLE_ASSESSMENT_S1['counts']['cells'], 48)
        channels = M.METAL_YOU_SATISFIABILITY['proof_channels']
        self.assertIn('土根零登记', channels[2]['argument'])
        self.assertEqual(F.BING_ALL_ROOT_BRANCHES,
                         ['寅', '巳', '午', '未', '戌'])
        from tianji_kb import bazi_fire_si_yin_morphology as F34
        self.assertIn('Standing gap',
                      F34.EARTH_ROOT_INTERFACE['gap'])

    def test_assessment_verdict(self):
        self.assertEqual(
            E.ROOT_TABLE_ASSESSMENT_EARTH['verdict'],
            'graded_with_registered_conflict_and_ungraded_light_'
            'layer')


if __name__ == '__main__':
    unittest.main()
