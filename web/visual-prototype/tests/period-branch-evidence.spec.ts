import { test, expect } from "@playwright/test";

test("real daily -> weekly -> monthly calculation shows audited branch dates and source", async ({ page }) => {
  await page.goto("/daily-structure");
  await page.getByLabel("出生日期").fill("2000-01-07");
  await page.getByLabel("出生时间").fill("12:00");
  await page.getByLabel("查看日期").fill("2026-10-04");
  await page.getByRole("button", { name: "查看这一天的结构" }).click();
  await expect(page.locator(".daily-result")).toBeVisible();
  await expect(page.getByRole("region", { name: "日地支与原局关系" })).toContainText("已核四组关系");
  await expect(page.locator(".daily-branch-structure")).toContainText("不");
  const daily = page.locator(".daily-branch-hits details");
  if (await daily.count()) {
    await daily.first().locator("summary").click();
    await expect(daily.first().locator("blockquote p").first()).not.toBeEmpty();
    await expect(daily.first()).toContainText("证据等级");
  }

  await page.goto("/weekly-structure");
  await page.getByLabel("本周参考日期").fill("2026-10-04");
  await page.getByRole("button", { name: "查看本周结构" }).click();
  await expect(page.locator(".period-result")).toBeVisible();
  await expect(page.getByRole("region", { name: "周期地支关系" })).toContainText("六合");
  await expect(page.getByRole("region", { name: "周期地支关系" })).toContainText("六害");
  await expect(page.getByRole("region", { name: "周期地支关系" })).toContainText("六冲");
  const weekly = page.locator(".period-branch-relation details");
  if (await weekly.count()) {
    await weekly.first().locator("summary").click();
    await expect(weekly.first().locator("blockquote p").first()).not.toBeEmpty();
  }

  await page.goto("/monthly-structure");
  await page.getByLabel("查看月份").fill("2026-10");
  await page.getByRole("button", { name: "查看本月结构" }).click();
  await expect(page.locator(".period-result")).toBeVisible();
  await expect(page.locator(".period-days article")).toHaveCount(31);
  await expect(page.locator(".period-branch-evidence")).toContainText("六合");
  await expect(page.locator(".period-branch-evidence")).toContainText("吉凶");
});
