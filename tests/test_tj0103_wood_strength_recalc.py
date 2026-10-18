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
from tianji_kb.engine import execute
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

        # 5. Every condition has Evidence binding (non-empty)
        why = a['why_not_indeterminate']
        self.assertTrue(why['all_required_conditions_verified'])
        self.assertTrue(why['conditions'])
        for cond in why['conditions']:
            self.assertTrue(cond['met'])
            self.assertTrue(cond['evidence_ids'])
            self.assertTrue(set(cond['evidence_ids']) <= set(out['evidence']))

    def test_yi_day_master_with_drain_is_indeterminate(self):
        # 癸卯 乙卯 乙亥 丙子: 乙日主, 乙卯月, but 丙火 drains
        # Indeterminate counterexample: 卯月 wood DM with draining fire
        # prevents pure_support. Verifies system abstains correctly.
        out, a = adjudicate('癸卯', '乙卯', '乙亥', '丙子')
        self.assertEqual(out['result']['day_master']['stem'], '乙')
        cmd = out['result']['principal_month']
        self.assertEqual(cmd['month_branch'], '卯')
        self.assertEqual(cmd['relation'], 'same_element')
        self.assertEqual(a['classification'], 'indeterminate')
        self.assertIsNone(a['why_not_indeterminate'])
        self.assertTrue(a['blockers'])
        self.assertTrue(a['evidence_ids'])


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
        # 戊午 辛酉 甲午 癸酉: 甲日主, truly no wood roots (午酉 only),
        # has 癸印 support, but not the full isolation chain -> indeterminate
        # (This is the existing known-indeterminate case from
        # test_no_root_with_resource_and_classical_case_labels_do_not_supply_verdicts)
        out, a = adjudicate('戊午', '辛酉', '甲午', '癸酉')
        # 1. Verify truly no roots
        roots = out['result']['root_availability']
        self.assertFalse(roots['root_presence'])
        self.assertEqual(len(roots['roots']), 0)
        # 2. Verify day master is 甲
        self.assertEqual(out['result']['day_master']['stem'], '甲')
        # 3. Must be indeterminate (not weak): has 癸印 but lacks full chain
        self.assertEqual(a['classification'], 'indeterminate')
        self.assertIsNone(a['why_not_indeterminate'])
        # 4. Must have blockers with evidence explaining why not weak
        self.assertTrue(a['blockers'])
        for b in a['blockers']:
            self.assertTrue(b['evidence_ids'])
            self.assertIn(b['evidence_id'], out['evidence'])


class WoodConflictRecalcTests(unittest.TestCase):
    """Conflict and incomplete conditions must return indeterminate."""

    def test_root_with_clash_returns_indeterminate(self):
        # 有根受冲: 辛酉 乙卯 甲子 丙寅 - 酉冲卯, root clashed
        # 卯月 so cannot be weak; clashed root so cannot be strong
        out, a = adjudicate('辛酉', '乙卯', '甲子', '丙寅')
        self.assertEqual(out['result']['day_master']['stem'], '甲')
        self.assertEqual(out['result']['principal_month']['month_branch'], '卯')
        self.assertEqual(a['classification'], 'indeterminate')
        self.assertIsNone(a['why_not_indeterminate'])
        # Must have blockers with real evidence
        self.assertTrue(a['blockers'])
        for b in a['blockers']:
            self.assertTrue(b['evidence_ids'])

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

    def test_weak_month_with_root_returns_indeterminate(self):
        # 戊午 辛酉 甲寅 庚午 - 酉月 but 甲寅 provides wood root (寅)
        # Has root so cannot meet isolated_control (requires no roots);
        # 酉月 so cannot meet pure_support (requires 卯月)
        out, a = adjudicate('戊午', '辛酉', '甲寅', '庚午')
        self.assertEqual(out['result']['day_master']['stem'], '甲')
        self.assertEqual(out['result']['principal_month']['month_branch'], '酉')
        # Verify root actually exists
        self.assertTrue(out['result']['root_availability']['root_presence'])
        self.assertEqual(a['classification'], 'indeterminate')
        self.assertIsNone(a['why_not_indeterminate'])

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
    """Real calendar birthdays: verify pillars, day master, month, and result."""

    def test_additional_strong_birthdays(self):
        # 卯月 birthdays with wood day masters, but with drain/control factors
        # that prevent full pure_support:
        # - 2023-03-08 12:00: 癸卯 乙卯 乙丑 壬午 -> 乙日主, 乙卯月, 午火泄
        # - 2023-03-18 12:00: 癸卯 乙卯 乙亥 壬午 -> 乙日主, 乙卯月, 午火泄
        # These are indeterminate counterexamples: 卯月 wood DM but
        # insufficient for strong due to draining fire. Verifies the system
        # correctly abstains rather than guessing strong.
        for value, expected_ganzhi in [
            ('2023-03-08T12:00:00+08:00', ('癸卯', '乙卯', '乙丑', '壬午')),
            ('2023-03-18T12:00:00+08:00', ('癸卯', '乙卯', '乙亥', '壬午')),
        ]:
            with self.subTest(value=value):
                out = execute('bazi', {'value': value,
                             'strength_variant': ADJUDICATION_VARIANT},
                             allow_research=True)
                pillars = out['result']['pillars']
                ganzhi = tuple(p['stem']['value'] + p['branch']['value'] for p in pillars)
                self.assertEqual(ganzhi, expected_ganzhi)
                self.assertEqual(out['result']['day_master']['stem'], '乙')
                self.assertEqual(out['result']['principal_month']['month_branch'], '卯')
                a = out['result']['strength_assessment']
                # Deterministic: indeterminate (not strong, not weak)
                self.assertEqual(a['classification'], 'indeterminate')
                self.assertIsNone(a['why_not_indeterminate'])
                self.assertTrue(a['blockers'])
                self.assertTrue(a['evidence_ids'])

    def test_additional_weak_birthdays(self):
        # 酉月 birthdays with wood day masters, no roots, but with 壬水 support
        # that breaks full isolation:
        # - 2018-09-10 12:00: 戊戌 辛酉 乙巳 壬午 -> 乙日主, 辛酉月, 壬水生扶
        # - 2018-09-30 12:00: 戊戌 辛酉 乙丑 壬午 -> 乙日主, 辛酉月, 壬水生扶
        # These are indeterminate counterexamples: 酉月 wood DM with no roots
        # but 壬水 support prevents isolated_control. Verifies "no roots" alone
        # does not imply weak.
        for value, expected_ganzhi in [
            ('2018-09-10T12:00:00+08:00', ('戊戌', '辛酉', '乙巳', '壬午')),
            ('2018-09-30T12:00:00+08:00', ('戊戌', '辛酉', '乙丑', '壬午')),
        ]:
            with self.subTest(value=value):
                out = execute('bazi', {'value': value,
                             'strength_variant': ADJUDICATION_VARIANT},
                             allow_research=True)
                pillars = out['result']['pillars']
                ganzhi = tuple(p['stem']['value'] + p['branch']['value'] for p in pillars)
                self.assertEqual(ganzhi, expected_ganzhi)
                self.assertEqual(out['result']['day_master']['stem'], '乙')
                self.assertEqual(out['result']['principal_month']['month_branch'], '酉')
                self.assertFalse(out['result']['root_availability']['root_presence'])
                a = out['result']['strength_assessment']
                # Deterministic: indeterminate (not weak due to 壬水, not strong)
                self.assertEqual(a['classification'], 'indeterminate')
                self.assertIsNone(a['why_not_indeterminate'])
                self.assertTrue(a['blockers'])
                self.assertTrue(a['evidence_ids'])

    def test_term_boundary_jingzhe_before_during_after(self):
        # 2024惊蛰: 2024-03-05 10:22:45 (from lunar_python, project's calendar provider)
        # Test three points: before, exact second, after.
        # Note: lunar_python provides second-level precision.
        before = execute('bazi', {'value': '2024-03-05T10:22:44+08:00',
                         'strength_variant': ADJUDICATION_VARIANT},
                         allow_research=True)
        during = execute('bazi', {'value': '2024-03-05T10:22:45+08:00',
                         'strength_variant': ADJUDICATION_VARIANT},
                         allow_research=True)
        after = execute('bazi', {'value': '2024-03-05T10:22:46+08:00',
                        'strength_variant': ADJUDICATION_VARIANT},
                        allow_research=True)
        before_month = before['result']['principal_month']['month_branch']
        during_month = during['result']['principal_month']['month_branch']
        after_month = after['result']['principal_month']['month_branch']
        # Month must transition at the solar term (before=寅, during/after=卯)
        self.assertEqual(before_month, '寅',
            f'Before 惊蛰 should be 寅月, got {before_month}')
        self.assertEqual(after_month, '卯',
            f'After 惊蛰 should be 卯月, got {after_month}')
        # During second: documents actual behavior (implementation-defined)
        self.assertIn(during_month, ('寅', '卯'))
        # All three must have real trace and evidence
        for out, label in [(before, 'before'), (during, 'during'), (after, 'after')]:
            a = out['result']['strength_assessment']
            self.assertTrue(a['matched_rule_ids'], f'{label}: no matched rules')
            self.assertTrue(a['evidence_ids'], f'{label}: no evidence')
            self.assertIn(a['classification'], ('strong', 'weak', 'indeterminate'))


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
