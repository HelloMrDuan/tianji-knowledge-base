import { useState } from "react";
import type { FormEvent } from "react";
import { Icon } from "../shared/Icon";
import { Link } from "../shared/router";
import { executeRomanceScenario, type ScenarioExecuteResponse } from "./api";
import "./romance-structure.css";

const pillarNames: Record<string, string> = {
  year: "年柱",
  month: "月柱",
  day: "日柱",
  hour: "时柱",
};

function displayEvidence(id: string, evidence: Record<string, any>) {
  return {
    id,
    title: String(
      evidence.classic_title ||
      evidence.title ||
      evidence.classic ||
      evidence.source_title ||
      "《三命通会》",
    ),
    quote: String(
      evidence.original_text ||
      evidence.quote ||
      evidence.text ||
      "该证据已由服务端绑定。",
    ),
    grade: String(evidence.evidence_level || evidence.grade || "—"),
  };
}

function relationLabel(kind: string) {
  if (kind === "six_harmony") return "六合";
  if (kind === "harm") return "六害";
  if (kind === "clash") return "六冲";
  return kind;
}

function basisLabel(value: string) {
  return value === "year_branch" ? "年支起查" : value === "day_branch" ? "日支起查" : value;
}

export function RomanceStructurePage() {
  const [date, setDate] = useState("");
  const [time, setTime] = useState("");
  const [result, setResult] = useState<ScenarioExecuteResponse | null>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  function fillSample() {
    setDate("2000-01-07");
    setTime("12:00");
    setResult(null);
    setError("");
  }

  async function submit(event: FormEvent) {
    event.preventDefault();
    setLoading(true);
    setError("");
    setResult(null);
    try {
      setResult(
        await executeRomanceScenario({
          birth_value: `${date}T${time}:00+08:00`,
          target_year: 2026,
        }),
      );
    } catch (err) {
      setError(err instanceof Error ? err.message : "桃花结构计算失败。");
    } finally {
      setLoading(false);
    }
  }

  const payload = result?.result || {};
  const natal = payload.natal || {};
  const pillars = Array.isArray(natal.pillars) ? natal.pillars : [];
  const xianchi = payload.xianchi || {};
  const targets = xianchi.targets || {};
  const natalMatches = Array.isArray(xianchi.natal_matches) ? xianchi.natal_matches : [];
  const activation = payload.target_year_activation || {};
  const targetYear = payload.target_year || {};
  const flowRelations = Array.isArray(payload.flow_branch_relations) ? payload.flow_branch_relations : [];
  const spouseInteraction = payload.spouse_palace_interaction || {};
  const spouseRelations = Array.isArray(spouseInteraction.relations) ? spouseInteraction.relations : [];
  const evidence = result
    ? Object.entries(result.evidence).map(([id, value]) => displayEvidence(id, value))
    : [];

  const yearMatches = natalMatches.filter((item: any) => item.basis === "year_branch");
  const dayMatches = natalMatches.filter((item: any) => item.basis === "day_branch");

  return (
    <div className="romance-page">
      <div className="breadcrumb">
        <Link href="/">生活场景</Link>
        <Icon name="chevron" size={12} />
        <span>桃花姻缘 · 结构内测</span>
      </div>

      <section className="romance-hero">
        <div className="romance-hero-copy">
          <span className="eyebrow">桃花姻缘 · 第一层真实能力</span>
          <h1>先看“桃花结构”有没有命中，再谈它意味着什么。</h1>
          <p>
            当前把两层已审核结构放到一起：先按《三命通会》分别列出年支、日支两套咸池目标，
            再检查 2026 流年支与原局、尤其日支传统配偶宫是否命中六合、六害或六冲。
            所有命中都只作为结构事实，不替你下婚恋结论。
          </p>
        </div>
        <div className="romance-mark" aria-hidden="true">
          <span>缘</span>
          <small>有据再言</small>
        </div>
      </section>

      <section className="romance-entry">
        <form onSubmit={submit}>
          <div className="romance-entry-head">
            <div>
              <span className="eyebrow">输入出生资料</span>
              <h2>查看你的咸池结构</h2>
            </div>
            <button type="button" className="sample-fill" onClick={fillSample}>填入示例</button>
          </div>
          <div className="romance-input-grid">
            <label>
              <span>出生日期</span>
              <input type="date" value={date} onChange={(e) => setDate(e.target.value)} required />
            </label>
            <label>
              <span>出生时间</span>
              <input type="time" value={time} onChange={(e) => setTime(e.target.value)} required />
            </label>
            <label className="romance-fixed-year">
              <span>观察年份</span>
              <input value="2026" readOnly />
            </label>
          </div>
          <div className="romance-entry-note">
            <Icon name="shield" size={16} />
            <span>北京时间 UTC+8。年支与日支分别计算，不强行合并成唯一流派结论。</span>
          </div>
          <button className="button primary romance-submit" type="submit" disabled={loading}>
            {loading ? "正在计算…" : "查看桃花结构"}
            {!loading && <Icon name="arrow" size={18} />}
          </button>
          {error && <p className="question-error" role="alert">{error}</p>}
        </form>

        <aside>
          <span className="eyebrow">当前不会输出</span>
          <h2>没有“桃花指数”，也不预测何时脱单</h2>
          <ul>
            <li>不把咸池命中等同于桃花旺</li>
            <li>不判断正缘、烂桃花或婚姻吉凶</li>
            <li>不根据古籍旧式断语推断性格、疾病</li>
            <li>不使用 AI 补齐缺失规则</li>
          </ul>
          <p>配偶宫与固定六合/六害/六冲已经接入；配偶星目前只在合盘里由用户显式选择传统口径。旺衰喜忌、三刑与紫微交叉仍待后续裁定。</p>
        </aside>
      </section>

      {!result && !loading && (
        <section className="romance-empty">
          <span>缘</span>
          <div>
            <h2>这里没有预制“情感文案”</h2>
            <p>真实 Scenario Engine 返回后，才展示你的结构结果。</p>
          </div>
        </section>
      )}

      {result && (
        <section className="romance-result">
          <header className="romance-result-head">
            <div>
              <span className="eyebrow">真实 Scenario Engine · production_limited</span>
              <h2>
                年支目标 {targets.year_branch || "—"}
                <span> · </span>
                日支目标 {targets.day_branch || "—"}
              </h2>
              <p>
                2026 {targetYear.ganzhi || "—"} · 流年地支 {targetYear.branch || "—"}。
                两个基准分别展示，不互相覆盖。
              </p>
            </div>
            <span className="romance-limited">结构内测</span>
          </header>

          <div className="romance-basis-grid">
            <article>
              <div className="romance-basis-title">
                <span>年</span>
                <div><small>年支起查</small><strong>咸池目标：{targets.year_branch || "—"}</strong></div>
              </div>
              <div className="romance-signal">
                <span>原局命中</span>
                <b>{yearMatches.length ? "有结构命中" : "未见结构命中"}</b>
              </div>
              <div className="romance-signal">
                <span>2026 流年</span>
                <b>{activation.year_branch_basis?.matched ? "命中目标支" : "未命中目标支"}</b>
              </div>
              {yearMatches.length > 0 && (
                <p>原局位置：{yearMatches.map((item: any) => pillarNames[item.pillar] || item.pillar).join("、")}</p>
              )}
            </article>

            <article>
              <div className="romance-basis-title">
                <span>日</span>
                <div><small>日支起查</small><strong>咸池目标：{targets.day_branch || "—"}</strong></div>
              </div>
              <div className="romance-signal">
                <span>原局命中</span>
                <b>{dayMatches.length ? "有结构命中" : "未见结构命中"}</b>
              </div>
              <div className="romance-signal">
                <span>2026 流年</span>
                <b>{activation.day_branch_basis?.matched ? "命中目标支" : "未命中目标支"}</b>
              </div>
              {dayMatches.length > 0 && (
                <p>原局位置：{dayMatches.map((item: any) => pillarNames[item.pillar] || item.pillar).join("、")}</p>
              )}
            </article>
          </div>

          <section className="romance-flow-relations">
            <div className="result-section-heading">
              <div><span>合</span><h2>2026 流年支 × 原局关系</h2></div>
              <small>六合 · 六害 · 六冲</small>
            </div>
            <div className="romance-spouse-focus">
              <small>{spouseInteraction.label || "日支（传统配偶宫结构位）"}</small>
              <strong>{spouseInteraction.day_branch || "—"} × {spouseInteraction.target_year_branch || targetYear.branch || "—"}</strong>
              <span>
                {spouseRelations.length
                  ? spouseRelations.map((item: any) => relationLabel(item.kind)).join("、")
                  : "当前无已审核关系命中"}
              </span>
              <em>这里只标记结构，不等于适合、不适合、争执、分手或婚姻结果。</em>
            </div>
            {flowRelations.length > 0 && (
              <div className="romance-flow-grid">
                {flowRelations.map((item: any, index: number) => (
                  <article key={index} className={item.natal_pillar === "day" ? "day-relation" : ""}>
                    <small>{pillarNames[item.natal_pillar] || item.natal_pillar}</small>
                    <strong>{item.natal_branch} · {item.flow_branch}</strong>
                    <span>{relationLabel(item.kind)}</span>
                    {item.traditional_result_element && <em>传统表字段：{item.traditional_result_element}</em>}
                  </article>
                ))}
              </div>
            )}
          </section>

          <section className="romance-natal">
            <div className="result-section-heading">
              <div><span>二</span><h2>你的原局四柱</h2></div>
              <small>只用于结构定位</small>
            </div>
            <div className="romance-pillars">
              {pillars.map((item: any) => (
                <article key={item.name} className={item.name === "day" ? "day-pillar" : ""}>
                  <small>{pillarNames[item.name] || item.name}</small>
                  <strong>{item.ganzhi}</strong>
                  <span>{item.stem?.ten_god}</span>
                </article>
              ))}
            </div>
          </section>

          <div className="romance-two-columns">
            <section className="live-section">
              <div className="result-section-heading"><div><span>三</span><h2>典籍依据</h2></div></div>
              {evidence.map((item) => (
                <article className="live-evidence" key={item.id}>
                  <div><strong>{item.title}</strong><span>{item.grade}</span></div>
                  <blockquote>{item.quote}</blockquote>
                  <small>{item.id}</small>
                </article>
              ))}
            </section>

            <section className="live-section romance-limits">
              <div className="result-section-heading"><div><span>四</span><h2>边界与下一步</h2></div></div>
              {result.limitations.map((item, index) => <p key={index}>{item}</p>)}
              {result.warnings.map((item, index) => <div className="live-warning" key={index}>{item}</div>)}
            </section>
          </div>

          <details className="trace-section romance-trace">
            <summary>
              <span className="trace-icon"><Icon name="layers" size={19} /></span>
              <div><strong>查看计算过程</strong><small>咸池查表 → 目标年 → 双基准命中 → 流年支关系</small></div>
              <Icon name="chevron" size={18} />
            </summary>
            <ol>
              {result.trace.map((step, index) => (
                <li key={index}>
                  <span>{String(index + 1).padStart(2, "0")}</span>
                  {step.step || step.rule_id || JSON.stringify(step)}
                </li>
              ))}
            </ol>
          </details>

          <div className="romance-next">
            <span>合</span>
            <div>
              <h3>下一层才是真正的“桃花姻缘报告”</h3>
              <p>
                咸池、日支传统配偶宫、六合/六害/六冲与流年互动已经进入本页。
                下一阶段主要是可选配偶星 lens、旺衰喜忌、三刑流派裁定与紫微交叉证据。
              </p>
            </div>
          </div>
        </section>
      )}
    </div>
  );
}
