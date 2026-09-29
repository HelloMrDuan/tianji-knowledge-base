import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CANONICAL = ROOT / "data/canonical"


class KnowledgeBaseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.seed = json.loads((CANONICAL / "seed.json").read_text(encoding="utf-8"))
        cls.zhouyi = json.loads((CANONICAL / "yijing/zhouyi_classic_core.json").read_text(encoding="utf-8"))
        cls.liuyao = json.loads((CANONICAL / "liuyao/najia_v1.json").read_text(encoding="utf-8"))

    def test_foundations(self):
        self.assertEqual(len(self.seed["wuxing"]), 5)
        self.assertEqual(len(self.seed["heavenly_stems"]), 10)
        self.assertEqual(len(self.seed["earthly_branches"]), 12)
        self.assertEqual(len(self.seed["trigrams"]), 8)

    def test_zhouyi_classic_corpus(self):
        records = self.zhouyi["records"]
        self.assertEqual(len(records), 64)
        self.assertEqual({x["number"] for x in records}, set(range(1, 65)))
        self.assertEqual(sum(len(x["lines"]) for x in records), 384)
        self.assertEqual(records[0]["full_name"], "乾为天")
        self.assertEqual(records[-1]["full_name"], "火水未济")
        self.assertTrue(all(x["judgment"] for x in records))
        self.assertTrue(all(x["image"] for x in records))

    def test_najia(self):
        n = self.liuyao["najia"]
        self.assertEqual(len(n), 8)
        self.assertEqual(n["乾"], ["甲子","甲寅","甲辰","壬午","壬申","壬戌"])


if __name__ == "__main__":
    unittest.main()
