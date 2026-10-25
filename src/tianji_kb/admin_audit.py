"""Append-only audit log skeleton (TJ-026.4 batch 1).

Every write attempt — allowed or denied — must leave a trace. Records
carry who/when/what/outcome and nothing else that could leak secrets:
`who` is a role name or 'unknown', never a raw token.

Append-only by construction: this module exposes no update and no delete
operation, and entries() returns deep copies, so a caller holding a
returned record cannot mutate the log through it. There is no API to
rewrite history; a future rollback feature (batch 3) must append a
compensating record, never edit an existing one.

Storage in batch 1 is process memory (one AuditLog per app instance).
That is sufficient for the skeleton — the records are real, appended
on every write attempt, and readable through the audit endpoint — but
it does not survive a restart. Durable audit storage is a later batch's
decision, not something this skeleton pretends to provide.

This module is pure stdlib so it can be tested in public CI without
the FastAPI stack or private knowledge data.
"""

import copy
from datetime import datetime, timezone

AUDIT_OUTCOMES = frozenset({'allowed', 'denied'})


class AuditLog:
    """In-memory append-only audit record store."""

    def __init__(self):
        self._entries = []

    def record(self, who, what, outcome, detail=None):
        """Append one record and return it. `outcome` must be
        'allowed' or 'denied'; anything else is rejected (fail-closed)
        so no ambiguous record can enter the log."""
        if outcome not in AUDIT_OUTCOMES:
            raise ValueError(f'unknown audit outcome: {outcome!r}')
        entry = {
            'who': who,
            'when': datetime.now(timezone.utc).isoformat(),
            'what': what,
            'outcome': outcome,
            'detail': detail,
        }
        self._entries.append(entry)
        return copy.deepcopy(entry)

    def entries(self):
        """Return a deep copy of all records, oldest first. Mutating
        the returned list or its records never affects the log."""
        return copy.deepcopy(self._entries)

    def __len__(self):
        return len(self._entries)
