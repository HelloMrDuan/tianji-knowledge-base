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
    (kind === "history" || favorite) &&
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
              ? "这里展示固定静态样例，不代表保存过真实推演。"
              : "收藏状态仅保存在当前浏览器，不保存出生或占时资料。"}
          </p>
        </div>
        <Icon name={kind === "history" ? "clock" : "star"} size={48} />
      </header>
      <div className="library-toolbar">
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
      </div>
      {visible ? (
        <section className="journal-list">
          <div className="journal-date">
            <span>演示记录</span>
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
            {kind === "favorites" && !favorite
              ? "还没有收藏"
              : "没有匹配的记录"}
          </h2>
          <p>
            {kind === "favorites" && !favorite
              ? "在六爻示例页点“收藏”，方便下次回看。"
              : "试试其他卦名，或者清除当前筛选。"}
          </p>
          <Link className="button primary" href="/liuyao/result">
            查看六爻示例
            <Icon name="arrow" size={16} />
          </Link>
          <button
            className="entry-reset"
            onClick={() => {
              setDomain("全部工具");
              setQuery("");
            }}
          >
            清除筛选
          </button>
        </div>
      )}
      <div className="entry-return">
        <Link className="text-action" href="/">
          开始新的研究
          <Icon name="arrow" size={16} />
        </Link>
        <p>演示记录与真实推演记录分别呈现。</p>
      </div>
    </div>
  );
}
