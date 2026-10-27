# TJ-011.2 F3/F4 审定：火×巳（禄月）与火×寅（长生/印月）形态裁定文档

状态：设计裁定文档（Design）。与数据登记模块
`src/tianji_kb/bazi_fire_si_yin_morphology.py`（register id
`bazi-fire-si-yin-morphology-adjudication-v1`）成对交付；Golden 设计见
`tests/golden_tj0112_f34_si_yin.json`。本批为纯审定+登记，**零谓词实现代码**：
合并后任何 F3/F4 命盘的现行裁决仍为 indeterminate，密封测试逐字钉住这一点。
F1 登记（`bazi_fire_morphology.py`）中 F3='not_adjudicated'、
F4='deferred_not_adjudicated' 的历史处置不改动，由本登记以 supersede 关系承接。

审定沿用 F1 口径：条件逐项标注锚点层级——`original_text`（原文锚点）、
`governance_convention`（治理约定，必须明示、不得冒充原典）、
`framework_derived`（推步级，必须披露、不得标作明句级）；
`scope_construction` 为沿 F1 既例的事实组装条件。冲突不裁定。

## 裁定一：F3 丙×巳可建——另立「禄月」新形态（九条件）

巳月不能套用既有两种同令形态，证明在案：

- **pure 构造性不可满足**：巳藏干固定为丙（本气，同类）/戊（中气，我生·食伤）/
  庚（余气，我克·财），任何巳月命盘必含非生扶藏干关系，
  pure 的「全位置仅生扶」恒假；
- **generating 名实不符**：巳本气丙对丙日主是 same_element 而非 generates_me，
  巳非火之印月；套用木×亥的 pure_generating_support 名义即误标月关系。

巳的真实身份是原文登记齐备的**禄位**：三命逐干明句「其禄在巳」（sm2.bing_lu，
校勘读巳）、节末总结块、三命禄列、神峰十干禄表「丙戊禄在巳」（sf.lubiao）、
滴天髓单点「丙禄居巳」（dt.bing_lu_single）三证互印，per_stem_listed 级。
故另立形态 `bing-si-lu-commanding-visible-support-v1`（候选谓词名
`lu_visible_support`），主锚从强定义（含「日主又当令」句，当令在此具体化为禄月）
+ 从旺共锚，九条件与 F1 commanding 形态同构、月份条件换为禄位条件：

| # | 条件 | 锚点层级 | 要点 |
|---|---|---|---|
| 1 | fire_day_master_bing | scope_construction | 日主丙；丁排除（冲突+禄锚丙专属） |
| 2 | reviewed_lu_command_month | original_text | 月支巳、本气丙已审 same_element、巳为已登记禄位（三证） |
| 3 | visible_positions_support_only | original_text | 显干（年/月/时）全为生扶 |
| 4 | visible_resource_present | original_text | 显干有印（甲/乙） |
| 5 | visible_peer_present | original_text | 显干有比劫（丙/丁） |
| 6 | effective_heavy_day_roots | original_text | 日主根全 effective 且有重根（重根集{寅,巳,午}，巳本身即禄重根） |
| 7 | all_visible_have_reviewed_roots | scope_construction | 显干各有已审根位（木 policy 集、火 BING_ALL 集） |
| 8 | no_unresolved_interactions | scope_construction | 无未决作用（干合/冲/合/害/成局三合） |
| 9 | hidden_layer_convention_applied | governance_convention | 新约定实例 `fire-morph.wu-geng-in-si-non-veto`：巳藏戊（食）/庚（财）不否决，仅作记录；若否决则形态构造性不可满足、与已齐备的定义+禄位证据不相称——与 F1 己藏午实例同一论证结构，约定明示为治理约定 |

克破排除与 F1 同构（显干官/杀/财/食逐项有否决锚点；藏干层只记录不裁定）。

**可满足性（如实登记）**：1900–2100 全部丙日主×巳月命盘穷举扫描（7512 盘，
时辰粒度，条件按登记口径执行）**正例恰 1 例**：1927-05-12 午时
丁卯/乙巳/丙午/甲午。瓶颈在「根印通道」：显干印须有已审根位，木已审根位支
{亥,寅,卯} 中寅害巳、亥冲巳，卯只能作年支进入（丙日卯时干为癸=官、丙卯非合法柱），
而卯年经显干过滤只剩丁卯/乙巳一家，其巳月丙日与生扶时辰几乎全灭于具名作用关系。
窄是该条件集的性质、不是证据缺口；**不为扩面放宽任何条件**（站立规则）。
按 S2 金×酉先例，窄面不碍实现：实现批另派，谓词按登记条件原样求值，
该唯一见证登记为 Golden 正例。

## 裁定二：丁×巳单独处置——blocked_by_conflict

巳本气丙对丁为比劫（同类），且丁禄在午（冲突两读法一致，sm2.ding_lu），
F3 的禄月锚点是丙专属、不可移用；丁线整体另有长生冲突
`sanming-juan2.ding-changsheng` 未裁。丁×巳只登记阻断关系与结构注记，不设计形态。

## 裁定三：F4 丙×寅审定成立、实现受门阻断（司令扩月用户裁定）

寅是印月（本气甲 generates_me 已审）且为丙之**长生位**：三命逐干明句
「丙火生于寅」（sm2.bing_sheng）+ 反句「生于寅而死于酉」（sm2.bing_shengsi）+
节末总结块 + 神峰四生说（sf.sisheng）+ 三命人元司事旁证（sm2.renyuan_bing：
寅中甲木用事二十日、丙火长生五日）互印，per_stem_listed 级。
pure/generating 两形状同样构造性不可满足（寅藏戊，我生，破全位置仅生扶；
人元句本身即为寅藏戊之同书证据），pure 之名亦不合（寅本气生我、非同类月）。

形态 `bing-yin-changsheng-visible-support-v1`（候选谓词名
`changsheng_visible_support`）主锚从旺（**无当令要件**，沿 generating 谱系先例），
月份条件为复合条件：已审印月 + 月支为日主已登记长生位。**明示不称当令**：
寅非丙之禄/帝旺位，无任何原文称寅月火日主「当令」。九条件与 F3 同构，
藏干约定实例为 `fire-morph.wu-in-yin-non-veto`（寅藏戊不否决；寅藏丙为中气比劫，
按约定记录不计效）。

**实现门（登记不省略）**：寅月是唯一已有登记且试点授权的任氏分日司令月份
（s024 分段：戊 [立春,+7d) / 丙 [+7d,+14d) / 甲 [+14d,下一交节)，
约定 `siling-calculation-convention` v1）。首段司令戊对丙为食伤，
与「印月」刻画在首段命盘正面冲突；强度形态月份条件是否按司令分段收紧，
与司令扩月裁定（Slice C 决策包 A/B）同属一个用户级流派决策。两读法并列登记：

- （甲）principal-only：月份条件按本审定，不问分段——扫描见证 39 例全在触发面；
- （乙）segment-tightened：月份条件增设司令段==甲——仅甲段 19 例在触发面。

裁定前两读法均不得单独落码；**形态审定与登记本身不受门阻断**。
可满足性已量化：1900–2100 穷举 7164 盘、正例 39 例、三段皆有
（戊 12 / 丙 8 / 甲 19）——门决定的是真实且已量化的触发面差异，不是形式关口。

附带注记：**本批无 framework_derived 元素**——巳禄位、寅长生位均有逐干明句，
不需 F1 帝旺推步那样的代偿披露。

## 裁定四：丁×寅——blocked_by_conflict（双重敏感）

寅正是丁长生冲突分支乙（神峰系，丁长生寅）的读法位点；为丁×寅设计长生形态
即预先裁掉冲突。只登记阻断与注记。

## 裁定五：土根位接口登记（站立缺口审计）

站立缺口（承 S2）：土根位整线零登记——密封 policy 无土集、无土根登记册，
戊/己显干根位资格未审，不得借未审根表。本批逐条件审计结论：
**F3/F4 任何条件都不消费土根位事实**——

- 显干层先于根位资格被 support-only 过滤：戊/己显干必先败于
  visible_positions_support_only，永远到不了根位资格审查；
- all_visible_have_reviewed_roots 在存活命盘上只会被咨询木/火干（生扶幸存者）；
- 日主根为火根、由火线登记分级；土支（辰戌丑未）只作载体
  （未/戌载已登记火轻根）；藏干土只经藏干约定作记录事实。

与 S2 金×酉相区别：彼处土是金日主之印、显干土能通过显干过滤，
根位资格是必经面，缺口具阻断性；此处土是火之食伤，缺口不在关键路径上。
待定面登记在案：未来形态若需戊/己显干根位资格、或消费藏干根位资格，
须先行审定；本批不补。

## 裁定六：Golden 设计（七例，全真实命盘）

文件 `tests/golden_tj0112_f34_si_yin.json`，结构镜像 F1 Golden
（meta + cases[category, condition_table, derivation, expect]）：

F3 五例——
1. **正例**（扫描唯一见证）：1927-05-12 午时 丁卯/乙巳/丙午/甲午，九条件全真；
2. **近失单失败**：2017-05-19 午时 丁酉/乙巳/丙午/甲午，
   仅 all_visible_have_reviewed_roots 假（两印无根：四支酉/巳/午/午无一藏木）；
3. **弃判例**：1927-06-01 午时 丁卯/乙巳/丙寅/甲午，
   寅巳害同源双失败（no_unresolved + effective_heavy）；原设计 1987 年同柱例
   因夏令时 +08:00 声称被生产历法链正确拒绝，换 1927 同柱例（Golden meta 已注记）；
4. **冲突呈现例**：2047-05-22 午时 丁卯/乙巳/丙戌/甲午，
   日根在戌携登记冲突 root_type_readings → effective_heavy 假，
   伴生卯戌合 → no_unresolved 假；附单失败冲突例不可构造证明
   （印根支被逼至卯、卯与戌六合，冲突例必 ≥2 失败）；
5. **形态外对照例**：2001-05-13 酉时 辛巳/癸巳/丙子/丁酉，
   显干财官触发定义层否决（失败集：support_only + resource_present），余条件真。

F4 两例——
6. **正例（两读法一致）**：2034-02-19 午时 甲寅/丙寅/丙午/甲午，
   出生于立春 +15 日余、甲段内，principal 与 segment 两读法下月份刻画一致；
7. **门敏感性例**：2014-02-04 午时 甲午/丙寅/丙午/甲午，
   出生于立春后约 6 小时、戊段内：principal 读法九条件全真，
   segment 读法月份条件假；expect 登记为 undetermined_pending_segment_decision，
   两读法结论并列——此例即实现门的存在理由。

七例现行裁决**全为 indeterminate**（F3/F4 谓词未实现），密封测试逐字钉住；
实现批落地时按各自 expect 翻转。

## 未覆盖清单（如实）

- F3 实现批：待本审定合并后另派（四类 Golden 复证 + 因子层测试）；
- F4 实现批：被实现门阻断，待司令扩月用户裁定，不得先行；
- 扶抑 S4 最小切片审定：未行；
- S5 密封 Phase1/Phase2 注册治理：多批 pending 注册存量（含本批两形态）未行，
  pending 披露口径保留；
- 丁线：长生冲突未裁，两面维持 blocked_by_conflict；
- 土根位登记：缺口维持，本批只登记接口不补表；
- 三命 T1 人元分配（寅：戊 5/丙 5/甲 20 日）与任氏分段（7/7/余）是两个不同陈述，
  本批只作旁证引用人元句，永不拼接。

## 验证口径

- 公开测试 `tests/test_tj0112_f34_si_yin.py`：登记结构、引文跨册引用完整性、
  九条件锚点层级（约定条目不得标原文）、门与接口字段、Golden 柱合法性
  （含干支阴阳配伍机检）、期望与条件表自洽；
- 密封测试 `tests/test_tj0112_f34_si_yin_sealed.py`（不入公开 CI，同既有分区规则）：
  跨册引文经 F1/C18/司令矩阵登记切片逐字复核、七例经生产历法链逐柱重演、
  七例现行裁决全 indeterminate、既有六谓词回归抽验（F1 丙午正例、
  S2 癸×子见证例仍 strong）、密封 policy 零改动；
- 合并前硬门：机上 `accept_offline.py --suite all` 对最终 Head SUCCESS，
  计数 = 同环境实测 main 正式基线 + 本批新增直跑计数对账；manifest 不变。
