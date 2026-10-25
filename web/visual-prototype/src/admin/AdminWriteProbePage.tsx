import { useState } from "react";
import type { FormEvent } from "react";
import {
  fetchAdminAudit,
  runAdminWriteProbe,
  type AdminAuditEntry,
  type AdminWriteProbeOperation,
  type AdminWriteProbeResponse,
} from "./adminApi";
import "./write-probe.css";

const OPERATIONS: { value: AdminWriteProbeOperation; label: string }[] = [
  { value: "draft", label: "起草" },
  { value: "approve", label: "审批" },
  { value: "publish", label: "发布" },
];

/**
 * TJ-026.4 batch 1: role model + unauthorized blocking + audit skeleton.
 *
 * This page is a CHECKPOINT, not a business write surface: the probe
 * endpoint never applies a write (write_applied is always false), and
 * no draft/approval/publish business exists behind it. Two distinct
 * credentials are used on purpose — a role token for the probe and
 * the TJ-026.3 read token (system scope) for audit reads — and neither
 * is persisted anywhere (component state only).
 */
export function AdminWriteProbePage() {
  const [roleToken, setRoleToken] = useState("");
  const [operation, setOperation] = useState<AdminWriteProbeOperation>("draft");
  const [probe, setProbe] = useState<AdminWriteProbeResponse | null>(null);
  const [probeError, setProbeError] = useState("");
  const [probeLoading, setProbeLoading] = useState(false);

  const [readToken, setReadToken] = useState("");
  const [entries, setEntries] = useState<AdminAuditEntry[] | null>(null);
  const [auditError, setAuditError] = useState("");
  const [auditLoading, setAuditLoading] = useState(false);

  async function submitProbe(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setProbeError("");
    setProbe(null);
    if (!roleToken.trim()) {
      setProbeError("请输入角色令牌。");
      return;
    }
    setProbeLoading(true);
    try {
      const next = await runAdminWriteProbe(roleToken.trim(), operation);
      setProbe(next);
    } catch (cause) {
      setProbeError(cause instanceof Error ? cause.message : "写探针请求失败。");
    } finally {
      setProbeLoading(false);
    }
  }

  async function submitAudit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setAuditError("");
    setEntries(null);
    if (!readToken.trim()) {
      setAuditError("请输入后台只读令牌。");
      return;
    }
    setAuditLoading(true);
    try {
      const next = await fetchAdminAudit(readToken.trim());
      setEntries(next.entries);
    } catch (cause) {
      setAuditError(cause instanceof Error ? cause.message : "审计记录读取失败。");
    } finally {
      setAuditLoading(false);
    }
  }

  return (
    <div className="admin-probe-workspace">
      <header className="admin-probe-hero">
        <span>内部工具 · 首批骨架</span>
        <h1>写权限探针与审计记录</h1>
        <p>
          首批只验证三件事：角色模型、未授权阻止、审计留痕。探针不产生真实写业务——
          没有草稿、审批、发布与回滚功能；草稿审批流与回滚另立任务。
          两个令牌均仅本次请求使用，不写入本机存储。
        </p>
      </header>

      <form className="admin-probe-form" onSubmit={submitProbe}>
        <label>
          <span>角色令牌（仅本次请求使用）</span>
          <input aria-label="角色令牌" type="password" autoComplete="off"
            value={roleToken} onChange={(event) => setRoleToken(event.target.value)}
            placeholder="TIANJI_ADMIN_ROLE_TOKENS 中的某一令牌" required />
        </label>
        <fieldset>
          <legend>探针操作</legend>
          <div className="admin-probe-radios">
            {OPERATIONS.map((item) => (
              <label key={item.value}>
                <input type="radio" name="probe-operation" value={item.value}
                  checked={operation === item.value}
                  onChange={() => setOperation(item.value)} />
                {item.label}
              </label>
            ))}
          </div>
        </fieldset>
        <div className="admin-probe-actions">
          <button type="submit" disabled={probeLoading}>
            {probeLoading ? "正在验证角色…" : "执行写探针"}
          </button>
        </div>
        {probeError && <p role="alert" className="admin-probe-error">{probeError}</p>}
      </form>

      {probe && (
        <section className="admin-probe-results" aria-live="polite">
          <h2>探针结果</h2>
          <p>
            角色 <strong>{probe.role}</strong> 可执行 <strong>{probe.operation}</strong>。
            本次探针未产生真实写入（write_applied 为 false）。
          </p>
        </section>
      )}

      <form className="admin-probe-form" onSubmit={submitAudit}>
        <label>
          <span>后台只读令牌（仅本次请求使用，需 system scope）</span>
          <input aria-label="后台只读令牌" type="password" autoComplete="off"
            value={readToken} onChange={(event) => setReadToken(event.target.value)}
            placeholder="TIANJI_ADMIN_READ_TOKEN" required />
        </label>
        <div className="admin-probe-actions">
          <button type="submit" disabled={auditLoading}>
            {auditLoading ? "正在读取审计记录…" : "查看审计记录"}
          </button>
        </div>
        {auditError && <p role="alert" className="admin-probe-error">{auditError}</p>}
      </form>

      {entries && (
        <section className="admin-probe-results" aria-live="polite">
          <h2>审计记录</h2>
          {entries.length === 0 ? (
            <p className="admin-probe-empty">暂无审计记录。执行一次写探针后记录会出现在这里。</p>
          ) : (
            <table className="admin-probe-table">
              <thead>
                <tr>
                  <th>角色</th>
                  <th>时间</th>
                  <th>操作</th>
                  <th>结果</th>
                </tr>
              </thead>
              <tbody>
                {entries.map((entry, index) => (
                  <tr key={index}>
                    <td>{entry.who}</td>
                    <td>{entry.when}</td>
                    <td>{entry.what}</td>
                    <td>{entry.outcome === "allowed" ? "通过" : "拒绝"}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </section>
      )}
    </div>
  );
}
