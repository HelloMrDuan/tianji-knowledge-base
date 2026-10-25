"""B018: admin role decision matrix + append-only audit log (TJ-026.4
batch 1: role model, unauthorized blocking, audit skeleton).

Runs in public CI (validate.yml). Imports only tianji_kb.admin_roles
and tianji_kb.admin_audit (pure stdlib): no FastAPI stack, no private
Canonical/RAG data required. HTTP-level verification (real status codes
end to end, probe endpoint, audit read gating) lives in
test_b018_admin_roles_http.py (offline acceptance only, NOT public CI).

Batch 1 scope reminder: role model + blocking + audit skeleton ONLY.
No draft storage, no approval state machine, no rollback, no version
snapshots — those are later batches and must not appear here.
"""

import unittest

from tianji_kb.admin_roles import (
    ADMIN_ROLES,
    WRITE_OPERATIONS,
    parse_admin_role_tokens,
    resolve_role_access,
)
from tianji_kb.admin_audit import AuditLog

ROLE_TOKENS = {
    'user-token': 'user',
    'editor-token': 'editor',
    'reviewer-token': 'reviewer',
    'publisher-token': 'publisher',
}


class TestB018RoleConstants(unittest.TestCase):
    def test_four_roles(self):
        self.assertEqual(ADMIN_ROLES, {'user', 'editor', 'reviewer', 'publisher'})

    def test_operation_role_sets(self):
        self.assertEqual(WRITE_OPERATIONS['draft'],
                         {'editor', 'reviewer', 'publisher'})
        self.assertEqual(WRITE_OPERATIONS['approve'],
                         {'reviewer', 'publisher'})
        self.assertEqual(WRITE_OPERATIONS['publish'], {'publisher'})
        # The read-only role may perform no write operation at all.
        for allowed in WRITE_OPERATIONS.values():
            self.assertNotIn('user', allowed)


class TestB018RoleTokenParse(unittest.TestCase):
    def test_unset_and_blank_mean_no_tokens(self):
        self.assertEqual(parse_admin_role_tokens(None), {})
        self.assertEqual(parse_admin_role_tokens(''), {})
        self.assertEqual(parse_admin_role_tokens('   ,  '), {})

    def test_valid_mapping_with_whitespace(self):
        self.assertEqual(
            parse_admin_role_tokens(' tok-a : editor , tok-b:publisher '),
            {'tok-a': 'editor', 'tok-b': 'publisher'})

    def test_unknown_roles_and_malformed_pairs_dropped(self):
        self.assertEqual(
            parse_admin_role_tokens('good:editor,bad:superuser,no-colon,'
                                    ':publisher,also-good:reviewer'),
            {'good': 'editor', 'also-good': 'reviewer'})


class TestB018RoleDecisionMatrix(unittest.TestCase):
    def test_not_configured(self):
        self.assertEqual(resolve_role_access({}, 'Bearer x', 'draft'),
                         ('not_configured', None))
        self.assertEqual(resolve_role_access(None, 'Bearer x', 'draft'),
                         ('not_configured', None))

    def test_missing_credential(self):
        self.assertEqual(resolve_role_access(ROLE_TOKENS, None, 'draft'),
                         ('unauthorized', 'missing'))
        self.assertEqual(resolve_role_access(ROLE_TOKENS, 'Bearer ', 'draft'),
                         ('unauthorized', 'missing'))
        self.assertEqual(resolve_role_access(ROLE_TOKENS, 'Token x', 'draft'),
                         ('unauthorized', 'missing'))

    def test_invalid_credential(self):
        self.assertEqual(
            resolve_role_access(ROLE_TOKENS, 'Bearer wrong-token', 'draft'),
            ('unauthorized', 'invalid'))

    def test_user_role_is_denied_every_write_operation(self):
        for operation in ('draft', 'approve', 'publish'):
            self.assertEqual(
                resolve_role_access(ROLE_TOKENS, 'Bearer user-token', operation),
                ('forbidden', operation))

    def test_editor_role_draft_only(self):
        self.assertEqual(
            resolve_role_access(ROLE_TOKENS, 'Bearer editor-token', 'draft'),
            ('ok', 'editor'))
        for operation in ('approve', 'publish'):
            self.assertEqual(
                resolve_role_access(ROLE_TOKENS, 'Bearer editor-token', operation),
                ('forbidden', operation))

    def test_reviewer_role_draft_and_approve(self):
        for operation in ('draft', 'approve'):
            self.assertEqual(
                resolve_role_access(ROLE_TOKENS, 'Bearer reviewer-token', operation),
                ('ok', 'reviewer'))
        self.assertEqual(
            resolve_role_access(ROLE_TOKENS, 'Bearer reviewer-token', 'publish'),
            ('forbidden', 'publish'))

    def test_publisher_role_all_operations(self):
        for operation in ('draft', 'approve', 'publish'):
            self.assertEqual(
                resolve_role_access(ROLE_TOKENS, 'Bearer publisher-token', operation),
                ('ok', 'publisher'))

    def test_unknown_operation_is_forbidden_fail_closed(self):
        for token in ROLE_TOKENS:
            self.assertEqual(
                resolve_role_access(ROLE_TOKENS, f'Bearer {token}', 'delete-all'),
                ('forbidden', 'delete-all'))


class TestB018AuditLog(unittest.TestCase):
    def test_record_carries_who_when_what_outcome(self):
        log = AuditLog()
        entry = log.record('editor', 'write_probe:draft', 'allowed')
        self.assertEqual(entry['who'], 'editor')
        self.assertEqual(entry['what'], 'write_probe:draft')
        self.assertEqual(entry['outcome'], 'allowed')
        self.assertTrue(entry['when'])
        self.assertEqual(len(log), 1)

    def test_denied_attempts_are_recorded_too(self):
        log = AuditLog()
        log.record('user', 'write_probe:publish', 'denied', 'forbidden')
        self.assertEqual(len(log), 1)
        self.assertEqual(log.entries()[0]['outcome'], 'denied')

    def test_entries_are_appended_oldest_first(self):
        log = AuditLog()
        log.record('editor', 'write_probe:draft', 'allowed')
        log.record('user', 'write_probe:publish', 'denied')
        whats = [e['what'] for e in log.entries()]
        self.assertEqual(whats, ['write_probe:draft', 'write_probe:publish'])

    def test_returned_entries_cannot_mutate_the_log(self):
        log = AuditLog()
        log.record('editor', 'write_probe:draft', 'allowed')
        snapshot = log.entries()
        snapshot[0]['outcome'] = 'denied'
        snapshot[0]['who'] = 'publisher'
        snapshot.append({'who': 'fake', 'what': 'fake', 'outcome': 'allowed'})
        self.assertEqual(len(log), 1)
        self.assertEqual(log.entries()[0]['outcome'], 'allowed')
        self.assertEqual(log.entries()[0]['who'], 'editor')

    def test_no_update_or_delete_api_exists(self):
        log = AuditLog()
        for name in ('update', 'delete', 'remove', 'clear', 'rewrite'):
            self.assertFalse(hasattr(log, name), f'unexpected mutator: {name}')

    def test_unknown_outcome_is_rejected(self):
        log = AuditLog()
        with self.assertRaises(ValueError):
            log.record('editor', 'write_probe:draft', 'maybe')
        self.assertEqual(len(log), 0)


if __name__ == '__main__':
    unittest.main()
