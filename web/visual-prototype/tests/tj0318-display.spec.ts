import { expect, test, type Page } from "@playwright/test";

/**
 * TJ-031.8（专业工具页呈现与表单诚实化）测试性质声明：
 * - 表单诚实化测试是真实 UI 测试：直接断言禁用态与注记文本在页面
 *   DOM 中成立，不经任何 mock。
 * - 请求契约测试走拦截（intercept），只验证前端实际提交的请求形状
 *   （禁用选项不进入请求），不是后端计算测试。
 * - 渲染测试使用固定 fixture 响应，只验证工具页/结果页对响应字段
 *   （warnings、calendar、auxiliary_variant、palaces、scope、
 *   futou_branch 等）的呈现，不验证任何计算正确性。fixture 字段值
 *   取自 TJ-031.6 复审在生产实测的真实响应（resp-ziwei.json /
 *   resp-qimen.json，样本输入分别为紫微 1996-05-18 09:30、奇门
 *   2026-10-03 09:30）。
 */

const ZIWEI_WARNING =
  "C 仅证明四化类型；逐干四化星表为 iztro-default-v2 软件约定 D；壬府/辅尚未裁定。";
const QIMEN_WARNING =
  "C 古典节气选择关系；精确节气时刻、历法转换由 lunar-python 1.4.8 软件提供，现代实现证据 D。";

const ziweiFixture = {
  domain: "ziwei",
  variant: "quanshu-lunar-iztro-mutagen-v1",
  mode: "production",
  deterministic: true,
  chart: {
    life_palace: "子",
    body_palace: "戌",
    life_ganzhi: "庚子",
    bureau: { element: "土", number: 5 },
    palaces: {
      命宫: "子", 兄弟: "亥", 夫妻: "戌", 子女: "酉", 财帛: "申", 疾厄: "未",
      迁移: "午", 仆役: "巳", 官禄: "辰", 田宅: "卯", 福德: "寅", 父母: "丑",
    },
    major_stars: {
      紫微: "亥", 天机: "戌", 太阳: "申", 武曲: "未", 天同: "午", 廉贞: "卯",
      天府: "巳", 太阴: "午", 贪狼: "未", 巨门: "申", 天相: "酉", 天梁: "戌",
      七杀: "亥", 破军: "卯",
    },
    auxiliary_stars: {
      左辅: "未", 右弼: "未", 文昌: "巳", 文曲: "酉", 禄存: "巳",
      擎羊: "午", 陀罗: "辰", 天马: "寅", 地劫: "辰", 天空: "午",
    },
    auxiliary_variant: "quanshu-kongjie-tiankong-v1",
    four_transformations: { 化禄: "天同", 化权: "天机", 化科: "文昌", 化忌: "廉贞" },
    mutagen_variant: "iztro-default-v2",
    mutagen_evidence: "D implementation table; classical types are C; 壬府/辅 unresolved",
    input_scope: "显式非闰月农历；年干支由调用方按约定年界提供；无大限流年或庙旺吉凶",
  },
  rule_matches: [],
  trace: [],
  evidence: {},
  warnings: [ZIWEI_WARNING],
  limitations: ["非闰月农历输入的基本安星链；年界与换日由调用方明确提供。"],
  explanation: null,
  explanation_status: "disabled",
  calendar: {
    local_datetime: "1996-05-18T09:30:00+08:00",
    solar_term: "立夏",
    year_ganzhi: "丙子",
    month_ganzhi: "癸巳",
    day_ganzhi: "乙卯",
    hour_ganzhi: "辛巳",
    day_boundary: "midnight",
    calendar_provider: "lunar-python==1.4.8",
    lunar_year: 1996,
    lunar_month: 4,
    lunar_day: 2,
    tz_name: "Asia/Shanghai",
    ziwei_year_boundary: "lunar-new-year",
  },
};

const qimenFixture = {
  domain: "qimen",
  variant: "qfdk-exact-term-midnight-v2",
  mode: "production",
  deterministic: true,
  chart: {
    dun: "阴",
    bureau: 7,
    yuan: "上元",
    futou_branch: "酉",
    day_ganzhi: "庚戌",
    hour_ganzhi: "辛巳",
    scope: "基础符号盘；不含置闰、超神接气、暗干、格局占断与其他流派。",
    earth_plate: { "7": "戊", "6": "己", "5": "庚", "4": "辛", "3": "壬", "2": "癸", "1": "丁", "9": "丙", "8": "乙" },
    sky_plate: { "9": "丁", "2": "乙", "7": "壬", "6": "辛", "1": "丙", "8": "癸", "3": "戊", "4": "己", "5": "庚" },
    star_positions: { 天蓬: "9", 天任: "2", 天冲: "7", 天辅: "6", 天英: "1", 天禽: "8", 天芮: "8", 天柱: "3", 天心: "4" },
    door_positions: { 休门: "3", 生门: "4", 伤门: "9", 杜门: "2", 景门: "7", 死门: "6", 惊门: "1", 开门: "8" },
    deity_positions: { 六合: "1", 九地: "2", 腾蛇: "3", 值符: "4", 白虎: "6", 玄武: "7", 太阴: "8", 九天: "9" },
    chief_star: { name: "天心", names: ["天心"], origin: "6", palace: "4" },
    chief_door: { name: "开门", palace: "8" },
    center_star_policy: "天禽随天芮同宫（禽芮）；保留所选qfdk转盘约定",
    calendar: {
      solar_term: "秋分",
      day_ganzhi: "庚戌",
      hour_ganzhi: "辛巳",
    },
  },
  rule_matches: [],
  trace: [],
  evidence: {},
  warnings: [QIMEN_WARNING],
  limitations: ["单一精确节气转盘；午夜换日配套五鼠遁时干；天禽寄坤。"],
  explanation: null,
  explanation_status: "disabled",
  calendar: {
    local_datetime: "2026-10-03T09:30:00+08:00",
    solar_term: "秋分",
    year_ganzhi: "丙午",
    month_ganzhi: "丁酉",
    day_ganzhi: "庚戌",
    hour_ganzhi: "辛巳",
    lunar_year: 2026,
    lunar_month: 8,
    lunar_day: 23,
  },
};

async function fulfillExecute(page: Page, fixture: Record<string, unknown>) {
  await page.route("**/api/v1/public/execute", async (route) => {
    await route.fulfill({ status: 200, json: fixture });
  });
}

test.describe("TJ-031.8: ziwei form honesty (real UI)", () => {
  test("school / ratHour / gender are disabled with explicit unsupported notes", async ({ page }) => {
    await page.goto("/ziwei");
    await expect(page.locator("#field-school")).toBeDisabled();
    await expect(page.locator("#field-school-hint")).toContainText("暂不支持中州派");
    await expect(page.locator("#field-school-hint")).toContainText("默认全书系");
    await expect(page.locator("#field-ratHour")).toBeDisabled();
    await expect(page.locator("#field-ratHour-hint")).toContainText("暂不支持顺延次日");
    await expect(page.locator("#field-ratHour-hint")).toContainText("按当日口径");
    await expect(page.locator("#field-gender")).toBeDisabled();
    await expect(page.locator("#field-gender-hint")).toContainText("不参与计算");
  });

  test("static ziwei diagram uses 仆役， matching engine palace names", async ({ page }) => {
    await page.goto("/ziwei");
    const diagram = page.locator(".star-illustration");
    await expect(diagram).toContainText("仆役");
    await expect(diagram).not.toContainText("交友");
  });

  test("disabled options never enter the submitted request (intercepted contract)", async ({ page }) => {
    const sent: Record<string, any>[] = [];
    await page.route("**/api/v1/public/execute", async (route) => {
      sent.push(route.request().postDataJSON());
      await route.abort("failed");
    });
    await page.goto("/ziwei");
    await page.locator("#field-date").fill("1996-05-18");
    await page.locator("#field-time").fill("09:30");
    await page.locator('form button[type="submit"]').first().click();
    await expect.poll(() => sent.length).toBe(1);
    expect(sent[0].domain).toBe("ziwei");
    expect(sent[0].input).toEqual({
      value: "1996-05-18T09:30:00+08:00",
      year_boundary: "lunar-new-year",
    });
  });
});

test.describe("TJ-031.8: ziwei rendering (fixture, NOT computation)", () => {
  test("tool page renders warnings verbatim, auxiliary_variant and the calendar block", async ({ page }) => {
    await fulfillExecute(page, ziweiFixture);
    await page.goto("/ziwei");
    await page.locator("#field-date").fill("1996-05-18");
    await page.locator("#field-time").fill("09:30");
    await page.locator('form button[type="submit"]').first().click();
    const result = page.locator(".entry-result");
    await expect(result).toBeVisible();
    await expect(result.locator(".result-warning")).toHaveText(ZIWEI_WARNING);
    await expect(result).toContainText("辅星口径");
    await expect(result).toContainText("quanshu-kongjie-tiankong-v1");
    const calendarRow = result.locator("div", { hasText: "排盘历法" }).last();
    await expect(result).toContainText("年 丙子");
    await expect(result).toContainText("日 乙卯");
    await expect(result).toContainText("农历 1996 年四月2 日");
    await expect(calendarRow).toContainText("丙子");
  });

  test("result page renders palaces, auxiliary_variant, calendar block and warnings", async ({ page }) => {
    await fulfillExecute(page, ziweiFixture);
    await page.goto(
      `/ziwei/result?value=${encodeURIComponent("1996-05-18T09:30:00+08:00")}&year_boundary=lunar-new-year`,
    );
    const slots = page.locator(".result-field-slots > div");
    const palaces = slots.filter({ hasText: "十二宫" });
    await expect(palaces).toContainText("命宫→子");
    await expect(palaces).toContainText("仆役→巳");
    const stars = slots.filter({ hasText: "主星与辅星" });
    await expect(stars).toContainText("辅星口径 quanshu-kongjie-tiankong-v1");
    const calendar = slots.filter({ hasText: "排盘历法" });
    await expect(calendar).toContainText("年 丙子");
    await expect(calendar).toContainText("农历 1996 年四月2 日");
    await expect(page.locator(".template-state .result-warning")).toHaveText(ZIWEI_WARNING);
  });
});

test.describe("TJ-031.8: qimen rendering (fixture, NOT computation)", () => {
  test("tool page renders warnings verbatim", async ({ page }) => {
    await fulfillExecute(page, qimenFixture);
    await page.goto("/qimen");
    await page.locator("#field-date").fill("2026-10-03");
    await page.locator("#field-time").fill("09:30");
    await page.locator('form button[type="submit"]').first().click();
    const result = page.locator(".entry-result");
    await expect(result).toBeVisible();
    await expect(result.locator(".result-warning")).toHaveText(QIMEN_WARNING);
  });

  test("result page renders scope, day/hour ganzhi, futou_branch and warnings", async ({ page }) => {
    await fulfillExecute(page, qimenFixture);
    await page.goto(
      `/qimen/result?value=${encodeURIComponent("2026-10-03T09:30:00+08:00")}`,
    );
    const slot = page
      .locator(".result-field-slots > div")
      .filter({ hasText: "日时干支与范围" });
    await expect(slot).toContainText("日干支 庚戌");
    await expect(slot).toContainText("时干支 辛巳");
    await expect(slot).toContainText("符头地支 酉");
    await expect(slot).toContainText("基础符号盘；不含置闰、超神接气、暗干、格局占断与其他流派。");
    await expect(page.locator(".template-state .result-warning")).toHaveText(QIMEN_WARNING);
  });
});

test.describe("TJ-031.8: fengshui form honesty (real UI)", () => {
  test("orientation control is gone and the form note states both directions are given", async ({ page }) => {
    await page.goto("/fengshui");
    await expect(page.locator("#field-orientation")).toHaveCount(0);
    await expect(page.locator(".entry-panel-heading p")).toContainText(
      "结果同时给出本向山与对向",
    );
  });
});
