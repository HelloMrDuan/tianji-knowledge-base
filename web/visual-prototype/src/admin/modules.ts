/** Fictional design fixtures only. These records never enter repository assets. */
export type ModuleRecord = {
  id: string;
  name: string;
  state: string;
  values: string[];
  detail: string;
};
export type ModuleDefinition = {
  id: string;
  title: string;
  description: string;
  columns: string[];
  records: ModuleRecord[];
  guide: [string, string][];
  mode?:
    | "pipeline"
    | "compare"
    | "settings"
    | "editor"
    | "evaluation"
    | "permissions"
    | "logs";
};
const record = (
  id: string,
  name: string,
  state: string,
  values: string[],
  detail: string,
): ModuleRecord => ({ id: "DEMO-" + id, name, state, values, detail });
export const modules: ModuleDefinition[] = [
  {
    id: "scenarios",
    title: "Scenario 管理",
    description: "管理前台场景入口、依赖引擎、开放状态与产品边界；未具备真实能力的场景不得发布。",
    columns: ["前台状态", "依赖能力", "开放策略"],
    records: [
      record(
        "SC001",
        "一事占问",
        "先行体验",
        ["六爻", "jingfang-eight-palaces-v1", "production"],
        "当前第一条真实闭环。前台调用统一 execute API，AI 默认关闭。",
      ),
      record(
        "SC002",
        "桃花姻缘",
        "能力补齐中",
        ["八字 + 紫微", "缺八字生产引擎", "暂不发布"],
        "等待八字确定性引擎与审核后的桃花场景规则，不允许用静态分数替代。",
      ),
      record(
        "SC003",
        "事业财运",
        "能力补齐中",
        ["八字 + 紫微", "缺八字生产引擎", "暂不发布"],
        "和桃花一样先补确定性基础，再形成聚合报告。",
      ),
      record(
        "SC004",
        "AI 解梦",
        "研究中",
        ["专门梦境语料", "RAG + AI", "research"],
        "必须建立独立梦境语料和真实模型评测，不能伪装成确定性排盘。",
      ),
    ],
    guide: [
      ["先看能力", "场景开放状态必须由真实 engine、rules、evidence 能力决定。"],
      ["再看产品", "前台只展示用户可理解的聚合结果，不暴露完整内部知识库。"],
      ["最后开放", "AI 与 research 内容需独立通过评测和人工审核。"],
    ],
  },
  {
    id: "conflicts",
    title: "流派与冲突",
    description: "读取受保护的 Canonical school_conflict 资产；未授权时不返回内部记录。",
    columns: ["差异维度", "候选口径", "处理策略"],
    records: [],
    guide: [
      ["并列比较", "每个口径必须绑定已审核 Evidence，不把分歧抹平成单一结论。"],
      ["生产边界", "bounded 可按明确限制使用；unresolved 继续阻断统一 executable。"],
      ["权限隔离", "真实冲突资产只通过受保护后台只读 API 返回。"],
    ],
  },
  {
    id: "algorithms",
    title: "算法与 Variant",
    description: "展示算法约定、输入边界与变体关系。",
    columns: ["领域", "算法口径", "测试覆盖"],
    records: [
      record(
        "A001",
        "六爻结构",
        "演示配置",
        ["六爻", "京房八宫", "设计占位"],
        "生产实现和测试结果应由真实服务提供。此页不执行计算。",
      ),
      record(
        "A002",
        "奇门转盘",
        "演示配置",
        ["奇门", "茅山转盘", "设计占位"],
        "不同起局法不默默合并。",
      ),
      record(
        "A003",
        "方位定位",
        "演示配置",
        ["风水", "二十四山", "边界待联调"],
        "角度范围、边界和坐向口径单独配置。",
      ),
    ],
    guide: [
      ["输入契约", "明确字段、单位与范围。"],
      ["版本冻结", "记录引擎和 Variant 标识。"],
      ["验证关系", "关联 golden cases 和失败记录。"],
    ],
  },
  {
    id: "providers",
    title: "AI Provider / Model",
    description: "管理解释模型的连接状态、超时和调用边界。",
    mode: "settings",
    columns: ["模型标识", "连接状态", "用途"],
    records: [
      record(
        "P001",
        "解释服务甲",
        "未连接",
        ["DEMO-model-a", "无凭据", "结构说明"],
        "模型名称为演示占位，不构成供应商推荐。",
      ),
      record(
        "P002",
        "解释服务乙",
        "未连接",
        ["DEMO-model-b", "无凭据", "备用解释"],
        "此页面不采集 API Key，也不发起模型请求。",
      ),
      record(
        "P003",
        "本地说明模板",
        "演示配置",
        ["DEMO-template", "无需联网", "缺省提示"],
        "模板只说明界面状态，不能替代真实推演。",
      ),
    ],
    guide: [
      ["凭据管理", "生产密钥应由服务端托管。"],
      ["调用边界", "只允许解释已确认的结构化结果。"],
      ["失败回退", "超时后保留盘面，不生成猜测答案。"],
    ],
  },
  {
    id: "prompts",
    title: "Prompt 版本",
    description: "把解释指令、关联模型与审核版本一起复核。",
    mode: "editor",
    columns: ["解释范围", "版本", "审核状态"],
    records: [
      record(
        "PR001",
        "盘面结构说明",
        "草稿",
        ["已确认字段", "DEMO-v1", "未发布"],
        "只解释提供的盘面字段；依据不足时说明限制，不补造规则。",
      ),
      record(
        "PR002",
        "依据引用说明",
        "待复核",
        ["相关片段", "DEMO-v2", "未发布"],
        "只引用本次允许公开的必要片段。",
      ),
      record(
        "PR003",
        "失败状态说明",
        "草稿",
        ["错误信息", "DEMO-v1", "未发布"],
        "说明失败原因与下一步，不生成替代盘面。",
      ),
    ],
    guide: [
      ["输入限定", "使用已确认结果，禁止猜盘。"],
      ["版本审核", "保存差异与复核理由。"],
      ["评测关联", "发布前关联可复现案例。"],
    ],
  },
  {
    id: "evaluations",
    title: "Eval / Golden Cases",
    description: "将案例输入、预期输出、实际差异和复现方式对应起来。",
    mode: "evaluation",
    columns: ["领域", "预期项目", "结果状态"],
    records: [
      record(
        "EV001",
        "初爻动 · 样例",
        "演示通过",
        ["六爻", "本变卦结构", "非真实跑测"],
        "演示通过仅是状态设计，不代表生产测试结果。",
      ),
      record(
        "EV002",
        "跨日边界 · 样例",
        "演示失败",
        ["紫微", "日期边界", "非真实跑测"],
        "详情展示预期与实际差异的阅读布局。",
      ),
      record(
        "EV003",
        "角度边界 · 样例",
        "未运行",
        ["风水", "扇区归属", "待联调"],
        "真实执行需关联算法版本与运行记录。",
      ),
    ],
    guide: [
      ["固定输入", "资料与时区完整保留。"],
      ["预期来源", "预期值附上审核来源。"],
      ["可复现运行", "连接固定算法版本后再执行。"],
    ],
  },
  {
    id: "failures",
    title: "失败案例",
    description: "按错误阶段整理复现资料、差异与处理进度。",
    columns: ["错误阶段", "影响范围", "跟进状态"],
    records: [
      record(
        "F001",
        "缺失占时字段",
        "待排查",
        ["输入校验", "单次输入", "未指派"],
        "演示失败，缺失字段应定位到表单，不显示过时结果。",
      ),
      record(
        "F002",
        "解释服务超时",
        "待排查",
        ["AI 解释", "解释段落", "保留盘面"],
        "超时时计算结果保留，解释单独显示错误。",
      ),
      record(
        "F003",
        "版本口径不一致",
        "已记录",
        ["版本检查", "结果比较", "需要复核"],
        "记录两侧版本差异，不能自动认定一侧正确。",
      ),
    ],
    guide: [
      ["错误定位", "输入、计算、解释分别诊断。"],
      ["复现记录", "只保存必要且获准的资料。"],
      ["处理闭环", "关联修复、验证与审计。"],
    ],
  },
  {
    id: "users",
    title: "用户与权限",
    description: "按职责查看最小权限与敏感操作边界。",
    mode: "permissions",
    columns: ["角色", "允许范围", "账户状态"],
    records: [
      record(
        "U001",
        "演示审核员",
        "演示角色",
        ["审核", "查看 / 留意见", "无实际账户"],
        "这些身份为虚构示例，不提供认证或真实授权。",
      ),
      record(
        "U002",
        "演示维护员",
        "演示角色",
        ["维护", "配置草稿", "无实际账户"],
        "生产授权需要独立服务与审计。",
      ),
      record(
        "U003",
        "演示访客",
        "演示角色",
        ["只读", "前台工具", "无实际账户"],
        "访客不访问内部原文、凭据或管理资产。",
      ),
    ],
    guide: [
      ["最小权限", "按用途赋权，不默认全开放。"],
      ["敏感操作", "写入、晋级、密钥独立控制。"],
      ["审计关联", "权限变更需要可追溯记录。"],
    ],
  },
  {
    id: "logs",
    title: "API / 系统日志",
    description: "按请求追踪查看处理阶段，敏感资料默认不展示。",
    mode: "logs",
    columns: ["处理阶段", "追踪标识", "耗时"],
    records: [
      record(
        "LG001",
        "输入校验",
        "演示事件",
        ["校验", "DEMO-trace-001", "12 ms（示例）"],
        "字段校验事件；未记录真实出生资料或问题文本。",
      ),
      record(
        "LG002",
        "版本检查",
        "演示事件",
        ["版本", "DEMO-trace-001", "4 ms（示例）"],
        "读取固定版本标识的界面演示。",
      ),
      record(
        "LG003",
        "解释超时",
        "演示事件",
        ["AI", "DEMO-trace-002", "3000 ms（示例）"],
        "虚构错误事件，没有真实请求或模型调用。",
      ),
    ],
    guide: [
      ["请求追踪", "使用 trace 标识关联阶段。"],
      ["数据最小化", "不直接记录出生资料、密钥和长原文。"],
      ["事件分级", "校验、服务和业务错误分别查看。"],
    ],
  },
];
export function moduleForPath(path: string) {
  return modules.find(
    (module) =>
      path === "/admin/" + module.id ||
      path.startsWith("/admin/" + module.id + "/"),
  );
}
