# 解梦来源首批：隔离登记与 17 类输入核查

本批为 #127 的历史审核记录。当前十个文化场景的实际建设见 [Dream Knowledge 首批](DREAM_KNOWLEDGE_BATCH_01.md)及[第二批](DREAM_KNOWLEDGE_BATCH_02.md)。以下描述 #127 当时的状态。

本批是来源调查和候选审核准备，**传统梦文化知识库仍为 NOT_BUILT，已确认解释为 0**。不增加已审核 Source、Canonical 实体、执行规则或解梦接口，不改变 AI 门控。调查记录不具有 Evidence 发布资格。

## 沿用已有流程

优先检查项目已有的 `source_registry.json` 和殆知阁古籍档案，找到 `易藏/术数/周公解梦.txt`。复用已有 `acquisition.stage_candidate`，完整字节只保存到忽略的 RAW 缓存；Quarantine 仅提交校验值、来源元数据和短 anchor 审核记录。`public_domain_manifest.json` 登记 `quarantine_only`，`canonical_ready=false`。

- 来源：`garychowcmu/daizhigev20`。
- 固定 commit：`4a6d6f2088825f132521d848c2ea86cf9c9a7620`。
- Git blob：`0c7b0823265c4ff00465f833e0be28f1bf0f2175`。
- 字节数：23527；SHA256：`d80c42b0b8f44f5b8cf2c4e1c286b200388b65dcd321347eb7ac1011d0be5e97`。
- [固定来源文件](https://github.com/garychowcmu/daizhigev20/blob/4a6d6f2088825f132521d848c2ea86cf9c9a7620/易藏/术数/周公解梦.txt)。
- 候选：`data/quarantine/phase1_candidates/daizhigev20/4a6d6f2088825f132521d848c2ea86cf9c9a7620/0c7b0823265c4ff00465f833e0be28f1bf0f2175.json`。
- 梦象调查：`data/quarantine/public_domain_snapshots/daizhigev20/zhougong_dream_candidates.json`。

`PUBLIC_DOMAIN_EXTRACT_ONLY` 只允许调查可能的前现代条目。采集资格不是整本公版或版本审核通过；现代编辑、注释、电子整理权利须另核。候选保留 D / pending。旧登记的 trust_level=A 不换算成古典 A 级 Evidence。

没有建立另一个梦知识 schema：现有七域模型目前不能直接容纳梦域，Source.kind 也不支持现代研究。后续应在原模型上通过独立的 schema/治理 PR 接纳新域和研究来源，然后用同样的 Classic/Chapter/Section/Term/Rule/Concept 及 SourceRef 逐项审核；不能绕过校验器创建一份“梦象大全”。本批候选没有获准进入 Canonical。

## 底本、异文与独立性

电子文件题为《周公解梦》，分 27 节；尚未核定它对应的刊本，不将周公旦认定为真实作者。

- [维基文库文本](https://zh.wikisource.org/zh-hans/周公解夢)也是 27 节，但开篇人名和若干条目不同，署名不能代替版本证明。
- [ctext 版本条目](https://ctext.org/wiki.pl?if=gb&remap=gb&res=801463)的底本信息显示“暂缺”；转写与殆知阁若干疑字一致。不能以三个网址当作三份独立刊本，也不以网页多数票改 RAW。
- [P.Ch.3908《新集周公解梦书》](https://www.shidianguji.com/book/PC3908/chapter/1lvx5l04rypf7)有敦煌抄本编号，属于另一历史见证；其分章和条目不同。只能另行核写本、影像、转录和利用权限，不能把该写本等同于这个 27 节电子文件。
- “江海得笔聪”“癸天上屋得高官”“得历日者中黄甲”等字句需要核本，不在本批纠字或据疑字释义。

## 17 类输入的调查结果

11 个直接场景候选、5 个相近语境、1 个未找到。**这些都不是已经确认的解释**。每条非空 anchor 在本地固定 RAW 中逐字唯一命中，记录原始字符偏移与行号；不清洗、补字或用别处文字填充。

| 输入 | 定位结果 | 审核范围 |
|---|---|---|
| 蛇 | 直接场景候选 | 蛇咬人，不能泛化到所有蛇梦 |
| 龙 | 直接场景候选 | 乘龙入水 |
| 鱼 | 直接场景候选 | 群鱼游水 |
| 水 | 直接场景候选 | 身在水中，和饮水/落水分开 |
| 火 | 直接场景候选 | 身在火中 |
| 房屋 | 直接场景候选 | 屋宅更新 |
| 家人 | 直接场景候选 | 仅兄弟相打，不能代表所有亲属情境 |
| 故人 | 相近语境，仍缺 | 死人复活不证明已故亲友梦，更不等于一般故人 |
| 被追 | 未找到 | 赶贼/逃走/被打不能替代被追 |
| 坠落 | 直接场景候选 | 仅坠井，不能覆盖所有坠落 |
| 飞翔 | 直接场景候选 | 人飞上天，排除飞熊/龙飞/鸟飞 |
| 死亡 | 直接场景候选 | 见人死或自死，不能预测现实生死 |
| 怀孕 | 相近语境，仍缺 | 上桥后“妻有孕”是古代断语，不是梦见怀孕的条目 |
| 婚姻 | 相近语境，仍缺 | 夫妻宴会不等于婚礼梦，不预测离别 |
| 钱财 | 直接场景候选 | 拾钱，不推一般财运 |
| 工作 | 相近语境，仍缺 | 古代受职上官不等于现代职场 |
| 考试 | 相近语境，仍缺 | 读书写字不等于考试，不使用疑字条目补缺 |

审查后仍须区分梦者、实体、动作、关系、条件和叙述结果。`dream_term` 可映射既有 Term；实体/关系/文化背景应在既有 Concept/Rule 条件中保存；每条 interpretation 必须追到审核过的 Section/SourceRef，不能把文化断语当作确定性个人 Fact。不能借现代心理理论补足古代条目。

## 学术资料与 dream-modern-psychology

下面只是独立的来源调查清单，未复制论文正文，尚未入已审核 Source 或 RAG。维持 research；传统梦文化、文化史研究和现代实验研究分别治理。

| 资料 | 核查结果 | 后续用途与限制 |
|---|---|---|
| [詹珮蓉，2022，《占梦书及其文化意涵研究：以〈梦占逸旨〉为中心》](https://ah.lib.nccu.edu.tw/item?item_id=161515) | 政治大学学位论文目录可核；重用权利未审核 | 文献和版本线索，属于文化研究，不能当临床心理 Evidence |
| [Kahn，2019，Reactions to Dream Content: Continuity and Non-continuity](https://pmc.ncbi.nlm.nih.gov/articles/PMC6901388/) | DOI `10.3389/fpsyg.2019.02676`，页面标注 CC BY | 研究视角候选；须保留研究类型、原研究样本与局限，不生成固定梦象对照表 |
| [Sikka 等，2022，Negative dream affect is associated with next-day affect level, but not with affect reactivity or affect regulation](https://www.frontiersin.org/journals/behavioral-neuroscience/articles/10.3389/fnbeh.2022.981289/full) | DOI `10.3389/fnbeh.2022.981289`；[PMC 许可记录](https://pmc.ncbi.nlm.nih.gov/articles/PMC9626956/)标注 CC BY | 研究梦中与醒后情绪的关联；不是蛇/水等符号的统一含义，也不是个人精神疾病、怀孕或未来的诊断依据 |

CC BY 许可不等于证据已经人工审核，也不等于实验结论适用于每个人。后续保留作者、年份、DOI、许可、方法、样本、统计范围和反例，研究型来源不能伪装成 classical 或 implementation 来通过现有 schema。

## 下一批的实际依赖

1. 找到并核准对应刊本/写本及允许使用的原典范围，区分现代整理。不能凭题名完成版权或作者审核。
2. 在现有模型中正式接纳梦域和独立研究来源；校验、索引与发布门控均须覆盖新域，禁止因添加域而把未审材料塞进生产运行清单。
3. 只从已核文本的小范围场景开始，审核 Term/Concept/Rule/Evidence、解释边界与冲突。被追等缺口保留为空。
4. Dream Golden 测试文化检索及引用的正确性和无依据拒答，不把现实吉凶或病孕当作测试真值。
5. 未完成真实 AI 质量校准前，不开放 AI 解梦。
