import { useState } from "react";
import type { FormEvent } from "react";
import {
  actOnAdminDraft,
  createAdminDraft,
  editAdminDraft,
  listAdminDrafts,
  type AdminDraft,
  type AdminDraftAction,
} from "./adminApi";
import { Drawer } from "./Drawer";
import "./drawer.css";
import "./drafts.css";

const STATUS_LABELS: Record<AdminDraft["status"], string> = {
  draft: "草稿",
  submitted: "已提交",
  approved: "已批准",
  rejected: "已驳回",
  published: "已发布",
};

const ACTION_LABELS: Record<AdminDraftAction, string> = {
  submit: "提交",
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
 * TJ-026.4 batch 2: draft approval flow (create/edit + submit +
 * approve/reject + publish). Role matrix (batch 1): user 全拒，
 * editor 仅草稿，reviewer 批准/驳回，publisher 发布 — enforced
 * server-side; this page only renders the server's 401/403/422
 * answers through the reused TJ-026.3 branching. The role token is
 * component state only (never persisted). Drafts live in process
 * memory: the restart-loss notice below is part of the page, not
 * fine print. Draft detail reuses the B020 Drawer component.
 */
export function AdminDraftsPage() {
  const [roleToken, setRoleToken] = useState("");
  const [drafts, setDrafts] = useState<AdminDraft[] | null>(null);
  const [storageNote, setStorageNote] = useState("");
  const [title, setTitle] = useState("");
  const [body, setBody] = useState("");
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [busy, setBusy] = useState(false);
  const [detail, setDetail] = useState<AdminDraft | null>(null);
  const [editing, setEditing] = useState<AdminDraft | null>(null);
  const [editTitle, setEditTitle] = useState("");
  const [editBody, setEditBody] = useState("");

  function requireToken(): string | null {
    if (!roleToken.trim()) {
      setError("请输入角色令牌。");
      return null;
    }
    return roleToken;
  }

  async function refresh(token: string) {
    const list = await listAdminDrafts(token);
    setDrafts(list.drafts);
    setStorageNote(list.storage_note);
    if (detail) {
      setDetail(list.drafts.find((d) => d.id === detail.id) ?? null);
    }
  }

  async function loadList() {
    const token = requireToken();
    if (!token) return;
    setError("");
    setNotice("");
    setBusy(true);
    try {
      await refresh(token);
    } catch (e) {
      setError(e instanceof Error ? e.message : "加载草稿列表失败。");
    } finally {
      setBusy(false);
    }
  }

  async function submitCreate(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const token = requireToken();
    if (!token) return;
    if (!title.trim() || !body.trim()) {
      setError("标题与正文均不能为空。");
      return;
    }
    setError("");
    setNotice("");
    setBusy(true);
    try {
      const created = await createAdminDraft(token, title, body);
      setTitle("");
      setBody("");
      setNotice(`草稿已创建（${created.draft.id}）。`);
      await refresh(token);
    } catch (e) {
      setError(e instanceof Error ? e.message : "创建草稿失败。");
    } finally {
      setBusy(false);
    }
  }

  async function runAction(draft: AdminDraft, action: AdminDraftAction) {
    const token = requireToken();
    if (!token) return;
    setError("");
    setNotice("");
    setBusy(true);
    try {
      const updated = await actOnAdminDraft(token, draft.id, action);
      setNotice(
        `草稿 ${draft.id} 已${ACTION_LABELS[action]}（现为${STATUS_LABELS[updated.draft.status]}）。`,
      );
      await refresh(token);
    } catch (e) {
      setError(e instanceof Error ? e.message : "操作失败。");
    } finally {
      setBusy(false);
    }
  }

  async function submitEdit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const token = requireToken();
    if (!token || !editing) return;
    if (!editTitle.trim() || !editBody.trim()) {
      setError("标题与正文均不能为空。");
      return;
    }
    setError("");
    setNotice("");
    setBusy(true);
    try {
      await editAdminDraft(token, editing.id, {
        title: editTitle,
        body: editBody,
      });
      setNotice(`草稿 ${editing.id} 已保存。`);
      setEditing(null);
      await refresh(token);
    } catch (e) {
      setError(e instanceof Error ? e.message : "保存草稿失败。");
    } finally {
      setBusy(false);
    }
  }

  return (
    <>
      <div className="admin-page-heading">
        <div>
          <h1>草稿审批</h1>
          <p>创建草稿、提交审批、批准或驳回、发布。角色门禁由服务端执行。</p>
        </div>
        <span className="admin-status">进程内存 · 重启丢失</span>
      </div>

      <section className="admin-card drafts-notice">
        <p>
          草稿仅保存在进程内存中，服务重启后丢失；持久化存储另行决策。
          角色门禁：访客（user）无任何写权限；编辑（editor）仅可起草；
          审核（reviewer）可批准或驳回；发布（publisher）可发布。
          草稿内容不进入任何公开端点。
        </p>
      </section>

      <section className="admin-card">
        <form
          onSubmit={(e) => {
            e.preventDefault();
            loadList();
          }}
        >
          <label>
            <span>角色令牌（仅本次请求使用）</span>
            <input
              aria-label="角色令牌"
              type="password"
              autoComplete="off"
              value={roleToken}
              onChange={(e) => setRoleToken(e.target.value)}
            />
          </label>
          <button className="admin-button" type="submit" disabled={busy}>
            刷新列表
          </button>
        </form>
        {error && (
          <p role="alert" className="drafts-error">
            {error}
          </p>
        )}
        {notice && <p className="drafts-notice-text">{notice}</p>}
      </section>

      <section className="admin-card">
        <h2>创建草稿</h2>
        <form onSubmit={submitCreate}>
          <label>
            <span>草稿标题</span>
            <input
              aria-label="草稿标题"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
            />
          </label>
          <label>
            <span>草稿正文</span>
            <textarea
              aria-label="草稿正文"
              value={body}
              onChange={(e) => setBody(e.target.value)}
              rows={4}
            />
          </label>
          <button className="admin-button" type="submit" disabled={busy}>
            创建草稿
          </button>
        </form>
      </section>

      <section className="admin-card">
        <h2>草稿列表</h2>
        {storageNote && <p className="drafts-storage-note">{storageNote}</p>}
        {drafts === null ? (
          <p>输入角色令牌并刷新列表。</p>
        ) : drafts.length === 0 ? (
          <p>暂无草稿。</p>
        ) : (
          <ol className="drafts-list">
            {drafts.map((draft) => (
              <li key={draft.id} className="admin-draft-item">
                <div className="drafts-item-head">
                  <button
                    className="drafts-item-title"
                    onClick={() => setDetail(draft)}
                  >
                    {draft.title}
                  </button>
                  <span className="admin-status">
                    {STATUS_LABELS[draft.status]}
                  </span>
                </div>
                <p className="drafts-item-meta">
                  {draft.id} · 起草角色 {draft.author_role} · 创建{" "}
                  {draft.created_at}
                </p>
                <div className="drafts-item-actions">
                  <button
                    className="admin-button"
                    onClick={() => setDetail(draft)}
                  >
                    详情
                  </button>
                  {draft.status === "draft" && (
                    <button
                      className="admin-button"
                      onClick={() => {
                        setEditing(draft);
                        setEditTitle(draft.title);
                        setEditBody(draft.body);
                      }}
                    >
                      编辑
                    </button>
                  )}
                  {actionsFor(draft.status).map((action) => (
                    <button
                      key={action}
                      className="admin-button"
                      disabled={busy}
                      onClick={() => runAction(draft, action)}
                    >
                      {ACTION_LABELS[action]}
                    </button>
                  ))}
                </div>
                {editing?.id === draft.id && (
                  <form
                    className="drafts-edit-form"
                    onSubmit={submitEdit}
                  >
                    <label>
                      <span>编辑标题</span>
                      <input
                        aria-label="编辑标题"
                        value={editTitle}
                        onChange={(e) => setEditTitle(e.target.value)}
                      />
                    </label>
                    <label>
                      <span>编辑正文</span>
                      <textarea
                        aria-label="编辑正文"
                        value={editBody}
                        onChange={(e) => setEditBody(e.target.value)}
                        rows={4}
                      />
                    </label>
                    <button
                      className="admin-button"
                      type="submit"
                      disabled={busy}
                    >
                      保存
                    </button>
                    <button
                      className="admin-button"
                      type="button"
                      onClick={() => setEditing(null)}
                    >
                      取消
                    </button>
                  </form>
                )}
              </li>
            ))}
          </ol>
        )}
      </section>

      {detail && (
        <Drawer title={detail.title} onClose={() => setDetail(null)}>
          <p className="drafts-item-meta">
            {detail.id} · {STATUS_LABELS[detail.status]} · 起草角色{" "}
            {detail.author_role}
          </p>
          <h3>正文</h3>
          <p className="drafts-detail-body">{detail.body}</p>
          <h3>审批历史</h3>
          {detail.transitions.length === 0 ? (
            <p>暂无审批记录。</p>
          ) : (
            <ol className="drafts-transitions">
              {detail.transitions.map((t, i) => (
                <li key={i}>
                  {t.action} · {t.role} · {t.at}
                </li>
              ))}
            </ol>
          )}
          <p className="drafts-storage-note">
            草稿仅保存在进程内存中，服务重启后丢失。
          </p>
        </Drawer>
      )}
    </>
  );
}
