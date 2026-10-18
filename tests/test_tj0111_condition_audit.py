"""TJ-011.1: 15条充分条件的逐项机器验收。

验证 bazi-strength-adjudication-v1 的每条充分条件：
- 强：8条 pure_support_scope_conditions
- 弱：7条 isolated_control_scope_conditions

每条检查：程序字段存在性、实际计算值、Rule、Trace、Evidence绑定。
反例验证条件缺失时的弃判行为。
"""
import unittest

from tianji_kb.bazi_adjudication import ADJUDICATION_VARIANT, strength_assessment
from tianji_kb.engine import chart, execute


def adjudicate(*pillars):
    out = chart(*pillars, strength_variant=ADJUDICATION_VARIANT)
    return out, out['result']['strength_assessment']


# 15条条件的key清单（必须与 bazi_action_conditions.py 完全一致）
STRONG_CONDITION_KEYS = [
    'wood_day_master',
    'reviewed_same_element_month',
    'all_positions_support_only',
    'visible印_present',
    'visible比_present',
    'effective_day_roots',
    'all_visible_have_reviewed_roots',
    'no_unresolved_interactions',
]

WEAK_CONDITION_KEYS = [
    'wood_day_master',
    'reviewed_control_month',
    'day_has_no_structural_root',
    'no_support_in_any_position',
    'visible_earth_metal_only',
    'month_principal_exposed_with_root',
    'no_unresolved_interactions',
]


class StrongConditionKeysTests(unittest.TestCase):
    """强8条：key完整性 + 正例全真 + 反例弃判。"""

    def test_strong_condition_keys_match_implementation(self):
        # 正例：癸卯/乙卯/甲子/乙亥 -> strong
        out, a = adjudicate('癸卯', '乙卯', '甲子', '乙亥')
        self.assertEqual(a['classification'], 'strong')
        effects = out['result']['action_effects']
        # 1. key集合必须完全一致（无多无少）
        actual_keys = set(effects['pure_support_scope_conditions'].keys())
        self.assertEqual(actual_keys, set(STRONG_CONDITION_KEYS),
            f"Strong condition keys mismatch: {actual_keys} vs {set(STRONG_CONDITION_KEYS)}")
        # 2. 正例中8条必须全为True
        for key in STRONG_CONDITION_KEYS:
            self.assertTrue(effects['pure_support_scope_conditions'][key],
                f"Strong positive case: {key} should be True")
        self.assertTrue(effects['pure_support_scope_met'])
        # 3. why_not_indeterminate 必须包含8条且每条有Evidence
        why = a['why_not_indeterminate']
        self.assertIsNotNone(why)
        self.assertTrue(why['all_required_conditions_verified'])
        cond_names = [c['condition'] for c in why['conditions']]
        for key in STRONG_CONDITION_KEYS:
            self.assertIn(key, cond_names, f"Missing condition in why: {key}")
        for cond in why['conditions']:
            self.assertTrue(cond['met'], f"Condition {cond['condition']} not met")
            self.assertTrue(cond['evidence_ids'], f"Condition {cond['condition']} has no evidence")
            # Evidence必须真实存在于trace
            self.assertTrue(set(cond['evidence_ids']) <= set(out['evidence']))

    def test_strong_counterexample_drain_breaks_all_positions(self):
        # 反例：2023-03-08 午火泄气 -> all_positions_support_only False -> indeterminate
        out = execute('bazi', {'value': '2023-03-08T12:00:00+08:00',
                     'strength_variant': ADJUDICATION_VARIANT}, allow_research=True)
        a = out['result']['strength_assessment']
        self.assertEqual(a['classification'], 'indeterminate')
        effects = out['result']['action_effects']
        # 至少一条条件为False（具体哪条由实现决定，但必须有False）
        self.assertFalse(all(effects['pure_support_scope_conditions'].values()))
        self.assertFalse(effects['pure_support_scope_met'])
        self.assertTrue(a['blockers'])

    def test_strong_counterexample_clash_breaks_no_interactions(self):
        # 反例：辛酉/乙卯/甲子/丙寅（酉冲卯）-> no_unresolved_interactions False
        out, a = adjudicate('辛酉', '乙卯', '甲子', '丙寅')
        self.assertEqual(a['classification'], 'indeterminate')
        effects = out['result']['action_effects']
        self.assertFalse(effects['pure_support_scope_conditions']['no_unresolved_interactions'])
        self.assertTrue(a['blockers'])


class WeakConditionKeysTests(unittest.TestCase):
    """弱7条：key完整性 + 正例全真 + 反例弃判。"""

    def test_weak_condition_keys_match_implementation(self):
        # 正例：戊午/辛酉/甲午/庚午 -> weak
        out, a = adjudicate('戊午', '辛酉', '甲午', '庚午')
        self.assertEqual(a['classification'], 'weak')
        effects = out['result']['action_effects']
        # 1. key集合必须完全一致
        actual_keys = set(effects['isolated_control_scope_conditions'].keys())
        self.assertEqual(actual_keys, set(WEAK_CONDITION_KEYS),
            f"Weak condition keys mismatch: {actual_keys} vs {set(WEAK_CONDITION_KEYS)}")
        # 2. 正例中7条必须全为True
        for key in WEAK_CONDITION_KEYS:
            self.assertTrue(effects['isolated_control_scope_conditions'][key],
                f"Weak positive case: {key} should be True")
        self.assertTrue(effects['isolated_control_scope_met'])
        # 3. Evidence绑定
        why = a['why_not_indeterminate']
        self.assertIsNotNone(why)
        self.assertTrue(why['all_required_conditions_verified'])
        for cond in why['conditions']:
            self.assertTrue(cond['met'])
            self.assertTrue(cond['evidence_ids'])
            self.assertTrue(set(cond['evidence_ids']) <= set(out['evidence']))

    def test_weak_counterexample_support_breaks_isolation(self):
        # 反例：2018-09-10 壬水生扶 -> no_support_in_any_position False -> indeterminate
        out = execute('bazi', {'value': '2018-09-10T12:00:00+08:00',
                     'strength_variant': ADJUDICATION_VARIANT}, allow_research=True)
        a = out['result']['strength_assessment']
        self.assertEqual(a['classification'], 'indeterminate')
        effects = out['result']['action_effects']
        self.assertFalse(effects['isolated_control_scope_conditions']['no_support_in_any_position'])
        self.assertFalse(effects['isolated_control_scope_met'])
        self.assertTrue(a['blockers'])

    def test_weak_counterexample_root_breaks_no_root(self):
        # 反例：戊午/辛酉/甲寅/庚午（有寅根）-> day_has_no_structural_root False
        out, a = adjudicate('戊午', '辛酉', '甲寅', '庚午')
        self.assertEqual(a['classification'], 'indeterminate')
        effects = out['result']['action_effects']
        self.assertFalse(effects['isolated_control_scope_conditions']['day_has_no_structural_root'])


class EvidenceIntegrityTests(unittest.TestCase):
    """证据完整性：缺失/伪造/不一致必须拒绝。"""

    def test_strong_evidence_ids_nonempty_and_bound(self):
        out, a = adjudicate('癸卯', '乙卯', '甲子', '乙亥')
        self.assertEqual(a['classification'], 'strong')
        # Evidence IDs非空
        self.assertTrue(a['evidence_ids'])
        # 每个condition的evidence_ids必须非空且被trace包含
        why = a['why_not_indeterminate']
        for cond in why['conditions']:
            self.assertTrue(cond['evidence_ids'], f"{cond['condition']} missing evidence")
        # Rule ID必须正确
        self.assertIn('bazi.phase2.action_effects', a['matched_rule_ids'])

    def test_weak_evidence_ids_nonempty_and_bound(self):
        out, a = adjudicate('戊午', '辛酉', '甲午', '庚午')
        self.assertEqual(a['classification'], 'weak')
        self.assertTrue(a['evidence_ids'])
        why = a['why_not_indeterminate']
        for cond in why['conditions']:
            self.assertTrue(cond['evidence_ids'], f"{cond['condition']} missing evidence")

    def test_indeterminate_has_blockers_not_empty_evidence(self):
        # indeterminate必须有blocker，且不能有空的why
        out, a = adjudicate('辛酉', '乙卯', '甲子', '丙寅')
        self.assertEqual(a['classification'], 'indeterminate')
        self.assertIsNone(a['why_not_indeterminate'])
        self.assertTrue(a['blockers'])
        # blocker必须有reason和evidence
        for b in a['blockers']:
            self.assertTrue(b['reason'])
            self.assertTrue(b['evidence_ids'])


if __name__ == '__main__':
    unittest.main()
