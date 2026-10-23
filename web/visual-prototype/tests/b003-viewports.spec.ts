import { test, expect } from "@playwright/test";
const VIEWPORTS = [
  { w: 1440, h: 900, name: "desktop" },
  { w: 768, h: 1024, name: "tablet" },
  { w: 360, h: 740, name: "phone" },
] as const;
for (const vp of VIEWPORTS) {
  test(`B003 viewport ${vp.name} (${vp.w}px): homepage + bazi flow`, async ({ page }) => {
    await page.setViewportSize({ width: vp.w, height: vp.h });
    await page.goto("/");
    await expect(page.locator("main h1")).toBeVisible();
    const overflow = await page.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth);
    expect(overflow, `${vp.name} homepage overflow`).toBeLessThanOrEqual(1);
    await page.goto("/bazi-profile");
    await expect(page.locator("main h1")).toBeVisible();
    await page.getByRole("button", { name: "填入示例", exact: true }).click();
    const resp = page.waitForResponse(r =>
      new URL(r.url()).pathname === "/api/v1/public/execute" && r.request().method() === "POST");
    await page.getByRole("button", { name: "生成基础档案" }).click();
    expect((await resp).status()).toBe(200);
    await expect(page.locator(".bazi-live-result")).toBeVisible({ timeout: 20000 });
    const overflow2 = await page.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth);
    expect(overflow2, `${vp.name} result overflow`).toBeLessThanOrEqual(1);
  });
}
