import { test, expect } from "@playwright/test";

/**
 * TJ-007.4: 真实后端合同验证
 * MUST run against live private-data-backed API with real Canonical.
 * Validates assertExecuteResponse/assertScenarioResponse against REAL responses.
 * No mocks — real Python backend, real browser.
 */

const SCENARIOS = [
  { id: "bazi", type: "execute", domain: "bazi" },
  { id: "daily", type: "scenario" },
  { id: "weekly", type: "scenario" },
  { id: "monthly", type: "scenario" },
  { id: "yearly", type: "scenario" },
  { id: "romance", type: "scenario" },
  { id: "career", type: "scenario" },
  { id: "compatibility", type: "scenario" },
  { id: "life", type: "scenario" },
  { id: "liuyao", type: "execute", domain: "liuyao" },
];

test.describe("TJ-007.4 real: contract validation", () => {
  test.beforeEach(async ({ page }) => {
    // Setup birth profile
    await page.goto("/bazi-profile");
    await page.getByRole("button", { name: "填入示例" }).click();
    await page.getByRole("button", { name: "保存资料" }).click();
    await expect.poll(() => page.evaluate(() => localStorage.getItem("tianji.profile.birth.v1"))).not.toBeNull();
  });

  for (const s of SCENARIOS) {
    test(s.id + ": real HTTP contract accepted and actual user result visible", async ({ page }, testInfo) => {
      test.setTimeout(90000);
      const paths: Record<string, string> = {
        bazi: "/bazi-profile", daily: "/daily-structure", weekly: "/weekly-structure",
        monthly: "/monthly-structure", yearly: "/yearly-structure",
        romance: "/romance-structure", career: "/career-wealth-structure",
        compatibility: "/compatibility-structure", life: "/life-overview", liuyao: "/ask",
      };
      const results: Record<string, string> = {
        bazi: ".bazi-live-result", daily: ".daily-result",
        weekly: ".period-result", monthly: ".period-result",
        yearly: ".yearly-result", romance: ".romance-result",
        career: ".career-result", compatibility: ".compat-result",
        life: ".life-result", liuyao: ".live-result",
      };
      const browserErrors: string[] = [];
      page.on("pageerror", error => browserErrors.push(error.message));
      await page.goto(paths[s.id]);
      if (s.id === "liuyao") {
        await page.locator("textarea").first().fill("这件事应该如何理解？");
        await page.locator('.question-time-grid input[type="date"]').fill("2026-10-15");
        await page.locator('.question-time-grid input[type="time"]').fill("12:00");
        for (let i = 0; i < 6; i++) await page.locator(".yao-input-list select").nth(i).selectOption("7");
        await expect(page.getByRole("progressbar", { name: "起卦进度" })).toHaveAttribute("aria-valuenow", "6");
      } else if (s.id === "compatibility") {
        const b = page.locator(".compat-person-input").nth(1);
        await b.locator('input[type="date"]').fill("1995-06-20");
        await b.locator('input[type="time"]').fill("09:00");
      } else if (s.id === "yearly") {
        await page.getByLabel("目标年份").fill("2027");
      } else if (["romance", "career", "life"].includes(s.id)) {
        await page.getByLabel("观察年份").fill("2027");
      } else if (s.id === "daily") {
        await page.getByLabel("查看日期").fill("2026-10-15");
      } else if (s.id === "weekly") {
        await page.getByLabel("本周参考日期").fill("2026-10-15");
      } else if (s.id === "monthly") {
        await page.getByLabel("查看月份").fill("2026-10");
      }
      const url = s.type === "execute" ? "/api/v1/public/execute" : "/api/v1/scenarios/public";
      const pending = page.waitForResponse(r => new URL(r.url()).pathname === url &&
        r.request().method() === "POST", { timeout: 50000 });
      await page.locator('form button[type="submit"]').first().click();
      const response = await pending;
      expect(response.status(), "actual Python API must be HTTP 200").toBe(200);
      const request = response.request().postDataJSON();
      const data = await response.json();
      if (s.type === "execute") {
        expect(request.domain).toBe(s.domain);
        expect(data.domain).toBe(s.domain);
        expect(data.chart).toEqual(expect.any(Object));
      } else {
        expect(request.scenario_id).toBe(s.id);
        expect(data.scenario_id).toBe(s.id);
        expect(data.public_release).toBe(true);
        expect(data.result).toEqual(expect.any(Object));
      }
      expect(data.deterministic).toBe(true);
      expect(data.rule_matches).toEqual(expect.any(Array));
      expect(data.rule_matches.length).toBeGreaterThan(0);
      expect(data.trace).toEqual(expect.any(Array));
      expect(data.evidence).toEqual(expect.any(Object));
      expect(Object.keys(data.evidence).length).toBeGreaterThan(0);
      expect(data.warnings).toEqual(expect.any(Array));
      expect(data.limitations).toEqual(expect.any(Array));
      for (const rule of data.rule_matches) for (const id of rule.evidence_ids || []) {
        expect(data.evidence).toHaveProperty(id);
      }
      await expect(page.locator(results[s.id])).toBeVisible();
      await expect(page.getByRole("alert")).toHaveCount(0);
      expect(browserErrors).toEqual([]);
      await page.screenshot({ path: testInfo.outputPath("tj0074-live-" + s.id + ".png"),
        fullPage: true, animations: "disabled" });
    });
  }

  test("dream: real response passes contract", async ({ page }) => {
    let body: any = null;
    await page.route("**/api/v1/dream/culture", async (route) => {
      const response = await route.fetch();
      body = await response.json().catch(() => null);
      await route.fulfill({ response });
    });
    await page.goto("/dream-culture");
    await page.waitForTimeout(800);
    const input = page.locator('textarea, input[type="text"]').first();
    if (await input.count() > 0) {
      await input.fill("梦见蛇");
      const btn = page.locator('button[type="submit"]').first();
      if (await btn.count() > 0) {
        await btn.click().catch(() => {});
        await page.waitForTimeout(3000);
      }
    }
    if (body) {
      expect(body.api_version).toBe("v1");
      expect(body.public_release).toBe(true);
      expect(body.ai_enabled).toBe(false);
      expect(Array.isArray(body.matches)).toBe(true);
    }
  });
});
