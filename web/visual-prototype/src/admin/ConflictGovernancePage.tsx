import { useEffect, useMemo, useState } from "react";
import type { FormEvent } from "react";
import { Icon } from "../shared/Icon";
import { fetchAdminConflicts, type AdminConflictRecord } from "./adminApi";
import "./conflicts.css";

const tokenKey = "tianji.admin.read.token.v1";

function statusLabel(status: string) {
  if (status === "bounded") return "已设边界";
  if (status === "unresolved") return "待裁定";
  return status || "未标记";
}

export function ConflictGovernancePage() {
  const [token, setToken] = useState(() => {
    try {
      return sessionStorage.getItem(tokenKey) || "";
    } catch {
      return "";
    }
  });
  const [records, setRecords] = useState<AdminConflictRecord[]>([]);
  const [loading, setLoading] = useState(false);
  const [connected, setConnected] = useState(false);
  const [error, setError] = useState("");

  async function load(nextToken: string) {
    if (!nextToken.trim()) {
      setError("请输入后台只读令牌。");
      return;
    }
    setLoading(true);
    setError("");
    try {
      const data = await fetchAdminConflicts(nextToken.trim());
      setRecords(data.records);
      setConnected(true);
      try {
        sessionStorage.setItem(tokenKey, nextToken.trim());
      } catch {
        /* session persistence is optional */
      }
    } catch (err) {
      setRecords([]);
      setConnected(false);
      setError(err instanceof Error ? err.message : "后台治理数据读取失败。");
      try {
        sessionStorage.removeItem(tokenKey);
      } catch {
        /* ignore */
      }
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    if (token) void load(token);
    // token is intentionally loaded once from the current browser session.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const summary = useMemo(
    () => ({
      total: records.length,
      bounded: records.filter((row) => row.status === "bounded").length,
      unresolved: records.filter((row) => row.status === "unresolved").length,
      evidence: records.reduce((sum, row) => sum + row.evidence.length, 0),
    }),
    [records],
  );

  function submit(event: FormEvent) {
    event.preventDefault();
    void load(token);
  }

  function disconnect() {
    setToken("");
    setRecords([]);
    setConnected(false);
    setError("");
    try {
      sessionStorage.removeItem(tokenKey);
    } catch {
      /* ignore */
    }
  }

  if (!connected) {
    return (
      <>
        <div className="admin-page-heading">
          <div>
            <h1>流派与冲突</h1>
            <p>真实内部治理数据默认不公开；授权后只读查看 Canonical 冲突资产。</p>
          </div>
          <span className="admin-readonly">
            <Icon name="shield" size={16} />
            受保护只读
          </span>
        </div>

        <section className="admin-card conflict-auth-card">
          <div className="conflict-auth-icon"><Icon name="shield" size={24} /></div>
          <div>
            <h2>需要内部只读授权</h2>
            <p>
              服务端必须先配置 <code>TIANJI_ADMIN_READ_TOKEN</code>。令牌只保存在当前浏览器会话，
              不写入仓库，不进入公开前台，也不会作为知识资产保存。
            </p>
          </div>
          <form onSubmit={submit}>
            <label>
              <span>后台只读令牌</span>
              <input
                type="password"
                autoComplete="off"
                value={token}
                onChange={(event) => setToken(event.target.value)}
                placeholder="Bearer token"
                aria-label="后台只读令牌"
              />
            </label>
            <button className="admin-button" disabled={loading}>
              {loading ? "正在验证…" : "读取真实冲突资产"}
            </button>
          </form>
          {error && <p className="conflict-auth-error" role="alert">{error}</p>}
          <div className="module-gate">
            未授权时不返回任何内部冲突记录或 Evidence 短引。
          </div>
        </section>
      </>
    );
  }

  return (
    <>
      <div className="admin-page-heading">
        <div>
          <h1>流派与冲突</h1>
          <p>来自 Canonical 的真实 school_conflict 资产；仅用于内部审核与生产边界治理。</p>
        </div>
        <div className="conflict-heading-actions">
          <span className="admin-status success">真实数据 · 只读</span>
          <button className="table-action" onClick={disconnect}>结束会话</button>
        </div>
      </div>

      <div className="asset-summary">
        <div><span>冲突记录</span><strong>{summary.total}</strong></div>
        <div><span>已设边界</span><strong>{summary.bounded}</strong></div>
        <div><span>待裁定</span><strong>{summary.unresolved}</strong></div>
        <div><span>审核短引</span><strong>{summary.evidence}</strong></div>
      </div>

      <section className="conflict-records">
        {records.map((record) => (
          <article className="admin-card conflict-record" key={record.id}>
            <header>
              <div>
                <span className="eyebrow">{record.domain} · {record.id}</span>
                <h2>{record.name}</h2>
                <p>{record.dimension}</p>
              </div>
              <span className={`admin-status ${record.status === "bounded" ? "success" : "warning"}`}>
                {statusLabel(record.status)}
              </span>
            </header>

            <div className="conflict-positions">
              {record.positions.map((position) => (
                <section key={position.id}>
                  <small>{position.label}</small>
                  <p>{position.position}</p>
                  <span>{position.section_ids.join(" · ")}</span>
                </section>
              ))}
            </div>

            <div className="conflict-policy-grid">
              <div>
                <small>生产策略</small>
                <p>{record.production_policy}</p>
              </div>
              <div>
                <small>执行策略</small>
                <p>{record.executable_policy}</p>
              </div>
            </div>

            <details className="conflict-evidence">
              <summary>
                <span>查看已审核 Evidence</span>
                <small>{record.evidence.length} 条</small>
              </summary>
              <div>
                {record.evidence.map((item) => (
                  <article key={`${record.id}-${item.section_id}`}>
                    <div>
                      <strong>{item.classic_title}</strong>
                      <span>{item.evidence_level}</span>
                    </div>
                    <small>{item.chapter_title} · {item.locator}</small>
                    <blockquote>{item.original_text}</blockquote>
                    <code>{item.section_id}</code>
                  </article>
                ))}
              </div>
            </details>
          </article>
        ))}
      </section>

      <div className="asset-boundary-note">
        <Icon name="shield" size={18} />
        <div>
          <strong>冲突记录不是“二选一自动裁决器”</strong>
          <p>
            bounded 表示已经明确了可执行边界；unresolved 表示仍禁止统一规则进入生产。
            后台只显示已审核短引，不开放完整古籍浏览。
          </p>
        </div>
      </div>
    </>
  );
}
