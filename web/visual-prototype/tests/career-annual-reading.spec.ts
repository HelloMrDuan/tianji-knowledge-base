import { test, expect } from "@playwright/test";

test("career annual synthesis is computed for selected year and grounded in source excerpts", async ({ page }) => {
  const years: number[] = [];
  page.on("request", (request) => {
    if (new URL(request.url()).pathname === "/api/v1/scenarios/public" &&
        request.method() === "POST") {
      const payload = request.postDataJSON();
      if (payload.scenario_id === "career") years.push(payload.input.target_year);
    }
  });

  await page.goto("/career-wealth-structure");
  await page.getByRole("button", { name: "填入示例" }).click();
  await page.getByLabel("观察年份").fill("2026");
  await page.getByRole("button", { name: "查看事业财运结构" }).click();

  const reading = page.getByLabel("年度十神与原局综合解读");
  await expect(reading).toContainText("2026年");
  await expect(reading).toContainText("回看原局");
  await expect(reading).toContainText("未判定月令旺衰");
  await reading.locator("summary").click();
  await expect(reading.locator("blockquote")).not.toHaveCount(0);
  await expect(reading.locator("blockquote p").first()).not.toBeEmpty();

  await page.getByLabel("观察年份").fill("2027");
  await expect(reading).toHaveCount(0);
  await page.getByRole("button", { name: "查看事业财运结构" }).click();
  await expect(page.getByLabel("年度十神与原局综合解读")).toContainText("2027年");
  expect(years).toEqual([2026, 2027]);
});
