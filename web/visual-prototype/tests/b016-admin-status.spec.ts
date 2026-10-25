/**
 * B016 TJ-026.3: controlled-page 401/403/404 status branching.
 *
 * Controlled synthetic HTTP contracts (page.route stubs), explicitly
 * labeled: no real backend is required, so this spec runs in public CI.
 * The REAL 401/403 behaviors of the backend are additionally verified by
 * tests/test_b016_admin_scope_http.py (offline acceptance, real server
 * code); this spec verifies the FRONTEND renders a distinct message per
 * status instead of collapsing all three into one generic fallback.
 *
 * Each controlled page shares the same token form (label "后台只读令牌")
 * and error slot (role="alert"), so one table-driven spec covers all 11
 * pages outside dream-research (which has its own spec).
 */
import { test, expect } from "@playwright/test";

const PAGES = [
  { path: "/admin/rules", endpoint: "/api/v1/admin/governance/rules" },
  { path: "/admin/evidence", endpoint: "/api/v1/admin/governance/evidence" },
  { path: "/admin/classics", endpoint: "/api/v1/admin/governance/classics" },
  { path: "/admin/chapters", endpoint: "/api/v1/admin/governance/chapters" },
  { path: "/admin/terms", endpoint: "/api/v1/admin/governance/terms" },
  { path: "/admin/sources", endpoint: "/api/v1/admin/governance/sources" },
  { path: "/admin/layers", endpoint: "/api/v1/admin/governance/layers" },
  { path: "/admin/algorithms", endpoint: "/api/v1/admin/governance/algorithms" },
  { path: "/admin/conflicts", endpoint: "/api/v1/admin/governance/conflicts" },
  { path: "/admin/providers", endpoint: "/api/v1/admin/system/provider" },
  { path: "/admin/prompts", endpoint: "/api/v1/admin/system/prompts" },
] as const;

const STATES = [
  {
    status: 401,
    body: { detail: { code: "admin_unauthorized", message: "Invalid admin bearer token" } },
    message: "后台访问令牌无效或缺失，请重新输入令牌。",
  },
  {
    status: 403,
    body: { detail: { code: "admin_forbidden", message: "Admin token scope does not include governance" } },
    message: "令牌权限不足，无法访问该受控数据（scope 不足）。",
  },
  {
    // FastAPI's real 404 body has no code field; the frontend must branch
    // on the STATUS, not on a body code.
    status: 404,
    body: { detail: "Not Found" },
    message: "受控页或端点不存在。",
  },
] as const;

for (const pageDef of PAGES) {
  for (const state of STATES) {
    test(`${pageDef.path} renders a distinct message for HTTP ${state.status}`, async ({ page }) => {
      await page.route(`**${pageDef.endpoint}`, (route) =>
        route.fulfill({ status: state.status, json: state.body }),
      );
      await page.goto(pageDef.path);
      await page.getByLabel("后台只读令牌").fill("b016-stub-token");
      await page.locator("form button").first().click();
      await expect(page.getByRole("alert")).toContainText(state.message);
      // The three states must not collapse into one another.
      for (const other of STATES) {
        if (other.status !== state.status) {
          await expect(page.getByRole("alert")).not.toContainText(other.message);
        }
      }
    });
  }
}

test("controlled pages request nothing without a token", async ({ page }) => {
  const apiCalls: string[] = [];
  page.on("request", (request) => {
    if (new URL(request.url()).pathname.startsWith("/api/")) {
      apiCalls.push(request.url());
    }
  });
  await page.goto("/admin/rules");
  await expect(page.getByLabel("后台只读令牌")).toBeVisible();
  expect(apiCalls).toEqual([]);
});

test("controlled pages never store the token in localStorage", async ({ page }) => {
  await page.route("**/api/v1/admin/governance/rules", (route) =>
    route.fulfill({
      status: 401,
      json: { detail: { code: "admin_unauthorized", message: "Invalid" } },
    }),
  );
  await page.goto("/admin/rules");
  await page.getByLabel("后台只读令牌").fill("b016-stub-token");
  await page.locator("form button").first().click();
  await expect(page.getByRole("alert")).toBeVisible();
  expect(
    await page.evaluate(() =>
      Object.keys(localStorage).filter((key) => key.includes("token")),
    ),
  ).toEqual([]);
});
