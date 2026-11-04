/**
 * TJ-013.3 U1 Batch C：八字页命盘结构分析呈现节浏览器专项。
 *
 * 性质如实标注：这是 **stub 契约测试** —— 四盘的两路 API 响应是
 * 2026-11-03 从已部署 Batch B 的生产后端（Merge SHA 1dc0ee03）
 * 经真实 API 录制的真实响应（1966-07-06T12:00 呈现强、1978-09-20
 * 呈现弱、2007-06-11 未命中、1981-12-21T22:30 冲突），经 page.route
 * 回放；本专项只验证页面渲染、文案与多态区分，不冒称真实后端
 * 计算。真实端到端行为另由生产只读探针与真实浏览器联调验证，
 * 并由离线验收中的密封 Python 专项钉住后端事实。
 *
 * 例外如实标注：大运一例不是录制响应——四盘录制时均未选传统
 * 口径，故无 dayun_presentation；该例在强盘场景上内联注入一个
 * 仅满足页面既有渲染字段的形状夹具（引文与提示均明标“形状夹具”，
 * 不是古籍原文），只验证大运既有渲染代码未被本次改版删改，不
 * 证明任何后端大运事实。
 *
 * 错误态一例不伪造 500 响应：只 abort 场景请求（domain 夹具照常
 * 200），复刻 live-error-partial 的正确变体——domain 成功 +
 * 场景失败才进入强度错误态；双路皆死时页面只有全局错误、根本
 * 没有结果区，该变体按设计不可达。
 *
 * 文案铁律：not_judgeable 在一切用户文案中都是无确定结论，永不
 * 写成弱或倾向性暗示；系统错误（场景调用失败）必须显示错误态，
 * 不得以空结果或“暂不可判”掩盖。
 */
import { readFileSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { expect, test, type Page } from "@playwright/test";

const here = path.dirname(fileURLToPath(import.meta.url));

function loadFixture(name: string) {
  return JSON.parse(
    readFileSync(path.join(here, "fixtures", name), "utf-8"),
  );
}

const CASES = {
  strong: {
    domain: loadFixture("tj0133-strength-presented-strong-domain.json"),
    scenario: loadFixture("tj0133-strength-presented-strong-scenario.json"),
    year: "1966", month: "7", day: "6", hour: "12", minute: "0",
  },
  weak: {
    domain: loadFixture("tj0133-strength-presented-weak-domain.json"),
    scenario: loadFixture("tj0133-strength-presented-weak-scenario.json"),
    year: "1978", month: "9", day: "20", hour: "10", minute: "0",
  },
  notJudgeable: {
    domain: loadFixture("tj0133-strength-not-judgeable-domain.json"),
    scenario: loadFixture("tj0133-strength-not-judgeable-scenario.json"),
    year: "2007", month: "6", day: "11", hour: "12", minute: "0",
  },
  conflict: {
    domain: loadFixture("tj0133-strength-conflict-domain.json"),
    scenario: loadFixture("tj0133-strength-conflict-scenario.json"),
    year: "1981", month: "12", day: "21", hour: "22", minute: "30",
  },
};

async function stubApis(page: Page, domainBody: unknown, scenarioBody: unknown) {
  await page.route("**/api/v1/public/execute", async (route) => {
    await route.fulfill({ status: 200, json: domainBody });
  });
  await page.route("**/api/v1/scenarios/public", async (route) => {
    await route.fulfill({ status: 200, json: scenarioBody });
  });
}

async function submitCase(page: Page, c: (typeof CASES)["strong"]) {
  await page.goto("/bazi-profile");
  const selects = page.locator("form.bazi-input-card select");
  await selects.nth(0).selectOption(c.year);
  await selects.nth(1).selectOption(c.month);
  await selects.nth(2).selectOption(c.day);
  await selects.nth(3).selectOption(c.hour);
  await selects.nth(4).selectOption(c.minute);
  await page.getByRole("button", { name: "生成基础档案" }).click();
  await expect(page.locator(".bazi-live-result")).toBeVisible();
}

async function submitCaseWithDayun(page: Page, c: (typeof CASES)["strong"]) {
  await page.goto("/bazi-profile");
  const selects = page.locator("form.bazi-input-card select");
  await selects.nth(0).selectOption(c.year);
  await selects.nth(1).selectOption(c.month);
  await selects.nth(2).selectOption(c.day);
  await selects.nth(3).selectOption(c.hour);
  await selects.nth(4).selectOption(c.minute);
  await page.locator("#bazi-dayun-role").selectOption("male");
  await page.getByRole("button", { name: "生成基础档案" }).click();
  await expect(page.locator(".bazi-live-result")).toBeVisible();
}

/** 形状夹具：只覆盖页面既有大运渲染字段，不含任何真实后端事实。 */
function dayunScenario() {
  const s = JSON.parse(JSON.stringify(CASES.strong.scenario));
  const quote = (id: string) => ({ id, quote: "形状夹具引文（非古籍原文）" });
  s.result.dayun_presentation = {
    methods: {
      sanming: {
        method: "sanming",
        natal: { pillars: { year: "丙午", month: "甲午", day: "丙寅", hour: "甲午", day_master: "丙" } },
        direction: {
          label: "顺行",
          counting_target: "future_jie",
          counted_jie: { name: "小暑", at: "1966-07-07" },
          rule_quote: quote("shape-direction-sanming"),
        },
        status: "resolved",
        duration: {
          interval_days: { min_days: 10, max_days: 20 },
          counting: { whole_shichen_counted: 3 },
          decomposition: { whole_year_units: 0, remainder_shichen: 3, remainder_days: 1, remainder_months_of_30_days: null },
        },
        entries: [{
          period_index: 1, ganzhi: "乙未", ten_god_relative_to_natal_day_stem: "正印",
          state: "interval", start_interval: { earliest: "1976-01-01", latest: "1976-02-01" },
        }],
        notices: [{ code: "shape-note", text: "形状夹具提示：本条为渲染形状测试文本。" }],
        sources: [{ quotes: [quote("shape-source-sanming")] }],
      },
      shenfeng: {
        method: "shenfeng",
        natal: { pillars: { year: "丙午", month: "甲午", day: "丙寅", hour: "甲午", day_master: "丙" } },
        direction: {
          label: "顺行",
          counting_target: "future_jie",
          counted_jie: { name: "小暑", at: "1966-07-07" },
          rule_quote: quote("shape-direction-shenfeng"),
        },
        status: "resolved",
        duration: {
          interval_days: { min_days: 10, max_days: 20 },
          counting: { whole_days: 5 },
          text_result_days: 6,
          granularity_note: "形状夹具粒度说明。",
        },
        entries: [{
          period_index: 1, ganzhi: "乙未", ten_god_relative_to_natal_day_stem: "正印",
          state: "not_provided",
        }],
        notices: [],
        sources: [{ quotes: [quote("shape-source-shenfeng")] }],
      },
    },
    scope: ["形状夹具范围行：大运只呈现已注册的方向与交运区间。"],
    limitations: ["形状夹具限制行：交运区间外不作推断。"],
  };
  return s;
}

// 以下两常量是默认视图实际渲染的转述后文案：后端 scope/limitations
// 原文仍含“充分谓词”等工程措辞，前端在渲染时就地转述为通俗中文，
// 后端文本本身未改；转述映射见 BaziProfilePage.tsx 的 plainUserText。
const SCOPE_STATEMENT =
  "本呈现仅陈述已审局部形态条件的命中事实；不是全盘旺衰判断，不意味着喜用神或吉凶；未命中不等于弱。";
const LIMITATIONS = [
  "仅限已审的八个局部形态条件类型；其余命盘形态暂不可判。",
  "金×酉这一类已通过审核但在真实历法命盘上构造性不可满足，不声称正例。",
];

async function directChildSectionLabels(page: Page): Promise<(string | null)[]> {
  return page.evaluate(() => [...document.querySelectorAll(".bazi-live-result > section")]
    .map((el) => el.getAttribute("aria-label")));
}

test("presented strong renders the retitled structure section in reading order", async ({ page }) => {
  const c = CASES.strong;
  await stubApis(page, c.domain, c.scenario);
  await submitCase(page, c);

  const section = page.locator(".bazi-strength-presentation");
  await expect(section).toBeVisible();
  await expect(section).toHaveAttribute("aria-label", "命盘结构分析");
  await expect(section).toContainText("命盘结构分析");
  await expect(section).not.toContainText("已审强弱形态事实");
  await expect(section).toContainText("日主丙生于午月，命中了一个已审的局部形态：司令显现支持形态。");
  await expect(section).toContainText("就本盘而言，这表示丙日主在午月满足了一项已审的支持条件——仅此而已，不再推出其他结论。");
  await expect(section).toContainText("限定形态：强形态");
  await expect(section).toContainText("规则来源：已通过审核的局部形态条件");
  // 证据条数已从默认视图彻底移除：按钮只写“查看判断依据”，
  // 来源说明只写“已核验”，不带任何条数。
  await expect(section.locator(".bazi-evidence-entry > summary")).toContainText("查看判断依据");
  await expect(section).not.toContainText("证据条目");
  await expect(section).not.toContainText("证据记录数量");
  await expect(section).toContainText("来源说明：同请求执行记录已核验。");
  await expect(section).toContainText("该结论只覆盖这一个已审形态，不覆盖全盘。");
  await expect(section).toContainText(SCOPE_STATEMENT);
  for (const line of LIMITATIONS) {
    await expect(section).toContainText(line);
  }
  // 技术字段与确定性误读一律不得出现在默认视图的本节。
  await expect(section).not.toContainText("身旺");
  await expect(section).not.toContainText("身弱");
  await expect(section).not.toContainText("bazi.rule");
  await expect(section).not.toContainText("bazi.phase2");
  await expect(section).not.toContainText("喜用神为");

  // 默认阅读顺序：概览 → 结构 → 旺衰因素（默认折叠的扩展知识区，
  // 仍为直接子节） → 调候病药 → 边界 → 审计。
  expect(await directChildSectionLabels(page)).toEqual([
    "命盘概览",
    "命盘结构分析",
    "旺衰因素与通根候选",
    "调候与病药取用依据",
    "当前分析边界",
    "专业审计视图",
  ]);

  // 调候/病药区块仍在场且结构不变；未选传统口径时大运区块缺席。
  await expect(page.locator(".bazi-xiyong-presentation")).toBeVisible();
  await expect(page.locator(".bazi-xiyong-presentation")).toContainText("调候");
  await expect(page.locator(".bazi-xiyong-presentation")).toContainText("病药");
  await expect(page.locator(".bazi-dayun-presentation")).toHaveCount(0);

  // 第 4 层：范围说明并入当前分析边界区。
  await expect(page.locator(".result-limitations")).toContainText(SCOPE_STATEMENT);
  await expect(page.locator(".result-limitations")).toContainText("命盘结构：已有结论的仅限这一个已审形态；其余命盘形态暂不可判。");
});

test("presented weak renders the weak form without ever writing 身弱", async ({ page }) => {
  const c = CASES.weak;
  await stubApis(page, c.domain, c.scenario);
  await submitCase(page, c);

  const section = page.locator(".bazi-strength-presentation");
  await expect(section).toBeVisible();
  await expect(section).toHaveAttribute("aria-label", "命盘结构分析");
  await expect(section).toContainText("日主乙生于酉月，命中了一个已审的局部形态：孤立受制形态。");
  await expect(section).toContainText("限定形态：弱形态");
  await expect(section).not.toContainText("身弱");
  await expect(section).not.toContainText("身旺");
  await expect(section).toContainText(SCOPE_STATEMENT);
});

test("not_judgeable shows 暂不可判 and no classification or lean", async ({ page }) => {
  const c = CASES.notJudgeable;
  await stubApis(page, c.domain, c.scenario);
  await submitCase(page, c);

  const section = page.locator(".bazi-strength-presentation");
  await expect(section).toBeVisible();
  await expect(section).toHaveAttribute("aria-label", "命盘结构分析·暂不可判");
  await expect(section).toContainText("暂不可判");
  await expect(section).toContainText("本盘未命中任何已审局部形态条件；未命中不等于弱。");
  await expect(section).toContainText("暂不可判，不作任何强弱结论。");
  await expect(section).not.toContainText("限定形态");
  await expect(section).not.toContainText("身弱");
  await expect(section).not.toContainText("身旺");
  await expect(section).toContainText(SCOPE_STATEMENT);
  await expect(page.locator(".result-limitations")).toContainText("命盘结构：暂不可判，不作任何强弱结论。");
});

test("conflict shows an undecided conflict and no classification", async ({ page }) => {
  const c = CASES.conflict;
  await stubApis(page, c.domain, c.scenario);
  await submitCase(page, c);

  const section = page.locator(".bazi-strength-presentation");
  await expect(section).toBeVisible();
  await expect(section).toHaveAttribute("aria-label", "命盘结构分析·未裁定冲突");
  await expect(section).toContainText("本盘存在未裁定的冲突，暂不可判；不作任何强弱结论。");
  await expect(section).not.toContainText("限定形态");
  await expect(section).not.toContainText("身弱");
  await expect(section).not.toContainText("身旺");
  // 冲突 id 与阻断原因码是技术字段，不得渲染。
  await expect(section).not.toContainText("sanming-juan2");
  await expect(section).not.toContainText("root_type_source_conflict");
  await expect(section).toContainText(SCOPE_STATEMENT);
  await expect(page.locator(".result-limitations")).toContainText("命盘结构：存在未裁定冲突，暂不可判；不作任何强弱结论。");
});

test("section is absent when the scenario response carries no strength key", async ({ page }) => {
  const without = JSON.parse(JSON.stringify(CASES.strong.scenario));
  delete without.result.strength_presentation;
  await stubApis(page, CASES.strong.domain, without);
  await submitCase(page, CASES.strong);
  await expect(page.locator(".bazi-pillars article")).toHaveCount(4);
  await expect(page.locator(".bazi-strength-presentation")).toHaveCount(0);
  await expect(page.locator(".bazi-xiyong-presentation")).toBeVisible();
  await expect(page.locator(".result-limitations")).toContainText("命盘结构：本次结果未附带已审强弱形态事实。");
});

test("scenario-only failure shows an error state distinct from 暂不可判", async ({ page }) => {
  // 只 abort 场景请求；domain 夹具照常 200（正确变体）。
  await page.route("**/api/v1/public/execute", async (route) => {
    await route.fulfill({ status: 200, json: CASES.strong.domain });
  });
  await page.route("**/api/v1/scenarios/public", (route) => route.abort());
  await submitCase(page, CASES.strong);

  // Domain 成功：结果区在场，且无全局错误。
  await expect(page.locator(".bazi-live-result")).toBeVisible();
  await expect(page.locator(".question-error")).toHaveCount(0);
  const errorSection = page.locator(
    '.bazi-strength-presentation[aria-label="命盘结构分析·加载失败"]',
  );
  await expect(errorSection).toBeVisible();
  await expect(errorSection).toContainText("强弱形态事实加载失败，请稍后重试。");
  await expect(errorSection).toContainText("这不是暂不可判：本次请求未能完成计算。");
  // 未命中与冲突两种正常拒判节一律不得出现。
  await expect(
    page.locator('.bazi-strength-presentation[aria-label="命盘结构分析·暂不可判"]'),
  ).toHaveCount(0);
  await expect(
    page.locator('.bazi-strength-presentation[aria-label="命盘结构分析·未裁定冲突"]'),
  ).toHaveCount(0);
  // 场景失败时调候/病药缺席，边界区仍如实记录失败而非暂不可判。
  await expect(page.locator(".bazi-xiyong-presentation")).toHaveCount(0);
  await expect(page.locator(".result-limitations")).toContainText("命盘结构：本次请求未能完成计算，这不是暂不可判。");
});

test("default view contains no rule-id codes, trace fields or evidence dumps", async ({ page }) => {
  const c = CASES.strong;
  await stubApis(page, c.domain, c.scenario);
  await submitCase(page, c);

  // 审计视图默认折叠：DOM 在场但不可见。
  const auditOpen = await page.evaluate(
    () => (document.querySelector(".bazi-audit-details") as HTMLDetailsElement | null)?.open,
  );
  expect(auditOpen).toBe(false);
  await expect(page.locator(".bazi-audit-view .live-rule").first()).toBeHidden();
  await expect(page.locator(".bazi-audit-view .live-evidence").first()).toBeHidden();
  await expect(page.locator(".bazi-audit-view .bazi-trace").first()).toBeHidden();

  // 默认视图各节均无规则编号、技术字段与计算过程。注意：
  // toContainText 会读到折叠 details 内的文本，因此“默认视图无
  // 规则编号”只能按节断言——审计视图的 R01 在折叠时上面已用
  // toBeHidden 断言不可见，不能用整结果区的 toContainText 断言。
  for (const scope of [
    ".bazi-overview",
    ".bazi-strength-presentation",
    ".bazi-xiyong-presentation",
    ".result-limitations",
  ]) {
    const section = page.locator(scope);
    await expect(section).not.toContainText("bazi.rule");
    await expect(section).not.toContainText("bazi.phase2");
    await expect(section).not.toContainText("计算步骤");
    await expect(section).not.toContainText("R01");
  }
  // 规则编号只在审计视图展开后才可见（见下一例），默认视图无“规则命中”体。
  await expect(page.locator(".bazi-overview")).not.toContainText("规则命中");
});

test("audit view expands on demand and collapses again", async ({ page }) => {
  const c = CASES.strong;
  await stubApis(page, c.domain, c.scenario);
  await submitCase(page, c);

  const summary = page.locator(".bazi-audit-details > summary");
  await expect(summary).toContainText("专业审计视图");
  await summary.click();
  await expect(page.locator(".bazi-audit-view .live-rule").first()).toBeVisible();
  await expect(page.locator(".bazi-audit-view .live-rule").first()).toContainText("R01");
  await expect(page.locator(".bazi-audit-view .live-evidence").first()).toBeVisible();
  await summary.click();
  await expect(page.locator(".bazi-audit-view .live-rule").first()).toBeHidden();
  await expect(page.locator(".bazi-audit-view .live-evidence").first()).toBeHidden();
});

test("evidence entries expand and collapse per conclusion", async ({ page }) => {
  const c = CASES.strong;
  await stubApis(page, c.domain, c.scenario);
  await submitCase(page, c);

  // 结构节：展开见说明与适用边界，收起后不可见。
  const strengthEntry = page.locator(".bazi-strength-presentation .bazi-evidence-entry");
  const strengthNote = strengthEntry.locator("p", { hasText: "本呈现对象未附带原文引文文本" });
  await expect(strengthNote).toBeHidden();
  await strengthEntry.locator("summary").click();
  await expect(strengthNote).toBeVisible();
  await expect(strengthEntry).toContainText("适用边界：仅限已审的八个局部形态条件类型");
  await strengthEntry.locator("summary").click();
  await expect(strengthNote).toBeHidden();

  // 调候块：展开见《穷通宝鉴》引文，收起后不可见。
  const tiaohouEntry = page.locator(".bazi-xiyong-presentation .bazi-evidence-entry").first();
  const tiaohouQuote = tiaohouEntry.locator("blockquote", { hasText: "五月丙火愈炎" });
  await expect(tiaohouQuote).toBeHidden();
  await tiaohouEntry.locator("summary").click();
  await expect(tiaohouQuote).toBeVisible();
  await expect(tiaohouEntry).toContainText("来源：《穷通宝鉴》");
  await expect(tiaohouEntry).toContainText("适用边界：证据等级为 C 级");
  await tiaohouEntry.locator("summary").click();
  await expect(tiaohouQuote).toBeHidden();

  // 病药块：展开见《神峰通考》引文。
  const bingyaoEntry = page.locator(".bazi-xiyong-presentation .bazi-evidence-entry").nth(1);
  await bingyaoEntry.locator("summary").click();
  await expect(bingyaoEntry.locator("blockquote", { hasText: "如用财见比肩为病" })).toBeVisible();
  await bingyaoEntry.locator("summary").click();
  await expect(bingyaoEntry.locator("blockquote", { hasText: "如用财见比肩为病" })).toBeHidden();
});


test("final close-out: default view contains none of the banned engineering terms", async ({ page }) => {
  const c = CASES.strong;
  await stubApis(page, c.domain, c.scenario);
  await submitCase(page, c);

  // 默认视图各节（审计视图除外）一律不得出现工程术语与 Variant 名；
  // 审计视图折叠在内，默认视图断言按节进行（见既有例的说明）。
  const banned = [
    "充分谓词",
    "司令段门",
    "证据条目",
    "证据记录数量",
    "ziping-structural-v1",
    "strength-public-presentation-v1",
    "ditiansui-root-visibility-v1",
    "bazi-strength-adjudication-v1",
    "Variant",
  ];
  for (const scope of [
    ".bazi-overview",
    ".bazi-strength-presentation",
    ".bazi-xiyong-presentation",
    ".result-limitations",
  ]) {
    const section = page.locator(scope);
    for (const term of banned) {
      await expect(section).not.toContainText(term);
    }
  }
  // Variant 名只移到折叠的审计视图内：展开后可见，默认仍不可见。
  await expect(page.locator(".bazi-audit-view .live-rule").first()).toBeHidden();
  await page.locator(".bazi-audit-details > summary").click();
  await expect(page.locator(".bazi-audit-view")).toContainText("计算版本：ziping-structural-v1");
});

test("final close-out: pending registration and segment gate render in plain wording", async ({ page }) => {
  const scenario = JSON.parse(JSON.stringify(CASES.strong.scenario));
  scenario.result.strength_presentation.rule_registration = "pending";
  scenario.result.strength_presentation.segment_gate = { segment_stem: "甲" };
  await stubApis(page, CASES.strong.domain, scenario);
  await submitCase(page, CASES.strong);

  const section = page.locator(".bazi-strength-presentation");
  await expect(section).toContainText("规则来源：尚在审核登记中的局部形态条件");
  await expect(section).toContainText("出生时刻已对照本月已核验的时段核查通过：甲段。");
  await expect(section).not.toContainText("充分谓词");
  await expect(section).not.toContainText("司令段门");
  await expect(section).not.toContainText("待第一阶段规则注册");
});

test("final close-out: 旺衰因素 area is collapsed by default and expands on demand", async ({ page }) => {
  const c = CASES.strong;
  await stubApis(page, c.domain, c.scenario);
  await submitCase(page, c);

  const area = page.locator(".bazi-strength-observations .bazi-extended-details");
  const open = await page.evaluate(
    () => (document.querySelector(".bazi-extended-details") as HTMLDetailsElement | null)?.open,
  );
  expect(open).toBe(false);
  await expect(area.locator("p", { hasText: "月支" }).first()).toBeHidden();
  await area.locator("> summary").click();
  await expect(area.locator("p", { hasText: "月支" }).first()).toBeVisible();
  await expect(area).toContainText("通根候选");
  await expect(area).toContainText("尚不能据此判断身强身弱");
  await area.locator("> summary").click();
  await expect(area.locator("p", { hasText: "月支" }).first()).toBeHidden();
});

test("final close-out: boundary section has no duplicated lines", async ({ page }) => {
  const c = CASES.strong;
  await stubApis(page, c.domain, c.scenario);
  await submitCase(page, c);

  const boundary = page.locator(".result-limitations");
  const texts = await boundary.evaluate((el) =>
    [...el.querySelectorAll("p")].map((p) => (p.textContent || "").trim()).filter(Boolean),
  );
  expect(new Set(texts).size).toBe(texts.length);
  // 后端 limitations 自带的重复行（三刑行出现两次）只保留一次。
  const sanxing = texts.filter((t) => t.includes("三刑存在明确流派分歧"));
  expect(sanxing).toHaveLength(1);
  // 不同事实一律保留：domain 限制、调候范围、强度转述范围、固定分界约定都在场。
  await expect(boundary).toContainText("真太阳时未实现。");
  await expect(boundary).toContainText("本呈现只含调候");
  await expect(boundary).toContainText(SCOPE_STATEMENT);
  await expect(boundary).toContainText("分界约定：年柱以立春交节为界");
});

test("final close-out: 下一阶段 promo card is deleted", async ({ page }) => {
  const c = CASES.strong;
  await stubApis(page, c.domain, c.scenario);
  await submitCase(page, c);

  await expect(page.locator(".bazi-next-card")).toHaveCount(0);
  await expect(page.locator(".bazi-live-result")).not.toContainText("下一阶段");
  await expect(page.locator(".bazi-live-result")).not.toContainText("从基础档案走向");
});

test("dayun section still renders with unchanged content (shape fixture)", async ({ page }) => {
  await stubApis(page, CASES.strong.domain, dayunScenario());
  await submitCaseWithDayun(page, CASES.strong);

  const dayun = page.locator(".bazi-dayun-presentation");
  await expect(dayun).toBeVisible();
  await expect(dayun).toContainText("大运方向与交运区间，按哪种口径数？");
  await expect(dayun).toContainText("四柱 丙午 · 甲午 · 丙寅 · 甲午，日主 丙");
  await expect(dayun).toContainText("大运方向：顺行");
  await expect(dayun).toContainText("交运时长区间 10–20 日");
  await expect(dayun).toContainText("共数 3 个时辰");
  await expect(dayun).toContainText("第 1 运 乙未");
  await expect(dayun).toContainText("交运区间：1976-01-01 至 1976-02-01");
  await expect(dayun).toContainText("形状夹具范围行：大运只呈现已注册的方向与交运区间。");
  // 大运 limitations 按既有代码渲染在边界区（非大运节内），此处如实跟随既有位置。
  await expect(page.locator(".result-limitations")).toContainText("形状夹具限制行：交运区间外不作推断。");
  // 大运在阅读顺序中位于调候病药之后、边界之前。
  const labels = await directChildSectionLabels(page);
  expect(labels.indexOf("大运方向与交运区间")).toBeGreaterThan(labels.indexOf("调候与病药取用依据"));
  expect(labels.indexOf("大运方向与交运区间")).toBeLessThan(labels.indexOf("当前分析边界"));
  // 口径切换仍工作：神峰口径内容与判断依据展开。
  await dayun.getByRole("tab", { name: "神峰通考口径" }).click();
  await expect(dayun).toContainText("整日 5 日，原文折算 6 日。");
  await dayun.locator(".bazi-evidence-entry summary").click();
  await expect(dayun.locator(".bazi-evidence-entry blockquote").first()).toBeVisible();
  // 调候/病药原文行未被改写。
  await expect(page.locator(".bazi-xiyong-presentation")).toContainText("调候体系（《穷通宝鉴》丙火五月条）");
  await expect(page.locator(".bazi-xiyong-presentation")).toContainText("病药体系（《神峰通考》）");
});

for (const width of [390, 360, 768, 1440]) {
  test(`viewport ${width} renders structure content without horizontal overflow`, async ({ page }) => {
    await page.setViewportSize({ width, height: 844 });
    await stubApis(page, CASES.strong.domain, CASES.strong.scenario);
    await submitCase(page, CASES.strong);
    const section = page.locator(".bazi-strength-presentation");
    await expect(section).toBeVisible();
    await expect(section).toContainText("命盘结构分析");
    await expect(page.locator(".bazi-pillars article")).toHaveCount(4);
    const overflow = await page.evaluate(
      () => document.documentElement.scrollWidth - document.documentElement.clientWidth,
    );
    expect(overflow).toBeLessThanOrEqual(1);
  });
}

test("bottom nav does not occlude results and the page scrolls to the bottom", async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await stubApis(page, CASES.strong.domain, CASES.strong.scenario);
  await submitCase(page, CASES.strong);

  const audit = page.locator(".bazi-audit-view");
  await audit.scrollIntoViewIfNeeded();
  const boxes = await page.evaluate(() => {
    const a = document.querySelector(".bazi-audit-view")!.getBoundingClientRect();
    const nav = document.querySelector(".mobile-bottom-nav") as HTMLElement | null;
    const n = nav ? nav.getBoundingClientRect() : null;
    return { auditBottom: a.bottom, navTop: n ? n.top : null, navVisible: !!n && getComputedStyle(nav).display !== "none" };
  });
  // 移动端底栏可见时，审计视图底部必须在其上方，不被遮挡。
  expect(boxes.navVisible).toBe(true);
  expect(boxes.auditBottom).toBeLessThanOrEqual(boxes.navTop!);

  // 正常滚动到底：滚动位置到达文档底部附近，审计视图仍在视口内。
  await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight));
  const atBottom = await page.evaluate(
    () => window.scrollY + window.innerHeight >= document.body.scrollHeight - 2,
  );
  expect(atBottom).toBe(true);
  await expect(audit).toBeInViewport();
});

test("desktop viewport keeps the audit view reachable by scrolling", async ({ page }) => {
  await page.setViewportSize({ width: 1440, height: 900 });
  await stubApis(page, CASES.strong.domain, CASES.strong.scenario);
  await submitCase(page, CASES.strong);
  const audit = page.locator(".bazi-audit-view");
  await audit.scrollIntoViewIfNeeded();
  await expect(audit).toBeInViewport();
  await expect(audit.locator(".bazi-audit-details > summary")).toContainText("专业审计视图");
});
