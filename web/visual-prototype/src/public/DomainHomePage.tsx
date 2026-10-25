import { useState } from "react";
import type { CSSProperties, FormEvent } from "react";
import { Icon } from "../shared/Icon";
import { Link } from "../shared/router";
import {
  domainPages,
  YIJING_HEXAGRAM_BITS,
  YIJING_LINE_TO_CHANGING,
} from "./domainPages";
import type { DomainPage, FieldSpec } from "./domainPages";
import {
  ApiError,
  executeFengshui,
  executeLiuren,
  executeQimen,
  executeYijing,
  executeZiwei,
} from "./api";
import type { ExecuteResponse } from "./api";
import "./domain-home.css";

const lineLabels = ["初爻", "二爻", "三爻", "四爻", "五爻", "上爻"];
const lineNames: Record<string, string> = {
  "6": "老阴 · 动",
  "7": "少阳 · 静",
  "8": "少阴 · 静",
  "9": "老阳 · 动",
};
function initialValues(page: DomainPage) {
  return Object.fromEntries(
    page.fields.map((field) => [
      field.id,
      field.fixedValue || field.options?.[0] || "",
    ]),
  );
}
export function Diagram({ page }: { page: DomainPage }) {
  if (page.id === "bazi")
    return (
      <div className="pillar-illustration" aria-hidden="true">
        {["年", "月", "日", "时"].map((label) => (
          <div key={label}>
            <span>{label}柱</span>
            <i>天干</i>
            <b>地支</b>
          </div>
        ))}
        <small>示意文字 · 非命盘</small>
      </div>
    );
  if (page.id === "qimen")
    return (
      <div className="palace-illustration" aria-hidden="true">
        {[
          "巽 · 四",
          "离 · 九",
          "坤 · 二",
          "震 · 三",
          "中 · 五",
          "兑 · 七",
          "艮 · 八",
          "坎 · 一",
          "乾 · 六",
        ].map((name) => (
          <span key={name}>{name}</span>
        ))}
      </div>
    );
  if (page.id === "ziwei")
    return (
      <div className="star-illustration" aria-hidden="true">
        {[
          "命宫",
          "兄弟",
          "夫妻",
          "子女",
          "财帛",
          "疾厄",
          "迁移",
          "交友",
          "官禄",
          "田宅",
          "福德",
          "父母",
        ].map((name, i) => (
          <span key={name} style={{ "--star-index": i } as CSSProperties}>
            {name}
          </span>
        ))}
        <div>
          星垣<i>十二宫</i>
        </div>
      </div>
    );
  if (page.id === "liuren")
    return (
      <div className="lesson-illustration" aria-hidden="true">
        <div>
          {["一课", "二课", "三课", "四课"].map((name) => (
            <span key={name}>{name}</span>
          ))}
        </div>
        <i>↓</i>
        <div>
          {["初传", "中传", "末传"].map((name) => (
            <span key={name}>{name}</span>
          ))}
        </div>
      </div>
    );
  if (page.id === "fengshui")
    return (
      <div className="compass-illustration" aria-hidden="true">
        <div className="compass-ring">
          <span>北 · 0°</span>
          <span>东 · 90°</span>
          <span>南 · 180°</span>
          <span>西 · 270°</span>
          <i />
        </div>
      </div>
    );
  if (page.id === "yijing")
    return (
      <div className="trigram-illustration" aria-hidden="true">
        <div>
          {["☰", "☱", "☲", "☳", "☴", "☵", "☶", "☷"].map((glyph) => (
            <span key={glyph}>{glyph}</span>
          ))}
        </div>
        <i>三爻为卦 · 两卦成六爻</i>
      </div>
    );
  return (
    <div className="line-illustration" aria-hidden="true">
      {[true, true, false, true, false, true].map((yang, index) => (
        <div key={index}>
          <small>{lineLabels[5 - index]}</small>
          <span className={yang ? "solid" : "broken"}>
            <i />
            <i />
          </span>
        </div>
      ))}
    </div>
  );
}
function Field({
  field,
  value,
  onChange,
}: {
  field: FieldSpec;
  value: string;
  onChange: (value: string) => void;
}) {
  const id = "field-" + field.id;
  const hintId = id + "-hint";
  return (
    <div
      className={
        "entry-field " + (field.kind === "textarea" ? "field-full" : "")
      }
    >
      <label htmlFor={id}>
        {field.label}
        {field.required && <span aria-hidden="true"> *</span>}
      </label>
      {field.kind === "select" ? (
        <select
          id={id}
          value={value}
          onChange={(e) => onChange(e.target.value)}
          aria-describedby={field.hint ? hintId : undefined}
        >
          {field.options?.map((option) => (
            <option key={option}>{option}</option>
          ))}
        </select>
      ) : field.kind === "textarea" ? (
        <textarea
          id={id}
          value={value}
          onChange={(e) => onChange(e.target.value)}
          placeholder={field.placeholder}
          rows={3}
          aria-describedby={field.hint ? hintId : undefined}
        />
      ) : (
        <input
          id={id}
          type={field.kind || "text"}
          value={field.fixedValue || value}
          readOnly={Boolean(field.fixedValue)}
          onChange={(e) => onChange(e.target.value)}
          placeholder={field.placeholder}
          required={field.required}
          min={field.min}
          max={field.max}
          step={field.step}
          aria-describedby={field.hint ? hintId : undefined}
        />
      )}
      {field.hint && <small id={hintId}>{field.hint}</small>}
    </div>
  );
}
export function hexText(hex: Record<string, unknown> | undefined): string {
  if (!hex || typeof hex.name !== "string") return "—";
  return `${hex.name} · 第${hex.number}卦 · 下卦${hex.lower} / 上卦${hex.upper}`;
}
export function lessonText(lesson: Record<string, unknown> | undefined): string {
  if (!lesson) return "—";
  return `${lesson.upper} / ${lesson.lower}`;
}
export function DomainHomePage({ page }: { page: DomainPage }) {
  const [values, setValues] = useState(() => initialValues(page));
  const [lines, setLines] = useState(["", "", "", "", "", ""]);
  const [summary, setSummary] = useState<[string, string][] | null>(null);
  const [result, setResult] = useState<ExecuteResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [linesOpen, setLinesOpen] = useState(false);
  const connected =
    page.id === "yijing" ||
    page.id === "liuren" ||
    page.id === "ziwei" ||
    page.id === "qimen" ||
    page.id === "fengshui";
  function update(id: string, value: string) {
    setValues((prev) => ({ ...prev, [id]: value }));
    setSummary(null);
    setResult(null);
    setError("");
  }
  async function submit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    if (page.id === "liuyao" && lines.some((value) => !value)) {
      setError("请录入初爻到上爻的全部六个爻值。");
      setLinesOpen(true);
      return;
    }
    if (!connected) {
      const entries: [string, string][] = page.fields
        .filter((field) => field.id !== "leapMonth" || values.calendar === "农历")
        .filter((field) => field.fixedValue || values[field.id])
        .map((field) => [field.label, field.fixedValue || values[field.id]]);
      if (page.id === "liuyao")
        entries.push(["爻值（初爻 → 上爻）", lines.join(" · ")]);
      setSummary(entries);
      setError("");
      return;
    }
    // B012: 周易 / 六壬提交即真实后端计算。B014: 紫微 / 奇门 / 风水
    // 同样接通。校验失败不发请求；计算失败只显示错误，绝不展示旧结果
    // 或把拒绝包装成已计算（闰月、绝对元运等门禁拒绝均走此失败态）。
    setSummary(null);
    setResult(null);
    setError("");
    let request: Promise<ExecuteResponse>;
    if (page.id === "yijing") {
      const bits = YIJING_HEXAGRAM_BITS[values.hexagram];
      if (!bits) {
        setError("请选择一个六十四卦。");
        return;
      }
      request = executeYijing({
        bits,
        changing_lines: YIJING_LINE_TO_CHANGING[values.line] ?? [],
      });
    } else if (page.id === "liuren") {
      if (!values.date || !values.time) {
        setError("请填写占时日期与时间。");
        return;
      }
      request = executeLiuren({
        value: `${values.date}T${values.time}:00+08:00`,
      });
    } else if (page.id === "ziwei") {
      if (!values.date || !values.time) {
        setError("请填写出生日期与时间。");
        return;
      }
      request = executeZiwei({
        value: `${values.date}T${values.time}:00+08:00`,
        year_boundary: "lunar-new-year",
      });
    } else if (page.id === "qimen") {
      if (!values.date || !values.time) {
        setError("请填写占时日期与时间。");
        return;
      }
      request = executeQimen({
        value: `${values.date}T${values.time}:00+08:00`,
      });
    } else {
      // fengshui: bearing in degrees.
      const degrees = Number(values.bearing);
      if (!values.bearing || !Number.isFinite(degrees) || degrees < 0 || degrees >= 360) {
        setError("请填写 0 至 359.99 之间的测量角度。");
        return;
      }
      request = executeFengshui({ degrees });
    }
    setLoading(true);
    try {
      setResult(await request);
    } catch (err) {
      setResult(null);
      setError(
        err instanceof ApiError
          ? err.message
          : "计算请求失败，请稍后重试。",
      );
    } finally {
      setLoading(false);
    }
  }
  function sample() {
    setValues({ ...page.sample });
    setLines(["9", "7", "7", "7", "7", "7"]);
    setSummary(null);
    setResult(null);
    setError("");
  }
  function reset() {
    setValues(initialValues(page));
    setLines(["", "", "", "", "", ""]);
    setSummary(null);
    setResult(null);
    setError("");
  }
  // 结果页链接：带上与本次计算完全相同的输入参数，结果页据此重新真实计算。
  const resultHref =
    page.id === "yijing"
      ? `/yijing/result?bits=${YIJING_HEXAGRAM_BITS[values.hexagram] || ""}&changing_lines=${(YIJING_LINE_TO_CHANGING[values.line] ?? []).join(",")}`
      : page.id === "liuren" && values.date && values.time
        ? `/liuren/result?value=${encodeURIComponent(`${values.date}T${values.time}:00+08:00`)}`
        : page.id === "ziwei" && values.date && values.time
          ? `/ziwei/result?value=${encodeURIComponent(`${values.date}T${values.time}:00+08:00`)}&year_boundary=lunar-new-year`
          : page.id === "qimen" && values.date && values.time
            ? `/qimen/result?value=${encodeURIComponent(`${values.date}T${values.time}:00+08:00`)}`
            : page.id === "fengshui" && values.bearing
              ? `/fengshui/result?degrees=${encodeURIComponent(values.bearing)}`
              : `/${page.id}/result`;
  return (
    <div className={"domain-home domain-" + page.id}>
      <div className="breadcrumb">
        <Link href="/">推演工具</Link>
        <Icon name="chevron" size={12} />
        <span>{page.name}</span>
      </div>
      <nav className="domain-switcher" aria-label="工具切换">
        {domainPages.map((item) => (
          <Link
            key={item.id}
            href={"/" + item.id}
            aria-current={item.id === page.id ? "page" : undefined}
          >
            <span>{item.glyph}</span>
            {item.name}
          </Link>
        ))}
      </nav>
      <header className="domain-heading">
        <div className="domain-seal" aria-hidden="true">
          {page.glyph}
        </div>
        <div>
          <span className="eyebrow">
            {page.name} · {page.en}
          </span>
          <h1>{page.title}</h1>
          <p>{page.introduction}</p>
        </div>
        <span className="entry-number">
          0{domainPages.indexOf(page) + 1}
          <small>七门 · 各循其法</small>
        </span>
      </header>
      <div className="entry-layout">
        <section className="entry-workspace">
          <div className="entry-panel-heading">
            <div>
              <span className="eyebrow">一 · 准备资料</span>
              <h2>{page.formTitle}</h2>
              <p>{page.formNote}</p>
            </div>
            <button className="sample-fill" type="button" onClick={sample}>
              <Icon name="file" size={16} />
              填入示例
            </button>
          </div>
          <form onSubmit={submit}>
            <div className="entry-fields">
              {page.fields
                .filter(
                  (field) =>
                    field.id !== "leapMonth" || values.calendar === "农历",
                )
                .map((field) => (
                  <Field
                    field={field}
                    key={field.id}
                    value={values[field.id] || ""}
                    onChange={(value) => update(field.id, value)}
                  />
                ))}
            </div>
            {page.id === "liuyao" && (
              <div
                className={"line-entry " + (linesOpen ? "line-entry-open" : "")}
              >
                <div>
                  <h3>六次爻值</h3>
                  <span>初爻在下 · 上爻在上</span>
                </div>
                <ol>
                  {lineLabels.map((label, index) => (
                    <li key={label}>
                      <label htmlFor={"line-" + index}>{label}</label>
                      <select
                        id={"line-" + index}
                        value={lines[index]}
                        onChange={(e) => {
                          setLines((prev) =>
                            prev.map((value, i) =>
                              i === index ? e.target.value : value,
                            ),
                          );
                          setSummary(null);
                          setError("");
                        }}
                      >
                        <option value="">请选择</option>
                        {Object.entries(lineNames).map(([value, name]) => (
                          <option key={value} value={value}>
                            {value} · {name}
                          </option>
                        ))}
                      </select>
                    </li>
                  ))}
                </ol>
                <p>
                  6 / 9 为动爻，7 / 8 为静爻。保留真实录入顺序，不随机生成。
                </p>
              </div>
            )}
            {error && (
              <p className="entry-error" role="alert">
                {error}
              </p>
            )}
            <div className="entry-submit-row">
              <button className="button primary" type="submit">
                确认资料
                <Icon name="arrow" size={18} />
              </button>
              <button className="entry-reset" type="button" onClick={reset}>
                清空
              </button>
            </div>
            <p className="entry-status">
              <Icon name="shield" size={15} />
              {page.id === "bazi"
                ? "八字基础档案已接入真实计算；此专业首页仍只做资料说明。"
                : connected
                  ? "已接入真实计算；结果仅为卦象 / 盘面结构，不作吉凶推断。"
                  : "当前为设计预览，仅展示输入摘要；不生成真实盘面。"}
            </p>
          </form>
          {summary && (
            <section
              className="entry-summary"
              aria-label="输入资料摘要"
              role="status"
            >
              <div>
                <Icon name="check" size={19} />
                <h3>资料已确认</h3>
                <span>尚未计算</span>
              </div>
              <dl>
                {summary.map(([label, value]) => (
                  <div key={label}>
                    <dt>{label}</dt>
                    <dd>{value}</dd>
                  </div>
                ))}
              </dl>
              <p>以上是你在当前页面填写的资料。真实计算与解读服务尚未接入。</p>
              <Link href={page.id === "bazi" ? "/bazi-profile" : "/" + page.id + "/result"} className="text-action">
                {page.id === "bazi"
                  ? "进入真实八字基础档案"
                  : page.id === "liuyao"
                    ? "另外查看固定六爻样例"
                    : "查看结果页设计"}
                <Icon name="arrow" size={16} />
              </Link>
            </section>
          )}
          {loading && (
            <p className="entry-status" role="status">
              正在计算……
            </p>
          )}
          {result && page.id === "yijing" && (
            <section
              className="entry-summary entry-result"
              aria-label="周易真实计算结果"
              role="status"
            >
              <div>
                <Icon name="check" size={19} />
                <h3>真实计算结果</h3>
                <span>仅卦象结构 · 不作吉凶推断</span>
              </div>
              <dl>
                <div>
                  <dt>本卦</dt>
                  <dd>{hexText(result.chart.original)}</dd>
                </div>
                <div>
                  <dt>变卦</dt>
                  <dd>{hexText(result.chart.change)}</dd>
                </div>
                <div>
                  <dt>错卦</dt>
                  <dd>{hexText(result.chart.opposite)}</dd>
                </div>
                <div>
                  <dt>综卦</dt>
                  <dd>{hexText(result.chart.inverse)}</dd>
                </div>
                <div>
                  <dt>互卦</dt>
                  <dd>{hexText(result.chart.nuclear)}</dd>
                </div>
              </dl>
              <Link href={resultHref} className="text-action">
                查看完整结果页
                <Icon name="arrow" size={16} />
              </Link>
            </section>
          )}
          {result && page.id === "liuren" && (
            <section
              className="entry-summary entry-result"
              aria-label="六壬真实计算结果"
              role="status"
            >
              <div>
                <Icon name="check" size={19} />
                <h3>真实计算结果</h3>
                <span>仅盘面结构 · 不作吉凶推断</span>
              </div>
              <dl>
                <div>
                  <dt>月将</dt>
                  <dd>
                    {result.chart.month_general?.name || "—"}（
                    {result.chart.month_general?.branch || "—"} ·{" "}
                    {(result.chart.month_general?.terms || []).join(" / ")}
                    ）
                  </dd>
                </div>
                <div>
                  <dt>取传法</dt>
                  <dd>{result.chart.method || "—"}</dd>
                </div>
                <div>
                  <dt>三传</dt>
                  <dd>
                    初传 {result.chart.transmissions?.[0] || "—"} · 中传{" "}
                    {result.chart.transmissions?.[1] || "—"} · 末传{" "}
                    {result.chart.transmissions?.[2] || "—"}
                  </dd>
                </div>
                <div>
                  <dt>四课</dt>
                  <dd>
                    一课 {lessonText(result.chart.four_lessons?.[0])} · 二课{" "}
                    {lessonText(result.chart.four_lessons?.[1])} · 三课{" "}
                    {lessonText(result.chart.four_lessons?.[2])} · 四课{" "}
                    {lessonText(result.chart.four_lessons?.[3])}
                  </dd>
                </div>
                <div>
                  <dt>天地盘</dt>
                  <dd>
                    {result.chart.sky_plate
                      ? Object.entries(result.chart.sky_plate)
                          .map(([earth, sky]) => `${earth}→${sky}`)
                          .join(" · ")
                      : "—"}
                  </dd>
                </div>
              </dl>
              {(result.chart.limitations || []).map((line: string) => (
                <p key={line}>{line}</p>
              ))}
              <Link href={resultHref} className="text-action">
                查看完整结果页
                <Icon name="arrow" size={16} />
              </Link>
            </section>
          )}
          {result && page.id === "ziwei" && (
            <section
              className="entry-summary entry-result"
              aria-label="紫微真实计算结果"
              role="status"
            >
              <div>
                <Icon name="check" size={19} />
                <h3>真实计算结果</h3>
                <span>仅安星结构 · 不作吉凶推断</span>
              </div>
              <dl>
                <div>
                  <dt>命宫与身宫</dt>
                  <dd>
                    命宫 {result.chart.life_palace || "—"} · 身宫{" "}
                    {result.chart.body_palace || "—"} · 命宫干支{" "}
                    {result.chart.life_ganzhi || "—"}
                  </dd>
                </div>
                <div>
                  <dt>局数</dt>
                  <dd>
                    {result.chart.bureau
                      ? `${result.chart.bureau.element}${result.chart.bureau.number}局`
                      : "—"}
                  </dd>
                </div>
                <div>
                  <dt>十二宫</dt>
                  <dd>
                    {result.chart.palaces
                      ? Object.entries(result.chart.palaces)
                          .map(([palace, branch]) => `${palace}→${branch}`)
                          .join(" · ")
                      : "—"}
                  </dd>
                </div>
                <div>
                  <dt>主星</dt>
                  <dd>
                    {result.chart.major_stars
                      ? Object.entries(result.chart.major_stars)
                          .map(([star, branch]) => `${star}→${branch}`)
                          .join(" · ")
                      : "—"}
                  </dd>
                </div>
                <div>
                  <dt>辅星</dt>
                  <dd>
                    {result.chart.auxiliary_stars
                      ? Object.entries(result.chart.auxiliary_stars)
                          .map(([star, branch]) => `${star}→${branch}`)
                          .join(" · ")
                      : "—"}
                  </dd>
                </div>
                <div>
                  <dt>四化</dt>
                  <dd>
                    {result.chart.four_transformations
                      ? Object.entries(result.chart.four_transformations)
                          .map(([kind, star]) => `${kind}→${star}`)
                          .join(" · ")
                      : "—"}
                    （{result.chart.mutagen_variant || "—"}）
                  </dd>
                </div>
              </dl>
              {result.chart.input_scope && <p>{result.chart.input_scope}</p>}
              {result.chart.mutagen_evidence && (
                <p>{result.chart.mutagen_evidence}</p>
              )}
              <p>
                闰月输入将被拒绝（仅非闰月农历）；大限流年、庙旺吉凶不在此基本盘中。
              </p>
              {(result.limitations || []).map((line: string) => (
                <p key={line}>{line}</p>
              ))}
              <Link href={resultHref} className="text-action">
                查看完整结果页
                <Icon name="arrow" size={16} />
              </Link>
            </section>
          )}
          {result && page.id === "qimen" && (
            <section
              className="entry-summary entry-result"
              aria-label="奇门真实计算结果"
              role="status"
            >
              <div>
                <Icon name="check" size={19} />
                <h3>真实计算结果</h3>
                <span>仅盘面结构 · 不作吉凶推断</span>
              </div>
              <dl>
                <div>
                  <dt>局法</dt>
                  <dd>
                    {result.chart.dun || "—"} · 第{result.chart.bureau || "—"}局 ·{" "}
                    {result.chart.yuan || "—"} · 节气{" "}
                    {result.chart.calendar?.solar_term || "—"} · 日干支{" "}
                    {result.chart.day_ganzhi || "—"} · 时干支{" "}
                    {result.chart.hour_ganzhi || "—"}
                  </dd>
                </div>
                <div>
                  <dt>值符与值使</dt>
                  <dd>
                    值符{" "}
                    {(result.chart.chief_star?.names || []).join(" / ") || "—"}（
                    {result.chart.chief_star?.palace || "—"}宫） · 值使{" "}
                    {result.chart.chief_door?.name || "—"}（
                    {result.chart.chief_door?.palace || "—"}宫）
                  </dd>
                </div>
                <div>
                  <dt>九星</dt>
                  <dd>
                    {result.chart.star_positions
                      ? Object.entries(result.chart.star_positions)
                          .map(([star, palace]) => `${star}→${palace}`)
                          .join(" · ")
                      : "—"}
                  </dd>
                </div>
                <div>
                  <dt>八门</dt>
                  <dd>
                    {result.chart.door_positions
                      ? Object.entries(result.chart.door_positions)
                          .map(([door, palace]) => `${door}→${palace}`)
                          .join(" · ")
                      : "—"}
                  </dd>
                </div>
                <div>
                  <dt>八神</dt>
                  <dd>
                    {result.chart.deity_positions
                      ? Object.entries(result.chart.deity_positions)
                          .map(([deity, palace]) => `${deity}→${palace}`)
                          .join(" · ")
                      : "—"}
                  </dd>
                </div>
              </dl>
              {result.chart.scope && <p>{result.chart.scope}</p>}
              {result.chart.center_star_policy && (
                <p>{result.chart.center_star_policy}</p>
              )}
              <p>超接置闰未实现；本结果不含置闰、超神接气、暗干与格局占断。</p>
              {(result.limitations || []).map((line: string) => (
                <p key={line}>{line}</p>
              ))}
              <Link href={resultHref} className="text-action">
                查看完整结果页
                <Icon name="arrow" size={16} />
              </Link>
            </section>
          )}
          {result && page.id === "fengshui" && (
            <section
              className="entry-summary entry-result"
              aria-label="风水真实计算结果"
              role="status"
            >
              <div>
                <Icon name="check" size={19} />
                <h3>真实计算结果</h3>
                <span>仅方位结构 · 不作吉凶推断</span>
              </div>
              <dl>
                <div>
                  <dt>测量角度</dt>
                  <dd>{result.chart.degrees ?? "—"}°</dd>
                </div>
                <div>
                  <dt>二十四山</dt>
                  <dd>
                    {result.chart.mountain || "—"}（
                    {result.chart.mountain_element || "—"}）
                  </dd>
                </div>
                <div>
                  <dt>卦象</dt>
                  <dd>
                    {result.chart.trigram || "—"}（
                    {result.chart.trigram_element || "—"}）
                  </dd>
                </div>
                <div>
                  <dt>对向</dt>
                  <dd>{result.chart.opposite || "—"}</dd>
                </div>
              </dl>
              <p>
                绝对元运未接入生产：本结果不含元运期数；元运口径需显式研究纪元，另立任务确立。
              </p>
              {(result.limitations || []).map((line: string) => (
                <p key={line}>{line}</p>
              ))}
              <Link href={resultHref} className="text-action">
                查看完整结果页
                <Icon name="arrow" size={16} />
              </Link>
            </section>
          )}
        </section>
        <aside className="entry-aside">
          <div className="entry-diagram">
            <span className="eyebrow">观其结构</span>
            <Diagram page={page} />
            <h2>{page.diagram}</h2>
            <p>固定布局示意 · 不随输入计算</p>
          </div>
          <div className="entry-reading">
            <span className="eyebrow">二 · 读懂结果</span>
            <h2>先看结构，再循来由</h2>
            <ol>
              {page.steps.map(([title, detail], i) => (
                <li key={title}>
                  <span>0{i + 1}</span>
                  <div>
                    <h3>{title}</h3>
                    <p>{detail}</p>
                  </div>
                </li>
              ))}
            </ol>
          </div>
          <Link className="entry-example" href={page.id === "bazi" ? "/bazi-profile" : "/" + page.id + "/result"}>
            <span>从结构开始</span>
            <strong>
              {page.id === "bazi" ? "真实四柱基础档案" : page.id === "liuyao" ? "乾为天 → 天风姤" : page.name + "结果页"}
            </strong>
            <p>
              {page.id === "bazi"
                ? "真实 API · 四柱 / 十神 / 藏干 / Evidence"
                : page.id === "liuyao"
                  ? "完整固定视觉示例"
                  : "查看布局与等待、失败状态"}
            </p>
            <Icon name="arrow" size={20} />
          </Link>
        </aside>
      </div>
      <section className="entry-guide">
        <div>
          <span className="eyebrow">开始之前</span>
          <h2>把边界，也看清</h2>
          <div className="entry-tags">
            {page.tags.map((tag) => (
              <span key={tag}>{tag}</span>
            ))}
          </div>
        </div>
        <div className="entry-questions">
          {page.questions.map(([question, answer]) => (
            <details key={question}>
              <summary>
                {question}
                <Icon name="chevron" size={16} />
              </summary>
              <p>{answer}</p>
            </details>
          ))}
        </div>
      </section>
      <div className="entry-return">
        <Link className="text-action" href="/">
          返回全部工具
          <Icon name="arrow" size={16} />
        </Link>
        <p>资料仅存在当前页面，不上传、不写入历史记录。</p>
      </div>
    </div>
  );
}
