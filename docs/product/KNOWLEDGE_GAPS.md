# 测算产品 × 知识库覆盖及缺口

由 `scripts/build_product_coverage.py` 扫描实际 JSON、来源、执行契约、Golden、代码和 RAG 自动生成。运行 `--check` 检查漂移。

这是现有知识库的派生报告，不是新知识模型、Rule 或上线授权。所有产品解释均未开放；结构计算与完整测算报告分开评估。

实际文件：Canonical 77，Quarantine 118；来源登记 37；逐项证据来源 97。
已注册确定性引擎 7 个，Phase2 Rule 48 条，Golden 34 个；八字结构已注册，梦境未建立。
证据等级 {"C": 91, "D": 6}；旧 registry trust_level A/B 不等于独立古典 Evidence A/B。
RAG：已审核实体 741 块；通用 2470 块，含旧资料，不能代替执行命中。

| 产品 | 所需专题 | 已有 | 缺失/阻塞 | 完整产品可生产 |
|---|---|---|---|---|
| 八字详批 | 八字基础与十神映射、十神结构与条件解释、旺衰及流派边界、格局、喜用神分体系治理、大运、流年与岁运作用 | bazi结构 | 缺产品解释及门控链路，详见下文 | 否 |
| 今日运势 | 八字基础与十神映射、旺衰及流派边界、喜用神分体系治理、大运、流年与岁运作用、流日 | bazi结构 | 缺产品解释及门控链路，详见下文 | 否 |
| 本周运势 | 八字基础与十神映射、旺衰及流派边界、喜用神分体系治理、大运、流年与岁运作用、流日 | bazi结构 | 缺产品解释及门控链路，详见下文 | 否 |
| 本月运势 | 八字基础与十神映射、旺衰及流派边界、喜用神分体系治理、大运、流年与岁运作用、流月、流日 | bazi结构 | 缺产品解释及门控链路，详见下文 | 否 |
| 今年运势 | 八字基础与十神映射、旺衰及流派边界、喜用神分体系治理、大运、流年与岁运作用 | bazi结构 | 缺产品解释及门控链路，详见下文 | 否 |
| 桃花姻缘 | 八字基础与十神映射、旺衰及流派边界、喜用神分体系治理、流年与岁运作用、婚恋专题 | bazi结构 | 缺产品解释及门控链路，详见下文 | 否 |
| 事业财运 | 八字基础与十神映射、十神结构与条件解释、旺衰及流派边界、格局、喜用神分体系治理、大运、流年与岁运作用、事业财富专题 | bazi结构 | 缺产品解释及门控链路，详见下文 | 否 |
| 缘分合盘 | 八字基础与十神映射、旺衰及流派边界、婚恋专题、流年与岁运作用、双人关系 | bazi结构 | 缺产品解释及门控链路，详见下文 | 否 |
| 人生总览 | 八字基础与十神映射、旺衰及流派边界、格局、喜用神分体系治理、大运、流年与岁运作用、婚恋专题、事业财富专题、人生聚合 | bazi结构 | 缺产品解释及门控链路，详见下文 | 否 |
| AI解梦 | 传统梦文化、现代心理梦研究 | 未建立 | 缺产品解释及门控链路，详见下文 | 否 |
| 一事占问 | 六爻占问深化、奇门专业能力 | liuyao结构, qimen结构 | 缺产品解释及门控链路，详见下文 | 否 |
| 紫微专业工具 | 紫微专业能力 | ziwei结构 | 缺产品解释及门控链路，详见下文 | 否 |
| 奇门专业工具 | 奇门专业能力 | qimen结构 | 缺产品解释及门控链路，详见下文 | 否 |
| 六壬专业工具 | 六壬专业能力 | liuren结构 | 缺产品解释及门控链路，详见下文 | 否 |
| 风水专业工具 | 风水专业能力 | fengshui结构 | 缺产品解释及门控链路，详见下文 | 否 |
| 周易专业工具 | 周易专业能力 | yijing结构 | 缺产品解释及门控链路，详见下文 | 否 |

## 现有治理路径

补库只走已有 Source → RAW → Quarantine → Review → Canonical → Terms/Rules → Evidence → Variant/Conflict → Golden → Phase2 → Scenario。
使用 `config/source_registry.json` / `source_file_manifest.json` / `public_domain_manifest.json` 的既有采纳范围；固定来源通过 `stage_phase1_sources.py` / `acquisition.stage_candidate` 隔离。
现有七域（包括八字）`phase1_knowledge.json` 与 `knowledge_sources.json` 使用既有 schema / `validate_knowledge`；Phase2 用既有执行、补充证据、来源审计、晋级记录、Golden 和 `validate_phase2.py`。
八字结构与条件化配偶星口径已接入同一模型；梦境尚未接入。补库必须沿用既有模型及校验，不另外造知识结构；本批不修改 schema、不自动晋级。

## 迭代顺序与小批量验收

P0：八字基础/十神 → 旺衰（先选并核单一 Variant）→ 格局 → 四套喜用体系分别治理 → 大运/流年 → 婚恋/事业财富 → 双人关系；梦境来源审查可独立进行。
P1：六爻解释深化、流月、流日、人生聚合；P2：紫微、奇门、六壬、风水扩展、周易专业。
首批优先复核现有《滴天髓阐微》知命/夫妻/女命、《渊海子平》月令/大运及《穷通宝鉴》月令材料。先抽少量原文与限制，保存反例；不得从整本存在直接推规则已审核。
每批只处理一个明确条件关系及反例：检查来源权利/版本/字面 → 已有模型引用 → 命名 Variant 与适用边界 → 固定 Golden/反例 → 测试 → 执行晋级记录；缺任何一步继续隔离。
六爻优先复用已登记《增删卜易》《卜筮正宗》；专业域优先复用下列真实 source_id。梦境当前无已登记专库，先做来源/权利审核，不能借命理语料或模型先验填充。

## 结论能力门控

`product_claims.py` 复用 EvidenceResolver、现有 explanation_policy 和 validate_reply；检查事实存在、可执行 Rule、Golden、等级/Variant、来源冲突。产品入口在模型调用前拒绝尚未审核的完整解释。现有结构API继续按原范围工作。
完整产品授权/claim白名单与模型人工复核绑定契约尚未实现；当前不接受改几个布尔值作为发布授权。此门控保持关闭，不宣称已完成全部生产放行能力。
当前全部 `production_claims=[]`，公开解释一律拒绝。新 Prompt v3 明示 “Absence of knowledge is not permission to use model prior knowledge.”；旧 v1/v2 保持不可变，仅供既有评测比较。
自由文本的语义蕴涵不能只靠 JSON/关键词证明；现有人工语义审核仍是必要步骤，门控测试不等于模型质量达标。

## 冲突与隔离边界

沿用既有governance.school_conflicts：传统配偶星口径已限定范围，三刑争议未解决；Rule difference/exceptions、执行unresolved与来源审计继续保留。
《三命通会》保持 quarantine_only / canonical_ready=false；原始 snapshot、已确认 PUA/OCR 映射未修改，不能进入 Canonical/RAG。

## 实查现有模型

| 域 | Classics | Chapters | Sections | Terms | Rules | Concepts |
|---|---:|---:|---:|---:|---:|---:|
| yijing | 4 | 85 | 104 | 19 | 6 | 73 |
| liuyao | 2 | 4 | 38 | 30 | 24 | 8 |
| qimen | 2 | 6 | 33 | 44 | 6 | 10 |
| ziwei | 1 | 15 | 44 | 48 | 11 | 14 |
| fengshui | 6 | 9 | 22 | 37 | 8 | 3 |
| liuren | 2 | 35 | 42 | 42 | 14 | 12 |
| bazi | 4 | 11 | 22 | 12 | 12 | 3 |

## 首批来源隔离及编辑标记审核

已按现有 `acquisition.stage_candidate` 保存以下固定来源的 RAW（忽略缓存）及 Quarantine 元数据；Git blob校验通过，整本review_status=pending，promotion_allowed=false。仅知命前段单独审核后入既有Phase1模型，整本不晋级，来源等级不变。

- `易藏/术数/渊海子平.txt` @ `4a6d6f2088825f132521d848c2ea86cf9c9a7620`，blob `c7de6ab493e19460f5efba49085d20437c17e1d4`。
- `易藏/术数/滴天髓阐微.txt` @ `4a6d6f2088825f132521d848c2ea86cf9c9a7620`，blob `e269843d0544fd18ac7d7c97d4e0bd268a5240ef`。

原典审核前须处理下列编者/增补标记（定位到实际 JSON；不自动删改旧文件）：

- `data/canonical/classics/bazi/ditiansui_chanwei_v1.json#/sections/3/text`：若思按、(新增)。
- `data/canonical/classics/bazi/ditiansui_chanwei_v1.json#/sections/4/text`：若思按。
- `data/canonical/classics/bazi/ditiansui_chanwei_v1.json#/sections/7/text`：若思按。

现有来源 schema 未显式包含 edition；97条来源的 edition 不可从书名推定。版本核验仍按现有来源审计记录，正式扩展应保持同一治理模型。

实查 API：GET `/api/v1/admin/governance/algorithms`；GET `/api/v1/admin/governance/chapters`；GET `/api/v1/admin/governance/classics`；GET `/api/v1/admin/governance/conflicts`；GET `/api/v1/admin/governance/evidence`；GET `/api/v1/admin/governance/layers`；GET `/api/v1/admin/governance/rules`；GET `/api/v1/admin/governance/sources`；GET `/api/v1/admin/governance/terms`；GET `/api/v1/admin/system/prompts`；GET `/api/v1/admin/system/provider`；GET `/api/v1/capabilities`；POST `/api/v1/execute`；GET `/api/v1/scenarios`；POST `/api/v1/scenarios/execute`；GET `/health`。已有真实Scenario执行与后台只读治理 API；历史记录与管理写入尚未完成。

## 八字详批

已有：

- 现有 Scenario `bazi-profile`：production，结构执行=True，结构公开标志=True；四柱、日主、十神、藏干结构事实。
- 八字基础与十神映射：术语 3，关联 Phase1 Rule 5，列入结构映射的 Phase2 Rule 3。
  旧资料 `data/canonical/bazi/foundations_v1.json`（实现/描述参考，未授权解释）。
  原文候选 `data/canonical/classics/bazi/ditiansui_chanwei_v1.json#/sections/0/text`；66 个字段命中，仅作待审查定位。
  原文候选 `data/canonical/classics/bazi/qiongtong_baojian_v1.json#/sections/0/title`；51 个字段命中，仅作待审查定位。
  原文候选 `data/canonical/classics/bazi/yuanhai_ziping_v1.json#/sections/0/text`；135 个字段命中，仅作待审查定位。
- 十神结构与条件解释：术语 1，关联 Phase1 Rule 4，列入结构映射的 Phase2 Rule 2。
  旧资料 `data/canonical/bazi/foundations_v1.json`（实现/描述参考，未授权解释）。
  原文候选 `data/canonical/classics/bazi/ditiansui_chanwei_v1.json#/sections/6/text`；17 个字段命中，仅作待审查定位。
  原文候选 `data/canonical/classics/bazi/qiongtong_baojian_v1.json#/sections/3/text`；33 个字段命中，仅作待审查定位。
  原文候选 `data/canonical/classics/bazi/yuanhai_ziping_v1.json#/sections/12/text`；10 个字段命中，仅作待审查定位。
- 旺衰及流派边界：术语 0，关联 Phase1 Rule 0，列入结构映射的 Phase2 Rule 0。
  原文候选 `data/canonical/classics/bazi/ditiansui_chanwei_v1.json#/sections/2/text`；55 个字段命中，仅作待审查定位。
  原文候选 `data/canonical/classics/bazi/qiongtong_baojian_v1.json#/sections/3/text`；33 个字段命中，仅作待审查定位。
  原文候选 `data/canonical/classics/bazi/yuanhai_ziping_v1.json#/sections/4/text`；51 个字段命中，仅作待审查定位。
- 格局：术语 0，关联 Phase1 Rule 0，列入结构映射的 Phase2 Rule 0。
  原文候选 `data/canonical/classics/bazi/ditiansui_chanwei_v1.json#/sections/7/text`；13 个字段命中，仅作待审查定位。
  原文候选 `data/canonical/classics/bazi/qiongtong_baojian_v1.json#/sections/3/text`；14 个字段命中，仅作待审查定位。
  原文候选 `data/canonical/classics/bazi/yuanhai_ziping_v1.json#/sections/14/text`；14 个字段命中，仅作待审查定位。
- 喜用神分体系治理：术语 0，关联 Phase1 Rule 0，列入结构映射的 Phase2 Rule 0。
- 大运：术语 0，关联 Phase1 Rule 0，列入结构映射的 Phase2 Rule 0。
  旧资料 `data/canonical/bazi/dayun_v1.json`（实现/描述参考，未授权解释）。
  原文候选 `data/canonical/classics/bazi/ditiansui_chanwei_v1.json#/sections/3/text`；9 个字段命中，仅作待审查定位。
  原文候选 `data/canonical/classics/bazi/qiongtong_baojian_v1.json#/sections/11/text`；1 个字段命中，仅作待审查定位。
  原文候选 `data/canonical/classics/bazi/yuanhai_ziping_v1.json#/sections/9/title`；7 个字段命中，仅作待审查定位。
- 流年与岁运作用：术语 1，关联 Phase1 Rule 1，列入结构映射的 Phase2 Rule 0。
  旧资料 `data/canonical/bazi/foundations_v1.json`（实现/描述参考，未授权解释）。
  原文候选 `data/canonical/classics/bazi/ditiansui_chanwei_v1.json#/sections/1/text`；62 个字段命中，仅作待审查定位。
  原文候选 `data/canonical/classics/bazi/qiongtong_baojian_v1.json#/sections/0/text`；59 个字段命中，仅作待审查定位。
  原文候选 `data/canonical/classics/bazi/yuanhai_ziping_v1.json#/sections/0/text`；126 个字段命中，仅作待审查定位。

缺失：

- 八字基础与十神映射：四柱/日主/十神/藏干已接入既有模型和执行Golden；仍缺十二长生、月令解释及基础结构到个人结论的条件规则；真太阳时尚未实现。旧表权重不作通用古典结论。
- 十神结构与条件解释：映射不等于组合、位置、透藏、月令条件下的解释；须补原典规则、限制及反例。
- 旺衰及流派边界：缺命名 school/variant、通根与月令条件、权重依据、冲突记录、执行与反例 Golden；不能用五行数量判断强弱。
- 格局：正文提及不等于结构规则；缺成格/破格/兼格条件、流派限制和 Golden。
- 喜用神分体系治理：调候、扶抑、病药、格局用神未分别治理；依赖旺衰与格局；禁止输出喜用木火等具体结论。
- 大运：旧说明不是执行；须核顺逆/起运法/节界/岁数换算/原局作用及不同 Variant。
- 流年与岁运作用：日历干支不等于运势；缺原局、大运、流年作用图及强弱/喜忌条件规则。

阻塞：

- 所需解释模块尚无产品级审核授权
- AI未完成真实质量校准及人工语义复核
- 已实现结构Scenario不等于运势/占断；完整解释与发布绑定尚未完成

禁止结论：身强身弱；格局成立；具体喜用神；完整详批。

推荐复核来源（本地已存在；不因列在这里自动升 Evidence）：

- `bazi.source.xieji-relations`
- `bazi.source.yuanhai`
- `data/canonical/classics/bazi/ditiansui_chanwei_v1.json`
- `data/canonical/classics/bazi/qiongtong_baojian_v1.json`
- `data/canonical/classics/bazi/yuanhai_ziping_v1.json`

前台降级：当前已实现的结构能力可供专业参考；该项深入解释仍在知识审核中。

## 今日运势

已有：

- 现有 Scenario `daily`：production_limited，结构执行=True，结构公开标志=False；返回目标日干支、日干相对日主的十神结构，以及两套咸池目标支是否被当日地支命中；不输出今日吉凶。
- 八字基础与十神映射：术语 3，关联 Phase1 Rule 5，列入结构映射的 Phase2 Rule 3。
  旧资料 `data/canonical/bazi/foundations_v1.json`（实现/描述参考，未授权解释）。
  原文候选 `data/canonical/classics/bazi/ditiansui_chanwei_v1.json#/sections/0/text`；66 个字段命中，仅作待审查定位。
  原文候选 `data/canonical/classics/bazi/qiongtong_baojian_v1.json#/sections/0/title`；51 个字段命中，仅作待审查定位。
  原文候选 `data/canonical/classics/bazi/yuanhai_ziping_v1.json#/sections/0/text`；135 个字段命中，仅作待审查定位。
- 旺衰及流派边界：术语 0，关联 Phase1 Rule 0，列入结构映射的 Phase2 Rule 0。
  原文候选 `data/canonical/classics/bazi/ditiansui_chanwei_v1.json#/sections/2/text`；55 个字段命中，仅作待审查定位。
  原文候选 `data/canonical/classics/bazi/qiongtong_baojian_v1.json#/sections/3/text`；33 个字段命中，仅作待审查定位。
  原文候选 `data/canonical/classics/bazi/yuanhai_ziping_v1.json#/sections/4/text`；51 个字段命中，仅作待审查定位。
- 喜用神分体系治理：术语 0，关联 Phase1 Rule 0，列入结构映射的 Phase2 Rule 0。
- 大运：术语 0，关联 Phase1 Rule 0，列入结构映射的 Phase2 Rule 0。
  旧资料 `data/canonical/bazi/dayun_v1.json`（实现/描述参考，未授权解释）。
  原文候选 `data/canonical/classics/bazi/ditiansui_chanwei_v1.json#/sections/3/text`；9 个字段命中，仅作待审查定位。
  原文候选 `data/canonical/classics/bazi/qiongtong_baojian_v1.json#/sections/11/text`；1 个字段命中，仅作待审查定位。
  原文候选 `data/canonical/classics/bazi/yuanhai_ziping_v1.json#/sections/9/title`；7 个字段命中，仅作待审查定位。
- 流年与岁运作用：术语 1，关联 Phase1 Rule 1，列入结构映射的 Phase2 Rule 0。
  旧资料 `data/canonical/bazi/foundations_v1.json`（实现/描述参考，未授权解释）。
  原文候选 `data/canonical/classics/bazi/ditiansui_chanwei_v1.json#/sections/1/text`；62 个字段命中，仅作待审查定位。
  原文候选 `data/canonical/classics/bazi/qiongtong_baojian_v1.json#/sections/0/text`；59 个字段命中，仅作待审查定位。
  原文候选 `data/canonical/classics/bazi/yuanhai_ziping_v1.json#/sections/0/text`；126 个字段命中，仅作待审查定位。
- 流日：术语 0，关联 Phase1 Rule 0，列入结构映射的 Phase2 Rule 0。
  原文候选 `data/canonical/classics/bazi/yuanhai_ziping_v1.json#/sections/7/text`；1 个字段命中，仅作待审查定位。

缺失：

- 八字基础与十神映射：四柱/日主/十神/藏干已接入既有模型和执行Golden；仍缺十二长生、月令解释及基础结构到个人结论的条件规则；真太阳时尚未实现。旧表权重不作通用古典结论。
- 旺衰及流派边界：缺命名 school/variant、通根与月令条件、权重依据、冲突记录、执行与反例 Golden；不能用五行数量判断强弱。
- 喜用神分体系治理：调候、扶抑、病药、格局用神未分别治理；依赖旺衰与格局；禁止输出喜用木火等具体结论。
- 大运：旧说明不是执行；须核顺逆/起运法/节界/岁数换算/原局作用及不同 Variant。
- 流年与岁运作用：日历干支不等于运势；缺原局、大运、流年作用图及强弱/喜忌条件规则。
- 流日：缺流日与原局/岁运关系及时间窗；日历日干支不能直接推每日吉凶。

阻塞：

- 所需解释模块尚无产品级审核授权
- AI未完成真实质量校准及人工语义复核
- 已实现结构Scenario不等于运势/占断；完整解释与发布绑定尚未完成

禁止结论：今日吉凶；今日综合分；今日财运/桃花概率。

推荐复核来源（本地已存在；不因列在这里自动升 Evidence）：

- `bazi.source.xieji-relations`
- `bazi.source.yuanhai`
- `data/canonical/classics/bazi/ditiansui_chanwei_v1.json`
- `data/canonical/classics/bazi/qiongtong_baojian_v1.json`
- `data/canonical/classics/bazi/yuanhai_ziping_v1.json`

前台降级：当前已实现的结构能力可供专业参考；该项深入解释仍在知识审核中。

## 本周运势

已有：

- 现有 Scenario `weekly`：production_limited，结构执行=True，结构公开标志=False；按北京时间周一至周日列出每日干支、日干十神结构与咸池日级命中；不输出周运吉凶。
- 八字基础与十神映射：术语 3，关联 Phase1 Rule 5，列入结构映射的 Phase2 Rule 3。
  旧资料 `data/canonical/bazi/foundations_v1.json`（实现/描述参考，未授权解释）。
  原文候选 `data/canonical/classics/bazi/ditiansui_chanwei_v1.json#/sections/0/text`；66 个字段命中，仅作待审查定位。
  原文候选 `data/canonical/classics/bazi/qiongtong_baojian_v1.json#/sections/0/title`；51 个字段命中，仅作待审查定位。
  原文候选 `data/canonical/classics/bazi/yuanhai_ziping_v1.json#/sections/0/text`；135 个字段命中，仅作待审查定位。
- 旺衰及流派边界：术语 0，关联 Phase1 Rule 0，列入结构映射的 Phase2 Rule 0。
  原文候选 `data/canonical/classics/bazi/ditiansui_chanwei_v1.json#/sections/2/text`；55 个字段命中，仅作待审查定位。
  原文候选 `data/canonical/classics/bazi/qiongtong_baojian_v1.json#/sections/3/text`；33 个字段命中，仅作待审查定位。
  原文候选 `data/canonical/classics/bazi/yuanhai_ziping_v1.json#/sections/4/text`；51 个字段命中，仅作待审查定位。
- 喜用神分体系治理：术语 0，关联 Phase1 Rule 0，列入结构映射的 Phase2 Rule 0。
- 大运：术语 0，关联 Phase1 Rule 0，列入结构映射的 Phase2 Rule 0。
  旧资料 `data/canonical/bazi/dayun_v1.json`（实现/描述参考，未授权解释）。
  原文候选 `data/canonical/classics/bazi/ditiansui_chanwei_v1.json#/sections/3/text`；9 个字段命中，仅作待审查定位。
  原文候选 `data/canonical/classics/bazi/qiongtong_baojian_v1.json#/sections/11/text`；1 个字段命中，仅作待审查定位。
  原文候选 `data/canonical/classics/bazi/yuanhai_ziping_v1.json#/sections/9/title`；7 个字段命中，仅作待审查定位。
- 流年与岁运作用：术语 1，关联 Phase1 Rule 1，列入结构映射的 Phase2 Rule 0。
  旧资料 `data/canonical/bazi/foundations_v1.json`（实现/描述参考，未授权解释）。
  原文候选 `data/canonical/classics/bazi/ditiansui_chanwei_v1.json#/sections/1/text`；62 个字段命中，仅作待审查定位。
  原文候选 `data/canonical/classics/bazi/qiongtong_baojian_v1.json#/sections/0/text`；59 个字段命中，仅作待审查定位。
  原文候选 `data/canonical/classics/bazi/yuanhai_ziping_v1.json#/sections/0/text`；126 个字段命中，仅作待审查定位。
- 流日：术语 0，关联 Phase1 Rule 0，列入结构映射的 Phase2 Rule 0。
  原文候选 `data/canonical/classics/bazi/yuanhai_ziping_v1.json#/sections/7/text`；1 个字段命中，仅作待审查定位。

缺失：

- 八字基础与十神映射：四柱/日主/十神/藏干已接入既有模型和执行Golden；仍缺十二长生、月令解释及基础结构到个人结论的条件规则；真太阳时尚未实现。旧表权重不作通用古典结论。
- 旺衰及流派边界：缺命名 school/variant、通根与月令条件、权重依据、冲突记录、执行与反例 Golden；不能用五行数量判断强弱。
- 喜用神分体系治理：调候、扶抑、病药、格局用神未分别治理；依赖旺衰与格局；禁止输出喜用木火等具体结论。
- 大运：旧说明不是执行；须核顺逆/起运法/节界/岁数换算/原局作用及不同 Variant。
- 流年与岁运作用：日历干支不等于运势；缺原局、大运、流年作用图及强弱/喜忌条件规则。
- 流日：缺流日与原局/岁运关系及时间窗；日历日干支不能直接推每日吉凶。

阻塞：

- 所需解释模块尚无产品级审核授权
- AI未完成真实质量校准及人工语义复核
- 已实现结构Scenario不等于运势/占断；完整解释与发布绑定尚未完成

禁止结论：本周趋势；本周有利日期；本周综合分。

推荐复核来源（本地已存在；不因列在这里自动升 Evidence）：

- `bazi.source.xieji-relations`
- `bazi.source.yuanhai`
- `data/canonical/classics/bazi/ditiansui_chanwei_v1.json`
- `data/canonical/classics/bazi/qiongtong_baojian_v1.json`
- `data/canonical/classics/bazi/yuanhai_ziping_v1.json`

前台降级：当前已实现的结构能力可供专业参考；该项深入解释仍在知识审核中。

## 本月运势

已有：

- 现有 Scenario `monthly`：production_limited，结构执行=True，结构公开标志=False；列出目标公历月每日干支、十神结构与咸池日级命中，并做结构频次汇总；不输出月运吉凶。
- 八字基础与十神映射：术语 3，关联 Phase1 Rule 5，列入结构映射的 Phase2 Rule 3。
  旧资料 `data/canonical/bazi/foundations_v1.json`（实现/描述参考，未授权解释）。
  原文候选 `data/canonical/classics/bazi/ditiansui_chanwei_v1.json#/sections/0/text`；66 个字段命中，仅作待审查定位。
  原文候选 `data/canonical/classics/bazi/qiongtong_baojian_v1.json#/sections/0/title`；51 个字段命中，仅作待审查定位。
  原文候选 `data/canonical/classics/bazi/yuanhai_ziping_v1.json#/sections/0/text`；135 个字段命中，仅作待审查定位。
- 旺衰及流派边界：术语 0，关联 Phase1 Rule 0，列入结构映射的 Phase2 Rule 0。
  原文候选 `data/canonical/classics/bazi/ditiansui_chanwei_v1.json#/sections/2/text`；55 个字段命中，仅作待审查定位。
  原文候选 `data/canonical/classics/bazi/qiongtong_baojian_v1.json#/sections/3/text`；33 个字段命中，仅作待审查定位。
  原文候选 `data/canonical/classics/bazi/yuanhai_ziping_v1.json#/sections/4/text`；51 个字段命中，仅作待审查定位。
- 喜用神分体系治理：术语 0，关联 Phase1 Rule 0，列入结构映射的 Phase2 Rule 0。
- 大运：术语 0，关联 Phase1 Rule 0，列入结构映射的 Phase2 Rule 0。
  旧资料 `data/canonical/bazi/dayun_v1.json`（实现/描述参考，未授权解释）。
  原文候选 `data/canonical/classics/bazi/ditiansui_chanwei_v1.json#/sections/3/text`；9 个字段命中，仅作待审查定位。
  原文候选 `data/canonical/classics/bazi/qiongtong_baojian_v1.json#/sections/11/text`；1 个字段命中，仅作待审查定位。
  原文候选 `data/canonical/classics/bazi/yuanhai_ziping_v1.json#/sections/9/title`；7 个字段命中，仅作待审查定位。
- 流年与岁运作用：术语 1，关联 Phase1 Rule 1，列入结构映射的 Phase2 Rule 0。
  旧资料 `data/canonical/bazi/foundations_v1.json`（实现/描述参考，未授权解释）。
  原文候选 `data/canonical/classics/bazi/ditiansui_chanwei_v1.json#/sections/1/text`；62 个字段命中，仅作待审查定位。
  原文候选 `data/canonical/classics/bazi/qiongtong_baojian_v1.json#/sections/0/text`；59 个字段命中，仅作待审查定位。
  原文候选 `data/canonical/classics/bazi/yuanhai_ziping_v1.json#/sections/0/text`；126 个字段命中，仅作待审查定位。
- 流月：术语 0，关联 Phase1 Rule 0，列入结构映射的 Phase2 Rule 0。
  原文候选 `data/canonical/classics/bazi/ditiansui_chanwei_v1.json#/sections/8/text`；9 个字段命中，仅作待审查定位。
  原文候选 `data/canonical/classics/bazi/yuanhai_ziping_v1.json#/sections/4/text`；20 个字段命中，仅作待审查定位。
- 流日：术语 0，关联 Phase1 Rule 0，列入结构映射的 Phase2 Rule 0。
  原文候选 `data/canonical/classics/bazi/yuanhai_ziping_v1.json#/sections/7/text`；1 个字段命中，仅作待审查定位。

缺失：

- 八字基础与十神映射：四柱/日主/十神/藏干已接入既有模型和执行Golden；仍缺十二长生、月令解释及基础结构到个人结论的条件规则；真太阳时尚未实现。旧表权重不作通用古典结论。
- 旺衰及流派边界：缺命名 school/variant、通根与月令条件、权重依据、冲突记录、执行与反例 Golden；不能用五行数量判断强弱。
- 喜用神分体系治理：调候、扶抑、病药、格局用神未分别治理；依赖旺衰与格局；禁止输出喜用木火等具体结论。
- 大运：旧说明不是执行；须核顺逆/起运法/节界/岁数换算/原局作用及不同 Variant。
- 流年与岁运作用：日历干支不等于运势；缺原局、大运、流年作用图及强弱/喜忌条件规则。
- 流月：缺节气月界/流月与原局、大运、流年作用；公历月复访范围与术数月界须分别记录。
- 流日：缺流日与原局/岁运关系及时间窗；日历日干支不能直接推每日吉凶。

阻塞：

- 所需解释模块尚无产品级审核授权
- AI未完成真实质量校准及人工语义复核
- 已实现结构Scenario不等于运势/占断；完整解释与发布绑定尚未完成

禁止结论：本月吉凶；本月关键时间；本月综合分。

推荐复核来源（本地已存在；不因列在这里自动升 Evidence）：

- `bazi.source.xieji-relations`
- `bazi.source.yuanhai`
- `data/canonical/classics/bazi/ditiansui_chanwei_v1.json`
- `data/canonical/classics/bazi/qiongtong_baojian_v1.json`
- `data/canonical/classics/bazi/yuanhai_ziping_v1.json`

前台降级：当前已实现的结构能力可供专业参考；该项深入解释仍在知识审核中。

## 今年运势

已有：

- 现有 Scenario `yearly`：production_limited，结构执行=True，结构公开标志=False；原局四柱 + 目标干支年 + 流年天干相对日主的十神结构；不输出年度吉凶。
- 八字基础与十神映射：术语 3，关联 Phase1 Rule 5，列入结构映射的 Phase2 Rule 3。
  旧资料 `data/canonical/bazi/foundations_v1.json`（实现/描述参考，未授权解释）。
  原文候选 `data/canonical/classics/bazi/ditiansui_chanwei_v1.json#/sections/0/text`；66 个字段命中，仅作待审查定位。
  原文候选 `data/canonical/classics/bazi/qiongtong_baojian_v1.json#/sections/0/title`；51 个字段命中，仅作待审查定位。
  原文候选 `data/canonical/classics/bazi/yuanhai_ziping_v1.json#/sections/0/text`；135 个字段命中，仅作待审查定位。
- 旺衰及流派边界：术语 0，关联 Phase1 Rule 0，列入结构映射的 Phase2 Rule 0。
  原文候选 `data/canonical/classics/bazi/ditiansui_chanwei_v1.json#/sections/2/text`；55 个字段命中，仅作待审查定位。
  原文候选 `data/canonical/classics/bazi/qiongtong_baojian_v1.json#/sections/3/text`；33 个字段命中，仅作待审查定位。
  原文候选 `data/canonical/classics/bazi/yuanhai_ziping_v1.json#/sections/4/text`；51 个字段命中，仅作待审查定位。
- 喜用神分体系治理：术语 0，关联 Phase1 Rule 0，列入结构映射的 Phase2 Rule 0。
- 大运：术语 0，关联 Phase1 Rule 0，列入结构映射的 Phase2 Rule 0。
  旧资料 `data/canonical/bazi/dayun_v1.json`（实现/描述参考，未授权解释）。
  原文候选 `data/canonical/classics/bazi/ditiansui_chanwei_v1.json#/sections/3/text`；9 个字段命中，仅作待审查定位。
  原文候选 `data/canonical/classics/bazi/qiongtong_baojian_v1.json#/sections/11/text`；1 个字段命中，仅作待审查定位。
  原文候选 `data/canonical/classics/bazi/yuanhai_ziping_v1.json#/sections/9/title`；7 个字段命中，仅作待审查定位。
- 流年与岁运作用：术语 1，关联 Phase1 Rule 1，列入结构映射的 Phase2 Rule 0。
  旧资料 `data/canonical/bazi/foundations_v1.json`（实现/描述参考，未授权解释）。
  原文候选 `data/canonical/classics/bazi/ditiansui_chanwei_v1.json#/sections/1/text`；62 个字段命中，仅作待审查定位。
  原文候选 `data/canonical/classics/bazi/qiongtong_baojian_v1.json#/sections/0/text`；59 个字段命中，仅作待审查定位。
  原文候选 `data/canonical/classics/bazi/yuanhai_ziping_v1.json#/sections/0/text`；126 个字段命中，仅作待审查定位。

缺失：

- 八字基础与十神映射：四柱/日主/十神/藏干已接入既有模型和执行Golden；仍缺十二长生、月令解释及基础结构到个人结论的条件规则；真太阳时尚未实现。旧表权重不作通用古典结论。
- 旺衰及流派边界：缺命名 school/variant、通根与月令条件、权重依据、冲突记录、执行与反例 Golden；不能用五行数量判断强弱。
- 喜用神分体系治理：调候、扶抑、病药、格局用神未分别治理；依赖旺衰与格局；禁止输出喜用木火等具体结论。
- 大运：旧说明不是执行；须核顺逆/起运法/节界/岁数换算/原局作用及不同 Variant。
- 流年与岁运作用：日历干支不等于运势；缺原局、大运、流年作用图及强弱/喜忌条件规则。

阻塞：

- 所需解释模块尚无产品级审核授权
- AI未完成真实质量校准及人工语义复核
- 已实现结构Scenario不等于运势/占断；完整解释与发布绑定尚未完成

禁止结论：流年吉凶；岁运事业财运断语；全年综合分。

推荐复核来源（本地已存在；不因列在这里自动升 Evidence）：

- `bazi.source.xieji-relations`
- `bazi.source.yuanhai`
- `data/canonical/classics/bazi/ditiansui_chanwei_v1.json`
- `data/canonical/classics/bazi/qiongtong_baojian_v1.json`
- `data/canonical/classics/bazi/yuanhai_ziping_v1.json`

前台降级：当前已实现的结构能力可供专业参考；该项深入解释仍在知识审核中。

## 桃花姻缘

已有：

- 现有 Scenario `romance`：production_limited，结构执行=True，结构公开标志=False；分别按年支、日支返回咸池目标支、原局命中与目标年份地支激活；不输出婚恋吉凶。
- 八字基础与十神映射：术语 3，关联 Phase1 Rule 5，列入结构映射的 Phase2 Rule 3。
  旧资料 `data/canonical/bazi/foundations_v1.json`（实现/描述参考，未授权解释）。
  原文候选 `data/canonical/classics/bazi/ditiansui_chanwei_v1.json#/sections/0/text`；66 个字段命中，仅作待审查定位。
  原文候选 `data/canonical/classics/bazi/qiongtong_baojian_v1.json#/sections/0/title`；51 个字段命中，仅作待审查定位。
  原文候选 `data/canonical/classics/bazi/yuanhai_ziping_v1.json#/sections/0/text`；135 个字段命中，仅作待审查定位。
- 旺衰及流派边界：术语 0，关联 Phase1 Rule 0，列入结构映射的 Phase2 Rule 0。
  原文候选 `data/canonical/classics/bazi/ditiansui_chanwei_v1.json#/sections/2/text`；55 个字段命中，仅作待审查定位。
  原文候选 `data/canonical/classics/bazi/qiongtong_baojian_v1.json#/sections/3/text`；33 个字段命中，仅作待审查定位。
  原文候选 `data/canonical/classics/bazi/yuanhai_ziping_v1.json#/sections/4/text`；51 个字段命中，仅作待审查定位。
- 喜用神分体系治理：术语 0，关联 Phase1 Rule 0，列入结构映射的 Phase2 Rule 0。
- 流年与岁运作用：术语 1，关联 Phase1 Rule 1，列入结构映射的 Phase2 Rule 0。
  旧资料 `data/canonical/bazi/foundations_v1.json`（实现/描述参考，未授权解释）。
  原文候选 `data/canonical/classics/bazi/ditiansui_chanwei_v1.json#/sections/1/text`；62 个字段命中，仅作待审查定位。
  原文候选 `data/canonical/classics/bazi/qiongtong_baojian_v1.json#/sections/0/text`；59 个字段命中，仅作待审查定位。
  原文候选 `data/canonical/classics/bazi/yuanhai_ziping_v1.json#/sections/0/text`；126 个字段命中，仅作待审查定位。
- 婚恋专题：术语 8，关联 Phase1 Rule 8，列入结构映射的 Phase2 Rule 8。
  旧资料 `data/canonical/bazi/shensha_v1.json`（实现/描述参考，未授权解释）。
  原文候选 `data/canonical/classics/bazi/ditiansui_chanwei_v1.json#/sections/3/text`；37 个字段命中，仅作待审查定位。
  原文候选 `data/canonical/classics/bazi/qiongtong_baojian_v1.json#/sections/54/text`；1 个字段命中，仅作待审查定位。
  原文候选 `data/canonical/classics/bazi/yuanhai_ziping_v1.json#/sections/5/text`；61 个字段命中，仅作待审查定位。

缺失：

- 八字基础与十神映射：四柱/日主/十神/藏干已接入既有模型和执行Golden；仍缺十二长生、月令解释及基础结构到个人结论的条件规则；真太阳时尚未实现。旧表权重不作通用古典结论。
- 旺衰及流派边界：缺命名 school/variant、通根与月令条件、权重依据、冲突记录、执行与反例 Golden；不能用五行数量判断强弱。
- 喜用神分体系治理：调候、扶抑、病药、格局用神未分别治理；依赖旺衰与格局；禁止输出喜用木火等具体结论。
- 流年与岁运作用：日历干支不等于运势；缺原局、大运、流年作用图及强弱/喜忌条件规则。
- 婚恋专题：咸池、日支传统配偶宫结构位、显式财星/官杀lens及五合/六合/六害/六冲/三合结构已核；缺红鸾天喜天姚、旺衰格局喜用与岁运婚恋解释；三刑争议仍阻塞；禁止命中结构直接断现代婚姻。

阻塞：

- 所需解释模块尚无产品级审核授权
- AI未完成真实质量校准及人工语义复核
- 已实现结构Scenario不等于运势/占断；完整解释与发布绑定尚未完成

禁止结论：结婚时间；桃花概率；由咸池推人品；由官星推现代伴侣身份。

推荐复核来源（本地已存在；不因列在这里自动升 Evidence）：

- `bazi.source.ditiansui-spouse`
- `bazi.source.sanming-xianchi-niutrans`
- `bazi.source.xieji-relations`
- `bazi.source.yuanhai`
- `data/canonical/classics/bazi/ditiansui_chanwei_v1.json`
- `data/canonical/classics/bazi/qiongtong_baojian_v1.json`
- `data/canonical/classics/bazi/yuanhai_ziping_v1.json`

前台降级：当前已实现的结构能力可供专业参考；该项深入解释仍在知识审核中。

## 事业财运

已有：

- 现有 Scenario `career`：production_limited，结构执行=True，结构公开标志=False；聚合原局财星、官杀、食伤、印星、比劫的位置事实，并显示目标年天干十神；不输出事业财运吉凶或评分。
- 八字基础与十神映射：术语 3，关联 Phase1 Rule 5，列入结构映射的 Phase2 Rule 3。
  旧资料 `data/canonical/bazi/foundations_v1.json`（实现/描述参考，未授权解释）。
  原文候选 `data/canonical/classics/bazi/ditiansui_chanwei_v1.json#/sections/0/text`；66 个字段命中，仅作待审查定位。
  原文候选 `data/canonical/classics/bazi/qiongtong_baojian_v1.json#/sections/0/title`；51 个字段命中，仅作待审查定位。
  原文候选 `data/canonical/classics/bazi/yuanhai_ziping_v1.json#/sections/0/text`；135 个字段命中，仅作待审查定位。
- 十神结构与条件解释：术语 1，关联 Phase1 Rule 4，列入结构映射的 Phase2 Rule 2。
  旧资料 `data/canonical/bazi/foundations_v1.json`（实现/描述参考，未授权解释）。
  原文候选 `data/canonical/classics/bazi/ditiansui_chanwei_v1.json#/sections/6/text`；17 个字段命中，仅作待审查定位。
  原文候选 `data/canonical/classics/bazi/qiongtong_baojian_v1.json#/sections/3/text`；33 个字段命中，仅作待审查定位。
  原文候选 `data/canonical/classics/bazi/yuanhai_ziping_v1.json#/sections/12/text`；10 个字段命中，仅作待审查定位。
- 旺衰及流派边界：术语 0，关联 Phase1 Rule 0，列入结构映射的 Phase2 Rule 0。
  原文候选 `data/canonical/classics/bazi/ditiansui_chanwei_v1.json#/sections/2/text`；55 个字段命中，仅作待审查定位。
  原文候选 `data/canonical/classics/bazi/qiongtong_baojian_v1.json#/sections/3/text`；33 个字段命中，仅作待审查定位。
  原文候选 `data/canonical/classics/bazi/yuanhai_ziping_v1.json#/sections/4/text`；51 个字段命中，仅作待审查定位。
- 格局：术语 0，关联 Phase1 Rule 0，列入结构映射的 Phase2 Rule 0。
  原文候选 `data/canonical/classics/bazi/ditiansui_chanwei_v1.json#/sections/7/text`；13 个字段命中，仅作待审查定位。
  原文候选 `data/canonical/classics/bazi/qiongtong_baojian_v1.json#/sections/3/text`；14 个字段命中，仅作待审查定位。
  原文候选 `data/canonical/classics/bazi/yuanhai_ziping_v1.json#/sections/14/text`；14 个字段命中，仅作待审查定位。
- 喜用神分体系治理：术语 0，关联 Phase1 Rule 0，列入结构映射的 Phase2 Rule 0。
- 大运：术语 0，关联 Phase1 Rule 0，列入结构映射的 Phase2 Rule 0。
  旧资料 `data/canonical/bazi/dayun_v1.json`（实现/描述参考，未授权解释）。
  原文候选 `data/canonical/classics/bazi/ditiansui_chanwei_v1.json#/sections/3/text`；9 个字段命中，仅作待审查定位。
  原文候选 `data/canonical/classics/bazi/qiongtong_baojian_v1.json#/sections/11/text`；1 个字段命中，仅作待审查定位。
  原文候选 `data/canonical/classics/bazi/yuanhai_ziping_v1.json#/sections/9/title`；7 个字段命中，仅作待审查定位。
- 流年与岁运作用：术语 1，关联 Phase1 Rule 1，列入结构映射的 Phase2 Rule 0。
  旧资料 `data/canonical/bazi/foundations_v1.json`（实现/描述参考，未授权解释）。
  原文候选 `data/canonical/classics/bazi/ditiansui_chanwei_v1.json#/sections/1/text`；62 个字段命中，仅作待审查定位。
  原文候选 `data/canonical/classics/bazi/qiongtong_baojian_v1.json#/sections/0/text`；59 个字段命中，仅作待审查定位。
  原文候选 `data/canonical/classics/bazi/yuanhai_ziping_v1.json#/sections/0/text`；126 个字段命中，仅作待审查定位。
- 事业财富专题：术语 0，关联 Phase1 Rule 0，列入结构映射的 Phase2 Rule 2。
  原文候选 `data/canonical/classics/bazi/ditiansui_chanwei_v1.json#/sections/3/text`；45 个字段命中，仅作待审查定位。
  原文候选 `data/canonical/classics/bazi/qiongtong_baojian_v1.json#/sections/3/text`；24 个字段命中，仅作待审查定位。
  原文候选 `data/canonical/classics/bazi/yuanhai_ziping_v1.json#/sections/23/text`；39 个字段命中，仅作待审查定位。

缺失：

- 八字基础与十神映射：四柱/日主/十神/藏干已接入既有模型和执行Golden；仍缺十二长生、月令解释及基础结构到个人结论的条件规则；真太阳时尚未实现。旧表权重不作通用古典结论。
- 十神结构与条件解释：映射不等于组合、位置、透藏、月令条件下的解释；须补原典规则、限制及反例。
- 旺衰及流派边界：缺命名 school/variant、通根与月令条件、权重依据、冲突记录、执行与反例 Golden；不能用五行数量判断强弱。
- 格局：正文提及不等于结构规则；缺成格/破格/兼格条件、流派限制和 Golden。
- 喜用神分体系治理：调候、扶抑、病药、格局用神未分别治理；依赖旺衰与格局；禁止输出喜用木火等具体结论。
- 大运：旧说明不是执行；须核顺逆/起运法/节界/岁数换算/原局作用及不同 Variant。
- 流年与岁运作用：日历干支不等于运势；缺原局、大运、流年作用图及强弱/喜忌条件规则。
- 事业财富专题：缺组合、位置、强弱、格局、岁运解释规则；财多身弱须先完成旺衰，不能用财星数量推财富。

阻塞：

- 所需解释模块尚无产品级审核授权
- AI未完成真实质量校准及人工语义复核
- 已实现结构Scenario不等于运势/占断；完整解释与发布绑定尚未完成

禁止结论：发财保证；事业升迁应期；财星多即富；财多身弱判断。

推荐复核来源（本地已存在；不因列在这里自动升 Evidence）：

- `bazi.source.xieji-relations`
- `bazi.source.yuanhai`
- `data/canonical/classics/bazi/ditiansui_chanwei_v1.json`
- `data/canonical/classics/bazi/qiongtong_baojian_v1.json`
- `data/canonical/classics/bazi/yuanhai_ziping_v1.json`

前台降级：当前已实现的结构能力可供专业参考；该项深入解释仍在知识审核中。

## 缘分合盘

已有：

- 现有 Scenario `compatibility`：production_limited，结构执行=True，结构公开标志=False；双人四柱并列、双方日主互看十神、咸池交叉匹配、五合、日支六合/六害/六冲、双方原局三合、跨柱关系矩阵、日支传统配偶宫结构位；用户显式选择传统口径时可附加财星/官杀候选位置。
- 八字基础与十神映射：术语 3，关联 Phase1 Rule 5，列入结构映射的 Phase2 Rule 3。
  旧资料 `data/canonical/bazi/foundations_v1.json`（实现/描述参考，未授权解释）。
  原文候选 `data/canonical/classics/bazi/ditiansui_chanwei_v1.json#/sections/0/text`；66 个字段命中，仅作待审查定位。
  原文候选 `data/canonical/classics/bazi/qiongtong_baojian_v1.json#/sections/0/title`；51 个字段命中，仅作待审查定位。
  原文候选 `data/canonical/classics/bazi/yuanhai_ziping_v1.json#/sections/0/text`；135 个字段命中，仅作待审查定位。
- 旺衰及流派边界：术语 0，关联 Phase1 Rule 0，列入结构映射的 Phase2 Rule 0。
  原文候选 `data/canonical/classics/bazi/ditiansui_chanwei_v1.json#/sections/2/text`；55 个字段命中，仅作待审查定位。
  原文候选 `data/canonical/classics/bazi/qiongtong_baojian_v1.json#/sections/3/text`；33 个字段命中，仅作待审查定位。
  原文候选 `data/canonical/classics/bazi/yuanhai_ziping_v1.json#/sections/4/text`；51 个字段命中，仅作待审查定位。
- 婚恋专题：术语 8，关联 Phase1 Rule 8，列入结构映射的 Phase2 Rule 8。
  旧资料 `data/canonical/bazi/shensha_v1.json`（实现/描述参考，未授权解释）。
  原文候选 `data/canonical/classics/bazi/ditiansui_chanwei_v1.json#/sections/3/text`；37 个字段命中，仅作待审查定位。
  原文候选 `data/canonical/classics/bazi/qiongtong_baojian_v1.json#/sections/54/text`；1 个字段命中，仅作待审查定位。
  原文候选 `data/canonical/classics/bazi/yuanhai_ziping_v1.json#/sections/5/text`；61 个字段命中，仅作待审查定位。
- 流年与岁运作用：术语 1，关联 Phase1 Rule 1，列入结构映射的 Phase2 Rule 0。
  旧资料 `data/canonical/bazi/foundations_v1.json`（实现/描述参考，未授权解释）。
  原文候选 `data/canonical/classics/bazi/ditiansui_chanwei_v1.json#/sections/1/text`；62 个字段命中，仅作待审查定位。
  原文候选 `data/canonical/classics/bazi/qiongtong_baojian_v1.json#/sections/0/text`；59 个字段命中，仅作待审查定位。
  原文候选 `data/canonical/classics/bazi/yuanhai_ziping_v1.json#/sections/0/text`；126 个字段命中，仅作待审查定位。
- 双人关系：术语 10，关联 Phase1 Rule 12，列入结构映射的 Phase2 Rule 9。
  旧资料 `data/canonical/yinyuan/hehun_rules_v1.json`（实现/描述参考，未授权解释）。
  原文候选 `data/canonical/classics/bazi/ditiansui_chanwei_v1.json#/sections/3/text`；57 个字段命中，仅作待审查定位。
  原文候选 `data/canonical/classics/bazi/qiongtong_baojian_v1.json#/sections/3/text`；4 个字段命中，仅作待审查定位。
  原文候选 `data/canonical/classics/bazi/yuanhai_ziping_v1.json#/sections/4/text`；50 个字段命中，仅作待审查定位。

缺失：

- 八字基础与十神映射：四柱/日主/十神/藏干已接入既有模型和执行Golden；仍缺十二长生、月令解释及基础结构到个人结论的条件规则；真太阳时尚未实现。旧表权重不作通用古典结论。
- 旺衰及流派边界：缺命名 school/variant、通根与月令条件、权重依据、冲突记录、执行与反例 Golden；不能用五行数量判断强弱。
- 婚恋专题：咸池、日支传统配偶宫结构位、显式财星/官杀lens及五合/六合/六害/六冲/三合结构已核；缺红鸾天喜天姚、旺衰格局喜用与岁运婚恋解释；三刑争议仍阻塞；禁止命中结构直接断现代婚姻。
- 流年与岁运作用：日历干支不等于运势；缺原局、大运、流年作用图及强弱/喜忌条件规则。
- 双人关系：已有真实双人Scenario、十神镜像、咸池交叉、干支关系矩阵与传统配偶星候选位置；缺双方旺衰/喜忌与共同岁运解释、用户关系结论Golden及发布授权；旧60分不可复用。

阻塞：

- 所需解释模块尚无产品级审核授权
- AI未完成真实质量校准及人工语义复核
- 已实现结构Scenario不等于运势/占断；完整解释与发布绑定尚未完成

禁止结论：合盘匹配分；六合即适婚；六冲必分手；共同婚期。

推荐复核来源（本地已存在；不因列在这里自动升 Evidence）：

- `bazi.source.ditiansui-spouse`
- `bazi.source.sanming-xianchi-niutrans`
- `bazi.source.xieji-relations`
- `bazi.source.yuanhai`
- `data/canonical/classics/bazi/ditiansui_chanwei_v1.json`
- `data/canonical/classics/bazi/qiongtong_baojian_v1.json`
- `data/canonical/classics/bazi/yuanhai_ziping_v1.json`

前台降级：当前已实现的结构能力可供专业参考；该项深入解释仍在知识审核中。

## 人生总览

已有：

- 现有 Scenario `life`：production_limited，结构执行=True，结构公开标志=False；聚合八字基础、年度结构、桃花结构、事业财运结构为一份可读总览；不新增任何吉凶判断。
- 八字基础与十神映射：术语 3，关联 Phase1 Rule 5，列入结构映射的 Phase2 Rule 3。
  旧资料 `data/canonical/bazi/foundations_v1.json`（实现/描述参考，未授权解释）。
  原文候选 `data/canonical/classics/bazi/ditiansui_chanwei_v1.json#/sections/0/text`；66 个字段命中，仅作待审查定位。
  原文候选 `data/canonical/classics/bazi/qiongtong_baojian_v1.json#/sections/0/title`；51 个字段命中，仅作待审查定位。
  原文候选 `data/canonical/classics/bazi/yuanhai_ziping_v1.json#/sections/0/text`；135 个字段命中，仅作待审查定位。
- 旺衰及流派边界：术语 0，关联 Phase1 Rule 0，列入结构映射的 Phase2 Rule 0。
  原文候选 `data/canonical/classics/bazi/ditiansui_chanwei_v1.json#/sections/2/text`；55 个字段命中，仅作待审查定位。
  原文候选 `data/canonical/classics/bazi/qiongtong_baojian_v1.json#/sections/3/text`；33 个字段命中，仅作待审查定位。
  原文候选 `data/canonical/classics/bazi/yuanhai_ziping_v1.json#/sections/4/text`；51 个字段命中，仅作待审查定位。
- 格局：术语 0，关联 Phase1 Rule 0，列入结构映射的 Phase2 Rule 0。
  原文候选 `data/canonical/classics/bazi/ditiansui_chanwei_v1.json#/sections/7/text`；13 个字段命中，仅作待审查定位。
  原文候选 `data/canonical/classics/bazi/qiongtong_baojian_v1.json#/sections/3/text`；14 个字段命中，仅作待审查定位。
  原文候选 `data/canonical/classics/bazi/yuanhai_ziping_v1.json#/sections/14/text`；14 个字段命中，仅作待审查定位。
- 喜用神分体系治理：术语 0，关联 Phase1 Rule 0，列入结构映射的 Phase2 Rule 0。
- 大运：术语 0，关联 Phase1 Rule 0，列入结构映射的 Phase2 Rule 0。
  旧资料 `data/canonical/bazi/dayun_v1.json`（实现/描述参考，未授权解释）。
  原文候选 `data/canonical/classics/bazi/ditiansui_chanwei_v1.json#/sections/3/text`；9 个字段命中，仅作待审查定位。
  原文候选 `data/canonical/classics/bazi/qiongtong_baojian_v1.json#/sections/11/text`；1 个字段命中，仅作待审查定位。
  原文候选 `data/canonical/classics/bazi/yuanhai_ziping_v1.json#/sections/9/title`；7 个字段命中，仅作待审查定位。
- 流年与岁运作用：术语 1，关联 Phase1 Rule 1，列入结构映射的 Phase2 Rule 0。
  旧资料 `data/canonical/bazi/foundations_v1.json`（实现/描述参考，未授权解释）。
  原文候选 `data/canonical/classics/bazi/ditiansui_chanwei_v1.json#/sections/1/text`；62 个字段命中，仅作待审查定位。
  原文候选 `data/canonical/classics/bazi/qiongtong_baojian_v1.json#/sections/0/text`；59 个字段命中，仅作待审查定位。
  原文候选 `data/canonical/classics/bazi/yuanhai_ziping_v1.json#/sections/0/text`；126 个字段命中，仅作待审查定位。
- 婚恋专题：术语 8，关联 Phase1 Rule 8，列入结构映射的 Phase2 Rule 8。
  旧资料 `data/canonical/bazi/shensha_v1.json`（实现/描述参考，未授权解释）。
  原文候选 `data/canonical/classics/bazi/ditiansui_chanwei_v1.json#/sections/3/text`；37 个字段命中，仅作待审查定位。
  原文候选 `data/canonical/classics/bazi/qiongtong_baojian_v1.json#/sections/54/text`；1 个字段命中，仅作待审查定位。
  原文候选 `data/canonical/classics/bazi/yuanhai_ziping_v1.json#/sections/5/text`；61 个字段命中，仅作待审查定位。
- 事业财富专题：术语 0，关联 Phase1 Rule 0，列入结构映射的 Phase2 Rule 2。
  原文候选 `data/canonical/classics/bazi/ditiansui_chanwei_v1.json#/sections/3/text`；45 个字段命中，仅作待审查定位。
  原文候选 `data/canonical/classics/bazi/qiongtong_baojian_v1.json#/sections/3/text`；24 个字段命中，仅作待审查定位。
  原文候选 `data/canonical/classics/bazi/yuanhai_ziping_v1.json#/sections/23/text`；39 个字段命中，仅作待审查定位。
- 人生聚合：术语 0，关联 Phase1 Rule 0，列入结构映射的 Phase2 Rule 0。

缺失：

- 八字基础与十神映射：四柱/日主/十神/藏干已接入既有模型和执行Golden；仍缺十二长生、月令解释及基础结构到个人结论的条件规则；真太阳时尚未实现。旧表权重不作通用古典结论。
- 旺衰及流派边界：缺命名 school/variant、通根与月令条件、权重依据、冲突记录、执行与反例 Golden；不能用五行数量判断强弱。
- 格局：正文提及不等于结构规则；缺成格/破格/兼格条件、流派限制和 Golden。
- 喜用神分体系治理：调候、扶抑、病药、格局用神未分别治理；依赖旺衰与格局；禁止输出喜用木火等具体结论。
- 大运：旧说明不是执行；须核顺逆/起运法/节界/岁数换算/原局作用及不同 Variant。
- 流年与岁运作用：日历干支不等于运势；缺原局、大运、流年作用图及强弱/喜忌条件规则。
- 婚恋专题：咸池、日支传统配偶宫结构位、显式财星/官杀lens及五合/六合/六害/六冲/三合结构已核；缺红鸾天喜天姚、旺衰格局喜用与岁运婚恋解释；三刑争议仍阻塞；禁止命中结构直接断现代婚姻。
- 事业财富专题：缺组合、位置、强弱、格局、岁运解释规则；财多身弱须先完成旺衰，不能用财星数量推财富。
- 人生聚合：只能组合已审核模块；缺模块授权、证据去重、冲突优先级、历史记录及综合指数依据；不另建人生算法。

阻塞：

- 所需解释模块尚无产品级审核授权
- AI未完成真实质量校准及人工语义复核
- 已实现结构Scenario不等于运势/占断；完整解释与发布绑定尚未完成

禁止结论：人生总分；健康寿命断语；未经模块审核的人生结论。

推荐复核来源（本地已存在；不因列在这里自动升 Evidence）：

- `bazi.source.ditiansui-spouse`
- `bazi.source.sanming-xianchi-niutrans`
- `bazi.source.xieji-relations`
- `bazi.source.yuanhai`
- `data/canonical/classics/bazi/ditiansui_chanwei_v1.json`
- `data/canonical/classics/bazi/qiongtong_baojian_v1.json`
- `data/canonical/classics/bazi/yuanhai_ziping_v1.json`

前台降级：当前已实现的结构能力可供专业参考；该项深入解释仍在知识审核中。

## AI解梦

已有：

- 现有 Scenario `dream`：research，结构执行=False，结构公开标志=False；待梦境语料与真实模型校准。
- 传统梦文化：术语 0，关联 Phase1 Rule 0，列入结构映射的 Phase2 Rule 0。
- 现代心理梦研究：术语 0，关联 Phase1 Rule 0，列入结构映射的 Phase2 Rule 0。

缺失：

- 传统梦文化：缺独立梦境来源、实体/象征/关系、source_ref、interpretation/type/confidence/cultural_context；现有文本偶见梦字不计覆盖。
- 现代心理梦研究：缺独立研究资料及许可审核；不得借古籍背书心理理论，不诊断、不从梦推怀孕/疾病/未来；与传统文化分段展示。

阻塞：

- 所需解释模块尚无产品级审核授权
- AI未完成真实质量校准及人工语义复核
- 已实现结构Scenario不等于运势/占断；完整解释与发布绑定尚未完成

禁止结论：无检索解梦；疾病或怀孕诊断；梦预示未来；心理理论冒充古籍。

推荐复核来源（本地已存在；不因列在这里自动升 Evidence）：

- 当前无已审核专属来源；先来源登记与 Quarantine，不编造书名/摘录。

前台降级：当前版本尚未开放，相关知识、规则与证据仍在校核中。

## 一事占问

已有：

- 现有 Scenario `question`：production，结构执行=True，结构公开标志=True；六爻确定性盘面、规则、典籍依据与 Trace。
- 六爻占问深化：术语 23，关联 Phase1 Rule 19，列入结构映射的 Phase2 Rule 7。
- 奇门专业能力：术语 13，关联 Phase1 Rule 3，列入结构映射的 Phase2 Rule 5。

缺失：

- 六爻占问深化：排盘七项结构已执行；术语/描述规则不等于占断；缺用神选取、旺衰、生克动变与应期解释的可执行链路。
- 奇门专业能力：指定精确节气转盘结构已执行；缺格局/用神解释；置闰、超接及其他盘法未实现。

阻塞：

- 所需解释模块尚无产品级审核授权
- AI未完成真实质量校准及人工语义复核
- 已实现结构Scenario不等于运势/占断；完整解释与发布绑定尚未完成

禁止结论：事件必成必败；应期断定；自由选择未实现流派。

推荐复核来源（本地已存在；不因列在这里自动升 Evidence）：

- `liuyao.source.bushi`
- `liuyao.source.zengshan`
- `qimen.source.baojian`
- `qimen.source.tongzong`

前台降级：当前已实现的结构能力可供专业参考；该项深入解释仍在知识审核中。

## 紫微专业工具

已有：

- 紫微专业能力：术语 12，关联 Phase1 Rule 1，列入结构映射的 Phase2 Rule 6。

缺失：

- 紫微专业能力：基本星宫结构已执行；缺亮度/三方四正/宫位解释/大限流年；闰月未裁定，四化D约定不能升古籍结论。

阻塞：

- 所需解释模块尚无产品级审核授权
- AI未完成真实质量校准及人工语义复核
- 已实现结构Scenario不等于运势/占断；完整解释与发布绑定尚未完成

禁止结论：大限流年吉凶；庙旺吉凶；闰月自动猜排。

推荐复核来源（本地已存在；不因列在这里自动升 Evidence）：

- `ziwei.source.quanshu`

前台降级：当前已实现的结构能力可供专业参考；该项深入解释仍在知识审核中。

## 奇门专业工具

已有：

- 奇门专业能力：术语 13，关联 Phase1 Rule 3，列入结构映射的 Phase2 Rule 5。

缺失：

- 奇门专业能力：指定精确节气转盘结构已执行；缺格局/用神解释；置闰、超接及其他盘法未实现。

阻塞：

- 所需解释模块尚无产品级审核授权
- AI未完成真实质量校准及人工语义复核
- 已实现结构Scenario不等于运势/占断；完整解释与发布绑定尚未完成

禁止结论：格局吉凶；择时胜率；置闰超接盘。

推荐复核来源（本地已存在；不因列在这里自动升 Evidence）：

- `qimen.source.baojian`
- `qimen.source.tongzong`

前台降级：当前已实现的结构能力可供专业参考；该项深入解释仍在知识审核中。

## 六壬专业工具

已有：

- 六壬专业能力：术语 16，关联 Phase1 Rule 14，列入结构映射的 Phase2 Rule 12。

缺失：

- 六壬专业能力：九宗门结构已执行；贵人双表/天后异文保留，缺神将排布、类神、旺衰与占类解释。

阻塞：

- 所需解释模块尚无产品级审核授权
- AI未完成真实质量校准及人工语义复核
- 已实现结构Scenario不等于运势/占断；完整解释与发布绑定尚未完成

禁止结论：十二天将已排；类神吉凶；应期。

推荐复核来源（本地已存在；不因列在这里自动升 Evidence）：

- `liuren.source.daquan`
- `liuren.source.zhinan`

前台降级：当前已实现的结构能力可供专业参考；该项深入解释仍在知识审核中。

## 风水专业工具

已有：

- 风水专业能力：术语 4，关联 Phase1 Rule 1，列入结构映射的 Phase2 Rule 1。
  旧资料 `data/canonical/fengshui/schools_v1.json`（实现/描述参考，未授权解释）。

缺失：

- 风水专业能力：生产计算只支持二十四山定位；三元绝对纪元仍研究，缺八宅/三元/玄空各自执行和解释，不串体系。

阻塞：

- 所需解释模块尚无产品级审核授权
- AI未完成真实质量校准及人工语义复核
- 已实现结构Scenario不等于运势/占断；完整解释与发布绑定尚未完成

禁止结论：飞星吉凶；宅运财运；绝对三元九运生产判断。

推荐复核来源（本地已存在；不因列在这里自动升 Evidence）：

- `fengshui.source.dibian`
- `fengshui.source.yangzhai`

前台降级：当前已实现的结构能力可供专业参考；该项深入解释仍在知识审核中。

## 周易专业工具

已有：

- 周易专业能力：术语 7，关联 Phase1 Rule 6，列入结构映射的 Phase2 Rule 5。
  旧资料 `data/canonical/yijing/zhouyi_classic_core.json`（实现/描述参考，未授权解释）。
  旧资料 `data/canonical/yijing/tuan_xiang_wenyan_v1.json`（实现/描述参考，未授权解释）。

缺失：

- 周易专业能力：结构和卦爻文本可追溯；缺面向事件的解释规则；经典原义与后世术数解释必须分开。

阻塞：

- 所需解释模块尚无产品级审核授权
- AI未完成真实质量校准及人工语义复核
- 已实现结构Scenario不等于运势/占断；完整解释与发布绑定尚未完成

禁止结论：卦义直接推具体事件；未来概率；后世术数冒充原义。

推荐复核来源（本地已存在；不因列在这里自动升 Evidence）：

- `yijing.source.meihua`
- `yijing.source.shuogua`
- `yijing.source.xici`

前台降级：当前已实现的结构能力可供专业参考；该项深入解释仍在知识审核中。

## 本批范围及未完成项

本批完成实查报告、两部既有来源的隔离复核候选、知命前段一条描述性解释边界及失败即拒绝的产品解释门控；未新增可执行推断、未开放产品、未上线 AI。
新增 `bazi.rule.r012`、`bazi.term.strength_review_boundary`、`bazi.section.s022` 与章节均沿用既有模型。规则保持descriptive_only，不参与执行RuleMatch，不伪造算法或Golden；已有34个结构Golden保留，解释性Golden与Phase2编译继续阻塞。
八字旺衰/格局/喜用/岁运解释治理、独立梦境资料、解释性 Golden、产品授权与模型质量校准仍须按上述批次完成。
