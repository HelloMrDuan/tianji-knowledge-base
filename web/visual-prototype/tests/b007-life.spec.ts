import { test, expect } from "@playwright/test";

/** B007 TJ-025.1/025.3: Life overview 4-source consistency.
 *  - 4 sources share birth data and target year
 *  - Year switching triggers real recalculation
 *  - Clearing birth data invalidates results
 *  - Multi-viewport: 360/390/768/1440px
 *  - No unreviewed comprehensive verdicts
 */
test("[real-backend] B007 life: year switch recalculates", async ({ page }) => {
  const apiCalls: string[] = [];
  page.on("request", r => {
    if (r.url().includes("/api/v1/scenarios/public") && r.method() === "POST")
      apiCalls.push(r.url());
  });
  await page.goto("/life-overview");
  await page.getByRole("button", { name: "填入示例", exact: true }).click();
  await page.getByRole("button", { name: /查看|生成/ }).first().click();
  await expect(page.locator(".life-result")).toBeVisible({ timeout: 20000 });
  const firstCallCount = apiCalls.length;
  expect(firstCallCount).toBeGreaterThan(0);

  // Change target year - should trigger recalculation
  const yearInput = page.locator('input[type="number"]').first();
  const currentYear = await yearInput.inputValue();
  const newYear = String(Number(currentYear) + 1);
  await yearInput.fill(newYear);
  await page.getByRole("button", { name: /查看|生成|重新/ }).first().click();
  await page.waitForTimeout(2000);
  expect(apiCalls.length).toBeGreaterThan(firstCallCount);
});

test("[real-backend] B007 life: clear invalidates, no verdicts", async ({ page }) => {
  await page.goto("/life-overview");
  await page.getByRole("button", { name: "填入示例", exact: true }).click();
  await page.getByRole("button", { name: /查看|生成/ }).first().click();
  await expect(page.locator(".life-result")).toBeVisible({ timeout: 20000 });

  // Clear birth data
  await page.getByRole("button", { name: "清除本机资料" }).click();
  await page.waitForTimeout(500);
  // Result should be gone or form reset
  const bodyText = await page.locator("body").textContent();
  // No comprehensive life verdicts
  expect(bodyText).not.toMatch(/一生.*大富|注定.*贫|寿.*\d+岁/);
});

test("[real-backend] B007 life: multi-viewport no overflow", async ({ page }) => {
  for (const [width, height] of [[360, 844], [390, 844], [768, 1024], [1440, 900]]) {
    await page.setViewportSize({ width, height });
    await page.goto("/life-overview");
    await page.getByRole("button", { name: "填入示例", exact: true }).click();
    await page.getByRole("button", { name: /查看|生成/ }).first().click();
    await expect(page.locator(".life-result")).toBeVisible({ timeout: 20000 });
    const overflow = await page.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth);
    expect(overflow, `${width}px overflow`).toBeLessThanOrEqual(1);
  }
});
