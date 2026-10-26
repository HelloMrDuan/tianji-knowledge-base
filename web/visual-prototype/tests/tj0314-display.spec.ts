import { expect, test, type Page } from "@playwright/test";
import { formatLunarMonth } from "../src/public/lunarConvert";

/**
 * TJ-031.4（中低批一：前端/展示三项）测试性质声明：
 * - formatLunarMonth 单元测试直接导入真实函数断言（非 stub）。
 * - 紫微请求测试走拦截/中止（intercept + abort），只验证前端提交的
 *   请求形状与客户端农历→公历换算结果，不是后端计算测试，不得
 *   冒称真实排盘。期望公历值由独立实现 lunar-python 1.4.8 核验：
 *   农历 2023-02-11（非闰）→ 公历 2023-03-02；农历 2023 年正月
 *   只有 29 天（LunarYear 月天数），故 2023-01-30 为无效农历日期。
 * - 渲染测试使用固定 fixture 响应，只验证结果页渲染（含说明与
 *   限制层分界约定句），不验证任何计算正确性。
 */

async function interceptExecute(page: Page) {
  const sent: Record<string, any>[] = [];
  await page.route("**/api/v1/public/execute", async (route) => {
    sent.push(route.request().postDataJSON());
    await route.abort("failed");
  });
  return sent;
}

async function fillZiwei(page: Page, opts: {
  calendar: string;
  leapMonth?: string;
  date: string;
  time: string;
}) {
  await page.goto("/ziwei");
  await page.locator("#field-calendar").selectOption(opts.calendar);
  if (opts.leapMonth) {
    await page.locator("#field-leapMonth").selectOption(opts.leapMonth);
  }
  await page.locator("#field-date").fill(opts.date);
  await page.locator("#field-time").fill(opts.time);
  await page.locator('form button[type="submit"]').first().click();
}

test.describe("TJ-031.4: formatLunarMonth (unit, real function)", () => {
  test("positive months render as Chinese month names", () => {
    expect(formatLunarMonth(1)).toBe("正月");
    expect(formatLunarMonth(2)).toBe("二月");
    expect(formatLunarMonth(11)).toBe("冬月");
    expect(formatLunarMonth(12)).toBe("腊月");
  });

  test("negative months render as leap-month text, never a signed number", () => {
    expect(formatLunarMonth(-2)).toBe("闰二月");
    expect(formatLunarMonth(-6)).toBe("闰六月");
  });

  test("invalid months throw instead of rendering a fallback", () => {
    expect(() => formatLunarMonth(0)).toThrow();
    expect(() => formatLunarMonth(13)).toThrow();
    expect(() => formatLunarMonth(-13)).toThrow();
    expect(() => formatLunarMonth(2.5)).toThrow();
  });
});

test.describe("TJ-031.4: ziwei lunar input (intercepted request contract, NOT a calculation test)", () => {
  test("lunar non-leap date is converted to the exact solar value before submit", async ({ page }) => {
    const sent = await interceptExecute(page);
    await fillZiwei(page, {
      calendar: "农历",
      leapMonth: "非闰月",
      date: "2023-02-11",
      time: "09:30",
    });
    await expect.poll(() => sent.length).toBe(1);
    expect(sent[0].domain).toBe("ziwei");
    expect(sent[0].variant).toBe("quanshu-lunar-iztro-mutagen-v1");
    expect(sent[0].mode).toBe("production");
    expect(sent[0].explain).toBe(false);
    expect(sent[0].input).toEqual({
      value: "2023-03-02T09:30:00+08:00",
      year_boundary: "lunar-new-year",
    });
  });

  test("solar input passes through unchanged (regression)", async ({ page }) => {
    const sent = await interceptExecute(page);
    await fillZiwei(page, {
      calendar: "公历",
      date: "1996-05-18",
      time: "09:30",
    });
    await expect.poll(() => sent.length).toBe(1);
    expect(sent[0].input).toEqual({
      value: "1996-05-18T09:30:00+08:00",
      year_boundary: "lunar-new-year",
    });
  });

  test("leap-month lunar input is explicitly rejected and never submitted", async ({ page }) => {
    const sent = await interceptExecute(page);
    await fillZiwei(page, {
      calendar: "农历",
      leapMonth: "闰月",
      date: "2023-02-15",
      time: "09:30",
    });
    await expect(page.locator(".entry-error")).toContainText("暂不支持闰月出生的排盘");
    await expect(page.locator(".entry-error")).toContainText("未提交计算");
    expect(sent.length).toBe(0);
  });

  test("invalid lunar date is rejected with a plain message and never submitted", async ({ page }) => {
    const sent = await interceptExecute(page);
    await fillZiwei(page, {
      calendar: "农历",
      leapMonth: "非闰月",
      date: "2023-01-30",
      time: "09:30",
    });
    await expect(page.locator(".entry-error")).toContainText("没有 30 日");
    expect(sent.length).toBe(0);
  });
});

test("ziwei result-page link carries the same converted solar value (fixture rendering, NOT computation)", async ({ page }) => {
  await page.route("**/api/v1/public/execute", async (route) => {
    await route.fulfill({
      status: 200,
      json: {
        domain: "ziwei",
        variant: "quanshu-lunar-iztro-mutagen-v1",
        mode: "production",
        deterministic: true,
        chart: {},
        rule_matches: [],
        trace: [],
        evidence: {},
        warnings: [],
        limitations: [],
        explanation: null,
        explanation_status: "disabled",
      },
    });
  });
  await fillZiwei(page, {
    calendar: "农历",
    leapMonth: "非闰月",
    date: "2023-02-11",
    time: "09:30",
  });
  const link = page.locator(".entry-result a.text-action");
  await expect(link).toBeVisible();
  await expect(link).toHaveAttribute(
    "href",
    `/ziwei/result?value=${encodeURIComponent("2023-03-02T09:30:00+08:00")}&year_boundary=lunar-new-year`,
  );
});

test("bazi result limitations layer always renders and states the boundary conventions (fixture rendering, NOT computation)", async ({ page }) => {
  await page.route("**/api/v1/public/execute", async (route) => {
    await route.fulfill({
      status: 200,
      json: {
        domain: "bazi",
        variant: "ziping-structural-v1",
        mode: "production",
        deterministic: true,
        chart: {
          pillars: [
            { name: "year", ganzhi: "庚午", stem: { value: "庚", ten_god: "偏财" }, branch: { value: "午", hidden_stems: [{ stem: "丁", ten_god: "正官" }] } },
            { name: "month", ganzhi: "辛巳", stem: { value: "辛", ten_god: "劫财" }, branch: { value: "巳", hidden_stems: [{ stem: "丙", ten_god: "偏印" }] } },
            { name: "day", ganzhi: "庚辰", stem: { value: "庚", ten_god: "日主" }, branch: { value: "辰", hidden_stems: [{ stem: "戊", ten_god: "偏印" }] } },
            { name: "hour", ganzhi: "甲申", stem: { value: "甲", ten_god: "偏财" }, branch: { value: "申", hidden_stems: [{ stem: "庚", ten_god: "比肩" }] } },
          ],
          day_master: { stem: "庚", element: "金", polarity: "阳" },
        },
        calendar: { solar_term: "雨水" },
        rule_matches: [],
        trace: [],
        evidence: {},
        warnings: [],
        limitations: [],
        explanation: null,
        explanation_status: "disabled",
      },
    });
  });
  await page.goto("/bazi-profile");
  await page.getByRole("button", { name: "填入示例" }).click();
  await page.getByRole("button", { name: "生成基础档案" }).click();
  const layer = page.locator(".result-limitations");
  await expect(layer).toBeVisible();
  await expect(layer).toContainText("年柱以立春交节为界");
  await expect(layer).toContainText("日柱以午夜 0 点为界");
  await expect(layer).toContainText("夜子时归当日");
});

test("leap-month checkbox label renders 闰二月 text, not a bare numeral (real UI)", async ({ page }) => {
  await page.goto("/bazi-profile");
  await page.getByRole("tab", { name: "农历" }).click();
  await page.locator(".birth-date-row select").nth(0).selectOption("2023");
  await page.locator(".birth-date-row select").nth(1).selectOption("2");
  const label = page.locator(".leap-month-check");
  await expect(label).toBeVisible();
  await expect(label).toContainText("闰二月");
  await expect(label).not.toContainText("闰2月");
});
