import { test, expect } from "@playwright/test";

/** TJ-004.2: this suite MUST run against a live private-data-backed API.
 * Never install page.route() mocks for a green report.
 */
const SCENARIOS = [
  { route: "/bazi-profile", id: "bazi", endpoint: "/api/v1/public/execute", result: ".bazi-live-result", mode: "sample" },
  { route: "/daily-structure", id: "daily", endpoint: "/api/v1/scenarios/public", result: ".daily-result", mode: "sample" },
  { route: "/weekly-structure", id: "weekly", endpoint: "/api/v1/scenarios/public", result: ".period-result", mode: "weekly" },
  { route: "/monthly-structure", id: "monthly", endpoint: "/api/v1/scenarios/public", result: ".period-result", mode: "monthly" },
  { route: "/yearly-structure", id: "yearly", endpoint: "/api/v1/scenarios/public", result: ".yearly-result", mode: "sample" },
  { route: "/romance-structure", id: "romance", endpoint: "/api/v1/scenarios/public", result: ".romance-result", mode: "sample" },
  { route: "/career-wealth-structure", id: "career", endpoint: "/api/v1/scenarios/public", result: ".career-result", mode: "sample" },
  { route: "/compatibility-structure", id: "compatibility", endpoint: "/api/v1/scenarios/public", result: ".compat-result", mode: "compatibility" },
  { route: "/ask", id: "liuyao", endpoint: "/api/v1/public/execute", result: ".live-result", mode: "question" },
  { route: "/dream-culture", id: "dream", endpoint: "/api/v1/dream/culture", result: ".dream-culture-match", mode: "dream" },
  { route: "/life-overview", id: "life", endpoint: "/api/v1/scenarios/public", result: ".life-result", mode: "sample" },
] as const;

async function provideRealInput(page: import("@playwright/test").Page, mode: typeof SCENARIOS[number]["mode"]) {
  if (mode === "sample") {
    await page.getByRole("button", { name: "填入示例", exact: true }).click();
    return;
  }
  if (mode === "weekly" || mode === "monthly") {
    await page.getByLabel("出生日期").fill("2000-01-07");
    await page.getByLabel("出生时间").fill("12:00");
    if (mode === "weekly") await page.getByLabel("本周参考日期").fill("2026-10-04");
    else await page.getByLabel("查看月份").fill("2026-10");
    return;
  }
  if (mode === "compatibility") {
    await page.getByRole("button", { name: "填入双人示例" }).click();
    return;
  }
  if (mode === "question") {
    await page.getByPlaceholder("例如：现在这个工作机会，我是否适合继续推进？")
      .fill("这件工作选择有什么可核验的结构参考？");
    await page.getByLabel("起卦日期").fill("2026-10-09");
    await page.getByLabel("起卦时间", { exact: true }).fill("17:30");
    await page.getByRole("button", { name: "一次投完六次" }).click();
    return;
  }
  await page.getByRole("button", { name: "填入蛇咬梦境示例" }).click();
}

for (const item of SCENARIOS) {
  test(`TJ-004.2 real private API: ${item.id} scenario submits from its actual user page`, async ({ page }) => {
    const requested: string[] = [];
    page.on("request", r => {
      if (new URL(r.url()).pathname === item.endpoint && r.method() === "POST")
        requested.push(r.url());
    });

    await page.goto(item.route);
    await expect(page.locator("main h1")).toBeVisible();
    expect(requested).toHaveLength(0); // Opening a page is not submitting a personal record.
    await provideRealInput(page, item.mode);
    const responsePromise = page.waitForResponse(r =>
      new URL(r.url()).pathname === item.endpoint && r.request().method() === "POST");
    await page.locator('form button[type="submit"]').click();
    const response = await responsePromise;
    expect(response.status(), `Actual ${item.id} backend returned ${response.status()}`).toBe(200);
    const sent = response.request().postDataJSON();
    if (item.endpoint === "/api/v1/scenarios/public") {
      expect(sent.scenario_id).toBe(item.id);
    } else if (item.endpoint === "/api/v1/public/execute") {
      expect(sent.domain).toBe(item.id);
      expect(sent.explain).toBe(false);
    } else {
      expect(typeof sent.dream_text).toBe("string");
    }

    const data = await response.json();
    if (item.id === "dream") {
      expect(data.ai_enabled).toBe(false);
      expect(data.cultural_reference_only).toBe(true);
      expect(data.matches.length).toBeGreaterThan(0);
    } else if (item.endpoint === "/api/v1/scenarios/public") {
      expect(data.scenario_id).toBe(item.id);
      expect(data.deterministic).toBe(true);
      expect(data.evidence).toEqual(expect.any(Object));
      expect(data.rule_matches).toEqual(expect.any(Array));
    } else {
      expect(data.domain).toBe(item.id);
      expect(data.deterministic).toBe(true);
      expect(data.evidence).toEqual(expect.any(Object));
    }
    await expect(page.locator(item.result).first()).toBeVisible();
    expect(requested).toHaveLength(1);
  });
}

test("TJ-004.3 invalid natal date is rejected before a real backend request", async ({ page }) => {
  const apiRequests: string[] = [];
  page.on("request", r => { if (new URL(r.url()).pathname.startsWith("/api/")) apiRequests.push(r.url()); });
  await page.goto("/bazi-profile");
  // Birth date via dropdowns (年/月/日); leave time (时/分) unselected.
  // The UI uses explicit dropdowns per the birth-time input contract (no text inputs).
  await page.getByLabel("年").selectOption("2000");
  await page.getByLabel("月").selectOption("1");
  await page.locator('select').nth(2).selectOption('7'); // day dropdown (年=0, 月=1, 日=2)
  await page.getByRole("button", { name: "生成基础档案" }).click();
  await expect(page.locator(".bazi-live-result")).toHaveCount(0);
  expect(apiRequests).toHaveLength(0);
});
