"""TJ-022.2 配偶星结构面实现（E0360）：公开治理测试。

本测试只读公开文件——审定文档（含 §9 实施记录）、场景引擎与前端
源码、台账两件与 CI 配置——钉住：实施记录在册且五问与验收清单
逐项有据、后端契约形态（可选键、配对块、匹配与 trace 步 id、
limitations 原文）与审定逐字对平、前端控件与发送形态同批落地、
台账 E0360 归属与行状态不变。真实配对计算的 Golden 在
tests/test_romance_spouse_star_pairing.py（离线验收执行）。
前端与 CI 配置类钉（页面、api.ts、stub spec、validate.yml）在
离线验收的组装后端树内按构造不存在（组装树不含 web/ 与
.github/），该两条在组装树内如实 skip 并注明原因、在真实检出
（公开 CI 按名执行本模块）全量断言；同批对 E0359 审定测试的同
类问题作了同一守卫修复，根因与证据见审定文档 §9.5。
"""
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
DOC = ROOT / "docs" / "product" / "TJ0222_SPOUSE_STAR_ADJUDICATION.md"
STATUS = ROOT / "docs" / "product" / "TASK_STATUS.md"
HISTORY = ROOT / "docs" / "product" / "TASK_HISTORY.md"
ENGINE = ROOT / "src" / "tianji_kb" / "scenario_engine.py"
PAGE = (ROOT / "web" / "visual-prototype" / "src" / "public"
        / "RomanceStructurePage.tsx")
API_TS = ROOT / "web" / "visual-prototype" / "src" / "public" / "api.ts"
STUB_SPEC = (ROOT / "web" / "visual-prototype" / "tests"
             / "b028-booklet-stubs.spec.ts")
VALIDATE = ROOT / ".github" / "workflows" / "validate.yml"


class SpouseStarE0360PublicTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc = DOC.read_text(encoding="utf-8")
        cls.status = STATUS.read_text(encoding="utf-8")
        cls.history = HISTORY.read_text(encoding="utf-8")
        cls.engine = ENGINE.read_text(encoding="utf-8")
        # The assembled offline-backend tree carries no web/ or
        # .github/ tree by construction; frontend and CI-config pins
        # read their files only on real checkouts and skip (with the
        # reason recorded) inside the assembled backend, where public
        # CI on the real checkout runs them in full.
        cls.page = (PAGE.read_text(encoding="utf-8")
                    if PAGE.exists() else None)
        cls.api_ts = (API_TS.read_text(encoding="utf-8")
                      if API_TS.exists() else None)
        cls.stub = (STUB_SPEC.read_text(encoding="utf-8")
                    if STUB_SPEC.exists() else None)
        cls.validate = (VALIDATE.read_text(encoding="utf-8")
                        if VALIDATE.exists() else None)

    def test_implementation_record_sections_present(self):
        self.assertIn("## 9 实施记录（E0360，append-only 补记）", self.doc)
        for heading in ("### 9.0 实施范围", "### 9.1 五问答复",
                        "### 9.2 验收清单逐项结果",
                        "### 9.3 Golden 用例表（手工复核推导）",
                        "### 9.4 等价比对语料与结果",
                        "### 9.5 与审定的偏差与实测订正"):
            self.assertIn(heading, self.doc)
        self.assertIn("22 封套逐字节全等", self.doc)
        self.assertIn("ALL OK", self.doc)
        self.assertIn("流年天干十神归属候选集", self.doc)

    def test_engine_contract_shape_matches_adjudication(self):
        self.assertIn("def _spouse_star_year_pairing(", self.engine)
        self.assertIn('"bazi.scenario.spouse_star_year_pairing"', self.engine)
        self.assertIn('"reviewed_spouse_star_target_year_pairing"', self.engine)
        self.assertIn('"reviewed_spouse_star_positions_and_year_pairs"',
                      self.engine)
        self.assertIn(
            "只观察配偶星候选位置与目标流年干支的同一性与已审六合、六害、六冲；"
            "无命中不代表配偶星缺失或婚恋缺失，不判断婚期、正缘、吉凶、合化或旺衰喜忌。",
            self.engine)
        self.assertIn(
            "夫妻宫仅以日支位置配对已审六合、六冲、六害；配偶星仅以候选位置与"
            "流年干支作同一性及已审六合、六冲、六害配对；三合、刑、破、合化效力、"
            "旺衰喜忌、大运和紫微等未组合裁定。",
            self.engine)
        # The adjudicated-out pairing (flow-stem ten-god attribution)
        # was NOT implemented, and no verdict vocabulary exists in the
        # pairing function.
        start = self.engine.index("def _spouse_star_year_pairing(")
        end = self.engine.index("\ndef ", start + 10)
        pairing = self.engine[start:end]
        for token in ("fortune_score", "marriage_date",
                      "compatibility_percent", "breakup_risk",
                      "flow_ten_god", "target_ten_god"):
            self.assertNotIn(token, pairing)

    def test_frontend_control_and_projection_in_same_batch(self):
        if self.page is None or self.api_ts is None or self.stub is None:
            self.skipTest(
                "web tree not present in assembled backend; frontend "
                "pins run on real checkouts (public CI / local)")
        self.assertIn("传统配偶星口径（可选）", self.page)
        self.assertIn("if (role) romanceInput.traditional_role = role;",
                      self.page)
        self.assertIn("spouse_star_year_pairing", self.page)
        self.assertIn('traditional_role?: "male" | "female"', self.api_ts)
        self.assertIn("traditional_role", self.stub)
        self.assertIn("renders the pairing block", self.stub)

    def test_ledger_event_and_status_row(self):
        rows = [line for line in self.history.splitlines()
                if line.startswith("| E0360 |")]
        self.assertEqual(len(rows), 1)
        self.assertIn("TJ-022.2", rows[0])
        self.assertIn("阻塞", rows[0])
        row = next(line for line in self.status.splitlines()
                   if line.startswith("| TJ-022.2 |"))
        self.assertIn("阻塞", row)
        self.assertIn("E0359", row)
        self.assertIn("E0360", row)

    def test_public_governance_test_wired_into_validate_yml(self):
        if self.validate is None:
            self.skipTest(
                ".github tree not present in assembled backend; this "
                "pin runs on real checkouts (public CI / local)")
        self.assertIn("test_tj0222_spouse_star_e0360_public.py", self.validate)


if __name__ == "__main__":
    unittest.main()
