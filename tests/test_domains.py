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

if __name__ == "__main__":
    unittest.main()
