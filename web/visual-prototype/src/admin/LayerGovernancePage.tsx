import { useEffect, useMemo, useState } from "react";
import type { FormEvent } from "react";
import { Icon } from "../shared/Icon";
import { fetchAdminLayers, type AdminLayerRecord } from "./adminApi";
import "./governance-assets.css";

const tokenKey = "tianji.admin.read.token.v1";

function readToken() {
  try {
    return sessionStorage.getItem(tokenKey) || "";
  } catch {
    return "";
  }
}

function tone(row: AdminLayerRecord) {
  if (row.id === "canonical") return "success";
  if (row.id === "quarantine") return "warning";
  return "neutral";
}

export function LayerGovernancePage() {
  const [token, setToken] = useState(readToken);
  const [records, setRecords] = useState<AdminLayerRecord[]>([]);
  const [connected, setConnected] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function load(nextToken: string) {
    if (!nextToken.trim()) {
      setError("请输入后台只读令牌。");
      return;
    }
    setLoading(true);
    setError("");
    try {
      setRecords(await fetchAdminLayers(nextToken.trim()));
      setConnected(true);
      try {
        sessionStorage.setItem(tokenKey, nextToken.trim());
      } catch {
        /* session persistence is optional */
      }
    } catch (err) {
      setConnected(false);
      setRecords([]);
      setError(err instanceof Error ? err.message : "知识分层治理数据读取失败。");
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
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  function submit(event: FormEvent) {
    event.preventDefault();
    void load(token);
  }

  function disconnect() {
    setConnected(false);
    setToken("");
    setRecords([]);
    setError("");
    try {
      sessionStorage.removeItem(tokenKey);
    } catch {
      /* ignore */
    }
  }

  const byId = useMemo(
    () => new Map(records.map((row) => [row.id, row])),
    [records],
  );
  const raw = byId.get("raw");
  const quarantine = byId.get("quarantine");
  const canonical = byId.get("canonical");

  if (!connected) {
    return (
      <>
        <div className="admin-page-heading">
          <div>
            <h1>RAW / Quarantine / Canonical</h1>
            <p>读取真实分层统计、晋级门槛与生产边界；不返回任何内部文件路径或隔离正文。</p>
          </div>
          <span className="admin-readonly">
            <Icon name="shield" size={16} />
            受保护只读
          </span>
        </div>
        <section className="admin-card governance-auth">
          <div className="governance-auth-copy">
            <span><Icon name="shield" size={22} /></span>
            <div>
              <h2>需要内部只读授权</h2>
              <p>
                未授权时页面不会请求分层统计。服务端令牌由
                <code> TIANJI_ADMIN_READ_TOKEN </code>配置。
              </p>
            </div>
          </div>
          <form onSubmit={submit}>
            <label>
              <span>后台只读令牌</span>
              <input
                type="password"
                autoComplete="off"
                value={token}
                onChange={(event) => setToken(event.target.value)}
                aria-label="后台只读令牌"
                placeholder="Bearer token"
              />
            </label>
            <button className="admin-button" disabled={loading}>
              {loading ? "正在验证…" : "读取真实分层"}
            </button>
          </form>
          {error && <p className="governance-auth-error" role="alert">{error}</p>}
          <div className="module-gate">
            接口只返回聚合统计与治理策略；不会返回 RAW/Quarantine/Canonical 的文件名、路径、正文或哈希。
          </div>
        </section>
      </>
    );
  }

  return (
    <>
      <div className="admin-page-heading">
        <div>
          <h1>RAW / Quarantine / Canonical</h1>
          <p>真实知识分层状态；统计来自当前仓库与已审运行时，而不是静态示例。</p>
        </div>
        <div className="governance-heading-actions">
          <span className="admin-status success">真实数据 · 只读</span>
          <button className="table-action" onClick={disconnect}>结束会话</button>
        </div>
      </div>

      <div className="asset-summary">
        <div><span>RAW 跟踪文件</span><strong>{raw?.tracked_file_count ?? 0}</strong></div>
        <div><span>Quarantine 文件</span><strong>{quarantine?.tracked_file_count ?? 0}</strong></div>
        <div><span>Canonical 文件</span><strong>{canonical?.tracked_file_count ?? 0}</strong></div>
        <div><span>Canonical 实体</span><strong>{canonical?.entity_count ?? 0}</strong></div>
      </div>

      <section className="admin-card governance-asset-card">
        <div className="admin-card-heading">
          <div>
            <h2>真实分层状态</h2>
            <p>RAW 默认不提交 Git；Quarantine 不进入生产；Canonical 仍受领域与 Variant 边界约束。</p>
          </div>
          <span className="admin-small-muted">聚合统计</span>
        </div>
        <div className="asset-table-scroll" role="region" aria-label="真实知识分层状态表" tabIndex={0}>
          <table className="asset-table governance-table">
            <thead>
              <tr>
                <th>层级</th><th>跟踪文件</th><th>古籍</th><th>实体</th><th>领域</th><th>生产检索</th><th>保护文件</th>
              </tr>
            </thead>
            <tbody>
              {records.map((row) => (
                <tr key={row.id}>
                  <td><strong>{row.name}</strong><small className="asset-id">{row.id}</small></td>
                  <td className="count-cell">{row.tracked_file_count}</td>
                  <td className="count-cell">{row.classic_count}</td>
                  <td className="count-cell">{row.entity_count}</td>
                  <td className="secondary-cell">{row.domains.join(" · ") || "—"}<small>{row.domain_count} 个领域</small></td>
                  <td><span className={`admin-status ${tone(row)}`}>{row.production_queryable ? "允许（受边界约束）" : "禁止"}</span></td>
                  <td className="count-cell">{row.protected_file_count}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <div className="asset-table-footer">
          <span>共 {records.length} 个治理层级</span>
          <span>内部只读 · 无晋级写入</span>
        </div>
      </section>

      <section className="admin-card">
        <div className="admin-card-heading">
          <div>
            <h2>晋级与发布边界</h2>
            <p>下面来自当前治理策略，不执行任何晋级操作。</p>
          </div>
        </div>
        <div className="dashboard-queue">
          {records.map((row) => (
            <article className="queue-item" key={row.id}>
              <span className="queue-document"><Icon name="layers" size={18} /></span>
              <div>
                <strong>{row.name}</strong>
                <p>{row.promotion_policy}</p>
                <small>{row.release_policy}</small>
              </div>
              <span className={`admin-status ${tone(row)}`}>
                {row.id === "raw" ? "原始层" : row.id === "quarantine" ? "隔离层" : "规范层"}
              </span>
            </article>
          ))}
        </div>
      </section>

      {raw && (
        <section className="admin-card">
          <div className="admin-card-heading">
            <div>
              <h2>采集与快照登记</h2>
              <p>RAW 文件数为 0 不代表没有采集能力，而是当前策略默认不把原始缓存提交到仓库。</p>
            </div>
          </div>
          <div className="asset-summary">
            <div><span>登记采集源</span><strong>{raw.registered_ingestion_sources}</strong></div>
            {Object.entries(raw.ingestion_modes).map(([name, count]) => (
              <div key={name}><span>{name}</span><strong>{count}</strong></div>
            ))}
          </div>
        </section>
      )}

      <div className="asset-boundary-note">
        <Icon name="shield" size={18} />
        <div>
          <strong>分层状态不是公开知识目录</strong>
          <p>后台只展示聚合治理事实；隔离资产正文、文件路径和具体候选内容仍不通过此页面暴露。</p>
        </div>
      </div>
    </>
  );
}
