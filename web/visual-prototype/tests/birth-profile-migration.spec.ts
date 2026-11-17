import { test, expect } from "@playwright/test";

/**
 * Line B (E0404 follow-up): independent negative cases for the birth-profile
 * migration in readSavedBirthProfile (birthProfile.ts).
 *
 * E0404 added isPlausibleDateTime so a malformed LEGACY value is rejected
 * instead of prefilling the form with an impossible date/time. These tests
 * pin that behavior at the real page level (prefill), not with mocks:
 *
 * (a) legacy old-format with an impossible date (2000-02-30) -> rejected.
 * (b) legacy old-format with an impossible time (25:99) -> rejected.
 * (c) legacy old-format with a valid date/time but an unknown timezone ->
 *     still loads (form prefilled) with _regionNeedsConfirm: the guard must
 *     NOT reject it; the page shows the region-confirm box instead and
 *     blocks calculation until the user confirms.
 * (d) new-format with an impossible date/time -> rejected by
 *     validateBirthInput (already the case before E0404; verified here).
 *
 * Each test loads at most 2 pages (local test browser exhausts resources
 * after ~4-5 page loads in one session).
 */

const profileKey = "tianji.profile.birth.v1";

async function setProfile(page: import("@playwright/test").Page, value: string) {
  await page.goto("/");
  await page.evaluate((args) => localStorage.setItem(args.key, args.value), { key: profileKey, value });
}

async function expectBaziEmpty(page: import("@playwright/test").Page) {
  await page.goto("/bazi-profile");
  await expect(page.locator(".birth-date-row select").nth(0)).toHaveValue("");
  await expect(page.locator(".birth-date-row select").nth(1)).toHaveValue("");
  await expect(page.locator(".birth-date-row select").nth(2)).toHaveValue("");
}

test("(a) legacy old-format with an impossible date is rejected", async ({ page }) => {
  await setProfile(page, '{"date":"2000-02-30","time":"12:00"}');
  await expectBaziEmpty(page);
});

test("(b) legacy old-format with an impossible time is rejected", async ({ page }) => {
  await setProfile(page, '{"date":"2000-01-07","time":"25:99"}');
  await expectBaziEmpty(page);
});

test("(c) legacy old-format with a valid date/time but unknown timezone still loads with region confirm", async ({ page }) => {
  await setProfile(page, '{"date":"2000-01-07","time":"12:00"}');
  await page.goto("/bazi-profile");
  // The profile loads (form prefilled) — the guard must not reject it.
  await expect(page.locator(".birth-date-row select").nth(0)).toHaveValue("2000");
  await expect(page.locator(".birth-date-row select").nth(1)).toHaveValue("1");
  await expect(page.locator(".birth-date-row select").nth(2)).toHaveValue("7");
  // But calculation is blocked until the region is confirmed.
  await expect(page.locator(".region-confirm-box")).toBeVisible();
  await expect(page.locator(".region-confirm-box")).toContainText("缺少出生地区信息");
  await expect(page.getByRole("button", { name: /确认出生地区/ })).toBeVisible();
  // The block is real, not just a banner: submitting must fail validation
  // with the region-confirm message and produce no result (no API call).
  // Two .question-error elements render the same message (form area +
  // result area, pre-existing page structure); .first() disambiguates
  // Playwright strict mode without weakening the check — both carry it.
  await page.getByRole("button", { name: "生成基础档案" }).click();
  await expect(page.locator(".question-error").first()).toContainText("请先在八字命理页面确认出生地区");
  await expect(page.locator(".bazi-live-result")).toHaveCount(0);
});

test("(d) new-format with an impossible date/time is rejected", async ({ page }) => {
  await setProfile(page, JSON.stringify({
    calendarType: "solar", year: 2000, month: 2, day: 30,
    isLeapMonth: false, time: "12:00", timeUnknown: false, region: "中国大陆",
  }));
  await expectBaziEmpty(page);
  await setProfile(page, JSON.stringify({
    calendarType: "solar", year: 2000, month: 1, day: 7,
    isLeapMonth: false, time: "25:99", timeUnknown: false, region: "中国大陆",
  }));
  await expectBaziEmpty(page);
});
