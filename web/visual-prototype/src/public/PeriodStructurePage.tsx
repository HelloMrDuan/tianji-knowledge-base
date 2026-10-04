import { useMemo, useState } from "react";
import type { FormEvent } from "react";
import { Icon } from "../shared/Icon";
import { Link } from "../shared/router";
import {
  executeMonthlyScenario,
  executeWeeklyScenario,
  type ScenarioExecuteResponse,
} from "./api";
import { recordReading } from "./readingLibrary";
import "./period-structure.css";

const profileKey = "tianji.profile.birth.v1";
const groupLabel: Record<string, string> = {
  wealth: "财星",
  authority: "官杀",
  output: "食伤",
  resource: "印星",
  peers: "比劫",
};

function beijingToday() {
  const formatter = new Intl.DateTimeFormat("zh-CN", {
    timeZone: "Asia/Shanghai",
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
  });
  const parts = Object.fromEntries(
    formatter.formatToParts(new Date()).map((part) => [part.type, part.value]),
  );
  return `${parts.year}-${parts.month}-${parts.day}`;
}

function readProfile() {
  try {
    const raw = localStorage.getItem(profileKey);
    if (!raw) return { date: "", time: "" };
    const parsed = JSON.parse(raw);
    return {
      date: typeof parsed.date === "string" ? parsed.date : "",
      time: typeof parsed.time === "string" ? parsed.time : "",
    };
  } catch {
    return { date: "", time: "" };
  }
}

type PeriodMode = "weekly" | "monthly";

export function PeriodStructurePage({ mode }: { mode: PeriodMode }) {
  const saved = useMemo(readProfile, []);
  const today = useMemo(beijingToday, []);
  const [birthDate, setBirthDate] = useState(saved.date);
  const [birthTime, setBirthTime] = useState(saved.time);
  const [anchorDate, setAnchorDate] = useState(today);
  const [targetMonth, setTargetMonth] = useState(today.slice(0, 7));
  const [result, setResult] = useState<ScenarioExecuteResponse | null>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const isWeekly = mode === "weekly";
  const title = isWeekly ? "本周结构" : "本月结构";
  const glyph = isWeekly ? "周" : "月";

  async function submit(event: FormEvent) {
    event.preventDefault();
    setLoading(true);
    setError("");
    setResult(null);
    try {
      const birthValue = `${birthDate}T${birthTime}:00+08:00`;
      const next = isWeekly
        ? await executeWeeklyScenario({ birth_value: birthValue, anchor_date: anchorDate })
        : await executeMonthlyScenario({ birth_value: birthValue, target_month: targetMonth });
      try {
        localStorage.setItem(profileKey, JSON.stringify({ date: birthDate, time: birthTime }));
      } catch {
        /* Local preference is optional. */
      }
      const period = isWeekly ? next.result?.week || {} : next.result?.month || {};
      const summary = next.result?.summary || {};
      const hits = Array.isArray(summary.xianchi_hit_dates) ? summary.xianchi_hit_dates.length : 0;
      recordReading({
        scenarioId: isWeekly ? "weekly" : "monthly",
        label: isWeekly ? "本周结构" : "本月结构",
        glyph,
        title: isWeekly
          ? `${period.start_date || anchorDate} → ${period.end_date || "本周"}`
          : `${period.target_month || targetMonth} · 月度结构`,
        subtitle: `真实周期结构已生成 · 咸池命中日 ${hits} 天`,
        href: isWeekly ? "/weekly-structure" : "/monthly-structure",
        resultVersion: next.result?.report_version || next.status,
      });
      setResult(next);
    } catch (err) {
      setError(err instanceof Error ? err.message : `${title}计算失败。`);
    } finally {
      setLoading(false);
    }
  }

  const payload = result?.result || {};
  const period = isWeekly ? payload.week || {} : payload.month || {};
  const days = Array.isArray(period.days) ? period.days : [];
  const summary = payload.summary || {};
  const counts = summary.structure_group_counts || {};
  const xianchiDates = Array.isArray(summary.xianchi_hit_dates) ? summary.xianchi_hit_dates : [];
  const hitSet = new Set(xianchiDates.map((item: any) => item.date));

  return (
    <div className="period-page">
      <div className="breadcrumb">
        <Link href="/">生活场景</Link>
        <Icon name="chevron" size={12} />
        <span>{title}</span>
      </div>

      <section className="period-hero">
        <div>
          <span className="eyebrow">{title} · 周期结构内测</span>
          <h1>{isWeekly ? "把这一周七天摊开来看。" : "把这个月每天的结构排成一张月历。"}</h1>
          <p>
            每一天都复用真实的日干支、十神与咸池结构。这里做的是周期分布，
            不是把出现次数换算成“好运指数”。
          </p>
        </div>
        <div className="period-mark">
          <strong>{glyph}</strong>
          <span>{isWeekly ? "7 日" : "全月"}</span>
          <small>每日可追</small>
        </div>
      </section>

      <section className="period-entry">
        <form onSubmit={submit}>
          <div className="period-entry-head">
            <div>
              <span className="eyebrow">{saved.date ? "已复用人生总览资料" : "出生资料"}</span>
              <h2>生成{title}</h2>
            </div>
          </div>
          <div className="period-input-grid">
            <label>
              <span>出生日期</span>
              <input type="date" value={birthDate} onChange={(e) => setBirthDate(e.target.value)} required />
            </label>
            <label>
              <span>出生时间</span>
              <input type="time" value={birthTime} onChange={(e) => setBirthTime(e.target.value)} required />
            </label>
            {isWeekly ? (
              <label>
                <span>本周参考日期</span>
                <input type="date" value={anchorDate} onChange={(e) => setAnchorDate(e.target.value)} required />
              </label>
            ) : (
              <label>
                <span>查看月份</span>
                <input type="month" value={targetMonth} onChange={(e) => setTargetMonth(e.target.value)} required />
              </label>
            )}
          </div>
          <div className="period-entry-note">
            <Icon name="shield" size={16} />
            <span>{isWeekly ? "按北京时间自然周：周一至周日。" : "当前按公历自然月展示，不等同于传统节气流月。"}</span>
          </div>
          <button className="button primary period-submit" type="submit" disabled={loading}>
            {loading ? "正在计算…" : `查看${title}`}
            {!loading && <Icon name="arrow" size={18} />}
          </button>
          {error && <p className="question-error" role="alert">{error}</p>}
        </form>

        <aside>
          <span className="eyebrow">周期里看什么</span>
          <h2>看分布，不做“哪天必发财”的表。</h2>
          <ul>
            <li>每天的干支与十神关系</li>
            <li>五类十神结构在周期内出现多少天</li>
            <li>哪些日期出现咸池固定查表命中</li>
            <li>每一天都能回到底层 Evidence</li>
          </ul>
        </aside>
      </section>

      {!result && !loading && (
        <section className="period-empty">
          <span>{glyph}</span>
          <div>
            <h2>{saved.date ? "出生资料已经准备好" : "先建立一次出生资料"}</h2>
            <p>点击生成后才会展示真实周期结构，不使用预制周运/月运。</p>
          </div>
        </section>
      )}

      {result && (
        <section className="period-result">
          <header className="period-result-head">
            <div>
              <span className="eyebrow">真实 Scenario Engine · {payload.release_scope}</span>
              <h2>
                {isWeekly
                  ? `${period.start_date || "—"} → ${period.end_date || "—"}`
                  : period.target_month || targetMonth}
              </h2>
              <p>
                日主 <strong>{payload.natal?.day_master?.stem || "—"}</strong>
                <span> · </span>
                共 <strong>{days.length}</strong> 天
                <span> · </span>
                咸池结构命中日 <strong>{xianchiDates.length}</strong> 天
              </p>
            </div>
            <span className="period-limited">{title}</span>
          </header>

          <section className="period-summary">
            {Object.entries(groupLabel).map(([id, label]) => (
              <article key={id}>
                <small>{label}</small>
                <strong>{counts[id] || 0}</strong>
                <span>天</span>
              </article>
            ))}
          </section>

          <section className="period-section">
            <div className="result-section-heading">
              <div><span>一</span><h2>{isWeekly ? "七日结构" : "月度日历结构"}</h2></div>
              <small>金色标记 = 咸池查表命中日</small>
            </div>
            <div className={isWeekly ? "period-days weekly" : "period-days monthly"}>
              {days.map((item: any) => (
                <article key={item.date} className={hitSet.has(item.date) ? "xianchi-hit" : ""}>
                  <small>{item.date.slice(5)}</small>
                  <strong>{item.ganzhi}</strong>
                  <span>{item.stem_ten_god}</span>
                  <em>{item.structure_group_label || "—"}</em>
                  {item.xianchi_hit_count > 0 && <b>咸池 {item.xianchi_hit_count}</b>}
                </article>
              ))}
            </div>
          </section>

          {xianchiDates.length > 0 && (
            <section className="period-section">
              <div className="result-section-heading">
                <div><span>二</span><h2>咸池结构命中日期</h2></div>
              </div>
              <div className="period-hit-list">
                {xianchiDates.map((item: any) => (
                  <span key={item.date}>{item.date} · {item.ganzhi} · {item.hit_count} 个基准</span>
                ))}
              </div>
              <p className="period-note">这些日期只表示固定查表结构相同，不等于一定发生感情事件。</p>
            </section>
          )}

          <section className="period-return">
            <div>
              <span className="eyebrow">周期入口已经连起来</span>
              <h2>今日 → 本周 → 本月 → 2026</h2>
              <p>出生资料继续复用，不需要每次重新填写。</p>
            </div>
            <div>
              <Link href="/daily-structure">今日</Link>
              <Link href="/weekly-structure">本周</Link>
              <Link href="/monthly-structure">本月</Link>
              <Link href="/yearly-structure">2026</Link>
            </div>
          </section>

          <details className="trace-section period-trace">
            <summary>
              <span className="trace-icon"><Icon name="layers" size={19} /></span>
              <div><strong>查看周期计算过程</strong><small>{result.trace.length} 个日级 Trace</small></div>
              <Icon name="chevron" size={18} />
            </summary>
            <ol>
              {result.trace.map((step, index) => (
                <li key={index}>
                  <span>{String(index + 1).padStart(2, "0")}</span>
                  {step.date || "—"} · {step.facts?.ganzhi || "—"} · {step.facts?.ten_god || "—"}
                </li>
              ))}
            </ol>
          </details>

          <section className="period-boundary">
            <strong>当前边界</strong>
            <p>{result.limitations.join(" ")}</p>
          </section>
        </section>
      )}
    </div>
  );
}
