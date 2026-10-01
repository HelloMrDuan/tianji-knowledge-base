import unittest
from pathlib import Path
from tianji_kb.knowledge import read_json
from tianji_kb.operations.liuren import *

ROOT=Path(__file__).resolve().parents[1]
class LiurenPhase1Tests(unittest.TestCase):
    def test_month_generals_cover_all_terms_once(self):
        rows=base()['month_general_by_solar_terms']
        terms=[term for row in rows for term in row['terms']]
        self.assertEqual(len(set(terms)),24)
        for row in rows:
            for term in row['terms']:
                self.assertEqual(month_general(term),row)
        with self.assertRaises(ValueError):
            month_general('unknown')

    def test_all_144_plates_align_month_general_to_hour(self):
        for general in BRANCHES:
            for hour in BRANCHES:
                sky=sky_plate(general,hour)
                self.assertEqual(sky[hour],general)
                self.assertEqual(set(sky.values()),set(BRANCHES))
                validate_sky(sky)
        self.assertEqual(sky_plate('子','子'),dict(zip(BRANCHES,BRANCHES)))

    def test_four_lessons_fixed_rotation_example(self):
        # 亥将加子时: 寅上丑、丑上子、子上亥、亥上戌；甲寄寅。
        sky=sky_plate('亥','子')
        self.assertEqual(four_lessons('甲','子',sky),[{'lesson':1,'upper':'丑','lower':'甲'},{'lesson':2,'upper':'子','lower':'丑'},{'lesson':3,'upper':'亥','lower':'子'},{'lesson':4,'upper':'戌','lower':'亥'}])
        self.assertEqual(follow_transmissions('丑',sky),['丑','子','亥'])
        with self.assertRaises(ValueError):
            four_lessons('甲','丑',sky)
        bad=dict(sky);bad['子'],bad['丑']=bad['丑'],bad['子']
        with self.assertRaises(ValueError):
            four_lessons('甲','子',bad)

    def test_noble_variants_remain_distinct(self):
        self.assertEqual(noble_start('甲','昼',0),'丑')
        self.assertEqual(noble_start('甲','昼',1),'未')
        with self.assertRaises(ValueError):
            noble_start('甲','昼',2)

    def test_nine_methods_and_general_properties_are_sourced(self):
        bundle=read_json(ROOT/'data/canonical/liuren/phase1_knowledge.json')
        names={t['name'] for t in bundle['terms']}
        self.assertTrue({'贼克','比用','涉害','遥克','昴星','别责','八专','伏吟','返吟'}<=names)
        generals=[c for c in bundle['concepts'] if c['kind']=='heavenly_general']
        self.assertEqual(len(generals),12)
        for general in generals:
            props=general['attributes']
            self.assertIn(props['element'],list('木火土金水'))
            self.assertIn(props['traditional_luck_attribute'],['吉将','凶将'])
        self.assertTrue(all(r['execution_status']=='partially_structured' for r in bundle['rules'] if r['operation']['kind']=='transmission_selection'))
