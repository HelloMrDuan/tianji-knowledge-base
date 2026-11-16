import { test, expect, type Page } from "@playwright/test";

const profileKey = "tianji.profile.birth.v1";

/**
 * E0404 (TJ-029.1): birth-profile regression tests updated to the current
 * verified product contract.
 *
 * - /bazi-profile uses BirthInputFields (year/month/day dropdowns + hour/
 *   minute selects), NOT a native date input, so getByLabel("出生日期")
 *   cannot find an element there. Other result pages use native date/time
 *   inputs and keep the "出生日期" / "出生时间" labels.
 * - localStorage now stores the structured profile
 *   {calendarType, year, month, day, isLeapMonth, time, timeUnknown, region}
 *   (the old {"date","time"} shape was replaced when lunar/leap/region
 *   support landed). Tests assert the parsed fields, not the old string.
 * - .bazi-rule-evidence lives inside the collapsed "专业审计视图" details;
 *   the test expands it first (evidence is present, just collapsed by design).
 * - Each test loads at most 4 pages: the local test browser exhausts
 *   resources after ~4-5 page loads in one session
 *   (net::ERR_INSUFFICIENT_RESOURCES / blank render), so the reuse checks
 *   are split by page group and each test redoes the bazi-profile setup.
 *   CI runs the same assertions.
 *
 * Real-backend behaviour behind these tests was verified by hand on
 * 2026-11-16 (main 764b442): profile reuse prefills yearly/romance/career
 * with 2000-01-07 / 12:00; lunar time change to 14:30 is saved after a real
 * backend submit; malformed local values are rejected and prefill nothing.
 */

async function expectBaziDropdowns(page: Page, year: string, month: string, day: string) {
  await expect(page.locator(".birth-date-row select").nth(0)).toHaveValue(year);
  await expect(page.locator(".birth-date-row select").nth(1)).toHaveValue(month);
  await expect(page.locator(".birth-date-row select").nth(2)).toHaveValue(day);
}

async function setupSampleProfile(page: Page) {
  await page.goto("/bazi-profile");
  await expectBaziDropdowns(page, "", "", "");
  await page.getByRole("button", { name: "填入示例" }).click();
  await expectBaziDropdowns(page, "2000", "1", "7");
  await page.getByRole("button", { name: "生成基础档案" }).click();
  await expect(page.locator(".bazi-live-result")).toBeVisible({ timeout: 30000 });
  await expect(page.locator(".bazi-pillars article")).toHaveCount(4);
  const saved = await page.evaluate((key) => JSON.parse(localStorage.getItem(key) || "null"), profileKey);
  expect(saved).toMatchObject({ calendarType: "solar", year: 2000, month: 1, day: 7, time: "12:00" });
}

async function expectBirthPrefill(page: Page, route: string, submitLabel: string) {
  await page.goto(route);
  await expect(page.getByLabel("出生日期")).toHaveValue("2000-01-07");
  await expect(page.getByLabel("出生时间")).toHaveValue("12:00");
  await expect(page.getByRole("button", { name: submitLabel })).toBeVisible();
}

async function expectBirthEmpty(page: Page, route: string) {
  await page.goto(route);
  await expect(page.getByLabel("出生日期")).toHaveValue("");
  await expect(page.getByLabel("出生时间")).toHaveValue("");
}

async function setMalformedProfile(page: Page) {
  await page.goto("/");
  await page.evaluate((key) => localStorage.setItem(key,
    '{"date":"2000-02-30","time":"25:99"}'), profileKey);
  const apiRequests: string[] = [];
  page.on("request", (request) => {
    if (new URL(request.url()).pathname.startsWith("/api/")) apiRequests.push(request.url());
  });
  return apiRequests;
}

test("real Bazi API establishes browser-local profile reused by yearly romance and career", async ({ page }) => {
  await setupSampleProfile(page);
  await expectBirthPrefill(page, "/yearly-structure", "查看 2026 流年结构");
  await expectBirthPrefill(page, "/romance-structure", "查看桃花结构");
  await expectBirthPrefill(page, "/career-wealth-structure", "查看事业财运结构");
});

test("real Bazi API establishes browser-local profile reused by daily weekly and monthly", async ({ page }) => {
  await setupSampleProfile(page);
  await expectBirthPrefill(page, "/daily-structure", "查看今日结构");
  await expectBirthPrefill(page, "/weekly-structure", "查看本周结构");
  await expectBirthPrefill(page, "/monthly-structure", "查看本月结构");
});

test("browser-local profile is reused by compatibility and clearing it empties the pages", async ({ page }) => {
  await setupSampleProfile(page);
  await page.goto("/compatibility-structure");
  await expect(page.locator(".compat-person-input").first().locator('input[type="date"]')).toHaveValue("2000-01-07");
  await expect(page.locator(".compat-person-input").first().locator('input[type="time"]')).toHaveValue("12:00");
  await page.goto("/bazi-profile");
  await expectBaziDropdowns(page, "2000", "1", "7");
  await page.getByRole("button", { name: "清除本机资料" }).click();
  await expectBaziDropdowns(page, "", "", "");
  expect(await page.evaluate((key) => localStorage.getItem(key), profileKey)).toBeNull();
  await expectBirthEmpty(page, "/yearly-structure");
});

test("stale or malformed local values do not prefill bazi yearly romance", async ({ page }) => {
  const apiRequests = await setMalformedProfile(page);
  await page.goto("/bazi-profile");
  await expectBaziDropdowns(page, "", "", "");
  await expectBirthEmpty(page, "/yearly-structure");
  await expectBirthEmpty(page, "/romance-structure");
  expect(apiRequests).toEqual([]);
});

test("stale or malformed local values do not prefill career daily weekly", async ({ page }) => {
  const apiRequests = await setMalformedProfile(page);
  await expectBirthEmpty(page, "/career-wealth-structure");
  await expectBirthEmpty(page, "/daily-structure");
  await expectBirthEmpty(page, "/weekly-structure");
  expect(apiRequests).toEqual([]);
});

test("stale or malformed local values do not prefill monthly compatibility", async ({ page }) => {
  const apiRequests = await setMalformedProfile(page);
  await expectBirthEmpty(page, "/monthly-structure");
  await page.goto("/compatibility-structure");
  await expect(page.locator(".compat-person-input").first().locator('input[type="date"]')).toHaveValue("");
  await expect(page.locator(".compat-person-input").first().locator('input[type="time"]')).toHaveValue("");
  expect(apiRequests).toEqual([]);
});

test("Bazi basic chart cites actual verified classical text per executed rule", async ({ page }) => {
  await page.goto("/bazi-profile");
  await page.getByRole("button", { name: "填入示例" }).click();
  await page.getByRole("button", { name: "生成基础档案" }).click();
  await expect(page.locator(".bazi-live-result")).toBeVisible({ timeout: 30000 });
  // Rule evidence lives inside the collapsed "专业审计视图" details.
  await page.locator(".bazi-audit-details > summary").click();
  const rules = page.locator(".bazi-rule-evidence");
  await expect(rules.first()).toBeVisible();
  const citations = rules.locator("details");
  await expect(citations.first()).toBeVisible();
  await citations.first().locator("summary").click();
  await expect(citations.first().locator("blockquote b").first()).toContainText("证据等级");
  await expect(citations.first().locator("blockquote p").first()).not.toBeEmpty();
  await expect(page.locator(".bazi-live-result")).not.toContainText("该证据已由后端绑定到本次确定性结果");
});
