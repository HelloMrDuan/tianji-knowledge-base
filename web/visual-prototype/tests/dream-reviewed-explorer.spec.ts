import { test, expect } from "@playwright/test";

test("ten verified dream example cards populate inputs without canned answers", async ({ page }) => {
  const calls: string[] = [];
  page.on("request", (request) => {
    if (request.method() === "POST" &&
        new URL(request.url()).pathname === "/api/v1/dream/culture") {
      calls.push(request.postData() || "");
    }
  });
  await page.goto("/dream-culture");
  const library = page.getByLabel("已审核梦象示例");
  await expect(library.locator("button")).toHaveCount(10);
  expect(calls).toHaveLength(0);

  await page.getByRole("button", { name: "填入蛇咬梦境示例" }).click();
  await expect(page.getByLabel("梦境叙述")).toHaveValue("我梦见一条蛇咬住我的手");
  await expect(page.getByRole("button", { name: "填入蛇咬梦境示例" })).toHaveAttribute("aria-pressed", "true");
  expect(calls).toHaveLength(0);

  await page.getByRole("button", { name: "查阅梦象" }).click();
  await expect(page.locator(".dream-culture-match")).toContainText("蛇咬人主得大财");
  expect(calls).toHaveLength(1);

  await page.getByRole("button", { name: "填入拾钱梦境示例" }).click();
  await expect(page.locator(".dream-culture-match")).toHaveCount(0);
  await expect(page.getByLabel("梦境叙述")).toHaveValue("我梦见我捡到了钱");
  expect(calls).toHaveLength(1);

  await page.getByRole("button", { name: "查阅梦象" }).click();
  await expect(page.locator(".dream-culture-match")).toContainText("拾得钱物皆大吉");
  expect(calls).toHaveLength(2);
  expect(JSON.parse(calls[1])).toEqual({ dream_text: "我梦见我捡到了钱" });
});

test("verified scene cards remain readable and accessible on mobile", async ({ page }) => {
  await page.setViewportSize({ width: 360, height: 844 });
  await page.goto("/dream-culture");
  await expect(page.getByLabel("已审核梦象示例").locator("button")).toHaveCount(10);
  await page.getByRole("button", { name: "填入游鱼梦境示例" }).click();
  await expect(page.getByLabel("梦境叙述")).toHaveValue("我梦见一群鱼在水里游");
  await expect(page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).resolves.toBe(true);
});
