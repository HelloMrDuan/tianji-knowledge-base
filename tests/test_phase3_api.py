import unittest
from unittest.mock import patch
from fastapi.testclient import TestClient
from tianji_kb.api import create_app,EXAMPLES
from tianji_kb.engine import PROVIDERS
from tianji_kb.resolver import EvidenceResolver

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
