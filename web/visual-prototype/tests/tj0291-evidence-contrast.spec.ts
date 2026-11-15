/**
 * TJ-029.1 evidence/boundary contrast (P1, E0400).
 *
 * LOCAL ONLY — real-backend acceptance. Requires a running backend on
 * 127.0.0.1:8000 with reviewed scenario data (production via the SSH tunnel
 * to tj-core-01, NOT the public repo checkout). This file is deliberately NOT
 * wired to any public CI workflow (workflows run specs by filename; none names
 * this file), so public CI never claims these results. Run locally with:
 *   npm test -- tests/tj0291-evidence-contrast.spec.ts
 *
 * What it proves: the classical-source quotes ("典籍依据") and boundary body
 * text ("当前不能说什么" / "边界与下一步" / "当前不能下的结论") on the
 * structure result pages are actually readable — WCAG AA contrast >= 4.5:1
 * against their effective (composited) background — at desktop and 360px.
 * Before the fix the same measurement read ~1.0:1 (yearly/romance/career
 * quotes) and ~1.99:1 (daily quotes): the semi-transparent card
 * (#fffdf66b over the dark page) composited to nearly the text color.
 */
import { expect, test, type Page } from "@playwright/test";

/** WCAG contrast from computed text color + composited effective background. */
async function contrastOf(page: Page, selector: string): Promise<number> {
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
  expect(m, `element not found: ${selector}`).not.toBeNull();
  return m as number;
}

async function submitSample(page: Page, route: string, submitName: string, resultSelector: string, yearLabel?: string) {
  await page.goto(route);
  await page.getByRole("button", { name: "填入示例" }).click();
  if (yearLabel) await page.getByLabel(yearLabel).fill("2026");
  await page.getByRole("button", { name: submitName }).click();
  await page.locator(resultSelector).waitFor({ state: "visible", timeout: 30000 });
  await expect(page.locator(".live-evidence blockquote").first()).toBeVisible();
}

const AA = 4.5;

test("yearly evidence quote and boundary text read at AA (desktop)", async ({ page }) => {
  await submitSample(page, "/yearly-structure", "查看 2026 流年结构", ".yearly-result");
  expect(await contrastOf(page, ".live-evidence blockquote")).toBeGreaterThanOrEqual(AA);
  expect(await contrastOf(page, ".yearly-limits p")).toBeGreaterThanOrEqual(AA);
  expect(await contrastOf(page, ".yearly-limits .live-warning")).toBeGreaterThanOrEqual(AA);
  expect(await contrastOf(page, ".live-evidence small")).toBeGreaterThanOrEqual(AA);
});

test("romance evidence quote and boundary text read at AA (desktop)", async ({ page }) => {
  await submitSample(page, "/romance-structure", "查看桃花结构", ".romance-result", "观察年份");
  expect(await contrastOf(page, ".live-evidence blockquote")).toBeGreaterThanOrEqual(AA);
  expect(await contrastOf(page, ".romance-limits p")).toBeGreaterThanOrEqual(AA);
  expect(await contrastOf(page, ".romance-limits .live-warning")).toBeGreaterThanOrEqual(AA);
  expect(await contrastOf(page, ".live-evidence small")).toBeGreaterThanOrEqual(AA);
});

test("career evidence quote and boundary text read at AA (desktop)", async ({ page }) => {
  await submitSample(page, "/career-wealth-structure", "查看事业财运结构", ".career-result", "观察年份");
  expect(await contrastOf(page, ".live-evidence blockquote")).toBeGreaterThanOrEqual(AA);
  expect(await contrastOf(page, ".career-limits p")).toBeGreaterThanOrEqual(AA);
  expect(await contrastOf(page, ".career-limits .live-warning")).toBeGreaterThanOrEqual(AA);
});

test("daily evidence quote reads at AA (desktop)", async ({ page }) => {
  await submitSample(page, "/daily-structure", "查看今日结构", ".daily-result");
  expect(await contrastOf(page, ".live-evidence blockquote")).toBeGreaterThanOrEqual(AA);
  expect(await contrastOf(page, ".live-evidence small")).toBeGreaterThanOrEqual(AA);
});

test("evidence quote and boundary text read at AA (360px)", async ({ page }) => {
  await page.setViewportSize({ width: 360, height: 800 });
  await submitSample(page, "/yearly-structure", "查看 2026 流年结构", ".yearly-result");
  expect(await contrastOf(page, ".live-evidence blockquote")).toBeGreaterThanOrEqual(AA);
  expect(await contrastOf(page, ".yearly-limits p")).toBeGreaterThanOrEqual(AA);
  await submitSample(page, "/romance-structure", "查看桃花结构", ".romance-result", "观察年份");
  expect(await contrastOf(page, ".live-evidence blockquote")).toBeGreaterThanOrEqual(AA);
  expect(await contrastOf(page, ".romance-limits p")).toBeGreaterThanOrEqual(AA);
  await submitSample(page, "/career-wealth-structure", "查看事业财运结构", ".career-result", "观察年份");
  expect(await contrastOf(page, ".live-evidence blockquote")).toBeGreaterThanOrEqual(AA);
  expect(await contrastOf(page, ".career-limits p")).toBeGreaterThanOrEqual(AA);
  await submitSample(page, "/daily-structure", "查看今日结构", ".daily-result");
  expect(await contrastOf(page, ".live-evidence blockquote")).toBeGreaterThanOrEqual(AA);
});

test("bazi tiaohou/bingyao quote stays readable (control, desktop)", async ({ page }) => {
  await page.goto("/bazi-profile");
  await page.getByRole("button", { name: "填入示例" }).click();
  await page.getByRole("button", { name: "生成基础档案" }).click();
  await page.locator(".bazi-evidence-entry").first().waitFor({ state: "attached", timeout: 30000 });
  await page.evaluate(() => {
    const det = document.querySelector(".bazi-evidence-entry");
    const summary = det && det.querySelector("summary");
    if (summary) (summary as HTMLElement).click();
  });
  await page.waitForTimeout(400);
  expect(await contrastOf(page, ".bazi-evidence-entry blockquote")).toBeGreaterThanOrEqual(AA);
});
