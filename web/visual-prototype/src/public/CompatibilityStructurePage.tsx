import { useEffect, useRef, useState } from "react";
import type { FormEvent } from "react";
import { Icon } from "../shared/Icon";
import { Link } from "../shared/router";
import { executeBaziProfileScenario, executeCompatibilityScenario, type ScenarioExecuteResponse } from "./api";
import { readSavedBirthProfile, saveBirthProfile, clearBirthProfile } from "./birthProfile";
import { toApiValue, toApiZone, fromLegacy, toSolarDateString, isConvertedFromLunar, fromSolarEdit, withUpdatedTime, regionToTimezone, REGION_OPTIONS } from "./birthProfile";
import "./compatibility-structure.css";

const pillarNames: Record<string, string> = {
  year: "年柱", month: "月柱", day: "日柱", hour: "时柱",
};

// TJ-0427 Lane D: condensed transcription-only renderers for the three
// lifted bazi-profile presentations and the first-period dayun. The
// label maps mirror BaziProfilePage / CareerWealthStructurePage (same
// backend contract, same wording); the frontend computes no divination
// and never presents a research candidate as a compatibility verdict.
// Pattern yongshen stays undecided: no readiness table is shown here
// and no pattern-yongshen conclusion is ever fabricated.
const compatStrengthPredicateLabels: Record<string, string> = {
  pure_support: "纯粹支持形态",
  pure_generating_support: "生扶支持形态",
  isolated_control: "孤立受制形态",
  commanding_visible_support: "司令显现支持形态",
  lu_visible_support: "禄位显现支持形态",
  changsheng_visible_support: "长生显现支持形态（司令甲段）",
  pure_support_metal: "纯粹支持形态",
  pure_generating_support_water: "生扶支持形态",
};

const compatStrengthReasonLabels: Record<string, string> = {
  no_predicate_matched: "本盘未命中任何已审局部形态条件",
  out_of_scope: "本盘的日主与月份组合不在已审谓词范围内",
  insufficient_evidence: "本盘的谓词条件证据不足",
};

const compatPatternReasonLabels: Record<string, string> = {
  month_not_yin: "本盘不在寅月，不属于任氏寅月局部真格研究范围",
  birth_uncomputable: "出生时刻无法核验司令段",
  pilot_uncertain: "司令试点未确立，暂不可判",
  pilot_rejected: "司令试点未通过核验，暂不可判",
  pilot_not_applicable: "司令试点不适用，暂不可判",
  pattern_name_not_public: "本盘的格名暂不在公开呈现范围内",
  luren_route_precedence: "本盘月逢禄刃，月令格局路线已关闭，本次不作呈现",
  pilot_result_unverifiable: "司令试点结果无法核验，本次不作呈现",
  pilot_not_computed: "司令试点未确立，本次不作呈现",
  commander_not_month_hidden: "司令不在月支藏干中，本次不作呈现",
};

const compatPatternPillarLabels: Record<string, string> = {
  year: "年干",
  month: "月干",
  hour: "时干",
};

const compatRelationKindLabels: Record<string, string> = {
  support: "两体系同向",
  conflict: "两体系方向相反",
  pivot_overlap: "两体系同指所论之神",
  one_sided: "仅一方点名",
};

const compatBingyaoRoleLabels: Record<string, string> = {
  subject: "病药所论之神",
  disease: "病药判为病之神",
  medicine: "病药判为药之神",
};

const compatBingyaoPairOrdinals: Record<string, string> = {
  wealth_peer_officer: "第一对",
  foodwound_seal_wealth: "第二对",
};

const compatDayunMethodLabels: Record<string, string> = {
  sanming: "三命口径",
  shenfeng: "神峰口径",
};

function compatRelationLine(item: any): string {
  const parts: string[] = [];
  if (item.tiaohou) parts.push(`调候取用顺序第 ${item.tiaohou.order} 位`);
  if (item.bingyao) {
    parts.push(
      `${compatBingyaoRoleLabels[item.bingyao.role] || "病药点名"}（${compatBingyaoPairOrdinals[item.bingyao.pair_id] || ""}）`,
    );
  }
  return `干${item.stem}：${compatRelationKindLabels[item.kind] || item.kind}。${parts.join("；")}。`;
}

function compatScopeDetails(p: any, keyPrefix: string) {
  return (
    <details className="compat-scope-details">
      <summary>查看范围与限制</summary>
      {typeof p.scope_statement === "string" && p.scope_statement && (
        <p>{p.scope_statement}</p>
      )}
      {Array.isArray(p.limitations) && p.limitations.map((line: string, i: number) => (
        <p key={`${keyPrefix}-${i}`}>{line}</p>
      ))}
    </details>
  );
}

function renderCompatStrength(p: any) {
  if (!p) return null;
  if (p.status === "presented") {
    return (
      <div className="compat-pres-block">
        <h4>命盘结构分析</h4>
        <p>日主{p.day_master}生于{p.month_branch}月，命中了一个已审的局部形态：{compatStrengthPredicateLabels[p.predicate_id || ""] || "已审局部形态条件命中"}。</p>
        <p>限定形态：{p.classification === "strong" ? "强形态" : p.classification === "weak" ? "弱形态" : "—"}</p>
        <p>规则来源：{p.rule_registration === "registered" ? "已通过审核的局部形态条件" : "尚在审核登记中的局部形态条件"}</p>
        {p.segment_gate && (
          <p>出生时刻已对照本月已核验的时段核查通过：{p.segment_gate.segment_stem}段。</p>
        )}
        <p>该结论只覆盖这一个已审形态，不覆盖全盘。</p>
        {compatScopeDetails(p, "s")}
      </div>
    );
  }
  if (p.status === "not_judgeable") {
    return (
      <div className="compat-pres-block">
        <h4>命盘结构分析</h4>
        <p>{compatStrengthReasonLabels[p.reason || ""] || "本盘暂不可判"}；未命中不等于弱。</p>
        <p>暂不可判，不作任何强弱结论。</p>
        {compatScopeDetails(p, "s")}
      </div>
    );
  }
  if (p.status === "conflict") {
    return (
      <div className="compat-pres-block">
        <h4>命盘结构分析</h4>
        <p>本盘存在未裁定的冲突，暂不可判；不作任何强弱结论。</p>
        {(p.blocker_reasons || []).map((reason: string, i: number) => (
          <p key={`cb-${i}`}>{reason}</p>
        ))}
        {compatScopeDetails(p, "s")}
      </div>
    );
  }
  return null;
}

function renderCompatPattern(p: any) {
  if (!p) return null;
  if (p.status === "presented") {
    return (
      <div className="compat-pres-block">
        <h4>任氏寅月局部真格研究结果</h4>
        <p>日主{p.day_master}生于寅月，{p.statement}</p>
        {p.outcome === "true_pattern" && p.pattern && <p>格名：{p.pattern}</p>}
        {p.commander && (
          <p>司令{p.commander.stem}（{p.commander.ten_god}）透于{(p.commander.visible_pillars || []).map((pillar: string) => compatPatternPillarLabels[pillar] || pillar).join("、")}。</p>
        )}
        <p>该结论只覆盖这一个已审局部事实，不覆盖全盘格局。</p>
        {compatScopeDetails(p, "p")}
      </div>
    );
  }
  if (p.status === "not_judgeable") {
    return (
      <div className="compat-pres-block">
        <h4>任氏寅月局部真格研究结果</h4>
        <p>{compatPatternReasonLabels[p.reason || ""] || "本盘暂不可判"}；暂不可判，不作任何格局结论。</p>
        {compatScopeDetails(p, "p")}
      </div>
    );
  }
  if (p.status === "abstained") {
    return (
      <div className="compat-pres-block">
        <h4>任氏寅月局部真格研究结果</h4>
        <p>{compatPatternReasonLabels[p.reason || ""] || "本次不作呈现"}；不作任何格局结论。</p>
        {compatScopeDetails(p, "p")}
      </div>
    );
  }
  return null;
}

function renderCompatXiyongBlock(block: any, heading: string) {
  if (!block) return null;
  const lines = Array.isArray(block.lines) ? block.lines : [];
  return (
    <div>
      <h4>{heading}（{block.source_label || heading}）</h4>
      {lines.length ? lines.map((line: string, i: number) => (
        <p key={`${heading}-${i}`}>{line}</p>
      )) : <p>本次没有呈现条目。</p>}
      {block.evidence?.quote && (
        <details className="compat-scope-details">
          <summary>查看判断依据：{block.source_label}</summary>
          <blockquote><p>{block.evidence.quote}</p></blockquote>
        </details>
      )}
      {Array.isArray(block.evidence?.quotes) && block.evidence.quotes.length > 0 && (
        <details className="compat-scope-details">
          <summary>查看判断依据：{block.source_label}</summary>
          {block.evidence.quotes.map((q: any, qi: number) => (
            <blockquote key={`q-${qi}`}><p>{q.quote}</p></blockquote>
          ))}
        </details>
      )}
    </div>
  );
}

function renderCompatXiyong(x: any) {
  if (!x) return null;
  const relations = Array.isArray(x.relations) ? x.relations : [];
  return (
    <div className="compat-pres-block">
      <h4>调候与病药：原文依据怎么说？</h4>
      {renderCompatXiyongBlock(x.blocks?.tiaohou, "调候")}
      {renderCompatXiyongBlock(x.blocks?.bingyao, "病药")}
      {relations.length > 0 && (
        <>
          <h4>两体系点名对照</h4>
          {relations.map((item: any) => (
            <p key={item.stem}>{compatRelationLine(item)}</p>
          ))}
          {relations.map((item: any) => item.not_judgeable_line ? (
            <p key={`nj-${item.stem}`}>{item.not_judgeable_line}</p>
          ) : null)}
          {typeof x.relations_closing_line === "string" && x.relations_closing_line && (
            <p>{x.relations_closing_line}</p>
          )}
        </>
      )}
      <p><strong>统一裁决：弃判。</strong>两体系并列呈现，不作统一裁决；扶抑、格局用神等其他取用判断尚未建成，暂不可判。</p>
      {compatScopeDetails(x, "x")}
    </div>
  );
}

// 首运呈现：只取两口径各自的第 1 运区间，第 2–8 运在本页不展开。
// 与服务端 _first_period_dayun_for_career_life 同一口径：只呈现首运，
// 不折算起运岁数，不输出单点日期。
function renderCompatFirstDayun(dayun: any, method: "sanming" | "shenfeng") {
  if (!dayun) return null;
  const view = dayun.methods?.[method];
  if (!view) return <p>本口径暂无大运呈现。</p>;
  if (view.status === "unresolved") {
    return <p>交运时间暂不可判：{view.reason || "本口径未能换算交运区间"}。不以近似值填充。</p>;
  }
  const first = Array.isArray(view.entries) ? view.entries[0] : null;
  if (!first) return <p>本口径暂无大运呈现。</p>;
  return (
    <div>
      <p>
        <strong>第 1 运 {first.ganzhi}</strong>
        <span>（{first.ten_god_relative_to_natal_day_stem}）</span>
      </p>
      {first.state === "interval" && first.start_interval ? (
        <p>交运区间：{first.start_interval.earliest} 至 {first.start_interval.latest}（不含上限）</p>
      ) : first.state === "not_provided" ? (
        <p>交运区间未提供：本口径只呈现首运交运区间。</p>
      ) : (
        <p>交运时间暂不可判。</p>
      )}
      <p>第 2–8 运在本页未展开。</p>
    </div>
  );
}


function evidenceLabel(id: string, value: Record<string, any>) {
  const title = value.classic_title || value.title || value.source_title;
  const quote = value.original_text;
  if (typeof title !== "string" || !title.trim() ||
      typeof quote !== "string" || !quote.trim()) return null;
  return { id, title, quote, grade: typeof value.evidence_level === "string" ? value.evidence_level : "未标注",
    excerpt: value.original_text_excerpt === true || value.classic_title_excerpt === true };
}

export function CompatibilityStructurePage() {
  // TJ-029.2 P1: A 方档案用 state 而不用 useMemo，页内清除后可就地重置；
  // 其他标签页清除时由 PublicApp 重载整页（重新读取档案）。
  const [saved, setSaved] = useState(() => readSavedBirthProfile());
  const [aName, setAName] = useState("我");
  const [bName, setBName] = useState("对方");
  const [aDate, setADate] = useState(() => toSolarDateString(saved));
  const [aTime, setATime] = useState(saved.time);
  // A 使用 saved.region（原始档案），不单独维护时区
  const [aRole, setARole] = useState<"" | "male" | "female">("");
  const [bDate, setBDate] = useState("");
  const [bTime, setBTime] = useState("");
  const [bRegion, setBRegion] = useState("中国大陆");
  const [bRole, setBRole] = useState<"" | "male" | "female">("");
  const [result, setResult] = useState<ScenarioExecuteResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  // TJ-0427 Lane D: each person's approved presentations, lifted from a
  // bazi-profile envelope for the same birth input (exactly as the
  // career page lifts them server-side). A failed lift only puts the
  // pattern/xiyong/dayun sections into an error state -- it never
  // masks itself as not_judgeable and never blocks the compat result.
  const [profiles, setProfiles] = useState<{ a: ScenarioExecuteResponse | null; b: ScenarioExecuteResponse | null } | null>(null);
  const [profilesLoading, setProfilesLoading] = useState(false);
  const [profilesError, setProfilesError] = useState(false);
  const [dayunMethod, setDayunMethod] = useState<"sanming" | "shenfeng">("sanming");
  const requestVersion = useRef(0);
  const [resultNames, setResultNames] = useState({a: "我", b: "对方"});
  // TJ-029.2 P1: 页内清除本机资料后的回执
  const [clearNote, setClearNote] = useState("");

  useEffect(() => () => { requestVersion.current += 1; }, []);

  function clearSavedProfile() {
    invalidateResult();
    clearBirthProfile();
    setSaved({ calendarType: "solar", year: 0, month: 0, day: 0, isLeapMonth: false, time: "", timeUnknown: false, region: "中国大陆" });
    setADate("");
    setATime("");
    setClearNote("已清除本机保存的出生资料。对方资料仅用于本次合盘计算，本就不保存到本机。");
  }

  function invalidateResult() {
    requestVersion.current += 1;
    setResult(null);
    setError("");
    setLoading(false);
    setProfiles(null);
    setProfilesLoading(false);
    setProfilesError(false);
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
    setProfiles(null);
    setProfilesLoading(false);
    setProfilesError(false);
    try {
      // Both birth values are computed once here and reused for the
      // compatibility call and the per-person profile lifts below, so
      // all three requests describe the same two birth instants.
      // They stay inside try: toApiValue throws on invalid input
      // (e.g. a region spanning multiple time zones) and the catch
      // below must surface it as the form alert instead of letting
      // the submit die silently.
      const aBirth = (() => {
        const initialSolar = toSolarDateString(saved);
        if (aDate === initialSolar && aTime === saved.time) {
          return toApiValue(saved);
        }
        if (aDate === initialSolar) {
          return toApiValue(withUpdatedTime(saved, aTime));
        }
        return toApiValue(fromSolarEdit(aDate, aTime, saved.region, saved));
      })();
      const bBirth = toApiValue(fromSolarEdit(bDate, bTime, bRegion));
      const input: {
        person_a_birth_value: string;
        person_b_birth_value: string;
        person_a_zone?: string;
        person_b_zone?: string;
        person_a_traditional_role?: "male" | "female";
        person_b_traditional_role?: "male" | "female";
      } = {
        person_a_birth_value: aBirth,
        person_a_zone: toApiZone(saved),
        person_b_birth_value: bBirth,
        person_b_zone: regionToTimezone(bRegion),
      };
      if (aRole) input.person_a_traditional_role = aRole;
      if (bRole) input.person_b_traditional_role = bRole;
      const next = await executeCompatibilityScenario(input);
      if (version !== requestVersion.current) return;
      // A：仅用户显式修改后才更新；未修改不覆写原始档案
      (() => {
        const initialSolar = toSolarDateString(saved);
        if (aDate === initialSolar && aTime === saved.time) return;
        if (aDate === initialSolar) {
          saveBirthProfile(withUpdatedTime(saved, aTime));
          return;
        }
        saveBirthProfile(fromSolarEdit(aDate, aTime, saved.region, saved));
      })();
      setResultNames({a: aName.trim() || "我", b: bName.trim() || "对方"});
      setResult(next);
      // Lift each person's approved presentations (strength / pattern /
      // xiyong / first-period dayun) from bazi-profile for the same
      // birth input. The traditional role is only sent when the user
      // explicitly selected it, so dayun appears only then.
      setProfilesLoading(true);
      const [aProfile, bProfile] = await Promise.allSettled([
        executeBaziProfileScenario({
          value: aBirth,
          zone: toApiZone(saved),
          strength_variant: "ditiansui-root-visibility-v1",
          ...(aRole ? { traditional_role: aRole } : {}),
        }),
        executeBaziProfileScenario({
          value: bBirth,
          zone: regionToTimezone(bRegion),
          strength_variant: "ditiansui-root-visibility-v1",
          ...(bRole ? { traditional_role: bRole } : {}),
        }),
      ]);
      if (version !== requestVersion.current) return;
      setProfiles({
        a: aProfile.status === "fulfilled" ? aProfile.value : null,
        b: bProfile.status === "fulfilled" ? bProfile.value : null,
      });
      setProfilesError(aProfile.status === "rejected" || bProfile.status === "rejected");
      setProfilesLoading(false);
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
            并把双方四柱之间已审核的合/冲/害命中分层展示。下方同时并列双方已批准的有限呈现
            （旺衰局部形态、寅月真格、调候病药）与各自首运；合盘本身不作推断。
            你也可以主动开启传统配偶星观察，但系统不会替你推断口径。
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
          { side: "A", name: aName, setName: setAName, date: aDate, setDate: setADate, time: aTime, setTime: setATime, role: aRole, setRole: setARole, saved: Boolean(saved.year), region: saved.region, setRegion: null, isLunar: isConvertedFromLunar(saved) },
          { side: "B", name: bName, setName: setBName, date: bDate, setDate: setBDate, time: bTime, setTime: setBTime, role: bRole, setRole: setBRole, saved: false, region: bRegion, setRegion: setBRegion, isLunar: false },
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
            {person.setRegion ? (
              <label>
                <span>出生地区</span>
                <select value={person.region} onChange={(e) => { invalidateResult(); person.setRegion(e.target.value); }}>
                  {REGION_OPTIONS.map((o) => (
                    <option key={o.value} value={o.value}>{o.label}</option>
                  ))}
                </select>
              </label>
            ) : (
              <p className="birth-note">出生地区：{person.region}{person.isLunar ? "（当前显示的是换算后公历）" : ""}</p>
            )}
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
        <p className="compat-privacy-notice" role="note">
          对方出生资料仅用于本次合盘计算，不会保存到本机浏览器。请确保已获得对方知情同意。资料将提交至后端进行结构计算，服务端留存以实际部署策略为准。
        </p>
        <div className="compat-submit-wrap">
          <button type="button" className="sample-fill" onClick={fillSample}>填入双人示例</button>
          <button className="button primary" type="submit" disabled={loading}>
            {loading ? "正在合盘…" : "生成双人结构"}
            {!loading && <Icon name="arrow" size={18} />}
          </button>
          <button
            type="button"
            className="sample-fill"
            onClick={() => {
              invalidateResult();
              setBName("对方");
              setBDate("");
              setBTime("");
              setBRegion("中国大陆");
              setBRole("");
              setResultNames({ a: "我", b: "对方" });
              setError("");
            }}
          >
            清空对方资料
          </button>
          <button type="button" className="sample-fill" onClick={clearSavedProfile}>清除本机资料</button>
        </div>
        {clearNote && <p className="compat-clear-note" role="status">{clearNote}</p>}
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
              <span className="eyebrow">真实双人排盘 · 结构限定版</span>
              <h2>{resultNames.a} × {resultNames.b}</h2>
              <p>双向分别计算，不把任何一方的视角当成唯一结论。</p>
            </div>
            <span className="compat-limited">合盘结构</span>
          </header>

          <section className="compat-section" aria-label="本次合盘摘要">
            <div className="result-section-heading">
              <div><span>合</span><h2>先看两人的命理结构</h2></div>
              <small>双方视角独立 · 仅供传统文化参考</small>
            </div>
            <p>
              {resultNames.a} 的日主为 {a.day_master?.stem || "—"}
              {a.day_master?.polarity && a.day_master?.element ? `（${a.day_master.polarity}${a.day_master.element}）` : ""}，
              {resultNames.b} 的日主为 {b.day_master?.stem || "—"}
              {b.day_master?.polarity && b.day_master?.element ? `（${b.day_master.polarity}${b.day_master.element}）` : ""}。
              从 {resultNames.a} 看 {resultNames.b}，两位日主对应 {relations.a_sees_b?.ten_god || "—"}；
              从 {resultNames.b} 看 {resultNames.a}，对应 {relations.b_sees_a?.ten_god || "—"}。
            </p>
            <p>
              本次已审核的双方四柱交叉结构命中 {crossMatrixHits.length} 处；
              双方日支关系命中 {spouseRelations.length} 处。
              这些是实际排盘与固定规则对应的观察，不是缘分评分，也不代表现实婚姻结果。
            </p>
            <p>
              双方格局、喜用与大运见下方第五、六节；合盘推理的边界见第七节。
            </p>
            <p className="compat-note">
              下面可分别查看双方四柱、关系矩阵和真实古籍依据。缺乏审核证据的婚期、正缘和感情吉凶不作推断。
            </p>
          </section>

          <div className="compat-people">
            {people.map((person) => (
              <section key={person.id}>
                <div className="compat-person-head">
                  <span>{person.id.toUpperCase()}</span>
                  <div><small>{person.name}</small><strong>日主 {person.data.day_master?.stem || "—"}{person.data.day_master?.polarity && person.data.day_master?.element ? ` · ${person.data.day_master.polarity}${person.data.day_master.element}` : ""}</strong></div>
                </div>
                <div className="compat-pillars">
                  {(person.data.pillars || []).map((pillar: any) => {
                    const hidden = Array.isArray(pillar.branch?.hidden_stems) ? pillar.branch.hidden_stems : [];
                    return (
                      <article key={pillar.name} className={pillar.name === "day" ? "day-pillar" : ""}>
                        <small>{pillarNames[pillar.name] || pillar.name}</small>
                        <strong>{pillar.ganzhi}</strong>
                        <span>{pillar.stem?.ten_god}{pillar.stem?.element ? ` · ${pillar.stem.element}` : ""}</span>
                        {hidden.length > 0 && (
                          <em className="compat-hidden-stems">藏干 {hidden.map((h: any) => `${h.stem} ${h.ten_god}`).join(" · ")}</em>
                        )}
                      </article>
                    );
                  })}
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
                    {(() => {
                      const lens = person.data.traditional_spouse_star_lens;
                      const visible = Array.isArray(lens.visible_positions) ? lens.visible_positions : [];
                      const hidden = Array.isArray(lens.hidden_positions) ? lens.hidden_positions : [];
                      return (
                        <>
                          {visible.length > 0 && (
                            <span>明见 {visible.map((pos: any) => `${pillarNames[pos.pillar] || pos.pillar}${pos.stem} ${pos.ten_god}`).join("、")}</span>
                          )}
                          {hidden.length > 0 && (
                            <span>藏干 {hidden.map((pos: any) => `${pillarNames[pos.pillar] || pos.pillar}（${pos.branch}藏干）${pos.stem} ${pos.ten_god}`).join("、")}</span>
                          )}
                          {visible.length === 0 && hidden.length === 0 && (
                            <span>明见 0 处 · 藏干 0 处</span>
                          )}
                        </>
                      );
                    })()}
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
            <p className="compat-note">
              地支刑：未评估。刑表不存在，不自造刑表，不作任何刑相关结论。
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
              <span>天干五合 <b>{crossMatrix.summary?.stem_five_combination || 0}</b></span>
              <span>地支六合 <b>{crossMatrix.summary?.six_harmony || 0}</b></span>
              <span>六害 <b>{crossMatrix.summary?.harm || 0}</b></span>
              <span>六冲 <b>{crossMatrix.summary?.clash || 0}</b></span>
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
              <div><span>五</span><h2>双方格局与喜用</h2></div>
              <small>已批准的有限呈现 · 两人并列，不作综合结论</small>
            </div>
            <p className="compat-note">
              以下取自两人各自八字命理页的已批准公开呈现：U1 最小公开旺衰、D-1 任氏寅月真格白名单、调候与病药 phase-1。
              格局用神仍未裁定，本页不呈现任何格局用神结论。
            </p>
            <div className="compat-person-presentations">
              {[
                { id: "a", name: resultNames.a, profile: profiles?.a ?? null, roleSelected: Boolean(aRole) },
                { id: "b", name: resultNames.b, profile: profiles?.b ?? null, roleSelected: Boolean(bRole) },
              ].map((person) => (
                <article key={person.id} className="compat-presentation-card">
                  <header><strong>{person.name}</strong><small>日主 {person.profile?.result?.strength_presentation?.day_master || person.profile?.result?.pattern_presentation?.day_master || "—"}</small></header>
                  {profilesLoading && !person.profile && <p>正在加载…</p>}
                  {profilesError && !person.profile && (
                    <p className="compat-pres-error" role="alert">个人呈现加载失败，请稍后重试。这不是暂不可判：本次请求未能完成计算。</p>
                  )}
                  {person.profile && (
                    <>
                      {renderCompatStrength(person.profile.result?.strength_presentation)}
                      {renderCompatPattern(person.profile.result?.pattern_presentation)}
                      {renderCompatXiyong(person.profile.result?.xiyong_presentation)}
                    </>
                  )}
                </article>
              ))}
            </div>
            <p className="compat-note">
              双方格局与喜用只并列呈现，不作综合结论；目前没有已批准的合盘推理输出。
            </p>
          </section>

          <section className="compat-section">
            <div className="result-section-heading">
              <div><span>六</span><h2>双方大运 · 只看首运</h2></div>
              <small>与事业、总览页同一口径 · 第 2–8 运不展开</small>
            </div>
            <div className="compat-dayun-switch" role="tablist" aria-label="大运口径切换">
              {(["sanming", "shenfeng"] as const).map((m) => (
                <button
                  key={m}
                  type="button"
                  role="tab"
                  aria-selected={dayunMethod === m}
                  className={dayunMethod === m ? "active" : ""}
                  onClick={() => setDayunMethod(m)}
                >
                  {compatDayunMethodLabels[m]}
                </button>
              ))}
            </div>
            <div className="compat-person-presentations">
              {[
                { id: "a", name: resultNames.a, profile: profiles?.a ?? null, roleSelected: Boolean(aRole) },
                { id: "b", name: resultNames.b, profile: profiles?.b ?? null, roleSelected: Boolean(bRole) },
              ].map((person) => (
                <article key={person.id} className="compat-presentation-card">
                  <header><strong>{person.name}</strong><small>{compatDayunMethodLabels[dayunMethod]}</small></header>
                  {profilesLoading && !person.profile && <p>正在加载…</p>}
                  {profilesError && !person.profile && (
                    <p className="compat-pres-error" role="alert">个人呈现加载失败，请稍后重试。这不是暂不可判：本次请求未能完成计算。</p>
                  )}
                  {!person.roleSelected && person.profile && (
                    <p>未选择传统大运口径，因此不呈现大运。本页不默认、不推断口径。</p>
                  )}
                  {person.roleSelected && person.profile && (
                    <>
                      {renderCompatFirstDayun(person.profile.result?.dayun_presentation, dayunMethod)}
                      <p className="compat-note">交运时间只给区间，不折算起运岁数或单点日期。</p>
                    </>
                  )}
                </article>
              ))}
            </div>
          </section>

          <section className="compat-section compat-boundary">
            <div className="result-section-heading">
              <div><span>七</span><h2>合盘推理边界</h2></div>
              <small>本页能说什么，到这里为止</small>
            </div>
            <p>
              目前没有已批准的合盘推理输出。本页只并列双方结构事实与已批准的有限呈现，不作综合结论，
              不输出缘分高低、正缘结论、结婚时间或分手风险。
            </p>
            <p className="compat-note">
              格局用神仍未裁定：除 D-1 白名单外，格局用神逐格规则待证据审查，本页不呈现任何格局用神结论，也不展示内部就绪表。
            </p>
          </section>

          <section className="compat-section">
            <div className="result-section-heading">
              <div><span>八</span><h2>关系证据矩阵</h2></div>
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
                  <p>古籍依据 {(item.evidence_ids || []).length} 条 · 不作解释</p>
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
                            <p>{ref.quote}{ref.excerpt ? "（节选）" : ""}</p>
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
              <div className="result-section-heading"><div><span>九</span><h2>典籍依据</h2></div></div>
              {evidence.map((item) => (
                <article className="live-evidence" key={item.id}>
                  <div><strong>{item.title}</strong><span>{item.grade}</span></div>
                  <blockquote>{item.quote}{item.excerpt ? "（节选）" : ""}</blockquote>
                </article>
              ))}
            </section>
            <section className="compat-section">
              <div className="result-section-heading"><div><span>十</span><h2>当前不能说什么</h2></div></div>
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
              <div><strong>查看双人计算过程</strong><small>{result.trace.length} 个计算步骤</small></div>
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
