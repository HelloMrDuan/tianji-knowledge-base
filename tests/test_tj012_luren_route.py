"""TJ-012.3 Slice A （禄刃选格路线负向裁定） public contract tests.

Public-safe by design: the registered 禄/刃 table, the pure route
lookup over the full stem x branch domain, forged-trace rejection, the
engine research gate and the public-projection strip need no sealed
data. Verbatim equality of every registered quote against the pinned
snapshot texts themselves, and real-chart coverage of the Golden
cases, live only in the sealed companion
test_tj012_luren_route_sealed.py (offline acceptance, NOT public CI),
following the test_tj013_bingyao precedent.

The route is a NEGATIVE determination only: it closes (or does not
close) the Ren month-pattern route when the month branch is the day
stem's 禄/刃 branch. It never establishes any pattern; every other
determination field stays None across the whole domain, which these
tests sweep exhaustively.
"""
import copy
import json
from pathlib import Path
import unittest

from tianji_kb.bazi_pattern import (
    LU_BRANCH, LUREN_ADJUDICATION_NOTES, LUREN_LIMITATIONS, LUREN_QUOTES,
    LUREN_ROUTE_VARIANT, MISCELLANEOUS_BRANCHES, PATTERN_VARIANT,
    REN_BRANCH, luren_route_lookup, month_pattern_route,
)
from tianji_kb.engine import execute
from tianji_kb.public_projection import project_execution

ROOT = Path(__file__).resolve().parents[1]
GOLDEN = json.loads(
    (ROOT / 'tests/golden_tj012_luren_route.json').read_text('utf-8'))
STEMS = '甲乙丙丁戊己庚辛壬癸'
BRANCHES = '子丑寅卯辰巳午未申酉戌亥'
VERDICT_KEYS = {'score', 'rating', 'fortune', 'fortune_verdict',
                'auspicious', 'inauspicious', 'luck', '吉凶', '评分',
                '喜用神', '用神', 'useful_god', 'favorable_god',
                'pattern_name', 'true_false', 'success_failure'}


def _keys(node):
    if isinstance(node, dict):
        for key, value in node.items():
            yield key
            yield from _keys(value)
    elif isinstance(node, list):
        for item in node:
            yield from _keys(item)


class TableTranscriptionTests(unittest.TestCase):
    def test_table_matches_golden_transcription(self):
        self.assertEqual(LUREN_ROUTE_VARIANT, GOLDEN['variant'])
        golden_table = {row['stem']: row for row in GOLDEN['table']}
        self.assertEqual(set(golden_table), set(STEMS))
        for stem in STEMS:
            want = golden_table[stem]
            self.assertEqual(LU_BRANCH[stem], want['lu'], stem)
            self.assertEqual(REN_BRANCH.get(stem), want['ren'], stem)
            if want['ren'] is None:
                self.assertIn(stem, '乙丁己辛癸',
                              'only yin stems may lack a blade entry')
                self.assertIn('阴干无刃', want['ren_note'])
        self.assertEqual(set(REN_BRANCH), set('甲丙戊庚壬'))

    def test_quotes_match_golden_transcription(self):
        golden_quotes = {q['id']: q for q in GOLDEN['quotes']}
        self.assertEqual({q['id'] for q in LUREN_QUOTES}, set(golden_quotes))
        for quote in LUREN_QUOTES:
            want = golden_quotes[quote['id']]
            self.assertEqual(quote['quote'], want['quote'])
            self.assertEqual(quote['locator'], want['locator'])
            self.assertEqual(quote['source_id'], want['source_id'])
            loc = quote['locator']
            self.assertEqual(loc['char_end'] - loc['char_start'],
                             len(quote['quote']),
                             'locator span must equal the verbatim quote')

    def test_per_stem_fragments_inside_sentence_quotes(self):
        # The per-stem fragments recorded in the Golden are substrings
        # of the two sentence quotes at exactly their recorded offsets
        # relative to each sentence's locator start.
        sentences = {q['id']: q for q in LUREN_QUOTES}
        lu_sentence = sentences['sanming.lu_sentence']
        ren_sentence = sentences['sanming.ren_positions']
        for row in GOLDEN['table']:
            frag = row['lu_fragment']
            start = frag['char_start'] - lu_sentence['locator']['char_start']
            self.assertEqual(
                lu_sentence['quote'][start:start + 3], frag['quote'],
                f"{row['stem']} 禄 fragment must sit inside the 禄 sentence")
            if row['ren_fragment'] is not None:
                rfrag = row['ren_fragment']
                rstart = (rfrag['char_start']
                          - ren_sentence['locator']['char_start'])
                self.assertEqual(
                    ren_sentence['quote'][rstart:rstart + 3], rfrag['quote'],
                    f"{row['stem']} 刃 fragment must sit inside the 刃 sentence")

    def test_branch_sets_disjoint_from_miscellaneous(self):
        # Boundary fact A5: under the registered table no miscellaneous
        # month (辰戌丑未) can be a 禄 or 刃 branch, so the hypothesised
        # miscellaneous-overlap case does not exist; miscellaneous
        # months are judged by the table directly (Slice B territory
        # is pattern SELECTION in such months, not this exclusion).
        self.assertFalse(set(LU_BRANCH.values()) & set(MISCELLANEOUS_BRANCHES))
        self.assertFalse(set(REN_BRANCH.values()) & set(MISCELLANEOUS_BRANCHES))
        self.assertEqual(set(GOLDEN['boundary_facts']['lu_branch_set']),
                         set(LU_BRANCH.values()))
        self.assertEqual(set(GOLDEN['boundary_facts']['ren_branch_set']),
                         set(REN_BRANCH.values()))
        # No stem's 禄 and 刃 coincide, so matched_via is never ambiguous.
        for stem in REN_BRANCH:
            self.assertNotEqual(LU_BRANCH[stem], REN_BRANCH[stem])


class LookupDomainTests(unittest.TestCase):
    def test_full_domain_sweep(self):
        for stem in STEMS:
            for branch in BRANCHES:
                with self.subTest(stem=stem, branch=branch):
                    out = luren_route_lookup(stem, branch)
                    self.assertEqual(out['lu_branch'], LU_BRANCH[stem])
                    self.assertEqual(out['ren_branch'], REN_BRANCH.get(stem))
                    if branch == LU_BRANCH[stem]:
                        self.assertEqual(out['route'],
                                         'luren_no_month_pattern')
                        self.assertEqual(out['matched_via'], 'lu')
                    elif REN_BRANCH.get(stem) == branch:
                        self.assertEqual(out['route'],
                                         'luren_no_month_pattern')
                        self.assertEqual(out['matched_via'], 'ren')
                    else:
                        self.assertEqual(out['route'], 'not_luren')
                        self.assertIsNone(out['matched_via'])
                    self.assertEqual(out['miscellaneous_month'],
                                     branch in MISCELLANEOUS_BRANCHES)

    def test_counterexample_pins(self):
        # 甲日卯月： 卯 is 乙's 禄 and 甲's 刃 — the route fires via the
        # blade channel only; the 禄 channel must not cross-assign.
        out = luren_route_lookup('甲', '卯')
        self.assertEqual(out['route'], 'luren_no_month_pattern')
        self.assertEqual(out['matched_via'], 'ren')
        self.assertEqual(out['lu_branch'], '寅')
        # 乙日寅月： 寅 is 甲's 禄 — another stem's 禄 never fires.
        out = luren_route_lookup('乙', '寅')
        self.assertEqual(out['route'], 'not_luren')
        # 辛日戌月： 戌月 is where an unregistered yin-blade doctrine
        # would place 辛's blade; the registered table has none.
        out = luren_route_lookup('辛', '戌')
        self.assertEqual(out['route'], 'not_luren')
        self.assertIsNone(out['ren_branch'])
        self.assertTrue(out['miscellaneous_month'])

    def test_determination_stays_none_across_domain(self):
        for stem in STEMS:
            for branch in BRANCHES:
                out = luren_route_lookup(stem, branch)
                det = out['determination']
                self.assertEqual(det['status'], 'unresolved')
                self.assertIsNone(det['pattern'])
                self.assertIsNone(det['true_false'])
                self.assertIsNone(det['success_failure'])
                self.assertIsNone(det['useful_god'])
                self.assertFalse(out['qualified_for_determination'])
                self.assertEqual(out['borrowed_route']['status'],
                                 'undetermined')
                self.assertIsNone(
                    out['borrowed_route']['borrowed_pattern_determination'])
                self.assertTrue(out['research_only'])
                self.assertFalse(out['public_enabled'])
                self.assertFalse(out['ai_enabled'])
                # E0339 (TJ-018.3 B-2): the route completed its
                # sealed Phase1/Phase2 registration (r035 /
                # bazi.phase2.pattern_route); the disclosure field
                # flipped, route semantics unchanged.
                self.assertEqual(out['evidence_binding'],
                                 'registered_phase1_phase2')
                self.assertEqual(out['adjudication_notes'],
                                 list(LUREN_ADJUDICATION_NOTES))
                self.assertEqual(out['scope_limits'],
                                 list(LUREN_LIMITATIONS))
                leaked = VERDICT_KEYS & set(_keys(out))
                self.assertLessEqual(
                    leaked, {'true_false', 'success_failure', 'useful_god'},
                    'no verdict/score/useful-god key may appear beyond the '
                    'pinned-None determination fields')

    def test_lookup_fails_closed(self):
        with self.assertRaises(ValueError):
            luren_route_lookup('猫', '寅')
        with self.assertRaises(ValueError):
            luren_route_lookup('甲', '猫')
        with self.assertRaises(ValueError):
            luren_route_lookup('', '')


class _StubTrace:
    def __init__(self, steps, evidence):
        self.steps = steps
        self.evidence = evidence


def _pillars_step(day_stem, month_branch, evidence_ids=('e1',)):
    ganzhi = ['己丑', '丙' + month_branch, day_stem + '戌', '己巳']
    return {'rule_id': 'bazi.phase2.pillars',
            'evidence_ids': list(evidence_ids),
            'output': {'ganzhi': ganzhi,
                       'day_master': {'stem': day_stem}}}


class TraceWrapperTests(unittest.TestCase):
    def test_month_pattern_route_consumes_pillars(self):
        trace = _StubTrace([_pillars_step('甲', '寅')], {'e1': object()})
        out = month_pattern_route(trace)
        self.assertEqual(out['route'], 'luren_no_month_pattern')
        self.assertEqual(out['matched_via'], 'lu')
        self.assertEqual(out['consumed_rule_ids'], ['bazi.phase2.pillars'])
        self.assertIn('/output/day_master/stem', out['fact_refs']['day_master'])
        self.assertIn('/output/ganzhi/1', out['fact_refs']['month_branch'])

    def test_forged_or_missing_facts_fail_closed(self):
        with self.assertRaises(ValueError):
            month_pattern_route(_StubTrace([], {}))
        with self.assertRaises(ValueError):
            month_pattern_route(
                _StubTrace([_pillars_step('甲', '寅')], {}))
        with self.assertRaises(ValueError):
            month_pattern_route(_StubTrace(
                [_pillars_step('甲', '寅', evidence_ids=())], {'e1': 1}))


class EngineAndProjectionTests(unittest.TestCase):
    def test_engine_requires_explicit_research_mode(self):
        with self.assertRaisesRegex(ValueError, 'research mode'):
            execute('bazi', {'pattern_variant': PATTERN_VARIANT,
                             'year_ganzhi': '己丑', 'month_ganzhi': '丙寅',
                             'day_ganzhi': '甲戌', 'hour_ganzhi': '己巳'})

    def test_public_projection_strips_pattern_route(self):
        payload = {
            'domain': 'bazi', 'variant': 'ziping-structural-v1',
            'deterministic': True,
            'result': {'pillars': [],
                       'pattern_route': {'route': 'luren_no_month_pattern'}},
            'chart': {'pattern_route': {'route': 'not_luren'}},
            'evidence': {}, 'rule_matches': [], 'trace': [],
        }
        out = project_execution(copy.deepcopy(payload))
        self.assertNotIn('pattern_route', out['chart'])
        self.assertNotIn('pattern_route', out['result'])


if __name__ == '__main__':
    unittest.main()
