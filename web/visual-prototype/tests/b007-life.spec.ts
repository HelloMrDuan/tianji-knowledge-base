import { test, expect, type Page } from "@playwright/test";

/** TJ-025.3: REAL CHROMIUM with CONTROLLED HTTP fixtures.
 * This is a frontend journey/regression test, not real Scenario Engine math
 * or private Canonical/Evidence acceptance. API responses are synthetic.
 */
const apiEndpoint = "**/api/v1/scenarios/public";

function controlledLifeResponse(targetYear: number) {
  const gz = targetYear === 2027 ? "丁未" : "丙午";
  return {
    scenario_id: "life",
    status: "production_limited",
    public_release: false,
    deterministic: true,
    result: {
      release_scope: "deterministic_aggregate_only",
      profile: {
        day_master: { stem: "甲" },
        pillars: [
          { name: "year", ganzhi: "庚辰", stem: { ten_god: "七杀" }, branch: { value: "辰" } },
          { name: "month", ganzhi: "丁丑", stem: { ten_god: "伤官" }, branch: { value: "丑" } },
          { name: "day", ganzhi: "甲子", stem: { ten_god: "日元" }, branch: { value: "子" } },
          { name: "hour", ganzhi: "庚午", stem: { ten_god: "七杀" }, branch: { value: "午" } },
        ],
      },
      yearly: { target_year: { year: targetYear, ganzhi: gz, stem_ten_god: "食神" } },
      romance: { xianchi: { targets: { year_branch: "酉", day_branch: "酉" } },
        target_year_activation: {} },
      career: { structure_groups: {}, interpretation_cards: [], target_year: { structure_group: "output" } },
      highlights: [],
    },
    evidence: {}, rule_matches: [], trace: [], warnings: [], limitations: [],
  };
}

async function interceptLife(page: Page, seen: number[]) {
  await page.route(apiEndpoint, async (route) => {
    const body = route.request().postDataJSON();
    expect(body.scenario_id).toBe("life");
    expect(body.input.birth_value).toBe("2000-01-07T12:00:00+08:00");
    const year = Number(body.input.target_year);
    seen.push(year);
    await route.fulfill({
      status: 200, contentType: "application/json",
      body: JSON.stringify(controlledLifeResponse(year)),
    });
  });
}

test("TJ-025.3 home → life → detail; year switch invalidates old result and re-requests", async ({ page }) => {
  const years: number[] = [];
  await interceptLife(page, years);

  await page.goto("/");
  const lifeLink = page.locator('a[href="/life-overview"]').first();
  await expect(lifeLink).toBeVisible();
  await lifeLink.click();
  await expect(page).toHaveURL(/\/life-overview$/);

  await page.getByRole("button", { name: "填入示例", exact: true }).click();
  await page.locator(".life-submit").click();
  await expect(page.locator(".life-result")).toBeVisible();
  expect(years).toHaveLength(1);
  await expect(page.locator(".life-result-head")).toContainText("丙午");
  for (const label of ["命盘基础", "流年结构", "桃花结构", "事业财运结构"]) {
    await expect(page.locator(".life-result")).toContainText(label);
  }

  await page.locator(".life-year input").fill("2027");
  await expect(page.locator(".life-result")).toHaveCount(0);
  expect(years).toHaveLength(1); // editing is NOT submitting
  await page.locator(".life-submit").click();
  await expect(page.locator(".life-result-head")).toContainText("丁未");
  expect(years).toEqual([years[0], 2027]);
  await expect(page.locator(".life-result-head")).not.toContainText("丙午");

  await page.locator('.life-next-actions a[href="/career-wealth-structure"]').click();
  await expect(page).toHaveURL(/\/career-wealth-structure$/);
  expect(years).toHaveLength(2); // navigation must not rerun life
});

test("TJ-025.3 clearing profile invalidates the result and never fabricates a verdict", async ({ page }) => {
  const years: number[] = [];
  await interceptLife(page, years);
  await page.goto("/life-overview");
  await page.getByRole("button", { name: "填入示例", exact: true }).click();
  await page.locator(".life-submit").click();
  await expect(page.locator(".life-result")).toBeVisible();
  await expect(page.locator(".life-boundary")).toContainText("不是完整人生预测");

  await page.getByRole("button", { name: "清除本机资料" }).click();
  await expect(page.locator(".life-result")).toHaveCount(0);
  await expect(page.locator('.life-entry input[type="date"]')).toHaveValue("");
  await expect(page.locator('.life-entry input[type="time"]')).toHaveValue("");
  expect(years).toHaveLength(1);
  await page.locator(".life-submit").click();
  expect(years).toHaveLength(1); // required fields reject request
});

test("TJ-025.3 controlled API: 360/390/768/1440px life result has no horizontal overflow", async ({ page }) => {
  const years: number[] = [];
  await interceptLife(page, years);
  for (const width of [360, 390, 768, 1440]) {
    await page.setViewportSize({ width, height: width >= 768 ? 900 : 844 });
    await page.goto("/life-overview");
    await page.getByRole("button", { name: "填入示例", exact: true }).click();
    await page.locator(".life-submit").click();
    await expect(page.locator(".life-result")).toBeVisible();
    const diff = await page.evaluate(() =>
      document.documentElement.scrollWidth - document.documentElement.clientWidth);
    expect(diff, `${width}px horizontal overflow`).toBeLessThanOrEqual(1);
  }
  expect(years).toHaveLength(4);
});
