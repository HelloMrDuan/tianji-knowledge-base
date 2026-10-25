"""B012: real yijing/liuren engine execution + public projection on real results.

OFFLINE CONTROLLED ACCEPTANCE ONLY. This file needs the full production
runtime + canonical knowledge data (backend-debug assembly). It is NOT
executed by public CI (public CI has no data/ directory) and must never be
reported as public-CI evidence. Run from the backend-debug assembly:
  PYTHONPATH=<backend>/src python -m unittest discover -s tests \\
      -p 'test_b012_tools_engine.py' -v
"""
import unittest

from tianji_kb.engine import execute
from tianji_kb.api import response_for
from tianji_kb.public_projection import project_execution, _PRIVATE_KEYS


def _walk(value):
    if isinstance(value, dict):
        for key, item in value.items():
            yield key, item
            yield from _walk(item)
    elif isinstance(value, list):
        for item in value:
            yield from _walk(item)


class TestB012YijingEngine(unittest.TestCase):
    def test_qian_first_line_change(self):
        raw = execute('yijing', {'bits': '111111', 'changing_lines': [1]},
                      None, allow_research=False)
        chart = raw['result']
        self.assertEqual(chart['original'],
                         {'number': 1, 'name': '乾为天', 'binary': '111111',
                          'lower': '乾', 'upper': '乾'})
        self.assertEqual(chart['change'],
                         {'number': 44, 'name': '天风姤', 'binary': '011111',
                          'lower': '巽', 'upper': '乾'})
        self.assertEqual(chart['opposite']['name'], '坤为地')
        self.assertEqual(chart['inverse']['name'], '乾为天')
        self.assertEqual(chart['nuclear']['name'], '乾为天')
        self.assertTrue(raw['deterministic'])
        self.assertEqual(raw['variant'], 'bottom-up-six-lines-v1')
        self.assertEqual(raw['mode'], 'production')

    def test_public_path_shape(self):
        raw = execute('yijing', {'bits': '111111', 'changing_lines': [1]},
                      None, allow_research=False)
        out = project_execution(response_for(raw).model_dump())
        self.assertEqual(out['domain'], 'yijing')
        self.assertTrue(out['deterministic'])
        self.assertEqual(out['chart']['original']['name'], '乾为天')
        self.assertEqual(out['chart']['change']['name'], '天风姤')
        keys = {k for k, _ in _walk(out['chart'])}
        self.assertFalse(keys & set(_PRIVATE_KEYS))


class TestB012LiurenEngine(unittest.TestCase):
    def test_october_2026_morning_chart(self):
        raw = execute('liuren', {'value': '2026-10-03T09:30:00+08:00'},
                      None, allow_research=False)
        chart = raw['result']
        self.assertEqual(chart['month_general']['name'], '天罡')
        self.assertEqual(chart['month_general']['branch'], '辰')
        self.assertEqual(len(chart['four_lessons']), 4)
        self.assertEqual(chart['method'], '遥克')
        self.assertEqual(chart['transmissions'], ['午', '巳', '辰'])
        self.assertEqual(raw['variant'], 'daquan-nine-methods-lodged-stems-v1')
        # Explicit boundary: no noble-general field exists in the chart.
        keys = {k for k, _ in _walk(chart)}
        self.assertNotIn('noble', keys)
        self.assertNotIn('天将', keys)
        # ... and the limitation is declared in the chart itself.
        self.assertTrue(any('天将未实现' in line
                            for line in chart['limitations']))

    def test_public_path_shape_and_projection(self):
        raw = execute('liuren', {'value': '2026-10-03T09:30:00+08:00'},
                      None, allow_research=False)
        out = project_execution(response_for(raw).model_dump())
        self.assertEqual(out['domain'], 'liuren')
        self.assertTrue(out['deterministic'])
        self.assertEqual(out['chart']['method'], '遥克')
        self.assertTrue(any('天将未实现' in line
                            for line in out['chart']['limitations']))
        keys = {k for k, _ in _walk(out['chart'])}
        self.assertFalse(keys & set(_PRIVATE_KEYS))
        # Rule ids in the public output are aliases, not raw rule strings.
        for row in out['rule_matches']:
            if 'rule_id' in row:
                self.assertRegex(row['rule_id'], r'^R\d+$')


if __name__ == '__main__':
    unittest.main()
