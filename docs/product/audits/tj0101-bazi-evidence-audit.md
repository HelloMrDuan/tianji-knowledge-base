# TJ-010.1 八字本气/月令/通根古籍证据审计报告

**任务**: TJ-010.1｜对照本气、月令/根与异文的每条短引  
**日期**: 2026-10-15  
**分支**: tj-010.1-bazi-evidence-audit  
**状态**: 进行中

## 一、审计范围

### 5个Variant
1. `ditiansui-root-visibility-v1` (bazi_strength.py)
2. `bazi-strength-conditions-v1` (bazi_root_conditions.py)
3. `ditiansui-root-conditions-v1` (bazi_root_conditions.py)
4. `ditiansui-wood-root-availability-v1` (bazi_root_conditions.py)
5. `bazi-strength-adjudication-v1` (bazi_adjudication.py)

### 4部古籍 (phase1_knowledge.json)
- bazi.classic.yuanhai (渊海子平)
- bazi.classic.sanming_tonghui (三命通会)
- bazi.classic.xieji (协纪辨方书)
- bazi.classic.ditiansui (滴天髓)

## 二、关键发现

### ⚠️ 来源层级需区分：二级表格与独立古籍短引

**文件**: `data/canonical/bazi/foundations_v1.json`

**provenance**:
```json
{
  "repo": "jinchenma94/bazi-skill",
  "path": "references/wuxing-tables.md",
  "commit": "112a5d84cd1a001a0038cafca3be68d93e4c0cc9"
}
```

**问题**:
- 藏干表（含本气/中气/余气结构）来自第三方MIT仓库，非审核古籍原文
- 该仓库是"二级摘要"，文件自身警告："不是古籍原文"
- 违反TJ-010.1要求："不把整书 D/pending 冒充 Canonical"
- 违反要求："不得从搜索摘要、二手文章或模型记忆中编造原文"

**独立复审修正**：私有 Phase1 中已有经审《渊海子平》“又地支藏遁歌”短引 `bazi.section.s004`；现有 Phase2 藏干规则与该短引关联。第三方表格的 provenance 不能冒充古籍，但亦不能推断所有藏干成员完全缺少古籍依据。s004 只支持成员集合，不直接支持本气次序/数值权重。

**建议**:
- 先区分“二级实现素材来源”与“已审核 C 级古籍结构证据”，不直接将整个表格下架。若逐项核对发现具体错引或差异，再针对性收紧规则/证据。
- 或补充：从《渊海子平》《三命通会》L0原文核实十二支藏干，固定SHA与字符定位

### 🟡 待核实：具体短引的SHA与定位

**现状**:
- phase2_execution.json 的 evidence_scope 提及"已核原典短引"
- 具体短引文本、SHA、字符偏移未在公开审计中找到
- 需在私有 `data/audit/` 补充每条短引的：
  1. 古籍名称、版本、电子版SHA
  2. 卷/篇/页/行或字符偏移
  3. 原文短引（繁简/异体标注）
  4. OCR差异说明
  5. 审核状态

### 🟢 已核定的公开发布边界

**优点**:
- 因素和根条件 Variant 不输出通用整体旺衰；有限充分条件 adjudication Variant 仅研究态输出个别 strong/weak，public_enabled=false
- `bazi_strength.py` 的unresolved列表诚实记录未裁定项
- 未将"藏干有同类"等同于"得令"
- 未给本气/中气/余气赋权重

## 三、异文冲突记录

### 寅月分日
- evidence_scope提及"寅月分日"短引
- 需核实：立春后分日司令的不同口径
- 状态：unresolved（代码中已标记）

### 三刑
- `bazi.concept.conflict_three_punishments` 已记录跨流派冲突
- 任氏口径：不机械消根
- 状态：保留冲突，未强行合并 ✓

### 本气/中气/余气口径
- 当前藏干表未区分本气/中气/余气权重（代码明确不赋权重）✓
- 表格实现来源为二级材料，但其藏干成员已有经审 s004 短引独立支持；排序、权重仍未核实

## 四、处理建议

| 问题 | 等级 | 处理 |
|------|------|------|
| 表格 provenance 为二级来源 | P1待核 | 与已审核 s004 逐支比对、保留原 provenance；未发现具体错误前不得整体降级 |
| 短引SHA/定位缺失 | P1 | 在私有audit补充完整引用信息 |
| 寅月分日冲突 | P2 | 保持unresolved，已正确处理 |
| 三刑冲突 | P2 | 保持unresolved，已正确处理 |

## 五、结论

TJ-010.1验收条件：
- [x] 现有相关来源完成逐条盘点
- [ ] 所有已审核短引具备可核验的来源定位（待补充）
- [x] 关键古籍异文和适用口径明确
- [x] 发现的错引得到记录（藏干表来源问题）
- [ ] Pending/Quarantine/Canonical边界正确（需独立复核数据表与古籍证据的层级）
- [x] 已审核规则的Rule/Evidence对应可复核
- [ ] 必要的测试执行成功（待补充来源验证测试）

**下一步**:
1. 在私有仓库创建TJ-010.1 PR，补充短引审计
2. 只对证明不符的具体条目降级，不直接破坏已验证的四柱结构
3. 不修改已验收的四柱算法（按任务要求）

## 独立复审核实的实证差异

《渊海子平》s004 的完整短引已在受限 Phase1 审核；其原始电子文本起始字符索引 737。《滴天髓阐微》s023/s024/s025/s026/s027/s028/s034/s035/s036/s037 的原始字符索引分别为 37963/38056/39989/40063/38284/39648/10034/10113/20509/38165；《渊海》s029 原始字符索引 409。上述均为字符索引而非 UTF-8 字节偏移。电子版 SHA-256 已存在于公开 Source 登记，但仍须私有 CI 重算。藏干成员集合不能证明本气排列和 60/30/10 权重。有限强弱裁决 Variant 可能在研究态输出 strong/weak，始终不得公开。

## 源级别裁决

第三方表格直接 provenance 为二级实现来源，不是古籍证据；私有经审核的 s004 能支持十二支藏干**成员集合**，但不能直接推导排列顺序、分日司令或 60/30/10 权重。故不得一键把已验证结构整体降级或下架，必须将未受古籍支持的衍生判断保持未决，具体差异逐项审定。私有证据测试和最终 Rule/Evidence 对应仍需 CI 证实。

