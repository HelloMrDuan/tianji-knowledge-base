import { test, expect } from "@playwright/test";

test("birth chart and life report display the same reviewed strength facts with real private API", async ({ page }) => {
  const calls: Array<{ scenario?: string; year?: number }> = [];
  page.on("request", (request) => {
    if (request.method() !== "POST") return;
    const url = new URL(request.url());
    const body = request.postDataJSON();
    if (url.pathname === "/api/v1/scenarios/public")
      calls.push({ scenario: body.scenario_id, year: body.input.target_year });
    if (url.pathname === "/api/v1/public/execute" && body.domain === "bazi")
      expect(body.input.strength_variant).toBe("ditiansui-root-visibility-v1");
  });

  await page.goto("/bazi-profile");
  await page.getByRole("button", { name: "填入示例" }).click();
  await page.getByRole("button", { name: "生成基础档案" }).click();
  const factors = page.getByLabel("旺衰因素与通根候选");
  await expect(factors).toContainText("通根候选");
  await expect(factors).toContainText("身强身弱");
  await factors.locator("summary").click();
  await expect(factors.locator("blockquote p").first()).not.toBeEmpty();

  await page.goto("/life-overview");
  await page.getByLabel("观察年份").fill("2026");
  await page.getByRole("button", { name: /生成人生总览|生成我的人生总览/ }).click();
  const integrated = page.getByLabel("旺衰因素与年度综合解读");
  await expect(integrated).toContainText("2026年");
  await expect(integrated).toContainText("日主");
  await expect(integrated).toContainText("大运方向");
  await expect(integrated).toContainText("跨规则一致性");
  await expect(integrated).toContainText("并非两份独立证据");
  const sourceCheck = page.getByLabel("四场景来源一致性核验");
  await expect(sourceCheck).toContainText("出生盘与目标年份已跨场景核对一致");
  await expect(sourceCheck).toContainText("同一套证据的交叉核查");
  for (const title of ["命盘基础", "年度结构", "桃花结构", "事业财运"])
    await expect(sourceCheck).toContainText(title);
  await integrated.locator("summary").click();
  await expect(integrated.locator("blockquote p").first()).not.toBeEmpty();
  expect(calls).toContainEqual({ scenario: "life", year: 2026 });

  await page.getByLabel("观察年份").fill("2027");
  await expect(integrated).toHaveCount(0);
  await page.getByRole("button", { name: /生成人生总览|生成我的人生总览/ }).click();
  await expect(page.getByLabel("旺衰因素与年度综合解读")).toContainText("2027年");
  await expect(page.getByLabel("旺衰因素与年度综合解读")).toContainText("跨规则一致性");
  expect(calls).toContainEqual({ scenario: "life", year: 2027 });
});
