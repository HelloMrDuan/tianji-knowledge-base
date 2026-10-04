import unittest
from unittest.mock import patch
from fastapi.testclient import TestClient
from tianji_kb.api import create_app,EXAMPLES
from tianji_kb.engine import PROVIDERS
from tianji_kb.resolver import EvidenceResolver
from tianji_kb.prompts import PROMPTS,DEFAULT_PROMPT,get_prompt

class UnifiedApiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client=TestClient(create_app());cls.contracts=EvidenceResolver().contracts
    def request(self,domain,**kwargs):return {'domain':domain,'input':EXAMPLES[domain],**kwargs}
    def test_all_six_normal_and_deterministic_with_model_disabled(self):
        with patch('socket.socket.connect',side_effect=AssertionError('Network model call forbidden')):
            for domain in PROVIDERS:
                first=self.client.post('/api/v1/execute',json=self.request(domain,explain=False))
                self.assertEqual(first.status_code,200,first.text)
                data=first.json();self.assertEqual(data,self.client.post('/api/v1/execute',json=self.request(domain)).json())
                self.assertEqual(data['variant'],self.contracts[domain]['variant'])
                self.assertEqual(data['explanation_status'],'disabled')
                self.assertIsNone(data['explanation'])
                for key in ['chart','rule_matches','trace','evidence','warnings','limitations']:self.assertIn(key,data)
                for step in data['trace']:self.assertEqual(step['variant'],data['variant'])
                for ref in data['evidence'].values():self.assertEqual(ref['variant'],data['variant'])
    def test_all_six_invalid_inputs_and_unsupported_variants(self):
        for domain in PROVIDERS:
            for payload in [self.request(domain,variant='unregistered'),{'domain':domain,'input':{'unknown_argument':'x'}}]:
                self.assertEqual(self.client.post('/api/v1/execute',json=payload).status_code,422)
        for payload in [{'domain':'taiyi','input':{}},{'domain':'yijing','input':'invalid'},{'domain':'yijing','input':EXAMPLES['yijing'],'explain':'false'}]:
            self.assertEqual(self.client.post('/api/v1/execute',json=payload).status_code,422)
    def test_explanation_unavailable_does_not_change_chart(self):
        for domain in PROVIDERS:
            plain=self.client.post('/api/v1/execute',json=self.request(domain)).json()
            explained=self.client.post('/api/v1/execute',json=self.request(domain,explain=True))
            self.assertEqual(explained.status_code,200)
            data=explained.json();self.assertEqual(data['explanation_status'],'failed')
            for key in ['chart','trace','evidence','rule_matches']:self.assertEqual(data[key],plain[key])
    def test_production_research_isolation_and_warnings(self):
        body={'domain':'fengshui','input':{'degrees':0,'year':2024,'epoch_year':1864}}
        self.assertEqual(self.client.post('/api/v1/execute',json=body).status_code,422)
        research=self.client.post('/api/v1/execute',json={**body,'mode':'research'})
        self.assertEqual(research.status_code,200);self.assertTrue(research.json()['warnings'])
        self.assertFalse(research.json()['chart']['period']['production_eligible'])
        self.assertEqual(research.json()['chart']['period']['epoch_evidence_level'],'D')
        self.assertEqual(self.client.post('/api/v1/execute',json={'domain':'fengshui','input':{'degrees':0,'research':True}}).status_code,422)
    def test_admin_conflicts_are_server_token_gated_and_canonical(self):
        disabled=TestClient(create_app(admin_read_token=""))
        unavailable=disabled.get('/api/v1/admin/governance/conflicts')
        self.assertEqual(unavailable.status_code,503)
        self.assertEqual(unavailable.json()['detail']['code'],'admin_auth_not_configured')

        client=TestClient(create_app(admin_read_token='review-token'))
        self.assertEqual(client.get('/api/v1/admin/governance/conflicts').status_code,401)
        self.assertEqual(
            client.get(
                '/api/v1/admin/governance/conflicts',
                headers={'Authorization':'Bearer wrong-token'},
            ).status_code,
            401,
        )
        response=client.get(
            '/api/v1/admin/governance/conflicts',
            headers={'Authorization':'Bearer review-token'},
        )
        self.assertEqual(response.status_code,200,response.text)
        data=response.json()
        self.assertTrue(data['read_only'])
        self.assertFalse(data['public_release'])
        records={row['id']:row for row in data['records']}
        self.assertIn('bazi.concept.conflict_spouse_star_lens',records)
        self.assertIn('bazi.concept.conflict_three_punishments',records)
        self.assertEqual(records['bazi.concept.conflict_spouse_star_lens']['status'],'bounded')
        self.assertEqual(records['bazi.concept.conflict_three_punishments']['status'],'unresolved')
        self.assertEqual(
            records['bazi.concept.conflict_three_punishments']['executable_policy'],
            'blocked_pending_school_resolution',
        )
        self.assertTrue(all(row['evidence'] for row in records.values()))
        self.assertTrue(all(
            evidence['evidence_level']=='C'
            for row in records.values()
            for evidence in row['evidence']
        ))

    def test_admin_classics_are_token_gated_metadata_only(self):
        client=TestClient(create_app(admin_read_token='review-token'))
        path='/api/v1/admin/governance/classics'
        self.assertEqual(client.get(path).status_code,401)
        response=client.get(path,headers={'Authorization':'Bearer review-token'})
        self.assertEqual(response.status_code,200,response.text)
        data=response.json()
        self.assertTrue(data['read_only'])
        self.assertFalse(data['public_release'])
        records=data['records']
        self.assertTrue(records)
        self.assertTrue(any(row['id']=='bazi.classic.yuanhai' for row in records))
        self.assertTrue(any(row['chapter_count'] > 0 for row in records))
        self.assertTrue(any(row['reviewed_section_count'] > 0 for row in records))
        self.assertTrue(all(row['evidence_level'] in ('A','B','C','D') for row in records))
        self.assertTrue(all(row['body_stage'] in ('canonical','quarantine') for row in records))
        serialized=str(records)
        self.assertNotIn('original_text',serialized)
        self.assertNotIn('data/quarantine/',serialized)
        self.assertNotIn('content_path',serialized)
        self.assertNotIn('TIANJI_ADMIN_READ_TOKEN',serialized)

    def test_admin_chapters_are_token_gated_metadata_only(self):
        client=TestClient(create_app(admin_read_token='review-token'))
        path='/api/v1/admin/governance/chapters'
        self.assertEqual(client.get(path).status_code,401)
        response=client.get(path,headers={'Authorization':'Bearer review-token'})
        self.assertEqual(response.status_code,200,response.text)
        data=response.json()
        self.assertTrue(data['read_only'])
        self.assertFalse(data['public_release'])
        records=data['records']
        self.assertTrue(records)
        self.assertTrue(any(row['reviewed_section_count'] > 0 for row in records))
        self.assertTrue(all(row['evidence_level'] in ('A','B','C','D') for row in records))
        self.assertTrue(all(row['classic_id'] and row['classic_title'] for row in records))
        serialized=str(records)
        self.assertNotIn('original_text',serialized)
        self.assertNotIn('data/quarantine/',serialized)
        self.assertNotIn('content_path',serialized)
        self.assertNotIn('TIANJI_ADMIN_READ_TOKEN',serialized)

    def test_admin_terms_are_token_gated_without_source_bodies(self):
        client=TestClient(create_app(admin_read_token='review-token'))
        path='/api/v1/admin/governance/terms'
        self.assertEqual(client.get(path).status_code,401)
        response=client.get(path,headers={'Authorization':'Bearer review-token'})
        self.assertEqual(response.status_code,200,response.text)
        data=response.json()
        self.assertTrue(data['read_only'])
        self.assertFalse(data['public_release'])
        records=data['records']
        self.assertTrue(records)
        self.assertTrue(any(row['aliases'] for row in records))
        self.assertTrue(any(row['evidence'] for row in records))
        self.assertTrue(all('definition' in row for row in records))
        serialized=str(records)
        self.assertNotIn('original_text',serialized)
        self.assertNotIn('data/quarantine/',serialized)
        self.assertNotIn('content_path',serialized)
        self.assertNotIn('TIANJI_ADMIN_READ_TOKEN',serialized)

    def test_admin_sources_are_token_gated_provenance_only(self):
        client=TestClient(create_app(admin_read_token='review-token'))
        path='/api/v1/admin/governance/sources'
        self.assertEqual(client.get(path).status_code,401)
        response=client.get(path,headers={'Authorization':'Bearer review-token'})
        self.assertEqual(response.status_code,200,response.text)
        data=response.json()
        self.assertTrue(data['read_only'])
        self.assertFalse(data['public_release'])
        records=data['records']
        self.assertTrue(records)
        self.assertTrue(any(row['repository'] for row in records))
        self.assertTrue(any(row['section_count'] > 0 for row in records))
        self.assertTrue(all(row['evidence_level'] in ('A','B','C','D') for row in records))
        serialized=str(records)
        self.assertNotIn('content_path',serialized)
        self.assertNotIn('sha256',serialized)
        self.assertNotIn('data/quarantine/',serialized)
        self.assertNotIn('TIANJI_ADMIN_READ_TOKEN',serialized)

    def test_admin_layers_are_token_gated_aggregate_only(self):
        client=TestClient(create_app(admin_read_token='review-token'))
        path='/api/v1/admin/governance/layers'
        self.assertEqual(client.get(path).status_code,401)
        response=client.get(path,headers={'Authorization':'Bearer review-token'})
        self.assertEqual(response.status_code,200,response.text)
        data=response.json()
        self.assertTrue(data['read_only'])
        self.assertFalse(data['public_release'])
        records={row['id']:row for row in data['records']}
        self.assertEqual(set(records),{'raw','quarantine','canonical'})
        self.assertFalse(records['raw']['production_queryable'])
        self.assertFalse(records['quarantine']['production_queryable'])
        self.assertTrue(records['canonical']['production_queryable'])
        self.assertGreater(records['quarantine']['tracked_file_count'],0)
        self.assertGreater(records['canonical']['tracked_file_count'],0)
        self.assertGreater(records['canonical']['protected_file_count'],0)
        serialized=str(records)
        self.assertNotIn('data/quarantine/',serialized)
        self.assertNotIn('data/canonical/',serialized)
        self.assertNotIn('content_path',serialized)
        self.assertNotIn('sha256',serialized)
        self.assertNotIn('TIANJI_ADMIN_READ_TOKEN',serialized)

    def test_admin_algorithms_are_real_reviewed_contracts(self):
        client=TestClient(create_app(admin_read_token='review-token'))
        path='/api/v1/admin/governance/algorithms'
        self.assertEqual(client.get(path).status_code,401)
        response=client.get(path,headers={'Authorization':'Bearer review-token'})
        self.assertEqual(response.status_code,200,response.text)
        data=response.json()
        self.assertTrue(data['read_only'])
        self.assertFalse(data['public_release'])
        records=data['records']
        self.assertEqual({row['domain'] for row in records},set(PROVIDERS))
        self.assertTrue(all(row['deterministic'] for row in records))
        self.assertTrue(all(not row['ai_may_compute_chart'] for row in records))
        self.assertTrue(all(row['rule_count'] > 0 for row in records))
        self.assertTrue(all(row['executable_rule_count'] == row['rule_count'] for row in records))
        self.assertTrue(all(row['validated_rule_count'] == row['rule_count'] for row in records))
        self.assertTrue(any(row['unresolved'] for row in records))
        self.assertTrue(any(row['golden_case_ids'] for row in records))
        serialized=str(records)
        self.assertNotIn('DEMO-',serialized)
        self.assertNotIn('TIANJI_ADMIN_READ_TOKEN',serialized)

    def test_admin_provider_configuration_never_exposes_credentials(self):
        env={
            'TIANJI_AI_PROVIDER':'openai-compatible',
            'TIANJI_AI_BASE_URL':'https://provider.example.invalid/v1/private-path',
            'TIANJI_AI_MODEL':'example-model',
            'TIANJI_AI_API_KEY':'super-secret-provider-key',
            'TIANJI_AI_TIMEOUT_SECONDS':'25',
            'TIANJI_AI_MAX_OUTPUT_TOKENS':'2048',
            'TIANJI_EXPLANATION_PROMPT_VERSION':'explanation-prompt-v2',
        }
        with patch.dict('os.environ',env,clear=False):
            client=TestClient(create_app(admin_read_token='review-token'))
            path='/api/v1/admin/system/provider'
            self.assertEqual(client.get(path).status_code,401)
            response=client.get(path,headers={'Authorization':'Bearer review-token'})
            self.assertEqual(response.status_code,200,response.text)
            record=response.json()['records'][0]
            self.assertEqual(record['driver'],'openai-compatible')
            self.assertEqual(record['status'],'configured')
            self.assertTrue(record['configured'])
            self.assertEqual(record['endpoint_origin'],'https://provider.example.invalid')
            self.assertEqual(record['endpoint_host'],'provider.example.invalid')
            self.assertEqual(record['model'],'example-model')
            self.assertTrue(record['api_key_present'])
            self.assertFalse(record['api_key_exposed'])
            self.assertEqual(record['timeout_seconds'],25)
            self.assertEqual(record['max_output_tokens'],2048)
            self.assertFalse(record['live_connectivity_verified'])
            self.assertFalse(record['automatic_release_allowed'])
            serialized=str(record)
            self.assertNotIn('super-secret-provider-key',serialized)
            self.assertNotIn('private-path',serialized)

    def test_admin_prompt_registry_is_real_immutable_and_versioned(self):
        with patch.dict('os.environ',{'TIANJI_EXPLANATION_PROMPT_VERSION':DEFAULT_PROMPT},clear=False):
            client=TestClient(create_app(admin_read_token='review-token'))
            path='/api/v1/admin/system/prompts'
            self.assertEqual(client.get(path).status_code,401)
            response=client.get(path,headers={'Authorization':'Bearer review-token'})
            self.assertEqual(response.status_code,200,response.text)
            records={row['version']:row for row in response.json()['records']}
            self.assertEqual(set(records),set(PROMPTS))
            for version,row in records.items():
                expected=get_prompt(version)
                self.assertEqual(row['sha256'],expected['sha256'])
                self.assertEqual(row['instruction'],expected['instruction'])
                self.assertEqual(row['instruction_length'],len(expected['instruction']))
                self.assertTrue(row['immutable'])
                self.assertFalse(row['automatic_release_allowed'])
                self.assertEqual(row['configured_selection'],DEFAULT_PROMPT)
                self.assertTrue(row['selection_registered'])
            self.assertTrue(records[DEFAULT_PROMPT]['selected'])
            self.assertFalse(records['explanation-prompt-v1']['production_eligible'])
            self.assertTrue(records['explanation-prompt-v2']['production_eligible'])

    def test_admin_evaluation_registry_never_fabricates_live_scores(self):
        client=TestClient(create_app(admin_read_token='review-token'))
        path='/api/v1/admin/system/evaluations'
        self.assertEqual(client.get(path).status_code,401)
        response=client.get(path,headers={'Authorization':'Bearer review-token'})
        self.assertEqual(response.status_code,200,response.text)
        records=response.json()['records']
        self.assertEqual({row['domain'] for row in records},set(PROVIDERS))
        self.assertTrue(all(row['fixed_suite'] for row in records))
        self.assertTrue(all(row['tracked_status']=='fixture_only' for row in records))
        self.assertTrue(all(not row['live_model_quality_verified'] for row in records))
        self.assertTrue(all(row['human_semantic_review_required'] for row in records))
        self.assertTrue(all(not row['automatic_release_allowed'] for row in records))
        self.assertTrue(all(not row['online_ready'] for row in records))
        self.assertGreater(sum(row['eval_case_count'] for row in records),0)
        self.assertGreater(sum(row['refusal_control_count'] for row in records),0)
        self.assertGreater(sum(row['phase2_golden_count'] for row in records),0)
        self.assertTrue(any(row['suite_golden_ref_count'] > 0 for row in records))
        serialized=str(records)
        self.assertNotIn('online_ready\': True',serialized)
        self.assertNotIn('live_model_quality_verified\': True',serialized)

    def test_admin_rules_and_evidence_are_token_gated_reviewed_assets(self):
        client=TestClient(create_app(admin_read_token='review-token'))
        for path in (
            '/api/v1/admin/governance/rules',
            '/api/v1/admin/governance/evidence',
        ):
            self.assertEqual(client.get(path).status_code,401)

        headers={'Authorization':'Bearer review-token'}
        rules_response=client.get('/api/v1/admin/governance/rules',headers=headers)
        evidence_response=client.get('/api/v1/admin/governance/evidence',headers=headers)
        self.assertEqual(rules_response.status_code,200,rules_response.text)
        self.assertEqual(evidence_response.status_code,200,evidence_response.text)

        rules=rules_response.json()['records']
        evidence=evidence_response.json()['records']
        self.assertTrue(rules)
        self.assertTrue(evidence)
        self.assertTrue(all(row['evidence'] for row in rules))
        self.assertTrue(all(row['evidence_level'] in ('A','B','C') for row in evidence))
        self.assertTrue(any(row['phase2_bindings'] for row in rules))
        self.assertTrue(any(row['phase2_rule_ids'] for row in evidence))
        self.assertTrue(any(row['id']=='bazi.rule.r011' for row in rules))
        self.assertTrue(any(row['id']=='bazi.section.s017' for row in evidence))
        serialized=str({'rules':rules,'evidence':evidence})
        self.assertNotIn('data/quarantine/public_domain_snapshots',serialized)
        self.assertNotIn('TIANJI_ADMIN_READ_TOKEN',serialized)

    def test_health_capabilities_and_openapi(self):
        self.assertEqual(self.client.get('/health').json()['status'],'ok')
        capabilities=self.client.get('/api/v1/capabilities').json()
        self.assertEqual({d['domain'] for d in capabilities['domains']},set(PROVIDERS))
        schema=self.client.get('/openapi.json').json()
        for path in ['/health','/api/v1/capabilities','/api/v1/execute']:self.assertIn(path,schema['paths'])
        self.assertEqual(self.client.get('/docs').status_code,200)
    def test_missing_runtime_returns_503_and_validation_hides_values(self):
        with patch('tianji_kb.runtime_catalog.Path.is_file',return_value=False):
            self.assertEqual(self.client.get('/health').status_code,503)
            self.assertEqual(self.client.post('/api/v1/execute',json=self.request('yijing')).status_code,503)
        response=self.client.post('/api/v1/execute',json={**self.request('yijing'),'api_key':'do-not-echo'})
        self.assertEqual(response.status_code,422);self.assertNotIn('do-not-echo',response.text)
