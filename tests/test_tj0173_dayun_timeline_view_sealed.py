"""TJ-017.3 sealed end-to-end verification of the timeline view.

Runs only in the assembled offline-acceptance environment (the
composition's sequence stage needs the canonical foundations data,
the same boundary as TJ-017.4 itself). Verifies, against LIVE
composition results for every TJ-017.4 Golden case, that:

- the Sanming view presents the composition's own intervals
  byte-identically and matches the hand-derived TJ-017.3 Golden
  expectations (the same expectations the public suite pins against
  assembled fixtures, so fixture and live result are bound through
  the Golden);
- the Shenfeng view presents the composition's parallel block
  (first-period interval verbatim, later periods not_provided);
- the zero-jie case renders the whole-view unresolved empty state
  and the unknown-precision case the widened approximate interval;
- method switching on a live timeline never changes natal facts;
- no view contains a single-point date or an age value anywhere;
- the production chart surface carries no view output.
"""
import json
import unittest
from pathlib import Path

from tianji_kb.bazi_dayun_compose import classical_dayun_timeline
from tianji_kb.bazi_dayun_timeline_view import (
    classical_dayun_timeline_views,
    dayun_timeline_view,
)
from tianji_kb.operations.bazi_chart import chart

GOLDEN174 = json.loads(
    (Path(__file__).parent / 'golden_tj0174_dayun_compose.json')
    .read_text(encoding='utf-8'))
CASES174 = {c['id']: c for c in GOLDEN174['cases']}
GOLDEN = json.loads(
    (Path(__file__).parent / 'golden_tj0173_dayun_timeline_view.json')
    .read_text(encoding='utf-8'))
GOLDEN17_CASES = {(c['id'], c['method']): c for c in GOLDEN['cases']}

FORBIDDEN = {'start_date', 'end_date', 'start_age', 'end_age',
             'handover_datetime', 'start_datetime', 'age_years',
             'current_age'}


def _walk_keys(node):
    if isinstance(node, dict):
        for key, value in node.items():
            yield key
            yield from _walk_keys(value)
    elif isinstance(node, list):
        for item in node:
            yield from _walk_keys(item)


def _compose(case, *, include_shenfeng=True):
    return classical_dayun_timeline(
        case['birth_value'], zone=case['zone'],
        traditional_role=case['traditional_role'],
        periods=case['periods'],
        birth_time_precision=case['birth_time_precision'],
        include_shenfeng=include_shenfeng)


class LiveViewTests(unittest.TestCase):
    def test_every_golden_case_sanming_view(self):
        for case in GOLDEN174['cases']:
            with self.subTest(case=case['id']):
                timeline = _compose(case)
                view = dayun_timeline_view(timeline, method='sanming')
                self.assertEqual(view['status'], case['status'])
                self.assertEqual(view['natal']['pillars']['year'],
                                 case['pillars'][0])
                self.assertEqual(view['natal']['pillars']['month'],
                                 case['pillars'][1])
                self.assertEqual(view['direction']['value'],
                                 case['direction'])
                self.assertEqual(
                    view['direction']['counted_jie'],
                    {'name': case['jie_name'], 'at': case['jie_at']})
                self.assertEqual(view['duration']['interval_days'],
                                 case['duration_interval_days'])
                self.assertEqual(len(view['entries']),
                                 len(case['sequence_rows']))
                for entry, row, aligned in zip(
                        view['entries'], case['sequence_rows'],
                        timeline['sequence_time_alignment']):
                    self.assertEqual(entry['ganzhi'],
                                     row['candidate_ganzhi'])
                    self.assertEqual(
                        entry['ten_god_relative_to_natal_day_stem'],
                        row['ten_god'])
                    # The view presents the composition's own
                    # interval object values, never a recomputation.
                    self.assertEqual(entry['start_interval'],
                                     aligned['start_interval'])
                self.assertIs(view['research_only'], True)
                self.assertIs(view['public_enabled'], False)
                self.assertIs(view['ai_enabled'], False)

    def test_golden17_expectations_against_live_results(self):
        for (case_id, method), golden in GOLDEN17_CASES.items():
            case = CASES174[case_id]
            expected = golden['expected']
            with self.subTest(case=case_id, method=method):
                timeline = _compose(case)
                view = dayun_timeline_view(timeline, method=method)
                self.assertEqual(view['status'], expected['status'])
                self.assertEqual(view['duration']['interval_days'],
                                 expected['duration']['interval_days'])
                self.assertEqual(
                    [n['code'] for n in view['notices']],
                    expected['notice_codes'])
                got_sources = {
                    block['role']: [q['id'] for q in block['quotes']]
                    for block in view['sources']}
                self.assertEqual(got_sources,
                                 expected['source_quote_ids'])
                for entry, want in zip(view['entries'],
                                       expected['entries']):
                    self.assertEqual(entry['state'], want['state'])
                    if want['state'] == 'interval':
                        self.assertEqual(
                            entry['start_interval']['earliest'],
                            want['earliest'])
                        self.assertEqual(
                            entry['start_interval']['latest'],
                            want['latest'])

    def test_shenfeng_view_against_live_parallel_block(self):
        case = CASES174['Q1-forward-male-1958']
        timeline = _compose(case)
        view = dayun_timeline_view(timeline, method='shenfeng')
        parallel = timeline['parallel_variants']['shenfeng_day_level']
        want = parallel['first_period_start_interval']
        got = view['entries'][0]['start_interval']
        self.assertEqual(got['earliest'], want['earliest'])
        self.assertEqual(got['latest'], want['latest'])
        self.assertEqual(got['derivation'], want['derivation'])
        golden_parallel = GOLDEN174['shenfeng_parallel_case']
        self.assertEqual(got['earliest'],
                         golden_parallel['first_period_start_interval']
                         ['earliest'])
        self.assertTrue(all(e['state'] == 'not_provided'
                            for e in view['entries'][1:]))
        self.assertEqual(view['duration']['text_result_days'],
                         golden_parallel['text_result_days'])

    def test_zero_jie_live_empty_states_both_methods(self):
        case = CASES174['ADV001-zero-jie-2000']
        views = classical_dayun_timeline_views(
            case['birth_value'], zone=case['zone'],
            traditional_role=case['traditional_role'],
            periods=case['periods'],
            birth_time_precision=case['birth_time_precision'])
        self.assertEqual(views['sanming']['status'], 'unresolved')
        self.assertEqual(views['sanming']['reason'],
                         'zero_jie_boundary_convention_unreviewed')
        self.assertEqual(views['shenfeng']['status'], 'unresolved')
        self.assertEqual(views['shenfeng']['reason'],
                         'zero_day_count_not_exemplified_in_text')
        for view in views.values():
            self.assertTrue(all(e['start_interval'] is None
                                for e in view['entries']))

    def test_method_switch_on_live_timeline_keeps_natal_facts(self):
        case = CASES174['Q3-forward-female-1959']
        views = classical_dayun_timeline_views(
            case['birth_value'], zone=case['zone'],
            traditional_role=case['traditional_role'],
            periods=case['periods'],
            birth_time_precision=case['birth_time_precision'])
        for key in ('natal', 'direction', 'counting'):
            self.assertEqual(views['sanming'][key],
                             views['shenfeng'][key])

    def test_no_point_dates_or_age_values_in_live_views(self):
        for case in GOLDEN174['cases']:
            with self.subTest(case=case['id']):
                timeline = _compose(case)
                for method in ('sanming', 'shenfeng'):
                    view = dayun_timeline_view(timeline, method=method)
                    keys = set(_walk_keys(view))
                    self.assertFalse(keys & FORBIDDEN)
                    self.assertEqual(
                        {k for k in keys if 'age' in k},
                        {'age_presentation'})


class ProductionSurfaceTests(unittest.TestCase):
    def test_default_chart_carries_no_view_output(self):
        result = chart('戊戌', '庚申', '甲子', '甲戌')
        self.assertNotIn('dayun_timeline_view', result)
        self.assertNotIn('dayun_timeline_views', result)
        self.assertNotIn('dayun-timeline-view-v1', json.dumps(
            result, ensure_ascii=False))


if __name__ == '__main__':
    unittest.main()
