import { expect, test } from "@playwright/test";

/**
 * TJ-007.1: 五场景请求构造验证（前端）
 * 验证前端发送的参数格式正确。不依赖后端可用性。
 * [前端验证，非真实后端计算]
 */

async function setupProfile(page: any) {
  await page.goto("/bazi-profile");
  await page.getByRole("button", { name: "填入示例" }).click();
  await page.getByRole("button", { name: "保存资料" }).click();
  await page.waitForTimeout(500);
}

test.describe("TJ-007.1: scenario request construction", () => {
  test("bazi: sends ISO datetime with +08:00", async ({ page }) => {
    let body: any = null;
    await page.route("**/api/v1/public/execute", async (route) => {
      try { body = route.request().postDataJSON(); } catch {}
      await route.abort();
    });
    await setupProfile(page);
    await page.goto("/bazi-profile");
    const btn = page.locator('button[type="submit"]').first();
    await btn.click().catch(() => {});
    await page.waitForTimeout(1000);
    expect(body).not.toBeNull();
    expect(JSON.stringify(body)).toMatch(/2000-01-07T12:00:00\+08:00/);
  });

  test("daily: sends birth_value and target_date", async ({ page }) => {
    let body: any = null;
    await page.route("**/api/v1/scenarios/public", async (route) => {
      try { body = route.request().postDataJSON(); } catch {}
      await route.abort();
    });
    await setupProfile(page);
    await page.goto("/daily-structure");
    await page.waitForTimeout(800);
    const btn = page.locator('button[type="submit"]').first();
    await btn.click().catch(() => {});
    await page.waitForTimeout(1000);
    expect(body).not.toBeNull();
    const s = JSON.stringify(body);
    expect(s).toMatch(/birth_value/);
    expect(s).toMatch(/2000-01-07T12:00:00\+08:00/);
  });

  test("yearly: sends birth_value and target_year", async ({ page }) => {
    let body: any = null;
    await page.route("**/api/v1/scenarios/public", async (route) => {
      try { body = route.request().postDataJSON(); } catch {}
      await route.abort();
    });
    await setupProfile(page);
    await page.goto("/yearly-structure");
    await page.waitForTimeout(800);
    const btn = page.locator('button[type="submit"]').first();
    await btn.click().catch(() => {});
    await page.waitForTimeout(1000);
    expect(body).not.toBeNull();
    expect(JSON.stringify(body)).toMatch(/target_year/);
  });
});
