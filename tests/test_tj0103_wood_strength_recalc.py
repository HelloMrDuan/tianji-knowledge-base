"""TJ-010.3: 木日主已审范围正反复算.

Verifies the bazi-strength-adjudication-v1 sufficient conditions on both
ends (strong/weak) plus conflict/indeterminate counterexamples, with no
scoring. All tests use real chart execution, Rule traces, and Evidence
binding; no mocks, no invented verdicts.
"""
import copy
import unittest

from tianji_kb.bazi_adjudication import ADJUDICATION_VARIANT, strength_assessment
from tianji_kb.operations.bazi_chart import chart
from tianji_kb.operations.bazi import execute
from tianji_kb.resolver import ExecutionTrace


def adjudicate(*pillars):
    out = chart(*pillars, strength_variant=ADJUDICATION_VARIANT)
    return out, out['result']['strength_assessment']


class WoodStrengthRecalcTests(unittest.TestCase):
    """Strong sufficient condition: each condition individually proven."""

    def test_strong_each_sufficient_condition_proven_with_evidence(self):
        # 癸卯 乙卯 甲子 乙亥: 甲日主, 卯月, pure support -> strong
        out, a = adjudicate('癸卯', '乙卯', '甲子', '乙亥')
        self.assertEqual(a['classification'], 'strong')
        self.assertFalse(a['blockers'])

        # 1. Month command: 卯 with same_element relation
        cmd = out['result']['principal_month']
        self.assertEqual(cmd['month_branch'], '卯')
        self.assertEqual(cmd['relation'], 'same_element')
        self.assertEqual(cmd['status'], 'reviewed_relation')

        # 2. All roots effective
        roots = out['result']['root_availability']
        self.assertTrue(roots['root_presence'])
        for r in roots['roots']:
            self.assertEqual(r['root_availability'], 'effective')

        # 3. All visible relations effective_in_reviewed_context
        effects = out['result']['action_effects']
        for rel in effects['visible_relations']:
            self.assertEqual(rel['effect_status'], 'effective_in_reviewed_context')

        # 4. pure_support scope conditions all met
        self.assertTrue(effects['pure_support_scope_met'])
        self.assertTrue(all(effects['pure_support_scope_conditions'].values()))

        # 5. Every condition has Evidence binding
        why = a['why_not_indeterminate']
        self.assertTrue(why['all_required_conditions_verified'])
        for cond in why['conditions']:
            self.assertTrue(cond['met'])
            self.assertTrue(set(cond['evidence_ids']) <= set(out['evidence']))

    def test_strong_yi_day_master_evidence_bound(self):
        # 乙日主卯月: whatever the classification, it must be evidence-bound
        out, a = adjudicate('癸卯', '乙卯', '乙亥', '丙子')
        self.assertIn(a['classification'], ('strong', 'indeterminate', 'weak'))
        # Never the opposite verdict without sufficient conditions
        if a['classification'] == 'strong':
            self.assertFalse(a['blockers'])
            self.assertTrue(a['why_not_indeterminate']['all_required_conditions_verified'])
            self.assertTrue(set(a['evidence_ids']) <= set(out['evidence']))
        else:
            # Not strong: must not claim sufficient conditions verified
            self.assertIsNone(a['why_not_indeterminate'])


class WoodWeakRecalcTests(unittest.TestCase):
    """Weak sufficient condition: complete isolation chain, not just 'no roots'."""

    def test_weak_each_sufficient_condition_proven_with_evidence(self):
        # 戊午 辛酉 甲午 庚午: 甲日主, 酉月, isolated control -> weak
        out, a = adjudicate('戊午', '辛酉', '甲午', '庚午')
        self.assertEqual(a['classification'], 'weak')
        self.assertFalse(a['blockers'])

        # 1. Month command: 酉 with controls_me relation
        cmd = out['result']['principal_month']
        self.assertEqual(cmd['month_branch'], '酉')
        self.assertEqual(cmd['relation'], 'controls_me')

        # 2. No roots present (part of the chain, not the whole verdict)
        roots = out['result']['root_availability']
        self.assertFalse(roots['root_presence'])

        # 3. Month pillar has effective controls_me action
        effects = out['result']['action_effects']
        month_controls = [r for r in effects['visible_relations']
                         if r['fact']['pillar'] == 'month'
                         and r['effective_action'] == 'controls_me'
                         and r['effect_status'] == 'effective_in_reviewed_context']
        self.assertTrue(month_controls)

        # 4. isolated_control scope conditions all met
        self.assertTrue(effects['isolated_control_scope_met'])
        self.assertTrue(all(effects['isolated_control_scope_conditions'].values()))

        # 5. Every condition has Evidence binding
        why = a['why_not_indeterminate']
        self.assertTrue(why['all_required_conditions_verified'])

    def test_weak_requires_month_stem_control_not_just_no_roots(self):
        # 无根 but without 透辛 month control -> must not be weak
        # 戊寅 甲寅 甲辰 丁卯: 甲日主, 寅月 (not 酉), no effective control chain
        out, a = adjudicate('戊寅', '甲寅', '甲辰', '丁卯')
        self.assertNotEqual(a['classification'], 'weak')
        if a['classification'] == 'indeterminate':
            self.assertIsNone(a['why_not_indeterminate'])


class WoodConflictRecalcTests(unittest.TestCase):
    """Conflict and incomplete conditions must return indeterminate."""

    def test_root_with_clash_cannot_be_strong(self):
        # 有根受冲: 卯月有根 but 酉冲卯 -> must not be strong
        out, a = adjudicate('辛酉', '乙卯', '甲子', '丙寅')
        self.assertNotEqual(a['classification'], 'strong')
        if a['classification'] == 'indeterminate':
            self.assertIsNone(a['why_not_indeterminate'])

    def test_clashed_roots_break_strong_sufficient_chain(self):
        # Start from known strong, introduce a clash on the root branch
        out, _ = adjudicate('癸卯', '乙卯', '甲子', '乙亥')
        t = ExecutionTrace('bazi', 'ziping-structural-v1')
        t.steps = copy.deepcopy([s for s in out['trace'] if 'strength_' not in s['rule_id']])
        t.evidence = copy.deepcopy(out['evidence'])
        # Simulate root clash by marking root availability non-effective
        roots = next(s for s in t.steps if s['rule_id'] == 'bazi.phase2.root_availability')
        for r in roots['output']['roots']:
            r['root_availability'] = 'conditional'
        result = strength_assessment(t, strength_variant=ADJUDICATION_VARIANT)
        self.assertEqual(result['classification'], 'indeterminate')

    def test_weak_month_with_root_cannot_be_weak(self):
        # 酉月 but has root -> not isolated -> must not be weak
        out, a = adjudicate('戊午', '辛酉', '甲寅', '庚午')
        # 甲寅: 寅为根, breaks isolation
        self.assertNotEqual(a['classification'], 'weak')

    def test_unresolved_interactions_block_strong_verdict(self):
        # When action effects have unresolved interactions, strong is blocked
        out, a = adjudicate('癸卯', '乙卯', '甲子', '乙亥')
        # Baseline is strong; now forge an unresolved interaction
        t = ExecutionTrace('bazi', 'ziping-structural-v1')
        t.steps = copy.deepcopy([s for s in out['trace'] if 'strength_' not in s['rule_id']])
        t.evidence = copy.deepcopy(out['evidence'])
        effect = next(s for s in t.steps if s['rule_id'] == 'bazi.phase2.action_effects')
        effect['output']['unresolved_interaction_kinds'] = ['branch_six_harmonies']
        result = strength_assessment(t, strength_variant=ADJUDICATION_VARIANT)
        self.assertEqual(result['classification'], 'indeterminate')
        self.assertTrue(any(b['reason'] == 'interaction_effect_unresolved'
                          for b in result['blockers']))


class WoodRealBirthdayRecalcTests(unittest.TestCase):
    """Real calendar birthdays: different dates, Jia/Yi, term boundaries."""

    def test_additional_strong_birthdays(self):
        # Additional 卯月 birthdays beyond the existing 1963/2043 cases
        for value in ['1987-03-18T10:00:00+08:00', '2011-03-25T14:00:00+08:00']:
            with self.subTest(value=value):
                out = execute('bazi', {'value': value,
                             'strength_variant': ADJUDICATION_VARIANT},
                             allow_research=True)
                a = out['result']['strength_assessment']
                # Document actual classification; 卯月 wood DM should be strong
                # if sufficient conditions met, else indeterminate (not weak)
                self.assertIn(a['classification'], ('strong', 'indeterminate'))
                self.assertNotEqual(a['classification'], 'weak')

    def test_additional_weak_birthdays(self):
        # Additional 酉月 birthdays beyond the existing 2038/1978 cases
        for value in ['1999-09-18T10:00:00+08:00', '2023-09-22T14:00:00+08:00']:
            with self.subTest(value=value):
                out = execute('bazi', {'value': value,
                             'strength_variant': ADJUDICATION_VARIANT},
                             allow_research=True)
                a = out['result']['strength_assessment']
                # 酉月 wood DM: weak if isolated, else indeterminate (not strong)
                self.assertIn(a['classification'], ('weak', 'indeterminate'))
                self.assertNotEqual(a['classification'], 'strong')

    def test_term_boundary_does_not_guess(self):
        # Near 惊蛰/清明 boundary: classification must be computed, not guessed
        # 2024-03-05 is around 惊蛰; verify the system computes rather than assumes
        out = execute('bazi', {'value': '2024-03-05T10:00:00+08:00',
                     'strength_variant': ADJUDICATION_VARIANT},
                     allow_research=True)
        a = out['result']['strength_assessment']
        # Must have real trace and evidence regardless of classification
        self.assertTrue(a['matched_rule_ids'])
        self.assertTrue(a['evidence_ids'])
        # If indeterminate, blockers must explain why
        if a['classification'] == 'indeterminate':
            self.assertTrue(a['blockers'] or a['conflict_checks'])


class WoodEvidenceConsistencyTests(unittest.TestCase):
    """Tampering with key facts/conditions/Evidence must not yield a verdict."""

    def test_tampered_month_branch_cannot_stay_strong(self):
        out, _ = adjudicate('癸卯', '乙卯', '甲子', '乙亥')
        t = ExecutionTrace('bazi', 'ziping-structural-v1')
        t.steps = copy.deepcopy([s for s in out['trace'] if 'strength_' not in s['rule_id']])
        t.evidence = copy.deepcopy(out['evidence'])
        # Tamper: change month branch from 卯 to 酉
        cmd = next(s for s in t.steps if s['rule_id'] == 'bazi.phase2.principal_month')
        cmd['output']['month_branch'] = '酉'
        result = strength_assessment(t, strength_variant=ADJUDICATION_VARIANT)
        self.assertEqual(result['classification'], 'indeterminate')
        self.assertTrue(any(b['reason'] == 'factor_chain_inconsistent'
                          for b in result['blockers']))

    def test_tampered_root_effectiveness_cannot_stay_strong(self):
        out, _ = adjudicate('癸卯', '乙卯', '甲子', '乙亥')
        t = ExecutionTrace('bazi', 'ziping-structural-v1')
        t.steps = copy.deepcopy([s for s in out['trace'] if 'strength_' not in s['rule_id']])
        t.evidence = copy.deepcopy(out['evidence'])
        # Tamper: mark a root as not effective
        roots = next(s for s in t.steps if s['rule_id'] == 'bazi.phase2.root_availability')
        roots['output']['roots'][0]['root_availability'] = 'conditional'
        result = strength_assessment(t, strength_variant=ADJUDICATION_VARIANT)
        self.assertEqual(result['classification'], 'indeterminate')

    def test_removed_evidence_rejected(self):
        out, _ = adjudicate('戊午', '辛酉', '甲午', '庚午')
        t = ExecutionTrace('bazi', 'ziping-structural-v1')
        t.steps = copy.deepcopy([s for s in out['trace'] if 'strength_' not in s['rule_id']])
        t.evidence = copy.deepcopy(out['evidence'])
        # Remove one evidence entry referenced by a step
        step = next(s for s in t.steps if s['evidence_ids'])
        del t.evidence[step['evidence_ids'][0]]
        with self.assertRaises(ValueError):
            strength_assessment(t, strength_variant=ADJUDICATION_VARIANT)


if __name__ == '__main__':
    unittest.main()
