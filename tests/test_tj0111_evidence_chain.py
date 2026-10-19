"""TJ-011.1: 15条条件证据链状态核验（诚实报告模式）。

不虚构证据关联，只报告实际可验证的内容。
S5/W5 明确为未验证实现选择。
"""
import unittest

from tianji_kb.bazi_adjudication import ADJUDICATION_VARIANT
from tianji_kb.operations.bazi_chart import chart


def adjudicate(*pillars):
    out = chart(*pillars, strength_variant=ADJUDICATION_VARIANT)
    return out, out['result']['strength_assessment']


class EvidenceStatusReportTests(unittest.TestCase):
    """报告15条条件的证据状态，不虚构。"""

    def test_strong_conditions_have_evidence_ids(self):
        """强8条：正例中每条必须有非空 Evidence IDs（实际验证）。"""
        out, a = adjudicate('癸卯', '乙卯', '甲子', '乙亥')
        self.assertEqual(a['classification'], 'strong')
        why = a['why_not_indeterminate']
        self.assertIsNotNone(why)
        # 8条条件必须都在 why.conditions 中
        self.assertEqual(len(why['conditions']), 8)
        for cond in why['conditions']:
            # 每条必须有非空 evidence_ids
            self.assertTrue(cond['evidence_ids'],
                f"Condition {cond['condition']}: empty evidence_ids")
            # 每个 evidence ID 必须在 trace evidence 字典中存在
            for eid in cond['evidence_ids']:
                self.assertIn(eid, out['evidence'],
                    f"Condition {cond['condition']}: evidence {eid} not in trace")

    def test_weak_conditions_have_evidence_ids(self):
        """弱7条：正例中每条必须有非空 Evidence IDs（实际验证）。"""
        out, a = adjudicate('戊午', '辛酉', '甲午', '庚午')
        self.assertEqual(a['classification'], 'weak')
        why = a['why_not_indeterminate']
        self.assertIsNotNone(why)
        self.assertEqual(len(why['conditions']), 7)
        for cond in why['conditions']:
            self.assertTrue(cond['evidence_ids'],
                f"Condition {cond['condition']}: empty evidence_ids")
            for eid in cond['evidence_ids']:
                self.assertIn(eid, out['evidence'],
                    f"Condition {cond['condition']}: evidence {eid} not in trace")

    def test_fact_ref_format_valid(self):
        """fact_ref 格式必须有效（#/trace/ 前缀）。"""
        out, a = adjudicate('癸卯', '乙卯', '甲子', '乙亥')
        why = a['why_not_indeterminate']
        for cond in why['conditions']:
            self.assertTrue(cond['fact_ref'],
                f"Condition {cond['condition']}: empty fact_ref")
            self.assertTrue(cond['fact_ref'].startswith('#/trace/'),
                f"Condition {cond['condition']}: invalid fact_ref")

    def test_s5_w5_no_classical_claim(self):
        """S5/W5 不得声称有古籍直接支持（仅验证值为布尔型）。"""
        out, a = adjudicate('癸卯', '乙卯', '甲子', '乙亥')
        effects = out['result']['action_effects']
        # S5 存在且为布尔值（不验证古籍依据）
        self.assertIn('visible比_present', effects['pure_support_scope_conditions'])
        self.assertIsInstance(
            effects['pure_support_scope_conditions']['visible比_present'], bool)
        
        out2, a2 = adjudicate('戊午', '辛酉', '甲午', '庚午')
        effects2 = out2['result']['action_effects']
        self.assertIn('visible_earth_metal_only', effects2['isolated_control_scope_conditions'])
        self.assertIsInstance(
            effects2['isolated_control_scope_conditions']['visible_earth_metal_only'], bool)


if __name__ == '__main__':
    unittest.main()
