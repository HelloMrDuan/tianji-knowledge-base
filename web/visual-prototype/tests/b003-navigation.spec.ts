import { test, expect } from "@playwright/test";

/** B003: homepage -> 11 scenarios navigation check.
 * Verifies each scenario has a working entry from the homepage
 * and each route loads its page. No mocks.
 */
const SCENARIOS = [
  { name: "今日运势", route: "/daily-structure" },
  { name: "桃花姻缘", route: "/romance-structure" },
  { name: "事业财运", route: "/career-wealth-structure" },
  { name: "流年运势", route: "/yearly-structure" },
  { name: "八字命理", route: "/bazi-profile" },
  { name: "解梦", route: "/dream-culture" },
  { name: "缘分合盘", route: "/compatibility-structure" },
  { name: "本周运势", route: "/weekly-structure" },
  { name: "本月运势", route: "/monthly-structure" },
  { name: "一事占问", route: "/ask" },
  { name: "人生总览", route: "/life-overview" },
] as const;

test("B003 homepage exposes all 11 scenario entries", async ({ page }) => {
  await page.goto("/");
  await expect(page.locator("main h1")).toBeVisible();
  for (const s of SCENARIOS) {
    const link = page.locator(`a[href="${s.route}"]`).first();
    await expect(link, `homepage entry for ${s.name} (${s.route})`).toBeVisible();
  }
});

for (const s of SCENARIOS) {
  test(`B003 navigate: homepage -> ${s.name} (${s.route})`, async ({ page }) => {
    await page.goto("/");
    const link = page.locator(`a[href="${s.route}"]`).first();
    await link.scrollIntoViewIfNeeded();
    await link.click();
    await expect(page).toHaveURL(new RegExp(s.route.replace("/", "\\/") + "$"));
    await expect(page.locator("main h1")).toBeVisible({ timeout: 10000 });
  });
}
