import unittest
from pathlib import Path
from tianji_kb.knowledge import read_json
from tianji_kb.operations.fengshui import *

ROOT=Path(__file__).resolve().parents[1]
class FengshuiPhase1Tests(unittest.TestCase):
    def test_luoshu_both_orientations_are_magic_squares(self):
        for orientation in ['south_up','north_up']:
            grid=luoshu_grid(orientation)
            self.assertEqual(set(sum(grid,[])),set(range(1,10)))
            self.assertTrue(all(sum(row)==15 for row in grid))
            self.assertTrue(all(sum(grid[i][j] for i in range(3))==15 for j in range(3)))
            self.assertEqual(sum(grid[i][i] for i in range(3)),15)
            self.assertEqual(sum(grid[i][2-i] for i in range(3)),15)

    def test_existing_24_sectors_boundaries_and_opposites(self):
        self.assertEqual(mountain_at(0)['mountain'],'子')
        self.assertEqual(mountain_at(7.49999)['mountain'],'子')
        self.assertEqual(mountain_at(7.5)['mountain'],'癸')
        self.assertEqual(mountain_at(352.5)['mountain'],'子')
        self.assertEqual(mountain_at(-360)['mountain'],'子')
        records=read_json(ROOT/'data/canonical/fengshui/twenty_four_mountains_v1.json')['records']
        for record in records:
            center=record['center_degrees']
            self.assertEqual(mountain_at(center)['mountain'],record['mountain'])
            self.assertEqual(mountain_at(center+180)['mountain'],record['opposite']['mountain'])
        with self.assertRaises(ValueError):
            mountain_at(float('nan'))

    def test_relative_beasts_do_not_assert_compass_directions(self):
        self.assertEqual(four_beasts(),{'left':'青龙','right':'白虎','front':'朱雀','back':'玄武'})

    def test_periods_require_explicit_research_mode(self):
        with self.assertRaises(ValueError):
            research_period(2024)
        for year,expected in [(1864,1),(1883,1),(1884,2),(2023,8),(2024,9),(2043,9)]:
            period=research_period(year,research=True)
            self.assertEqual(period['period'],expected)
            self.assertEqual(period['evidence_level'],'D')
            self.assertEqual(period['stage'],'quarantine')
        with self.assertRaises(ValueError):
            research_period(2044,research=True)

    def test_glossary_and_school_contracts(self):
        bundle=read_json(ROOT/'data/canonical/fengshui/phase1_knowledge.json')
        names={t['name'] for t in bundle['terms']}
        self.assertTrue({'龙','穴','砂','水','明堂','来龙','去水','朝案','青龙','白虎','朱雀','玄武','坐','向','河图','洛书','先天八卦','后天八卦','三元九运'}<=names)
        self.assertTrue({'玄空','三合','八宅','三元'}<={r['school'] for r in bundle['rules']})
