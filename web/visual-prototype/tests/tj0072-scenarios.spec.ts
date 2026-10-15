import { expect, test, type Page } from "@playwright/test";

/**
 * TJ-007.2: FRONTEND REQUEST CONTRACT ONLY.
 * API requests are intercepted and aborted; no fake successful calculation.
 * Actual calculation correctness is verified separately on the private live API.
 */
async function savedSample(page: Page) {
  await page.goto("/bazi-profile");
  await page.getByRole("button", { name: "填入示例" }).click();
  await page.getByRole("button", { name: "保存资料" }).click();
  await expect.poll(() => page.evaluate(() => localStorage.getItem("tianji.profile.birth.v1"))).not.toBeNull();
}

async function captureRequests(page: Page) {
  const requests: Record<string, any>[] = [];
  await page.route("**/api/v1/scenarios/public", async route => {
    requests.push(route.request().postDataJSON());
    await route.abort("failed");
  });
  return requests;
}

test("romance: submit sends exact birth instant and selected observation year", async ({ page }) => {
  await savedSample(page);
  const seen = await captureRequests(page);
  await page.goto("/romance-structure");
  await page.getByLabel("观察年份").fill("2027");
  await page.locator('form button[type="submit"]').first().click();
  await expect.poll(() => seen.length).toBe(1);
  expect(seen[0].scenario_id).toBe("romance");
  expect(seen[0].input).toEqual({ birth_value: "2000-01-07T12:00:00+08:00", target_year: 2027 });
});

test("career: submit sends exact birth instant and selected observation year", async ({ page }) => {
  await savedSample(page);
  const seen = await captureRequests(page);
  await page.goto("/career-wealth-structure");
  await page.getByLabel("观察年份").fill("2025");
  await page.locator('form button[type="submit"]').first().click();
  await expect.poll(() => seen.length).toBe(1);
  expect(seen[0].scenario_id).toBe("career");
  expect(seen[0].input).toEqual({ birth_value: "2000-01-07T12:00:00+08:00", target_year: 2025 });
});

test("compatibility: exactly mapped A/B inputs and separate traditional roles", async ({ page }) => {
  await savedSample(page);
  const seen = await captureRequests(page);
  await page.goto("/compatibility-structure");
  const personA = page.locator(".compat-person-input").nth(0);
  const personB = page.locator(".compat-person-input").nth(1);
  await personA.locator("select").last().selectOption("male");
  await personB.locator('input[type="date"]').fill("1995-06-20");
  await personB.locator('input[type="time"]').fill("09:00");
  await personB.locator("select").last().selectOption("female");
  await page.locator('form button[type="submit"]').first().click();
  await expect.poll(() => seen.length).toBe(1);
  expect(seen[0].scenario_id).toBe("compatibility");
  expect(seen[0].input).toEqual({
    person_a_birth_value: "2000-01-07T12:00:00+08:00",
    person_b_birth_value: "1995-06-20T09:00:00+08:00",
    person_a_traditional_role: "male",
    person_b_traditional_role: "female",
  });
});

test("romance: 2025 to 2027 updates actual request year (not just the heading)", async ({ page }) => {
  await savedSample(page);
  const seen = await captureRequests(page);
  await page.goto("/romance-structure");
  const year = page.getByLabel("观察年份");
  const submit = page.locator('form button[type="submit"]').first();
  await year.fill("2025");
  await submit.click();
  await expect.poll(() => seen.length).toBe(1);
  await year.fill("2027");
  await submit.click();
  await expect.poll(() => seen.length).toBe(2);
  expect(seen.map(r => r.input.target_year)).toEqual([2025, 2027]);
  expect(seen.every(r => r.scenario_id === "romance")).toBe(true);
});
