import { test, expect } from "@playwright/test";

/** B012 / TJ-030.1: yijing home submit + result page against a REAL backend.
 * LOCAL CONTROLLED ACCEPTANCE ONLY: needs the assembled backend-debug
 * server on 127.0.0.1:8000 (public CI has no knowledge data, so it cannot
 * run this spec). NOT public-CI evidence. Run locally with the backend
 * server running:
 *   npx playwright test --workers=1 tests/b012-yijing.spec.ts
 * Asserts real computed hexagram names (never stubbed), no "尚未接入"
 * placeholder in the result area, and no horizontal overflow.
 */
test("yijing home submit renders real computed hexagrams", async ({ page }) => {
  await page.goto("/yijing");
  await page.getByRole("button", { name: "填入示例" }).click();
  // 样例：乾卦 + 初爻变
  await expect(page.locator("#field-hexagram")).toHaveValue("乾");
  await expect(page.locator("#field-line")).toHaveValue("初爻");
  await page.locator('form button[type="submit"]').first().click();
  const result = page.locator(".entry-result");
  await expect(result).toBeVisible();
  await expect(result).toContainText("乾为天");
  await expect(result).toContainText("天风姤");
  await expect(result).toContainText("坤为地");
  await expect(result).not.toContainText("尚未计算");
  await expect(result).not.toContainText("尚未接入");
});

test("yijing result page renders real hexagrams, no placeholder, no overflow", async ({
  page,
}) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto("/yijing/result?bits=111111&changing_lines=1");
  await expect(page.locator("body")).toContainText("乾为天");
  await expect(page.locator("body")).toContainText("天风姤");
  await expect(page.locator("body")).toContainText("坤为地");
  await expect(page.locator("body")).not.toContainText("实际结果尚未接入");
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
