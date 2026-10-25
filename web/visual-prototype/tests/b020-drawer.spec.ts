/**
 * B020 TJ-026.1 layout only: drawer component + ModulePage detail
 * migration (frontend).
 *
 * No backend is required: ModulePage renders design fixtures only,
 * so this spec runs in public CI. It verifies the #87 shell stays
 * faithful (left sidebar + table + detail action, as in the #87
 * rules-desktop reference screenshot: sidebar groups, search/filter,
 * table with a detail action per row) and that record detail now
 * opens in a right-docked drawer over the list instead of replacing
 * it with a full-page view. Screenshots are saved to test-results/
 * for human review against the #87 reference; assertions below are
 * structural (presence + geometry), never pixel equality with #87.
 */
import { test, expect } from "@playwright/test";
import type { Page } from "@playwright/test";

async function assertNoHorizontalOverflow(page: Page) {
  const overflow = await page.evaluate(() => {
    const doc = document.documentElement;
    return doc.scrollWidth - doc.clientWidth;
  });
  expect(overflow).toBeLessThanOrEqual(0);
}

async function openDrawer(page: Page) {
  await page.goto("/admin/evaluations");
  // #87 shell fidelity: sidebar + table + per-row detail action.
  await expect(page.locator(".admin-sidebar")).toBeVisible();
  await expect(page.locator(".module-table")).toBeVisible();
  const row = page.locator("tr", { hasText: "初爻动 · 样例" });
  await expect(row).toBeVisible();
  await row.getByRole("link", { name: "详情" }).click();
  const drawer = page.getByRole("dialog");
  await expect(drawer).toBeVisible();
  return drawer;
}

test("detail opens in a right-docked drawer over the list (desktop)", async ({
  page,
}) => {
  await page.setViewportSize({ width: 1280, height: 800 });
  const drawer = await openDrawer(page);
  // Same detail content as the old full-page view: tabs + fields.
  await expect(drawer).toContainText("初爻动 · 样例");
  await expect(drawer).toContainText("记录详情");
  await expect(drawer).toContainText("关联关系");
  await expect(drawer).toContainText("审核轨迹");
  // Right-docked geometry: drawer starts past the viewport middle
  // and never spans the full width on desktop. The width band is
  // 520px ± 1px, not an exact equality: Chromium reports sub-pixel
  // float noise for a 520px panel (observed 520.00006), so an exact
  // <= 520 flakes. The ±1px band still pins the designed width and
  // still fails a full-width or resized panel.
  const box = await drawer.boundingBox();
  expect(box).not.toBeNull();
  expect(box!.x).toBeGreaterThan(640);
  expect(box!.width).toBeGreaterThanOrEqual(519);
  expect(box!.width).toBeLessThanOrEqual(521);
  // The list underneath stays in the DOM (not replaced).
  await expect(page.locator(".module-table")).toBeVisible();
  await assertNoHorizontalOverflow(page);
  await page.screenshot({ path: "test-results/b020-drawer-desktop.png" });
});

test("drawer closes via button, backdrop, and Escape", async ({ page }) => {
  await page.setViewportSize({ width: 1280, height: 800 });
  const drawer = await openDrawer(page);
  await drawer.getByLabel("关闭详情").click();
  await expect(page.getByRole("dialog")).toHaveCount(0);
  await expect(page.locator(".module-table")).toBeVisible();

  await openDrawer(page);
  await page.locator(".admin-drawer-backdrop").click();
  await expect(page.getByRole("dialog")).toHaveCount(0);

  await openDrawer(page);
  await page.keyboard.press("Escape");
  await expect(page.getByRole("dialog")).toHaveCount(0);
  // Closing returns to the plain list URL (deep-link round-trip).
  expect(page.url()).toContain("/admin/evaluations");
  expect(page.url()).not.toContain("DEMO-");
});

test("drawer on mobile is viewport-bounded with no horizontal overflow", async ({
  page,
}) => {
  await page.setViewportSize({ width: 390, height: 844 });
  const drawer = await openDrawer(page);
  await expect(drawer).toContainText("初爻动 · 样例");
  const box = await drawer.boundingBox();
  expect(box).not.toBeNull();
  expect(box!.width).toBeLessThanOrEqual(390);
  await assertNoHorizontalOverflow(page);
  await page.screenshot({ path: "test-results/b020-drawer-mobile.png" });
});
