# Benchmark 来源与观察记录

日期：2026-10-02。这里只登记产品研究的公开资料，不向 RAW、quarantine、Canonical 或生产 RAG 导入任何竞品内容；研究来源标记不替代知识库 A/B/C/D 证据等级。

## 访问与版本边界

GitHub 原生 HTTPS/API 路径可读取资料。三个主项目已固定完整 commit；两个补充项目也固定 commit。没有安装、执行其项目或验证其算法测试。公开截图只在工作区研究目录查看，没有复制到本仓库或原型。

| 对象 | 快照 commit | 观察方式 |
| --- | --- | --- |
| Jam0731/MingPan | `c7b314993a7b8820c5dfd1826952961296e4e4b2` | 文档、文本 renderer 源码 |
| Brhiza/mingyu | `396ca00b57f43ca0aad8dd7105f70bfd90d898bc` | 文档、主入口/相关组件/CSS、两张公开静态截图 |
| Sudo-Biao/Chinese-Metaphysics-Platform | `e1b96e0193a2aec44929df442924e9a4aba45418` | 文档、主入口/各域组件/CSS |
| westernwaterfall/yi-basic | `b0f843f74fa5d13997dbffe1f5b3ff03a00c02c9` | 第三方资源目录，仅证明链接线索 |
| joyful00/ai-gua-plugin | `e7783452be18a9d774b5ef12a52ca2902819ed14` | 第三方扩展 README，仅证明其声明/适配页面清单 |

### M-01

[MingPan README](https://github.com/Jam0731/MingPan/blob/c7b314993a7b8820c5dfd1826952961296e4e4b2/README.md)、[API 文档](https://github.com/Jam0731/MingPan/blob/c7b314993a7b8820c5dfd1826952961296e4e4b2/API.md)。支持纯计算、输入参数、data/text 双输出与关联站点的文档结论，不证明关联站点实际 UI。

### M-02

[六爻文本 renderer](https://github.com/Jam0731/MingPan/blob/c7b314993a7b8820c5dfd1826952961296e4e4b2/src/mingpan/output/liuyaoTextRenderer.ts)、[奇门文本 renderer](https://github.com/Jam0731/MingPan/blob/c7b314993a7b8820c5dfd1826952961296e4e4b2/src/mingpan/output/qimenTextRenderer.ts)、[六壬文本 renderer](https://github.com/Jam0731/MingPan/blob/c7b314993a7b8820c5dfd1826952961296e4e4b2/src/mingpan/output/daliurenTextRenderer.ts)。支持字段组织/文本层级结论，不是浏览器交互实测。

### MY-01

[主 App 与路由](https://github.com/Brhiza/mingyu/blob/396ca00b57f43ca0aad8dd7105f70bfd90d898bc/src/App.tsx)、[HomePage](https://github.com/Brhiza/mingyu/blob/396ca00b57f43ca0aad8dd7105f70bfd90d898bc/src/pages/HomePage.tsx)、[WorkspaceShell](https://github.com/Brhiza/mingyu/blob/396ca00b57f43ca0aad8dd7105f70bfd90d898bc/src/components/WorkspaceShell.tsx)、[工作区分类](https://github.com/Brhiza/mingyu/blob/396ca00b57f43ca0aad8dd7105f70bfd90d898bc/src/lib/workspace.ts)。支持入口/导航组织的源码结论。

### MY-02

[出生资料输入](https://github.com/Brhiza/mingyu/blob/396ca00b57f43ca0aad8dd7105f70bfd90d898bc/src/pages/InputPage.PersonForm.tsx)、[占问输入](https://github.com/Brhiza/mingyu/blob/396ca00b57f43ca0aad8dd7105f70bfd90d898bc/src/components/DivinationPanel/DivinationForm.tsx)。支持条件字段与输入流程结论；没有在手机上提交实际请求。

### MY-03

[传统占问盘](https://github.com/Brhiza/mingyu/blob/396ca00b57f43ca0aad8dd7105f70bfd90d898bc/src/components/DivinationPanel/TraditionalDivinationBoard.tsx)、[盘面/助手布局](https://github.com/Brhiza/mingyu/blob/396ca00b57f43ca0aad8dd7105f70bfd90d898bc/src/components/DivinationPanel/DivinationResult.tsx)、[八字结构盘](https://github.com/Brhiza/mingyu/blob/396ca00b57f43ca0aad8dd7105f70bfd90d898bc/src/pages/ResultPage/components/BaziChartBoard.tsx)、[紫微盘](https://github.com/Brhiza/mingyu/blob/396ca00b57f43ca0aad8dd7105f70bfd90d898bc/src/pages/ResultPage/components/ZiweiBoard.tsx)、[能力边界文档](https://github.com/Brhiza/mingyu/blob/396ca00b57f43ca0aad8dd7105f70bfd90d898bc/docs/capabilities.md)。风水在本报告中的能力陈述主要来自文档，未验证在线风水盘面。

### MY-04

[工作区响应式 CSS](https://github.com/Brhiza/mingyu/blob/396ca00b57f43ca0aad8dd7105f70bfd90d898bc/src/workspace.css)、[移动布局判断](https://github.com/Brhiza/mingyu/blob/396ca00b57f43ca0aad8dd7105f70bfd90d898bc/src/lib/responsive-layout.ts)、[公开奇门阶段卡截图](https://github.com/Brhiza/mingyu/blob/396ca00b57f43ca0aad8dd7105f70bfd90d898bc/docs/images/qimen-lifetime-decadal-mobile.png)、[公开八字章节截图](https://github.com/Brhiza/mingyu/blob/396ca00b57f43ca0aad8dd7105f70bfd90d898bc/docs/images/minglu-reliability-mobile.png)。截图中可见移动标题/案例切换/纵向卡片/悬浮动作，不据此判断实际性能、盘面精度或 AI 质量。

### MY-05

[术语释义组件](https://github.com/Brhiza/mingyu/blob/396ca00b57f43ca0aad8dd7105f70bfd90d898bc/src/components/TermExplanationModal/TermExplanationModal.tsx)、[教程页](https://github.com/Brhiza/mingyu/blob/396ca00b57f43ca0aad8dd7105f70bfd90d898bc/src/pages/TutorialPage.tsx)。支持就地释义、分任务说明；并未审核其每条释义、古典文本或 fallback 的正确性。

### MY-06

[AI 工作流文档](https://github.com/Brhiza/mingyu/blob/396ca00b57f43ca0aad8dd7105f70bfd90d898bc/docs/AI%E8%A7%A3%E8%AF%BB%E5%B7%A5%E4%BD%9C%E6%B5%81.md)、[AI 对话组件](https://github.com/Brhiza/mingyu/blob/396ca00b57f43ca0aad8dd7105f70bfd90d898bc/src/components/AiChatPanel.tsx)、[提示词展示](https://github.com/Brhiza/mingyu/blob/396ca00b57f43ca0aad8dd7105f70bfd90d898bc/src/components/PromptPreview.tsx)。工作流中的补查/补算与事实核对是该项目的说明，本研究没有模型实测。

### C-01

[当前 App](https://github.com/Sudo-Biao/Chinese-Metaphysics-Platform/blob/e1b96e0193a2aec44929df442924e9a4aba45418/frontend/src/App.jsx)、[路由辅助](https://github.com/Sudo-Biao/Chinese-Metaphysics-Platform/blob/e1b96e0193a2aec44929df442924e9a4aba45418/frontend/src/router.js)。以实际 App 为准；未把未接入该入口的旧 `components/Layout/Layout.jsx` 当作当前移动导航。

### C-02

[BirthForm](https://github.com/Sudo-Biao/Chinese-Metaphysics-Platform/blob/e1b96e0193a2aec44929df442924e9a4aba45418/frontend/src/components/UI/BirthForm.jsx)、[六爻梯形盘](https://github.com/Sudo-Biao/Chinese-Metaphysics-Platform/blob/e1b96e0193a2aec44929df442924e9a4aba45418/frontend/src/pages/LiuYao/LiuyaoLadderPlate.jsx)、[奇门页](https://github.com/Sudo-Biao/Chinese-Metaphysics-Platform/blob/e1b96e0193a2aec44929df442924e9a4aba45418/frontend/src/pages/QiMen/QiMenPage.jsx)、[紫微页](https://github.com/Sudo-Biao/Chinese-Metaphysics-Platform/blob/e1b96e0193a2aec44929df442924e9a4aba45418/frontend/src/pages/ZiWei/ZiWeiPage.jsx)、[风水页](https://github.com/Sudo-Biao/Chinese-Metaphysics-Platform/blob/e1b96e0193a2aec44929df442924e9a4aba45418/frontend/src/pages/FengShui/FengShuiPage.jsx)、[盘面响应式 CSS](https://github.com/Sudo-Biao/Chinese-Metaphysics-Platform/blob/e1b96e0193a2aec44929df442924e9a4aba45418/frontend/src/styles/plates.css)。只作布局/字段组织参考，不作计算真值。

### C-03

[知识页](https://github.com/Sudo-Biao/Chinese-Metaphysics-Platform/blob/e1b96e0193a2aec44929df442924e9a4aba45418/frontend/src/pages/Knowledge/KnowledgePage.jsx)。支持目录、典籍精读、搜索、分类和等级筛选的源码结论，不代表其全部正文已核校。

### C-04

[AI 面板](https://github.com/Sudo-Biao/Chinese-Metaphysics-Platform/blob/e1b96e0193a2aec44929df442924e9a4aba45418/frontend/src/components/UI/AiInterpretPanel.jsx)、[结构化 AI 输出组件](https://github.com/Sudo-Biao/Chinese-Metaphysics-Platform/blob/e1b96e0193a2aec44929df442924e9a4aba45418/frontend/src/components/UI/StructuredAiOutput.jsx)。支持按需展开/停止/错误状态及 provider/key 传递方式的源码结论，不代表经 citation 校验。

### C-05

[项目 README](https://github.com/Sudo-Biao/Chinese-Metaphysics-Platform/blob/e1b96e0193a2aec44929df442924e9a4aba45418/README.md)、[作者竞品分析](https://github.com/Sudo-Biao/Chinese-Metaphysics-Platform/blob/e1b96e0193a2aec44929df442924e9a4aba45418/docs/COMPETITIVE_ANALYSIS.md)。后者为作者自述，提及问真和传统网站；**其数字评分、精度、下载量和“唯一/行业首创”等不纳入本报告结论**。

### S-01

[yi-basic 资源目录](https://github.com/westernwaterfall/yi-basic/blob/b0f843f74fa5d13997dbffe1f5b3ff03a00c02c9/README.md)。提供问真网页及元亨排盘/论坛链接线索，不证明官方归属或当前页面体验。

### S-02

[独立 china95 AI 插件 README](https://github.com/joyful00/ai-gua-plugin/blob/e7783452be18a9d774b5ef12a52ca2902819ed14/README.md)。说明匹配页面、首问/追问和失败重试；不能将插件归为元亨官方 AI，也未安装插件。

### T-01

本仓库 [API 实现](../../src/tianji_kb/api.py)、[执行层](../../src/tianji_kb/engine.py)、[API 文档](../phase3/API.md)、[Phase 2 报告](../phase2/REPORT.md)、[来源等级](../PHASE1_MODEL.md)、[Phase 4 质量状态](../phase4/QUALITY_STATUS.md)。本次通过现有 FastAPI TestClient 读取 capabilities 并执行六域全部例子，均 HTTP 200、`explanation_status=disabled`；没有调用模型或把测试当作 AI 校准。

## 网站访问阻塞

通过环境原有 HTTPS 代理且保留 TLS 验证，`pcbz.iwzwh.com`、`paipan.china95.net`、`aov.cc` 的只读请求均在代理层返回 403，未取得网页内容。MingPan 的关联体验站 `www.niangxuanzhai.top` 未实测。易百查未确认官方链接，不把猜测域名作为证据。

为直接网页观察，尝试通过正式配置工具保留原名单并增加以上已确认链接线索的精确 host；工具返回 `INVALID_ARGUMENT`：“The draft changed or a secret requirement conflicts.” 重新读取后草稿仍为 revision 8，新增研究域名**未保存成功、未生效**。不绕过代理或替换未知配置。必要域名为 `pcbz.iwzwh.com`、`paipan.china95.net`、`www.china95.net`、`aov.cc`、`www.niangxuanzhai.top`，后续素材/跳转域名只能依据实际请求再核定；不需要竞品账号或模型密钥。

[环境网络技能](skill://plugin_connector_1p_c5b7d5df5d7081918f2c4be5a633ed5d/cloud-environment-runtime/SKILL.md)要求通过正式环境配置流程更改策略。其 [网络说明](skill://plugin_connector_1p_c5b7d5df5d7081918f2c4be5a633ed5d/cloud-environment-runtime/references/networking.md)明确：“An explicit destination-policy denial requires the supported configuration workflow; do not bypass the proxy to reach a blocked destination.” 因此商业产品的直接观察仍是外部阻塞，不用印象补填。

## 后续实测清单

取得官方链接并通过环境配置放通后，使用桌面 1440×900、手机 390×844 和窄屏 360×800 作同一任务对比。先验证公开页面身份/版本；登录/付费/不可用状态单独记录，不能把公开介绍当作付费功能实测。只用合成日期和公开 Golden Case，不上传真实出生资料。

1. 首页到指定术式需几步；能否直接打开深链接并返回；不凭按钮数量估算。
2. 时间输入、时区、公农历、子时、闰月、真太阳时的默认口径与异常提示；区分计算约定和仅展示选项。
3. 八字四柱/运限、六爻逐爻本变、奇门九宫/寄宫、紫微十二宫/四化、六壬四课/三传、风水山向/元运逐项观察；不存在或受限如实标注。
4. 手机键盘、单手返回、文字放大、弹层、盘面横向溢出、点选宫位与返回定位；统计实测，不宣称截图等价。
5. 是否可从盘面字段追到规则、引用/版本；原文与现代解释是否可区分；AI 不可用时盘面能否继续使用。
6. 补充八个维度的直接观察，修订 Benchmark 与设计归因；不直接复制界面素材，也不因本次对比去替换 deterministic engine。
