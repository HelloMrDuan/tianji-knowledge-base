/**
 * TJ-004.4 music player verification (real Chromium, real audio element).
 *
 * Covers, on desktop (1440) and mobile (390):
 *   1. default: no autoplay (fresh context, audio paused, optedIn=false)
 *   2. trigger opens the music popover
 *   3. user play -> audio actually playing (/music/quiet-waters.ogg)
 *   4. volume slider -> audio.volume changes + localStorage persists
 *   5. SPA route change (/ -> /romance-structure) keeps playing
 *   6. global pause button stops playback
 *   7. entering /admin stops playback (separate app root unmounts player)
 *
 * Run:
 *   cd web/visual-prototype
 *   npm run build
 *   npx vite preview --port 4174 --host 127.0.0.1   # separate shell
 *   node scripts/tj0044-music.mjs
 *
 * Acceptance: every CHECK line prints PASS; any FAIL exits non-zero.
 */
import { chromium } from "@playwright/test";
import { mkdir } from "node:fs/promises";
import { fileURLToPath } from "node:url";
import path from "node:path";

const repoRoot = fileURLToPath(new URL("../../..", import.meta.url));
const shots = path.join(repoRoot, "docs/product/evidence/tj-004.4/screenshots");
await mkdir(shots, { recursive: true });
const baseURL = process.env.PROTOTYPE_BASE_URL || "http://127.0.0.1:4174";

const results = [];
const check = (name, cond, extra = "") => {
  results.push([name, !!cond]);
  console.log(`${cond ? "PASS" : "FAIL"} ${name}${extra ? " " + extra : ""}`);
};

const browser = await chromium.launch({ args: ["--no-sandbox"] });
try {
  for (const [vp, viewport] of [["1440", { width: 1440, height: 1000 }], ["390", { width: 390, height: 844 }]]) {
    const context = await browser.newContext({ viewport, reducedMotion: "reduce" });
    const page = await context.newPage();
    const tag = `[${vp}]`;

    // 1. default: no autoplay on fresh load
    await page.goto(`${baseURL}/`, { waitUntil: "domcontentloaded" });
    await page.locator("main h1, main h2").first().waitFor({ timeout: 10000 });
    await page.waitForTimeout(800);
    let st = await page.evaluate(() => {
      const a = document.querySelector("audio");
      return a ? { paused: a.paused, src: a.currentSrc || a.src } : null;
    });
    check(`${tag} default-no-autoplay`, st && st.paused && /quiet-waters\.ogg$/.test(st.src), JSON.stringify(st));

    // 2. trigger opens popover
    await page.locator("button.music-trigger").click();
    await page.waitForTimeout(300);
    check(`${tag} popover-opens`, await page.locator(".music-popover").isVisible());
    await page.screenshot({ path: path.join(shots, `music-popover-${vp}.png`), animations: "disabled" });

    // 3. user play -> really playing
    await page.locator(".music-play").click();
    await page.waitForTimeout(900);
    st = await page.evaluate(() => {
      const a = document.querySelector("audio");
      return a ? { paused: a.paused, vol: a.volume, err: a.error ? a.error.code : 0 } : null;
    });
    check(`${tag} user-play`, st && !st.paused && st.err === 0, JSON.stringify(st));

    // 4. volume + persistence
    const slider = page.locator('.music-popover input[type="range"]');
    check(`${tag} volume-slider-visible`, await slider.isVisible());
    await slider.fill("0.6");
    await page.waitForTimeout(300);
    st = await page.evaluate(() => ({
      vol: document.querySelector("audio")?.volume,
      stored: localStorage.getItem("tianji.prototype.music"),
    }));
    check(`${tag} volume-persists`, st.vol === 0.6 && /"volume":0\.6/.test(st.stored || ""), JSON.stringify(st));

    // 5. SPA route change keeps playing
    await page.locator('button[aria-label="关闭音乐设置"]').click();
    await page.locator('main a[href="/daily-structure"]').first().click();
    await page.waitForTimeout(900);
    st = await page.evaluate(() => ({
      paused: document.querySelector("audio")?.paused,
      url: location.pathname,
    }));
    check(`${tag} spa-route-keeps-playing`, st.paused === false && st.url === "/daily-structure", JSON.stringify(st));

    // 6. global pause
    const gpause = page.locator('button[aria-label="全局暂停音乐"]');
    check(`${tag} global-pause-visible`, await gpause.isVisible().catch(() => false));
    if (await gpause.isVisible().catch(() => false)) {
      await gpause.click();
      await page.waitForTimeout(400);
      const paused = await page.evaluate(() => document.querySelector("audio")?.paused ?? null);
      check(`${tag} global-pause-works`, paused === true);
    }

    // 7. entering /admin stops playback
    await page.goto(`${baseURL}/`, { waitUntil: "domcontentloaded" });
    await page.waitForTimeout(400);
    await page.locator("button.music-trigger").click();
    await page.waitForTimeout(200);
    await page.locator(".music-play").click();
    await page.waitForTimeout(900);
    const playingBefore = await page.evaluate(() => {
      const a = document.querySelector("audio");
      return a ? !a.paused : false;
    });
    await page.goto(`${baseURL}/admin`, { waitUntil: "domcontentloaded" });
    await page.waitForTimeout(900);
    const adminState = await page.evaluate(() => ({
      hasPublicAudio: !!document.querySelector(".music-player audio"),
      url: location.pathname,
    }));
    check(
      `${tag} admin-stops-music`,
      playingBefore && adminState.url === "/admin" && !adminState.hasPublicAudio,
      JSON.stringify({ playingBefore, ...adminState }),
    );

    await context.close();
  }
} finally {
  await browser.close();
}
const failed = results.filter(([, ok]) => !ok);
console.log(`\nTJ-004.4 music: pass=${results.length - failed.length}/${results.length}`);
if (failed.length) process.exit(1);
