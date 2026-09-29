import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load_json(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def load_jsonl(path):
    rows = []
    for line in (ROOT / path).read_text(encoding="utf-8").splitlines():
        if line.strip():
            rows.append(json.loads(line))
    return rows


class CanonicalIntegrityTests(unittest.TestCase):
    def test_zhouyi_complete(self):
        data = load_json("data/canonical/classics/yijing/zhouyi-64.json")
        items = data["items"]
        self.assertEqual(data["hexagram_count"], 64)
        self.assertEqual(data["line_count"], 384)
        self.assertEqual(len(items), 64)
        self.assertEqual(sum(len(x["lines"]) for x in items), 384)
        self.assertTrue(all(x["judgment"] for x in items))
        self.assertTrue(all(x["great_image"] for x in items))
        self.assertTrue(all(len(x["lines"]) == 6 for x in items))

    def test_yijing_index(self):
        rows = load_jsonl("data/index/yijing-core.jsonl")
        ids = [x["id"] for x in rows]
        self.assertEqual(len(rows), 537)
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(sum(x.get("topic") == "爻辞" for x in rows), 384)
        self.assertEqual(sum(x.get("topic") == "彖传" for x in rows), 64)

    def test_liuyao_classics_index(self):
        rows = load_jsonl("data/index/liuyao-classics.jsonl")
        ids = [x["id"] for x in rows]
        self.assertGreaterEqual(len(rows), 200)
        self.assertEqual(len(ids), len(set(ids)))
        self.assertTrue(all(x["layer"] == "L0" for x in rows))
        self.assertTrue(all(x["source_repo"] == "yaomancy/liuyao-engine" for x in rows))

    def test_bazi_index(self):
        rows = load_jsonl("data/index/bazi-rules.jsonl")
        self.assertGreaterEqual(len(rows), 50)
        self.assertTrue(all(x["domain"] == "bazi" for x in rows))
        self.assertTrue(all(x["license"] == "MIT" for x in rows))

    def test_manifest_is_explicit(self):
        manifest = load_json("config/source_file_manifest.json")["files"]
        keys = [(x["repo"], x["path"]) for x in manifest]
        targets = [x["target"] for x in manifest]
        self.assertEqual(len(keys), len(set(keys)))
        self.assertEqual(len(targets), len(set(targets)))
        for x in manifest:
            self.assertIn("license", x)
            self.assertIn("ingestion", x)
            self.assertTrue(x.get("auto_refresh") in {True, False})


if __name__ == "__main__":
    unittest.main()
