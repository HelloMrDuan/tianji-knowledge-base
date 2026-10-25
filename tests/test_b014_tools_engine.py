"""B014: real-engine cases for ziwei/qimen/fengshui public connection.

OFFLINE CONTROLLED ACCEPTANCE ONLY: needs the full production runtime
+ knowledge data (backend-debug assembly). Public CI has no data/
directory, so it cannot run this file -- it is intentionally NOT wired
into validate.yml (only test_b014_tools_public.py runs there).
Run locally against an assembled backend:
  PYTHONPATH=<backend>/src python -m unittest tests.test_b014_tools_engine -v

Expected values below were observed from real executions and cross-checked
against the chart formulas (ziwei life/body palaces, 丙干四化, qimen bureau,
fengshui half-open mountain sectors). They are regression pins, not stubs.
"""
import unittest

from tianji_kb.engine import execute


class TestB014ZiweiEngine(unittest.TestCase):
    def test_sample_birth_computes_real_chart(self):
        # Sample birth on the ziwei home page: 1996-05-18 09:30 +08:00.
        # Gregorian -> lunar 1996-04-02, 巳时, 丙子年.
        result = execute(
            'ziwei',
            {'value': '1996-05-18T09:30:00+08:00',
             'year_boundary': 'lunar-new-year'},
            allow_research=False)
        self.assertEqual(result['variant'], 'quanshu-lunar-iztro-mutagen-v1')
        self.assertTrue(result['deterministic'])
        chart = result['result']
        # Life/body palaces from the formula (month 4, hour 巳=5):
        # life=(4+1-5)%12=0->子, body=(4+1+5)%12=10->戌.
        self.assertEqual(chart['life_palace'], '子')
        self.assertEqual(chart['body_palace'], '戌')
        self.assertEqual(chart['life_ganzhi'], '庚子')
        self.assertEqual(chart['bureau'], {'element': '土', 'number': 5})
        self.assertEqual(chart['palaces']['命宫'], '子')
        self.assertEqual(chart['palaces']['兄弟'], '亥')
        self.assertEqual(chart['palaces']['父母'], '丑')
        self.assertEqual(len(chart['palaces']), 12)
        self.assertEqual(chart['major_stars']['紫微'], '亥')
        self.assertEqual(chart['major_stars']['天机'], '戌')
        self.assertEqual(len(chart['major_stars']), 14)
        self.assertEqual(chart['auxiliary_stars']['左辅'], '未')
        # 丙干四化 standard: 天同禄 / 天机权 / 文昌科 / 廉贞忌.
        self.assertEqual(chart['four_transformations'],
                         {'化禄': '天同', '化权': '天机',
                          '化科': '文昌', '化忌': '廉贞'})
        self.assertEqual(chart['mutagen_variant'], 'iztro-default-v2')
        self.assertIn('无大限流年', chart['input_scope'])
        # No dayun / brightness / fortune field is computed.
        self.assertNotIn('dayun', chart)
        self.assertNotIn('大限', chart)

    def test_leap_lunar_month_is_rejected_not_computed(self):
        # 2023-04-01 falls in leap lunar month 2 (lunar_month -2).
        with self.assertRaises(ValueError) as ctx:
            execute(
                'ziwei',
                {'value': '2023-04-01T09:30:00+08:00',
                 'year_boundary': 'lunar-new-year'},
                allow_research=False)
        self.assertIn('Leap-lunar-month', str(ctx.exception))

    def test_year_boundary_must_be_explicit(self):
        with self.assertRaises(ValueError) as ctx:
            execute('ziwei', {'value': '1996-05-18T09:30:00+08:00'},
                    allow_research=False)
        self.assertIn('year_boundary', str(ctx.exception))


class TestB014QimenEngine(unittest.TestCase):
    def test_sample_time_computes_real_chart(self):
        # Sample time on the qimen home page: 2026-10-03 09:30 +08:00.
        result = execute('qimen', {'value': '2026-10-03T09:30:00+08:00'},
                         allow_research=False)
        self.assertEqual(result['variant'], 'qfdk-exact-term-midnight-v2')
        self.assertTrue(result['deterministic'])
        chart = result['result']
        self.assertEqual(chart['dun'], '阴')
        self.assertEqual(chart['bureau'], 7)
        self.assertEqual(chart['yuan'], '上元')
        self.assertEqual(chart['chief_star']['name'], '天心')
        self.assertEqual(chart['chief_star']['palace'], '4')
        self.assertEqual(chart['chief_door']['name'], '开门')
        self.assertEqual(chart['chief_door']['palace'], '8')
        # All nine stars, eight doors, eight deities placed exactly once.
        self.assertEqual(len(chart['star_positions']), 9)
        self.assertEqual(set(chart['star_positions']),
                         {'天蓬', '天任', '天冲', '天辅', '天英',
                          '天禽', '天芮', '天柱', '天心'})
        self.assertEqual(chart['star_positions']['天蓬'], '9')
        self.assertEqual(len(chart['door_positions']), 8)
        self.assertEqual(chart['door_positions']['开门'], '8')
        self.assertEqual(len(chart['deity_positions']), 8)
        self.assertEqual(chart['deity_positions']['值符'], '4')
        # The scope itself excludes super-intercalation.
        self.assertIn('不含置闰', chart['scope'])
        self.assertNotIn('intercalation', chart)

    def test_qimen_plates_cover_all_nine_palaces(self):
        result = execute('qimen', {'value': '2026-10-03T09:30:00+08:00'},
                         allow_research=False)
        chart = result['result']
        # Sky plate maps every palace 1-9 to a stem.
        self.assertEqual(set(chart['sky_plate']), set('123456789'))
        self.assertEqual(set(chart['earth_plate']), set('123456789'))


class TestB014FengshuiEngine(unittest.TestCase):
    def test_sample_bearing_computes_real_mountain(self):
        # Sample bearing on the fengshui home page: 180 degrees.
        result = execute('fengshui', {'degrees': 180}, allow_research=False)
        self.assertEqual(result['variant'],
                         'compass-half-open-explicit-epoch-v1')
        self.assertTrue(result['deterministic'])
        chart = result['result']
        self.assertEqual(chart['degrees'], 180)
        self.assertEqual(chart['mountain'], '午')
        self.assertEqual(chart['mountain_element'], '火')
        self.assertEqual(chart['trigram'], '离')
        self.assertEqual(chart['trigram_element'], '火')
        self.assertEqual(chart['opposite'], '子')
        # Production gate: no absolute period without explicit research.
        self.assertIsNone(chart['period'])

    def test_second_bearing_sector_boundary(self):
        # 37.5 degrees falls in the 艮 sector (half-open intervals).
        result = execute('fengshui', {'degrees': 37.5}, allow_research=False)
        chart = result['result']
        self.assertEqual(chart['mountain'], '艮')
        self.assertEqual(chart['mountain_element'], '土')
        self.assertEqual(chart['trigram'], '艮')
        self.assertEqual(chart['opposite'], '坤')
        self.assertIsNone(chart['period'])

    def test_absolute_period_refused_in_production(self):
        with self.assertRaises(ValueError) as ctx:
            execute('fengshui', {'degrees': 180, 'year': 2026},
                    allow_research=False)
        self.assertIn('Absolute period epochs', str(ctx.exception))


if __name__ == '__main__':
    unittest.main()
