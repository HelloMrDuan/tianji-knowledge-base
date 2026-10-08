# 八字立春流年干支区间 v1（研究模式）

## 本批真正新增的能力

- 通过固定版本 `lunar-python==1.4.8` 的 `getJieQiTable()['立春']` 获取指定公历年的立春秒级时刻和下一年的立春时刻。
- 对研究型八字排盘可额外提交 `annual_boundary_years`（1–10 个升序、不重复整数，1900..2098），输出 `[start_inclusive, end_exclusive)` 半开区间、区间年干支与日主相对十神。
- 每个区间使用**同一个固定历法库的** `getYearInGanZhiExact` 复验立春前一秒、立春当秒、下一次立春前一秒与当秒。如果与历法库给定的六十甲子序列不一致，直接拒绝输出。记录 `provider_seconds` 与 `Asia/Shanghai`，不宣称未经第三方核验的天文秒级精度。
- 接入现有 `bazi.phase2.annual_li_chun_boundaries` 的 Trace/Evidence；经典来源仅支撑日主/立春月令背景，**具体节令秒值来自历法软件而非古籍原文**。
- 旧 `annual_reference_years` 七月一日参考功能完全保留，避免静默变更已通过的 143 个 Golden 或消费者结果。

## 研究 API 示例

```json
{
  "domain": "bazi",
  "mode": "research",
  "explain": false,
  "input": {
    "value": "2000-01-07T12:00:00+08:00",
    "annual_boundary_years": [2024, 2025, 2026]
  }
}
```

向已有 `POST /api/v1/execute` 提交。结果位于 `chart.annual_li_chun_boundaries.rows`。输入手动四柱亦可；请求必须明确 `mode=research`。默认排盘不额外输出此数据，AI 自动解释继续关闭。公历 2099 年不纳入本功能，因为其区间终点在 2100 年，已超出现有历法接口允许的 1900–2099 范围。

## 保留的不可推断项

- 这只是**传统立春为界的年柱历法变动**，不是完整大运排盘，也不是完整「流年运势」。
- 不实现大运顺逆、起运日期与年龄、真太阳时、原局喜忌、流年与原局作用、旺衰或任何财富/事业/桃花/婚恋吉凶断言。
- 立春时刻取值精确到固定历法库的秒，未与独立天文/时区历史数据交叉标定。不得称为权威的天文精度认证或跨学派统一口径。
- `annual_luck_assessment=null`、`effective_natal_interaction=null`，不可用 UI 把干支、十神标签转换为预测分数。

此批不晋级旧大运来源、不更改知识库私有权限、不授权公开解释。
