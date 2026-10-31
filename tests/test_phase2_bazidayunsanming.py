"""Governance pending-8 audit third batch (E0346) sealed
registration tests: the dayun Sanming segment -- Phase1 rules
r038 (direction) and r039 (Sanming conversion), Phase2 steps
bazi.phase2.dayun_classical_direction and
bazi.phase2.dayun_sanming_conversion, Canonical chapters/sections
s068/s069/s070 and terms dayun_direction / dayun_handover.

Pinned here:
- the Canonical sections hold exactly the S3 applied-text slices
  registered in stage 1 (sanming-juan2-dayun-collation-register-v1),
  PUA-free and box-free; the residual 防 in s068 sits outside
  every bound quote;
- both rules bind exactly the consumed citation subsets (2 + 8),
  each ref verbatim inside its section under the applied-text
  source; the Shenfeng quotes are bound by NO rule and no
  Shenfeng step or rule exists (E0348 supersedes this point:
  the Shenfeng segment is registered there -- r041 binds exactly
  sf_ex1/sf_ex3/sf_ex4 -- and the assertions below were migrated
  in that batch);
- the steps are validated and fire on the six real Golden cases
  (real charts / real instants from the TJ-017.4 witness set,
  including the ADV-001 zero-jie unresolved case) through the
  trace, via the minimally extended harness input contract (the
  gated chart kwargs dayun_classical_role /
  dayun_sanming_measurement);
- the gated chart blocks are byte-identical to the standalone
  TJ-017.1 function results over the same inputs; the month and
  direction cross-checks refuse inconsistent claims;
- without the gated inputs the envelope carries no dayun
  classical blocks and the steps do not fire;
- forged bindings are rejected by the resolver (altered quote
  glyph, quote bound to the wrong section, the S0 PUA form of
  the handover quote, a ref under the snapshot source).
"""
import copy
import unittest

from tianji_kb import bazi_dayun_classical as dc
from tianji_kb import bazi_registration_governance as governance
from tianji_kb import bazi_sanming_juan2_dayun_collation as reg
from tianji_kb.bazi_dayun_jie import adjacent_jie_distance
from tianji_kb.golden import run_cases
from tianji_kb.knowledge import read_json, validate_knowledge
from tianji_kb.operations.bazi_chart import chart
from tianji_kb.public_projection import project_execution
from tianji_kb.resolver import ROOT, EvidenceResolver

APPLIED = 'bazi.source.sanmingtonghui-applied'
DIR_STEP = 'bazi.phase2.dayun_classical_direction'
CONV_STEP = 'bazi.phase2.dayun_sanming_conversion'
DIR_RULE = 'bazi.rule.r038'
CONV_RULE = 'bazi.rule.r039'
GOLDEN_IDS = [
    'bazi.dayun-sanming-q1-1958-forward-male',
    'bazi.dayun-sanming-q2-1949-backward-female',
    'bazi.dayun-sanming-q3-1959-forward-female',
    'bazi.dayun-sanming-q4-1959-backward-male',
    'bazi.dayun-sanming-adv001-zero-jie-2000',
    'bazi.dayun-sanming-direction-only-1959-male']
SNAP = ROOT / 'data/quarantine/public_domain_snapshots/daizhigev20'
S3 = (SNAP / 'sanming_tonghui_applied_v1.txt').read_bytes().decode(
    'utf-8')


def _bundle():
    model = validate_knowledge(ROOT)
    return next(x for x in model['bundles'] if x['domain'] == 'bazi')


def _golden_cases():
    path = ROOT / 'data/canonical/bazi/phase2_golden.json'
    return {c['id']: c for c in read_json(path)['cases']}


class DayunSanmingRegistrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bundle = _bundle()
        cls.cases = _golden_cases()
        cls.resolver = EvidenceResolver(ROOT)

    def test_counts(self):
        knowledge = read_json(
            ROOT / 'data/canonical/bazi/phase1_knowledge.json')
        # E0348 (Shenfeng Canonical expansion): +4 chapters
        # (33), +4 sections (74), +2 terms (38), +2 rules (41),
        # +2 execution steps (42), +11 Golden cases (180).
        self.assertEqual(len(knowledge['chapters']), 33)
        self.assertEqual(len(knowledge['sections']), 74)
        self.assertEqual(len(knowledge['terms']), 38)
        self.assertEqual(len(knowledge['rules']), 41)
        execution = read_json(
            ROOT / 'data/canonical/bazi/phase2_execution.json')
        self.assertEqual(len(execution['rules']), 42)
        self.assertEqual(len(self.cases), 180)

    def test_sections_hold_the_s3_slices(self):
        sections = {s['id']: s for s in self.bundle['sections']}
        expected = {
            'bazi.section.s068': S3[58456:59197],
            'bazi.section.s069': S3[396897:397158],
            'bazi.section.s070': S3[408770:408794],
        }
        for section_id, text in expected.items():
            section = sections[section_id]
            self.assertEqual(section['text'], text, section_id)
            self.assertEqual(section['source_id'], APPLIED)
            self.assertNotIn('□', section['text'])
            for ch in section['text']:
                self.assertFalse(0xE000 <= ord(ch) <= 0xF8FF,
                                 section_id)
        # The residual 防 in s068 is the registered unresolved
        # point (stage-1 note ldy-fang-58542): exactly one, at the
        # aligned offset, outside every bound quote span.
        text = sections['bazi.section.s068']['text']
        self.assertEqual(text.count('防'), 1)
        self.assertEqual(text[58541 - 58456], '防')

    def test_chapters_and_terms(self):
        chapters = {c['id'] for c in self.bundle['chapters']}
        self.assertIn('bazi.chapter.sanming_lun_dayun', chapters)
        self.assertIn('bazi.chapter.sanming_luoluozi_dayun_witness',
                      chapters)
        terms = {t['id'] for t in self.bundle['terms']}
        self.assertIn('bazi.term.dayun_direction', terms)
        self.assertIn('bazi.term.dayun_handover', terms)

    def test_rules_bind_exactly_the_consumed_subsets(self):
        rules = {r['id']: r for r in self.bundle['rules']}
        sections = {s['id']: s for s in self.bundle['sections']}
        stage1 = {q['classical_quote_id']: q
                  for q in reg.COLLATION_QUOTES}
        for rule_id, want_ids in (
                (DIR_RULE, ['direction_rule',
                            'vol11_direction_witness']),
                (CONV_RULE, ['ratio_statement', 'ratio_derivation',
                             'worked_example', 'anti_rounding',
                             'zero_borrow_definition',
                             'zero_borrow_example', 'handover_decade',
                             'handover_approx'])):
            rule = rules[rule_id]
            refs = rule['source_refs']
            self.assertEqual(len(refs), len(want_ids), rule_id)
            for ref, quote_id in zip(refs, want_ids):
                row = stage1[quote_id]
                self.assertEqual(ref['source_id'], APPLIED, rule_id)
                self.assertEqual(ref['section_id'],
                                 row['canonical_section_id'], rule_id)
                self.assertEqual(ref['original_text'],
                                 row['s3_quote'], rule_id)
                self.assertIn(ref['original_text'],
                              sections[ref['section_id']]['text'],
                              rule_id)
            self.resolver.resolve(rule_id, 'ziping-structural-v1')
        # E0348 migration: at E0346 no rule bound any Shenfeng
        # quote and no Shenfeng rule existed. The Shenfeng
        # Canonical expansion registered the segment: exactly one
        # rule (r041) binds exactly the three consumed conversion
        # examples; the heading quotes and sf_ex2 stay unbound,
        # and r040 exists as the bingyao rule (a different
        # Variant, bound to the Shenfeng classic's bingyao
        # sections, not to any dayun quote).
        binding_rules = {}
        for rule in rules.values():
            for ref in rule['source_refs']:
                binding_rules.setdefault(ref['original_text'],
                                         set()).add(rule['id'])
        sf_by_id = {q['id']: q for q in dc.QUOTES
                    if q['id'].startswith('sf_')}
        for quote_id in ('sf_ex1', 'sf_ex3', 'sf_ex4'):
            self.assertEqual(
                binding_rules.get(sf_by_id[quote_id]['quote']),
                {'bazi.rule.r041'}, quote_id)
        for quote_id in ('sf_heading_yang', 'sf_heading_yin',
                         'sf_ex2'):
            self.assertNotIn(sf_by_id[quote_id]['quote'],
                             binding_rules, quote_id)
        self.assertIn('bazi.rule.r040', rules)

    def test_steps_validated_with_golden(self):
        execution = read_json(
            ROOT / 'data/canonical/bazi/phase2_execution.json')
        steps = {s['id']: s for s in execution['rules']}
        direction = steps[DIR_STEP]
        self.assertEqual(direction['phase1_rule_refs'], [DIR_RULE])
        self.assertEqual(direction['validation_status'], 'validated')
        self.assertEqual(direction['golden_case_ids'], GOLDEN_IDS)
        conversion = steps[CONV_STEP]
        self.assertEqual(conversion['phase1_rule_refs'], [CONV_RULE])
        self.assertEqual(conversion['validation_status'],
                         'validated')
        self.assertEqual(conversion['golden_case_ids'],
                         GOLDEN_IDS[:5])

    def test_golden_cases_fire_the_registered_steps(self):
        results = {c['id']: c for c in run_cases(ROOT, 'bazi')}
        # E0348: 169 + 11 new Golden cases (6 bingyao, 5 Shenfeng
        # conversion).
        self.assertEqual(len(results), 180)
        for case_id in GOLDEN_IDS:
            self.assertIn(DIR_STEP, results[case_id]['rule_ids'],
                          case_id)
        for case_id in GOLDEN_IDS[:5]:
            self.assertIn(CONV_STEP, results[case_id]['rule_ids'],
                          case_id)
        self.assertNotIn(CONV_STEP,
                         results[GOLDEN_IDS[5]]['rule_ids'])
        # The zero-jie witness keeps the refusal contract through
        # the registered step: unresolved, no fabricated duration.
        case = self.cases[GOLDEN_IDS[4]]
        envelope = chart(
            case['input']['year_ganzhi'],
            case['input']['month_ganzhi'],
            case['input']['day_ganzhi'],
            case['input']['hour_ganzhi'],
            dayun_classical_role=case['input']['dayun_classical_role'],
            dayun_sanming_measurement=copy.deepcopy(
                case['input']['dayun_sanming_measurement']))
        block = envelope['result']['dayun_sanming_conversion']
        self.assertEqual(block['status'], 'unresolved')
        self.assertEqual(block['reason'],
                         'zero_jie_boundary_convention_unreviewed')
        self.assertIsNone(block['duration_interval_days'])

    def test_gated_blocks_equal_standalone_functions(self):
        measured = adjacent_jie_distance(
            '1958-08-15T19:30:00+08:00', 'forward',
            expected_month_ganzhi='庚申')
        envelope = chart('戊戌', '庚申', '甲子', '甲戌',
                         dayun_classical_role='male',
                         dayun_sanming_measurement=measured)
        self.assertEqual(
            envelope['result']['dayun_classical_direction'],
            dc.classical_direction('戊戌', traditional_role='male'))
        self.assertEqual(
            envelope['result']['dayun_sanming_conversion'],
            dc.sanming_convert_measurement(measured))
        self.assertTrue(envelope['research_only'])
        self.assertFalse(
            envelope['interpretation_contract']['ai_may_explain'])

    def test_cross_checks_refuse_inconsistent_claims(self):
        backward = adjacent_jie_distance(
            '1958-08-15T19:30:00+08:00', 'backward',
            expected_month_ganzhi='庚申')
        with self.assertRaises(ValueError):
            chart('戊戌', '庚申', '甲子', '甲戌',
                  dayun_classical_role='male',
                  dayun_sanming_measurement=backward)
        forward = adjacent_jie_distance(
            '1958-08-15T19:30:00+08:00', 'forward',
            expected_month_ganzhi='庚申')
        forged = dict(forward, birth_month_ganzhi='甲子')
        with self.assertRaises(ValueError):
            chart('戊戌', '庚申', '甲子', '甲戌',
                  dayun_sanming_measurement=forged)
        tampered = dict(forward, elapsed_seconds=forward[
            'elapsed_seconds'] + 60)
        with self.assertRaises(ValueError):
            chart('戊戌', '庚申', '甲子', '甲戌',
                  dayun_sanming_measurement=tampered)

    def test_old_contract_unchanged_without_gated_inputs(self):
        envelope = chart('戊戌', '庚申', '甲子', '甲戌')
        self.assertNotIn('dayun_classical_direction',
                         envelope['result'])
        self.assertNotIn('dayun_sanming_conversion',
                         envelope['result'])
        # E0348: the Shenfeng conversion block/step are gated the
        # same way (absent without dayun_shenfeng_measurement).
        self.assertNotIn('dayun_shenfeng_conversion',
                         envelope['result'])
        fired = {step['rule_id'] for step in envelope['trace']}
        self.assertNotIn(DIR_STEP, fired)
        self.assertNotIn(CONV_STEP, fired)
        self.assertNotIn('bazi.phase2.dayun_shenfeng_conversion',
                         fired)

    def test_public_projection_strips_the_blocks(self):
        measured = adjacent_jie_distance(
            '1958-08-15T19:30:00+08:00', 'forward',
            expected_month_ganzhi='庚申')
        envelope = chart('戊戌', '庚申', '甲子', '甲戌',
                         dayun_classical_role='male',
                         dayun_sanming_measurement=measured)
        projected = project_execution(copy.deepcopy(envelope))
        for container in (projected.get('chart'),
                          projected.get('result')):
            if isinstance(container, dict):
                self.assertNotIn('dayun_classical_direction',
                                 container)
                self.assertNotIn('dayun_sanming_conversion',
                                 container)

    def test_forged_bindings_are_rejected(self):
        # The resolver holds the bundle entities; forging appends
        # one bad ref to the live rule and restores it afterwards
        # (the ren batch's pattern).
        def _assert_forged_rejected(rule_id, forged_ref):
            rule = self.resolver.entities[rule_id][1]
            original_refs = rule['source_refs']
            rule['source_refs'] = original_refs + [forged_ref]
            try:
                with self.assertRaises(ValueError):
                    self.resolver.resolve(rule_id,
                                          'ziping-structural-v1')
            finally:
                rule['source_refs'] = original_refs

        rules = {r['id']: r for r in self.bundle['rules']}
        direction_ref = rules[DIR_RULE]['source_refs'][0]
        decade_ref = next(
            ref for ref in rules[CONV_RULE]['source_refs']
            if '十周年方换一运' in ref['original_text'])
        # Altered quote glyph.
        _assert_forged_rejected(DIR_RULE, {
            'source_id': APPLIED, 'section_id': 'bazi.section.s068',
            'original_text': direction_ref['original_text'].replace(
                '阳男', '阳安', 1),
            'role': 'classical'})
        # Direction quote bound to the wrong section.
        _assert_forged_rejected(DIR_RULE, {
            'source_id': APPLIED, 'section_id': 'bazi.section.s069',
            'original_text': direction_ref['original_text'],
            'role': 'classical'})
        # The handover quote in its snapshot (PUA) form instead of
        # the applied form held by the section.
        _assert_forged_rejected(CONV_RULE, {
            'source_id': APPLIED, 'section_id': 'bazi.section.s068',
            'original_text': decade_ref['original_text'].replace(
                '算', chr(0xED92), 1),
            'role': 'classical'})
        # A ref under the snapshot source instead of the applied
        # text source.
        _assert_forged_rejected(CONV_RULE, {
            'source_id': 'bazi.source.sanmingtonghui',
            'section_id': 'bazi.section.s068',
            'original_text': rules[CONV_RULE]['source_refs'][0][
                'original_text'],
            'role': 'classical'})

    def test_governance_flip_consistency(self):
        record = governance.GOVERNANCE_DAYUN_SANMING_RECORD
        self.assertEqual(record['phase1_rules_added'],
                         [DIR_RULE, CONV_RULE])
        self.assertEqual(record['phase2_rules_added'],
                         [DIR_STEP, CONV_STEP])
        self.assertEqual(record['golden_cases_added'], GOLDEN_IDS)
        row = next(r for r in governance.REGISTRATION_INVENTORY
                   if r['item'] == 'dayun-classical-variants')
        self.assertEqual(row['disposition'], 'registered')
        # E0348: the Shenfeng segment flipped inside the row.
        self.assertIn('registered', row['segments']['shenfeng'])
        self.assertNotIn('maintained_pending',
                         row['segments']['shenfeng'])


if __name__ == '__main__':
    unittest.main()
