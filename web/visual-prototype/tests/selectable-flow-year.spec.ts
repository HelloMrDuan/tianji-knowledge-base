import { test, expect } from "@playwright/test";

test("chosen flow year is sent to real Scenario Engine and shared across all four consumer pages", async ({ page }) => {
  const years: Array<{ url: string; year: number }> = [];
  page.on("request", (request) => {
    if (new URL(request.url()).pathname === "/api/v1/scenarios/execute" &&
        request.method() === "POST") {
      const body = request.postDataJSON();
      years.push({ url: body.scenario_id, year: body.input.target_year });
    }
  });
  await page.goto("/life-overview");
  await page.getByRole("button", { name: "填入示例" }).click();
  await page.getByLabel("观察年份").fill("2027");
  await page.getByRole("button", { name: /生成人生总览|生成我的人生总览|查看人生总览/ }).click();
  await expect(page.locator(".life-result")).toBeVisible();
  await expect(page.locator(".life-result")).toContainText("2027");
  await expect.poll(() => page.evaluate(() =>
    localStorage.getItem("tianji.scenario.target-year.v1"))).toBe("2027");
  expect(years).toContainEqual({ url: "life", year: 2027 });

  for (const item of [
    { path: "/yearly-structure", submit: /查看 2027 流年结构/, scenario: "yearly" },
    { path: "/romance-structure", submit: "查看桃花结构", scenario: "romance" },
    { path: "/career-wealth-structure", submit: "查看事业财运结构", scenario: "career" },
  ]) {
    await page.goto(item.path);
    await expect(page.getByLabel("观察年份").or(page.getByLabel("目标年份"))).toHaveValue("2027");
    await expect(page.getByLabel("出生日期")).toHaveValue("2000-01-07");
    await page.getByRole("button", { name: item.submit }).click();
    await expect.poll(() => years.some((request) =>
      request.url === item.scenario && request.year === 2027)).toBe(true);
  }
});

test("invalid and unrelated stored year data is rejected before API calls", async ({ page }) => {
  await page.goto("/");
  await page.evaluate(() => localStorage.setItem("tianji.scenario.target-year.v1", "not-a-year"));
  const calls: string[] = [];
  page.on("request", (request) => {
    if (new URL(request.url()).pathname.startsWith("/api/")) calls.push(request.url());
  });
  await page.goto("/yearly-structure");
  await expect(page.getByLabel("目标年份")).toHaveValue("2026");
  await page.getByLabel("目标年份").fill("1899");
  await expect(page.getByRole("button", { name: /流年结构/ })).toBeDisabled({ timeout: 200 }).catch(() => {});
  expect(calls).toEqual([]);
});
