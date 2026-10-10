import { useEffect, useMemo, useRef, useState } from "react";
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

type CoinCast = { faces: [2 | 3, 2 | 3, 2 | 3]; value: number };

function castThreeCoins(): CoinCast {
  const bytes = new Uint8Array(3);
  crypto.getRandomValues(bytes);
  const faces = bytes.map((value) => (value & 1 ? 3 : 2)) as unknown as [2 | 3, 2 | 3, 2 | 3];
  return { faces, value: faces[0] + faces[1] + faces[2] };
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
  const [yaoValues, setYaoValues] = useState<Array<number | null>>([null, null, null, null, null, null]);
  const [coinHistory, setCoinHistory] = useState<Array<CoinCast | null>>([null, null, null, null, null, null]);
  const [result, setResult] = useState<ExecuteResponse | null>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const requestVersion = useRef(0);
  const completed = yaoValues.filter((value) => value !== null).length;
  const nextLine = yaoValues.findIndex((value) => value === null);

  useEffect(() => () => { requestVersion.current += 1; }, []);

  function invalidateResult() {
    requestVersion.current += 1;
    setResult(null);
    setError("");
    setLoading(false);
  }

  function castNext() {
    if (nextLine === -1) return;
    const cast = castThreeCoins();
    const values = [...yaoValues];
    const history = [...coinHistory];
    values[nextLine] = cast.value;
    history[nextLine] = cast;
    setYaoValues(values);
    setCoinHistory(history);
    invalidateResult();
  }

  function randomCast() {
    const casts = Array.from({ length: 6 }, castThreeCoins);
    setYaoValues(casts.map((cast) => cast.value));
    setCoinHistory(casts);
    invalidateResult();
  }

  function resetCasting() {
    setYaoValues([null, null, null, null, null, null]);
    setCoinHistory([null, null, null, null, null, null]);
    invalidateResult();
  }

  function selectYao(index: number, raw: string) {
    const next = [...yaoValues];
    const history = [...coinHistory];
    next[index] = raw === "" ? null : Number(raw);
    history[index] = null;
    setYaoValues(next);
    setCoinHistory(history);
    invalidateResult();
  }

  async function submit(event: FormEvent) {
    event.preventDefault();
    if (question.trim().length < 2) {
      setError("请先写清楚想问的事情（至少两个字）。");
      return;
    }
    if (yaoValues.length !== 6 || yaoValues.some((value) => value === null || ![6, 7, 8, 9].includes(value))) {
      setError("请先完成六次起卦，或逐爻录入六个有效结果。");
      return;
    }
    const version = ++requestVersion.current;
    setError("");
    setLoading(true);
    setResult(null);
    try {
      const value = `${date}T${time}:00+08:00`;
      const response = await executeLiuyao({ value, yao_values: yaoValues as number[] });
      if (version === requestVersion.current) setResult(response);
    } catch (err) {
      if (version === requestVersion.current)
        setError(err instanceof Error ? err.message : "排盘请求失败，请检查后端服务。");
    } finally {
      if (version === requestVersion.current) setLoading(false);
    }
  }

  const chart = result?.chart || {};
  const original = chart.original || {};
  const changed = chart.changed || {};
  const palace = chart.palace || {};
  const classic = chart.zhouyi_classic;
  const movingTexts: Array<{ line: number; position: string; text: string }> =
    Array.isArray(classic?.original?.moving_line_texts) ? classic.original.moving_line_texts : [];
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
          <p>先写下这一件事，再从初爻到上爻掷六次铜钱。系统只把六次实际起卦结果交给已审核的六爻引擎，生成本卦、变卦和经典依据；不预设答案。</p>
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
              onChange={(e) => { invalidateResult(); setQuestion(e.target.value); }}
              placeholder="例如：现在这个工作机会，我是否适合继续推进？"
              maxLength={180}
              minLength={2}
              required
            />
            <small>问题用于当前页面阅读，不发送给排盘引擎；排盘只使用起卦时间与六爻值。</small>
          </label>
          <div className="question-time-grid">
            <label className="question-field">
              <span>起卦日期</span>
              <input type="date" value={date} onChange={(e) => { invalidateResult(); setDate(e.target.value); }} required />
            </label>
            <label className="question-field">
              <span>起卦时间</span>
              <input type="time" value={time} onChange={(e) => { invalidateResult(); setTime(e.target.value); }} required />
            </label>
          </div>
          <p className="question-zone">固定口径：北京时间（UTC+8）</p>
        </section>

        <section className="question-form-card">
          <div className="question-card-title">
            <div className="result-section-heading">
              <div><span>二</span><h2>亲手完成六次起卦</h2></div>
            </div>
          </div>
          <p className="question-help">三枚铜钱法：每枚随机取 2 或 3，三枚相加得到 6、7、8 或 9。六次从下向上，先初爻后上爻。也可直接录入真实投币结果。</p>
          <div className="coin-casting" aria-label="六次铜钱起卦">
            <div className="coin-casting-progress">
              <strong>已完成 {completed} / 6 爻</strong>
              <div role="progressbar" aria-label="起卦进度" aria-valuemin={0} aria-valuemax={6} aria-valuenow={completed}>
                <span style={{ width: `${completed / 6 * 100}%` }} />
              </div>
              <small>{nextLine === -1 ? "六爻已齐，可以查看真实排盘。" : `下一次：${labels[nextLine]}`}</small>
            </div>
            <div className="coin-casting-actions">
              <button className="button primary" type="button" onClick={castNext} disabled={nextLine === -1}>
                {nextLine === -1 ? "六次起卦已完成" : `掷第 ${nextLine + 1} 次铜钱 · ${labels[nextLine]}`}
              </button>
              <button className="button outlined compact-button" type="button" onClick={randomCast}>一次投完六次</button>
              <button className="button outlined compact-button" type="button" onClick={resetCasting} disabled={completed === 0}>重新起卦</button>
            </div>
          </div>
          <div className="yao-input-list">
            {yaoValues.map((value, index) => (
              <label key={index} className={value === 6 || value === 9 ? "is-moving" : ""}>
                <span className="yao-order">{labels[index]}</span>
                <span className={"mini-yao " + (value === 7 || value === 9 ? "yang" : value === null ? "unset" : "yin")}>
                  <i /><i />
                </span>
                <div className="yao-cast-value">
                  <select
                    aria-label={`${labels[index]}结果`}
                    value={value ?? ""}
                    onChange={(e) => selectYao(index, e.target.value)}
                  >
                    <option value="">未起卦</option>
                    {[6, 7, 8, 9].map((item) => <option key={item} value={item}>{item} · {yaoText[item]}</option>)}
                  </select>
                  {coinHistory[index] && (
                    <small>铜钱：{coinHistory[index]!.faces.join(" + ")} = {coinHistory[index]!.value}</small>
                  )}
                </div>
              </label>
            ))}
          </div>
          <button className="button primary question-submit" disabled={loading || completed !== 6 || question.trim().length < 2} type="submit">
            {loading ? "正在排盘…" : "开始推演"}
            {!loading && <Icon name="arrow" size={18} />}
          </button>
          {completed !== 6 && <p className="question-help">六爻未完成：还差 {6 - completed} 爻，完成后才能进行排盘。</p>}
          {error && <div className="question-error" role="alert">{error}</div>}
        </section>
      </form>

      {!result && !loading && (
        <section className="question-empty">
          <span>问</span>
          <div>
            <h2>先写问题，再亲手起六爻</h2>
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

          {classic?.scope === "verbatim_classical_excerpts_only" && (
            <section className="question-classical-report" aria-label="本卦与动爻周易原典">
              <header>
                <span className="eyebrow">真实命盘 × 审核原典</span>
                <h3>本次起出的卦，《周易》原文怎么说？</h3>
                <small>{classic.title} · {classic.source_level} · 原典查阅</small>
              </header>
              <div className="question-classic-grid">
                <article>
                  <span>本卦 · 第 {classic.original.number} 卦</span>
                  <h4>{classic.original.name}</h4>
                  <strong>卦辞</strong>
                  <blockquote>{classic.original.judgment}</blockquote>
                  <strong>象辞</strong>
                  <blockquote>{classic.original.image}</blockquote>
                </article>
                <article>
                  <span>变卦 · 第 {classic.changed.number} 卦</span>
                  <h4>{classic.changed.name}</h4>
                  <strong>卦辞</strong>
                  <blockquote>{classic.changed.judgment}</blockquote>
                  <small>变卦由此次动爻翻转计算，不代表未来事件已经注定。</small>
                </article>
              </div>
              <section className="question-moving-classics">
                <h4>本次动爻原文 · {movingTexts.length} 爻</h4>
                {movingTexts.length ? movingTexts.map((item) => (
                  <blockquote key={item.line}>
                    <strong>{labels[item.line - 1]} · {item.position}</strong>
                    <p>{item.text}</p>
                  </blockquote>
                )) : <p>本次六爻均为静爻，无动爻原文需要单独摘录；仍可查阅本卦卦辞与象辞。</p>}
              </section>
              <p className="question-classical-limit">这些文字是经过收录的传世古籍原文，并不是针对你所提问题的吉凶判断。完整的用神、旺衰、应期与个人解释仍需进一步审核。</p>
            </section>
          )}

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
