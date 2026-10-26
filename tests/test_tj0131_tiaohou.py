"""TJ-013.1 public contract tests for the tiaohou (调候) research Variant.

Public-safe by design: the rule table, the pure lookup, the engine
research gate, forged-trace rejection and the public-projection strip
need no sealed data. Verbatim equality of every quote against the
pinned snapshot text itself is checked only in the sealed companion
test_tj0131_tiaohou_sealed.py (offline acceptance, NOT public CI),
following the test_phase2_liuyao precedent.
"""
import copy
import json
from pathlib import Path
import unittest

from tianji_kb.bazi_tiaohou import (
    ENTRIES, SNAPSHOT_SHA256, SOURCE_ID, VARIANT,
    tiaohou_assessment, tiaohou_lookup,
)
from tianji_kb.engine import execute
from tianji_kb.public_projection import project_execution

ROOT = Path(__file__).resolve().parents[1]
GOLDEN = json.loads((ROOT / 'tests/golden_tj0131_tiaohou.json').read_text('utf-8'))
BRANCHES = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']
VERDICT_KEYS = {'score', 'rating', 'fortune', 'fortune_verdict', 'auspicious',
                'inauspicious', 'luck', '吉凶', '评分'}


def _keys(node):
    if isinstance(node, dict):
        for key, value in node.items():
            yield key
            yield from _keys(value)
    elif isinstance(node, list):
        for item in node:
            yield from _keys(item)


class RuleTableTests(unittest.TestCase):
    def test_table_matches_golden_transcription(self):
        self.assertEqual(len(ENTRIES), 119)
        golden = {(e['day_master'], e['month_branch']): e
                  for e in GOLDEN['entries']}
        self.assertEqual({(e['day_master'], e['month_branch']) for e in ENTRIES},
                         set(golden))
        for entry in ENTRIES:
            want = golden[(entry['day_master'], entry['month_branch'])]
            self.assertEqual(entry['quote'], want['quote'])
            self.assertEqual(entry['quote_locator'], want['quote_locator'])
            self.assertEqual(entry['section'], want['section'])
            self.assertEqual([(s['stem'], s['order']) for s in entry['sequence']],
                             [(s['stem'], s['order']) for s in want['sequence']])
            self.assertEqual(
                [(b['id'], b['quote'], b['locator']) for b in entry['branches']],
                [(b['id'], b['quote'], b['locator']) for b in want['branches']])
            self.assertEqual(
                [(u['quote'], u['locator']) for u in entry['unencoded_branches']],
                [(u['quote'], u['locator']) for u in want['unencoded_branches']])
            self.assertEqual(
                [(r['quote'], r['locator']) for r in entry['related']],
                [(r['quote'], r['locator']) for r in want['related']])

    def test_locators_are_inside_sections_and_quotes_short(self):
        for entry in ENTRIES:
            self.assertLessEqual(len(entry['quote']), 120)
            sec, loc = entry['section'], entry['quote_locator']
            self.assertGreaterEqual(loc['char_start'], sec['char_start'])
            self.assertLessEqual(loc['char_end'], sec['char_end'])
            self.assertEqual(loc['char_end'] - loc['char_start'], len(entry['quote']))
            orders = [s['order'] for s in entry['sequence']]
            self.assertEqual(orders, list(range(1, len(orders) + 1)),
                             'first-take must precede next-take in every entry')

    def test_variant_flags_are_research_only(self):
        for entry in ENTRIES:
            self.assertTrue(entry['quote'])
        self.assertEqual(VARIANT, 'tiaohou-qiongtong-v1')
        self.assertEqual(GOLDEN['source']['snapshot_sha256'], SNAPSHOT_SHA256)


class LookupGoldenTests(unittest.TestCase):
    def test_all_golden_cases(self):
        for case in GOLDEN['cases']:
            with self.subTest(case=case['id']):
                out = tiaohou_lookup(case['day_master'], case['month_branch'],
                                     case['visible_stems'], case['hidden_stems'])
                expected = case['expected']
                self.assertEqual(out['status'], expected['status'])
                if expected['status'] == 'not_applicable':
                    self.assertEqual(out['reason'], expected['reason'])
                    self.assertNotIn('sequence', out)
                    continue
                self.assertEqual(
                    [(s['stem'], s['order'], s['presence']) for s in out['sequence']],
                    [(s['stem'], s['order'], s['presence']) for s in expected['sequence']])
                self.assertEqual(
                    [(b['id'], b['applied']) for b in out['branches']],
                    [(b['id'], b['applied']) for b in expected['branches']])

    def test_presence_variants_are_all_exercised(self):
        seen = set()
        for case in GOLDEN['cases']:
            if case['expected']['status'] != 'matched':
                continue
            out = tiaohou_lookup(case['day_master'], case['month_branch'],
                                 case['visible_stems'], case['hidden_stems'])
            seen |= {s['presence'] for s in out['sequence']}
        self.assertEqual(seen, {'visible', 'hidden', 'absent'})

    def test_no_verdict_or_score_fields_anywhere(self):
        for case in GOLDEN['cases']:
            out = tiaohou_lookup(case['day_master'], case['month_branch'],
                                 case['visible_stems'], case['hidden_stems'])
            self.assertFalse(VERDICT_KEYS & set(_keys(out)))
            self.assertTrue(out['research_only'])
            self.assertFalse(out['public_enabled'])
            self.assertFalse(out['ai_enabled'])


class AbstainAndFailClosedTests(unittest.TestCase):
    def test_full_grid_coverage_only_yi_chou_absent(self):
        # All 120 (day master, month branch) combinations: 119 match a
        # reviewed entry; the single exception is 乙×丑, whose entry does
        # not exist in the pinned snapshot (see GOLDEN absent_entries).
        absent = {(a['day_master'], a['month_branch'])
                  for a in GOLDEN['absent_entries']}
        self.assertEqual(absent, {('乙', '丑')})
        matched = 0
        for stem in '甲乙丙丁戊己庚辛壬癸':
            for branch in BRANCHES:
                with self.subTest(stem=stem, branch=branch):
                    out = tiaohou_lookup(stem, branch, ['甲', '乙', '丙', '丁'],
                                         [[], [], [], []])
                    if (stem, branch) in absent:
                        self.assertEqual(out['status'], 'not_applicable')
                        self.assertEqual(out['reason'], 'entry_absent_in_source')
                        self.assertEqual(out['day_master'], stem)
                        self.assertEqual(out['month_branch'], branch)
                        self.assertNotIn('sequence', out)
                    else:
                        self.assertEqual(out['status'], 'matched')
                        self.assertEqual(out['day_master'], stem)
                        self.assertEqual(out['month_branch'], branch)
                        matched += 1
        self.assertEqual(matched, 119)

    def test_illegal_month_branch_fails_closed(self):
        for bad in ('猫', '', '甲', None, 3):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                tiaohou_lookup('甲', bad, ['甲'] * 4, [[]] * 4)

    def test_missing_or_malformed_inputs_fail_closed(self):
        with self.assertRaises(ValueError):
            tiaohou_lookup(None, '卯', ['甲'] * 4, [[]] * 4)
        with self.assertRaises(ValueError):
            tiaohou_lookup('甲', '卯', ['甲'] * 3, [[]] * 4)
        with self.assertRaises(ValueError):
            tiaohou_lookup('甲', '卯', ['甲'] * 4, [[]] * 3)
        with self.assertRaises(ValueError):
            tiaohou_lookup('甲', '卯', ['甲', '乙', '丙', '猫'], [[]] * 4)


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
    ganzhi = ['戊辰', '庚辰', '甲寅', '甲申']
    pillars = _step('bazi.phase2.pillars',
                    {'ganzhi': ganzhi, 'day_master': {'stem': '甲'}})
    ten = _step('bazi.phase2.ten_gods', [
        {'pillar': name, 'stem': g[0], 'ten_god': 'x'}
        for name, g in zip(('year', 'month', 'day', 'hour'), ganzhi)])
    hidden = _step('bazi.phase2.hidden_stems', [
        {'pillar': name, 'branch': g[1],
         'hidden_stems': [{'stem': s} for s in stems]}
        for name, g, stems in zip(
            ('year', 'month', 'day', 'hour'), ganzhi,
            (['戊', '乙', '癸'], ['戊', '乙', '癸'],
             ['甲', '丙', '戊'], ['庚', '壬', '戊']))])
    return [pillars, ten, hidden]


class TraceGateTests(unittest.TestCase):
    def test_consistent_trace_matches_lookup(self):
        out = tiaohou_assessment(_StubTrace(_consistent_steps(), {'e1': {}}))
        self.assertEqual(out['status'], 'matched')
        self.assertEqual(out['month_branch'], '辰')
        self.assertEqual([(s['stem'], s['presence']) for s in out['sequence']],
                         [('庚', 'visible'), ('壬', 'hidden')])

    def test_forged_traces_fail_closed(self):
        with self.assertRaises(ValueError):
            tiaohou_assessment(_StubTrace(_consistent_steps(), {'e1': {}},
                                          domain='liuyao'))
        with self.assertRaises(ValueError):
            tiaohou_assessment(_StubTrace(_consistent_steps(), {'e1': {}},
                                          variant='ziping-forged-v9'))
        with self.assertRaises(ValueError):
            tiaohou_assessment(_StubTrace([], {}))
        unbound = _consistent_steps()
        unbound[0] = _step('bazi.phase2.pillars', unbound[0]['output'],
                           evidence_ids=())
        with self.assertRaises(ValueError):
            tiaohou_assessment(_StubTrace(unbound, {'e1': {}}))
        inconsistent = _consistent_steps()
        inconsistent[1]['output'][0]['stem'] = '丁'
        with self.assertRaises(ValueError):
            tiaohou_assessment(_StubTrace(inconsistent, {'e1': {}}))
        with self.assertRaises(ValueError):
            tiaohou_assessment(_StubTrace(_consistent_steps(), {'e1': {}}),
                               tiaohou_variant='tiaohou-other-v9')


class PublicIsolationTests(unittest.TestCase):
    def test_engine_requires_explicit_research_mode(self):
        with self.assertRaisesRegex(ValueError, 'research mode'):
            execute('bazi', {'tiaohou_variant': VARIANT,
                             'year_ganzhi': '甲子', 'month_ganzhi': '丙寅',
                             'day_ganzhi': '甲辰', 'hour_ganzhi': '戊辰'})

    def test_projection_strips_tiaohou_assessment(self):
        payload = {
            'domain': 'bazi', 'variant': 'ziping-structural-v1',
            'deterministic': True,
            'result': {'pillars': [], 'tiaohou_assessment': {'variant': VARIANT}},
            'chart': {'tiaohou_assessment': {'variant': VARIANT}},
            'evidence': {}, 'rule_matches': [], 'trace': [],
        }
        projected = project_execution(copy.deepcopy(payload))
        self.assertNotIn('tiaohou_assessment',
                         json.dumps(projected, ensure_ascii=False))


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
                         'daizhigev20/qiongtong_baojian.txt')
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
