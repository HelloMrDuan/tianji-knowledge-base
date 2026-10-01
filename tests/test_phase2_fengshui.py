import unittest
from tianji_kb.golden import run_cases
from tianji_kb.operations.fengshui import mountain_at
from tianji_kb.operations.fengshui_chart import chart,relative_period

class FengshuiExecutionTests(unittest.TestCase):
    def test_fixed_boundaries_and_gated_research_case(self):
        self.assertEqual(len(run_cases(domain='fengshui')),4)
    def test_all_24_centers_edges_opposites_and_wraps(self):
        for i in range(24):
            degree=i*15
            center=mountain_at(degree)
            self.assertEqual(mountain_at(degree+720)['mountain'],center['mountain'])
            self.assertEqual(mountain_at(degree+180)['mountain'],center['opposite']['mountain'])
            self.assertEqual(mountain_at(degree+7.5-1e-8)['mountain'],center['mountain'])
            self.assertNotEqual(mountain_at(degree+7.5)['mountain'],center['mountain'])
        self.assertEqual(chart(-0.1)['result']['trigram'],'坎')
    def test_relative_twenty_year_and_180_year_periods(self):
        self.assertEqual(relative_period(2023,1864)['period'],8)
        self.assertEqual(relative_period(2024,1864)['period'],9)
        self.assertEqual(relative_period(2044,1864)['yuan'],'上元')
        for year in range(1664,2200):
            p=relative_period(year,1864)
            self.assertLessEqual(p['start_year'],year)
            self.assertGreaterEqual(p['end_year'],year)
            self.assertEqual(relative_period(year+180,1864)['period'],p['period'])
    def test_production_cannot_infer_unverified_epoch(self):
        for kw in [{'year':2024},{'year':2024,'epoch_year':1864},{'year':2024,'research':True}]:
            with self.assertRaises(ValueError):chart(0,**kw)
        with self.assertRaises(ValueError):chart(0,variant='unreviewed')
        with self.assertRaises(ValueError):relative_period(True,1864)
        r=chart(0,year=2024,epoch_year=1864,research=True)
        self.assertFalse(r['result']['period']['production_eligible'])
        self.assertIsNone(r['trace'][0]['output']['period'])
