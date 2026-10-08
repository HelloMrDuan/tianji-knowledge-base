"""Reviewed Yuanhai official/hour seven-killing restriction remains bounded."""
import unittest
from tianji_kb.bazi_pattern import PATTERN_VARIANT
from tianji_kb.operations.bazi_chart import chart
from tianji_kb.golden import run_cases

class YuanhaiHourRestrictionTests(unittest.TestCase):
    def test_seven_fixed_positive_negative_cases(self):
        rows=[r for r in run_cases(domain='bazi')
              if r['id'].startswith('bazi.pattern-hour-killing-')]
        self.assertEqual(len(rows),7)

    def test_hour_stem_and_branch_are_not_conflated(self):
        checks=[
            (('戊午','辛酉','甲午','庚午'),True,1,0),
            (('戊午','辛酉','甲午','壬申'),True,0,1),
            (('戊午','辛酉','甲午','庚申'),True,1,1),
            (('戊午','辛酉','甲午','丙寅'),False,0,0),
            (('庚申','辛酉','甲午','丙寅'),False,0,0)
        ]
        for pillars,matched,v_count,h_count in checks:
            with self.subTest(pillars=pillars):
                out=chart(*pillars,pattern_variant=PATTERN_VARIANT)
                official=out['result']['pattern_candidates']['official']
                conflict=official['yuanhai_hour_killing_restriction']
                self.assertEqual(conflict['status'],'restriction_observed' if matched else 'not_observed')
                self.assertEqual(len(conflict['hour_visible_killing_positions']),v_count)
                self.assertEqual(len(conflict['hour_hidden_killing_positions']),h_count)
                self.assertEqual(official['qualification']['family_determination_status'],'unresolved')
                self.assertIsNone(official['determination']['pattern'])
                for name in ('month_official_positions','hour_visible_killing_positions','hour_hidden_killing_positions'):
                    for position in conflict[name]:
                        value=out
                        for token in position['fact_ref'][2:].split('/'):
                            value=value[int(token)] if isinstance(value,list) else value[token]
                        self.assertIsNotNone(value)
                for cond in conflict['conditions']:
                    value=out
                    for token in cond['fact_ref'][2:].split('/'):
                        value=value[int(token)] if isinstance(value,list) else value[token]
                    self.assertIsNotNone(value)
                self.assertFalse(out['interpretation_contract']['ai_may_explain'])

    def test_source_evidence_is_real_and_public_disabled(self):
        out=chart('戊午','辛酉','甲午','庚午',pattern_variant=PATTERN_VARIANT)
        step=next(s for s in out['trace'] if s['rule_id']=='bazi.phase2.official_pattern_candidates')
        self.assertTrue(any(out['evidence'][eid]['section_id']=='bazi.section.s055'
                            for eid in step['evidence_ids']))
        self.assertTrue(out['research_only'])
        plain=chart('戊午','辛酉','甲午','庚午')
        self.assertNotIn('pattern_candidates',plain['result'])

if __name__=='__main__':
    unittest.main()
