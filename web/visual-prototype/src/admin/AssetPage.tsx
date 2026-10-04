import { useCallback, useMemo, useState } from "react";
import { Icon } from "../shared/Icon";
import { Dialog } from "../shared/Dialog";
import { assets } from "./fixtures";
import type { AssetKind, AssetRecord } from "./fixtures";

const definitions = {
  classics: {
    title: "古籍管理",
    description: "管理书目、章节关联与可发布内容范围。",
    item: "典籍",
    name: "典籍 / 记录",
    extra: "章节范围",
    count: "章节数量",
  },
  rules: {
    title: "规则管理",
    description: "区分计算规则、解释规则及其流派与执行范围。",
    item: "规则",
    name: "规则名称",
    extra: "流派 / 约定",
    count: "关联证据",
  },
  evidence: {
    title: "Evidence 管理",
    description: "核对原文片段、出处、证据等级与规则关联。",
    item: "Evidence",
    name: "必要片段 / 记录",
    extra: "典籍 / 章节",
    count: "对应规则",
  },
};
function tone(state: string) {
  return state === "隔离"
    ? "danger"
    : state === "仅研究" || state === "实现依据"
      ? "warning"
      : state.startsWith("已审") || state === "示例可执行"
        ? "success"
        : "neutral";
}
export function AssetPage({ kind }: { kind: AssetKind }) {
  const def = definitions[kind];
  const [query, setQuery] = useState("");
  const [domain, setDomain] = useState("全部领域");
  const [state, setState] = useState("全部状态");
  const [selected, setSelected] = useState<AssetRecord | null>(null);
  const close = useCallback(() => setSelected(null), []);
  const rows = useMemo(
    () =>
      assets[kind].filter(
        (row) =>
          (domain === "全部领域" || row.domain === domain) &&
          (state === "全部状态" || row.state === state) &&
          `${row.name} ${row.id} ${row.secondary} ${row.count}`
            .toLowerCase()
            .includes(query.toLowerCase().trim()),
      ),
    [kind, domain, state, query],
  );
  return (
    <>
      <div className="admin-page-heading">
        <div>
          <h1>{def.title}</h1>
          <p>{def.description}</p>
        </div>
        <span className="admin-readonly">
          <Icon name="shield" size={15} />
          静态示例 · 只读
        </span>
      </div>
      <div className="asset-summary">
        <div>
          <span>展示记录</span>
          <strong>6</strong>
        </div>
        <div>
          <span>已审 / 可执行示例</span>
          <strong>
            {assets[kind].filter((r) => tone(r.state) === "success").length}
          </strong>
        </div>
        <div>
          <span>需关注记录</span>
          <strong>
            {assets[kind].filter((r) => tone(r.state) !== "success").length}
          </strong>
        </div>
        <div>
          <span>生产发布</span>
          <strong className="summary-text">未连接</strong>
        </div>
      </div>
      <section className="admin-card asset-card">
        <div className="asset-toolbar">
          <div className="asset-search">
            <Icon name="search" size={17} />
            <input
              aria-label={`搜索${def.item}`}
              placeholder={`搜索${def.item}名称、编号或关联内容`}
              value={query}
              onChange={(e) => setQuery(e.target.value)}
            />
          </div>
          <div className="asset-filters">
            <label>
              <span className="sr-only">领域筛选</span>
              <select
                aria-label="领域筛选"
                value={domain}
                onChange={(e) => setDomain(e.target.value)}
              >
                {[
                  "全部领域",
                  ...new Set(assets[kind].map((r) => r.domain)),
                ].map((item) => (
                  <option key={item}>{item}</option>
                ))}
              </select>
            </label>
            <label>
              <span className="sr-only">状态筛选</span>
              <select
                aria-label="状态筛选"
                value={state}
                onChange={(e) => setState(e.target.value)}
              >
                {["全部状态", ...new Set(assets[kind].map((r) => r.state))].map(
                  (item) => (
                    <option key={item}>{item}</option>
                  ),
                )}
              </select>
            </label>
          </div>
        </div>
        <p className="asset-scroll-hint">
          <Icon name="arrow" size={13} />
          左右滑动表格，查看等级、状态与详情
        </p>
        <div
          className="asset-table-scroll"
          role="region"
          aria-label={`${def.title}表格，可横向滚动`}
          tabIndex={0}
        >
          <table className="asset-table">
            <thead>
              <tr>
                <th>{def.name}</th>
                <th>领域</th>
                <th>{def.extra}</th>
                <th>{def.count}</th>
                <th>等级</th>
                <th>审核状态</th>
                <th>更新时间</th>
                <th>操作</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((row) => (
                <tr key={row.id}>
                  <td>
                    <button
                      className="asset-name"
                      onClick={() => setSelected(row)}
                    >
                      {row.name}
                    </button>
                    <small className="asset-id">{row.id}</small>
                  </td>
                  <td>
                    <span className="domain-label">{row.domain}</span>
                  </td>
                  <td className="secondary-cell">{row.secondary}</td>
                  <td className="count-cell">{row.count}</td>
                  <td>
                    <span className={`level-tag level-${row.level}`}>
                      {row.level}
                    </span>
                  </td>
                  <td>
                    <span className={`admin-status ${tone(row.state)}`}>
                      {row.state}
                    </span>
                  </td>
                  <td className="date-cell">{row.updated}</td>
                  <td>
                    <button
                      className="table-action"
                      onClick={() => setSelected(row)}
                    >
                      详情
                      <Icon name="chevron" size={12} />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          {rows.length === 0 && (
            <div className="admin-empty-results">
              <Icon name="search" size={26} />
              <p>没有匹配的示例记录</p>
              <button
                className="admin-button"
                onClick={() => {
                  setQuery("");
                  setDomain("全部领域");
                  setState("全部状态");
                }}
              >
                清除筛选
              </button>
            </div>
          )}
        </div>
        <div className="asset-table-footer">
          <span>共 {rows.length} 条静态示例</span>
          <span>仅此页 · 无数据写入</span>
        </div>
      </section>
      <div className="asset-boundary-note">
        <Icon name="shield" size={18} />
        <div>
          <strong>
            {kind === "evidence"
              ? "证据等级不等于发布许可"
              : kind === "rules"
                ? "规则类型与执行范围必须分别审核"
                : "已审选段不等于整本古籍可以发布"}
          </strong>
          <p>
            所有记录均为视觉示例。RAW / Quarantine 不自动进入 Canonical；C/D
            等级不得伪造升级。前台不会通过此表浏览全量内部资产。
          </p>
        </div>
      </div>
      {selected && (
        <Dialog
          title={`${def.item}详情`}
          onClose={close}
          className="admin-detail-dialog"
        >
          <div className="admin-detail-title">
            <h3>{selected.name}</h3>
            <span className={`admin-status ${tone(selected.state)}`}>
              {selected.state}
            </span>
          </div>
          <dl className="admin-detail-fields">
            <div>
              <dt>编号</dt>
              <dd>{selected.id}</dd>
            </div>
            <div>
              <dt>领域</dt>
              <dd>{selected.domain}</dd>
            </div>
            <div>
              <dt>等级</dt>
              <dd>
                {selected.level} ·{" "}
                {selected.level === "C"
                  ? "单一可追溯来源示意"
                  : "实现或待复核依据示意"}
              </dd>
            </div>
            <div>
              <dt>{def.extra}</dt>
              <dd>{selected.secondary}</dd>
            </div>
            <div>
              <dt>{def.count}</dt>
              <dd>{selected.count}</dd>
            </div>
          </dl>
          <p>{selected.detail}</p>
          <div className="admin-detail-warning">
            <Icon name="shield" size={17} />
            仅展示字段与审核层级。本轮不提供编辑、导入、删除或晋级操作。
          </div>
        </Dialog>
      )}
    </>
  );
}
