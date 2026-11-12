"""TJ-003.3: public-boundary red-line tests (public CI).

Systematic raw-identifier detection for every public presentation
object and public envelope -- not a one-field patch. The shared check
lives in ``tianji_kb.public_boundary`` (pure stdlib, no sealed data);
this file proves, with real counterexamples, that it catches the
pre-existing leak class and that the current public shapes pass it:

* the real strength builder, fed an internal view whose evidence
  records carry REAL-FORMAT 24-hex ids (production c1 ids, already
  public in the repo's Playwright fixtures), emits a presented object
  with no ``evidence_ids`` / ``source_ids`` at all;
* the shared check flags the old shape (raw 24-hex evidence ids,
  ``renshi.*`` rule ids, ``bazi.source.*`` source ids,
  ``bazi.section.*`` source sections, a 64-hex hash) -- each is a
  real negative control proving the check can fail;
* the shared check passes a clean synthetic envelope modeled on the
  production baseline shape, including the approved xiyong bound
  citations, and proves the xiyong exemption is field-scoped;
* the shipped frontend fixtures and sources carry no raw hash
  (the two presented Playwright fixtures carried the same 107/106
  raw ids until the TJ-003.3 scrub -- this test fails on the old
  fixtures and passes on the scrubbed ones);
* the public HTTP error surface fails closed with structured codes
  (422 / 404 / 503) and no traceback, filesystem path, or sealed
  marker in any body, and admin routes without a token never return
  200. These probes run identically with and without the assembled
  runtime: they exercise only pre-runtime validation and auth
  gates, so they are safe in public CI and in the offline
  acceptance alike. (A valid request's 200 path is covered by the
  sealed companion, which runs the whole-envelope check over a
  real projected envelope.)

The sealed companion ``test_tj0033_public_boundary_sealed.py`` runs
only in the offline acceptance (assembled backend), never in public
CI: it executes a real chart and runs the shared check over the
whole projected envelope. This file must NOT be added to the sealed
list, and the sealed file must NOT be added to validate.yml.
"""

import copy
import json
import re
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

from tianji_kb.api import create_app
from tianji_kb.bazi_strength_public import (
    ADJUDICATION_VARIANT,
    PREDICATES,
    is_valid_public_strength_presentation,
    public_strength_presentation,
)
from tianji_kb.public_boundary import (
    find_public_boundary_violations,
    find_raw_hash_tokens,
)

ROOT = Path(__file__).resolve().parents[1]

# Real-format 24-hex evidence ids from the production c1 envelope
# (already public in the repo's Playwright fixtures). Used ONLY as
# internal-view keys here, to prove the builder never leaks the
# format it is fed.
REAL_IDS = {
    "pillars": "014d74071e5e7b84f6c920fa",
    "principal": "09612a7f3b13c33702e85962",
    "roots": "0c0020008f674c25659d72d8",
    "effects": "1243f3c6b37c20ddab616ff2",
    "gate": "15b2bf0508ba0070ac999867",
}
REAL_SOURCES = {
    "pillars": "bazi.source.ditiansui-spouse",
    "principal": "bazi.source.ditiansui-spouse",
    "roots": "bazi.source.xieji-relations",
    "effects": "bazi.source.yuanhai",
    "gate": "bazi.source.yuanhai",
}
HASH_64 = "a" * 64

# No traceback, filesystem path, sealed marker, or code frame may
# appear in any public error body.
LEAK_MARKERS = (
    "Traceback", "/home/", "/data/", ".py", "tianji-private",
    'File "', "canonical_path", "sealed",
)


def _real_format_view():
    """Synthetic commanding (丙×午) view, evidence keyed by real-format ids.

    SYNTHETIC: no calendar, no sealed bundle, no real chart -- the
    same shape as the public strength test's synthetic view, except
    the evidence records are keyed by real-format 24-hex ids (the
    production format) so the test proves the builder does not leak
    the format it consumes.
    """
    evidence = {}
    trace = []
    matches = []

    def add_step(rule_id, output, key):
        evidence_id = REAL_IDS[key]
        evidence[evidence_id] = {
            "source_id": REAL_SOURCES[key], "section_id": "s",
            "chapter_id": "c", "chapter_title": "t",
            "original_text": "fact", "rule_id": rule_id}
        trace.append({"rule_id": rule_id, "evidence_scope": "registered",
                      "inputs": {}, "output": output,
                      "evidence_ids": [evidence_id]})
        matches.append({"rule_id": rule_id, "matched": True,
                        "kind": "executed_calculation",
                        "evidence_scope": "registered",
                        "evidence_ids": [evidence_id]})
        return evidence_id

    add_step("bazi.phase2.pillars", {
        "ganzhi": [["甲", "子"], ["乙", "午"], ["丙", "子"], ["丙", "子"]],
        "day_master": {"stem": "丙", "branch": "子"}}, "pillars")
    add_step("bazi.phase2.principal_month", {
        "day_master": "丙", "month_branch": "午",
        "relation": "same_element", "status": "reviewed_relation",
        "principal_qi": "synthetic"}, "principal")
    add_step("bazi.phase2.root_availability", {
        "root_presence": True, "roots": []}, "roots")
    scope_key = "commanding_visible_support_scope_conditions"
    scope_conditions = {"visible_a": True, "visible_b": True}
    effects_id = add_step("bazi.phase2.action_effects", {
        scope_key: scope_conditions,
        "commanding_visible_support_scope_met": True}, "effects")
    source_ids = sorted({REAL_SOURCES[key] for key in REAL_IDS})
    assessment = {
        "classification": "strong",
        "variant": ADJUDICATION_VARIANT,
        "decision_status": "reviewed_sufficient_rule_matched",
        "matched_rule_ids": [step["rule_id"] for step in trace],
        "fact_refs": ["#/trace/%d/output" % i for i in range(len(trace))],
        "evidence_ids": [REAL_IDS[key] for key in
                         ("pillars", "principal", "roots", "effects")],
        "source_ids": source_ids,
        "conflict_checks": [],
        "conflict_ids": [],
        "blockers": [],
        "unresolved_evidence": [],
        "why_not_indeterminate": {
            "conditions": [
                {"condition": name, "met": True,
                 "fact_ref": "#/trace/3/output/%s/%s" % (scope_key, name),
                 "rule_id": "bazi.phase2.action_effects",
                 "evidence_ids": [effects_id]}
                for name in scope_conditions],
            "all_required_conditions_verified": True,
            "excluded_dependencies": ["dated_commander",
                                      "independent_hidden_effect_scores"],
            "sufficient_rule":
                PREDICATES["commanding_visible_support"][4],
        },
        "supported_classifications": ["strong", "weak", "indeterminate"],
        "variant_dependencies": {
            "dated_commander": False, "principal_qi": True,
            "root_availability": True, "bounded_visible_effects": True,
            "independent_hidden_effect_scores": False},
        "maturity": "PARTIAL", "research_only": True,
        "public_enabled": False, "ai_enabled": False,
        "weights_available": False, "source_case_lookup_used": False,
        "full_strength_classifier_ready": False,
        "limitations": [],
    }
    gate_id = add_step(
        "bazi.phase2.strength_bounded_adjudication", assessment, "gate")
    assessment["matched_rule_ids"].append(
        "bazi.phase2.strength_bounded_adjudication")
    assessment["evidence_ids"].append(gate_id)
    return assessment, {"trace": trace, "rule_matches": matches,
                        "evidence": evidence}


def _old_shape_strength():
    """The pre-fix production presented shape (c1): raw ids included."""
    assessment, view = _real_format_view()
    result = public_strength_presentation(assessment, view)
    forged = copy.deepcopy(result)
    forged["evidence_ids"] = sorted(REAL_IDS.values())
    forged["source_ids"] = sorted(set(REAL_SOURCES.values()))
    return forged


def _clean_envelope():
    """Synthetic projected envelope in the production baseline shape.

    Every identifier-carrying field below is copied from the real
    production baseline envelope (baseline4-c1): the xiyong bound
    citations (with ``consumed_rule_ids`` / ``fact_refs`` -- the
    adjudicated registry ids the check deliberately does NOT flag),
    the pattern not-judgeable shape, the E-aliased rule matches.
    The strength object is built by the real builder (see
    ``_real_format_view``). Scan fixture only: the xiyong /
    strength / pattern shapes themselves are pinned in their own
    test files; this envelope proves the shared check accepts the
    approved shapes together.
    """
    assessment, view = _real_format_view()
    strength = public_strength_presentation(assessment, view)
    return {
        "scenario_id": "bazi-profile",
        "status": "ok",
        "result": {
            "xiyong_presentation": {
                "variant": "xiyong-public-presentation-v1",
                "presentation_scope": "tiaohou_bingyao_only",
                "day_master": "丙", "month_branch": "午",
                "scope_statement": "本呈现只含调候（《穷通宝鉴》）与病药"
                    "（《神峰通考》）两类已注册取用依据，逐条可回溯到注册"
                    "证据与本次执行记录；两类依据并列呈现、互不合并，系统"
                    "不据此给出统一的取用结论；扶抑、格局用神等其他取用"
                    "判断尚未建成，不在本呈现内，暂不可判。",
                "limitations": [
                    "证据等级为 C 级：所据《穷通宝鉴》《神峰通考》均为"
                    "单一电子谱系、简体转写，未做多底本校勘。",
                    "调候条目的未编码分支与关联条目不在注册范围内，"
                    "不呈现；本呈现只含条目主序列与已编码分支。",
                    "病药两对均为结构候选，去病效力未裁定；某一对未"
                    "触发不等于无病。",
                    "本呈现为传统文化观察，不构成对现实的预测。",
                ],
                "unified_verdict": None,
                "public_enabled": False,
                "ai_enabled": False,
                "relations": [],
                "relations_closing_line": "各体系陈述并列呈现，系统不作统一裁定。",
                "blocks": {
                    "tiaohou": {
                        "system": "tiaohou",
                        "source_label": "《穷通宝鉴》",
                        "day_master": "丙", "month_branch": "午",
                        "state": "presented",
                        "month_label": "五月",
                        "sequence": ["壬", "庚"],
                        "branches": [],
                        "entry_basis": "条目主序列",
                        "lines": ["调候体系呈现（合成夹具行，非引文）。"],
                        "evidence": {
                            "source_id": "bazi.source.qiongtong",
                            "evidence_level": "C",
                            "phase1_rule_id": "bazi.rule.r044",
                            "phase2_step_id":
                                "bazi.phase2.tiaohou_assessment",
                            "section_id": "bazi.section.s102",
                            "quote": "五月丙火愈炎,得壬庚高透,方为上命。",
                            "quote_locator": {"line": 38,
                                            "char_start": 7351,
                                            "char_end": 7367},
                            "consumed_rule_ids": [
                                "bazi.phase2.pillars",
                                "bazi.phase2.ten_gods",
                                "bazi.phase2.hidden_stems"],
                            "fact_refs": {
                                "pillars": "#/trace/0/output",
                                "ten_gods": "#/trace/1/output",
                                "hidden_stems": "#/trace/2/output"},
                        },
                    },
                    "bingyao": {
                        "system": "bingyao",
                        "source_label": "《神峰通考》",
                        "day_master": "丙", "month_branch": "午",
                        "state": "presented",
                        "pairs": [],
                        "lines": ["病药体系呈现（合成夹具行，非引文）。"],
                        "evidence": {
                            "source_id": "bazi.source.shenfeng",
                            "evidence_level": "C",
                            "phase1_rule_id": "bazi.rule.r040",
                            "phase2_step_id":
                                "bazi.phase2.bingyao_assessment",
                            "section_ids": ["bazi.section.s071"],
                            "quotes": [
                                {"pair_id": "wealth_peer_officer",
                                 "quote": "如用财见比肩为病,喜见官杀为药也",
                                 "quote_locator": {"line": 38,
                                                 "char_start": 7351,
                                                 "char_end": 7367},
                                 "section_id": "bazi.section.s071"},
                            ],
                            "consumed_rule_ids": [
                                "bazi.phase2.pillars",
                                "bazi.phase2.ten_gods"],
                            "fact_refs": {
                                "pillars": "#/trace/0/output"},
                        },
                    },
                },
            },
            "strength_presentation": strength,
            "pattern_presentation": {
                "variant": "bazi-pattern-public-presentation-v1",
                "status": "not_judgeable",
                "day_master": "丙", "month_branch": "午",
                "reason": "month_not_yin",
                "title": "任氏寅月局部真格研究结果",
                "scope_statement": "本呈现仅陈述任氏分支寅月局部真格研究"
                    "结果：司令之神透于年/月/时干（日干不计）则真格成立，"
                    "司令不透则无真格；不是全盘格局判断，不构成八格真假"
                    "判断体系，不意味着喜用神或吉凶；未呈现不等于假格。",
                "limitations": [
                    "仅限任氏分支寅月试点；其余月份与流派暂不可判。",
                    "不输出假格、破格、成败、清浊、用神或吉凶。",
                    "公开呈现的格名仅限正官、七杀、正财、偏财、正印、偏印、"
                    "食神、伤官八格；其余格名暂不公开呈现。",
                    "司令段以已审试点为准；试点不确定时暂不可判。",
                ],
            },
        },
        "evidence": {
            "E01": {"classic_title": "《穷通宝鉴》",
                    "original_text": "五月丙火愈炎,得壬庚高透,方为上命。",
                    "evidence_level": "C",
                    "classic_title_excerpt": False,
                    "original_text_excerpt": False},
        },
        "rule_matches": [
            {"rule_id": "R01", "matched": True,
             "kind": "executed_calculation",
             "evidence_scope": "registered",
             "evidence_ids": ["E01"]},
        ],
        "trace": [{"step": "计算步骤 01"}],
    }


class StrengthBuilderBoundaryTests(unittest.TestCase):
    def test_real_format_internal_ids_never_reach_the_public_object(self):
        assessment, view = _real_format_view()
        result = public_strength_presentation(assessment, view)
        self.assertTrue(
            is_valid_public_strength_presentation(result))
        self.assertEqual(result["status"], "presented")
        self.assertEqual(result["predicate_id"],
                         "commanding_visible_support")
        self.assertNotIn("evidence_ids", result)
        self.assertNotIn("source_ids", result)
        self.assertEqual(len(result), 13)
        self.assertEqual(find_public_boundary_violations(result), [])

    def test_forged_real_format_evidence_id_still_fails_closed(self):
        # The internal binding is unchanged: an assessment naming
        # an evidence id with no bound record is a forgery, even
        # when the id is real-format.
        assessment, view = _real_format_view()
        assessment["evidence_ids"] = assessment["evidence_ids"] + \
            ["f" * 24]
        with self.assertRaises(ValueError):
            public_strength_presentation(assessment, view)


class SharedCheckNegativeControlTests(unittest.TestCase):
    def test_old_shape_strength_is_flagged(self):
        violations = find_public_boundary_violations(_old_shape_strength())
        self.assertTrue(violations, "check must flag the old shape")
        self.assertTrue(any("014d74071e5e7b84f6c920fa" in v
                            for v in violations))
        self.assertTrue(any("bazi.source.ditiansui-spouse" in v
                            for v in violations))

    def test_renshi_rule_id_is_flagged(self):
        envelope = _clean_envelope()
        envelope["result"]["pattern_presentation"]["rule_ids"] = [
            "renshi.pattern.yin_true"]
        violations = find_public_boundary_violations(envelope)
        self.assertTrue(any("renshi.pattern.yin_true" in v
                            for v in violations))

    def test_bazi_section_source_section_is_flagged(self):
        envelope = _clean_envelope()
        envelope["result"]["pattern_presentation"]["source_sections"] = [
            "bazi.section.s102"]
        violations = find_public_boundary_violations(envelope)
        self.assertTrue(any("bazi.section.s102" in v
                            for v in violations))

    def test_64_hex_hash_is_flagged_anywhere(self):
        envelope = _clean_envelope()
        envelope["trace"][0]["step"] = HASH_64
        violations = find_public_boundary_violations(envelope)
        self.assertTrue(any(HASH_64 in v for v in violations))

    def test_non_alias_rule_id_in_evidence_field_is_flagged(self):
        envelope = _clean_envelope()
        envelope["rule_matches"][0]["evidence_ids"] = [
            "bazi.rule.r030"]
        violations = find_public_boundary_violations(envelope)
        self.assertTrue(any("bazi.rule.r030" in v for v in violations))

    def test_xiyong_exemption_is_field_scoped_not_subtree_scoped(self):
        # A raw source id inside a xiyong prose line is still a
        # violation: only the bound-citation fields are exempt.
        envelope = _clean_envelope()
        envelope["result"]["xiyong_presentation"]["blocks"]["tiaohou"][
            "lines"] = ["见 bazi.source.qiongtong 原文。"]
        violations = find_public_boundary_violations(envelope)
        self.assertTrue(any("bazi.source.qiongtong" in v
                            for v in violations))


class CleanEnvelopeTests(unittest.TestCase):
    def test_approved_shapes_pass_together(self):
        self.assertEqual(
            find_public_boundary_violations(_clean_envelope()), [])


class ShippedFrontendTests(unittest.TestCase):
    def test_strength_fixtures_carry_no_raw_identifiers(self):
        fixtures = ROOT / "web" / "visual-prototype" / "tests" / "fixtures"
        names = (
            "tj0133-strength-presented-strong-scenario.json",
            "tj0133-strength-presented-weak-scenario.json",
            "tj0133-strength-conflict-scenario.json",
            "tj0133-strength-not-judgeable-scenario.json",
        )
        for name in names:
            with self.subTest(fixture=name):
                envelope = json.loads(
                    (fixtures / name).read_text(encoding="utf-8"))
                self.assertEqual(
                    find_public_boundary_violations(envelope), [],
                    name)

    def test_shipped_frontend_sources_carry_no_raw_hash(self):
        # Scans what ships to users (src + Playwright fixtures).
        # tests/ (python) is excluded by design: it holds this
        # file's own negative controls in real 24-hex format.
        roots = (
            ROOT / "web" / "visual-prototype" / "src",
            ROOT / "web" / "visual-prototype" / "tests" / "fixtures",
        )
        suffixes = (".ts", ".tsx", ".js", ".json", ".html", ".css")
        hits = []
        for root in roots:
            for path in root.rglob("*"):
                if not path.is_file() or path.suffix not in suffixes:
                    continue
                tokens = find_raw_hash_tokens(
                    path.read_text(encoding="utf-8", errors="ignore"))
                if tokens:
                    hits.append("%s: %s" % (path.name, tokens[:3]))
        self.assertEqual(hits, [], "raw hashes in shipped frontend")


class HttpErrorHygieneTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = cls.enterClassContext(
            TestClient(create_app(), raise_server_exceptions=False))

    def _assert_fail_closed(self, response, ok_statuses):
        self.assertIn(response.status_code, ok_statuses,
                      response.text)
        self.assertNotEqual(response.status_code, 200)
        for marker in LEAK_MARKERS:
            self.assertNotIn(marker, response.text,
                             "leak marker %r in %s" % (
                                 marker, response.request.url.path))

    def test_missing_field_is_structured_422(self):
        response = self.client.post(
            "/api/v1/public/execute", json={"domain": "bazi"})
        self._assert_fail_closed(response, (422,))
        self.assertEqual(response.json()["detail"][0]["type"], "missing")

    def test_malformed_json_is_structured_422(self):
        response = self.client.post(
            "/api/v1/public/execute", content="not-json",
            headers={"Content-Type": "application/json"})
        self._assert_fail_closed(response, (422,))
        self.assertEqual(response.json()["detail"][0]["type"],
                         "json_invalid")

    def test_research_mode_is_refused_422(self):
        response = self.client.post(
            "/api/v1/public/execute",
            json={"domain": "bazi",
                  "input": {"value": "2000-01-07T12:00:00+08:00"},
                  "mode": "research"})
        self._assert_fail_closed(response, (422,))
        self.assertEqual(response.json()["detail"]["code"],
                         "unsupported_public_execution")

    def test_unknown_scenario_is_refused_422(self):
        response = self.client.post(
            "/api/v1/scenarios/public",
            json={"scenario_id": "nope", "input": {}})
        self._assert_fail_closed(response, (422,))
        self.assertEqual(response.json()["detail"]["code"],
                         "unsupported_public_scenario")

    def test_unknown_route_is_structured_404(self):
        response = self.client.get("/nonexistent-route")
        self._assert_fail_closed(response, (404,))

    def test_admin_governance_without_token_never_200(self):
        response = self.client.get("/api/v1/admin/governance/rules")
        # Unconfigured auth fails closed (503) or rejects (401/403);
        # an unauthenticated admin read is never a 200.
        self._assert_fail_closed(response, (401, 403, 503))

    def test_admin_drafts_without_token_never_200(self):
        response = self.client.get("/api/v1/admin/drafts")
        self._assert_fail_closed(response, (401, 403, 503))


if __name__ == "__main__":
    unittest.main()
