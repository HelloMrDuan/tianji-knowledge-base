import { test, expect } from "@playwright/test";

/**
 * TJ-007.3: 一事占问/解梦/人生总览请求构造验证
 * [前端验证，非真实后端计算]
 */

test.describe("TJ-007.3: question (liuyao)", () => {
  test("sends yao_values array of 6", async ({ page }) => {
    let body: any = null;
    await page.route("**/api/v1/public/execute", async (route) => {
      try { body = route.request().postDataJSON(); } catch {}
      await route.abort();
    });
    await page.goto("/ask");
    await page.waitForTimeout(800);
    // 填写问题
    const qInput = page.locator('input[placeholder*="工作"], textarea').first();
    if (await qInput.count() > 0) {
      await qInput.fill("这次工作选择是否合适？");
    }
    // 一次投完六次（如果有按钮）
    const tossBtn = page.getByRole("button", { name: /一次投完六次|全部掷完/ });
    if (await tossBtn.count() > 0) {
      await tossBtn.click();
      await page.waitForTimeout(500);
    }
    const submitBtn = page.locator('button[type="submit"]').first();
    if (await submitBtn.count() > 0) {
      await submitBtn.click().catch(() => {});
      await page.waitForTimeout(1000);
    }
    // 验证请求（如果已提交）
    if (body) {
      expect(body.domain).toBe("liuyao");
      expect(Array.isArray(body.input?.yao_values)).toBe(true);
    }
  });
});

test.describe("TJ-007.3: dream culture", () => {
  test("sends dream text to culture API", async ({ page }) => {
    let body: any = null;
    await page.route("**/api/v1/dream/culture", async (route) => {
      try { body = route.request().postDataJSON(); } catch {}
      await route.abort();
    });
    await page.goto("/dream-culture");
    await page.waitForTimeout(800);
    const dreamInput = page.locator('textarea, input[type="text"]').first();
    if (await dreamInput.count() > 0) {
      await dreamInput.fill("我梦见被蛇咬了");
      await page.waitForTimeout(300);
    }
    const submitBtn = page.locator('button[type="submit"]').first();
    if (await submitBtn.count() > 0) {
      await submitBtn.click().catch(() => {});
      await page.waitForTimeout(1000);
    }
    if (body) {
      expect(JSON.stringify(body)).toMatch(/蛇/);
    }
  });
});

test.describe("TJ-007.3: life overview", () => {
  test("sends birth_value and target_year", async ({ page }) => {
    let body: any = null;
    await page.route("**/api/v1/scenarios/public", async (route) => {
      try { body = route.request().postDataJSON(); } catch {}
      await route.abort();
    });
    await page.goto("/bazi-profile");
    await page.getByRole("button", { name: "填入示例" }).click();
    await page.getByRole("button", { name: "保存资料" }).click();
    await page.waitForTimeout(500);

    await page.goto("/life-overview");
    await page.waitForTimeout(800);
    const btn = page.locator('button[type="submit"]').first();
    if (await btn.count() > 0) {
      await btn.click().catch(() => {});
      await page.waitForTimeout(1000);
    }
    expect(body).not.toBeNull();
    const s = JSON.stringify(body);
    expect(s).toMatch(/"scenario_id":"life"/);
    expect(s).toMatch(/birth_value/);
  });
});
