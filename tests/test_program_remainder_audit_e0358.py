"""能力补全 program 剩余任务再审计（E0358）：公开治理测试。

只读审计批的结论钉：TASK_STATUS 全部 28 行未完成任务逐行以 WBS
原文与现行实测复核后重新定级（头条分布 A 3 行、B 9 行、C 9 行、
D 7 行）；重点复核面包偶星结构面可先行（A）、013.3 前置部分变化、
012.3 无新窄切片、场景接线唯一门为分阶段开放裁定、025.2 文案微项。
本测试只读公开文件（审计文档与台账两件）；机上与代码实测锚点见
审计文档 §1/§4–§8。本批未实现任何 A 类项、未代决任何 B 类项。
"""

from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs" / "product" / "PROGRAM_REMAINDER_AUDIT_E0358.md"
HISTORY = ROOT / "docs" / "product" / "TASK_HISTORY.md"
STATUS = ROOT / "docs" / "product" / "TASK_STATUS.md"


class ProgramRemainderAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc = DOC.read_text(encoding="utf-8")
        cls.history = HISTORY.read_text(encoding="utf-8")
        cls.status = STATUS.read_text(encoding="utf-8")

    def test_audit_doc_on_file_with_all_sections(self):
        for heading in (
            "## 0 授权与范围",
            "## 1 开工核实与基线",
            "## 2 审计方法与定级口径",
            "## 3 全量定级表（28 行）",
            "## 4 重点复核（a）：TJ-022.2 配偶星结构面可否先行",
            "## 5 重点复核（b）：TJ-013.3 第二阶段前置变化",
            "## 6 重点复核（c）：TJ-012.3 注册后窄切片复审",
            "## 7 重点复核（d）：新注册能力的场景接线机会（11 场景逐个）",
            "## 8 重点复核（e）：TJ-025.2 后续面（人生总览 7 维）",
            "## 9 重点复核（f）：其余余项与在册结论冲突清单",
            "## 10 A 类批次切分与顺位建议",
            "## 11 B 类裁定点清单（只列示不代决）",
            "## 12 本批产出与边界",
        ):
            self.assertIn(heading, self.doc)

    def test_full_inventory_and_grading_distribution_pinned(self):
        self.assertIn("未完成共 28 行", self.doc)
        self.assertIn("A 3 行、B 9 行、C 9 行、D 7 行", self.doc)
        # Every non-completed task row is graded in the table.
        for task_id in (
            "TJ-001.6", "TJ-003.1", "TJ-003.2", "TJ-003.3", "TJ-005.1",
            "TJ-005.3", "TJ-008.1", "TJ-008.5", "TJ-009.1", "TJ-009.2",
            "TJ-011.2", "TJ-012.3", "TJ-013.1", "TJ-013.2", "TJ-013.3",
            "TJ-017.2", "TJ-017.3", "TJ-018.1", "TJ-018.2", "TJ-018.3",
            "TJ-019.2", "TJ-022.2", "TJ-023.3", "TJ-028.1", "TJ-028.2",
            "TJ-028.3", "TJ-029.1", "TJ-029.2",
        ):
            self.assertIn(f"| {task_id} |", self.doc)

    def test_measured_facts_pinned(self):
        # Registration inventory measured live from the governance module.
        self.assertIn("18 行 = registered 12 / maintained_pending 3", self.doc)
        # (c) general strength still absent; determination still None-bound.
        self.assertIn("overall_strength: None", self.doc)
        self.assertIn("无新的 A 类窄切片", self.doc)
        # (d) scenario layer references none of the research gates.
        self.assertIn("引用为 **0**", self.doc)
        # (a) spouse-star structural face separable from the strength face.
        self.assertIn("不消费任何旺衰/喜忌量", self.doc)
        # (e) dayun exit wording partially stale after registration.
        self.assertIn("部分陈旧", self.doc)

    def test_a_sequence_and_b_points_pinned(self):
        for marker in (
            "E0359 审定批", "E0360 实现批", "E0362 实现批", "E0364 实现批",
            "不建议排入能力队列",
        ):
            self.assertIn(marker, self.doc)
        for point in (
            "B002 可信备份授权", "扶抑 U1/U3", "司令扩月 / 24 小时计日约定转正",
            "S3 勘误定向重应用", "新梦来源引入", "化气表述采用 P-D1",
            "从化象分类 P-D2", "长生冲突裁定", "分阶段开放裁定",
            "真模型访问提供",
        ):
            self.assertIn(point, self.doc)
        # Read-only boundary: nothing implemented, nothing adjudicated.
        self.assertIn("未实现 A 类任何一项，未代决 B 类任何一项", self.doc)

    def test_ledger_event_and_status_row(self):
        rows = [line for line in self.history.splitlines()
                if line.startswith("| E0358 |")]
        self.assertEqual(len(rows), 1)
        cells = [c.strip() for c in rows[0].strip().strip("|").split("|")]
        self.assertEqual(len(cells), 8)
        self.assertEqual(cells[2], "TJ-018.2")
        self.assertEqual(cells[3], "阻塞")
        status_rows = [line for line in self.status.splitlines()
                       if line.startswith("| TJ-018.2 |")]
        self.assertEqual(len(status_rows), 1)
        self.assertIn("阻塞", status_rows[0])
        self.assertIn("E0358", status_rows[0])
        self.assertIn("PROGRAM_REMAINDER_AUDIT_E0358.md", status_rows[0])


if __name__ == "__main__":
    unittest.main()
