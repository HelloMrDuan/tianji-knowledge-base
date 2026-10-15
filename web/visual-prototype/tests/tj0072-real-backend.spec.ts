import { expect, test, type Page } from "@playwright/test";

/** Private Actions only: genuine private Canonical, reviewed runtime and Python API. NO MOCKS. */
type Json = Record<string, any>;
const apiPath = "/api/v1/scenarios/public";
const sampleBirth = "2000-01-07T12:00:00+08:00";

async function setSample(page: Page) {
  await page.goto("/bazi-profile");
  await page.getByRole("button", { name: "填入示例" }).click();
  await page.getByRole("button", { name: "保存资料" }).click();
  await expect.poll(() => page.evaluate(() => localStorage.getItem("tianji.profile.birth.v1"))).not.toBeNull();
}

async function submitLive(page: Page, scenario: string): Promise<{ sent: Json; data: Json }> {
  const pending = page.waitForResponse(r =>
    new URL(r.url()).pathname === apiPath && r.request().method() === "POST",
    { timeout: 40_000 }
  );
  await page.locator('form button[type="submit"]').first().click();
  const response = await pending;
  expect(response.status(), scenario + " must be real HTTP 200").toBe(200);
  const sent = response.request().postDataJSON() as Json;
  const data = await response.json() as Json;
  expect(sent.scenario_id).toBe(scenario);
  expect(data.scenario_id).toBe(scenario);
  expect(data.deterministic).toBe(true);
  expect(data.result).toBeTruthy();
  expect(data.rule_matches).toEqual(expect.any(Array));
  expect(data.rule_matches.length).toBeGreaterThan(0);
  expect(data.evidence).toEqual(expect.any(Object));
  for (const rule of data.rule_matches as Json[]) {
    for (const id of rule.evidence_ids || []) {
      expect(data.evidence, "orphan source ID: " + id).toHaveProperty(id);
    }
  }
  return { sent, data };
}

test("romance: live natal chart, two Xianchi bases, flow year and user summary", async ({ page }) => {
  await setSample(page);
  await page.goto("/romance-structure");
  await page.getByLabel("观察年份").fill("2027");
  const { sent, data } = await submitLive(page, "romance");
  expect(sent.input).toEqual({ birth_value: sampleBirth, target_year: 2027 });
  const r = data.result;
  expect(r.target_year.year).toBe(2027);
  expect(r.target_year.ganzhi).toEqual(expect.any(String));
  expect(r.natal.pillars).toHaveLength(4);
  expect(r.xianchi.targets.year_branch).toEqual(expect.any(String));
  expect(r.xianchi.targets.day_branch).toEqual(expect.any(String));
  expect(r.target_year_activation.year_branch_basis.matched).toEqual(expect.any(Boolean));
  expect(r.target_year_activation.day_branch_basis.matched).toEqual(expect.any(Boolean));
  await expect(page.locator(".romance-result")).toBeVisible();
  await expect(page.locator(".romance-result .consumer-result-summary")).toContainText(r.xianchi.targets.year_branch);
  await expect(page.locator(".romance-result-head")).toContainText(r.target_year.ganzhi);
  await expect(page.locator(".romance-result")).toContainText("典籍依据");
});

test("career: real structural groups, annual reading and verified citations", async ({ page }) => {
  await setSample(page);
  await page.goto("/career-wealth-structure");
  await page.getByLabel("观察年份").fill("2026");
  const { sent, data } = await submitLive(page, "career");
  expect(sent.input).toEqual({ birth_value: sampleBirth, target_year: 2026 });
  const r = data.result;
  expect(r.target_year.year).toBe(2026);
  expect(r.natal.pillars).toHaveLength(4);
  for (const key of ["wealth", "authority", "output", "resource", "peers"]) {
    expect(r.structure_groups).toHaveProperty(key);
    expect(r.structure_groups[key].visible_count).toEqual(expect.any(Number));
    expect(r.structure_groups[key].hidden_count).toEqual(expect.any(Number));
  }
  expect(r.annual_reading.year).toBe(2026);
  for (const id of r.annual_reading.evidence_ids || []) expect(data.evidence).toHaveProperty(id);
  await expect(page.locator(".career-result")).toBeVisible();
  await expect(page.locator(".career-annual-reading")).toContainText(r.annual_reading.headline);
  await expect(page.locator(".career-result .consumer-result-summary")).toContainText(r.target_year.stem_ten_god);
  await expect(page.locator(".career-result")).not.toContainText("该证据已由服务端绑定");
});

test("compatibility: real two-person charts, directional ten gods and evidence matrix", async ({ page }) => {
  await setSample(page);
  await page.goto("/compatibility-structure");
  const b = page.locator(".compat-person-input").nth(1);
  await b.locator('input[type="date"]').fill("1995-06-20");
  await b.locator('input[type="time"]').fill("09:00");
  const { sent, data } = await submitLive(page, "compatibility");
  expect(sent.input.person_a_birth_value).toBe(sampleBirth);
  expect(sent.input.person_b_birth_value).toBe("1995-06-20T09:00:00+08:00");
  const r = data.result;
  expect(r.person_a.pillars).toHaveLength(4);
  expect(r.person_b.pillars).toHaveLength(4);
  expect(r.person_a.pillars.map((x: Json) => x.ganzhi)).not.toEqual(r.person_b.pillars.map((x: Json) => x.ganzhi));
  const relations = r.day_master_relations;
  expect(relations.a_sees_b.ten_god).toEqual(expect.any(String));
  expect(relations.b_sees_a.ten_god).toEqual(expect.any(String));
  expect(r.relation_evidence_matrix).toEqual(expect.any(Array));
  expect(r.relation_evidence_matrix.length).toBeGreaterThan(0);
  for (const item of r.relation_evidence_matrix as Json[]) {
    for (const id of item.evidence_ids || []) expect(data.evidence).toHaveProperty(id);
  }
  await expect(page.locator(".compat-result")).toBeVisible();
  await expect(page.getByRole("region", { name: "本次合盘摘要" })).toContainText(relations.a_sees_b.ten_god);
  await expect(page.getByRole("region", { name: "本次合盘摘要" })).toContainText(relations.b_sees_a.ten_god);
  await expect(page.locator(".compat-people .compat-pillars article")).toHaveCount(8);
  await expect(page.locator(".compat-result")).toContainText("关系证据矩阵");
});

test("romance: 2025 -> 2027 triggers two actual computations and matching result years", async ({ page }) => {
  await setSample(page);
  await page.goto("/romance-structure");
  const year = page.getByLabel("观察年份");
  let previous = "";
  for (const y of [2025, 2027]) {
    await year.fill(String(y));
    const { sent, data } = await submitLive(page, "romance");
    expect(sent.input.target_year).toBe(y);
    expect(data.result.target_year.year).toBe(y);
    await expect(page.locator(".romance-result-head")).toContainText(String(y));
    await expect(page.locator(".romance-result-head")).toContainText(data.result.target_year.ganzhi);
    if (previous) expect(data.result.target_year.ganzhi).not.toBe(previous);
    previous = data.result.target_year.ganzhi;
  }
});

test("career: 2025 -> 2027 recomputes genuine annual interpretation", async ({ page }) => {
  await setSample(page);
  await page.goto("/career-wealth-structure");
  const year = page.getByLabel("观察年份");
  for (const y of [2025, 2027]) {
    await year.fill(String(y));
    const { sent, data } = await submitLive(page, "career");
    expect(sent.input.target_year).toBe(y);
    expect(data.result.target_year.year).toBe(y);
    expect(data.result.annual_reading.year).toBe(y);
    await expect(page.locator(".career-annual-reading")).toContainText(data.result.annual_reading.headline);
    await expect(page.locator(".career-result-head")).toContainText(data.result.target_year.ganzhi);
  }
});
