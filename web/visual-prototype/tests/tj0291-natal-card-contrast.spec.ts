/**
 * TJ-029.1 E0403: natal-card readability (romance / career / yearly).
 *
 * Local-only: needs a real backend (vite proxies /api + /health to it).
 * Base URL is the vite dev server on port 4174. Do not add to public CI.
 *
 * Failing state before the fix (real backend, 360px, every visible text node
 * inside the natal cards measured):
 *  - .romance-natal / .career-natal background #fffdf7a6 (semi-transparent):
 *    effective bg rgb(170,174,173); heading h2 inherited night gold 1.58:1,
 *    numeral 1.52:1, heading small 1.49:1.
 *  - Pillar ganzhi <strong> has no color rule, inherits night gold:
 *    romance/career 1.25-1.40:1, yearly 1.39:1.
 *  - Pillar labels #8e9386 / #8b9384: 2.78-3.13:1.
 *  - Romance spouse-hits span "子 ↔ 午" inherits gold: 1.35:1; rule id
 *    #85817a: 3.69:1; boundary #84776c: 1.94:1; palace strongs #7f5349: 2.90:1.
 *  - Yearly eyebrow var(--gold) #e2bb79: 1.73:1.
 * Fix: opaque card backgrounds + explicit dark ink (h2 #315943, numeral
 * #7d6033, heading small #6b7264, pillar labels #5a6b5c, pillar ganzhi
 * #315943, hits span #315943, rule id #6b7264, boundary #5a6b5c, eyebrow
 * #7d6033). Pillar labels use #5a6b5c, not #6b7264: #6b7264 scores
 * 4.40-4.41:1 on the day-pillar cells (#f0f2e9 / #eff2e8) and would fail.
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

async function submitSample(page: Page, route: string, submitName: string, resultSelector: string) {
  await page.goto(route);
  await page.getByRole("button", { name: "填入示例" }).click();
  const year = page.getByLabel("观察年份");
  if (await year.count()) await year.fill("2026");
  await page.getByRole("button", { name: submitName }).click();
  await page.locator(resultSelector).waitFor({ state: "visible", timeout: 30000 });
  await page.waitForTimeout(400);
}

function assertAllContrast(rows: NodeRow[], pageName: string) {
  expect(rows.length, `${pageName}: natal card must contain visible text`).toBeGreaterThan(0);
  const failing = rows.filter((r) => r.ratio < MIN_RATIO);
  expect(failing, `${pageName}: failing text nodes: ${JSON.stringify(failing)}`).toEqual([]);
}

for (const width of [360, 390, 768, 1440]) {
  test(`natal cards readable at ${width}px (romance + career + yearly)`, async ({ page }) => {
    await page.setViewportSize({ width, height: 800 });
    await submitSample(page, "/romance-structure", "查看桃花结构", ".romance-result");
    const romanceRows = await measureCardText(page, ".romance-natal");
    expect(romanceRows.length).toBeGreaterThanOrEqual(20);
    assertAllContrast(romanceRows, "romance");
    // The four pillars must be present and their ganzhi visible.
    for (const ganzhi of ["己卯", "丁丑", "甲子", "庚午"]) {
      await expect(page.locator(".romance-pillars strong", { hasText: ganzhi }).first()).toBeVisible();
    }
    await submitSample(page, "/career-wealth-structure", "查看事业财运结构", ".career-result");
    const careerRows = await measureCardText(page, ".career-natal");
    expect(careerRows.length).toBeGreaterThanOrEqual(12);
    assertAllContrast(careerRows, "career");
    for (const ganzhi of ["己卯", "丁丑", "甲子", "庚午"]) {
      await expect(page.locator(".career-pillars strong", { hasText: ganzhi }).first()).toBeVisible();
    }
    await submitSample(page, "/yearly-structure", "查看 2026 流年结构", ".yearly-result");
    const yearlyRows = await measureCardText(page, ".yearly-natal");
    expect(yearlyRows.length).toBeGreaterThanOrEqual(10);
    assertAllContrast(yearlyRows, "yearly");
    // No horizontal overflow on any of the three pages.
    expect(await page.evaluate(() => document.documentElement.scrollWidth > document.documentElement.clientWidth + 1)).toBe(false);
  });
}

test("E0401 yearly-rule contrast does not regress (E0400 is re-run as its own spec)", async ({ page }) => {
  await page.setViewportSize({ width: 360, height: 800 });
  await submitSample(page, "/yearly-structure", "查看 2026 流年结构", ".yearly-result");
  const ruleRows = await measureCardText(page, ".yearly-rule");
  expect(ruleRows.length).toBeGreaterThan(0);
  assertAllContrast(ruleRows, "yearly-rule (E0401)");
});

test("dark night areas keep light headings (no reverse regression)", async ({ page }) => {
  await page.setViewportSize({ width: 360, height: 800 });
  await submitSample(page, "/yearly-structure", "查看 2026 流年结构", ".yearly-result");
  const color = await page.evaluate(() => {
    const el = document.querySelector(".yearly-result-head h2") as HTMLElement | null;
    return el ? getComputedStyle(el).color : null;
  });
  expect(color).toBe("rgb(240, 214, 160)");
});
