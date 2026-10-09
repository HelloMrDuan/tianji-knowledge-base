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
  // Legacy container kept only for the unused generic AssetPage component.
  // Real classics/rules/evidence are served by protected governance APIs.
  classics: [],
  rules: [],
  evidence: [],
};
export const adminGroups = [
  {
    title: "工作台",
    items: [
      { label: "仪表盘", icon: "grid", path: "/admin" },
      { label: "Scenario 管理", icon: "layers", path: "/admin/scenarios" },
      { label: "解梦知识研究", icon: "book", path: "/admin/dream-research" },
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
