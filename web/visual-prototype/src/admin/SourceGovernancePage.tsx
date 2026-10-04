import { useEffect, useMemo, useState } from "react";
import type { FormEvent } from "react";
import { Icon } from "../shared/Icon";
import { Dialog } from "../shared/Dialog";
import { fetchAdminSources, type AdminSourceRecord } from "./adminApi";
import "./governance-assets.css";

const tokenKey = "tianji.admin.read.token.v1";

function readToken() {
  try {
    return sessionStorage.getItem(tokenKey) || "";
  } catch {
    return "";
  }
}

export function SourceGovernancePage() {
  const [token, setToken] = useState(readToken);
  const [records, setRecords] = useState<AdminSourceRecord[]>([]);
  const [connected, setConnected] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [query, setQuery] = useState("");
  const [domain, setDomain] = useState("全部领域");
  const [stage, setStage] = useState("全部等级");
  const [selected, setSelected] = useState<AdminSourceRecord | null>(null);

  async function load(nextToken: string) {
    if (!nextToken.trim()) {
      setError("请输入后台只读令牌。");
      return;
    }
    setLoading(true);
    setError("");
    try {
      setRecords(await fetchAdminSources(nextToken.trim()));
      setConnected(true);
      try {
        sessionStorage.setItem(tokenKey, nextToken.trim());
      } catch {
        /* session persistence is optional */
      }
    } catch (err) {
      setConnected(false);
      setRecords([]);
      setError(err instanceof Error ? err.message : "后台来源治理数据读取失败。");
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
    () => ["全部领域", ...Array.from(new Set(records.flatMap((row) => row.domains))).sort()],
    [records],
  );
  const stages = useMemo(
    () => ["全部等级", ...Array.from(new Set(records.map((row) => row.evidence_level))).sort()],
    [records],
  );
  const visible = useMemo(
    () =>
      records.filter(
        (row) =>
          (domain === "全部领域" || row.domains.includes(domain)) &&
          (stage === "全部等级" || row.evidence_level === stage) &&
          `${row.title} ${row.id} ${row.repository || ""} ${row.license || ""}`
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
            <h1>来源管理</h1>
            <p>真实读取已登记证据来源、固定版本、许可与审核边界；不返回内部文件路径。</p>
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
                未授权时页面不会请求任何真实来源资产。服务端令牌由
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
              {loading ? "正在验证…" : "读取真实来源"}
            </button>
          </form>
          {error && <p className="governance-auth-error" role="alert">{error}</p>}
          <div className="module-gate">
            接口只返回来源治理元数据与使用统计；正文、RAW/Quarantine 内容、content_path 和内部文件路径不会通过此页返回。
          </div>
        </section>
      </>
    );
  }

  const reviewedSections = records.reduce((sum, row) => sum + row.section_count, 0);
  const repositories = new Set(records.map((row) => row.repository).filter(Boolean)).size;

  return (
    <>
      <div className="admin-page-heading">
        <div>
          <h1>来源管理</h1>
          <p>真实证据来源、固定版本和权利边界；知识正文仍保持内部隔离。</p>
        </div>
        <div className="governance-heading-actions">
          <span className="admin-status success">真实数据 · 只读</span>
          <button className="table-action" onClick={disconnect}>结束会话</button>
        </div>
      </div>

      <div className="asset-summary">
        <div><span>真实来源</span><strong>{records.length}</strong></div>
        <div><span>当前筛选</span><strong>{visible.length}</strong></div>
        <div><span>审核选段</span><strong>{reviewedSections}</strong></div>
        <div><span>上游仓库</span><strong>{repositories}</strong></div>
      </div>

      <section className="admin-card governance-asset-card">
        <div className="asset-toolbar">
          <div className="asset-search">
            <Icon name="search" size={17} />
            <input
              aria-label="搜索来源管理"
              value={query}
              onChange={(event) => setQuery(event.target.value)}
              placeholder="搜索来源、ID、仓库或许可"
            />
          </div>
          <div className="asset-filters">
            <select aria-label="领域筛选" value={domain} onChange={(event) => setDomain(event.target.value)}>
              {domains.map((item) => <option key={item}>{item}</option>)}
            </select>
            <select aria-label="Evidence 等级筛选" value={stage} onChange={(event) => setStage(event.target.value)}>
              {stages.map((item) => <option key={item}>{item}</option>)}
            </select>
          </div>
        </div>

        <div className="asset-table-scroll" role="region" aria-label="来源管理真实记录表" tabIndex={0}>
          <table className="asset-table governance-table">
            <thead>
              <tr>
                <th>来源 / ID</th><th>领域</th><th>类型 / 等级</th><th>许可</th><th>书目</th><th>审核选段</th><th>引用实体</th><th>操作</th>
              </tr>
            </thead>
            <tbody>
              {visible.map((row) => (
                <tr key={row.id}>
                  <td><strong>{row.title}</strong><small className="asset-id">{row.id}</small></td>
                  <td className="secondary-cell">{row.domains.join(" · ") || "—"}</td>
                  <td className="secondary-cell">{row.kind}<small>{row.evidence_level}</small></td>
                  <td className="secondary-cell">{row.license || "未登记"}<small>{row.public_domain === true ? "Public Domain" : row.public_domain === false ? "非公版" : "未声明"}</small></td>
                  <td className="count-cell">{row.classic_ids.length}</td>
                  <td className="count-cell">{row.section_count}</td>
                  <td className="count-cell">{row.entity_count}</td>
                  <td><button className="table-action" onClick={() => setSelected(row)}>详情 <Icon name="chevron" size={12} /></button></td>
                </tr>
              ))}
            </tbody>
          </table>
          {visible.length === 0 && (
            <div className="admin-empty-results"><Icon name="search" size={26} /><p>没有匹配的真实来源</p></div>
          )}
        </div>
        <div className="asset-table-footer">
          <span>共 {visible.length} / {records.length} 条</span>
          <span>内部只读 · 不返回正文与内部路径</span>
        </div>
      </section>

      {selected && (
        <Dialog title="真实来源详情" onClose={() => setSelected(null)} className="admin-detail-dialog">
          <div className="governance-detail">
            <h3>{selected.title}</h3>
            <code>{selected.id}</code>
            <dl className="admin-detail-fields">
              <div><dt>Evidence 等级</dt><dd>{selected.evidence_level}</dd></div>
              <div><dt>类型</dt><dd>{selected.kind}</dd></div>
              <div><dt>许可</dt><dd>{selected.license || "未登记"}</dd></div>
              <div><dt>公版标记</dt><dd>{selected.public_domain === true ? "是" : selected.public_domain === false ? "否" : "未声明"}</dd></div>
              <div><dt>抓取日期</dt><dd>{selected.retrieved_at || "未登记"}</dd></div>
              <div><dt>使用选段</dt><dd>{selected.section_count}</dd></div>
            </dl>
            <h4>上游与固定版本</h4>
            <p>{selected.repository || "未登记仓库"} · <code>{selected.commit}</code></p>
            <p>{selected.author || "作者未确证"} · {selected.era || "时代未登记"}</p>
            <h4>权利边界</h4>
            <p>{selected.rights_basis || "未登记额外权利说明。"}</p>
            <h4>审核范围</h4>
            <p>{selected.review_scope || "未登记额外审核范围。"}</p>
            <h4>领域</h4>
            <p>{selected.domains.join(" · ") || "当前未绑定领域。"}</p>
            <h4>关联书目 / 章节</h4>
            <p>{selected.classic_ids.join(" · ") || "无书目关联。"}</p>
            <p>{selected.chapter_ids.join(" · ") || "无章节关联。"}</p>
            <div className="module-gate">
              详情页不返回来源正文、RAW/Quarantine 文件内容、content_path、sha256 或内部文件路径。
            </div>
          </div>
        </Dialog>
      )}

      <div className="asset-boundary-note">
        <Icon name="shield" size={18} />
        <div>
          <strong>来源治理与公开产品严格分离</strong>
          <p>后台可看真实来源、固定版本、许可与审核边界；公开前台不提供来源库浏览。</p>
        </div>
      </div>
    </>
  );
}
