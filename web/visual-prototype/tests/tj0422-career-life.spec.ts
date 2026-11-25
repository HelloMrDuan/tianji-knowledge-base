/**
 * TJ-0422 phase 2 slice B: career three layers + life five screens.
 *
 * Local tests (no backend needed) cover page rendering, zero calls on
 * load, friendly errors, shared localStorage prefill and the shared
 * target-year key read on mount. They must pass in this sandbox with
 * no sealed runtime and no backend on 127.0.0.1:8000.
 *
 * Real-backend tests run ONLY when TIANJI_E2E_RUNTIME_BACKEND is set
 * to the URL of a runtime-capable test backend AND the vite dev server
 * proxies /api to that backend (vite.config.ts points at
 * 127.0.0.1:8000 by default; point it at the test backend for this
 * run). They assert the real envelopes: the three lifted presentations
 * on the career/life top level, the lazy full-8 dayun fetch from
 * bazi-profile, current-period resolution, branch interactions, the
 * year stepper re-request, and the life deep links preserving birth
 * data + the shared year. Without the env var they are skipped, so
 * public CI stays green. No stubs anywhere: a skipped real-backend
 * test is reported as skipped, never as passed.
 */
import { test, expect, type Page } from "@playwright/test";

const RUNTIME_BACKEND = process.env.TIANJI_E2E_RUNTIME_BACKEND || "";
const SAMPLE_PROFILE = {
  calendarType: "solar",
  year: 2000,
  month: 1,
  day: 7,
  isLeapMonth: false,
  time: "12:00",
  timeUnknown: false,
  region: "中国大陆",
};

async function collectScenarioRequests(page: Page) {
  const calls: Array<{ scenario?: string; year?: number; role?: string }> = [];
  page.on("request", (request) => {
    if (request.method() !== "POST") return;
    if (new URL(request.url()).pathname !== "/api/v1/scenarios/public") return;
    const payload = request.postDataJSON();
    calls.push({
      scenario: payload.scenario_id,
      year: payload.input?.target_year,
      role: payload.input?.traditional_role,
    });
  });
  return calls;
}

test("career page loads with no API calls and shows the empty state", async ({ page }) => {
  const calls = await collectScenarioRequests(page);
  await page.goto("/career-wealth-structure");
  await expect(page.getByRole("heading", { name: "事业与财运，先看可核对的线索。" })).toBeVisible();
  await expect(page.getByText("没有预制“财运指数”")).toBeVisible();
  await expect(page.getByLabel("命局基础")).toHaveCount(0);
  await expect(page.getByLabel("当前大运")).toHaveCount(0);
  await expect(page.getByLabel("指定流年")).toHaveCount(0);
  expect(calls).toEqual([]);
});

test("career submit with no backend shows a friendly error and never fires the lazy dayun call", async ({ page }) => {
  // Premise is "no backend": with a runtime-capable backend the
  // submit succeeds and no alert appears, so skip there.
  test.skip(!!RUNTIME_BACKEND, "assumes no backend is reachable (TIANJI_E2E_RUNTIME_BACKEND unset)");
  const calls = await collectScenarioRequests(page);
  await page.goto("/career-wealth-structure");
  await page.getByRole("button", { name: "填入示例" }).click();
  await page.getByLabel("观察年份").fill("2026");
  await page.getByRole("button", { name: "查看事业财运结构" }).click();
  await expect(page.getByRole("alert")).toBeVisible();
  await expect(page.getByLabel("命局基础")).toHaveCount(0);
  // Exactly one career attempt; the bazi-profile timeline call is lazy
  // and only fires from the Layer B button, which never renders here.
  expect(calls.filter((call) => call.scenario === "bazi-profile")).toEqual([]);
  expect(calls.filter((call) => call.scenario === "career")).toHaveLength(1);
});

test("life page reads the shared target year on mount and shows no screens before a result", async ({ page }) => {
  await page.addInitScript(() => {
    localStorage.setItem("tianji.scenario.target-year.v1", "2031");
    localStorage.setItem("tianji.profile.birth.v1", JSON.stringify({
      calendarType: "solar", year: 2000, month: 1, day: 7,
      isLeapMonth: false, time: "12:00", timeUnknown: false, region: "中国大陆",
    }));
  });
  await page.goto("/life-overview");
  await expect(page.getByLabel("观察年份")).toHaveValue("2031");
  await expect(page.getByLabel("出生日期")).toHaveValue("2000-01-07");
  await expect(page.getByLabel("出生时间")).toHaveValue("12:00");
  await expect(page.getByLabel("总览分屏")).toHaveCount(0);
  await expect(page.getByText("出生时间须精确到分钟")).toBeVisible();
});

test("birth profile prefill is reused across the career and life pages without retyping", async ({ page }) => {
  await page.addInitScript((profile) => {
    localStorage.setItem("tianji.profile.birth.v1", JSON.stringify(profile));
  }, SAMPLE_PROFILE);
  await page.goto("/life-overview");
  await expect(page.getByLabel("出生日期")).toHaveValue("2000-01-07");
  await expect(page.getByLabel("出生时间")).toHaveValue("12:00");
  await page.goto("/career-wealth-structure");
  await expect(page.getByLabel("出生日期")).toHaveValue("2000-01-07");
  await expect(page.getByLabel("出生时间")).toHaveValue("12:00");
});

test("life submit with no backend shows a friendly error and no screens", async ({ page }) => {
  // Premise is "no backend": with a runtime-capable backend the
  // submit succeeds and no alert appears, so skip there.
  test.skip(!!RUNTIME_BACKEND, "assumes no backend is reachable (TIANJI_E2E_RUNTIME_BACKEND unset)");
  await page.goto("/life-overview");
  await page.getByRole("button", { name: "填入示例" }).click();
  await page.getByLabel("观察年份").fill("2026");
  await page.getByRole("button", { name: "生成我的人生总览" }).click();
  await expect(page.getByRole("alert")).toBeVisible();
  await expect(page.getByLabel("总览分屏")).toHaveCount(0);
});

// ---- real-backend tests: skipped locally, re-verified on the trusted machine ----
test.describe("real backend", () => {
  test.skip(!RUNTIME_BACKEND, "needs a runtime-capable test backend (TIANJI_E2E_RUNTIME_BACKEND)");

  test("career three layers: lifted presentations, lazy full-8 dayun, branch structure, year stepper", async ({ page }) => {
    const calls = await collectScenarioRequests(page);
    await page.goto("/career-wealth-structure");
    await page.getByRole("button", { name: "填入示例" }).click();
    await page.getByLabel("观察年份").fill("2026");
    await page.locator("#career-dayun-role").selectOption("male");
    await page.getByRole("button", { name: "查看事业财运结构" }).click();
    await expect(page.locator(".career-groups")).toBeVisible({ timeout: 30000 });

    // Layer A: the three lifted presentations, read from the top level.
    const layerA = page.getByLabel("命局基础");
    await expect(layerA).toContainText("命盘结构分析");
    await expect(layerA).toContainText("调候与病药");
    await expect(layerA).toContainText("统一裁决：弃判");
    await expect(layerA).toContainText("任氏寅月局部真格研究结果");

    // Layer B: no bazi-profile call yet — the timeline is lazy.
    expect(calls.filter((call) => call.scenario === "bazi-profile")).toEqual([]);
    // Once the timeline opens, a second element carries the same
    // label (the current-period div inside DayunTimeline), so
    // getByLabel resolves to two elements. The Layer B section is
    // the only region with that name.
    const layerB = page.getByRole("region", { name: "当前大运" });
    await expect(layerB).toContainText("查看完整 8 运时间线");
    await layerB.getByRole("button", { name: "查看完整 8 运时间线" }).click();
    await expect(page.locator(".slice-dayun-entries li")).toHaveCount(8, { timeout: 30000 });
    expect(calls).toContainEqual({ scenario: "bazi-profile", year: undefined, role: "male" });
    await expect(layerB).toContainText("当前大运");
    const bodyText = await page.locator("body").textContent();
    expect(bodyText).not.toMatch(/起运\s*\d+\s*岁|\d+\s*岁起运/);

    // Layer C: annual branch structure from the career envelope.
    const layerC = page.getByLabel("指定流年");
    await expect(layerC).toContainText("流年地支 午");
    await expect(layerC).toContainText("已核对 4 组地支");
    // "年度十神与原局综合解读" is the section's aria-label, not
    // visible text, so toContainText can never match it. Assert the
    // section itself plus its visible headline instead (the real
    // backend renders "2026年食神 · 食伤视角" for this sample).
    await expect(page.locator("section.career-annual-reading")).toBeVisible();
    await expect(layerC).toContainText("2026年食神 · 食伤视角");

    // Year stepper re-requests immediately and updates all layers.
    await layerC.getByRole("button", { name: "2027 年 →" }).click();
    await expect(page.locator(".career-groups")).toBeVisible({ timeout: 30000 });
    expect(calls).toContainEqual({ scenario: "career", year: 2027, role: "male" });
    await expect(page.getByLabel("指定流年")).toContainText("2027 年");
  });

  test("life five screens: presentations, lazy dayun, deep links keep birth data and year", async ({ page }) => {
    const calls = await collectScenarioRequests(page);
    await page.goto("/life-overview");
    await page.getByRole("button", { name: "填入示例" }).click();
    await page.getByLabel("观察年份").fill("2026");
    await page.locator("#life-dayun-role").selectOption("female");
    await page.getByRole("button", { name: "生成我的人生总览" }).click();
    await expect(page.locator(".life-highlights")).toBeVisible({ timeout: 30000 });

    const nav = page.getByLabel("总览分屏");
    await expect(nav).toBeVisible();
    for (const label of ["① 命盘概况", "② 旺衰与喜用", "③ 大运流年", "④ 事业财运", "⑤ 桃花姻缘"]) {
      await expect(nav.getByRole("tab", { name: label })).toBeVisible();
    }

    // Screen 1: pillars + stem elements, no invented wealth/marriage text.
    await expect(page.getByLabel("命盘概况")).toContainText("天干五行分布与阴阳");
    await expect(page.getByLabel("命盘概况")).toContainText("本次计算所用出生资料：2000-01-07 12:00");

    // Screen 2: the three lifted presentations; unified verdict abstains.
    await nav.getByRole("tab", { name: "② 旺衰与喜用" }).click();
    const strength = page.getByLabel("旺衰与喜用");
    await expect(strength).toContainText("命盘结构分析");
    await expect(strength).toContainText("统一裁决：弃判");
    await expect(strength).toContainText("任氏寅月局部真格研究结果");

    // Screen 3: lazy full timeline + flow-year detail entry.
    await nav.getByRole("tab", { name: "③ 大运流年" }).click();
    const dayunScreen = page.getByLabel("大运流年");
    await dayunScreen.getByRole("button", { name: "查看完整 8 运时间线" }).click();
    await expect(page.locator(".slice-dayun-entries li")).toHaveCount(8, { timeout: 30000 });
    expect(calls).toContainEqual({ scenario: "bazi-profile", year: undefined, role: "female" });
    await expect(dayunScreen).toContainText("当前大运");
    await expect(dayunScreen).toContainText("流年结构");

    // Screen 4: career strip + deep link keeps birth data and year.
    await nav.getByRole("tab", { name: "④ 事业财运" }).click();
    const careerScreen = page.getByLabel("事业财运");
    await expect(careerScreen).toContainText("财星");
    await careerScreen.getByRole("link", { name: "查看详情" }).click();
    await expect(page).toHaveURL(/\/career-wealth-structure/);
    await expect(page.getByLabel("出生日期")).toHaveValue("2000-01-07");
    await expect(page.getByLabel("出生时间")).toHaveValue("12:00");
    await expect(page.getByLabel("观察年份")).toHaveValue("2026");

    // Back on the overview: mount reads the shared year key.
    await page.goto("/life-overview");
    await expect(page.getByLabel("观察年份")).toHaveValue("2026");
    await page.getByRole("button", { name: "填入示例" }).click();
    await page.getByLabel("观察年份").fill("2026");
    await page.locator("#life-dayun-role").selectOption("female");
    await page.getByRole("button", { name: "生成我的人生总览" }).click();
    await expect(page.locator(".life-highlights")).toBeVisible({ timeout: 30000 });

    // Screen 5: xianchi + spouse palace facts; no spouse-star pairing.
    await nav.getByRole("tab", { name: "⑤ 桃花姻缘" }).click();
    const romanceScreen = page.getByLabel("桃花姻缘");
    await expect(romanceScreen).toContainText("夫妻宫");
    await expect(romanceScreen).toContainText("总览内不呈现配偶星配对");
    await expect(romanceScreen.getByRole("link", { name: "缘分合盘" })).toBeVisible();

    // Year stepper on the overview re-requests and syncs every screen.
    await page.getByRole("button", { name: "2027 年 →" }).click();
    // .life-highlights only renders on screen ①; the stepper leaves
    // the active screen at ⑤, so switch back before waiting for it.
    await nav.getByRole("tab", { name: "① 命盘概况" }).click();
    await expect(page.locator(".life-highlights")).toBeVisible({ timeout: 30000 });
    expect(calls).toContainEqual({ scenario: "life", year: 2027, role: "female" });
    await expect(page.getByLabel("命盘概况")).toContainText("2027");
  });
});
