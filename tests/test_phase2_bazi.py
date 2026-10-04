import unittest
from tianji_kb.engine import execute
from tianji_kb.operations.bazi_chart import chart

class BaziPhase2Tests(unittest.TestCase):
    def test_reviewed_structural_chart(self):
        out=chart("庚辰","己丑","甲子","庚午")
        self.assertEqual(out["domain"],"bazi")
        self.assertEqual(out["variant"],"ziping-structural-v1")
        self.assertEqual(out["result"]["day_master"]["stem"],"甲")
        self.assertEqual([x["stem"]["ten_god"] for x in out["result"]["pillars"]],["七杀","正财","日主","七杀"])
        self.assertEqual([x["rule_id"] for x in out["trace"]],["bazi.phase2.pillars","bazi.phase2.ten_gods","bazi.phase2.hidden_stems"])
        self.assertTrue(out["evidence"])
        self.assertTrue(all(v["evidence_level"]=="C" for v in out["evidence"].values()))

    def test_gateway_datetime_adapter_is_deterministic(self):
        payload={"value":"2000-01-07T12:00:00+08:00"}
        first=execute("bazi",payload)
        second=execute("bazi",payload)
        self.assertEqual(first,second)
        self.assertEqual(first["input_calendar"]["calendar_provider"],"lunar-python==1.4.8")
        self.assertEqual(first["result"]["production_scope"],"四柱、日主、十神、藏干结构事实")
        self.assertTrue(first["unresolved"])

    def test_no_interpretive_fields_leak_into_production(self):
        out=chart("庚辰","己丑","甲子","庚午")["result"]
        for key in ("strength","useful_god","pattern","fortune_score","taohua","branch_relations"):
            self.assertNotIn(key,out)

    def test_unknown_variant_rejected(self):
        with self.assertRaises(ValueError):
            chart("庚辰","己丑","甲子","庚午",variant="unknown")

if __name__=="__main__":
    unittest.main()
