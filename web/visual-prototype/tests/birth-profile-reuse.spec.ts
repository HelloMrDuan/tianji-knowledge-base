import { test, expect } from "@playwright/test";

const profileKey = "tianji.profile.birth.v1";

test("real Bazi API establishes browser-local profile reused by yearly romance and career", async ({ page }) => {
  await page.goto("/bazi-profile");
  await expect(page.getByLabel("出生日期")).toHaveValue("");
  await page.getByRole("button", { name: "填入示例" }).click();
  await page.getByRole("button", { name: "生成基础档案" }).click();
  await expect(page.locator(".bazi-live-result")).toBeVisible();
  await expect(page.locator(".bazi-pillars article")).toHaveCount(4);
  await expect.poll(() => page.evaluate(
    (key) => localStorage.getItem(key), profileKey
  )).toBe('{"date":"2000-01-07","time":"12:00"}');

  for (const [route, submitLabel] of [
    ["/yearly-structure", "查看 2026 流年结构"],
    ["/romance-structure", "查看桃花结构"],
    ["/career-wealth-structure", "查看事业财运结构"],
  ]) {
    await page.goto(route);
    await expect(page.getByLabel("出生日期")).toHaveValue("2000-01-07");
    await expect(page.getByLabel("出生时间")).toHaveValue("12:00");
    await expect(page.getByRole("button", { name: submitLabel })).toBeVisible();
  }

  await page.goto("/bazi-profile");
  await expect(page.getByLabel("出生日期")).toHaveValue("2000-01-07");
  await page.getByRole("button", { name: "清除本机资料" }).click();
  await expect(page.getByLabel("出生日期")).toHaveValue("");
  await expect(page.getByLabel("出生时间")).toHaveValue("");
  expect(await page.evaluate((key) => localStorage.getItem(key), profileKey)).toBeNull();
  await page.goto("/yearly-structure");
  await expect(page.getByLabel("出生日期")).toHaveValue("");
});

test("stale or malformed local values do not prefill or trigger calculations", async ({ page }) => {
  await page.goto("/");
  await page.evaluate((key) => localStorage.setItem(key,
    '{"date":"2000-02-30","time":"25:99"}'), profileKey);
  const apiRequests: string[] = [];
  page.on("request", (request) => {
    if (new URL(request.url()).pathname.startsWith("/api/")) apiRequests.push(request.url());
  });
  for (const route of ["/bazi-profile", "/yearly-structure", "/romance-structure", "/career-wealth-structure"]) {
    await page.goto(route);
    await expect(page.getByLabel("出生日期")).toHaveValue("");
    await expect(page.getByLabel("出生时间")).toHaveValue("");
  }
  expect(apiRequests).toEqual([]);
});
