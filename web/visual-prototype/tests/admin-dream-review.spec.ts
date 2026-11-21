import { test, expect } from "@playwright/test";

/**
 * Dream review workflow, end to end (TJ-028.3, E0417).
 *
 * Runs ONLY when TIANJI_E2E_RUNTIME_BACKEND is set to the URL of a
 * runtime-capable test backend AND the vite dev server proxies /api
 * to that backend (vite.config.ts points at 127.0.0.1:8000 by default;
 * point it at the test backend for this run). The backend must be a
 * scratch build of this branch with the audited retrieval runtime
 * assembled and TIANJI_AI_* pointing at a LOCAL mock model server,
 * plus TIANJI_ADMIN_ROLE_TOKENS for the test roles
 * (editor-token:editor, reviewer-token:reviewer,
 * publisher-token:publisher): no real AMD/DuanYan call is made
 * anywhere in this spec. Without the env var the tests are skipped,
 * so public CI (no runtime, no mock) stays green; the role matrix,
 * content gate and restart persistence live in
 * test_tj0283_dream_review_http.py.
 *
 * Flow: research page generates the explained draft and saves it as
 * a review draft; the review page submits, approves with a reason,
 * and publishes it. A second test rolls the published draft back and
 * re-reviews it. A third test proves the public dream page never
 * shows AI results.
 *
 * Every test generates its own draft and scopes all assertions to
 * that draft's detail section: the test backend's SQLite store
 * persists across runs, so earlier drafts stay listed.
 */
const RUNTIME_BACKEND = process.env.TIANJI_E2E_RUNTIME_BACKEND || "";
test.skip(!RUNTIME_BACKEND, "needs a runtime-capable test backend");

// The three tests share one test backend and its SQLite store, so
// they must run serially: parallel workers would race each other's
// drafts and role-token input.
test.describe.configure({ mode: "serial" });

const READ_TOKEN = "test-admin-token";
const EDITOR = "editor-token";
const REVIEWER = "reviewer-token";
const PUBLISHER = "publisher-token";

async function generateAndSaveDraft(page) {
  await page.goto("/admin/dream-research");
  await page.getByLabel("管理端访问令牌").fill(READ_TOKEN);
  await page.getByLabel("梦境叙述").fill("我梦见自己死了");
  await page.getByRole("button", { name: "AI 解释（研究草稿）" }).click();
  const draft = page.locator("section", { hasText: "AI 解释 · 研究草稿" }).last();
  await expect(draft.getByText("已生成研究草稿")).toBeVisible();
  await page.getByLabel("角色令牌").fill(EDITOR);
  await page.getByRole("button", { name: "保存为审核草稿" }).click();
  await expect(page.getByText("已保存为审核草稿：")).toBeVisible();
  const text = (await page.getByText("已保存为审核草稿：").textContent()) || "";
  const match = text.match(/已保存为审核草稿：(D-\d+)/);
  return match ? match[1] : "";
}

async function openDraftDetail(page, draftId) {
  await page.goto("/admin/dream-review");
  await page.getByLabel("角色令牌").fill(EDITOR);
  await page.getByRole("button", { name: "加载审核草稿" }).click();
  await expect(page.getByText(draftId).first()).toBeVisible();
  await page
    .locator("article", { hasText: draftId })
    .getByRole("button", { name: "查看与审核" })
    .click();
  const detail = page.locator("section[aria-label='审核草稿详情']");
  await expect(detail.getByText(draftId)).toBeVisible();
  return detail;
}

test("review flow: submit, approve with reason, publish", async ({ page }) => {
  const draftId = await generateAndSaveDraft(page);
  expect(draftId).toMatch(/^D-\d+$/);
  const detail = await openDraftDetail(page, draftId);

  // Detail shows the dream, the verbatim quote and the citation.
  await expect(detail.getByText("梦境叙述：我梦见自己死了")).toBeVisible();
  await expect(detail.locator("blockquote", { hasText: "见人死自死皆吉" }).first()).toBeVisible();
  await expect(detail.getByText("周公解梦", { exact: false }).first()).toBeVisible();

  // An unreviewed draft offers only submit: no publish button yet.
  await expect(detail.getByRole("button", { name: "发布" })).toHaveCount(0);
  await detail.getByRole("button", { name: "提交审核" }).click();
  await expect(detail.getByText("状态 已提交")).toBeVisible();

  // An editor may not approve: the server answers 403.
  await detail.getByLabel("审核原因").fill("编辑尝试批准。");
  await detail.getByRole("button", { name: "批准" }).click();
  await expect(page.getByRole("alert")).toBeVisible();

  // A reviewer approves with a reason; the trail records it.
  await page.getByLabel("角色令牌").fill(REVIEWER);
  await detail.getByLabel("审核原因").fill("证据链完整，通过。");
  await detail.getByRole("button", { name: "批准" }).click();
  await expect(detail.getByText("状态 已批准")).toBeVisible();
  await expect(detail.getByText("原因：证据链完整，通过。")).toBeVisible();

  // A reviewer may not publish: the server answers 403.
  await detail.getByRole("button", { name: "发布" }).click();
  await expect(page.getByRole("alert")).toBeVisible();

  // A publisher publishes it.
  await page.getByLabel("角色令牌").fill(PUBLISHER);
  await detail.getByRole("button", { name: "发布" }).click();
  await expect(detail.getByText("状态 已发布")).toBeVisible();
});

test("rollback after publish forces a fresh review", async ({ page }) => {
  const draftId = await generateAndSaveDraft(page);
  expect(draftId).toMatch(/^D-\d+$/);
  const detail = await openDraftDetail(page, draftId);

  await detail.getByRole("button", { name: "提交审核" }).click();
  await expect(detail.getByText("状态 已提交")).toBeVisible();
  await page.getByLabel("角色令牌").fill(REVIEWER);
  await detail.getByLabel("审核原因").fill("证据链完整，通过。");
  await detail.getByRole("button", { name: "批准" }).click();
  await expect(detail.getByText("状态 已批准")).toBeVisible();
  await page.getByLabel("角色令牌").fill(PUBLISHER);
  await detail.getByRole("button", { name: "发布" }).click();
  await expect(detail.getByText("状态 已发布")).toBeVisible();

  await detail.getByLabel("回滚版本").selectOption({ index: 1 });
  await detail.getByRole("button", { name: "回滚" }).click();
  await expect(page.getByText("已回滚到版本")).toBeVisible();
  await expect(detail.getByText("状态 草稿")).toBeVisible();

  // The rolled-back draft must pass review again: only submit shows.
  await expect(detail.getByRole("button", { name: "发布" })).toHaveCount(0);
  await detail.getByRole("button", { name: "提交审核" }).click();
  // Wait for the submit to complete first: its handler clears the
  // reason field on success, so filling before it lands would be
  // wiped and the approve would stop client-side with no request.
  await expect(detail.getByText("状态 已提交")).toBeVisible();
  await page.getByLabel("角色令牌").fill(REVIEWER);
  await detail.getByLabel("审核原因").fill("回滚后重新审核，通过。");
  await detail.getByRole("button", { name: "批准" }).click();
  await expect(detail.getByText("状态 已批准")).toBeVisible();
  await expect(detail.getByText("原因：回滚后重新审核，通过。")).toBeVisible();
});

test("a refusal cannot be saved and the public page shows no AI", async ({ page }) => {
  await page.goto("/admin/dream-research");
  await page.getByLabel("管理端访问令牌").fill(READ_TOKEN);
  await page.getByLabel("梦境叙述").fill("我梦见在开会讨论工作");
  await page.getByRole("button", { name: "AI 解释（研究草稿）" }).click();
  await expect(page.getByText("无已审核解读，已弃判").first()).toBeVisible();
  await expect(page.getByRole("button", { name: "保存为审核草稿" })).toHaveCount(0);

  await page.goto("/dream-culture");
  await expect(page.getByText("AI 解释")).toHaveCount(0);
  await expect(page.getByText("研究草稿")).toHaveCount(0);
});
