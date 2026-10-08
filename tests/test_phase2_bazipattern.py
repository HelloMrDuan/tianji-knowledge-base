"""Reviewed candidate facts cannot silently become 定格 or public/AI authority."""
import asyncio
import copy
from pathlib import Path
import unittest
from unittest.mock import AsyncMock

from fastapi.testclient import TestClient
from tianji_kb.api import create_app
from tianji_kb.bazi_adjudication import ADJUDICATION_VARIANT
from tianji_kb.bazi_pattern import PATTERN_VARIANT, candidates
from tianji_kb.engine import execute
from tianji_kb.explanation import ExplanationFailure, ExplanationService
from tianji_kb.golden import run_cases
from tianji_kb.knowledge import read_json
from tianji_kb.operations.bazi_chart import chart
from tianji_kb.product_claims import authorize_structural_claim
from tianji_kb.product_coverage import build_product_coverage
from tianji_kb.resolver import ExecutionTrace
from tianji_kb.scenario_engine import execute_scenario

ROOT = Path(__file__).resolve().parents[1]
RULES = {'bazi.phase2.official_pattern_candidates', 'bazi.phase2.resource_pattern_candidates'}


def resolve(out, pointer):
    value = out
    for token in pointer.removeprefix('#/').split('/'):
        value = value[int(token)] if isinstance(value, list) else value[token]
    return value


class BaziPatternTests(unittest.TestCase):
    def chart(self, *ps, **kwargs):
        return chart(*ps, pattern_variant=PATTERN_VARIANT, **kwargs)

    def test_eight_fixed_goldens_cover_observation_negative_abstention_and_conflict(self):
        policy = next(c['attributes'] for c in read_json(ROOT/'data/canonical/bazi/phase1_knowledge.json')['concepts']
                      if c['id']=='bazi.concept.pattern_candidates_v1')
        original_ids = {cid for ids in policy['golden_case_groups'].values() for cid in ids}
        rows = [r for r in run_cases(ROOT, 'bazi') if r['id'] in original_ids]
        self.assertEqual(len(rows), 8)
        self.assertTrue(all(RULES <= set(r['rule_ids']) for r in rows))
        self.assertEqual({k:len(v) for k,v in policy['golden_case_groups'].items()},
                         {'positive':4,'negative':1,'abstention':2,'conflict':1})

    def test_month_hidden_god_is_not_replaced_by_month_visible_god(self):
        out = self.chart('癸亥','壬子','甲寅','癸酉')
        row = out['result']['pattern_candidates']['resource']['observations'][0]
        self.assertEqual((row['stem'],row['ten_god']),('癸','正印'))
        self.assertEqual([p['pillar'] for p in row['visible_positions']],['year','hour'])
        self.assertEqual(out['result']['stem_ten_gods'][1]['ten_god'],'偏印')
        self.assertIsNone(out['result']['pattern_candidates']['resource']['determination']['pattern'])
        yin = self.chart('庚申','甲申','乙丑','壬午')['result']['pattern_candidates']
        self.assertEqual(yin['official']['observations'][0]['ten_god'],'正官')
        self.assertEqual(yin['resource']['observations'][0]['ten_god'],'正印')

    def test_no_month_match_does_not_import_a_scattered_visible_official(self):
        out = self.chart('辛酉','丙寅','甲子','庚午')
        candidate = out['result']['pattern_candidates']['official']
        self.assertEqual(candidate['status'],'no_month_candidate')
        self.assertEqual(candidate['observations'],[])
        self.assertTrue(any(p['stem']=='辛' and p['pillar']=='year' for p in candidate['context_positions']))
        self.assertEqual(candidate['determination']['status'],'unresolved')

    def test_unexposed_and_miscellaneous_months_never_become_true_false_verdicts(self):
        out = self.chart('戊午','丁酉','甲午','丙午')
        row = out['result']['pattern_candidates']['official']['observations'][0]
        self.assertFalse(row['exposed'])
        self.assertEqual(row['visible_positions'],[])
        self.assertIsNone(row['visibility_fact_ref'])
        mixed = self.chart('辛酉','丁丑','甲子','癸亥')['result']['pattern_candidates']
        self.assertEqual(mixed['official']['observations'][0]['stem'],'辛')
        self.assertEqual(mixed['resource']['observations'][0]['stem'],'癸')
        for family in mixed.values():
            self.assertFalse(family['special_month_conditions_reviewed'])
            self.assertTrue(all(v is None for k,v in family['determination'].items() if k != 'status'))

    def test_dated_conflict_is_preserved_and_strength_waiver_cannot_determine_pattern(self):
        out = self.chart('甲子','丙寅','丙午','乙亥')
        command = out['result']['pattern_candidates']['resource']['dated_commander']
        self.assertEqual(command['conflict_ids'],['bazi.concept.conflict_siling_days'])
        self.assertEqual(command['status'],'unresolved')
        self.assertTrue(command['required_for_ren_pattern_determination'])
        self.assertFalse(command['blocks_structural_observation'])
        combined = self.chart('癸卯','乙卯','甲子','乙亥',strength_variant=ADJUDICATION_VARIANT)
        self.assertEqual(combined['result']['strength_assessment']['classification'],'strong')
        for family in combined['result']['pattern_candidates'].values():
            self.assertIsNone(family['dated_commander']['value'])
            self.assertEqual(family['determination']['status'],'unresolved')
            self.assertIsNone(family['determination']['pattern'])

    def test_every_position_and_rule_match_is_bound_to_actual_trace_and_classical_evidence(self):
        out = self.chart('辛酉','丁丑','甲子','癸亥')
        for family, row in out['result']['pattern_candidates'].items():
            rule_id = 'bazi.phase2.'+family+'_pattern_candidates'
            step = next(s for s in out['trace'] if s['rule_id']==rule_id)
            match = next(m for m in out['rule_matches'] if m['rule_id']==rule_id)
            self.assertEqual(match['facts'],row)
            self.assertEqual(match['evidence_ids'],step['evidence_ids'])
            self.assertTrue(all(e in out['evidence'] for e in match['evidence_ids']))
            self.assertEqual({out['evidence'][e]['evidence_level'] for e in match['evidence_ids']},{'C'})
            self.assertEqual(resolve(out,row['month_fact_ref'])['branch'],'丑')
            self.assertEqual(resolve(out,row['dated_commander']['fact_ref'])['commander_status'],'unresolved')
            for observation in row['observations']:
                hidden = resolve(out,observation['hidden_fact_ref'])
                self.assertEqual((hidden['stem'],hidden['ten_god']),(observation['stem'],observation['ten_god']))
                exposure = resolve(out,observation['visibility_fact_ref'])
                self.assertEqual(exposure['hidden_pillar'],'month')
                self.assertEqual(exposure['hidden_stem'],observation['stem'])
                for position in observation['visible_positions']:
                    self.assertEqual(resolve(out,position['fact_ref'])['stem'],position['stem'])
            for position in row['context_positions']:
                self.assertEqual(resolve(out,position['fact_ref'])['ten_god'],position['ten_god'])

    def test_missing_evidence_and_disagreeing_exposure_are_rejected(self):
        out = self.chart('癸亥','壬子','甲寅','癸酉')
        t = ExecutionTrace('bazi','ziping-structural-v1')
        t.steps = copy.deepcopy(out['trace'])
        t.evidence = {}
        with self.assertRaisesRegex(ValueError,'lack executed evidence'):
            candidates(t,family='resource')
        t.evidence = copy.deepcopy(out['evidence'])
        visible = next(s for s in t.steps if s['rule_id']=='bazi.phase2.ten_gods')
        visible['output'][0]['stem'] = '壬'
        with self.assertRaisesRegex(ValueError,'facts disagree'):
            candidates(t,family='resource')
        with self.assertRaises(ValueError):
            candidates(ExecutionTrace('bazi','ziping-structural-v1'),family='resource')

    def test_short_excerpts_and_source_scope_preserve_conditions_and_original_spelling(self):
        bundle = read_json(ROOT/'data/canonical/bazi/phase1_knowledge.json')
        sources = {s['source_id']:s for s in read_json(ROOT/'config/knowledge_sources.json')['sources']}
        sections = {s['id']:s for s in bundle['sections']}
        for n in range(53,60):
            s = sections[f'bazi.section.s{n:03d}']
            source = sources[s['source_id']]
            text = (ROOT/source['content_path']).read_text(encoding='utf-8')
            self.assertEqual(text.count(s['text']),1)
            self.assertIn(f'[{text.index(s["text"])},{text.index(s["text"])+len(s["text"])})',s['locator'])
            self.assertEqual(source['evidence_level'],'C')
            self.assertEqual(s['review']['status'],'approved')
        self.assertIn('再究司令以定真假',sections['bazi.section.s054']['text'])
        self.assertIn('若月逢禄刃',sections['bazi.section.s054']['text'])
        self.assertIn('如天干不透出辛字',sections['bazi.section.s056']['text'])
        self.assertIn('亦可言官',sections['bazi.section.s056']['text'])
        self.assertIn('印綬',sections['bazi.section.s057']['text'])
        self.assertIn('或入别格',sections['bazi.section.s058']['text'])

    def test_default_gateway_and_public_scenario_cannot_enable_candidates(self):
        inputs = {'value':'2000-01-01T12:00:00+08:00','pattern_variant':PATTERN_VARIANT}
        with self.assertRaisesRegex(ValueError,'explicit research mode'):
            execute('bazi',inputs)
        with self.assertRaises(ValueError):
            execute_scenario('bazi-profile',inputs)
        with self.assertRaisesRegex(ValueError,'Unsupported pattern'):
            execute('bazi',{**inputs,'pattern_variant':'unreviewed'},allow_research=True)
        plain = execute('bazi',{'value':inputs['value']})
        self.assertNotIn('pattern_candidates',plain['result'])
        legacy = chart('癸亥','壬子','甲寅','癸酉',False,False,None,None,None,None,None,'ziping-structural-v1')
        self.assertEqual(legacy['variant'],'ziping-structural-v1')
        self.assertNotIn('pattern_candidates',legacy['result'])
        with self.assertRaisesRegex(ValueError,'claim_unavailable'):
            authorize_structural_claim(ROOT,'bazi-reading',plain,'bazi.pattern_candidates')

    def test_api_requires_research_and_refuses_ai_before_model(self):
        inputs = {'value':'2000-01-01T12:00:00+08:00','pattern_variant':PATTERN_VARIANT}
        provider = type('ForbiddenProvider',(),{'explain':AsyncMock(side_effect=AssertionError('No model'))})()
        with TestClient(create_app(provider=provider)) as client:
            response = client.post('/api/v1/execute',json={'domain':'bazi','input':inputs})
            self.assertEqual(response.status_code,422)
            response = client.post('/api/v1/execute',json={'domain':'bazi','input':inputs,'mode':'research','explain':True})
            self.assertEqual(response.status_code,200,response.text)
            self.assertIn('pattern_candidates',response.json()['chart'])
            self.assertEqual(response.json()['explanation_error'],'interpretation_not_authorized')
        provider.explain.assert_not_called()

    def test_all_prompt_versions_refuse_candidate_explanation_before_retrieval(self):
        out = self.chart('癸亥','壬子','甲寅','癸酉')
        provider = type('ForbiddenProvider',(),{'explain':AsyncMock(side_effect=AssertionError('No model'))})()
        retriever = type('ForbiddenRetriever',(),{'retrieve':lambda *args: (_ for _ in ()).throw(AssertionError('No retrieval'))})()
        for version in ['explanation-prompt-v1','explanation-prompt-v2','explanation-prompt-v3']:
            with self.assertRaises(ExplanationFailure) as caught:
                asyncio.run(ExplanationService(provider,retriever=retriever,prompt_version=version).explain(out))
            self.assertEqual(caught.exception.code,'interpretation_not_authorized')
        provider.explain.assert_not_called()

    def test_product_map_keeps_candidates_research_only_and_full_pattern_not_built(self):
        report = build_product_coverage(ROOT)
        self.assertEqual(report['_audit']['pattern']['status'],'NOT_BUILT')
        policy = report['_audit']['pattern']['variants'][PATTERN_VARIANT]
        self.assertEqual(policy['status'],'RESEARCH_VALIDATED')
        self.assertEqual(policy['golden_categories'],{'positive':4,'negative':1,'abstention':2,'conflict':1})
        self.assertFalse(policy['pattern_determination_available'])
        topic = report['_audit']['topics']['bazi-pattern']
        self.assertEqual(len(topic['reviewed_terms']),2)
        self.assertTrue({'正官格','印格'} <= set(topic['terms_not_structured']))
        self.assertFalse(topic['explanation_ready'])
        for pid,row in report.items():
            if pid.startswith('_'): continue
            self.assertFalse(row['ai_enabled'])
            for capability in row['supported_capabilities']:
                self.assertFalse(RULES.intersection(capability['rule_ids']))
            if 'bazi-pattern' in row['required_topics']:
                research = [c for c in row['research_capabilities'] if c.get('pattern_variant')==PATTERN_VARIANT]
                self.assertEqual(len(research),1)
                self.assertEqual(set(research[0]['rule_ids']),RULES)
                self.assertFalse(research[0]['scenario_public_enabled'])


if __name__ == '__main__':
    unittest.main()
