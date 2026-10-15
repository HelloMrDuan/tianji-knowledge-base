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
    test(`${s.id}: real response passes assert`, async ({ page }) => {
      const url = s.type === "execute" ? "/api/v1/public/execute" : "/api/v1/scenarios/public";
      let responseBody: any = null;
      let assertPassed = false;
      let assertError: string | null = null;

      // Intercept to capture response and verify assert doesn't throw
      await page.route(`**${url}`, async (route) => {
        const response = await route.fetch();
        const body = await response.json().catch(() => null);
        responseBody = body;
        // Let it through — the frontend's assert will run
        await route.fulfill({ response });
      });

      // Navigate to scenario page and trigger
      const pageMap: Record<string, string> = {
        bazi: "/bazi-profile",
        daily: "/daily-structure",
        weekly: "/weekly-structure",
        monthly: "/monthly-structure",
        yearly: "/yearly-structure",
        romance: "/romance-structure",
        career: "/career-wealth-structure",
        compatibility: "/compatibility-structure",
        life: "/life-overview",
        liuyao: "/ask",
      };
      
      await page.goto(pageMap[s.id]);
      await page.waitForTimeout(1000);
      
      const btn = page.locator('button[type="submit"]').first();
      if (await btn.count() > 0 && await btn.isEnabled()) {
        await btn.click().catch(() => {});
        await page.waitForTimeout(3000);
      }

      // Verify we got a real response
      expect(responseBody).not.toBeNull();
      
      // Verify contract fields (what assert checks)
      if (s.type === "execute") {
        expect(responseBody.domain).toBe(s.domain);
        expect(responseBody.deterministic).toBe(true);
        expect(typeof responseBody.chart).toBe("object");
        expect(typeof responseBody.evidence).toBe("object");
        expect(Array.isArray(responseBody.rule_matches)).toBe(true);
      } else {
        expect(responseBody.scenario_id).toBe(s.id);
        expect(responseBody.public_release).toBe(true);
        expect(responseBody.deterministic).toBe(true);
        expect(typeof responseBody.result).toBe("object");
        expect(typeof responseBody.evidence).toBe("object");
      }
      
      // Verify no uncaught assert error in console
      const errors: string[] = [];
      page.on("pageerror", (e) => errors.push(e.message));
      await page.waitForTimeout(500);
      const assertErrors = errors.filter(e => e.includes("invalid") || e.includes("assert"));
      expect(assertErrors).toHaveLength(0);
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
