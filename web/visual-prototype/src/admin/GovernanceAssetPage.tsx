import { useEffect, useMemo, useState } from "react";
import type { FormEvent } from "react";
import { Icon } from "../shared/Icon";
import { Dialog } from "../shared/Dialog";
import {
  fetchAdminEvidence,
  fetchAdminRules,
  type AdminEvidenceRecord,
  type AdminRuleRecord,
} from "./adminApi";
import "./governance-assets.css";

const tokenKey = "tianji.admin.read.token.v1";
type GovernanceKind = "rules" | "evidence";

function readToken() {
  try {
    return sessionStorage.getItem(tokenKey) || "";
  } catch {
    return "";
  }
}

export function GovernanceAssetPage({ kind }: { kind: GovernanceKind }) {
  const [token, setToken] = useState(readToken);
  const [rules, setRules] = useState<AdminRuleRecord[]>([]);
  const [evidence, setEvidence] = useState<AdminEvidenceRecord[]>([]);
  const [connected, setConnected] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [query, setQuery] = useState("");
  const [domain, setDomain] = useState("全部领域");
  const [selectedRule, setSelectedRule] = useState<AdminRuleRecord | null>(null);
  const [selectedEvidence, setSelectedEvidence] = useState<AdminEvidenceRecord | null>(null);

  async function load(nextToken: string) {
    if (!nextToken.trim()) {
      setError("请输入后台只读令牌。");
      return;
    }
    setLoading(true);
    setError("");
    try {
      if (kind === "rules") {
        setRules(await fetchAdminRules(nextToken.trim()));
        setEvidence([]);
      } else {
        setEvidence(await fetchAdminEvidence(nextToken.trim()));
        setRules([]);
      }
      setConnected(true);
      try {
        sessionStorage.setItem(tokenKey, nextToken.trim());
      } catch {
        /* session persistence is optional */
      }
    } catch (err) {
      setConnected(false);
      setRules([]);
      setEvidence([]);
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
    // Only restore the explicit token from this browser session once.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [kind]);

  function submit(event: FormEvent) {
    event.preventDefault();
    void load(token);
  }

  function disconnect() {
    setConnected(false);
    setToken("");
    setRules([]);
    setEvidence([]);
    setError("");
    try {
      sessionStorage.removeItem(tokenKey);
    } catch {
      /* ignore */
    }
  }

  const domains = useMemo(() => {
    const rows = kind === "rules" ? rules : evidence;
    return ["全部领域", ...Array.from(new Set(rows.map((row) => row.domain))).sort()];
  }, [kind, rules, evidence]);

  const visibleRules = useMemo(
    () =>
      rules.filter(
        (row) =>
          (domain === "全部领域" || row.domain === domain) &&
          `${row.name} ${row.id} ${row.school} ${row.variant}`
            .toLowerCase()
            .includes(query.trim().toLowerCase()),
      ),
    [rules, domain, query],
  );

  const visibleEvidence = useMemo(
    () =>
      evidence.filter(
        (row) =>
          (domain === "全部领域" || row.domain === domain) &&
          `${row.name} ${row.id} ${row.classic_title} ${row.chapter_title} ${row.original_text}`
            .toLowerCase()
            .includes(query.trim().toLowerCase()),
      ),
    [evidence, domain, query],
  );

  const title = kind === "rules" ? "规则管理" : "Evidence 管理";
  const description =
    kind === "rules"
      ? "真实读取 Canonical 规则、Phase2 绑定、Golden Case 与审核 Evidence。"
      : "真实读取已审核 Canonical 短引、出处与规则关联；不提供完整古籍浏览。";

  if (!connected) {
    return (
      <>
        <div className="admin-page-heading">
          <div>
            <h1>{title}</h1>
            <p>{description}</p>
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
                未授权时页面不会请求任何真实规则或 Evidence。服务端令牌由
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
              {loading ? "正在验证…" : `读取真实${kind === "rules" ? "规则" : " Evidence"}`}
            </button>
          </form>
          {error && <p className="governance-auth-error" role="alert">{error}</p>}
          <div className="module-gate">
            只读接口仅返回 Canonical 结构和已审核短引；RAW / Quarantine / 完整书体不会通过此页返回。
          </div>
        </section>
      </>
    );
  }

  const total = kind === "rules" ? rules.length : evidence.length;
  const visible = kind === "rules" ? visibleRules.length : visibleEvidence.length;
  const productionBindings =
    kind === "rules"
      ? rules.reduce((sum, row) => sum + row.phase2_bindings.length, 0)
      : evidence.reduce((sum, row) => sum + row.phase2_rule_ids.length, 0);

  return (
    <>
      <div className="admin-page-heading">
        <div>
          <h1>{title}</h1>
          <p>{description}</p>
        </div>
        <div className="governance-heading-actions">
          <span className="admin-status success">真实数据 · 只读</span>
          <button className="table-action" onClick={disconnect}>结束会话</button>
        </div>
      </div>

      <div className="asset-summary">
        <div><span>真实记录</span><strong>{total}</strong></div>
        <div><span>当前筛选</span><strong>{visible}</strong></div>
        <div><span>Phase2 关联</span><strong>{productionBindings}</strong></div>
        <div><span>公开前台</span><strong className="summary-text">不开放</strong></div>
      </div>

      <section className="admin-card governance-asset-card">
        <div className="asset-toolbar">
          <div className="asset-search">
            <Icon name="search" size={17} />
            <input
              aria-label={`搜索${title}`}
              value={query}
              onChange={(event) => setQuery(event.target.value)}
              placeholder={kind === "rules" ? "搜索规则、编号、流派或 Variant" : "搜索短引、典籍、章节或编号"}
            />
          </div>
          <div className="asset-filters">
            <select aria-label="领域筛选" value={domain} onChange={(event) => setDomain(event.target.value)}>
              {domains.map((item) => <option key={item}>{item}</option>)}
            </select>
          </div>
        </div>

        <div className="asset-table-scroll" role="region" aria-label={`${title}真实记录表`} tabIndex={0}>
          {kind === "rules" ? (
            <table className="asset-table governance-table">
              <thead>
                <tr>
                  <th>规则 / ID</th><th>领域</th><th>流派 / Variant</th><th>Phase2</th><th>Evidence</th><th>状态</th><th>操作</th>
                </tr>
              </thead>
              <tbody>
                {visibleRules.map((row) => (
                  <tr key={row.id}>
                    <td><strong>{row.name}</strong><small className="asset-id">{row.id}</small></td>
                    <td><span className="domain-label">{row.domain}</span></td>
                    <td className="secondary-cell">{row.school}<small>{row.variant}</small></td>
                    <td className="count-cell">{row.phase2_bindings.length}</td>
                    <td className="count-cell">{row.evidence.length}</td>
                    <td><span className="admin-status success">{row.execution_status}</span></td>
                    <td><button className="table-action" onClick={() => setSelectedRule(row)}>详情 <Icon name="chevron" size={12} /></button></td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <table className="asset-table governance-table">
              <thead>
                <tr>
                  <th>Evidence / ID</th><th>领域</th><th>典籍 / 章节</th><th>等级</th><th>实体引用</th><th>Phase2</th><th>操作</th>
                </tr>
              </thead>
              <tbody>
                {visibleEvidence.map((row) => (
                  <tr key={row.id}>
                    <td><strong>{row.name}</strong><small className="asset-id">{row.id}</small></td>
                    <td><span className="domain-label">{row.domain}</span></td>
                    <td className="secondary-cell">{row.classic_title}<small>{row.chapter_title}</small></td>
                    <td><span className={`level-tag level-${row.evidence_level}`}>{row.evidence_level}</span></td>
                    <td className="count-cell">{row.used_by_entity_ids.length}</td>
                    <td className="count-cell">{row.phase2_rule_ids.length}</td>
                    <td><button className="table-action" onClick={() => setSelectedEvidence(row)}>详情 <Icon name="chevron" size={12} /></button></td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
          {visible === 0 && <div className="admin-empty-results"><Icon name="search" size={26} /><p>没有匹配的真实记录</p></div>}
        </div>
        <div className="asset-table-footer">
          <span>共 {visible} / {total} 条</span>
          <span>内部只读 · Canonical</span>
        </div>
      </section>

      {selectedRule && (
        <Dialog title="真实规则详情" onClose={() => setSelectedRule(null)} className="admin-detail-dialog">
          <div className="governance-detail">
            <h3>{selectedRule.name}</h3>
            <code>{selectedRule.id}</code>
            <dl className="admin-detail-fields">
              <div><dt>领域</dt><dd>{selectedRule.domain}</dd></div>
              <div><dt>流派</dt><dd>{selectedRule.school}</dd></div>
              <div><dt>Variant</dt><dd>{selectedRule.variant}</dd></div>
              <div><dt>Phase2 绑定</dt><dd>{selectedRule.phase2_bindings.length}</dd></div>
            </dl>
            <p>{selectedRule.difference}</p>
            <h4>执行边界</h4>
            {selectedRule.exceptions.map((item) => <p key={item} className="governance-limit">{item}</p>)}
            <h4>Phase2 / Golden</h4>
            {selectedRule.phase2_bindings.length ? selectedRule.phase2_bindings.map((item) => (
              <article className="governance-binding" key={item.id}>
                <strong>{item.id}</strong><span>{item.validation_status}</span>
                <small>{item.golden_case_ids.join(" · ") || "无 Golden Case"}</small>
              </article>
            )) : <p>当前未绑定 Phase2 executable。</p>}
            <h4>已审核 Evidence</h4>
            {selectedRule.evidence.map((item) => (
              <blockquote key={item.section_id}>{item.original_text}<small>{item.classic_title} · {item.locator} · {item.evidence_level}</small></blockquote>
            ))}
          </div>
        </Dialog>
      )}

      {selectedEvidence && (
        <Dialog title="真实 Evidence 详情" onClose={() => setSelectedEvidence(null)} className="admin-detail-dialog">
          <div className="governance-detail">
            <h3>{selectedEvidence.name}</h3>
            <code>{selectedEvidence.id}</code>
            <dl className="admin-detail-fields">
              <div><dt>领域</dt><dd>{selectedEvidence.domain}</dd></div>
              <div><dt>等级</dt><dd>{selectedEvidence.evidence_level}</dd></div>
              <div><dt>典籍</dt><dd>{selectedEvidence.classic_title}</dd></div>
              <div><dt>章节</dt><dd>{selectedEvidence.chapter_title}</dd></div>
            </dl>
            <p>{selectedEvidence.locator}</p>
            <blockquote>{selectedEvidence.original_text}</blockquote>
            <h4>审核范围</h4>
            <p>{selectedEvidence.review.scope}</p>
            <h4>关联实体</h4>
            <p>{selectedEvidence.used_by_entity_ids.join(" · ") || "当前无引用"}</p>
            <h4>Phase2 规则</h4>
            <p>{selectedEvidence.phase2_rule_ids.join(" · ") || "当前未进入 Phase2"}</p>
          </div>
        </Dialog>
      )}

      <div className="asset-boundary-note">
        <Icon name="shield" size={18} />
        <div>
          <strong>真实后台不等于公开知识库</strong>
          <p>这些记录只供内部治理；公开前台仍然只能获得本次推演命中的必要 Evidence。</p>
        </div>
      </div>
    </>
  );
}
