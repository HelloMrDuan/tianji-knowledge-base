import { test, expect } from "@playwright/test";

/**
 * TJ-007.1: screenshot only AFTER genuine private-data-backed HTTP 200 and rendered result.
 * Screenshots contain synthetic fixed test dates only; stored as restricted private Actions artifact.
 */
const viewports = [
  { width: 1440, height: 900, label: "desktop" },
  { width: 390, height: 844, label: "mobile390" },
  { width: 360, height: 740, label: "mobile360" },
] as const;
const scenes = [
  { route: "/bazi-profile", endpoint: "/api/v1/public/execute", result: ".bazi-live-result", name: "bazi" },
  { route: "/daily-structure", endpoint: "/api/v1/scenarios/public", result: ".daily-result", name: "daily" },
  { route: "/weekly-structure", endpoint: "/api/v1/scenarios/public", result: ".period-result", name: "weekly" },
  { route: "/monthly-structure", endpoint: "/api/v1/scenarios/public", result: ".period-result", name: "monthly" },
  { route: "/yearly-structure", endpoint: "/api/v1/scenarios/public", result: ".yearly-result", name: "yearly" },
] as const;

for (const viewport of viewports) {
  test.describe("TJ-007.1 live "+viewport.label+" screenshots", () => {
    test.use({ viewport: { width: viewport.width, height: viewport.height } });

    for (const scene of scenes) {
      test(scene.name+": real-result screenshot with no page overflow", async ({ page }) => {
        await page.goto("/bazi-profile");
        await page.getByRole("button", { name: "填入示例" }).click();
        await page.getByRole("button", { name: "保存资料" }).click();

        await page.goto(scene.route);
        const responsePromise = page.waitForResponse(
          r => new URL(r.url()).pathname === scene.endpoint && r.request().method() === "POST",
          { timeout: 30_000 }
        );
        await page.locator('form button[type="submit"]').first().click();
        const response = await responsePromise;
        expect(response.status(), "real private HTTP response").toBe(200);
        const body = await response.json();
        expect(body.deterministic).toBe(true);
        await expect(page.locator(scene.result).first()).toBeVisible({ timeout: 10_000 });
        await expect.poll(async () =>
          page.evaluate(() => document.documentElement.scrollWidth <= document.documentElement.clientWidth)
        ).toBe(true);
        await page.screenshot({
          path: "test-results/tj0071-"+scene.name+"-"+viewport.label+".png",
          fullPage: true,
          animations: "disabled",
        });
      });
    }
  });
}
