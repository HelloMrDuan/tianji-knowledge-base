# TJ-018.3 P2 卷二干支两节补充审定（入册版）

- 入册形制：本文件由本地审定文档入册为仓库文档，审定正文逐字保留（见下方原文），仅在文首加本文件头、文末加入册注记一行，审定结论、数字与措辞结论一律不回改。
- 审定授权来源：用户 2026-10-30 裁定——P1《论三刑》立即实施、P2 卷二干支两节先补充审定（未满足绑定条件不得执行注册翻转）、P3《论阳刃》暂缓。
- 基线与入册事件：审定基线为 live main `006097d5`（审定以该基线在册文件为据，见正文 §0）；本文件由入册批入册，台账事件 E0331。入册时点现状注记：P1 已关账（E0330，main `3e7ea90a`），正文结尾审定边界声明中「待 P1 关账后另批入册」系审定当时状态表述，按入册纪律只在此处注记、正文不回改。
- 本批边界：本批只入册审定文档，不执行注册翻转、不建 Canonical、不动快照与 manifest 钉值。

---

# TJ-018.3 P2 卷二干支两节补充审定

- 审定授权：用户 2026-10-30 09:35 裁定（P2 先补充审定，与 P1 并行；未满足绑定条件不得执行注册翻转）。
- 审定执行：2026-10-30（CST）。本文件为审定文档：**不执行注册翻转、不建 Canonical、不动密封数据、不建 PR、不动台账**。
- 审定对象：卷二《论天干阴阳生死》（`sanming.juan2.tiangan_yinyang_shengsi`）与《论五行旺相休囚死并寄生十二宫》（`sanming.juan2.wuxing_wangxiang_jisheng`）两节，及其承载的三个已执行旺衰谓词——丙×巳 `lu_visible_support`、金×酉 `pure_support_metal`、水×子 `pure_generating_support_water`——的 Canonical 注册绑定条件。
- 结论用语：每项结论只能是「满足 / 不满足 / 满足但须附条件」，条件逐项写明。

## 0 基线

| 项 | 值 | 来源 |
|---|---|---|
| Live main HEAD | `006097d5de1ce524cf08eb7d7ed124b8d2a080c2`（实时 API 核实，与授权时点一致） | GitHub API `GET /repos/HelloMrDuan/tianji-knowledge-base/commits/main` |
| Live main tree | `2a658f4496837be97d4a7b92c53d8fcf29572bdb` | 同上 |
| 数据口径 | 本审定所引文件均经 API 拉取并以 git blob 哈希与 live tree 逐一验合（全 OK）：`bazi_sanming_juan2_collation.py`（018-A 登记册）、`bazi_registration_governance.py`（S5 治理登记册）、`bazi_metal_water_roots.py`（S1）、`bazi_earth_roots.py`（分级呈现先例）、`bazi_fire_morphology.py`（火线裁定）、`bazi_fire_si_yin_morphology.py`（F3/F4 审定册）、`bazi_adjudication.py`（谓词实现）、`tests/golden_tj0112_s2_metal_water.json`、`tests/golden_tj0112_f34_si_yin.json`、`tests/test_phase2_baziadjudication.py` | 本批程序核对 |
| 两节在册形制 | 登记册 `sanming-juan2-collation-register-v1`（TJ-018-A）：节一 [38890,43082)，分段 per_stem_exposition [38890,41810) / lunyue_summary [41810,42151) 均 registered_evidence、debate_quotations [42151,43082) 为 archived_not_evidence；节二 [54894,55673) 全节 registered_evidence。校勘记 44 条（confirmed 25 / contextual 14 / suspected 3 / unresolved 2），本节引文 12 条（节一 9 + 节二 3；另跨书互证引文 9 条与人元司事旁证 1 条在同模块内） | `bazi_sanming_juan2_collation.py` COLLATION_SECTIONS / COLLATION_QUOTES / COLLATION_NOTES 程序计数 |
| 三谓词治理状态 | 三条在 S5 治理登记册均为 `maintained_pending`、reason_class = `canonical_evidence_absent` | `bazi_registration_governance.py` REGISTRATION_INVENTORY（原文见 §1 各谓词条） |
| 红线遵守 | UD-1/2/3 A 方案不变；□1 不补字；扶抑 U1/U3 不触碰（本审定只及旺衰谓词注册证据）；长生冲突只隔离不裁定；整书 canonical_ready=false 不变 | — |

**审定总纲**：三谓词的定义性证据在三命侧全部落在本审定两节之内（逐干句在节一、推步框架在节二），证据本体齐备；三者的注册阻塞不在证据缺失，而在（a）Canonical 无对应 section（P1 同型问题，属实施批的密封侧施工）、（b）帝旺推步位的等级披露必须随注册携带、（c）各自的 conflict 相邻面必须保持既有阻断。逐项审定如下。

## 1 逐谓词证据清单

### 1.0 两节的证据分工（共同前提）

- **节一《论天干阴阳生死》**是定义性证据的载体：逐干铺陈段（per_stem_exposition）含十干禄/长生/死逐干明句（`STEM_COVERAGE` 十干三锚点俱全，`STEM_COVERAGE_CONCLUSION.missing_stems = []`）；论曰总结段（lunyue_summary）含四长生总结块与土行讨论，为复述级互证。
- **节二《论五行旺相休囚死并寄生十二宫》**是推步框架的载体：`sm2.gong_sequence`「夫五行寄生十二官长生沐浴冠带临官帝旺衰病死墓絶胎飬循环无端」[55290,55319) 给出十二宫次序，`sm2.tiyao` [55343,55599) 给出十二宫逐位定义，`sm2.wangxiang_chun` 给出旺相休囚死框架。三条引文均为 framework_evidence。三谓词的帝旺推步链（§2/§3）以本节为框架依据——**节二不载任何逐干定位句，不得把推步结果表述为节二原文**。

### 1.1 丙×巳 `lu_visible_support`（形态 `bing-si-lu-commanding-visible-support-v1`）

治理登记册原文：reason =「定义性锚点『丙禄在巳』（三命卷二逐干句、卷三禄节、神峰禄表）无 canonical section：Canonical 三命通会仅咸池一节，神峰通考不在 Canonical 经典内。F34 登记 13 条引文引用中三命/神峰部分 0 条可在 Canonical 验证。」unlock_path =「先行 Canonical sections 扩编（三命卷二/卷三禄节逐节登记入 Canonical 并复核），再行注册批。」

| 证据句 | 在册引文 | 位置 | 层级 | 在本谓词中的作用 |
|---|---|---|---|---|
| 「其禄在己巳为炉冶之火」（己经校勘记 sm2-ji-39571 读巳） | `sm2.bing_lu` | 节一 per_stem_exposition [39568,39578) | **列举级原文**（per_stem_listed） | 月条件 `reviewed_lu_command_month` 的主定义锚（F3 登记册 QUOTE_REFERENCES 原文：「F3 lu position, per-stem listed sentence」） |
| 总结块「…丙火生寅…至巳临官归禄丙火得垣…」 | `sm2.summary_bracket` | 节一 lunyue_summary [41895,42017) | 列举级原文（同节复述） | 禄位与长生/死位的同节复述互证 |
| 「丙火生于寅其理甚明」 | `sm2.bing_sheng` | 节一 [39659,39668) | 列举级原文 | 丙根表长生位锚（根条件 `effective_heavy_day_roots` 的登记依据之一） |
| 「故丙火生于寅而死于酉」 | `sm2.bing_shengsi` | 节一 [39709,39719) | 列举级原文 | 丙根表生/死合句锚 |
| 丙帝旺午（无句，推步） | —（`bazi_fire_morphology` BING_ROOT_POSITIONS 午条） | 由丙长生寅 + 节二次序 + 阳干顺行推得 | **推步推论级**（framework_derived） | 丙根表重根位之一（寅/巳/午三重根位中的推步位）；见 §2 |
| 神峰禄表「丙戊禄在巳」 | `sf.lubiao` | 神峰（非三命） | 跨书互证 | 旁证。**神峰通考不在 Canonical 四书之内，此锚永不能作 Canonical source_refs**，只作登记层互证保留 |
| 滴天髓「丙禄居巳」单点、从旺/从强定义、根重轻列举 | `dt.bing_lu_single`、`dt.congqiang_def`、`dt.congwang_def`、`dt.root_heavy_light` | 滴天髓阐微（Canonical 四书之一） | 定义层锚（他书） | 本谓词的**定义本体**（从强/从旺定义 + 禄月形态的当令要件）在滴天髓侧；其 Canonical 绑定属他书 section 问题，不在本审定两节范围内（见 §8） |

拟绑定 Canonical 章节：节一（per_stem_exposition 丙段 + lunyue_summary 总结块）为主绑定；节二为推步框架绑定（帝旺链）。

**本谓词特有审定点（卷三禄节问题）**：治理登记册 unlock_path 并列了「卷三禄节」。查 F3 形态登记册（`bazi_fire_si_yin_morphology.FORM_BING_SI`）：月条件的 registered anchors 为 `sm2.bing_lu`、`sm2.summary_bracket`、`sf.lubiao`、`dt.bing_lu_single`、`dt.congqiang_def`——**主定义锚是卷二逐干句**，神峰禄表与滴天髓单点均为 witness 级；卷三《论十干禄》在本谓词的任何条件中未被引作锚。卷三禄节是 `pattern-route-luren`（禄刃路线）的定义锚（治理登记册该条 reason 原文），属 P3 前置（该节未登记），不是本谓词的定义锚。审定结论：**本谓词的注册绑定以卷二两节为足，卷三禄节未登记不阻断本谓词**；但实施批的注册记录必须明记此口径（主锚 = 卷二句；卷三禄节为 luren 路线的前置、与本谓词无关），防止后续把 luren 的未解锁误记为本谓词语义缺口。

### 1.2 金×酉 `pure_support_metal`（形态 `metal-you-pure-support-v1`）

治理登记册原文：reason =「根有效性定义锚点为 S1 登记的三命卷二庚/辛逐干生死句，10 条根引文 0 条在 Canonical sections 内（Canonical 三命仅咸池一节）。」unlock_path =「先行 Canonical sections 扩编（三命卷二干支生死节登记入 Canonical），再行注册批。」

定义性证据 = S1 登记册 `bazi_metal_water_roots.ROOT_QUOTES` 10 条中的金四干 6 条（全部位于节一 per_stem_exposition）：

| 证据句 | 在册引文 | 层级 | 作用 |
|---|---|---|---|
| 「其禄到申」 | `sm.geng_lu`（庚段 [40653,40657)） | 列举级原文 | 庚禄位锚 |
| 「长生于己巳中戊土」（己经 sm2-ji-40674 读巳） | `sm.geng_sheng_frag` | 列举级原文（经校定） | 庚长生位锚（帝旺推步链的起点） |
| 「故庚金生于已而死于子」（已经 sm2-yi-40755 读巳） | `sm.geng_shengsi` | 列举级原文（经校定） | 庚生/死合句锚 |
| 「其禄到酉」 | `sm.xin_lu`（辛段 [40936,40940)） | 列举级原文 | **辛禄位锚 = 本谓词月支酉对辛的月根事实（明句重根）** |
| 「长生于子子乃坎水」 | `sm.xin_sheng` | 列举级原文，但属 **conflict 分支甲载体** | 辛长生 conflict 分支甲（阴阳分判）的本节证据；见 §3/§4 相邻说明 |
| 「故辛金生于子而死于巳」 | `sm.xin_shengsi` | 列举级原文，同上 | 同上 |

月根事实（条件 `reviewed_same_element_month_you`）：酉对庚 = 帝旺（**推步推论级**，framework_derived，由庚长生巳推步）；酉对辛 = 禄（列举级）。实现侧已在条件输出上携带 `month_root_grade` 区分两级（庚酉 = framework_derived、辛酉 = per_stem_listed，`bazi_adjudication.py` S2 分支原文）。

拟绑定 Canonical 章节：节一（庚/辛段）为主绑定；节二为庚帝旺推步链的框架绑定。

conflict 相邻面：辛长生 conflict（`sanming-juan2.xin-changsheng`，子 vs 巳）使辛根表子/巳/申三格为 conflicted_pending——但**月支酉对辛是禄位明句、不随分支**（S1 `S2_IMPACT.unlocked` 原文：「酉为庚帝旺（推步重根）与辛禄（明句重根），两干均不随长生分支」），谓词本体不被该 conflict 阻断；实现侧对辛根落子/巳/申的命盘已作冲突阻断，此阻断在注册后必须原样保留。

### 1.3 水×子 `pure_generating_support_water`（形态 `water-zi-pure-generating-v1`）

治理登记册原文：reason =「同 pure_support_metal：壬/癸逐干生死句 0/10 在 Canonical 内。」unlock_path 同金。

定义性证据 = S1 ROOT_QUOTES 中的水四干 4 条（全部位于节一 per_stem_exposition）：

| 证据句 | 在册引文 | 层级 | 作用 |
|---|---|---|---|
| 「其禄在亥」 | `sm.ren_lu`（壬段 [41235,41239)） | 列举级原文 | 壬禄位锚 |
| 「故壬水生于申而死于卯」 | `sm.ren_shengsi` | 列举级原文 | 壬长生位锚（帝旺推步链起点）+ 死位锚 |
| 「其禄在子」 | `sm.gui_lu`（癸段 [41535,41539)） | 列举级原文 | **癸禄位锚 = 本谓词月支子对癸的月根事实（明句重根）**，亦是全谓词唯一真实盘正例（1981-12-21）的根位依据 |
| 「故癸水生于邜而死于申」（邜为快照异体） | `sm.gui_shengsi` | 列举级原文，但属 **conflict 分支甲载体** | 癸长生 conflict 分支甲（生卯）的本节证据 |

月根事实（条件 `reviewed_same_element_month_zi`）：子对壬 = 帝旺（**推步推论级**，由壬长生申推步）；子对癸 = 禄（列举级）。实现侧 `month_root_grade` 已区分（壬子 = framework_derived、癸子 = per_stem_listed）。

conflict 相邻面：癸长生 conflict（`sanming-juan2.gui-changsheng`，卯 vs 申）使癸根表卯/申/亥三格 conflicted_pending；月支子对癸为禄位明句不随分支，谓词本体不被阻断；实现侧冲突阻断须原样保留。

可满足性事实（注册记录必须携带）：壬日主在本形态八条件下**无真实命盘可全真**（`WATER_ZI_SATISFIABILITY.ren_unrealizable`，两条构造性证明通道在册）；癸日主有真实见证正例（1981-12-21，S2 Golden 在册）。注册不得把壬侧表述为「已有真实盘验证」。

## 2 帝旺代偿审定

**问题**：根表将帝旺位计作重根位（如丙午、庚酉、壬子），其在原文中的依据层级为何？

**实证（三层，逐层在册）**：

1. **原文层：无句**。018-A 登记册 `CORROBORATION_FACTS` 的 `no-diwang-sentence` 条原文：「帝旺位无逐干逐字句：以『帝旺在午/临官在巳』式句式全书检索 0 见；丙/丁帝旺（午）只有季节级『火旺于夏』陈述。」`ROOT_TABLE_ASSESSMENT`（verdict = partial）将帝旺列入 `derived_positions`（沐浴/冠带/帝旺/衰/病/墓/绝/胎/养共 9 位），`listed_positions` 只有禄（临官）/长生/死三位。
2. **推步层：框架推论**。帝旺位由三个已登记环节机械推得：该干长生位（逐干明句，节一）+ 十二宫次序（框架明文，节二 `sm2.gong_sequence`）+ 阴阳顺逆（阳干顺行/阴干逆行）。推步链每一环都有登记依据，但**结论句本身不是任何原文或注家的陈述**——它既不是原文列举，也不是注家推论，而是**框架推步（推论级）**。S1 登记册对此的等级名是 `framework_derived`，与 `per_stem_listed` 分级并列、永不混同。
3. **处置层：我方审定裁定**。「推步得出的帝旺位可否计作重根位」不是文本问题而是处置问题，已由火线审定裁定在先：`bazi_fire_morphology.DIWANG_DISPOSITION`（裁定二）verdict = `substituted_by_framework_derivation_with_grade_disclosure`，原文：「午登记为丙的帝旺根位，等级 framework_derived（十二宫推步，推论级）……本形态的『当令』功能要件由 commander 层已审的本气同类关系承担，不由推步单独承担。任何后续引用若把午帝旺表述为原文逐干句，即属证据等级冒充，禁止。」S1 沿用并细化为 verdict = `framework_derivation_for_uncontested_stems_branch_pending_for_conflicted_stems`（庚酉/壬子登记 framework_derived；辛/癸帝旺随长生分支作 conflicted_pending，惟辛酉/癸子已由禄位明句独立定为重根、不受影响）。

**审定结论：满足但须附条件。**

- 条件 1（层级定性）：帝旺代偿的依据层级定性为**推步推论级（framework_derived）**，其可用性来自既有审定裁定（火线裁定二 + S1 处置），**不是原文授权**。注册记录不得出现「原文」「明言」类表述；禁用表述沿 S1 登记册 `DIWANG_DISPOSITION.forbidden_phrasings` 六条（「庚帝旺在酉（原文）」「三命明言庚旺于酉」「壬帝旺在子（原文）」「三命明言壬旺于子」「辛帝旺在申（原文）」「癸帝旺在亥（原文）」），并类推适用于丙（火线登记册 forbidden_phrasings 两条）。
- 条件 2（注册措辞）：Phase1 规则的 evidence 元数据与 Canonical section 记录中，凡引用帝旺位必须使用如下措辞形态（建议定稿）：「帝旺位（推步）：本位无逐干逐字句，系由该干逐干明句之长生位 + 《论五行旺相休囚死并寄生十二宫》十二宫次序 + 阴阳顺逆推步得出，证据等级 framework_derived（推论级），与 per_stem_listed（逐干明句级）分级并列、永不混同。」
- 条件 3（链环绑定）：推步链的每一环必须有已绑定引文支撑——长生明句（节一）与次序框架句（节二 `sm2.gong_sequence`）须同批绑定；缺任一环，该干帝旺位不得随注册引用。
- 条件 4（功能边界）：沿火线裁定二，帝旺推步只作**根位登记**，不单独承担任何形态的「当令」证据；三谓词的月条件当令要件分别由禄位明句（丙巳/辛酉/癸子）或本气同类关系承担，庚酉/壬子的月根事实以 framework_derived 等级随条件输出披露（实现侧已如此，注册后不得回退）。

## 3 推步宫位分级表

**通则（节一 + 节二合并口径，`ROOT_TABLE_ASSESSMENT` 原文）**：十干逐干**列举级**只有三位——禄（临官）、长生、死，陈述俱全（`STEM_COVERAGE` 十干三锚点及定位在册，见下表锚点列）；其余九位——沐浴、冠带、帝旺、衰、病、墓（库）、绝、胎、养——**全部为推步**（长生位 + 十二宫序 + 阴阳顺逆），属推论级。节二只给次序与逐位定义（框架级），不给任何一干的逐位定位。

### 3.1 十干列举级三位锚点（节一 per_stem_exposition，逐干）

| 干 | 禄 | 长生 | 死 |
|---|---|---|---|
| 甲 | 其禄到寅 [39015,39019) | 长生于亥 [39053,39057) | 故甲木死于午 [39177,39183) |
| 乙 | 其禄到邜 [39316,39320) | 生于午 [39414,39426) | 故乙木死于亥 [39454,39460) |
| 丙 | 其禄在己巳 [39568,39578)（校定读巳） | 丙火生于寅 [39659,39668) | 故丙火生于寅而死于酉 [39709,39719) |
| 丁 | 其禄到午 [39864,39873) | **conflict**（见 §4） | **conflict 随生位**（见 §4） |
| 戊 | 其禄在己巳 [40132,40142)（校定读巳） | 故戊土生于寅而死于酉 [40230,40240) | 同左合句 |
| 己 | 其禄到午 [40448,40456) | 故己土生于酉而死于寅 [40515,40525) | 同左合句 |
| 庚 | 其禄到申 [40653,40657) | 长生于己巳中戊土 [40671,40679)（校定读巳） | 故庚金生于已而死于子 [40750,40760)（校定读巳） |
| 辛 | 其禄到酉 [40936,40940) | 长生于子 [40991,40999)（**分支甲**，conflict） | 故辛金生于子而死于巳 [41083,41093)（**分支甲**） |
| 壬 | 其禄在亥 [41235,41239) | 故壬水生于申而死于卯 [41327,41337) | 同左合句 |
| 癸 | 其禄在子 [41535,41539) | 故癸水生于邜而死于申 [41664,41674)（**分支甲**，conflict） | 同左合句（分支甲） |

注：戊/己的长生锚本身是土长生 conflict 的分支甲载体（土行两干皆分歧，`bazi_earth_roots` 登记在册）——本审定三谓词不消费戊/己锚点，此处只登记其层级事实，不展开（土根消费接入是另一条线，且运行时零接入）。

### 3.2 已建根表的四干逐位分级（S1 登记册原文，根相关位）

庚（无 conflict）：巳 长生 = per_stem_listed；申 禄/临官 = per_stem_listed；**酉 帝旺 = framework_derived**；子 死 = 列举级（非根位）；丑/戌 轻根（light_listed_conflicted，根类异文冲突）；余位推步非根位（no_root）。

壬（无 conflict）：申 长生 = per_stem_listed；亥 禄/临官 = per_stem_listed；**子 帝旺 = framework_derived**；卯 死 = 列举级（非根位）；丑/辰 轻根（light_listed_conflicted）；余位推步非根位。

辛（长生 conflict）：酉 禄/临官 = per_stem_listed（**唯一不随分支的重根位**）；子 = conflicted_pending（分支甲长生/分支乙非根）；巳 = conflicted_pending（分支甲死·明句/分支乙长生·五行级）；申 = conflicted_pending（分支甲帝旺·推步/分支乙非根）；丑/戌 轻根（light_listed_conflicted）；余位宫位名随分支、no_root。

癸（长生 conflict）：子 禄/临官 = per_stem_listed（**唯一不随分支的重根位**）；卯 = conflicted_pending（分支甲长生·明句/分支乙死）；申 = conflicted_pending（分支甲死·明句/分支乙长生·五行级）；亥 = conflicted_pending（分支甲帝旺·推步/分支乙非根）；丑/辰 轻根；余位宫位名随分支、no_root。

丙（火线登记册 BING_ROOT_POSITIONS，只登记根相关五位）：寅 长生 = per_stem_listed；巳 禄/临官 = per_stem_listed；**午 帝旺 = framework_derived**；未 余气轻根 = light_listed；戌 墓/余气轻根 = light_listed_conflicted。

丁：**无根表**。禄午两说一致（列举级），但长生/死随 conflict 两分支互换，根位集合不可视为齐备（`DING_BLOCK` 原文：「丁禄午两说一致，不受影响，但禄一位不足以构成根表」）。

甲/乙/戊/己：无逐位根表登记（三谓词不消费；甲/乙的根事实由密封政策 reviewed_root_branches 承载，戊/己见土根登记册）。其九位推步位未逐位登记，任何未来消费者须先建表再引用，不得直接以本审定的通则替代逐位登记。

### 3.3 推步位的可执行证据层级与呈现形态（审定）

**结论：满足但须附条件。**

- 呈现形态：推步位在 Canonical section 与注册记录中必须以**逐位标注**形态出现——每一格位携带 `position_kind`（含「（推步）」字样）与 `grade = framework_derived`，与 per_stem_listed 格位分列呈现（S1/土根登记册的 GRADE_VOCABULARY 形制即为先例，照此执行）。
- 可作 source_refs 的范围：推步位**可以**作为 Rule 的 source_refs 被引用，但引用对象必须是「推步链」整体（长生明句引文 + 次序框架引文 + 顺逆规则），且引用处必须携带 framework_derived 等级字段；**不得**把推步位伪装成一条原文引文引用（不存在可引的原文句）。
- 功能上限：推步位可支撑根位**存在性**事实（如庚根在酉、壬根在子）；不得单独支撑当令、定义性命题或任何需要明句级的条件（§2 条件 4）。

## 4 丁长生 conflict 隔离审定

**conflict 在册形制**：`DING_CHANGSHENG_CONFLICT`（conflict_id = `sanming-juan2.ding-changsheng`，status = conflict，adjudication = null，research_only = true）。分支甲 ding-sheng-you（酉，阴阳分判：本节丁段两句 `sm2.ding_sheng`/`sm2.ding_shengsi` + 神峰楠曰个例）；分支乙 ding-sheng-yin（寅，五行统摄：神峰五行级四生 + 本节论辩段通论存档）。登记册 statement 原文：「两说并列登记、不裁定；任何后续引用必须指名分支。丁的形态（TJ-011.2 F2 等）在本 conflict 处置前不得据丁长生位建立。」

**拟隔离方案**（任务书口径）：丁的长生锚点不绑、其余九干照绑。审定须先把「绑」分两层，否则方案不成立：

- **文本层**：Canonical section 是整节文本，丁段（含丁生/死两句）是节一文本的组成部分，**不存在、也不允许把丁段从 section 文本中切除**——隔离不在文本层执行。
- **绑定层**：Phase1 规则的 source_refs 逐条绑定的是**被谓词消费的引文**。三谓词消费的引文集合（§1）中没有任何丁引文：丁禄句 `sm2.ding_lu` 虽为 agreed 列举级，但无任何谓词以其为锚（丁无形态、无谓词）；丁生/死两句 role 本就是 `conflict_branch_evidence`，不是 `root_table_evidence`。

**审定结论：满足但须附条件**——隔离在**绑定层**成立，「其余九干照绑」须修正为「其余各干**按谓词消费范围**绑定」：本批实际绑定集合 = 丙/庚/辛/壬/癸五干被消费的锚点 + 节二框架引文；甲/乙/戊/己锚点不在本批绑定范围内（无消费者），不是「照绑」。条件如下：

1. **绑定排除断言**：实施批须有专项测试断言——三谓词任一 Phase1 规则的 source_refs 集合 ∩ {`sm2.ding_sheng`, `sm2.ding_shengsi`} = ∅，且任何以丁长生位为定义锚的规则不得存在。
2. **conflict 记录随节携带**：Canonical section 的元数据须逐字携带 `DING_CHANGSHENG_CONFLICT` 记录（两分支 + adjudication = null），使任何读到丁段文本的消费者先看到未裁状态；同理辛/癸两 conflict 记录随节携带（它们与三谓词相邻，见 §1.2/§1.3）。
3. **丁线状态断言**：实施批须有回归断言钉住 `DING_BLOCK`（`bazi_fire_morphology`，status = blocked_by_conflict）、`DING_SI_DISPOSITION` / `DING_YIN_DISPOSITION`（`bazi_fire_si_yin_morphology`，verdict = blocked_by_conflict）三处登记在注册批前后逐字不变，且裁定输出中不存在任何丁日主旺衰谓词（现状即如此，注册批不得改变）。
4. **披露措辞复核**：现行措辞经复核**成立、逐字保留**——DING_BLOCK statement：「丁长生位两说并列未裁定……本批不设计任何丁谓词、不登记丁形态定义；丁形态在本 conflict 处置（用户裁定级流派取舍或长期并列分支登记）之前一律 blocked_by_conflict，不得以任一分支单独建模。」其中「用户裁定级流派取舍」的定性与本审定红线一致：**本审定不裁定、不代裁，隔离只是不让未裁文本进入定义绑定**。

## 5 □1 排除审定

**落点复核（程序实测）**：□1 在册校勘记为 `sm2-gap-42148`（char_offset 42148，snapshot_glyph = □ U+25A1，reading = null，reading_status = unresolved，disposition = unresolved，note 原文：「缺字占位符（非 PUA）：原文保留、不补字、不入引文。」）。其上下文为「…戊生申酉沐浴戌冠带阴阳间隔谬□甚矣或曰五行长生有母而后有子…」，位于节一 lunyue_summary 段 [41810,42151) 的尾部。本批程序核对：节一全部 9 条登记引文中**无一条覆盖 42148**（最接近的 `sm2.summary_tu` 止于 42116），`STEM_COVERAGE` 全部锚点亦无一覆盖该位点——现状即「不入引文」，与 UD-2 = A（永久缺口不补字）一致。

**周边引文可用范围复核**：

- `sm2.summary_bracket` [41895,42017) 与 `sm2.summary_tu` [42017,42116)：均在缺口句之前，内容为四长生总结块与土行讨论正述，**可用**（summary_tu 内的设问驳斥句「若以戊生申…」是被驳斥的假设句，引用时不得把假设读法当作者立场——登记册 mapped_reading 已注明此性质）。
- lunyue_summary 尾段 [42116,42151)：含拟土歌引文句与含 □ 的整句，**整段排除于任何新绑定引文之外**。双重理由：(a) 含永久缺口字；(b) 该句内的「戊生申酉沐浴戌冠带」是紧随设问驳斥语境的推步式枚举，把它作定义锚会同时踩中缺口与语境误读。
- debate_quotations 段 [42151,43082) 本为 archived_not_evidence，`sm2.sida_archive` 只作 conflict 体例背景存档——维持现状，不入绑定。

**机检方案（审定结论：满足但须附条件）**——条件为实施批必须落以下三条断言，缺一不可：

1. **覆盖断言**：对实施批绑定的全部引文集合逐条断言 `not (char_start <= 42148 < char_end)`（坐标为 S0 口径；经 origin 位点图换算至 S3 后坐标不变，P4 在案 S3 位点同为 42148，断言须在换算后坐标上再跑一次）。
2. **负例断言**：构造一条覆盖 [42140,42151) 的伪绑定引文，验证器必须拒绝（fail-closed），证明排除不是靠人工清单而是靠机检。
3. **缺口状态断言**：断言 Canonical section 元数据中 `sm2-gap-42148` 仍为 disposition = unresolved、reading = null（UD-2 A 定格在注册后不变）。

## 6 Trace / Golden / Phase2 入口核查

逐谓词以 `bazi_adjudication.py` 在册实现与登记为据。三谓词共有的执行形制先述，差异后述。

**共有形制（代码原文核实）**：三谓词均已实现于 bounded strength assessment，运行在 `ExecutionTrace` 之上：每个条件的成立都绑定到已执行步骤 `bazi.phase2.action_effects` 的 evidence（fact_ref 逐条指向 trace 内事实）。但三谓词都**没有自己的 Phase1 规则 ID，也没有自己的 Phase2 规则步**：裁定经已注册的 bounded-adjudication 出口 `bazi.rule.r026` 发出，裁定对象上明示 `sufficient_rule = None`、`predicate_rule_registration = 'pending_phase1_rule_registration'`（lu 分支与 S2 分支注释原文均如此自述：「has no sealed Phase1/Phase2 rule registration yet … no rule ID is borrowed from another predicate」）。对照组：S5 已注册的两谓词（r029 `pure_generating_support`、r030 `commanding_visible_support`）经各自的 `bazi.phase2.strength_<predicate>` 规则步发出裁定——这正是注册翻转要补的实体。`tests/test_phase2_baziadjudication.py` 只断言 `bazi.phase2.strength_adjudication` 在场，不构成三谓词的 Phase2 入口。

| 入口 | lu_visible_support | pure_support_metal | pure_generating_support_water |
|---|---|---|---|
| ExecutionTrace 覆盖 | **满足**：条件逐条绑定 action_effects 已执行证据，经 r026 出口发出，pending 状态随裁定披露 | **满足**（同左） | **满足**（同左） |
| 真实盘 Golden | **满足**：`golden_tj0112_f34_si_yin.json`（7 例），含穷举扫描（1900–2100、7,512 盘）唯一正例 1927-05-12（丁卯/乙巳/丙午/甲午）为正例见证 | **满足但须附条件**：无真实盘正例——八条件构造性不可满足已在册证明（`METAL_YOU_SATISFIABILITY` status = chart_unrealizable，两条历法构造通道 + E0257 复核在案）；S2 Golden 以因子层基线 + 不可满足登记为形态。条件：注册验收**不得要求真实盘正例**，须以「不可满足证明 + 因子层 Golden + 近失面」为本谓词的 Golden 形态并在注册记录中明记 | **满足**：S2 Golden 含癸日主真实盘正例（1981-12-21 辛酉/庚子/癸酉/壬子，八条件全真逐项推导在册）与壬日主近失例（1921-12-15，其余七条件全真、仅 visible 比劫一条假）；壬侧不可满足另有证明在册 |
| 自有 Phase1 规则 | **不满足**：无（pending 即此） | **不满足**：无 | **不满足**：无 |
| 自有 Phase2 规则步/执行入口 | **不满足**：无 `bazi.phase2.strength_lu_visible_support` 步 | **不满足**：无 | **不满足**：无 |

**本节总结论**：三谓词的**执行**是真实的（Trace + 已实现条件逻辑 + Golden 均在），缺的只是**注册实体**（自有 Phase1 规则 + 自有 Phase2 步）。因此注册翻转的验收对象是「新注册的规则步与既有 r026 出口裁定逐盘等价」，而不是重新验证谓词逻辑；同时**严禁以「Canonical section 已建」替代本节逐项验收**——Canonical 建节只解决 source_refs 可绑，不自动产生 Phase1/Phase2 规则。

## 7 逐谓词结论与最小实施批切法

| 谓词 | 补审结论 | 依据要点 |
|---|---|---|
| 丙×巳 `lu_visible_support` | **满足但须附条件 → 可进入实施批** | 定义锚（卷二禄句）列举级齐备；条件 = §1.1 卷三禄节口径明记、§2 帝旺披露四条件、§4 丁隔离三断言、§5 □1 三断言、滴天髓侧定义锚的 Canonical 绑定问题须在实施批内单独核（见 §8），核不通则本谓词单独保留 pending |
| 金×酉 `pure_support_metal` | **满足但须附条件 → 可进入实施批** | 庚/辛锚点齐备、月根两级已分级披露；条件 = §2 帝旺披露、辛 conflict 三格阻断原样保留、§6 Golden 形态按不可满足口径验收（不要求真实盘正例） |
| 水×子 `pure_generating_support_water` | **满足但须附条件 → 可进入实施批** | 壬/癸锚点齐备、癸有真实盘正例；条件 = §2 帝旺披露、癸 conflict 三格阻断原样保留、壬侧不可满足事实随注册记录明记 |

**最小实施批切法（建议，一批三谓词、逐条独立翻转）**：

- **切法原则**：一个实施批（密封 Canonical 两节建节 + 三谓词注册），但**注册翻转逐谓词独立判定**——任一谓词在批内验收有一项条件不齐，该谓词单独保留 pending，其余照常翻转（沿 S5 只翻 2 项、余项维持 pending 的先例）。本审定**不承诺三条全部注册成功**。
- **密封侧文件面**：Canonical 三命通会新增两节 section（整节文本经 origin 图换算 S0→S3 逐字校验）+ 逐条引文绑定（§1 清单 + 节二框架引文）+ 三 conflict 记录与 □1 缺口记录随节元数据携带；快照/manifest 若因此变动，按既有原子换代四步纪律由父级在合并时同步执行（本审定不预判是否触发换代，见 §8）。
- **公开仓文件面**：`bazi_registration_governance.py` 三条 disposition 更新（逐条独立）；`bazi_adjudication.py` 三谓词裁定出口由 r026 改走各自新规则步（照 r029/r030 先例形态，sufficient_rule 落新 ID、conditions 的 anchor_type 与 month_root_grade 披露不变）。
- **测试面**：密封侧 Phase1/Phase2 注册专项（新规则步存在性 + 与 r026 出口的逐盘等价）；公开侧治理登记专项更新；§4 绑定排除断言 + 丁线状态断言；§5 □1 三断言；判定面零变化比对（照 S5 先例的逐盘比对，覆盖三谓词各自的正例/近失/阻断面盘例：丙 1927-05-12、癸 1981-12-21、壬 1921-12-15 近失、辛/癸 conflict 阻断盘）。
- **全配方复跑**：**需要**。本批动来源登记与 Golden，按 TJ-013.1 站立规则，合并前必须在机上按完整配方（`scripts/accept_offline.py --suite all`）复跑 0 失败；计数口径 = 届时正式基线 + 本批新增，逐项对平。
- **不做**：不建任何新谓词；不改三谓词的任何条件与输出；不碰丁线、扶抑、土根消费接入；不把卷三禄节混入本批（属 P3 前置）。

## 8 仍无法判断的范围

1. **滴天髓侧定义锚的 Canonical 绑定状态未在本审定内核实**：lu 谓词的定义本体（从旺/从强定义、根重轻列举）在滴天髓阐微侧，其引文是否已有 Canonical section 可绑、绑定形制如何，须在实施批开工时于密封环境内核查（公开仓只能确认 Canonical 有滴天髓阐微一书，不能确认逐节 section 覆盖）。若该侧绑定不通，lu 单独保留 pending（§7 已作此条件）。
2. **密封注册验证器的实际校验口径**：Phase1 注册时验证器对 source_refs 的校验粒度（逐引文校验还是逐节校验）、对 framework_derived 等级字段的接受形态，只能在实施批的密封环境内实证；本审定的措辞与断言按最严口径（逐引文 + 等级随行）设计，若验证器更严，以验证器实测为准并回记本文件。
3. **Canonical 建节是否触发快照换代**：取决于密封侧 Canonical 数据的存放形态（是否在快照 manifest 覆盖内），公开仓不可判；实施批开工先核此项，再决定是否走换代四步。
4. **甲/乙/戊/己四干的逐位推步表**：未建登记、无消费者，不在本审定范围；将来任何引用此四干根位的谓词须另行建表审定，不得援引本审定的通则充当逐位登记。
5. **辛/癸/丁/土四组长生 conflict 的最终处置**：全部维持并列未裁；其裁定属用户级流派取舍（丁）或后续审定（辛/癸/土），本审定的隔离方案只保证未裁文本不进入定义绑定，不构成任何一方的胜出。

---

*审定边界声明：本文件为本地审定文档，未提交仓库、未建 PR、未动台账（事件号 E0331 由父级预留，待 P1 关账后另批入册）；全部结论以 live main `006097d5` 在册文件为据，数字均经程序化核对；未登录密封环境调取 Canonical 本体，涉及密封侧的事项已在 §8 逐项标明为待实施批实证。*

入册注记（E0331）：本文件于 2026-10-30 入册为仓库文档 `docs/product/TJ0183_P2_GANZHI_ADJUDICATION.md`；入册不构成任何注册翻转，三谓词注册状态以 `bazi_registration_governance.py` 在册登记为准，实施批另按审定 §7 切法启动。
