import { expect, test, type Page } from "@playwright/test";

/** Browser-side contract tests with controlled HTTP responses, NOT genuine calculations. */
async function saveSample(page: Page) {
  await page.goto("/bazi-profile");
  await page.getByRole("button", { name: "填入示例" }).click();
  await page.getByRole("button", { name: "保存资料" }).click();
  await expect.poll(() => page.evaluate(() => localStorage.getItem("tianji.profile.birth.v1"))).not.toBeNull();
}
function resultFor(id: string, target: string) {
  return {
    scenario_id: id, status: "success", public_release: true, deterministic: true,
    result: id === "yearly"
      ? { target_year: { year: Number(target), ganzhi: "丁未", stem: "丁", branch: "未",
          stem_ten_god: "食神", year_boundary: "solar-term year" },
          natal: { day_master: { stem: "甲" }, pillars: [] }, annual_branch_interactions: { hits: [] } }
      : { target_day: { date: target, ganzhi: "甲子", stem: "甲" },
          natal: { day_master: { stem: "甲" } }, xianchi: { target_day_activation: {} } },
    rule_matches: [], evidence: {}, trace: [], warnings: [], limitations: [],
  };
}

test("503 reviewed Chinese message and retry preserve birth inputs, clear old error", async ({ page }) => {
  await saveSample(page);
  const stored = await page.evaluate(() => localStorage.getItem("tianji.profile.birth.v1"));
  const sent: string[] = [];
  await page.route("**/api/v1/scenarios/public", async route => {
    const req = route.request().postDataJSON();
    expect(req.scenario_id).toBe("daily");
    sent.push(req.input.target_date);
    if (sent.length === 1) {
      await route.fulfill({ status: 503, contentType: "application/json",
        body: JSON.stringify({ detail: { message: "服务暂不可用" } }) });
    } else {
      await route.fulfill({ status: 200, contentType: "application/json",
        body: JSON.stringify(resultFor("daily", req.input.target_date)) });
    }
  });
  await page.goto("/daily-structure");
  await page.getByLabel("查看日期").fill("2026-10-15");
  const submit = page.locator('form button[type="submit"]').first();
  await submit.click();
  await expect(page.getByRole("alert")).toContainText("服务暂不可用");
  await expect(page.locator(".daily-result")).toHaveCount(0);
  await expect(page.getByLabel("出生日期")).toHaveValue("2000-01-07");
  await submit.click();
  await expect(page.locator(".daily-result-head")).toContainText("2026-10-15");
  await expect(page.getByRole("alert")).toHaveCount(0);
  expect(sent).toEqual(["2026-10-15", "2026-10-15"]);
  expect(await page.evaluate(() => localStorage.getItem("tianji.profile.birth.v1"))).toBe(stored);
});

test("plain-text 503 displays safe fallback, not upstream raw text or HTTP status", async ({ page }) => {
  await saveSample(page);
  let requests = 0;
  await page.route("**/api/v1/scenarios/public", async route => {
    requests++;
    await route.fulfill({ status: 503, body: "StackTrace internal /var/secret/token" });
  });
  await page.goto("/daily-structure");
  await page.locator('form button[type="submit"]').first().click();
  await expect(page.getByRole("alert")).toHaveText("服务暂时繁忙，请稍后重试。");
  await expect(page.locator(".daily-result")).toHaveCount(0);
  expect(requests).toBe(1);
});

for (const [name, body] of [["malformed JSON", "not json {{{"], ["HTTP 200 empty payload", "{}"]] as const) {
  test(`${name} is rejected and never produces a result`, async ({ page }) => {
    await saveSample(page);
    let requested = 0;
    await page.route("**/api/v1/scenarios/public", async route => {
      requested++;
      await route.fulfill({ status: 200, contentType: "application/json", body });
    });
    await page.goto("/daily-structure");
    await page.locator('form button[type="submit"]').first().click();
    await expect(page.getByRole("alert")).toContainText("服务端返回数据");
    await expect(page.locator(".daily-result")).toHaveCount(0);
    expect(requested).toBe(1);
  });
}

test("30-second deadline aborts an indefinitely pending request and permits retry", async ({ page }) => {
  await saveSample(page);
  await page.clock.install();
  let attempts = 0;
  await page.route("**/api/v1/scenarios/public", async route => {
    attempts++;
    if (attempts === 1) {
      // No fulfill/continue: browser-side AbortController must terminate this request.
      return;
    }
    const req = route.request().postDataJSON();
    await route.fulfill({ status: 200, contentType: "application/json",
      body: JSON.stringify(resultFor("daily", req.input.target_date)) });
  });
  await page.goto("/daily-structure");
  const submit = page.locator('form button[type="submit"]').first();
  await submit.click();
  await expect.poll(() => attempts).toBe(1);
  await page.clock.fastForward(30001);
  await expect(page.getByRole("alert")).toContainText("请求超时");
  await expect(submit).toBeEnabled();
  await submit.click();
  await expect(page.locator(".daily-result-head")).toBeVisible();
  await expect(page.getByRole("alert")).toHaveCount(0);
  expect(attempts).toBe(2);
});

test("service technical details are not copied into public alert", async ({ page }) => {
  await saveSample(page);
  let requested = 0;
  await page.route("**/api/v1/scenarios/public", async route => {
    requested++;
    await route.fulfill({ status: 500, contentType: "application/json",
      body: JSON.stringify({ detail: { message: "/home/service/src/runner.py trace token=private" } }) });
  });
  await page.goto("/daily-structure");
  await page.locator('form button[type="submit"]').first().click();
  await expect(page.getByRole("alert")).toHaveText("服务端出现问题，请稍后重试。");
  expect(requested).toBe(1);
});

test("saved lunar date survives navigation and leaves original lunar fields intact", async ({ page }) => {
  await page.goto("/bazi-profile");
  await page.getByRole("tab", { name: "农历" }).click();
  await page.locator(".birth-date-row select").nth(0).selectOption("2000");
  await page.locator(".birth-date-row select").nth(1).selectOption("4");
  await page.locator(".birth-date-row select").nth(2).selectOption("15");
  await page.locator(".time-selects select").nth(0).selectOption("12");
  await page.locator(".time-selects select").nth(1).selectOption("0");
  await page.getByRole("button", { name: "保存资料" }).click();
  const saved = await page.evaluate(() => JSON.parse(localStorage.getItem("tianji.profile.birth.v1") || "{}"));
  expect(saved).toMatchObject({ calendarType: "lunar", year: 2000, month: 4, day: 15, time: "12:00" });
  let solarDate = "";
  for (const route of ["/daily-structure", "/yearly-structure", "/romance-structure", "/career-wealth-structure", "/life-overview"]) {
    await page.goto(route);
    const visibleDate = await page.getByLabel("出生日期").inputValue();
    expect(visibleDate).toMatch(/^\d{4}-\d{2}-\d{2}$/);
    if (solarDate) expect(visibleDate).toBe(solarDate);
    else solarDate = visibleDate;
    await expect(page.getByLabel("出生时间")).toHaveValue("12:00");
    expect(await page.evaluate(() => JSON.parse(localStorage.getItem("tianji.profile.birth.v1") || "{}"))).toEqual(saved);
  }
});

test("target year is saved by actual successful yearly request and reused across three scenes", async ({ page }) => {
  await saveSample(page);
  const sent: number[] = [];
  await page.route("**/api/v1/scenarios/public", async route => {
    const req = route.request().postDataJSON();
    expect(req.scenario_id).toBe("yearly");
    sent.push(req.input.target_year);
    await route.fulfill({ status: 200, contentType: "application/json",
      body: JSON.stringify(resultFor("yearly", String(req.input.target_year))) });
  });
  await page.goto("/yearly-structure");
  await page.getByLabel("目标年份").fill("2027");
  await page.locator('form button[type="submit"]').first().click();
  await expect(page.locator(".yearly-result")).toBeVisible();
  expect(sent).toEqual([2027]);
  await expect.poll(() => page.evaluate(() => localStorage.getItem("tianji.scenario.target-year.v1"))).toBe("2027");
  for (const route of ["/romance-structure", "/career-wealth-structure", "/life-overview"]) {
    await page.goto(route);
    await expect(page.getByLabel("观察年份")).toHaveValue("2027");
  }
});
