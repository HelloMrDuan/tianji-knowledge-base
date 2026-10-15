import { test, expect } from "@playwright/test";

/**
 * TJ-006.3: 双人合盘隐私隔离与本机资料删除
 */

test.describe("TJ-006.3: A/B isolation", () => {
  test("modifying B does not affect A", async ({ page }) => {
    await page.goto("/bazi-profile");
    await page.getByRole("button", { name: "填入示例" }).click();
    await page.getByRole("button", { name: "保存资料" }).click();
    await page.waitForTimeout(500);

    await page.goto("/compatibility-structure");
    await page.waitForTimeout(800);
    // B 填写不同资料
    const bSection = page.locator('.compat-person-input').nth(1);
    await bSection.locator('input[type="date"]').fill("1995-06-20");
    await bSection.locator('input[type="time"]').fill("09:00");
    await page.waitForTimeout(300);

    // A 应仍为示例资料（2000-01-07）
    const aSection = page.locator('.compat-person-input').nth(0);
    const aDate = await aSection.locator('input[type="date"]').inputValue();
    expect(aDate).toBe("2000-01-07");

    // B 不应写入 localStorage
    const saved = await page.evaluate(() => localStorage.getItem("tianji.profile.birth.v1"));
    const profile = JSON.parse(saved || "{}");
    expect(profile.year).not.toBe(1995);
  });

  test("clear B resets B state", async ({ page }) => {
    await page.goto("/compatibility-structure");
    await page.waitForTimeout(800);
    const bSection = page.locator('.compat-person-input').nth(1);
    await bSection.locator('input[type="date"]').fill("1995-06-20");
    await bSection.locator('input[type="time"]').fill("09:00");
    await page.waitForTimeout(300);

    await page.getByRole("button", { name: "清空对方资料" }).click();
    await page.waitForTimeout(300);

    const bDate = await bSection.locator('input[type="date"]').inputValue();
    expect(bDate).toBe("");
  });

  test("A/B request params correspond correctly", async ({ page }) => {
    // [前端流程测试，非真实后端计算]
    await page.goto("/bazi-profile");
    await page.getByRole("button", { name: "填入示例" }).click();
    await page.getByRole("button", { name: "保存资料" }).click();
    await page.waitForTimeout(500);

    let body: any = null;
    await page.route("**/api/v1/scenarios/public", async (route) => {
      try { body = route.request().postDataJSON(); } catch {}
      await route.fulfill({ status: 200, body: JSON.stringify({ ok: true, stub: "frontend-flow" }) });
    });

    await page.goto("/compatibility-structure");
    await page.waitForTimeout(800);
    const bSection = page.locator('.compat-person-input').nth(1);
    await bSection.locator('input[type="date"]').fill("1995-06-20");
    await bSection.locator('input[type="time"]').fill("09:00");
    await page.locator('button[type="submit"]').first().click();
    await page.waitForTimeout(1500);

    expect(body).not.toBeNull();
    const s = JSON.stringify(body.input || body);
    // A: 2000-01-07, B: 1995-06-20
    expect(s).toMatch(/2000-01-07/);
    expect(s).toMatch(/1995-06-20/);
  });
});

test.describe("TJ-006.3: personal data deletion", () => {
  test("clear removes storage and UI state", async ({ page }) => {
    await page.goto("/bazi-profile");
    await page.getByRole("button", { name: "填入示例" }).click();
    await page.getByRole("button", { name: "保存资料" }).click();
    await page.waitForTimeout(500);
    expect(await page.evaluate(() => localStorage.getItem("tianji.profile.birth.v1"))).not.toBeNull();

    await page.getByRole("button", { name: "清除本机资料" }).click();
    await page.waitForTimeout(500);

    // localStorage 已清除
    expect(await page.evaluate(() => localStorage.getItem("tianji.profile.birth.v1"))).toBeNull();
    // 主题、音乐设置保留
    await page.evaluate(() => {
      localStorage.setItem("tianji.theme", "night-ink");
      localStorage.setItem("tianji.prototype.music", "{}");
    });
    await page.getByRole("button", { name: "填入示例" }).click();
    await page.getByRole("button", { name: "保存资料" }).click();
    await page.waitForTimeout(300);
    await page.getByRole("button", { name: "清除本机资料" }).click();
    await page.waitForTimeout(300);
    expect(await page.evaluate(() => localStorage.getItem("tianji.theme"))).toBe("night-ink");
  });

  test("deleted data does not reappear across pages", async ({ page }) => {
    await page.goto("/bazi-profile");
    await page.getByRole("button", { name: "填入示例" }).click();
    await page.getByRole("button", { name: "保存资料" }).click();
    await page.waitForTimeout(500);
    await page.getByRole("button", { name: "清除本机资料" }).click();
    await page.waitForTimeout(500);

    // 访问各场景，不应带出旧资料
    for (const route of ["/daily-structure", "/weekly-structure", "/monthly-structure", "/yearly-structure"]) {
      await page.goto(route);
      await page.waitForTimeout(800);
      const dateInput = page.locator('input[type="date"]').first();
      if (await dateInput.count() > 0) {
        const val = await dateInput.inputValue();
        expect(val).not.toBe("2000-01-07");
      }
    }
  });

  test("stale async response does not revive deleted result", async ({ page }) => {
    // [前端状态测试，受控延迟]
    let resolveSlow: any;
    const slowPromise = new Promise((r) => { resolveSlow = r; });
    await page.route("**/api/v1/public/execute", async (route) => {
      await slowPromise;
      await route.fulfill({ status: 200, body: JSON.stringify({ result: {}, stub: "late" }) });
    });

    await page.goto("/bazi-profile");
    await page.getByRole("button", { name: "填入示例" }).click();
    await page.locator('button[type="submit"]').first().click().catch(() => {});
    await page.waitForTimeout(500);
    // 删除资料（应使 requestVersion 失效）
    await page.getByRole("button", { name: "清除本机资料" }).click();
    await page.waitForTimeout(300);
    resolveSlow!();
    await page.waitForTimeout(1000);
    // 结果不应重新出现
    const resultVisible = await page.locator(".bazi-live-result").count();
    expect(resultVisible).toBe(0);
  });
});
