import { useEffect, useMemo, useState } from "react";
import { Icon } from "../shared/Icon";
import { Link } from "../shared/router";
import {
  loadReadings,
  removeReading,
  subscribeReadings,
  toggleReadingFavorite,
  type ReadingRecord,
} from "./readingLibrary";
import "./pages.css";

function formatWhen(value: string) {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "本地记录";
  return new Intl.DateTimeFormat("zh-CN", {
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  }).format(date);
}

export function LibraryPage({ kind }: { kind: "history" | "favorites" }) {
  const [query, setQuery] = useState("");
  const [scenario, setScenario] = useState("全部场景");
  const [records, setRecords] = useState<ReadingRecord[]>(() => loadReadings());

  useEffect(() => subscribeReadings(() => setRecords(loadReadings())), []);

  const source = kind === "favorites" ? records.filter((item) => item.favorite) : records;
  const scenarioOptions = useMemo(
    () => ["全部场景", ...Array.from(new Set(source.map((item) => item.label)))],
    [source],
  );
  const visible = source.filter((item) => {
    const matchesScenario = scenario === "全部场景" || item.label === scenario;
    const needle = query.trim().toLowerCase();
    const matchesQuery =
      !needle ||
      [item.label, item.title, item.subtitle]
        .join(" ")
        .toLowerCase()
        .includes(needle);
    return matchesScenario && matchesQuery;
  });

  function refresh(next: ReadingRecord[]) {
    setRecords(next);
  }

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
            {kind === "history" ? "LOCAL READING JOURNAL" : "LOCAL FAVORITES"}
          </span>
          <h1>
            {kind === "history"
              ? "真实推演，才会留下记录。"
              : "把真正算过的结果，留在手边。"}
          </h1>
          <p>
            {kind === "history"
              ? "这里只记录当前浏览器里成功完成的真实计算摘要；计算失败、静态示例都不会进入历史。"
              : "收藏来自真实历史记录，只保存在当前浏览器，不同步到账号或服务器。"}
          </p>
        </div>
        <Icon name={kind === "history" ? "clock" : "star"} size={48} />
      </header>

      <div className="library-privacy-note">
        <Icon name="check" size={15} />
        <span>本地存储：不保存完整 Evidence / Trace，也不会额外复制出生时间或占问文本。</span>
      </div>

      <div className="library-toolbar">
        <label>
          <Icon name="search" size={18} />
          <input
            aria-label="搜索记录"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="搜索场景或结果摘要"
          />
        </label>
        <select
          aria-label="场景筛选"
          value={scenario}
          onChange={(e) => setScenario(e.target.value)}
        >
          {scenarioOptions.map((name) => <option key={name}>{name}</option>)}
        </select>
      </div>

      {visible.length ? (
        <section className="journal-list">
          <div className="journal-date">
            <span>{kind === "history" ? "真实本地记录" : "已收藏记录"}</span>
            <small>{visible.length} 条 · 当前浏览器</small>
          </div>
          {visible.map((item) => (
            <article className="journal-row" key={item.id}>
              <span className="journal-glyph">{item.glyph}</span>
              <div>
                <span className="eyebrow">{item.label} · 真实计算</span>
                <h2>{item.title}</h2>
                <p>{item.subtitle} · {formatWhen(item.createdAt)}</p>
              </div>
              <button
                className={"journal-save" + (item.favorite ? " saved" : "")}
                aria-label={item.favorite ? `取消收藏：${item.title}` : `收藏：${item.title}`}
                aria-pressed={item.favorite}
                onClick={() => refresh(toggleReadingFavorite(item.id))}
              >
                <Icon name="star" size={20} />
              </button>
              <Link className="journal-open" href={item.href}>
                打开工具
                <Icon name="arrow" size={18} />
              </Link>
              <button
                className="journal-delete"
                aria-label={`删除记录：${item.title}`}
                onClick={() => refresh(removeReading(item.id))}
              >
                删除
              </button>
            </article>
          ))}
        </section>
      ) : (
        <div className="library-empty">
          <Icon name={kind === "favorites" ? "star" : "clock"} size={42} />
          <h2>
            {source.length === 0
              ? kind === "favorites" ? "还没有真实收藏" : "还没有真实推演记录"
              : "没有匹配的记录"}
          </h2>
          <p>
            {source.length === 0
              ? "完成一次真实排盘或场景计算后，这里才会出现记录。"
              : "试试其他关键词，或者清除当前筛选。"}
          </p>
          <Link className="button primary" href="/">
            开始一次真实推演
            <Icon name="arrow" size={16} />
          </Link>
          {(query || scenario !== "全部场景") && (
            <button
              className="entry-reset"
              onClick={() => {
                setScenario("全部场景");
                setQuery("");
              }}
            >
              清除筛选
            </button>
          )}
        </div>
      )}

      <div className="entry-return">
        <Link className="text-action" href="/">
          开始新的研究
          <Icon name="arrow" size={16} />
        </Link>
        <p>这里只展示真实执行后生成的本地摘要，不混入固定 Demo。</p>
      </div>
    </div>
  );
}
