import { useRef, useState } from "react";
import type { FormEvent } from "react";
import { Icon } from "../shared/Icon";
import { Link } from "../shared/router";
import { interpretDream, type DreamInterpretResponse } from "./api";
import "./dream-interpret.css";

// Reviewed scene examples. The sentences are the same vetted examples
// used by the traditional lookup page: each one matches exactly one
// reviewed scene when submitted. Choosing one only fills the input;
// the normal reviewed API call happens after the user submits.
const REVIEWED_EXAMPLES = [
  { label: "蛇咬", symbol: "蛇", glyph: "巳", hint: "被蛇咬住手", example: "我梦见一条蛇咬住我的手" },
  { label: "入水", symbol: "水", glyph: "水", hint: "身处水中自在", example: "我梦见我在水里感到很自在" },
  { label: "火中", symbol: "火", glyph: "火", hint: "自己站在火里", example: "我梦见我站在火里" },
  { label: "飞天", symbol: "飞翔", glyph: "云", hint: "飞向天空", example: "我梦见我飞向天空" },
  { label: "坠井", symbol: "坠落", glyph: "井", hint: "掉进井里", example: "我梦见我掉进井里" },
  { label: "乘龙", symbol: "龙", glyph: "龙", hint: "骑龙进入水中", example: "我梦见我骑着一条龙进入河里" },
  { label: "游鱼", symbol: "鱼", glyph: "鱼", hint: "群鱼游水", example: "我梦见一群鱼在水里游" },
  { label: "新屋", symbol: "房屋", glyph: "舍", hint: "自家房屋翻修", example: "我梦见我家的房子正在翻修" },
  { label: "兄弟", symbol: "家人", glyph: "人", hint: "兄弟相打", example: "我梦见我的两个兄弟在打架" },
  { label: "拾钱", symbol: "钱财", glyph: "财", hint: "捡到钱币", example: "我梦见我捡到了钱" },
] as const;

export function DreamInterpretPage() {
  const [dream, setDream] = useState("");
  const [submittedDream, setSubmittedDream] = useState("");
  const [result, setResult] = useState<DreamInterpretResponse | null>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const requestVersion = useRef(0);
  const textareaRef = useRef<HTMLTextAreaElement | null>(null);

  function changeDream(value: string) {
    requestVersion.current += 1;
    setDream(value);
    setResult(null);
    setError("");
    setLoading(false);
  }

  function clearAll() {
    changeDream("");
    setSubmittedDream("");
    textareaRef.current?.focus();
  }

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const clean = dream.trim();
    if (clean.length < 2 || clean.length > 500) {
      setResult(null);
      setError("请填写 2—500 字的梦境叙述。");
      return;
    }
    const version = ++requestVersion.current;
    setLoading(true);
    setError("");
    setResult(null);
    try {
      const data = await interpretDream(clean);
      if (version === requestVersion.current) {
        setSubmittedDream(clean);
        setResult(data);
      }
    } catch (cause) {
      if (version === requestVersion.current)
        setError(cause instanceof Error ? cause.message : "梦境解读失败，请稍后再试。");
    } finally {
      if (version === requestVersion.current) setLoading(false);
    }
  }

  const matchedSymbols = result ? result.symbols.map((s) => s.symbol) : [];
  const exploreExamples = REVIEWED_EXAMPLES.filter(
    (item) => !matchedSymbols.includes(item.symbol),
  );
  const distinctSources = result
    ? Array.from(new Map(result.symbols.map((s) => [s.source_title, s])).values())
    : [];

  return (
    <div className="dream-interpret-page">
      <div className="breadcrumb">
        <Link href="/">生活场景</Link>
        <Icon name="chevron" size={12} />
        <span>AI 解梦</span>
      </div>

      <section className="dream-interpret-hero">
        <span className="eyebrow">梦境有象 · 典籍可查</span>
        <h1>解读你的梦境</h1>
        <p>从传统梦文化角度探索梦中的意象与象征。以下解读来自已经人工审核的传统梦象条目，逐条附有典籍出处；AI 解读尚未启用，本页不生成 AI 内容，也不预测现实吉凶。</p>
        <span className="dream-interpret-stamp" aria-hidden="true">梦</span>
      </section>

      <section className="dream-interpret-examples" aria-label="常见梦象快捷入口">
        <div className="dream-interpret-examples-head">
          <div>
            <span className="eyebrow">常见梦象 · 一点即填</span>
            <h2>从一个具体梦境开始</h2>
          </div>
          <p>选一项填入描述，点击“解读梦境”才会请求真实知识库；示例本身不是解释。</p>
        </div>
        <div className="dream-interpret-examples-grid">
          {REVIEWED_EXAMPLES.map((item) => (
            <button
              key={item.label}
              type="button"
              className="dream-interpret-example-item"
              aria-label={`填入${item.label}梦境示例`}
              aria-pressed={dream === item.example}
              onClick={() => changeDream(item.example)}
            >
              <span className="dream-interpret-example-glyph" aria-hidden="true">{item.glyph}</span>
              <span className="dream-interpret-example-copy">
                <strong>{item.label}</strong>
                <small>{item.hint}</small>
              </span>
              <span className="dream-interpret-example-arrow" aria-hidden="true">↗</span>
            </button>
          ))}
        </div>
      </section>

      <section className="dream-interpret-layout">
        <form className="dream-interpret-form" onSubmit={submit}>
          <label htmlFor="dream-interpret-narrative">我梦见了……</label>
          <textarea
            id="dream-interpret-narrative"
            ref={textareaRef}
            aria-label="梦境叙述"
            name="dream_text"
            minLength={2}
            maxLength={500}
            required
            rows={6}
            value={dream}
            onChange={(event) => changeDream(event.target.value)}
            placeholder="例如：我梦见被蛇咬了。请尽量描述实际梦见的画面。"
          />
          <div className="dream-interpret-form-bottom">
            <span>{dream.length} / 500 字 · 内容仅用于本次解读，不在本站保存</span>
            <span className="dream-interpret-ai-state" role="status">
              AI 解读：未启用
            </span>
          </div>
          <div className="dream-interpret-actions">
            <button className="button outlined" type="button" onClick={clearAll} disabled={loading || (!dream && !result)}>
              清空
            </button>
            <button className="button primary" type="submit" disabled={loading}>
              {loading ? "正在检索已审核条目…" : "解读梦境"}
              {!loading && <Icon name="arrow" size={16} />}
            </button>
          </div>
          {error && <p role="alert" className="dream-interpret-error">{error}</p>}
        </form>
        <aside className="dream-interpret-aside">
          <span className="eyebrow">解读说明</span>
          <h2>先有证据，再有解释</h2>
          <p>同样是蛇梦，“见蛇”与“被蛇咬”不是同一个场景。否定、转述或不明确的语句不会强行推断。</p>
          <p>传统文本可能含有吉凶措辞，这些都只是历史文化记载，并非对个人未来的判断。</p>
          <p>
            想要逐条查阅典籍原文，可使用
            <Link href="/dream-culture">传统梦象查阅</Link>。
          </p>
        </aside>
      </section>

      {!result && !loading && !error && (
        <section className="dream-interpret-placeholder">
          <strong>解读尚未开始</strong>
          <p>输入梦境后才会向真实知识检索服务发起请求，不使用预制的“万能解梦”。</p>
        </section>
      )}

      {loading && (
        <section className="dream-interpret-loading" aria-live="polite">
          <strong>正在检索已审核条目…</strong>
          <p>只查已经人工审核的传统梦象条目，请稍候。</p>
        </section>
      )}

      {result && (
        <section className="dream-interpret-results" aria-live="polite">
          <div className="dream-interpret-result-head">
            <div>
              <span className="eyebrow">已审核典籍 · 文化参考</span>
              <h2>梦境解读</h2>
            </div>
            <span>{result.symbols.length} 个梦象</span>
          </div>

          <article className="dream-interpret-summary">
            <span className="eyebrow">梦境摘要</span>
            <p>“{submittedDream}”</p>
            {result.symbols.length > 0 && (
              <small>
                识别出 {result.symbols.length} 个有据可查的梦象：
                {result.symbols.map((s) => s.scene).join("、")}。
              </small>
            )}
          </article>

          {result.symbols.length === 0 ? (
            <div className="dream-interpret-empty">
              <h3>暂无可核验的对应条目</h3>
              <p>现有知识库尚未审核与你描述严格匹配的梦境场景，因此不会猜测或编造含义。你可以补充梦中的具体动作，再解读一次，或从下方继续探索其他梦象。</p>
            </div>
          ) : (
            <>
              <div className="dream-interpret-symbols">
                {result.symbols.map((item, index) => (
                  <article key={index} className="dream-interpret-symbol">
                    <span className="dream-interpret-symbol-index">梦象 {String(index + 1).padStart(2, "0")}</span>
                    <h3>{item.symbol} · {item.scene}</h3>
                    {item.matched_texts.length > 0 && (
                      <p className="dream-interpret-input-proof">
                        <strong>对应梦中原话：</strong>{item.matched_texts.join("；")}
                      </p>
                    )}
                    <p>{item.cultural_reading}</p>
                    <blockquote>“{item.short_quote}”</blockquote>
                    <small>出处：{item.source_title || "未标注"} · 审核证据等级 {item.evidence_level} · 传统文化用语</small>
                  </article>
                ))}
              </div>

              <section className="dream-interpret-relations" aria-label="梦象之间的关联">
                <span className="eyebrow">梦象关联</span>
                {result.relations.length > 0 ? (
                  result.relations.map((relation, index) => (
                    <div key={index} className="dream-interpret-relation">
                      <strong>{relation.scenes.join("、")}</strong>
                      <p>{relation.note}</p>
                    </div>
                  ))
                ) : (
                  <p>各梦象分属不同典籍，解释各自独立，不强行建立联系。</p>
                )}
              </section>

              <section className="dream-interpret-sources" aria-label="经典文献与解释依据">
                <span className="eyebrow">经典依据</span>
                <h3>解释所引的典籍</h3>
                <ul>
                  {distinctSources.map((item) => (
                    <li key={item.source_title || item.scene}>
                      <strong>{item.source_title || "未标注"}</strong>
                      <span>“{item.short_quote}”</span>
                      <small>审核证据等级 {item.evidence_level}</small>
                    </li>
                  ))}
                </ul>
              </section>
            </>
          )}

          {result.unreviewed_topics.length > 0 && (
            <aside className="dream-interpret-unreviewed" aria-label="未获审核的梦境主题">
              <h3>有些梦境细节尚无审核解释</h3>
              <p>以下只是您输入中的主题识别，不是古籍解释，也不代表这些事情会发生。</p>
              <ul>
                {result.unreviewed_topics.map((topic) => (
                  <li key={topic.label}>
                    <strong>{topic.label}</strong>
                    <span>{topic.matched_texts.join("；")}</span>
                    <small>尚无严格对应的已审核条目</small>
                  </li>
                ))}
              </ul>
            </aside>
          )}

          <section className="dream-interpret-ai" aria-label="AI 解读状态">
            <span className="eyebrow">AI 解读</span>
            <h3>未启用</h3>
            <p>{result.ai_interpretation.message}</p>
          </section>

          <section className="dream-interpret-boundaries" aria-label="解释边界">
            <span className="eyebrow">解释边界</span>
            <h3>需要注意的限制</h3>
            <ul>
              {result.boundaries.map((line, index) => (
                <li key={index}>{line}</li>
              ))}
            </ul>
            <p className="dream-interpret-notice">文化限界：{result.notice}</p>
          </section>

          {exploreExamples.length > 0 && (
            <section className="dream-interpret-explore" aria-label="继续探索相关梦象">
              <span className="eyebrow">继续探索</span>
              <h3>看看其他梦象</h3>
              <div className="dream-interpret-examples-grid">
                {exploreExamples.map((item) => (
                  <button
                    key={item.label}
                    type="button"
                    className="dream-interpret-example-item"
                    aria-label={`填入${item.label}梦境示例`}
                    onClick={() => changeDream(item.example)}
                  >
                    <span className="dream-interpret-example-glyph" aria-hidden="true">{item.glyph}</span>
                    <span className="dream-interpret-example-copy">
                      <strong>{item.label}</strong>
                      <small>{item.hint}</small>
                    </span>
                    <span className="dream-interpret-example-arrow" aria-hidden="true">↗</span>
                  </button>
                ))}
              </div>
              <p>选一项填入上方输入框，再点“解读梦境”。</p>
            </section>
          )}

          <div className="dream-interpret-again">
            <button className="button outlined" type="button" onClick={clearAll}>
              再解一梦
            </button>
          </div>
        </section>
      )}
    </div>
  );
}
