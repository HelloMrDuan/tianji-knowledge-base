# 天机 · 场景化产品 Web

这一目录已经从“纯视觉原型”演进为场景化产品前端。当前不是所有页面都属于生产能力，但主产品链路已经开始真实调用后端 API，不能再按静态 Demo 理解。

## 当前真实链路

以下场景已经接入确定性后端，不使用 Mock 代替计算：

- 八字基础档案：`/bazi-profile`
- 一事占问：`/ask`
- 今日结构：`/daily-structure`
- 本周结构：`/weekly-structure`
- 本月结构：`/monthly-structure`
- 2026 流年结构：`/yearly-structure`
- 桃花姻缘结构：`/romance-structure`
- 事业财运结构：`/career-wealth-structure`
- 人生总览：`/life-overview`
- 缘分合盘：`/compatibility-structure`

前端通过现有 `/api/v1/execute` 与 `/api/v1/scenarios/execute` 调用正式确定性引擎。后端失败时页面明确报错，不用静态盘面冒充真实结果。

AI 自动解释仍未作为公开生产能力开启。当前场景计算以确定性规则、RuleMatch、Evidence 与 Trace 为准。

## 历史与收藏

前台“历史记录 / 收藏”不再使用固定六爻 Demo 冒充用户记录。

- 只有真实 API / Scenario Engine 成功返回后才写入历史；
- 记录只保存在当前浏览器 `localStorage`，当前没有账号级云同步；
- 历史只保存场景、结果摘要、时间、结果版本和收藏状态；
- 不额外复制出生时间，不保存一事占问的用户问题原文，也不保存完整 Evidence / Trace；
- 最多保留最近 50 条；
- 静态六爻视觉示例明确标记为 Demo，不进入真实历史或收藏。


## 能力边界

“今日 / 本周 / 本月 / 流年 / 桃花 / 事业财运 / 合盘”等当前均属于结构化产品，不等同于完整吉凶预测。不得从前端自行补出旺衰、喜用神、格局、正缘时间、结婚时间、收益预测、健康判断、投资建议或事件应期。

管理后台仍以知识治理与产品管理界面为主，部分数据是展示/设计资料；不能把尚未接入真实写服务的后台操作宣称为已落库能力。

## 本地运行

```bash
cd web/visual-prototype
npm ci
npm run dev
```

环境：Node.js 22.12+ 或 24、npm。构建使用固定版本的 React、TypeScript、Vite。

Vite 开发环境会通过项目现有代理访问后端 API。需要真实体验时，应同时启动后端服务；不要为“页面能显示”而退回 Mock。

```bash
npm run build
npx playwright install chromium
npm test
```

已有系统 Chromium 的云环境可直接执行：

```bash
PROTOTYPE_CHROMIUM=/usr/bin/chromium npm test
```

## 视觉与音乐

前台继续使用新中式 / 古风视觉体系。全局音乐播放器支持跨前台路由保持播放状态与音量设置；浏览器自动播放限制仍以用户主动开启为准。

项目内 `public/music/quiet-waters.ogg` 可由：

```bash
python scripts/generate_music.py
```

重现。它是项目自编五声音阶合成拨弦循环，不使用第三方录音样本。

## 前后台边界

公开前台只展示用户本次计算需要的盘面、规则命中、必要 Evidence、限制说明和可折叠 Trace，不提供完整内部知识库浏览。

`/admin` 用于知识资产、规则、Evidence、来源、分层、算法 Variant、Prompt、评测和系统治理等管理视图。RAW、Quarantine、完整规则库、内部 Prompt、全量 Evidence 与知识图谱不作为公开前台资源。

具体场景运行边界见 `docs/scenarios/RUNTIME.md`。
