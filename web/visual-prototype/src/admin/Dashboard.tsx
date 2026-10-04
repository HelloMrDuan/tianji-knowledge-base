import { Icon } from "../shared/Icon";
import { Link } from "../shared/router";

export function Dashboard() {
  return (
    <>
      <div className="admin-page-heading">
        <div>
          <h1>资产与审核概览</h1>
          <p>集中查看知识资产、审核队列与生产边界。</p>
        </div>
        <span className="admin-date">2026.10.02 · 静态展示</span>
      </div>
      <div className="admin-context-banner">
        <Icon name="shield" size={19} />
        <div>
          <strong>内部资产与用户结果保持分离</strong>
          <span>
            前台仅展示当前推演命中的典籍片段。RAW 与 Quarantine 不自动进入生产。
          </span>
        </div>
        <span>边界说明</span>
      </div>
      <div className="admin-stats">
        {[
          ["典籍资产", "24", "6 个术数分类", "book"],
          ["规则记录", "128", "18 条待复核", "layers"],
          ["Evidence", "326", "C / D 分级记录", "shield"],
          ["治理事项", "—", "真实冲突需授权读取", "file"],
        ].map(([label, value, note, icon]) => (
          <article className="admin-stat" key={label}>
            <div>
              <span>{label}</span>
              <Icon name={icon as "book"} size={18} />
            </div>
            <strong>
              {value}
              <small>演示</small>
            </strong>
            <p>{note}</p>
          </article>
        ))}
      </div>
      <div className="dashboard-columns">
        <section className="admin-card">
          <div className="admin-card-heading">
            <div>
              <h2>待审队列</h2>
              <p>静态示例 · 优先处理影响生产边界的记录</p>
            </div>
            <span className="admin-count">4 项示例</span>
          </div>
          <div className="dashboard-queue">
            {[
              [
                "绝对元运纪元",
                "风水 · D 级研究假设",
                "仅研究",
                "warning",
                "/admin/rules",
              ],
              [
                "安星章节版本差异",
                "紫微 · 原文与版本复核",
                "待复核",
                "neutral",
                "/admin/classics",
              ],
              [
                "动变规则引用定位",
                "六爻 · 对应章节与片段",
                "待确认",
                "neutral",
                "/admin/evidence",
              ],
              [
                "待核电子文本",
                "风水 · 来源信息不完整",
                "隔离",
                "danger",
                "/admin/classics",
              ],
            ].map(([title, note, status, tone, href]) => (
              <Link href={href} className="queue-item" key={title}>
                <span className="queue-document">
                  <Icon name="file" size={18} />
                </span>
                <div>
                  <strong>{title}</strong>
                  <p>{note}</p>
                </div>
                <span className={`admin-status ${tone}`}>{status}</span>
                <Icon name="chevron" size={15} />
              </Link>
            ))}
          </div>
        </section>
        <section className="admin-card governance-card">
          <div className="admin-card-heading">
            <div>
              <h2>发布与解释边界</h2>
              <p>界面规划，不代表运行状态</p>
            </div>
          </div>
          <div className="governance-item">
            <span className="governance-icon">
              <Icon name="shield" size={18} />
            </span>
            <div>
              <strong>Canonical 审核后发布</strong>
              <p>隔离内容不自动晋级。</p>
            </div>
          </div>
          <div className="governance-item">
            <span className="governance-icon">
              <Icon name="layers" size={18} />
            </span>
            <div>
              <strong>算法与流派显式隔离</strong>
              <p>约定变更需要独立复核。</p>
            </div>
          </div>
          <div className="governance-item">
            <span className="governance-icon">
              <Icon name="settings" size={18} />
            </span>
            <div>
              <strong>AI 服务暂不接入</strong>
              <p>没有模型调用或密钥设置。</p>
            </div>
          </div>
          <div className="governance-bottom">
            来源等级与审核状态分别保留，不能相互替代。
          </div>
        </section>
      </div>
      <section className="admin-card quick-assets">
        <div className="admin-card-heading">
          <div>
            <h2>资产管理入口</h2>
            <p>本轮开放的三个管理页示例</p>
          </div>
          <span className="admin-small-muted">只读展示</span>
        </div>
        <div className="admin-shortcuts">
          {[
            ["古籍管理", "书目、章节、审核状态", "book", "/admin/classics"],
            ["规则管理", "执行范围、流派与证据关联", "layers", "/admin/rules"],
            [
              "Evidence 管理",
              "原文片段、等级与对应规则",
              "shield",
              "/admin/evidence",
            ],
          ].map(([title, note, icon, href]) => (
            <Link href={href} key={title}>
              <Icon name={icon as "book"} size={24} />
              <div>
                <strong>{title}</strong>
                <span>{note}</span>
              </div>
              <Icon name="arrow" size={18} />
            </Link>
          ))}
        </div>
      </section>
      <section className="admin-card audit-notes">
        <div className="admin-card-heading">
          <div>
            <h2>最近审核记录</h2>
            <p>视觉展示记录，不是系统日志</p>
          </div>
        </div>
        <div className="audit-row">
          <span>09:12</span>
          <strong>更新六爻示例章节定位</strong>
          <small>演示管理员</small>
          <span className="admin-status success">示例</span>
        </div>
        <div className="audit-row">
          <span>08:36</span>
          <strong>标记一条 D 级研究假设</strong>
          <small>演示管理员</small>
          <span className="admin-status neutral">示例</span>
        </div>
      </section>
    </>
  );
}
