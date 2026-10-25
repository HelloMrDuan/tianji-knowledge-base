/**
 * B020 TJ-026.4 batch 2: draft approval flow (frontend).
 *
 * Controlled synthetic HTTP contracts (page.route stubs with an
 * in-spec draft store), explicitly labeled: no real backend is
 * required, so this spec runs in public CI. The REAL state machine,
 * role matrix, status codes, audit entries, and no-leakage behavior
 * of the backend are additionally verified by
 * tests/test_b020_drafts_http.py (offline acceptance, real server
 * code); this spec verifies the FRONTEND wires the full flow
 * (create -> submit -> approve -> publish), renders the reused
 * TJ-026.3 error branching for denied/illegal attempts, and shows
 * draft detail in the B020 Drawer — instead of inventing a second
 * error copy or demo data.
 *
 * The drafts page never persists a token (component state only);
 * the stub tokens below are synthetic and match nothing server-side.
 */
import { test, expect } from "@playwright/test";
import type { Page } from "@playwright/test";

const FORBIDDEN_403 = "令牌权限不足，无法访问该受控数据（scope 不足）。";

type StubDraft = {
  id: string;
  title: string;
  body: string;
  author_role: string;
  status: "draft" | "submitted" | "approved" | "rejected" | "published";
  created_at: string;
  updated_at: string;
  transitions: { action: string; role: string; at: string }[];
  // B022: the draft contract now carries version snapshots (batch 3).
  // The stub models them so the Drawer versions section renders.
  versions: {
    version: number;
    title: string;
    body: string;
    action: string;
    role: string;
    at: string;
  }[];
};

type StubFailure = { action: string; status: number; message: string };

async function installDraftStub(page: Page, fail?: StubFailure) {
  const store: Record<string, StubDraft> = {};
  let seq = 0;
  await page.route("**/api/v1/admin/drafts**", async (route) => {
    const req = route.request();
    const url = new URL(req.url());
    const parts = url.pathname.split("/").filter(Boolean);
    // parts: api, v1, admin, drafts, [id, [action]]
    const method = req.method();
    const post = () => {
      try {
        return JSON.parse(req.postData() ?? "{}") as Record<string, unknown>;
      } catch {
        return {};
      }
    };
    const note = {
      api_version: "v1",
      storage: "process_memory",
      storage_note: "stub storage note",
    };
    if (parts.length === 4 && method === "GET") {
      return route.fulfill({
        status: 200,
        json: { ...note, drafts: Object.values(store) },
      });
    }
    if (parts.length === 4 && method === "POST") {
      const body = post();
      seq += 1;
      const id = `D-${seq}`;
      const now = "2026-10-25T00:00:00+00:00";
      const draft: StubDraft = {
        id,
        title: String(body.title ?? ""),
        body: String(body.body ?? ""),
        author_role: "editor",
        status: "draft",
        created_at: now,
        updated_at: now,
        transitions: [{ action: "create", role: "editor", at: now }],
        versions: [
          {
            version: 1,
            title: String(body.title ?? ""),
            body: String(body.body ?? ""),
            action: "create",
            role: "editor",
            at: now,
          },
        ],
      };
      store[id] = draft;
      return route.fulfill({ status: 200, json: { ...note, draft } });
    }
    if (parts.length === 6 && method === "POST") {
      const draft = store[parts[4]];
      const action = parts[5];
      if (!draft) {
        return route.fulfill({
          status: 404,
          json: { detail: { code: "draft_not_found", message: "No draft" } },
        });
      }
      if (fail && fail.action === action) {
        return route.fulfill({
          status: fail.status,
          json: {
            detail: { code: "invalid_draft_transition", message: fail.message },
          },
        });
      }
      const next: Record<string, Record<string, string>> = {
        draft: { submit: "submitted" },
        submitted: { approve: "approved", reject: "rejected" },
        approved: { publish: "published" },
      };
      const target = next[draft.status]?.[action];
      if (!target) {
        return route.fulfill({
          status: 422,
          json: {
            detail: {
              code: "invalid_draft_transition",
              message: `cannot '${action}' a draft in status '${draft.status}'`,
            },
          },
        });
      }
      draft.status = target as StubDraft["status"];
      draft.transitions.push({
        action,
        role: "reviewer",
        at: "2026-10-25T00:01:00+00:00",
      });
      // B022: every transition appends a version snapshot, mirroring
      // the real batch-3 semantics (the B020 spec itself does not
      // assert versions; this keeps the stub contract faithful).
      draft.versions.push({
        version: draft.versions.length + 1,
        title: draft.title,
        body: draft.body,
        action,
        role: "reviewer",
        at: "2026-10-25T00:01:00+00:00",
      });
      return route.fulfill({ status: 200, json: { ...note, draft } });
    }
    return route.fulfill({ status: 404, json: {} });
  });
}

async function createDraft(page: Page, title: string, body: string) {
  await page.getByLabel("草稿标题").fill(title);
  await page.getByLabel("草稿正文").fill(body);
  await page.getByRole("button", { name: "创建草稿" }).click();
  const item = page.locator(".admin-draft-item", { hasText: title });
  await expect(item).toContainText("草稿");
  return item;
}

test("draft full flow create -> submit -> approve -> publish in drawer detail", async ({
  page,
}) => {
  await installDraftStub(page);
  await page.goto("/admin/drafts");
  await page.getByLabel("角色令牌").fill("b020-stub-editor-token");
  const item = await createDraft(page, "B020 流程草稿", "流程正文内容");
  await item.getByRole("button", { name: "提交", exact: true }).click();
  await expect(item).toContainText("已提交");
  await item.getByRole("button", { name: "批准", exact: true }).click();
  await expect(item).toContainText("已批准");
  await item.getByRole("button", { name: "发布", exact: true }).click();
  await expect(item).toContainText("已发布");
  // Detail reuses the Drawer: body + approval history visible.
  await item.getByRole("button", { name: "详情", exact: true }).click();
  const drawer = page.getByRole("dialog");
  await expect(drawer).toContainText("流程正文内容");
  await expect(drawer).toContainText("submit");
  await expect(drawer).toContainText("approve");
  await expect(drawer).toContainText("publish");
  await drawer.getByLabel("关闭详情").click();
  await expect(page.getByRole("dialog")).toHaveCount(0);
  // Token is component state only: nothing token-like persisted.
  const keys = await page.evaluate(() => Object.keys(localStorage));
  expect(keys.filter((k) => k.toLowerCase().includes("token"))).toEqual([]);
});

test("failed action renders the server 422 message, not a generic fallback", async ({
  page,
}) => {
  // The stub injects a server-side rejection of the approve action
  // to verify the page surfaces 422 detail messages through the
  // reused error branching. Real illegal-transition enforcement is
  // covered by test_b020_drafts_http.py, not by this stub.
  await installDraftStub(page, {
    action: "approve",
    status: 422,
    message: "cannot 'approve' a draft in status 'draft'",
  });
  await page.goto("/admin/drafts");
  await page.getByLabel("角色令牌").fill("b020-stub-editor-token");
  const item = await createDraft(page, "B020 失败动作草稿", "失败动作正文");
  await item.getByRole("button", { name: "提交", exact: true }).click();
  await expect(item).toContainText("已提交");
  await item.getByRole("button", { name: "批准", exact: true }).click();
  await expect(page.getByRole("alert").first()).toContainText(
    "cannot 'approve'",
  );
  // The failed attempt leaves the draft state untouched.
  await expect(item).toContainText("已提交");
});

test("user-role create renders the reused 403 prompt", async ({ page }) => {
  await page.route("**/api/v1/admin/drafts", (route) =>
    route.fulfill({
      status: 403,
      json: {
        detail: {
          code: "admin_forbidden",
          message: "Admin role does not allow draft",
        },
      },
    }),
  );
  await page.goto("/admin/drafts");
  await page.getByLabel("角色令牌").fill("b020-stub-user-token");
  await page.getByLabel("草稿标题").fill("B020 越权草稿");
  await page.getByLabel("草稿正文").fill("越权正文");
  await page.getByRole("button", { name: "创建草稿" }).click();
  await expect(page.getByRole("alert").first()).toContainText(FORBIDDEN_403);
});
