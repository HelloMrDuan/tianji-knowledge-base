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
  { id: "daily", name: "今日运势 · 结构版", glyph: "今", tagline: "每天回来直接看今天", description: "真实计算当日干支、日干十神与咸池结构命中；当前不输出吉凶或宜忌。", status: "available", href: "/daily-structure", badge: "每日可看" },
  { id: "weekly", name: "本周运势 · 结构版", glyph: "周", tagline: "把七天摊开来看", description: "真实计算周一至周日的日干支、十神结构与咸池命中；不输出周运吉凶。", status: "available", href: "/weekly-structure", badge: "周期内测" },
  { id: "monthly", name: "本月运势 · 结构版", glyph: "月", tagline: "一个月的日结构分布", description: "真实展开整月每日干支、十神结构与咸池命中，并做频次汇总；不输出月运吉凶。", status: "available", href: "/monthly-structure", badge: "周期内测" },
  { id: "yearly", name: "2026 流年结构", glyph: "年", tagline: "年运底座先给你看", description: "真实计算 2026 干支与日主十神结构；不等同于全年吉凶。", status: "available", href: "/yearly-structure", badge: "结构内测" },
  { id: "romance", name: "桃花姻缘", glyph: "缘", tagline: "先看真实桃花结构", description: "年支、日支两套咸池结构分别计算，并检查原局与 2026 流年是否命中；不等同于婚恋吉凶。", status: "available", href: "/romance-structure", badge: "结构内测" },
  { id: "career", name: "事业财运", glyph: "业", tagline: "先看真实事业财运结构", description: "聚合财星、官杀、食伤、印星、比劫的位置，并显示 2026 流年天干十神；不等同于吉凶或收益预测。", status: "available", href: "/career-wealth-structure", badge: "结构内测" },
  { id: "compatibility", name: "缘分合盘 · 结构版", glyph: "合", tagline: "两个人放在一起双向看", description: "真实比较双方四柱、日主互看十神、日主五合、日支六合/六害、传统配偶宫结构位与双向咸池；不输出缘分分数。", status: "available", href: "/compatibility-structure", badge: "双人内测" },
  { id: "question", name: "一事占问", glyph: "问", tagline: "现在就问一件具体的事", description: "先以六爻确定性排盘打通真实闭环。", status: "available", href: "/ask", badge: "先行体验" },
  { id: "dream", name: "AI 解梦", glyph: "梦", tagline: "从梦境意象找线索", description: "等待专门梦境语料与真实 AI 校准。", status: "research", badge: "研究中" },
  { id: "life", name: "人生总览", glyph: "命", tagline: "一次输入，看四条真实主线", description: "聚合八字基础、2026、桃花、事业财运结构；不另造吉凶结论。", status: "available", href: "/life-overview", badge: "聚合内测" },
];

export const featuredScenarioIds = ["question", "romance", "career"];
