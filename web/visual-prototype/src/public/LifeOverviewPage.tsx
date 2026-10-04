import { useState } from "react";
import type { FormEvent } from "react";
import { Icon } from "../shared/Icon";
import { Link } from "../shared/router";
import { executeLifeScenario, type ScenarioExecuteResponse } from "./api";
import { recordReading } from "./readingLibrary";
import "./life-overview.css";

const profileKey = "tianji.profile.birth.v1";
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

export function LifeOverviewPage() {
  const initial = readProfile();
  const [date, setDate] = useState(initial.date);
  const [time, setTime] = useState(initial.time);
  const [result, setResult] = useState<ScenarioExecuteResponse | null>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  function fillSample() {
    setDate("2000-01-07");
    setTime("12:00");
    setResult(null);
    setError("");
  }

  async function submit(event: FormEvent) {
    event.preventDefault();
    setLoading(true);
    setError("");
    setResult(null);
    try {
      const next = await executeLifeScenario({
        birth_value: `${date}T${time}:00+08:00`,
        target_year: 2026,
      });
      try {
        localStorage.setItem(profileKey, JSON.stringify({ date, time }));
      } catch {
        /* Preference persistence is optional. */
      }
      const dayMaster = next.result?.profile?.day_master?.stem;
      recordReading({
        scenarioId: "life",
        label: "人生总览",
        glyph: "命",
        title: "2026 人生结构总览",
        subtitle: dayMaster ? `日主 ${dayMaster} · 八字 / 流年 / 桃花 / 事业财运已聚合` : "四条真实结构主线已聚合",
        href: "/life-overview",
        resultVersion: next.result?.report_version || next.status,
      });
      setResult(next);
    } catch (err) {
      setError(err instanceof Error ? err.message : "人生总览生成失败。");
    } finally {
      setLoading(false);
    }
  }

  const payload = result?.result || {};
  const profile = payload.profile || {};
  const yearly = payload.yearly || {};
  const romance = payload.romance || {};
  const career = payload.career || {};
  const highlights = Array.isArray(payload.highlights) ? payload.highlights : [];
  const pillars = Array.isArray(profile.pillars) ? profile.pillars : [];
  const careerGroups = career.structure_groups || {};
  const yearTarget = yearly.target_year || {};
  const romanceTargets = romance.xianchi?.targets || {};
  const activation = romance.target_year_activation || {};
  const evidenceCount = result ? Object.keys(result.evidence).length : 0;

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
            <span>2026 结构</span><i />
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

      <section className="life-entry">
        <form onSubmit={submit}>
          <div className="life-entry-head">
            <div>
              <span className="eyebrow">只填一次</span>
              <h2>建立你的个人总览</h2>
            </div>
            <button type="button" className="sample-fill" onClick={fillSample}>填入示例</button>
          </div>

          <div className="life-input-grid">
            <label>
              <span>出生日期</span>
              <input type="date" value={date} onChange={(e) => setDate(e.target.value)} required />
            </label>
            <label>
              <span>出生时间</span>
              <input type="time" value={time} onChange={(e) => setTime(e.target.value)} required />
            </label>
            <label className="life-year">
              <span>观察年份</span>
              <input value="2026" readOnly />
            </label>
          </div>

          <div className="life-entry-note">
            <Icon name="shield" size={16} />
            <span>出生资料只保存在当前浏览器本地用于下次预填；当前计算固定使用北京时间 UTC+8。</span>
          </div>

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
            <li>想看全年：进入 2026 流年结构</li>
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
                2026 <strong>{yearTarget.ganzhi || "—"}</strong>
                <span> · </span>
                已绑定 <strong>{evidenceCount}</strong> 条去重 Evidence
              </p>
            </div>
            <span className="life-limited">总览内测</span>
          </header>

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

          <section className="life-section">
            <div className="result-section-heading">
              <div><span>一</span><h2>命盘基础</h2></div>
              <Link className="text-action" href="/bazi-profile">展开八字档案 <Icon name="arrow" size={15} /></Link>
            </div>
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
          </section>

          <div className="life-double">
            <section className="life-section life-focus">
              <div className="result-section-heading">
                <div><span>二</span><h2>2026 流年结构</h2></div>
                <Link className="text-action" href="/yearly-structure">查看详情 <Icon name="arrow" size={15} /></Link>
              </div>
              <div className="life-focus-main">
                <strong>{yearTarget.ganzhi || "—"}</strong>
                <div>
                  <small>流年天干相对日主</small>
                  <b>{yearTarget.stem_ten_god || "—"}</b>
                </div>
              </div>
              <p>这里只复述已验证结构关系，不把单个十神直接解释为全年吉凶。</p>
            </section>

            <section className="life-section life-focus">
              <div className="result-section-heading">
                <div><span>三</span><h2>桃花结构</h2></div>
                <Link className="text-action" href="/romance-structure">查看详情 <Icon name="arrow" size={15} /></Link>
              </div>
              <div className="life-romance-grid">
                <div><small>年支基准目标</small><strong>{romanceTargets.year_branch || "—"}</strong></div>
                <div><small>日支基准目标</small><strong>{romanceTargets.day_branch || "—"}</strong></div>
                <div>
                  <small>2026 年支基准</small>
                  <strong>{activation.year_branch_basis?.matched ? "命中" : "未命中"}</strong>
                </div>
                <div>
                  <small>2026 日支基准</small>
                  <strong>{activation.day_branch_basis?.matched ? "命中" : "未命中"}</strong>
                </div>
              </div>
              <p>命中仅表示咸池固定查表结构成立，不等于恋爱发生或婚姻结果。</p>
            </section>
          </div>

          <section className="life-section">
            <div className="result-section-heading">
              <div><span>四</span><h2>事业财运结构</h2></div>
              <Link className="text-action" href="/career-wealth-structure">查看详情 <Icon name="arrow" size={15} /></Link>
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
                    {active && <em>2026 天干结构</em>}
                  </article>
                );
              })}
            </div>
            <p className="life-inline-note">数量只是位置统计，不代表旺衰，更不是财运或事业评分。</p>
          </section>

          <section className="life-next">
            <div>
              <span className="eyebrow">接下来想看什么</span>
              <h2>从总览继续深入，而不是从头再填。</h2>
            </div>
            <div className="life-next-actions">
              <Link href="/daily-structure">今日结构</Link>
              <Link href="/weekly-structure">本周结构</Link>
              <Link href="/monthly-structure">本月结构</Link>
              <Link href="/yearly-structure">2026 流年</Link>
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
            <p>这是一份结构聚合报告，不是完整人生预测。旺衰、喜用、格局、正缘、收入、健康和事件应期等尚未通过完整规则与证据校验的内容不会在这里补写。</p>
          </section>
        </section>
      )}
    </div>
  );
}
