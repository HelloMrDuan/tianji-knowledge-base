# 测算产品 × 知识库覆盖及缺口

由 `scripts/build_product_coverage.py` 扫描实际 JSON、来源、执行契约、Golden、代码和 RAG 自动生成。运行 `--check` 检查漂移。

这是现有知识库的派生报告，不是新知识模型、Rule 或上线授权。所有产品解释均未开放；结构计算与完整测算报告分开评估。

实际文件：Canonical 74，Quarantine 117；来源登记 37；逐项证据来源 93。
已注册确定性引擎 6 个，Phase2 Rule 37 条，Golden 28 个；八字与梦境引擎未注册。
证据等级 {"C": 87, "D": 6}；旧 registry trust_level A/B 不等于独立古典 Evidence A/B。
RAG：已审核实体 692 块；通用 2421 块，含旧资料，不能代替执行命中。

| 产品 | 所需专题 | 已有 | 缺失/阻塞 | 完整产品可生产 |
|---|---|---|---|---|
| 八字详批 | 八字基础与十神映射、十神结构与条件解释、旺衰及流派边界、格局、喜用神分体系治理、大运、流年与岁运作用 | 旧表/正文候选 | 缺产品解释及门控链路，详见下文 | 否 |
| 今日运势 | 八字基础与十神映射、旺衰及流派边界、喜用神分体系治理、大运、流年与岁运作用、流日 | 旧表/正文候选 | 缺产品解释及门控链路，详见下文 | 否 |
| 本周运势 | 八字基础与十神映射、旺衰及流派边界、喜用神分体系治理、大运、流年与岁运作用、流日 | 旧表/正文候选 | 缺产品解释及门控链路，详见下文 | 否 |
| 本月运势 | 八字基础与十神映射、旺衰及流派边界、喜用神分体系治理、大运、流年与岁运作用、流月、流日 | 旧表/正文候选 | 缺产品解释及门控链路，详见下文 | 否 |
| 今年运势 | 八字基础与十神映射、旺衰及流派边界、喜用神分体系治理、大运、流年与岁运作用 | 旧表/正文候选 | 缺产品解释及门控链路，详见下文 | 否 |
| 桃花姻缘 | 八字基础与十神映射、旺衰及流派边界、喜用神分体系治理、流年与岁运作用、婚恋专题 | 旧表/正文候选 | 缺产品解释及门控链路，详见下文 | 否 |
| 事业财运 | 八字基础与十神映射、十神结构与条件解释、旺衰及流派边界、格局、喜用神分体系治理、大运、流年与岁运作用、事业财富专题 | 旧表/正文候选 | 缺产品解释及门控链路，详见下文 | 否 |
| 缘分合盘 | 八字基础与十神映射、旺衰及流派边界、婚恋专题、流年与岁运作用、双人关系 | 旧表/正文候选 | 缺产品解释及门控链路，详见下文 | 否 |
| 人生总览 | 八字基础与十神映射、旺衰及流派边界、格局、喜用神分体系治理、大运、流年与岁运作用、婚恋专题、事业财富专题、人生聚合 | 旧表/正文候选 | 缺产品解释及门控链路，详见下文 | 否 |
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
现有六域 `phase1_knowledge.json` 与 `knowledge_sources.json` 使用既有 schema / `validate_knowledge`；Phase2 用既有执行、补充证据、来源审计、晋级记录、Golden 和 `validate_phase2.py`。
当前 Phase1 schema 与 domain registry 明确限于六域；八字、梦境尚未接入。后续应审核扩展同一模型的领域枚举及既有校验，不另外造一套知识结构；本批不修改 schema、不自动晋级。

## 迭代顺序与小批量验收

P0：八字基础/十神 → 旺衰（先选并核单一 Variant）→ 格局 → 四套喜用体系分别治理 → 大运/流年 → 婚恋/事业财富 → 双人关系；梦境来源审查可独立进行。
P1：六爻解释深化、流月、流日、人生聚合；P2：紫微、奇门、六壬、风水扩展、周易专业。
首批优先复核现有《滴天髓阐微》知命/夫妻/女命、《渊海子平》月令/大运及《穷通宝鉴》月令材料。先抽少量原文与限制，保存反例；不得从整本存在直接推规则已审核。
每批只处理一个明确条件关系及反例：检查来源权利/版本/字面 → 已有模型引用 → 命名 Variant 与适用边界 → 固定 Golden/反例 → 测试 → 执行晋级记录；缺任何一步继续隔离。
六爻优先复用已登记《增删卜易》《卜筮正宗》；专业域优先复用下列真实 source_id。梦境当前无已登记专库，先做来源/权利审核，不能借命理语料或模型先验填充。

## 结论能力门控

`product_claims.py` 复用 EvidenceResolver、现有 explanation_policy 和 validate_reply；检查事实存在、可执行 Rule、Golden、等级/Variant、来源冲突。产品入口在模型调用前拒绝未开放的 Scenario。
完整产品授权/claim白名单与模型人工复核绑定契约尚未实现；当前不接受改几个布尔值作为发布授权。此门控保持关闭，不宣称已完成全部生产放行能力。
当前全部 `production_claims=[]`，公开解释一律拒绝。新 Prompt v3 明示 “Absence of knowledge is not permission to use model prior knowledge.”；旧 v1/v2 保持不可变，仅供既有评测比较。
自由文本的语义蕴涵不能只靠 JSON/关键词证明；现有人工语义审核仍是必要步骤，门控测试不等于模型质量达标。

## 冲突与隔离边界

当前无独立school_conflict实体；已有Rule difference/exceptions、执行unresolved与来源审计，不能把空集合解释为无流派冲突。
《三命通会》保持 quarantine_only / canonical_ready=false；原始 snapshot、已确认 PUA/OCR 映射未修改，不能进入 Canonical/RAG。

## 实查六域模型

| 域 | Classics | Chapters | Sections | Terms | Rules | Concepts |
|---|---:|---:|---:|---:|---:|---:|
| yijing | 4 | 85 | 104 | 19 | 6 | 73 |
| liuyao | 2 | 4 | 38 | 30 | 24 | 8 |
| qimen | 2 | 6 | 33 | 44 | 6 | 10 |
| ziwei | 1 | 15 | 44 | 48 | 11 | 14 |
| fengshui | 6 | 9 | 22 | 37 | 8 | 3 |
| liuren | 2 | 35 | 42 | 42 | 14 | 12 |

## 首批来源隔离及编辑标记审核

已按现有 `acquisition.stage_candidate` 保存以下固定来源的 RAW（忽略缓存）及 Quarantine 元数据；Git blob校验通过，review_status=pending，promotion_allowed=false。没有新增正式知识或来源等级。

- `易藏/术数/渊海子平.txt` @ `4a6d6f2088825f132521d848c2ea86cf9c9a7620`，blob `c7de6ab493e19460f5efba49085d20437c17e1d4`。
- `易藏/术数/滴天髓阐微.txt` @ `4a6d6f2088825f132521d848c2ea86cf9c9a7620`，blob `e269843d0544fd18ac7d7c97d4e0bd268a5240ef`。

原典审核前须处理下列编者/增补标记（定位到实际 JSON；不自动删改旧文件）：

- `data/canonical/classics/bazi/ditiansui_chanwei_v1.json#/sections/3/text`：若思按、(新增)。
- `data/canonical/classics/bazi/ditiansui_chanwei_v1.json#/sections/4/text`：若思按。
- `data/canonical/classics/bazi/ditiansui_chanwei_v1.json#/sections/7/text`：若思按。

现有来源 schema 未显式包含 edition；93条来源的 edition 不可从书名推定。版本核验仍按现有来源审计记录，正式扩展应保持同一治理模型。

实查 API：GET `/api/v1/capabilities`；POST `/api/v1/execute`；GET `/health`。尚无产品 Scenario/历史记录/管理写入 API。

## 八字详批

已有：

- 八字基础与十神映射：术语 0，关联 Phase1 Rule 0，列入结构映射的 Phase2 Rule 0。
  旧资料 `data/canonical/bazi/foundations_v1.json`（实现/描述参考，未授权解释）。
  原文候选 `data/canonical/classics/bazi/ditiansui_chanwei_v1.json#/sections/0/text`；66 个字段命中，仅作待审查定位。
  原文候选 `data/canonical/classics/bazi/qiongtong_baojian_v1.json#/sections/0/title`；51 个字段命中，仅作待审查定位。
  原文候选 `data/canonical/classics/bazi/yuanhai_ziping_v1.json#/sections/0/text`；135 个字段命中，仅作待审查定位。
- 十神结构与条件解释：术语 0，关联 Phase1 Rule 0，列入结构映射的 Phase2 Rule 0。
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
- 流年与岁运作用：术语 0，关联 Phase1 Rule 0，列入结构映射的 Phase2 Rule 0。
  旧资料 `data/canonical/bazi/foundations_v1.json`（实现/描述参考，未授权解释）。
  原文候选 `data/canonical/classics/bazi/ditiansui_chanwei_v1.json#/sections/1/text`；62 个字段命中，仅作待审查定位。
  原文候选 `data/canonical/classics/bazi/qiongtong_baojian_v1.json#/sections/0/text`；59 个字段命中，仅作待审查定位。
  原文候选 `data/canonical/classics/bazi/yuanhai_ziping_v1.json#/sections/0/text`；126 个字段命中，仅作待审查定位。

缺失：

- 八字基础与十神映射：缺八字 Phase1 注册、原典逐项绑定、出生时间/四柱执行契约及 Golden；旧实现表的权重不作通用古典结论。
- 十神结构与条件解释：映射不等于组合、位置、透藏、月令条件下的解释；须补原典规则、限制及反例。
- 旺衰及流派边界：缺命名 school/variant、通根与月令条件、权重依据、冲突记录、执行与反例 Golden；不能用五行数量判断强弱。
- 格局：正文提及不等于结构规则；缺成格/破格/兼格条件、流派限制和 Golden。
- 喜用神分体系治理：调候、扶抑、病药、格局用神未分别治理；依赖旺衰与格局；禁止输出喜用木火等具体结论。
- 大运：旧说明不是执行；须核顺逆/起运法/节界/岁数换算/原局作用及不同 Variant。
- 流年与岁运作用：日历干支不等于运势；缺原局、大运、流年作用图及强弱/喜忌条件规则。

阻塞：

- 所需解释模块尚无产品级审核授权
- AI未完成真实质量校准及人工语义复核
- Scenario尚未实现并验证完整聚合/检索/门控链路

禁止结论：身强身弱；格局成立；具体喜用神；完整详批。

推荐复核来源（本地已存在；不因列在这里自动升 Evidence）：

- `data/canonical/classics/bazi/ditiansui_chanwei_v1.json`
- `data/canonical/classics/bazi/qiongtong_baojian_v1.json`
- `data/canonical/classics/bazi/yuanhai_ziping_v1.json`

前台降级：当前版本尚未开放，相关知识、规则与证据仍在校核中。

## 今日运势

已有：

- 八字基础与十神映射：术语 0，关联 Phase1 Rule 0，列入结构映射的 Phase2 Rule 0。
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
- 流年与岁运作用：术语 0，关联 Phase1 Rule 0，列入结构映射的 Phase2 Rule 0。
  旧资料 `data/canonical/bazi/foundations_v1.json`（实现/描述参考，未授权解释）。
  原文候选 `data/canonical/classics/bazi/ditiansui_chanwei_v1.json#/sections/1/text`；62 个字段命中，仅作待审查定位。
  原文候选 `data/canonical/classics/bazi/qiongtong_baojian_v1.json#/sections/0/text`；59 个字段命中，仅作待审查定位。
  原文候选 `data/canonical/classics/bazi/yuanhai_ziping_v1.json#/sections/0/text`；126 个字段命中，仅作待审查定位。
- 流日：术语 0，关联 Phase1 Rule 0，列入结构映射的 Phase2 Rule 0。
  原文候选 `data/canonical/classics/bazi/yuanhai_ziping_v1.json#/sections/7/text`；1 个字段命中，仅作待审查定位。

缺失：

- 八字基础与十神映射：缺八字 Phase1 注册、原典逐项绑定、出生时间/四柱执行契约及 Golden；旧实现表的权重不作通用古典结论。
- 旺衰及流派边界：缺命名 school/variant、通根与月令条件、权重依据、冲突记录、执行与反例 Golden；不能用五行数量判断强弱。
- 喜用神分体系治理：调候、扶抑、病药、格局用神未分别治理；依赖旺衰与格局；禁止输出喜用木火等具体结论。
- 大运：旧说明不是执行；须核顺逆/起运法/节界/岁数换算/原局作用及不同 Variant。
- 流年与岁运作用：日历干支不等于运势；缺原局、大运、流年作用图及强弱/喜忌条件规则。
- 流日：缺流日与原局/岁运关系及时间窗；日历日干支不能直接推每日吉凶。

阻塞：

- 所需解释模块尚无产品级审核授权
- AI未完成真实质量校准及人工语义复核
- Scenario尚未实现并验证完整聚合/检索/门控链路

禁止结论：今日吉凶；今日综合分；今日财运/桃花概率。

推荐复核来源（本地已存在；不因列在这里自动升 Evidence）：

- `data/canonical/classics/bazi/ditiansui_chanwei_v1.json`
- `data/canonical/classics/bazi/qiongtong_baojian_v1.json`
- `data/canonical/classics/bazi/yuanhai_ziping_v1.json`

前台降级：当前版本尚未开放，相关知识、规则与证据仍在校核中。

## 本周运势

已有：

- 八字基础与十神映射：术语 0，关联 Phase1 Rule 0，列入结构映射的 Phase2 Rule 0。
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
- 流年与岁运作用：术语 0，关联 Phase1 Rule 0，列入结构映射的 Phase2 Rule 0。
  旧资料 `data/canonical/bazi/foundations_v1.json`（实现/描述参考，未授权解释）。
  原文候选 `data/canonical/classics/bazi/ditiansui_chanwei_v1.json#/sections/1/text`；62 个字段命中，仅作待审查定位。
  原文候选 `data/canonical/classics/bazi/qiongtong_baojian_v1.json#/sections/0/text`；59 个字段命中，仅作待审查定位。
  原文候选 `data/canonical/classics/bazi/yuanhai_ziping_v1.json#/sections/0/text`；126 个字段命中，仅作待审查定位。
- 流日：术语 0，关联 Phase1 Rule 0，列入结构映射的 Phase2 Rule 0。
  原文候选 `data/canonical/classics/bazi/yuanhai_ziping_v1.json#/sections/7/text`；1 个字段命中，仅作待审查定位。

缺失：

- 八字基础与十神映射：缺八字 Phase1 注册、原典逐项绑定、出生时间/四柱执行契约及 Golden；旧实现表的权重不作通用古典结论。
- 旺衰及流派边界：缺命名 school/variant、通根与月令条件、权重依据、冲突记录、执行与反例 Golden；不能用五行数量判断强弱。
- 喜用神分体系治理：调候、扶抑、病药、格局用神未分别治理；依赖旺衰与格局；禁止输出喜用木火等具体结论。
- 大运：旧说明不是执行；须核顺逆/起运法/节界/岁数换算/原局作用及不同 Variant。
- 流年与岁运作用：日历干支不等于运势；缺原局、大运、流年作用图及强弱/喜忌条件规则。
- 流日：缺流日与原局/岁运关系及时间窗；日历日干支不能直接推每日吉凶。

阻塞：

- 所需解释模块尚无产品级审核授权
- AI未完成真实质量校准及人工语义复核
- Scenario尚未实现并验证完整聚合/检索/门控链路

禁止结论：本周趋势；本周有利日期；本周综合分。

推荐复核来源（本地已存在；不因列在这里自动升 Evidence）：

- `data/canonical/classics/bazi/ditiansui_chanwei_v1.json`
- `data/canonical/classics/bazi/qiongtong_baojian_v1.json`
- `data/canonical/classics/bazi/yuanhai_ziping_v1.json`

前台降级：当前版本尚未开放，相关知识、规则与证据仍在校核中。

## 本月运势

已有：

- 八字基础与十神映射：术语 0，关联 Phase1 Rule 0，列入结构映射的 Phase2 Rule 0。
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
- 流年与岁运作用：术语 0，关联 Phase1 Rule 0，列入结构映射的 Phase2 Rule 0。
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

- 八字基础与十神映射：缺八字 Phase1 注册、原典逐项绑定、出生时间/四柱执行契约及 Golden；旧实现表的权重不作通用古典结论。
- 旺衰及流派边界：缺命名 school/variant、通根与月令条件、权重依据、冲突记录、执行与反例 Golden；不能用五行数量判断强弱。
- 喜用神分体系治理：调候、扶抑、病药、格局用神未分别治理；依赖旺衰与格局；禁止输出喜用木火等具体结论。
- 大运：旧说明不是执行；须核顺逆/起运法/节界/岁数换算/原局作用及不同 Variant。
- 流年与岁运作用：日历干支不等于运势；缺原局、大运、流年作用图及强弱/喜忌条件规则。
- 流月：缺节气月界/流月与原局、大运、流年作用；公历月复访范围与术数月界须分别记录。
- 流日：缺流日与原局/岁运关系及时间窗；日历日干支不能直接推每日吉凶。

阻塞：

- 所需解释模块尚无产品级审核授权
- AI未完成真实质量校准及人工语义复核
- Scenario尚未实现并验证完整聚合/检索/门控链路

禁止结论：本月吉凶；本月关键时间；本月综合分。

推荐复核来源（本地已存在；不因列在这里自动升 Evidence）：

- `data/canonical/classics/bazi/ditiansui_chanwei_v1.json`
- `data/canonical/classics/bazi/qiongtong_baojian_v1.json`
- `data/canonical/classics/bazi/yuanhai_ziping_v1.json`

前台降级：当前版本尚未开放，相关知识、规则与证据仍在校核中。

## 今年运势

已有：

- 八字基础与十神映射：术语 0，关联 Phase1 Rule 0，列入结构映射的 Phase2 Rule 0。
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
- 流年与岁运作用：术语 0，关联 Phase1 Rule 0，列入结构映射的 Phase2 Rule 0。
  旧资料 `data/canonical/bazi/foundations_v1.json`（实现/描述参考，未授权解释）。
  原文候选 `data/canonical/classics/bazi/ditiansui_chanwei_v1.json#/sections/1/text`；62 个字段命中，仅作待审查定位。
  原文候选 `data/canonical/classics/bazi/qiongtong_baojian_v1.json#/sections/0/text`；59 个字段命中，仅作待审查定位。
  原文候选 `data/canonical/classics/bazi/yuanhai_ziping_v1.json#/sections/0/text`；126 个字段命中，仅作待审查定位。

缺失：

- 八字基础与十神映射：缺八字 Phase1 注册、原典逐项绑定、出生时间/四柱执行契约及 Golden；旧实现表的权重不作通用古典结论。
- 旺衰及流派边界：缺命名 school/variant、通根与月令条件、权重依据、冲突记录、执行与反例 Golden；不能用五行数量判断强弱。
- 喜用神分体系治理：调候、扶抑、病药、格局用神未分别治理；依赖旺衰与格局；禁止输出喜用木火等具体结论。
- 大运：旧说明不是执行；须核顺逆/起运法/节界/岁数换算/原局作用及不同 Variant。
- 流年与岁运作用：日历干支不等于运势；缺原局、大运、流年作用图及强弱/喜忌条件规则。

阻塞：

- 所需解释模块尚无产品级审核授权
- AI未完成真实质量校准及人工语义复核
- Scenario尚未实现并验证完整聚合/检索/门控链路

禁止结论：流年吉凶；岁运事业财运断语；全年综合分。

推荐复核来源（本地已存在；不因列在这里自动升 Evidence）：

- `data/canonical/classics/bazi/ditiansui_chanwei_v1.json`
- `data/canonical/classics/bazi/qiongtong_baojian_v1.json`
- `data/canonical/classics/bazi/yuanhai_ziping_v1.json`

前台降级：当前版本尚未开放，相关知识、规则与证据仍在校核中。

## 桃花姻缘

已有：

- 八字基础与十神映射：术语 0，关联 Phase1 Rule 0，列入结构映射的 Phase2 Rule 0。
  旧资料 `data/canonical/bazi/foundations_v1.json`（实现/描述参考，未授权解释）。
  原文候选 `data/canonical/classics/bazi/ditiansui_chanwei_v1.json#/sections/0/text`；66 个字段命中，仅作待审查定位。
  原文候选 `data/canonical/classics/bazi/qiongtong_baojian_v1.json#/sections/0/title`；51 个字段命中，仅作待审查定位。
  原文候选 `data/canonical/classics/bazi/yuanhai_ziping_v1.json#/sections/0/text`；135 个字段命中，仅作待审查定位。
- 旺衰及流派边界：术语 0，关联 Phase1 Rule 0，列入结构映射的 Phase2 Rule 0。
  原文候选 `data/canonical/classics/bazi/ditiansui_chanwei_v1.json#/sections/2/text`；55 个字段命中，仅作待审查定位。
  原文候选 `data/canonical/classics/bazi/qiongtong_baojian_v1.json#/sections/3/text`；33 个字段命中，仅作待审查定位。
  原文候选 `data/canonical/classics/bazi/yuanhai_ziping_v1.json#/sections/4/text`；51 个字段命中，仅作待审查定位。
- 喜用神分体系治理：术语 0，关联 Phase1 Rule 0，列入结构映射的 Phase2 Rule 0。
- 流年与岁运作用：术语 0，关联 Phase1 Rule 0，列入结构映射的 Phase2 Rule 0。
  旧资料 `data/canonical/bazi/foundations_v1.json`（实现/描述参考，未授权解释）。
  原文候选 `data/canonical/classics/bazi/ditiansui_chanwei_v1.json#/sections/1/text`；62 个字段命中，仅作待审查定位。
  原文候选 `data/canonical/classics/bazi/qiongtong_baojian_v1.json#/sections/0/text`；59 个字段命中，仅作待审查定位。
  原文候选 `data/canonical/classics/bazi/yuanhai_ziping_v1.json#/sections/0/text`；126 个字段命中，仅作待审查定位。
- 婚恋专题：术语 0，关联 Phase1 Rule 0，列入结构映射的 Phase2 Rule 0。
  旧资料 `data/canonical/bazi/shensha_v1.json`（实现/描述参考，未授权解释）。
  原文候选 `data/canonical/classics/bazi/ditiansui_chanwei_v1.json#/sections/3/text`；37 个字段命中，仅作待审查定位。
  原文候选 `data/canonical/classics/bazi/qiongtong_baojian_v1.json#/sections/54/text`；1 个字段命中，仅作待审查定位。
  原文候选 `data/canonical/classics/bazi/yuanhai_ziping_v1.json#/sections/5/text`；61 个字段命中，仅作待审查定位。

缺失：

- 八字基础与十神映射：缺八字 Phase1 注册、原典逐项绑定、出生时间/四柱执行契约及 Golden；旧实现表的权重不作通用古典结论。
- 旺衰及流派边界：缺命名 school/variant、通根与月令条件、权重依据、冲突记录、执行与反例 Golden；不能用五行数量判断强弱。
- 喜用神分体系治理：调候、扶抑、病药、格局用神未分别治理；依赖旺衰与格局；禁止输出喜用木火等具体结论。
- 流年与岁运作用：日历干支不等于运势；缺原局、大运、流年作用图及强弱/喜忌条件规则。
- 婚恋专题：缺配偶宫/星的条件规则与岁运触发；保存传统性别 lens 与批判材料，现代中性表达另审，不以咸池或官星断人品/婚姻。

阻塞：

- 所需解释模块尚无产品级审核授权
- AI未完成真实质量校准及人工语义复核
- Scenario尚未实现并验证完整聚合/检索/门控链路

禁止结论：结婚时间；桃花概率；由咸池推人品；由官星推现代伴侣身份。

推荐复核来源（本地已存在；不因列在这里自动升 Evidence）：

- `data/canonical/classics/bazi/ditiansui_chanwei_v1.json`
- `data/canonical/classics/bazi/qiongtong_baojian_v1.json`
- `data/canonical/classics/bazi/yuanhai_ziping_v1.json`

前台降级：当前版本尚未开放，相关知识、规则与证据仍在校核中。

## 事业财运

已有：

- 八字基础与十神映射：术语 0，关联 Phase1 Rule 0，列入结构映射的 Phase2 Rule 0。
  旧资料 `data/canonical/bazi/foundations_v1.json`（实现/描述参考，未授权解释）。
  原文候选 `data/canonical/classics/bazi/ditiansui_chanwei_v1.json#/sections/0/text`；66 个字段命中，仅作待审查定位。
  原文候选 `data/canonical/classics/bazi/qiongtong_baojian_v1.json#/sections/0/title`；51 个字段命中，仅作待审查定位。
  原文候选 `data/canonical/classics/bazi/yuanhai_ziping_v1.json#/sections/0/text`；135 个字段命中，仅作待审查定位。
- 十神结构与条件解释：术语 0，关联 Phase1 Rule 0，列入结构映射的 Phase2 Rule 0。
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
- 流年与岁运作用：术语 0，关联 Phase1 Rule 0，列入结构映射的 Phase2 Rule 0。
  旧资料 `data/canonical/bazi/foundations_v1.json`（实现/描述参考，未授权解释）。
  原文候选 `data/canonical/classics/bazi/ditiansui_chanwei_v1.json#/sections/1/text`；62 个字段命中，仅作待审查定位。
  原文候选 `data/canonical/classics/bazi/qiongtong_baojian_v1.json#/sections/0/text`；59 个字段命中，仅作待审查定位。
  原文候选 `data/canonical/classics/bazi/yuanhai_ziping_v1.json#/sections/0/text`；126 个字段命中，仅作待审查定位。
- 事业财富专题：术语 0，关联 Phase1 Rule 0，列入结构映射的 Phase2 Rule 0。
  原文候选 `data/canonical/classics/bazi/ditiansui_chanwei_v1.json#/sections/3/text`；45 个字段命中，仅作待审查定位。
  原文候选 `data/canonical/classics/bazi/qiongtong_baojian_v1.json#/sections/3/text`；24 个字段命中，仅作待审查定位。
  原文候选 `data/canonical/classics/bazi/yuanhai_ziping_v1.json#/sections/23/text`；39 个字段命中，仅作待审查定位。

缺失：

- 八字基础与十神映射：缺八字 Phase1 注册、原典逐项绑定、出生时间/四柱执行契约及 Golden；旧实现表的权重不作通用古典结论。
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
- Scenario尚未实现并验证完整聚合/检索/门控链路

禁止结论：发财保证；事业升迁应期；财星多即富；财多身弱判断。

推荐复核来源（本地已存在；不因列在这里自动升 Evidence）：

- `data/canonical/classics/bazi/ditiansui_chanwei_v1.json`
- `data/canonical/classics/bazi/qiongtong_baojian_v1.json`
- `data/canonical/classics/bazi/yuanhai_ziping_v1.json`

前台降级：当前版本尚未开放，相关知识、规则与证据仍在校核中。

## 缘分合盘

已有：

- 八字基础与十神映射：术语 0，关联 Phase1 Rule 0，列入结构映射的 Phase2 Rule 0。
  旧资料 `data/canonical/bazi/foundations_v1.json`（实现/描述参考，未授权解释）。
  原文候选 `data/canonical/classics/bazi/ditiansui_chanwei_v1.json#/sections/0/text`；66 个字段命中，仅作待审查定位。
  原文候选 `data/canonical/classics/bazi/qiongtong_baojian_v1.json#/sections/0/title`；51 个字段命中，仅作待审查定位。
  原文候选 `data/canonical/classics/bazi/yuanhai_ziping_v1.json#/sections/0/text`；135 个字段命中，仅作待审查定位。
- 旺衰及流派边界：术语 0，关联 Phase1 Rule 0，列入结构映射的 Phase2 Rule 0。
  原文候选 `data/canonical/classics/bazi/ditiansui_chanwei_v1.json#/sections/2/text`；55 个字段命中，仅作待审查定位。
  原文候选 `data/canonical/classics/bazi/qiongtong_baojian_v1.json#/sections/3/text`；33 个字段命中，仅作待审查定位。
  原文候选 `data/canonical/classics/bazi/yuanhai_ziping_v1.json#/sections/4/text`；51 个字段命中，仅作待审查定位。
- 婚恋专题：术语 0，关联 Phase1 Rule 0，列入结构映射的 Phase2 Rule 0。
  旧资料 `data/canonical/bazi/shensha_v1.json`（实现/描述参考，未授权解释）。
  原文候选 `data/canonical/classics/bazi/ditiansui_chanwei_v1.json#/sections/3/text`；37 个字段命中，仅作待审查定位。
  原文候选 `data/canonical/classics/bazi/qiongtong_baojian_v1.json#/sections/54/text`；1 个字段命中，仅作待审查定位。
  原文候选 `data/canonical/classics/bazi/yuanhai_ziping_v1.json#/sections/5/text`；61 个字段命中，仅作待审查定位。
- 流年与岁运作用：术语 0，关联 Phase1 Rule 0，列入结构映射的 Phase2 Rule 0。
  旧资料 `data/canonical/bazi/foundations_v1.json`（实现/描述参考，未授权解释）。
  原文候选 `data/canonical/classics/bazi/ditiansui_chanwei_v1.json#/sections/1/text`；62 个字段命中，仅作待审查定位。
  原文候选 `data/canonical/classics/bazi/qiongtong_baojian_v1.json#/sections/0/text`；59 个字段命中，仅作待审查定位。
  原文候选 `data/canonical/classics/bazi/yuanhai_ziping_v1.json#/sections/0/text`；126 个字段命中，仅作待审查定位。
- 双人关系：术语 0，关联 Phase1 Rule 0，列入结构映射的 Phase2 Rule 0。
  旧资料 `data/canonical/yinyuan/hehun_rules_v1.json`（实现/描述参考，未授权解释）。
  原文候选 `data/canonical/classics/bazi/ditiansui_chanwei_v1.json#/sections/3/text`；57 个字段命中，仅作待审查定位。
  原文候选 `data/canonical/classics/bazi/qiongtong_baojian_v1.json#/sections/3/text`；4 个字段命中，仅作待审查定位。
  原文候选 `data/canonical/classics/bazi/yuanhai_ziping_v1.json#/sections/4/text`；49 个字段命中，仅作待审查定位。

缺失：

- 八字基础与十神映射：缺八字 Phase1 注册、原典逐项绑定、出生时间/四柱执行契约及 Golden；旧实现表的权重不作通用古典结论。
- 旺衰及流派边界：缺命名 school/variant、通根与月令条件、权重依据、冲突记录、执行与反例 Golden；不能用五行数量判断强弱。
- 婚恋专题：缺配偶宫/星的条件规则与岁运触发；保存传统性别 lens 与批判材料，现代中性表达另审，不以咸池或官星断人品/婚姻。
- 流年与岁运作用：日历干支不等于运势；缺原局、大运、流年作用图及强弱/喜忌条件规则。
- 双人关系：旧合盘60分为实现约定；缺双人镜像/方向与对称关系/共同岁运规则及双人 Golden；六合不推适婚，六冲不推分手。

阻塞：

- 所需解释模块尚无产品级审核授权
- AI未完成真实质量校准及人工语义复核
- Scenario尚未实现并验证完整聚合/检索/门控链路

禁止结论：合盘匹配分；六合即适婚；六冲必分手；共同婚期。

推荐复核来源（本地已存在；不因列在这里自动升 Evidence）：

- `data/canonical/classics/bazi/ditiansui_chanwei_v1.json`
- `data/canonical/classics/bazi/qiongtong_baojian_v1.json`
- `data/canonical/classics/bazi/yuanhai_ziping_v1.json`

前台降级：当前版本尚未开放，相关知识、规则与证据仍在校核中。

## 人生总览

已有：

- 八字基础与十神映射：术语 0，关联 Phase1 Rule 0，列入结构映射的 Phase2 Rule 0。
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
- 流年与岁运作用：术语 0，关联 Phase1 Rule 0，列入结构映射的 Phase2 Rule 0。
  旧资料 `data/canonical/bazi/foundations_v1.json`（实现/描述参考，未授权解释）。
  原文候选 `data/canonical/classics/bazi/ditiansui_chanwei_v1.json#/sections/1/text`；62 个字段命中，仅作待审查定位。
  原文候选 `data/canonical/classics/bazi/qiongtong_baojian_v1.json#/sections/0/text`；59 个字段命中，仅作待审查定位。
  原文候选 `data/canonical/classics/bazi/yuanhai_ziping_v1.json#/sections/0/text`；126 个字段命中，仅作待审查定位。
- 婚恋专题：术语 0，关联 Phase1 Rule 0，列入结构映射的 Phase2 Rule 0。
  旧资料 `data/canonical/bazi/shensha_v1.json`（实现/描述参考，未授权解释）。
  原文候选 `data/canonical/classics/bazi/ditiansui_chanwei_v1.json#/sections/3/text`；37 个字段命中，仅作待审查定位。
  原文候选 `data/canonical/classics/bazi/qiongtong_baojian_v1.json#/sections/54/text`；1 个字段命中，仅作待审查定位。
  原文候选 `data/canonical/classics/bazi/yuanhai_ziping_v1.json#/sections/5/text`；61 个字段命中，仅作待审查定位。
- 事业财富专题：术语 0，关联 Phase1 Rule 0，列入结构映射的 Phase2 Rule 0。
  原文候选 `data/canonical/classics/bazi/ditiansui_chanwei_v1.json#/sections/3/text`；45 个字段命中，仅作待审查定位。
  原文候选 `data/canonical/classics/bazi/qiongtong_baojian_v1.json#/sections/3/text`；24 个字段命中，仅作待审查定位。
  原文候选 `data/canonical/classics/bazi/yuanhai_ziping_v1.json#/sections/23/text`；39 个字段命中，仅作待审查定位。
- 人生聚合：术语 0，关联 Phase1 Rule 0，列入结构映射的 Phase2 Rule 0。

缺失：

- 八字基础与十神映射：缺八字 Phase1 注册、原典逐项绑定、出生时间/四柱执行契约及 Golden；旧实现表的权重不作通用古典结论。
- 旺衰及流派边界：缺命名 school/variant、通根与月令条件、权重依据、冲突记录、执行与反例 Golden；不能用五行数量判断强弱。
- 格局：正文提及不等于结构规则；缺成格/破格/兼格条件、流派限制和 Golden。
- 喜用神分体系治理：调候、扶抑、病药、格局用神未分别治理；依赖旺衰与格局；禁止输出喜用木火等具体结论。
- 大运：旧说明不是执行；须核顺逆/起运法/节界/岁数换算/原局作用及不同 Variant。
- 流年与岁运作用：日历干支不等于运势；缺原局、大运、流年作用图及强弱/喜忌条件规则。
- 婚恋专题：缺配偶宫/星的条件规则与岁运触发；保存传统性别 lens 与批判材料，现代中性表达另审，不以咸池或官星断人品/婚姻。
- 事业财富专题：缺组合、位置、强弱、格局、岁运解释规则；财多身弱须先完成旺衰，不能用财星数量推财富。
- 人生聚合：只能组合已审核模块；缺模块授权、证据去重、冲突优先级、历史记录及综合指数依据；不另建人生算法。

阻塞：

- 所需解释模块尚无产品级审核授权
- AI未完成真实质量校准及人工语义复核
- Scenario尚未实现并验证完整聚合/检索/门控链路

禁止结论：人生总分；健康寿命断语；未经模块审核的人生结论。

推荐复核来源（本地已存在；不因列在这里自动升 Evidence）：

- `data/canonical/classics/bazi/ditiansui_chanwei_v1.json`
- `data/canonical/classics/bazi/qiongtong_baojian_v1.json`
- `data/canonical/classics/bazi/yuanhai_ziping_v1.json`

前台降级：当前版本尚未开放，相关知识、规则与证据仍在校核中。

## AI解梦

已有：

- 传统梦文化：术语 0，关联 Phase1 Rule 0，列入结构映射的 Phase2 Rule 0。
- 现代心理梦研究：术语 0，关联 Phase1 Rule 0，列入结构映射的 Phase2 Rule 0。

缺失：

- 传统梦文化：缺独立梦境来源、实体/象征/关系、source_ref、interpretation/type/confidence/cultural_context；现有文本偶见梦字不计覆盖。
- 现代心理梦研究：缺独立研究资料及许可审核；不得借古籍背书心理理论，不诊断、不从梦推怀孕/疾病/未来；与传统文化分段展示。

阻塞：

- 所需解释模块尚无产品级审核授权
- AI未完成真实质量校准及人工语义复核
- Scenario尚未实现并验证完整聚合/检索/门控链路

禁止结论：无检索解梦；疾病或怀孕诊断；梦预示未来；心理理论冒充古籍。

推荐复核来源（本地已存在；不因列在这里自动升 Evidence）：

- 当前无已审核专属来源；先来源登记与 Quarantine，不编造书名/摘录。

前台降级：当前版本尚未开放，相关知识、规则与证据仍在校核中。

## 一事占问

已有：

- 六爻占问深化：术语 23，关联 Phase1 Rule 19，列入结构映射的 Phase2 Rule 7。
- 奇门专业能力：术语 13，关联 Phase1 Rule 3，列入结构映射的 Phase2 Rule 5。

缺失：

- 六爻占问深化：排盘七项结构已执行；术语/描述规则不等于占断；缺用神选取、旺衰、生克动变与应期解释的可执行链路。
- 奇门专业能力：指定精确节气转盘结构已执行；缺格局/用神解释；置闰、超接及其他盘法未实现。

阻塞：

- 所需解释模块尚无产品级审核授权
- AI未完成真实质量校准及人工语义复核
- Scenario尚未实现并验证完整聚合/检索/门控链路

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
- Scenario尚未实现并验证完整聚合/检索/门控链路

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
- Scenario尚未实现并验证完整聚合/检索/门控链路

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
- Scenario尚未实现并验证完整聚合/检索/门控链路

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
- Scenario尚未实现并验证完整聚合/检索/门控链路

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
- Scenario尚未实现并验证完整聚合/检索/门控链路

禁止结论：卦义直接推具体事件；未来概率；后世术数冒充原义。

推荐复核来源（本地已存在；不因列在这里自动升 Evidence）：

- `yijing.source.meihua`
- `yijing.source.shuogua`
- `yijing.source.xici`

前台降级：当前已实现的结构能力可供专业参考；该项深入解释仍在知识审核中。

## 本批范围及未完成项

本批完成实查报告、两部既有来源的隔离复核候选及失败即拒绝的产品解释门控；未新增/晋级知识、未开放产品、未上线 AI。
八字逐项术语/规则治理、独立梦境资料、解释性 Golden、Scenario 运行与模型质量校准仍须按上述批次完成。
