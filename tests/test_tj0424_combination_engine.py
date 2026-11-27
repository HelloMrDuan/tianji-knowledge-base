"""TJ-0424 原局/大运/流年组合引擎专项。

真实算例（均取自仓内已审 Golden，不另造命盘）：

- 算例 A：1958-08-15T19:30:00+08:00，男，四柱 戊戌/庚申/甲子/甲戌，
  日主甲；大运为 golden_tj0174_dayun_compose.json 的 Q1 行
  （辛酉/壬戌/癸亥，正官/偏印/正印，顺行）；流年 1988（戊辰）。
- 算例 B：1959-06-15T10:30:00+08:00，女，四柱 己亥/庚午/戊辰/丁巳，
  日主戊；大运为同 Golden 的 Q3 行（辛未/壬申/癸酉，伤官/偏财/正财，
  顺行）；流年 1970（庚戌）。

强弱/调候/病药夹具为 factors()/tiaohou_lookup()/bingyao_lookup() 在
组装环境对上述真实命盘的逐字输出（见 _fixture_json 解析后的
``_CROSS_CHECK`` 守卫：在组装环境逐项复算，漂移即失败；公开检出无
历法 provider 与密封数据时守卫跳过，不伪造通过）。
本文件只依赖标准库与 ``tianji_kb.foundations`` 之外的引擎模块本身；
引擎只 import ``foundations``，故公开检出可直接运行。

第二批（TJ-0425，P0-4）：新增 ``LiveEngineInputsTests``（机上实时
构建 assess_strength / evaluate_all / evaluate_xiyong 输出并传入
combine；公开检出无密封模块时跳过，不伪造通过）、
``ThreeLayerGroupTests``（跨三层之组，公开可跑）与
``NewInputFailClosedTests``（新形态输入漂移拒收，公开可跑）。
第三算例 C：2023-02-12T16:00:00+08:00，四柱 癸卯/甲寅/辛丑/丙申，
日主辛，D-1 正官格成立（任氏寅月真格，trace 路径 + 司令试点）；
大运为 candidate_sequence forward 前 3 运（乙卯/丙辰/丁巳）；
流年 2026（丙午）。

第三批（P0-4 效力判断扩展）：条件结论由四种扩至八种——新增病药
三角色（已触发对的主体/病/药类）与格局候选格神（只认 validated
规则、只认十神格名）；地支关系行补齐五行方向事实（本气转录表），
天干行补 same_stem、地支行补 same_branch；scope_coverage 补齐每对
已审关系命中/未命中对数。凡新增结论皆只陈述存在性事实，overall
_effect 恒 None。

2026-11-25 14:41 第二轮 33 问全部裁定：C2/C3/C4/C5/C6 已批（见引擎
LIMITATIONS）；C1 已接通（喜用路 pin 已升 v2，``_build`` 传入真实
格局 v2 输出；本地验证通过，机上实时接通待验证）。
"""
import json
from pathlib import Path
import unittest

from tianji_kb.bazi_combination_engine import (
    BRANCH_ELEMENTS,
    CONDITIONAL_VERDICTS,
    VARIANT,
    combine,
    ten_god_for,
)

# --- 真实算例夹具（逐字转录自组装环境的真实模块输出） ---------------
_FIXTURES = json.loads("""{"A":{"pillars":[{"name":"year","ganzhi":"戊戌","stem":{"value":"戊","element":"土","polarity":"阳","ten_god":"偏财"},"branch":{"value":"戌","hidden_stems":[{"stem":"戊","ten_god":"偏财"},{"stem":"辛","ten_god":"正官"},{"stem":"丁","ten_god":"伤官"}]}},{"name":"month","ganzhi":"庚申","stem":{"value":"庚","element":"金","polarity":"阳","ten_god":"七杀"},"branch":{"value":"申","hidden_stems":[{"stem":"庚","ten_god":"七杀"},{"stem":"壬","ten_god":"偏印"},{"stem":"戊","ten_god":"偏财"}]}},{"name":"day","ganzhi":"甲子","stem":{"value":"甲","element":"木","polarity":"阳","ten_god":"日主"},"branch":{"value":"子","hidden_stems":[{"stem":"癸","ten_god":"正印"}]}},{"name":"hour","ganzhi":"甲戌","stem":{"value":"甲","element":"木","polarity":"阳","ten_god":"比肩"},"branch":{"value":"戌","hidden_stems":[{"stem":"戊","ten_god":"偏财"},{"stem":"辛","ten_god":"正官"},{"stem":"丁","ten_god":"伤官"}]}}],"day_master":"甲","strength":{"factor_variant":"ditiansui-root-visibility-v1","month_command":{"month_branch":"申","hidden_stems":["庚","壬","戊"],"same_element_hidden_stems":[],"siling_by_days":null,"de_ling":null,"scope":"月支及藏干事实，不把藏干有日主同类当成司令或得令"},"root_candidates":{"day_master":"甲","element":"木","positions":[],"present_structurally":false,"effective_strength":null,"scope":"只核同五行藏干通根候选；不赋本气中气余气权重，不以冲刑自动消根"},"hidden_to_visible":{"positions":[{"hidden_pillar":"year","branch":"戌","hidden_stem":"戊","visible_pillars":["year"]},{"hidden_pillar":"month","branch":"申","hidden_stem":"庚","visible_pillars":["month"]},{"hidden_pillar":"month","branch":"申","hidden_stem":"戊","visible_pillars":["year"]},{"hidden_pillar":"hour","branch":"戌","hidden_stem":"戊","visible_pillars":["year"]}],"day_stem_excluded":true,"siling_proven":false,"scope":"支中藏干与年/月/时干同字显现，不等于取格、取用或得势"},"support_relations":{"day_master":{"stem":"甲","element":"木","polarity":"阳"},"visible_positions":[{"pillar":"year","stem":"戊","element":"土","polarity":"阳","relation":"i_control","ten_god":"偏财"},{"pillar":"month","stem":"庚","element":"金","polarity":"阳","relation":"controls_me","ten_god":"七杀"},{"pillar":"hour","stem":"甲","element":"木","polarity":"阳","relation":"same_element","ten_god":"比肩"}],"hidden_positions":[{"pillar":"year","branch":"戌","stem":"戊","element":"土","polarity":"阳","relation":"i_control","ten_god":"偏财"},{"pillar":"year","branch":"戌","stem":"辛","element":"金","polarity":"阴","relation":"controls_me","ten_god":"正官"},{"pillar":"year","branch":"戌","stem":"丁","element":"火","polarity":"阴","relation":"i_generate","ten_god":"伤官"},{"pillar":"month","branch":"申","stem":"庚","element":"金","polarity":"阳","relation":"controls_me","ten_god":"七杀"},{"pillar":"month","branch":"申","stem":"壬","element":"水","polarity":"阳","relation":"generates_me","ten_god":"偏印"},{"pillar":"month","branch":"申","stem":"戊","element":"土","polarity":"阳","relation":"i_control","ten_god":"偏财"},{"pillar":"day","branch":"子","stem":"癸","element":"水","polarity":"阴","relation":"generates_me","ten_god":"正印"},{"pillar":"hour","branch":"戌","stem":"戊","element":"土","polarity":"阳","relation":"i_control","ten_god":"偏财"},{"pillar":"hour","branch":"戌","stem":"辛","element":"金","polarity":"阴","relation":"controls_me","ten_god":"正官"},{"pillar":"hour","branch":"戌","stem":"丁","element":"火","polarity":"阴","relation":"i_generate","ten_god":"伤官"}],"day_stem_excluded_from_visible":true,"effective_support":null,"de_shi":null,"overall_strength":null,"scope":"只标明同类、生我、我生、克我、我克的位置；不计算生扶克泄耗效力或得势，不作强弱喜忌断语"},"overall_strength":null,"maturity":"PARTIAL","full_strength_classifier_ready":false,"unresolved":["司令分日有原典口径差异，未裁定。","季节旺相休囚与得令不等于整局强弱。","尚未定量或裁定得地、得势、生扶与克泄耗的实际效力。","成化、根受损、从格、旺极衰极与阴阳十二长生尚未纳入。","不能据本结果选喜用神、格局或断婚恋事业财富。"]},"tiaohou":{"variant":"tiaohou-qiongtong-v1","status":"matched","system":"tiaohou","source_id":"bazi.source.qiongtong","evidence_level":"C","day_master":"甲","month_branch":"申","month_label":"七月","entry":{"quote":"七月甲木,丁火为尊,庚金次之,庚金不可少。","quote_locator":{"line":62,"char_start":3430,"char_end":3451},"section":{"line":62,"char_start":3430,"char_end":3512},"order_basis":"原文「丁火为尊,庚金次之」明示先次,并明示「庚金不可少」。"},"sequence":[{"stem":"丁","order":1,"presence":"hidden","visible_positions":[],"hidden_positions":["year:2","hour:2"]},{"stem":"庚","order":2,"presence":"visible","visible_positions":["month"],"hidden_positions":["month:0"]}],"branches":[],"unencoded_branches":[],"related":[],"notes":[],"research_only":true,"public_enabled":false,"ai_enabled":false,"evidence_binding":"registered_phase1_phase2","limitations":["审定范围为十日主分月条目共 119 条；乙木十二月条目在审定快照中缺失，该组合返回未审定，不以其他月份条目或其他典籍补齐。","部分条目据同日主季总论或合论段审定（己土夏、秋、冬三段总论，丁火八月、九月、十二月，戊土正月、二月、十一月、十二月），逐条注明依据形态；总论与分月条目先次不一致时并列登记，不暗中合并。","来源为 C 级单一电子谱系（简体转写），未做多底本校勘；引文逐字以固定快照为准，快照缺字（如戊土正二月总论句第二位干名）不补。","只陈述条目原文的取用顺序与盘面存在性事实，不作吉凶、强弱、格局或喜用结论，不与其他喜用体系合并。","本 Variant 已在密封 Phase1 bundle 注册十条规则（bazi.rule.r042–r051）、经 Phase2 步 bazi.phase2.tiaohou_assessment 进入 RuleMatch 与 Evidence（evidence_binding=registered_phase1_phase2）；注册不改变本节其余限制，条目陈述仍不作任何裁决。"]},"bingyao":{"variant":"bingyao-shenfeng-v1","system":"bingyao","source_id":"bazi.source.shenfeng","evidence_level":"C","day_master":"甲","subject":{"god_class":"财","gods":[{"pillar":"year","stem":"戊","ten_god":"偏财"}]},"status":"triggered","disease_candidate":{"god_class":"比劫","gods":[{"pillar":"hour","stem":"甲","ten_god":"比肩"}],"relation_to_subject":"比劫为所论之财的所害之神（按原句）"},"medicine_candidate":{"god_class":"官杀","gods":[{"pillar":"month","stem":"庚","ten_god":"七杀"}],"structural_relation":"medicine_element_controls_disease_element","medicine_element":"金","disease_element":"木"},"medicine_status":"candidate_present","determination":null,"medicine_effect_status":"unadjudicated","research_only":true,"public_enabled":false,"ai_enabled":false,"evidence_binding":"registered_phase1_phase2","rule":{"pair_id":"wealth_peer_officer","id":"shenfeng.wealth_peer_officer","subject_god_class":"财","subject_gods":["正财","偏财"],"disease_god_class":"比劫","disease_gods":["比肩","劫财"],"medicine_god_class":"官杀","medicine_gods":["正官","七杀"],"quote":"如用财见比肩为病,喜见官杀为药也","quote_locator":{"line":38,"char_start":7351,"char_end":7367},"section":{"line":38,"char_start":7019,"char_end":7680}},"pairs":[{"pair_id":"wealth_peer_officer","rule":{"pair_id":"wealth_peer_officer","id":"shenfeng.wealth_peer_officer","subject_god_class":"财","subject_gods":["正财","偏财"],"disease_god_class":"比劫","disease_gods":["比肩","劫财"],"medicine_god_class":"官杀","medicine_gods":["正官","七杀"],"quote":"如用财见比肩为病,喜见官杀为药也","quote_locator":{"line":38,"char_start":7351,"char_end":7367},"section":{"line":38,"char_start":7019,"char_end":7680}},"subject":{"god_class":"财","gods":[{"pillar":"year","stem":"戊","ten_god":"偏财"}]},"determination":null,"medicine_effect_status":"unadjudicated","status":"triggered","disease_candidate":{"god_class":"比劫","gods":[{"pillar":"hour","stem":"甲","ten_god":"比肩"}],"relation_to_subject":"比劫为所论之财的所害之神（按原句）"},"medicine_candidate":{"god_class":"官杀","gods":[{"pillar":"month","stem":"庚","ten_god":"七杀"}],"structural_relation":"medicine_element_controls_disease_element","medicine_element":"金","disease_element":"木"},"medicine_status":"candidate_present"},{"pair_id":"foodwound_seal_wealth","rule":{"pair_id":"foodwound_seal_wealth","id":"shenfeng.foodwound_seal_wealth","subject_god_class":"食伤","subject_gods":["食神","伤官"],"disease_god_class":"印","disease_gods":["正印","偏印"],"medicine_god_class":"财","medicine_gods":["正财","偏财"],"quote":"如用食神伤官,以印为病,喜财为药也","quote_locator":{"line":38,"char_start":7368,"char_end":7385},"section":{"line":38,"char_start":7019,"char_end":7680}},"subject":{"god_class":"食伤","gods":[]},"determination":null,"medicine_effect_status":"unadjudicated","status":"not_triggered","disease_candidate":null,"medicine_candidate":null,"medicine_status":null,"not_triggered_reason":"subject_foodwound_not_visible"}],"adjudication_notes":["S1 用财=所论之神（非格局用神）：同句下句「如用食神伤官」平行，定义节通篇不论格局，开篇以「原所害之神」立病。备选读法（用神义）若成立，本切片被格局裁定缺位阻塞，降级路径为仅登记 Source 与定义节审定存档。","S2 比肩取比劫类（比肩、劫财）：本书土重例以「比肩太重」指同行类聚；夺财之害以比劫并称。Golden 劫财单见例钉住此类界。","S3 只计显干：原句用「见」；藏干不计。Golden 双边界例（比劫仅藏干、财仅藏干）钉住此口径。","S4 财显一字即触发候选；「从重者论」的未尽事项写入 LIMITATIONS，不另设门槛。","冲突例处置：药被食伤所克的构形需第四个非日主显干位，真实命盘中不可出现（年、月、时三位已被财、比劫、官杀占满）；效力守卫由 medicine_effect_status 恒未裁定承担，不设不可达成的子状态，不以合成盘面充数。","S1 延伸（第二对）：「用食神伤官」的「用」与首对「用财」同构——两句在定义节中相邻并列（字符 7351–7385），句式全同（用 X、见/以 Y 为病、喜 Z 为药），同读作所论之神；若改作用神义，两对同被格局裁定缺位阻塞，降级路径与首对相同。","S2 类读延伸（第二对）：食伤取食神、伤官两神（原句并列明言「食神伤官」，非类推）；印取正印、偏印（原句单言「印」，按十神类读，与首对「比肩」取比劫类同例）；财取正财、偏财（与首对主体财同一类读）。各类成员在规则表逐项写明，Golden 以伤官、偏印、偏财同盘例钉住各类的第二成员。","S4 延伸（第二对）：食伤显一字即触发第二对候选（与首对财显一字同口径）；「从重者论」的未尽事项同样适用，不另设门槛。","双对独立：两对主体不同（财为日主所克，食伤为日主所生），同盘逐对独立评估、逐对陈述（pairs），不合并为单一病药结论；一对的部分事实（如食伤已显而印未显）不借给另一对，顶层字段保持第一对语义不变。","双对同触发不可实现：两对触发共需财、比劫、食伤、印四个互异十神类各至少一显干，非日主显干只有年、月、时三位，鸽笼原理下真实命盘不可出现；已登记 Golden unrealizable_designs 并附算术证明，不以合成盘面充数，公开全域扫描断言至多一对 triggered。"],"scope_limits":["本 Variant 编码《神峰通考》病药说类定义节示例二、示例三两对（财—比劫—官杀；食伤—印—财）；示例一（土重）的前提无操作定义，四病四药或缺阈值判据或是行运之药，均不在本 Variant 范围。","存在性口径只计显干（年、月、时三干），不计藏干（审定点 S3）；两对的主体与病、药均按此口径，藏干中出现的财、比劫、官杀、食伤、印不触发、不补位。","本 Variant 未按定义节「从重者论」选定唯一病神：「重」在书中无阈值，切片只陈述示例对的存在性命中（审定点 S4）。","药候选只陈述存在与「药之五行克病之五行」的结构关系，去病效力恒未裁定；药存在不等于病已去，本 Variant 不输出「药已去病」。","本 Variant 永不输出「无病」：无病（平常）的成立要求整盘不旺不弱且中和的裁定（定义节否定侧条款），本平台无此能力；未命中只记未触发。","正官格节「惟官星太弱太旺，方为有病」口径（字符 10010）与定义节口径并存未统一，本 Variant 不覆盖太弱太旺型之病，不得引该句把候选升级为用神结论。","《滴天髓阐微》中和篇任氏注明言病药之论「仍乃失之偏」「总以中和为主」（字符 43767），病药说非通则，本 Variant 的候选陈述须与此制衡同读。","审定点 S1：「用财」按所论之神读法审定（依据同节平行句与总定义语境）；若改作用神义，本 Variant 应被格局裁定缺位阻塞并降级，不得静默沿用。","来源为 C 级单一电子谱系（简体转写），未做全书逐字校勘，已见个别讹字与一处重文，未订正；同书末篇「病源赋」为身体疾病占验文字，属排除范围，本 Variant 不引用。","与调候 Variant 并列而非合并：病药候选不得与调候、扶抑、格局用神的输出合并为统一「喜用神」结论。","注册状态（E0348）：本 Variant 已注册 Phase1 规则 bazi.rule.r040 与 Phase2 步 bazi.phase2.bingyao_assessment（Canonical《神峰通考》s071/s072、滴天髓 s074），经 bazi_chart 研究门控进入 RuleMatch 与 Evidence；注册不改变本条以上任何语义边界，determination 恒未裁定。"]}},"B":{"pillars":[{"name":"year","ganzhi":"己亥","stem":{"value":"己","element":"土","polarity":"阴","ten_god":"劫财"},"branch":{"value":"亥","hidden_stems":[{"stem":"壬","ten_god":"偏财"},{"stem":"甲","ten_god":"七杀"}]}},{"name":"month","ganzhi":"庚午","stem":{"value":"庚","element":"金","polarity":"阳","ten_god":"食神"},"branch":{"value":"午","hidden_stems":[{"stem":"丁","ten_god":"正印"},{"stem":"己","ten_god":"劫财"}]}},{"name":"day","ganzhi":"戊辰","stem":{"value":"戊","element":"土","polarity":"阳","ten_god":"日主"},"branch":{"value":"辰","hidden_stems":[{"stem":"戊","ten_god":"比肩"},{"stem":"乙","ten_god":"正官"},{"stem":"癸","ten_god":"正财"}]}},{"name":"hour","ganzhi":"丁巳","stem":{"value":"丁","element":"火","polarity":"阴","ten_god":"正印"},"branch":{"value":"巳","hidden_stems":[{"stem":"丙","ten_god":"偏印"},{"stem":"庚","ten_god":"食神"},{"stem":"戊","ten_god":"比肩"}]}}],"day_master":"戊","strength":{"factor_variant":"ditiansui-root-visibility-v1","month_command":{"month_branch":"午","hidden_stems":["丁","己"],"same_element_hidden_stems":["己"],"siling_by_days":null,"de_ling":null,"scope":"月支及藏干事实，不把藏干有日主同类当成司令或得令"},"root_candidates":{"day_master":"戊","element":"土","positions":[{"pillar":"month","branch":"午","hidden_stem":"己","same_stem":false},{"pillar":"day","branch":"辰","hidden_stem":"戊","same_stem":true},{"pillar":"hour","branch":"巳","hidden_stem":"戊","same_stem":true}],"present_structurally":true,"effective_strength":null,"scope":"只核同五行藏干通根候选；不赋本气中气余气权重，不以冲刑自动消根"},"hidden_to_visible":{"positions":[{"hidden_pillar":"month","branch":"午","hidden_stem":"丁","visible_pillars":["hour"]},{"hidden_pillar":"month","branch":"午","hidden_stem":"己","visible_pillars":["year"]},{"hidden_pillar":"hour","branch":"巳","hidden_stem":"庚","visible_pillars":["month"]}],"day_stem_excluded":true,"siling_proven":false,"scope":"支中藏干与年/月/时干同字显现，不等于取格、取用或得势"},"support_relations":{"day_master":{"stem":"戊","element":"土","polarity":"阳"},"visible_positions":[{"pillar":"year","stem":"己","element":"土","polarity":"阴","relation":"same_element","ten_god":"劫财"},{"pillar":"month","stem":"庚","element":"金","polarity":"阳","relation":"i_generate","ten_god":"食神"},{"pillar":"hour","stem":"丁","element":"火","polarity":"阴","relation":"generates_me","ten_god":"正印"}],"hidden_positions":[{"pillar":"year","branch":"亥","stem":"壬","element":"水","polarity":"阳","relation":"i_control","ten_god":"偏财"},{"pillar":"year","branch":"亥","stem":"甲","element":"木","polarity":"阳","relation":"controls_me","ten_god":"七杀"},{"pillar":"month","branch":"午","stem":"丁","element":"火","polarity":"阴","relation":"generates_me","ten_god":"正印"},{"pillar":"month","branch":"午","stem":"己","element":"土","polarity":"阴","relation":"same_element","ten_god":"劫财"},{"pillar":"day","branch":"辰","stem":"戊","element":"土","polarity":"阳","relation":"same_element","ten_god":"比肩"},{"pillar":"day","branch":"辰","stem":"乙","element":"木","polarity":"阴","relation":"controls_me","ten_god":"正官"},{"pillar":"day","branch":"辰","stem":"癸","element":"水","polarity":"阴","relation":"i_control","ten_god":"正财"},{"pillar":"hour","branch":"巳","stem":"丙","element":"火","polarity":"阳","relation":"generates_me","ten_god":"偏印"},{"pillar":"hour","branch":"巳","stem":"庚","element":"金","polarity":"阳","relation":"i_generate","ten_god":"食神"},{"pillar":"hour","branch":"巳","stem":"戊","element":"土","polarity":"阳","relation":"same_element","ten_god":"比肩"}],"day_stem_excluded_from_visible":true,"effective_support":null,"de_shi":null,"overall_strength":null,"scope":"只标明同类、生我、我生、克我、我克的位置；不计算生扶克泄耗效力或得势，不作强弱喜忌断语"},"overall_strength":null,"maturity":"PARTIAL","full_strength_classifier_ready":false,"unresolved":["司令分日有原典口径差异，未裁定。","季节旺相休囚与得令不等于整局强弱。","尚未定量或裁定得地、得势、生扶与克泄耗的实际效力。","成化、根受损、从格、旺极衰极与阴阳十二长生尚未纳入。","不能据本结果选喜用神、格局或断婚恋事业财富。"]},"tiaohou":{"variant":"tiaohou-qiongtong-v1","status":"matched","system":"tiaohou","source_id":"bazi.source.qiongtong","evidence_level":"C","day_master":"戊","month_branch":"午","month_label":"五月","entry":{"quote":"五月戊土,仲夏火炎,先看壬水,次取甲木,丙火酌用,用癸力微。","quote_locator":{"line":578,"char_start":16213,"char_end":16243},"section":{"line":578,"char_start":16213,"char_end":16405},"order_basis":"原文「先看壬水，次取甲木」明示先次；「丙火酌用」「用癸力微」为酌量与力微陈述，未列先次，不入序列。"},"sequence":[{"stem":"壬","order":1,"presence":"hidden","visible_positions":[],"hidden_positions":["year:0"]},{"stem":"甲","order":2,"presence":"hidden","visible_positions":[],"hidden_positions":["year:1"]}],"branches":[],"unencoded_branches":[],"related":[],"notes":[],"research_only":true,"public_enabled":false,"ai_enabled":false,"evidence_binding":"registered_phase1_phase2","limitations":["审定范围为十日主分月条目共 119 条；乙木十二月条目在审定快照中缺失，该组合返回未审定，不以其他月份条目或其他典籍补齐。","部分条目据同日主季总论或合论段审定（己土夏、秋、冬三段总论，丁火八月、九月、十二月，戊土正月、二月、十一月、十二月），逐条注明依据形态；总论与分月条目先次不一致时并列登记，不暗中合并。","来源为 C 级单一电子谱系（简体转写），未做多底本校勘；引文逐字以固定快照为准，快照缺字（如戊土正二月总论句第二位干名）不补。","只陈述条目原文的取用顺序与盘面存在性事实，不作吉凶、强弱、格局或喜用结论，不与其他喜用体系合并。","本 Variant 已在密封 Phase1 bundle 注册十条规则（bazi.rule.r042–r051）、经 Phase2 步 bazi.phase2.tiaohou_assessment 进入 RuleMatch 与 Evidence（evidence_binding=registered_phase1_phase2）；注册不改变本节其余限制，条目陈述仍不作任何裁决。"]},"bingyao":{"variant":"bingyao-shenfeng-v1","system":"bingyao","source_id":"bazi.source.shenfeng","evidence_level":"C","day_master":"戊","subject":{"god_class":"财","gods":[]},"status":"not_triggered","disease_candidate":null,"medicine_candidate":null,"medicine_status":null,"determination":null,"medicine_effect_status":"unadjudicated","research_only":true,"public_enabled":false,"ai_enabled":false,"evidence_binding":"registered_phase1_phase2","rule":{"pair_id":"wealth_peer_officer","id":"shenfeng.wealth_peer_officer","subject_god_class":"财","subject_gods":["正财","偏财"],"disease_god_class":"比劫","disease_gods":["比肩","劫财"],"medicine_god_class":"官杀","medicine_gods":["正官","七杀"],"quote":"如用财见比肩为病,喜见官杀为药也","quote_locator":{"line":38,"char_start":7351,"char_end":7367},"section":{"line":38,"char_start":7019,"char_end":7680}},"pairs":[{"pair_id":"wealth_peer_officer","rule":{"pair_id":"wealth_peer_officer","id":"shenfeng.wealth_peer_officer","subject_god_class":"财","subject_gods":["正财","偏财"],"disease_god_class":"比劫","disease_gods":["比肩","劫财"],"medicine_god_class":"官杀","medicine_gods":["正官","七杀"],"quote":"如用财见比肩为病,喜见官杀为药也","quote_locator":{"line":38,"char_start":7351,"char_end":7367},"section":{"line":38,"char_start":7019,"char_end":7680}},"subject":{"god_class":"财","gods":[]},"determination":null,"medicine_effect_status":"unadjudicated","status":"not_triggered","disease_candidate":null,"medicine_candidate":null,"medicine_status":null,"not_triggered_reason":"subject_wealth_not_visible"},{"pair_id":"foodwound_seal_wealth","rule":{"pair_id":"foodwound_seal_wealth","id":"shenfeng.foodwound_seal_wealth","subject_god_class":"食伤","subject_gods":["食神","伤官"],"disease_god_class":"印","disease_gods":["正印","偏印"],"medicine_god_class":"财","medicine_gods":["正财","偏财"],"quote":"如用食神伤官,以印为病,喜财为药也","quote_locator":{"line":38,"char_start":7368,"char_end":7385},"section":{"line":38,"char_start":7019,"char_end":7680}},"subject":{"god_class":"食伤","gods":[{"pillar":"month","stem":"庚","ten_god":"食神"}]},"determination":null,"medicine_effect_status":"unadjudicated","status":"triggered","disease_candidate":{"god_class":"印","gods":[{"pillar":"hour","stem":"丁","ten_god":"正印"}],"relation_to_subject":"印为所论之食伤的所害之神（按原句）"},"medicine_candidate":null,"medicine_status":"absent"}],"adjudication_notes":["S1 用财=所论之神（非格局用神）：同句下句「如用食神伤官」平行，定义节通篇不论格局，开篇以「原所害之神」立病。备选读法（用神义）若成立，本切片被格局裁定缺位阻塞，降级路径为仅登记 Source 与定义节审定存档。","S2 比肩取比劫类（比肩、劫财）：本书土重例以「比肩太重」指同行类聚；夺财之害以比劫并称。Golden 劫财单见例钉住此类界。","S3 只计显干：原句用「见」；藏干不计。Golden 双边界例（比劫仅藏干、财仅藏干）钉住此口径。","S4 财显一字即触发候选；「从重者论」的未尽事项写入 LIMITATIONS，不另设门槛。","冲突例处置：药被食伤所克的构形需第四个非日主显干位，真实命盘中不可出现（年、月、时三位已被财、比劫、官杀占满）；效力守卫由 medicine_effect_status 恒未裁定承担，不设不可达成的子状态，不以合成盘面充数。","S1 延伸（第二对）：「用食神伤官」的「用」与首对「用财」同构——两句在定义节中相邻并列（字符 7351–7385），句式全同（用 X、见/以 Y 为病、喜 Z 为药），同读作所论之神；若改作用神义，两对同被格局裁定缺位阻塞，降级路径与首对相同。","S2 类读延伸（第二对）：食伤取食神、伤官两神（原句并列明言「食神伤官」，非类推）；印取正印、偏印（原句单言「印」，按十神类读，与首对「比肩」取比劫类同例）；财取正财、偏财（与首对主体财同一类读）。各类成员在规则表逐项写明，Golden 以伤官、偏印、偏财同盘例钉住各类的第二成员。","S4 延伸（第二对）：食伤显一字即触发第二对候选（与首对财显一字同口径）；「从重者论」的未尽事项同样适用，不另设门槛。","双对独立：两对主体不同（财为日主所克，食伤为日主所生），同盘逐对独立评估、逐对陈述（pairs），不合并为单一病药结论；一对的部分事实（如食伤已显而印未显）不借给另一对，顶层字段保持第一对语义不变。","双对同触发不可实现：两对触发共需财、比劫、食伤、印四个互异十神类各至少一显干，非日主显干只有年、月、时三位，鸽笼原理下真实命盘不可出现；已登记 Golden unrealizable_designs 并附算术证明，不以合成盘面充数，公开全域扫描断言至多一对 triggered。"],"scope_limits":["本 Variant 编码《神峰通考》病药说类定义节示例二、示例三两对（财—比劫—官杀；食伤—印—财）；示例一（土重）的前提无操作定义，四病四药或缺阈值判据或是行运之药，均不在本 Variant 范围。","存在性口径只计显干（年、月、时三干），不计藏干（审定点 S3）；两对的主体与病、药均按此口径，藏干中出现的财、比劫、官杀、食伤、印不触发、不补位。","本 Variant 未按定义节「从重者论」选定唯一病神：「重」在书中无阈值，切片只陈述示例对的存在性命中（审定点 S4）。","药候选只陈述存在与「药之五行克病之五行」的结构关系，去病效力恒未裁定；药存在不等于病已去，本 Variant 不输出「药已去病」。","本 Variant 永不输出「无病」：无病（平常）的成立要求整盘不旺不弱且中和的裁定（定义节否定侧条款），本平台无此能力；未命中只记未触发。","正官格节「惟官星太弱太旺，方为有病」口径（字符 10010）与定义节口径并存未统一，本 Variant 不覆盖太弱太旺型之病，不得引该句把候选升级为用神结论。","《滴天髓阐微》中和篇任氏注明言病药之论「仍乃失之偏」「总以中和为主」（字符 43767），病药说非通则，本 Variant 的候选陈述须与此制衡同读。","审定点 S1：「用财」按所论之神读法审定（依据同节平行句与总定义语境）；若改作用神义，本 Variant 应被格局裁定缺位阻塞并降级，不得静默沿用。","来源为 C 级单一电子谱系（简体转写），未做全书逐字校勘，已见个别讹字与一处重文，未订正；同书末篇「病源赋」为身体疾病占验文字，属排除范围，本 Variant 不引用。","与调候 Variant 并列而非合并：病药候选不得与调候、扶抑、格局用神的输出合并为统一「喜用神」结论。","注册状态（E0348）：本 Variant 已注册 Phase1 规则 bazi.rule.r040 与 Phase2 步 bazi.phase2.bingyao_assessment（Canonical《神峰通考》s071/s072、滴天髓 s074），经 bazi_chart 研究门控进入 RuleMatch 与 Evidence；注册不改变本条以上任何语义边界，determination 恒未裁定。"],"not_triggered_reason":"subject_wealth_not_visible"}}}""")

CASE_A_PILLARS = _FIXTURES["A"]["pillars"]
CASE_A_DAYUN = [
    {"candidate_ganzhi": "辛酉", "period_index": 1, "ten_god": "正官"},
    {"candidate_ganzhi": "壬戌", "period_index": 2, "ten_god": "偏印"},
    {"candidate_ganzhi": "癸亥", "period_index": 3, "ten_god": "正印"},
]
CASE_B_PILLARS = _FIXTURES["B"]["pillars"]
CASE_B_DAYUN = [
    {"candidate_ganzhi": "辛未", "period_index": 1, "ten_god": "伤官"},
    {"candidate_ganzhi": "壬申", "period_index": 2, "ten_god": "偏财"},
    {"candidate_ganzhi": "癸酉", "period_index": 3, "ten_god": "正财"},
]


def _combine_a(**overrides):
    kwargs = {
        "strength": _FIXTURES["A"]["strength"],
        "tiaohou": _FIXTURES["A"]["tiaohou"],
        "bingyao": _FIXTURES["A"]["bingyao"],
    }
    kwargs.update(overrides)
    return combine(CASE_A_PILLARS, "甲", CASE_A_DAYUN, 1988, **kwargs)


def _combine_b(**overrides):
    kwargs = {
        "strength": _FIXTURES["B"]["strength"],
        "tiaohou": _FIXTURES["B"]["tiaohou"],
        "bingyao": _FIXTURES["B"]["bingyao"],
    }
    kwargs.update(overrides)
    return combine(CASE_B_PILLARS, "戊", CASE_B_DAYUN, 1970, **kwargs)


def _relations(output, scope=None, kind=None, period_index=None):
    rows = output["structural_relations"]
    if scope is not None:
        rows = [r for r in rows if r["scope"] == scope]
    if kind is not None:
        rows = [r for r in rows if r["kind"] == kind]
    if period_index is not None:
        rows = [r for r in rows if r["period_index"] == period_index]
    return rows


def _has_pair(rows, first, second):
    """是否存在一对干支关系，其两端干支集合恰为 {first, second}。"""
    for row in rows:
        detail = row["detail"]
        members = detail.get("stems") or detail.get("branches") or []
        if set(members) == {first, second}:
            return True
    return False


class RealCaseATests(unittest.TestCase):
    def test_flow_year_and_flags(self):
        output = _combine_a()
        self.assertEqual(output["variant"], VARIANT)
        self.assertTrue(output["research_only"])
        self.assertFalse(output["public_enabled"])
        self.assertFalse(output["ai_enabled"])
        flow = output["flow_year"]
        self.assertEqual(flow["ganzhi"], "戊辰")
        self.assertEqual(flow["stem_ten_god"], "偏财")
        self.assertEqual(output["natal"]["month_branch"], "申")
        self.assertEqual(output["dayun"]["period_year_mapping"],
                         "not_determined")

    def test_relation_totals_case_a(self):
        output = _combine_a()
        summary = output["relation_summary"]
        # 手算：大运×原局 17（干 13＋支 3＋组 1），流年×原局 7
        # （干 4＋支 2＋组 1），大运×流年 6（干 4＋支 2），合计 30。
        self.assertEqual(summary["total"], 30)
        self.assertEqual(summary["counts_by_scope"], {
            "dayun_x_natal": 17, "flow_x_natal": 7, "dayun_x_flow": 6})
        self.assertEqual(summary["counts_by_kind"], {
            "stem_five_element": 19,
            "stem_five_combination": 2,
            "branch_harm": 3,
            "branch_clash": 3,
            "branch_six_harmony": 1,
            "branch_triple_harmony": 1,
            "branch_directional_meeting": 1,
        })

    def test_named_relations_case_a(self):
        output = _combine_a()
        # 癸（大运三）与戊（原局年干）五合：大运×原局与大运×流年各一。
        self.assertTrue(_has_pair(
            _relations(output, "dayun_x_natal", "stem_five_combination", 3),
            "癸", "戊"))
        self.assertTrue(_has_pair(
            _relations(output, "dayun_x_flow", "stem_five_combination", 3),
            "癸", "戊"))
        self.assertEqual(_relations(
            output, "dayun_x_flow", "stem_five_combination", 3)[0]["detail"]
            ["traditional_result_element"], "火")
        # 大运亥害原局申；流年辰冲原局两戌；大运酉合流年辰。
        self.assertTrue(_has_pair(
            _relations(output, "dayun_x_natal", "branch_harm", 3),
            "亥", "申"))
        self.assertEqual(len(_relations(
            output, "flow_x_natal", "branch_clash")), 2)
        self.assertTrue(_has_pair(
            _relations(output, "dayun_x_flow", "branch_six_harmony", 1),
            "酉", "辰"))
        self.assertEqual(_relations(
            output, "dayun_x_flow", "branch_six_harmony", 1)[0]["detail"]
            ["traditional_result_element"], "金")
        self.assertTrue(_has_pair(
            _relations(output, "dayun_x_flow", "branch_clash", 2),
            "戌", "辰"))
        # 三合水（申子辰：原局申/子＋流年辰）与方位会金（申酉戌）。
        triple = _relations(output, "flow_x_natal", "branch_triple_harmony")
        self.assertEqual(len(triple), 1)
        self.assertEqual(triple[0]["detail"]["branches"], ["申", "子", "辰"])
        self.assertEqual(triple[0]["detail"]["traditional_result_element"], "水")
        meeting = _relations(output, "dayun_x_natal",
                             "branch_directional_meeting", 1)
        self.assertEqual(len(meeting), 1)
        self.assertEqual(meeting[0]["detail"]["branches"], ["申", "酉", "戌"])

    def test_conditions_and_effects_case_a(self):
        output = _combine_a()
        for relation in output["structural_relations"]:
            with self.subTest(relation=relation["id"]):
                statuses = {c["status"] for c in relation["conditions"]}
                self.assertIn("satisfied", statuses)
                self.assertIn("cannot_judge", statuses)
                self.assertTrue(all(c["rule_ids"]
                                    for c in relation["conditions"]))
                if relation["effect"]["status"] == "conditional":
                    self.assertIn(relation["effect"]["verdict"],
                                  CONDITIONAL_VERDICTS)
                    self.assertTrue(relation["effect"]["basis"]
                                    ["not_an_efficacy_verdict"])
                    self.assertTrue(
                        relation["effect"]["conditional_conclusions"])
                else:
                    self.assertEqual(relation["effect"]["status"], "abstain")
                    self.assertIsNone(relation["effect"]["verdict"])
        effects = output["effects"]
        self.assertIsNone(effects["overall_effect"])
        self.assertFalse(effects["all_abstained"])
        # 第三批：病药角色结论——大运辛（正官，药神类）5 条、流年戊
        # （偏财，所论之神类）8 条，R025 两侧各中一类故只计一次；
        # 其余 18 条（地支关系与组关系）仍 abstain。
        self.assertEqual(effects["abstain_count"], 18)
        self.assertEqual(effects["conditional_count"], 12)
        self.assertEqual(effects["verdict_counts"],
                         {"abstain": 18, "conditional": 12})
        self.assertEqual(
            {c["relation_id"] for c in effects["conditional_effects"]},
            {"R001", "R003", "R004", "R005", "R018", "R020", "R021",
             "R022", "R025", "R027", "R029", "R030"})
        mentions = {}
        for entry in effects["conditional_effects"]:
            for verdict in entry["verdicts"]:
                mentions[verdict] = mentions.get(verdict, 0) + 1
        self.assertEqual(mentions, {
            "stem_matches_bingyao_medicine_god": 5,
            "stem_matches_bingyao_subject_god": 8})
        # 大运×流年未指定当期运，期位前提一律无法判定。
        for relation in _relations(output, "dayun_x_flow"):
            mapping = [c for c in relation["conditions"]
                       if c["id"] == "period_year_mapping"]
            self.assertEqual(len(mapping), 1)
            self.assertEqual(mapping[0]["status"], "cannot_judge")
        # 刑不在已审表中：无刑关系，只登记未评估。
        self.assertFalse([r for r in output["structural_relations"]
                          if "punishment" in r["kind"]])
        self.assertEqual(
            output["relation_summary"]["not_evaluated"][0]["kind"],
            "branch_punishment")
        # 第三批结构补齐：地支行带本气五行方向事实，天干行标同干。
        clash = _relations(output, "flow_x_natal", "branch_clash")[0]
        self.assertEqual(clash["detail"]["branches"], ["辰", "戌"])
        self.assertEqual(clash["detail"]["elements"], ["土", "土"])
        self.assertEqual(clash["detail"]["direction_from_a_to_b"], "same")
        self.assertFalse(clash["detail"]["same_branch"])
        same_stem = [r for r in output["structural_relations"]
                     if r["kind"] == "stem_five_element"
                     and r["detail"]["same_stem"]]
        self.assertEqual(len(same_stem), 1)
        self.assertEqual(same_stem[0]["detail"]["stems"], ["戊", "戊"])

    def test_xiyong_contract_case_a(self):
        output = _combine_a()
        xiyong = output["xiyong"]
        self.assertIsNone(xiyong["unified_verdict"])
        self.assertEqual(xiyong["unified_verdict_status"],
                         "abstain_by_adjudication_TJ-013.2-A")
        fuyi = xiyong["systems"]["fuyi"]
        self.assertEqual(fuyi["status"], "not_buildable")
        self.assertEqual(fuyi["buildable_count"], 0)
        self.assertIsNone(fuyi["direction"])
        self.assertIsNone(fuyi["useful_god"])
        self.assertFalse(fuyi["consumed_strength_factors"]
                         ["root_candidates"]["present_structurally"])
        self.assertIsNone(fuyi["consumed_strength_factors"]
                          ["overall_strength"])
        tiaohou = xiyong["systems"]["tiaohou"]
        self.assertEqual(tiaohou["status"], "presented")
        self.assertEqual(tiaohou["sequence_stems"], ["丁", "庚"])
        self.assertIsNone(tiaohou["determination"])
        bingyao = xiyong["systems"]["bingyao"]
        self.assertEqual(bingyao["status"], "presented")
        self.assertEqual(bingyao["pairs"], [
            {"pair_id": "wealth_peer_officer", "status": "triggered",
             "medicine_status": "candidate_present",
             "medicine_effect_status": "unadjudicated"},
            {"pair_id": "foodwound_seal_wealth", "status": "not_triggered",
             "medicine_status": None,
             "medicine_effect_status": "unadjudicated"},
        ])
        self.assertIsNone(bingyao["determination"])
        pattern = xiyong["systems"]["pattern_yongshen"]
        self.assertEqual(pattern["status"], "not_provided")
        self.assertIsNone(pattern["useful_god"])
        annual = xiyong["annual_xiyong"]
        self.assertEqual(annual["status"], "contract_only_pending_rules")
        self.assertIsNone(annual["derivation"])
        self.assertIsNone(annual["unified_verdict"])
        self.assertIn("annual_tiaohou_derivation", annual["pending"])
        self.assertIn("flow_year_ganzhi_and_ten_god",
                      annual["implemented"])
        # 流年干戊不在原局调候序列（丁/庚）中；其十神偏财为病药第一对主体。
        self.assertFalse(annual["flow_references"]["tiaohou"]
                         ["flow_stem_in_natal_tiaohou_sequence"])
        pair_refs = annual["flow_references"]["bingyao"]["pairs"]
        self.assertEqual(pair_refs[0]["flow_ten_god_role_in_pair"], "subject")
        self.assertEqual(pair_refs[1]["flow_ten_god_role_in_pair"], "medicine")

    def test_consumed_rule_ids_case_a(self):
        output = _combine_a()
        for rule_id in (
                "bazi.phase2.pillars", "bazi.phase2.ten_gods",
                "bazi.phase2.stem_five_combinations",
                "bazi.phase2.branch_six_harmonies",
                "bazi.phase2.branch_six_harms",
                "bazi.phase2.branch_six_clashes",
                "bazi.phase2.branch_triple_harmonies",
                "bazi-dayun-month-sequence-research-v1",
                "bazi.phase2.tiaohou_assessment",
                "bazi.phase2.bingyao_assessment",
                "ditiansui-root-visibility-v1"):
            self.assertIn(rule_id, output["consumed_rule_ids"])


class RealCaseBTests(unittest.TestCase):
    def test_relation_totals_case_b(self):
        output = _combine_b()
        summary = output["relation_summary"]
        # 手算：大运×原局 19（干 14＋支 4＋组 1），流年×原局 5
        # （干 4＋支 1＋组 0），大运×流年 4（干 3＋支 1），合计 28。
        self.assertEqual(summary["total"], 28)
        self.assertEqual(summary["counts_by_scope"], {
            "dayun_x_natal": 19, "flow_x_natal": 5, "dayun_x_flow": 4})
        self.assertEqual(summary["counts_by_kind"], {
            "stem_five_element": 19,
            "stem_five_combination": 2,
            "branch_six_harmony": 3,
            "branch_harm": 2,
            "branch_clash": 1,
            "branch_directional_meeting": 1,
        })
        self.assertEqual(output["flow_year"]["ganzhi"], "庚戌")
        self.assertEqual(output["flow_year"]["stem_ten_god"], "食神")

    def test_named_relations_case_b(self):
        output = _combine_b()
        # 丁壬合木（大运二壬×原局时丁）与戊癸合火（大运三癸×原局日戊）。
        self.assertTrue(_has_pair(
            _relations(output, "dayun_x_natal", "stem_five_combination", 2),
            "丁", "壬"))
        self.assertEqual(_relations(
            output, "dayun_x_natal", "stem_five_combination", 2)[0]["detail"]
            ["traditional_result_element"], "木")
        self.assertTrue(_has_pair(
            _relations(output, "dayun_x_natal", "stem_five_combination", 3),
            "戊", "癸"))
        # 午未合（大运一未×原局月午）、巳申合、辰酉合、申亥害、酉戌害、辰戌冲。
        self.assertTrue(_has_pair(
            _relations(output, "dayun_x_natal", "branch_six_harmony", 1),
            "午", "未"))
        self.assertEqual(_relations(
            output, "dayun_x_natal", "branch_six_harmony", 1)[0]["detail"]
            ["traditional_result_element"], "火/土(有争议)")
        self.assertTrue(_has_pair(
            _relations(output, "dayun_x_natal", "branch_six_harmony", 2),
            "巳", "申"))
        self.assertTrue(_has_pair(
            _relations(output, "dayun_x_natal", "branch_six_harmony", 3),
            "辰", "酉"))
        self.assertTrue(_has_pair(
            _relations(output, "dayun_x_natal", "branch_harm", 2),
            "申", "亥"))
        self.assertTrue(_has_pair(
            _relations(output, "dayun_x_flow", "branch_harm", 3),
            "酉", "戌"))
        self.assertTrue(_has_pair(
            _relations(output, "flow_x_natal", "branch_clash"),
            "辰", "戌"))
        # 方位会火（巳午未：原局巳/午＋大运一未）；本例无三合。
        meeting = _relations(output, "dayun_x_natal",
                             "branch_directional_meeting", 1)
        self.assertEqual(len(meeting), 1)
        self.assertEqual(meeting[0]["detail"]["branches"], ["巳", "午", "未"])
        self.assertEqual(_relations(output, "branch_triple_harmony"), [])

    def test_xiyong_contract_case_b(self):
        output = _combine_b()
        xiyong = output["xiyong"]
        self.assertIsNone(xiyong["unified_verdict"])
        fuyi = xiyong["systems"]["fuyi"]
        self.assertEqual(fuyi["status"], "not_buildable")
        # 与算例 A 对照：本例通根结构存在（月午藏己、日辰藏戊、时巳藏戊），
        # 但扶抑仍零行可建——通根事实不推出扶抑方向。
        self.assertTrue(fuyi["consumed_strength_factors"]
                        ["root_candidates"]["present_structurally"])
        self.assertEqual(
            len(fuyi["consumed_strength_factors"]["root_candidates"]
                ["positions"]), 3)
        tiaohou = xiyong["systems"]["tiaohou"]
        self.assertEqual(tiaohou["sequence_stems"], ["壬", "甲"])
        bingyao = xiyong["systems"]["bingyao"]
        self.assertEqual(
            [(p["pair_id"], p["status"], p["medicine_status"])
             for p in bingyao["pairs"]],
            [("wealth_peer_officer", "not_triggered", None),
             ("foodwound_seal_wealth", "triggered", "absent")])
        annual = xiyong["annual_xiyong"]
        self.assertFalse(annual["flow_references"]["tiaohou"]
                         ["flow_stem_in_natal_tiaohou_sequence"])
        pair_refs = annual["flow_references"]["bingyao"]["pairs"]
        self.assertEqual(pair_refs[0]["flow_ten_god_role_in_pair"], "none")
        self.assertEqual(pair_refs[1]["flow_ten_god_role_in_pair"], "subject")
        for relation in output["structural_relations"]:
            if relation["effect"]["status"] == "conditional":
                verdicts = [c["verdict"] for c in relation["effect"]
                            ["conditional_conclusions"]]
                self.assertTrue(all(
                    verdict in (
                        "stem_matches_natal_tiaohou_sequence",
                        "stem_matches_bingyao_medicine_god",
                        "stem_matches_bingyao_subject_god")
                    for verdict in verdicts))
                self.assertTrue(relation["effect"]["basis"]
                                ["not_an_efficacy_verdict"])
            else:
                self.assertEqual(relation["effect"]["status"], "abstain")
                self.assertIsNone(relation["effect"]["verdict"])
        # 第二批：大运二壬在原局调候序列（壬/甲）中，5 条大运×原局天干
        # 关系（第 2 运 4 条 five_element＋1 条丁壬五合）与 1 条大运×流年
        # 天干关系（第 2 运）得条件结论；第三批：病药第二对已触发，
        # 辛/庚（食伤，所论之神类）11 条、壬/癸（财，药神类）12 条；
        # 条件结论只记存在性事实，不是大运效力断言。
        effects = output["effects"]
        self.assertIsNone(effects["overall_effect"])
        self.assertFalse(effects["all_abstained"])
        self.assertEqual(effects["conditional_count"], 21)
        self.assertEqual(effects["abstain_count"], 7)
        self.assertEqual(effects["verdict_counts"],
                         {"abstain": 7, "conditional": 21})
        self.assertEqual(
            {c["relation_id"] for c in effects["conditional_effects"]},
            {"R001", "R002", "R004", "R005", "R007", "R009", "R010",
             "R011", "R012", "R014", "R015", "R016", "R017", "R019",
             "R020", "R021", "R022", "R024", "R025", "R026", "R027"})
        mentions = {}
        for entry in effects["conditional_effects"]:
            for verdict in entry["verdicts"]:
                mentions[verdict] = mentions.get(verdict, 0) + 1
        self.assertEqual(mentions, {
            "stem_matches_bingyao_subject_god": 11,
            "stem_matches_natal_tiaohou_sequence": 6,
            "stem_matches_bingyao_medicine_god": 12})
        # 药神类在场但药不在盘（medicine_status absent）：结论只记
        # 药神类存在性，不据此称药已到、病已去。
        medicine = [c for e in effects["conditional_effects"]
                    for c in e["conclusions"]
                    if c["verdict"]
                    == "stem_matches_bingyao_medicine_god"]
        self.assertEqual(len(medicine), 12)
        self.assertTrue(all(
            c["pair_id"] == "foodwound_seal_wealth" for c in medicine))
        self.assertTrue(all(
            c["basis"]["medicine_status"] == "absent" for c in medicine))


class CounterexampleTests(unittest.TestCase):
    """反证：不存在的关系不得出现；有结构事实也不得推出效力。"""

    def test_no_combination_where_none_exists(self):
        # 算例 B 流年干庚与原局四干（己/庚/戊/丁）无一五合。
        output = _combine_b()
        self.assertEqual(
            _relations(output, "flow_x_natal", "stem_five_combination"), [])
        # 算例 A 大运酉与原局子无已审地支关系。
        output_a = _combine_a()
        self.assertFalse(_has_pair(
            _relations(output_a, "dayun_x_natal", period_index=1),
            "酉", "子"))
        # 算例 A 大运×原局无六合（只有害）；流年×原局无三合以外的组关系
        # 之外的六合。
        self.assertEqual(
            _relations(output_a, "dayun_x_natal", "branch_six_harmony"), [])
        self.assertEqual(
            _relations(output_a, "dayun_x_natal", "branch_triple_harmony"),
            [])

    def test_present_medicine_does_not_prove_effect(self):
        # 算例 A 病药第一对药候选已 present，但去病效力仍未裁定，
        # 且组合效力层 overall_effect 恒为 None——存在药候选不等于
        # 药已去病。第三批：药神类在场只得存在性条件结论（大运辛
        # 5 条），结论本身亦明记不是效力断言。
        output = _combine_a()
        pairs = output["xiyong"]["systems"]["bingyao"]["pairs"]
        self.assertEqual(pairs[0]["medicine_status"], "candidate_present")
        self.assertEqual(pairs[0]["medicine_effect_status"], "unadjudicated")
        self.assertIsNone(output["effects"]["overall_effect"])
        self.assertEqual(output["effects"]["verdict_counts"],
                         {"abstain": 18, "conditional": 12})
        medicine_entries = [
            entry for entry in output["effects"]["conditional_effects"]
            if "stem_matches_bingyao_medicine_god" in entry["verdicts"]]
        self.assertEqual(len(medicine_entries), 5)
        for entry in medicine_entries:
            conclusions = [c for c in entry["conclusions"]
                           if c["verdict"]
                           == "stem_matches_bingyao_medicine_god"]
            self.assertEqual(len(conclusions), 1)
            conclusion = conclusions[0]
            self.assertEqual(conclusion["pair_id"],
                             "wealth_peer_officer")
            self.assertEqual(conclusion["role"], "medicine")
            self.assertIn("不等于病已去", conclusion["reason"])
            self.assertIn("bazi.phase2.bingyao_assessment",
                          conclusion["basis"]["rule_ids"])
            self.assertIn("shenfeng.wealth_peer_officer",
                          conclusion["basis"]["rule_ids"])
        for relation in output["structural_relations"]:
            if relation["effect"]["status"] == "conditional":
                self.assertTrue(relation["effect"]["basis"]
                                ["not_an_efficacy_verdict"])

    def test_ganzhi_string_pillars_agree_with_structured_pillars(self):
        structured = _combine_a()
        plain = combine(["戊戌", "庚申", "甲子", "甲戌"], "甲",
                        CASE_A_DAYUN, 1988,
                        strength=_FIXTURES["A"]["strength"],
                        tiaohou=_FIXTURES["A"]["tiaohou"],
                        bingyao=_FIXTURES["A"]["bingyao"])
        self.assertEqual(plain["relation_summary"],
                         structured["relation_summary"])
        self.assertEqual(plain["structural_relations"],
                         structured["structural_relations"])


class CallerSelectedPeriodTests(unittest.TestCase):
    def test_current_period_selection_is_recorded_not_derived(self):
        output = _combine_a(current_period_index=3,
                            current_period_basis=(
                                "Golden Q1 handover interval period 3 "
                                "[1986-05-25, 1986-06-04)"))
        self.assertEqual(output["dayun"]["period_year_mapping"],
                         "caller_selected")
        self.assertEqual(output["dayun"]["current_period_index"], 3)
        for relation in _relations(output, "dayun_x_flow"):
            mapping = [c for c in relation["conditions"]
                       if c["id"] == "period_year_mapping"][0]
            if relation["period_index"] == 3:
                self.assertEqual(mapping["status"], "satisfied")
            else:
                self.assertEqual(mapping["status"], "not_satisfied")
        # 指定当期运只改期位前提的标注，不改变关系总数与效力。
        self.assertEqual(output["relation_summary"]["total"], 30)
        self.assertEqual(output["effects"]["verdict_counts"],
                         {"abstain": 18, "conditional": 12})


class FailClosedTests(unittest.TestCase):
    def test_bad_inputs(self):
        with self.assertRaises(ValueError):
            combine(CASE_A_PILLARS, "乙", CASE_A_DAYUN, 1988)
        with self.assertRaises(ValueError):
            combine(list(reversed(CASE_A_PILLARS)), "甲", CASE_A_DAYUN, 1988)
        with self.assertRaises(ValueError):
            combine(CASE_A_PILLARS, "甲", CASE_A_DAYUN, 1800)
        with self.assertRaises(ValueError):
            combine(CASE_A_PILLARS, "甲", [], 1988)
        with self.assertRaises(ValueError):
            combine(CASE_A_PILLARS, "甲", CASE_A_DAYUN, 1988,
                    variant="not-a-variant")
        with self.assertRaises(ValueError):
            combine(CASE_A_PILLARS, "甲", CASE_A_DAYUN, 1988,
                    current_period_index=3)
        with self.assertRaises(ValueError):
            combine(CASE_A_PILLARS, "甲", CASE_A_DAYUN, 1988,
                    current_period_index=9,
                    current_period_basis="no such period")

    def test_dayun_ten_god_mismatch_is_rejected(self):
        wrong = [dict(row) for row in CASE_A_DAYUN]
        wrong[0] = dict(wrong[0], ten_god="正印")
        with self.assertRaises(ValueError):
            combine(CASE_A_PILLARS, "甲", wrong, 1988)

    def test_system_statement_drift_is_rejected(self):
        drifted = json.loads(json.dumps(_FIXTURES["A"]["tiaohou"]))
        drifted["variant"] = "tiaohou-qiongtong-v2"
        with self.assertRaises(ValueError):
            _combine_a(tiaohou=drifted)
        drifted = json.loads(json.dumps(_FIXTURES["A"]["bingyao"]))
        drifted["determination"] = {"pattern": "正官格"}
        with self.assertRaises(ValueError):
            _combine_a(bingyao=drifted)
        drifted = json.loads(json.dumps(_FIXTURES["A"]["strength"]))
        drifted["overall_strength"] = "strong"
        with self.assertRaises(ValueError):
            _combine_a(strength=drifted)
        # 格局候选若带已定格名，一律拒收。
        with self.assertRaises(ValueError):
            _combine_a(pattern={
                "variant": "bazi-pattern-structure-candidates-v1",
                "family": "official",
                "status": "structural_observation_only",
                "determination": {"status": "resolved", "pattern": "正官格",
                                  "true_false": True, "useful_god": "财"},
                "research_only": True, "public_enabled": False,
                "ai_enabled": False})

    def test_pattern_candidate_passthrough_without_determination(self):
        pattern = {
            "variant": "bazi-pattern-structure-candidates-v1",
            "family": "official",
            "status": "structural_observation_only",
            "observations": [],
            "determination": {"status": "unresolved", "pattern": None,
                              "true_false": None, "useful_god": None},
            "research_only": True, "public_enabled": False,
            "ai_enabled": False,
        }
        output = _combine_a(pattern=pattern)
        block = output["xiyong"]["systems"]["pattern_yongshen"]
        self.assertEqual(block["status"], "structural_observation_only")
        self.assertIsNone(block["pattern"])
        self.assertIsNone(block["useful_god"])
        self.assertIsNone(output["xiyong"]["unified_verdict"])

    def test_missing_systems_are_not_invented(self):
        output = combine(CASE_A_PILLARS, "甲", CASE_A_DAYUN, 1988)
        systems = output["xiyong"]["systems"]
        self.assertEqual(systems["tiaohou"]["status"], "not_provided")
        self.assertEqual(systems["bingyao"]["status"], "not_provided")
        self.assertEqual(systems["pattern_yongshen"]["status"], "not_provided")
        self.assertEqual(systems["fuyi"]["status"], "not_buildable")
        self.assertIsNone(output["xiyong"]["unified_verdict"])
        self.assertIsNone(output["xiyong"]["annual_xiyong"]["derivation"])


class TenGodTests(unittest.TestCase):
    def test_ten_god_spot_values(self):
        self.assertEqual(ten_god_for("甲", "丙"), "食神")
        self.assertEqual(ten_god_for("甲", "庚"), "七杀")
        self.assertEqual(ten_god_for("甲", "辛"), "正官")
        self.assertEqual(ten_god_for("甲", "癸"), "正印")
        self.assertEqual(ten_god_for("甲", "甲"), "比肩")
        self.assertEqual(ten_god_for("甲", "乙"), "劫财")
        self.assertEqual(ten_god_for("戊", "庚"), "食神")
        self.assertEqual(ten_god_for("戊", "丁"), "正印")
        self.assertEqual(ten_god_for("戊", "壬"), "偏财")
        self.assertEqual(ten_god_for("戊", "甲"), "七杀")
        with self.assertRaises(ValueError):
            ten_god_for("甲", "子")


class CrossCheckTests(unittest.TestCase):
    """组装环境复核：夹具与转录表须与真实模块逐项一致。

    公开检出无历法 provider 与密封数据时跳过（不伪造通过）。
    """

    def _sealed_modules(self):
        try:
            from tianji_kb import bazi_bingyao as _by  # noqa: F401
            from tianji_kb import bazi_core as _bc  # noqa: F401
            from tianji_kb import bazi_strength as _st  # noqa: F401
            from tianji_kb import bazi_tiaohou as _th  # noqa: F401
            from tianji_kb.bazi_annual_reference import (  # noqa: F401
                annual_lichun_boundaries as _lb)
            from tianji_kb.bazi_dayun_sequence import (  # noqa: F401
                candidate_sequence as _cs)
        except Exception as error:  # noqa: BLE001 - 密封依赖缺失即跳过
            self.skipTest("sealed modules unavailable: %s" % error)
        return _bc, _st, _th, _by, _lb, _cs

    def test_fixtures_match_live_modules(self):
        (bc, st, th, by, _lb, cs) = self._sealed_modules()
        cases = (
            ("A", "1958-08-15T19:30:00+08:00", "forward"),
            ("B", "1959-06-15T10:30:00+08:00", "forward"),
        )
        for key, birth, direction in cases:
            with self.subTest(case=key):
                chart = bc.chart_from_datetime(birth)
                pillars = chart["pillars"]
                self.assertEqual(
                    [(p["name"], p["ganzhi"]) for p in pillars],
                    [(p["name"], p["ganzhi"])
                     for p in _FIXTURES[key]["pillars"]])
                # 夹具经 JSON 嵌入，tuple 已归一化为 list；比对前对实时输出
                # 做同一 JSON 往返，逐字比对才有意义。
                def _normalized(value):
                    return json.loads(json.dumps(value, ensure_ascii=False))
                self.assertEqual(
                    _normalized(st.factors(pillars,
                                           chart["day_master"]["stem"])),
                    _FIXTURES[key]["strength"])
                visible = [p["stem"]["value"] for p in pillars]
                hidden = [[h["stem"] for h in p["branch"]["hidden_stems"]]
                          for p in pillars]
                self.assertEqual(
                    _normalized(th.tiaohou_lookup(
                        chart["day_master"]["stem"],
                        pillars[1]["branch"]["value"], visible, hidden)),
                    _FIXTURES[key]["tiaohou"])
                visible_gods = [
                    {"pillar": name, "stem": pillars[i]["stem"]["value"],
                     "ten_god": pillars[i]["stem"]["ten_god"]}
                    for i, name in ((0, "year"), (1, "month"), (3, "hour"))]
                self.assertEqual(
                    _normalized(by.bingyao_lookup(chart["day_master"]["stem"],
                                                  visible_gods)),
                    _FIXTURES[key]["bingyao"])
                sequence = cs(pillars[1]["ganzhi"],
                              chart["day_master"]["stem"],
                              direction=direction, periods=3)
                dayun = CASE_A_DAYUN if key == "A" else CASE_B_DAYUN
                self.assertEqual(
                    [(r["candidate_ganzhi"],
                      r["ten_god_relative_to_natal_day_stem"])
                     for r in sequence["rows"]],
                    [(r["candidate_ganzhi"], r["ten_god"]) for r in dayun])

    def test_flow_ganzhi_matches_lichun_boundaries(self):
        (_bc, _st, _th, _by, lb, _cs) = self._sealed_modules()
        for key, year in (("A", 1988), ("B", 1970)):
            output = _combine_a() if key == "A" else _combine_b()
            rows = lb(output["natal"]["pillars"][2]["stem"], [year])["rows"]
            self.assertEqual(rows[0]["ganzhi_in_interval"],
                             output["flow_year"]["ganzhi"])
            self.assertEqual(rows[0]["ten_god_relative_to_natal_day_stem"],
                             output["flow_year"]["stem_ten_god"])

    def test_transcribed_tables_match_canonical(self):
        (bc, _st, _th, _by, _lb, _cs) = self._sealed_modules()
        from tianji_kb.bazi_combination_engine import (
            BRANCH_CLASHES,
            BRANCH_HARMS,
            BRANCH_SIX_HARMONIES,
            STEM_FIVE_COMBINATIONS,
        )
        from tianji_kb.foundations import BRANCHES, STEMS
        for left in STEMS:
            for right in STEMS:
                if left >= right:
                    continue
                expected = bc.stem_five_combination(left, right)
                key = frozenset((left, right))
                if key in STEM_FIVE_COMBINATIONS:
                    self.assertTrue(expected["matched"])
                    self.assertEqual(expected["traditional_result_element"],
                                     STEM_FIVE_COMBINATIONS[key])
                else:
                    self.assertFalse(expected["matched"])
        for left in BRANCHES:
            for right in BRANCHES:
                if left >= right:
                    continue
                expected = {item["kind"]: item
                            for item in bc.reviewed_branch_pair_relations(
                                left, right)}
                key = frozenset((left, right))
                if key in BRANCH_SIX_HARMONIES:
                    self.assertIn("six_harmony", expected)
                    self.assertEqual(
                        expected["six_harmony"]["traditional_result_element"],
                        BRANCH_SIX_HARMONIES[key])
                else:
                    self.assertNotIn("six_harmony", expected)
                self.assertEqual("harm" in expected, key in BRANCH_HARMS)
                self.assertEqual("clash" in expected, key in BRANCH_CLASHES)
        for left in STEMS:
            for right in STEMS:
                self.assertEqual(ten_god_for(left, right),
                                 bc.ten_god(left, right))
        # 第三批：地支本气转录表须与 seed.json 的 earthly_branches
        # 行本气列逐项一致（公开检出无 seed.json，本测试只在机上跑）。
        from tianji_kb.bazi_combination_engine import BRANCH_ELEMENTS
        from tianji_kb.foundations import branch_element
        for branch in BRANCHES:
            self.assertEqual(BRANCH_ELEMENTS[branch],
                             branch_element(branch))


class LiveEngineInputsTests(unittest.TestCase):
    """第二批接线：机上实时构建三路引擎输出并传入 combine()。

    公开检出无密封模块时整类跳过（不伪造通过）。C1 已接通
    （2026-11-25）：喜用引擎格局 pin 已升 v2，``evaluate_xiyong``
    传入真实格局 v2 输出；本地已验证输入结构/版本/字段语义与
    兼容性（见 /tmp/c1_verify.py 式验证：v2 接受、v1 拒收、
    pattern=None 仍可用），机上实时接通待验证。
    """

    @classmethod
    def setUpClass(cls):
        try:
            from tianji_kb import bazi_bingyao as _by  # noqa: F401
            from tianji_kb import bazi_core as _bc  # noqa: F401
            from tianji_kb import bazi_tiaohou as _th  # noqa: F401
            from tianji_kb.bazi_dayun_sequence import (  # noqa: F401
                candidate_sequence as _cs)
            from tianji_kb.bazi_pattern import (  # noqa: F401
                PATTERN_VARIANT as _pv)
            from tianji_kb.bazi_pattern_engine import (  # noqa: F401
                evaluate_all as _ea,
                evaluate_patterns_from_trace as _ept)
            from tianji_kb.bazi_siling_pilot import (  # noqa: F401
                yin_siling_pilot as _pilot)
            from tianji_kb.bazi_strength_engine import (  # noqa: F401
                assess_strength as _assess)
            from tianji_kb.bazi_xiyong_engine import (  # noqa: F401
                evaluate_xiyong as _ex)
            from tianji_kb.operations.bazi_chart import (  # noqa: F401
                chart as _chart_op)
        except Exception as error:  # noqa: BLE001 - 密封依赖缺失即跳过
            raise unittest.SkipTest(
                "live engine modules unavailable: %s" % error)
        cls.core = _bc
        # 函数赋给类属性会被绑定为方法（多传 self），须包 staticmethod。
        cls.assess = staticmethod(_assess)
        cls.evaluate_all = staticmethod(_ea)
        cls.evaluate_from_trace = staticmethod(_ept)
        cls.pattern_variant = _pv
        cls.pilot_fn = staticmethod(_pilot)
        cls.chart_op = staticmethod(_chart_op)
        cls.tiaohou_fn = staticmethod(_th.tiaohou_lookup)
        cls.bingyao_fn = staticmethod(_by.bingyao_lookup)
        cls.dayun_fn = staticmethod(_cs)
        cls.xiyong_fn = staticmethod(_ex)
        root = Path(__file__).resolve().parents[1]
        cls.ren_yin_golden = json.loads(
            (root / "tests/golden_tj012_ren_yin_true.json")
            .read_text(encoding="utf-8"))

    def _build(self, birth, target_year, *, trace_pattern=False):
        chart = self.core.chart_from_datetime(birth)
        pillars = chart["pillars"]
        day_master = chart["day_master"]["stem"]
        ganzhi = [p["ganzhi"] for p in pillars]
        strength = self.assess(pillars, day_master)
        if trace_pattern:
            year = birth[:4]
            window = self.ren_yin_golden["jie_windows"][year]
            pilot = self.pilot_fn(
                birth, version_id="ditiansui-yuanshuo",
                jie_facts={
                    "provider": dict(self.ren_yin_golden["provider"]),
                    "lichun": dict(window["lichun"]),
                    "next_jie": dict(window["next_jie"])})
            out = self.chart_op(
                *ganzhi, pattern_variant=self.pattern_variant,
                ren_yin_pilot_result=pilot)
            pattern = self.evaluate_from_trace(
                {"trace": out["trace"], "evidence": out["evidence"]},
                pilot_result=pilot)
        else:
            pattern = self.evaluate_all(
                self.core.chart_from_pillars(*ganzhi))
        visible = [p["stem"]["value"] for p in pillars]
        hidden = [[h["stem"] for h in p["branch"]["hidden_stems"]]
                 for p in pillars]
        tiaohou = self.tiaohou_fn(
            day_master, pillars[1]["branch"]["value"], visible, hidden)
        visible_gods = [
            {"pillar": name, "stem": pillars[i]["stem"]["value"],
             "ten_god": pillars[i]["stem"]["ten_god"]}
            for i, name in ((0, "year"), (1, "month"), (3, "hour"))]
        bingyao = self.bingyao_fn(day_master, visible_gods)
        sequence = self.dayun_fn(
            pillars[1]["ganzhi"], day_master, direction="forward",
            periods=3)
        dayun = [{"candidate_ganzhi": r["candidate_ganzhi"],
                  "period_index": r["period_index"],
                  "ten_god": r["ten_god_relative_to_natal_day_stem"]}
                 for r in sequence["rows"]]
        xiyong = self.xiyong_fn(
            day_master=day_master,
            month_branch=pillars[1]["branch"]["value"],
            pillars=ganzhi, strength=strength, tiaohou=tiaohou,
            bingyao=bingyao, pattern=pattern, flow_year=target_year)
        combined = combine(pillars, day_master, dayun, target_year,
                           strength=strength, tiaohou=tiaohou,
                           bingyao=bingyao, pattern=pattern,
                           xiyong=xiyong)
        return {"chart": chart, "ganzhi": ganzhi,
                "day_master": day_master, "strength": strength,
                "pattern": pattern, "tiaohou": tiaohou,
                "bingyao": bingyao, "dayun": dayun, "xiyong": xiyong,
                "combined": combined}

    def _verdict_counter(self, output):
        counter = {}
        for entry in output["effects"]["conditional_effects"]:
            for verdict in entry["verdicts"]:
                counter[verdict] = counter.get(verdict, 0) + 1
        return counter

    def test_full_inputs_case_a(self):
        built = self._build("1958-08-15T19:30:00+08:00", 1988)
        self.assertEqual(built["dayun"], CASE_A_DAYUN)
        out = built["combined"]
        self.assertEqual(out["relation_summary"]["total"], 30)
        # 裁定后新期望（X1/C3 已批，E2 条件结论点火，verdict 由 abstain
        # 为主转为 conditional 为主）：机上实测 2026-11-25。
        self.assertEqual(out["effects"]["verdict_counts"],
                         {"abstain": 7, "conditional": 23})
        # 裁定后新期望：病药三角色（主体 8、药 5）与格局候选格神（5）
        # 随 X1/C3 点火加入原有 7 条模型口径结论；机上实测 2026-11-25。
        self.assertEqual(self._verdict_counter(out),
                         {"model_treatment_recorded_only": 7,
                          "stem_matches_bingyao_medicine_god": 5,
                          "stem_matches_bingyao_subject_god": 8,
                          "stem_matches_pattern_candidate_god": 5})
        self.assertEqual(
            {c["relation_id"]
             for c in out["effects"]["conditional_effects"]},
            {"R001", "R002", "R003", "R004", "R005", "R006", "R008",
             "R009", "R010", "R011", "R015", "R018", "R019", "R020",
             "R021", "R022", "R023", "R025", "R026", "R027", "R028",
             "R029", "R030"})
        # 旺衰：古典 indeterminate、现代 weak -21（definite），分项照录。
        strength = out["strength"]
        self.assertEqual(strength["classical"]["classification"],
                         "indeterminate")
        self.assertIsNone(strength["classical"]["matched_predicate"])
        modern = strength["modern"]
        self.assertEqual(modern["verdict"], "weak")
        self.assertEqual(modern["score"], -21)
        self.assertEqual(modern["classification_status"], "definite")
        self.assertEqual(modern["definite_classification"], "weak")
        self.assertEqual(modern["uncertainty_flags"], [])
        self.assertEqual(
            {k: v["score"] for k, v in modern["components"].items()},
            {"de_ling": -15, "de_di": 0, "de_shi": 10,
             "shengfu_hidden": 4, "kexiehao": -20})
        self.assertEqual(modern["components"]["de_ling"]["basis"],
                         "principal_qi_庚_controls_me")
        self.assertEqual(strength["agreement"]["relationship"],
                         "classical_indeterminate")
        self.assertEqual(
            modern["cong_candidates"]["candidates"], [])
        self.assertFalse(
            modern["cong_candidates"]["screen_triggered"])
        # 格局：3 候选（七杀/偏印/偏财），无成立、无冲突。
        # A1 后新期望：bijian/jiecai 常驻 not_judgeable，结果数 12→14。
        pattern = out["pattern"]
        self.assertEqual(pattern["counts"],
                         {"not_judgeable": 11, "candidate": 3})
        self.assertEqual(pattern["established"], [])
        self.assertEqual(
            {c["pattern_key"] for c in pattern["candidates"]},
            {"qisha", "pianyin", "piancai"})
        # 喜用：年度契约 6 项已实现（含新增 2 项），待批 5 项不变。
        xiyong = out["xiyong"]
        self.assertEqual(xiyong["variant"], "bazi-xiyong-engine-v1")
        self.assertIsNone(xiyong["unified_verdict"])
        annual = xiyong["annual_xiyong"]
        self.assertEqual(annual["implemented"], [
            "flow_year_ganzhi_and_ten_god",
            "flow_stem_presence_against_natal_tiaohou_sequence",
            "flow_stem_ten_god_role_against_bingyao_pairs",
            "rule_call_structure",
            "flow_stem_presence_against_fuyi_modern_candidates",
            "flow_stem_presence_against_pattern_basis",
        ])
        self.assertEqual(annual["pending"], [
            "annual_tiaohou_derivation", "annual_bingyao_derivation",
            "annual_fuyi_derivation",
            "annual_pattern_yongshen_derivation",
            "unified_annual_verdict",
        ])
        self.assertEqual(
            annual["flow_references"]["fuyi"]
            ["natal_fuyi_modern_candidate_stems"], ["甲"])
        self.assertFalse(
            annual["flow_references"]["fuyi"]
            ["flow_stem_in_natal_fuyi_modern_candidates"])
        # 扶抑现代层：weak→生扶，候选干甲（时干）；流年干戊不在其中。
        fuyi_modern = xiyong["systems"]["fuyi"]["modern"]
        self.assertEqual(fuyi_modern["direction_cn"], "生扶")
        self.assertEqual(
            [g["stem"] for g in fuyi_modern["candidate_stems"]], ["甲"])
        for rule_id in ("bazi-strength-engine-v1",
                        "bazi-pattern-engine-v2",
                        "bazi-xiyong-engine-v1",
                        "strength_model_modern_v1"):
            self.assertIn(rule_id, out["consumed_rule_ids"])

    def test_full_inputs_case_b_uncertainty_propagates(self):
        built = self._build("1959-06-15T10:30:00+08:00", 1970)
        self.assertEqual(built["dayun"], CASE_B_DAYUN)
        out = built["combined"]
        self.assertEqual(out["relation_summary"]["total"], 28)
        # 裁定后新期望（X1/C3 已批，E2 条件结论点火）：机上实测
        # 2026-11-25。
        self.assertEqual(out["effects"]["verdict_counts"],
                         {"abstain": 1, "conditional": 27})
        # 裁定后新期望：病药三角色（主体 11、药 12）加入原有 6+6；
        # 机上实测 2026-11-25。
        self.assertEqual(self._verdict_counter(out), {
            "model_treatment_recorded_only": 6,
            "stem_matches_bingyao_medicine_god": 12,
            "stem_matches_bingyao_subject_god": 11,
            "stem_matches_natal_tiaohou_sequence": 6})
        # 旺衰：土日主 Q5 暂定分——balanced 53 只作研究性暂定分，
        # definite_classification 恒 None，不确定性传导进组合层。
        modern = out["strength"]["modern"]
        self.assertEqual(modern["verdict"], "balanced")
        self.assertEqual(modern["score"], 53)
        self.assertEqual(modern["classification_status"],
                         "provisional_incomplete")
        self.assertIsNone(modern["definite_classification"])
        self.assertEqual(modern["uncertainty_flags"],
                         ["earth_de_di_uncalibrated"])
        self.assertEqual(
            {k: v["score"] for k, v in modern["components"].items()},
            {"de_ling": 20, "de_di": 15, "de_shi": 20,
             "shengfu_hidden": 10, "kexiehao": -12})
        self.assertEqual(out["strength"]["agreement"]["relationship"],
                         "modern_provisional")
        # 扶抑现代层 balanced 不给方向；不确定性标记随喜用层传导。
        fuyi = out["xiyong"]["systems"]["fuyi"]
        self.assertEqual(fuyi["status"], "not_judgeable")
        self.assertEqual(fuyi["modern"]["status"],
                         "indeterminate_direction")
        self.assertIn("earth_de_di_uncalibrated",
                      fuyi["modern"]["uncertainty"])
        # X8 裁定后新期望（用户裁定 2026-11-25）：balanced 只是现代模
        # 型分数区间，本身不代表输入证据不足，不入 uncertainty；只
        # 传导 Q5/Q6 条件缺失。机上实测 2026-11-25。
        self.assertEqual(fuyi["uncertainty"],
                         ["classical_strength_indeterminate",
                          "ding_de_di_uncalibrated",
                          "earth_de_di_uncalibrated",
                          "tomb_de_ling_zero_provisional"])
        self.assertNotIn("balanced_middle_band_only",
                         fuyi["uncertainty"])
        # 格局：仅正印候选。A1 后新期望：bijian/jiecai 常驻，结果数 12→14。
        self.assertEqual(out["pattern"]["counts"],
                         {"not_judgeable": 13, "candidate": 1})
        self.assertEqual(
            [c["pattern_key"] for c in out["pattern"]["candidates"]],
            ["zhengyin"])

    def test_full_inputs_case_c_established_pattern_consumable(self):
        built = self._build("2023-02-12T16:00:00+08:00", 2026,
                            trace_pattern=True)
        self.assertEqual(built["ganzhi"], ["癸卯", "甲寅", "辛丑", "丙申"])
        self.assertEqual(built["dayun"], [
            {"candidate_ganzhi": "乙卯", "period_index": 1,
             "ten_god": "偏财"},
            {"candidate_ganzhi": "丙辰", "period_index": 2,
             "ten_god": "正官"},
            {"candidate_ganzhi": "丁巳", "period_index": 3,
             "ten_god": "七杀"},
        ])
        out = built["combined"]
        self.assertEqual(out["flow_year"]["ganzhi"], "丙午")
        self.assertEqual(out["flow_year"]["stem_ten_god"], "正官")
        self.assertEqual(out["relation_summary"]["total"], 26)
        self.assertEqual(out["relation_summary"]["counts_by_scope"],
                         {"dayun_x_natal": 17, "flow_x_natal": 6,
                          "dayun_x_flow": 3})
        # C6 弃判传导：现代旺衰层弃判（components 为 None），Q3-A 模型
        # 口径结论不发；13 条成立格神结论（独立）不受影响。
        self.assertEqual(out["effects"]["verdict_counts"],
                         {"abstain": 13, "conditional": 13})
        self.assertEqual(self._verdict_counter(out), {
            "stem_matches_established_pattern_god": 13})
        # C4：forward 是 _build 向 candidate_sequence 明确指定的研究
        # 算例参数；combine() 本身不推导、不记录方向。
        self.assertNotIn("direction", out["dayun"])
        # D-1 正官格成立可被岁运组合消费：大运二丙、流年丙与格神同十神。
        # A1 后新期望：bijian/jiecai 常驻 not_judgeable，结果数 12→14。
        pattern = out["pattern"]
        self.assertEqual(pattern["counts"],
                         {"established": 1, "not_judgeable": 10,
                          "candidate": 3})
        self.assertEqual(
            [e["pattern"] for e in pattern["established"]], ["正官"])
        self.assertIn("ren_yin_true_pattern",
                      pattern["established"][0]["evidence_ids"])
        self.assertIn("ren_yin_rule",
                      pattern["established"][0]["evidence_ids"])
        self.assertNotIn("broken", pattern["counts"])
        god_matches = [
            c for c in out["effects"]["conditional_effects"]
            if c["verdicts"] == ["stem_matches_established_pattern_god"]]
        self.assertEqual(len(god_matches), 13)
        self.assertTrue(all(
            c["conclusions"][0]["pattern_god"] == "正官"
            for c in god_matches))
        # 旺衰现代层因合化未决而弃判：丙辛五合在场，components 为 None。
        modern = out["strength"]["modern"]
        self.assertEqual(modern["verdict"], "abstain")
        self.assertEqual(modern["abstain_reason"],
                         "transformation_candidate_unresolved")
        self.assertIsNone(modern["score"])
        self.assertIsNone(modern["components"])
        self.assertEqual(out["strength"]["agreement"]["relationship"],
                         "modern_abstains")
        # 喜用：调候序列己/壬/庚，流年丙不在其中；扶抑现代层亦弃判。
        self.assertEqual(
            [c["stem"] for c in
             out["xiyong"]["systems"]["tiaohou"]["candidates"]],
            ["己", "壬", "庚"])
        self.assertFalse(
            out["xiyong"]["annual_xiyong"]["flow_references"]["tiaohou"]
            ["flow_stem_in_natal_tiaohou_sequence"])
        self.assertEqual(
            out["xiyong"]["systems"]["fuyi"]["modern"]["status"],
            "abstain")

    def test_full_inputs_case_a_flow_1984_fuyi_candidate_match(self):
        # 流年 1984 甲子：流年干甲与扶抑现代候选干同字，E2 触发。
        built = self._build("1958-08-15T19:30:00+08:00", 1984)
        out = built["combined"]
        self.assertEqual(out["flow_year"]["ganzhi"], "甲子")
        self.assertEqual(out["relation_summary"]["total"], 24)
        # 裁定后新期望（X1/C3 已批，E2 条件结论点火）：机上实测
        # 2026-11-25。
        self.assertEqual(out["effects"]["verdict_counts"],
                         {"abstain": 6, "conditional": 18})
        # 裁定后新期望：E2（7）与模型口径（3）不变，病药（病 7、药 5）
        # 与格局候选格神（5）加入；机上实测 2026-11-25。
        self.assertEqual(self._verdict_counter(out), {
            "stem_matches_fuyi_modern_candidate": 7,
            "stem_matches_bingyao_disease_god": 7,
            "stem_matches_bingyao_medicine_god": 5,
            "stem_matches_pattern_candidate_god": 5,
            "model_treatment_recorded_only": 3})
        # E2 仍在 R018–R024 点火；现每条关系可带多条 verdict（病药/
        # 格局结论同条并存），故以包含判定，不再要求 verdicts 恰为
        # 单条 E2。
        self.assertEqual(
            {c["relation_id"]
             for c in out["effects"]["conditional_effects"]
             if "stem_matches_fuyi_modern_candidate" in c["verdicts"]},
            {"R018", "R019", "R020", "R021", "R022", "R023", "R024"})
        self.assertTrue(
            out["xiyong"]["annual_xiyong"]["flow_references"]["fuyi"]
            ["flow_stem_in_natal_fuyi_modern_candidates"])

    def test_no_xiyong_path_keeps_legacy_annual_contract(self):
        # 未传 xiyong 输出时：旧 4 项契约＋新形态评估/格局摘要照录。
        built = self._build("1958-08-15T19:30:00+08:00", 1988)
        out = combine(built["chart"]["pillars"], "甲", built["dayun"],
                      1988, strength=built["strength"],
                      tiaohou=built["tiaohou"],
                      bingyao=built["bingyao"],
                      pattern=built["pattern"])
        self.assertEqual(
            out["xiyong"]["annual_xiyong"]["implemented"], [
                "flow_year_ganzhi_and_ten_god",
                "flow_stem_presence_against_natal_tiaohou_sequence",
                "flow_stem_ten_god_role_against_bingyao_pairs",
                "rule_call_structure",
            ])
        fuyi = out["xiyong"]["systems"]["fuyi"]
        self.assertEqual(fuyi["status"], "not_buildable")
        self.assertEqual(
            fuyi["consumed_strength_assessment"]["modern_verdict"],
            "weak")
        self.assertEqual(
            fuyi["consumed_strength_assessment"]["modern_score"], -21)
        pattern_block = out["xiyong"]["systems"]["pattern_yongshen"]
        self.assertEqual(pattern_block["status"],
                         "presented_from_pattern_v2")
        self.assertEqual(
            [e["pattern_key"] for e in pattern_block["eligible"]],
            ["pianyin"])
        self.assertIsNone(pattern_block["useful_god"])
        # 裁定后新期望（无 xiyong 路径亦消费病药角色与格局候选格神）：
        # 机上实测 2026-11-25；C 盘 {13, 13} 不变（同日实测）。
        self.assertEqual(out["effects"]["verdict_counts"],
                         {"abstain": 7, "conditional": 23})
        # C 盘同路径：已成立正官格列入有资格格，但仍无已审用神。
        built_c = self._build("2023-02-12T16:00:00+08:00", 2026,
                              trace_pattern=True)
        out_c = combine(built_c["chart"]["pillars"], "辛",
                        built_c["dayun"], 2026,
                        strength=built_c["strength"],
                        tiaohou=built_c["tiaohou"],
                        bingyao=built_c["bingyao"],
                        pattern=built_c["pattern"])
        pattern_c = out_c["xiyong"]["systems"]["pattern_yongshen"]
        self.assertEqual(pattern_c["established"], ["正官"])
        self.assertEqual(
            [(e["pattern_key"], e["state"])
             for e in pattern_c["eligible"]],
            [("zhengguan", "established"),
             ("zhengyin", "candidate")])
        self.assertIsNone(pattern_c["useful_god"])
        # C6：现代旺衰弃判，Q3-A 模型口径结论不发；成立格神结论独立。
        self.assertEqual(out_c["effects"]["verdict_counts"],
                         {"abstain": 13, "conditional": 13})

    def test_scope_coverage_and_not_evaluated(self):
        built = self._build("1958-08-15T19:30:00+08:00", 1988)
        summary = built["combined"]["relation_summary"]
        self.assertEqual(summary["scope_coverage"]["dayun_x_natal"],
                         {"stem_pairs_enumerated": 12,
                          "branch_pairs_enumerated": 12,
                          "group_evaluated": True,
                          "group_branches": "natal_four_plus_dayun",
                          "relations": 17,
                          "branch_pairs_with_reviewed_relation": 3,
                          "branch_pairs_without_reviewed_relation": 9})
        self.assertEqual(summary["scope_coverage"]["flow_x_natal"],
                         {"stem_pairs_enumerated": 4,
                          "branch_pairs_enumerated": 4,
                          "group_evaluated": True,
                          "group_branches": "natal_four_plus_flow",
                          "relations": 7,
                          "branch_pairs_with_reviewed_relation": 2,
                          "branch_pairs_without_reviewed_relation": 2})
        self.assertEqual(summary["scope_coverage"]["dayun_x_flow"],
                         {"stem_pairs_enumerated": 3,
                          "branch_pairs_enumerated": 3,
                          "group_evaluated": True,
                          "group_branches":
                              "dayun_plus_flow_only_two_branches_no_group_formable",
                          "relations": 6,
                          "branch_pairs_with_reviewed_relation": 2,
                          "branch_pairs_without_reviewed_relation": 1})
        self.assertEqual(
            summary["scope_coverage"]["dayun_x_flow_x_natal"],
            {"stem_pairs_enumerated": 0,
             "branch_pairs_enumerated": 0,
             "group_evaluated": True,
             "group_branches":
                 "natal_four_plus_dayun_plus_flow_spanning_only",
             "relations": 0,
             "branch_pairs_with_reviewed_relation": 0,
             "branch_pairs_without_reviewed_relation": 0})
        self.assertEqual(
            {row["kind"] for row in summary["not_evaluated"]},
            {"branch_punishment", "branch_group_dayun_x_flow"})
        self.assertFalse([r for r in built["combined"]["structural_relations"]
                          if "punishment" in r["kind"]])

    def test_xiyong_pattern_v2_pin_accepted(self):
        # C1 已接通：喜用引擎接受格局 v2 输出（有资格门控与 combine()
        # 一致，useful_god 恒 None）；v1 变体则拒收。
        built = self._build("1958-08-15T19:30:00+08:00", 1988)
        pattern_system = built["xiyong"]["systems"]["pattern_yongshen"]
        self.assertEqual(pattern_system["status"], "presented")
        self.assertEqual(
            [e["pattern_key"] for e in pattern_system["eligible"]],
            ["pianyin"])
        self.assertEqual(
            [(e["pattern_key"], e["state"], e["pattern_god"])
             for e in pattern_system["eligible"]],
            [("pianyin", "candidate", "偏印")])
        self.assertTrue(all(e["useful_god"] is None
                            for e in pattern_system["eligible"]))
        # A1 后新期望：bijian/jiecai 常驻，结果数 12→14。
        self.assertEqual(pattern_system["counts"],
                         {"eligible": 1, "ineligible": 13, "total": 14})
        self.assertEqual(pattern_system["counts_by_state"],
                         {"candidate": 3, "not_judgeable": 11})
        self.assertIsNone(built["xiyong"]["unified_verdict"])
        v1 = dict(built["pattern"], variant="bazi-pattern-engine-v1")
        with self.assertRaises(ValueError):
            self.xiyong_fn(
                day_master="甲", month_branch="申",
                pillars=built["ganzhi"], strength=built["strength"],
                tiaohou=built["tiaohou"], bingyao=built["bingyao"],
                pattern=v1, flow_year=1988)


class ThreeLayerGroupTests(unittest.TestCase):
    """跨三层之组：只记同时含大运支与流年支之组（公开可跑）。"""

    def test_spanning_triple_harmony_case_b_1997(self):
        # B 盘：原局巳（时支）＋大运三酉＋流年丁丑＝巳酉丑三合金。
        output = combine(CASE_B_PILLARS, "戊", CASE_B_DAYUN, 1997)
        self.assertEqual(output["flow_year"]["ganzhi"], "丁丑")
        spanning = _relations(output, "dayun_x_flow_x_natal")
        self.assertEqual(len(spanning), 1)
        self.assertEqual(spanning[0]["kind"], "branch_triple_harmony")
        self.assertEqual(spanning[0]["detail"]["branches"],
                         ["巳", "酉", "丑"])
        self.assertEqual(
            spanning[0]["detail"]["traditional_result_element"], "金")
        self.assertEqual(spanning[0]["period_index"], 3)
        self.assertEqual(spanning[0]["effect"]["status"], "abstain")
        self.assertEqual(output["relation_summary"]["total"], 30)
        self.assertEqual(
            output["relation_summary"]["counts_by_scope"]
            ["dayun_x_flow_x_natal"], 1)

    def test_spanning_case_b_1997_with_fixtures(self):
        # 同盘带原局夹具：流年丁（正印）为已触发第二对的病神类，
        # 大运辛/庚为所论之神类、壬/癸为药神类；组关系本身仍 abstain。
        output = combine(CASE_B_PILLARS, "戊", CASE_B_DAYUN, 1997,
                         strength=_FIXTURES["B"]["strength"],
                         tiaohou=_FIXTURES["B"]["tiaohou"],
                         bingyao=_FIXTURES["B"]["bingyao"])
        self.assertEqual(output["relation_summary"]["total"], 30)
        effects = output["effects"]
        self.assertEqual(effects["verdict_counts"],
                         {"abstain": 8, "conditional": 22})
        mentions = {}
        for entry in effects["conditional_effects"]:
            for verdict in entry["verdicts"]:
                mentions[verdict] = mentions.get(verdict, 0) + 1
        self.assertEqual(mentions, {
            "stem_matches_bingyao_subject_god": 5,
            "stem_matches_natal_tiaohou_sequence": 7,
            "stem_matches_bingyao_medicine_god": 13,
            "stem_matches_bingyao_disease_god": 8})
        self.assertEqual(
            {c["relation_id"] for c in effects["conditional_effects"]},
            {"R001", "R002", "R004", "R005", "R007", "R009", "R010",
             "R011", "R012", "R014", "R015", "R016", "R017", "R019",
             "R020", "R021", "R023", "R024", "R025", "R027", "R028",
             "R029"})
        spanning = _relations(output, "dayun_x_flow_x_natal")
        self.assertEqual(len(spanning), 1)
        self.assertEqual(spanning[0]["effect"]["status"], "abstain")

    def test_no_spanning_group_in_batch1_cases(self):
        # 第一批两例均无跨三层之组：评估已执行，命中为 0，不是未评估。
        for output in (_combine_a(), _combine_b()):
            self.assertEqual(
                _relations(output, "dayun_x_flow_x_natal"), [])
            self.assertEqual(
                output["relation_summary"]["scope_coverage"]
                ["dayun_x_flow_x_natal"]["relations"], 0)


class Batch3ConditionalTests(unittest.TestCase):
    """第三批：病药角色/格局候选格神条件结论与结构层补齐（公开可跑）。"""

    def _verdict_mentions(self, output):
        mentions = {}
        for entry in output["effects"]["conditional_effects"]:
            for verdict in entry["verdicts"]:
                mentions[verdict] = mentions.get(verdict, 0) + 1
        return mentions

    def test_disease_role_via_flow_1984_case_a(self):
        # 流年 1984 甲子：流年干甲（比肩）为已触发第一对的病神类，
        # 4 条流年×原局天干关系与 3 条大运×流年天干关系（流年侧）
        # 得病神结论；大运辛药神类 5 条不变。
        output = combine(CASE_A_PILLARS, "甲", CASE_A_DAYUN, 1984,
                         strength=_FIXTURES["A"]["strength"],
                         tiaohou=_FIXTURES["A"]["tiaohou"],
                         bingyao=_FIXTURES["A"]["bingyao"])
        self.assertEqual(output["flow_year"]["ganzhi"], "甲子")
        self.assertEqual(output["relation_summary"]["total"], 24)
        self.assertEqual(output["effects"]["verdict_counts"],
                         {"abstain": 13, "conditional": 11})
        self.assertEqual(self._verdict_mentions(output), {
            "stem_matches_bingyao_medicine_god": 5,
            "stem_matches_bingyao_disease_god": 7})
        disease = [c for e in output["effects"]["conditional_effects"]
                   for c in e["conclusions"]
                   if c["verdict"] == "stem_matches_bingyao_disease_god"]
        self.assertEqual(len(disease), 7)
        self.assertTrue(all(c["pair_id"] == "wealth_peer_officer"
                            and c["role"] == "disease" for c in disease))
        self.assertTrue(all("病在场不等于害已成" in c["reason"]
                            for c in disease))
        # 同干标识：流年甲与原局日/时甲同干。
        same = [r for r in output["structural_relations"]
                if r["kind"] == "stem_five_element"
                and r["detail"]["same_stem"]]
        self.assertEqual({r["detail"]["stems"][0] for r in same}, {"甲"})
        self.assertTrue(all(r["detail"]["stems"] == ["甲", "甲"]
                            for r in same))

    def test_branch_element_facts_case_a(self):
        output = _combine_a()
        # 地支行一律带本气五行与方向事实；午未合保留有争议的原文。
        for relation in output["structural_relations"]:
            if relation["kind"].startswith("branch_") \
                    and relation["kind"] not in (
                        "branch_triple_harmony",
                        "branch_directional_meeting"):
                detail = relation["detail"]
                self.assertEqual(
                    [BRANCH_ELEMENTS[b] for b in detail["branches"]],
                    detail["elements"])
                self.assertIn(detail["direction_from_a_to_b"],
                              ("same", "generates", "generated_by",
                               "controls", "controlled_by"))
                self.assertEqual(
                    detail["same_branch"],
                    detail["branches"][0] == detail["branches"][1])
        harmony = _relations(output, "dayun_x_flow",
                             "branch_six_harmony", 1)[0]
        self.assertEqual(harmony["detail"]["branches"], ["酉", "辰"])
        self.assertEqual(harmony["detail"]["elements"], ["金", "土"])
        self.assertEqual(harmony["detail"]["direction_from_a_to_b"],
                         "generated_by")  # 土生金：辰土生酉金。
        self.assertEqual(harmony["detail"]["traditional_result_element"],
                         "金")

    def test_scope_coverage_hit_counts_case_a(self):
        output = _combine_a()
        coverage = output["relation_summary"]["scope_coverage"]
        self.assertEqual(coverage["dayun_x_natal"], {
            "stem_pairs_enumerated": 12,
            "branch_pairs_enumerated": 12,
            "group_evaluated": True,
            "group_branches": "natal_four_plus_dayun",
            "relations": 17,
            "branch_pairs_with_reviewed_relation": 3,
            "branch_pairs_without_reviewed_relation": 9})
        self.assertEqual(coverage["flow_x_natal"], {
            "stem_pairs_enumerated": 4,
            "branch_pairs_enumerated": 4,
            "group_evaluated": True,
            "group_branches": "natal_four_plus_flow",
            "relations": 7,
            "branch_pairs_with_reviewed_relation": 2,
            "branch_pairs_without_reviewed_relation": 2})
        self.assertEqual(coverage["dayun_x_flow"], {
            "stem_pairs_enumerated": 3,
            "branch_pairs_enumerated": 3,
            "group_evaluated": True,
            "group_branches":
                "dayun_plus_flow_only_two_branches_no_group_formable",
            "relations": 6,
            "branch_pairs_with_reviewed_relation": 2,
            "branch_pairs_without_reviewed_relation": 1})
        self.assertEqual(coverage["dayun_x_flow_x_natal"], {
            "stem_pairs_enumerated": 0,
            "branch_pairs_enumerated": 0,
            "group_evaluated": True,
            "group_branches":
                "natal_four_plus_dayun_plus_flow_spanning_only",
            "relations": 0,
            "branch_pairs_with_reviewed_relation": 0,
            "branch_pairs_without_reviewed_relation": 0})

    def test_pattern_candidate_god_minimal_inputs(self):
        # 最小输入＋正印候选格（validated 资源规则）：大运癸（正印）
        # 7 条天干关系得候选格神结论；无 validated 规则的正官候选
        # 不产生结论；非十神格名（从财格）亦不产生结论。
        helper = NewInputFailClosedTests(
            "test_minimal_new_inputs_are_consumed")
        pattern = helper._pattern_v2()
        pattern["results"]["zhengyin"] = {
            "pattern": "正印", "pattern_key": "zhengyin",
            "state": "candidate", "evidence": [], "limitations": [],
            "rule_ids": ["bazi.phase2.resource_pattern_candidates"]}
        pattern["results"]["zhengguan"] = {
            "pattern": "正官", "pattern_key": "zhengguan",
            "state": "candidate", "evidence": [], "limitations": [],
            "rule_ids": []}
        pattern["results"]["cong"] = {
            "pattern": "从财格", "pattern_key": "cong",
            "state": "candidate", "evidence": [], "limitations": [],
            "rule_ids": ["bazi.phase2.official_pattern_candidates"]}
        output = combine(CASE_A_PILLARS, "甲", CASE_A_DAYUN, 1988,
                         strength=helper._assessment(),
                         pattern=pattern, xiyong=helper._xiyong())
        self.assertEqual(output["effects"]["verdict_counts"],
                         {"abstain": 16, "conditional": 14})
        self.assertEqual(self._verdict_mentions(output), {
            "model_treatment_recorded_only": 7,
            "stem_matches_pattern_candidate_god": 7})
        candidate = [c for e in output["effects"]["conditional_effects"]
                     for c in e["conclusions"]
                     if c["verdict"]
                     == "stem_matches_pattern_candidate_god"]
        self.assertEqual(len(candidate), 7)
        self.assertTrue(all(c["pattern_key"] == "zhengyin"
                            and c["pattern"] == "正印"
                            and c["pattern_god"] == "正印"
                            for c in candidate))
        self.assertTrue(all("候选恒不等于成立" in c["reason"]
                            for c in candidate))
        self.assertTrue(all(
            c["basis"]["rule_ids"]
            == ["bazi.phase2.resource_pattern_candidates"]
            for c in candidate))

    def test_bingyao_drift_is_rejected(self):
        helper = NewInputFailClosedTests(
            "test_minimal_new_inputs_are_consumed")
        # 病药对带已裁定的药效，一律拒收（结论以效力恒未裁定为前提）。
        drifted = json.loads(json.dumps(_FIXTURES["A"]["bingyao"]))
        drifted["pairs"][0]["medicine_effect_status"] = "cured"
        with self.assertRaises(ValueError):
            _combine_a(bingyao=drifted)
        # 角色类含未知十神，一律拒收。
        drifted = json.loads(json.dumps(_FIXTURES["A"]["bingyao"]))
        drifted["pairs"][0]["rule"]["medicine_gods"] = ["正官", "天医"]
        with self.assertRaises(ValueError):
            _combine_a(bingyao=drifted)
        # 喜用引擎路径的病药体系形态漂移亦拒收。
        xiyong = helper._xiyong()
        xiyong["systems"]["bingyao"] = {
            "system": "bingyao", "status": "presented",
            "pairs": [{"pair_id": "wealth_peer_officer",
                       "status": "triggered",
                       "subject_gods": ["正财", "偏财"],
                       "disease_gods": ["比肩", "劫财"],
                       "medicine_gods": ["正官", "天医"],
                       "medicine_status": "candidate_present",
                       "medicine_effect_status": "unadjudicated",
                       "rule_id": "shenfeng.wealth_peer_officer"}]}
        with self.assertRaises(ValueError):
            combine(CASE_A_PILLARS, "甲", CASE_A_DAYUN, 1988,
                    strength=helper._assessment(),
                    pattern=helper._pattern_v2(), xiyong=xiyong)

    def test_bingyao_pair_shapes_are_equivalent(self):
        # 病药角色类三种写法同值：列表（夹具 JSON 形）、元组（原生
        # bingyao_lookup 规则常量形——机上实测 2026-11-25，未修前
        # _bingyao_god_list 只认 list 而拒收）、字典块（对级
        # subject/disease_candidate/medicine_candidate，
        # {god_class, gods}）。三种写法对同一盘须产出同一病药结论；
        # 字典块以 god_class 定类，gods 行只作交叉核对。
        def _bingyao_conclusions(output):
            return sorted(
                (e["relation_id"], c["verdict"], c["stem"],
                 c["ten_god"], c["pair_id"], c["role"])
                for e in output["effects"]["conditional_effects"]
                for c in e["conclusions"]
                if c["verdict"].startswith("stem_matches_bingyao_"))

        baseline = _combine_a()
        base_counts = baseline["effects"]["verdict_counts"]
        base_conclusions = _bingyao_conclusions(baseline)
        self.assertTrue(base_conclusions)

        tuple_shaped = json.loads(json.dumps(_FIXTURES["A"]["bingyao"]))
        for pair in tuple_shaped["pairs"]:
            rule = pair["rule"]
            for key in ("subject_gods", "disease_gods", "medicine_gods"):
                rule[key] = tuple(rule[key])
        out_tuple = _combine_a(bingyao=tuple_shaped)
        self.assertEqual(out_tuple["effects"]["verdict_counts"],
                         base_counts)
        self.assertEqual(_bingyao_conclusions(out_tuple),
                         base_conclusions)

        dict_shaped = json.loads(json.dumps(_FIXTURES["A"]["bingyao"]))
        for pair in dict_shaped["pairs"]:
            rule = pair["rule"]
            for key in ("subject_gods", "disease_gods", "medicine_gods"):
                del rule[key]
        out_dict = _combine_a(bingyao=dict_shaped)
        self.assertEqual(out_dict["effects"]["verdict_counts"],
                         base_counts)
        self.assertEqual(_bingyao_conclusions(out_dict),
                         base_conclusions)

        # 字典块所载之神不在其类中，一律拒收。
        bad_dict = json.loads(json.dumps(dict_shaped))
        bad_dict["pairs"][0]["subject"]["gods"][0]["ten_god"] = "比肩"
        with self.assertRaises(ValueError):
            _combine_a(bingyao=bad_dict)
        # 字典形且药不在盘时药类不可知（无类表、无药候选块），拒收
        # 而非拟制药类：B 盘已触发对 medicine_candidate 为 None。
        dict_b = json.loads(json.dumps(_FIXTURES["B"]["bingyao"]))
        for pair in dict_b["pairs"]:
            rule = pair["rule"]
            for key in ("subject_gods", "disease_gods", "medicine_gods"):
                del rule[key]
        with self.assertRaises(ValueError):
            _combine_b(bingyao=dict_b)

    def test_limitations_record_batch3_blockers(self):
        output = _combine_a()
        text = "\n".join(output["limitations"])
        for marker in ("C2", "C3", "C4", "C5", "C6",
                       "已批为研究模型", "已批保留",
                       "overall_effect 恒为 None"):
            self.assertIn(marker, text)
        self.assertNotIn("proposed_pending_adjudication", text)
        self.assertIsNone(output["effects"]["overall_effect"])

    def test_c6_abstention_propagates_to_model_treatment(self):
        # C6：现代旺衰弃判（components 为 None）时，Q3-A 模型口径结论
        # 不发；无其他引用时效力层全 abstain。
        helper = NewInputFailClosedTests(
            "test_minimal_new_inputs_are_consumed")
        assessment = helper._assessment()
        assessment["modern"] = dict(
            assessment["modern"], verdict="abstain", score=None,
            classification_status="abstain",
            definite_classification=None,
            abstain_reason="transformation_candidate_unresolved",
            components=None, cong_candidates=None,
            interaction_effects=None)
        output = combine(CASE_A_PILLARS, "甲", CASE_A_DAYUN, 1988,
                         strength=assessment,
                         pattern=helper._pattern_v2(),
                         xiyong=helper._xiyong())
        self.assertEqual(output["strength"]["modern"]["verdict"], "abstain")
        self.assertIsNone(output["strength"]["modern"]["components"])
        self.assertEqual(output["effects"]["verdict_counts"],
                         {"abstain": 30})
        self.assertTrue(output["effects"]["all_abstained"])
        self.assertEqual(output["effects"]["conditional_effects"], [])
        self.assertIsNone(output["effects"]["overall_effect"])

    def test_c5_spanning_groups_are_not_double_counted(self):
        # C5：跨层组与两对 scope 的组无重叠，组关系本身不产生条件结论，
        # 不将重复结构关系计为多份独立作用。
        output = combine(CASE_B_PILLARS, "戊", CASE_B_DAYUN, 1997,
                         strength=_FIXTURES["B"]["strength"],
                         tiaohou=_FIXTURES["B"]["tiaohou"],
                         bingyao=_FIXTURES["B"]["bingyao"])
        groups = [r for r in output["structural_relations"]
                  if r["kind"] in ("branch_triple_harmony",
                                   "branch_directional_meeting")]
        branch_sets = [tuple(sorted(r["detail"]["branches"]))
                       for r in groups]
        self.assertEqual(len(branch_sets), len(set(branch_sets)))
        spanning = _relations(output, "dayun_x_flow_x_natal")
        self.assertEqual(len(spanning), 1)
        self.assertEqual(spanning[0]["detail"]["branches"],
                         ["巳", "酉", "丑"])
        self.assertNotIn(
            tuple(sorted(spanning[0]["detail"]["branches"])),
            [tuple(sorted(r["detail"]["branches"]))
             for r in groups if r["scope"] != "dayun_x_flow_x_natal"])
        self.assertEqual(spanning[0]["effect"]["status"], "abstain")
        self.assertFalse([
            e for e in output["effects"]["conditional_effects"]
            if e["scope"] == "dayun_x_flow_x_natal"])


class NewInputFailClosedTests(unittest.TestCase):
    """新形态输入漂移一律拒收（公开可跑，手造最小漂移输入）。"""

    def _assessment(self, **overrides):
        base = {
            "variant": "bazi-strength-engine-v1",
            "day_master": "甲", "month_branch": "申",
            "research_only": True, "public_enabled": False,
            "ai_enabled": False,
            "classical": {"classification": "indeterminate",
                          "matched_predicate": None, "blockers": []},
            "modern": {"model_id": "strength_model_modern_v1",
                       "model_kind": "modern_engineering",
                       "verdict": "weak", "score": -21,
                       "classification_status": "definite",
                       "definite_classification": "weak",
                       "uncertainty_flags": [],
                       "abstain_reason": None,
                       "components": {}, "cong_candidates": None,
                       "interaction_effects": None},
            "agreement": {"classical": "indeterminate",
                          "modern": "weak",
                          "relationship": "classical_indeterminate",
                          "note": ""},
        }
        base.update(overrides)
        return base

    def _pattern_v2(self, **overrides):
        base = {
            "variant": "bazi-pattern-engine-v2",
            "day_stem": "甲", "month_branch": "申",
            "research_only": True, "public": False, "ai": False,
            "results": {
                "zhengguan": {"pattern": "正官", "pattern_key": "zhengguan",
                              "state": "candidate", "evidence": [],
                              "limitations": [], "rule_ids": []},
            },
        }
        base.update(overrides)
        return base

    def _xiyong(self, **overrides):
        base = {
            "variant": "bazi-xiyong-engine-v1",
            "day_master": "甲", "month_branch": "申",
            "research_only": True, "public_enabled": False,
            "ai_enabled": False,
            "systems": {
                "fuyi": {"system": "fuyi", "status": "not_provided"},
                "tiaohou": {"system": "tiaohou",
                            "status": "not_provided"},
                "bingyao": {"system": "bingyao",
                            "status": "not_provided"},
                "pattern_yongshen": {"system": "pattern_yongshen",
                                     "status": "not_provided"},
            },
            "annual_xiyong": {
                "variant": "bazi-xiyong-annual-contract-v1",
                "status": "contract_only_pending_rules",
                "implemented": [
                    "flow_year_ganzhi_and_ten_god",
                    "flow_stem_presence_against_natal_tiaohou_sequence",
                    "flow_stem_ten_god_role_against_bingyao_pairs",
                    "rule_call_structure",
                    "flow_stem_presence_against_fuyi_modern_candidates",
                    "flow_stem_presence_against_pattern_basis",
                ],
                "pending": [
                    "annual_tiaohou_derivation",
                    "annual_bingyao_derivation",
                    "annual_fuyi_derivation",
                    "annual_pattern_yongshen_derivation",
                    "unified_annual_verdict",
                ],
                "derivation": None, "unified_verdict": None,
            },
            "unified_verdict": None,
        }
        base.update(overrides)
        return base

    def test_strength_variant_drift_rejected(self):
        with self.assertRaises(ValueError):
            combine(CASE_A_PILLARS, "甲", CASE_A_DAYUN, 1988,
                    strength=self._assessment(
                        variant="bazi-strength-engine-v9"))
        with self.assertRaises(ValueError):
            combine(CASE_A_PILLARS, "甲", CASE_A_DAYUN, 1988,
                    strength=self._assessment(day_master="乙"))
        with self.assertRaises(ValueError):
            combine(CASE_A_PILLARS, "甲", CASE_A_DAYUN, 1988,
                    strength={"variant": "unknown",
                              "factor_variant": "unknown"})

    def test_pattern_broken_state_rejected(self):
        # 第三批集成：broken 只认伤官见官一途；正官格破格无已审通道，
        # 仍拒收（合法的伤官破格见 test_tj0424_broken_integration）。
        broken = self._pattern_v2()
        broken["results"]["zhengguan"]["state"] = "broken"
        with self.assertRaises(ValueError):
            combine(CASE_A_PILLARS, "甲", CASE_A_DAYUN, 1988,
                    pattern=broken)
        with self.assertRaises(ValueError):
            combine(CASE_A_PILLARS, "甲", CASE_A_DAYUN, 1988,
                    pattern=self._pattern_v2(
                        variant="bazi-pattern-engine-v1"))

    def test_xiyong_drift_rejected(self):
        with self.assertRaises(ValueError):
            combine(CASE_A_PILLARS, "甲", CASE_A_DAYUN, 1988,
                    xiyong=self._xiyong(
                        variant="bazi-xiyong-engine-v9"))
        with self.assertRaises(ValueError):
            combine(CASE_A_PILLARS, "甲", CASE_A_DAYUN, 1988,
                    xiyong=self._xiyong(unified_verdict="甲"))
        annual = self._xiyong()
        annual["annual_xiyong"] = dict(
            annual["annual_xiyong"],
            implemented=["flow_year_ganzhi_and_ten_god"])
        with self.assertRaises(ValueError):
            combine(CASE_A_PILLARS, "甲", CASE_A_DAYUN, 1988,
                    xiyong=annual)
        annual = self._xiyong()
        annual["annual_xiyong"] = dict(
            annual["annual_xiyong"], pending=[])
        with self.assertRaises(ValueError):
            combine(CASE_A_PILLARS, "甲", CASE_A_DAYUN, 1988,
                    xiyong=annual)

    def test_minimal_new_inputs_are_consumed(self):
        output = combine(CASE_A_PILLARS, "甲", CASE_A_DAYUN, 1988,
                         strength=self._assessment(),
                         pattern=self._pattern_v2(),
                         xiyong=self._xiyong())
        self.assertEqual(output["strength"]["modern"]["verdict"], "weak")
        self.assertEqual(output["strength"]["modern"]["score"], -21)
        self.assertEqual(output["pattern"]["counts"], {"candidate": 1})
        self.assertEqual(output["xiyong"]["variant"],
                         "bazi-xiyong-engine-v1")
        self.assertIsNone(output["xiyong"]["unified_verdict"])
        # 最小输入无调候/扶抑候选/成立格：Q3-A 仍使冲害合得条件结论。
        self.assertEqual(output["effects"]["verdict_counts"],
                         {"abstain": 23, "conditional": 7})


if __name__ == "__main__":
    unittest.main()
