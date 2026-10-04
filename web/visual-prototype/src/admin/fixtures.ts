/** Fictional admin display records. They never enter the knowledge base or any index. */
export type AssetKind = "classics" | "rules" | "evidence";
export type AssetRecord = {
  id: string;
  name: string;
  domain: string;
  state: string;
  level: string;
  detail: string;
  secondary: string;
  count: string;
  updated: string;
};
export const assets: Record<AssetKind, AssetRecord[]> = {
  classics: [
    {
      id: "DEMO-B001",
      name: "增删卜易",
      domain: "六爻",
      state: "已审选段",
      level: "C",
      detail: "本轮演示记录 · 非真实资产",
      secondary: "动变章、世应章等",
      count: "12 章",
      updated: "10-02 09:12",
    },
    {
      id: "DEMO-B002",
      name: "卜筮正宗",
      domain: "六爻",
      state: "待复核",
      level: "C",
      detail: "章节校核的视觉示例",
      secondary: "纳甲、六亲相关章节",
      count: "18 章",
      updated: "10-02 08:36",
    },
    {
      id: "DEMO-B003",
      name: "周易",
      domain: "周易",
      state: "已审选段",
      level: "C",
      detail: "卦爻正文的视觉示例",
      secondary: "卦辞、爻辞",
      count: "64 卦",
      updated: "10-01 16:20",
    },
    {
      id: "DEMO-B004",
      name: "紫微斗数全书",
      domain: "紫微",
      state: "待复核",
      level: "C",
      detail: "保留安星疑文的视觉示例",
      secondary: "安星相关选段",
      count: "8 章",
      updated: "10-01 14:45",
    },
    {
      id: "DEMO-B005",
      name: "六壬大全",
      domain: "六壬",
      state: "已审选段",
      level: "C",
      detail: "九宗门章节的视觉示例",
      secondary: "取传相关选段",
      count: "9 章",
      updated: "09-30 11:05",
    },
    {
      id: "DEMO-B006",
      name: "待核电子文本",
      domain: "风水",
      state: "隔离",
      level: "D",
      detail: "隔离资产的虚构占位记录，无实际原文",
      secondary: "待核版本与来源",
      count: "—",
      updated: "09-30 10:30",
    },
  ],
  rules: [],
  evidence: [],
};
export const adminGroups = [
  {
    title: "工作台",
    items: [
      { label: "仪表盘", icon: "grid", path: "/admin" },
      { label: "Scenario 管理", icon: "layers", path: "/admin/scenarios" },
    ],
  },
  {
    title: "知识资产",
    items: [
      { label: "古籍管理", icon: "book", path: "/admin/classics" },
      { label: "章节管理", icon: "file", path: "/admin/chapters" },
      { label: "术语管理", icon: "file", path: "/admin/terms" },
      { label: "规则管理", icon: "layers", path: "/admin/rules" },
      { label: "Evidence 管理", icon: "shield", path: "/admin/evidence" },
    ],
  },
  {
    title: "审核与溯源",
    items: [
      { label: "来源管理", icon: "external", path: "/admin/sources" },
      {
        label: "RAW / Quarantine / Canonical",
        icon: "layers",
        path: "/admin/layers",
      },
      { label: "流派与冲突", icon: "layers", path: "/admin/conflicts" },
    ],
  },
  {
    title: "计算与解释",
    items: [
      { label: "算法与 Variant", icon: "settings", path: "/admin/algorithms" },
      {
        label: "AI Provider / Model",
        icon: "settings",
        path: "/admin/providers",
      },
      { label: "Prompt 版本", icon: "file", path: "/admin/prompts" },
      {
        label: "Eval / Golden Cases",
        icon: "check",
        path: "/admin/evaluations",
      },
      { label: "失败案例", icon: "file", path: "/admin/failures" },
    ],
  },
  {
    title: "系统",
    items: [
      { label: "用户与权限", icon: "shield", path: "/admin/users" },
      { label: "API / 系统日志", icon: "file", path: "/admin/logs" },
    ],
  },
];
