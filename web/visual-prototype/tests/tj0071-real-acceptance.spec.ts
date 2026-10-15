import { expect, test, type Page } from "@playwright/test";

/**
 * TJ-007.1: live private-data-backed backend + real Chromium only.
 * Never fulfill or intercept API success. This test must run inside restricted private Actions.
 */
type Json = Record<string, any>;
const BIRTH_VALUE = "2000-01-07T12:00:00+08:00";
const LUNAR_VALUE = "2000-05-18T12:00:00+08:00";

async function savedSample(page: Page) {
  await page.goto("/bazi-profile");
  await page.getByRole("button", { name: "填入示例" }).click();
  await page.getByRole("button", { name: "保存资料" }).click();
}

async function liveSubmit(page: Page, path: string): Promise<{ request: Json; data: Json }> {
  const pending = page.waitForResponse(
    r => new URL(r.url()).pathname === path && r.request().method() === "POST",
    { timeout: 30_000 }
  );
  await page.locator('form button[type="submit"]').first().click();
  const response = await pending;
  expect(response.status(), "real HTTP response (no mock)").toBe(200);
  const request = response.request().postDataJSON() as Json;
  const data = await response.json() as Json;
  expect(data.deterministic).toBe(true);
  expect(data.evidence).toBeTruthy();
  return { request, data };
}

function verifyEvidence(data: Json) {
  expect(data.rule_matches).toEqual(expect.any(Array));
  expect(data.rule_matches.length).toBeGreaterThan(0);
  expect(data.evidence).toEqual(expect.any(Object));
  const sources = data.evidence as Json;
  // Every claimed rule-to-evidence reference must resolve in this actual response.
  for (const rule of data.rule_matches as Json[]) {
    for (const id of rule.evidence_ids || []) {
      expect(sources, "missing evidence reference " + id).toHaveProperty(id);
    }
  }
}

test("bazi: solar pillars, frontend display and reviewed Evidence", async ({ page }) => {
  await savedSample(page);
  const { request, data } = await liveSubmit(page, "/api/v1/public/execute");
  expect(request.domain).toBe("bazi");
  expect(request.input.value).toBe(BIRTH_VALUE);
  const pillars = data.chart?.pillars as Json[];
  expect(pillars).toEqual(expect.any(Array));
  expect(pillars.map(x => x.ganzhi)).toEqual(["己卯", "丁丑", "甲子", "庚午"]);
  verifyEvidence(data);
  const result = page.locator(".bazi-live-result");
  await expect(result).toBeVisible();
  await expect(result).toContainText("己卯");
  await expect(result).toContainText("甲子");
});

test("bazi: same birth moment entered in lunar calendar yields same chart", async ({ page }) => {
  await savedSample(page);
  const solar = await liveSubmit(page, "/api/v1/public/execute");
  await page.getByRole("tab", { name: "农历" }).click();
  await page.locator(".birth-date-row select").nth(0).selectOption("1999");
  await page.locator(".birth-date-row select").nth(1).selectOption("12");
  await page.locator(".birth-date-row select").nth(2).selectOption("1");
  await page.locator(".time-selects select").nth(0).selectOption("12");
  await page.locator(".time-selects select").nth(1).selectOption("0");
  const lunar = await liveSubmit(page, "/api/v1/public/execute");
  expect(lunar.request.input.value).toBe(BIRTH_VALUE);
  expect(lunar.data.chart.pillars).toEqual(solar.data.chart.pillars);
});

test("bazi: unknown birth hour never issues a calculation request", async ({ page }) => {
  await savedSample(page);
  await page.locator(".time-unknown-check input").check();
  const requests: string[] = [];
  page.on("request", r => {
    if (new URL(r.url()).pathname === "/api/v1/public/execute" && r.method() === "POST")
      requests.push(r.url());
  });
  await page.locator('form button[type="submit"]').first().click();
  await expect(page.getByRole("alert")).toContainText(/出生时刻未知/);
  expect(requests).toHaveLength(0);
  await expect(page.locator(".bazi-live-result")).toHaveCount(0);
});

test("daily: changing 查看日期 triggers two authentic distinct computations", async ({ page }) => {
  await savedSample(page);
  await page.goto("/daily-structure");
  for (const day of ["2026-10-15", "2026-10-16"]) {
    await page.getByLabel("查看日期").fill(day); // NOT the first date input: it is 出生日期!
    const { request, data } = await liveSubmit(page, "/api/v1/scenarios/public");
    expect(request.scenario_id).toBe("daily");
    expect(request.input.birth_value).toBe(BIRTH_VALUE);
    expect(request.input.target_date).toBe(day);
    expect(data.result.target_day.date).toBe(day);
    verifyEvidence(data);
    await expect(page.locator(".daily-result")).toContainText(day);
  }
});

test("weekly: real Monday/Sunday ranges and a December/January crossover", async ({ page }) => {
  await savedSample(page);
  await page.goto("/weekly-structure");
  for (const tc of [
    { anchor: "2026-10-15", start: "2026-10-12", end: "2026-10-18" },
    { anchor: "2025-12-31", start: "2025-12-29", end: "2026-01-04" },
  ]) {
    await page.getByLabel("本周参考日期").fill(tc.anchor);
    const { request, data } = await liveSubmit(page, "/api/v1/scenarios/public");
    expect(request.scenario_id).toBe("weekly");
    expect(request.input.anchor_date).toBe(tc.anchor);
    expect(request.input.birth_value).toBe(BIRTH_VALUE);
    expect(data.result.week.start_date).toBe(tc.start);
    expect(data.result.week.end_date).toBe(tc.end);
    expect(data.result.week.days).toHaveLength(7);
    verifyEvidence(data);
    await expect(page.locator(".period-result")).toContainText(tc.start);
    await expect(page.locator(".period-result")).toContainText(tc.end);
  }
});

test("monthly: leap February, ordinary February and displayed day count", async ({ page }) => {
  await savedSample(page);
  await page.goto("/monthly-structure");
  for (const tc of [
    { month: "2024-02", days: 29 },
    { month: "2025-02", days: 28 },
    { month: "2026-10", days: 31 },
  ]) {
    await page.getByLabel("查看月份").fill(tc.month);
    const { request, data } = await liveSubmit(page, "/api/v1/scenarios/public");
    expect(request.scenario_id).toBe("monthly");
    expect(request.input.target_month).toBe(tc.month);
    expect(request.input.birth_value).toBe(BIRTH_VALUE);
    expect(data.result.month.target_month).toBe(tc.month);
    expect(data.result.month.day_count).toBe(tc.days);
    expect(data.result.month.days).toHaveLength(tc.days);
    verifyEvidence(data);
    await expect(page.locator(".period-result")).toContainText(tc.month);
    await expect(page.locator(".period-result .period-days article")).toHaveCount(tc.days);
  }
});

test("yearly: explicit year selection recomputes from real rules and displays the year", async ({ page }) => {
  await savedSample(page);
  await page.goto("/yearly-structure");
  const seen: string[] = [];
  for (const year of [2025, 2026, 2027]) {
    await page.getByLabel("目标年份").fill(String(year));
    const { request, data } = await liveSubmit(page, "/api/v1/scenarios/public");
    expect(request.scenario_id).toBe("yearly");
    expect(request.input.birth_value).toBe(BIRTH_VALUE);
    expect(request.input.target_year).toBe(year);
    expect(data.result.target_year.year).toBe(year);
    expect(data.result.target_year.year_boundary).toContain("solar-term");
    seen.push(data.result.target_year.ganzhi);
    verifyEvidence(data);
    await expect(page.locator(".yearly-result")).toContainText(String(year));
    await expect(page.locator(".yearly-result")).toContainText(data.result.target_year.ganzhi);
  }
  expect(new Set(seen).size).toBe(3);
});

test("lunar stored once: all five API birth values match; original lunar survives", async ({ page }) => {
  await page.goto("/bazi-profile");
  await page.getByRole("tab", { name: "农历" }).click();
  await page.locator(".birth-date-row select").nth(0).selectOption("2000");
  await page.locator(".birth-date-row select").nth(1).selectOption("4");
  await page.locator(".birth-date-row select").nth(2).selectOption("15");
  await page.locator(".time-selects select").nth(0).selectOption("12");
  await page.locator(".time-selects select").nth(1).selectOption("0");
  await page.getByRole("button", { name: "保存资料" }).click();
  const natal = await liveSubmit(page, "/api/v1/public/execute");
  expect(natal.request.input.value).toBe(LUNAR_VALUE);

  for (const [route, id] of [
    ["/daily-structure", "daily"],
    ["/weekly-structure", "weekly"],
    ["/monthly-structure", "monthly"],
    ["/yearly-structure", "yearly"],
  ]) {
    await page.goto(route);
    const { request, data } = await liveSubmit(page, "/api/v1/scenarios/public");
    expect(request.scenario_id).toBe(id);
    expect(request.input.birth_value).toBe(LUNAR_VALUE);
    expect(data.scenario_id).toBe(id);
    verifyEvidence(data);
  }
  await page.goto("/bazi-profile");
  await expect(page.getByRole("tab", { name: "农历" })).toHaveAttribute("aria-selected", "true");
  const saved = await page.evaluate(() => JSON.parse(localStorage.getItem("tianji.profile.birth.v1") || "{}"));
  expect(saved.calendarType).toBe("lunar");
  expect(saved.year).toBe(2000);
  expect(saved.month).toBe(4);
  expect(saved.day).toBe(15);
  expect(saved.time).toBe("12:00");
});

test("result remains readable on narrow mobile after live API computation", async ({ page }) => {
  await page.setViewportSize({ width: 360, height: 780 });
  await savedSample(page);
  await page.goto("/daily-structure");
  const { data } = await liveSubmit(page, "/api/v1/scenarios/public");
  await expect(page.locator(".daily-result")).toBeVisible();
  await expect(page.locator(".daily-result")).toContainText(data.result.target_day.ganzhi);
});
