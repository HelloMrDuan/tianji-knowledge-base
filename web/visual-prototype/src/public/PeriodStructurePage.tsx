import { useEffect, useMemo, useRef, useState } from "react";
import type { FormEvent } from "react";
import { Icon } from "../shared/Icon";
import { Link } from "../shared/router";
import {
  executeMonthlyScenario,
  executeWeeklyScenario,
  type ScenarioExecuteResponse,
} from "./api";
import "./period-structure.css";

const profileKey = "tianji.profile.birth.v1";
const relationLabel: Record<string, string> = {six_harmony: "六合", harm: "六害", clash: "六冲"};
const pillarLabel: Record<string, string> = {year: "年柱", month: "月柱", day: "日柱", hour: "时柱"};

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
  const requestVersion = useRef(0);
  useEffect(() => () => { requestVersion.current += 1; }, []);
  function invalidateResult() {
    requestVersion.current += 1;
    setResult(null);
    setError("");
    setLoading(false);
  }

  const isWeekly = mode === "weekly";
  const title = isWeekly ? "本周结构" : "本月结构";
  const glyph = isWeekly ? "周" : "月";

  async function submit(event: FormEvent) {
    event.preventDefault();
    const version = ++requestVersion.current;
    setLoading(true);
    setError("");
    setResult(null);
    try {
      const birthValue = `${birthDate}T${birthTime}:00+08:00`;
      const next = isWeekly
        ? await executeWeeklyScenario({ birth_value: birthValue, anchor_date: anchorDate })
        : await executeMonthlyScenario({ birth_value: birthValue, target_month: targetMonth });
      if (version !== requestVersion.current) return;
      try {
        localStorage.setItem(profileKey, JSON.stringify({ date: birthDate, time: birthTime }));
      } catch {
        /* Local preference is optional. */
      }
      setResult(next);
    } catch (err) {
      if (version === requestVersion.current)
        setError(err instanceof Error ? err.message : `${title}计算失败。`);
    } finally {
      if (version === requestVersion.current) setLoading(false);
    }
  }

  const payload = result?.result || {};
  const period = isWeekly ? payload.week || {} : payload.month || {};
  const days = Array.isArray(period.days) ? period.days : [];
  const summary = payload.summary || {};
  const counts = summary.structure_group_counts || {};
  const xianchiDates = Array.isArray(summary.xianchi_hit_dates) ? summary.xianchi_hit_dates : [];
  const hitSet = new Set(xianchiDates.map((item: any) => item.date));
  const branchDates: Array<any> = Array.isArray(summary.branch_relation_dates) ? summary.branch_relation_dates : [];
  const branchCounts = summary.branch_relation_counts || {};
  const verifiedEvidence = result?.evidence || {};

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
            每一天都复用真实日干支、十神、咸池和已审地支冲合害。这里做的是周期分布，
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
              <input type="date" value={birthDate} onChange={(e) => { invalidateResult(); setBirthDate(e.target.value); }} required />
            </label>
            <label>
              <span>出生时间</span>
              <input type="time" value={birthTime} onChange={(e) => { invalidateResult(); setBirthTime(e.target.value); }} required />
            </label>
            {isWeekly ? (
              <label>
                <span>本周参考日期</span>
                <input type="date" value={anchorDate} onChange={(e) => { invalidateResult(); setAnchorDate(e.target.value); }} required />
              </label>
            ) : (
              <label>
                <span>查看月份</span>
                <input type="month" value={targetMonth} onChange={(e) => { invalidateResult(); setTargetMonth(e.target.value); }} required />
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
            <li>哪些日期与出生四柱匹配六合、六冲、六害</li>
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
                  {item.branch_interactions?.hits?.length > 0 && <b>冲合害 {item.branch_interactions.hits.length}</b>}
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

          {summary.branch_relation_counts && (
            <section className="period-section period-branch-evidence" aria-label="周期地支关系">
              <div className="result-section-heading">
                <div><span>支</span><h2>周期地支冲合害</h2></div>
                <small>经过审核的静态成对关系</small>
              </div>
              <p>六合 {branchCounts.six_harmony || 0} 条 · 六害 {branchCounts.harm || 0} 条 · 六冲 {branchCounts.clash || 0} 条；出现于 {branchDates.length} 个日期。</p>
              {branchDates.length ? (
                <div className="period-branch-dates">
                  {branchDates.map((day) => (
                    <article key={day.date}>
                      <strong>{day.date} · {day.ganzhi}</strong>
                      {(Array.isArray(day.relations) ? day.relations : []).map((hit: any, index: number) => {
                        const citations = Array.isArray(hit.evidence_ids) ? hit.evidence_ids.flatMap((id: string) => {
                          const record = verifiedEvidence[id];
                          if (!record || typeof record.original_text !== "string" || !record.original_text.trim()
                              || typeof record.classic_title !== "string" || !record.classic_title.trim()) return [];
                          return [{id, title: record.classic_title, quote: record.original_text,
                                   grade: typeof record.evidence_level === "string" ? record.evidence_level : "未标注"}];
                        }) : [];
                        return (
                          <div className="period-branch-relation" key={hit.rule_id + "-" + hit.natal_pillar + "-" + index}>
                            <span>{relationLabel[hit.relation_type] || hit.relation_type} · {hit.flow_branch} ↔ {hit.natal_branch} · {pillarLabel[hit.natal_pillar] || hit.natal_pillar}</span>
                            {citations.length ? (
                              <details>
                                <summary>对应古籍依据（{citations.length}）</summary>
                                {citations.map((ref) => (
                                  <blockquote key={ref.id}>
                                    <small>{ref.title} · {ref.grade}</small>
                                    <p>{ref.quote}</p>
                                  </blockquote>
                                ))}
                              </details>
                            ) : <small>缺少可核验的对应原典引文，不追加解释。</small>}
                          </div>
                        );
                      })}
                    </article>
                  ))}
                </div>
              ) : <p>本周期未命中本版审核的三类成对结构，不等于没有其他关系。</p>}
              <p className="period-note">只是结构分布，不判断作用效力、宜忌、财富或婚恋事件。</p>
            </section>
          )}

          <section className="period-return">
            <div>
              <span className="eyebrow">周期入口已经连起来</span>
              <h2>今日 → 本周 → 本月 → 流年</h2>
              <p>出生资料继续复用，不需要每次重新填写。</p>
            </div>
            <div>
              <Link href="/daily-structure">今日</Link>
              <Link href="/weekly-structure">本周</Link>
              <Link href="/monthly-structure">本月</Link>
              <Link href="/yearly-structure">流年</Link>
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
