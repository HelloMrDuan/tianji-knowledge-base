import { Icon } from "../shared/Icon";
import { Link } from "../shared/router";
import { InkLandscape } from "./InkLandscape";
import { NightHeroScene } from "./NightHeroScene";
import { PaperCard, MobileCardRow } from "./PaperCard";
import { domainPages } from "./domainPages";
import { scenarioProducts } from "./scenarioProducts";
import "./scenarios.css";
import "./night-home.css";

export function HomePage() {
  const baziProfile = scenarioProducts.find((item) => item.id === "bazi-profile")!;
  const daily = scenarioProducts.find((item) => item.id === "daily")!;
  const yearly = scenarioProducts.find((item) => item.id === "yearly")!;
  const romance = scenarioProducts.find((item) => item.id === "romance")!;
  const career = scenarioProducts.find((item) => item.id === "career")!;
  const life = scenarioProducts.find((item) => item.id === "life")!;
  const dream = scenarioProducts.find((item) => item.id === "dream")!;
  const compatibility = scenarioProducts.find((item) => item.id === "compatibility")!;
  const weekly = scenarioProducts.find((item) => item.id === "weekly")!;
  const monthly = scenarioProducts.find((item) => item.id === "monthly")!;
  const question = scenarioProducts.find((item) => item.id === "question")!;
  const homePriority = [
    "daily", "romance", "career", "yearly", "weekly", "monthly",
    "bazi-profile", "dream", "compatibility", "life", "question",
  ];
  const orderedProducts = [...scenarioProducts].sort(
    (a, b) => homePriority.indexOf(a.id) - homePriority.indexOf(b.id),
  );
  const keyProducts = new Set(["daily", "romance", "career"]);
  return (
    <div className="scenario-home">
      <section className="scenario-hero night-hero">
        <div className="night-hero-night" aria-hidden="true">
          <NightHeroScene />
        </div>
        <div className="night-hero-paper" aria-hidden="true">
          <InkLandscape />
        </div>
        <div className="night-hero-brand">
          <h1 className="brand-title">
            天机命理
            <span className="brand-seal" aria-hidden="true">天机</span>
          </h1>
          <p className="brand-sub">观天之道 · 知人之命</p>
          <p className="brand-desc">
            以真实历法推演时序流转，参已审核的传统典籍，看今日运势结构，亦观桃花、事业与财运。
          </p>
          <div className="scenario-hero-actions">
            <Link className="button primary" href="/daily-structure">
              查看今日运势
              <Icon name="arrow" size={18} />
            </Link>
            <Link className="button outlined" href="/romance-structure">
              测桃花姻缘
            </Link>
            <Link className="button outlined" href="/career-wealth-structure">
              看事业财运
            </Link>
            <a className="text-action" href="/bazi-profile">
              八字测算
              <Icon name="chevron" size={16} />
            </a>
          </div>
        </div>
      </section>

      <section className="night-cards-section" aria-label="主要测算入口">
        <div className="paper-cards">
          <PaperCard product={daily} art="sunrise" />
          <PaperCard product={romance} art="peach" />
          <PaperCard product={career} art="horse" />
          <PaperCard product={yearly} art="mountains" />
        </div>
        {/* 手机紧凑列表（原图手机端样式），桌面端隐藏 */}
        <div className="mobile-card-list">
          <MobileCardRow product={daily} art="sunrise" />
          <MobileCardRow product={romance} art="peach" />
          <MobileCardRow product={career} art="horse" />
          <MobileCardRow product={yearly} art="mountains" />
        </div>
        <div className="scenario-proof">
          <span><i />确定性计算先行</span>
          <span><i />规则与典籍可追溯</span>
          <span><i />今日 / 本周 / 本月 / 年度可重复计算</span>
          <span><i />AI 未校准前不自动公开</span>
        </div>
      </section>

      {/* 第二层：三个重点测算入口（八字/解梦/合盘） */}
      <section className="spotlight-section" aria-label="重点测算入口">
        <div className="section-heading">
          <div>
            <span className="eyebrow">命理 · 梦象 · 缘分</span>
            <h2>深入测算</h2>
          </div>
        </div>
        <div className="paper-cards spotlight-cards">
          <PaperCard product={baziProfile} art="bazi" />
          <PaperCard product={dream} art="dream" />
          <PaperCard product={compatibility} art="compatibility" />
        </div>
        <div className="mobile-card-list">
          <MobileCardRow product={baziProfile} art="bazi" />
          <MobileCardRow product={dream} art="dream" />
          <MobileCardRow product={compatibility} art="compatibility" />
        </div>
      </section>

      {/* 第三层：其他四个测算场景 */}
      <section className="tier3-section" aria-label="其他测算场景">
        <div className="section-heading">
          <div>
            <span className="eyebrow">周期 · 问事 · 总览</span>
            <h2>更多测算</h2>
          </div>
        </div>
        <div className="tier3-list">
          <MobileCardRow product={weekly} art="sunrise" />
          <MobileCardRow product={monthly} art="mountains" />
          <MobileCardRow product={question} art="horse" />
          <MobileCardRow product={life} art="peach" />
        </div>
      </section>

      <section className="professional-section" id="professional">
        <div className="section-heading">
          <div>
            <span className="eyebrow">更多传统工具 · 进阶入口</span>
            <h2>专业排盘</h2>
          </div>
          <span className="quiet-label">退到第二层，不再占据首页主入口</span>
        </div>
        <div className="tool-grid">
          {domainPages.map((tool, index) => (
            <article key={tool.name} className="tool-card">
              <div className="tool-top">
                <span className="tool-glyph">{tool.glyph}</span>
                <span className="tool-index">0{index + 1}</span>
              </div>
              <h3>{tool.name}</h3>
              <p>{tool.tags.slice(0, 2).join(" · ")}</p>
              <Link
                href={"/" + tool.id}
                className="tool-action"
                aria-label={"进入" + tool.name + "专业页"}
              >
                专业入口
                <Icon name="arrow" size={17} />
              </Link>
            </article>
          ))}
        </div>
        <p className="professional-note">
          八字基础、年度、桃花与事业财运结构已进入真实链路；完整吉凶报告、合盘和应期仍不会提前包装成“已可用”。
        </p>
      </section>

      <section className="home-music-hint">
        <div>
          <strong>古风背景音乐已经保留在全站右上角</strong>
          <small>默认关闭。你主动播放后，页面内切换路由不会中断，并会记住音量。</small>
        </div>
        <span className="eyebrow">听一曲 · 再看运势</span>
      </section>
    </div>
  );
}
