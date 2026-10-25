"""Role model for admin write operations (TJ-026.4 batch 1: skeleton).

This is a NEW decision layer, deliberately separate from the TJ-026.3
read-scope model (admin_scopes.py): read scopes gate a single read token
for read endpoints; roles gate multi-token write operations. A role token
is compared verbatim and never parsed for its role; the token-to-role
mapping is server-side configuration only.

Batch 1 scope (do not expand): role model, unauthorized blocking, and
the audit-log skeleton. There is NO draft/approval/publish business in
batch 1 — no draft storage, no approval state machine, no rollback, no
version snapshots. The only verifiable write checkpoint is the controlled
write-probe operation, whose result always reports write_applied=False.

Roles:
- user: read only; no write operation is allowed.
- editor: may draft (probe only in batch 1).
- reviewer: may draft and approve (probe only in batch 1).
- publisher: may draft, approve and publish (probe only in batch 1).

This module is pure stdlib so the decision matrix can be tested in
public CI without the FastAPI stack or private knowledge data.
"""

import secrets

ADMIN_ROLES = frozenset({'user', 'editor', 'reviewer', 'publisher'})

# Probe operation -> roles allowed to perform it. These are the ONLY
# write operations in batch 1; each maps to a future business operation
# of the same name, but no such business exists yet.
#
# TJ-026.4 batch 3 adds exactly one operation below it: 'rollback'
# (publisher only). It gates the draft rollback endpoint (see
# admin_drafts.rollback); it is NOT a draft state-machine action and
# is deliberately absent from DRAFT_ACTION_OPERATION, so the generic
# action endpoint can never route a rollback (fail-closed: a rollback
# without a version body is rejected there as an unknown action).
WRITE_OPERATIONS = {
    'draft': frozenset({'editor', 'reviewer', 'publisher'}),
    'approve': frozenset({'reviewer', 'publisher'}),
    'publish': frozenset({'publisher'}),
    'rollback': frozenset({'publisher'}),
}


def parse_admin_role_tokens(value):
    """Parse a token-to-role mapping (e.g. TIANJI_ADMIN_ROLE_TOKENS).

    Format: 'token:role,token:role'. Returns {} when unset/blank.
    Malformed pairs and unknown roles are dropped; a token mapped to an
    unknown role grants nothing. Later entries overwrite earlier ones
    for the same token (plain dict semantics).
    """
    if value is None:
        return {}
    mapping = {}
    for part in value.split(','):
        part = part.strip()
        if not part or ':' not in part:
            continue
        token, role = part.split(':', 1)
        token = token.strip()
        role = role.strip()
        if token and role in ADMIN_ROLES:
            mapping[token] = role
    return mapping


def resolve_role_access(role_tokens, authorization, operation):
    """Decide an admin write request without any HTTP framework.

    Returns (outcome, detail):
    - ('not_configured', None): no role tokens configured server-side.
    - ('unauthorized', 'missing'): no Bearer token supplied.
    - ('unauthorized', 'invalid'): credential supplied but matches no
      configured role token.
    - ('forbidden', operation): role valid but the operation is not
      allowed for it (unknown operations are also forbidden: fail-closed).
    - ('ok', role): role valid and the operation is allowed for it.
    """
    if not role_tokens:
        return ('not_configured', None)
    prefix = 'Bearer '
    if not authorization or not authorization.startswith(prefix):
        return ('unauthorized', 'missing')
    supplied = authorization[len(prefix):]
    if not supplied:
        return ('unauthorized', 'missing')
    role = None
    for token, candidate in role_tokens.items():
        if secrets.compare_digest(supplied, token):
            role = candidate
            break
    if role is None:
        return ('unauthorized', 'invalid')
    allowed = WRITE_OPERATIONS.get(operation)
    if allowed is None or role not in allowed:
        return ('forbidden', operation)
    return ('ok', role)
