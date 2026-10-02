import asyncio,copy,json,os,threading,unittest
from pathlib import Path
from unittest.mock import patch
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from fastapi.testclient import TestClient
from phase4_helpers import valid_reply,MechanicalProvider
from tianji_kb.api import create_app,EXAMPLES
from tianji_kb.engine import execute
from tianji_kb.explanation import context_for,validate_reply,ExplanationFailure,ExplanationService
from tianji_kb.explanation_eval import evaluate_suite,score_reply,markdown_report
from tianji_kb.prompts import get_prompt,DEFAULT_PROMPT
from tianji_kb.rag_context import CanonicalRetriever

class PolicyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw={d:execute(d,i) for d,i in EXAMPLES.items()}
        cls.contexts={d:context_for(raw,CanonicalRetriever().retrieve(raw)) for d,raw in cls.raw.items()}
    def test_fixed_suite_v1_v2_regression_test_provider_never_implies_model_quality(self):
        strict=asyncio.run(evaluate_suite(MechanicalProvider(),prompt_version='explanation-prompt-v2',model='mechanical-protocol-fixture'))
        self.assertEqual(len(strict['cases']),102)
        self.assertEqual([c['id']+':'+str(c.get('error')) for c in strict['cases'] if c['status']!='passed'],[])
        baseline=asyncio.run(evaluate_suite(MechanicalProvider(),prompt_version='explanation-prompt-v1',model='mechanical-protocol-fixture'))
        self.assertEqual(strict['suite_sha256'],baseline['suite_sha256'])
        output=Path('build/phase4-protocol-regression');output.mkdir(parents=True,exist_ok=True)
        for report in [strict,baseline]:
            version=report['prompt']['version']
            (output/(version+'.json')).write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
            (output/(version+'.md')).write_text(markdown_report(report))
        for report in [strict,baseline]:
            self.assertFalse(report['real_model_evaluation']);self.assertFalse(report['online_ready'])
            self.assertTrue(all(not r['online_ready'] for r in report['reports'].values()))
        self.assertTrue(all(r['pass_rate']==1 for r in strict['reports'].values()))
        self.assertTrue(all(r['pass_rate']==0 for r in baseline['reports'].values()))
    def test_five_categories_required_facts_all_rules_and_server_bound_citations(self):
        for context in self.contexts.values():
            reply=valid_reply(context);validated=validate_reply(reply,context)
            self.assertEqual(set(validated['sections']),{'deterministic_fact','rule_match','classical_evidence','synthesis','uncertainty'})
            self.assertTrue(validated['semantic_review_required']);self.assertFalse(validated['automatic_release_allowed'])
            self.assertEqual(validated['prompt_version'],DEFAULT_PROMPT)
            for claim in validated['claims']:
                self.assertEqual(claim['citations'][0]['source_ref'],context['evidence'][claim['evidence_ids'][0]])
    def test_unknown_rule_wrong_fact_binding_unrelated_real_evidence_and_missing_quotes_rejected(self):
        context=self.contexts['yijing'];reply=valid_reply(context)
        mutations=[lambda r:r['claims'][0].update(rule_ids=['invented-rule']),
                   lambda r:r['claims'][0].update(rule_ids=['yijing.phase2.nuclear']),
                   lambda r:r['claims'][0].update(quotes=[]),
                   lambda r:r['claims'][0].update(fact_value=False),
                   lambda r:r.update(prompt_sha256='forged'),
                   lambda r:r.update(prompt_version='explanation-prompt-v1')]
        for mutation in mutations:
            bad=copy.deepcopy(reply);mutation(bad)
            with self.assertRaises(ExplanationFailure):validate_reply(bad,context)
        bad=copy.deepcopy(reply);rid='yijing.phase2.nuclear';eid=next(e for e,ref in context['evidence'].items() if ref['rule_id']==rid)
        bad['claims'][0].update(evidence_ids=[eid],quotes=[{'evidence_id':eid,'text':context['evidence'][eid]['original_text'][:20]}])
        scores=score_reply(bad,context)
        self.assertEqual(scores['metrics']['citation_validity'],1)
        self.assertGreater(scores['unsupported_claims'],0)
        with self.assertRaises(ExplanationFailure):validate_reply(bad,context)
    def test_c_d_and_research_cannot_overstate_strength(self):
        for domain in ['yijing','qimen','ziwei']:
            context=self.contexts[domain];reply=valid_reply(context)
            target=next(c for c in reply['claims'] if c['kind']=='classical_evidence')
            target['strength']='computed'
            with self.assertRaises(ExplanationFailure):validate_reply(reply,context)
        raw=execute('fengshui',{'degrees':0,'year':2024,'epoch_year':1864,'research':True},allow_research=True)
        context=context_for(raw,CanonicalRetriever().retrieve(raw));reply=valid_reply(context)
        self.assertTrue(all(c['strength']=='unverified' for c in reply['claims']))
        self.assertEqual(validate_reply(reply,context)['quality_status'],'degraded_requires_review')
        reply['claims'][0]['strength']='conditional'
        with self.assertRaises(ExplanationFailure):validate_reply(reply,context)
    def test_certainty_out_of_scope_and_whitespace_grounding_rejected(self):
        context=self.contexts['yijing']
        for text in ['必然发财，确定结论','独立A级原典已经证实','大限吉凶已经算出']:
            reply=valid_reply(context);reply['claims'][0]['text']=text
            with self.assertRaises(ExplanationFailure):validate_reply(reply,context)
            self.assertGreater(score_reply(reply,context)['unsupported_claims'],0)
        reply=valid_reply(context);reply['claims'][0]['quotes'][0]['text']=' '
        with self.assertRaises(ExplanationFailure):validate_reply(reply,context)
    def test_missing_categories_key_facts_rules_and_limitations_rejected(self):
        context=self.contexts['ziwei'];reply=valid_reply(context)
        filters=[lambda c:c['kind']!='synthesis',lambda c:c['kind']!='rule_match',
                 lambda c:not(c['kind']=='deterministic_fact' and c['fact_ref']=='/chart/bureau')]
        for predicate in filters:
            bad=copy.deepcopy(reply);bad['claims']=[c for c in bad['claims'] if predicate(c)]
            with self.assertRaises(ExplanationFailure):validate_reply(bad,context)
        bad=copy.deepcopy(reply)
        for c in bad['claims']:c['uncertainty_refs']=[]
        with self.assertRaises(ExplanationFailure):validate_reply(bad,context)
    def test_insufficient_evidence_conflict_and_variant_preflight_never_call_model(self):
        class Forbidden:
            async def explain(self,context):raise AssertionError('Provider must not be called')
        for changes,code in [({'evidence':{}},'insufficient_evidence'),({'source_conflicts':[{'status':'unresolved'}]},'source_conflict_unresolved')]:
            raw=copy.deepcopy(self.raw['yijing']);raw.update(changes)
            with patch.object(CanonicalRetriever,'retrieve',side_effect=AssertionError('No retrieval after refusal')):
                with self.assertRaises(ExplanationFailure) as error:asyncio.run(ExplanationService(Forbidden()).explain(raw))
            self.assertEqual(error.exception.code,code)
        raw=copy.deepcopy(self.raw['yijing']);next(iter(raw['evidence'].values()))['variant']='foreign-school'
        with self.assertRaises(ExplanationFailure) as error:asyncio.run(ExplanationService(Forbidden()).explain(raw))
        self.assertEqual(error.exception.code,'variant_policy_mismatch')
    def test_legacy_prompt_only_for_evaluation_or_explicit_research(self):
        with patch.dict(os.environ,{'TIANJI_EXPLANATION_PROMPT_VERSION':'explanation-prompt-v1'}):
            data=TestClient(create_app(MechanicalProvider())).post('/api/v1/execute',json={'domain':'yijing','input':EXAMPLES['yijing'],'explain':True}).json()
            self.assertEqual(data['explanation_error'],'prompt_not_production_eligible');self.assertTrue(data['chart'])
        with patch.dict(os.environ,{'TIANJI_EXPLANATION_PROMPT_VERSION':'unknown'}):
            data=TestClient(create_app(MechanicalProvider())).post('/api/v1/execute',json={'domain':'yijing','input':EXAMPLES['yijing'],'explain':True}).json()
            self.assertEqual(data['explanation_error'],'prompt_configuration_invalid')
    def test_explicit_prose_contradiction_and_named_foreign_variant_rejected(self):
        for domain,text in [('liuyao','世爻为1'),('qimen','当前为阴遁'),('liuren','三传法为八专'),
                            ('ziwei','命宫在子'),('fengshui','坐山为子'),('yijing','本卦编号为2')]:
            context=self.contexts[domain];reply=valid_reply(context);reply['claims'][0]['text']=text
            with self.assertRaises(ExplanationFailure) as error:validate_reply(reply,context)
            self.assertEqual(error.exception.code,'chart_text_contradiction')
            scores=score_reply(reply,context);self.assertGreater(scores['contradiction_count'],0)
            self.assertLess(scores['metrics']['chart_fidelity'],1)
        context=self.contexts['yijing'];reply=valid_reply(context)
        reply['claims'][0]['text']='采用 quanshu-lunar-iztro-mutagen-v1'
        with self.assertRaises(ExplanationFailure) as error:validate_reply(reply,context)
        self.assertEqual(error.exception.code,'variant_policy_mismatch')
        self.assertEqual(score_reply(reply,context)['metrics']['variant_consistency'],0)

    def test_v2_prompt_hash_is_frozen(self):
        self.assertEqual(get_prompt()['sha256'],'e1bd1a809e8f494d9ff5eeba6723b34c3d59cc67fe1e5b779022f6722696a886')
    def test_real_openai_compatible_http_protocol_uses_v2_system_instruction_all_six(self):
        calls=[]
        class Handler(BaseHTTPRequestHandler):
            def log_message(self,*args):pass
            def do_POST(self):
                body=json.loads(self.rfile.read(int(self.headers['Content-Length'])))
                context=json.loads(body['messages'][1]['content']);calls.append((body,context))
                data=json.dumps({'choices':[{'message':{'content':json.dumps(valid_reply(context),ensure_ascii=False)}}]}).encode()
                self.send_response(200);self.send_header('Content-Length',str(len(data)));self.end_headers();self.wfile.write(data)
        server=ThreadingHTTPServer(('127.0.0.1',0),Handler);worker=threading.Thread(target=server.serve_forever,daemon=True);worker.start()
        try:
            with patch.dict(os.environ,{'TIANJI_AI_PROVIDER':'openai-compatible','TIANJI_AI_BASE_URL':f'http://127.0.0.1:{server.server_port}/v1',
                    'TIANJI_AI_MODEL':'local-protocol-fixture','TIANJI_AI_API_KEY':'test-only-credential','TIANJI_EXPLANATION_PROMPT_VERSION':'explanation-prompt-v2'}):
                client=TestClient(create_app())
                for domain in EXAMPLES:
                    data=client.post('/api/v1/execute',json={'domain':domain,'input':EXAMPLES[domain],'explain':True}).json()
                    self.assertEqual(data['explanation_status'],'succeeded',data.get('explanation_error'))
                    self.assertEqual(calls[-1][0]['messages'][0]['content'],get_prompt()['instruction'])
                    self.assertEqual(calls[-1][1]['prompt_version'],'explanation-prompt-v2')
                    self.assertNotIn('test-only-credential',json.dumps(calls[-1]))
                self.assertEqual(len(calls),6)
        finally:server.shutdown();server.server_close();worker.join(timeout=2)
