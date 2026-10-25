import { test, expect } from "@playwright/test";

/** B008 / TJ-021.3: dream page readability + private-text non-render contract.
 * REAL CHROMIUM with CONTROLLED HTTP fixtures.
 * This is a frontend rendering contract test, NOT real dream-backend
 * computation or private Canonical/Evidence acceptance. The API response
 * is synthetic; what it proves is presentation: at 390px the rendered
 * result text is readable, and the page renders ONLY the short quotes
 * from the response, never a full private passage.
 */
const DREAM_API = "**/api/v1/dream/culture";

const STUB_RESPONSE = {
  api_version: "v1",
  status: "reviewed_cultural_matches",
  public_release: true,
  cultural_reference_only: true,
  ai_enabled: false,
  personal_prediction: false,
  matches: [
    {
      scene: "蛇咬人",
      matched_texts: ["蛇咬住我的手"],
      cultural_reading: "传统典籍中蛇咬多与得财相关，此处仅作文化参考，不预测现实得失。",
      short_quote: "蛇咬人主得大财",
      source_title: "周公解梦",
      evidence_level: "已审核",
    },
    {
      scene: "拾得钱物",
      matched_texts: ["捡到了钱"],
      cultural_reading: "拾钱场景在典籍中有吉语，同样只作文化参考。",
      short_quote: "拾得钱物皆大吉",
      source_title: "周公解梦",
      evidence_level: "已审核",
    },
  ],
  unreviewed_topics: [],
  notice: "以上为传统文化参考，不构成对现实的预测。",
};

test.beforeEach(async ({ page }) => {
  await page.route(DREAM_API, async (route) => {
    await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify(STUB_RESPONSE) });
  });
});

test("dream result at 390px is readable and renders only short quotes", async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  const adminRequests: string[] = [];
  page.on("request", (req) => {
    if (new URL(req.url()).pathname.startsWith("/api/v1/admin/")) adminRequests.push(req.url());
  });

  await page.goto("/dream-culture");
  await page.getByLabel("梦境叙述").fill("我梦见一条蛇咬住我的手，接着我梦见捡到了钱");
  await page.locator('form button[type="submit"]').first().click();
  await expect(page.locator(".dream-culture-results")).toBeVisible();
  await expect(page.locator(".dream-culture-match")).toHaveCount(2);

  // --- Readability: computed font-size, line-height ratio, WCAG contrast ---
  // Contrast uses alpha compositing: semi-transparent card backgrounds are
  // blended with every ancestor layer down to an opaque base, so the ratio
  // reflects what the user actually sees (not the naive opaque assumption).
  const readability = await page.evaluate(() => {
    function parseRgb(rgb: string): [number, number, number, number] {
      const m = rgb.match(/rgba?\((\d+),\s*(\d+),\s*(\d+)(?:,\s*([\d.]+))?/);
      if (!m) return [0, 0, 0, 1];
      return [Number(m[1]), Number(m[2]), Number(m[3]), m[4] === undefined ? 1 : Number(m[4])];
    }
    function luminance(r: number, g: number, b: number): number {
      const [lr, lg, lb] = [r, g, b].map((v) => {
        const s = v / 255;
        return s <= 0.03928 ? s / 12.92 : Math.pow((s + 0.055) / 1.055, 2.4);
      });
      return 0.2126 * lr + 0.7152 * lg + 0.0722 * lb;
    }
    function effectiveBackground(el: Element): [number, number, number] {
      // Collect background layers from the element up to <html>.
      const layers: [number, number, number, number][] = [];
      let node: Element | null = el;
      while (node) {
        const bg = getComputedStyle(node).backgroundColor;
        if (bg && bg !== "rgba(0, 0, 0, 0)") layers.push(parseRgb(bg));
        node = node.parentElement;
      }
      // Composite top-down onto opaque white (page base fallback).
      let [r, g, b] = [255, 255, 255];
      for (let i = layers.length - 1; i >= 0; i--) {
        const [lr, lg, lb, a] = layers[i];
        r = lr * a + r * (1 - a);
        g = lg * a + g * (1 - a);
        b = lb * a + b * (1 - a);
      }
      return [r, g, b];
    }
    const rows: { tag: string; fontSize: number; lineHeightRatio: number; contrast: number }[] = [];
    document.querySelectorAll(".dream-culture-match p, .dream-culture-match blockquote").forEach((el) => {
      const cs = getComputedStyle(el);
      const fontSize = parseFloat(cs.fontSize);
      const lineHeight = cs.lineHeight === "normal" ? fontSize * 1.4 : parseFloat(cs.lineHeight);
      const [fr, fg, fb] = parseRgb(cs.color);
      const [br, bg, bb] = effectiveBackground(el);
      const l1 = luminance(fr, fg, fb);
      const l2 = luminance(br, bg, bb);
      const [hi, lo] = l1 >= l2 ? [l1, l2] : [l2, l1];
      rows.push({
        tag: el.tagName.toLowerCase(),
        fontSize,
        lineHeightRatio: lineHeight / fontSize,
        contrast: (hi + 0.05) / (lo + 0.05),
      });
    });
    return rows;
  });
  expect(readability.length).toBeGreaterThan(0);
  for (const row of readability) {
    expect(row.fontSize, `${row.tag} font-size`).toBeGreaterThanOrEqual(14);
    expect(row.lineHeightRatio, `${row.tag} line-height ratio`).toBeGreaterThanOrEqual(1.4);
    expect(row.contrast, `${row.tag} contrast`).toBeGreaterThanOrEqual(4.5);
  }

  // --- Privacy: only short quotes render, never a full passage ---
  const quotes = await page.locator(".dream-culture-match blockquote").allTextContents();
  expect(quotes).toHaveLength(2);
  const expected = STUB_RESPONSE.matches.map((m) => m.short_quote);
  for (let i = 0; i < quotes.length; i++) {
    const rendered = quotes[i].replace(/[“”]/g, "").trim();
    expect(rendered, `blockquote ${i} must equal exactly the stub short_quote`).toBe(expected[i]);
    expect(rendered.length, `blockquote ${i} must be a short quote, not a passage`).toBeLessThanOrEqual(200);
  }
  // No element in the result may carry a long passage-like text node.
  const longNodes = await page.evaluate(() => {
    const out: string[] = [];
    document.querySelectorAll(".dream-culture-results p, .dream-culture-results blockquote, .dream-culture-results li").forEach((el) => {
      const text = (el.textContent || "").trim();
      if (text.length > 500) out.push(text.slice(0, 80));
    });
    return out;
  });
  expect(longNodes, "no passage-length text node may render in the dream result").toEqual([]);
  expect(adminRequests, "no private admin endpoint may be requested").toEqual([]);
  expect(
    await page.evaluate(() => Object.keys(localStorage).filter((k) => /dream|token/i.test(k))),
    "no dream/token keys may be stored",
  ).toEqual([]);

  // --- No horizontal overflow at 390px ---
  await expect
    .poll(() => page.evaluate(() => document.documentElement.scrollWidth <= document.documentElement.clientWidth))
    .toBe(true);
});
