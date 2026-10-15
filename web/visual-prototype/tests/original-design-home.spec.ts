import { test, expect } from "@playwright/test";
import { scenarioProducts } from "../src/public/scenarioProducts";
import { domainPages } from "../src/public/domainPages";

test("TJ-008: user-first ink home prioritizes fortune, romance, career and time shortcuts", async ({ page }) => {
  await page.goto("/");
  const hero = page.locator(".scenario-hero");
  // TJ-008.7 第四轮：夜景 hero 为 <picture> 单图加载（按视口选择桌面/手机绘景）
  await expect(hero.locator(".night-hero-night .night-hero-picture img")).toBeVisible();
  await expect(hero.locator(".scenario-hero-actions .button.primary")).toHaveText(/查看今日运势/);
  await expect(hero.locator(".scenario-hero-actions .button.primary")).toHaveAttribute("href", "/daily-structure");
  await expect(hero.locator(".scenario-hero-actions .button.outlined")).toHaveCount(2);
  await expect(hero.locator('a[href="/romance-structure"]')).toBeVisible();
  await expect(hero.locator('a[href="/career-wealth-structure"]')).toBeVisible();
  // 第一层：四张核心卡（桌面大卡）
  const layer1 = page.locator(".night-cards-section .paper-cards .paper-card");
  await expect(layer1).toHaveCount(4);
  await expect(layer1.nth(0)).toContainText("今日运势");
  await expect(layer1.nth(1)).toContainText("桃花姻缘");
  await expect(layer1.nth(2)).toContainText("事业财运");
  await expect(layer1.nth(3)).toContainText("流年运势");
  await expect(layer1.nth(0).locator('a, [href]')).toHaveCount(0); // paper-card is the link
  await expect(page.locator('.night-cards-section .paper-cards a[href="/daily-structure"]')).toHaveCount(1);
  await expect(page.locator('.night-cards-section .paper-cards a[href="/romance-structure"]')).toHaveCount(1);
  await expect(page.locator('.night-cards-section .paper-cards a[href="/career-wealth-structure"]')).toHaveCount(1);
  await expect(page.locator('.night-cards-section .paper-cards a[href="/yearly-structure"]')).toHaveCount(1);
  // 第二层：八字/解梦/合盘重点入口
  const layer2 = page.locator(".spotlight-section .spotlight-cards .paper-card");
  await expect(layer2).toHaveCount(3);
  await expect(page.locator('.spotlight-section .spotlight-cards a[href="/bazi-profile"]')).toHaveCount(1);
  await expect(page.locator('.spotlight-section .spotlight-cards a[href="/dream-culture"]')).toHaveCount(1);
  await expect(page.locator('.spotlight-section .spotlight-cards a[href="/compatibility-structure"]')).toHaveCount(1);
  // 第三层：本周/本月/一事占问/人生总览
  const layer3 = page.locator(".tier3-section .tier3-list a");
  await expect(layer3).toHaveCount(4);
  await expect(page.locator('.tier3-section a[href="/weekly-structure"]')).toHaveCount(1);
  await expect(page.locator('.tier3-section a[href="/monthly-structure"]')).toHaveCount(1);
  await expect(page.locator('.tier3-section a[href="/ask"]')).toHaveCount(1);
  await expect(page.locator('.tier3-section a[href="/life-overview"]')).toHaveCount(1);
  // 无重复大型卡片区
  await expect(page.locator(".scenario-time-strip")).toHaveCount(0);
  await expect(page.locator(".scenario-grid")).toHaveCount(0);
  await expect(page.locator(".scenario-featured")).toHaveCount(0);
  // 11/11 场景全部可达
  const hrefs = ["/daily-structure","/romance-structure","/career-wealth-structure","/yearly-structure","/bazi-profile","/dream-culture","/compatibility-structure","/weekly-structure","/monthly-structure","/ask","/life-overview"];
  for (const h of hrefs) await expect(page.locator(`main a[href="${h}"]`).first()).toBeAttached();
  await expect(page.locator('.scenario-hero a.button.primary[href="/daily-structure"]')).toBeVisible();
  await expect(page.locator('.scenario-hero a[href="/bazi-profile"]')).toBeVisible();
  await expect(page.locator(".professional-section .tool-card")).toHaveCount(domainPages.length);
  await expect(page.getByRole("button", { name: "背景音乐设置" })).toBeVisible();
  const local = await page.evaluate(() => Object.keys(localStorage).filter(k => k.includes("birth")));
  expect(local).toEqual([]);
});

for (const width of [1440, 390, 360]) {
  test(`TJ-008: first original-design home audit snapshot at width ${width}`, async ({ page }) => {
    await page.setViewportSize({ width, height: width === 1440 ? 1000 : 844 });
    await page.goto("/");
    await expect(page.locator(".scenario-hero h1")).toBeVisible();
    // 第一层：桌面 4 大卡，窄屏 4 紧凑行
    if (width <= 640) {
      await expect(page.locator(".night-cards-section .mobile-card-list .mobile-card-row")).toHaveCount(4);
    } else {
      await expect(page.locator(".night-cards-section .paper-cards .paper-card")).toHaveCount(4);
    }
    // 第二层 3 重点 + 第三层 4 其他
    await expect(page.locator(".spotlight-section")).toBeAttached();
    await expect(page.locator(".tier3-section .tier3-list a")).toHaveCount(4);
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
    const link = page.locator(`main a[href="${path}"]`).first();
    await link.waitFor({ state: "visible", timeout: 10000 });
    await link.click();
    await expect(page).toHaveURL(new RegExp(path + "$"), { timeout: 10000 });
    await expect(page.locator("main h1")).toBeVisible();
  }
});

// TJ-008.7 第五轮：手机首屏四入口不得被固定底部导航遮挡。
// 严格几何断言：不滚动、不 scrollIntoView，实测每张卡片矩形与导航顶部。
for (const theme of ["night", "paper"] as const) {
  for (const [width, height] of [[390, 844], [360, 800]] as const) {
    test(`TJ-008.7: mobile first screen four entries clear bottom nav (${theme} ${width}x${height})`, async ({ page }) => {
      await page.setViewportSize({ width, height });
      await page.addInitScript((t) => {
        try { localStorage.setItem("tianji.theme", t); } catch {}
      }, theme);
      await page.goto("/");
      await page.locator(".scenario-hero h1").waitFor({ timeout: 10000 });
      // 不滚动：初始 scrollY 必须为 0
      expect(await page.evaluate(() => window.scrollY)).toBe(0);
      const geom = await page.evaluate(() => {
        const nav = document.querySelector(".mobile-bottom-nav");
        const navTop = nav ? nav.getBoundingClientRect().top : window.innerHeight;
        const rows = [...document.querySelectorAll(".night-cards-section .mobile-card-list .mobile-card-row")];
        return {
          navTop,
          rows: rows.map((r) => {
            const b = r.getBoundingClientRect();
            return { top: b.top, bottom: b.bottom, width: b.width, height: b.height };
          }),
        };
      });
      expect(geom.rows).toHaveLength(4);
      for (const r of geom.rows) {
        // 有实际尺寸
        expect(r.width).toBeGreaterThan(0);
        expect(r.height).toBeGreaterThan(0);
        // 顶部不小于 0
        expect(r.top).toBeGreaterThanOrEqual(0);
        // 底部必须在导航顶部 - 4px 安全间距之上
        expect(r.bottom).toBeLessThanOrEqual(geom.navTop - 4);
      }
    });
  }
}
