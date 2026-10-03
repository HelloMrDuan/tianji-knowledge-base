import { useState } from "react";
import { Icon } from "../shared/Icon";
import { Link } from "../shared/router";
import { Diagram } from "./DomainHomePage";
import type { DomainPage } from "./domainPages";
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
                <strong>尚未提交</strong>
              </div>
              <div>
                <span>采用口径</span>
                <strong>随真实结果返回</strong>
              </div>
              <div>
                <span>输入与时区</span>
                <strong>待核对</strong>
              </div>
              <div>
                <span>服务连接</span>
                <strong>设计预览</strong>
              </div>
            </div>
          </section>
          <section className="template-chart">
            <div className="result-section-heading">
              <div>
                <span>二</span>
                <h2>{title}</h2>
              </div>
              <small>固定结构图 · 非计算结果</small>
            </div>
            <div className="template-chart-body">
              <Diagram page={page} />
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
                      : "实际结果尚未接入。结构图仅帮助理解各部分的位置。"}
                </p>
                <Link className="text-action" href={"/" + page.id}>
                  前往资料录入
                  <Icon name="arrow" size={16} />
                </Link>
              </div>
            </div>
            <div className="result-field-slots">
              {fields.map((field, i) => (
                <div key={field}>
                  <span>0{i + 1}</span>
                  <h3>{field}</h3>
                  <p>等待真实结果</p>
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
              <p>{note}</p>
            </section>
          ))}
          <details className="trace-section">
            <summary>
              查看推演过程
              <Icon name="chevron" size={16} />
            </summary>
            <p>
              真实服务接入后，按顺序呈现输入校验、采用版本、规则执行与输出追踪。
            </p>
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
