/**
 * B028 frontend/dream verification batch (TJ-021.1 / TJ-022.3 / TJ-025.1).
 *
 * Controlled synthetic HTTP contracts (page.route stubs with fixed responses),
 * explicitly labeled: no real backend is required, so this spec runs in public CI.
 * What it proves is FRONTEND wiring only: the pages render the WBS structures
 * (dream 4-layer booklet, romance two-basis + year recalculation display,
 * life 4-source consistency display) from well-formed API responses, and show
 * limits instead of predictions. Real engine behavior (actual recalculation,
 * actual reviewed matching) is covered by backend tests and by the local-only
 * b028-real-backend.spec.ts, which is NOT wired to public CI.
 */
import { test, expect } from "@playwright/test";

const DREAM_NOTICE = "仅展示已审核传统占梦条目，不代表个人运势、健康或未来事件。";

async function stubDreamCulture(page: import("@playwright/test").Page, mode: "two" | "none") {
  await page.route("**/api/v1/dream/culture", async (route) => {
    if (mode === "none") {
      return route.fulfill({
        status: 200,
        json: {
          api_version: "v1",
          status: "no_reviewed_interpretation",
          public_release: true,
          cultural_reference_only: true,
          ai_enabled: false,
          personal_prediction: false,
          matches: [],
          unreviewed_topics: [{ label: "考试", matched_texts: ["梦见考试"] }],
          notice: DREAM_NOTICE,
        },
      });
    }
    return route.fulfill({
      status: 200,
      json: {
        api_version: "v1",
        status: "reviewed_cultural_matches",
        public_release: true,
        cultural_reference_only: true,
        ai_enabled: false,
        personal_prediction: false,
        matches: [
          {
            scene: "蛇咬人",
            matched_texts: ["一条蛇咬住我"],
            cultural_reading: "此条目将蛇咬人的梦象关联得财，是传统占梦文本中的象征说法。",
            short_quote: "蛇咬人主得大财",
            source_title: "《周公解梦》固定电子本",
            evidence_level: "C",
          },
          {
            scene: "拾得钱物",
            matched_texts: ["捡到了钱"],
            cultural_reading: "此条目将拾得钱物的梦象关联大吉，是传统占梦文本中的象征说法。",
            short_quote: "拾得钱物皆大吉",
            source_title: "《周公解梦》固定电子本",
            evidence_level: "C",
          },
        ],
        unreviewed_topics: [],
        notice: DREAM_NOTICE,
      },
    });
  });
}

test("TJ-021.1 dream booklet renders all four layers per match, grouped", async ({ page }) => {
  await stubDreamCulture(page, "two");
  await page.goto("/dream-culture");
  await page.getByLabel("梦境叙述").fill("我梦见一条蛇咬住我的手，后来梦见我捡到了钱");
  await page.getByRole("button", { name: "查阅梦象" }).click();
  await expect(page.getByRole("heading", { name: "梦象查阅结果" })).toBeVisible();
  // Grouping: two matches render as two separate booklet articles.
  await expect(page.locator(".dream-culture-match")).toHaveCount(2);
  await expect(page.locator(".dream-culture-match").first()).toContainText("梦象 01");
  await expect(page.locator(".dream-culture-match").nth(1)).toContainText("梦象 02");
  const first = page.locator(".dream-culture-match").first();
  // Layer 1 原梦叙述, layer 2 审核对应, layer 3 出处, layer 4 文化限界.
  await expect(first).toContainText("对应梦中原话：");
  await expect(first).toContainText("一条蛇咬住我");
  await expect(first).toContainText("蛇咬人");
  await expect(first).toContainText("蛇咬人主得大财");
  await expect(first).toContainText("出处：《周公解梦》固定电子本");
  await expect(first).toContainText("审核证据等级 C");
  await expect(page.locator(".dream-culture-notice")).toContainText(`文化限界：${DREAM_NOTICE}`);
  const second = page.locator(".dream-culture-match").nth(1);
  await expect(second).toContainText("拾得钱物");
  await expect(second).toContainText("拾得钱物皆大吉");
  await expect(second).toContainText("出处：《周公解梦》固定电子本");
});

test("TJ-021.1 dream booklet shows honest empty state and unreviewed topics", async ({ page }) => {
  await stubDreamCulture(page, "none");
  await page.goto("/dream-culture");
  await page.getByLabel("梦境叙述").fill("梦见考试");
  await page.getByRole("button", { name: "查阅梦象" }).click();
  await expect(page.getByRole("heading", { name: "暂无可核验的对应条目" })).toBeVisible();
  await expect(page.locator(".dream-culture-match")).toHaveCount(0);
  const unresolved = page.getByLabel("未获审核的梦境主题");
  await expect(unresolved).toContainText("考试");
  await expect(unresolved).toContainText("尚无严格对应的已审核条目");
});

function romanceStub(year: number) {
  const target = year === 2027
    ? { ganzhi: "丁未", branch: "未", relation: "harm", relationName: "六害" }
    : { ganzhi: "丙午", branch: "午", relation: "clash", relationName: "六冲" };
  return {
    scenario_id: "romance",
    status: "production_limited",
    public_release: false,
    deterministic: true,
    result: {
      release_scope: "xianchi_structure_only",
      natal: {
        pillars: [
          { name: "year", ganzhi: "己卯", stem: { ten_god: "七杀" } },
          { name: "month", ganzhi: "丁丑", stem: { ten_god: "食神" } },
          { name: "day", ganzhi: "甲子", stem: { ten_god: "日主" } },
          { name: "hour", ganzhi: "庚午", stem: { ten_god: "正官" } },
        ],
      },
      xianchi: {
        targets: { year_branch: "子", day_branch: "酉" },
        natal_matches: [
          { basis: "year_branch", pillar: "year" },
          { basis: "day_branch", pillar: "day" },
        ],
      },
      target_year_activation: {
        year_branch_basis: { matched: false },
        day_branch_basis: { matched: false },
      },
      target_year: { year, ganzhi: target.ganzhi, branch: target.branch },
      spouse_palace_year_relations: {
        natal_day_branch: "子",
        target_year_branch: target.branch,
        relations: [
          {
            relation_type: target.relation,
            natal_branch: "子",
            flow_branch: target.branch,
            rule_id: "stub.rule.spouse",
            evidence_ids: ["E01"],
          },
        ],
      },
    },
    rule_matches: [],
    trace: [{ step: "stub romance trace" }],
    evidence: {
      E01: {
        classic_title: "《周公解梦》固定电子本",
        original_text: "子午相冲之例",
        evidence_level: "C",
      },
    },
    warnings: [],
    limitations: ["结构命中或未命中都不等于现实婚恋结果。"],
  };
}

test("TJ-022.3 romance page shows two bases separately and truly recalculates on year change", async ({ page }) => {
  const years: number[] = [];
  await page.route("**/api/v1/scenarios/public", async (route) => {
    const body = route.request().postDataJSON() as { scenario_id: string; input: { target_year: number } };
    if (body?.scenario_id === "romance") {
      years.push(body.input.target_year);
      return route.fulfill({ status: 200, json: romanceStub(body.input.target_year) });
    }
    return route.continue();
  });
  await page.goto("/romance-structure");
  await page.getByRole("button", { name: "填入示例" }).click();
  await page.getByLabel("观察年份").fill("2026");
  await page.getByRole("button", { name: "查看桃花结构" }).click();
  const result = page.locator(".romance-result");
  await expect(result).toBeVisible();
  // Plain-language condition summary first (UI-07).
  await expect(page.getByLabel("本次测算摘要")).toContainText("桃花姻缘 · 本次核对结果");
  await expect(page.getByLabel("本次测算摘要")).toContainText("正缘、婚期、婚姻吉凶尚无足够审定依据");
  // Method differences: two bases shown separately, never merged.
  await expect(result).toContainText("年支目标 子");
  await expect(result).toContainText("日支目标 酉");
  await expect(result).toContainText("年支起查");
  await expect(result).toContainText("日支起查");
  // 2026 display: 丙午 + 子午六冲.
  await expect(page.locator(".romance-result-head")).toContainText("丙午");
  await expect(page.locator(".romance-result-head")).toContainText("流年地支 午");
  await expect(page.getByLabel("日支与流年地支关系")).toContainText("六冲");
  await expect(page.getByLabel("日支与流年地支关系")).toContainText("子 ↔ 午");
  // No prediction rendering inside the result.
  await expect(result).not.toContainText("桃花指数");
  expect(years).toEqual([2026]);

  // Year change truly recalculates: new request + new display.
  await page.getByLabel("观察年份").fill("2027");
  await page.getByRole("button", { name: "查看桃花结构" }).click();
  await expect(page.locator(".romance-result-head")).toContainText("丁未");
  await expect(page.locator(".romance-result-head")).toContainText("流年地支 未");
  await expect(page.locator(".romance-result-head")).not.toContainText("丙午");
  await expect(page.getByLabel("日支与流年地支关系")).toContainText("六害");
  await expect(page.getByLabel("日支与流年地支关系")).toContainText("子 ↔ 未");
  expect(years).toEqual([2026, 2027]);
});

function lifeStub() {
  return {
    scenario_id: "life",
    status: "production_limited",
    public_release: false,
    deterministic: true,
    result: {
      release_scope: "deterministic_aggregate_only",
      profile: {
        pillars: [
          { name: "year", ganzhi: "己卯" },
          { name: "month", ganzhi: "丁丑" },
          { name: "day", ganzhi: "甲子" },
          { name: "hour", ganzhi: "庚午" },
        ],
        day_master: { stem: "甲" },
        strength_context: { boundary: "旺衰仍未裁定。" },
      },
      integrated_reading: {
        headline: "四源同盘同年的交叉核对",
        foundation: "命盘因素来自已审四柱。",
        career: "事业财运来自已审十神位置。",
        romance: "桃花与夫妻宫来自已审地支关系。",
        cross_rule: "四源出生盘与目标年一致。",
        evidence_ids: ["E01"],
        dayun: "大运仍未裁定。",
        boundary: "不是完整人生预测。",
      },
      integration_provenance: {
        all_natal_charts_identical: true,
        all_target_years_identical: true,
        evidence_contributions: [
          { scenario: "profile", evidence_ids: ["E01", "E02"] },
          { scenario: "yearly", evidence_ids: ["E01"] },
          { scenario: "romance", evidence_ids: ["E01"] },
          { scenario: "career", evidence_ids: ["E02"] },
        ],
      },
      yearly: {
        target_year: { year: 2026, ganzhi: "丙午" },
        annual_branch_interactions: { evaluated_pairs: 4, hits: [] },
      },
      romance: {
        xianchi: { targets: { year_branch: "子", day_branch: "酉" } },
        target_year_activation: {},
        spouse_palace_year_relations: null,
      },
      career: { structure_groups: {}, interpretation_cards: [], target_year: {} },
      highlights: [],
    },
    rule_matches: [],
    trace: [{ step: "stub life trace" }],
    evidence: {
      E01: { classic_title: "《周公解梦》固定电子本", original_text: "子午相冲之例", evidence_level: "C" },
      E02: { classic_title: "《渊海子平》", original_text: "甲木生于丑月之例", evidence_level: "C" },
    },
    warnings: [],
    limitations: ["不是完整人生预测。"],
  };
}

test("TJ-025.1 life page shows four sources on one birth and one year, deduped", async ({ page }) => {
  await page.route("**/api/v1/scenarios/public", async (route) => {
    const body = route.request().postDataJSON() as { scenario_id: string };
    if (body?.scenario_id === "life") {
      return route.fulfill({ status: 200, json: lifeStub() });
    }
    return route.continue();
  });
  await page.goto("/life-overview");
  await page.getByRole("button", { name: "填入示例" }).click();
  await page.getByLabel("观察年份").fill("2026");
  await page.getByRole("button", { name: /生成我的人生总览/ }).click();
  const result = page.locator(".life-result");
  await expect(result).toBeVisible();
  await expect(page.locator(".life-result-head")).toContainText("己卯 · 丁丑 · 甲子 · 庚午");
  await expect(page.locator(".life-result-head")).toContainText("2026");
  await expect(page.locator(".life-result-head")).toContainText("丙午");
  await expect(page.locator(".life-result-head")).toContainText("已绑定 2 条去重 Evidence");
  const proof = page.getByLabel("四场景来源一致性核验");
  await expect(proof).toContainText("出生盘与目标年份已跨场景核对一致。");
  await expect(proof).toContainText("这是同一套证据的交叉核查，不算新增独立印证。");
  await expect(proof).toContainText("命盘基础");
  await expect(proof).toContainText("年度结构");
  await expect(proof).toContainText("桃花结构");
  await expect(proof).toContainText("事业财运");
  await expect(result).toContainText("不推断吉凶");
  await expect(result).not.toContainText("分数");
});
