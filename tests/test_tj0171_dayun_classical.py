"""TJ-017.1 dayun classical-evidence public contract tests.

Public-safe by design: the quote/rule tables, the pure direction and
conversion functions, real pinned-provider measurements and forged-input
rejection need no sealed data. Verbatim equality of every registered
quote against the pinned snapshot texts themselves lives only in the
sealed companion test_tj0171_dayun_classical_sealed.py (offline
acceptance, NOT public CI), following the TJ-013 precedents.

Golden expectations are derived from the classical texts themselves
(the worked examples in 《三命通会·论大运》 and 《神峰通考·起大运法》),
never back-filled from implementation output.
"""
import copy
import json
from datetime import datetime, timedelta
from pathlib import Path
import unittest

from tianji_kb.bazi_dayun_classical import (
    CONSUMER_CONVENTIONS, DIRECTION_VARIANT, CONVERSION_VARIANT,
    EXCLUDED_SPANS, LIMITATIONS, QUOTES, SANMING_SECTION,
    SANMING_SNAPSHOT_SHA256, SHENFENG_CONVERSION_VARIANT, SHENFENG_SECTION,
    classical_direction, compare_with_modern_candidate,
    sanming_convert_elapsed, sanming_convert_measurement,
    shenfeng_convert_days, validate_classical_direction,
)
from tianji_kb.bazi_dayun_direction import traditional_direction
from tianji_kb.bazi_dayun_jie import adjacent_jie_distance
from tianji_kb.foundations import CYCLE

ROOT = Path(__file__).resolve().parents[1]
GOLDEN = json.loads(
    (ROOT / 'tests/golden_tj0171_dayun_classical.json').read_text('utf-8'))

AGE_KEYS = {'age', 'start_age', 'end_age', 'age_years', '岁数', '年龄'}
POINT_KEYS = {'handover_datetime', 'handover_date', 'start_date',
              'end_date', 'start_datetime'}


def _keys(node):
    if isinstance(node, dict):
        for key, value in node.items():
            yield key
            yield from _keys(value)
    elif isinstance(node, list):
        for item in node:
            yield from _keys(item)


def _assert_interval_only(test, out):
    keys = set(_keys(out))
    test.assertFalse(POINT_KEYS & keys,
                     'single-point handover fields are forbidden')
    # No age-valued field may exist anywhere. ('age_counting' is the
    # consumer-conventions label documenting the refusal itself, not a
    # value field, and is the single allowed exception.)
    test.assertFalse(AGE_KEYS & keys)
    for key in keys:
        test.assertNotIn('岁', key)
    test.assertTrue(out['research_only'])
    test.assertFalse(out['public_enabled'])
    test.assertFalse(out['ai_enabled'])


class QuoteTableTests(unittest.TestCase):
    def test_quotes_match_golden_transcription(self):
        golden = {q['id']: q for q in GOLDEN['quotes']}
        self.assertEqual({q['id'] for q in QUOTES}, set(golden))
        for quote in QUOTES:
            want = golden[quote['id']]
            self.assertEqual(quote['quote'], want['quote'])
            self.assertEqual(quote['locator'], want['locator'])
            self.assertEqual(quote['source_id'], want['source_id'])
            self.assertEqual(quote['role'], want['role'])
            self.assertEqual(
                quote['locator']['char_end'] - quote['locator']['char_start'],
                len(quote['quote']))
        encoded = [q['id'] for q in QUOTES if q['role'] == 'encoded_rule']
        self.assertEqual(encoded, ['direction_rule'],
                         'exactly one quote is encoded as the direction rule')

    def test_excluded_spans_match_golden(self):
        golden = {e['id']: e for e in GOLDEN['excluded_spans']}
        mine = {e['id']: e for e in EXCLUDED_SPANS}
        self.assertEqual(set(mine), set(golden))
        for span_id, span in mine.items():
            self.assertEqual(span['quote'], golden[span_id]['quote'])
            self.assertEqual(span['locator'], golden[span_id]['locator'])
        ids = {e['id'] for e in GOLDEN['registered_not_golden']}
        self.assertEqual(ids, {'sf_ex2_conversion', 'leap_handover_subrule',
                               'handover_example_full_arithmetic'})

    def test_pua_annotations_are_mapped_not_silent(self):
        annotated = [q for q in QUOTES if 'pua_annotations' in q]
        self.assertEqual({q['id'] for q in annotated},
                         {'handover_example', 'handover_decade'})
        for quote in annotated:
            for note in quote['pua_annotations']:
                offset = note['char_offset']
                self.assertEqual(quote['quote'][offset - quote['locator']
                                                ['char_start']], '')
                self.assertEqual(note['mapped_reading'], '算')
                self.assertEqual(note['mapping_status'], 'confirmed')
            # The mapped reading differs from the verbatim quote exactly
            # at the annotated PUA positions, nowhere else.
            verbatim, mapped = quote['quote'], quote['mapped_reading_text']
            self.assertEqual(len(verbatim), len(mapped))
            diffs = [i for i, (a, b) in enumerate(zip(verbatim, mapped))
                     if a != b]
            base = quote['locator']['char_start']
            self.assertEqual(
                diffs, [n['char_offset'] - base
                        for n in quote['pua_annotations']])
            for i in diffs:
                self.assertEqual(mapped[i], '算')

    def test_sections_match_golden(self):
        sections = {s['id']: s for s in GOLDEN['sections']}
        sanming = sections['sanming_lun_dayun']['locator']
        self.assertEqual(SANMING_SECTION['char_start'],
                         sanming['char_start'])
        self.assertEqual(SANMING_SECTION['char_end'], sanming['char_end'])
        shenfeng = sections['shenfeng_qi_dayun_fa']['locator']
        self.assertEqual(SHENFENG_SECTION['char_start'],
                         shenfeng['char_start'])
        self.assertEqual(SHENFENG_SECTION['char_end'],
                         shenfeng['char_end'])


class DirectionGoldenTests(unittest.TestCase):
    def test_text_cases(self):
        for case in GOLDEN['direction_cases']:
            with self.subTest(case=case['id']):
                out = classical_direction(
                    case['year_ganzhi'],
                    traditional_role=case['traditional_role'])
                for field, want in case['expected'].items():
                    self.assertEqual(out[field], want)
                self.assertEqual(out['variant'], DIRECTION_VARIANT)
                self.assertTrue(validate_classical_direction(out))
                _assert_interval_only(self, out)

    def test_full_agreement_with_modern_candidate(self):
        # 审源裁定零分歧： all 60 year ganzhi x both roles.
        checked = 0
        for ganzhi in CYCLE:
            for role in ('male', 'female'):
                classical = classical_direction(
                    ganzhi, traditional_role=role)
                candidate = traditional_direction(
                    ganzhi, traditional_role=role)
                self.assertEqual(classical['direction'],
                                 candidate['direction'], (ganzhi, role))
                self.assertEqual(
                    classical['counting_target'],
                    'future_jie' if candidate['direction'] == 'forward'
                    else 'past_jie')
                checked += 1
        self.assertEqual(checked, 120)

    def test_compare_keeps_both_registrations_unmerged(self):
        out = compare_with_modern_candidate('甲子', traditional_role='male')
        self.assertTrue(out['agreement'])
        self.assertEqual(out['classical']['variant'], DIRECTION_VARIANT)
        self.assertEqual(out['modern_candidate']['variant'],
                         'bazi-dayun-year-stem-traditional-role-research-v1')
        self.assertEqual(out['primary_registration'], 'classical')

    def test_role_must_be_explicit_and_never_inferred(self):
        with self.assertRaises(ValueError):
            classical_direction('甲子', traditional_role=None)
        with self.assertRaises(ValueError):
            classical_direction('甲子', traditional_role='Male')
        with self.assertRaises(ValueError):
            classical_direction('甲子', traditional_role='')
        with self.assertRaises(ValueError):
            classical_direction('甲丑', traditional_role='male')
        with self.assertRaises(ValueError):
            classical_direction(42, traditional_role='male')

    def test_forged_direction_results_fail_closed(self):
        good = classical_direction('乙丑', traditional_role='female')
        self.assertTrue(validate_classical_direction(copy.deepcopy(good)))
        for mutate in (
                lambda r: r.update(public_enabled=True),
                lambda r: r.update(ai_enabled=False, research_only=False),
                lambda r: r.update(direction='backward'),
                lambda r: r.update(counting_target='past_jie'),
                lambda r: r.update(direction_rule_match='bazi.phase2.dayun'),
                lambda r: r.update(phase2_allowed=True),
                lambda r: r.update(evidence_binding='bound'),
                lambda r: r.update(handover_intervals=[]),
                lambda r: r['rule_quote'].update(quote='伪造规则句'),
                lambda r: r['evidence_quotes'].pop(),
        ):
            forged = copy.deepcopy(good)
            mutate(forged)
            with self.assertRaises(ValueError):
                validate_classical_direction(forged)


class ConversionGoldenTests(unittest.TestCase):
    def test_sanming_text_cases(self):
        for case in GOLDEN['conversion_cases']:
            with self.subTest(case=case['id']):
                out = sanming_convert_elapsed(
                    case['input']['elapsed_seconds'],
                    birth_time_precision=case['input']
                    ['birth_time_precision'])
                want = case['expected']
                self.assertEqual(out['status'], want['status'])
                if want['status'] != 'converted':
                    self.assertEqual(out['reason'], want['reason'])
                    continue
                interval = out['duration_interval_days']
                self.assertEqual(interval['min_days'], want['min_days'])
                self.assertEqual(interval['max_days'], want['max_days'])
                self.assertEqual(interval['max_inclusive'],
                                 want['max_inclusive'])
                self.assertEqual(out['counting']['whole_shichen_counted'],
                                 want['whole_shichen_counted'])
                self.assertEqual(
                    out['counting']['sub_shichen_remainder_seconds'],
                    want['sub_shichen_remainder_seconds'])
                decomp = out['duration_decomposition']
                for field in ('whole_year_units', 'remainder_shichen',
                              'remainder_days',
                              'remainder_months_of_30_days'):
                    self.assertEqual(decomp[field], want[field],
                                     (case['id'], field))
                self.assertEqual(out['approximate'], want['approximate'])
                self.assertFalse(out['rounding_applied'])
                _assert_interval_only(self, out)

    def test_shenfeng_text_cases(self):
        for case in GOLDEN['shenfeng_conversion_cases']:
            with self.subTest(case=case['id']):
                out = shenfeng_convert_days(
                    case['input']['whole_days'],
                    direction=case['input']['direction'])
                want = case['expected']
                self.assertEqual(out['status'], want['status'])
                if want['status'] != 'converted':
                    self.assertEqual(out['reason'], want['reason'])
                    continue
                interval = out['duration_interval_days']
                self.assertEqual(
                    (interval['min_days'], interval['max_days'],
                     interval['max_inclusive']),
                    (want['min_days'], want['max_days'],
                     want['max_inclusive']))
                self.assertEqual(out['text_result_days'],
                                 want['text_result_days'])
                self.assertEqual(out['variant'],
                                 SHENFENG_CONVERSION_VARIANT)
                _assert_interval_only(self, out)

    def test_two_methods_are_never_merged(self):
        sanming = sanming_convert_elapsed(453600)
        shenfeng = shenfeng_convert_days(5, direction='forward')
        self.assertEqual(sanming['variant'], CONVERSION_VARIANT)
        self.assertEqual(sanming['method'], 'sanming_shichen_level')
        self.assertEqual(shenfeng['method'], 'shenfeng_day_level')
        self.assertNotEqual(sanming['variant'], shenfeng['variant'])
        self.assertIn('分立', ''.join(LIMITATIONS))

    def test_rounding_is_refused_not_applied(self):
        for rounding in ('nearest_year', 'floor', 'ceil', 'round_half_up'):
            out = sanming_convert_elapsed(453600, rounding=rounding)
            self.assertEqual(out['status'], 'unresolved')
            out = shenfeng_convert_days(30, direction='forward',
                                        rounding=rounding)
            self.assertEqual(out['status'], 'unresolved')

    def test_anti_rounding_arithmetic_sweep(self):
        # For every whole-shichen count, the duration is exactly
        # count x 10 days: surplus/deficit carries linearly, never
        # snaps to a whole-year multiple (the text's prohibition).
        for count in range(1, 400):
            out = sanming_convert_elapsed(count * 7200)
            interval = out['duration_interval_days']
            self.assertEqual(interval['min_days'], count * 10)
            self.assertEqual(interval['max_days'], count * 10)
            self.assertTrue(interval['max_inclusive'])

    def test_fail_closed_inputs(self):
        with self.assertRaises(ValueError):
            sanming_convert_elapsed(-1)
        with self.assertRaises(ValueError):
            sanming_convert_elapsed(453600.5)
        with self.assertRaises(ValueError):
            sanming_convert_elapsed(True)
        with self.assertRaises(ValueError):
            sanming_convert_elapsed(100, birth_time_precision='minute')
        with self.assertRaises(ValueError):
            shenfeng_convert_days(-3, direction='forward')
        with self.assertRaises(ValueError):
            shenfeng_convert_days(30, direction='sideways')
        with self.assertRaises(ValueError):
            shenfeng_convert_days(30.0, direction='forward')


class MeasurementContractTests(unittest.TestCase):
    def test_real_measurement_interval_contract(self):
        measured = adjacent_jie_distance(
            '1958-08-15T19:30:00+08:00', 'forward',
            expected_month_ganzhi='庚申')
        out = sanming_convert_measurement(measured, periods=3)
        self.assertEqual(out['status'], 'converted')
        self.assertEqual(out['direction'], 'forward')
        self.assertEqual(out['counting_target'], 'future_jie')
        self.assertEqual(out['counted_jie']['name'], '白露')
        # Independent recomputation from the measured seconds.
        whole, rem = divmod(measured['elapsed_seconds'], 7200)
        self.assertEqual(out['duration_interval_days']['min_days'],
                         whole * 10)
        self.assertEqual(out['duration_interval_days']['max_days'],
                         whole * 10 + (10 if rem else 0))
        birth = datetime.fromisoformat('1958-08-15T19:30:00+08:00')
        rows = out['handover_intervals']
        self.assertEqual([r['period_index'] for r in rows], [1, 2, 3])
        first = rows[0]
        self.assertEqual(datetime.fromisoformat(first['earliest']),
                         birth + timedelta(
                             days=out['duration_interval_days']
                             ['min_days']))
        self.assertEqual(datetime.fromisoformat(first['latest']),
                         birth + timedelta(
                             days=out['duration_interval_days']
                             ['max_days']))
        # Decade shifts move both endpoints by exactly 10 calendar
        # years each; the width never grows.
        width = timedelta(days=out['duration_interval_days']['max_days']
                          - out['duration_interval_days']['min_days'])
        for row in rows:
            earliest = datetime.fromisoformat(row['earliest'])
            latest = datetime.fromisoformat(row['latest'])
            self.assertEqual(latest - earliest, width)
        first_earliest = datetime.fromisoformat(first['earliest'])
        second = datetime.fromisoformat(rows[1]['earliest'])
        self.assertEqual((second.year, second.month, second.day),
                         (first_earliest.year + 10, first_earliest.month,
                          first_earliest.day))
        _assert_interval_only(self, out)

    def test_backward_measurement_counts_past_jie(self):
        measured = adjacent_jie_distance(
            '1949-01-04T09:30:00+08:00', 'backward',
            expected_month_ganzhi='甲子')
        out = sanming_convert_measurement(measured)
        self.assertEqual(out['status'], 'converted')
        self.assertEqual(out['counting_target'], 'past_jie')
        self.assertEqual(out['counted_jie']['name'],
                         measured['selected_jie']['name'])
        self.assertEqual(out['counted_jie']['name'], '大雪')

    def test_zero_distance_measurement_is_refused(self):
        # TJ-016.2 ADV-001 instant: birth exactly at 立春.
        measured = adjacent_jie_distance(
            '2000-02-04T20:40:24+08:00', 'backward',
            expected_month_ganzhi='戊寅')
        self.assertTrue(measured['zero_distance'])
        out = sanming_convert_measurement(measured)
        self.assertEqual(out['status'], 'unresolved')
        self.assertEqual(out['reason'],
                         'zero_jie_boundary_convention_unreviewed')
        self.assertIsNone(out['duration_interval_days'])
        self.assertIsNone(out['handover_intervals'])

    def test_forged_measurements_fail_closed(self):
        measured = adjacent_jie_distance(
            '1958-08-15T19:30:00+08:00', 'forward',
            expected_month_ganzhi='庚申')
        tampered = copy.deepcopy(measured)
        tampered['elapsed_seconds'] += 7200
        with self.assertRaises(ValueError):
            sanming_convert_measurement(tampered)
        forged = copy.deepcopy(measured)
        forged['start_age'] = 7
        with self.assertRaises(ValueError):
            sanming_convert_measurement(forged)
        with self.assertRaises(ValueError):
            sanming_convert_measurement({'variant': 'forged'})
        with self.assertRaises(ValueError):
            sanming_convert_measurement(measured, periods=0)
        with self.assertRaises(ValueError):
            sanming_convert_measurement(measured, periods=13)


class RegistrationAndIsolationTests(unittest.TestCase):
    def test_sources_and_lineages_registered(self):
        sources = json.loads((ROOT / 'config/knowledge_sources.json')
                             .read_text('utf-8'))['sources']
        entry = next(s for s in sources
                     if s['source_id'] == 'bazi.source.sanmingtonghui')
        self.assertEqual(entry['evidence_level'], 'C')
        self.assertEqual(entry['kind'], 'classical')
        self.assertTrue(entry['public_domain'])
        self.assertEqual(entry['sha256'], SANMING_SNAPSHOT_SHA256)
        self.assertEqual(entry['content_path'],
                         'data/quarantine/public_domain_snapshots/'
                         'daizhigev20/sanming_tonghui.txt')
        self.assertIn('quarantine_only', entry['review_scope'])
        self.assertIn('59080', entry['review_scope'])
        audit = json.loads((ROOT / 'config/phase2_source_audit.json')
                           .read_text('utf-8'))
        lineage = {r['source_id']: r for r in audit['lineages']}
        self.assertEqual({s['source_id'] for s in sources}, set(lineage),
                         'every registered source needs exactly one lineage')
        row = lineage['bazi.source.sanmingtonghui']
        self.assertEqual(row['grade_ceiling'], 'C')
        self.assertEqual(row['edition_status'], 'unverified')
        # 神峰 review_scope extended, same source (no census change).
        shenfeng = next(s for s in sources
                        if s['source_id'] == 'bazi.source.shenfeng')
        self.assertIn('起大运法', shenfeng['review_scope'])
        self.assertIn('85001', shenfeng['review_scope'])

    def test_variants_not_wired_into_production_paths(self):
        # Batch transition (E0346, governance dayun Sanming-segment
        # promotion): the TJ-017.1-era blanket isolation (no
        # production path references the classical module at all)
        # is superseded for the Sanming segment ONLY — direction
        # and Sanming conversion are registered (Phase1 r038/r039,
        # Phase2 bazi.phase2.dayun_classical_direction /
        # bazi.phase2.dayun_sanming_conversion) and execute through
        # chart()'s gated trace steps. The isolation contract now
        # pins the exact gated shape instead: engine.py and
        # public_projection.py still never name the module, the
        # variant id or handover internals; bazi_chart.py imports
        # the module exactly once, hardcodes no variant id, never
        # touches handover internals, and wires only the two
        # registered Sanming steps — the Shenfeng conversion
        # function is NOT wired anywhere (its segment stays
        # pending).
        for rel in ('src/tianji_kb/engine.py',
                    'src/tianji_kb/public_projection.py'):
            text = (ROOT / rel).read_text('utf-8')
            self.assertNotIn('bazi_dayun_classical', text, rel)
            self.assertNotIn('dayun-direction-classical-v1', text, rel)
            self.assertNotIn('handover_intervals', text, rel)
        chart_text = (ROOT / 'src/tianji_kb/operations/bazi_chart.py'
                      ).read_text('utf-8')
        self.assertEqual(chart_text.count('bazi_dayun_classical'), 1)
        self.assertIn('from ..bazi_dayun_classical import',
                      chart_text)
        self.assertNotIn('dayun-direction-classical-v1', chart_text)
        self.assertNotIn('handover_intervals', chart_text)
        self.assertIn('bazi.phase2.dayun_classical_direction',
                      chart_text)
        self.assertIn('bazi.phase2.dayun_sanming_conversion',
                      chart_text)
        self.assertNotIn('shenfeng_convert_days', chart_text)

    def test_consumer_conventions_recorded(self):
        self.assertIn('禁止先把区间折算成某个「岁数」再调用',
                      CONSUMER_CONVENTIONS['tj0172'])
        self.assertIn('产品约定', CONSUMER_CONVENTIONS['tj0173'])
        self.assertIn('refuse_age_counting_conversion',
                      CONSUMER_CONVENTIONS['age_counting'])

    def test_golden_consumer_conventions_match_module(self):
        self.assertEqual(GOLDEN['consumer_conventions'],
                         CONSUMER_CONVENTIONS)


if __name__ == '__main__':
    unittest.main()
