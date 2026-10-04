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

    def test_explicit_xianchi_lookup_is_evidence_bound_and_non_interpretive(self):
        out=chart("甲寅","甲子","甲申","乙卯",include_xianchi=True)
        lookup=out["result"]["xianchi_lookup"]
        self.assertEqual(lookup["targets"],{"year_branch":"卯","day_branch":"酉"})
        self.assertEqual(lookup["matches"],[{"basis":"year_branch","target_branch":"卯","pillar":"hour"}])
        step=next(x for x in out["trace"] if x["rule_id"]=="bazi.phase2.xianchi_lookup")
        self.assertTrue(step["evidence_ids"])
        self.assertIn("分别",out["result"]["production_scope"])
        serialized=str(out["result"])
        for forbidden in ("romance_score","marriage_score","auspicious","fortune_score"):
            self.assertNotIn(forbidden,serialized)

    def test_xianchi_is_opt_in_and_boolean_only(self):
        plain=chart("甲寅","甲子","甲申","乙卯")
        self.assertNotIn("xianchi_lookup",plain["result"])
        with self.assertRaises(ValueError):
            chart("甲寅","甲子","甲申","乙卯",include_xianchi="yes")

    def test_reviewed_relations_are_opt_in_evidence_bound_and_non_interpretive(self):
        out=chart("甲子","己丑","丙寅","辛巳",include_relations=True)
        relations=out["result"]["reviewed_relations"]
        self.assertEqual(relations["stem_five_combinations"],[
            {"pillars":["year","month"],"stems":["甲","己"],"traditional_result_element":"土"},
            {"pillars":["day","hour"],"stems":["丙","辛"],"traditional_result_element":"水"},
        ])
        self.assertEqual(relations["branch_six_harmonies"],[
            {"pillars":["year","month"],"branches":["子","丑"],"traditional_result_element":"土"},
        ])
        self.assertEqual(relations["branch_six_harms"],[
            {"pillars":["day","hour"],"branches":["寅","巳"]},
        ])
        self.assertEqual(relations["branch_six_clashes"],[])
        self.assertEqual(relations["branch_triple_harmonies"],[])
        self.assertEqual(relations["spouse_palace"],{
            "pillar":"day","day_branch":"寅","label":"日支（传统配偶宫结构位）",
        })
        relation_steps=[x for x in out["trace"] if x["rule_id"] in {
            "bazi.phase2.stem_five_combinations",
            "bazi.phase2.branch_six_harmonies",
            "bazi.phase2.branch_six_harms",
            "bazi.phase2.branch_six_clashes",
            "bazi.phase2.branch_triple_harmonies",
            "bazi.phase2.spouse_palace_day_branch",
        }]
        self.assertEqual(len(relation_steps),6)
        self.assertTrue(all(x["evidence_ids"] for x in relation_steps))
        self.assertTrue(all(v["evidence_level"]=="C" for v in out["evidence"].values()))
        serialized=str(relations)
        for forbidden in ("compatibility_score","marriage_score","auspicious","breakup_risk"):
            self.assertNotIn(forbidden,serialized)

    def test_clash_and_triple_harmony_are_reviewed_structural_facts(self):
        out=chart("庚申","戊子","壬辰","庚午",include_relations=True)
        relations=out["result"]["reviewed_relations"]
        self.assertEqual(relations["branch_six_clashes"],[
            {"pillars":["month","hour"],"branches":["子","午"]},
        ])
        self.assertEqual(relations["branch_triple_harmonies"],[
            {
                "pillars":["year","month","day"],
                "branches":["申","子","辰"],
                "traditional_result_element":"水",
            },
        ])
        clash_step=next(x for x in out["trace"] if x["rule_id"]=="bazi.phase2.branch_six_clashes")
        triple_step=next(x for x in out["trace"] if x["rule_id"]=="bazi.phase2.branch_triple_harmonies")
        self.assertTrue(clash_step["evidence_ids"])
        self.assertTrue(triple_step["evidence_ids"])
        serialized=str(relations)
        for forbidden in ("conflict_score","auspicious","relationship_advice","breakup_risk"):
            self.assertNotIn(forbidden,serialized)

    def test_traditional_spouse_star_lens_requires_explicit_role_and_is_evidence_bound(self):
        male=chart("己丑","戊辰","甲子","庚申",traditional_role="male")
        lens=male["result"]["traditional_spouse_star_lens"]
        self.assertEqual(lens["candidate_ten_gods"],["正财","偏财"])
        self.assertEqual(lens["visible_positions"],[
            {"pillar":"year","stem":"己","ten_god":"正财"},
            {"pillar":"month","stem":"戊","ten_god":"偏财"},
        ])
        self.assertEqual(lens["hidden_positions"],[
            {"pillar":"year","branch":"丑","stem":"己","ten_god":"正财"},
            {"pillar":"month","branch":"辰","stem":"戊","ten_god":"偏财"},
            {"pillar":"hour","branch":"申","stem":"戊","ten_god":"偏财"},
        ])
        step=next(x for x in male["trace"] if x["rule_id"]=="bazi.phase2.spouse_star_lens")
        self.assertTrue(step["evidence_ids"])
        self.assertFalse(lens["interpretation_allowed"])
        self.assertTrue(all(v["evidence_level"]=="C" for v in male["evidence"].values()))

        female=chart("己丑","戊辰","甲子","庚申",traditional_role="female")
        self.assertEqual(female["result"]["traditional_spouse_star_lens"]["candidate_ten_gods"],["正官","七杀"])
        self.assertEqual(female["result"]["traditional_spouse_star_lens"]["visible_positions"],[
            {"pillar":"hour","stem":"庚","ten_god":"七杀"},
        ])
        self.assertEqual(female["result"]["traditional_spouse_star_lens"]["hidden_positions"],[
            {"pillar":"year","branch":"丑","stem":"辛","ten_god":"正官"},
            {"pillar":"hour","branch":"申","stem":"庚","ten_god":"七杀"},
        ])

    def test_traditional_spouse_star_lens_is_opt_in_and_role_is_strict(self):
        plain=chart("己丑","戊辰","甲子","庚申")
        self.assertNotIn("traditional_spouse_star_lens",plain["result"])
        with self.assertRaises(ValueError):
            chart("己丑","戊辰","甲子","庚申",traditional_role="unknown")

    def test_relations_are_opt_in_and_boolean_only(self):
        plain=chart("甲子","己丑","丙寅","辛巳")
        self.assertNotIn("reviewed_relations",plain["result"])
        with self.assertRaises(ValueError):
            chart("甲子","己丑","丙寅","辛巳",include_relations="yes")

    def test_unknown_variant_rejected(self):
        with self.assertRaises(ValueError):
            chart("庚辰","己丑","甲子","庚午",variant="unknown")

if __name__=="__main__":
    unittest.main()
