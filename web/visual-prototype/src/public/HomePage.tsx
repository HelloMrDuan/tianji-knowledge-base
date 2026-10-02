import { Icon } from "../shared/Icon";
import { Link, useNotice } from "../shared/router";
import { InkLandscape } from "./InkLandscape";
import { recentSamples, tools } from "./fixtures";

export function HomePage() {
  const notice = useNotice();
  return (
    <>
      <section className="public-hero">
        <InkLandscape />
        <div className="hero-copy">
          <div className="eyebrow">
            <span />
            东方术数 · 当代表达
          </div>
          <h1>
            观象，循理。
            <br />
            <span>让推演有据可寻。</span>
          </h1>
          <p>
            从一张清晰的盘面出发，读懂规则，核对典籍。
            <br className="desktop-only" />
            把每一步的来由，留在结果之中。
          </p>
          <div className="hero-actions">
            <Link className="button primary" href="/liuyao/result">
              查看六爻示例
              <Icon name="arrow" size={18} />
            </Link>
            <a className="text-action" href="#tools">
              选择推演工具
              <Icon name="chevron" size={16} />
            </a>
          </div>
          <div className="hero-footnote">
            <span className="tiny-seal">序</span>排盘有序 · 规则有迹 · 典籍有据
          </div>
        </div>
        <div className="landscape-caption">
          山静水长
          <br />
          <span>以象见理</span>
        </div>
      </section>
      <section id="tools" className="tools-section">
        <div className="section-heading">
          <div>
            <span className="eyebrow">七种入口 · 各循其法</span>
            <h2>择一门，开始推演</h2>
          </div>
          <span className="quiet-label">当前开放六爻视觉示例</span>
        </div>
        <div className="tool-grid">
          {tools.map((tool, index) => (
            <article
              key={tool.name}
              className={`tool-card ${tool.available ? "featured" : ""}`}
            >
              <div className="tool-top">
                <span className="tool-glyph">{tool.glyph}</span>
                <span className="tool-index">0{index + 1}</span>
              </div>
              <h3>{tool.name}</h3>
              <p>{tool.subtitle}</p>
              {tool.available ? (
                <Link href="/liuyao/result" className="tool-action">
                  查看示例
                  <Icon name="arrow" size={17} />
                </Link>
              ) : (
                <button
                  className="tool-action muted"
                  onClick={() =>
                    notice("此工具尚未开放。本轮可以先查看六爻示例。")
                  }
                >
                  尚未开放<span>—</span>
                </button>
              )}
            </article>
          ))}
          <div className="tool-philosophy">
            <span>循</span>
            <p>
              不急于一句结论，
              <br />
              先看清推演的来由。
            </p>
            <small>天机 · 观象循理</small>
          </div>
        </div>
      </section>
      <section className="recent-section" id="recent">
        <div className="section-heading">
          <div>
            <span className="eyebrow">留住每一次思考</span>
            <h2>最近使用</h2>
          </div>
          <span className="quiet-label">静态示例记录</span>
        </div>
        <div className="recent-grid">
          {recentSamples.map((item, index) => (
            <Link className="recent-card" href={item.href} key={item.name}>
              <span className="recent-symbol">{index === 0 ? "䷀" : "爻"}</span>
              <div>
                <span className="small-label">
                  {item.type} · {item.when}
                </span>
                <h3>{item.name}</h3>
                <p>{item.subtitle}</p>
              </div>
              <Icon name="arrow" size={19} />
            </Link>
          ))}
        </div>
      </section>
      <section className="example-banner">
        <div className="mini-hexagram" aria-hidden="true">
          {[1, 1, 1, 1, 1, 1].map((_, i) => (
            <span key={i} className={i === 5 ? "gold-line" : ""} />
          ))}
        </div>
        <div>
          <span className="eyebrow">一例知其序</span>
          <h2>从乾为天，到天风姤</h2>
          <p>查看一爻之变如何落在盘面、规则与典籍依据中。</p>
        </div>
        <Link className="button outlined" href="/liuyao/result">
          展开示例
          <Icon name="arrow" size={18} />
        </Link>
      </section>
      <section className="product-principles">
        <div>
          <Icon name="grid" size={24} />
          <h3>盘面为先</h3>
          <p>
            结构清晰，位置明确。
            <br />
            解释始终围绕当前盘面。
          </p>
        </div>
        <div>
          <Icon name="book" size={24} />
          <h3>典籍为据</h3>
          <p>
            只展示本次推演相关片段，
            <br />
            让规则与依据相互对应。
          </p>
        </div>
        <div>
          <Icon name="shield" size={24} />
          <h3>边界清楚</h3>
          <p>
            计算事实与综合解释分开，
            <br />
            未确定之处如实保留。
          </p>
        </div>
      </section>
    </>
  );
}
