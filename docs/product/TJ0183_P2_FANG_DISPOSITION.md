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

## 9. 第二分册（卷首·卷一·卷二·卷三节外 86 处，E0304）

### 9.1 范围与方法补记

- 范围：按卷序自最早未处置卷起、连续覆盖整卷——卷首 1 +
  卷一 10 + 卷二 26 + 卷三 49 = **86 处**（全部为节外
  pending 位点）。整卷不拆：若再并入卷四（118 处），本批
  将达 204 处，超出任务书约 120–160 处之度，故卷四起为
  后续分册。本册范围内**无 RD-12 位点**（7 处节外 RD-12
  「防」位点分布于卷五/卷七/卷十/卷十一，仍只标记、处置
  随 P3）。
- 方法补记：节外位点无既有校勘记可预设候选读法，本册定位
  改为**捕获式**——以快照 ±13/10/8/6 字侧翼全锚（失败时
  9/8/7 字单侧锚 + 邻字校验补位）在见证规范化文本中定位
  后，直接捕获位点实际字；读法完全由捕获结果决定，裁定
  表在生成器内逐条断言复核（捕获与裁定不一致即停批）。
  四库两家 **86/86 全部定位且读法逐处完全一致**（无一
  分歧、无一脱字）；现代谱系定位 26 处（NiuTrans 13、
  youngzs 14 含脱字 1、Banny-Gao 旁证 13）。

### 9.2 本册计数

| 卷 | 盘点 | confirmed | kept | parallel | deferred | pending |
|---|---|---|---|---|---|---|
| 卷首 | 1 | 0 | 0 | 1 | 0 | 0 |
| 卷一 | 10 | 0 | 8 | 0 | 2 | 0 |
| 卷二 | 34 | 2 | 2 | 1 | 29 | 0 |
| 卷三 | 50 | 1 | 6 | 0 | 43 | 0 |
| 本册合计 | 86 | 3 | 15 | 1 | 67 | 0 |

### 9.3 本册处置（86 处逐处）

| S0 位点 | 卷 | 语境（S3 ±6） | 处置分类 | 结论与见证要点 |
|---|---|---|---|---|
| 188 | 卷首 | 以此本为总彚防于家有其书中 | parallel 并列 | 四库读「㡬」（幾）与 youngzs 文句在场脱字分歧，并列不裁；NiuTrans 未载；youngzs 文句在场而该字脱字；Banny-Gao（旁证） 未载 |
| 12695 | 卷一 | 城头之土取隄防之功王公恃之 | kept 保留 | 保留「防」，四库两家同读防、无已定位异读；NiuTrans 同读「防」（side_anchored）；youngzs 同读「防」（side_anchored）；Banny-Gao（旁证） 同读「防」（side_anchored） |
| 17070 | 卷一 | 光大惟忌夏生防吉中有凶
  | kept 保留 | 保留「防」，四库两家同读防、无已定位异读；NiuTrans 同读「防」（side_anchored）；youngzs 同读「防」（full_flank）；Banny-Gao（旁证） 同读「防」（side_anchored） |
| 22196 | 卷一 | 帅外藩出镇边防有不常矣丁巳 | kept 保留 | 保留「防」，四库两家同读防、无已定位异读；NiuTrans 同读「防」（full_flank）；youngzs 同读「防」（full_flank）；Banny-Gao（旁证） 同读「防」（full_flank） |
| 24647 | 卷一 | 上火日时遇之防刑尅再考玅选 | kept 保留 | 保留「防」，四库两家同读防、无已定位异读；NiuTrans 同读「防」（side_anchored）；youngzs 同读「防」（side_anchored）；Banny-Gao（旁证） 同读「防」（side_anchored） |
| 25375 | 卷一 | 宜五行见土须防尅破若壁土可 | kept 保留 | 保留「防」，四库两家同读防、无已定位异读；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 26673 | 卷一 |  桑柘木者缯防镃基绮罗根本 | deferred 待补见证 | 四库两家同读「綵」（綵），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 29196 | 卷一 | 吉推土爱路傍防见诸火大驿逢 | kept 保留 | 保留「防」，四库两家同读防、无已定位异读；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 31469 | 卷一 | 蹇涸而土有隄防之用六土之中 | kept 保留 | 保留「防」，四库两家同读防、无已定位异读；NiuTrans 同读「防」（full_flank）；youngzs 同读「防」（full_flank）；Banny-Gao（旁证） 同读「防」（full_flank） |
| 36359 | 卷一 | 滥赖土尅以隄防水火均则合旣 | kept 保留 | 保留「防」，四库两家同读防、无已定位异读；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 37828 | 卷一 | 

 三命通防卷一
<子部 | deferred 待补见证 | 四库两家同读「㑹」（會），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载；位点为卷端页眉书名「三命通㑹卷一」之「㑹」字；现代各家页眉形态不同、位点未载，候选只据四库两家登记 |
| 38234 | 卷二 | 金纳于离火火防金销不能退立 | deferred 待补见证 | 四库两家同读「㷔」（焰），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 38814 | 卷二 | 皆同润下行凡防人命如遇甲乙 | deferred 待补见证 | 四库两家同读「㸔」（看），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 44578 | 卷二 | 出地上之格有防哉有防哉凡六 | deferred 待补见证 | 四库两家同读「㫖」（旨），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 44581 | 卷二 | 之格有防哉有防哉凡六丙生冬 | deferred 待补见证 | 四库两家同读「㫖」（旨），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 46864 | 卷二 | 墙不产珍金剑防功成遇火乡而 | deferred 待补见证 | 四库两家同读「㦸」（戟），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 47477 | 卷二 | 缺兽体岂全故防少光夜出牛无 | deferred 待补见证 | 四库两家同读「䑕」（鼠），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 47568 | 卷二 | 化相应惟人独防其全此其所以 | deferred 待补见证 | 四库两家同读「㑹」（會），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 49278 | 卷二 | 也卦气正月为防天气下降当为 | confirmed 定案 | 应改读「泰」（四库字形 㤗），登记为未来应用候选；NiuTrans 同读「泰」（side_anchored）；youngzs 同读「泰」（side_anchored）；Banny-Gao（旁证） 同读「泰」（side_anchored） |
| 49483 | 卷二 | 萌之初虑之深防之预也小雪后 | kept 保留 | 保留「防」，四库两家同读防、无已定位异读；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 50778 | 卷二 | 谓也观天之杳防岂复有度乎乃 | deferred 待补见证 | 四库两家同读「㝠」（冥），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 51212 | 卷二 | 也故申子辰气防同者此也已酉 | deferred 待补见证 | 四库两家同读「㑹」（會），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 51503 | 卷二 | 今厯之便于筹防也世谓子午卯 | deferred 待补见证 | 四库两家同读「䇿」（策），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 52780 | 卷二 | 隂纳甲及出入防合
 陈抟曰 | deferred 待补见证 | 四库两家同读「㑹」（會），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 53507 | 卷二 | 之一而与日交防日之明全不能 | deferred 待补见证 | 四库两家同读「㑹」（會），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 54725 | 卷二 | 化生成无方有防防矣丹经歴术 | deferred 待补见证 | 四库两家同读「㡬」（幾），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载；与紧邻位点 54726「㣲」构成「幾微」连读（快照作「有防防矣」），两处分别登记、互不冒认 |
| 54726 | 卷二 | 生成无方有防防矣丹经歴术纳 | deferred 待补见证 | 四库两家同读「㣲」（微），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载；与紧邻位点 54725「㡬」构成「幾微」连读（快照作「有防防矣」），两处分别登记、互不冒认 |
| 57178 | 卷二 | 为父母则知亲防名利有无之类 | deferred 待补见证 | 四库两家同读「䕃」（蔭），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 58012 | 卷二 | 月见贵必受福防刑冲破害决主 | deferred 待补见证 | 四库两家同读「䕃」（蔭），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 59396 | 卷二 | 生年时得气浅防四柱得煞深迎 | deferred 待补见证 | 四库两家同读「㴱」（深），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 59988 | 卷二 | 可遇元辰之厄防壶中子云元辰 | deferred 待补见证 | 四库两家同读「㑹」（會），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 60358 | 卷二 | 之气反战故有防恶而终
 又 | deferred 待补见证 | 四库两家同读「㐫」（凶），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 69106 | 卷二 | 葢巳与申合奏防賔歌林钟舞大 | deferred 待补见证 | 四库两家同读「㽔」（蕤），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 69118 | 卷二 | 大夏以祀山川防賔午林钟未葢 | deferred 待补见证 | 四库两家同读「㽔」（蕤），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 69154 | 卷二 | 三才之体其理防哉广録云寅午 | deferred 待补见证 | 四库两家同读「㣲」（微），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 70165 | 卷二 | 合吉神则吉合防神则凶玉井云 | confirmed 定案 | 应改读「凶」（四库字形 㓙），登记为未来应用候选；NiuTrans 同读「凶」（side_anchored）；youngzs 同读「凶」（side_anchored）；Banny-Gao（旁证） 同读「凶」（side_anchored） |
| 74860 | 卷二 | 

 三命通防卷二
<子部 | deferred 待补见证 | 四库两家同读「㑹」（會），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载；位点为卷端页眉书名「三命通㑹卷二」之「㑹」字；现代各家页眉形态不同、位点未载，候选只据四库两家登记 |
| 74897 | 卷三 | 书
 三命通防卷三
 明  | deferred 待补见证 | 四库两家同读「㑹」（會），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载；位点为卷端页眉书名「三命通㑹卷三」之「㑹」字；现代各家页眉形态不同、位点未载，候选只据四库两家登记 |
| 77782 | 卷三 | 恐但以岁中吉防言之
 寅午 | deferred 待补见证 | 四库两家同读「㐫」（凶），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 89147 | 卷三 | 奔走利名塲须防祖业消亡尽妻 | kept 保留 | 保留「防」，四库两家同读防、无已定位异读；NiuTrans 同读「防」（side_anchored）；youngzs 同读「防」（side_anchored）；Banny-Gao（旁证） 同读「防」（side_anchored） |
| 89962 | 卷三 | 格又看日辰吉防何如増减断
 | deferred 待补见证 | 四库两家同读「㓙」（凶），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 90054 | 卷三 | 祸等事为日辰防煞者必然为贵 | deferred 待补见证 | 四库两家同读「㐫」（凶），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 90298 | 卷三 | 名刀鎗刼煞主防暴恶死干音尅 | deferred 待补见证 | 四库两家同读「㓙」（凶），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 91106 | 卷三 | 度日更引日家防煞衣食艰难亡 | deferred 待补见证 | 四库两家同读「㓙」（凶），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 91200 | 卷三 | 寅壬申独者主防
 有刼头见 | deferred 待补见证 | 四库两家同读「㓙」（凶），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 92276 | 卷三 | 有甲字之类主防若日干在时上 | deferred 待补见证 | 四库两家同读「㓙」（凶），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 95187 | 卷三 | 红煞日凡百皆防出行尤忌】
 | deferred 待补见证 | 四库两家同读「㐫」（凶），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 95694 | 卷三 | 于冲破未必皆防此之谓也论灾 | confirmed 定案 | 应改读「凶」（四库字形 㓙），登记为未来应用候选；NiuTrans 同读「凶」（side_anchored）；youngzs 同读「凶」（side_anchored）；Banny-Gao（旁证） 同读「凶」（side_anchored） |
| 95838 | 卷三 | 光横死在水火防焚溺金木杖刃 | kept 保留 | 保留「防」，四库两家同读防、无已定位异读；NiuTrans 同读「防」（full_flank）；youngzs 同读「防」（full_flank）；Banny-Gao（旁证） 同读「防」（full_flank） |
| 97460 | 卷三 | 云龙蛇混杂常防妇女忧危猪犬 | kept 保留 | 保留「防」，四库两家同读防、无已定位异读；NiuTrans 同读「防」（full_flank）；youngzs 同读「防」（full_flank）；Banny-Gao（旁证） 同读「防」（full_flank） |
| 98864 | 卷三 | 遇吉因酒成家防则破家或醉死 | deferred 待补见证 | 四库两家同读「㓙」（凶），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 99316 | 卷三 | 顚坠金神羊刃防同位要知自缢 | kept 保留 | 保留「防」，四库两家同读防、无已定位异读；NiuTrans 同读「防」（side_anchored）；youngzs 同读「防」（side_anchored）；Banny-Gao（旁证） 同读「防」（side_anchored） |
| 99518 | 卷三 | 火气生旺处当防火灾诗曰寅午 | kept 保留 | 保留「防」，四库两家同读防、无已定位异读；NiuTrans 同读「防」（full_flank）；youngzs 同读「防」（full_flank）；Banny-Gao（旁证） 同读「防」（full_flank） |
| 101642 | 卷三 | 逢吉神多则吉防煞多则防】
 | deferred 待补见证 | 四库两家同读「㐫」（凶），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 101646 | 卷三 | 则吉防煞多则防】
 煞中包 | deferred 待补见证 | 四库两家同读「㐫」（凶），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 102419 | 卷三 | 法盗资财三重防狠人顽恶生不 | deferred 待补见证 | 四库两家同读「㓙」（凶），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 102606 | 卷三 | 窃气难凭贵煞防贵善又无功
 | deferred 待补见证 | 四库两家同读「㓙」（凶），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 102636 | 卷三 | 起吞啖亡刼为防故一生修读竟 | deferred 待补见证 | 四库两家同读「㓙」（凶），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 103115 | 卷三 | 弱刼煞亡神最防恶聚众攻身大 | deferred 待补见证 | 四库两家同读「㓙」（凶），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 103193 | 卷三 | 年罗纹不战也防恶生死荣枯在 | deferred 待补见证 | 四库两家同读「㓙」（凶），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 103230 | 卷三 | 死】
 凡是防神莫尅年尅年 | deferred 待补见证 | 四库两家同读「㓙」（凶），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 103259 | 卷三 | 煞变权
 【防神恶煞宜尅出 | deferred 待补见证 | 四库两家同读「㓙」（凶），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 103347 | 卷三 | 大贵】
 最防卯酉见寅申卯 | deferred 待补见证 | 四库两家同读「㓙」（凶），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 103886 | 卷三 | 冲煞神遇合为防煞禄马刑冲吉 | deferred 待补见证 | 四库两家同读「㓙」（凶），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 103894 | 卷三 | 禄马刑冲吉反防
 【如甲子 | deferred 待补见证 | 四库两家同读「㓙」（凶），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 104631 | 卷三 | 也还观反合吉防祸福要详明
 | deferred 待补见证 | 四库两家同读「㓙」（凶），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 104742 | 卷三 | 支逢冲故主大防又丁己壬申天 | deferred 待补见证 | 四库两家同读「㓙」（凶），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 105343 | 卷三 | 名为岁煞反招防暴亡水火离乡 | deferred 待补见证 | 四库两家同读「㐫」（凶），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 106001 | 卷三 | 己卯四十四岁防死】
 白虎 | deferred 待补见证 | 四库两家同读「㐫」（凶），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 106190 | 卷三 | 阴错阳差煞最防日时年月莫相 | deferred 待补见证 | 四库两家同读「㓙」（凶），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 106649 | 卷三 | 皆分散聚煞攒防命不存
 【 | deferred 待补见证 | 四库两家同读「㓙」（凶），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 106696 | 卷三 | 子甲午谓之攒防聚煞贫贱早夭 | deferred 待补见证 | 四库两家同读「㓙」（凶），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 106767 | 卷三 | 神最喜落空亡防煞空亡大吉昌 | deferred 待补见证 | 四库两家同读「㓙」（凶），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 107030 | 卷三 | 遇羊刃破碎则防秀而不实】
 | deferred 待补见证 | 四库两家同读「㐫」（凶），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 107452 | 卷三 | 难定浮生吉与防【人命辰戌丑 | deferred 待补见证 | 四库两家同读「㐫」（凶），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 108035 | 卷三 | 来飞刃并三刑防狠强梁不可亲 | deferred 待补见证 | 四库两家同读「㓙」（凶），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 108214 | 卷三 | 鬼强我弱便为防鬼多只利术医 | deferred 待补见证 | 四库两家同读「㓙」（凶），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 108307 | 卷三 | 怕鬼多兼煞众防多吉少便为愆 | deferred 待补见证 | 四库两家同读「㐫」（凶），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 108322 | 卷三 | 鬼强不可例言防鬼伏他家受制 | deferred 待补见证 | 四库两家同读「㓙」（凶），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 108546 | 卷三 | 旺家徒四壁免防灾
 【凡上 | deferred 待补见证 | 四库两家同读「㓙」（凶），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 108642 | 卷三 | 亡能觉悟吉人防变作祯祥
  | deferred 待补见证 | 四库两家同读「㐫」（凶），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 108979 | 卷三 | 不停鱼腹有灾防溺水鼠牙莫近 | kept 保留 | 保留「防」，四库两家同读防、无已定位异读；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 110147 | 卷三 | 合来神煞便为防神煞如何一様 | deferred 待补见证 | 四库两家同读「㓙」（凶），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 110529 | 卷三 | 纵饶富贵也招防
 【如己未 | deferred 待补见证 | 四库两家同读「㐫」（凶），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 110634 | 卷三 | 人言死絶最为防起死为生福反 | deferred 待补见证 | 四库两家同读「㐫」（凶），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 110844 | 卷三 | 

 三命通防卷三
<子部 | deferred 待补见证 | 四库两家同读「㑹」（會），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载；位点为卷端页眉书名「三命通㑹卷三」之「㑹」字；现代各家页眉形态不同、位点未载，候选只据四库两家登记 |

### 9.4 定案要点与 deferred 缺口形态

- **confirmed 3**：49278 㤗（泰）——「卦氣正月為㤗」，现代
  三家（含旁证）同读「泰」；70165 㓙、95694 㓙——现代两家
  （及旁证）同读「凶」。
- **kept 15**：四库两家同读「防」且无已定位异读——含固定
  语汇隄防（12695/31469）、边防（22196）与论述/诗句中的
  实义「防」（17070「夏生防吉中有凶」、99518「当防火灾」
  等）；其中 10 处现代谱系同读防、5 处现代文句未载（保留
  不主张文本有误，依 §2 不对称标准只须四库同读、无异读）。
- **parallel 1**：188——四库读「㡬」（幾，「總彚㡬於家有
  其書」），youngzs 本书转录文句在场而该字脱字（作「總
  彚。於家有其書」），与首批 73703 同型，字级分歧、并列
  不裁。
- **deferred 67**：缺口形态单一——四库读法全部在案，现代
  三家于该位点文句全部未载（节选/重编所致），缺第二个
  独立见证方。其中凶字异体 41 处（㓙 27 + 㐫 14——快照
  「防神/防煞/主防」等处四库作㓙/㐫）、㑹 9 处（含卷端
  页眉书名「三命通㑹」4 处）、餘为幾微连读（54725/54726）
  等单字。升级路径同 §5（补独立转录谱系或四库影印原叶
  定位）。

### 9.5 累计进度与剩余分册计划（更新）

- 累计处置进度：**disposed 33/769**（confirmed 12、kept
  19、parallel 2）；deferred 96（节内 29 + 本册 67）；
  pending 640。
- 全卷累计：

| 卷 | 盘点 | confirmed | kept | parallel | deferred | pending |
|---|---|---|---|---|---|---|
| 卷首 | 1 | 0 | 0 | 1 | 0 | 0 |
| 卷一 | 10 | 0 | 8 | 0 | 2 | 0 |
| 卷二 | 34 | 2 | 2 | 1 | 29 | 0 |
| 卷三 | 50 | 1 | 6 | 0 | 43 | 0 |
| 卷四 | 118 | 0 | 0 | 0 | 0 | 118 |
| 卷五 | 89 | 5 | 2 | 0 | 15 | 67 |
| 卷六 | 142 | 4 | 1 | 0 | 7 | 130 |
| 卷七 | 75 | 0 | 0 | 0 | 0 | 75 |
| 卷八 | 61 | 0 | 0 | 0 | 0 | 61 |
| 卷九 | 94 | 0 | 0 | 0 | 0 | 94 |
| 卷十 | 26 | 0 | 0 | 0 | 0 | 26 |
| 卷十一 | 45 | 0 | 0 | 0 | 0 | 45 |
| 卷十二 | 24 | 0 | 0 | 0 | 0 | 24 |
| 合计 | 769 | 12 | 19 | 2 | 96 | 640 |

- 剩余分册（按卷序）：卷四 118、卷五 67、卷六 130、卷七
  75、卷八 61、卷九 94、卷十 26、卷十一 45、卷十二 24；
  RD-12 的 7 处节外「防」位点（卷五 seq 361/385、卷七
  612/616、卷十 824、卷十一 873/933）在各册中只标记、
  处置随 P3。本册同样只登记处置结论、零文本改动，
  `canonical_ready` 保持 false。
