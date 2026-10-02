import { useCallback, useEffect, useState } from "react";
import { Dialog } from "../shared/Dialog";
import { Icon } from "../shared/Icon";
import { Link, NoticeContext, usePath } from "../shared/router";
import { HomePage } from "./HomePage";
import { LiuyaoResultPage } from "./LiuyaoResultPage";
import { MusicPlayer } from "./MusicPlayer";
import { recentSamples } from "./fixtures";
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
  const [panel, setPanel] = useState<"history" | "favorites" | null>(null);
  const [favorite, setFavorite] = useState(initialFavorite);
  const [notice, setNotice] = useState("");
  const closePanel = useCallback(() => setPanel(null), []);
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
      path === "/liuyao/result" ? "六爻示例 · 天机" : "天机 · 观象循理";
    setPanel(null);
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
            <button onClick={() => setPanel("history")}>历史记录</button>
            <button onClick={() => setPanel("favorites")}>收藏</button>
          </nav>
          <div className="public-header-end">
            <span className="prototype-badge">视觉样稿</span>
            <MusicPlayer />
          </div>
        </header>
        <main className="public-main">
          {path === "/" ? (
            <HomePage />
          ) : path === "/liuyao/result" ? (
            <LiuyaoResultPage
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
          <button onClick={() => setPanel("history")}>
            <Icon name="clock" size={20} />
            <span>历史</span>
          </button>
          <button onClick={() => setPanel("favorites")}>
            <Icon name="star" size={20} />
            <span>收藏</span>
          </button>
        </nav>
        {notice && (
          <div className="public-toast" role="status">
            {notice}
          </div>
        )}
        {panel && (
          <Dialog
            title={panel === "history" ? "历史记录" : "我的收藏"}
            onClose={closePanel}
            className="public-dialog"
          >
            <p className="sample-note">
              这里只展示本轮静态示例，不代表已保存真实推演。
            </p>
            {panel === "history" ? (
              recentSamples.map((item) => (
                <Link
                  href={item.href}
                  className="history-item"
                  key={item.name}
                  onClick={closePanel}
                >
                  <Icon name="clock" />
                  <div>
                    <strong>{item.name}</strong>
                    <span>
                      {item.when} · {item.subtitle}
                    </span>
                  </div>
                  <Icon name="chevron" size={16} />
                </Link>
              ))
            ) : favorite ? (
              <Link
                href="/liuyao/result"
                className="history-item"
                onClick={closePanel}
              >
                <Icon name="star" />
                <div>
                  <strong>乾为天 · 天风姤</strong>
                  <span>收藏的视觉示例</span>
                </div>
                <Icon name="chevron" size={16} />
              </Link>
            ) : (
              <div className="empty-state">
                <Icon name="star" size={32} />
                <h3>还没有收藏</h3>
                <p>在六爻示例页点“收藏”，便于再次查看。</p>
              </div>
            )}
          </Dialog>
        )}
      </div>
    </NoticeContext.Provider>
  );
}
