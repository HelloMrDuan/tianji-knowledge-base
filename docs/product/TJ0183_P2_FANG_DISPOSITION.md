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

## 10. 第三分册（卷四节外 118 处，E0306）

### 10.1 范围与方法补记

- 范围：卷四节外 pending **118 处**整卷（一卷一册）。本册
  范围内**无 RD-12 位点**（7 处节外 RD-12「防」位点分布于
  卷五/卷七/卷十/卷十一，仍只标记、处置随 P3）。
- 捕获式定位沿第二分册。四库两家 **117/118 处定位且读法
  逐处一致**，其余三处形态各异：130766、131317 两处
  kanripo 原文在位点前有段落标记（）¶　（）介入、侧翼全锚
  与脱字定位均失败，改以句段锚定（segment_anchored：左
  8 字句段锚定、右句段近邻复核）定位，与 mikkokotila
  同读；126098 处 kanripo KR3g0042_004 全文无此段（侧翼、
  脱字、句段与关键词检索均无），四库谱系仅 mikkokotila
  一家定位读「㤗」，候选只据一家登记、归 deferred。
- **见证口径澄清（自本册起适用）**：现代谱系的位点见证只认
  其《三命通会》转录子集。youngzs 语料兼含《三命通会》与
  《五行精纪》两书：卷四多节系大段引录《五行精纪》，其
  《三命通会》转录于卷四仅有 056/057/058 三节；本册
  youngzs 全语料命中 27 处中，24 处实为其《五行精纪》
  转录对源文本的命中——该读法是源文本的读法，不构成对
  三命通会文本的位点见证（146688 处两书读法实异：四库
  三命读「䄂」、源文本读「福」，足证引文位点的三命读法
  不能以源文本替代）。此 24 处逐字登记为
  `attested_parallel_source`（平行源文本旁证）：证据、定位
  文档与引文全量在案，但不计现代方、亦不作谱系分歧；其
  中 22 处源文本与四库同读、本可据全语料口径定案，本册
  一律降为 deferred，待三命文本自身的第二见证方补齐后
  逐处升级。首批 17070 处既有条目的 youngzs 证据同为
  《五行精纪》文档命中（kept 类、四库同读防即足、非承重），
  按 append-only 原样保留、不回溯改写；Banny-Gao 的引文
  子集限制（只取其《三命通会》转录）自首批即然，与本
  澄清同向。
- 现代谱系本册实定位：NiuTrans 3 处、youngzs 三命子集
  3 处（与 NiuTrans 在 114728/122205/124647 三处重合）、
  Banny-Gao 旁证 2 处；余皆文句未载（youngzs 三命转录
  未覆盖本卷诸节、NiuTrans 本卷仅定位三节）。

### 10.2 本册计数

| 卷 | 盘点 | confirmed | kept | parallel | deferred | pending |
|---|---|---|---|---|---|---|
| 卷四 | 118 | 2 | 4 | 0 | 112 | 0 |
| 本册合计 | 118 | 2 | 4 | 0 | 112 | 0 |

### 10.3 本册处置（118 处逐处）

| S0 位点 | 卷 | 语境（S3 ±6） | 处置分类 | 结论与见证要点 |
|---|---|---|---|---|
| 110881 | 卷四 | 书
 三命通防卷四
 明  | deferred 待补见证 | 四库两家同读「㑹」（會），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载；位点为卷端页眉书名「三命通㑹卷四」之「㑹」字；现代各家页眉形态不同、位点未载，候选只据四库两家登记 |
| 111515 | 卷四 | 天赦】有吉为防防为吉更防天 | deferred 待补见证 | 四库两家同读「㐫」（凶），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 111516 | 卷四 | 赦】有吉为防防为吉更防天时 | deferred 待补见证 | 四库两家同读「㐫」（凶），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 111520 | 卷四 | 为防防为吉更防天时仔细详
 | deferred 待补见证 | 四库两家同读「㸔」（看），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 111928 | 卷四 | 壬水者轻】更防天时并合局吉 | deferred 待补见证 | 四库两家同读「㸔」（看），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 111935 | 卷四 | 天时并合局吉防祸福细推详
 | deferred 待补见证 | 四库两家同读「㐫」（凶），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 113076 | 卷四 | 时贵】人生吉防如何定月气时 | deferred 待补见证 | 四库两家同读「㓙」（凶），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 114728 | 卷四 | 少金盛火微皆防暴之軰【六庚 | confirmed 定案 | 应改读「凶」（四库字形 㓙），登记为未来应用候选；NiuTrans 同读「凶」（side_anchored）；youngzs 同读「凶」（side_anchored）；Banny-Gao（旁证） 未载 |
| 114955 | 卷四 | 【子上木败火防庚死谓金沉水 | deferred 待补见证 | 四库两家同读「㓕」（滅），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 114984 | 卷四 | 丁火则吉】须防天时分贵贱柱 | deferred 待补见证 | 四库两家同读「㸔」（看），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 115413 | 卷四 | 死囚分月气更防有用细推详
 | deferred 待补见证 | 四库两家同读「㸔」（看），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 116070 | 卷四 | 辰中建禄却卑防【壬辰魁罡柱 | deferred 待补见证 | 四库两家同读「㣲」（微），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 116107 | 卷四 | 生于功名中歇防若财官生旺别 | deferred 待补见证 | 四库两家同读「㓕」（滅），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 120129 | 卷四 | 生作丁火用霜防节皆是戊
  | deferred 待补见证 | 四库两家同读「䧏」（降），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 122205 | 卷四 | 谷雨之后生者防水无㐫盖土司 | confirmed 定案 | 应改读「微」（四库字形 㣲），登记为未来应用候选；NiuTrans 同读「微」（side_anchored）；youngzs 同读「微」（side_anchored）；Banny-Gao（旁证） 同读「微」（side_anchored） |
| 124647 | 卷四 | 际见土则有隄防昼则富贵夜则 | kept 保留 | 保留「防」，四库两家同读防、无已定位异读；NiuTrans 同读「防」（full_flank）；youngzs 同读「防」（full_flank）；Banny-Gao（旁证） 同读「防」（full_flank） |
| 125219 | 卷四 | 冀雍人頼以隄防而无泛溢之患 | kept 保留 | 保留「防」，四库两家同读防、无已定位异读；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 125553 | 卷四 | 富贵坎地却为防是也】
 甲 | deferred 待补见证 | 四库两家同读「㐫」（凶），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 126050 | 卷四 | 内无破只以富防若金火互相攻 | deferred 待补见证 | 四库两家同读「㫁」（斷），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 126098 | 卷四 | 趋干又地天交防 巳亥甲戊乙 | deferred 待补见证 | 四库谱系仅 mikkokotila 一家读「㤗」（泰），kanripo 全文无此段，现代独立见证亦未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载；四库谱系仅 mikkokotila 一家定位：kanripo KR3g0042_004 全文无此段（侧翼全锚、脱字与句段检索均无），候选读法只据一家登记；现代三家亦未载，缺口为四库谱系内部第二文本与现代见证双方 |
| 126517 | 卷四 | 莫要猜疑作混防干上再逢庚字 | deferred 待补见证 | 四库两家同读「㸔」（看），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 127443 | 卷四 | 丁火戊己土轻防得遇东南之地 | deferred 待补见证 | 四库两家同读「㣲」（微），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 128034 | 卷四 | 中之火及木相防皆壊格局宜行 | deferred 待补见证 | 四库两家同读「㑹」（會），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 128181 | 卷四 | 福怕逢水金及防木入墓若身用 | deferred 待补见证 | 四库两家同读「㑹」（會），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 128268 | 卷四 | 柱原有一二字防成木局全不吉 | deferred 待补见证 | 四库两家同读「㑹」（會），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 128386 | 卷四 | 牛宜见嫌南火防水扶持入庙廊 | deferred 待补见证 | 四库两家同读「㣲」（微），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 128544 | 卷四 | 又吉若入火木防旺之地用神虽 | deferred 待补见证 | 四库两家同读「㑹」（會），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 128581 | 卷四 | 庚辛带水利名防不论何月时辰 | deferred 待补见证 | 四库两家同读「㸔」（看），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 128842 | 卷四 | 引戌从作大贵防若乙酉则无前 | deferred 待补见证 | 四库两家同读「㸔」（看），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 129335 | 卷四 | 若行财旺地反防为吉佐王侯  | deferred 待补见证 | 四库两家同读「㐫」（凶），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 129522 | 卷四 | 纲伐木壤印则防生三月本是伤 | deferred 待补见证 | 四库两家同读「㓙」（凶），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 129537 | 卷四 | 宜金水之用如防申子全主发达 | deferred 待补见证 | 四库两家同读「㑹」（會），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 129951 | 卷四 | 土或支遇子辰防水行南北皆吉 | deferred 待补见证 | 四库两家同读「㑹」（會），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 130138 | 卷四 | 若从化作上命防如丙生此际遇 | deferred 待补见证 | 四库两家同读「㸔」（看），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 130155 | 卷四 | 相连或申子辰防柱有辛则化有 | deferred 待补见证 | 四库两家同读「㑹」（會），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 130285 | 卷四 | 吉破用主弱则防】
 丙日秋 | deferred 待补见证 | 四库两家同读「㓙」（凶），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 130499 | 卷四 | 旺皆不作上命防】
 丙临申 | deferred 待补见证 | 四库两家同读「㸔」（看），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 130543 | 卷四 | 遇壬辰时申辰防煞春夏火旺相 | deferred 待补见证 | 四库两家同读「㑹」（會），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 130552 | 卷四 | 夏火旺相不以防论秋冬水旺相 | deferred 待补见证 | 四库两家同读「㐫」（凶），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 130596 | 卷四 | 主休败之地吉防宜细详之】
 | deferred 待补见证 | 四库两家同读「㓙」（凶），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 130766 | 卷四 | 飞失局失垣则防 如丙寅甲午 | deferred 待补见证 | 四库两家同读「㐫」（凶），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载；kanripo 原文该位点前有段落标记介入、侧翼全锚失败，经句段锚定（segment_anchored）定位同读「㐫」；现代三家未载 |
| 131021 | 卷四 | 申酉地吉中主防】
 丁壬化 | deferred 待补见证 | 四库两家同读「㓙」（凶），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 131168 | 卷四 | 月寅时不作化防九月化煞化木 | deferred 待补见证 | 四库两家同读「㸔」（看），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 131317 | 卷四 | 有土神子申运防 如髙文荐都 | deferred 待补见证 | 四库两家同读「㓙」（凶），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载；kanripo 原文该位点前有段落标记介入、侧翼全锚失败，经句段锚定（segment_anchored）定位同读「㓙」；现代三家未载 |
| 131600 | 卷四 | 方轻则非重则防】
 丁日蛇 | deferred 待补见证 | 四库两家同读「㐫」（凶），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 131710 | 卷四 | 申俱行戊子运防】
 丁生卯 | deferred 待补见证 | 四库两家同读「㓙」（凶），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 131810 | 卷四 | 星若出干头上防水相征祸始侵 | deferred 待补见证 | 四库两家同读「㑹」（會），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 131984 | 卷四 | 原有煞刃者尤防如顺行不遇财 | deferred 待补见证 | 四库两家同读「㐫」（凶），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 132114 | 卷四 | 寅停节子寅运防祸九月不遇甲 | kept 保留 | 保留「防」，四库两家同读防、无已定位异读；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 132153 | 卷四 | 忌寅午如流年防煞防伤基之地 | deferred 待补见证 | 四库两家同读「㑹」（會），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 132155 | 卷四 | 午如流年防煞防伤基之地祸福 | deferred 待补见证 | 四库两家同读「㑹」（會），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 132289 | 卷四 | 无印行北方亦防生二月正官要 | deferred 待补见证 | 四库两家同读「㓙」（凶），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 132712 | 卷四 | 又生扶土过宜防水滋泽其间俱 | deferred 待补见证 | 四库两家同读「㣲」（微），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 132793 | 卷四 | 浊者不利俱宜防水不为坏印如 | deferred 待补见证 | 四库两家同读「㣲」（微），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 133251 | 卷四 | 壬癸庚辛去玷防用为财名如无 | deferred 待补见证 | 四库两家同读「㑹」（會），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 135169 | 卷四 | 丑辰午戌运专防岁防碍此运有 | deferred 待补见证 | 四库两家同读「㸔」（看），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 135171 | 卷四 | 午戌运专防岁防碍此运有咎非 | deferred 待补见证 | 四库两家同读「㑹」（會），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 135693 | 卷四 | 辰遇丙或丁不防火木及刼则吉 | deferred 待补见证 | 四库两家同读「㑹」（會），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 135873 | 卷四 | 营利之徒清者防名难作贵论若 | deferred 待补见证 | 四库两家同读「㣲」（微），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 136561 | 卷四 | 旺运生祸有官防木成局行火木 | deferred 待补见证 | 四库两家同读「㑹」（會），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 137350 | 卷四 | 之用吉者甚吉防者甚防若运行 | deferred 待补见证 | 四库两家同读「㐫」（凶），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 137353 | 卷四 | 者甚吉防者甚防若运行击触煞 | deferred 待补见证 | 四库两家同读「㓙」（凶），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 137362 | 卷四 | 行击触煞起及防冲刑之地其防 | deferred 待补见证 | 四库两家同读「㑹」（會），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 137368 | 卷四 | 防冲刑之地其防不可当多不善 | deferred 待补见证 | 四库两家同读「㓙」（凶），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 137506 | 卷四 | 庚子日乃中堂防申辰冲寅午戌 | deferred 待补见证 | 四库两家同读「㑹」（會），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 137925 | 卷四 | 寒月兔猪羊局防财成富贵详无 | deferred 待补见证 | 四库两家同读「㑹」（會），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 138086 | 卷四 | 原刼多行财则防原财遇比行亥 | deferred 待补见证 | 四库两家同读「㓙」（凶），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 138099 | 卷四 | 戌运可入酉亦防用丙忌壬亥怕 | deferred 待补见证 | 四库两家同读「㓙」（凶），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 138170 | 卷四 | 官煞秋冬南地防木火畏逢金水 | deferred 待补见证 | 四库两家同读「㓙」（凶），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 138303 | 卷四 | 致之乡用此如防】
 辛日东 | deferred 待补见证 | 四库两家同读「㫁」（斷），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 138584 | 卷四 |  壬癸春生喜防财干支得土亦 | deferred 待补见证 | 四库两家同读「㑹」（會），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 138605 | 卷四 | 利木遇金多成防荄
 【壬癸 | deferred 待补见证 | 四库两家同读「㫁」（斷），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 139014 | 卷四 | 贵忌庚申辛酉防金折木若浮金 | deferred 待补见证 | 四库两家同读「㑹」（會），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 139249 | 卷四 | 六月伤官一格防全者贵富亦宜 | deferred 待补见证 | 四库两家同读「㑹」（會），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 139282 | 卷四 | 贵淆者次壬子防伤为合亦可拟 | deferred 待补见证 | 四库两家同读「㑹」（會），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 139427 | 卷四 | 吉遇丁多反覆防甲宜木火忌徃 | deferred 待补见证 | 四库两家同读「㑹」（會），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 139662 | 卷四 | 交争及刑冲者防 癸日七八月 | deferred 待补见证 | 四库两家同读「㓙」（凶），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 139690 | 卷四 | 吉忌寅丙冲提防火之地见火返 | deferred 待补见证 | 四库两家同读「㑹」（會），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 139818 | 卷四 | 持阴阳混杂则防此両干七八月 | deferred 待补见证 | 四库两家同读「㓙」（凶），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 140527 | 卷四 | 妨大抵吉中生防甚则危】
  | deferred 待补见证 | 四库两家同读「㐫」（凶），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 140820 | 卷四 | 煞多尤利风云防富贵愁逢丙甲 | deferred 待补见证 | 四库两家同读「㑹」（會），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 141572 | 卷四 | 寅甲富贵功名防可成
 【癸 | deferred 待补见证 | 四库两家同读「㫁」（斷），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 141792 | 卷四 | 利客若逢寅甲防青春
 【癸 | deferred 待补见证 | 四库两家同读「䘮」（喪），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 141852 | 卷四 | 印变改忽然其防不测】
 癸 | deferred 待补见证 | 四库两家同读「㓙」（凶），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 141879 | 卷四 | 运只嫌申午地防青枝上利名期 | deferred 待补见证 | 四库两家同读「㑹」（會），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 142236 | 卷四 | 转祸为福又甲防丙子丙午旺水 | deferred 待补见证 | 四库两家同读「㑹」（會），现代独立见证未齐，不裁；NiuTrans 未载；youngzs《五行精纪》平行源文本同读「会」（不计现代方）；Banny-Gao（旁证） 未载 |
| 142438 | 卷四 | 纵逢火盛不为防若见甲来加子 | deferred 待补见证 | 四库两家同读「㓙」（凶），现代独立见证未齐，不裁；NiuTrans 未载；youngzs《五行精纪》平行源文本同读「凶」（不计现代方）；Banny-Gao（旁证） 未载 |
| 142801 | 卷四 | 移乡井事多歇防】
 夭横无 | deferred 待补见证 | 四库两家同读「㓕」（滅），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 142986 | 卷四 | 位子母俱旺福防之庆己酉以摄 | deferred 待补见证 | 四库两家同读「㑹」（會），现代独立见证未齐，不裁；NiuTrans 未载；youngzs《五行精纪》平行源文本同读「会」（不计现代方）；Banny-Gao（旁证） 未载 |
| 143134 | 卷四 | 如无救助定成防若値五行多水 | deferred 待补见证 | 四库两家同读「㐫」（凶），现代独立见证未齐，不裁；NiuTrans 未载；youngzs《五行精纪》平行源文本同读「凶」（不计现代方）；Banny-Gao（旁证） 未载 |
| 143817 | 卷四 | 竭矣】
 烟防灰飞【火木临 | deferred 待补见证 | 四库两家同读「㓕」（滅），现代独立见证未齐，不裁；NiuTrans 未载；youngzs《五行精纪》平行源文本同读「灭」（不计现代方）；Banny-Gao（旁证） 未载 |
| 143983 | 卷四 | 午头带戊丙人防以为食神名誉 | deferred 待补见证 | 四库两家同读「㑹」（會），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 144186 | 卷四 | 于土数木神加防至三台
 【 | deferred 待补见证 | 四库两家同读「䕶」（護），现代独立见证未齐，不裁；NiuTrans 未载；youngzs《五行精纪》平行源文本同读「护」（不计现代方）；Banny-Gao（旁证） 未载 |
| 144785 | 卷四 | 有气五行要不防若有金无水又 | deferred 待补见证 | 四库两家同读「㫁」（斷），现代独立见证未齐，不裁；NiuTrans 未载；youngzs《五行精纪》平行源文本同读「断」（不计现代方）；Banny-Gao（旁证） 未载 |
| 144808 | 卷四 | 】
 相为庆防【土壮合水生 | deferred 待补见证 | 四库两家同读「㑹」（會），现代独立见证未齐，不裁；NiuTrans 未载；youngzs《五行精纪》平行源文本同读「会」（不计现代方）；Banny-Gao（旁证） 未载 |
| 145046 | 卷四 | 局纵能财禄亦防余
 【逢甲 | deferred 待补见证 | 四库两家同读「㣲」（微），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 145145 | 卷四 | 巳用功乙庚相防禄髙封炎上火 | deferred 待补见证 | 四库两家同读「㑹」（會），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 145448 | 卷四 | 必见其形而黙防之可也若只见 | deferred 待补见证 | 四库两家同读「㑹」（會），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 145986 | 卷四 | 马之说要在穷防曲尽其理方知 | deferred 待补见证 | 四库两家同读「䆒」（究），现代独立见证未齐，不裁；NiuTrans 未载；youngzs《五行精纪》平行源文本同读「究」（不计现代方）；Banny-Gao（旁证） 未载 |
| 146025 | 卷四 | 系丁壬天魁合防功曹盛名达朝 | deferred 待补见证 | 四库两家同读「㑹」（會），现代独立见证未齐，不裁；NiuTrans 未载；youngzs《五行精纪》平行源文本同读「会」（不计现代方）；Banny-Gao（旁证） 未载 |
| 146205 | 卷四 | 快哉】
 先防后吉
 辛人 | deferred 待补见证 | 四库两家同读「㐫」（凶），现代独立见证未齐，不裁；NiuTrans 未载；youngzs《五行精纪》平行源文本同读「凶」（不计现代方）；Banny-Gao（旁证） 未载 |
| 146355 | 卷四 | 难显达得木卫防犹且庻防稍若 | deferred 待补见证 | 四库两家同读「䕶」（護），现代独立见证未齐，不裁；NiuTrans 未载；youngzs《五行精纪》平行源文本同读「护」（不计现代方）；Banny-Gao（旁证） 未载 |
| 146359 | 卷四 | 木卫防犹且庻防稍若阙此终当 | deferred 待补见证 | 四库两家同读「㡬」（幾），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 146389 | 卷四 | 自然光丙辛交防势堂堂太冲还 | deferred 待补见证 | 四库两家同读「㑹」（會），现代独立见证未齐，不裁；NiuTrans 未载；youngzs《五行精纪》平行源文本同读「会」（不计现代方）；Banny-Gao（旁证） 未载 |
| 146399 | 卷四 | 太冲还共登明防必是金门紫绶 | deferred 待补见证 | 四库两家同读「㑹」（會），现代独立见证未齐，不裁；NiuTrans 未载；youngzs《五行精纪》平行源文本同读「会」（不计现代方）；Banny-Gao（旁证） 未载 |
| 146688 | 卷四 | 更加土多壬人防禄自然显著岂 | deferred 待补见证 | 四库两家同读「䄂」（袖），现代独立见证未齐，不裁；NiuTrans 未载；youngzs《五行精纪》平行源文本异读「福」（不计现代方）；Banny-Gao（旁证） 未载；youngzs《五行精纪》平行源文本读「福」（福禄），属源文本旁证、非三命通会转录见证，不计现代方、亦不作谱系分歧；四库三命文本读「䄂」，两读并录在案，待三命通会现代全本转录或四库影印原叶补证后另议 |
| 146704 | 卷四 | 享快】
 反防成庆
 六壬 | deferred 待补见证 | 四库两家同读「㐫」（凶），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 147029 | 卷四 |  【亥子乃水防之地癸人得之 | deferred 待补见证 | 四库两家同读「㑹」（會），现代独立见证未齐，不裁；NiuTrans 未载；youngzs《五行精纪》平行源文本同读「会」（不计现代方）；Banny-Gao（旁证） 未载 |
| 147232 | 卷四 | 中逢生最为喜防更得西北带金 | deferred 待补见证 | 四库两家同读「㑹」（會），现代独立见证未齐，不裁；NiuTrans 未载；youngzs《五行精纪》平行源文本同读「会」（不计现代方）；Banny-Gao（旁证） 未载 |
| 147530 | 卷四 | 火盛则灰飞烟防得氷可制火局 | deferred 待补见证 | 四库两家同读「㓕」（滅），现代独立见证未齐，不裁；NiuTrans 未载；youngzs《五行精纪》平行源文本同读「灭」（不计现代方）；Banny-Gao（旁证） 未载 |
| 147720 | 卷四 | 火败地本自衰防逢水则金不能 | deferred 待补见证 | 四库两家同读「㣲」（微），现代独立见证未齐，不裁；NiuTrans 未载；youngzs《五行精纪》平行源文本同读「微」（不计现代方）；Banny-Gao（旁证） 未载 |
| 147770 | 卷四 | 灾
 众火须防水在寅平生迍 | kept 保留 | 保留「防」，四库两家同读防、无已定位异读；NiuTrans 未载；youngzs《五行精纪》平行源文本同读「防」（不计现代方）；Banny-Gao（旁证） 未载 |
| 148363 | 卷四 | 本利得火相逢防害至更无火木 | deferred 待补见证 | 四库两家同读「㐫」（凶），现代独立见证未齐，不裁；NiuTrans 未载；youngzs《五行精纪》平行源文本同读「凶」（不计现代方）；Banny-Gao（旁证） 未载 |
| 148434 | 卷四 | 】
 无救成防
 水人切忌 | deferred 待补见证 | 四库两家同读「㐫」（凶），现代独立见证未齐，不裁；NiuTrans 未载；youngzs《五行精纪》平行源文本同读「凶」（不计现代方）；Banny-Gao（旁证） 未载 |
| 148445 | 卷四 | 切忌戊申寅截防根源主祸频局 | deferred 待补见证 | 四库两家同读「㫁」（斷），现代独立见证未齐，不裁；NiuTrans 未载；youngzs《五行精纪》平行源文本同读「断」（不计现代方）；Banny-Gao（旁证） 未载 |
| 148491 | 卷四 | 处见鬼故曰截防根源五行中若 | deferred 待补见证 | 四库两家同读「㫁」（斷），现代独立见证未齐，不裁；NiuTrans 未载；youngzs《五行精纪》平行源文本同读「断」（不计现代方）；Banny-Gao（旁证） 未载 |
| 148590 | 卷四 | 丙戌之类转衰防矣】

 三 | deferred 待补见证 | 四库两家同读「䘮」（喪），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 148599 | 卷四 | 

 三命通防卷四
<子部 | deferred 待补见证 | 四库两家同读「㑹」（會），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载；位点为卷末页眉书名「三命通㑹卷四」之「㑹」字；现代各家页眉形态不同、位点未载，候选只据四库两家登记 |

### 10.4 定案要点与 deferred 缺口形态

- **confirmed 2**：114728 㓙（凶，「少金盛火微皆防暴之
  軰」）与 122205 㣲（微，「谷雨之后生者防」）——均四库
  两家与 NiuTrans、youngzs 三命子集两方同读，Banny-Gao
  旁证于 122205 同读「微」。
- **kept 4**：124647（隄防，现代两方及旁证同读防）、
  125219（隄防）、132114（运防祸）、147770（须防水，
  youngzs 源文本旁证同读防）——四库同读防且无已定位
  异读，依 §2 不对称标准保留。
- **parallel 0**：本册无计方见证间的位点分歧；
  146688 的「䄂/福」异读系三命文本与源文本之间、非谱系
  见证分歧，归 deferred 并两读并录（见该行注记）。
- **deferred 112**：缺口形态为三命通会文本自身的第二个
  独立见证方未齐（现代转录于本卷覆盖极稀）。字形分布：
  㑹 39（含卷端页眉书名 2 处）、凶字异体 33（㓙 17 +
  㐫 16）、㸔 11、㣲 8、㫁 7、㓕 5、䘮 2、䕶 2，餘
  䧏（霜降节）/㤗/䆒/㡬/䄂 各 1。其中 23 处有
  youngzs《五行精纪》平行源文本旁证在案（同读 22、
  146688 异读 1）；126098 处另缺四库谱系内部第二文本。
  升级路径同 §5：补齐现代全本转录（如 Wikisource
  michiboo《三命通会》对应卷次）或四库影印原叶定位后
  逐处升级；有平行源旁证的 22 处同读位点届时可优先
  复核。

### 10.5 累计进度与剩余分册计划（更新）

- 累计处置进度：**disposed 39/769**（confirmed 14、kept
  23、parallel 2）；deferred 208（节内 29 + 第二分册
  67 + 本册 112）；pending 522。
- 全卷累计：

| 卷 | 盘点 | confirmed | kept | parallel | deferred | pending |
|---|---|---|---|---|---|---|
| 卷首 | 1 | 0 | 0 | 1 | 0 | 0 |
| 卷一 | 10 | 0 | 8 | 0 | 2 | 0 |
| 卷二 | 34 | 2 | 2 | 1 | 29 | 0 |
| 卷三 | 50 | 1 | 6 | 0 | 43 | 0 |
| 卷四 | 118 | 2 | 4 | 0 | 112 | 0 |
| 卷五 | 89 | 5 | 2 | 0 | 15 | 67 |
| 卷六 | 142 | 4 | 1 | 0 | 7 | 130 |
| 卷七 | 75 | 0 | 0 | 0 | 0 | 75 |
| 卷八 | 61 | 0 | 0 | 0 | 0 | 61 |
| 卷九 | 94 | 0 | 0 | 0 | 0 | 94 |
| 卷十 | 26 | 0 | 0 | 0 | 0 | 26 |
| 卷十一 | 45 | 0 | 0 | 0 | 0 | 45 |
| 卷十二 | 24 | 0 | 0 | 0 | 0 | 24 |
| 合计 | 769 | 14 | 23 | 2 | 208 | 522 |

- 剩余分册（按卷序）：卷五 67、卷六 130、卷七 75、卷八
  61、卷九 94、卷十 26、卷十一 45、卷十二 24；RD-12 的
  7 处节外「防」位点（卷五 seq 361/385、卷七 612/616、
  卷十 824、卷十一 873/933）在各册中只标记、处置随
  P3。本册同样只登记处置结论、零文本改动，
  `canonical_ready` 保持 false。

## 11. 第四分册（卷五节外 65 处，另 RD-12 两处只标记，E0308）

### 11.1 范围与方法补记

- 范围：卷五节外 pending **67 处**，其中 **65 处**逐处处置
  （一卷一册）；RD-12 seq 361（S0 157779）与 seq 385
  （S0 164133）两处**只标记、不处置**，保持
  pending_later_tranche、处置随 P3（其捕获证据见 §11.3
  末表）。
- 捕获式定位沿第二、第三分册，见证口径含 E0306 子集澄清。
  四库谱系：mikkokotila **65/65 处定位**、kanripo **62/65
  处定位**，定位处两家读法逐处一致。其余三处（149947、
  161345、175574）均系论正官/论正财/论食神三节卷首的
  喜忌 bracket 位点：kanripo 四库本（KR3g0042_005）该
  bracket 以栏式编排分行、清单项目次序与快照底本不同，
  标准捕获（侧翼全锚/脱字/单侧锚/句段锚定）均未定位；
  其中 149947 处四库本对应语作「逢官  財」、161345 处作
  「逄財  官」，位点字本身阙空；175574 处四库本同
  bracket 内有「逢食㸔財」一语而次序不同（宜行財鄉/比肩
  在前），逐字在案、但不作位点见证。三处一律按未定位
  如实登记、候选只据 mikkokotila 一家，归 deferred（与
  第三分册 126098 处四库谱系仅一家定位同型）。
- 现代谱系本册实定位：NiuTrans 10 处、youngzs 三命子集
  14 处、Banny-Gao 旁证 10 处；youngzs 平行源文本旁证
  1 处（154979，见 §11.4）。本册多处位点位于卷五引录的
  赋文段（奥旨篇、幽微赋、相心赋等），同一赋文段亦见于
  卷六诸节，现代两家部分定位文档为其卷六转录中的同文
  位点——侧翼全锚/单侧锚定的同文对应（非关键词散检），
  读法即该赋文读法，与第二分册 214497 处以 NiuTrans
  卷十二《四言独步》平行传文互证同型，在案可核。

### 11.2 本册计数

| 卷 | 盘点 | confirmed | kept | parallel | deferred | pending |
|---|---|---|---|---|---|---|
| 卷五 | 65 | 9 | 6 | 0 | 50 | 0 |
| 本册合计（处置范围） | 65 | 9 | 6 | 0 | 50 | 0 |

（卷五全卷口径另含：已登记节内既处 22 处与本册只标记的
RD-12 两处 pending，见 §11.5 全卷累计表。）

### 11.3 本册处置（65 处逐处）

| S0 位点 | 卷 | 语境（S3 ±6） | 处置分类 | 结论与见证要点 |
|---|---|---|---|---|
| 148636 | 卷五 | 书
 三命通防卷五
 明  | deferred 待补见证 | 四库两家同读「㑹」（會），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载；位点为卷端页眉书名「三命通㑹卷五」之「㑹」字；现代各家页眉形态不同、位点未载，候选只据四库两家登记 |
| 149947 | 卷五 | 以财为引逢官防财
 忌身弱 | deferred 待补见证 | 四库谱系仅 mikkokotila 一家读「㸔」（看），kanripo bracket 栏式编排致未定位，现代独立见证亦未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 151346 | 卷五 | 偏之见也又云防官星有天官乡 | confirmed 定案 | 应改读「看」（四库字形 㸔），登记为未来应用候选；NiuTrans 同读「看」（side_anchored）；youngzs 同读「看」（side_anchored）；Banny-Gao（旁证） 同读「看」（side_anchored） |
| 152142 | 卷五 | 登科甲而封妻防子岁运行官印 | deferred 待补见证 | 四库两家同读「䕃」（蔭），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 152155 | 卷五 | 之乡万鼎千钟防旌五马若是庸 | deferred 待补见证 | 四库两家同读「䨇」（雙），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 152818 | 卷五 | 若遇火有重权防御刺史臣【如 | kept 保留 | 保留「防」，四库两家同读防、无已定位异读；NiuTrans 同读「防」（full_flank）；youngzs 同读「防」（full_flank）；Banny-Gao（旁证） 同读「防」（full_flank） |
| 153455 | 卷五 | 时上正官午戌防官局卯未防木 | deferred 待补见证 | 四库两家同读「㑹」（會），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 153460 | 卷五 | 戌防官局卯未防木局运至丁亥 | deferred 待补见证 | 四库两家同读「㑹」（會），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 154979 | 卷五 | 竒生日生时如防入太师太傅佩 | deferred 待补见证 | 四库两家同读「㸃」（點），youngzs《五行精纪》平行源文本异读「直」并录，现代计方见证未齐，不裁；NiuTrans 未载；youngzs《五行精纪》平行源文本异读「直」（不计现代方）；Banny-Gao（旁证） 未载 |
| 155128 | 卷五 | 发越
 官煞防墓
 如甲乙 | deferred 待补见证 | 四库两家同读「㑹」（會），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 155245 | 卷五 | 间故名如不犯防神恶煞冲破则 | deferred 待补见证 | 四库两家同读「㓙」（凶），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 155477 | 卷五 | 扶即经云逄煞防财如身强煞弱 | confirmed 定案 | 应改读「看」（四库字形 㸔），登记为未来应用候选；NiuTrans 未载；youngzs 同读「看」（side_anchored）；Banny-Gao（旁证） 未载 |
| 155929 | 卷五 | 见癸而煇光自防戊临甲位湏防 | confirmed 定案 | 应改读「滅」（四库字形 㓕），登记为未来应用候选；NiuTrans 未载；youngzs 同读「灭」（side_anchored）；Banny-Gao（旁证） 未载 |
| 155935 | 卷五 | 防戊临甲位湏防转福为殃巳坐 | kept 保留 | 保留「防」，四库两家同读防、无已定位异读；NiuTrans 未载；youngzs 同读「防」（side_anchored）；Banny-Gao（旁证） 未载 |
| 156199 | 卷五 | 逄财助其煞愈防又云刃为兵器 | confirmed 定案 | 应改读「凶」（四库字形 㓙），登记为未来应用候选；NiuTrans 未载；youngzs 同读「凶」（side_anchored）；Banny-Gao（旁证） 未载 |
| 156244 | 卷五 | 印又云受职宪防之除偏官得地 | deferred 待补见证 | 四库两家同读「䑓」（臺），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 156287 | 卷五 | 煞佩印足为乌防之论四言云煞 | deferred 待补见证 | 四库两家同读「䑓」（臺），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 156463 | 卷五 | 风定真赋云最防者七煞临身日 | deferred 待补见证 | 四库两家同读「㓙」（凶），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 156677 | 卷五 | 少年身旺定登防諌客印助扶官 | deferred 待补见证 | 四库两家同读「䑓」（臺），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 157717 | 卷五 | 喜逄羊刃不为防无冲有制为真 | deferred 待补见证 | 四库两家同读「㓙」（凶），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 158217 | 卷五 | 初年难免一塲防
 弃命从煞 | deferred 待补见证 | 四库两家同读「㓙」（凶），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 158886 | 卷五 | 杂为贱论
 防煞化印
 乃 | deferred 待补见证 | 四库两家同读「㑹」（會），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 158895 | 卷五 | 印
 乃支辰防合煞局如甲日 | deferred 待补见证 | 四库两家同读「㑹」（會），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 158928 | 卷五 | 最怕与流年相防旺财伤印防危 | deferred 待补见证 | 四库两家同读「㑹」（會），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 158933 | 卷五 | 相防旺财伤印防危如柱中元有 | deferred 待补见证 | 四库两家同读「㓙」（凶），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 158954 | 卷五 | 财星并克必遭防暴死如甲辰日 | deferred 待补见证 | 四库两家同读「㓙」（凶），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 158967 | 卷五 | 生子月见申时防起庚煞化印贵 | deferred 待补见证 | 四库两家同读「㑹」（會），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 159009 | 卷五 | 亥年受刑诗曰防煞为权福最多 | deferred 待补见证 | 四库两家同读「㑹」（會），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 161345 | 卷五 | 绶 食神逄财防官 以食为引 | deferred 待补见证 | 四库谱系仅 mikkokotila 一家读「㸔」（看），kanripo bracket 栏式编排致未定位，现代独立见证亦未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 162241 | 卷五 | 温两入中书奥防云我去克他为 | confirmed 定案 | 应改读「旨」（四库字形 㫖），登记为未来应用候选；NiuTrans 同读「旨」（side_anchored）；youngzs 同读「旨」（side_anchored）；Banny-Gao（旁证） 同读「旨」（side_anchored） |
| 163028 | 卷五 | 一世安然身康防纵使流年有财 | deferred 待补见证 | 四库两家同读「㤗」（泰），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 164471 | 卷五 | 子破财贫薄又防阴贼小人同类 | kept 保留 | 保留「防」，四库两家同读防、无已定位异读；NiuTrans 同读「防」（full_flank）；youngzs 同读「防」（full_flank）；Banny-Gao（旁证） 同读「防」（full_flank） |
| 165134 | 卷五 | 财还无遇富贵防全比石崇【又 | deferred 待补见证 | 四库两家同读「䨇」（雙），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 165323 | 卷五 | 简金鱼贵福夀防全事事宜
  | deferred 待补见证 | 四库两家同读「䨇」（雙），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 168046 | 卷五 | 比老彭之夀幽防赋云印绶逢生 | deferred 待补见证 | 四库两家同读「㣲」（微），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 168059 | 卷五 | 母当贤贵又云防嵗离母只为财 | deferred 待补见证 | 四库两家同读「㓜」（幼），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 168151 | 卷五 | 绶财伤母年早防又云贪财壊印 | deferred 待补见证 | 四库两家同读「䘮」（喪），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 168165 | 卷五 | 行比刼之乡奥防云印绶太过不 | deferred 待补见证 | 四库两家同读「㫖」（旨），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 168336 | 卷五 | 华葢与文星共防管仲为佐覇良 | deferred 待补见证 | 四库两家同读「㑹」（會），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 168345 | 卷五 | 为佐覇良臣造防论云印绶逢华 | confirmed 定案 | 应改读「微」（四库字形 㣲），登记为未来应用候选；NiuTrans 同读「微」（side_anchored）；youngzs 同读「微」（side_anchored）；Banny-Gao（旁证） 同读「微」（side_anchored） |
| 168392 | 卷五 | 若得官煞财相防亦为超迈贵人 | deferred 待补见证 | 四库两家同读「㑹」（會），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 168616 | 卷五 | 不善终【此言防煞与印绶同位 | deferred 待补见证 | 四库两家同读「㓙」（凶），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 168901 | 卷五 | 会却主斯人定防亡【又】印绶 | deferred 待补见证 | 四库两家同读「䘮」（喪），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 169057 | 卷五 | 若逢财旺地反防为吉遇王侯【 | deferred 待补见证 | 四库两家同读「㓙」（凶），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 169415 | 卷五 | 月内遭定因庇防显英豪多能少 | deferred 待补见证 | 四库两家同读「䕃」（蔭），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 169702 | 卷五 | 皆是午火当以防论却得年支寅 | deferred 待补见证 | 四库两家同读「㓙」（凶），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 169719 | 卷五 | 刃生火寅午又防火局化成印绶 | deferred 待补见证 | 四库两家同读「㑹」（會），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 170550 | 卷五 | 而多学少成奥防赋云年时月令 | deferred 待补见证 | 四库两家同读「㫖」（旨），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 170739 | 卷五 | 一见倒食便以防论
 论杂气 | confirmed 定案 | 应改读「凶」（四库字形 㓙），登记为未来应用候选；NiuTrans 同读「凶」（side_anchored）；youngzs 同读「凶」（side_anchored）；Banny-Gao（旁证） 同读「凶」（side_anchored） |
| 174934 | 卷五 | 遇官盛无印则防伤官不尽须防 | deferred 待补见证 | 四库两家同读「㓙」（凶），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 174940 | 卷五 | 防伤官不尽须防不测之灾伤官 | kept 保留 | 保留「防」，四库两家同读防、无已定位异读；NiuTrans 同读「防」（full_flank）；youngzs 同读「防」（full_flank）；Banny-Gao（旁证） 同读「防」（full_flank） |
| 175574 | 卷五 | 行财乡 逢食防财忌身弱 比 | deferred 待补见证 | 四库谱系仅 mikkokotila 一家读「㸔」（看），kanripo bracket 栏式编排致未定位，现代独立见证亦未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 177088 | 卷五 | 两省武为建节防团无亦主财帛 | kept 保留 | 保留「防」，四库两家同读防、无已定位异读；NiuTrans 同读「防」（full_flank）；youngzs 同读「防」（full_flank）；Banny-Gao（旁证） 同读「防」（full_flank） |
| 177441 | 卷五 | 食神带旺贤奥防篇云月令值食 | confirmed 定案 | 应改读「旨」（四库字形 㫖），登记为未来应用候选；NiuTrans 同读「旨」（side_anchored）；youngzs 同读「旨」（side_anchored）；Banny-Gao（旁证） 同读「旨」（side_anchored） |
| 177497 | 卷五 | 夭须知乞化幽防赋云食神旺相 | confirmed 定案 | 应改读「微」（四库字形 㣲），登记为未来应用候选；NiuTrans 同读「微」（side_anchored）；youngzs 同读「微」（side_anchored）；Banny-Gao（旁证） 同读「微」（side_anchored） |
| 177601 | 卷五 | 坐官三监九卿防万祺赋云食神 | deferred 待补见证 | 四库两家同读「㸔」（看），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 177885 | 卷五 | 何忧在嵗时禁防制暴干头旺此 | deferred 待补见证 | 四库两家同读「㓙」（凶），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 178901 | 卷五 | 虚离位就丁功防中同伴子难动 | deferred 待补见证 | 四库两家同读「䑕」（鼠），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 178980 | 卷五 | 若无填实虚有防豪杰英雄逈不 | deferred 待补见证 | 四库两家同读「㑹」（會），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 179218 | 卷五 | 午是刃虽贵终防一见合刃便为 | deferred 待补见证 | 四库两家同读「㓙」（凶），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 179225 | 卷五 | 一见合刃便为防命若月令亥子 | deferred 待补见证 | 四库两家同读「㓙」（凶），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 180330 | 卷五 | 行丙戊生灾害防子刑妻不可当 | deferred 待补见证 | 四库两家同读「䘮」（喪），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 185380 | 卷五 | 建禄将何取须防年时多透露局 | deferred 待补见证 | 四库两家同读「㸔」（看），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 185427 | 卷五 | 兴财禄水取堤防破贵元明通赋 | kept 保留 | 保留「防」，四库两家同读防、无已定位异读；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 185571 | 卷五 | 

 三命通防卷五
<子部 | deferred 待补见证 | 四库两家同读「㑹」（會），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载；位点为卷末页眉书名「三命通㑹卷五」之「㑹」字；现代各家页眉形态不同、位点未载，候选只据四库两家登记 |

RD-12 只标记两处（不处置，捕获证据逐字在案，裁定随 P3）：

| S0 位点 | RD-12 seq | 语境（S3 ±6） | 四库两家 | 现代三家 |
|---|---|---|---|---|
| 157779 | 361 | 有制身强好命防制过喜行煞旺 | 同读「㸔」（看） | NiuTrans/youngzs/Banny-Gao 同读「者」 |
| 164133 | 385 | 受伯叔祖考产防丰隆或外祖产 | 同读「䕃」（蔭） | NiuTrans/youngzs/Banny-Gao 同读「业」 |

### 11.4 定案要点与 deferred 缺口形态

- **confirmed 9**：151346 㸔（看，四库与现代三家同读）、
  155477 㸔（看，youngzs 子集同读）、155929 㓕（滅，
  youngzs 子集同读「灭」）、156199 㓙（凶，youngzs 子集
  同读）、162241 㫖（旨，现代三家同读）、168345 㣲
  （微，现代三家同读）、170739 㓙（凶，现代三家同读）、
  177441 㫖（旨，《奥旨篇》篇名位点，现代三家同读）、
  177497 㣲（微，《幽微赋》篇名位点，现代三家同读）——
  均四库 + 至少一独立现代方同读、读法只登记为未来 v2
  应用候选，文本未动。
- **kept 6**：152818（防御）、155935、164471、174940、
  177088、185427（堤防）——四库同读防且无已定位异读，
  依 §2 不对称标准保留。
- **parallel 0**：本册无计方见证间的位点分歧；154979 的
  「㸃/直」异读系三命文本与被引源文本（《五行精纪》）
  之间、非谱系见证分歧，归 deferred 并两读并录。
- **deferred 50**：缺口形态为三命通会文本自身的第二个
  独立见证方未齐。字形分布：㑹 14（含卷端页眉书名 2
  处）、㓙 13、㸔 5（其中三处另缺 kanripo 位点定位，
  见 §11.1）、䨇 3、䑓 3、䘮 3、䕃 2、㫖 2，餘 㣲/㤗/
  㓜/䑕/㸃 各 1。升级路径同 §5：补齐现代全本转录（如
  Wikisource michiboo《三命通会》对应卷次）或四库影印
  原叶定位后逐处升级。

### 11.5 累计进度与剩余分册计划（更新）

- 累计处置进度：**disposed 54/769**（confirmed 23、kept
  29、parallel 2）；deferred 258（节内 29 + 第二分册
  67 + 第三分册 112 + 本册 50）；pending 457（其中
  RD-12 位点 7 处只标记、处置随 P3）。
- 全卷累计：

| 卷 | 盘点 | confirmed | kept | parallel | deferred | pending |
|---|---|---|---|---|---|---|
| 卷首 | 1 | 0 | 0 | 1 | 0 | 0 |
| 卷一 | 10 | 0 | 8 | 0 | 2 | 0 |
| 卷二 | 34 | 2 | 2 | 1 | 29 | 0 |
| 卷三 | 50 | 1 | 6 | 0 | 43 | 0 |
| 卷四 | 118 | 2 | 4 | 0 | 112 | 0 |
| 卷五 | 89 | 14 | 8 | 0 | 65 | 2 |
| 卷六 | 142 | 4 | 1 | 0 | 7 | 130 |
| 卷七 | 75 | 0 | 0 | 0 | 0 | 75 |
| 卷八 | 61 | 0 | 0 | 0 | 0 | 61 |
| 卷九 | 94 | 0 | 0 | 0 | 0 | 94 |
| 卷十 | 26 | 0 | 0 | 0 | 0 | 26 |
| 卷十一 | 45 | 0 | 0 | 0 | 0 | 45 |
| 卷十二 | 24 | 0 | 0 | 0 | 0 | 24 |
| 合计 | 769 | 23 | 29 | 2 | 258 | 457 |

- 剩余分册（按卷序）：卷六 130、卷七 75、卷八 61、卷九
  94、卷十 26、卷十一 45、卷十二 24，另卷五 RD-12 两处
  随 P3。本册同样只登记处置结论、零文本改动，
  `canonical_ready` 保持 false。

## 12. 第五分册（卷六节外 130 处，E0310）

### 12.1 范围与方法补记

- 范围：卷六节外 pending **130 处**全部逐处处置（一卷
  一册）；本册**无 RD-12 标记位点**（盘点在册的节外
  RD-12 位点分布于卷五/卷七/卷十/卷十一，仍只标记、
  处置随 P3）。
- 捕获式定位沿第二至第四分册，见证口径含 E0306 子集
  澄清。四库谱系：kanripo 与 mikkokotila **130/130 处
  全定位**，读法逐处完全一致（其中 mikkokotila 于
  212273 一处为单侧锚定定位）——本册无第三分册 126098
  式 kanripo 全文无此段的情形，亦无第四分册卷首喜忌
  bracket 栏式编排致未定位的情形。
- 现代谱系计方见证本册实定位 **9 处**：NiuTrans 7 处、
  youngzs 三命子集 7 处（交集 5 处），Banny-Gao 旁证
  9 处。其中 193388（拱禄拱贵塡实则㐫）与 196506
  （月干见煞䨇目不明）两处位点语亦载于卷十二《四言
  独步》，NiuTrans 定位于其卷十二《四言独步》转录的
  同文位点（侧翼锚定对应、非关键词散检），与第二分册
  214497、第四分册卷五赋文跨卷定位同型，在案可核；
  两处四库两家均于卷六本节定位同读。
- youngzs 平行源文本旁证 1 处：218248 处其《五行精纪》
  转录读「双」，与四库两家同读之「䨇」**同读**——旁证
  同读亦只登记为 attested_parallel_source、不计现代
  方、不作定案依据（与第三分册 146688、第四分册
  154979 的旁证异读同例：旁证形态只登记、不计方、
  不作分歧），该处归 deferred。

### 12.2 本册计数

| 卷 | 盘点 | confirmed | kept | parallel | deferred | pending |
|---|---|---|---|---|---|---|
| 卷六 | 130 | 7 | 5 | 0 | 118 | 0 |
| 本册合计（处置范围） | 130 | 7 | 5 | 0 | 118 | 0 |

（卷六全卷口径另含首批已登记节内既处 12 处——
confirmed 4、kept 1、deferred 7，见 §12.5 全卷累计表。）

### 12.3 本册处置（130 处逐处）

| S0 位点 | 卷 | 语境（S3 ±6） | 处置分类 | 结论与见证要点 |
|---|---|---|---|---|
| 186546 | 卷六 | 煞太旺尅壬为防【独歩云】壬 | deferred 待补见证 | 四库两家同读「㐫」（凶），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 186868 | 卷六 | 合全水局富贵防全逈异常【鹧 | deferred 待补见证 | 四库两家同读「䨇」（雙），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 188010 | 卷六 | 酉癸逄官会合防蛇愁见福消磨 | deferred 待补见证 | 四库两家同读「䑕」（鼠），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 188121 | 卷六 | 助行财印刑冲防合皆美歳月支 | deferred 待补见证 | 四库两家同读「㑹」（會），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 188556 | 卷六 | 得任戊己倘逄防易致庚申忽遇 | deferred 待补见证 | 四库两家同读「㐫」（凶），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 190153 | 卷六 | 子是得一分三防其元辰有此为 | deferred 待补见证 | 四库两家同读「㸔」（看），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 190231 | 卷六 | 命之理所以为防也
 刑冲带 | deferred 待补见证 | 四库两家同读「㣲」（微），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 190310 | 卷六 | 多躭酒色重则防身破家轻则成 | deferred 待补见证 | 四库两家同读「䘮」（喪），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 190362 | 卷六 | 漂荡无成运行防煞尅身多致防 | deferred 待补见证 | 四库两家同读「㐫」（凶），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 190368 | 卷六 | 防煞尅身多致防生女命尤忌【 | deferred 待补见证 | 四库两家同读「䘮」（喪），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 191038 | 卷六 | 深子隠贵渊成防合戊来动丙得 | deferred 待补见证 | 四库两家同读「㑹」（會），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 191139 | 卷六 | 万民
 六乙防贵
 【喜忌 | deferred 待补见证 | 四库两家同读「䑕」（鼠），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 191539 | 卷六 | 【眞宝赋云】防贵带食蚤为藩 | deferred 待补见证 | 四库两家同读「䑕」（鼠），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 191588 | 卷六 | 墀【又】六乙防贵在生时煞官 | deferred 待补见证 | 四库两家同读「䑕」（鼠），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 191677 | 卷六 | 逄之为丐子【防】乙日时逄丙 | deferred 待补见证 | 四库两家同读「㐅」（五），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载；位点为【】内单字题字，四库两家读「㐅」（五之异体），候选字词依四库字形登记为「五」；语境不足以再定其文义，现代见证未载 |
| 191748 | 卷六 | 生逄丙子名为防贵幽玄无冲无 | deferred 待补见证 | 四库两家同读「䑕」（鼠），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 192407 | 卷六 | 于日所以承祖防受职富贵成名 | deferred 待补见证 | 四库两家同读「䕃」（蔭），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 192941 | 卷六 | 禄拱贵塡实则防拱向也夹也禄 | confirmed 定案 | 应改读「凶」（四库字形 㐫），登记为未来应用候选；NiuTrans 同读「凶」（side_anchored）；youngzs 同读「凶」（side_anchored）；Banny-Gao（旁证） 同读「凶」（side_anchored） |
| 193151 | 卷六 | 曰】虚拱之法防拱出空中之物 | deferred 待补见证 | 四库两家同读「㸔」（看），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 193167 | 卷六 | 家何物或吉神防煞之类如子寅 | deferred 待补见证 | 四库两家同读「㐫」（凶），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 193388 | 卷六 | 禄拱贵塡实则防提纲有用论之 | confirmed 定案 | 应改读「凶」（四库字形 㐫），登记为未来应用候选；NiuTrans 同读「凶」（side_anchored）；youngzs 未载；Banny-Gao（旁证） 同读「凶」（side_anchored）；位点语「拱禄拱贵塡实则㐫」亦载于卷十二《四言独步》；NiuTrans 计方见证定位于其卷十二《四言独步》转录的同文位点（侧翼锚定对应），与第二分册 214497、第四分册卷五赋文跨卷定位同型；四库两家于卷六本节定位同读㐫、Banny-Gao 旁证同读凶 |
| 194156 | 卷六 | 喜财
 财官防美
 【继善 | confirmed 定案 | 应改读「雙」（四库字形 䨇），登记为未来应用候选；NiuTrans 未载；youngzs 同读「双」（side_anchored）；Banny-Gao（旁证） 同读「双」（side_anchored） |
| 194973 | 卷六 | 月二德乃日月防合照临有何隂 | deferred 待补见证 | 四库两家同读「㑹」（會），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 195008 | 卷六 | 地德秀之气化防为吉之神人命 | deferred 待补见证 | 四库两家同读「㐫」（凶），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 195064 | 卷六 | 禄显一生不遭防横若犯伤破作 | deferred 待补见证 | 四库两家同读「㐫」（凶），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 195327 | 卷六 | 】一德扶持众防解释男逄平歩 | deferred 待补见证 | 四库两家同读「㐫」（凶），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 195439 | 卷六 | 施恩布德【幽防赋云】慈祥敏 | deferred 待补见证 | 四库两家同读「㣲」（微），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 195455 | 卷六 | 二德呈祥【奥防赋云】命亏煞 | deferred 待补见证 | 四库两家同读「㫖」（旨），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 195582 | 卷六 | 汾阳富石崇祖防丰肥承福厚不 | deferred 待补见证 | 四库两家同读「䕃」（蔭），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 195826 | 卷六 | 本主生旺富贵防全本主休囚未 | deferred 待补见证 | 四库两家同读「䨇」（雙），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 195875 | 卷六 | 丙丁日是也更防日干见官贵禄 | deferred 待补见证 | 四库两家同读「㑹」（會），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 196506 | 卷六 | 金神月干见煞防目不明【经云 | confirmed 定案 | 应改读「雙」（四库字形 䨇），登记为未来应用候选；NiuTrans 同读「双」（side_anchored）；youngzs 未载；Banny-Gao（旁证） 同读「双」（side_anchored）；位点语「月干见煞䨇目不明」为金神语，亦载于卷十二《四言独步》；NiuTrans 计方见证定位于其卷十二《四言独步》转录的同文位点（侧翼锚定对应），与193388 同型；四库两家于卷六本节定位同读䨇、Banny-Gao 旁证同读双 |
| 196566 | 卷六 | 乡若行北方则防【相心赋云】 | deferred 待补见证 | 四库两家同读「㐫」（凶），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 196833 | 卷六 | 趋南虽逄羊刃防为吉纵欲偏官 | deferred 待补见证 | 四库两家同读「㐫」（凶），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 197319 | 卷六 | 害谩咨嗟才临防合方成贵终始 | deferred 待补见证 | 四库两家同读「㑹」（會），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 197387 | 卷六 | 魁罡分昼夜更防刑害失尊卑运 | kept 保留 | 保留「防」，四库两家同读防、无已定位异读；NiuTrans 同读「防」（full_flank）；youngzs 同读「防」（full_flank）；Banny-Gao（旁证） 同读「防」（full_flank） |
| 197418 | 卷六 | 厚德或逄前戒防无疑
 日德 | deferred 待补见证 | 四库两家同读「㐫」（凶），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 197792 | 卷六 | 见壬辰壬戌隄防戊戌临日坐庚 | kept 保留 | 保留「防」，四库两家同读防、无已定位异读；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 198182 | 卷六 | 临财官旺处主防竒祸若月令见 | kept 保留 | 保留「防」，四库两家同读防、无已定位异读；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 199534 | 卷六 | 内三竒地支暗防财官为眞禄眞 | deferred 待补见证 | 四库两家同读「㑹」（會），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 199922 | 卷六 | 帛丰盛但三竒防食只以偏印为 | deferred 待补见证 | 四库两家同读「㑹」（會），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 200125 | 卷六 | 伤故正官正印防偏财也凡人遇 | deferred 待补见证 | 四库两家同读「㑹」（會），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 200250 | 卷六 | 损破耗镃基祖防歳运临死絶之 | deferred 待补见证 | 四库两家同读「䕃」（蔭），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 200270 | 卷六 | 必见重祸但凡防命要察柱中何 | deferred 待补见证 | 四库两家同读「㸔」（看），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 200308 | 卷六 | 相助者有救虽防不死再相助者 | deferred 待补见证 | 四库两家同读「㐫」（凶），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 200355 | 卷六 | 纲纪大满门受防定光辉【又】 | deferred 待补见证 | 四库两家同读「䕃」（蔭），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 200656 | 卷六 | 申位逄阳水难防延年巳入亥宫 | deferred 待补见证 | 四库两家同读「䕶」（護），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 200755 | 卷六 | 生
 禄元三防
 此格如甲 | deferred 待补见证 | 四库两家同读「㑹」（會），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 200907 | 卷六 | 子论】禄有三防乃甲见寅而得 | deferred 待补见证 | 四库两家同读「㑹」（會），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 201279 | 卷六 | 用乃虚中之奥防祸福贫贱载在 | deferred 待补见证 | 四库两家同读「㫖」（旨），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 201433 | 卷六 | 子日时俱财官防美【又】丙子 | deferred 待补见证 | 四库两家同读「䨇」（雙），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 201737 | 卷六 | 贵基
 子午防包
 子为帝 | confirmed 定案 | 应改读「雙」（四库字形 䨇），登记为未来应用候选；NiuTrans 未载；youngzs 同读「双」（side_anchored）；Banny-Gao（旁证） 同读「双」（side_anchored） |
| 201982 | 卷六 | 逄库相助财官防美不寻常
  | deferred 待补见证 | 四库两家同读「䨇」（雙），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 202407 | 卷六 | 吉冲破身弱则防歳运司有以壬 | deferred 待补见证 | 四库两家同读「㐫」（凶），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 202426 | 卷六 | 受戮主官员被防有失小人是非 | confirmed 定案 | 应改读「讒」（四库字形 䜛），登记为未来应用候选；NiuTrans 同读「谗」（side_anchored）；youngzs 同读「谗」（side_anchored）；Banny-Gao（旁证） 同读「谗」（side_anchored） |
| 204968 | 卷六 | 从众水得土堤防行丙申丁酉运 | kept 保留 | 保留「防」，四库两家同读防、无已定位异读；NiuTrans 同读「防」（full_flank）；youngzs 同读「防」（full_flank）；Banny-Gao（旁证） 同读「防」（full_flank） |
| 205003 | 卷六 | 戊巳居润下为防
 金白水清 | deferred 待补见证 | 四库两家同读「㐫」（凶），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 206113 | 卷六 | 月夹藏墓中皆防
 四位纯全 | confirmed 定案 | 应改读「凶」（四库字形 㐫），登记为未来应用候选；NiuTrans 同读「凶」（side_anchored）；youngzs 同读「凶」（side_anchored）；Banny-Gao（旁证） 同读「凶」（side_anchored） |
| 206432 | 卷六 | 带孤寡刑害尅防必重【精纪云 | deferred 待补见证 | 四库两家同读「䧟」（陷），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 206912 | 卷六 | 气重多主孤或防失防亲或至晚 | deferred 待补见证 | 四库两家同读「㓜」（幼），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 206914 | 卷六 | 多主孤或防失防亲或至晚年多 | deferred 待补见证 | 四库两家同读「䨇」（雙），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 206964 | 卷六 | 四丁未刃旺多防恶为军人却以 | deferred 待补见证 | 四库两家同读「㐫」（凶），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 207016 | 卷六 | 皆有此祸湏预防之四丙申七月 | kept 保留 | 保留「防」，四库两家同读防、无已定位异读；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 207031 | 卷六 | 死财旺生煞为防喜四丙同类助 | deferred 待补见证 | 四库两家同读「㐫」（凶），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 207125 | 卷六 | 火为印多贵男防女吉【又曰】 | deferred 待补见证 | 四库两家同读「㐫」（凶），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 207301 | 卷六 | 三子时亥为羣防夜逰三酉时寅 | deferred 待补见证 | 四库两家同读「䑕」（鼠），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 207881 | 卷六 | 南方行运数还防
 天干顺食 | deferred 待补见证 | 四库两家同读「㐫」（凶），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 208378 | 卷六 | 大纲难去得更防向背运辰行不 | deferred 待补见证 | 四库两家同读「㸔」（看），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 209533 | 卷六 | 上湿木不能生防非特财薄反自 | deferred 待补见证 | 四库两家同读「㷔」（焰），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 209567 | 卷六 | 星【又云】但防财命有气逄背 | deferred 待补见证 | 四库两家同读「㸔」（看），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 209934 | 卷六 | 忌见伤官土局防横夭折葢一隂 | deferred 待补见证 | 四库两家同读「㐫」（凶），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 209946 | 卷六 | 隂初生其气甚防故也此象用丙 | deferred 待补见证 | 四库两家同读「㣲」（微），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 210336 | 卷六 | 印两全虽辰子防水寅午亦防火 | deferred 待补见证 | 四库两家同读「㑹」（會），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 210341 | 卷六 | 子防水寅午亦防火力停不降故 | deferred 待补见证 | 四库两家同读「㑹」（會），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 210379 | 卷六 | 后居官定入紫防垣
 吉防防 | deferred 待补见证 | 四库两家同读「㣲」（微），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 210384 | 卷六 | 紫防垣
 吉防防防
 假甲 | deferred 待补见证 | 四库两家同读「㑹」（會），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 210385 | 卷六 | 防垣
 吉防防防
 假甲日 | deferred 待补见证 | 四库两家同读「㐫」（凶），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 210386 | 卷六 | 垣
 吉防防防
 假甲日生 | deferred 待补见证 | 四库两家同读「㑹」（會），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 210398 | 卷六 | 生人见子辰全防起申庚为甲七 | deferred 待补见证 | 四库两家同读「㑹」（會），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 210407 | 卷六 | 庚为甲七煞乃防防也柱有丙或 | deferred 待补见证 | 四库两家同读「㐫」（凶），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 210408 | 卷六 | 为甲七煞乃防防也柱有丙或乙 | deferred 待补见证 | 四库两家同读「㑹」（會），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 210475 | 卷六 | 日生人见卯未防出亥壬为七煞 | deferred 待补见证 | 四库两家同读「㑹」（會），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 210542 | 卷六 | 余例推窃详吉防防如命喜财官 | deferred 待补见证 | 四库两家同读「㐫」（凶），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 210543 | 卷六 | 例推窃详吉防防如命喜财官印 | deferred 待补见证 | 四库两家同读「㑹」（會），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 210563 | 卷六 | 小运歳君俱合防决主大发富贵 | deferred 待补见证 | 四库两家同读「㑹」（會），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 210598 | 卷六 | 合会决主大发防祸谓之防防非 | deferred 待补见证 | 四库两家同读「㐫」（凶），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 210602 | 卷六 | 大发防祸谓之防防非专指三合 | deferred 待补见证 | 四库两家同读「㐫」（凶），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 210603 | 卷六 | 发防祸谓之防防非专指三合会 | deferred 待补见证 | 四库两家同读「㑹」（會），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 210625 | 卷六 | 【诗曰】吉会防防要推详吉防 | deferred 待补见证 | 四库两家同读「㐫」（凶），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 210626 | 卷六 | 诗曰】吉会防防要推详吉防相 | deferred 待补见证 | 四库两家同读「㑹」（會），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 210631 | 卷六 | 防防要推详吉防相逄最吉昌若 | deferred 待补见证 | 四库两家同读「㑹」（會），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 210639 | 卷六 | 逄最吉昌若是防神三合起破财 | deferred 待补见证 | 四库两家同读「㐫」（凶），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 210729 | 卷六 | 以有辱日时同防四柱暗带切于 | deferred 待补见证 | 四库两家同读「㸔」（看），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 210747 | 卷六 | 带以言贵贱吉防若夹煞持墓决 | deferred 待补见证 | 四库两家同读「㐫」（凶），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 210755 | 卷六 | 夹煞持墓决主防死
 五行拘 | deferred 待补见证 | 四库两家同读「㐫」（凶），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 210969 | 卷六 | 来眞举世无人防发明甲乙人言 | deferred 待补见证 | 四库两家同读「㑹」（會），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 211443 | 卷六 | 空自忙节槩低防无足取眼前骨 | deferred 待补见证 | 四库两家同读「㣲」（微），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 211515 | 卷六 | 粮戊癸南方火防高午寅时上逞 | deferred 待补见证 | 四库两家同读「㷔」（焰），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 212168 | 卷六 | 临于天秤禄逄防美欣巳共于金 | deferred 待补见证 | 四库两家同读「䨇」（雙），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 212273 | 卷六 | 位飘蓬落魄戊防煞方皓首无成 | deferred 待补见证 | 四库两家同读「㑹」（會），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 215083 | 卷六 | 也
 君臣庆防
 干为君之 | deferred 待补见证 | 四库两家同读「㑹」（會），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 215112 | 卷六 | 之是谓君臣庆防如甲戌见巳卯 | deferred 待补见证 | 四库两家同读「㑹」（會），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 215146 | 卷六 | 合日与时合为防鸳徳合尤妙以 | deferred 待补见证 | 四库两家同读「䨇」（雙），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 215436 | 卷六 | 壬寅辛亥王一防状元乙巳戊子 | deferred 待补见证 | 四库两家同读「䕫」（夔），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载；位点在例命人名语境（壬寅辛亥王一䕫状元），四库两家读「䕫」，候选字词依四库字形登记为「夔」；现代见证未载 |
| 215943 | 卷六 | 记】
 聚精防神
 淮南子 | deferred 待补见证 | 四库两家同读「㑹」（會），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 216120 | 卷六 | 壬为阳干之吉防生于孟月尤佳 | deferred 待补见证 | 四库两家同读「㑹」（會），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 216144 | 卷六 | 居季月最好六防神至此而潜藏 | deferred 待补见证 | 四库两家同读「㐫」（凶），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 216311 | 卷六 | 则煞没 天乙防将有六螣蛇朱 | deferred 待补见证 | 四库两家同读「㐫」（凶），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 216583 | 卷六 | 是也
 干支防连
 谓甲午 | deferred 待补见证 | 四库两家同读「䨇」（雙），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 216903 | 卷六 | 之类【赋云】防茅连茹兮愈坚 | deferred 待补见证 | 四库两家同读「㧞」（拔），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 216936 | 卷六 | 地支俱连富贵防全如英国公丁 | deferred 待补见证 | 四库两家同读「䨇」（雙），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 217138 | 卷六 | 重是也
 福防相迎
 此十 | deferred 待补见证 | 四库两家同读「㑹」（會），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 217538 | 卷六 | 之宫福自强更防权煞在何方数 | deferred 待补见证 | 四库两家同读「㸔」（看），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 217607 | 卷六 | 位与四位纯全防不同谓寅申巳 | deferred 待补见证 | 四库两家同读「㣲」（微），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 217825 | 卷六 | 卯火为沐浴气防而败灰烬镕竭 | deferred 待补见证 | 四库两家同读「㣲」（微），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 218222 | 卷六 | 尤胜
 六合防鸳
 如戊辰 | deferred 待补见证 | 四库两家同读「䨇」（雙），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 218248 | 卷六 | 【经云】六合防鸳坐槐庭而布 | deferred 待补见证 | 四库两家同读「䨇」（雙），youngzs《五行精纪》平行源文本同读「双」并录，现代计方见证未齐，不裁；NiuTrans 未载；youngzs《五行精纪》平行源文本同读「双」（不计现代方）；Banny-Gao（旁证） 未载 |
| 218268 | 卷六 | 寅甲寅丙寅名防飞蝴蝶格此格 | deferred 待补见证 | 四库两家同读「䨇」（雙），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 218483 | 卷六 | 地气全前后要防纳音有无生旺 | deferred 待补见证 | 四库两家同读「㸔」（看），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 219341 | 卷六 | 吟啸风云成聚防荣华富贵受皇 | deferred 待补见证 | 四库两家同读「㑹」（會），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 219613 | 卷六 | 逄墓印为灾为防丙丁猪鸡以戌 | deferred 待补见证 | 四库两家同读「㐫」（凶），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 219724 | 卷六 | 断不必在牛羊防猴鸡猪马虎之 | deferred 待补见证 | 四库两家同读「䑕」（鼠），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 220294 | 卷六 | 空亡只在格上防之又湏尊者吉 | deferred 待补见证 | 四库两家同读「㸔」（看），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 220335 | 卷六 | 絶兹为尊吉卑防若纳音既死絶 | deferred 待补见证 | 四库两家同读「㐫」（凶），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 220740 | 卷六 | 禄马官印贵德防于帝座三合于 | deferred 待补见证 | 四库两家同读「㑹」（會），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 222434 | 卷六 | 十干日内细推防甲乙逄寅卯为 | deferred 待补见证 | 四库两家同读「㸔」（看），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 222445 | 卷六 | 卯为贵
 重防重官
 重防 | deferred 待补见证 | 四库两家同读「䕃」（蔭），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 222451 | 卷六 | 防重官
 重防者如甲人逄癸 | deferred 待补见证 | 四库两家同读「䕃」（蔭），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 222477 | 卷六 | 丙葢甲以癸为防癸以庚为防甲 | deferred 待补见证 | 四库两家同读「䕃」（蔭），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 222482 | 卷六 | 为防癸以庚为防甲以辛为官辛 | deferred 待补见证 | 四库两家同读「䕃」（蔭），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |

### 12.4 定案要点与 deferred 缺口形态

- **confirmed 7**：192941 㐫（凶，《喜忌篇》拱禄拱贵语，
  现代三家同读）、193388 㐫（凶，同语见卷十二《四言
  独步》，NiuTrans 于其四言独步转录同文位点同读）、
  206113 㐫（凶，墓煞语，现代三家同读）、194156 䨇
  （雙，《继善篇》财官双美节题位点，youngzs 子集与
  Banny-Gao 同读「双」）、196506 䨇（雙，金神语，
  NiuTrans 于其四言独步转录同文位点同读）、201737 䨇
  （雙，子午双包节题位点，youngzs 子集同读）、202426
  䜛（讒，玄武当权语，现代三家同读「谗」）——均四库
  + 至少一独立现代方同读、读法只登记为未来 v2 应用
  候选，文本未动。
- **kept 5**：197387（更防刑害，现代三家同读防）、
  197792（隄防）、198182（主防竒祸）、204968（堤防，
  现代三家同读防）、207016（湏预防之）——四库同读防
  且无已定位异读，依 §2 不对称标准保留。
- **parallel 0**：本册无计方见证间的位点分歧；218248
  的「䨇/双」同读系三命文本与被引源文本（《五行精
  纪》）之间、非谱系见证分歧，归 deferred 并两读
  并录。
- **deferred 118**：缺口形态为三命通会文本自身的第二
  个独立见证方未齐。字形分布：㐫 31、㑹 31、䨇 12
  （含 218248 旁证同读 1）、㸔 10、䕃 8、䑕 7、㣲 7、
  䘮 2、㫖 2、㷔 2，餘 㐅/䕶/䧟/㓜/䕫/㧞 各 1（㐅为
  【】内单字题字、䕫为例命人名用字，均已逐处注记）。
  升级路径同 §5：补齐现代全本转录（如 Wikisource
  michiboo《三命通会》对应卷次）或四库影印原叶定位后
  逐处升级。

### 12.5 累计进度与剩余分册计划（更新）

- 累计处置进度：**disposed 66/769**（confirmed 30、kept
  34、parallel 2）；deferred 376（节内 29 + 第二分册
  67 + 第三分册 112 + 第四分册 50 + 本册 118）；pending
  327（其中 RD-12 位点 7 处只标记、处置随 P3）。
- 全卷累计：

| 卷 | 盘点 | confirmed | kept | parallel | deferred | pending |
|---|---|---|---|---|---|---|
| 卷首 | 1 | 0 | 0 | 1 | 0 | 0 |
| 卷一 | 10 | 0 | 8 | 0 | 2 | 0 |
| 卷二 | 34 | 2 | 2 | 1 | 29 | 0 |
| 卷三 | 50 | 1 | 6 | 0 | 43 | 0 |
| 卷四 | 118 | 2 | 4 | 0 | 112 | 0 |
| 卷五 | 89 | 14 | 8 | 0 | 65 | 2 |
| 卷六 | 142 | 11 | 6 | 0 | 125 | 0 |
| 卷七 | 75 | 0 | 0 | 0 | 0 | 75 |
| 卷八 | 61 | 0 | 0 | 0 | 0 | 61 |
| 卷九 | 94 | 0 | 0 | 0 | 0 | 94 |
| 卷十 | 26 | 0 | 0 | 0 | 0 | 26 |
| 卷十一 | 45 | 0 | 0 | 0 | 0 | 45 |
| 卷十二 | 24 | 0 | 0 | 0 | 0 | 24 |
| 合计 | 769 | 30 | 34 | 2 | 376 | 327 |

- 剩余分册（按卷序）：卷七 75、卷八 61、卷九 94、卷十
  26、卷十一 45、卷十二 24，另卷五 RD-12 两处随 P3。
  本册同样只登记处置结论、零文本改动，
  `canonical_ready` 保持 false。

## 13. 第六分册（卷七节外 73 处，另 RD-12 两处只标记，E0312）

### 13.1 范围与方法补记

- 范围：卷七节外 pending **75 处**中的 **73 处**逐处处置
  （一卷一册）；RD-12 seq 612（S0 228261）与 seq 616
  （S0 228869）两处**只标记、不处置、保持 pending**
  （裁定权在 P3）。两处捕获证据在案：228261 四库两家
  同读「㿀」、现代计方两家（NiuTrans 与 youngzs 子集）
  同读「癍」、Banny-Gao 旁证同读「癍」；228869 四库
  两家同读「䖝」、现代计方两家同读「茧」、Banny-Gao
  旁证同读「茧」——双方读法分歧逐字在案、不在本册裁定。
- 捕获式定位沿第二至第五分册，见证口径含 E0306 子集
  澄清。四库谱系：kanripo 与 mikkokotila 于 73 处中
  **72 处标准捕获全定位**、读法逐处完全一致；余 245945
  一处紧邻左字在快照底本作「妝」、四库两家转录均作
  「粧」（同词异体），致标准侧翼全锚、单侧锚定与句段
  锚定全数失败，改以**变体锚定**定位——左翼仅紧邻一位
  放宽为通配、其余侧翼逐字全锚，两家同读「䑓」（臺），
  match_mode 登记 `variant_anchored`，逐字对位关系在
  该处注记中在案。放宽只及紧邻异体一位，位点字仍由全
  锚侧翼对位捕获、不预设读法。
- 现代谱系计方见证本册实定位 **6 处**：NiuTrans 6 处、
  youngzs 三命子集 5 处（交集 5 处），Banny-Gao 旁证
  6 处（与计方定位同位点集）。youngzs 全语料定位与三
  命子集定位全同，**本册无平行源文本旁证命中**（全册
  累计仍 26 处）。
- 226603 处四库字形「膞」与现代计方读「膊」系同词
  异体，依 §2 分类定义「字形异体以词为准」定案（登记
  字形从四库、词从膊）。

### 13.2 本册计数

| 卷 | 盘点 | confirmed | kept | parallel | deferred | pending |
|---|---|---|---|---|---|---|
| 卷七 | 73 | 4 | 8 | 0 | 61 | 0 |
| 本册合计（处置范围） | 73 | 4 | 8 | 0 | 61 | 0 |

（卷七全卷口径另含 RD-12 两处只标记 pending，见 §13.5
全卷累计表：卷七盘点 75 = 本册处置 73 + RD-12 两处。）

### 13.3 本册处置（73 处逐处）

| S0 位点 | 卷 | 语境（S3 ±6） | 处置分类 | 结论与见证要点 |
|---|---|---|---|---|
| 224376 | 卷七 | 亨通譬医家补防之法耳若日干 | deferred 待补见证 | 四库两家同读「㵼」（瀉），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 224675 | 卷七 | 行所授铜钹要防占人吉凶极验 | deferred 待补见证 | 四库两家同读「㫖」（旨），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 224850 | 卷七 | 观五行精纪兰防妙选三车一覧 | deferred 待补见证 | 四库两家同读「䑓」（臺），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 225847 | 卷七 | 欢乐多情尚义防有不善终之患 | kept 保留 | 保留「防」，四库两家同读防、无已定位异读；NiuTrans 同读「防」（full_flank）；youngzs 同读「防」（full_flank）；Banny-Gao（旁证） 同读「防」（full_flank） |
| 225897 | 卷七 | 检约不妄设施防有隂谋之患若 | kept 保留 | 保留「防」，四库两家同读防、无已定位异读；NiuTrans 同读「防」（side_anchored）；youngzs 同读「防」（side_anchored）；Banny-Gao（旁证） 同读「防」（side_anchored） |
| 225973 | 卷七 | 抝举动修饰专防言词好自矜衒 | deferred 待补见证 | 四库两家同读「㺯」（弄），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 226603 | 卷七 | 两肩均左右二防是辰申夘酉双 | confirmed 定案 | 应改读「膊」（四库字形 膞），登记为未来应用候选；NiuTrans 同读「膊」（side_anchored）；youngzs 同读「膊」（side_anchored）；Banny-Gao（旁证） 同读「膊」（side_anchored）；四库两家字形作「膞」、现代计方两家读「膊」，系同词异体，依处置分类定义「字形异体以词为准」定案，登记字形从四库、词从膊 |
| 226776 | 卷七 | 调畅早年落髪防青爪枯属肝家 | deferred 待补见证 | 四库两家同读「䈥」（筋），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 228279 | 卷七 | 丙丁火旺疾难防四柱休囚辰巳 | kept 保留 | 保留「防」，四库两家同读防、无已定位异读；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 229609 | 卷七 | 夘金木交加主防骨劳嗽之疾癸 | deferred 待补见证 | 四库两家同读「䈥」（筋），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 230807 | 卷七 | 气遇二运太岁防集在死絶衰息 | deferred 待补见证 | 四库两家同读「㑹」（會），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 231562 | 卷七 | 命带长生多者防有夀须本家纳 | deferred 待补见证 | 四库两家同读「㝎」（定），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 231925 | 卷七 | 来莫跨牛木通防蛇须逺走水逢 | deferred 待补见证 | 四库两家同读「䑕」（鼠），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 231941 | 卷七 | 堪愁土人更切防猪兎难保年光 | kept 保留 | 保留「防」，四库两家同读防、无已定位异读；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 232186 | 卷七 | 煞【歌曰】猪防无良犬战牛鸡 | deferred 待补见证 | 四库两家同读「䑕」（鼠），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 232236 | 卷七 | 主夀不长多遇防祸若身能尅煞 | deferred 待补见证 | 四库两家同读「䘮」（喪），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 232270 | 卷七 | 丙子亥子切须防庚辛巳午如风 | kept 保留 | 保留「防」，四库两家同读防、无已定位异读；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 232756 | 卷七 | 身五行命里皆防此遇者知非鹤 | kept 保留 | 保留「防」，四库两家同读防、无已定位异读；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 233403 | 卷七 | 不杂故主子贵防余仿此推
  | deferred 待补见证 | 四库两家同读「䕃」（蔭），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 233591 | 卷七 | 酉中财旺荣夫防子之造余仿此 | deferred 待补见证 | 四库两家同读「䕃」（蔭），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 234350 | 卷七 | 月甲木旺夘未防局偏正夫多子 | deferred 待补见证 | 四库两家同读「㑹」（會），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 234482 | 卷七 | 以癸为夫辰子防水夫多日时丙 | deferred 待补见证 | 四库两家同读「㑹」（會），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 234690 | 卷七 | 食神长生木地防局甲木归禄身 | deferred 待补见证 | 四库两家同读「㑹」（會），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 235844 | 卷七 | 运伤官见官又防丙煞尅身故有 | confirmed 定案 | 应改读「會」（四库字形 㑹），登记为未来应用候选；NiuTrans 同读「会」（side_anchored）；youngzs 未载；Banny-Gao（旁证） 同读「会」（side_anchored） |
| 237421 | 卷七 | 从人财衰运絶防出娘门身旺印 | deferred 待补见证 | 四库两家同读「㓜」（幼），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 237551 | 卷七 | 水火比刃遭刑防局掩玉骨于尘 | deferred 待补见证 | 四库两家同读「䘮」（喪），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 238198 | 卷七 | 偏房即为舞妓防合过盛不媒妁 | deferred 待补见证 | 四库两家同读「㑹」（會），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 238904 | 卷七 | 官临死絶知夫防枭遇驱除断子 | deferred 待补见证 | 四库两家同读「䘮」（喪），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 239945 | 卷七 | 宜官煞重逢须防滛乱娣妹透出 | kept 保留 | 保留「防」，四库两家同读防、无已定位异读；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 240039 | 卷七 | 无子伤官旺而防伤夫四柱不见 | deferred 待补见证 | 四库两家同读「㓜」（幼），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 240732 | 卷七 | 煞即为偏夫因防正官偏正交集 | deferred 待补见证 | 四库两家同读「㑹」（會），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 240764 | 卷七 | 但主欺夫夺权防持家性刚若日 | deferred 待补见证 | 四库两家同读「㑹」（會），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 241205 | 卷七 | 合贵此法人难防但以日为年此 | deferred 待补见证 | 四库两家同读「㑹」（會），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 241543 | 卷七 | 孤辰寡宿皆主防夫尅子
 凡 | deferred 待补见证 | 四库两家同读「䘮」（喪），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 241949 | 卷七 | 带惹为上等清防之格若贵人天 | deferred 待补见证 | 四库两家同读「㢘」（廉），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 242271 | 卷七 | 五分则近贵上防娼次则尼妾甚 | deferred 待补见证 | 四库两家同读「㳺」（遊），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 242735 | 卷七 | 建禄贵人者市防牙贩狼藉妇人 | deferred 待补见证 | 四库两家同读「㕓」（廛），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 243741 | 卷七 | 阳临四正益夫防子防持家
  | deferred 待补见证 | 四库两家同读「䕃」（蔭），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 243743 | 卷七 | 四正益夫防子防持家
 【禄 | deferred 待补见证 | 四库两家同读「㑹」（會），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 243751 | 卷七 | 家
 【禄马防于长生或带墓 | deferred 待补见证 | 四库两家同读「㑹」（會），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 244900 | 卷七 | 天使喽啰无半防却交顽福重千 | deferred 待补见证 | 四库两家同读「㸃」（點），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 245316 | 卷七 | 多生灾行建禄防旺地柱无官煞 | deferred 待补见证 | 四库两家同读「㑹」（會），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 245865 | 卷七 | 独守空闺哭子防
 【煞印相 | deferred 待补见证 | 四库两家同读「䘮」（喪），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 245945 | 卷七 | 两交差频向妆防理鬓斜若有官 | deferred 待补见证 | 四库两家同读「䑓」（臺），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载；紧邻左字在快照底本作「妝」、四库两家转录均作「粧」（同词异体），致标准侧翼全锚、单侧锚定与句段锚定全数失败；改以变体锚定定位（左翼仅紧邻一位放宽、余侧翼逐字全锚，match_mode=variant_anchored），四库两家同读「䑓」（臺）：「頻向粧䑓理鬢斜」与底本「頻向妝防理鬢斜」逐字对位仅此邻字异体一处；现代见证未载，候选只据四库两家登记 |
| 247070 | 卷七 | 干遇合方成吉防水重金又一评 | deferred 待补见证 | 四库两家同读「㑹」（會），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 249493 | 卷七 | 一位生三四位防失乳犯戊寅戊 | deferred 待补见证 | 四库两家同读「㓜」（幼），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 249527 | 卷七 | 背父生方不尅防四孟母先亡辰 | deferred 待补见证 | 四库两家同读「䧟」（陷），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 249740 | 卷七 | 或妨尅父母若防年运行财旺之 | deferred 待补见证 | 四库两家同读「㓜」（幼），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 249858 | 卷七 | 事三火隣家有防祸事或家中有 | deferred 待补见证 | 四库两家同读「䘮」（喪），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 250055 | 卷七 | 左眼圆小见前防后吊名曰防吊 | deferred 待补见证 | 四库两家同读「䘮」（喪），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 250060 | 卷七 | 前防后吊名曰防吊直帐多汤火 | deferred 待补见证 | 四库两家同读「䘮」（喪），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 250069 | 卷七 | 帐多汤火灾见防门吊客初生时 | deferred 待补见证 | 四库两家同读「䘮」（喪），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 250086 | 卷七 | 草之性生时见防门母氏难产及 | deferred 待补见证 | 四库两家同读「䘮」（喪），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 250123 | 卷七 | 势不行气不转防离父母如戊辰 | confirmed 定案 | 应改读「幼」（四库字形 㓜），登记为未来应用候选；NiuTrans 同读「幼」（side_anchored）；youngzs 同读「幼」（side_anchored）；Banny-Gao（旁证） 同读「幼」（side_anchored） |
| 250176 | 卷七 | 推
 胎中带防贞两位冲一位 | deferred 待补见证 | 四库两家同读「㢘」（廉），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载；位点语「胎中带㢘贞」为廉贞星名，四库两家读「㢘」，候选字词依四库字形登记为「廉」；现代见证未载 |
| 252612 | 卷七 | 求日妻家不是防无人便是自身 | deferred 待补见证 | 四库两家同读「䘮」（喪），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 252646 | 卷七 | 应须少日里当防几换妻
 妻 | kept 保留 | 保留「防」，四库两家同读防、无已定位异读；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 252754 | 卷七 | 分縁若己字落防或坐死絶之乡 | deferred 待补见证 | 四库两家同读「䧟」（陷），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 253118 | 卷七 | 若伤官成格如防贵刑合之例柱 | deferred 待补见证 | 四库两家同读「䑕」（鼠），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 253633 | 卷七 | 房兄弟无情被防欺如带比肩成 | deferred 待补见证 | 四库两家同读「㒺」（罔），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 253787 | 卷七 | 生丙戌丁壬妻防灵背父而生甲 | deferred 待补见证 | 四库两家同读「䕶」（護），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 253828 | 卷七 | 空印旺早年父防偏财临死絶煞 | deferred 待补见证 | 四库两家同读「䘮」（喪），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 253836 | 卷七 | 财临死絶煞宫防岁母离印绶逢 | deferred 待补见证 | 四库两家同读「㓜」（幼），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 254033 | 卷七 | 印绶被尅母亲防早桃花若坐煞 | deferred 待补见证 | 四库两家同读「䘮」（喪），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 254311 | 卷七 | 曰】年逢刃煞防年早䘮爹娘时 | confirmed 定案 | 应改读「幼」（四库字形 㓜），登记为未来应用候选；NiuTrans 同读「幼」（side_anchored）；youngzs 同读「幼」（side_anchored）；Banny-Gao（旁证） 同读「幼」（side_anchored） |
| 255513 | 卷七 | 妻是絶若无倾防也先亏日光华 | deferred 待补见证 | 四库两家同读「䧟」（陷），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 255579 | 卷七 | 坐华葢主妻不防不孝日坐驿马 | deferred 待补见证 | 四库两家同读「㢘」（廉），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 255601 | 卷七 | 行相尅亦主尅防辛酉日生尅妻 | deferred 待补见证 | 四库两家同读「䧟」（陷），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 255774 | 卷七 | 主得美妻多不防凡命以日之纳 | deferred 待补见证 | 四库两家同读「㢘」（廉），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 256186 | 卷七 | 宜生女生女则防妻如甲子金男 | deferred 待补见证 | 四库两家同读「䘮」（喪），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 256217 | 卷七 | 宜生男生男即防夫如甲子金女 | deferred 待补见证 | 四库两家同读「䘮」（喪），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 256997 | 卷七 | 多厄浮沉煞死防痢时坐本音墓 | deferred 待补见证 | 四库两家同读「㵼」（瀉），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 257500 | 卷七 | 

 三命通防卷七
<子部 | deferred 待补见证 | 四库两家同读「㑹」（會），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载；位点为卷七卷端页眉书名「三命通會」之「會」字位点（S3 语境作「三命通防卷七」），四库两家读「㑹」；现代见证未载 |

### 13.4 定案要点与 deferred 缺口形态

- **confirmed 4**：226603 膞（膊，《论疾病》两肩膊语，
  现代三家同读膊、四库字形异体以词为准）、235844 㑹
  （會，横夭少年语，NiuTrans 子集同读会）、250123 㓜
  （幼，《论小儿》语，现代三家同读幼）、254311 㓜
  （幼，《论六亲》语，现代三家同读幼）——均四库
  + 至少一独立现代方同读、读法只登记为未来 v2 应用
  候选，文本未动。
- **kept 8**：225847（尚义防有不善终之患，现代三家同
  读防）、225897（设施防有隂谋之患，现代三家同读防）、
  228279（疾难防）、231941（更切防）、232270（切须
  防）、232756（皆防）、239945（须防滛乱）、252646
  （当防）——四库同读防且无已定位异读，依 §2 不对称
  标准保留。
- **parallel 0**：本册无计方见证间的位点分歧；RD-12
  两处的四库与现代分歧（㿀对癍、䖝对茧）不属本册处置
  范围，只标记在案、归 P3。
- **deferred 61**：缺口形态为三命通会文本自身的第二
  个独立见证方未齐。字形分布：䘮 15、㑹 13（含 257500
  卷端页眉书名「三命通會」位点 1）、㓜 5、㢘 4、䧟 4、
  䑕 3、䕃 3、㵼 2、䈥 2、䑓 2（含 245945 变体锚定
  1），餘 㫖/㺯/㝎/㳺/㕓/㸃/㒺/䕶 各 1。升级路径
  同 §5：补齐现代全本转录（如 Wikisource michiboo
  《三命通会》对应卷次）或四库影印原叶定位后逐处升级。

### 13.5 累计进度与剩余分册计划（更新）

- 累计处置进度：**disposed 78/769**（confirmed 34、kept
  42、parallel 2）；deferred 437（节内 29 + 第二分册
  67 + 第三分册 112 + 第四分册 50 + 第五分册 118
  + 本册 61）；pending 254（其中 RD-12 位点 7 处只标记、
  处置随 P3）。
- 全卷累计：

| 卷 | 盘点 | confirmed | kept | parallel | deferred | pending |
|---|---|---|---|---|---|---|
| 卷首 | 1 | 0 | 0 | 1 | 0 | 0 |
| 卷一 | 10 | 0 | 8 | 0 | 2 | 0 |
| 卷二 | 34 | 2 | 2 | 1 | 29 | 0 |
| 卷三 | 50 | 1 | 6 | 0 | 43 | 0 |
| 卷四 | 118 | 2 | 4 | 0 | 112 | 0 |
| 卷五 | 89 | 14 | 8 | 0 | 65 | 2 |
| 卷六 | 142 | 11 | 6 | 0 | 125 | 0 |
| 卷七 | 75 | 4 | 8 | 0 | 61 | 2 |
| 卷八 | 61 | 0 | 0 | 0 | 0 | 61 |
| 卷九 | 94 | 0 | 0 | 0 | 0 | 94 |
| 卷十 | 26 | 0 | 0 | 0 | 0 | 26 |
| 卷十一 | 45 | 0 | 0 | 0 | 0 | 45 |
| 卷十二 | 24 | 0 | 0 | 0 | 0 | 24 |
| 合计 | 769 | 34 | 42 | 2 | 437 | 254 |

- 剩余分册（按卷序）：卷八 61、卷九 94、卷十 26、卷十一
  45、卷十二 24，另卷五 RD-12 两处、卷七 RD-12 两处随
  P3。本册同样只登记处置结论、零文本改动，
  `canonical_ready` 保持 false。

## 14. 第七分册（卷八节外 61 处，E0314）

### 14.1 范围与方法补记

- 范围：卷八节外 pending **61 处全部**逐处处置（一卷
  一册）；本册范围内**无 RD-12 标记位点**。
- 捕获式定位沿第二至第六分册，见证口径含 E0306 子集
  澄清。四库谱系：mikkokotila **61/61 全定位**、kanripo
  **43/61 定位**，定位处两家读法逐处完全一致；余 **18 处**
  （260367/261108/261144/266498/269097/274978/277068/
  279203/282829/283513/288515/289512/291757/292646/
  293451/294747/300970/302090）均位于各日时断 bracket
  仕宦名录清单内，kanripo 四库本（KR3g0042_008）该清单
  以栏式编排、项目干支次序与快照底本不同，标准捕获
  （侧翼全锚/脱字/单侧锚/句段锚定）全数未定位；逐字
  如实登记 `not_located`、候选只据 mikkokotila 一家、
  18 处一律 deferred（与第四分册 bracket 三处同型）。
- **本册未用变体锚定**：第六分册新设 `variant_anchored`
  形态仅限紧邻一位字形异体致标准锚定全灭时兜底，本册
  kanripo 缺位系清单次序差异、非邻字异体，不扩用；本册
  四库证据 match_mode 无 variant_anchored（测试在案）。
- 现代谱系计方见证本册实定位 **13 处**：NiuTrans 13 处、
  youngzs 三命子集 12 处，Banny-Gao 旁证 13 处。
  youngzs 全语料定位与三命子集定位全同，**本册无平行源
  文本旁证命中**（全册累计仍 26 处）。
- 两处计方谱系分歧并列不裁：272529 四库作「綵」而现代
  计方两家作「采」（「喝采」字级分歧）；277562 四库作
  「㑹」而现代计方两家作「合」（现代转录该句作「申月
  三合，合煞有印」，底本作「甲月三合㑹煞有印貴」）。

### 14.2 本册计数

| 卷 | 盘点 | confirmed | kept | parallel | deferred | pending |
|---|---|---|---|---|---|---|
| 卷八 | 61 | 5 | 7 | 2 | 47 | 0 |
| 本册合计（处置范围） | 61 | 5 | 7 | 2 | 47 | 0 |

### 14.3 本册处置（61 处逐处）

| S0 位点 | 卷 | 语境（S3 ±6） | 处置分类 | 结论与见证要点 |
|---|---|---|---|---|
| 257537 | 卷八 | 书
 三命通防卷八
 明  | deferred 待补见证 | 四库两家同读「㑹」（會），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载；位点为卷八卷端页眉书名「三命通會」之「會」字位点（S3 语境作「三命通防卷八」），四库两家读「㑹」；现代见证未载 |
| 258500 | 卷八 | 喜忌当通融活防【下同】
  | confirmed 定案 | 应改读「看」（四库字形 㸔），登记为未来应用候选；NiuTrans 同读「看」（side_anchored）；youngzs 同读「看」（side_anchored）；Banny-Gao（旁证） 同读「看」（side_anchored） |
| 260023 | 卷八 | 章丙午癸丑科防元榜眼江南人 | deferred 待补见证 | 四库两家同读「㑹」（會），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 260367 | 卷八 | 长庚 己巳钱防少卿南人丁丑 | deferred 待补见证 | 四库谱系仅 mikkokotila 一家读「䇿」（策），kanripo bracket 栏式编排致未定位，现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载；四库谱系仅 mikkokotila 一家定位：kanripo 四库本该位点所在 bracket 仕宦名录以栏式编排、项目干支次序与快照底本不同，标准捕获（侧翼全锚/脱字/单侧锚/句段锚定）均未定位，逐字如实登记未定位；候选读法只据一家登记，现代三家亦未载 |
| 261108 | 卷八 |  癸酉胡正蒙防元探花祭酒癸 | deferred 待补见证 | 四库谱系仅 mikkokotila 一家读「㑹」（會），kanripo bracket 栏式编排致未定位，现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载；四库谱系仅 mikkokotila 一家定位：kanripo 四库本该位点所在 bracket 仕宦名录以栏式编排、项目干支次序与快照底本不同，标准捕获（侧翼全锚/脱字/单侧锚/句段锚定）均未定位，逐字如实登记未定位；候选读法只据一家登记，现代三家亦未载 |
| 261130 | 卷八 |  【戊午林春防元部郎 庚子 | deferred 待补见证 | 四库两家同读「㑹」（會），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 261144 | 卷八 | 烃尚书乙卯 防州人 丙戌  | deferred 待补见证 | 四库谱系仅 mikkokotila 一家读「㤗」（泰），kanripo bracket 栏式编排致未定位，现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载；四库谱系仅 mikkokotila 一家定位：kanripo 四库本该位点所在 bracket 仕宦名录以栏式编排、项目干支次序与快照底本不同，标准捕获（侧翼全锚/脱字/单侧锚/句段锚定）均未定位，逐字如实登记未定位；候选读法只据一家登记，现代三家亦未载 |
| 261979 | 卷八 | 人壬戌陶望龄防元探花戊申  | deferred 待补见证 | 四库两家同读「㑹」（會），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 262582 | 卷八 | 巳丑年月虽贵防疾申子辰戌大 | kept 保留 | 保留「防」，四库两家同读防、无已定位异读；NiuTrans 同读「防」（full_flank）；youngzs 同读「防」（full_flank）；Banny-Gao（旁证） 同读「防」（full_flank） |
| 262695 | 卷八 | 子年月承袭父防主富
 【庚 | deferred 待补见证 | 四库两家同读「䕃」（蔭），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 263353 | 卷八 | 女命子周延儒防 丁卯进士甲 | deferred 待补见证 | 四库两家同读「㑹」（會），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 263422 | 卷八 |  【癸巳林应防尙书 丁卯呉 | deferred 待补见证 | 四库两家同读「㭿」（㭿），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载；位点字「㭿」为人名用字（林應㭿），四库两家同读「㭿」，其字本身即为候选词；现代见证未载 |
| 263635 | 卷八 | 身旺俱贵寅戌防伤制煞甲得倚 | confirmed 定案 | 应改读「會」（四库字形 㑹），登记为未来应用候选；NiuTrans 同读「会」（side_anchored）；youngzs 同读「会」（side_anchored）；Banny-Gao（旁证） 同读「会」（side_anchored） |
| 264033 | 卷八 |  戊申冯梦正防元 癸亥举人 | deferred 待补见证 | 四库两家同读「㑹」（會），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 266498 | 卷八 |  戊寅庄际昌防状己未 甲戌 | deferred 待补见证 | 四库谱系仅 mikkokotila 一家读「㑹」（會），kanripo bracket 栏式编排致未定位，现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载；四库谱系仅 mikkokotila 一家定位：kanripo 四库本该位点所在 bracket 仕宦名录以栏式编排、项目干支次序与快照底本不同，标准捕获（侧翼全锚/脱字/单侧锚/句段锚定）均未定位，逐字如实登记未定位；候选读法只据一家登记，现代三家亦未载 |
| 267631 | 卷八 | 少力花开结子防风文章显逹改 | kept 保留 | 保留「防」，四库两家同读防、无已定位异读；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 268463 | 卷八 | 但坐酉巳不成防贵别格论之】 | deferred 待补见证 | 四库两家同读「䑕」（鼠），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 269097 | 卷八 | 】
 【辛巳防魁 丁丑御史 | deferred 待补见证 | 四库谱系仅 mikkokotila 一家读「㑹」（會），kanripo bracket 栏式编排致未定位，现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载；四库谱系仅 mikkokotila 一家定位：kanripo 四库本该位点所在 bracket 仕宦名录以栏式编排、项目干支次序与快照底本不同，标准捕获（侧翼全锚/脱字/单侧锚/句段锚定）均未定位，逐字如实登记未定位；候选读法只据一家登记，现代三家亦未载 |
| 270849 | 卷八 | 酉通官贵 却防目疾减精神
 | kept 保留 | 保留「防」，四库两家同读防、无已定位异读；NiuTrans 同读「防」（full_flank）；youngzs 同读「防」（full_flank）；Banny-Gao（旁证） 同读「防」（full_flank） |
| 270885 | 卷八 | 人秀丽主贵却防目疾如不见化 | kept 保留 | 保留「防」，四库两家同读防、无已定位异读；NiuTrans 同读「防」（full_flank）；youngzs 同读「防」（full_flank）；Banny-Gao（旁证） 同读「防」（full_flank） |
| 271013 | 卷八 |  【庚午许獬防元编修丙戌】 | deferred 待补见证 | 四库两家同读「㑹」（會），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 271305 | 卷八 | 【丁卯唐顺之防元都宪 壬申 | deferred 待补见证 | 四库两家同读「㑹」（會），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 271629 | 卷八 | 】
 乙庚相防贵无疑 隂木 | deferred 待补见证 | 四库两家同读「㑹」（會），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 272104 | 卷八 | 
 【癸酉陆防翰林 癸亥佥 | deferred 待补见证 | 四库两家同读「㤗」（泰），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 272529 | 卷八 | 怀富贵时人喝防
 六乙日午 | parallel 并列 | 四库两家同读「綵」（綵）与现代计方两家同读「采」分歧，并列不裁；NiuTrans 同读「采」（side_anchored）；youngzs 同读「采」（side_anchored）；Banny-Gao（旁证） 同读「采」（side_anchored）；四库两家同读「綵」；现代计方两家（NiuTrans 与 youngzs 三命子集）同读「采」——「喝采」一语四库作綵、现代作采，字级分歧、并列不裁；Banny-Gao 旁证同读「采」 |
| 273955 | 卷八 | 贵己酉丑贵中防凶午未纯吉亥 | kept 保留 | 保留「防」，四库两家同读防、无已定位异读；NiuTrans 同读「防」（side_anchored）；youngzs 同读「防」（side_anchored）；Banny-Gao（旁证） 同读「防」（side_anchored） |
| 274978 | 卷八 |  乙亥刘康祉防魁丙辰 乙巳 | deferred 待补见证 | 四库谱系仅 mikkokotila 一家读「㑹」（會），kanripo bracket 栏式编排致未定位，现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载；四库谱系仅 mikkokotila 一家定位：kanripo 四库本该位点所在 bracket 仕宦名录以栏式编排、项目干支次序与快照底本不同，标准捕获（侧翼全锚/脱字/单侧锚/句段锚定）均未定位，逐字如实登记未定位；候选读法只据一家登记，现代三家亦未载 |
| 276317 | 卷八 | 金局行水运者防目疾四柱见财 | kept 保留 | 保留「防」，四库两家同读防、无已定位异读；NiuTrans 同读「防」（full_flank）；youngzs 同读「防」（full_flank）；Banny-Gao（旁证） 同读「防」（full_flank） |
| 277068 | 卷八 | 可量贵人相聚防 富贵坐朝堂 | deferred 待补见证 | 四库谱系仅 mikkokotila 一家读「㑹」（會），kanripo bracket 栏式编排致未定位，现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载；四库谱系仅 mikkokotila 一家定位：kanripo 四库本该位点所在 bracket 仕宦名录以栏式编排、项目干支次序与快照底本不同，标准捕获（侧翼全锚/脱字/单侧锚/句段锚定）均未定位，逐字如实登记未定位；候选读法只据一家登记，现代三家亦未载 |
| 277313 | 卷八 |  【癸卯董玘防元侍郎 丁未 | deferred 待补见证 | 四库两家同读「㑹」（會），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 277562 | 卷八 | 中贵甲月三合防煞有印贵忌己 | parallel 并列 | 四库两家同读「㑹」（會）与现代计方两家同读「合」分歧，并列不裁；NiuTrans 同读「合」（side_anchored）；youngzs 同读「合」（side_anchored）；Banny-Gao（旁证） 同读「合」（side_anchored）；四库两家同读「㑹」（會）；现代计方两家同读「合」——现代转录该句作「申月三合，合煞有印」（底本作「甲月三合㑹煞有印貴」），位点字分歧、并列不裁；Banny-Gao 旁证同读「合」 |
| 278647 | 卷八 | 子辰㑹官寅卯防印俱吉
 【 | confirmed 定案 | 应改读「會」（四库字形 㑹），登记为未来应用候选；NiuTrans 同读「会」（side_anchored）；youngzs 同读「会」（side_anchored）；Banny-Gao（旁证） 同读「会」（side_anchored） |
| 278876 | 卷八 | 刼财算来须有防害六亲真假少 | deferred 待补见证 | 四库两家同读「㱔」（些），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载；四库两家同读「㱔」（些，「須有㱔害」）；现代见证未载 |
| 279203 | 卷八 | 子 乙亥壬辰防财 庚辰千户 | deferred 待补见证 | 四库谱系仅 mikkokotila 一家读「䕃」（蔭），kanripo bracket 栏式编排致未定位，现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载；四库谱系仅 mikkokotila 一家定位：kanripo 四库本该位点所在 bracket 仕宦名录以栏式编排、项目干支次序与快照底本不同，标准捕获（侧翼全锚/脱字/单侧锚/句段锚定）均未定位，逐字如实登记未定位；候选读法只据一家登记，现代三家亦未载 |
| 280259 | 卷八 | 癸酉丁酉陈栋防元乙巳 探花 | deferred 待补见证 | 四库两家同读「㑹」（會），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 282582 | 卷八 |  【壬辰林廷防尚书 己卯大 | deferred 待补见证 | 四库两家同读「㭿」（㭿），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载；位点字「㭿」为人名用字（林廷㭿），四库两家同读「㭿」，其字本身即为候选词；现代见证未载 |
| 282829 | 卷八 | 眼 壬子呉黙防元癸酉 阁老 | deferred 待补见证 | 四库谱系仅 mikkokotila 一家读「㑹」（會），kanripo bracket 栏式编排致未定位，现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载；四库谱系仅 mikkokotila 一家定位：kanripo 四库本该位点所在 bracket 仕宦名录以栏式编排、项目干支次序与快照底本不同，标准捕获（侧翼全锚/脱字/单侧锚/句段锚定）均未定位，逐字如实登记未定位；候选读法只据一家登记，现代三家亦未载 |
| 283464 | 卷八 | 子辰㑹官亥卯防印俱贵
 【 | confirmed 定案 | 应改读「會」（四库字形 㑹），登记为未来应用候选；NiuTrans 同读「会」（side_anchored）；youngzs 同读「会」（side_anchored）；Banny-Gao（旁证） 同读「会」（side_anchored） |
| 283476 | 卷八 | 【壬午明光宗防昌帝 壬子太 | deferred 待补见证 | 四库两家同读「㤗」（泰），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 283513 | 卷八 | 人 甲辰王一防尚书丙午 辛 | deferred 待补见证 | 四库谱系仅 mikkokotila 一家读「䕫」（夔），kanripo bracket 栏式编排致未定位，现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载；四库谱系仅 mikkokotila 一家定位：kanripo 四库本该位点所在 bracket 仕宦名录以栏式编排、项目干支次序与快照底本不同，标准捕获（侧翼全锚/脱字/单侧锚/句段锚定）均未定位，逐字如实登记未定位；候选读法只据一家登记，现代三家亦未载 |
| 283949 | 卷八 | 【庚子田一儁防元 丁卯戴士 | deferred 待补见证 | 四库两家同读「㑹」（會），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 284528 | 卷八 | 年月大贵有辰防子有丑防酉俱 | deferred 待补见证 | 四库两家同读「㑹」（會），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 284532 | 卷八 | 有辰防子有丑防酉俱以贵论
 | deferred 待补见证 | 四库两家同读「㑹」（會），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 287004 | 卷八 | 戌女命子韩敬防状癸未 甲子 | deferred 待补见证 | 四库两家同读「㑹」（會），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 288515 | 卷八 | 
 【乙亥万防侍郎 乙卯富 | deferred 待补见证 | 四库谱系仅 mikkokotila 一家读「㳟」（恭），kanripo bracket 栏式编排致未定位，现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载；位点为人名「萬㳟」之「㳟」字（恭之异体）；四库谱系仅 mikkokotila 一家定位：kanripo 四库本该位点所在 bracket 仕宦名录以栏式编排、项目干支次序与快照底本不同，标准捕获（侧翼全锚/脱字/单侧锚/句段锚定）均未定位，逐字如实登记未定位；候选读法只据一家登记，现代三家亦未载 |
| 289183 | 卷八 | 壬戌】
 【防铁成金局 时 | deferred 待补见证 | 四库两家同读「㸃」（點），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 289512 | 卷八 |  庚戌萧良有防元榜眼癸巳  | deferred 待补见证 | 四库谱系仅 mikkokotila 一家读「㑹」（會），kanripo bracket 栏式编排致未定位，现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载；四库谱系仅 mikkokotila 一家定位：kanripo 四库本该位点所在 bracket 仕宦名录以栏式编排、项目干支次序与快照底本不同，标准捕获（侧翼全锚/脱字/单侧锚/句段锚定）均未定位，逐字如实登记未定位；候选读法只据一家登记，现代三家亦未载 |
| 289737 | 卷八 | 辛卯 乙未 防状
 丁酉唐 | deferred 待补见证 | 四库两家同读「㑹」（會），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 289986 | 卷八 | 耗财粮守祖须防破荡父母鴈行 | kept 保留 | 保留「防」，四库两家同读防、无已定位异读；NiuTrans 同读「防」（side_anchored）；youngzs 未载；Banny-Gao（旁证） 同读「防」（side_anchored） |
| 291757 | 卷八 | 士 辛酉金逹防元探花乙巳  | deferred 待补见证 | 四库谱系仅 mikkokotila 一家读「㑹」（會），kanripo bracket 栏式编排致未定位，现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载；四库谱系仅 mikkokotila 一家定位：kanripo 四库本该位点所在 bracket 仕宦名录以栏式编排、项目干支次序与快照底本不同，标准捕获（侧翼全锚/脱字/单侧锚/句段锚定）均未定位，逐字如实登记未定位；候选读法只据一家登记，现代三家亦未载 |
| 292646 | 卷八 |  辛亥邹守益防元尚书己丑  | deferred 待补见证 | 四库谱系仅 mikkokotila 一家读「㑹」（會），kanripo bracket 栏式编排致未定位，现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载；四库谱系仅 mikkokotila 一家定位：kanripo 四库本该位点所在 bracket 仕宦名录以栏式编排、项目干支次序与快照底本不同，标准捕获（侧翼全锚/脱字/单侧锚/句段锚定）均未定位，逐字如实登记未定位；候选读法只据一家登记，现代三家亦未载 |
| 293312 | 卷八 | 亥卯㑹未子辰防申俱以贵论
 | confirmed 定案 | 应改读「會」（四库字形 㑹），登记为未来应用候选；NiuTrans 同读「会」（side_anchored）；youngzs 同读「会」（side_anchored）；Banny-Gao（旁证） 同读「会」（side_anchored） |
| 293451 | 卷八 | 贵
 壬子大防 丙午佥宪  | deferred 待补见证 | 四库谱系仅 mikkokotila 一家读「㕘」（參），kanripo bracket 栏式编排致未定位，现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载；位点语「大㕘」（參）为明代大參之称；四库谱系仅 mikkokotila 一家定位：kanripo 四库本该位点所在 bracket 仕宦名录以栏式编排、项目干支次序与快照底本不同，标准捕获（侧翼全锚/脱字/单侧锚/句段锚定）均未定位，逐字如实登记未定位；候选读法只据一家登记，现代三家亦未载 |
| 294653 | 卷八 |  【戊申张治防元阁老 戊戌 | deferred 待补见证 | 四库两家同读「㑹」（會），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 294747 | 卷八 | 丙辰 至侍郎防二子 戊辰】 | deferred 待补见证 | 四库谱系仅 mikkokotila 一家读「䕃」（蔭），kanripo bracket 栏式编排致未定位，现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载；四库谱系仅 mikkokotila 一家定位：kanripo 四库本该位点所在 bracket 仕宦名录以栏式编排、项目干支次序与快照底本不同，标准捕获（侧翼全锚/脱字/单侧锚/句段锚定）均未定位，逐字如实登记未定位；候选读法只据一家登记，现代三家亦未载 |
| 297467 | 卷八 | 忌年月通融活防更参诸命则得 | deferred 待补见证 | 四库两家同读「㸔」（看），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 300970 | 卷八 | 
 【风云聚防局 不要见官 | deferred 待补见证 | 四库谱系仅 mikkokotila 一家读「㑹」（會），kanripo bracket 栏式编排致未定位，现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载；四库谱系仅 mikkokotila 一家定位：kanripo 四库本该位点所在 bracket 仕宦名录以栏式编排、项目干支次序与快照底本不同，标准捕获（侧翼全锚/脱字/单侧锚/句段锚定）均未定位，逐字如实登记未定位；候选读法只据一家登记，现代三家亦未载 |
| 301363 | 卷八 | 午庚子李同芳防魁己丑】
  | deferred 待补见证 | 四库两家同读「㑹」（會），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 302090 | 卷八 |  庚子李多见防魁吏部甲午  | deferred 待补见证 | 四库谱系仅 mikkokotila 一家读「㑹」（會），kanripo bracket 栏式编排致未定位，现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载；四库谱系仅 mikkokotila 一家定位：kanripo 四库本该位点所在 bracket 仕宦名录以栏式编排、项目干支次序与快照底本不同，标准捕获（侧翼全锚/脱字/单侧锚/句段锚定）均未定位，逐字如实登记未定位；候选读法只据一家登记，现代三家亦未载 |
| 302489 | 卷八 | 重谢花开结菓防亲鴈行夭孤自 | deferred 待补见证 | 四库两家同读「䨇」（雙），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 305444 | 卷八 | 

 三命通防卷八
<子部 | deferred 待补见证 | 四库两家同读「㑹」（會），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载；位点为卷八卷末页眉书名「三命通會」之「會」字位点（S3 语境作「三命通防卷八」），四库两家读「㑹」；现代见证未载 |

### 14.4 定案要点与 deferred 缺口形态

- **confirmed 5**：258500 㸔（看，「通融活㸔」语，现代
  三家同读看）、263635 㑹（會，寅戌㑹伤语）、278647
  㑹（會，子辰㑹官语）、283464 㑹（會，子辰㑹官语）、
  293312 㑹（會，亥卯㑹未语）——均四库 + 至少一独立
  现代方同读、读法只登记为未来 v2 应用候选，文本未动。
- **kept 7**：262582（贵防疾，现代三家同读防）、267631
  （花开结子防风，固定语汇、现代未载，依 §2 不对称标准
  保留）、270849/270885（却防目疾）、273955（防凶）、
  276317（防目疾）、289986（须防破荡）——四库同读防
  且无已定位异读。
- **parallel 2**：272529（綵对采）、277562（㑹对合），
  双方读法并列登记、不裁（见 §14.1）。
- **deferred 47**：字形分布：㑹 30（含 257537/305444
  卷端卷末页眉书名「三命通會」位点 2）、㤗 3、䕃 3、
  㭿 2（人名用字，其字本身即为候选词）、䇿/䑕/㱔/䕫/
  㳟/㸃/㕘/㸔/䨇 各 1。其中 18 处四库谱系亦仅
  mikkokotila 一家定位（见 §14.1），余 29 处缺口为三命
  通会文本自身的第二独立见证方未齐。升级路径同 §5：
  补齐现代全本转录（如 Wikisource michiboo《三命通会》
  对应卷次）、kanripo 对应原叶定位或四库影印原叶后
  逐处升级。

### 14.5 累计进度与剩余分册计划（更新）

- 累计处置进度：**disposed 92/769**（confirmed 39、kept
  49、parallel 4）；deferred 484（节内 29 + 第二分册
  67 + 第三分册 112 + 第四分册 50 + 第五分册 118
  + 第六分册 61 + 本册 47）；pending 193（其中 RD-12
  位点 4 处只标记、处置随 P3）。
- 全卷累计：

| 卷 | 盘点 | confirmed | kept | parallel | deferred | pending |
|---|---|---|---|---|---|---|
| 卷首 | 1 | 0 | 0 | 1 | 0 | 0 |
| 卷一 | 10 | 0 | 8 | 0 | 2 | 0 |
| 卷二 | 34 | 2 | 2 | 1 | 29 | 0 |
| 卷三 | 50 | 1 | 6 | 0 | 43 | 0 |
| 卷四 | 118 | 2 | 4 | 0 | 112 | 0 |
| 卷五 | 89 | 14 | 8 | 0 | 65 | 2 |
| 卷六 | 142 | 11 | 6 | 0 | 125 | 0 |
| 卷七 | 75 | 4 | 8 | 0 | 61 | 2 |
| 卷八 | 61 | 5 | 7 | 2 | 47 | 0 |
| 卷九 | 94 | 0 | 0 | 0 | 0 | 94 |
| 卷十 | 26 | 0 | 0 | 0 | 0 | 26 |
| 卷十一 | 45 | 0 | 0 | 0 | 0 | 45 |
| 卷十二 | 24 | 0 | 0 | 0 | 0 | 24 |
| 合计 | 769 | 39 | 49 | 4 | 484 | 193 |

- 剩余分册（按卷序）：卷九 94、卷十 26、卷十一 45、卷十二
  24，另卷五 RD-12 两处、卷七 RD-12 两处随 P3。本册同样
  只登记处置结论、零文本改动，`canonical_ready` 保持
  false。

## 15. 第八分册（卷九节外 94 处，E0316）

### 15.1 范围与方法补记

- 范围：卷九 pending **94 处全部**逐处处置（一卷
  一册）；本册范围内**无 RD-12 标记位点**。
- 捕获式定位沿第二至第七分册，见证口径含 E0306 子集
  澄清。四库谱系：mikkokotila **94/94 全定位**、kanripo
  **62/94 定位**，定位处两家读法逐处完全一致；余 **32 处**
  （306793/309094/309452/315277/318098/320174/321649/
  322401/322977/322982/323349/325074/325426/325758/
  326785/326924/327205/332658/332813/334348/334733/
  334739/335989/338002/339003/340074/342584/342858/
  343797/345811/347559/349212）kanripo 未定位，多位于
  各日时断 bracket 名录条目内，标准捕获（侧翼全锚/脱字/
  单侧锚/句段锚定）全数未定位；逐字如实登记
  `not_located`、候选只据 mikkokotila 一家、32 处一律
  deferred。
- **本册未用变体锚定**：第六分册新设 `variant_anchored`
  形态仅限紧邻一位字形异体致标准锚定全灭时兜底，本册
  kanripo 缺位系名录条目定位缺位、非邻字异体，不扩用；
  本册四库证据 match_mode 无 variant_anchored（测试在案）。
- 现代谱系计方见证本册实定位 **20 处**：NiuTrans 20 处、
  youngzs 三命子集 20 处，Banny-Gao 旁证 20 处。另
  324699/324706 两处 youngzs 全语料仅于其《五行精纪》
  转录（第十一卷释日时凶中凶格）命中「凶」、与四库同读，
  登记 `attested_parallel_source` 旁证、不计现代方，两处
  一律 deferred；平行源旁证累计 26 增至 **28 处**。
- 本册**无计方谱系分歧**：已定位的计方现代见证与四库
  读法逐处同读，并列累计仍 4 处。

### 15.2 本册计数

| 卷 | 盘点 | confirmed | kept | parallel | deferred | pending |
|---|---|---|---|---|---|---|
| 卷九 | 94 | 16 | 7 | 0 | 71 | 0 |
| 本册合计（处置范围） | 94 | 16 | 7 | 0 | 71 | 0 |

### 15.3 本册处置（94 处逐处）

| S0 位点 | 卷 | 语境（S3 ±6） | 处置分类 | 结论与见证要点 |
|---|---|---|---|---|
| 306793 | 卷九 | 右都 丙戌鄕防丁未 辛卯】 | deferred 待补见证 | 四库谱系仅 mikkokotila 一家读「㐫」（凶），kanripo 未定位（多位于 bracket 名录条目），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载；四库谱系仅 mikkokotila 一家定位：kanripo 未定位（该位点多位于日时断 bracket 名录条目内），逐字如实登记未定位；候选读法只据一家登记，现代三家亦未载 |
| 308023 | 卷九 | 再遇流年冲运防死
 【乙巳 | confirmed 定案 | 应改读「凶」（四库字形 㐫），登记为未来应用候选；NiuTrans 同读「凶」（side_anchored）；youngzs 同读「凶」（side_anchored）；Banny-Gao（旁证） 同读「凶」（side_anchored） |
| 308097 | 卷九 | 三辛卯 命通防原本即此公所 | deferred 待补见证 | 四库两家同读「㑹」（會），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 308163 | 卷九 | 制化亦贵否则防夭
 【癸卯 | confirmed 定案 | 应改读「凶」（四库字形 㐫），登记为未来应用候选；NiuTrans 同读「凶」（side_anchored）；youngzs 同读「凶」（side_anchored）；Banny-Gao（旁证） 同读「凶」（side_anchored） |
| 308909 | 卷九 | 寅李廷机解元防元榜眼 戊寅 | deferred 待补见证 | 四库两家同读「㑹」（會），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 309094 | 卷九 | 壬午 丙戌年防死 甲子中书 | deferred 待补见证 | 四库谱系仅 mikkokotila 一家读「㐫」（凶），kanripo 未定位（多位于 bracket 名录条目），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载；四库谱系仅 mikkokotila 一家定位：kanripo 未定位（该位点多位于日时断 bracket 名录条目内），逐字如实登记未定位；候选读法只据一家登记，现代三家亦未载 |
| 309452 | 卷九 | 人 辛卯锦衣防死乙未 丁酉 | deferred 待补见证 | 四库谱系仅 mikkokotila 一家读「㐫」（凶），kanripo 未定位（多位于 bracket 名录条目），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载；四库谱系仅 mikkokotila 一家定位：kanripo 未定位（该位点多位于日时断 bracket 名录条目内），逐字如实登记未定位；候选读法只据一家登记，现代三家亦未载 |
| 310836 | 卷九 | 贵【一云】刑防
 【丁未举 | deferred 待补见证 | 四库两家同读「㐫」（凶），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 311149 | 卷九 | 俱吉【一云】防刑后旺
 【 | confirmed 定案 | 应改读「凶」（四库字形 㐫），登记为未来应用候选；NiuTrans 同读「凶」（side_anchored）；youngzs 同读「凶」（side_anchored）；Banny-Gao（旁证） 同读「凶」（side_anchored） |
| 311221 | 卷九 | 【一云】贵中防失
 【甲子 | confirmed 定案 | 应改读「凶」（四库字形 㐫），登记为未来应用候选；NiuTrans 同读「凶」（side_anchored）；youngzs 同读「凶」（side_anchored）；Banny-Gao（旁证） 同读「凶」（side_anchored） |
| 311961 | 卷九 | 
 日干是巳防申时 无破无 | deferred 待补见证 | 四库两家同读「㑹」（會），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 313059 | 卷九 | 未日甲戌时尅防遭刑寅午年月 | deferred 待补见证 | 四库两家同读「䧟」（陷），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 313709 | 卷九 | 戊午 丁亥 防年不免壬辰贫 | deferred 待补见证 | 四库两家同读「㐫」（凶），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 314836 | 卷九 | 㐫己丑月破败防
 【丙戌大 | deferred 待补见证 | 四库两家同读「㐫」（凶），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 314956 | 卷九 | 忌己巳月破祖防己亥月被刼盗 | confirmed 定案 | 应改读「凶」（四库字形 㐫），登记为未来应用候选；NiuTrans 同读「凶」（full_flank）；youngzs 同读「凶」（full_flank）；Banny-Gao（旁证） 同读「凶」（full_flank） |
| 314963 | 卷九 | 己亥月被刼盗防癸丑月孤
  | confirmed 定案 | 应改读「凶」（四库字形 㐫），登记为未来应用候选；NiuTrans 同读「凶」（side_anchored）；youngzs 同读「凶」（side_anchored）；Banny-Gao（旁证） 同读「凶」（side_anchored） |
| 315136 | 卷九 | 刑己丑月破败防戊戌月恶死
 | confirmed 定案 | 应改读「凶」（四库字形 㐫），登记为未来应用候选；NiuTrans 同读「凶」（side_anchored）；youngzs 同读「凶」（side_anchored）；Banny-Gao（旁证） 同读「凶」（side_anchored） |
| 315277 | 卷九 | 跃到天津运至防成吉 时来不 | deferred 待补见证 | 四库谱系仅 mikkokotila 一家读「㐫」（凶），kanripo 未定位（多位于 bracket 名录条目），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载；四库谱系仅 mikkokotila 一家定位：kanripo 未定位（该位点多位于日时断 bracket 名录条目内），逐字如实登记未定位；候选读法只据一家登记，现代三家亦未载 |
| 316742 | 卷九 | 遇亡刼尅身则防【甲寅祭酒  | deferred 待补见证 | 四库两家同读「㐫」（凶），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 316806 | 卷九 | 丑 庚寅辛巳防死丙申】
  | deferred 待补见证 | 四库两家同读「㐫」（凶），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 318003 | 卷九 | 片顽金为盗遭防宜矣】
 【 | deferred 待补见证 | 四库两家同读「㐫」（凶），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 318098 | 卷九 | 
 壬戌大富防死 己未刘廷 | deferred 待补见证 | 四库谱系仅 mikkokotila 一家读「㐫」（凶），kanripo 未定位（多位于 bracket 名录条目），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载；四库谱系仅 mikkokotila 一家定位：kanripo 未定位（该位点多位于日时断 bracket 名录条目内），逐字如实登记未定位；候选读法只据一家登记，现代三家亦未载 |
| 320174 | 卷九 | 己酉贫 庚子防丙子 庚辰】 | deferred 待补见证 | 四库谱系仅 mikkokotila 一家读「㐫」（凶），kanripo 未定位（多位于 bracket 名录条目），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载；四库谱系仅 mikkokotila 一家定位：kanripo 未定位（该位点多位于日时断 bracket 名录条目内），逐字如实登记未定位；候选读法只据一家登记，现代三家亦未载 |
| 321164 | 卷九 | 品贵夘刑子多防
 【庚戌孔 | deferred 待补见证 | 四库两家同读「㐫」（凶），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 321649 | 卷九 | 元 庚寅上郎防死癸夘 甲申 | deferred 待补见证 | 四库谱系仅 mikkokotila 一家读「㐫」（凶），kanripo 未定位（多位于 bracket 名录条目），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载；四库谱系仅 mikkokotila 一家定位：kanripo 未定位（该位点多位于日时断 bracket 名录条目内），逐字如实登记未定位；候选读法只据一家登记，现代三家亦未载 |
| 322031 | 卷九 | 一云】破祖刑防
 【壬申京 | deferred 待补见证 | 四库两家同读「㐫」（凶），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 322065 | 卷九 | 寅午戌吉申子防暴
 【癸巳 | confirmed 定案 | 应改读「凶」（四库字形 㐫），登记为未来应用候选；NiuTrans 同读「凶」（side_anchored）；youngzs 同读「凶」（side_anchored）；Banny-Gao（旁证） 同读「凶」（side_anchored） |
| 322401 | 卷九 | 尚书 乙丑沈防阁老乙丑 庚 | deferred 待补见证 | 四库谱系仅 mikkokotila 一家读「㴶」（㴶），kanripo 未定位（多位于 bracket 名录条目），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载；位点字「㴶」为人名用字（沈㴶），四库谱系仅 mikkokotila 一家读「㴶」，其字本身即为候选词；四库谱系仅 mikkokotila 一家定位：kanripo 未定位（该位点多位于日时断 bracket 名录条目内），逐字如实登记未定位；候选读法只据一家登记，现代三家亦未载 |
| 322525 | 卷九 | 凡事后吉先多防入品显达之命 | deferred 待补见证 | 四库两家同读「㐫」（凶），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 322739 | 卷九 | 辰魏允中解元防魁 甲子常少 | deferred 待补见证 | 四库两家同读「㑹」（會），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 322977 | 卷九 |  庚辰 癸亥防死丙戌 防死 | deferred 待补见证 | 四库谱系仅 mikkokotila 一家读「㐫」（凶），kanripo 未定位（多位于 bracket 名录条目），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载；四库谱系仅 mikkokotila 一家定位：kanripo 未定位（该位点多位于日时断 bracket 名录条目内），逐字如实登记未定位；候选读法只据一家登记，现代三家亦未载 |
| 322982 | 卷九 | 亥防死丙戌 防死无子 乙酉 | deferred 待补见证 | 四库谱系仅 mikkokotila 一家读「㐫」（凶），kanripo 未定位（多位于 bracket 名录条目），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载；四库谱系仅 mikkokotila 一家定位：kanripo 未定位（该位点多位于日时断 bracket 名录条目内），逐字如实登记未定位；候选读法只据一家登记，现代三家亦未载 |
| 323287 | 卷九 | 【丙戌蔡茂春防元 丁亥廉使 | deferred 待补见证 | 四库两家同读「㑹」（會），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 323349 | 卷九 | 申太守 丙寅防死乙夘 辛丑 | deferred 待补见证 | 四库谱系仅 mikkokotila 一家读「㐫」（凶），kanripo 未定位（多位于 bracket 名录条目），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载；四库谱系仅 mikkokotila 一家定位：kanripo 未定位（该位点多位于日时断 bracket 名录条目内），逐字如实登记未定位；候选读法只据一家登记，现代三家亦未载 |
| 324615 | 卷九 | 癸丑月破败孤防
 【乙亥孙 | deferred 待补见证 | 四库两家同读「㐫」（凶），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 324699 | 卷九 | 忌辛夘月父母防死辛巳月大破 | deferred 待补见证 | 四库两家同读「㐫」（凶），现代独立见证未齐，不裁；NiuTrans 未载；youngzs《五行精纪》平行源文本同读「凶」（不计现代方）；Banny-Gao（旁证） 未载；四库两家同读「㐫」（凶）；youngzs 全语料仅于其《五行精纪》转录（第十一卷释日时凶中凶格）同读「凶」，属被引源文本、登记 attested_parallel_source 旁证、不计现代方（E0306 口径，旁证同读亦不计方）；计方现代见证（三命子集）未载 |
| 324706 | 卷九 | 死辛巳月大破防壬申月尸不全 | deferred 待补见证 | 四库两家同读「㐫」（凶），现代独立见证未齐，不裁；NiuTrans 未载；youngzs《五行精纪》平行源文本同读「凶」（不计现代方）；Banny-Gao（旁证） 未载；四库两家同读「㐫」（凶）；youngzs 全语料仅于其《五行精纪》转录（第十一卷释日时凶中凶格）同读「凶」，属被引源文本、登记 attested_parallel_source 旁证、不计现代方（E0306 口径，旁证同读亦不计方）；计方现代见证（三命子集）未载 |
| 324983 | 卷九 | 月孤㓙癸丑月防刑死
 【己 | confirmed 定案 | 应改读「凶」（四库字形 㐫），登记为未来应用候选；NiuTrans 同读「凶」（side_anchored）；youngzs 同读「凶」（side_anchored）；Banny-Gao（旁证） 同读「凶」（side_anchored） |
| 325074 | 卷九 | 
 甲戌太守防死无子 壬寅 | deferred 待补见证 | 四库谱系仅 mikkokotila 一家读「㓙」（凶），kanripo 未定位（多位于 bracket 名录条目），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载；四库谱系仅 mikkokotila 一家定位：kanripo 未定位（该位点多位于日时断 bracket 名录条目内），逐字如实登记未定位；候选读法只据一家登记，现代三家亦未载 |
| 325173 | 卷九 | 辛巳月大败祖防庚戌月防死【 | deferred 待补见证 | 四库两家同读「㓙」（凶），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载；四库两家同读「㓙」（凶之异体）；紧邻位点 325177 四库作「㐫」，异形同词；现代见证未载本处 |
| 325177 | 卷九 | 败祖防庚戌月防死【甲午侍郎 | confirmed 定案 | 应改读「凶」（四库字形 㐫），登记为未来应用候选；NiuTrans 同读「凶」（side_anchored）；youngzs 同读「凶」（side_anchored）；Banny-Gao（旁证） 同读「凶」（side_anchored） |
| 325426 | 卷九 | 丙戌贵 己丑防癸亥 辛巳  | deferred 待补见证 | 四库谱系仅 mikkokotila 一家读「㐫」（凶），kanripo 未定位（多位于 bracket 名录条目），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载；四库谱系仅 mikkokotila 一家定位：kanripo 未定位（该位点多位于日时断 bracket 名录条目内），逐字如实登记未定位；候选读法只据一家登记，现代三家亦未载 |
| 325758 | 卷九 | 申大参 甲申防死辛丑 元  | deferred 待补见证 | 四库谱系仅 mikkokotila 一家读「㐫」（凶），kanripo 未定位（多位于 bracket 名录条目），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载；四库谱系仅 mikkokotila 一家定位：kanripo 未定位（该位点多位于日时断 bracket 名录条目内），逐字如实登记未定位；候选读法只据一家登记，现代三家亦未载 |
| 326785 | 卷九 | 酉进士 辛酉防死 壬寅依覔 | deferred 待补见证 | 四库谱系仅 mikkokotila 一家读「㐫」（凶），kanripo 未定位（多位于 bracket 名录条目），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载；四库谱系仅 mikkokotila 一家定位：kanripo 未定位（该位点多位于日时断 bracket 名录条目内），逐字如实登记未定位；候选读法只据一家登记，现代三家亦未载 |
| 326924 | 卷九 | 戌极富 己亥防死丁酉 乙夘 | deferred 待补见证 | 四库谱系仅 mikkokotila 一家读「㐫」（凶），kanripo 未定位（多位于 bracket 名录条目），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载；四库谱系仅 mikkokotila 一家定位：kanripo 未定位（该位点多位于日时断 bracket 名录条目内），逐字如实登记未定位；候选读法只据一家登记，现代三家亦未载 |
| 327205 | 卷九 |  壬辰查布政防死 甲申御史 | deferred 待补见证 | 四库谱系仅 mikkokotila 一家读「㐫」（凶），kanripo 未定位（多位于 bracket 名录条目），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载；四库谱系仅 mikkokotila 一家定位：kanripo 未定位（该位点多位于日时断 bracket 名录条目内），逐字如实登记未定位；候选读法只据一家登记，现代三家亦未载 |
| 327474 | 卷九 | 未辰运戊午年防死甲戌 丙申 | deferred 待补见证 | 四库两家同读「㐫」（凶），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 327805 | 卷九 | 丑钱四窓御史防死 丁亥范应 | deferred 待补见证 | 四库两家同读「㐫」（凶），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 328001 | 卷九 | 
 四柱火虚防尅害 九流技 | kept 保留 | 保留「防」，四库两家同读防、无已定位异读；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 329898 | 卷九 | 】
 【壬辰防死乙巳】
  | deferred 待补见证 | 四库两家同读「㓙」（凶），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 330666 | 卷九 | 太旺财官无气防夭
 【己巳 | confirmed 定案 | 应改读「凶」（四库字形 㐫），登记为未来应用候选；NiuTrans 同读「凶」（side_anchored）；youngzs 同读「凶」（side_anchored）；Banny-Gao（旁证） 同读「凶」（side_anchored） |
| 331330 | 卷九 | 日丙申时发福防孤尅带疾通金 | kept 保留 | 保留「防」，四库两家同读防、无已定位异读；NiuTrans 同读「防」（side_anchored）；youngzs 同读「防」（side_anchored）；Banny-Gao（旁证） 同读「防」（side_anchored） |
| 332658 | 卷九 | 寅举人 丁夘防死甲戊 丁丑 | deferred 待补见证 | 四库谱系仅 mikkokotila 一家读「㐫」（凶），kanripo 未定位（多位于 bracket 名录条目），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载；四库谱系仅 mikkokotila 一家定位：kanripo 未定位（该位点多位于日时断 bracket 名录条目内），逐字如实登记未定位；候选读法只据一家登记，现代三家亦未载 |
| 332677 | 卷九 | 辛酉日戊戌时防刑己酉丑辰戌 | deferred 待补见证 | 四库两家同读「㐫」（凶），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 332797 | 卷九 | 计较【一云】防后发【乙酉进 | confirmed 定案 | 应改读「凶」（四库字形 㐫），登记为未来应用候选；NiuTrans 同读「凶」（side_anchored）；youngzs 同读「凶」（side_anchored）；Banny-Gao（旁证） 同读「凶」（side_anchored） |
| 332813 | 卷九 | 申举人 丁亥防死 戊辰御史 | deferred 待补见证 | 四库谱系仅 mikkokotila 一家读「㐫」（凶），kanripo 未定位（多位于 bracket 名录条目），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载；四库谱系仅 mikkokotila 一家定位：kanripo 未定位（该位点多位于日时断 bracket 名录条目内），逐字如实登记未定位；候选读法只据一家登记，现代三家亦未载 |
| 333768 | 卷九 | 术睦残花结果防风若无尅破与 | kept 保留 | 保留「防」，四库两家同读防、无已定位异读；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载；「防风」为固定语汇（残花结果防风语），四库两家同读防、现代见证未载，依 §2 不对称标准保留 |
| 333959 | 卷九 | 恶死辛亥月大防甲子月刑
  | confirmed 定案 | 应改读「凶」（四库字形 㐫），登记为未来应用候选；NiuTrans 同读「凶」（side_anchored）；youngzs 同读「凶」（side_anchored）；Banny-Gao（旁证） 同读「凶」（side_anchored） |
| 334348 | 卷九 | 工科 癸酉贫防戊申 壬戌  | deferred 待补见证 | 四库谱系仅 mikkokotila 一家读「㐫」（凶），kanripo 未定位（多位于 bracket 名录条目），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载；四库谱系仅 mikkokotila 一家定位：kanripo 未定位（该位点多位于日时断 bracket 名录条目内），逐字如实登记未定位；候选读法只据一家登记，现代三家亦未载 |
| 334475 | 卷九 | 袁封君子宗道防元宏道中道  | deferred 待补见证 | 四库两家同读「㑹」（會），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 334733 | 卷九 | 重沙滩局 飏防待顺风几畨防 | deferred 待补见证 | 四库谱系仅 mikkokotila 一家读「㠶」（帆），kanripo 未定位（多位于 bracket 名录条目），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载；位点字「㠶」为帆之异体（「飏㠶待顺风」语），四库谱系仅 mikkokotila 一家定位；四库谱系仅 mikkokotila 一家定位：kanripo 未定位（该位点多位于日时断 bracket 名录条目内），逐字如实登记未定位；候选读法只据一家登记，现代三家亦未载 |
| 334739 | 卷九 | 防待顺风几畨防险处 遇吉又 | deferred 待补见证 | 四库谱系仅 mikkokotila 一家读「㐫」（凶），kanripo 未定位（多位于 bracket 名录条目），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载；四库谱系仅 mikkokotila 一家定位：kanripo 未定位（该位点多位于日时断 bracket 名录条目内），逐字如实登记未定位；候选读法只据一家登记，现代三家亦未载 |
| 334772 | 卷九 | 
 运弱妻儿防尅害 运强财 | kept 保留 | 保留「防」，四库两家同读防、无已定位异读；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 335227 | 卷九 | 未李天宠都宪防死丁亥 丁酉 | deferred 待补见证 | 四库两家同读「㐫」（凶），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 335989 | 卷九 | 
 癸夘孙鑛防元南兵部 辛 | deferred 待补见证 | 四库谱系仅 mikkokotila 一家读「㑹」（會），kanripo 未定位（多位于 bracket 名录条目），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载；四库谱系仅 mikkokotila 一家定位：kanripo 未定位（该位点多位于日时断 bracket 名录条目内），逐字如实登记未定位；候选读法只据一家登记，现代三家亦未载 |
| 336503 | 卷九 | 酉 壬戌丁亥防死壬子】
  | deferred 待补见证 | 四库两家同读「㓙」（凶），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 337747 | 卷九 | 贵【又云】尅防极贫
 【丙 | deferred 待补见证 | 四库两家同读「䧟」（陷），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 338002 | 卷九 | 丙寅富 戊申防死庚辰 癸亥 | deferred 待补见证 | 四库谱系仅 mikkokotila 一家读「㓙」（凶），kanripo 未定位（多位于 bracket 名录条目），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载；四库谱系仅 mikkokotila 一家定位：kanripo 未定位（该位点多位于日时断 bracket 名录条目内），逐字如实登记未定位；候选读法只据一家登记，现代三家亦未载 |
| 338051 | 卷九 | 【又云】自刑防恶死
 【乙 | deferred 待补见证 | 四库两家同读「㐫」（凶），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 339003 | 卷九 | 中莫见官见之防不足 刑害事 | deferred 待补见证 | 四库谱系仅 mikkokotila 一家读「防」（防），kanripo 未定位（多位于 bracket 名录条目），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载；四库谱系仅 mikkokotila 一家定位：kanripo 未定位（该位点多位于日时断 bracket 名录条目内），逐字如实登记未定位；候选读法只据一家登记，现代三家亦未载 |
| 340074 | 卷九 | 庚午富 壬申防 戊戌廕郎壬 | deferred 待补见证 | 四库谱系仅 mikkokotila 一家读「㐫」（凶），kanripo 未定位（多位于 bracket 名录条目），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载；四库谱系仅 mikkokotila 一家定位：kanripo 未定位（该位点多位于日时断 bracket 名录条目内），逐字如实登记未定位；候选读法只据一家登记，现代三家亦未载 |
| 341431 | 卷九 | 【一云】破祖防
 【戊戌桂 | deferred 待补见证 | 四库两家同读「㐫」（凶），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 342011 | 卷九 | 戌透戊煞旺亦防【一云】名利 | deferred 待补见证 | 四库两家同读「㐫」（凶），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 342584 | 卷九 | 子进士 丁夘防壬戌 部侍郎 | deferred 待补见证 | 四库谱系仅 mikkokotila 一家读「㓙」（凶），kanripo 未定位（多位于 bracket 名录条目），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载；四库谱系仅 mikkokotila 一家定位：kanripo 未定位（该位点多位于日时断 bracket 名录条目内），逐字如实登记未定位；候选读法只据一家登记，现代三家亦未载 |
| 342858 | 卷九 | 戊申 三己夘防棍 甲戌夭  | deferred 待补见证 | 四库谱系仅 mikkokotila 一家读「㐫」（凶），kanripo 未定位（多位于 bracket 名录条目），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载；四库谱系仅 mikkokotila 一家定位：kanripo 未定位（该位点多位于日时断 bracket 名录条目内），逐字如实登记未定位；候选读法只据一家登记，现代三家亦未载 |
| 343797 | 卷九 | 癸亥贫 戊午防癸丑 戊寅  | deferred 待补见证 | 四库谱系仅 mikkokotila 一家读「㐫」（凶），kanripo 未定位（多位于 bracket 名录条目），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载；四库谱系仅 mikkokotila 一家定位：kanripo 未定位（该位点多位于日时断 bracket 名录条目内），逐字如实登记未定位；候选读法只据一家登记，现代三家亦未载 |
| 343964 | 卷九 | 刑乙丑月失土防死
 【癸亥 | confirmed 定案 | 应改读「凶」（四库字形 㐫），登记为未来应用候选；NiuTrans 同读「凶」（side_anchored）；youngzs 同读「凶」（side_anchored）；Banny-Gao（旁证） 同读「凶」（side_anchored） |
| 344416 | 卷九 | 
 月通身旺防妻损 丑巳遥 | kept 保留 | 保留「防」，四库两家同读防、无已定位异读；NiuTrans 同读「防」（full_flank）；youngzs 同读「防」（full_flank）；Banny-Gao（旁证） 同读「防」（full_flank） |
| 344470 | 卷九 | 身旺比肩之月防损妻财柱丑寅 | kept 保留 | 保留「防」，四库两家同读防、无已定位异读；NiuTrans 同读「防」（full_flank）；youngzs 同读「防」（full_flank）；Banny-Gao（旁证） 同读「防」（full_flank） |
| 344550 | 卷九 | 贵特达火土运防金水运吉【一 | confirmed 定案 | 应改读「凶」（四库字形 㐫），登记为未来应用候选；NiuTrans 同读「凶」（side_anchored）；youngzs 同读「凶」（side_anchored）；Banny-Gao（旁证） 同读「凶」（side_anchored） |
| 345494 | 卷九 | 贫下纯申破寅防
 【壬申髙 | deferred 待补见证 | 四库两家同读「㐫」（凶），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 345647 | 卷九 | 己未曾铣都宪防死 乙亥副使 | deferred 待补见证 | 四库两家同读「㐫」（凶），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 345811 | 卷九 |  甲辰司道屡防乙丑 乙亥】 | deferred 待补见证 | 四库谱系仅 mikkokotila 一家读「㐫」（凶），kanripo 未定位（多位于 bracket 名录条目），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载；四库谱系仅 mikkokotila 一家定位：kanripo 未定位（该位点多位于日时断 bracket 名录条目内），逐字如实登记未定位；候选读法只据一家登记，现代三家亦未载 |
| 345929 | 卷九 | 丑干透甲丁者防【一云】津梁 | deferred 待补见证 | 四库两家同读「㐫」（凶），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 346053 | 卷九 | 【又云】贵中防死
 【壬子 | deferred 待补见证 | 四库两家同读「㐫」（凶），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 346439 | 卷九 | 丑吉己丑丙子防
 【戊午林 | deferred 待补见证 | 四库两家同读「㐫」（凶），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 347559 | 卷九 |  乙亥武贵多防 丁夘侯辛夘 | deferred 待补见证 | 四库谱系仅 mikkokotila 一家读「㐫」（凶），kanripo 未定位（多位于 bracket 名录条目），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载；四库谱系仅 mikkokotila 一家定位：kanripo 未定位（该位点多位于日时断 bracket 名录条目内），逐字如实登记未定位；候选读法只据一家登记，现代三家亦未载 |
| 347576 | 卷九 | 戊申庚戌发财防死壬午】
  | deferred 待补见证 | 四库两家同读「㐫」（凶），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 348711 | 卷九 | 【又云】破祖防败
 【丁亥 | deferred 待补见证 | 四库两家同读「㐫」（凶），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 348962 | 卷九 | 半是非成败难防六亲不睦暗刑 | kept 保留 | 保留「防」，四库两家同读防、无已定位异读；NiuTrans 同读「防」（full_flank）；youngzs 同读「防」（full_flank）；Banny-Gao（旁证） 同读「防」（full_flank） |
| 349212 | 卷九 | 戌进士丁未 防终 壬子 庚 | deferred 待补见证 | 四库谱系仅 mikkokotila 一家读「㐫」（凶），kanripo 未定位（多位于 bracket 名录条目），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载；四库谱系仅 mikkokotila 一家定位：kanripo 未定位（该位点多位于日时断 bracket 名录条目内），逐字如实登记未定位；候选读法只据一家登记，现代三家亦未载 |
| 350711 | 卷九 | 大贵丑月煞重防夭
 【庚子 | confirmed 定案 | 应改读「凶」（四库字形 㐫），登记为未来应用候选；NiuTrans 同读「凶」（side_anchored）；youngzs 同读「凶」（side_anchored）；Banny-Gao（旁证） 同读「凶」（side_anchored） |
| 351535 | 卷九 | 亥】
 【田防船仓局 运拙 | deferred 待补见证 | 四库两家同读「䑕」（鼠），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载 |
| 352663 | 卷九 | 

 三命通防巻九
<子部 | deferred 待补见证 | 四库两家同读「㑹」（會），现代独立见证未齐，不裁；NiuTrans 未载；youngzs 未载；Banny-Gao（旁证） 未载；位点为卷九卷端书名「三命通會」之「會」字位点（S3 语境作「三命通防巻九」），四库两家读「㑹」；现代见证未载 |

### 15.4 定案要点与 deferred 缺口形态

- **confirmed 16**：308023/308163/311149/311221/314956/
  314963/315136/322065/324983/325177/330666/332797/
  333959/343964/344550/350711，四库作「㐫」而现代计方
  两家同读「凶」——均四库 + 独立现代方同读、读法只登记
  为未来 v2 应用候选，文本未动。
- **kept 7**：328001（防尅害）、331330（防孤尅，现代三家
  同读防）、333768（防风，固定语汇）、334772（防尅害）、
  344416（防妻损，现代三家同读防）、344470（防损妻财，
  现代三家同读防）、348962（难防，现代三家同读防）——
  四库同读防且无已定位异读。
- **parallel 0**：本册无谱系分歧并列。
- **deferred 71**：字形分布：㐫 51、㑹 8（含 352663 卷端
  书名「三命通會」位点 1）、㓙 6、䧟 2、㴶/㠶/䑕/防 各 1
  （㴶为人名用字、其字本身即为候选词；㠶为帆之异体；
  防 1 处为 339003，四库谱系仅 mikkokotila 一家读防、
  kanripo 未定位，不以一家定保留）。其中 32 处四库谱系
  亦仅 mikkokotila 一家定位（见 §15.1），324699/324706
  两处另有《五行精纪》平行源旁证同读在案（不计方），余
  37 处缺口为三命通会文本自身的第二独立见证方未齐。
  升级路径同 §5：补齐现代全本转录（如 Wikisource
  michiboo《三命通会》对应卷次）、kanripo 对应原叶定位
  或四库影印原叶后逐处升级。

### 15.5 累计进度与剩余分册计划（更新）

- 累计处置进度：**disposed 115/769**（confirmed 55、kept
  56、parallel 4）；deferred 555（节内 29 + 第二分册
  67 + 第三分册 112 + 第四分册 50 + 第五分册 118
  + 第六分册 61 + 第七分册 47 + 本册 71）；pending 99
  （其中 RD-12 位点 7 处只标记、处置随 P3）。
- 全卷累计：

| 卷 | 盘点 | confirmed | kept | parallel | deferred | pending |
|---|---|---|---|---|---|---|
| 卷首 | 1 | 0 | 0 | 1 | 0 | 0 |
| 卷一 | 10 | 0 | 8 | 0 | 2 | 0 |
| 卷二 | 34 | 2 | 2 | 1 | 29 | 0 |
| 卷三 | 50 | 1 | 6 | 0 | 43 | 0 |
| 卷四 | 118 | 2 | 4 | 0 | 112 | 0 |
| 卷五 | 89 | 14 | 8 | 0 | 65 | 2 |
| 卷六 | 142 | 11 | 6 | 0 | 125 | 0 |
| 卷七 | 75 | 4 | 8 | 0 | 61 | 2 |
| 卷八 | 61 | 5 | 7 | 2 | 47 | 0 |
| 卷九 | 94 | 16 | 7 | 0 | 71 | 0 |
| 卷十 | 26 | 0 | 0 | 0 | 0 | 26 |
| 卷十一 | 45 | 0 | 0 | 0 | 0 | 45 |
| 卷十二 | 24 | 0 | 0 | 0 | 0 | 24 |
| 合计 | 769 | 55 | 56 | 4 | 555 | 99 |

- 剩余分册（按卷序）：卷十 26、卷十一 45、卷十二 24，另
  卷五 RD-12 两处、卷七 RD-12 两处、卷十 RD-12 一处、
  卷十一 RD-12 两处随 P3。本册同样只登记处置结论、零
  文本改动，`canonical_ready` 保持 false。
