import { useState } from "react";
import type { FormEvent } from "react";
import { Icon } from "../shared/Icon";
import { Link } from "../shared/router";
import { executeCareerScenario, type ScenarioExecuteResponse } from "./api";
import { readSavedTargetYear, saveTargetYear, isValidTargetYear, MIN_TARGET_YEAR, MAX_TARGET_YEAR } from "./targetYear";
import { readSavedBirthProfile, saveBirthProfile } from "./birthProfile";
import "./career-wealth-structure.css";

const groupOrder = ["wealth", "authority", "output", "resource", "peers"];
const groupGlyph: Record<string, string> = {
  wealth: "财",
  authority: "官",
  output: "食",
  resource: "印",
  peers: "比",
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
      "古籍依据",
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

export function CareerWealthStructurePage() {
  const [date, setDate] = useState(() => readSavedBirthProfile().date);
  const [time, setTime] = useState(() => readSavedBirthProfile().time);
  const [targetYear, setTargetYear] = useState(readSavedTargetYear);
  const [result, setResult] = useState<ScenarioExecuteResponse | null>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  function fillSample() {
    setDate("2000-01-07");
    setTime("12:00");
    setResult(null);
    setError("");
  }

  async function submit(event: FormEvent) {
    event.preventDefault();
    setLoading(true);
    setError("");
    setResult(null);
    try {
      if (!isValidTargetYear(targetYear)) throw new Error("请选择 1901 至 2098 年的公历年份");
      const response = await executeCareerScenario({
        birth_value: `${date}T${time}:00+08:00`,
        target_year: targetYear,
      });
      saveBirthProfile({ date, time });
      saveTargetYear(targetYear);
      setResult(response);
    } catch (err) {
      setError(err instanceof Error ? err.message : "事业财运结构计算失败。");
    } finally {
      setLoading(false);
    }
  }

  const payload = result?.result || {};
  const natal = payload.natal || {};
  const groups = payload.structure_groups || {};
  const flowYear = payload.target_year || {};
  const cards: Array<any> = Array.isArray(payload.interpretation_cards) ? payload.interpretation_cards : [];
  const evidence = result
    ? Object.entries(result.evidence).map(([id, value]) => displayEvidence(id, value))
    : [];

  return (
    <div className="career-page">
      <div className="breadcrumb">
        <Link href="/">生活场景</Link>
        <Icon name="chevron" size={12} />
        <span>事业财运 · 结构内测</span>
      </div>

      <section className="career-hero">
        <div>
          <span className="eyebrow">事业财运 · 第一层真实能力</span>
          <h1>先把财、官、食伤、印、比劫的位置看清。</h1>
          <p>
            这一版只聚合已经验证的十神与藏干结构：哪些星明见在天干、哪些藏在地支，
            以及 {targetYear} 流年天干与你日主形成什么十神。它不是“发财预测”，也不会给你编一个事业指数。
          </p>
        </div>
        <div className="career-mark" aria-hidden="true">
          <span>业</span>
          <small>结构先行</small>
        </div>
      </section>

      <section className="career-entry">
        <form onSubmit={submit}>
          <div className="career-entry-head">
            <div>
              <span className="eyebrow">输入出生资料</span>
              <h2>查看你的事业财运结构</h2>
            </div>
            <button type="button" className="sample-fill" onClick={fillSample}>填入示例</button>
          </div>
          <div className="career-input-grid">
            <label>
              <span>出生日期</span>
              <input type="date" value={date} onChange={(e) => setDate(e.target.value)} required />
            </label>
            <label>
              <span>出生时间</span>
              <input type="time" value={time} onChange={(e) => setTime(e.target.value)} required />
            </label>
            <label className="career-fixed-year">
              <span>观察年份</span>
              <input type="number" min={MIN_TARGET_YEAR} max={MAX_TARGET_YEAR} step={1} value={targetYear}
                onChange={(event) => { setTargetYear(Number(event.target.value)); setResult(null); }}
                required />
            </label>
          </div>
          <div className="career-entry-note">
            <Icon name="shield" size={16} />
            <span>只统计确定性结构位置，不比较旺衰、月令权重，也不把数量换算成“好坏分数”。</span>
          </div>
          <button className="button primary career-submit" type="submit" disabled={loading}>
            {loading ? "正在计算…" : "查看事业财运结构"}
            {!loading && <Icon name="arrow" size={18} />}
          </button>
          {error && <p className="question-error" role="alert">{error}</p>}
        </form>

        <aside>
          <span className="eyebrow">本轮回答</span>
          <h2>“有哪些结构”，不是“今年赚多少钱”</h2>
          <ul>
            <li>财星在什么位置出现</li>
            <li>官杀在什么位置出现</li>
            <li>食伤、印星、比劫如何分布</li>
            <li>{targetYear} 流年天干对应什么十神</li>
          </ul>
          <p>升职、跳槽、收入、投资、行业推荐等结论，要等旺衰、格局、喜用、大运和更多证据补齐。</p>
        </aside>
      </section>

      {!result && !loading && (
        <section className="career-empty">
          <span>业</span>
          <div>
            <h2>没有预制“财运指数”</h2>
            <p>真实 Scenario Engine 返回后才展示你的结构分布。</p>
          </div>
        </section>
      )}

      {result && (
        <section className="career-result">
          <header className="career-result-head">
            <div>
              <span className="eyebrow">真实 Scenario Engine · production_limited</span>
              <h2>
                日主 {natal.day_master?.stem || "—"}
                <span> · </span>
                {targetYear} {flowYear.ganzhi || "—"}
              </h2>
              <p>
                流年天干 {flowYear.stem || "—"} 相对日主为
                <strong> {flowYear.stem_ten_god || "—"} </strong>
                · 归入 {flowYear.structure_group_label || "—"} 结构。
              </p>
            </div>
            <span className="career-limited">结构内测</span>
          </header>

          <div className="career-groups">
            {groupOrder.map((groupId) => {
              const group = groups[groupId] || {};
              const insight = cards.find((item) => item.group_id === groupId);
              const occurrences = Array.isArray(group.occurrences) ? group.occurrences : [];
              return (
                <article key={groupId} className={flowYear.structure_group === groupId ? "flow-hit" : ""}>
                  <div className="career-group-title">
                    <span>{groupGlyph[groupId]}</span>
                    <div>
                      <small>{group.label || groupId}</small>
                      <strong>{(group.ten_gods || []).join(" · ")}</strong>
                    </div>
                  </div>
                  <div className="career-counts">
                    <span>天干明见 <b>{group.visible_count ?? 0}</b></span>
                    <span>地支藏干 <b>{group.hidden_count ?? 0}</b></span>
                  </div>
                  <div className="career-occurrences">
                    {occurrences.length ? occurrences.map((item: any, index: number) => (
                      <span key={index}>
                        {pillarNames[item.pillar] || item.pillar}
                        · {item.stem}
                        · {item.ten_god}
                        <i>{item.layer === "visible_stem" ? "明" : "藏"}</i>
                      </span>
                    )) : <em>当前结构中未见</em>}
                  </div>
                  {insight && (
                    <div className="career-interpretation">
                      <strong>传统十神关系 · {insight.five_element_relation}</strong>
                      <p>{insight.traditional_structure_definition}</p>
                      <p>{insight.observation}</p>
                      {insight.target_year_note && <p>{insight.target_year_note}</p>}
                      <small>已审十神及藏干规则 · {insight.interpretation_level === "reviewed_structural_relation_only" ? "只作结构释义" : "未审核"}</small>
                    </div>
                  )}
                  {flowYear.structure_group === groupId && !insight && (
                    <p>{targetYear} 流年天干落入这一结构组，仅表示十神关系命中。</p>
                  )}
                </article>
              );
            })}
          </div>

          <section className="career-natal">
            <div className="result-section-heading">
              <div><span>一</span><h2>原局四柱</h2></div>
              <small>结构定位底座</small>
            </div>
            <div className="career-pillars">
              {(natal.pillars || []).map((item: any) => (
                <article key={item.name} className={item.name === "day" ? "day-pillar" : ""}>
                  <small>{pillarNames[item.name] || item.name}</small>
                  <strong>{item.ganzhi}</strong>
                  <span>{item.stem?.ten_god}</span>
                </article>
              ))}
            </div>
          </section>

          <div className="career-two-columns">
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

            <section className="live-section career-limits">
              <div className="result-section-heading"><div><span>三</span><h2>当前不能下的结论</h2></div></div>
              {result.limitations.map((item, index) => <p key={index}>{item}</p>)}
              {result.warnings.map((item, index) => <div className="live-warning" key={index}>{item}</div>)}
            </section>
          </div>

          <details className="trace-section career-trace">
            <summary>
              <span className="trace-icon"><Icon name="layers" size={19} /></span>
              <div><strong>查看聚合过程</strong><small>十神位置 → 藏干 → {targetYear} 流年天干</small></div>
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

          <div className="career-next">
            <span>势</span>
            <div>
              <h3>下一层才会接近真正的事业财运报告</h3>
              <p>
                本版补充了有规则证据的五组十神结构释义；下一步仍需补旺衰、格局、喜用、大运与流年实际作用并做跨证据验证。
                这些完成前，只展示结构，不给收益承诺。
              </p>
            </div>
          </div>
        </section>
      )}
    </div>
  );
}
