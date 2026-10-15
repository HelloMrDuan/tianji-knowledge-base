import { expect, test, type Page } from "@playwright/test";

/**
 * TJ-006.2: FRONTEND STATE CONTRACT TESTS ONLY.
 * Controlled HTTP replies test concurrent requests, invalidation and validation.
 * They are NOT genuine calendrical / production Scenario Engine calculations.
 */

async function saveSample(page: Page) {
  await page.goto("/bazi-profile");
  await page.getByRole("button", { name: "填入示例" }).click();
  await page.getByRole("button", { name: "保存资料" }).click();
  const profile = await page.evaluate(() => JSON.parse(localStorage.getItem("tianji.profile.birth.v1") || "{}"));
  expect(profile.year).toBe(2000);
  expect(profile.time).toBe("12:00");
}

function scenarioResponse(id: string, target: string) {
  return {
    scenario_id: id,
    status: "success",
    public_release: true,
    deterministic: true,
    result: id === "yearly"
      ? {
          target_year: {
            year: Number(target),
            ganzhi: target === "2027" ? "丁未" : "乙巳",
            stem: target === "2027" ? "丁" : "乙",
            branch: target === "2027" ? "未" : "巳",
            stem_ten_god: "食神",
            year_boundary: "solar-term year",
          },
          natal: { day_master: { stem: "甲" }, pillars: [] },
          annual_branch_interactions: { hits: [] },
        }
      : {
          target_day: { date: target, ganzhi: target === "2026-10-16" ? "乙丑" : "甲子", stem: "甲" },
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

test("yearly: first 2025 reply arrives LAST and cannot overwrite latest 2027 result", async ({ page }) => {
  await saveSample(page);
  let releaseOld: (() => void) | undefined;
  let oldDelivered = false;
  const years: number[] = [];
  await page.route("**/api/v1/scenarios/public", async (route) => {
    const data = route.request().postDataJSON();
    expect(data.scenario_id).toBe("yearly");
    const year = Number(data.input.target_year);
    years.push(year);
    if (year === 2025) {
      await new Promise<void>((resolve) => { releaseOld = resolve; });
    }
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify(scenarioResponse("yearly", String(year))),
    });
    if (year === 2025) oldDelivered = true;
  });

  await page.goto("/yearly-structure");
  const year = page.getByLabel("目标年份");
  const submit = page.locator('form button[type="submit"]').first();

  await year.fill("2025");
  await submit.click();
  await expect.poll(() => years).toContain(2025);
  await expect(submit).toBeDisabled();

  // Editing the target invalidates the pending 2025 request and enables a new submit.
  await year.fill("2027");
  await expect(page.locator(".yearly-result")).toHaveCount(0);
  await expect(submit).toBeEnabled();
  await submit.click();
  await expect.poll(() => years).toEqual([2025, 2027]);
  await expect(page.locator(".yearly-result-head")).toContainText("丁未");
  await expect(page.locator(".yearly-result-head")).not.toContainText("乙巳");

  expect(releaseOld).toBeDefined();
  releaseOld!();
  await expect.poll(() => oldDelivered).toBe(true);
  await expect(page.locator(".yearly-result-head")).toContainText("丁未");
  await expect(page.locator(".yearly-result-head")).not.toContainText("乙巳");
  const storedYear = await page.evaluate(() => localStorage.getItem("tianji.scenario.target-year.v1"));
  expect(storedYear).toBe("2027");
});

test("daily: editing VIEW DATE immediately clears the old computed result", async ({ page }) => {
  await saveSample(page);
  const targets: string[] = [];
  await page.route("**/api/v1/scenarios/public", async (route) => {
    const body = route.request().postDataJSON();
    expect(body.scenario_id).toBe("daily");
    targets.push(body.input.target_date);
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify(scenarioResponse("daily", body.input.target_date)),
    });
  });
  await page.goto("/daily-structure");
  const viewDate = page.getByLabel("查看日期");
  await viewDate.fill("2026-10-15");
  await page.locator('form button[type="submit"]').first().click();
  await expect(page.locator(".daily-result-head")).toContainText("2026-10-15");
  expect(targets).toEqual(["2026-10-15"]);

  await viewDate.fill("2026-10-16");
  await expect(page.locator(".daily-result")).toHaveCount(0);
  expect(targets).toEqual(["2026-10-15"]); // changing the field does not submit itself
  await page.locator('form button[type="submit"]').first().click();
  await expect.poll(() => targets).toEqual(["2026-10-15", "2026-10-16"]);
  await expect(page.locator(".daily-result-head")).toContainText("2026-10-16");
});

test("daily: an empty required VIEW DATE prevents API requests", async ({ page }) => {
  await saveSample(page);
  let sent = 0;
  await page.route("**/api/v1/scenarios/public", async (route) => {
    sent += 1;
    await route.abort();
  });
  await page.goto("/daily-structure");
  const viewDate = page.getByLabel("查看日期");
  await viewDate.fill("");
  expect(await viewDate.evaluate((el) => (el as HTMLInputElement).validity.valueMissing)).toBe(true);
  await page.locator('form button[type="submit"]').first().click();
  expect(sent).toBe(0);
  await expect(page.locator(".daily-result")).toHaveCount(0);
});

test("yearly: 1900/2100 are blocked and 1901 is accepted by frontend bounds", async ({ page }) => {
  await saveSample(page);
  const requestedYears: number[] = [];
  await page.route("**/api/v1/scenarios/public", async (route) => {
    const body = route.request().postDataJSON();
    requestedYears.push(body.input.target_year);
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify(scenarioResponse("yearly", String(body.input.target_year))),
    });
  });
  await page.goto("/yearly-structure");
  const year = page.getByLabel("目标年份");
  const submit = page.locator('form button[type="submit"]').first();
  await expect(year).toHaveAttribute("min", "1901");
  await expect(year).toHaveAttribute("max", "2098");

  await year.fill("1900");
  expect(await year.evaluate((el) => (el as HTMLInputElement).validity.rangeUnderflow)).toBe(true);
  await submit.click();
  expect(requestedYears).toEqual([]);

  await year.fill("2100");
  expect(await year.evaluate((el) => (el as HTMLInputElement).validity.rangeOverflow)).toBe(true);
  await submit.click();
  expect(requestedYears).toEqual([]);

  await year.fill("1901");
  expect(await year.evaluate((el) => (el as HTMLInputElement).validity.valid)).toBe(true);
  await submit.click();
  await expect.poll(() => requestedYears).toEqual([1901]);
  await expect(page.locator(".yearly-result")).toBeVisible();
});
