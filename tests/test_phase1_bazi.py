import unittest
from tianji_kb.knowledge import validate_knowledge
from tianji_kb.resolver import ROOT

class BaziPhase1Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.model=validate_knowledge(ROOT)
        cls.bundle=next(x for x in cls.model["bundles"] if x["domain"]=="bazi")

    def test_bazi_entities_are_reviewed_and_isolated(self):
        classic_ids={item["id"] for item in self.bundle["classics"]}
        self.assertTrue({
            "bazi.classic.yuanhai",
            "bazi.classic.sanming-xianchi",
            "bazi.classic.xieji",
        }.issubset(classic_ids))
        xieji=next(item for item in self.bundle["classics"] if item["id"]=="bazi.classic.xieji")
        self.assertEqual(xieji["body_stage"],"quarantine")
        self.assertGreaterEqual(len(self.bundle["sections"]),13)
        self.assertGreaterEqual(len(self.bundle["rules"]),8)
        self.assertTrue(all(r["execution_status"]=="partially_structured" for r in self.bundle["rules"]))
        self.assertEqual(
            {ref["source_id"] for r in self.bundle["rules"] for ref in r["source_refs"]},
            {
                "bazi.source.yuanhai",
                "bazi.source.sanming-xianchi-niutrans",
                "bazi.source.xieji-relations",
            },
        )

    def test_xianchi_table_is_reviewed_but_not_promoted_to_fortune_logic(self):
        rule=next(r for r in self.bundle["rules"] if r["id"]=="bazi.rule.r004")
        self.assertEqual(rule["variant"],"ziping-xianchi-table-v0")
        self.assertEqual(rule["execution_status"],"partially_structured")
        self.assertEqual(
            rule["result"]["target_branch"],
            "寅午戌→卯；巳酉丑→午；申子辰→酉；亥卯未→子",
        )
        self.assertTrue(any("基准" in item for item in rule["exceptions"]))
        self.assertTrue(any("纳音" in item for item in rule["exceptions"]))
        section=next(s for s in self.bundle["sections"] if s["id"]=="bazi.section.s009")
        self.assertIn("已酉丑午",section["text"])
        self.assertNotIn("巳酉丑午",section["text"])
        term=next(t for t in self.bundle["terms"] if t["id"]=="bazi.term.xianchi")
        self.assertFalse(term["attributes"]["production_interpretation"])

if __name__=="__main__":unittest.main()
