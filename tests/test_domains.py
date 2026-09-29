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
