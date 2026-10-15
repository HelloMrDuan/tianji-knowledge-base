import {
  TIMEZONE_OPTIONS,
  validateProfile,
  type BirthProfile,
} from "./birthProfile";

/**
 * TJ-006.1 第二轮：受控组件。
 * - 通过 value/onChange 与父级统一状态，无内部 useState
 * - 示例填充、清除、恢复都以父级 profile 为准
 */
export function BirthInputFields({
  value,
  onChange,
}: {
  value: BirthProfile;
  onChange: (profile: BirthProfile) => void;
}) {
  const update = (patch: Partial<BirthProfile>) => {
    onChange({ ...value, ...patch });
  };

  const v = validateProfile(value);
  const errorMsg = v.ok ? "" : (v as { message: string }).message;

  return (
    <div>
      <div className="birth-input-grid">
        <label>
          <span>出生日期 <em className="required-mark">必填</em></span>
          <input
            type="date"
            value={value.date}
            min="1900-01-01"
            max="2099-12-31"
            onChange={(e) => update({ date: e.target.value })}
            required
          />
        </label>
        <label>
          <span>出生时刻 <em className="optional-mark">选填（不知可不填）</em></span>
          <input
            type="time"
            value={value.time}
            onChange={(e) => update({ time: e.target.value })}
          />
        </label>
        <label>
          <span>出生地时区 <em className="required-mark">必填</em></span>
          <select
            value={value.timezone || "Asia/Shanghai"}
            onChange={(e) => update({ timezone: e.target.value })}
          >
            {TIMEZONE_OPTIONS.map((o) => (
              <option key={o.value} value={o.value}>
                {o.label}
              </option>
            ))}
          </select>
        </label>
      </div>
      {errorMsg && (
        <p className="question-error" role="alert">
          {errorMsg}
        </p>
      )}
    </div>
  );
}
