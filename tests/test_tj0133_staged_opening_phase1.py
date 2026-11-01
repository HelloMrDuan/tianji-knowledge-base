"""TJ-013.3 分阶段开放第一阶段开放契约审定（E0371）：公开治理测试。

审定批结论钉：开放范围严格限定已注册的调候、病药两体系；呈现面
为 bazi-profile 场景结果内的 xiyong_presentation 对象（Variant
xiyong-public-presentation-v1）；开放经新对象达成、两 Variant 与
readable Variant 的研究标志不翻转；engine 客户端四研究键门禁在本
批后逐字不变。「零引用」与「剥离表」两钉已由实现批 E0372 按审
定 §7 第 3/5 项有意更新为裁定后的新形态（状态转换钉，依据
E0371）：场景层服务端专属开启门引用 tiaohou/bingyao/
xiyong_presentation 为审定内行为，readable_hints/
conflict_presentation 两层仍零引用、api.py 六 token 仍全零；投
影剥离表新增 xiyong_presentation 全域剥离 + 经形态校验的定域放
行（仅 bazi-profile 信封）。

本测试只读组装树内文件（docs/、src/、tests/ 与台账两件），不读
web/ 任何文件——E0359 教训：治理测试不得无条件读取组装树外文
件；本批审定不依赖前端源码断言（前端文案收窄由实现批以其专项
钉住），故无需存在性守卫。
"""

from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs" / "product" / "TJ0133_STAGED_OPENING_PHASE1.md"
HISTORY = ROOT / "docs" / "product" / "TASK_HISTORY.md"
STATUS = ROOT / "docs" / "product" / "TASK_STATUS.md"
ENGINE = ROOT / "src" / "tianji_kb" / "engine.py"
SCENARIO = ROOT / "src" / "tianji_kb" / "scenario_engine.py"
API = ROOT / "src" / "tianji_kb" / "api.py"
PROJECTION = ROOT / "src" / "tianji_kb" / "public_projection.py"
TIAOHOU = ROOT / "src" / "tianji_kb" / "bazi_tiaohou.py"
BINGYAO = ROOT / "src" / "tianji_kb" / "bazi_bingyao.py"
READABLE = ROOT / "src" / "tianji_kb" / "bazi_xiyong_readable.py"

RESEARCH_FLAG_FRAGMENT = (
    "'research_only': True, 'public_enabled': False, 'ai_enabled': False")


class StagedOpeningPhase1AdjudicationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc = DOC.read_text(encoding="utf-8")
        cls.history = HISTORY.read_text(encoding="utf-8")
        cls.status = STATUS.read_text(encoding="utf-8")
        cls.engine = ENGINE.read_text(encoding="utf-8")
        cls.scenario = SCENARIO.read_text(encoding="utf-8")
        cls.api = API.read_text(encoding="utf-8")
        cls.projection = PROJECTION.read_text(encoding="utf-8")

    def test_adjudication_doc_registered_with_contract_anchors(self):
        for anchor in (
            "xiyong-public-presentation-v1", "xiyong_presentation",
            "tiaohou_bingyao_only", "bazi_xiyong_public.py",
            "public_xiyong_presentation", "E0372", "E0373",
            "门控翻转清单", "暂不可判契约", "Golden 判据设计",
            "not_judgeable", "entry_absent_in_source",
        ):
            self.assertIn(anchor, self.doc)

    def test_variants_keep_research_flags_unflipped(self):
        # 两 Variant 与 readable Variant 的陈述标志逐字不变（审定 §7
        # 第 4 项）：开放不经由翻转 Variant 标志达成。
        for path in (TIAOHOU, BINGYAO, READABLE):
            text = path.read_text(encoding="utf-8")
            self.assertIn(RESEARCH_FLAG_FRAGMENT, text, path.name)

    def test_variant_statements_functionally_research_only(self):
        # 纯函数实测：调候缺席/命中两形态与病药陈述的标志、绑定与
        # determination 纪律在运行时成立，不只是源码字面。
        import sys
        sys.path.insert(0, str(ROOT / "src"))
        from tianji_kb.bazi_tiaohou import tiaohou_lookup
        from tianji_kb.bazi_bingyao import bingyao_lookup

        absent = tiaohou_lookup(
            "乙", "丑", ["己", "丁", "乙", "壬"],
            [["癸"], ["己", "癸", "辛"], ["乙"], ["壬"]])
        self.assertEqual(absent["status"], "not_applicable")
        self.assertEqual(absent["reason"], "entry_absent_in_source")
        self.assertIs(absent["research_only"], True)
        self.assertIs(absent["public_enabled"], False)
        self.assertIs(absent["ai_enabled"], False)
        self.assertEqual(absent["evidence_binding"],
                         "registered_phase1_phase2")

        matched = tiaohou_lookup(
            "甲", "寅", ["庚", "己", "甲", "乙"],
            [["癸"], ["甲", "丙", "戊"], ["丁", "己"], ["己", "癸", "辛"]])
        self.assertEqual(matched["status"], "matched")
        self.assertIs(matched["public_enabled"], False)
        self.assertEqual(matched["evidence_binding"],
                         "registered_phase1_phase2")

        bingyao = bingyao_lookup("甲", [
            {"pillar": "year", "stem": "庚", "ten_god": "七杀"},
            {"pillar": "month", "stem": "己", "ten_god": "正财"},
            {"pillar": "hour", "stem": "乙", "ten_god": "劫财"},
        ])
        self.assertEqual(bingyao["status"], "triggered")
        self.assertIsNone(bingyao["determination"])
        self.assertEqual(bingyao["medicine_effect_status"],
                         "unadjudicated")
        self.assertIs(bingyao["public_enabled"], False)
        self.assertIs(bingyao["ai_enabled"], False)

    def test_scenario_and_api_have_zero_research_object_references(self):
        # 状态转换钉（E0372 按审定 §7 第 3 项有意更新，依据 E0371；
        # 原钉为审定批的零引用基线）：实现批的开启门住在场景层，
        # scenario_engine 引用 tiaohou/bingyao/xiyong_presentation
        # 与构建器为审定内行为；但 readable/conflict 两研究对象在场
        # 景层仍须零引用（不在本阶段接线），api.py 对六 token 仍全
        # 零（API 层不新增任何研究对象接线）。
        for token in ("readable_hints", "conflict_presentation"):
            self.assertNotIn(token, self.scenario, token)
        for token in ("tiaohou_variant", "bingyao_variant",
                      "xiyong_presentation", "public_xiyong_presentation",
                      "allow_research=True"):
            self.assertIn(token, self.scenario, token)
        for token in ("tiaohou", "bingyao", "xiyong",
                      "readable_hints", "conflict_presentation",
                      "xiyong_presentation"):
            self.assertNotIn(token, self.api, token)

    def test_engine_client_research_gates_registered(self):
        for message in (
            "Tiaohou entry statements require explicit research mode",
            "Bingyao structural candidates require explicit research mode",
            "Cross-system conflict presentation requires explicit "
            "research mode",
            "Xiyong readable hints require explicit research mode",
        ):
            self.assertIn(message, self.engine)

    def test_projection_strips_raw_research_statements(self):
        # 状态转换钉（E0372 按审定 §7 第 5 项有意更新，依据 E0371）：
        # 三原料键剥离保留，xiyong_presentation 加入全域剥离表；唯
        # 一放行是经形态校验、且只认 bazi-profile 信封的定域回填。
        for key in ("tiaohou_assessment", "bingyao_assessment",
                    "readable_hints", "conflict_presentation",
                    "xiyong_presentation"):
            self.assertIn(f"container.pop('{key}', None)",
                          self.projection, key)
        self.assertIn("is_valid_public_presentation", self.projection)
        self.assertIn("data.get('scenario_id') == 'bazi-profile'",
                      self.projection)
        self.assertIn("result['result']['xiyong_presentation']",
                      self.projection)

    def test_ledger_records_adjudication(self):
        event_lines = [line for line in self.history.splitlines()
                       if line.startswith("| E0371 |")]
        self.assertEqual(len(event_lines), 1)
        self.assertIn("TJ-013.3", event_lines[0])
        self.assertIn("阻塞", event_lines[0])
        row_lines = [line for line in self.status.splitlines()
                     if line.startswith("| TJ-013.3 |")]
        self.assertEqual(len(row_lines), 1)
        self.assertIn("阻塞", row_lines[0])
        self.assertIn("E0371", row_lines[0])
        self.assertIn("TJ0133_STAGED_OPENING_PHASE1.md", row_lines[0])


if __name__ == "__main__":
    unittest.main()
