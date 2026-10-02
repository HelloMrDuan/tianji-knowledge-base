import { useCallback, useEffect, useState } from "react";
import { Icon } from "../shared/Icon";
import { Dialog } from "../shared/Dialog";
import { Link, usePath } from "../shared/router";
import { adminGroups } from "./fixtures";
import { Dashboard } from "./Dashboard";
import { AssetPage } from "./AssetPage";
import type { AssetKind } from "./fixtures";
import "./admin.css";

const titles: Record<string, string> = {
  "/admin": "仪表盘",
  "/admin/classics": "古籍管理",
  "/admin/rules": "规则管理",
  "/admin/evidence": "Evidence 管理",
};
export default function AdminApp() {
  const path = usePath();
  const [menuOpen, setMenuOpen] = useState(false);
  const [planned, setPlanned] = useState<string | null>(null);
  const closePlanned = useCallback(() => setPlanned(null), []);
  const kind = path.split("/")[2] as AssetKind;
  useEffect(() => {
    document.title = `${titles[path] || "页面未开放"} · 天机管理`;
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
              {group.items.map((item) =>
                item.path ? (
                  <Link
                    href={item.path}
                    className={`admin-nav-item ${path === item.path ? "active" : ""}`}
                    key={item.label}
                    onClick={() => setMenuOpen(false)}
                  >
                    <Icon name={item.icon as "grid"} size={17} />
                    <span>{item.label}</span>
                  </Link>
                ) : (
                  <button
                    className="admin-nav-item planned"
                    key={item.label}
                    onClick={() => {
                      setPlanned(item.label);
                      setMenuOpen(false);
                    }}
                  >
                    <Icon name={item.icon as "file"} size={17} />
                    <span>{item.label}</span>
                    <small>规划</small>
                  </button>
                ),
              )}
            </section>
          ))}
        </nav>
        <div className="admin-sidebar-bottom">
          <span className="status-dot" />
          <span>静态原型 · 无数据写入</span>
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
            <strong>{titles[path] || "页面未开放"}</strong>
          </div>
          <div className="admin-header-right">
            <span className="admin-demo-tag">演示模式</span>
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
          ) : ["classics", "rules", "evidence"].includes(kind) &&
            path === `/admin/${kind}` ? (
            <AssetPage kind={kind} key={kind} />
          ) : (
            <section className="admin-card admin-empty">
              <h1>此页面尚未开放</h1>
              <p>当前展示仪表盘、古籍、规则和 Evidence 四个后台示例。</p>
              <Link className="admin-button" href="/admin">
                返回仪表盘
              </Link>
            </section>
          )}
        </main>
        <footer className="admin-footer">
          天机内部资产管理 · 视觉原型，不具备认证、权限或真实管理能力
        </footer>
      </div>
      {planned && (
        <Dialog title={planned} onClose={closePlanned}>
          <span className="admin-status neutral">信息架构规划</span>
          <p>此模块已列入后台规划，本轮不实现。</p>
          <p>
            当前原型仅展示独立后台布局及古籍、规则、Evidence
            管理页，不连接真实资产或提供写入能力。
          </p>
        </Dialog>
      )}
    </div>
  );
}
