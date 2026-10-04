import unittest
from tianji_kb.knowledge import validate_knowledge
from tianji_kb.resolver import ROOT

class BaziPhase1Tests(unittest.TestCase):
    def test_bazi_entities_are_reviewed_and_isolated(self):
        model=validate_knowledge(ROOT)
        bundle=next(x for x in model["bundles"] if x["domain"]=="bazi")
        self.assertEqual(len(bundle["classics"]),1)
        self.assertGreaterEqual(len(bundle["sections"]),8)
        self.assertEqual(len(bundle["rules"]),3)
        self.assertTrue(all(r["execution_status"]=="partially_structured" for r in bundle["rules"]))
        self.assertTrue(all(ref["source_id"]=="bazi.source.yuanhai" for r in bundle["rules"] for ref in r["source_refs"]))

if __name__=="__main__":unittest.main()
