import { test, expect } from "@playwright/test";

test("reviewed dream culture lookup uses real API and clears stale results", async ({ page }) => {
  const publicCalls: string[] = [];
  const privateCalls: string[] = [];
  page.on("request", (request) => {
    const url = new URL(request.url()).pathname;
    if (url === "/api/v1/dream/culture") publicCalls.push(request.postData() || "");
    if (url.startsWith("/api/v1/admin/")) privateCalls.push(url);
  });
  await page.goto("/");
  await page.getByRole("link", { name: /传统梦象查阅/ }).click();
  await expect(page.getByRole("heading", { name: "昨夜一梦，古书如何记载？" })).toBeVisible();
  expect(publicCalls).toEqual([]);
  await page.getByLabel("梦境叙述").fill("我梦见被蛇咬了");
  await page.getByRole("button", { name: "查阅梦象" }).click();
  await expect(page.getByRole("heading", { name: "梦象查阅结果" })).toBeVisible();
  await expect(page.locator(".dream-culture-match")).toHaveCount(1);
  await expect(page.locator(".dream-culture-match")).toContainText("蛇咬人主得大财");
  expect(publicCalls).toHaveLength(1);
  expect(JSON.parse(publicCalls[0])).toEqual({ dream_text: "我梦见被蛇咬了" });
  expect(privateCalls).toEqual([]);
  await page.getByLabel("梦境叙述").fill("梦见考试");
  await expect(page.locator(".dream-culture-match")).toHaveCount(0);
  await page.getByRole("button", { name: "查阅梦象" }).click();
  await expect(page.getByRole("heading", { name: "暂无可核验的对应条目" })).toBeVisible();
  expect(publicCalls).toHaveLength(2);
  expect(privateCalls).toEqual([]);
  expect(await page.evaluate(() => Object.keys(localStorage).filter((key) => /dream|token/i.test(key)))).toEqual([]);
});

test("contrastive dream example sends real input and shows only the affirmed citation", async ({ page }) => {
  const requests: string[] = [];
  page.on("request", (request) => {
    if (new URL(request.url()).pathname === "/api/v1/dream/culture")
      requests.push(request.postData() || "");
  });
  await page.goto("/dream-culture");
  await page.getByRole("button", { name: "填入多场景示例" }).click();
  const narrative = "我梦见没有被蛇咬但我梦见我捡到了钱。";
  await expect(page.getByLabel("梦境叙述")).toHaveValue(narrative);
  expect(requests).toHaveLength(0);
  await page.getByRole("button", { name: "查阅梦象" }).click();
  await expect(page.locator(".dream-culture-match")).toHaveCount(1);
  await expect(page.locator(".dream-culture-match")).toContainText("拾得钱物皆大吉");
  await expect(page.locator(".dream-culture-match")).not.toContainText("蛇咬人主得大财");
  expect(JSON.parse(requests[0])).toEqual({ dream_text: narrative });
});

test("dream lookup on mobile never renders a fabricated answer for reported or negated scenes", async ({ page }) => {
  await page.setViewportSize({ width: 360, height: 844 });
  await page.goto("/dream-culture");
  const narrative = page.getByLabel("梦境叙述");
  for (const value of ["梦见没有被蛇咬", "梦见电影里被蛇咬了"]) {
    await narrative.fill(value);
    await page.getByRole("button", { name: "查阅梦象" }).click();
    await expect(page.getByRole("heading", { name: "暂无可核验的对应条目" })).toBeVisible();
    await expect(page.locator(".dream-culture-match")).toHaveCount(0);
  }
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
});


test("additional reviewed dream phrasings retrieve real citations but reject imagined events", async ({ page }) => {
  await page.goto("/dream-culture");
  const narrative = page.getByLabel("梦境叙述");
  for (const [dream, excerpt] of [
    ["我梦见一条蛇咬住我的手", "蛇咬人主得大财"],
    ["我梦见我拾得一枚铜钱", "拾得钱物皆大吉"],
    ["我梦见我飞向天空", "飞上天富贵大吉"],
    ["我梦见我跌落井中", "身坠井中疾病凶"],
  ]) {
    await narrative.fill(dream);
    await page.getByRole("button", { name: "查阅梦象" }).click();
    await expect(page.locator(".dream-culture-match")).toHaveCount(1);
    await expect(page.locator(".dream-culture-match")).toContainText(excerpt);
  }
  await narrative.fill("我梦见我没有跌落井中");
  await page.getByRole("button", { name: "查阅梦象" }).click();
  await expect(page.getByRole("heading", { name: "暂无可核验的对应条目" })).toBeVisible();
});

test("mixed dream reveals unreviewed exam without fabricating a classical source", async ({ page }) => {
  await page.goto("/dream-culture");
  await page.getByLabel("梦境叙述").fill("我梦见我捡到了钱，后来梦见考试");
  await page.getByRole("button", { name: "查阅梦象" }).click();
  await expect(page.locator(".dream-culture-match")).toHaveCount(1);
  await expect(page.locator(".dream-culture-match")).toContainText("拾得钱物皆大吉");
  const unresolved = page.getByLabel("未获审核的梦境主题");
  await expect(unresolved).toContainText("考试");
  await expect(unresolved).toContainText("尚无严格对应的已审核条目");
  await expect(unresolved).not.toContainText("古籍原文");
  await page.getByLabel("梦境叙述").fill("听说别人梦见考试");
  await page.getByRole("button", { name: "查阅梦象" }).click();
  await expect(unresolved).toHaveCount(0);
  await expect(page.locator(".dream-culture-match")).toHaveCount(0);
});
