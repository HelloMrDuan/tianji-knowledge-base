/**
 * TJ-026.5 SQLite admin storage labels (frontend).
 *
 * Controlled synthetic HTTP contracts (page.route stubs with fixed
 * responses), explicitly labeled: no real backend is required, so
 * this spec runs in public CI. The REAL SQLite persistence behavior
 * (restart keeps drafts/audit, id sequence never repeats) is covered
 * by the backend's storage tests; this spec verifies the FRONTEND
 * reports the durable story instead of the old process-memory story:
 * drafts page badge + notice texts, logs page badge + panel text,
 * and the API-driven storage_note paragraph after a list refresh.
 * No old "进程内存 · 重启丢失" text may remain on either page.
 *
 * The stub tokens below are synthetic and match nothing server-side.
 */
import { test, expect } from "@playwright/test";

test("drafts page shows the SQLite durable-storage labels", async ({
  page,
}) => {
  await page.goto("/admin/drafts");
  await expect(
    page.getByText("SQLite 持久存储 · 重启不丢").first(),
  ).toBeVisible();
  await expect(
    page.getByText("草稿保存在 SQLite 单文件中，服务重启后不丢失", {
      exact: false,
    }).first(),
  ).toBeVisible();
  await expect(
    page.getByText("版本快照与草稿同存 SQLite 单文件", {
      exact: false,
    }).first(),
  ).toBeVisible();
  await expect(page.getByText("进程内存")).toHaveCount(0);
  await expect(page.getByText("重启丢失")).toHaveCount(0);
});

test("logs page shows the SQLite durable-storage labels", async ({
  page,
}) => {
  await page.goto("/admin/logs");
  await expect(
    page.getByRole("heading", { name: "审计轨迹" }).first(),
  ).toBeVisible();
  await expect(
    page.getByText("SQLite 持久存储 · 重启不丢").first(),
  ).toBeVisible();
  await expect(
    page.getByText("条目存入 SQLite 单文件", { exact: false }).first(),
  ).toBeVisible();
  await expect(page.getByText("进程内存")).toHaveCount(0);
  await expect(page.getByText("重启丢失")).toHaveCount(0);
});

test("drafts list refresh renders the API storage_note", async ({
  page,
}) => {
  await page.route("**/api/v1/admin/drafts", async (route) => {
    if (route.request().method() !== "GET") {
      return route.fulfill({ status: 404, json: { detail: "no stub" } });
    }
    return route.fulfill({
      status: 200,
      json: {
        api_version: "v1",
        drafts: [],
        storage: "sqlite",
        storage_note:
          "草稿保存在 SQLite 单文件中，服务重启后不丢失；备份为拷贝该文件。",
      },
    });
  });
  await page.goto("/admin/drafts");
  await page.getByLabel("角色令牌").fill("b0265-stub-token");
  await page.getByRole("button", { name: "刷新列表" }).click();
  await expect(
    page.getByText("草稿保存在 SQLite 单文件中，服务重启后不丢失", {
      exact: false,
    }).first(),
  ).toBeVisible();
});
