/**
 * T-D1 (E0409): career + life first-period dayun wiring, real-backend
 * end-to-end. No stubs: the pages call the real backend through the
 * SSH tunnel (127.0.0.1:8000) and the vite dev server serves this
 * worktree's pages. Each test captures the real scenario response
 * and asserts both the API contract (the legacy dayun_presentation
 * field is first period only; sanming periods 2-8 `unresolved`,
 * shenfeng periods 2-8 `not_provided`, no starting age anywhere)
 * and the rendered section.
 *
 * TJ-031.19 (E0427, Q3=A, 2026-11-28): the legacy field stays
 * first-period-only, but the full 8-period timeline is now presented
 * via the career_presentation / life_presentation (period 2 carries
 * a real interval there, not the trim's `unresolved`). The role tests
 * assert both contracts.
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
    // Adjudicated contract (E0410 / #584): sanming 2-8 are `unresolved`
    // (real intervals cleared; the shared validator forbids sanming +
    // not_provided), shenfeng 2-8 stay `not_provided`.
    const laterState = method === "sanming" ? "unresolved" : "not_provided";
    for (const entry of entries.slice(1)) {
      expect(entry.state).toBe(laterState);
      expect(entry.start_interval).toBeNull();
    }
  }
  const blob = JSON.stringify(body.result);
  for (const key of BANNED_KEYS) {
    expect(blob, `no ${key} anywhere in the response`).not.toContain(key);
  }
}

// TJ-031.19 (E0427, Q3=A): the full 8-period timeline is presented
// via the career presentation -- period 2 carries a real interval
// there, not the legacy field's `unresolved` trim.
function assertFullTimelineInCareerPresentation(body: any) {
  const presentation = body?.result?.career_presentation;
  expect(presentation, "career_presentation present").toBeTruthy();
  const section = presentation.sections.find((s: any) => s.id === "dayun_timeline");
  expect(section, "dayun_timeline section present").toBeTruthy();
  expect(section.status).toBe("presented");
  const entries = section.content.methods.sanming.entries;
  expect(entries).toHaveLength(8);
  expect(entries[1].state).toBe("interval");
  expect(entries[1].start_interval).toBeTruthy();
  expect(entries[7].state).toBe("interval");
  expect(entries[7].start_interval).toBeTruthy();
}

// TJ-031.19 (E0427, Q3=A): the full 8-period timeline is presented
// via the life presentation -- 8 stages, each with a real interval.
function assertFullTimelineInLifePresentation(body: any) {
  const presentation = body?.result?.life_presentation;
  expect(presentation, "life_presentation present").toBeTruthy();
  expect(presentation.dayun.status).toBe("presented");
  expect(presentation.stages).toHaveLength(8);
  expect(presentation.stages[1].start_interval).toBeTruthy();
  expect(presentation.stages[7].start_interval).toBeTruthy();
}

test("[real-backend] T-D1 career: role renders first-period legacy field + full 8-period timeline", async ({ page }) => {
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
  assertFullTimelineInCareerPresentation(captured.body);

  const section = page.locator(".bazi-dayun-presentation");
  await expect(section).toBeVisible();
  await expect(section).toContainText("大运首运方向与交运区间");
  await expect(section).toContainText("第 1 运");
  await expect(section).toContainText("本块只呈现首运方向与交运区间");
  await expect(section).toContainText("完整 8 运时间线见上方");
  await expect(section).toContainText("不折算起运岁数");
  // No computed starting age is rendered anywhere on the page.
  const bodyText = await page.locator("body").textContent();
  expect(bodyText).not.toMatch(/起运\s*\d+\s*岁|\d+\s*岁起运|第 1 运[^。]*\d+ 岁/);

  // Method switch: Shenfeng shows its own first-period interval.
  await section.getByRole("tab", { name: "神峰口径" }).click();
  await expect(section).toContainText("第 1 运");
  await expect(section).toContainText("本块只呈现首运方向与交运区间");
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

test("[real-backend] T-D1 life: role renders first-period legacy field + full 8-period timeline", async ({ page }) => {
  const captured = await captureScenarioResponse(page);
  await page.goto("/life-overview");
  await page.getByRole("button", { name: "填入示例", exact: true }).click();
  await page.locator("#life-dayun-role").selectOption("female");
  await page.getByRole("button", { name: "生成我的人生总览" }).click();
  await expect(page.locator(".life-highlights")).toBeVisible({ timeout: 15000 });

  expect(captured.input?.traditional_role).toBe("female");
  expect(captured.status).toBe(200);
  assertFirstPeriodOnly(captured.body);
  assertFullTimelineInLifePresentation(captured.body);

  // E0422: the dayun section now lives on life-overview screen 3.
  await page.getByRole("tab", { name: "③ 大运流年", exact: true }).click();

  const section = page.locator(".bazi-dayun-presentation");
  await expect(section).toBeVisible();
  await expect(section).toContainText("大运首运方向与交运区间");
  await expect(section).toContainText("第 1 运");
  await expect(section).toContainText("本块只呈现首运方向与交运区间");
  await expect(section).toContainText("完整 8 运时间线见本屏上方完整时间线");
  await expect(section).toContainText("不折算起运岁数");
  const bodyText = await page.locator("body").textContent();
  expect(bodyText).not.toMatch(/起运\s*\d+\s*岁|\d+\s*岁起运|第 1 运[^。]*\d+ 岁/);

  await section.getByRole("tab", { name: "神峰口径" }).click();
  await expect(section).toContainText("第 1 运");
  await expect(section).toContainText("本块只呈现首运方向与交运区间");
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
