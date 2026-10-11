import type { ScenarioExecuteResponse } from "./api";
import "./consumer-result-summary.css";

export type ConsumerScenario = "daily" | "yearly" | "romance" | "career";

type Report = {
  title: string;
  lead: string;
  facts: Array<{ label: string; value: string }>;
  boundary: string;
};

function meaningful(value: unknown): string | null {
  if (typeof value !== "string") return null;
  const text = value.trim();
  return text && text !== "—" ? text : null;
}

function verifiedEvidenceCount(response: ScenarioExecuteResponse): number {
  return Object.values(response.evidence || {}).filter((row) => (
    typeof row?.classic_title === "string" && row.classic_title.trim() &&
    typeof row?.original_text === "string" && row.original_text.trim()
  )).length;
}

/**
 * Explain ONLY deterministic facts supplied by the actual Scenario API.
 * Do not derive favorable/unfavorable outcomes, scores, wedding dates or returns
 * from a ten-god, branch relation, Xianchi hit or an absence of matches.
 */
export function buildConsumerReport(
  scenario: ConsumerScenario,
  response: ScenarioExecuteResponse,
): Report {
  const data = response.result || {};
  const facts: Report["facts"] = [];
  const add = (label: string, value: unknown) => {
    const text = meaningful(value);
    if (text) facts.push({ label, value: text });
  };

  if (scenario === "daily") {
    const day = data.target_day || {};
    const natal = data.natal || {};
    add("你查看的日期", day.date);
    add("这一天的干支", day.ganzhi);
    if (meaningful(day.stem_ten_god) && meaningful(natal.day_master?.stem))
      add("相对你的日主", `${day.stem_ten_god}（日主 ${natal.day_master.stem}）`);
    const matches = data.xianchi?.target_day_activation || {};
    const count = Number(matches.year_branch_basis?.matched === true) +
      Number(matches.day_branch_basis?.matched === true);
    add("传统桃花查表", `两种基准中命中 ${count} 项，仅指结构`);
    return {
      title: "今日运势 · 已核算的部分",
      lead: `这是当天的传统干支与关系参考，以下 ${facts.length} 项来自本次真实计算。`,
      facts,
      boundary: "尚不能据此判断今天运气好坏、宜忌或是否有桃花事件。",
    };
  }

  if (scenario === "yearly") {
    const year = data.target_year || {};
    const natal = data.natal || {};
    add("流年干支", year.ganzhi);
    if (meaningful(year.stem_ten_god) && meaningful(natal.day_master?.stem))
      add("与你日主的关系", `${year.stem_ten_god}（日主 ${natal.day_master.stem}）`);
    const rel = data.annual_branch_interactions;
    if (rel && Array.isArray(rel.hits)) {
      add("已审核的地支关系", `与原局逐项对照，命中 ${rel.hits.length} 条六合、六害或六冲`);
    }
    return {
      title: "流年运势 · 先看真实关系",
      lead: "流年与出生盘的对应关系已计算；结果按规则与适用范围呈现。",
      facts,
      boundary: "没有完成旺衰、喜用及大运的综合裁定，不能推导全年吉凶、财富或婚期。",
    };
  }

  if (scenario === "romance") {
    const targets = data.xianchi?.targets || {};
    const activation = data.target_year_activation || {};
    const natal = Array.isArray(data.xianchi?.natal_matches) ? data.xianchi.natal_matches : [];
    add("年支查表对应", targets.year_branch);
    add("日支查表对应", targets.day_branch);
    add("出生盘匹配", `已审核的查表位置共 ${natal.length} 处`);
    const matched = Number(activation.year_branch_basis?.matched === true) +
      Number(activation.day_branch_basis?.matched === true);
    if (activation.year_branch_basis || activation.day_branch_basis)
      add("所选年份的匹配", `两种查表基准中命中 ${matched} 项`);
    return {
      title: "桃花姻缘 · 本次核对结果",
      lead: "分别看年支和日支的传统咸池条件，不把两种方法混成一个评分。",
      facts,
      boundary: "结构命中或未命中都不等于现实中会不会恋爱；正缘、婚期、婚姻吉凶尚无足够审定依据。",
    };
  }

  const year = data.target_year || {};
  const groups = data.structure_groups || {};
  add("所选年份的流年关系", year.stem_ten_god);
  for (const [id, label] of [["wealth", "财星"], ["authority", "官杀"]] as const) {
    const group = groups[id] || {};
    if (Number.isInteger(group.visible_count) && Number.isInteger(group.hidden_count))
      add(`${label}在出生盘的位置`, `天干明见 ${group.visible_count} 处、地支藏干 ${group.hidden_count} 处`);
  }
  return {
    title: "事业财运 · 本次核对结果",
    lead: "先展示可核验的十神位置与年份关系，再阅读下方详细原局分析。",
    facts,
    boundary: "十神位置和出现次数不能直接预测升职、收入、投资回报；旺衰、格局、喜用与大运仍待完整审定。",
  };
}

export function ConsumerResultSummary({
  scenario, response,
}: {
  scenario: ConsumerScenario;
  response: ScenarioExecuteResponse;
}) {
  const report = buildConsumerReport(scenario, response);
  const sources = verifiedEvidenceCount(response);
  return (
    <section className="consumer-result-summary" aria-label="本次测算摘要">
      <div className="consumer-result-summary-header">
        <span className="eyebrow">先读这份结果 · 真实数据</span>
        <span className="consumer-result-status">限定版 · 不编吉凶</span>
      </div>
      <h2>{report.title}</h2>
      <p className="consumer-result-lead">{report.lead}</p>
      {report.facts.length ? (
        <dl className="consumer-result-facts">
          {report.facts.map(({ label, value }) => (
            <div key={label}><dt>{label}</dt><dd>{value}</dd></div>
          ))}
        </dl>
      ) : (
        <p role="status">本次未返回可展示的审核结构字段，不能生成个人结论。</p>
      )}
      <div className="consumer-result-bottom">
        <p><strong>目前不能断言：</strong>{report.boundary}</p>
        <small>{sources
          ? `本次响应包含 ${sources} 条具有原文与书名的审核来源；具体引用及适用条件见下方。`
          : "本次没有收到可展示的完整审核短引；只能查看返回的计算事实，不补充解释。"}
        </small>
      </div>
    </section>
  );
}
