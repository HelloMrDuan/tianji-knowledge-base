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
import { QuestionPage } from "./QuestionPage";
import { BaziProfilePage } from "./BaziProfilePage";
import { YearlyStructurePage } from "./YearlyStructurePage";
import { RomanceStructurePage } from "./RomanceStructurePage";
import { CareerWealthStructurePage } from "./CareerWealthStructurePage";
import { LifeOverviewPage } from "./LifeOverviewPage";
import { DailyStructurePage } from "./DailyStructurePage";
import { PeriodStructurePage } from "./PeriodStructurePage";
import { CompatibilityStructurePage } from "./CompatibilityStructurePage";
import "./public.css";

const favoriteKey = "tianji.product.favorite";
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
    const title =
      path === "/"
        ? "天机"
        : path === "/ask"
          ? "一事占问"
          : path === "/bazi-profile"
            ? "八字基础档案"
            : path === "/yearly-structure"
              ? "流年结构"
              : path === "/romance-structure"
                ? "桃花姻缘 · 结构内测"
                : path === "/career-wealth-structure"
                  ? "事业财运 · 结构内测"
                  : path === "/life-overview"
                    ? "人生总览"
                    : path === "/daily-structure"
                      ? "今日运势 · 结构版"
                      : path === "/weekly-structure"
                        ? "本周运势 · 结构版"
                        : path === "/monthly-structure"
                          ? "本月运势 · 结构版"
                          : path === "/compatibility-structure"
                            ? "缘分合盘 · 结构版"
                            : domainPage?.name ||
            resultPage?.name ||
            (path === "/history"
              ? "历史记录"
              : path === "/favorites"
                ? "我的收藏"
                : "天机");
    document.title = `${title} · 有据可寻`;
  }, [path, domainPage, resultPage]);

  return (
    <NoticeContext.Provider value={setNotice}>
      <div className="public-app">
        <header className="public-header">
          <Link className="public-brand" href="/" aria-label="天机首页">
            <span className="brand-mark" aria-hidden="true"><i /><i /><i /></span>
            <span>天机<small>一件事，一份有据的参考</small></span>
          </Link>

          <nav className="public-nav" aria-label="前台导航">
            <Link href="/" aria-current={path === "/" ? "page" : undefined}>生活场景</Link>
            <a href="/#professional">专业排盘</a>
            <Link href="/history" aria-current={path === "/history" ? "page" : undefined}>历史记录</Link>
            <Link href="/favorites" aria-current={path === "/favorites" ? "page" : undefined}>收藏</Link>
          </nav>

          <div className="public-header-end">
            <MusicPlayer />
          </div>
        </header>

        <main className="public-main">
          {path === "/" ? (
            <HomePage />
          ) : path === "/ask" ? (
            <QuestionPage />
          ) : path === "/bazi-profile" ? (
            <BaziProfilePage />
          ) : path === "/yearly-structure" ? (
            <YearlyStructurePage />
          ) : path === "/romance-structure" ? (
            <RomanceStructurePage />
          ) : path === "/career-wealth-structure" ? (
            <CareerWealthStructurePage />
          ) : path === "/life-overview" ? (
            <LifeOverviewPage />
          ) : path === "/daily-structure" ? (
            <DailyStructurePage />
          ) : path === "/weekly-structure" ? (
            <PeriodStructurePage mode="weekly" />
          ) : path === "/monthly-structure" ? (
            <PeriodStructurePage mode="monthly" />
          ) : path === "/compatibility-structure" ? (
            <CompatibilityStructurePage />
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
              <h1>回到你真正关心的事</h1>
              <p>当前页面尚未进入正式能力范围。</p>
              <Link className="button primary" href="/">
                返回首页
                <Icon name="arrow" />
              </Link>
            </section>
          )}
        </main>

        <footer className="public-footer">
          <Link className="footer-brand" href="/">天机 <span>以象见理</span></Link>
          <p>传统文化研究与学习 · 结果提供结构化参考，不替代现实专业判断</p>
          <small>确定性计算、规则与典籍依据优先；AI 解读通过真实校准后再开放。</small>
        </footer>

        <nav className="mobile-bottom-nav" aria-label="移动导航">
          <Link href="/" className={path === "/" ? "active" : ""}>
            <Icon name="grid" size={20} /><span>首页</span>
          </Link>
          <Link href="/ask" className={path === "/ask" ? "active" : ""}>
            <Icon name="layers" size={20} /><span>占问</span>
          </Link>
          <Link href="/history" className={path === "/history" ? "active" : ""}>
            <Icon name="clock" size={20} /><span>历史</span>
          </Link>
          <Link href="/favorites" className={path === "/favorites" ? "active" : ""}>
            <Icon name="star" size={20} /><span>收藏</span>
          </Link>
        </nav>

        {notice && <div className="public-toast" role="status">{notice}</div>}
      </div>
    </NoticeContext.Provider>
  );
}
