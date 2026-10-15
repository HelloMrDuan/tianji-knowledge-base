/**
 * TJ-006.1 第三轮：面向普通用户的出生资料模型。
 *
 * - 历法：阳历/农历二选一；农历支持闰月
 * - 时间：几点几分，或明确"不知道"
 * - 地区：出生地区选择（中国大陆默认），系统内部处理时区
 * - 原始输入与转换参数分层存储，避免重复转换漂移
 */

import { lunarToSolar, validateLunarDate } from "./lunarConvert";

const KEY = "tianji.profile.birth.v1";

export type CalendarType = "solar" | "lunar";

/** 用户原始输入（按用户认知） */
export type BirthInput = {
  calendarType: CalendarType;
  year: number;
  month: number;
  day: number;
  /** 农历闰月标记；阳历时忽略 */
  isLeapMonth: boolean;
  /** HH:MM；空表示未知 */
  time: string;
  /** 明确"不知道出生时间" */
  timeUnknown: boolean;
  /** 出生地区，如 "中国大陆" */
  region: string;
  /** 内部标记：旧资料时区未知，需用户确认地区 */
  _regionNeedsConfirm?: boolean;
};

/** 完整资料（含原始输入） */
export type BirthProfile = BirthInput;

const EMPTY_PROFILE: BirthProfile = {
  calendarType: "solar",
  year: 0,
  month: 0,
  day: 0,
  isLeapMonth: false,
  time: "",
  timeUnknown: false,
  region: "中国大陆",
};

/** 出生地区选项（用户认知） */
export const REGION_OPTIONS: { value: string; label: string }[] = [
  { value: "中国大陆", label: "中国大陆" },
  { value: "香港", label: "香港" },
  { value: "台湾", label: "台湾" },
  { value: "澳门", label: "澳门" },
  { value: "新加坡", label: "新加坡" },
  { value: "马来西亚", label: "马来西亚" },
  { value: "美国", label: "美国" },
  { value: "加拿大", label: "加拿大" },
  { value: "英国", label: "英国" },
  { value: "澳大利亚", label: "澳大利亚" },
  { value: "日本", label: "日本" },
  { value: "其他", label: "其他国家/地区" },
];

/** 地区 → IANA 时区（内部映射，不暴露给用户） */
const REGION_TIMEZONE: Record<string, string> = {
  "中国大陆": "Asia/Shanghai",
  "香港": "Asia/Hong_Kong",
  "台湾": "Asia/Taipei",
  "澳门": "Asia/Macau",
  "新加坡": "Asia/Singapore",
  "马来西亚": "Asia/Kuala_Lumpur",
  "日本": "Asia/Tokyo",
  "英国": "Europe/London",
  // 多时区国家暂不支持精确排盘，需用户选择州/省/城市（后续任务）
  // 不静默指定错误地点
  "美国": "",
  "加拿大": "",
  "澳大利亚": "",
  "其他": "",
};

export function regionToTimezone(region: string): string {
  return REGION_TIMEZONE[region] || "";
}

export const MIN_YEAR = 1949;
export const MAX_YEAR = 2099;

/** 阳历闰年 */
export function isLeapYear(year: number): boolean {
  return year % 400 === 0 || (year % 4 === 0 && year % 100 !== 0);
}

/** 阳历每月天数 */
export function solarDaysInMonth(year: number, month: number): number {
  if (month === 2) return isLeapYear(year) ? 29 : 28;
  if ([4, 6, 9, 11].includes(month)) return 30;
  return 31;
}

/** 农历每月天数（需 lunar-javascript；此处为接口，实际调用在 lunarConvert.ts） */
export function lunarDaysInMonth(year: number, month: number, isLeap: boolean): number {
  // 由 lunar-javascript 提供；占位，实际在组件中动态计算
  return 30;
}

export type ValidationResult = { ok: true } | { ok: false; message: string };

/** 日期校验（含农历闰月） */
export function validateBirthInput(input: BirthInput): ValidationResult {
  const { calendarType, year, month, day, isLeapMonth, time, timeUnknown, region } = input;

  if (!year || year < MIN_YEAR || year > MAX_YEAR) {
    return { ok: false, message: `请选择 ${MIN_YEAR}–${MAX_YEAR} 年间的出生年份` };
  }
  if (!month || month < 1 || month > 12) {
    return { ok: false, message: "请选择出生月份（1–12月）" };
  }
  // 日期有效性由调用方按历法校验（阳历用 solarDaysInMonth，农历用 lunar-javascript）
  if (!day || day < 1) {
    return { ok: false, message: "请选择有效的出生日期" };
  }
  if (calendarType === "solar") {
    if (day > 31) {
      return { ok: false, message: "请选择有效的出生日期" };
    }
    const maxDay = solarDaysInMonth(year, month);
    if (day > maxDay) {
      return { ok: false, message: `${year} 年 ${month} 月只有 ${maxDay} 天，请检查日期` };
    }
  } else {
    // 农历：由真实历法库校验月大小和闰月
    if (!validateLunarDate(year, month, day, isLeapMonth)) {
      return { ok: false, message: `农历 ${year} 年${isLeapMonth ? "闰" : ""}${month} 月没有 ${day} 日，请检查日期` };
    }
  }
  // 农历日期范围由 lunar-javascript 校验（含闰月）
  if (!timeUnknown && time) {
    if (!/^\d{2}:\d{2}$/.test(time)) {
      return { ok: false, message: "时间格式不正确" };
    }
    const [h, mi] = time.split(":").map(Number);
    if (h > 23 || mi > 59) return { ok: false, message: "时间不正确（0–23点，0–59分）" };
  }
  if (!region) {
    return { ok: false, message: "请选择出生地区" };
  }
  // P0-4: 旧资料时区未知，需用户确认后才能计算
  if ((input as BirthInput)._regionNeedsConfirm) {
    return { ok: false, message: "请先在八字命理页面确认出生地区，然后再进行测算" };
  }
  if (region === "其他") {
    return { ok: false, message: "暂不支持该地区的精确时间换算，请选择列表中的地区" };
  }
  const tz = regionToTimezone(region);
  if (!tz) {
    if (["美国", "加拿大", "澳大利亚"].includes(region)) {
      return { ok: false, message: `${region}横跨多个时区，暂不支持精确排盘，请选择其他地区或等待后续支持` };
    }
    return { ok: false, message: "该地区时区暂未支持，请选择其他地区" };
  }
  return { ok: true };
}

/** 读取本地资料 */
export function readSavedBirthProfile(): BirthProfile {
  try {
    const raw = localStorage.getItem(KEY);
    if (!raw) return { ...EMPTY_PROFILE };
    const parsed = JSON.parse(raw) as Partial<BirthProfile>;
    // 兼容旧格式 {date, time, timezone}
    if (typeof (parsed as any).date === "string" && !(parsed as any).calendarType) {
      const [y, m, d] = ((parsed as any).date as string).split("-").map(Number);
      const oldTz = (parsed as any).timezone as string;
      // IANA -> 地区的反向映射
      const tzToRegion: Record<string, string> = {
        "Asia/Shanghai": "中国大陆",
        "Asia/Taipei": "台湾",
        "Asia/Hong_Kong": "香港",
        "Asia/Macau": "澳门",
        "Asia/Singapore": "新加坡",
        "Asia/Kuala_Lumpur": "马来西亚",
        "Asia/Tokyo": "日本",
        "Europe/London": "英国",
        "UTC": "其他",
      };
      const region = (oldTz && tzToRegion[oldTz]) || "中国大陆";
      const needsConfirm = !oldTz || !tzToRegion[oldTz];
      return {
        calendarType: "solar",
        year: y || 0,
        month: m || 0,
        day: d || 0,
        isLeapMonth: false,
        time: (parsed as any).time || "",
        timeUnknown: !(parsed as any).time,
        region,
        // 标记需要用户确认地区（如果原时区未知）
        ...(needsConfirm ? { _regionNeedsConfirm: true } : {}),
      } as BirthProfile;
    }
    const profile: BirthProfile = {
      calendarType: parsed.calendarType === "lunar" ? "lunar" : "solar",
      year: Number(parsed.year) || 0,
      month: Number(parsed.month) || 0,
      day: Number(parsed.day) || 0,
      isLeapMonth: Boolean(parsed.isLeapMonth),
      time: typeof parsed.time === "string" ? parsed.time : "",
      timeUnknown: Boolean(parsed.timeUnknown),
      region: typeof parsed.region === "string" ? parsed.region : "中国大陆",
    };
    if (!validateBirthInput(profile).ok) return { ...EMPTY_PROFILE };
    return profile;
  } catch {
    return { ...EMPTY_PROFILE };
  }
}

/** 保存本地资料 */
export function saveBirthProfile(profile: BirthProfile): boolean {
  if (!validateBirthInput(profile).ok) return false;
  try {
    localStorage.setItem(KEY, JSON.stringify(profile));
    return true;
  } catch {
    return false;
  }
}

export function clearBirthProfile(): void {
  try {
    localStorage.removeItem(KEY);
  } catch {
    // best-effort
  }
}

export function hasSavedBirthProfile(): boolean {
  const p = readSavedBirthProfile();
  return p.year > 0;
}

// 兼容旧 API（逐步迁移）
export type { BirthProfile as BirthProfileLegacy };
export const TIMEZONE_OPTIONS = REGION_OPTIONS;

/**
 * 构造后端兼容的 ISO 8601 参数。
 * - 农历先转换为公历，再构造参数
 * - 地区映射为内部时区
 * - 未知时刻：抛出明确错误
 */
export function toApiValue(profile: BirthProfile): string {
  const v = validateBirthInput(profile);
  if (!v.ok) throw new Error((v as { message: string }).message);
  if (profile.timeUnknown || !profile.time) {
    throw new Error("出生时刻未知：当前排盘需要完整的出生时刻，请补充后重试");
  }

  let solarYear = profile.year;
  let solarMonth = profile.month;
  let solarDay = profile.day;
  if (profile.calendarType === "lunar") {
    const solar = lunarToSolar({
      year: profile.year,
      month: profile.month,
      day: profile.day,
      isLeapMonth: profile.isLeapMonth,
    });
    solarYear = solar.year;
    solarMonth = solar.month;
    solarDay = solar.day;
  }

  const tz = regionToTimezone(profile.region);
  if (!tz) {
    throw new Error(`地区 ${profile.region} 的时区暂未支持，请选择其他地区`);
  }

  const dateStr = `${solarYear}-${String(solarMonth).padStart(2, "0")}-${String(solarDay).padStart(2, "0")}`;
  const offset = timezoneOffsetString(dateStr, profile.time, tz);
  return `${dateStr}T${profile.time}:00${offset}`;
}

function timezoneOffsetString(date: string, time: string, tz: string): string {
  const [y, m, d] = date.split("-").map(Number);
  const [h, mi] = time.split(":").map(Number);

  // P0-3: 历史时区精度限制
  // 1949 年前中国及 1970 年前多地的时区偏移含分钟/秒级历史调整，
  // 前端 Intl 扫描无法可靠映射。明确拒绝，不返回错误瞬时。
  if (y < 1949) {
    throw new Error(`暂不支持 ${y} 年的历史时间精确换算（时区历史精度无法保证），请选择 1949 年后的日期`);
  }

  const fmt = new Intl.DateTimeFormat("en-US", {
    timeZone: tz,
    year: "numeric", month: "2-digit", day: "2-digit",
    hour: "2-digit", minute: "2-digit", hour12: false,
  });
  const localAsUTC = Date.UTC(y, m - 1, d, h, mi);
  const candidates: number[] = [];
  // P0-4: 支持半小时偏移（如新加坡 1985 年前的 +07:30）
  // 以 30 分钟步长扫描，覆盖整小时和半小时时区
  for (let deltaMin = -14 * 60; deltaMin <= 14 * 60; deltaMin += 30) {
    const testUTC = localAsUTC - deltaMin * 60000;
    const parts = Object.fromEntries(
      fmt.formatToParts(new Date(testUTC)).map((p) => [p.type, p.value]),
    );
    let ph = Number(parts.hour);
    if (ph === 24) ph = 0;
    if (
      Number(parts.year) === y && Number(parts.month) === m && Number(parts.day) === d &&
      ph === h && Number(parts.minute) === mi
    ) {
      const offsetMin = Math.round((localAsUTC - testUTC) / 60000);
      if (!candidates.includes(offsetMin)) candidates.push(offsetMin);
    }
  }
  if (candidates.length === 0) {
    throw new Error("该时间在所选地区不存在（夏令时切换），请选择有效时间");
  }
  if (candidates.length > 1) {
    // DST 重复时间：明确拒绝，不自动选择
    throw new Error("该时间在所选地区存在歧义（夏令时重复），请选择其他时间");
  }
  const offsetMin = candidates[0];
  const sign = offsetMin >= 0 ? "+" : "-";
  const abs = Math.abs(offsetMin);
  return `${sign}${String(Math.floor(abs / 60)).padStart(2, "0")}:${String(abs % 60).padStart(2, "0")}`;
}

/**
 * 兼容旧调用：将 {date: "YYYY-MM-DD", time: "HH:MM", timezone} 转为新模型。
 * 旧资料默认按阳历、中国大陆处理。
 */
export function fromLegacy(date: string, time: string, timezone?: string): BirthProfile {
  const [y, m, d] = date.split("-").map(Number);
  // timezone -> region 的反向映射（完整）
  const tzToRegion: Record<string, string> = {
    "Asia/Shanghai": "中国大陆",
    "Asia/Taipei": "台湾",
    "Asia/Hong_Kong": "香港",
    "Asia/Macau": "澳门",
    "Asia/Singapore": "新加坡",
    "Asia/Kuala_Lumpur": "马来西亚",
    "Asia/Tokyo": "日本",
    "Europe/London": "英国",
    "UTC": "其他",
  };
  return {
    calendarType: "solar",
    year: y || 0,
    month: m || 0,
    day: d || 0,
    isLeapMonth: false,
    time: time || "",
    timeUnknown: !time,
    region: (timezone && tzToRegion[timezone]) || "中国大陆",
  };
}

/**
 * P0-B 统一适配器：从 BirthProfile 导出用于显示的公历日期字符串。
 * - 阳历：直接返回 YYYY-MM-DD
 * - 农历：返回转换后的公历 YYYY-MM-DD（调用方应提示"当前显示的是换算后公历"）
 */
export function toSolarDateString(profile: BirthProfile): string {
  if (profile.calendarType === "solar") {
    if (!profile.year) return "";
    return `${profile.year}-${String(profile.month).padStart(2, "0")}-${String(profile.day).padStart(2, "0")}`;
  }
  // 农历 → 公历
  if (!profile.year) return "";
  const solar = lunarToSolar({
    year: profile.year,
    month: profile.month,
    day: profile.day,
    isLeapMonth: profile.isLeapMonth,
  });
  return `${solar.year}-${String(solar.month).padStart(2, "0")}-${String(solar.day).padStart(2, "0")}`;
}

/** 是否由农历转换而来（用于显示提示） */
export function isConvertedFromLunar(profile: BirthProfile): boolean {
  return profile.calendarType === "lunar" && profile.year > 0;
}

/**
 * 用户在旧表单（公历 date input）中编辑后的资料。
 * 明确标记为阳历，因为用户编辑的是显示的公历日期。
 */
export function fromSolarEdit(dateStr: string, time: string, region: string, source?: BirthProfile): BirthProfile {
  const [y, m, d] = dateStr.split("-").map(Number);
  return {
    calendarType: "solar",
    year: y || 0,
    month: m || 0,
    day: d || 0,
    isLeapMonth: false,
    time: time || "",
    timeUnknown: !time,
    region: region || "中国大陆",
    // P0: 保留待确认标记，防止绕过地区确认
    ...(source?._regionNeedsConfirm ? { _regionNeedsConfirm: true } : {}),
  };
}

/**
 * P0-2: 仅更新时刻，保留历法/日期/地区不变。
 * 用于用户只修改出生时刻的场景。
 */
export function withUpdatedTime(profile: BirthProfile, newTime: string): BirthProfile {
  return {
    ...profile,
    time: newTime,
    timeUnknown: !newTime,
  };
}

/**
 * P0-4: 用户确认出生地区后，清除待确认标记。
 */
export function confirmRegion(profile: BirthProfile, region: string): BirthProfile {
  const { _regionNeedsConfirm, ...rest } = profile;
  return { ...rest, region };
}

/**
 * TJ-006.3: 跨标签页同步。当其他标签页清除出生资料时，当前页应感知。
 * 返回取消监听的函数。回调在资料被清除时触发。
 */
export function onBirthProfileCleared(callback: () => void): () => void {
  const handler = (event: StorageEvent) => {
    if (event.key === KEY && event.newValue === null) {
      callback();
    }
  };
  window.addEventListener("storage", handler);
  return () => window.removeEventListener("storage", handler);
}
