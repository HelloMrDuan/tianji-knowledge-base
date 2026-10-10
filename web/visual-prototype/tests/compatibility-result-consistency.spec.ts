import { test, expect } from "@playwright/test";

test("changing either partner's birth data clears a previous real compatibility result", async ({page}) => {
  const requests: string[] = [];
  page.on("request", req => {
    if (new URL(req.url()).pathname === "/api/v1/scenarios/public") requests.push(req.postData() || "");
  });
  await page.goto("/compatibility-structure");
  await page.getByRole("button", {name:"填入双人示例"}).click();
  await page.getByRole("button", {name:"生成双人结构"}).click();
  await expect(page.locator(".compat-result")).toBeVisible();
  await expect(page.locator(".compat-result-head h2")).toContainText("我 × 对方");
  const input = page.locator(".compat-person-input").nth(1).locator('input[type="date"]');
  await input.fill("2000-02-02");
  await expect(page.locator(".compat-result")).toHaveCount(0);
  await page.getByRole("button", {name:"生成双人结构"}).click();
  await expect(page.locator(".compat-result")).toBeVisible();
  expect(requests).toHaveLength(2);
  expect(JSON.parse(requests[1]).input.person_b_birth_value).toContain("2000-02-02");
});

test("each relationship evidence card shows a real source quote or explicitly abstains", async ({page}) => {
  await page.goto("/compatibility-structure");
  await page.getByRole("button", {name:"填入双人示例"}).click();
  await page.getByRole("button", {name:"生成双人结构"}).click();
  await expect(page.locator(".compat-result")).toBeVisible();
  const matrix = page.locator(".compat-matrix article");
  await expect(matrix.first()).toBeVisible();
  const cited = matrix.locator("details.compat-matrix-citations");
  if (await cited.count() > 0) {
    await cited.first().locator("summary").click();
    await expect(cited.first().locator("blockquote p").first()).not.toBeEmpty();
  } else {
    await expect(matrix.first()).toContainText("没有对应的可核验短引");
  }
  await expect(page.locator(".compat-result")).not.toContainText("该证据已由服务端绑定");
});
