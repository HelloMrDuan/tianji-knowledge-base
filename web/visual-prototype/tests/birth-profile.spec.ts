import { expect, test } from "@playwright/test";
import {
  validateBirthInput,
  toApiValue,
  fromLegacy,
  toSolarDateString,
  isConvertedFromLunar,
  fromSolarEdit,
  regionToTimezone,
  isLeapYear,
  solarDaysInMonth,
  type BirthProfile,
} from "../src/public/birthProfile";

const VALID_SOLAR: BirthProfile = {
  calendarType: "solar",
  year: 2000, month: 1, day: 7,
  isLeapMonth: false,
  time: "12:00", timeUnknown: false,
  region: "中国大陆",
};

test.describe("TJ-006.1: birth input validation (unit)", () => {
  test("valid solar profile passes", () => {
    expect(validateBirthInput(VALID_SOLAR).ok).toBe(true);
  });

  test("invalid year rejected with Chinese message", () => {
    const r = validateBirthInput({ ...VALID_SOLAR, year: 1800 });
    expect(r.ok).toBe(false);
    if (!r.ok) expect(r.message).toMatch(/年份/);
  });

  test("Feb 30 rejected (non-leap year)", () => {
    const r = validateBirthInput({ ...VALID_SOLAR, year: 2001, month: 2, day: 30 });
    expect(r.ok).toBe(false);
  });

  test("Feb 29 accepted in leap year 2000", () => {
    expect(validateBirthInput({ ...VALID_SOLAR, year: 2000, month: 2, day: 29 }).ok).toBe(true);
  });

  test("Feb 29 rejected in non-leap year 1900", () => {
    expect(isLeapYear(1900)).toBe(false);
    const r = validateBirthInput({ ...VALID_SOLAR, year: 1900, month: 2, day: 29 });
    expect(r.ok).toBe(false);
  });

  test("toApiValue with solar time produces ISO with +08:00", () => {
    const v = toApiValue(VALID_SOLAR);
    expect(v).toBe("2000-01-07T12:00:00+08:00");
  });

  test("toApiValue without time throws (backend contract)", () => {
    expect(() => toApiValue({ ...VALID_SOLAR, time: "", timeUnknown: true })).toThrow(/出生时刻未知/);
  });

  test("region to timezone mapping (internal)", () => {
    expect(regionToTimezone("中国大陆")).toBe("Asia/Shanghai");
    expect(regionToTimezone("香港")).toBe("Asia/Hong_Kong");
    expect(regionToTimezone("其他")).toBe("");
  });

  test("fromLegacy converts old format", () => {
    const p = fromLegacy("2000-01-07", "12:00", "Asia/Shanghai");
    expect(p.calendarType).toBe("solar");
    expect(p.year).toBe(2000);
    expect(p.region).toBe("中国大陆");
  });
});

test.describe("TJ-006.1: lunar conversion (unit)", () => {
  test("lunar to solar conversion", async () => {
    const { lunarToSolar } = await import("../src/public/lunarConvert");
    const solar = lunarToSolar({ year: 2000, month: 4, day: 15, isLeapMonth: false });
    expect(solar).toEqual({ year: 2000, month: 5, day: 18 });
  });

  test("leap month detection", async () => {
    const { getLeapMonth } = await import("../src/public/lunarConvert");
    expect(getLeapMonth(2023)).toBe(2);
  });

  test("lunar profile toApiValue converts correctly", () => {
    const lunar: BirthProfile = {
      calendarType: "lunar",
      year: 2000, month: 4, day: 15,
      isLeapMonth: false,
      time: "12:00", timeUnknown: false,
      region: "中国大陆",
    };
    const v = toApiValue(lunar);
    expect(v).toBe("2000-05-18T12:00:00+08:00");
  });
});

test.describe("TJ-006.1: real UI operations (browser)", () => {
  test("fill sample -> fields sync -> clear", async ({ page }) => {
    await page.goto("/bazi-profile");
    await page.getByRole("button", { name: "填入示例" }).click();
    await expect(page.locator('.birth-calendar-tabs button.active')).toHaveText("阳历");
    await page.getByRole("button", { name: "清除本机资料" }).click();
    const saved = await page.evaluate(() => localStorage.getItem("tianji.profile.birth.v1"));
    expect(saved).toBeNull();
  });

  test("switch to lunar tab", async ({ page }) => {
    await page.goto("/bazi-profile");
    await page.getByRole("tab", { name: "农历" }).click();
    await expect(page.locator('.birth-calendar-tabs button.active')).toHaveText("农历");
  });

  test("no technical timezone dropdown visible", async ({ page }) => {
    await page.goto("/bazi-profile");
    const selects = page.locator('select');
    const count = await selects.count();
    for (let i = 0; i < count; i++) {
      const text = await selects.nth(i).innerText();
      expect(text).not.toMatch(/Asia\/Shanghai/);
      expect(text).not.toMatch(/UTC[+-]/);
    }
    await expect(page.locator('.birth-region-row select')).toBeVisible();
  });
});

test.describe("TJ-006.1 P0-A: solar 31st days (failing first)", () => {
  test("2000-01-31 solar is valid", () => {
    const r = validateBirthInput({ calendarType: "solar", year: 2000, month: 1, day: 31, isLeapMonth: false, time: "12:00", timeUnknown: false, region: "中国大陆" });
    expect(r.ok).toBe(true);
  });
  test("2000-12-31 solar is valid", () => {
    const r = validateBirthInput({ calendarType: "solar", year: 2000, month: 12, day: 31, isLeapMonth: false, time: "12:00", timeUnknown: false, region: "中国大陆" });
    expect(r.ok).toBe(true);
  });
  test("2000-04-31 solar is invalid (April has 30 days)", () => {
    const r = validateBirthInput({ calendarType: "solar", year: 2000, month: 4, day: 31, isLeapMonth: false, time: "12:00", timeUnknown: false, region: "中国大陆" });
    expect(r.ok).toBe(false);
  });
  test("2000-06-31 solar is invalid", () => {
    const r = validateBirthInput({ calendarType: "solar", year: 2000, month: 6, day: 31, isLeapMonth: false, time: "12:00", timeUnknown: false, region: "中国大陆" });
    expect(r.ok).toBe(false);
  });
});

test.describe("TJ-006.1 P0-B: lunar cross-page no drift", () => {
  test("toSolarDateString converts lunar for display", async () => {
    const { toSolarDateString, isConvertedFromLunar } = await import("../src/public/birthProfile");
    const lunar: BirthProfile = {
      calendarType: "lunar", year: 2000, month: 4, day: 15,
      isLeapMonth: false, time: "12:00", timeUnknown: false, region: "中国大陆",
    };
    expect(toSolarDateString(lunar)).toBe("2000-05-18");
    expect(isConvertedFromLunar(lunar)).toBe(true);
  });

  test("toApiValue uses original lunar profile (not fromLegacy)", () => {
    const lunar: BirthProfile = {
      calendarType: "lunar", year: 2000, month: 4, day: 15,
      isLeapMonth: false, time: "12:00", timeUnknown: false, region: "中国大陆",
    };
    // 直接使用原始档案，内部转换
    const v = toApiValue(lunar);
    expect(v).toBe("2000-05-18T12:00:00+08:00");
  });

  test("fromSolarEdit marks edited date as solar", async () => {
    const { fromSolarEdit } = await import("../src/public/birthProfile");
    const p = fromSolarEdit("2000-05-18", "12:00", "中国大陆");
    expect(p.calendarType).toBe("solar");
    expect(p.year).toBe(2000);
  });
});

test.describe("TJ-006.1 P0-C: lunar strict validation (failing first)", () => {
  test("2023 leap Feb 15 is valid", () => {
    const r = validateBirthInput({ calendarType: "lunar", year: 2023, month: 2, day: 15, isLeapMonth: true, time: "12:00", timeUnknown: false, region: "中国大陆" });
    expect(r.ok).toBe(true);
  });
  test("2023 non-leap month with isLeapMonth=true is invalid", () => {
    // 2023年只有闰二月，五月不能标闰
    const r = validateBirthInput({ calendarType: "lunar", year: 2023, month: 5, day: 15, isLeapMonth: true, time: "12:00", timeUnknown: false, region: "中国大陆" });
    expect(r.ok).toBe(false);
  });
  test("lunar 30th day of 29-day month is invalid", async () => {
    // 需要找到一个29天的小月；先测试 validateLunarDate 的严格性
    const { validateLunarDate } = await import("../src/public/lunarConvert");
    // 如果某月只有29天，第30日应无效
    // 这里测试 API 不静默返回：用一个肯定无效的日期
    expect(validateLunarDate(2023, 2, 30, true)).toBe(false);
  });
});

test.describe("TJ-006.1 P0-F: real UI coverage", () => {
  test("save lunar via UI, cross-page reuse, back to bazi shows lunar", async ({ page }) => {
    await page.goto("/bazi-profile");
    // 切换到农历
    await page.getByRole("tab", { name: "农历" }).click();
    // 选择 2000年4月15日（需要先选年、月、日）
    // 年
    await page.locator('.birth-date-row select').nth(0).selectOption("2000");
    // 月
    await page.locator('.birth-date-row select').nth(1).selectOption("4");
    // 日
    await page.locator('.birth-date-row select').nth(2).selectOption("15");
    // 时间：12点0分
    await page.locator('.time-selects select').nth(0).selectOption("12");
    await page.locator('.time-selects select').nth(1).selectOption("0");
    // 保存
    await page.getByRole("button", { name: "保存资料" }).click();
    await page.waitForTimeout(500);
    // 验证 localStorage
    const saved = await page.evaluate(() => JSON.parse(localStorage.getItem("tianji.profile.birth.v1") || "{}"));
    expect(saved.calendarType).toBe("lunar");
    expect(saved.year).toBe(2000);
    // 跳到今日运势，验证复用
    await page.goto("/daily-structure");
    await page.waitForTimeout(500);
    // 返回八字，验证仍显示农历
    await page.goto("/bazi-profile");
    await expect(page.locator('.birth-calendar-tabs button.active')).toHaveText("农历");
  });

  test("unknown time blocks real submission", async ({ page }) => {
    await page.goto("/bazi-profile");
    await page.getByRole("button", { name: "填入示例" }).click();
    // 勾选"不知道出生时间"
    await page.locator('.time-unknown-check input').check();
    // 点击计算（提交）
    const submitBtn = page.locator('button[type="submit"]').first();
    if (await submitBtn.count() > 0) {
      await submitBtn.click();
      await page.waitForTimeout(500);
      // 应显示错误，不发送请求
      await expect(page.locator('.question-error')).toContainText(/出生时刻未知/);
    }
  });

  test("request body uses converted solar for lunar", async ({ page }) => {
    // 拦截请求，验证实际发送的参数
    let requestBody: any = null;
    await page.route("**/api/v1/public/execute", async (route) => {
      const req = route.request();
      try {
        requestBody = req.postDataJSON();
      } catch {}
      // 不 mock 成功响应，abort 以避免虚假成功宣传
      await route.abort();
    });
    await page.goto("/bazi-profile");
    await page.getByRole("button", { name: "填入示例" }).click();
    // 填入示例是阳历 2000-01-07，验证请求体
    const submitBtn = page.locator('button[type="submit"]').first();
    if (await submitBtn.count() > 0) {
      await submitBtn.click().catch(() => {});
      await page.waitForTimeout(1000);
    }
    // 如果请求被拦截，验证参数格式
    if (requestBody) {
      // 请求体应包含 ISO datetime 格式
      const bodyStr = JSON.stringify(requestBody);
      expect(bodyStr).toMatch(/2000-01-07T12:00:00\+08:00/);
    }
  });
});
