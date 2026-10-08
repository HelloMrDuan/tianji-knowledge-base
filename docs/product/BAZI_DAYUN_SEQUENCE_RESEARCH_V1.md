# 八字大运：月柱相邻干支候选序列 v1（仅研究，待审核）

## 第 156 批实际能力

沿用 `POST /api/v1/execute`、`bazi` Phase2 四柱与十神映射、Trace/Evidence、固定的六十甲子 `CYCLE`，在调用者**显式指定候选方向**时，计算从月柱起顺行或逆行的连续干支和各干对日主的十神。默认 8 个候选，可指定 1–12 个。对每项只返回干支结构、序号、十神；**不计算起运时间、交运年月、实际年龄、运势**。

本实现不是已经验证的「大运起运规则」；`data/canonical/bazi/dayun_v1.json` 来源为 `jinchenma94/bazi-skill/references/dayun-rules.md`，其所述阳男/阴女顺行、节令天数÷3、余日换算均**尚未获得 Canonical Phase1/Phase2 审核**。为避免借既有四柱 C 级证据伪装大运方法为已审核，本批**不添加大运 Phase2 Rule，也不生成对应的 RuleMatch/证据编号**。候选结果指向已校验的月柱 fact `#/trace/0/output/ganzhi/1`，并引用既有十神结构 Rule ID；这两个事实链不构成对「大运取法」的古籍背书。

## 可调用的研究 API

```json
{
  "domain": "bazi",
  "mode": "research",
  "explain": false,
  "input": {
    "value": "2000-01-07T12:00:00+08:00",
    "dayun_sequence_direction": "forward",
    "dayun_sequence_count": 8
  }
}
```

如已有合法人工四柱，也可用 `year_ganzhi`、`month_ganzhi`、`day_ganzhi`、`hour_ganzhi` 代替 `value`，不得两种来源混用。方向只能是 `forward` / `backward`，不得根据上传性别或年干自行隐式推断。结果位于 `result.dayun_sequence_research`，首项**不包括本命月柱**。所有年龄、日期与效果字段固定为 `null`，`ai_enabled=false`、`public_enabled=false`。生产模式请求被拒绝，默认四柱完全不改变。

示例：本命月柱 `己丑`、日主 `甲`、方向 `forward`，前三个候选分别为 `庚寅/七杀`、`辛卯/正官`、`壬辰/偏印`。这是已定义符号的确定性演算及人工固定预期，并非命主在某十年必经历任何事件。

## 继续受阻的关键问题

1. **顺逆取法**：核验古籍片段、时代语境、年干阴阳与传统性别分类的适用性，记录流派差异；不得将历史规范变为现代用户属性推断。
2. **起运节界**：前后十二节的选择、立春/惊蛰等实际交节时间、极近交节的前后秒、出生时区和历史时区/真太阳时策略；固定历法库 `lunar-python==1.4.8` 本身尚非独立天文精度认证。
3. **年龄与交运日期**：节令时间差、三日一年等换算法的版本/四舍五入、岁数虚实、闰日与跨年月、实际交运瞬间均需独立裁定、边界 Golden。
4. **作用与解释**：完整旺衰、格局、喜用、岁运相互作用未闭环，不能输出健康/事业/婚姻/财富等确定性判断。

`tests/test_phase2_bazidayun.py` 提供固定向前、向后、循环折返及错误输入回归；**不是** `data/canonical/bazi/phase2_golden.json` 中已审核 Golden。产品覆盖的「bazi-dayun」仍应保持缺口状态，不升级为 READY。新增 Python 文件纳入已有运行时 Manifest/校验链，必须由 CI 实测通过后才能合并。

此批不公开知识库内部原文，不改变知识库权限与 AI 放行。
