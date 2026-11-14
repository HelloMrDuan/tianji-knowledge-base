/**
 * TJ-008.1: professional-tool tab bar (domain-switcher) must stay on one
 * row at mobile width.
 *
 * REGRESSION: before this fix `.domain-switcher` used `flex-wrap: wrap`,
 * so at 360px the seven tool tabs wrapped to two rows (5 + 2), wasting
 * vertical space and looking broken. The fix makes it a single
 * horizontally scrollable row below 760px (the standard tab-bar pattern);
 * the scroll is contained inside the switcher, so the page itself must
 * still have zero horizontal overflow.
 *
 * WHAT THIS SPEC PROVES (and does not prove):
 * - At 360px: exactly 7 tabs, exactly 1 row, switcher is scrollable
 *   (scrollWidth > clientWidth), page has no horizontal overflow, and
 *   the last tab (风水) becomes visible after scrolling the switcher
 *   to its end. Nothing here proves engine behavior or any other page.
 * - At 1440px: the desktop layout is unchanged — 1 row, no scroll
 *   (tabs fit), no page overflow.
 * - No backend is required: the tool home page renders its tab bar
 *   without any API call.
 */
import { test, expect } from "@playwright/test";

const TOOL_TABS = ["八字", "六爻", "奇门遁甲", "紫微斗数", "大六壬", "周易", "风水"];

async function switcherState(page: import("@playwright/test").Page) {
  return page.evaluate(() => {
    const sw = document.querySelector(".domain-switcher") as HTMLElement | null;
    const links = [...document.querySelectorAll(".domain-switcher a")];
    const doc = document.documentElement;
    const rows = new Set(
      links.map((a) => Math.round(a.getBoundingClientRect().top)),
    );
    // Each link is <span>{glyph}</span>{name}; the name is the trailing
    // text node, not the glyph. Use lastChild so the assertion matches
    // the visible tool name, not "八八字".
    const nameOf = (a: Element) =>
      (a.lastChild?.textContent ?? "").trim();
    return {
      exists: !!sw,
      tabCount: links.length,
      tabNames: links.map(nameOf),
      rows: rows.size,
      flexWrap: sw ? getComputedStyle(sw).flexWrap : "?",
      scrollable: sw ? sw.scrollWidth > sw.clientWidth : false,
      pageOverflowX: doc.scrollWidth - doc.clientWidth,
    };
  });
}

test.describe("TJ-008.1 domain-switcher mobile single row", () => {
  test("360px: seven tabs on one scrollable row, no page overflow", async ({
    page,
  }) => {
    await page.setViewportSize({ width: 360, height: 800 });
    await page.goto("/bazi");
    const s = await switcherState(page);
    expect(s.exists).toBe(true);
    expect(s.tabCount).toBe(7);
    expect(s.tabNames).toEqual(TOOL_TABS);
    expect(s.rows).toBe(1);
    expect(s.flexWrap).toBe("nowrap");
    expect(s.scrollable).toBe(true);
    expect(s.pageOverflowX).toBe(0);
  });

  test("360px: last tab (风水) reachable by scrolling the switcher", async ({
    page,
  }) => {
    await page.setViewportSize({ width: 360, height: 800 });
    await page.goto("/bazi");
    await page.evaluate(() => {
      const sw = document.querySelector(".domain-switcher") as HTMLElement;
      sw.scrollLeft = sw.scrollWidth;
    });
    const last = await page.evaluate(() => {
      const links = [...document.querySelectorAll(".domain-switcher a")];
      const lastLink = links[links.length - 1] as HTMLElement;
      const r = lastLink.getBoundingClientRect();
      const sw = document
        .querySelector(".domain-switcher")!
        .getBoundingClientRect();
      return {
        name: (lastLink.lastChild?.textContent ?? "").trim(),
        visible: r.left >= sw.left - 1 && r.right <= sw.right + 1,
      };
    });
    expect(last.name).toBe("风水");
    expect(last.visible).toBe(true);
  });

  test("1440px: desktop layout unchanged — one row, no scroll, no overflow", async ({
    page,
  }) => {
    await page.setViewportSize({ width: 1440, height: 1000 });
    await page.goto("/bazi");
    const s = await switcherState(page);
    expect(s.exists).toBe(true);
    expect(s.tabCount).toBe(7);
    expect(s.rows).toBe(1);
    expect(s.scrollable).toBe(false);
    expect(s.pageOverflowX).toBe(0);
  });
});
