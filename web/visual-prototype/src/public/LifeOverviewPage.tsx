import { useEffect, useRef, useState } from "react";
import type { FormEvent } from "react";
import { Icon } from "../shared/Icon";
import { Link } from "../shared/router";
import { executeLifeScenario, executeBaziProfileScenario, type ScenarioExecuteResponse } from "./api";
import { readSavedTargetYear, saveTargetYear, isValidTargetYear, MIN_TARGET_YEAR, MAX_TARGET_YEAR } from "./targetYear";
import { readSavedBirthProfile, saveBirthProfile, clearBirthProfile } from "./birthProfile";
import { toApiValue, toApiZone, fromLegacy, toSolarDateString, isConvertedFromLunar, fromSolarEdit, withUpdatedTime } from "./birthProfile";
import "./life-overview.css";

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


type ReviewedExcerpt = { id: string; title: string; original: string; level: string; excerpt: boolean };

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
      excerpt: source.original_text_excerpt === true || source.classic_title_excerpt === true,
    }];
  });
}

const dayunMethodLabels: Record<string, string> = {
  sanming: "三命口径",
  shenfeng: "神峰口径",
};

// TJ-0422 phase 2 slice B: local structural types + transcription-only
// renderers for the three lifted presentations and the full 8-period
// dayun presentation. Field names are copied verbatim from the backend
// contract; api.ts is untouched. The frontend computes no divination:
// every string below is a backend field, a fixed label, or a count of
// backend-provided facts.
type SliceStrengthPresentation = {
  variant: string;
  status: "presented" | "not_judgeable" | "conflict";
  day_master: string;
  month_branch: string;
  scope_statement: string;
  limitations: string[];
  statement?: string;
  classification?: string;
  predicate_id?: string;
  phase1_rule_id?: string;
  phase2_step_id?: string;
  rule_registration?: string;
  conditions?: Record<string, unknown>;
  segment_gate?: { segment_stem?: string } | null;
  reason?: string;
  conflict_ids?: string[];
  blocker_reasons?: string[];
};

type SliceXiyongBlock = {
  system: string;
  source_label: string;
  state: string;
  lines: string[];
  evidence?: { quote?: string; quotes?: Array<{ quote: string }> };
};

type SliceXiyongRelation = {
  stem: string;
  kind: string;
  tiaohou?: { order: number } | null;
  bingyao?: { role: string; pair_id: string } | null;
  not_judgeable_line?: string | null;
};

type SliceXiyongPresentation = {
  variant: string;
  presentation_scope: string;
  day_master: string;
  month_branch: string;
  blocks: { tiaohou: SliceXiyongBlock; bingyao: SliceXiyongBlock };
  relations: SliceXiyongRelation[];
  relations_closing_line: string;
  unified_verdict: null;
  public_enabled: boolean;
  ai_enabled: boolean;
  scope_statement: string;
  limitations: string[];
};

type SlicePatternPresentation = {
  variant: string;
  title: string;
  status: "presented" | "not_judgeable" | "abstained";
  day_master: string;
  month_branch: string;
  scope_statement: string;
  limitations: string[];
  outcome?: string;
  statement?: string;
  pattern?: string;
  commander?: { stem: string; ten_god: string; visible_pillars: string[] } | null;
  school?: string;
  scope_month_branch?: string;
  reason?: string;
  decision_step?: string;
};

type SliceDayunEntry = {
  period_index: number;
  ganzhi: string;
  stem?: string;
  branch?: string;
  ten_god_relative_to_natal_day_stem: string;
  state: string;
  start_interval: { earliest: string; latest: string } | null;
  start_interval_status?: string;
};

type SliceDayunMethodView = {
  method: string;
  status: string;
  reason?: string;
  direction: {
    value: string;
    label: string;
    counting_target: string;
    counted_jie: { name: string; at: string };
  };
  entries: SliceDayunEntry[];
  notices: Array<{ code: string; text: string }>;
};

type SliceDayunPresentation = {
  variant: string;
  status: string;
  methods: { sanming: SliceDayunMethodView; shenfeng: SliceDayunMethodView };
  scope: string[];
  limitations: string[];
};

// 只转述后端谓词 id，不生成任何新判断；未知形态不崩溃。
const sliceStrengthPredicateLabels: Record<string, string> = {
  pure_support: "纯粹支持形态",
  pure_generating_support: "生扶支持形态",
  isolated_control: "孤立受制形态",
  commanding_visible_support: "司令显现支持形态",
  lu_visible_support: "禄位显现支持形态",
  changsheng_visible_support: "长生显现支持形态（司令甲段）",
  pure_support_metal: "纯粹支持形态",
  pure_generating_support_water: "生扶支持形态",
};

const sliceStrengthReasonLabels: Record<string, string> = {
  no_predicate_matched: "本盘未命中任何已审局部形态条件",
  out_of_scope: "本盘的日主与月份组合不在已审谓词范围内",
  insufficient_evidence: "本盘的谓词条件证据不足",
};

const slicePatternReasonLabels: Record<string, string> = {
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

const slicePatternPillarLabels: Record<string, string> = {
  year: "年干",
  month: "月干",
  hour: "时干",
};

const sliceRelationKindLabels: Record<string, string> = {
  support: "两体系同向",
  conflict: "两体系方向相反",
  pivot_overlap: "两体系同指所论之神",
  one_sided: "仅一方点名",
};

const sliceBingyaoRoleLabels: Record<string, string> = {
  subject: "病药所论之神",
  disease: "病药判为病之神",
  medicine: "病药判为药之神",
};

const sliceBingyaoPairOrdinals: Record<string, string> = {
  wealth_peer_officer: "第一对",
  foodwound_seal_wealth: "第二对",
};

function sliceRelationLine(item: SliceXiyongRelation): string {
  const parts: string[] = [];
  if (item.tiaohou) parts.push(`调候取用顺序第 ${item.tiaohou.order} 位`);
  if (item.bingyao) {
    parts.push(
      `${sliceBingyaoRoleLabels[item.bingyao.role] || "病药点名"}（${sliceBingyaoPairOrdinals[item.bingyao.pair_id] || ""}）`,
    );
  }
  return `干${item.stem}：${sliceRelationKindLabels[item.kind] || item.kind}。${parts.join("；")}。`;
}

function sliceRenderStrength(p: SliceStrengthPresentation | null | undefined) {
  if (!p) return null;
  if (p.status === "presented") {
    const conditionNames = p.conditions ? Object.keys(p.conditions) : [];
    return (
      <section className="slice-presentation" aria-label="命盘结构分析">
        <span className="eyebrow">命盘结构 · 仅限一个已审局部形态</span>
        <h3>命盘结构分析</h3>
        <p>日主{p.day_master}生于{p.month_branch}月，命中了一个已审的局部形态：{sliceStrengthPredicateLabels[p.predicate_id || ""] || "已审局部形态条件命中"}。</p>
        <p>限定形态：{p.classification === "strong" ? "强形态" : p.classification === "weak" ? "弱形态" : "—"}</p>
        <p>规则来源：{p.rule_registration === "registered" ? "已通过审核的局部形态条件" : "尚在审核登记中的局部形态条件"}</p>
        {p.segment_gate && (
          <p>出生时刻已对照本月已核验的时段核查通过：{p.segment_gate.segment_stem}段。</p>
        )}
        <p>该结论只覆盖这一个已审形态，不覆盖全盘。</p>
        <p className="slice-scope">{p.scope_statement}</p>
        {p.limitations.map((l, i) => (
          <p key={`sl-${i}`} className="slice-scope">{l}</p>
        ))}
        {conditionNames.length > 0 && (
          <details className="slice-evidence-entry">
            <summary>查看计算依据（已审条件）</summary>
            <p>本次命中核对了以下已审条件：{conditionNames.join("、")}。条件本身来自后端已审谓词的执行记录，前端不另作判断。</p>
          </details>
        )}
      </section>
    );
  }
  if (p.status === "not_judgeable") {
    return (
      <section className="slice-presentation" aria-label="命盘结构分析·暂不可判">
        <span className="eyebrow">命盘结构 · 暂不可判</span>
        <h3>命盘结构分析</h3>
        <p>{sliceStrengthReasonLabels[p.reason || ""] || "本盘暂不可判"}；未命中不等于弱。</p>
        <p>暂不可判，不作任何强弱结论。</p>
        <p className="slice-scope">{p.scope_statement}</p>
        {p.limitations.map((l, i) => (
          <p key={`sl-${i}`} className="slice-scope">{l}</p>
        ))}
      </section>
    );
  }
  if (p.status === "conflict") {
    return (
      <section className="slice-presentation" aria-label="命盘结构分析·未裁定冲突">
        <span className="eyebrow">命盘结构 · 未裁定冲突</span>
        <h3>命盘结构分析</h3>
        <p>本盘存在未裁定的冲突，暂不可判；不作任何强弱结论。</p>
        {(p.blocker_reasons || []).map((reason, i) => (
          <p key={`cb-${i}`}>{reason}</p>
        ))}
        <p className="slice-scope">{p.scope_statement}</p>
        {p.limitations.map((l, i) => (
          <p key={`sl-${i}`} className="slice-scope">{l}</p>
        ))}
      </section>
    );
  }
  return null;
}

function sliceRenderXiyongBlock(block: SliceXiyongBlock, heading: string) {
  return (
    <div>
      <h4>{heading}（{block.source_label}）</h4>
      {block.lines.map((line, i) => (
        <p key={`${heading}-${i}`}>{line}</p>
      ))}
      {block.evidence?.quote && (
        <details className="slice-evidence-entry">
          <summary>查看判断依据：{block.source_label}</summary>
          <blockquote><p>{block.evidence.quote}</p></blockquote>
        </details>
      )}
      {block.evidence?.quotes?.length ? (
        <details className="slice-evidence-entry">
          <summary>查看判断依据：{block.source_label}</summary>
          {block.evidence.quotes.map((q, qi) => (
            <blockquote key={`q-${qi}`}><p>{q.quote}</p></blockquote>
          ))}
        </details>
      ) : null}
    </div>
  );
}

function sliceRenderXiyong(x: SliceXiyongPresentation | null | undefined) {
  if (!x) return null;
  return (
    <section className="slice-presentation" aria-label="调候与病药取用依据">
      <span className="eyebrow">已注册取用依据 · 两体系并列呈现</span>
      <h3>调候与病药：原文依据怎么说？</h3>
      {sliceRenderXiyongBlock(x.blocks.tiaohou, "调候")}
      {sliceRenderXiyongBlock(x.blocks.bingyao, "病药")}
      {x.relations.length > 0 && (
        <>
          <h4>两体系点名对照</h4>
          {x.relations.map((item) => (
            <p key={item.stem}>{sliceRelationLine(item)}</p>
          ))}
          {x.relations.map((item) => item.not_judgeable_line ? (
            <p key={`nj-${item.stem}`}>{item.not_judgeable_line}</p>
          ) : null)}
          <p>{x.relations_closing_line}</p>
        </>
      )}
      <p><strong>统一裁决：弃判。</strong>两体系并列呈现，不作统一裁决；扶抑、格局用神等其他取用判断尚未建成，暂不可判。</p>
      <p className="slice-scope">{x.scope_statement}</p>
      {x.limitations.map((l, i) => (
        <p key={`xl-${i}`} className="slice-scope">{l}</p>
      ))}
    </section>
  );
}

function sliceRenderPattern(p: SlicePatternPresentation | null | undefined) {
  if (!p) return null;
  const scopeAndLimits = (
    <>
      <p className="slice-scope">{p.scope_statement}</p>
      {p.limitations.map((l, i) => (
        <p key={`pl-${i}`} className="slice-scope">{l}</p>
      ))}
    </>
  );
  if (p.status === "presented" && p.outcome === "true_pattern") {
    return (
      <section className="slice-presentation" aria-label="命盘结构分析·格局局部研究">
        <span className="eyebrow">命盘结构 · 任氏寅月局部真格研究结果</span>
        <h4>任氏寅月局部真格研究结果</h4>
        <p>日主{p.day_master}生于寅月，{p.statement}</p>
        <p>格名：{p.pattern}</p>
        {p.commander && (
          <p>司令{p.commander.stem}（{p.commander.ten_god}）透于{(p.commander.visible_pillars || []).map((pillar) => slicePatternPillarLabels[pillar] || pillar).join("、")}。</p>
        )}
        {p.school && <p>流派：{p.school}</p>}
        {p.scope_month_branch && <p>适用月份：{p.scope_month_branch}</p>}
        <p>该结论只覆盖这一个已审局部事实，不覆盖全盘格局。</p>
        {scopeAndLimits}
      </section>
    );
  }
  if (p.status === "presented") {
    return (
      <section className="slice-presentation" aria-label="命盘结构分析·格局局部研究">
        <span className="eyebrow">命盘结构 · 任氏寅月局部真格研究结果</span>
        <h4>任氏寅月局部真格研究结果</h4>
        <p>日主{p.day_master}生于寅月，{p.statement}</p>
        <p>该结论只覆盖这一个已审局部事实，不覆盖全盘格局。</p>
        {scopeAndLimits}
      </section>
    );
  }
  if (p.status === "not_judgeable") {
    return (
      <section className="slice-presentation" aria-label="命盘结构分析·格局局部研究·暂不可判">
        <span className="eyebrow">命盘结构 · 任氏寅月局部真格研究结果</span>
        <h4>任氏寅月局部真格研究结果</h4>
        <p>{slicePatternReasonLabels[p.reason || ""] || "本盘暂不可判"}；暂不可判，不作任何格局结论。</p>
        {scopeAndLimits}
      </section>
    );
  }
  if (p.status === "abstained") {
    return (
      <section className="slice-presentation" aria-label="命盘结构分析·格局局部研究·不作呈现">
        <span className="eyebrow">命盘结构 · 任氏寅月局部真格研究结果</span>
        <h4>任氏寅月局部真格研究结果</h4>
        <p>{slicePatternReasonLabels[p.reason || ""] || "本次不作呈现"}；不作任何格局结论。</p>
        {scopeAndLimits}
      </section>
    );
  }
  return null;
}

// 按交运区间包含关系确定当前所处大运。区间端点一律取自后端
// start_interval 的 earliest/latest（左闭右开，与八字页口径一致）。
// 今日落在某运交运区间内时，交运是否已发生暂不可判，显式写
// “可能处于交运前后”，不强行定归属。
type SliceCurrentDayun =
  | { kind: "current"; entry: SliceDayunEntry; next: SliceDayunEntry | null }
  | { kind: "ambiguous"; previous: SliceDayunEntry | null; next: SliceDayunEntry }
  | { kind: "not_started"; first: SliceDayunEntry }
  | { kind: "unknown_beyond_first"; entry: SliceDayunEntry };

function sliceResolveCurrentDayun(entries: SliceDayunEntry[], nowMs: number): SliceCurrentDayun | null {
  const withIntervals = entries.filter((e) => e.state === "interval" && e.start_interval);
  if (!withIntervals.length) return null;
  for (const entry of withIntervals) {
    const start = Date.parse(entry.start_interval!.earliest);
    const end = Date.parse(entry.start_interval!.latest);
    if (Number.isFinite(start) && Number.isFinite(end) && nowMs >= start && nowMs < end) {
      const previous = withIntervals.filter((x) => x.period_index < entry.period_index).pop() ?? null;
      return { kind: "ambiguous", previous, next: entry };
    }
  }
  const started = withIntervals.filter((e) => Date.parse(e.start_interval!.latest) <= nowMs);
  if (!started.length) return { kind: "not_started", first: withIntervals[0] };
  const current = started[started.length - 1];
  const hasLaterWithoutInterval = entries.some(
    (e) => e.period_index > current.period_index && e.state !== "interval",
  );
  if (hasLaterWithoutInterval) return { kind: "unknown_beyond_first", entry: current };
  const next = withIntervals.find((e) => e.period_index === current.period_index + 1) ?? null;
  return { kind: "current", entry: current, next };
}

function sliceRenderFullDayun(props: {
  fullDayun: SliceDayunPresentation | null;
  fullDayunError: boolean;
  fullDayunLoading: boolean;
  roleSelected: boolean;
  method: "sanming" | "shenfeng";
  onMethodChange: (method: "sanming" | "shenfeng") => void;
  onLoad: () => void;
  groupForTenGod?: (tenGod: string) => string | null;
}) {
  const { fullDayun, fullDayunError, fullDayunLoading, roleSelected, method, onMethodChange, onLoad, groupForTenGod } = props;
  if (!roleSelected) {
    return (
      <p className="slice-dayun-prompt">
        未选择传统大运口径，因此不呈现大运。本页不默认、不推断口径：如需查看当前大运与完整时间线，
        请在上方选择传统大运口径后重新计算，再点下面的按钮加载。
      </p>
    );
  }
  if (!fullDayun && !fullDayunError) {
    return (
      <div>
        <p>完整 8 运时间线取自八字命理场景（bazi-profile）对同一出生资料的另一次真实请求，与本页场景的首运呈现口径相同，不合并、不改写；只在你点下面的按钮时才请求一次。</p>
        <button type="button" className="button primary slice-dayun-load" onClick={onLoad} disabled={fullDayunLoading}>
          {fullDayunLoading ? "正在加载完整大运…" : "查看完整 8 运时间线"}
        </button>
      </div>
    );
  }
  if (fullDayunError || !fullDayun) {
    return (
      <p className="slice-dayun-error" role="alert">完整大运呈现加载失败，请稍后重试。这不是暂不可判：本次请求未能完成计算。</p>
    );
  }
  const view = fullDayun.methods[method];
  const resolved = sliceResolveCurrentDayun(view.entries, Date.now());
  const currentIndex = resolved?.kind === "current" ? resolved.entry.period_index : null;
  return (
    <div>
      <p className="slice-dayun-source">完整 8 运时间线取自八字命理场景（bazi-profile）同一出生资料的真实请求；与本页场景的首运呈现口径相同，不合并、不改写。交运时间只给区间，不折算起运岁数或单点日期。</p>
      <div className="slice-dayun-switch" role="tablist" aria-label="大运口径切换">
        {(["sanming", "shenfeng"] as const).map((m) => (
          <button
            key={m}
            type="button"
            role="tab"
            aria-selected={method === m}
            className={method === m ? "active" : ""}
            onClick={() => onMethodChange(m)}
          >
            {dayunMethodLabels[m]}
          </button>
        ))}
      </div>
      {view.status === "unresolved" ? (
        <p>交运时间暂不可判：{view.reason || "本口径未能换算交运区间"}。不以近似值填充。</p>
      ) : (
        <>
          <p>
            大运方向：{view.direction.label}（{view.direction.counting_target === "future_jie" ? "数至出生后之节" : "数至出生前之节"}：{view.direction.counted_jie.name} {view.direction.counted_jie.at}）。
          </p>
          <div className="slice-dayun-current" aria-label="当前大运">
            <h4>当前大运</h4>
            {resolved?.kind === "current" && (
              <>
                <p>
                  <strong>第 {resolved.entry.period_index} 运 {resolved.entry.ganzhi}</strong>
                  <span>（{resolved.entry.ten_god_relative_to_natal_day_stem}）</span>
                </p>
                <p>交运区间：{resolved.entry.start_interval!.earliest} 至 {resolved.entry.start_interval!.latest}（不含上限）</p>
                {resolved.next && (
                  <p>下一运：第 {resolved.next.period_index} 运 {resolved.next.ganzhi}（{resolved.next.ten_god_relative_to_natal_day_stem}），交运区间：{resolved.next.start_interval!.earliest} 至 {resolved.next.start_interval!.latest}（不含上限）</p>
                )}
                {groupForTenGod && groupForTenGod(resolved.entry.ten_god_relative_to_natal_day_stem) && (
                  <p>该运十神在原局中的位置见第一层{groupForTenGod(resolved.entry.ten_god_relative_to_natal_day_stem)}组；这里只并列两组已算事实，不作大运与原局的相互作用判断。</p>
                )}
              </>
            )}
            {resolved?.kind === "ambiguous" && (
              <>
                <p><strong>可能处于交运前后。</strong>今日落在第 {resolved.next.period_index} 运 {resolved.next.ganzhi} 的交运区间内，交运是否已经发生暂不可判，不强行定归属。</p>
                {resolved.previous && (
                  <p>上一运：第 {resolved.previous.period_index} 运 {resolved.previous.ganzhi}（{resolved.previous.ten_god_relative_to_natal_day_stem}）。</p>
                )}
                <p>下一运：第 {resolved.next.period_index} 运 {resolved.next.ganzhi}（{resolved.next.ten_god_relative_to_natal_day_stem}），交运区间：{resolved.next.start_interval!.earliest} 至 {resolved.next.start_interval!.latest}（不含上限）。</p>
              </>
            )}
            {resolved?.kind === "not_started" && (
              <p>尚未进入第 1 运：第 1 运 {resolved.first.ganzhi}（{resolved.first.ten_god_relative_to_natal_day_stem}），交运区间：{resolved.first.start_interval!.earliest} 至 {resolved.first.start_interval!.latest}（不含上限）。</p>
            )}
            {resolved?.kind === "unknown_beyond_first" && (
              <p>已过首运交运区间，但本口径第 2–8 运区间未提供，无法确定当前所处大运。请切换到三命口径查看完整时间线。</p>
            )}
            {resolved === null && (
              <p>本口径未提供可用于确定当前大运的交运区间，当前大运暂不可判。</p>
            )}
          </div>
          <ol className="slice-dayun-entries">
            {view.entries.map((entry) => (
              <li key={entry.period_index} className={entry.period_index === currentIndex ? "slice-dayun-now" : ""}>
                <strong>第 {entry.period_index} 运 {entry.ganzhi}</strong>
                <span>（{entry.ten_god_relative_to_natal_day_stem}）</span>
                {entry.period_index === currentIndex && <em>当前</em>}
                {entry.state === "interval" && entry.start_interval && (
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
          {view.notices.map((notice) => (
            <p key={notice.code} className="slice-dayun-notice">{notice.text}</p>
          ))}
          <details className="slice-evidence-entry">
            <summary>查看大运呈现的范围与限制</summary>
            {fullDayun.scope.map((line, i) => (
              <p key={`ds-${i}`}>{line}</p>
            ))}
            {fullDayun.limitations.map((line, i) => (
              <p key={`dl-${i}`}>{line}</p>
            ))}
          </details>
        </>
      )}
    </div>
  );
}


export function LifeOverviewPage() {
  const initial = readSavedBirthProfile();
  const [date, setDate] = useState(() => toSolarDateString(initial));
  const [time, setTime] = useState(initial.time);
  const [targetYear, setTargetYear] = useState(readSavedTargetYear);
  const [result, setResult] = useState<ScenarioExecuteResponse | null>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  // T-D1 (E0409): optional traditional dayun role, same precedent as
  // bazi-profile; the role is sent only when explicitly selected.
  const [dayunRole, setDayunRole] = useState<"" | "male" | "female">("");
  const [dayun, setDayun] = useState<any>(null);
  const [dayunMethod, setDayunMethod] = useState<"sanming" | "shenfeng">("sanming");
  // TJ-0422 phase 2 slice B: five in-page screens (not five routes);
  // the full 8-period timeline is a lazy, single bazi-profile call
  // (same reason as the career page: the T-D1 capture reads the last
  // scenario response, which must stay the life envelope).
  const [screen, setScreen] = useState<"overview" | "strength" | "dayun" | "career" | "romance">("overview");
  const [fullDayun, setFullDayun] = useState<SliceDayunPresentation | null>(null);
  const [fullDayunError, setFullDayunError] = useState(false);
  const [fullDayunLoading, setFullDayunLoading] = useState(false);
  const [submittedBirth, setSubmittedBirth] = useState<{ value: string; zone?: string } | null>(null);
  const requestVersion = useRef(0);

  useEffect(() => () => { requestVersion.current += 1; }, []);

  function invalidateResult() {
    requestVersion.current += 1;
    setResult(null);
    setDayun(null);
    setFullDayun(null);
    setFullDayunError(false);
    setFullDayunLoading(false);
    setSubmittedBirth(null);
    setError("");
    setLoading(false);
  }

  function fillSample() {
    setDate("2000-01-07");
    setTime("12:00");
    invalidateResult();
  }

  async function runCalculation(yearOverride?: number) {
    const year = yearOverride ?? targetYear;
    const version = ++requestVersion.current;
    setLoading(true);
    setError("");
    setResult(null);
    setDayun(null);
    setFullDayun(null);
    setFullDayunError(false);
    setSubmittedBirth(null);
    try {
      if (!isValidTargetYear(year)) throw new Error("请选择 1901 至 2098 年的公历年份");
      // T-D1: traditional_role is an optional scenario input; the
      // typed executor signature does not list it yet, so the input
      // is built as a wider variable (assignable to the narrower
      // parameter type) and the key is only present when explicitly
      // selected. No api.ts change in this slice.
      const birthValue = (() => {
        const currentProfile = readSavedBirthProfile();
        const initialSolar = toSolarDateString(currentProfile);
        // 如果用户未修改日期，使用原始档案（含农历信息）；否则按阳历编辑处理
        if (date === initialSolar && time === currentProfile.time) {
          return toApiValue(currentProfile);
        }
        if (date === initialSolar) {
          return toApiValue(withUpdatedTime(currentProfile, time));
        }
        return toApiValue(fromSolarEdit(date, time, currentProfile.region, currentProfile));
      })();
      const lifeInput: {
        birth_value: string;
        birth_zone?: string;
        target_year: number;
        traditional_role?: "male" | "female";
      } = {
        birth_value: birthValue,
        target_year: year,
        birth_zone: toApiZone(readSavedBirthProfile()),
      };
      if (dayunRole) lifeInput.traditional_role = dayunRole;
      const next = await executeLifeScenario(lifeInput);
      if (version !== requestVersion.current) return;
      setDayun(next.result?.dayun_presentation ?? null);
      setSubmittedBirth({ value: birthValue, zone: toApiZone(readSavedBirthProfile()) });
      (() => {
        const currentProfile = readSavedBirthProfile();
        const initialSolar = toSolarDateString(currentProfile);
        if (date === initialSolar && time === currentProfile.time) {
          return; // 未修改，不覆写
        }
        if (date === initialSolar) {
          saveBirthProfile(withUpdatedTime(currentProfile, time));
          return;
        }
        saveBirthProfile(fromSolarEdit(date, time, currentProfile.region, currentProfile));
      })();
      saveTargetYear(year);
      setTargetYear(year);
      setResult(next);
    } catch (err) {
      if (version === requestVersion.current)
        setError(err instanceof Error ? err.message : "人生总览生成失败。");
    } finally {
      if (version === requestVersion.current) setLoading(false);
    }
  }

  async function submit(event: FormEvent) {
    event.preventDefault();
    await runCalculation();
  }

  // TJ-0422 phase 2 slice B: fetch the full 8-period dayun presentation
  // once, from bazi-profile with the same birth input and the same
  // explicitly selected role (same endpoint as the bazi-profile page).
  async function loadFullDayun() {
    if (!submittedBirth || !dayunRole || fullDayunLoading || fullDayun) return;
    const version = requestVersion.current;
    setFullDayunLoading(true);
    setFullDayunError(false);
    try {
      const profile = await executeBaziProfileScenario({
        value: submittedBirth.value,
        zone: submittedBirth.zone,
        strength_variant: "ditiansui-root-visibility-v1",
        traditional_role: dayunRole,
      });
      if (version !== requestVersion.current) return;
      setFullDayun((profile.result?.dayun_presentation ?? null) as SliceDayunPresentation | null);
    } catch {
      if (version === requestVersion.current) {
        setFullDayun(null);
        setFullDayunError(true);
      }
    } finally {
      if (version === requestVersion.current) setFullDayunLoading(false);
    }
  }

  const payload = result?.result || {};
  const profile = payload.profile || {};
  const strengthContext = profile.strength_context || null;
  const integrated = payload.integrated_reading || null;
  const provenance = payload.integration_provenance || null;
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
  // TJ-0422 phase 2 slice B: read the three lifted presentations from
  // the top level only. The nested career copy is projection-rewritten
  // (rule_id aliased, evidence dropped) and is never read for these.
  const strengthPresentation = (payload.strength_presentation ?? null) as SliceStrengthPresentation | null;
  const xiyongPresentation = (payload.xiyong_presentation ?? null) as SliceXiyongPresentation | null;
  const patternPresentation = (payload.pattern_presentation ?? null) as SlicePatternPresentation | null;
  // 天干五行分布只统计四柱天干自带的五行字段（后端原字段），地支五
  // 行不在本呈现内；只作位置统计，不据此判断旺衰。
  const stemElementCounts = pillars.reduce((acc: Record<string, number>, item: any) => {
    const element = item?.stem?.element;
    if (typeof element === "string" && element) acc[element] = (acc[element] || 0) + 1;
    return acc;
  }, {});
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

      <section className="life-entry" id="life-entry">
        <form onSubmit={submit}>
          <div className="life-entry-head">
            <div>
              <span className="eyebrow">只填一次</span>
              <h2>建立你的个人总览</h2>
            </div>
            <button type="button" className="sample-fill" onClick={fillSample}>填入示例</button>
            <button type="button" className="sample-fill" onClick={() => { invalidateResult(); clearBirthProfile(); setDate(""); setTime(""); }}>清除本机资料</button>
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

          {/* T-D1 (E0409): optional traditional dayun role, same
              precedent as bazi-profile; not selected means no dayun. */}
          <div className="bazi-dayun-role">
            <label htmlFor="life-dayun-role">传统大运口径（可选）</label>
            <select
              id="life-dayun-role"
              value={dayunRole}
              onChange={(e) => { invalidateResult(); setDayunRole(e.target.value as "" | "male" | "female"); }}
            >
              <option value="">不启用</option>
              <option value="male">传统男命口径</option>
              <option value="female">传统女命口径</option>
            </select>
            <small>只用于按传统口径呈现大运首运方向与交运区间；不选择时不呈现大运。该选择只随本次计算发送，不保存。</small>
          </div>

          <div className="life-entry-note">
            <Icon name="shield" size={16} />
            <span>出生资料只保存在当前浏览器本地用于下次预填；当前计算固定使用北京时间 UTC+8。</span>
          </div>
          <p className="life-entry-precision">出生时间须精确到分钟；缺少出生时间或地区未确认时，计算条件不足，相关呈现会标注暂不可判，不以近似值填充。</p>

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

          <nav className="slice-life-nav" role="tablist" aria-label="总览分屏">
            {([["overview", "① 命盘概况"], ["strength", "② 旺衰与喜用"], ["dayun", "③ 大运流年"], ["career", "④ 事业财运"], ["romance", "⑤ 桃花姻缘"]] as const).map(([id, label]) => (
              <button
                key={id}
                type="button"
                role="tab"
                aria-selected={screen === id}
                className={screen === id ? "active" : ""}
                onClick={() => setScreen(id)}
              >
                {label}
              </button>
            ))}
          </nav>
          <div className="slice-year-stepper" aria-label="切换观察年份">
            <button type="button" onClick={() => runCalculation(targetYear - 1)} disabled={loading || !isValidTargetYear(targetYear - 1)}>← {targetYear - 1} 年</button>
            <strong>{targetYear} 年</strong>
            <button type="button" onClick={() => runCalculation(targetYear + 1)} disabled={loading || !isValidTargetYear(targetYear + 1)}>{targetYear + 1} 年 →</button>
            <small>点不同年份即时重新请求并更新；各屏同步更新。</small>
            <a className="slice-edit-birth" href="#life-entry">修改出生资料</a>
          </div>

          {screen === "overview" && (
            <section className="slice-life-screen" aria-label="命盘概况">
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
          <nav className="slice-hub-cards" aria-label="分析卡片">
            <Link href="/bazi-profile" onClick={() => saveTargetYear(targetYear)}>
              <strong>命盘基础</strong>
              <span>四柱、日主与天干五行分布</span>
            </Link>
            <Link href="/yearly-structure" onClick={() => saveTargetYear(targetYear)}>
              <strong>流年结构</strong>
              <span>{targetYear} 年干支与流年地支结构</span>
            </Link>
            <Link href="/romance-structure" onClick={() => saveTargetYear(targetYear)}>
              <strong>桃花结构</strong>
              <span>咸池与夫妻宫的已有事实</span>
            </Link>
            <Link href="/career-wealth-structure" onClick={() => saveTargetYear(targetYear)}>
              <strong>事业财运结构</strong>
              <span>十神结构、旺衰喜用与大运流年</span>
            </Link>
          </nav>
          <section className="life-section">
            <div className="result-section-heading">
              <div><h2>命盘基础</h2></div>
              <Link className="text-action" href="/bazi-profile" onClick={() => saveTargetYear(targetYear)}>展开八字档案 <Icon name="arrow" size={15} /></Link>
            </div>
            <p className="slice-birth-line">本次计算所用出生资料：{date} {time}。出生资料保存在本机，下次打开自动预填，不必重复输入。</p>
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
            <div className="slice-five-elements" aria-label="天干五行分布与阴阳">
              <h3>天干五行分布与阴阳</h3>
              <p>以下只统计四柱天干自带的五行与阴阳（后端四柱原字段），地支五行不在本呈现内，不据此判断旺衰。</p>
              <ul>
                {pillars.map((item: any) => (
                  <li key={item.name}>{pillarNames[item.name] || item.name}：{item.stem?.value} · {item.stem?.element || "—"} · {item.stem?.polarity || "—"}</li>
                ))}
              </ul>
              <p>五行计数（天干）：{Object.entries(stemElementCounts).map(([element, count]) => `${element}${count}`).join("、") || "—"}</p>
            </div>
          </section>          {integrated && strengthContext && (
            <section className="life-integrated-report" aria-label="旺衰因素与年度综合解读">
              <span className="eyebrow">有出处的综合观察 · 不推断吉凶</span>
              <h2>{integrated.headline}</h2>
              <div className="life-integrated-grid">
                <article><h3>命盘因素</h3><p>{integrated.foundation}</p><small>{strengthContext.boundary}</small></article>
                <article><h3>事业财运</h3><p>{integrated.career}</p></article>
                <article><h3>桃花与夫妻宫</h3><p>{integrated.romance}</p></article>
              </div>
              {integrated.cross_rule && <p className="life-cross-rule">
                <strong>跨规则一致性：</strong>{integrated.cross_rule}
              </p>}
              {provenance && (
                <section className="life-proof-overview" aria-label="四场景来源一致性核验">
                  <h3>四场景计算来源核验</h3>
                  <p>
                    {provenance.all_natal_charts_identical && provenance.all_target_years_identical
                      ? "出生盘与目标年份已跨场景核对一致。"
                      : "场景资料存在不一致，综合解释不可用。"}
                    {" "}这是同一套证据的交叉核查，不算新增独立印证。
                  </p>
                  <ul>
                    {(Array.isArray(provenance.evidence_contributions)
                      ? provenance.evidence_contributions : []).map((entry: any) => (
                      <li key={entry.scenario}>
                        <strong>{{ profile: "命盘基础", yearly: "年度结构",
                                   romance: "桃花结构", career: "事业财运" }[entry.scenario as "profile" | "yearly" | "romance" | "career"] || "来源场景"}</strong>
                        <span>引用 {Array.isArray(entry.evidence_ids) ? entry.evidence_ids.length : 0} 条已核验出处</span>
                      </li>
                    ))}
                  </ul>
                </section>
              )}
              <details>
                <summary>核查以上结论引用的古籍证据</summary>
                {reviewedExcerpts(integrated.evidence_ids, reviewedEvidence).map((item) => (
                  <blockquote key={item.id}><small>{item.title} · {item.level}</small><p>{item.original}{item.excerpt ? "（节选）" : ""}</p></blockquote>
                ))}
              </details>
              {Array.isArray(payload.condition_markers) && payload.condition_markers.length > 0 && (
                <section className="life-condition-markers" aria-label="逐项条件说明">
                  <h3>逐项条件说明</h3>
                  <ul>
                    {payload.condition_markers.map((item: any) => (
                      <li key={item.dimension}>
                        <strong>{item.label}</strong>
                        <span>{item.statement}</span>
                        {item.condition === "available" && item.scope === "reviewed_structure_only" && (
                          <small>仅限已审核结构事实</small>
                        )}
                        {item.condition === "not_available" && item.reason && <p>{item.reason}</p>}
                      </li>
                    ))}
                  </ul>
                </section>
              )}
              <aside aria-label="大运与强弱未决边界">
                <strong>大运与旺衰仍未裁定</strong>
                <p>{integrated.dayun}</p><p>{integrated.boundary}</p>
              </aside>
            </section>
          )}
            </section>
          )}

          {screen === "strength" && (
            <section className="slice-life-screen" aria-label="旺衰与喜用">
              <div className="slice-layer-head">
                <span className="eyebrow">第二屏</span>
                <h2>旺衰与喜用</h2>
                <p>以下三项取自本次计算顶层字段（与八字命理场景同一组呈现对象），只转述后端结论、依据与适用限制；统一裁决弃判。</p>
              </div>
              {sliceRenderStrength(strengthPresentation)}
              {sliceRenderXiyong(xiyongPresentation)}
              {sliceRenderPattern(patternPresentation)}
            </section>
          )}

          {screen === "dayun" && (
            <section className="slice-life-screen" aria-label="大运流年">
              <div className="slice-layer-head">
                <span className="eyebrow">第三屏</span>
                <h2>大运流年</h2>
                <p>当前所处大运按交运区间包含关系确定；今日落在交运区间内时，显式写“可能处于交运前后”，不强行定归属。点“查看详情”进流年结构完整页。</p>
              </div>
              {sliceRenderFullDayun({
                fullDayun,
                fullDayunError,
                fullDayunLoading,
                roleSelected: dayunRole !== "",
                method: dayunMethod,
                onMethodChange: setDayunMethod,
                onLoad: loadFullDayun,
              })}
          {/* T-D1 (E0409): first-period dayun only. The presentation
              carries eight entries; only the first has an interval,
              periods 2-8 are not_provided, and no starting age is
              ever shown. Read the top-level dayun_presentation, not
              the nested career section's copy. */}
          {dayun && (
            <section className="bazi-dayun-presentation" aria-label="大运首运方向与交运区间">
              <span className="eyebrow">大运首运 · 两口径分立呈现</span>
              <h3>大运首运方向与交运区间</h3>
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
                const first = view.entries[0];
                return (
                  <div className="bazi-dayun-method">
                    <p>
                      大运方向：{view.direction.label}（{view.direction.counting_target === "future_jie" ? "数至出生后之节" : "数至出生前之节"}：{view.direction.counted_jie.name} {view.direction.counted_jie.at}）。
                    </p>
                    <p>
                      <strong>第 1 运 {first.ganzhi}</strong>
                      <span>（{first.ten_god_relative_to_natal_day_stem}）</span>
                      {first.state === "interval" && (
                        <span>交运区间：{first.start_interval.earliest} 至 {first.start_interval.latest}（不含上限）</span>
                      )}
                      {first.state === "unresolved" && (
                        <span>交运时间暂不可判。</span>
                      )}
                    </p>
                    <p className="bazi-dayun-notice">第 2–8 运尚未在本场景开放：本口径只呈现首运交运区间。不折算起运岁数或日期；大运时间轴整体仍未获批。</p>
                    {view.notices.map((notice: any) => (
                      <p key={notice.code} className="bazi-dayun-notice">{notice.text}</p>
                    ))}
                  </div>
                );
              })()}
            </section>
          )}
            <section className="life-section life-focus">
              <div className="result-section-heading">
                <div><h2>{targetYear} 流年结构</h2></div>
                <Link className="text-action" href="/yearly-structure" onClick={() => saveTargetYear(targetYear)}>查看详情 <Icon name="arrow" size={15} /></Link>
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
                    const refs: Array<{ id: string; title: string; quote: string; grade: string; excerpt: boolean }> =
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
                          excerpt: source.original_text_excerpt === true || source.classic_title_excerpt === true,
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
                                <p>{ref.quote}{ref.excerpt ? "（节选）" : ""}</p>
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
            </section>
          )}

          {screen === "career" && (
            <section className="slice-life-screen" aria-label="事业财运">
              <div className="slice-layer-head">
                <span className="eyebrow">第四屏</span>
                <h2>事业财运</h2>
                <p>财星与相关十神结构、主要分析信息与当前大运、流年的并列关联。点“查看详情”进事业财运完整页。</p>
              </div>
          <section className="life-section">
            <div className="result-section-heading">
              <div><h2>事业财运结构</h2></div>
              <Link className="text-action" href="/career-wealth-structure" onClick={() => saveTargetYear(targetYear)}>查看详情 <Icon name="arrow" size={15} /></Link>
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
                          <p>{item.original}{item.excerpt ? "（节选）" : ""}</p>
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
                            {refs.map((ref) => <blockquote key={ref.id}><small>{ref.title} · {ref.level}</small><p>{ref.original}{ref.excerpt ? "（节选）" : ""}</p></blockquote>)}
                          </details>
                        ) : <small>无可核验原典短引，不进行扩展解释。</small>;
                      })()}
                    </article>
                  ))}
                </div>
              </details>
            )}
          </section>
            </section>
          )}

          {screen === "romance" && (
            <section className="slice-life-screen" aria-label="桃花姻缘">
              <div className="slice-layer-head">
                <span className="eyebrow">第五屏</span>
                <h2>桃花姻缘</h2>
                <p>咸池与夫妻宫的已有事实、解释依据与适用限制。总览内不呈现配偶星配对，配对详情请进缘分合盘页。</p>
              </div>
            <section className="life-section life-focus">
              <div className="result-section-heading">
                <div><h2>桃花结构</h2></div>
                <Link className="text-action" href="/romance-structure" onClick={() => saveTargetYear(targetYear)}>查看详情 <Icon name="arrow" size={15} /></Link>
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
                              <blockquote key={item.id}><small>{item.title} · {item.level}</small><p>{item.original}{item.excerpt ? "（节选）" : ""}</p></blockquote>
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
              <p className="slice-romance-note">总览内不呈现配偶星配对，配对详情请进缘分合盘页查看。</p>
              <Link className="text-action" href="/compatibility-structure" onClick={() => saveTargetYear(targetYear)}>缘分合盘 <Icon name="arrow" size={15} /></Link>
            </section>
          )}

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
            <p>这是一份结构聚合报告，不是完整人生预测。旺衰、喜用、格局的呈现仅限已审局部事实（见“旺衰与喜用”屏）；正缘、收入、健康和事件应期等尚未通过完整规则与证据校验的内容不会在这里补写。</p>
          </section>
        </section>
      )}
    </div>
  );
}
