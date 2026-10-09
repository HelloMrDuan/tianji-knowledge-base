"""Real deterministic public projection checks."""
import unittest
import os
from unittest.mock import patch
from fastapi.testclient import TestClient
from tianji_kb.api import create_app

class ProjectionSmoke(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client=cls.enterClassContext(TestClient(create_app()))

    def test_bazi_public_result_matches_detailed_facts(self):
        body={'domain':'bazi','input':{'value':'2000-01-07T12:00:00+08:00'},'explain':False}
        full=self.client.post('/api/v1/execute',json=body)
        safe=self.client.post('/api/v1/public/execute',json=body)
        self.assertEqual(safe.status_code,200,safe.text)
        self.assertEqual(full.json()['chart'],safe.json()['chart'])
        self.assertEqual(safe.json()['chart']['day_master']['stem'],'甲')
        self.assertEqual(safe.headers['cache-control'],'no-store')
        for row in safe.json()['evidence'].values():
            self.assertEqual(set(row),{'classic_title','original_text','evidence_level'})
            self.assertLessEqual(len(row['original_text']),120)
        self.assertTrue(all(set(row)=={'step'} for row in safe.json()['trace']))
        self.assertEqual(self.client.post('/api/v1/public/execute',
                         json={**body,'mode':'research'}).status_code,422)

    def test_annual_scenario_keeps_calculation_but_projects_evidence(self):
        body={'scenario_id':'yearly','input':{
            'birth_value':'2000-01-07T12:00:00+08:00','target_year':2027}}
        original=self.client.post('/api/v1/scenarios/execute',json=body)
        safe=self.client.post('/api/v1/scenarios/public',json=body)
        self.assertEqual(safe.status_code,200,safe.text)
        self.assertEqual(original.json()['result'],safe.json()['result'])
        self.assertEqual(safe.json()['result']['target_year']['ganzhi'],'丁未')
        self.assertEqual(safe.headers['cache-control'],'no-store')
        for row in safe.json()['evidence'].values():
            self.assertEqual(set(row),{'classic_title','original_text','evidence_level'})
        self.assertEqual(self.client.post('/api/v1/scenarios/public',
            json={'scenario_id':'dream','input':{}}).status_code,422)

    def test_sealed_detailed_execution_needs_internal_configuration(self):
        body={'domain':'bazi','input':{'value':'2000-01-07T12:00:00+08:00'}}
        with patch.dict(os.environ,{'TIANJI_RUNTIME_MODE':'sealed'},clear=True):
            client=TestClient(create_app())
            self.assertEqual(client.post('/api/v1/execute',json=body).status_code,503)
            self.assertEqual(client.post('/api/v1/scenarios/execute',
                json={'scenario_id':'yearly','input':{}}).status_code,503)
        with patch.dict(os.environ,{'TIANJI_RUNTIME_MODE':'sealed',
                                      'TIANJI_INTERNAL_EXECUTE_TOKEN':'restricted'},clear=True):
            client=TestClient(create_app())
            self.assertEqual(client.post('/api/v1/execute',json=body).status_code,401)
            self.assertEqual(client.post('/api/v1/scenarios/execute',
                json={'scenario_id':'yearly','input':{}}).status_code,401)
