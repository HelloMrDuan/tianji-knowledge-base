import { test, expect } from "@playwright/test";

/** B014 / TJ-030.5: fengshui home submit + result page against a REAL backend.
 * LOCAL CONTROLLED ACCEPTANCE ONLY: needs the assembled backend-debug
 * server on 127.0.0.1:8000 (public CI has no knowledge data, so it cannot
 * run this spec). NOT public-CI evidence. Run locally with the backend
 * server running:
 *   npx playwright test --workers=1 tests/b014-fengshui.spec.ts
 * Asserts real computed mountain/trigram/opposite (never stubbed), the
 * absolute-period production refusal, no "尚未接入" placeholder in the
 * result area, and no horizontal overflow.
 */
test("fengshui home submit renders real computed mountain and facing", async ({
  page,
}) => {
  await page.goto("/fengshui");
  await page.getByRole("button", { name: "填入示例" }).click();
  // 样例：测量角度 180°
  await expect(page.locator("#field-bearing")).toHaveValue("180");
  await page.locator('form button[type="submit"]').first().click();
  const result = page.locator(".entry-result");
  await expect(result).toBeVisible();
  await expect(result).toContainText("180°");
  await expect(result).toContainText("午（火）");
  await expect(result).toContainText("离（火）");
  await expect(result).toContainText("绝对元运未接入生产");
  await expect(result).not.toContainText("尚未计算");
  await expect(result).not.toContainText("尚未接入");
});

test("fengshui result page renders real chart, no placeholder, no overflow", async ({
  page,
}) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto("/fengshui/result?degrees=180");
  await expect(page.locator("body")).toContainText("180°");
  await expect(page.locator("body")).toContainText("午（火）");
  await expect(page.locator("body")).toContainText("对向 子");
  await expect(page.locator("body")).toContainText("绝对元运未接入生产");
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
