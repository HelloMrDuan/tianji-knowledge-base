import { useEffect, useMemo, useState } from "react";
import type { FormEvent } from "react";
import { Icon } from "../shared/Icon";
import { Dialog } from "../shared/Dialog";
import { fetchAdminEvaluations, type AdminEvaluationRecord } from "./adminApi";
import "./governance-assets.css";

const tokenKey = "tianji.admin.read.token.v1";

function readToken() {
  try {
    return sessionStorage.getItem(tokenKey) || "";
  } catch {
    return "";
  }
}

export function EvaluationGovernancePage() {
  const [token, setToken] = useState(readToken);
  const [records, setRecords] = useState<AdminEvaluationRecord[]>([]);
  const [connected, setConnected] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [selected, setSelected] = useState<AdminEvaluationRecord | null>(null);

  async function load(nextToken: string) {
    if (!nextToken.trim()) {
      setError("请输入后台只读令牌。");
      return;
    }
    setLoading(true);
    setError("");
    try {
      setRecords(await fetchAdminEvaluations(nextToken.trim()));
      setConnected(true);
      try {
        sessionStorage.setItem(tokenKey, nextToken.trim());
      } catch {
        /* session persistence is optional */
      }
    } catch (err) {
      setConnected(false);
      setRecords([]);
      setError(err instanceof Error ? err.message : "评测治理数据读取失败。");
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

  const totals = useMemo(
    () => ({
      evalCases: records.reduce((sum, row) => sum + row.eval_case_count, 0),
      goldenCases: records.reduce((sum, row) => sum + row.phase2_golden_count, 0),
      refusalControls: records.reduce((sum, row) => sum + row.refusal_control_count, 0),
      coveredDomains: records.filter((row) => row.eval_case_count > 0).length,
    }),
    [records],
  );

  if (!connected) {
    return (
      <>
        <div className="admin-page-heading">
          <div>
            <h1>Eval / Golden Cases</h1>
            <p>读取真实固定评测集与 Golden Case 覆盖；没有真实模型评测结果时不会伪造通过分数。</p>
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
                未授权时页面不会请求内部评测 Case ID、Golden Case 或基线信息。服务端令牌由
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
              {loading ? "正在验证…" : "读取真实评测资产"}
            </button>
          </form>
          {error && <p className="governance-auth-error" role="alert">{error}</p>}
          <div className="module-gate">
            本页展示的是已提交的 fixture 与 Golden Case，不把 dry-run、测试 Provider 或未运行模型伪装成真实质量评分。
          </div>
        </section>
      </>
    );
  }

  return (
    <>
      <div className="admin-page-heading">
        <div>
          <h1>Eval / Golden Cases</h1>
          <p>真实固定 suite、Golden Case、拒绝控制与确定性引擎基线。</p>
        </div>
        <div className="governance-heading-actions">
          <span className="admin-status warning">fixture_only · 未上线就绪</span>
          <button className="table-action" onClick={disconnect}>结束会话</button>
        </div>
      </div>

      <div className="asset-summary">
        <div><span>Eval Cases</span><strong>{totals.evalCases}</strong></div>
        <div><span>Golden Cases</span><strong>{totals.goldenCases}</strong></div>
        <div><span>拒绝控制</span><strong>{totals.refusalControls}</strong></div>
        <div><span>Suite 覆盖域</span><strong>{totals.coveredDomains}</strong></div>
      </div>

      <section className="admin-card governance-asset-card">
        <div className="admin-card-heading">
          <div>
            <h2>领域评测覆盖</h2>
            <p>真实模型质量与人工语义复核尚未验证时，状态始终保持 fixture_only。</p>
          </div>
          <span className="admin-small-muted">{records[0]?.suite_id || "无 suite"}</span>
        </div>
        <div className="asset-table-scroll" role="region" aria-label="真实评测覆盖表" tabIndex={0}>
          <table className="asset-table governance-table">
            <thead>
              <tr>
                <th>领域</th><th>Variant</th><th>Eval</th><th>解释 Case</th><th>拒绝控制</th><th>Golden</th><th>真实模型</th><th>操作</th>
              </tr>
            </thead>
            <tbody>
              {records.map((row) => (
                <tr key={row.id}>
                  <td><strong>{row.domain}</strong><small className="asset-id">{row.tracked_status}</small></td>
                  <td className="secondary-cell">{row.variants.join(" · ") || "—"}</td>
                  <td className="count-cell">{row.eval_case_count}</td>
                  <td className="count-cell">{row.explanation_case_count}</td>
                  <td className="count-cell">{row.refusal_control_count}</td>
                  <td className="count-cell">{row.phase2_golden_count}</td>
                  <td><span className="admin-status warning">{row.live_model_quality_verified ? "已验证" : "未验证"}</span></td>
                  <td><button className="table-action" onClick={() => setSelected(row)}>详情 <Icon name="chevron" size={12} /></button></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <div className="asset-table-footer">
          <span>共 {records.length} 个领域记录</span>
          <span>自动发布：禁止</span>
        </div>
      </section>

      {selected && (
        <Dialog title="真实评测资产详情" onClose={() => setSelected(null)} className="admin-detail-dialog">
          <div className="governance-detail">
            <h3>{selected.domain}</h3>
            <code>{selected.suite_id || "未进入 explanation suite"}</code>
            <dl className="admin-detail-fields">
              <div><dt>Eval Cases</dt><dd>{selected.eval_case_count}</dd></div>
              <div><dt>解释 Case</dt><dd>{selected.explanation_case_count}</dd></div>
              <div><dt>拒绝控制</dt><dd>{selected.refusal_control_count}</dd></div>
              <div><dt>Suite Golden 引用</dt><dd>{selected.suite_golden_ref_count}</dd></div>
              <div><dt>Phase2 Golden</dt><dd>{selected.phase2_golden_count}</dd></div>
              <div><dt>Engine Baseline 文件</dt><dd>{selected.engine_baseline_file_count}</dd></div>
            </dl>
            <h4>Variant</h4>
            <p>{selected.variants.join(" · ") || "无"}</p>
            <h4>Golden Case IDs</h4>
            <p>{selected.phase2_golden_ids.join(" · ") || "当前无 Phase2 Golden Case。"}</p>
            <h4>Eval Case IDs</h4>
            <p>{selected.eval_case_ids.join(" · ") || "当前未进入固定 explanation suite。"}</p>
            <h4>Tags</h4>
            <p>{Object.entries(selected.tag_counts).map(([tag, count]) => `${tag}:${count}`).join(" · ") || "无"}</p>
            <h4>Engine Baseline</h4>
            <p><code>{selected.engine_baseline_main_sha}</code></p>
            <div className="module-gate">
              人工语义复核：{selected.human_semantic_review_required ? "必须" : "否"} · 在线就绪：{selected.online_ready ? "是" : "否"} · 自动发布：{selected.automatic_release_allowed ? "允许" : "禁止"}
            </div>
          </div>
        </Dialog>
      )}

      <div className="asset-boundary-note">
        <Icon name="shield" size={18} />
        <div>
          <strong>Fixture 完整不等于真实模型通过</strong>
          <p>只有真实配置模型在同一固定 suite 上完成运行，并经过完整人工语义复核，才有资格讨论 supervised beta；本页当前不提供虚构分数。</p>
        </div>
      </div>
    </>
  );
}
