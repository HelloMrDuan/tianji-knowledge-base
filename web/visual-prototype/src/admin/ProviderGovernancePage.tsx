import { useEffect, useState } from "react";
import type { FormEvent } from "react";
import { Icon } from "../shared/Icon";
import { fetchAdminProvider, type AdminProviderRecord } from "./adminApi";
import "./governance-assets.css";

const tokenKey = "tianji.admin.read.token.v1";

function readToken() {
  try {
    return sessionStorage.getItem(tokenKey) || "";
  } catch {
    return "";
  }
}

function statusLabel(status: AdminProviderRecord["status"]) {
  if (status === "configured") return "配置完整";
  if (status === "disabled") return "已禁用";
  if (status === "invalid") return "配置无效";
  return "配置不完整";
}

function statusTone(status: AdminProviderRecord["status"]) {
  if (status === "configured") return "success";
  if (status === "invalid") return "danger";
  if (status === "incomplete") return "warning";
  return "neutral";
}

export function ProviderGovernancePage() {
  const [token, setToken] = useState(readToken);
  const [record, setRecord] = useState<AdminProviderRecord | null>(null);
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
      const rows = await fetchAdminProvider(nextToken.trim());
      setRecord(rows[0] || null);
      setConnected(true);
      try {
        sessionStorage.setItem(tokenKey, nextToken.trim());
      } catch {
        /* session persistence is optional */
      }
    } catch (err) {
      setConnected(false);
      setRecord(null);
      setError(err instanceof Error ? err.message : "Provider 配置读取失败。");
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
    setRecord(null);
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
            <h1>AI Provider / Model</h1>
            <p>读取服务端真实配置状态；不读取、不返回也不编辑 API Key。</p>
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
                未授权时页面不会请求 Provider 配置。服务端令牌由
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
              {loading ? "正在验证…" : "读取真实配置"}
            </button>
          </form>
          {error && <p className="governance-auth-error" role="alert">{error}</p>}
          <div className="module-gate">
            本页不会发起模型网络请求，也不会把 API Key、完整带路径 Endpoint 或凭据写入前端。
          </div>
        </section>
      </>
    );
  }

  return (
    <>
      <div className="admin-page-heading">
        <div>
          <h1>AI Provider / Model</h1>
          <p>真实服务端环境配置状态；只读，不做假连接测试。</p>
        </div>
        <div className="governance-heading-actions">
          <span className={`admin-status ${statusTone(record?.status || "disabled")}`}>
            {record ? statusLabel(record.status) : "无记录"}
          </span>
          <button className="table-action" onClick={disconnect}>结束会话</button>
        </div>
      </div>

      {record ? (
        <>
          <div className="asset-summary">
            <div><span>Driver</span><strong className="summary-text">{record.driver}</strong></div>
            <div><span>Model</span><strong className="summary-text">{record.model || "未配置"}</strong></div>
            <div><span>API Key</span><strong className="summary-text">{record.api_key_present ? "已设置" : "未设置"}</strong></div>
            <div><span>自动发布</span><strong className="summary-text">{record.automatic_release_allowed ? "允许" : "禁止"}</strong></div>
          </div>

          <section className="admin-card governance-asset-card">
            <div className="admin-card-heading">
              <div>
                <h2>当前解释服务配置</h2>
                <p>配置完整只代表环境变量满足要求，不代表外部网络或模型质量已经验证。</p>
              </div>
              <span className={`admin-status ${statusTone(record.status)}`}>{statusLabel(record.status)}</span>
            </div>
            <dl className="admin-detail-fields">
              <div><dt>允许 Driver</dt><dd>{record.allowed_drivers.join(" · ")}</dd></div>
              <div><dt>Endpoint Origin</dt><dd>{record.endpoint_origin || "未配置 / 不可解析"}</dd></div>
              <div><dt>Endpoint Host</dt><dd>{record.endpoint_host || "—"}</dd></div>
              <div><dt>Model</dt><dd>{record.model || "未配置"}</dd></div>
              <div><dt>Timeout</dt><dd>{record.timeout_seconds == null ? "无效" : `${record.timeout_seconds}s`}</dd></div>
              <div><dt>Max Output Tokens</dt><dd>{record.max_output_tokens ?? "无效"}</dd></div>
              <div><dt>Prompt Version</dt><dd>{record.prompt_version}</dd></div>
              <div><dt>API Key 存在</dt><dd>{record.api_key_present ? "是" : "否"}</dd></div>
              <div><dt>API Key 暴露</dt><dd>{record.api_key_exposed ? "是" : "否"}</dd></div>
              <div><dt>Live Connectivity</dt><dd>{record.live_connectivity_verified ? "已验证" : "未验证"}</dd></div>
            </dl>
            <div className="module-gate">
              服务端只返回 Key 是否存在，不返回 Key 值；Endpoint 只返回 origin/host，不返回可能包含部署细节的完整路径。
            </div>
          </section>

          <div className="asset-boundary-note">
            <Icon name="shield" size={18} />
            <div>
              <strong>配置完整 ≠ 模型质量通过</strong>
              <p>真实模型仍需在固定评测集上执行并经过人工语义复核；当前自动发布保持关闭。</p>
            </div>
          </div>
        </>
      ) : (
        <section className="admin-card admin-empty">
          <h2>没有 Provider 配置记录</h2>
          <p>服务端未返回可展示的配置状态。</p>
        </section>
      )}
    </>
  );
}
