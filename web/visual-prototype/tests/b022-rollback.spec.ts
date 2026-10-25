/**
 * B022 TJ-026.4 batch 3: draft rollback (frontend).
 *
 * Controlled synthetic HTTP contracts (page.route stubs with an
 * in-spec draft store), explicitly labeled: no real backend is
 * required, so this spec runs in public CI. The REAL version
 * snapshots, rollback state machine, role matrix, status codes,
 * compensating audit records, and no-leakage behavior of the backend
 * are additionally verified by tests/test_b022_rollback_http.py
 * (offline acceptance, real server code); this spec verifies the
 * FRONTEND wires rollback (detail Drawer version list -> rollback
 * button -> reverted content + draft status + rollback transition
 * visible), renders the reused TJ-026.3 error branching for a
 * non-publisher rollback 403, and hides rollback for rejected drafts
 * — instead of inventing a second error copy or demo data.
 *
 * The drafts page never persists a token (component state only);
 * the stub tokens below are synthetic and match nothing server-side.
 * The stub's role comes from the token string itself
 * (b022-stub-<role>-token), so the 403 test only changes the input.
 */
import { test, expect } from "@playwright/test";
import type { Page } from "@playwright/test";

const FORBIDDEN_403 = "令牌权限不足，无法访问该受控数据（scope 不足）。";

type StubVersion = {
  version: number;
  title: string;
  body: string;
  action: string;
  role: string;
  at: string;
};

type StubDraft = {
  id: string;
  title: string;
  body: string;
  author_role: string;
  status: "draft" | "submitted" | "approved" | "rejected" | "published";
  created_at: string;
  updated_at: string;
  transitions: { action: string; role: string; at: string; version?: number }[];
  versions: StubVersion[];
};

function roleOf(token: string): string {
  if (token.includes("publisher")) return "publisher";
  if (token.includes("editor")) return "editor";
  if (token.includes("reviewer")) return "reviewer";
  if (token.includes("user")) return "user";
  return "unknown";
}

async function installRollbackStub(page: Page) {
  const store: Record<string, StubDraft> = {};
  let seq = 0;
  const now = "2026-10-25T00:00:00+00:00";
  const note = {
    api_version: "v1",
    storage: "process_memory",
    storage_note: "stub storage note",
  };
  const snap = (draft: StubDraft, action: string, role: string) => {
    draft.versions.push({
      version: draft.versions.length + 1,
      title: draft.title,
      body: draft.body,
      action,
      role,
      at: now,
    });
  };
  await page.route("**/api/v1/admin/drafts**", async (route) => {
    const req = route.request();
    const url = new URL(req.url());
    const parts = url.pathname.split("/").filter(Boolean);
    // parts: api, v1, admin, drafts, [id, [action]]
    const method = req.method();
    const token = (req.headers()["authorization"] ?? "").replace(
      "Bearer ",
      "",
    );
    const role = roleOf(token);
    const post = () => {
      try {
        return JSON.parse(req.postData() ?? "{}") as Record<string, unknown>;
      } catch {
        return {};
      }
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
      const draft: StubDraft = {
        id,
        title: String(body.title ?? ""),
        body: String(body.body ?? ""),
        author_role: "editor",
        status: "draft",
        created_at: now,
        updated_at: now,
        transitions: [{ action: "create", role: "editor", at: now }],
        versions: [],
      };
      snap(draft, "create", "editor");
      store[id] = draft;
      return route.fulfill({ status: 200, json: { ...note, draft } });
    }
    if (parts.length === 5 && method === "PATCH") {
      const draft = store[parts[4]];
      if (!draft) {
        return route.fulfill({
          status: 404,
          json: { detail: { code: "draft_not_found", message: "No draft" } },
        });
      }
      if (draft.status !== "draft") {
        return route.fulfill({
          status: 422,
          json: {
            detail: {
              code: "invalid_draft_transition",
              message: `cannot edit a draft in status '${draft.status}'`,
            },
          },
        });
      }
      const body = post();
      if (typeof body.title === "string") draft.title = body.title;
      if (typeof body.body === "string") draft.body = body.body;
      snap(draft, "edit", role);
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
      if (action === "rollback") {
        // Publisher-only, mirroring the batch-1 'rollback' operation.
        if (role !== "publisher") {
          return route.fulfill({
            status: 403,
            json: {
              detail: {
                code: "admin_forbidden",
                message: "Admin role does not allow rollback",
              },
            },
          });
        }
        if (draft.status === "rejected") {
          return route.fulfill({
            status: 422,
            json: {
              detail: {
                code: "invalid_draft_transition",
                message: "cannot rollback a rejected draft",
              },
            },
          });
        }
        const target = draft.versions.find(
          (v) => v.version === Number(post().version),
        );
        if (!target) {
          return route.fulfill({
            status: 422,
            json: {
              detail: {
                code: "invalid_draft_transition",
                message: "unknown version",
              },
            },
          });
        }
        draft.title = target.title;
        draft.body = target.body;
        draft.status = "draft";
        draft.transitions.push({
          action: "rollback",
          role,
          at: now,
          version: target.version,
        });
        snap(draft, "rollback", role);
        return route.fulfill({ status: 200, json: { ...note, draft } });
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
      draft.transitions.push({ action, role, at: now });
      snap(draft, action, role);
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

async function publishDraft(page: Page, title: string, body: string) {
  const item = await createDraft(page, title, body);
  await item.getByRole("button", { name: "提交", exact: true }).click();
  await expect(item).toContainText("已提交");
  await item.getByRole("button", { name: "批准", exact: true }).click();
  await expect(item).toContainText("已批准");
  await item.getByRole("button", { name: "发布", exact: true }).click();
  await expect(item).toContainText("已发布");
  return item;
}

test("rollback published draft to v1 restores content and draft status", async ({
  page,
}) => {
  await installRollbackStub(page);
  await page.goto("/admin/drafts");
  await page.getByLabel("角色令牌").fill("b022-stub-publisher-token");
  // v1: created content. Edit to v2, then publish.
  const item = await createDraft(page, "B022 v1 标题", "B022 v1 正文");
  await item.getByRole("button", { name: "编辑" }).click();
  await page.getByLabel("编辑标题").fill("B022 v2 标题");
  await page.getByLabel("编辑正文").fill("B022 v2 正文");
  await page.getByRole("button", { name: "保存", exact: true }).click();
  const edited = page.locator(".admin-draft-item", {
    hasText: "B022 v2 标题",
  });
  await expect(edited).toContainText("草稿");
  await edited.getByRole("button", { name: "提交", exact: true }).click();
  await expect(edited).toContainText("已提交");
  await edited.getByRole("button", { name: "批准", exact: true }).click();
  await expect(edited).toContainText("已批准");
  await edited.getByRole("button", { name: "发布", exact: true }).click();
  await expect(edited).toContainText("已发布");
  // Detail Drawer: version history lists v1..publish; roll back to v1.
  await edited.getByRole("button", { name: "详情", exact: true }).click();
  const drawer = page.getByRole("dialog");
  await expect(drawer).toContainText("版本历史");
  await expect(drawer).toContainText("B022 v2 标题");
  await drawer.getByLabel("回滚到版本 1").click();
  // Content equals the v1 snapshot; status is back to draft; the
  // rollback transition is visible in the approval history.
  await expect(drawer).toContainText("B022 v1 正文");
  await expect(drawer).toContainText("草稿");
  await expect(drawer).toContainText("rollback");
  await expect(drawer).toContainText("回滚到版本 1");
  // The list item follows the rollback too.
  const reverted = page.locator(".admin-draft-item", {
    hasText: "B022 v1 标题",
  });
  await expect(reverted).toContainText("草稿");
  await drawer.getByLabel("关闭详情").click();
  await expect(page.getByRole("dialog")).toHaveCount(0);
});

test("non-publisher rollback renders the reused 403 prompt", async ({
  page,
}) => {
  await installRollbackStub(page);
  await page.goto("/admin/drafts");
  await page.getByLabel("角色令牌").fill("b022-stub-publisher-token");
  const item = await publishDraft(page, "B022 越权回滚草稿", "越权回滚正文");
  await item.getByRole("button", { name: "详情", exact: true }).click();
  const drawer = page.getByRole("dialog");
  // Switch to an editor token: the stub gates rollback to publisher.
  await page.getByLabel("角色令牌").fill("b022-stub-editor-token");
  await drawer.getByLabel("回滚到版本 1").click();
  await expect(page.getByRole("alert").first()).toContainText(FORBIDDEN_403);
  // The failed rollback leaves the published draft untouched.
  await expect(drawer).toContainText("越权回滚正文");
  await expect(item).toContainText("已发布");
});

test("rejected draft shows versions but no rollback button", async ({
  page,
}) => {
  await installRollbackStub(page);
  await page.goto("/admin/drafts");
  await page.getByLabel("角色令牌").fill("b022-stub-publisher-token");
  const item = await createDraft(page, "B022 已驳回草稿", "已驳回正文");
  await item.getByRole("button", { name: "提交", exact: true }).click();
  await expect(item).toContainText("已提交");
  await item.getByRole("button", { name: "驳回", exact: true }).click();
  await expect(item).toContainText("已驳回");
  await item.getByRole("button", { name: "详情", exact: true }).click();
  const drawer = page.getByRole("dialog");
  await expect(drawer).toContainText("版本历史");
  await expect(
    drawer.getByRole("button", { name: "回滚到此版本" }),
  ).toHaveCount(0);
});
