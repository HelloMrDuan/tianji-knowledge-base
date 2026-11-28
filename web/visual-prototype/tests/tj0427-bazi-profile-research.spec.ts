/**
 * TJ-031.19 P0-1/P0-2/P0-3：八字页研究层接线浏览器专项。
 *
 * 性质如实标注：这是 **渲染契约测试**，不是真实后端端到端测试。
 * 两路 API 响应经 page.route 回放：
 * - 详批呈现（profile_presentation）是仓库自有构造器
 *   `build_bazi_profile_presentation` 的真实输出，由
 *   `tests/fixtures/generate-tj0427-fixtures.py` 从后端单元测试的
 *   标注夹具输入生成（见该脚本头的诚实标注）；不是密封运行时的
 *   录制响应，不证明任何后端事实，只验证页面把已返回的研究参考
 *   如实渲染出来、且不再显示已删除的陈旧文案。
 * - 真太阳时对照是 `research_dual_time_chart` 的结果形状夹具：
 *   换算记录、时区校验与节气距离由真实纯函数算出（见生成脚本），
 *   四柱行复用详批夹具的四柱（该经度下时辰不变，四柱相同）；
 *   它验证页面渲染与请求发送，不证明后端对照计算。
 * 真实端到端行为由密封验收（repro21）与生产只读探针验证。
 *
 * 覆盖：P0-1 现代强度模型真实显示；P0-2 扶抑候选真实显示；
 * P0-3 真太阳时输入、请求与对照结果显示；三处陈旧文案消失；
 * 研究层未返回时的诚实未附带态；经度校验与请求失败态。
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

const DOMAIN = loadFixture("tj0427-bazi-profile-domain.json");
const SCENARIO = loadFixture("tj0427-bazi-profile-scenario.json");
const TRUE_SOLAR = loadFixture("tj0427-true-solar.json");

async function stubBaziApis(page: Page, scenarioBody: unknown) {
  await page.route("**/api/v1/public/execute", async (route) => {
    await route.fulfill({ status: 200, json: DOMAIN });
  });
  await page.route("**/api/v1/scenarios/public", async (route) => {
    const body = route.request().postDataJSON() as {
      scenario_id?: string;
    };
    if (body?.scenario_id === "true-solar") {
      await route.fulfill({ status: 200, json: TRUE_SOLAR });
      return;
    }
    await route.fulfill({ status: 200, json: scenarioBody });
  });
}

async function submitBirth(page: Page) {
  await page.goto("/bazi-profile");
  const selects = page.locator("form.bazi-input-card select");
  await selects.nth(0).selectOption("2024");
  await selects.nth(1).selectOption("2");
  await selects.nth(2).selectOption("11");
  await selects.nth(3).selectOption("16");
  await selects.nth(4).selectOption("27");
  await page.getByRole("button", { name: "生成基础档案" }).click();
  await expect(page.locator(".bazi-live-result")).toBeVisible();
}

test("P0-1 现代强度模型显示真实分数与分项", async ({ page }) => {
  await stubBaziApis(page, SCENARIO);
  await submitBirth(page);

  const research = page.locator(
    ".bazi-detail-section[aria-label='研究列：现代强度模型']",
  );
  await expect(research).toBeVisible();
  // 真实模型结论与总分（后端构造器输出：strong，62 分）。
  await expect(research).toContainText("模型结论：强侧（strong），总分 62 分");
  await expect(research).toContainText("总分域 [-35, 105]");
  // 五个分项及其贡献（得令 0、得地 +12、得势 +10、得助 +8、克泄耗 -5）。
  await expect(research).toContainText("得令");
  await expect(research).toContainText("+0 分");
  await expect(research).toContainText("得地");
  await expect(research).toContainText("+12 分");
  await expect(research).toContainText("得势（显干生扶）");
  await expect(research).toContainText("+10 分");
  await expect(research).toContainText("得助（藏干生扶）");
  await expect(research).toContainText("+8 分");
  await expect(research).toContainText("克泄耗");
  await expect(research).toContainText("-5 分");
  // 不确定性与适用边界随模型结果一并说明。
  await expect(research).toContainText("土日主无已审重根集");
  await expect(research).toContainText("四库，本气未审");
  await expect(research).toContainText("适用边界：现代模型是工程近似");
  await expect(research).toContainText("计算依据：");
  // 与已审结论分开呈现；陈旧文案消失。
  await expect(research).toContainText("互不覆盖");
  await expect(page.locator(".bazi-live-result")).not.toContainText(
    "不列模型分数与分项",
  );
});

test("P0-2 扶抑现代层显示候选方向与候选干", async ({ page }) => {
  await stubBaziApis(page, SCENARIO);
  await submitBirth(page);

  const research = page.locator(
    ".bazi-detail-section[aria-label='扶抑现代层研究']",
  );
  await expect(research).toBeVisible();
  // 当前模型强度方向与扶抑候选方向（后端构造器输出）。
  await expect(research).toContainText(
    "当前模型强度方向：现代强度模型结论为 强侧（strong，62 分）",
  );
  await expect(research).toContainText("扶抑候选方向：泄耗克");
  // 候选干（均在本盘显干中）：戊（月干，比肩）。
  await expect(research).toContainText("戊");
  await expect(research).toContainText("月干");
  await expect(research).toContainText("比肩");
  // 候选形成理由与调候/病药并列呈现。
  await expect(research).toContainText("候选形成理由");
  await expect(research).toContainText("得地分 +12：该分项指向强侧");
  await expect(research).toContainText("调候体系（已审）");
  await expect(research).toContainText("病药体系（已审）");
  // 候选不是确定用神；统一喜用结论暂不可判；陈旧文案消失。
  await expect(research).toContainText("候选不是确定用神");
  await expect(research).toContainText("统一喜用结论暂不可判");
  await expect(research).toContainText("格局用神：暂不可判");
  await expect(page.locator(".bazi-live-result")).not.toContainText(
    "不列具体候选方向与候选干",
  );
  await expect(page.locator(".bazi-live-result")).not.toContainText(
    "不列候选干",
  );
});

test("P0-1/P0-2 研究层未返回时如实说明未附带", async ({ page }) => {
  const withoutProfile = JSON.parse(JSON.stringify(SCENARIO));
  delete withoutProfile.result.profile_presentation;
  await stubBaziApis(page, withoutProfile);
  await submitBirth(page);

  const strength = page.locator(
    ".bazi-detail-section[aria-label='研究列：现代强度模型']",
  );
  await expect(strength).toContainText("本次结果未附带详批呈现，研究列暂不呈现。");
  await expect(strength).not.toContainText("总分 62 分");
  const fuyi = page.locator(
    ".bazi-detail-section[aria-label='扶抑现代层研究']",
  );
  await expect(fuyi).toContainText(
    "本次结果未附带详批呈现，候选方向与候选干暂不呈现。",
  );
  await expect(fuyi).not.toContainText("泄耗克");
});

test("P0-3 真太阳时对照：输入经度与时区后显示对照结果", async ({ page }) => {
  const trueSolarRequests: Array<Record<string, any>> = [];
  await page.route("**/api/v1/public/execute", async (route) => {
    await route.fulfill({ status: 200, json: DOMAIN });
  });
  await page.route("**/api/v1/scenarios/public", async (route) => {
    const body = route.request().postDataJSON() as {
      scenario_id?: string;
      input?: Record<string, any>;
    };
    if (body?.scenario_id === "true-solar") {
      trueSolarRequests.push(body.input ?? {});
      await route.fulfill({ status: 200, json: TRUE_SOLAR });
      return;
    }
    await route.fulfill({ status: 200, json: SCENARIO });
  });
  await submitBirth(page);

  const section = page.locator(
    ".bazi-detail-section[aria-label='真太阳时对照（研究）']",
  );
  await expect(section).toBeVisible();
  // 陈旧的固定文案已删除，改为真实输入。
  await expect(page.locator(".bazi-live-result")).not.toContainText(
    "未提供出生地经纬度",
  );
  await page.getByLabel("出生地经度（东经为正，西经为负）").fill("116.4");
  await expect(
    page.getByLabel("出生地时区"),
  ).toHaveValue("");
  await page.getByRole("button", { name: "计算真太阳时对照" }).click();

  // 请求确按场景 API 模式发出：同一出生时刻、经度与出生地时区。
  expect(trueSolarRequests).toHaveLength(1);
  expect(trueSolarRequests[0].value).toBe("2024-02-11T16:27:00+08:00");
  expect(trueSolarRequests[0].longitude_deg).toBe(116.4);
  expect(trueSolarRequests[0].tz_name).toBe("Asia/Shanghai");

  // 对照结果：标准时间 vs 真太阳时、四柱相同、变化原因与月令归属。
  const result = page.locator(".bazi-true-solar-result");
  await expect(result).toBeVisible();
  await expect(result).toContainText("标准时间（出生时刻）：2024-02-11 16:27:07+08:00");
  await expect(result).toContainText("真太阳时（出生地地方太阳时）：2024-02-11 15:58:29+08:00");
  await expect(result).toContainText("与公开排盘相比，真太阳时排盘四柱相同。");
  await expect(result).toContainText("年柱");
  await expect(result).toContainText("标准 甲辰");
  await expect(result).toContainText("真太阳时 甲辰");
  await expect(result).toContainText("时柱");
  await expect(result).toContainText("标准 甲寅");
  await expect(result).toContainText("真太阳时 甲寅");
  await expect(result).not.toContainText("有变化");
  await expect(result).toContainText("月令归属：已确定");
  // 默认排盘未被替换：概览仍显示标准四柱。
  await expect(page.locator(".bazi-result-head h2")).toContainText(
    "甲辰 · 戊辰 · 戊午 · 甲寅",
  );
});

test("P0-3 经度越界不发请求并提示", async ({ page }) => {
  let trueSolarCalls = 0;
  await page.route("**/api/v1/public/execute", async (route) => {
    await route.fulfill({ status: 200, json: DOMAIN });
  });
  await page.route("**/api/v1/scenarios/public", async (route) => {
    const body = route.request().postDataJSON() as {
      scenario_id?: string;
    };
    if (body?.scenario_id === "true-solar") trueSolarCalls += 1;
    await route.fulfill({ status: 200, json: SCENARIO });
  });
  await submitBirth(page);

  await page.getByLabel("出生地经度（东经为正，西经为负）").fill("200");
  await page.getByRole("button", { name: "计算真太阳时对照" }).click();
  await expect(
    page.locator(".bazi-detail-section[aria-label='真太阳时对照（研究）']"),
  ).toContainText("请输入 -180 至 180 之间的出生地经度");
  expect(trueSolarCalls).toBe(0);
});

test("P0-3 对照请求失败时进入错误态，不伪造结果", async ({ page }) => {
  await page.route("**/api/v1/public/execute", async (route) => {
    await route.fulfill({ status: 200, json: DOMAIN });
  });
  await page.route("**/api/v1/scenarios/public", async (route) => {
    const body = route.request().postDataJSON() as {
      scenario_id?: string;
    };
    if (body?.scenario_id === "true-solar") {
      await route.fulfill({ status: 500, json: {} });
      return;
    }
    await route.fulfill({ status: 200, json: SCENARIO });
  });
  await submitBirth(page);

  await page.getByLabel("出生地经度（东经为正，西经为负）").fill("116.4");
  await page.getByRole("button", { name: "计算真太阳时对照" }).click();
  const section = page.locator(
    ".bazi-detail-section[aria-label='真太阳时对照（研究）']",
  );
  await expect(section).toContainText("对照未完成，公开排盘不受影响。");
  await expect(page.locator(".bazi-true-solar-result")).toHaveCount(0);
});
