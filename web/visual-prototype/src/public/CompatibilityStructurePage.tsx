import { useEffect, useMemo, useRef, useState } from "react";
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
  const title = value.classic_title || value.title || value.source_title;
  const quote = value.original_text;
  if (typeof title !== "string" || !title.trim() ||
      typeof quote !== "string" || !quote.trim()) return null;
  return { id, title, quote, grade: typeof value.evidence_level === "string" ? value.evidence_level : "未标注" };
}

export function CompatibilityStructurePage() {
  const saved = useMemo(readProfile, []);
  const [aName, setAName] = useState("我");
  const [bName, setBName] = useState("对方");
  const [aDate, setADate] = useState(saved.date);
  const [aTime, setATime] = useState(saved.time);
  const [aRole, setARole] = useState<"" | "male" | "female">("");
  const [bDate, setBDate] = useState("");
  const [bTime, setBTime] = useState("");
  const [bRole, setBRole] = useState<"" | "male" | "female">("");
  const [result, setResult] = useState<ScenarioExecuteResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const requestVersion = useRef(0);
  const [resultNames, setResultNames] = useState({a: "我", b: "对方"});

  useEffect(() => () => { requestVersion.current += 1; }, []);

  function invalidateResult() {
    requestVersion.current += 1;
    setResult(null);
    setError("");
    setLoading(false);
  }

  function fillSample() {
    setADate("2000-01-07");
    setATime("12:00");
    setBDate("2000-02-01");
    setBTime("12:00");
    setARole("male");
    setBRole("female");
    invalidateResult();
  }

  async function submit(event: FormEvent) {
    event.preventDefault();
    const version = ++requestVersion.current;
    setLoading(true);
    setError("");
    setResult(null);
    try {
      const input: {
        person_a_birth_value: string;
        person_b_birth_value: string;
        person_a_traditional_role?: "male" | "female";
        person_b_traditional_role?: "male" | "female";
      } = {
        person_a_birth_value: `${aDate}T${aTime}:00+08:00`,
        person_b_birth_value: `${bDate}T${bTime}:00+08:00`,
      };
      if (aRole) input.person_a_traditional_role = aRole;
      if (bRole) input.person_b_traditional_role = bRole;
      const next = await executeCompatibilityScenario(input);
      if (version !== requestVersion.current) return;
      try {
        localStorage.setItem(profileKey, JSON.stringify({ date: aDate, time: aTime }));
      } catch {
        /* optional */
      }
      setResultNames({a: aName.trim() || "我", b: bName.trim() || "对方"});
      setResult(next);
    } catch (err) {
      if (version === requestVersion.current)
        setError(err instanceof Error ? err.message : "合盘结构计算失败。");
    } finally {
      if (version === requestVersion.current) setLoading(false);
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
  const crossMatrix = payload.cross_relation_matrix || {};
  const crossMatrixHits = Array.isArray(crossMatrix.hits) ? crossMatrix.hits : [];
  const matrix = Array.isArray(payload.relation_evidence_matrix) ? payload.relation_evidence_matrix : [];
  const evidence = result
    ? Object.entries(result.evidence).map(([id, value]) => evidenceLabel(id, value))
        .filter((item): item is NonNullable<typeof item> => item !== null)
    : [];

  const evidenceById = new Map(evidence.map((item) => [item.id, item]));

  const people = [
    { id: "a", name: resultNames.a, data: a },
    { id: "b", name: resultNames.b, data: b },
  ];

  const crossRows = [
    {
      key: "a_targets_vs_b",
      subject: resultNames.a,
      other: resultNames.b,
      data: cross.a_targets_vs_b || {},
    },
    {
      key: "b_targets_vs_a",
      subject: resultNames.b,
      other: resultNames.a,
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
            当前比较双方真实四柱、双方日主互看十神、日主五合、日支六合/六害/六冲、传统配偶宫结构位，
            并把双方四柱之间已审核的合/冲/害命中分层展示。你也可以主动开启传统配偶星观察，但系统不会替你推断口径。
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
          { side: "A", name: aName, setName: setAName, date: aDate, setDate: setADate, time: aTime, setTime: setATime, role: aRole, setRole: setARole, saved: Boolean(saved.date) },
          { side: "B", name: bName, setName: setBName, date: bDate, setDate: setBDate, time: bTime, setTime: setBTime, role: bRole, setRole: setBRole, saved: false },
        ].map((person) => (
          <section className="compat-person-input" key={person.side}>
            <span className="eyebrow">{person.side} · {person.saved ? "已带入我的资料" : "出生资料"}</span>
            <label>
              <span>显示称呼</span>
              <input value={person.name} onChange={(e) => { invalidateResult(); person.setName(e.target.value); }} maxLength={12} />
            </label>
            <div>
              <label>
                <span>出生日期</span>
                <input type="date" value={person.date} onChange={(e) => { invalidateResult(); person.setDate(e.target.value); }} required />
              </label>
              <label>
                <span>出生时间</span>
                <input type="time" value={person.time} onChange={(e) => { invalidateResult(); person.setTime(e.target.value); }} required />
              </label>
            </div>
            <label>
              <span>传统配偶星观察口径（可选）</span>
              <select value={person.role} onChange={(e) => { invalidateResult(); person.setRole(e.target.value as "" | "male" | "female"); }}>
                <option value="">不启用</option>
                <option value="male">传统男命口径 · 看财星</option>
                <option value="female">传统女命口径 · 看官杀</option>
              </select>
              <small>只用于古籍传统结构观察，不用于判断或推断你的现代性别身份。</small>
            </label>
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
              <h2>{resultNames.a} × {resultNames.b}</h2>
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
                {Array.isArray(person.data.natal_triple_harmonies) && person.data.natal_triple_harmonies.length > 0 && (
                  <div className="compat-triples">
                    <small>原局三合结构</small>
                    {person.data.natal_triple_harmonies.map((item: any, index: number) => (
                      <span key={index}>{(item.branches || []).join(" · ")} → {item.traditional_result_element || "—"}</span>
                    ))}
                  </div>
                )}
                {person.data.traditional_spouse_star_lens && (
                  <div className="compat-spouse-stars">
                    <small>传统配偶星观察</small>
                    <strong>{(person.data.traditional_spouse_star_lens.candidate_ten_gods || []).join(" · ")}</strong>
                    <span>
                      明见 {(person.data.traditional_spouse_star_lens.visible_positions || []).length} 处 ·
                      藏干 {(person.data.traditional_spouse_star_lens.hidden_positions || []).length} 处
                    </span>
                    <em>仅定位候选星位，不代表真实配偶、正缘或婚姻质量。</em>
                  </div>
                )}
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
                <small>{resultNames.a} 看 {resultNames.b}</small>
                <strong>{relations.a_sees_b?.subject_day_master || "—"} → {relations.a_sees_b?.other_day_master || "—"}</strong>
                <span>{relations.a_sees_b?.ten_god || "—"}</span>
              </article>
              <i>⇄</i>
              <article>
                <small>{resultNames.b} 看 {resultNames.a}</small>
                <strong>{relations.b_sees_a?.subject_day_master || "—"} → {relations.b_sees_a?.other_day_master || "—"}</strong>
                <span>{relations.b_sees_a?.ten_god || "—"}</span>
              </article>
            </div>
            <p className="compat-note">十神关系只是五行生克与阴阳结构，不等于“适合/不适合”。</p>
          </section>

          <section className="compat-section">
            <div className="result-section-heading">
              <div><span>二</span><h2>已审核的双人关系结构</h2></div>
              <small>五合 · 六合 · 六害 · 六冲 · 原局三合 · 日支结构位</small>
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
                    ? spouseRelations.map((item: any) => item.kind === "six_harmony" ? "六合" : item.kind === "harm" ? "六害" : item.kind === "clash" ? "六冲" : item.kind).join("、")
                    : "当前无已审核关系命中"}
                </span>
                {spouseRelations.map((item: any, index: number) => (
                  <em key={index}>
                    {item.kind === "six_harmony" ? "六合" : item.kind === "harm" ? "六害" : item.kind === "clash" ? "六冲" : item.kind}：{(item.branches || []).join(" · ")}
                  </em>
                ))}
              </article>
            </div>
            <p className="compat-note">
              “合 / 害 / 冲”都只表示固定结构命中；原局三合也只表示完整三支组合。这里不把这些结构翻译成适合、不适合、感情好坏、争执或分手风险。
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

          <section className="compat-section">
            <div className="result-section-heading">
              <div><span>四</span><h2>跨柱关系矩阵</h2></div>
              <small>日柱核心 · 日柱相关 · 其他辅助</small>
            </div>
            <div className="compat-matrix-summary">
              <span>日柱核心 <b>{crossMatrix.summary?.core || 0}</b></span>
              <span>日柱相关 <b>{crossMatrix.summary?.day_context || 0}</b></span>
              <span>其他辅助 <b>{crossMatrix.summary?.supplemental || 0}</b></span>
            </div>
            <div className="compat-matrix-groups">
              {[
                { id: "core", title: "日柱核心", note: "双方日柱直接结构" },
                { id: "day_context", title: "日柱相关", note: "一方日柱与另一方其他柱" },
                { id: "supplemental", title: "其他辅助", note: "双方其他柱之间，仅作补充" },
              ].map((tier) => {
                const rows = crossMatrixHits.filter((item: any) => item.tier === tier.id);
                return (
                  <article key={tier.id}>
                    <header><strong>{tier.title}</strong><small>{tier.note}</small></header>
                    {rows.length ? rows.map((item: any, index: number) => {
                      const relationName =
                        item.relation_type === "stem_five_combination" ? "天干五合" :
                        item.relation_type === "six_harmony" ? "地支六合" :
                        item.relation_type === "harm" ? "地支六害" :
                        item.relation_type === "clash" ? "地支六冲" : item.relation_type;
                      const values = item.stems || item.branches || [];
                      return (
                        <div className="compat-matrix-hit" key={index}>
                          <span>{pillarNames[item.person_a_pillar] || item.person_a_pillar} × {pillarNames[item.person_b_pillar] || item.person_b_pillar}</span>
                          <strong>{relationName}</strong>
                          <em>{values.join(" · ")}</em>
                        </div>
                      );
                    }) : <p>当前没有已审核结构命中</p>}
                  </article>
                );
              })}
            </div>
            <p className="compat-note">
              “核心 / 相关 / 辅助”只是阅读层级，不是权重、分数或吉凶排序；命中数量也不能换算成缘分高低。
            </p>
          </section>

          <section className="compat-section">
            <div className="result-section-heading">
              <div><span>五</span><h2>关系证据矩阵</h2></div>
              <small>Fact → Rule → Evidence</small>
            </div>
            <div className="compat-matrix">
              {matrix.map((item: any) => (
                <article key={item.id}>
                  <div>
                    <strong>{item.label}</strong>
                    <span className={item.status === "matched" ? "matched" : item.status === "observed" ? "observed" : ""}>
                      {item.status === "matched" ? "命中" : item.status === "observed" ? "已观察" : "未命中"}
                    </span>
                  </div>
                  <small>{(item.derived_from_rule_ids || []).join(" · ")}</small>
                  <p>Evidence {(item.evidence_ids || []).length} 条 · 解释权限：关闭</p>
                  {(() => {
                    const refs = Array.isArray(item.evidence_ids)
                      ? item.evidence_ids.map((id: string) => evidenceById.get(id))
                          .filter((ref: any) => ref !== undefined)
                      : [];
                    return refs.length ? (
                      <details className="compat-matrix-citations">
                        <summary>本条结构的古籍依据（{refs.length}）</summary>
                        {refs.map((ref: any) => (
                          <blockquote key={ref.id}>
                            <strong>{ref.title} · {ref.grade}</strong>
                            <p>{ref.quote}</p>
                          </blockquote>
                        ))}
                      </details>
                    ) : <small>没有对应的可核验短引，不生成解释。</small>;
                  })()}
                </article>
              ))}
            </div>
            <p className="compat-note">
              这里把每条结构事实绑定到具体 Rule 与 Evidence；矩阵不会把多条命中累加成缘分分数，也不会自动生成吉凶解释。
            </p>
          </section>

          <div className="compat-two-columns">
            <section className="compat-section">
              <div className="result-section-heading"><div><span>六</span><h2>典籍依据</h2></div></div>
              {evidence.map((item) => (
                <article className="live-evidence" key={item.id}>
                  <div><strong>{item.title}</strong><span>{item.grade}</span></div>
                  <blockquote>{item.quote}</blockquote>
                  <small>{item.id}</small>
                </article>
              ))}
            </section>
            <section className="compat-section">
              <div className="result-section-heading"><div><span>七</span><h2>当前不能说什么</h2></div></div>
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
