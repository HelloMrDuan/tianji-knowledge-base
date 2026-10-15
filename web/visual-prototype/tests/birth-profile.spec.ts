import { expect, test } from "@playwright/test";
import {
  validateBirthInput,
  toApiValue,
  fromLegacy,
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
