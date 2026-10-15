import { expect, test } from "@playwright/test";

/** TJ-007.2: 3 real calculation result pages x 3 viewports, private Actions only. */
const scenes = [
  { name: "romance", route: "/romance-structure", result: ".romance-result" },
  { name: "career", route: "/career-wealth-structure", result: ".career-result" },
  { name: "compatibility", route: "/compatibility-structure", result: ".compat-result" },
] as const;
const sizes = [
  { width: 1440, height: 900, name: "desktop" },
  { width: 390, height: 844, name: "mobile390" },
  { width: 360, height: 740, name: "mobile360" },
] as const;

for (const size of sizes) {
  test.describe("TJ-007.2 live "+size.name+" results", () => {
    test.use({ viewport: { width: size.width, height: size.height } });
    for (const scene of scenes) {
      test(scene.name+": synthetic-data screenshot AFTER actual API calculation", async ({ page }) => {
        await page.goto("/bazi-profile");
        await page.getByRole("button", { name: "填入示例" }).click();
        await page.getByRole("button", { name: "保存资料" }).click();
        await page.goto(scene.route);
        if (scene.name === "compatibility") {
          const b = page.locator(".compat-person-input").nth(1);
          await b.locator('input[type="date"]').fill("1995-06-20");
          await b.locator('input[type="time"]').fill("09:00");
        } else {
          await page.getByLabel("观察年份").fill("2026");
        }
        const pending = page.waitForResponse(r =>
          new URL(r.url()).pathname === "/api/v1/scenarios/public" && r.request().method() === "POST",
          { timeout: 40_000 });
        await page.locator('form button[type="submit"]').first().click();
        const response = await pending;
        expect(response.status()).toBe(200);
        const body = await response.json();
        expect(body.deterministic).toBe(true);
        expect(body.scenario_id).toBe(scene.name);
        await expect(page.locator(scene.result)).toBeVisible();
        await expect.poll(async () => page.evaluate(() =>
          document.documentElement.scrollWidth <= document.documentElement.clientWidth)).toBe(true);
        await page.screenshot({
          path: "test-results/tj0072-"+scene.name+"-"+size.name+".png",
          animations: "disabled",
          fullPage: true,
        });
      });
    }
  });
}
