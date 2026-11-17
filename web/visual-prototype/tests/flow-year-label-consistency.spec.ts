import { test, expect } from "@playwright/test";

test("year default follows current browser year and no false Ganzhi appears before real response", async ({ page }) => {
  await page.clock.install({ time: new Date("2028-07-01T06:00:00Z") });
  await page.goto("/yearly-structure");
  await expect(page.getByLabel("目标年份")).toHaveValue("2028");
  await expect(page.locator(".yearly-seal strong")).toHaveText("待计算");
  await page.getByRole("button", { name: "填入示例" }).click();
  await page.getByLabel("目标年份").fill("2027");
  await expect(page.locator(".yearly-seal strong")).toHaveText("待计算");
  await page.getByRole("button", { name: /查看 2027 流年结构/ }).click();
  await expect(page.locator(".yearly-result-head")).toContainText("2027 丁未");
  await expect(page.locator(".yearly-seal strong")).toHaveText("丁未");
  // Line B: the production backend returns the short canonical rule IDs
  // "R04" (flow stem ten-god) and "R05" (annual branch relations); the
  // public scenario_engine uses the long "bazi.scenario.*" IDs. The rule
  // list is scoped to the first .yearly-rule section (the branch section
  // .yearly-branch-section also carries .yearly-rule and its hit articles
  // have their own strongs, e.g. "未 ↔ 丑").
  await expect(page.locator(".yearly-rule:not(.yearly-branch-section) article strong")).toHaveText([
    "R04",
    "R05",
  ]);
  await expect(page.locator(".yearly-rule:not(.yearly-branch-section) article p").first()).toContainText("流年天干：丁");
  await expect(page.locator(".yearly-rule:not(.yearly-branch-section) article p").last()).toContainText("流年地支：未");
  // The R05 paragraph must be the branch summary, not the stem paragraph:
  // only the branch summary carries "已核原局四柱地支".
  await expect(page.locator(".yearly-rule:not(.yearly-branch-section) article p").last()).toContainText("已核原局四柱地支");
  await expect(page.locator(".yearly-branch-hit")).toHaveCount(3);
  const cited = page.locator(".yearly-branch-hit .yearly-branch-sources");
  await expect(cited).toHaveCount(3);
  await cited.first().locator("summary").click();
  await expect(cited.first().locator("blockquote").first()).not.toBeEmpty();
  await expect(cited.first()).toContainText("证据等级");
  await expect(page.locator(".yearly-rule:not(.yearly-branch-section) article p").first()).not.toContainText("—");

  await page.getByLabel("目标年份").fill("2028");
  await expect(page.locator(".yearly-result")).toHaveCount(0);
  await expect(page.locator(".yearly-seal strong")).toHaveText("待计算");
  // The last completed year stays in local storage until another calculation succeeds.
  expect(await page.evaluate(() => localStorage.getItem("tianji.scenario.target-year.v1"))).toBe("2027");
});

test("all four scenario pages use the same current-year fallback without changing saved preferences", async ({ page }) => {
  await page.clock.install({ time: new Date("2029-02-12T12:00:00Z") });
  for (const item of [
    { path: "/life-overview", label: "观察年份" },
    { path: "/yearly-structure", label: "目标年份" },
    { path: "/romance-structure", label: "观察年份" },
    { path: "/career-wealth-structure", label: "观察年份" },
  ]) {
    await page.goto(item.path);
    await expect(page.getByLabel(item.label)).toHaveValue("2029");
  }
  expect(await page.evaluate(() => localStorage.getItem("tianji.scenario.target-year.v1"))).toBeNull();
});
