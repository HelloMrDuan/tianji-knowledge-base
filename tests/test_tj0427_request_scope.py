"""TJ-031.19 / E0427 request-scope activation tests (P1 follow-up).

Proves ``unified_compute_request_scope()`` is actually entered on the
real serving path — not just available as a helper:

* ``scenario_engine.execute_scenario`` (the single choke point all 11
  scenarios pass through, reached by both API endpoints via
  ``starlette.concurrency.run_in_threadpool``) enters one fresh scope
  per request, reusing an ambient scope when the caller already
  entered one.
* ``life_presentation.build_life_presentation_for`` enters one scope
  around its whole body, so the direct ``assemble_birth`` call that
  runs AFTER ``execute_scenario("life", ...)`` returns shares the
  request's scope instead of falling back to the ambient module
  caches.
* The scope is active during unified compute, evicted on exit
  (including on exception), and nothing is retained in the
  module-level caches afterwards; two sequential requests with
  different births recompute independently.

Honest classes, following the batch-5 lane test discipline:

* Local stub tests: the sealed engine (``execute("bazi", ...)``)
  raises ``RuntimeUnavailable`` without sealed ``data/``. Every
  scenario executor runs its unified assembly FIRST and only then
  calls the sealed engine, so the expected local shape is
  ``RuntimeUnavailable`` AFTER the assembly ran in-scope — the
  scope assertions are taken from spies on the sanctioned seam
  (``cached_execute``, patched exactly as in
  ``test_tj0427_unified_compute._stub_engine_patchers``) and on the
  life wrapper's direct ``assemble_birth`` call. Full end-to-end
  success (real envelopes, byte-identical public output) is sealed
  acceptance, not claimed here; the batch-5 equivalence snapshots
  in ``test_tj0427_unified_compute`` are the byte-identical guard
  and must keep passing unchanged.
* No computation result is stubbed into a pass: the stub engines
  only replace sealed computation (same fakes as the P1 file); the
  scope entry / reuse / eviction code under test is real.
"""

import copy
import unittest
from unittest import mock

from starlette.concurrency import run_in_threadpool

from tianji_kb import scenario_engine
from tianji_kb import unified_compute as uc
from tianji_kb.life_presentation import build_life_presentation_for
from tianji_kb.runtime_catalog import RuntimeUnavailable
from tianji_kb.scenario_engine import execute_scenario

F2_BIRTH = '2024-02-11T16:27:07+08:00'
F2B_BIRTH = '2024-03-11T10:00:00+08:00'
F2_GANZHI = ['甲辰', '丙寅', '乙巳', '甲申']
F2B_GANZHI = ['乙巳', '丁卯', '丙午', '丁酉']


def _fake_dayun_timeline():
    """Copied from test_tj0427_unified_compute (same fixture)."""
    ganzhi_cycle = ['丁卯', '戊辰', '己巳', '庚午',
                    '辛未', '壬申', '癸酉', '甲戌']
    rows = [{'period_index': i + 1, 'candidate_ganzhi': ganzhi,
             'stem': ganzhi[0], 'branch': ganzhi[1],
             'ten_god_relative_to_natal_day_stem': '比肩'}
            for i, ganzhi in enumerate(ganzhi_cycle)]
    return {
        'variant': 'dayun-classical-composition-v1',
        'status': 'converted',
        'traditional_role': 'male',
        'sequence': {'rows': rows},
        'sequence_time_alignment': [
            {'period_index': row['period_index'],
             'candidate_ganzhi': row['candidate_ganzhi'],
             'stem': row['stem'], 'branch': row['branch'],
             'ten_god_relative_to_natal_day_stem': '比肩',
             'start_interval': {
                 'earliest': '2030-01-01T00:00:00+08:00',
                 'latest': '2030-01-02T00:00:00+08:00',
                 'max_inclusive': True,
                 'basis': 'sanming_shichen_level',
                 'method': 'sanming_shichen_level',
                 'variant': 'bazi-dayun-adjacent-jie-research-v1'}}
            for row in rows],
    }


def _fake_flow_boundary():
    """Copied from test_tj0427_unified_compute (same fixture)."""
    return {
        'variant': 'bazi-annual-lichun-boundary-v1',
        'day_master': '乙',
        'rows': [{'gregorian_lichun_year': 2025,
                  'start_inclusive': '2025-02-03T22:10:00+08:00',
                  'end_exclusive': '2026-02-04T04:00:00+08:00',
                  'ganzhi_in_interval': '乙巳',
                  'year_stem': '乙', 'year_branch': '巳'}],
    }


def _pillars_for(ganzhi_list, day_stem):
    return [
        {'name': name, 'ganzhi': ganzhi,
         'stem': {'value': ganzhi[0], 'ten_god': '比肩'},
         'branch': {'value': ganzhi[1], 'hidden_stems': []}}
        for name, ganzhi in zip(('year', 'month', 'day', 'hour'),
                                ganzhi_list)]


def _research_block(variant):
    return {'variant': variant, 'research_only': True,
            'public_enabled': False, 'ai_enabled': False}


def _scope_spy_patchers(natal_calls, scope_seen):
    """Stub engine patchers (copied from
    ``test_tj0427_unified_compute._stub_engine_patchers``) with one
    addition: the fake ``cached_execute`` records whether a request
    scope was active at the moment unified compute ran, and which
    birth it computed for. Only computation is replaced, never the
    scope / cache / entry code under test.
    """

    def fake_cached_execute(domain, inputs, allow_research=False):
        scope_seen.append(uc.unified_compute_request_scope_active())
        natal_calls.append((domain, dict(inputs), allow_research))
        birth = inputs['value']
        ganzhi = F2_GANZHI if birth == F2_BIRTH else F2B_GANZHI
        day_stem = '乙' if birth == F2_BIRTH else '丙'
        return {
            'result': {
                'pillars': _pillars_for(ganzhi, day_stem),
                'day_master': {'stem': day_stem, 'element': '木',
                               'polarity': '阴'},
            },
            'trace': [], 'rule_matches': [], 'evidence': {},
        }

    return [
        mock.patch.object(uc, 'cached_execute',
                          side_effect=fake_cached_execute),
        mock.patch.object(uc, '_live_pilot',
                          return_value=(None, 'month_not_piloted')),
        mock.patch('tianji_kb.bazi_core.ten_god',
                   return_value='比肩'),
        mock.patch(
            'tianji_kb.bazi_strength_engine.assess_strength',
            side_effect=lambda *a, **k: dict(
                _research_block(uc.PIN_STRENGTH_ENGINE_VARIANT),
                marker='strength')),
        mock.patch(
            'tianji_kb.bazi_pattern_engine.evaluate_all',
            side_effect=lambda *a, **k: dict(
                _research_block(uc.PIN_PATTERN_ENGINE_VARIANT),
                marker='pattern')),
        mock.patch(
            'tianji_kb.bazi_tiaohou.tiaohou_lookup',
            return_value={'variant': 'tiaohou-qiongtong-v1'}),
        mock.patch(
            'tianji_kb.bazi_bingyao.bingyao_lookup',
            return_value={'variant': 'bingyao-shenfeng-v1'}),
        mock.patch(
            'tianji_kb.bazi_xiyong_engine.evaluate_xiyong',
            side_effect=lambda *a, **k: dict(
                _research_block(uc.PIN_XIYONG_ENGINE_VARIANT),
                unified_verdict=None, systems={})),
        mock.patch(
            'tianji_kb.bazi_dayun_compose.classical_dayun_timeline',
            side_effect=lambda *a, **k: copy.deepcopy(
                _fake_dayun_timeline())),
        mock.patch(
            'tianji_kb.bazi_annual_reference'
            '.annual_lichun_boundaries',
            side_effect=lambda *a, **k: copy.deepcopy(
                _fake_flow_boundary())),
        mock.patch(
            'tianji_kb.bazi_combination_engine.combine',
            side_effect=lambda *a, **k: dict(
                _research_block(uc.PIN_COMBINATION_ENGINE_VARIANT),
                overall_effect=None)),
    ]


class _ScopeTestBase(unittest.TestCase):
    """Shared stub setup + no-retention assertions."""

    def setUp(self):
        uc.clear_unified_compute_cache()
        self.natal_calls = []
        self.scope_seen = []
        self.patchers = _scope_spy_patchers(self.natal_calls,
                                            self.scope_seen)
        for patcher in self.patchers:
            patcher.start()

    def tearDown(self):
        for patcher in reversed(self.patchers):
            patcher.stop()
        uc.clear_unified_compute_cache()

    def assert_no_retention(self):
        """No scope active, no entries in the live caches, and nothing
        leaked into the ambient module-level caches."""
        self.assertFalse(uc.unified_compute_request_scope_active())
        info = uc.unified_compute_cache_info()
        self.assertEqual(info['core_entries'], 0)
        self.assertEqual(info['year_entries'], 0)
        self.assertEqual(info['execute_entries'], 0)
        self.assertEqual(len(uc._CORE_CACHE), 0)
        self.assertEqual(len(uc._YEAR_CACHE), 0)
        self.assertEqual(len(uc._EXECUTE_CACHE), 0)


class ExecuteScenarioScopeTests(_ScopeTestBase):
    """The scope is entered on the real scenario entry point."""

    def test_romance_request_runs_unified_compute_inside_a_scope(self):
        # Locally the sealed engine raises AFTER the unified
        # assembly; that is the expected shape, not a test failure.
        with self.assertRaises(RuntimeUnavailable):
            execute_scenario("romance", {"birth_value": F2_BIRTH,
                                         "target_year": 2026})
        # The assembly ran (one natal computation for this birth)
        # and it ran inside a request scope.
        self.assertEqual(len(self.natal_calls), 1)
        self.assertEqual(self.natal_calls[0][1]['value'], F2_BIRTH)
        self.assertEqual(self.scope_seen, [True])
        # The exception exit evicted the scope: nothing retained.
        self.assert_no_retention()

    def test_two_sequential_requests_recompute_independently(self):
        for birth in (F2_BIRTH, F2B_BIRTH):
            with self.assertRaises(RuntimeUnavailable):
                execute_scenario("romance", {"birth_value": birth,
                                             "target_year": 2026})
            self.assert_no_retention()
        # Each request recomputed its own birth — the second was not
        # served from the first request's cache, and the charts differ.
        self.assertEqual([call[1]['value'] for call in self.natal_calls],
                         [F2_BIRTH, F2B_BIRTH])
        self.assertEqual(self.scope_seen, [True, True])

    def test_same_birth_twice_recomputes_per_request(self):
        for _ in range(2):
            with self.assertRaises(RuntimeUnavailable):
                execute_scenario("romance", {"birth_value": F2_BIRTH,
                                             "target_year": 2026})
            self.assert_no_retention()
        # Per-request scopes do not share: the second identical
        # request recomputes instead of reusing the first's cache.
        self.assertEqual(len(self.natal_calls), 2)

    def test_unknown_scenario_rejected_before_any_scope(self):
        with self.assertRaises(ValueError):
            execute_scenario("missing", {})
        self.assertEqual(self.natal_calls, [])
        self.assertEqual(self.scope_seen, [])
        self.assert_no_retention()

    def test_execute_scenario_reuses_ambient_scope(self):
        # A caller that already entered a scope (the life wrapper)
        # must be reused, not nested: the assembly stays visible in
        # the ambient scope until the caller exits it.
        with uc.unified_compute_request_scope():
            with self.assertRaises(RuntimeUnavailable):
                execute_scenario("romance", {"birth_value": F2_BIRTH,
                                             "target_year": 2026})
            self.assertEqual(self.scope_seen, [True])
            info = uc.unified_compute_cache_info()
            self.assertEqual(info['core_entries'], 1)
            self.assertEqual(info['year_entries'], 1)
            self.assertTrue(uc.unified_compute_request_scope_active())
        self.assert_no_retention()


class ThreadpoolServingPathTests(_ScopeTestBase,
                                 unittest.IsolatedAsyncioTestCase):
    """The exact API mechanism: ``run_in_threadpool(execute_scenario,
    ...)`` as used by both ``/api/v1/scenarios/*`` endpoints."""

    async def test_run_in_threadpool_execute_scenario_is_scoped(self):
        with self.assertRaises(RuntimeUnavailable):
            await run_in_threadpool(
                execute_scenario, "romance",
                {"birth_value": F2_BIRTH, "target_year": 2026})
        # The scope was entered synchronously inside execute_scenario
        # in the worker thread, active during unified compute there,
        # and evicted on return — no cross-thread propagation relied
        # on.
        self.assertEqual(self.scope_seen, [True])
        self.assert_no_retention()

    async def test_scope_entered_in_event_loop_propagates_to_worker(self):
        # Empirical check of the mechanism the API would rely on if a
        # scope were entered in the async handler: anyio copies the
        # calling context into the worker thread, so a scope entered
        # in the event loop is visible inside run_in_threadpool.
        # (The wiring does not depend on this — the scope is entered
        # inside execute_scenario in the worker — but the property
        # is verified, not assumed.)
        seen = []

        def record():
            seen.append(uc.unified_compute_request_scope_active())

        with uc.unified_compute_request_scope():
            await run_in_threadpool(record)
        self.assertEqual(seen, [True])
        self.assert_no_retention()

    async def test_two_threadpool_requests_do_not_share_cache(self):
        for birth in (F2_BIRTH, F2B_BIRTH):
            with self.assertRaises(RuntimeUnavailable):
                await run_in_threadpool(
                    execute_scenario, "romance",
                    {"birth_value": birth, "target_year": 2026})
            self.assert_no_retention()
        self.assertEqual([call[1]['value'] for call in self.natal_calls],
                         [F2_BIRTH, F2B_BIRTH])
        self.assertEqual(self.scope_seen, [True, True])


class LifeWrapperScopeTests(_ScopeTestBase):
    """The life wrapper's direct assemble_birth runs in-scope.

    The sealed scenario execution and the presentation builders are
    stubbed (they are not the code under test here); the request
    scope and the direct ``assemble_birth`` call are real.
    """

    def _life_patchers(self, fail_romance=False):
        """Stub the sealed parts of the life wrapper only."""
        assemble_seen = []
        assemble_charts = []
        real_assemble = uc.assemble_birth

        def spy_assemble(*args, **kwargs):
            assemble_seen.append(
                uc.unified_compute_request_scope_active())
            result = real_assemble(*args, **kwargs)
            assemble_charts.append(result['chart']['ganzhi'])
            return result

        def fake_execute_scenario(scenario_id, inputs):
            if fail_romance and scenario_id == "romance":
                raise RuntimeUnavailable(
                    "Build the reviewed production runtime before "
                    "serving requests")
            return {}

        captured = {}

        def fake_build_life(envelope, **kwargs):
            captured.update(kwargs)
            return "LIFE-PRESENTATION"

        return (assemble_seen, assemble_charts, captured, [
            mock.patch.object(uc, 'assemble_birth',
                              side_effect=spy_assemble),
            mock.patch.object(scenario_engine, 'execute_scenario',
                              side_effect=fake_execute_scenario),
            mock.patch(
                'tianji_kb.romance_presentation'
                '.build_romance_presentation',
                return_value={"romance_theme": "stub"}),
            mock.patch(
                'tianji_kb.life_presentation.build_life_presentation',
                side_effect=fake_build_life),
        ])

    def test_direct_assemble_birth_runs_inside_wrapper_scope(self):
        assemble_seen, assemble_charts, captured, extra = \
            self._life_patchers()
        for patcher in extra:
            patcher.start()
        try:
            result = build_life_presentation_for(F2_BIRTH, 2026)
        finally:
            for patcher in reversed(extra):
                patcher.stop()
        self.assertEqual(result, "LIFE-PRESENTATION")
        # The direct assemble_birth (life_presentation.py:807) ran
        # inside the wrapper's scope, for this request's birth.
        self.assertEqual(assemble_seen, [True])
        self.assertEqual(assemble_charts, [F2_GANZHI])
        # The trim handed to the builder came from this request's
        # own assembly, not from a retained cache.
        self.assertEqual(
            [p['ganzhi'] for p in
             captured['life_trim']['chart']['pillars']],
            F2_GANZHI)
        self.assert_no_retention()

    def test_two_life_requests_are_independent(self):
        assemble_seen, assemble_charts, captured, extra = \
            self._life_patchers()
        for patcher in extra:
            patcher.start()
        try:
            first = build_life_presentation_for(F2_BIRTH, 2026)
            first_trim = copy.deepcopy(captured['life_trim'])
            self.assert_no_retention()
            second = build_life_presentation_for(F2B_BIRTH, 2026)
            second_trim = copy.deepcopy(captured['life_trim'])
        finally:
            for patcher in reversed(extra):
                patcher.stop()
        self.assertEqual(first, "LIFE-PRESENTATION")
        self.assertEqual(second, "LIFE-PRESENTATION")
        self.assertEqual(assemble_seen, [True, True])
        self.assertEqual(assemble_charts, [F2_GANZHI, F2B_GANZHI])
        # Independent results: different births, different trims.
        self.assertNotEqual(first_trim, second_trim)
        self.assertEqual(
            [p['ganzhi'] for p in
             second_trim['chart']['pillars']],
            F2B_GANZHI)
        # Same birth twice is deterministic (same trim), but each
        # request recomputed it (two natal computations, no reuse
        # across requests).
        self.assert_no_retention()

    def test_same_life_birth_twice_is_deterministic(self):
        _, assemble_charts, captured, extra = self._life_patchers()
        for patcher in extra:
            patcher.start()
        try:
            build_life_presentation_for(F2_BIRTH, 2026)
            first_trim = copy.deepcopy(captured['life_trim'])
            build_life_presentation_for(F2_BIRTH, 2026)
            second_trim = copy.deepcopy(captured['life_trim'])
        finally:
            for patcher in reversed(extra):
                patcher.stop()
        self.assertEqual(first_trim, second_trim)
        self.assertEqual(assemble_charts, [F2_GANZHI, F2_GANZHI])
        self.assertEqual(len(self.natal_calls), 2)
        self.assert_no_retention()

    def test_life_wrapper_reuses_ambient_scope(self):
        assemble_seen, _, _, extra = self._life_patchers()
        for patcher in extra:
            patcher.start()
        try:
            with uc.unified_compute_request_scope():
                result = build_life_presentation_for(F2_BIRTH, 2026)
                # Reused, not nested: the assembly is still visible
                # in the ambient scope after the wrapper returns.
                self.assertEqual(assemble_seen, [True])
                info = uc.unified_compute_cache_info()
                self.assertEqual(info['core_entries'], 1)
        finally:
            for patcher in reversed(extra):
                patcher.stop()
        self.assertEqual(result, "LIFE-PRESENTATION")
        self.assert_no_retention()

    def test_life_wrapper_exception_evicts_scope(self):
        # The romance step fails after the direct assembly ran: the
        # scope must still be evicted, nothing retained.
        assemble_seen, _, _, extra = self._life_patchers(
            fail_romance=True)
        for patcher in extra:
            patcher.start()
        try:
            with self.assertRaises(RuntimeUnavailable):
                build_life_presentation_for(F2_BIRTH, 2026)
        finally:
            for patcher in reversed(extra):
                patcher.stop()
        self.assertEqual(assemble_seen, [True])
        self.assert_no_retention()


if __name__ == "__main__":
    unittest.main()
