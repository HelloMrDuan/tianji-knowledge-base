/**
 * TJ-029.1 yearly rule-list contrast (P1, E0401).
 *
 * LOCAL ONLY — real-backend acceptance. Requires a running backend on
 * 127.0.0.1:8000 with reviewed scenario data (production via the SSH tunnel
 * to tj-core-01, NOT the public repo checkout). This file is deliberately NOT
 * wired to any public CI workflow (workflows run specs by filename; none names
 * this file), so public CI never claims these results. Run locally with:
 *   npm test -- tests/tj0291-yearly-rule-contrast.spec.ts
 *
 * What it proves: the rule list on /yearly-structure (`.yearly-rule`) is
 * actually readable — WCAG AA contrast >= 4.5:1 against its effective
 * (composited) background — at 360px, 390px, 768px and 1440px.
 *
 * Root cause (E0400 did not cover this card): `.yearly-rule` used
 * `background:#fffdf66b` (alpha 0.42) over the dark night page (#0b1c23),
 * compositing to rgb(113,123,124); the rule body text #526a58 then read
 * 1.35:1. The fix makes the card opaque (#fffdf6) and darkens the text
 * colors that still fail on the light card (gold-inherited headings and
 * rule ids, #92998c small text, #748273 boundary note).
 * Before the fix the same measurement read 1.08:1–3.09:1 for the 10 failing
 * elements; after the fix all read >= 4.5:1.
 * The daily branch list, romance and career rule content were checked with
 * the same measurement and do NOT share this root cause (their cards are
 * opaque after E0400); this file asserts they stay readable as a guard.
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

async function submitYearly(page: Page) {
  await page.goto("/yearly-structure");
  await page.getByRole("button", { name: "填入示例" }).click();
  await page.getByRole("button", { name: "查看 2026 流年结构" }).click();
  await page.locator(".yearly-result").waitFor({ state: "visible", timeout: 30000 });
  await expect(page.locator(".yearly-rule").first()).toBeVisible();
  await page.waitForTimeout(300);
}

async function assertNoOverflow(page: Page, tag: string) {
  const o = await page.evaluate(() => ({
    scrollWidth: document.documentElement.scrollWidth,
    clientWidth: document.documentElement.clientWidth,
  }));
  expect(o.scrollWidth, `${tag}: horizontal overflow (scrollWidth ${o.scrollWidth} > clientWidth ${o.clientWidth})`).toBeLessThanOrEqual(o.clientWidth);
}

/** All rule-list text inside .yearly-rule at the current viewport. */
async function assertYearlyRuleList(page: Page) {
  // Rule content is present and non-empty (not hidden or deleted to pass).
  await expect(page.locator(".yearly-rule article p").first()).not.toBeEmpty();
  await expect(page.locator(".yearly-branch-summary")).not.toBeEmpty();
  await expect(page.locator(".yearly-branch-boundary")).toContainText("仅展示已核验的成对结构");
  // Section headings inside the rule card.
  await assertContrast(page, ".yearly-rule .result-section-heading h2");
  await assertContrast(page, ".yearly-rule .result-section-heading > div > span");
  // Rule rows: id, body, source note.
  await assertContrast(page, ".yearly-rule article strong");
  await assertContrast(page, ".yearly-rule article p");
  await assertContrast(page, ".yearly-rule article small");
  // Branch relation summary.
  await assertContrast(page, ".yearly-branch-summary");
  await assertContrast(page, ".yearly-branch-summary strong");
  // Branch hits (or the no-hit note when the sample has none).
  if (await page.locator(".yearly-branch-hit").count()) {
    await assertContrast(page, ".yearly-branch-hit > span");
    await assertContrast(page, ".yearly-branch-hit > strong");
    await assertContrast(page, ".yearly-branch-hit p");
    await assertContrast(page, ".yearly-branch-hit small");
    await assertContrast(page, ".yearly-branch-sources summary");
    await assertContrast(page, ".yearly-branch-source p");
    await assertContrast(page, ".yearly-branch-source blockquote");
    if (await page.locator(".yearly-branch-evidence-missing").count()) {
      await assertContrast(page, ".yearly-branch-evidence-missing");
    }
  } else {
    await assertContrast(page, ".yearly-branch-no-hit");
  }
  // Boundary note.
  await assertContrast(page, ".yearly-branch-boundary");
}

const AA = 4.5;

test("yearly rule list reads at AA (360px phone)", async ({ page }) => {
  await page.setViewportSize({ width: 360, height: 800 });
  await submitYearly(page);
  await assertYearlyRuleList(page);
  await assertNoOverflow(page, "360px");
});

test("yearly rule list reads at AA (390px phone)", async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await submitYearly(page);
  await assertYearlyRuleList(page);
  await assertNoOverflow(page, "390px");
});

test("yearly rule list reads at AA (768px tablet)", async ({ page }) => {
  await page.setViewportSize({ width: 768, height: 1024 });
  await submitYearly(page);
  await assertYearlyRuleList(page);
  await assertNoOverflow(page, "768px");
});

test("yearly rule list reads at AA (1440px desktop)", async ({ page }) => {
  await page.setViewportSize({ width: 1440, height: 900 });
  await submitYearly(page);
  await assertYearlyRuleList(page);
  await assertNoOverflow(page, "1440px");
});

test("E0400 evidence quote and boundary do not regress (360px)", async ({ page }) => {
  await page.setViewportSize({ width: 360, height: 800 });
  await submitYearly(page);
  await assertContrast(page, ".live-evidence blockquote", AA);
  await assertContrast(page, ".yearly-limits p", AA);
  await assertContrast(page, ".live-evidence small", AA);
});

test("daily branch list and romance/career rule content stay readable (360px)", async ({ page }) => {
  await page.setViewportSize({ width: 360, height: 800 });
  await page.goto("/daily-structure");
  await page.getByRole("button", { name: "填入示例" }).click();
  await page.getByRole("button", { name: "查看今日结构" }).click();
  await page.locator(".daily-result").waitFor({ state: "visible", timeout: 30000 });
  await assertContrast(page, ".daily-branch-structure > p", AA);
  await page.goto("/romance-structure");
  await page.getByRole("button", { name: "填入示例" }).click();
  await page.getByLabel("观察年份").fill("2026");
  await page.getByRole("button", { name: "查看桃花结构" }).click();
  await page.locator(".romance-result").waitFor({ state: "visible", timeout: 30000 });
  await assertContrast(page, ".live-evidence blockquote", AA);
  await assertContrast(page, ".romance-limits p", AA);
  await page.goto("/career-wealth-structure");
  await page.getByRole("button", { name: "填入示例" }).click();
  await page.getByLabel("观察年份").fill("2026");
  await page.getByRole("button", { name: "查看事业财运结构" }).click();
  await page.locator(".career-result").waitFor({ state: "visible", timeout: 30000 });
  await assertContrast(page, ".live-evidence blockquote", AA);
  await assertContrast(page, ".career-limits p", AA);
});
