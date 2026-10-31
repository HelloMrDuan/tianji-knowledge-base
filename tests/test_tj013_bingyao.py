"""TJ-013 bingyao (病药) public contract tests for the shenfeng research Variant.

Public-safe by design: the rule table, the pure lookup, the engine
research gate, forged-trace rejection and the public-projection strip
need no sealed data. Verbatim equality of every registered quote
against the pinned snapshot texts themselves, and real-chart coverage
of the Golden cases, live only in the sealed companion
test_tj013_bingyao_sealed.py (offline acceptance, NOT public CI),
following the test_tj0131_tiaohou precedent.
"""
import copy
import itertools
import json
from pathlib import Path
import unittest

from tianji_kb.bazi_bingyao import (
    QUOTES, RULE, RULES, SNAPSHOT_SHA256, SOURCE_ID, VARIANT,
    bingyao_assessment, bingyao_lookup,
)
from tianji_kb.engine import execute
from tianji_kb.public_projection import project_execution

ROOT = Path(__file__).resolve().parents[1]
GOLDEN = json.loads((ROOT / 'tests/golden_tj013_bingyao.json').read_text('utf-8'))
VERDICT_KEYS = {'score', 'rating', 'fortune', 'fortune_verdict', 'auspicious',
                'inauspicious', 'luck', '吉凶', '评分', '喜用神', '用神',
                'useful_god', 'favorable_god', 'disease_free', '无病'}
ALL_GODS = ('比肩', '劫财', '食神', '伤官', '偏财', '正财',
            '七杀', '正官', '偏印', '正印')


def _keys(node):
    if isinstance(node, dict):
        for key, value in node.items():
            yield key
            yield from _keys(value)
    elif isinstance(node, list):
        for item in node:
            yield from _keys(item)


def _facts(rows):
    return [{'pillar': p, 'stem': s, 'ten_god': g} for p, s, g in rows]


class RuleTableTests(unittest.TestCase):
    def test_rule_and_quotes_match_golden_transcription(self):
        self.assertEqual(VARIANT, 'bingyao-shenfeng-v1')
        self.assertEqual(len(RULES), 2)
        self.assertEqual(len(GOLDEN['rules']), 2)
        self.assertIs(RULE, RULES[0],
                      'the first-slice RULE alias must stay the wealth pair')
        for rule, want in zip(RULES, GOLDEN['rules']):
            self.assertEqual(rule['pair_id'], want['pair_id'])
            self.assertEqual(rule['id'], want['id'])
            self.assertEqual(rule['quote'], want['quote'])
            self.assertEqual(rule['quote_locator'], want['quote_locator'])
            self.assertEqual(rule['section'], want['section'])
            self.assertEqual(tuple(rule['subject_gods']),
                             tuple(want['subject_gods']))
            self.assertEqual(tuple(rule['disease_gods']),
                             tuple(want['disease_gods']))
            self.assertEqual(tuple(rule['medicine_gods']),
                             tuple(want['medicine_gods']))
        # The wealth pair's rule fields are the first slice's, unchanged.
        self.assertEqual(RULES[0]['id'], 'shenfeng.wealth_peer_officer')
        self.assertEqual(RULES[1]['id'], 'shenfeng.foodwound_seal_wealth')
        self.assertEqual(RULES[1]['subject_gods'], ('食神', '伤官'))
        self.assertEqual(RULES[1]['disease_gods'], ('正印', '偏印'))
        self.assertEqual(RULES[1]['medicine_gods'], ('正财', '偏财'))
        golden_quotes = {q['id']: q for q in GOLDEN['quotes']}
        self.assertEqual({q['id'] for q in QUOTES}, set(golden_quotes))
        for quote in QUOTES:
            want = golden_quotes[quote['id']]
            self.assertEqual(quote['quote'], want['quote'])
            self.assertEqual(quote['locator'], want['locator'])
            self.assertEqual(quote['source_id'], want['source_id'])
            self.assertLessEqual(len(quote['quote']), 120)
            self.assertEqual(
                quote['locator']['char_end'] - quote['locator']['char_start'],
                len(quote['quote']))
        encoded = [q for q in QUOTES if q['role'] == 'encoded_rule']
        self.assertEqual([q['id'] for q in encoded],
                         ['wealth_pair', 'food_pair'],
                         'exactly the two definition-section pairs are encoded')

    def test_both_definition_pairs_are_encoded(self):
        # 示例三 (食伤对) is encoded as the second pair in this slice;
        # the earth example and the four-diseases section stay unencoded.
        food = next(q for q in QUOTES if q['id'] == 'food_pair')
        self.assertEqual(food['role'], 'encoded_rule')
        earth = next(q for q in QUOTES if q['id'] == 'earth_example')
        self.assertEqual(earth['role'], 'registered_not_encoded')


class LookupGoldenTests(unittest.TestCase):
    def test_all_golden_cases(self):
        for case in GOLDEN['cases']:
            with self.subTest(case=case['id']):
                out = bingyao_lookup(case['day_master'], case['visible_gods'])
                expected = case['expected']
                self.assertEqual(out['status'], expected['status'])
                self.assertIsNone(out['determination'])
                self.assertEqual(out['medicine_effect_status'], 'unadjudicated')
                if expected['status'] == 'not_triggered':
                    self.assertEqual(out['not_triggered_reason'],
                                     expected['not_triggered_reason'])
                    self.assertIsNone(out['disease_candidate'])
                    self.assertIsNone(out['medicine_candidate'])
                    self.assertIsNone(out['medicine_status'])
                    continue
                self.assertEqual(out['disease_candidate']['gods'],
                                 expected['disease_gods'])
                self.assertEqual(out['medicine_status'],
                                 expected['medicine_status'])
                if expected['medicine_status'] == 'candidate_present':
                    self.assertEqual(out['medicine_candidate']['gods'],
                                     expected['medicine_gods'])
                    self.assertEqual(
                        out['medicine_candidate']['structural_relation'],
                        'medicine_element_controls_disease_element')
                    self.assertEqual(out['medicine_candidate']['medicine_element'],
                                     expected['medicine_element'])
                    self.assertEqual(out['medicine_candidate']['disease_element'],
                                     expected['disease_element'])
                else:
                    self.assertIsNone(out['medicine_candidate'])
                self._assert_pairs(case, out)

    def _assert_pair(self, pair, expected):
        self.assertEqual(pair['status'], expected['status'])
        self.assertIsNone(pair['determination'])
        self.assertEqual(pair['medicine_effect_status'], 'unadjudicated')
        if 'subject_gods' in expected:
            self.assertEqual(pair['subject']['gods'], expected['subject_gods'])
        if expected['status'] == 'not_triggered':
            self.assertEqual(pair['not_triggered_reason'],
                             expected['not_triggered_reason'])
            self.assertIsNone(pair['disease_candidate'])
            self.assertIsNone(pair['medicine_candidate'])
            self.assertIsNone(pair['medicine_status'])
            return
        self.assertEqual(pair['disease_candidate']['gods'],
                         expected['disease_gods'])
        self.assertEqual(pair['medicine_status'], expected['medicine_status'])
        if expected['medicine_status'] == 'candidate_present':
            self.assertEqual(pair['medicine_candidate']['gods'],
                             expected['medicine_gods'])
            self.assertEqual(
                pair['medicine_candidate']['structural_relation'],
                'medicine_element_controls_disease_element')
            self.assertEqual(pair['medicine_candidate']['medicine_element'],
                             expected['medicine_element'])
            self.assertEqual(pair['medicine_candidate']['disease_element'],
                             expected['disease_element'])
        else:
            self.assertIsNone(pair['medicine_candidate'])

    def _assert_pairs(self, case, out):
        pairs = out['pairs']
        self.assertEqual([p['pair_id'] for p in pairs],
                         ['wealth_peer_officer', 'foodwound_seal_wealth'])
        first = pairs[0]
        # The top level IS the first pair's statement, field for field.
        self.assertEqual(first['status'], out['status'])
        self.assertEqual(first['subject'], out['subject'])
        self.assertEqual(first['disease_candidate'],
                         out['disease_candidate'])
        self.assertEqual(first['medicine_candidate'],
                         out['medicine_candidate'])
        self.assertEqual(first['medicine_status'], out['medicine_status'])
        self.assertEqual(first['rule']['id'], out['rule']['id'])
        if first['status'] == 'not_triggered':
            self.assertEqual(first['not_triggered_reason'],
                             out['not_triggered_reason'])
        second = pairs[1]
        if 'expected_pair2' in case:
            self._assert_pair(second, case['expected_pair2'])
            self.assertEqual(second['rule']['id'],
                             'shenfeng.foodwound_seal_wealth')
        else:
            # First-slice cases: the second pair's expectation is pinned
            # in the golden regression map (hand-derived: none of the
            # seven charts shows both 食伤 and 印).
            regression = GOLDEN['pair2_regression_on_first_slice_cases']
            want = regression[case['id']]
            self.assertEqual(second['status'], want['status'])
            self.assertEqual(second['not_triggered_reason'],
                             want['not_triggered_reason'])
            self.assertIsNone(second['disease_candidate'])
            self.assertIsNone(second['medicine_candidate'])
            self.assertIsNone(second['determination'])
            self.assertEqual(second['medicine_effect_status'],
                             'unadjudicated')

    def test_no_verdict_or_merged_useful_god_fields_anywhere(self):
        for case in GOLDEN['cases']:
            out = bingyao_lookup(case['day_master'], case['visible_gods'])
            self.assertFalse(VERDICT_KEYS & set(_keys(out)))
            self.assertTrue(out['research_only'])
            self.assertFalse(out['public_enabled'])
            self.assertFalse(out['ai_enabled'])
            # E0348 (Shenfeng Canonical expansion): the Variant is
            # registered (Phase1 bazi.rule.r040 / Phase2
            # bazi.phase2.bingyao_assessment); the binding discloses
            # the registration while every verdict guard above is
            # unchanged.
            self.assertEqual(out['evidence_binding'],
                             'registered_phase1_phase2')


class NeverNoDiseaseSweepTests(unittest.TestCase):
    def test_exhaustive_visible_god_sweep_never_yields_a_verdict(self):
        # Every assignment of ten-god classes to the three visible
        # pillars, for every day master: the only statuses are
        # triggered / not_triggered, determination is always None and
        # medicine efficacy is always unadjudicated. There is no code
        # path that can output 「无病」 or a useful-god conclusion.
        stems = ('甲', '乙', '丙')
        checked = 0
        for day_master in '甲乙丙丁戊己庚辛壬癸':
            for combo in itertools.product(ALL_GODS, repeat=3):
                facts = _facts(zip(('year', 'month', 'hour'), stems, combo))
                out = bingyao_lookup(day_master, facts)
                self.assertIn(out['status'], ('triggered', 'not_triggered'))
                self.assertIsNone(out['determination'])
                self.assertEqual(out['medicine_effect_status'], 'unadjudicated')
                self.assertNotIn('无病', json.dumps(
                    {'status': out['status'],
                     'determination': out['determination']},
                    ensure_ascii=False))
                self.assertFalse(VERDICT_KEYS & set(_keys(out)))
                # Both pairs, independently: only triggered /
                # not_triggered, determination always None, efficacy
                # always unadjudicated — and never both triggered at
                # once (the two pairs need four distinct visible god
                # classes; only three visible stems exist).
                self.assertEqual(len(out['pairs']), 2)
                triggered_pairs = 0
                for pair in out['pairs']:
                    self.assertIn(pair['status'],
                                  ('triggered', 'not_triggered'))
                    self.assertIsNone(pair['determination'])
                    self.assertEqual(pair['medicine_effect_status'],
                                     'unadjudicated')
                    triggered_pairs += pair['status'] == 'triggered'
                self.assertLessEqual(triggered_pairs, 1)
                checked += 1
        self.assertEqual(checked, 10 * 10 ** 3)


class AbstainAndFailClosedTests(unittest.TestCase):
    def test_missing_or_malformed_facts_fail_closed(self):
        good = _facts((('year', '戊', '偏财'), ('month', '庚', '七杀'),
                       ('hour', '甲', '比肩')))
        with self.assertRaises(ValueError):
            bingyao_lookup('甲', good[:2])
        with self.assertRaises(ValueError):
            bingyao_lookup('甲', good + [_facts((('hour', '甲', '比肩'),))[0]])
        with self.assertRaises(ValueError):
            bingyao_lookup(None, good)
        with self.assertRaises(ValueError):
            bingyao_lookup('猫', good)
        bad = _facts((('year', '戊', '偏财'), ('month', '庚', '七杀'),
                      ('day', '甲', '日主')))
        with self.assertRaises(ValueError):
            bingyao_lookup('甲', bad)
        bad = _facts((('year', '戊', '偏财'), ('month', '庚', '七杀'),
                      ('hour', '甲', '财星')))
        with self.assertRaises(ValueError):
            bingyao_lookup('甲', bad)
        bad = _facts((('year', '戊', '偏财'), ('month', '庚', '七杀'),
                      ('hour', '猫', '比肩')))
        with self.assertRaises(ValueError):
            bingyao_lookup('甲', bad)

    def test_hidden_only_gods_cannot_trigger(self):
        # The lookup contract has no hidden-stem input at all: a god
        # attested only in hidden stems is invisible to the rule (S3).
        # Chart-level proof lives in the sealed Golden boundary cases.
        out = bingyao_lookup('甲', _facts((('year', '戊', '偏财'),
                                          ('month', '庚', '七杀'),
                                          ('hour', '辛', '正官'))))
        self.assertEqual(out['status'], 'not_triggered')
        self.assertEqual(out['not_triggered_reason'], 'peer_god_not_visible')


class _StubTrace:
    def __init__(self, steps, evidence=None, domain='bazi',
                 variant='ziping-structural-v1'):
        self.domain = domain
        self.variant = variant
        self.steps = steps
        self.evidence = evidence or {}


def _step(rule_id, output, evidence_ids=('e1',)):
    return {'rule_id': rule_id, 'inputs': {}, 'output': output,
            'evidence_ids': list(evidence_ids)}


def _consistent_steps():
    ganzhi = ['戊戌', '庚申', '甲子', '甲戌']
    gods = ['偏财', '七杀', '日主', '比肩']
    pillars = _step('bazi.phase2.pillars',
                    {'ganzhi': ganzhi, 'day_master': {'stem': '甲'}})
    ten = _step('bazi.phase2.ten_gods', [
        {'pillar': name, 'stem': g[0], 'ten_god': god}
        for name, g, god in zip(('year', 'month', 'day', 'hour'), ganzhi, gods)])
    return [pillars, ten]


class TraceGateTests(unittest.TestCase):
    def test_consistent_trace_matches_lookup(self):
        out = bingyao_assessment(_StubTrace(_consistent_steps(), {'e1': {}}))
        self.assertEqual(out['status'], 'triggered')
        self.assertEqual(out['medicine_status'], 'candidate_present')
        self.assertEqual(out['disease_candidate']['gods'],
                         [{'pillar': 'hour', 'stem': '甲', 'ten_god': '比肩'}])
        self.assertEqual(out['consumed_rule_ids'],
                         ['bazi.phase2.pillars', 'bazi.phase2.ten_gods'])
        # The second pair rides along independently: this chart shows
        # neither 食神/伤官, so it abstains on its own reason.
        second = out['pairs'][1]
        self.assertEqual(second['pair_id'], 'foodwound_seal_wealth')
        self.assertEqual(second['status'], 'not_triggered')
        self.assertEqual(second['not_triggered_reason'],
                         'subject_foodwound_not_visible')

    def test_missing_ten_god_facts_abstain(self):
        # 事实缺失弃判： no executed ten-god step -> no candidate at all.
        steps = _consistent_steps()
        with self.assertRaises(ValueError):
            bingyao_assessment(_StubTrace(steps[:1], {'e1': {}}))
        with self.assertRaises(ValueError):
            bingyao_assessment(_StubTrace([], {}))

    def test_forged_traces_fail_closed(self):
        with self.assertRaises(ValueError):
            bingyao_assessment(_StubTrace(_consistent_steps(), {'e1': {}},
                                          domain='liuyao'))
        with self.assertRaises(ValueError):
            bingyao_assessment(_StubTrace(_consistent_steps(), {'e1': {}},
                                          variant='ziping-forged-v9'))
        unbound = _consistent_steps()
        unbound[1] = _step('bazi.phase2.ten_gods', unbound[1]['output'],
                           evidence_ids=())
        with self.assertRaises(ValueError):
            bingyao_assessment(_StubTrace(unbound, {'e1': {}}))
        inconsistent = _consistent_steps()
        inconsistent[1]['output'][0]['stem'] = '丁'
        with self.assertRaises(ValueError):
            bingyao_assessment(_StubTrace(inconsistent, {'e1': {}}))
        wrong_day = _consistent_steps()
        wrong_day[1]['output'][2]['ten_god'] = '比肩'
        with self.assertRaises(ValueError):
            bingyao_assessment(_StubTrace(wrong_day, {'e1': {}}))
        with self.assertRaises(ValueError):
            bingyao_assessment(_StubTrace(_consistent_steps(), {'e1': {}}),
                               bingyao_variant='bingyao-other-v9')


class PublicIsolationTests(unittest.TestCase):
    def test_engine_requires_explicit_research_mode(self):
        with self.assertRaisesRegex(ValueError, 'research mode'):
            execute('bazi', {'bingyao_variant': VARIANT,
                             'year_ganzhi': '戊戌', 'month_ganzhi': '庚申',
                             'day_ganzhi': '甲子', 'hour_ganzhi': '甲戌'})

    def test_projection_strips_bingyao_assessment(self):
        payload = {
            'domain': 'bazi', 'variant': 'ziping-structural-v1',
            'deterministic': True,
            'result': {'pillars': [], 'bingyao_assessment': {'variant': VARIANT},
                       'tiaohou_assessment': {'variant': 'tiaohou-qiongtong-v1'}},
            'chart': {'bingyao_assessment': {'variant': VARIANT}},
            'evidence': {}, 'rule_matches': [], 'trace': [],
        }
        projected = project_execution(copy.deepcopy(payload))
        self.assertNotIn('bingyao_assessment',
                         json.dumps(projected, ensure_ascii=False))

    def test_bingyao_and_tiaohou_stay_parallel_never_merged(self):
        # 口径外弃判： the two systems' outputs are separate objects;
        # neither module emits a merged useful-god field.
        bingyao_out = bingyao_lookup('甲', _facts((('year', '戊', '偏财'),
                                                  ('month', '庚', '七杀'),
                                                  ('hour', '甲', '比肩'))))
        self.assertEqual(bingyao_out['system'], 'bingyao')
        self.assertNotIn('sequence', bingyao_out)
        self.assertFalse({'tiaohou_assessment', 'useful_god', '喜用神'}
                         & set(_keys(bingyao_out)))


class SourceRegistrationTests(unittest.TestCase):
    def test_source_and_lineage_registered_at_grade_c(self):
        sources = json.loads((ROOT / 'config/knowledge_sources.json')
                             .read_text('utf-8'))['sources']
        entry = next(s for s in sources if s['source_id'] == SOURCE_ID)
        self.assertEqual(entry['evidence_level'], 'C')
        self.assertEqual(entry['kind'], 'classical')
        self.assertTrue(entry['public_domain'])
        self.assertEqual(entry['sha256'], SNAPSHOT_SHA256)
        self.assertEqual(entry['content_path'],
                         'data/quarantine/public_domain_snapshots/'
                         'daizhigev20/shenfeng_tongkao.txt')
        audit = json.loads((ROOT / 'config/phase2_source_audit.json')
                           .read_text('utf-8'))
        lineage = {r['source_id']: r for r in audit['lineages']}
        self.assertEqual({s['source_id'] for s in sources}, set(lineage),
                         'every registered source needs exactly one lineage')
        row = lineage[SOURCE_ID]
        self.assertEqual(row['grade_ceiling'], 'C')
        self.assertEqual(row['edition_status'], 'unverified')
        self.assertEqual(row['authority_status'], 'unverified')


if __name__ == '__main__':
    unittest.main()
