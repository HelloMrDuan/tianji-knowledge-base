"""B020: draft approval flow HTTP verification (TJ-026.4 batch 2).

Offline acceptance ONLY: requires the FastAPI stack. NOT wired into
public CI (validate.yml) and must never be claimed as a public CI run.
Run against an assembled backend copy, e.g.:

    PYTHONPATH=<backend-copy>/src python -m unittest tests.test_b020_drafts_http -v

Pure state-machine coverage (no FastAPI, no data) lives in
test_b020_drafts.py and DOES run in public CI.

Batch 2 scope reminder: draft storage (process memory) + state machine
+ draft/approve/publish endpoints ONLY. No durable storage, no
rollback, no version snapshots. Draft content must never appear in
audit records or public endpoints; every write attempt (allowed or
denied) leaves exactly one audit record.
"""

import unittest

from fastapi.testclient import TestClient

from tianji_kb.api import create_app

ROLE_TOKENS = {
    'user-token': 'user',
    'editor-token': 'editor',
    'reviewer-token': 'reviewer',
    'publisher-token': 'publisher',
}
READ_TOKEN = 'read-token-for-tests'


def _client(role_tokens=None):
    return TestClient(create_app(
        admin_role_tokens=dict(ROLE_TOKENS) if role_tokens is None else role_tokens,
        admin_read_token=READ_TOKEN,
        admin_read_scopes={'system'}))


def _auth(token):
    return {} if token is None else {'Authorization': f'Bearer {token}'}


def _create(client, token, title='Draft title', body='Draft body secret'):
    return client.post('/api/v1/admin/drafts',
                       json={'title': title, 'body': body},
                       headers=_auth(token))


def _act(client, token, draft_id, action):
    return client.post(f'/api/v1/admin/drafts/{draft_id}/{action}',
                       headers=_auth(token))


def _audit(client):
    resp = client.get('/api/v1/admin/system/audit', headers=_auth(READ_TOKEN))
    assert resp.status_code == 200, resp.text
    return resp.json()['entries']


class TestB020DraftFlowHttp(unittest.TestCase):
    def test_full_flow_create_submit_approve_publish(self):
        client = _client()
        created = _create(client, 'editor-token')
        self.assertEqual(created.status_code, 200, created.text)
        draft = created.json()['draft']
        self.assertEqual(draft['status'], 'draft')
        self.assertEqual(draft['author_role'], 'editor')
        self.assertEqual(created.json()['storage'], 'process_memory')
        self.assertIn('重启', created.json()['storage_note'])
        draft_id = draft['id']
        for token, action, expected in [
                ('editor-token', 'submit', 'submitted'),
                ('reviewer-token', 'approve', 'approved'),
                ('publisher-token', 'publish', 'published')]:
            resp = _act(client, token, draft_id, action)
            self.assertEqual(resp.status_code, 200, resp.text)
            self.assertEqual(resp.json()['draft']['status'], expected)
        # Approval history is queryable on the record itself.
        got = client.get(f'/api/v1/admin/drafts/{draft_id}',
                         headers=_auth('publisher-token'))
        self.assertEqual(got.status_code, 200)
        actions = [(t['action'], t['role'])
                   for t in got.json()['draft']['transitions']]
        self.assertEqual(actions, [
            ('create', 'editor'),
            ('submit', 'editor'),
            ('approve', 'reviewer'),
            ('publish', 'publisher'),
        ])

    def test_reject_branch_and_rejected_is_terminal(self):
        client = _client()
        draft_id = _create(client, 'editor-token').json()['draft']['id']
        self.assertEqual(
            _act(client, 'editor-token', draft_id, 'submit').status_code, 200)
        rejected = _act(client, 'reviewer-token', draft_id, 'reject')
        self.assertEqual(rejected.status_code, 200)
        self.assertEqual(rejected.json()['draft']['status'], 'rejected')
        for token, action in [('publisher-token', 'publish'),
                              ('editor-token', 'submit')]:
            resp = _act(client, token, draft_id, action)
            self.assertEqual(resp.status_code, 422, resp.text)
            self.assertEqual(resp.json()['detail']['code'],
                             'invalid_draft_transition')

    def test_edit_only_in_draft_status(self):
        client = _client()
        draft_id = _create(client, 'editor-token').json()['draft']['id']
        edited = client.patch(f'/api/v1/admin/drafts/{draft_id}',
                              json={'title': 'Edited title'},
                              headers=_auth('editor-token'))
        self.assertEqual(edited.status_code, 200)
        self.assertEqual(edited.json()['draft']['title'], 'Edited title')
        _act(client, 'editor-token', draft_id, 'submit')
        late = client.patch(f'/api/v1/admin/drafts/{draft_id}',
                            json={'title': 'Too late'},
                            headers=_auth('editor-token'))
        self.assertEqual(late.status_code, 422)
        self.assertEqual(late.json()['detail']['code'],
                         'invalid_draft_transition')
        empty = client.patch(f'/api/v1/admin/drafts/{draft_id}',
                             json={}, headers=_auth('editor-token'))
        self.assertEqual(empty.status_code, 422)

    def test_illegal_publish_from_draft_is_422_and_audited(self):
        client = _client()
        draft_id = _create(client, 'editor-token').json()['draft']['id']
        resp = _act(client, 'publisher-token', draft_id, 'publish')
        self.assertEqual(resp.status_code, 422)
        self.assertEqual(resp.json()['detail']['code'],
                         'invalid_draft_transition')
        # The draft itself is untouched by the failed attempt.
        got = client.get(f'/api/v1/admin/drafts/{draft_id}',
                         headers=_auth('publisher-token'))
        self.assertEqual(got.json()['draft']['status'], 'draft')
        entries = _audit(client)
        denied = [e for e in entries
                  if e['what'] == f'draft:publish:{draft_id}'
                  and e['outcome'] == 'denied']
        self.assertEqual(len(denied), 1)
        self.assertEqual(denied[0]['detail'], 'invalid_transition')

    def test_role_matrix_over_endpoints(self):
        client = _client()
        # user: every write denied.
        resp = _create(client, 'user-token')
        self.assertEqual(resp.status_code, 403)
        self.assertEqual(resp.json()['detail']['code'], 'admin_forbidden')
        # editor: draft ops yes, approve/publish no.
        draft_id = _create(client, 'editor-token').json()['draft']['id']
        _act(client, 'editor-token', draft_id, 'submit')
        denied_approve = _act(client, 'editor-token', draft_id, 'approve')
        self.assertEqual(denied_approve.status_code, 403)
        # reviewer: approve yes, publish no.
        _act(client, 'reviewer-token', draft_id, 'approve')
        denied_publish = _act(client, 'reviewer-token', draft_id, 'publish')
        self.assertEqual(denied_publish.status_code, 403)
        # publisher: publish yes.
        published = _act(client, 'publisher-token', draft_id, 'publish')
        self.assertEqual(published.status_code, 200)
        # Unknown action: forbidden before any state is touched.
        # B022 note: batch 2 used 'rollback' here as the unknown
        # example, but batch 3 gave rollback its own endpoint (with a
        # version body), so the example moves to a genuinely unknown
        # action. The 403 assertion is unchanged.
        unknown = _act(client, 'publisher-token', draft_id, 'bogus')
        self.assertEqual(unknown.status_code, 403)

    def test_auth_failures(self):
        client = _client()
        self.assertEqual(_create(client, None).status_code, 401)
        self.assertEqual(_create(client, 'bogus-token').status_code, 401)
        listed = client.get('/api/v1/admin/drafts', headers=_auth(None))
        self.assertEqual(listed.status_code, 401)
        unconfigured = _client(role_tokens={})
        self.assertEqual(_create(unconfigured, 'editor-token').status_code,
                         503)

    def test_not_found_and_list(self):
        client = _client()
        self.assertEqual(
            client.get('/api/v1/admin/drafts/D-99',
                       headers=_auth('editor-token')).status_code, 404)
        self.assertEqual(
            _act(client, 'editor-token', 'D-99', 'submit').status_code, 404)
        _create(client, 'editor-token', title='First')
        _create(client, 'reviewer-token', title='Second')
        listed = client.get('/api/v1/admin/drafts',
                            headers=_auth('user-token'))
        self.assertEqual(listed.status_code, 200)
        # Reads need a valid role token but no write operation: even
        # the read-only user role may list.
        self.assertEqual([d['title'] for d in listed.json()['drafts']],
                         ['First', 'Second'])

    def test_audit_covers_every_attempt_without_content_leakage(self):
        client = _client()
        secret_title = 'Secret draft title 7f3a'
        secret_body = 'Secret draft body 9c21'
        draft_id = _create(client, 'editor-token', title=secret_title,
                           body=secret_body).json()['draft']['id']
        _act(client, 'editor-token', draft_id, 'submit')
        _act(client, 'user-token', draft_id, 'approve')  # denied
        _act(client, 'publisher-token', draft_id, 'publish')  # 422
        entries = _audit(client)
        whats = [(e['what'], e['outcome']) for e in entries]
        self.assertEqual(whats, [
            ('draft:create', 'allowed'),
            (f'draft:submit:{draft_id}', 'allowed'),
            (f'draft:approve:{draft_id}', 'denied'),
            (f'draft:publish:{draft_id}', 'denied'),
        ])
        # No draft content anywhere in the audit trail.
        blob = str(entries)
        self.assertNotIn(secret_title, blob)
        self.assertNotIn(secret_body, blob)
        # Exactly one record per attempt (no double-recording).
        self.assertEqual(len(entries), 4)


if __name__ == '__main__':
    unittest.main()
