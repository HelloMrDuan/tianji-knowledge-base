"""TJ-031.14: Qian Yongjiu / Kun Yongliu special-use texts reach production.

The reviewed Zhouyi classic core carries a special_use record only for
hexagram 1 (Qian, Yongjiu) and hexagram 2 (Kun, Yongliu) — the texts
consulted when all six lines move. Before TJ-031.14 no production code
read that field, so an all-old-yang Qian or all-old-yin Kun cast never
surfaced the text even though the data was already in the sealed
runtime (TJ-031.12 finding; data present, wiring missing, the same
shape as TJ-031.3).

These tests run the real backend path — operations.liuyao_chart.chart
assembly and the public HTTP execute endpoint — against the real
reviewed corpus, and assert the exact verbatim text and the exact
appearance conditions. Like tests/test_phase2_liuyao.py, this module
needs the assembled canonical data tree (data/canonical/...), which
is not part of the public checkout: it runs in the offline sealed
acceptance only and is deliberately NOT named in
.github/workflows/validate.yml. The public-CI-safe projection
contract for the same fields lives in
tests/test_tj0315_public_labels.py (SpecialUseScopeTests).
"""
import json
import unittest
from pathlib import Path

from tianji_kb.operations.liuyao_chart import chart

ROOT = Path(__file__).resolve().parents[1]
DAY, MONTH = '甲子', '午'

# Traditional texts exactly as stored in the reviewed corpus and
# verified character-for-character by the TJ-031.12 on-machine
# equivalence check. Pinned here so a silent data change cannot
# redefine what production must surface.
YONGJIU_POSITION, YONGJIU_TEXT = '用九', '見群龍無首，吉。'
YONGLIU_POSITION, YONGLIU_TEXT = '用六', '利永貞。'
SPECIAL_USE_SCOPE = 'verbatim_classical_special_use_text_not_a_verdict'
JUDGMENT_SCOPE = 'verbatim_classical_hexagram_text_not_a_verdict'


def _records():
    document = json.loads(
        (ROOT / 'data/canonical/yijing/zhouyi_classic_core.json')
        .read_text(encoding='utf-8'))
    return {row['number']: row for row in document['records']}


class SpecialUseCorpusTests(unittest.TestCase):
    """The wiring is data-driven: exactly two records may carry it."""

    @classmethod
    def setUpClass(cls):
        cls.records = _records()

    def test_special_use_records_are_exactly_qian_and_kun(self):
        carriers = {number for number, row in self.records.items()
                    if row.get('special_use')}
        self.assertEqual(carriers, {1, 2})
        self.assertEqual(self.records[1]['special_use']['position'], YONGJIU_POSITION)
        self.assertEqual(self.records[1]['special_use']['text'], YONGJIU_TEXT)
        self.assertEqual(self.records[2]['special_use']['position'], YONGLIU_POSITION)
        self.assertEqual(self.records[2]['special_use']['text'], YONGLIU_TEXT)


class SpecialUseChartTests(unittest.TestCase):
    """chart() attaches the verbatim text only for the two all-moving
    pure-hexagram casts, and for nothing else."""

    @classmethod
    def setUpClass(cls):
        cls.records = _records()

    def test_qian_all_old_yang_surfaces_yongjiu_verbatim(self):
        result = chart([9] * 6, DAY, MONTH)['result']
        self.assertEqual(result['original']['number'], 1)
        self.assertEqual(result['changing_lines'], [1, 2, 3, 4, 5, 6])
        classic = result['zhouyi_classic']
        self.assertEqual(classic['original']['special_use'],
                         {'position': YONGJIU_POSITION, 'text': YONGJIU_TEXT})
        self.assertEqual(classic['original']['special_use']['text'],
                         self.records[1]['special_use']['text'])
        self.assertEqual(len(classic['original']['moving_line_texts']), 6)
        self.assertNotIn('special_use', classic['changed'])

    def test_kun_all_old_yin_surfaces_yongliu_verbatim(self):
        result = chart([6] * 6, DAY, MONTH)['result']
        self.assertEqual(result['original']['number'], 2)
        self.assertEqual(result['changing_lines'], [1, 2, 3, 4, 5, 6])
        classic = result['zhouyi_classic']
        self.assertEqual(classic['original']['special_use'],
                         {'position': YONGLIU_POSITION, 'text': YONGLIU_TEXT})
        self.assertEqual(classic['original']['special_use']['text'],
                         self.records[2]['special_use']['text'])
        self.assertEqual(len(classic['original']['moving_line_texts']), 6)
        self.assertNotIn('special_use', classic['changed'])

    def test_qian_without_moving_lines_has_no_special_use(self):
        classic = chart([7] * 6, DAY, MONTH)['result']['zhouyi_classic']
        self.assertEqual(classic['original']['number'], 1)
        self.assertNotIn('special_use', classic['original'])

    def test_qian_single_moving_line_has_no_special_use(self):
        classic = chart([9, 7, 7, 7, 7, 7], DAY, MONTH)['result']['zhouyi_classic']
        self.assertEqual(classic['original']['number'], 1)
        self.assertNotIn('special_use', classic['original'])

    def test_kun_single_moving_line_has_no_special_use(self):
        classic = chart([6, 8, 8, 8, 8, 8], DAY, MONTH)['result']['zhouyi_classic']
        self.assertEqual(classic['original']['number'], 2)
        self.assertNotIn('special_use', classic['original'])

    def test_other_hexagram_all_moving_has_no_special_use(self):
        # Jiji (63): every line moves, but the record carries no
        # special_use, so the field must not appear.
        result = chart([9, 6, 9, 6, 9, 6], DAY, MONTH)['result']
        self.assertEqual(result['original']['number'], 63)
        self.assertEqual(result['changing_lines'], [1, 2, 3, 4, 5, 6])
        self.assertEqual(result['changed']['number'], 64)
        self.assertNotIn('special_use', result['zhouyi_classic']['original'])


class SpecialUsePublicApiTests(unittest.TestCase):
    """The public execute path delivers the field through projection,
    with its verbatim scope marker beside it."""

    def _execute(self, yao_values):
        from fastapi.testclient import TestClient
        from tianji_kb.api import create_app
        with TestClient(create_app()) as client:
            response = client.post('/api/v1/public/execute', json={
                'domain': 'liuyao', 'variant': 'jingfang-eight-palaces-v1',
                'input': {'value': '2026-10-09T17:30:00+08:00',
                          'yao_values': list(yao_values)},
                'mode': 'production', 'explain': False,
            })
        self.assertEqual(response.status_code, 200, response.text)
        return response.json()

    def test_public_api_qian_all_old_yang(self):
        classic = self._execute([9] * 6)['chart']['zhouyi_classic']
        self.assertEqual(classic['original']['special_use'],
                         {'position': YONGJIU_POSITION, 'text': YONGJIU_TEXT})
        self.assertEqual(classic['original']['special_use_scope'], SPECIAL_USE_SCOPE)
        self.assertEqual(classic['original']['judgment_scope'], JUDGMENT_SCOPE)

    def test_public_api_kun_all_old_yin(self):
        classic = self._execute([6] * 6)['chart']['zhouyi_classic']
        self.assertEqual(classic['original']['special_use'],
                         {'position': YONGLIU_POSITION, 'text': YONGLIU_TEXT})
        self.assertEqual(classic['original']['special_use_scope'], SPECIAL_USE_SCOPE)

    def test_public_api_without_all_moving_has_no_special_use(self):
        for values in ([7] * 6, [9, 7, 7, 7, 7, 7], [6, 8, 8, 8, 8, 8],
                       [9, 6, 9, 6, 9, 6]):
            with self.subTest(values=values):
                classic = self._execute(values)['chart']['zhouyi_classic']
                self.assertNotIn('special_use', classic['original'])
                self.assertNotIn('special_use_scope', classic['original'])


if __name__ == '__main__':
    unittest.main()
