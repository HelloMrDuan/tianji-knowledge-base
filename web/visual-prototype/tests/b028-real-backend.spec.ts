/**
 * B028 frontend/dream verification batch (TJ-021.1 / TJ-022.3 / TJ-025.1 / TJ-019.3).
 *
 * LOCAL ONLY — real-backend acceptance. Requires a running backend on
 * 127.0.0.1:8000 with reviewed dream/scenario data (assembled acceptance
 * backend, NOT the public repo checkout). This file is deliberately NOT wired
 * to any public CI workflow (workflows run specs by filename; none names this
 * file), so public CI never claims these results. Run locally with:
 *   npm test -- tests/b028-real-backend.spec.ts
 * What it proves beyond the stub spec: the engine REALLY recalculates on year
 * change, the dream API REALLY matches the ten reviewed scenes precisely and
 * rejects generic phrasings, and the life page REALLY aggregates four sources
 * on one birth and one year.
 */
import { test, expect } from "@playwright/test";

test("TJ-021.1 real dream lookup renders all four booklet layers", async ({ page }) => {
  await page.goto("/dream-culture");
  await page.getByLabel("梦境叙述").fill("我梦见一条蛇咬住我的手");
  await page.getByRole("button", { name: "查阅梦象" }).click();
  await expect(page.locator(".dream-culture-match")).toHaveCount(1);
  const match = page.locator(".dream-culture-match").first();
  await expect(match).toContainText("对应梦中原话：");
  await expect(match).toContainText("一条蛇咬住我");
  await expect(match).toContainText("蛇咬人");
  await expect(match).toContainText("蛇咬人主得大财");
  await expect(match).toContainText("出处：《周公解梦》固定电子本");
  await expect(match).toContainText("审核证据等级 C");
  await expect(page.locator(".dream-culture-notice")).toContainText("文化限界：");
  await expect(page.locator(".dream-culture-notice")).toContainText("不代表个人运势、健康或未来事件");
});

test("TJ-021.1 real two-scene dream groups into two booklet articles", async ({ page }) => {
  await page.goto("/dream-culture");
  await page.getByLabel("梦境叙述").fill("我梦见一条蛇咬住我的手，后来梦见我捡到了钱");
  await page.getByRole("button", { name: "查阅梦象" }).click();
  await expect(page.locator(".dream-culture-match")).toHaveCount(2);
  await expect(page.locator(".dream-culture-match").first()).toContainText("梦象 01");
  await expect(page.locator(".dream-culture-match").nth(1)).toContainText("梦象 02");
  await expect(page.locator(".dream-culture-match").first()).toContainText("蛇咬人主得大财");
  await expect(page.locator(".dream-culture-match").nth(1)).toContainText("拾得钱物皆大吉");
});

test("TJ-022.3 real romance page recalculates display on target-year change", async ({ page }) => {
  const years: number[] = [];
  page.on("request", (request) => {
    if (new URL(request.url()).pathname === "/api/v1/scenarios/public" &&
        request.method() === "POST") {
      const body = request.postDataJSON() as { scenario_id: string; input: { target_year: number } };
      if (body?.scenario_id === "romance") years.push(body.input.target_year);
    }
  });
  await page.goto("/romance-structure");
  await page.getByRole("button", { name: "填入示例" }).click();
  await page.getByLabel("观察年份").fill("2026");
  await page.getByRole("button", { name: "查看桃花结构" }).click();
  const result = page.locator(".romance-result");
  await expect(result).toBeVisible();
  await expect(result).toContainText("年支目标 子");
  await expect(result).toContainText("日支目标 酉");
  await expect(page.locator(".romance-result-head")).toContainText("丙午");
  await expect(page.getByLabel("日支与流年地支关系")).toContainText("六冲");
  await expect(page.getByLabel("日支与流年地支关系")).toContainText("子 ↔ 午");
  expect(years).toEqual([2026]);

  await page.getByLabel("观察年份").fill("2027");
  await page.getByRole("button", { name: "查看桃花结构" }).click();
  await expect(page.locator(".romance-result-head")).toContainText("丁未");
  await expect(page.locator(".romance-result-head")).not.toContainText("丙午");
  await expect(page.getByLabel("日支与流年地支关系")).toContainText("六害");
  await expect(page.getByLabel("日支与流年地支关系")).toContainText("子 ↔ 未");
  expect(years).toEqual([2026, 2027]);
});

test("TJ-025.1 real life page aggregates four sources on one birth and one year", async ({ page }) => {
  await page.goto("/life-overview");
  await page.getByRole("button", { name: "填入示例" }).click();
  await page.getByLabel("观察年份").fill("2026");
  await page.getByRole("button", { name: /生成我的人生总览/ }).click();
  const result = page.locator(".life-result");
  await expect(result).toBeVisible();
  await expect(page.locator(".life-result-head")).toContainText("己卯 · 丁丑 · 甲子 · 庚午");
  await expect(page.locator(".life-result-head")).toContainText("2026");
  await expect(page.locator(".life-result-head")).toContainText("丙午");
  await expect(page.locator(".life-result-head")).toContainText(/已绑定 \d+ 条去重 Evidence/);
  const proof = page.getByLabel("四场景来源一致性核验");
  await expect(proof).toContainText("出生盘与目标年份已跨场景核对一致。");
  await expect(proof).toContainText("这是同一套证据的交叉核查，不算新增独立印证。");
  for (const label of ["命盘基础", "年度结构", "桃花结构", "事业财运"]) {
    await expect(proof).toContainText(label);
  }
  await expect(result).toContainText("不推断吉凶");
});

const TEN_EXAMPLES: Array<[string, string]> = [
  ["蛇咬", "蛇咬人主得大财"],
  ["入水", "自在水中大吉利"],
  ["火中", "身在火中贵人扶"],
  ["飞天", "飞上天富贵大吉"],
  ["坠井", "身坠井中疾病凶"],
  ["乘龙", "乘龙入水有贵位"],
  ["游鱼", "群鱼游水主有财"],
  ["新屋", "屋宅更新主大吉"],
  ["兄弟", "兄弟相打大吉利"],
  ["拾钱", "拾得钱物皆大吉"],
];

test("TJ-019.3 all ten reviewed page examples resolve to exactly one precise match", async ({ page }) => {
  await page.goto("/dream-culture");
  for (const [label, excerpt] of TEN_EXAMPLES) {
    await page.getByRole("button", { name: `填入${label}梦境示例` }).click();
    await page.getByRole("button", { name: "查阅梦象" }).click();
    await expect(page.locator(".dream-culture-match")).toHaveCount(1);
    await expect(page.locator(".dream-culture-match")).toContainText(excerpt);
  }
});

test("TJ-019.3 generic phrasings never generalize into a reviewed scene", async ({ page }) => {
  await page.goto("/dream-culture");
  const narrative = page.getByLabel("梦境叙述");
  for (const value of ["梦见蛇", "梦见水", "梦见龙", "梦见鱼", "梦见我家房子", "梦见火"]) {
    await narrative.fill(value);
    await page.getByRole("button", { name: "查阅梦象" }).click();
    await expect(page.locator(".dream-culture-match")).toHaveCount(0);
    await expect(page.getByRole("heading", { name: "暂无可核验的对应条目" })).toBeVisible();
  }
});
