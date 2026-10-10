import { useEffect, useRef, useState } from "react";
import type { FormEvent } from "react";
import { Icon } from "../shared/Icon";
import { Link } from "../shared/router";
import { executeLifeScenario, type ScenarioExecuteResponse } from "./api";
import { readSavedTargetYear, saveTargetYear, isValidTargetYear, MIN_TARGET_YEAR, MAX_TARGET_YEAR } from "./targetYear";
import "./life-overview.css";

const profileKey = "tianji.profile.birth.v1";
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
const highlightGlyph: Record<string, string> = {
  foundation: "命",
  yearly: "年",
  romance: "缘",
  career: "业",
};

function readProfile() {
  try {
    const raw = localStorage.getItem(profileKey);
    if (!raw) return { date: "", time: "" };
    const parsed = JSON.parse(raw);
    return {
      date: typeof parsed.date === "string" ? parsed.date : "",
      time: typeof parsed.time === "string" ? parsed.time : "",
    };
  } catch {
    return { date: "", time: "" };
  }
}

type ReviewedExcerpt = { id: string; title: string; original: string; level: string };

function reviewedExcerpts(ids: unknown, evidence: Record<string, any>): ReviewedExcerpt[] {
  if (!Array.isArray(ids)) return [];
  return ids.flatMap((id: unknown) => {
    if (typeof id !== "string") return [];
    const source = evidence[id];
    if (!source || typeof source.classic_title !== "string" ||
        !source.classic_title.trim() || typeof source.original_text !== "string" ||
        !source.original_text.trim()) return [];
    return [{
      id, title: source.classic_title, original: source.original_text,
      level: typeof source.evidence_level === "string" ? source.evidence_level : "未标注",
    }];
  });
}

export function LifeOverviewPage() {
  const initial = readProfile();
  const [date, setDate] = useState(initial.date);
  const [time, setTime] = useState(initial.time);
  const [targetYear, setTargetYear] = useState(readSavedTargetYear);
  const [result, setResult] = useState<ScenarioExecuteResponse | null>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const requestVersion = useRef(0);

  useEffect(() => () => { requestVersion.current += 1; }, []);

  function invalidateResult() {
    requestVersion.current += 1;
    setResult(null);
    setError("");
    setLoading(false);
  }

  function fillSample() {
    setDate("2000-01-07");
    setTime("12:00");
    invalidateResult();
  }

  async function submit(event: FormEvent) {
    event.preventDefault();
    const version = ++requestVersion.current;
    setLoading(true);
    setError("");
    setResult(null);
    try {
      if (!isValidTargetYear(targetYear)) throw new Error("请选择 1901 至 2098 年的公历年份");
      const next = await executeLifeScenario({
        birth_value: `${date}T${time}:00+08:00`,
        target_year: targetYear,
      });
      if (version !== requestVersion.current) return;
      try {
        localStorage.setItem(profileKey, JSON.stringify({ date, time }));
        saveTargetYear(targetYear);
      } catch {
        /* Preference persistence is optional. */
      }
      setResult(next);
    } catch (err) {
      if (version === requestVersion.current)
        setError(err instanceof Error ? err.message : "人生总览生成失败。");
    } finally {
      if (version === requestVersion.current) setLoading(false);
    }
  }

  const payload = result?.result || {};
  const profile = payload.profile || {};
  const strengthContext = profile.strength_context || null;
  const integrated = payload.integrated_reading || null;
  const yearly = payload.yearly || {};
  const romance = payload.romance || {};
  const career = payload.career || {};
  const highlights = Array.isArray(payload.highlights) ? payload.highlights : [];
  const pillars = Array.isArray(profile.pillars) ? profile.pillars : [];
  const careerGroups = career.structure_groups || {};
  const yearTarget = yearly.target_year || {};
  const annualRelations = yearly.annual_branch_interactions;
  const annualHits: Array<any> = Array.isArray(annualRelations?.hits) ? annualRelations.hits : [];
  const romanceTargets = romance.xianchi?.targets || {};
  const activation = romance.target_year_activation || {};
  const palace = romance.spouse_palace_year_relations;
  const palaceHits: Array<any> = Array.isArray(palace?.relations) ? palace.relations : [];
  const careerReadings: Array<any> = Array.isArray(career.interpretation_cards) ? career.interpretation_cards : [];
  const focusReading = careerReadings.find((item) => item.group_id === career.target_year?.structure_group);
  const evidenceCount = result ? Object.keys(result.evidence).length : 0;
  const reviewedEvidence = result?.evidence || {};

  return (
    <div className="life-page">
      <div className="breadcrumb">
        <Link href="/">生活场景</Link>
        <Icon name="chevron" size={12} />
        <span>人生总览</span>
      </div>

      <section className="life-hero">
        <div>
          <span className="eyebrow">人生总览 · 聚合内测</span>
          <h1>一份出生资料，把散落的结果收成一张图。</h1>
          <p>
            不再让你来回点八字、流年、桃花、事业财运。一次输入后，
            系统把已经验证的四条确定性链路聚在一起，再把每条结果的来源与边界保留下来。
          </p>
          <div className="life-hero-proof">
            <span>四柱基础</span><i />
            <span>{targetYear} 结构</span><i />
            <span>桃花结构</span><i />
            <span>事业财运结构</span>
          </div>
        </div>
        <div className="life-seal" aria-hidden="true">
          <strong>命</strong>
          <span>一览</span>
          <small>有据 · 可追</small>
        </div>
      </section>

      <section className="life-entry">
        <form onSubmit={submit}>
          <div className="life-entry-head">
            <div>
              <span className="eyebrow">只填一次</span>
              <h2>建立你的个人总览</h2>
            </div>
            <button type="button" className="sample-fill" onClick={fillSample}>填入示例</button>
          </div>

          <div className="life-input-grid">
            <label>
              <span>出生日期</span>
              <input type="date" value={date} onChange={(e) => { invalidateResult(); setDate(e.target.value); }} required />
            </label>
            <label>
              <span>出生时间</span>
              <input type="time" value={time} onChange={(e) => { invalidateResult(); setTime(e.target.value); }} required />
            </label>
            <label className="life-year">
              <span>观察年份</span>
              <input type="number" min={MIN_TARGET_YEAR} max={MAX_TARGET_YEAR} step={1} value={targetYear}
                onChange={(event) => { invalidateResult(); setTargetYear(Number(event.target.value)); }}
                required />
            </label>
          </div>

          <div className="life-entry-note">
            <Icon name="shield" size={16} />
            <span>出生资料只保存在当前浏览器本地用于下次预填；当前计算固定使用北京时间 UTC+8。</span>
          </div>

          <button className="button primary life-submit" type="submit" disabled={loading}>
            {loading ? "正在聚合…" : "生成我的人生总览"}
            {!loading && <Icon name="arrow" size={18} />}
          </button>
          {error && <p className="question-error" role="alert">{error}</p>}
        </form>

        <aside>
          <span className="eyebrow">这次和以前不同</span>
          <h2>先看一张总图，再决定往哪里深入。</h2>
          <p>总览不会重新算一套“神秘分数”，而是复用已经通过校验的真实结果。</p>
          <ul>
            <li>想看全年：进入 {targetYear} 流年结构</li>
            <li>想看感情：进入桃花结构</li>
            <li>想看工作与钱：进入事业财运结构</li>
            <li>有具体问题：转一事占问</li>
          </ul>
        </aside>
      </section>

      {!result && !loading && (
        <section className="life-empty">
          <span>览</span>
          <div>
            <h2>先建立你的总览</h2>
            <p>结果来自真实 Scenario Engine，不使用预制命盘或随机评分。</p>
          </div>
        </section>
      )}

      {result && (
        <section className="life-result">
          <header className="life-result-head">
            <div>
              <span className="eyebrow">life-overview-v1 · deterministic</span>
              <h2>{pillars.map((item: any) => item.ganzhi).join(" · ")}</h2>
              <p>
                日主 <strong>{profile.day_master?.stem || "—"}</strong>
                <span> · </span>
                {targetYear} <strong>{yearTarget.ganzhi || "—"}</strong>
                <span> · </span>
                已绑定 <strong>{evidenceCount}</strong> 条去重 Evidence
              </p>
            </div>
            <span className="life-limited">总览内测</span>
          </header>

          {integrated && strengthContext && (
            <section className="life-integrated-report" aria-label="旺衰因素与年度综合解读">
              <span className="eyebrow">有出处的综合观察 · 不推断吉凶</span>
              <h2>{integrated.headline}</h2>
              <div className="life-integrated-grid">
                <article><h3>命盘因素</h3><p>{integrated.foundation}</p><small>{strengthContext.boundary}</small></article>
                <article><h3>事业财运</h3><p>{integrated.career}</p></article>
                <article><h3>桃花与夫妻宫</h3><p>{integrated.romance}</p></article>
              </div>
              <details>
                <summary>核查以上结论引用的古籍证据</summary>
                {reviewedExcerpts(integrated.evidence_ids, reviewedEvidence).map((item) => (
                  <blockquote key={item.id}><small>{item.title} · {item.level}</small><p>{item.original}</p></blockquote>
                ))}
              </details>
              <aside aria-label="大运与强弱未决边界">
                <strong>大运与旺衰仍未裁定</strong>
                <p>{integrated.dayun}</p><p>{integrated.boundary}</p>
              </aside>
            </section>
          )}

          <div className="life-highlights">
            {highlights.map((item: any) => (
              <article key={item.id}>
                <span className="life-highlight-glyph">{highlightGlyph[item.id] || "·"}</span>
                <div>
                  <small>{item.title}</small>
                  <p>{item.text}</p>
                </div>
              </article>
            ))}
          </div>

          <section className="life-section">
            <div className="result-section-heading">
              <div><span>一</span><h2>命盘基础</h2></div>
              <Link className="text-action" href="/bazi-profile">展开八字档案 <Icon name="arrow" size={15} /></Link>
            </div>
            <div className="life-pillars">
              {pillars.map((item: any) => (
                <article key={item.name} className={item.name === "day" ? "day-pillar" : ""}>
                  <small>{pillarNames[item.name] || item.name}</small>
                  <strong>{item.ganzhi}</strong>
                  <span>{item.stem?.ten_god}</span>
                  <em>{item.branch?.value}</em>
                </article>
              ))}
            </div>
          </section>

          <div className="life-double">
            <section className="life-section life-focus">
              <div className="result-section-heading">
                <div><span>二</span><h2>{targetYear} 流年结构</h2></div>
                <Link className="text-action" href="/yearly-structure">查看详情 <Icon name="arrow" size={15} /></Link>
              </div>
              <div className="life-focus-main">
                <strong>{yearTarget.ganzhi || "—"}</strong>
                <div>
                  <small>流年天干相对日主</small>
                  <b>{yearTarget.stem_ten_god || "—"}</b>
                </div>
              </div>
              <p>这里只复述已验证结构关系，不把单个十神直接解释为全年吉凶。</p>
              {annualRelations && (
                <div className="life-annual-relations" aria-label="流年冲合害来源">
                  <h3>流年地支 {annualRelations.flow_branch} 与四柱的结构关系</h3>
                  <p>已核对 {annualRelations.evaluated_pairs} 组地支；命中 {annualHits.length} 条六合、六害或六冲。</p>
                  {annualHits.length ? annualHits.map((hit: any, index: number) => {
                    const refs: Array<{ id: string; title: string; quote: string; grade: string }> =
                      Array.isArray(hit.evidence_ids) ? hit.evidence_ids.flatMap((id: string) => {
                        const source = reviewedEvidence[id];
                        if (!source || typeof source.original_text !== "string" ||
                            !source.original_text.trim() ||
                            typeof source.classic_title !== "string" ||
                            !source.classic_title.trim()) return [];
                        return [{
                          id,
                          title: source.classic_title,
                          quote: source.original_text,
                          grade: typeof source.evidence_level === "string" ? source.evidence_level : "未标注",
                        }];
                      }) : [];
                    return (
                      <article className="life-annual-hit" key={hit.rule_id + "-" + hit.natal_pillar + "-" + index}>
                        <strong>{relationNames[hit.relation_type] || hit.relation_type}</strong>
                        <span>{hit.flow_branch} ↔ {hit.natal_branch} · {pillarNames[hit.natal_pillar] || hit.natal_pillar}</span>
                        {refs.length ? (
                          <details>
                            <summary>本条古籍依据（{refs.length}）</summary>
                            {refs.map((ref) => (
                              <blockquote key={ref.id}>
                                <small>{ref.title} · {ref.grade}</small>
                                <p>{ref.quote}</p>
                              </blockquote>
                            ))}
                          </details>
                        ) : <p>未收到可核验的对应引文，不扩展解释。</p>}
                      </article>
                    );
                  }) : <p>此年未命中已审核的三类成对结构，不等于全年没有变化。</p>}
                  <small>仅是固定规则的结构命中，不推断应事、婚恋、财运或吉凶。</small>
                </div>
              )}
            </section>

            <section className="life-section life-focus">
              <div className="result-section-heading">
                <div><span>三</span><h2>桃花结构</h2></div>
                <Link className="text-action" href="/romance-structure">查看详情 <Icon name="arrow" size={15} /></Link>
              </div>
              <div className="life-romance-grid">
                <div><small>年支基准目标</small><strong>{romanceTargets.year_branch || "—"}</strong></div>
                <div><small>日支基准目标</small><strong>{romanceTargets.day_branch || "—"}</strong></div>
                <div>
                  <small>{targetYear} 年支基准</small>
                  <strong>{activation.year_branch_basis?.matched ? "命中" : "未命中"}</strong>
                </div>
                <div>
                  <small>{targetYear} 日支基准</small>
                  <strong>{activation.day_branch_basis?.matched ? "命中" : "未命中"}</strong>
                </div>
              </div>
              <p>命中仅表示咸池固定查表结构成立，不等于恋爱发生或婚姻结果。</p>
              {palace && (
                <div className="life-spouse-report" aria-label="夫妻宫流年关系解读">
                  <h3>传统夫妻宫（日支）与 {targetYear} 年</h3>
                  <p>你的日支是 <strong>{palace.natal_day_branch}</strong>，观察年地支是 <strong>{palace.target_year_branch}</strong>。这是一组固定地支结构对照，不是婚恋事件预测。</p>
                  {palaceHits.length ? palaceHits.map((hit: any, index: number) => {
                    const citations = reviewedExcerpts(hit.evidence_ids, reviewedEvidence);
                    return (
                      <article className="life-spouse-relation" key={hit.natal_pillar + "-" + hit.relation_type + "-" + index}>
                        <strong>{relationNames[hit.relation_type] || hit.relation_type}</strong>
                        <span>{hit.natal_branch} ↔ {hit.flow_branch}</span>
                        {citations.length ? (
                          <details>
                            <summary>查看此关系的古籍依据（{citations.length}）</summary>
                            {citations.map((item) => (
                              <blockquote key={item.id}><small>{item.title} · {item.level}</small><p>{item.original}</p></blockquote>
                            ))}
                          </details>
                        ) : <small>这条关系没有可核验的原典短引，不进行解释。</small>}
                      </article>
                    );
                  }) : <p>本年度未命中已审六合、六害、六冲，不代表婚姻或感情缺失。</p>}
                  <small>仅观察已审核的地支关系，不能据此判断正缘、结婚年份或关系好坏。</small>
                </div>
              )}
            </section>
          </div>

          <section className="life-section">
            <div className="result-section-heading">
              <div><span>四</span><h2>事业财运结构</h2></div>
              <Link className="text-action" href="/career-wealth-structure">查看详情 <Icon name="arrow" size={15} /></Link>
            </div>
            <div className="life-career-strip">
              {[
                ["wealth", "财星"],
                ["authority", "官杀"],
                ["output", "食伤"],
                ["resource", "印星"],
                ["peers", "比劫"],
              ].map(([id, label]) => {
                const group = careerGroups[id] || {};
                const active = career.target_year?.structure_group === id;
                return (
                  <article key={id} className={active ? "active" : ""}>
                    <small>{label}</small>
                    <strong>{(group.visible_count || 0) + (group.hidden_count || 0)}</strong>
                    <span>明 {group.visible_count || 0} · 藏 {group.hidden_count || 0}</span>
                    {active && <em>{targetYear} 天干结构</em>}
                  </article>
                );
              })}
            </div>
            <p className="life-inline-note">数量只是位置统计，不代表旺衰，更不是财运或事业评分。</p>
            {focusReading && (
              <div className="life-career-reading" aria-label="流年十神解释卡">
                <span className="eyebrow">本年重点 · 已审十神关系</span>
                <h3>{targetYear} 的{focusReading.label}，在古法中表示什么？</h3>
                <p>{focusReading.traditional_structure_definition}</p>
                <p>{focusReading.observation}</p>
                {focusReading.target_year_note && <p>{focusReading.target_year_note}</p>}
                {(() => {
                  const refs = reviewedExcerpts(focusReading.evidence_ids, reviewedEvidence);
                  return refs.length ? (
                    <details>
                      <summary>查阅这组十神结构的原典依据（{refs.length}）</summary>
                      {refs.map((item) => (
                        <blockquote key={item.id}>
                          <small>{item.title} · 证据等级 {item.level}</small>
                          <p>{item.original}</p>
                        </blockquote>
                      ))}
                    </details>
                  ) : <small>缺少可核验的原典引文，不能延伸此结构解释。</small>;
                })()}
                <small>不包含旺衰、用神、大运与应期判断；不能等同于实际收入、职位或工作成果。</small>
              </div>
            )}
            {careerReadings.length > 0 && (
              <details className="life-other-career-readings">
                <summary>展开其余十神结构释义（{careerReadings.length} 组）</summary>
                <div>
                  {careerReadings.map((item) => (
                    <article key={item.group_id}>
                      <strong>{item.label} · {item.five_element_relation}</strong>
                      <p>{item.traditional_structure_definition}</p>
                      <p>{item.observation}</p>
                      {(() => {
                        const refs = reviewedExcerpts(item.evidence_ids, reviewedEvidence);
                        return refs.length ? (
                          <details>
                            <summary>来源短引（{refs.length}）</summary>
                            {refs.map((ref) => <blockquote key={ref.id}><small>{ref.title} · {ref.level}</small><p>{ref.original}</p></blockquote>)}
                          </details>
                        ) : <small>无可核验原典短引，不进行扩展解释。</small>;
                      })()}
                    </article>
                  ))}
                </div>
              </details>
            )}
          </section>

          <section className="life-next">
            <div>
              <span className="eyebrow">接下来想看什么</span>
              <h2>从总览继续深入，而不是从头再填。</h2>
            </div>
            <div className="life-next-actions">
              <Link href="/daily-structure">今日结构</Link>
              <Link href="/weekly-structure">本周结构</Link>
              <Link href="/monthly-structure">本月结构</Link>
              <Link href="/yearly-structure">{targetYear} 流年</Link>
              <Link href="/romance-structure">桃花姻缘</Link>
              <Link href="/compatibility-structure">缘分合盘</Link>
              <Link href="/career-wealth-structure">事业财运</Link>
              <Link href="/ask">一事占问</Link>
            </div>
          </section>

          <details className="trace-section life-trace">
            <summary>
              <span className="trace-icon"><Icon name="layers" size={19} /></span>
              <div><strong>查看总览证据链</strong><small>{result.rule_matches.length} 条 RuleMatch · {result.trace.length} 个 Trace 步骤</small></div>
              <Icon name="chevron" size={18} />
            </summary>
            <ol>
              {result.trace.map((step, index) => (
                <li key={index}>
                  <span>{String(index + 1).padStart(2, "0")}</span>
                  {step.scenario_section || "overview"} · {step.step || step.rule_id || "deterministic"}
                </li>
              ))}
            </ol>
          </details>

          <section className="life-boundary">
            <strong>当前边界</strong>
            <p>这是一份结构聚合报告，不是完整人生预测。旺衰、喜用、格局、正缘、收入、健康和事件应期等尚未通过完整规则与证据校验的内容不会在这里补写。</p>
          </section>
        </section>
      )}
    </div>
  );
}
