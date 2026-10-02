# 网站调用约定

统一入口 `tianji_kb.engine.execute(domain, inputs, variant=None)` 只接受六个注册域及已审查 variant。CLI：

```bash
PYTHONPATH=src python scripts/chart.py liuyao --input-json '{"value":"2000-01-07T12:00:00+08:00","yao_values":[7,7,7,7,7,7]}'
PYTHONPATH=src python scripts/chart.py qimen --input-json '{"value":"2000-01-07T12:00:00+08:00"}'
PYTHONPATH=src python scripts/chart.py liuren --input-json '{"value":"2000-01-07T12:00:00+08:00"}'
PYTHONPATH=src python scripts/chart.py ziwei --input-json '{"value":"1999-02-16T00:00:00+08:00","year_boundary":"lunar-new-year"}'
PYTHONPATH=src python scripts/chart.py fengshui --input-json '{"degrees":37.5}'
PYTHONPATH=src python scripts/chart.py yijing --input-json '{"bits":"111000","changing_lines":[1]}'
```

返回 `result`、`trace`、`rule_matches`、`evidence`、`scope`、`unresolved` 与 `interpretation_contract`。RuleMatch 是已执行确定性规则的命中及月破/取传等计算条件，不表示自动吉凶断语。

每步输入、输出、variant、证据 ID、证据适用范围均保留；证据包含原文、书章/选段标识、定位、源 URL、固定 commit 与 SHA256。Phase 2 编辑选段的章/节标识在对应 `phase2_evidence.json` 可解析；不能冒充旧书完整章节实体。

AI 在这之后解释这些事实、关系与原文，禁止重算盘面、填补未实施步骤、替换 variant、把 D 软件约定说成已核原典，或把 C 说成独立 A/B。网站需按此约定绑定模型输入；仓库没有接入或部署模型服务，也没有改动网站仓库。

公用历法仅支持 1900..2099 的带时区时刻，归一到上海，子夜换日，小时天干与同一日干一致。精确节气由固定 lunar-python 1.4.8 软件提供，来源为 D。六爻/六壬可以输入显式干支，也可以由统一接口从时间确定性推导；禁止把两种输入混合。

紫微时间适配必须显式选择春节农历年界 `year_boundary=lunar-new-year`，闰月自动拒绝；直接农历接口要求调用方明确年干支约定。四化是指定 iztro 软件表 D，天空按全书空劫诀名称独立输出，不混为另一派地空或天空。

风水生产入口拒绝绝对元运年份；研究入口须同时使用 `allow_research=True`、`research=True` 和显式 `epoch_year`。结果的绝对纪元为 D，`production_eligible=false`。没有读取隔离年表或自动晋级的路径。

默认检索仍只收 Phase 1 已审 Canonical；契约、Golden 与 Phase 2 证据文件不被通用 RAG 自动展开。新增的已审短引由 EvidenceResolver 按规则返回；完整隔离正文和现代源代码不进入生产检索或计算。D 约定在结果/trace 标记，不能用所附 C 类型原句来掩盖。

奇门另外输出 `star_positions`（九星，天禽随天芮）、`door_positions`（八门）、`deity_positions`（八神），便于网站按具名对象展示。
