"""TJ-022.2 配偶星×桃花年运结构面审定（E0359）：公开治理测试。

审定批结论钉：Q1 配对只许位置级事实（同一性＋已审六合/六害/六冲，
禁入旺衰喜忌、效力、婚恋预测与评分）；Q2 取 (ii) 新增可选输入
traditional_role 沿合盘在产先例、缺席即配对块整体缺席（产品面
影响在审定文档 §3.3 单独标明）。本测试只读公开文件——审定文档、
台账两件、场景引擎与透镜源码、出生档案类型。

状态转换钉（E0360）：审定批在此钉住的「现行契约逐字未变」已按
审定 §3.2/§6 由实现批 E0360 有意更新为裁定后的新契约形态
（可选集恰增 traditional_role 一键、校验与透传同形于合盘先例、
_life 仍不转发 role）；其余审定结论钉不变。

组装树守卫（E0360 修复）：离线验收的组装后端树按构造不含 web/
目录；birthProfile.ts 只存在于真实检出。审定批原 setUpClass 无
条件读取该文件，使本模块在组装树内整体 error 并令 6b8964ef 的
管线验收三次失败（E0360 复现定位）。修复只加存在性守卫：文件
在场时全部断言逐字不变（公开 CI 与本地真实检出），缺席时该一
条测试如实 skip 并注明原因，不计通过。
"""

from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs" / "product" / "TJ0222_SPOUSE_STAR_ADJUDICATION.md"
HISTORY = ROOT / "docs" / "product" / "TASK_HISTORY.md"
STATUS = ROOT / "docs" / "product" / "TASK_STATUS.md"
ENGINE = ROOT / "src" / "tianji_kb" / "scenario_engine.py"
CORE = ROOT / "src" / "tianji_kb" / "bazi_core.py"
PROFILE = ROOT / "web" / "visual-prototype" / "src" / "public" / "birthProfile.ts"


class SpouseStarAdjudicationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc = DOC.read_text(encoding="utf-8")
        cls.history = HISTORY.read_text(encoding="utf-8")
        cls.status = STATUS.read_text(encoding="utf-8")
        cls.engine = ENGINE.read_text(encoding="utf-8")
        cls.core = CORE.read_text(encoding="utf-8")
        # The assembled offline-backend tree carries no web/ tree by
        # construction; read the profile type only on real checkouts.
        cls.profile = (PROFILE.read_text(encoding="utf-8")
                       if PROFILE.exists() else None)

    def test_adjudication_doc_on_file_with_all_sections(self):
        for heading in (
            "## 0 授权与范围",
            "## 1 开工核实与基线实测",
            "## 2 Q1 裁定：配对只许位置级事实",
            "### 2.1 允许的配对事实（穷举三类）",
            "### 2.2 禁止项（穷举）",
            "### 2.3 配对结构数据形态（字段级契约）",
            "### 2.4 空态与 fail-closed 条件",
            "## 3 Q2 裁定：新增可选输入 traditional_role（结论 ii）【产品面影响单独标明】",
            "### 3.1 三案证据与裁定理由",
            "### 3.2 输入契约裁定",
            "### 3.3 产品面影响（单独标明，供父级合并审读）",
            "### 3.4 与既有输入契约的相容性",
            "## 4 与既有配偶宫结构的组合方式",
            "## 5 Golden 设计判据",
            "## 6 实现批（E0360）验收清单",
            "## 7 仍不可判断范围",
            "## 8 本批产出与边界",
        ):
            self.assertIn(heading, self.doc)

    def test_q1_position_level_only_and_prohibitions_pinned(self):
        self.assertIn("配对只许位置级事实", self.doc)
        for allowed in ("P1 地支同一性", "P2 已审地支关系", "P3 天干同一性"):
            self.assertIn(allowed, self.doc)
        for rule_id in (
            "bazi.phase2.branch_six_harmonies",
            "bazi.phase2.branch_six_harms",
            "bazi.phase2.branch_six_clashes",
        ):
            self.assertIn(rule_id, self.doc)
        # Prohibition tokens named in the adjudication stay on file.
        for token in ("fortune_score", "marriage_date", "breakup_risk"):
            self.assertIn(token, self.doc)
        self.assertIn("spouse_star_year_pairing", self.doc)
        self.assertIn("no_candidates", self.doc)
        self.assertIn("F1 role 非法", self.doc)
        self.assertIn("F6 未知键", self.doc)

    def test_q2_verdict_ii_and_rejected_alternatives_pinned(self):
        self.assertIn("裁定取 (ii)", self.doc)
        # (i) rejection rests on two measured facts: the lens is opt-in
        # on an explicit role, and the stored birth profile carries
        # no gender field (both pinned by the tests below).
        self.assertIn("(i) 无需新输入即可自洽计算——否决", self.doc)
        self.assertIn("(iii) 输入不足、本项收敛——不取", self.doc)
        self.assertIn("产品面影响（单独标明", self.doc)
        self.assertIn("同一实现批（E0360）内同时落地", self.doc)

    def test_current_contract_matches_e0359_verdict(self):
        # State-transition pin (E0360, per adjudication §3.2/§6 and
        # this file's header): the pre-implementation contract pin is
        # intentionally replaced by the adjudicated contract shape —
        # _romance takes {birth_value, target_year} plus optional
        # {birth_zone, traditional_role}, validates and forwards the
        # role exactly like the compatibility precedent, and _life
        # still forwards no role.
        start = self.engine.index("def _romance(inputs):")
        end = self.engine.index("\ndef ", start + 10)
        romance = self.engine[start:end]
        self.assertIn(
            '_require_with_optional(inputs, {"birth_value", "target_year"}, {"birth_zone", "traditional_role"})',
            romance,
        )
        self.assertIn('traditional_role not in ("male", "female")', romance)
        self.assertIn('natal_input["traditional_role"] = traditional_role', romance)
        self.assertIn("spouse_star_year_pairing", romance)
        life_start = self.engine.index("def _life(inputs):")
        life_end = self.engine.index("\ndef ", life_start + 10)
        life = self.engine[life_start:life_end]
        self.assertNotIn("traditional_role", life)
        # The lens itself keeps its registered basis and strict role.
        self.assertIn("user_selected_traditional_lens", self.core)
        self.assertIn('if traditional_role not in ("male", "female"):', self.core)

    def test_birth_profile_has_no_gender_field(self):
        # Q2 evidence leg: the stored BirthInput type has no gender
        # field to derive a role from (calendar/date/time/region only).
        if self.profile is None:
            self.skipTest(
                "web tree not present in assembled backend; this pin "
                "runs on real checkouts (public CI / local)")
        start = self.profile.index("export type BirthInput = {")
        end = self.profile.index("};", start)
        block = self.profile[start:end]
        self.assertIn("calendarType", block)
        self.assertIn("_regionNeedsConfirm", block)
        self.assertNotIn("gender", block)

    def test_ledger_event_and_status_row(self):
        rows = [line for line in self.history.splitlines()
                if line.startswith("| E0359 |")]
        self.assertEqual(len(rows), 1)
        cells = [c.strip() for c in rows[0].strip().strip("|").split("|")]
        self.assertEqual(len(cells), 8)
        self.assertEqual(cells[2], "TJ-022.2")
        self.assertEqual(cells[3], "阻塞")
        self.assertEqual(cells[5:], ["—", "—", "—"])
        status_rows = [line for line in self.status.splitlines()
                       if line.startswith("| TJ-022.2 |")]
        self.assertEqual(len(status_rows), 1)
        self.assertIn("阻塞", status_rows[0])
        self.assertIn("E0359", status_rows[0])
        self.assertIn("TJ0222_SPOUSE_STAR_ADJUDICATION.md", status_rows[0])


if __name__ == "__main__":
    unittest.main()
