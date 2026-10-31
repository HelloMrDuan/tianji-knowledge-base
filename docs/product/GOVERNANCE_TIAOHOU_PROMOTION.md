# GOVERNANCE_TIAOHOU_PROMOTION — 穷通宝鉴经典 Canonical 建制与调候注册晋级（E0352）

批次：治理 pending 队列末项实质实施批（tiaohou-qiongtong-v1 经典建制实施）。设计依据：`docs/product/TIAOHOU_CANONICAL_DESIGN.md`（E0350 定稿 D-T1…D-T6 + §10 设计修订 E0351，冲突处以 §10 为准）。台账事件 E0352（归属 TJ-018.2、状态「阻塞」不变），关账预留 E0353。本批止于 PR：快照换代由父级在合并前先行，本批只交付暂存快照与换代清单（§7），未动 live 快照与 cicd 钉。

## 0 授权与范围

治理 pending-8 审计（E0341）将 tiaohou-qiongtong-v1 归为「缺 Canonical 经典建制」类，须先立设计审定批；设计批 E0350 已定稿并经 E0351 修订（窗口节解法 A）。本批按设计实施：新建 Canonical 经典 `bazi.classic.qiongtong`、11 章、110 节、术语 1 条、Phase1 规则 r042–r051、Phase2 步 `bazi.phase2.tiaohou_assessment`，治理行翻转为 registered。范围外（未做）：siling 试点任何变更、扶抑 U1/U3、tiaohou 查表语义与判定、harness 契约、合化不变量口径、场景接线与公开开放、AI。

## 1 五问答复

（1）真正补齐的专业判断是什么？——无新增判断。补齐的是调候 Variant 的证据注册：《穷通宝鉴》此前不在密封 Canonical 五经典内（渊海子平、三命通会、协纪辨方书、滴天髓阐微、神峰通考），TJ-013.1 已审定的 119 条条目引文 0 条可在 Canonical 验证，evidence_binding 为 pending_phase1_rule_registration。本批按设计建经典、建节、按干注册规则，使调候条目陈述（只陈述原文先次之序与盘面存在性）成为可由 EvidenceResolver 逐条复核、由 ExecutionTrace 留痕、由密封 Golden 真实 fire 的注册产出。查表不产生任何吉凶、强弱、格局或喜用裁决，注册前后产出值逐字不变（§5）。

（2）引文如何绑定到 Canonical 节？——按条目跨度建节（D-T2，含 §10 窗口节例外）：总论锚节 s075 取快照 [6,517)；109 个不同条目跨度按 (char_start, char_end) 升序建节 s076–s184，节文本为钉定快照对应区间逐字切片；丙×卯条目跨度 [8668,9025) 的尾段含未裁合化命题（字符 8863「从化格」命例句，在任何已登记引文之外），按 §10 定稿只取窗口 [8668,8852)（184 字）建节 s099，排除段 [8853,9025)（172 字）登记未建节、不入任何 refs。ENTRIES 119 条各补 source_section_id 指向其条目节（丙×卯指向 s099）。术语 `bazi.term.tiaohou` 锚总论气候生成句（快照 [33,98)，位于 s075 内）；s075 不被任何规则 refs 消费。

（3）Phase1/Phase2 注册形态？——Phase1 按干 10 条规则 r042–r051（school 统一「子平·穷通宝鉴（调候）」，term_refs 均为 bazi.term.tiaohou）：每干 refs 的 (section_id, original_text) 集合恰等于该干主引文对（按（节跨度、引文定位点）去重，111 条）与已编码分支引文对（按（引文、定位点）去重，9 条）的并集，逐干计数 甲13/乙11/丙16/丁13/戊10/己6/庚13/辛13/壬12/癸13，合计恰 120；丁火七、八月同文同位点分支引文按 §10.5(ii) 合成 1 条并绑共享跨度之节。unencoded 24 条留在条目内只登记、related 17 条保持节外登记现状，均不入 refs。Phase2 恰 1 步 `bazi.phase2.tiaohou_assessment`（validated，phase1_rule_refs = r042–r051），30 例 Golden 按 G1–G6 真实 fire。

（4）翻转前后等价如何证明？——比对集与封闭清单见 §5：公开 TJ-013.1 Golden 54 例盘 +（日主，月支）120 格逐格真实出生时刻枚举盘 + 门控关闭 54 例盘，翻转前后全封套逐叶比对，封闭清单（evidence_binding 值、LIMITATIONS/docstring 注册句、治理披露字段、新步 trace/RuleMatch/Evidence 增量、ENTRIES 的 source_section_id 新增键）外差异 0、查表计算值差异 0、门控关闭面逐字一致。

（5）仍未判断的范围？——见 §8：调候条目陈述之外的任何裁决（喜用、吉凶、强弱、格局）仍不可判断；四喜用体系冲突仍只并列呈现不裁决；未建节文本（未消费缺口并集 4,744 字与 s099 排除段 172 字）不入任何 refs；siling 扩月与 24 小时计日约定转正仍待用户裁定；公开开放与 AI 仍关闭。

## 2 设计符合性（D-T1…D-T6 与 §10 修订逐项）

| 设计项 | 定稿口径 | 实施结果 |
|---|---|---|
| D-T1 底本 | 钉定快照逐字切片、简体/半角如实保留、不补缺字、证据等级恒 C、新经典 body_stage=quarantine | 符合：110 节文本全部与快照对应区间逐字相等（密封专项逐节断言）；经典字段 {id, domain, name=《穷通宝鉴》, source_id, body_stage=quarantine} 镜像神峰经典 |
| D-T2 建节 | 章 11、节 110（s075 + 条目跨度升序 s076–s184）、共享跨度一节多绑、嵌套各自成节 | 符合：逐章计数 11/11/12/11/10/6/12/12/12/12（总论章 1 节）；共享跨度 7 个、嵌套/同始交叠 3 对均 scope 互注 |
| §10 窗口节 | s099 = [8668,8852) 窗口节，排除段登记未建节，2 条 refs 改绑 s099 | 符合：s099 恰为丙×卯条目节顺位（第 24 条目节）；locator 记窗口坐标并注原条目跨度；scope 明示窗口形态、原跨度与排除段；排除段文本不等于任何一节文本（密封专项断言） |
| D-T3 术语与规则 | 术语恰 1 条锚 s075 气候生成句；规则按干 10 条、refs 恰等合计 120 | 符合：独立复算的恰等断言在密封专项内与 bundle refs 逐干全等（见 §3）；术语 definition 为平台陈述式自限摘要 |
| D-T4 分工 | s075 只作术语锚、不入规则 refs | 符合：10 条规则 refs 的 section_id 集合不含 s075（密封专项恰等断言蕴含） |
| D-T5 执行接入 | harness 契约零扩展、沿既有 tiaohou_variant 门控、计算后 trace.add 登记 | 符合：golden.py/schema/provider 钉死与 chart 签名零改动；bazi_chart 的 tiaohou 块改「计算后登记」形态，沿 ren/bingyao 先例 |
| D-T6 Golden | G1–G6 判据并集、真实出生时刻四柱、id 形如 bazi.tiaohou-<slug> | 符合：30 例（复用公开 Golden 真实四柱 27 例 + sxtwl 检索真实出生时刻补 3 例），G1–G6 由密封专项逐项复核（见 §3） |
| §10.4 计数钉迁移 | 经典 5→6、章 33→44、节 74→184、术语 38→39、规则 41→51、步 42→43、Golden 180→210；合化 SEALED_MEASUREMENTS 三总数同步 | 符合：逐项实测对平（§3）；合化不变量在新 bundle 上全过、phase1_sections_with_hehua_keywords 仍 0 |
| §10.5 填值注记 | 丁合并 ref 绑共享节；缺口并集口径 4,744 字 | 符合：丁 refs 13 条中合并 ref 绑 bazi.section.s117（共享跨度 (13476,13592) 之节）；缺口未建节范围不变 |

## 3 密封著录明细

- 经典：`bazi.classic.qiongtong`（《穷通宝鉴》，source_id=bazi.source.qiongtong，body_stage=quarantine）。
- 章 11：`bazi.chapter.qiongtong_zonglun`（五行总论，[6,517)）+ 十干章 `_jia/_yi/_bing/_ding/_wu/_ji/_geng/_xin/_ren/_gui`（章界为该干全部条目跨度最小包络）。
- 节 110：s075 总论锚节（511 字）+ s076–s184 条目节；每节 review.scope 逐字含 D-T1 披露口径（单一电子谱系 daizhigev20、简体转写、C 级、未做多底本校勘、引文以固定快照 SHA256 a8125d7de94f93d1a3eec48f1610b0c4baf31c264e9d7c19f586a85a78a2b0b4 为准）；全 110 节（text 与 name）PUA/□ 与六关键词（化气/合化/化象/真化/化格/五合）扫描零命中（密封专项 fail-hard 断言）。
- 术语：`bazi.term.tiaohou`（名「调候」），source_refs 恰 1 条（s075 气候生成句，快照 [33,98) 逐字切片）。
- 规则：r042–r051，refs 合计恰 120（逐干计数见 §1(3)）；穷举绑定密封测试断言 119 条主引文与 10 条分支引文逐条为其条目节文本子串（丙×卯两引文为 s099 窗口文本子串）。
- 步：`bazi.phase2.tiaohou_assessment`（validated；golden_case_ids 与 30 例新用例集恰等）。
- Golden 30 例构成：G1 十条已编码分支双极 20 例、G2 乙×丑 1 例、G3 空序列三条 3 例、G4 共享跨度补例与既有覆盖 5 例（戊正二月、己三冬复用 + 戊十一十二月、己三夏、己三秋检索补例）、G5 壬补例 1 例；检索补例真实出生时刻：戊×丑 1930-01-08T00:00、己×巳 1930-05-09T00:00、己×申 1930-08-17T00:00（均 +08:00、Asia/Shanghai，sxtwl 计算四柱）；G6 presence 三态（visible/hidden/absent）在全集齐备（密封专项复核）。
- 密封文件 sha256（著录后）：phase1_knowledge.json `942caeefbf249428d07b4ffc868b0e663c955fde0089995a836ad5586efac091`、phase2_execution.json `ad7a4f17d6dae6c69899a9c2785dfee46a49e38b3d50097c7c634d567fd5c1e8`、phase2_golden.json `7e15dbc6e37860fdbcff225283022d75cf393646906d3c67dc8660ff3c1944b0`；coverage 两文件以最终代码在组装树内重生后拷回私有检出，其 sha256 与新 manifest 见 §7。

## 4 公开侧改动明细

- `src/tianji_kb/bazi_tiaohou.py`：ENTRIES 119 条各补 `source_section_id`（由条目自身 section 跨度计算、按升序顺位赋值，生成注记已同步说明该字段的 E0352 来源）；docstring 注册段与 LIMITATIONS 末项改记注册形态；`tiaohou_lookup` 两处 evidence_binding 由 pending_phase1_rule_registration 改记 registered_phase1_phase2。ENTRIES 既有字段与查表语义逐字未动。
- `src/tianji_kb/operations/bazi_chart.py`：tiaohou 块改「计算后登记」形态（assessment 计算后 trace.add 新步，沿 bingyao 块先例）；production_scope 句逐字未动；chart 签名零改动。
- `src/tianji_kb/bazi_registration_governance.py`：tiaohou 行翻转 registered（phase1_rule_id=r042、additional_phase1_rule_ids=[r043…r051]、phase2_rule_id、reason 整体重写、unlock_path=None）；新增 GOVERNANCE_TIAOHOU_RECORD；TIAOHOU_DESIGN_RECORD（E0350/E0351 设计裁定历史）逐字未动。
- 测试：新公开专项 `tests/test_governance_tiaohou_promotion_public.py`（validate.yml 按名接入）；新密封专项 `tests/test_phase2_bazitiaohou.py`（与步 regression_test 字段一致）；设计测试 `test_governance_tiaohou_design_public.py` 按其自注迁移（行翻转与 binding 两处，其余设计钉逐字保留）；S5 与历批治理公开/密封测试的 FLIPPED/MAINTAINED 全局集合钉、密封计数钉、合化 SEALED_MEASUREMENTS 三总数及其 golden 镜像、phase1 可执行规则集钉逐文件以 E0352 注释链迁移（迁移而非放宽：集合恰等与计数恰等口径不变）。

## 5 等价比对（封闭清单与结果）

比对集（同一捕获脚本在基线组装 = main 3dd83b6f + 旧快照 380bb73e… 与工作组装 = 本批代码 + 新密封数据各跑一次，全封套逐叶 JSON 比对）：公开 TJ-013.1 Golden 54 例四柱盘（门控开）、（日主，月支）120 格逐格真实出生时刻枚举盘（sxtwl 1930–2030 检索首个命中时刻，120/120 格全命中、无格手编）、公开 Golden 54 例盘（门控关）。

封闭清单（先行定义）：（i）result.tiaohou_assessment.evidence_binding 值 pending→registered；（ii）tiaohou_assessment.limitations 末项注册句改记；（iii）新步 `bazi.phase2.tiaohou_assessment` 的 trace 条目 1 条、RuleMatch 条目与 Evidence 条目增量；（iv）治理披露字段（治理行与记录、模块 docstring 注册段）；（v）ENTRIES 新增 source_section_id 键（只新增、无既有键改值）。

实测结果：三组比对集（54 + 120 + 54 封套）封闭清单外差异 **0**、查表计算值差异 **0**；门控关闭 54 封套与基线逐字全等；每例门控封套恰含新步 trace 条目 1 条。

## 6 伪造负例与回滚演练

伪造负例（密封专项 ForgedNegativeTests，篡改副本根上以 EvidenceResolver(review_sources=True) 校验）：(1) 条目主引文改字（r042 首条 ref 首字改）——拒（Quote/section mismatch）；(2) 引文错绑他干之节（r042 首条 ref 的 section_id 改指 r043 首条之节）——拒；(3) 分支引文冒充主引文（甲×午分支引文填入甲×寅主引文 ref 位、节不变）——拒；(4) 总论锚句改字（术语 bazi.term.tiaohou 锚引文首字改）——拒。四类均被拒绝。

回滚演练（本批代码 + 旧快照 380bb73e… 组装）：门控路径 fail-closed（ValueError: Unknown rule: bazi.phase2.tiaohou_assessment）；门控关闭封套与基线逐字一致；既有 bingyao 门控路径在旧快照下照常执行、不受影响。

## 7 实施记录与换代清单

- 机上全配方复跑（accept_offline --suite all，本批最终代码 + 暂存快照 + 新钉）：{{REPRO}}。
- 换代清单（交付父级，合并前先行换代）：暂存快照 237 文件 / {{BYTES_AFTER}} 字节 / manifest SHA256 `{{MANIFEST_AFTER}}`（旧值 237 / 16,272,294 / `380bb73e34babc30bcc80e5ad7f296175f6be206af6a77f1abb4a07b94da654b`）；私有检出根 manifest 与 import_public_snapshot EXPECTED（237 / {{BYTES_AFTER}}）已同步重生 verify 通过；live 快照备份名建议 `secure/tianji-knowledge-pre-tiaohou-backup`；cicd 钉改 `TRUSTED_MANIFEST_SHA256={{MANIFEST_AFTER}}`（父级合并前先行，本批不动 live 与 cicd 钉）。
- 密封变更文件恰 5 件：data/canonical/bazi/phase1_knowledge.json、data/canonical/bazi/phase2_execution.json、data/canonical/bazi/phase2_golden.json、data/coverage/phase1.json、data/product/knowledge_coverage.json。
- 台账：E0352（归属 TJ-018.2、状态「阻塞」不变、后三列「—」）；TASK_STATUS 仅动 TJ-018.2 行。

## 8 仍未判断与后续

- 调候注册不解锁任何裁决：喜用四体系（扶抑/病药/格局/调候）仍分别治理，冲突只并列呈现；TJ-013.1/TJ-013.2/TJ-013.3 与真 TJ-017.2 仍因扶抑 U1/U3 用户暂缓而阻塞，与本批无涉。
- 《穷通宝鉴》经典只建分月条目与总论：未消费缺口（并集 4,744 字）与 s099 排除段（172 字）未建节、未注册；书中其余文字（如各干总纲段未被条目跨度覆盖部分）不在本批建节范围。
- 治理维持名单余 3 项：siling-yin-pilot（扩月或 24 小时计日约定转正，待用户裁定）、dayun-compose / dayun-timeline-view（inherited 终局形态）。
- 注册五条件第五项（部署验收绑定）待关账 E0353 终局核对；公开开放与 AI 仍关闭。
- 后续队列：阳刃「凶/㓙」校勘勘误登记批、土根消费接入实现批（按 E0257 审定契约）。
