import { useEffect, useMemo, useRef, useState } from "react";
import type { FormEvent } from "react";
import { Icon } from "../shared/Icon";
import { Link } from "../shared/router";
import { executeDailyScenario, type ScenarioExecuteResponse } from "./api";
import { readSavedBirthProfile, saveBirthProfile } from "./birthProfile";
import "./daily-structure.css";


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


const relationNames: Record<string, string> = {six_harmony: "六合", harm: "六害", clash: "六冲"};
const pillarNames: Record<string, string> = {year: "年柱", month: "月柱", day: "日柱", hour: "时柱"};

function displayEvidence(id: string, source: Record<string, any>) {
  const title = source.classic_title || source.title || source.source_title;
  const quote = source.original_text;
  if (typeof title !== "string" || !title.trim() ||
      typeof quote !== "string" || !quote.trim()) return null;
  return {id, title, quote, grade: typeof source.evidence_level === "string" ? source.evidence_level : "未标注"};
}

export function DailyStructurePage() {
  const saved = useMemo(readSavedBirthProfile, []);
  const today = useMemo(beijingToday, []);
  const [birthDate, setBirthDate] = useState(saved.date);
  const [birthTime, setBirthTime] = useState(saved.time);
  const [targetDate, setTargetDate] = useState(today);
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

  function fillSample() {
    setBirthDate("2000-01-07");
    setBirthTime("12:00");
    setTargetDate(today);
    invalidateResult();
  }

  async function submit(event: FormEvent) {
    event.preventDefault();
    const version = ++requestVersion.current;
    setLoading(true);
    setError("");
    setResult(null);
    try {
      const next = await executeDailyScenario({
        birth_value: `${birthDate}T${birthTime}:00+08:00`,
        target_date: targetDate,
      });
      if (version !== requestVersion.current) return;
      saveBirthProfile({ date: birthDate, time: birthTime });
      setResult(next);
    } catch (err) {
      if (version === requestVersion.current)
        setError(err instanceof Error ? err.message : "今日结构计算失败。");
    } finally {
      if (version === requestVersion.current) setLoading(false);
    }
  }

  const payload = result?.result || {};
  const target = payload.target_day || {};
  const natal = payload.natal || {};
  const xianchi = payload.xianchi || {};
  const activation = xianchi.target_day_activation || {};
  const evidence = result
    ? Object.entries(result.evidence).map(([id, value]) => displayEvidence(id, value))
        .filter((row): row is NonNullable<typeof row> => row !== null)
    : [];
  const evidenceById = new Map(evidence.map((row) => [row.id, row]));
  const branchStructure = payload.day_branch_interactions;
  const branchHits: Array<any> = Array.isArray(branchStructure?.hits) ? branchStructure.hits : [];
  const hitCount =
    Number(Boolean(activation.year_branch_basis?.matched)) +
    Number(Boolean(activation.day_branch_basis?.matched));

  return (
    <div className="daily-page">
      <div className="breadcrumb">
        <Link href="/">生活场景</Link>
        <Icon name="chevron" size={12} />
        <span>今日结构</span>
      </div>

      <section className="daily-hero">
        <div>
          <span className="eyebrow">每日回访入口 · 今日结构</span>
          <h1>不用重新排一遍，今天回来直接看今天。</h1>
          <p>
            如果你已经做过“人生总览”，出生资料会自动带入。这里每天只更新目标日干支、
            当日天干十神、两套咸池查表，以及当日地支与出生四柱的已审冲合害结构。
          </p>
        </div>
        <div className="daily-date-mark">
          <strong>{targetDate.slice(5).replace("-", "·")}</strong>
          <span>北京时间</span>
          <small>每日可重算</small>
        </div>
      </section>

      <section className="daily-entry">
        <form onSubmit={submit}>
          <div className="daily-entry-head">
            <div>
              <span className="eyebrow">{saved.date && saved.time ? "已带入上次资料" : "建立每日档案"}</span>
              <h2>查看当天结构</h2>
            </div>
            <button type="button" className="sample-fill" onClick={fillSample}>填入示例</button>
          </div>

          <div className="daily-input-grid">
            <label>
              <span>出生日期</span>
              <input type="date" value={birthDate} onChange={(e) => { invalidateResult(); setBirthDate(e.target.value); }} required />
            </label>
            <label>
              <span>出生时间</span>
              <input type="time" value={birthTime} onChange={(e) => { invalidateResult(); setBirthTime(e.target.value); }} required />
            </label>
            <label>
              <span>查看日期</span>
              <input type="date" value={targetDate} onChange={(e) => { invalidateResult(); setTargetDate(e.target.value); }} required />
            </label>
          </div>

          <div className="daily-entry-note">
            <Icon name="shield" size={16} />
            <span>目标日固定取北京时间中午计算日干支，避免时区与日界混淆；AI 不参与计算。</span>
          </div>
          <button className="button primary daily-submit" type="submit" disabled={loading}>
            {loading ? "正在计算…" : targetDate === today ? "查看今日结构" : "查看这一天的结构"}
            {!loading && <Icon name="arrow" size={18} />}
          </button>
          {error && <p className="question-error" role="alert">{error}</p>}
        </form>

        <aside>
          <span className="eyebrow">每天真正变化的部分</span>
          <h2>日干支 + 十神 + 咸池 + 地支冲合害</h2>
          <ul>
            <li>当天是什么干支</li>
            <li>当天的天干与你日主是什么十神</li>
            <li>当天地支是否等于年支基准咸池目标</li>
            <li>当天地支是否等于日支基准咸池目标</li>
            <li>当日地支与原局四柱是否匹配已审六合、六害、六冲</li>
          </ul>
          <p>当前不会把这些信号换算成“幸运指数”或宜忌清单。</p>
        </aside>
      </section>

      {!result && !loading && (
        <section className="daily-empty">
          <span>今</span>
          <div>
            <h2>{saved.date ? "你的出生资料已经准备好" : "先填一次出生资料"}</h2>
            <p>{saved.date ? "直接点击上方按钮，就能生成今天的真实结构。" : "生成后会保存在当前浏览器，明天回来无需重复填写。"}</p>
          </div>
        </section>
      )}

      {result && (
        <section className="daily-result">
          <header className="daily-result-head">
            <div>
              <span className="eyebrow">真实 Scenario Engine · daily_structure_only</span>
              <h2>{target.date || targetDate} · {target.ganzhi || "—"}</h2>
              <p>
                日主 <strong>{natal.day_master?.stem || "—"}</strong>
                <span> × </span>
                当日天干 <strong>{target.stem || "—"}</strong>
              </p>
            </div>
            <span className="daily-limited">每日结构</span>
          </header>

          <section className="daily-main-card">
            <div className="daily-ganzhi">
              <small>目标日干支</small>
              <strong>{target.ganzhi || "—"}</strong>
              <span>{target.structure_group_label || "—"}结构</span>
            </div>
            <div className="daily-relation">
              <span className="eyebrow">当天最核心的确定性关系</span>
              <h3>{target.stem || "—"} 相对 {natal.day_master?.stem || "—"} 为 {target.stem_ten_god || "—"}</h3>
              <p>{payload.summary?.text || "该关系由已审核十神规则计算。"}</p>
            </div>
          </section>

          {branchStructure && (
            <section className="daily-section daily-branch-structure" aria-label="日地支与原局关系">
              <div className="result-section-heading">
                <div><span>支</span><h2>今日地支 × 出生四柱</h2></div>
                <small>已核四组关系 · 命中 {branchHits.length} 条</small>
              </div>
              <p>今天的地支 <strong>{branchStructure.flow_branch}</strong> 与四柱逐一对照；只呈现已审核的六合、六害、六冲结构。</p>
              {branchHits.length ? (
                <div className="daily-branch-hits">
                  {branchHits.map((hit, index) => {
                    const linked = Array.isArray(hit.evidence_ids)
                      ? hit.evidence_ids.map((id: string) => evidenceById.get(id)).filter((ref: any) => ref !== undefined)
                      : [];
                    return (
                      <article key={hit.rule_id + "-" + hit.natal_pillar + "-" + index}>
                        <b>{relationNames[hit.relation_type] || hit.relation_type}</b>
                        <strong>{hit.flow_branch} ↔ {hit.natal_branch}</strong>
                        <span>{pillarNames[hit.natal_pillar] || hit.natal_pillar} · {hit.rule_id}</span>
                        {linked.length ? (
                          <details>
                            <summary>对应原典依据（{linked.length}）</summary>
                            {linked.map((ref: any) => (
                              <blockquote key={ref.id}>
                                <small>{ref.title} · 证据等级 {ref.grade}</small>
                                <p>{ref.quote}</p>
                              </blockquote>
                            ))}
                          </details>
                        ) : <p>暂无可核验的原典短引，不追加解释。</p>}
                      </article>
                    );
                  })}
                </div>
              ) : <p>当前未命中审核范围内的六合、六害、六冲；不代表没有其他关系。</p>}
              <p className="daily-note">结构命中不是吉凶、宜忌、婚期或投资建议。</p>
            </section>
          )}

          <div className="daily-double">
            <section className="daily-section">
              <div className="result-section-heading">
                <div><span>一</span><h2>今日桃花结构</h2></div>
                <small>{hitCount} 个基准命中</small>
              </div>
              <div className="daily-xianchi-grid">
                {[
                  ["year_branch_basis", "年支基准"],
                  ["day_branch_basis", "日支基准"],
                ].map(([key, label]) => {
                  const item = activation[key] || {};
                  return (
                    <article key={key} className={item.matched ? "matched" : ""}>
                      <small>{label}</small>
                      <strong>{item.target_branch || "—"}</strong>
                      <span>今日地支 {item.target_day_branch || target.branch || "—"}</span>
                      <em>{item.matched ? "结构命中" : "未命中"}</em>
                    </article>
                  );
                })}
              </div>
              <p className="daily-note">结构命中不等于今天一定有桃花、恋爱或关系事件。</p>
              <Link className="text-action" href="/romance-structure">查看桃花结构 <Icon name="arrow" size={15} /></Link>
            </section>

            <section className="daily-section">
              <div className="result-section-heading">
                <div><span>二</span><h2>典籍依据</h2></div>
                <small>{evidence.length} 条去重 Evidence</small>
              </div>
              <div className="daily-evidence-list">
                {evidence.slice(0, 4).map((item) => (
                  <article className="live-evidence" key={item.id}>
                    <div><strong>{item.title}</strong><span>{item.grade}</span></div>
                    <blockquote>{item.quote}</blockquote>
                    <small>{item.id}</small>
                  </article>
                ))}
              </div>
            </section>
          </div>

          <section className="daily-return">
            <div>
              <span className="eyebrow">明天回来</span>
              <h2>出生资料不用再填，日结构会随日期变化。</h2>
              <p>这才是网站的每日回访入口；遇到具体事情时，再转到一事占问。</p>
            </div>
            <div>
              <Link className="button outlined" href="/life-overview">返回人生总览</Link>
              <Link className="button primary" href="/ask">有事就问 <Icon name="arrow" size={16} /></Link>
            </div>
          </section>

          <details className="trace-section daily-trace">
            <summary>
              <span className="trace-icon"><Icon name="layers" size={19} /></span>
              <div><strong>查看今日计算过程</strong><small>{result.trace.length} 个 deterministic steps</small></div>
              <Icon name="chevron" size={18} />
            </summary>
            <ol>
              {result.trace.map((step, index) => (
                <li key={index}>
                  <span>{String(index + 1).padStart(2, "0")}</span>
                  {step.step || step.rule_id || "deterministic"}
                </li>
              ))}
            </ol>
          </details>

          <section className="daily-boundary">
            <strong>当前不是“今日吉凶”</strong>
            <p>{result.limitations.join(" ")}</p>
          </section>
        </section>
      )}
    </div>
  );
}
