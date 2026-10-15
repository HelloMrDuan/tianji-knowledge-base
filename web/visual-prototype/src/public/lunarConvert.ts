/**
 * TJ-006.1: 农历↔公历转换（基于 lunar-javascript）。
 * - 农历输入必须经此转换为公历后再提交后端
 * - 保留原始农历信息，不直接丢弃
 */
import { Lunar, LunarYear, Solar } from "lunar-javascript";

export type LunarDate = {
  year: number;
  month: number;
  day: number;
  isLeapMonth: boolean;
};

export type SolarDate = {
  year: number;
  month: number;
  day: number;
};

/** 获取某年闰月（0 表示无闰月） */
export function getLeapMonth(year: number): number {
  try {
    return LunarYear.fromYear(year).getLeapMonth();
  } catch {
    return 0;
  }
}

/** 农历某月天数 */
export function getLunarMonthDays(year: number, month: number, isLeap: boolean): number {
  try {
    // 通过构造该月初一再取月天数
    const lunar = (Lunar as any).fromYmd(year, isLeap ? -month : month, 1);
    // lunar-javascript 的 monthDays API
    if (typeof lunar.getMonthDays === "function") {
      return lunar.getMonthDays();
    }
    // 兜底：尝试 30 天
    return 30;
  } catch {
    return 30;
  }
}

/** 农历 → 公历 */
export function lunarToSolar(lunar: LunarDate): SolarDate {
  const m = lunar.isLeapMonth ? -lunar.month : lunar.month;
  const l = (Lunar as any).fromYmd(lunar.year, m, lunar.day);
  const solar = l.getSolar();
  return {
    year: solar.getYear(),
    month: solar.getMonth(),
    day: solar.getDay(),
  };
}

/** 公历 → 农历（用于显示对照） */
export function solarToLunar(solar: SolarDate): LunarDate & { leapMonth: number } {
  const s = Solar.fromYmd(solar.year, solar.month, solar.day);
  const l = s.getLunar();
  return {
    year: l.getYear(),
    month: Math.abs(l.getMonth()),
    day: l.getDay(),
    isLeapMonth: l.getMonth() < 0,
    leapMonth: 0,
  };
}

/** 校验农历日期有效性 */
export function validateLunarDate(year: number, month: number, day: number, isLeap: boolean): boolean {
  try {
    const leapMonth = getLeapMonth(year);
    if (isLeap && leapMonth !== month) return false;
    if (month < 1 || month > 12 || day < 1 || day > 30) return false;
    // 尝试转换，失败则无效
    lunarToSolar({ year, month, day, isLeapMonth: isLeap });
    return true;
  } catch {
    return false;
  }
}
