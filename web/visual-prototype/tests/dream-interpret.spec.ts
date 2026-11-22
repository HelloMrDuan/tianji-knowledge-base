import { test, expect } from "@playwright/test";

/**
 * User-facing AI dream interpretation page (TJ-028.1 user slice).
 *
 * Runs against a LOCAL backend on 127.0.0.1:8000 (vite.config.ts
 * proxies /api there) and the vite dev server on 127.0.0.1:4174.
 *
 * The result tests need a runtime-capable backend (the reviewed
 * production runtime built from sealed Canonical data): the local
 * public checkout has no runtime, so the audited lookup fails
 * closed and the endpoint answers 422/503 there. Run the full spec
 * in a runtime-capable environment (trusted-machine assembly).
 * The no-backend tests (entry, examples, validation, AI status,
 * no admin calls) run anywhere.
 */

const INTERPRET = "/api/v1/dream/interpret";

test("homepage entry opens the dream interpretation page", async ({ page }) => {
  await page.goto("/");
  // The homepage card keeps its fixed display name "解梦" (presentation
  // only) and links to the new page; two card variants share the href.
  await page.locator('a[href="/dream-interpret"]').first().click();
  await expect(page.getByRole("heading", { name: "解读你的梦境" })).toBeVisible();
  await expect(page.getByText("AI 解读：未启用")).toBeVisible();
  await expect(page.getByLabel("梦境叙述")).toBeVisible();
  await expect(page.getByRole("button", { name: "解读梦境" })).toBeVisible();
  await expect(page.getByRole("button", { name: "清空" })).toBeVisible();
});

test("example fills the input without calling the API", async ({ page }) => {
  const calls: string[] = [];
  page.on("request", (request) => {
    if (request.method() === "POST" &&
        new URL(request.url()).pathname === INTERPRET) {
      calls.push(request.postData() || "");
    }
  });
  await page.goto("/dream-interpret");
  await page.getByRole("button", { name: "填入蛇咬梦境示例" }).click();
  await expect(page.getByLabel("梦境叙述")).toHaveValue("我梦见一条蛇咬住我的手");
  expect(calls).toHaveLength(0);
});

test("blank-only input shows a friendly error, clear works", async ({ page }) => {
  const calls: string[] = [];
  page.on("request", (request) => {
    if (request.method() === "POST" &&
        new URL(request.url()).pathname === INTERPRET) {
      calls.push(request.postData() || "");
    }
  });
  await page.goto("/dream-interpret");
  // Whitespace-only input passes native required/minLength checks, so
  // the page's own validation must reject it with a friendly message.
  await page.getByLabel("梦境叙述").fill("   ");
  await page.getByRole("button", { name: "解读梦境" }).click();
  await expect(page.getByRole("alert")).toContainText("请填写 2—500 字的梦境叙述。");
  expect(calls).toHaveLength(0);
  await page.getByLabel("梦境叙述").fill("我梦见一条蛇咬住我的手");
  await page.getByRole("button", { name: "清空" }).click();
  await expect(page.getByLabel("梦境叙述")).toHaveValue("");
});

test("real single-scene interpretation shows symbols, sources and AI status", async ({ page }) => {
  const calls: string[] = [];
  const adminCalls: string[] = [];
  page.on("request", (request) => {
    const url = new URL(request.url()).pathname;
    if (request.method() === "POST" && url === INTERPRET) calls.push(request.postData() || "");
    if (url.startsWith("/api/v1/admin/")) adminCalls.push(url);
  });
  await page.goto("/dream-interpret");
  await page.getByLabel("梦境叙述").fill("我梦见被蛇咬了");
  await page.getByRole("button", { name: "解读梦境" }).click();
  await expect(page.getByRole("heading", { name: "梦境解读" })).toBeVisible();
  await expect(page.locator(".dream-interpret-symbol")).toHaveCount(1);
  await expect(page.locator(".dream-interpret-symbol")).toContainText("蛇咬人主得大财");
  await expect(page.locator(".dream-interpret-symbol")).toContainText("对应梦中原话");
  await expect(page.locator(".dream-interpret-sources")).toContainText("周公解梦");
  await expect(page.locator(".dream-interpret-ai")).toContainText("未启用");
  await expect(page.locator(".dream-interpret-ai")).toContainText("AI 解读尚未启用");
  await expect(page.locator(".dream-interpret-boundaries")).toBeVisible();
  expect(calls).toHaveLength(1);
  expect(JSON.parse(calls[0])).toEqual({ dream_text: "我梦见被蛇咬了" });
  expect(adminCalls).toEqual([]);
  expect(await page.evaluate(() => Object.keys(localStorage).filter((key) => /dream|token/i.test(key)))).toEqual([]);
});

test("real two-scene dream shows both symbols and their shared-source relation", async ({ page }) => {
  await page.goto("/dream-interpret");
  await page.getByLabel("梦境叙述").fill("我梦见被蛇咬了，我梦见我捡到了钱");
  await page.getByRole("button", { name: "解读梦境" }).click();
  await expect(page.locator(".dream-interpret-symbol")).toHaveCount(2);
  await expect(page.locator(".dream-interpret-symbol").first()).toContainText("蛇咬人主得大财");
  await expect(page.locator(".dream-interpret-symbol").last()).toContainText("拾得钱物皆大吉");
  await expect(page.locator(".dream-interpret-relations")).toContainText("出处相同，含义各自独立");
  await expect(page.locator(".dream-interpret-explore")).toBeVisible();
  await expect(page.getByRole("button", { name: "填入飞天梦境示例" })).toBeVisible();
  await expect(page.getByRole("button", { name: "再解一梦" })).toBeVisible();
});

test("no reviewed interpretation gives an honest empty state", async ({ page }) => {
  await page.goto("/dream-interpret");
  await page.getByLabel("梦境叙述").fill("梦见考试");
  await page.getByRole("button", { name: "解读梦境" }).click();
  await expect(page.getByRole("heading", { name: "暂无可核验的对应条目" })).toBeVisible();
  await expect(page.locator(".dream-interpret-symbol")).toHaveCount(0);
  await expect(page.locator(".dream-interpret-ai")).toContainText("未启用");
});

test("three viewports render the real result page without horizontal overflow", async ({ page }) => {
  for (const [name, width, height] of [
    ["desktop", 1440, 900],
    ["tablet", 768, 1024],
    ["mobile", 375, 667],
  ] as const) {
    await page.setViewportSize({ width, height });
    await page.goto("/dream-interpret");
    await page.getByLabel("梦境叙述").fill("我梦见被蛇咬了，我梦见我捡到了钱");
    await page.getByRole("button", { name: "解读梦境" }).click();
    await expect(page.getByRole("heading", { name: "梦境解读" })).toBeVisible();
    await expect(page.locator(".dream-interpret-symbol")).toHaveCount(2);
    expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
    await page.screenshot({ path: `tests/screenshots/dream-interpret/result-${name}.png`, fullPage: true });
  }
});
