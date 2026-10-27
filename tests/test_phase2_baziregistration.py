"""TJ-011.2 S5: sealed regression for the two strength predicates
registered by the S5 governance batch (bazi.rule.r029 /
bazi.phase2.strength_pure_generating_support and bazi.rule.r030 /
bazi.phase2.strength_commanding_visible_support).

Runs only in the assembled offline acceptance (needs the sealed
canonical snapshot with the S5 registration); NOT public CI, same
partition rule as the other Phase2 bazi suites. Pins:

- both execution rules exist in the bazi Phase2 contract, are
  executable + validated, and reference exactly their own Phase1 rule;
- both Phase1 rules resolve through EvidenceResolver to reviewed
  classical evidence (every source_ref verifies in its section);
- the registered Golden cases fire their own rule (trace step present)
  and keep classification 'strong' -- the registration flips only the
  binding surface, never the verdict;
- witness charts for the two predicates report
  why.sufficient_rule == the registered rule ID, with no
  pending-registration disclosure left;
- the still-pending predicates (lu / metal / water) keep their
  r026-exit disclosure verbatim (registration was NOT extended to
  them: their defining root evidence has no canonical section).
"""
import unittest
from pathlib import Path

from tianji_kb.bazi_adjudication import ADJUDICATION_VARIANT
from tianji_kb.engine import execute
from tianji_kb.golden import run_cases
from tianji_kb.resolver import EvidenceResolver

ROOT = Path(__file__).resolve().parents[1]

NEW_RULES = {
    'bazi.phase2.strength_pure_generating_support': 'bazi.rule.r029',
    'bazi.phase2.strength_commanding_visible_support': 'bazi.rule.r030',
}


class RegistrationContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.resolver = EvidenceResolver()
        cls.contract = cls.resolver.contracts['bazi']

    def test_execution_rules_registered(self):
        rules = {r['id']: r for r in self.contract['rules']}
        for rule_id, phase1_id in NEW_RULES.items():
            self.assertIn(rule_id, rules)
            rule = rules[rule_id]
            self.assertEqual(rule['execution_status'], 'executable')
            self.assertEqual(rule['validation_status'], 'validated')
            self.assertEqual(rule['phase1_rule_refs'], [phase1_id])
            self.assertEqual(rule['regression_test'],
                             'tests/test_phase2_baziregistration.py')
            self.assertTrue(rule['golden_case_ids'])

    def test_phase1_rules_resolve_to_reviewed_evidence(self):
        for phase1_id in NEW_RULES.values():
            refs = self.resolver.resolve(phase1_id, 'ziping-structural-v1')
            self.assertTrue(refs, phase1_id)
            for ref in refs:
                self.assertEqual(ref['rule_id'], phase1_id)
                self.assertNotEqual(ref['evidence_level'], 'D')

    def test_golden_cases_fire_their_registered_rules(self):
        rows = {r['id']: r for r in run_cases(ROOT, 'bazi')}
        hai = rows['bazi.adjudication-strong-hai-generating']
        self.assertIn('bazi.phase2.strength_pure_generating_support',
                      hai['rule_ids'])
        wu = rows['bazi.adjudication-strong-bingwu-commanding']
        self.assertIn('bazi.phase2.strength_commanding_visible_support',
                      wu['rule_ids'])


class WitnessVerdictTests(unittest.TestCase):
    def run_birth(self, birth):
        out = execute('bazi', {'value': birth,
                               'strength_variant': ADJUDICATION_VARIANT},
                      allow_research=True)
        return out['result']['strength_assessment']

    def test_hai_witness_uses_registered_rule(self):
        # Public Golden tj0112-hai-positive-zhongqi-root witness.
        a = self.run_birth('1983-12-02T00:30:00+08:00')
        self.assertEqual(a['classification'], 'strong')
        why = a['why_not_indeterminate']
        self.assertEqual(why['sufficient_rule'],
                         'bazi.phase2.strength_pure_generating_support')
        self.assertNotIn('predicate_rule_registration', why)
        self.assertIn('bazi.phase2.strength_pure_generating_support',
                      a['matched_rule_ids'])

    def test_bingwu_witness_uses_registered_rule(self):
        # Public Golden tj0112-bingwu-positive witness.
        a = self.run_birth('1966-07-06T12:00:00+08:00')
        self.assertEqual(a['classification'], 'strong')
        why = a['why_not_indeterminate']
        self.assertEqual(why['sufficient_rule'],
                         'bazi.phase2.strength_commanding_visible_support')
        self.assertNotIn('predicate_rule_registration', why)
        self.assertIn('bazi.phase2.strength_commanding_visible_support',
                      a['matched_rule_ids'])

    def test_pending_predicates_keep_r026_disclosure(self):
        # S2 witness (Gui x Zi, pure_generating_support_water): the
        # registration was NOT extended to it -- its defining root
        # evidence has no canonical section (S5 governance register).
        a = self.run_birth('1981-12-21T00:30:00+08:00')
        self.assertEqual(a['classification'], 'strong')
        why = a['why_not_indeterminate']
        self.assertIsNone(why['sufficient_rule'])
        self.assertEqual(why['sufficient_predicate'],
                         'pure_generating_support_water')
        self.assertEqual(why['predicate_rule_registration'],
                         'pending_phase1_rule_registration')
        self.assertNotIn('bazi.phase2.strength_pure_generating_support_water',
                         a['matched_rule_ids'])


if __name__ == '__main__':
    unittest.main()
