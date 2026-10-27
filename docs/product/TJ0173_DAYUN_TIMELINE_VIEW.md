# TJ-017.3 大运时间轴用户可读视图：落点与口径裁定（2026-10-27）

本批在 TJ-017.4 组合入口 `classical_dayun_timeline` 之上落地视图层
`bazi_dayun_timeline_view.py`（Variant `dayun-timeline-view-v1`）：
把组合结果确定性构造为用户可读的时间轴视图数据（逐运干支与起始
时刻区间、区间依据分解、方法选择、逐方法出处），不产生任何新规
则、新裁定，不改 TJ-017.1/017.4 的任何计算与输出。全部工件
research_only，public/ai 关闭，生产 dayun 显示口径不变。

## 1. WBS 定义核对（先行审计）

WBS TJ-017.3 原文行：「用户可读时间轴视图 | 允许方法选择与来
源；未知/争议交运年份用空态，而不是拟制时间」。与本批任务书一
致，无冲突。台账 TJ-017.3 行此前为阻塞（等待证据/前置依赖）；
其前置（TJ-017.1 区间契约、TJ-017.4 组合入口）均已部署验收，
阻塞原因已消解，本批即该任务的实现批（行状态按关账口径另行处
理，不在本批虚进）。

既有呈现资产审计：

- 前端公开页面中与大运相关的只有诚实未裁定说明：八字命理页
  （「大运起运仍未完成证据裁定」「不计算大运起运岁数」）与人生
  总览场景文本（「本总览不推算或伪造大运时间线」，
  `dayun_timeline_approved: False`）。不存在既有大运时间轴组件
  可接线。
- TJ-014.2 候选序列、TJ-015 节距测量、TJ-016 换算登记与
  TJ-017.1/017.4 古典链全部 research_only / public_enabled=False；
  TJ-016.3 已立研究模拟与正式运期的硬边界（公开无暴露断言）。
  公开投影对研究键的防御剥离有 TJ-013.1/013.3、TJ-012.3 先例。

## 2. 落点裁定：后端研究层视图模型，不接公开页面

理由：(1) 全链 public_enabled=False 是已审治理状态，翻转它即改
变 TJ-017.1/017.4 的输出（红线禁止），且超出 TJ-014–016 既有公
开口径；(2) 视图所依赖的 Variant 尚未完成密封 Phase1 注册
（evidence_binding = pending_phase1_rule_registration），公开
开放属能力纲领「分阶段开放」阶段，须在注册完成后另行裁定；
(3) 与 TJ-013.3 研究级可读渲染的落点先例一致。本批同时在公开投
影层加防御性剥离（`dayun_timeline_view`/`dayun_timeline_views`
键），保证视图即使被误置于结果容器也不会到达公开响应。

## 3. 视图契约

- 输入：一个 `classical_dayun_timeline` 结果对象，逐字消费、绝
  不重算。治理标志被篡改、方向块未过 TJ-017.1 自校验
  （`validate_classical_direction` 重算核对）、所消费字段缺失
  或形态不符，一律 ValueError（fail-closed）。
- 方法选择：`method='sanming'`（三命时级，主口径，逐运起始区
  间）与 `method='shenfeng'`（神峰日级，并列口径）。两视图由同
  一组合结果构造（便捷入口 `classical_dayun_timeline_views` 以
  include_shenfeng=True 组合一次），原局四柱、方向、节距计数在
  两视图间逐字相同（专项钉死）；两口径永不合并、不取平均。
- 逐运条目：干支、干、支、对日主十神（序列事实透传）、起始时
  刻区间 `{earliest, latest, max_inclusive, basis, method,
  variant}`——逐字复制组合的序列时间对齐，不折算单点、不取中
  点。首运区间端点 = 出生时刻 + 时长区间端点（专项以日期算术
  钉住）。
- 时长呈现：三命给日数区间 + 换算自身的分解（年单位/余时/余
  日）+ 计数（整时数、亚时余秒及其只进上端的处理）+ approximate
  标志与近似依据；神峰给日数区间 + 原文结果日数 + 整日计数与
  日级粒度说明。
- 来源呈现：每视图带 sources 块（Variant + Source 登记 + 引
  文）。只呈现组合结果实际携带的引文：三命为方向规则句与卷十
  一见证（《三命通会》）及换算的交运依据句（converted 时）；
  神峰为《神峰通考·起大运法》例句三条（即神峰换算 Variant 自
  身的引用集）。换算比率诸句登记在 TJ-017.1 算术层结果中、组合
  层未嵌入，视图不越权补引，出处链以 Variant 与 Source 登记标
  明（模块 docstring 已披露此边界）。

## 4. 年龄口径裁定：不呈现年龄

古典起运为实历时长（TJ-017.1 审源：虚岁/实岁五书零命中、无年
龄原典）；「约 X 岁」折算需要无审定来源的年长约定，且既有公开
页面口径为「不计算大运起运岁数」。视图以 `age_presentation:
'not_presented'` 显式声明，全域无任何年龄数值字段（专项键扫
描钉死：含 'age' 的键只许该声明键本身）。

## 5. 空态清单（不拟制、不留空白冒充有值）

| code | 情形 | 呈现 |
|---|---|---|
| `zero_jie_boundary` | 出生恰逢节气交界（实历为零，ADV-001 口径） | 整图 status='unresolved'，时长与逐运区间均不给出，序列干支事实仍呈现并逐条标 unresolved |
| `shenfeng_zero_day_count` | 神峰整日计数为零（未见原文例） | 神峰视图 status='unresolved'（三命视图不受影响，反之亦然） |
| `approximate_birth_time` | 生刻不明/时辰级精度 | 区间按原文近似口径加宽后照常呈现，附提示：加宽不代表更精确 |
| `shenfeng_decade_shifts_not_provided` | 神峰口径第二运起 | 条目 state='not_provided'、区间为 None 并附状态说明，不以十年平移拟制 |
| （拒绝）`shenfeng_not_composed` | 请求神峰视图但组合未含神峰并列块 | ValueError fail-closed，视图层绝不临时补算并列口径 |
| （拒绝）角色缺失 | 组合入口要求 traditional_role 显式传入 | 组合层先行拒绝（视图便捷入口同口径），绝不由身份数据推断 |

争议口径（三命时级 vs 神峰日级同盘区间不同）以双口径并列呈现
（method_options 标明可选性与各自 Variant/Source），不作取舍；
notices 中恒有 `methods_presented_separately` 说明。

## 6. 测试分区

- 公开专项 `tests/test_tj0173_dayun_timeline_view.py`：Golden 视
  图期望与 TJ-017.4 Golden 的转写一致性；视图变换的区间保真、
  首运端点一致性、方法切换不变性、空态目录、禁用字段全域扫
  描、伪造拒绝、公开投影剥离。fixture 以真实前三阶段函数输出
  + TJ-017.4 Golden 转写的序列行按组合模块的字段映射组装（测
  试 docstring 明示其性质，不冒称组合结果）。
- 密封专项 `tests/test_tj0173_dayun_timeline_view_sealed.py`
  （仅离线验收，不接入公开 CI）：对全部 TJ-017.4 Golden 用例跑
  真实组合 → 双视图回验（区间逐字、Golden 期望、空态、生产图
  表面无视图输出）。

## 7. 未覆盖（不在本批）

- 公开页面开放与前端组件（待 Phase1 注册与分阶段开放裁定）；
- TJ-017.2 跨规则调用（独立任务，仍阻塞，与本视图无涉）；
- 神峰口径逐运平移（组合层未提供，本视图不拟制）；
- 任何大运吉凶、岁运作用、流年合用（TJ-023.3 后置）与预测性
  文案（永久禁止线）。
