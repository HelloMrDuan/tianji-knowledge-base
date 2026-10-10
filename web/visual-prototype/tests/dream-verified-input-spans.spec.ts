import { test, expect } from "@playwright/test";

test("new bounded dream phrasing shows the user's exact matched scene next to reviewed source", async ({ page }) => {
  const requests: string[] = [];
  page.on("request", (request) => {
    if (new URL(request.url()).pathname === "/api/v1/dream/culture")
      requests.push(request.postData() || "");
  });
  await page.goto("/dream-culture");
  const field = page.getByLabel("梦境叙述");
  await field.fill("我梦见我拾起一枚硬币，我梦见一群鱼儿在湖里游来游去。");
  await page.getByRole("button", { name: "查阅梦象" }).click();
  const matches = page.locator(".dream-culture-match");
  await expect(matches).toHaveCount(2);
  await expect(matches.first()).toContainText("对应梦中原话");
  await expect(matches).toContainText(["一群鱼儿在湖里游来游去", "我拾起一枚硬币"]);
  await expect(page.locator(".dream-culture-match blockquote")).toHaveCount(2);
  expect(requests).toHaveLength(1);

  await field.fill("我梦见没有拾起一枚硬币");
  await expect(matches).toHaveCount(0);
  await page.getByRole("button", { name: "查阅梦象" }).click();
  await expect(page.getByRole("heading", { name: "暂无可核验的对应条目" })).toBeVisible();
});
