# TJ-018.3 批三 B-2：禄刃两节 Canonical 晋级与禄刃路线注册

事件：E0339（关账预留 E0340）。基线 main `6959de27e4e813f58da6dfae91c5ee3455a684cb`（B-1 / PR #515 已合并），台账 338 事件，密封钉 `c815dc4ed02a9b7d0bd1487c3e1ed4e39d0bc826659d4ff0fb7f8a37ff685cdf`。依据：批三阳刃重新评估（E0337，`docs/product/TJ0183_P3_YANGREN_REEVALUATION.md`）结论 B 与其 §3.3 B-2 草案；B-1 卷三禄节登记（E0338，`docs/product/TJ0183_B1_SHIGANLU_REGISTRATION.md`）；P1 三刑晋级与批一/批二执行绑定先例。本批止于 PR；快照换代由父级在合并前先行执行，本批只交付暂存快照与换代清单，不动 live 快照与 cicd 钉。

## 0. 授权与范围

- 范围恰为：卷三《论十干禄》与卷五《论阳刃》两节的密封 Canonical 扩编（建节 + 引文绑定）、禄刃路线（Slice A，Variant `bazi-pattern-luren-route-v1`）的 Phase1/Phase2 注册、治理行 `pattern-route-luren` 由 pending 翻转 registered。
- 不在范围：新增任何 determination；扶抑 U1/U3；三谓词/三刑既有注册的任何改动；seq 450 的任何裁定（UD-1=A 并列保留快照字定格不变）；杂气选格（pattern-zaqi）与任氏寅月真格（ren-pattern-yin-true-v1）的注册状态；B2 组名采用 / B5 统一教义 / 三刑 concept 口径（逐字不变）。

## 1. 晋级五问答复

1. **新增哪些 Canonical 实体**：章 2（`bazi.chapter.sanming_shiganlu`、`bazi.chapter.sanming_yangren`）；节 2（`bazi.section.s063` 卷三禄节、`bazi.section.s064` 阳刃节，文本口径均为 S3 应用文本）；术语 1（`bazi.term.luren_route`，定义取任氏 s054 排除句）；Phase1 规则 1（`bazi.rule.r035`）；Phase2 步 1（`bazi.phase2.pattern_route`，validated）；密封 Golden +9 例（总数 133 → 142）。来源登记零新增（复用 P1 已登记的 `bazi.source.sanmingtonghui-applied`）。
2. **解除了哪个 pending**：治理行 `pattern-route-luren`（pending 理由 `canonical_binding_absent`）翻转 registered；治理维持名单 9 → 8 项；其解锁条件（禄表/刃表两源均完成 Canonical 绑定）由本批两节建节 + 引文绑定达成。
3. **下游条件变化**：D-1 任氏寅月真格的判定序第 2 步（禄刃路线优先序衔接）自此消费的是已注册路线步的输出（语义逐字不变，见 §4）；杂气与 D-1 自身的注册缺口（execution_binding_structure）不在本批范围、维持 pending 不变。
4. **用户可见变化**：零。路线输出除 `evidence_binding` 披露字段与其 limitations 中的注册状态句外逐盘逐字不变（§4）；determination 全部字段恒 None 不变；公开投影、场景、页面零改动。
5. **下一前置**：禄刃两节晋级线收官；治理维持 8 项（tiaohou / bingyao / pattern-zaqi / ren-pattern-yin-true-v1 / siling-yin-pilot / dayun 三项等）随各自材料齐备逐项再议，与本批无耦合。

## 2. 注册形态结论（实施前复核定稿）

实测基线形态：路线原非 trace 步——`operations/bazi_chart.chart` 在 `pattern_variant` 开启时于 pillars 步之后调用 `month_pattern_route(trace)`，结果只附于 `result['pattern_route']`，不进 `ExecutionTrace`、不产 RuleMatch/证据条目（Slice A 注释明示：未注册故不得进 RuleMatch/Evidence）。密封侧原无任何禄刃 Phase1 规则或 Phase2 步。

形态定为**批一式 trace 接入**（唯一可注册形态）：路线计算改为经 `trace.add('bazi.phase2.pattern_route', {'pattern_variant': ...}, route)` 发出，`result['pattern_route']` 取同一步的输出。理由：`scripts/validate_phase2.py` 对 `validation_status='validated'` 的步硬性要求至少一条其 `golden_case_ids` 用例在执行 trace 中真实包含该步的 rule_id；路线可真实 fire，故不得学 metal 谓词的 pending 姿态（那是构造性不可满足的专属契约，对可 fire 的路线属虚假注册）。`ExecutionTrace.add` 经 EvidenceResolver 逐条验 `source_refs`（原文须为对应 section 文本逐字子串且 source 一致），绑定即受机检。

规则 r035 的 `source_refs` 恰 4 条 = 路线实际消费引文（子集定稿沿 r031 先例）：任氏排除句（s054）、禄定义句（s063）、阳刃纲句与刃位句（s064）。禄/刃逐干 fragments 与「甲禄寅」等表行项不作 source_refs（它们是查找表数据、非规则引文，与 Slice A 密封测试的口径一致：fragments 不主张唯一出现）。

## 3. 密封著录明细

### 3.1 两节（S3 文本口径）

- `bazi.section.s063`《论十干禄》：S3 [74910, 77453)，2,543 字，PUA 0、□ 0；`review_scope` 逐字携带：B-1 校勘记登记指针（56 条）、残余防 1 位点（S3 76987 / S0 76988，unresolved——P2 分日处置 seq 47 `deferred_no_witness` 逐字不变）、A3 同类槽位读法登记说明。
- `bazi.section.s064`《论阳刃》：S3 [180873, 184327)，3,454 字，PUA 0、□ 0；`review_scope` 逐字携带：评估登记指针（校勘记 72 条 confirmed 48 / contextual 24 / unresolved 0、引文 22 条）、残余防 14 位点 S3 坐标清单（180885、182492、182678、182821、183538、183539、183677、183916、183982、184102、184158、184164、184186、184317）、**seq 450 并列记录**（节末例造引文 `yr.moli_hulu` 内，UD-1=A 并列保留快照字、无裁定，晋级不改变其状态）。

### 3.2 引文绑定

- 禄节定义句与 Slice A `sanming.lu_sentence` 为**同一引文**：公开登记侧补 `source_section_id = bazi.section.s063`（不重复立条）；密封侧该句即 s063 节文本子串，逐字同一（含己/巳快照原字）。
- 阳刃两条定义引文（纲句 S3 [180960, 180981)、刃位 S3 [181643, 181688)）公开登记侧补 `source_section_id = bazi.section.s064`；坐标已经评估与本批双重复验。
- 绑定引文与登记引文的隔离机检：r035 的 4 条绑定引文逐字无「防」；`yr.moli_hulu`（含 seq 450 位点）不入任何绑定；两节登记引文全量（禄 30 + 刃 22 = 52 条）在 S3 节文本内按登记坐标逐条在位（mapped 口径）。

### 3.3 术语与规则

- `bazi.term.luren_route`：名「禄刃路线（月逢禄刃无格可取）」，定义取 s054 排除句原文，`related_terms` = [bazi.term.official_pattern_candidate, bazi.term.resource_pattern_candidate]（路线输出实际引用的两候选术语），confidence medium，source_refs 1 条（s054 排除句）。
- `bazi.rule.r035`：operation provider `tianji_kb.operations.bazi_chart.chart`（沿 r031 形制，coverage 校验要求 provider 以 `tianji_kb.operations.` 开头）；school「子平·任氏取格路线（三命禄/刃表）」；`evidence_scope` 明示：只报路线事实（命中/未命中/杂气月标记/借路线未定），不产出格之成败、真假、清浊与用神；research/publication 开关维持 false。

## 4. 等价比对（硬验收）

<!-- EQUIVALENCE_RESULTS -->

## 5. 伪造引文负例与回滚演练

<!-- NEGATIVE_AND_ROLLBACK -->

## 6. 快照换代清单（交付父级，合并前先行）

- before：237 文件 / 15,964,218 字节 / manifest `c815dc4ed02a9b7d0bd1487c3e1ed4e39d0bc826659d4ff0fb7f8a37ff685cdf`
- after：237 文件 / 16,001,603 字节 / manifest `15bd5a268d792c86072cf9ac51effb22ca5aefa004ea7ab44e7bbf44135682d5`
- 变更恰 4 文件：
  - `data/canonical/bazi/phase1_knowledge.json`：`6501e0b6…` → `19457363a783279ebeb75674ddfde5da7f90e43bc9053936acaaedf129ab41ad`
  - `data/canonical/bazi/phase2_execution.json`：`aaf8a385…` → `8332bd98c1f007bfc5e4ba8fe55920961d23856becd2d472ffb2f2c7805be68f`
  - `data/canonical/bazi/phase2_golden.json`：`7f1620de…` → `bad517b3983eff0caf376ff93826a51b1e6bf49e9c81f919d5061444cc5a9a45`
  - `data/coverage/phase1.json`：`a9aa13a4…` → `dde15c29ac0f9552c98e581598a7fe3661379fc931a2b7420855723469e7f333`
- 暂存快照路径（机上）：`/data/workspace/b2-luren/stage-snapshot`；私有检出已同步（`scripts/import_public_snapshot.py` EXPECTED_BYTES 15964218 → 16001603、FILES 237 不变；检出根 manifest 以脚本自身 inventory()/manifest_for() 重生、verify(root) 通过）。live 快照与 cicd 钉未动。

## 7. 实施前复核结论

- ID 占用：sections 现行最大 s062 → s063/s064 空闲可用；新章 ID 未占用（现行 sanming 章仅 xianchi/sanxing/tianganshengsi/wangxiangjisheng）；rules 现行最大 r034 → r035 空闲；terms 31 → 新增 1。
- 新来源：不需要——`bazi.source.sanmingtonghui-applied` 已由 P1 登记，两节同属该来源。
- S3 切片复验：两节长度、零 PUA、零 □、残余防位点（禄 1 / 刃 14）与三条绑定引文坐标，机上以 S3 原文直读逐项复验通过，与 B-1 登记 / 批三评估实测逐一相符。
- 注册形态：见 §2（评估 §5 遗留问题就此定稿）。
- 计数对账基线：B-1 复跑 SUCCESS 2689（公开 15 + 密封 24 / 2650，skipped 1）；本批全配方复跑见 §4/§5 回填段。

## 8. 仍未判断与后续

- 路线 determination 恒 None 不变：禄刃路线只报路线事实；正格成败/真假/清浊/用神仍全部未裁定（D-1 窄字段除外，其注册维持 pending）。
- seq 450 并列维持 UD-1=A 定格；禄节 seq 47（76988）维持 deferred；两节残余防只登记不改字。
- 扶抑 U1/U3 未触及；TJ-013.1 / TJ-013.2 / 真 TJ-017.2 的阻塞与本批无关、不受影响。
- 关账 E0340 由父级在本批合并 + 正式验收 + 部署后处理。
