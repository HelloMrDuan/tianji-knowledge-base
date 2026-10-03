export type DomainId =
  | "bazi"
  | "liuyao"
  | "qimen"
  | "ziwei"
  | "liuren"
  | "yijing"
  | "fengshui";
export type FieldSpec = {
  id: string;
  label: string;
  kind?: "text" | "date" | "time" | "select" | "number" | "textarea";
  placeholder?: string;
  hint?: string;
  required?: boolean;
  options?: string[];
  min?: number;
  max?: number;
  step?: string;
};
export type DomainPage = {
  id: DomainId;
  name: string;
  glyph: string;
  en: string;
  title: string;
  introduction: string;
  formTitle: string;
  formNote: string;
  fields: FieldSpec[];
  sample: Record<string, string>;
  diagram: string;
  steps: [string, string][];
  questions: [string, string][];
  tags: string[];
};
const date: FieldSpec = {
  id: "date",
  label: "日期",
  kind: "date",
  required: true,
};
const time: FieldSpec = {
  id: "time",
  label: "时间",
  kind: "time",
  required: true,
};
const zone: FieldSpec = {
  id: "timezone",
  label: "时区",
  kind: "select",
  options: ["Asia/Shanghai · UTC+8", "UTC · 世界协调时"],
};
const subject: FieldSpec = {
  id: "subject",
  label: "想了解的事情",
  kind: "textarea",
  placeholder: "用一句话写下这次想研究的问题",
  hint: "可留空。资料只留在当前页面，刷新后清除。",
};
const birthFields: FieldSpec[] = [
  {
    id: "calendar",
    label: "历法",
    kind: "select",
    options: ["公历", "农历"],
    hint: "农历另选是否闰月；此页面不做历法换算。",
  },
  { ...date, label: "出生日期" },
  { ...time, label: "出生时间" },
  {
    id: "leapMonth",
    label: "农历月份",
    kind: "select",
    options: ["非闰月", "闰月"],
    hint: "仅在选择农历时显示。",
  },
  {
    id: "gender",
    label: "传统排盘性别口径",
    kind: "select",
    options: ["女", "男"],
    hint: "用于传统算法选项，不代表性格结论。",
  },
  zone,
];
export const domainPages: DomainPage[] = [
  {
    id: "bazi",
    name: "八字",
    glyph: "八",
    en: "FOUR PILLARS",
    title: "四时有序，观其相生。",
    introduction: "从出生资料出发，按年月日时读懂四柱之间的关系。",
    formTitle: "录入出生资料",
    formNote: "先确认历法与时区，再核对出生时刻。",
    fields: [
      ...birthFields,
      {
        id: "place",
        label: "出生地点（选填）",
        placeholder: "例如：江苏南京",
        hint: "本轮不计算真太阳时。",
      },
    ],
    sample: {
      calendar: "公历",
      date: "1996-05-18",
      time: "09:30",
      gender: "女",
      timezone: "Asia/Shanghai · UTC+8",
      place: "江苏南京",
      leapMonth: "非闰月",
    },
    diagram: "四柱结构示意",
    tags: ["出生资料", "四柱关系", "五行结构"],
    steps: [
      ["核对四柱", "先看年、月、日、时的资料是否准确。"],
      ["理解关系", "区分干支、五行与十神的表达。"],
      ["回到依据", "结论应能追溯到采用的规则与版本。"],
    ],
    questions: [
      [
        "不知道出生时间怎么办？",
        "先核对出生记录。不能用随意填入的时刻替代；本页不会据此猜时辰。",
      ],
      [
        "这里会生成命盘吗？",
        "本轮完成输入首页；尚未接入八字计算服务，提交只展示资料摘要。",
      ],
    ],
  },
  {
    id: "liuyao",
    name: "六爻",
    glyph: "爻",
    en: "SIX LINES",
    title: "一问一卦，循象明理。",
    introduction: "记录一次起卦的六个爻值，把动变、世应与依据放回同一张盘面。",
    formTitle: "记录这一次起卦",
    formNote: "从初爻到上爻，自下而上录入。",
    fields: [date, time, zone, subject],
    sample: {
      date: "2026-10-03",
      time: "09:30",
      timezone: "Asia/Shanghai · UTC+8",
      subject: "学习本卦与变卦的结构关系",
    },
    diagram: "六爻录入示意",
    tags: ["手动录爻", "本卦与变卦", "世应位置"],
    steps: [
      ["记下六爻", "保留原始爻值与起卦时间。"],
      ["核对装卦", "把纳甲、六亲、六神和世应分别看清。"],
      ["理解动变", "查看命中规则和本次相关的典籍片段。"],
    ],
    questions: [
      [
        "六个爻值怎么填写？",
        "6 为老阴、7 为少阳、8 为少阴、9 为老阳。第一次所得为初爻，最后一次为上爻。",
      ],
      [
        "可以先看一个结果吗？",
        "可打开已有六爻视觉示例。它是独立固定样例，不是根据当前输入计算的结果。",
      ],
    ],
  },
  {
    id: "qimen",
    name: "奇门遁甲",
    glyph: "门",
    en: "NINE PALACES",
    title: "时落九宫，门星相映。",
    introduction:
      "先选定排盘口径，再记录时刻；九宫、星门与神盘各有自己的层次。",
    formTitle: "设定起局资料",
    formNote: "当前展示口径为茅山派转盘，不混合其他起局法。",
    fields: [
      date,
      time,
      zone,
      {
        id: "school",
        label: "排盘口径",
        kind: "select",
        options: ["茅山派 · 转盘"],
      },
      subject,
    ],
    sample: {
      date: "2026-10-03",
      time: "09:30",
      timezone: "Asia/Shanghai · UTC+8",
      school: "茅山派 · 转盘",
      subject: "学习九宫与星门的对应结构",
    },
    diagram: "九宫空间示意",
    tags: ["茅山转盘", "九宫结构", "星门分层"],
    steps: [
      ["确认时刻", "节气与三元取决于采用的时间规则。"],
      ["读懂盘层", "地盘、天盘、门盘与神盘分层查看。"],
      ["保留口径", "比较结果时，先核对是否为同一派别。"],
    ],
    questions: [
      [
        "能切换拆补或置闰法吗？",
        "本首页只展示茅山转盘口径，不把其他门派算法当作已支持功能。",
      ],
      [
        "九宫图会随时间变化吗？",
        "右侧是固定结构示意；本轮没有排盘，不能把它当作真实星门落宫。",
      ],
    ],
  },
  {
    id: "ziwei",
    name: "紫微斗数",
    glyph: "星",
    en: "TWELVE PALACES",
    title: "星曜入宫，各有其序。",
    introduction: "核对出生资料与安星版本，再理解宫位、星曜和四化的关系。",
    formTitle: "设定安星资料",
    formNote: "历法、闰月与子时边界需要明确。",
    fields: [
      ...birthFields,
      {
        id: "school",
        label: "安星口径",
        kind: "select",
        options: ["默认全书系", "中州派"],
      },
      {
        id: "ratHour",
        label: "晚子时口径",
        kind: "select",
        options: ["按当日", "顺延次日"],
      },
    ],
    sample: {
      calendar: "公历",
      date: "1996-05-18",
      time: "09:30",
      gender: "女",
      timezone: "Asia/Shanghai · UTC+8",
      leapMonth: "非闰月",
      school: "默认全书系",
      ratHour: "按当日",
    },
    diagram: "十二宫结构示意",
    tags: ["十二宫位", "主星与辅星", "四化版本"],
    steps: [
      ["核对身命", "从明确的出生资料和边界口径开始。"],
      ["逐宫阅读", "宫位结构先于星曜解释。"],
      ["区分版本", "四化与安星差异保留各自的流派标记。"],
    ],
    questions: [
      [
        "为什么需要安星口径？",
        "不同版本可能采用不同的安星和四化表，不能合成一个默认唯一答案。",
      ],
      [
        "图中宫位是我的命盘吗？",
        "不是。右侧只展示十二宫的阅读布局，不包含当前输入的计算结果。",
      ],
    ],
  },
  {
    id: "liuren",
    name: "大六壬",
    glyph: "壬",
    en: "FOUR LESSONS",
    title: "四课三传，层层有据。",
    introduction: "从占时资料走向天地盘、四课与三传，每一步保留采用的起法。",
    formTitle: "记录占时资料",
    formNote: "月将、日干支与贵人起法须在排盘时核对。",
    fields: [
      date,
      time,
      zone,
      {
        id: "noble",
        label: "贵人起法",
        kind: "select",
        options: ["引擎默认口径", "异本对照（仅资料选项）"],
      },
      subject,
    ],
    sample: {
      date: "2026-10-03",
      time: "09:30",
      timezone: "Asia/Shanghai · UTC+8",
      noble: "引擎默认口径",
      subject: "理解四课与三传的形成顺序",
    },
    diagram: "四课三传流程示意",
    tags: ["天地盘", "四课三传", "贵人口径"],
    steps: [
      ["确认天地盘", "先核对占时、月将和干支。"],
      ["审视四课", "逐课区分上下关系和生克。"],
      ["循序取传", "记录所用宗门与特殊条件，不跳过推演过程。"],
    ],
    questions: [
      [
        "贵人起法可以混用吗？",
        "不能。不同版本应分别记录，右侧示意不代表任何起法已执行。",
      ],
      [
        "会自动选择九宗门吗？",
        "这轮是首页设计；不在浏览器中猜初传或生成三传，须待真实引擎联调。",
      ],
    ],
  },
  {
    id: "yijing",
    name: "周易",
    glyph: "易",
    en: "BOOK OF CHANGES",
    title: "观卦知变，回到本义。",
    introduction:
      "选择一卦，从卦名、上下卦与爻位认识结构；原典阅读与占断保持区分。",
    formTitle: "选择要研究的卦",
    formNote: "先选卦，再记录需要对照的爻位。",
    fields: [
      {
        id: "hexagram",
        label: "六十四卦",
        kind: "select",
        options: [
          "乾",
          "坤",
          "屯",
          "蒙",
          "需",
          "讼",
          "师",
          "比",
          "小畜",
          "履",
          "泰",
          "否",
          "同人",
          "大有",
          "谦",
          "豫",
          "随",
          "蛊",
          "临",
          "观",
          "噬嗑",
          "贲",
          "剥",
          "复",
          "无妄",
          "大畜",
          "颐",
          "大过",
          "坎",
          "离",
          "咸",
          "恒",
          "遁",
          "大壮",
          "晋",
          "明夷",
          "家人",
          "睽",
          "蹇",
          "解",
          "损",
          "益",
          "夬",
          "姤",
          "萃",
          "升",
          "困",
          "井",
          "革",
          "鼎",
          "震",
          "艮",
          "渐",
          "归妹",
          "丰",
          "旅",
          "巽",
          "兑",
          "涣",
          "节",
          "中孚",
          "小过",
          "既济",
          "未济",
        ],
      },
      {
        id: "line",
        label: "爻位",
        kind: "select",
        options: ["全卦", "初爻", "二爻", "三爻", "四爻", "五爻", "上爻"],
      },
      {
        id: "focus",
        label: "研究方向",
        kind: "select",
        options: ["卦象结构", "动爻关系", "错综互卦"],
      },
      {
        ...subject,
        label: "阅读笔记（选填）",
        placeholder: "记下想对照的问题或爻位",
      },
    ],
    sample: {
      hexagram: "乾",
      line: "初爻",
      focus: "卦象结构",
      subject: "认识初爻与卦象的阅读顺序",
    },
    diagram: "八卦组合示意",
    tags: ["六十四卦", "卦爻结构", "错综互变"],
    steps: [
      ["辨上下卦", "六爻由上下两个三爻卦组合。"],
      ["定位爻位", "从初爻到上爻，对照所选位置。"],
      ["认识关系", "区分变卦、错卦、综卦与互卦，不混淆名称。"],
    ],
    questions: [
      [
        "这里提供完整古籍浏览吗？",
        "不提供内部知识库入口。这是工具首页，正式结果只展示本次操作允许公开的相关内容。",
      ],
      [
        "选卦后会自动占断吗？",
        "不会。此页面完成选卦与资料确认，不生成现实吉凶结论。",
      ],
    ],
  },
  {
    id: "fengshui",
    name: "风水",
    glyph: "山",
    en: "DIRECTION & SPACE",
    title: "辨山识向，理解方位。",
    introduction:
      "从一项可靠的方位测量开始，把坐向、角度与所采用的体系分开记录。",
    formTitle: "记录方位资料",
    formNote: "北为 0°，顺时针增加；请使用实际测量资料。",
    fields: [
      {
        id: "bearing",
        label: "测量角度（°）",
        kind: "number",
        required: true,
        min: 0,
        max: 359.99,
        step: "0.01",
        placeholder: "0 至 359.99",
      },
      {
        id: "orientation",
        label: "测量对象",
        kind: "select",
        options: ["朝向", "坐向"],
      },
      {
        id: "school",
        label: "研究体系",
        kind: "select",
        options: ["二十四山 · 方位定位"],
      },
      {
        id: "location",
        label: "测量位置（选填）",
        placeholder: "例如：客厅中心，朝门外测量",
      },
      {
        id: "note",
        label: "现场笔记（选填）",
        kind: "textarea",
        placeholder: "记录测量方式与环境，便于复核",
      },
    ],
    sample: {
      bearing: "180",
      orientation: "朝向",
      school: "二十四山 · 方位定位",
      location: "客厅中心，朝门外",
      note: "演示资料，不代表实测。",
    },
    diagram: "方位罗盘示意",
    tags: ["二十四山", "测量角度", "坐向区分"],
    steps: [
      ["明确测量", "记录角度、测量位置和所指方向。"],
      ["定位扇区", "查看二十四山及扇区边界口径。"],
      ["区分体系", "三合、玄空、八宅等规则不得静默混用。"],
    ],
    questions: [
      [
        "可以生成完整玄空宅盘吗？",
        "本首页仅设计二十四山方位输入，不承诺山星、向星或完整宅盘。",
      ],
      [
        "0°和360°怎样填写？",
        "本表单采用 [0, 360) 范围，正北填 0°。页面只校验输入，未做山向计算。",
      ],
    ],
  },
];
export function getDomainPage(path: string) {
  return domainPages.find((page) => path === "/" + page.id);
}
