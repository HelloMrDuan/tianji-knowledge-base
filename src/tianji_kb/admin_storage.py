"""SQLite-backed admin storage (TJ-026.5).

Single-file durable storage for the TJ-026.4 admin surface: audit
entries, drafts, version snapshots, and transition records live in
one SQLite file (stdlib sqlite3, zero new dependencies). The classes
here keep the exact interface of the in-memory AuditLog/DraftStore,
so the API layer, role gating, state machine, and rollback logic
need no changes; only the construction site (create_app) switches
which implementation backs app.state.

Tables (one file, created on first open):
  audit_entries     — append-only: this module contains INSERT and
                       SELECT statements for it and no UPDATE or
                       DELETE statement, so history cannot be
                       rewritten through this store. Columns: seq
                       (AUTOINCREMENT order), who, when_iso, what,
                       outcome, detail.
  draft_id_seq      — AUTOINCREMENT sequence source for D-{N} ids.
                       One row is inserted per draft creation and
                       its rowid is the draft number. AUTOINCREMENT
                       never reuses rowids, so ids never repeat,
                       even after restart.
  drafts            — current draft state: id, seq (creation order),
                       title, body, author_role, status, created_at,
                       updated_at. The current row is mutable through
                       edit/transition/rollback exactly as the
                       in-memory store allows; history lives in the
                       append-only tables below, never here.
  draft_versions    — immutable snapshots: draft_id, version, title,
                       body, action, role, at. Append-only.
  draft_transitions — transition records: draft_id, action, role, at,
                       version (NULL except rollback). Append-only.

Timestamps are ISO strings generated in Python (same format as the
in-memory stores), stored as TEXT; SQLite date functions are not
used, so record shapes are identical across implementations.

Concurrency: app.state stores are shared across requests and FastAPI
runs sync endpoints in a threadpool, so each store serializes its
own connection with a lock and opens it with check_same_thread=False
plus a 30s busy timeout. Admin traffic is low volume; the lock is
not a bottleneck.

Backup is copying the file. Honest caveat: the file lives on the app
machine's disk — it survives restarts, but a container redeploy
without a mounted persistent volume may still lose it; the deploy
volume is a separate decision, not something this module solves.

This module is pure stdlib so it can be tested in public CI without
the FastAPI stack or private knowledge data.
"""

import copy
import os
import sqlite3
import threading
from datetime import datetime, timezone

from .admin_audit import AUDIT_OUTCOMES
from .admin_drafts import (
    DraftNotFoundError,
    InvalidTransitionError,
    _TRANSITIONS,
    _validate_text,
)

SQLITE_STORAGE_NOTE = ('草稿保存在 SQLite 单文件中，服务重启后不丢失；'
                       '备份为拷贝该文件。')

DEFAULT_DB_PATH = 'tianji_admin.db'

_SCHEMA = """
CREATE TABLE IF NOT EXISTS audit_entries (
    seq INTEGER PRIMARY KEY AUTOINCREMENT,
    who TEXT NOT NULL,
    when_iso TEXT NOT NULL,
    what TEXT NOT NULL,
    outcome TEXT NOT NULL,
    detail TEXT
);
CREATE TABLE IF NOT EXISTS draft_id_seq (
    seq INTEGER PRIMARY KEY AUTOINCREMENT
);
CREATE TABLE IF NOT EXISTS drafts (
    id TEXT PRIMARY KEY,
    seq INTEGER NOT NULL,
    title TEXT NOT NULL,
    body TEXT NOT NULL,
    author_role TEXT NOT NULL,
    status TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS draft_versions (
    draft_id TEXT NOT NULL,
    version INTEGER NOT NULL,
    title TEXT NOT NULL,
    body TEXT NOT NULL,
    action TEXT NOT NULL,
    role TEXT NOT NULL,
    at TEXT NOT NULL,
    PRIMARY KEY (draft_id, version)
);
CREATE TABLE IF NOT EXISTS draft_transitions (
    seq INTEGER PRIMARY KEY AUTOINCREMENT,
    draft_id TEXT NOT NULL,
    action TEXT NOT NULL,
    role TEXT NOT NULL,
    at TEXT NOT NULL,
    version INTEGER
);
"""


def _now():
    return datetime.now(timezone.utc).isoformat()


def _connect(path):
    """Open the SQLite file, creating parent dirs and tables."""
    parent = os.path.dirname(os.path.abspath(path))
    os.makedirs(parent, exist_ok=True)
    conn = sqlite3.connect(path, timeout=30.0, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.executescript(_SCHEMA)
    conn.commit()
    return conn


class SqliteAuditLog:
    """SQLite-backed append-only audit log. Same interface as AuditLog.

    Only INSERT and SELECT statements exist in this class for
    audit_entries: there is no code path that updates or deletes an
    audit row, so history cannot be rewritten through this store.
    """

    storage = 'sqlite'

    def __init__(self, path):
        self._path = path
        self._conn = _connect(path)
        self._lock = threading.Lock()

    def record(self, who, what, outcome, detail=None):
        """Append one record and return it. `outcome` must be
        'allowed' or 'denied'; anything else is rejected (fail-closed)
        so no ambiguous record can enter the log."""
        if outcome not in AUDIT_OUTCOMES:
            raise ValueError(f'unknown audit outcome: {outcome!r}')
        entry = {
            'who': who,
            'when': _now(),
            'what': what,
            'outcome': outcome,
            'detail': detail,
        }
        with self._lock, self._conn:
            self._conn.execute(
                'INSERT INTO audit_entries (who, when_iso, what, outcome, detail)'
                ' VALUES (?, ?, ?, ?, ?)',
                (who, entry['when'], what, outcome, detail))
        return copy.deepcopy(entry)

    def entries(self):
        """Return all records, oldest first."""
        with self._lock, self._conn:
            rows = self._conn.execute(
                'SELECT who, when_iso, what, outcome, detail'
                ' FROM audit_entries ORDER BY seq ASC').fetchall()
        return [{'who': r['who'], 'when': r['when_iso'], 'what': r['what'],
                 'outcome': r['outcome'], 'detail': r['detail']}
                for r in rows]

    def __len__(self):
        with self._lock, self._conn:
            return self._conn.execute(
                'SELECT COUNT(*) FROM audit_entries').fetchone()[0]


class SqliteDraftStore:
    """SQLite-backed draft store. Same interface as DraftStore.

    State machine, role-operation mapping, and rollback rules are
    identical to the in-memory store: fail-closed transitions,
    publisher-only rollback, rejected terminal, and append-only
    versions/transitions. Only the persistence changes: every
    mutation commits to the SQLite file, so records survive restart.
    """

    storage = 'sqlite'
    storage_note = SQLITE_STORAGE_NOTE

    def __init__(self, path):
        self._path = path
        self._conn = _connect(path)
        self._lock = threading.Lock()

    def _record_for_row(self, row):
        """Rebuild a full draft record dict from a drafts row.

        Shapes match the in-memory store exactly: transitions carry
        a 'version' key only for rollback; versions carry
        {version, title, body, action, role, at}.
        """
        draft_id = row['id']
        version_rows = self._conn.execute(
            'SELECT version, title, body, action, role, at'
            ' FROM draft_versions WHERE draft_id = ? ORDER BY version ASC',
            (draft_id,)).fetchall()
        transition_rows = self._conn.execute(
            'SELECT action, role, at, version'
            ' FROM draft_transitions WHERE draft_id = ? ORDER BY seq ASC',
            (draft_id,)).fetchall()
        transitions = []
        for t in transition_rows:
            item = {'action': t['action'], 'role': t['role'], 'at': t['at']}
            if t['version'] is not None:
                item['version'] = t['version']
            transitions.append(item)
        return {
            'id': draft_id,
            'title': row['title'],
            'body': row['body'],
            'author_role': row['author_role'],
            'status': row['status'],
            'created_at': row['created_at'],
            'updated_at': row['updated_at'],
            'transitions': transitions,
            'versions': [{'version': v['version'], 'title': v['title'],
                          'body': v['body'], 'action': v['action'],
                          'role': v['role'], 'at': v['at']}
                         for v in version_rows],
        }

    def _get_row(self, draft_id):
        return self._conn.execute(
            'SELECT * FROM drafts WHERE id = ?', (draft_id,)).fetchone()

    def _next_version(self, draft_id):
        row = self._conn.execute(
            'SELECT COALESCE(MAX(version), 0) FROM draft_versions'
            ' WHERE draft_id = ?', (draft_id,)).fetchone()
        return row[0] + 1

    def _snapshot(self, draft_id, title, body, action, role, at):
        self._conn.execute(
            'INSERT INTO draft_versions (draft_id, version, title, body, action, role, at)'
            ' VALUES (?, ?, ?, ?, ?, ?, ?)',
            (draft_id, self._next_version(draft_id), title, body, action, role, at))

    def create(self, title, body, author_role):
        """Create a draft in 'draft' status and return its record."""
        title = _validate_text(title, 'title')
        body = _validate_text(body, 'body')
        now = _now()
        with self._lock, self._conn:
            cur = self._conn.execute('INSERT INTO draft_id_seq DEFAULT VALUES')
            draft_id = f'D-{cur.lastrowid}'
            self._conn.execute(
                'INSERT INTO drafts (id, seq, title, body, author_role, status, created_at, updated_at)'
                ' VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
                (draft_id, cur.lastrowid, title, body, author_role, 'draft', now, now))
            self._conn.execute(
                'INSERT INTO draft_versions (draft_id, version, title, body, action, role, at)'
                ' VALUES (?, 1, ?, ?, ?, ?, ?)',
                (draft_id, title, body, 'create', author_role, now))
            self._conn.execute(
                'INSERT INTO draft_transitions (draft_id, action, role, at, version)'
                ' VALUES (?, ?, ?, ?, NULL)',
                (draft_id, 'create', author_role, now))
            return self._record_for_row(self._get_row(draft_id))

    def get(self, draft_id):
        """Return a deep copy of the draft, or None when unknown."""
        with self._lock, self._conn:
            row = self._get_row(draft_id)
            if row is None:
                return None
            return self._record_for_row(row)

    def list(self):
        """Return deep copies of all drafts, oldest first."""
        with self._lock, self._conn:
            rows = self._conn.execute(
                'SELECT * FROM drafts ORDER BY seq ASC').fetchall()
            return [self._record_for_row(r) for r in rows]

    def edit(self, draft_id, title=None, body=None, role=None):
        """Replace title/body in place. Only legal in 'draft' status.

        At least one of title/body must be supplied; omitted fields
        keep their value. Raises DraftNotFoundError or
        InvalidTransitionError (fail-closed). A successful edit
        appends a version snapshot; `role` records who made it.
        """
        with self._lock, self._conn:
            row = self._get_row(draft_id)
            if row is None:
                raise DraftNotFoundError(draft_id)
            if row['status'] != 'draft':
                raise InvalidTransitionError(
                    f"cannot edit a draft in status {row['status']!r}")
            new_title = row['title'] if title is None else _validate_text(title, 'title')
            new_body = row['body'] if body is None else _validate_text(body, 'body')
            now = _now()
            self._conn.execute(
                'UPDATE drafts SET title = ?, body = ?, updated_at = ? WHERE id = ?',
                (new_title, new_body, now, draft_id))
            self._snapshot(draft_id, new_title, new_body, 'edit',
                           role if role is not None else 'unknown', now)
            return self._record_for_row(self._get_row(draft_id))

    def transition(self, draft_id, action, role):
        """Apply a state-machine action and return the record.

        Unknown actions and illegal (status, action) pairs raise
        InvalidTransitionError; unknown ids raise DraftNotFoundError.
        Both are fail-closed: the stored record is untouched.
        """
        with self._lock, self._conn:
            row = self._get_row(draft_id)
            if row is None:
                raise DraftNotFoundError(draft_id)
            nxt = _TRANSITIONS.get((row['status'], action))
            if nxt is None:
                raise InvalidTransitionError(
                    f"cannot {action!r} a draft in status "
                    f"{row['status']!r}")
            now = _now()
            self._conn.execute(
                'UPDATE drafts SET status = ?, updated_at = ? WHERE id = ?',
                (nxt, now, draft_id))
            self._conn.execute(
                'INSERT INTO draft_transitions (draft_id, action, role, at, version)'
                ' VALUES (?, ?, ?, ?, NULL)',
                (draft_id, action, role, now))
            self._snapshot(draft_id, row['title'], row['body'], action, role, now)
            return self._record_for_row(self._get_row(draft_id))

    def rollback(self, draft_id, version, role):
        """Restore a draft's content to a prior snapshot (batch 3).

        Legal from 'draft', 'submitted', 'approved', and 'published';
        every rollback lands in 'draft' so reverted content must pass
        review again before it can be re-published. 'rejected' stays
        terminal (fail-closed). Unknown ids raise DraftNotFoundError;
        unknown versions and rejected drafts raise
        InvalidTransitionError; the stored record is untouched on any
        failure.

        Effects on success (all appends, never rewrites): the live
        title/body become the snapshot's content, one 'rollback'
        transition (carrying the restored version) is appended, and
        one new snapshot records the post-rollback content. Prior
        transitions, snapshots, and audit records are never edited or
        deleted.
        """
        with self._lock, self._conn:
            row = self._get_row(draft_id)
            if row is None:
                raise DraftNotFoundError(draft_id)
            if row['status'] == 'rejected':
                raise InvalidTransitionError(
                    'cannot rollback a rejected draft')
            target = self._conn.execute(
                'SELECT title, body FROM draft_versions'
                ' WHERE draft_id = ? AND version = ?',
                (draft_id, version)).fetchone()
            if target is None:
                raise InvalidTransitionError(
                    f'unknown version {version!r}')
            now = _now()
            self._conn.execute(
                'UPDATE drafts SET title = ?, body = ?, status = ?, updated_at = ? WHERE id = ?',
                (target['title'], target['body'], 'draft', now, draft_id))
            self._conn.execute(
                'INSERT INTO draft_transitions (draft_id, action, role, at, version)'
                ' VALUES (?, ?, ?, ?, ?)',
                (draft_id, 'rollback', role, now, version))
            self._snapshot(draft_id, target['title'], target['body'],
                           'rollback', role, now)
            return self._record_for_row(self._get_row(draft_id))

    def __len__(self):
        with self._lock, self._conn:
            return self._conn.execute(
                'SELECT COUNT(*) FROM drafts').fetchone()[0]
