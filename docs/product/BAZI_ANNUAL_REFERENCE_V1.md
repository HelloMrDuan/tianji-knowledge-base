# 八字流年历法参照 v1（研究入口）

## 实现与用途

本批交付**真实可调用的流年历法参照**，不是“AI 随机运势”。使用仓库固定版本 `lunar-python==1.4.8`，对用户指定的 1–20 个升序不重复的公历年份，以 `Asia/Shanghai` 的**7月1日12时**为取样时点，读取该时点真实 `year_ganzhi`，再复用已审核的日主十神映射，生成可追溯表格。

原典证据来自现有 `bazi.rule.r001`（四柱以日干为主）和 `bazi.rule.r002`（十神），而“7月1日参考时点”是软件算法产品选择，**不是原典关于全年起止或流年作用的断言**。结果返回 `bazi.phase2.annual_reference_facts` 的实际 Trace 和 Evidence，不通过 AI 凭空生成；默认四柱结构接口原样不变。

## 可执行研究调用

```json
{
  "domain": "bazi",
  "mode": "research",
  "explain": false,
  "input": {
    "value": "2000-01-07T12:00:00+08:00",
    "annual_reference_years": [2024, 2025, 2026]
  }
}
```

POST 到现有 `/api/v1/execute`。响应 `chart.annual_reference.rows` 中每行包含公历年、准确参考时点、干支、年干与年支、相对十神、provider。也可使用已确认的手动四柱输入。所有研究请求需 `mode=research`，不得在生产接口靠添加字段绕过；`annual_reference_years` 非整数、重复、乱序、空数组、超出 1900..2099 或超过20年均拒绝。

## 明确不支持的部分

1. **未提供全年生效区间**：公历元旦不等于立春，7月1日是年干支参照时点，不能将该行据以解释1月/2月节气边界。需要真正的立春精确交界及其校验后才能升级。
2. **未计算大运顺逆、起运岁数和交运时间**：旧 `dayun_v1.json` 属于外部旧资料，不因本接口而被晋级为审核算法。
3. **未计算流年对原局的作用**：十神是关系标签，不是喜忌、强弱、凶吉、事件预测。字段 `annual_natal_interaction_status=not_evaluated`、`annual_luck_prediction=null`、`annual_boundary_calculated=false` 必须保留；不开放 AI/公开解释。

下一步应完成立春精确边界的可信历法验收，再审大运起运法的流派分歧，而不是套用“3天1岁”口诀做无审计推断。
