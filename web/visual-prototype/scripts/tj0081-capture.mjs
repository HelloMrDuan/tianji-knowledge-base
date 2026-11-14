/**
 * TJ-008.1 visual audit capture (robust, low-memory).
 *
 * Screenshots the 11 life-scenario pages (input state) + the 7 professional
 * tools pages + the bazi-profile RESULT state (real backend via vite proxy
 * to the production tunnel on :8000) at 1440 / 360 viewports, with real
 * Chromium. Checks horizontal overflow + page errors per page.
 *
 * Run:
 *   cd web/visual-prototype
 *   npm run dev -- --host 127.0.0.1 --port 4174 --strictPort  # separate shell
 *   node scripts/tj0081-capture.mjs
 *
 * Output: docs/product/evidence/tj-008.1/screenshots/ + audit JSON.
 */
import { chromium } from "@playwright/test";
import { mkdir, writeFile } from "node:fs/promises";
import { fileURLToPath } from "node:url";
import path from "node:path";

const repoRoot = fileURLToPath(new URL("../../..", import.meta.url));
const target = path.join(repoRoot, "docs/product/evidence/tj-008.1/screenshots");
await mkdir(target, { recursive: true });
const baseURL = process.env.PROTOTYPE_BASE_URL || "http://127.0.0.1:4174";

const scenarioPages = [
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
const toolPages = [
  ["tool-bazi", "/bazi"],
  ["tool-liuyao", "/liuyao"],
  ["tool-qimen", "/qimen"],
  ["tool-ziwei", "/ziwei"],
  ["tool-liuren", "/liuren"],
  ["tool-yijing", "/yijing"],
  ["tool-fengshui", "/fengshui"],
];
const viewports = [
  ["1440", { width: 1440, height: 1000 }],
  ["360", { width: 360, height: 800 }],
];

const browser = await chromium.launch({
  args: ["--no-sandbox", "--disable-dev-shm-usage", "--disable-gpu"],
});
const audit = { pages: [], failures: [], ok: 0 };
let total = 0;

async function checkPage(page, name, vpName) {
  const overflow = await page.evaluate(() => {
    const doc = document.documentElement;
    return {
      scrollWidth: doc.scrollWidth,
      clientWidth: doc.clientWidth,
      overflowX: doc.scrollWidth > doc.clientWidth,
    };
  }).catch(() => ({ scrollWidth: -1, clientWidth: -1, overflowX: false }));
  const title = await page.title().catch(() => "");
  return { name, viewport: vpName, title, overflow };
}

for (const [vpName, viewport] of viewports) {
  const context = await browser.newContext({ viewport });
  for (const [name, route] of [...scenarioPages, ...toolPages]) {
    total++;
    const page = await context.newPage();
    const errors = [];
    page.on("pageerror", (e) => errors.push(String(e).slice(0, 200)));
    try {
      await page.goto(baseURL + route, { waitUntil: "domcontentloaded", timeout: 60000 });
      await page.waitForTimeout(2500);
      const info = await checkPage(page, name, vpName);
      info.errors = errors;
      const file = `${name}-${vpName}.png`;
      await page.screenshot({ path: path.join(target, file), fullPage: false });
      audit.pages.push({ ...info, file });
      if (info.overflow.overflowX || info.errors.length > 0) {
        audit.failures.push({ ...info, kind: info.overflow.overflowX ? "overflow" : "error" });
      } else {
        audit.ok++;
      }
      console.log(`${name} ${vpName}: overflow=${info.overflow.overflowX} errors=${info.errors.length}`);
    } catch (e) {
      audit.failures.push({ name, viewport: vpName, kind: "goto", error: String(e).slice(0, 200) });
      console.log(`${name} ${vpName}: FAILED ${String(e).slice(0, 120)}`);
    } finally {
      await page.close().catch(() => {});
    }
  }
  // bazi-profile RESULT state (real backend).
  total++;
  const page = await context.newPage();
  const errors = [];
  page.on("pageerror", (e) => errors.push(String(e).slice(0, 200)));
  try {
    await page.goto(baseURL + "/bazi-profile", { waitUntil: "domcontentloaded", timeout: 60000 });
    await page.waitForTimeout(1500);
    await page.getByRole("button", { name: "填入示例" }).click();
    await page.waitForTimeout(500);
    await page.locator('button[type="submit"]').first().click();
    await page.locator('[aria-label="命盘概览"]').first().waitFor({ timeout: 60000 });
    await page.waitForTimeout(1500);
    const info = await checkPage(page, "bazi-profile-result", vpName);
    info.errors = errors;
    const file = `bazi-profile-result-${vpName}.png`;
    await page.screenshot({ path: path.join(target, file), fullPage: false });
    if (vpName === "1440") {
      await page.screenshot({ path: path.join(target, "bazi-profile-result-1440-full.png"), fullPage: true });
    }
    audit.pages.push({ ...info, file, result: true });
    if (info.overflow.overflowX || info.errors.length > 0) {
      audit.failures.push({ ...info, kind: info.overflow.overflowX ? "overflow" : "error" });
    } else {
      audit.ok++;
    }
    console.log(`bazi-profile-result ${vpName}: overflow=${info.overflow.overflowX} errors=${info.errors.length}`);
  } catch (e) {
    audit.failures.push({ name: "bazi-profile-result", viewport: vpName, kind: "result", error: String(e).slice(0, 200) });
    console.log(`bazi-profile-result ${vpName}: FAILED ${String(e).slice(0, 120)}`);
  } finally {
    await page.close().catch(() => {});
  }
  await context.close();
}
await browser.close();
audit.total = total;
await writeFile(path.join(target, "audit.json"), JSON.stringify(audit, null, 2));
console.log(`\nCAPTURE DONE ok=${audit.ok}/${total} failures=${audit.failures.length}`);
for (const f of audit.failures) console.log("FAIL:", JSON.stringify(f).slice(0, 300));
