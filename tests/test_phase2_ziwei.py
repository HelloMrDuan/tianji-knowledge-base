import unittest
from tianji_kb.foundations import CYCLE,BRANCHES
from tianji_kb.golden import run_cases
from tianji_kb.operations.ziwei_chart import chart,compute,bureau_for,ziwei_position

class ZiweiExecutionTests(unittest.TestCase):
    def test_fixed_classical_example_and_named_mutagen_cases(self):
        self.assertEqual(len(run_cases(domain='ziwei')),3)
        result=chart('甲子',1,1,'子')
        self.assertTrue(any('酉宮起初一日' in r['original_text'] for r in result['evidence'].values()))
        self.assertIn('D implementation',result['result']['mutagen_evidence'])

    def test_life_body_and_palace_ring_for_all_months_hours(self):
        for month in range(1,13):
            for hour in BRANCHES:
                result=compute('甲子',month,1,hour)
                self.assertEqual(len(set(result['palaces'].values())),12)
                self.assertEqual(result['palaces']['命宫'],result['life_palace'])
                self.assertEqual(BRANCHES.index(result['palaces']['迁移']),(BRANCHES.index(result['life_palace'])+6)%12)
                self.assertEqual(len(result['major_stars']),14)
                self.assertEqual(len(result['auxiliary_stars']),10)

    def test_nayin_all_sixty_pairs_and_ziwei_tianfu_mirror(self):
        expected_elements=['金','火','木','土','金','火','水','土','金','木','水','土','火','木','水','金','火','木','土','金','火','水','土','金','木','水','土','火','木','水']
        self.assertEqual([bureau_for(day[0],day[1])['element'] for day in CYCLE],[e for e in expected_elements for _ in range(2)])
        for number in range(2,7):
            for day in range(1,31):
                z=ziwei_position(day,number)
                self.assertIn(z,range(12))
                self.assertEqual((4-(4-z)%12)%12,z)
        self.assertEqual(ziwei_position(1,6),9)
        self.assertEqual(ziwei_position(1,2),1)

    def test_invalid_calendar_scope_or_variant_rejected(self):
        for args in [('甲丑',1,1,'子'),('甲子',-1,1,'子'),('甲子',True,1,'子'),('甲子',1,31,'子'),('甲子',1,1,'不明')]:
            with self.assertRaises(ValueError):compute(*args)
        with self.assertRaises(ValueError):chart('甲子',1,1,'子','unreviewed')
