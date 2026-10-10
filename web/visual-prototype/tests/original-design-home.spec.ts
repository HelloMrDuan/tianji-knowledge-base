import { test, expect } from "@playwright/test";
import { scenarioProducts } from "../src/public/scenarioProducts";
import { domainPages } from "../src/public/domainPages";

test("TJ-008: original scenario-first ink home keeps one-question primary CTA and time strip", async ({ page }) => {
  await page.goto("/");
  const hero = page.locator(".scenario-hero");
  await expect(hero.locator(".ink-landscape")).toBeVisible();
  await expect(hero.locator(".scenario-hero-actions .button.primary")).toHaveText(/一事占问/);
  await expect(hero.locator(".scenario-hero-actions .button.primary")).toHaveAttribute("href", "/ask");
  await expect(hero.locator(".scenario-hero-actions .button.outlined")).toHaveCount(2);
  await expect(hero.locator('a[href="/romance-structure"]')).toBeVisible();
  await expect(hero.locator('a[href="/career-wealth-structure"]')).toBeVisible();
  const quick = page.getByRole("navigation", { name: "运势时间快捷入口" });
  await expect(quick.getByRole("link")).toHaveCount(4);
  const paths = ["/daily-structure", "/weekly-structure", "/monthly-structure", "/yearly-structure"];
  for (const path of paths) await expect(quick.locator(`a[href="${path}"]`)).toBeVisible();
  await expect(page.locator(".scenario-card")).toHaveCount(scenarioProducts.length);
  await expect(page.locator(".professional-section .tool-card")).toHaveCount(domainPages.length);
  await expect(page.locator(".scenario-featured a[href='/life-overview']")).toBeVisible();
  await expect(page.getByRole("button", { name: "背景音乐设置" })).toBeVisible();
  const local = await page.evaluate(() => Object.keys(localStorage).filter(k => k.includes("birth")));
  expect(local).toEqual([]);
});

for (const width of [1440, 390, 360]) {
  test(`TJ-008: first original-design home audit snapshot at width ${width}`, async ({ page }) => {
    await page.setViewportSize({ width, height: width === 1440 ? 1000 : 844 });
    await page.goto("/");
    await expect(page.locator(".scenario-hero h1")).toBeVisible();
    await expect(page.getByRole("navigation", { name: "运势时间快捷入口" })).toBeVisible();
    const overflow = await page.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth);
    expect(overflow).toBeLessThanOrEqual(1);
    await page.screenshot({ path: `test-results/tj008-home-${width}.png`, fullPage: true, animations: "disabled" });
  });
}

test("TJ-008: all four time links really open the corresponding scenario form", async ({ page }) => {
  for (const [path,heading] of [
    ["/daily-structure", "今日"],
    ["/weekly-structure", "本周"],
    ["/monthly-structure", "本月"],
    ["/yearly-structure", "流年"],
  ]) {
    await page.goto("/");
    await page.locator(`.scenario-time-strip a[href="${path}"]`).click();
    await expect(page).toHaveURL(new RegExp(path + "$"));
    await expect(page.locator("main h1")).toContainText(heading);
  }
});
