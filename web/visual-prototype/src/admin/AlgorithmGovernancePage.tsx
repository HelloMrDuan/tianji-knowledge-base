import { useEffect, useMemo, useState } from "react";
import type { FormEvent } from "react";
import { Icon } from "../shared/Icon";
import { Dialog } from "../shared/Dialog";
import { fetchAdminAlgorithms, type AdminAlgorithmRecord } from "./adminApi";
import "./governance-assets.css";

const tokenKey = "tianji.admin.read.token.v1";

function readToken() {
  try {
    return sessionStorage.getItem(tokenKey) || "";
  } catch {
    return "";
  }
}

export function AlgorithmGovernancePage() {
  const [token, setToken] = useState(readToken);
  const [records, setRecords] = useState<AdminAlgorithmRecord[]>([]);
  const [connected, setConnected] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [query, setQuery] = useState("");
  const [domain, setDomain] = useState("全部领域");
  const [selected, setSelected] = useState<AdminAlgorithmRecord | null>(null);

  async function load(nextToken: string) {
    if (!nextToken.trim()) {
      setError("请输入后台只读令牌。");
      return;
    }
    setLoading(true);
    setError("");
    try {
      setRecords(await fetchAdminAlgorithms(nextToken.trim()));
      setConnected(true);
      try {
        sessionStorage.setItem(tokenKey, nextToken.trim());
      } catch {
        /* session persistence is optional */
      }
    } catch (err) {
      setConnected(false);
      setRecords([]);
      setError(err instanceof Error ? err.message : "算法治理数据读取失败。");
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

  const domains = useMemo(
    () => ["全部领域", ...Array.from(new Set(records.map((row) => row.domain))).sort()],
    [records],
  );
  const visible = useMemo(
    () =>
      records.filter(
        (row) =>
          (domain === "全部领域" || row.domain === domain) &&
          `${row.domain} ${row.variant} ${row.provider} ${row.scope}`
            .toLowerCase()
            .includes(query.trim().toLowerCase()),
      ),
    [records, domain, query],
  );

  if (!connected) {
    return (
      <>
        <div className="admin-page-heading">
          <div>
            <h1>算法与 Variant</h1>
            <p>真实读取 Phase2 execution contracts；不再展示静态算法占位记录。</p>
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
                未授权时页面不会请求真实 Variant、provider 或验证关系。服务端令牌由
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
              {loading ? "正在验证…" : "读取真实算法"}
            </button>
          </form>
          {error && <p className="governance-auth-error" role="alert">{error}</p>}
          <div className="module-gate">
            本页只展示当前已审执行契约和测试关联，不修改算法、Variant 或生产默认值。
          </div>
        </section>
      </>
    );
  }

  const totalRules = records.reduce((sum, row) => sum + row.rule_count, 0);
  const validatedRules = records.reduce((sum, row) => sum + row.validated_rule_count, 0);
  const goldenCases = new Set(records.flatMap((row) => row.golden_case_ids)).size;

  return (
    <>
      <div className="admin-page-heading">
        <div>
          <h1>算法与 Variant</h1>
          <p>真实 Phase2 execution contracts、provider、验证状态与未决边界。</p>
        </div>
        <div className="governance-heading-actions">
          <span className="admin-status success">真实数据 · 只读</span>
          <button className="table-action" onClick={disconnect}>结束会话</button>
        </div>
      </div>

      <div className="asset-summary">
        <div><span>真实 Variant</span><strong>{records.length}</strong></div>
        <div><span>执行规则</span><strong>{totalRules}</strong></div>
        <div><span>Validated</span><strong>{validatedRules}</strong></div>
        <div><span>Golden Cases</span><strong>{goldenCases}</strong></div>
      </div>

      <section className="admin-card governance-asset-card">
        <div className="asset-toolbar">
          <div className="asset-search">
            <Icon name="search" size={17} />
            <input
              aria-label="搜索算法与 Variant"
              value={query}
              onChange={(event) => setQuery(event.target.value)}
              placeholder="搜索领域、Variant、provider 或 scope"
            />
          </div>
          <div className="asset-filters">
            <select aria-label="领域筛选" value={domain} onChange={(event) => setDomain(event.target.value)}>
              {domains.map((item) => <option key={item}>{item}</option>)}
            </select>
          </div>
        </div>

        <div className="asset-table-scroll" role="region" aria-label="真实算法与 Variant 表" tabIndex={0}>
          <table className="asset-table governance-table">
            <thead>
              <tr>
                <th>领域 / Variant</th><th>Provider</th><th>规则</th><th>Validated</th><th>Golden</th><th>未决项</th><th>生产状态</th><th>操作</th>
              </tr>
            </thead>
            <tbody>
              {visible.map((row) => (
                <tr key={row.id}>
                  <td><strong>{row.domain}</strong><small className="asset-id">{row.variant}</small></td>
                  <td className="secondary-cell">{row.provider || "—"}</td>
                  <td className="count-cell">{row.executable_rule_count} / {row.rule_count}</td>
                  <td className="count-cell">{row.validated_rule_count}</td>
                  <td className="count-cell">{row.golden_case_ids.length}</td>
                  <td className="count-cell">{row.unresolved.length}</td>
                  <td><span className={`admin-status ${row.production_ready ? "success" : "warning"}`}>{row.production_ready ? "已验证" : "有限能力"}</span></td>
                  <td><button className="table-action" onClick={() => setSelected(row)}>详情 <Icon name="chevron" size={12} /></button></td>
                </tr>
              ))}
            </tbody>
          </table>
          {visible.length === 0 && (
            <div className="admin-empty-results"><Icon name="search" size={26} /><p>没有匹配的真实 Variant</p></div>
          )}
        </div>
        <div className="asset-table-footer">
          <span>共 {visible.length} / {records.length} 条</span>
          <span>deterministic · AI 不参与排盘计算</span>
        </div>
      </section>

      {selected && (
        <Dialog title="真实算法契约详情" onClose={() => setSelected(null)} className="admin-detail-dialog">
          <div className="governance-detail">
            <h3>{selected.domain}</h3>
            <code>{selected.variant}</code>
            <dl className="admin-detail-fields">
              <div><dt>Provider</dt><dd>{selected.provider || "—"}</dd></div>
              <div><dt>规则</dt><dd>{selected.executable_rule_count} / {selected.rule_count} executable</dd></div>
              <div><dt>Validated</dt><dd>{selected.validated_rule_count}</dd></div>
              <div><dt>Golden Cases</dt><dd>{selected.golden_case_ids.length}</dd></div>
              <div><dt>确定性</dt><dd>{selected.deterministic ? "是" : "否"}</dd></div>
              <div><dt>AI 可计算盘面</dt><dd>{selected.ai_may_compute_chart ? "是" : "否"}</dd></div>
            </dl>
            <h4>Scope</h4>
            <p>{selected.scope || "当前契约未登记额外 scope。"}</p>
            <h4>未决边界</h4>
            {selected.unresolved.length ? selected.unresolved.map((item) => <p className="governance-limit" key={item}>{item}</p>) : <p>当前契约未登记 unresolved。</p>}
            <h4>Golden Cases</h4>
            <p>{selected.golden_case_ids.join(" · ") || "无"}</p>
            <h4>Phase1 规则</h4>
            <p>{selected.phase1_rule_ids.join(" · ") || "无"}</p>
            <div className="module-gate">
              这里展示的是当前真实 execution contract，不读取旧 engine registry 的 planned 状态来替代运行时事实。
            </div>
          </div>
        </Dialog>
      )}

      <div className="asset-boundary-note">
        <Icon name="shield" size={18} />
        <div>
          <strong>Variant 必须显式，AI 不能替代确定性算法</strong>
          <p>后台只读展示真实执行范围、验证与未决边界；不同流派或时间口径不得静默合并。</p>
        </div>
      </div>
    </>
  );
}
