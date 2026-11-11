import { useEffect, useRef, useState } from "react";
import type { FormEvent } from "react";
import { Icon } from "../shared/Icon";
import { Link } from "../shared/router";
import { executeBazi, executeBaziProfileScenario, type ExecuteResponse } from "./api";
import { readSavedBirthProfile, saveBirthProfile, clearBirthProfile, toApiValue, toApiZone, validateBirthInput, onBirthProfileCleared, type BirthProfile } from "./birthProfile";
import { BirthInputFields } from "./BirthInputFields";
import "./bazi-profile.css";

const pillarNames: Record<string, string> = {
  year: "年柱",
  month: "月柱",
  day: "日柱",
  hour: "时柱",
};

// TJ-013.3 第一阶段：关系段的结构化转写标签（只转写呈现对象字段，
// 不生成任何新判断）。
const relationKindLabels: Record<string, string> = {
  support: "两体系同向",
  conflict: "两体系方向相反",
  pivot_overlap: "两体系同指所论之神",
  one_sided: "仅一方点名",
};

const bingyaoRoleLabels: Record<string, string> = {
  subject: "病药所论之神",
  disease: "病药判为病之神",
  medicine: "病药判为药之神",
};

const bingyaoPairOrdinals: Record<string, string> = {
  wealth_peer_officer: "第一对",
  foodwound_seal_wealth: "第二对",
};

// TJ-017.3 第二阶段：大运呈现的口径标签与暂不可判原因转写（只转写
// 呈现对象字段，不生成任何新判断；两口径分立呈现，永不合并）。
const dayunMethodLabels: Record<string, string> = {
  sanming: "三命通会口径",
  shenfeng: "神峰通考口径",
};

const dayunReasonLabels: Record<string, string> = {
  zero_jie_boundary_convention_unreviewed:
    "出生时刻恰逢节气交界，交运换算口径尚未裁定",
  zero_day_count_not_exemplified_in_text:
    "本口径以整日计数，本盘整日数为零，原文未给出此情形的示例",
};

// TJ-013.3 U1 Batch C：已审强弱形态事实的呈现转写（只转写呈现对象
// 字段，不生成任何新判断）。谓词描述只转述日主×月份形态，永不写
// 身旺/身弱；默认阅读流中规则 id、证据哈希、Trace 一律不渲染
// （门控执行证据在场景信封中无法解析为引文，且用户 brief 明令
// 默认视图不展示技术字段），只渲染通俗转述后的注册状态，不渲染证据条数；
// 完整技术信息只放在页底默认折叠的“专业审计视图”内。金×酉谓词
// 按后端证明永不呈现，此处映射仅为防御未知形态不崩溃。
const strengthPredicateLabels: Record<string, string> = {
  pure_support: "纯粹支持形态",
  pure_generating_support: "生扶支持形态",
  isolated_control: "孤立受制形态",
  commanding_visible_support: "司令显现支持形态",
  lu_visible_support: "禄位显现支持形态",
  changsheng_visible_support: "长生显现支持形态（司令甲段）",
  pure_support_metal: "纯粹支持形态",
  pure_generating_support_water: "生扶支持形态",
};

// 最终收尾：后端 scope/limitations 原文仍可能带工程措辞（充分谓词、
// Variant 编号、strength_variant 参数名）；默认视图在渲染时就地转述
// 为通俗中文，后端原文本身不改。调候/病药/大运区块不经过本函数，
// 内容保持原样；专业审计视图内的技术信息也不经过本函数。
function plainUserText(text: string): string {
  return text
    .replace(/充分谓词家族/g, "局部形态条件类型")
    .replace(/充分谓词/g, "局部形态条件")
    .replace(/谓词已注册/g, "这一类已通过审核")
    .replace(/谓词/g, "局部形态条件")
    .replace(/strength_variant/g, "强度因素口径")
    .replace(/[a-z][a-z0-9-]*-v\d+/g, "")
    .replace(/Variant/g, "版本")
    .replace(/\s{2,}/g, " ")
    .trim();
}

// not_judgeable 在一切用户文案中都是无确定结论：只转述后端原因，
// 永不写成弱或倾向性暗示。
const strengthReasonLabels: Record<string, string> = {
  no_predicate_matched: "本盘未命中任何已审局部形态条件",
  out_of_scope: "本盘的日主与月份组合不在已审谓词范围内",
  insufficient_evidence: "本盘的谓词条件证据不足",
};

// TJ-012.3 Stage B：任氏寅月局部真格研究结果的呈现转写（只转写
// 呈现对象字段，不生成任何新判断）。只转述后端 pattern_presentation；
// 暂不可判与不作呈现只转述后端原因，永不写成假格或改写格名；格名
// 只在后端已呈现时原样显示。范围说明始终在场，不得省略。
const patternReasonLabels: Record<string, string> = {
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

const patternPillarLabels: Record<string, string> = {
  year: "年干",
  month: "月干",
  hour: "时干",
};

function relationLine(item: any): string {
  const parts: string[] = [];
  if (item.tiaohou) parts.push(`调候取用顺序第 ${item.tiaohou.order} 位`);
  if (item.bingyao) {
    parts.push(
      `${bingyaoRoleLabels[item.bingyao.role] || "病药点名"}（${bingyaoPairOrdinals[item.bingyao.pair_id] || ""}）`,
    );
  }
  return `干${item.stem}：${relationKindLabels[item.kind] || item.kind}。${parts.join("；")}。`;
}

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
    excerpt: value.original_text_excerpt === true || value.classic_title_excerpt === true,
  };
}

export function BaziProfilePage() {
  const [profile, setProfile] = useState<BirthProfile>(() => readSavedBirthProfile());
  const [inputError, setInputError] = useState("");
  const [result, setResult] = useState<ExecuteResponse | null>(null);
  const [xiyong, setXiyong] = useState<any>(null);
  // TJ-017.3 第二阶段：传统大运口径为可选逐请求输入，缺省不选择；
  // 不写入出生资料档案、不进 URL。
  const [dayunRole, setDayunRole] = useState<"" | "male" | "female">("");
  const [dayun, setDayun] = useState<any>(null);
  const [dayunMethod, setDayunMethod] = useState<"sanming" | "shenfeng">("sanming");
  // TJ-013.3 U1 Batch C：强度呈现取自同一场景信封；场景调用失败时
  // 只令强度节进入错误态，不以暂不可判掩盖（xiyong/dayun 的既有
  // 缺席行为不变）。
  const [strengthPresentation, setStrengthPresentation] = useState<any>(null);
  const [strengthLoadError, setStrengthLoadError] = useState(false);
  // TJ-012.3 Stage B：格局局部呈现取自同一场景信封；场景调用失败时
  // 与强度节同一错误态（xiyong/dayun 的既有缺席行为不变）。
  const [patternPresentation, setPatternPresentation] = useState<any>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const requestVersion = useRef(0);

  useEffect(() => () => { requestVersion.current += 1; }, []);

  // TJ-006.3: 其他标签页清除资料时，本页同步清空
  useEffect(() => onBirthProfileCleared(() => {
    invalidateResult();
    setProfile({ calendarType: "solar", year: 0, month: 0, day: 0, isLeapMonth: false, time: "", timeUnknown: false, region: "中国大陆" });
    setInputError("");
  }), []);

  function invalidateResult() {
    requestVersion.current += 1;
    setResult(null);
    setXiyong(null);
    setDayun(null);
    setStrengthPresentation(null);
    setPatternPresentation(null);
    setStrengthLoadError(false);
    setError("");
    setLoading(false);
  }

  function fillSample() {
    invalidateResult();
    const sample: BirthProfile = {
      calendarType: "solar",
      year: 2000, month: 1, day: 7,
      isLeapMonth: false,
      time: "12:00", timeUnknown: false,
      region: "中国大陆",
    };
    setProfile(sample);
    setInputError("");
  }

  async function submit(event: FormEvent) {
    event.preventDefault();
    const v = validateBirthInput(profile);
    if (!v.ok) {
      setInputError(v.ok === false ? v.message : "");
      return;
    }
    setInputError("");
    const version = ++requestVersion.current;
    setLoading(true);
    setError("");
    setResult(null);
    setXiyong(null);
    setDayun(null);
    setStrengthPresentation(null);
    setPatternPresentation(null);
    setStrengthLoadError(false);
    try {
      const response = await executeBazi({ value: toApiValue(profile), zone: toApiZone(profile), strength_variant: "ditiansui-root-visibility-v1" });
      if (version !== requestVersion.current) return;
      saveBirthProfile(profile);
      setResult(response);
      // TJ-013.3 第一阶段 + TJ-017.3 第二阶段：同一出生输入另取场景
      // 信封中的呈现对象；传统口径仅在用户显式选择时随请求发送。
      // 场景调用失败只令 xiyong/dayun 呈现节缺席（既有行为不变），
      // 但强度节必须进入错误态，不得以暂不可判掩盖执行失败。
      try {
        const scenarioInput: { value: string; zone?: string; strength_variant?: string; traditional_role?: "male" | "female" } = { value: toApiValue(profile), zone: toApiZone(profile), strength_variant: "ditiansui-root-visibility-v1" };
        if (dayunRole) scenarioInput.traditional_role = dayunRole;
        const scenario = await executeBaziProfileScenario(scenarioInput);
        if (version !== requestVersion.current) return;
        setXiyong(scenario.result?.xiyong_presentation ?? null);
        setDayun(scenario.result?.dayun_presentation ?? null);
        setStrengthPresentation(scenario.result?.strength_presentation ?? null);
        setPatternPresentation(scenario.result?.pattern_presentation ?? null);
        setStrengthLoadError(false);
      } catch {
        if (version === requestVersion.current) { setXiyong(null); setDayun(null); setStrengthPresentation(null); setPatternPresentation(null); setStrengthLoadError(true); }
      }
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
  // 当前分析边界去重：同一边界句只保留首次出现（后端 limitations
  // 本身含重复行，如三刑行出现两次）；不同事实一律保留。去重只看
  // 转述后的默认视图文本，调候/病药/大运原文行不在此集合内。
  const boundarySeen = new Set<string>();
  const firstBoundaryLine = (text: string) => {
    if (boundarySeen.has(text)) return false;
    boundarySeen.add(text);
    return true;
  };
  // 边界区去重后的默认视图行：先 domain 警告/限制（转述后），再强度
  // 范围/限制（转述后）；调候/病药/大运原文行保持原样、不参与去重。
  const boundaryDomainWarnings = (result?.warnings || []).map(plainUserText).filter(firstBoundaryLine);
  const boundaryDomainLimitations = (result?.limitations || []).map(plainUserText).filter(firstBoundaryLine);
  const boundaryStrengthScope = strengthPresentation
    ? (firstBoundaryLine(plainUserText(strengthPresentation.scope_statement)) ? plainUserText(strengthPresentation.scope_statement) : null)
    : null;
  const boundaryStrengthLimitations = strengthPresentation
    ? (strengthPresentation.limitations || []).map(plainUserText).filter(firstBoundaryLine)
    : [];
  // TJ-012.3 Stage B：格局局部呈现的范围与限制同样进入当前分析边界，
  // 与强度节同一去重规则；范围说明始终在场。
  const boundaryPatternScope = patternPresentation
    ? (firstBoundaryLine(plainUserText(patternPresentation.scope_statement)) ? plainUserText(patternPresentation.scope_statement) : null)
    : null;
  const boundaryPatternLimitations = patternPresentation
    ? (patternPresentation.limitations || []).map(plainUserText).filter(firstBoundaryLine)
    : [];

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
            已可核验月支藏干、通根候选和透藏位置；已注册的大运方向与交运区间可在下方按传统口径查看（须先选择传统口径）；
            但通用旺衰与完整喜用神结论仍未完成证据裁定，因此这里不会提前生成断语。
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
              <button type="button" className="sample-fill" onClick={() => {
                // 独立保存：未知时刻也可保存本地资料（仅本地存储，不提交计算）
                if (saveBirthProfile(profile)) {
                  setInputError("");
                } else {
                  const vr = validateBirthInput(profile);
                  setInputError(vr.ok ? "保存失败" : (vr as { message: string }).message);
                }
              }}>保存资料</button>
              <button type="button" className="sample-fill" onClick={() => { invalidateResult(); clearBirthProfile(); setProfile({ calendarType: "solar", year: 0, month: 0, day: 0, isLeapMonth: false, time: "", timeUnknown: false, region: "中国大陆" }); setInputError(""); }}>清除本机资料</button>
            </div>
          </div>

          <BirthInputFields
            value={profile}
            onChange={(p) => { invalidateResult(); setProfile(p); setInputError(""); }}
          />
          {/* TJ-017.3 第二阶段：可选传统大运口径（同合盘/桃花先例的
              历史类别显式选择）；缺省不选择，不选择时不呈现大运。 */}
          <div className="bazi-dayun-role">
            <label htmlFor="bazi-dayun-role">传统大运口径（可选）</label>
            <select
              id="bazi-dayun-role"
              value={dayunRole}
              onChange={(e) => { invalidateResult(); setDayunRole(e.target.value as "" | "male" | "female"); }}
            >
              <option value="">不启用</option>
              <option value="male">传统男命口径</option>
              <option value="female">传统女命口径</option>
            </select>
            <small>只用于按传统口径呈现大运方向与交运区间；不选择时不呈现大运时间轴。该选择只随本次计算发送，不保存。</small>
          </div>
          {inputError && <p className="question-error" role="alert">{inputError}</p>}

          <div className="bazi-input-note">
            <Icon name="shield" size={16} />
            <span>计算成功后出生资料仅保存在本浏览器以便其他场景复用，可随时清除。真太阳时与晚子时变体尚未开放。</span>
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
            <li>不自动定格局；调候与病药只呈现已注册依据，不作统一喜用结论</li>
            <li>不输出婚恋、事业、财富吉凶</li>
            <li>大运只呈现已注册的方向与交运区间，不折算起运岁数、不判断大运吉凶</li>
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
          <section className="bazi-overview" aria-label="命盘概览">
            <span className="eyebrow">命盘概览</span>
          <header className="bazi-result-head">
            <div>
              <span className="eyebrow">真实 API</span>
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
          </section>

          {/* UX overhaul：命盘结构分析是默认阅读顺序第 2 位（命盘概览之后、
              调候病药之前）。只转写后端 strength_presentation，前端不计算
              任何命理；无该键的旧信封、或未知状态一律不渲染本节。 */}
          {strengthPresentation && strengthPresentation.status === "presented" && (
            <section className="bazi-strength-presentation" aria-label="命盘结构分析">
              <span className="eyebrow">命盘结构 · 仅限一个已审局部形态</span>
              <h3>命盘结构分析</h3>
              <p>日主{strengthPresentation.day_master}生于{strengthPresentation.month_branch}月，命中了一个已审的局部形态：{strengthPredicateLabels[strengthPresentation.predicate_id] || "已审局部形态条件命中"}。</p>
              <p>限定形态：{strengthPresentation.classification === "strong" ? "强形态" : strengthPresentation.classification === "weak" ? "弱形态" : "—"}</p>
              <p>规则来源：{strengthPresentation.rule_registration === "registered" ? "已通过审核的局部形态条件" : "尚在审核登记中的局部形态条件"}</p>
              {strengthPresentation.segment_gate && (
                <p>出生时刻已对照本月已核验的时段核查通过：{strengthPresentation.segment_gate.segment_stem}段。</p>
              )}
              {strengthPresentation.day_master === "丙" && strengthPresentation.month_branch === "午" && strengthPresentation.predicate_id === "commanding_visible_support" && (
                <p>就本盘而言，这表示丙日主在午月满足了一项已审的支持条件——仅此而已，不再推出其他结论。</p>
              )}
              <p>该结论只覆盖这一个已审形态，不覆盖全盘。</p>
              <p className="bazi-strength-scope">{plainUserText(strengthPresentation.scope_statement)}</p>
              {strengthPresentation.limitations.map((l: string, i: number) => (
                <p key={`sl-${i}`} className="bazi-strength-scope">{plainUserText(l)}</p>
              ))}
              <details className="bazi-evidence-entry">
                <summary>查看判断依据</summary>
                <p>来源说明：同请求执行记录已核验。</p>
                <p>本呈现对象未附带原文引文文本，因此这里不列出引文。</p>
                <p>说明：{plainUserText(strengthPresentation.scope_statement)}</p>
                {strengthPresentation.limitations.map((l: string, i: number) => (
                  <p key={`sl-ev-${i}`} className="bazi-evidence-boundary">适用边界：{plainUserText(l)}</p>
                ))}
              </details>
            </section>
          )}

          {strengthPresentation && strengthPresentation.status === "not_judgeable" && (
            <section className="bazi-strength-presentation" aria-label="命盘结构分析·暂不可判">
              <span className="eyebrow">命盘结构 · 暂不可判</span>
              <h3>命盘结构分析</h3>
              <p className="bazi-strength-not-judgeable">{strengthReasonLabels[strengthPresentation.reason] || "本盘暂不可判"}；未命中不等于弱。</p>
              <p>暂不可判，不作任何强弱结论。</p>
              <p className="bazi-strength-scope">{plainUserText(strengthPresentation.scope_statement)}</p>
              {strengthPresentation.limitations.map((l: string, i: number) => (
                <p key={`sl-${i}`} className="bazi-strength-scope">{plainUserText(l)}</p>
              ))}
            </section>
          )}

          {strengthPresentation && strengthPresentation.status === "conflict" && (
            <section className="bazi-strength-presentation" aria-label="命盘结构分析·未裁定冲突">
              <span className="eyebrow">命盘结构 · 未裁定冲突</span>
              <h3>命盘结构分析</h3>
              <p className="bazi-strength-not-judgeable">本盘存在未裁定的冲突，暂不可判；不作任何强弱结论。</p>
              <p className="bazi-strength-scope">{plainUserText(strengthPresentation.scope_statement)}</p>
              {strengthPresentation.limitations.map((l: string, i: number) => (
                <p key={`sl-${i}`} className="bazi-strength-scope">{plainUserText(l)}</p>
              ))}
            </section>
          )}

          {!strengthPresentation && strengthLoadError && (
            <section className="bazi-strength-presentation" aria-label="命盘结构分析·加载失败">
              <span className="eyebrow">命盘结构 · 加载失败</span>
              <h3>命盘结构分析</h3>
              <p className="bazi-strength-error" role="alert">强弱形态事实加载失败，请稍后重试。这不是暂不可判：本次请求未能完成计算。</p>
            </section>
          )}

          {/* TJ-012.3 Stage B：格局局部研究是命盘结构分析内的一小节，
              与强度节同一版式、不是独立大卡。只转写后端
              pattern_presentation，前端不计算任何命理；无该键的旧信封、
              或未知状态一律不渲染本节。范围说明始终在场，以免误认
              为全盘格局判断。 */}
          {patternPresentation && patternPresentation.status === "presented" && patternPresentation.outcome === "true_pattern" && (
            <section className="bazi-strength-presentation" aria-label="命盘结构分析·格局局部研究">
              <span className="eyebrow">命盘结构 · 任氏寅月局部真格研究结果</span>
              <h4>任氏寅月局部真格研究结果</h4>
              <p>日主{patternPresentation.day_master}生于寅月，{patternPresentation.statement}</p>
              <p>格名：{patternPresentation.pattern}</p>
              <p>司令{patternPresentation.commander?.stem}（{patternPresentation.commander?.ten_god}）透于{(patternPresentation.commander?.visible_pillars || []).map((p: string) => patternPillarLabels[p] || p).join("、")}。</p>
              <p>该结论只覆盖这一个已审局部事实，不覆盖全盘格局。</p>
              <p className="bazi-strength-scope">{plainUserText(patternPresentation.scope_statement)}</p>
              {patternPresentation.limitations.map((l: string, i: number) => (
                <p key={`pl-${i}`} className="bazi-strength-scope">{plainUserText(l)}</p>
              ))}
            </section>
          )}

          {patternPresentation && patternPresentation.status === "presented" && patternPresentation.outcome === "commander_not_visible" && (
            <section className="bazi-strength-presentation" aria-label="命盘结构分析·格局局部研究">
              <span className="eyebrow">命盘结构 · 任氏寅月局部真格研究结果</span>
              <h4>任氏寅月局部真格研究结果</h4>
              <p>日主{patternPresentation.day_master}生于寅月，{patternPresentation.statement}</p>
              <p>该结论只覆盖这一个已审局部事实，不覆盖全盘格局。</p>
              <p className="bazi-strength-scope">{plainUserText(patternPresentation.scope_statement)}</p>
              {patternPresentation.limitations.map((l: string, i: number) => (
                <p key={`pl-${i}`} className="bazi-strength-scope">{plainUserText(l)}</p>
              ))}
            </section>
          )}

          {patternPresentation && patternPresentation.status === "not_judgeable" && (
            <section className="bazi-strength-presentation" aria-label="命盘结构分析·格局局部研究·暂不可判">
              <span className="eyebrow">命盘结构 · 任氏寅月局部真格研究结果</span>
              <h4>任氏寅月局部真格研究结果</h4>
              <p className="bazi-strength-not-judgeable">{patternReasonLabels[patternPresentation.reason] || "本盘暂不可判"}；暂不可判，不作任何格局结论。</p>
              <p className="bazi-strength-scope">{plainUserText(patternPresentation.scope_statement)}</p>
              {patternPresentation.limitations.map((l: string, i: number) => (
                <p key={`pl-${i}`} className="bazi-strength-scope">{plainUserText(l)}</p>
              ))}
            </section>
          )}

          {patternPresentation && patternPresentation.status === "abstained" && (
            <section className="bazi-strength-presentation" aria-label="命盘结构分析·格局局部研究·不作呈现">
              <span className="eyebrow">命盘结构 · 任氏寅月局部真格研究结果</span>
              <h4>任氏寅月局部真格研究结果</h4>
              <p className="bazi-strength-not-judgeable">{patternReasonLabels[patternPresentation.reason] || "本次不作呈现"}；不作任何格局结论。</p>
              <p className="bazi-strength-scope">{plainUserText(patternPresentation.scope_statement)}</p>
              {patternPresentation.limitations.map((l: string, i: number) => (
                <p key={`pl-${i}`} className="bazi-strength-scope">{plainUserText(l)}</p>
              ))}
            </section>
          )}

          {strength && (
            <section className="bazi-strength-observations" aria-label="旺衰因素与通根候选">
              {/* 最终收尾：本区从主阅读流改为默认折叠的扩展知识区，
                  与审计视图相同的 details/summary 按需展开模式；内文不变。 */}
              <details className="bazi-extended-details">
              <summary>旺衰因素与通根候选</summary>
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
              <details className="bazi-evidence-entry">
                <summary>查看判断依据</summary>
                {result.rule_matches.flatMap((rule) => Array.isArray(rule.evidence_ids)
                  ? rule.evidence_ids.map((id: string) => evidenceById.get(id)).filter(Boolean)
                  : []).filter((item: any, index: number, rows: any[]) =>
                    rows.findIndex((row) => row.id === item.id) === index
                  ).map((source: any) => (
                  <blockquote key={source.id}><b>{source.title} · {source.grade}</b><p>{source.quote}{source.excerpt ? "（节选）" : ""}</p></blockquote>
                ))}
              </details>
              </details>
            </section>
          )}

          {xiyong && (
            <section className="bazi-xiyong-presentation" aria-label="调候与病药取用依据">
              <span className="eyebrow">已注册取用依据 · 两体系并列呈现</span>
              <h3>调候与病药：原文依据怎么说？</h3>
              <h4>调候（{xiyong.blocks.tiaohou.source_label}）</h4>
              {xiyong.blocks.tiaohou.lines.map((line: string, i: number) => (
                <p key={`th-${i}`}>{line}</p>
              ))}
              {xiyong.blocks.tiaohou.evidence?.quote && (
                <details className="bazi-evidence-entry">
                  <summary>查看判断依据：{xiyong.blocks.tiaohou.source_label}</summary>
                  <p>来源：{xiyong.blocks.tiaohou.source_label}</p>
                  <blockquote><p>{xiyong.blocks.tiaohou.evidence.quote}</p></blockquote>
                  <p>说明：{xiyong.scope_statement}</p>
                  {xiyong.limitations.map((l: string, i: number) => (
                    <p key={`th-limit-${i}`} className="bazi-evidence-boundary">适用边界：{l}</p>
                  ))}
                </details>
              )}
              <h4>病药（{xiyong.blocks.bingyao.source_label}）</h4>
              {xiyong.blocks.bingyao.lines.map((line: string, i: number) => (
                <p key={`by-${i}`}>{line}</p>
              ))}
              {xiyong.blocks.bingyao.evidence?.quotes?.length ? (
                <details className="bazi-evidence-entry">
                  <summary>查看判断依据：{xiyong.blocks.bingyao.source_label}</summary>
                  <p>来源：{xiyong.blocks.bingyao.source_label}</p>
                  {xiyong.blocks.bingyao.evidence.quotes.map((q: any, qi: number) => (
                    <blockquote key={`byq-${qi}`}><p>{q.quote}</p></blockquote>
                  ))}
                  <p>说明：{xiyong.scope_statement}</p>
                  {xiyong.limitations.map((l: string, i: number) => (
                    <p key={`by-limit-${i}`} className="bazi-evidence-boundary">适用边界：{l}</p>
                  ))}
                </details>
              ) : null}
              {xiyong.relations.length > 0 && (
                <>
                  <h4>两体系点名对照</h4>
                  {xiyong.relations.map((item: any) => (
                    <p key={item.stem}>{relationLine(item)}</p>
                  ))}
                  {xiyong.relations.map((item: any) => item.not_judgeable_line ? (
                    <p key={`nj-${item.stem}`} className="bazi-xiyong-not-judgeable">{item.not_judgeable_line}</p>
                  ) : null)}
                  <p className="bazi-xiyong-closing">{xiyong.relations_closing_line}</p>
                </>
              )}
            </section>
          )}

          {dayun && (
            <section className="bazi-dayun-presentation" aria-label="大运方向与交运区间">
              <span className="eyebrow">大运时间轴 · 两口径分立呈现</span>
              <h3>大运方向与交运区间，按哪种口径数？</h3>
              <div className="bazi-dayun-switch" role="tablist" aria-label="大运口径切换">
                {(["sanming", "shenfeng"] as const).map((method) => (
                  <button
                    key={method}
                    type="button"
                    role="tab"
                    aria-selected={dayunMethod === method}
                    className={dayunMethod === method ? "active" : ""}
                    onClick={() => setDayunMethod(method)}
                  >
                    {dayunMethodLabels[method]}
                  </button>
                ))}
              </div>
              {(() => {
                const view = dayun.methods[dayunMethod];
                const pillars = view.natal.pillars;
                return (
                  <div className="bazi-dayun-method">
                    <p>
                      四柱 {pillars.year} · {pillars.month} · {pillars.day} · {pillars.hour}，日主 {pillars.day_master}；
                      大运方向：{view.direction.label}（{view.direction.counting_target === "future_jie" ? "数至出生后之节" : "数至出生前之节"}：{view.direction.counted_jie.name} {view.direction.counted_jie.at}）。
                    </p>
                    {view.status === "unresolved" ? (
                      <p className="bazi-dayun-not-judgeable">
                        交运时间暂不可判：{dayunReasonLabels[view.reason] || view.reason}。
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
                        <ol className="bazi-dayun-entries">
                          {view.entries.map((entry: any) => (
                            <li key={entry.period_index}>
                              <strong>第 {entry.period_index} 运 {entry.ganzhi}</strong>
                              <span>（{entry.ten_god_relative_to_natal_day_stem}）</span>
                              {entry.state === "interval" && (
                                <span>交运区间：{entry.start_interval.earliest} 至 {entry.start_interval.latest}（不含上限）</span>
                              )}
                              {entry.state === "not_provided" && (
                                <span>交运区间未提供：本口径只呈现首运交运区间。</span>
                              )}
                              {entry.state === "unresolved" && (
                                <span>交运时间暂不可判。</span>
                              )}
                            </li>
                          ))}
                        </ol>
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
              })()}
              {dayun.scope.map((line: string, i: number) => (
                <p key={`ds-${i}`} className="bazi-dayun-scope">{line}</p>
              ))}
            </section>
          )}

          {/* TJ-031.4（Track B F3）：当前分析边界是结果四层结构的第 4 层，
              有结果即须在场，不再随 warnings/limitations 是否为空而消失；
              分界约定在此明示，不用技术字段名。 */}
          <section className="live-section result-limitations" aria-label="当前分析边界">
            <h3>当前分析边界</h3>
            {strengthPresentation && strengthPresentation.status === "presented" && (
              <p className="bazi-boundary-state">命盘结构：已有结论的仅限这一个已审形态；其余命盘形态暂不可判。</p>
            )}
            {strengthPresentation && strengthPresentation.status === "not_judgeable" && (
              <p className="bazi-boundary-state">命盘结构：暂不可判，不作任何强弱结论。</p>
            )}
            {strengthPresentation && strengthPresentation.status === "conflict" && (
              <p className="bazi-boundary-state">命盘结构：存在未裁定冲突，暂不可判；不作任何强弱结论。</p>
            )}
            {!strengthPresentation && strengthLoadError && (
              <p className="bazi-boundary-state">命盘结构：本次请求未能完成计算，这不是暂不可判。</p>
            )}
            {!strengthPresentation && !strengthLoadError && (
              <p className="bazi-boundary-state">命盘结构：本次结果未附带已审强弱形态事实。</p>
            )}
            {patternPresentation && patternPresentation.status === "presented" && (
              <p className="bazi-boundary-state">格局局部研究：已有结论的仅限任氏寅月这一个局部真格事实；其余格局暂不可判。</p>
            )}
            {patternPresentation && patternPresentation.status === "not_judgeable" && (
              <p className="bazi-boundary-state">格局局部研究：暂不可判，不作任何格局结论。</p>
            )}
            {patternPresentation && patternPresentation.status === "abstained" && (
              <p className="bazi-boundary-state">格局局部研究：本次不作呈现，不作任何格局结论。</p>
            )}
            {boundaryDomainWarnings.map((w: string, i: number) => (
              <p key={`w-${i}`} className="limitation-warning">⚠️ {w}</p>
            ))}
            {boundaryDomainLimitations.map((l: string, i: number) => (
              <p key={`l-${i}`} className="limitation-note">ℹ️ {l}</p>
            ))}
            <p className="limitation-note">
              分界约定：年柱以立春交节为界，立春之前出生仍按上一年计算；日柱以午夜 0 点为界，晚上 23 点后的夜子时归当日，不顺延到次日。
            </p>
            <p className="limitation-note">
              以上为传统文化观察，不构成科学验证的未来预测。旺衰与完整喜用神结论需充分裁定，当前暂不提供；
              大运仅呈现已注册方向与交运区间，不作吉凶判断。
            </p>
            {xiyong && (
              <>
                <p className="limitation-note">ℹ️ {xiyong.scope_statement}</p>
                {xiyong.limitations.map((l: string, i: number) => (
                  <p key={`xy-${i}`} className="limitation-note">ℹ️ {l}</p>
                ))}
              </>
            )}
            {dayun && dayun.limitations.map((l: string, i: number) => (
              <p key={`dy-${i}`} className="limitation-note">ℹ️ {l}</p>
            ))}
            {strengthPresentation && boundaryStrengthScope && (
              <>
                <p className="limitation-note">ℹ️ {boundaryStrengthScope}</p>
                {boundaryStrengthLimitations.map((l: string, i: number) => (
                  <p key={`st-${i}`} className="limitation-note">ℹ️ {l}</p>
                ))}
              </>
            )}
            {patternPresentation && boundaryPatternScope && (
              <>
                <p className="limitation-note">ℹ️ {boundaryPatternScope}</p>
                {boundaryPatternLimitations.map((l: string, i: number) => (
                  <p key={`pt-${i}`} className="limitation-note">ℹ️ {l}</p>
                ))}
              </>
            )}
          </section>

          <section className="bazi-audit-view" aria-label="专业审计视图">
            <details className="bazi-audit-details">
              <summary>专业审计视图</summary>
              <p className="bazi-audit-note">这里是完整的技术核查信息：规则命中、典籍依据与计算过程。平时不需要展开；展开后可见规则编号与原始记录。</p>
              <p className="bazi-audit-note">计算版本：{result.variant}</p>
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
                            <p>{item.quote}{item.excerpt ? "（节选）" : ""}</p>
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
              {xiyong && xiyong.blocks.tiaohou.evidence?.quote && (
                <article className="live-evidence">
                  <div><strong>《穷通宝鉴》调候条目原文</strong><span>证据等级 C</span></div>
                  <blockquote>{xiyong.blocks.tiaohou.evidence.quote}</blockquote>
                </article>
              )}
              {xiyong && (xiyong.blocks.bingyao.evidence?.quotes || []).map((q: any) => (
                <article className="live-evidence" key={q.pair_id}>
                  <div><strong>《神峰通考》病药原文</strong><span>证据等级 C</span></div>
                  <blockquote>{q.quote}</blockquote>
                </article>
              ))}
              {evidence.map((item) => (
                <article className="live-evidence" key={item.id}>
                  <div><strong>{item.title}</strong><span>{item.grade}</span></div>
                  <blockquote>{item.quote}{item.excerpt ? "（节选）" : ""}</blockquote>
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
            </details>
          </section>
        </section>
      )}
    </div>
  );
}
