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

### 🔴 严重：藏干表来源非古籍

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

**影响**:
- `bazi_strength.py` 的月令藏干事实基于未审核来源
- `bazi_root_conditions.py` 的通根判断基于未审核来源
- 所有5个Variant的"结构事实"层存在来源缺陷

**建议**:
- 降级：藏干表标记为 `secondary_pending`，不得作为Canonical证据
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

### 🟢 确认：规则边界正确

**优点**:
- 5个Variant均明确声明"不输出整体旺衰"
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
- 但来源本身未审核，需降级

## 四、处理建议

| 问题 | 等级 | 处理 |
|------|------|------|
| 藏干表来源非古籍 | P0 | 标记为secondary_pending；在公开代码注释来源限制 |
| 短引SHA/定位缺失 | P1 | 在私有audit补充完整引用信息 |
| 寅月分日冲突 | P2 | 保持unresolved，已正确处理 |
| 三刑冲突 | P2 | 保持unresolved，已正确处理 |

## 五、结论

TJ-010.1验收条件：
- [x] 现有相关来源完成逐条盘点
- [ ] 所有已审核短引具备可核验的来源定位（待补充）
- [x] 关键古籍异文和适用口径明确
- [x] 发现的错引得到记录（藏干表来源问题）
- [ ] Pending/Quarantine/Canonical边界正确（需降级藏干表）
- [x] 已审核规则的Rule/Evidence对应可复核
- [ ] 必要的测试执行成功（待补充来源验证测试）

**下一步**:
1. 在私有仓库创建TJ-010.1 PR，补充短引审计
2. 或接受藏干表为pending，明确标注限制
3. 不修改已验收的四柱算法（按任务要求）
