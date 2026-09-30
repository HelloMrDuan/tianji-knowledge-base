import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
C = ROOT / "data/canonical"

def load(path):
    return json.loads((C / path).read_text(encoding="utf-8"))

class DomainIntegrityTests(unittest.TestCase):
    def test_ten_wings(self):
        mins = {"xici_shang":2500,"xici_xia":2500,"shuogua":1000,"xugua":1000,"zagua":350}
        for name, minimum in mins.items():
            obj = load(f"yijing/ten_wings/{name}.json")
            text = obj["normalized_text"]
            self.assertGreaterEqual(len(text), minimum)
            self.assertNotIn("□", text)
            self.assertNotIn("�", text)
            self.assertEqual(obj["source_level"], "L0-public-domain-classic")

    def test_ziwei(self):
        z = load("ziwei/iztro_rules_v1.json")
        self.assertEqual(len(z["palaces"]), 12)
        self.assertEqual(len(z["major_stars"]), 14)
        self.assertEqual(len(z["four_transformations"]), 10)
        self.assertTrue(all(len(v)==4 for v in z["four_transformations"].values()))

    def test_qimen(self):
        q = load("qimen/qfdk_maoshan_v1.json")
        self.assertEqual(len(q["nine_palaces"]), 9)
        self.assertEqual(len(q["nine_stars"]), 9)
        self.assertEqual(len(q["eight_doors"]), 8)
        self.assertEqual(len(q["eight_deities"]), 8)
        self.assertEqual(len(q["solar_term_bureaus"]), 24)
        self.assertEqual(q["canonical_terms"]["san_qi"], ["乙","丙","丁"])
        self.assertEqual(q["canonical_terms"]["liu_yi"], ["戊","己","庚","辛","壬","癸"])

    def test_bibliographies(self):
        self.assertGreaterEqual(load("liuren/classics_catalog_v1.json")["record_count"], 120)
        self.assertGreaterEqual(load("taiyi/classics_catalog_v1.json")["record_count"], 90)

    def test_liuren_rules(self):
        x = load("liuren/rules_v1.json")
        self.assertEqual(len(x["month_general_by_solar_terms"]), 12)
        self.assertEqual(x["month_general_by_solar_terms"][0]["branch"], "亥")
        self.assertEqual(x["month_general_by_solar_terms"][-1]["branch"], "子")
        self.assertEqual(len(x["heavenly_generals"]["order"]), 12)
        self.assertEqual(
            x["three_transmissions"]["engine_selection_precedence"],
            ["贼克","比用","涉害","遥克","昴星","别责","八专","伏吟"],
        )
        self.assertEqual(len(x["branch_relations"]["clash"]), 12)
        self.assertEqual(x["branch_relations"]["clash"]["子"], "午")

    def test_taiyi_rules(self):
        x = load("taiyi/rules_v1.json")
        self.assertEqual(len(x["classical_methods"]), 4)
        self.assertEqual(len(x["taiyi_palace"]["yang_72"]), 72)
        self.assertEqual(len(x["taiyi_palace"]["yin_72"]), 72)
        self.assertEqual(set(x["taiyi_palace"]["valid_palace_numbers"]), {1,2,3,4,6,7,8,9})
        self.assertEqual(x["eight_doors"]["base_order"], ["开","休","生","伤","杜","景","死","惊"])
        self.assertEqual(len(x["sixteen_palaces"]), 16)
        self.assertEqual(x["luoshu_outer_order"], [8,3,4,9,2,7,6,1])
        self.assertTrue(all(v != 5 for v in x["taiyi_palace"]["yang_72"]))
        self.assertTrue(all(v != 5 for v in x["taiyi_palace"]["yin_72"]))

    def test_bazi_public_domain_classics(self):
        y = load("classics/bazi/yuanhai_ziping_v1.json")
        q = load("classics/bazi/qiongtong_baojian_v1.json")
        self.assertGreaterEqual(y["section_count"], 180)
        self.assertGreaterEqual(sum(len(x["text"]) for x in y["sections"]), 55000)
        self.assertEqual(y["cleaning"]["replacement_chars"], 0)
        self.assertTrue(any(x["title"] == "论大运" for x in y["sections"]))
        self.assertGreaterEqual(q["section_count"], 95)
        self.assertGreaterEqual(sum(len(x["text"]) for x in q["sections"]), 30000)
        self.assertEqual(q["cleaning"]["replacement_chars"], 0)
        self.assertTrue(any(x["title"] == "五行总论" for x in q["sections"]))
        self.assertTrue(any(x["title"] == "正月丙火" for x in q["sections"]))

    def test_tarot(self):
        t = load("tarot/rws_cn_v1.json")
        self.assertEqual(t["record_count"], 78)
        self.assertEqual(t["spread_count"], 9)
        self.assertEqual(t["counts"]["MajorArcana"], 22)
        self.assertEqual(t["counts"]["Swords"], 14)
        self.assertEqual(t["counts"]["Wands"], 14)
        self.assertEqual(t["counts"]["Cups"], 14)
        self.assertEqual(t["counts"]["Pentacles"], 14)
        self.assertTrue(all("pic" not in card for card in t["cards"]))

    def test_zeri_and_almanac(self):
        z = load("zeri/zeri_core_v1.json")
        a = load("almanac/scoring_v1.json")
        self.assertEqual(len(z["events"]), 10)
        self.assertEqual(len(z["branch_clashes"]), 12)
        self.assertEqual(len(z["sha_direction"]), 12)
        self.assertEqual(len(a["fixed_inauspicious"]["yang_gong_13_avoid"]), 13)
        self.assertEqual(len(a["fixed_inauspicious"]["san_niang_sha_lunar_days"]), 6)
        self.assertEqual(len(a["fixed_inauspicious"]["shi_e_da_bai_jiazi"]), 10)

    def test_fengshui(self):
        f = load("fengshui/calculation_v1.json")
        schools = load("fengshui/schools_v1.json")
        self.assertEqual(len(f["san_yuan_periods"]), 9)
        self.assertEqual(len(f["luoshu"]["palace_numbers"]), 9)
        self.assertEqual(len(f["luoshu"]["flight_path"]), 9)
        self.assertEqual(len(f["ming_gua"]["directions"]), 8)
        self.assertGreaterEqual(len(schools["schools"]), 7)
        self.assertIn("完整玄空宅盘", f["luoshu"]["limitation"])

    def test_fengshui_24_mountains(self):
        m = load("fengshui/twenty_four_mountains_v1.json")
        rows = m["records"]
        self.assertEqual(len(rows), 24)
        self.assertEqual(len({x["mountain"] for x in rows}), 24)
        self.assertEqual(len({x["compass_label"] for x in rows}), 24)
        self.assertEqual(rows[0]["mountain"], "子")
        self.assertEqual(rows[0]["compass_label"], "N2")
        self.assertEqual(rows[0]["start_degrees"], 352.5)
        self.assertEqual(rows[0]["end_degrees"], 7.5)
        self.assertTrue(rows[0]["wraps_zero"])
        self.assertEqual(rows[-1]["mountain"], "壬")
        for x in rows:
            self.assertEqual(x["center_degrees"], (x["index"] * 15) % 360)
            self.assertEqual(x["opposite"]["index"], (x["index"] + 12) % 24)

    def test_public_domain_bazi_classics(self):
        dit = load("classics/bazi/ditiansui_chanwei_v1.json")
        self.assertEqual(dit["section_count"], 63)
        self.assertGreaterEqual(sum(len(x["text"]) for x in dit["sections"]), 120000)
        self.assertEqual(dit["sections"][0]["title"], "通神论·一、天道")
        self.assertEqual(dit["sections"][-1]["title"], "六亲论·二十九、贞元")
        self.assertEqual(dit["cleaning"]["private_use_chars"], 0)
        self.assertFalse((C / "classics/bazi/sanming_tonghui_v1.json").exists())

    def test_sanming_pua_collation_progress(self):
        audit_path = ROOT / "data/quarantine/public_domain_snapshots/daizhigev20/sanming_pua_audit.json"
        map_path = ROOT / "data/quarantine/public_domain_snapshots/daizhigev20/sanming_pua_collation.json"
        audit = json.loads(audit_path.read_text(encoding="utf-8"))
        mapping = json.loads(map_path.read_text(encoding="utf-8"))
        summary = mapping["summary"]
        self.assertEqual(audit["total_private_use_chars"], 524)
        self.assertEqual(audit["unique_private_use_chars"], 86)
        self.assertEqual(summary["confirmed_mappings"], 72)
        self.assertEqual(summary["confirmed_occurrences"], 503)
        self.assertEqual(summary["remaining_unique_codepoints"], 14)
        self.assertEqual(summary["remaining_occurrences"], 21)
        self.assertTrue(all(x["status"] == "confirmed" for x in mapping["mappings"]))
        self.assertIn(("U+E4BF", "琐"), {(x["codepoint"], x["replacement"]) for x in mapping["mappings"]})
        self.assertIn(("U+EA40", "𠒋"), {(x["codepoint"], x["replacement"]) for x in mapping["mappings"]})
        self.assertIn(("U+E749", "渺"), {(x["codepoint"], x["replacement"]) for x in mapping["mappings"]})
        self.assertIn(("U+ECDE", "点"), {(x["codepoint"], x["replacement"]) for x in mapping["mappings"]})
        self.assertIn(("U+ED3F", "眩"), {(x["codepoint"], x["replacement"]) for x in mapping["mappings"]})
        self.assertIn(("U+EA7B", "冢"), {(x["codepoint"], x["replacement"]) for x in mapping["mappings"]})
        self.assertIn(("U+EA85", "刑"), {(x["codepoint"], x["replacement"]) for x in mapping["mappings"]})
        self.assertIn(("U+EB8E", "弦"), {(x["codepoint"], x["replacement"]) for x in mapping["mappings"]})
        self.assertIn(("U+EE60", "蒙"), {(x["codepoint"], x["replacement"]) for x in mapping["mappings"]})
        self.assertIn(("U+EA23", "胤"), {(x["codepoint"], x["replacement"]) for x in mapping["mappings"]})
        self.assertIn(("U+ED92", "算"), {(x["codepoint"], x["replacement"]) for x in mapping["mappings"]})
        self.assertIn(("U+EEA1", "过"), {(x["codepoint"], x["replacement"]) for x in mapping["mappings"]})
        self.assertIn(("U+E898", "瓜"), {(x["codepoint"], x["replacement"]) for x in mapping["mappings"]})
        self.assertIn(("U+EEA6", "蓬"), {(x["codepoint"], x["replacement"]) for x in mapping["mappings"]})
        self.assertIn(("U+EA5B", "传"), {(x["codepoint"], x["replacement"]) for x in mapping["mappings"]})
        self.assertIn(("U+EA62", "备"), {(x["codepoint"], x["replacement"]) for x in mapping["mappings"]})
        self.assertIn(("U+E8AA", "恶"), {(x["codepoint"], x["replacement"]) for x in mapping["mappings"]})
        self.assertIn(("U+EA26", "兮"), {(x["codepoint"], x["replacement"]) for x in mapping["mappings"]})
        self.assertIn(("U+E9C7", "真"), {(x["codepoint"], x["replacement"]) for x in mapping["mappings"]})
        self.assertIn(("U+EAC0", "嗤"), {(x["codepoint"], x["replacement"]) for x in mapping["mappings"]})
        self.assertIn(("U+EAE6", "涂"), {(x["codepoint"], x["replacement"]) for x in mapping["mappings"]})
        self.assertIn(("U+EAF6", "压"), {(x["codepoint"], x["replacement"]) for x in mapping["mappings"]})
        self.assertIn(("U+ECD6", "熬"), {(x["codepoint"], x["replacement"]) for x in mapping["mappings"]})
        self.assertIn(("U+EA7C", "寵"), {(x["codepoint"], x["replacement"]) for x in mapping["mappings"]})
        self.assertIn(("U+EEB8", "𫑗"), {(x["codepoint"], x["replacement"]) for x in mapping["mappings"]})
        self.assertIn(("U+E59C", "燥"), {(x["codepoint"], x["replacement"]) for x in mapping["mappings"]})
        self.assertIn(("U+EBB8", "博"), {(x["codepoint"], x["replacement"]) for x in mapping["mappings"]})
        self.assertIn(("U+EBDE", "哲"), {(x["codepoint"], x["replacement"]) for x in mapping["mappings"]})
        self.assertIn(("U+EDE6", "苑"), {(x["codepoint"], x["replacement"]) for x in mapping["mappings"]})
        self.assertIn(("U+E3E5", "坷"), {(x["codepoint"], x["replacement"]) for x in mapping["mappings"]})
        self.assertIn(("U+ECEC", "管"), {(x["codepoint"], x["replacement"]) for x in mapping["mappings"]})
        self.assertIn(("U+E10C", "𣷉"), {(x["codepoint"], x["replacement"]) for x in mapping["mappings"]})
        self.assertIn(("U+E5AB", "𨽻"), {(x["codepoint"], x["replacement"]) for x in mapping["mappings"]})
        self.assertIn(("U+ED9E", "簪"), {(x["codepoint"], x["replacement"]) for x in mapping["mappings"]})
        self.assertIn(("U+EE26", "亏"), {(x["codepoint"], x["replacement"]) for x in mapping["mappings"]})
        self.assertIn(("U+EE6D", "博"), {(x["codepoint"], x["replacement"]) for x in mapping["mappings"]})
        self.assertIn(("U+EF6A", "惕"), {(x["codepoint"], x["replacement"]) for x in mapping["mappings"]})
        self.assertIn(("U+EF6C", "场"), {(x["codepoint"], x["replacement"]) for x in mapping["mappings"]})
        self.assertIn(("U+EBA5", "忘"), {(x["codepoint"], x["replacement"]) for x in mapping["mappings"]})
        self.assertIn(("U+ECCA", "烽"), {(x["codepoint"], x["replacement"]) for x in mapping["mappings"]})
        self.assertIn(("U+ED51", "瞽"), {(x["codepoint"], x["replacement"]) for x in mapping["mappings"]})
        self.assertIn(("U+EEA3", "递"), {(x["codepoint"], x["replacement"]) for x in mapping["mappings"]})
        self.assertIn(("U+EED7", "开"), {(x["codepoint"], x["replacement"]) for x in mapping["mappings"]})
        self.assertIn(("U+EEE4", "徒"), {(x["codepoint"], x["replacement"]) for x in mapping["mappings"]})
        self.assertIn(("U+EEE5", "隐"), {(x["codepoint"], x["replacement"]) for x in mapping["mappings"]})
        self.assertIn(("U+EF6B", "疡"), {(x["codepoint"], x["replacement"]) for x in mapping["mappings"]})
        self.assertIn(("U+EA7D", "凌"), {(x["codepoint"], x["replacement"]) for x in mapping["mappings"]})
        self.assertIn(("U+EAA7", "段"), {(x["codepoint"], x["replacement"]) for x in mapping["mappings"]})
        self.assertIn(("U+EBC2", "惨"), {(x["codepoint"], x["replacement"]) for x in mapping["mappings"]})
        self.assertIn(("U+ED94", "算"), {(x["codepoint"], x["replacement"]) for x in mapping["mappings"]})
        self.assertIn(("U+EF17", "鬓"), {(x["codepoint"], x["replacement"]) for x in mapping["mappings"]})
        self.assertIn(("U+EF33", "类"), {(x["codepoint"], x["replacement"]) for x in mapping["mappings"]})
        self.assertIn(("U+EF3F", "抟"), {(x["codepoint"], x["replacement"]) for x in mapping["mappings"]})
        self.assertIn(("U+EF67", "参"), {(x["codepoint"], x["replacement"]) for x in mapping["mappings"]})
        singleton = next(x for x in mapping["mappings"] if x["codepoint"] == "U+EA62")
        self.assertEqual(singleton["count"], 1)
        self.assertEqual(len(singleton["source_anchors"]), 1)
        self.assertGreaterEqual(len(singleton["evidence"]), 2)
        self.assertFalse((C / "classics/bazi/sanming_tonghui_v1.json").exists())

    def test_hetu_luoshu(self):
        h = load("foundations/hetu_luoshu_v1.json")
        pairs = h["hetu"]["pairs"]
        self.assertEqual(len(pairs), 5)
        self.assertTrue(all(x["completing"] - x["generating"] == 5 for x in pairs))
        matrix = h["luoshu"]["matrix_south_up"]
        self.assertEqual(matrix, [[4,9,2],[3,5,7],[8,1,6]])
        rows = matrix
        cols = [list(x) for x in zip(*matrix)]
        diags = [[matrix[i][i] for i in range(3)], [matrix[i][2-i] for i in range(3)]]
        self.assertTrue(all(sum(line) == 15 for line in rows + cols + diags))
        self.assertEqual(len(h["luoshu"]["nine_palaces"]), 9)
        self.assertEqual(h["hetu"]["textual_attribution_status"], "UNVERIFIED")

if __name__ == "__main__":
    unittest.main()
