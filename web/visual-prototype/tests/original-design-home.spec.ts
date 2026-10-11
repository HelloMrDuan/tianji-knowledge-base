import { test, expect } from "@playwright/test";
import { scenarioProducts } from "../src/public/scenarioProducts";
import { domainPages } from "../src/public/domainPages";

test("TJ-008: user-first ink home prioritizes fortune, romance, career and time shortcuts", async ({ page }) => {
  await page.goto("/");
  const hero = page.locator(".scenario-hero");
  await expect(hero.locator(".ink-landscape")).toBeVisible();
  await expect(hero.locator(".scenario-hero-actions .button.primary")).toHaveText(/查看今日运势/);
  await expect(hero.locator(".scenario-hero-actions .button.primary")).toHaveAttribute("href", "/daily-structure");
  await expect(hero.locator(".scenario-hero-actions .button.outlined")).toHaveCount(2);
  await expect(hero.locator('a[href="/romance-structure"]')).toBeVisible();
  await expect(hero.locator('a[href="/career-wealth-structure"]')).toBeVisible();
  const quick = page.getByRole("navigation", { name: "运势时间快捷入口" });
  await expect(quick.getByRole("link")).toHaveCount(4);
  const paths = ["/daily-structure", "/weekly-structure", "/monthly-structure", "/yearly-structure"];
  for (const path of paths) await expect(quick.locator(`a[href="${path}"]`)).toBeVisible();
  await expect(page.locator(".scenario-card")).toHaveCount(scenarioProducts.length);
  const cards = page.locator(".scenario-grid .scenario-card");
  await expect(cards.nth(0)).toContainText("今日运势");
  await expect(cards.nth(1)).toContainText("桃花姻缘");
  await expect(cards.nth(2)).toContainText("事业财运");
  await expect(cards.nth(0)).toHaveClass(/scenario-card-featured/);
  await expect(cards.nth(1)).toHaveClass(/scenario-card-featured/);
  await expect(cards.nth(2)).toHaveClass(/scenario-card-featured/);
  await expect(page.locator('a.scenario-card[href="/ask"]')).toHaveCount(1);
  await expect(page.locator('.scenario-hero a.button.primary[href="/daily-structure"]')).toBeVisible();
  await expect(page.locator('.scenario-hero a[href="/bazi-profile"]')).toBeVisible();
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
    await expect(page.locator(".scenario-grid .scenario-card-featured")).toHaveCount(3);
    const overflow = await page.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth);
    expect(overflow).toBeLessThanOrEqual(1);
    await page.screenshot({ path: `test-results/tj008-home-${width}.png`, fullPage: true, animations: "disabled" });
  });
}

test("TJ-008: all four time links really open the corresponding scenario form", async ({ page }) => {
  for (const path of [
    "/daily-structure", "/weekly-structure", "/monthly-structure", "/yearly-structure",
  ]) {
    await page.goto("/");
    await page.locator(`.scenario-time-strip a[href="${path}"]`).click();
    await expect(page).toHaveURL(new RegExp(path + "$"));
    await expect(page.locator("main h1")).toBeVisible();
  }
});
