import { test, expect } from "@playwright/test";

/**
 * Admin AI dream explanation (TJ-028.1 sub-slice).
 *
 * Runs against a LOCAL backend on 127.0.0.1:8000 started with
 * TIANJI_ADMIN_READ_TOKEN=test-admin-token and NO TIANJI_AI_* variables
 * (see the task report for the exact command). The local public checkout
 * has no production runtime, so the audited lookup fails closed and the
 * AI-explain endpoint answers 422: this spec verifies the wired flow
 * and the error feedback through real HTTP, not the explained path.
 * The explained path (claims rendered from a mock model) is verified
 * at the HTTP level in tests/test_tj0281_dream_ai_http.py; a browser
 * check of it needs a runtime-capable environment.
 */

test("AI explain action is present and no API calls happen on load", async ({ page }) => {
  const apiCalls: string[] = [];
  page.on("request", (request) => {
    if (new URL(request.url()).pathname.startsWith("/api/")) apiCalls.push(request.url());
  });
  await page.goto("/admin/dream-research");
  await expect(page.getByRole("heading", { name: "解梦知识检索实验台" })).toBeVisible();
  await expect(page.getByRole("button", { name: "AI 解释（研究草稿）" })).toBeVisible();
  expect(apiCalls).toEqual([]);
  await expect(page.locator(".admin-dream-results")).toHaveCount(0);
});

test("AI explain requires a valid token and surfaces the error", async ({ page }) => {
  await page.goto("/admin/dream-research");
  await page.getByLabel("管理端访问令牌").fill("not-an-admin-token");
  await page.getByLabel("梦境叙述").fill("我梦见自己死了");
  await page.getByRole("button", { name: "AI 解释（研究草稿）" }).click();
  await expect(page.getByRole("alert")).toBeVisible();
  await expect(page.locator(".admin-dream-results")).toHaveCount(0);
});

test("AI explain with a valid token reaches the endpoint and reports its failure", async ({ page }) => {
  const statuses: number[] = [];
  page.on("response", (response) => {
    if (new URL(response.url()).pathname.endsWith("/admin/research/dream/ai-explain")) {
      statuses.push(response.status());
    }
  });
  await page.goto("/admin/dream-research");
  await page.getByLabel("管理端访问令牌").fill("test-admin-token");
  await page.getByLabel("梦境叙述").fill("我梦见自己死了");
  await page.getByRole("button", { name: "AI 解释（研究草稿）" }).click();
  await expect(page.getByRole("alert")).toBeVisible();
  await expect(page.getByRole("alert")).toContainText("Dream narrative");
  // The request really reached the backend: without the assembled
  // runtime the endpoint fails closed with 422, it is not a network
  // error and no AI claims are rendered.
  await expect.poll(() => statuses).toEqual([422]);
  await expect(page.locator(".admin-dream-results")).toHaveCount(0);
});
