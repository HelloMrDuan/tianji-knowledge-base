# TJ-014.1 大运顺逆原典规则与流派矩阵

任务：TJ-014.1｜顺/逆原典规则与不同流派矩阵
验收口径：年干/传统角色分类与出生事实分开，用户明确选择口径；无隐式真实性别判断。
配套实现：`src/tianji_kb/bazi_dayun_direction.py`（`school_matrix()`、`evidence_assessment`、`validate_direction_candidate()`），测试 `tests/test_phase2_bazidayunmatrix.py`。

## 一、审核结论（先行）

1. **四象限顺逆表（阳男/阴女顺、阴男/阳女逆）目前只有 B 类证据**：其唯一来源是现代开源项目实现（jinchenma94/bazi-skill 的 dayun-rules.md，汇编为 `data/canonical/bazi/dayun_v1.json`），**没有任何古籍 Source → Section → Rule → Evidence 绑定**，Phase1 规则 0 条、Phase2 规则 0 条、Golden 0 例涉及大运方向。
2. **固定底本《渊海子平·论大运》（section 10）正文不含顺逆取法文字**。方向相关术语实际出现在同书收录的《珞琭子消息赋》（section 188）。
3. 已校勘的 4 条固定主张（`bazi.dayun.fixed-source-collation-v1`）与 1 条术语附录主张，**没有一条裁定顺逆方向**；术语附录仅证明传统角色配对术语在固定传本中存在，其 scope 明确「不独立证明大运顺逆」。
4. 因此方向候选保持 `legacy_candidate_unreviewed`、`classical_direction_evidence_approved=false`、`direction_rule_match=null`、`research_only=true / public_enabled=false / ai_enabled=false`，**不晋级 Phase2、不生成 Golden、不宣布起运岁数或交运日期**。

## 二、证据分级

- **A 类**：原典片段已在固定底本中逐字校勘（偏移、唯一出现、SHA 绑定）。
- **B 类**：现代程序还原的传统规则候选（有明确现代出处，无古籍绑定）。
- **C 类**：研究者推导或隔离材料，未完成审核。
- **D 类**：仅定位到外部转录，未影印校勘，不能裁定。

## 三、流派/来源矩阵

| 记录 | 来源 | Section | Variant | 级别 | 支持什么 | 对顺逆的支持 | 年干条件 | 角色条件 | 方向候选 | 未审前置 | 冲突 | 审核结论 | Phase2 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| collated-month-pillar-origin | bazi.source.yuanhai | 10《论大运》 | bazi-dayun-source-collation-v1 | A | 月柱为序列起点 | 无 | — | — | — | 方向措辞不在此片段 | — | 仅片段校勘，非方向规则 | 否 |
| collated-nominal-ten-year | bazi.source.yuanhai | 188《珞琭子消息赋》 | 同上 | A | 「一辰十载」文本存在 | 无 | — | — | — | 同上 | — | 同上 | 否 |
| collated-three-day-year | bazi.source.yuanhai | 188《珞琭子消息赋》 | 同上 | A | 三日折年文本存在 | 无 | — | — | — | 折算精度未裁定 | ratio-precision 未决 | 同上 | 否 |
| collated-no-universal-fortune | bazi.source.yuanhai | 10《论大运》 | 同上 | A | 限制机械吉凶套用 | 无 | — | — | — | — | — | 同上 | 否 |
| collated-role-terminology-appendix | bazi.source.yuanhai | 188《珞琭子消息赋》 | 同上（附录 bazi.dayun.traditional-role-terminology-appendix-v1） | A（仅术语） | 传统角色配对术语在固定传本中存在 | **仅术语，不证明方向** | — | 配对术语存在 | — | 由术语推方向未校勘 | — | 术语已证，方向未证 | 否 |
| modern-four-quadrant-candidate | 无古籍来源（现代实现 jinchenma94/bazi-skill） | — | bazi-dayun-modern-restoration-candidate-v1 | B | 现代实现四象限表 | 候选，未校勘 | 阳干=甲丙戊庚壬；阴干=乙丁己辛癸 | 用户明确选定 male/female | 阳男顺、阳女逆、阴男逆、阴女顺 | 古籍方向措辞未校勘；无第二独立来源；起运/交运规则未裁定 | direction-wording 未决等 5 项 | 现代还原候选，未审核 | 否 |
| external-witness-lun-qi-dayun-fa | 外部网页转录登记 | —（《论起大运法》不在固定底本） | bazi-dayun-external-witness-v1 | D | 仅登记存在 | 无 | — | — | — | 未影印比对；无独立印本见证 | direction-wording 未决 | D 级见证不能裁定 | 否 |
| sanming-tonghui-quarantine | bazi.source.sanming-xianchi-niutrans | —（无大运 canonical 节） | bazi-dayun-sanming-quarantine-v1 | C | 无 | 无 | — | — | — | 全书隔离；PUA 校勘未完 | — | 隔离材料不能裁定 | 否 |

## 四、已确认与未确认

**已确认（A 类）**：月柱起点、十年名义周期、三日折年文本、非普适吉凶限制、传统角色配对术语存在。
**未确认**：顺逆方向规则本身的古籍措辞与适用条件；年干阴阳作为取法依据的原典表述；《论起大运法》的底本真实性；起运岁数折算精度；交运日期规则。

## 五、尚未裁定的争议（保留，不多数表决）

1. `direction-wording`：方向措辞的版本差异——未决。
2. `ratio-precision`：三日折年的折算精度——未决。
3. `chronology`：纪年/交运 chronology 口径——未决。
4. 《三命通会》整书隔离，无大运节进入 Canonical，不能作为第二来源参与裁定。
5. 术语附录的角色配对术语不能独立推出方向结论。

## 六、用户口径与隐私门控

- 传统 `male`/`female` 仅为历史分类标签，由用户在研究模式下**明确选定**；不从姓名、资料性别字段、日主或生辰推断；不默认任一角色。
- 未选定角色时不计算方向；手动 `forward/backward` 模式与角色模式相互独立、互斥，不静默覆盖。
- `validate_direction_candidate()` 失败关闭：任何把候选伪造为已批准（`classical_direction_evidence_approved=true`）、伪造规则命中、升级证据级别、开启公开/AI 的结果都会被拒绝。

## 七、遗留证据缺口（阻塞晋级，非本轮可补造）

1. 对 section 188 方向措辞做逐字校勘并形成独立 direction claim（含偏移与唯一性校验）。
2. 为《论起大运法》取得可影印比对的独立印本见证，替代 D 级网页转录。
3. 《三命通会》完成 PUA 校勘并有大运节进入 Canonical 后，作为第二来源复核。
4. 起运折算精度与交运规则的独立裁定（属 TJ-014.2 以后范围，本轮不做）。
