"""B022: draft version snapshots + rollback (TJ-026.4 batch 3).

Runs in public CI (validate.yml). Imports only tianji_kb.admin_drafts,
tianji_kb.admin_roles, and tianji_kb.admin_audit (pure stdlib): no
FastAPI stack, no private Canonical/RAG data required. HTTP-level
verification (real status codes end to end, role matrix over
endpoints, compensating audit entries, no content leakage) lives in
test_b022_rollback_http.py (offline acceptance only, NOT public CI).

Batch 3 scope reminder: version snapshots on every mutation +
publisher-only rollback (draft-internal version history, scheme A).
No durable storage, no standalone published-content registry (scheme
B, a later task). Rollback lands in 'draft' status; rejected stays
terminal. Rollback never rewrites history: it appends a transition, a
snapshot, and (at the API layer) a compensating audit record.
"""

import unittest

from tianji_kb.admin_audit import AuditLog
from tianji_kb.admin_drafts import (
    DRAFT_ACTION_OPERATION,
    DraftNotFoundError,
    DraftStore,
    InvalidTransitionError,
)
from tianji_kb.admin_roles import WRITE_OPERATIONS, resolve_role_access

ROLE_TOKENS = {
    'user-token': 'user',
    'editor-token': 'editor',
    'reviewer-token': 'reviewer',
    'publisher-token': 'publisher',
}


def _published(store):
    """Create -> edit -> submit -> approve -> publish; return record."""
    draft = store.create('v1 title', 'v1 body', 'editor')
    store.edit(draft['id'], title='v2 title', role='editor')
    store.transition(draft['id'], 'submit', 'editor')
    store.transition(draft['id'], 'approve', 'reviewer')
    store.transition(draft['id'], 'publish', 'publisher')
    return store.get(draft['id'])


class TestB022RollbackOperation(unittest.TestCase):
    def test_rollback_operation_is_publisher_only(self):
        self.assertEqual(WRITE_OPERATIONS['rollback'], {'publisher'})

    def test_rollback_role_matrix(self):
        for token, role in ROLE_TOKENS.items():
            outcome, _ = resolve_role_access(
                ROLE_TOKENS, f'Bearer {token}', 'rollback')
            if role == 'publisher':
                self.assertEqual(outcome, 'ok')
            else:
                self.assertEqual(outcome, 'forbidden')

    def test_rollback_not_routed_through_generic_action_map(self):
        # Rollback has a dedicated endpoint carrying the version body;
        # the generic /{action} route must never capture it.
        self.assertNotIn('rollback', DRAFT_ACTION_OPERATION)


class TestB022VersionSnapshots(unittest.TestCase):
    def test_every_mutation_appends_one_snapshot(self):
        store = DraftStore()
        draft = store.create('v1 title', 'v1 body', 'editor')
        self.assertEqual(
            [(v['version'], v['action']) for v in draft['versions']],
            [(1, 'create')])
        store.edit(draft['id'], title='v2 title', role='editor')
        store.transition(draft['id'], 'submit', 'editor')
        store.transition(draft['id'], 'approve', 'reviewer')
        store.transition(draft['id'], 'publish', 'publisher')
        got = store.get(draft['id'])
        self.assertEqual(
            [(v['version'], v['action']) for v in got['versions']],
            [(1, 'create'), (2, 'edit'), (3, 'submit'),
             (4, 'approve'), (5, 'publish')])
        # Each snapshot carries the content as of its mutation.
        self.assertEqual(got['versions'][1]['title'], 'v2 title')
        self.assertEqual(got['versions'][4]['title'], 'v2 title')
        self.assertEqual(got['versions'][0]['title'], 'v1 title')

    def test_edit_snapshot_records_the_editing_role(self):
        store = DraftStore()
        draft = store.create('t', 'b', 'editor')
        store.edit(draft['id'], body='b2', role='reviewer')
        got = store.get(draft['id'])
        self.assertEqual(got['versions'][1]['role'], 'reviewer')
        self.assertEqual(got['versions'][1]['action'], 'edit')

    def test_snapshots_are_immutable_via_deep_copies(self):
        store = DraftStore()
        draft = store.create('v1 title', 'v1 body', 'editor')
        store.edit(draft['id'], title='v2 title', role='editor')
        hacked = store.get(draft['id'])
        hacked['versions'][0]['title'] = 'HACKED'
        hacked['versions'][0]['body'] = 'HACKED'
        hacked['title'] = 'HACKED'
        again = store.get(draft['id'])
        self.assertEqual(again['versions'][0]['title'], 'v1 title')
        self.assertEqual(again['versions'][0]['body'], 'v1 body')
        self.assertEqual(again['title'], 'v2 title')

    def test_created_record_cannot_mutate_the_store(self):
        store = DraftStore()
        created = store.create('v1 title', 'v1 body', 'editor')
        created['versions'].append({'version': 99, 'title': 'X',
                                    'body': 'X', 'action': 'fake',
                                    'role': 'fake', 'at': 'now'})
        self.assertEqual(len(store.get(created['id'])['versions']), 1)


class TestB022RollbackBehavior(unittest.TestCase):
    def test_rollback_restores_snapshot_and_lands_in_draft(self):
        store = DraftStore()
        published = _published(store)
        rolled = store.rollback(published['id'], 1, 'publisher')
        self.assertEqual(rolled['status'], 'draft')
        self.assertEqual(rolled['title'], 'v1 title')
        self.assertEqual(rolled['body'], 'v1 body')
        # Rollback appends a transition carrying the restored version.
        self.assertEqual(
            rolled['transitions'][-1]['action'], 'rollback')
        self.assertEqual(
            rolled['transitions'][-1]['version'], 1)
        self.assertEqual(
            rolled['transitions'][-1]['role'], 'publisher')
        # Rollback appends a snapshot of the restored content.
        self.assertEqual(
            [(v['version'], v['action'])
             for v in rolled['versions']][-1], (6, 'rollback'))
        self.assertEqual(rolled['versions'][-1]['title'], 'v1 title')
        self.assertEqual(rolled['versions'][-1]['body'], 'v1 body')

    def test_rollback_from_published_is_legal(self):
        store = DraftStore()
        published = _published(store)
        self.assertEqual(published['status'], 'published')
        rolled = store.rollback(published['id'], 1, 'publisher')
        self.assertEqual(rolled['status'], 'draft')

    def test_rollback_from_draft_submitted_approved_is_legal(self):
        store = DraftStore()
        draft = store.create('v1 title', 'v1 body', 'editor')
        store.edit(draft['id'], title='v2 title', role='editor')
        self.assertEqual(
            store.rollback(draft['id'], 1, 'publisher')['status'], 'draft')
        store.transition(draft['id'], 'submit', 'editor')
        self.assertEqual(
            store.rollback(draft['id'], 1, 'publisher')['status'], 'draft')
        store.transition(draft['id'], 'submit', 'editor')
        store.transition(draft['id'], 'approve', 'reviewer')
        self.assertEqual(
            store.rollback(draft['id'], 1, 'publisher')['status'], 'draft')

    def test_rollback_after_rollback_can_republish(self):
        # Reverted content goes through review again: the full flow
        # still works from the rolled-back draft state.
        store = DraftStore()
        published = _published(store)
        store.rollback(published['id'], 1, 'publisher')
        store.transition(published['id'], 'submit', 'editor')
        store.transition(published['id'], 'approve', 'reviewer')
        republished = store.transition(
            published['id'], 'publish', 'publisher')
        self.assertEqual(republished['status'], 'published')
        self.assertEqual(republished['title'], 'v1 title')

    def test_rollback_never_rewrites_prior_history(self):
        store = DraftStore()
        published = _published(store)
        before = store.get(published['id'])
        rolled = store.rollback(published['id'], 1, 'publisher')
        self.assertEqual(
            rolled['transitions'][:-1], before['transitions'])
        self.assertEqual(
            rolled['versions'][:-1], before['versions'])

    def test_rollback_rejected_fails_closed_and_preserves_state(self):
        store = DraftStore()
        draft = store.create('v1 title', 'v1 body', 'editor')
        store.transition(draft['id'], 'submit', 'editor')
        store.transition(draft['id'], 'reject', 'reviewer')
        before = store.get(draft['id'])
        with self.assertRaises(InvalidTransitionError):
            store.rollback(draft['id'], 1, 'publisher')
        self.assertEqual(store.get(draft['id']), before)

    def test_rollback_unknown_version_fails_closed(self):
        store = DraftStore()
        published = _published(store)
        before = store.get(published['id'])
        with self.assertRaises(InvalidTransitionError):
            store.rollback(published['id'], 99, 'publisher')
        self.assertEqual(store.get(published['id']), before)

    def test_rollback_unknown_draft_fails_closed(self):
        store = DraftStore()
        with self.assertRaises(DraftNotFoundError):
            store.rollback('D-999', 1, 'publisher')


class TestB022AuditAppendOnly(unittest.TestCase):
    def test_compensating_record_only_appends(self):
        # The API layer appends one compensating record per rollback;
        # the log itself exposes no update/delete, and earlier entries
        # are byte-identical after the append.
        log = AuditLog()
        log.record('editor', 'draft:create', 'allowed', 'D-1')
        log.record('publisher', 'draft:publish:D-1', 'allowed', 'D-1')
        before = log.entries()
        log.record('publisher', 'draft:rollback:D-1', 'allowed',
                   'version:1')
        after = log.entries()
        self.assertEqual(after[:-1], before)
        self.assertEqual(len(after), len(before) + 1)
        self.assertEqual(after[-1]['what'], 'draft:rollback:D-1')
        self.assertEqual(after[-1]['detail'], 'version:1')
        # Returned entries are copies: mutating them never rewrites
        # the log.
        after[0]['what'] = 'HACKED'
        self.assertEqual(log.entries()[0]['what'], 'draft:create')
        self.assertFalse(hasattr(log, 'update'))
        self.assertFalse(hasattr(log, 'delete'))


if __name__ == '__main__':
    unittest.main()
