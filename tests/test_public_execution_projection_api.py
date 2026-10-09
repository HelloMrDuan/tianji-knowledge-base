"""Real deterministic public projection checks."""
import unittest
import os
import json
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


    def test_public_bazi_internal_rule_and_evidence_ids_not_exposed(self):
        body={'domain':'bazi','input':{'value':'2000-01-07T12:00:00+08:00'},'explain':False}
        detailed=self.client.post('/api/v1/execute',json=body)
        public=self.client.post('/api/v1/public/execute',json=body)
        self.assertEqual(public.status_code,200,public.text)
        original=detailed.json()
        projected=public.json()
        serialized=json.dumps(projected,ensure_ascii=False)
        for identifier in original['evidence']:
            self.assertNotIn(identifier,serialized)
        for match in original['rule_matches']:
            self.assertNotIn(match['rule_id'],serialized)
        self.assertTrue(all(key.startswith('E') for key in projected['evidence']))
        self.assertTrue(all(row['rule_id'].startswith('R')
                            for row in projected['rule_matches'] if row.get('rule_id')))
        self.assertTrue(all(step['step'].startswith('计算步骤 ')
                            for step in projected['trace']))

    def test_public_compatibility_matrix_uses_opaque_identifiers(self):
        body={'scenario_id':'compatibility','input':{
            'person_a_birth_value':'2000-01-07T12:00:00+08:00',
            'person_b_birth_value':'2000-02-01T12:00:00+08:00'}}
        detailed=self.client.post('/api/v1/scenarios/execute',json=body)
        projected=self.client.post('/api/v1/scenarios/public',json=body)
        self.assertEqual(projected.status_code,200,projected.text)
        full, safe=detailed.json(),projected.json()
        self.assertEqual(full['result']['person_a']['day_master'],
                         safe['result']['person_a']['day_master'])
        matrix=safe['result']['relation_evidence_matrix']
        self.assertTrue(matrix)
        for item in matrix:
            self.assertTrue(all(ref.startswith('R') for ref in item['derived_from_rule_ids']))
            self.assertTrue(all(ref.startswith('E') for ref in item['evidence_ids']))
        serialized=json.dumps(safe,ensure_ascii=False)
        for identifier in full['evidence']:
            self.assertNotIn(identifier,serialized)
        self.assertNotIn('bazi.phase2.',serialized)

    def test_projection_strips_injected_private_paths_in_nested_results(self):
        from tianji_kb.public_projection import project_execution
        internal={
            'domain':'test','chart':{
                'ganzhi':'丁未','canonical_path':'data/canonical/secret.json',
                'sections':[{'derived_from_rule_ids':['private.rule'],
                             'evidence_ids':['private-ref'],
                             'source_refs':[{'path':'internal'}],
                             'sha256':'abc'}]},
            'evidence':{'private-ref':{
                'classic_title':'校勘文本',
                'original_text':'已经审核的短引',
                'canonical_path':'data/canonical/secret.json',
                'evidence_level':'C'}},
            'rule_matches':[{'rule_id':'private.rule','matched':True,
                             'evidence_ids':['private-ref']}],
            'trace':[{'rule_id':'private.rule','inputs':{'private_token':'do not publish'}}],
        }
        public=project_execution(internal)
        serialized=json.dumps(public,ensure_ascii=False)
        for forbidden in ('data/canonical','private.rule','private-ref',
                          'private_token','source_refs','sha256'):
            self.assertNotIn(forbidden,serialized)
        self.assertEqual(public['chart']['ganzhi'],'丁未')
        self.assertEqual(public['chart']['sections'][0]['derived_from_rule_ids'],['R01'])
        self.assertEqual(public['chart']['sections'][0]['evidence_ids'],['E01'])
        self.assertEqual(public['rule_matches'][0]['evidence_ids'],['E01'])
        self.assertEqual(internal['evidence']['private-ref']['canonical_path'],
                         'data/canonical/secret.json')

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
