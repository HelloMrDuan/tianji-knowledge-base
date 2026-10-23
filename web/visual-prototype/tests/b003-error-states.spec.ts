import { test, expect } from "@playwright/test";

/** B003: error prompts and duplicate-submit protection.
 *  [fault-injection] tests use route.abort to simulate backend failure.
 *  [real-backend] tests hit the live API with no mocks.
 */

test("[fault-injection] B003 API down: exact Chinese prompt, no empty result", async ({ page }) => {
  await page.route("**/api/**", route => route.abort("failed"));
  await page.goto("/bazi-profile");
  await page.getByRole("button", { name: "填入示例", exact: true }).click();
  await page.getByRole("button", { name: "生成基础档案" }).click();
  const alert = page.locator('[role="alert"]');
  await expect(alert).toBeVisible({ timeout: 15000 });
  // Exact prompt required: a non-empty alert alone does not prove the UX contract.
  await expect(alert).toHaveText("网络连接失败，请检查网络后重试。");
  await expect(page.locator(".bazi-live-result")).toHaveCount(0);
});

test("[real-backend] B003 duplicate submit: exactly one API request", async ({ page }) => {
  const apiCalls: string[] = [];
  page.on("request", r => {
    if (new URL(r.url()).pathname === "/api/v1/public/execute" && r.method() === "POST")
      apiCalls.push(r.url());
  });
  await page.goto("/bazi-profile");
  await page.getByRole("button", { name: "填入示例", exact: true }).click();
  await page.getByRole("button", { name: "生成基础档案" }).dblclick();
  await expect(page.locator(".bazi-live-result")).toBeVisible({ timeout: 20000 });
  // Strict: rapid double-click must produce exactly one request, not "at most two".
  expect(apiCalls).toHaveLength(1);
});

test("[real-backend] B003 force-click while request in-flight: still one request", async ({ page }) => {
  const apiCalls: string[] = [];
  // Delay the API response so the forced second click lands while the first is pending.
  // force:true bypasses Playwright's actionability wait (which would otherwise wait
  // for the button to re-enable), simulating a real user double-clicking fast.
  await page.route("**/api/v1/public/execute", async route => {
    await new Promise(res => setTimeout(res, 2500));
    await route.continue();
  });
  page.on("request", r => {
    if (new URL(r.url()).pathname === "/api/v1/public/execute" && r.method() === "POST")
      apiCalls.push(r.url());
  });
  await page.goto("/bazi-profile");
  await page.getByRole("button", { name: "填入示例", exact: true }).click();
  const btn = page.locator(".bazi-submit"); // stable selector: text changes to 正在计算… while loading
  await btn.click();
  await page.waitForTimeout(400); // first request now in-flight
  await expect(btn).toBeDisabled(); // button must be disabled while loading
  await btn.click({ force: true }); // bypass disabled: must still not issue a second request
  await expect(page.locator(".bazi-live-result")).toBeVisible({ timeout: 25000 });
  expect(apiCalls).toHaveLength(1);
});
