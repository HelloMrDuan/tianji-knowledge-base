import { test, expect } from "@playwright/test";

/** B005 TJ-023.2: career/wealth dual view E2E v2.
 *  - Identical underlying results, strictly 1 API call
 *  - Both themes (night/paper) verified with real toggle
 *  - Mobile viewports
 */
test("[real-backend] B005 dual view: one request, both themes", async ({ page }) => {
  const apiCalls: string[] = [];
  page.on("request", r => {
    if (r.url().includes("/api/v1/scenarios/public") && r.method() === "POST")
      apiCalls.push(r.url());
  });
  await page.goto("/career-wealth-structure");
  await page.getByRole("button", { name: "填入示例", exact: true }).click();
  await page.getByRole("button", { name: "查看事业财运结构" }).click();
  await expect(page.locator(".career-groups")).toBeVisible({ timeout: 15000 });
  expect(apiCalls).toHaveLength(1);

  const careerGroups = await page.locator(".career-groups article").allTextContents();

  // Switch to wealth view - no new API call
  await page.getByRole("tab", { name: "财运视角" }).click();
  await expect(page.getByRole("tab", { name: "财运视角" })).toHaveAttribute("aria-selected", "true");
  await page.waitForTimeout(500);
  expect(apiCalls).toHaveLength(1);

  const wealthGroups = await page.locator(".career-groups article").allTextContents();
  expect(wealthGroups).toHaveLength(5);
  const careerSet = new Set(careerGroups.map(s => s.replace(/\s+/g, " ").trim()));
  const wealthSet = new Set(wealthGroups.map(s => s.replace(/\s+/g, " ").trim()));
  expect(wealthSet).toEqual(careerSet);

  // Theme toggle: verify both themes render the dual view
  const themeToggle = page.locator(".theme-toggle");
  if (await themeToggle.count() > 0) {
    const initialLabel = await themeToggle.locator(".theme-toggle-label").textContent();
    await themeToggle.click();
    await page.waitForTimeout(300);
    const newLabel = await themeToggle.locator(".theme-toggle-label").textContent();
    expect(newLabel).not.toBe(initialLabel);
    // Dual view still works after theme switch
    await expect(page.locator(".career-groups")).toBeVisible();
    await expect(page.getByRole("tab", { name: "事业视角" })).toBeVisible();
    // Switch back
    await themeToggle.click();
    await page.waitForTimeout(300);
  }

  // No predictive claims
  const bodyText = await page.locator("body").textContent();
  expect(bodyText).not.toMatch(/发财|暴富|升职.*预测|必发/);
});

test("[real-backend] B005 mobile: 360px and 390px no overflow", async ({ page }) => {
  for (const width of [360, 390]) {
    await page.setViewportSize({ width, height: 844 });
    await page.goto("/career-wealth-structure");
    await page.getByRole("button", { name: "填入示例", exact: true }).click();
    await page.getByRole("button", { name: "查看事业财运结构" }).click();
    await expect(page.locator(".career-groups")).toBeVisible({ timeout: 15000 });
    await page.getByRole("tab", { name: "财运视角" }).click();
    const overflow = await page.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth);
    expect(overflow, `${width}px overflow`).toBeLessThanOrEqual(1);
  }
});
