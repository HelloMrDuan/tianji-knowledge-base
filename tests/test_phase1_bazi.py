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
            "bazi.classic.sanming_tonghui",
            "bazi.classic.xieji",
            "bazi.classic.ditiansui",
        }.issubset(classic_ids))
        xieji=next(item for item in self.bundle["classics"] if item["id"]=="bazi.classic.xieji")
        self.assertEqual(xieji["body_stage"],"quarantine")
        self.assertGreaterEqual(len(self.bundle["sections"]),21)
        self.assertGreaterEqual(len(self.bundle["rules"]),11)
        self.assertTrue(all(r["execution_status"]=="partially_structured" for r in self.bundle["rules"] if r['id'] not in {'bazi.rule.r012','bazi.rule.r013','bazi.rule.r014','bazi.rule.r015','bazi.rule.r016','bazi.rule.r017','bazi.rule.r018','bazi.rule.r019','bazi.rule.r020','bazi.rule.r021','bazi.rule.r022','bazi.rule.r023','bazi.rule.r024','bazi.rule.r025','bazi.rule.r026'}))
        self.assertTrue(all(r['execution_status']=='executable' for r in self.bundle['rules'] if r['id'] in {'bazi.rule.r013','bazi.rule.r014','bazi.rule.r015','bazi.rule.r016','bazi.rule.r017','bazi.rule.r018','bazi.rule.r019','bazi.rule.r020','bazi.rule.r021','bazi.rule.r022','bazi.rule.r023','bazi.rule.r024','bazi.rule.r025','bazi.rule.r026'}))
        self.assertEqual(
            {ref["source_id"] for r in self.bundle["rules"] for ref in r["source_refs"]},
            {
                "bazi.source.yuanhai",
                "bazi.source.sanming-xianchi-niutrans",
                "bazi.source.xieji-relations",
                "bazi.source.ditiansui-spouse",
            },
        )

    def test_school_conflicts_remain_evidence_bound_and_non_executable(self):
        conflicts={
            item["id"]:item
            for item in self.bundle["concepts"]
            if item.get("kind")=="school_conflict"
        }
        self.assertIn("bazi.concept.conflict_spouse_star_lens",conflicts)
        self.assertIn("bazi.concept.conflict_three_punishments",conflicts)
        spouse=conflicts["bazi.concept.conflict_spouse_star_lens"]
        punishment=conflicts["bazi.concept.conflict_three_punishments"]
        self.assertEqual(spouse["attributes"]["status"],"bounded")
        self.assertEqual(punishment["attributes"]["status"],"unresolved")
        self.assertEqual(
            punishment["attributes"]["executable_policy"],
            "blocked_pending_school_resolution",
        )
        self.assertEqual(
            {ref["source_id"] for ref in punishment["source_refs"]},
            {"bazi.source.yuanhai","bazi.source.ditiansui-spouse"},
        )
        self.assertFalse(any(
            rule["id"].startswith("bazi.rule.") and "punish" in rule["id"]
            for rule in self.bundle["rules"]
        ))

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

    def test_zhiming_boundary_has_real_excerpt_and_cannot_become_strength_algorithm(self):
        from tianji_kb.knowledge import read_json
        section=next(s for s in self.bundle['sections'] if s['id']=='bazi.section.s022')
        corpus=read_json(ROOT/'data/canonical/classics/bazi/ditiansui_chanwei_v1.json')['sections'][3]['text']
        self.assertIn(section['text'],corpus)
        self.assertIn('不论日主之衰旺',section['text'])
        self.assertNotIn('若思按',section['text'])
        self.assertNotIn('新增',section['text'])
        rule=next(r for r in self.bundle['rules'] if r['id']=='bazi.rule.r012')
        self.assertEqual(rule['execution_status'],'descriptive_only')
        self.assertNotIn('provider',rule['operation'])
        contract=read_json(ROOT/'data/canonical/bazi/phase2_execution.json')
        self.assertFalse(any(rule['id'] in r['phase1_rule_refs'] for r in contract['rules']))
        self.assertEqual(rule['source_refs'][0]['section_id'],section['id'])
        term=next(t for t in self.bundle['terms'] if t['id']=='bazi.term.strength_review_boundary')
        self.assertFalse(term['attributes']['algorithm_available'])
        self.assertFalse(term['attributes']['production_interpretation'])

if __name__=="__main__":unittest.main()
