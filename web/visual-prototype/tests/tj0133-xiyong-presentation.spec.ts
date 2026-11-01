/**
 * TJ-013.3 第一阶段（E0372）：八字页调候/病药呈现节浏览器专项。
 *
 * 性质如实标注：这是 **stub 契约测试** —— 两个 API 响应是 2026-11-01
 * 从组装后的真实后端（生产 runtime、真实知识包）录制的真实响应
 * （G1 盘 1960-03-07T01:30+08:00），经 page.route 回放；本专项只
 * 验证页面渲染与文案，不冒称真实后端计算。真实端到端行为由离线
 * 验收中的密封 Python 专项（test_tj0133_xiyong_public_sealed.py）
 * 钉住。
 */
import { readFileSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { expect, test, type Page } from "@playwright/test";

const here = path.dirname(fileURLToPath(import.meta.url));
const domainFixture = JSON.parse(
  readFileSync(path.join(here, "fixtures", "tj0133-g1-domain.json"), "utf-8"),
);
const scenarioFixture = JSON.parse(
  readFileSync(path.join(here, "fixtures", "tj0133-g1-scenario.json"), "utf-8"),
);

async function stubApis(page: Page, scenarioBody: unknown) {
  await page.route("**/api/v1/public/execute", async (route) => {
    await route.fulfill({ status: 200, json: domainFixture });
  });
  await page.route("**/api/v1/scenarios/public", async (route) => {
    await route.fulfill({ status: 200, json: scenarioBody });
  });
}

async function submitG1(page: Page) {
  await page.goto("/bazi-profile");
  const selects = page.locator("form.bazi-input-card select");
  await selects.nth(0).selectOption("1960");
  await selects.nth(1).selectOption("3");
  await selects.nth(2).selectOption("7");
  await selects.nth(3).selectOption("1");
  await selects.nth(4).selectOption("30");
  await page.getByRole("button", { name: "生成基础档案" }).click();
  await expect(page.locator(".bazi-live-result")).toBeVisible();
}

test("presentation section renders both systems, relations and layers", async ({ page }) => {
  await stubApis(page, scenarioFixture);
  await submitG1(page);

  const section = page.locator(".bazi-xiyong-presentation");
  await expect(section).toBeVisible();
  await expect(section).toContainText("调候体系（《穷通宝鉴》甲木二月条）：原文取用顺序为：庚（第1取，透于年柱）。");
  await expect(section).toContainText("病药体系（《神峰通考》）");
  await expect(section).toContainText("第一对（所论之神财、病为比劫、药为官杀）：所论之神财见于月柱干己（正财）；病之比劫见于时柱干乙（劫财）；药之官杀见于年柱干庚（七杀）。");
  await expect(section).toContainText("去病效力暂不可判。");
  await expect(section).toContainText("干庚：两体系同向。调候取用顺序第 1 位；病药判为药之神（第一对）。");
  await expect(section).toContainText("各体系陈述并列呈现，系统不作统一裁定。");
  await expect(section).not.toContainText("喜用神");

  // 第 3 层：两体系逐字短引。
  await expect(page.locator(".bazi-result-columns")).toContainText("《穷通宝鉴》调候条目原文");
  await expect(page.locator(".bazi-result-columns")).toContainText("《神峰通考》病药原文");

  // 第 4 层：范围声明与限制并入。
  await expect(page.locator(".result-limitations")).toContainText(
    "本呈现只含调候（《穷通宝鉴》）与病药（《神峰通考》）两类已注册取用依据",
  );
  await expect(page.locator(".result-limitations")).toContainText("某一对未触发不等于无病。");

  // §4.7 文案收窄：新边界文案在场，旧的全称否定文案消失。
  await expect(page.locator(".bazi-boundary-card")).toContainText(
    "不自动定格局；调候与病药只呈现已注册依据，不作统一喜用结论",
  );
  await expect(page.locator(".bazi-boundary-card")).not.toContainText("不自动定格局、调候");
});

test("section is absent when the scenario response carries no presentation", async ({ page }) => {
  const without = JSON.parse(JSON.stringify(scenarioFixture));
  delete without.result.xiyong_presentation;
  await stubApis(page, without);
  await submitG1(page);
  await expect(page.locator(".bazi-pillars article")).toHaveCount(4);
  await expect(page.locator(".bazi-xiyong-presentation")).toHaveCount(0);
});
