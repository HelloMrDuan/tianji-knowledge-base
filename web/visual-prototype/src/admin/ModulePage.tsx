import { useState } from "react";
import { Icon } from "../shared/Icon";
import { Link } from "../shared/router";
import type { ModuleDefinition, ModuleRecord } from "./modules";

function FeaturePanel({ module }: { module: ModuleDefinition }) {
  const [draft, setDraft] = useState(
    "只解释已确认的结构化结果。\n依据不足时说明限制，不补造规则或原文。",
  );
  const [timeout, setTimeout] = useState("3000");
  const [saved, setSaved] = useState(false);
  if (module.mode === "editor")
    return (
      <section className="admin-card module-feature">
        <div className="admin-card-heading">
          <div>
            <h2>解释指令 · 草稿预览</h2>
            <p>编辑只保留在当前页面，刷新后清除；不发布 Prompt。</p>
          </div>
          <span className="admin-status warning">未发布</span>
        </div>
        <label className="module-editor-label" htmlFor="prompt-draft">
          指令内容
        </label>
        <textarea
          id="prompt-draft"
          className="module-editor"
          value={draft}
          onChange={(e) => {
            setDraft(e.target.value);
            setSaved(false);
          }}
          rows={5}
        />
        <div className="module-feature-actions">
          <button className="admin-button" onClick={() => setSaved(true)}>
            确认草稿预览
          </button>
          {saved && <span role="status">草稿已确认 · 仅当前页面</span>}
          <span>模型：未连接 · 版本：DEMO-v1</span>
        </div>
      </section>
    );
  if (module.mode === "settings")
    return (
      <section className="admin-card module-feature">
        <div className="admin-card-heading">
          <div>
            <h2>连接配置预览</h2>
            <p>不采集密钥，不调用外部服务。</p>
          </div>
          <span className="admin-status">未连接</span>
        </div>
        <form
          className="module-settings"
          onSubmit={(e) => {
            e.preventDefault();
            setSaved(true);
          }}
        >
          <label>
            调用用途
            <select aria-label="调用用途">
              <option>结构化结果解释</option>
              <option>依据摘要</option>
            </select>
          </label>
          <label>
            超时（毫秒）
            <input
              aria-label="超时（毫秒）"
              type="number"
              min="100"
              max="60000"
              required
              value={timeout}
              onChange={(e) => {
                setTimeout(e.target.value);
                setSaved(false);
              }}
            />
          </label>
          <div>
            <button className="admin-button">确认配置预览</button>
            {saved && <p role="status">预览已确认 · 未发送连接请求</p>}
          </div>
        </form>
      </section>
    );
  if (module.mode === "pipeline")
    return (
      <section className="admin-card module-feature">
        <div className="admin-card-heading">
          <div>
            <h2>审核流程与门槛</h2>
            <p>每一层保留自己的发布边界。</p>
          </div>
          <Icon name="shield" />
        </div>
        <ol className="module-pipeline">
          {[
            ["RAW", "原始快照", "只读保存"],
            ["Quarantine", "文本与来源核对", "等待独立审核"],
            ["Canonical", "审核通过的内容", "按许可范围发布"],
          ].map(([name, title, note], i) => (
            <li key={name}>
              <span>0{i + 1}</span>
              <h3>{name}</h3>
              <strong>{title}</strong>
              <p>{note}</p>
            </li>
          ))}
        </ol>
        <div className="module-gate">
          晋级操作未连接 · 设计预览不会改变任何资产层级
        </div>
      </section>
    );
  if (module.mode === "compare")
    return (
      <section className="admin-card module-feature">
        <div className="admin-card-heading">
          <div>
            <h2>口径对照 · 晚子时</h2>
            <p>固定演示差异，实际结果需各自版本计算。</p>
          </div>
        </div>
        <div className="module-compare">
          {[
            ["口径甲", "按当日", "出生日期保持录入日期"],
            ["口径乙", "顺延次日", "边界跨日，日期采用次日"],
          ].map(([name, title, note]) => (
            <div key={name}>
              <span>{name} · DEMO</span>
              <h3>{title}</h3>
              <p>{note}</p>
              <small>来源与适用条件：待核</small>
            </div>
          ))}
        </div>
      </section>
    );
  if (module.mode === "permissions")
    return (
      <section className="admin-card module-feature">
        <div className="admin-card-heading">
          <div>
            <h2>职责与权限矩阵</h2>
            <p>角色设计示意，不代表真实授权。</p>
          </div>
          <Icon name="shield" />
        </div>
        <div className="module-table-scroll">
          <table className="module-table">
            <thead>
              <tr>
                <th>职责</th>
                <th>读取资产</th>
                <th>提交意见</th>
                <th>修改配置</th>
                <th>晋级发布</th>
              </tr>
            </thead>
            <tbody>
              {[
                ["访客", "—", "—", "—", "—"],
                ["审核员", "允许", "允许", "—", "另行审核"],
                ["维护员", "允许", "允许", "草稿", "另行审核"],
              ].map((row) => (
                <tr key={row[0]}>
                  {row.map((cell, i) => (
                    <td key={i}>{cell}</td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    );
  if (module.mode === "evaluation")
    return (
      <section className="admin-card module-feature">
        <div className="admin-card-heading">
          <div>
            <h2>评测阅读板</h2>
            <p>以下为状态分布样稿，没有执行实际评测。</p>
          </div>
          <span className="admin-status">DEMO</span>
        </div>
        <div className="module-eval">
          {[
            ["01", "演示通过", "固定输入与预期一致的布局"],
            ["01", "演示失败", "差异字段单独呈现"],
            ["01", "尚未运行", "等待真实引擎联调"],
          ].map(([n, label, note]) => (
            <div key={label}>
              <strong>{n}</strong>
              <h3>{label}</h3>
              <p>{note}</p>
            </div>
          ))}
        </div>
      </section>
    );
  if (module.mode === "logs")
    return (
      <section className="admin-card module-feature">
        <div className="admin-card-heading">
          <div>
            <h2>请求阶段 · DEMO-trace-001</h2>
            <p>虚构事件，不包含用户输入或访问凭据。</p>
          </div>
        </div>
        <ol className="module-timeline">
          {[
            ["09:30:00", "输入校验", "字段范围检查"],
            ["09:30:00", "版本检查", "采用版本标识"],
            ["09:30:01", "等待服务", "无真实计算请求"],
          ].map(([time, name, note]) => (
            <li key={name}>
              <time>{time}</time>
              <span />
              <div>
                <strong>{name}</strong>
                <p>{note}</p>
              </div>
            </li>
          ))}
        </ol>
      </section>
    );
  return null;
}
function RecordDetail({
  module,
  record,
}: {
  module: ModuleDefinition;
  record: ModuleRecord;
}) {
  const [tab, setTab] = useState("details");
  return (
    <>
      <div className="module-breadcrumb">
        <Link href={"/admin/" + module.id}>{module.title}</Link>
        <Icon name="chevron" size={14} />
        <span>{record.id}</span>
      </div>
      <div className="admin-page-heading">
        <div>
          <h1>{record.name}</h1>
          <p>{record.id} · 虚构演示记录</p>
        </div>
        <span className="admin-status">{record.state}</span>
      </div>
      <div className="module-tabs" role="group" aria-label="记录详情视图">
        {[
          ["details", "记录详情"],
          ["relations", "关联关系"],
          ["audit", "审核轨迹"],
        ].map(([id, name]) => (
          <button key={id} aria-pressed={tab === id} onClick={() => setTab(id)}>
            {name}
          </button>
        ))}
      </div>
      <section className="admin-card module-detail">
        {tab === "details" ? (
          <>
            <h2>字段与说明</h2>
            <dl className="admin-detail-fields">
              {module.columns.map((label, i) => (
                <div key={label}>
                  <dt>{label}</dt>
                  <dd>{record.values[i]}</dd>
                </div>
              ))}
            </dl>
            <p>{record.detail}</p>
          </>
        ) : tab === "relations" ? (
          <>
            <h2>关联关系</h2>
            <div className="module-relation">
              <span>{record.id}</span>
              <Icon name="arrow" />
              <span>关联标识待服务返回</span>
            </div>
            <p>展示关联位置，不伪造真实书目、规则或生产记录的引用。</p>
          </>
        ) : (
          <>
            <h2>审核轨迹</h2>
            <ol className="module-timeline">
              <li>
                <time>DEMO</time>
                <span />
                <div>
                  <strong>设计记录创建</strong>
                  <p>字段与状态布局示例。</p>
                </div>
              </li>
              <li>
                <time>未审核</time>
                <span />
                <div>
                  <strong>等待真实审核记录</strong>
                  <p>未发生发布、写入或晋级。</p>
                </div>
              </li>
            </ol>
          </>
        )}
        <div className="module-gate">
          静态演示 · 真实记录、写入与权限服务尚未接入
        </div>
      </section>
      <Link className="admin-button" href={"/admin/" + module.id}>
        返回{module.title}
      </Link>
    </>
  );
}
export function ModulePage({
  module,
  recordId,
}: {
  module: ModuleDefinition;
  recordId?: string;
}) {
  const [query, setQuery] = useState("");
  const [state, setState] = useState("全部状态");
  const record = module.records.find((r) => r.id === recordId);
  if (recordId)
    return record ? (
      <RecordDetail module={module} record={record} />
    ) : (
      <section className="admin-card module-detail">
        <h1>没有这个记录</h1>
        <p>请回到列表核对编号。</p>
        <Link className="admin-button" href={"/admin/" + module.id}>
          返回列表
        </Link>
      </section>
    );
  const rows = module.records.filter(
    (r) =>
      (state === "全部状态" || r.state === state) &&
      (r.name + r.id + r.values.join(" "))
        .toLowerCase()
        .includes(query.trim().toLowerCase()),
  );
  return (
    <>
      <div className="admin-page-heading">
        <div>
          <h1>{module.title}</h1>
          <p>{module.description}</p>
        </div>
        <span className="admin-readonly">
          <Icon name="shield" size={16} />
          设计预览 · DEMO
        </span>
      </div>
      <FeaturePanel key={module.id} module={module} />
      <section className="admin-card">
        <div className="asset-toolbar">
          <div className="asset-search">
            <Icon name="search" size={17} />
            <input
              aria-label={"搜索" + module.title}
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="搜索名称、编号或相关字段"
            />
          </div>
          <div className="asset-filters">
            <select
              aria-label="状态筛选"
              value={state}
              onChange={(e) => setState(e.target.value)}
            >
              {["全部状态", ...new Set(module.records.map((r) => r.state))].map(
                (s) => (
                  <option key={s}>{s}</option>
                ),
              )}
            </select>
          </div>
        </div>
        <p className="asset-scroll-hint">
          <Icon name="arrow" size={13} />
          左右滑动表格，查看完整字段与详情
        </p>
        <div
          className="module-table-scroll"
          role="region"
          aria-label={module.title + "记录表"}
          tabIndex={0}
        >
          <table className="module-table">
            <thead>
              <tr>
                <th>记录 / 编号</th>
                {module.columns.map((c) => (
                  <th key={c}>{c}</th>
                ))}
                <th>状态</th>
                <th>操作</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((r) => (
                <tr key={r.id}>
                  <td>
                    <Link
                      className="module-record-name"
                      href={"/admin/" + module.id + "/" + r.id}
                    >
                      {r.name}
                    </Link>
                    <small>{r.id}</small>
                  </td>
                  {r.values.map((v, i) => (
                    <td key={i}>{v}</td>
                  ))}
                  <td>
                    <span className="admin-status">{r.state}</span>
                  </td>
                  <td>
                    <Link
                      className="table-action"
                      href={"/admin/" + module.id + "/" + r.id}
                    >
                      详情
                      <Icon name="chevron" size={13} />
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        {rows.length === 0 && (
          <div className="admin-empty-results">
            <Icon name="search" size={28} />
            <p>没有匹配的演示记录</p>
            <button
              className="admin-button"
              onClick={() => {
                setQuery("");
                setState("全部状态");
              }}
            >
              清除筛选
            </button>
          </div>
        )}
        <div className="asset-table-footer">
          <span>共 {rows.length} 条虚构演示记录</span>
          <span>不连接生产数据</span>
        </div>
      </section>
      <section className="module-guides">
        {module.guide.map(([name, note], i) => (
          <article key={name}>
            <span>0{i + 1}</span>
            <h2>{name}</h2>
            <p>{note}</p>
          </article>
        ))}
      </section>
    </>
  );
}
