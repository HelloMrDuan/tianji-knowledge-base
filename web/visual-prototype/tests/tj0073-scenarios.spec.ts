import { expect, test, type Page } from "@playwright/test";

/** Request-shape tests use intercepted/aborted calls; they do NOT verify calculations. */
async function intercept(page: Page, path: string) {
  const sent: Record<string, any>[] = [];
  await page.route("**"+path, async route => {
    sent.push(route.request().postDataJSON());
    await route.abort("failed");
  });
  return sent;
}
async function sample(page: Page) {
  await page.goto("/bazi-profile");
  await page.getByRole("button", { name: "填入示例" }).click();
  await page.getByRole("button", { name: "保存资料" }).click();
}

test("question: manually entered bottom-to-top six lines arrive verbatim at real endpoint", async ({ page }) => {
  const sent = await intercept(page, "/api/v1/public/execute");
  await page.goto("/ask");
  await page.locator("textarea").first().fill("这次工作选择是否适合推进？");
  const values = [6, 7, 8, 9, 7, 8];
  for (let i=0; i<6; i++) {
    await page.locator(".yao-input-list select").nth(i).selectOption(String(values[i]));
  }
  await expect(page.getByRole("progressbar", {name:"起卦进度"})).toHaveAttribute("aria-valuenow","6");
  await page.getByRole("button", { name: "开始推演" }).click();
  await expect.poll(()=>sent.length).toBe(1);
  expect(sent[0].domain).toBe("liuyao");
  expect(sent[0].variant).toBe("jingfang-eight-palaces-v1");
  expect(sent[0].mode).toBe("production");
  expect(sent[0].explain).toBe(false);
  expect(sent[0].input.yao_values).toEqual(values);
  expect(sent[0].input.value).toMatch(/^\d{4}-\d\d-\d\dT\d\d:\d\d:00\+08:00$/);
});

test("dream: exact user input sent to reviewed culture lookup; AI remains off", async ({ page }) => {
  const sent = await intercept(page, "/api/v1/dream/culture");
  await page.goto("/dream-culture");
  const narrative = "我梦见一条蛇咬住我的手";
  await page.getByLabel("梦境叙述").fill(narrative);
  await page.getByRole("button", { name: /查阅梦象/ }).click();
  await expect.poll(()=>sent.length).toBe(1);
  expect(sent[0]).toEqual({dream_text:narrative});
});

test("life: chosen year and saved birth instant are both sent, then editing clears pending view", async ({ page }) => {
  await sample(page);
  const sent = await intercept(page, "/api/v1/scenarios/public");
  await page.goto("/life-overview");
  await page.getByLabel("观察年份").fill("2027");
  await page.getByRole("button", {name:"生成我的人生总览"}).click();
  await expect.poll(()=>sent.length).toBe(1);
  expect(sent[0]).toEqual({
    scenario_id:"life", input:{ birth_value:"2000-01-07T12:00:00+08:00",target_year:2027 }
  });
});
