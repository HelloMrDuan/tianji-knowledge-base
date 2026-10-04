import { useEffect, useMemo, useState } from "react";
import type { FormEvent } from "react";
import { Icon } from "../shared/Icon";
import { Dialog } from "../shared/Dialog";
import { fetchAdminTerms, type AdminTermRecord } from "./adminApi";
import "./governance-assets.css";

const tokenKey = "tianji.admin.read.token.v1";

function readToken() {
  try {
    return sessionStorage.getItem(tokenKey) || "";
  } catch {
    return "";
  }
}

export function TermGovernancePage() {
  const [token, setToken] = useState(readToken);
  const [records, setRecords] = useState<AdminTermRecord[]>([]);
  const [connected, setConnected] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [query, setQuery] = useState("");
  const [domain, setDomain] = useState("全部领域");
  const [stage, setStage] = useState("全部类型");
  const [selected, setSelected] = useState<AdminTermRecord | null>(null);

  async function load(nextToken: string) {
    if (!nextToken.trim()) {
      setError("请输入后台只读令牌。");
      return;
    }
    setLoading(true);
    setError("");
    try {
      setRecords(await fetchAdminTerms(nextToken.trim()));
      setConnected(true);
      try {
        sessionStorage.setItem(tokenKey, nextToken.trim());
      } catch {
        /* session persistence is optional */
      }
    } catch (err) {
      setConnected(false);
      setRecords([]);
      setError(err instanceof Error ? err.message : "后台术语治理数据读取失败。");
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
    // Restore only a token explicitly stored in this browser session.
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
  const stages = useMemo(
    () => ["全部类型", ...Array.from(new Set(records.map((row) => row.definition_kind || "未分类"))).sort()],
    [records],
  );
  const visible = useMemo(
    () =>
      records.filter(
        (row) =>
          (domain === "全部领域" || row.domain === domain) &&
          (stage === "全部类型" || (row.definition_kind || "未分类") === stage) &&
          `${row.name} ${row.id} ${row.aliases.join(" ")} ${row.definition}`
            .toLowerCase()
            .includes(query.trim().toLowerCase()),
      ),
    [records, domain, stage, query],
  );

  if (!connected) {
    return (
      <>
        <div className="admin-page-heading">
          <div>
            <h1>术语管理</h1>
            <p>真实读取 Canonical 术语、别名、定义与来源定位；不返回来源章节正文。</p>
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
                未授权时页面不会请求任何真实术语资产。服务端令牌由
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
              {loading ? "正在验证…" : "读取真实术语"}
            </button>
          </form>
          {error && <p className="governance-auth-error" role="alert">{error}</p>}
          <div className="module-gate">
            接口只返回术语定义、别名、来源定位和关联 ID；来源章节正文、RAW/Quarantine 文件与内部路径不会通过此页返回。
          </div>
        </section>
      </>
    );
  }

  const evidenceCount = records.reduce((sum, row) => sum + row.evidence.length, 0);
  const phase2Rules = new Set(records.flatMap((row) => row.phase2_rule_ids)).size;

  return (
    <>
      <div className="admin-page-heading">
        <div>
          <h1>术语管理</h1>
          <p>真实 Canonical 术语治理数据；来源正文仍保持内部隔离。</p>
        </div>
        <div className="governance-heading-actions">
          <span className="admin-status success">真实数据 · 只读</span>
          <button className="table-action" onClick={disconnect}>结束会话</button>
        </div>
      </div>

      <div className="asset-summary">
        <div><span>真实术语</span><strong>{records.length}</strong></div>
        <div><span>当前筛选</span><strong>{visible.length}</strong></div>
        <div><span>来源定位</span><strong>{evidenceCount}</strong></div>
        <div><span>Phase2 关联</span><strong>{phase2Rules}</strong></div>
      </div>

      <section className="admin-card governance-asset-card">
        <div className="asset-toolbar">
          <div className="asset-search">
            <Icon name="search" size={17} />
            <input
              aria-label="搜索术语管理"
              value={query}
              onChange={(event) => setQuery(event.target.value)}
              placeholder="搜索术语、ID、别名或定义"
            />
          </div>
          <div className="asset-filters">
            <select aria-label="领域筛选" value={domain} onChange={(event) => setDomain(event.target.value)}>
              {domains.map((item) => <option key={item}>{item}</option>)}
            </select>
            <select aria-label="定义类型筛选" value={stage} onChange={(event) => setStage(event.target.value)}>
              {stages.map((item) => <option key={item}>{item}</option>)}
            </select>
          </div>
        </div>

        <div className="asset-table-scroll" role="region" aria-label="术语管理真实记录表" tabIndex={0}>
          <table className="asset-table governance-table">
            <thead>
              <tr>
                <th>术语 / ID</th><th>领域</th><th>别名</th><th>定义类型</th><th>Evidence</th><th>规则关联</th><th>Phase2</th><th>操作</th>
              </tr>
            </thead>
            <tbody>
              {visible.map((row) => (
                <tr key={row.id}>
                  <td><strong>{row.name}</strong><small className="asset-id">{row.id}</small></td>
                  <td><span className="domain-label">{row.domain}</span></td>
                  <td className="secondary-cell">{row.aliases.join(" · ") || "—"}</td>
                  <td className="secondary-cell">{row.definition_kind || "未分类"}<small>{row.confidence}</small></td>
                  <td className="count-cell">{row.evidence.length}</td>
                  <td className="count-cell">{row.related_rule_ids.length}</td>
                  <td className="count-cell">{row.phase2_rule_ids.length}</td>
                  <td><button className="table-action" onClick={() => setSelected(row)}>详情 <Icon name="chevron" size={12} /></button></td>
                </tr>
              ))}
            </tbody>
          </table>
          {visible.length === 0 && (
            <div className="admin-empty-results"><Icon name="search" size={26} /><p>没有匹配的真实术语</p></div>
          )}
        </div>
        <div className="asset-table-footer">
          <span>共 {visible.length} / {records.length} 条</span>
          <span>内部只读 · 不返回来源章节正文</span>
        </div>
      </section>

      {selected && (
        <Dialog title="真实术语详情" onClose={() => setSelected(null)} className="admin-detail-dialog">
          <div className="governance-detail">
            <h3>{selected.name}</h3>
            <code>{selected.id}</code>
            <dl className="admin-detail-fields">
              <div><dt>领域</dt><dd>{selected.domain}</dd></div>
              <div><dt>置信度</dt><dd>{selected.confidence}</dd></div>
              <div><dt>定义类型</dt><dd>{selected.definition_kind || "未分类"}</dd></div>
              <div><dt>生产解释</dt><dd>{selected.production_interpretation === true ? "允许" : selected.production_interpretation === false ? "不允许自动解释" : "未声明"}</dd></div>
            </dl>
            <h4>术语定义</h4>
            <p>{selected.definition}</p>
            <h4>别名</h4>
            <p>{selected.aliases.join(" · ") || "无"}</p>
            <h4>来源定位</h4>
            {selected.evidence.length ? selected.evidence.map((item) => (
              <article className="governance-binding" key={item.section_id}>
                <strong>{item.classic_title} · {item.chapter_title}</strong>
                <span>{item.evidence_level}</span>
                <small>{item.locator}</small>
              </article>
            )) : <p>当前没有来源定位。</p>}
            <h4>关联术语</h4>
            <p>{selected.related_terms.join(" · ") || "无"}</p>
            <h4>关联规则</h4>
            <p>{selected.related_rule_ids.join(" · ") || "当前没有规则通过同一 Evidence 直接关联。"}</p>
            <h4>Phase2 关联</h4>
            <p>{selected.phase2_rule_ids.join(" · ") || "当前未关联 Phase2 executable。"}</p>
            <div className="module-gate">
              详情页不返回来源章节正文、Evidence 原文、RAW/Quarantine 文件内容或内部文件路径。
            </div>
          </div>
        </Dialog>
      )}

      <div className="asset-boundary-note">
        <Icon name="shield" size={18} />
        <div>
          <strong>术语治理与公开知识库严格分离</strong>
          <p>后台可查看真实术语定义与来源定位，公开前台仍然只能获得当前推演实际需要的结果与 Evidence。</p>
        </div>
      </div>
    </>
  );
}
