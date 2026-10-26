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

/** 农历某月天数；API 缺失或转换失败时抛出明确错误，不静默兜底 */
export function getLunarMonthDays(year: number, month: number, isLeap: boolean): number {
  const ly = LunarYear.fromYear(year);
  const months = ly.getMonths();
  for (const m of months) {
    const mMonth = Math.abs(m.getMonth());
    const mIsLeap = m.getMonth() < 0;
    if (mMonth === month && mIsLeap === isLeap) {
      const days = m.getDayCount();
      if (days !== 29 && days !== 30) {
        throw new Error(`历法库返回异常的月天数：${days}`);
      }
      return days;
    }
  }
  throw new Error(`未找到 ${year} 年${isLeap ? "闰" : ""}${month} 月`);
}

/** 农历 → 公历（含 roundtrip 校验） */
export function lunarToSolar(lunar: LunarDate): SolarDate {
  const m = lunar.isLeapMonth ? -lunar.month : lunar.month;
  const l = (Lunar as any).fromYmd(lunar.year, m, lunar.day);
  const solar = l.getSolar();
  const result = {
    year: solar.getYear(),
    month: solar.getMonth(),
    day: solar.getDay(),
  };
  // Roundtrip 校验：转回农历应一致
  const back = solarToLunar(result);
  if (back.year !== lunar.year || back.month !== lunar.month || back.day !== lunar.day ||
      back.isLeapMonth !== lunar.isLeapMonth) {
    throw new Error(`农历转换校验失败：${lunar.year}-${lunar.month}-${lunar.day} 转换后回检不一致`);
  }
  return result;
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

const LUNAR_MONTH_NAMES = [
  "正月", "二月", "三月", "四月", "五月", "六月",
  "七月", "八月", "九月", "十月", "冬月", "腊月",
];

/**
 * 有符号农历月份 → 展示文字。
 * 约定（与后端 lunar-python getMonth 一致，见 docs/phase2/API.md）：
 * 正数是本月，负数是闰月，如 -2 表示闰二月。展示层必须经此函数
 * 转换为「闰二月」等文字，不得直接显示负数或裸数字。
 * 非法输入（0、绝对值大于 12、非整数）直接抛错，不静默兜底。
 */
export function formatLunarMonth(signedMonth: number): string {
  if (
    !Number.isInteger(signedMonth) ||
    signedMonth === 0 ||
    Math.abs(signedMonth) > 12
  ) {
    throw new RangeError(`无效的农历月份：${signedMonth}`);
  }
  const name = LUNAR_MONTH_NAMES[Math.abs(signedMonth) - 1];
  return signedMonth < 0 ? `闰${name}` : name;
}

/** 校验农历日期有效性 */
export function validateLunarDate(year: number, month: number, day: number, isLeap: boolean): boolean {
  try {
    const leapMonth = getLeapMonth(year);
    if (isLeap && leapMonth !== month) return false;
    if (!isLeap && leapMonth === month) {
      // 该月有闰月，但用户未勾选闰月标记 — 这是有效的（普通月）
      // 不拒绝，继续校验
    }
    if (month < 1 || month > 12 || day < 1) return false;
    // 严格校验月大小：29天小月的第30日无效
    const monthDays = getLunarMonthDays(year, month, isLeap);
    if (day > monthDays) return false;
    // 尝试转换（含 roundtrip），失败则无效
    lunarToSolar({ year, month, day, isLeapMonth: isLeap });
    return true;
  } catch {
    return false;
  }
}
