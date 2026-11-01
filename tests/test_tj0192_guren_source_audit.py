"""TJ-019.2「故人」主题来源审计（E0357）：公开治理测试。

只读审计批的结论钉：已登记全部来源语料（周公 RAW 全文／Source 全集
102＋37／密封快照文本清单）三面查证后，「故人」主题无合格原典来源
（结论 B，全文级关闭），缺口保持登记、不得以既有条目填充，解除路径
只有新来源准入（用户级资源决策）。本测试只读公开文件：审计文档
（docs/product/TJ0192_GUREN_SOURCE_AUDIT.md）、台账两件与公开运行面
dream_knowledge.py 的未审输入主题形态；不读密封数据（RAW 复拉三钉、
候选记录与快照清单的机上直读实证见审计文档 §1/§4/§6）。
"""

from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs" / "product" / "TJ0192_GUREN_SOURCE_AUDIT.md"
HISTORY = ROOT / "docs" / "product" / "TASK_HISTORY.md"
STATUS = ROOT / "docs" / "product" / "TASK_STATUS.md"
DREAM_OPS = ROOT / "src" / "tianji_kb" / "operations" / "dream_knowledge.py"


class GurenSourceAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc = DOC.read_text(encoding="utf-8")
        cls.history = HISTORY.read_text(encoding="utf-8")
        cls.status = STATUS.read_text(encoding="utf-8")
        cls.ops = DREAM_OPS.read_text(encoding="utf-8")

    def test_audit_doc_on_file_with_all_sections(self):
        for heading in (
            "## 0 授权与范围",
            "## 1 开工核实与基线",
            "## 2 合格判据（沿 TJ-019.2 既有准入线）",
            "## 3 审计范围清单（三面穷举）",
            "## 4 面（a）：周公 RAW 全文复核",
            "## 5 面（b）：已登记 Source 全集核查",
            "## 6 面（c）：密封快照文本清单核查",
            "## 7 结论（B）与终局处置建议",
            "## 8 本批产出与边界",
        ):
            self.assertIn(heading, self.doc)

    def test_conclusion_b_and_zero_hit_facts_pinned(self):
        # RAW pin + the full-text zero-hit registration for the 故 family.
        self.assertIn("0c7b0823265c4ff00465f833e0be28f1bf0f2175", self.doc)
        self.assertIn(
            "d80c42b0b8f44f5b8cf2c4e1c286b200388b65dcd321347eb7ac1011d0be5e97",
            self.doc)
        self.assertIn("全书无一「故」字", self.doc)
        self.assertIn("结论 B", self.doc)
        self.assertIn("不存在能支撑「故人」主题的合格原典来源", self.doc)
        # Every adjudicated hit stays verbatim in the doc's table.
        for entry in (
            "洗足旧患除", "木梳旧事尽去", "远人来悲泣主凶", "死人食者主疾病",
            "开棺与死人言凶", "棺敛死人主得财", "死人哭泣有口舌",
            "死人立者主大凶", "先祖考言求食吉", "水牛主先祖索食",
            "见死亡尊长大吉", "子死者主添喜事",
        ):
            self.assertIn(entry, self.doc)

    def test_gap_kept_and_no_filling(self):
        # The gap stays registered; the revival entry must not fill it,
        # and the only exit is a new-source admission (user decision).
        self.assertIn("保持缺口登记", self.doc)
        self.assertIn("不填充故人缺口", self.doc)
        self.assertIn("不得以任何既有条目填充", self.doc)
        self.assertIn("属用户级资源决策", self.doc)
        self.assertIn("未入库任何条目", self.doc)

    def test_guren_stays_input_observation_only(self):
        # Public runtime surface unchanged: 故人 remains an unreviewed
        # input-observation topic with no reviewed interpretation.
        self.assertIn("'故人': re.compile", self.ops)
        block = self.ops.split("'故人': re.compile", 1)[1][:300]
        self.assertIn("input_observation_only", self.ops)
        self.assertIn("'reviewed_interpretation_available': False", self.ops)
        self.assertNotIn("dream.term.deceased", self.ops)
        self.assertNotIn("dream.term.guren", self.ops)
        self.assertTrue(block.strip())

    def test_ledger_event_and_status_row(self):
        rows = [line for line in self.history.splitlines()
                if line.startswith("| E0357 |")]
        self.assertEqual(len(rows), 1)
        cells = [c.strip() for c in rows[0].strip().strip("|").split("|")]
        self.assertEqual(len(cells), 8)
        self.assertEqual(cells[2], "TJ-019.2")
        self.assertEqual(cells[3], "阻塞")
        status_rows = [line for line in self.status.splitlines()
                       if line.startswith("| TJ-019.2 |")]
        self.assertEqual(len(status_rows), 1)
        self.assertIn("阻塞", status_rows[0])
        self.assertIn("E0357", status_rows[0])
        self.assertIn("TJ0192_GUREN_SOURCE_AUDIT.md", status_rows[0])


if __name__ == "__main__":
    unittest.main()
