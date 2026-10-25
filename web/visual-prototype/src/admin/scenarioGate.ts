/**
 * Scenario publish-gate tables and evaluation (TJ-026.2).
 *
 * The tables below are REVIEWED code claims, not live data: each one is
 * verified by tests/test_b016_scenario_gate_table.py in public CI, which
 * asserts (a) every registry scenario id has a table entry, (b) every
 * route in SCENARIO_ROUTES exists in the public frontend router, and
 * (c) every spec file in SCENARIO_KEY_TESTS exists in tests/. A scenario
 * whose page or test is removed must update its table entry, or CI fails.
 *
 * Live inputs (status, execution) always come from /api/v1/scenarios at
 * runtime; nothing about a scenario's readiness is hardcoded here beyond
 * the three reviewed facts above.
 */

export type ScenarioRegistryEntry = {
  id: string;
  name: string;
  status: string;
  public_release: boolean;
  execution: string | null;
  depends_on: string[];
  scope: string;
};

/** Frontend route for each scenario id (the 11 real product routes). */
export const SCENARIO_ROUTES: Record<string, string> = {
  "bazi-profile": "/bazi-profile",
  question: "/ask",
  yearly: "/yearly-structure",
  daily: "/daily-structure",
  weekly: "/weekly-structure",
  monthly: "/monthly-structure",
  romance: "/romance-structure",
  career: "/career-wealth-structure",
  compatibility: "/compatibility-structure",
  dream: "/dream-culture",
  life: "/life-overview",
};

/** Primary engine domain per scenario, for variant display. Dream has no
 * engine domain (research state) and is intentionally absent. */
export const SCENARIO_DOMAINS: Record<string, string> = {
  "bazi-profile": "bazi",
  question: "liuyao",
  yearly: "bazi",
  daily: "bazi",
  weekly: "bazi",
  monthly: "bazi",
  romance: "bazi",
  career: "bazi",
  compatibility: "bazi",
  life: "bazi",
};

/**
 * Whether the scenario has a dedicated real result page (not the
 * "实际结果尚未接入" placeholder). All 11 do today; the route regression
 * specs assert no scenario page renders placeholder copy.
 */
export const SCENARIO_REAL_PAGES: Record<string, boolean> = {
  "bazi-profile": true,
  question: true,
  yearly: true,
  daily: true,
  weekly: true,
  monthly: true,
  romance: true,
  career: true,
  compatibility: true,
  dream: true,
  life: true,
};

/** Key browser specs covering each scenario (files must exist in tests/). */
export const SCENARIO_KEY_TESTS: Record<string, string[]> = {
  "bazi-profile": ["birth-profile.spec.ts", "birth-profile-reuse.spec.ts"],
  question: ["guided-coin-casting.spec.ts", "tj-007.1-requests.spec.ts"],
  yearly: ["flow-year-label-consistency.spec.ts", "selectable-flow-year.spec.ts"],
  daily: ["tj004-all-scenarios-real-api.spec.ts"],
  weekly: ["tj004-all-scenarios-real-api.spec.ts"],
  monthly: ["tj004-all-scenarios-real-api.spec.ts"],
  romance: ["tj004-all-scenarios-real-api.spec.ts"],
  career: ["b005-career-e2e.spec.ts", "career-annual-reading.spec.ts"],
  compatibility: ["compatibility-result-consistency.spec.ts", "b006-privacy.spec.ts"],
  dream: ["public-dream-culture.spec.ts", "dream-reviewed-explorer.spec.ts"],
  life: ["b007-life.spec.ts", "life-strength-integration.spec.ts"],
};

export type GateItem = {
  key: "route" | "api" | "page" | "tests";
  label: string;
  passed: boolean;
  detail: string;
};

export type GateResult = {
  passed: boolean;
  items: GateItem[];
};

/**
 * Evaluate the publish gate for one scenario. All four items must pass:
 * real route, real API execution, real result page, key tests on file.
 * The gate never fabricates readiness: a research-state scenario (dream)
 * fails the API item by its live execution value, not by opinion.
 */
export function evaluateScenarioGate(scenario: ScenarioRegistryEntry): GateResult {
  const route = SCENARIO_ROUTES[scenario.id];
  const keyTests = SCENARIO_KEY_TESTS[scenario.id] ?? [];
  const items: GateItem[] = [
    {
      key: "route",
      label: "真实路由存在",
      passed: typeof route === "string" && route.length > 0,
      detail: route ? `前台路由 ${route}` : "未登记前台路由",
    },
    {
      key: "api",
      label: "真实 API 已接通",
      passed:
        scenario.execution === "scenario_api" &&
        (scenario.status === "production" || scenario.status === "production_limited"),
      detail: `执行 ${scenario.execution ?? "无"} · 状态 ${scenario.status}`,
    },
    {
      key: "page",
      label: "结果页真实",
      passed: SCENARIO_REAL_PAGES[scenario.id] === true,
      detail: SCENARIO_REAL_PAGES[scenario.id] === true
        ? "专用结果页，非占位"
        : "结果页仍为占位或未登记",
    },
    {
      key: "tests",
      label: "关键测试在册",
      passed: keyTests.length > 0,
      detail: keyTests.length > 0 ? keyTests.join("、") : "未登记关键测试",
    },
  ];
  return { passed: items.every((item) => item.passed), items };
}
