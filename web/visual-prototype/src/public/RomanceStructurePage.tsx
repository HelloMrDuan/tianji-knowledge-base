import { useState } from "react";
import type { FormEvent } from "react";
import { Icon } from "../shared/Icon";
import { Link } from "../shared/router";
import { executeRomanceScenario, type ScenarioExecuteResponse } from "./api";
import { recordReading } from "./readingLibrary";
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
      const next = await executeRomanceScenario({
        birth_value: `${date}T${time}:00+08:00`,
        target_year: 2026,
      });
      const target = next.result?.target_year || {};
      const activation = next.result?.target_year_activation || {};
      const hitCount = ["year_branch_basis", "day_branch_basis"].filter((key) => activation[key]?.matched).length;
      recordReading({
        scenarioId: "romance",
        label: "桃花姻缘",
        glyph: "缘",
        title: `2026 ${target.ganzhi || "桃花结构"}`,
        subtitle: `咸池结构命中 ${hitCount} 个基准 · 仅结构事实`,
        href: "/romance-structure",
        resultVersion: next.result?.report_version || next.status,
      });
      setResult(next);
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
            当前只做一件可靠的事：依据已审核的《三命通会》咸池四组，
            把年支和日支两套起查结果分别列出来，并检查原局与 2026 流年地支是否命中。
            不用一个神煞就替你下婚恋结论。
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
          <p>后续会在配偶星、夫妻宫、合冲刑害、旺衰喜忌等证据完成后再逐层扩展。</p>
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

          <section className="romance-natal">
            <div className="result-section-heading">
              <div><span>一</span><h2>你的原局四柱</h2></div>
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
              <div className="result-section-heading"><div><span>二</span><h2>典籍依据</h2></div></div>
              {evidence.map((item) => (
                <article className="live-evidence" key={item.id}>
                  <div><strong>{item.title}</strong><span>{item.grade}</span></div>
                  <blockquote>{item.quote}</blockquote>
                  <small>{item.id}</small>
                </article>
              ))}
            </section>

            <section className="live-section romance-limits">
              <div className="result-section-heading"><div><span>三</span><h2>边界与下一步</h2></div></div>
              {result.limitations.map((item, index) => <p key={index}>{item}</p>)}
              {result.warnings.map((item, index) => <div className="live-warning" key={index}>{item}</div>)}
            </section>
          </div>

          <details className="trace-section romance-trace">
            <summary>
              <span className="trace-icon"><Icon name="layers" size={19} /></span>
              <div><strong>查看计算过程</strong><small>咸池查表 → 目标年 → 双基准命中</small></div>
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
                接下来继续补配偶星、夫妻宫、合冲刑害和流年互动，再考虑紫微交叉证据。
                这些完成前，本页只叫“结构内测”。
              </p>
            </div>
          </div>
        </section>
      )}
    </div>
  );
}
