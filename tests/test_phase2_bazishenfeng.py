"""Governance Shenfeng Canonical expansion (E0348) sealed
registration tests: the new classic bazi.classic.shenfeng,
chapters/sections s071 (bingyao definition section), s072
(zhengguan tension window), s073 (《起大运法》), the Ditiansui
zhonghe counterweight window s074 inside the existing classic,
terms bingyao / dayun_shenfeng_conversion, Phase1 rules r040
(bingyao) and r041 (Shenfeng conversion), Phase2 steps
bazi.phase2.bingyao_assessment and
bazi.phase2.dayun_shenfeng_conversion.

Pinned here:
- the new classic mirrors the existing four classics' entity
  structure exactly (same five fields; body_stage=quarantine as
  with Sanming / Xieji, whose Canonical presence is section-level
  slices of the quarantine snapshot text);
- the four sections hold exactly the adjudicated snapshot slices
  (verbatim, PUA-free and box-free), no more sections than the
  consumed / registered citation sets require;
- r040 binds exactly the four consumed bingyao quotes (two
  definitions + the two encoded pair sentences); r041 binds
  exactly the three consumed Shenfeng conversion examples; the
  registered-only quotes (earth example, procedure sentence,
  no-disease clause, zhengguan tension, Ditiansui counterweight,
  the two Shenfeng headings and sf_ex2) are bound by NO rule;
- both steps are validated and fire on real Golden cases (the
  TJ-013 bingyao witness charts and the TJ-017.1 measurement
  witnesses, including the ADV-001 zero-jie unresolved case)
  through the trace, via the gated chart kwargs bingyao_variant /
  dayun_shenfeng_measurement;
- the gated chart blocks equal the standalone Variant results;
  the month / direction cross-checks refuse inconsistent claims;
- without the gated inputs the envelope carries neither block
  and the steps do not fire;
- forged bindings are rejected by the resolver (altered quote
  glyph, quote bound to the wrong section, a non-consumed
  registered quote presented as a rule ref).
"""
import copy
import unittest

from tianji_kb import bazi_bingyao as by
from tianji_kb import bazi_dayun_classical as dc
from tianji_kb import bazi_registration_governance as governance
from tianji_kb.bazi_dayun_jie import adjacent_jie_distance
from tianji_kb.engine import execute
from tianji_kb.golden import run_cases
from tianji_kb.knowledge import read_json, validate_knowledge
from tianji_kb.operations.bazi_chart import chart
from tianji_kb.public_projection import project_execution
from tianji_kb.resolver import ROOT, EvidenceResolver

SHENFENG = 'bazi.source.shenfeng'
DITIANSUI = 'bazi.source.ditiansui-spouse'
BINGYAO_STEP = 'bazi.phase2.bingyao_assessment'
SHENFENG_STEP = 'bazi.phase2.dayun_shenfeng_conversion'
BINGYAO_RULE = 'bazi.rule.r040'
SHENFENG_RULE = 'bazi.rule.r041'
BINGYAO_GOLDEN_IDS = [
    'bazi.bingyao-wealth-disease-medicine',
    'bazi.bingyao-wealth-disease-no-medicine',
    'bazi.bingyao-medicine-without-disease',
    'bazi.bingyao-peer-class-boundary-jiecai',
    'bazi.bingyao-foodwound-disease-medicine',
    'bazi.bingyao-dual-pair-wealth-only']
SHENFENG_GOLDEN_IDS = [
    'bazi.dayun-shenfeng-q1-1958-forward-male',
    'bazi.dayun-shenfeng-q2-1949-backward-female',
    'bazi.dayun-shenfeng-q3-1959-forward-female',
    'bazi.dayun-shenfeng-q4-1959-backward-male',
    'bazi.dayun-shenfeng-adv001-zero-jie-2000']
SNAP = ROOT / 'data/quarantine/public_domain_snapshots/daizhigev20'
SF = (SNAP / 'shenfeng_tongkao.txt').read_bytes().decode('utf-8')
DT = (SNAP / 'ditiansui_chanwei.txt').read_bytes().decode('utf-8')
BY_QUOTES = {q['id']: q for q in by.QUOTES}
DC_QUOTES = {q['id']: q for q in dc.QUOTES}


def _bundle():
    model = validate_knowledge(ROOT)
    return next(x for x in model['bundles'] if x['domain'] == 'bazi')


def _golden_cases():
    path = ROOT / 'data/canonical/bazi/phase2_golden.json'
    return {c['id']: c for c in read_json(path)['cases']}


class ShenfengExpansionRegistrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bundle = _bundle()
        cls.cases = _golden_cases()
        cls.resolver = EvidenceResolver(ROOT)

    def test_counts(self):
        knowledge = read_json(
            ROOT / 'data/canonical/bazi/phase1_knowledge.json')
        # E0352 (governance tiaohou Canonical construction): +1 classic (qiongtong), +11 chapters, +110 sections (s075-s184), +1 term (tiaohou), +10 rules (r042-r051), +1 contract step, +30 Golden cases (210).
        self.assertEqual(len(knowledge['classics']), 6)
        self.assertEqual(len(knowledge['chapters']), 44)
        self.assertEqual(len(knowledge['sections']), 184)
        self.assertEqual(len(knowledge['terms']), 39)
        self.assertEqual(len(knowledge['rules']), 51)
        execution = read_json(
            ROOT / 'data/canonical/bazi/phase2_execution.json')
        self.assertEqual(len(execution['rules']), 43)
        self.assertEqual(len(self.cases), 210)

    def test_classic_mirrors_existing_structure(self):
        classics = {c['id']: c for c in self.bundle['classics']}
        existing = classics['bazi.classic.ditiansui']
        shenfeng = classics['bazi.classic.shenfeng']
        self.assertEqual(set(shenfeng), set(existing))
        # Sanming's extra source_ids key is its pre-existing
        # dual-source (S0 + applied text) special case; Shenfeng
        # has no dual track and must not grow the key.
        sanming = classics['bazi.classic.sanming_tonghui']
        self.assertEqual(set(sanming), set(shenfeng) | {'source_ids'})
        self.assertNotIn('source_ids', shenfeng)
        self.assertEqual(shenfeng['name'], '神峰通考')
        self.assertEqual(shenfeng['source_id'], SHENFENG)
        # body_stage quarantine, as with Sanming / Xieji: the
        # classic's Canonical presence is section-level slices of
        # the quarantine snapshot text, no separate cleaned body.
        self.assertEqual(shenfeng['body_stage'], 'quarantine')
        chapters = {c['id']: c for c in self.bundle['chapters']}
        for chapter_id in ('bazi.chapter.shenfeng_bingyao',
                           'bazi.chapter.shenfeng_zhengguan',
                           'bazi.chapter.shenfeng_qi_dayun_fa',
                           'bazi.chapter.ditiansui_zhonghe'):
            self.assertIn(chapter_id, chapters)
            self.assertEqual(
                set(chapters[chapter_id]),
                {'id', 'domain', 'name', 'classic_id', 'locator'})

    def test_sections_hold_the_snapshot_slices(self):
        sections = {s['id']: s for s in self.bundle['sections']}
        expected = {
            'bazi.section.s071': (SF[7019:7680], SHENFENG,
                                  'bazi.classic.shenfeng'),
            'bazi.section.s072': (SF[10010:10041], SHENFENG,
                                  'bazi.classic.shenfeng'),
            'bazi.section.s073': (SF[85001:85246], SHENFENG,
                                  'bazi.classic.shenfeng'),
            'bazi.section.s074': (DT[43767:43825], DITIANSUI,
                                  'bazi.classic.ditiansui'),
        }
        for section_id, (text, source_id, classic_id) in \
                expected.items():
            section = sections[section_id]
            self.assertEqual(section['text'], text, section_id)
            self.assertEqual(section['source_id'], source_id,
                             section_id)
            self.assertEqual(section['classic_id'], classic_id,
                             section_id)
            self.assertNotIn('□', section['text'])
            for ch in section['text']:
                self.assertFalse(0xE000 <= ord(ch) <= 0xF8FF,
                                 section_id)
        # Every registered bingyao / dayun-Shenfeng quote sits
        # inside its bound section, verbatim.
        for quote in by.QUOTES:
            self.assertIn(quote['quote'],
                          sections[quote['section_id']]['text'],
                          quote['id'])
        for quote in dc.QUOTES:
            if quote['id'].startswith('sf_'):
                self.assertIn(
                    quote['quote'],
                    sections['bazi.section.s073']['text'],
                    quote['id'])

    def test_rules_bind_exactly_the_consumed_subsets(self):
        rules = {r['id']: r for r in self.bundle['rules']}
        sections = {s['id']: s for s in self.bundle['sections']}
        bingyao = rules[BINGYAO_RULE]
        self.assertEqual(
            [(ref['source_id'], ref['section_id'],
              ref['original_text']) for ref in
             bingyao['source_refs']],
            [(SHENFENG, 'bazi.section.s071',
              BY_QUOTES[qid]['quote']) for qid in (
                  'disease_definition', 'medicine_definition',
                  'wealth_pair', 'food_pair')])
        shenfeng = rules[SHENFENG_RULE]
        self.assertEqual(
            [(ref['source_id'], ref['section_id'],
              ref['original_text']) for ref in
             shenfeng['source_refs']],
            [(SHENFENG, 'bazi.section.s073',
              DC_QUOTES[qid]['quote']) for qid in (
                  'sf_ex1', 'sf_ex3', 'sf_ex4')])
        for rule_id in (BINGYAO_RULE, SHENFENG_RULE):
            for ref in rules[rule_id]['source_refs']:
                self.assertIn(ref['original_text'],
                              sections[ref['section_id']]['text'],
                              rule_id)
            self.resolver.resolve(rule_id, 'ziping-structural-v1')
        # The registered-only quotes are bound by NO rule: the
        # bingyao earth example / procedure sentence / no-disease
        # clause / zhengguan tension / Ditiansui counterweight,
        # and the Shenfeng headings / sf_ex2 (direction
        # corroboration only).
        all_refs = {ref['original_text'] for r in rules.values()
                    for ref in r['source_refs']}
        for quote_id in ('earth_example', 'procedure_zhong',
                         'no_disease_clause', 'zhengguan_tension',
                         'ditiansui_counterweight'):
            self.assertNotIn(BY_QUOTES[quote_id]['quote'], all_refs,
                             quote_id)
        for quote_id in ('sf_heading_yang', 'sf_heading_yin',
                         'sf_ex2'):
            self.assertNotIn(DC_QUOTES[quote_id]['quote'], all_refs,
                             quote_id)

    def test_steps_validated_with_golden(self):
        execution = read_json(
            ROOT / 'data/canonical/bazi/phase2_execution.json')
        steps = {s['id']: s for s in execution['rules']}
        bingyao = steps[BINGYAO_STEP]
        self.assertEqual(bingyao['phase1_rule_refs'], [BINGYAO_RULE])
        self.assertEqual(bingyao['validation_status'], 'validated')
        self.assertEqual(bingyao['golden_case_ids'],
                         BINGYAO_GOLDEN_IDS)
        shenfeng = steps[SHENFENG_STEP]
        self.assertEqual(shenfeng['phase1_rule_refs'],
                         [SHENFENG_RULE])
        self.assertEqual(shenfeng['validation_status'], 'validated')
        self.assertEqual(shenfeng['golden_case_ids'],
                         SHENFENG_GOLDEN_IDS)

    def test_golden_cases_fire_the_registered_steps(self):
        results = {c['id']: c for c in run_cases(ROOT, 'bazi')}
        self.assertEqual(len(results), 210)
        for case_id in BINGYAO_GOLDEN_IDS:
            self.assertIn(BINGYAO_STEP,
                          results[case_id]['rule_ids'], case_id)
        for case_id in SHENFENG_GOLDEN_IDS:
            self.assertIn(SHENFENG_STEP,
                          results[case_id]['rule_ids'], case_id)
        # The zero-jie witness keeps the refusal contract through
        # the registered Shenfeng step: unresolved, no fabricated
        # duration.
        case = self.cases[SHENFENG_GOLDEN_IDS[4]]
        envelope = chart(
            case['input']['year_ganzhi'],
            case['input']['month_ganzhi'],
            case['input']['day_ganzhi'],
            case['input']['hour_ganzhi'],
            dayun_shenfeng_measurement=copy.deepcopy(
                case['input']['dayun_shenfeng_measurement']))
        block = envelope['result']['dayun_shenfeng_conversion']
        self.assertEqual(block['status'], 'unresolved')
        self.assertEqual(
            block['reason'],
            'zero_day_count_not_exemplified_in_text')
        self.assertNotIn('duration_interval_days', block)

    def test_gated_blocks_equal_standalone_functions(self):
        measured = adjacent_jie_distance(
            '1958-08-15T19:30:00+08:00', 'forward',
            expected_month_ganzhi='庚申')
        envelope = chart('戊戌', '庚申', '甲子', '甲戌',
                         bingyao_variant='bingyao-shenfeng-v1',
                         dayun_shenfeng_measurement=measured)
        self.assertEqual(
            envelope['result']['dayun_shenfeng_conversion'],
            dc.shenfeng_convert_measurement(measured))
        block = envelope['result']['bingyao_assessment']
        facts = [{'pillar': row['pillar'], 'stem': row['stem'],
                  'ten_god': row['ten_god']}
                 for row in envelope['result']['stem_ten_gods']
                 if row['pillar'] != 'day']
        standalone = by.bingyao_lookup('甲', facts)
        for key, value in standalone.items():
            self.assertEqual(block[key], value, key)
        self.assertEqual(block['evidence_binding'],
                         'registered_phase1_phase2')
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
                  dayun_shenfeng_measurement=backward)
        forward = adjacent_jie_distance(
            '1958-08-15T19:30:00+08:00', 'forward',
            expected_month_ganzhi='庚申')
        forged = dict(forward, birth_month_ganzhi='甲子')
        with self.assertRaises(ValueError):
            chart('戊戌', '庚申', '甲子', '甲戌',
                  dayun_shenfeng_measurement=forged)
        tampered = dict(forward, elapsed_whole_days=(
            forward['elapsed_whole_days'] + 1))
        with self.assertRaises(ValueError):
            chart('戊戌', '庚申', '甲子', '甲戌',
                  dayun_shenfeng_measurement=tampered)
        with self.assertRaises(ValueError):
            execute('bazi', {'value': '1958-08-15T19:30:00+08:00',
                             'zone': 'Asia/Shanghai',
                             'dayun_shenfeng_measurement': forward})

    def test_old_contract_unchanged_without_gated_inputs(self):
        envelope = chart('戊戌', '庚申', '甲子', '甲戌')
        self.assertNotIn('bingyao_assessment', envelope['result'])
        self.assertNotIn('dayun_shenfeng_conversion',
                         envelope['result'])
        fired = {step['rule_id'] for step in envelope['trace']}
        self.assertNotIn(BINGYAO_STEP, fired)
        self.assertNotIn(SHENFENG_STEP, fired)

    def test_public_projection_strips_the_blocks(self):
        measured = adjacent_jie_distance(
            '1958-08-15T19:30:00+08:00', 'forward',
            expected_month_ganzhi='庚申')
        envelope = chart('戊戌', '庚申', '甲子', '甲戌',
                         bingyao_variant='bingyao-shenfeng-v1',
                         dayun_shenfeng_measurement=measured)
        projected = project_execution(copy.deepcopy(envelope))
        for container in (projected.get('chart'),
                          projected.get('result')):
            if isinstance(container, dict):
                self.assertNotIn('bingyao_assessment', container)
                self.assertNotIn('dayun_shenfeng_conversion',
                                 container)

    def test_forged_bindings_are_rejected(self):
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
        disease_ref = rules[BINGYAO_RULE]['source_refs'][0]
        # Altered quote glyph.
        _assert_forged_rejected(BINGYAO_RULE, {
            'source_id': SHENFENG, 'section_id': 'bazi.section.s071',
            'original_text': disease_ref['original_text'].replace(
                '病', '疾', 1),
            'role': 'classical'})
        # Encoded pair quote bound to the wrong section (the
        # zhengguan window does not hold it).
        _assert_forged_rejected(BINGYAO_RULE, {
            'source_id': SHENFENG, 'section_id': 'bazi.section.s072',
            'original_text': BY_QUOTES['wealth_pair']['quote'],
            'role': 'classical'})
        # (The counterweight quote is NOT a resolver case: bound
        # to its own section s074 it is a well-formed citation --
        # the discipline that it never serves as an r040 rule ref
        # is semantic and is pinned by the exact-subset test, not
        # by the resolver.)
        # A consumed Shenfeng example bound to the wrong section
        # (the bingyao section does not hold it), and an altered
        # glyph in another consumed example. (Binding discipline
        # for in-section but non-consumed quotes -- sf_ex2, the
        # headings -- is pinned by the exact-subset test above,
        # not by the resolver.)
        _assert_forged_rejected(SHENFENG_RULE, {
            'source_id': SHENFENG, 'section_id': 'bazi.section.s071',
            'original_text': DC_QUOTES['sf_ex1']['quote'],
            'role': 'classical'})
        ex4_ref = rules[SHENFENG_RULE]['source_refs'][2]
        _assert_forged_rejected(SHENFENG_RULE, {
            'source_id': SHENFENG, 'section_id': 'bazi.section.s073',
            'original_text': ex4_ref['original_text'].replace(
                '三岁', '四岁', 1),
            'role': 'classical'})

    def test_module_quote_section_bindings(self):
        for quote in by.QUOTES:
            if quote['id'] == 'zhengguan_tension':
                want = 'bazi.section.s072'
            elif quote['id'] == 'ditiansui_counterweight':
                want = 'bazi.section.s074'
            else:
                want = 'bazi.section.s071'
            self.assertEqual(quote['section_id'], want, quote['id'])
        for quote in dc.QUOTES:
            if quote['id'].startswith('sf_'):
                self.assertEqual(quote['source_id'], SHENFENG,
                                 quote['id'])
                self.assertEqual(quote['source_section_id'],
                                 'bazi.section.s073', quote['id'])

    def test_governance_flip_consistency(self):
        record = governance.GOVERNANCE_SHENFENG_RECORD
        self.assertEqual(record['phase1_rules_added'],
                         [BINGYAO_RULE, SHENFENG_RULE])
        self.assertEqual(record['phase2_rules_added'],
                         [BINGYAO_STEP, SHENFENG_STEP])
        self.assertEqual(record['golden_cases_added'],
                         BINGYAO_GOLDEN_IDS + SHENFENG_GOLDEN_IDS)
        rows = {r['item']: r for r in
                governance.REGISTRATION_INVENTORY}
        bingyao = rows['bingyao-shenfeng-v1']
        self.assertEqual(bingyao['disposition'], 'registered')
        self.assertEqual(bingyao['phase1_rule_id'], BINGYAO_RULE)
        self.assertEqual(bingyao['phase2_rule_id'], BINGYAO_STEP)
        dayun = rows['dayun-classical-variants']
        self.assertEqual(dayun['additional_phase1_rule_ids'],
                         ['bazi.rule.r039', 'bazi.rule.r041'])
        self.assertEqual(dayun['additional_phase2_rule_ids'],
                         ['bazi.phase2.dayun_sanming_conversion',
                          'bazi.phase2.dayun_shenfeng_conversion'])
        self.assertIn('registered', dayun['segments']['shenfeng'])
        for item in ('dayun-compose', 'dayun-timeline-view'):
            self.assertIn('inherited_registered_phase1_phase2',
                          rows[item]['reason'])


if __name__ == '__main__':
    unittest.main()
