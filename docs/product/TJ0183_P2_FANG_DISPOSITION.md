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
