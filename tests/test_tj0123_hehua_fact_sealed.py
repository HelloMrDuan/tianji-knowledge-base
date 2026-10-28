"""TJ-012.3 合化审源与事实层设计审定：密封验证。

Runs in the offline assembled acceptance only (NOT public CI, same
partition rule as the earlier batches). Pins:

- snapshot integrity for the Sanming snapshot the adjudication pins
  (sha256 + char counts, identical to the 018-C register pin);
- every quote reference in bazi_hehua_fact_adjudication resolves to
  its home register and the registered quote slice re-verifies
  byte-for-byte against the sealed snapshot;
- the Canonical pins (s010 roster section, the stem_five_combinations
  term definition, r005's exceptions) match the assembled phase1
  bundle byte-for-byte, and the bundle measurements the adjudication
  recorded still hold (59 sections, no section carrying transformation
  condition text, 18 concepts with no hehua concept, 30 rules);
- the assembled phase2 bundle still states the pinned unresolved
  posture for transformation and the stem_five_combinations evidence
  scope; the foundations roster equals the pinned five pairs;
- the Ditiansui huaxiang chapter measurements (chapter bounds, the
  P05 audit anchor, per-file keyword counts) re-verify against the
  sealed snapshot texts;
- current behaviour regression: relation facts produced by the
  production structural functions for a chart containing a stem
  combination still carry no transformation verdict of any kind
  (the adjudication batch wires nothing).
"""
import hashlib
import json
from pathlib import Path
import unittest

from tianji_kb import bazi_hehua_fact_adjudication as adj
from tianji_kb import bazi_sanming_juan2_hehua_collation as hc
from tianji_kb import bazi_sanming_juan6_fangju_baxiang_collation as j6
from tianji_kb.bazi_core import (chart_from_datetime, reviewed_relations,
                                 stem_five_combination)

ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT_DIR = (ROOT / 'data' / 'quarantine' / 'public_domain_snapshots'
                / 'daizhigev20')
CANONICAL_BAZI = ROOT / 'data' / 'canonical' / 'bazi'

HOME = {'bazi_sanming_juan2_hehua_collation':
        {q['id']: q for q in hc.COLLATION_QUOTES},
        'bazi_sanming_juan6_fangju_baxiang_collation':
        {q['id']: q for q in j6.COLLATION_QUOTES}}
MEAS = adj.SEALED_MEASUREMENTS
HEHUA_KEYWORDS = ('化气', '合化', '化象', '真化', '化格')


def _text(filename):
    return (SNAPSHOT_DIR / filename).read_bytes().decode('utf-8')


def _phase1():
    return json.loads((CANONICAL_BAZI / 'phase1_knowledge.json')
                      .read_text(encoding='utf-8'))


def _phase2():
    return json.loads((CANONICAL_BAZI / 'phase2_execution.json')
                      .read_text(encoding='utf-8'))


class SnapshotIntegrityTest(unittest.TestCase):
    def test_sanming_pin_matches_018c_and_snapshot(self):
        meta = hc.COLLATION_SNAPSHOTS['sanming_tonghui.txt']
        raw = (SNAPSHOT_DIR / 'sanming_tonghui.txt').read_bytes()
        self.assertEqual(hashlib.sha256(raw).hexdigest(), meta['sha256'])
        self.assertEqual(len(raw.decode('utf-8')), meta['chars'])
        pin = adj.HEHUA_ADJUDICATION_REGISTER['source_snapshot']
        self.assertEqual(pin['sanming_sha256'], meta['sha256'])
        self.assertEqual(pin['sanming_chars'], meta['chars'])


class QuoteSliceTest(unittest.TestCase):
    def test_all_referenced_quotes_verify_byte_for_byte(self):
        text = _text('sanming_tonghui.txt')
        for ref in adj.QUOTE_REFERENCES:
            quote = HOME[ref['register']][ref['quote_id']]
            loc = quote['locator']
            self.assertEqual(text[loc['char_start']:loc['char_end']],
                             quote['quote'], ref['quote_id'])
            self.assertEqual(text.count(quote['quote']), 1,
                             ref['quote_id'])


class Phase1PinsTest(unittest.TestCase):
    def test_section_keyword_scan(self):
        p1 = _phase1()
        sections = p1['sections']
        self.assertEqual(len(sections), MEAS['phase1_sections_total'])
        wuhe_sections = []
        for s in sections:
            blob = (s.get('text') or '') + (s.get('name') or '')
            for kw in HEHUA_KEYWORDS:
                self.assertNotIn(kw, blob, (s['id'], kw))
            if '五合' in blob:
                wuhe_sections.append(s['id'])
        self.assertEqual(wuhe_sections, MEAS['phase1_sections_with_wuhe'])
        self.assertEqual(MEAS['phase1_sections_with_hehua_keywords'], 0)

    def test_roster_section_and_term_and_rule_pins(self):
        p1 = _phase1()
        pins = {p.get('section_id') or p.get('term_id')
                or p.get('rule_id'): p for p in adj.SEALED_PINS}
        s010 = next(s for s in p1['sections']
                    if s['id'] == 'bazi.section.s010')
        self.assertEqual(s010['text'],
                         pins['bazi.section.s010']['original_text'])
        term = next(t for t in p1['terms']
                    if t['id'] == 'bazi.term.stem_five_combinations')
        self.assertEqual(
            term['definition'],
            pins['bazi.term.stem_five_combinations']['definition'])
        r005 = next(r for r in p1['rules'] if r['id'] == 'bazi.rule.r005')
        self.assertEqual(r005['exceptions'],
                         pins['bazi.rule.r005']['exceptions'])
        self.assertEqual(len(p1['rules']), MEAS['phase1_rules_total'])

    def test_no_hehua_concept(self):
        p1 = _phase1()
        concepts = p1['concepts']
        self.assertEqual(len(concepts), MEAS['phase1_concepts_total'])
        for c in concepts:
            blob = json.dumps(c, ensure_ascii=False)
            self.assertNotIn('合化', blob, c['id'])
            self.assertNotIn('化气', blob, c['id'])
        self.assertEqual(MEAS['phase1_hehua_concepts'], 0)


class Phase2AndFoundationsTest(unittest.TestCase):
    def test_phase2_posture(self):
        p2 = _phase2()
        self.assertEqual(len(p2['rules']), MEAS['phase2_rules_total'])
        rule = next(r for r in p2['rules']
                    if r['id'] == 'bazi.phase2.stem_five_combinations')
        self.assertIn('不判断化气成败', rule['evidence_scope'])
        unresolved = p2['unresolved']
        self.assertTrue(any('五合/六合命中不代表化气成立' in u
                            for u in unresolved))
        self.assertTrue(any('成化条件' in u and '未裁定' in u
                            for u in unresolved))
        for stmt in adj.STATUS_QUO_LINKAGE[
                'phase2_unresolved_statements']:
            self.assertTrue(any(stmt in u for u in unresolved), stmt)

    def test_foundations_roster(self):
        foundations = json.loads(
            (CANONICAL_BAZI / 'foundations_v1.json').read_text(
                encoding='utf-8'))
        self.assertEqual(foundations['stem_combinations'],
                         MEAS['foundations_stem_combinations'])


class SnapshotMeasurementsTest(unittest.TestCase):
    def test_keyword_counts(self):
        for filename, counts in MEAS['snapshot_keyword_counts'].items():
            text = _text(filename)
            for kw, expected in counts.items():
                self.assertEqual(text.count(kw), expected,
                                 (filename, kw))

    def test_ditiansui_huaxiang_chapter_bounds(self):
        text = _text('ditiansui_chanwei.txt')
        chapter = MEAS['ditiansui_huaxiang_chapter']
        self.assertEqual(text[chapter['start']:chapter['start'] + 5],
                         chapter['heading'])
        anchor = chapter['audit_anchor']
        self.assertEqual(text[anchor:anchor + 4], '化得真者')
        self.assertEqual(text[chapter['end']:chapter['end'] + 5],
                         '十四、假从')


class CurrentBehaviourRegressionTest(unittest.TestCase):
    def test_combination_fact_carries_no_transformation_verdict(self):
        result = stem_five_combination('丙', '辛')
        self.assertTrue(result['matched'])
        self.assertEqual(result['traditional_result_element'], '水')
        self.assertEqual(set(result),
                         {'matched', 'stems',
                          'traditional_result_element'})

    def test_real_chart_relations_have_no_transformation_keys(self):
        chart = chart_from_datetime('1990-01-15T10:30:00+08:00')
        stems = [p['stem']['value'] for p in chart['pillars']]
        branches = [p['branch']['value'] for p in chart['pillars']]
        relations = reviewed_relations(stems, branches)
        self.assertEqual(set(relations),
                         {'stem_five_combinations',
                          'branch_six_harmonies', 'branch_six_harms',
                          'branch_six_clashes',
                          'branch_triple_harmonies', 'spouse_palace'})
        blob = json.dumps(relations, ensure_ascii=False)
        self.assertNotIn('transformation', blob)
        self.assertNotIn('化气成立', blob)


if __name__ == '__main__':
    unittest.main()
