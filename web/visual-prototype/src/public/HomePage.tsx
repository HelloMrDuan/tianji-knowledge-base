import { Icon } from "../shared/Icon";
import { Link } from "../shared/router";
import { InkLandscape } from "./InkLandscape";
import { NightHeroScene } from "./NightHeroScene";
import { PaperCard } from "./PaperCard";
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
            以真实历法计算与已审核的传统知识为据，看今天的运势结构，也看看桃花、事业和财运。
            现阶段提供结构参考；暂未证实的吉凶、婚期和收益预测不会编造。
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
        <div className="scenario-proof">
          <span><i />确定性计算先行</span>
          <span><i />规则与典籍可追溯</span>
          <span><i />今日 / 本周 / 本月 / 年度可重复计算</span>
          <span><i />AI 未校准前不自动公开</span>
        </div>
      </section>

      <nav className="scenario-time-strip" aria-label="运势时间快捷入口">
        <Link href="/daily-structure">
          <strong>今日运势</strong>
          <span>每日结构参考</span>
        </Link>
        <Link href="/weekly-structure">
          <strong>本周运势</strong>
          <span>七日结构一览</span>
        </Link>
        <Link href="/monthly-structure">
          <strong>本月运势</strong>
          <span>本月每日变化</span>
        </Link>
        <Link href="/yearly-structure">
          <strong>流年运势</strong>
          <span>自选年份查看</span>
        </Link>
      </nav>

      <section className="scenario-section" id="scenarios">
        <div className="section-heading">
          <div>
            <span className="eyebrow">运势 · 桃花 · 事业财运</span>
            <h2>热门测算</h2>
          </div>
          <span className="quiet-label">真实结构参考 · 高级判读逐步完善</span>
        </div>
        <div className="scenario-grid">
          {orderedProducts.map((item) => {
            const card = (
              <>
                <div className="scenario-card-top">
                  <span className="scenario-glyph">{item.glyph}</span>
                  <span className="scenario-state">{item.badge}</span>
                </div>
                <h3>{item.name.replace(" · 结构版", "").replace("流年结构", "流年运势")}</h3>
                <span className="scenario-tagline">{item.tagline}</span>
                <p>{item.description}</p>
                {item.status === "available" ? (
                  <span className="scenario-enter">
                    现在体验 <Icon name="arrow" size={15} />
                  </span>
                ) : (
                  <span className="scenario-disabled">
                    {item.status === "research" ? "研究中" : "能力补齐中"}
                  </span>
                )}
              </>
            );
            return item.href ? (
              <Link
                key={item.id}
                href={item.href}
                className={"scenario-card " + item.status + (keyProducts.has(item.id) ? " scenario-card-featured" : "")}
              >
                {card}
              </Link>
            ) : (
              <article key={item.id} className={"scenario-card " + item.status}>
                {card}
              </article>
            );
          })}
        </div>

        <div className="scenario-featured">
          <div>
            <span className="eyebrow">进阶探索 · 多场景汇总</span>
            <h3>{life.name} · 把 {baziProfile.name}、{yearly.name}、{romance.name}、{career.name} 聚到一起</h3>
            <p>
              现在不需要在多个页面之间来回拼答案。人生总览会一次调用真实 Scenario Engine，
              聚合四条已经验证的确定性链路，并保留 RuleMatch、Evidence 和 Trace。
              如果有一件具体的事想问，也可以使用六爻一事占问。
            </p>
          </div>
          <div className="scenario-featured-actions">
            <Link className="button primary" href="/life-overview">
              生成人生总览
              <Icon name="arrow" size={18} />
            </Link>
            <Link className="button outlined" href="/ask">
              有具体问题再占问
            </Link>
          </div>
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
