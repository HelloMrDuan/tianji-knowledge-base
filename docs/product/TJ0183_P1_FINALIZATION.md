# TJ-018.3 晋级 P1：993 候选终局化登记（E0300）

> 对象：《三命通会》钉定快照 `sanming_tonghui.txt`（SHA256 `00e2a7db…`，461,157 字）的 OCR 校对候选 993 条中，E0298 正式应用批未处置、设计 §5.2 定为 P1 的 **822 条**（variant_preserve 47 + historical_only_hold 775）。产物：公开侧纯数据登记册 `sanming-ocr-candidates-finalization-register-v1`（`src/tianji_kb/bazi_sanming_finalization.py` + `tests/golden_tj0183_sanming_finalization.json` 全量镜像）+ 公开/密封专项。**纯登记批：不改快照任何文件（含应用产物与候选 JSON），不改候选状态语义，`canonical_ready` 保持 false。**

## 结论

- 822/822 条逐条登记完成：每条含 S2 基线坐标、经应用报告 origin 位点图换算的 S3 坐标、S3 位点实际字、S2/S3 两侧 context 跨度与哈希、锚定类别、携带标记与见证原文。
- S3 位点实际字 **822/822 与 S2 读法逐字相同**（实测结论：本批 822 条位点均未被 ocr-445..603 尾段订正改写；订正改写的位点全部落在 confirmed_applied 159 条内）。
- 历史读法与 S3 现读 **822/822 互异且严格分栏**：historical_reading 只来自四库谱系见证（kanripo/KR3g0042、mikkokotila/Sanming-Tongshui 两家转录逐条在案，同谱系计一个见证方）；variant 47 条另有现代谱系 crosscheck 见证 52 条（含 observed 读法）并列登记，不择一、不改字；hold 775 条的历史读法只作定位登记，不冒充 S3 现读。

## 双维度对账（禁止混算）

状态维度（候选处置的唯一加总口径）：

| 状态 | 条数 | 处置 |
|---|---|---|
| historical_only_hold | 775 | 本批定位登记 |
| variant_preserve | 47 | 本批并列登记 |
| confirmed_applied | 159 | E0298 应用批已核销关闭 |
| reading_disagreement_hold | 12 | P3 待办，不在本批 |
| **合计** | **993** | 775 + 47 + 159 + 12 = 993 |

携带维度（context 跨越订正边界，与状态维度**正交**）：76 = hold 40 + variant 6 + confirmed 29 + RD 1，由 E0298 应用报告 `context_carry` 按 C1–C5 携带（limitations 0）；本批与之交叠 46 条（40 + 6）。**159 + 76 + 822 + 12 = 1069 ≠ 993** 是把正交维度误入状态加总的错账形态，登记册中显式声明禁止。

## 方法（全部可复算）

1. **坐标换算只经 origin 图**：S3 坐标逐条取自应用报告 `candidate_annex.dispositions[].site_s3_offset`；其 `site_s2_offset` 与重锚登记册 `basis_offset` 993/993 逐条一致（生成时全验），禁止手算偏移。
2. **基线侧复验**：在密封环境两阶段复放重建 S2（钉 `db8618c9…`），822 条 S2 位点字与 context 全文/哈希（与重锚登记册 `context_sha256` 一致）逐条核对。
3. **S3 侧核验**：位点字逐条与应用文本（钉 `a89c0b5d…`）实切比对，且与报告 `site_state_in_S3` 一致；S3 context 按应用批 C1 同形口径重建（`[site_s3 − site_in_context, +len(context))`），46 条交叠者的跨度/全文/哈希与报告 `context_carry` 逐条一致，其余条目哈希按重建文本实算登记。
4. **候选对齐**：候选 JSON 与重锚登记册逐条对齐（位置 seq、status、old、historical_reading、基线坐标、context、volume、correction_id 全等）；见证记录（historical_evidence / crosscheck_evidence）逐字复制入登记册，密封专项再与密封候选 JSON 逐条比对。

验证面：登记册生成断言链（四份输入哈希钉合、上述全部逐条核对，任一失败即整批不出数）；公开专项 11 测（Golden 镜像、纯数据形制、与重锚/应用记录登记册交叉、双维度对账、见证覆盖）；密封专项 6 测（对密封原文执行：阶段文本钉、候选逐条对齐、origin 图对账、S2/S3 逐字与哈希全量、46 条携带对平）。正式验收以部署管线对合并 SHA 的完整配方结果为准（现行钉值：快照 manifest `5ea551f5…`，237 文件 / 15,883,200 字节）。

## 红线与剩余

- 快照本体、应用产物两件、候选 JSON 逐字未动（哈希在密封专项中逐一钉合复验）；异文不择一、历史读法不冒充现读，均由测试钉住。
- 剩余晋级接口：P2 残余「防」769 逐处处置、P3 RD-12 见证互校（含本批外 12 条 reading_disagreement_hold）、P4 TJ-018.3 决策包（UD-1/2/3 不代决）；TJ-018.2 与 TJ-018.3 任务状态不变。
