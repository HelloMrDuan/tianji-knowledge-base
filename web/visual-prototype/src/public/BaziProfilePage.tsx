import { useState } from "react";
import type { FormEvent } from "react";
import { Icon } from "../shared/Icon";
import { Link } from "../shared/router";
import { executeBazi, type ExecuteResponse } from "./api";
import "./bazi-profile.css";

const pillarNames: Record<string, string> = {
  year: "年柱",
  month: "月柱",
  day: "日柱",
  hour: "时柱",
};

function displayEvidence(id: string, evidence: Record<string, any>) {
  const title =
    evidence.title ||
    evidence.classic_title ||
    evidence.classic ||
    evidence.work ||
    evidence.source_title ||
    "《渊海子平》";
  const quote =
    evidence.original_text ||
    evidence.quote ||
    evidence.anchor ||
    evidence.text ||
    "该证据已由后端绑定到本次确定性结果。";
  const grade =
    evidence.evidence_level ||
    evidence.grade ||
    evidence.level ||
    "—";
  return { id, title: String(title), quote: String(quote), grade: String(grade) };
}

export function BaziProfilePage() {
  const [date, setDate] = useState("");
  const [time, setTime] = useState("");
  const [result, setResult] = useState<ExecuteResponse | null>(null);
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
    if (!date || !time) return;
    setLoading(true);
    setError("");
    setResult(null);
    try {
      setResult(await executeBazi({ value: `${date}T${time}:00+08:00` }));
    } catch (err) {
      setError(err instanceof Error ? err.message : "八字计算失败，请检查后端服务。");
    } finally {
      setLoading(false);
    }
  }

  const chart = result?.chart || {};
  const pillars = Array.isArray(chart.pillars) ? chart.pillars : [];
  const calendar = result?.calendar || {};
  const evidence = result ? Object.entries(result.evidence).map(([id, value]) => displayEvidence(id, value)) : [];

  return (
    <div className="bazi-profile-page">
      <div className="breadcrumb">
        <Link href="/">生活场景</Link>
        <Icon name="chevron" size={12} />
        <span>八字基础档案</span>
      </div>

      <section className="bazi-profile-hero">
        <div>
          <span className="eyebrow">八字 · 真实确定性结构</span>
          <h1>先把四柱看清，再谈后面的事。</h1>
          <p>
            当前正式能力只计算四柱、日主、十神与藏干，并把规则和典籍依据一起返回。
            旺衰、喜用神、格局、桃花吉凶、事业财运等尚未完成证据裁定，因此这里不会提前生成断语。
          </p>
        </div>
        <div className="bazi-scope-card">
          <strong>现在真实可用</strong>
          <span>四柱</span>
          <span>日主</span>
          <span>十神</span>
          <span>藏干</span>
          <small>北京时间 · midnight 日界</small>
        </div>
      </section>

      <section className="bazi-profile-workspace">
        <form className="bazi-input-card" onSubmit={submit}>
          <div className="bazi-card-heading">
            <div>
              <span className="eyebrow">一 · 出生资料</span>
              <h2>公历出生时间</h2>
            </div>
            <button type="button" className="sample-fill" onClick={fillSample}>填入示例</button>
          </div>

          <div className="bazi-input-grid">
            <label>
              <span>出生日期</span>
              <input type="date" value={date} onChange={(e) => setDate(e.target.value)} required />
            </label>
            <label>
              <span>出生时间</span>
              <input type="time" value={time} onChange={(e) => setTime(e.target.value)} required />
            </label>
          </div>

          <div className="bazi-input-note">
            <Icon name="shield" size={16} />
            <span>当前固定按北京时间 UTC+8 计算；真太阳时、农历直接输入、晚子时变体尚未进入本生产口径。</span>
          </div>

          <button className="button primary bazi-submit" type="submit" disabled={loading}>
            {loading ? "正在计算…" : "生成基础档案"}
            {!loading && <Icon name="arrow" size={18} />}
          </button>
          {error && <p className="question-error" role="alert">{error}</p>}
        </form>

        <aside className="bazi-boundary-card">
          <span className="eyebrow">二 · 能力边界</span>
          <h2>不把“能算结构”说成“能断人生”</h2>
          <ul>
            <li>不计算旺衰强弱</li>
            <li>不选择喜用神</li>
            <li>不自动定格局、调候</li>
            <li>不输出婚恋、事业、财富吉凶</li>
            <li>不计算大运起运岁数</li>
          </ul>
          <p>这些能力会在规则、证据和 Golden Cases 完成后逐项开放。</p>
        </aside>
      </section>

      {!result && !loading && (
        <section className="bazi-empty">
          <span>命</span>
          <div>
            <h2>这里不会展示预制命盘</h2>
            <p>只有真实 API 返回后才生成四柱档案；后端失败就直接报错。</p>
          </div>
        </section>
      )}

      {result && (
        <section className="bazi-live-result">
          <header className="bazi-result-head">
            <div>
              <span className="eyebrow">真实 API · {result.variant}</span>
              <h2>{pillars.map((item: any) => item.ganzhi).join(" · ")}</h2>
              <p>
                {calendar.solar_term ? `节气：${calendar.solar_term} · ` : ""}
                日主：{chart.day_master?.stem || "—"} · {chart.day_master?.element || "—"} · {chart.day_master?.polarity || "—"}
              </p>
            </div>
            <span className="live-badge">确定性结果</span>
          </header>

          <div className="bazi-pillars">
            {pillars.map((item: any) => (
              <article key={item.name} className={item.name === "day" ? "day-pillar" : ""}>
                <span>{pillarNames[item.name] || item.name}</span>
                <strong>{item.ganzhi}</strong>
                <div className="bazi-stem">
                  <small>天干</small>
                  <b>{item.stem?.value}</b>
                  <em>{item.stem?.ten_god}</em>
                </div>
                <div className="bazi-branch">
                  <small>地支</small>
                  <b>{item.branch?.value}</b>
                  <div>
                    {(item.branch?.hidden_stems || []).map((hidden: any) => (
                      <span key={hidden.stem}>{hidden.stem}<i>{hidden.ten_god}</i></span>
                    ))}
                  </div>
                </div>
              </article>
            ))}
          </div>

          <div className="bazi-result-columns">
            <section className="live-section">
              <div className="result-section-heading"><div><span>三</span><h2>规则命中</h2></div></div>
              {result.rule_matches.map((rule, index) => (
                <article className="live-rule" key={rule.rule_id || index}>
                  <strong>{rule.rule_id || `规则 ${index + 1}`}</strong>
                  <p>{rule.evidence_scope || "本规则已由后端执行并绑定证据。"}</p>
                </article>
              ))}
            </section>

            <section className="live-section">
              <div className="result-section-heading"><div><span>四</span><h2>典籍依据</h2></div></div>
              {evidence.map((item) => (
                <article className="live-evidence" key={item.id}>
                  <div><strong>{item.title}</strong><span>{item.grade}</span></div>
                  <blockquote>{item.quote}</blockquote>
                  <small>{item.id}</small>
                </article>
              ))}
            </section>
          </div>

          <details className="trace-section bazi-trace">
            <summary>
              <span className="trace-icon"><Icon name="layers" size={19} /></span>
              <div><strong>查看计算过程</strong><small>真实 Trace，默认折叠</small></div>
              <Icon name="chevron" size={18} />
            </summary>
            <ol>
              {result.trace.map((step, index) => (
                <li key={index}>
                  <span>{String(index + 1).padStart(2, "0")}</span>
                  {step.rule_id || step.step || JSON.stringify(step)}
                </li>
              ))}
            </ol>
          </details>

          <div className="bazi-next-card">
            <div>
              <span className="eyebrow">下一阶段</span>
              <h3>从基础档案走向“2026 流年 / 桃花 / 事业财运”</h3>
              <p>这些场景会复用现在这份真实四柱结构，但必须等相应规则与证据补齐后才开放。</p>
            </div>
            <Link className="text-action" href="/">返回场景首页 <Icon name="arrow" size={16} /></Link>
          </div>
        </section>
      )}
    </div>
  );
}
