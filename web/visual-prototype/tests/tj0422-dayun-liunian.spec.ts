/**
 * TJ-0422 phase 2 slice A (E0422): dayun timeline + yearly linkage.
 *
 * 诚实标注：本专项是 **stub 契约测试**，不是真实后端计算。
 * - 八字响应复用 tj0173 的录制 fixture（2026-11-02 从组装后的真实
 *   后端录制的 Q1 盘 1958-08-15T19:30+08:00、传统男命口径），经
 *   page.route 回放；只验证页面渲染、时间线交互与跨页联动。
 * - 流年响应是按后端 _yearly 契约手工构造的 stub（target_year /
 *   natal / annual_branch_interactions / release_scope
 *   annual_structure_only；干支与十神按 Q1 盘日主甲手工填入，
 *   2026 丙午·食神·午子冲、2027 丁未·伤官·子未害、2028 戊申·
 *   偏财·无命中），只验证年份切换重新请求与定位渲染，不冒称
 *   真实后端计算。
 * - 真实端到端行为（真实后端大运呈现 + 流年结构）由本文件末尾
 *   明确跳过的测试钉住，待可信机环境复验；本地无后端
 *   （127.0.0.1:8000 无服务），不得把本专项的通过说成真实
 *   后端已验证。
 */
import { readFileSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { expect, test, type Page } from "@playwright/test";

const here = path.dirname(fileURLToPath(import.meta.url));
const domainFixture = JSON.parse(
  readFileSync(path.join(here, "fixtures", "tj0173-q1-domain.json"), "utf-8"),
);
const scenarioFixture = JSON.parse(
  readFileSync(path.join(here, "fixtures", "tj0173-q1-scenario.json"), "utf-8"),
);

const YEARLY_STUB: Record<number, { ganzhi: string; stem: string; branch: string; tenGod: string; hits: Array<Record<string, unknown>> }> = {
  2026: {
    ganzhi: "丙午", stem: "丙", branch: "午", tenGod: "食神",
    hits: [{
      relation_type: "clash", rule_id: "bazi.phase2.branch_six_clashes",
      flow_branch: "午", natal_pillar: "day", natal_branch: "子",
      branches: ["午", "子"], evidence_ids: [],
    }],
  },
  2027: {
    ganzhi: "丁未", stem: "丁", branch: "未", tenGod: "伤官",
    hits: [{
      relation_type: "harm", rule_id: "bazi.phase2.branch_six_harms",
      flow_branch: "未", natal_pillar: "day", natal_branch: "子",
      branches: ["未", "子"], evidence_ids: [],
    }],
  },
  2028: {
    ganzhi: "戊申", stem: "戊", branch: "申", tenGod: "偏财", hits: [],
  },
};

function yearlyStub(year: number) {
  const stub = YEARLY_STUB[year];
  if (!stub) throw new Error(`no yearly stub for ${year}`);
  const counts = {
    six_harmony: stub.hits.filter((h) => h.relation_type === "six_harmony").length,
    harm: stub.hits.filter((h) => h.relation_type === "harm").length,
    clash: stub.hits.filter((h) => h.relation_type === "clash").length,
  };
  return {
    scenario_id: "yearly",
    status: "production_limited",
    public_release: false,
    deterministic: true,
    result: {
      natal: {
        pillars: domainFixture.chart.pillars,
        day_master: domainFixture.chart.day_master,
      },
      target_year: {
        year,
        ganzhi: stub.ganzhi,
        stem: stub.stem,
        branch: stub.branch,
        stem_ten_god: stub.tenGod,
        calendar_provider: "stub",
        year_boundary: "solar-term year; reference date fixed to July 1 for stable annual stem/branch selection",
      },
      annual_branch_interactions: {
        flow_branch: stub.branch,
        natal_branches_checked: domainFixture.chart.pillars.map((p: any) => ({ pillar: p.name, branch: p.branch.value })),
        hits: stub.hits,
        counts,
        evaluated_pairs: 4,
        rule_ids: ["bazi.phase2.branch_six_harmonies", "bazi.phase2.branch_six_harms", "bazi.phase2.branch_six_clashes"],
        evidence_ids: [],
        interpretation_allowed: false,
        policy: "Only reviewed 六冲/六合/六害 fixed pair structures. No 破/刑/三合, effects, luck, or events.",
      },
      release_scope: "annual_structure_only",
    },
    rule_matches: [
      {
        rule_id: "bazi.scenario.flow_stem_ten_god",
        derived_from_rule_id: "bazi.phase2.ten_gods",
        variant: "ziping-structural-v1",
        matched: true,
        kind: "scenario_composition",
        evidence_scope: "stub",
        facts: { day_master: "甲", flow_year_stem: stub.stem, flow_year_stem_ten_god: stub.tenGod },
        evidence_ids: [],
      },
      {
        rule_id: "bazi.scenario.annual_branch_relations",
        derived_from_rule_ids: ["bazi.phase2.branch_six_harmonies", "bazi.phase2.branch_six_harms", "bazi.phase2.branch_six_clashes"],
        variant: "ziping-structural-v1",
        matched: true,
        kind: "scenario_composition",
        evidence_scope: "仅复用已验证六合、六害、六冲规则的地支成对结构，不推断作用强弱和吉凶。",
        facts: { flow_branch: stub.branch, hits: stub.hits, counts, evaluated_pairs: 4 },
        evidence_ids: [],
      },
    ],
    trace: [
      { step: "natal_bazi", facts: { day_master: domainFixture.chart.day_master } },
      { step: "target_year_calendar", facts: { year_ganzhi: stub.ganzhi } },
      { step: "flow_stem_ten_god", facts: { day_master: "甲", flow_year_stem: stub.stem, flow_year_stem_ten_god: stub.tenGod }, evidence_ids: [] },
    ],
    evidence: {},
    warnings: [],
    limitations: ["流年结构只呈现已审核的干支与冲合害关系，不作吉凶判断。"],
  };
}

async function stubBaziAndYearly(page: Page, captured: { scenarioInputs: any[]; yearlyYears: number[] }) {
  await page.route("**/api/v1/public/execute", async (route) => {
    await route.fulfill({ status: 200, json: domainFixture });
  });
  await page.route("**/api/v1/scenarios/public", async (route) => {
    const body = route.request().postDataJSON() as any;
    captured.scenarioInputs.push(body);
    if (body?.scenario_id === "yearly") {
      captured.yearlyYears.push(body.input.target_year);
      await route.fulfill({ status: 200, json: yearlyStub(body.input.target_year) });
      return;
    }
    await route.fulfill({ status: 200, json: scenarioFixture });
  });
}

async function stubYearlyOnly(page: Page, captured: { yearlyYears: number[] }) {
  await page.route("**/api/v1/scenarios/public", async (route) => {
    const body = route.request().postDataJSON() as any;
    captured.yearlyYears.push(body.input.target_year);
    await route.fulfill({ status: 200, json: yearlyStub(body.input.target_year) });
  });
}

async function fillQ1(page: Page) {
  await page.goto("/bazi-profile");
  const selects = page.locator("form.bazi-input-card select");
  await selects.nth(0).selectOption("1958");
  await selects.nth(1).selectOption("8");
  await selects.nth(2).selectOption("15");
  await selects.nth(3).selectOption("19");
  await selects.nth(4).selectOption("30");
}

async function submitQ1WithRole(page: Page) {
  await fillQ1(page);
  await page.locator("#bazi-dayun-role").selectOption("male");
  await page.getByRole("button", { name: "生成基础档案" }).click();
  await expect(page.locator(".bazi-live-result")).toBeVisible();
  await expect(page.locator(".bazi-dayun-presentation")).toBeVisible();
}

test("dayun timeline renders 8 periods, current period highlighted, detail panel shows interval facts", async ({ page }) => {
  const captured: { scenarioInputs: any[]; yearlyYears: number[] } = { scenarioInputs: [], yearlyYears: [] };
  await stubBaziAndYearly(page, captured);
  await submitQ1WithRole(page);

  // Texts carried over verbatim from the previous static rendering.
  const section = page.locator(".bazi-dayun-presentation");
  await expect(section).toContainText("大运方向：顺行");
  await expect(section).toContainText("白露");
  await expect(section).toContainText("2840–2850 日");
  await expect(section).toContainText("第 1 运 辛酉");
  await expect(section).toContainText("1966-05-25T19:30:00+08:00");
  await expect(section).toContainText("三命时级与神峰日级为两套分立注册口径、并列呈现、永不合并");
  await expect(section).not.toContainText("吉凶");

  // Interactive timeline: 8 period buttons, not a static list.
  await expect(page.locator(".dayun-timeline button")).toHaveCount(8);
  // Fixture intervals pin period 7 (2026-05-25..06-04 → 2036) as current
  // for any run date from 2026-06-04 until 2036-05-25.
  await expect(page.locator('.dayun-timeline [data-period="7"]')).toContainText("当前");
  // Default detail is the current period (fixture: period 7 丁卯,
  // interval 2026-05-25..06-04, next period starts 2036).
  await expect(page.locator(".dayun-detail")).toContainText("第 7 运 丁卯");
  await expect(page.locator(".dayun-detail")).toContainText("丁（火）");
  await expect(page.locator(".dayun-detail")).toContainText("卯（木）");

  // Click period 1: detail shows backend fields only.
  await page.locator('.dayun-timeline [data-period="1"] button').click();
  const detail = page.locator(".dayun-detail");
  await expect(detail).toContainText("第 1 运 辛酉");
  await expect(detail).toContainText("辛（金）");
  await expect(detail).toContainText("酉（金）");
  await expect(detail).toContainText("相对日主 甲 为正官");
  await expect(detail).toContainText("1966-05-25T19:30:00+08:00 至 1966-06-04T19:30:00+08:00");
  await expect(detail).toContainText("约在下一运交运区间之前结束");
  await expect(detail).not.toContainText("吉凶");

  // Last period honestly has no end.
  await page.locator('.dayun-timeline [data-period="8"] button').click();
  await expect(detail).toContainText("第 8 运 戊辰");
  await expect(detail).toContainText("末段无终点：未提供");
  await expect(detail).toContainText("2036 年");
});

test("shenfeng method: later periods honestly not provided, current period unknown", async ({ page }) => {
  const captured: { scenarioInputs: any[]; yearlyYears: number[] } = { scenarioInputs: [], yearlyYears: [] };
  await stubBaziAndYearly(page, captured);
  await submitQ1WithRole(page);

  await page.locator(".bazi-dayun-presentation").getByRole("tab", { name: "神峰通考口径" }).click();
  await expect(page.locator('.dayun-timeline [data-period="2"]')).toContainText("交运区间未提供");
  await expect(page.locator(".dayun-timeline .dayun-current-badge")).toHaveCount(0);
  await page.locator('.dayun-timeline [data-period="2"] button').click();
  const detail = page.locator(".dayun-detail");
  await expect(detail).toContainText("第 2 运 壬戌");
  await expect(detail).toContainText("交运区间未提供：本口径只呈现首运交运区间。");
  await expect(detail).toContainText("下一运交运区间未提供，本运终点未提供。");
  await expect(page.locator(".dayun-year-links")).toHaveCount(0);
});

test("timeline year link opens yearly page for that year, locates it in its dayun, and returns", async ({ page }) => {
  const captured: { scenarioInputs: any[]; yearlyYears: number[] } = { scenarioInputs: [], yearlyYears: [] };
  await stubBaziAndYearly(page, captured);
  await submitQ1WithRole(page);

  await page.locator('.dayun-timeline [data-period="7"] button').click();
  await page.locator(".dayun-year-links a", { hasText: "2027 年" }).click();
  await expect(page).toHaveURL(/\/yearly-structure$/);
  await expect(page.getByLabel("目标年份")).toHaveValue("2027");
  // The yearly page auto-loads the linked year (one-shot request).
  await expect(page.locator(".yearly-result")).toBeVisible();
  await expect(page.locator(".yearly-result")).toContainText("丁未");
  await expect(page.locator(".yearly-result")).toContainText("丁（火）");
  await expect(page.locator(".yearly-result")).toContainText("未（土）");
  await expect(captured.yearlyYears).toContain(2027);
  const location = page.locator(".yearly-dayun-location");
  await expect(location).toContainText("2027 年 · 第 7 运 丁卯");
  await expect(location).toContainText("相对日主伤官");

  // 2026 overlaps period 7's start interval: ambiguous, never forced.
  await page.getByRole("button", { name: "上一年" }).click();
  await expect(page.locator(".yearly-result")).toContainText("丙午");
  await expect(location).toContainText("交运年，所属大运不唯一");
  await expect(location).toContainText("可能处于交运前后");

  // Back to the bazi timeline, period 7 selected.
  await page.locator(".yearly-dayun-location").getByRole("link", { name: "查看第 7 运" }).click();
  await expect(page).toHaveURL(/\/bazi-profile$/);
  await expect(page.locator(".bazi-dayun-presentation")).toBeVisible();
  await expect(page.locator(".bazi-dayun-presentation")).toContainText("本次会话中保存的大运呈现");
  await expect(page.locator('.dayun-timeline [data-period="7"] button')).toHaveAttribute("aria-pressed", "true");
  await expect(page.locator(".dayun-detail")).toContainText("第 7 运 丁卯");
});

test("yearly page without a dayun presentation shows the entry, makes no API call, and fabricates nothing", async ({ page }) => {
  const calls: string[] = [];
  page.on("request", (request) => {
    if (new URL(request.url()).pathname.startsWith("/api/")) calls.push(request.url());
  });
  await page.goto("/yearly-structure");
  const location = page.locator(".yearly-dayun-location");
  await expect(location).toContainText("尚未查看大运");
  await expect(location).toContainText("先在八字命理页选择传统大运口径查看完整大运");
  await expect(location.getByRole("link", { name: "先在八字命理页选择传统大运口径查看完整大运" })).toHaveAttribute("href", "/bazi-profile");
  expect(calls).toEqual([]);
});

test("year stepping re-requests the scenario and keeps the birth inputs", async ({ page }) => {
  const captured: { yearlyYears: number[] } = { yearlyYears: [] };
  await stubYearlyOnly(page, captured);
  await page.goto("/yearly-structure");
  await page.getByRole("button", { name: "填入示例" }).click();
  await page.getByLabel("目标年份").fill("2027");
  await page.getByRole("button", { name: "查看 2027 流年结构" }).click();
  await expect(page.locator(".yearly-result")).toBeVisible();
  await expect(page.locator(".yearly-result")).toContainText("丁未");
  await expect(page.locator(".yearly-branch-summary")).toContainText("共命中 1 条");

  await page.getByRole("button", { name: "下一年" }).click();
  await expect(page.locator(".yearly-result")).toContainText("戊申");
  await expect(page.getByLabel("出生日期")).toHaveValue("2000-01-07");
  await expect(page.getByLabel("出生时间")).toHaveValue("12:00");

  await page.getByRole("button", { name: "上一年" }).click();
  await expect(page.locator(".yearly-result")).toContainText("丁未");
  await page.getByRole("button", { name: "上一年" }).click();
  await expect(page.locator(".yearly-result")).toContainText("丙午");
  await expect(page.getByLabel("目标年份")).toHaveValue("2026");
  expect(captured.yearlyYears).toEqual([2027, 2028, 2027, 2026]);
  await expect.poll(() => page.evaluate(() =>
    localStorage.getItem("tianji.scenario.target-year.v1"))).toBe("2026");
});

test("blank year shows a friendly error and makes no API call", async ({ page }) => {
  const calls: string[] = [];
  page.on("request", (request) => {
    if (new URL(request.url()).pathname.startsWith("/api/")) calls.push(request.url());
  });
  await stubYearlyOnly(page, { yearlyYears: [] });
  await page.goto("/yearly-structure");
  await page.getByRole("button", { name: "填入示例" }).click();
  await page.getByLabel("目标年份").fill("");
  await page.getByRole("button", { name: /查看 .* 流年结构/ }).click();
  await expect(page.locator(".question-error")).toContainText("请选择 1901 至 2098 年的公历年份");
  expect(calls).toEqual([]);
});

test("real backend: bazi timeline + yearly location (trusted-machine re-verification)", async ({ page }) => {
  test.skip(true, "本地无密封运行时/后端（127.0.0.1:8000 无服务）：以下真实后端断言待可信机环境复验，不得以本文件其他测试的通过代替。");
  await fillQ1(page);
  await page.locator("#bazi-dayun-role").selectOption("male");
  await page.getByRole("button", { name: "生成基础档案" }).click();
  await expect(page.locator(".dayun-timeline button")).toHaveCount(8);
  await page.locator(".dayun-year-links a", { hasText: "2027 年" }).click();
  await expect(page.locator(".yearly-result")).toBeVisible();
  await expect(page.locator(".yearly-dayun-location")).toContainText("第 7 运 丁卯");
});
