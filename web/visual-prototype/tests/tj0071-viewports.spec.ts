import { test, expect } from "@playwright/test";

/**
 * TJ-007.1 P1: 三视口真实结果截图
 * 在私有受控环境运行，截图保留在私有 Actions artifact（不上传公开仓库）
 */

const VIEWPORTS = [
  { width: 1440, height: 900, name: "desktop" },
  { width: 390, height: 844, name: "mobile-390" },
  { width: 360, height: 740, name: "mobile-360" },
];

const SCENARIOS = [
  { route: "/bazi-profile", result: ".bazi-live-result", name: "bazi" },
  { route: "/daily-structure", result: ".daily-result", name: "daily" },
  { route: "/weekly-structure", result: ".period-result", name: "weekly" },
  { route: "/monthly-structure", result: ".period-result", name: "monthly" },
  { route: "/yearly-structure", result: ".yearly-result", name: "yearly" },
];

for (const vp of VIEWPORTS) {
  test.describe(`TJ-007.1 screenshots @ ${vp.name} (${vp.width}x${vp.height})`, () => {
    test.use({ viewport: { width: vp.width, height: vp.height } });

    for (const sc of SCENARIOS) {
      test(`${sc.name} real result screenshot`, async ({ page }) => {
        // 准备出生资料
        await page.goto("/bazi-profile");
        await page.getByRole("button", { name: "填入示例" }).click();
        await page.waitForTimeout(300);

        await page.goto(sc.route);
        await page.waitForTimeout(800);
        // 填写并提交（各场景输入方式不同，这里用通用方式）
        const fillBtn = page.getByRole("button", { name: "填入示例" });
        if (await fillBtn.count() > 0) {
          await fillBtn.click();
          await page.waitForTimeout(300);
        } else {
          // weekly/monthly 用日期填充
          const dateInput = page.locator('input[type="date"]').first();
          if (await dateInput.count() > 0 && sc.name !== "bazi") {
            // 已有保存资料，直接提交
          }
        }
        const submitBtn = page.locator('button[type="submit"]').first();
        if (await submitBtn.count() > 0) {
          await submitBtn.click().catch(() => {});
          // 等待真实结果
          await expect(page.locator(sc.result)).toBeVisible({ timeout: 30000 });
          await page.waitForTimeout(1000);
        }
        // 检查无横向溢出（移动端）
        if (vp.width < 768) {
          const overflow = await page.evaluate(() => {
            return document.documentElement.scrollWidth > document.documentElement.clientWidth;
          });
          expect(overflow).toBe(false);
        }
        // 截图（保存到私有 artifact）
        await page.screenshot({
          path: `test-results/tj0071-${sc.name}-${vp.name}.png`,
          fullPage: false,
        });
      });
    }
  });
}
