import { useState } from "react";
import {
  actOnAdminDraft,
  listAdminDrafts,
  parseDreamReviewResult,
  rollbackAdminDraft,
  type AdminDraft,
  type AdminDraftAction,
} from "./adminApi";
import "./drafts.css";
import "./dream-research.css";

const STATUS_LABELS: Record<AdminDraft["status"], string> = {
  draft: "草稿",
  submitted: "已提交",
  approved: "已批准",
  rejected: "已驳回",
  published: "已发布",
};

const ACTION_LABELS: Record<AdminDraftAction, string> = {
  submit: "提交审核",
  approve: "批准",
  reject: "驳回",
  publish: "发布",
};

function actionsFor(status: AdminDraft["status"]): AdminDraftAction[] {
  if (status === "draft") return ["submit"];
  if (status === "submitted") return ["approve", "reject"];
  if (status === "approved") return ["publish"];
  return [];
}

/**
 * TJ-028.3: human review for AI dream research drafts. The drafts
 * themselves are ordinary drafts in the existing store (same state
 * machine, roles, audit log, SQLite persistence); this page only
 * shows the dream-kind ones and renders their embedded result
 * (dream text, elements, claims, verbatim quotes, citation sources)
 * plus the review trail (who/when/reason/version).
 *
 * Rules enforced server-side and reflected here: approve/reject need
 * a human reason; approve/publish re-validate the embedded evidence
 * (a corrupted body can be rejected but never approved or published);
 * editing is only legal in 'draft' status, so modified content must
 * pass review again; publishing marks the research draft published
 * and never enables public AI.
 */
export function AdminDreamReviewPage() {
  const [roleToken, setRoleToken] = useState("");
  const [drafts, setDrafts] = useState<AdminDraft[] | null>(null);
  const [storageNote, setStorageNote] = useState("");
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [busy, setBusy] = useState(false);
  const [detail, setDetail] = useState<AdminDraft | null>(null);
  const [reason, setReason] = useState("");
  const [rollbackVersion, setRollbackVersion] = useState("");

  function requireToken(): string | null {
    if (!roleToken.trim()) {
      setError("请输入角色令牌。");
      return null;
    }
    return roleToken;
  }

  async function refresh(token: string) {
    const list = await listAdminDrafts(token);
    // A draft is a dream review draft when its server-persisted
    // marker says so, even if its editable body was tampered with
    // (kind removed / plain text / other kind): it stays visible
    // here so a reviewer can roll it back, and the server still
    // refuses to approve or publish it.
    setDrafts(
      list.drafts.filter(
        (draft) => draft.review_kind === "dream_ai" || parseDreamReviewResult(draft) !== null,
      ),
    );
    setStorageNote(list.storage_note);
  }

  async function load() {
    const token = requireToken();
    if (!token) return;
    setError("");
    setNotice("");
    setBusy(true);
    try {
      await refresh(token);
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "加载审核草稿失败。");
    } finally {
      setBusy(false);
    }
  }

  async function act(draft: AdminDraft, action: AdminDraftAction) {
    const token = requireToken();
    if (!token) return;
    if ((action === "approve" || action === "reject") && !reason.trim()) {
      setError("批准或驳回需要填写审核原因。");
      return;
    }
    setError("");
    setNotice("");
    setBusy(true);
    try {
      const updated = await actOnAdminDraft(
        token,
        draft.id,
        action,
        action === "approve" || action === "reject" ? reason.trim() : undefined,
      );
      setDetail(updated.draft);
      setReason("");
      setNotice(`${draft.id} 已${ACTION_LABELS[action]}。`);
      await refresh(token);
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "审核操作失败。");
    } finally {
      setBusy(false);
    }
  }

  async function rollback(draft: AdminDraft) {
    const token = requireToken();
    if (!token) return;
    const version = Number(rollbackVersion);
    if (!Number.isInteger(version) || version < 1) {
      setError("请选择要回滚到的版本号。");
      return;
    }
    setError("");
    setNotice("");
    setBusy(true);
    try {
      const updated = await rollbackAdminDraft(token, draft.id, version);
      setDetail(updated.draft);
      setRollbackVersion("");
      setNotice(`${draft.id} 已回滚到版本 ${version}，需重新审核。`);
      await refresh(token);
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "回滚失败。");
    } finally {
      setBusy(false);
    }
  }

  const selected = detail ? parseDreamReviewResult(detail) : null;

  return (
    <div>
      <h1 className="admin-page-heading">解梦审核</h1>
      <p className="drafts-notice-text">
        人工审核 AI 解梦研究草稿：查看梦境、已审梦象、逐字引文与证据来源，批准、驳回或发布。
        未审核的草稿不得发布；拒判、证据不完整或引用无效的结果不能进入审核流程。
        发布仅标记研究草稿已发布，公开 AI 仍处于关闭状态。
      </p>

      <label>
        <span>角色令牌（仅本次使用，不写入存储）</span>
        <input
          aria-label="角色令牌"
          type="password"
          autoComplete="off"
          value={roleToken}
          onChange={(event) => setRoleToken(event.target.value)}
          placeholder="TIANJI_ADMIN_ROLE_TOKENS 中的令牌"
        />
      </label>
      <div>
        <button type="button" className="admin-button" onClick={load} disabled={busy}>
          {busy ? "加载中…" : "加载审核草稿"}
        </button>
      </div>
      {storageNote && <p className="drafts-storage-note">{storageNote}</p>}
      {error && <p role="alert" className="drafts-error">{error}</p>}
      {notice && <p role="status">{notice}</p>}

      {drafts !== null && (
        <section className="drafts-list" aria-label="解梦审核草稿列表">
          {drafts.length === 0 ? (
            <p>暂无解梦审核草稿。请先在“解梦知识研究”页生成解释并保存为审核草稿。</p>
          ) : (
            drafts.map((draft) => (
              <article key={draft.id} className="admin-draft-item">
                <div className="drafts-item-head">
                  <span className="drafts-item-title">{draft.title}</span>
                  <span className="admin-status">{STATUS_LABELS[draft.status]}</span>
                </div>
                <p className="drafts-item-meta">
                  {draft.id} · 创建者 {draft.author_role} · 版本 {draft.versions.length} · 更新于 {draft.updated_at}
                </p>
                <div className="drafts-item-actions">
                  <button
                    type="button"
                    className="admin-button"
                    onClick={() => {
                      setDetail(draft);
                      setError("");
                      setNotice("");
                    }}
                  >
                    查看与审核
                  </button>
                </div>
              </article>
            ))
          )}
        </section>
      )}

      {detail && (
        <section className="admin-card" aria-label="审核草稿详情">
          <h2>{detail.title}</h2>
          <p className="drafts-item-meta">
            {detail.id} · 状态 {STATUS_LABELS[detail.status]} · 版本 {detail.versions.length}
          </p>
          {selected ? (
          <div className="admin-dream-results">
            <p><strong>梦境叙述：</strong>{selected.dream_text}</p>
            {selected.elements.map((element) => (
              <article key={element.term_id} className="admin-dream-result">
                <h3>{element.symbol} · {element.scene}</h3>
                <p>{element.interpretation}</p>
                <blockquote>{element.original_text_short_quote}</blockquote>
                <small>{element.source} · {element.term_id} · {element.evidence_ids.length} 个可追溯来源</small>
              </article>
            ))}
            {selected.claims.map((claim, index) => (
              <article key={index} className="admin-dream-result">
                <p>{claim.text}</p>
                {claim.quotes.map((quote) => (
                  <blockquote key={quote.evidence_id}>{quote.text}</blockquote>
                ))}
                <small>
                  {claim.citations
                    .map((citation) => {
                      const ref = citation.source_ref as Record<string, unknown>;
                      const title = typeof ref.classic_title === "string" ? ref.classic_title : "";
                      const locator = typeof ref.locator === "string" ? ref.locator : "";
                      return `${title} ${locator}`.trim();
                    })
                    .join("；")}
                  {" · "}
                  {claim.evidence_ids.length} 个可追溯来源
                </small>
              </article>
            ))}
            <details>
              <summary>解释边界及限制</summary>
              <ul>{(selected.limitations || []).map((rule) => <li key={rule}>{rule}</li>)}</ul>
              <p>本草稿仅供人工审核（TJ-028.3），不是公开答案，不作个人预测；公开 AI 仍处于关闭状态。</p>
            </details>
          </div>
          ) : (
            <p role="alert" className="drafts-error">
              草稿正文已损坏或不再是解梦审核正文，无法批准或发布；可回滚到更早的版本恢复。
            </p>
          )}

          <h3>审核记录</h3>
          <ul className="drafts-transitions">
            {detail.transitions.map((transition, index) => (
              <li key={index}>
                {transition.action} · {transition.role} · {transition.at}
                {transition.reason ? ` · 原因：${transition.reason}` : ""}
                {transition.version !== undefined ? ` · 版本 ${transition.version}` : ""}
              </li>
            ))}
          </ul>
          <h3>版本快照</h3>
          <ul className="drafts-versions">
            {detail.versions.map((version) => (
              <li key={version.version}>
                版本 {version.version} · {version.action} · {version.role} · {version.at}
              </li>
            ))}
          </ul>

          {actionsFor(detail.status).length > 0 && (
            <div className="drafts-edit-form">
              <label>
                <span>审核原因（批准/驳回必填，最多 500 字）</span>
                <input
                  aria-label="审核原因"
                  type="text"
                  value={reason}
                  onChange={(event) => setReason(event.target.value)}
                  placeholder="例如：证据链完整，通过。"
                  maxLength={500}
                />
              </label>
              <div className="drafts-item-actions">
                {actionsFor(detail.status).map((action) => (
                  <button
                    key={action}
                    type="button"
                    className="admin-button"
                    onClick={() => act(detail, action)}
                    disabled={busy}
                  >
                    {ACTION_LABELS[action]}
                  </button>
                ))}
              </div>
            </div>
          )}

          {detail.status !== "rejected" && detail.versions.length > 0 && (
            <div className="drafts-edit-form">
              <label>
                <span>回滚到版本（仅发布者；回滚后需重新审核）</span>
                <select
                  aria-label="回滚版本"
                  value={rollbackVersion}
                  onChange={(event) => setRollbackVersion(event.target.value)}
                >
                  <option value="">选择版本</option>
                  {detail.versions.map((version) => (
                    <option key={version.version} value={version.version}>
                      版本 {version.version}（{version.action}）
                    </option>
                  ))}
                </select>
              </label>
              <button
                type="button"
                className="admin-button"
                onClick={() => rollback(detail)}
                disabled={busy}
              >
                回滚
              </button>
            </div>
          )}
          {detail.status === "rejected" && <p>已驳回的草稿为终态，不能再回滚或发布。</p>}
        </section>
      )}
    </div>
  );
}
