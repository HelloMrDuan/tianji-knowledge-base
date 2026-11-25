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
"""
import json
import unittest

from tianji_kb.bazi_combination_engine import (
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
                self.assertIsNone(relation["effect"]["verdict"])
                self.assertEqual(relation["effect"]["status"], "abstain")
                self.assertTrue(relation["effect"]["reason"])
                statuses = {c["status"] for c in relation["conditions"]}
                self.assertIn("satisfied", statuses)
                self.assertIn("cannot_judge", statuses)
                self.assertTrue(all(c["rule_ids"]
                                    for c in relation["conditions"]))
        effects = output["effects"]
        self.assertIsNone(effects["overall_effect"])
        self.assertTrue(effects["all_abstained"])
        self.assertEqual(effects["abstain_count"], 30)
        self.assertEqual(effects["verdict_counts"], {"abstain": 30})
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
            self.assertEqual(relation["effect"]["status"], "abstain")
            self.assertIsNone(relation["effect"]["verdict"])


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
        # 且组合效力层仍全部 abstain——存在药候选不等于药已去病。
        output = _combine_a()
        pairs = output["xiyong"]["systems"]["bingyao"]["pairs"]
        self.assertEqual(pairs[0]["medicine_status"], "candidate_present")
        self.assertEqual(pairs[0]["medicine_effect_status"], "unadjudicated")
        self.assertTrue(all(r["effect"]["status"] == "abstain"
                            for r in output["structural_relations"]))

    def test_ganzhi_string_pillars_agree_with_structured_pillars(self):
        structured = _combine_a()
        plain = combine(["戊戌", "庚申", "甲子", "甲戌"], "甲",
                        CASE_A_DAYUN, 1988)
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
        self.assertTrue(all(r["effect"]["status"] == "abstain"
                            for r in output["structural_relations"]))


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


if __name__ == "__main__":
    unittest.main()
