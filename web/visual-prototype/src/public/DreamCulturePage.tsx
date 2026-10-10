import { useRef, useState } from "react";
import type { FormEvent } from "react";
import { Icon } from "../shared/Icon";
import { Link } from "../shared/router";
import { lookupDreamCulture, type DreamCultureResponse } from "./api";
import "./dream-culture.css";

// Public examples contain only simple dream descriptions, not private source
// records. The button must never return a canned interpretation: the normal
// reviewed API lookup is required after the user chooses to submit.
const REVIEWED_SCENE_EXAMPLES = [
  { label: "蛇咬", glyph: "巳", hint: "被蛇咬住手", example: "我梦见一条蛇咬住我的手" },
  { label: "入水", glyph: "水", hint: "身处水中自在", example: "我梦见我在水里感到很自在" },
  { label: "火中", glyph: "火", hint: "自己站在火里", example: "我梦见我站在火里" },
  { label: "飞天", glyph: "云", hint: "飞向天空", example: "我梦见我飞向天空" },
  { label: "坠井", glyph: "井", hint: "掉进井里", example: "我梦见我掉进井里" },
  { label: "乘龙", glyph: "龙", hint: "骑龙进入水中", example: "我梦见我骑着一条龙进入河里" },
  { label: "游鱼", glyph: "鱼", hint: "群鱼游水", example: "我梦见一群鱼在水里游" },
  { label: "新屋", glyph: "舍", hint: "自家房屋翻修", example: "我梦见我家的房子正在翻修" },
  { label: "兄弟", glyph: "人", hint: "兄弟相打", example: "我梦见我的两个兄弟在打架" },
  { label: "拾钱", glyph: "财", hint: "捡到钱币", example: "我梦见我捡到了钱" },
] as const;

export function DreamCulturePage() {
  const [dream, setDream] = useState("");
  const [result, setResult] = useState<DreamCultureResponse | null>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const requestVersion = useRef(0);

  function changeDream(value: string) {
    requestVersion.current += 1;
    setDream(value);
    setResult(null);
    setError("");
    setLoading(false);
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
      const data = await lookupDreamCulture(clean);
      if (version === requestVersion.current) setResult(data);
    } catch (cause) {
      if (version === requestVersion.current)
        setError(cause instanceof Error ? cause.message : "梦象查阅失败。");
    } finally {
      if (version === requestVersion.current) setLoading(false);
    }
  }

  return (
    <div className="dream-culture-page">
      <div className="breadcrumb">
        <Link href="/">生活场景</Link>
        <Icon name="chevron" size={12} />
        <span>传统梦象查阅</span>
      </div>
      <section className="dream-culture-hero">
        <span className="eyebrow">梦境有象 · 典籍可查</span>
        <h1>昨夜一梦，古书如何记载？</h1>
        <p>写下你记得的梦境细节，我们仅检索已经人工审核的传统梦象条目。这里呈现的是古代文化中的象征说法，不是预测，也不是心理或医学诊断。</p>
        <span className="dream-culture-stamp" aria-hidden="true">梦</span>
      </section>

      <section className="dream-culture-library" aria-label="已审核梦象示例">
        <div className="dream-culture-library-head">
          <div>
            <span className="eyebrow">十种有据可查的梦境表达</span>
            <h2>循象入梦 · 从具体场景开始</h2>
          </div>
          <p>这些只是检索示例，不是梦境预言。选一项可填入描述，点击“查阅梦象”才会请求真实知识库。</p>
        </div>
        <div className="dream-culture-library-grid">
          {REVIEWED_SCENE_EXAMPLES.map((item) => (
            <button
              key={item.label}
              type="button"
              className="dream-culture-library-item"
              aria-label={`填入${item.label}梦境示例`}
              aria-pressed={dream === item.example}
              onClick={() => changeDream(item.example)}
            >
              <span className="dream-culture-library-glyph" aria-hidden="true">{item.glyph}</span>
              <span className="dream-culture-library-copy">
                <strong>{item.label}</strong>
                <small>{item.hint}</small>
              </span>
              <span className="dream-culture-library-arrow" aria-hidden="true">↗</span>
            </button>
          ))}
        </div>
        <p className="dream-culture-library-foot">同一动物或物品的不同动作，未必对应相同古籍条目；只匹配审核过的具体场景。</p>
      </section>

      <section className="dream-culture-layout">
        <form className="dream-culture-form" onSubmit={submit}>
          <label htmlFor="dream-narrative">我梦见了……</label>
          <textarea
            id="dream-narrative"
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
          <div className="dream-culture-example">
            <span>不知道怎么写？试试带有否定与新梦象的真实检索示例。</span>
            <button type="button" onClick={() => changeDream("我梦见没有被蛇咬但我梦见我捡到了钱。")}>
              填入多场景示例
            </button>
          </div>
          <div className="dream-culture-form-bottom">
            <span>{dream.length} / 500 字 · 内容仅用于本次查阅，不在本站保存</span>
            <button className="button primary" type="submit" disabled={loading}>
              {loading ? "正在查阅审核条目…" : "查阅梦象"}
              {!loading && <Icon name="arrow" size={16} />}
            </button>
          </div>
          {error && <p role="alert" className="dream-culture-error">{error}</p>}
        </form>
        <aside className="dream-culture-aside">
          <span className="eyebrow">查阅边界</span>
          <h2>有证据才有解释</h2>
          <p>同样是蛇梦，“见蛇”与“被蛇咬”不是同一个场景。否定、转述或不明确的语句不会强行推断。</p>
          <p>传统文本可能含有吉凶措辞，这些都只是历史文化记载，并非对个人未来的判断。</p>
        </aside>
      </section>

      {!result && !loading && !error && <section className="dream-culture-placeholder">
        <strong>检索尚未开始</strong>
        <p>输入梦境后才会向真实知识检索服务发起请求，不使用预制的“万能解梦”。</p>
      </section>}

      {result && <section className="dream-culture-results" aria-live="polite">
        <div className="dream-culture-result-head">
          <div>
            <span className="eyebrow">已审核典籍 · 文化参考</span>
            <h2>梦象查阅结果</h2>
          </div>
          <span>{result.matches.length} 条命中</span>
        </div>
        {result.matches.length === 0 ? (
          <div className="dream-culture-empty">
            <h3>暂无可核验的对应条目</h3>
            <p>现有知识库尚未审核与你描述严格匹配的梦境场景，因此不会猜测或编造含义。你可以补充梦中的具体动作，再查阅一次。</p>
          </div>
        ) : result.matches.map((item, index) => (
          <article key={index} className="dream-culture-match">
            <span className="dream-culture-match-index">梦象 {String(index + 1).padStart(2, "0")}</span>
            <h3>{item.scene}</h3>
            {item.matched_texts?.length > 0 && (
              <p className="dream-culture-input-proof">
                <strong>对应梦中原话：</strong>{item.matched_texts.join("；")}
              </p>
            )}
            <p>{item.cultural_reading}</p>
            <blockquote>“{item.short_quote}”</blockquote>
            <small>{item.source_title} · 审核证据等级 {item.evidence_level} · 传统文化用语</small>
          </article>
        ))}
        <p className="dream-culture-notice">{result.notice}</p>
      </section>}
    </div>
  );
}
