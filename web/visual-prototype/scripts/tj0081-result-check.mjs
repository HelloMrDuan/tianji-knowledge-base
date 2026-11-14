/**
 * TJ-008.1: verify result states for daily-structure + romance-structure
 * (closes the TJ-004.4 gap for the two most-used scenarios after bazi).
 * Submits a real birth via the sample button and captures the result.
 */
import { chromium } from "@playwright/test";
import { mkdir } from "node:fs/promises";
import { fileURLToPath } from "node:url";
import path from "node:path";

const repoRoot = fileURLToPath(new URL("../../..", import.meta.url));
const target = path.join(repoRoot, "docs/product/evidence/tj-008.1/screenshots");
await mkdir(target, { recursive: true });
const baseURL = process.env.PROTOTYPE_BASE_URL || "http://127.0.0.1:4174";

const browser = await chromium.launch({ args: ["--no-sandbox", "--disable-dev-shm-usage", "--disable-gpu"] });
const results = [];
for (const [name, route, resultSelector] of [
  ["daily-structure-result", "/daily-structure", null],
  ["romance-structure-result", "/romance-structure", null],
]) {
  for (const [vpName, viewport] of [["1440", { width: 1440, height: 1000 }]]) {
    const context = await browser.newContext({ viewport });
    const page = await context.newPage();
    const errors = [];
    page.on("pageerror", (e) => errors.push(String(e).slice(0, 200)));
    try {
      await page.goto(baseURL + route, { waitUntil: "domcontentloaded", timeout: 60000 });
      await page.waitForTimeout(1500);
      // Fill sample if available.
      const sample = page.getByRole("button", { name: "填入示例" });
      if (await sample.count() > 0) await sample.click();
      await page.waitForTimeout(500);
      await page.locator('button[type="submit"]').first().click();
      // Wait for a result section to appear (any of the known result markers).
      await page.waitForTimeout(8000);
      const overflow = await page.evaluate(() => {
        const doc = document.documentElement;
        return { scrollWidth: doc.scrollWidth, clientWidth: doc.clientWidth, overflowX: doc.scrollWidth > doc.clientWidth };
      });
      const bodyText = (await page.locator("body").innerText()).slice(0, 400);
      const file = `${name}-${vpName}.png`;
      await page.screenshot({ path: path.join(target, file), fullPage: false });
      await page.screenshot({ path: path.join(target, `${name}-${vpName}-full.png`), fullPage: true });
      results.push({ name, viewport: vpName, overflow, errors, bodyText: bodyText.replace(/\n/g, " | ").slice(0, 300) });
      console.log(`${name} ${vpName}: overflow=${overflow.overflowX} errors=${errors.length}`);
      console.log("  body:", bodyText.replace(/\n/g, " | ").slice(0, 250));
    } catch (e) {
      results.push({ name, viewport: vpName, error: String(e).slice(0, 200) });
      console.log(`${name} ${vpName}: FAILED ${String(e).slice(0, 150)}`);
    } finally {
      await page.close().catch(() => {});
    }
    await context.close();
  }
}
await browser.close();
console.log("RESULT CHECK DONE", JSON.stringify(results.map(r => ({ name: r.name, overflow: r.overflow, errors: (r.errors||[]).length, error: r.error || null }))));
