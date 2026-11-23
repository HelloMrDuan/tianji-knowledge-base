/**
 * TJ-0422 phase 2 slice A: interactive dayun timeline.
 *
 * Replaces the static <ol> on the bazi-profile page. Everything shown
 * comes from the backend dayun presentation passed in: the two method
 * views are rendered separately and never merged, and no age, no
 * single handover date, and no luck verdict is ever produced here.
 *
 * - Each period is a button; clicking it opens the detail panel.
 * - The current period is highlighted from today's date against the
 *   returned start intervals only. A today inside a start interval is
 *   shown explicitly as "可能处于交运前后", never forced into one side.
 * - A period's end is only ever described from the next period's
 *   start interval ("约在下一运交运区间之前结束"); the last period
 *   honestly shows its end as "未提供".
 * - The detail panel links onward: into the career page, and into the
 *   yearly page for individual years (which writes the shared year key
 *   and arms a one-shot auto-load via requestYearView).
 */
import { Link } from "../shared/router";
import {
  locateCurrentPeriod,
  requestYearView,
  STEM_ELEMENTS,
  BRANCH_ELEMENTS,
  type DayunEntry,
  type DayunMethod,
  type DayunPresentation,
} from "./yearContext";
import "./dayun-timeline.css";

const dayunReasonLabels: Record<string, string> = {
  zero_jie_boundary_convention_unreviewed:
    "出生时刻恰逢节气交界，交运换算口径尚未裁定",
  zero_day_count_not_exemplified_in_text:
    "本口径以整日计数，本盘整日数为零，原文未给出此情形的示例",
};

/** Years offered as yearly-page links for one period (navigation only). */
function entryYears(entry: DayunEntry, next: DayunEntry | undefined): number[] {
  if (entry.state !== "interval" || !entry.start_interval) return [];
  const startYear = new Date(entry.start_interval.earliest).getFullYear();
  if (Number.isNaN(startYear)) return [];
  if (!next) return [startYear];
  if (next.state === "interval" && next.start_interval) {
    const nextYear = new Date(next.start_interval.earliest).getFullYear();
    if (Number.isNaN(nextYear) || nextYear <= startYear) return [startYear];
    const years: number[] = [];
    for (let year = startYear; year < nextYear; year += 1) years.push(year);
    return years;
  }
  return [startYear];
}

export function DayunTimeline({
  presentation,
  method,
  selectedPeriodIndex,
  onSelectPeriod,
  today,
}: {
  presentation: DayunPresentation;
  method: DayunMethod;
  selectedPeriodIndex: number | null;
  onSelectPeriod: (periodIndex: number) => void;
  today?: Date;
}) {
  const view = presentation.methods[method];
  if (!view) {
    return <p className="bazi-dayun-not-judgeable">本口径暂无大运呈现。</p>;
  }
  const entries = [...(view.entries || [])].sort((a, b) => a.period_index - b.period_index);
  const pillars = view.natal.pillars;
  const unresolvedReason = typeof view.reason === "string" ? view.reason : "";
  const current = locateCurrentPeriod(presentation, method, today ?? new Date());
  const effectiveSelected =
    selectedPeriodIndex ??
    (current.status === "current" ? current.periodIndex : null) ??
    (current.status === "ambiguous" ? current.toPeriodIndex : null) ??
    entries[0]?.period_index ??
    null;
  const selected = entries.find((entry) => entry.period_index === effectiveSelected) ?? null;
  const selectedIndex = selected ? entries.findIndex((entry) => entry === selected) : -1;
  const nextEntry = selectedIndex >= 0 ? entries[selectedIndex + 1] : undefined;
  const dayMaster = pillars?.day_master;

  return (
    <div className="bazi-dayun-method">
      <p>
        四柱 {pillars.year} · {pillars.month} · {pillars.day} · {pillars.hour}，日主 {pillars.day_master}；
        大运方向：{view.direction.label}（{view.direction.counting_target === "future_jie" ? "数至出生后之节" : "数至出生前之节"}：{view.direction.counted_jie.name} {view.direction.counted_jie.at}）。
      </p>
      {view.status === "unresolved" ? (
        <p className="bazi-dayun-not-judgeable">
          交运时间暂不可判：{dayunReasonLabels[unresolvedReason] || unresolvedReason}。
        </p>
      ) : (
        <>
          {view.method === "sanming" ? (
            <p>
              交运时长区间 {view.duration.interval_days.min_days}–{view.duration.interval_days.max_days} 日（不含上限）：
              共数 {view.duration.counting.whole_shichen_counted} 个时辰，计 {view.duration.decomposition.whole_year_units} 年单位又 {view.duration.decomposition.remainder_shichen} 时辰，折 {view.duration.decomposition.remainder_days} 日
              {view.duration.decomposition.remainder_months_of_30_days != null ? `，其中含 ${view.duration.decomposition.remainder_months_of_30_days} 个整月` : ""}；未作舍入。
            </p>
          ) : (
            <p>
              交运时长区间 {view.duration.interval_days.min_days}–{view.duration.interval_days.max_days} 日（不含上限）：
              整日 {view.duration.counting.whole_days} 日，原文折算 {view.duration.text_result_days} 日。{view.duration.granularity_note}
            </p>
          )}
          <ol className="dayun-timeline">
            {entries.map((entry) => {
              const isCurrent = current.status === "current" && current.periodIndex === entry.period_index;
              const isAmbiguous =
                current.status === "ambiguous" && current.toPeriodIndex === entry.period_index;
              const isSelected = entry.period_index === effectiveSelected;
              return (
                <li key={entry.period_index} data-period={entry.period_index}>
                  <button
                    type="button"
                    className={[
                      "dayun-timeline-entry",
                      isSelected ? "selected" : "",
                      isCurrent ? "current" : "",
                      isAmbiguous ? "ambiguous" : "",
                    ].join(" ")}
                    aria-pressed={isSelected}
                    aria-current={isCurrent ? "true" : undefined}
                    onClick={() => onSelectPeriod(entry.period_index)}
                  >
                    <strong>第 {entry.period_index} 运 {entry.ganzhi}</strong>
                    <span>（{entry.ten_god_relative_to_natal_day_stem}）</span>
                    {isCurrent && <span className="dayun-current-badge">当前</span>}
                    {isAmbiguous && <span className="dayun-ambiguous-badge">可能处于交运前后</span>}
                    {entry.state === "interval" && entry.start_interval && (
                      <span>交运区间：{entry.start_interval.earliest} 至 {entry.start_interval.latest}（不含上限）</span>
                    )}
                    {entry.state === "not_provided" && (
                      <span>交运区间未提供：本口径只呈现首运交运区间。</span>
                    )}
                    {entry.state === "unresolved" && (
                      <span>交运时间暂不可判。</span>
                    )}
                  </button>
                </li>
              );
            })}
          </ol>

          {selected && (
            <article className="dayun-detail" aria-label={`第 ${selected.period_index} 运详情`}>
              <h4>第 {selected.period_index} 运 {selected.ganzhi}</h4>
              <p>
                天干 {selected.stem}（{STEM_ELEMENTS[selected.stem] || "—"}）·
                地支 {selected.branch}（{BRANCH_ELEMENTS[selected.branch] || "—"}）
                {dayMaster ? `；相对日主 ${dayMaster} 为${selected.ten_god_relative_to_natal_day_stem}` : `；相对日主为${selected.ten_god_relative_to_natal_day_stem}`}。
              </p>
              {selected.state === "interval" && selected.start_interval && (
                <p>
                  交运区间：{selected.start_interval.earliest} 至 {selected.start_interval.latest}（不含上限）。
                  交运时刻只给出区间，不折算为单点日期，也不折算起运年龄。
                </p>
              )}
              {selected.state === "not_provided" && (
                <p>交运区间未提供：本口径只呈现首运交运区间。</p>
              )}
              {selected.state === "unresolved" && (
                <p>交运时间暂不可判。</p>
              )}
              {nextEntry ? (
                nextEntry.state === "interval" && nextEntry.start_interval ? (
                  <p>
                    本运约在下一运交运区间之前结束：结束于第 {nextEntry.period_index} 运交运区间（{nextEntry.start_interval.earliest} 至 {nextEntry.start_interval.latest}，不含上限）内。
                  </p>
                ) : (
                  <p>下一运交运区间未提供，本运终点未提供。</p>
                )
              ) : (
                <p>末段无终点：未提供。</p>
              )}
              {current.status === "ambiguous" && current.toPeriodIndex === selected.period_index && (
                <p className="dayun-ambiguous-note">
                  今日可能处于交运前后：
                  {current.fromPeriodIndex !== null
                    ? `第 ${current.fromPeriodIndex} 运${current.fromGanzhi ? ` ${current.fromGanzhi}` : ""}与第 ${current.toPeriodIndex} 运 ${current.toGanzhi}之间`
                    : `首运开始之前与第 ${current.toPeriodIndex} 运 ${current.toGanzhi}之间`}
                  ，不强行定归属。
                </p>
              )}
              {(() => {
                const years = entryYears(selected, nextEntry);
                if (years.length === 0) return null;
                return (
                  <div className="dayun-year-links">
                    <span>进入流年页查看其中某年：</span>
                    <div>
                      {years.map((year) => (
                        <Link
                          key={year}
                          href="/yearly-structure"
                          onClick={() => requestYearView(year)}
                        >
                          {year} 年
                        </Link>
                      ))}
                    </div>
                    <small>
                      交运当年的所属大运以流年页的定位为准。
                      {!nextEntry ? "末运无终点，此处仅列出起始年份供导航。" : ""}
                    </small>
                  </div>
                );
              })()}
              <div className="dayun-detail-links">
                <Link href="/career-wealth-structure">进入事业财运页</Link>
                <small>事业财运页需另选目标年份与传统口径；该页的大运呈现只含首运。</small>
              </div>
            </article>
          )}
        </>
      )}
      {view.notices.map((notice: any) => (
        <p key={notice.code} className="bazi-dayun-notice">{notice.text}</p>
      ))}
      <details className="bazi-evidence-entry">
        <summary>查看判断依据</summary>
        <blockquote>
          <b>{view.direction.rule_quote.quote}</b>
        </blockquote>
        {view.sources.flatMap((block: any) => block.quotes
          .filter((q: any) => q.id !== view.direction.rule_quote.id)
          .map((q: any) => (
            <blockquote key={q.id}><p>{q.quote}</p></blockquote>
          )))}
      </details>
    </div>
  );
}
