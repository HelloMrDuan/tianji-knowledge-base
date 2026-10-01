import unittest
from tianji_kb.operations.liuyao import *

class LiuyaoPhase1Tests(unittest.TestCase):
    def test_najia_and_shiying_classical_examples(self):
        self.assertEqual(assign_najia('乾','乾'), ['甲子','甲寅','甲辰','壬午','壬申','壬戌'])
        self.assertEqual(assign_najia('巽','乾'), ['辛丑','辛亥','辛酉','壬午','壬申','壬戌'])
        self.assertEqual(shi_ying('本宫'), {'shi':6,'ying':3})
        self.assertEqual(shi_ying('归魂'), {'shi':3,'ying':6})
        with self.assertRaises(ValueError):
            assign_najia('unknown','乾')

    def test_six_spirits_match_existing_golden_case(self):
        self.assertEqual(six_spirits('己'),['螣蛇','白虎','玄武','青龙','朱雀','勾陈'])
        for stem in STEMS:
            self.assertEqual(len(set(six_spirits(stem))),6)
        with self.assertRaises(ValueError):
            six_spirits('甲子')

    def test_five_elements_complete_relatives(self):
        expected = {'金':'兄弟','土':'父母','木':'妻财','火':'官鬼','水':'子孙'}
        for element,relative in expected.items():
            self.assertEqual(six_relative('金',element),relative)
        for element in ELEMENTS:
            self.assertEqual(len({six_relative(element,e) for e in ELEMENTS}),5)

    def test_all_60_days_have_exactly_the_missing_pair(self):
        cycle = [STEMS[i%10]+BRANCHES[i%12] for i in range(60)]
        for index,day in enumerate(cycle):
            occupied = {x[1] for x in cycle[index//10*10:index//10*10+10]}
            self.assertEqual(set(xunkong(day)),set(BRANCHES)-occupied)
        self.assertEqual(xunkong('甲子'),['戌','亥'])
        with self.assertRaises(ValueError):
            xunkong('甲丑')

    def test_combine_clash_are_symmetric_and_distinct(self):
        self.assertEqual(branch_relation('子','丑'),{'combine':True,'clash':False})
        self.assertEqual(branch_relation('子','午'),{'combine':False,'clash':True})
        for a in BRANCHES:
            for b in BRANCHES:
                self.assertEqual(branch_relation(a,b),branch_relation(b,a))
