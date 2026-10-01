import unittest
from collections import Counter
from tianji_kb.foundations import CYCLE,BRANCHES
from tianji_kb.golden import run_cases
from tianji_kb.operations.liuren_chart import chart,compute,controls
from tianji_kb.operations.liuren import validate_sky,base

class LiurenExecutionTests(unittest.TestCase):
    def test_eleven_independently_fixed_cases_cover_all_nine_methods(self):
        self.assertEqual(len(run_cases(domain='liuren')),11)

    def test_all_60_days_times_12_rotations_are_defined(self):
        counts=Counter()
        for day in CYCLE:
            for hour in BRANCHES:
                result=compute('雨水',day,hour)
                validate_sky(result['sky_plate'])
                self.assertEqual(len(result['transmissions']),3)
                self.assertTrue(all(b in BRANCHES for b in result['transmissions']))
                counts[result['method']]+=1
                if result['method'] not in ('伏吟','别责','八专','昴星'):
                    if result['method']!='返吟' or result['selection']['control_candidates']:
                        initial,middle,final=result['transmissions']
                        self.assertEqual(result['sky_plate'][initial],middle)
                        self.assertEqual(result['sky_plate'][middle],final)
        self.assertEqual(set(counts),{'贼克','比用','涉害','遥克','昴星','别责','八专','伏吟','返吟'})
        self.assertEqual(sum(counts.values()),720)

    def test_every_month_general_reproduces_same_rotation(self):
        baseline=compute('雨水','甲子','子')
        for row in base()['month_general_by_solar_terms']:
            hour=BRANCHES[(BRANCHES.index(row['branch'])+1)%12]
            result=compute(row['terms'][0],'甲子',hour)
            self.assertEqual(result['sky_plate'],baseline['sky_plate'])
            self.assertEqual(result['transmissions'],baseline['transmissions'])

    def test_special_rules_are_not_generic_succession(self):
        self.assertEqual(compute('雨水','甲子','亥')['transmissions'],['寅','巳','申'])
        self.assertEqual(compute('雨水','辛丑','巳')['transmissions'],['亥','未','辰'])
        output=chart('雨水','乙丑','辰')
        self.assertEqual(output['result']['method'],'比用')
        self.assertEqual(output['result']['transmissions'],['卯','戌','巳'])
        self.assertEqual(output['trace'][-1]['rule_id'],'liuren.phase2.biyong')
        with self.assertRaises(ValueError):chart('雨水','甲子','子','unreviewed')
