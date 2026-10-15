import { useState } from "react";
import { Icon } from "../shared/Icon";
import { Link } from "../shared/router";
import { domainPages } from "./domainPages";
import "./pages.css";

export function LibraryPage({
  kind,
  favorite,
  onToggleFavorite,
}: {
  kind: "history" | "favorites";
  favorite: boolean;
  onToggleFavorite: () => void;
}) {
  const [query, setQuery] = useState("");
  const [domain, setDomain] = useState("全部工具");
  const visible =
    kind === "favorites" && favorite &&
    (domain === "全部工具" || domain === "六爻") &&
    "乾为天 天风姤 六爻 固定视觉示例".includes(query.trim());
  return (
    <div className="library-page">
      <div className="breadcrumb">
        <Link href="/">天机</Link>
        <Icon name="chevron" size={12} />
        <span>{kind === "history" ? "历史记录" : "我的收藏"}</span>
      </div>
      <header className="library-heading">
        <div>
          <span className="eyebrow">
            {kind === "history" ? "READING JOURNAL" : "SAVED READINGS"}
          </span>
          <h1>
            {kind === "history"
              ? "让每一次研究，有迹可循。"
              : "把值得回看的，留在手边。"}
          </h1>
          <p>
            {kind === "history"
              ? "当前尚未启用真实推演历史保存；演示卦例不会冒充您的计算记录。"
              : "这里只展示您主动收藏的固定演示卦例，不包含个人出生或占时资料。"}
          </p>
        </div>
        <Icon name={kind === "history" ? "clock" : "star"} size={48} />
      </header>
      {kind === "favorites" && <div className="library-toolbar">
        <label>
          <Icon name="search" size={18} />
          <input
            aria-label="搜索记录"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="搜索卦名或示例"
          />
        </label>
        <select
          aria-label="工具筛选"
          value={domain}
          onChange={(e) => setDomain(e.target.value)}
        >
          {["全部工具", ...domainPages.map((p) => p.name)].map((name) => (
            <option key={name}>{name}</option>
          ))}
        </select>
      </div>}
      {visible ? (
        <section className="journal-list">
          <div className="journal-date">
            <span>演示收藏（非真实推演历史）</span>
            <small>DEMO · 固定样例</small>
          </div>
          <article className="journal-row">
            <span className="journal-glyph">爻</span>
            <div>
              <span className="eyebrow">六爻 · 结构研究</span>
              <h2>
                <Link href="/liuyao/result">乾为天 → 天风姤</Link>
              </h2>
              <p>初爻动 · 京房八宫 · 静态视觉示例</p>
            </div>
            <button
              className="journal-save"
              aria-label={favorite ? "取消收藏示例" : "收藏示例"}
              aria-pressed={favorite}
              onClick={onToggleFavorite}
            >
              <Icon name="star" size={20} />
            </button>
            <Link className="journal-open" href="/liuyao/result">
              查看
              <Icon name="arrow" size={18} />
            </Link>
          </article>
        </section>
      ) : (
        <div className="library-empty">
          <Icon name={kind === "favorites" ? "star" : "search"} size={42} />
          <h2>
            {kind === "history"
              ? "暂无真实推演历史"
              : !favorite ? "还没有收藏" : "没有匹配的记录"}
          </h2>
          <p>
            {kind === "history"
              ? "目前不会自动保存八字、运势或占问结果；这里没有已保存的真实记录。"
              : !favorite ? "在六爻示例页点“收藏”，可以保存该演示页面入口。"
              : "试试其他卦名，或者清除当前筛选。"}
          </p>
          <Link className="button primary" href={kind === "history" ? "/ask" : "/liuyao/result"}>
            {kind === "history" ? "前往一事占问" : "查看六爻示例"}
            <Icon name="arrow" size={16} />
          </Link>
          {kind === "favorites" && <button
            className="entry-reset"
            onClick={() => {
              setDomain("全部工具");
              setQuery("");
            }}
          >
            清除筛选
          </button>}
        </div>
      )}
      <div className="entry-return">
        <Link className="text-action" href="/">
          开始新的研究
          <Icon name="arrow" size={16} />
        </Link>
        <p>固定示例仅可收藏为演示入口，不会自动生成个人推演历史。</p>
      </div>
    </div>
  );
}
