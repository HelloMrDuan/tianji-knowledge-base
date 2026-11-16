/**
 * TJ-029.1 Line C: remaining four-pillar cards readability
 * (.bazi-pillars / .life-pillars / .compat-pillars) + romance spouse-pairing.
 *
 * Local-only: needs a real backend (vite proxies /api + /health to it).
 * Base URL is the vite dev server on port 4174. Do not add to public CI.
 *
 * Failing state before the fix (computed from the CSS values, same WCAG
 * formula as E0403; browser measurement pending backend availability):
 *  - Pillar ganzhi <strong> has no color rule in any of the three cards and
 *    inherits night gold #f0d6a0: bazi 1.25-1.35:1 (27px, on #fbfaf4 /
 *    #eef2e8), life 1.25-1.40:1 (23px, on #fffef9 / #edf2e8), compat
 *    1.25-1.39:1 (18px, on #fffdf8 / #edf2e8). Even the 27px bazi ganzhi
 *    fails the 3:1 large-text bar.
 *  - Bazi stem/branch values (.bazi-stem b / .bazi-branch b, 20px) and the
 *    hidden-stem spans (.bazi-branch>div span, 11px) inherit gold the same
 *    way: 1.25-1.35:1.
 *  - Life pillar labels (.life-pillars small #8d9486, 10px): 3.10:1 on
 *    #fffef9, 2.75:1 on day-pillar #edf2e8. Life branch value
 *    (.life-pillars em #a18a60, 11px): 3.29:1 / 2.92:1.
 *  - Compat labels (.compat-pillars small/span #8b9384, 9px): 3.13:1 on
 *    #fffdf8, 2.80:1 on day-pillar #edf2e8.
 * Fix (one grouped rule in public.css, Line C): the three cards share the
 * structure of the fixed .romance-pillars / .yearly-pillars grids (E0403),
 * so one rule pins the verified palette on these three cards only —
 * ganzhi / stem / branch values #315943 (6.99-7.88:1), failing labels
 * #5a6b5c (5.00-5.63:1). The bazi labels (#66705f, 4.57-4.96:1) and
 * ten-god values (#49634f, #566d5c) already pass AA and are unchanged.
 * The .life-result-head h2 joins the four ganzhi on the DARK page
 * background and keeps its gold by design; it is guarded, not changed.
 *
 * Romance spouse-pairing (.romance-spouse-pairing > p): E0403 coloured it
 * structurally (#667268 / strong #7f5349) but the sample never rendered it
 * because fillSample does not set a traditional_role. This spec selects
 * the "female" role (传统女命口径 · 看官杀), which makes the backend
 * return spouse_star_year_pairing, and measures the paragraph for real.
 */
import { test, expect, type Page } from "@playwright/test";

const MIN_RATIO = 4.5;

type NodeRow = { sel: string; text: string; ratio: number };

async function measureCardText(page: Page, cardSel: string): Promise<NodeRow[]> {
  return await page.evaluate((sel) => {
    const parse = (s: string) => {
      const m = s.match(/rgba?\(([^)]+)\)/);
      if (!m) return null;
      const p = m[1].split(",").map((x) => parseFloat(x));
      return { r: p[0], g: p[1], b: p[2], a: p.length > 3 ? p[3] : 1 };
    };
    const lum = (c: { r: number; g: number; b: number }) => {
      const f = (v: number) => {
        v /= 255;
        return v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4);
      };
      return 0.2126 * f(c.r) + 0.7152 * f(c.g) + 0.0722 * f(c.b);
    };
    const rows: NodeRow[] = [];
    for (const card of Array.from(document.querySelectorAll(sel))) {
      for (const el of Array.from(card.querySelectorAll("*"))) {
        const cs = getComputedStyle(el);
        const text = (el.textContent || "").trim();
        if (!text || el.children.length > 0) continue;
        if (cs.display === "none" || cs.visibility === "hidden") continue;
        const color = parse(cs.color)!;
        const chain: string[] = [];
        let node: Element | null = el;
        while (node && node !== document.documentElement) {
          chain.push(getComputedStyle(node).backgroundColor);
          node = node.parentElement;
        }
        chain.push(getComputedStyle(document.documentElement).backgroundColor);
        chain.push(getComputedStyle(document.body).backgroundColor);
        let acc = { r: 255, g: 255, b: 255 };
        for (let i = chain.length - 1; i >= 0; i--) {
          const p = parse(chain[i]);
          if (!p || p.a <= 0) continue;
          acc = { r: p.r * p.a + acc.r * (1 - p.a), g: p.g * p.a + acc.g * (1 - p.a), b: p.b * p.a + acc.b * (1 - p.a) };
        }
        const l1 = lum(color), l2 = lum(acc);
        const ratio = (Math.max(l1, l2) + 0.05) / (Math.min(l1, l2) + 0.05);
        let path = el.tagName.toLowerCase();
        const cls = (el.getAttribute("class") || "").split(" ")[0];
        if (cls) path += "." + cls;
        rows.push({ sel: path, text: text.slice(0, 20), ratio: Math.round(ratio * 100) / 100 });
      }
    }
    return rows;
  }, cardSel);
}

function assertAllContrast(rows: NodeRow[], pageName: string) {
  expect(rows.length, `${pageName}: pillar card must contain visible text`).toBeGreaterThan(0);
  const failing = rows.filter((r) => r.ratio < MIN_RATIO);
  expect(failing, `${pageName}: failing text nodes: ${JSON.stringify(failing)}`).toEqual([]);
}

const SAMPLE_GANZHI = ["己卯", "丁丑", "甲子", "庚午"];

for (const width of [360, 390, 768, 1440]) {
  test(`pillar cards readable at ${width}px (bazi + life + compat)`, async ({ page }) => {
    await page.setViewportSize({ width, height: 800 });
    // Bazi profile: sample 2000-01-07 12:00.
    await page.goto("/bazi-profile");
    await page.getByRole("button", { name: "填入示例" }).click();
    await page.getByRole("button", { name: "生成基础档案" }).click();
    await page.locator(".bazi-live-result").waitFor({ state: "visible", timeout: 30000 });
    await page.waitForTimeout(400);
    const baziRows = await measureCardText(page, ".bazi-pillars");
    expect(baziRows.length).toBeGreaterThanOrEqual(12);
    assertAllContrast(baziRows, "bazi-pillars");
    for (const ganzhi of SAMPLE_GANZHI) {
      await expect(page.locator(".bazi-pillars strong", { hasText: ganzhi }).first()).toBeVisible();
    }

    // Life overview: same birth data, target year 2026.
    await page.goto("/life-overview");
    await page.getByRole("button", { name: "填入示例" }).click();
    await page.getByLabel("观察年份").fill("2026");
    await page.getByRole("button", { name: "生成我的人生总览" }).click();
    await page.locator(".life-result").waitFor({ state: "visible", timeout: 30000 });
    await page.waitForTimeout(400);
    const lifeRows = await measureCardText(page, ".life-pillars");
    expect(lifeRows.length).toBeGreaterThanOrEqual(12);
    assertAllContrast(lifeRows, "life-pillars");
    for (const ganzhi of SAMPLE_GANZHI) {
      await expect(page.locator(".life-pillars strong", { hasText: ganzhi }).first()).toBeVisible();
    }

    // Compatibility: two-person sample.
    await page.goto("/compatibility-structure");
    await page.getByRole("button", { name: "填入双人示例" }).click();
    await page.getByRole("button", { name: "生成双人结构" }).click();
    await page.locator(".compat-result").waitFor({ state: "visible", timeout: 30000 });
    await page.waitForTimeout(400);
    const compatRows = await measureCardText(page, ".compat-pillars");
    expect(compatRows.length).toBeGreaterThanOrEqual(12);
    assertAllContrast(compatRows, "compat-pillars");

    // No horizontal overflow on any of the three pages.
    expect(await page.evaluate(() => document.documentElement.scrollWidth > document.documentElement.clientWidth + 1)).toBe(false);
  });
}

test("romance spouse-pairing paragraph renders with a role and reads clearly", async ({ page }) => {
  await page.setViewportSize({ width: 360, height: 800 });
  await page.goto("/romance-structure");
  await page.getByRole("button", { name: "填入示例" }).click();
  await page.getByLabel("观察年份").fill("2026");
  // The pairing block only renders when a traditional_role is sent; the
  // sample fill does not set one, so select it explicitly.
  await page.getByLabel("传统配偶星口径（可选）").selectOption("female");
  await page.getByRole("button", { name: "查看桃花结构" }).click();
  await page.locator(".romance-result").waitFor({ state: "visible", timeout: 30000 });
  await page.locator(".romance-spouse-pairing").waitFor({ state: "visible", timeout: 10000 });
  await page.waitForTimeout(400);
  const pairingRows = await measureCardText(page, ".romance-spouse-pairing > p");
  expect(pairingRows.length).toBeGreaterThan(0);
  assertAllContrast(pairingRows, "romance-spouse-pairing");
  // The pairing paragraph names the candidate ten-gods and the flow year.
  await expect(page.locator(".romance-spouse-pairing > p").first()).toContainText("传统口径候选十神");
  expect(await page.evaluate(() => document.documentElement.scrollWidth > document.documentElement.clientWidth + 1)).toBe(false);
});

test("E0403 natal cards do not regress (romance + career + yearly)", async ({ page }) => {
  await page.setViewportSize({ width: 360, height: 800 });
  for (const [route, submit, result, card] of [
    ["/romance-structure", "查看桃花结构", ".romance-result", ".romance-natal"],
    ["/career-wealth-structure", "查看事业财运结构", ".career-result", ".career-natal"],
    ["/yearly-structure", "查看 2026 流年结构", ".yearly-result", ".yearly-natal"],
  ] as const) {
    await page.goto(route);
    await page.getByRole("button", { name: "填入示例" }).click();
    const year = page.getByLabel("观察年份");
    if (await year.count()) await year.fill("2026");
    await page.getByRole("button", { name: submit }).click();
    await page.locator(result).waitFor({ state: "visible", timeout: 30000 });
    await page.waitForTimeout(400);
    const rows = await measureCardText(page, card);
    expect(rows.length).toBeGreaterThan(0);
    assertAllContrast(rows, `${card} (E0403 no-regression)`);
  }
});

test("dark night headings keep gold (no reverse regression)", async ({ page }) => {
  await page.setViewportSize({ width: 360, height: 800 });
  // The life result-head h2 joins the four ganzhi on the DARK page
  // background; it must stay night gold, not the paper ink.
  await page.goto("/life-overview");
  await page.getByRole("button", { name: "填入示例" }).click();
  await page.getByLabel("观察年份").fill("2026");
  await page.getByRole("button", { name: "生成我的人生总览" }).click();
  await page.locator(".life-result").waitFor({ state: "visible", timeout: 30000 });
  const lifeH2 = await page.evaluate(() => {
    const el = document.querySelector(".life-result-head h2") as HTMLElement | null;
    return el ? getComputedStyle(el).color : null;
  });
  expect(lifeH2).toBe("rgb(240, 214, 160)");
  // Yearly result-head h2 is also a dark heading (E0403 guard, re-checked).
  await page.goto("/yearly-structure");
  await page.getByRole("button", { name: "填入示例" }).click();
  await page.getByRole("button", { name: "查看 2026 流年结构" }).click();
  await page.locator(".yearly-result").waitFor({ state: "visible", timeout: 30000 });
  const yearlyH2 = await page.evaluate(() => {
    const el = document.querySelector(".yearly-result-head h2") as HTMLElement | null;
    return el ? getComputedStyle(el).color : null;
  });
  expect(yearlyH2).toBe("rgb(240, 214, 160)");
});
