"""Yuanhai alternate official-branch evidence, without pattern determination."""
import unittest
from tianji_kb.bazi_pattern import PATTERN_VARIANT
from tianji_kb.operations.bazi_chart import chart
from tianji_kb.golden import run_cases

class YuanhaiOfficialBranchTests(unittest.TestCase):
    def _chart(self, *pillars):
        return chart(*pillars, pattern_variant=PATTERN_VARIANT)

    def test_five_independent_fixed_cases(self):
        cases=[c for c in run_cases() if c['id'].startswith('bazi.pattern-yuanhai-')]
        self.assertEqual(len(cases),5)

    def test_complete_unexposed_group_is_structural_only(self):
        out=self._chart('丁巳','己酉','甲寅','乙丑')
        official=out['result']['pattern_candidates']['official']
        branch=official['yuanhai_unexposed_official_branch']
        self.assertEqual(branch['status'],'reviewed_structural_candidate')
        self.assertEqual(branch['full_metal_group'],['巳','酉','丑'])
        self.assertIsNone(branch['determination'])
        self.assertFalse(branch['qualified_for_determination'])
        self.assertEqual(official['qualification']['qualification_status'],'indeterminate')
        self.assertEqual(official['determination']['status'],'unresolved')
        self.assertTrue(any(s['rule_id']=='bazi.phase2.branch_triple_harmonies' for s in out['trace']))
        match=next(m for m in out['rule_matches'] if m['rule_id']=='bazi.phase2.official_pattern_candidates')
        self.assertTrue(any(out['evidence'][k]['section_id']=='bazi.section.s056' for k in match['evidence_ids']))
        for entry in branch['conditions']:
            self.assertTrue(entry['fact_ref'].startswith('#/trace/'))
            val=out
            for token in entry['fact_ref'][2:].split('/'):
                val=val[int(token)] if isinstance(val,list) else val[token]
            self.assertIsNotNone(val)
        self.assertFalse(out['interpretation_contract']['ai_may_explain'])
        self.assertTrue(out['research_only'])

    def test_false_conditions_do_not_determine_any_pattern(self):
        cases=[
            ('丁巳','己酉','甲寅','乙亥'),
            ('辛巳','己酉','甲寅','乙丑'),
            ('丁巳','己丑','甲寅','乙酉'),
            ('丁巳','己酉','乙卯','乙丑')
        ]
        for pillars in cases:
            with self.subTest(pillars=pillars):
                out=self._chart(*pillars)
                official=out['result']['pattern_candidates']['official']
                self.assertEqual(official['yuanhai_unexposed_official_branch']['status'],'not_observed')
                self.assertIsNone(official['determination']['pattern'])
                self.assertFalse(official['qualification']['research_only'] is False)

    def test_default_nonresearch_does_not_gain_extra_evidence(self):
        plain=chart('丁巳','己酉','甲寅','乙丑')
        self.assertNotIn('pattern_candidates',plain['result'])
        self.assertFalse(any(s['rule_id']=='bazi.phase2.branch_triple_harmonies' for s in plain['trace']))

if __name__=='__main__':
    unittest.main()
