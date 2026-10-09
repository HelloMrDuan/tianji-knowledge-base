import { test, expect } from "@playwright/test";

test("real Bazi and yearly charts clear as soon as birth inputs change", async ({ page }) => {
  await page.goto("/bazi-profile");
  await page.getByRole("button", { name: "填入示例" }).click();
  await page.getByRole("button", { name: "生成基础档案" }).click();
  await expect(page.locator(".bazi-live-result")).toBeVisible();

  await page.getByLabel("出生日期").fill("2000-01-08");
  await expect(page.locator(".bazi-live-result")).toHaveCount(0);
  await page.getByRole("button", { name: "生成基础档案" }).click();
  await expect(page.locator(".bazi-live-result")).toBeVisible();
  await page.getByLabel("出生时间").fill("13:00");
  await expect(page.locator(".bazi-live-result")).toHaveCount(0);

  await page.goto("/yearly-structure");
  await page.getByLabel("目标年份").fill("2027");
  await page.getByRole("button", { name: /查看 2027 流年结构/ }).click();
  await expect(page.locator(".yearly-result")).toBeVisible();
  await page.getByLabel("出生时间").fill("14:00");
  await expect(page.locator(".yearly-result")).toHaveCount(0);
  await expect(page.locator(".yearly-seal strong")).toHaveText("待计算");
});

test("late real Bazi API response cannot repopulate an edited birth chart", async ({ page }) => {
  await page.goto("/bazi-profile");
  await page.getByRole("button", { name: "填入示例" }).click();
  let responseIntercepted: (() => void) | undefined;
  let releaseResponse: (() => void) | undefined;
  const intercepted = new Promise<void>((resolve) => { responseIntercepted = resolve; });
  const released = new Promise<void>((resolve) => { releaseResponse = resolve; });
  await page.route("**/api/v1/public/execute", async (route) => {
    // Fetch the actual backend response; only delay delivery to reproduce a race.
    const actual = await route.fetch();
    responseIntercepted?.();
    await released;
    await route.fulfill({ response: actual });
  });

  await page.getByRole("button", { name: "生成基础档案" }).click();
  await intercepted;
  await page.getByLabel("出生日期").fill("2000-01-08");
  await expect(page.getByRole("button", { name: "生成基础档案" })).toBeVisible();
  const finished = page.waitForResponse((response) =>
    new URL(response.url()).pathname === "/api/v1/public/execute");
  releaseResponse?.();
  await finished;
  await page.waitForTimeout(150);
  await expect(page.locator(".bazi-live-result")).toHaveCount(0);
  expect(await page.evaluate(() => localStorage.getItem("tianji.profile.birth.v1"))).toBeNull();
});
