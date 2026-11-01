"""TJ-017.3 分阶段开放第二阶段独立性复核与开放契约审定（E0374）：公开治理测试。

审定批结论钉：独立性复核判方向/三命换算/神峰换算（限首运）/序列
事实/方法选择与来源呈现独立，人生总览大运维与跨规则作用效力面不
在本阶段；开放经 bazi-profile 定域新对象 dayun_presentation
（Variant dayun-public-presentation-v1）与新增可选输入
traditional_role 达成，源 Variant、组合/视图治理标志与治理登记三
行不翻转；本批只审定未实现——场景层现行契约逐字未变、投影剥离表
未含新键、构建器模块尚不存在。实现批 E0375 落地时须按审定 §7
有意更新本文件的现状钉（状态转换钉，依据 E0374）。

本测试只读组装树内文件（docs/、src/、tests/ 与台账两件），不读
web/ 任何文件——E0359 教训：治理测试不得无条件读取组装树外文件；
本批审定不依赖前端源码断言（前端控件与呈现由实现批以其专项钉
住），故无需存在性守卫。
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs" / "product" / "TJ0173_STAGED_OPENING_PHASE2.md"
HISTORY = ROOT / "docs" / "product" / "TASK_HISTORY.md"
STATUS = ROOT / "docs" / "product" / "TASK_STATUS.md"
ENGINE = ROOT / "src" / "tianji_kb" / "engine.py"
SCENARIO = ROOT / "src" / "tianji_kb" / "scenario_engine.py"
API = ROOT / "src" / "tianji_kb" / "api.py"
PROJECTION = ROOT / "src" / "tianji_kb" / "public_projection.py"
COMPOSE = ROOT / "src" / "tianji_kb" / "bazi_dayun_compose.py"
VIEW = ROOT / "src" / "tianji_kb" / "bazi_dayun_timeline_view.py"
GOVERNANCE = ROOT / "src" / "tianji_kb" / "bazi_registration_governance.py"
PUBLIC_BUILDER = ROOT / "src" / "tianji_kb" / "bazi_dayun_public.py"

RESEARCH_FLAG_FRAGMENT = (
    "'research_only': True, 'public_enabled': False,\n"
    "            'ai_enabled': False")


class StagedOpeningPhase2AdjudicationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc = DOC.read_text(encoding="utf-8")
        cls.history = HISTORY.read_text(encoding="utf-8")
        cls.status = STATUS.read_text(encoding="utf-8")
        cls.engine = ENGINE.read_text(encoding="utf-8")
        cls.scenario = SCENARIO.read_text(encoding="utf-8")
        cls.api = API.read_text(encoding="utf-8")
        cls.projection = PROJECTION.read_text(encoding="utf-8")
        cls.governance = GOVERNANCE.read_text(encoding="utf-8")

    def test_adjudication_doc_registered_with_contract_anchors(self):
        for anchor in (
            "dayun-public-presentation-v1", "dayun_presentation",
            "bazi_dayun_public.py", "public_dayun_presentation",
            "traditional_role", "独立性复核", "门控翻转清单",
            "暂不可判契约", "Golden 判据设计", "E0375", "E0376",
            "bazi.rule.r038", "bazi.rule.r039", "bazi.rule.r041",
            "inherited_registered_phase1_phase2",
        ):
            self.assertIn(anchor, self.doc)

    def test_source_governance_flags_unflipped(self):
        # 组合与视图的治理标志集逐字不变（审定 §7 第 5 项）：开放不
        # 经由翻转源标志达成。运行时纯函数实测同结论。
        for path in (COMPOSE, VIEW):
            text = path.read_text(encoding="utf-8")
            self.assertIn(RESEARCH_FLAG_FRAGMENT, text, path.name)
            self.assertIn(
                "'evidence_binding': "
                "'inherited_registered_phase1_phase2'", text, path.name)
        sys.path.insert(0, str(ROOT / "src"))
        from tianji_kb import bazi_dayun_compose, bazi_dayun_timeline_view
        expected = {"research_only": True, "public_enabled": False,
                    "ai_enabled": False,
                    "evidence_binding":
                        "inherited_registered_phase1_phase2"}
        self.assertEqual(bazi_dayun_compose._flags(), expected)
        self.assertEqual(bazi_dayun_timeline_view._flags(), expected)
        self.assertEqual(bazi_dayun_timeline_view.AGE_PRESENTATION,
                         "not_presented")

    def test_registered_segments_and_inherited_rows_in_governance(self):
        # dayun-classical-variants 已注册（r038/r039/r041 与三 Phase2
        # 步）；compose 与 timeline-view 两行 inherited 终局形态。
        for anchor in (
            "'item': 'dayun-classical-variants'",
            "'disposition': 'registered'",
            "bazi.rule.r038", "bazi.rule.r039", "bazi.rule.r041",
            "bazi.phase2.dayun_classical_direction",
            "bazi.phase2.dayun_sanming_conversion",
            "bazi.phase2.dayun_shenfeng_conversion",
            "'item': 'dayun-compose'", "'item': 'dayun-timeline-view'",
        ):
            self.assertIn(anchor, self.governance)

    def test_scenario_contract_and_public_surface_unchanged(self):
        # 审定批未实现钉（实现批按 §7 更新）：bazi-profile 契约逐字
        # 未增 traditional_role；场景层与 API 层无 dayun 呈现引用；
        # 构建器模块尚不存在。
        self.assertIn(
            '_require_with_optional(inputs, {"value"}, '
            '{"strength_variant", "zone"})', self.scenario)
        for token in ("dayun_presentation", "bazi_dayun_public",
                      "public_dayun_presentation",
                      "classical_dayun_timeline"):
            self.assertNotIn(token, self.scenario, token)
            self.assertNotIn(token, self.api, token)
        self.assertFalse(PUBLIC_BUILDER.exists())

    def test_projection_strip_list_baseline(self):
        # 既有 dayun 研究键全域剥离在册（审定基线）；新呈现键尚未进
        # 剥离表（实现批按 §7 第 3 项新增全域剥离 + 定域放行）。
        for key in ("dayun_timeline_view", "dayun_timeline_views",
                    "dayun_classical_direction",
                    "dayun_sanming_conversion",
                    "dayun_shenfeng_conversion"):
            self.assertIn("container.pop('%s', None)" % key,
                          self.projection, key)
        self.assertNotIn("dayun_presentation", self.projection)

    def test_engine_client_research_gates_registered(self):
        for message in (
            "Classical dayun direction requires explicit research mode",
            "Classical dayun Sanming conversion requires explicit "
            "research mode",
            "Classical dayun Shenfeng conversion requires explicit "
            "research mode",
            "Dayun Jie distance requires explicit research mode",
        ):
            self.assertIn(message, self.engine)

    def test_life_overview_dayun_approval_stays_closed(self):
        # 人生总览大运维不在本阶段：两处硬编码旗标恒 False 在册。
        self.assertEqual(
            self.scenario.count('"dayun_timeline_approved": False'), 2)
        self.assertNotIn('"dayun_timeline_approved": True',
                         self.scenario)

    def test_ledger_records_adjudication(self):
        self.assertIn("| E0374 |", self.history)
        self.assertIn("TJ0173_STAGED_OPENING_PHASE2.md", self.history)
        row = next(line for line in self.status.splitlines()
                   if line.startswith("| TJ-017.3 |"))
        self.assertIn("| 阻塞 |", row)
        self.assertIn("TJ0173_STAGED_OPENING_PHASE2.md", row)


if __name__ == "__main__":
    unittest.main()
