# 第一批：正官、印绶结构候选

从 main `c4784e8771e99fd47e41df4eb5b5cc814962f15e`（#140）继续，沿既有 Source / Classic / Chapter / Section / Term / Rule / Concept / Evidence / Variant / Golden / Phase2 模型补两个研究范围。没有新增知识 schema、平行知识库或生产格局算法。

**已实现的只是结构候选观察**：月支所藏的正官、正印、偏印及该干在年/月/时逐字透出的位置。完整格局仍 NOT_BUILT，真假、成败、喜用、个人吉凶均 unresolved。研究 Variant 需显式选择，公共 Scenario、产品 claim 与 AI 不开放。

## 短引审核

沿用已固定且有校验和的 Quarantine 快照，追加其 Source.review_scope 与 Phase1 Section.review，不修改来源 commit、正文、字形或证据等级。研究材料先在[格局审计](BAZI_PATTERN_AUDIT.md) 定位，再逐字核唯一短引、章内上下文和限制，最后投影到既有 `data/canonical/bazi/phase1_knowledge.json`。本批只授权这些短引的结构观察及边界，不授权整书或定格解释。

| 新 Section | 依据和审查内容 | 执行边界 |
| --- | --- | --- |
| s053 | 滴天髓·八格原注：月支之神透干，散乱显干不等于格 | 月藏与逐字透干观察，不把显干十神当月令候选 |
| s054 | 同章任氏：月令、透干、再究司令；禄刃例外另审喜忌 | 保留司令依赖，不把本气强弱口径的豁免迁移到定格 |
| s055 | 渊海·正官论：月令正官、时干支偏官的限制 | 官杀同现只报位置，不执行去杀留官或混杂成败 |
| s056 | 同章甲用辛：透干/不透而地支官局、中气与身旺分支 | 保留不透分支；未透不等于无官格，本候选不覆盖官局定格 |
| s057 | 渊海·论印綬：正偏阴阳与财旺破印条件 | 正偏分别返回；财出现不等于财旺或破印 |
| s058 | 同章：官鬼多、别格不能专论印綬 | 不发明“多”的阈值，不由印位置直接定印格 |
| s059 | 同章：各日干的生我月份语境 | 仅月令生我背景，不执行后段岁运、疾病、寿命等断语 |

每条 Section 保存固定快照 Unicode `[start,end)` 与一基行号、Source ID、原字形、审核方法和明确范围；与 s004 藏遁歌等已审结构证据一起绑定 r027 / r028。来源仍 C，现代结构过滤明确列为形式化，不冒充古籍原句。

《渊海》印綬部分不复用旧整书错误分段；新 Chapter locator 明示原正文标题缺开括号及编辑划定边界。外部[渊海固定转录 oldid=2593607](https://zh.wikisource.org/w/index.php?title=淵海子平&oldid=2593607) 可对照正官分支，但页面本身来源待核、内容未全；不作为独立底本投票或等级升级证据。

## 执行链

显式 `pattern_variant=bazi-pattern-structure-candidates-v1` 在原 `ziping-structural-v1` 中启用：

1. 复用四柱、日主、天干十神、藏干的实际执行结果。
2. 复用 `hidden_to_visible` 的逐字曝光结果，只取 `hidden_pillar=month`；不重新造透干算法。
3. 运行既有 `month_command_variant`，保留司令未解及适用的寅月分日冲突。
4. 两条执行 Rule 各自过滤正官、正印/偏印的月藏位置，并核透藏事实与显干事实一致。
5. 返回 `pattern_candidates.official` / `.resource`，各自有真实 RuleMatch、Evidence 和事实指针。

候选观察包含 `observations`（藏干、十神、是否透出、各透出柱）、`context_positions`（相关官杀/财印位置）、`dated_commander`（状态、实际冲突 ID、trace 引用）与 `unresolved_conditions`。上下文只报事实，不把存在当成作用，也不推官鬼多、财旺或破格。藏干没有变成显干或参与权重计票。

复用的 r015 透藏规则同步明确服务端 `factor_variant` 条件与研究候选入口；仍执行同一逐字位置操作，避免新入口的 trace 与旧文字条件不一致。原有强弱入口保持其范围，公共入口不因此开放候选。

有月藏命中时状态为 `structural_observation_only`；没有命中为 `no_month_candidate`。两种情况的 `determination` 都为 unresolved，`pattern / true_false / success_failure / useful_god` 都为 null。“本范围没候选”不表示原典所有取格分支均不成立。

未解条件显式保留：具体司令、禄刃/杂气例外、官杀去留或财旺破印/别格、一般旺衰及实际作用、原典分支选择。即使组合现有有限强弱研究得 strong，也不替代这些定格条件；依赖之间各自保留自己的授权范围。

## 输入与门禁

沿用现有 `/api/v1/execute`，无新路由、页面或 Scenario。示例研究请求：

```json
{
  "domain": "bazi",
  "mode": "research",
  "input": {
    "value": "2000-01-01T12:00:00+08:00",
    "pattern_variant": "bazi-pattern-structure-candidates-v1"
  }
}
```

日期继续使用国内时区。手工四柱沿既有 engine 契约；不能与日期混入。默认 execute / 生产 API 拒绝该候选选项，公共 bazi-profile 不接收它；候选 Rule 不进入 `supported_capabilities` 或公开 claim，只列在 `research_capabilities`。

引擎返回 `research_only=true`、`interpretation_contract.ai_may_explain=false`。现有 ExplanationService 在检索/模型调用前拒绝，即使请求 `explain=true` 或更换 prompt 版本也不能绕过。没有调用真实模型或更改秘钥配置。

## 固定 Golden 与关键反例

8 个预期从已审藏干、十神和原文边界手工固定，不从待测输出生成。这里都是结构四柱案例，不额外宣称对应日期或古籍命例。

| 类别 | 四柱 | 固定观察/限制 |
| --- | --- | --- |
| positive | 戊午 / 辛酉 / 甲午 / 庚午 | 月酉藏辛正官在月干透；庚七杀存在仍不定格 |
| positive | 癸亥 / 壬子 / 甲寅 / 癸酉 | 月子藏癸正印，年/时透；月干壬偏印不能替代月藏癸 |
| positive | 壬申 / 丁亥 / 甲子 / 壬申 | 月亥藏壬偏印，年/时透；偏印不写成正印格 |
| positive | 庚申 / 甲申 / 乙丑 / 壬午 | 阴日乙：月申庚正官年透、壬正印时透，分别保留 |
| negative | 辛酉 / 丙寅 / 甲子 / 庚午 | 月寅无本范围官/印；年辛显官不偷换成月令候选 |
| abstention | 戊午 / 丁酉 / 甲午 / 丙午 | 月酉藏官而未透，只报未透，不否定未覆盖官局分支 |
| abstention | 辛酉 / 丁丑 / 甲子 / 癸亥 | 杂气丑月的辛官/癸印及曝光可报，选格与冲法仍未解 |
| conflict | 甲子 / 丙寅 / 丙午 / 乙亥 | 寅月甲偏印年透；寅月分日冲突保持未解，不取司令或定真假 |

Golden 的 positive 指结构观察有命中；没有任何一例授权成格、破格、喜用或吉凶。所有类别都保留 determination unresolved。

测试覆盖固定预期、阴阳正偏、非月显干反例、未透与杂气拒断、司令冲突、与有限强弱同时调用的边界、trace/Evidence 引用、缺失或矛盾执行事实、生产/API/Scenario/产品拒用、三个 prompt 版本在模型前拒绝。

## 成熟度与保护范围

候选子口径为 RESEARCH_VALIDATED / PARTIAL；完整定格为 NOT_BUILT，explanation_ready=false。派生报告核已审契约和固定 Golden 定义，不冒充实际运行测试，运行结果以本 PR CI 为准。全仓执行规则由 62 增至 64，Golden 由 84 增至 92；Source 仍 C92/D6，已有冲突概念仍 4。

《三命通会》仍 quarantine_only、canonical_ready=false，计划整书 Canonical 不存在；RAW、PUA、603 条普通 OCR collation 均未改。PUA 86/86、524/524、remaining=0。梦境、前端、喜用和岁运没有扩展。

下一阶段应先补明确口径的定格资格依赖和反例。司令尚未裁定时，不进入任氏真假裁决；不能用本次候选研究完成来宣布格局产品完成。
