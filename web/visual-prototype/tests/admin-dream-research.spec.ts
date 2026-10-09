import { test, expect } from "@playwright/test";

test("private dream workbench is an actual admin route and does not fetch without action", async ({ page }) => {
  const apiCalls: string[] = [];
  page.on("request", (request) => {
    if (new URL(request.url()).pathname.startsWith("/api/")) apiCalls.push(request.url());
  });
  await page.goto("/admin/dream-research");
  await expect(page.getByRole("heading", { name: "解梦知识检索实验台" })).toBeVisible();
  await expect(page.getByLabel("管理端访问令牌")).toBeVisible();
  await expect(page.getByLabel("梦境叙述")).toBeVisible();
  expect(apiCalls).toEqual([]);
  await expect(page.locator(".admin-dream-results")).toHaveCount(0);
});

test("dream lab requires auth token and does not save secrets or display unreviewed text", async ({ page }) => {
  await page.goto("/admin/dream-research");
  await page.getByLabel("管理端访问令牌").fill("not-an-admin-token");
  await page.getByLabel("梦境叙述").fill("我梦见被蛇咬了");
  await page.getByRole("button", { name: "检索真实梦象知识" }).click();
  await expect(page.getByRole("alert")).toBeVisible();
  await expect(page.locator(".admin-dream-results")).toHaveCount(0);
  expect(await page.evaluate(() => Object.keys(localStorage).filter((key) => key.includes("token")))).toEqual([]);
  await page.getByRole("link", { name: "仪表盘" }).click();
  await page.getByRole("link", { name: "解梦知识研究" }).click();
  await expect(page.getByLabel("管理端访问令牌")).toHaveValue("");
});
