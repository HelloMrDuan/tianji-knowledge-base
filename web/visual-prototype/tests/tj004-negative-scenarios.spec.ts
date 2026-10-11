import { test, expect } from "@playwright/test";

/** TJ-004.3 faults and invalid inputs against the real user application.
 * No mock positive business result. Network fault injection and reviewed-source
 * removal are intentional negative cases; retries query the real assembled API.
 */
const natalRoutes = [
  "/bazi-profile", "/daily-structure", "/weekly-structure",
  "/monthly-structure", "/yearly-structure", "/romance-structure",
  "/career-wealth-structure", "/compatibility-structure", "/life-overview",
];

for (const route of natalRoutes) {
  test(`TJ-004.3 ${route}: missing mandatory birth time cannot submit`, async ({ page }) => {
    let count = 0;
    page.on("request", req => { if (new URL(req.url()).pathname.startsWith("/api/")) count++; });
    await page.goto(route);
    const button = page.locator('form button[type="submit"]');
    await expect(button).toBeVisible();
    // No previous user consent and no valid birth time. HTML validity must block API.
    if (await button.isEnabled()) await button.click();
    await expect(page.locator('form input[type="time"]').first()).toBeInvalid();
    expect(count).toBe(0);
    await expect(page.locator(".consumer-result-summary")).toHaveCount(0);
  });
}

test("TJ-004.3 an incomplete coin casting cannot call private Bazi/Liuyao", async ({ page }) => {
  let count = 0;
  page.on("request", req => { if (new URL(req.url()).pathname.startsWith("/api/")) count++; });
  await page.goto("/ask");
  const button = page.locator('form button[type="submit"]');
  await expect(button).toBeDisabled();
  expect(count).toBe(0);
});

test("TJ-004.3 a one-character dream does not call the cultural API", async ({ page }) => {
  let count = 0;
  page.on("request", req => { if (new URL(req.url()).pathname.startsWith("/api/")) count++; });
  await page.goto("/dream-culture");
  await page.locator("textarea").fill("蛇");
  await page.locator('form button[type="submit"]').click();
  await expect(page.locator("textarea")).toBeInvalid();
  expect(count).toBe(0);
  await expect(page.locator(".dream-culture-match")).toHaveCount(0);
});

for (const route of ["/yearly-structure", "/romance-structure", "/career-wealth-structure"]) {
  test(`TJ-004.3 ${route}: offline failure is visible and recovery hits real API`, async ({ page }) => {
    await page.goto(route);
    await page.getByRole("button", { name: "填入示例" }).click();
    await page.route("**/api/v1/scenarios/public", route => route.abort("failed"));
    await page.locator('form button[type="submit"]').click();
    await expect(page.getByRole("alert")).toBeVisible();
    await expect(page.locator(".consumer-result-summary")).toHaveCount(0);
    await page.unroute("**/api/v1/scenarios/public");
    const response = page.waitForResponse(r =>
      new URL(r.url()).pathname === "/api/v1/scenarios/public" && r.request().method() === "POST");
    await page.locator('form button[type="submit"]').click();
    expect((await response).status()).toBe(200);
    await expect(page.getByRole("region", { name: "本次测算摘要" })).toBeVisible();
  });
}

test("TJ-004.3 source omission must not invent an ancient quote", async ({ page }) => {
  await page.goto("/yearly-structure");
  await page.getByRole("button", { name: "填入示例" }).click();
  await page.route("**/api/v1/scenarios/public", async route => {
    const actual = await route.fetch();
    const data = await actual.json();
    // Actual deterministic result preserved, reviewed citation part deliberately omitted.
    await route.fulfill({ response: actual, json: { ...data, evidence: {} } });
  });
  await page.locator('form button[type="submit"]').click();
  const summary = page.getByRole("region", { name: "本次测算摘要" });
  await expect(summary).toBeVisible();
  await expect(summary).toContainText("没有收到可展示的完整审核短引");
});

test("TJ-004.3 a late old-year API response must not overwrite the newer result", async ({ page }) => {
  await page.goto("/yearly-structure");
  await page.getByRole("button", { name: "填入示例" }).click();
  await page.getByLabel("目标年份").fill("2026");
  let captured: () => void = () => {};
  let release: () => void = () => {};
  const oldCaptured = new Promise<void>(resolve => { captured = resolve; });
  const oldReleased = new Promise<void>(resolve => { release = resolve; });
  await page.route("**/api/v1/scenarios/public", async route => {
    const request = route.request().postDataJSON();
    const real = await route.fetch();
    if (request.input?.target_year === 2026) {
      captured();
      await oldReleased;
    }
    await route.fulfill({ response: real });
  });
  await page.locator('form button[type="submit"]').click();
  await oldCaptured;
  await page.getByLabel("目标年份").fill("2027");
  const newResponse = page.waitForResponse(r =>
    new URL(r.url()).pathname === "/api/v1/scenarios/public" &&
    r.request().postDataJSON()?.input?.target_year === 2027);
  await page.locator('form button[type="submit"]').click();
  const second = await newResponse;
  const secondData = await second.json();
  await expect(page.getByRole("region", { name: "本次测算摘要" }))
    .toContainText(secondData.result.target_year.ganzhi);
  release();
  await page.waitForTimeout(220);
  await expect(page.getByRole("region", { name: "本次测算摘要" }))
    .toContainText(secondData.result.target_year.ganzhi);
  await expect(page.getByLabel("目标年份")).toHaveValue("2027");
});
