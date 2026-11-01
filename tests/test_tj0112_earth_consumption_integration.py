"""TJ-011.2 earth-root consumption integration (E0355): public,
register-level contracts.

The E0257 consumption contract (bazi-earth-root-consumption-
contract-v1) is implemented at exactly one runtime locus --
registered_eligible in bazi_action_conditions -- as a cell-level
whitelist derived from the contract record. This module pins, at
data/import level (no sealed runtime needed, so it runs in public
CI):

- the derived whitelist is EXACTLY the two per-stem-listed Lu cells
  and the earth stem set is exactly {Wu, Ji};
- the whitelist is derived from the contract, whose adjudicated
  counts stay untouched (the E0257 record itself is history and is
  not rewritten by the wiring);
- the day-root effectiveness path is NOT wired for earth (the
  contract's precondition 5: the effective caliber is unreviewed) --
  the metal/water grade lookup still knows no earth stem;
- the integration records (earth register, metal satisfiability,
  S5 registration governance) disclose the wiring and keep the
  metal form's chart-unrealizable conclusion, now carried by the
  two calendar channels alone.

Engine/factor-level behaviour (the 24-cell exhaustive pin and the
real-chart Golden four classes) lives in
test_tj0112_earth_consumption_integration_sealed.py, which runs in
the offline assembled acceptance only.
"""
import unittest
from pathlib import Path

from tianji_kb import bazi_earth_roots as E
from tianji_kb import bazi_metal_water_roots as M
from tianji_kb.bazi_action_conditions import (
    _EARTH_ELIGIBLE_ROOT_CELLS, _EARTH_STEMS, _mw_root_grade)
from tianji_kb.bazi_registration_governance import (
    REGISTRATION_INVENTORY)

SRC = Path(__file__).resolve().parents[1] / 'src' / 'tianji_kb'


class WhitelistDerivationTests(unittest.TestCase):
    def test_whitelist_is_exactly_the_two_lu_cells(self):
        self.assertEqual(_EARTH_ELIGIBLE_ROOT_CELLS,
                         frozenset({('戊', '巳'), ('己', '午')}))
        self.assertEqual(_EARTH_STEMS, frozenset({'戊', '己'}))

    def test_whitelist_comes_from_the_contract_record(self):
        derived = {(gc_stem, branch)
                   for gc in E.EARTH_CONSUMPTION_CONTRACT[
                       'grade_contracts']
                   if gc['eligibility'] == 'eligible'
                   for cell in gc['cells']
                   for gc_stem, branch in [tuple(cell.split('×'))]}
        self.assertEqual(_EARTH_ELIGIBLE_ROOT_CELLS,
                         frozenset(derived))

    def test_contract_record_itself_unchanged(self):
        # The E0257 adjudication record is history: its counts and
        # its as-adjudicated runtime_wiring statement stay as
        # adjudicated; the wiring is recorded in the E0355
        # integration record, not by rewriting the contract.
        c = E.EARTH_CONSUMPTION_CONTRACT
        self.assertEqual(c['counts_check'],
                         {'cells': 24, 'eligible': 2, 'blocked': 8,
                          'not_eligible': 14})
        self.assertEqual(c['runtime_wiring'], 'none')
        self.assertEqual(c['event'], 'E0257')

    def test_effective_path_not_wired_for_earth(self):
        # register_effective reads day-root grades off the
        # metal/water tables only; earth stems have no grade there,
        # so no earth day root can become register-effective through
        # this batch (contract preconditions 3 and 5).
        for stem in ('戊', '己'):
            for branch in '子丑寅卯辰巳午未申酉戌亥':
                self.assertIsNone(_mw_root_grade(stem, branch))


class IntegrationRecordTests(unittest.TestCase):
    def test_earth_register_integration_record(self):
        r = E.EARTH_CONSUMPTION_INTEGRATION_E0355
        self.assertEqual(r['event'], 'E0355')
        self.assertEqual(
            r['contract_id'], 'bazi-earth-root-consumption-contract-v1')
        self.assertEqual(set(r['whitelist_cells']),
                         {'戊×巳', '己×午'})
        self.assertEqual(r['wiring_locus'],
                         'bazi_action_conditions.registered_eligible')
        self.assertEqual(r['counts_check'],
                         {'cells': 24, 'eligible': 2, 'blocked': 8,
                          'not_eligible': 14})

    def test_metal_satisfiability_integration_note(self):
        sat = M.METAL_YOU_SATISFIABILITY
        self.assertEqual(sat['status'], 'chart_unrealizable')
        note = sat['integration_e0355']
        self.assertEqual(note['channel_3_status'],
                         'retired_as_independent_channel')
        self.assertEqual(note['conclusion_verdict'],
                         'chart_unrealizable_unchanged')
        # The E0257 review record stays as history.
        self.assertIn('review_e0257', sat)
        self.assertFalse(
            sat['review_e0257']['runtime_verdict_surface_changed'])
        self.assertEqual(len(sat['proof_channels']), 3)

    def test_governance_discloses_the_wiring(self):
        row = next(r for r in REGISTRATION_INVENTORY
                   if r['item'] == 'pure_support_metal')
        self.assertEqual(row['disposition'], 'registered')
        self.assertEqual(row['phase1_rule_id'], 'bazi.rule.r033')
        self.assertIn('E0355', row['reason'])
        self.assertIn('戊×巳', row['reason'])
        self.assertIn('己×午', row['reason'])

    def test_register_stays_pure_data(self):
        import inspect
        members = inspect.getmembers(E)
        bad = [n for n, v in members
               if (inspect.isfunction(v) or inspect.isclass(v))
               and getattr(v, '__module__', None) == E.__name__]
        self.assertEqual(bad, [])


if __name__ == '__main__':
    unittest.main()
