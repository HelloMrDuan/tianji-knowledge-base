import { useEffect, useRef, useState } from "react";
import type { FormEvent } from "react";
import { ConsumerResultSummary } from "./ConsumerResultSummary";
import { Icon } from "../shared/Icon";
import { Link } from "../shared/router";
import { executeRomanceScenario, type ScenarioExecuteResponse } from "./api";
import { readSavedTargetYear, saveTargetYear, isValidTargetYear, MIN_TARGET_YEAR, MAX_TARGET_YEAR } from "./targetYear";
import { readSavedBirthProfile, saveBirthProfile } from "./birthProfile";
import { toApiValue, toApiZone, fromLegacy, toSolarDateString, isConvertedFromLunar, fromSolarEdit, withUpdatedTime } from "./birthProfile";
import "./romance-structure.css";

const relationNames: Record<string, string> = {
  six_harmony: "六合",
  harm: "六害",
  clash: "六冲",
  same_branch: "地支相同",
  same_stem: "天干相同",
};

const pillarNames: Record<string, string> = {
  year: "年柱",
  month: "月柱",
  day: "日柱",
  hour: "时柱",
};

function displayEvidence(id: string, source: Record<string, any>) {
  const title = source.classic_title || source.title || source.source_title;
  const quote = source.original_text;
  if (typeof title !== "string" || !title.trim() ||
      typeof quote !== "string" || !quote.trim()) return null;
  return {
    id,
    title,
    quote,
    grade: typeof source.evidence_level === "string" ? source.evidence_level : "未标注",
    excerpt: source.original_text_excerpt === true || source.classic_title_excerpt === true,
  };
}

function basisLabel(value: string) {
  return value === "year_branch" ? "年支起查" : value === "day_branch" ? "日支起查" : value;
}

export function RomanceStructurePage() {
  const [date, setDate] = useState(() => toSolarDateString(readSavedBirthProfile()));
  const [time, setTime] = useState(() => readSavedBirthProfile().time);
  const [role, setRole] = useState<"" | "male" | "female">("");
  const [targetYear, setTargetYear] = useState(readSavedTargetYear);
  const [result, setResult] = useState<ScenarioExecuteResponse | null>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const requestVersion = useRef(0);

  useEffect(() => () => { requestVersion.current += 1; }, []);

  function invalidateResult() {
    requestVersion.current += 1;
    setResult(null);
    setError("");
    setLoading(false);
  }

  function fillSample() {
    setDate("2000-01-07");
    setTime("12:00");
    invalidateResult();
  }

  async function submit(event: FormEvent) {
    event.preventDefault();
    const version = ++requestVersion.current;
    setLoading(true);
    setError("");
    setResult(null);
    try {
      if (!isValidTargetYear(targetYear)) throw new Error("请选择 1901 至 2098 年的公历年份");
      const romanceInput: {
        birth_value: string;
        birth_zone?: string;
        target_year: number;
        traditional_role?: "male" | "female";
      } = {
        birth_value: (() => {
        const currentProfile = readSavedBirthProfile();
        const initialSolar = toSolarDateString(currentProfile);
        if (date === initialSolar && time === currentProfile.time) {
          return toApiValue(currentProfile);
        }
        if (date === initialSolar) {
          return toApiValue(withUpdatedTime(currentProfile, time));
        }
        return toApiValue(fromSolarEdit(date, time, currentProfile.region, currentProfile));
      })(),
        target_year: targetYear,
        birth_zone: toApiZone(readSavedBirthProfile()),
      };
      // 仅当用户显式选择传统口径时才发送；未选择时请求与既往逐字一致。
      if (role) romanceInput.traditional_role = role;
      const response = await executeRomanceScenario(romanceInput);
      if (version !== requestVersion.current) return;
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
      saveTargetYear(targetYear);
      setResult(response);
    } catch (err) {
      if (version === requestVersion.current)
        setError(err instanceof Error ? err.message : "桃花结构计算失败。");
    } finally {
      if (version === requestVersion.current) setLoading(false);
    }
  }

  const payload = result?.result || {};
  const natal = payload.natal || {};
  const pillars = Array.isArray(natal.pillars) ? natal.pillars : [];
  const xianchi = payload.xianchi || {};
  const targets = xianchi.targets || {};
  const natalMatches = Array.isArray(xianchi.natal_matches) ? xianchi.natal_matches : [];
  const activation = payload.target_year_activation || {};
  const flowYear = payload.target_year || {};
  const spousePalace = payload.spouse_palace_year_relations;
  const spouseRelations: Array<any> = Array.isArray(spousePalace?.relations) ? spousePalace.relations : [];
  const spousePairing = payload.spouse_star_year_pairing;
  const pairingRows: Array<any> = Array.isArray(spousePairing?.pairings) ? spousePairing.pairings : [];
  const pairingVisible: Array<any> = Array.isArray(spousePairing?.candidate_positions?.visible) ? spousePairing.candidate_positions.visible : [];
  const pairingHidden: Array<any> = Array.isArray(spousePairing?.candidate_positions?.hidden) ? spousePairing.candidate_positions.hidden : [];
  const evidence = result
    ? Object.entries(result.evidence).map(([id, value]) => displayEvidence(id, value))
        .filter((item): item is NonNullable<typeof item> => item !== null)
    : [];
  const evidenceById = new Map(evidence.map((item) => [item.id, item]));

  const yearMatches = natalMatches.filter((item: any) => item.basis === "year_branch");
  const dayMatches = natalMatches.filter((item: any) => item.basis === "day_branch");

  return (
    <div className="romance-page">
      <div className="breadcrumb">
        <Link href="/">生活场景</Link>
        <Icon name="chevron" size={12} />
        <span>桃花姻缘 · 结构内测</span>
      </div>

      <section className="romance-hero">
        <div className="romance-hero-copy">
          <span className="eyebrow">桃花姻缘 · 第一层真实能力</span>
          <h1>看看你的桃花姻缘，有哪些传统线索。</h1>
          <p>
            依据已审核的传统咸池查表与地支冲合害规则，
            分别列出年支、日支两套咸池结果，另外核对日支与 {targetYear} 流年地支的结构关系。
            不用一个神煞就替你下婚恋结论。
          </p>
        </div>
        <div className="romance-mark" aria-hidden="true">
          <span>缘</span>
          <small>有据再言</small>
        </div>
      </section>

      <section className="romance-entry">
        <form onSubmit={submit}>
          <div className="romance-entry-head">
            <div>
              <span className="eyebrow">输入出生资料</span>
              <h2>查看你的咸池结构</h2>
            </div>
            <button type="button" className="sample-fill" onClick={fillSample}>填入示例</button>
          </div>
          <div className="romance-input-grid">
            <label>
              <span>出生日期</span>
              <input type="date" value={date} onChange={(e) => { invalidateResult(); setDate(e.target.value); }} required />
            </label>
            <label>
              <span>出生时间</span>
              <input type="time" value={time} onChange={(e) => { invalidateResult(); setTime(e.target.value); }} required />
            </label>
            <label className="romance-fixed-year">
              <span>观察年份</span>
              <input type="number" min={MIN_TARGET_YEAR} max={MAX_TARGET_YEAR} step={1} value={targetYear}
                onChange={(event) => { invalidateResult(); setTargetYear(Number(event.target.value)); }}
                required />
            </label>
            <label>
              <span>传统配偶星口径（可选）</span>
              <select value={role} onChange={(e) => { invalidateResult(); setRole(e.target.value as "" | "male" | "female"); }}>
                <option value="">不启用</option>
                <option value="female">传统女命口径 · 看官杀</option>
                <option value="male">传统男命口径 · 看财星</option>
              </select>
              <small>只用于传统配偶星定位观察，不代表婚恋结论；不启用时不做配偶星配对。</small>
            </label>
          </div>
          <div className="romance-entry-note">
            <Icon name="shield" size={16} />
            <span>北京时间 UTC+8。年支与日支分别计算，不强行合并成唯一流派结论。</span>
          </div>
          <button className="button primary romance-submit" type="submit" disabled={loading}>
            {loading ? "正在计算…" : "查看桃花结构"}
            {!loading && <Icon name="arrow" size={18} />}
          </button>
          {error && <p className="question-error" role="alert">{error}</p>}
        </form>

        <aside>
          <span className="eyebrow">当前不会输出</span>
          <h2>没有“桃花指数”，也不预测何时脱单</h2>
          <ul>
            <li>不把咸池命中等同于桃花旺</li>
            <li>不判断正缘、烂桃花或婚姻吉凶</li>
            <li>不根据古籍旧式断语推断性格、疾病</li>
            <li>不使用 AI 补齐缺失规则</li>
            <li>不由流年结构推断大运影响</li>
          </ul>
          <p>当前夫妻宫仅观察日支位置与流年的已审六合、六冲、六害，不代表现实婚恋结果。其他体系继续补充。</p>
        </aside>
      </section>

      {!result && !loading && (
        <section className="romance-empty">
          <span>缘</span>
          <div>
            <h2>这里没有预制“情感文案”</h2>
            <p>真实 Scenario Engine 返回后，才展示你的结构结果。</p>
          </div>
        </section>
      )}

      {result && (
        <section className="romance-result">
          <ConsumerResultSummary scenario="romance" response={result} />
          <header className="romance-result-head">
            <div>
              <span className="eyebrow">结构事实 · 不作婚恋推断</span>
              <h2>
                年支目标 {targets.year_branch || "—"}
                <span> · </span>
                日支目标 {targets.day_branch || "—"}
              </h2>
              <p>
                {targetYear} {flowYear.ganzhi || "—"} · 流年地支 {flowYear.branch || "—"}。
                两个基准分别展示，不互相覆盖。
              </p>
            </div>
            <span className="romance-limited">结构内测</span>
          </header>

          <section className="romance-presentation-section" aria-label="桃花、配偶星与夫妻宫">
            <div className="result-section-heading">
              <div><span>一</span><h2>桃花、配偶星与夫妻宫</h2></div>
              <small>结构事实 · 两套基准分别展示</small>
            </div>
            <p className="romance-section-basis">
              依据：已审咸池查表（年支、日支两套基准分别展示）与夫妻宫日支配对；
              配偶星仅在用户显式选择传统口径时配对。只陈述结构事实，不作婚恋推断。
            </p>

          <div className="romance-basis-grid">
            <article>
              <div className="romance-basis-title">
                <span>年</span>
                <div><small>年支起查</small><strong>咸池目标：{targets.year_branch || "—"}</strong></div>
              </div>
              <div className="romance-signal">
                <span>原局命中</span>
                <b>{yearMatches.length ? "有结构命中" : "未见结构命中"}</b>
              </div>
              <div className="romance-signal">
                <span>{targetYear} 流年</span>
                <b>{activation.year_branch_basis?.matched ? "命中目标支" : "未命中目标支"}</b>
              </div>
              {yearMatches.length > 0 && (
                <p>原局位置：{yearMatches.map((item: any) => pillarNames[item.pillar] || item.pillar).join("、")}</p>
              )}
            </article>

            <article>
              <div className="romance-basis-title">
                <span>日</span>
                <div><small>日支起查</small><strong>咸池目标：{targets.day_branch || "—"}</strong></div>
              </div>
              <div className="romance-signal">
                <span>原局命中</span>
                <b>{dayMatches.length ? "有结构命中" : "未见结构命中"}</b>
              </div>
              <div className="romance-signal">
                <span>{targetYear} 流年</span>
                <b>{activation.day_branch_basis?.matched ? "命中目标支" : "未命中目标支"}</b>
              </div>
              {dayMatches.length > 0 && (
                <p>原局位置：{dayMatches.map((item: any) => pillarNames[item.pillar] || item.pillar).join("、")}</p>
              )}
            </article>
          </div>

          {spousePalace && (
            <section className="romance-natal romance-spouse-palace" aria-label="日支与流年地支关系">
              <div className="result-section-heading">
                <div><span>宫</span><h2>日支（传统夫妻宫位置） × {targetYear} 流年</h2></div>
                <small>成对规则 · 不作婚恋预测</small>
              </div>
              <p>
                原局日支 <strong>{spousePalace.natal_day_branch}</strong>，流年地支
                <strong> {spousePalace.target_year_branch}</strong>。已核对 1 组成对地支关系。
              </p>
              {spouseRelations.length ? (
                <div className="romance-spouse-hits">
                  {spouseRelations.map((item, index) => {
                    const linked = Array.isArray(item.evidence_ids)
                      ? item.evidence_ids.map((id: string) => evidenceById.get(id))
                          .filter((ref: any) => ref !== undefined)
                      : [];
                    return (
                      <article key={item.relation_type + "-" + index}>
                        <strong>{relationNames[item.relation_type] || item.relation_type}</strong>
                        <span>{item.natal_branch} ↔ {item.flow_branch}</span>
                        {typeof item.traditional_result_element === "string" && item.traditional_result_element && (
                          <small>传统合化结果五行：{item.traditional_result_element}（合化效力未评估）</small>
                        )}
                        {linked.length ? (
                          <details>
                            <summary>查看对应古籍短引（{linked.length}）</summary>
                            {linked.map((ref: any) => (
                              <blockquote key={ref.id}>
                                <b>{ref.title} · {ref.grade}</b>
                                <p>{ref.quote}{ref.excerpt ? "（节选）" : ""}</p>
                              </blockquote>
                            ))}
                          </details>
                        ) : <p className="romance-source-missing">缺少可核验的短引，不追加推断。</p>}
                      </article>
                    );
                  })}
                </div>
              ) : (
                <p>当前未命中本版已审核的六合、六冲、六害成对规则；不代表婚恋缺失或没有其他结构关系。</p>
              )}
              <p className="romance-spouse-boundary">日支位置不等于完整婚姻判断；没有裁定合化、生克效力、配偶星、婚期或吉凶。</p>
            </section>
          )}

          {spousePairing && (
            <section className="romance-natal romance-spouse-pairing" aria-label="配偶星候选位置与流年干支配对">
              <div className="result-section-heading">
                <div><span>星</span><h2>配偶星候选位置 × {targetYear} 流年干支</h2></div>
                <small>位置级配对 · 不作婚恋预测</small>
              </div>
              <p>
                传统口径候选十神：{(spousePairing.candidate_ten_gods || []).join("、")}。
                显干候选 {pairingVisible.length} 处、藏干候选 {pairingHidden.length} 处，共核对 {spousePairing.pairs_checked} 个候选位置；
                流年干支 <strong>{spousePairing.target_year?.ganzhi}</strong>。
              </p>
              {(pairingVisible.length > 0 || pairingHidden.length > 0) && (
                <p className="romance-candidate-overview">
                  候选位置总览：
                  {pairingVisible.length > 0 && (
                    <>显干 {pairingVisible.map((row: any) => `${pillarNames[row.pillar] || row.pillar} ${row.stem}（${row.ten_god}）`).join("、")}</>
                  )}
                  {pairingVisible.length > 0 && pairingHidden.length > 0 && "；"}
                  {pairingHidden.length > 0 && (
                    <>藏干 {pairingHidden.map((row: any) => `${pillarNames[row.pillar] || row.pillar} ${row.stem}（${row.ten_god}）`).join("、")}</>
                  )}
                  。未配对的位置也一并列出，不代表缺失。
                </p>
              )}
              {pairingRows.length ? (
                <div className="romance-spouse-hits">
                  {pairingRows.map((item, index) => {
                    const linked = Array.isArray(item.evidence_ids)
                      ? item.evidence_ids.map((id: string) => evidenceById.get(id))
                          .filter((ref: any) => ref !== undefined)
                      : [];
                    return (
                      <article key={item.relation + "-" + item.pillar + "-" + item.stem + "-" + index}>
                        <strong>{relationNames[item.relation] || item.relation}</strong>
                        <span>
                          {pillarNames[item.pillar] || item.pillar}
                          {item.position_kind === "hidden" ? "藏干" : "显干"} {item.stem}（{item.ten_god}）
                          ↔ 流年 {item.relation === "same_stem" ? spousePairing.target_year?.stem : spousePairing.target_year?.branch}
                        </span>
                        {item.relation === "six_harmony" && typeof item.traditional_result_element === "string" && item.traditional_result_element && (
                          <small>传统合化结果五行：{item.traditional_result_element}（合化效力未评估）</small>
                        )}
                        {linked.length ? (
                          <details>
                            <summary>查看对应古籍短引（{linked.length}）</summary>
                            {linked.map((ref: any) => (
                              <blockquote key={ref.id}>
                                <b>{ref.title} · {ref.grade}</b>
                                <p>{ref.quote}{ref.excerpt ? "（节选）" : ""}</p>
                              </blockquote>
                            ))}
                          </details>
                        ) : <p className="romance-source-missing">缺少可核验的短引，不追加推断。</p>}
                      </article>
                    );
                  })}
                </div>
              ) : spousePairing.pairing_state === "no_candidates" ? (
                <p>所选传统口径下，原局显干与藏干中未见候选十神位置。</p>
              ) : (
                <p>候选位置与流年干支未见天干、地支同一性，也未命中已审六合、六害、六冲。</p>
              )}
              <p className="romance-spouse-boundary">{spousePairing.limitations}</p>
            </section>
          )}

          </section>

          <section className="romance-natal romance-presentation-section" aria-label="原局婚姻关系结构">
            <div className="result-section-heading">
              <div><span>二</span><h2>原局婚姻关系结构</h2></div>
              <small>四柱、日主与藏干 · 只陈述结构</small>
            </div>
            {typeof natal.day_master?.stem === "string" && natal.day_master.stem && (
              <p className="romance-section-basis">
                日主 {natal.day_master.stem}{typeof natal.day_master?.element === "string" && natal.day_master.element ? `（${natal.day_master.element}）` : ""}，
                日支 {spousePalace?.natal_day_branch || "—"} 为传统夫妻宫位置。
              </p>
            )}
            <div className="romance-pillars">
              {pillars.map((item: any) => (
                <article key={item.name} className={item.name === "day" ? "day-pillar" : ""}>
                  <small>{pillarNames[item.name] || item.name}</small>
                  <strong>{item.ganzhi}</strong>
                  <span>{item.stem?.ten_god}</span>
                  {Array.isArray(item.branch?.hidden_stems) && item.branch.hidden_stems.length > 0 && (
                    <span className="romance-hidden-stems">
                      藏干：{item.branch.hidden_stems.map((hidden: any) => `${hidden.stem}（${hidden.ten_god}）`).join("、")}
                    </span>
                  )}
                </article>
              ))}
            </div>
            <p className="romance-section-undecided">
              夫妻宫喜忌、配偶星强弱与婚姻关系质量暂不可判：没有已获批的推理输出，
              旺衰、格局、喜用推理均未接入本页；日支位置与候选位置不等于完整婚姻判断。
            </p>
          </section>

          <section className="romance-natal romance-presentation-section" aria-label="流年联动与大运">
            <div className="result-section-heading">
              <div><span>三</span><h2>流年联动与大运</h2></div>
              <small>目标年结构联动 · 大运见八字命理页</small>
            </div>
            <p className="romance-section-basis">
              依据：目标年流年干支与原局结构的配对事实；大运不在本场景计算范围内。
            </p>
            <dl className="romance-linkage-facts">
              <div><dt>目标年</dt><dd>{targetYear} 年 {flowYear.ganzhi || "—"}（流年地支 {flowYear.branch || "—"}）</dd></div>
              <div><dt>咸池目标年激活</dt><dd>两个基准中命中 {Number(activation.year_branch_basis?.matched === true) + Number(activation.day_branch_basis?.matched === true)} 项</dd></div>
              <div><dt>夫妻宫 × 流年</dt><dd>{spouseRelations.length ? spouseRelations.map((item: any) => `${relationNames[item.relation_type] || item.relation_type}（${item.natal_branch} ↔ ${item.flow_branch}${typeof item.traditional_result_element === "string" && item.traditional_result_element ? `；传统合化结果五行：${item.traditional_result_element}，合化效力未评估` : ""}）`).join("、") : "未命中已审六合、六冲、六害"}</dd></div>
              {spousePairing && (
                <div><dt>配偶星 × 流年</dt><dd>{pairingRows.length ? `命中 ${pairingRows.length} 处配对` : spousePairing.pairing_state === "no_candidates" ? "所选传统口径下未见候选十神位置" : "未见配对命中"}</dd></div>
              )}
              <div><dt>流年边界口径</dt><dd>太阳年；参考日固定为 7 月 1 日，以稳定选取年度地支。</dd></div>
            </dl>
            <p className="romance-section-undecided">
              大运联动暂不可判：本场景不计算大运，大运与婚姻的组合规则尚未获批；
              大运时间轴请见<Link href="/bazi-profile">八字命理页</Link>，本页不由流年结构推断大运影响。
              本呈现不推断结婚年份或具体时间。
            </p>
          </section>

          <div className="romance-two-columns">
            <section className="live-section">
              <div className="result-section-heading"><div><span>四</span><h2>典籍依据</h2></div></div>
              {evidence.map((item) => (
                <article className="live-evidence" key={item.id}>
                  <div><strong>{item.title}</strong><span>{item.grade}</span></div>
                  <blockquote>{item.quote}{item.excerpt ? "（节选）" : ""}</blockquote>
                  <small>{item.id}</small>
                </article>
              ))}
            </section>

            <section className="live-section romance-limits">
              <div className="result-section-heading"><div><span>五</span><h2>边界与下一步</h2></div></div>
              {result.limitations.map((item, index) => <p key={index}>{item}</p>)}
              {result.warnings.map((item, index) => <div className="live-warning" key={index}>{item}</div>)}
            </section>
          </div>

          <div className="romance-next">
            <span>合</span>
            <div>
              <h3>目前没有已获批的桃花姻缘推理输出</h3>
              <p>
                本页完整呈现了已审核的结构计算：两套咸池查表、夫妻宫日支配对、
                配偶星全部候选位置与流年配对、四柱藏干，以及目标年的结构联动。
                旺衰、格局、喜用、组合推理均未接入本页公开呈现，配偶星与桃花推理的
                公开口径须另行提请晋升——在那之前，本页只陈述结构事实，不作婚恋推断。
              </p>
            </div>
          </div>
        </section>
      )}
    </div>
  );
}
