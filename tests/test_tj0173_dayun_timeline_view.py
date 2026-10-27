"""TJ-017.3 public contracts for the Dayun timeline view model.

What this suite pins in the public checkout:

- the Golden view expectations are faithful transcriptions of the
  TJ-017.4 Golden (same real charts, same hand-derived intervals);
- the view transform over composition fixtures: interval fidelity
  (every view interval byte-identical to the composition interval
  it presents), first-entry endpoint consistency (birth + duration
  interval), method-switch invariance of natal/direction/counting
  facts, the full empty-state catalogue, the forbidden-field sweep
  (no single-point dates, no age values anywhere), source citation
  sets, and fail-closed rejection of forged or promoted inputs;
- the public projection's defensive strip of the view keys.

Fixture honesty: a full composition result needs the TJ-014.2
sequence stage, whose ten-god computation requires the assembled
canonical foundations, so -- exactly as in the TJ-017.4 public
suite -- the fixtures here assemble the composition's first three
stages from the REAL reviewed functions (calendar, TJ-017.1
direction, TJ-015 measurement, TJ-017.1 conversion) and zip them
with the sequence rows transcribed from the TJ-017.4 Golden, using
the composition module's own field mapping. The fixtures are
transports for the pure view transform, not composition results;
end-to-end verification against live composition results lives in
test_tj0173_dayun_timeline_view_sealed.py (offline acceptance only,
NOT public CI, same partition rule).
"""
import copy
import json
import unittest
from datetime import datetime, timedelta
from pathlib import Path

from tianji_kb.bazi_dayun_classical import (
    CONVERSION_VARIANT,
    DIRECTION_VARIANT,
    SHENFENG_CONVERSION_VARIANT,
    classical_direction,
    sanming_convert_measurement,
    shenfeng_convert_days,
)
from tianji_kb.bazi_dayun_compose import COMPOSE_VARIANT
from tianji_kb.bazi_dayun_jie import adjacent_jie_distance
from tianji_kb.bazi_dayun_sequence import VARIANT as SEQUENCE_VARIANT
from tianji_kb.bazi_dayun_timeline_view import (
    VIEW_VARIANT,
    classical_dayun_timeline_views,
    dayun_timeline_view,
)
from tianji_kb.calendar_tz import calendar_for_zone
from tianji_kb.public_projection import project_execution

GOLDEN = json.loads(
    (Path(__file__).parent / 'golden_tj0173_dayun_timeline_view.json')
    .read_text(encoding='utf-8'))
GOLDEN17_CASES = {(c['id'], c['method']): c for c in GOLDEN['cases']}
GOLDEN174 = json.loads(
    (Path(__file__).parent / 'golden_tj0174_dayun_compose.json')
    .read_text(encoding='utf-8'))
CASES174 = {c['id']: c for c in GOLDEN174['cases']}
MEASUREMENT_VARIANT = 'bazi-dayun-adjacent-jie-research-v1'


def _shenfeng_block(measured, direction):
    """Mirror of the composition's Shenfeng parallel block assembly."""
    converted = shenfeng_convert_days(measured['elapsed_whole_days'],
                                      direction=direction)
    block = {
        'variant': SHENFENG_CONVERSION_VARIANT,
        'status': converted['status'],
        'method': 'shenfeng_day_level',
        'input': converted.get('input'),
        'counting_target': converted.get('counting_target'),
        'text_result_days': converted.get('text_result_days'),
        'duration_interval_days': converted.get('duration_interval_days'),
        'granularity_note': converted.get('granularity_note'),
        'parallel_note': 'fixture mirror of the composition block',
    }
    if converted['status'] == 'converted':
        birth = datetime.fromisoformat(measured['birth_local_datetime'])
        interval = converted['duration_interval_days']
        block['first_period_start_interval'] = {
            'earliest': (birth + timedelta(days=interval['min_days']))
            .isoformat(),
            'latest': (birth + timedelta(days=interval['max_days']))
            .isoformat(),
            'max_inclusive': interval['max_inclusive'],
            'derivation': ('composition_level_birth_plus_shenfeng_'
                           'duration_interval'),
            'decade_shifts': ('not_provided_for_shenfeng_at_'
                              'composition_level'),
        }
    else:
        block['reason'] = converted['reason']
    return block


def build_timeline(case_id, *, include_shenfeng=False):
    """Assemble a composition-shaped fixture from real stage outputs.

    The first three stages run the reviewed functions live; the
    sequence rows are transcribed from the TJ-017.4 Golden and the
    alignment is zipped with the composition module's field mapping.
    """
    case = CASES174[case_id]
    cal = calendar_for_zone(case['birth_value'], case['zone'])
    assert [cal['year_ganzhi'], cal['month_ganzhi'], cal['day_ganzhi'],
            cal['hour_ganzhi']] == case['pillars']
    direction = classical_direction(
        cal['year_ganzhi'], traditional_role=case['traditional_role'])
    measured = adjacent_jie_distance(
        case['birth_value'], direction['direction'],
        expected_month_ganzhi=cal['month_ganzhi'])
    converted = sanming_convert_measurement(
        measured, birth_time_precision=case['birth_time_precision'],
        periods=case['periods'])
    rows = [{
        'period_index': r['period_index'],
        'candidate_ganzhi': r['candidate_ganzhi'],
        'stem': r['candidate_ganzhi'][0],
        'branch': r['candidate_ganzhi'][1],
        'ten_god_relative_to_natal_day_stem': r['ten_god'],
        'start_date': None, 'end_date': None,
        'start_age': None, 'end_age': None,
        'natal_interaction': None, 'luck_assessment': None,
    } for r in case['sequence_rows']]
    handovers = converted.get('handover_intervals') or []
    alignment = []
    for row in rows:
        entry = {
            'period_index': row['period_index'],
            'candidate_ganzhi': row['candidate_ganzhi'],
            'stem': row['stem'],
            'branch': row['branch'],
            'ten_god_relative_to_natal_day_stem':
                row['ten_god_relative_to_natal_day_stem'],
        }
        if converted['status'] == 'converted':
            handover = handovers[row['period_index'] - 1]
            entry['start_interval'] = {
                'earliest': handover['earliest'],
                'latest': handover['latest'],
                'max_inclusive': handover['max_inclusive'],
                'basis': handover['basis'],
                'method': 'sanming_shichen_level',
                'variant': CONVERSION_VARIANT,
            }
        else:
            entry['start_interval'] = None
            entry['start_interval_status'] = (
                'unresolved: ' + converted['reason'])
        alignment.append(entry)
    timeline = {
        'variant': COMPOSE_VARIANT,
        'status': converted['status'],
        'composition_chain': [
            DIRECTION_VARIANT, MEASUREMENT_VARIANT, CONVERSION_VARIANT,
            SEQUENCE_VARIANT],
        'birth': {
            'input_value': case['birth_value'],
            'zone': case['zone'],
            'local_datetime': measured['birth_local_datetime'],
        },
        'pillars': {
            'year_ganzhi': cal['year_ganzhi'],
            'month_ganzhi': cal['month_ganzhi'],
            'day_ganzhi': cal['day_ganzhi'],
            'hour_ganzhi': cal['hour_ganzhi'],
            'day_master': cal['day_ganzhi'][0],
        },
        'traditional_role': case['traditional_role'],
        'traditional_role_selection':
            'explicit_historical_category_not_inferred_identity',
        'direction': direction,
        'counting': {
            'measurement_variant': measured['variant'],
            'calendar_provider': measured['calendar_provider'],
            'selected_jie': measured['selected_jie'],
            'previous_jie': measured['previous_jie'],
            'next_jie': measured['next_jie'],
            'elapsed_seconds': measured['elapsed_seconds'],
            'elapsed_whole_days': measured['elapsed_whole_days'],
            'remaining_seconds_after_whole_days':
                measured['remaining_seconds_after_whole_days'],
            'zero_distance': measured['zero_distance'],
        },
        'sanming_conversion': converted,
        'sequence': {'variant': SEQUENCE_VARIANT, 'rows': rows},
        'sequence_time_alignment': alignment,
        'alignment_method': 'sanming_shichen_level',
        'parallel_variants': {},
        'limitations': [],
        'research_only': True, 'public_enabled': False,
        'ai_enabled': False,
        'evidence_binding': 'pending_phase1_rule_registration',
    }
    if converted['status'] != 'converted':
        timeline['reason'] = converted['reason']
    if include_shenfeng:
        timeline['parallel_variants']['shenfeng_day_level'] = (
            _shenfeng_block(measured, direction['direction']))
    return timeline


def _walk_keys(node):
    if isinstance(node, dict):
        for key, value in node.items():
            yield key
            yield from _walk_keys(value)
    elif isinstance(node, list):
        for item in node:
            yield from _walk_keys(item)


class GoldenTranscriptionTests(unittest.TestCase):
    def test_golden_matches_view_variant_and_source_cases(self):
        self.assertEqual(GOLDEN['variant'], VIEW_VARIANT)
        for (case_id, _method) in GOLDEN17_CASES:
            self.assertIn(case_id, CASES174)

    def test_golden_intervals_equal_tj0174_golden(self):
        for (case_id, method), golden in GOLDEN17_CASES.items():
            case = CASES174[case_id]
            expected = golden['expected']
            with self.subTest(case=case_id, method=method):
                if method == 'sanming':
                    if case['status'] == 'converted':
                        self.assertEqual(
                            expected['duration']['interval_days'],
                            case['duration_interval_days'])
                        for entry, handover in zip(
                                expected['entries'],
                                case['handover_intervals']):
                            self.assertEqual(entry['earliest'],
                                             handover['earliest'])
                            self.assertEqual(entry['latest'],
                                             handover['latest'])
                    else:
                        self.assertIsNone(
                            expected['duration']['interval_days'])
                else:
                    parallel = GOLDEN174['shenfeng_parallel_case']
                    self.assertEqual(
                        expected['duration']['interval_days'],
                        parallel['duration_interval_days'])
                    first = expected['entries'][0]
                    want = parallel['first_period_start_interval']
                    self.assertEqual(first['earliest'], want['earliest'])
                    self.assertEqual(first['latest'], want['latest'])


class ViewContractTests(unittest.TestCase):
    """View outputs against the hand-derived Golden expectations."""

    def _view(self, case_id, method):
        timeline = build_timeline(
            case_id, include_shenfeng=(method == 'shenfeng'))
        return dayun_timeline_view(timeline, method=method)

    def test_golden_cases(self):
        for (case_id, method), golden in GOLDEN17_CASES.items():
            expected = golden['expected']
            with self.subTest(case=case_id, method=method):
                view = self._view(case_id, method)
                self.assertEqual(view['variant'], VIEW_VARIANT)
                self.assertEqual(view['status'], expected['status'])
                self.assertEqual(view['method'], method)
                direction = view['direction']
                want_dir = expected['direction']
                self.assertEqual(direction['value'], want_dir['value'])
                self.assertEqual(direction['label'], want_dir['label'])
                self.assertEqual(direction['counting_target'],
                                 want_dir['counting_target'])
                self.assertEqual(direction['counted_jie'],
                                 want_dir['counted_jie'])
                duration = view['duration']
                want_dur = expected['duration']
                self.assertEqual(duration['interval_days'],
                                 want_dur['interval_days'])
                self.assertEqual(duration['approximate'],
                                 want_dur['approximate'])
                if 'decomposition' in want_dur:
                    got = duration['decomposition']
                    for key, value in want_dur['decomposition'].items():
                        self.assertEqual(got[key], value)
                if 'text_result_days' in want_dur:
                    self.assertEqual(duration['text_result_days'],
                                     want_dur['text_result_days'])
                    self.assertEqual(duration['counting']['whole_days'],
                                     want_dur['whole_days'])
                self.assertEqual(len(view['entries']),
                                 len(expected['entries']))
                for entry, want in zip(view['entries'],
                                       expected['entries']):
                    self.assertEqual(entry['period_index'],
                                     want['period_index'])
                    self.assertEqual(entry['ganzhi'], want['ganzhi'])
                    self.assertEqual(
                        entry['ten_god_relative_to_natal_day_stem'],
                        want['ten_god'])
                    self.assertEqual(entry['state'], want['state'])
                    if want['state'] == 'interval':
                        interval = entry['start_interval']
                        self.assertEqual(interval['earliest'],
                                         want['earliest'])
                        self.assertEqual(interval['latest'],
                                         want['latest'])
                        self.assertEqual(interval['max_inclusive'],
                                         want['max_inclusive'])
                        if 'basis' in want:
                            self.assertEqual(interval['basis'],
                                             want['basis'])
                        if 'derivation' in want:
                            self.assertEqual(interval['derivation'],
                                             want['derivation'])
                    else:
                        self.assertIsNone(entry['start_interval'])
                self.assertEqual(
                    [n['code'] for n in view['notices']],
                    expected['notice_codes'])
                got_sources = {
                    block['role']: [q['id'] for q in block['quotes']]
                    for block in view['sources']}
                self.assertEqual(got_sources,
                                 expected['source_quote_ids'])
                if 'reason' in expected:
                    self.assertEqual(view['reason'], expected['reason'])


class FidelityTests(unittest.TestCase):
    def test_view_intervals_are_composition_intervals_verbatim(self):
        for case_id in ('Q1-forward-male-1958', 'Q2-backward-female-1949',
                        'Q3-forward-female-1959',
                        'Q4-backward-male-1959'):
            with self.subTest(case=case_id):
                timeline = build_timeline(case_id)
                view = dayun_timeline_view(timeline, method='sanming')
                for entry, aligned in zip(
                        view['entries'],
                        timeline['sequence_time_alignment']):
                    self.assertEqual(entry['start_interval'],
                                     aligned['start_interval'])

    def test_first_entry_endpoints_equal_birth_plus_duration(self):
        timeline = build_timeline('Q1-forward-male-1958')
        view = dayun_timeline_view(timeline, method='sanming')
        birth = datetime.fromisoformat(
            timeline['birth']['local_datetime'])
        interval = view['duration']['interval_days']
        first = view['entries'][0]['start_interval']
        self.assertEqual(
            first['earliest'],
            (birth + timedelta(days=interval['min_days'])).isoformat())
        self.assertEqual(
            first['latest'],
            (birth + timedelta(days=interval['max_days'])).isoformat())

    def test_shenfeng_first_entry_matches_parallel_block(self):
        timeline = build_timeline('Q1-forward-male-1958',
                                  include_shenfeng=True)
        view = dayun_timeline_view(timeline, method='shenfeng')
        parallel = timeline['parallel_variants']['shenfeng_day_level']
        want = parallel['first_period_start_interval']
        got = view['entries'][0]['start_interval']
        self.assertEqual(got['earliest'], want['earliest'])
        self.assertEqual(got['latest'], want['latest'])
        self.assertEqual(got['max_inclusive'], want['max_inclusive'])
        self.assertEqual(got['derivation'], want['derivation'])

    def test_view_does_not_mutate_or_alias_input(self):
        timeline = build_timeline('Q1-forward-male-1958',
                                  include_shenfeng=True)
        snapshot = copy.deepcopy(timeline)
        view = dayun_timeline_view(timeline, method='sanming')
        view['entries'][0]['start_interval']['earliest'] = 'tampered'
        view['sources'][0]['quotes'][0]['quote'] = 'tampered'
        self.assertEqual(timeline, snapshot)


class MethodSwitchTests(unittest.TestCase):
    def test_switching_method_keeps_natal_facts_identical(self):
        timeline = build_timeline('Q1-forward-male-1958',
                                  include_shenfeng=True)
        sanming = dayun_timeline_view(timeline, method='sanming')
        shenfeng = dayun_timeline_view(timeline, method='shenfeng')
        for key in ('natal', 'direction', 'counting',
                    'composition_chain'):
            self.assertEqual(sanming[key], shenfeng[key])
        self.assertEqual(
            [e['ganzhi'] for e in sanming['entries']],
            [e['ganzhi'] for e in shenfeng['entries']])
        options = {o['id']: o for o in sanming['method_options']}
        self.assertTrue(options['sanming']['selectable'])
        self.assertTrue(options['shenfeng']['selectable'])
        self.assertNotEqual(sanming['duration']['interval_days'],
                            shenfeng['duration']['interval_days'])

    def test_shenfeng_not_selectable_without_parallel_block(self):
        timeline = build_timeline('Q1-forward-male-1958')
        view = dayun_timeline_view(timeline, method='sanming')
        options = {o['id']: o for o in view['method_options']}
        self.assertFalse(options['shenfeng']['selectable'])
        with self.assertRaises(ValueError):
            dayun_timeline_view(timeline, method='shenfeng')


class EmptyStateTests(unittest.TestCase):
    def test_zero_jie_boundary_whole_view_unresolved(self):
        timeline = build_timeline('ADV001-zero-jie-2000')
        view = dayun_timeline_view(timeline, method='sanming')
        self.assertEqual(view['status'], 'unresolved')
        self.assertEqual(view['reason'],
                         'zero_jie_boundary_convention_unreviewed')
        self.assertIsNone(view['duration']['interval_days'])
        self.assertTrue(all(e['state'] == 'unresolved'
                            for e in view['entries']))
        self.assertTrue(all(e['start_interval'] is None
                            for e in view['entries']))
        self.assertIn('zero_jie_boundary',
                      [n['code'] for n in view['notices']])
        # Natal facts are still presented; only the times are empty.
        self.assertEqual(view['natal']['pillars']['year'], '庚辰')
        self.assertEqual(view['direction']['value'], 'backward')

    def test_shenfeng_zero_day_count_empty_state(self):
        timeline = build_timeline('ADV001-zero-jie-2000',
                                  include_shenfeng=True)
        view = dayun_timeline_view(timeline, method='shenfeng')
        self.assertEqual(view['status'], 'unresolved')
        self.assertEqual(view['reason'],
                         'zero_day_count_not_exemplified_in_text')
        codes = [n['code'] for n in view['notices']]
        self.assertIn('shenfeng_zero_day_count', codes)
        self.assertTrue(all(e['start_interval'] is None
                            for e in view['entries']))

    def test_approximate_precision_notice_and_widened_interval(self):
        timeline = build_timeline('P1-unknown-precision-1958')
        view = dayun_timeline_view(timeline, method='sanming')
        self.assertTrue(view['duration']['approximate'])
        self.assertIn('approximation_basis', view['duration'])
        self.assertEqual(view['duration']['interval_days'],
                         {'min_days': 2830, 'max_days': 2860,
                          'max_inclusive': False})
        self.assertIn('approximate_birth_time',
                      [n['code'] for n in view['notices']])


class ForbiddenFieldTests(unittest.TestCase):
    FORBIDDEN = {'start_date', 'end_date', 'start_age', 'end_age',
                 'handover_datetime', 'start_datetime', 'age_years',
                 'current_age'}

    def _views(self):
        timeline = build_timeline('Q1-forward-male-1958',
                                  include_shenfeng=True)
        return [dayun_timeline_view(timeline, method='sanming'),
                dayun_timeline_view(timeline, method='shenfeng')]

    def test_no_single_point_or_age_fields_anywhere(self):
        for view in self._views():
            keys = set(_walk_keys(view))
            self.assertFalse(keys & self.FORBIDDEN)
            age_keys = {k for k in keys if 'age' in k}
            self.assertEqual(age_keys, {'age_presentation'})
            self.assertEqual(view['age_presentation'], 'not_presented')

    def test_governance_flags(self):
        for view in self._views():
            self.assertIs(view['research_only'], True)
            self.assertIs(view['public_enabled'], False)
            self.assertIs(view['ai_enabled'], False)


class FailClosedTests(unittest.TestCase):
    def setUp(self):
        self.timeline = build_timeline('Q1-forward-male-1958',
                                       include_shenfeng=True)

    def test_bad_method(self):
        with self.assertRaises(ValueError):
            dayun_timeline_view(self.timeline, method='modern')

    def test_wrong_variant(self):
        forged = copy.deepcopy(self.timeline)
        forged['variant'] = 'dayun-timeline-view-v1'
        with self.assertRaises(ValueError):
            dayun_timeline_view(forged, method='sanming')

    def test_promoted_flags_rejected(self):
        for key, value in (('public_enabled', True),
                           ('ai_enabled', True),
                           ('research_only', False)):
            forged = copy.deepcopy(self.timeline)
            forged[key] = value
            with self.subTest(key=key):
                with self.assertRaises(ValueError):
                    dayun_timeline_view(forged, method='sanming')

    def test_tampered_direction_rejected(self):
        forged = copy.deepcopy(self.timeline)
        forged['direction']['direction'] = 'backward'
        with self.assertRaises(ValueError):
            dayun_timeline_view(forged, method='sanming')

    def test_missing_alignment_interval_rejected(self):
        forged = copy.deepcopy(self.timeline)
        forged['sequence_time_alignment'][0]['start_interval'] = None
        with self.assertRaises(ValueError):
            dayun_timeline_view(forged, method='sanming')

    def test_tampered_shenfeng_quote_set_rejected(self):
        forged = copy.deepcopy(self.timeline)
        forged['direction']['evidence_quotes'] = [
            q for q in forged['direction']['evidence_quotes']
            if q['id'] != 'sf_ex3']
        with self.assertRaises(ValueError):
            dayun_timeline_view(forged, method='shenfeng')

    def test_convenience_entry_rejects_missing_role_first(self):
        with self.assertRaises(ValueError):
            classical_dayun_timeline_views(
                '1958-08-15T19:30:00+08:00', zone='Asia/Shanghai',
                traditional_role=None)


class ProjectionStripTests(unittest.TestCase):
    def test_view_keys_never_reach_public_projection(self):
        payload = {
            'evidence': {},
            'rule_matches': [],
            'trace': [],
            'chart': {'dayun_timeline_view': {'variant': VIEW_VARIANT}},
            'result': {'dayun_timeline_views': {'sanming': {}}},
        }
        projected = project_execution(payload)
        self.assertNotIn('dayun_timeline_view', projected['chart'])
        self.assertNotIn('dayun_timeline_views', projected['result'])


if __name__ == '__main__':
    unittest.main()
