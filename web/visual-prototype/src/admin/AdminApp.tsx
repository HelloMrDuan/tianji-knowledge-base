import { useEffect, useState } from "react";
import { Icon } from "../shared/Icon";
import { ModulePage } from "./ModulePage";
import { moduleForPath } from "./modules";
import { Link, usePath } from "../shared/router";
import { adminGroups } from "./fixtures";
import { Dashboard } from "./Dashboard";
import { ConflictGovernancePage } from "./ConflictGovernancePage";
import { GovernanceAssetPage } from "./GovernanceAssetPage";
import { ClassicGovernancePage } from "./ClassicGovernancePage";
import { ChapterGovernancePage } from "./ChapterGovernancePage";
import { TermGovernancePage } from "./TermGovernancePage";
import "./admin.css";
import "./modules.css";

const titles: Record<string, string> = {
  "/admin": "仪表盘",
  "/admin/classics": "古籍管理",
  "/admin/chapters": "章节管理",
  "/admin/terms": "术语管理",
  "/admin/rules": "规则管理",
  "/admin/evidence": "Evidence 管理",
  "/admin/conflicts": "流派与冲突",
};
export default function AdminApp() {
  const path = usePath();
  const [menuOpen, setMenuOpen] = useState(false);
  const module = moduleForPath(path);
  const recordId = path.split("/")[3];
  useEffect(() => {
    document.title = `${titles[path] || module?.title || "页面未找到"} · 天机管理`;
    setMenuOpen(false);
  }, [path]);
  return (
    <div className="admin-app">
      {menuOpen && (
        <button
          className="admin-sidebar-backdrop"
          aria-label="关闭管理导航"
          onClick={() => setMenuOpen(false)}
        />
      )}
      <aside className={`admin-sidebar ${menuOpen ? "is-open" : ""}`}>
        <div className="admin-brand">
          <span className="admin-brand-icon">
            <Icon name="layers" size={21} />
          </span>
          <div>
            <strong>天机管理</strong>
            <small>内部资产工作台</small>
          </div>
          <button
            className="icon-button admin-menu-close"
            aria-label="关闭侧栏"
            onClick={() => setMenuOpen(false)}
          >
            <Icon name="close" />
          </button>
        </div>
        <nav aria-label="后台管理导航">
          {adminGroups.map((group) => (
            <section key={group.title}>
              <h2>{group.title}</h2>
              {group.items.map((item) => (
                <Link
                  href={item.path}
                  className={`admin-nav-item ${path === item.path || (item.path !== "/admin" && path.startsWith(item.path + "/")) ? "active" : ""}`}
                  aria-current={path === item.path ? "page" : undefined}
                  key={item.label}
                  onClick={() => setMenuOpen(false)}
                >
                  <Icon name={item.icon as "grid"} size={17} />
                  <span>{item.label}</span>
                </Link>
              ))}
            </section>
          ))}
        </nav>
        <div className="admin-sidebar-bottom">
          <span className="status-dot" />
          <span>管理工作台 · 当前只读</span>
        </div>
      </aside>
      <div className="admin-workspace">
        <header className="admin-header">
          <div className="admin-header-left">
            <button
              className="icon-button admin-menu-toggle"
              aria-label="打开管理导航"
              onClick={() => setMenuOpen(true)}
            >
              <Icon name="menu" />
            </button>
            <span>工作台</span>
            <Icon name="chevron" size={13} />
            <strong>{titles[path] || module?.title || "页面未找到"}</strong>
          </div>
          <div className="admin-header-right">
            <span className="admin-demo-tag">只读模式</span>
            <Link href="/" className="admin-public-link">
              查看前台
              <Icon name="external" size={14} />
            </Link>
            <span className="admin-avatar">管</span>
          </div>
        </header>
        <main className="admin-main">
          {path === "/admin" ? (
            <Dashboard />
          ) : path.startsWith("/admin/conflicts") ? (
            <ConflictGovernancePage />
          ) : path === "/admin/rules" ? (
            <GovernanceAssetPage kind="rules" />
          ) : path === "/admin/evidence" ? (
            <GovernanceAssetPage kind="evidence" />
          ) : path === "/admin/classics" ? (
            <ClassicGovernancePage />
          ) : path === "/admin/chapters" ? (
            <ChapterGovernancePage />
          ) : path === "/admin/terms" ? (
            <TermGovernancePage />
          ) : module && path.split("/").length <= 4 ? (
            <ModulePage key={path} module={module} recordId={recordId} />
          ) : (
            <section className="admin-card admin-empty">
              <h1>页面未找到</h1>
              <p>请从管理导航选择一个页面。请从管理导航选择一个页面。</p>
              <Link className="admin-button" href="/admin">
                返回仪表盘
              </Link>
            </section>
          )}
        </main>
        <footer className="admin-footer">
          天机内部资产管理 · 当前阶段只读，写入、认证与权限服务待后续接入
        </footer>
      </div>
    </div>
  );
}
