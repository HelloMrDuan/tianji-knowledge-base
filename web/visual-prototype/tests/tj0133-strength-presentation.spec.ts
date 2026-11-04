/**
 * TJ-013.3 U1 Batch C：八字页已审强弱形态事实呈现节浏览器专项。
 *
 * 性质如实标注：这是 **stub 契约测试** —— 四盘的两路 API 响应是
 * 2026-11-03 从已部署 Batch B 的生产后端（Merge SHA 1dc0ee03）
 * 经真实 API 录制的真实响应（1966-07-06T12:00 呈现强、1978-09-20
 * 呈现弱、2007-06-11 未命中、1981-12-21T22:30 冲突），经 page.route
 * 回放；本专项只验证页面渲染、文案与三态区分，不冒称真实后端
 * 计算。真实端到端行为另由生产只读探针与真实浏览器联调验证，
 * 并由离线验收中的密封 Python 专项钉住后端事实。
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

const SCOPE_STATEMENT =
  "本呈现仅陈述已审充分谓词的命中事实；不是全盘旺衰判断，不意味着喜用神或吉凶；未命中不等于弱。";
const LIMITATIONS = [
  "仅限已审的八个充分谓词家族；其余命盘形态暂不可判。",
  "金×酉谓词已注册但在真实历法命盘上构造性不可满足，不声称正例。",
];

test("presented strong renders predicate facts and the approved scope wording", async ({ page }) => {
  const c = CASES.strong;
  await stubApis(page, c.domain, c.scenario);
  await submitCase(page, c);

  const section = page.locator(".bazi-strength-presentation");
  await expect(section).toBeVisible();
  await expect(section).toContainText("已审强弱形态事实");
  await expect(section).toContainText("谓词：司令显现支持形态");
  await expect(section).toContainText("日主：丙 · 月支：午");
  await expect(section).toContainText("限定形态：强形态");
  await expect(section).toContainText("规则来源：已注册的充分谓词");
  await expect(section).toContainText(
    `证据绑定：同请求执行记录已核验（证据条目 ${c.scenario.result.strength_presentation.evidence_ids.length} 条）。`,
  );
  await expect(section).toContainText("该结论只覆盖这一个已审形态，不覆盖全盘。");
  await expect(section).toContainText(SCOPE_STATEMENT);
  for (const line of LIMITATIONS) {
    await expect(section).toContainText(line);
  }
  // 技术字段与确定性误读一律不得出现。
  await expect(section).not.toContainText("身旺");
  await expect(section).not.toContainText("身弱");
  await expect(section).not.toContainText("bazi.rule");
  await expect(section).not.toContainText("bazi.phase2");
  await expect(section).not.toContainText("喜用神为");

  // 调候/病药区块仍在场且结构不变；未选传统口径时大运区块缺席。
  await expect(page.locator(".bazi-xiyong-presentation")).toBeVisible();
  await expect(page.locator(".bazi-xiyong-presentation")).toContainText("调候");
  await expect(page.locator(".bazi-xiyong-presentation")).toContainText("病药");
  await expect(page.locator(".bazi-dayun-presentation")).toHaveCount(0);

  // 第 4 层：范围说明并入说明与限制区。
  await expect(page.locator(".result-limitations")).toContainText(SCOPE_STATEMENT);
});

test("presented weak renders the weak form without ever writing 身弱", async ({ page }) => {
  const c = CASES.weak;
  await stubApis(page, c.domain, c.scenario);
  await submitCase(page, c);

  const section = page.locator(".bazi-strength-presentation");
  await expect(section).toBeVisible();
  await expect(section).toContainText("谓词：孤立受制形态");
  await expect(section).toContainText("日主：乙 · 月支：酉");
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
  await expect(section).toContainText("暂不可判");
  await expect(section).toContainText("本盘未命中任何已审充分谓词；未命中不等于弱。");
  await expect(section).toContainText("暂不可判，不作任何强弱结论。");
  await expect(section).not.toContainText("限定形态");
  await expect(section).not.toContainText("身弱");
  await expect(section).not.toContainText("身旺");
  await expect(section).toContainText(SCOPE_STATEMENT);
});

test("conflict shows an undecided conflict and no classification", async ({ page }) => {
  const c = CASES.conflict;
  await stubApis(page, c.domain, c.scenario);
  await submitCase(page, c);

  const section = page.locator(".bazi-strength-presentation");
  await expect(section).toBeVisible();
  await expect(section).toContainText("本盘存在未裁定的冲突，暂不可判；不作任何强弱结论。");
  await expect(section).not.toContainText("限定形态");
  await expect(section).not.toContainText("身弱");
  await expect(section).not.toContainText("身旺");
  // 冲突 id 与阻断原因码是技术字段，不得渲染。
  await expect(section).not.toContainText("sanming-juan2");
  await expect(section).not.toContainText("root_type_source_conflict");
  await expect(section).toContainText(SCOPE_STATEMENT);
});

test("section is absent when the scenario response carries no strength key", async ({ page }) => {
  const without = JSON.parse(JSON.stringify(CASES.strong.scenario));
  delete without.result.strength_presentation;
  await stubApis(page, CASES.strong.domain, without);
  await submitCase(page, CASES.strong);
  await expect(page.locator(".bazi-pillars article")).toHaveCount(4);
  await expect(page.locator(".bazi-strength-presentation")).toHaveCount(0);
  await expect(page.locator(".bazi-xiyong-presentation")).toBeVisible();
});

test("scenario failure shows an error state distinct from 暂不可判", async ({ page }) => {
  await page.route("**/api/v1/public/execute", async (route) => {
    await route.fulfill({ status: 200, json: CASES.strong.domain });
  });
  await page.route("**/api/v1/scenarios/public", async (route) => {
    await route.fulfill({ status: 500, json: {} });
  });
  await submitCase(page, CASES.strong);

  const errorSection = page.locator(
    '.bazi-strength-presentation[aria-label="已审强弱形态事实加载失败"]',
  );
  await expect(errorSection).toBeVisible();
  await expect(errorSection).toContainText("强弱形态事实加载失败，请稍后重试。");
  await expect(errorSection).toContainText("这不是暂不可判：本次请求未能完成计算。");
  // 未命中与冲突两种正常拒判节一律不得出现。
  await expect(
    page.locator('.bazi-strength-presentation[aria-label="已审强弱形态事实暂不可判"]'),
  ).toHaveCount(0);
  await expect(
    page.locator('.bazi-strength-presentation[aria-label="已审强弱形态事实未裁定冲突"]'),
  ).toHaveCount(0);
});

test("mobile viewport renders the presented section", async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await stubApis(page, CASES.strong.domain, CASES.strong.scenario);
  await submitCase(page, CASES.strong);
  const section = page.locator(".bazi-strength-presentation");
  await expect(section).toBeVisible();
  await section.scrollIntoViewIfNeeded();
  await page.screenshot({ path: "test-results/tj0133-strength-mobile.png" });
});

test("desktop viewport renders the presented section", async ({ page }) => {
  await page.setViewportSize({ width: 1280, height: 800 });
  await stubApis(page, CASES.strong.domain, CASES.strong.scenario);
  await submitCase(page, CASES.strong);
  const section = page.locator(".bazi-strength-presentation");
  await expect(section).toBeVisible();
  await section.scrollIntoViewIfNeeded();
  await page.screenshot({ path: "test-results/tj0133-strength-desktop.png" });
});
