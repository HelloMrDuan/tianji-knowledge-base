import { test, expect } from "@playwright/test";

/**
 * Admin AI dream explanation, explained path (TJ-028.1 sub-slice, E0416).
 *
 * Runs ONLY when TIANJI_E2E_RUNTIME_BACKEND is set to the URL of a
 * runtime-capable test backend AND the vite dev server proxies /api
 * to that backend (vite.config.ts points at 127.0.0.1:8000 by default;
 * point it at the test backend for this run). The backend must be a
 * scratch build of this branch with the audited retrieval runtime
 * assembled (see the task report) and TIANJI_AI_* pointing at a LOCAL
 * mock model server: no real AMD/DuanYan call is made anywhere in
 * this spec. Without the env var the test is skipped, so public CI
 * (no runtime, no mock) stays green; the wired-flow and refusal
 * cases live in admin-dream-ai-explain.spec.ts.
 *
 * The mock model only repeats audited data: it builds its reply from
 * the adapter context's own candidates and evidence, so every
 * rendered string below is traceable to the audited retrieval.
 */
const RUNTIME_BACKEND = process.env.TIANJI_E2E_RUNTIME_BACKEND || "";
test.skip(!RUNTIME_BACKEND, "needs a runtime-capable test backend");

test("AI explain renders the explained research draft", async ({ page }) => {
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

  // The request really reached the runtime backend and succeeded:
  // without the assembled runtime the same endpoint fails closed
  // with 422, so a single 200 here is the explained path, not a
  // network error or a refusal.
  await expect.poll(() => statuses).toEqual([200]);
  await expect(page.getByRole("alert")).toHaveCount(0);

  const draft = page.locator("section", { hasText: "AI 解释 · 研究草稿" }).last();
  await expect(draft.getByRole("heading", { name: "AI 解释 · 研究草稿" })).toBeVisible();
  // Verdict label and research-mode markers. The markers live
  // inside the collapsed <details>, so open it first.
  await expect(draft.getByText("已生成研究草稿")).toBeVisible();
  await draft.getByText("解释边界及限制").click();
  await expect(draft.getByText("本草稿仅供人工审核")).toBeVisible();
  await expect(draft.getByText("公开 AI 仍处于关闭状态")).toBeVisible();
  // Draft text: the claim the mock built from audited data.
  await expect(draft.getByText("不作个人运势判断")).toBeVisible();
  // Verbatim quote, rendered as a blockquote.
  await expect(draft.locator("blockquote", { hasText: "见人死自死皆吉" })).toBeVisible();
  // Evidence source: classic title + locator + traceable-source
  // count, scoped to the citation line (the claim text also names
  // the classic, so a bare getByText would match twice).
  const citation = draft.locator("small", { hasText: "可追溯来源" });
  await expect(citation).toContainText("周公解梦");
  await expect(citation).toContainText("1 个可追溯来源");

  await page.screenshot({ path: "test-results/admin-dream-ai-explained.png", fullPage: true });
});
