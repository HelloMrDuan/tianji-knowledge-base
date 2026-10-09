import { useEffect, useRef, useState } from "react";
import type { FormEvent } from "react";
import { Icon } from "../shared/Icon";
import { Link } from "../shared/router";
import { executeYearlyScenario, type ScenarioExecuteResponse } from "./api";
import { readSavedTargetYear, saveTargetYear, isValidTargetYear, MIN_TARGET_YEAR, MAX_TARGET_YEAR } from "./targetYear";
import { readSavedBirthProfile, saveBirthProfile } from "./birthProfile";
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

function displayEvidence(id: string, evidence: Record<string, any>) {
  return {
    id,
    title: String(
      evidence.classic_title ||
      evidence.title ||
      evidence.classic ||
      evidence.source_title ||
      "《渊海子平》",
    ),
    quote: String(
      evidence.original_text ||
      evidence.quote ||
      evidence.text ||
      "该证据已由服务端绑定。",
    ),
    grade: String(evidence.evidence_level || evidence.grade || "—"),
  };
}

export function YearlyStructurePage() {
  const [date, setDate] = useState(() => readSavedBirthProfile().date);
  const [time, setTime] = useState(() => readSavedBirthProfile().time);
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
    invalidateResult();
    setDate("2000-01-07");
    setTime("12:00");
  }

  async function submit(event: FormEvent) {
    event.preventDefault();
    const version = ++requestVersion.current;
    setLoading(true);
    setError("");
    setResult(null);
    try {
      if (!isValidTargetYear(targetYear)) throw new Error("请选择 1901 至 2098 年的公历年份");
      const response = await executeYearlyScenario({
        birth_value: `${date}T${time}:00+08:00`,
        target_year: targetYear,
      });
      if (version !== requestVersion.current) return;
      saveBirthProfile({ date, time });
      saveTargetYear(targetYear);
      setResult(response);
    } catch (err) {
      if (version === requestVersion.current)
        setError(err instanceof Error ? err.message : "年度结构计算失败。");
    } finally {
      if (version === requestVersion.current) setLoading(false);
    }
  }

  const annual = result?.result?.target_year || {};
  const natal = result?.result?.natal || {};
  const branchRelations = result?.result?.annual_branch_interactions;
  const branchHits: Array<any> = Array.isArray(branchRelations?.hits) ? branchRelations.hits : [];
  const pillars = Array.isArray(natal.pillars) ? natal.pillars : [];
  const evidence = result
    ? Object.entries(result.evidence).map(([id, value]) => displayEvidence(id, value))
    : [];

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
          <h1>先看 {targetYear} 与你的日主，发生了什么结构关系。</h1>
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
        <form onSubmit={submit}>
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
            <label className="yearly-fixed-year">
              <span>目标年份</span>
              <input type="number" min={MIN_TARGET_YEAR} max={MAX_TARGET_YEAR} step={1} value={targetYear}
                onChange={(event) => { invalidateResult(); setTargetYear(Number(event.target.value)); }}
                required />
            </label>
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
              <div><span>天干</span><b>{annual.stem || "—"}</b></div>
              <div><span>地支</span><b>{annual.branch || "—"}</b></div>
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
                <p>
                  日主：{natal.day_master?.stem || "—"} ·
                  流年天干：{annual.stem || "—"} ·
                  十神：{annual.stem_ten_god || "—"}
                </p>
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
                    <small>有来源绑定的传统结构关系；不代表吉凶或事件必然发生。</small>
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
                  <blockquote>{item.quote}</blockquote>
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
