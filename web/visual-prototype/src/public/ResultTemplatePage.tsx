import { useEffect, useState } from "react";
import { Icon } from "../shared/Icon";
import { Link } from "../shared/router";
import { Diagram, hexText, lessonText } from "./DomainHomePage";
import type { DomainPage } from "./domainPages";
import {
  ApiError,
  executeFengshui,
  executeLiuren,
  executeQimen,
  executeYijing,
  executeZiwei,
} from "./api";
import type { ExecuteResponse } from "./api";
import "./pages.css";

const resultSections: Record<string, [string, string[]]> = {
  bazi: ["四柱关系", ["四柱与藏干", "五行分布", "十神关系", "起运口径"]],
  qimen: ["九宫盘层", ["地盘与天盘", "星盘与门盘", "神盘", "值符与值使"]],
  ziwei: ["十二宫星曜", ["命宫与身宫", "主星与辅星", "四化版本", "大限口径"]],
  liuren: ["四课三传", ["天地盘", "四课", "三传", "贵人与天将"]],
  yijing: ["卦爻结构", ["本卦与上下卦", "爻位", "错卦与综卦", "互卦与变卦"]],
  fengshui: ["方位定位", ["测量角度", "坐向关系", "二十四山", "扇区边界"]],
};
export function ResultTemplatePage({ page }: { page: DomainPage }) {
  const [state, setState] = useState("empty");
  const [title, fields] = resultSections[page.id];
  // B012: 周易 / 六壬结果页在带参数时进入真实模式：据 URL 参数向真实
  // 后端请求计算并渲染；无参数时为诚实空态，失败时为诚实失败态，
  // 绝不把门禁拒绝或空态包装成已计算，也绝不编造吉凶结论。
  // B014: 紫微 / 奇门 / 风水结果页同样接通。
  const connected =
    page.id === "yijing" ||
    page.id === "liuren" ||
    page.id === "ziwei" ||
    page.id === "qimen" ||
    page.id === "fengshui";
  const search = connected ? new URLSearchParams(window.location.search) : null;
  let yijingInput: { bits: string; changing_lines: number[] } | null = null;
  let liurenInput: { value: string } | null = null;
  let ziweiInput: { value: string; year_boundary: "lunar-new-year" } | null =
    null;
  let qimenInput: { value: string } | null = null;
  let fengshuiInput: { degrees: number } | null = null;
  let paramError = "";
  if (page.id === "yijing" && search) {
    const bits = search.get("bits") || "";
    const changingRaw = search.get("changing_lines") || "";
    if (!/^[01]{6}$/.test(bits)) {
      paramError = "卦象参数不完整，请返回录入页重新提交。";
    } else {
      yijingInput = {
        bits,
        changing_lines: changingRaw
          .split(",")
          .map((n) => Number(n))
          .filter((n) => n >= 1 && n <= 6),
      };
    }
  }
  if (page.id === "liuren" && search) {
    const value = search.get("value") || "";
    if (!value) {
      paramError = "占时参数不完整，请返回录入页重新提交。";
    } else {
      liurenInput = { value };
    }
  }
  if (page.id === "ziwei" && search) {
    const value = search.get("value") || "";
    if (!value || search.get("year_boundary") !== "lunar-new-year") {
      paramError = "安星参数不完整，请返回录入页重新提交。";
    } else {
      ziweiInput = { value, year_boundary: "lunar-new-year" };
    }
  }
  if (page.id === "qimen" && search) {
    const value = search.get("value") || "";
    if (!value) {
      paramError = "占时参数不完整，请返回录入页重新提交。";
    } else {
      qimenInput = { value };
    }
  }
  if (page.id === "fengshui" && search) {
    const raw = search.get("degrees") || "";
    const degrees = Number(raw);
    if (
      raw === "" ||
      !Number.isFinite(degrees) ||
      degrees < 0 ||
      degrees >= 360
    ) {
      paramError = "角度参数不完整，请返回录入页重新提交。";
    } else {
      fengshuiInput = { degrees };
    }
  }
  const realMode =
    connected &&
    (yijingInput !== null ||
      liurenInput !== null ||
      ziweiInput !== null ||
      qimenInput !== null ||
      fengshuiInput !== null);
  const [result, setResult] = useState<ExecuteResponse | null>(null);
  const [fetchError, setFetchError] = useState(paramError);
  useEffect(() => {
    if (!realMode) return;
    let cancelled = false;
    const request = yijingInput
      ? executeYijing(yijingInput)
      : liurenInput
        ? executeLiuren(liurenInput)
        : ziweiInput
          ? executeZiwei(ziweiInput)
          : qimenInput
            ? executeQimen(qimenInput)
            : executeFengshui(fengshuiInput as { degrees: number });
    request
      .then((data) => {
        if (!cancelled) setResult(data);
      })
      .catch((err) => {
        if (!cancelled) {
          setResult(null);
          setFetchError(
            err instanceof ApiError
              ? err.message
              : "计算请求失败，请稍后重试。",
          );
        }
      });
    return () => {
      cancelled = true;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);
  // 真实模式下的字段槽位：只填后端实际返回的结构；贵人与天将一栏
  // 填后端返回的限界声明本身，绝不虚构天将排布。
  function slotValue(field: string): string {
    if (!result) return "";
    const chart = result.chart;
    if (page.id === "yijing") {
      if (field === "本卦与上下卦") return hexText(chart.original);
      if (field === "爻位")
        return chart.change && chart.change.binary !== chart.original?.binary
          ? `变卦 ${hexText(chart.change)}`
          : "全卦，无变爻";
      if (field === "错卦与综卦")
        return `错卦 ${hexText(chart.opposite)} · 综卦 ${hexText(chart.inverse)}`;
      if (field === "互卦与变卦")
        return `互卦 ${hexText(chart.nuclear)} · 变卦 ${hexText(chart.change)}`;
      return "";
    }
    if (page.id === "ziwei") {
      if (field === "命宫与身宫")
        return `命宫 ${chart.life_palace || "—"} · 身宫 ${chart.body_palace || "—"} · 命宫干支 ${chart.life_ganzhi || "—"} · ${chart.bureau ? `${chart.bureau.element}${chart.bureau.number}局` : "—"}`;
      if (field === "主星与辅星") {
        const major = chart.major_stars
          ? Object.entries(chart.major_stars)
              .map(([star, branch]) => `${star}→${branch}`)
              .join(" · ")
          : "";
        const aux = chart.auxiliary_stars
          ? Object.entries(chart.auxiliary_stars)
              .map(([star, branch]) => `${star}→${branch}`)
              .join(" · ")
          : "";
        return `主星 ${major}；辅星 ${aux}`;
      }
      if (field === "四化版本") {
        const four = chart.four_transformations
          ? Object.entries(chart.four_transformations)
              .map(([kind, star]) => `${kind}→${star}`)
              .join(" · ")
          : "";
        return `${chart.mutagen_variant || "—"} · ${four}；${chart.mutagen_evidence || ""}`;
      }
      if (field === "大限口径") return chart.input_scope || "";
      return "";
    }
    if (page.id === "qimen") {
      if (field === "地盘与天盘") {
        const earth = chart.earth_plate
          ? Object.entries(chart.earth_plate)
              .map(([palace, stem]) => `${palace}→${stem}`)
              .join(" · ")
          : "";
        const sky = chart.sky_plate
          ? Object.entries(chart.sky_plate)
              .map(([palace, stem]) => `${palace}→${stem}`)
              .join(" · ")
          : "";
        return `${chart.dun || "—"} · 第${chart.bureau || "—"}局 · ${chart.yuan || "—"} · 节气 ${chart.calendar?.solar_term || "—"}；地盘 ${earth}；天盘 ${sky}`;
      }
      if (field === "星盘与门盘") {
        const stars = chart.star_positions
          ? Object.entries(chart.star_positions)
              .map(([star, palace]) => `${star}→${palace}`)
              .join(" · ")
          : "";
        const doors = chart.door_positions
          ? Object.entries(chart.door_positions)
              .map(([door, palace]) => `${door}→${palace}`)
              .join(" · ")
          : "";
        return `星 ${stars}；门 ${doors}`;
      }
      if (field === "神盘")
        return chart.deity_positions
          ? Object.entries(chart.deity_positions)
              .map(([deity, palace]) => `${deity}→${palace}`)
              .join(" · ")
          : "";
      if (field === "值符与值使")
        return `值符 ${(chart.chief_star?.names || []).join(" / ") || "—"}（${chart.chief_star?.palace || "—"}宫） · 值使 ${chart.chief_door?.name || "—"}（${chart.chief_door?.palace || "—"}宫）；${chart.center_star_policy || ""}`;
      return "";
    }
    if (page.id === "fengshui") {
      if (field === "测量角度") return `${chart.degrees ?? "—"}°`;
      if (field === "坐向关系")
        return `对向 ${chart.opposite || "—"} · 卦 ${chart.trigram || "—"}（${chart.trigram_element || "—"}）`;
      if (field === "二十四山")
        return `${chart.mountain || "—"}（${chart.mountain_element || "—"}）`;
      if (field === "扇区边界")
        return `按半开区间落 ${chart.mountain || "—"}山；绝对元运未接入生产`;
      return "";
    }
    if (field === "天地盘")
      return chart.sky_plate
        ? Object.entries(chart.sky_plate)
            .map(([earth, sky]) => `${earth}→${sky}`)
            .join(" · ")
        : "";
    if (field === "四课")
      return (chart.four_lessons || [])
        .map(
          (lesson: Record<string, unknown>, i: number) =>
            `${["一", "二", "三", "四"][i]}课 ${lessonText(lesson)}`,
        )
        .join(" · ");
    if (field === "三传")
      return `${chart.method || ""} · 初传 ${chart.transmissions?.[0] || "—"} · 中传 ${chart.transmissions?.[1] || "—"} · 末传 ${chart.transmissions?.[2] || "—"}`;
    if (field === "贵人与天将")
      return (chart.limitations || []).join("；") || "天将未实现";
    return "";
  }
  return (
    <div className="template-result">
      <div className="breadcrumb">
        <Link href={"/" + page.id}>{page.name}</Link>
        <Icon name="chevron" size={12} />
        <span>结果页设计</span>
      </div>
      <header className="domain-heading">
        <div className="domain-seal">{page.glyph}</div>
        <div>
          <span className="eyebrow">{page.en} · RESULT</span>
          <h1>{page.name} · 结果工作台</h1>
          <p>结构、解释与依据分层阅读，每一步都可回溯。</p>
        </div>
        <Link className="button outlined" href={"/" + page.id}>
          重新录入
          <Icon name="arrow" size={16} />
        </Link>
      </header>
      {!realMode && (
      <div className="preview-state-bar">
        <span>设计状态预览</span>
        <div role="group" aria-label="结果状态">
          {[
            ["empty", "等待资料"],
            ["loading", "计算中"],
            ["error", "计算失败"],
          ].map(([id, label]) => (
            <button
              key={id}
              aria-pressed={state === id}
              onClick={() => setState(id)}
            >
              {label}
            </button>
          ))}
        </div>
      </div>
      )}
      <div className="result-layout">
        <div className="result-content">
          <section className="result-basic">
            <div className="result-section-heading">
              <div>
                <span>一</span>
                <h2>基础信息</h2>
              </div>
            </div>
            <div className="basic-grid">
              <div>
                <span>资料状态</span>
                <strong>
                  {realMode && result
                    ? "已计算"
                    : realMode && fetchError
                      ? "计算失败"
                      : realMode
                        ? "计算中"
                        : "尚未提交"}
                </strong>
              </div>
              <div>
                <span>采用口径</span>
                <strong>
                  {realMode && result ? result.variant : "随真实结果返回"}
                </strong>
              </div>
              <div>
                <span>
                  {page.fields.some((field) => field.id === "timezone")
                    ? "固定时区"
                    : "输入资料"}
                </span>
                <strong>
                  {page.fields.some((field) => field.id === "timezone")
                    ? "北京时间（UTC+8）"
                    : "待核对"}
                </strong>
              </div>
              <div>
                <span>服务连接</span>
                <strong>
                  {realMode && result
                    ? "真实后端"
                    : realMode
                      ? "真实后端请求中"
                      : "设计预览"}
                </strong>
              </div>
            </div>
          </section>
          <section className="template-chart">
            <div className="result-section-heading">
              <div>
                <span>二</span>
                <h2>{title}</h2>
              </div>
              <small>
                {realMode ? "真实计算结果" : "固定结构图 · 非计算结果"}
              </small>
            </div>
            <div className="template-chart-body">
              <Diagram page={page} />
              {realMode && result ? (
                <div className="template-state" role="status">
                  <span className="eyebrow">真实计算完成</span>
                  <h3>
                    {page.id === "yijing"
                      ? `本卦 ${hexText(result.chart.original)}`
                      : page.id === "liuren"
                        ? `月将 ${result.chart.month_general?.name || "—"}（${result.chart.month_general?.branch || "—"}） · 取传 ${result.chart.method || "—"} · 初传 ${result.chart.transmissions?.[0] || "—"} · 中传 ${result.chart.transmissions?.[1] || "—"} · 末传 ${result.chart.transmissions?.[2] || "—"}`
                        : page.id === "ziwei"
                          ? `命宫 ${result.chart.life_palace || "—"} · 身宫 ${result.chart.body_palace || "—"} · ${result.chart.bureau ? `${result.chart.bureau.element}${result.chart.bureau.number}局` : "—"}`
                          : page.id === "qimen"
                            ? `${result.chart.dun || "—"}第${result.chart.bureau || "—"}局 · 值符 ${(result.chart.chief_star?.names || []).join(" / ") || "—"} · 值使 ${result.chart.chief_door?.name || "—"}`
                            : `${result.chart.degrees ?? "—"}° · ${result.chart.mountain || "—"}（${result.chart.mountain_element || "—"}） · 对向 ${result.chart.opposite || "—"}`}
                  </h3>
                  <p>
                    {page.id === "yijing"
                      ? "仅卦象结构，不作吉凶推断。"
                      : page.id === "liuren"
                        ? (result.chart.limitations || []).join("；")
                        : (result.limitations || []).join("；")}
                  </p>
                  <Link className="text-action" href={"/" + page.id}>
                    前往资料录入
                    <Icon name="arrow" size={16} />
                  </Link>
                </div>
              ) : realMode ? (
                <div className="template-state" role="status">
                  <span className="eyebrow">
                    {fetchError ? "暂未取得结果" : "正在计算"}
                  </span>
                  <h3>
                    {fetchError ? "计算未完成，请保留原始资料" : "等待计算结果"}
                  </h3>
                  <p>
                    {fetchError
                      ? "失败时不展示旧盘面或生成替代结论。可返回录入页重新核对。"
                      : "正在向真实后端请求计算结果，请稍候。"}
                  </p>
                  <Link className="text-action" href={"/" + page.id}>
                    前往资料录入
                    <Icon name="arrow" size={16} />
                  </Link>
                </div>
              ) : (
                <div className="template-state" role="status">
                  <span className="eyebrow">
                    {state === "error"
                      ? "暂未取得结果"
                      : state === "loading"
                        ? "正在核对输入"
                        : "从准确的资料开始"}
                  </span>
                  <h3>
                    {state === "error"
                      ? "计算未完成，请保留原始资料"
                      : state === "loading"
                        ? "等待计算结果"
                        : "这里将呈现你的盘面"}
                  </h3>
                  <p>
                    {state === "error"
                      ? "失败时不展示旧盘面或生成替代结论。可返回录入页重新核对。"
                      : state === "loading"
                        ? "此状态用于展示等待布局，没有发起计算请求。"
                        : connected
                          ? "尚未提交资料。请返回录入页填写后提交，方可看到真实计算结果。"
                          : "实际结果尚未接入。结构图仅帮助理解各部分的位置。"}
                  </p>
                  <Link className="text-action" href={"/" + page.id}>
                    前往资料录入
                    <Icon name="arrow" size={16} />
                  </Link>
                </div>
              )}
            </div>
            <div className="result-field-slots">
              {fields.map((field, i) => (
                <div key={field}>
                  <span>0{i + 1}</span>
                  <h3>{field}</h3>
                  <p>
                    {realMode && result
                      ? slotValue(field)
                      : realMode && fetchError
                        ? "计算失败，未生成结果"
                        : realMode
                          ? "正在计算……"
                          : "等待真实结果"}
                  </p>
                </div>
              ))}
            </div>
          </section>
          {[
            ["三", "结构摘要", "待计算完成后展示本次盘面的结构说明。"],
            [
              "四",
              "规则与依据",
              "只展示本次结果命中的规则及允许公开的必要片段。",
            ],
            ["五", "AI 解读", "解读服务尚未接入。先核对盘面，再阅读解释。"],
          ].map(([number, name, note]) => (
            <section className="result-placeholder" key={number}>
              <div className="result-section-heading">
                <div>
                  <span>{number}</span>
                  <h2>{name}</h2>
                </div>
                <small>待接入</small>
              </div>
              <p>
                {realMode && result && number === "三"
                  ? `采用口径：${result.variant}。${(result.limitations || []).join("；")}`
                  : note}
              </p>
            </section>
          ))}
          <details className="trace-section">
            <summary>
              查看推演过程
              <Icon name="chevron" size={16} />
            </summary>
            {realMode && result ? (
              <ol>
                {result.trace.map((step, i) => (
                  <li key={i}>
                    {step.step || `计算步骤 ${String(i + 1).padStart(2, "0")}`}
                  </li>
                ))}
              </ol>
            ) : (
              <p>
                真实服务接入后，按顺序呈现输入校验、采用版本、规则执行与输出追踪。
              </p>
            )}
          </details>
        </div>
        <aside className="template-aside">
          <span className="eyebrow">阅读次序</span>
          <h2>先核盘，后释义。</h2>
          {page.steps.map(([name, note], i) => (
            <div key={name}>
              <span>0{i + 1}</span>
              <h3>{name}</h3>
              <p>{note}</p>
            </div>
          ))}
          <Link className="text-action" href="/history">
            历史记录
            <Icon name="clock" size={16} />
          </Link>
          <p className="sample-note">
            暂无真实推演记录。输入资料不会自动保存。
          </p>
        </aside>
      </div>
    </div>
  );
}
