import { useEffect, useMemo, useState } from "react";
import type { FormEvent } from "react";
import { Icon } from "../shared/Icon";
import { Dialog } from "../shared/Dialog";
import { fetchAdminChapters, type AdminChapterRecord } from "./adminApi";
import "./governance-assets.css";

const tokenKey = "tianji.admin.read.token.v1";

function readToken() {
  try {
    return sessionStorage.getItem(tokenKey) || "";
  } catch {
    return "";
  }
}

export function ChapterGovernancePage() {
  const [token, setToken] = useState(readToken);
  const [records, setRecords] = useState<AdminChapterRecord[]>([]);
  const [connected, setConnected] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [query, setQuery] = useState("");
  const [domain, setDomain] = useState("全部领域");
  const [stage, setStage] = useState("全部状态");
  const [selected, setSelected] = useState<AdminChapterRecord | null>(null);

  async function load(nextToken: string) {
    if (!nextToken.trim()) {
      setError("请输入后台只读令牌。");
      return;
    }
    setLoading(true);
    setError("");
    try {
      setRecords(await fetchAdminChapters(nextToken.trim()));
      setConnected(true);
      try {
        sessionStorage.setItem(tokenKey, nextToken.trim());
      } catch {
        /* session persistence is optional */
      }
    } catch (err) {
      setConnected(false);
      setRecords([]);
      setError(err instanceof Error ? err.message : "后台章节治理数据读取失败。");
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
    () => ["全部状态", ...Array.from(new Set(records.map((row) => row.body_stage))).sort()],
    [records],
  );
  const visible = useMemo(
    () =>
      records.filter(
        (row) =>
          (domain === "全部领域" || row.domain === domain) &&
          (stage === "全部状态" || row.body_stage === stage) &&
          `${row.name} ${row.id} ${row.classic_title} ${row.locator} ${row.source_title}`
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
            <h1>章节管理</h1>
            <p>真实读取 Canonical 章节元数据与审核覆盖；不返回章节正文。</p>
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
                未授权时页面不会请求任何真实章节资产。服务端令牌由
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
              {loading ? "正在验证…" : "读取真实章节"}
            </button>
          </form>
          {error && <p className="governance-auth-error" role="alert">{error}</p>}
          <div className="module-gate">
            接口只返回章节名称、定位、所属书目、审核覆盖和关联 ID；章节正文、RAW、Quarantine 文件与内部路径不会通过此页返回。
          </div>
        </section>
      </>
    );
  }

  const reviewedSections = records.reduce((sum, row) => sum + row.reviewed_section_count, 0);
  const phase2Rules = new Set(records.flatMap((row) => row.phase2_rule_ids)).size;

  return (
    <>
      <div className="admin-page-heading">
        <div>
          <h1>章节管理</h1>
          <p>真实 Canonical 章节治理元数据；完整章节正文仍保持内部隔离。</p>
        </div>
        <div className="governance-heading-actions">
          <span className="admin-status success">真实数据 · 只读</span>
          <button className="table-action" onClick={disconnect}>结束会话</button>
        </div>
      </div>

      <div className="asset-summary">
        <div><span>真实章节</span><strong>{records.length}</strong></div>
        <div><span>当前筛选</span><strong>{visible.length}</strong></div>
        <div><span>审核短引</span><strong>{reviewedSections}</strong></div>
        <div><span>Phase2 关联</span><strong>{phase2Rules}</strong></div>
      </div>

      <section className="admin-card governance-asset-card">
        <div className="asset-toolbar">
          <div className="asset-search">
            <Icon name="search" size={17} />
            <input
              aria-label="搜索古籍管理"
              value={query}
              onChange={(event) => setQuery(event.target.value)}
              placeholder="搜索章节、ID、书目或定位"
            />
          </div>
          <div className="asset-filters">
            <select aria-label="领域筛选" value={domain} onChange={(event) => setDomain(event.target.value)}>
              {domains.map((item) => <option key={item}>{item}</option>)}
            </select>
            <select aria-label="状态筛选" value={stage} onChange={(event) => setStage(event.target.value)}>
              {stages.map((item) => <option key={item}>{item}</option>)}
            </select>
          </div>
        </div>

        <div className="asset-table-scroll" role="region" aria-label="章节管理真实记录表" tabIndex={0}>
          <table className="asset-table governance-table">
            <thead>
              <tr>
                <th>章节 / ID</th><th>领域</th><th>所属书目</th><th>来源 / 等级</th><th>审核短引</th><th>实体引用</th><th>Phase2</th><th>操作</th>
              </tr>
            </thead>
            <tbody>
              {visible.map((row) => (
                <tr key={row.id}>
                  <td><strong>{row.name}</strong><small className="asset-id">{row.id}</small></td>
                  <td><span className="domain-label">{row.domain}</span></td>
                  <td className="secondary-cell">{row.classic_title}<small>{row.body_stage}</small></td>
                  <td className="secondary-cell">{row.source_title}<small>{row.evidence_level} · {row.source_id}</small></td>
                  <td className="count-cell">{row.reviewed_section_count}</td>
                  <td className="count-cell">{row.used_by_entity_ids.length}</td>
                  <td className="count-cell">{row.phase2_rule_ids.length}</td>
                  <td><button className="table-action" onClick={() => setSelected(row)}>详情 <Icon name="chevron" size={12} /></button></td>
                </tr>
              ))}
            </tbody>
          </table>
          {visible.length === 0 && (
            <div className="admin-empty-results"><Icon name="search" size={26} /><p>没有匹配的真实章节</p></div>
          )}
        </div>
        <div className="asset-table-footer">
          <span>共 {visible.length} / {records.length} 条</span>
          <span>内部只读 · 不返回章节正文</span>
        </div>
      </section>

      {selected && (
        <Dialog title="真实章节详情" onClose={() => setSelected(null)} className="admin-detail-dialog">
          <div className="governance-detail">
            <h3>{selected.name}</h3>
            <code>{selected.id}</code>
            <dl className="admin-detail-fields">
              <div><dt>领域</dt><dd>{selected.domain}</dd></div>
              <div><dt>Body Stage</dt><dd>{selected.body_stage}</dd></div>
              <div><dt>Evidence 等级</dt><dd>{selected.evidence_level}</dd></div>
              <div><dt>审核短引</dt><dd>{selected.reviewed_section_count}</dd></div>
            </dl>
            <h4>来源</h4>
            <p>{selected.source_title} · {selected.source_id}</p>
            <p>固定提交：<code>{selected.commit}</code></p>
            <h4>审核范围</h4>
            <p>{selected.review_scope || "当前来源未登记额外审核说明。"}</p>
            <h4>权利边界</h4>
            <p>{selected.rights_basis || "按来源登记策略处理。"}</p>
            <h4>章节定位</h4>
            <p>{selected.locator || "当前章节未登记额外 locator。"}</p>
            <h4>关联实体</h4>
            <p>{selected.used_by_entity_ids.join(" · ") || "当前没有规则、术语或概念引用。"}</p>
            <h4>Phase2 关联</h4>
            <p>{selected.phase2_rule_ids.join(" · ") || "当前未进入 Phase2 executable。"}</p>
            <div className="module-gate">
              详情页不返回章节正文、审核短引正文、RAW/Quarantine 文件内容或内部文件路径。
            </div>
          </div>
        </Dialog>
      )}

      <div className="asset-boundary-note">
        <Icon name="shield" size={18} />
        <div>
          <strong>章节治理与公开阅读严格分离</strong>
          <p>后台可看真实章节元数据与审核覆盖，公开前台仍然只能获得当前推演实际命中的必要 Evidence。</p>
        </div>
      </div>
    </>
  );
}
