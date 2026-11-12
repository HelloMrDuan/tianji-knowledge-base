/**
 * TJ-012.3 Stage B — 寅月 D-1 limited public presentation (pattern_presentation),
 * real-backend end-to-end acceptance.
 *
 * LOCAL ONLY — NOT wired to any public CI workflow (workflows run specs by
 * filename; none names this file), so public CI never claims these results.
 *
 * Requires a REAL assembled backend on 127.0.0.1:8000 (the vite dev proxy
 * forwards /api there). No route stubs, no mocks, no fixture responses:
 * every assertion below reads the live page rendered from the live API.
 * Backend under test: tj0123-pattern-public-presentation @
 * c800e44cb753a236cf76905094496d5c730f0131 (E0387, Gap A; PR #560 merge SHA,
 * deployed 2026-11-11T06:40:33Z), assembled on the
 * trusted machine and served on :8001, forwarded locally via
 * `ssh -L 8000:127.0.0.1:8001 instabox-machine`. The production run uses
 * the deployed web container instead (see playwright.prod.config.ts).
 *
 * Run locally with:
 *   npm test -- tests/tj0123-pattern-public-e2e.spec.ts
 *
 * Screenshots land in ~/workspace/tj0123-pattern-public-e2e/screenshots/
 * (outside the repo; the repo worktree stays clean of local-only artifacts).
 */
import { test, expect, type Page } from "@playwright/test";

const SCREENSHOTS = "/home/hatch/workspace/tj0123-pattern-public-e2e/screenshots";

// Evidence-hash boundary: the real D-1 evidence IDs are 24 lowercase hex
// chars, so a 64-hex-only check misses them. The 64-hex alternative covers
// the longer digest form. Either form inside pattern_presentation is a leak
// (the public shape carries no evidence IDs at all). The check stays scoped
// to the presentation object: a response-wide 24-hex check would also match
// the pre-existing strength_presentation.evidence_ids raw hashes (outside
// the #560 scope; see TJ-003.3 leak red-line), so it must not be widened.
const EVIDENCE_HASH_RE = /[0-9a-f]{24}|[0-9a-f]{64}/;

// Research raw fields that must never reach the public page or the public
// API responses (D-1 research block, live pilot result, D-1 trace).
const FORBIDDEN_STRINGS = [
  "pattern_determination_ren_yin",
  "ren_yin_pilot_result",
  "ren-pattern-yin-true-v1",
  "bazi.phase2.ren_yin_true_pattern",
];

// The pattern section lives inside 命盘结构分析. Presented outcomes share
// one aria-label; not_judgeable / abstained carry a suffixed label.
const PATTERN_SECTION = 'section[aria-label^="命盘结构分析·格局局部研究"]';

async function submitBirth(page: Page, date: string, time: string) {
  // The form uses separate 年/月/日/时/分 dropdowns (no date/time
  // inputs): hour and minute are selected explicitly and separately.
  // fill() overwrites any profile restored from localStorage (a prior
  // computation in the same context saves the birth for reuse).
  const [year, month, day] = date.split("-").map(Number);
  const [hour, minute] = time.split(":").map(Number);
  await page.goto("/bazi-profile");
  // Scoped by row + position: getByLabel("年", { exact: true }) matches
  // zero elements here (Chromium computes the select's accessible name
  // from the wrapping label including its option text), and bare
  // getByLabel("日") / ("时") are ambiguous. The row order is stable:
  // 年/月/日 in .birth-date-row, 时/分 in .time-selects.
  const dateSelects = page.locator(".birth-date-row select");
  await dateSelects.nth(0).selectOption(String(year));
  await dateSelects.nth(1).selectOption(String(month));
  await dateSelects.nth(2).selectOption(String(day));
  const timeSelects = page.locator(".time-selects select");
  await timeSelects.nth(0).selectOption(String(hour));
  await timeSelects.nth(1).selectOption(String(minute));
  await page.getByRole("button", { name: "生成基础档案" }).click();
  const section = page.locator(PATTERN_SECTION);
  await expect(section).toBeVisible({ timeout: 60000 });
  return section;
}

test.describe("TJ-012.3 pattern_presentation real-backend E2E (c800e44c)", () => {
  test.setTimeout(180000);

  test("(1) 正财格成立 — presented true_pattern with scope note", async ({ page }) => {
    const section = await submitBirth(page, "2024-02-11", "04:00");
    await expect(section).toContainText("任氏寅月局部真格研究结果");
    await expect(section).toContainText("格名：正财格");
    await expect(section).toContainText("司令戊透于时干，真格成立。");
    await expect(section).toContainText("日主乙生于寅月");
    // Scope note: the presentation states its own limit, never a whole-chart verdict.
    await expect(section).toContainText("仅陈述任氏分支寅月局部真格研究结果");
    await expect(section).toContainText("不是全盘格局判断");
    // No false-pattern verdict is rendered. The scope note legitimately
    // explains the rule with negations ("未呈现不等于假格",
    // "不输出假格、破格…"), so the no-假格 check is scoped to the
    // verdict paragraphs (outcome line + 格名 line), not the section.
    await expect(section.locator("p").first()).not.toContainText("假格");
    await expect(section.locator("p").nth(1)).not.toContainText("假格");
    await page.screenshot({ path: `${SCREENSHOTS}/pattern-public-t1-desktop.png`, fullPage: true });
  });

  test("(2) 司令未透 — presented commander_not_visible", async ({ page }) => {
    const section = await submitBirth(page, "2024-02-06", "00:30");
    await expect(section).toContainText("任氏寅月局部真格研究结果");
    await expect(section).toContainText("司令戊不透，无真格。");
    await expect(section).toContainText("日主庚生于寅月");
    // The scope note legitimately states the rule ("…则真格成立，司令不透
    // 则无真格", "未呈现不等于假格"), so the negative checks are scoped
    // to the outcome paragraph (first <p>), not the whole section.
    // "格名：" appears in no scope wording, so it stays section-wide.
    const outcome = section.locator("p").first();
    await expect(outcome).not.toContainText("真格成立");
    await expect(outcome).not.toContainText("假格");
    await expect(section).not.toContainText("格名：");
  });

  test("(3) 比肩格 not public — D5 fail-closed not_judgeable", async ({ page }) => {
    const section = await submitBirth(page, "2023-02-09", "12:00");
    await expect(section).toContainText("任氏寅月局部真格研究结果");
    await expect(section).toContainText("本盘的格名暂不在公开呈现范围内");
    await expect(section).toContainText("暂不可判，不作任何格局结论");
    // The mechanical name (戊 day master, 戊 commander, 戊透于时干) must
    // never appear as a presented pattern, in the section or anywhere.
    await expect(section).not.toContainText("比肩格");
    await expect(page.locator("body")).not.toContainText("比肩格");
    await expect(section).not.toContainText("格名：");
    await page.screenshot({ path: `${SCREENSHOTS}/pattern-public-d5-desktop.png`, fullPage: true });
  });

  test("(4) 劫财格 not public — fail-closed not_judgeable", async ({ page }) => {
    // 丁 day master, 丙 commander segment [立春+7d, 立春+14d), 丙透于月干:
    // ten-god of 丙 against 丁 is 劫财, so the mechanical name is 劫财格.
    // Verified against the live API before asserting (day_master 丁,
    // month stem 丙 ten_god 劫财, pattern_presentation reason
    // pattern_name_not_public).
    let apiBody = "";
    page.on("response", async (response) => {
      if (
        response.url().includes("/api/v1/scenarios/public") &&
        response.request().method() === "POST"
      ) {
        try {
          apiBody = await response.text();
        } catch {
          /* response already consumed; ignore */
        }
      }
    });
    const section = await submitBirth(page, "2024-02-13", "10:00");
    await expect(section).toContainText("任氏寅月局部真格研究结果");
    await expect(section).toContainText("本盘的格名暂不在公开呈现范围内");
    await expect(section).toContainText("暂不可判，不作任何格局结论");
    await expect(section).not.toContainText("劫财格");
    await expect(page.locator("body")).not.toContainText("劫财格");
    await expect(section).not.toContainText("格名：");
    expect(apiBody).toContain('"pattern_presentation"');
    expect(apiBody).toContain('"status":"not_judgeable"');
    expect(apiBody).toContain('"reason":"pattern_name_not_public"');
    expect(apiBody).not.toContain("劫财格");
  });

  test("(5) non-寅月 not judgeable — month_not_yin", async ({ page }) => {
    const section = await submitBirth(page, "2024-06-15", "10:00");
    await expect(section).toContainText("任氏寅月局部真格研究结果");
    await expect(section).toContainText("本盘不在寅月，不属于任氏寅月局部真格研究范围");
    await expect(section).toContainText("暂不可判，不作任何格局结论");
    await expect(section).not.toContainText("格名：");
  });

  test("(6) research raw fields do not leak — page + API responses", async ({ page }) => {
    const apiBodies: string[] = [];
    page.on("response", async (response) => {
      if (
        response.url().includes("/api/v1/scenarios/public") &&
        response.request().method() === "POST"
      ) {
        try {
          apiBodies.push(await response.text());
        } catch {
          /* response already consumed; ignore */
        }
      }
    });
    await submitBirth(page, "2024-02-11", "04:00");
    const bodyText = await page.locator("body").innerText();
    for (const forbidden of FORBIDDEN_STRINGS) {
      expect(bodyText).not.toContain(forbidden);
    }
    expect(apiBodies.length).toBeGreaterThanOrEqual(1);
    const joined = apiBodies.join("\n");
    expect(joined).toContain('"pattern_presentation"');
    for (const forbidden of FORBIDDEN_STRINGS) {
      expect(joined).not.toContain(forbidden);
    }
    // Public-identifier boundary (independent-review remediation):
    // the public shape carries no internal reference fields, and no
    // renshi rule id or raw D-1 evidence hash appears anywhere in
    // the API response. The D-1 evidence hashes are 24-hex, so the
    // check below is EVIDENCE_HASH_RE (24-hex or 64-hex), scoped to
    // the presentation object; renshi. is checked response-wide.
    expect(joined).not.toContain("renshi.");
    const parsed = JSON.parse(apiBodies[apiBodies.length - 1]) as {
      result?: { pattern_presentation?: Record<string, unknown> };
    };
    const presentation = parsed.result?.pattern_presentation;
    expect(presentation).toBeDefined();
    for (const key of ["rule_ids", "source_sections", "evidence_ids", "source_ids"]) {
      expect(presentation).not.toHaveProperty(key);
    }
    expect(JSON.stringify(presentation)).not.toMatch(EVIDENCE_HASH_RE);
  });

  test("(6n) leak check can fail — real-format 24-hex / renshi IDs are caught", async () => {
    // Negative control for the leak detection in test (6)/(8): the check
    // must TRIGGER on a presentation carrying real-format evidence
    // identifiers, so a passing run is not a vacuous pass. The 24-hex
    // value below is format-real but synthetic — the actual D-1 evidence
    // hashes are sealed and never appear in the public repo. The renshi
    // rule id is already public as a forbidden string above.
    const tainted24 = {
      variant: "bazi-pattern-public-presentation-v1",
      status: "presented",
      evidence_ids: ["0123456789abcdef01234567"],
    };
    expect(JSON.stringify(tainted24)).toMatch(EVIDENCE_HASH_RE);
    const taintedRenshi = {
      variant: "bazi-pattern-public-presentation-v1",
      rule_ids: ["renshi.zhenge_definition"],
    };
    expect(JSON.stringify(taintedRenshi)).toContain("renshi.");
    // The 64-hex digest form is still caught.
    expect(
      JSON.stringify({ evidence_ids: ["a".repeat(64)] }),
    ).toMatch(EVIDENCE_HASH_RE);
    // Positive control: a clean presentation still passes the check.
    const clean = {
      variant: "bazi-pattern-public-presentation-v1",
      status: "presented",
      pattern: "正财格",
    };
    expect(JSON.stringify(clean)).not.toMatch(EVIDENCE_HASH_RE);
    expect(JSON.stringify(clean)).not.toContain("renshi.");
  });

  test("(8) public evidence references resolve in the same envelope", async ({ page }) => {
    // Every evidence reference in the public presentation must both
    // follow the public identifier rules AND correspond to real
    // public evidence: pattern_presentation carries no reference
    // fields, and every E-alias referenced in the response's
    // rule_matches resolves to a key in the response's evidence
    // map (same envelope). D-1 evidence is not in that map, which
    // is why the pattern object names no evidence at all.
    let apiBody = "";
    page.on("response", async (response) => {
      if (
        response.url().includes("/api/v1/scenarios/public") &&
        response.request().method() === "POST"
      ) {
        try {
          apiBody = await response.text();
        } catch {
          /* response already consumed; ignore */
        }
      }
    });
    await submitBirth(page, "2024-02-11", "04:00");
    expect(apiBody).toContain('"pattern_presentation"');
    const parsed = JSON.parse(apiBody) as {
      result?: { pattern_presentation?: Record<string, unknown> };
      evidence?: Record<string, unknown>;
      rule_matches?: Array<{ evidence_ids?: unknown }>;
    };
    const presentation = parsed.result?.pattern_presentation;
    expect(presentation).toBeDefined();
    for (const key of ["rule_ids", "source_sections", "evidence_ids", "source_ids"]) {
      expect(presentation).not.toHaveProperty(key);
    }
    expect(JSON.stringify(presentation)).not.toMatch(EVIDENCE_HASH_RE);
    expect(apiBody).not.toContain("renshi.");
    const evidenceKeys = new Set(Object.keys(parsed.evidence ?? {}));
    expect(evidenceKeys.size).toBeGreaterThan(0);
    const rows = parsed.rule_matches ?? [];
    expect(rows.length).toBeGreaterThan(0);
    let checkedAliases = 0;
    for (const row of rows) {
      const aliases = row.evidence_ids;
      if (aliases === undefined) {
        continue;
      }
      expect(Array.isArray(aliases)).toBe(true);
      for (const alias of aliases as unknown[]) {
        expect(typeof alias).toBe("string");
        expect(alias as string).toMatch(/^E\d+$/);
        expect(evidenceKeys.has(alias as string)).toBe(true);
        checkedAliases += 1;
      }
    }
    expect(checkedAliases).toBeGreaterThan(0);
  });

  test("(7a) desktop 1280px — no abnormal horizontal overflow", async ({ page }) => {
    await page.setViewportSize({ width: 1280, height: 800 });
    await submitBirth(page, "2024-02-11", "04:00");
    const overflow = await page.evaluate(() => ({
      scrollWidth: document.documentElement.scrollWidth,
      clientWidth: document.documentElement.clientWidth,
    }));
    expect(overflow.scrollWidth).toBeLessThanOrEqual(overflow.clientWidth + 1);
  });

  test("(7b) mobile 390px — no abnormal horizontal overflow", async ({ page }) => {
    await page.setViewportSize({ width: 390, height: 844 });
    await submitBirth(page, "2024-02-11", "04:00");
    const overflow = await page.evaluate(() => ({
      scrollWidth: document.documentElement.scrollWidth,
      clientWidth: document.documentElement.clientWidth,
    }));
    expect(overflow.scrollWidth).toBeLessThanOrEqual(overflow.clientWidth + 1);
    await page.screenshot({ path: `${SCREENSHOTS}/pattern-public-t1-mobile.png`, fullPage: true });
    // D5 case at mobile width as well.
    await submitBirth(page, "2023-02-09", "12:00");
    const overflowD5 = await page.evaluate(() => ({
      scrollWidth: document.documentElement.scrollWidth,
      clientWidth: document.documentElement.clientWidth,
    }));
    expect(overflowD5.scrollWidth).toBeLessThanOrEqual(overflowD5.clientWidth + 1);
    await page.screenshot({ path: `${SCREENSHOTS}/pattern-public-d5-mobile.png`, fullPage: true });
  });
});
