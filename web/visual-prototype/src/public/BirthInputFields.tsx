import { useState } from "react";
import {
  TIMEZONE_OPTIONS,
  validateProfile,
  type BirthProfile,
} from "./birthProfile";

/**
 * TJ-006.1: 统一出生资料输入（日期/时刻/时区）。
 * - 中文错误提示，直接指出问题
 * - 时刻可选（未知不伪造）
 * - 时区显式选择
 */
export function BirthInputFields({
  initial,
  onChange,
}: {
  initial: BirthProfile;
  onChange: (profile: BirthProfile, valid: boolean, error: string) => void;
}) {
  const [date, setDate] = useState(initial.date);
  const [time, setTime] = useState(initial.time);
  const [timezone, setTimezone] = useState(
    initial.timezone || Intl.DateTimeFormat().resolvedOptions().timeZone || "Asia/Shanghai",
  );

  const update = (d: string, t: string, tz: string) => {
    setDate(d);
    setTime(t);
    setTimezone(tz);
    const profile: BirthProfile = { date: d, time: t, timezone: tz };
    const v = validateProfile(profile);
    onChange(profile, v.ok, v.ok ? "" : (v as { message: string }).message);
  };

  return (
    <div className="birth-input-grid">
      <label>
        <span>出生日期 <em className="required-mark">必填</em></span>
        <input
          type="date"
          value={date}
          min="1900-01-01"
          max="2099-12-31"
          onChange={(e) => update(e.target.value, time, timezone)}
          required
        />
      </label>
      <label>
        <span>出生时刻 <em className="optional-mark">选填（不知可不填）</em></span>
        <input
          type="time"
          value={time}
          onChange={(e) => update(date, e.target.value, timezone)}
        />
      </label>
      <label>
        <span>出生地时区</span>
        <select value={timezone} onChange={(e) => update(date, time, e.target.value)}>
          {TIMEZONE_OPTIONS.map((o) => (
            <option key={o.value} value={o.value}>
              {o.label}
            </option>
          ))}
        </select>
      </label>
    </div>
  );
}
