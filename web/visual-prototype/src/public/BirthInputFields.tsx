import { useMemo } from "react";
import {
  REGION_OPTIONS,
  MIN_YEAR,
  MAX_YEAR,
  solarDaysInMonth,
  validateBirthInput,
  type BirthProfile,
  type CalendarType,
} from "./birthProfile";
import { getLeapMonth, getLunarMonthDays } from "./lunarConvert";

/**
 * TJ-006.1 第三轮：面向普通用户的出生资料输入。
 * - 阳历/农历切换；农历支持闰月
 * - 时间：几点几分 + "不知道"选项
 * - 地区选择（无技术时区）
 */
export function BirthInputFields({
  value,
  onChange,
}: {
  value: BirthProfile;
  onChange: (profile: BirthProfile) => void;
}) {
  const years = useMemo(() => {
    const arr: number[] = [];
    for (let y = MAX_YEAR; y >= MIN_YEAR; y--) arr.push(y);
    return arr;
  }, []);

  const leapMonth = useMemo(() => {
    if (value.calendarType !== "lunar" || !value.year) return 0;
    return getLeapMonth(value.year);
  }, [value.calendarType, value.year]);

  const maxDay = useMemo(() => {
    if (!value.year || !value.month) return 31;
    if (value.calendarType === "solar") {
      return solarDaysInMonth(value.year, value.month);
    }
    return getLunarMonthDays(value.year, value.month, value.isLeapMonth);
  }, [value.calendarType, value.year, value.month, value.isLeapMonth]);

  const days = useMemo(() => {
    const arr: number[] = [];
    for (let d = 1; d <= maxDay; d++) arr.push(d);
    return arr;
  }, [maxDay]);

  const update = (patch: Partial<BirthProfile>) => {
    onChange({ ...value, ...patch });
  };

  const setCalendarType = (t: CalendarType) => {
    // 切换历法时重置日期，避免混淆
    update({ calendarType: t, year: 0, month: 0, day: 0, isLeapMonth: false });
  };

  const v = validateBirthInput(value);
  const errorMsg = v.ok ? "" : (v as { message: string }).message;

  const hours = Array.from({ length: 24 }, (_, i) => i);
  const minutes = Array.from({ length: 60 }, (_, i) => i);
  const [curH, curM] = value.time ? value.time.split(":").map(Number) : [12, 0];

  return (
    <div className="birth-input-user">
      {/* 历法选择 */}
      <div className="birth-calendar-tabs" role="tablist" aria-label="历法选择">
        <button
          type="button"
          role="tab"
          aria-selected={value.calendarType === "solar"}
          className={value.calendarType === "solar" ? "active" : ""}
          onClick={() => setCalendarType("solar")}
        >
          阳历
        </button>
        <button
          type="button"
          role="tab"
          aria-selected={value.calendarType === "lunar"}
          className={value.calendarType === "lunar" ? "active" : ""}
          onClick={() => setCalendarType("lunar")}
        >
          农历
        </button>
      </div>

      {/* 日期选择 */}
      <div className="birth-date-row">
        <label>
          <span>年</span>
          <select
            value={value.year || ""}
            onChange={(e) => update({ year: Number(e.target.value) || 0 })}
          >
            <option value="">请选择</option>
            {years.map((y) => (
              <option key={y} value={y}>{y} 年</option>
            ))}
          </select>
        </label>
        <label>
          <span>月</span>
          <select
            value={value.month || ""}
            onChange={(e) => update({ month: Number(e.target.value) || 0, day: 0, isLeapMonth: false })}
          >
            <option value="">请选择</option>
            {Array.from({ length: 12 }, (_, i) => i + 1).map((m) => (
              <option key={m} value={m}>{m} 月</option>
            ))}
          </select>
        </label>
        {value.calendarType === "lunar" && leapMonth > 0 && (
          <label className="leap-month-check">
            <input
              type="checkbox"
              checked={value.isLeapMonth}
              onChange={(e) => update({ isLeapMonth: e.target.checked, day: 0 })}
            />
            <span>闰{leapMonth}月</span>
          </label>
        )}
        <label>
          <span>日</span>
          <select
            value={value.day || ""}
            onChange={(e) => update({ day: Number(e.target.value) || 0 })}
          >
            <option value="">请选择</option>
            {days.map((d) => (
              <option key={d} value={d}>{d} 日</option>
            ))}
          </select>
        </label>
      </div>

      {/* 时间选择 */}
      <div className="birth-time-row">
        <label className="time-unknown-check">
          <input
            type="checkbox"
            checked={value.timeUnknown}
            onChange={(e) => update({ timeUnknown: e.target.checked, time: "" })}
          />
          <span>不知道出生时间</span>
        </label>
        {!value.timeUnknown && (
          <div className="time-selects">
            <label>
              <span>时</span>
              <select
                value={curH}
                onChange={(e) => {
                  const h = Number(e.target.value);
                  update({ time: `${String(h).padStart(2, "0")}:${String(curM).padStart(2, "0")}` });
                }}
              >
                {hours.map((h) => (
                  <option key={h} value={h}>{h} 点</option>
                ))}
              </select>
            </label>
            <label>
              <span>分</span>
              <select
                value={curM}
                onChange={(e) => {
                  const mi = Number(e.target.value);
                  update({ time: `${String(curH).padStart(2, "0")}:${String(mi).padStart(2, "0")}` });
                }}
              >
                {minutes.map((mi) => (
                  <option key={mi} value={mi}>{mi} 分</option>
                ))}
              </select>
            </label>
          </div>
        )}
      </div>
      {value.timeUnknown && (
        <p className="birth-note">
          暂不知晓时刻时可先保存资料；当前排盘需要完整时刻，提交计算时请补充。
        </p>
      )}

      {/* 地区选择 */}
      <div className="birth-region-row">
        <label>
          <span>出生地区</span>
          <select
            value={value.region}
            onChange={(e) => update({ region: e.target.value })}
          >
            {REGION_OPTIONS.map((o) => (
              <option key={o.value} value={o.value}>{o.label}</option>
            ))}
          </select>
        </label>
      </div>

      {errorMsg && (
        <p className="question-error" role="alert">{errorMsg}</p>
      )}
    </div>
  );
}
