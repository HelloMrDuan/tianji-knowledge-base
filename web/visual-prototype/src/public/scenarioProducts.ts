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
  { id: "bazi-profile", name: "八字基础档案", glyph: "八", tagline: "先看清自己的四柱结构", description: "真实计算四柱、日主、十神、藏干，并返回规则与典籍依据。", status: "available", href: "/bazi-profile", badge: "真实可用" },
  { id: "daily", name: "今日运势", glyph: "今", tagline: "看今天的节奏", description: "日运能力依赖八字生产引擎补齐。", status: "building", badge: "筹备中" },
  { id: "weekly", name: "本周运势", glyph: "周", tagline: "这一周怎么走", description: "周运能力依赖八字与场景规则补齐。", status: "building", badge: "筹备中" },
  { id: "monthly", name: "本月运势", glyph: "月", tagline: "把握当月起伏", description: "月运能力依赖八字与流月规则补齐。", status: "building", badge: "筹备中" },
  { id: "yearly", name: "2026 流年结构", glyph: "年", tagline: "年运底座先给你看", description: "真实计算 2026 干支与日主十神结构；不等同于全年吉凶。", status: "available", href: "/yearly-structure", badge: "结构内测" },
  { id: "romance", name: "桃花姻缘", glyph: "缘", tagline: "先看真实桃花结构", description: "年支、日支两套咸池结构分别计算，并检查原局与 2026 流年是否命中；不等同于婚恋吉凶。", status: "available", href: "/romance-structure", badge: "结构内测" },
  { id: "career", name: "事业财运", glyph: "业", tagline: "工作、选择与财务节奏", description: "将组合八字、紫微与场景证据。", status: "building", badge: "重点建设" },
  { id: "compatibility", name: "缘分合盘", glyph: "合", tagline: "两个人放在一起看", description: "需要双人输入、八字引擎及合盘规则。", status: "building", badge: "筹备中" },
  { id: "question", name: "一事占问", glyph: "问", tagline: "现在就问一件具体的事", description: "先以六爻确定性排盘打通真实闭环。", status: "available", href: "/ask", badge: "先行体验" },
  { id: "dream", name: "AI 解梦", glyph: "梦", tagline: "从梦境意象找线索", description: "等待专门梦境语料与真实 AI 校准。", status: "research", badge: "研究中" },
  { id: "life", name: "人生全盘", glyph: "命", tagline: "建立长期个人档案", description: "基础四柱档案已可用；完整人生报告仍需更多规则、证据与长期场景聚合。", status: "building", badge: "筹备中" },
];

export const featuredScenarioIds = ["question", "romance", "career"];
