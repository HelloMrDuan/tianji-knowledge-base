import { test, expect, type Page } from "@playwright/test";

/**
 * TJ-007.4 controlled browser-contract tests. API replies are intercepted;
 * these tests DO NOT prove authentic Scenario Engine calculations.
 */

async function saveBirth(page: Page) {
  await page.goto("/bazi-profile");
  await page.getByRole("button", { name: "填入示例" }).click();
  await page.getByRole("button", { name: "保存资料" }).click();
  await expect.poll(() => page.evaluate(() => localStorage.getItem("tianji.profile.birth.v1"))).not.toBeNull();
}

function validDailyResponse(targetDate: string) {
  return {
    scenario_id: "daily",
    status: "success",
    public_release: true,
    deterministic: true,
    result: {
      target_day: { date: targetDate, ganzhi: "甲子", stem: "甲" },
      natal: { day_master: { stem: "甲" } },
      xianchi: { target_day_activation: {} },
    },
    rule_matches: [],
    evidence: {},
    trace: [],
    warnings: [],
    limitations: [],
  };
}

test("history never impersonates a saved reading; favorited demo stays explicitly a demo", async ({ page }) => {
  await page.goto("/history");
  await expect(page.getByRole("heading", { name: "暂无真实推演历史" })).toBeVisible();
  await expect(page.locator(".journal-row")).toHaveCount(0);
  await page.goto("/liuyao/result");
  await page.getByRole("button", { name: "收藏示例", exact: true }).click();
  await page.goto("/history");
  await expect(page.locator(".journal-row")).toHaveCount(0);
  await expect(page.getByRole("heading", { name: "暂无真实推演历史" })).toBeVisible();
  await page.reload();
  await expect(page.locator(".journal-row")).toHaveCount(0);
  await page.goto("/favorites");
  await expect(page.locator(".journal-row")).toContainText("乾为天");
  await expect(page.locator(".journal-date")).toContainText("演示收藏");
});

test("retry after HTTP 503 preserves saved birth profile and clears the old error", async ({ page }) => {
  await saveBirth(page);
  const original = await page.evaluate(() => localStorage.getItem("tianji.profile.birth.v1"));
  let attempts = 0;
  await page.route("**/api/v1/scenarios/public", async route => {
    const request = route.request().postDataJSON();
    expect(request.scenario_id).toBe("daily");
    attempts++;
    if (attempts === 1) {
      await route.fulfill({ status: 503, contentType: "application/json", body: JSON.stringify({detail:{message:"服务暂不可用"}}) });
    } else {
      await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify(validDailyResponse(request.input.target_date)) });
    }
  });
  await page.goto("/daily-structure");
  await expect(page.getByLabel("出生日期")).toHaveValue("2000-01-07");
  await page.getByLabel("查看日期").fill("2026-10-15");
  const submit = page.locator('form button[type="submit"]').first();
  await submit.click();
  await expect(page.getByRole("alert")).toContainText("服务暂不可用");
  await expect(page.locator(".daily-result")).toHaveCount(0);
  expect(await page.evaluate(() => localStorage.getItem("tianji.profile.birth.v1"))).toBe(original);
  await submit.click();
  await expect(page.locator(".daily-result-head")).toContainText("2026-10-15");
  await expect(page.getByRole("alert")).toHaveCount(0);
  expect(attempts).toBe(2);
  expect(await page.evaluate(() => localStorage.getItem("tianji.profile.birth.v1"))).toBe(original);
});

test("offline request displays an error and user can retry without losing inputs", async ({ page }) => {
  await saveBirth(page);
  let attempts = 0;
  await page.route("**/api/v1/scenarios/public", async route => {
    attempts++;
    if (attempts === 1) await route.abort("internetdisconnected");
    else await route.fulfill({ status: 200, contentType: "application/json",
      body: JSON.stringify(validDailyResponse(route.request().postDataJSON().input.target_date)) });
  });
  await page.goto("/daily-structure");
  const date = page.getByLabel("查看日期");
  await date.fill("2026-10-16");
  const submit = page.locator('form button[type="submit"]').first();
  await submit.click();
  await expect(page.getByRole("alert")).toBeVisible();
  await expect(date).toHaveValue("2026-10-16");
  await expect(page.getByLabel("出生日期")).toHaveValue("2000-01-07");
  await submit.click();
  await expect(page.locator(".daily-result-head")).toContainText("2026-10-16");
  await expect(page.getByRole("alert")).toHaveCount(0);
  expect(attempts).toBe(2);
});

for (const width of [1440, 390, 360]) {
  test(`empty real-history viewport ${width} has no overflow or fake rows`, async ({ page }, testInfo) => {
    await page.setViewportSize({ width, height: 900 });
    await page.goto("/history");
    await expect(page.getByRole("heading", { name: "暂无真实推演历史" })).toBeVisible();
    await expect(page.locator(".journal-row")).toHaveCount(0);
    const overflow = await page.evaluate(() => document.documentElement.scrollWidth > window.innerWidth + 1);
    expect(overflow).toBe(false);
    await page.screenshot({ path: testInfo.outputPath(`history-${width}.png`), fullPage: true });
  });
}
