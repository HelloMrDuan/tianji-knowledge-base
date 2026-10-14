/**
* TJ-008.6 夜景/宣纸文字对比度门禁（真实 Chromium）。
*
* 对每页重点区域（导航、Hero 标题/副标题/正文、按钮、场景卡片、表单标题）
* 计算文本与有效背景的对比度：
* - 普通文本 WCAG AA 4.5:1，大号文本（≥24px，或 ≥18.66px 加粗）3:1
* - 任一可验证元素不达标 → 打印 FAIL 并以非零退出
*
* 渐变 / 图片 / 半透明叠加背景无法准确计算：
* - 祖先链上存在 backgroundImage（渐变、SVG 纹理、图片）时，该元素记为
* UNVERIFIABLE，仅报告、不参与失败判定，需人工看截图复核；
* - 半透明背景（alpha < 0.95）会与下层纯色合成后再计算，为近似值。
*
* 运行：npm run build 后起 vite preview（4174），再 node scripts/tj0086-contrast.mjs
* 可用 THEME=paper|night 指定主题（默认 night）。
*/
import { chromium} from "@playwright/test";

const baseURL = process.env.PROTOTYPE_BASE_URL || "http://127.0.0.1:4174";
const THEME = process.env.THEME === "paper"? "paper": "night";
const pages = [
"/", "/bazi-profile", "/daily-structure", "/weekly-structure",
"/monthly-structure", "/yearly-structure", "/romance-structure",
"/career-wealth-structure", "/compatibility-structure", "/ask",
"/dream-culture", "/life-overview",
];
// 每页重点检查的选择器（文本必须可读）
const KEY_SELECTORS = [
".public-brand", ".public-nav a", ".theme-toggle", ".music-trigger",
"main h1", "main h2", "main h3", "main.eyebrow",
"main.button", "main p", "main li", "main label span", "main small",
];

const lum = ([r, g, b]) => {
const f = (c) => { c /= 255; return c <= 0.03928? c / 12.92: Math.pow((c + 0.055) / 1.055, 2.4);};
return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b);
};
const ratio = (a, b) => { const [l1, l2] = [lum(a), lum(b)].sort((x, y) => y - x); return (l1 + 0.05) / (l2 + 0.05);};
const px = (s) => parseFloat(s) || 0;

const browser = await chromium.launch({ args: ["--no-sandbox"]});
const failures = [];
const unverifiable = [];
try {
const ctx = await browser.newContext({ viewport: { width: 1440, height: 1000}, reducedMotion: "reduce"});
const page = await ctx.newPage();
for (const route of pages) {
await page.goto(`${baseURL}${route}`, { waitUntil: "domcontentloaded"});
await page.evaluate((t) => {
try { localStorage.setItem("tianji.theme", t);} catch {}
document.documentElement.setAttribute("data-theme", t);
}, THEME);
await page.reload({ waitUntil: "domcontentloaded"});
await page.locator("main h1, main h2").first().waitFor({ timeout: 10000});
await page.waitForTimeout(400);

const items = await page.evaluate((selectors) => {
const seen = new Set();
const out = [];
for (const sel of selectors) {
for (const el of document.querySelectorAll(sel)) {
if (seen.has(el)) continue;
seen.add(el);
const r = el.getBoundingClientRect();
const text = (el.textContent || "").trim().replace(/\s+/g, " ").slice(0, 30);
if (r.width < 2 || r.height < 2 ||!text) continue;
const cs = getComputedStyle(el);
// 有效背景：向上找第一个不透明纯色；遇到渐变/图片则不可验证
let bg = null, bgEl = null, blocked = null, node = el;
const layers = [];
while (node && node!== document.documentElement) {
const ncs = getComputedStyle(node);
if (ncs.backgroundImage!== "none") { blocked = (node.className?.toString?.().split(" ")[0] || node.tagName); break;}
const m = ncs.backgroundColor.match(/[\d.]+/g).map(Number);
layers.push({ a: m[3]?? 1, c: m.slice(0, 3)});
if ((m[3]?? 1) >= 0.95) { bg = m.slice(0, 3); bgEl = node; break;}
node = node.parentElement;
}
if (blocked) { out.push({ text, sel: el.className?.toString?.().slice(0, 36) || el.tagName, unverifiable: blocked}); continue;}
if (!bg) {
const bm = getComputedStyle(document.body).backgroundColor.match(/[\d.]+/g).map(Number);
bg = bm.slice(0, 3); bgEl = "body";
} else if (layers.length > 1) {
// 半透明合成（近似）
let [cr, cg, cb] = bg;
for (let i = layers.length - 2; i >= 0; i--) {
const l = layers[i], a = l.a;
cr = l.c[0] * a + cr * (1 - a); cg = l.c[1] * a + cg * (1 - a); cb = l.c[2] * a + cb * (1 - a);
}
bg = [cr, cg, cb];
}
out.push({
text, sel: el.className?.toString?.().slice(0, 36) || el.tagName,
fg: cs.color.match(/[\d.]+/g).slice(0, 3).map(Number),
bg, bgEl: (bgEl?.className?.toString?.().split(" ")[0] || bgEl),
size: parseFloat(cs.fontSize) || 0, weight: parseFloat(cs.fontWeight) || 0,
});
}
}
return out;
}, KEY_SELECTORS);

for (const it of items) {
if (it.unverifiable) { unverifiable.push(`${route}:: ${it.sel} "${it.text}"（背景含渐变/图片：${it.unverifiable}，需人工看截图）`); continue;}
const large = it.size >= 24 || (it.size >= 18.66 && it.weight >= 700);
const need = large? 3: 4.5;
const r = ratio(it.fg, it.bg);
if (r < need) failures.push(`${route}:: ${it.sel} "${it.text}" 对比度 ${r.toFixed(2)} < ${need}（${large? "大号": "普通"}文本，字号 ${it.size}px）`);
}
}
} finally {
  await browser.close();
}

// 定点抽查：页面级渐变底（public-app 夜景 wash）上的关键文字。
// 近似假设：以页面基色（夜景 #0b1c23 / 宣纸 #f7f4ec）为背景计算；wash 为弱透明径向渐变，
// 实际渲染略亮于基色，结论为近似值，最终以截图人工复核为准。
// 注意：此处重新启动浏览器（主循环已在 finally 中关闭）。
console.log(`\n===== 对比度门禁 [${THEME}] =====`);
console.log(`失败: ${failures.length}，不可验证（需人工看截图）: ${unverifiable.length}`);
for (const f of failures) console.log(`FAIL ${f}`);
const SPOT_BG = THEME === "night" ? [11, 28, 35] : [247, 244, 236];
// 英雄区 h1 位于浅色卡片上（夜景重设为深墨色），用卡片近似底色单独校验
const SPOT_CARD_BG = [245, 242, 234];
const SPOT_CHECKS = [
  ["/", ".hero-copy h1", true, SPOT_BG],
  ["/", ".hero-copy > p", false, SPOT_BG],
  ["/", ".public-nav a", false, SPOT_BG],
  ["/", ".theme-toggle", false, SPOT_BG],
  ["/", ".professional-note", false, SPOT_BG],
  ["/", ".home-music-hint small", false, SPOT_BG],
  ["/romance-structure", ".romance-hero h1", true, SPOT_CARD_BG],
  ["/daily-structure", ".daily-hero h1", true, SPOT_CARD_BG],
];
const spotFails = [];
{
  const browser2 = await chromium.launch({ args: ["--no-sandbox"] });
  try {
  const ctx2 = await browser2.newContext({ viewport: { width: 1440, height: 1000 }, reducedMotion: "reduce" });
  const sp = await ctx2.newPage();
  for (const [route, sel, large, bg] of SPOT_CHECKS) {
    await sp.goto(`${baseURL}${route}`, { waitUntil: "domcontentloaded" });
    await sp.evaluate((t) => {
      try { localStorage.setItem("tianji.theme", t); } catch {}
      document.documentElement.setAttribute("data-theme", t);
    }, THEME);
    await sp.reload({ waitUntil: "domcontentloaded" });
    await sp.locator("main h1, main h2").first().waitFor({ timeout: 10000 });
    const items = await sp.evaluate((s) => {
      const out = [];
      for (const el of document.querySelectorAll(s)) {
        const r = el.getBoundingClientRect();
        const text = (el.textContent || "").trim().replace(/\s+/g, " ").slice(0, 30);
        if (r.width < 2 || !text) continue;
        const cs = getComputedStyle(el);
        out.push({ text, fg: cs.color.match(/[\d.]+/g).slice(0, 3).map(Number), size: parseFloat(cs.fontSize) || 0, weight: parseFloat(cs.fontWeight) || 0 });
      }
      return out;
    }, sel);
    for (const it of items) {
      const isLarge = large || it.size >= 24 || (it.size >= 18.66 && it.weight >= 700);
      const need = isLarge ? 3 : 4.5;
      const r = ratio(it.fg, bg);
      const mark = r < need ? "FAIL" : "ok";
      if (r < need) spotFails.push(`${route} :: ${sel} "${it.text}" ≈${r.toFixed(2)} < ${need}`);
      else console.log(`${mark}  [抽查] ${route} :: ${sel} ≈${r.toFixed(2)} ≥ ${need}`);
    }
  }
  await ctx2.close();
  } finally {
    await browser2.close();
  }
}
for (const f of spotFails) console.log(`FAIL ${f}`);
if (spotFails.length) failures.push(...spotFails);
if (unverifiable.length) {
console.log(`\n--- 不可验证项（渐变/图片背景，脚本无法准确计算）---`);
const seen = new Set();
for (const u of unverifiable) { if (!seen.has(u)) { seen.add(u); console.log(`SKIP ${u}`);}}
}
if (failures.length) { console.log(`\n对比度门禁未通过`); process.exit(1);}
console.log(`\n对比度门禁通过`);
