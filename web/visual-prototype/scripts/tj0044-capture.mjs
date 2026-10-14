/**
 * TJ-004.4 visual evidence capture.
 *
 * Screenshots the public home page plus the 11 life-scenario pages at
 * 1440 / 390 / 360 viewports with real Chromium, and stores them under
 * docs/product/evidence/tj-004.4/screenshots/ so the PR carries reviewable
 * evidence instead of local-only paths.
 *
 * Run:
 *   cd web/visual-prototype
 *   npm ci && npx playwright install chromium
 *   npm run build
 *   npx vite preview --port 4174 --host 127.0.0.1   # separate shell
 *   node scripts/tj0044-capture.mjs
 *
 * Deps: @playwright/test (devDependencies), a built dist/ served on
 * PROTOTYPE_BASE_URL (default http://127.0.0.1:4174).
 *
 * Acceptance: 12 pages x 3 viewports = 36 PNG files, each non-empty,
 * no page errors during capture.
 */
import { chromium } from "@playwright/test";
import { mkdir, stat } from "node:fs/promises";
import { fileURLToPath } from "node:url";
import path from "node:path";

const repoRoot = fileURLToPath(new URL("../../..", import.meta.url));
const target = path.join(
  repoRoot,
  "docs/product/evidence/tj-004.4/screenshots",
);
await mkdir(target, { recursive: true });
const baseURL = process.env.PROTOTYPE_BASE_URL || "http://127.0.0.1:4174";

const pages = [
  ["home", "/"],
  ["bazi-profile", "/bazi-profile"],
  ["daily-structure", "/daily-structure"],
  ["weekly-structure", "/weekly-structure"],
  ["monthly-structure", "/monthly-structure"],
  ["yearly-structure", "/yearly-structure"],
  ["romance-structure", "/romance-structure"],
  ["career-wealth-structure", "/career-wealth-structure"],
  ["compatibility-structure", "/compatibility-structure"],
  ["ask", "/ask"],
  ["dream-culture", "/dream-culture"],
  ["life-overview", "/life-overview"],
];
const viewports = [
  ["1440", { width: 1440, height: 1000 }],
  ["390", { width: 390, height: 844 }],
  ["360", { width: 360, height: 800 }],
];

const browser = await chromium.launch({ args: ["--no-sandbox"] });
let ok = 0;
const failures = [];
try {
  for (const [vpName, viewport] of viewports) {
    const context = await browser.newContext({
      viewport,
      deviceScaleFactor: 1,
      reducedMotion: "reduce",
    });
    const page = await context.newPage();
    const pageErrors = [];
    page.on("pageerror", (e) => pageErrors.push(String(e).slice(0, 120)));
    for (const [name, route] of pages) {
      const file = path.join(target, `${name}-${vpName}.png`);
      try {
        await page.goto(`${baseURL}${route}`, {
          waitUntil: "domcontentloaded",
          timeout: 20000,
        });
        await page.locator("main h1, main h2").first().waitFor({ timeout: 10000 });
        await page.evaluate(() => document.fonts.ready);
        await page.waitForTimeout(600);
        await page.screenshot({ path: file, fullPage: true, animations: "disabled" });
        const size = (await stat(file)).size;
        if (size < 1024) throw new Error(`suspiciously small file (${size} bytes)`);
        ok += 1;
        console.log(`OK ${name}-${vpName} (${Math.round(size / 1024)} KB)`);
      } catch (e) {
        failures.push(`${name}-${vpName}: ${String(e).slice(0, 120)}`);
        console.log(`FAIL ${name}-${vpName}: ${String(e).slice(0, 120)}`);
      }
    }
    if (pageErrors.length) {
      failures.push(`pageerrors-${vpName}: ${pageErrors.join(" | ")}`);
    }
    await context.close();
  }
} finally {
  await browser.close();
}
console.log(`\nTJ-004.4 capture: ok=${ok}/36 failures=${failures.length}`);
if (failures.length) {
  console.log(failures.join("\n"));
  process.exit(1);
}
