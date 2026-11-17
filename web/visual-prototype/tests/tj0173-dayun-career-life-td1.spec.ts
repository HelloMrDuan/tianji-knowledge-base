/**
 * T-D1 (E0409): career + life first-period dayun wiring, real-backend
 * end-to-end. No stubs: the pages call the real backend through the
 * SSH tunnel (127.0.0.1:8000) and the vite dev server serves this
 * worktree's pages. Each test captures the real scenario response
 * and asserts both the API contract (first period only, periods 2-8
 * not_provided, no starting age anywhere) and the rendered section.
 *
 * SEQUENCING NOTE: the role tests can only pass once this slice has
 * merged AND deployed -- production still runs the old contract
 * (career/life reject traditional_role). Until then they fail at the
 * backend rejection (the API returns an error and no dayun section
 * renders); the no-role tests pass against either contract.
 */
import { expect, test, type Page } from "@playwright/test";

const BANNED_KEYS = ["start_age", "end_age", "start_date", "end_date"];

async function captureScenarioResponse(page: Page) {
  const captured: { status?: number; body?: any; input?: any } = {};
  page.on("response", async (res) => {
    if (res.url().includes("/api/v1/scenarios/public") && res.request().method() === "POST") {
      captured.status = res.status();
      captured.input = res.request().postDataJSON()?.input;
      try {
        captured.body = await res.json();
      } catch {
        captured.body = undefined;
      }
    }
  });
  return captured;
}

function assertFirstPeriodOnly(body: any) {
  const presentation = body?.result?.dayun_presentation;
  expect(presentation, "dayun_presentation present").toBeTruthy();
  expect(Object.keys(presentation).sort()).toEqual(
    ["evidence", "limitations", "method_options", "methods", "role", "scope", "status", "variant"]);
  for (const method of ["sanming", "shenfeng"] as const) {
    const entries = presentation.methods[method].entries;
    expect(entries).toHaveLength(8);
    expect(entries[0].period_index).toBe(1);
    expect(entries[0].state).toBe("interval");
    expect(entries[0].start_interval).toBeTruthy();
    for (const entry of entries.slice(1)) {
      expect(entry.state).toBe("not_provided");
      expect(entry.start_interval).toBeNull();
    }
  }
  const blob = JSON.stringify(body.result);
  for (const key of BANNED_KEYS) {
    expect(blob, `no ${key} anywhere in the response`).not.toContain(key);
  }
}

test("[real-backend] T-D1 career: role renders first-period dayun only", async ({ page }) => {
  const captured = await captureScenarioResponse(page);
  await page.goto("/career-wealth-structure");
  await page.getByRole("button", { name: "填入示例", exact: true }).click();
  await page.locator("#career-dayun-role").selectOption("male");
  await page.getByRole("button", { name: "查看事业财运结构" }).click();
  await expect(page.locator(".career-groups")).toBeVisible({ timeout: 15000 });

  // The role is sent only because it was explicitly selected.
  expect(captured.input?.traditional_role).toBe("male");
  expect(captured.status).toBe(200);
  assertFirstPeriodOnly(captured.body);

  const section = page.locator(".bazi-dayun-presentation");
  await expect(section).toBeVisible();
  await expect(section).toContainText("大运首运方向与交运区间");
  await expect(section).toContainText("第 1 运");
  await expect(section).toContainText("第 2–8 运尚未在本场景开放");
  await expect(section).toContainText("不折算起运岁数或日期");
  // No computed starting age is rendered anywhere on the page.
  const bodyText = await page.locator("body").textContent();
  expect(bodyText).not.toMatch(/起运\s*\d+\s*岁|\d+\s*岁起运|第 1 运[^。]*\d+ 岁/);

  // Method switch: Shenfeng shows its own first-period interval.
  await section.getByRole("tab", { name: "神峰口径" }).click();
  await expect(section).toContainText("第 1 运");
  await expect(section).toContainText("第 2–8 运尚未在本场景开放");
});

test("[real-backend] T-D1 career: no role means no dayun section", async ({ page }) => {
  const captured = await captureScenarioResponse(page);
  await page.goto("/career-wealth-structure");
  await page.getByRole("button", { name: "填入示例", exact: true }).click();
  await page.getByRole("button", { name: "查看事业财运结构" }).click();
  await expect(page.locator(".career-groups")).toBeVisible({ timeout: 15000 });

  expect(captured.input?.traditional_role).toBeUndefined();
  expect(captured.status).toBe(200);
  expect(captured.body?.result?.dayun_presentation).toBeUndefined();
  await expect(page.locator(".bazi-dayun-presentation")).toHaveCount(0);
});

test("[real-backend] T-D1 life: role renders first-period dayun only", async ({ page }) => {
  const captured = await captureScenarioResponse(page);
  await page.goto("/life-overview");
  await page.getByRole("button", { name: "填入示例", exact: true }).click();
  await page.locator("#life-dayun-role").selectOption("female");
  await page.getByRole("button", { name: "生成我的人生总览" }).click();
  await expect(page.locator(".life-highlights")).toBeVisible({ timeout: 15000 });

  expect(captured.input?.traditional_role).toBe("female");
  expect(captured.status).toBe(200);
  assertFirstPeriodOnly(captured.body);

  const section = page.locator(".bazi-dayun-presentation");
  await expect(section).toBeVisible();
  await expect(section).toContainText("大运首运方向与交运区间");
  await expect(section).toContainText("第 1 运");
  await expect(section).toContainText("第 2–8 运尚未在本场景开放");
  await expect(section).toContainText("不折算起运岁数或日期");
  const bodyText = await page.locator("body").textContent();
  expect(bodyText).not.toMatch(/起运\s*\d+\s*岁|\d+\s*岁起运|第 1 运[^。]*\d+ 岁/);

  await section.getByRole("tab", { name: "神峰口径" }).click();
  await expect(section).toContainText("第 1 运");
  await expect(section).toContainText("第 2–8 运尚未在本场景开放");
});

test("[real-backend] T-D1 life: no role means no dayun section", async ({ page }) => {
  const captured = await captureScenarioResponse(page);
  await page.goto("/life-overview");
  await page.getByRole("button", { name: "填入示例", exact: true }).click();
  await page.getByRole("button", { name: "生成我的人生总览" }).click();
  await expect(page.locator(".life-highlights")).toBeVisible({ timeout: 15000 });

  expect(captured.input?.traditional_role).toBeUndefined();
  expect(captured.status).toBe(200);
  expect(captured.body?.result?.dayun_presentation).toBeUndefined();
  await expect(page.locator(".bazi-dayun-presentation")).toHaveCount(0);
});
