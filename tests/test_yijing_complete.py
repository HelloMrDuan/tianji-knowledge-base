import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "data/canonical/yijing"

def load(name):
    return json.loads((ROOT / name).read_text(encoding="utf-8"))

class CompleteYijingTests(unittest.TestCase):
    def test_classic_core_special_uses(self):
        core = load("zhouyi_classic_core.json")
        self.assertEqual(sum(len(x["lines"]) for x in core["records"]), 384)
        special = {x["special_use"]["position"] for x in core["records"] if x.get("special_use")}
        self.assertEqual(special, {"用九", "用六"})
        self.assertEqual(core["classic_statement_count"], 386)

    def test_tuan_xiang_wenyan(self):
        corpus = load("tuan_xiang_wenyan_v1.json")
        self.assertEqual(len(corpus["records"]), 64)
        self.assertEqual(sum(len(x["line_images"]) for x in corpus["records"]), 386)
        self.assertEqual({x["number"] for x in corpus["records"] if x["wenyan"]}, {1, 2})
        self.assertTrue(all(x["tuan"] and x["great_image"] for x in corpus["records"]))

    def test_relation_graph(self):
        graph = load("hexagram_relations_v1.json")
        self.assertEqual(len(graph["records"]), 64)
        qian = next(x for x in graph["records"] if x["number"] == 1)
        self.assertEqual(qian["opposite"]["number"], 2)
        self.assertEqual(qian["line_changes"][0]["target"]["number"], 44)
        self.assertTrue(all(len(x["line_changes"]) == 6 for x in graph["records"]))

if __name__ == "__main__":
    unittest.main()
