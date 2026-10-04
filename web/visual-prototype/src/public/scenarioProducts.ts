export type ScenarioProduct = {
  id: string;
  name: string;
  glyph: string;
  tagline: string;
  description: string;
  status: "available" | "building" | "research";
  href?: string;
  badge?: string;
};

export const scenarioProducts: ScenarioProduct[] = [
  { id: "daily", name: "今日运势", glyph: "今", tagline: "看今天的节奏", description: "日运能力依赖八字生产引擎补齐。", status: "building", badge: "筹备中" },
  { id: "weekly", name: "本周运势", glyph: "周", tagline: "这一周怎么走", description: "周运能力依赖八字与场景规则补齐。", status: "building", badge: "筹备中" },
  { id: "monthly", name: "本月运势", glyph: "月", tagline: "把握当月起伏", description: "月运能力依赖八字与流月规则补齐。", status: "building", badge: "筹备中" },
  { id: "yearly", name: "2026 年运势", glyph: "年", tagline: "提前看全年重点", description: "流年报告待八字确定性引擎完成后开放。", status: "building", badge: "重点建设" },
  { id: "romance", name: "桃花姻缘", glyph: "缘", tagline: "关系与缘分趋势", description: "将组合八字、紫微与审核后的姻缘规则。", status: "building", badge: "重点建设" },
  { id: "career", name: "事业财运", glyph: "业", tagline: "工作、选择与财务节奏", description: "将组合八字、紫微与场景证据。", status: "building", badge: "重点建设" },
  { id: "compatibility", name: "缘分合盘", glyph: "合", tagline: "两个人放在一起看", description: "需要双人输入、八字引擎及合盘规则。", status: "building", badge: "筹备中" },
  { id: "question", name: "一事占问", glyph: "问", tagline: "现在就问一件具体的事", description: "先以六爻确定性排盘打通真实闭环。", status: "available", href: "/ask", badge: "先行体验" },
  { id: "dream", name: "AI 解梦", glyph: "梦", tagline: "从梦境意象找线索", description: "等待专门梦境语料与真实 AI 校准。", status: "research", badge: "研究中" },
  { id: "life", name: "人生全盘", glyph: "命", tagline: "建立长期个人档案", description: "待八字生产引擎与长期场景聚合完成。", status: "building", badge: "筹备中" },
];

export const featuredScenarioIds = ["question", "romance", "career"];
