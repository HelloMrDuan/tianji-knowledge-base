import { useMemo, useState } from "react";
import type { FormEvent } from "react";
import { Icon } from "../shared/Icon";
import { Link } from "../shared/router";
import { executeLiuyao, type ExecuteResponse } from "./api";
import "./question.css";

const labels = ["初爻", "二爻", "三爻", "四爻", "五爻", "上爻"];
const yaoText: Record<number, string> = {
  6: "老阴 · 动",
  7: "少阳 · 静",
  8: "少阴 · 静",
  9: "老阳 · 动",
};

function chinaNow() {
  const formatter = new Intl.DateTimeFormat("zh-CN", {
    timeZone: "Asia/Shanghai",
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
    hour12: false,
  });
  const parts = Object.fromEntries(
    formatter.formatToParts(new Date()).map((item) => [item.type, item.value]),
  );
  return {
    date: `${parts.year}-${parts.month}-${parts.day}`,
    time: `${parts.hour}:${parts.minute}`,
  };
}

function castLine() {
  const bytes = new Uint8Array(3);
  crypto.getRandomValues(bytes);
  return Array.from(bytes).reduce((sum, value) => sum + (value % 2 ? 3 : 2), 0);
}

function displayEvidence(id: string, evidence: Record<string, any>) {
  const title =
    evidence.title ||
    evidence.classic ||
    evidence.work ||
    evidence.source_title ||
    evidence.source_id ||
    id;
  const quote =
    evidence.quote ||
    evidence.original_text ||
    evidence.anchor ||
    evidence.text ||
    "该证据已由后端绑定到本次执行结果。";
  const grade =
    evidence.grade ||
    evidence.evidence_grade ||
    evidence.level ||
    evidence.source_grade ||
    "—";
  return { title: String(title), quote: String(quote), grade: String(grade) };
}

export function QuestionPage() {
  const initial = useMemo(chinaNow, []);
  const [question, setQuestion] = useState("");
  const [date, setDate] = useState(initial.date);
  const [time, setTime] = useState(initial.time);
  const [yaoValues, setYaoValues] = useState<number[]>([7, 7, 7, 7, 7, 7]);
  const [result, setResult] = useState<ExecuteResponse | null>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const randomCast = () => {
    setYaoValues(Array.from({ length: 6 }, () => castLine()));
    setResult(null);
  };

  async function submit(event: FormEvent) {
    event.preventDefault();
    setError("");
    setLoading(true);
    setResult(null);
    try {
      const value = `${date}T${time}:00+08:00`;
      setResult(await executeLiuyao({ value, yao_values: yaoValues }));
    } catch (err) {
      setError(err instanceof Error ? err.message : "排盘请求失败，请检查后端服务。");
    } finally {
      setLoading(false);
    }
  }

  const chart = result?.chart || {};
  const original = chart.original || {};
  const changed = chart.changed || {};
  const palace = chart.palace || {};
  const lines = Array.isArray(chart.lines) ? chart.lines : [];

  return (
    <div className="question-page">
      <div className="breadcrumb">
        <Link href="/">生活场景</Link>
        <Icon name="chevron" size={12} />
        <span>一事占问</span>
      </div>

      <section className="question-hero">
        <div>
          <span className="eyebrow">一事占问 · 六爻先行版</span>
          <h1>心里有一件事，就从这一件事问起。</h1>
          <p>把问题写清楚，录入六爻。排盘、规则和依据全部来自现有确定性后端，AI 暂不参与计算。</p>
        </div>
        <div className="question-boundary">
          <strong>当前边界</strong>
          <span>真实排盘</span>
          <span>真实 RuleMatch</span>
          <span>真实 Evidence</span>
          <span>AI 解读关闭</span>
        </div>
      </section>

      <form className="question-workspace" onSubmit={submit}>
        <section className="question-form-card">
          <div className="result-section-heading">
            <div><span>一</span><h2>写下这件事</h2></div>
          </div>
          <label className="question-field">
            <span>你现在最想问什么？</span>
            <textarea
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              placeholder="例如：现在这个工作机会，我是否适合继续推进？"
              maxLength={180}
            />
            <small>问题用于当前页面阅读，不发送给排盘引擎；排盘只使用起卦时间与六爻值。</small>
          </label>
          <div className="question-time-grid">
            <label className="question-field">
              <span>起卦日期</span>
              <input type="date" value={date} onChange={(e) => setDate(e.target.value)} required />
            </label>
            <label className="question-field">
              <span>起卦时间</span>
              <input type="time" value={time} onChange={(e) => setTime(e.target.value)} required />
            </label>
          </div>
          <p className="question-zone">固定口径：北京时间（UTC+8）</p>
        </section>

        <section className="question-form-card">
          <div className="question-card-title">
            <div className="result-section-heading">
              <div><span>二</span><h2>录入六爻</h2></div>
            </div>
            <button className="button outlined compact-button" type="button" onClick={randomCast}>
              模拟投六次铜钱
            </button>
          </div>
          <p className="question-help">自下而上：第一次是初爻，第六次是上爻。已有实际起卦结果时，请直接手动选择。</p>
          <div className="yao-input-list">
            {yaoValues.map((value, index) => (
              <label key={index} className={value === 6 || value === 9 ? "is-moving" : ""}>
                <span className="yao-order">{labels[index]}</span>
                <span className={"mini-yao " + (value === 7 || value === 9 ? "yang" : "yin")}>
                  <i /><i />
                </span>
                <select
                  value={value}
                  onChange={(e) => {
                    const next = [...yaoValues];
                    next[index] = Number(e.target.value);
                    setYaoValues(next);
                    setResult(null);
                  }}
                >
                  {[6, 7, 8, 9].map((item) => <option key={item} value={item}>{item} · {yaoText[item]}</option>)}
                </select>
              </label>
            ))}
          </div>
          <button className="button primary question-submit" disabled={loading} type="submit">
            {loading ? "正在排盘…" : "开始推演"}
            {!loading && <Icon name="arrow" size={18} />}
          </button>
          {error && <div className="question-error" role="alert">{error}</div>}
        </section>
      </form>

      {!result && !loading && (
        <section className="question-empty">
          <span>问</span>
          <div>
            <h2>先完成一次真实排盘</h2>
            <p>结果不会使用静态示例替代。后端不可用时会明确报错，不生成假的盘面。</p>
          </div>
        </section>
      )}

      {result && (
        <section className="live-result">
          <div className="live-result-head">
            <div>
              <span className="eyebrow">确定性结果 · {result.variant}</span>
              <h2>{original.name || `第 ${original.number || "—"} 卦`} → {changed.name || `第 ${changed.number || "—"} 卦`}</h2>
              {question && <p>本次问题：{question}</p>}
            </div>
            <span className="live-badge">真实 API</span>
          </div>

          <div className="live-summary-grid">
            <article><small>本卦</small><strong>{original.name || original.number || "—"}</strong><span>{original.lower || "—"}下 · {original.upper || "—"}上</span></article>
            <article><small>所属宫</small><strong>{palace.palace || "—"}宫</strong><span>{palace.sequence || "—"} · 五行 {palace.element || "—"}</span></article>
            <article><small>动爻</small><strong>{(chart.changing_lines || []).join("、") || "无"}</strong><span>自下而上计数</span></article>
            <article><small>旬空</small><strong>{(chart.empty_branches || []).join("、") || "—"}</strong><span>由后端历法计算</span></article>
          </div>

          <div className="live-section">
            <div className="result-section-heading"><div><span>三</span><h2>六爻盘面</h2></div><small>自下而上</small></div>
            <div className="live-lines">
              {[...lines].reverse().map((line: any) => (
                <div key={line.position} className={line.moving ? "live-line moving" : "live-line"}>
                  <span>{labels[(line.position || 1) - 1]}</span>
                  <span>{line.spirit || "—"}</span>
                  <strong>{line.relative || "—"} · {line.najia || "—"}</strong>
                  <span>{line.element || "—"}</span>
                  <span>{line.moving ? "动" : "静"}</span>
                  <span>{line.empty ? "空" : line.month_break ? "月破" : "—"}</span>
                </div>
              ))}
            </div>
          </div>

          <div className="live-columns">
            <section className="live-section">
              <div className="result-section-heading"><div><span>四</span><h2>规则命中</h2></div></div>
              {result.rule_matches.length ? result.rule_matches.map((rule, index) => (
                <article className="live-rule" key={index}>
                  <strong>{rule.rule_id || `规则 ${index + 1}`}</strong>
                  <p>{Object.entries(rule).filter(([key]) => key !== "rule_id").map(([key, value]) => `${key}: ${String(value)}`).join(" · ") || "本规则已命中。"}</p>
                </article>
              )) : <p className="live-muted">本次没有额外条件规则命中；盘面计算仍然有效。</p>}
            </section>

            <section className="live-section">
              <div className="result-section-heading"><div><span>五</span><h2>典籍依据</h2></div></div>
              {Object.entries(result.evidence).map(([id, raw]) => {
                const evidence = displayEvidence(id, raw);
                return <article className="live-evidence" key={id}>
                  <div><strong>{evidence.title}</strong><span>{evidence.grade}</span></div>
                  <blockquote>{evidence.quote}</blockquote>
                  <small>{id}</small>
                </article>;
              })}
            </section>
          </div>

          {result.warnings.length > 0 && <div className="live-warning">{result.warnings.join("；")}</div>}
          {result.limitations.length > 0 && <div className="live-limit"><strong>当前边界：</strong>{result.limitations.join("；")}</div>}

          <details className="trace-section">
            <summary><span className="trace-icon"><Icon name="layers" size={19} /></span><div><strong>查看推演过程</strong><small>公开计算步骤摘要，默认折叠</small></div><Icon name="chevron" size={18} /></summary>
            <ol>
              {result.trace.map((step, index) => (
                <li key={index}><span>{String(index + 1).padStart(2, "0")}</span>{step.rule_id || step.step || step.operation || JSON.stringify(step)}</li>
              ))}
            </ol>
          </details>

          <div className="ai-quiet-panel live-ai">
            <span className="ai-symbol">释</span>
            <div><h3>AI 深度解读仍关闭</h3><p>这不会影响上面的确定性盘面、规则和 Evidence。等真实模型校准通过后再开放。</p></div>
            <span className="quiet-status">校准中</span>
          </div>
        </section>
      )}
    </div>
  );
}
