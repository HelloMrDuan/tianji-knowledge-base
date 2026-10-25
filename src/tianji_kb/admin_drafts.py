"""Draft approval flow (TJ-026.4 batch 2).

Batch 2 adds the business that batch 1 deliberately left out: draft
storage, an approval state machine, and the draft/approve/publish
endpoints. It does NOT add durable storage or rollback — those are
later batches' decisions, and this module must not pretend otherwise.

Storage is process memory (one DraftStore per app instance, same
lifecycle decision as the batch-1 audit skeleton): drafts are real
while the process lives and are lost on restart. Every draft response
carries that fact in its storage note; the frontend shows it too.

State machine (fail-closed: anything not listed is rejected):
    draft --submit--> submitted --approve--> approved --publish--> published
                                  +--reject--> rejected (terminal)

Role gating reuses the batch-1 decision layer (admin_roles): the
operation each action maps to is fixed here and tested in public CI:
    create / edit / submit -> 'draft'   (editor, reviewer, publisher)
    approve / reject       -> 'approve' (reviewer, publisher)
    publish                -> 'publish' (publisher only)
The read-only 'user' role may perform no draft action at all.

Records carry who/when/what/outcome history (the approval trail) but
never a version snapshot of prior content: editing replaces the
current title/body in place, and only the transition log is kept.
Audit records (admin_audit) never contain draft content — only draft
ids and outcomes — so drafts cannot leak through the audit endpoint.

TJ-026.4 batch 3 (this change) adds what batch 2 deliberately left
out: version snapshots and rollback. The batch-2 premise ("the task
depends on batch-2 versioning") was a mismatch — batch 2 kept only the
transition log — so batch 3 first builds versioning itself:

- Every mutation (create, edit, each transition, rollback) appends
  one immutable snapshot {version, title, body, action, role, at}.
  Snapshots are deep-copied on return, so a caller can never mutate
  a stored snapshot through a returned record.
- Rollback (publisher only, enforced by the batch-1 role layer via
  the 'rollback' write operation) restores a draft's title/body to a
  chosen snapshot and lands the draft in 'draft' status, so reverted
  content must pass review again before it can be re-published.
  Design decision (scheme A, draft-internal version history): versions
  belong to the draft record itself. Scheme B (a standalone registry
  of published content) is explicitly excluded to a later task.
- State-machine extension: rollback is legal from draft, submitted,
  approved, and published (all land in 'draft'); rejected stays
  terminal (fail-closed). There is NO new status: published rolls
  back to 'draft', reusing the existing approval flow.
- Rollback never edits or deletes prior transitions, snapshots, or
  audit records: it appends one 'rollback' transition, one new
  snapshot (the restored content), and — at the API layer — one
  compensating audit record (draft id + version only, no content).
  Versions share the draft's process-memory lifecycle: they are lost
  on restart, and this batch does not pretend otherwise.

This module is pure stdlib so the state machine and the action-to-
operation mapping can be tested in public CI without the FastAPI
stack or private knowledge data. HTTP-level verification (real status
codes end to end, role matrix over endpoints, audit entries, no
content leakage) lives in test_b020_drafts_http.py (offline acceptance
only, NOT public CI); rollback HTTP verification lives in
test_b022_rollback_http.py (same offline-acceptance rule).
"""

import copy
from datetime import datetime, timezone

DRAFT_STATUSES = frozenset(
    {'draft', 'submitted', 'approved', 'rejected', 'published'})

# Draft action -> batch-1 write operation whose role set gates it.
# Unknown actions are rejected (fail-closed) by transition().
DRAFT_ACTION_OPERATION = {
    'create': 'draft',
    'edit': 'draft',
    'submit': 'draft',
    'approve': 'approve',
    'reject': 'approve',
    'publish': 'publish',
}

# (current status, action) -> next status. Anything absent is illegal.
_TRANSITIONS = {
    ('draft', 'submit'): 'submitted',
    ('submitted', 'approve'): 'approved',
    ('submitted', 'reject'): 'rejected',
    ('approved', 'publish'): 'published',
}

STORAGE_NOTE = ('草稿仅保存在进程内存中，服务重启后丢失；'
                '持久化存储另行决策。')


class DraftNotFoundError(Exception):
    """No draft with the requested id exists in this store."""


class InvalidTransitionError(Exception):
    """The requested action is illegal from the draft's status."""


class InvalidDraftInputError(Exception):
    """Title/body fail validation (wrong type or blank)."""


def _validate_text(value, field):
    if not isinstance(value, str) or not value.strip():
        raise InvalidDraftInputError(f'{field} must be a non-empty string')
    return value


def _now():
    return datetime.now(timezone.utc).isoformat()


def _snapshot(record, action, role, at):
    """Append one immutable snapshot of the record's current content.

    Versions are sequential from 1. Title/body are strings (immutable),
    so storing them is isolation-safe: later edits replace the live
    record's fields instead of mutating a snapshot's strings.
    """
    record['versions'].append({
        'version': len(record['versions']) + 1,
        'title': record['title'],
        'body': record['body'],
        'action': action,
        'role': role,
        'at': at,
    })


class DraftStore:
    """In-memory draft store with an approval state machine.

    Append-only in the transition-log sense only: records themselves
    are mutable through edit() while in 'draft' status, but the
    transition log is never edited or deleted. Returned records are
    deep copies, so a caller holding one cannot mutate the store
    through it.

    Batch 3 adds version snapshots (see _snapshot) and rollback():
    versions are append-only like the transition log, and rollback
    appends rather than rewrites. Versions share the store's
    process-memory lifecycle and are lost on restart.

    TJ-026.5 adds a SQLite-backed store with the same interface
    (admin_storage.SqliteDraftStore); the API reports which store
    backs a draft response through `storage` / `storage_note`
    below. Memory keeps the old wording.
    """

    storage = 'process_memory'
    storage_note = STORAGE_NOTE

    def __init__(self):
        self._drafts = {}
        self._seq = 0

    def create(self, title, body, author_role):
        """Create a draft in 'draft' status and return its record."""
        title = _validate_text(title, 'title')
        body = _validate_text(body, 'body')
        self._seq += 1
        draft_id = f'D-{self._seq}'
        now = _now()
        record = {
            'id': draft_id,
            'title': title,
            'body': body,
            'author_role': author_role,
            'status': 'draft',
            'created_at': now,
            'updated_at': now,
            'transitions': [
                {'action': 'create', 'role': author_role, 'at': now},
            ],
            'versions': [],
        }
        _snapshot(record, 'create', author_role, now)
        self._drafts[draft_id] = record
        return copy.deepcopy(record)

    def get(self, draft_id):
        """Return a deep copy of the draft, or None when unknown."""
        record = self._drafts.get(draft_id)
        return copy.deepcopy(record) if record is not None else None

    def list(self):
        """Return deep copies of all drafts, oldest first."""
        return copy.deepcopy(list(self._drafts.values()))

    def edit(self, draft_id, title=None, body=None, role=None):
        """Replace title/body in place. Only legal in 'draft' status.

        At least one of title/body must be supplied; omitted fields
        keep their value. Raises DraftNotFoundError or
        InvalidTransitionError (fail-closed). A successful edit
        appends a version snapshot (batch 3); `role` records who made
        it (the API layer passes the authenticated role).
        """
        record = self._drafts.get(draft_id)
        if record is None:
            raise DraftNotFoundError(draft_id)
        if record['status'] != 'draft':
            raise InvalidTransitionError(
                f"cannot edit a draft in status {record['status']!r}")
        if title is not None:
            record['title'] = _validate_text(title, 'title')
        if body is not None:
            record['body'] = _validate_text(body, 'body')
        now = _now()
        record['updated_at'] = now
        _snapshot(record, 'edit', role if role is not None else 'unknown', now)
        return copy.deepcopy(record)

    def transition(self, draft_id, action, role):
        """Apply a state-machine action and return the record.

        Unknown actions and illegal (status, action) pairs raise
        InvalidTransitionError; unknown ids raise DraftNotFoundError.
        Both are fail-closed: the stored record is untouched.
        """
        record = self._drafts.get(draft_id)
        if record is None:
            raise DraftNotFoundError(draft_id)
        nxt = _TRANSITIONS.get((record['status'], action))
        if nxt is None:
            raise InvalidTransitionError(
                f"cannot {action!r} a draft in status "
                f"{record['status']!r}")
        now = _now()
        record['status'] = nxt
        record['updated_at'] = now
        record['transitions'].append(
            {'action': action, 'role': role, 'at': now})
        _snapshot(record, action, role, now)
        return copy.deepcopy(record)

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
        deleted — the API layer appends the compensating audit record
        separately. Role gating (publisher only) is enforced by the
        API layer through the batch-1 'rollback' write operation.
        """
        record = self._drafts.get(draft_id)
        if record is None:
            raise DraftNotFoundError(draft_id)
        if record['status'] == 'rejected':
            raise InvalidTransitionError(
                'cannot rollback a rejected draft')
        target = None
        for snap in record['versions']:
            if snap['version'] == version:
                target = snap
                break
        if target is None:
            raise InvalidTransitionError(
                f'unknown version {version!r}')
        now = _now()
        record['title'] = target['title']
        record['body'] = target['body']
        record['status'] = 'draft'
        record['updated_at'] = now
        record['transitions'].append(
            {'action': 'rollback', 'role': role, 'at': now,
             'version': version})
        _snapshot(record, 'rollback', role, now)
        return copy.deepcopy(record)

    def __len__(self):
        return len(self._drafts)
