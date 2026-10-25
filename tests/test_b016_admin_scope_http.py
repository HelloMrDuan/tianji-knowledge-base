"""B016: admin read-scope HTTP verification (TJ-026.3).

Offline acceptance ONLY: requires the FastAPI stack plus full runtime +
knowledge data (EvidenceResolver reads reviewed Canonical assets). NOT
wired into public CI (validate.yml) and must never be claimed as a public
CI run. Run against an assembled backend copy, e.g.:

    PYTHONPATH=<backend-copy>/src python -m unittest tests.test_b016_admin_scope_http -v

Pure decision-matrix coverage (no FastAPI, no data) lives in
test_b016_admin_scope.py and DOES run in public CI.
"""

import os
import unittest
from unittest import mock

from fastapi.testclient import TestClient

from tianji_kb.api import create_app

TOKEN = 'b016-http-token'

# (path, method, scope, body-or-None). The research POST needs a valid body;
# governance/system GETs need none.
ENDPOINTS = [
    ('/api/v1/admin/research/dream', 'POST', 'research', {'dream_text': 'test dream'}),
    ('/api/v1/admin/governance/conflicts', 'GET', 'governance', None),
    ('/api/v1/admin/governance/rules', 'GET', 'governance', None),
    ('/api/v1/admin/governance/evidence', 'GET', 'governance', None),
    ('/api/v1/admin/governance/classics', 'GET', 'governance', None),
    ('/api/v1/admin/governance/chapters', 'GET', 'governance', None),
    ('/api/v1/admin/governance/terms', 'GET', 'governance', None),
    ('/api/v1/admin/governance/sources', 'GET', 'governance', None),
    ('/api/v1/admin/governance/layers', 'GET', 'governance', None),
    ('/api/v1/admin/governance/algorithms', 'GET', 'governance', None),
    ('/api/v1/admin/system/provider', 'GET', 'system', None),
    ('/api/v1/admin/system/prompts', 'GET', 'system', None),
]


def _call(client, path, method, token, body):
    headers = {} if token is None else {'Authorization': f'Bearer {token}'}
    if method == 'POST':
        return client.post(path, json=body, headers=headers)
    return client.get(path, headers=headers)


class TestB016AdminScopeHttp(unittest.TestCase):
    def test_unconfigured_token_is_503(self):
        client = TestClient(create_app())
        for path, method, _scope, body in ENDPOINTS:
            with self.subTest(path=path):
                resp = _call(client, path, method, TOKEN, body)
                self.assertEqual(resp.status_code, 503)
                self.assertEqual(resp.json()['detail']['code'],
                                 'admin_auth_not_configured')

    def test_missing_or_wrong_token_is_401(self):
        client = TestClient(create_app(admin_read_token=TOKEN))
        for path, method, _scope, body in ENDPOINTS:
            for token in (None, 'wrong-token'):
                with self.subTest(path=path, token=token):
                    resp = _call(client, path, method, token, body)
                    self.assertEqual(resp.status_code, 401)
                    self.assertEqual(resp.json()['detail']['code'],
                                     'admin_unauthorized')

    def test_restricted_token_is_403_out_of_scope_and_200_in_scope(self):
        # Token granted governance only: research + system must 403,
        # governance must 200 with real records.
        client = TestClient(create_app(admin_read_token=TOKEN,
                                       admin_read_scopes={'governance'}))
        for path, method, scope, body in ENDPOINTS:
            with self.subTest(path=path, scope=scope):
                resp = _call(client, path, method, TOKEN, body)
                if scope == 'governance':
                    self.assertEqual(resp.status_code, 200)
                    self.assertTrue(resp.json()['read_only'])
                    self.assertIsInstance(resp.json()['records'], list)
                else:
                    self.assertEqual(resp.status_code, 403)
                    self.assertEqual(resp.json()['detail']['code'],
                                     'admin_forbidden')

    def test_empty_scope_set_forbids_everywhere(self):
        client = TestClient(create_app(admin_read_token=TOKEN,
                                       admin_read_scopes=set()))
        for path, method, _scope, body in ENDPOINTS:
            with self.subTest(path=path):
                resp = _call(client, path, method, TOKEN, body)
                self.assertEqual(resp.status_code, 403)
                self.assertEqual(resp.json()['detail']['code'],
                                 'admin_forbidden')

    def test_unrestricted_token_reaches_all_endpoints(self):
        client = TestClient(create_app(admin_read_token=TOKEN))
        for path, method, _scope, body in ENDPOINTS:
            with self.subTest(path=path):
                resp = _call(client, path, method, TOKEN, body)
                self.assertEqual(resp.status_code, 200)

    def test_env_scope_list_restricts_when_param_absent(self):
        with mock.patch.dict(os.environ, {'TIANJI_ADMIN_READ_SCOPES': 'system'}):
            client = TestClient(create_app(admin_read_token=TOKEN))
        resp = _call(client, '/api/v1/admin/system/provider', 'GET', TOKEN, None)
        self.assertEqual(resp.status_code, 200)
        resp = _call(client, '/api/v1/admin/governance/rules', 'GET', TOKEN, None)
        self.assertEqual(resp.status_code, 403)
        self.assertEqual(resp.json()['detail']['code'], 'admin_forbidden')


if __name__ == '__main__':
    unittest.main()
