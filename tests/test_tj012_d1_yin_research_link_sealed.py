"""TJ-012.3 D-1 寅月 research-execution link SEALED tests (E0385).

Offline acceptance ONLY (machine-assembled sealed data tree),
following the test_tj012_ren_yin_true_sealed precedent. This file is
deliberately NOT named in .github/workflows/validate.yml: the research
gate's execute("bazi") step and the real-chart pattern candidates need
the sealed Canonical foundations, which a public checkout does not
contain.

What is verified here and nowhere else:
- the full gate, real birth instant -> provider replay -> live 寅月
  pilot -> research-mode execute("bazi") -> D-1 trace / RuleMatch /
  Evidence, over all fifteen Golden cases: the gate envelope's D-1
  block is byte-equal to the direct chart composition over the same
  pillars and the same live pilot, and its fields equal the
  hand-derived Golden expectations;
- the s2 distinction: the gate carries no precision-warning
  declaration, so the s2 birth enters and determines (true 七杀格,
  same pillars/segment as t2); uncertainty is a caller declaration
  and stays a composition-level abstention (pinned in public CI);
- the silent-drop fix on real charts: legal pilot + legal Variant
  succeeds, legal pilot + missing/wrong Variant fails closed with an
  explicit ValueError, a forged pilot abstains, and a no-pilot call
  leaves the envelope unchanged apart from the D-1 key;
- the protected semantics on gate envelopes: candidates()
  determination stays unresolved, no success/failure/purity/
  useful-god/fortune judgement appears, no 巳月 D-1, no
  tiaohou/bingyao/dayun keys, the normal production API carries no
  D-1, and the public projection strips it;
- the F4 strength gate and this D-1 gate do not contaminate each
  other on a shared 丙×寅 甲段 birth.
"""
import json
import unittest
from pathlib import Path

from tianji_kb.bazi_pattern import PATTERN_VARIANT
from tianji_kb.bazi_siling_pilot import yin_siling_pilot
from tianji_kb.bazi_siling_si_pilot import si_siling_pilot
from tianji_kb.engine import execute
from tianji_kb.operations.bazi_chart import chart
from tianji_kb.public_projection import project_execution
from tianji_kb.scenario_engine import (
    _bazi_profile,
    ren_yin_research_execution,
)

ROOT = Path(__file__).resolve().parents[1]
REN_GOLDEN = json.loads(
    (ROOT / 'tests/golden_tj012_ren_yin_true.json').read_text('utf-8'))
LINK_GOLDEN = json.loads(
    (ROOT / 'tests/golden_tj012_d1_yin_research_link.json').read_text('utf-8'))
SI_GOLDEN = json.loads(
    (ROOT / 'tests/golden_tj012_siling_si_pilot.json').read_text('utf-8'))
CANDIDATES_DETERMINATION = {
    'status': 'unresolved', 'pattern': None, 'true_false': None,
    'success_failure': None, 'useful_god': None}
ZONE = 'Asia/Shanghai'


def _jie_facts(case):
    window = REN_GOLDEN['jie_windows'][case['window']]
    facts = {'provider': dict(REN_GOLDEN['provider']),
             'lichun': dict(window['lichun']),
             'next_jie': dict(window['next_jie'])}
    override = case.get('jie_override') or {}
    if override.get('precision_warning'):
        facts['precision_warning'] = True
    return facts


def _live_pilot(case):
    return yin_siling_pilot(
        case['source_birth']['value'], version_id='ditiansui-yuanshuo',
        jie_facts=_jie_facts(case))


class RealChartGateTests(unittest.TestCase):
    def test_all_golden_cases_through_the_gate(self):
        for case in REN_GOLDEN['cases']:
            with self.subTest(case=case['id']):
                birth = case['source_birth']
                record = ren_yin_research_execution(
                    birth['value'], birth['zone'])
                if case['id'] == 's1-non-yin':
                    self.assertFalse(record['entered'])
                    self.assertEqual(record['reason'], 'month_not_yin')
                    self.assertIsNone(record['determination'])
                    continue
                self.assertTrue(record['entered'], record)
                envelope = record['envelope']
                block = record['determination']
                self.assertEqual(
                    [envelope['result']['pillars'][i]['stem']['value']
                     + envelope['result']['pillars'][i]['branch']['value']
                     for i in range(4)],
                    case['pillars'])
                # The gate envelope's D-1 block equals the direct
                # chart composition over the same pillars and the
                # same live pilot, byte for byte. The pilot compared
                # here must be the one the gate itself used
                # (record['pilot']): _live_pilot(case) re-applies
                # the case's caller-side jie_override, which the
                # gate never sees — for s2-pilot-uncertain that
                # override makes the pilot uncertain (abstained)
                # while the gate's own pilot is computed
                # (determined), so comparing against it would
                # equate two different pilot inputs.
                pilot = record['pilot']
                direct = chart(
                    *case['pillars'], pattern_variant=PATTERN_VARIANT,
                    ren_yin_pilot_result=pilot)
                self.assertEqual(
                    block, direct['result']['pattern_determination_ren_yin'])
                # The D-1 trace step and RuleMatch carry the same block.
                step = next(
                    row for row in envelope['trace']
                    if row['rule_id'] == 'bazi.phase2.ren_yin_true_pattern')
                self.assertEqual(step['output'], block)
                match = next(
                    row for row in envelope['rule_matches']
                    if row['rule_id'] == 'bazi.phase2.ren_yin_true_pattern')
                self.assertTrue(match['evidence_ids'])
                for eid in match['evidence_ids']:
                    self.assertIn(eid, envelope['evidence'])
                # Fields equal the hand-derived Golden expectations.
                # s2 is the two-layer case: its own expected is the
                # caller-declared-uncertainty outcome (abstained),
                # but the gate carries no precision-warning
                # declaration, so the gate-layer expectation is t2's
                # (same pillars/segment) - see the link Golden's
                # expected_gate and
                # test_s2_birth_enters_without_caller_warning.
                if case['id'] == 's2-pilot-uncertain':
                    want = next(
                        c['expected'] for c in REN_GOLDEN['cases']
                        if c['id'] == 't2-bing-qisha')
                else:
                    want = case['expected']
                self.assertEqual(block['status'], want['status'])
                self.assertEqual(block['decision_step'],
                                 want['decision_step'])
                self.assertEqual(block['abstention_reason'],
                                 want['abstention_reason'])
                det = block['determination']
                self.assertEqual(det['true_false'], want['true_false'])
                self.assertEqual(det['pattern'], want['pattern'])
                self.assertIsNone(det['success_failure'])
                self.assertIsNone(det['purity'])
                self.assertIsNone(det['useful_god'])
                if want['commander_visible_pillars'] is None:
                    self.assertIsNone(block['commander'])
                else:
                    self.assertEqual(
                        block['commander']['visible_pillars'],
                        want['commander_visible_pillars'])

    def test_s2_birth_enters_without_caller_warning(self):
        # The gate derives Jie facts itself and carries no
        # precision-warning declaration, so the s2 birth (same
        # pillars/segment as t2) enters and determines; the
        # uncertainty in the Golden s2 case is a caller declaration,
        # not a gate inference.
        case = next(c for c in REN_GOLDEN['cases']
                    if c['id'] == 's2-pilot-uncertain')
        record = ren_yin_research_execution(
            case['source_birth']['value'], case['source_birth']['zone'])
        self.assertTrue(record['entered'])
        self.assertEqual(
            record['determination']['determination']['true_false'], 'true')
        self.assertEqual(
            record['determination']['determination']['pattern'], '七杀格')


class SilentDropFixRealChartTests(unittest.TestCase):
    def test_legal_pilot_plus_legal_variant_succeeds(self):
        case = next(c for c in REN_GOLDEN['cases']
                    if c['id'] == 't1-wu-zhengcai')
        out = chart(*case['pillars'], pattern_variant=PATTERN_VARIANT,
                    ren_yin_pilot_result=_live_pilot(case))
        block = out['result']['pattern_determination_ren_yin']
        self.assertEqual(block['determination']['true_false'], 'true')
        self.assertEqual(block['determination']['pattern'], '正财格')

    def test_legal_pilot_without_variant_fails_closed(self):
        case = next(c for c in REN_GOLDEN['cases']
                    if c['id'] == 't1-wu-zhengcai')
        with self.assertRaises(ValueError) as caught:
            chart(*case['pillars'],
                  ren_yin_pilot_result=_live_pilot(case))
        self.assertEqual(
            str(caught.exception),
            'ren_yin_pilot_result requires the registered pattern variant')

    def test_legal_pilot_with_wrong_variant_fails_closed(self):
        case = next(c for c in REN_GOLDEN['cases']
                    if c['id'] == 't1-wu-zhengcai')
        with self.assertRaises(ValueError) as caught:
            chart(*case['pillars'], pattern_variant='bogus-variant',
                  ren_yin_pilot_result=_live_pilot(case))
        self.assertEqual(
            str(caught.exception),
            'ren_yin_pilot_result requires the registered pattern variant')

    def test_forged_pilot_abstains_on_real_chart(self):
        case = next(c for c in REN_GOLDEN['cases']
                    if c['id'] == 't1-wu-zhengcai')
        forged = dict(_live_pilot(case))
        forged['variant'] = 'forged'
        out = chart(*case['pillars'], pattern_variant=PATTERN_VARIANT,
                    ren_yin_pilot_result=forged)
        block = out['result']['pattern_determination_ren_yin']
        self.assertEqual(block['abstention_reason'],
                         'pilot_result_unverifiable')
        self.assertEqual(block['determination']['true_false'], 'abstained')

    def test_no_pilot_call_is_unchanged(self):
        case = next(c for c in REN_GOLDEN['cases']
                    if c['id'] == 't1-wu-zhengcai')
        baseline = chart(*case['pillars'],
                         pattern_variant=PATTERN_VARIANT)
        self.assertNotIn('pattern_determination_ren_yin',
                         baseline['result'])
        with_pilot = chart(
            *case['pillars'], pattern_variant=PATTERN_VARIANT,
            ren_yin_pilot_result=_live_pilot(case))
        self.assertEqual(
            set(with_pilot['result']) - set(baseline['result']),
            {'pattern_determination_ren_yin'})
        self.assertTrue(
            with_pilot['result']['production_scope'].startswith(
                baseline['result']['production_scope']))


class ProtectedSemanticsTests(unittest.TestCase):
    def test_candidates_determination_stays_unresolved(self):
        case = next(c for c in REN_GOLDEN['cases']
                    if c['id'] == 't1-wu-zhengcai')
        record = ren_yin_research_execution(
            case['source_birth']['value'], case['source_birth']['zone'])
        candidates = record['envelope']['result']['pattern_candidates']
        for family in ('official', 'resource'):
            self.assertEqual(candidates[family]['determination'],
                             CANDIDATES_DETERMINATION)

    def test_no_new_judgements_on_gate_envelope(self):
        for case in REN_GOLDEN['cases']:
            with self.subTest(case=case['id']):
                record = ren_yin_research_execution(
                    case['source_birth']['value'],
                    case['source_birth']['zone'])
                if not record['entered']:
                    continue
                block = record['determination']
                det = block['determination']
                self.assertIn(det['true_false'],
                              ('true', 'commander_not_visible', 'abstained'))
                self.assertIsNone(det['success_failure'])
                self.assertIsNone(det['purity'])
                self.assertIsNone(det['useful_god'])
                for field in ('success_failure', 'purity', 'useful_god'):
                    self.assertIn('unreviewed',
                                  block['unreviewed'][field])
                result = record['envelope']['result']
                self.assertNotIn('tiaohou_assessment', result)
                self.assertNotIn('bingyao_assessment', result)
                self.assertNotIn('dayun_sequence_research', result)

    def test_no_si_month_d1(self):
        case = next(c for c in LINK_GOLDEN['cases']
                    if c['id'] == 'link-si')
        window = SI_GOLDEN['jie_windows']['2025']
        facts = {'provider': dict(SI_GOLDEN['provider']),
                 'lixia': dict(window['lixia']),
                 'next_jie': dict(window['next_jie'])}
        si_pilot = si_siling_pilot(
            case['source_birth']['value'], version_id='sanming-t1',
            jie_facts=facts)
        self.assertEqual(si_pilot['status'], 'computed')
        out = chart(*case['pillars'], pattern_variant=PATTERN_VARIANT,
                    ren_yin_pilot_result=si_pilot)
        block = out['result']['pattern_determination_ren_yin']
        self.assertEqual(block['abstention_reason'], 'month_not_yin')
        self.assertEqual(block['determination']['true_false'], 'abstained')

    def test_production_api_carries_no_d1_and_projection_strips_it(self):
        case = next(c for c in REN_GOLDEN['cases']
                    if c['id'] == 't1-wu-zhengcai')
        plain = execute('bazi', {'value': case['source_birth']['value'],
                                 'zone': ZONE})
        self.assertNotIn('pattern_determination_ren_yin',
                         plain['result'])
        record = ren_yin_research_execution(
            case['source_birth']['value'], case['source_birth']['zone'])
        projected = project_execution(record['envelope'])
        self.assertNotIn('pattern_determination_ren_yin',
                         projected['result'])

    def test_f4_and_d1_gates_do_not_contaminate_each_other(self):
        # Shared 丙×寅 birth in the 甲段 (t3): F4 can trigger in the
        # production profile, D-1 determines true 偏印格 through the
        # research gate; neither gate's output appears in the other's
        # envelope, and both agree on the pillars.
        case = next(c for c in REN_GOLDEN['cases']
                    if c['id'] == 't3-jia-pianyin')
        profile = _bazi_profile({'value': case['source_birth']['value'],
                                 'zone': ZONE})
        self.assertIn('strength_presentation',
                      profile['result'])
        self.assertNotIn('pattern_determination_ren_yin',
                         profile['result'])
        record = ren_yin_research_execution(
            case['source_birth']['value'], case['source_birth']['zone'])
        self.assertTrue(record['entered'])
        self.assertEqual(
            record['determination']['determination']['true_false'], 'true')
        self.assertEqual(
            record['determination']['determination']['pattern'], '偏印格')
        self.assertNotIn('strength_presentation',
                         record['envelope']['result'])
        self.assertEqual(profile['result']['pillars'],
                         record['envelope']['result']['pillars'])


if __name__ == '__main__':
    unittest.main()
