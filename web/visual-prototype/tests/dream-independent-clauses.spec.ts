import { test, expect } from "@playwright/test";

test("new self-dream after a temporal connector retains only reviewed grounded scene", async ({ page }) => {
  await page.goto("/dream-culture");
  const narrative = page.getByLabel("梦境叙述");
  await narrative.fill("我梦见没有被蛇咬后来我梦见我捡到了钱");
  await page.getByRole("button", { name: "查阅梦象" }).click();
  const matches = page.locator(".dream-culture-match");
  await expect(matches).toHaveCount(1);
  await expect(matches).toContainText("拾得钱物皆大吉");
  await expect(matches).not.toContainText("蛇咬人主得大财");

  await narrative.fill("我梦见我捡到了钱后来发现只是想象");
  await page.getByRole("button", { name: "查阅梦象" }).click();
  await expect(page.getByRole("heading", { name: "暂无可核验的对应条目" })).toBeVisible();
  await expect(matches).toHaveCount(0);
});


test("explicit another dream keeps the first affirmed scene even when second is denied", async ({ page }) => {
  await page.goto("/dream-culture");
  const input = page.getByLabel("梦境叙述");
  await input.fill("我梦见被蛇咬了但是我又梦见我没有捡到钱");
  await page.getByRole("button", { name: "查阅梦象" }).click();
  const matches = page.locator(".dream-culture-match");
  await expect(matches).toHaveCount(1);
  await expect(matches).toContainText("蛇咬人主得大财");
  await expect(matches).not.toContainText("拾得钱物皆大吉");

  await input.fill("我梦见被蛇咬了但我梦见没有被蛇咬");
  await page.getByRole("button", { name: "查阅梦象" }).click();
  await expect(page.getByRole("heading", { name: "暂无可核验的对应条目" })).toBeVisible();
});

test("reported snake hearsay does not suppress an independently affirmed self dream", async ({ page }) => {
  await page.goto("/dream-culture");
  const input = page.getByLabel("梦境叙述");
  const matches = page.locator(".dream-culture-match");

  await input.fill("听说别人被蛇咬随后我也梦见我捡到了钱");
  await page.getByRole("button", { name: "查阅梦象" }).click();
  await expect(matches).toHaveCount(1);
  await expect(matches).toContainText("拾得钱物皆大吉");
  await expect(matches).not.toContainText("蛇咬人主得大财");

  await input.fill("听说别人被蛇咬随后我也梦见我没有捡到钱");
  await page.getByRole("button", { name: "查阅梦象" }).click();
  await expect(page.getByRole("heading", { name: "暂无可核验的对应条目" })).toBeVisible();
  await expect(matches).toHaveCount(0);
});
