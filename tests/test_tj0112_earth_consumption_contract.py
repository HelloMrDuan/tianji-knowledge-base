"""TJ-011.2 earth-root consumption contract (E0257): public contracts.

Adjudication-only batch: the consumption contract must cover exactly
the 24 registered cells grade by grade, the only eligible cells must
be the two per-stem-listed Lu positions, conflicted cells must be
blocked, ungraded structural cells must be adjudicated NOT eligible
(with the anti-mechanical-integration clause registered), no-root
cells must be fact-consumption only, the S2 channel-three review must
leave channels one/two and the unrealizable conclusion unchanged
while restating channel three, the surface audit must cover all
seven predicates plus D-1 with zero earth-root consumption, and --
as adjudicated at E0257 -- no runtime module imported the earth
register (zero wiring). E0355 state transition: the contract's one
adjudicated landing point (registered_eligible in
bazi_action_conditions) is now wired to this contract's whitelist;
the wiring-locus test below pins the new state exactly (one locus,
contract-derived whitelist, the other runtime modules still clean).
"""
import inspect
import unittest
from pathlib import Path

from tianji_kb import bazi_earth_roots as E
from tianji_kb import bazi_metal_water_roots as M

SRC = Path(__file__).resolve().parents[1] / 'src' / 'tianji_kb'
STEMS = ('戊', '己')


def _cells_by_grade():
    out = {}
    for stem in STEMS:
        for cell in E.EARTH_ROOT_TABLES[stem]:
            out.setdefault(cell['grade'], set()).add(
                f"{stem}×{cell['branch']}")
    return out


class ContractCoverageTests(unittest.TestCase):
    def test_contract_identity(self):
        c = E.EARTH_CONSUMPTION_CONTRACT
        self.assertEqual(c['contract_id'],
                         'bazi-earth-root-consumption-contract-v1')
        self.assertEqual(c['event'], 'E0257')
        self.assertEqual(c['runtime_wiring'], 'none')

    def test_grade_contracts_cover_exactly_the_registered_cells(self):
        by_grade = _cells_by_grade()
        covered = set()
        for gc in E.EARTH_CONSUMPTION_CONTRACT['grade_contracts']:
            cells = set(gc['cells'])
            self.assertEqual(cells, by_grade.get(gc['grade'], set()),
                             gc['grade'])
            self.assertEqual(gc['count'], len(cells), gc['grade'])
            covered |= cells
        self.assertEqual(len(covered), 24)

    def test_counts_check(self):
        cc = E.EARTH_CONSUMPTION_CONTRACT['counts_check']
        self.assertEqual(cc, {'cells': 24, 'eligible': 2, 'blocked': 8,
                              'not_eligible': 14})

    def test_only_lu_cells_eligible(self):
        by_grade = {gc['grade']: gc for gc in
                    E.EARTH_CONSUMPTION_CONTRACT['grade_contracts']}
        self.assertEqual(by_grade['per_stem_listed']['eligibility'],
                         'eligible')
        self.assertEqual(set(by_grade['per_stem_listed']['cells']),
                         {'戊×巳', '己×午'})
        self.assertEqual(by_grade['per_stem_listed']['anchor_type'],
                         'per_stem_listed_heavy_root')
        heavy = {s: set(v) for s, v in E.HEAVY_ROOT_BRANCHES.items()}
        self.assertEqual(heavy, {'戊': {'巳'}, '己': {'午'}})

    def test_framework_derived_has_no_consumable_cells(self):
        gc = {g['grade']: g for g in
              E.EARTH_CONSUMPTION_CONTRACT['grade_contracts']}
        self.assertEqual(gc['framework_derived']['cells'], [])
        self.assertEqual(gc['framework_derived']['count'], 0)

    def test_conflicted_cells_blocked(self):
        gc = {g['grade']: g for g in
              E.EARTH_CONSUMPTION_CONTRACT['grade_contracts']}
        self.assertEqual(gc['conflicted_pending']['eligibility'],
                         'blocked')
        pending = {f"{s}×{b}" for s, bs in
                   E.PENDING_ROOT_BRANCHES.items() for b in bs}
        self.assertEqual(set(gc['conflicted_pending']['cells']),
                         pending)

    def test_ungraded_cells_adjudicated_not_eligible(self):
        gc = {g['grade']: g for g in
              E.EARTH_CONSUMPTION_CONTRACT['grade_contracts']}
        u = gc['structural_present_ungraded']
        self.assertEqual(u['eligibility'], 'not_eligible_unreviewed')
        ungraded = {f"{s}×{b}" for s, bs in
                    E.UNGRADED_STRUCTURAL_BRANCHES.items() for b in bs}
        self.assertEqual(set(u['cells']), ungraded)
        # The anti-mechanical-integration clause must be registered:
        # the exclusion-rule shape would miscount these cells.
        self.assertIn('误计', u['statement'])
        self.assertIn('白名单', u['statement'])
        joined = ' '.join(
            E.EARTH_CONSUMPTION_CONTRACT['forbidden_integrations'])
        self.assertIn('排除法', joined)

    def test_no_root_cells_fact_consumption_only(self):
        gc = {g['grade']: g for g in
              E.EARTH_CONSUMPTION_CONTRACT['grade_contracts']}
        n = gc['no_root']
        self.assertEqual(n['eligibility'],
                         'not_eligible_no_root_fact')
        self.assertEqual(len(n['cells']), 6)


class Channel3ReviewTests(unittest.TestCase):
    def test_review_structure(self):
        r = E.CHANNEL3_REVIEW_E0257
        self.assertEqual(r['event'], 'E0257')
        self.assertEqual(len(r['channels']), 3)
        self.assertFalse(r['runtime_surface_changed'])

    def test_channels_one_two_unchanged_and_root_table_free(self):
        r = E.CHANNEL3_REVIEW_E0257
        for ch in r['channels'][:2]:
            self.assertEqual(ch['verdict'], 'unchanged')
            self.assertFalse(ch['consumes_root_table'])

    def test_channel_three_restated(self):
        r = E.CHANNEL3_REVIEW_E0257
        ch = r['channels'][2]
        self.assertTrue(ch['consumes_root_table'])
        self.assertEqual(
            ch['verdict'],
            'restated_premise_overturned_runtime_unchanged')

    def test_conclusion_not_rejudged(self):
        r = E.CHANNEL3_REVIEW_E0257
        self.assertEqual(r['conclusion']['metal_you_status'],
                         'chart_unrealizable')
        self.assertEqual(r['conclusion']['verdict'],
                         'unchanged_not_rejudged')
        self.assertEqual(M.METAL_YOU_SATISFIABILITY['status'],
                         'chart_unrealizable')

    def test_metal_register_carries_the_correction(self):
        sat = M.METAL_YOU_SATISFIABILITY
        self.assertIn('review_e0257', sat)
        rev = sat['review_e0257']
        self.assertEqual(rev['channel_1_verdict'],
                         'unchanged_calendar_fact')
        self.assertEqual(rev['channel_2_verdict'],
                         'unchanged_calendar_fact')
        self.assertEqual(rev['conclusion_verdict'],
                         'chart_unrealizable_unchanged')
        self.assertFalse(rev['runtime_verdict_surface_changed'])
        ch3 = sat['proof_channels'][2]['argument']
        # Historical premise stays visible as history; the current
        # register state and the unwired runtime must both be stated.
        self.assertIn('土根零登记', ch3)
        self.assertIn('E0250', ch3)
        self.assertIn('登记已', ch3)
        self.assertIn('未接入', ch3)
        # Channels one and two keep their original arguments.
        self.assertIn('只有酉', sat['proof_channels'][0]['argument'])
        self.assertIn('五虎遁', sat['proof_channels'][1]['argument'])

    def test_water_ren_proof_untouched(self):
        w = M.WATER_ZI_SATISFIABILITY
        self.assertEqual(w['status'], 'satisfiable_for_gui_only')
        self.assertEqual(
            w['ren_unrealizable']['status'], 'chart_unrealizable')
        self.assertEqual(len(w['ren_unrealizable']['proof_channels']),
                         2)


class SurfaceAuditTests(unittest.TestCase):
    def test_audit_verdict_zero_consumption(self):
        a = E.CONSUMPTION_SURFACE_AUDIT_E0257
        self.assertEqual(
            a['verdict'],
            'contract_ready_zero_runtime_consumption_zero_'
            'verdict_surface_change')
        self.assertEqual(len(a['surfaces']), 6)

    def test_audit_covers_seven_predicates_and_d1(self):
        joined = ' '.join(s['surface'] for s in
                          E.CONSUMPTION_SURFACE_AUDIT_E0257['surfaces'])
        for name in ('pure_support', 'pure_generating_support',
                     'isolated_control', 'commanding_visible_support',
                     'lu_visible_support', 'pure_support_metal',
                     'pure_generating_support_water', 'D-1'):
            self.assertIn(name, joined)
        for s in E.CONSUMPTION_SURFACE_AUDIT_E0257['surfaces']:
            self.assertTrue(
                s['earth_root_consumption'].startswith('none'),
                s['surface'])

    def test_wiring_locus_is_exactly_the_contract_surface(self):
        # E0355 state transition (was test_no_runtime_wiring_anywhere
        # at E0257, when zero wiring was the adjudicated state): the
        # contract's single landing point is now wired, and ONLY
        # there. bazi_action_conditions derives its earth whitelist
        # from this contract record; it must not consume the raw
        # grading table (the exclusion shape over EARTH_ROOT_TABLES
        # is the contract's forbidden mechanical integration), and
        # the other runtime modules stay entirely clean.
        text = (SRC / 'bazi_action_conditions.py').read_text('utf-8')
        self.assertIn('EARTH_CONSUMPTION_CONTRACT', text)
        self.assertNotIn('EARTH_ROOT_TABLES', text)
        for name in ('bazi_adjudication.py', 'bazi_strength.py',
                     'bazi_pattern.py'):
            text = (SRC / name).read_text('utf-8')
            self.assertNotIn('bazi_earth_roots', text, name)
            self.assertNotIn('EARTH_ROOT_TABLES', text, name)
            self.assertNotIn('EARTH_CONSUMPTION_CONTRACT', text, name)

    def test_preconditions_registered(self):
        pre = E.FUTURE_INTEGRATION_PRECONDITIONS_E0257
        self.assertEqual(len(pre), 7)
        joined = ' '.join(pre)
        self.assertIn('白名单', joined)
        self.assertIn('principal', joined)
        self.assertIn('藏干根位资格', joined)
        self.assertIn('effective', joined)

    def test_register_stays_pure_data(self):
        members = inspect.getmembers(E)
        bad = [n for n, v in members
               if (inspect.isfunction(v) or inspect.isclass(v))
               and getattr(v, '__module__', None) == E.__name__]
        self.assertEqual(bad, [])
        import_lines = [ln for ln in inspect.getsource(E).splitlines()
                        if ln.startswith(('import ', 'from '))]
        self.assertEqual(import_lines, [])


if __name__ == '__main__':
    unittest.main()
