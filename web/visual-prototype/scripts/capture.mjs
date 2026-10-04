import { chromium } from "@playwright/test";
import { mkdir } from "node:fs/promises";
import { fileURLToPath } from "node:url";

const target = fileURLToPath(
  new URL(
    "../../../docs/phase5/visual-prototype/screenshots/",
    import.meta.url,
  ),
);
const baseURL = process.env.PROTOTYPE_BASE_URL || "http://127.0.0.1:4174";
await mkdir(target, { recursive: true });
const browser = await chromium.launch({
  executablePath: process.env.PROTOTYPE_CHROMIUM || undefined,
  args: ["--no-sandbox"],
});
try {
  for (const [device, viewport] of [
    ["desktop", { width: 1440, height: 1000 }],
    ["mobile", { width: 390, height: 844 }],
  ]) {
    const context = await browser.newContext({
      viewport,
      deviceScaleFactor: 1,
      reducedMotion: "reduce",
    });
    const page = await context.newPage();
    const routes = [
      ["home", "/"],
      ...[
        "bazi",
        "liuyao",
        "qimen",
        "ziwei",
        "liuren",
        "yijing",
        "fengshui",
      ].flatMap((id) => [
        [id + "-home", "/" + id],
        [id + "-result", "/" + id + "/result"],
      ]),
      ["history", "/history"],
      ["favorites", "/favorites"],
      ["admin-dashboard", "/admin"],
      ...[
        "classics",
        "rules",
        "evidence",
        "chapters",
        "terms",
        "sources",
        "layers",
        "conflicts",
        "algorithms",
        "providers",
        "prompts",
        "evaluations",
        "failures",
        "users",
        "logs",
      ].map((id) => ["admin-" + id, "/admin/" + id]),
    ];
    for (const [name, route] of routes) {
      await page.goto(`${baseURL}${route}`);
      await page.locator("main h1").waitFor();
      await page.evaluate(() => document.fonts.ready);
      await page.screenshot({
        path: `${target}/${name}-${device}.png`,
        fullPage: device === "desktop",
        animations: "disabled",
      });
      console.log(`${name}-${device}.png`);
      if (device === "mobile")
        await page.screenshot({
          path: `${target}/${name}-mobile-full.png`,
          fullPage: true,
          animations: "disabled",
        });
      if (device === "mobile" && name === "liuyao-result") {
        await page.locator("#chart").scrollIntoViewIfNeeded();
        await page.evaluate(() =>
          document
            .querySelector("#chart")
            .scrollIntoView({ block: "start", behavior: "instant" }),
        );
        await page.screenshot({
          path: `${target}/liuyao-chart-mobile.png`,
          animations: "disabled",
        });
      }
    }
    await context.close();
  }
} finally {
  await browser.close();
}
