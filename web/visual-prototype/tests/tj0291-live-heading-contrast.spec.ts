/**
 * TJ-029.1 live-section / daily-section heading contrast (P1, E0402).
 *
 * LOCAL ONLY — real-backend acceptance. Requires a running backend on
 * 127.0.0.1:8000 with reviewed scenario data (production via the SSH tunnel
 * to tj-core-01, NOT the public repo checkout). This file is deliberately NOT
 * wired to any public CI workflow (workflows run specs by filename; none names
 * this file), so public CI never claims these results. Run locally with:
 *   npm test -- tests/tj0291-live-heading-contrast.spec.ts
 *
 * What it proves: the section headings (h2, numeral, small) inside the light
 * result cards (.live-section on yearly/romance/career, .daily-section on
 * daily) are actually readable — WCAG AA contrast >= 4.5:1 against their
 * effective (composited) background — at 360/390/768/1440px.
 * Before the fix the h2 inherited night gold #f0d6a0 with no color rule and
 * read 1.39:1 on the opaque paper card; the numeral #a8864e read 3.34:1 and
 * the small #889078 read 3.27:1. The fix pins dark ink on these cards only
 * (public.css, scoped to .live-section / .daily-section), reusing the
 * E0400/E0401 verified palette (#315943 / #7d6033 / #6b7264).
 * Dark backgrounds are untouched: headings outside light cards keep night
 * gold, verified by the dark-area guard below.
 */
import { expect, test, type Page } from "@playwright/test";

/** WCAG contrast from computed text color + composited effective background. */
async function contrastOf(page: Page, selector: string): Promise<number | null> {
  const m = await page.evaluate((sel) => {
    const el = document.querySelector(sel);
    if (!el) return null;
    const color = getComputedStyle(el).color;
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
      const mm = chain[i].match(/rgba?\(([^)]+)\)/);
      if (!mm) continue;
      const p = mm[1].split(",").map((x) => parseFloat(x));
      const a = p.length > 3 ? p[3] : 1;
      if (a > 0) {
        acc = {
          r: p[0] * a + acc.r * (1 - a),
          g: p[1] * a + acc.g * (1 - a),
          b: p[2] * a + acc.b * (1 - a),
        };
      }
    }
    const parse = (s: string) => {
      const parts = s.match(/rgba?\(([^)]+)\)/)![1].split(",").map((x) => parseFloat(x));
      return { r: parts[0], g: parts[1], b: parts[2] };
    };
    const lum = (c: { r: number; g: number; b: number }) => {
      const f = (v: number) => {
        v /= 255;
        return v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4);
      };
      return 0.2126 * f(c.r) + 0.7152 * f(c.g) + 0.0722 * f(c.b);
    };
    const fg = parse(color);
    const l1 = lum(fg), l2 = lum(acc);
    return (Math.max(l1, l2) + 0.05) / (Math.min(l1, l2) + 0.05);
  }, selector);
  return m;
}

async function assertContrast(page: Page, selector: string, min = 4.5) {
  const ratio = await contrastOf(page, selector);
  expect(ratio, `element not found: ${selector}`).not.toBeNull();
  expect(ratio as number, `${selector} contrast ${(ratio as number).toFixed(2)}:1 < ${min}:1`).toBeGreaterThanOrEqual(min);
}

async function submitSample(page: Page, route: string, submitName: string, resultSelector: string, yearLabel?: string) {
  await page.goto(route);
  await page.getByRole("button", { name: "填入示例" }).click();
  if (yearLabel) await page.getByLabel(yearLabel).fill("2026");
  await page.getByRole("button", { name: submitName }).click();
  await page.locator(resultSelector).waitFor({ state: "visible", timeout: 30000 });
  await page.waitForTimeout(400);
}

async function assertNoOverflow(page: Page, tag: string) {
  const o = await page.evaluate(() => ({
    scrollWidth: document.documentElement.scrollWidth,
    clientWidth: document.documentElement.clientWidth,
  }));
  expect(o.scrollWidth, `${tag}: horizontal overflow (scrollWidth ${o.scrollWidth} > clientWidth ${o.clientWidth})`).toBeLessThanOrEqual(o.clientWidth);
}

/** All section headings inside .live-section on a page (h2 + numeral). */
async function assertLiveHeadings(page: Page) {
  await expect(page.locator(".live-section .result-section-heading h2").first()).toBeVisible();
  await expect(page.locator(".live-section .result-section-heading h2").first()).not.toBeEmpty();
  await assertContrast(page, ".live-section .result-section-heading h2");
  await assertContrast(page, ".live-section .result-section-heading > div > span");
}

/** All section headings inside .daily-section (h2 + numeral + small). */
async function assertDailyHeadings(page: Page) {
  await expect(page.locator(".daily-section .result-section-heading h2").first()).toBeVisible();
  await expect(page.locator(".daily-section .result-section-heading h2").first()).not.toBeEmpty();
  await assertContrast(page, ".daily-section .result-section-heading h2");
  await assertContrast(page, ".daily-section .result-section-heading > div > span");
  await assertContrast(page, ".daily-section .result-section-heading > small");
}

const AA = 4.5;

test("live-section headings read at AA (360px phone)", async ({ page }) => {
  await page.setViewportSize({ width: 360, height: 800 });
  await submitSample(page, "/yearly-structure", "查看 2026 流年结构", ".yearly-result");
  await assertLiveHeadings(page);
  await assertNoOverflow(page, "yearly 360px");
  await submitSample(page, "/romance-structure", "查看桃花结构", ".romance-result", "观察年份");
  await assertLiveHeadings(page);
  await assertNoOverflow(page, "romance 360px");
  await submitSample(page, "/career-wealth-structure", "查看事业财运结构", ".career-result", "观察年份");
  await assertLiveHeadings(page);
  await assertNoOverflow(page, "career 360px");
});

test("daily-section headings read at AA (360px phone)", async ({ page }) => {
  await page.setViewportSize({ width: 360, height: 800 });
  await submitSample(page, "/daily-structure", "查看今日结构", ".daily-result");
  await assertDailyHeadings(page);
  await assertNoOverflow(page, "daily 360px");
});

test("live-section headings read at AA (390px phone)", async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await submitSample(page, "/yearly-structure", "查看 2026 流年结构", ".yearly-result");
  await assertLiveHeadings(page);
  await assertNoOverflow(page, "yearly 390px");
  await submitSample(page, "/romance-structure", "查看桃花结构", ".romance-result", "观察年份");
  await assertLiveHeadings(page);
  await assertNoOverflow(page, "romance 390px");
  await submitSample(page, "/career-wealth-structure", "查看事业财运结构", ".career-result", "观察年份");
  await assertLiveHeadings(page);
  await assertNoOverflow(page, "career 390px");
  await submitSample(page, "/daily-structure", "查看今日结构", ".daily-result");
  await assertDailyHeadings(page);
  await assertNoOverflow(page, "daily 390px");
});

test("live-section headings read at AA (768px tablet)", async ({ page }) => {
  await page.setViewportSize({ width: 768, height: 1024 });
  await submitSample(page, "/yearly-structure", "查看 2026 流年结构", ".yearly-result");
  await assertLiveHeadings(page);
  await assertNoOverflow(page, "yearly 768px");
  await submitSample(page, "/romance-structure", "查看桃花结构", ".romance-result", "观察年份");
  await assertLiveHeadings(page);
  await assertNoOverflow(page, "romance 768px");
  await submitSample(page, "/career-wealth-structure", "查看事业财运结构", ".career-result", "观察年份");
  await assertLiveHeadings(page);
  await assertNoOverflow(page, "career 768px");
  await submitSample(page, "/daily-structure", "查看今日结构", ".daily-result");
  await assertDailyHeadings(page);
  await assertNoOverflow(page, "daily 768px");
});

test("live-section headings read at AA (1440px desktop)", async ({ page }) => {
  await page.setViewportSize({ width: 1440, height: 900 });
  await submitSample(page, "/yearly-structure", "查看 2026 流年结构", ".yearly-result");
  await assertLiveHeadings(page);
  await assertNoOverflow(page, "yearly 1440px");
  await submitSample(page, "/romance-structure", "查看桃花结构", ".romance-result", "观察年份");
  await assertLiveHeadings(page);
  await assertNoOverflow(page, "romance 1440px");
  await submitSample(page, "/career-wealth-structure", "查看事业财运结构", ".career-result", "观察年份");
  await assertLiveHeadings(page);
  await assertNoOverflow(page, "career 1440px");
  await submitSample(page, "/daily-structure", "查看今日结构", ".daily-result");
  await assertDailyHeadings(page);
  await assertNoOverflow(page, "daily 1440px");
});

test("E0400/E0401 no regression + dark-area headings stay light (360px)", async ({ page }) => {
  await page.setViewportSize({ width: 360, height: 800 });
  // E0400: evidence quote and boundary text on yearly.
  await submitSample(page, "/yearly-structure", "查看 2026 流年结构", ".yearly-result");
  expect(await contrastOf(page, ".live-evidence blockquote")).toBeGreaterThanOrEqual(AA);
  expect(await contrastOf(page, ".yearly-limits p")).toBeGreaterThanOrEqual(AA);
  // E0401: yearly rule list.
  expect(await contrastOf(page, ".yearly-rule article p")).toBeGreaterThanOrEqual(AA);
  expect(await contrastOf(page, ".yearly-rule .result-section-heading h2")).toBeGreaterThanOrEqual(AA);
  // Dark-area guard: the result page title sits on the dark night background
  // (not inside a light card) and must keep night gold, not flip to dark ink.
  const titleColor = await page.evaluate(() => {
    const el = document.querySelector(".yearly-result-head h2");
    return el ? getComputedStyle(el).color : null;
  });
  expect(titleColor, "yearly result title should stay night gold").toBe("rgb(240, 214, 160)");
  expect(await contrastOf(page, ".yearly-result-head h2")).toBeGreaterThanOrEqual(AA);
  await assertNoOverflow(page, "yearly 360px guard");
});
