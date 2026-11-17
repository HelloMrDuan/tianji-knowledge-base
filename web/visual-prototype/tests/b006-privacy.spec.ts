import { test, expect } from "@playwright/test";

/** B006 TJ-024.3: Person B privacy verification.
 *  - B data not persisted to localStorage/sessionStorage
 *  - Clearing B invalidates results
 *  - A's saved data not overwritten by B
 *  - Mobile viewports no overflow
 *  - No compatibility percentages or marriage predictions
 */
test("[real-backend] B006 B-data not persisted, clear invalidates", async ({ page, context }) => {
  await page.goto("/compatibility-structure");
  await page.getByRole("button", { name: "填入双人示例", exact: true }).click();

  // Get B's data from inputs (before submit)
  const bDateInput = page.locator('input[type="date"]').nth(1);
  const bDate = await bDateInput.inputValue();
  expect(bDate).not.toBe(""); // B has data

  // Check localStorage: B's birth date must NOT be there
  const ls = await page.evaluate(() => JSON.stringify(localStorage));
  expect(ls).not.toContain(bDate);

  // Check sessionStorage
  const ss = await page.evaluate(() => JSON.stringify(sessionStorage));
  expect(ss).not.toContain(bDate);

  // Submit and get result
  await page.getByRole("button", { name: "生成双人结构" }).click();
  await expect(page.locator(".compat-result")).toBeVisible({ timeout: 15000 });

  // Clear B's data
  await page.getByRole("button", { name: "清空对方资料" }).click();
  const bDateAfter = await bDateInput.inputValue();
  expect(bDateAfter).toBe("");

  // A stale two-person result must disappear immediately when B is cleared.
  await expect(page.locator(".compat-result")).toHaveCount(0);
});

test("[real-backend] B006 A-data not overwritten by B", async ({ page }) => {
  await page.goto("/compatibility-structure");
  await page.getByRole("button", { name: "填入双人示例", exact: true }).click();
  const aDateInput = page.locator('input[type="date"]').first();
  const bDateInput = page.locator('input[type="date"]').nth(1);
  const aDate = await aDateInput.inputValue();
  expect(aDate).not.toBe("");
  // Changing B must not mutate A, regardless of saved-profile defaults.
  await bDateInput.fill("2001-03-04");
  await expect(aDateInput).toHaveValue(aDate);
  await expect(bDateInput).toHaveValue("2001-03-04");
});

test("[real-backend] B006 no predictions, mobile OK", async ({ page }) => {
  for (const width of [360, 390]) {
    await page.setViewportSize({ width, height: 844 });
    await page.goto("/compatibility-structure");
    await page.getByRole("button", { name: "填入双人示例", exact: true }).click();
    await page.getByRole("button", { name: "生成双人结构" }).click();
    await expect(page.locator(".compat-result")).toBeVisible({ timeout: 15000 });

    const bodyText = await page.locator("body").textContent();
    // No compatibility percentages
    expect(bodyText).not.toMatch(/\d+\s*%/);
    expect(bodyText).not.toMatch(/缘分.*\d+分/);
    // No marriage predictions. Bounded window: the classical quote
    // ("不必专执官星而论夫", arguing AGAINST mechanical spouse judgment)
    // and the boundary note ("不输出……结婚时间") sit paragraphs apart on
    // this page, so an unbounded `.*` joins them into a false positive.
    // A real prediction phrase keeps both words in one clause (<=12 chars).
    expect(bodyText).not.toMatch(/必.{0,12}结婚|婚姻.{0,12}预测|何时.{0,12}婚/);

    const overflow = await page.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth);
    expect(overflow, `${width}px overflow`).toBeLessThanOrEqual(1);
  }
});
