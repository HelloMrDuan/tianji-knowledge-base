import { useCallback, useState } from "react";
import { Dialog } from "../shared/Dialog";
import { Icon } from "../shared/Icon";
import { Link } from "../shared/router";
import { matchedEvidence, sampleLines, sampleRules } from "./fixtures";

function Yao({ yang, moving = false }: { yang: boolean; moving?: boolean }) {
  return (
    <span
      className={`yao ${yang ? "yang" : "yin"} ${moving ? "moving" : ""}`}
      aria-label={`${yang ? "阳" : "阴"}爻${moving ? "，动爻" : ""}`}
    >
      <i />
      <i />
    </span>
  );
}
function SectionTitle({
  number,
  title,
  note,
}: {
  number: string;
  title: string;
  note?: string;
}) {
  return (
    <div className="result-section-heading">
      <div>
        <span>{number}</span>
        <h2>{title}</h2>
      </div>
      {note && <small>{note}</small>}
    </div>
  );
}
export function LiuyaoResultPage({
  favorite,
  onToggleFavorite,
}: {
  favorite: boolean;
  onToggleFavorite: () => void;
}) {
  const [selectedLine, setSelectedLine] = useState<number | null>(null);
  const [selectedRule, setSelectedRule] = useState<number | null>(null);
  const [selectedEvidence, setSelectedEvidence] = useState<string | null>(null);
  const closeLine = useCallback(() => setSelectedLine(null), []);
  const closeRule = useCallback(() => setSelectedRule(null), []);
  const closeEvidence = useCallback(() => setSelectedEvidence(null), []);
  const line = sampleLines.find((item) => item.position === selectedLine);
  const evidence = matchedEvidence.find((item) => item.id === selectedEvidence);
  return (
    <div className="result-page">
      <div className="breadcrumb">
        <Link href="/">推演工具</Link>
        <Icon name="chevron" size={12} />
        <span>六爻示例</span>
      </div>
      <div className="result-page-title">
        <div>
          <span className="eyebrow">六爻 · 示例推演</span>
          <h1>一爻之变，循其来由</h1>
          <p>乾为天 · 初爻动 · 天风姤</p>
        </div>
        <button
          className={`button outlined favorite-button ${favorite ? "saved" : ""}`}
          onClick={onToggleFavorite}
          aria-pressed={favorite}
        >
          <Icon name="star" size={18} />
          {favorite ? "已收藏" : "收藏示例"}
        </button>
      </div>
      <div className="result-layout">
        <div className="result-content">
          <section className="result-basic">
            <SectionTitle number="一" title="基础信息" />
            <div className="basic-grid">
              <div>
                <span>推演时间</span>
                <strong>2026年10月2日 09:30</strong>
              </div>
              <div>
                <span>干支资料</span>
                <strong>甲子日 · 午月</strong>
              </div>
              <div>
                <span>装卦口径</span>
                <strong>京房八宫</strong>
              </div>
              <div>
                <span>示例范围</span>
                <strong>盘面结构 · 不作吉凶断语</strong>
              </div>
            </div>
            <p className="sample-note">
              <span className="note-dot" />
              静态视觉示例：时间与干支为展示资料，未进行真实排盘。
            </p>
          </section>
          <section className="chart-panel" id="chart">
            <SectionTitle
              number="二"
              title="核心盘面"
              note="点选一爻，查看完整信息"
            />
            <div className="chart-summary">
              <div>
                <span className="small-label">本卦 · 乾宫</span>
                <h3>
                  乾为天 <small>䷀</small>
                </h3>
              </div>
              <div className="change-label">
                <span>初爻动</span>
                <Icon name="arrow" size={25} />
              </div>
              <div>
                <span className="small-label">变卦</span>
                <h3>
                  天风姤 <small>䷫</small>
                </h3>
              </div>
            </div>
            <div
              className="chart-table"
              role="group"
              aria-label="六爻本卦与变卦逐爻对照"
            >
              <div className="chart-table-head" aria-hidden="true">
                <span>爻位</span>
                <span className="chart-extra">六神</span>
                <span className="chart-extra">六亲 · 纳甲</span>
                <span>本卦</span>
                <span>动变</span>
                <span>变卦</span>
                <span>标记</span>
              </div>
              {sampleLines.map((item) => (
                <button
                  className={`chart-line ${item.moving ? "is-moving" : ""}`}
                  key={item.position}
                  onClick={() => setSelectedLine(item.position)}
                  aria-label={`${item.label}${item.marker ? "，" + item.marker + "爻" : ""}${item.moving ? "，动爻" : ""}详情`}
                >
                  <span className="line-position">{item.label}</span>
                  <span className="chart-extra line-spirit">{item.spirit}</span>
                  <span className="chart-extra line-relative">
                    {item.relative}
                    <small>{item.branch}</small>
                  </span>
                  <Yao yang={item.yang} moving={item.moving} />
                  <span className="motion-symbol">
                    {item.moving ? "○" : "·"}
                  </span>
                  <Yao yang={item.moving ? !item.yang : item.yang} />
                  <span
                    className={`line-marker ${item.marker ? "has-marker" : ""}`}
                  >
                    {item.marker || (item.moving ? "动" : "—")}
                  </span>
                </button>
              ))}
            </div>
            <div className="chart-legend">
              <span>
                <i className="legend-line" />
                阳爻
              </span>
              <span>
                <i className="legend-line broken" />
                阴爻
              </span>
              <span>
                <i className="legend-dot" />
                动爻
              </span>
              <span>世 / 应为本卦位置标记</span>
            </div>
            <div className="chart-bottom">
              <span>本例旬空：戌、亥</span>
              <span>仅标示结构，不等同于吉凶结论</span>
            </div>
          </section>
          <section className="conclusions-section" id="conclusions">
            <SectionTitle number="三" title="核心结论" note="只总结盘面事实" />
            <div className="conclusion-grid">
              <article>
                <span>01</span>
                <h3>本卦为乾宫</h3>
                <p>六爻皆阳，世在上爻，应在三爻。</p>
              </article>
              <article>
                <span>02</span>
                <h3>变化来自初爻</h3>
                <p>初爻阳动转阴，变卦为天风姤。</p>
              </article>
              <article>
                <span>03</span>
                <h3>保留解读边界</h3>
                <p>此处不推断具体事情成败，也不补写应期。</p>
              </article>
            </div>
          </section>
          <section className="rules-section" id="rules">
            <SectionTitle number="四" title="规则命中" note="与这张盘面相关" />
            <div className="rule-list">
              {sampleRules.map((rule, index) => (
                <button
                  key={rule.title}
                  className="rule-item"
                  onClick={() => setSelectedRule(index)}
                >
                  <span className="rule-check">
                    <Icon name="check" size={16} />
                  </span>
                  <div>
                    <strong>{rule.title}</strong>
                    <p>{rule.brief}</p>
                  </div>
                  <span className="rule-reference">{rule.evidence}</span>
                  <Icon name="chevron" size={17} />
                </button>
              ))}
            </div>
          </section>
          <section className="evidence-section" id="evidence">
            <SectionTitle
              number="五"
              title="典籍依据"
              note="仅限本次示例相关片段"
            />
            <div className="evidence-cards">
              {matchedEvidence.map((item) => (
                <article className="evidence-card" key={item.id}>
                  <div className="evidence-card-top">
                    <span>《{item.book}》</span>
                    <span className="source-level">
                      {item.level} · 可追溯单一来源
                    </span>
                  </div>
                  <h3>{item.chapter}</h3>
                  <blockquote>{item.quote}</blockquote>
                  <div className="evidence-card-bottom">
                    <span>对应规则：{item.rule}</span>
                    <button onClick={() => setSelectedEvidence(item.id)}>
                      查看依据
                      <Icon name="chevron" size={14} />
                    </button>
                  </div>
                </article>
              ))}
            </div>
            <p className="evidence-boundary">
              仅呈现这次推演相关的必要原文；不提供整本古籍或全量证据浏览。
            </p>
          </section>
          <section className="ai-section" id="ai">
            <SectionTitle number="六" title="AI 解读" />
            <div className="ai-quiet-panel">
              <span className="ai-symbol">释</span>
              <div>
                <h3>盘面先行，解释有界</h3>
                <p>AI 解读暂未开放。你仍可查看完整盘面、命中规则与典籍依据。</p>
                <small>未来解释将区分盘面事实、依据与不确定之处。</small>
              </div>
              <span className="quiet-status">尚未开放</span>
            </div>
          </section>
          <details className="trace-section" id="trace">
            <summary>
              <span className="trace-icon">
                <Icon name="layers" size={19} />
              </span>
              <div>
                <strong>查看推演过程</strong>
                <small>按步骤了解这张盘的来由</small>
              </div>
              <Icon name="chevron" size={18} />
            </summary>
            <ol>
              {[
                "读取六个爻值，确认初爻为动爻。",
                "确定乾宫本卦，标明世爻与应爻。",
                "逐爻安纳甲、六亲与六神。",
                "初爻阳变阴，形成天风姤。",
                "关联本例规则与必要典籍片段。",
              ].map((step, i) => (
                <li key={step}>
                  <span>0{i + 1}</span>
                  {step}
                </li>
              ))}
            </ol>
            <p className="sample-note">
              这是一份示例过程说明，不展示内部调试数据。
            </p>
          </details>
        </div>
        <aside className="result-aside">
          <div className="result-toc">
            <span className="eyebrow">本次推演</span>
            <h3>从盘面，读到依据</h3>
            <nav aria-label="结果目录">
              {[
                ["chart", "核心盘面"],
                ["conclusions", "核心结论"],
                ["rules", "规则命中"],
                ["evidence", "典籍依据"],
                ["ai", "AI 解读"],
              ].map(([id, name], index) => (
                <a href={`#${id}`} key={id}>
                  <span>0{index + 1}</span>
                  {name}
                  <Icon name="chevron" size={14} />
                </a>
              ))}
            </nav>
            <p>
              先看结构，再读解释。
              <br />
              不确定的部分，不急于下结论。
            </p>
          </div>
          <div className="aside-note">
            <span>有据，亦有界。</span>
            <p>
              典籍片段说明规则来由，
              <br />
              不替代现实中的判断。
            </p>
          </div>
        </aside>
      </div>
      {line && (
        <Dialog
          title={`${line.label} · 盘面详情`}
          onClose={closeLine}
          className="public-dialog"
        >
          <div className="line-detail-grid">
            {[
              ["爻位", line.label],
              ["六神", line.spirit],
              ["六亲", line.relative],
              ["纳甲", line.branch],
              ["世应", line.marker || "未标记"],
              ["动静", line.moving ? "阳动，变阴" : "静爻"],
              ["旬空", line.empty ? "空亡标记" : "无空亡标记"],
            ].map(([k, v]) => (
              <div key={k}>
                <small>{k}</small>
                <strong>{v}</strong>
              </div>
            ))}
          </div>
          <p className="sample-note">静态示例中的结构资料，不代表吉凶判断。</p>
        </Dialog>
      )}
      {selectedRule !== null && (
        <Dialog
          title={sampleRules[selectedRule].title}
          onClose={closeRule}
          className="public-dialog"
        >
          <p>{sampleRules[selectedRule].detail}</p>
          <p className="sample-note">
            对应典籍片段：{sampleRules[selectedRule].evidence}
            。示例记录不等同于真实执行命中。
          </p>
        </Dialog>
      )}
      {evidence && (
        <Dialog
          title={`《${evidence.book}》· ${evidence.chapter}`}
          onClose={closeEvidence}
          className="public-dialog"
        >
          <span className="source-level">
            {evidence.level} · 可追溯单一来源
          </span>
          <blockquote className="evidence-detail-quote">
            {evidence.quote}
          </blockquote>
          <p>对应规则：{evidence.rule}</p>
          <p className="sample-note">{evidence.note}</p>
          <p className="sample-note">
            静态展示片段。正式联调后只接受当前推演实际返回的命中
            Evidence，不提供“浏览更多原文”。
          </p>
        </Dialog>
      )}
    </div>
  );
}
