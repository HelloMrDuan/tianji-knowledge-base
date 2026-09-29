import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class SeedTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.seed = json.loads((ROOT / "data/canonical/seed.json").read_text(encoding="utf-8"))

    def test_foundations(self):
        self.assertEqual(len(self.seed["wuxing"]), 5)
        self.assertEqual(len(self.seed["heavenly_stems"]), 10)
        self.assertEqual(len(self.seed["earthly_branches"]), 12)
        self.assertEqual(len(self.seed["trigrams"]), 8)

    def test_hexagrams(self):
        hs = self.seed["hexagrams"]
        self.assertEqual(len(hs), 64)
        self.assertEqual({h[0] for h in hs}, set(range(1, 65)))
        self.assertEqual(hs[0][2], "乾为天")
        self.assertEqual(hs[-1][2], "火水未济")

    def test_najia(self):
        n = self.seed["liuyao"]["najia"]
        self.assertEqual(len(n), 8)
        self.assertEqual(n["乾"], ["甲子","甲寅","甲辰","壬午","壬申","壬戌"])


if __name__ == "__main__":
    unittest.main()
