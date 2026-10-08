import { useState } from "react";
import type { FormEvent } from "react";
import { runAdminDreamResearch, type AdminDreamResearchResponse } from "./adminApi";
import "./dream-research.css";

export function AdminDreamResearchPage() {
  const [token, setToken] = useState("");
  const [narrative, setNarrative] = useState("");
  const [result, setResult] = useState<AdminDreamResearchResponse | null>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");
    setResult(null);
    if (!token.trim() || narrative.trim().length < 2 || narrative.length > 500) {
      setError("请输入后台令牌与 2—500 字梦境描述。");
      return;
    }
    setLoading(true);
    try {
      const next = await runAdminDreamResearch(token.trim(), narrative.trim());
      setResult(next);
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "研究检索失败。");
    } finally {
      setLoading(false);
    }
  }

  const payload = result?.result;
  const matches = payload?.matched_interpretations || [];
  return (
    <div className="admin-dream-workspace">
      <header className="admin-dream-hero">
        <span>内部工具 · 固定原文 / 文化检索</span>
        <h1>解梦知识检索实验台</h1>
        <p>使用现有已审核梦象与真实 RAG 检索，不生成命理预测，不调用 AI，不开放公众访问。输入结果只显示当前有证据支持的传统文化条目。</p>
      </header>

      <form className="admin-dream-form" onSubmit={submit}>
        <label>
          <span>管理端访问令牌（仅本次请求使用）</span>
          <input aria-label="管理端访问令牌" type="password" autoComplete="off"
            value={token} onChange={(event) => setToken(event.target.value)}
            placeholder="TIANJI_ADMIN_READ_TOKEN" required />
        </label>
        <label>
          <span>梦境叙述</span>
          <textarea aria-label="梦境叙述" rows={5} minLength={2} maxLength={500}
            value={narrative} onChange={(event) => setNarrative(event.target.value)}
            placeholder="例如：我梦见被蛇咬了" required />
        </label>
        <div className="admin-dream-actions">
          <button type="submit" disabled={loading}>
            {loading ? "正在检索已审核资料…" : "检索真实梦象知识"}
          </button>
          <button type="button" onClick={() => { setNarrative(""); setResult(null); setError(""); }}>清空检索</button>
        </div>
        {error && <p role="alert" className="admin-dream-error">{error}</p>}
      </form>

      {!result && <section className="admin-dream-status">
        <h2>检索规则</h2>
        <p>仅匹配固定场景；蛇、水、火等字面提及不等于命中梦义。否定、假设、转述或未知场景将保守弃判。令牌不写入本机存储。</p>
      </section>}

      {result && <section className="admin-dream-results" aria-live="polite">
        <header>
          <h2>检索结果</h2>
          <span>研究模式 · 非个人预测</span>
        </header>
        {matches.length === 0
          ? <p className="admin-dream-empty">没有与叙述严格匹配的已审核梦象。不会生成无依据的解读。</p>
          : matches.map((item) => (
            <article key={item.term_id} className="admin-dream-result">
              <h3>{item.symbol} · {item.scene}</h3>
              <p>{item.interpretation}</p>
              <blockquote>{item.original_text_short_quote}</blockquote>
              <small>Evidence 级别：{item.evidence_level} · {item.evidence_ids.length} 个可追溯来源 · {item.term_id}</small>
            </article>
          ))}
        <details>
          <summary>证据边界及限制</summary>
          <ul>{(payload?.limitations || []).map((rule) => <li key={rule}>{rule}</li>)}</ul>
          <p>本工具不输出整本 RAW/Quarantine 原文，不据文化文本预测健康、财富或婚姻。</p>
        </details>
      </section>}
    </div>
  );
}
