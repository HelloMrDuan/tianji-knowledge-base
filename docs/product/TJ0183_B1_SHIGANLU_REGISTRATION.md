# TJ-018.3-B1 三命卷三《论十干禄》校勘登记

任务归属：TJ-018.2（台账事件 E0338）。授权依据：用户 2026-10-30 分级裁定 P3 暂缓条件为「卷三禄节前置 + 下轮复核」；下轮复核（E0337，`TJ0183_P3_YANGREN_REEVALUATION.md`）结论 B 立项两批路径，本批为 B-1。

## 1. 执行摘要

本批为**纯登记批**：按 TJ-018 既有校勘模块体系（COLLATION_SECTIONS / COLLATION_QUOTES / COLLATION_NOTES）为三命通会卷三《论十干禄》新建一册登记——新模块 `src/tianji_kb/bazi_sanming_juan3_collation.py`、新注册表 `sanming-juan3-collation-register-v1`（沿 018-D 为卷五建册、018-G 为卷六建册先例；本节 section_id 采用 P2 残余防处置册 seq 47 预留名 `sanming.juan3.shiganlu`，不可改）。

登记结论：

- 整节逐字登记：S0 字符 [74911, 77454)，2,543 字，两 part（主文 `shiganlu_exposition` [74911, 77214) + 金轝附论 `jinyu_appendix` [77214, 77454)）。
- 校勘记 56 条：confirmed 26 / contextual 28 / suspected 1 / unresolved 1；disposition 分布 corrected 28 / genuine 27 / unresolved 1。
- 引文 30 条逐条登记，全文计数均为 1。
- 三命校勘记累计 383 → **439 条**，登记节数 24 → **25 节**。
- 来源普查不变：102 条（C:96 / D:6），本批不新增 Source，仅追加 `bazi.source.sanmingtonghui` 的 review_scope 述事段落。

**本批明确不做**：不建 Canonical 节、不翻转任何注册（`pattern-route-luren` 维持 pending，其与禄刃两节的联合翻转属 B-2）、不写规则/判定代码、不动密封资产、determination 零变化、用户可见能力零变化。

## 2. 节界定稿与逐节校勘清单

### 2.1 节界与结构

- S0（快照 `sanming_tonghui.txt`，sha256 `00e2a7db…`）：[74911, 77454)，2,543 字。节题 [74911, 74936)「论十干禄」25 字——节题自注即声明金轝附论附于本节之后，附论属本节登记范围。下一节《论驿马》题起于 77454。
- S3（正式应用文本 `sanming_tonghui_applied_v1.txt`，sha256 `a89c0b5d…`）：对应 [74910, 77453)，全程位移 −1（与 P1/P2/批三换算口径一致：603 条校勘应用复放换算 + 锚点位移核对）。
- 结构发现：Slice A 登记窗口恰为 [74911, 77214)——只覆主文；金轝附论 [77214, 77454) 此前不在任何登记内，本批首次登记。
- S0→S3 差异恰 **17 处**：防 15 处（经密封订正）+ PUA 2 处（经 confirmed 映射），逐位与校勘记对平（密封专项机检）。

### 2.2 校勘记分类清单

- **PUA 2 处**（confirmed / corrected / Q1）：76614 U+EA20→玄（「洞玄经」之玄；映射源锚含《五行精纪》同文）；77193 U+EAC0→嗤（全书仅此 1 见，源锚即本节句在《五行精纪》论禄篇同文「主不犯枭神为佳」段）。候选池对 76614 另有历史字形「𤣥」held 登记，不采。
- **防 16 处**：15 处 confirmed / corrected / Q1，经密封文字订正 11 条（ocr-104/105/106/108/109/110/111/112/113/137/478）定字，读法谱系 㓙×1（75151)、㐫×11、㑹×2（75722/76220)、㫖×1（76505）——「防」多源汇讹在本节再实证（四种互不相干原字）。余 1 处（76988）为 unresolved，见 §3。
- **己 23 处全量分判**：支名槽读巳 9 处入册——confirmed 8 处（74974 配同句、75028/75034 定义句 A3、75233/75319 段首、76025 朝元、76661 己酉丑、76829 木局在己），每条附两个同节互证锚（逐干分论五柱、封闭枚举、同句平行结构等）；suspected 1 处（76212「鬼在己上」，仅结构平行、无见证，Q3，沿 smxing-zuo 先例）；干名与真义 contextual 14 处。其余同类槽位读法的证据结构见 §4 的 A3 扩展披露。
- **已 2 处**：76644 支位槽读巳（contextual / corrected / Q2，同段金局三合自述与长生封闭枚举互证，无见证级锚，按先例槽位读法口径定 contextual）；76744「而已」真义（contextual / genuine / Q1）。
- **巳 18 处分判**：干名槽读己 1 处逐条入册（75035，Slice A 审定 A3，confirmed / corrected / Q2，锚为定义句紧随自释「谓己午」与己禄段段首）；支位真义 17 处入 `SI_GLYPH_DISPOSITION` 清单（stem_slot_offsets=[75035]、branch_slot_offsets 17 位），沿 018-F 形制不逐条入册。
- **戌 12 处**真义逐条入册（contextual / genuine / Q1，basis 只凭本节语境槽位，不冒称见证）；**戍 0 见**；戊 18 处全在干槽（扫描在案，非处置类）。

### 2.3 引文清单

引文 30 条逐字保留快照原字，全文计数均为 1：禄配四方（sgl.allocation）、禄定义句（sgl.definition）、四宫配属、逐干分论十段各一条（sgl.stem_jia … sgl.stem_gui）、禄类诸说（生成/明位/真禄）、防合十神、禄头驯中、干支朝元、禄堂、背向建禄、建禄性情、库合拱、禄马总论、洞玄经引文、希尹论马、烛神经引文、破禄空亡、主文结语、金轝定义与金轝引文块。含 corrected 注记的引文 18 条带 mapped_reading 与 collation_refs（读法只在登记层呈现，快照原字不动）。

## 3. 未决与传本异常清单

- **76988「市防态」之防（S3 残余防全节唯一位点）**：候选池 historical 读法「㕓」（市㕓）为 historical_only_hold、未应用；P2 残余防处置册 **seq 47**（section_id 已预留 `sanming.juan3.shiganlu`）对本位点处置为 deferred_no_witness。本批登记 `sgl-fang-76988` 为 **unresolved**（reading=None、usable_grade=None）：不采候选读法、不作处置裁定，处置状态逐字不变。
- **76212「鬼在己上」**：支槽读巳仅有结构平行（禄鬼/命鬼平行对举），无见证、无封闭枚举强制，登记 suspected / Q3，不升级。
- **节题自注**：节题 25 字内自注金轝附论的附属关系（「禄前二辰为金轝喻人得禄须坐车也故附于后」），传本结构事实入 TRANSMISSION_NOTES，不作改订。
- **Slice A 窗口口径**：Slice A 审定记载「引用窗口内 PUA 0」指定义句窗口 [75008, 75053)；全节 PUA 2 处（76614/77193）均在该窗口之外，两说不冲突，位置关系入 TRANSMISSION_NOTES。
- **字形体例**：本节轝/禄等字形从快照原样，异体只入校勘记，不入正文改订（TRANSMISSION_NOTES glyph-variant-style）。

## 4. 与既有代码的衔接

衔接关系登记于模块 `SHIGANLU_FACT_LINKAGE`（adjudication_semantics_changed=False），三条 existing_code_references：

- `src/tianji_kb/bazi_pattern.py`（status: consistent）：Slice A 禄刃路线 LU_BRANCH 十项与本节定义句经校勘记读法逐项相符（10/10，公开测试逐字钉住）。
- `src/tianji_kb/bazi_earth_roots.py`（status: consistent）：土根审定登记注记以本节定义句「戊寄巳」「己寄午」读法为互证材料，与本册读法一致。
- `src/tianji_kb/bazi_registration_governance.py`（status: unresolved）：`pattern-route-luren` 维持 pending，本批不翻转；其联合翻转（禄刃两节 Canonical 晋级 + 路线注册）属 B-2。

**与 Slice A 引文零重复的对账**：本节定义句已由 Slice A 登记为表源引文 `sanming.lu_sentence`（LUREN_QUOTES，locator [75008, 75053)，登记时 source_section_id 为 None）。本批引文 `sgl.definition` 与之**逐字同一、定位一致**（公开测试与密封测试双重逐字断言），并在该引文 note 字段与 `SHIGANLU_FACT_LINKAGE.slice_a_consistency` 中明示：本批以节登记引文承接其节内绑定（补上 source_section_id），**不作第二条独立引文**。两处登记指向同一文本同一坐标，是同一引文的节内绑定补全，非重复登记。

**A3 扩展发现（如实披露）**：Slice A 审定 A3 只处理定义句内 3 处互讹（75028 丙禄己→巳、75034 戊寄己→巳、75035 巳寄午→己）。全节扫描另见同类槽位读法 7 处 + 存疑 1 处（见 §2.2），均属**读法登记层**——快照与 S3 文本逐字未动，LU_BRANCH 无须订正、代码零改动。各读法的证明为节内机械互证（逐干分论段逐列巳支五柱、配同四方支对、三合封闭枚举、金长生于巳等）；分级沿 sanxing / 018-F 先例：槽位读法 confirmed+Q2（A3 三处同）、存疑 suspected+Q3、真义 contextual+Q1、见证定字（防/PUA）confirmed+Q1。

## 5. 密封资产对账

对账登记于模块 `SEALED_ASSET_RECONCILIATION`，密封专项在机上逐项机检：

- 窗口内密封文字订正 11 条（ocr-104/105/106/108/109/110/111/112/113/137/478）：old 在 S0 全文计数 1、new 在 S3 全文计数 1，本批防注记 basis 引用集合与之逐一对应。
- 窗口内候选池 3 条逐条处置：75721（S0 坐标）confirmed_applied（即 ocr-478 位点）；76613 historical_only_hold（玄→𤣥 held 不采）；76987 historical_only_hold（防→㕓，见 §3）。
- PUA 码位 2 个（U+EA20、U+EAC0）与密封 PUA 映射表对平。
- S0→S3 差异 17 处与校勘记 corrected（防 15 + PUA 2）逐位对平；S3 残余防恰 1 处（S3 76987，即 S0 76988）。
- 零匹配订正全书 66 条中本窗口 0 条（018-H 归因在案）。
- P2 seq 47 衔接：处置册预留 section_id 与本节 section_id 一致，残余防位点处置状态不变。

## 6. 测试

- 公开专项 `tests/test_tj0183_b1_shiganlu.py`（18 测，接入 validate.yml）：Golden 镜像逐字一致、节登记形制、校勘记字段完备与语境中心位、confirmed 两锚门槛、未决/存疑集合精确钉住、分类计数与等级分布、巳分判清单、引文形制与 mapped 引用完整性、定义句与 Slice A 零重复断言、LU_BRANCH 10/10 钉住、既有六册回归与累计 439 条、来源普查 102 与 review_scope 片段。
- 密封专项 `tests/test_tj0183_b1_shiganlu_sealed.py`（只在离线验收环境运行，公开 CI 不执行）：快照完整性（S0/S3 哈希）、30 引文切片逐字 + 全文计数、节题与节界、56 注记定位字与语境窗口逐字、六类字形全量扫描对账、mapped_reading 变换复核、S0→S3 差异 17 处与残余防 1 处、密封订正 11 条与候选 3 条对账、普查与六册回归。
- 合并前硬门（TJ-013.1 站立规则）：机上全配方复跑（accept_offline --suite all，钉 manifest `c815dc4e…`）SUCCESS 0 失败，增量与正式基线 2657 对平（结果见 PR 与台账关账记录）。

## 7. 未覆盖清单与后续

- 本批不建 Canonical 节：本节 Canonical 晋级与《论阳刃》节晋级、pattern-route-luren 路线注册翻转同属 **B-2**（禄刃两节 Canonical 晋级与路线注册批），B-2 的翻转第五条件为正式验收 + 部署验证，照批一/批二关账形制终局核对。
- 76988 残余防位点维持 deferred_no_witness，不因本批登记而改变；后续如有新见证另行处置。
- 本节不产生任何规则、Phase1/Phase2 步骤或 Golden 盘例；禄的相关既有消费（Slice A 路线、土根审定）行为逐字不变。
- 用户可见能力零变化；TJ-013.1 不因本批解锁。
