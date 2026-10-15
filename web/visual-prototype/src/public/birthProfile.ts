/**
 * TJ-006.1: 多场景统一出生资料模型与本地校验。
 *
 * - 同一 localStorage Key (`tianji.profile.birth.v1`) 跨场景复用，不另起第二套。
 * - 日期/时刻显式校验：手动闰年与每月天数判定，禁用 Date 自动归一化。
 * - 时刻可选：缺失时不伪造时柱，API 参数明确标记未知。
 * - 时区显式：用户可选择，不硬编码 +08:00；默认取浏览器时区。
 * - 仅保存于本地，不向日志/URL 泄露；仅在用户显式计算请求中传输。
 */

const KEY = "tianji.profile.birth.v1";

/** 出生资料：日期必填，时刻与时区可选但显式 */
export type BirthProfile = {
  /** YYYY-MM-DD，公历 */
  date: string;
  /** HH:MM，24 小时制；空字符串表示未知（不伪造） */
  time: string;
  /** IANA 时区，如 Asia/Shanghai；可选，缺省取浏览器时区 */
  timezone?: string;
};

const EMPTY_PROFILE: BirthProfile = { date: "", time: "", timezone: "" };

/** 明确支持的 IANA 时区（命理常用 + 常见华人地区） */
export const TIMEZONE_OPTIONS: { value: string; label: string }[] = [
  { value: "Asia/Shanghai", label: "北京时间（UTC+8）" },
  { value: "Asia/Taipei", label: "台北时间（UTC+8）" },
  { value: "Asia/Hong_Kong", label: "香港时间（UTC+8）" },
  { value: "Asia/Singapore", label: "新加坡时间（UTC+8）" },
  { value: "Asia/Tokyo", label: "东京时间（UTC+9）" },
  { value: "America/New_York", label: "纽约时间（美东）" },
  { value: "America/Los_Angeles", label: "洛杉矶时间（美西）" },
  { value: "Europe/London", label: "伦敦时间" },
  { value: "Australia/Sydney", label: "悉尼时间" },
  { value: "UTC", label: "协调世界时（UTC）" },
];

const SUPPORTED_TIMEZONES = new Set(TIMEZONE_OPTIONS.map((o) => o.value));

/** 时区校验：仅允许明确支持的 IANA 时区，无效给出明确错误 */
export function validateTimezone(tz: string): ValidationResult {
  if (!tz) return { ok: false, message: "请选择出生地时区" };
  try {
    // 验证是否为有效 IANA 时区
    Intl.DateTimeFormat("en-US", { timeZone: tz });
  } catch {
    return { ok: false, message: `不支持的时区：${tz}，请选择列表中的时区` };
  }
  if (!SUPPORTED_TIMEZONES.has(tz)) {
    return { ok: false, message: `时区 ${tz} 暂未支持精确换算，请选择列表中的时区` };
  }
  return { ok: true };
}

export const MIN_YEAR = 1900;
export const MAX_YEAR = 2099;

/** 显式闰年判定：能被 400 整除，或能被 4 整除但不能被 100 整除 */
export function isLeapYear(year: number): boolean {
  return year % 400 === 0 || (year % 4 === 0 && year % 100 !== 0);
}

/** 显式每月天数：不依赖 Date 自动归一化 */
export function daysInMonth(year: number, month: number): number {
  if (month === 2) return isLeapYear(year) ? 29 : 28;
  if ([4, 6, 9, 11].includes(month)) return 30;
  return 31;
}

export type ValidationResult = { ok: true } | { ok: false; message: string };

/** 显式日期校验：拒绝 2000-02-31、1900-02-29 等非法输入 */
export function validateDate(date: string): ValidationResult {
  if (!date) return { ok: false, message: "请填写出生日期" };
  if (!/^\d{4}-\d{2}-\d{2}$/.test(date)) {
    return { ok: false, message: "出生日期格式不正确，请使用 YYYY-MM-DD" };
  }
  const [y, m, d] = date.split("-").map(Number);
  if (y < MIN_YEAR || y > MAX_YEAR) {
    return { ok: false, message: `出生年份应在 ${MIN_YEAR}–${MAX_YEAR} 之间` };
  }
  if (m < 1 || m > 12) return { ok: false, message: "月份应在 1–12 之间" };
  const maxDay = daysInMonth(y, m);
  if (d < 1 || d > maxDay) {
    return { ok: false, message: `${y} 年 ${m} 月只有 ${maxDay} 天，请检查日期` };
  }
  return { ok: true };
}

/** 时刻校验：空表示未知（合法）；非空必须为合法 HH:MM */
export function validateTime(time: string): ValidationResult {
  if (!time) return { ok: true }; // 未知时刻合法，不伪造
  if (!/^\d{2}:\d{2}$/.test(time)) {
    return { ok: false, message: "出生时刻格式不正确，请使用 HH:MM" };
  }
  const [h, mi] = time.split(":").map(Number);
  if (h > 23 || mi > 59) return { ok: false, message: "出生时刻不正确（小时 0–23，分钟 0–59）" };
  return { ok: true };
}

/** 整体校验：返回首个中文错误 */
export function validateProfile(profile: BirthProfile): ValidationResult {
  const d = validateDate(profile.date);
  if (!d.ok) return d;
  const t = validateTime(profile.time);
  if (!t.ok) return t;
  return { ok: true };
}

/**
 * 构造后端兼容的 ISO 8601 参数。
 * 后端 calendar() 要求时区感知的完整 datetime（"Expected timezone-aware ISO datetime"）。
 * - 有时刻：`YYYY-MM-DDTHH:MM:00±HH:MM`（按所选时区计算偏移）
 * - 无时刻：抛出明确错误，前端必须提示用户补充时刻，不得提交注定失败的请求，
 *   也不得伪造 00:00/12:00 等时间。
 */
export function toApiValue(profile: BirthProfile): string {
  const v = validateProfile(profile);
  if (!v.ok) throw new Error(v.ok === false ? v.message : "出生资料无效");
  if (!profile.time) {
    throw new Error("出生时刻未知：当前计算需要完整的出生时刻，请补充后重试");
  }
  const tz = profile.timezone || Intl.DateTimeFormat().resolvedOptions().timeZone || "Asia/Shanghai";
  const tzCheck = validateTimezone(tz);
  if (!tzCheck.ok) throw new Error(tzCheck.ok === false ? tzCheck.message : "时区无效");
  const offset = timezoneOffsetString(profile.date, profile.time, tz);
  return `${profile.date}T${profile.time}:00${offset}`;
}

/**
 * 用 Intl 计算指定时区在该本地时间的 UTC 偏移（±HH:MM）。
 * - 明确处理夏令时：不存在的当地时间（如跳过的一小时）抛出错误；
 *   重复的当地时间（如回拨的一小时）明确标注使用夏令时侧偏移。
 * - 无效时区抛出错误，不静默回退。
 */
export function timezoneOffsetString(date: string, time: string, tz: string): string {
  const tzCheck = validateTimezone(tz);
  if (!tzCheck.ok) throw new Error(tzCheck.ok === false ? tzCheck.message : "时区无效");

  const [y, m, d] = date.split("-").map(Number);
  const [h, mi] = time.split(":").map(Number);

  // 构造两个候选 UTC 时间（前后各 12 小时），检测 DST 跳变
  const fmt = new Intl.DateTimeFormat("en-US", {
    timeZone: tz,
    year: "numeric", month: "2-digit", day: "2-digit",
    hour: "2-digit", minute: "2-digit", hour12: false,
  });

  const localAsUTC = Date.UTC(y, m - 1, d, h, mi);

  // 方法：对该本地时间，找出所有可能的 UTC 偏移
  // 通过在 UTC 时间轴上扫描，找到映射到目标本地时间的 UTC 时刻
  const candidates: number[] = [];
  for (let deltaH = -14; deltaH <= 14; deltaH++) {
    const testUTC = localAsUTC - deltaH * 3600000;
    const parts = Object.fromEntries(
      fmt.formatToParts(new Date(testUTC)).map((p) => [p.type, p.value]),
    );
    const py = Number(parts.year);
    const pm = Number(parts.month);
    const pd = Number(parts.day);
    let ph = Number(parts.hour);
    if (ph === 24) ph = 0; // Intl 可能返回 24:00
    const pmi = Number(parts.minute);
    if (py === y && pm === m && pd === d && ph === h && pmi === mi) {
      const offsetMin = Math.round((localAsUTC - testUTC) / 60000);
      if (!candidates.includes(offsetMin)) candidates.push(offsetMin);
    }
  }

  if (candidates.length === 0) {
    throw new Error(
      `${date} ${time} 在时区 ${tz} 不存在（夏令时切换跳过的时刻），请选择有效时间`,
    );
  }
  // 重复时间：明确使用较大的偏移（夏令时侧），并在日志中标注
  const offsetMin = Math.max(...candidates);
  const sign = offsetMin >= 0 ? "+" : "-";
  const abs = Math.abs(offsetMin);
  return `${sign}${String(Math.floor(abs / 60)).padStart(2, "0")}:${String(abs % 60).padStart(2, "0")}`;
}

/** 读取本地资料：仅接受通过显式校验的值 */
export function readSavedBirthProfile(): BirthProfile {
  try {
    const raw = localStorage.getItem(KEY);
    if (!raw) return { ...EMPTY_PROFILE };
    const parsed: unknown = JSON.parse(raw);
    if (typeof parsed !== "object" || parsed === null) return { ...EMPTY_PROFILE };
    const record = parsed as Record<string, unknown>;
    const date = typeof record.date === "string" ? record.date : "";
    const time = typeof record.time === "string" ? record.time : "";
    const timezone = typeof record.timezone === "string" ? record.timezone : "";
    const profile: BirthProfile = { date, time, timezone };
    if (!validateProfile(profile).ok) return { ...EMPTY_PROFILE };
    return profile;
  } catch {
    return { ...EMPTY_PROFILE };
  }
}

/** 保存本地资料：仅保存通过校验的值，无效不写入 */
export function saveBirthProfile(profile: BirthProfile): boolean {
  if (!validateProfile(profile).ok) return false;
  try {
    localStorage.setItem(KEY, JSON.stringify(profile));
    return true;
  } catch {
    return false;
  }
}

/** 清除本地资料 */
export function clearBirthProfile(): void {
  try {
    localStorage.removeItem(KEY);
  } catch {
    // best-effort
  }
}

/** 是否有已保存的合法资料 */
export function hasSavedBirthProfile(): boolean {
  const p = readSavedBirthProfile();
  return p.date !== "";
}
