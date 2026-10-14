/**
 * TJ-008.6 双主题基础验证（真实 Chromium）。
 *
 * 覆盖（1440 / 390 / 360）：
 *   1. 默认主题为深青夜景（新鲜上下文，data-theme=night，深色底）
 *   2. 切换按钮可见可点；切换后为米白宣纸（浅色底）
 *   3. 刷新后偏好保持（localStorage）
 *   4. 非法存储值回退为默认夜景
 *   5. SPA 路由切换保持主题
 *   6. 无横向溢出；移动端切换入口可见
 *   7. 音乐播放不受主题机制影响（冒烟）
 *   8. 截图归档至 docs/product/evidence/tj-008.6/
 *
 * 运行：npm run build 后起 vite preview（4174），再 node scripts/tj0086-theme.mjs
 * 验收：全部 CHECK 为 PASS；任一 FAIL 则非零退出。
 */
import { chromium } from "@playwright/test";
import { mkdir } from "node:fs/promises";
import { fileURLToPath } from "node:url";
import path from "node:path";

const repoRoot = fileURLToPath(new URL("../../..", import.meta.url));
const shots = path.join(repoRoot, "docs/product/evidence/tj-008.6");
await mkdir(shots, { recursive: true });
const baseURL = process.env.PROTOTYPE_BASE_URL || "http://127.0.0.1:4174";

const results = [];
const check = (name, cond, extra = "") => {
  results.push([name, !!cond]);
  console.log(`${cond ? "PASS" : "FAIL"} ${name}${extra ? " " + extra : ""}`);
};

const themeState = (page) =>
  page.evaluate(() => ({
    attr: document.documentElement.getAttribute("data-theme"),
    stored: (() => { try { return localStorage.getItem("tianji.theme"); } catch { return "n/a"; } })(),
    bodyBg: getComputedStyle(document.body).backgroundColor,
  }));

const noOverflow = (page) =>
  page.evaluate(() => document.documentElement.scrollWidth <= document.documentElement.clientWidth + 1);

const browser = await chromium.launch({ args: ["--no-sandbox"] });
try {
  for (const [vp, viewport] of [
    ["1440", { width: 1440, height: 1000 }],
    ["390", { width: 390, height: 844 }],
    ["360", { width: 360, height: 800 }],
  ]) {
    const tag = `[${vp}]`;

    // 1. 默认夜景
    const ctx1 = await browser.newContext({ viewport, reducedMotion: "reduce" });
    const p1 = await ctx1.newPage();
    await p1.goto(`${baseURL}/`, { waitUntil: "domcontentloaded" });
    await p1.locator("main h1, main h2").first().waitFor({ timeout: 10000 });
    await p1.waitForTimeout(500);
    let st = await themeState(p1);
    check(`${tag} default-is-night`, st.attr === "night", JSON.stringify(st));
    const toggle = p1.locator(".theme-toggle");
    check(`${tag} toggle-visible`, await toggle.isVisible());
    await p1.screenshot({ path: path.join(shots, `home-night-${vp}.png`), animations: "disabled" });

    // 2. 切换为宣纸
    await toggle.click();
    await p1.waitForTimeout(400);
    st = await themeState(p1);
    check(`${tag} toggle-to-paper`, st.attr === "paper" && st.stored === "paper", JSON.stringify(st));
    await p1.screenshot({ path: path.join(shots, `home-paper-${vp}.png`), animations: "disabled" });

    // 3. 刷新保持
    await p1.reload({ waitUntil: "domcontentloaded" });
    await p1.locator("main h1, main h2").first().waitFor({ timeout: 10000 });
    st = await themeState(p1);
    check(`${tag} persists-after-reload`, st.attr === "paper", JSON.stringify(st));

    // 5. SPA 路由保持主题
    await p1.locator('main a[href="/daily-structure"]').first().click();
    await p1.waitForTimeout(700);
    st = await themeState(p1);
    check(`${tag} keeps-theme-across-spa-route`, st.attr === "paper", JSON.stringify(st));

    // 6. 无横向溢出
    check(`${tag} no-horizontal-overflow`, await noOverflow(p1));

    // 切回夜景再截一张场景页
    await p1.locator(".theme-toggle").click();
    await p1.waitForTimeout(400);
    await p1.screenshot({ path: path.join(shots, `daily-night-${vp}.png`), animations: "disabled" });
    check(`${tag} no-overflow-night`, await noOverflow(p1));
    await ctx1.close();

    // 4. 非法值回退
    const ctx2 = await browser.newContext({ viewport, reducedMotion: "reduce" });
    await ctx2.addInitScript(() => {
      try { localStorage.setItem("tianji.theme", "neon-pink"); } catch {}
    });
    const p2 = await ctx2.newPage();
    await p2.goto(`${baseURL}/`, { waitUntil: "domcontentloaded" });
    await p2.locator("main h1, main h2").first().waitFor({ timeout: 10000 });
    st = await themeState(p2);
    check(`${tag} invalid-value-falls-back`, st.attr === "night", JSON.stringify(st));
    await ctx2.close();
  }

  // 7. 音乐冒烟（夜景下播放/暂停正常）
  const ctx3 = await browser.newContext({ viewport: { width: 1440, height: 1000 } });
  const p3 = await ctx3.newPage();
  await p3.goto(`${baseURL}/`, { waitUntil: "domcontentloaded" });
  await p3.locator("main h1, main h2").first().waitFor({ timeout: 10000 });
  await p3.locator("button.music-trigger").click();
  await p3.waitForTimeout(200);
  await p3.locator(".music-play").click();
  await p3.waitForTimeout(900);
  const playing = await p3.evaluate(() => {
    const a = document.querySelector("audio");
    return a ? !a.paused : false;
  });
  check(`[music] plays-under-night-theme`, playing);
  await ctx3.close();
} finally {
  await browser.close();
}
const failed = results.filter(([, ok]) => !ok);
console.log(`\nTJ-008.6 theme: pass=${results.length - failed.length}/${results.length}`);
if (failed.length) process.exit(1);
