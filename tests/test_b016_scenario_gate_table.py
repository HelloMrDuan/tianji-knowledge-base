"""B016: Scenario publish-gate tables are truthful (TJ-026.2).

Runs in public CI (validate.yml). Pure repository-file parsing: no
FastAPI stack, no private Canonical/RAG data required.

The gate tables in web/visual-prototype/src/admin/scenarioGate.ts are
reviewed code claims. This test pins them to reality:
- every scenario id in the backend registry has exactly one entry in
  each table (routes, real pages, key tests) and vice versa;
- every route in the table exists in the public frontend router;
- every spec file in the key-tests table exists in tests/.

If a scenario, page or spec is added/removed/renamed without updating
the tables, this test fails rather than letting the admin page render a
stale gate.
"""

import os
import re
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GATE_TS = os.path.join(ROOT, 'web', 'visual-prototype', 'src', 'admin',
                        'scenarioGate.ts')
ENGINE_PY = os.path.join(ROOT, 'src', 'tianji_kb', 'scenario_engine.py')
PUBLIC_APP = os.path.join(ROOT, 'web', 'visual-prototype', 'src', 'public',
                          'PublicApp.tsx')
TESTS_DIR = os.path.join(ROOT, 'web', 'visual-prototype', 'tests')


def _block(text, const_name):
    start = text.find(f'export const {const_name}')
    assert start >= 0, f'{const_name} not found'
    end = text.find('};', start)
    assert end >= 0, f'{const_name} block not closed'
    return text[start:end]


def _registry_ids():
    with open(ENGINE_PY, encoding='utf-8') as f:
        text = f.read()
    start = text.find('SCENARIOS = [')
    assert start >= 0
    end = text.find('\n]\n', start)
    assert end >= 0
    block = text[start:end]
    return set(re.findall(r'"id": "([^"]+)"', block))


class TestB016ScenarioGateTable(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(GATE_TS, encoding='utf-8') as f:
            cls.gate = f.read()
        with open(PUBLIC_APP, encoding='utf-8') as f:
            cls.app = f.read()
        cls.registry = _registry_ids()

    def test_registry_has_eleven_scenarios(self):
        self.assertEqual(len(self.registry), 11)

    def test_gate_tables_cover_registry_exactly(self):
        # Table keys may be quoted ("bazi-profile") or bare (question).
        def _keys(block, value_pattern):
            ids = set()
            for quoted, bare in re.findall(
                    rf'(?:"([^"]+)"|([A-Za-z0-9_-]+))\s*:\s*{value_pattern}',
                    block):
                ids.add(quoted or bare)
            return ids
        routes = _block(self.gate, 'SCENARIO_ROUTES')
        route_ids = _keys(routes, r'"[^"]*"')
        pages = _block(self.gate, 'SCENARIO_REAL_PAGES')
        page_ids = _keys(pages, r'true')
        tests = _block(self.gate, 'SCENARIO_KEY_TESTS')
        test_ids = _keys(tests, r'\[')
        self.assertEqual(route_ids, self.registry)
        self.assertEqual(page_ids, self.registry)
        self.assertEqual(test_ids, self.registry)

    def test_table_routes_exist_in_public_router(self):
        routes = _block(self.gate, 'SCENARIO_ROUTES')
        table_routes = set(re.findall(r': "(/[^"]*)"', routes))
        app_routes = set(re.findall(r'path === "(/[^"]*)"', self.app))
        # Domain tool pages also resolve through domainPage, but scenario
        # routes must be explicit router branches.
        missing = table_routes - app_routes
        self.assertEqual(missing, set())

    def test_key_test_files_exist(self):
        tests = _block(self.gate, 'SCENARIO_KEY_TESTS')
        specs = set(re.findall(r'"([^"]+\.spec\.ts)"', tests))
        self.assertTrue(specs, 'no spec files parsed from table')
        for spec in sorted(specs):
            with self.subTest(spec=spec):
                self.assertTrue(os.path.isfile(os.path.join(TESTS_DIR, spec)),
                                f'missing spec file: {spec}')

    def test_gate_module_contains_no_demo_records(self):
        self.assertNotIn('DEMO', self.gate)


if __name__ == '__main__':
    unittest.main()
