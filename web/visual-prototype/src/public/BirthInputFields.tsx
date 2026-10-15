import { useEffect, useMemo, useState } from "react";
import {
  REGION_OPTIONS,
  MIN_YEAR,
  MAX_YEAR,
  solarDaysInMonth,
  validateBirthInput,
  confirmRegion,
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
  // P0-1: 显式待选状态；从 value.time 初始化，外部变化时同步
  const [pendingH, setPendingH] = useState<number>(() =>
    value.time ? Number(value.time.split(":")[0]) : -1
  );
  const [pendingM, setPendingM] = useState<number>(() =>
    value.time ? Number(value.time.split(":")[1]) : -1
  );
  // 外部 value.time 变化时同步 pending（示例/清除/恢复）
  useEffect(() => {
    if (value.time) {
      const [h, m] = value.time.split(":").map(Number);
      setPendingH(h);
      setPendingM(m);
    } else if (!value.timeUnknown) {
      // 非"不知道"且 time 为空：重置为待选（但保留用户已选的一侧）
      // 注意：不强制重置，允许用户继续选另一侧
    }
  }, [value.time]);
  // 清除时重置
  useEffect(() => {
    if (!value.time && !value.timeUnknown && pendingH >= 0 && pendingM >= 0) {
      // 如果外部清空了但 pending 还有值，说明是清除操作，重置
      // 通过检查 value.year 是否为 0 来判断是否为清除
      if (value.year === 0) {
        setPendingH(-1);
        setPendingM(-1);
      }
    }
  }, [value.year]);

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
        {value.calendarType === "lunar" && leapMonth > 0 && value.month === leapMonth && (
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
            onChange={(e) => {
              const unknown = e.target.checked;
              if (unknown) {
                setPendingH(-1);
                setPendingM(-1);
              }
              update({ timeUnknown: unknown, time: "" });
            }}
          />
          <span>不知道出生时间</span>
        </label>
        {!value.timeUnknown && (
          <div className="time-selects">
            <label>
              <span>时</span>
              <select
                value={pendingH}
                onChange={(e) => {
                  const h = Number(e.target.value);
                  setPendingH(h);
                  // P0-1: 两侧都选齐才通知父级
                  if (h >= 0 && pendingM >= 0) {
                    update({ time: `${String(h).padStart(2, "0")}:${String(pendingM).padStart(2, "0")}` });
                  } else if (h < 0) {
                    update({ time: "" });
                  }
                }}
              >
                <option value={-1}>请选择</option>
                {hours.map((h) => (
                  <option key={h} value={h}>{h} 点</option>
                ))}
              </select>
            </label>
            <label>
              <span>分</span>
              <select
                value={pendingM}
                onChange={(e) => {
                  const mi = Number(e.target.value);
                  setPendingM(mi);
                  if (mi >= 0 && pendingH >= 0) {
                    update({ time: `${String(pendingH).padStart(2, "0")}:${String(mi).padStart(2, "0")}` });
                  } else if (mi < 0) {
                    update({ time: "" });
                  }
                }}
              >
                <option value={-1}>请选择</option>
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
          已选择“不知道出生时间”。可点击“保存资料”在本地保留；提交排盘计算时仍需补充具体时刻。
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
        {value._regionNeedsConfirm && (
          <div className="region-confirm-box">
            <p className="birth-note" role="alert">
              您的旧资料缺少出生地区信息，请确认后才能计算。
            </p>
            <button
              type="button"
              className="sample-fill"
              onClick={() => onChange(confirmRegion(value, value.region))}
            >
              确认出生地区：{value.region}
            </button>
          </div>
        )}
      </div>

      {errorMsg && (
        <p className="question-error" role="alert">{errorMsg}</p>
      )}
    </div>
  );
}
