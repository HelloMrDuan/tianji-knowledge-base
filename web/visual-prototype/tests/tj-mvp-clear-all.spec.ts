import { test, expect, type Page } from "@playwright/test";

/** TJ-029.2 P1 (E0407): 统一清除本机资料。
 * 全部 5 条均为 [local-only]：只操作 localStorage 与页面 UI，不调用后端，
 * 因此 SSH 冷却期间也可运行。
 *
 * 关键约束（Line A 核查 + 本实现）：
 * - 主题/收藏/音乐 3 键在每次挂载时由 effect 写回默认值，因此“5 键全部
 *   缺失”只能在点击清除后、重载前断言；重载后应断言值回到默认而非键缺失。
 * - 出生资料与目标年份键没有任何挂载写回，重载后必须仍缺失才是“无恢复”。
 */

const KEYS = [
  "tianji.profile.birth.v1",
  "tianji.scenario.target-year.v1",
  "tianji.product.favorite",
  "tianji.prototype.music",
  "tianji.theme",
] as const;

const SEED_PROFILE = {
  calendarType: "solar",
  year: 2000,
  month: 1,
  day: 7,
  isLeapMonth: false,
  time: "12:00",
  timeUnknown: false,
  region: "中国大陆",
};

async function seedAllKeys(page: Page) {
  await page.evaluate(() => {
    localStorage.setItem(
      "tianji.profile.birth.v1",
      JSON.stringify({
        calendarType: "solar",
        year: 2000,
        month: 1,
        day: 7,
        isLeapMonth: false,
        time: "12:00",
        timeUnknown: false,
        region: "中国大陆",
      }),
    );
    localStorage.setItem("tianji.scenario.target-year.v1", "2030");
    localStorage.setItem("tianji.product.favorite", "true");
    localStorage.setItem(
      "tianji.prototype.music",
      JSON.stringify({ volume: 0.9, optedIn: true }),
    );
    localStorage.setItem("tianji.theme", "paper");
  });
}

async function seedBirthProfile(page: Page) {
  await page.evaluate((profile) => {
    localStorage.setItem("tianji.profile.birth.v1", JSON.stringify(profile));
  }, SEED_PROFILE);
}

async function readKeys(page: Page): Promise<Record<string, string | null>> {
  return page.evaluate((keys: readonly string[]) => {
    const out: Record<string, string | null> = {};
    for (const k of keys) out[k] = localStorage.getItem(k);
    return out;
  }, KEYS);
}

/** 八字页年份下拉（.birth-date-row 第一个 select）。 */
function baziYearSelect(page: Page) {
  return page.locator(".birth-date-row select").first();
}

test("[local-only] TJ-029.2 clear-all removes all 5 keys and confirms", async ({ page }) => {
  await page.goto("/bazi-profile");
  await seedAllKeys(page);
  await page.reload();

  // 种子已生效：表单带入 2000 年，主题为宣纸
  await expect(baziYearSelect(page)).toHaveValue("2000");
  await expect
    .poll(() => page.evaluate(() => document.documentElement.getAttribute("data-theme")))
    .toBe("paper");
  const before = await readKeys(page);
  expect(before["tianji.profile.birth.v1"]).toContain("2000");
  expect(before["tianji.scenario.target-year.v1"]).toBe("2030");
  expect(before["tianji.product.favorite"]).toBe("true");
  expect(before["tianji.prototype.music"]).toContain("true");
  expect(before["tianji.theme"]).toBe("paper");

  // 两步确认：先出现确认面板，列出将清除的类别
  await page.getByRole("button", { name: "清除全部本机资料", exact: true }).click();
  await expect(page.locator(".bazi-clear-all-confirm")).toContainText(
    "将清除本机保存的：出生资料档案、目标年份、收藏偏好、音乐偏好、主题偏好。",
  );

  await page
    .locator(".bazi-clear-all-confirm")
    .getByRole("button", { name: "确认清除", exact: true })
    .click();

  // 立即断言：5 键全部缺失（重载前），回执列出已清除类别，表单已空
  const after = await readKeys(page);
  for (const k of KEYS) expect(after[k], `${k} should be removed`).toBeNull();
  await expect(page.getByRole("status")).toContainText(
    "已清除本机全部资料：出生资料档案、目标年份、收藏偏好、音乐偏好、主题偏好。",
  );
  await expect(baziYearSelect(page)).toHaveValue("");
  await expect
    .poll(() => page.evaluate(() => document.documentElement.getAttribute("data-theme")))
    .toBe("night");
});

test("[local-only] TJ-029.2 compat page clear removes the shared birth profile", async ({ page }) => {
  await page.goto("/compatibility-structure");
  await seedBirthProfile(page);
  await page.reload();

  // A 方已带入档案日期
  const aDate = page.locator('input[type="date"]').first();
  await expect(aDate).toHaveValue("2000-01-07");

  await page.getByRole("button", { name: "清除本机资料", exact: true }).click();

  const after = await readKeys(page);
  expect(after["tianji.profile.birth.v1"]).toBeNull();
  await expect(aDate).toHaveValue("");
  await expect(page.getByRole("status")).toContainText(
    "已清除本机保存的出生资料。对方资料仅用于本次合盘计算，本就不保存到本机。",
  );
});

test("[local-only] TJ-029.2 cross-tab sync: clear in one tab empties the other", async ({ page, context }) => {
  const page2 = await context.newPage();
  await page.goto("/bazi-profile");
  await seedBirthProfile(page);
  await page.reload();
  await expect(baziYearSelect(page)).toHaveValue("2000");

  // 第二页同一来源：应读到共享档案
  await page2.goto("/bazi-profile");
  await expect(baziYearSelect(page2)).toHaveValue("2000");

  // 第一页清除出生资料；第二页应通过 storage 事件重载并清空
  await page.getByRole("button", { name: "清除本机资料", exact: true }).click();
  await expect(baziYearSelect(page2)).toHaveValue("", { timeout: 10000 });
  const page2Keys = await readKeys(page2);
  expect(page2Keys["tianji.profile.birth.v1"]).toBeNull();
  await page2.close();
});

test("[local-only] TJ-029.2 no auto-restore after clear-all and reload", async ({ page }) => {
  await page.goto("/bazi-profile");
  await seedAllKeys(page);
  await page.reload();
  await expect(baziYearSelect(page)).toHaveValue("2000");

  await page.getByRole("button", { name: "清除全部本机资料", exact: true }).click();
  await page
    .locator(".bazi-clear-all-confirm")
    .getByRole("button", { name: "确认清除", exact: true })
    .click();
  const cleared = await readKeys(page);
  for (const k of KEYS) expect(cleared[k], `${k} should be removed`).toBeNull();

  await page.reload();

  // 出生资料与目标年份没有任何挂载写回：必须仍缺失，表单保持空白
  const afterReload = await readKeys(page);
  expect(afterReload["tianji.profile.birth.v1"]).toBeNull();
  expect(afterReload["tianji.scenario.target-year.v1"]).toBeNull();
  await expect(baziYearSelect(page)).toHaveValue("");
  // 其余 3 键由挂载 effect 写回默认值——这是应用初始化，不是用户数据恢复
  expect(afterReload["tianji.theme"]).toBe("night");
  expect(afterReload["tianji.product.favorite"]).toBe("false");
  expect(afterReload["tianji.prototype.music"]).toContain('"optedIn":false');
  await expect
    .poll(() => page.evaluate(() => document.documentElement.getAttribute("data-theme")))
    .toBe("night");
});

test("[local-only] TJ-029.2 clear-all resets the theme toggle label without re-writing the key", async ({
  page,
}) => {
  await page.goto("/bazi-profile");
  await seedAllKeys(page);
  await page.reload();

  // 种子主题为宣纸：切换按钮标签应为“宣纸”
  await expect
    .poll(() => page.evaluate(() => document.documentElement.getAttribute("data-theme")))
    .toBe("paper");
  await expect(page.locator(".theme-toggle-label")).toHaveText("宣纸");

  await page.getByRole("button", { name: "清除全部本机资料", exact: true }).click();
  await page
    .locator(".bazi-clear-all-confirm")
    .getByRole("button", { name: "确认清除", exact: true })
    .click();

  // 修复点：按钮标签立即回到“夜景”（React 状态已同步），且主题键
  // 仍缺失——静默重置不得把默认主题重新写入 localStorage
  await expect(page.locator(".theme-toggle-label")).toHaveText("夜景");
  const after = await readKeys(page);
  expect(after["tianji.theme"]).toBeNull();
  await expect
    .poll(() => page.evaluate(() => document.documentElement.getAttribute("data-theme")))
    .toBe("night");
});
