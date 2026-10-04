import { Icon } from "../shared/Icon";
import { Link } from "../shared/router";
import { InkLandscape } from "./InkLandscape";
import { domainPages } from "./domainPages";
import { scenarioProducts } from "./scenarioProducts";
import "./scenarios.css";

export function HomePage() {
  const question = scenarioProducts.find((item) => item.id === "question")!;
  const baziProfile = scenarioProducts.find((item) => item.id === "bazi-profile")!;
  const yearly = scenarioProducts.find((item) => item.id === "yearly")!;
  const romance = scenarioProducts.find((item) => item.id === "romance")!;
  const career = scenarioProducts.find((item) => item.id === "career")!;
  return (
    <div className="scenario-home">
      <section className="scenario-hero">
        <InkLandscape />
        <div className="scenario-hero-copy">
          <div className="eyebrow"><span />天机 · 生活场景</div>
          <h1>
            今天，你最想看哪一件事？
            <span>把复杂术数，收进一个可读的答案里。</span>
          </h1>
          <p>
            不要求你懂八字、六爻或奇门。先从你真正关心的问题开始，
            后台再选择已经验证的确定性引擎、规则与典籍依据。
          </p>
          <div className="scenario-hero-actions">
            <Link className="button primary" href="/ask">
              一事占问
              <Icon name="arrow" size={18} />
            </Link>
            <a className="text-action" href="#scenarios">
              看全部场景
              <Icon name="chevron" size={16} />
            </a>
          </div>
          <div className="scenario-proof">
            <span><i />确定性计算先行</span>
            <span><i />规则与典籍可追溯</span>
            <span><i />AI 未校准前不自动公开</span>
          </div>
        </div>
      </section>

      <section className="scenario-section" id="scenarios">
        <div className="section-heading">
          <div>
            <span className="eyebrow">先选你关心的事</span>
            <h2>生活场景</h2>
          </div>
          <span className="quiet-label">可用能力先开放，其余不伪造</span>
        </div>
        <div className="scenario-grid">
          {scenarioProducts.map((item) => {
            const card = (
              <>
                <div className="scenario-card-top">
                  <span className="scenario-glyph">{item.glyph}</span>
                  <span className="scenario-state">{item.badge}</span>
                </div>
                <h3>{item.name}</h3>
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
                className={"scenario-card " + item.status}
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
            <span className="eyebrow">五条真实闭环</span>
            <h3>{baziProfile.name} + {question.name} + {yearly.name} + {romance.name} + {career.name}</h3>
            <p>
              八字基础档案与六爻一事占问调用 <code>/api/v1/execute</code>，
              2026 流年、桃花姻缘与事业财运结构都调用真实 Scenario Engine。五条链路均返回确定性结果、规则、
              Evidence 和 Trace；后端不可用就明确报错，不拿静态示例冒充结果。
            </p>
          </div>
          <div className="scenario-featured-actions">
            <Link className="button outlined" href="/bazi-profile">
              建立八字档案
            </Link>
            <Link className="button outlined" href="/yearly-structure">
              看 2026 结构
            </Link>
            <Link className="button outlined" href="/romance-structure">
              看桃花结构
            </Link>
            <Link className="button outlined" href="/career-wealth-structure">
              看事业财运结构
            </Link>
            <Link className="button primary" href="/ask">
              开始占问
              <Icon name="arrow" size={18} />
            </Link>
          </div>
        </div>
      </section>

      <section className="professional-section" id="professional">
        <div className="section-heading">
          <div>
            <span className="eyebrow">懂术数的人仍可直接进入</span>
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
        <span className="eyebrow">听一曲 · 再问一事</span>
      </section>
    </div>
  );
}
