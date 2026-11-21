import { useState } from "react";
import type { FormEvent } from "react";
import {
  runAdminDreamAiExplain,
  runAdminDreamResearch,
  saveDreamReviewDraft,
  type AdminDreamAiExplainResponse,
  type AdminDreamResearchResponse,
} from "./adminApi";
import "./dream-research.css";

/** Research-draft verdict labels. A refusal never also shows claims. */
const VERDICT_LABELS: Record<string, string> = {
  explained: "已生成研究草稿",
  abstained_no_reviewed_interpretation: "无已审核解读，已弃判",
  not_configured: "未配置模型提供方，未调用模型",
  provider_timeout: "模型调用超时，已拒判",
  provider_rate_limited: "模型调用受限（429），已拒判",
  provider_failed: "模型调用失败，已拒判",
  invalid_model_response: "模型回复不符合契约，已拒判",
  citation_rejected: "模型引用未通过证据校验，已拒判",
  diagnosis_rejected: "模型回复含诊断内容，已拒判",
  prediction_rejected: "模型回复含个人预测，已拒判",
  context_rejected: "上下文未通过安全检查，已拒判",
};

export function AdminDreamResearchPage() {
  const [token, setToken] = useState("");
  const [narrative, setNarrative] = useState("");
  const [result, setResult] = useState<AdminDreamResearchResponse | null>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [aiResult, setAiResult] = useState<AdminDreamAiExplainResponse | null>(null);
  const [aiError, setAiError] = useState("");
  const [aiLoading, setAiLoading] = useState(false);
  const [roleToken, setRoleToken] = useState("");
  const [draftId, setDraftId] = useState("");
  const [draftError, setDraftError] = useState("");
  const [draftSaving, setDraftSaving] = useState(false);

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

  async function explainWithAi() {
    setAiError("");
    setAiResult(null);
    if (!token.trim() || narrative.trim().length < 2 || narrative.length > 500) {
      setAiError("请输入后台令牌与 2—500 字梦境描述。");
      return;
    }
    setAiLoading(true);
    try {
      const next = await runAdminDreamAiExplain(token.trim(), narrative.trim());
      setAiResult(next);
    } catch (cause) {
      setAiError(cause instanceof Error ? cause.message : "AI 解释失败。");
    } finally {
      setAiLoading(false);
    }
  }

  async function saveAsReviewDraft() {
    setDraftError("");
    setDraftId("");
    if (!aiPayload || aiPayload.verdict !== "explained") {
      setDraftError("只有已生成的解释草稿可以进入人工审核，拒判结果不能保存。");
      return;
    }
    if (!roleToken.trim()) {
      setDraftError("请输入角色令牌（编辑及以上角色）以保存审核草稿。");
      return;
    }
    setDraftSaving(true);
    try {
      const saved = await saveDreamReviewDraft(roleToken.trim(), aiPayload);
      setDraftId(saved.draft.id);
    } catch (cause) {
      setDraftError(cause instanceof Error ? cause.message : "保存审核草稿失败。");
    } finally {
      setDraftSaving(false);
    }
  }

  const payload = result?.result;
  const matches = payload?.matched_interpretations || [];
  const aiPayload = aiResult?.result;
  return (
    <div className="admin-dream-workspace">
      <header className="admin-dream-hero">
        <span>内部工具 · 固定原文 / 文化检索</span>
        <h1>解梦知识检索实验台</h1>
        <p>使用现有已审核梦象与真实 RAG 检索，不生成命理预测，不开放公众访问。检索本身不调用 AI；「AI 解释」是显式的独立研究动作，仅生成待人工审核的草稿，证据不足或模型异常时拒判。输入结果只显示当前有证据支持的传统文化条目。</p>
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
          <button type="button" onClick={explainWithAi} disabled={aiLoading}>
            {aiLoading ? "正在生成研究草稿…" : "AI 解释（研究草稿）"}
          </button>
          <button type="button" onClick={() => { setNarrative(""); setResult(null); setError(""); setAiResult(null); setAiError(""); }}>清空检索</button>
        </div>
        {error && <p role="alert" className="admin-dream-error">{error}</p>}
        {aiError && <p role="alert" className="admin-dream-error">{aiError}</p>}
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

      {aiPayload && <section className="admin-dream-results" aria-live="polite">
        <header>
          <h2>AI 解释 · 研究草稿</h2>
          <span className="admin-dream-verdict">{VERDICT_LABELS[aiPayload.verdict] || aiPayload.verdict}</span>
        </header>
        {aiPayload.verdict === "explained" ? (
          aiPayload.claims.map((claim, index) => (
            <article key={index} className="admin-dream-result">
              <p>{claim.text}</p>
              {claim.quotes.map((quote) => (
                <blockquote key={quote.evidence_id}>{quote.text}</blockquote>
              ))}
              <small>{claim.citations.map((citation) => {
                const ref = citation.source_ref as Record<string, unknown>;
                const title = typeof ref.classic_title === "string" ? ref.classic_title : "";
                const locator = typeof ref.locator === "string" ? ref.locator : "";
                return `${title} ${locator}`.trim();
              }).join("；")} · {claim.evidence_ids.length} 个可追溯来源</small>
            </article>
          ))
        ) : (
          <p className="admin-dream-refusal">未生成解释：{VERDICT_LABELS[aiPayload.verdict] || aiPayload.verdict}{aiPayload.reason ? `（${aiPayload.reason}）` : ""}不会返回无依据的解读。</p>
        )}
        {aiPayload.verdict === "explained" && (
          <div className="admin-dream-review-save">
            <label>
              <span>角色令牌（编辑及以上，用于保存审核草稿，仅本次使用）</span>
              <input aria-label="角色令牌" type="password" autoComplete="off"
                value={roleToken} onChange={(event) => setRoleToken(event.target.value)}
                placeholder="TIANJI_ADMIN_ROLE_TOKENS 中的令牌" />
            </label>
            <button type="button" onClick={saveAsReviewDraft} disabled={draftSaving}>
              {draftSaving ? "正在保存审核草稿…" : "保存为审核草稿"}
            </button>
            {draftId && <p role="status">已保存为审核草稿：{draftId}。请前往“解梦审核”页面提交审核。</p>}
            {draftError && <p role="alert" className="admin-dream-error">{draftError}</p>}
          </div>
        )}
        <details>
          <summary>解释边界及限制</summary>
          <ul>{(aiPayload.limitations || []).map((rule) => <li key={rule}>{rule}</li>)}</ul>
          <p>本草稿仅供人工审核（TJ-028.3），不是公开答案，不作个人预测；公开 AI 仍处于关闭状态。</p>
        </details>
      </section>}
    </div>
  );
}
