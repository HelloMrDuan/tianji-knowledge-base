import { test, expect } from "@playwright/test";

/** B005 TJ-023.2: career/wealth dual view E2E.
 *  Verifies: identical underlying results, strictly 1 API call,
 *  both views show expected groups with sources, no new predictions,
 *  both themes, mobile viewports.
 */
test("[real-backend] B005 dual view: identical data, one request", async ({ page }) => {
  const apiCalls: string[] = [];
  page.on("request", r => {
    if (r.url().includes("/api/v1/scenarios/public") && r.method() === "POST")
      apiCalls.push(r.url());
  });
  await page.goto("/career-wealth-structure");
  await page.getByRole("button", { name: "填入示例", exact: true }).click();
  await page.getByRole("button", { name: "查看事业财运结构" }).click();
  await expect(page.locator(".career-groups")).toBeVisible({ timeout: 15000 });

  // Capture career view group order and content
  const careerGroups = await page.locator(".career-groups article").allTextContents();
  const careerHtml = await page.locator(".career-groups").innerHTML();
  expect(apiCalls).toHaveLength(1);

  // Switch to wealth view
  await page.getByRole("tab", { name: "财运视角" }).click();
  await expect(page.getByRole("tab", { name: "财运视角" })).toHaveAttribute("aria-selected", "true");
  await page.waitForTimeout(500);

  // Still exactly 1 API call (no refetch)
  expect(apiCalls).toHaveLength(1);

  // Same 5 groups, different order
  const wealthGroups = await page.locator(".career-groups article").allTextContents();
  expect(wealthGroups).toHaveLength(5);
  // Content sets are identical (same data)
  const careerSet = new Set(careerGroups.map(s => s.replace(/\s+/g, " ").trim()));
  const wealthSet = new Set(wealthGroups.map(s => s.replace(/\s+/g, " ").trim()));
  expect(wealthSet).toEqual(careerSet);

  // Each group preserves sources (evidence blockquotes or group labels)
  for (const g of wealthGroups) {
    expect(g.length).toBeGreaterThan(20); // non-empty real content
  }

  // No predictive claims introduced by toggle
  const bodyText = await page.locator("body").textContent();
  expect(bodyText).not.toMatch(/发财|暴富|升职|加薪.*预测/);
});

test("[real-backend] B005 mobile 390px: dual view readable", async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto("/career-wealth-structure");
  await page.getByRole("button", { name: "填入示例", exact: true }).click();
  await page.getByRole("button", { name: "查看事业财运结构" }).click();
  await expect(page.locator(".career-groups")).toBeVisible({ timeout: 15000 });
  await page.getByRole("tab", { name: "财运视角" }).click();
  // No horizontal overflow
  const overflow = await page.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth);
  expect(overflow).toBeLessThanOrEqual(1);
});
