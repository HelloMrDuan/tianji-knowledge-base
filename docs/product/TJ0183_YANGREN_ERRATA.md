# TJ-018.3 阳刃节「凶/㓙」登记—应用分歧勘误登记（E0354）

事件：E0354。基线 main `297bd936767fbe60d50d51355f82b82e6a961b6d`（tiaohou 关账 PR #530 已合并），台账 353 事件，密封钉 `26b63e64bed736b08a7dcd686f6a75de733fd44ba9eec9195248e69730485329`。机器可读登记册：`sanming-yangren-errata-register-v1`（`src/tianji_kb/bazi_sanming_yangren_errata.py`）。本批止于 PR；只登记勘误，不订正任何文本。

## 0 授权与范围

- 范围恰为：《三命通会》卷五《论阳刃》节（登记节 `sanming.juan5.yangren`、Canonical `bazi.section.s064`）内两处「防」位点——引文 `yr.ersha` 第 6 字（S0 182078）与 `yr.he_xing` 第 16 字（S0 182375）——的登记—应用分歧勘误登记，及同节全部 25 处校勘读法为「㓙」的「防」位点逐处复核。
- 分歧来历：B-2 禄刃两节晋级（E0339）发现并披露于 `TJ0183_LUREN_PROMOTION.md` §3.2；治理 pending 审计（E0341）`GOVERNANCE_PENDING8_AUDIT.md` §3 定性为校勘订正（勘误）路径：勘误登记先行，是否重应用属独立决策、不与登记捆绑；不属 P2 残余处置（P2 对象是未被应用的残余位点，本两处恰已被应用且结果与登记相左），不需用户裁定（不涉流派取舍、无对立见证）。
- 不在范围：修改 S0 快照、S3 应用文本、密封快照、cicd 钉、s064 节文本、既有校勘记与 B-2 密封枚举钉的任何一字；重应用决策；阳刃节外位点的处置。

## 1 开工核实

- API main HEAD = `297bd936767fbe60d50d51355f82b82e6a961b6d`，与任务书基线逐字一致；台账 353 事件、末号 E0353（tiaohou 关账）。
- B-2 治理文档 §3.2（`TJ0183_LUREN_PROMOTION.md` 第 38 行）与任务书逐项对平：两处防位点（`yr.ersha` 第 6 字、`yr.he_xing` 第 16 字），密封订正集应用作「凶」，018-F 校勘记登记读法作「㓙」；该分歧不涉及任何绑定引文；密封专项以精确枚举钉住这两处、第三处出现即测试失败。
- 密封枚举钉（`tests/test_phase2_baziluren.py`）实测：`divergent = {('yr.ersha', 6), ('yr.he_xing', 16)}`，且断言该两处 S3 字为「凶」、登记 mapped_reading 为「㓙」。本批未动此钉。
- 校勘记两条（`sm5y-fang-182078`、`sm5y-fang-182375`，于 `bazi_sanming_juan5_zaqi_yangren_collation.py`）实测均为 `reading_status = confirmed`、`usable_grade = Q1`、`disposition = corrected`，读法「㓙」各有两家见证同作（kanripo KR3g0042、mikkokotila 转录子集，逐字引文在册）。
- 影响面在册复核：Phase1 规则 `bazi.rule.r035` 绑定恰 4 条引文（`renshi.luren_route_exclusion`、`sanming.lu_sentence`、`sanming.ren_doctrine`、`sanming.ren_positions`）；`yr.ersha`、`yr.he_xing` 均不在其中。
- 机上 cicd 钉与 live 快照 manifest 均为 `26b63e64…`，与任务书一致；S0 文件 SHA256 = `00e2a7db…`、S3 应用文本 SHA256 = `a89c0b5d…`，与正式应用批（E0298）钉值逐字一致；S0 全长 461,157 字、S3 全长 461,156 字，S0→S3 位移 −1 与在册口径一致。

## 2 阳刃节 25 处逐处复核

复核口径：以校勘册 `COLLATION_NOTES` 中 `section_id = sanming.juan5.yangren`、`snapshot_glyph = 防`、登记读法 = 㓙 的全部条目为复核集（实测恰 25 条，全部 confirmed / Q1 / corrected）；2026-11-01 于可信机 live 密封快照直读 S0 与 S3 两文件，逐处比对 S0 原字与 S3 应用字（S3 位点 = S0 位点 − 1）。

复核结论：S0 原字 25/25 全为「防」；S3 应用字分布为——按登记读法作「㓙」17 处、保留快照原字「防」6 处、作「凶」恰 2 处。偏离恰 2 处（S0 182078、S0 182375），无第三处；6 处残余「防」为未应用保留，与 P2 残余处置口径一致，不属本勘误范围。

| # | S0 位点 | S3 位点 | 校勘记 | S0 字 | 登记读法（等级） | S3 应用字 | 结论 |
|---|---|---|---|---|---|---|---|
| 1 | 181025 | 181024 | sm5y-fang-181025 | 防 | 㓙（confirmed/Q1） | 㓙 | 按登记读法应用 |
| 2 | 181169 | 181168 | sm5y-fang-181169 | 防 | 㓙（confirmed/Q1） | 㓙 | 按登记读法应用 |
| 3 | 181174 | 181173 | sm5y-fang-181174 | 防 | 㓙（confirmed/Q1） | 㓙 | 按登记读法应用 |
| 4 | 181190 | 181189 | sm5y-fang-181190 | 防 | 㓙（confirmed/Q1） | 㓙 | 按登记读法应用 |
| 5 | 181200 | 181199 | sm5y-fang-181200 | 防 | 㓙（confirmed/Q1） | 㓙 | 按登记读法应用 |
| 6 | 181279 | 181278 | sm5y-fang-181279 | 防 | 㓙（confirmed/Q1） | 㓙 | 按登记读法应用 |
| 7 | 181314 | 181313 | sm5y-fang-181314 | 防 | 㓙（confirmed/Q1） | 㓙 | 按登记读法应用 |
| 8 | 181372 | 181371 | sm5y-fang-181372 | 防 | 㓙（confirmed/Q1） | 㓙 | 按登记读法应用 |
| 9 | 181532 | 181531 | sm5y-fang-181532 | 防 | 㓙（confirmed/Q1） | 㓙 | 按登记读法应用 |
| 10 | 181862 | 181861 | sm5y-fang-181862 | 防 | 㓙（confirmed/Q1） | 㓙 | 按登记读法应用 |
| 11 | 181873 | 181872 | sm5y-fang-181873 | 防 | 㓙（confirmed/Q1） | 㓙 | 按登记读法应用 |
| 12 | 181891 | 181890 | sm5y-fang-181891 | 防 | 㓙（confirmed/Q1） | 㓙 | 按登记读法应用 |
| 13 | 181918 | 181917 | sm5y-fang-181918 | 防 | 㓙（confirmed/Q1） | 㓙 | 按登记读法应用 |
| 14 | 182078 | 182077 | sm5y-fang-182078 | 防 | 㓙（confirmed/Q1） | 凶 | **偏离：应用作「凶」** |
| 15 | 182120 | 182119 | sm5y-fang-182120 | 防 | 㓙（confirmed/Q1） | 㓙 | 按登记读法应用 |
| 16 | 182291 | 182290 | sm5y-fang-182291 | 防 | 㓙（confirmed/Q1） | 㓙 | 按登记读法应用 |
| 17 | 182375 | 182374 | sm5y-fang-182375 | 防 | 㓙（confirmed/Q1） | 凶 | **偏离：应用作「凶」** |
| 18 | 182438 | 182437 | sm5y-fang-182438 | 防 | 㓙（confirmed/Q1） | 㓙 | 按登记读法应用 |
| 19 | 182493 | 182492 | sm5y-fang-182493 | 防 | 㓙（confirmed/Q1） | 防 | 残余保留快照原字 |
| 20 | 182679 | 182678 | sm5y-fang-182679 | 防 | 㓙（confirmed/Q1） | 防 | 残余保留快照原字 |
| 21 | 183540 | 183539 | sm5y-fang-183540 | 防 | 㓙（confirmed/Q1） | 防 | 残余保留快照原字 |
| 22 | 183644 | 183643 | sm5y-fang-183644 | 防 | 㓙（confirmed/Q1） | 㓙 | 按登记读法应用 |
| 23 | 183983 | 183982 | sm5y-fang-183983 | 防 | 㓙（confirmed/Q1） | 防 | 残余保留快照原字 |
| 24 | 184103 | 184102 | sm5y-fang-184103 | 防 | 㓙（confirmed/Q1） | 防 | 残余保留快照原字 |
| 25 | 184165 | 184164 | sm5y-fang-184165 | 防 | 㓙（confirmed/Q1） | 防 | 残余保留快照原字 |

## 3 勘误登记（两条）

勘误条目全文见登记册 `sanming-yangren-errata-register-v1` 的 `ERRATA`，字段与本节逐项对应。

### 3.1 sm5y-errata-182078

- 位点：登记节 `sanming.juan5.yangren`、Canonical 节 `bazi.section.s064`、引文 `yr.ersha` 第 6 字；S0 182078、S3 182077；语境「则以好命断之又曰阳刄者天上之防星人间之煞喜偏官印绶忌反吟」。
- 校勘记：`sm5y-fang-182078`；快照原字「防」；登记读法「㓙」（confirmed / Q1 / corrected）。
- 见证依据：kanripo KR3g0042（KR3g0042_005.txt：「以好命斷之又曰陽刄者天上之㓙星人間之悪煞喜偏官印綬忌反」）与 mikkokotila《三命通会》转录子集（source/juan-05.md：「以好命斷之又曰陽刄者天上之㓙星人間之𢙣煞喜偏官印綬忌反」）两家同作「㓙」，无对立见证。
- 应用现状：S3 作「凶」——既非登记读法、亦非快照原字。本批登记后 S3 文本逐字未动。
- 处置状态：`registered_unapplied`。

### 3.2 sm5y-errata-182375

- 位点：登记节 `sanming.juan5.yangren`、Canonical 节 `bazi.section.s064`、引文 `yr.he_xing` 第 16 字；S0 182375、S3 182374；语境「日刄大忌冲合喜官煞相制合者防遇印者吉有煞无刃施为有勇无威」。
- 校勘记：`sm5y-fang-182375`；快照原字「防」；登记读法「㓙」（confirmed / Q1 / corrected）。
- 见证依据：kanripo KR3g0042（KR3g0042_005.txt：「刄大忌衝合喜官煞相制合刑者㓙遇印者吉有煞無刃施為有勇無」）与 mikkokotila 转录子集（source/juan-05.md：「刄大忌衝合喜官煞相制合𠛬者㓙遇印者吉有煞無刃施為有勇無」）两家同作「㓙」，无对立见证。
- 应用现状：S3 作「凶」——既非登记读法、亦非快照原字。本批登记后 S3 文本逐字未动。
- 处置状态：`registered_unapplied`。

## 4 定性与影响面

- 偏离定性（两条同）：`application_deviation`——订正集正式应用对已 confirmed 登记的偏离，属应用层勘误。不是登记错误：登记读法有双见证支撑且定级 confirmed/Q1 在册；不是见证分歧：无任何对立见证。「凶」是「㓙」的现代通行字形，两读同词，歧义只在字形层。同节其余 23 处同类位点的应用结果（17 处从登记读法、6 处保留原字）亦表明按登记读法应用是订正集常态，本两处为仅有的例外。
- 影响声明（两条同）：零。两处位点所在引文 `yr.ersha`、`yr.he_xing` 为 018-F 登记引文，均非 `bazi.rule.r035` 的 source_refs（绑定恰 4 条，见 §1）；不入任何其他绑定引文；不涉及任何 determination；s064 节文本从 S3 的携带口径不变。
- 遏制现状：密封专项 `test_phase2_baziluren.py` 的精确枚举钉保持不动且继续成立——勘误登记落地后两处在 S3 中仍作「凶」，登记状态由「已披露、已钉住、未订正」推进为「已披露、已钉住、已登记勘误、未订正」，不得在任何报告中记为已解决或已订正。

## 5 后续决策点与未订正声明

- 后续决策点（本批不裁）：是否定向重应用——按登记读法将 S3 两位点订正为「㓙」，并连动 s064 节文本 2 字、密封快照换代与 B-2 密封枚举钉的同步修订。该决策成本远高于 2 字本身（快照换代全链），属独立批次决策，须另行立项；本批不代决、不预设结论。
- 未订正声明：截至本批，S3 应用文本与 s064 节文本中两处仍作「凶」；既有校勘记两条逐字未动；整书 `canonical_ready` 保持 false 不变。

## 6 本批产出与边界

- 新增文档：`docs/product/TJ0183_YANGREN_ERRATA.md`（本文）。
- 新增登记模块：`src/tianji_kb/bazi_sanming_yangren_errata.py`（纯数据：登记册头、复核依据、25 处复核表、勘误 2 条、遏制引用；不被任何可执行路径 import）。
- 新增公开治理测试：`tests/test_tj0183_yangren_errata.py`（登记存在、勘误恰 2 条枚举、状态 unapplied、与校勘册逐项对平、25 处复核集与校勘册全集恰等、影响面非绑定断言），已按名接入 `.github/workflows/validate.yml`。
- 台账：E0354 追加（归属 TJ-018.2、状态「阻塞」不变）；TASK_STATUS 仅动 TJ-018.2 一行。
- 边界复核：本批未改动 S0/S3 文本、密封快照与 cicd 钉、既有校勘记、B-2 密封枚举钉、任何 determination 与公开投影；登记落点全部在公开治理层，无需密封侧文件变更。
