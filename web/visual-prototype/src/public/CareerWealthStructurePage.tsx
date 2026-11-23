import { useEffect, useRef, useState } from "react";
import type { FormEvent } from "react";
import { ConsumerResultSummary } from "./ConsumerResultSummary";
import { Icon } from "../shared/Icon";
import { Link } from "../shared/router";
import { executeCareerScenario, executeBaziProfileScenario, type ScenarioExecuteResponse } from "./api";
import { readSavedTargetYear, saveTargetYear, isValidTargetYear, MIN_TARGET_YEAR, MAX_TARGET_YEAR } from "./targetYear";
import { readSavedBirthProfile, saveBirthProfile } from "./birthProfile";
import { toApiValue, toApiZone, fromLegacy, toSolarDateString, isConvertedFromLunar, fromSolarEdit, withUpdatedTime } from "./birthProfile";
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

function displayEvidence(id: string, row: Record<string, any>) {
  // Reject incomplete citations rather than fabricating titles or quotations.
  const title = row.classic_title || row.title || row.source_title;
  const quote = row.original_text;
  if (typeof title !== "string" || !title.trim() ||
      typeof quote !== "string" || !quote.trim()) return null;
  return { id, title, quote,
    grade: typeof row.evidence_level === "string" ? row.evidence_level : "未标注",
    excerpt: row.original_text_excerpt === true || row.classic_title_excerpt === true };
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


export function CareerWealthStructurePage() {
  const [date, setDate] = useState(() => toSolarDateString(readSavedBirthProfile()));
  const [time, setTime] = useState(() => readSavedBirthProfile().time);
  const [targetYear, setTargetYear] = useState(readSavedTargetYear);
  const [result, setResult] = useState<ScenarioExecuteResponse | null>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [view, setView] = useState<"career" | "wealth">("career"); // TJ-023.2: dual view, same underlying run
  // T-D1 (E0409): optional traditional dayun role, same precedent as
  // bazi-profile; the role is sent only when explicitly selected.
  const [dayunRole, setDayunRole] = useState<"" | "male" | "female">("");
  const [dayun, setDayun] = useState<any>(null);
  const [dayunMethod, setDayunMethod] = useState<"sanming" | "shenfeng">("sanming");
  // TJ-0422 phase 2 slice B: full 8-period timeline comes from a lazy,
  // single bazi-profile call on the same birth input (never eager: the
  // T-D1 capture in tj0173-dayun-career-life-td1.spec.ts reads the last
  // scenario response, which must stay the career envelope). The role
  // is only ever the explicitly selected one; nothing is defaulted.
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
        if (date === initialSolar && time === currentProfile.time) {
          return toApiValue(currentProfile);
        }
        if (date === initialSolar) {
          return toApiValue(withUpdatedTime(currentProfile, time));
        }
        return toApiValue(fromSolarEdit(date, time, currentProfile.region, currentProfile));
      })();
      const careerInput: {
        birth_value: string;
        birth_zone?: string;
        target_year: number;
        traditional_role?: "male" | "female";
      } = {
        birth_value: birthValue,
        target_year: year,
        birth_zone: toApiZone(readSavedBirthProfile()),
      };
      if (dayunRole) careerInput.traditional_role = dayunRole;
      const response = await executeCareerScenario(careerInput);
      if (version !== requestVersion.current) return;
      setDayun(response.result?.dayun_presentation ?? null);
      setSubmittedBirth({ value: birthValue, zone: toApiZone(readSavedBirthProfile()) });
      (() => {
        const currentProfile = readSavedBirthProfile();
        const initialSolar = toSolarDateString(currentProfile);
        if (date === initialSolar && time === currentProfile.time) {
          return;
        }
        if (date === initialSolar) {
          saveBirthProfile(withUpdatedTime(currentProfile, time));
          return;
        }
        saveBirthProfile(fromSolarEdit(date, time, currentProfile.region, currentProfile));
      })();
      saveTargetYear(year);
      setTargetYear(year);
      setResult(response);
    } catch (err) {
      if (version === requestVersion.current)
        setError(err instanceof Error ? err.message : "事业财运结构计算失败。");
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
  // Lazy on purpose: the first-period section above keeps reading the
  // career envelope only, and no second call fires unless the user
  // asks for the timeline.
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
  const natal = payload.natal || {};
  const groups = payload.structure_groups || {};
  const flowYear = payload.target_year || {};
  const cards: Array<any> = Array.isArray(payload.interpretation_cards) ? payload.interpretation_cards : [];
  const annualReading = payload.annual_reading || null;
  const strengthPresentation = (payload.strength_presentation ?? null) as SliceStrengthPresentation | null;
  const xiyongPresentation = (payload.xiyong_presentation ?? null) as SliceXiyongPresentation | null;
  const patternPresentation = (payload.pattern_presentation ?? null) as SlicePatternPresentation | null;
  const branchInteractions = annualReading?.annual_branch_interactions ?? null;
  const branchHits: Array<any> = Array.isArray(branchInteractions?.hits) ? branchInteractions.hits : [];
  // 十神到结构组的归属直接取自本场景 structure_groups 的 ten_gods
  // 列表，不另造映射；只用于把当前运十神指回第一层的位置统计。
  const groupForTenGod = (tenGod: string): string | null => {
    for (const group of Object.values(groups as Record<string, any>)) {
      if (Array.isArray(group?.ten_gods) && group.ten_gods.includes(tenGod))
        return typeof group.label === "string" ? group.label : null;
    }
    return null;
  };
  const fullDayunCurrent = fullDayun
    ? sliceResolveCurrentDayun(fullDayun.methods.sanming.entries, Date.now())
    : null;
  const evidence = result
    ? Object.entries(result.evidence).map(([id, value]) => displayEvidence(id, value))
        .filter((entry): entry is NonNullable<typeof entry> => entry !== null)
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
          <h1>事业与财运，先看可核对的线索。</h1>
          <p>
            这一版在十神与藏干结构之外，补上了已审的旺衰、喜用、格局呈现、
            完整 8 运时间线与 {targetYear} 流年地支结构：哪些星明见在天干、哪些藏在地支，
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
              <input type="date" value={date} onChange={(e) => { invalidateResult(); setDate(e.target.value); }} required />
            </label>
            <label>
              <span>出生时间</span>
              <input type="time" value={time} onChange={(e) => { invalidateResult(); setTime(e.target.value); }} required />
            </label>
            <label className="career-fixed-year">
              <span>观察年份</span>
              <input type="number" min={MIN_TARGET_YEAR} max={MAX_TARGET_YEAR} step={1} value={targetYear}
                onChange={(event) => { invalidateResult(); setTargetYear(Number(event.target.value)); }}
                required />
            </label>
          </div>
          {/* T-D1 (E0409): optional traditional dayun role, same
              precedent as bazi-profile; not selected means no dayun. */}
          <div className="bazi-dayun-role">
            <label htmlFor="career-dayun-role">传统大运口径（可选）</label>
            <select
              id="career-dayun-role"
              value={dayunRole}
              onChange={(e) => { invalidateResult(); setDayunRole(e.target.value as "" | "male" | "female"); }}
            >
              <option value="">不启用</option>
              <option value="male">传统男命口径</option>
              <option value="female">传统女命口径</option>
            </select>
            <small>只用于按传统口径呈现大运首运方向与交运区间；不选择时不呈现大运。该选择只随本次计算发送，不保存。</small>
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
            <li>已审的旺衰形态、调候与病药取用依据、寅月局部真格</li>
            <li>当前大运与完整 8 运时间线（须选传统口径）</li>
            <li>{targetYear} 流年地支与四柱的冲合害结构</li>
          </ul>
          <p>升职、跳槽、收入、投资、行业推荐等结论仍不在本版内：大运与流年的相互作用、岁运效力与应期尚未裁定，这里只并列已算事实，不作效力判断。</p>
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
          <ConsumerResultSummary scenario="career" response={result} />
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
              <p className="career-view-note">
                {view === "career"
                  ? "事业视角：优先展示官杀（事业格局）、印星（资源助力）、食伤（才华输出）的真实位置。"
                  : "财运视角：优先展示财星（财富结构）、比劫（竞争合作）的真实位置。"}
                同一份计算结果，不因视角产生矛盾结论。
              </p>
            </div>
            <span className="career-limited">结构内测</span>
          </header>

          <section className="career-layer" aria-label="命局基础">
            <div className="slice-layer-head">
              <span className="eyebrow">第一层</span>
              <h2>命局基础</h2>
              <p>四柱、日主、十神结构与位置计数，加上已审的旺衰、喜用、格局呈现。白话解释为主，依据与限制可展开查看。</p>
            </div>
          <section className="career-natal">
            <div className="result-section-heading">
              <div><h2>原局四柱</h2></div>
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
          <div className="career-view-toggle" role="tablist" aria-label="事业/财运视图切换">
            <button
              role="tab"
              aria-selected={view === "career"}
              className={view === "career" ? "active" : ""}
              onClick={() => setView("career")}
            >
              事业视角
            </button>
            <button
              role="tab"
              aria-selected={view === "wealth"}
              className={view === "wealth" ? "active" : ""}
              onClick={() => setView("wealth")}
            >
              财运视角
            </button>
            <small>同一底层计算结果，仅切换呈现重点，不生成两份事实</small>
          </div>
          <div className="career-groups">
            {(view === "career"
              ? ["authority", "resource", "output", "wealth", "peers"]
              : ["wealth", "peers", "output", "authority", "resource"]
            ).map((groupId) => {
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
            {sliceRenderStrength(strengthPresentation)}
            {sliceRenderXiyong(xiyongPresentation)}
            {sliceRenderPattern(patternPresentation)}
          </section>

          <section className="career-layer" aria-label="当前大运">
            <div className="slice-layer-head">
              <span className="eyebrow">第二层</span>
              <h2>当前大运</h2>
              <p>当前所处大运按交运区间包含关系确定；今日落在交运区间内时，显式写“可能处于交运前后”，不强行定归属。只并列大运与原局的已算事实，不作相互作用判断。</p>
            </div>
            {sliceRenderFullDayun({
              fullDayun,
              fullDayunError,
              fullDayunLoading,
              roleSelected: dayunRole !== "",
              method: dayunMethod,
              onMethodChange: setDayunMethod,
              onLoad: loadFullDayun,
              groupForTenGod,
            })}
          {/* T-D1 (E0409): first-period dayun only. The presentation
              carries eight entries; only the first has an interval,
              periods 2-8 are not_provided, and no starting age is
              ever shown. */}
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
          </section>

          <section className="career-layer" aria-label="指定流年">
            <div className="slice-layer-head">
              <span className="eyebrow">第三层</span>
              <h2>指定流年</h2>
              <p>所选年份的流年干支、流年天干十神与流年地支结构，及与当前大运、命局的并列关联。点不同年份即时重新请求并更新。</p>
            </div>
            <div className="slice-year-stepper" aria-label="切换观察年份">
              <button type="button" onClick={() => runCalculation(targetYear - 1)} disabled={loading || !isValidTargetYear(targetYear - 1)}>← {targetYear - 1} 年</button>
              <strong>{targetYear} 年</strong>
              <button type="button" onClick={() => runCalculation(targetYear + 1)} disabled={loading || !isValidTargetYear(targetYear + 1)}>{targetYear + 1} 年 →</button>
              <small>点不同年份即时重新请求并更新。</small>
            </div>
          {annualReading && (
            <section className="career-annual-reading" aria-label="年度十神与原局综合解读">
              <span className="eyebrow">年度视角 · 已审依据</span>
              <h3>{annualReading.headline}</h3>
              <p>{annualReading.year_context}</p>
              <p>{annualReading.natal_context}</p>
              <p className="career-annual-boundary">{annualReading.boundary}</p>
              <details>
                <summary>查阅本段所依据的古籍原文</summary>
                {(annualReading.evidence_ids || []).map((id: string) => {
                  const source = evidence.find((item) => item.id === id);
                  return source ? (
                    <blockquote key={id}>
                      <strong>{source.title} · {source.grade}</strong>
                      <p>{source.quote}{source.excerpt ? "（节选）" : ""}</p>
                    </blockquote>
                  ) : null;
                })}
              </details>
            </section>
          )}
            {branchInteractions && (
              <section className="slice-branch" aria-label="流年地支与四柱的结构关系">
                <span className="eyebrow">流年地支结构 · 已审核固定关系</span>
                <h3>流年地支 {branchInteractions.flow_branch} 与四柱的结构关系</h3>
                <p>已核对 {branchInteractions.evaluated_pairs} 组地支；命中 {branchHits.length} 条六合、六害或六冲。与流年场景同源全等，只呈现固定结构关系，不推断应事与吉凶。</p>
                {branchHits.length ? branchHits.map((hit: any, index: number) => (
                  <article className="slice-branch-hit" key={hit.rule_id + "-" + hit.natal_pillar + "-" + index}>
                    <strong>{({ six_harmony: "六合", harm: "六害", clash: "六冲" } as Record<string, string>)[hit.relation_type] || hit.relation_type}</strong>
                    <span>{hit.flow_branch} ↔ {hit.natal_branch} · {pillarNames[hit.natal_pillar] || hit.natal_pillar}</span>
                    <details>
                      <summary>本条古籍依据</summary>
                      {(hit.evidence_ids || []).map((id: string) => {
                        const source = evidence.find((item) => item.id === id);
                        return source ? (
                          <blockquote key={id}>
                            <strong>{source.title} · {source.grade}</strong>
                            <p>{source.quote}{source.excerpt ? "（节选）" : ""}</p>
                          </blockquote>
                        ) : null;
                      })}
                    </details>
                  </article>
                )) : <p>此年未命中已审核的三类成对结构，不等于全年没有变化。</p>}
                <small>仅是固定规则的结构命中，不推断应事、婚恋、财运或吉凶。</small>
              </section>
            )}
            {fullDayunCurrent?.kind === "current" && (
              <p className="slice-dayun-link">与当前大运并列：当前为第 {fullDayunCurrent.entry.period_index} 运 {fullDayunCurrent.entry.ganzhi}（{fullDayunCurrent.entry.ten_god_relative_to_natal_day_stem}），{targetYear} 年流年干支为 {flowYear.ganzhi || "—"}。两组事实只并列呈现，不作大运与流年的相互作用或岁运效力判断。</p>
            )}
            {fullDayunCurrent?.kind === "ambiguous" && (
              <p className="slice-dayun-link">与当前大运并列：今日可能处于交运前后（第 {fullDayunCurrent.next.period_index} 运交运区间内），{targetYear} 年流年干支为 {flowYear.ganzhi || "—"}。两组事实只并列呈现，不作大运与流年的相互作用或岁运效力判断。</p>
            )}
          </section>

          <div className="career-two-columns">
            <section className="live-section">
              <div className="result-section-heading"><div><h2>典籍依据</h2></div></div>
              {!evidence.length && <p>当前没有可核验的古籍短引，不追加推断。</p>}
              {evidence.map((item) => (
                <article className="live-evidence" key={item.id}>
                  <div><strong>{item.title}</strong><span>{item.grade}</span></div>
                  <blockquote>{item.quote}{item.excerpt ? "（节选）" : ""}</blockquote>
                </article>
              ))}
            </section>

            <section className="live-section career-limits">
              <div className="result-section-heading"><div><h2>当前不能下的结论</h2></div></div>
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
              <h3>下一步才会接近真正的事业财运报告</h3>
              <p>
                本版已补上有规则证据的旺衰、喜用、格局呈现与完整大运时间线；下一步仍需补大运与流年的实际作用、岁运效力与应期判断并做跨证据验证。
                这些完成前，只展示结构，不给收益承诺。
              </p>
            </div>
          </div>
        </section>
      )}
    </div>
  );
}
