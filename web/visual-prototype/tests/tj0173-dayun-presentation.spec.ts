/**
 * TJ-017.3 第二阶段（E0375）：八字页大运呈现节浏览器专项。
 *
 * 性质如实标注：这是 **stub 契约测试** —— 两个 API 响应是 2026-11-02
 * 从组装后的真实后端（生产 runtime、真实知识包）录制的真实响应
 * （Q1 盘 1958-08-15T19:30+08:00、传统男命口径），经 page.route
 * 回放；本专项只验证页面渲染、口径切换与请求契约（口径仅在显式
 * 选择时发送），不冒称真实后端计算。真实端到端行为由离线验收中
 * 的密封 Python 专项（test_tj0173_dayun_public_sealed.py）钉住；
 * 暂不可判形态（恰逢节/神峰零日）由该密封专项钉住，本专项不构造
 * 混合 fixture 冒充。
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

async function stubApis(page: Page, scenarioBody: unknown, captured: { scenarioInput?: any }) {
  await page.route("**/api/v1/public/execute", async (route) => {
    await route.fulfill({ status: 200, json: domainFixture });
  });
  await page.route("**/api/v1/scenarios/public", async (route) => {
    captured.scenarioInput = route.request().postDataJSON()?.input;
    await route.fulfill({ status: 200, json: scenarioBody });
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

test("dayun section renders both methods separately with sanming default", async ({ page }) => {
  const captured: { scenarioInput?: any } = {};
  await stubApis(page, scenarioFixture, captured);
  await fillQ1(page);
  await page.locator("#bazi-dayun-role").selectOption("male");
  await page.getByRole("button", { name: "生成基础档案" }).click();
  await expect(page.locator(".bazi-live-result")).toBeVisible();

  // The role is sent only because it was explicitly selected.
  expect(captured.scenarioInput?.traditional_role).toBe("male");

  const section = page.locator(".bazi-dayun-presentation");
  await expect(section).toBeVisible();
  // Default tab is the Sanming method (method_options.default_method).
  await expect(section).toContainText("大运方向：顺行");
  await expect(section).toContainText("白露");
  await expect(section).toContainText("2840–2850 日");
  await expect(section).toContainText("第 1 运 辛酉");
  await expect(section).toContainText("1966-05-25T19:30:00+08:00");
  await expect(section).toContainText("三命时级与神峰日级为两套分立注册口径、并列呈现、永不合并");
  await expect(section).not.toContainText("吉凶");

  // Switch to the Shenfeng method: its own duration and first-period
  // interval; later periods are honestly not provided.
  await section.getByRole("tab", { name: "神峰通考口径" }).click();
  await expect(section).toContainText("2760–2880 日");
  await expect(section).toContainText("1966-03-06T19:30:00+08:00");
  await expect(section).toContainText("交运区间未提供：本口径只呈现首运交运区间。");
  await expect(section).not.toContainText("2840–2850 日");

  // Limitations are merged into the explanation section verbatim.
  await expect(page.locator(".result-limitations")).toContainText(
    "不呈现任何年龄数值：古典起运为实历时长，年龄折算无原典口径。",
  );
  await expect(page.locator(".result-limitations")).toContainText(
    "本呈现不是吉凶判断，不预测任何现实事件。",
  );
});

test("no role selected: role is not sent and the section is absent", async ({ page }) => {
  const captured: { scenarioInput?: any } = {};
  const without = JSON.parse(JSON.stringify(scenarioFixture));
  delete without.result.dayun_presentation;
  await stubApis(page, without, captured);
  await fillQ1(page);
  await page.getByRole("button", { name: "生成基础档案" }).click();
  await expect(page.locator(".bazi-pillars article")).toHaveCount(4);
  expect(captured.scenarioInput?.traditional_role).toBeUndefined();
  await expect(page.locator(".bazi-dayun-presentation")).toHaveCount(0);
});
