import { useEffect, useMemo, useState } from "react";
import type { FormEvent } from "react";
import { Icon } from "../shared/Icon";
import { Dialog } from "../shared/Dialog";
import { fetchAdminPrompts, type AdminPromptRecord } from "./adminApi";
import "./governance-assets.css";

const tokenKey = "tianji.admin.read.token.v1";

function readToken() {
  try {
    return sessionStorage.getItem(tokenKey) || "";
  } catch {
    return "";
  }
}

export function PromptGovernancePage() {
  const [token, setToken] = useState(readToken);
  const [records, setRecords] = useState<AdminPromptRecord[]>([]);
  const [connected, setConnected] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [selected, setSelected] = useState<AdminPromptRecord | null>(null);

  async function load(nextToken: string) {
    if (!nextToken.trim()) {
      setError("请输入后台只读令牌。");
      return;
    }
    setLoading(true);
    setError("");
    try {
      setRecords(await fetchAdminPrompts(nextToken.trim()));
      setConnected(true);
      try {
        sessionStorage.setItem(tokenKey, nextToken.trim());
      } catch {
        /* session persistence is optional */
      }
    } catch (err) {
      setConnected(false);
      setRecords([]);
      setError(err instanceof Error ? err.message : "Prompt 注册表读取失败。");
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
    setSelected(null);
    try {
      sessionStorage.removeItem(tokenKey);
    } catch {
      /* ignore */
    }
  }

  const selectedVersion = records[0]?.configured_selection || "未配置";
  const selectionRegistered = records[0]?.selection_registered ?? false;
  const productionEligible = useMemo(
    () => records.filter((row) => row.production_eligible).length,
    [records],
  );

  if (!connected) {
    return (
      <>
        <div className="admin-page-heading">
          <div>
            <h1>Prompt 版本</h1>
            <p>读取真实不可变 Prompt 注册表、SHA256 与当前环境选择；不再提供页面内假编辑器。</p>
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
                未授权时页面不会请求真实 Prompt 文本。服务端令牌由
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
              {loading ? "正在验证…" : "读取真实 Prompt"}
            </button>
          </form>
          {error && <p className="governance-auth-error" role="alert">{error}</p>}
          <div className="module-gate">
            Prompt 文本属于内部解释策略；页面只读，版本变更必须通过代码审查与固定评测集。
          </div>
        </section>
      </>
    );
  }

  return (
    <>
      <div className="admin-page-heading">
        <div>
          <h1>Prompt 版本</h1>
          <p>真实不可变注册表、当前选择、SHA256 与生产资格。</p>
        </div>
        <div className="governance-heading-actions">
          <span className={`admin-status ${selectionRegistered ? "success" : "danger"}`}>
            {selectionRegistered ? "选择有效" : "选择无效"}
          </span>
          <button className="table-action" onClick={disconnect}>结束会话</button>
        </div>
      </div>

      <div className="asset-summary">
        <div><span>注册版本</span><strong>{records.length}</strong></div>
        <div><span>当前选择</span><strong className="summary-text">{selectedVersion}</strong></div>
        <div><span>生产资格</span><strong>{productionEligible}</strong></div>
        <div><span>自动发布</span><strong className="summary-text">禁止</strong></div>
      </div>

      <section className="admin-card governance-asset-card">
        <div className="admin-card-heading">
          <div>
            <h2>Prompt Registry</h2>
            <p>指令修改需要新版本；当前注册项不可在浏览器内覆盖。</p>
          </div>
          <span className="admin-small-muted">immutable</span>
        </div>
        <div className="asset-table-scroll" role="region" aria-label="真实 Prompt 版本表" tabIndex={0}>
          <table className="asset-table governance-table">
            <thead>
              <tr>
                <th>版本</th><th>SHA256</th><th>长度</th><th>默认</th><th>当前选择</th><th>生产资格</th><th>操作</th>
              </tr>
            </thead>
            <tbody>
              {records.map((row) => (
                <tr key={row.id}>
                  <td><strong>{row.version}</strong><small className="asset-id">{row.immutable ? "immutable" : "mutable"}</small></td>
                  <td className="secondary-cell"><code>{row.sha256}</code></td>
                  <td className="count-cell">{row.instruction_length}</td>
                  <td><span className={`admin-status ${row.default ? "success" : "neutral"}`}>{row.default ? "默认" : "否"}</span></td>
                  <td><span className={`admin-status ${row.selected ? "success" : "neutral"}`}>{row.selected ? "已选择" : "否"}</span></td>
                  <td><span className={`admin-status ${row.production_eligible ? "success" : "warning"}`}>{row.production_eligible ? "允许" : "仅基线/研究"}</span></td>
                  <td><button className="table-action" onClick={() => setSelected(row)}>查看指令 <Icon name="chevron" size={12} /></button></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <div className="asset-table-footer">
          <span>当前环境选择：{selectedVersion}</span>
          <span>只读 · 修改必须新增版本</span>
        </div>
      </section>

      {selected && (
        <Dialog title="真实 Prompt 指令" onClose={() => setSelected(null)} className="admin-detail-dialog">
          <div className="governance-detail">
            <h3>{selected.version}</h3>
            <code>{selected.sha256}</code>
            <dl className="admin-detail-fields">
              <div><dt>长度</dt><dd>{selected.instruction_length}</dd></div>
              <div><dt>默认</dt><dd>{selected.default ? "是" : "否"}</dd></div>
              <div><dt>当前选择</dt><dd>{selected.selected ? "是" : "否"}</dd></div>
              <div><dt>生产资格</dt><dd>{selected.production_eligible ? "允许" : "仅基线/研究"}</dd></div>
              <div><dt>不可变</dt><dd>{selected.immutable ? "是" : "否"}</dd></div>
              <div><dt>自动发布</dt><dd>{selected.automatic_release_allowed ? "允许" : "禁止"}</dd></div>
            </dl>
            <h4>完整系统指令</h4>
            <textarea
              className="module-editor"
              aria-label="Prompt 完整指令"
              readOnly
              value={selected.instruction}
              rows={18}
            />
            <div className="module-gate">
              该文本来自服务端真实 Prompt registry；页面不会保存任何编辑，也不会直接发布新 Prompt。
            </div>
          </div>
        </Dialog>
      )}

      <div className="asset-boundary-note">
        <Icon name="shield" size={18} />
        <div>
          <strong>Prompt 版本化，不做页面内临时覆盖</strong>
          <p>生产解释仍需固定评测集和人工语义复核；Prompt 通过结构校验不等于模型质量已通过。</p>
        </div>
      </div>
    </>
  );
}
