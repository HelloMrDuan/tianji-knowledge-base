/**
 * TJ-009.3 standalone (single task, no batch marker): STATIC HERO
 * PERFORMANCE VERIFICATION + DEAD CSS CLEANUP — REDEFINED DEFINITION.
 *
 * USER-AUTHORIZED REDEFINITION (2026-10-25, option tap): the WBS literal
 * "mountain/mist animation performance" no longer exists as a verifiable
 * object, so the task was redefined instead of being faked or closed:
 * - InkLandscape was static SVG from the start (no animation, no canvas,
 *   no requestAnimationFrame); NightHeroScene became static <picture>
 *   images by an intentional TJ-008.7 round-4 decision (one image per
 *   viewport, night theme only). There is no running landscape/mist
 *   animation whose "smoothness" could be measured.
 * - The baseline itself says the existing static SVG is the base, and the
 *   page spec requires "no animation interference" — not "animation that
 *   is smooth". Reviving animation would be a new feature against the
 *   008.7 decision, with no user-demand evidence, so this batch does not
 *   revive anything.
 *
 * THE THREE POINTS THE PR DESCRIPTION MUST STATE (mirrored here):
 * (1) WBS literal "animation" no longer exists (008.7 round 4 static
 *     pictures replaced it; InkLandscape was always static SVG).
 * (2) This batch verifies STATIC HERO PERFORMANCE + DEAD CSS HANDLING.
 * (3) ALL QUANTITATIVE THRESHOLDS BELOW ARE SUGGESTED STANDARDS, NOT
 *     WBS TEXT. WBS has no numbers (no fps, no load time, no network
 *     condition, no device tier). Each threshold states its measured
 *     basis where it is used. NEVER cite this spec as completing the
 *     literal WBS "animation performance".
 *
 * WHAT "HERO IMAGE" MEANS HERE (scope precision, read before citing):
 * - Only hero-desktop.jpg / hero-mobile.jpg, the NightHeroScene
 *   <picture> images. The PaperCard art-*.jpg card images live under the
 *   same night-home/ folder but are a DIFFERENT mechanism (card art,
 *   rendered in both themes) and are OUT OF SCOPE here.
 * - Vite dev module fetches (hero-*.jpg?import, resourceType 'script')
 *   are the JS bundle importing both images; they fire in BOTH themes
 *   and are NOT image downloads. Only resourceType 'image' requests
 *   without '?import' count as hero image loads (verified by probe:
 *   ?import -> script, <picture> selection -> image).
 * - Distinct-URL counting: the same hero URL re-requested from cache
 *   still counts once (the property is "one image per viewport").
 *
 * SLOW 3G HONESTY NOTE: CDP Network.emulateNetworkConditions throttles
 * the WHOLE page. In Vite dev mode the app is served as many modules,
 * so absolute page-load time under full throttling is slow and
 * variable (probe: hero request fired 33s after nav start) and is NOT
 * asserted. What IS asserted is the hero TRANSFER duration once the
 * request fires (request -> full body), which isolates hero bytes
 * under the shared ~200KB/s emulation from JS-load slowness.
 * SUGGESTED threshold 20,000ms: probe measured 10,204ms for a 504KB
 * hero competing with 7 concurrent art images for the shared bucket;
 * 20s is ~2x headroom for CI variance and catches 2x+ size regressions.
 * Desktop fast-network results are never presented as weak-network
 * results; this test really throttles.
 *
 * CPU THROTTLING HONESTY NOTE: CDP Emulation.setCPUThrottlingRate 4x,
 * hero render completion measured as performance.now() at img load
 * (navigation start -> img complete). SUGGESTED threshold 10,000ms:
 * probe measured 3,567-3,782ms locally; 10s is ~2.6x headroom and
 * catches gross JS/hero regressions.
 *
 * REDUCED-MOTION WEAKNESS (admitted, not hidden): NightHeroScene and
 * InkLandscape are STATIC — they have no animation to stop. The
 * reduce assertions below prove only that no animation RUNS on hero
 * elements under reduce; they must NEVER be cited as "animation stop
 * verification". The site-wide reduced-motion global rule was already
 * verified by TJ-008.4 and is NOT double-counted here.
 *
 * DEAD CSS CLEANUP IN THIS BATCH: night-home.css lantern/mist keyframes
 * (nhs-lantern-flicker, nhs-mist-drift), the .nhs-lantern/.nhs-mist-1/
 * .nhs-mist-2 application rules, and the dead selectors inside the
 * prefers-reduced-motion block were deleted (0 references in any .tsx;
 * the live .paper-card rules in the same block and the generic
 * .night-hero-scene container rule stay). This is CLEANUP, not
 * "animation stop verification".
 *
 * WHAT THIS SPEC DOES AND DOES NOT PROVE:
 * - No backend is required and no API route is stubbed: every assertion
 *   runs against the homepage initial state. Nothing here proves engine
 *   behavior, and no frame-rate data is claimed (no animation exists
 *   to measure frames for).
 * - NOT re-tested here (already covered elsewhere, do not double-count):
 *   site-wide reduced-motion global rule (TJ-008.4), contrast (TJ-021.3),
 *   dual-theme basics (TJ-008.6). TJ-008.5 is untouched. No page was
 *   visually redesigned.
 */
import { test, expect } from "@playwright/test";

const HERO_RE = /hero-(desktop|mobile)/;
const isHeroImageReq = (req: import("@playwright/test").Request) =>
  HERO_RE.test(req.url()) &&
  req.resourceType() === "image" &&
  !req.url().includes("?import");

async function gotoWithTheme(
  page: import("@playwright/test").Page,
  theme: "night" | "paper",
  width: number,
) {
  await page.addInitScript((t: string) => {
    window.localStorage.setItem("tianji.theme", t);
  }, theme);
  await page.setViewportSize({ width, height: 900 });
  await page.goto("/");
}

async function heroImageUrls(
  page: import("@playwright/test").Page,
  theme: "night" | "paper",
  width: number,
): Promise<string[]> {
  const urls = new Set<string>();
  page.on("request", (req) => {
    if (isHeroImageReq(req)) urls.add(req.url());
  });
  await gotoWithTheme(page, theme, width);
  await page.waitForTimeout(2000);
  return [...urls];
}

function heroKind(url: string): string {
  if (url.includes("hero-desktop")) return "desktop";
  if (url.includes("hero-mobile")) return "mobile";
  return "unknown";
}

test("night 1440 loads exactly one hero image: desktop", async ({ page }) => {
  const urls = await heroImageUrls(page, "night", 1440);
  expect(urls).toHaveLength(1);
  expect(heroKind(urls[0])).toBe("desktop");
  await expect(page.locator(".night-hero-picture")).toHaveCount(1);
});

test("night 390 loads exactly one hero image: mobile", async ({ page }) => {
  const urls = await heroImageUrls(page, "night", 390);
  expect(urls).toHaveLength(1);
  expect(heroKind(urls[0])).toBe("mobile");
});

test("night 640 boundary loads mobile (max-width:640px inclusive)", async ({
  page,
}) => {
  const urls = await heroImageUrls(page, "night", 640);
  expect(urls).toHaveLength(1);
  expect(heroKind(urls[0])).toBe("mobile");
});

test("night 641 boundary loads desktop (above 640px)", async ({ page }) => {
  const urls = await heroImageUrls(page, "night", 641);
  expect(urls).toHaveLength(1);
  expect(heroKind(urls[0])).toBe("desktop");
});

test("paper 1440 loads zero hero images", async ({ page }) => {
  const urls = await heroImageUrls(page, "paper", 1440);
  expect(urls).toHaveLength(0);
  await expect(page.locator(".night-hero-picture")).toHaveCount(0);
  await expect(page.locator(".night-hero-paper svg")).toHaveCount(1);
});

test("paper 390 loads zero hero images", async ({ page }) => {
  const urls = await heroImageUrls(page, "paper", 390);
  expect(urls).toHaveLength(0);
  await expect(page.locator(".night-hero-picture")).toHaveCount(0);
});

test("slow 3G hero transfer completes within suggested 20s", async ({
  page,
}) => {
  test.setTimeout(180000);
  await page.addInitScript(() => {
    window.localStorage.setItem("tianji.theme", "night");
  });
  await page.setViewportSize({ width: 1440, height: 900 });
  const cdp = await page.context().newCDPSession(page);
  await cdp.send("Network.enable");
  await cdp.send("Network.emulateNetworkConditions", {
    offline: false,
    latency: 150,
    downloadThroughput: (1.6 * 1024 * 1024) / 8,
    uploadThroughput: (750 * 1024) / 8,
  });
  const t0 = Date.now();
  const reqAt = new Map<string, number>();
  const doneAt = new Map<string, number>();
  page.on("request", (req) => {
    if (isHeroImageReq(req) && !reqAt.has(req.url())) {
      reqAt.set(req.url(), Date.now() - t0);
    }
  });
  page.on("response", (res) => {
    const req = res.request();
    if (isHeroImageReq(req) && !doneAt.has(req.url())) {
      void res
        .body()
        .catch(() => null)
        .then(() => {
          doneAt.set(req.url(), Date.now() - t0);
        });
    }
  });
  await page.goto("/", { waitUntil: "commit" });
  const deadline = Date.now() + 150000;
  while (doneAt.size === 0 && Date.now() < deadline) {
    await page.waitForTimeout(1000);
  }
  expect(doneAt.size).toBe(1);
  const [[url, start]] = [...reqAt];
  const end = doneAt.get(url)!;
  // SUGGESTED threshold (not WBS): 20,000ms; probe basis 10,204ms.
  expect(end - start).toBeLessThan(20000);
  expect(heroKind(url)).toBe("desktop");
});

test("cpu 4x hero render completes within suggested 10s", async ({
  page,
}) => {
  await page.addInitScript(() => {
    window.localStorage.setItem("tianji.theme", "night");
  });
  await page.setViewportSize({ width: 1440, height: 900 });
  const cdp = await page.context().newCDPSession(page);
  await cdp.send("Emulation.setCPUThrottlingRate", { rate: 4 });
  await page.goto("/", { waitUntil: "domcontentloaded" });
  await page.waitForSelector(".night-hero-painting");
  const heroMs = await page.evaluate(() => {
    const img = document.querySelector(
      ".night-hero-painting",
    ) as HTMLImageElement | null;
    if (!img) return -1;
    if (img.complete && img.naturalWidth > 0) return Math.round(performance.now());
    return new Promise<number>((resolve) => {
      img.addEventListener("load", () => resolve(Math.round(performance.now())), {
        once: true,
      });
      img.addEventListener("error", () => resolve(-1), { once: true });
    });
  });
  expect(heroMs).toBeGreaterThan(0);
  // SUGGESTED threshold (not WBS): 10,000ms; probe basis 3,567-3,782ms.
  expect(heroMs).toBeLessThan(10000);
});

test("WEAK reduce: night hero runs no animation under reduce", async ({
  browser,
}) => {
  const ctx = await browser.newContext({ reducedMotion: "reduce" });
  const p = await ctx.newPage();
  await p.addInitScript(() => {
    window.localStorage.setItem("tianji.theme", "night");
  });
  await p.setViewportSize({ width: 1440, height: 900 });
  await p.goto("/");
  await p.waitForSelector(".night-hero-painting");
  const styles = await p.evaluate(() => {
    const pick = (sel: string) => {
      const el = document.querySelector(sel) as HTMLElement | null;
      if (!el) return null;
      const cs = getComputedStyle(el);
      return { name: cs.animationName, duration: cs.animationDuration };
    };
    return {
      picture: pick(".night-hero-picture"),
      img: pick(".night-hero-painting"),
    };
  });
  expect(styles.picture).toEqual({ name: "none", duration: "0s" });
  expect(styles.img).toEqual({ name: "none", duration: "0s" });
  await ctx.close();
});

test("WEAK reduce: paper ink landscape runs no animation under reduce", async ({
  browser,
}) => {
  const ctx = await browser.newContext({ reducedMotion: "reduce" });
  const p = await ctx.newPage();
  await p.addInitScript(() => {
    window.localStorage.setItem("tianji.theme", "paper");
  });
  await p.setViewportSize({ width: 1440, height: 900 });
  await p.goto("/");
  await p.waitForSelector(".night-hero-paper svg");
  const name = await p.evaluate(() => {
    const el = document.querySelector(
      ".night-hero-paper svg",
    ) as unknown as HTMLElement | null;
    return el ? getComputedStyle(el).animationName : null;
  });
  expect(name).toBe("none");
  await ctx.close();
});
