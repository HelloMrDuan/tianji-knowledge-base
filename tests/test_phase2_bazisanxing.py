"""TJ-018.3 batch 1 (E0333): sealed regression for the sanxing fact
execution binding -- Phase1 bazi.rule.r031 and Phase2 step
bazi.phase2.branch_punishment_facts (design
docs/product/TJ0183_EXECUTION_BINDING_DESIGN.md sections 2/4/5/7).

Runs only in the assembled offline acceptance (needs the sealed
canonical snapshot with the batch-1 registration); NOT public CI,
same partition rule as the other Phase2 bazi suites. Pins:

- the execution step exists in the bazi Phase2 contract, is
  executable + validated, references exactly bazi.rule.r031, and
  its golden_case_ids are the ten real-chart cases converted from
  the public sanxing impl Golden;
- r031 resolves through EvidenceResolver to exactly the six
  definitional quotes of bazi.section.s060 (the adjudication
  register's group-table / self-punishment citation union), every
  quote a substring of the sealed section text; a forged quote in
  an in-memory copy of the rule is rejected (fail-closed);
- the Golden harness really fires the step for all ten cases and
  the step output equals the fact function applied to the case
  branches (and the registered expectations);
- separation: the fact step never appears in any RuleMatch or
  sufficient_rule, and existing adjudication envelopes keep their
  sufficient_rule verbatim with the gate open or closed;
- section 7 equivalence over all 119 pre-existing sealed Golden
  pillar inputs plus the 10 real birth charts: gate closed is
  byte-identical to the previous behaviour (the whole Golden
  suite still passes unchanged), gate open differs only inside
  the closed delta list (new result key + scope suffix, one
  inserted trace step, the step's evidence and executed_calculation
  entries, envelope research marking, fact_ref index shifts with
  identical referents);
- the engine gate: the flag without allow_research is rejected;
  the public projection strips the fact block from an enabled
  envelope.
"""
import copy
import itertools
import json
import unittest
from pathlib import Path

from tianji_kb import bazi_sanxing_facts as impl
from tianji_kb.calendar import calendar
from tianji_kb.engine import execute
from tianji_kb.golden import run_cases
from tianji_kb.knowledge import read_json
from tianji_kb.operations.bazi_chart import chart
from tianji_kb.public_projection import project_execution
from tianji_kb.resolver import EvidenceResolver

ROOT = Path(__file__).resolve().parents[1]
STEP = 'bazi.phase2.branch_punishment_facts'
RULE = 'bazi.rule.r031'
CASE_IDS = [
    'bazi.sanxing-fact-chou-wei-partial-no-edges',
    'bazi.sanxing-fact-yin-shen-only',
    'bazi.sanxing-fact-group2-full',
    'bazi.sanxing-fact-group3-full',
    'bazi.sanxing-fact-zi-mao-bidirectional',
    'bazi.sanxing-fact-self-chen-double',
    'bazi.sanxing-fact-g6b-self-you-triple',
    'bazi.sanxing-fact-empty-self-singles',
    'bazi.sanxing-fact-zi-mao-multi-pillar',
    'bazi.sanxing-fact-group2-partial-with-edge',
]
SUBSET_SOURCES = {'sm3.enum_opening', 'sm3.enum_group4_partial',
                  'sm3.summary_groups', 'sm3.counting_method',
                  'sm3.wuen_core', 'sm3.zixing_definition'}
SCOPE_SUFFIX = ('；研究用三刑结构事实（只报组态、有向对与自刑在场，'
                '不作吉凶解释）')


def _golden_cases():
    obj = read_json(ROOT / 'data/canonical/bazi/phase2_golden.json')
    return obj['cases']


def _canon(envelope):
    """Replace #/trace/N/output refs with rule-id refs so index
    shifts from the inserted step do not masquerade as changes."""
    trace = envelope['trace']
    text = json.dumps(envelope, ensure_ascii=False, sort_keys=True)
    for i in range(len(trace) - 1, -1, -1):
        text = text.replace(f'#/trace/{i}/output',
                            f"#/trace/{trace[i]['rule_id']}/output")
    return json.loads(text)


def _delta_only(test, off, on):
    """Assert the gate-open envelope differs from the gate-closed
    one only inside the design section 7.2 closed list."""
    off = _canon(off)
    on = _canon(on)
    # result: only the new key and the production_scope suffix.
    off_r, on_r = dict(off['result']), dict(on['result'])
    facts = on_r.pop('branch_punishment_facts')
    test.assertEqual(set(facts), {'directed_pairs',
                                  'group_configurations',
                                  'self_punishments', 'names'})
    test.assertIsNone(facts['names'])
    # The scope sentence is inserted at the step's assembly point
    # (later scope sentences may follow it), so the invariant is:
    # removing the one occurrence restores the closed scope.
    on_scope = on_r.pop('production_scope')
    test.assertEqual(on_scope.count(SCOPE_SUFFIX), 1)
    test.assertEqual(on_scope.replace(SCOPE_SUFFIX, '', 1),
                     off_r.pop('production_scope'))
    test.assertEqual(on_r, off_r)
    # trace: exactly one inserted step, everything else identical.
    off_t, on_t = off['trace'], on['trace']
    test.assertEqual([s['rule_id'] for s in on_t].count(STEP), 1)
    test.assertEqual([s for s in on_t if s['rule_id'] != STEP], off_t)
    step = [s for s in on_t if s['rule_id'] == STEP][0]
    test.assertEqual(step['output'], facts)
    # evidence: only the new step's entries are added (the envelope
    # evidence is a hash-keyed dict of resolved refs).
    off_e = {(k, e['rule_id']) for k, e in off['evidence'].items()}
    on_e = {(k, e['rule_id']) for k, e in on['evidence'].items()}
    test.assertTrue(off_e <= on_e)
    test.assertTrue(all(r == STEP for _, r in on_e - off_e))
    test.assertEqual(len(on['evidence']) - len(off['evidence']),
                     len(step['evidence_ids']))
    # rule_matches: only the step's executed_calculation entry added;
    # the fact step never carries an algorithm_selection match.
    off_m = [m for m in off['rule_matches'] if m['rule_id'] != STEP]
    on_m = [m for m in on['rule_matches'] if m['rule_id'] != STEP]
    test.assertEqual(on_m, off_m)
    added = [m for m in on['rule_matches'] if m['rule_id'] == STEP]
    test.assertEqual(len(added), 1)
    test.assertEqual(added[0]['kind'], 'executed_calculation')
    test.assertTrue(added[0]['matched'])
    # envelope: only the research marking may be added.
    for key in set(off) | set(on):
        if key in ('result', 'trace', 'evidence', 'rule_matches'):
            continue
        if key == 'research_only':
            test.assertTrue(on.get('research_only'))
            continue
        if key == 'interpretation_contract':
            oc, nc = dict(off[key]), dict(on[key])
            test.assertFalse(nc['ai_may_explain'])
            nc['ai_may_explain'] = oc['ai_may_explain']
            test.assertEqual(nc, oc)
            continue
        test.assertEqual(on.get(key), off.get(key), key)


class RegistrationContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.resolver = EvidenceResolver()
        cls.contract = cls.resolver.contracts['bazi']

    def test_execution_step_registered(self):
        rules = {r['id']: r for r in self.contract['rules']}
        self.assertIn(STEP, rules)
        rule = rules[STEP]
        self.assertEqual(rule['execution_status'], 'executable')
        self.assertEqual(rule['validation_status'], 'validated')
        self.assertEqual(rule['phase1_rule_refs'], [RULE])
        self.assertEqual(rule['regression_test'],
                         'tests/test_phase2_bazisanxing.py')
        self.assertEqual(rule['golden_case_ids'], CASE_IDS)

    def test_phase1_rule_resolves_to_s060_subset(self):
        refs = self.resolver.resolve(RULE, 'ziping-structural-v1')
        self.assertEqual(len(refs), 6)
        for ref in refs:
            self.assertEqual(ref['rule_id'], RULE)
            self.assertEqual(ref['source_id'],
                             'bazi.source.sanmingtonghui-applied')
            self.assertEqual(ref['section_id'], 'bazi.section.s060')
            self.assertNotEqual(ref['evidence_level'], 'D')
        section = self.resolver.entities['bazi.section.s060'][1]
        for ref in refs:
            self.assertIn(ref['original_text'], section['text'])

    def test_subset_covers_group_table_and_self_union(self):
        from tianji_kb import bazi_sanxing_fact_adjudication as adj
        union = set()
        for group in adj.GROUP_TABLE['groups']:
            union.update(group['evidence_refs'])
        union.update(adj.GROUP_TABLE['self_punishment']
                     ['evidence_refs'])
        self.assertEqual(union, SUBSET_SOURCES)

    def test_forged_quote_rejected_fail_closed(self):
        resolver = EvidenceResolver()
        kind, rule = resolver.entities[RULE]
        forged = copy.deepcopy(rule)
        forged['source_refs'] = [dict(forged['source_refs'][0],
                                      original_text='伪造引文不在节内')]
        resolver.entities[RULE] = (kind, forged)
        with self.assertRaises(ValueError):
            resolver.resolve(RULE, 'ziping-structural-v1')

    def test_missing_step_registration_fails_closed(self):
        # A trace step naming an unregistered rule must raise, never
        # silently pass: this is the rollback-state behaviour (new
        # code against the P1 snapshot rejects the gated path).
        from tianji_kb.resolver import ExecutionTrace
        trace = ExecutionTrace('bazi', 'ziping-structural-v1',
                               resolver=self.resolver)
        ghost = 'bazi.phase2.no_such_step_e0333'
        with self.assertRaises(ValueError):
            trace.add(ghost, {'branches': []}, {})


class GoldenFireTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = {r['id']: r for r in run_cases(ROOT, 'bazi')}
        cls.cases = {c['id']: c for c in _golden_cases()}

    def test_all_preexisting_cases_still_pass(self):
        # run_cases asserts every case's expectations; reaching this
        # point means the default surface is unchanged for all 119
        # pre-existing pillar inputs.
        # E0335: four ganzhi strength cases joined the golden file
        # (129 + 4 = 133 rows); they pass the same harness.
        # E0339: nine luren route cases joined (133 + 9 = 142 rows).
        self.assertEqual(len(self.rows), 142)

    def test_new_cases_fire_the_step(self):
        for case_id in CASE_IDS:
            self.assertIn(STEP, self.rows[case_id]['rule_ids'])

    def test_step_output_equals_fact_function(self):
        for case_id in CASE_IDS:
            case = self.cases[case_id]
            out = chart(**case['input'])
            steps = [s for s in out['trace'] if s['rule_id'] == STEP]
            self.assertEqual(len(steps), 1, case_id)
            branches = [case['input'][k][1] for k in
                        ('year_ganzhi', 'month_ganzhi', 'day_ganzhi',
                         'hour_ganzhi')]
            expected = impl.reviewed_branch_punishment_facts(branches)
            self.assertEqual(steps[0]['output'], expected, case_id)
            self.assertEqual(out['result']['branch_punishment_facts'],
                             expected, case_id)
            self.assertEqual(
                case['expected']['branch_punishment_facts'], expected,
                case_id)


class SeparationTests(unittest.TestCase):
    def test_fact_step_never_a_match_or_sufficient_rule(self):
        for case in _golden_cases():
            out = chart(**case['input'])
            for match in out['rule_matches']:
                if match['rule_id'] == STEP:
                    self.assertEqual(match['kind'],
                                     'executed_calculation')
            assessment = out['result'].get('strength_assessment')
            if assessment is not None:
                why = assessment.get('why_not_indeterminate') or {}
                self.assertNotEqual(why.get('sufficient_rule'), STEP)
                self.assertNotIn(STEP,
                                 assessment.get('matched_rule_ids', []))

    def test_strength_witness_unchanged_with_gate_open(self):
        birth = {'value': '1981-12-21T00:30:00+08:00',
                 'strength_variant': 'bazi-strength-adjudication-v1'}
        off = execute('bazi', dict(birth), allow_research=True)
        on = execute('bazi', dict(birth, include_punishment_facts=True),
                     allow_research=True)
        # The assessment embeds trace fact_refs by index; the inserted
        # fact step shifts later indices (design section 7.2 allows
        # exactly this shift). Compare with refs normalised to the
        # rule each index points at: everything else must be equal.
        self.assertEqual(
            _canon({'result': on['result'],
                    'trace': on['trace']})['result']
            ['strength_assessment'],
            _canon({'result': off['result'],
                    'trace': off['trace']})['result']
            ['strength_assessment'])
        why = on['result']['strength_assessment'][
            'why_not_indeterminate']
        # E0335: the water witness now exits through its registered
        # step (bazi.rule.r034); the verdict content is unchanged.
        self.assertEqual(
            why['sufficient_rule'],
            'bazi.phase2.strength_pure_generating_support_water')
        self.assertNotIn('sufficient_predicate', why)


class EquivalenceTests(unittest.TestCase):
    def test_129_charts_open_differs_only_in_closed_list(self):
        inputs = []
        for case in _golden_cases():
            if case['id'] in CASE_IDS:
                continue
            inputs.append(dict(case['input']))
        impl_golden = json.loads(
            (ROOT / 'tests/golden_tj0123_sanxing_impl.json').read_text(
                encoding='utf-8'))
        for case in impl_golden['cases']:
            cal = calendar(case['birth'])
            inputs.append({'year_ganzhi': cal['year_ganzhi'],
                           'month_ganzhi': cal['month_ganzhi'],
                           'day_ganzhi': cal['day_ganzhi'],
                           'hour_ganzhi': cal['hour_ganzhi']})
        # E0335: the golden file grew by four ganzhi cases
        # (133 - 10 sanxing cases + 10 impl births = 133 inputs).
        # E0339: the golden file grew by nine luren route cases
        # (142 - 10 sanxing cases + 10 impl births = 142 inputs);
        # those inputs carry pattern_variant, and the registered
        # route step appears identically in both gate states, so
        # the sanxing closed-list delta is unaffected.
        self.assertEqual(len(inputs), 142)
        for inputs_one in inputs:
            off = chart(**inputs_one)
            self.assertNotIn('branch_punishment_facts', off['result'])
            self.assertNotIn(STEP,
                             [s['rule_id'] for s in off['trace']])
            on = chart(**dict(inputs_one, include_punishment_facts=True))
            _delta_only(self, off, on)

    def test_exhaustive_guard_still_holds(self):
        branches = ['子', '丑', '寅', '卯', '辰', '巳',
                    '午', '未', '申', '酉', '戌', '亥']
        for combo in itertools.product(branches, repeat=4):
            out = impl.reviewed_branch_punishment_facts(list(combo))
            for pair in out['directed_pairs']:
                self.assertNotEqual(
                    (pair['actor_branch'], pair['target_branch']),
                    ('未', '丑'))
            self.assertIsNone(out['names'])


class GateAndProjectionTests(unittest.TestCase):
    PILLARS = {'year_ganzhi': '丙寅', 'month_ganzhi': '癸巳',
               'day_ganzhi': '戊午', 'hour_ganzhi': '庚申'}

    def test_engine_gate_rejects_without_research_mode(self):
        with self.assertRaises(ValueError):
            execute('bazi', dict(self.PILLARS,
                                 include_punishment_facts=True))

    def test_engine_gate_accepts_in_research_mode(self):
        out = execute('bazi', dict(self.PILLARS,
                                   include_punishment_facts=True),
                      allow_research=True)
        self.assertIn('branch_punishment_facts', out['result'])
        self.assertTrue(out['research_only'])
        self.assertFalse(
            out['interpretation_contract']['ai_may_explain'])

    def test_default_engine_call_has_no_fact_block(self):
        out = execute('bazi', dict(self.PILLARS), allow_research=True)
        self.assertNotIn('branch_punishment_facts', out['result'])

    def test_public_projection_strips_fact_block(self):
        out = execute('bazi', dict(self.PILLARS,
                                   include_punishment_facts=True),
                      allow_research=True)
        projected = project_execution(out)
        self.assertNotIn('branch_punishment_facts',
                         json.dumps(projected, ensure_ascii=False))


if __name__ == '__main__':
    unittest.main()
