import { test, expect } from "@playwright/test";

/**
 * TJ-008.3: against REAL private assembled API. No mocked request handlers.
 * The summary must come from the actual returned result, not a hard-coded
 * positive fortune / romance / investment prediction.
 */
for (const entry of [
  { path: "/daily-structure", id: "daily", title: "今日运势", scope: "今日运势" },
  { path: "/yearly-structure", id: "yearly", title: "流年运势", scope: "流年运势" },
  { path: "/romance-structure", id: "romance", title: "桃花姻缘", scope: "桃花姻缘" },
  { path: "/career-wealth-structure", id: "career", title: "事业财运", scope: "事业财运" },
] as const) {
  test(`TJ-008.3 ${entry.id} renders a consumer report grounded in real API`, async ({ page }) => {
    await page.goto(entry.path);
    await expect(page.getByRole("heading", { level: 1 })).toBeVisible();
    await expect(page.getByRole("region", { name: "本次测算摘要" })).toHaveCount(0);
    await page.getByRole("button", { name: "填入示例" }).click();

    const response = page.waitForResponse(r =>
      new URL(r.url()).pathname === "/api/v1/scenarios/public" &&
      r.request().method() === "POST",
    );
    await page.locator('form button[type="submit"]').click();
    const reply = await response;
    expect(reply.ok()).toBe(true);
    const data = await reply.json();
    expect(data.scenario_id).toBe(entry.id);
    const summary = page.getByRole("region", { name: "本次测算摘要" });
    await expect(summary).toBeVisible();
    await expect(summary).toContainText(entry.title);
    await expect(summary.locator("dl dt").first()).toBeVisible();
    await expect(summary.locator("dl dd").first()).not.toBeEmpty();
    await expect(summary).toContainText("目前不能断言");
    await expect(summary).toContainText("审核");
    await expect(summary).not.toContainText("好运指数");
    await expect(summary).not.toContainText("匹配度100%");
    // Test that a second section still provides detailed, traceable facts.
    await expect(page.locator("main").getByText("典籍依据", { exact: true }).first()).toBeVisible();
    await page.setViewportSize({ width: 390, height: 844 });
    await page.screenshot({ path: `test-results/tj0083-${entry.id}-390.png`, fullPage: true, animations: "disabled" });
    const overflow = await page.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth);
    expect(overflow).toBeLessThanOrEqual(1);
  });
}

test("TJ-008.3 selected year is not merely relabelled in the summary", async ({ page }) => {
  await page.goto("/yearly-structure");
  await page.getByRole("button", { name: "填入示例" }).click();
  await page.getByLabel("目标年份").fill("2027");
  const responsePromise = page.waitForResponse(r =>
    new URL(r.url()).pathname === "/api/v1/scenarios/public" &&
    r.request().method() === "POST");
  await page.locator('form button[type="submit"]').click();
  const response = await responsePromise;
  expect(response.request().postDataJSON().input.target_year).toBe(2027);
  const payload = await response.json();
  expect(payload.result.target_year.ganzhi).toBeTruthy();
  const summary = page.getByRole("region", { name: "本次测算摘要" });
  await expect(summary).toContainText(payload.result.target_year.ganzhi);
});

test("TJ-008.3 cannot display a personal outcome before real submission", async ({ page }) => {
  await page.goto("/romance-structure");
  await expect(page.getByRole("region", { name: "本次测算摘要" })).toHaveCount(0);
  await expect(page.locator(".romance-empty")).toBeVisible();
});
