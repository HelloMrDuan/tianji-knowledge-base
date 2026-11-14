/**
 * TJ-008.1: verify the domain-switcher mobile fix.
 * At 360px the seven tool tabs must stay on ONE row (scrollable),
 * not wrap to two rows, and the page must have no horizontal overflow.
 * Also verifies all seven tabs are reachable by scrolling the switcher.
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
let pass = 0, fail = 0;
for (const [vpName, viewport] of [["360", { width: 360, height: 800 }], ["1440", { width: 1440, height: 1000 }]]) {
  const context = await browser.newContext({ viewport });
  const page = await context.newPage();
  const errors = [];
  page.on("pageerror", (e) => errors.push(String(e).slice(0, 200)));
  await page.goto(baseURL + "/bazi", { waitUntil: "domcontentloaded", timeout: 60000 });
  await page.waitForTimeout(2000);
  const m = await page.evaluate(() => {
    const sw = document.querySelector(".domain-switcher");
    const links = [...document.querySelectorAll(".domain-switcher a")];
    const doc = document.documentElement;
    const rows = new Set(links.map((a) => Math.round(a.getBoundingClientRect().top)));
    return {
      switcherExists: !!sw,
      tabCount: links.length,
      rows: rows.size,
      switcherScrollWidth: sw ? sw.scrollWidth : -1,
      switcherClientWidth: sw ? sw.clientWidth : -1,
      switcherScrollable: sw ? sw.scrollWidth > sw.clientWidth : false,
      switcherWrap: sw ? getComputedStyle(sw).flexWrap : "?",
      pageOverflowX: doc.scrollWidth > doc.clientWidth,
      tabNames: links.map((a) => a.textContent.trim().slice(0, 6)),
    };
  });
  console.log(`${vpName}: tabs=${m.tabCount} rows=${m.rows} wrap=${m.switcherWrap} ` +
    `switcherScrollable=${m.switcherScrollable} (${m.switcherScrollWidth} > ${m.switcherClientWidth}) ` +
    `pageOverflowX=${m.pageOverflowX} errors=${errors.length}`);
  console.log(`  tabs: ${m.tabNames.join(" | ")}`);
  // At 360 the switcher must be exactly one row and scrollable (7 tabs
  // cannot fit 360px); at 1440 it must be one row and not scroll.
  const ok = m.tabCount === 7 && m.rows === 1 && !m.pageOverflowX && errors.length === 0 &&
    (vpName === "360" ? m.switcherScrollable : !m.switcherScrollable);
  if (ok) { pass++; console.log(`  PASS ${vpName}`); }
  else { fail++; console.log(`  FAIL ${vpName}`); }
  // Screenshot after fix.
  await page.screenshot({ path: path.join(target, `tool-bazi-fixed-${vpName}.png`), fullPage: false });
  // At 360, scroll the switcher to the end and confirm the last tab (风水) is visible.
  if (vpName === "360") {
    await page.evaluate(() => {
      document.querySelector(".domain-switcher").scrollLeft = 9999;
    });
    await page.waitForTimeout(400);
    const last = await page.evaluate(() => {
      const links = [...document.querySelectorAll(".domain-switcher a")];
      const last = links[links.length - 1];
      const r = last.getBoundingClientRect();
      const sw = document.querySelector(".domain-switcher").getBoundingClientRect();
      return { name: last.textContent.trim(), visible: r.left >= sw.left && r.right <= sw.right + 1 };
    });
    console.log(`  scrolled-to-end last tab: ${last.name} visible=${last.visible}`);
    if (last.visible) pass++; else fail++;
    await page.screenshot({ path: path.join(target, "tool-bazi-fixed-360-scrolled.png"), fullPage: false });
  }
  await context.close();
}
await browser.close();
console.log(`\nSWITCHER VERIFY pass=${pass} fail=${fail}`);
process.exit(fail > 0 ? 1 : 0);
