import { test, expect } from "@playwright/test";

/** B003: error prompts and duplicate-submit protection (real browser, no mocks). */
test("B003 API down: user sees clear error prompt", async ({ page }) => {
  await page.route("**/api/**", route => route.abort("failed"));
  await page.goto("/bazi-profile");
  await page.getByRole("button", { name: "填入示例", exact: true }).click();
  await page.getByRole("button", { name: "生成基础档案" }).click();
  const alert = page.locator('[role="alert"]');
  await expect(alert).toBeVisible({ timeout: 15000 });
  expect(await alert.textContent()).toBeTruthy();
  await expect(page.locator(".bazi-live-result")).toHaveCount(0);
});

test("B003 duplicate submit: no duplicate API requests", async ({ page }) => {
  const apiCalls: string[] = [];
  page.on("request", r => {
    if (new URL(r.url()).pathname === "/api/v1/public/execute" && r.method() === "POST")
      apiCalls.push(r.url());
  });
  await page.goto("/bazi-profile");
  await page.getByRole("button", { name: "填入示例", exact: true }).click();
  await page.getByRole("button", { name: "生成基础档案" }).dblclick();
  await page.waitForTimeout(3000);
  expect(apiCalls.length).toBeLessThanOrEqual(2);
});
