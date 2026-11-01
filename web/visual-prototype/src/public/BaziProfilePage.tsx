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
    try {
      const response = await executeBazi({ value: toApiValue(profile), zone: toApiZone(profile), strength_variant: "ditiansui-root-visibility-v1" });
      if (version !== requestVersion.current) return;
      saveBirthProfile(profile);
      setResult(response);
      // TJ-013.3 第一阶段：同一出生输入另取场景信封中的呈现对象；
      // 场景调用失败只令呈现节缺席，本页既有结果与行为不变。
      try {
        const scenario = await executeBaziProfileScenario({ value: toApiValue(profile), zone: toApiZone(profile), strength_variant: "ditiansui-root-visibility-v1" });
        if (version !== requestVersion.current) return;
        setXiyong(scenario.result?.xiyong_presentation ?? null);
      } catch {
        if (version === requestVersion.current) setXiyong(null);
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
            已可核验月支藏干、通根候选和透藏位置；但通用旺衰、喜用神、大运起运仍未完成证据裁定，因此这里不会提前生成断语。
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
            <li>不计算大运起运岁数</li>
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
          <header className="bazi-result-head">
            <div>
              <span className="eyebrow">真实 API · {result.variant}</span>
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

          {strength && (
            <section className="bazi-strength-observations" aria-label="旺衰因素与通根候选">
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
              <details>
                <summary>查看旺衰因素规则引用的真实古籍依据</summary>
                {result.rule_matches.flatMap((rule) => Array.isArray(rule.evidence_ids)
                  ? rule.evidence_ids.map((id: string) => evidenceById.get(id)).filter(Boolean)
                  : []).filter((item: any, index: number, rows: any[]) =>
                    rows.findIndex((row) => row.id === item.id) === index
                  ).map((source: any) => (
                  <blockquote key={source.id}><b>{source.title} · {source.grade}</b><p>{source.quote}{source.excerpt ? "（节选）" : ""}</p></blockquote>
                ))}
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
              <h4>病药（{xiyong.blocks.bingyao.source_label}）</h4>
              {xiyong.blocks.bingyao.lines.map((line: string, i: number) => (
                <p key={`by-${i}`}>{line}</p>
              ))}
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

          {/* TJ-031.4（Track B F3）：说明与限制是结果四层结构的第 4 层，
              有结果即须在场，不再随 warnings/limitations 是否为空而消失；
              分界约定在此明示，不用技术字段名。 */}
          <section className="live-section result-limitations">
            <div className="result-section-heading"><div><span>五</span><h2>说明与限制</h2></div></div>
            {result.warnings?.map((w: string, i: number) => (
              <p key={`w-${i}`} className="limitation-warning">⚠️ {w}</p>
            ))}
            {result.limitations?.map((l: string, i: number) => (
              <p key={`l-${i}`} className="limitation-note">ℹ️ {l}</p>
            ))}
            <p className="limitation-note">
              分界约定：年柱以立春交节为界，立春之前出生仍按上一年计算；日柱以午夜 0 点为界，晚上 23 点后的夜子时归当日，不顺延到次日。
            </p>
            <p className="limitation-note">
              以上为传统文化观察，不构成科学验证的未来预测。旺衰、喜用神、大运等需充分裁定，当前暂不提供结论。
            </p>
            {xiyong && (
              <>
                <p className="limitation-note">ℹ️ {xiyong.scope_statement}</p>
                {xiyong.limitations.map((l: string, i: number) => (
                  <p key={`xy-${i}`} className="limitation-note">ℹ️ {l}</p>
                ))}
              </>
            )}
          </section>

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

          <div className="bazi-next-card">
            <div>
              <span className="eyebrow">下一阶段</span>
              <h3>从基础档案走向“流年 / 桃花 / 事业财运”</h3>
              <p>这些场景会复用现在这份真实四柱结构，但必须等相应规则与证据补齐后才开放。</p>
            </div>
            <div className="bazi-journey-links">
              <Link href="/life-overview">人生总览</Link>
              <Link href="/yearly-structure">流年结构</Link>
              <Link href="/romance-structure">桃花姻缘</Link>
              <Link href="/career-wealth-structure">事业财运</Link>
              <Link href="/daily-structure">今日结构</Link>
            </div>
          </div>
        </section>
      )}
    </div>
  );
}
