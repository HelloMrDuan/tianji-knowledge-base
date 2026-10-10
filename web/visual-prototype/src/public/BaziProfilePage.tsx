import { useEffect, useRef, useState } from "react";
import type { FormEvent } from "react";
import { Icon } from "../shared/Icon";
import { Link } from "../shared/router";
import { executeBazi, type ExecuteResponse } from "./api";
import { readSavedBirthProfile, saveBirthProfile, clearBirthProfile } from "./birthProfile";
import "./bazi-profile.css";

const pillarNames: Record<string, string> = {
  year: "年柱",
  month: "月柱",
  day: "日柱",
  hour: "时柱",
};

function displayEvidence(id: string, value: Record<string, any>) {
  const title = value.classic_title || value.title || value.source_title;
  const quote = value.original_text;
  if (typeof title !== "string" || !title.trim() ||
      typeof quote !== "string" || !quote.trim()) return null;
  return {
    id,
    title,
    quote,
    grade: typeof value.evidence_level === "string" ? value.evidence_level : "未标注",
  };
}

export function BaziProfilePage() {
  const [date, setDate] = useState(() => readSavedBirthProfile().date);
  const [time, setTime] = useState(() => readSavedBirthProfile().time);
  const [result, setResult] = useState<ExecuteResponse | null>(null);
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
    invalidateResult();
    setDate("2000-01-07");
    setTime("12:00");
  }

  async function submit(event: FormEvent) {
    event.preventDefault();
    if (!date || !time) return;
    const version = ++requestVersion.current;
    setLoading(true);
    setError("");
    setResult(null);
    try {
      const response = await executeBazi({ value: `${date}T${time}:00+08:00`, strength_variant: "ditiansui-root-visibility-v1" });
      if (version !== requestVersion.current) return;
      saveBirthProfile({ date, time });
      setResult(response);
    } catch (err) {
      if (version === requestVersion.current)
        setError(err instanceof Error ? err.message : "八字计算失败，请检查后端服务。");
    } finally {
      if (version === requestVersion.current) setLoading(false);
    }
  }

  const chart = result?.chart || {};
  const strength = chart.strength_factors || null;
  const pillars = Array.isArray(chart.pillars) ? chart.pillars : [];
  const calendar = result?.calendar || {};
  const evidence = result
    ? Object.entries(result.evidence).map(([id, value]) => displayEvidence(id, value))
        .filter((item): item is NonNullable<typeof item> => item !== null)
    : [];
  const evidenceById = new Map(evidence.map((item) => [item.id, item]));

  return (
    <div className="bazi-profile-page">
      <div className="breadcrumb">
        <Link href="/">生活场景</Link>
        <Icon name="chevron" size={12} />
        <span>八字基础档案</span>
      </div>

      <section className="bazi-profile-hero">
        <div>
          <span className="eyebrow">八字 · 真实确定性结构</span>
          <h1>先把四柱看清，再谈后面的事。</h1>
          <p>
            当前正式能力只计算四柱、日主、十神与藏干，并把规则和典籍依据一起返回。
            已可核验月支藏干、通根候选和透藏位置；但通用旺衰、喜用神、大运起运仍未完成证据裁定，因此这里不会提前生成断语。
          </p>
        </div>
        <div className="bazi-scope-card">
          <strong>现在真实可用</strong>
          <span>四柱</span>
          <span>日主</span>
          <span>十神</span>
          <span>藏干</span>
          <small>北京时间 · midnight 日界</small>
        </div>
      </section>

      <section className="bazi-profile-workspace">
        <form className="bazi-input-card" onSubmit={submit}>
          <div className="bazi-card-heading">
            <div>
              <span className="eyebrow">一 · 出生资料</span>
              <h2>公历出生时间</h2>
            </div>
            <div className="bazi-profile-actions">
              <button type="button" className="sample-fill" onClick={fillSample}>填入示例</button>
              <button type="button" className="sample-fill" onClick={() => { invalidateResult(); clearBirthProfile(); setDate(""); setTime(""); }}>清除本机资料</button>
            </div>
          </div>

          <div className="bazi-input-grid">
            <label>
              <span>出生日期</span>
              <input type="date" value={date} onChange={(e) => { invalidateResult(); setDate(e.target.value); }} required />
            </label>
            <label>
              <span>出生时间</span>
              <input type="time" value={time} onChange={(e) => { invalidateResult(); setTime(e.target.value); }} required />
            </label>
          </div>

          <div className="bazi-input-note">
            <Icon name="shield" size={16} />
            <span>当前固定按北京时间 UTC+8 计算；计算成功后出生资料仅保存在本浏览器以便其他场景复用，可随时清除。真太阳时与晚子时变体尚未开放。</span>
          </div>

          <button className="button primary bazi-submit" type="submit" disabled={loading}>
            {loading ? "正在计算…" : "生成基础档案"}
            {!loading && <Icon name="arrow" size={18} />}
          </button>
          {error && <p className="question-error" role="alert">{error}</p>}
        </form>

        <aside className="bazi-boundary-card">
          <span className="eyebrow">二 · 能力边界</span>
          <h2>不把“能算结构”说成“能断人生”</h2>
          <ul>
            <li>仅观察旺衰相关因素，不判断身强身弱</li>
            <li>不选择喜用神</li>
            <li>不自动定格局、调候</li>
            <li>不输出婚恋、事业、财富吉凶</li>
            <li>不计算大运起运岁数</li>
          </ul>
          <p>这些能力会在规则、证据和 Golden Cases 完成后逐项开放。</p>
        </aside>
      </section>

      {!result && !loading && (
        <section className="bazi-empty">
          <span>命</span>
          <div>
            <h2>这里不会展示预制命盘</h2>
            <p>只有真实 API 返回后才生成四柱档案；后端失败就直接报错。</p>
          </div>
        </section>
      )}

      {result && (
        <section className="bazi-live-result">
          <header className="bazi-result-head">
            <div>
              <span className="eyebrow">真实 API · {result.variant}</span>
              <h2>{pillars.map((item: any) => item.ganzhi).join(" · ")}</h2>
              <p>
                {calendar.solar_term ? `节气：${calendar.solar_term} · ` : ""}
                日主：{chart.day_master?.stem || "—"} · {chart.day_master?.element || "—"} · {chart.day_master?.polarity || "—"}
              </p>
            </div>
            <span className="live-badge">确定性结果</span>
          </header>

          <div className="bazi-pillars">
            {pillars.map((item: any) => (
              <article key={item.name} className={item.name === "day" ? "day-pillar" : ""}>
                <span>{pillarNames[item.name] || item.name}</span>
                <strong>{item.ganzhi}</strong>
                <div className="bazi-stem">
                  <small>天干</small>
                  <b>{item.stem?.value}</b>
                  <em>{item.stem?.ten_god}</em>
                </div>
                <div className="bazi-branch">
                  <small>地支</small>
                  <b>{item.branch?.value}</b>
                  <div>
                    {(item.branch?.hidden_stems || []).map((hidden: any) => (
                      <span key={hidden.stem}>{hidden.stem}<i>{hidden.ten_god}</i></span>
                    ))}
                  </div>
                </div>
              </article>
            ))}
          </div>

          {strength && (
            <section className="bazi-strength-observations" aria-label="旺衰因素与通根候选">
              <span className="eyebrow">已审核因素 · 不等于旺衰定论</span>
              <h3>月令、通根与透藏，可以先看清哪些？</h3>
              <p>月支 <strong>{strength.month_command?.month_branch || "—"}</strong>，藏干：
                {(strength.month_command?.hidden_stems || []).join("、") || "—"}。</p>
              <p>与日主同五行的通根候选：
                {strength.root_candidates?.positions?.length
                  ? strength.root_candidates.positions.map((item: any) =>
                      `${pillarNames[item.pillar] || item.pillar}${item.branch}藏${item.hidden_stem}`).join("、")
                  : "目前已核藏干没有同五行通根候选"}。</p>
              <p>藏干在其他天干同字显现：
                {strength.hidden_to_visible?.positions?.length || 0} 处。这不意味着该十神已经生效。</p>
              <p className="bazi-strength-boundary">尚不能据此判断身强身弱、喜用、格局或大运吉凶；不提供虚构的旺衰分数。</p>
              <details>
                <summary>查看旺衰因素规则引用的真实古籍依据</summary>
                {result.rule_matches.flatMap((rule) => Array.isArray(rule.evidence_ids)
                  ? rule.evidence_ids.map((id: string) => evidenceById.get(id)).filter(Boolean)
                  : []).filter((item: any, index: number, rows: any[]) =>
                    rows.findIndex((row) => row.id === item.id) === index
                  ).map((source: any) => (
                  <blockquote key={source.id}><b>{source.title} · {source.grade}</b><p>{source.quote}</p></blockquote>
                ))}
              </details>
            </section>
          )}

          <div className="bazi-result-columns">
            <section className="live-section">
              <div className="result-section-heading"><div><span>三</span><h2>规则命中</h2></div></div>
              {result.rule_matches.map((rule, index) => {
                const citations = Array.isArray(rule.evidence_ids)
                  ? rule.evidence_ids.map((id: string) => evidenceById.get(id))
                      .filter((ref: any) => ref !== undefined)
                  : [];
                return (
                  <article className="live-rule bazi-rule-evidence" key={rule.rule_id || index}>
                    <strong>{rule.rule_id || `规则 ${index + 1}`}</strong>
                    <p>{rule.evidence_scope || "已执行结构规则，具体适用条件以服务端为准。"}</p>
                    {citations.length ? (
                      <details>
                        <summary>查看此规则对应的原典证据（{citations.length}）</summary>
                        {citations.map((item: any) => (
                          <blockquote key={item.id}>
                            <b>{item.title} · 证据等级 {item.grade}</b>
                            <p>{item.quote}</p>
                          </blockquote>
                        ))}
                      </details>
                    ) : <p className="bazi-evidence-missing">未返回可核验的古籍引文，不追加解释。</p>}
                  </article>
                );
              })}
            </section>

            <section className="live-section">
              <div className="result-section-heading"><div><span>四</span><h2>典籍依据</h2></div></div>
              {evidence.map((item) => (
                <article className="live-evidence" key={item.id}>
                  <div><strong>{item.title}</strong><span>{item.grade}</span></div>
                  <blockquote>{item.quote}</blockquote>
                  <small>{item.id}</small>
                </article>
              ))}
            </section>
          </div>

          <details className="trace-section bazi-trace">
            <summary>
              <span className="trace-icon"><Icon name="layers" size={19} /></span>
              <div><strong>查看计算过程</strong><small>公开计算步骤摘要，默认折叠</small></div>
              <Icon name="chevron" size={18} />
            </summary>
            <ol>
              {result.trace.map((step, index) => (
                <li key={index}>
                  <span>{String(index + 1).padStart(2, "0")}</span>
                  {step.rule_id || step.step || JSON.stringify(step)}
                </li>
              ))}
            </ol>
          </details>

          <div className="bazi-next-card">
            <div>
              <span className="eyebrow">下一阶段</span>
              <h3>从基础档案走向“流年 / 桃花 / 事业财运”</h3>
              <p>这些场景会复用现在这份真实四柱结构，但必须等相应规则与证据补齐后才开放。</p>
            </div>
            <div className="bazi-journey-links">
              <Link href="/life-overview">人生总览</Link>
              <Link href="/yearly-structure">流年结构</Link>
              <Link href="/romance-structure">桃花姻缘</Link>
              <Link href="/career-wealth-structure">事业财运</Link>
              <Link href="/daily-structure">今日结构</Link>
            </div>
          </div>
        </section>
      )}
    </div>
  );
}
