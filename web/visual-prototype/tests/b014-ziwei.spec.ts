import { test, expect } from "@playwright/test";

/** B014 / TJ-030.2: ziwei home submit + result page against a REAL backend.
 * LOCAL CONTROLLED ACCEPTANCE ONLY: needs the assembled backend-debug
 * server on 127.0.0.1:8000 (public CI has no knowledge data, so it cannot
 * run this spec). NOT public-CI evidence. Run locally with the backend
 * server running:
 *   npx playwright test --workers=1 tests/b014-ziwei.spec.ts
 * Asserts real computed palaces/stars/transformations (never stubbed),
 * no "尚未接入" placeholder in the result area, and no horizontal overflow.
 */
test("ziwei home submit renders real computed palaces and transformations", async ({
  page,
}) => {
  await page.goto("/ziwei");
  await page.getByRole("button", { name: "填入示例" }).click();
  // 样例：1996-05-18 09:30（农历 1996-04-02 巳时，丙子年）
  await expect(page.locator("#field-date")).toHaveValue("1996-05-18");
  await expect(page.locator("#field-time")).toHaveValue("09:30");
  await page.locator('form button[type="submit"]').first().click();
  const result = page.locator(".entry-result");
  await expect(result).toBeVisible();
  await expect(result).toContainText("庚子");
  await expect(result).toContainText("土5局");
  await expect(result).toContainText("命宫→子");
  await expect(result).toContainText("紫微→亥");
  await expect(result).toContainText("化禄→天同");
  await expect(result).toContainText("无大限流年");
  await expect(result).not.toContainText("尚未计算");
  await expect(result).not.toContainText("尚未接入");
});

test("ziwei result page renders real chart, no placeholder, no overflow", async ({
  page,
}) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto(
    "/ziwei/result?value=1996-05-18T09%3A30%3A00%2B08%3A00&year_boundary=lunar-new-year",
  );
  await expect(page.locator("body")).toContainText("土5局");
  await expect(page.locator("body")).toContainText("紫微→亥");
  await expect(page.locator("body")).toContainText("化禄→天同");
  await expect(page.locator("body")).toContainText("无大限流年");
  await expect(page.locator(".template-chart")).not.toContainText("尚未接入");
  await expect
    .poll(() =>
      page.evaluate(
        () =>
          document.documentElement.scrollWidth <=
          document.documentElement.clientWidth,
      ),
    )
    .toBe(true);
  await page.setViewportSize({ width: 1280, height: 800 });
  await expect
    .poll(() =>
      page.evaluate(
        () =>
          document.documentElement.scrollWidth <=
          document.documentElement.clientWidth,
      ),
    )
    .toBe(true);
});
