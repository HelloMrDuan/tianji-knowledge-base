"""B016: admin read-scope decision matrix (TJ-026.3).

Runs in public CI (validate.yml). Imports only tianji_kb.admin_scopes
(pure stdlib): no FastAPI stack, no private Canonical/RAG data required.
HTTP-level verification (real status codes end to end) lives in
test_b016_admin_scope_http.py (offline acceptance only, NOT public CI).
"""

import unittest

from tianji_kb.admin_scopes import (
    ADMIN_READ_SCOPES,
    parse_admin_scopes,
    resolve_admin_access,
)

TOKEN = 'b016-test-token'


class TestB016AdminScopeConstants(unittest.TestCase):
    def test_scope_groups_mirror_endpoint_groups(self):
        self.assertEqual(ADMIN_READ_SCOPES, {'research', 'governance', 'system'})


class TestB016AdminScopeParse(unittest.TestCase):
    def test_unset_and_blank_mean_all_scopes(self):
        self.assertIsNone(parse_admin_scopes(None))
        self.assertIsNone(parse_admin_scopes(''))
        self.assertIsNone(parse_admin_scopes('   ,  '))

    def test_comma_list_with_whitespace(self):
        self.assertEqual(parse_admin_scopes(' governance, system '),
                         {'governance', 'system'})

    def test_unknown_names_dropped(self):
        self.assertEqual(parse_admin_scopes('governance,bogus'), {'governance'})
        # A list yielding no known scope forbids everywhere (not "all").
        self.assertEqual(parse_admin_scopes('bogus'), frozenset())


class TestB016AdminScopeDecision(unittest.TestCase):
    def test_unconfigured_token_is_503_path(self):
        self.assertEqual(
            resolve_admin_access(None, None, 'Bearer x', 'governance'),
            ('not_configured', None))
        self.assertEqual(
            resolve_admin_access('', None, 'Bearer x', 'governance'),
            ('not_configured', None))

    def test_missing_or_malformed_credential_is_401_missing(self):
        for auth in (None, '', 'Token abc'):
            with self.subTest(auth=auth):
                self.assertEqual(
                    resolve_admin_access(TOKEN, None, auth, 'governance'),
                    ('unauthorized', 'missing'))

    def test_wrong_credential_is_401_invalid(self):
        # 'Bearer ' with an empty token matches the pre-existing API
        # behavior: it reaches the comparison and fails as invalid.
        for auth in ('Bearer wrong', 'Bearer '):
            with self.subTest(auth=auth):
                self.assertEqual(
                    resolve_admin_access(TOKEN, None, auth, 'governance'),
                    ('unauthorized', 'invalid'))

    def test_valid_token_with_granted_scope_is_ok(self):
        for scope in ('research', 'governance', 'system'):
            with self.subTest(scope=scope):
                self.assertEqual(
                    resolve_admin_access(TOKEN, {scope}, f'Bearer {TOKEN}', scope),
                    ('ok', None))

    def test_valid_token_with_insufficient_scope_is_403(self):
        # Each group is forbidden to a token granted only another group.
        cases = [
            ({'governance'}, 'research'),
            ({'governance'}, 'system'),
            ({'research'}, 'governance'),
            ({'system'}, 'research'),
            (frozenset(), 'governance'),
        ]
        for granted, required in cases:
            with self.subTest(granted=granted, required=required):
                self.assertEqual(
                    resolve_admin_access(TOKEN, granted, f'Bearer {TOKEN}', required),
                    ('forbidden', required))

    def test_unrestricted_token_grants_all_scopes(self):
        for scope in ('research', 'governance', 'system'):
            with self.subTest(scope=scope):
                self.assertEqual(
                    resolve_admin_access(TOKEN, None, f'Bearer {TOKEN}', scope),
                    ('ok', None))

    def test_no_required_scope_needs_no_grant(self):
        # Endpoints that declare no scope stay reachable to any valid token,
        # even one granted an empty set.
        self.assertEqual(
            resolve_admin_access(TOKEN, frozenset(), f'Bearer {TOKEN}', None),
            ('ok', None))

    def test_bearer_token_never_parsed_for_scopes(self):
        # A token string containing scope-like text is compared verbatim:
        # it must not gain scopes by naming them.
        tricky = 'tok:governance,system'
        self.assertEqual(
            resolve_admin_access(tricky, {'research'}, f'Bearer {tricky}', 'governance'),
            ('forbidden', 'governance'))
        self.assertEqual(
            resolve_admin_access(tricky, {'research'}, f'Bearer {tricky}', 'research'),
            ('ok', None))


if __name__ == '__main__':
    unittest.main()
