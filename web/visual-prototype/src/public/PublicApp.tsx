import { useEffect, useState } from "react";
import { Icon } from "../shared/Icon";
import { Link, NoticeContext, usePath } from "../shared/router";
import { HomePage } from "./HomePage";
import { DomainHomePage } from "./DomainHomePage";
import { getDomainPage } from "./domainPages";
import { LiuyaoResultPage } from "./LiuyaoResultPage";
import { MusicPlayer } from "./MusicPlayer";
import { ResultTemplatePage } from "./ResultTemplatePage";
import { LibraryPage } from "./LibraryPage";
import { domainPages } from "./domainPages";
import "./public.css";

const favoriteKey = "tianji.prototype.favorite";
function initialFavorite() {
  try {
    return localStorage.getItem(favoriteKey) === "true";
  } catch {
    return false;
  }
}
export function PublicApp() {
  const path = usePath();
  const domainPage = getDomainPage(path);
  const resultPage = domainPages.find((item) => path === `/${item.id}/result`);
  const [favorite, setFavorite] = useState(initialFavorite);
  const [notice, setNotice] = useState("");
  useEffect(() => {
    try {
      localStorage.setItem(favoriteKey, String(favorite));
    } catch {
      /* Optional local preference. */
    }
  }, [favorite]);
  useEffect(() => {
    if (!notice) return;
    const timer = setTimeout(() => setNotice(""), 4000);
    return () => clearTimeout(timer);
  }, [notice]);
  useEffect(() => {
    document.title =
      (domainPage?.name ||
        resultPage?.name ||
        (path === "/history"
          ? "历史记录"
          : path === "/favorites"
            ? "我的收藏"
            : "观象循理")) + " · 天机";
  }, [path]);
  return (
    <NoticeContext.Provider value={setNotice}>
      <div className="public-app">
        <header className="public-header">
          <Link className="public-brand" href="/" aria-label="天机首页">
            <span className="brand-mark" aria-hidden="true">
              <i />
              <i />
              <i />
            </span>
            <span>
              天机<small>观象循理</small>
            </span>
          </Link>
          <nav className="public-nav" aria-label="前台导航">
            <Link href="/">推演工具</Link>
            <Link
              href="/history"
              aria-current={path === "/history" ? "page" : undefined}
            >
              历史记录
            </Link>
            <Link
              href="/favorites"
              aria-current={path === "/favorites" ? "page" : undefined}
            >
              收藏
            </Link>
          </nav>
          <div className="public-header-end">
            <span className="prototype-badge">视觉样稿</span>
            <MusicPlayer />
          </div>
        </header>
        <main className="public-main">
          {path === "/" ? (
            <HomePage />
          ) : domainPage ? (
            <DomainHomePage key={domainPage.id} page={domainPage} />
          ) : path === "/liuyao/result" ? (
            <LiuyaoResultPage
              favorite={favorite}
              onToggleFavorite={() => setFavorite(!favorite)}
            />
          ) : resultPage ? (
            <ResultTemplatePage key={resultPage.id} page={resultPage} />
          ) : path === "/history" || path === "/favorites" ? (
            <LibraryPage
              key={path}
              kind={path === "/history" ? "history" : "favorites"}
              favorite={favorite}
              onToggleFavorite={() => setFavorite(!favorite)}
            />
          ) : (
            <section className="public-not-found">
              <span className="eyebrow">此处暂未开放</span>
              <h1>回到推演的起点</h1>
              <p>这个页面不在当前展示范围内。</p>
              <Link className="button primary" href="/">
                返回首页
                <Icon name="arrow" />
              </Link>
            </section>
          )}
        </main>
        <footer className="public-footer">
          <Link className="footer-brand" href="/">
            天机 <span>以象见理</span>
          </Link>
          <p>传统文化研究与学习 · 视觉示例不构成现实判断</p>
          <small>静态设计原型 · 尚未接入排盘或 AI 服务</small>
        </footer>
        <nav className="mobile-bottom-nav" aria-label="移动导航">
          <Link href="/" className={path === "/" ? "active" : ""}>
            <Icon name="grid" size={20} />
            <span>首页</span>
          </Link>
          <Link href="/history" className={path === "/history" ? "active" : ""}>
            <Icon name="clock" size={20} />
            <span>历史</span>
          </Link>
          <Link
            href="/favorites"
            className={path === "/favorites" ? "active" : ""}
          >
            <Icon name="star" size={20} />
            <span>收藏</span>
          </Link>
        </nav>
        {notice && (
          <div className="public-toast" role="status">
            {notice}
          </div>
        )}
      </div>
    </NoticeContext.Provider>
  );
}
