import { test, expect, type Page } from "@playwright/test";

/** PRIVATE Actions: production reviewed runtime, private Canonical and real API. NO HTTP MOCKS. */
type Json = Record<string, any>;
async function getLiveResponse(page: Page, path: string, action: () => Promise<void>) {
  const pending = page.waitForResponse(r => new URL(r.url()).pathname === path && r.request().method() === "POST",
    {timeout:40000});
  await action();
  const response = await pending;
  expect(response.status(), "real API response, never a stub").toBe(200);
  return {sent:response.request().postDataJSON() as Json, data:await response.json() as Json};
}
function validEvidence(data: Json) {
  expect(data.rule_matches).toEqual(expect.any(Array));
  expect(data.rule_matches.length).toBeGreaterThan(0);
  expect(data.evidence).toEqual(expect.any(Object));
  expect(Object.keys(data.evidence).length).toBeGreaterThan(0);
  for (const rule of data.rule_matches as Json[]) {
    for (const id of rule.evidence_ids || []) expect(data.evidence).toHaveProperty(id);
  }
}
async function questionSetup(page: Page, values: number[]) {
  await page.goto("/ask");
  await page.locator("textarea").first().fill("现在这个工作机会我需要如何看待？");
  await page.locator(".question-time-grid input[type=\"date\"]").fill("2026-10-15");
  await page.locator(".question-time-grid input[type=\"time\"]").fill("12:00");
  for(let i=0;i<6;i++) await page.locator(".yao-input-list select").nth(i).selectOption(String(values[i]));
}
async function sample(page: Page) {
  await page.goto("/bazi-profile");
  await page.getByRole("button", {name:"填入示例"}).click();
  await page.getByRole("button", {name:"保存资料"}).click();
}

test("liuyao: six static yang lines produce same authentic Qian original/changed hexagram", async ({page}) => {
  const values=[7,7,7,7,7,7];
  await questionSetup(page,values);
  const {sent,data}=await getLiveResponse(page,"/api/v1/public/execute",
    ()=>page.getByRole("button",{name:"开始推演"}).click());
  expect(sent.input).toEqual({value:"2026-10-15T12:00:00+08:00",yao_values:values});
  expect(sent.domain).toBe("liuyao");
  expect(data.deterministic).toBe(true);
  expect(data.chart.original.name).toContain("乾");
  expect(data.chart.changed.name).toBe(data.chart.original.name);
  expect(data.chart.changing_lines).toEqual([]);
  validEvidence(data);
  await expect(page.locator(".live-result")).toBeVisible();
  await expect(page.locator(".live-result-head")).toContainText(data.chart.original.name);
  await expect(page.locator(".live-lines .live-line")).toHaveCount(6);
});
test("liuyao: moving line flips real changed chart, invalidation clears previous result", async ({page}) => {
  const values=[9,7,7,7,7,7];
  await questionSetup(page,values);
  const {data}=await getLiveResponse(page,"/api/v1/public/execute",
    ()=>page.getByRole("button",{name:"开始推演"}).click());
  expect(data.chart.original.name).toContain("乾");
  expect(data.chart.changed.name).not.toBe(data.chart.original.name);
  expect(data.chart.changing_lines).toContain(1);
  validEvidence(data);
  await expect(page.locator(".live-result")).toBeVisible();
  await page.locator(".yao-input-list select").first().selectOption("7");
  await expect(page.locator(".live-result")).toHaveCount(0);
});
test("dream: reviewed snake bite yields actual cited cultural match and no AI", async ({page}) => {
  await page.goto("/dream-culture");
  const phrase="我梦见一条蛇咬住我的手";
  await page.getByLabel("梦境叙述").fill(phrase);
  const {sent,data}=await getLiveResponse(page,"/api/v1/dream/culture",
    ()=>page.getByRole("button",{name:/查阅梦象/}).click());
  expect(sent).toEqual({dream_text:phrase});
  expect(data.status).toBe("reviewed_cultural_matches");
  expect(data.ai_enabled).toBe(false);
  expect(data.personal_prediction).toBe(false);
  expect(data.matches.length).toBeGreaterThan(0);
  for(const m of data.matches) {
    expect(m.short_quote.length).toBeGreaterThan(0);
    expect(m.source_title.length).toBeGreaterThan(0);
    expect(m.matched_texts.length).toBeGreaterThan(0);
    for(const text of m.matched_texts) expect(phrase).toContain(text);
  }
  await expect(page.locator(".dream-culture-match")).toHaveCount(data.matches.length);
  await expect(page.locator(".dream-culture-results")).toContainText(data.matches[0].short_quote);
});
test("dream: absent reviewed topic produces honest no-match rather than guessed prediction", async ({page}) => {
  await page.goto("/dream-culture");
  await page.getByLabel("梦境叙述").fill("我梦见明天考试");
  const {data}=await getLiveResponse(page,"/api/v1/dream/culture",
    ()=>page.getByRole("button",{name:/查阅梦象/}).click());
  expect(data.status).toBe("no_reviewed_interpretation");
  expect(data.matches).toEqual([]);
  expect(data.ai_enabled).toBe(false);
  await expect(page.locator(".dream-culture-empty")).toBeVisible();
  await expect(page.locator(".dream-culture-results")).toContainText("暂无可核验的对应条目");
});
test("life: genuine four-source composition, all shared years/charts, citations, and visible report", async ({page}) => {
  await sample(page);
  await page.goto("/life-overview");
  await page.getByLabel("观察年份").fill("2027");
  const {sent,data}=await getLiveResponse(page,"/api/v1/scenarios/public",
    ()=>page.getByRole("button",{name:"生成我的人生总览"}).click());
  expect(sent).toEqual({scenario_id:"life",input:{birth_value:"2000-01-07T12:00:00+08:00",target_year:2027}});
  expect(data.scenario_id).toBe("life");
  expect(data.deterministic).toBe(true);
  validEvidence(data);
  const result=data.result;
  expect(result.profile.pillars).toHaveLength(4);
  for(const key of ["yearly","romance","career"]) {
    expect(result).toHaveProperty(key);
    expect(result[key].target_year.year).toBe(2027);
    expect(result[key].target_year.ganzhi).toBe(result.yearly.target_year.ganzhi);
  }
  const p=result.integration_provenance;
  expect(p.source_scenarios).toEqual(["profile","yearly","romance","career"]);
  expect(p.all_natal_charts_identical).toBe(true);
  expect(p.all_target_years_identical).toBe(true);
  expect(p.evidence_identity_conflicts).toBe(0);
  expect(p.interpretation_allowed).toBe(false);
  for(const id of p.evidence_ids) expect(data.evidence).toHaveProperty(id);
  expect(result.highlights.map((x:Json)=>x.id)).toEqual(["foundation","yearly","romance","career"]);
  expect(result.integrated_reading.personal_prediction).toBe(false);
  await expect(page.locator(".life-result")).toBeVisible();
  await expect(page.locator(".life-result")).toContainText(result.yearly.target_year.ganzhi);
  await expect(page.locator(".life-integrated-report")).toBeVisible();
});
