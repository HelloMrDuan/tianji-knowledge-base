import asyncio
import copy
from pathlib import Path
import unittest
from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient
from tianji_kb.api import create_app
from tianji_kb.bazi_adjudication import ADJUDICATION_VARIANT, strength_assessment
from tianji_kb.bazi_root_conditions import STRENGTH_VARIANT
from tianji_kb.engine import execute
from tianji_kb.explanation import ExplanationFailure, ExplanationService
from tianji_kb.golden import run_cases
from tianji_kb.operations.bazi_chart import chart
from tianji_kb.product_coverage import build_product_coverage
from tianji_kb.resolver import ExecutionTrace
from tianji_kb.scenario_engine import execute_scenario

ROOT=Path(__file__).resolve().parents[1]

def resolve(out, pointer):
    value=out
    for token in pointer.removeprefix('#/').split('/'):
        value=value[int(token)] if isinstance(value,list) else value[token]
    return value


class PositiveStrengthTests(unittest.TestCase):
    def chart(self,*ps): return chart(*ps,strength_variant=ADJUDICATION_VARIANT)

    def test_nine_fixed_goldens_cover_four_categories_in_the_same_strength_variant(self):
        rows=[r for r in run_cases(ROOT,'bazi') if r['id'].startswith('bazi.adjudication-')]
        self.assertEqual(len(rows),9)
        self.assertEqual(sum('bazi.phase2.strength_pure_support' in r['rule_ids'] for r in rows),2)
        self.assertEqual(sum('bazi.phase2.strength_isolated_control' in r['rule_ids'] for r in rows),2)
        self.assertTrue(all('bazi.phase2.strength_bounded_adjudication' in r['rule_ids'] for r in rows))

    def test_real_calendar_strong_dates_have_distinct_pillars_and_actual_rule_matches(self):
        rows=[]
        for value in ['1963-03-22T22:00:00+08:00','2043-03-22T22:00:00+08:00']:
            out=execute('bazi',{'value':value,'strength_variant':ADJUDICATION_VARIANT},allow_research=True)
            a=out['result']['strength_assessment']
            self.assertEqual(a['classification'],'strong')
            self.assertTrue(a['why_not_indeterminate']['all_required_conditions_verified'])
            self.assertIn('bazi.phase2.strength_pure_support',a['matched_rule_ids'])
            self.assertNotIn('bazi.phase2.strength_isolated_control',a['matched_rule_ids'])
            self.assertFalse(out['interpretation_contract']['ai_may_explain'])
            self.assertEqual(out['mode'],'research')
            rows.append(tuple(p['stem']['value']+p['branch']['value'] for p in out['result']['pillars']))
        self.assertNotEqual(rows[0],rows[1])

    def test_real_calendar_yang_and_yin_weak_dates_require_the_complete_isolation_chain(self):
        for value,day in [('2038-09-14T12:00:00+08:00','甲'),('1978-09-20T10:00:00+08:00','乙')]:
            out=execute('bazi',{'value':value,'strength_variant':ADJUDICATION_VARIANT},allow_research=True)
            a=out['result']['strength_assessment']
            self.assertEqual(out['result']['day_master']['stem'],day)
            self.assertEqual(a['classification'],'weak')
            self.assertIn('bazi.phase2.strength_isolated_control',a['matched_rule_ids'])
            self.assertNotIn('bazi.phase2.strength_pure_support',a['matched_rule_ids'])
            self.assertFalse(out['result']['root_availability']['root_presence'])

    def test_positive_provenance_and_why_conditions_resolve_to_real_facts_and_evidence(self):
        for ps in [('癸卯','乙卯','甲子','乙亥'),('戊午','辛酉','甲午','庚午')]:
            out=self.chart(*ps);a=out['result']['strength_assessment']
            self.assertFalse(a['blockers'])
            for pointer in a['fact_refs']: self.assertIsNotNone(resolve(out,pointer))
            self.assertTrue(set(a['matched_rule_ids']) <= {s['rule_id'] for s in out['trace']})
            self.assertTrue(set(a['evidence_ids']) <= set(out['evidence']))
            self.assertEqual(set(a['source_ids']),{out['evidence'][e]['source_id'] for e in a['evidence_ids']})
            for c in a['why_not_indeterminate']['conditions']:
                self.assertIs(resolve(out,c['fact_ref']),True)
                self.assertTrue(set(c['evidence_ids']) <= set(out['evidence']))
            self.assertEqual(out['result']['strength_factor_graph']['overall_strength'],a['classification'])
            self.assertFalse(a['weights_available'])
            self.assertFalse(a['source_case_lookup_used'])

    def test_source_conflicts_block_only_their_applicable_variant_dependencies(self):
        out=self.chart('甲子','丙寅','甲辰','戊辰');a=out['result']['strength_assessment']
        self.assertEqual(a['classification'],'indeterminate')
        self.assertIn('bazi.concept.conflict_root_type_readings',a['conflict_ids'])
        dated=next(c for c in a['conflict_checks'] if c['conflict_id']=='bazi.concept.conflict_siling_days')
        self.assertFalse(dated['blocking'])
        self.assertNotIn('dated_commander_unresolved',{b['reason'] for b in a['blockers']})
        self.assertTrue(a['unresolved_evidence'])
        for b in a['blockers']:
            self.assertIsNotNone(resolve(out,b['fact_ref']))
            self.assertIn(b['evidence_id'],out['evidence'])
        positive=self.chart('癸卯','乙卯','甲子','乙亥')
        self.assertEqual(positive['result']['month_command_variant']['commander_status'],'unresolved')
        self.assertTrue(any(r['effect_status']=='unresolved' for r in positive['result']['action_effects']['hidden_relations']))
        self.assertEqual(positive['result']['strength_assessment']['classification'],'strong')

    def test_no_root_with_resource_and_classical_case_labels_do_not_supply_verdicts(self):
        for ps in [('戊午','辛酉','甲午','癸酉'),('戊寅','甲寅','甲辰','丁卯'),('庚申','乙酉','丙申','丙申')]:
            a=self.chart(*ps)['result']['strength_assessment']
            self.assertEqual(a['classification'],'indeterminate')
            self.assertIsNone(a['why_not_indeterminate'])
            self.assertFalse(a['source_case_lookup_used'])

    def test_missing_evidence_or_false_context_conditions_cannot_be_promoted(self):
        out=self.chart('癸卯','乙卯','甲子','乙亥')
        t=ExecutionTrace('bazi','ziping-structural-v1')
        t.steps=copy.deepcopy([s for s in out['trace'] if 'strength_' not in s['rule_id']])
        t.evidence=copy.deepcopy(out['evidence'])
        effect=next(s for s in t.steps if s['rule_id']=='bazi.phase2.action_effects')
        effect['output']['pure_support_scope_conditions']['effective_day_roots']=False
        a=strength_assessment(t,strength_variant=ADJUDICATION_VARIANT)
        self.assertEqual(a['classification'],'indeterminate')
        t.evidence={}
        with self.assertRaises(ValueError):strength_assessment(t,strength_variant=ADJUDICATION_VARIANT)
        with self.assertRaises(ValueError):strength_assessment(ExecutionTrace('bazi','ziping-structural-v1'),strength_variant=ADJUDICATION_VARIANT)

    def test_cross_rule_factor_identity_is_required_even_with_valid_evidence_ids(self):
        # Use a genuinely executed positive chart, not mocked upstream facts.
        original=self.chart('癸卯','乙卯','甲子','乙亥')
        self.assertEqual(original['result']['strength_assessment']['classification'],'strong')
        changes=(
            ('principal_month', lambda v: v.__setitem__('day_master','乙')),
            ('principal_month', lambda v: v.__setitem__('month_branch','酉')),
            ('root_availability', lambda v: v.__setitem__('root_presence',False)),
            ('root_availability', lambda v: v['roots'][0].__setitem__('root_index',9)),
            ('action_effects', lambda v: v['visible_relations'][0]['fact'].__setitem__('stem','辛')),
            ('action_effects', lambda v: v['hidden_relations'].pop()),
        )
        for rule, change in changes:
            with self.subTest(rule=rule, change=change.__code__.co_firstlineno):
                trace=ExecutionTrace('bazi','ziping-structural-v1')
                trace.steps=copy.deepcopy([s for s in original['trace']
                                           if 'strength_' not in s['rule_id']])
                trace.evidence=copy.deepcopy(original['evidence'])
                step=next(s for s in trace.steps if s['rule_id']=='bazi.phase2.'+rule)
                change(step['output'])
                result=strength_assessment(trace,strength_variant=ADJUDICATION_VARIANT)
                self.assertEqual(result['classification'],'indeterminate')
                self.assertIsNone(result['why_not_indeterminate'])
                offenders=[b for b in result['blockers']
                           if b['reason']=='factor_chain_inconsistent']
                self.assertTrue(offenders)
                for b in offenders:
                    self.assertIn(b['evidence_id'],trace.evidence)

    def test_cross_rule_factor_chain_preserves_both_existing_positive_classes(self):
        for pillars,classification in (
            (('癸卯','乙卯','甲子','乙亥'),'strong'),
            (('戊午','辛酉','甲午','庚午'),'weak'),
        ):
            with self.subTest(pillars=pillars):
                out=self.chart(*pillars)
                assessment=out['result']['strength_assessment']
                self.assertEqual(assessment['classification'],classification)
                self.assertNotIn('factor_chain_inconsistent',
                                 {b['reason'] for b in assessment['blockers']})
                self.assertFalse(assessment['public_enabled'])
                self.assertFalse(assessment['ai_enabled'])

    def test_research_api_is_available_but_production_and_public_scenario_do_not_auto_open(self):
        inputs={'value':'1963-03-22T22:00:00+08:00','strength_variant':ADJUDICATION_VARIANT}
        with self.assertRaises(ValueError):execute('bazi',inputs)
        with self.assertRaises(ValueError):execute_scenario('bazi-profile',inputs)
        provider=type('ForbiddenProvider',(),{'explain':AsyncMock(side_effect=AssertionError('No model'))})()
        with TestClient(create_app(provider=provider)) as client:
            production=client.post('/api/v1/execute',json={'domain':'bazi','input':inputs,'mode':'production'})
            self.assertEqual(production.status_code,422)
            research=client.post('/api/v1/execute',json={'domain':'bazi','input':inputs,'mode':'research'})
            self.assertEqual(research.status_code,200,research.text)
            self.assertEqual(research.json()['chart']['strength_assessment']['classification'],'strong')
            denied=client.post('/api/v1/execute',json={'domain':'bazi','input':inputs,'mode':'research','explain':True})
            self.assertEqual(denied.status_code,200,denied.text)
            self.assertEqual(denied.json()['explanation_error'],'interpretation_not_authorized')
            self.assertEqual(denied.json()['chart']['strength_assessment']['classification'],'strong')
            provider.explain.assert_not_called()

    def test_every_explanation_prompt_refuses_before_retrieval_or_model(self):
        out=execute('bazi',{'value':'1963-03-22T22:00:00+08:00','strength_variant':ADJUDICATION_VARIANT},allow_research=True)
        provider=type('ForbiddenProvider',(),{'explain':AsyncMock(side_effect=AssertionError('No model'))})()
        retriever=type('ForbiddenRetriever',(),{'retrieve':lambda *args: (_ for _ in ()).throw(AssertionError('No retrieval'))})()
        for version in ['explanation-prompt-v1','explanation-prompt-v2','explanation-prompt-v3']:
            service=ExplanationService(provider,retriever=retriever,prompt_version=version)
            with self.assertRaises(ExplanationFailure) as caught:asyncio.run(service.explain(out))
            self.assertEqual(caught.exception.code,'interpretation_not_authorized')
        provider.explain.assert_not_called()

    def test_variant_coverage_keeps_research_rules_out_of_public_supported_capabilities(self):
        report=build_product_coverage(ROOT);a=report['_audit']['strength']
        self.assertEqual(a['status'],'PARTIAL')
        v=a['variants'][ADJUDICATION_VARIANT]
        self.assertEqual(v['status'],'RESEARCH_VALIDATED')
        self.assertEqual(v['golden_categories'],{'strong-positive':2,'weak-positive':2,'abstention':3,'conflict':2})
        self.assertFalse(v['public_enabled'])
        self.assertFalse(v['ai_enabled'])
        self.assertEqual(a['variants']['bazi-strength-month-command-v1']['status'],'BLOCKED')
        research=set(v['positive_rule_ids']+[v['gate_rule_id']])
        for row in report.values():
            if 'supported_capabilities' in row:
                self.assertFalse(any(research & set(c['rule_ids']) for c in row['supported_capabilities']))
        from tianji_kb.product_coverage import read_json
        def missing_abstention(path):
            obj=read_json(path)
            if path.name=='phase2_golden.json' and path.parent.name=='bazi':
                obj['cases']=[c for c in obj['cases'] if c['id']!='bazi.adjudication-abstain-nonwood']
            return obj
        with patch('tianji_kb.product_coverage.read_json',side_effect=missing_abstention), self.assertRaisesRegex(ValueError,'Missing or incompatible Golden Case'):
            build_product_coverage(ROOT)
        def mismatched_strength_variant(path):
            obj=read_json(path)
            if path.name=='phase2_golden.json' and path.parent.name=='bazi':
                case=next(c for c in obj['cases'] if c['id']=='bazi.adjudication-abstain-nonwood')
                case['expected']['strength_assessment']['variant']='other-unreviewed-strength'
            return obj
        with patch('tianji_kb.product_coverage.read_json',side_effect=mismatched_strength_variant):
            blocked=build_product_coverage(ROOT)['_audit']['strength']['variants'][ADJUDICATION_VARIANT]
        self.assertEqual(blocked['status'],'BLOCKED')
        self.assertEqual(blocked['golden_categories']['abstention'],3)

    def test_legacy_and_default_behaviors_remain_opt_in_abstention_without_model_or_raw_reads(self):
        self.assertNotIn('strength_assessment',chart('癸卯','乙卯','甲子','乙亥')['result'])
        self.assertEqual(chart('癸卯','乙卯','甲子','乙亥',strength_variant=STRENGTH_VARIANT)['result']['strength_assessment']['classification'],'indeterminate')
        original=Path.read_bytes
        def guard(path,*args,**kwargs):
            if '/data/quarantine/' in path.as_posix() or '/data/raw/' in path.as_posix():raise AssertionError('No source body at runtime')
            return original(path,*args,**kwargs)
        with patch.object(Path,'read_bytes',guard),patch('socket.create_connection',side_effect=AssertionError('No network/model')):
            self.assertEqual(self.chart('癸卯','乙卯','甲子','乙亥')['result']['strength_assessment']['classification'],'strong')


if __name__=='__main__':unittest.main()
