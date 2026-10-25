"""B022: draft rollback HTTP verification (TJ-026.4 batch 3).

Offline acceptance ONLY: requires the FastAPI stack. NOT wired into
public CI (validate.yml) and must never be claimed as a public CI run.
Run against an assembled backend copy, e.g.:

    PYTHONPATH=<backend-copy>/src python -m unittest tests.test_b022_rollback_http -v

Pure state-machine coverage (no FastAPI, no data) lives in
test_b022_rollback.py and DOES run in public CI.

Batch 3 scope reminder: version snapshots on every mutation +
publisher-only rollback through the dedicated endpoint (NOT the
generic /{action} route — route order matters: the rollback route
must be registered before it). Rollback lands in 'draft'; rejected
stays terminal. The compensating audit record is appended only and
carries the draft id + version, never draft content.
"""

import os
import tempfile
import unittest

from fastapi.testclient import TestClient

from tianji_kb.api import create_app

ROLE_TOKENS = {
    'user-token': 'user',
    'editor-token': 'editor',
    'reviewer-token': 'reviewer',
    'publisher-token': 'publisher',
}
READ_TOKEN = 'read-token'


def _client(role_tokens=None):
    # TJ-026.5: the app now persists admin state to SQLite by
    # default. Tests point it at a throwaway tmp file so runs stay
    # hermetic and never create tianji_admin.db in the repo. Stores
    # are per-app-instance, so a fresh file per _client() call keeps
    # the same isolation the in-memory stores had.
    fd, db_path = tempfile.mkstemp(suffix='.db')
    os.close(fd)
    return TestClient(create_app(
        admin_role_tokens=dict(ROLE_TOKENS) if role_tokens is None else role_tokens,
        admin_read_token=READ_TOKEN,
        admin_read_scopes={'system'},
        admin_db_path=db_path))


def _auth(token):
    return {} if token is None else {'Authorization': f'Bearer {token}'}


def _create(client, token, title='Draft title', body='Draft body secret'):
    return client.post('/api/v1/admin/drafts',
                       json={'title': title, 'body': body},
                       headers=_auth(token))


def _edit(client, token, draft_id, title=None, body=None):
    payload = {}
    if title is not None:
        payload['title'] = title
    if body is not None:
        payload['body'] = body
    return client.patch(f'/api/v1/admin/drafts/{draft_id}',
                        json=payload, headers=_auth(token))


def _act(client, token, draft_id, action):
    return client.post(f'/api/v1/admin/drafts/{draft_id}/{action}',
                       headers=_auth(token))


def _rollback(client, token, draft_id, version):
    return client.post(f'/api/v1/admin/drafts/{draft_id}/rollback',
                       json={'version': version}, headers=_auth(token))


def _get(client, token, draft_id):
    return client.get(f'/api/v1/admin/drafts/{draft_id}',
                      headers=_auth(token))


def _audit(client):
    resp = client.get('/api/v1/admin/system/audit', headers=_auth(READ_TOKEN))
    assert resp.status_code == 200, resp.text
    return resp.json()['entries']


def _published(client, title='v1 title', body='v1 body'):
    """Create -> edit -> submit -> approve -> publish; return id."""
    created = _create(client, 'editor-token', title, body)
    assert created.status_code == 200, created.text
    draft_id = created.json()['draft']['id']
    edited = _edit(client, 'editor-token', draft_id, title='v2 title')
    assert edited.status_code == 200, edited.text
    for token, action, expected in [
            ('editor-token', 'submit', 'submitted'),
            ('reviewer-token', 'approve', 'approved'),
            ('publisher-token', 'publish', 'published')]:
        resp = _act(client, token, draft_id, action)
        assert resp.status_code == 200, resp.text
        assert resp.json()['draft']['status'] == expected
    return draft_id


class TestB022RollbackHttp(unittest.TestCase):
    def test_full_rollback_flow_restores_v1_and_draft_status(self):
        client = _client()
        draft_id = _published(client)
        before = _get(client, 'publisher-token', draft_id).json()['draft']
        self.assertEqual(before['status'], 'published')
        self.assertEqual(
            [(v['version'], v['action']) for v in before['versions']],
            [(1, 'create'), (2, 'edit'), (3, 'submit'),
             (4, 'approve'), (5, 'publish')])
        resp = _rollback(client, 'publisher-token', draft_id, 1)
        self.assertEqual(resp.status_code, 200, resp.text)
        draft = resp.json()['draft']
        self.assertEqual(draft['status'], 'draft')
        self.assertEqual(draft['title'], 'v1 title')
        self.assertEqual(draft['body'], 'v1 body')
        self.assertEqual(draft['transitions'][-1]['action'], 'rollback')
        self.assertEqual(draft['transitions'][-1]['version'], 1)
        self.assertEqual(draft['versions'][-1]['action'], 'rollback')
        self.assertEqual(draft['versions'][-1]['title'], 'v1 title')
        # Prior history untouched: only the rollback records are new.
        self.assertEqual(draft['transitions'][:-1], before['transitions'])
        self.assertEqual(draft['versions'][:-1], before['versions'])
        # Response carries the SQLite storage note (TJ-026.5).
        self.assertEqual(resp.json()['storage'], 'sqlite')
        self.assertIn('重启', resp.json()['storage_note'])

    def test_rollback_endpoint_not_captured_by_action_route(self):
        # Route-order regression guard: if the dedicated rollback route
        # were registered after the generic /{action} route, 'rollback'
        # would be rejected as an unknown action (403) instead of
        # reaching the rollback handler.
        client = _client()
        draft_id = _published(client)
        resp = _rollback(client, 'publisher-token', draft_id, 1)
        self.assertEqual(resp.status_code, 200, resp.text)
        self.assertEqual(resp.json()['draft']['status'], 'draft')

    def test_rollback_role_matrix_403_and_denied_audit(self):
        client = _client()
        draft_id = _published(client)
        for token in ['user-token', 'editor-token', 'reviewer-token']:
            resp = _rollback(client, token, draft_id, 1)
            self.assertEqual(resp.status_code, 403, resp.text)
            self.assertEqual(
                resp.json()['detail']['code'], 'admin_forbidden')
        # Denied attempts leave the published draft untouched.
        got = _get(client, 'publisher-token', draft_id).json()['draft']
        self.assertEqual(got['status'], 'published')
        self.assertEqual(got['title'], 'v2 title')
        # Each denied attempt leaves exactly one denied audit record.
        denied = [e for e in _audit(client)
                  if e['what'] == f'draft:rollback:{draft_id}'
                  and e['outcome'] == 'denied']
        self.assertEqual(len(denied), 3)
        self.assertTrue(all(e['detail'] == 'forbidden' for e in denied))

    def test_rollback_unknown_draft_404_unknown_version_422(self):
        client = _client()
        draft_id = _published(client)
        resp = _rollback(client, 'publisher-token', 'D-999', 1)
        self.assertEqual(resp.status_code, 404, resp.text)
        self.assertEqual(
            resp.json()['detail']['code'], 'draft_not_found')
        resp = _rollback(client, 'publisher-token', draft_id, 99)
        self.assertEqual(resp.status_code, 422, resp.text)
        self.assertEqual(
            resp.json()['detail']['code'], 'invalid_draft_transition')

    def test_rollback_rejected_draft_422(self):
        client = _client()
        created = _create(client, 'editor-token')
        draft_id = created.json()['draft']['id']
        _act(client, 'editor-token', draft_id, 'submit')
        _act(client, 'reviewer-token', draft_id, 'reject')
        resp = _rollback(client, 'publisher-token', draft_id, 1)
        self.assertEqual(resp.status_code, 422, resp.text)
        got = _get(client, 'publisher-token', draft_id).json()['draft']
        self.assertEqual(got['status'], 'rejected')

    def test_rollback_audit_compensating_only_appends_no_content(self):
        client = _client()
        draft_id = _published(client)
        before = _audit(client)
        resp = _rollback(client, 'publisher-token', draft_id, 1)
        self.assertEqual(resp.status_code, 200, resp.text)
        after = _audit(client)
        # Prior entries byte-identical; exactly one new record.
        self.assertEqual(after[:-1], before)
        self.assertEqual(len(after), len(before) + 1)
        compensating = after[-1]
        self.assertEqual(compensating['what'], f'draft:rollback:{draft_id}')
        self.assertEqual(compensating['outcome'], 'allowed')
        self.assertEqual(compensating['detail'], 'version:1')
        # No draft content leaks into any audit record.
        blob = repr(after)
        self.assertNotIn('v1 body', blob)
        self.assertNotIn('v2 title', blob)
        self.assertNotIn('Draft body secret', blob)

    def test_rollback_without_role_token_401(self):
        client = _client()
        draft_id = _published(client)
        resp = _rollback(client, None, draft_id, 1)
        self.assertEqual(resp.status_code, 401, resp.text)
        resp = _rollback(client, 'bad-token', draft_id, 1)
        self.assertEqual(resp.status_code, 401, resp.text)


if __name__ == '__main__':
    unittest.main()
