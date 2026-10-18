# TJ-011.1 充分条件逐条审核草稿

**Variant**: `bazi-strength-adjudication-v1`
**审核基线**: 公开 main `02b9485af14c9cc36b9e4cf745f9c577927473c7`（TJ-010.3 关账后）
**审核日期**: 2026-10-18
**状态**: 草稿，仅审核分析，未修改代码或测试

---

## 审核总览

### 证据等级声明

- 《滴天髓阐微》为 **C 级单一电子版本**，SHA256 `6a875a317c7ba1012285ed12d3bfa5577b50c9fdfd568ece323a12feafe38795`，不能升级为独立底本一致。
- 原注与任氏不视作两个独立底本。
- 古籍原文支持的是**整体状态**（"从旺/从强之极"、"孤立无气"），不能自动证明每个分解条件的实现细节。
- 以下 15 个条件中，**直接古籍支持**的仅为整体状态描述；各分解条件多为**保守实现假设**（比原文更严格）或**未验证假设**。

### 古籍依据总表（来自 BAZI_STRENGTH_ADJUDICATION_AUDIT.md Section C）

| 用途 | 出处 | 字符定位 | 原文关键句 |
|---|---|---|---|
| 强（从旺） | 滴天髓从象 | char 96521 / line 4905 | "从旺者…无官杀之制，有印绶之生，旺之极者" |
| 强（从强） | 滴天髓从象 | char 96605 / line 4906 | "从强者…绝无一毫财星官杀之气…强之极矣" |
| 弱（孤立） | 滴天髓从象 | char 96219 / line 4903 | "日主孤立无气，无地人元，绝无一毫生扶之意…" |
| 弱（补充） | 滴天髓从象 | char 98032 / line 5028 | "日主休囚无根，惟官星当令…所谓弱之极者不可益也" |

**Source ID**: `bazi.source.ditiansui-spouse`（滴天髓阐微）
**Section ID**: 强对应从象章节（具体 Section ID 待查）；弱对应 s049（"日主孤立无气"）、s051（补充）
**流派**: 任氏（原文自称立说）；弱亦引原注"日主孤立无气，四柱无生扶之意"

---

## 第一部分：强充分条件（pure_support_scope_conditions）

代码位置：`src/tianji_kb/bazi_action_conditions.py` 第 29-40 行
最终裁决：`src/tianji_kb/bazi_adjudication.py` 第 129-134 行

```python
pure = (effects['pure_support_scope_met']
    and all(effects['pure_support_scope_conditions'].values())
    and command['month_branch'] == '卯' and command['relation'] == 'same_element'
    and roots['root_presence']
    and all(r['root_availability'] == 'effective' for r in roots['roots'])
    and all(r['effect_status'] == 'effective_in_reviewed_context' for r in effects['visible_relations']))
```

---

### 强-1: wood_day_master

**1. 此条件为什么存在？**
古籍从旺/从强论述针对的是特定日主状态。本 Variant 限定为木日主（甲/乙），因为已审核的根表（s026、s033"甲乙逢亥寅卯"）和月令关系（卯月同类）仅覆盖木。若日主非木，后续所有"同类/印比"判断均失去古籍依据。

**2. 支持它的古籍短引？**
- 滴天髓 s026、s033：明列"甲乙逢亥寅卯"（衰旺 char 39893 / line 1613，天干 char 5159 / line 241）
- 从象 char 96521/96605 的"从旺/从强"论述以日主状态为前提

**3. Source ID、Section ID？**
- Source: `bazi.source.ditiansui-spouse`
- Section: s026、s033（根表）；从象章节（具体 Section ID 待查）

**4. 证据支持整体还是部分？**
**部分**。s026/s033 支持"甲乙有特定木根位置"这一事实，不支持"木日主+卯月即可判强"的完整推论。从象原文描述的是整体极强状态，wood_day_master 只是该状态的必要非充分前提。

**5. 适用流派和 Variant？**
任氏；`bazi-strength-adjudication-v1`（research_only）

**6. 现有程序如何计算？**
`bazi_action_conditions.py` 第 28 行：
```python
wood = stem_element(observed['day_master']) == policy['day_master_element']
```
其中 `policy['day_master_element']` 为 `'木'`（来自 `bazi.concept.action_effects_v1` 实体属性，私有知识库）。

**7. 能否从真实四柱和 Trace 复算？**
能。需要：
- Trace `bazi.phase2.pillars` 输出的 `day_master.stem`
- `foundations()` 的干支五行映射（甲乙→木）
- `bazi.phase2.action_effects` 输出的 `pure_support_scope_conditions.wood_day_master`

**8. 缺少时是否停止输出 strong？**
是。`pure` 是合取（conjunction），`all(pure_conditions.values())` 中任一 False 即导致 `pure=False`，`classification` 保持 `indeterminate`（`bazi_adjudication.py` 第 129-141 行）。

**9. 真实反例或证据冲突？**
- 反例：任何非木日主（如丙日主卯月）→ wood_day_master=False → indeterminate。符合"不扩展为通用旺衰"边界。
- 无证据冲突。C 级单版本限制已声明。

**审核结论**: ✅ 直接古籍支持（s026/s033 根表）+ 保守实现假设。**不能推出**：木日主即强。

---

### 强-2: reviewed_same_element_month

**1. 此条件为什么存在？**
从旺要求"当令"——月令本气与日主同类是"旺之极"的前提。任氏 s033–036 强调"然以本气为主"。本 Variant 进一步限定为**已审核的卯月**（非任意同类月），因 principal_qi Variant 仅输出已审核八支的本气关系。

**2. 支持它的古籍短引？**
- 滴天髓 s033–036，地支 char 10115 / line 280；衰旺 char 39648 / line 1613："然以本气为主"
- 从象 char 96521："从旺者…"（当令为隐含前提）

**3. Source ID、Section ID？**
- Source: `bazi.source.ditiansui-spouse`
- Section: s033–s036（本气）；从象章节（待查）

**4. 证据支持整体还是部分？**
**部分**。s033–036 支持"月支本气关系需审查"，不支持"仅卯月可判强"。限定卯月是**保守实现假设**——原文未说"只有卯月木才能从旺"，实现者选择最窄的已审核范围以避免外推。

**5. 适用流派和 Variant？**
任氏本气口径；`bazi-strength-adjudication-v1`

**6. 现有程序如何计算？**
`bazi_action_conditions.py` 第 31-32 行：
```python
'reviewed_same_element_month': principal['month_branch'] in policy['pure_months']
    and principal['status'] == 'reviewed_relation' and principal['relation'] == 'same_element',
```
三重要求：(a) 月支在 `pure_months`（政策值，含'卯'）；(b) principal_month 状态为 `reviewed_relation`；(c) 关系为 `same_element`。另在 `_bounded_assessment` 第 131 行有冗余校验：`command['month_branch'] == '卯' and command['relation'] == 'same_element'`。

**7. 能否从真实四柱和 Trace 复算？**
能。需要：
- Trace `bazi.phase2.principal_month` 输出的 `month_branch`、`status`、`relation`
- `bazi.phase2.action_effects` 的 `pure_support_scope_conditions.reviewed_same_element_month`

**8. 缺少时是否停止输出 strong？**
是。合取逻辑，同上。

**9. 真实反例或证据冲突？**
- 反例：寅月甲日主（同为木月但非卯）→ 条件 False → indeterminate。这是保守性体现：原文未明确排除寅月，但实现选择不裁定。
- 冲突：s024 分日口径（寅月分日）与本条件无关，因本条件不依赖具体日司令。

**审核结论**: ⚠️ **保守实现假设**（比原文更严格）。古籍支持"本气为主"，**不支持**"仅卯月"的排他性。**不能推出**：卯月即强；亦**不能推出**：寅月木一定不强（只是本 Variant 不裁定）。

---

### 强-3: all_positions_support_only

**1. 此条件为什么存在？**
从象原文"无官杀之制"、"绝无一毫财星官杀之气"要求全局无反向势力。本条件将其操作化为：所有显干与藏干的作用关系必须属于 `support_relations`（印比方向）。

**2. 支持它的古籍短引？**
- 从象 char 96521："无官杀之制，有印绶之生"
- 从象 char 96605："绝无一毫财星官杀之气"

**3. Source ID、Section ID？**
- Source: `bazi.source.ditiansui-spouse`
- Section: 从象章节（具体 Section ID 待查）

**4. 证据支持整体还是部分？**
**整体状态描述，非分解条件**。原文说的是"旺之极者"的整体特征，本条件将其分解为"每个位置的作用关系都属于支持类"。这是一个**合理的保守转译**，但原文未定义"支持"的精确外延（如是否含"泄"）。

**5. 适用流派和 Variant？**
任氏原文自称立说；`bazi-strength-adjudication-v1`

**6. 现有程序如何计算？**
`bazi_action_conditions.py` 第 33 行：
```python
'all_positions_support_only': all(r['fact']['relation'] in supports for r in visible + hidden),
```
其中 `supports = tuple(policy['support_relations'])`，政策值应为 `('generates_me', 'same_element')`（印、比）。检查**所有**显干关系（visible）和藏干关系（hidden）。

**7. 能否从真实四柱和 Trace 复算？**
能。需要：
- Trace `bazi.phase2.action_conditions` 的 `visible_relations` + `hidden_relations` 中每条的 `fact.relation`
- 政策 `support_relations` 值

**8. 缺少时是否停止输出 strong？**
是。合取逻辑。

**9. 真实反例或证据冲突？**
- **真实反例**：TJ-010.3 的 2023-03-08（癸卯 乙卯 乙丑 壬午）：卯月乙日主，但午火（泄）存在 → 某 relation 为 `i_generate` 或 drain 方向 → 本条件 False → indeterminate ✅（系统正确弃判）
- **真实反例**：癸卯/乙卯/乙亥/丙子：丙火泄 → indeterminate ✅
- 冲突：无。但注意"泄"是否算"反向势力"在原文中未明确，本实现将其排除在 supports 之外，属于保守选择。

**审核结论**: ✅ 古籍整体支持 + 保守转译。**不能推出**："有印比"即强（还需其他条件）；**不能推出**：原文的"无官杀"精确等价于本实现的外延。

---

### 强-4: visible印_present

### 强-5: visible比_present

**1. 此条件为什么存在？**
与强-4 对称，从旺要求"纯粹印比"。本条件要求显干中至少有一个同类关系（比）。

**2. 支持它的古籍短引？**
- 从象 char 96521/96605 的"纯粹"表述（隐含印比结构）
- s043 众寡；s027 月令："通根得气才可谈具体生化"

**3. Source ID、Section ID？**
- Source: `bazi.source.ditiansui-spouse`
- Section: 从象章节（待查）；s027、s043（辅助）

**4. 证据支持整体还是部分？**
**部分，且比强-4 更弱**。原文未明确说"必须有显比"，本条件是与"纯印比"命名对应的实现选择。属于**未验证假设**——原文的"纯粹"可能指"无杂气"而非"印比兼备"。

**5. 适用流派和 Variant？**
任氏；`bazi-strength-adjudication-v1`

**6. 现有程序如何计算？**
`bazi_action_conditions.py` 第 35 行：
```python
'visible比_present': any(r['fact']['relation'] == 'same_element' for r in visible),
```

**7. 能否从真实四柱和 Trace 复算？**
能。同强-4，检查 `fact.relation == 'same_element'`。

**8. 缺少时是否停止输出 strong？**
是。合取逻辑。

**9. 真实反例或证据冲突？**
- 潜在反例：重印无比的卯月木（如三水一木）→ 本条件 False → indeterminate。原文是否允许"纯印无 比"？**未明确**。
- 冲突：无。但这是三个显干条件中古籍依据最弱的一个。

**审核结论**: ⚠️ **未验证假设**。**不能推出**：有比即强；亦**不能推出**：原文要求"印比兼备"。

---

### 强-6: effective_day_roots

**1. 此条件为什么存在？**
从象要求"有根"——无根之木不能言旺。s026 明列"甲乙逢亥寅卯"为木根。本条件要求：存在结构根，且所有根的可用性为 effective。

**2. 支持它的古籍短引？**
- 滴天髓 s026、s033：衰旺 char 39893 / line 1613；"甲乙逢亥寅卯"
- 从象 char 96521："旺之极者"隐含有根前提
- s043："通根得气才可谈具体生化"

**3. Source ID、Section ID？**
- Source: `bazi.source.ditiansui-spouse`
- Section: s026、s033、s043

**4. 证据支持整体还是部分？**
**整体中的关键部分**。s026 支持"甲乙有特定根位置"，s043 支持"通根是谈生化的前提"。但"所有根都必须 effective"（无一例外）是**保守实现假设**——原文未说"一根受损即不旺"。

**5. 适用流派和 Variant？**
任氏；`bazi-strength-adjudication-v1`

**6. 现有程序如何计算？**
`bazi_action_conditions.py` 第 36-37 行：
```python
'effective_day_roots': availability['root_presence']
    and all(r['root_availability'] == 'effective' for r in availability['roots']),
```
两重要求：(a) 结构上有根（`root_presence`）；(b) **所有**根的 `root_availability` 为 `'effective'`（非 conditional/unresolved）。

**7. 能否从真实四柱和 Trace 复算？**
能。需要：
- Trace `bazi.phase2.root_availability` 的 `root_presence` 和 `roots[].root_availability`
- 每个根的 `blockers`（`root_type_not_in_reviewed_scope`、`branch_interaction_effect_unresolved` 等）

**8. 缺少时是否停止输出 strong？**
是。合取逻辑。另在 `_bounded_assessment` 第 132-133 行有独立校验：
```python
and roots['root_presence']
and all(r['root_availability'] == 'effective' for r in roots['roots'])
```
以及第 118-120 行：任何 `root_availability != 'effective'` 的根直接产生 blocker。

**9. 真实反例或证据冲突？**
- **真实反例**：辛酉/乙卯/甲子/丙寅（酉冲卯）：卯根受冲 → `branch_interaction_effect_unresolved` → 非 effective → indeterminate ✅
- **真实反例**：戊午/辛酉/甲寅/庚午（酉月有寅根）：非卯月场景，但说明根检查有效
- 冲突：s038–040 论冲"须看强弱喜忌"，本实现将受冲根标为非 effective 而非直接删除，符合"冲相关根标 conditional 并保留结构"的审核结论。

**审核结论**: ✅ 直接古籍支持（s026 根表、s043 通根前提）+ 保守的"全部有效"假设。**不能推出**：有根即强；**不能推出**：原文要求"所有根无瑕疵"。

---

### 强-7: all_visible_have_reviewed_roots

**1. 此条件为什么存在？**
s043："通根得气才可谈具体生化；地支人元需天干引助"。本条件要求每个显干作用都有已审核的根位置支撑，防止"无根之干"参与生扶判定。

**2. 支持它的古籍短引？**
- 滴天髓 s043 众寡；s027 月令
- B部分审核表："地支人元需天干引助"

**3. Source ID、Section ID？**
- Source: `bazi.source.ditiansui-spouse`
- Section: s027、s043

**4. 证据支持整体还是部分？**
**部分**。s043 支持"通根是谈生化的前提"，但本条件要求**每个**显干都有已审核根（`all(eligible)`），是**保守实现假设**。原文未说"一干无根即全局不旺"。

**5. 适用流派和 Variant？**
任氏；`bazi-strength-adjudication-v1`

**6. 现有程序如何计算？**
`bazi_action_conditions.py` 第 20-23 行先计算每个显干的 `eligible` 根：
```python
for row in visible:
    fact = row['fact']
    roots = [r for r in fact['root_positions']
             if r['branch'] in policy['reviewed_root_branches'].get(fact['element'], [])]
    eligible.append(roots)
```
第 38 行：
```python
'all_visible_have_reviewed_roots': all(eligible),
```
要求每个显干的 `eligible` 列表非空。

**7. 能否从真实四柱和 Trace 复算？**
能。需要 Trace `bazi.phase2.action_effects` 的 `visible_relations[].eligible_root_positions` 非空。

**8. 缺少时是否停止输出 strong？**
是。合取逻辑。

**9. 真实反例或证据冲突？**
- 潜在反例：某显干（如时干）在已审核根分支中无藏干 → eligible 为空 → indeterminate。是否合理？**待验证**：原文"地支人元需天干引助"主要针对印比，本实现将其泛化到所有显干。
- 冲突：无直接冲突。

**审核结论**: ⚠️ **保守实现假设**。古籍支持"通根前提"，**不支持**"每干必有已审核根"的泛化。**不能推出**：某干无根即全局不旺（原文未如此说）。

---

### 强-8: no_unresolved_interactions

**1. 此条件为什么存在？**
从象要求"化与根冲合不得未解"（审核表 Section C 强行）。任何未解决的合冲刑害都可能改变根或作用的有效性，必须先 abstain。

**2. 支持它的古籍短引？**
- 审核表 Section C 强行："化与根冲合不得未解"
- s038–040：冲须看强弱喜忌
- 合化相关：合存在与成化不是同一事实

**3. Source ID、Section ID？**
- Source: `bazi.source.ditiansui-spouse`
- Section: s038–s040；审核表 Section C

**4. 证据支持整体还是部分？**
**整体支持**。这是审核表明确列为强充分条件支持条件的一项，直接来自"化与根冲合不得未解"。

**5. 适用流派和 Variant？**
任氏；`bazi-strength-adjudication-v1`

**6. 现有程序如何计算？**
`bazi_action_conditions.py` 第 18、39 行：
```python
interaction_kinds = [key for key in policy['unresolved_interactions'] if relations[key]]
...
'no_unresolved_interactions': no_interactions,  # not interaction_kinds
```
检查政策 `unresolved_interactions` 中的每种关系（五合、六合、六害、六冲、三合等）在 `relations` 中是否存在。另在 `_bounded_assessment` 第 123-124 行：
```python
if effects['unresolved_interaction_kinds']:
    block('action_effects','/unresolved_interaction_kinds','interaction_effect_unresolved')
```
直接产生 blocker。

**7. 能否从真实四柱和 Trace 复算？**
能。需要 Trace `bazi.phase2.action_effects` 的 `unresolved_interaction_kinds` 为空列表。

**8. 缺少时是否停止输出 strong？**
是。双重保障：条件 False 导致 pure=False；且直接产生 blocker 使 `not blockers` 为 False。

**9. 真实反例或证据冲突？**
- **真实反例**：辛酉/乙卯/甲子/丙寅（酉冲卯）→ `unresolved_interaction_kinds` 含六冲 → blocker → indeterminate ✅
- 冲突：s021 任氏"不取刑" vs 渊海三刑。本实现对刑保留 `punishment_status: unresolved`，符合"跨流派状态仍 unresolved"。

**审核结论**: ✅ 直接古籍支持（审核表 Section C 明确列出）。**不能推出**：无合冲即强（仅为必要条件）。

---

## 第一部分小结：强条件证据分级

| 条件 | 分级 | 说明 |
|---|---|---|
| wood_day_master | ✅ 直接支持 | s026/s033 根表 |
| reviewed_same_element_month | ⚠️ 保守假设 | "仅卯月"比原文更严格 |
| all_positions_support_only | ✅ 整体支持+转译 | "无官杀"转译为关系检查 |
| visible印_present | ⚠️ 保守假设 | "显印必要"原文未明确 |
| visible比_present | ⚠️ 未验证假设 | "显比必要"依据最弱 |
| effective_day_roots | ✅ 直接支持 | s026/s043 |
| all_visible_have_reviewed_roots | ⚠️ 保守假设 | "每干必有根"泛化 |
| no_unresolved_interactions | ✅ 直接支持 | 审核表 Section C 明确 |

**关键警告**：8 个条件中仅 4 个有直接古籍支持，其余为保守假设。古籍原文支持的是整体"从旺之极"状态，**不能将任一单个条件单独视为身强的充分条件**，更不能将"卯月""有木根""有印比"单独视为充分条件。

## 第二部分：弱充分条件（isolated_control_scope_conditions）

代码位置：`src/tianji_kb/bazi_action_conditions.py` 第 41-52 行
最终裁决：`src/tianji_kb/bazi_adjudication.py` 第 135-140 行

```python
isolated = (effects['isolated_control_scope_met']
    and all(effects['isolated_control_scope_conditions'].values())
    and command['month_branch'] == '酉' and command['relation'] == 'controls_me'
    and not roots['root_presence']
    and any(r['fact']['pillar'] == 'month' and r['effective_action'] == 'controls_me'
            and r['effect_status'] == 'effective_in_reviewed_context' for r in effects['visible_relations']))
```

---

### 弱-1: wood_day_master

**1. 此条件为什么存在？**
同强-1。本 Variant 限定木日主，因已审核的根表和月令关系仅覆盖木。

**2. 支持它的古籍短引？**
- 滴天髓 s026、s033："甲乙逢亥寅卯"
- 从象 char 96219 的"日主孤立无气"以日主状态为前提

**3. Source ID、Section ID？**
- Source: `bazi.source.ditiansui-spouse`
- Section: s026、s033；从象 s049（待查）

**4. 证据支持整体还是部分？**
**部分**。同强-1。

**5. 适用流派和 Variant？**
原注/任氏；`bazi-strength-adjudication-v1`

**6. 现有程序如何计算？**
`bazi_action_conditions.py` 第 42 行：`'wood_day_master': wood`（与强条件共享同一 `wood` 变量）。

**7. 能否从真实四柱和 Trace 复算？**
能。同强-1。

**8. 缺少时是否停止输出 weak？**
是。合取逻辑。

**9. 真实反例或证据冲突？**
无。非木日主酉月 → indeterminate，符合边界。

**审核结论**: ✅ 直接古籍支持。**不能推出**：木日主酉月即弱。

---

### 弱-2: reviewed_control_month

**1. 此条件为什么存在？**
"孤立"要求月令主气克制日主（官杀当令）。char 98032 明写"惟官星当令"。本 Variant 限定为已审核的酉月（金克木）。

**2. 支持它的古籍短引？**
- 从象 char 98032 / line 5028："日主休囚无根，惟官星当令"
- 从象 char 96219："日主孤立无气"

**3. Source ID、Section ID？**
- Source: `bazi.source.ditiansui-spouse`
- Section: 从象 s049、s051（待查具体映射）

**4. 证据支持整体还是部分？**
**部分**。原文支持"官星当令"是弱之极的特征，但限定**仅酉月**是**保守实现假设**（如申月金亦克木，但未纳入）。

**5. 适用流派和 Variant？**
原注/任氏；`bazi-strength-adjudication-v1`

**6. 现有程序如何计算？**
`bazi_action_conditions.py` 第 43-44 行：
```python
'reviewed_control_month': principal['month_branch'] in policy['isolated_months']
    and principal['status'] == 'reviewed_relation' and principal['relation'] == 'controls_me',
```
另在 `_bounded_assessment` 第 137 行冗余校验：`command['month_branch'] == '酉' and command['relation'] == 'controls_me'`。

**7. 能否从真实四柱和 Trace 复算？**
能。需要 `bazi.phase2.principal_month` 的 `month_branch`、`status`、`relation`。

**8. 缺少时是否停止输出 weak？**
是。合取逻辑。

**9. 真实反例或证据冲突？**
- 反例：申月甲日主（金克木但非酉）→ indeterminate。保守性体现。
- 冲突：无。

**审核结论**: ⚠️ **保守实现假设**（"仅酉月"比原文更严格）。**不能推出**：酉月即弱；**不能推出**：月干透辛即弱。

---

### 弱-3: day_has_no_structural_root

**1. 此条件为什么存在？**
"孤立无气"的核心是"无地人元"——结构上无任何木根。s026 定义木根位置，本条件要求结构根不存在。

**2. 支持它的古籍短引？**
- 从象 char 96219："无地人元"
- char 98032："日主休囚无根"
- s026："甲乙逢亥寅卯"（反向定义：无这些即无根）

**3. Source ID、Section ID？**
- Source: `bazi.source.ditiansui-spouse`
- Section: s026；从象 s049

**4. 证据支持整体还是部分？**
**整体中的核心部分**。原文"无根"是孤立状态的必要特征，本条件将其操作化为 `not root_presence`。这是**直接支持**最强的弱条件之一。

**5. 适用流派和 Variant？**
原注/任氏；`bazi-strength-adjudication-v1`

**6. 现有程序如何计算？**
`bazi_action_conditions.py` 第 45 行：
```python
'day_has_no_structural_root': not availability['root_presence'],
```
其中 `root_presence` 来自 `root_conditions` 的 `present_structurally`（是否有藏干为木的支）。

**7. 能否从真实四柱和 Trace 复算？**
能。需要 Trace `bazi.phase2.root_availability` 的 `root_presence` 为 False。

**8. 缺少时是否停止输出 weak？**
是。合取逻辑。另在 `_bounded_assessment` 第 138 行：`not roots['root_presence']`。

**9. 真实反例或证据冲突？**
- **真实反例**：戊午/辛酉/甲寅/庚午（酉月但有寅根）→ `root_presence=True` → indeterminate ✅（"无根不等于有根即强，但有根一定不弱"）
- **真实反例**：2024-09-17（甲辰 癸酉 甲申 庚午）：辰藏乙木 → 有根 → indeterminate ✅
- 冲突：无。但注意**"无根不等于身弱"**——本条件仅为必要条件，必须与其他条件合取。

**审核结论**: ✅ 直接古籍支持。**不能推出**：无根即弱（必须结合无生扶、官星当令等）；**不能推出**：有根即强。

---

### 弱-4: no_support_in_any_position

**1. 此条件为什么存在？**
从象"绝无一毫生扶之意"要求全局无任何生扶。本条件将其操作化为：所有显干+藏干的作用关系都不属于 `support_relations`。

**2. 支持它的古籍短引？**
- 从象 char 96219 / line 4903："绝无一毫生扶之意"
- 任氏："日主孤立无气，四柱无生扶之意"

**3. Source ID、Section ID？**
- Source: `bazi.source.ditiansui-spouse`
- Section: 从象 s049

**4. 证据支持整体还是部分？**
**整体状态描述的操作化**。原文"绝无一毫生扶"是孤立状态的核心特征，本条件将其转译为关系检查。转译合理但**"生扶"的外延**（是否含"泄"？）在原文中未精确定义。

**5. 适用流派和 Variant？**
原注/任氏；`bazi-strength-adjudication-v1`

**6. 现有程序如何计算？**
`bazi_action_conditions.py` 第 46 行：
```python
'no_support_in_any_position': all(r['fact']['relation'] not in supports for r in visible + hidden),
```
检查**所有**显干和藏干关系都不在 `supports`（印比）中。

**7. 能否从真实四柱和 Trace 复算？**
能。需要 `bazi.phase2.action_conditions` 的全部 visible+hidden relations。

**8. 缺少时是否停止输出 weak？**
是。合取逻辑。

**9. 真实反例或证据冲突？**
- **真实反例**：2018-09-10（戊戌 辛酉 乙巳 壬午）：酉月乙日主无根，但**壬水生扶** → 某 relation 为 `generates_me` → 本条件 False → indeterminate ✅（"无木根但存在壬癸印星时不能直接判弱"）
- **真实反例**：2018-09-30（戊戌 辛酉 乙丑 壬午）：同上 ✅
- 冲突：char 98032 提到"藏印伏而无气"——藏印存在但"无气"是否算"生扶"？本实现将任何 `generates_me` 关系都视为生扶，属于**保守选择**（宁可弃判）。

**审核结论**: ✅ 古籍整体支持 + 保守转译。**不能推出**：无生扶即弱（还需官星当令等）；**不能推出**："藏印无气"在本实现中被特殊处理（实际被视为生扶而弃判）。

---

### 弱-5: visible_earth_metal_only

**1. 此条件为什么存在？**
"孤立"状态下，显干应只有克泄耗（土金）而无生扶。本条件要求所有显干的五行仅为土或金。

**2. 支持它的古籍短引？**
- 从象 char 96219："孤立无气"的隐含结构
- char 98032："财官伤三者并旺"（财=土，官=金，伤=火——但本实现仅允许土金，**比原文更窄**）

**3. Source ID、Section ID？**
- Source: `bazi.source.ditiansui-spouse`
- Section: 从象 s049、s051（待查）

**4. 证据支持整体还是部分？**
**部分，且存在收窄**。char 98032 提到"财官伤三者并旺"（含火），但本实现仅允许土金（`('土', '金')`）。这是一个**未在审核表中明确说明的收窄假设**——可能为了排除火（火泄木，但火本身是否破坏"孤立"？原文未明确）。

**5. 适用流派和 Variant？**
原注/任氏；`bazi-strength-adjudication-v1`

**6. 现有程序如何计算？**
`bazi_action_conditions.py` 第 47 行：
```python
'visible_earth_metal_only': all(r['fact']['element'] in ('土', '金') for r in visible),
```
检查**所有显干**的五行属于土或金。

**7. 能否从真实四柱和 Trace 复算？**
能。需要 `bazi.phase2.action_conditions` 的 `visible_relations[].fact.element`。

**8. 缺少时是否停止输出 weak？**
是。合取逻辑。

**9. 真实反例或证据冲突？**
- 潜在反例：酉月木日主，显干有丙火（伤官）→ 本条件 False → indeterminate。但 char 98032 明确将"伤"列为弱之极的并旺者之一，**本实现将其排除可能过度保守**。
- **证据缺口**：审核表未明确说明为何排除火。需在 TJ-011.1 中记录此缺口。

**审核结论**: ⚠️ **未验证假设 + 可能过度收窄**。古籍（char 98032）提到"财官伤三者并旺"，本实现仅允许土金，**排除了火**。**不能推出**：原文支持"仅土金"的排他性。**建议**：在 TJ-011.1 中明确记录此收窄的依据缺口。

---

### 弱-6: month_principal_exposed_with_root

**1. 此条件为什么存在？**
"官星当令"需要实际作用：月干透出主气（辛），且该透干有已审核的根支撑（否则为"虚透"）。s027 强调"引助/透干"的条件意义。

**2. 支持它的古籍短引？**
- s027、s042：引助/透干有条件意义
- 审核表："显干有已审核可用根、作用链满足已审核范围"
- char 98032："惟官星当令"（隐含实际作用）

**3. Source ID、Section ID？**
- Source: `bazi.source.ditiansui-spouse`
- Section: s027、s042；从象 s051

**4. 证据支持整体还是部分？**
**部分**。s027 支持"透干有条件意义"，但"月干必须透主气且有根"这一**具体组合**是**实现假设**。原文未说"官星不透即不弱"。

**5. 适用流派和 Variant？**
任氏；`bazi-strength-adjudication-v1`

**6. 现有程序如何计算？**
`bazi_action_conditions.py` 第 48-50 行：
```python
'month_principal_exposed_with_root': any(r['fact']['pillar'] == 'month'
    and r['fact']['stem'] == principal['principal_qi'] and eligible[i]
    for i, r in enumerate(visible)),
```
三重要求：(a) 为月柱显干；(b) 干等于 `principal_qi`（主气，如辛）；(c) 该显干有已审核根（`eligible[i]` 非空）。

**7. 能否从真实四柱和 Trace 复算？**
能。需要：
- `bazi.phase2.principal_month` 的 `principal_qi`
- `bazi.phase2.action_effects` 的 `visible_relations[].eligible_root_positions`

**8. 缺少时是否停止输出 weak？**
是。合取逻辑。

**9. 真实反例或证据冲突？**
- **真实反例**：`test_weak_requires_month_stem_control_not_just_no_roots`：酉月无根但月干非辛 → indeterminate ✅（"月干透辛不等于身弱"的反向：不透辛则不弱）
- 冲突：无。但"必须透主气"的必要性在原文中**未明确**，属于保守假设。

**审核结论**: ⚠️ **保守实现假设**。古籍支持"透干有意义"，**不支持**"不透主气即不能判弱"的必要性。**不能推出**：月干透辛即弱（还需其他条件）。

---

### 弱-7: no_unresolved_interactions

**1. 此条件为什么存在？**
同强-8。未解的合冲可能引入生扶或改变根状态，必须 abstain。

**2. 支持它的古籍短引？**
- 审核表 Section C 弱行："未解合化不能可能引入支持"
- s038–040：冲的条件性

**3. Source ID、Section ID？**
- Source: `bazi.source.ditiansui-spouse`
- Section: s038–s040；审核表 Section C

**4. 证据支持整体还是部分？**
**整体支持**。审核表明确列为弱充分条件的支持条件。

**5. 适用流派和 Variant？**
任氏；`bazi-strength-adjudication-v1`

**6. 现有程序如何计算？**
同强-8（共享 `no_interactions` 变量，`bazi_action_conditions.py` 第 51 行）。

**7. 能否从真实四柱和 Trace 复算？**
能。同强-8。

**8. 缺少时是否停止输出 weak？**
是。双重保障（条件 False + blocker）。

**9. 真实反例或证据冲突？**
- 潜在反例：酉月无根无扶但有未解六合 → indeterminate。符合"五合、局部作用未解必须 abstain"。
- 冲突：无。

**审核结论**: ✅ 直接古籍支持。**不能推出**：无合冲即弱。

---

## 第二部分小结：弱条件证据分级

| 条件 | 分级 | 说明 |
|---|---|---|
| wood_day_master | ✅ 直接支持 | s026/s033 |
| reviewed_control_month | ⚠️ 保守假设 | "仅酉月"比原文更严格 |
| day_has_no_structural_root | ✅ 直接支持 | "无地人元"核心 |
| no_support_in_any_position | ✅ 整体支持+转译 | "绝无生扶"转译 |
| visible_earth_metal_only | ⚠️ 未验证+收窄 | 排除火，依据缺口 |
| month_principal_exposed_with_root | ⚠️ 保守假设 | "必透主气"原文未明确 |
| no_unresolved_interactions | ✅ 直接支持 | 审核表明确 |

**关键警告**：
1. **无根不等于身弱**：`day_has_no_structural_root` 仅为必要条件，必须与"无生扶""官星当令"等合取。
2. **酉月不等于身弱**：`reviewed_control_month` 仅为必要条件。
3. **月干透辛不等于身弱**：`month_principal_exposed_with_root` 仅为必要条件。
4. **无木根但有壬癸印星时不能判弱**：`no_support_in_any_position` 会将其拦截（2018-09-10/30 反例）。
5. **visible_earth_metal_only 存在证据缺口**：char 98032 提到"财官伤三者并旺"，本实现排除火，依据未在审核表中说明。

## 第三部分：最终裁决附加条件（_bounded_assessment）

除 15 个 scope 条件外，`_bounded_assessment`（`bazi_adjudication.py` 第 129-140 行）还有以下附加合取条件：

### 附加-1: 纯支持的月令冗余校验

```python
and command['month_branch'] == '卯' and command['relation'] == 'same_element'
```
- **作用**：与 `reviewed_same_element_month` 形成双重检查，防止 policy 篡改。
- **证据**：实现假设（防篡改），非古籍要求。

### 附加-2: 纯支持的根有效性冗余校验

```python
and roots['root_presence']
and all(r['root_availability'] == 'effective' for r in roots['roots'])
```
- **作用**：与 `effective_day_roots` 冗余，且第 118-120 行对非 effective 根直接产生 blocker。
- **证据**：实现假设（纵深防御）。

### 附加-3: 纯支持的显干作用状态校验

```python
and all(r['effect_status'] == 'effective_in_reviewed_context' for r in effects['visible_relations'])
```
- **作用**：确保每个显干的 `effect_status` 为 `effective_in_reviewed_context`（而非 unresolved）。这是 `action_effects` 中 `proved = pure or ...` 逻辑的结果。
- **证据**：实现假设。注意：此条件与 `pure_support_scope_met` 存在循环依赖（`proved` 依赖 `pure`，而 `pure` 又检查 `effect_status`），但因 `pure` 先计算，此处为一致性校验。

### 附加-4: 孤立控制的月令冗余校验

```python
and command['month_branch'] == '酉' and command['relation'] == 'controls_me'
```
- **作用**：同附加-1，防篡改。

### 附加-5: 孤立控制的无根校验

```python
and not roots['root_presence']
```
- **作用**：与 `day_has_no_structural_root` 冗余。

### 附加-6: 孤立控制的月柱实际作用校验

```python
and any(r['fact']['pillar'] == 'month' and r['effective_action'] == 'controls_me'
        and r['effect_status'] == 'effective_in_reviewed_context' for r in effects['visible_relations'])
```
- **作用**：要求月柱有一个实际生效的 controls_me 作用。这是 `month_principal_exposed_with_root` 的**作用层面**对应条件（前者是结构层面）。
- **证据**：实现假设。确保"官星当令"不仅是结构存在，而是实际生效。

---

## 第四部分：综合审核结论

### 证据分级统计

| 分级 | 强条件 | 弱条件 | 合计 |
|---|---|---|---|
| ✅ 直接古籍支持 | 4（1,3,6,8） | 4（1,3,4,7） | 8 |
| ⚠️ 保守实现假设 | 3（2,4,7） | 2（2,6） | 5 |
| ⚠️ 未验证假设 | 1（5） | 1（5） | 2 |

### 关键发现

1. **古籍支持的是整体状态，非分解条件**：从象原文描述"从旺之极""孤立无气"的整体特征，15 个分解条件中有 7 个是实现者为保守起见添加的假设（比原文更严格）。

2. **最弱的三个条件**：
   - 强-5 `visible比_present`：原文未明确要求"显比必要"
   - 弱-5 `visible_earth_metal_only`：排除火，char 98032 却提到"伤"，**存在证据缺口**
   - 强-4 `visible印_present`：原文未明确"显印必要"

3. **防篡改设计有效**：`_bounded_assessment` 的重放校验（第 99-108 行）和冗余合取条件可防止伪造 `pure_support_scope_met` 为 true 骗过裁决（TJ-010.3 篡改测试已验证）。

4. **真实反例覆盖**：
   - 强：2023-03-08/18（午火泄气）、癸卯/乙卯/乙亥/丙子（丙火泄）、辛酉/乙卯/甲子/丙寅（酉冲卯）
   - 弱：2018-09-10/30（壬水生扶）、戊午/辛酉/甲寅/庚午（有寅根）

### 不能推出的结论（永久边界）

1. 不能将"卯月""有木根""有印比"单独视为身强的充分条件。
2. 不能将"酉月""无根""透辛"单独视为身弱的充分条件。
3. 不能将本 Variant 的充分条件外推为通用旺衰算法。
4. 不能将 C 级单一电子版本升级为独立底本一致。
5. 不能用"代码可运行""测试通过"替代"证据充分"。

### 待查事项

1. 从象章节的具体 Section ID（对应 char 96521/96605/96219/98032）
2. `visible_earth_metal_only` 排除火的依据（需补充审核或放宽）
3. `visible比_present` 的古籍依据（或降级为"实现选择"并明确标记）

---

**审核人**：Muse（TJ-011.1 审核子任务）
**审核日期**：2026-10-18
**状态**：草稿，待主代理复核后纳入 TJ-011.1 正式交付

---

### 强-6: effective_day_roots

**1. 此条件为什么存在？**
从旺要求"通根得气"。无根则无从旺之基础。

**2. 支持它的古籍短引？**
- 滴天髓 s026、s033："甲乙逢亥寅卯"（衰旺 char 39893 / line 1613）
- s043："通根得气才可谈具体生化"

**3. Source ID、Section ID？**
- Source: `bazi.source.ditiansui-spouse`
- Section: s026、s033、s043

**4. 证据支持整体还是部分？**
**直接支持**。原文明确列出木之根位置，"通根"是生化的前提。

**5. 适用流派和 Variant？**
任氏；`bazi-strength-adjudication-v1`

**6. 现有程序如何计算？**
```python
'effective_day_roots': availability['root_presence']
    and all(r['root_availability'] == 'effective' for r in availability['roots']),
```

**7. 能否从真实四柱和 Trace 复算？**
能。Trace `bazi.phase2.root_availability` 输出。

**8. 缺少时是否停止输出 strong？**
是。合取逻辑。且 `_bounded_assessment` 第 132-133 行重复验证。

**9. 真实反例或证据冲突？**
- 反例：`戊午,辛酉,甲午,庚午`（无根）→ False → 不输出strong。正确。
- 无冲突。

**审核结论**: ✅ 直接古籍支持。**不能推出**：有根即强。

---

### 强-7: all_visible_have_reviewed_roots

**1. 此条件为什么存在？**
s027、s043：显干须有根引助，否则为"虚浮"。要求每个显干作用都有已审核的根支持。

**2. 支持它的古籍短引？**
- s027、s042："引助/透干、紧贴有条件意义"
- s043："地支人元需天干引助"

**3. Source ID、Section ID？**
- Source: `bazi.source.ditiansui-spouse`
- Section: s027、s042、s043

**4. 证据支持整体还是部分？**
**部分**。原文支持"透干需有根"，但"所有显干"的外延是实现选择。属于保守假设。

**5. 适用流派和 Variant？**
任氏；`bazi-strength-adjudication-v1`

**6. 现有程序如何计算？**
```python
'all_visible_have_reviewed_roots': all(eligible),
```
其中 eligible 检查每个 visible 的 root_positions 是否在 policy['reviewed_root_branches'] 中。

**7. 能否从真实四柱和 Trace 复算？**
能。Trace `bazi.phase2.action_effects` 的 eligible_root_positions。

**8. 缺少时是否停止输出 strong？**
是。合取逻辑。

**9. 真实反例或证据冲突？**
- 无直接反例。属于保守假设。
- 证据缺口：原文未证明"所有"显干的必要性。

**审核结论**: ⚠️ 保守实现假设。**不能推出**：原文要求所有显干有根。

---

### 强-8: no_unresolved_interactions

**1. 此条件为什么存在？**
s038-040：冲须看强弱；合化未决不能删根。存在未决相互作用时，根的有效性无法确定。

**2. 支持它的古籍短引？**
- s038-040；地支 char 11399 / line 355："冲须看强弱喜忌"
- 合化：地支合局不能删除原藏干

**3. Source ID、Section ID？**
- Source: `bazi.source.ditiansui-spouse`
- Section: s038-040

**4. 证据支持整体还是部分？**
**直接支持**。原文明确要求冲合需审查，未决时不能定论。

**5. 适用流派和 Variant？**
任氏；`bazi-strength-adjudication-v1`

**6. 现有程序如何计算？**
```python
'no_unresolved_interactions': no_interactions,
```
其中 `interaction_kinds = [key for key in policy['unresolved_interactions'] if relations[key]]`

**7. 能否从真实四柱和 Trace 复算？**
能。Trace `bazi.phase2.action_effects` 的 unresolved_interaction_kinds。

**8. 缺少时是否停止输出 strong？**
是。且 `_bounded_assessment` 第 126 行显式 block。

**9. 真实反例或证据冲突？**
- 反例：`辛酉,乙卯,甲子,丙寅`（酉冲卯）→ 有unresolved → indeterminate。正确。
- 无冲突。

**审核结论**: ✅ 直接古籍支持。**不能推出**：无冲合即强。

---

## 第二部分：弱充分条件（isolated_control_scope_conditions）

代码位置：`src/tianji_kb/bazi_action_conditions.py` 第 42-53 行

### 弱-1: wood_day_master
同强-1。**审核结论**: ✅ 直接古籍支持 + 保守实现假设。**不能推出**：木日主即弱。

### 弱-2: reviewed_control_month

**1. 此条件为什么存在？**
从象"日主孤立"要求月主气克制。限定为已审核的酉月（辛金）。

**2. 支持它的古籍短引？**
- 从象 char 96219 / line 4903："日主孤立无气"
- 从象 char 98032 / line 5028："日主休囚无根，惟官星当令…弱之极者"
- s033-036本气

**3. Source ID、Section ID？**
- Source: `bazi.source.ditiansui-spouse`
- Section: 从象（s049、s051待查）；s033-036

**4. 证据支持整体还是部分？**
**部分**。原文支持"官星当令"，但"仅酉月"的排他性是实现限定。属于保守假设。

**5. 适用流派和 Variant？**
任氏/原注；`bazi-strength-adjudication-v1`

**6. 现有程序如何计算？**
```python
'reviewed_control_month': principal['month_branch'] in policy['isolated_months']
    and principal['status'] == 'reviewed_relation' and principal['relation'] == 'controls_me',
```

**7. 能否从真实四柱和 Trace 复算？**
能。Trace `bazi.phase2.principal_month`。

**8. 缺少时是否停止输出 weak？**
是。合取逻辑。

**9. 真实反例或证据冲突？**
- 反例：申月木日主 → 不在isolated_months → indeterminate。符合"不扩展"边界。
- 无冲突。

**审核结论**: ⚠️ 保守实现假设。**不能推出**：酉月即弱；**不能推出**：申月木一定不弱（只是不裁定）。

### 弱-3: day_has_no_structural_root

**1. 此条件为什么存在？**
从象"无地人元"——无根是孤立的前提。

**2. 支持它的古籍短引？**
- 从象 char 96219："无地人元，绝无一毫生扶之意"

**3. Source ID、Section ID？**
- Source: `bazi.source.ditiansui-spouse`
- Section: 从象 s049

**4. 证据支持整体还是部分？**
**直接支持**。"无地人元"即无根。

**5. 适用流派和 Variant？**
原注/任氏；`bazi-strength-adjudication-v1`

**6. 现有程序如何计算？**
```python
'day_has_no_structural_root': not availability['root_presence'],
```

**7. 能否从真实四柱和 Trace 复算？**
能。Trace `bazi.phase2.root_availability`。

**8. 缺少时是否停止输出 weak？**
是。且 `_bounded_assessment` 第 138 行重复验证 `not roots['root_presence']`。

**9. 真实反例或证据冲突？**
- 反例：2018-09-10（有辰根藏乙）→ 有根 → 不输出weak。正确。
- 关键：**无根≠弱**，还需其他条件。本实现正确要求合取。

**审核结论**: ✅ 直接古籍支持。**不能推出**：无根即弱。

### 弱-4: no_support_in_any_position

**1. 此条件为什么存在？**
从象"绝无一毫生扶之意"——任何位置都不能有生扶。

**2. 支持它的古籍短引？**
- 从象 char 96219："绝无一毫生扶之意"

**3. Source ID、Section ID？**
- Source: `bazi.source.ditiansui-spouse`
- Section: 从象 s049

**4. 证据支持整体还是部分？**
**直接支持**。原文明确"绝无一毫"。

**5. 适用流派和 Variant？**
原注/任氏；`bazi-strength-adjudication-v1`

**6. 现有程序如何计算？**
```python
'no_support_in_any_position': all(r['fact']['relation'] not in supports for r in visible + hidden),
```

**7. 能否从真实四柱和 Trace 复算？**
能。Trace `bazi.phase2.action_conditions` 的 visible+hidden relations。

**8. 缺少时是否停止输出 weak？**
是。合取逻辑。

**9. 真实反例或证据冲突？**
- 反例：2018-09-10（有壬水印）→ 有support → indeterminate。正确。
- 这是 TJ-010.3 的重要发现：无根但有印不能判弱。

**审核结论**: ✅ 直接古籍支持。**不能推出**：无生扶即弱（还需无根+月令克制）。

### 弱-5: visible_earth_metal_only

**1. 此条件为什么存在？**
孤立状态下，显干应仅为克泄耗（土金为官杀/财），不能有印比。

**2. 支持它的古籍短引？**
- 从象"孤立无气"的整体描述
- **无直接原文支持"仅土金"的外延**

**3. Source ID、Section ID？**
- Source: `bazi.source.ditiansui-spouse`
- Section: 从象（整体）

**4. 证据支持整体还是部分？**
**未验证假设**。原文说"无生扶"，本实现转译为"显干仅土金"。土生金、金克木，逻辑上成立，但原文未明确列出允许的五行。

**5. 适用流派和 Variant？**
任氏；`bazi-strength-adjudication-v1`

**6. 现有程序如何计算？**
```python
'visible_earth_metal_only': all(r['fact']['element'] in ('土', '金') for r in visible),
```

**7. 能否从真实四柱和 Trace 复算？**
能。Trace visible relations 的 element。

**8. 缺少时是否停止输出 weak？**
是。合取逻辑。

**9. 真实反例或证据冲突？**
- 潜在问题：若显干有火（泄），按五行生克火泄木，也是"无生扶"，但本条件会 False。属于**比原文更严格**。
- 证据缺口：原文未枚举允许的五行。

**审核结论**: ⚠️ **未验证假设**。逻辑合理但无直接古籍支持。**不能推出**：原文限定仅土金。

### 弱-6: month_principal_exposed_with_root

**1. 此条件为什么存在？**
s027透干：月令主气须透出且有根，才能形成有效克制。

**2. 支持它的古籍短引？**
- s027、s042："引助/透干"
- 从象 char 98032："惟官星当令"

**3. Source ID、Section ID？**
- Source: `bazi.source.ditiansui-spouse`
- Section: s027、从象

**4. 证据支持整体还是部分？**
**部分**。原文支持"官星当令"，但"透干+有根"的具体实现是保守转译。

**5. 适用流派和 Variant？**
任氏；`bazi-strength-adjudication-v1`

**6. 现有程序如何计算？**
```python
'month_principal_exposed_with_root': any(r['fact']['pillar'] == 'month'
    and r['fact']['stem'] == principal['principal_qi'] and eligible[i]
    for i, r in enumerate(visible)),
```

**7. 能否从真实四柱和 Trace 复算？**
能。需要 principal_qi + visible month relation + eligible roots。

**8. 缺少时是否停止输出 weak？**
是。合取逻辑。

**9. 真实反例或证据冲突？**
- 反例：酉月但月干不透辛 → False → indeterminate。正确（月干透辛≠身弱，但不透则不能判弱）。
- 无冲突。

**审核结论**: ⚠️ 保守实现假设。**不能推出**：月干透辛即弱。

### 弱-7: no_unresolved_interactions
同强-8。**审核结论**: ✅ 直接古籍支持。**不能推出**：无冲合即弱。

---

## 审核总结

### 条件统计
- 强充分条件：8 条
  - 直接古籍支持：4 条（S3、S6、S8、部分S1）
  - 保守实现假设：3 条（S2、S4、S7）
  - 未验证假设：1 条（S5 visible比_present）
- 弱充分条件：7 条
  - 直接古籍支持：3 条（W3、W4、W7）
  - 保守实现假设：3 条（W1、W2、W6）
  - 未验证假设：1 条（W5 visible_earth_metal_only）

### 关键发现
1. **无过度宽松**：所有条件均为"直接支持"或"保守（更严格）"，无条件比原文更宽松。实现是安全的。
2. **两个未验证假设**需明确记录：
   - S5：原文未明确要求"显比必要"
   - W5：原文未明确限定"仅土金"
3. **C级证据**：所有古籍依据仍为C级单一电子版本，不能升级。
4. **不能推出的结论**已在每条中明确。

### 是否需代码修复？
**否**。未发现过度宽松的条件。两个未验证假设均为保守方向（更严格），不会导致错误输出 strong/weak，只会导致更少的情况被裁定。这是研究 Variant 可接受的。

建议：在审核矩阵文档中明确标记这两个缺口，不修改代码。
