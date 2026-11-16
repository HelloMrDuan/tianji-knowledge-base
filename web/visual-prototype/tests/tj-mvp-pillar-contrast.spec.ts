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
 *
 * HOLD fix (ChatGPT #578 review): the first version of measureCardText
 * skipped any element with children (el.children.length > 0), so the
 * plain text of a <p> containing a nested <strong> and the direct text of
 * a <span> containing an <i> were never measured. This version measures
 * visible TEXT NODES (TreeWalker, SHOW_TEXT): each text node's parent
 * element supplies the computed color, so a <p>'s direct text and its
 * nested <strong> are measured separately and neither is double-counted
 * (a text node belongs to exactly one parent, and the parent's
 * textContent is never used). The horizontal-overflow check now runs
 * immediately after each page renders, at every viewport, instead of
 * once at the end of the loop.
 */
import { test, expect, type Page } from "@playwright/test";

const MIN_RATIO = 4.5;

type NodeRow = { sel: string; parentTag: string; text: string; ratio: number };

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
    // Effective background for a text node: composite the background
    // colors from its parent element up through the ancestors (outermost
    // first), starting from white. Transparent layers blend with what is
    // below; the innermost opaque layer wins.
    const effectiveBg = (el: Element) => {
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
      return acc;
    };
    const isVisible = (el: Element) => {
      const cs = getComputedStyle(el);
      if (cs.display === "none" || cs.visibility === "hidden") return false;
      return true;
    };
    const rows: NodeRow[] = [];
    const seen = new Set<string>();
    for (const card of Array.from(document.querySelectorAll(sel))) {
      const walker = document.createTreeWalker(card, NodeFilter.SHOW_TEXT);
      let node: Text | null;
      while ((node = walker.nextNode() as Text | null)) {
        const text = (node.nodeValue || "").trim();
        if (!text) continue;
        const parent = node.parentElement;
        if (!parent) continue;
        if (!isVisible(parent)) continue;
        // Skip text that is not actually rendered (e.g. inside a closed
        // <details>): its range has a zero box.
        const range = document.createRange();
        range.selectNodeContents(node);
        const rect = range.getBoundingClientRect();
        if (rect.width === 0 && rect.height === 0) continue;
        const color = parse(getComputedStyle(parent).color);
        if (!color) continue;
        const bg = effectiveBg(parent);
        const l1 = lum(color), l2 = lum(bg);
        const ratio = (Math.max(l1, l2) + 0.05) / (Math.min(l1, l2) + 0.05);
        let path = parent.tagName.toLowerCase();
        const cls = (parent.getAttribute("class") || "").split(" ")[0];
        if (cls) path += "." + cls;
        const rounded = Math.round(ratio * 100) / 100;
        // Dedupe identical (parent, text, ratio) measurements so the same
        // rendered text is not counted twice; a different ratio (different
        // background) is a different measurement and is kept.
        const key = `${path}|${text}|${rounded}`;
        if (seen.has(key)) continue;
        seen.add(key);
        rows.push({ sel: path, parentTag: parent.tagName.toLowerCase(), text: text.slice(0, 40), ratio: rounded });
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

// Assert that both the plain (direct) text of a container and its nested
// styled text were actually measured — a test must not pass with an empty
// plain-text set. plainTags are the container tags whose direct text must
// appear (e.g. "p" for the romance paragraph, "span" for a bazi-branch
// span); nestedTags are the nested styled tags (e.g. "strong", "i").
function assertPlainAndNested(rows: NodeRow[], pageName: string, plainTags: string[], nestedTags: string[]) {
  for (const tag of plainTags) {
    const found = rows.filter((r) => r.parentTag === tag);
    expect(found.length, `${pageName}: expected plain text under <${tag}> to be measured, got none`).toBeGreaterThan(0);
    const failing = found.filter((r) => r.ratio < MIN_RATIO);
    expect(failing, `${pageName}: plain <${tag}> text failing: ${JSON.stringify(failing)}`).toEqual([]);
  }
  for (const tag of nestedTags) {
    const found = rows.filter((r) => r.parentTag === tag);
    expect(found.length, `${pageName}: expected nested <${tag}> text to be measured, got none`).toBeGreaterThan(0);
    const failing = found.filter((r) => r.ratio < MIN_RATIO);
    expect(failing, `${pageName}: nested <${tag}> text failing: ${JSON.stringify(failing)}`).toEqual([]);
  }
}

async function assertNoOverflow(page: Page, pageName: string) {
  const dims = await page.evaluate(() => {
    const de = document.documentElement;
    return { scrollWidth: de.scrollWidth, clientWidth: de.clientWidth };
  });
  expect(
    dims.scrollWidth <= dims.clientWidth + 1,
    `${pageName}: horizontal overflow (scrollWidth ${dims.scrollWidth} > clientWidth ${dims.clientWidth})`,
  ).toBe(true);
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
    // The bazi-branch span holds direct text plus a nested <i>; both must
    // be measured (the old element-based measurement skipped the span).
    assertPlainAndNested(baziRows, "bazi-pillars", ["span"], ["strong", "i"]);
    for (const ganzhi of SAMPLE_GANZHI) {
      await expect(page.locator(".bazi-pillars strong", { hasText: ganzhi }).first()).toBeVisible();
    }
    await assertNoOverflow(page, `bazi-profile @${width}px`);

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
    assertPlainAndNested(lifeRows, "life-pillars", ["small", "em"], ["strong"]);
    for (const ganzhi of SAMPLE_GANZHI) {
      await expect(page.locator(".life-pillars strong", { hasText: ganzhi }).first()).toBeVisible();
    }
    await assertNoOverflow(page, `life-overview @${width}px`);

    // Compatibility: two-person sample.
    await page.goto("/compatibility-structure");
    await page.getByRole("button", { name: "填入双人示例" }).click();
    await page.getByRole("button", { name: "生成双人结构" }).click();
    await page.locator(".compat-result").waitFor({ state: "visible", timeout: 30000 });
    await page.waitForTimeout(400);
    const compatRows = await measureCardText(page, ".compat-pillars");
    expect(compatRows.length).toBeGreaterThanOrEqual(12);
    assertAllContrast(compatRows, "compat-pillars");
    assertPlainAndNested(compatRows, "compat-pillars", ["small", "span"], ["strong"]);
    await assertNoOverflow(page, `compatibility-structure @${width}px`);
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
  // The paragraph's plain text ("传统口径候选十神……流年干支") lives in
  // direct text nodes of the <p> alongside a nested <strong>; both must
  // be measured (the old measurement skipped the <p> entirely).
  assertPlainAndNested(pairingRows, "romance-spouse-pairing", ["p"], ["strong"]);
  // The pairing paragraph names the candidate ten-gods and the flow year.
  await expect(page.locator(".romance-spouse-pairing > p").first()).toContainText("传统口径候选十神");
  await assertNoOverflow(page, "romance-structure @360px");
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
    await assertNoOverflow(page, `${route} @360px`);
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
