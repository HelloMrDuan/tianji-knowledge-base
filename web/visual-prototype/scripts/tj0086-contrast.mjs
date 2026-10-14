/**
 * TJ-008.6 夜景可读性审计：对每页所有可见文本计算与有效背景的对比度，
 * 找出对比度 < 3 的元素并按最近容器类名分组，指导兜底修复。
 * 运行：node scripts/tj0086-contrast.mjs（需 vite preview 在 4174）
 */
import { chromium } from "@playwright/test";

const baseURL = process.env.PROTOTYPE_BASE_URL || "http://127.0.0.1:4174";
const pages = [
  "/", "/bazi-profile", "/daily-structure", "/weekly-structure",
  "/monthly-structure", "/yearly-structure", "/romance-structure",
  "/career-wealth-structure", "/compatibility-structure", "/ask",
  "/dream-culture", "/life-overview",
];

const lum = ([r, g, b]) => {
  const f = (c) => {
    c /= 255;
    return c <= 0.03928 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4);
  };
  return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b);
};
const ratio = (a, b) => {
  const [l1, l2] = [lum(a), lum(b)].sort((x, y) => y - x);
  return (l1 + 0.05) / (l2 + 0.05);
};
const parse = (s) => s.match(/[\d.]+/g).slice(0, 3).map(Number);

const browser = await chromium.launch({ args: ["--no-sandbox"] });
const page = await (await browser.newContext({
  viewport: { width: 1440, height: 1000 }, reducedMotion: "reduce",
})).newPage();

const byContainer = {};
for (const route of pages) {
  await page.goto(`${baseURL}${route}`, { waitUntil: "domcontentloaded" });
  await page.locator("main h1, main h2").first().waitFor({ timeout: 10000 });
  await page.waitForTimeout(500);
  const bad = await page.evaluate(() => {
    const out = [];
    const els = document.querySelectorAll("main p, main h1, main h2, main h3, main h4, main span, main a, main button, main li, main label, main small, main strong, main em, main dt, main dd, main td, main th");
    for (const el of els) {
      const r = el.getBoundingClientRect();
      if (r.width < 2 || r.height < 2) continue;
      const text = (el.textContent || "").trim().slice(0, 24);
      if (!text || el.children.length > 3) continue;
      const fg = getComputedStyle(el).color;
      let bg = null, node = el;
      while (node && node !== document.documentElement) {
        const c = getComputedStyle(node).backgroundColor;
        const m = c.match(/[\d.]+/g);
        if (m && Number(m[3] ?? 1) > 0.85) { bg = c; break; }
        node = node.parentElement;
      }
      if (!bg) bg = getComputedStyle(document.body).backgroundColor;
      out.push({ text, fg, bg, cls: el.className?.toString?.().slice(0, 40) || el.tagName });
    }
    return out;
  });
  for (const b of bad) {
    const r = ratio(parse(b.fg), parse(b.bg));
    if (r < 3) {
      const key = `${route} :: ${b.cls}`;
      (byContainer[key] ||= []).push(`"${b.text}" ${r.toFixed(2)}`);
    }
  }
}
await browser.close();

const keys = Object.keys(byContainer).sort();
console.log(`\n低对比度分组: ${keys.length}`);
for (const k of keys.slice(0, 40)) {
  const items = byContainer[k];
  console.log(`\n${k} (${items.length})`);
  for (const i of items.slice(0, 4)) console.log(`   ${i}`);
}
if (keys.length > 40) console.log(`\n…另有 ${keys.length - 40} 组未列出`);
