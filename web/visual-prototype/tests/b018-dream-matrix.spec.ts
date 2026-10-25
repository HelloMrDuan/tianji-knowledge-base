/**
 * B018 TJ-019.1: high-frequency dream demand matrix view.
 *
 * No backend is required: the matrix is a static frontend section on the
 * dream-culture page (visible without submitting a query). This spec
 * verifies the RENDERING contract — seven categories in WBS order, each
 * marked unreviewed with an explicit no-interpretation declaration, and
 * no fortune/medical verdict text inside the matrix section.
 *
 * The REAL no-interpretation discipline of the backend (unreviewed
 * topics carry no original-source text and no omen claim) is covered by
 * tests/test_public_dream_culture_api.py and the B004 semantics tests;
 * this spec covers only the new matrix VIEW.
 */
import { test, expect } from "@playwright/test";

const MATRIX_ORDER = ["被追", "故人", "考试", "结婚", "怀孕", "工作", "死亡"];

test("dream matrix lists seven categories in WBS order, each unreviewed", async ({
  page,
}) => {
  await page.goto("/dream-culture");
  const matrix = page.locator(".dream-culture-matrix");
  await expect(matrix).toBeVisible();
  await expect(matrix).toContainText("高频梦境需求矩阵");
  const items = matrix.locator(".dream-culture-matrix-item");
  await expect(items).toHaveCount(7);
  for (let index = 0; index < MATRIX_ORDER.length; index += 1) {
    const item = items.nth(index);
    await expect(item).toContainText(MATRIX_ORDER[index]);
    await expect(item).toContainText("未审核");
    await expect(item).toContainText("无精确动作原典，不产解释");
  }
});

test("dream matrix carries no verdict text and does not overflow", async ({
  page,
}) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto("/dream-culture");
  const matrix = page.locator(".dream-culture-matrix");
  await expect(matrix).toBeVisible();
  // Scoped to the matrix section only: the rest of the page legitimately
  // discusses historical fortune wording as cultural record.
  await expect(matrix).not.toContainText("吉");
  await expect(matrix).not.toContainText("凶");
  await expect(matrix).not.toContainText("预示");
  await expect(matrix).not.toContainText("会发生");
  await expect(matrix).not.toContainText("诊断");
  await expect(matrix).toContainText("矩阵仅做分类排队，不产解释");
  await expect
    .poll(() =>
      page.evaluate(
        () =>
          document.documentElement.scrollWidth <=
          document.documentElement.clientWidth,
      ),
    )
    .toBe(true);
  await page.setViewportSize({ width: 1280, height: 800 });
  await expect
    .poll(() =>
      page.evaluate(
        () =>
          document.documentElement.scrollWidth <=
          document.documentElement.clientWidth,
      ),
    )
    .toBe(true);
});
