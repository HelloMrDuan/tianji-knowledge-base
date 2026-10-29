"""TJ-018.3 正式应用批 phase 0「PUA 86/86 全核」：公开结构测试。

本批是复核登记批：登记模块 ``bazi_sanming_pua_verification`` 为
纯数据、零函数、不被任何可执行路径 import；本测试只钉登记形制
与复核红线（逐码位字段完备、计数对账聚合、结论分布钉值、
disputed 并列登记形态、设计全核门 54 个零引用码位的销项交叉
核对、见证方与谱系独立性口径、应用批接口声明、零应用口径、
来源普查不变），不验证任何应用产物。密封侧逐码位计数对账
（快照实测、校勘表逐字比对、审计文件字段形态）在密封专项
``tests/test_tj0183_sanming_pua_verification_sealed.py``
（仅离线验收，不进公开 CI）。
"""

from __future__ import annotations

import inspect
import json
import unittest
from pathlib import Path

from tianji_kb import bazi_sanming_formal_application as fa
from tianji_kb import bazi_sanming_pua_verification as pv

ROOT = Path(__file__).resolve().parents[1]
GOLDEN = json.loads(
    (ROOT / "tests" / "golden_tj0183_sanming_pua_verification.json")
    .read_text(encoding="utf-8"))
KS = json.loads(
    (ROOT / "config" / "knowledge_sources.json").read_text(encoding="utf-8"))
REG = pv.PUA_FULL_VERIFICATION_REGISTER
VERDICTS = {e["codepoint"]: e for e in pv.CODEPOINT_VERDICTS}
DISPUTED = {"U+E3E5", "U+E9C7", "U+E87D", "U+EEE4"}


def _mirror():
    return {
        "meta": {
            "register_id": REG["id"],
            "task": REG["task"],
            "kind": REG["kind"],
            "purpose": GOLDEN["meta"]["purpose"],
        },
        "headline": REG["headline"],
        "witness_parties": [p["party_id"] for p in pv.WITNESS_PARTIES],
        "codepoints": [
            {"codepoint": e["codepoint"], "replacement": e["replacement"],
             "registered_count": e["registered_count"],
             "snapshot_count": e["snapshot_count"],
             "attested_loci": e["attested_loci"], "verdict": e["verdict"],
             "attesting_parties": e["attesting_parties"]}
            for e in pv.CODEPOINT_VERDICTS],
        "contextual": [
            {"rule_id": c["rule_id"], "new": c["new"],
             "loci_count": c["loci_count"], "verdict": c["verdict"]}
            for c in pv.CONTEXTUAL_VERDICTS],
        "disputed_codepoints": sorted(
            cp for cp, e in VERDICTS.items() if e["verdict"] == "disputed"),
    }


class TestModulePurity(unittest.TestCase):
    def test_no_functions(self):
        fns = [n for n, _ in inspect.getmembers(pv, inspect.isfunction)]
        self.assertEqual(fns, [])

    def test_not_imported_by_executable_paths(self):
        src = ROOT / "src" / "tianji_kb"
        offenders = []
        for py in src.glob("*.py"):
            if py.name == "bazi_sanming_pua_verification.py":
                continue
            if "bazi_sanming_pua_verification" in py.read_text(encoding="utf-8"):
                offenders.append(py.name)
        self.assertEqual(offenders, [])


class TestGoldenMirror(unittest.TestCase):
    def test_mirror_equals_golden(self):
        self.assertEqual(_mirror(), GOLDEN)


class TestCountsAndCompleteness(unittest.TestCase):
    def test_eighty_five_uniform_plus_contextual_codepoint(self):
        self.assertEqual(len(pv.CODEPOINT_VERDICTS), 85)
        self.assertEqual(len(VERDICTS), 85)
        self.assertEqual(REG["headline"]["codepoints_total"], 86)

    def test_uniform_counts_reconciled_and_sum_519(self):
        total = 0
        for e in pv.CODEPOINT_VERDICTS:
            self.assertTrue(e["count_reconciled"], e["codepoint"])
            self.assertEqual(e["registered_count"], e["snapshot_count"])
            self.assertEqual(
                e["attested_loci"] + len(e["unattested_loci_offsets"]),
                e["snapshot_count"], e["codepoint"])
            total += e["snapshot_count"]
        self.assertEqual(total, 519)

    def test_contextual_rules_five_loci(self):
        self.assertEqual(len(pv.CONTEXTUAL_VERDICTS), 4)
        self.assertEqual(
            [c["loci_count"] for c in pv.CONTEXTUAL_VERDICTS], [1, 2, 1, 1])
        self.assertEqual(
            sum(c["loci_count"] for c in pv.CONTEXTUAL_VERDICTS), 5)
        for c in pv.CONTEXTUAL_VERDICTS:
            self.assertEqual(c["codepoint"], "U+E7E8")
            self.assertIn("\ue7e8", c["old"])
            self.assertNotIn("\ue7e8", c["new"])
            self.assertEqual(c["verdict"], "verified")
        self.assertEqual(REG["headline"]["total_loci"], 524)

    def test_entry_fields_complete(self):
        required = {"codepoint", "replacement", "kind", "registered_count",
                    "snapshot_count", "count_reconciled", "attested_loci",
                    "representative_attested_offsets",
                    "unattested_loci_offsets", "attesting_parties",
                    "attestation_methods", "variant_glyphs",
                    "word_corroborations", "locus_notes", "rival_readings",
                    "verdict", "verification_basis"}
        for e in pv.CODEPOINT_VERDICTS:
            self.assertTrue(required <= set(e), e["codepoint"])
            self.assertEqual(e["kind"], "uniform")
            self.assertEqual(
                len(e["representative_attested_offsets"]),
                min(3, e["attested_loci"]), e["codepoint"])
            self.assertTrue(e["verification_basis"], e["codepoint"])


class TestVerdicts(unittest.TestCase):
    def test_distribution_pinned(self):
        from collections import Counter
        dist = Counter(e["verdict"] for e in pv.CODEPOINT_VERDICTS)
        self.assertEqual(dist, {"verified": 81, "disputed": 4})
        self.assertEqual(REG["headline"]["verified"], 82)
        self.assertEqual(REG["headline"]["disputed"], 4)
        self.assertEqual(REG["headline"]["unverifiable"], 0)
        self.assertTrue(REG["headline"]["gate_passed"])

    def test_disputed_set_exact_and_parallel_registration(self):
        got = {cp for cp, e in VERDICTS.items() if e["verdict"] == "disputed"}
        self.assertEqual(got, DISPUTED)
        for cp in DISPUTED:
            e = VERDICTS[cp]
            self.assertTrue(e["rival_readings"], cp)
            for r in e["rival_readings"]:
                self.assertIn("并列登记", r["disposition"])
                self.assertTrue(r["attested_by"])
                self.assertTrue(r["loci"])
        for cp, e in VERDICTS.items():
            if cp not in DISPUTED:
                self.assertEqual(e["rival_readings"], [], cp)

    def test_disputed_replacements_unchanged(self):
        self.assertEqual(VERDICTS["U+E3E5"]["replacement"], "坷")
        self.assertEqual(VERDICTS["U+E9C7"]["replacement"], "真")
        self.assertEqual(VERDICTS["U+E87D"]["replacement"], "曄")
        self.assertEqual(VERDICTS["U+EEE4"]["replacement"], "徒")

    def test_unattested_loci_offsets_pinned(self):
        gaps = {cp: e["unattested_loci_offsets"]
                for cp, e in VERDICTS.items() if e["unattested_loci_offsets"]}
        self.assertEqual(gaps, {
            "U+E3E5": [264534], "U+E408": [229612], "U+E645": [248455],
            "U+E87D": [280424], "U+E9C7": [46813],
            "U+EA20": [191751, 214758], "U+EB07": [180885, 297469],
            "U+EBB7": [429592]})


class TestDesignGateCoverage(unittest.TestCase):
    def test_zero_citation_codepoints_all_verdicted(self):
        zero = fa.PUA_FULL_VERIFICATION["measured_coverage_now"][
            "zero_citation_codepoints"]
        self.assertEqual(len(zero), 54)
        for cp in zero:
            self.assertIn(cp, VERDICTS, cp)
        cov = pv.DESIGN_GATE_COVERAGE["after_this_batch"]
        self.assertEqual(cov["verdicts_registered"], 86)
        self.assertEqual(cov["zero_citation_codepoints_remaining"], 0)
        zero_disputed = sorted(
            cp for cp in zero if VERDICTS[cp]["verdict"] == "disputed")
        self.assertEqual(zero_disputed,
                         ["U+E3E5", "U+E87D", "U+E9C7", "U+EEE4"])


class TestWitnessesAndMethod(unittest.TestCase):
    def test_witness_parties_pinned(self):
        parties = {p["party_id"]: p for p in pv.WITNESS_PARTIES}
        self.assertEqual(
            set(parties), {"siku_lineage", "niutrans", "youngzs",
                           "banny_corroboration", "registered_anchor"})
        siku = {m["repo"]: m["commit"] for m in parties["siku_lineage"]["members"]}
        self.assertEqual(siku, {
            "kanripo/KR3g0042": "efe780a4f6fd835f4e2d769ffc8f79b7099db3b1",
            "mikkokotila/Sanming-Tongshui": "eb3cacbf4b41a4fe8fc3c0e77e0d12b5bd17c079"})
        self.assertEqual(
            parties["niutrans"]["members"][0]["commit"],
            "4e746ea9fa99c3c0d7051c45397330bef7b0962d")
        self.assertEqual(
            parties["youngzs"]["members"][0]["commit"],
            "aa7bc942602d2d88ef94778a726c0d19a4d286ff")
        self.assertEqual(
            parties["banny_corroboration"]["members"][0]["commit"],
            "5a75273ea615ba2938f608871c0361f749c4f0f9")
        self.assertIn("一个见证方", parties["siku_lineage"]["counts_as"])
        self.assertIn("不单独支撑结论", parties["banny_corroboration"]["counts_as"])
        self.assertIn("ShousenZHANG", parties["siku_lineage"]["independence_note"])

    def test_no_codepoint_verified_on_banny_alone(self):
        for e in pv.CODEPOINT_VERDICTS:
            if e["verdict"] == "verified" and e["attested_loci"]:
                self.assertNotEqual(
                    e["attesting_parties"], ["banny_corroboration"],
                    e["codepoint"])

    def test_variant_glyph_bases_present(self):
        for e in pv.CODEPOINT_VERDICTS:
            for v in e["variant_glyphs"]:
                self.assertTrue(v["basis"], (e["codepoint"], v["glyph"]))
                self.assertTrue(v["witnesses"])
        ea20 = VERDICTS["U+EA20"]["variant_glyphs"]
        self.assertEqual([v["glyph"] for v in ea20], ["𤣥"])
        eb07 = VERDICTS["U+EB07"]["variant_glyphs"]
        self.assertEqual([v["glyph"] for v in eb07], ["𠫵"])
        self.assertEqual(VERDICTS["U+ED92"]["replacement"], "算")
        self.assertEqual(VERDICTS["U+ED94"]["replacement"], "算")
        self.assertEqual(
            [v["glyph"] for v in VERDICTS["U+ED92"]["variant_glyphs"]], ["𮅕"])
        self.assertEqual(
            [v["glyph"] for v in VERDICTS["U+ED94"]["variant_glyphs"]], ["𥮅"])

    def test_locus_notes_for_special_cases(self):
        def kinds(cp):
            return {n["kind"] for n in VERDICTS[cp]["locus_notes"]}
        self.assertIn("textual_variant", kinds("U+EA20"))
        self.assertIn("textual_variant", kinds("U+EA23"))
        self.assertIn("transcription_divergence", kinds("U+E59C"))
        self.assertIn("transcription_divergence", kinds("U+EB07"))
        self.assertIn("matching_artifact_excluded", kinds("U+E3D0"))
        self.assertIn("targeted_verification", kinds("U+EA62"))
        self.assertIn("targeted_verification", kinds("U+EA7B"))
        self.assertIn("targeted_verification", kinds("U+EE6D"))
        self.assertIn("glyph_asset_attestation", kinds("U+EE9C"))
        self.assertIn("registered_anchor", kinds("U+E7E9"))
        eb07 = [n for n in VERDICTS["U+EB07"]["locus_notes"]
                if n["kind"] == "transcription_divergence"][0]
        self.assertEqual(len(eb07["raw_offsets"]), 13)


class TestApplicationImpactAndRedLines(unittest.TestCase):
    def test_application_stage_impact(self):
        imp = REG["application_stage_impact"]
        self.assertIn("登记映射执行全部 86 码位", imp["stage1_execution"])
        self.assertIn("专项标记", imp["disputed_flagging"])
        for cp in DISPUTED:
            self.assertIn(cp, imp["disputed_flagging"])
        self.assertIn("unverifiable 为 0 条", imp["unverifiable_blocking"])

    def test_red_lines(self):
        h = REG["headline"]
        self.assertFalse(h["applied_in_this_batch"])
        self.assertFalse(h["snapshot_modified"])
        self.assertFalse(h["existing_registers_modified"])
        self.assertFalse(h["canonical_ready"])
        self.assertEqual(
            REG["source_snapshot"]["sanming_sha256"],
            "00e2a7db8bb59b259b99938033bb1bb77947e04a15dafc111e62b59378010c86")
        self.assertEqual(
            REG["source_snapshot"]["trusted_manifest_sha256"],
            "e5a590b48d496d846c888551695e45843e90b543fb10f671aa9f229a6c9960a5")

    def test_source_census_unchanged_and_scope_noted(self):
        sources = KS["sources"] if "sources" in KS else KS
        self.assertEqual(len(sources), 101)
        sanming = [s for s in sources
                   if s.get("source_id") == "bazi.source.sanmingtonghui"]
        self.assertEqual(len(sanming), 1)
        self.assertIn("sanming-pua-full-verification-register-v1",
                      sanming[0]["review_scope"])
        self.assertIn("E0296", sanming[0]["review_scope"])


if __name__ == "__main__":
    unittest.main()
