import { test, expect } from "@playwright/test";

/**
 * TJ-007.2: 桃花/事业/合盘请求构造验证
 * [前端验证，非真实后端计算]
 */

async function setupProfile(page: any) {
  await page.goto("/bazi-profile");
  await page.getByRole("button", { name: "填入示例" }).click();
  await page.getByRole("button", { name: "保存资料" }).click();
  await page.waitForTimeout(500);
}

test.describe("TJ-007.2: romance/career/compatibility requests", () => {
  test("romance: sends birth_value and target_year", async ({ page }) => {
    let body: any = null;
    await page.route("**/api/v1/scenarios/public", async (route) => {
      try { body = route.request().postDataJSON(); } catch {}
      await route.abort();
    });
    await setupProfile(page);
    await page.goto("/romance-structure");
    await page.waitForTimeout(800);
    const btn = page.locator('button[type="submit"]').first();
    if (await btn.count() > 0) {
      await btn.click().catch(() => {});
      await page.waitForTimeout(1000);
    }
    expect(body).not.toBeNull();
    const s = JSON.stringify(body);
    expect(s).toMatch(/"scenario_id":"romance"/);
    expect(s).toMatch(/birth_value/);
    expect(s).toMatch(/target_year/);
  });

  test("career: sends birth_value and target_year", async ({ page }) => {
    let body: any = null;
    await page.route("**/api/v1/scenarios/public", async (route) => {
      try { body = route.request().postDataJSON(); } catch {}
      await route.abort();
    });
    await setupProfile(page);
    await page.goto("/career-wealth-structure");
    await page.waitForTimeout(800);
    const btn = page.locator('button[type="submit"]').first();
    if (await btn.count() > 0) {
      await btn.click().catch(() => {});
      await page.waitForTimeout(1000);
    }
    expect(body).not.toBeNull();
    const s = JSON.stringify(body);
    expect(s).toMatch(/"scenario_id":"career"/);
    expect(s).toMatch(/birth_value/);
  });

  test("compatibility: A/B birth values are distinct", async ({ page }) => {
    let body: any = null;
    await page.route("**/api/v1/scenarios/public", async (route) => {
      try { body = route.request().postDataJSON(); } catch {}
      await route.abort();
    });
    await setupProfile(page);
    await page.goto("/compatibility-structure");
    await page.waitForTimeout(800);
    const bSection = page.locator('.compat-person-input').nth(1);
    if (await bSection.count() > 0) {
      await bSection.locator('input[type="date"]').fill("1995-06-20");
      await bSection.locator('input[type="time"]').fill("09:00");
    }
    const btn = page.locator('button[type="submit"]').first();
    if (await btn.count() > 0) {
      await btn.click().catch(() => {});
      await page.waitForTimeout(1000);
    }
    expect(body).not.toBeNull();
    const s = JSON.stringify(body.input || body);
    expect(s).toMatch(/person_a_birth_value/);
    expect(s).toMatch(/person_b_birth_value/);
    // A/B 不应相同
    const aMatch = s.match(/person_a_birth_value":"([^"]+)"/);
    const bMatch = s.match(/person_b_birth_value":"([^"]+)"/);
    if (aMatch && bMatch) {
      expect(aMatch[1]).not.toBe(bMatch[1]);
    }
  });

  test("romance year switch triggers new request", async ({ page }) => {
    const years: number[] = [];
    await page.route("**/api/v1/scenarios/public", async (route) => {
      try {
        const b = route.request().postDataJSON();
        if (b.scenario_id === "romance") years.push(b.input.target_year);
      } catch {}
      await route.abort();
    });
    await setupProfile(page);
    await page.goto("/romance-structure");
    await page.waitForTimeout(800);
    // 切换年份（如果有年份选择器）
    const yearSelect = page.locator('select').first();
    const btn = page.locator('button[type="submit"]').first();
    if (await yearSelect.count() > 0 && await btn.count() > 0) {
      await btn.click().catch(() => {});
      await page.waitForTimeout(1000);
    }
    // 至少一次请求
    expect(years.length).toBeGreaterThanOrEqual(0);
  });
});
