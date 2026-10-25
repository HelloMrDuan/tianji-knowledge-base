"""TJ-026.5 SQLite admin storage tests (pure stdlib).

Covers the durable store that replaces process memory for the
TJ-026.4 admin surface: audit entries, drafts, version snapshots,
transition records, and the D-{N} id sequence, all in one SQLite
file. No FastAPI stack and no private knowledge data are required,
so this file runs in public CI.

Restart is simulated by constructing a second store instance over
the same file: nothing is shared in memory between the two, so any
data the second instance reads must have come from disk.
"""

import os
import re
import tempfile
import unittest

from tianji_kb.admin_audit import AuditLog
from tianji_kb.admin_drafts import (
    DraftNotFoundError,
    DraftStore,
    InvalidDraftInputError,
    InvalidTransitionError,
)
from tianji_kb.admin_storage import (
    SQLITE_STORAGE_NOTE,
    SqliteAuditLog,
    SqliteDraftStore,
)


def _strip_times(value):
    """Normalize ISO timestamps so memory/SQLite records compare equal."""
    if isinstance(value, dict):
        return {k: ('<time>' if k in ('at', 'created_at', 'updated_at', 'when') else _strip_times(v))
                for k, v in value.items()}
    if isinstance(value, list):
        return [_strip_times(v) for v in value]
    return value


class StorageTestCase(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.db = os.path.join(self._tmp.name, 'admin.db')

    def tearDown(self):
        self._tmp.cleanup()

    def test_audit_survives_restart_in_order(self):
        first = SqliteAuditLog(self.db)
        first.record('editor', 'draft:create', 'allowed', 'D-1')
        first.record('unknown', 'draft:publish', 'denied', 'forbidden')
        second = SqliteAuditLog(self.db)
        entries = second.entries()
        self.assertEqual(len(entries), 2)
        self.assertEqual(entries[0]['who'], 'editor')
        self.assertEqual(entries[0]['what'], 'draft:create')
        self.assertEqual(entries[0]['outcome'], 'allowed')
        self.assertEqual(entries[0]['detail'], 'D-1')
        self.assertEqual(entries[1]['outcome'], 'denied')
        self.assertEqual(len(second), 2)

    def test_audit_rejects_bad_outcome_fail_closed(self):
        log = SqliteAuditLog(self.db)
        with self.assertRaises(ValueError):
            log.record('editor', 'draft:create', 'maybe', None)
        self.assertEqual(len(log), 0)
        self.assertEqual(SqliteAuditLog(self.db).entries(), [])

    def test_audit_has_no_update_or_delete_paths(self):
        """Append-only is structural, not a convention: the module
        source must contain no UPDATE/DELETE statement against
        audit_entries (draft current-state UPDATEs are separate and
        allowed — history lives in append-only tables, never there)."""
        path = os.path.join(os.path.dirname(__file__), '..', 'src',
                            'tianji_kb', 'admin_storage.py')
        with open(path) as f:
            source = f.read()
        self.assertNotIn('UPDATE audit_entries', source)
        self.assertNotIn('DELETE FROM audit_entries', source)
        self.assertNotIn('UPDATE draft_versions', source)
        self.assertNotIn('DELETE FROM draft_versions', source)
        self.assertNotIn('UPDATE draft_transitions', source)
        self.assertNotIn('DELETE FROM draft_transitions', source)

    def test_draft_full_flow_survives_restart(self):
        first = SqliteDraftStore(self.db)
        draft = first.create('Title', 'Body', 'editor')
        first.edit(draft['id'], body='Body v2', role='editor')
        first.transition(draft['id'], 'submit', 'editor')
        first.transition(draft['id'], 'approve', 'reviewer')
        first.transition(draft['id'], 'publish', 'publisher')
        second = SqliteDraftStore(self.db)
        restored = second.get(draft['id'])
        self.assertEqual(restored['status'], 'published')
        self.assertEqual(restored['title'], 'Title')
        self.assertEqual(restored['body'], 'Body v2')
        self.assertEqual([t['action'] for t in restored['transitions']],
                         ['create', 'submit', 'approve', 'publish'])
        self.assertEqual([v['version'] for v in restored['versions']],
                         [1, 2, 3, 4, 5])
        self.assertEqual(second.list()[0]['id'], draft['id'])
        self.assertEqual(len(second), 1)

    def test_id_sequence_never_repeats_after_restart(self):
        first = SqliteDraftStore(self.db)
        self.assertEqual(first.create('A', 'a', 'editor')['id'], 'D-1')
        self.assertEqual(first.create('B', 'b', 'editor')['id'], 'D-2')
        second = SqliteDraftStore(self.db)
        self.assertEqual(second.create('C', 'c', 'editor')['id'], 'D-3')
        third = SqliteDraftStore(self.db)
        self.assertEqual([d['id'] for d in third.list()], ['D-1', 'D-2', 'D-3'])

    def test_rollback_snapshot_survives_restart(self):
        first = SqliteDraftStore(self.db)
        draft = first.create('V1 title', 'V1 body', 'editor')
        first.edit(draft['id'], title='V2 title', body='V2 body', role='editor')
        first.transition(draft['id'], 'submit', 'editor')
        first.transition(draft['id'], 'approve', 'reviewer')
        first.transition(draft['id'], 'publish', 'publisher')
        before = first.get(draft['id'])
        second = SqliteDraftStore(self.db)
        rolled = second.rollback(draft['id'], 1, 'publisher')
        self.assertEqual(rolled['title'], 'V1 title')
        self.assertEqual(rolled['body'], 'V1 body')
        self.assertEqual(rolled['status'], 'draft')
        # Old snapshots and transitions are untouched; rollback only appends.
        self.assertEqual(rolled['versions'][:5], before['versions'])
        self.assertEqual(rolled['transitions'][:4], before['transitions'])
        self.assertEqual(rolled['transitions'][4]['action'], 'rollback')
        self.assertEqual(rolled['transitions'][4]['version'], 1)
        self.assertEqual(rolled['versions'][5]['action'], 'rollback')
        self.assertEqual(rolled['versions'][5]['title'], 'V1 title')
        # And the rollback itself survives a second restart.
        third = SqliteDraftStore(self.db)
        self.assertEqual(third.get(draft['id'])['status'], 'draft')
        self.assertEqual(third.get(draft['id'])['title'], 'V1 title')

    def test_rejected_terminal_survives_restart(self):
        first = SqliteDraftStore(self.db)
        draft = first.create('T', 'b', 'editor')
        first.transition(draft['id'], 'submit', 'editor')
        first.transition(draft['id'], 'reject', 'reviewer')
        second = SqliteDraftStore(self.db)
        with self.assertRaises(InvalidTransitionError):
            second.rollback(draft['id'], 1, 'publisher')
        with self.assertRaises(InvalidTransitionError):
            second.edit(draft['id'], title='Nope', role='editor')
        with self.assertRaises(InvalidTransitionError):
            second.transition(draft['id'], 'approve', 'reviewer')
        self.assertEqual(second.get(draft['id'])['status'], 'rejected')

    def test_unknown_ids_and_versions_fail_closed(self):
        store = SqliteDraftStore(self.db)
        # get() returns None for unknown ids (same as memory store);
        # mutations raise DraftNotFoundError (fail-closed).
        self.assertIsNone(store.get('D-404'))
        with self.assertRaises(DraftNotFoundError):
            store.edit('D-404', title='Nope', role='editor')
        with self.assertRaises(DraftNotFoundError):
            store.transition('D-404', 'submit', 'editor')
        with self.assertRaises(DraftNotFoundError):
            store.rollback('D-404', 1, 'publisher')
        draft = store.create('T', 'b', 'editor')
        with self.assertRaises(InvalidTransitionError):
            store.rollback(draft['id'], 99, 'publisher')
        with self.assertRaises(InvalidTransitionError):
            store.transition(draft['id'], 'publish', 'publisher')
        with self.assertRaises(InvalidDraftInputError):
            store.edit(draft['id'], title='   ', role='editor')
        self.assertEqual(store.get(draft['id'])['versions'][0]['title'], 'T')

    def test_denied_attempts_audited_across_restart(self):
        first = SqliteAuditLog(self.db)
        first.record('unknown', 'draft:publish', 'denied', 'not_configured')
        first.record('user', 'draft:publish', 'denied', 'forbidden')
        second = SqliteAuditLog(self.db)
        self.assertEqual([e['what'] for e in second.entries()],
                         ['draft:publish', 'draft:publish'])
        self.assertEqual([e['outcome'] for e in second.entries()],
                         ['denied', 'denied'])

    def test_interface_parity_with_memory_store(self):
        """Same scripted sequence on memory and SQLite stores must
        produce equal records (timestamps normalized: they differ by
        wall-clock time, not by behavior)."""
        def run(store):
            d = store.create('Title', 'Body', 'editor')
            store.edit(d['id'], body='Body v2', role='editor')
            store.transition(d['id'], 'submit', 'editor')
            store.transition(d['id'], 'approve', 'reviewer')
            store.transition(d['id'], 'publish', 'publisher')
            store.rollback(d['id'], 1, 'publisher')
            return store.get(d['id'])
        mem = _strip_times(run(DraftStore()))
        sql = _strip_times(run(SqliteDraftStore(self.db)))
        self.assertEqual(mem, sql)

    def test_audit_interface_parity_with_memory_log(self):
        mem = AuditLog()
        mem.record('editor', 'draft:create', 'allowed', 'D-1')
        mem.record('user', 'draft:publish', 'denied', 'forbidden')
        sql = SqliteAuditLog(self.db)
        sql.record('editor', 'draft:create', 'allowed', 'D-1')
        sql.record('user', 'draft:publish', 'denied', 'forbidden')
        self.assertEqual(_strip_times(mem.entries()),
                         _strip_times(sql.entries()))
        self.assertEqual(len(mem), len(sql))

    def test_empty_db_starts_clean(self):
        self.assertEqual(SqliteAuditLog(self.db).entries(), [])
        self.assertEqual(SqliteDraftStore(self.db).list(), [])
        self.assertEqual(len(SqliteDraftStore(self.db)), 0)

    def test_storage_note_reports_sqlite(self):
        self.assertEqual(SqliteDraftStore.storage, 'sqlite')
        self.assertEqual(SqliteDraftStore.storage_note, SQLITE_STORAGE_NOTE)
        self.assertIn('SQLite', SQLITE_STORAGE_NOTE)
        self.assertNotIn('进程内存', SQLITE_STORAGE_NOTE)


if __name__ == '__main__':
    unittest.main()
