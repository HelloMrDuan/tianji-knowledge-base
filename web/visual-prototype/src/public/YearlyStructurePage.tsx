import { useEffect, useRef, useState } from "react";
import type { FormEvent } from "react";
import { ConsumerResultSummary } from "./ConsumerResultSummary";
import { Icon } from "../shared/Icon";
import { Link } from "../shared/router";
import { executeYearlyScenario, type ScenarioExecuteResponse } from "./api";
import { isValidTargetYear, MIN_TARGET_YEAR, MAX_TARGET_YEAR } from "./targetYear";
import {
  BRANCH_ELEMENTS,
  consumePendingYearRequest,
  getDayunPresentation,
  getSelectedDayunMethod,
  getSelectedYear,
  locateYearInDayun,
  requestDayunReturn,
  setSelectedYear,
  STEM_ELEMENTS,
  subscribe as subscribeYearContext,
  type DayunMethod,
  type DayunPresentation,
} from "./yearContext";
import { readSavedBirthProfile, saveBirthProfile } from "./birthProfile";
import { toApiValue, toApiZone, fromLegacy, toSolarDateString, isConvertedFromLunar, fromSolarEdit, withUpdatedTime, getSavedBirthFingerprint } from "./birthProfile";
import "./yearly-structure.css";

const relationNames: Record<string, string> = {
  six_harmony: "六合",
  harm: "六害",
  clash: "六冲",
};

const pillarNames: Record<string, string> = {
  year: "年柱",
  month: "月柱",
  day: "日柱",
  hour: "时柱",
};

function displayEvidence(id: string, source: Record<string, any>) {
  const title = source.classic_title || source.title || source.source_title;
  const quote = source.original_text;
  if (typeof title !== "string" || !title.trim() ||
      typeof quote !== "string" || !quote.trim()) {
    return null;
  }
  return {
    id,
    title,
    quote,
    grade: typeof source.evidence_level === "string" ? source.evidence_level : "未标注",
    excerpt: source.original_text_excerpt === true || source.classic_title_excerpt === true,
  };
}

const dayunMethodLabels: Record<DayunMethod, string> = {
  sanming: "三命通会",
  shenfeng: "神峰通考",
};

export function YearlyStructurePage() {
  const [date, setDate] = useState(() => toSolarDateString(readSavedBirthProfile()));
  const [time, setTime] = useState(() => readSavedBirthProfile().time);
  const [targetYear, setTargetYear] = useState(getSelectedYear);
  const [result, setResult] = useState<ScenarioExecuteResponse | null>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  // TJ-0422 phase 2 slice A: session-shared dayun presentation (set by
  // the bazi page) and the method tab selected there; used only to
  // locate this year inside the returned intervals. Reads are
  // fingerprint-checked against the saved birth data (PR #594
  // re-review fix): when the birth data changed on this page, the
  // old presentation reads back as null and the section shows
  // "尚未查看大运" instead of the old data's dayun.
  const [dayunPresentation, setDayunPresentation] = useState<DayunPresentation | null>(() => getDayunPresentation(getSavedBirthFingerprint()));
  const [dayunMethod, setDayunMethod] = useState<DayunMethod>(() => getSelectedDayunMethod());
  const requestVersion = useRef(0);

  useEffect(() => () => { requestVersion.current += 1; }, []);

  // TJ-0422 phase 2 slice A: stay in sync with the shared year key and
  // the session dayun state (e.g. after a timeline year link).
  useEffect(() => subscribeYearContext(() => {
    setTargetYear((prev) => {
      const next = getSelectedYear();
      return prev === next ? prev : next;
    });
    setDayunPresentation(getDayunPresentation(getSavedBirthFingerprint()));
    setDayunMethod(getSelectedDayunMethod());
  }), []);

  // TJ-0422 phase 2 slice A: a timeline year link arms a one-shot
  // request; on arrival the yearly scenario is loaded for that year
  // at once (birth data is reused from the saved profile, never
  // re-entered). Without a saved birth profile only the year field
  // is set and the user submits as before.
  useEffect(() => {
    const pending = consumePendingYearRequest();
    if (pending === null) return;
    if (!readSavedBirthProfile().year) return;
    void requestYearly(pending);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  function invalidateResult() {
    requestVersion.current += 1;
    setResult(null);
    setError("");
    setLoading(false);
  }

  function fillSample() {
    invalidateResult();
    setDate("2000-01-07");
    setTime("12:00");
  }

  async function requestYearly(year: number) {
    const version = ++requestVersion.current;
    setLoading(true);
    setError("");
    setResult(null);
    try {
      if (!isValidTargetYear(year)) throw new Error("请选择 1901 至 2098 年的公历年份");
      const response = await executeYearlyScenario({
        birth_value: (() => {
        const currentProfile = readSavedBirthProfile();
        const initialSolar = toSolarDateString(currentProfile);
        if (date === initialSolar && time === currentProfile.time) {
          return toApiValue(currentProfile);
        }
        if (date === initialSolar) {
          return toApiValue(withUpdatedTime(currentProfile, time));
        }
        return toApiValue(fromSolarEdit(date, time, currentProfile.region, currentProfile));
      })(),
        target_year: year,
        birth_zone: toApiZone(readSavedBirthProfile()),
      });
      if (version !== requestVersion.current) return;
      (() => {
        const currentProfile = readSavedBirthProfile();
        const initialSolar = toSolarDateString(currentProfile);
        if (date === initialSolar && time === currentProfile.time) {
          return;
        }
        if (date === initialSolar) {
          saveBirthProfile(withUpdatedTime(currentProfile, time));
          return;
        }
        saveBirthProfile(fromSolarEdit(date, time, currentProfile.region, currentProfile));
      })();
      setSelectedYear(year);
      setResult(response);
    } catch (err) {
      if (version === requestVersion.current)
        setError(err instanceof Error ? err.message : "年度结构计算失败。");
    } finally {
      if (version === requestVersion.current) setLoading(false);
    }
  }

  async function submit(event: FormEvent) {
    event.preventDefault();
    await requestYearly(targetYear);
  }

  // TJ-0422 phase 2 slice A: step to the previous/next year. The year
  // is written to the shared key and the scenario is re-requested at
  // once when a result is already on screen; the birth date/time
  // edits on this page are left untouched (no unsaved change is lost).
  async function changeYear(next: number) {
    if (!isValidTargetYear(next) || next === targetYear) return;
    setTargetYear(next);
    setSelectedYear(next);
    if (result) await requestYearly(next);
  }

  const annual = result?.result?.target_year || {};
  const natal = result?.result?.natal || {};
  const branchRelations = result?.result?.annual_branch_interactions;
  const branchHits: Array<any> = Array.isArray(branchRelations?.hits) ? branchRelations.hits : [];
  const pillars = Array.isArray(natal.pillars) ? natal.pillars : [];
  const evidence = result
    ? Object.entries(result.evidence).map(([id, value]) => displayEvidence(id, value))
        .filter((item): item is NonNullable<typeof item> => item !== null)
    : [];
  const evidenceById = new Map(evidence.map((item) => [item.id, item]));
  // TJ-0422 phase 2 slice A: locate this year inside the session-shared
  // dayun presentation (returned intervals only; never computed here).
  const yearLocation = locateYearInDayun(dayunPresentation, dayunMethod, targetYear);

  return (
    <div className="yearly-page">
      <div className="breadcrumb">
        <Link href="/">生活场景</Link>
        <Icon name="chevron" size={12} />
        <span>{targetYear} 流年结构</span>
      </div>

      <section className="yearly-hero">
        <div>
          <span className="eyebrow">{targetYear} · 流年结构内测</span>
          <h1>看看 {targetYear} 年的流年运势。</h1>
          <p>
            这一版已经是真实计算，但还不是“全年吉凶报告”。它只把出生四柱、{targetYear}
            干支、流年天干十神及流年地支与四柱的已审核冲合害关系放到一起，并给出来源和边界。
          </p>
        </div>
        <div className="yearly-seal" aria-hidden="true">
          <strong>{result ? annual.ganzhi || "—" : "待计算"}</strong>
          <span>{targetYear}</span>
          <small>结构 · 非断语</small>
        </div>
      </section>

      <section className="yearly-entry">
        {/* TJ-0422 phase 2 slice A: noValidate lets the friendly
            in-page year error show instead of the native bubble;
            the input's validity flags are unchanged. */}
        <form onSubmit={submit} noValidate>
          <div className="yearly-entry-head">
            <div>
              <span className="eyebrow">输入出生资料</span>
              <h2>查看你的 {targetYear} 流年结构</h2>
            </div>
            <button type="button" className="sample-fill" onClick={fillSample}>填入示例</button>
          </div>
          <div className="yearly-input-grid">
            <label>
              <span>出生日期</span>
              <input type="date" value={date} onChange={(e) => { invalidateResult(); setDate(e.target.value); }} required />
            </label>
            <label>
              <span>出生时间</span>
              <input type="time" value={time} onChange={(e) => { invalidateResult(); setTime(e.target.value); }} required />
            </label>
            <div className="yearly-fixed-year yearly-year-field">
              <span>目标年份</span>
              <span className="yearly-year-stepper">
                <button
                  type="button"
                  className="yearly-year-step"
                  aria-label="上一年"
                  disabled={targetYear <= MIN_TARGET_YEAR}
                  onClick={() => void changeYear(targetYear - 1)}
                >
                  ‹ 上一年
                </button>
                <input type="number" aria-label="目标年份" min={MIN_TARGET_YEAR} max={MAX_TARGET_YEAR} step={1} value={targetYear}
                  onChange={(event) => {
                    invalidateResult();
                    const next = Number(event.target.value);
                    setTargetYear(next);
                    if (isValidTargetYear(next)) setSelectedYear(next);
                  }}
                  required />
                <button
                  type="button"
                  className="yearly-year-step"
                  aria-label="下一年"
                  disabled={targetYear >= MAX_TARGET_YEAR}
                  onClick={() => void changeYear(targetYear + 1)}
                >
                  下一年 ›
                </button>
              </span>
            </div>
          </div>
          <div className="yearly-entry-note">
            <Icon name="shield" size={16} />
            <span>北京时间 UTC+8；目标年干支由固定历法适配器计算。AI 不参与排盘。</span>
          </div>
          <button className="button primary yearly-submit" type="submit" disabled={loading}>
            {loading ? "正在生成…" : `查看 ${targetYear} 流年结构`}
            {!loading && <Icon name="arrow" size={18} />}
          </button>
          {error && <p className="question-error" role="alert">{error}</p>}
        </form>

        <aside>
          <span className="eyebrow">本轮只回答</span>
          <h2>“结构是什么”，不回答“吉凶如何”</h2>
          <ul>
            <li>你的出生四柱与日主</li>
            <li>{targetYear} 的干支</li>
            <li>流年天干相对日主的十神</li>
            <li>流年地支与原局四柱的六合、六冲、六害</li>
            <li>这条关系引用了哪条审核规则</li>
          </ul>
          <p>旺衰、喜用、格局、桃花、事业、财富、健康、应期均未进入当前公开结论。</p>
        </aside>
      </section>

      {/* TJ-0422 phase 2 slice A: which dayun this year falls in, from
          the session-shared presentation only. Shown before any
          calculation, because locating needs no API call. */}
      <section className="yearly-dayun-location" aria-label="所属大运">
        <span className="eyebrow">所属大运 · {dayunMethodLabels[dayunMethod]}口径</span>
        {yearLocation.status === "no_presentation" && (
          <>
            <h2>尚未查看大运</h2>
            <p>
              本页不知道 {targetYear} 年处在哪段大运：大运呈现只在八字命理页选择传统口径并计算后，才会保存在本次会话中；这里不编造。
            </p>
            <p>
              <Link href="/bazi-profile">先在八字命理页选择传统大运口径查看完整大运</Link>
            </p>
          </>
        )}
        {yearLocation.status === "located" && (
          <>
            <h2>{targetYear} 年 · 第 {yearLocation.periodIndex} 运 {yearLocation.ganzhi}</h2>
            <p>
              按{dayunMethodLabels[dayunMethod]}口径，{targetYear} 年处于第 {yearLocation.periodIndex} 运（{yearLocation.ganzhi}，相对日主{yearLocation.tenGod}）。
              另一口径的定位可能不同，可在八字命理页切换口径查看。
            </p>
            <p>
              <Link href="/bazi-profile" onClick={() => requestDayunReturn(yearLocation.periodIndex)}>返回所属大运</Link>
            </p>
          </>
        )}
        {yearLocation.status === "ambiguous" && (
          <>
            <h2>{targetYear} 年 · 交运年，所属大运不唯一</h2>
            <p>
              按{dayunMethodLabels[dayunMethod]}口径，{targetYear} 年内有第 {yearLocation.toPeriodIndex} 运的交运区间：
              {yearLocation.fromPeriodIndex !== null
                ? `第 ${yearLocation.fromPeriodIndex} 运${yearLocation.fromGanzhi ? ` ${yearLocation.fromGanzhi}` : ""}与第 ${yearLocation.toPeriodIndex} 运 ${yearLocation.toGanzhi}之间`
                : `首运开始之前与第 ${yearLocation.toPeriodIndex} 运 ${yearLocation.toGanzhi}之间`}，
              可能处于交运前后，不强行定归属。
            </p>
            <p>
              <Link href="/bazi-profile" onClick={() => requestDayunReturn(yearLocation.toPeriodIndex)}>查看第 {yearLocation.toPeriodIndex} 运</Link>
            </p>
          </>
        )}
        {yearLocation.status === "before_first" && (
          <>
            <h2>{targetYear} 年 · 尚未进入首运</h2>
            <p>
              按{dayunMethodLabels[dayunMethod]}口径，{targetYear} 年在首运交运区间之前，尚未进入首运。
            </p>
            <p>
              <Link href="/bazi-profile">在八字命理页查看完整大运</Link>
            </p>
          </>
        )}
        {yearLocation.status === "not_provided" && (
          <>
            <h2>{targetYear} 年 · 所属大运无法定位</h2>
            <p>
              按{dayunMethodLabels[dayunMethod]}口径，本口径只提供首运交运区间（第 {yearLocation.lastKnownPeriodIndex} 运 {yearLocation.lastKnownGanzhi}之后未提供），
              {targetYear} 年的所属大运无法定位，不以十年平移拟制。
            </p>
            <p>
              <Link href="/bazi-profile">在八字命理页查看完整大运</Link>
            </p>
          </>
        )}
        {yearLocation.status === "unresolved" && (
          <>
            <h2>{targetYear} 年 · 交运时间暂不可判</h2>
            <p>
              按{dayunMethodLabels[dayunMethod]}口径，交运时间暂不可判（出生时刻恰逢节气交界，交运换算口径尚未裁定），{targetYear} 年的所属大运无法定位。
            </p>
            <p>
              <Link href="/bazi-profile">在八字命理页查看完整大运</Link>
            </p>
          </>
        )}
      </section>

      {!result && !loading && (
        <section className="yearly-empty">
          <span>岁</span>
          <div>
            <h2>真实结果生成后才显示</h2>
            <p>这里没有预制“好运指数”或随机分数。</p>
          </div>
        </section>
      )}

      {result && (
        <section className="yearly-result">
          <ConsumerResultSummary scenario="yearly" response={result} />
          <header className="yearly-result-head">
            <div>
              <span className="eyebrow">真实 Scenario Engine · production_limited</span>
              <h2>
                日主 {natal.day_master?.stem || "—"}
                <span> × </span>
                {targetYear} {annual.ganzhi || "—"}
              </h2>
              <p>流年天干 {annual.stem || "—"} 相对日主：<strong>{annual.stem_ten_god || "—"}</strong></p>
            </div>
            <span className="yearly-limited">结构内测</span>
          </header>

          <div className="yearly-core">
            <article className="yearly-flow-card">
              <small>{targetYear} 流年干支</small>
              <strong>{annual.ganzhi || "—"}</strong>
              {/* TJ-0422 phase 2 slice A: annual stem/branch elements are
                  a fixed display lookup (see yearContext); the ganzhi,
                  ten-god and branch relations all come from this same
                  scenario result — nothing is computed in the browser. */}
              <div><span>天干</span><b>{annual.stem || "—"}{annual.stem && STEM_ELEMENTS[annual.stem] ? `（${STEM_ELEMENTS[annual.stem]}）` : ""}</b></div>
              <div><span>地支</span><b>{annual.branch || "—"}{annual.branch && BRANCH_ELEMENTS[annual.branch] ? `（${BRANCH_ELEMENTS[annual.branch]}）` : ""}</b></div>
              <div><span>相对日主</span><b>{annual.stem_ten_god || "—"}</b></div>
              <p>{annual.year_boundary || ""}</p>
            </article>

            <div className="yearly-natal">
              <span className="eyebrow">你的原局基础</span>
              <div className="yearly-pillars">
                {pillars.map((item: any) => (
                  <article key={item.name}>
                    <small>{pillarNames[item.name] || item.name}</small>
                    <strong>{item.ganzhi}</strong>
                    <span>{item.stem?.ten_god}</span>
                  </article>
                ))}
              </div>
            </div>
          </div>

          <section className="yearly-rule">
            <div className="result-section-heading">
              <div><span>一</span><h2>本次结构关系</h2></div>
            </div>
            {result.rule_matches.map((rule, index) => (
              <article key={rule.rule_id || index}>
                <strong>{rule.rule_id}</strong>
                {/* Line B: the production backend returns the short canonical
                    rule ID "R05" for the annual-branch rule (the public
                    scenario_engine uses the long
                    "bazi.scenario.annual_branch_relations"); accept both so
                    the branch rule renders its branch summary instead of the
                    stem paragraph. */}
                {rule.rule_id === "bazi.scenario.annual_branch_relations" || rule.rule_id === "R05" ? (
                  <p>流年地支：{annual.branch || "—"} · 已核原局四柱地支 · 命中 {branchHits.length} 条六合、六害或六冲</p>
                ) : (
                  <p>
                    日主：{natal.day_master?.stem || "—"} ·
                    流年天干：{annual.stem || "—"} ·
                    十神：{annual.stem_ten_god || "—"}
                  </p>
                )}
                <small>依据：已审结构规则 · 计算过程由服务端校验</small>
              </article>
            ))}
          </section>

          <section className="yearly-rule yearly-branch-section" aria-label="流年地支与原局关系">
            <div className="result-section-heading">
              <div><span>支</span><h2>流年地支 × 四柱冲合害</h2></div>
            </div>
            <p className="yearly-branch-summary">
              流年地支 <strong>{branchRelations?.flow_branch || "—"}</strong>，逐一对照四个出生地支。
              {branchRelations?.evaluated_pairs === 4 ? " 已核 4 组结构。 " : ""}
              共命中 <strong>{branchHits.length}</strong> 条。
            </p>
            {branchHits.length ? (
              <div className="yearly-branch-grid">
                {branchHits.map((item, index) => (
                  <article key={item.rule_id + "-" + item.natal_pillar + "-" + index} className="yearly-branch-hit">
                    <span>{relationNames[item.relation_type] || item.relation_type}</span>
                    <strong>{item.flow_branch} ↔ {item.natal_branch}</strong>
                    <p>{pillarNames[item.natal_pillar] || item.natal_pillar}地支 · {item.rule_id}</p>
                    <small>仅为已审核的结构关系；不代表吉凶或事件必然发生。</small>
                    {(() => {
                      const linked = Array.isArray(item.evidence_ids)
                        ? item.evidence_ids.map((id: string) => evidenceById.get(id))
                            .filter((source: any) => source !== undefined)
                        : [];
                      return linked.length > 0 ? (
                        <details className="yearly-branch-sources">
                          <summary>查看本条依据（{linked.length}）</summary>
                          {linked.map((source: any) => (
                            <div key={source.id} className="yearly-branch-source">
                              <p>{source.title} · 证据等级 {source.grade}</p>
                              <blockquote>{source.quote}{source.excerpt ? "（节选）" : ""}</blockquote>
                            </div>
                          ))}
                        </details>
                      ) : (
                        <p className="yearly-branch-evidence-missing">本条未返回可核验的原典短引，不能据此追加解释。</p>
                      );
                    })()}
                  </article>
                ))}
              </div>
            ) : (
              <p className="yearly-branch-no-hit">四柱未命中本版审核的六合、六冲、六害成对规则，不代表不存在其他关系。</p>
            )}
            <p className="yearly-branch-boundary">仅展示已核验的成对结构，不包含刑、破、三合、合化效力、大运作用或应事推断。依据详见下方典籍证据。</p>
          </section>

          <div className="yearly-two-columns">
            <section className="live-section">
              <div className="result-section-heading"><div><span>二</span><h2>典籍依据</h2></div></div>
              {evidence.map((item) => (
                <article className="live-evidence" key={item.id}>
                  <div><strong>{item.title}</strong><span>{item.grade}</span></div>
                  <blockquote>{item.quote}{item.excerpt ? "（节选）" : ""}</blockquote>
                  <small>{item.id}</small>
                </article>
              ))}
            </section>

            <section className="live-section yearly-limits">
              <div className="result-section-heading"><div><span>三</span><h2>当前不能说什么</h2></div></div>
              {result.limitations.map((item, index) => <p key={index}>{item}</p>)}
              {result.warnings.map((item, index) => <div className="live-warning" key={index}>{item}</div>)}
            </section>
          </div>

          <details className="trace-section yearly-trace">
            <summary>
              <span className="trace-icon"><Icon name="layers" size={19} /></span>
              <div><strong>查看聚合过程</strong><small>Scenario Trace · 默认折叠</small></div>
              <Icon name="chevron" size={18} />
            </summary>
            <ol>
              {result.trace.map((step, index) => (
                <li key={index}>
                  <span>{String(index + 1).padStart(2, "0")}</span>
                  {step.step || step.rule_id || JSON.stringify(step)}
                </li>
              ))}
            </ol>
          </details>

          <div className="yearly-future">
            <span>运</span>
            <div>
              <h3>完整“{targetYear} 年运势”还差什么？</h3>
              <p>要继续补旺衰、格局、喜用、大运以及流年关系实际效力等证据，再分别形成桃花、事业财运等场景规则。现在不会用一个“食神”就给你下全年吉凶结论。</p>
            </div>
          </div>
        </section>
      )}
    </div>
  );
}
