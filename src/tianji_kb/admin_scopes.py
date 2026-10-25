"""Minimal read-scope model for admin read endpoints (TJ-026.3).

Scopes are server-side configuration of the single admin read token, NOT
encoded in the bearer string: bearer tokens are compared verbatim and never
parsed for scopes. This is deliberately NOT a role system (roles, draft
approval, rollback and audit belong to TJ-026.4); it exists only so a
restricted read token is refused with 403 instead of silently serving
out-of-scope data.

Scope groups mirror the admin endpoint groups:
- research: POST /api/v1/admin/research/dream
- governance: GET /api/v1/admin/governance/*
- system: GET /api/v1/admin/system/*

Granted scopes None means "all scopes" (backward compatible default for
deployments that configure a single unrestricted read token). This module
is pure stdlib so the decision matrix can be tested in public CI without
the FastAPI stack or private knowledge data.
"""

import secrets

ADMIN_READ_SCOPES = frozenset({'research', 'governance', 'system'})


def parse_admin_scopes(value):
    """Parse a comma-separated scope list (e.g. TIANJI_ADMIN_READ_SCOPES).

    Returns None when unset/blank (all scopes granted). Unknown names are
    dropped; a list that yields no known scope becomes an empty frozenset
    (token valid but forbidden everywhere).
    """
    if value is None:
        return None
    names = {part.strip() for part in value.split(',')}
    names.discard('')
    if not names:
        return None
    return frozenset(name for name in names if name in ADMIN_READ_SCOPES)


def resolve_admin_access(configured_token, granted_scopes, authorization,
                         required_scope):
    """Decide an admin read request without any HTTP framework.

    Returns (outcome, detail):
    - ('not_configured', None): no token configured server-side.
    - ('unauthorized', 'missing'): no Bearer credential supplied.
    - ('unauthorized', 'invalid'): credential supplied but does not match.
    - ('forbidden', scope): credential valid but required scope not granted.
    - ('ok', None): credential valid and scope granted (or unrestricted).
    """
    if not configured_token:
        return ('not_configured', None)
    prefix = 'Bearer '
    if not authorization or not authorization.startswith(prefix):
        return ('unauthorized', 'missing')
    supplied = authorization[len(prefix):]
    if not supplied or not secrets.compare_digest(supplied, configured_token):
        return ('unauthorized', 'invalid')
    if (required_scope is not None and granted_scopes is not None
            and required_scope not in granted_scopes):
        return ('forbidden', required_scope)
    return ('ok', None)
