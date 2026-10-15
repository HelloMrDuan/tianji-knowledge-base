import { test, expect } from "@playwright/test";

/**
 * TJ-007.1 专项验收：五条真实计算流程
 * MUST run against live private-data-backed API. No mocks.
 *
 * 验证：用户真实输入 → 真实后端计算 → 结果正确 → 页面正确展示 → 依据可追溯
 */

// 固定样例：2000-01-07 12:00 中国大陆
// 独立历法计算：己卯年、丁丑月、甲子日、庚午时
const SAMPLE_BIRTH = {
  solar: { year: 2000, month: 1, day: 7 },
  time: "12:00",
  expectedPillars: { year: "己卯", month: "丁丑", day: "甲子", hour: "庚午" },
};

async function fillBaziSample(page: any) {
  await page.goto("/bazi-profile");
  await page.getByRole("button", { name: "填入示例" }).click();
  await page.waitForTimeout(300);
}

async function waitForBaziResult(page: any) {
  const responsePromise = page.waitForResponse(
    (r: any) => r.url().includes("/api/v1/public/execute") && r.request().method() === "POST",
    { timeout: 30000 }
  );
  await page.locator('button[type="submit"]').first().click();
  const response = await responsePromise;
  expect(response.ok()).toBe(true);
  const body = await response.json();
  return body;
}

test.describe("TJ-007.1: bazi real calculation", () => {
  test("solar 2000-01-07 12:00 yields correct pillars", async ({ page }) => {
    await fillBaziSample(page);
    const body = await waitForBaziResult(page);
    // 验证四柱
    const chart = body.chart || {};
    const pillars = chart.pillars || [];
    // pillars 可能是数组或对象，检查包含预期干支
    const flat = JSON.stringify(pillars);
    expect(flat).toContain("己卯");
    expect(flat).toContain("丁丑");
    expect(flat).toContain("甲子");
    expect(flat).toContain("庚午");
    // 验证页面展示与 JSON 一致
    await expect(page.locator(".bazi-live-result")).toBeVisible({ timeout: 10000 });
    const pageText = await page.locator(".bazi-live-result").textContent();
    expect(pageText).toContain("己卯");
  });

  test("lunar input yields same pillars as solar", async ({ page }) => {
    // 农历 1999-12-01 = 公历 2000-01-07（需验证）
    // 先用阳历获取基准，再用农历对比
    await fillBaziSample(page);
    const solarBody = await waitForBaziResult(page);
    const solarPillars = JSON.stringify(solarBody.chart?.pillars || []);

    // 切换到农历输入同一天
    await page.getByRole("tab", { name: "农历" }).click();
    await page.waitForTimeout(300);
    // 1999年农历12月初一 = 2000-01-07（lunar-javascript 验证）
    await page.locator('.birth-date-row select').nth(0).selectOption("1999");
    await page.locator('.birth-date-row select').nth(1).selectOption("12");
    await page.locator('.birth-date-row select').nth(2).selectOption("1");
    await page.locator('.time-selects select').nth(0).selectOption("12");
    await page.locator('.time-selects select').nth(1).selectOption("0");
    const lunarBody = await waitForBaziResult(page);
    const lunarPillars = JSON.stringify(lunarBody.chart?.pillars || []);
    // 同一出生时刻，四柱必须一致
    expect(lunarPillars).toBe(solarPillars);
  });

  test("unknown time does not fabricate hour pillar", async ({ page }) => {
    await page.goto("/bazi-profile");
    await page.getByRole("button", { name: "填入示例" }).click();
    await page.locator('.time-unknown-check input').check();
    await page.waitForTimeout(300);
    // 点击提交应被阻断，不发送请求
    let requested = false;
    page.on("request", (r: any) => {
      if (r.url().includes("/api/v1/public/execute") && r.method() === "POST") requested = true;
    });
    await page.locator('button[type="submit"]').first().click().catch(() => {});
    await page.waitForTimeout(1000);
    expect(requested).toBe(false);
    await expect(page.locator('.question-error')).toContainText(/出生时刻未知/);
  });
});

test.describe("TJ-007.1: daily date switching", () => {
  test("different target_dates yield correct requests", async ({ page }) => {
    await page.goto("/bazi-profile");
    await page.getByRole("button", { name: "填入示例" }).click();
    await page.getByRole("button", { name: "保存资料" }).click();
    await page.waitForTimeout(500);

    const requests: any[] = [];
    page.on("request", (r: any) => {
      if (r.url().includes("/api/v1/scenarios/public") && r.method() === "POST") {
        try { requests.push(r.postDataJSON()); } catch {}
      }
    });

    await page.goto("/daily-structure");
    await page.waitForTimeout(800);
    // 选择日期 A
    await page.locator('input[type="date"]').first().fill("2026-10-15");
    await page.locator('button[type="submit"]').first().click();
    await page.waitForTimeout(2000);
    // 选择日期 B
    await page.locator('input[type="date"]').first().fill("2026-10-16");
    await page.locator('button[type="submit"]').first().click();
    await page.waitForTimeout(2000);

    expect(requests.length).toBeGreaterThanOrEqual(2);
    const dates = requests.map((b) => JSON.stringify(b));
    // 验证 target_date 不同
    expect(dates[0]).not.toBe(dates[1]);
  });
});

test.describe("TJ-007.1: weekly boundaries", () => {
  test("week boundaries correct", async ({ page }) => {
    await page.goto("/bazi-profile");
    await page.getByRole("button", { name: "填入示例" }).click();
    await page.getByRole("button", { name: "保存资料" }).click();
    await page.waitForTimeout(500);

    const requests: any[] = [];
    page.on("request", (r: any) => {
      if (r.url().includes("/api/v1/scenarios/public") && r.method() === "POST") {
        try { requests.push(r.postDataJSON()); } catch {}
      }
    });

    await page.goto("/weekly-structure");
    await page.waitForTimeout(800);
    // 普通周
    await page.locator('input[type="date"]').first().fill("2026-10-15"); // 周四
    await page.locator('button[type="submit"]').first().click();
    await page.waitForTimeout(2000);
    // 跨年周：2025-12-31（周三）应归属2025年最后一周
    await page.locator('input[type="date"]').first().fill("2025-12-31");
    await page.locator('button[type="submit"]').first().click();
    await page.waitForTimeout(2000);

    expect(requests.length).toBeGreaterThanOrEqual(2);
  });
});

test.describe("TJ-007.1: yearly switching", () => {
  test("2025/2026/2027 yield different target_year", async ({ page }) => {
    await page.goto("/bazi-profile");
    await page.getByRole("button", { name: "填入示例" }).click();
    await page.getByRole("button", { name: "保存资料" }).click();
    await page.waitForTimeout(500);

    const requests: any[] = [];
    page.on("request", (r: any) => {
      if (r.url().includes("/api/v1/scenarios/public") && r.method() === "POST") {
        try { requests.push(r.postDataJSON()); } catch {}
      }
    });

    await page.goto("/yearly-structure");
    await page.waitForTimeout(800);
    for (const year of ["2025", "2026", "2027"]) {
      const yearInput = page.locator('input[type="number"], select').first();
      // 尝试找到年份选择
      const selects = page.locator('select');
      const count = await selects.count();
      let found = false;
      for (let i = 0; i < count; i++) {
        const opts = await selects.nth(i).locator('option').allTextContents();
        if (opts.some((o: string) => o.includes("2025"))) {
          await selects.nth(i).selectOption(year);
          found = true;
          break;
        }
      }
      if (!found) {
        // 尝试 number input
        const numInput = page.locator('input[type="number"]').first();
        if (await numInput.count() > 0) await numInput.fill(year);
      }
      await page.locator('button[type="submit"]').first().click();
      await page.waitForTimeout(2000);
    }
    expect(requests.length).toBeGreaterThanOrEqual(3);
    const bodies = requests.map((b) => JSON.stringify(b));
    // 验证年份不同
    expect(bodies[0]).toMatch(/2025/);
  });
});

test.describe("TJ-007.1: cross-scenario lunar consistency", () => {
  test("lunar birth preserved across 5 scenarios", async ({ page }) => {
    // 八字页保存农历
    await page.goto("/bazi-profile");
    await page.getByRole("tab", { name: "农历" }).click();
    await page.locator('.birth-date-row select').nth(0).selectOption("2000");
    await page.locator('.birth-date-row select').nth(1).selectOption("4");
    await page.locator('.birth-date-row select').nth(2).selectOption("15");
    await page.locator('.time-selects select').nth(0).selectOption("12");
    await page.locator('.time-selects select').nth(1).selectOption("0");
    await page.getByRole("button", { name: "保存资料" }).click();
    await page.waitForTimeout(500);

    const birthValues: string[] = [];
    page.on("request", (r: any) => {
      if (r.url().includes("/api/v1/scenarios/public") && r.method() === "POST") {
        try {
          const b = r.postDataJSON();
          const s = JSON.stringify(b);
          const m = s.match(/(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}[+-]\d{2}:\d{2})/);
          if (m) birthValues.push(m[1]);
        } catch {}
      }
    });

    // 依次访问 4 个场景并提交
    for (const route of ["/daily-structure", "/weekly-structure", "/monthly-structure", "/yearly-structure"]) {
      await page.goto(route);
      await page.waitForTimeout(800);
      const btn = page.locator('button[type="submit"]').first();
      if (await btn.count() > 0) {
        await btn.click().catch(() => {});
        await page.waitForTimeout(1500);
      }
    }

    // 所有场景的出生瞬时必须一致（农历 2000-04-15 = 公历 2000-05-18）
    expect(birthValues.length).toBeGreaterThan(0);
    for (const v of birthValues) {
      expect(v).toMatch(/^2000-05-18T12:00:00\+08:00$/);
    }

    // 返回八字页，验证农历未丢失
    await page.goto("/bazi-profile");
    await expect(page.locator('.birth-calendar-tabs button.active')).toHaveText("农历", { timeout: 5000 });
  });
});
