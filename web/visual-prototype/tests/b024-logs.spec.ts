/**
 * B024 TJ-026.1 logs single item: logs redefined from request-tracing
 * to an audit-trail view (frontend).
 *
 * Controlled synthetic HTTP contracts (page.route stubs with fixed
 * audit entries), explicitly labeled: no real backend is required, so
 * this spec runs in public CI. The REAL /api/v1/admin/system/audit
 * endpoint behavior (system-scope gate, process-memory entries,
 * no-leakage of draft bodies) is covered by the backend's existing
 * admin tests; this spec verifies the FRONTEND wires the logs module
 * to live audit data (token form -> audit list -> entries with
 * who/when/what/outcome), renders the reused TJ-026.3 error branching
 * for 401/403/404/503-unconfigured, requests nothing before a token
 * is supplied, and shows no DEMO trace or fictional-records text.
 *
 * The logs page never persists a token (component state only); the
 * stub tokens below are synthetic and match nothing server-side.
 */
import { test, expect } from "@playwright/test";
import type { Page } from "@playwright/test";

const UNAUTHORIZED_401 = "后台访问令牌无效或缺失，请重新输入令牌。";
const FORBIDDEN_403 = "令牌权限不足，无法访问该受控数据（scope 不足）。";
const NOT_FOUND_404 = "受控页或端点不存在。";
const NOT_CONFIGURED_503 = "服务端尚未配置后台只读令牌。";

const VALID_TOKEN = "b024-stub-valid-token";

type AuditMode = "ok" | "forbidden" | "missing" | "unconfigured";

async function installAuditStub(page: Page, mode: AuditMode) {
  let requests = 0;
  await page.route("**/api/v1/admin/system/audit", async (route) => {
    requests += 1;
    const token = (route.request().headers()["authorization"] ?? "").replace(
      "Bearer ",
      "",
    );
    if (mode === "forbidden") {
      return route.fulfill({
        status: 403,
        json: {
          detail: { code: "admin_forbidden", message: "scope insufficient" },
        },
      });
    }
    if (mode === "missing") {
      return route.fulfill({
        status: 404,
        json: { detail: { code: "not_found", message: "No endpoint" } },
      });
    }
    if (mode === "unconfigured") {
      return route.fulfill({
        status: 503,
        json: {
          detail: {
            code: "admin_auth_not_configured",
            message: "Admin read token not configured",
          },
        },
      });
    }
    if (token !== VALID_TOKEN) {
      return route.fulfill({
        status: 401,
        json: {
          detail: { code: "admin_unauthorized", message: "Bad token" },
        },
      });
    }
    return route.fulfill({
      status: 200,
      json: {
        api_version: "v1",
        read_only: true,
        public_release: false,
        entries: [
          {
            who: "publisher",
            when: "2026-10-25T00:00:00+00:00",
            what: "draft_publish",
            outcome: "allowed",
            detail: "D-1",
          },
          {
            who: "editor",
            when: "2026-10-25T00:01:00+00:00",
            what: "draft_rollback",
            outcome: "denied",
            detail: null,
          },
        ],
      },
    });
  });
  return () => requests;
}

async function loadWithToken(page: Page, token: string) {
  await page.getByLabel("审计令牌").fill(token);
  await page.getByRole("button", { name: "加载审计条目" }).click();
}

test("logs renders live audit entries and requests nothing before a token", async ({
  page,
}) => {
  const requestCount = await installAuditStub(page, "ok");
  await page.goto("/admin/logs");
  // Redefined heading + process-memory label; no demo trace anywhere.
  await expect(page.getByRole("heading", { name: "审计轨迹" }).first()).toBeVisible();
  await expect(page.getByText("进程内存 · 重启丢失").first()).toBeVisible();
  await expect(page.getByText("DEMO-trace-001")).toHaveCount(0);
  await expect(page.getByText("虚构演示记录")).toHaveCount(0);
  // Route-guard contract: no request before a token is supplied.
  expect(requestCount()).toBe(0);
  await loadWithToken(page, VALID_TOKEN);
  expect(requestCount()).toBe(1);
  // Entries render with who/when/what/outcome/detail.
  await expect(page.getByText("draft_publish")).toBeVisible();
  await expect(page.getByText("publisher · 允许 · D-1")).toBeVisible();
  await expect(page.getByText("draft_rollback")).toBeVisible();
  await expect(page.getByText("editor · 拒绝")).toBeVisible();
  await expect(page.getByText("2026-10-25T00:00:00+00:00")).toBeVisible();
});

test("logs with an invalid token renders the reused 401 prompt", async ({
  page,
}) => {
  await installAuditStub(page, "ok");
  await page.goto("/admin/logs");
  await loadWithToken(page, "b024-stub-wrong-token");
  await expect(page.getByRole("alert")).toContainText(UNAUTHORIZED_401);
  await expect(page.getByText("draft_publish")).toHaveCount(0);
});

test("logs with an insufficient-scope token renders the reused 403 prompt", async ({
  page,
}) => {
  await installAuditStub(page, "forbidden");
  await page.goto("/admin/logs");
  await loadWithToken(page, VALID_TOKEN);
  await expect(page.getByRole("alert")).toContainText(FORBIDDEN_403);
  await expect(page.getByText("draft_publish")).toHaveCount(0);
});

test("logs renders the reused 404 prompt when the endpoint is missing", async ({
  page,
}) => {
  await installAuditStub(page, "missing");
  await page.goto("/admin/logs");
  await loadWithToken(page, VALID_TOKEN);
  await expect(page.getByRole("alert")).toContainText(NOT_FOUND_404);
});

test("logs renders the unconfigured-server prompt on 503", async ({
  page,
}) => {
  await installAuditStub(page, "unconfigured");
  await page.goto("/admin/logs");
  await loadWithToken(page, VALID_TOKEN);
  await expect(page.getByRole("alert")).toContainText(NOT_CONFIGURED_503);
});
