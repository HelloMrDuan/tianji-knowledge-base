# 旺衰首批：月令、通根候选与透藏

本批沿用七域 Phase1/Phase2 模型、来源登记、Conflict、晋级记录和 Golden，没有另建知识库。执行子范围 `ditiansui-root-visibility-v1` 挂在现有 `ziping-structural-v1`，必须显式选择；基础接口默认行为保留。

这是旺衰因素观察的 PARTIAL 第一批，**整体身强身弱分类器尚未完成**。不能把三条结构规则、六个 Golden 或本批合并当成完整旺衰验收通过。

## 来源与审核

已有来源 `bazi.source.ditiansui-spouse`、`bazi.source.yuanhai` 均固定在 daizhigev20 `4a6d6f2088825f132521d848c2ea86cf9c9a7620`，等级 C。原始快照和字面 SHA 不改；已有 acquisition.stage_candidate 的 RAW / Quarantine 复核候选继续 pending，整本不晋级。仅所列七条短引经过逐字审核进入既有 Canonical 实体。

- 《滴天髓阐微》月令：s023（提纲）、s024（寅月分日）、s027（地支人元与天干引助）。
- 《滴天髓阐微》衰旺：s025（比肩不能数量等同于根）、s026（余气与长生禄旺根示例）、s028（得时即旺是死法）。
- 《渊海子平》暗藏总诀：s029 保留“立春念三丙火用”的原字，不擅改或换算日数。
- 三条观察规则同时引用既有 s004 藏遁歌；经典语句没有定义通用百分比权重。

每段 locator 保存到原始隔离快照的字符位置；Section → SourceRef → Source → SHA/commit → 原文逐字可查。RAW 对照复用现有 normalize_text；不据清洗后的标点差异改原始文本。

对照[维基文库《滴天髓阐微》](https://zh.wikisource.org/zh-hant/滴天髓闡微)时发现多个疑字与仓库转写一致。**这不是已经证实独立的刊本**，不计独立证据票、不升级 A/B，也不补齐疑字后冒充原文。

## 规则与执行

| Phase1 | Phase2 | 已执行范围 | 仍未执行 |
|---|---|---|---|
| r013 | month_command_factors | 月支、月支藏干、日主同五行藏干位置 | 分日司令、得令、整体旺衰 |
| r014 | root_candidates | 四支藏干中的同五行通根候选，同字与异字分开 | 根力权重、冲刑自动消根、强弱评分 |
| r015 | hidden_to_visible | 藏干在年/月/时天干同字出现的位置 | 日干自证透干、取格、取用、得势 |

`bazi.concept.conflict_siling_days` 保留两段分日材料，status=unresolved。只执行共同的月支/藏干结构，不使用未裁定的司令表。`bazi.concept.strength_factor_variant_v1` 明列不支持的范围和 `full_strength_classifier_ready=false`。

Golden 正常例、墓库边界、干多无根、干少有根、冲根不自动抹除、司令未决六例均手工固定期望，没有从执行结果自动生成“正确答案”。新增阴日干异字同五行候选、默认关闭、错误 Variant、场景接线和逐条引文检查。

## API / Scenario

沿既有 `/api/v1/execute` 调用八字，或 `/api/v1/scenarios/execute` 调用 `bazi-profile`：

```json
{
  "value": "2000-01-01T12:00:00+08:00",
  "strength_variant": "ditiansui-root-visibility-v1"
}
```

返回 `strength_factors`，每条因素有实际 RuleMatch / Trace / Evidence。可绑定 `bazi.month_command_factors`、`bazi.root_candidates`、`bazi.hidden_to_visible` 三个结构 claim。缺少该选项或规则未执行时拒绝 claim；`bazi.yongshen`、整体强弱、婚期等继续拒绝。AI 保持未批准，不改变模型配置。

为在本机验证真实执行，本批同时修复既有 runtime manifest 的 Windows 路径问题：统一 POSIX 相对路径，继续拒绝越界、反斜线别名和文件漂移；不降低来源或路径校验。

## 后续验收

下一批优先核季节旺相休囚、司令分日异文、有效根力和生扶克泄耗条件；取得可审核的综合判断条件、反例和流派限制后，才能推进整体旺衰 Variant。格局、喜用和岁运高级解释仍依赖这些未完成项。不能先写通用身强身弱判断再找引文。
