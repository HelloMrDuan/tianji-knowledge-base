"""B020: draft approval state machine + action-to-role mapping (TJ-026.4
batch 2: draft storage, approval flow, no persistence, no rollback).

Runs in public CI (validate.yml). Imports only tianji_kb.admin_drafts
and tianji_kb.admin_roles (pure stdlib): no FastAPI stack, no private
Canonical/RAG data required. HTTP-level verification (real status codes
end to end, role matrix over endpoints, audit entries, no content
leakage) lives in test_b020_drafts_http.py (offline acceptance only,
NOT public CI).

Batch 2 scope reminder: draft storage (process memory) + state machine
+ draft/approve/publish endpoints ONLY. No durable storage, no
rollback, no version snapshots — those are later batches and must not
appear here. Rejected drafts are terminal: the specified machine has
no rejected -> draft edge, and this test pins that fail-closed choice.
"""

import unittest

from tianji_kb.admin_drafts import (
    DRAFT_ACTION_OPERATION,
    DRAFT_STATUSES,
    DraftNotFoundError,
    DraftStore,
    InvalidDraftInputError,
    InvalidTransitionError,
    STORAGE_NOTE,
)
from tianji_kb.admin_roles import resolve_role_access

ROLE_TOKENS = {
    'user-token': 'user',
    'editor-token': 'editor',
    'reviewer-token': 'reviewer',
    'publisher-token': 'publisher',
}


def _draft(store, role='editor'):
    return store.create('Test draft', 'Test body', role)


class TestB020DraftConstants(unittest.TestCase):
    def test_statuses(self):
        self.assertEqual(
            DRAFT_STATUSES,
            {'draft', 'submitted', 'approved', 'rejected', 'published'})

    def test_action_operation_mapping(self):
        # The mapping is the contract between the draft flow and the
        # batch-1 role matrix; changing it changes who may do what.
        self.assertEqual(DRAFT_ACTION_OPERATION, {
            'create': 'draft',
            'edit': 'draft',
            'submit': 'draft',
            'approve': 'approve',
            'reject': 'approve',
            'publish': 'publish',
        })

    def test_storage_note_declares_restart_loss(self):
        self.assertIn('进程内存', STORAGE_NOTE)
        self.assertIn('重启', STORAGE_NOTE)


class TestB020StateMachine(unittest.TestCase):
    def test_happy_path_create_submit_approve_publish(self):
        store = DraftStore()
        draft = _draft(store)
        self.assertEqual(draft['status'], 'draft')
        self.assertEqual(draft['id'], 'D-1')
        draft = store.transition('D-1', 'submit', 'editor')
        self.assertEqual(draft['status'], 'submitted')
        draft = store.transition('D-1', 'approve', 'reviewer')
        self.assertEqual(draft['status'], 'approved')
        draft = store.transition('D-1', 'publish', 'publisher')
        self.assertEqual(draft['status'], 'published')

    def test_reject_branch(self):
        store = DraftStore()
        _draft(store)
        store.transition('D-1', 'submit', 'editor')
        draft = store.transition('D-1', 'reject', 'reviewer')
        self.assertEqual(draft['status'], 'rejected')

    def test_illegal_transitions_fail_closed_and_preserve_state(self):
        store = DraftStore()
        _draft(store)
        illegal = [
            # (setup actions, illegal action)
            ([], 'approve'),
            ([], 'reject'),
            ([], 'publish'),
            (['submit'], 'submit'),
            (['submit'], 'publish'),
            (['submit', 'approve'], 'approve'),
            (['submit', 'approve'], 'reject'),
            (['submit', 'approve'], 'submit'),
            (['submit', 'approve', 'publish'], 'publish'),
            (['submit', 'approve', 'publish'], 'submit'),
            (['submit', 'reject'], 'publish'),
            (['submit', 'reject'], 'submit'),
            (['submit', 'reject'], 'approve'),
        ]
        for setup, action in illegal:
            probe = DraftStore()
            _draft(probe)
            for step in setup:
                probe.transition('D-1', step, 'editor' if step == 'submit' else 'reviewer' if step in ('approve', 'reject') else 'publisher')
            before = probe.get('D-1')
            with self.assertRaises(InvalidTransitionError):
                probe.transition('D-1', action, 'publisher')
            # Fail-closed: the stored record is untouched.
            self.assertEqual(probe.get('D-1'), before)
        # Unknown actions and unknown ids are equally fail-closed.
        with self.assertRaises(InvalidTransitionError):
            store.transition('D-1', 'rollback', 'publisher')
        with self.assertRaises(InvalidTransitionError):
            store.transition('D-1', 'delete', 'publisher')
        with self.assertRaises(DraftNotFoundError):
            store.transition('D-99', 'submit', 'editor')

    def test_edit_only_in_draft_status(self):
        store = DraftStore()
        _draft(store)
        edited = store.edit('D-1', title='New title')
        self.assertEqual(edited['title'], 'New title')
        self.assertEqual(edited['body'], 'Test body')
        self.assertEqual(edited['status'], 'draft')
        store.transition('D-1', 'submit', 'editor')
        with self.assertRaises(InvalidTransitionError):
            store.edit('D-1', title='Too late')
        self.assertEqual(store.get('D-1')['title'], 'New title')
        with self.assertRaises(DraftNotFoundError):
            store.edit('D-99', title='Ghost')

    def test_edit_rejects_blank_values(self):
        store = DraftStore()
        _draft(store)
        # Blank values are rejected; valid partial edits pass. (An
        # edit with both fields omitted is rejected at the endpoint
        # layer, not here.)
        with self.assertRaises(InvalidDraftInputError):
            store.edit('D-1', title='   ')
        with self.assertRaises(InvalidDraftInputError):
            store.edit('D-1', body='')
        edited = store.edit('D-1', body='New body')
        self.assertEqual(edited['body'], 'New body')

    def test_create_validation(self):
        store = DraftStore()
        with self.assertRaises(InvalidDraftInputError):
            store.create('', 'body', 'editor')
        with self.assertRaises(InvalidDraftInputError):
            store.create('title', '   ', 'editor')
        with self.assertRaises(InvalidDraftInputError):
            store.create(None, 'body', 'editor')
        with self.assertRaises(InvalidDraftInputError):
            store.create('title', 42, 'editor')
        self.assertEqual(len(store), 0)

    def test_transition_log_is_the_approval_history(self):
        store = DraftStore()
        _draft(store, role='editor')
        store.transition('D-1', 'submit', 'editor')
        store.transition('D-1', 'approve', 'reviewer')
        draft = store.transition('D-1', 'publish', 'publisher')
        actions = [(t['action'], t['role']) for t in draft['transitions']]
        self.assertEqual(actions, [
            ('create', 'editor'),
            ('submit', 'editor'),
            ('approve', 'reviewer'),
            ('publish', 'publisher'),
        ])
        # No version snapshots: the log carries actions, never bodies.
        for entry in draft['transitions']:
            self.assertNotIn('body', entry)
            self.assertNotIn('title', entry)

    def test_store_isolation_via_deep_copies(self):
        store = DraftStore()
        draft = _draft(store)
        draft['title'] = 'Mutated outside'
        draft['transitions'].append({'action': 'fake', 'role': 'x', 'at': 'x'})
        stored = store.get('D-1')
        self.assertEqual(stored['title'], 'Test draft')
        self.assertEqual(len(stored['transitions']), 1)
        listed = store.list()
        listed[0]['status'] = 'published'
        self.assertEqual(store.get('D-1')['status'], 'draft')
        self.assertEqual(len(store), 1)
        ids = [store.create(f'T{i}', 'b', 'editor')['id'] for i in range(3)]
        self.assertEqual(ids, ['D-2', 'D-3', 'D-4'])
        self.assertEqual([d['id'] for d in store.list()],
                         ['D-1', 'D-2', 'D-3', 'D-4'])


class TestB020DraftRoleMatrix(unittest.TestCase):
    def test_each_action_maps_to_batch1_role_sets(self):
        # user: nothing. editor: draft ops only. reviewer: draft +
        # approve. publisher: everything. (Matrix itself is batch 1;
        # here it is pinned through the batch-2 action mapping.)
        cases = {
            'user': {'create': False, 'edit': False, 'submit': False,
                     'approve': False, 'reject': False, 'publish': False},
            'editor': {'create': True, 'edit': True, 'submit': True,
                       'approve': False, 'reject': False, 'publish': False},
            'reviewer': {'create': True, 'edit': True, 'submit': True,
                         'approve': True, 'reject': True, 'publish': False},
            'publisher': {'create': True, 'edit': True, 'submit': True,
                          'approve': True, 'reject': True, 'publish': True},
        }
        for role, expected in cases.items():
            token = f'{role}-token'
            for action, allowed in expected.items():
                operation = DRAFT_ACTION_OPERATION[action]
                outcome, _ = resolve_role_access(
                    ROLE_TOKENS, f'Bearer {token}', operation)
                self.assertEqual(
                    outcome == 'ok', allowed,
                    f'{role} {action} ({operation}) should be '
                    f'{"allowed" if allowed else "denied"}')

    def test_unknown_operation_is_forbidden(self):
        # B022 note: batch 2 used 'rollback' here as the unknown
        # example, but batch 3 legitimately made 'rollback' a known
        # publisher-only operation — so the example moves to a
        # genuinely unknown operation. The assertion is unchanged:
        # unknown operations stay forbidden (fail-closed).
        outcome, _ = resolve_role_access(
            ROLE_TOKENS, 'Bearer publisher-token', 'bogus')
        self.assertEqual(outcome, 'forbidden')


if __name__ == '__main__':
    unittest.main()
