/**
 * B018 TJ-026.4 batch 1: role blocking + audit visibility (frontend).
 *
 * Controlled synthetic HTTP contracts (page.route stubs), explicitly
 * labeled: no real backend is required, so this spec runs in public CI.
 * The REAL 403/audit behaviors of the backend are additionally verified
 * by tests/test_b018_admin_roles_http.py (offline acceptance, real
 * server code); this spec verifies the FRONTEND renders the reused
 * TJ-026.3 403 prompt for a denied probe and shows audit records,
 * instead of inventing a second error copy or demo data.
 *
 * The probe page itself never persists a token (component state only);
 * the stub tokens below are synthetic and match nothing server-side.
 */
import { test, expect } from "@playwright/test";

const FORBIDDEN_403 = "令牌权限不足，无法访问该受控数据（scope 不足）。";

test("user-role probe renders the reused 403 prompt", async ({ page }) => {
  await page.route("**/api/v1/admin/write/probe", (route) =>
    route.fulfill({
      status: 403,
      json: {
        detail: { code: "admin_forbidden", message: "Admin role does not allow publish" },
      },
    }),
  );
  await page.goto("/admin/write-probe");
  await page.getByLabel("角色令牌").fill("b018-stub-user-token");
  await page.getByLabel("发布").check();
  await page.locator('form button[type="submit"]').first().click();
  await expect(page.getByRole("alert").first()).toContainText(FORBIDDEN_403);
});

test("editor-role probe renders success and no-write honesty note", async ({
  page,
}) => {
  await page.route("**/api/v1/admin/write/probe", (route) =>
    route.fulfill({
      status: 200,
      json: {
        api_version: "v1",
        probe: true,
        operation: "draft",
        role: "editor",
        write_applied: false,
        note: "Batch 1 checkpoint only.",
      },
    }),
  );
  await page.goto("/admin/write-probe");
  await page.getByLabel("角色令牌").fill("b018-stub-editor-token");
  await page.getByLabel("起草").check();
  await page.locator('form button[type="submit"]').first().click();
  const result = page.locator(".admin-probe-results").first();
  await expect(result).toContainText("editor");
  await expect(result).toContainText("draft");
  await expect(result).toContainText("未产生真实写入");
});

test("audit viewer renders stubbed records with who/when/what/outcome", async ({
  page,
}) => {
  await page.route("**/api/v1/admin/system/audit", (route) =>
    route.fulfill({
      status: 200,
      json: {
        api_version: "v1",
        read_only: true,
        public_release: false,
        entries: [
          {
            who: "editor",
            when: "2026-10-25T00:00:00+00:00",
            what: "write_probe:draft",
            outcome: "allowed",
            detail: null,
          },
          {
            who: "user",
            when: "2026-10-25T00:01:00+00:00",
            what: "write_probe:publish",
            outcome: "denied",
            detail: "forbidden",
          },
        ],
      },
    }),
  );
  await page.goto("/admin/write-probe");
  await page.getByLabel("后台只读令牌").fill("b018-stub-read-token");
  await page.getByRole("button", { name: "查看审计记录" }).click();
  const table = page.locator(".admin-probe-table");
  await expect(table).toBeVisible();
  await expect(table).toContainText("editor");
  await expect(table).toContainText("write_probe:draft");
  await expect(table).toContainText("通过");
  await expect(table).toContainText("user");
  await expect(table).toContainText("write_probe:publish");
  await expect(table).toContainText("拒绝");
});

test("audit viewer without system scope renders the reused 403 prompt", async ({
  page,
}) => {
  await page.route("**/api/v1/admin/system/audit", (route) =>
    route.fulfill({
      status: 403,
      json: {
        detail: { code: "admin_forbidden", message: "Admin token scope does not include system" },
      },
    }),
  );
  await page.goto("/admin/write-probe");
  await page.getByLabel("后台只读令牌").fill("b018-stub-read-token");
  await page.getByRole("button", { name: "查看审计记录" }).click();
  await expect(page.getByRole("alert").last()).toContainText(FORBIDDEN_403);
});

test("probe page requests nothing without a token", async ({ page }) => {
  const apiCalls: string[] = [];
  page.on("request", (request) => {
    if (new URL(request.url()).pathname.startsWith("/api/")) {
      apiCalls.push(request.url());
    }
  });
  await page.goto("/admin/write-probe");
  await expect(page.getByLabel("角色令牌")).toBeVisible();
  expect(apiCalls).toEqual([]);
});
