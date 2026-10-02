import unittest
from datetime import datetime,timedelta
from tianji_kb.calendar import calendar,hour_pillar
from tianji_kb.golden import run_cases
from tianji_kb.operations.qimen_chart import chart
from tianji_kb.operations.qimen import chart_from_calendar,base,ORDER
from tianji_kb.foundations import CYCLE

class QimenExecutionTests(unittest.TestCase):
    def test_fixed_time_plate_and_boundary_goldens(self):
        self.assertEqual(len(run_cases(domain='qimen')),4)

    def test_shared_calendar_day_boundary_and_timezone(self):
        midnight=calendar('2026-02-03T23:00:00+08:00')
        zi=calendar('2026-02-03T23:00:00+08:00','zi-start')
        self.assertEqual((midnight['day_ganzhi'],midnight['hour_ganzhi']),('戊申','壬子'))
        self.assertEqual((zi['day_ganzhi'],zi['hour_ganzhi']),('己酉','甲子'))
        self.assertEqual(calendar('2026-06-21T08:24:30Z'),calendar('2026-06-21T16:24:30+08:00'))
        with self.assertRaises(ValueError):calendar('2026-01-01T00:00:00')
        with self.assertRaises(ValueError):calendar('1800-01-01T00:00:00+08:00')

    def test_all_24_terms_60_days_and_hours_preserve_symbols(self):
        # Existing plate operations already cross-check against pinned Node modules.
        for term,_,_ in base()['solar_term_bureaus']:
            for day in CYCLE:
                hour=hour_pillar(day[0],'子')
                result=chart_from_calendar(term,day,hour)
                self.assertEqual(set(result['earth_plate']),set(map(str,range(1,10))))
                self.assertEqual(len(set(result['stars'].values())-{''}),8)
                self.assertEqual(result['deities'][result['chief_star_palace']],'值符')
                self.assertIn(result['chief_door_palace'],ORDER)

    def test_trace_and_variant_rejection(self):
        result=chart('2000-01-07T12:00:00+08:00')
        self.assertEqual(len(result['trace']),5)
        self.assertTrue(all(step['evidence_ids'] for step in result['trace']))
        with self.assertRaises(ValueError):chart('2000-01-07T12:00:00+08:00','超接置闰')

class NamedQimenStarsTests(unittest.TestCase):
    def test_nine_named_stars_and_eight_doors_gods_are_exposed(self):
        from tianji_kb.operations.qimen_chart import chart,named_stars
        output=chart('2000-01-07T12:00:00+08:00')
        result=output['result'];positions=result['star_positions']
        self.assertEqual(set(positions),{'天蓬','天任','天冲','天辅','天英','天禽','天芮','天柱','天心'})
        self.assertEqual(positions['天禽'],positions['天芮'])
        self.assertEqual(len(set(positions.values())),8)
        self.assertEqual(len(result['door_positions']),8)
        self.assertEqual(len(result['deity_positions']),8)
        self.assertEqual(output['trace'][-1]['output']['star_positions'],positions)
        with self.assertRaises(ValueError):named_stars({'1':'天蓬'})
