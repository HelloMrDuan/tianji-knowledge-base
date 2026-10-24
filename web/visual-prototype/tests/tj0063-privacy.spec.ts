import { expect, test, type Page } from "@playwright/test";

/**
 * TJ-006.3 FRONTEND privacy/state tests. Intercepted responses are ONLY for
 * request-shape and asynchronous UI-state checks; NOT real backend calculations.
 */
const profileKey = "tianji.profile.birth.v1";
const apiBazi = "**/api/v1/public/execute";
const apiScenario = "**/api/v1/scenarios/public";

async function savePersonalProfile(page: Page) {
  await page.goto("/bazi-profile");
  await page.getByRole("button", { name: "填入示例" }).click();
  await page.getByRole("button", { name: "保存资料" }).click();
  await expect.poll(() => page.evaluate((k) => localStorage.getItem(k), profileKey)).not.toBeNull();
}

async function expectPersonalCleared(page: Page) {
  expect(await page.evaluate((k) => localStorage.getItem(k), profileKey)).toBeNull();
}

function previewCompatibilityResponse() {
  return {
    scenario_id: "compatibility",
    status: "success",
    deterministic: true,
    public_release: true,
    result: { person_a: {}, person_b: {}, day_master_relations: {},
      reviewed_cross_relations: {}, xianchi_cross_matches: {}, cross_relation_matrix: {},
      relation_evidence_matrix: [] },
    evidence: {}, rule_matches: [], trace: [], warnings: [], limitations: [],
  };
}

test("B name, birth date, time, region and role never overwrite personal A", async ({ page }) => {
  await savePersonalProfile(page);
  await page.goto("/compatibility-structure");
  const a = page.locator(".compat-person-input").nth(0);
  const b = page.locator(".compat-person-input").nth(1);
  await expect(a.locator('input[type="date"]')).toHaveValue("2000-01-07");
  await b.locator('input[type="date"]').fill("1995-06-20");
  await b.locator('input[type="time"]').fill("09:00");
  await b.locator("select").first().selectOption("英国");
  await b.locator('input:not([type])').fill("另一位");
  await b.locator("select").nth(1).selectOption("female");
  await expect(a.locator('input[type="date"]')).toHaveValue("2000-01-07");
  const saved = await page.evaluate((key) => JSON.parse(localStorage.getItem(key) || "{}"), profileKey);
  expect(saved).toMatchObject({ year: 2000, month: 1, day: 7, time: "12:00", region: "中国大陆" });
  expect(JSON.stringify(saved)).not.toContain("1995");
  expect(JSON.stringify(saved)).not.toContain("另一位");
});

test("real UI request uses different exact A and B instants and independent roles (stubbed response)", async ({ page }) => {
  await savePersonalProfile(page);
  let sent: Record<string, any> | null = null;
  await page.route(apiScenario, async route => {
    sent = route.request().postDataJSON();
    await route.fulfill({ status: 200, contentType: "application/json",
      body: JSON.stringify(previewCompatibilityResponse()) });
  });
  await page.goto("/compatibility-structure");
  const a = page.locator(".compat-person-input").nth(0);
  const b = page.locator(".compat-person-input").nth(1);
  await a.locator("select").last().selectOption("male");
  await b.locator('input[type="date"]').fill("1995-06-20");
  await b.locator('input[type="time"]').fill("09:00");
  await b.locator("select").first().selectOption("英国");
  await b.locator("select").last().selectOption("female");
  await page.locator('form button[type="submit"]').first().click();
  await expect.poll(() => sent).not.toBeNull();
  const input = (sent as any).input;
  expect(input.person_a_birth_value).toBe("2000-01-07T12:00:00+08:00");
  expect(input.person_b_birth_value).toBe("1995-06-20T09:00:00+01:00");
  expect(input.person_a_traditional_role).toBe("male");
  expect(input.person_b_traditional_role).toBe("female");
  const stored = await page.evaluate((key) => JSON.parse(localStorage.getItem(key) || "{}"), profileKey);
  expect(stored.year).toBe(2000);
});

test("clearing B resets all B fields and previously displayed result without touching A", async ({ page }) => {
  await savePersonalProfile(page);
  await page.route(apiScenario, async route => route.fulfill({ status: 200,
    contentType: "application/json", body: JSON.stringify(previewCompatibilityResponse()) }));
  await page.goto("/compatibility-structure");
  const a = page.locator(".compat-person-input").nth(0);
  const b = page.locator(".compat-person-input").nth(1);
  await b.locator('input[type="date"]').fill("1995-06-20");
  await b.locator('input[type="time"]').fill("09:00");
  await b.locator("select").first().selectOption("英国");
  await b.locator("select").last().selectOption("female");
  await page.locator('form button[type="submit"]').first().click();
  await expect(page.locator(".compat-result")).toBeVisible();
  await page.getByRole("button", { name: "清空对方资料" }).click();
  await expect(b.locator('input[type="date"]')).toHaveValue("");
  await expect(b.locator('input[type="time"]')).toHaveValue("");
  await expect(b.locator("select").first()).toHaveValue("中国大陆");
  await expect(b.locator("select").last()).toHaveValue("");
  await expect(page.locator(".compat-result")).toHaveCount(0);
  await expect(a.locator('input[type="date"]')).toHaveValue("2000-01-07");
  await page.reload();
  await expect(page.locator(".compat-person-input").nth(1).locator('input[type="date"]')).toHaveValue("");
});

test("clearing personal birth data empties form and keeps unrelated user preferences", async ({ page }) => {
  await savePersonalProfile(page);
  await page.evaluate(() => {
    localStorage.setItem("tianji.theme", "night-ink");
    localStorage.setItem("tianji.prototype.music", "off");
    localStorage.setItem("tianji.product.favorite", "true");
  });
  await page.getByRole("button", { name: "清除本机资料" }).click();
  await expectPersonalCleared(page);
  const date = page.locator(".birth-date-row select");
  await expect(date.nth(0)).toHaveValue("");
  await expect(date.nth(1)).toHaveValue("");
  await expect(page.locator(".bazi-live-result")).toHaveCount(0);
  const flags = await page.evaluate(() => ({
    theme: localStorage.getItem("tianji.theme"),
    music: localStorage.getItem("tianji.prototype.music"),
    favorite: localStorage.getItem("tianji.product.favorite"),
  }));
  expect(flags).toEqual({ theme: "night-ink", music: "off", favorite: "true" });
  await page.reload();
  await expectPersonalCleared(page);
});

test("deleted personal profile cannot reappear after navigating all birth-related scenarios", async ({ page }) => {
  await savePersonalProfile(page);
  await page.getByRole("button", { name: "清除本机资料" }).click();
  for (const route of [
    "/bazi-profile", "/daily-structure", "/weekly-structure", "/monthly-structure",
    "/yearly-structure", "/romance-structure", "/career-wealth-structure",
    "/compatibility-structure", "/life-overview",
  ]) {
    await page.goto(route);
    await expectPersonalCleared(page);
    if (route === "/bazi-profile") {
      await expect(page.locator(".birth-date-row select").first()).toHaveValue("");
    } else {
      await expect(page.locator('input[type="date"]').first()).toHaveValue("");
    }
  }
});

test("late bazi API response cannot revive a cleared profile or result", async ({ page }) => {
  await savePersonalProfile(page);
  let release!: () => void;
  const hold = new Promise<void>(resolve => { release = resolve; });
  let requests = 0;
  await page.route(apiBazi, async route => {
    requests += 1;
    await hold;
    await route.fulfill({ status: 200, contentType: "application/json",
      body: JSON.stringify({ chart: { pillars: [] }, evidence: {}, calendar: {}, variant: "test" }) });
  });
  await page.locator('form button[type="submit"]').first().click();
  await expect.poll(() => requests).toBe(1);
  await page.getByRole("button", { name: "清除本机资料" }).click();
  release();
  await expect(page.locator(".bazi-live-result")).toHaveCount(0);
  await expectPersonalCleared(page);
  await page.waitForTimeout(300); // permit delayed handler to finish before final assertion
  await expectPersonalCleared(page);
  await expect(page.locator(".bazi-live-result")).toHaveCount(0);
});

test("cross-tab deletion reloads active daily and compatibility screens, wiping cached A/B details", async ({ page, context }) => {
  await savePersonalProfile(page);
  const daily = await context.newPage();
  const compat = await context.newPage();
  await daily.goto("/daily-structure");
  await compat.goto("/compatibility-structure");
  await expect(daily.getByLabel("出生日期")).toHaveValue("2000-01-07");
  const a = compat.locator(".compat-person-input").nth(0);
  const b = compat.locator(".compat-person-input").nth(1);
  await expect(a.locator('input[type="date"]')).toHaveValue("2000-01-07");
  await b.locator('input[type="date"]').fill("1995-06-20");
  await b.locator('input[type="time"]').fill("09:00");
  const reloadDaily = daily.waitForEvent("load");
  const reloadCompat = compat.waitForEvent("load");
  await page.getByRole("button", { name: "清除本机资料" }).click();
  await Promise.all([reloadDaily, reloadCompat]);
  await expectPersonalCleared(daily);
  await expectPersonalCleared(compat);
  await expect(daily.getByLabel("出生日期")).toHaveValue("");
  await expect(compat.locator(".compat-person-input").nth(0).locator('input[type="date"]')).toHaveValue("");
  await expect(compat.locator(".compat-person-input").nth(1).locator('input[type="date"]')).toHaveValue("");
  await expect(compat.locator(".compat-result")).toHaveCount(0);
});

test("invalid counterpart cannot trigger an API request or overwrite personal A", async ({ page }) => {
  await savePersonalProfile(page);
  let requests = 0;
  await page.route(apiScenario, async route => { requests += 1; await route.abort(); });
  await page.goto("/compatibility-structure");
  const b = page.locator(".compat-person-input").nth(1);
  await b.locator('input[type="date"]').fill("1995-06-20");
  await b.locator('input[type="time"]').fill("09:00");
  await b.locator("select").first().selectOption("美国");
  await page.locator('form button[type="submit"]').first().click();
  await expect(page.getByRole("alert")).toContainText("横跨多个时区");
  expect(requests).toBe(0);
  const p = await page.evaluate(k => JSON.parse(localStorage.getItem(k) || "{}"), profileKey);
  expect(p.year).toBe(2000);
});


test("B006 counterpart consent notice states client-side and backend-retention boundaries", async ({ page }) => {
  await page.goto("/compatibility-structure");
  const notice = page.getByRole("note");
  await expect(notice).toContainText("请确保已获得对方知情同意");
  await expect(notice).toContainText("不会保存到本机浏览器");
  await expect(notice).toContainText("服务端留存以实际部署策略为准");
});
