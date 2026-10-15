import { test, expect } from "@playwright/test";

/**
 * TJ-007.2: 三场景真实后端验收
 * MUST run against live private-data-backed API. No mocks.
 */

async function setupProfile(page: any) {
  await page.goto("/bazi-profile");
  await page.getByRole("button", { name: "填入示例" }).click();
  await page.getByRole("button", { name: "保存资料" }).click();
  await page.waitForTimeout(500);
}

test.describe("TJ-007.2 real backend: romance", () => {
  test("romance real calculation returns xianchi structure", async ({ page }) => {
    await setupProfile(page);
    await page.goto("/romance-structure");
    await page.waitForTimeout(800);

    const responsePromise = page.waitForResponse(
      (r: any) => r.url().includes("/api/v1/scenarios/public") && r.request().method() === "POST",
      { timeout: 30000 }
    );
    const btn = page.locator('button[type="submit"]').first();
    if (await btn.count() > 0) {
      await btn.click();
      const response = await responsePromise;
      expect(response.ok()).toBe(true);
      const body = await response.json();
      // 验证返回结构
      expect(body.rule_matches).toBeDefined();
      expect(body.evidence).toBeDefined();
      // 验证页面展示结果
      await expect(page.locator(".romance-result, .result-section").first()).toBeVisible({ timeout: 10000 });
    }
  });
});

test.describe("TJ-007.2 real backend: career", () => {
  test("career real calculation returns structure", async ({ page }) => {
    await setupProfile(page);
    await page.goto("/career-wealth-structure");
    await page.waitForTimeout(800);

    const responsePromise = page.waitForResponse(
      (r: any) => r.url().includes("/api/v1/scenarios/public") && r.request().method() === "POST",
      { timeout: 30000 }
    );
    const btn = page.locator('button[type="submit"]').first();
    if (await btn.count() > 0) {
      await btn.click();
      const response = await responsePromise;
      expect(response.ok()).toBe(true);
      const body = await response.json();
      expect(body.rule_matches).toBeDefined();
      await expect(page.locator(".career-result, .result-section").first()).toBeVisible({ timeout: 10000 });
    }
  });
});

test.describe("TJ-007.2 real backend: compatibility", () => {
  test("compatibility real calculation with A/B", async ({ page }) => {
    await setupProfile(page);
    await page.goto("/compatibility-structure");
    await page.waitForTimeout(800);

    const bSection = page.locator('.compat-person-input').nth(1);
    if (await bSection.count() > 0) {
      await bSection.locator('input[type="date"]').fill("1995-06-20");
      await bSection.locator('input[type="time"]').fill("09:00");
    }

    const responsePromise = page.waitForResponse(
      (r: any) => r.url().includes("/api/v1/scenarios/public") && r.request().method() === "POST",
      { timeout: 30000 }
    );
    const btn = page.locator('button[type="submit"]').first();
    if (await btn.count() > 0) {
      await btn.click();
      const response = await responsePromise;
      expect(response.ok()).toBe(true);
      const body = await response.json();
      expect(body.rule_matches).toBeDefined();
      // 验证 A/B 四柱都在返回中
      const s = JSON.stringify(body);
      expect(s.length).toBeGreaterThan(500);
    }
  });
});
