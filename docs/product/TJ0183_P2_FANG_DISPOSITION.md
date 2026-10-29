# TJ-018.3 晋级 P2：残余「防」769 处逐处处置（首批）

登记册：`sanming-residual-fang-disposition-register-v1`
（`src/tianji_kb/bazi_sanming_fang_disposition.py`，纯数据；
Golden：`tests/golden_tj0183_sanming_fang_disposition.json`）。
任务书：`TJ0183_FORMAL_APPLICATION_DESIGN.md` §4.1（残余防路线）
与 §5.2 P2。台账事件 E0302（归属 TJ-018.2，状态不变）。

## 1. 定位与边界

《三命通会》S3 应用文本（SHA256
`a89c0b5da16ea4e07dc85180c49135ed280875318059f923ff7154f2c217662f`）
的残余扫描定案为：PUA 0、**防 769**、□ 2（应用记录登记册
`RESIDUAL_SCAN` 同值）。「防」是多源汇讹字（各校勘组实测其校定
读法涉及 㑹/㸔/㓙/㽞/䌓/喬/㣲/從 等多字），设计明定**全局替换
永久禁用、逐处互校**。本批建立处置登记册形态并完成第一分册：

- **只登记处置结论，不改任何文本**：S3 应用文本、快照本体、
  三份校勘 JSON、PUA 审计 JSON、应用报告逐字未动（密封专项
  以文件哈希钉验证）；`canonical_ready` 保持 false。
- `disposed_confirmed` 的读法只是**未来 v2 应用的裁定候选**，
  本批不应用；何时应用由后续批次按同一 fail-hard 纪律另行执行。
- 累计处置进度口径：**disposed 14/769**（本批定案数/残余总数）；
  deferred 不计入 disposed；节外 726 处只盘点、未处置。

## 2. 处置分类（先定义，后使用）

| 分类 | 定义 |
|---|---|
| disposed_confirmed | = 设计 §4.1 的 confirmed_reading。四库谱系与至少一个独立现代谱系在该位点同读 X（X≠防），且无已定位的独立异读；X 登记为未来应用候选，文本不动。保留侧从严：四库同读防时不要求第二方（见 disposed_kept），改读侧必须双方齐备。 |
| disposed_kept | 见证支持保留「防」：四库谱系同读防、无已定位异读（含固定语汇：隄防、预防、防灾、多防）。保留不主张文本有误，故不要求现代第二方。 |
| disposed_parallel | = 设计 §4.1 的 variant_parallel。独立谱系在该位点分歧（一方之读法与他方在场证据冲突，含文句在场而该字脱字）；并列登记、不裁定。 |
| deferred_no_witness | = 设计 §4.1 的 hold。本批已逐处互校，但独立见证未齐（现代谱系文句未载、仅有旁证、或属 P3 的 RD-12 范围）；已有证据逐字在案，不凭语境猜改，待补第二独立见证方后逐处升级。 |
| pending_later_tranche | 节外位点：本批只盘点登记（坐标、语境、卷属、候选/RD-12 标记），处置留待后续分册。 |

## 3. 全量盘点（769/769）

盘点方法：对 S3 应用文本逐字扫描「防」得 769 处；每处经应用批
origin 位点图（自建两阶段复放逐字追踪，S1/S2/444 检查点/S3 四
钉全符；与应用报告 993 条 dispositions 的 S2→S3 位点腿
993/993 一致）换算 S0 坐标。**769 处的 origin 全部是真实的 S0
「防」字**（identity 739、位于某条订正替换串内 30；无一处由
PUA 替换或订正插入产生）。每行登记：S3/S0 坐标、±6 字语境及
SHA256、所在卷、是否位于已登记节、既有校勘记 id、是否为
603 候选位点（518 处）、是否为 RD-12 位点（8 处：seq
361/385/450/612/616/824/873/933——RD-12 中有 8 条的位点本身
即残余「防」位点，其处置属 P3，其中 seq 450 在本批节内、
已 deferred 并记录双方证据，余 7 处在后续分册盘点中同标 P3
范围）。

已登记节全集 32 个 span：六个校勘登记模块的 24 节（节内快照
「防」106 处，与六模块 106 条 `-fang-` 校勘记一一对应）+
review_scope 散文登记的 8 个 span（论人元司事、论大运、
论十干禄、Slice B 两窗口、珞琭子三窗口）。节内 S3 残留
43 处（其余 63 处节内「防」已被 603 应用改写、不再残留），
其中 40 处有校勘记、3 处无（S0 49021/58542/76988）。

| 卷 | 盘点 | confirmed | kept | parallel | deferred | pending |
|---|---|---|---|---|---|---|
| 卷首 | 1 | 0 | 0 | 0 | 0 | 1 |
| 卷一 | 10 | 0 | 0 | 0 | 0 | 10 |
| 卷二 | 34 | 0 | 1 | 1 | 6 | 26 |
| 卷三 | 50 | 0 | 0 | 0 | 1 | 49 |
| 卷四 | 118 | 0 | 0 | 0 | 0 | 118 |
| 卷五 | 89 | 5 | 2 | 0 | 15 | 67 |
| 卷六 | 142 | 4 | 1 | 0 | 7 | 130 |
| 卷七 | 75 | 0 | 0 | 0 | 0 | 75 |
| 卷八 | 61 | 0 | 0 | 0 | 0 | 61 |
| 卷九 | 94 | 0 | 0 | 0 | 0 | 94 |
| 卷十 | 26 | 0 | 0 | 0 | 0 | 26 |
| 卷十一 | 45 | 0 | 0 | 0 | 0 | 45 |
| 卷十二 | 24 | 0 | 0 | 0 | 0 | 24 |
| 合计 | 769 | 9 | 4 | 1 | 29 | 726 |

## 4. 本批处置（节内 43 处逐处）

见证口径（沿 PUA 全核批）：四库谱系 = kanripo
`efe780a4…` + mikkokotila `eb3cacbf…` 合计**一方**；现代
NiuTrans `4e746ea9…`、youngzs `aa7bc942…` 各为独立一方；
Banny-Gao `5a75273e…` 只作旁证（record-only，其引文只取其
《三命通会》转录子集，他书引文不作旁证）。43/43 处四库两家
均已在该位点定位并登记逐字引文。定案门槛不对称从严：
confirmed 须四库 + 至少一独立现代方同读；kept 只须四库同读
防且无异读（保留不主张文本有误）；现代转录多为节选/重编本，
「文句未载」是常态而非反证——未载者一律 deferred，不猜改。

| S0 位点 | 卷·节 | 校勘记读法（状态/处置） | 处置分类 | 结论与见证要点 |
|---|---|---|---|---|
| 39476 | 卷二·论天干阴阳生死 | 䌓（confirmed/corrected） | deferred 待补见证 | 四库及校勘读法在案，现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 39804 | 卷二·论天干阴阳生死 | 䌓（confirmed/corrected） | deferred 待补见证 | 四库及校勘读法在案，现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 41370 | 卷二·论天干阴阳生死 | 防（contextual/genuine） | kept 保留 | 保留「防」，语境与见证自明（固定语汇）；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 41426 | 卷二·论天干阴阳生死 | 㑹（confirmed/corrected） | deferred 待补见证 | 四库及校勘读法在案，现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 49021 | 卷二·论人元司事 | （无校勘记） | deferred 待补见证 | 四库读法在案（本批见证引文），无既有校勘记，现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 58542 | 卷二·论大运 | （无校勘记） | deferred 待补见证 | 四库读法在案（本批见证引文），无既有校勘记，现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 73447 | 卷二·论三刑 | 䘮（confirmed/corrected） | deferred 待补见证 | 四库及校勘读法在案，现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 73703 | 卷二·论三刑 | 㸔（confirmed/corrected） | parallel 并列 | 四库读「㸔」与现代脱字分歧，并列不裁；NiuTrans 文句在场而该字脱字；youngzs 文句在场而该字脱字；Banny-Gao（旁证） 文句在场而该字脱字 |
| 76988 | 卷三·论十干禄 | （无校勘记） | deferred 待补见证 | 四库读法在案（本批见证引文），无既有校勘记，现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 158245 | 卷五·弃命从煞 | 㑹（confirmed/corrected） | deferred 待补见证 | 四库及校勘读法在案，现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 158422 | 卷五·弃命从煞 | 䘮（confirmed/corrected） | deferred 待补见证 | 四库及校勘读法在案，现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 159249 | 卷五·官煞去留杂论 | 㽞（confirmed/corrected） | confirmed 定案 | 应改读「留」（校勘字形 㽞），登记为未来应用候选；NiuTrans 题级同读「留」；youngzs 题级同读「留」；Banny-Gao（旁证） 未载 |
| 161294 | 卷五·官煞去留杂论 | 㓕（confirmed/corrected） | confirmed 定案 | 应改读「滅」（校勘字形 㓕），登记为未来应用候选；NiuTrans 未载；youngzs 同读「灭」（sentence）；Banny-Gao（旁证） 未载 |
| 161298 | 卷五·官煞去留杂论 | 㓙（confirmed/corrected） | confirmed 定案 | 应改读「凶」（校勘字形 㓙），登记为未来应用候选；NiuTrans 未载；youngzs 同读「凶」（sentence）；Banny-Gao（旁证） 未载 |
| 172012 | 卷五·论杂气 | 㓙（confirmed/corrected） | deferred 待补见证 | 四库及校勘读法在案，现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 172641 | 卷五·论杂气 | 㓙（confirmed/corrected） | deferred 待补见证 | 四库及校勘读法在案，现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 172644 | 卷五·论杂气 | 㓙（confirmed/corrected） | deferred 待补见证 | 四库及校勘读法在案，现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 180886 | 卷五·论阳刃 | 㸔（confirmed/corrected） | confirmed 定案 | 应改读「看」（校勘字形 㸔），登记为未来应用候选；NiuTrans 同读「看」（full_flank）；youngzs 同读「看」（full_flank）；Banny-Gao（旁证） 未载 |
| 182493 | 卷五·论阳刃 | 㓙（confirmed/corrected） | deferred 待补见证 | 四库及校勘读法在案，现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 182679 | 卷五·论阳刃 | 㓙（confirmed/corrected） | confirmed 定案 | 应改读「凶」（校勘字形 㓙），登记为未来应用候选；NiuTrans 同读「凶」（sentence）；youngzs 同读「凶」（sentence）；Banny-Gao（旁证） 未载 |
| 182822 | 卷五·论阳刃 | 㫁（confirmed/corrected） | deferred 待补见证 | 四库及校勘读法在案，现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 183539 | 卷五·论阳刃 | 㸔（confirmed/corrected） | deferred 待补见证 | 四库及校勘读法在案，现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 183540 | 卷五·论阳刃 | 㓙（confirmed/corrected） | deferred 待补见证 | 四库及校勘读法在案，现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 183678 | 卷五·论阳刃 | 防（contextual/genuine） | kept 保留 | 保留「防」，语境与见证自明（固定语汇）；NiuTrans 同读「防」（full_flank）；youngzs 同读「防」（full_flank）；Banny-Gao（旁证） 同读「防」（full_flank） |
| 183917 | 卷五·论阳刃 | 㑹（confirmed/corrected） | deferred 待补见证 | 四库及校勘读法在案，现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 183983 | 卷五·论阳刃 | 㓙（confirmed/corrected） | deferred 待补见证 | 四库及校勘读法在案，现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 184103 | 卷五·论阳刃 | 㓙（confirmed/corrected） | deferred 待补见证 | 四库及校勘读法在案，现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 184159 | 卷五·论阳刃 | 㑹（confirmed/corrected） | deferred 待补见证 | 四库及校勘读法在案，现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 184165 | 卷五·论阳刃 | 㓙（confirmed/corrected） | deferred 待补见证 | 四库及校勘读法在案，现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 184187 | 卷五·论阳刃 | 防（contextual/genuine） | kept 保留 | 保留「防」，语境与见证自明（固定语汇）；NiuTrans 同读「防」（full_flank）；youngzs 同读「防」（full_flank）；Banny-Gao（旁证） 同读「防」（full_flank） |
| 184318 | 卷五·论阳刃 | 䕶（confirmed/corrected） | deferred 待补见证 | RD-12 位点（seq 450），裁定权在 P3；双方证据在案；NiuTrans 异读「获」；youngzs 未载；Banny-Gao（旁证） 异读「获」 |
| 204784 | 卷六·稼穑 | 防（contextual/genuine） | kept 保留 | 保留「防」，语境与见证自明（固定语汇）；NiuTrans 同读「防」（side_anchored）；youngzs 同读「防」（side_anchored）；Banny-Gao（旁证） 同读「防」（side_anchored） |
| 204834 | 卷六·稼穑 | 㐫（confirmed/corrected） | confirmed 定案 | 应改读「凶」（校勘字形 㐫），登记为未来应用候选；NiuTrans 同读「凶」（side_anchored）；youngzs 同读「凶」（side_anchored）；Banny-Gao（旁证） 同读「凶」（side_anchored） |
| 213136 | 卷六·贵象 | 㣲（confirmed/corrected） | deferred 待补见证 | 四库及校勘读法在案，现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 213562 | 卷六·属象 | 㸔（confirmed/corrected） | confirmed 定案 | 应改读「看」（校勘字形 㸔），登记为未来应用候选；NiuTrans 同读「看」（side_anchored）；youngzs 同读「看」（side_anchored）；Banny-Gao（旁证） 同读「看」（side_anchored） |
| 213569 | 卷六·属象 | 㸔（confirmed/corrected） | deferred 待补见证 | 四库及校勘读法在案，现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 213823 | 卷六·类象 | 㑹（confirmed/corrected） | deferred 待补见证 | 四库及校勘读法在案，现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 213837 | 卷六·类象 | 㑹（confirmed/corrected） | deferred 待补见证 | 四库及校勘读法在案，现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 214489 | 卷六·从象 | 㑹（confirmed/corrected） | confirmed 定案 | 应改读「會」（校勘字形 㑹），登记为未来应用候选；NiuTrans 同读「会」（side_anchored）；youngzs 同读「会」（side_anchored）；Banny-Gao（旁证） 同读「会」（side_anchored） |
| 214497 | 卷六·从象 | 㑹（confirmed/corrected） | confirmed 定案 | 应改读「會」（校勘字形 㑹），登记为未来应用候选；NiuTrans 同读「会」（side_anchored）；youngzs 未载；Banny-Gao（旁证） 同读「会」（side_anchored）；见证路径：四言独步平行传文（卷十二） |
| 214507 | 卷六·从象 | 㑹（confirmed/corrected） | deferred 待补见证 | 四库及校勘读法在案，现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 214575 | 卷六·化象 | 㸔（confirmed/corrected） | deferred 待补见证 | 四库及校勘读法在案，现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 214929 | 卷六·化象 | 㸔（confirmed/corrected） | deferred 待补见证 | 四库及校勘读法在案，现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |

定案 14 处要点：

- **confirmed 9**：159249 㽞（节题字，现代谱系以分节题名
  「官煞去留杂论」及正文首句题级互证）、161294 㓕/161298 㓙
  （youngzs 句级互证「木绝得火则火飞烟灭此为尤凶」——该家
  此句作「火飞」与快照「灰飞」邻位异文，故以句级而非侧翼
  定位）、180886 㸔、182679 㓙（现代两家句级互证）、
  204834 㐫、213562 㸔、214489 㑹、214497 㑹（NiuTrans 本节
  文本节略，经其卷十二《四言独步》平行传文互证「须要会煞」；
  Banny-Gao 旁证同读并载完整歌句）。
- **kept 4**：41370 隄防、183678 预防、184187 防灾、
  204784 多防——四库同读防，固定语汇；后三处现代谱系同读防。
- **parallel 1**：73703——四库读「㸔」（贵命㸔余准此推），
  现代三家文句在场而该字脱字（作「贵命余准此推」），字级
  分歧、并列不裁。与「整句被节选删去」的未载位点严格区别。

## 5. deferred 29 处的升级路径

29 处中 26 处有 confirmed 校勘记（四库读法在案）、3 处无
既有校勘记（49021/58542/76988，四库读法由本批见证引文
在案），缺口统一为**第二个独立见证方**：现代三家于该位点
文句未载（节选/重编所致）。升级路径（任一成立
即可逐处升级）：(1) 补入新的独立转录谱系（如 Wikisource
michiboo 转录的对应卷次，PUA 全核批已用其为 crosscheck
谱系之一）；(2) 四库影印原叶定位（位点级纸本见证）；(3)
现代全本转录补齐对应节。184318（RD-12 seq 450）不在此
路径内：其「䕶/获」分歧已由本批记录双方证据，裁定随 P3
按 §4.2 谱系标准处理。

## 6. 剩余分册计划（节外 726 处，按卷序；卷首 1 处并入卷一册）

| 分册 | 范围 |
|---|---|
| P2 后续分册·卷首 | 待处置 1 处 |
| P2 后续分册·卷一 | 待处置 10 处 |
| P2 后续分册·卷二 | 待处置 26 处 |
| P2 后续分册·卷三 | 待处置 49 处 |
| P2 后续分册·卷四 | 待处置 118 处 |
| P2 后续分册·卷五 | 待处置 67 处 |
| P2 后续分册·卷六 | 待处置 130 处 |
| P2 后续分册·卷七 | 待处置 75 处 |
| P2 后续分册·卷八 | 待处置 61 处 |
| P2 后续分册·卷九 | 待处置 94 处 |
| P2 后续分册·卷十 | 待处置 26 处 |
| P2 后续分册·卷十一 | 待处置 45 处 |
| P2 后续分册·卷十二 | 待处置 24 处 |
| P3（并行） | RD-12 十二条逐条互校；其中「防」位点 8 处（本批 seq 450 已 deferred，余 7 处在各卷册中只标记） |

每册沿用本册形态：逐处互校、分类计数对账、累计进度
disposed/769 更新；RD-12 的 7 处节外「防」位点在各册中只
标记、处置随 P3。

## 7. 方法与限制

- 定位方法：见证文本经 NFKC + OpenCC 繁转简 + 标点剥离
  规范化后，以快照 ±13/10/8/6 字侧翼全锚定位，失败者以
  9/8/7 字单侧锚 + 邻字校验补位（登记册逐条记 match_mode）；
  另设形近字折叠表（僅用于定位，如 刄→刃、刼→劫、藉→借、
  著→着、乆→久；含 PUA 字与相邻「防」位点的通配）——
  登记引文一律逐字取见证原文，折叠不进入证据。
  双生位点（如独步歌句在弃命从煞/从财、从象三处重出）只认
  本节定位或明示的平行传文路径（如《四言独步》），不以
  相似句投票跨节冒认（158245 处 NiuTrans《四言独步》文本
  在该字处残缺「�」，故该处仍 deferred，不借旁证 Banny-Gao
  的完整歌句定案——旁证不计方）。
- 现代谱系的独立性沿 PUA 全核批口径：NiuTrans 与 youngzs
  为两家独立转录（简体、分节/分篇形态互异）；Banny-Gao
  汇编性质，只作旁证。
- 本批不动：应用文本与报告、快照与校勘/PUA JSON、
  public_domain_manifest（无新密封文件入快照）、来源登记
  条数（101，review_scope 仅尾部追加本批记录段）。

## 8. 验收口径

- 公开专项：Golden 逐字镜像、纯数据形制、盘点完备性与
  分类计数对账、与应用记录登记册的残余扫描/产物钉交叉
  一致、处置规则（confirmed 双见证、kept 四库同读、
  parallel 唯一、deferred 不冒认 candidate）。
- 密封专项（离线验收）：六件密封文件哈希钉逐字未动、
  两阶段复放四钉重建、769 位点/origin/语境对密封原文
  全量复核、43 条处置的 S0/S3 语境逐字、校勘记交叉核对。
- 机上完整复跑（accept_offline --suite all）对 PR Head 执行，
  计数与同环境基线对账后由父级合并；本批止于 PR。
