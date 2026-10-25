/**
 * TJ-008.4 standalone (single task, no batch marker): mobile + accessibility.
 *
 * WBS acceptance, verbatim scope: 390/360/768 viewports, 200% zoom, keyboard
 * and reduced-motion, no core button occluded by the fixed bottom nav.
 *
 * WHAT THIS SPEC DOES AND DOES NOT PROVE (honesty notes, read before citing):
 * - No backend is required and no API route is stubbed: every assertion runs
 *   against initial page states (forms before submit, static liuyao fixture)
 *   that render without any API call. Nothing here proves engine behavior.
 * - 200% ZOOM METHOD: Playwright has no browser-zoom API. At 200% zoom the
 *   CSS layout viewport halves, so a 195px viewport reproduces exactly the
 *   layout geometry real 200% zoom produces on a 390px phone (media queries,
 *   reflow, fixed-nav position in layout coordinates); 180px is the same for
 *   a 360px phone. Two tempting proxies were measured and REJECTED:
 *   deviceScaleFactor (changes device pixels only, no layout change, so it
 *   cannot reveal zoom breakage) and CSS body zoom (its coordinate system
 *   disagrees with clientWidth in ways real zoom does not, e.g. a 424px
 *   scrollWidth against a 390px clientWidth with no real overflow).
 * - FIRST-VIEWPORT vs MAX-SCROLL: scenario submit buttons sit BELOW the
 *   fold by design (measured tops 965-2295px against an 844px viewport), so
 *   no scrollY===0 test can cover them. This spec therefore splits occlusion
 *   into two honest measurements: (a) scrollY===0, no scrolling, for buttons
 *   actually in the first viewport (liuyao favorite, entry sample buttons);
 *   (b) maximum-scroll revealability for every submit and primary action:
 *   the page is scrolled to its very bottom and each button must clear the
 *   nav by 4px. Max-scroll is the opposite of masking: if bottom clearance
 *   were insufficient, the button would stay under the nav even at maximum
 *   scroll and this test would FAIL. scrollIntoView() and toBeVisible() are
 *   never used to prove non-occlusion anywhere in this file.
 * - FOCUS TRAP is out of scope: the WBS "keyboard" condition does not name
 *   it, no FocusTrap exists in src, and this spec does not claim one. The
 *   native <dialog> Escape/focus-restore behavior on the liuyao page is
 *   browser behavior, tested as such, not claimed as app implementation.
 * - REDUCED-MOTION dead selectors (removed in TJ-009.3, redefined):
 *   the .night-hero-scene .nhs-lantern/.nhs-mist rules formerly in
 *   night-home.css targeted classes with zero matches in any .tsx (the
 *   hero renders a <picture> since TJ-008.7 round 4); TJ-009.3 deleted
 *   them as dead CSS. The global * reduced-motion rule is verified
 *   below and covers every element including any future lantern/mist
 *   element.
 * - NOT re-tested here (already covered elsewhere, do not double-count):
 *   homepage first-screen 4 card rows (TJ-008.7 round 5), contrast
 *   (TJ-021.3), dual-theme basics (TJ-008.6). TJ-008.5 is untouched.
 */
import { test, expect } from "@playwright/test";

const FOCUS_OUTLINE = "2px solid rgb(170, 131, 69)";

async function navTop(page: import("@playwright/test").Page) {
  return page.evaluate(() => {
    const nav = document.querySelector(".mobile-bottom-nav") as HTMLElement | null;
    return nav ? nav.getBoundingClientRect().top : window.innerHeight;
  });
}

async function overflow(page: import("@playwright/test").Page) {
  return page.evaluate(
    () => document.documentElement.scrollWidth - document.documentElement.clientWidth,
  );
}

async function navDisplay(page: import("@playwright/test").Page) {
  return page.evaluate(() => {
    const nav = document.querySelector(".mobile-bottom-nav") as HTMLElement | null;
    return nav ? getComputedStyle(nav).display : "none";
  });
}

/** Pages with a stable "page is rendered" marker. No submission happens. */
const PAGES: Array<{ route: string; marker: string; name: string }> = [
  { route: "/", marker: ".scenario-hero h1", name: "home" },
  { route: "/daily-structure", marker: ".daily-submit", name: "daily" },
  { route: "/romance-structure", marker: ".romance-submit", name: "romance" },
  { route: "/career-wealth-structure", marker: ".career-submit", name: "career" },
  { route: "/yearly-structure", marker: ".yearly-submit", name: "yearly" },
  { route: "/weekly-structure", marker: ".period-submit", name: "weekly" },
  { route: "/monthly-structure", marker: ".period-submit", name: "monthly" },
  { route: "/bazi-profile", marker: ".bazi-submit", name: "bazi" },
  { route: "/compatibility-structure", marker: "form button[type='submit']", name: "compatibility" },
  { route: "/dream-culture", marker: "form button[type='submit']", name: "dream" },
  { route: "/life-overview", marker: ".life-submit", name: "life" },
  { route: "/ask", marker: ".question-submit", name: "ask" },
  { route: "/liuyao/result", marker: ".favorite-button", name: "liuyao-result" },
];

// ---------- 1. Viewport matrix: no horizontal overflow, nav presence ----------
for (const width of [390, 360, 768, 1440] as const) {
  test.describe(`TJ-008.4 viewport matrix ${width}px`, () => {
    for (const p of PAGES) {
      test(`${p.name}: no horizontal overflow, nav ${width <= 760 ? "shown" : "hidden"}`, async ({ page }) => {
        await page.setViewportSize({ width, height: width >= 768 ? 900 : width === 390 ? 844 : 800 });
        await page.goto(p.route);
        await page.locator(p.marker).first().waitFor({ state: "attached", timeout: 15000 });
        const diff = await overflow(page);
        expect(diff, `${p.name} @${width}px horizontal overflow`).toBeLessThanOrEqual(1);
        expect(await navDisplay(page)).toBe(width <= 760 ? "flex" : "none");
      });
    }
  });
}

// ---------- 2. First-viewport occlusion at scrollY===0 (no scrolling) ----------
const FIRST_VIEWPORT_BUTTONS: Array<{ route: string; selector: string; name: string }> = [
  { route: "/liuyao/result", selector: ".favorite-button", name: "liuyao favorite" },
  { route: "/daily-structure", selector: ".sample-fill", name: "daily sample" },
  { route: "/romance-structure", selector: ".sample-fill", name: "romance sample" },
  { route: "/career-wealth-structure", selector: ".sample-fill", name: "career sample" },
  { route: "/yearly-structure", selector: ".sample-fill", name: "yearly sample" },
];

for (const b of FIRST_VIEWPORT_BUTTONS) {
  for (const [width, height] of [[390, 844], [360, 800]] as const) {
    test(`TJ-008.4 first viewport ${b.name} clears nav (${width}x${height}, scrollY=0)`, async ({ page }) => {
      await page.setViewportSize({ width, height });
      await page.goto(b.route);
      await page.locator(b.selector).first().waitFor({ state: "attached", timeout: 15000 });
      expect(await page.evaluate(() => window.scrollY)).toBe(0);
      const geom = await page.evaluate((sel) => {
        const el = document.querySelector(sel) as HTMLElement | null;
        const r = el ? el.getBoundingClientRect() : null;
        return r ? { top: r.top, bottom: r.bottom, inFirst: r.bottom <= window.innerHeight } : null;
      }, b.selector);
      expect(geom, `${b.name} must render`).not.toBeNull();
      // The button must actually be in the first viewport for this test to
      // mean anything; below-fold buttons are covered by max-scroll below.
      expect(geom!.inFirst, `${b.name} must be in the first viewport`).toBe(true);
      const top = await navTop(page);
      expect(geom!.bottom, `${b.name} bottom must clear nav by 4px`).toBeLessThanOrEqual(top - 4);
    });
  }
}

// ---------- 3. Max-scroll revealability for every submit + primary action ----------
const MAX_SCROLL_PAGES: Array<{ route: string; selectors: string[]; name: string }> = [
  { route: "/daily-structure", selectors: [".daily-submit", ".sample-fill"], name: "daily" },
  { route: "/romance-structure", selectors: [".romance-submit", ".sample-fill"], name: "romance" },
  { route: "/career-wealth-structure", selectors: [".career-submit", ".sample-fill"], name: "career" },
  { route: "/yearly-structure", selectors: [".yearly-submit", ".sample-fill"], name: "yearly" },
  { route: "/weekly-structure", selectors: [".period-submit"], name: "weekly" },
  { route: "/monthly-structure", selectors: [".period-submit"], name: "monthly" },
  { route: "/bazi-profile", selectors: [".bazi-submit", ".sample-fill"], name: "bazi" },
  { route: "/compatibility-structure", selectors: ["form button[type='submit']", ".compat-submit-wrap button"], name: "compatibility" },
  { route: "/dream-culture", selectors: ["form button[type='submit']"], name: "dream" },
  { route: "/life-overview", selectors: [".life-submit", ".sample-fill"], name: "life" },
  { route: "/ask", selectors: [".question-submit", ".compact-button"], name: "ask" },
];

for (const p of MAX_SCROLL_PAGES) {
  for (const [width, height] of [[390, 844], [360, 800]] as const) {
    test(`TJ-008.4 max-scroll ${p.name} actions clear nav (${width}x${height})`, async ({ page }) => {
      await page.setViewportSize({ width, height });
      await page.goto(p.route);
      await page.locator(p.selectors[0]).first().waitFor({ state: "attached", timeout: 15000 });
      await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight));
      await page.waitForTimeout(300);
      const result = await page.evaluate((sels) => {
        const nav = document.querySelector(".mobile-bottom-nav") as HTMLElement | null;
        const top = nav ? nav.getBoundingClientRect().top : window.innerHeight;
        const bad: string[] = [];
        const counts: Record<string, number> = {};
        for (const sel of sels) {
          const els = [...document.querySelectorAll(sel)] as HTMLElement[];
          counts[sel] = els.length;
          for (const el of els) {
            const r = el.getBoundingClientRect();
            if (r.bottom > top - 4) {
              bad.push(`${sel} bottom=${r.bottom.toFixed(1)} navTop=${top.toFixed(1)}`);
            }
          }
        }
        return { top, counts, bad };
      }, p.selectors);
      for (const sel of p.selectors) {
        expect(result.counts[sel], `${p.name} selector ${sel} must match at least one button`).toBeGreaterThan(0);
      }
      expect(result.bad, `${p.name} buttons stuck under nav at max scroll`).toEqual([]);
    });
  }
}

// ---------- 4. 200% zoom equivalence: 195px (390@200%) and 180px (360@200%) ----------
for (const { width, height, label } of [
  { width: 195, height: 422, label: "390@200%" },
  { width: 180, height: 400, label: "360@200%" },
] as const) {
  test.describe(`TJ-008.4 zoom equivalence ${label} (${width}px layout viewport)`, () => {
    for (const p of PAGES) {
      test(`${p.name}: no horizontal overflow, nav shown`, async ({ page }) => {
        await page.setViewportSize({ width, height });
        await page.goto(p.route);
        await page.locator(p.marker).first().waitFor({ state: "attached", timeout: 15000 });
        const diff = await overflow(page);
        expect(diff, `${p.name} @${label} horizontal overflow`).toBeLessThanOrEqual(1);
        expect(await navDisplay(page)).toBe("flex");
      });
    }
  });
}

// ---------- 5. Keyboard ----------
test("TJ-008.4 keyboard: home Tab order follows DOM with visible focus", async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto("/");
  await page.locator(".scenario-hero h1").waitFor({ timeout: 15000 });
  const seq: Array<{ tag: string; classes: string[]; outline: string; offset: string }> = [];
  for (let i = 0; i < 14; i++) {
    await page.keyboard.press("Tab");
    seq.push(await page.evaluate(() => {
      const el = document.activeElement as HTMLElement | null;
      if (!el) return { tag: "null", classes: [], outline: "", offset: "" };
      const cs = getComputedStyle(el);
      return {
        tag: el.tagName.toLowerCase(),
        classes: [...el.classList],
        outline: `${cs.outlineWidth} ${cs.outlineStyle} ${cs.outlineColor}`,
        offset: cs.outlineOffset,
      };
    }));
  }
  // Brand -> theme toggle -> music trigger -> 11 scenario card rows.
  expect(seq[0].tag).toBe("a");
  expect(seq[0].classes).toContain("public-brand");
  expect(seq[1].tag).toBe("button");
  expect(seq[1].classes).toContain("theme-toggle");
  expect(seq[2].tag).toBe("button");
  expect(seq[2].classes).toContain("music-trigger");
  for (let i = 3; i < 14; i++) {
    expect(seq[i].tag).toBe("a");
    expect(seq[i].classes).toContain("mobile-card-row");
  }
  for (const step of seq) {
    expect(step.outline).toBe(FOCUS_OUTLINE);
    expect(step.offset).toBe("4px");
  }
});

test("TJ-008.4 keyboard: mobile bottom nav is Tab-reachable with visible focus", async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto("/");
  await page.locator(".scenario-hero h1").waitFor({ timeout: 15000 });
  let reached = false;
  let outline = "";
  for (let i = 0; i < 60; i++) {
    await page.keyboard.press("Tab");
    const info = await page.evaluate(() => {
      const el = document.activeElement as HTMLElement | null;
      if (!el) return { inNav: false, outline: "" };
      const cs = getComputedStyle(el);
      return {
        inNav: !!el.closest(".mobile-bottom-nav"),
        outline: `${cs.outlineWidth} ${cs.outlineStyle} ${cs.outlineColor}`,
      };
    });
    if (info.inNav) {
      reached = true;
      outline = info.outline;
      break;
    }
  }
  expect(reached, "mobile nav link must be reachable by Tab").toBe(true);
  expect(outline).toBe(FOCUS_OUTLINE);
});

test("TJ-008.4 keyboard: daily form controls show focus, submit is Tab-reachable", async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto("/daily-structure");
  await page.locator(".daily-submit").waitFor({ state: "attached", timeout: 15000 });
  for (let i = 0; i < 8; i++) {
    await page.keyboard.press("Tab");
    const outline = await page.evaluate(() => {
      const el = document.activeElement as HTMLElement | null;
      if (!el) return "";
      const cs = getComputedStyle(el);
      return `${cs.outlineWidth} ${cs.outlineStyle} ${cs.outlineColor}`;
    });
    expect(outline, `Tab ${i + 1} focused element must show focus outline`).toBe(FOCUS_OUTLINE);
  }
  let submitReached = false;
  for (let i = 0; i < 30; i++) {
    const onSubmit = await page.evaluate(() => {
      const el = document.activeElement as HTMLElement | null;
      return !!el && el.matches(".daily-submit");
    });
    if (onSubmit) {
      submitReached = true;
      break;
    }
    await page.keyboard.press("Tab");
  }
  expect(submitReached, "daily submit must be Tab-reachable").toBe(true);
  const submitFocus = await page.evaluate(() => {
    const el = document.querySelector(".daily-submit") as HTMLElement;
    const cs = getComputedStyle(el);
    return {
      focusVisible: el.matches(":focus-visible"),
      outline: `${cs.outlineWidth} ${cs.outlineStyle} ${cs.outlineColor}`,
      offset: cs.outlineOffset,
    };
  });
  expect(submitFocus.focusVisible).toBe(true);
  expect(submitFocus.outline).toBe(FOCUS_OUTLINE);
  expect(submitFocus.offset).toBe("4px");
});

test("TJ-008.4 keyboard: liuyao dialog closes on Escape and restores focus", async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto("/liuyao/result");
  await page.locator(".chart-line").first().waitFor({ state: "attached", timeout: 15000 });
  await page.locator(".chart-line").first().click();
  const opened = await page.evaluate(() => {
    const d = document.querySelector("dialog") as HTMLDialogElement | null;
    return d ? d.open : false;
  });
  expect(opened, "dialog must open on chart line click").toBe(true);
  const insideDialog = await page.evaluate(() => {
    const el = document.activeElement as HTMLElement | null;
    return !!el && !!el.closest("dialog");
  });
  expect(insideDialog, "focus must move inside the dialog").toBe(true);
  await page.keyboard.press("Escape");
  await page.waitForTimeout(300);
  const closed = await page.evaluate(() => {
    const d = document.querySelector("dialog") as HTMLDialogElement | null;
    return d ? d.open : false;
  });
  expect(closed, "dialog must close on Escape").toBe(false);
  const restored = await page.evaluate(() => {
    const el = document.activeElement as HTMLElement | null;
    return !!el && el.matches(".chart-line");
  });
  expect(restored, "focus must return to the triggering chart line").toBe(true);
});

// ---------- 6. Reduced motion ----------
test("TJ-008.4 reduced-motion control: paper card lifts on hover without reduce", async ({ page }) => {
  await page.setViewportSize({ width: 1440, height: 900 });
  await page.goto("/");
  await page.locator(".paper-card").first().waitFor({ state: "attached", timeout: 15000 });
  await page.locator(".paper-card").first().hover();
  await page.waitForTimeout(400);
  const style = await page.evaluate(() => {
    const el = document.querySelector(".paper-card") as HTMLElement;
    const cs = getComputedStyle(el);
    return { transform: cs.transform, transition: cs.transitionDuration };
  });
  // Proves the reduce test below is not vacuous: the lift exists to disable.
  expect(style.transform).not.toBe("none");
  expect(style.transition).toContain("0.2s");
});

test("TJ-008.4 reduced-motion: paper card stays static under reduce", async ({ browser }) => {
  const ctx = await browser.newContext({ reducedMotion: "reduce", viewport: { width: 1440, height: 900 } });
  const page = await ctx.newPage();
  await page.goto("/");
  await page.locator(".paper-card").first().waitFor({ state: "attached", timeout: 15000 });
  await page.locator(".paper-card").first().hover();
  await page.waitForTimeout(400);
  const style = await page.evaluate(() => {
    const el = document.querySelector(".paper-card") as HTMLElement;
    const cs = getComputedStyle(el);
    const body = getComputedStyle(document.body);
    return {
      transform: cs.transform,
      transition: cs.transitionDuration,
      animation: `${cs.animationName}/${cs.animationDuration}`,
      bodyAnimation: `${body.animationName}/${body.animationDuration}`,
      bodyTransition: body.transitionDuration,
    };
  });
  expect(style.transform, "hover lift must be disabled under reduce").toBe("none");
  expect(style.transition, "transitions must be disabled under reduce").toBe("0s");
  expect(style.animation).toBe("none/0s");
  expect(style.bodyAnimation).toBe("none/0s");
  expect(style.bodyTransition).toBe("0s");
  await ctx.close();
});
