import { useRef, useState } from "react";
import type { FormEvent } from "react";
import { Icon } from "../shared/Icon";
import { Link } from "../shared/router";
import { lookupDreamCulture, type DreamCultureResponse } from "./api";
import "./dream-culture.css";

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
            <button type="button" onClick={() => changeDream("我梦见没有被蛇咬，但我梦见我捡到了钱。")}>
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
