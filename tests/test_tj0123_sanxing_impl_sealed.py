"""TJ-012.3 三刑事实层实现：密封验证。

Runs in the offline assembled acceptance only (NOT public CI, same
partition rule as the earlier batches). Pins:

- the implementation's registration integrity check passes against
  the assembled tree's registers, and every evidence ref the fact
  function actually emits resolves byte-for-byte: quote refs slice
  the sealed Sanming snapshot at the registered locator and equal
  the registered quote; section refs equal the adjudication's
  Canonical section pins in the assembled phase1 bundle;
- every Golden case replays end-to-end through the production
  chain (chart_from_datetime in the assembled tree): pillars equal
  the Golden's recorded pillars and the fact output equals the
  hand-derived expectations;
- kind isolation on real charts: the pre-existing relation surface
  (branch_relations / reviewed_relations / chart branch_relations)
  still contains no punishment fact of any kind, and the
  adjudicated coexistence pairs really carry the named existing
  kinds alongside the new directed pairs (巳申 six_harmony next to
  巳→申, 寅巳 harm next to 寅→巳, 寅申/丑未 clash next to the
  group configurations);
- the three-punishments concept in the assembled bundle still
  carries the pinned semantics (the fact layer changes no concept
  field), and the foundations / phase2 surfaces still have no
  punishment rule surface (no Phase2 rule was built).
"""
import json
from pathlib import Path
import unittest

from tianji_kb import bazi_sanming_juan2_sanxing_collation as cj
from tianji_kb import bazi_sanxing_fact_adjudication as adj
from tianji_kb import bazi_sanxing_facts as impl
from tianji_kb.bazi_core import (branch_relations, chart_from_datetime,
                                 reviewed_relations)

ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT_DIR = (ROOT / 'data' / 'quarantine' / 'public_domain_snapshots'
                / 'daizhigev20')
CANONICAL_BAZI = ROOT / 'data' / 'canonical' / 'bazi'
GOLDEN = json.loads(
    (ROOT / 'tests' / 'golden_tj0123_sanxing_impl.json').read_text(
        encoding='utf-8'))
CASES = GOLDEN['cases']
SANMING_QUOTES = {q['id']: q for q in cj.COLLATION_QUOTES}
SECTION_PINS = {s['section_id']: s for s in adj.SEALED_SECTION_PINS}


class RegistrationIntegritySealedTest(unittest.TestCase):
    def test_integrity_check_passes_in_assembled_tree(self):
        self.assertEqual(impl._registration_integrity_errors(), [])

    def test_emitted_evidence_refs_verify_byte_for_byte(self):
        text = (SNAPSHOT_DIR / 'sanming_tonghui.txt').read_bytes() \
            .decode('utf-8')
        emitted_refs = set()
        for case in CASES:
            out = impl.reviewed_branch_punishment_facts(
                case['expected_branches'])
            for row in out['directed_pairs'] + out['self_punishments']:
                emitted_refs.update(row['evidence_refs'])
        self.assertTrue(emitted_refs)
        for ref in emitted_refs:
            if ref in SANMING_QUOTES:
                quote = SANMING_QUOTES[ref]
                loc = quote['locator']
                self.assertEqual(text[loc['char_start']:loc['char_end']],
                                 quote['quote'], ref)
            else:
                self.assertIn(ref, SECTION_PINS, ref)

    def test_section_pin_matches_assembled_phase1(self):
        bundle = json.loads(
            (CANONICAL_BAZI / 'phase1_knowledge.json').read_text('utf-8'))
        found = {}

        def walk(o):
            if isinstance(o, dict):
                sid = o.get('section_id')
                if sid and 'original_text' in o:
                    found[sid] = o
                for v in o.values():
                    walk(v)
            elif isinstance(o, list):
                for v in o:
                    walk(v)

        walk(bundle)
        pin = SECTION_PINS['bazi.section.s021']
        self.assertEqual(found['bazi.section.s021']['original_text'],
                         pin['original_text'])


class GoldenAssembledReplayTest(unittest.TestCase):
    def test_golden_cases_replay_through_full_production_chain(self):
        for case in CASES:
            with self.subTest(case=case['id']):
                chart = chart_from_datetime(case['birth'])
                pillars = [p['ganzhi'] for p in chart['pillars']]
                self.assertEqual(pillars, case['expected_pillars'])
                branches = [p['branch']['value']
                            for p in chart['pillars']]
                self.assertEqual(branches, case['expected_branches'])
                out = impl.reviewed_branch_punishment_facts(branches)
                self.assertEqual(out, case['expected'])


class KindIsolationSealedTest(unittest.TestCase):
    def test_existing_surfaces_have_no_punishment_facts(self):
        for case in CASES:
            with self.subTest(case=case['id']):
                chart = chart_from_datetime(case['birth'])
                stems = [p['stem']['value'] for p in chart['pillars']]
                branches = case['expected_branches']
                for output in (branch_relations(branches),
                               reviewed_relations(stems, branches),
                               chart['branch_relations']):
                    dump = json.dumps(output, ensure_ascii=False)
                    self.assertNotIn('punish', dump)
                    self.assertNotIn('sanxing', dump)
                    self.assertNotIn('三刑', dump)

    def test_coexisting_kinds_present_alongside_punishment_facts(self):
        checked = 0
        for case in CASES:
            for spec in case.get('coexisting_pair_kinds', []):
                branches = case['expected_branches']
                relations = branch_relations(branches)
                kinds = {row['kind'] for row in relations['pairs']
                         if set(row['branches']) == set(spec['branches'])}
                for kind in spec['kinds']:
                    self.assertIn(kind, kinds,
                                  (case['id'], spec['branches'], kind))
                checked += 1
        # g2 clash, g3 harm+six_harmony+clash, g4 clash, g9 harm
        self.assertEqual(checked, 6)


class ConceptAndRuleSurfaceSealedTest(unittest.TestCase):
    def test_concept_semantics_unchanged_in_bundle(self):
        bundle = json.loads(
            (CANONICAL_BAZI / 'phase1_knowledge.json').read_text('utf-8'))
        concept = next(c for c in bundle['concepts']
                       if c['id']
                       == 'bazi.concept.conflict_three_punishments')
        attrs = concept['attributes']
        self.assertEqual(attrs['status'], 'unresolved')
        self.assertEqual(attrs['executable_policy'],
                         'blocked_pending_school_resolution')
        self.assertEqual(attrs['production_policy'],
                         adj.CONCEPT_LINKAGE['production_policy'])

    def test_no_phase2_punishment_rule_was_built(self):
        # Batch transition (E0333, TJ-018.3 execution-binding batch
        # 1): at implementation time (E0268) no Phase2 punishment
        # rule existed at all. The execution-binding batch builds
        # exactly one -- the gated structural FACT step
        # bazi.phase2.branch_punishment_facts -- which is not an
        # adjudication rule (no RuleMatch, no sufficient_rule; the
        # sealed execbind suite pins the separation). The carrying
        # invariant is now: that fact step is the only punishment
        # entry in the Phase2 contract.
        bundle = json.loads(
            (CANONICAL_BAZI / 'phase2_execution.json').read_text('utf-8'))
        punish = [r['id'] for r in bundle['rules']
                  if 'punish' in r['id']]
        self.assertEqual(punish,
                         ['bazi.phase2.branch_punishment_facts'])
        foundations = json.loads(
            (CANONICAL_BAZI / 'foundations_v1.json').read_text('utf-8'))
        self.assertEqual(
            set(foundations['earthly_branch_relations']),
            {'clashes', 'triple_harmonies', 'directional_meetings',
             'six_harmonies', 'harms'})


if __name__ == '__main__':
    unittest.main()
