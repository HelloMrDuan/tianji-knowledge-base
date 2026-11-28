import { useEffect, useRef, useState } from "react";
import type { FormEvent } from "react";
import { Icon } from "../shared/Icon";
import { Link } from "../shared/router";
import { executeBazi, executeBaziProfileScenario, executeTrueSolarComparison, type ExecuteResponse, type TrueSolarComparison } from "./api";
import { readSavedBirthProfile, saveBirthProfile, clearBirthProfile, getSavedBirthFingerprint, toApiValue, toApiZone, validateBirthInput, onBirthProfileCleared, type BirthProfile } from "./birthProfile";
import { clearAllLocalData, presentLocalDataLabels } from "./localData";
import { resetThemeDomToDefault } from "./theme";
import { BirthInputFields } from "./BirthInputFields";
import { DayunTimeline } from "./DayunTimeline";
import {
  computeDayunFingerprint,
  consumePendingDayunReturn,
  getDayunPresentation,
  getSelectedDayunMethod,
  getSelectedPeriodIndex,
  locateCurrentPeriod,
  setDayunPresentation,
  setSelectedDayunMethod,
  setSelectedPeriodIndex,
  subscribe as subscribeYearContext,
  type DayunPresentation,
} from "./yearContext";
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

// TJ-031.19 P0-1/P0-2：研究层转写只转写呈现对象字段，不生成任何
// 新判断。现代模型 verdict 是工程模型内部结论（强侧/弱侧/中间
// 分数带/弃判），不是古典旺衰定论。
const modernVerdictLabels: Record<string, string> = {
  strong: "强侧",
  weak: "弱侧",
  balanced: "中间分数带",
  abstain: "弃判",
};

const fuyiConfidenceLabels: Record<string, string> = {
  model_candidate: "模型候选",
};

const fuyiPillarLabels: Record<string, string> = {
  year: "年干",
  month: "月干",
  hour: "时干",
};

function formatSignedScore(score: number): string {
  // 与后端 "%+d" 一致：零分也带正号（+0），与分项符号读数对应。
  return `${score >= 0 ? "+" : ""}${score}`;
}

// TJ-031.19 P0-3：真太阳时对照只转写服务端返回的记录，不计算任何
// 时间换算。ISO 时刻只作显示整理（去毫秒），修正分钟保留一位小数。
function formatSolarTime(value: unknown): string {
  if (typeof value !== "string") return "—";
  return value.replace("T", " ").replace(/\.\d+/, "");
}

function formatMinutes(value: unknown): string {
  if (typeof value !== "number" || !Number.isFinite(value)) return "—";
  const rounded = Math.round(value * 10) / 10;
  return `${rounded > 0 ? "+" : ""}${rounded} 分钟`;
}

// TJ-031.19 P0-3：出生地时区选择。第一项“与出生资料同一时区”是
// 默认——出生资料的时区即出生地时区；其余为常见 IANA 时区，供出生
// 地与出生资料地区不一致时改选。服务端按 tzdb 解析校验区名，
// 前端不计算任何时区偏移。
const TRUE_SOLAR_TIMEZONES: Array<{ value: string; label: string }> = [
  { value: "", label: "与出生资料同一时区（默认）" },
  { value: "Asia/Shanghai", label: "Asia/Shanghai（北京时间）" },
  { value: "Asia/Urumqi", label: "Asia/Urumqi（乌鲁木齐）" },
  { value: "Asia/Hong_Kong", label: "Asia/Hong_Kong（香港）" },
  { value: "Asia/Taipei", label: "Asia/Taipei（台北）" },
  { value: "Asia/Tokyo", label: "Asia/Tokyo（东京）" },
  { value: "Asia/Seoul", label: "Asia/Seoul（首尔）" },
  { value: "Asia/Singapore", label: "Asia/Singapore（新加坡）" },
  { value: "Asia/Kuala_Lumpur", label: "Asia/Kuala_Lumpur（吉隆坡）" },
  { value: "Asia/Bangkok", label: "Asia/Bangkok（曼谷）" },
  { value: "Asia/Jakarta", label: "Asia/Jakarta（雅加达）" },
  { value: "Asia/Kolkata", label: "Asia/Kolkata（加尔各答）" },
  { value: "Asia/Dubai", label: "Asia/Dubai（迪拜）" },
  { value: "Europe/London", label: "Europe/London（伦敦）" },
  { value: "Europe/Paris", label: "Europe/Paris（巴黎）" },
  { value: "Europe/Berlin", label: "Europe/Berlin（柏林）" },
  { value: "Europe/Moscow", label: "Europe/Moscow（莫斯科）" },
  { value: "America/New_York", label: "America/New_York（纽约）" },
  { value: "America/Chicago", label: "America/Chicago（芝加哥）" },
  { value: "America/Denver", label: "America/Denver（丹佛）" },
  { value: "America/Los_Angeles", label: "America/Los_Angeles（洛杉矶）" },
  { value: "Australia/Sydney", label: "Australia/Sydney（悉尼）" },
  { value: "Pacific/Auckland", label: "Pacific/Auckland（奥克兰）" },
  { value: "UTC", label: "UTC（协调世界时）" },
];

// TJ-017.3 第二阶段：大运呈现的口径标签（只转写呈现对象字段，
// 不生成任何新判断；两口径分立呈现，永不合并）。暂不可判原因
// 转写随时间线组件移入 DayunTimeline.tsx。
const dayunMethodLabels: Record<string, string> = {
  sanming: "三命通会口径",
  shenfeng: "神峰通考口径",
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

// TJ-031.19 Lane A：五行分布只对已返回的四柱作确定性计数（天干、
// 地支、藏干的固定五行配属），与渲染藏干同属已返回数据的呈现，
// 前端不计算任何命理、不作旺衰/喜用/格局/吉凶判断。
const STEM_ELEMENTS: Record<string, string> = {
  甲: "木", 乙: "木", 丙: "火", 丁: "火", 戊: "土",
  己: "土", 庚: "金", 辛: "金", 壬: "水", 癸: "水",
};
const BRANCH_ELEMENTS: Record<string, string> = {
  寅: "木", 卯: "木", 巳: "火", 午: "火", 申: "金",
  酉: "金", 亥: "水", 子: "水", 辰: "土", 戌: "土",
  丑: "土", 未: "土",
};
const FIVE_ELEMENTS = ["木", "火", "土", "金", "水"];

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

export function BaziProfilePage({
  onClearAllThemeReset,
}: {
  /** TJ-029.2: 全部清除时把主题 React 状态静默回默认（不写回存储）。 */
  onClearAllThemeReset?: () => void;
}) {
  const [profile, setProfile] = useState<BirthProfile>(() => readSavedBirthProfile());
  const [inputError, setInputError] = useState("");
  const [result, setResult] = useState<ExecuteResponse | null>(null);
  const [xiyong, setXiyong] = useState<any>(null);
  // TJ-017.3 第二阶段：传统大运口径为可选逐请求输入，缺省不选择；
  // 不写入出生资料档案、不进 URL。
  const [dayunRole, setDayunRole] = useState<"" | "male" | "female">("");
  const [dayun, setDayun] = useState<any>(null);
  const [dayunMethod, setDayunMethod] = useState<"sanming" | "shenfeng">(() => getSelectedDayunMethod());
  // TJ-0422 phase 2 slice A: session-shared dayun state (yearContext).
  // storedDayun lets the yearly page's "back to my dayun" link land on
  // the timeline even though a fresh calculation has not run in this
  // mount; it is cleared whenever the birth input changes, so it can
  // never outlive the birth data it was computed from. Reads are
  // fingerprint-checked against the saved birth data (PR #594
  // re-review fix): a presentation computed from other birth data
  // reads back as null here.
  const [storedDayun, setStoredDayun] = useState<DayunPresentation | null>(() => getDayunPresentation(getSavedBirthFingerprint()));
  const [selectedPeriodIndex, setSelectedPeriodIndexState] = useState<number | null>(() => getSelectedPeriodIndex());
  // TJ-013.3 U1 Batch C：强度呈现取自同一场景信封；场景调用失败时
  // 只令强度节进入错误态，不以暂不可判掩盖（xiyong/dayun 的既有
  // 缺席行为不变）。
  const [strengthPresentation, setStrengthPresentation] = useState<any>(null);
  const [strengthLoadError, setStrengthLoadError] = useState(false);
// TJ-031.19 Lane A：详批呈现（profile_presentation）取自同一场景信封；
// 其中 strength 节的 research_reference 是现代强度模型研究列，
// fuyi_research 节的 research_reference 是扶抑现代层研究；两者
// 只作明确标注的研究参考，永不改写已审结论。
const [profilePresentation, setProfilePresentation] = useState<any>(null);
  // TJ-012.3 Stage B：格局局部呈现取自同一场景信封；场景调用失败时
  // 与强度节同一错误态（xiyong/dayun 的既有缺席行为不变）。
  const [patternPresentation, setPatternPresentation] = useState<any>(null);
  // TJ-031.19 P0-3：真太阳时对照是按需的研究入口——出生地经度与
  // 出生地时区由用户显式输入后才向服务端请求对照；默认排盘永不
  // 因此改变，对照结果只在本次结果区内呈现，不保存、不进 URL。
  const [trueSolarLongitude, setTrueSolarLongitude] = useState("");
  const [trueSolarTzName, setTrueSolarTzName] = useState("");
  const [trueSolarResult, setTrueSolarResult] = useState<TrueSolarComparison | null>(null);
  const [trueSolarLoading, setTrueSolarLoading] = useState(false);
  const [trueSolarError, setTrueSolarError] = useState("");
  const trueSolarRequestVersion = useRef(0);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  // TJ-029.2 P1: 统一清除全部本机资料（两步确认 + 回执）
  const [confirmClearAll, setConfirmClearAll] = useState(false);
  const [clearAllPreview, setClearAllPreview] = useState<string[]>([]);
  const [clearAllNote, setClearAllNote] = useState("");
  const requestVersion = useRef(0);

  useEffect(() => () => { requestVersion.current += 1; }, []);

  // TJ-0422 phase 2 slice A: stay in sync with session-shared dayun
  // state (timeline selection, method tab, stored presentation).
  useEffect(() => subscribeYearContext(() => {
    setStoredDayun(getDayunPresentation(getSavedBirthFingerprint()));
    setSelectedPeriodIndexState(getSelectedPeriodIndex());
    setDayunMethod(getSelectedDayunMethod());
  }), []);

  // TJ-0422 phase 2 slice A: a return from the yearly page's
  // "返回所属大运" link scrolls the timeline into view (one-shot).
  useEffect(() => {
    if (!consumePendingDayunReturn()) return;
    requestAnimationFrame(() => {
      document.querySelector(".bazi-dayun-presentation")?.scrollIntoView({ behavior: "instant", block: "start" });
    });
  }, []);

  // TJ-006.3: 其他标签页清除资料时，本页同步清空
  useEffect(() => onBirthProfileCleared(() => {
    invalidateResult();
    setProfile({ calendarType: "solar", year: 0, month: 0, day: 0, isLeapMonth: false, time: "", timeUnknown: false, region: "中国大陆" });
    setInputError("");
  }), []);

  function invalidateResult() {
    requestVersion.current += 1;
    trueSolarRequestVersion.current += 1;
    setResult(null);
    setXiyong(null);
    setDayun(null);
    setStrengthPresentation(null);
    setProfilePresentation(null);
    setPatternPresentation(null);
    setStrengthLoadError(false);
    setError("");
    setLoading(false);
    setTrueSolarResult(null);
    setTrueSolarLoading(false);
    setTrueSolarError("");
    // TJ-0422 phase 2 slice A: the birth input changed, so the
    // session-shared dayun presentation is stale and must not survive.
    setDayunPresentation(null, null);
    setSelectedPeriodIndex(null);
  }

  function startClearAll() {
    setClearAllPreview(presentLocalDataLabels());
    setConfirmClearAll(true);
    setClearAllNote("");
  }

  function doClearAll() {
    const cleared = clearAllLocalData();
    invalidateResult();
    setProfile({ calendarType: "solar", year: 0, month: 0, day: 0, isLeapMonth: false, time: "", timeUnknown: false, region: "中国大陆" });
    setInputError("");
    // 可见主题同步回默认；只改 DOM 不写回存储，否则默认主题会重建该键
    resetThemeDomToDefault();
    // 同步 React 主题状态，使切换按钮标签立即回到“夜景”；静默重置
    // 不触发持久化，否则默认主题会重新写入 localStorage
    onClearAllThemeReset?.();
    setConfirmClearAll(false);
    setClearAllNote(cleared.length > 0 ? `已清除本机全部资料：${cleared.join("、")}。` : "本机未保存任何天机资料，无需清除。");
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
    setProfilePresentation(null);
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
        setProfilePresentation(scenario.result?.profile_presentation ?? null);
        setPatternPresentation(scenario.result?.pattern_presentation ?? null);
        setStrengthLoadError(false);
        // TJ-0422 phase 2 slice A: share the full dayun presentation
        // with the yearly page for this session only (never persisted),
        // bound to the exact birth inputs it was computed from (PR #594
        // re-review fix: fingerprint-checked on read).
        setDayunPresentation(
          scenario.result?.dayun_presentation ?? null,
          scenario.result?.dayun_presentation
            ? computeDayunFingerprint(toApiValue(profile), toApiZone(profile))
            : null,
        );
        setSelectedPeriodIndex(null);
      } catch {
        if (version === requestVersion.current) { setXiyong(null); setDayun(null); setStrengthPresentation(null); setProfilePresentation(null); setPatternPresentation(null); setStrengthLoadError(true); setDayunPresentation(null, null); setSelectedPeriodIndex(null); }
      }
    } catch (err) {
      if (version === requestVersion.current)
        setError(err instanceof Error ? err.message : "八字计算失败，请检查后端服务。");
    } finally {
      if (version === requestVersion.current) setLoading(false);
    }
  }

  // TJ-031.19 P0-3：真太阳时对照的按需请求。经度与时区缺一不可：
  // 经度必须由用户显式输入（不从出生地区推断——地区不等于经度）；
  // 时区默认与出生资料同一时区，用户可改选出生地实际时区。请求
  // 失败只进入错误态，不伪造对照；对照结果只在本次结果区内呈现。
  async function submitTrueSolar(event: FormEvent) {
    event.preventDefault();
    const longitude = Number(trueSolarLongitude);
    if (trueSolarLongitude.trim() === "" || !Number.isFinite(longitude) || longitude < -180 || longitude > 180) {
      setTrueSolarError("请输入 -180 至 180 之间的出生地经度（东经为正，西经为负，如北京 116.4）。");
      return;
    }
    let birthValue: string;
    let tzName: string;
    try {
      birthValue = toApiValue(profile);
      tzName = trueSolarTzName || toApiZone(profile);
    } catch (err) {
      setTrueSolarError(err instanceof Error ? err.message : "出生资料不完整，无法计算对照。");
      return;
    }
    const version = ++trueSolarRequestVersion.current;
    setTrueSolarLoading(true);
    setTrueSolarError("");
    setTrueSolarResult(null);
    try {
      const comparison = await executeTrueSolarComparison({ value: birthValue, longitude_deg: longitude, tz_name: tzName });
      if (version !== trueSolarRequestVersion.current) return;
      setTrueSolarResult(comparison);
    } catch (err) {
      if (version === trueSolarRequestVersion.current)
        setTrueSolarError(err instanceof Error ? err.message : "真太阳时对照计算失败，请稍后重试。");
    } finally {
      if (version === trueSolarRequestVersion.current) setTrueSolarLoading(false);
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
  // TJ-031.19 P0-1/P0-2：详批呈现中的两块研究参考（只转写呈现对象
  // 字段，不生成任何新判断）。profile_presentation 未返回时两者
  // 均为 null，页面如实说明未附带，不伪造研究数据。
  const profileSection = (id: string) =>
    Array.isArray(profilePresentation?.sections)
      ? profilePresentation.sections.find((section: any) => section.id === id) ?? null
      : null;
  const modernStrengthSection = profileSection("strength");
  const modernStrength = modernStrengthSection?.research_reference ?? null;
  const fuyiResearchSection = profileSection("fuyi_research");
  const fuyiResearch = fuyiResearchSection?.research_reference ?? null;
  // 弃判/缺分显示：分数只认数字（typeof === "number"），null 与
  // undefined 一律按无分处理；真正的 0 分仍是数字，正常显示为 0，
  // 绝不把 null 转成 0，也绝不因 0 触发弃判分支。
  const modernStrengthHasScore =
    modernStrength !== null && typeof modernStrength.score === "number";
  const modernStrengthAbstainReason =
    modernStrength?.abstain_detail || modernStrength?.abstain_reason || null;
  const fuyiHasInputScore =
    fuyiResearch !== null && typeof fuyiResearch.input_score === "number";
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

  // TJ-0422 phase 2 slice A: the dayun section (method tabs + the
  // interactive timeline). Rendered from a fresh calculation, or —
  // when sessionOnly — from the session-shared presentation after a
  // return from the yearly page, before any new calculation here.
  // TJ-031.19 Lane A + 2026-11-28 Q3=A: the timeline itself already
  // renders all 8 sanming periods, method switching, period
  // selection, end-from-next-start, and per-period liunian links
  // (DayunTimeline, shared). The supplement below adds only what the
  // timeline does not carry: the selected period's branch hidden
  // stems, reused from the natal chart only when the dayun branch
  // matches a natal branch; otherwise honestly not listed. No age
  // interval is produced: the public dayun object carries no age
  // field and no start age is converted here.
  function renderDayunSection(presentation: DayunPresentation, sessionOnly: boolean) {
    const dayunEntries = [...(presentation.methods[dayunMethod]?.entries || [])].sort((a: any, b: any) => a.period_index - b.period_index);
    const dayunCurrent = locateCurrentPeriod(presentation, dayunMethod);
    const effectivePeriodIndex = selectedPeriodIndex
      ?? (dayunCurrent.status === "current" ? dayunCurrent.periodIndex : null)
      ?? (dayunCurrent.status === "ambiguous" ? dayunCurrent.toPeriodIndex : null)
      ?? dayunEntries[0]?.period_index
      ?? null;
    const effectiveEntry = dayunEntries.find((entry: any) => entry.period_index === effectivePeriodIndex) ?? null;
    const effectiveBranchHidden = (!sessionOnly && pillars.length === 4 && effectiveEntry)
      ? (() => {
          const match = pillars.find((item: any) => item.branch?.value === effectiveEntry.branch);
          const hidden = match?.branch?.hidden_stems || [];
          return hidden.length > 0 ? hidden.map((h: any) => h.stem).join("、") : null;
        })()
      : null;
    return (
      <section className="bazi-dayun-presentation" aria-label="大运方向与交运区间">
        <span className="eyebrow">大运时间轴 · 两口径分立呈现</span>
        <h3>大运方向与交运区间，按哪种口径数？</h3>
        {sessionOnly && (
          <p className="bazi-dayun-session-note">
            这是本次会话中保存的大运呈现（出生资料未变）。重新生成基础档案可刷新；修改出生资料后本呈现即失效。
          </p>
        )}
        <div className="bazi-dayun-switch" role="tablist" aria-label="大运口径切换">
          {(["sanming", "shenfeng"] as const).map((method) => (
            <button
              key={method}
              type="button"
              role="tab"
              aria-selected={dayunMethod === method}
              className={dayunMethod === method ? "active" : ""}
              onClick={() => setSelectedDayunMethod(method)}
            >
              {dayunMethodLabels[method]}
            </button>
          ))}
        </div>
        <DayunTimeline
          presentation={presentation}
          method={dayunMethod}
          selectedPeriodIndex={selectedPeriodIndex}
          onSelectPeriod={(periodIndex) => setSelectedPeriodIndex(periodIndex)}
        />
        {!sessionOnly && effectiveEntry && (
          <div className="bazi-dayun-supplement" aria-label={`第 ${effectiveEntry.period_index} 运补充`}>
            <p>
              第 {effectiveEntry.period_index} 运补充：地支 {effectiveEntry.branch}
              {effectiveBranchHidden
                ? `藏干 ${effectiveBranchHidden}（与原局同支的已核验藏干）。`
                : "藏干未包含在本次公开呈现内，暂不列出（藏干只取与原局同支的已核验数据）。"}
            </p>
            <p>年龄区间不呈现：公开大运对象不含年龄字段，不折算起运年龄。流年入口见上方时间线（进入流年页查看其中某年）。</p>
          </div>
        )}
        {(presentation.scope || []).map((line: string, i: number) => (
          <p key={`ds-${i}`} className="bazi-dayun-scope">{line}</p>
        ))}
      </section>
    );
  }

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
              <button type="button" className="sample-fill" onClick={startClearAll}>清除全部本机资料</button>
            </div>
          </div>

          {confirmClearAll && (
            <div className="bazi-clear-all-confirm" role="group" aria-label="确认清除全部本机资料">
              <p>{clearAllPreview.length > 0 ? `将清除本机保存的：${clearAllPreview.join("、")}。` : "本机未保存任何天机资料。"}</p>
              <p>此操作只影响本浏览器，不影响其他设备；清除后主题、收藏与音乐偏好恢复默认。</p>
              <div className="bazi-profile-actions">
                <button type="button" className="sample-fill" onClick={doClearAll}>确认清除</button>
                <button type="button" className="sample-fill" onClick={() => setConfirmClearAll(false)}>取消</button>
              </div>
            </div>
          )}
          {clearAllNote && <p className="bazi-clear-all-note" role="status">{clearAllNote}</p>}

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
            <span>计算成功后出生资料仅保存在本浏览器以便其他场景复用，可随时清除。真太阳时对照可在下方结果区按出生地经度计算（研究入口，不改变公开排盘）；晚子时变体尚未开放。</span>
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

          {/* TJ-031.19 P0-1 + 2026-11-28 Q1=C：研究列：现代强度模型，
              取自同一场景信封的 profile_presentation。只转写后端研究
              参考字段（模型结论、总分、分项贡献、计算依据、不确定性
              与适用边界），与已审结论分开呈现、互不覆盖；不改权重，
              不扩展任何古典裁定。分数是工程模型内部总分，不是百分位、
              不是概率、不是古典旺衰定论。研究参考未返回时如实说明
              未附带，不伪造分数。 */}
          <section className="bazi-detail-section bazi-research-column" aria-label="研究列：现代强度模型">
            <span className="eyebrow">命盘结构 · 研究列（与已审结论分开呈现）</span>
            <h3>研究列：现代强度模型</h3>
            <p>现代强度模型是独立的研究列，与已审结论分开呈现，互不覆盖；现代模型结论永不改写已审结论。</p>
            <p>模型分数是工程模型内部总分（总分域 [-35, 105]），不是百分位，不是概率，不是古典旺衰定论，不作科学预测。</p>
            <p>未校准条件：土日主与丁日主得地分只计余根、未校准；四库月得令分记 0 是缺失条件的暂定处理，不代表已证明月令无作用。</p>
            {modernStrength && modernStrength.verdict !== "abstain" && modernStrengthHasScore && (
              <>
                <p>模型：{modernStrength.model_id || "现代强度模型"}（研究模型，不是古典结论）。</p>
                <p>模型结论：{modernVerdictLabels[modernStrength.verdict] || modernStrength.verdict}（{modernStrength.verdict}），总分 {modernStrength.score} 分（总分域 [{modernStrength.score_range?.[0] ?? -35}, {modernStrength.score_range?.[1] ?? 105}]{modernStrength.score_band ? `，分数档位 ${modernStrength.score_band}` : ""}）。</p>
                {Array.isArray(modernStrength.components) && modernStrength.components.length > 0 && (
                  <div className="bazi-research-table" aria-label="现代强度模型分项贡献">
                    {modernStrength.components.map((component: any) => (
                      <div key={component.key} className="bazi-research-row">
                        <b>{component.label}</b>
                        <span>{formatSignedScore(component.score)} 分</span>
                        <span>{component.detail || ""}</span>
                      </div>
                    ))}
                  </div>
                )}
                <p>分项说明：得令、得地、得势（显干生扶）、得助（藏干生扶）、克泄耗；每项分数为该因素对模型结果的贡献。</p>
                {modernStrength.classification_status && (
                  <p>分类状态：{modernStrength.classification_status}{modernStrength.classification_status !== "definite" ? "；分数为研究性暂定分，不输出确定旺衰分类。" : "。"}{modernStrength.definite_classification ? `确定分类：${modernStrength.definite_classification}。` : ""}</p>
                )}
                {(modernStrength.uncertainty_lines || []).map((line: string, i: number) => (
                  <p key={`mu-${i}`} className="bazi-detail-undecided">{line}</p>
                ))}
                {(modernStrength.limitations || []).map((line: string, i: number) => (
                  <p key={`ml-${i}`} className="bazi-strength-scope">适用边界：{line}</p>
                ))}
                {modernStrengthSection?.basis && (
                  <p className="bazi-strength-scope">计算依据：{modernStrengthSection.basis}</p>
                )}
                {modernStrengthSection?.caliber && (
                  <p className="bazi-strength-scope">适用口径：{modernStrengthSection.caliber}</p>
                )}
              </>
            )}
            {modernStrength && modernStrength.verdict !== "abstain" && !modernStrengthHasScore && (
              <p>现代模型未给出分数，暂不呈现分数。</p>
            )}
            {modernStrength && modernStrength.verdict === "abstain" && (
              <>
                <p>现代模型弃判{modernStrengthAbstainReason ? `（${modernStrengthAbstainReason}）` : "（未注明原因）"}；不输出模型分数与分项。</p>
                {(modernStrength.uncertainty_lines || []).map((line: string, i: number) => (
                  <p key={`mu-${i}`} className="bazi-detail-undecided">{line}</p>
                ))}
                {(modernStrength.limitations || []).map((line: string, i: number) => (
                  <p key={`ml-${i}`} className="bazi-strength-scope">适用边界：{line}</p>
                ))}
              </>
            )}
            {!modernStrength && (
              <p className="bazi-detail-undecided">{profilePresentation ? "现代强度模型研究输出未附带，研究列暂不呈现。" : "本次结果未附带详批呈现，研究列暂不呈现。"}</p>
            )}
          </section>

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

          {/* TJ-031.19 Lane A：五行分布与日主（详批第 1 节）。只对已返
              回的四柱作确定性计数，不作任何旺衰/喜用/格局/吉凶判断；
              无四柱数据时不渲染本节。 */}
          {pillars.length === 4 && (() => {
            const stemCounts: Record<string, number> = { 木: 0, 火: 0, 土: 0, 金: 0, 水: 0 };
            const branchCounts: Record<string, number> = { 木: 0, 火: 0, 土: 0, 金: 0, 水: 0 };
            const hiddenCounts: Record<string, number> = { 木: 0, 火: 0, 土: 0, 金: 0, 水: 0 };
            pillars.forEach((item: any) => {
              const stemEl = STEM_ELEMENTS[item.stem?.value];
              if (stemEl) stemCounts[stemEl] += 1;
              const branchEl = BRANCH_ELEMENTS[item.branch?.value];
              if (branchEl) branchCounts[branchEl] += 1;
              (item.branch?.hidden_stems || []).forEach((hidden: any) => {
                const hiddenEl = STEM_ELEMENTS[hidden.stem];
                if (hiddenEl) hiddenCounts[hiddenEl] += 1;
              });
            });
            const dayElement = STEM_ELEMENTS[chart.day_master?.stem] || "";
            const sameStems = pillars
              .map((item: any) => item.stem?.value)
              .filter((stem: string) => STEM_ELEMENTS[stem] === dayElement);
            return (
              <section className="bazi-detail-section" aria-label="五行分布与日主">
                <span className="eyebrow">命盘结构 · 确定性计数</span>
                <h3>五行分布与日主</h3>
                <p>日主{chart.day_master?.stem || "—"}属{dayElement || "—"}；天干中与日主同五行的干有 {sameStems.length} 个{sameStems.length ? `（${sameStems.join("、")}）` : ""}。</p>
                <div className="bazi-five-elements">
                  {FIVE_ELEMENTS.map((element) => (
                    <div key={element}>
                      <b>{element}</b>
                      <span>天干 {stemCounts[element]} · 地支 {branchCounts[element]} · 藏干 {hiddenCounts[element]}</span>
                      <span>合计 {stemCounts[element] + branchCounts[element] + hiddenCounts[element]}</span>
                    </div>
                  ))}
                </div>
                <p className="bazi-strength-scope">以上只是确定性计数，不作旺衰、喜用、格局或吉凶判断。</p>
              </section>
            );
          })()}

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
              {/* TJ-031.19 P0-2：扶抑与统一喜用结论（详批第 4 节的已裁定
                  口径）。古典扶抑方向可建行数为 0 行是已裁定状态，不重
                  提、不补方向；统一喜用结论恒为暂不可判。现代扶抑候选
                  只在研究层（下方扶抑现代层研究节），不是古典结论，
                  不作公开判断。 */}
              <p>扶抑古典方向：十行方向表逐行核对后可建行数为 0 行（已裁定关闭），本节不给出任何扶抑古典方向结论。</p>
              <p>统一喜用结论：暂不可判（系统不据此给出统一的取用结论）。</p>
              <details className="bazi-research-note">
                <summary>研究参考：现代扶抑候选</summary>
                {fuyiResearch ? (
                  <p>现代扶抑层只给候选方向与候选干作研究参考，不是古典结论，不作公开判断；候选方向与候选干见下方“扶抑现代层研究”节。</p>
                ) : (
                  <p>现代扶抑层只给候选干作研究参考，不是古典结论，不作公开判断；本次结果未附带研究层候选，故这里不列候选干。</p>
                )}
              </details>
            </section>
          )}

          {/* TJ-031.19 P0-2 + 2026-11-28 Q2=C：扶抑现代层研究（研究）。
              取自同一场景信封的 profile_presentation，与公开的调候/
              病药节分开的独立研究节：当前模型强度方向、扶抑候选方向、
              候选干、候选形成理由，与已审的调候/病药结果并列呈现。
              候选不是确定用神；格局用神暂不可判，14 格就绪表不公开
              呈现；统一喜用结论暂不可判。研究参考未返回时如实说明
              未附带，不伪造候选。 */}
          <section className="bazi-detail-section bazi-research-column" aria-label="扶抑现代层研究">
            <span className="eyebrow">喜用 · 研究（与公开呈现分开）</span>
            <h3>扶抑现代层研究</h3>
            <p>调候体系（已审）：{xiyong ? (xiyong.blocks.tiaohou.state === "presented" ? "取用顺序见上节。" : "条目在审定文本中不存在，该组合调候暂不可判。") : "公开呈现未附带，暂不可判。"}</p>
            <p>病药体系（已审）：{xiyong ? `两对结构候选，去病效力未裁定${(xiyong.blocks.bingyao.pairs || []).filter((pair: any) => pair.status === "triggered").length > 0 ? `；已触发：${(xiyong.blocks.bingyao.pairs || []).filter((pair: any) => pair.status === "triggered").map((pair: any) => pair.pair_id).join("、")}` : ""}，见上节。` : "公开呈现未附带，暂不可判。"}</p>
            <p>扶抑古典层：十行方向表逐行核对后可建行数为 0 行（已裁定关闭），不给方向结论。</p>
            {fuyiResearch && (
              <>
                {fuyiResearch.input_verdict === "abstain" ? (
                  <p>当前模型强度方向：现代强度模型弃判，未给出模型分数；该结论只是工程模型输出，不是古典旺衰定论。</p>
                ) : fuyiResearch.input_verdict && !fuyiHasInputScore ? (
                  <p>当前模型强度方向：现代强度模型结论为 {modernVerdictLabels[fuyiResearch.input_verdict] || fuyiResearch.input_verdict}（{fuyiResearch.input_verdict}），未给出模型分数；该结论只是工程模型输出，不是古典旺衰定论。</p>
                ) : fuyiResearch.input_verdict ? (
                  <p>当前模型强度方向：现代强度模型结论为 {modernVerdictLabels[fuyiResearch.input_verdict] || fuyiResearch.input_verdict}（{fuyiResearch.input_verdict}，{fuyiResearch.input_score} 分）；该结论只是工程模型输出，不是古典旺衰定论。</p>
                ) : (
                  <p>当前模型强度方向：现代层未给模型强度方向。</p>
                )}
                {fuyiResearch.direction_cn ? (
                  <>
                    <p>扶抑候选方向：{fuyiResearch.direction_cn}（{fuyiResearch.direction}；研究模型候选，不是确定用神）。</p>
                    {Array.isArray(fuyiResearch.direction_elements) && fuyiResearch.direction_elements.length > 0 && (
                      <p>方向元素：{fuyiResearch.direction_elements.join("、")}；十神类：{(fuyiResearch.ten_god_classes || []).join("、") || "—"}。</p>
                    )}
                    {Array.isArray(fuyiResearch.candidate_stems) && fuyiResearch.candidate_stems.length > 0 ? (
                      <div className="bazi-research-table" aria-label="扶抑候选干">
                        {fuyiResearch.candidate_stems.map((candidate: any) => (
                          <div key={`${candidate.pillar}-${candidate.stem}`} className="bazi-research-row">
                            <b>{candidate.stem}</b>
                            <span>{fuyiPillarLabels[candidate.pillar] || candidate.pillar}</span>
                            <span>{candidate.ten_god || ""}{candidate.element ? ` · ${candidate.element}` : ""}</span>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <p>候选干：本盘显干中无方向元素之干，候选为空。</p>
                    )}
                    {Array.isArray(fuyiResearch.formation_reasons) && fuyiResearch.formation_reasons.length > 0 && (
                      <>
                        <p>候选形成理由（分项符号读数，不构成独立的方向结论）：</p>
                        {fuyiResearch.formation_reasons.map((reason: any, i: number) => (
                          <p key={`fr-${i}`}>{reason.note}</p>
                        ))}
                      </>
                    )}
                  </>
                ) : (
                  <p>扶抑候选方向：现代层未给方向（balanced 只是中间分数带，不是古典中和裁决）；候选干暂不呈现。</p>
                )}
                {fuyiResearch.confidence && (
                  <p>候选可信度：{fuyiConfidenceLabels[fuyiResearch.confidence] || fuyiResearch.confidence}。</p>
                )}
                {(fuyiResearch.uncertainty || []).map((line: string, i: number) => (
                  <p key={`fu-${i}`} className="bazi-detail-undecided">{typeof line === "string" ? line : JSON.stringify(line)}</p>
                ))}
                {fuyiResearch.reason && <p className="bazi-strength-scope">模型说明：{fuyiResearch.reason}</p>}
                {fuyiResearchSection?.basis && (
                  <p className="bazi-strength-scope">计算依据：{fuyiResearchSection.basis}</p>
                )}
                <p>候选不是确定用神：扶抑现代层只给候选方向与候选干，不作确定用神结论。</p>
              </>
            )}
            {!fuyiResearch && (
              <p className="bazi-detail-undecided">{profilePresentation ? "扶抑现代层研究输出未附带，候选方向与候选干暂不呈现。" : "本次结果未附带详批呈现，候选方向与候选干暂不呈现。"}</p>
            )}
            <p>三体系口径不同，并列呈现，不合并为统一结论；统一喜用结论暂不可判。</p>
            <p>格局用神：暂不可判；14 格就绪表不公开呈现，用神恒未审，不捏造用神。</p>
            <p className="bazi-strength-scope">研究参考：以下内容来自已批研究模型，不是古典结论，不作公开判断。</p>
          </section>

          {dayun && renderDayunSection(dayun, false)}

          {/* TJ-031.19 P0-3：真太阳时对照（研究，详批第 5 节）。按需的
              研究入口：出生地经度与出生地时区由用户显式输入后，服务端
              按 research_dual_time_chart / compare_pillars 计算对照；
              公开排盘口径不变，对照结果只在本次结果区内呈现，不替换
              公开排盘、不保存。请求失败只进入错误态，不伪造对照。 */}
          <section className="bazi-detail-section bazi-research-column" aria-label="真太阳时对照（研究）">
            <span className="eyebrow">命盘结构 · 研究（与公开排盘分开）</span>
            <h3>真太阳时对照（研究）</h3>
            <p>真太阳时排盘是研究入口，不是公开排盘口径；公开排盘口径不变（北京时间，午夜 0 点为日界）。本对照只比较、不替换公开排盘：年柱、月柱与节气由出生时刻本身决定，两种口径下永不改变；只有日柱、时柱按出生地真太阳时重读。</p>
            <form className="bazi-true-solar-form" onSubmit={submitTrueSolar}>
              <label htmlFor="bazi-true-solar-longitude">
                <span>出生地经度（东经为正，西经为负）</span>
                <input
                  id="bazi-true-solar-longitude"
                  type="number"
                  inputMode="decimal"
                  step="any"
                  placeholder="如 116.4"
                  value={trueSolarLongitude}
                  onChange={(e) => setTrueSolarLongitude(e.target.value)}
                  required
                />
              </label>
              <label htmlFor="bazi-true-solar-tz">
                <span>出生地时区</span>
                <select
                  id="bazi-true-solar-tz"
                  value={trueSolarTzName}
                  onChange={(e) => setTrueSolarTzName(e.target.value)}
                >
                  {TRUE_SOLAR_TIMEZONES.map((zone) => (
                    <option key={zone.value || "default"} value={zone.value}>{zone.label}</option>
                  ))}
                </select>
              </label>
              <button className="button primary" type="submit" disabled={trueSolarLoading}>
                {trueSolarLoading ? "正在计算对照…" : "计算真太阳时对照"}
              </button>
            </form>
            <p className="bazi-strength-scope">出生时刻取本次已生成的档案；经度不从出生地区推断，须按实际出生地填写。历史时区不猜测：时区按出生时刻由服务端 tzdb 解析校验。</p>
            {trueSolarError && <p className="question-error" role="alert">{trueSolarError}对照未完成，公开排盘不受影响。</p>}
            {trueSolarResult && (
              <div className="bazi-true-solar-result" aria-label="真太阳时对照结果">
                <p>标准时间（出生时刻）：{formatSolarTime(trueSolarResult.conversion.input_local_time)}；真太阳时（出生地地方太阳时）：{formatSolarTime(trueSolarResult.conversion.apparent_solar_time)}。</p>
                <p>总修正 {formatMinutes(trueSolarResult.conversion.total_correction_minutes)}（经度修正 {formatMinutes(trueSolarResult.conversion.longitude_correction_minutes)}，均时差 {formatMinutes(trueSolarResult.conversion.equation_of_time_minutes)}）；出生地经度 {trueSolarResult.conversion.longitude_deg}°，时区偏移 UTC{typeof trueSolarResult.conversion.tz_offset_hours === "number" && trueSolarResult.conversion.tz_offset_hours >= 0 ? "+" : ""}{trueSolarResult.conversion.tz_offset_hours}，标准子午线 {trueSolarResult.conversion.standard_meridian_deg}°{trueSolarResult.conversion.date_shifted ? `；地方太阳日期移动了 ${trueSolarResult.conversion.date_shift_days} 天。` : "；地方太阳日期未移动。"}</p>
                <p>{(() => {
                  const changed = trueSolarResult.pillar_comparison.pillars.filter((row: any) => row.changed).map((row: any) => pillarNames[row.name] || row.name);
                  return changed.length > 0 ? `与公开排盘相比，真太阳时排盘有变化的柱：${changed.join("、")}；其余柱相同。` : "与公开排盘相比，真太阳时排盘四柱相同。";
                })()}</p>
                <div className="bazi-research-table" aria-label="标准时间与真太阳时四柱对照">
                  {trueSolarResult.pillar_comparison.pillars.map((row: any) => (
                    <div key={row.name} className="bazi-research-row">
                      <b>{pillarNames[row.name] || row.name}</b>
                      <span>标准 {row.standard?.ganzhi || "—"}</span>
                      <span>真太阳时 {row.true_solar?.ganzhi || "—"}</span>
                      <span>{row.changed ? "有变化" : "相同"}</span>
                    </div>
                  ))}
                </div>
                {trueSolarResult.pillar_comparison.pillars.map((row: any) => (
                  <p key={`reason-${row.name}`}>{pillarNames[row.name] || row.name}：{row.reason}</p>
                ))}
                <p>日主：标准 {trueSolarResult.pillar_comparison.day_master.standard?.stem || "—"} → 真太阳时 {trueSolarResult.pillar_comparison.day_master.true_solar?.stem || "—"}{trueSolarResult.pillar_comparison.day_master.changed ? "（日主随日柱变化，十神已按新日主重算）" : "（未变）"}。</p>
                <p>月令归属：{trueSolarResult.pillar_comparison.month_attribution_settled ? "已确定" : "未定（月令归属未定）"}{trueSolarResult.jieqi?.within_precision_budget ? "；出生时刻在节气精度窗口内，月柱归属不作定论。" : "。"}</p>
                {trueSolarResult.tz_validation && (
                  <p className="bazi-strength-scope">时区校验：{trueSolarResult.tz_validation.status}{trueSolarResult.tz_validation.tzdb_version ? `（tzdb ${trueSolarResult.tz_validation.tzdb_version}）` : ""}。</p>
                )}
                {trueSolarResult.comparison_note && <p className="bazi-strength-scope">{trueSolarResult.comparison_note}</p>}
                <p className="bazi-strength-scope">本对照只作研究比较，不替换公开排盘；真太阳时排盘不作任何古典结论。</p>
              </div>
            )}
          </section>

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
            {/* TJ-031.19 Lane A：破格只认伤官见官一途，其余古典破格通道暂无。 */}
            <p className="bazi-boundary-state">格局破格：除伤官见官外，暂无其他已审古典破格通道；其余破格缺口只作登记，不作破格结论。</p>
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

      {/* TJ-0422 phase 2 slice A: return from the yearly page lands on
          the session-shared timeline before any new calculation here. */}
      {!result && storedDayun && renderDayunSection(storedDayun, true)}
    </div>
  );
}
