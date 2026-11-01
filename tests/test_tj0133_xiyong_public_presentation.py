"""TJ-013.3 分阶段开放第一阶段（实现批 E0372）：公开专项测试。

构建器以真实纯查找（tiaohou_lookup / bingyao_lookup）从 Golden 在
册盘面事实构造的两份陈述为输入；执行视图为**合成视图**（证据记
录与 Phase1 引用索引按注册形态伪造，条目记录坐标为真实包内坐
标、钉在 Golden 文件中）。合成视图是知识包的测试替身：真实视图
与真实包的恰等、真实场景/API 信封对平由密封专项
test_tj0133_xiyong_public_sealed.py 在离线验收中钉住，本文件不冒
称真实执行。篡改四类、投影定域与内容禁入在本文件以合成视图与合
成信封实测；前端源码断言带存在性守卫（组装树无 web/ 时跳过该
段，沿 E0359/E0362 先例）。
"""

from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from tianji_kb.bazi_bingyao import RULES as BINGYAO_RULES
from tianji_kb.bazi_bingyao import bingyao_lookup
from tianji_kb.bazi_tiaohou import entry_for, tiaohou_lookup
from tianji_kb.bazi_xiyong_public import (
    BINGYAO_STEP_ID,
    SCOPE_STATEMENT,
    TIAOHOU_STEP_ID,
    VARIANT,
    is_valid_public_presentation,
    public_xiyong_presentation,
)
from tianji_kb.public_projection import project_execution
from tianji_kb.scenario_engine import execute_scenario

ROOT = Path(__file__).resolve().parents[1]
GOLDEN = json.loads(
    (ROOT / "tests" / "golden_tj0133_xiyong_public.json").read_text(
        encoding="utf-8"))
CASES = {case["id"]: case for case in GOLDEN["cases"]}
SHENFENG_SECTION = "bazi.section.s071"
BINGYAO_REF_TEXTS = [
    "何以为之病?原八字中原所害之神也",
    "何以为之药?如八字原有所害之字,而得一字以去之谓了",
] + [rule["quote"] for rule in BINGYAO_RULES]

BANNED_SUBSTRINGS = (
    "吉", "凶", "宜", "忌", "灾", "祸", "发财", "升职", "旺财", "旺夫",
    "喜用神", "宜用", "忌用", "推荐", "建议", "评分", "得分",
    "扶抑", "格局", "旺衰", "统一喜用", "真格", "假格",
)


def _record(source_id, section_id, chapter_id, chapter_title, text, rule_id):
    return {
        "source_id": source_id, "section_id": section_id,
        "chapter_id": chapter_id, "chapter_title": chapter_title,
        "original_text": text, "rule_id": rule_id,
        "evidence_level": "C", "variant": "synthetic-view",
    }


def _statements(case):
    """Pure lookups plus the assessment layer's deterministic
    augmentation (consumed_rule_ids / fact_refs), mirrored verbatim
    from tiaohou_assessment / bingyao_assessment: the fact steps sit
    at trace positions 0-2 of the synthetic view. The real assessment
    augmentation over a real trace is exercised by the sealed tests.
    """
    facts = case["facts"]
    tiaohou = tiaohou_lookup(
        facts["day_master"], facts["month_branch"],
        facts["tiaohou"]["visible_stems"],
        facts["tiaohou"]["hidden_stems"])
    tiaohou["consumed_rule_ids"] = [
        "bazi.phase2.pillars", "bazi.phase2.ten_gods",
        "bazi.phase2.hidden_stems"]
    tiaohou["fact_refs"] = {
        "pillars": "#/trace/0/output", "ten_gods": "#/trace/1/output",
        "hidden_stems": "#/trace/2/output"}
    bingyao = bingyao_lookup(
        facts["day_master"], facts["bingyao"]["visible_gods"])
    bingyao["consumed_rule_ids"] = [
        "bazi.phase2.pillars", "bazi.phase2.ten_gods"]
    bingyao["fact_refs"] = {
        "pillars": "#/trace/0/output", "ten_gods": "#/trace/1/output"}
    return tiaohou, bingyao


def _synthetic_view(case, tiaohou, bingyao):
    """Fabricate the execution view in the registered shapes.

    The Phase1 reference index carries exactly the pairs the builder
    must derive from (entry pair + encoded branch pairs for the
    expected owner rule; the four registered r040 pairs for bingyao).
    Full-bundle equality of the real index is the sealed test's job.
    """
    evidence = {}
    trace = []
    matches = []

    def add_step(rule_id, output, records, *, matched=True):
        ids = []
        for index, record in enumerate(records):
            evidence_id = f"{rule_id}#{index}"
            evidence[evidence_id] = record
            ids.append(evidence_id)
        trace.append({"rule_id": rule_id, "evidence_scope": "registered",
                      "inputs": {}, "output": output, "evidence_ids": ids})
        matches.append({"rule_id": rule_id, "matched": matched,
                        "kind": "executed_calculation",
                        "evidence_scope": "registered",
                        "evidence_ids": list(ids)})
        return ids

    dummy = {"source_id": "bazi.source.fact", "section_id": "s",
             "chapter_id": "c", "chapter_title": "t",
             "original_text": "fact", "rule_id": "bazi.phase2.pillars"}
    add_step("bazi.phase2.pillars", {}, [dict(dummy)])
    add_step("bazi.phase2.ten_gods", [], [dict(dummy)])
    add_step("bazi.phase2.hidden_stems", [], [dict(dummy)])
    tiaohou_refs = {}
    tiaohou_records = []
    entry_info = case["view"]["entry"]
    if entry_info is None:
        # N1: the real step still resolves its full evidence binding;
        # the synthetic view carries one bound record for shape.
        tiaohou_records.append(_record(
            "bazi.source.qiongtong", "bazi.section.s085",
            "bazi.chapter.qiongtong_yi", "乙木分月条目",
            "（合成视图占位记录）", TIAOHOU_STEP_ID))
    if entry_info is not None:
        pairs = [(entry_info["section_id"], tiaohou["entry"]["quote"])]
        tiaohou_records.append(_record(
            "bazi.source.qiongtong", entry_info["section_id"],
            entry_info["chapter_id"], entry_info["chapter_title"],
            tiaohou["entry"]["quote"], TIAOHOU_STEP_ID))
        for branch in tiaohou["branches"]:
            pairs.append((entry_info["section_id"], branch["quote"]))
            tiaohou_records.append(_record(
                "bazi.source.qiongtong", entry_info["section_id"],
                entry_info["chapter_id"], entry_info["chapter_title"],
                branch["quote"], TIAOHOU_STEP_ID))
        tiaohou_refs = {case["expected"]["tiaohou_phase1_rule_id"]: pairs}
    add_step(TIAOHOU_STEP_ID, tiaohou, tiaohou_records)
    bingyao_records = [
        _record("bazi.source.shenfeng", SHENFENG_SECTION,
                case["view"]["bingyao_chapter_id"], "神峰通考病药篇",
                text, BINGYAO_STEP_ID)
        for text in BINGYAO_REF_TEXTS]
    add_step(BINGYAO_STEP_ID, bingyao, bingyao_records)
    return {
        "trace": trace, "rule_matches": matches, "evidence": evidence,
        "phase1_rule_refs": {
            TIAOHOU_STEP_ID: tiaohou_refs,
            BINGYAO_STEP_ID: {
                "bazi.rule.r040": [(SHENFENG_SECTION, text)
                                   for text in BINGYAO_REF_TEXTS]},
        },
    }


def _build(case):
    tiaohou, bingyao = _statements(case)
    view = _synthetic_view(case, tiaohou, bingyao)
    return public_xiyong_presentation(tiaohou, bingyao, execution=view)


def _strings(value):
    """System-composed strings only: verbatim registered text (quote
    fields, the entry's order basis) and the scope statement are
    exempt from the wording scan — quotes are pinned verbatim against
    the registered data instead (a classical quote may itself contain
    characters like 「切忌」; presenting it verbatim is the §4
    contract, not a system verdict), and the scope statement is the
    one registered negation context, pinned as an exact constant.
    """
    if isinstance(value, dict):
        for key, item in value.items():
            if key in ("quote", "entry_basis", "scope_statement"):
                continue
            yield from _strings(item)
    elif isinstance(value, list):
        for item in value:
            yield from _strings(item)
    elif isinstance(value, str):
        yield value


def _keys(value):
    if isinstance(value, dict):
        for key, item in value.items():
            yield key
            yield from _keys(item)
    elif isinstance(value, list):
        for item in value:
            yield from _keys(item)


class GoldenPresentationTests(unittest.TestCase):
    def test_golden_cases_cover_adjudicated_matrix(self):
        self.assertEqual(len(CASES), 9)
        for prefix in ("G1-", "G2-", "G3-", "G4-", "G5-", "G6-", "G7-",
                       "G8-branch-condition-applies",
                       "G8-branch-condition-not-applies"):
            self.assertTrue(
                any(case_id.startswith(prefix) for case_id in CASES),
                prefix)

    def test_golden_presentations(self):
        for case in GOLDEN["cases"]:
            with self.subTest(case=case["id"]):
                presentation = _build(case)
                expected = case["expected"]
                self.assertEqual(presentation["variant"], VARIANT)
                self.assertEqual(presentation["presentation_scope"],
                                 "tiaohou_bingyao_only")
                self.assertIsNone(presentation["unified_verdict"])
                self.assertIs(presentation["public_enabled"], True)
                self.assertIs(presentation["ai_enabled"], False)
                self.assertEqual(presentation["scope_statement"],
                                 SCOPE_STATEMENT)
                self.assertEqual(presentation["day_master"],
                                 case["facts"]["day_master"])
                self.assertEqual(presentation["month_branch"],
                                 case["facts"]["month_branch"])
                tiaohou_block = presentation["blocks"]["tiaohou"]
                bingyao_block = presentation["blocks"]["bingyao"]
                self.assertEqual(tiaohou_block["state"],
                                 expected["tiaohou_state"])
                self.assertEqual(tiaohou_block["lines"],
                                 expected["tiaohou_lines"])
                self.assertEqual(bingyao_block["lines"],
                                 expected["bingyao_lines"])
                self.assertEqual(presentation["relations"],
                                 expected["relations"])
                self.assertEqual(
                    [(b["id"], b["applied"])
                     for b in tiaohou_block.get("branches", [])],
                    [(b["id"], b["applied"]) for b in expected["branches"]])
                self.assertEqual(
                    [pair["status"] for pair in bingyao_block["pairs"]],
                    expected["pair_statuses"])
                for pair in bingyao_block["pairs"]:
                    self.assertIsNone(pair["determination"])
                    self.assertEqual(pair["medicine_effect_status"],
                                     "unadjudicated")
                    self.assertEqual(pair["efficacy_state"],
                                     "not_judgeable")
                if expected["tiaohou_state"] == "presented":
                    self.assertEqual(
                        tiaohou_block["evidence"]["phase1_rule_id"],
                        expected["tiaohou_phase1_rule_id"])
                    self.assertEqual(
                        tiaohou_block["evidence"]["section_id"],
                        expected["entry_section_id"])
                    entry = entry_for(case["facts"]["day_master"],
                                      case["facts"]["month_branch"])
                    self.assertEqual(
                        tiaohou_block["evidence"]["quote"], entry["quote"])
                    self.assertEqual(tiaohou_block["entry_basis"],
                                     entry["order_basis"])
                    dump = json.dumps(presentation, ensure_ascii=False)
                    for item in entry["unencoded_branches"]:
                        self.assertNotIn(item["quote"], dump)
                    for item in entry["related"]:
                        self.assertNotIn(item["quote"], dump)
                self.assertEqual(
                    bingyao_block["evidence"]["phase1_rule_id"],
                    "bazi.rule.r040")
                self.assertEqual(
                    bingyao_block["evidence"]["section_ids"],
                    [SHENFENG_SECTION])
                for quote_info, rule in zip(
                        bingyao_block["evidence"]["quotes"], BINGYAO_RULES):
                    self.assertEqual(quote_info["quote"], rule["quote"])

    def test_second_pair_triggered_and_medicine_absent_forms(self):
        # G5/G6 （审定 §8): the second pair is presented on its own
        # registered fields; G6's absent medicine stays a stated
        # absence with the efficacy line, never a negative verdict.
        for case_id, medicine_present in (
                ("G5-second-pair-triggered", True),
                ("G6-second-pair-triggered-medicine-absent", False)):
            presentation = _build(CASES[case_id])
            pair = presentation["blocks"]["bingyao"]["pairs"][1]
            self.assertEqual(pair["status"], "triggered")
            if medicine_present:
                self.assertEqual(pair["medicine_status"],
                                 "candidate_present")
                self.assertTrue(pair["medicine_candidate"]["gods"])
            else:
                self.assertEqual(pair["medicine_status"], "absent")
                self.assertIsNone(pair["medicine_candidate"])
                self.assertTrue(any(
                    "药之财在本盘显干中未见。" in line
                    for line in
                    presentation["blocks"]["bingyao"]["lines"]))

    def test_relations_empty_when_tiaohou_entry_absent(self):
        # G3: even with a triggered bingyao pair, no relation section
        # exists without a tiaohou sequence to relate to.
        presentation = _build(CASES["G3-tiaohou-entry-absent"])
        self.assertEqual(presentation["relations"], [])
        self.assertEqual(
            presentation["blocks"]["tiaohou"]["not_judgeable_reason"],
            "entry_absent_in_source")

    def test_deterministic_rebuild(self):
        for case in GOLDEN["cases"]:
            self.assertEqual(_build(case), _build(case), case["id"])

    def test_no_banned_content_anywhere(self):
        # G9: the whole presentation (Golden-wide) carries no verdict,
        # fortune, score or unopened-system wording. The single
        # registered exemption is the scope statement itself: it names
        # the unbuilt systems once, inside an explicit negation, and
        # is pinned as an exact constant above.
        for case in GOLDEN["cases"]:
            presentation = _build(case)
            for text in _strings(presentation):
                for banned in BANNED_SUBSTRINGS:
                    self.assertNotIn(banned, text, (case["id"], text))
                self.assertNotIn("有病", text, (case["id"], text))
                position = text.find("无病")
                while position != -1:
                    self.assertEqual(
                        text[max(0, position - 3):position], "不等于",
                        (case["id"], text))
                    position = text.find("无病", position + 1)

    def test_no_research_or_unopened_system_keys(self):
        # G10 (builder half): no research object keys and no
        # unopened-system (strength/pattern) content keys anywhere.
        forbidden = {
            "tiaohou_assessment", "bingyao_assessment", "readable_hints",
            "conflict_presentation", "strength_observation",
            "strength_factors", "pattern_candidates",
            "pattern_determination", "useful_god", "research_only",
        }
        for case in GOLDEN["cases"]:
            keys = set(_keys(_build(case)))
            self.assertFalse(keys & forbidden, (case["id"], keys))


class TamperTests(unittest.TestCase):
    """§6.2: four tamper classes against the G1 synthetic view."""

    def setUp(self):
        self.case = CASES["G1-support-first-pick-is-medicine"]
        self.tiaohou, self.bingyao = _statements(self.case)
        self.view = _synthetic_view(self.case, self.tiaohou, self.bingyao)

    def _tiaohou_step(self, view):
        return next(step for step in view["trace"]
                    if step["rule_id"] == TIAOHOU_STEP_ID)

    def test_quote_text_tampered(self):
        tiaohou = copy.deepcopy(self.tiaohou)
        quote = tiaohou["entry"]["quote"]
        tiaohou["entry"]["quote"] = quote[:-1] + "X"
        view = copy.deepcopy(self.view)
        self._tiaohou_step(view)["output"] = tiaohou
        with self.assertRaises(ValueError):
            public_xiyong_presentation(tiaohou, self.bingyao,
                                       execution=view)

    def test_record_section_tampered(self):
        view = copy.deepcopy(self.view)
        step = self._tiaohou_step(view)
        record = view["evidence"][step["evidence_ids"][0]]
        record["section_id"] = "bazi.section.s999"
        with self.assertRaises(ValueError):
            public_xiyong_presentation(self.tiaohou, self.bingyao,
                                       execution=view)

    def test_phase1_attribution_moved_to_another_rule(self):
        view = copy.deepcopy(self.view)
        refs = view["phase1_rule_refs"][TIAOHOU_STEP_ID]
        pairs = refs.pop("bazi.rule.r042")
        refs["bazi.rule.r043"] = list(pairs) + [
            ("bazi.section.s090", "乙木条目原文占位")]
        # The other rule's own references live in another chapter's
        # records; register one so the moved attribution is derivable
        # and must be caught by the chapter-homogeneity check.
        step = self._tiaohou_step(view)
        evidence_id = "bazi.phase2.tiaohou_assessment#other"
        view["evidence"][evidence_id] = _record(
            "bazi.source.qiongtong", "bazi.section.s090",
            "bazi.chapter.qiongtong_yi", "乙木分月条目",
            "乙木条目原文占位", TIAOHOU_STEP_ID)
        step["evidence_ids"] = step["evidence_ids"] + [evidence_id]
        for match in view["rule_matches"]:
            if match["rule_id"] == TIAOHOU_STEP_ID:
                match["evidence_ids"] = list(step["evidence_ids"])
        with self.assertRaises(ValueError):
            public_xiyong_presentation(self.tiaohou, self.bingyao,
                                       execution=view)

    def test_evidence_binding_deleted(self):
        view = copy.deepcopy(self.view)
        step = self._tiaohou_step(view)
        step["evidence_ids"] = step["evidence_ids"][1:]
        for match in view["rule_matches"]:
            if match["rule_id"] == TIAOHOU_STEP_ID:
                match["evidence_ids"] = list(step["evidence_ids"])
        with self.assertRaises(ValueError):
            public_xiyong_presentation(self.tiaohou, self.bingyao,
                                       execution=view)

    def test_rule_match_evidence_drift(self):
        view = copy.deepcopy(self.view)
        for match in view["rule_matches"]:
            if match["rule_id"] == TIAOHOU_STEP_ID:
                match["evidence_ids"] = []
        with self.assertRaises(ValueError):
            public_xiyong_presentation(self.tiaohou, self.bingyao,
                                       execution=view)

    def test_statement_research_flags_flipped(self):
        tiaohou = copy.deepcopy(self.tiaohou)
        tiaohou["public_enabled"] = True
        view = copy.deepcopy(self.view)
        self._tiaohou_step(view)["output"] = tiaohou
        with self.assertRaises(ValueError):
            public_xiyong_presentation(tiaohou, self.bingyao,
                                       execution=view)


class ProjectionScopeTests(unittest.TestCase):
    """§7 row 5: the scoped release — verbatim only for bazi-profile."""

    def _envelope(self, scenario_id, presentation, container="result"):
        envelope = {
            "scenario_id": scenario_id,
            "status": "ok",
            "result": {},
            "evidence": {},
            "rule_matches": [],
            "trace": [],
        }
        envelope[container] = {
            "xiyong_presentation": presentation,
            "tiaohou_assessment": {"variant": "tiaohou-qiongtong-v1"},
            "bingyao_assessment": {"variant": "bingyao-shenfeng-v1"},
            "readable_hints": {"variant": "x"},
            "conflict_presentation": {"variant": "y"},
        }
        return envelope

    def setUp(self):
        self.presentation = _build(
            CASES["G1-support-first-pick-is-medicine"])
        self.assertTrue(is_valid_public_presentation(self.presentation))

    def test_bazi_profile_release_is_verbatim(self):
        projected = project_execution(
            self._envelope("bazi-profile", self.presentation))
        self.assertEqual(projected["result"]["xiyong_presentation"],
                         self.presentation)
        for key in ("tiaohou_assessment", "bingyao_assessment",
                    "readable_hints", "conflict_presentation"):
            self.assertNotIn(key, projected["result"])

    def test_other_scenario_carrier_is_stripped(self):
        projected = project_execution(
            self._envelope("life-overview", self.presentation))
        self.assertNotIn("xiyong_presentation", projected["result"])

    def test_domain_chart_carrier_is_stripped(self):
        envelope = self._envelope("bazi-profile", self.presentation,
                                  container="chart")
        del envelope["scenario_id"]
        projected = project_execution(envelope)
        self.assertNotIn("xiyong_presentation", projected["chart"])
        self.assertNotIn("xiyong_presentation", projected["result"])

    def test_malformed_presentation_is_stripped(self):
        forged = copy.deepcopy(self.presentation)
        forged["unified_verdict"] = {"verdict": "forged"}
        projected = project_execution(
            self._envelope("bazi-profile", forged))
        self.assertNotIn("xiyong_presentation", projected["result"])


class ClientGateTests(unittest.TestCase):
    """§3.2/§7 rows 3-4: the client contract cannot reach the gate."""

    BIRTH = "1960-03-07T01:30:00+08:00"

    def test_research_keys_rejected_by_contract(self):
        for key in ("tiaohou_variant", "bingyao_variant",
                    "conflict_variant", "readable_variant"):
            with self.assertRaises(ValueError) as caught:
                execute_scenario("bazi-profile",
                                 {"value": self.BIRTH, key: "x"})
            self.assertIn("do not match the reviewed contract",
                          str(caught.exception))

    def test_adjudication_strength_variant_keeps_baseline_refusal(self):
        with self.assertRaises(ValueError) as caught:
            execute_scenario("bazi-profile", {
                "value": self.BIRTH,
                "strength_variant": "bazi-strength-adjudication-v1"})
        self.assertEqual(
            str(caught.exception),
            "Bounded strength adjudication requires explicit research mode")


class FrontendWiringTests(unittest.TestCase):
    """Guarded source pins for the page wiring (E0359 lesson: the
    assembled acceptance tree has no web/ — skip when absent)."""

    def test_page_consumes_presentation_and_narrowed_copy(self):
        page_path = (ROOT / "web" / "visual-prototype" / "src" / "public"
                     / "BaziProfilePage.tsx")
        api_path = (ROOT / "web" / "visual-prototype" / "src" / "public"
                    / "api.ts")
        if not page_path.exists() or not api_path.exists():
            self.skipTest("web tree not present in this checkout")
        page = page_path.read_text(encoding="utf-8")
        api = api_path.read_text(encoding="utf-8")
        self.assertIn("executeBaziProfileScenario", api)
        self.assertIn("executeBaziProfileScenario", page)
        self.assertIn("xiyong_presentation", page)
        # §4.7: line-176 narrowing landed; the old blanket wording
        # (claiming tiaohou is never presented) is gone.
        self.assertNotIn("不自动定格局、调候", page)
        self.assertIn("不自动定格局；调候与病药只呈现已注册依据，"
                      "不作统一喜用结论", page)


if __name__ == "__main__":
    unittest.main()
