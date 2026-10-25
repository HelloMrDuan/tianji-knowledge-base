"""B018: admin role probe + audit read HTTP verification (TJ-026.4
batch 1: role model, unauthorized blocking, audit skeleton).

Offline acceptance ONLY: requires the FastAPI stack. NOT wired into
public CI (validate.yml) and must never be claimed as a public CI run.
Run against an assembled backend copy, e.g.:

    PYTHONPATH=<backend-copy>/src python -m unittest tests.test_b018_admin_roles_http -v

Pure decision-matrix coverage (no FastAPI, no data) lives in
test_b018_admin_roles.py and DOES run in public CI.

Batch 1 scope reminder: the probe endpoint is a CHECKPOINT, not a
business write. Every allowed probe response carries write_applied=False
and no draft/approval/publish business exists behind it.
"""

import os
import tempfile
import unittest
from unittest import mock

from fastapi.testclient import TestClient

from tianji_kb.api import create_app

ROLE_TOKENS = {
    'user-token': 'user',
    'editor-token': 'editor',
    'reviewer-token': 'reviewer',
    'publisher-token': 'publisher',
}
READ_TOKEN = 'read-token'


def _role_client(read_scopes={'system'}):
    # TJ-026.5: tmp DB per client (see test_b020_drafts_http).
    fd, db_path = tempfile.mkstemp(suffix='.db')
    os.close(fd)
    return TestClient(create_app(
        admin_role_tokens=dict(ROLE_TOKENS),
        admin_read_token=READ_TOKEN,
        admin_read_scopes=set(read_scopes),
        admin_db_path=db_path))


def _probe(client, token, operation):
    headers = {} if token is None else {'Authorization': f'Bearer {token}'}
    return client.post('/api/v1/admin/write/probe',
                       json={'operation': operation}, headers=headers)


def _audit(client, token):
    headers = {} if token is None else {'Authorization': f'Bearer {token}'}
    return client.get('/api/v1/admin/system/audit', headers=headers)


class TestB018WriteProbeHttp(unittest.TestCase):
    def test_user_role_denied_and_audited(self):
        client = _role_client()
        resp = _probe(client, 'user-token', 'publish')
        self.assertEqual(resp.status_code, 403)
        self.assertEqual(resp.json()['detail']['code'], 'admin_forbidden')
        audit = _audit(client, READ_TOKEN)
        self.assertEqual(audit.status_code, 200)
        entries = audit.json()['entries']
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0]['who'], 'user')
        self.assertEqual(entries[0]['what'], 'write_probe:publish')
        self.assertEqual(entries[0]['outcome'], 'denied')

    def test_editor_draft_allowed_but_applies_no_write(self):
        client = _role_client()
        resp = _probe(client, 'editor-token', 'draft')
        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        self.assertEqual(body['role'], 'editor')
        self.assertEqual(body['operation'], 'draft')
        self.assertTrue(body['probe'])
        # Batch 1 honesty contract: the probe never applies a write.
        self.assertFalse(body['write_applied'])
        audit = _audit(client, READ_TOKEN)
        entries = audit.json()['entries']
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0]['outcome'], 'allowed')

    def test_editor_publish_denied(self):
        client = _role_client()
        resp = _probe(client, 'editor-token', 'publish')
        self.assertEqual(resp.status_code, 403)
        self.assertEqual(resp.json()['detail']['code'], 'admin_forbidden')

    def test_invalid_and_missing_tokens_are_401_and_audited(self):
        client = _role_client()
        resp = _probe(client, 'wrong-token', 'draft')
        self.assertEqual(resp.status_code, 401)
        self.assertEqual(resp.json()['detail']['code'], 'admin_unauthorized')
        resp = _probe(client, None, 'draft')
        self.assertEqual(resp.status_code, 401)
        audit = _audit(client, READ_TOKEN)
        entries = audit.json()['entries']
        self.assertEqual(len(entries), 2)
        self.assertTrue(all(e['outcome'] == 'denied' for e in entries))
        self.assertTrue(all(e['who'] == 'unknown' for e in entries))

    def test_unconfigured_role_tokens_is_503(self):
        # TJ-026.5: tmp DB keeps runs hermetic (see _role_client).
        fd, db_path = tempfile.mkstemp(suffix='.db')
        os.close(fd)
        client = TestClient(create_app(admin_read_token=READ_TOKEN,
                                       admin_db_path=db_path))
        resp = _probe(client, 'user-token', 'draft')
        self.assertEqual(resp.status_code, 503)
        self.assertEqual(resp.json()['detail']['code'],
                         'admin_role_not_configured')

    def test_unknown_operation_is_422(self):
        client = _role_client()
        resp = _probe(client, 'publisher-token', 'delete-all')
        self.assertEqual(resp.status_code, 422)

    def test_audit_entries_accumulate_in_order(self):
        client = _role_client()
        _probe(client, 'editor-token', 'draft')
        _probe(client, 'user-token', 'publish')
        _probe(client, 'publisher-token', 'publish')
        entries = _audit(client, READ_TOKEN).json()['entries']
        self.assertEqual(
            [(e['who'], e['what'], e['outcome']) for e in entries],
            [('editor', 'write_probe:draft', 'allowed'),
             ('user', 'write_probe:publish', 'denied'),
             ('publisher', 'write_probe:publish', 'allowed')])


class TestB018EnvFallbackHttp(unittest.TestCase):
    def test_env_vars_configure_read_token_and_scopes(self):
        # Regression for a pre-existing defect found during B018 live
        # verification: create_app() with NO explicit params used to
        # leave the read token unset (503 for every read) and set the
        # scopes to the token string. Env configuration must work.
        # TJ-026.5: the tmp DB path also comes via env, so the
        # create_app() call below stays param-free (token fallback is
        # what this test exercises) while runs stay hermetic.
        fd, db_path = tempfile.mkstemp(suffix='.db')
        os.close(fd)
        env = {
            'TIANJI_ADMIN_READ_TOKEN': 'env-read-token',
            'TIANJI_ADMIN_READ_SCOPES': 'system',
            'TIANJI_ADMIN_ROLE_TOKENS': 'env-user:user,env-editor:editor',
            'TIANJI_ADMIN_DB_PATH': db_path,
        }
        with mock.patch.dict(os.environ, env, clear=False):
            client = TestClient(create_app())
            probe = client.post(
                '/api/v1/admin/write/probe', json={'operation': 'draft'},
                headers={'Authorization': 'Bearer env-editor'})
            self.assertEqual(probe.status_code, 200)
            audit = client.get(
                '/api/v1/admin/system/audit',
                headers={'Authorization': 'Bearer env-read-token'})
            self.assertEqual(audit.status_code, 200)
            self.assertEqual(len(audit.json()['entries']), 1)

    def test_env_read_token_without_system_scope_is_403(self):
        # TJ-026.5: tmp DB via env (see above) keeps runs hermetic.
        fd, db_path = tempfile.mkstemp(suffix='.db')
        os.close(fd)
        env = {
            'TIANJI_ADMIN_READ_TOKEN': 'env-read-token',
            'TIANJI_ADMIN_READ_SCOPES': 'governance',
            'TIANJI_ADMIN_DB_PATH': db_path,
        }
        with mock.patch.dict(os.environ, env, clear=False):
            client = TestClient(create_app())
            resp = client.get(
                '/api/v1/admin/system/audit',
                headers={'Authorization': 'Bearer env-read-token'})
            self.assertEqual(resp.status_code, 403)
            self.assertEqual(resp.json()['detail']['code'], 'admin_forbidden')


class TestB018AuditReadHttp(unittest.TestCase):
    def test_audit_read_requires_system_scope(self):
        client = _role_client(read_scopes={'governance'})
        resp = _audit(client, READ_TOKEN)
        self.assertEqual(resp.status_code, 403)
        self.assertEqual(resp.json()['detail']['code'], 'admin_forbidden')

    def test_audit_read_without_token_is_401(self):
        client = _role_client()
        resp = _audit(client, None)
        self.assertEqual(resp.status_code, 401)

    def test_audit_endpoint_has_no_write_method(self):
        client = _role_client()
        headers = {'Authorization': f'Bearer {READ_TOKEN}'}
        self.assertEqual(client.put('/api/v1/admin/system/audit',
                                    headers=headers).status_code, 405)
        self.assertEqual(client.delete('/api/v1/admin/system/audit',
                                       headers=headers).status_code, 405)


if __name__ == '__main__':
    unittest.main()
