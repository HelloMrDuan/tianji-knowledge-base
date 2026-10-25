import { test, expect } from "@playwright/test";

/** B012 / TJ-030.4: liuren home submit + result page against a REAL backend.
 * LOCAL CONTROLLED ACCEPTANCE ONLY: needs the assembled backend-debug
 * server on 127.0.0.1:8000 (public CI has no knowledge data, so it cannot
 * run this spec). NOT public-CI evidence. Run locally with the backend
 * server running:
 *   npx playwright test --workers=1 tests/b012-liuren.spec.ts
 * Asserts real computed lessons/transmissions (never stubbed), the explicit
 * 天将未实现 limitation, no "尚未接入" placeholder in the result area,
 * and no horizontal overflow.
 */
test("liuren home submit renders real lessons and transmissions", async ({
  page,
}) => {
  await page.goto("/liuren");
  await page.getByRole("button", { name: "填入示例" }).click();
  // 样例：2026-10-03 09:30
  await expect(page.locator("#field-date")).toHaveValue("2026-10-03");
  await expect(page.locator("#field-time")).toHaveValue("09:30");
  await page.locator('form button[type="submit"]').first().click();
  const result = page.locator(".entry-result");
  await expect(result).toBeVisible();
  await expect(result).toContainText("天罡");
  await expect(result).toContainText("遥克");
  await expect(result).toContainText("天将未实现");
  await expect(result).not.toContainText("尚未计算");
  // 注意：限界声明本身含“尚未接入”四字（天将起法尚未接入本计算），
  // 因此此处只排除模板占位原句“实际结果尚未接入”，不排除该子串。
  await expect(result).not.toContainText("实际结果尚未接入");
});

test("liuren result page renders real chart, limitation, no placeholder, no overflow", async ({
  page,
}) => {
  await page.setViewportSize({ width: 390, height: 844 });
  // value 中的 + 必须编码为 %2B，否则会被解析为空格。
  await page.goto("/liuren/result?value=2026-10-03T09:30:00%2B08%3A00");
  await expect(page.locator("body")).toContainText("天罡");
  await expect(page.locator("body")).toContainText("遥克");
  await expect(page.locator("body")).toContainText("初传 午");
  await expect(page.locator("body")).toContainText("天将未实现");
  await expect(page.locator("body")).not.toContainText("实际结果尚未接入");
  // 同上：限界声明本身含“尚未接入”，只排除模板占位原句。
  await expect(page.locator(".template-chart")).not.toContainText(
    "实际结果尚未接入",
  );
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
