import { useMemo, useState } from "react";
import type { FormEvent } from "react";
import { Icon } from "../shared/Icon";
import { Link } from "../shared/router";
import { executeCompatibilityScenario, type ScenarioExecuteResponse } from "./api";
import "./compatibility-structure.css";

const profileKey = "tianji.profile.birth.v1";
const pillarNames: Record<string, string> = {
  year: "年柱", month: "月柱", day: "日柱", hour: "时柱",
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

function evidenceLabel(id: string, value: Record<string, any>) {
  return {
    id,
    title: String(value.classic_title || value.title || value.source_title || "古籍依据"),
    quote: String(value.original_text || value.quote || value.text || "该证据已由服务端绑定。"),
    grade: String(value.evidence_level || value.grade || "—"),
  };
}

export function CompatibilityStructurePage() {
  const saved = useMemo(readProfile, []);
  const [aName, setAName] = useState("我");
  const [bName, setBName] = useState("对方");
  const [aDate, setADate] = useState(saved.date);
  const [aTime, setATime] = useState(saved.time);
  const [bDate, setBDate] = useState("");
  const [bTime, setBTime] = useState("");
  const [result, setResult] = useState<ScenarioExecuteResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  function fillSample() {
    setADate("2000-01-07");
    setATime("12:00");
    setBDate("2000-02-01");
    setBTime("12:00");
    setResult(null);
    setError("");
  }

  async function submit(event: FormEvent) {
    event.preventDefault();
    setLoading(true);
    setError("");
    setResult(null);
    try {
      const next = await executeCompatibilityScenario({
        person_a_birth_value: `${aDate}T${aTime}:00+08:00`,
        person_b_birth_value: `${bDate}T${bTime}:00+08:00`,
      });
      try {
        localStorage.setItem(profileKey, JSON.stringify({ date: aDate, time: aTime }));
      } catch {
        /* optional */
      }
      setResult(next);
    } catch (err) {
      setError(err instanceof Error ? err.message : "合盘结构计算失败。");
    } finally {
      setLoading(false);
    }
  }

  const payload = result?.result || {};
  const a = payload.person_a || {};
  const b = payload.person_b || {};
  const relations = payload.day_master_relations || {};
  const reviewed = payload.reviewed_cross_relations || {};
  const fiveCombination = reviewed.day_master_five_combination || {};
  const spouseRelation = reviewed.spouse_palace_relation || {};
  const spouseRelations = Array.isArray(spouseRelation.relations) ? spouseRelation.relations : [];
  const cross = payload.xianchi_cross_matches || {};
  const evidence = result
    ? Object.entries(result.evidence).map(([id, value]) => evidenceLabel(id, value))
    : [];

  const people = [
    { id: "a", name: aName || "我", data: a },
    { id: "b", name: bName || "对方", data: b },
  ];

  const crossRows = [
    {
      key: "a_targets_vs_b",
      subject: aName || "我",
      other: bName || "对方",
      data: cross.a_targets_vs_b || {},
    },
    {
      key: "b_targets_vs_a",
      subject: bName || "对方",
      other: aName || "我",
      data: cross.b_targets_vs_a || {},
    },
  ];

  return (
    <div className="compat-page">
      <div className="breadcrumb">
        <Link href="/">生活场景</Link>
        <Icon name="chevron" size={12} />
        <span>缘分合盘 · 结构版</span>
      </div>

      <section className="compat-hero">
        <div>
          <span className="eyebrow">双人合盘 · 结构内测</span>
          <h1>把两个人放在同一张结构图里看。</h1>
          <p>
            当前比较双方真实四柱、双方日主互看十神、日主五合、日支六合/六害、传统配偶宫结构位，
            以及双方年支/日支是否落入对方的咸池目标。不使用“缘分 98 分”这种无法追溯的评分。
          </p>
        </div>
        <div className="compat-mark" aria-hidden="true">
          <strong>合</strong>
          <span>双向看</span>
          <small>不打分</small>
        </div>
      </section>

      <form className="compat-input" onSubmit={submit}>
        {[
          { side: "A", name: aName, setName: setAName, date: aDate, setDate: setADate, time: aTime, setTime: setATime, saved: Boolean(saved.date) },
          { side: "B", name: bName, setName: setBName, date: bDate, setDate: setBDate, time: bTime, setTime: setBTime, saved: false },
        ].map((person) => (
          <section className="compat-person-input" key={person.side}>
            <span className="eyebrow">{person.side} · {person.saved ? "已带入我的资料" : "出生资料"}</span>
            <label>
              <span>显示称呼</span>
              <input value={person.name} onChange={(e) => person.setName(e.target.value)} maxLength={12} />
            </label>
            <div>
              <label>
                <span>出生日期</span>
                <input type="date" value={person.date} onChange={(e) => person.setDate(e.target.value)} required />
              </label>
              <label>
                <span>出生时间</span>
                <input type="time" value={person.time} onChange={(e) => person.setTime(e.target.value)} required />
              </label>
            </div>
          </section>
        ))}
        <div className="compat-submit-wrap">
          <button type="button" className="sample-fill" onClick={fillSample}>填入双人示例</button>
          <button className="button primary" type="submit" disabled={loading}>
            {loading ? "正在合盘…" : "生成双人结构"}
            {!loading && <Icon name="arrow" size={18} />}
          </button>
        </div>
        {error && <p className="question-error compat-error" role="alert">{error}</p>}
      </form>

      {!result && !loading && (
        <section className="compat-empty">
          <span>合</span>
          <div>
            <h2>没有预制“缘分分数”</h2>
            <p>只有两份真实八字都算出来后，才显示双方结构关系。</p>
          </div>
        </section>
      )}

      {result && (
        <section className="compat-result">
          <header className="compat-result-head">
            <div>
              <span className="eyebrow">真实 Scenario Engine · two_person_structure_only</span>
              <h2>{aName || "我"} × {bName || "对方"}</h2>
              <p>双向分别计算，不把任何一方的视角当成唯一结论。</p>
            </div>
            <span className="compat-limited">合盘结构</span>
          </header>

          <div className="compat-people">
            {people.map((person) => (
              <section key={person.id}>
                <div className="compat-person-head">
                  <span>{person.id.toUpperCase()}</span>
                  <div><small>{person.name}</small><strong>日主 {person.data.day_master?.stem || "—"}</strong></div>
                </div>
                <div className="compat-pillars">
                  {(person.data.pillars || []).map((pillar: any) => (
                    <article key={pillar.name} className={pillar.name === "day" ? "day-pillar" : ""}>
                      <small>{pillarNames[pillar.name] || pillar.name}</small>
                      <strong>{pillar.ganzhi}</strong>
                      <span>{pillar.stem?.ten_god}</span>
                    </article>
                  ))}
                </div>
                <p className="compat-palace-line">
                  <span>传统配偶宫结构位</span>
                  <strong>日支 {person.data.spouse_palace?.day_branch || "—"}</strong>
                </p>
              </section>
            ))}
          </div>

          <section className="compat-section">
            <div className="result-section-heading">
              <div><span>一</span><h2>双方日主互看十神</h2></div>
              <small>两个方向分别计算</small>
            </div>
            <div className="compat-relations">
              <article>
                <small>{aName || "我"} 看 {bName || "对方"}</small>
                <strong>{relations.a_sees_b?.subject_day_master || "—"} → {relations.a_sees_b?.other_day_master || "—"}</strong>
                <span>{relations.a_sees_b?.ten_god || "—"}</span>
              </article>
              <i>⇄</i>
              <article>
                <small>{bName || "对方"} 看 {aName || "我"}</small>
                <strong>{relations.b_sees_a?.subject_day_master || "—"} → {relations.b_sees_a?.other_day_master || "—"}</strong>
                <span>{relations.b_sees_a?.ten_god || "—"}</span>
              </article>
            </div>
            <p className="compat-note">十神关系只是五行生克与阴阳结构，不等于“适合/不适合”。</p>
          </section>

          <section className="compat-section">
            <div className="result-section-heading">
              <div><span>二</span><h2>已审核的双人关系结构</h2></div>
              <small>五合 · 六合 · 六害 · 日支结构位</small>
            </div>
            <div className="compat-reviewed-grid">
              <article>
                <small>双方日主 · 天干五合</small>
                <strong>{(fiveCombination.stems || []).join(" · ") || "—"}</strong>
                <span>{fiveCombination.matched ? "命中五合结构" : "未命中五合结构"}</span>
                {fiveCombination.matched && fiveCombination.traditional_result_element && (
                  <em>传统表字段：{fiveCombination.traditional_result_element}</em>
                )}
              </article>
              <article>
                <small>双方日支 · 传统配偶宫结构位</small>
                <strong>{spouseRelation.person_a_day_branch || "—"} · {spouseRelation.person_b_day_branch || "—"}</strong>
                <span>
                  {spouseRelations.length
                    ? spouseRelations.map((item: any) => item.kind === "six_harmony" ? "六合" : item.kind === "harm" ? "六害" : item.kind).join("、")
                    : "当前无已审核关系命中"}
                </span>
                {spouseRelations.map((item: any, index: number) => (
                  <em key={index}>
                    {item.kind === "six_harmony" ? "六合" : "六害"}：{(item.branches || []).join(" · ")}
                  </em>
                ))}
              </article>
            </div>
            <p className="compat-note">
              “合”只表示固定结构配对，“害”也只表示传统结构关系；这里不把它们翻译成适合、不适合、感情好坏或分手风险。
            </p>
          </section>

          <section className="compat-section">
            <div className="result-section-heading">
              <div><span>三</span><h2>咸池目标交叉匹配</h2></div>
              <small>只看固定查表是否相等</small>
            </div>
            <div className="compat-cross">
              {crossRows.map((row) => {
                const matches = Array.isArray(row.data.matches) ? row.data.matches : [];
                const targets = row.data.targets || {};
                const otherBranches = row.data.other_branches || {};
                return (
                  <article key={row.key}>
                    <div className="compat-cross-head">
                      <strong>{row.subject} 的目标</strong>
                      <span>对照 {row.other} 的年支/日支</span>
                    </div>
                    <div className="compat-cross-grid">
                      <div><small>年支基准目标</small><b>{targets.year_branch || "—"}</b></div>
                      <div><small>日支基准目标</small><b>{targets.day_branch || "—"}</b></div>
                      <div><small>{row.other} 年支</small><b>{otherBranches.year_branch || "—"}</b></div>
                      <div><small>{row.other} 日支</small><b>{otherBranches.day_branch || "—"}</b></div>
                    </div>
                    <p>{matches.length ? `结构命中 ${matches.length} 处` : "当前没有结构命中"}</p>
                    {matches.map((item: any, index: number) => (
                      <span className="compat-hit" key={index}>
                        {item.subject_basis} 目标 {item.target_branch} = {row.other} {item.other_basis} {item.other_branch}
                      </span>
                    ))}
                  </article>
                );
              })}
            </div>
            <p className="compat-note">命中只表示枝支与咸池固定目标相等，不等于吸引力、正缘或婚姻结果。</p>
          </section>

          <div className="compat-two-columns">
            <section className="compat-section">
              <div className="result-section-heading"><div><span>四</span><h2>典籍依据</h2></div></div>
              {evidence.slice(0, 12).map((item) => (
                <article className="live-evidence" key={item.id}>
                  <div><strong>{item.title}</strong><span>{item.grade}</span></div>
                  <blockquote>{item.quote}</blockquote>
                  <small>{item.id}</small>
                </article>
              ))}
            </section>
            <section className="compat-section">
              <div className="result-section-heading"><div><span>五</span><h2>当前不能说什么</h2></div></div>
              <div className="compat-limit-list">
                {result.limitations.map((item, index) => <p key={index}>{item}</p>)}
              </div>
            </section>
          </div>

          <section className="compat-next">
            <div>
              <span className="eyebrow">继续看自己</span>
              <h2>合盘之外，个人周期入口仍然保留。</h2>
            </div>
            <div>
              <Link href="/life-overview">人生总览</Link>
              <Link href="/daily-structure">今日结构</Link>
              <Link href="/romance-structure">桃花结构</Link>
              <Link href="/ask">一事占问</Link>
            </div>
          </section>

          <details className="trace-section compat-trace">
            <summary>
              <span className="trace-icon"><Icon name="layers" size={19} /></span>
              <div><strong>查看双人计算过程</strong><small>{result.trace.length} 个 deterministic steps</small></div>
              <Icon name="chevron" size={18} />
            </summary>
            <ol>
              {result.trace.map((step, index) => (
                <li key={index}><span>{String(index + 1).padStart(2, "0")}</span>{step.step || "deterministic"}</li>
              ))}
            </ol>
          </details>
        </section>
      )}
    </div>
  );
}
