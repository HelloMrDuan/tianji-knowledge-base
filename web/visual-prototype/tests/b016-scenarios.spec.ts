/**
 * B016 TJ-026.2: Scenario management renders real registry data + gate.
 *
 * Default mode (public CI): controlled synthetic HTTP contracts. The
 * /api/v1/scenarios stub below mirrors the PUBLIC backend registry values
 * verbatim (id/name/status/public_release/execution) so the gate logic is
 * exercised deterministically; the stub itself is synthetic and labeled.
 * Set B016_REAL_API=1 to skip all stubs and verify the same assertions
 * against a live backend (offline acceptance only).
 *
 * The page must never render DEMO fixture records, and publish clicks
 * must never issue a network request (there is no publish endpoint;
 * refusal and read-only notices are UI-only by design).
 */
import { test, expect } from "@playwright/test";

const REAL_API = process.env.B016_REAL_API === "1";

// Mirror of the public scenario registry (src/tianji_kb/scenario_engine.py).
const SCENARIOS = [
  { id: "bazi-profile", name: "八字基础档案", status: "production", public_release: true, execution: "scenario_api", depends_on: ["bazi/ziping-structural-v1"], scope: "" },
  { id: "question", name: "一事占问", status: "production", public_release: true, execution: "scenario_api", depends_on: ["liuyao/jingfang-eight-palaces-v1"], scope: "" },
  { id: "yearly", name: "年度结构", status: "production_limited", public_release: false, execution: "scenario_api", depends_on: ["bazi/ziping-structural-v1"], scope: "" },
  { id: "daily", name: "今日结构", status: "production_limited", public_release: false, execution: "scenario_api", depends_on: ["bazi.phase2.ten_gods"], scope: "" },
  { id: "weekly", name: "本周结构", status: "production_limited", public_release: false, execution: "scenario_api", depends_on: ["bazi.phase2.ten_gods"], scope: "" },
  { id: "monthly", name: "本月结构", status: "production_limited", public_release: false, execution: "scenario_api", depends_on: ["bazi.phase2.ten_gods"], scope: "" },
  { id: "romance", name: "桃花结构", status: "production_limited", public_release: false, execution: "scenario_api", depends_on: ["bazi/ziping-structural-v1"], scope: "" },
  { id: "career", name: "事业财运结构", status: "production_limited", public_release: false, execution: "scenario_api", depends_on: ["bazi.phase2.ten_gods"], scope: "" },
  { id: "compatibility", name: "缘分合盘结构", status: "production_limited", public_release: false, execution: "scenario_api", depends_on: ["bazi.phase2.ten_gods"], scope: "" },
  { id: "dream", name: "AI 解梦", status: "research", public_release: false, execution: null, depends_on: ["dream-rag", "ai"], scope: "" },
  { id: "life", name: "人生总览", status: "production_limited", public_release: false, execution: "scenario_api", depends_on: ["bazi-profile"], scope: "" },
];

const CAPABILITIES = {
  api_version: "v1",
  domains: [
    { domain: "bazi", variants: ["ziping-structural-v1"], default_variant: "ziping-structural-v1" },
    { domain: "liuyao", variants: ["jingfang-eight-palaces-v1"], default_variant: "jingfang-eight-palaces-v1" },
  ],
};

async function openScenarioPage(page) {
  if (!REAL_API) {
    await page.route("**/api/v1/scenarios", (route) =>
      route.fulfill({ status: 200, json: { api_version: "v1", scenarios: SCENARIOS } }),
    );
    await page.route("**/api/v1/capabilities", (route) =>
      route.fulfill({ status: 200, json: CAPABILITIES }),
    );
  }
  await page.goto("/admin/scenarios");
  await expect(page.locator("[data-scenario-id]")).toHaveCount(11);
}

test("scenario page lists all 11 real entries and no DEMO records", async ({ page }) => {
  await openScenarioPage(page);
  await expect(page.getByText("DEMO-", { exact: false })).toHaveCount(0);
  for (const entry of SCENARIOS) {
    const row = page.locator(`[data-scenario-id="${entry.id}"]`);
    await expect(row).toContainText(entry.name);
    await expect(row).toContainText(entry.status);
  }
});

test("gate passes production scenarios and fails the research dream scenario", async ({ page }) => {
  await openScenarioPage(page);
  const dreamRow = page.locator('[data-scenario-id="dream"]');
  await expect(dreamRow).toContainText("门禁未通过");
  await expect(dreamRow).toContainText("真实 API 已接通");
  const baziRow = page.locator('[data-scenario-id="bazi-profile"]');
  await expect(baziRow).toContainText("门禁通过");
  if (!REAL_API) {
    await expect(baziRow).toContainText("ziping-structural-v1");
  } else {
    // Real backend: variant value is live data, assert presence only.
    await expect(baziRow).not.toContainText("研究态");
  }
  await expect(dreamRow).toContainText("研究态");
});

test("publish on a gate-failed scenario refuses without any request", async ({ page }) => {
  const apiCalls: string[] = [];
  await openScenarioPage(page);
  page.on("request", (request) => {
    if (new URL(request.url()).pathname.startsWith("/api/")) {
      apiCalls.push(request.url());
    }
  });
  apiCalls.length = 0;
  await page.locator('[data-scenario-id="dream"] button', { hasText: "发布" }).click();
  await expect(page.locator('[data-scenario-id="dream"]')).toContainText("发布被门禁拒绝");
  expect(apiCalls).toEqual([]);
});

test("publish on a gate-passed scenario states read-only without any request", async ({ page }) => {
  const apiCalls: string[] = [];
  await openScenarioPage(page);
  page.on("request", (request) => {
    if (new URL(request.url()).pathname.startsWith("/api/")) {
      apiCalls.push(request.url());
    }
  });
  apiCalls.length = 0;
  await page.locator('[data-scenario-id="bazi-profile"] button', { hasText: "发布" }).click();
  await expect(page.locator('[data-scenario-id="bazi-profile"]')).toContainText("发布写入通道未接入");
  expect(apiCalls).toEqual([]);
});

test("scenario page has no horizontal overflow at 390px and 1280px", async ({ page }) => {
  await openScenarioPage(page);
  for (const width of [390, 1280]) {
    await page.setViewportSize({ width, height: 900 });
    const overflow = await page.evaluate(
      () => document.documentElement.scrollWidth > document.documentElement.clientWidth,
    );
    expect(overflow).toBe(false);
  }
});
