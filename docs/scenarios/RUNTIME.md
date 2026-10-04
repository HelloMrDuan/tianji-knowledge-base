# Scenario Runtime API

产品层不直接让用户选择术数算法。Scenario Engine 负责把场景映射到已审核的确定性能力，同时保持能力边界。

## Endpoints

- `GET /api/v1/scenarios`：返回场景注册表、开放状态与依赖。
- `POST /api/v1/scenarios/execute`：执行已实现的场景。

请求：

```json
{
  "scenario_id": "yearly",
  "input": {
    "birth_value": "2000-01-07T12:00:00+08:00",
    "target_year": 2026
  }
}
```

当前可执行场景：

| scenario_id | 状态 | 对外状态 | 说明 |
|---|---|---|---|
| bazi-profile | production | 已开放 | 四柱、日主、十神、藏干 |
| question | production | 已开放 | 六爻确定性盘面、规则、Evidence、Trace |
| yearly | production_limited | 暂不公开自动解释 | 原局 + 目标干支年 + 流年天干十神结构 |

其余场景仍返回注册状态，但执行请求会 fail closed。

## yearly 当前边界

`yearly` 不是“年度吉凶报告”。

它当前只组合：

1. 已审核的八字结构引擎；
2. pinned `lunar-python==1.4.8` 年干支；
3. 已审核十神规则。

目标年份使用 7 月 1 日作为稳定的干支年取样点，避免把公历 1 月 1 日误当作传统干支年边界；响应会明确返回该约定。

当前不输出：

- 旺衰
- 喜用神
- 格局
- 流年吉凶
- 桃花吉凶
- 事业/财富评分
- 健康判断
- 事件应期

AI 不参与 Scenario Engine 的确定性计算。
