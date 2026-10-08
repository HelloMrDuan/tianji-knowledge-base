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

## 第 157 批：出生时刻到相邻十二节的真实历法库间隔

在第 156 批研究请求中额外提交 `"dayun_jie_distance": true`，必须同时有 **实际出生时间 `value`** 和显式 `dayun_sequence_direction=forward|backward`；人工四柱因缺出生瞬间会被拒绝。研究模式和 AI 禁用要求不变。返回 `result.dayun_sequence_research.jie_distance`，包含当地出生时刻、上一节、下一节、方向对应所选节、原始秒数、整日与余秒、交节当秒 `zero_distance`，并保留独立源版本、范围和未审核声明。

使用固定 `lunar-python==1.4.8` 的 `getPrevJie(False)`、`getNextJie(False)`：只接受十二个真正的**节**，不把雨水、春分等中气当作下一月令。算法按 `Asia/Shanghai` 归一出生时间并以 UTC 时间差计算实际秒数，兼顾时区偏移，随后使用该版本的 `getMonthInGanZhiExact` 间接经 `calendar` 对节交界前一秒、当秒、下一节前一秒及当秒进行交叉验证；不一致直接报错。

**精度与适用界限**：出生时刻必须是带时区的整秒，当前只支持中国当地 1901..2098 的出生年，避免跨过历法适用边界；节令秒值来自软件计算，未经独立天文校核。历法库对中国历史夏令时、地方时、真太阳时的对应关系仍未独立审计，标记为 `historical_timezone_independently_verified=false`。零距离的起运处理口径待审核，不能从它推断零岁交运。此研究操作**绝不运行三日折岁或计算交运日期**，这些字段显式为 `null`。出生到节的连续秒值属于事实测量，按何种传统规则折算大运年龄属于另一个尚未审核的判断。

### 原典审核待办（不能自动晋级）

《三命通会·卷二·论大运》有关于「阳男阴女」「阴男阳女」「未来/过去节气日时」「三日为年」的传统文字。已找到公开文本定位：

- `https://www.shidianguji.com/book/HY1521/chapter/1knwemh3lrtpj`
- `https://shuyuan.zhiming.life/read/三命通会/17`

这些是待审索引，**尚未核对项目固定 RAW 底本、版本、可发布权利与具体字符 SHA**。仓库内《三命通会》全文仍维持 `quarantine_only`，不因为找到网页短引就更新 Phase1 `source_refs`、Phase2、Golden 或对外声明“已审核”。应另批登记逐字短引、版本来源、冲突政策、边界实测及权利审批。

`tests/test_phase2_bazidayunjie.py` 含真实历法库的出生前后节边界、立春前一秒/当秒/后一秒、时区等价、非法输入和生产模式拒绝测试。现有 66 条已审核 Phase2 及 145 个 Golden 保持不变。

## 第 158 批：显式研究模式的折岁模拟、拟制时间轴（非交运裁定）

本批允许在出生时间 `value`、`dayun_sequence_direction`、`dayun_jie_distance=true` 同时存在时，再显式设置：

```json
"dayun_age_simulation": "bazi-dayun-three-days-mean-year-research-v1"
```

返回 `result.dayun_sequence_research.age_simulation`。在已经测出的真实十二节时间差 `elapsed_seconds` 基础上，将 **每 3 个完整的 24h 日长对应 1 个象征性年** 作为独立的研究 Variant。用不可约分数 `elapsed_seconds / 259200` 保存 `age_years_exact`，另有六位小数供展示。为演算一个可复算的**非权威模拟日历锚点**，采用固定公历平均年 `365.2425 × 86400 = 31,556,952 秒`；按有理数舍入到最近秒（正值 0.5 向上）后加到公历出生的 UTC 瞬间，再按每 10 个平均公历年延伸。它严格是人为声明的现代计时映射，不是古籍直接给出的换算公式。每一项输出 `simulated_start`、`simulated_end_exclusive` 和既有候选干支/十神。

- 原先的 `rows[].start_date/end_date/start_age/end_age`、真实 `jie_distance.start_age/handover_datetime` 保持 **null**。
- `actual_start_age_adjudicated=false`、`verified_handover_dates_calculated=false`、`classical_method_reviewed=false`；这组模拟时间 **不是** 可以公示的真实起运/交运日期。
- 不按传统男女、年干自动判断方向，不推算强弱喜忌或断吉凶；没有新增任何 Phase2 RuleMatch、Evidence 或已审核 Golden，默认公开页面也不会打开此功能。
- 交节当秒 `elapsed_seconds=0` 的起运口径未裁定，主动拒绝生成模拟时间；原始节令事实仍可单独查询。

### 可审的原典线索（非 Canonical 晋级）

《渊海子平》卷一《论起大运法》能定位顺逆、节、三日一年及传统性别口径，但公开流通版本中存在异文，部分校勘页明确记录原本和改字。对照入口：

- `https://www.yuceshu.cn/book/bazi/3_1_1_1_55.html`
- `https://huamuchengxi.com/chapter/12802.html`
- `https://www.shidianguji.com/book/SDZJ0626/chapter/1lhnc3bvvh5bo`

以上只是待审的版本定位，不能取代项目固定来源快照、引文逐字校勘及权利核实，也不能推定各种余日、余时或置闰折算共享同一个十年区间规则。仓库现有《三命通会》隔离状态不变。未经历史时区、历法与古籍流派完整治理，不授权 AI 将模拟日期解释为一生事业、财富、婚姻或健康结论。

固定回归测试：`tests/test_phase2_bazidayunsimulation.py` 验证真实历法库双方向、整数分数、秒级舍入、模拟区间相接、同瞬间时区一致、零距离弃判、非法 variant 拒绝和研究/生产隔离。产品 Web CI 增加真实 HTTP 请求。

## 第 159 批：固定底本可复查的起运原典短引（来源校勘，不是完整规则晋级）

新增内部离线资产 `data/research/bazi/dayun_source_collation_v1.json`、核验器 `src/tianji_kb/bazi_dayun_source_audit.py` 和不可篡改性回归 `tests/test_phase2_bazidayunsource.py`。

**固定底本**：`garychowcmu/daizhigev20`，commit `4a6d6f2088825f132521d848c2ea86cf9c9a7620`，`易藏/术数/渊海子平.txt`。仓库 RAW 快照在 `data/quarantine/public_domain_snapshots/daizhigev20/yuanhai_ziping.txt`；清洗后的 Canonical 经典在 `data/canonical/classics/bazi/yuanhai_ziping_v1.json`。两份均固定 SHA-256，且四个极短引文同时逐字匹配原始 RAW 的 Unicode 字符位置和已清洗章节 ID / 标题。

已核对的四处短引与边界：

- `论大运`（section 10），「今运就月上起」：支持起点关联月令，不单独证明顺逆、首运起始时刻。
- `珞琭子消息赋`（该底本收录，section 188），「运行则一辰十载。」：支持十载说法，不等于每十年固定 `365.2425 * 10` 公历日。
- 同一 section 188，「折除乃三日为年」：支持折除说法的原文存在，不代表余数、闰日、交界秒数或取前后节的算法已经古籍审核。
- `论大运`（section 10），「此乃死法譬喻,须随格局喜忌推之,不可执一」：限制将套表吉凶机械用在用户身上。

**权限与晋级**：这是固定来源校勘 `snapshot_collated_not_classical_method_adjudicated`，而不是可执行的 Phase1/Phase2 Rule/Evidence；没有增加 Golden、改变 66 条既有已审核规则，也不在公网 API 输出原文字段。别把软件库计算结果或 #158 的现代均年时间轴称为“原典交运日期”，仍需补《三命通会》或更完整的起运顺逆版本校勘，以及余时换算、节界流派、历史时区和实历十年范围的独立审议。

校验逻辑强制验证 source repo/commit、权利策略、RAW/Canonical SHA-256、原文唯一区间、section ID/title、摘要最小范围及未批准状态。任何原文篡改、偏移漂移、换来源、改执照、将研究误设为公开/AI/Golden 晋级都直接失败；CI 在真实生产 Runtime 创建后运行相同离线核验（并保持整个既有知识库校验与前端回归）。
