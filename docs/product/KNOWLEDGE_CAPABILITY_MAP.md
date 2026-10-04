# 产品知识能力图

范围按已实现的 Scenario 与确定性引擎区分。结构事实可用不等于完整预测、前台发布或 AI 校准完成。所有条目由现有注册项派生，不另建知识模型。

## 八字详批 · PRODUCTIZABLE

Scenario：`bazi-profile`；已执行=True；现有结构公开标志=True；AI=false。

已有知识、Rule 与 Evidence：

- 八字基础与十神映射：Terms `bazi.term.day_master`, `bazi.term.ten_gods`, `bazi.term.hidden_stems`, `bazi.term.month_command`, `bazi.term.root_candidates`, `bazi.term.hidden_to_visible`, `bazi.term.heavenly_stems`, `bazi.term.stem_polarity`, `bazi.term.five_elements`, `bazi.term.generation_control`；Phase1 Rule `bazi.rule.r001`, `bazi.rule.r002`, `bazi.rule.r003`, `bazi.rule.r011`, `bazi.rule.r012`, `bazi.rule.r013`, `bazi.rule.r014`, `bazi.rule.r015`, `bazi.rule.r016`。
- 十神结构与条件解释：Terms `bazi.term.ten_gods`, `bazi.term.hidden_to_visible`；Phase1 Rule `bazi.rule.r002`, `bazi.rule.r003`, `bazi.rule.r011`, `bazi.rule.r012`, `bazi.rule.r015`。
- 旺衰及流派边界：Terms `bazi.term.strength_review_boundary`, `bazi.term.month_command`, `bazi.term.root_candidates`, `bazi.term.hidden_to_visible`；Phase1 Rule `bazi.rule.r012`, `bazi.rule.r013`, `bazi.rule.r014`, `bazi.rule.r015`。
- 格局：Terms 尚无对应审核术语；Phase1 Rule 尚无对应审核规则。
- 喜用神分体系治理：Terms 尚无对应审核术语；Phase1 Rule 尚无对应审核规则。
- 大运：Terms 尚无对应审核术语；Phase1 Rule 尚无对应审核规则。
- 流年与岁运作用：Terms `bazi.term.branch_triple_harmonies`；Phase1 Rule `bazi.rule.r010`。

已有 Phase2 / Golden / Variant：

- `bazi.phase2.pillars` / `ziping-structural-v1`；Golden：`bazi.structural-basic`；测试 `tests/test_phase2_bazi.py`。
  Evidence C：`bazi.source.yuanhai` / 渊海子平 / 喜忌篇 / `《渊海子平》喜忌篇；本轮固定短引`，引文：四柱排定,三才次分,专以日上天元,配合八字支干;有见不见之形,无时不有;神煞相绊,轻重较量。。
- `bazi.phase2.ten_gods` / `ziping-structural-v1`；Golden：`bazi.structural-basic`；测试 `tests/test_phase2_bazi.py`。
  Evidence C：`bazi.source.yuanhai` / 渊海子平 / 基础与藏遁 / `《渊海子平》基础；本轮固定短引`，引文：以甲为例★见甲:为比肩、兄弟。
 见乙:为劫财、败财,剋父及妻。
 见丙:为食神、天厨、寿星,为男。
 见丁:为伤官、退财、耗气,子甥。
 见戊:为偏财、偏妻、偏妾,剋子。
 见己:为正财、正妻,剋母,为合神。
 见庚:为偏官、七杀、官鬼、将星。
 见辛:为正官、禄马、荣神,父母。
 见壬:为倒食、偏印、梟神,剋女。
 见癸:为印綬、正人、君子,产业。。
  Evidence C：`bazi.source.yuanhai` / 渊海子平 / 基础与藏遁 / `《渊海子平》基础；本轮固定短引`，引文：以乙为例★见甲:为劫财、逐马,剋妻。
 见乙:为比肩、兄弟、朋友。
 见丙:为伤官、小人、盗气,为姪。
 见丁:为食神、天厨、寿星,子孙。
 见戊:为正财、正妻,剋母。
 见己:为偏财、偏妻、偏妾,剋子。
 见庚:为正官、禄马,剋父母。
 见辛:为偏官、七杀、官鬼,媒人。
 见壬:为印綬、正人、君子,忌杀。
 见癸:为倒食、偏印、梟神,剋母。。
  Evidence C：`bazi.source.yuanhai` / 渊海子平 / 十神关系选段 / `《渊海子平》论伤官；本轮固定短引`，引文：又云,伤官者,我生彼之谓也;以阳见阴,阴见阳,亦名盗气。。
  Evidence C：`bazi.source.yuanhai` / 渊海子平 / 十神关系选段 / `《渊海子平》论正财；本轮固定短引`，引文：何谓之正财?犹如正官之意;是阴见阳财,阳见阴财。。
  Evidence C：`bazi.source.yuanhai` / 渊海子平 / 十神关系选段 / `《渊海子平》正官论；本轮固定短引`，引文：夫正官者,甲见辛之类;乃阴见阳为官,阳见阴为鬼,阴阳配合成其道也。。
  Evidence C：`bazi.source.yuanhai` / 渊海子平 / 十神关系选段 / `《渊海子平》论印绶；本轮固定短引`，引文：夫印綬者,生我之谓也,亦名生气。以阳见阴,以阴见阳,谓之正印;阳见阳,阴见阴,谓之偏印。。
- `bazi.phase2.hidden_stems` / `ziping-structural-v1`；Golden：`bazi.structural-basic`；测试 `tests/test_phase2_bazi.py`。
  Evidence C：`bazi.source.yuanhai` / 渊海子平 / 基础与藏遁 / `《渊海子平》又地支藏遁歌；本轮固定短引`，引文：子宫癸水在其中,丑癸辛金己土同;寅宫甲木兼丙戊,卯宫乙木独相逢。辰藏乙戊三分癸,巳中庚金丙戊丛;午宫丁火并己土,未宫乙己丁共宗。申位庚金壬水戊,酉宫辛金独丰隆;戌宫辛金及丁戊,亥藏壬甲是真踪。。
- `bazi.phase2.month_command_factors` / `ziping-structural-v1`；Golden：`bazi.factors-normal`, `bazi.factors-tomb-boundary`, `bazi.factors-many-stems-no-root`, `bazi.factors-few-stems-with-root`, `bazi.factors-clash-not-erasure`, `bazi.factors-siling-unresolved`；测试 `tests/test_phase2_bazistrength.py`。
  Evidence C：`bazi.source.ditiansui-spouse` / 滴天髓阐微 / 月令、通根与透藏观察边界 / `《滴天髓阐微》通神论·月令；固定原文字符位置 37963；月令提纲`，引文：月令乃提纲之府,譬之宅也,人元为用事之神,宅之定向也,不可以不卜。。
  Evidence C：`bazi.source.ditiansui-spouse` / 滴天髓阐微 / 月令、通根与透藏观察边界 / `《滴天髓阐微》通神论·月令；固定原文字符位置 38056；寅月司令分日`，引文：如寅月生人,立春后七日前,皆值戊土用事;八日后十四日前者,丙火用事 ;十五日后,甲木用事。。
  Evidence C：`bazi.source.ditiansui-spouse` / 滴天髓阐微 / 月令、通根与透藏观察边界 / `《滴天髓阐微》通神论·衰旺；固定原文字符位置 39648；不可得令即旺失令即弱`，引文：得时俱为旺论,失令便作衰看,虽是至理,亦死法也。。
  Evidence C：`bazi.source.yuanhai` / 渊海子平 / 基础与藏遁 / `《渊海子平》又地支藏遁歌；本轮固定短引`，引文：子宫癸水在其中,丑癸辛金己土同;寅宫甲木兼丙戊,卯宫乙木独相逢。辰藏乙戊三分癸,巳中庚金丙戊丛;午宫丁火并己土,未宫乙己丁共宗。申位庚金壬水戊,酉宫辛金独丰隆;戌宫辛金及丁戊,亥藏壬甲是真踪。。
- `bazi.phase2.root_candidates` / `ziping-structural-v1`；Golden：`bazi.factors-normal`, `bazi.factors-tomb-boundary`, `bazi.factors-many-stems-no-root`, `bazi.factors-few-stems-with-root`, `bazi.factors-clash-not-erasure`, `bazi.factors-siling-unresolved`；测试 `tests/test_phase2_bazistrength.py`。
  Evidence C：`bazi.source.ditiansui-spouse` / 滴天髓阐微 / 月令、通根与透藏观察边界 / `《滴天髓阐微》通神论·衰旺；固定原文字符位置 39989；比肩与地支根不可数量等同`，引文：天干得一比肩,不如地支得一余气墓库。。
  Evidence C：`bazi.source.ditiansui-spouse` / 滴天髓阐微 / 月令、通根与透藏观察边界 / `《滴天髓阐微》通神论·衰旺；固定原文字符位置 40063；余气与长生禄旺根示例`，引文：余气者,如丙丁逢未,甲乙逢辰,庚辛逢戌,壬癸逢丑之类是也,得二比肩,不如支中得一长生禄旺,如甲乙逢亥寅卯之类是也。。
  Evidence C：`bazi.source.ditiansui-spouse` / 滴天髓阐微 / 月令、通根与透藏观察边界 / `《滴天髓阐微》通神论·衰旺；固定原文字符位置 39648；不可得令即旺失令即弱`，引文：得时俱为旺论,失令便作衰看,虽是至理,亦死法也。。
  Evidence C：`bazi.source.yuanhai` / 渊海子平 / 基础与藏遁 / `《渊海子平》又地支藏遁歌；本轮固定短引`，引文：子宫癸水在其中,丑癸辛金己土同;寅宫甲木兼丙戊,卯宫乙木独相逢。辰藏乙戊三分癸,巳中庚金丙戊丛;午宫丁火并己土,未宫乙己丁共宗。申位庚金壬水戊,酉宫辛金独丰隆;戌宫辛金及丁戊,亥藏壬甲是真踪。。
- `bazi.phase2.hidden_to_visible` / `ziping-structural-v1`；Golden：`bazi.factors-normal`, `bazi.factors-tomb-boundary`, `bazi.factors-many-stems-no-root`, `bazi.factors-few-stems-with-root`, `bazi.factors-clash-not-erasure`, `bazi.factors-siling-unresolved`；测试 `tests/test_phase2_bazistrength.py`。
  Evidence C：`bazi.source.ditiansui-spouse` / 滴天髓阐微 / 月令、通根与透藏观察边界 / `《滴天髓阐微》通神论·月令；固定原文字符位置 38284；藏干与显干引助`，引文：故知地支人元必得天干引助,天干为用,必要地支司令。。
  Evidence C：`bazi.source.yuanhai` / 渊海子平 / 基础与藏遁 / `《渊海子平》又地支藏遁歌；本轮固定短引`，引文：子宫癸水在其中,丑癸辛金己土同;寅宫甲木兼丙戊,卯宫乙木独相逢。辰藏乙戊三分癸,巳中庚金丙戊丛;午宫丁火并己土,未宫乙己丁共宗。申位庚金壬水戊,酉宫辛金独丰隆;戌宫辛金及丁戊,亥藏壬甲是真踪。。
- `bazi.phase2.support_relations` / `ziping-structural-v1`；Golden：`bazi.support-normal`, `bazi.support-yin`, `bazi.support-visible-peers`, `bazi.support-conflict`；测试 `tests/test_phase2_bazisupport.py`。
  Evidence C：`bazi.source.yuanhai` / 渊海子平 / 生克关系与效力界限 / `《渊海子平》五行相生及条件界限；固定原文字符位置 964`，引文：金能生水,水多金沉;水能生木,木盛水缩;木能生火,火多木焚;火能生土,土多火埋;土能生金,金多土变。。
  Evidence C：`bazi.source.yuanhai` / 渊海子平 / 生克关系与效力界限 / `《渊海子平》五行相克及条件界限；固定原文字符位置 1016`，引文：金能剋木,木坚金缺;木能剋土,土重木折;土能剋水,水多土流;水能剋火,火多水热;火能剋金,金多火熄。。
  Evidence C：`bazi.source.ditiansui-spouse` / 滴天髓阐微 / 天干阴阳五行分类 / `《滴天髓阐微·审核短引》十干阴阳短引；固定原文字符位置 4991`，引文：甲、丙、戊、庚、壬为阳,独丙火秉阳之精,而为阳中之阳;乙、丁、己、辛、癸为阴,独癸水秉阴之精,而为阴中之阴。。
  Evidence C：`bazi.source.ditiansui-spouse` / 滴天髓阐微 / 天干阴阳五行分类 / `《滴天髓阐微·审核短引》十干五行短引；固定原文字符位置 5159`，引文：甲乙一木也,丙丁一火也,戊己一土也,庚辛一金也,壬癸一水也,即分别所用,不过阳刚阴柔,阳健阴顺而已。。
  Evidence C：`bazi.source.yuanhai` / 渊海子平 / 基础与藏遁 / `《渊海子平》基础；本轮固定短引`，引文：以甲为例★见甲:为比肩、兄弟。
 见乙:为劫财、败财,剋父及妻。
 见丙:为食神、天厨、寿星,为男。
 见丁:为伤官、退财、耗气,子甥。
 见戊:为偏财、偏妻、偏妾,剋子。
 见己:为正财、正妻,剋母,为合神。
 见庚:为偏官、七杀、官鬼、将星。
 见辛:为正官、禄马、荣神,父母。
 见壬:为倒食、偏印、梟神,剋女。
 见癸:为印綬、正人、君子,产业。。
  Evidence C：`bazi.source.yuanhai` / 渊海子平 / 基础与藏遁 / `《渊海子平》基础；本轮固定短引`，引文：以乙为例★见甲:为劫财、逐马,剋妻。
 见乙:为比肩、兄弟、朋友。
 见丙:为伤官、小人、盗气,为姪。
 见丁:为食神、天厨、寿星,子孙。
 见戊:为正财、正妻,剋母。
 见己:为偏财、偏妻、偏妾,剋子。
 见庚:为正官、禄马,剋父母。
 见辛:为偏官、七杀、官鬼,媒人。
 见壬:为印綬、正人、君子,忌杀。
 见癸:为倒食、偏印、梟神,剋母。。
  Evidence C：`bazi.source.yuanhai` / 渊海子平 / 十神关系选段 / `《渊海子平》论伤官；本轮固定短引`，引文：又云,伤官者,我生彼之谓也;以阳见阴,阴见阳,亦名盗气。。
  Evidence C：`bazi.source.yuanhai` / 渊海子平 / 十神关系选段 / `《渊海子平》论正财；本轮固定短引`，引文：何谓之正财?犹如正官之意;是阴见阳财,阳见阴财。。
  Evidence C：`bazi.source.yuanhai` / 渊海子平 / 十神关系选段 / `《渊海子平》正官论；本轮固定短引`，引文：夫正官者,甲见辛之类;乃阴见阳为官,阳见阴为鬼,阴阳配合成其道也。。
  Evidence C：`bazi.source.yuanhai` / 渊海子平 / 十神关系选段 / `《渊海子平》论印绶；本轮固定短引`，引文：夫印綬者,生我之谓也,亦名生气。以阳见阴,以阴见阳,谓之正印;阳见阳,阴见阴,谓之偏印。。
  Evidence C：`bazi.source.yuanhai` / 渊海子平 / 基础与藏遁 / `《渊海子平》又地支藏遁歌；本轮固定短引`，引文：子宫癸水在其中,丑癸辛金己土同;寅宫甲木兼丙戊,卯宫乙木独相逢。辰藏乙戊三分癸,巳中庚金丙戊丛;午宫丁火并己土,未宫乙己丁共宗。申位庚金壬水戊,酉宫辛金独丰隆;戌宫辛金及丁戊,亥藏壬甲是真踪。。

当前场景可输出结论（只描述事实，不追加吉凶含义）：

- `bazi.pillars`：READY；匹配 `bazi.phase2.pillars`，事实路径 `/ganzhi`；deterministic_structure_only。
- `bazi.day_master`：READY；匹配 `bazi.phase2.pillars`，事实路径 `/day_master`；deterministic_structure_only。
- `bazi.ten_gods`：READY；匹配 `bazi.phase2.ten_gods`，事实路径 `/`；deterministic_structure_only。
- `bazi.hidden_stems`：READY；匹配 `bazi.phase2.hidden_stems`，事实路径 `/`；deterministic_structure_only。
- `bazi.month_command_factors`：READY；匹配 `bazi.phase2.month_command_factors`，事实路径 `/`；deterministic_structure_only。
- `bazi.root_candidates`：READY；匹配 `bazi.phase2.root_candidates`，事实路径 `/`；deterministic_structure_only。
- `bazi.hidden_to_visible`：READY；匹配 `bazi.phase2.hidden_to_visible`，事实路径 `/`；deterministic_structure_only。
- `bazi.support_relations`：READY；匹配 `bazi.phase2.support_relations`，事实路径 `/`；deterministic_structure_only。
  `bazi.month_command_factors` 仅在显式输入 `{"strength_variant": "ditiansui-root-visibility-v1"}` 且对应 RuleMatch 实际执行时可用。
  `bazi.root_candidates` 仅在显式输入 `{"strength_variant": "ditiansui-root-visibility-v1"}` 且对应 RuleMatch 实际执行时可用。
  `bazi.hidden_to_visible` 仅在显式输入 `{"strength_variant": "ditiansui-root-visibility-v1"}` 且对应 RuleMatch 实际执行时可用。
  `bazi.support_relations` 仅在显式输入 `{"strength_variant": "ditiansui-root-visibility-v1"}` 且对应 RuleMatch 实际执行时可用。

当前禁止结论：身强身弱；格局成立；具体喜用神；完整详批。

缺失能力 / 依赖 / 下一批：

- `bazi-foundation`：十干阴阳五行、生克方向及四柱/日主/十神/藏干已有审核短引、执行与 Golden；仍缺十二长生、季节实际效力及基础结构到个人结论的条件规则，真太阳时未实现；旧表权重不作通用结论。
  下一批从 `data/canonical/classics/bazi/ditiansui_chanwei_v1.json#/sections/0/text` 核短引、条件和反例；全文命中仅是待审定位，不是 Evidence。
- `bazi-ten-gods`：映射不等于组合、位置、透藏、月令条件下的解释；须补原典规则、限制及反例。
  下一批从 `data/canonical/classics/bazi/ditiansui_chanwei_v1.json#/sections/6/text` 核短引、条件和反例；全文命中仅是待审定位，不是 Evidence。
- `bazi-strength`：月令/通根候选/透藏/生克方向位置 v1 已按原模型执行，含正常/阴日干/多比肩不判强/冲克不定凶及分日冲突反例。整体强弱仍缺季节司令、根力、得势、生扶克泄耗效力与从化边界，不以数量或自创权重填补。
  下一批从 `data/canonical/classics/bazi/ditiansui_chanwei_v1.json#/sections/2/text` 核短引、条件和反例；全文命中仅是待审定位，不是 Evidence。
- `bazi-pattern`：正文提及不等于结构规则；缺成格/破格/兼格条件、流派限制和 Golden。
  下一批从 `data/canonical/classics/bazi/ditiansui_chanwei_v1.json#/sections/7/text` 核短引、条件和反例；全文命中仅是待审定位，不是 Evidence。
- `bazi-useful-god`：调候、扶抑、病药、格局用神未分别治理；依赖旺衰与格局；禁止输出喜用木火等具体结论。
  下一批先登记来源及权利，保存 RAW/Quarantine；无审核引文时保持未支持。
- `bazi-dayun`：旧说明不是执行；须核顺逆/起运法/节界/岁数换算/原局作用及不同 Variant。
  下一批从 `data/canonical/classics/bazi/ditiansui_chanwei_v1.json#/sections/3/text` 核短引、条件和反例；全文命中仅是待审定位，不是 Evidence。
- `bazi-annual`：日历干支不等于运势；缺原局、大运、流年作用图及强弱/喜忌条件规则。
  下一批从 `data/canonical/classics/bazi/ditiansui_chanwei_v1.json#/sections/1/text` 核短引、条件和反例；全文命中仅是待审定位，不是 Evidence。

## 今日运势 · PARTIAL

Scenario：`daily`；已执行=True；现有结构公开标志=False；AI=false。

已有知识、Rule 与 Evidence：

- 八字基础与十神映射：Terms `bazi.term.day_master`, `bazi.term.ten_gods`, `bazi.term.hidden_stems`, `bazi.term.month_command`, `bazi.term.root_candidates`, `bazi.term.hidden_to_visible`, `bazi.term.heavenly_stems`, `bazi.term.stem_polarity`, `bazi.term.five_elements`, `bazi.term.generation_control`；Phase1 Rule `bazi.rule.r001`, `bazi.rule.r002`, `bazi.rule.r003`, `bazi.rule.r011`, `bazi.rule.r012`, `bazi.rule.r013`, `bazi.rule.r014`, `bazi.rule.r015`, `bazi.rule.r016`。
- 旺衰及流派边界：Terms `bazi.term.strength_review_boundary`, `bazi.term.month_command`, `bazi.term.root_candidates`, `bazi.term.hidden_to_visible`；Phase1 Rule `bazi.rule.r012`, `bazi.rule.r013`, `bazi.rule.r014`, `bazi.rule.r015`。
- 喜用神分体系治理：Terms 尚无对应审核术语；Phase1 Rule 尚无对应审核规则。
- 大运：Terms 尚无对应审核术语；Phase1 Rule 尚无对应审核规则。
- 流年与岁运作用：Terms `bazi.term.branch_triple_harmonies`；Phase1 Rule `bazi.rule.r010`。
- 流日：Terms 尚无对应审核术语；Phase1 Rule 尚无对应审核规则。

已有 Phase2 / Golden / Variant：

- `bazi.phase2.pillars` / `ziping-structural-v1`；Golden：`bazi.structural-basic`；测试 `tests/test_phase2_bazi.py`。
  Evidence C：`bazi.source.yuanhai` / 渊海子平 / 喜忌篇 / `《渊海子平》喜忌篇；本轮固定短引`，引文：四柱排定,三才次分,专以日上天元,配合八字支干;有见不见之形,无时不有;神煞相绊,轻重较量。。
- `bazi.phase2.ten_gods` / `ziping-structural-v1`；Golden：`bazi.structural-basic`；测试 `tests/test_phase2_bazi.py`。
  Evidence C：`bazi.source.yuanhai` / 渊海子平 / 基础与藏遁 / `《渊海子平》基础；本轮固定短引`，引文：以甲为例★见甲:为比肩、兄弟。
 见乙:为劫财、败财,剋父及妻。
 见丙:为食神、天厨、寿星,为男。
 见丁:为伤官、退财、耗气,子甥。
 见戊:为偏财、偏妻、偏妾,剋子。
 见己:为正财、正妻,剋母,为合神。
 见庚:为偏官、七杀、官鬼、将星。
 见辛:为正官、禄马、荣神,父母。
 见壬:为倒食、偏印、梟神,剋女。
 见癸:为印綬、正人、君子,产业。。
  Evidence C：`bazi.source.yuanhai` / 渊海子平 / 基础与藏遁 / `《渊海子平》基础；本轮固定短引`，引文：以乙为例★见甲:为劫财、逐马,剋妻。
 见乙:为比肩、兄弟、朋友。
 见丙:为伤官、小人、盗气,为姪。
 见丁:为食神、天厨、寿星,子孙。
 见戊:为正财、正妻,剋母。
 见己:为偏财、偏妻、偏妾,剋子。
 见庚:为正官、禄马,剋父母。
 见辛:为偏官、七杀、官鬼,媒人。
 见壬:为印綬、正人、君子,忌杀。
 见癸:为倒食、偏印、梟神,剋母。。
  Evidence C：`bazi.source.yuanhai` / 渊海子平 / 十神关系选段 / `《渊海子平》论伤官；本轮固定短引`，引文：又云,伤官者,我生彼之谓也;以阳见阴,阴见阳,亦名盗气。。
  Evidence C：`bazi.source.yuanhai` / 渊海子平 / 十神关系选段 / `《渊海子平》论正财；本轮固定短引`，引文：何谓之正财?犹如正官之意;是阴见阳财,阳见阴财。。
  Evidence C：`bazi.source.yuanhai` / 渊海子平 / 十神关系选段 / `《渊海子平》正官论；本轮固定短引`，引文：夫正官者,甲见辛之类;乃阴见阳为官,阳见阴为鬼,阴阳配合成其道也。。
  Evidence C：`bazi.source.yuanhai` / 渊海子平 / 十神关系选段 / `《渊海子平》论印绶；本轮固定短引`，引文：夫印綬者,生我之谓也,亦名生气。以阳见阴,以阴见阳,谓之正印;阳见阳,阴见阴,谓之偏印。。
- `bazi.phase2.hidden_stems` / `ziping-structural-v1`；Golden：`bazi.structural-basic`；测试 `tests/test_phase2_bazi.py`。
  Evidence C：`bazi.source.yuanhai` / 渊海子平 / 基础与藏遁 / `《渊海子平》又地支藏遁歌；本轮固定短引`，引文：子宫癸水在其中,丑癸辛金己土同;寅宫甲木兼丙戊,卯宫乙木独相逢。辰藏乙戊三分癸,巳中庚金丙戊丛;午宫丁火并己土,未宫乙己丁共宗。申位庚金壬水戊,酉宫辛金独丰隆;戌宫辛金及丁戊,亥藏壬甲是真踪。。
- `bazi.phase2.month_command_factors` / `ziping-structural-v1`；Golden：`bazi.factors-normal`, `bazi.factors-tomb-boundary`, `bazi.factors-many-stems-no-root`, `bazi.factors-few-stems-with-root`, `bazi.factors-clash-not-erasure`, `bazi.factors-siling-unresolved`；测试 `tests/test_phase2_bazistrength.py`。
  Evidence C：`bazi.source.ditiansui-spouse` / 滴天髓阐微 / 月令、通根与透藏观察边界 / `《滴天髓阐微》通神论·月令；固定原文字符位置 37963；月令提纲`，引文：月令乃提纲之府,譬之宅也,人元为用事之神,宅之定向也,不可以不卜。。
  Evidence C：`bazi.source.ditiansui-spouse` / 滴天髓阐微 / 月令、通根与透藏观察边界 / `《滴天髓阐微》通神论·月令；固定原文字符位置 38056；寅月司令分日`，引文：如寅月生人,立春后七日前,皆值戊土用事;八日后十四日前者,丙火用事 ;十五日后,甲木用事。。
  Evidence C：`bazi.source.ditiansui-spouse` / 滴天髓阐微 / 月令、通根与透藏观察边界 / `《滴天髓阐微》通神论·衰旺；固定原文字符位置 39648；不可得令即旺失令即弱`，引文：得时俱为旺论,失令便作衰看,虽是至理,亦死法也。。
  Evidence C：`bazi.source.yuanhai` / 渊海子平 / 基础与藏遁 / `《渊海子平》又地支藏遁歌；本轮固定短引`，引文：子宫癸水在其中,丑癸辛金己土同;寅宫甲木兼丙戊,卯宫乙木独相逢。辰藏乙戊三分癸,巳中庚金丙戊丛;午宫丁火并己土,未宫乙己丁共宗。申位庚金壬水戊,酉宫辛金独丰隆;戌宫辛金及丁戊,亥藏壬甲是真踪。。
- `bazi.phase2.root_candidates` / `ziping-structural-v1`；Golden：`bazi.factors-normal`, `bazi.factors-tomb-boundary`, `bazi.factors-many-stems-no-root`, `bazi.factors-few-stems-with-root`, `bazi.factors-clash-not-erasure`, `bazi.factors-siling-unresolved`；测试 `tests/test_phase2_bazistrength.py`。
  Evidence C：`bazi.source.ditiansui-spouse` / 滴天髓阐微 / 月令、通根与透藏观察边界 / `《滴天髓阐微》通神论·衰旺；固定原文字符位置 39989；比肩与地支根不可数量等同`，引文：天干得一比肩,不如地支得一余气墓库。。
  Evidence C：`bazi.source.ditiansui-spouse` / 滴天髓阐微 / 月令、通根与透藏观察边界 / `《滴天髓阐微》通神论·衰旺；固定原文字符位置 40063；余气与长生禄旺根示例`，引文：余气者,如丙丁逢未,甲乙逢辰,庚辛逢戌,壬癸逢丑之类是也,得二比肩,不如支中得一长生禄旺,如甲乙逢亥寅卯之类是也。。
  Evidence C：`bazi.source.ditiansui-spouse` / 滴天髓阐微 / 月令、通根与透藏观察边界 / `《滴天髓阐微》通神论·衰旺；固定原文字符位置 39648；不可得令即旺失令即弱`，引文：得时俱为旺论,失令便作衰看,虽是至理,亦死法也。。
  Evidence C：`bazi.source.yuanhai` / 渊海子平 / 基础与藏遁 / `《渊海子平》又地支藏遁歌；本轮固定短引`，引文：子宫癸水在其中,丑癸辛金己土同;寅宫甲木兼丙戊,卯宫乙木独相逢。辰藏乙戊三分癸,巳中庚金丙戊丛;午宫丁火并己土,未宫乙己丁共宗。申位庚金壬水戊,酉宫辛金独丰隆;戌宫辛金及丁戊,亥藏壬甲是真踪。。
- `bazi.phase2.hidden_to_visible` / `ziping-structural-v1`；Golden：`bazi.factors-normal`, `bazi.factors-tomb-boundary`, `bazi.factors-many-stems-no-root`, `bazi.factors-few-stems-with-root`, `bazi.factors-clash-not-erasure`, `bazi.factors-siling-unresolved`；测试 `tests/test_phase2_bazistrength.py`。
  Evidence C：`bazi.source.ditiansui-spouse` / 滴天髓阐微 / 月令、通根与透藏观察边界 / `《滴天髓阐微》通神论·月令；固定原文字符位置 38284；藏干与显干引助`，引文：故知地支人元必得天干引助,天干为用,必要地支司令。。
  Evidence C：`bazi.source.yuanhai` / 渊海子平 / 基础与藏遁 / `《渊海子平》又地支藏遁歌；本轮固定短引`，引文：子宫癸水在其中,丑癸辛金己土同;寅宫甲木兼丙戊,卯宫乙木独相逢。辰藏乙戊三分癸,巳中庚金丙戊丛;午宫丁火并己土,未宫乙己丁共宗。申位庚金壬水戊,酉宫辛金独丰隆;戌宫辛金及丁戊,亥藏壬甲是真踪。。
- `bazi.phase2.support_relations` / `ziping-structural-v1`；Golden：`bazi.support-normal`, `bazi.support-yin`, `bazi.support-visible-peers`, `bazi.support-conflict`；测试 `tests/test_phase2_bazisupport.py`。
  Evidence C：`bazi.source.yuanhai` / 渊海子平 / 生克关系与效力界限 / `《渊海子平》五行相生及条件界限；固定原文字符位置 964`，引文：金能生水,水多金沉;水能生木,木盛水缩;木能生火,火多木焚;火能生土,土多火埋;土能生金,金多土变。。
  Evidence C：`bazi.source.yuanhai` / 渊海子平 / 生克关系与效力界限 / `《渊海子平》五行相克及条件界限；固定原文字符位置 1016`，引文：金能剋木,木坚金缺;木能剋土,土重木折;土能剋水,水多土流;水能剋火,火多水热;火能剋金,金多火熄。。
  Evidence C：`bazi.source.ditiansui-spouse` / 滴天髓阐微 / 天干阴阳五行分类 / `《滴天髓阐微·审核短引》十干阴阳短引；固定原文字符位置 4991`，引文：甲、丙、戊、庚、壬为阳,独丙火秉阳之精,而为阳中之阳;乙、丁、己、辛、癸为阴,独癸水秉阴之精,而为阴中之阴。。
  Evidence C：`bazi.source.ditiansui-spouse` / 滴天髓阐微 / 天干阴阳五行分类 / `《滴天髓阐微·审核短引》十干五行短引；固定原文字符位置 5159`，引文：甲乙一木也,丙丁一火也,戊己一土也,庚辛一金也,壬癸一水也,即分别所用,不过阳刚阴柔,阳健阴顺而已。。
  Evidence C：`bazi.source.yuanhai` / 渊海子平 / 基础与藏遁 / `《渊海子平》基础；本轮固定短引`，引文：以甲为例★见甲:为比肩、兄弟。
 见乙:为劫财、败财,剋父及妻。
 见丙:为食神、天厨、寿星,为男。
 见丁:为伤官、退财、耗气,子甥。
 见戊:为偏财、偏妻、偏妾,剋子。
 见己:为正财、正妻,剋母,为合神。
 见庚:为偏官、七杀、官鬼、将星。
 见辛:为正官、禄马、荣神,父母。
 见壬:为倒食、偏印、梟神,剋女。
 见癸:为印綬、正人、君子,产业。。
  Evidence C：`bazi.source.yuanhai` / 渊海子平 / 基础与藏遁 / `《渊海子平》基础；本轮固定短引`，引文：以乙为例★见甲:为劫财、逐马,剋妻。
 见乙:为比肩、兄弟、朋友。
 见丙:为伤官、小人、盗气,为姪。
 见丁:为食神、天厨、寿星,子孙。
 见戊:为正财、正妻,剋母。
 见己:为偏财、偏妻、偏妾,剋子。
 见庚:为正官、禄马,剋父母。
 见辛:为偏官、七杀、官鬼,媒人。
 见壬:为印綬、正人、君子,忌杀。
 见癸:为倒食、偏印、梟神,剋母。。
  Evidence C：`bazi.source.yuanhai` / 渊海子平 / 十神关系选段 / `《渊海子平》论伤官；本轮固定短引`，引文：又云,伤官者,我生彼之谓也;以阳见阴,阴见阳,亦名盗气。。
  Evidence C：`bazi.source.yuanhai` / 渊海子平 / 十神关系选段 / `《渊海子平》论正财；本轮固定短引`，引文：何谓之正财?犹如正官之意;是阴见阳财,阳见阴财。。
  Evidence C：`bazi.source.yuanhai` / 渊海子平 / 十神关系选段 / `《渊海子平》正官论；本轮固定短引`，引文：夫正官者,甲见辛之类;乃阴见阳为官,阳见阴为鬼,阴阳配合成其道也。。
  Evidence C：`bazi.source.yuanhai` / 渊海子平 / 十神关系选段 / `《渊海子平》论印绶；本轮固定短引`，引文：夫印綬者,生我之谓也,亦名生气。以阳见阴,以阴见阳,谓之正印;阳见阳,阴见阴,谓之偏印。。
  Evidence C：`bazi.source.yuanhai` / 渊海子平 / 基础与藏遁 / `《渊海子平》又地支藏遁歌；本轮固定短引`，引文：子宫癸水在其中,丑癸辛金己土同;寅宫甲木兼丙戊,卯宫乙木独相逢。辰藏乙戊三分癸,巳中庚金丙戊丛;午宫丁火并己土,未宫乙己丁共宗。申位庚金壬水戊,酉宫辛金独丰隆;戌宫辛金及丁戊,亥藏壬甲是真踪。。

当前场景可输出结论（只描述事实，不追加吉凶含义）：

- `fortune.day_structure`：READY；匹配 `bazi.scenario.daily_structure`，事实路径 `/`；deterministic_structure_only。

当前禁止结论：今日吉凶；今日综合分；今日财运/桃花概率。

缺失能力 / 依赖 / 下一批：

- `bazi-foundation`：十干阴阳五行、生克方向及四柱/日主/十神/藏干已有审核短引、执行与 Golden；仍缺十二长生、季节实际效力及基础结构到个人结论的条件规则，真太阳时未实现；旧表权重不作通用结论。
  下一批从 `data/canonical/classics/bazi/ditiansui_chanwei_v1.json#/sections/0/text` 核短引、条件和反例；全文命中仅是待审定位，不是 Evidence。
- `bazi-strength`：月令/通根候选/透藏/生克方向位置 v1 已按原模型执行，含正常/阴日干/多比肩不判强/冲克不定凶及分日冲突反例。整体强弱仍缺季节司令、根力、得势、生扶克泄耗效力与从化边界，不以数量或自创权重填补。
  下一批从 `data/canonical/classics/bazi/ditiansui_chanwei_v1.json#/sections/2/text` 核短引、条件和反例；全文命中仅是待审定位，不是 Evidence。
- `bazi-useful-god`：调候、扶抑、病药、格局用神未分别治理；依赖旺衰与格局；禁止输出喜用木火等具体结论。
  下一批先登记来源及权利，保存 RAW/Quarantine；无审核引文时保持未支持。
- `bazi-dayun`：旧说明不是执行；须核顺逆/起运法/节界/岁数换算/原局作用及不同 Variant。
  下一批从 `data/canonical/classics/bazi/ditiansui_chanwei_v1.json#/sections/3/text` 核短引、条件和反例；全文命中仅是待审定位，不是 Evidence。
- `bazi-annual`：日历干支不等于运势；缺原局、大运、流年作用图及强弱/喜忌条件规则。
  下一批从 `data/canonical/classics/bazi/ditiansui_chanwei_v1.json#/sections/1/text` 核短引、条件和反例；全文命中仅是待审定位，不是 Evidence。
- `bazi-day`：缺流日与原局/岁运关系及时间窗；日历日干支不能直接推每日吉凶。
  下一批从 `data/canonical/classics/bazi/yuanhai_ziping_v1.json#/sections/7/text` 核短引、条件和反例；全文命中仅是待审定位，不是 Evidence。

## 本周运势 · PARTIAL

Scenario：`weekly`；已执行=True；现有结构公开标志=False；AI=false。

已有知识、Rule 与 Evidence：

- 八字基础与十神映射：Terms `bazi.term.day_master`, `bazi.term.ten_gods`, `bazi.term.hidden_stems`, `bazi.term.month_command`, `bazi.term.root_candidates`, `bazi.term.hidden_to_visible`, `bazi.term.heavenly_stems`, `bazi.term.stem_polarity`, `bazi.term.five_elements`, `bazi.term.generation_control`；Phase1 Rule `bazi.rule.r001`, `bazi.rule.r002`, `bazi.rule.r003`, `bazi.rule.r011`, `bazi.rule.r012`, `bazi.rule.r013`, `bazi.rule.r014`, `bazi.rule.r015`, `bazi.rule.r016`。
- 旺衰及流派边界：Terms `bazi.term.strength_review_boundary`, `bazi.term.month_command`, `bazi.term.root_candidates`, `bazi.term.hidden_to_visible`；Phase1 Rule `bazi.rule.r012`, `bazi.rule.r013`, `bazi.rule.r014`, `bazi.rule.r015`。
- 喜用神分体系治理：Terms 尚无对应审核术语；Phase1 Rule 尚无对应审核规则。
- 大运：Terms 尚无对应审核术语；Phase1 Rule 尚无对应审核规则。
- 流年与岁运作用：Terms `bazi.term.branch_triple_harmonies`；Phase1 Rule `bazi.rule.r010`。
- 流日：Terms 尚无对应审核术语；Phase1 Rule 尚无对应审核规则。

已有 Phase2 / Golden / Variant：

- `bazi.phase2.pillars` / `ziping-structural-v1`；Golden：`bazi.structural-basic`；测试 `tests/test_phase2_bazi.py`。
  Evidence C：`bazi.source.yuanhai` / 渊海子平 / 喜忌篇 / `《渊海子平》喜忌篇；本轮固定短引`，引文：四柱排定,三才次分,专以日上天元,配合八字支干;有见不见之形,无时不有;神煞相绊,轻重较量。。
- `bazi.phase2.ten_gods` / `ziping-structural-v1`；Golden：`bazi.structural-basic`；测试 `tests/test_phase2_bazi.py`。
  Evidence C：`bazi.source.yuanhai` / 渊海子平 / 基础与藏遁 / `《渊海子平》基础；本轮固定短引`，引文：以甲为例★见甲:为比肩、兄弟。
 见乙:为劫财、败财,剋父及妻。
 见丙:为食神、天厨、寿星,为男。
 见丁:为伤官、退财、耗气,子甥。
 见戊:为偏财、偏妻、偏妾,剋子。
 见己:为正财、正妻,剋母,为合神。
 见庚:为偏官、七杀、官鬼、将星。
 见辛:为正官、禄马、荣神,父母。
 见壬:为倒食、偏印、梟神,剋女。
 见癸:为印綬、正人、君子,产业。。
  Evidence C：`bazi.source.yuanhai` / 渊海子平 / 基础与藏遁 / `《渊海子平》基础；本轮固定短引`，引文：以乙为例★见甲:为劫财、逐马,剋妻。
 见乙:为比肩、兄弟、朋友。
 见丙:为伤官、小人、盗气,为姪。
 见丁:为食神、天厨、寿星,子孙。
 见戊:为正财、正妻,剋母。
 见己:为偏财、偏妻、偏妾,剋子。
 见庚:为正官、禄马,剋父母。
 见辛:为偏官、七杀、官鬼,媒人。
 见壬:为印綬、正人、君子,忌杀。
 见癸:为倒食、偏印、梟神,剋母。。
  Evidence C：`bazi.source.yuanhai` / 渊海子平 / 十神关系选段 / `《渊海子平》论伤官；本轮固定短引`，引文：又云,伤官者,我生彼之谓也;以阳见阴,阴见阳,亦名盗气。。
  Evidence C：`bazi.source.yuanhai` / 渊海子平 / 十神关系选段 / `《渊海子平》论正财；本轮固定短引`，引文：何谓之正财?犹如正官之意;是阴见阳财,阳见阴财。。
  Evidence C：`bazi.source.yuanhai` / 渊海子平 / 十神关系选段 / `《渊海子平》正官论；本轮固定短引`，引文：夫正官者,甲见辛之类;乃阴见阳为官,阳见阴为鬼,阴阳配合成其道也。。
  Evidence C：`bazi.source.yuanhai` / 渊海子平 / 十神关系选段 / `《渊海子平》论印绶；本轮固定短引`，引文：夫印綬者,生我之谓也,亦名生气。以阳见阴,以阴见阳,谓之正印;阳见阳,阴见阴,谓之偏印。。
- `bazi.phase2.hidden_stems` / `ziping-structural-v1`；Golden：`bazi.structural-basic`；测试 `tests/test_phase2_bazi.py`。
  Evidence C：`bazi.source.yuanhai` / 渊海子平 / 基础与藏遁 / `《渊海子平》又地支藏遁歌；本轮固定短引`，引文：子宫癸水在其中,丑癸辛金己土同;寅宫甲木兼丙戊,卯宫乙木独相逢。辰藏乙戊三分癸,巳中庚金丙戊丛;午宫丁火并己土,未宫乙己丁共宗。申位庚金壬水戊,酉宫辛金独丰隆;戌宫辛金及丁戊,亥藏壬甲是真踪。。
- `bazi.phase2.month_command_factors` / `ziping-structural-v1`；Golden：`bazi.factors-normal`, `bazi.factors-tomb-boundary`, `bazi.factors-many-stems-no-root`, `bazi.factors-few-stems-with-root`, `bazi.factors-clash-not-erasure`, `bazi.factors-siling-unresolved`；测试 `tests/test_phase2_bazistrength.py`。
  Evidence C：`bazi.source.ditiansui-spouse` / 滴天髓阐微 / 月令、通根与透藏观察边界 / `《滴天髓阐微》通神论·月令；固定原文字符位置 37963；月令提纲`，引文：月令乃提纲之府,譬之宅也,人元为用事之神,宅之定向也,不可以不卜。。
  Evidence C：`bazi.source.ditiansui-spouse` / 滴天髓阐微 / 月令、通根与透藏观察边界 / `《滴天髓阐微》通神论·月令；固定原文字符位置 38056；寅月司令分日`，引文：如寅月生人,立春后七日前,皆值戊土用事;八日后十四日前者,丙火用事 ;十五日后,甲木用事。。
  Evidence C：`bazi.source.ditiansui-spouse` / 滴天髓阐微 / 月令、通根与透藏观察边界 / `《滴天髓阐微》通神论·衰旺；固定原文字符位置 39648；不可得令即旺失令即弱`，引文：得时俱为旺论,失令便作衰看,虽是至理,亦死法也。。
  Evidence C：`bazi.source.yuanhai` / 渊海子平 / 基础与藏遁 / `《渊海子平》又地支藏遁歌；本轮固定短引`，引文：子宫癸水在其中,丑癸辛金己土同;寅宫甲木兼丙戊,卯宫乙木独相逢。辰藏乙戊三分癸,巳中庚金丙戊丛;午宫丁火并己土,未宫乙己丁共宗。申位庚金壬水戊,酉宫辛金独丰隆;戌宫辛金及丁戊,亥藏壬甲是真踪。。
- `bazi.phase2.root_candidates` / `ziping-structural-v1`；Golden：`bazi.factors-normal`, `bazi.factors-tomb-boundary`, `bazi.factors-many-stems-no-root`, `bazi.factors-few-stems-with-root`, `bazi.factors-clash-not-erasure`, `bazi.factors-siling-unresolved`；测试 `tests/test_phase2_bazistrength.py`。
  Evidence C：`bazi.source.ditiansui-spouse` / 滴天髓阐微 / 月令、通根与透藏观察边界 / `《滴天髓阐微》通神论·衰旺；固定原文字符位置 39989；比肩与地支根不可数量等同`，引文：天干得一比肩,不如地支得一余气墓库。。
  Evidence C：`bazi.source.ditiansui-spouse` / 滴天髓阐微 / 月令、通根与透藏观察边界 / `《滴天髓阐微》通神论·衰旺；固定原文字符位置 40063；余气与长生禄旺根示例`，引文：余气者,如丙丁逢未,甲乙逢辰,庚辛逢戌,壬癸逢丑之类是也,得二比肩,不如支中得一长生禄旺,如甲乙逢亥寅卯之类是也。。
  Evidence C：`bazi.source.ditiansui-spouse` / 滴天髓阐微 / 月令、通根与透藏观察边界 / `《滴天髓阐微》通神论·衰旺；固定原文字符位置 39648；不可得令即旺失令即弱`，引文：得时俱为旺论,失令便作衰看,虽是至理,亦死法也。。
  Evidence C：`bazi.source.yuanhai` / 渊海子平 / 基础与藏遁 / `《渊海子平》又地支藏遁歌；本轮固定短引`，引文：子宫癸水在其中,丑癸辛金己土同;寅宫甲木兼丙戊,卯宫乙木独相逢。辰藏乙戊三分癸,巳中庚金丙戊丛;午宫丁火并己土,未宫乙己丁共宗。申位庚金壬水戊,酉宫辛金独丰隆;戌宫辛金及丁戊,亥藏壬甲是真踪。。
- `bazi.phase2.hidden_to_visible` / `ziping-structural-v1`；Golden：`bazi.factors-normal`, `bazi.factors-tomb-boundary`, `bazi.factors-many-stems-no-root`, `bazi.factors-few-stems-with-root`, `bazi.factors-clash-not-erasure`, `bazi.factors-siling-unresolved`；测试 `tests/test_phase2_bazistrength.py`。
  Evidence C：`bazi.source.ditiansui-spouse` / 滴天髓阐微 / 月令、通根与透藏观察边界 / `《滴天髓阐微》通神论·月令；固定原文字符位置 38284；藏干与显干引助`，引文：故知地支人元必得天干引助,天干为用,必要地支司令。。
  Evidence C：`bazi.source.yuanhai` / 渊海子平 / 基础与藏遁 / `《渊海子平》又地支藏遁歌；本轮固定短引`，引文：子宫癸水在其中,丑癸辛金己土同;寅宫甲木兼丙戊,卯宫乙木独相逢。辰藏乙戊三分癸,巳中庚金丙戊丛;午宫丁火并己土,未宫乙己丁共宗。申位庚金壬水戊,酉宫辛金独丰隆;戌宫辛金及丁戊,亥藏壬甲是真踪。。
- `bazi.phase2.support_relations` / `ziping-structural-v1`；Golden：`bazi.support-normal`, `bazi.support-yin`, `bazi.support-visible-peers`, `bazi.support-conflict`；测试 `tests/test_phase2_bazisupport.py`。
  Evidence C：`bazi.source.yuanhai` / 渊海子平 / 生克关系与效力界限 / `《渊海子平》五行相生及条件界限；固定原文字符位置 964`，引文：金能生水,水多金沉;水能生木,木盛水缩;木能生火,火多木焚;火能生土,土多火埋;土能生金,金多土变。。
  Evidence C：`bazi.source.yuanhai` / 渊海子平 / 生克关系与效力界限 / `《渊海子平》五行相克及条件界限；固定原文字符位置 1016`，引文：金能剋木,木坚金缺;木能剋土,土重木折;土能剋水,水多土流;水能剋火,火多水热;火能剋金,金多火熄。。
  Evidence C：`bazi.source.ditiansui-spouse` / 滴天髓阐微 / 天干阴阳五行分类 / `《滴天髓阐微·审核短引》十干阴阳短引；固定原文字符位置 4991`，引文：甲、丙、戊、庚、壬为阳,独丙火秉阳之精,而为阳中之阳;乙、丁、己、辛、癸为阴,独癸水秉阴之精,而为阴中之阴。。
  Evidence C：`bazi.source.ditiansui-spouse` / 滴天髓阐微 / 天干阴阳五行分类 / `《滴天髓阐微·审核短引》十干五行短引；固定原文字符位置 5159`，引文：甲乙一木也,丙丁一火也,戊己一土也,庚辛一金也,壬癸一水也,即分别所用,不过阳刚阴柔,阳健阴顺而已。。
  Evidence C：`bazi.source.yuanhai` / 渊海子平 / 基础与藏遁 / `《渊海子平》基础；本轮固定短引`，引文：以甲为例★见甲:为比肩、兄弟。
 见乙:为劫财、败财,剋父及妻。
 见丙:为食神、天厨、寿星,为男。
 见丁:为伤官、退财、耗气,子甥。
 见戊:为偏财、偏妻、偏妾,剋子。
 见己:为正财、正妻,剋母,为合神。
 见庚:为偏官、七杀、官鬼、将星。
 见辛:为正官、禄马、荣神,父母。
 见壬:为倒食、偏印、梟神,剋女。
 见癸:为印綬、正人、君子,产业。。
  Evidence C：`bazi.source.yuanhai` / 渊海子平 / 基础与藏遁 / `《渊海子平》基础；本轮固定短引`，引文：以乙为例★见甲:为劫财、逐马,剋妻。
 见乙:为比肩、兄弟、朋友。
 见丙:为伤官、小人、盗气,为姪。
 见丁:为食神、天厨、寿星,子孙。
 见戊:为正财、正妻,剋母。
 见己:为偏财、偏妻、偏妾,剋子。
 见庚:为正官、禄马,剋父母。
 见辛:为偏官、七杀、官鬼,媒人。
 见壬:为印綬、正人、君子,忌杀。
 见癸:为倒食、偏印、梟神,剋母。。
  Evidence C：`bazi.source.yuanhai` / 渊海子平 / 十神关系选段 / `《渊海子平》论伤官；本轮固定短引`，引文：又云,伤官者,我生彼之谓也;以阳见阴,阴见阳,亦名盗气。。
  Evidence C：`bazi.source.yuanhai` / 渊海子平 / 十神关系选段 / `《渊海子平》论正财；本轮固定短引`，引文：何谓之正财?犹如正官之意;是阴见阳财,阳见阴财。。
  Evidence C：`bazi.source.yuanhai` / 渊海子平 / 十神关系选段 / `《渊海子平》正官论；本轮固定短引`，引文：夫正官者,甲见辛之类;乃阴见阳为官,阳见阴为鬼,阴阳配合成其道也。。
  Evidence C：`bazi.source.yuanhai` / 渊海子平 / 十神关系选段 / `《渊海子平》论印绶；本轮固定短引`，引文：夫印綬者,生我之谓也,亦名生气。以阳见阴,以阴见阳,谓之正印;阳见阳,阴见阴,谓之偏印。。
  Evidence C：`bazi.source.yuanhai` / 渊海子平 / 基础与藏遁 / `《渊海子平》又地支藏遁歌；本轮固定短引`，引文：子宫癸水在其中,丑癸辛金己土同;寅宫甲木兼丙戊,卯宫乙木独相逢。辰藏乙戊三分癸,巳中庚金丙戊丛;午宫丁火并己土,未宫乙己丁共宗。申位庚金壬水戊,酉宫辛金独丰隆;戌宫辛金及丁戊,亥藏壬甲是真踪。。

当前场景可输出结论（只描述事实，不追加吉凶含义）：

- `fortune.week_structure`：READY；匹配 `bazi.scenario.weekly_structure`，事实路径 `/`；deterministic_structure_only。

当前禁止结论：本周趋势；本周有利日期；本周综合分。

缺失能力 / 依赖 / 下一批：

- `bazi-foundation`：十干阴阳五行、生克方向及四柱/日主/十神/藏干已有审核短引、执行与 Golden；仍缺十二长生、季节实际效力及基础结构到个人结论的条件规则，真太阳时未实现；旧表权重不作通用结论。
  下一批从 `data/canonical/classics/bazi/ditiansui_chanwei_v1.json#/sections/0/text` 核短引、条件和反例；全文命中仅是待审定位，不是 Evidence。
- `bazi-strength`：月令/通根候选/透藏/生克方向位置 v1 已按原模型执行，含正常/阴日干/多比肩不判强/冲克不定凶及分日冲突反例。整体强弱仍缺季节司令、根力、得势、生扶克泄耗效力与从化边界，不以数量或自创权重填补。
  下一批从 `data/canonical/classics/bazi/ditiansui_chanwei_v1.json#/sections/2/text` 核短引、条件和反例；全文命中仅是待审定位，不是 Evidence。
- `bazi-useful-god`：调候、扶抑、病药、格局用神未分别治理；依赖旺衰与格局；禁止输出喜用木火等具体结论。
  下一批先登记来源及权利，保存 RAW/Quarantine；无审核引文时保持未支持。
- `bazi-dayun`：旧说明不是执行；须核顺逆/起运法/节界/岁数换算/原局作用及不同 Variant。
  下一批从 `data/canonical/classics/bazi/ditiansui_chanwei_v1.json#/sections/3/text` 核短引、条件和反例；全文命中仅是待审定位，不是 Evidence。
- `bazi-annual`：日历干支不等于运势；缺原局、大运、流年作用图及强弱/喜忌条件规则。
  下一批从 `data/canonical/classics/bazi/ditiansui_chanwei_v1.json#/sections/1/text` 核短引、条件和反例；全文命中仅是待审定位，不是 Evidence。
- `bazi-day`：缺流日与原局/岁运关系及时间窗；日历日干支不能直接推每日吉凶。
  下一批从 `data/canonical/classics/bazi/yuanhai_ziping_v1.json#/sections/7/text` 核短引、条件和反例；全文命中仅是待审定位，不是 Evidence。

## 本月运势 · PARTIAL

Scenario：`monthly`；已执行=True；现有结构公开标志=False；AI=false。

已有知识、Rule 与 Evidence：

- 八字基础与十神映射：Terms `bazi.term.day_master`, `bazi.term.ten_gods`, `bazi.term.hidden_stems`, `bazi.term.month_command`, `bazi.term.root_candidates`, `bazi.term.hidden_to_visible`, `bazi.term.heavenly_stems`, `bazi.term.stem_polarity`, `bazi.term.five_elements`, `bazi.term.generation_control`；Phase1 Rule `bazi.rule.r001`, `bazi.rule.r002`, `bazi.rule.r003`, `bazi.rule.r011`, `bazi.rule.r012`, `bazi.rule.r013`, `bazi.rule.r014`, `bazi.rule.r015`, `bazi.rule.r016`。
- 旺衰及流派边界：Terms `bazi.term.strength_review_boundary`, `bazi.term.month_command`, `bazi.term.root_candidates`, `bazi.term.hidden_to_visible`；Phase1 Rule `bazi.rule.r012`, `bazi.rule.r013`, `bazi.rule.r014`, `bazi.rule.r015`。
- 喜用神分体系治理：Terms 尚无对应审核术语；Phase1 Rule 尚无对应审核规则。
- 大运：Terms 尚无对应审核术语；Phase1 Rule 尚无对应审核规则。
- 流年与岁运作用：Terms `bazi.term.branch_triple_harmonies`；Phase1 Rule `bazi.rule.r010`。
- 流月：Terms `bazi.term.month_command`；Phase1 Rule `bazi.rule.r013`。
- 流日：Terms 尚无对应审核术语；Phase1 Rule 尚无对应审核规则。

已有 Phase2 / Golden / Variant：

- `bazi.phase2.pillars` / `ziping-structural-v1`；Golden：`bazi.structural-basic`；测试 `tests/test_phase2_bazi.py`。
  Evidence C：`bazi.source.yuanhai` / 渊海子平 / 喜忌篇 / `《渊海子平》喜忌篇；本轮固定短引`，引文：四柱排定,三才次分,专以日上天元,配合八字支干;有见不见之形,无时不有;神煞相绊,轻重较量。。
- `bazi.phase2.ten_gods` / `ziping-structural-v1`；Golden：`bazi.structural-basic`；测试 `tests/test_phase2_bazi.py`。
  Evidence C：`bazi.source.yuanhai` / 渊海子平 / 基础与藏遁 / `《渊海子平》基础；本轮固定短引`，引文：以甲为例★见甲:为比肩、兄弟。
 见乙:为劫财、败财,剋父及妻。
 见丙:为食神、天厨、寿星,为男。
 见丁:为伤官、退财、耗气,子甥。
 见戊:为偏财、偏妻、偏妾,剋子。
 见己:为正财、正妻,剋母,为合神。
 见庚:为偏官、七杀、官鬼、将星。
 见辛:为正官、禄马、荣神,父母。
 见壬:为倒食、偏印、梟神,剋女。
 见癸:为印綬、正人、君子,产业。。
  Evidence C：`bazi.source.yuanhai` / 渊海子平 / 基础与藏遁 / `《渊海子平》基础；本轮固定短引`，引文：以乙为例★见甲:为劫财、逐马,剋妻。
 见乙:为比肩、兄弟、朋友。
 见丙:为伤官、小人、盗气,为姪。
 见丁:为食神、天厨、寿星,子孙。
 见戊:为正财、正妻,剋母。
 见己:为偏财、偏妻、偏妾,剋子。
 见庚:为正官、禄马,剋父母。
 见辛:为偏官、七杀、官鬼,媒人。
 见壬:为印綬、正人、君子,忌杀。
 见癸:为倒食、偏印、梟神,剋母。。
  Evidence C：`bazi.source.yuanhai` / 渊海子平 / 十神关系选段 / `《渊海子平》论伤官；本轮固定短引`，引文：又云,伤官者,我生彼之谓也;以阳见阴,阴见阳,亦名盗气。。
  Evidence C：`bazi.source.yuanhai` / 渊海子平 / 十神关系选段 / `《渊海子平》论正财；本轮固定短引`，引文：何谓之正财?犹如正官之意;是阴见阳财,阳见阴财。。
  Evidence C：`bazi.source.yuanhai` / 渊海子平 / 十神关系选段 / `《渊海子平》正官论；本轮固定短引`，引文：夫正官者,甲见辛之类;乃阴见阳为官,阳见阴为鬼,阴阳配合成其道也。。
  Evidence C：`bazi.source.yuanhai` / 渊海子平 / 十神关系选段 / `《渊海子平》论印绶；本轮固定短引`，引文：夫印綬者,生我之谓也,亦名生气。以阳见阴,以阴见阳,谓之正印;阳见阳,阴见阴,谓之偏印。。
- `bazi.phase2.hidden_stems` / `ziping-structural-v1`；Golden：`bazi.structural-basic`；测试 `tests/test_phase2_bazi.py`。
  Evidence C：`bazi.source.yuanhai` / 渊海子平 / 基础与藏遁 / `《渊海子平》又地支藏遁歌；本轮固定短引`，引文：子宫癸水在其中,丑癸辛金己土同;寅宫甲木兼丙戊,卯宫乙木独相逢。辰藏乙戊三分癸,巳中庚金丙戊丛;午宫丁火并己土,未宫乙己丁共宗。申位庚金壬水戊,酉宫辛金独丰隆;戌宫辛金及丁戊,亥藏壬甲是真踪。。
- `bazi.phase2.month_command_factors` / `ziping-structural-v1`；Golden：`bazi.factors-normal`, `bazi.factors-tomb-boundary`, `bazi.factors-many-stems-no-root`, `bazi.factors-few-stems-with-root`, `bazi.factors-clash-not-erasure`, `bazi.factors-siling-unresolved`；测试 `tests/test_phase2_bazistrength.py`。
  Evidence C：`bazi.source.ditiansui-spouse` / 滴天髓阐微 / 月令、通根与透藏观察边界 / `《滴天髓阐微》通神论·月令；固定原文字符位置 37963；月令提纲`，引文：月令乃提纲之府,譬之宅也,人元为用事之神,宅之定向也,不可以不卜。。
  Evidence C：`bazi.source.ditiansui-spouse` / 滴天髓阐微 / 月令、通根与透藏观察边界 / `《滴天髓阐微》通神论·月令；固定原文字符位置 38056；寅月司令分日`，引文：如寅月生人,立春后七日前,皆值戊土用事;八日后十四日前者,丙火用事 ;十五日后,甲木用事。。
  Evidence C：`bazi.source.ditiansui-spouse` / 滴天髓阐微 / 月令、通根与透藏观察边界 / `《滴天髓阐微》通神论·衰旺；固定原文字符位置 39648；不可得令即旺失令即弱`，引文：得时俱为旺论,失令便作衰看,虽是至理,亦死法也。。
  Evidence C：`bazi.source.yuanhai` / 渊海子平 / 基础与藏遁 / `《渊海子平》又地支藏遁歌；本轮固定短引`，引文：子宫癸水在其中,丑癸辛金己土同;寅宫甲木兼丙戊,卯宫乙木独相逢。辰藏乙戊三分癸,巳中庚金丙戊丛;午宫丁火并己土,未宫乙己丁共宗。申位庚金壬水戊,酉宫辛金独丰隆;戌宫辛金及丁戊,亥藏壬甲是真踪。。
- `bazi.phase2.root_candidates` / `ziping-structural-v1`；Golden：`bazi.factors-normal`, `bazi.factors-tomb-boundary`, `bazi.factors-many-stems-no-root`, `bazi.factors-few-stems-with-root`, `bazi.factors-clash-not-erasure`, `bazi.factors-siling-unresolved`；测试 `tests/test_phase2_bazistrength.py`。
  Evidence C：`bazi.source.ditiansui-spouse` / 滴天髓阐微 / 月令、通根与透藏观察边界 / `《滴天髓阐微》通神论·衰旺；固定原文字符位置 39989；比肩与地支根不可数量等同`，引文：天干得一比肩,不如地支得一余气墓库。。
  Evidence C：`bazi.source.ditiansui-spouse` / 滴天髓阐微 / 月令、通根与透藏观察边界 / `《滴天髓阐微》通神论·衰旺；固定原文字符位置 40063；余气与长生禄旺根示例`，引文：余气者,如丙丁逢未,甲乙逢辰,庚辛逢戌,壬癸逢丑之类是也,得二比肩,不如支中得一长生禄旺,如甲乙逢亥寅卯之类是也。。
  Evidence C：`bazi.source.ditiansui-spouse` / 滴天髓阐微 / 月令、通根与透藏观察边界 / `《滴天髓阐微》通神论·衰旺；固定原文字符位置 39648；不可得令即旺失令即弱`，引文：得时俱为旺论,失令便作衰看,虽是至理,亦死法也。。
  Evidence C：`bazi.source.yuanhai` / 渊海子平 / 基础与藏遁 / `《渊海子平》又地支藏遁歌；本轮固定短引`，引文：子宫癸水在其中,丑癸辛金己土同;寅宫甲木兼丙戊,卯宫乙木独相逢。辰藏乙戊三分癸,巳中庚金丙戊丛;午宫丁火并己土,未宫乙己丁共宗。申位庚金壬水戊,酉宫辛金独丰隆;戌宫辛金及丁戊,亥藏壬甲是真踪。。
- `bazi.phase2.hidden_to_visible` / `ziping-structural-v1`；Golden：`bazi.factors-normal`, `bazi.factors-tomb-boundary`, `bazi.factors-many-stems-no-root`, `bazi.factors-few-stems-with-root`, `bazi.factors-clash-not-erasure`, `bazi.factors-siling-unresolved`；测试 `tests/test_phase2_bazistrength.py`。
  Evidence C：`bazi.source.ditiansui-spouse` / 滴天髓阐微 / 月令、通根与透藏观察边界 / `《滴天髓阐微》通神论·月令；固定原文字符位置 38284；藏干与显干引助`，引文：故知地支人元必得天干引助,天干为用,必要地支司令。。
  Evidence C：`bazi.source.yuanhai` / 渊海子平 / 基础与藏遁 / `《渊海子平》又地支藏遁歌；本轮固定短引`，引文：子宫癸水在其中,丑癸辛金己土同;寅宫甲木兼丙戊,卯宫乙木独相逢。辰藏乙戊三分癸,巳中庚金丙戊丛;午宫丁火并己土,未宫乙己丁共宗。申位庚金壬水戊,酉宫辛金独丰隆;戌宫辛金及丁戊,亥藏壬甲是真踪。。
- `bazi.phase2.support_relations` / `ziping-structural-v1`；Golden：`bazi.support-normal`, `bazi.support-yin`, `bazi.support-visible-peers`, `bazi.support-conflict`；测试 `tests/test_phase2_bazisupport.py`。
  Evidence C：`bazi.source.yuanhai` / 渊海子平 / 生克关系与效力界限 / `《渊海子平》五行相生及条件界限；固定原文字符位置 964`，引文：金能生水,水多金沉;水能生木,木盛水缩;木能生火,火多木焚;火能生土,土多火埋;土能生金,金多土变。。
  Evidence C：`bazi.source.yuanhai` / 渊海子平 / 生克关系与效力界限 / `《渊海子平》五行相克及条件界限；固定原文字符位置 1016`，引文：金能剋木,木坚金缺;木能剋土,土重木折;土能剋水,水多土流;水能剋火,火多水热;火能剋金,金多火熄。。
  Evidence C：`bazi.source.ditiansui-spouse` / 滴天髓阐微 / 天干阴阳五行分类 / `《滴天髓阐微·审核短引》十干阴阳短引；固定原文字符位置 4991`，引文：甲、丙、戊、庚、壬为阳,独丙火秉阳之精,而为阳中之阳;乙、丁、己、辛、癸为阴,独癸水秉阴之精,而为阴中之阴。。
  Evidence C：`bazi.source.ditiansui-spouse` / 滴天髓阐微 / 天干阴阳五行分类 / `《滴天髓阐微·审核短引》十干五行短引；固定原文字符位置 5159`，引文：甲乙一木也,丙丁一火也,戊己一土也,庚辛一金也,壬癸一水也,即分别所用,不过阳刚阴柔,阳健阴顺而已。。
  Evidence C：`bazi.source.yuanhai` / 渊海子平 / 基础与藏遁 / `《渊海子平》基础；本轮固定短引`，引文：以甲为例★见甲:为比肩、兄弟。
 见乙:为劫财、败财,剋父及妻。
 见丙:为食神、天厨、寿星,为男。
 见丁:为伤官、退财、耗气,子甥。
 见戊:为偏财、偏妻、偏妾,剋子。
 见己:为正财、正妻,剋母,为合神。
 见庚:为偏官、七杀、官鬼、将星。
 见辛:为正官、禄马、荣神,父母。
 见壬:为倒食、偏印、梟神,剋女。
 见癸:为印綬、正人、君子,产业。。
  Evidence C：`bazi.source.yuanhai` / 渊海子平 / 基础与藏遁 / `《渊海子平》基础；本轮固定短引`，引文：以乙为例★见甲:为劫财、逐马,剋妻。
 见乙:为比肩、兄弟、朋友。
 见丙:为伤官、小人、盗气,为姪。
 见丁:为食神、天厨、寿星,子孙。
 见戊:为正财、正妻,剋母。
 见己:为偏财、偏妻、偏妾,剋子。
 见庚:为正官、禄马,剋父母。
 见辛:为偏官、七杀、官鬼,媒人。
 见壬:为印綬、正人、君子,忌杀。
 见癸:为倒食、偏印、梟神,剋母。。
  Evidence C：`bazi.source.yuanhai` / 渊海子平 / 十神关系选段 / `《渊海子平》论伤官；本轮固定短引`，引文：又云,伤官者,我生彼之谓也;以阳见阴,阴见阳,亦名盗气。。
  Evidence C：`bazi.source.yuanhai` / 渊海子平 / 十神关系选段 / `《渊海子平》论正财；本轮固定短引`，引文：何谓之正财?犹如正官之意;是阴见阳财,阳见阴财。。
  Evidence C：`bazi.source.yuanhai` / 渊海子平 / 十神关系选段 / `《渊海子平》正官论；本轮固定短引`，引文：夫正官者,甲见辛之类;乃阴见阳为官,阳见阴为鬼,阴阳配合成其道也。。
  Evidence C：`bazi.source.yuanhai` / 渊海子平 / 十神关系选段 / `《渊海子平》论印绶；本轮固定短引`，引文：夫印綬者,生我之谓也,亦名生气。以阳见阴,以阴见阳,谓之正印;阳见阳,阴见阴,谓之偏印。。
  Evidence C：`bazi.source.yuanhai` / 渊海子平 / 基础与藏遁 / `《渊海子平》又地支藏遁歌；本轮固定短引`，引文：子宫癸水在其中,丑癸辛金己土同;寅宫甲木兼丙戊,卯宫乙木独相逢。辰藏乙戊三分癸,巳中庚金丙戊丛;午宫丁火并己土,未宫乙己丁共宗。申位庚金壬水戊,酉宫辛金独丰隆;戌宫辛金及丁戊,亥藏壬甲是真踪。。

当前场景可输出结论（只描述事实，不追加吉凶含义）：

- `fortune.civil_month_structure`：READY；匹配 `bazi.scenario.monthly_structure`，事实路径 `/`；deterministic_structure_only。

当前禁止结论：本月吉凶；本月关键时间；本月综合分。

缺失能力 / 依赖 / 下一批：

- `bazi-foundation`：十干阴阳五行、生克方向及四柱/日主/十神/藏干已有审核短引、执行与 Golden；仍缺十二长生、季节实际效力及基础结构到个人结论的条件规则，真太阳时未实现；旧表权重不作通用结论。
  下一批从 `data/canonical/classics/bazi/ditiansui_chanwei_v1.json#/sections/0/text` 核短引、条件和反例；全文命中仅是待审定位，不是 Evidence。
- `bazi-strength`：月令/通根候选/透藏/生克方向位置 v1 已按原模型执行，含正常/阴日干/多比肩不判强/冲克不定凶及分日冲突反例。整体强弱仍缺季节司令、根力、得势、生扶克泄耗效力与从化边界，不以数量或自创权重填补。
  下一批从 `data/canonical/classics/bazi/ditiansui_chanwei_v1.json#/sections/2/text` 核短引、条件和反例；全文命中仅是待审定位，不是 Evidence。
- `bazi-useful-god`：调候、扶抑、病药、格局用神未分别治理；依赖旺衰与格局；禁止输出喜用木火等具体结论。
  下一批先登记来源及权利，保存 RAW/Quarantine；无审核引文时保持未支持。
- `bazi-dayun`：旧说明不是执行；须核顺逆/起运法/节界/岁数换算/原局作用及不同 Variant。
  下一批从 `data/canonical/classics/bazi/ditiansui_chanwei_v1.json#/sections/3/text` 核短引、条件和反例；全文命中仅是待审定位，不是 Evidence。
- `bazi-annual`：日历干支不等于运势；缺原局、大运、流年作用图及强弱/喜忌条件规则。
  下一批从 `data/canonical/classics/bazi/ditiansui_chanwei_v1.json#/sections/1/text` 核短引、条件和反例；全文命中仅是待审定位，不是 Evidence。
- `bazi-month`：缺节气月界/流月与原局、大运、流年作用；公历月复访范围与术数月界须分别记录。
  下一批从 `data/canonical/classics/bazi/ditiansui_chanwei_v1.json#/sections/8/text` 核短引、条件和反例；全文命中仅是待审定位，不是 Evidence。
- `bazi-day`：缺流日与原局/岁运关系及时间窗；日历日干支不能直接推每日吉凶。
  下一批从 `data/canonical/classics/bazi/yuanhai_ziping_v1.json#/sections/7/text` 核短引、条件和反例；全文命中仅是待审定位，不是 Evidence。

## 今年运势 · PARTIAL

Scenario：`yearly`；已执行=True；现有结构公开标志=False；AI=false。

已有知识、Rule 与 Evidence：

- 八字基础与十神映射：Terms `bazi.term.day_master`, `bazi.term.ten_gods`, `bazi.term.hidden_stems`, `bazi.term.month_command`, `bazi.term.root_candidates`, `bazi.term.hidden_to_visible`, `bazi.term.heavenly_stems`, `bazi.term.stem_polarity`, `bazi.term.five_elements`, `bazi.term.generation_control`；Phase1 Rule `bazi.rule.r001`, `bazi.rule.r002`, `bazi.rule.r003`, `bazi.rule.r011`, `bazi.rule.r012`, `bazi.rule.r013`, `bazi.rule.r014`, `bazi.rule.r015`, `bazi.rule.r016`。
- 旺衰及流派边界：Terms `bazi.term.strength_review_boundary`, `bazi.term.month_command`, `bazi.term.root_candidates`, `bazi.term.hidden_to_visible`；Phase1 Rule `bazi.rule.r012`, `bazi.rule.r013`, `bazi.rule.r014`, `bazi.rule.r015`。
- 喜用神分体系治理：Terms 尚无对应审核术语；Phase1 Rule 尚无对应审核规则。
- 大运：Terms 尚无对应审核术语；Phase1 Rule 尚无对应审核规则。
- 流年与岁运作用：Terms `bazi.term.branch_triple_harmonies`；Phase1 Rule `bazi.rule.r010`。

已有 Phase2 / Golden / Variant：

- `bazi.phase2.pillars` / `ziping-structural-v1`；Golden：`bazi.structural-basic`；测试 `tests/test_phase2_bazi.py`。
  Evidence C：`bazi.source.yuanhai` / 渊海子平 / 喜忌篇 / `《渊海子平》喜忌篇；本轮固定短引`，引文：四柱排定,三才次分,专以日上天元,配合八字支干;有见不见之形,无时不有;神煞相绊,轻重较量。。
- `bazi.phase2.ten_gods` / `ziping-structural-v1`；Golden：`bazi.structural-basic`；测试 `tests/test_phase2_bazi.py`。
  Evidence C：`bazi.source.yuanhai` / 渊海子平 / 基础与藏遁 / `《渊海子平》基础；本轮固定短引`，引文：以甲为例★见甲:为比肩、兄弟。
 见乙:为劫财、败财,剋父及妻。
 见丙:为食神、天厨、寿星,为男。
 见丁:为伤官、退财、耗气,子甥。
 见戊:为偏财、偏妻、偏妾,剋子。
 见己:为正财、正妻,剋母,为合神。
 见庚:为偏官、七杀、官鬼、将星。
 见辛:为正官、禄马、荣神,父母。
 见壬:为倒食、偏印、梟神,剋女。
 见癸:为印綬、正人、君子,产业。。
  Evidence C：`bazi.source.yuanhai` / 渊海子平 / 基础与藏遁 / `《渊海子平》基础；本轮固定短引`，引文：以乙为例★见甲:为劫财、逐马,剋妻。
 见乙:为比肩、兄弟、朋友。
 见丙:为伤官、小人、盗气,为姪。
 见丁:为食神、天厨、寿星,子孙。
 见戊:为正财、正妻,剋母。
 见己:为偏财、偏妻、偏妾,剋子。
 见庚:为正官、禄马,剋父母。
 见辛:为偏官、七杀、官鬼,媒人。
 见壬:为印綬、正人、君子,忌杀。
 见癸:为倒食、偏印、梟神,剋母。。
  Evidence C：`bazi.source.yuanhai` / 渊海子平 / 十神关系选段 / `《渊海子平》论伤官；本轮固定短引`，引文：又云,伤官者,我生彼之谓也;以阳见阴,阴见阳,亦名盗气。。
  Evidence C：`bazi.source.yuanhai` / 渊海子平 / 十神关系选段 / `《渊海子平》论正财；本轮固定短引`，引文：何谓之正财?犹如正官之意;是阴见阳财,阳见阴财。。
  Evidence C：`bazi.source.yuanhai` / 渊海子平 / 十神关系选段 / `《渊海子平》正官论；本轮固定短引`，引文：夫正官者,甲见辛之类;乃阴见阳为官,阳见阴为鬼,阴阳配合成其道也。。
  Evidence C：`bazi.source.yuanhai` / 渊海子平 / 十神关系选段 / `《渊海子平》论印绶；本轮固定短引`，引文：夫印綬者,生我之谓也,亦名生气。以阳见阴,以阴见阳,谓之正印;阳见阳,阴见阴,谓之偏印。。
- `bazi.phase2.hidden_stems` / `ziping-structural-v1`；Golden：`bazi.structural-basic`；测试 `tests/test_phase2_bazi.py`。
  Evidence C：`bazi.source.yuanhai` / 渊海子平 / 基础与藏遁 / `《渊海子平》又地支藏遁歌；本轮固定短引`，引文：子宫癸水在其中,丑癸辛金己土同;寅宫甲木兼丙戊,卯宫乙木独相逢。辰藏乙戊三分癸,巳中庚金丙戊丛;午宫丁火并己土,未宫乙己丁共宗。申位庚金壬水戊,酉宫辛金独丰隆;戌宫辛金及丁戊,亥藏壬甲是真踪。。
- `bazi.phase2.month_command_factors` / `ziping-structural-v1`；Golden：`bazi.factors-normal`, `bazi.factors-tomb-boundary`, `bazi.factors-many-stems-no-root`, `bazi.factors-few-stems-with-root`, `bazi.factors-clash-not-erasure`, `bazi.factors-siling-unresolved`；测试 `tests/test_phase2_bazistrength.py`。
  Evidence C：`bazi.source.ditiansui-spouse` / 滴天髓阐微 / 月令、通根与透藏观察边界 / `《滴天髓阐微》通神论·月令；固定原文字符位置 37963；月令提纲`，引文：月令乃提纲之府,譬之宅也,人元为用事之神,宅之定向也,不可以不卜。。
  Evidence C：`bazi.source.ditiansui-spouse` / 滴天髓阐微 / 月令、通根与透藏观察边界 / `《滴天髓阐微》通神论·月令；固定原文字符位置 38056；寅月司令分日`，引文：如寅月生人,立春后七日前,皆值戊土用事;八日后十四日前者,丙火用事 ;十五日后,甲木用事。。
  Evidence C：`bazi.source.ditiansui-spouse` / 滴天髓阐微 / 月令、通根与透藏观察边界 / `《滴天髓阐微》通神论·衰旺；固定原文字符位置 39648；不可得令即旺失令即弱`，引文：得时俱为旺论,失令便作衰看,虽是至理,亦死法也。。
  Evidence C：`bazi.source.yuanhai` / 渊海子平 / 基础与藏遁 / `《渊海子平》又地支藏遁歌；本轮固定短引`，引文：子宫癸水在其中,丑癸辛金己土同;寅宫甲木兼丙戊,卯宫乙木独相逢。辰藏乙戊三分癸,巳中庚金丙戊丛;午宫丁火并己土,未宫乙己丁共宗。申位庚金壬水戊,酉宫辛金独丰隆;戌宫辛金及丁戊,亥藏壬甲是真踪。。
- `bazi.phase2.root_candidates` / `ziping-structural-v1`；Golden：`bazi.factors-normal`, `bazi.factors-tomb-boundary`, `bazi.factors-many-stems-no-root`, `bazi.factors-few-stems-with-root`, `bazi.factors-clash-not-erasure`, `bazi.factors-siling-unresolved`；测试 `tests/test_phase2_bazistrength.py`。
  Evidence C：`bazi.source.ditiansui-spouse` / 滴天髓阐微 / 月令、通根与透藏观察边界 / `《滴天髓阐微》通神论·衰旺；固定原文字符位置 39989；比肩与地支根不可数量等同`，引文：天干得一比肩,不如地支得一余气墓库。。
  Evidence C：`bazi.source.ditiansui-spouse` / 滴天髓阐微 / 月令、通根与透藏观察边界 / `《滴天髓阐微》通神论·衰旺；固定原文字符位置 40063；余气与长生禄旺根示例`，引文：余气者,如丙丁逢未,甲乙逢辰,庚辛逢戌,壬癸逢丑之类是也,得二比肩,不如支中得一长生禄旺,如甲乙逢亥寅卯之类是也。。
  Evidence C：`bazi.source.ditiansui-spouse` / 滴天髓阐微 / 月令、通根与透藏观察边界 / `《滴天髓阐微》通神论·衰旺；固定原文字符位置 39648；不可得令即旺失令即弱`，引文：得时俱为旺论,失令便作衰看,虽是至理,亦死法也。。
  Evidence C：`bazi.source.yuanhai` / 渊海子平 / 基础与藏遁 / `《渊海子平》又地支藏遁歌；本轮固定短引`，引文：子宫癸水在其中,丑癸辛金己土同;寅宫甲木兼丙戊,卯宫乙木独相逢。辰藏乙戊三分癸,巳中庚金丙戊丛;午宫丁火并己土,未宫乙己丁共宗。申位庚金壬水戊,酉宫辛金独丰隆;戌宫辛金及丁戊,亥藏壬甲是真踪。。
- `bazi.phase2.hidden_to_visible` / `ziping-structural-v1`；Golden：`bazi.factors-normal`, `bazi.factors-tomb-boundary`, `bazi.factors-many-stems-no-root`, `bazi.factors-few-stems-with-root`, `bazi.factors-clash-not-erasure`, `bazi.factors-siling-unresolved`；测试 `tests/test_phase2_bazistrength.py`。
  Evidence C：`bazi.source.ditiansui-spouse` / 滴天髓阐微 / 月令、通根与透藏观察边界 / `《滴天髓阐微》通神论·月令；固定原文字符位置 38284；藏干与显干引助`，引文：故知地支人元必得天干引助,天干为用,必要地支司令。。
  Evidence C：`bazi.source.yuanhai` / 渊海子平 / 基础与藏遁 / `《渊海子平》又地支藏遁歌；本轮固定短引`，引文：子宫癸水在其中,丑癸辛金己土同;寅宫甲木兼丙戊,卯宫乙木独相逢。辰藏乙戊三分癸,巳中庚金丙戊丛;午宫丁火并己土,未宫乙己丁共宗。申位庚金壬水戊,酉宫辛金独丰隆;戌宫辛金及丁戊,亥藏壬甲是真踪。。
- `bazi.phase2.support_relations` / `ziping-structural-v1`；Golden：`bazi.support-normal`, `bazi.support-yin`, `bazi.support-visible-peers`, `bazi.support-conflict`；测试 `tests/test_phase2_bazisupport.py`。
  Evidence C：`bazi.source.yuanhai` / 渊海子平 / 生克关系与效力界限 / `《渊海子平》五行相生及条件界限；固定原文字符位置 964`，引文：金能生水,水多金沉;水能生木,木盛水缩;木能生火,火多木焚;火能生土,土多火埋;土能生金,金多土变。。
  Evidence C：`bazi.source.yuanhai` / 渊海子平 / 生克关系与效力界限 / `《渊海子平》五行相克及条件界限；固定原文字符位置 1016`，引文：金能剋木,木坚金缺;木能剋土,土重木折;土能剋水,水多土流;水能剋火,火多水热;火能剋金,金多火熄。。
  Evidence C：`bazi.source.ditiansui-spouse` / 滴天髓阐微 / 天干阴阳五行分类 / `《滴天髓阐微·审核短引》十干阴阳短引；固定原文字符位置 4991`，引文：甲、丙、戊、庚、壬为阳,独丙火秉阳之精,而为阳中之阳;乙、丁、己、辛、癸为阴,独癸水秉阴之精,而为阴中之阴。。
  Evidence C：`bazi.source.ditiansui-spouse` / 滴天髓阐微 / 天干阴阳五行分类 / `《滴天髓阐微·审核短引》十干五行短引；固定原文字符位置 5159`，引文：甲乙一木也,丙丁一火也,戊己一土也,庚辛一金也,壬癸一水也,即分别所用,不过阳刚阴柔,阳健阴顺而已。。
  Evidence C：`bazi.source.yuanhai` / 渊海子平 / 基础与藏遁 / `《渊海子平》基础；本轮固定短引`，引文：以甲为例★见甲:为比肩、兄弟。
 见乙:为劫财、败财,剋父及妻。
 见丙:为食神、天厨、寿星,为男。
 见丁:为伤官、退财、耗气,子甥。
 见戊:为偏财、偏妻、偏妾,剋子。
 见己:为正财、正妻,剋母,为合神。
 见庚:为偏官、七杀、官鬼、将星。
 见辛:为正官、禄马、荣神,父母。
 见壬:为倒食、偏印、梟神,剋女。
 见癸:为印綬、正人、君子,产业。。
  Evidence C：`bazi.source.yuanhai` / 渊海子平 / 基础与藏遁 / `《渊海子平》基础；本轮固定短引`，引文：以乙为例★见甲:为劫财、逐马,剋妻。
 见乙:为比肩、兄弟、朋友。
 见丙:为伤官、小人、盗气,为姪。
 见丁:为食神、天厨、寿星,子孙。
 见戊:为正财、正妻,剋母。
 见己:为偏财、偏妻、偏妾,剋子。
 见庚:为正官、禄马,剋父母。
 见辛:为偏官、七杀、官鬼,媒人。
 见壬:为印綬、正人、君子,忌杀。
 见癸:为倒食、偏印、梟神,剋母。。
  Evidence C：`bazi.source.yuanhai` / 渊海子平 / 十神关系选段 / `《渊海子平》论伤官；本轮固定短引`，引文：又云,伤官者,我生彼之谓也;以阳见阴,阴见阳,亦名盗气。。
  Evidence C：`bazi.source.yuanhai` / 渊海子平 / 十神关系选段 / `《渊海子平》论正财；本轮固定短引`，引文：何谓之正财?犹如正官之意;是阴见阳财,阳见阴财。。
  Evidence C：`bazi.source.yuanhai` / 渊海子平 / 十神关系选段 / `《渊海子平》正官论；本轮固定短引`，引文：夫正官者,甲见辛之类;乃阴见阳为官,阳见阴为鬼,阴阳配合成其道也。。
  Evidence C：`bazi.source.yuanhai` / 渊海子平 / 十神关系选段 / `《渊海子平》论印绶；本轮固定短引`，引文：夫印綬者,生我之谓也,亦名生气。以阳见阴,以阴见阳,谓之正印;阳见阳,阴见阴,谓之偏印。。
  Evidence C：`bazi.source.yuanhai` / 渊海子平 / 基础与藏遁 / `《渊海子平》又地支藏遁歌；本轮固定短引`，引文：子宫癸水在其中,丑癸辛金己土同;寅宫甲木兼丙戊,卯宫乙木独相逢。辰藏乙戊三分癸,巳中庚金丙戊丛;午宫丁火并己土,未宫乙己丁共宗。申位庚金壬水戊,酉宫辛金独丰隆;戌宫辛金及丁戊,亥藏壬甲是真踪。。

当前场景可输出结论（只描述事实，不追加吉凶含义）：

- `fortune.year_stem_structure`：READY；匹配 `bazi.scenario.flow_stem_ten_god`，事实路径 `/`；deterministic_structure_only。

当前禁止结论：流年吉凶；岁运事业财运断语；全年综合分。

缺失能力 / 依赖 / 下一批：

- `bazi-foundation`：十干阴阳五行、生克方向及四柱/日主/十神/藏干已有审核短引、执行与 Golden；仍缺十二长生、季节实际效力及基础结构到个人结论的条件规则，真太阳时未实现；旧表权重不作通用结论。
  下一批从 `data/canonical/classics/bazi/ditiansui_chanwei_v1.json#/sections/0/text` 核短引、条件和反例；全文命中仅是待审定位，不是 Evidence。
- `bazi-strength`：月令/通根候选/透藏/生克方向位置 v1 已按原模型执行，含正常/阴日干/多比肩不判强/冲克不定凶及分日冲突反例。整体强弱仍缺季节司令、根力、得势、生扶克泄耗效力与从化边界，不以数量或自创权重填补。
  下一批从 `data/canonical/classics/bazi/ditiansui_chanwei_v1.json#/sections/2/text` 核短引、条件和反例；全文命中仅是待审定位，不是 Evidence。
- `bazi-useful-god`：调候、扶抑、病药、格局用神未分别治理；依赖旺衰与格局；禁止输出喜用木火等具体结论。
  下一批先登记来源及权利，保存 RAW/Quarantine；无审核引文时保持未支持。
- `bazi-dayun`：旧说明不是执行；须核顺逆/起运法/节界/岁数换算/原局作用及不同 Variant。
  下一批从 `data/canonical/classics/bazi/ditiansui_chanwei_v1.json#/sections/3/text` 核短引、条件和反例；全文命中仅是待审定位，不是 Evidence。
- `bazi-annual`：日历干支不等于运势；缺原局、大运、流年作用图及强弱/喜忌条件规则。
  下一批从 `data/canonical/classics/bazi/ditiansui_chanwei_v1.json#/sections/1/text` 核短引、条件和反例；全文命中仅是待审定位，不是 Evidence。

## 桃花姻缘 · PRODUCTIZABLE

Scenario：`romance`；已执行=True；现有结构公开标志=False；AI=false。

已有知识、Rule 与 Evidence：

- 八字基础与十神映射：Terms `bazi.term.day_master`, `bazi.term.ten_gods`, `bazi.term.hidden_stems`, `bazi.term.month_command`, `bazi.term.root_candidates`, `bazi.term.hidden_to_visible`, `bazi.term.heavenly_stems`, `bazi.term.stem_polarity`, `bazi.term.five_elements`, `bazi.term.generation_control`；Phase1 Rule `bazi.rule.r001`, `bazi.rule.r002`, `bazi.rule.r003`, `bazi.rule.r011`, `bazi.rule.r012`, `bazi.rule.r013`, `bazi.rule.r014`, `bazi.rule.r015`, `bazi.rule.r016`。
- 旺衰及流派边界：Terms `bazi.term.strength_review_boundary`, `bazi.term.month_command`, `bazi.term.root_candidates`, `bazi.term.hidden_to_visible`；Phase1 Rule `bazi.rule.r012`, `bazi.rule.r013`, `bazi.rule.r014`, `bazi.rule.r015`。
- 喜用神分体系治理：Terms 尚无对应审核术语；Phase1 Rule 尚无对应审核规则。
- 流年与岁运作用：Terms `bazi.term.branch_triple_harmonies`；Phase1 Rule `bazi.rule.r010`。
- 婚恋专题：Terms `bazi.term.xianchi`, `bazi.term.stem_five_combinations`, `bazi.term.branch_six_harmonies`, `bazi.term.branch_six_harms`, `bazi.term.spouse_palace_day_branch`, `bazi.term.branch_six_clashes`, `bazi.term.branch_triple_harmonies`, `bazi.term.traditional_spouse_star_lens`；Phase1 Rule `bazi.rule.r004`, `bazi.rule.r005`, `bazi.rule.r006`, `bazi.rule.r007`, `bazi.rule.r008`, `bazi.rule.r009`, `bazi.rule.r010`, `bazi.rule.r011`。

已有 Phase2 / Golden / Variant：

- `bazi.phase2.pillars` / `ziping-structural-v1`；Golden：`bazi.structural-basic`；测试 `tests/test_phase2_bazi.py`。
  Evidence C：`bazi.source.yuanhai` / 渊海子平 / 喜忌篇 / `《渊海子平》喜忌篇；本轮固定短引`，引文：四柱排定,三才次分,专以日上天元,配合八字支干;有见不见之形,无时不有;神煞相绊,轻重较量。。
- `bazi.phase2.ten_gods` / `ziping-structural-v1`；Golden：`bazi.structural-basic`；测试 `tests/test_phase2_bazi.py`。
  Evidence C：`bazi.source.yuanhai` / 渊海子平 / 基础与藏遁 / `《渊海子平》基础；本轮固定短引`，引文：以甲为例★见甲:为比肩、兄弟。
 见乙:为劫财、败财,剋父及妻。
 见丙:为食神、天厨、寿星,为男。
 见丁:为伤官、退财、耗气,子甥。
 见戊:为偏财、偏妻、偏妾,剋子。
 见己:为正财、正妻,剋母,为合神。
 见庚:为偏官、七杀、官鬼、将星。
 见辛:为正官、禄马、荣神,父母。
 见壬:为倒食、偏印、梟神,剋女。
 见癸:为印綬、正人、君子,产业。。
  Evidence C：`bazi.source.yuanhai` / 渊海子平 / 基础与藏遁 / `《渊海子平》基础；本轮固定短引`，引文：以乙为例★见甲:为劫财、逐马,剋妻。
 见乙:为比肩、兄弟、朋友。
 见丙:为伤官、小人、盗气,为姪。
 见丁:为食神、天厨、寿星,子孙。
 见戊:为正财、正妻,剋母。
 见己:为偏财、偏妻、偏妾,剋子。
 见庚:为正官、禄马,剋父母。
 见辛:为偏官、七杀、官鬼,媒人。
 见壬:为印綬、正人、君子,忌杀。
 见癸:为倒食、偏印、梟神,剋母。。
  Evidence C：`bazi.source.yuanhai` / 渊海子平 / 十神关系选段 / `《渊海子平》论伤官；本轮固定短引`，引文：又云,伤官者,我生彼之谓也;以阳见阴,阴见阳,亦名盗气。。
  Evidence C：`bazi.source.yuanhai` / 渊海子平 / 十神关系选段 / `《渊海子平》论正财；本轮固定短引`，引文：何谓之正财?犹如正官之意;是阴见阳财,阳见阴财。。
  Evidence C：`bazi.source.yuanhai` / 渊海子平 / 十神关系选段 / `《渊海子平》正官论；本轮固定短引`，引文：夫正官者,甲见辛之类;乃阴见阳为官,阳见阴为鬼,阴阳配合成其道也。。
  Evidence C：`bazi.source.yuanhai` / 渊海子平 / 十神关系选段 / `《渊海子平》论印绶；本轮固定短引`，引文：夫印綬者,生我之谓也,亦名生气。以阳见阴,以阴见阳,谓之正印;阳见阳,阴见阴,谓之偏印。。
- `bazi.phase2.hidden_stems` / `ziping-structural-v1`；Golden：`bazi.structural-basic`；测试 `tests/test_phase2_bazi.py`。
  Evidence C：`bazi.source.yuanhai` / 渊海子平 / 基础与藏遁 / `《渊海子平》又地支藏遁歌；本轮固定短引`，引文：子宫癸水在其中,丑癸辛金己土同;寅宫甲木兼丙戊,卯宫乙木独相逢。辰藏乙戊三分癸,巳中庚金丙戊丛;午宫丁火并己土,未宫乙己丁共宗。申位庚金壬水戊,酉宫辛金独丰隆;戌宫辛金及丁戊,亥藏壬甲是真踪。。
- `bazi.phase2.xianchi_lookup` / `ziping-structural-v1`；Golden：`bazi.xianchi-explicit-dual-basis`；测试 `tests/test_phase2_bazi.py`。
  Evidence C：`bazi.source.sanming-xianchi-niutrans` / 三命通会 / 卷二·论咸池 / `《三命通会》卷二·论咸池；固定短引`，引文：《淮南子》曰： 日出扶桑，入于咸池。 故五行沐浴之地，名咸池。是取日人之义，万物暗昧之时。寅午戌卯、已酉丑午、申子辰酉、亥卯未子即长生第二位沐浴之宫是也。一名败神，一名桃花煞。
- `bazi.phase2.stem_five_combinations` / `ziping-structural-v1`；Golden：`bazi.relations-core`；测试 `tests/test_phase2_bazi.py`。
  Evidence C：`bazi.source.xieji-relations` / 钦定协纪辨方书 / 五合六合六害结构短引 / `《钦定协纪辨方书》卷一·五合；固定短引`，引文：甲与己合乙与庚合丙与辛合丁与壬合戊与癸合。
- `bazi.phase2.branch_six_harmonies` / `ziping-structural-v1`；Golden：`bazi.relations-core`；测试 `tests/test_phase2_bazi.py`。
  Evidence C：`bazi.source.xieji-relations` / 钦定协纪辨方书 / 五合六合六害结构短引 / `《钦定协纪辨方书》卷一·六合；固定短引`，引文：子与丑合寅与亥合卯与戌合辰与酉合巳与申合午与未合。
- `bazi.phase2.branch_six_harms` / `ziping-structural-v1`；Golden：`bazi.relations-core`；测试 `tests/test_phase2_bazi.py`。
  Evidence C：`bazi.source.xieji-relations` / 钦定协纪辨方书 / 五合六合六害结构短引 / `《钦定协纪辨方书》月害条；固定短引`，引文：月害者月中六害也假令夘辰相害者夘以乙旺之木害辰墓之土辰以墓土却害夘中癸水也寅巳相害者谓寅以旺甲害巳中戊土而巳以生庚害寅中旺甲也丑午相害者丑以癸水害午中丁火午以巳土害丑中癸水也子未相害者子以所生之辛金害未中墓木未以旺土害子中旺水也申亥相害者亥以生木害申中生土申以旺金害亥中生木又以生土害亥中旺水也酉戌相害者戌以墓火害酉之旺金酉以所生丁火害戌中辛金也。
- `bazi.phase2.spouse_palace_day_branch` / `ziping-structural-v1`；Golden：`bazi.relations-core`；测试 `tests/test_phase2_bazi.py`。
  Evidence C：`bazi.source.yuanhai` / 渊海子平 / 络绎赋·日支妻位 / `《渊海子平》络绎赋；固定短引`，引文：年干父兮支母。
 日干己兮支妻。
 月干兄兮支弟。
 时支女兮干儿。。
- `bazi.phase2.branch_six_clashes` / `ziping-structural-v1`；Golden：`bazi.relations-expanded`；测试 `tests/test_phase2_bazi.py`。
  Evidence C：`bazi.source.xieji-relations` / 钦定协纪辨方书 / 五合六合六害结构短引 / `《钦定协纪辨方书》月建相关条；固定短引`，引文：洞源经曰对七为冲隔三为破选择家所谓辰破丑而丑冲未亥破寅而寅冲申午破夘而夘冲酉酉破子而子冲午申破巳而巳冲亥戌破未而未冲丑是也。
  Evidence C：`bazi.source.xieji-relations` / 钦定协纪辨方书 / 五合六合六害结构短引 / `《钦定协纪辨方书》月建相关条；固定短引`，引文：假如建在子前三为平为夘后三为收为酉夘酉冲也建在丑前三为平为辰后三为收为戌辰戌冲也推之十二辰莫不皆然。
- `bazi.phase2.branch_triple_harmonies` / `ziping-structural-v1`；Golden：`bazi.relations-expanded`；测试 `tests/test_phase2_bazi.py`。
  Evidence C：`bazi.source.xieji-relations` / 钦定协纪辨方书 / 五合六合六害结构短引 / `《钦定协纪辨方书》大煞条；固定短引`，引文：考原曰大煞子年在子丑年在酉寅年在午夘年在夘辰年又在子如是逆行四正盖申子辰三合为水水旺于子也巳酉丑三合为金金旺于酉也寅午戌三合为火火旺于午也亥夘未三合为木木旺于夘也。
- `bazi.phase2.spouse_star_lens` / `ziping-structural-v1`；Golden：`bazi.spouse-star-lens-male`, `bazi.spouse-star-lens-female`；测试 `tests/test_phase2_bazi.py`。
  Evidence C：`bazi.source.yuanhai` / 渊海子平 / 传统配偶星观察口径 / `《渊海子平》六亲总篇；固定短引`，引文：用日干为主:正印正母;偏印偏母及祖父也;偏财是父,乃母之夫星也,亦为偏妻;正财为妻;偏财为妾,为父是也;比肩为兄弟姐妹也;七杀是男;正官是女;食神是男孙;伤官是女孙及祖母也。
 妇人命取六亲,与男命不同:取官星为夫星;七杀是偏夫;食神是男;伤官是女。。
  Evidence C：`bazi.source.ditiansui-spouse` / 滴天髓阐微 / 夫妻与女命观察边界 / `《滴天髓阐微》六亲论·女命章；固定短引`，引文：不必专执官星而论夫。专执伤食而论子。但以安祥顺静为贵,二德三奇不必论,咸池驿马纵有验,总之于理不长。其中究论,不可不详。。
  Evidence C：`bazi.source.ditiansui-spouse` / 滴天髓阐微 / 夫妻与女命观察边界 / `《滴天髓阐微》六亲论·夫妻；固定短引`，引文：子平之法,以财为妻,财是我克。人以财来侍我,此理出于正论。
- `bazi.phase2.month_command_factors` / `ziping-structural-v1`；Golden：`bazi.factors-normal`, `bazi.factors-tomb-boundary`, `bazi.factors-many-stems-no-root`, `bazi.factors-few-stems-with-root`, `bazi.factors-clash-not-erasure`, `bazi.factors-siling-unresolved`；测试 `tests/test_phase2_bazistrength.py`。
  Evidence C：`bazi.source.ditiansui-spouse` / 滴天髓阐微 / 月令、通根与透藏观察边界 / `《滴天髓阐微》通神论·月令；固定原文字符位置 37963；月令提纲`，引文：月令乃提纲之府,譬之宅也,人元为用事之神,宅之定向也,不可以不卜。。
  Evidence C：`bazi.source.ditiansui-spouse` / 滴天髓阐微 / 月令、通根与透藏观察边界 / `《滴天髓阐微》通神论·月令；固定原文字符位置 38056；寅月司令分日`，引文：如寅月生人,立春后七日前,皆值戊土用事;八日后十四日前者,丙火用事 ;十五日后,甲木用事。。
  Evidence C：`bazi.source.ditiansui-spouse` / 滴天髓阐微 / 月令、通根与透藏观察边界 / `《滴天髓阐微》通神论·衰旺；固定原文字符位置 39648；不可得令即旺失令即弱`，引文：得时俱为旺论,失令便作衰看,虽是至理,亦死法也。。
  Evidence C：`bazi.source.yuanhai` / 渊海子平 / 基础与藏遁 / `《渊海子平》又地支藏遁歌；本轮固定短引`，引文：子宫癸水在其中,丑癸辛金己土同;寅宫甲木兼丙戊,卯宫乙木独相逢。辰藏乙戊三分癸,巳中庚金丙戊丛;午宫丁火并己土,未宫乙己丁共宗。申位庚金壬水戊,酉宫辛金独丰隆;戌宫辛金及丁戊,亥藏壬甲是真踪。。
- `bazi.phase2.root_candidates` / `ziping-structural-v1`；Golden：`bazi.factors-normal`, `bazi.factors-tomb-boundary`, `bazi.factors-many-stems-no-root`, `bazi.factors-few-stems-with-root`, `bazi.factors-clash-not-erasure`, `bazi.factors-siling-unresolved`；测试 `tests/test_phase2_bazistrength.py`。
  Evidence C：`bazi.source.ditiansui-spouse` / 滴天髓阐微 / 月令、通根与透藏观察边界 / `《滴天髓阐微》通神论·衰旺；固定原文字符位置 39989；比肩与地支根不可数量等同`，引文：天干得一比肩,不如地支得一余气墓库。。
  Evidence C：`bazi.source.ditiansui-spouse` / 滴天髓阐微 / 月令、通根与透藏观察边界 / `《滴天髓阐微》通神论·衰旺；固定原文字符位置 40063；余气与长生禄旺根示例`，引文：余气者,如丙丁逢未,甲乙逢辰,庚辛逢戌,壬癸逢丑之类是也,得二比肩,不如支中得一长生禄旺,如甲乙逢亥寅卯之类是也。。
  Evidence C：`bazi.source.ditiansui-spouse` / 滴天髓阐微 / 月令、通根与透藏观察边界 / `《滴天髓阐微》通神论·衰旺；固定原文字符位置 39648；不可得令即旺失令即弱`，引文：得时俱为旺论,失令便作衰看,虽是至理,亦死法也。。
  Evidence C：`bazi.source.yuanhai` / 渊海子平 / 基础与藏遁 / `《渊海子平》又地支藏遁歌；本轮固定短引`，引文：子宫癸水在其中,丑癸辛金己土同;寅宫甲木兼丙戊,卯宫乙木独相逢。辰藏乙戊三分癸,巳中庚金丙戊丛;午宫丁火并己土,未宫乙己丁共宗。申位庚金壬水戊,酉宫辛金独丰隆;戌宫辛金及丁戊,亥藏壬甲是真踪。。
- `bazi.phase2.hidden_to_visible` / `ziping-structural-v1`；Golden：`bazi.factors-normal`, `bazi.factors-tomb-boundary`, `bazi.factors-many-stems-no-root`, `bazi.factors-few-stems-with-root`, `bazi.factors-clash-not-erasure`, `bazi.factors-siling-unresolved`；测试 `tests/test_phase2_bazistrength.py`。
  Evidence C：`bazi.source.ditiansui-spouse` / 滴天髓阐微 / 月令、通根与透藏观察边界 / `《滴天髓阐微》通神论·月令；固定原文字符位置 38284；藏干与显干引助`，引文：故知地支人元必得天干引助,天干为用,必要地支司令。。
  Evidence C：`bazi.source.yuanhai` / 渊海子平 / 基础与藏遁 / `《渊海子平》又地支藏遁歌；本轮固定短引`，引文：子宫癸水在其中,丑癸辛金己土同;寅宫甲木兼丙戊,卯宫乙木独相逢。辰藏乙戊三分癸,巳中庚金丙戊丛;午宫丁火并己土,未宫乙己丁共宗。申位庚金壬水戊,酉宫辛金独丰隆;戌宫辛金及丁戊,亥藏壬甲是真踪。。
- `bazi.phase2.support_relations` / `ziping-structural-v1`；Golden：`bazi.support-normal`, `bazi.support-yin`, `bazi.support-visible-peers`, `bazi.support-conflict`；测试 `tests/test_phase2_bazisupport.py`。
  Evidence C：`bazi.source.yuanhai` / 渊海子平 / 生克关系与效力界限 / `《渊海子平》五行相生及条件界限；固定原文字符位置 964`，引文：金能生水,水多金沉;水能生木,木盛水缩;木能生火,火多木焚;火能生土,土多火埋;土能生金,金多土变。。
  Evidence C：`bazi.source.yuanhai` / 渊海子平 / 生克关系与效力界限 / `《渊海子平》五行相克及条件界限；固定原文字符位置 1016`，引文：金能剋木,木坚金缺;木能剋土,土重木折;土能剋水,水多土流;水能剋火,火多水热;火能剋金,金多火熄。。
  Evidence C：`bazi.source.ditiansui-spouse` / 滴天髓阐微 / 天干阴阳五行分类 / `《滴天髓阐微·审核短引》十干阴阳短引；固定原文字符位置 4991`，引文：甲、丙、戊、庚、壬为阳,独丙火秉阳之精,而为阳中之阳;乙、丁、己、辛、癸为阴,独癸水秉阴之精,而为阴中之阴。。
  Evidence C：`bazi.source.ditiansui-spouse` / 滴天髓阐微 / 天干阴阳五行分类 / `《滴天髓阐微·审核短引》十干五行短引；固定原文字符位置 5159`，引文：甲乙一木也,丙丁一火也,戊己一土也,庚辛一金也,壬癸一水也,即分别所用,不过阳刚阴柔,阳健阴顺而已。。
  Evidence C：`bazi.source.yuanhai` / 渊海子平 / 基础与藏遁 / `《渊海子平》基础；本轮固定短引`，引文：以甲为例★见甲:为比肩、兄弟。
 见乙:为劫财、败财,剋父及妻。
 见丙:为食神、天厨、寿星,为男。
 见丁:为伤官、退财、耗气,子甥。
 见戊:为偏财、偏妻、偏妾,剋子。
 见己:为正财、正妻,剋母,为合神。
 见庚:为偏官、七杀、官鬼、将星。
 见辛:为正官、禄马、荣神,父母。
 见壬:为倒食、偏印、梟神,剋女。
 见癸:为印綬、正人、君子,产业。。
  Evidence C：`bazi.source.yuanhai` / 渊海子平 / 基础与藏遁 / `《渊海子平》基础；本轮固定短引`，引文：以乙为例★见甲:为劫财、逐马,剋妻。
 见乙:为比肩、兄弟、朋友。
 见丙:为伤官、小人、盗气,为姪。
 见丁:为食神、天厨、寿星,子孙。
 见戊:为正财、正妻,剋母。
 见己:为偏财、偏妻、偏妾,剋子。
 见庚:为正官、禄马,剋父母。
 见辛:为偏官、七杀、官鬼,媒人。
 见壬:为印綬、正人、君子,忌杀。
 见癸:为倒食、偏印、梟神,剋母。。
  Evidence C：`bazi.source.yuanhai` / 渊海子平 / 十神关系选段 / `《渊海子平》论伤官；本轮固定短引`，引文：又云,伤官者,我生彼之谓也;以阳见阴,阴见阳,亦名盗气。。
  Evidence C：`bazi.source.yuanhai` / 渊海子平 / 十神关系选段 / `《渊海子平》论正财；本轮固定短引`，引文：何谓之正财?犹如正官之意;是阴见阳财,阳见阴财。。
  Evidence C：`bazi.source.yuanhai` / 渊海子平 / 十神关系选段 / `《渊海子平》正官论；本轮固定短引`，引文：夫正官者,甲见辛之类;乃阴见阳为官,阳见阴为鬼,阴阳配合成其道也。。
  Evidence C：`bazi.source.yuanhai` / 渊海子平 / 十神关系选段 / `《渊海子平》论印绶；本轮固定短引`，引文：夫印綬者,生我之谓也,亦名生气。以阳见阴,以阴见阳,谓之正印;阳见阳,阴见阴,谓之偏印。。
  Evidence C：`bazi.source.yuanhai` / 渊海子平 / 基础与藏遁 / `《渊海子平》又地支藏遁歌；本轮固定短引`，引文：子宫癸水在其中,丑癸辛金己土同;寅宫甲木兼丙戊,卯宫乙木独相逢。辰藏乙戊三分癸,巳中庚金丙戊丛;午宫丁火并己土,未宫乙己丁共宗。申位庚金壬水戊,酉宫辛金独丰隆;戌宫辛金及丁戊,亥藏壬甲是真踪。。

当前场景可输出结论（只描述事实，不追加吉凶含义）：

- `romance.xianchi_structure`：READY；匹配 `bazi.scenario.xianchi_structure`，事实路径 `/`；deterministic_structure_only。
- 引擎另有配偶宫、传统配偶星 lens、五合/六合/六害/六冲/三合；当前 romance 只接咸池，这些其他能力已在 compatibility 接入，不能宣称 romance 已输出。

当前禁止结论：结婚时间；桃花概率；由咸池推人品；由官星推现代伴侣身份。

缺失能力 / 依赖 / 下一批：

- `bazi-foundation`：十干阴阳五行、生克方向及四柱/日主/十神/藏干已有审核短引、执行与 Golden；仍缺十二长生、季节实际效力及基础结构到个人结论的条件规则，真太阳时未实现；旧表权重不作通用结论。
  下一批从 `data/canonical/classics/bazi/ditiansui_chanwei_v1.json#/sections/0/text` 核短引、条件和反例；全文命中仅是待审定位，不是 Evidence。
- `bazi-strength`：月令/通根候选/透藏/生克方向位置 v1 已按原模型执行，含正常/阴日干/多比肩不判强/冲克不定凶及分日冲突反例。整体强弱仍缺季节司令、根力、得势、生扶克泄耗效力与从化边界，不以数量或自创权重填补。
  下一批从 `data/canonical/classics/bazi/ditiansui_chanwei_v1.json#/sections/2/text` 核短引、条件和反例；全文命中仅是待审定位，不是 Evidence。
- `bazi-useful-god`：调候、扶抑、病药、格局用神未分别治理；依赖旺衰与格局；禁止输出喜用木火等具体结论。
  下一批先登记来源及权利，保存 RAW/Quarantine；无审核引文时保持未支持。
- `bazi-annual`：日历干支不等于运势；缺原局、大运、流年作用图及强弱/喜忌条件规则。
  下一批从 `data/canonical/classics/bazi/ditiansui_chanwei_v1.json#/sections/1/text` 核短引、条件和反例；全文命中仅是待审定位，不是 Evidence。
- `bazi-romance`：咸池、日支传统配偶宫结构位、显式财星/官杀lens及五合/六合/六害/六冲/三合结构已核；缺红鸾天喜天姚、旺衰格局喜用与岁运婚恋解释；三刑争议仍阻塞；禁止命中结构直接断现代婚姻。
  下一批从 `data/canonical/classics/bazi/ditiansui_chanwei_v1.json#/sections/3/text` 核短引、条件和反例；全文命中仅是待审定位，不是 Evidence。

## 事业财运 · PARTIAL

Scenario：`career`；已执行=True；现有结构公开标志=False；AI=false。

已有知识、Rule 与 Evidence：

- 八字基础与十神映射：Terms `bazi.term.day_master`, `bazi.term.ten_gods`, `bazi.term.hidden_stems`, `bazi.term.month_command`, `bazi.term.root_candidates`, `bazi.term.hidden_to_visible`, `bazi.term.heavenly_stems`, `bazi.term.stem_polarity`, `bazi.term.five_elements`, `bazi.term.generation_control`；Phase1 Rule `bazi.rule.r001`, `bazi.rule.r002`, `bazi.rule.r003`, `bazi.rule.r011`, `bazi.rule.r012`, `bazi.rule.r013`, `bazi.rule.r014`, `bazi.rule.r015`, `bazi.rule.r016`。
- 十神结构与条件解释：Terms `bazi.term.ten_gods`, `bazi.term.hidden_to_visible`；Phase1 Rule `bazi.rule.r002`, `bazi.rule.r003`, `bazi.rule.r011`, `bazi.rule.r012`, `bazi.rule.r015`。
- 旺衰及流派边界：Terms `bazi.term.strength_review_boundary`, `bazi.term.month_command`, `bazi.term.root_candidates`, `bazi.term.hidden_to_visible`；Phase1 Rule `bazi.rule.r012`, `bazi.rule.r013`, `bazi.rule.r014`, `bazi.rule.r015`。
- 格局：Terms 尚无对应审核术语；Phase1 Rule 尚无对应审核规则。
- 喜用神分体系治理：Terms 尚无对应审核术语；Phase1 Rule 尚无对应审核规则。
- 大运：Terms 尚无对应审核术语；Phase1 Rule 尚无对应审核规则。
- 流年与岁运作用：Terms `bazi.term.branch_triple_harmonies`；Phase1 Rule `bazi.rule.r010`。
- 事业财富专题：Terms 尚无对应审核术语；Phase1 Rule 尚无对应审核规则。

已有 Phase2 / Golden / Variant：

- `bazi.phase2.pillars` / `ziping-structural-v1`；Golden：`bazi.structural-basic`；测试 `tests/test_phase2_bazi.py`。
  Evidence C：`bazi.source.yuanhai` / 渊海子平 / 喜忌篇 / `《渊海子平》喜忌篇；本轮固定短引`，引文：四柱排定,三才次分,专以日上天元,配合八字支干;有见不见之形,无时不有;神煞相绊,轻重较量。。
- `bazi.phase2.ten_gods` / `ziping-structural-v1`；Golden：`bazi.structural-basic`；测试 `tests/test_phase2_bazi.py`。
  Evidence C：`bazi.source.yuanhai` / 渊海子平 / 基础与藏遁 / `《渊海子平》基础；本轮固定短引`，引文：以甲为例★见甲:为比肩、兄弟。
 见乙:为劫财、败财,剋父及妻。
 见丙:为食神、天厨、寿星,为男。
 见丁:为伤官、退财、耗气,子甥。
 见戊:为偏财、偏妻、偏妾,剋子。
 见己:为正财、正妻,剋母,为合神。
 见庚:为偏官、七杀、官鬼、将星。
 见辛:为正官、禄马、荣神,父母。
 见壬:为倒食、偏印、梟神,剋女。
 见癸:为印綬、正人、君子,产业。。
  Evidence C：`bazi.source.yuanhai` / 渊海子平 / 基础与藏遁 / `《渊海子平》基础；本轮固定短引`，引文：以乙为例★见甲:为劫财、逐马,剋妻。
 见乙:为比肩、兄弟、朋友。
 见丙:为伤官、小人、盗气,为姪。
 见丁:为食神、天厨、寿星,子孙。
 见戊:为正财、正妻,剋母。
 见己:为偏财、偏妻、偏妾,剋子。
 见庚:为正官、禄马,剋父母。
 见辛:为偏官、七杀、官鬼,媒人。
 见壬:为印綬、正人、君子,忌杀。
 见癸:为倒食、偏印、梟神,剋母。。
  Evidence C：`bazi.source.yuanhai` / 渊海子平 / 十神关系选段 / `《渊海子平》论伤官；本轮固定短引`，引文：又云,伤官者,我生彼之谓也;以阳见阴,阴见阳,亦名盗气。。
  Evidence C：`bazi.source.yuanhai` / 渊海子平 / 十神关系选段 / `《渊海子平》论正财；本轮固定短引`，引文：何谓之正财?犹如正官之意;是阴见阳财,阳见阴财。。
  Evidence C：`bazi.source.yuanhai` / 渊海子平 / 十神关系选段 / `《渊海子平》正官论；本轮固定短引`，引文：夫正官者,甲见辛之类;乃阴见阳为官,阳见阴为鬼,阴阳配合成其道也。。
  Evidence C：`bazi.source.yuanhai` / 渊海子平 / 十神关系选段 / `《渊海子平》论印绶；本轮固定短引`，引文：夫印綬者,生我之谓也,亦名生气。以阳见阴,以阴见阳,谓之正印;阳见阳,阴见阴,谓之偏印。。
- `bazi.phase2.hidden_stems` / `ziping-structural-v1`；Golden：`bazi.structural-basic`；测试 `tests/test_phase2_bazi.py`。
  Evidence C：`bazi.source.yuanhai` / 渊海子平 / 基础与藏遁 / `《渊海子平》又地支藏遁歌；本轮固定短引`，引文：子宫癸水在其中,丑癸辛金己土同;寅宫甲木兼丙戊,卯宫乙木独相逢。辰藏乙戊三分癸,巳中庚金丙戊丛;午宫丁火并己土,未宫乙己丁共宗。申位庚金壬水戊,酉宫辛金独丰隆;戌宫辛金及丁戊,亥藏壬甲是真踪。。
- `bazi.phase2.month_command_factors` / `ziping-structural-v1`；Golden：`bazi.factors-normal`, `bazi.factors-tomb-boundary`, `bazi.factors-many-stems-no-root`, `bazi.factors-few-stems-with-root`, `bazi.factors-clash-not-erasure`, `bazi.factors-siling-unresolved`；测试 `tests/test_phase2_bazistrength.py`。
  Evidence C：`bazi.source.ditiansui-spouse` / 滴天髓阐微 / 月令、通根与透藏观察边界 / `《滴天髓阐微》通神论·月令；固定原文字符位置 37963；月令提纲`，引文：月令乃提纲之府,譬之宅也,人元为用事之神,宅之定向也,不可以不卜。。
  Evidence C：`bazi.source.ditiansui-spouse` / 滴天髓阐微 / 月令、通根与透藏观察边界 / `《滴天髓阐微》通神论·月令；固定原文字符位置 38056；寅月司令分日`，引文：如寅月生人,立春后七日前,皆值戊土用事;八日后十四日前者,丙火用事 ;十五日后,甲木用事。。
  Evidence C：`bazi.source.ditiansui-spouse` / 滴天髓阐微 / 月令、通根与透藏观察边界 / `《滴天髓阐微》通神论·衰旺；固定原文字符位置 39648；不可得令即旺失令即弱`，引文：得时俱为旺论,失令便作衰看,虽是至理,亦死法也。。
  Evidence C：`bazi.source.yuanhai` / 渊海子平 / 基础与藏遁 / `《渊海子平》又地支藏遁歌；本轮固定短引`，引文：子宫癸水在其中,丑癸辛金己土同;寅宫甲木兼丙戊,卯宫乙木独相逢。辰藏乙戊三分癸,巳中庚金丙戊丛;午宫丁火并己土,未宫乙己丁共宗。申位庚金壬水戊,酉宫辛金独丰隆;戌宫辛金及丁戊,亥藏壬甲是真踪。。
- `bazi.phase2.root_candidates` / `ziping-structural-v1`；Golden：`bazi.factors-normal`, `bazi.factors-tomb-boundary`, `bazi.factors-many-stems-no-root`, `bazi.factors-few-stems-with-root`, `bazi.factors-clash-not-erasure`, `bazi.factors-siling-unresolved`；测试 `tests/test_phase2_bazistrength.py`。
  Evidence C：`bazi.source.ditiansui-spouse` / 滴天髓阐微 / 月令、通根与透藏观察边界 / `《滴天髓阐微》通神论·衰旺；固定原文字符位置 39989；比肩与地支根不可数量等同`，引文：天干得一比肩,不如地支得一余气墓库。。
  Evidence C：`bazi.source.ditiansui-spouse` / 滴天髓阐微 / 月令、通根与透藏观察边界 / `《滴天髓阐微》通神论·衰旺；固定原文字符位置 40063；余气与长生禄旺根示例`，引文：余气者,如丙丁逢未,甲乙逢辰,庚辛逢戌,壬癸逢丑之类是也,得二比肩,不如支中得一长生禄旺,如甲乙逢亥寅卯之类是也。。
  Evidence C：`bazi.source.ditiansui-spouse` / 滴天髓阐微 / 月令、通根与透藏观察边界 / `《滴天髓阐微》通神论·衰旺；固定原文字符位置 39648；不可得令即旺失令即弱`，引文：得时俱为旺论,失令便作衰看,虽是至理,亦死法也。。
  Evidence C：`bazi.source.yuanhai` / 渊海子平 / 基础与藏遁 / `《渊海子平》又地支藏遁歌；本轮固定短引`，引文：子宫癸水在其中,丑癸辛金己土同;寅宫甲木兼丙戊,卯宫乙木独相逢。辰藏乙戊三分癸,巳中庚金丙戊丛;午宫丁火并己土,未宫乙己丁共宗。申位庚金壬水戊,酉宫辛金独丰隆;戌宫辛金及丁戊,亥藏壬甲是真踪。。
- `bazi.phase2.hidden_to_visible` / `ziping-structural-v1`；Golden：`bazi.factors-normal`, `bazi.factors-tomb-boundary`, `bazi.factors-many-stems-no-root`, `bazi.factors-few-stems-with-root`, `bazi.factors-clash-not-erasure`, `bazi.factors-siling-unresolved`；测试 `tests/test_phase2_bazistrength.py`。
  Evidence C：`bazi.source.ditiansui-spouse` / 滴天髓阐微 / 月令、通根与透藏观察边界 / `《滴天髓阐微》通神论·月令；固定原文字符位置 38284；藏干与显干引助`，引文：故知地支人元必得天干引助,天干为用,必要地支司令。。
  Evidence C：`bazi.source.yuanhai` / 渊海子平 / 基础与藏遁 / `《渊海子平》又地支藏遁歌；本轮固定短引`，引文：子宫癸水在其中,丑癸辛金己土同;寅宫甲木兼丙戊,卯宫乙木独相逢。辰藏乙戊三分癸,巳中庚金丙戊丛;午宫丁火并己土,未宫乙己丁共宗。申位庚金壬水戊,酉宫辛金独丰隆;戌宫辛金及丁戊,亥藏壬甲是真踪。。
- `bazi.phase2.support_relations` / `ziping-structural-v1`；Golden：`bazi.support-normal`, `bazi.support-yin`, `bazi.support-visible-peers`, `bazi.support-conflict`；测试 `tests/test_phase2_bazisupport.py`。
  Evidence C：`bazi.source.yuanhai` / 渊海子平 / 生克关系与效力界限 / `《渊海子平》五行相生及条件界限；固定原文字符位置 964`，引文：金能生水,水多金沉;水能生木,木盛水缩;木能生火,火多木焚;火能生土,土多火埋;土能生金,金多土变。。
  Evidence C：`bazi.source.yuanhai` / 渊海子平 / 生克关系与效力界限 / `《渊海子平》五行相克及条件界限；固定原文字符位置 1016`，引文：金能剋木,木坚金缺;木能剋土,土重木折;土能剋水,水多土流;水能剋火,火多水热;火能剋金,金多火熄。。
  Evidence C：`bazi.source.ditiansui-spouse` / 滴天髓阐微 / 天干阴阳五行分类 / `《滴天髓阐微·审核短引》十干阴阳短引；固定原文字符位置 4991`，引文：甲、丙、戊、庚、壬为阳,独丙火秉阳之精,而为阳中之阳;乙、丁、己、辛、癸为阴,独癸水秉阴之精,而为阴中之阴。。
  Evidence C：`bazi.source.ditiansui-spouse` / 滴天髓阐微 / 天干阴阳五行分类 / `《滴天髓阐微·审核短引》十干五行短引；固定原文字符位置 5159`，引文：甲乙一木也,丙丁一火也,戊己一土也,庚辛一金也,壬癸一水也,即分别所用,不过阳刚阴柔,阳健阴顺而已。。
  Evidence C：`bazi.source.yuanhai` / 渊海子平 / 基础与藏遁 / `《渊海子平》基础；本轮固定短引`，引文：以甲为例★见甲:为比肩、兄弟。
 见乙:为劫财、败财,剋父及妻。
 见丙:为食神、天厨、寿星,为男。
 见丁:为伤官、退财、耗气,子甥。
 见戊:为偏财、偏妻、偏妾,剋子。
 见己:为正财、正妻,剋母,为合神。
 见庚:为偏官、七杀、官鬼、将星。
 见辛:为正官、禄马、荣神,父母。
 见壬:为倒食、偏印、梟神,剋女。
 见癸:为印綬、正人、君子,产业。。
  Evidence C：`bazi.source.yuanhai` / 渊海子平 / 基础与藏遁 / `《渊海子平》基础；本轮固定短引`，引文：以乙为例★见甲:为劫财、逐马,剋妻。
 见乙:为比肩、兄弟、朋友。
 见丙:为伤官、小人、盗气,为姪。
 见丁:为食神、天厨、寿星,子孙。
 见戊:为正财、正妻,剋母。
 见己:为偏财、偏妻、偏妾,剋子。
 见庚:为正官、禄马,剋父母。
 见辛:为偏官、七杀、官鬼,媒人。
 见壬:为印綬、正人、君子,忌杀。
 见癸:为倒食、偏印、梟神,剋母。。
  Evidence C：`bazi.source.yuanhai` / 渊海子平 / 十神关系选段 / `《渊海子平》论伤官；本轮固定短引`，引文：又云,伤官者,我生彼之谓也;以阳见阴,阴见阳,亦名盗气。。
  Evidence C：`bazi.source.yuanhai` / 渊海子平 / 十神关系选段 / `《渊海子平》论正财；本轮固定短引`，引文：何谓之正财?犹如正官之意;是阴见阳财,阳见阴财。。
  Evidence C：`bazi.source.yuanhai` / 渊海子平 / 十神关系选段 / `《渊海子平》正官论；本轮固定短引`，引文：夫正官者,甲见辛之类;乃阴见阳为官,阳见阴为鬼,阴阳配合成其道也。。
  Evidence C：`bazi.source.yuanhai` / 渊海子平 / 十神关系选段 / `《渊海子平》论印绶；本轮固定短引`，引文：夫印綬者,生我之谓也,亦名生气。以阳见阴,以阴见阳,谓之正印;阳见阳,阴见阴,谓之偏印。。
  Evidence C：`bazi.source.yuanhai` / 渊海子平 / 基础与藏遁 / `《渊海子平》又地支藏遁歌；本轮固定短引`，引文：子宫癸水在其中,丑癸辛金己土同;寅宫甲木兼丙戊,卯宫乙木独相逢。辰藏乙戊三分癸,巳中庚金丙戊丛;午宫丁火并己土,未宫乙己丁共宗。申位庚金壬水戊,酉宫辛金独丰隆;戌宫辛金及丁戊,亥藏壬甲是真踪。。

当前场景可输出结论（只描述事实，不追加吉凶含义）：

- `career.ten_god_positions`：READY；匹配 `bazi.scenario.career_wealth_structure`，事实路径 `/`；deterministic_structure_only。

当前禁止结论：发财保证；事业升迁应期；财星多即富；财多身弱判断。

缺失能力 / 依赖 / 下一批：

- `bazi-foundation`：十干阴阳五行、生克方向及四柱/日主/十神/藏干已有审核短引、执行与 Golden；仍缺十二长生、季节实际效力及基础结构到个人结论的条件规则，真太阳时未实现；旧表权重不作通用结论。
  下一批从 `data/canonical/classics/bazi/ditiansui_chanwei_v1.json#/sections/0/text` 核短引、条件和反例；全文命中仅是待审定位，不是 Evidence。
- `bazi-ten-gods`：映射不等于组合、位置、透藏、月令条件下的解释；须补原典规则、限制及反例。
  下一批从 `data/canonical/classics/bazi/ditiansui_chanwei_v1.json#/sections/6/text` 核短引、条件和反例；全文命中仅是待审定位，不是 Evidence。
- `bazi-strength`：月令/通根候选/透藏/生克方向位置 v1 已按原模型执行，含正常/阴日干/多比肩不判强/冲克不定凶及分日冲突反例。整体强弱仍缺季节司令、根力、得势、生扶克泄耗效力与从化边界，不以数量或自创权重填补。
  下一批从 `data/canonical/classics/bazi/ditiansui_chanwei_v1.json#/sections/2/text` 核短引、条件和反例；全文命中仅是待审定位，不是 Evidence。
- `bazi-pattern`：正文提及不等于结构规则；缺成格/破格/兼格条件、流派限制和 Golden。
  下一批从 `data/canonical/classics/bazi/ditiansui_chanwei_v1.json#/sections/7/text` 核短引、条件和反例；全文命中仅是待审定位，不是 Evidence。
- `bazi-useful-god`：调候、扶抑、病药、格局用神未分别治理；依赖旺衰与格局；禁止输出喜用木火等具体结论。
  下一批先登记来源及权利，保存 RAW/Quarantine；无审核引文时保持未支持。
- `bazi-dayun`：旧说明不是执行；须核顺逆/起运法/节界/岁数换算/原局作用及不同 Variant。
  下一批从 `data/canonical/classics/bazi/ditiansui_chanwei_v1.json#/sections/3/text` 核短引、条件和反例；全文命中仅是待审定位，不是 Evidence。
- `bazi-annual`：日历干支不等于运势；缺原局、大运、流年作用图及强弱/喜忌条件规则。
  下一批从 `data/canonical/classics/bazi/ditiansui_chanwei_v1.json#/sections/1/text` 核短引、条件和反例；全文命中仅是待审定位，不是 Evidence。
- `bazi-career-wealth`：缺组合、位置、强弱、格局、岁运解释规则；财多身弱须先完成旺衰，不能用财星数量推财富。
  下一批从 `data/canonical/classics/bazi/ditiansui_chanwei_v1.json#/sections/3/text` 核短引、条件和反例；全文命中仅是待审定位，不是 Evidence。

## 缘分合盘 · PRODUCTIZABLE

Scenario：`compatibility`；已执行=True；现有结构公开标志=False；AI=false。

已有知识、Rule 与 Evidence：

- 八字基础与十神映射：Terms `bazi.term.day_master`, `bazi.term.ten_gods`, `bazi.term.hidden_stems`, `bazi.term.month_command`, `bazi.term.root_candidates`, `bazi.term.hidden_to_visible`, `bazi.term.heavenly_stems`, `bazi.term.stem_polarity`, `bazi.term.five_elements`, `bazi.term.generation_control`；Phase1 Rule `bazi.rule.r001`, `bazi.rule.r002`, `bazi.rule.r003`, `bazi.rule.r011`, `bazi.rule.r012`, `bazi.rule.r013`, `bazi.rule.r014`, `bazi.rule.r015`, `bazi.rule.r016`。
- 旺衰及流派边界：Terms `bazi.term.strength_review_boundary`, `bazi.term.month_command`, `bazi.term.root_candidates`, `bazi.term.hidden_to_visible`；Phase1 Rule `bazi.rule.r012`, `bazi.rule.r013`, `bazi.rule.r014`, `bazi.rule.r015`。
- 婚恋专题：Terms `bazi.term.xianchi`, `bazi.term.stem_five_combinations`, `bazi.term.branch_six_harmonies`, `bazi.term.branch_six_harms`, `bazi.term.spouse_palace_day_branch`, `bazi.term.branch_six_clashes`, `bazi.term.branch_triple_harmonies`, `bazi.term.traditional_spouse_star_lens`；Phase1 Rule `bazi.rule.r004`, `bazi.rule.r005`, `bazi.rule.r006`, `bazi.rule.r007`, `bazi.rule.r008`, `bazi.rule.r009`, `bazi.rule.r010`, `bazi.rule.r011`。
- 流年与岁运作用：Terms `bazi.term.branch_triple_harmonies`；Phase1 Rule `bazi.rule.r010`。
- 双人关系：Terms `bazi.term.day_master`, `bazi.term.ten_gods`, `bazi.term.xianchi`, `bazi.term.stem_five_combinations`, `bazi.term.branch_six_harmonies`, `bazi.term.branch_six_harms`, `bazi.term.spouse_palace_day_branch`, `bazi.term.branch_six_clashes`, `bazi.term.branch_triple_harmonies`, `bazi.term.traditional_spouse_star_lens`；Phase1 Rule `bazi.rule.r001`, `bazi.rule.r002`, `bazi.rule.r003`, `bazi.rule.r004`, `bazi.rule.r005`, `bazi.rule.r006`, `bazi.rule.r007`, `bazi.rule.r008`, `bazi.rule.r009`, `bazi.rule.r010`, `bazi.rule.r011`, `bazi.rule.r012`, `bazi.rule.r013`, `bazi.rule.r014`, `bazi.rule.r015`, `bazi.rule.r016`。

已有 Phase2 / Golden / Variant：

- `bazi.phase2.pillars` / `ziping-structural-v1`；Golden：`bazi.structural-basic`；测试 `tests/test_phase2_bazi.py`。
  Evidence C：`bazi.source.yuanhai` / 渊海子平 / 喜忌篇 / `《渊海子平》喜忌篇；本轮固定短引`，引文：四柱排定,三才次分,专以日上天元,配合八字支干;有见不见之形,无时不有;神煞相绊,轻重较量。。
- `bazi.phase2.ten_gods` / `ziping-structural-v1`；Golden：`bazi.structural-basic`；测试 `tests/test_phase2_bazi.py`。
  Evidence C：`bazi.source.yuanhai` / 渊海子平 / 基础与藏遁 / `《渊海子平》基础；本轮固定短引`，引文：以甲为例★见甲:为比肩、兄弟。
 见乙:为劫财、败财,剋父及妻。
 见丙:为食神、天厨、寿星,为男。
 见丁:为伤官、退财、耗气,子甥。
 见戊:为偏财、偏妻、偏妾,剋子。
 见己:为正财、正妻,剋母,为合神。
 见庚:为偏官、七杀、官鬼、将星。
 见辛:为正官、禄马、荣神,父母。
 见壬:为倒食、偏印、梟神,剋女。
 见癸:为印綬、正人、君子,产业。。
  Evidence C：`bazi.source.yuanhai` / 渊海子平 / 基础与藏遁 / `《渊海子平》基础；本轮固定短引`，引文：以乙为例★见甲:为劫财、逐马,剋妻。
 见乙:为比肩、兄弟、朋友。
 见丙:为伤官、小人、盗气,为姪。
 见丁:为食神、天厨、寿星,子孙。
 见戊:为正财、正妻,剋母。
 见己:为偏财、偏妻、偏妾,剋子。
 见庚:为正官、禄马,剋父母。
 见辛:为偏官、七杀、官鬼,媒人。
 见壬:为印綬、正人、君子,忌杀。
 见癸:为倒食、偏印、梟神,剋母。。
  Evidence C：`bazi.source.yuanhai` / 渊海子平 / 十神关系选段 / `《渊海子平》论伤官；本轮固定短引`，引文：又云,伤官者,我生彼之谓也;以阳见阴,阴见阳,亦名盗气。。
  Evidence C：`bazi.source.yuanhai` / 渊海子平 / 十神关系选段 / `《渊海子平》论正财；本轮固定短引`，引文：何谓之正财?犹如正官之意;是阴见阳财,阳见阴财。。
  Evidence C：`bazi.source.yuanhai` / 渊海子平 / 十神关系选段 / `《渊海子平》正官论；本轮固定短引`，引文：夫正官者,甲见辛之类;乃阴见阳为官,阳见阴为鬼,阴阳配合成其道也。。
  Evidence C：`bazi.source.yuanhai` / 渊海子平 / 十神关系选段 / `《渊海子平》论印绶；本轮固定短引`，引文：夫印綬者,生我之谓也,亦名生气。以阳见阴,以阴见阳,谓之正印;阳见阳,阴见阴,谓之偏印。。
- `bazi.phase2.hidden_stems` / `ziping-structural-v1`；Golden：`bazi.structural-basic`；测试 `tests/test_phase2_bazi.py`。
  Evidence C：`bazi.source.yuanhai` / 渊海子平 / 基础与藏遁 / `《渊海子平》又地支藏遁歌；本轮固定短引`，引文：子宫癸水在其中,丑癸辛金己土同;寅宫甲木兼丙戊,卯宫乙木独相逢。辰藏乙戊三分癸,巳中庚金丙戊丛;午宫丁火并己土,未宫乙己丁共宗。申位庚金壬水戊,酉宫辛金独丰隆;戌宫辛金及丁戊,亥藏壬甲是真踪。。
- `bazi.phase2.xianchi_lookup` / `ziping-structural-v1`；Golden：`bazi.xianchi-explicit-dual-basis`；测试 `tests/test_phase2_bazi.py`。
  Evidence C：`bazi.source.sanming-xianchi-niutrans` / 三命通会 / 卷二·论咸池 / `《三命通会》卷二·论咸池；固定短引`，引文：《淮南子》曰： 日出扶桑，入于咸池。 故五行沐浴之地，名咸池。是取日人之义，万物暗昧之时。寅午戌卯、已酉丑午、申子辰酉、亥卯未子即长生第二位沐浴之宫是也。一名败神，一名桃花煞。
- `bazi.phase2.stem_five_combinations` / `ziping-structural-v1`；Golden：`bazi.relations-core`；测试 `tests/test_phase2_bazi.py`。
  Evidence C：`bazi.source.xieji-relations` / 钦定协纪辨方书 / 五合六合六害结构短引 / `《钦定协纪辨方书》卷一·五合；固定短引`，引文：甲与己合乙与庚合丙与辛合丁与壬合戊与癸合。
- `bazi.phase2.branch_six_harmonies` / `ziping-structural-v1`；Golden：`bazi.relations-core`；测试 `tests/test_phase2_bazi.py`。
  Evidence C：`bazi.source.xieji-relations` / 钦定协纪辨方书 / 五合六合六害结构短引 / `《钦定协纪辨方书》卷一·六合；固定短引`，引文：子与丑合寅与亥合卯与戌合辰与酉合巳与申合午与未合。
- `bazi.phase2.branch_six_harms` / `ziping-structural-v1`；Golden：`bazi.relations-core`；测试 `tests/test_phase2_bazi.py`。
  Evidence C：`bazi.source.xieji-relations` / 钦定协纪辨方书 / 五合六合六害结构短引 / `《钦定协纪辨方书》月害条；固定短引`，引文：月害者月中六害也假令夘辰相害者夘以乙旺之木害辰墓之土辰以墓土却害夘中癸水也寅巳相害者谓寅以旺甲害巳中戊土而巳以生庚害寅中旺甲也丑午相害者丑以癸水害午中丁火午以巳土害丑中癸水也子未相害者子以所生之辛金害未中墓木未以旺土害子中旺水也申亥相害者亥以生木害申中生土申以旺金害亥中生木又以生土害亥中旺水也酉戌相害者戌以墓火害酉之旺金酉以所生丁火害戌中辛金也。
- `bazi.phase2.spouse_palace_day_branch` / `ziping-structural-v1`；Golden：`bazi.relations-core`；测试 `tests/test_phase2_bazi.py`。
  Evidence C：`bazi.source.yuanhai` / 渊海子平 / 络绎赋·日支妻位 / `《渊海子平》络绎赋；固定短引`，引文：年干父兮支母。
 日干己兮支妻。
 月干兄兮支弟。
 时支女兮干儿。。
- `bazi.phase2.branch_six_clashes` / `ziping-structural-v1`；Golden：`bazi.relations-expanded`；测试 `tests/test_phase2_bazi.py`。
  Evidence C：`bazi.source.xieji-relations` / 钦定协纪辨方书 / 五合六合六害结构短引 / `《钦定协纪辨方书》月建相关条；固定短引`，引文：洞源经曰对七为冲隔三为破选择家所谓辰破丑而丑冲未亥破寅而寅冲申午破夘而夘冲酉酉破子而子冲午申破巳而巳冲亥戌破未而未冲丑是也。
  Evidence C：`bazi.source.xieji-relations` / 钦定协纪辨方书 / 五合六合六害结构短引 / `《钦定协纪辨方书》月建相关条；固定短引`，引文：假如建在子前三为平为夘后三为收为酉夘酉冲也建在丑前三为平为辰后三为收为戌辰戌冲也推之十二辰莫不皆然。
- `bazi.phase2.branch_triple_harmonies` / `ziping-structural-v1`；Golden：`bazi.relations-expanded`；测试 `tests/test_phase2_bazi.py`。
  Evidence C：`bazi.source.xieji-relations` / 钦定协纪辨方书 / 五合六合六害结构短引 / `《钦定协纪辨方书》大煞条；固定短引`，引文：考原曰大煞子年在子丑年在酉寅年在午夘年在夘辰年又在子如是逆行四正盖申子辰三合为水水旺于子也巳酉丑三合为金金旺于酉也寅午戌三合为火火旺于午也亥夘未三合为木木旺于夘也。
- `bazi.phase2.spouse_star_lens` / `ziping-structural-v1`；Golden：`bazi.spouse-star-lens-male`, `bazi.spouse-star-lens-female`；测试 `tests/test_phase2_bazi.py`。
  Evidence C：`bazi.source.yuanhai` / 渊海子平 / 传统配偶星观察口径 / `《渊海子平》六亲总篇；固定短引`，引文：用日干为主:正印正母;偏印偏母及祖父也;偏财是父,乃母之夫星也,亦为偏妻;正财为妻;偏财为妾,为父是也;比肩为兄弟姐妹也;七杀是男;正官是女;食神是男孙;伤官是女孙及祖母也。
 妇人命取六亲,与男命不同:取官星为夫星;七杀是偏夫;食神是男;伤官是女。。
  Evidence C：`bazi.source.ditiansui-spouse` / 滴天髓阐微 / 夫妻与女命观察边界 / `《滴天髓阐微》六亲论·女命章；固定短引`，引文：不必专执官星而论夫。专执伤食而论子。但以安祥顺静为贵,二德三奇不必论,咸池驿马纵有验,总之于理不长。其中究论,不可不详。。
  Evidence C：`bazi.source.ditiansui-spouse` / 滴天髓阐微 / 夫妻与女命观察边界 / `《滴天髓阐微》六亲论·夫妻；固定短引`，引文：子平之法,以财为妻,财是我克。人以财来侍我,此理出于正论。
- `bazi.phase2.month_command_factors` / `ziping-structural-v1`；Golden：`bazi.factors-normal`, `bazi.factors-tomb-boundary`, `bazi.factors-many-stems-no-root`, `bazi.factors-few-stems-with-root`, `bazi.factors-clash-not-erasure`, `bazi.factors-siling-unresolved`；测试 `tests/test_phase2_bazistrength.py`。
  Evidence C：`bazi.source.ditiansui-spouse` / 滴天髓阐微 / 月令、通根与透藏观察边界 / `《滴天髓阐微》通神论·月令；固定原文字符位置 37963；月令提纲`，引文：月令乃提纲之府,譬之宅也,人元为用事之神,宅之定向也,不可以不卜。。
  Evidence C：`bazi.source.ditiansui-spouse` / 滴天髓阐微 / 月令、通根与透藏观察边界 / `《滴天髓阐微》通神论·月令；固定原文字符位置 38056；寅月司令分日`，引文：如寅月生人,立春后七日前,皆值戊土用事;八日后十四日前者,丙火用事 ;十五日后,甲木用事。。
  Evidence C：`bazi.source.ditiansui-spouse` / 滴天髓阐微 / 月令、通根与透藏观察边界 / `《滴天髓阐微》通神论·衰旺；固定原文字符位置 39648；不可得令即旺失令即弱`，引文：得时俱为旺论,失令便作衰看,虽是至理,亦死法也。。
  Evidence C：`bazi.source.yuanhai` / 渊海子平 / 基础与藏遁 / `《渊海子平》又地支藏遁歌；本轮固定短引`，引文：子宫癸水在其中,丑癸辛金己土同;寅宫甲木兼丙戊,卯宫乙木独相逢。辰藏乙戊三分癸,巳中庚金丙戊丛;午宫丁火并己土,未宫乙己丁共宗。申位庚金壬水戊,酉宫辛金独丰隆;戌宫辛金及丁戊,亥藏壬甲是真踪。。
- `bazi.phase2.root_candidates` / `ziping-structural-v1`；Golden：`bazi.factors-normal`, `bazi.factors-tomb-boundary`, `bazi.factors-many-stems-no-root`, `bazi.factors-few-stems-with-root`, `bazi.factors-clash-not-erasure`, `bazi.factors-siling-unresolved`；测试 `tests/test_phase2_bazistrength.py`。
  Evidence C：`bazi.source.ditiansui-spouse` / 滴天髓阐微 / 月令、通根与透藏观察边界 / `《滴天髓阐微》通神论·衰旺；固定原文字符位置 39989；比肩与地支根不可数量等同`，引文：天干得一比肩,不如地支得一余气墓库。。
  Evidence C：`bazi.source.ditiansui-spouse` / 滴天髓阐微 / 月令、通根与透藏观察边界 / `《滴天髓阐微》通神论·衰旺；固定原文字符位置 40063；余气与长生禄旺根示例`，引文：余气者,如丙丁逢未,甲乙逢辰,庚辛逢戌,壬癸逢丑之类是也,得二比肩,不如支中得一长生禄旺,如甲乙逢亥寅卯之类是也。。
  Evidence C：`bazi.source.ditiansui-spouse` / 滴天髓阐微 / 月令、通根与透藏观察边界 / `《滴天髓阐微》通神论·衰旺；固定原文字符位置 39648；不可得令即旺失令即弱`，引文：得时俱为旺论,失令便作衰看,虽是至理,亦死法也。。
  Evidence C：`bazi.source.yuanhai` / 渊海子平 / 基础与藏遁 / `《渊海子平》又地支藏遁歌；本轮固定短引`，引文：子宫癸水在其中,丑癸辛金己土同;寅宫甲木兼丙戊,卯宫乙木独相逢。辰藏乙戊三分癸,巳中庚金丙戊丛;午宫丁火并己土,未宫乙己丁共宗。申位庚金壬水戊,酉宫辛金独丰隆;戌宫辛金及丁戊,亥藏壬甲是真踪。。
- `bazi.phase2.hidden_to_visible` / `ziping-structural-v1`；Golden：`bazi.factors-normal`, `bazi.factors-tomb-boundary`, `bazi.factors-many-stems-no-root`, `bazi.factors-few-stems-with-root`, `bazi.factors-clash-not-erasure`, `bazi.factors-siling-unresolved`；测试 `tests/test_phase2_bazistrength.py`。
  Evidence C：`bazi.source.ditiansui-spouse` / 滴天髓阐微 / 月令、通根与透藏观察边界 / `《滴天髓阐微》通神论·月令；固定原文字符位置 38284；藏干与显干引助`，引文：故知地支人元必得天干引助,天干为用,必要地支司令。。
  Evidence C：`bazi.source.yuanhai` / 渊海子平 / 基础与藏遁 / `《渊海子平》又地支藏遁歌；本轮固定短引`，引文：子宫癸水在其中,丑癸辛金己土同;寅宫甲木兼丙戊,卯宫乙木独相逢。辰藏乙戊三分癸,巳中庚金丙戊丛;午宫丁火并己土,未宫乙己丁共宗。申位庚金壬水戊,酉宫辛金独丰隆;戌宫辛金及丁戊,亥藏壬甲是真踪。。
- `bazi.phase2.support_relations` / `ziping-structural-v1`；Golden：`bazi.support-normal`, `bazi.support-yin`, `bazi.support-visible-peers`, `bazi.support-conflict`；测试 `tests/test_phase2_bazisupport.py`。
  Evidence C：`bazi.source.yuanhai` / 渊海子平 / 生克关系与效力界限 / `《渊海子平》五行相生及条件界限；固定原文字符位置 964`，引文：金能生水,水多金沉;水能生木,木盛水缩;木能生火,火多木焚;火能生土,土多火埋;土能生金,金多土变。。
  Evidence C：`bazi.source.yuanhai` / 渊海子平 / 生克关系与效力界限 / `《渊海子平》五行相克及条件界限；固定原文字符位置 1016`，引文：金能剋木,木坚金缺;木能剋土,土重木折;土能剋水,水多土流;水能剋火,火多水热;火能剋金,金多火熄。。
  Evidence C：`bazi.source.ditiansui-spouse` / 滴天髓阐微 / 天干阴阳五行分类 / `《滴天髓阐微·审核短引》十干阴阳短引；固定原文字符位置 4991`，引文：甲、丙、戊、庚、壬为阳,独丙火秉阳之精,而为阳中之阳;乙、丁、己、辛、癸为阴,独癸水秉阴之精,而为阴中之阴。。
  Evidence C：`bazi.source.ditiansui-spouse` / 滴天髓阐微 / 天干阴阳五行分类 / `《滴天髓阐微·审核短引》十干五行短引；固定原文字符位置 5159`，引文：甲乙一木也,丙丁一火也,戊己一土也,庚辛一金也,壬癸一水也,即分别所用,不过阳刚阴柔,阳健阴顺而已。。
  Evidence C：`bazi.source.yuanhai` / 渊海子平 / 基础与藏遁 / `《渊海子平》基础；本轮固定短引`，引文：以甲为例★见甲:为比肩、兄弟。
 见乙:为劫财、败财,剋父及妻。
 见丙:为食神、天厨、寿星,为男。
 见丁:为伤官、退财、耗气,子甥。
 见戊:为偏财、偏妻、偏妾,剋子。
 见己:为正财、正妻,剋母,为合神。
 见庚:为偏官、七杀、官鬼、将星。
 见辛:为正官、禄马、荣神,父母。
 见壬:为倒食、偏印、梟神,剋女。
 见癸:为印綬、正人、君子,产业。。
  Evidence C：`bazi.source.yuanhai` / 渊海子平 / 基础与藏遁 / `《渊海子平》基础；本轮固定短引`，引文：以乙为例★见甲:为劫财、逐马,剋妻。
 见乙:为比肩、兄弟、朋友。
 见丙:为伤官、小人、盗气,为姪。
 见丁:为食神、天厨、寿星,子孙。
 见戊:为正财、正妻,剋母。
 见己:为偏财、偏妻、偏妾,剋子。
 见庚:为正官、禄马,剋父母。
 见辛:为偏官、七杀、官鬼,媒人。
 见壬:为印綬、正人、君子,忌杀。
 见癸:为倒食、偏印、梟神,剋母。。
  Evidence C：`bazi.source.yuanhai` / 渊海子平 / 十神关系选段 / `《渊海子平》论伤官；本轮固定短引`，引文：又云,伤官者,我生彼之谓也;以阳见阴,阴见阳,亦名盗气。。
  Evidence C：`bazi.source.yuanhai` / 渊海子平 / 十神关系选段 / `《渊海子平》论正财；本轮固定短引`，引文：何谓之正财?犹如正官之意;是阴见阳财,阳见阴财。。
  Evidence C：`bazi.source.yuanhai` / 渊海子平 / 十神关系选段 / `《渊海子平》正官论；本轮固定短引`，引文：夫正官者,甲见辛之类;乃阴见阳为官,阳见阴为鬼,阴阳配合成其道也。。
  Evidence C：`bazi.source.yuanhai` / 渊海子平 / 十神关系选段 / `《渊海子平》论印绶；本轮固定短引`，引文：夫印綬者,生我之谓也,亦名生气。以阳见阴,以阴见阳,谓之正印;阳见阳,阴见阴,谓之偏印。。
  Evidence C：`bazi.source.yuanhai` / 渊海子平 / 基础与藏遁 / `《渊海子平》又地支藏遁歌；本轮固定短引`，引文：子宫癸水在其中,丑癸辛金己土同;寅宫甲木兼丙戊,卯宫乙木独相逢。辰藏乙戊三分癸,巳中庚金丙戊丛;午宫丁火并己土,未宫乙己丁共宗。申位庚金壬水戊,酉宫辛金独丰隆;戌宫辛金及丁戊,亥藏壬甲是真踪。。

当前场景可输出结论（只描述事实，不追加吉凶含义）：

- `compatibility.a_sees_b`：READY；匹配 `bazi.scenario.compatibility_structure`，事实路径 `/a_sees_b_ten_god`；deterministic_structure_only。
- `compatibility.b_sees_a`：READY；匹配 `bazi.scenario.compatibility_structure`，事实路径 `/b_sees_a_ten_god`；deterministic_structure_only。
- `relationship.stem_combination`：READY；匹配 `bazi.scenario.compatibility_structure`，事实路径 `/day_master_five_combination`；deterministic_structure_only。
- `relationship.branch_clash`：READY；匹配 `bazi.scenario.compatibility_structure`，事实路径 `/spouse_palace_relation/relations`；deterministic_structure_only。
- `relationship.branch_harmony`：READY；匹配 `bazi.scenario.compatibility_structure`，事实路径 `/spouse_palace_relation/relations`；deterministic_structure_only。
- `relationship.branch_harm`：READY；匹配 `bazi.scenario.compatibility_structure`，事实路径 `/spouse_palace_relation/relations`；deterministic_structure_only。
- `compatibility.cross_matrix_structure`：READY；匹配 `bazi.scenario.compatibility_structure`，事实路径 `/cross_relation_matrix_summary`；deterministic_structure_only。

当前禁止结论：合盘匹配分；六合即适婚；六冲必分手；共同婚期。

缺失能力 / 依赖 / 下一批：

- `bazi-foundation`：十干阴阳五行、生克方向及四柱/日主/十神/藏干已有审核短引、执行与 Golden；仍缺十二长生、季节实际效力及基础结构到个人结论的条件规则，真太阳时未实现；旧表权重不作通用结论。
  下一批从 `data/canonical/classics/bazi/ditiansui_chanwei_v1.json#/sections/0/text` 核短引、条件和反例；全文命中仅是待审定位，不是 Evidence。
- `bazi-strength`：月令/通根候选/透藏/生克方向位置 v1 已按原模型执行，含正常/阴日干/多比肩不判强/冲克不定凶及分日冲突反例。整体强弱仍缺季节司令、根力、得势、生扶克泄耗效力与从化边界，不以数量或自创权重填补。
  下一批从 `data/canonical/classics/bazi/ditiansui_chanwei_v1.json#/sections/2/text` 核短引、条件和反例；全文命中仅是待审定位，不是 Evidence。
- `bazi-romance`：咸池、日支传统配偶宫结构位、显式财星/官杀lens及五合/六合/六害/六冲/三合结构已核；缺红鸾天喜天姚、旺衰格局喜用与岁运婚恋解释；三刑争议仍阻塞；禁止命中结构直接断现代婚姻。
  下一批从 `data/canonical/classics/bazi/ditiansui_chanwei_v1.json#/sections/3/text` 核短引、条件和反例；全文命中仅是待审定位，不是 Evidence。
- `bazi-annual`：日历干支不等于运势；缺原局、大运、流年作用图及强弱/喜忌条件规则。
  下一批从 `data/canonical/classics/bazi/ditiansui_chanwei_v1.json#/sections/1/text` 核短引、条件和反例；全文命中仅是待审定位，不是 Evidence。
- `bazi-pair`：已有真实双人Scenario、十神镜像、咸池交叉、干支关系矩阵与传统配偶星候选位置；缺双方旺衰/喜忌与共同岁运解释、用户关系结论Golden及发布授权；旧60分不可复用。
  下一批从 `data/canonical/classics/bazi/ditiansui_chanwei_v1.json#/sections/3/text` 核短引、条件和反例；全文命中仅是待审定位，不是 Evidence。

## 人生总览 · BLOCKED_ADVANCED

Scenario：`life`；已执行=True；现有结构公开标志=False；AI=false。

已有知识、Rule 与 Evidence：

- 八字基础与十神映射：Terms `bazi.term.day_master`, `bazi.term.ten_gods`, `bazi.term.hidden_stems`, `bazi.term.month_command`, `bazi.term.root_candidates`, `bazi.term.hidden_to_visible`, `bazi.term.heavenly_stems`, `bazi.term.stem_polarity`, `bazi.term.five_elements`, `bazi.term.generation_control`；Phase1 Rule `bazi.rule.r001`, `bazi.rule.r002`, `bazi.rule.r003`, `bazi.rule.r011`, `bazi.rule.r012`, `bazi.rule.r013`, `bazi.rule.r014`, `bazi.rule.r015`, `bazi.rule.r016`。
- 旺衰及流派边界：Terms `bazi.term.strength_review_boundary`, `bazi.term.month_command`, `bazi.term.root_candidates`, `bazi.term.hidden_to_visible`；Phase1 Rule `bazi.rule.r012`, `bazi.rule.r013`, `bazi.rule.r014`, `bazi.rule.r015`。
- 格局：Terms 尚无对应审核术语；Phase1 Rule 尚无对应审核规则。
- 喜用神分体系治理：Terms 尚无对应审核术语；Phase1 Rule 尚无对应审核规则。
- 大运：Terms 尚无对应审核术语；Phase1 Rule 尚无对应审核规则。
- 流年与岁运作用：Terms `bazi.term.branch_triple_harmonies`；Phase1 Rule `bazi.rule.r010`。
- 婚恋专题：Terms `bazi.term.xianchi`, `bazi.term.stem_five_combinations`, `bazi.term.branch_six_harmonies`, `bazi.term.branch_six_harms`, `bazi.term.spouse_palace_day_branch`, `bazi.term.branch_six_clashes`, `bazi.term.branch_triple_harmonies`, `bazi.term.traditional_spouse_star_lens`；Phase1 Rule `bazi.rule.r004`, `bazi.rule.r005`, `bazi.rule.r006`, `bazi.rule.r007`, `bazi.rule.r008`, `bazi.rule.r009`, `bazi.rule.r010`, `bazi.rule.r011`。
- 事业财富专题：Terms 尚无对应审核术语；Phase1 Rule 尚无对应审核规则。
- 人生聚合：Terms 尚无对应审核术语；Phase1 Rule 尚无对应审核规则。

已有 Phase2 / Golden / Variant：

- `bazi.phase2.pillars` / `ziping-structural-v1`；Golden：`bazi.structural-basic`；测试 `tests/test_phase2_bazi.py`。
  Evidence C：`bazi.source.yuanhai` / 渊海子平 / 喜忌篇 / `《渊海子平》喜忌篇；本轮固定短引`，引文：四柱排定,三才次分,专以日上天元,配合八字支干;有见不见之形,无时不有;神煞相绊,轻重较量。。
- `bazi.phase2.ten_gods` / `ziping-structural-v1`；Golden：`bazi.structural-basic`；测试 `tests/test_phase2_bazi.py`。
  Evidence C：`bazi.source.yuanhai` / 渊海子平 / 基础与藏遁 / `《渊海子平》基础；本轮固定短引`，引文：以甲为例★见甲:为比肩、兄弟。
 见乙:为劫财、败财,剋父及妻。
 见丙:为食神、天厨、寿星,为男。
 见丁:为伤官、退财、耗气,子甥。
 见戊:为偏财、偏妻、偏妾,剋子。
 见己:为正财、正妻,剋母,为合神。
 见庚:为偏官、七杀、官鬼、将星。
 见辛:为正官、禄马、荣神,父母。
 见壬:为倒食、偏印、梟神,剋女。
 见癸:为印綬、正人、君子,产业。。
  Evidence C：`bazi.source.yuanhai` / 渊海子平 / 基础与藏遁 / `《渊海子平》基础；本轮固定短引`，引文：以乙为例★见甲:为劫财、逐马,剋妻。
 见乙:为比肩、兄弟、朋友。
 见丙:为伤官、小人、盗气,为姪。
 见丁:为食神、天厨、寿星,子孙。
 见戊:为正财、正妻,剋母。
 见己:为偏财、偏妻、偏妾,剋子。
 见庚:为正官、禄马,剋父母。
 见辛:为偏官、七杀、官鬼,媒人。
 见壬:为印綬、正人、君子,忌杀。
 见癸:为倒食、偏印、梟神,剋母。。
  Evidence C：`bazi.source.yuanhai` / 渊海子平 / 十神关系选段 / `《渊海子平》论伤官；本轮固定短引`，引文：又云,伤官者,我生彼之谓也;以阳见阴,阴见阳,亦名盗气。。
  Evidence C：`bazi.source.yuanhai` / 渊海子平 / 十神关系选段 / `《渊海子平》论正财；本轮固定短引`，引文：何谓之正财?犹如正官之意;是阴见阳财,阳见阴财。。
  Evidence C：`bazi.source.yuanhai` / 渊海子平 / 十神关系选段 / `《渊海子平》正官论；本轮固定短引`，引文：夫正官者,甲见辛之类;乃阴见阳为官,阳见阴为鬼,阴阳配合成其道也。。
  Evidence C：`bazi.source.yuanhai` / 渊海子平 / 十神关系选段 / `《渊海子平》论印绶；本轮固定短引`，引文：夫印綬者,生我之谓也,亦名生气。以阳见阴,以阴见阳,谓之正印;阳见阳,阴见阴,谓之偏印。。
- `bazi.phase2.hidden_stems` / `ziping-structural-v1`；Golden：`bazi.structural-basic`；测试 `tests/test_phase2_bazi.py`。
  Evidence C：`bazi.source.yuanhai` / 渊海子平 / 基础与藏遁 / `《渊海子平》又地支藏遁歌；本轮固定短引`，引文：子宫癸水在其中,丑癸辛金己土同;寅宫甲木兼丙戊,卯宫乙木独相逢。辰藏乙戊三分癸,巳中庚金丙戊丛;午宫丁火并己土,未宫乙己丁共宗。申位庚金壬水戊,酉宫辛金独丰隆;戌宫辛金及丁戊,亥藏壬甲是真踪。。
- `bazi.phase2.xianchi_lookup` / `ziping-structural-v1`；Golden：`bazi.xianchi-explicit-dual-basis`；测试 `tests/test_phase2_bazi.py`。
  Evidence C：`bazi.source.sanming-xianchi-niutrans` / 三命通会 / 卷二·论咸池 / `《三命通会》卷二·论咸池；固定短引`，引文：《淮南子》曰： 日出扶桑，入于咸池。 故五行沐浴之地，名咸池。是取日人之义，万物暗昧之时。寅午戌卯、已酉丑午、申子辰酉、亥卯未子即长生第二位沐浴之宫是也。一名败神，一名桃花煞。
- `bazi.phase2.stem_five_combinations` / `ziping-structural-v1`；Golden：`bazi.relations-core`；测试 `tests/test_phase2_bazi.py`。
  Evidence C：`bazi.source.xieji-relations` / 钦定协纪辨方书 / 五合六合六害结构短引 / `《钦定协纪辨方书》卷一·五合；固定短引`，引文：甲与己合乙与庚合丙与辛合丁与壬合戊与癸合。
- `bazi.phase2.branch_six_harmonies` / `ziping-structural-v1`；Golden：`bazi.relations-core`；测试 `tests/test_phase2_bazi.py`。
  Evidence C：`bazi.source.xieji-relations` / 钦定协纪辨方书 / 五合六合六害结构短引 / `《钦定协纪辨方书》卷一·六合；固定短引`，引文：子与丑合寅与亥合卯与戌合辰与酉合巳与申合午与未合。
- `bazi.phase2.branch_six_harms` / `ziping-structural-v1`；Golden：`bazi.relations-core`；测试 `tests/test_phase2_bazi.py`。
  Evidence C：`bazi.source.xieji-relations` / 钦定协纪辨方书 / 五合六合六害结构短引 / `《钦定协纪辨方书》月害条；固定短引`，引文：月害者月中六害也假令夘辰相害者夘以乙旺之木害辰墓之土辰以墓土却害夘中癸水也寅巳相害者谓寅以旺甲害巳中戊土而巳以生庚害寅中旺甲也丑午相害者丑以癸水害午中丁火午以巳土害丑中癸水也子未相害者子以所生之辛金害未中墓木未以旺土害子中旺水也申亥相害者亥以生木害申中生土申以旺金害亥中生木又以生土害亥中旺水也酉戌相害者戌以墓火害酉之旺金酉以所生丁火害戌中辛金也。
- `bazi.phase2.spouse_palace_day_branch` / `ziping-structural-v1`；Golden：`bazi.relations-core`；测试 `tests/test_phase2_bazi.py`。
  Evidence C：`bazi.source.yuanhai` / 渊海子平 / 络绎赋·日支妻位 / `《渊海子平》络绎赋；固定短引`，引文：年干父兮支母。
 日干己兮支妻。
 月干兄兮支弟。
 时支女兮干儿。。
- `bazi.phase2.branch_six_clashes` / `ziping-structural-v1`；Golden：`bazi.relations-expanded`；测试 `tests/test_phase2_bazi.py`。
  Evidence C：`bazi.source.xieji-relations` / 钦定协纪辨方书 / 五合六合六害结构短引 / `《钦定协纪辨方书》月建相关条；固定短引`，引文：洞源经曰对七为冲隔三为破选择家所谓辰破丑而丑冲未亥破寅而寅冲申午破夘而夘冲酉酉破子而子冲午申破巳而巳冲亥戌破未而未冲丑是也。
  Evidence C：`bazi.source.xieji-relations` / 钦定协纪辨方书 / 五合六合六害结构短引 / `《钦定协纪辨方书》月建相关条；固定短引`，引文：假如建在子前三为平为夘后三为收为酉夘酉冲也建在丑前三为平为辰后三为收为戌辰戌冲也推之十二辰莫不皆然。
- `bazi.phase2.branch_triple_harmonies` / `ziping-structural-v1`；Golden：`bazi.relations-expanded`；测试 `tests/test_phase2_bazi.py`。
  Evidence C：`bazi.source.xieji-relations` / 钦定协纪辨方书 / 五合六合六害结构短引 / `《钦定协纪辨方书》大煞条；固定短引`，引文：考原曰大煞子年在子丑年在酉寅年在午夘年在夘辰年又在子如是逆行四正盖申子辰三合为水水旺于子也巳酉丑三合为金金旺于酉也寅午戌三合为火火旺于午也亥夘未三合为木木旺于夘也。
- `bazi.phase2.spouse_star_lens` / `ziping-structural-v1`；Golden：`bazi.spouse-star-lens-male`, `bazi.spouse-star-lens-female`；测试 `tests/test_phase2_bazi.py`。
  Evidence C：`bazi.source.yuanhai` / 渊海子平 / 传统配偶星观察口径 / `《渊海子平》六亲总篇；固定短引`，引文：用日干为主:正印正母;偏印偏母及祖父也;偏财是父,乃母之夫星也,亦为偏妻;正财为妻;偏财为妾,为父是也;比肩为兄弟姐妹也;七杀是男;正官是女;食神是男孙;伤官是女孙及祖母也。
 妇人命取六亲,与男命不同:取官星为夫星;七杀是偏夫;食神是男;伤官是女。。
  Evidence C：`bazi.source.ditiansui-spouse` / 滴天髓阐微 / 夫妻与女命观察边界 / `《滴天髓阐微》六亲论·女命章；固定短引`，引文：不必专执官星而论夫。专执伤食而论子。但以安祥顺静为贵,二德三奇不必论,咸池驿马纵有验,总之于理不长。其中究论,不可不详。。
  Evidence C：`bazi.source.ditiansui-spouse` / 滴天髓阐微 / 夫妻与女命观察边界 / `《滴天髓阐微》六亲论·夫妻；固定短引`，引文：子平之法,以财为妻,财是我克。人以财来侍我,此理出于正论。
- `bazi.phase2.month_command_factors` / `ziping-structural-v1`；Golden：`bazi.factors-normal`, `bazi.factors-tomb-boundary`, `bazi.factors-many-stems-no-root`, `bazi.factors-few-stems-with-root`, `bazi.factors-clash-not-erasure`, `bazi.factors-siling-unresolved`；测试 `tests/test_phase2_bazistrength.py`。
  Evidence C：`bazi.source.ditiansui-spouse` / 滴天髓阐微 / 月令、通根与透藏观察边界 / `《滴天髓阐微》通神论·月令；固定原文字符位置 37963；月令提纲`，引文：月令乃提纲之府,譬之宅也,人元为用事之神,宅之定向也,不可以不卜。。
  Evidence C：`bazi.source.ditiansui-spouse` / 滴天髓阐微 / 月令、通根与透藏观察边界 / `《滴天髓阐微》通神论·月令；固定原文字符位置 38056；寅月司令分日`，引文：如寅月生人,立春后七日前,皆值戊土用事;八日后十四日前者,丙火用事 ;十五日后,甲木用事。。
  Evidence C：`bazi.source.ditiansui-spouse` / 滴天髓阐微 / 月令、通根与透藏观察边界 / `《滴天髓阐微》通神论·衰旺；固定原文字符位置 39648；不可得令即旺失令即弱`，引文：得时俱为旺论,失令便作衰看,虽是至理,亦死法也。。
  Evidence C：`bazi.source.yuanhai` / 渊海子平 / 基础与藏遁 / `《渊海子平》又地支藏遁歌；本轮固定短引`，引文：子宫癸水在其中,丑癸辛金己土同;寅宫甲木兼丙戊,卯宫乙木独相逢。辰藏乙戊三分癸,巳中庚金丙戊丛;午宫丁火并己土,未宫乙己丁共宗。申位庚金壬水戊,酉宫辛金独丰隆;戌宫辛金及丁戊,亥藏壬甲是真踪。。
- `bazi.phase2.root_candidates` / `ziping-structural-v1`；Golden：`bazi.factors-normal`, `bazi.factors-tomb-boundary`, `bazi.factors-many-stems-no-root`, `bazi.factors-few-stems-with-root`, `bazi.factors-clash-not-erasure`, `bazi.factors-siling-unresolved`；测试 `tests/test_phase2_bazistrength.py`。
  Evidence C：`bazi.source.ditiansui-spouse` / 滴天髓阐微 / 月令、通根与透藏观察边界 / `《滴天髓阐微》通神论·衰旺；固定原文字符位置 39989；比肩与地支根不可数量等同`，引文：天干得一比肩,不如地支得一余气墓库。。
  Evidence C：`bazi.source.ditiansui-spouse` / 滴天髓阐微 / 月令、通根与透藏观察边界 / `《滴天髓阐微》通神论·衰旺；固定原文字符位置 40063；余气与长生禄旺根示例`，引文：余气者,如丙丁逢未,甲乙逢辰,庚辛逢戌,壬癸逢丑之类是也,得二比肩,不如支中得一长生禄旺,如甲乙逢亥寅卯之类是也。。
  Evidence C：`bazi.source.ditiansui-spouse` / 滴天髓阐微 / 月令、通根与透藏观察边界 / `《滴天髓阐微》通神论·衰旺；固定原文字符位置 39648；不可得令即旺失令即弱`，引文：得时俱为旺论,失令便作衰看,虽是至理,亦死法也。。
  Evidence C：`bazi.source.yuanhai` / 渊海子平 / 基础与藏遁 / `《渊海子平》又地支藏遁歌；本轮固定短引`，引文：子宫癸水在其中,丑癸辛金己土同;寅宫甲木兼丙戊,卯宫乙木独相逢。辰藏乙戊三分癸,巳中庚金丙戊丛;午宫丁火并己土,未宫乙己丁共宗。申位庚金壬水戊,酉宫辛金独丰隆;戌宫辛金及丁戊,亥藏壬甲是真踪。。
- `bazi.phase2.hidden_to_visible` / `ziping-structural-v1`；Golden：`bazi.factors-normal`, `bazi.factors-tomb-boundary`, `bazi.factors-many-stems-no-root`, `bazi.factors-few-stems-with-root`, `bazi.factors-clash-not-erasure`, `bazi.factors-siling-unresolved`；测试 `tests/test_phase2_bazistrength.py`。
  Evidence C：`bazi.source.ditiansui-spouse` / 滴天髓阐微 / 月令、通根与透藏观察边界 / `《滴天髓阐微》通神论·月令；固定原文字符位置 38284；藏干与显干引助`，引文：故知地支人元必得天干引助,天干为用,必要地支司令。。
  Evidence C：`bazi.source.yuanhai` / 渊海子平 / 基础与藏遁 / `《渊海子平》又地支藏遁歌；本轮固定短引`，引文：子宫癸水在其中,丑癸辛金己土同;寅宫甲木兼丙戊,卯宫乙木独相逢。辰藏乙戊三分癸,巳中庚金丙戊丛;午宫丁火并己土,未宫乙己丁共宗。申位庚金壬水戊,酉宫辛金独丰隆;戌宫辛金及丁戊,亥藏壬甲是真踪。。
- `bazi.phase2.support_relations` / `ziping-structural-v1`；Golden：`bazi.support-normal`, `bazi.support-yin`, `bazi.support-visible-peers`, `bazi.support-conflict`；测试 `tests/test_phase2_bazisupport.py`。
  Evidence C：`bazi.source.yuanhai` / 渊海子平 / 生克关系与效力界限 / `《渊海子平》五行相生及条件界限；固定原文字符位置 964`，引文：金能生水,水多金沉;水能生木,木盛水缩;木能生火,火多木焚;火能生土,土多火埋;土能生金,金多土变。。
  Evidence C：`bazi.source.yuanhai` / 渊海子平 / 生克关系与效力界限 / `《渊海子平》五行相克及条件界限；固定原文字符位置 1016`，引文：金能剋木,木坚金缺;木能剋土,土重木折;土能剋水,水多土流;水能剋火,火多水热;火能剋金,金多火熄。。
  Evidence C：`bazi.source.ditiansui-spouse` / 滴天髓阐微 / 天干阴阳五行分类 / `《滴天髓阐微·审核短引》十干阴阳短引；固定原文字符位置 4991`，引文：甲、丙、戊、庚、壬为阳,独丙火秉阳之精,而为阳中之阳;乙、丁、己、辛、癸为阴,独癸水秉阴之精,而为阴中之阴。。
  Evidence C：`bazi.source.ditiansui-spouse` / 滴天髓阐微 / 天干阴阳五行分类 / `《滴天髓阐微·审核短引》十干五行短引；固定原文字符位置 5159`，引文：甲乙一木也,丙丁一火也,戊己一土也,庚辛一金也,壬癸一水也,即分别所用,不过阳刚阴柔,阳健阴顺而已。。
  Evidence C：`bazi.source.yuanhai` / 渊海子平 / 基础与藏遁 / `《渊海子平》基础；本轮固定短引`，引文：以甲为例★见甲:为比肩、兄弟。
 见乙:为劫财、败财,剋父及妻。
 见丙:为食神、天厨、寿星,为男。
 见丁:为伤官、退财、耗气,子甥。
 见戊:为偏财、偏妻、偏妾,剋子。
 见己:为正财、正妻,剋母,为合神。
 见庚:为偏官、七杀、官鬼、将星。
 见辛:为正官、禄马、荣神,父母。
 见壬:为倒食、偏印、梟神,剋女。
 见癸:为印綬、正人、君子,产业。。
  Evidence C：`bazi.source.yuanhai` / 渊海子平 / 基础与藏遁 / `《渊海子平》基础；本轮固定短引`，引文：以乙为例★见甲:为劫财、逐马,剋妻。
 见乙:为比肩、兄弟、朋友。
 见丙:为伤官、小人、盗气,为姪。
 见丁:为食神、天厨、寿星,子孙。
 见戊:为正财、正妻,剋母。
 见己:为偏财、偏妻、偏妾,剋子。
 见庚:为正官、禄马,剋父母。
 见辛:为偏官、七杀、官鬼,媒人。
 见壬:为印綬、正人、君子,忌杀。
 见癸:为倒食、偏印、梟神,剋母。。
  Evidence C：`bazi.source.yuanhai` / 渊海子平 / 十神关系选段 / `《渊海子平》论伤官；本轮固定短引`，引文：又云,伤官者,我生彼之谓也;以阳见阴,阴见阳,亦名盗气。。
  Evidence C：`bazi.source.yuanhai` / 渊海子平 / 十神关系选段 / `《渊海子平》论正财；本轮固定短引`，引文：何谓之正财?犹如正官之意;是阴见阳财,阳见阴财。。
  Evidence C：`bazi.source.yuanhai` / 渊海子平 / 十神关系选段 / `《渊海子平》正官论；本轮固定短引`，引文：夫正官者,甲见辛之类;乃阴见阳为官,阳见阴为鬼,阴阳配合成其道也。。
  Evidence C：`bazi.source.yuanhai` / 渊海子平 / 十神关系选段 / `《渊海子平》论印绶；本轮固定短引`，引文：夫印綬者,生我之谓也,亦名生气。以阳见阴,以阴见阳,谓之正印;阳见阳,阴见阴,谓之偏印。。
  Evidence C：`bazi.source.yuanhai` / 渊海子平 / 基础与藏遁 / `《渊海子平》又地支藏遁歌；本轮固定短引`，引文：子宫癸水在其中,丑癸辛金己土同;寅宫甲木兼丙戊,卯宫乙木独相逢。辰藏乙戊三分癸,巳中庚金丙戊丛;午宫丁火并己土,未宫乙己丁共宗。申位庚金壬水戊,酉宫辛金独丰隆;戌宫辛金及丁戊,亥藏壬甲是真踪。。

当前场景可输出结论（只描述事实，不追加吉凶含义）：

- `bazi.pillars`：READY；匹配 `bazi.phase2.pillars`，事实路径 `/ganzhi`；deterministic_structure_only。
- `bazi.day_master`：READY；匹配 `bazi.phase2.pillars`，事实路径 `/day_master`；deterministic_structure_only。
- `romance.xianchi_structure`：READY；匹配 `bazi.scenario.xianchi_structure`，事实路径 `/`；deterministic_structure_only。
- `career.ten_god_positions`：READY；匹配 `bazi.scenario.career_wealth_structure`，事实路径 `/`；deterministic_structure_only。

当前禁止结论：人生总分；健康寿命断语；未经模块审核的人生结论。

缺失能力 / 依赖 / 下一批：

- `bazi-foundation`：十干阴阳五行、生克方向及四柱/日主/十神/藏干已有审核短引、执行与 Golden；仍缺十二长生、季节实际效力及基础结构到个人结论的条件规则，真太阳时未实现；旧表权重不作通用结论。
  下一批从 `data/canonical/classics/bazi/ditiansui_chanwei_v1.json#/sections/0/text` 核短引、条件和反例；全文命中仅是待审定位，不是 Evidence。
- `bazi-strength`：月令/通根候选/透藏/生克方向位置 v1 已按原模型执行，含正常/阴日干/多比肩不判强/冲克不定凶及分日冲突反例。整体强弱仍缺季节司令、根力、得势、生扶克泄耗效力与从化边界，不以数量或自创权重填补。
  下一批从 `data/canonical/classics/bazi/ditiansui_chanwei_v1.json#/sections/2/text` 核短引、条件和反例；全文命中仅是待审定位，不是 Evidence。
- `bazi-pattern`：正文提及不等于结构规则；缺成格/破格/兼格条件、流派限制和 Golden。
  下一批从 `data/canonical/classics/bazi/ditiansui_chanwei_v1.json#/sections/7/text` 核短引、条件和反例；全文命中仅是待审定位，不是 Evidence。
- `bazi-useful-god`：调候、扶抑、病药、格局用神未分别治理；依赖旺衰与格局；禁止输出喜用木火等具体结论。
  下一批先登记来源及权利，保存 RAW/Quarantine；无审核引文时保持未支持。
- `bazi-dayun`：旧说明不是执行；须核顺逆/起运法/节界/岁数换算/原局作用及不同 Variant。
  下一批从 `data/canonical/classics/bazi/ditiansui_chanwei_v1.json#/sections/3/text` 核短引、条件和反例；全文命中仅是待审定位，不是 Evidence。
- `bazi-annual`：日历干支不等于运势；缺原局、大运、流年作用图及强弱/喜忌条件规则。
  下一批从 `data/canonical/classics/bazi/ditiansui_chanwei_v1.json#/sections/1/text` 核短引、条件和反例；全文命中仅是待审定位，不是 Evidence。
- `bazi-romance`：咸池、日支传统配偶宫结构位、显式财星/官杀lens及五合/六合/六害/六冲/三合结构已核；缺红鸾天喜天姚、旺衰格局喜用与岁运婚恋解释；三刑争议仍阻塞；禁止命中结构直接断现代婚姻。
  下一批从 `data/canonical/classics/bazi/ditiansui_chanwei_v1.json#/sections/3/text` 核短引、条件和反例；全文命中仅是待审定位，不是 Evidence。
- `bazi-career-wealth`：缺组合、位置、强弱、格局、岁运解释规则；财多身弱须先完成旺衰，不能用财星数量推财富。
  下一批从 `data/canonical/classics/bazi/ditiansui_chanwei_v1.json#/sections/3/text` 核短引、条件和反例；全文命中仅是待审定位，不是 Evidence。
- `life-aggregation`：只能组合已审核模块；缺模块授权、证据去重、冲突优先级、历史记录及综合指数依据；不另建人生算法。
  下一批先登记来源及权利，保存 RAW/Quarantine；无审核引文时保持未支持。

## AI解梦 · NOT_BUILT

Scenario：`dream`；已执行=False；现有结构公开标志=False；AI=false。

已有知识、Rule 与 Evidence：

- 传统梦文化：Terms 尚无对应审核术语；Phase1 Rule 尚无对应审核规则。
- 现代心理梦研究：Terms 尚无对应审核术语；Phase1 Rule 尚无对应审核规则。

已有 Phase2 / Golden / Variant：


当前场景可输出结论（只描述事实，不追加吉凶含义）：

- 无已接入的结构 claim；引擎能力如上，场景接线须另审。

当前禁止结论：无检索解梦；疾病或怀孕诊断；梦预示未来；心理理论冒充古籍。

缺失能力 / 依赖 / 下一批：

- `dream-traditional`：已登记固定 daizhigev20 周公解梦 RAW/Quarantine 调查候选并核 17 类输入：11 个直接场景定位、5 个仅相近语境、1 个未找到；0 个已确认解释。底本、权利/编者、异文与场景条件仍须审核；尚无梦域 Terms/Rules/Evidence/Golden、RAG 解释或执行，不把吉凶短句变成个人预测。
  下一批先登记来源及权利，保存 RAW/Quarantine；无审核引文时保持未支持。
- `dream-psychology`：dream-modern-psychology 已有独立学术来源调查清单，含可核查研究及许可信息；尚未入既有 Source/Review 模型，未形成已审核证据或执行。文化梦书研究不作临床心理证据，不从梦诊断精神疾病、怀孕或预测必然未来。
  下一批先登记来源及权利，保存 RAW/Quarantine；无审核引文时保持未支持。

## 一事占问 · PRODUCTIZABLE

Scenario：`question`；已执行=True；现有结构公开标志=True；AI=false。

已有知识、Rule 与 Evidence：

- 六爻占问深化：Terms `liuyao.term.t003`, `liuyao.term.t004`, `liuyao.term.t005`, `liuyao.term.t006`, `liuyao.term.t007`, `liuyao.term.t008`, `liuyao.term.t009`, `liuyao.term.t010`, `liuyao.term.t012`, `liuyao.term.t015`, `liuyao.term.t016`, `liuyao.term.t017`, `liuyao.term.t018`, `liuyao.term.t019`, `liuyao.term.t020`, `liuyao.term.t021`, `liuyao.term.t022`, `liuyao.term.t023`, `liuyao.term.t024`, `liuyao.term.t025`, `liuyao.term.t028`, `liuyao.term.t029`, `liuyao.term.t030`；Phase1 Rule `liuyao.rule.r001`, `liuyao.rule.r002`, `liuyao.rule.r003`, `liuyao.rule.r004`, `liuyao.rule.r005`, `liuyao.rule.r006`, `liuyao.rule.r008`, `liuyao.rule.r009`, `liuyao.rule.r010`, `liuyao.rule.r013`, `liuyao.rule.r014`, `liuyao.rule.r015`, `liuyao.rule.r016`, `liuyao.rule.r017`, `liuyao.rule.r018`, `liuyao.rule.r019`, `liuyao.rule.r020`, `liuyao.rule.r023`, `liuyao.rule.r024`。
- 奇门专业能力：Terms `qimen.term.t001`, `qimen.term.t002`, `qimen.term.t003`, `qimen.term.t004`, `qimen.term.t005`, `qimen.term.t006`, `qimen.term.t007`, `qimen.term.t008`, `qimen.term.t011`, `qimen.term.t012`, `qimen.term.t013`, `qimen.term.t014`, `qimen.term.t015`；Phase1 Rule `qimen.rule.r002`, `qimen.rule.r003`, `qimen.rule.r004`。

已有 Phase2 / Golden / Variant：

- `liuyao.phase2.najia` / `jingfang-eight-palaces-v1`；Golden：`liuyao.qian-static`, `liuyao.qian-to-gou`, `liuyao.tai-to-sheng`；测试 `tests/test_phase2_liuyao.py`。
  Evidence C：`liuyao.source.zengshan` / 增删卜易 / 基础选段（编者定位） / `渾天甲子章第四`，引文：乾在內：子水寅木辰土。乾在外：午火申金戌土。。
  Evidence C：`liuyao.source.zengshan` / 增删卜易 / 基础选段（编者定位） / `渾天甲子章第四`，引文：兌在內：巳火卯木丑土。兌在外：亥水酉金未土。。
  Evidence C：`liuyao.source.zengshan` / 增删卜易 / 基础选段（编者定位） / `渾天甲子章第四`，引文：離在內：卯木丑土亥水。離在外：酉金未土巳火。。
  Evidence C：`liuyao.source.zengshan` / 增删卜易 / 基础选段（编者定位） / `渾天甲子章第四`，引文：震在內：子水寅木辰土。震在外；午火申金戌土。。
  Evidence C：`liuyao.source.zengshan` / 增删卜易 / 基础选段（编者定位） / `渾天甲子章第四`，引文：巽在內：丑土亥水酉金。巽在外：未土巳火卯木。。
  Evidence C：`liuyao.source.zengshan` / 增删卜易 / 基础选段（编者定位） / `渾天甲子章第四`，引文：坎在內：寅木辰土午火。坎在外：申金戌土子水。。
  Evidence C：`liuyao.source.bushi` / 卜筮正宗 / 基础选段（编者定位） / `纳甲表·艮阳卦行`，引文：艮　納丙	辰，午，申	艮　納丙	戌，子，寅。
  Evidence C：`liuyao.source.zengshan` / 增删卜易 / 基础选段（编者定位） / `渾天甲子章第四`，引文：坤在內：未土巳火卯木。坤在外：丑土亥水酉金。。
- `liuyao.phase2.relatives` / `jingfang-eight-palaces-v1`；Golden：`liuyao.qian-static`, `liuyao.qian-to-gou`, `liuyao.tai-to-sheng`；测试 `tests/test_phase2_liuyao.py`。
  Evidence C：`liuyao.source.bushi` / 卜筮正宗 / 基础选段（编者定位） / `基础选段（编者定位）; decoded-character interval [4018,4053)`，引文：生我者為父母，我生者為子孫，克我者為官鬼，我克者為妻財．比和者為兄弟．。
  Evidence C：`liuyao.source.zengshan` / 增删卜易 / 六親歌章第五 / `UTF-8 text chars [14445,14578); edited excerpt boundary, original chapter heading`，引文：乾兌宮金兄、土父、木財、火鬼、水子。乾兌宮八卦都屬金
坎宮水兄、火財、土鬼、金父、木子。坎宮八卦都屬水。
坤艮宮土兄、火父、木鬼、水財、金子。坤艮宮八卦都屬土。
離宮火兄、水鬼、土子、木父﹐金財。離宮八卦都屬火。
震巽木兄、水父、金鬼、火子、土財。震巽宮八卦都屬木。。
- `liuyao.phase2.palace` / `jingfang-eight-palaces-v1`；Golden：`liuyao.qian-static`, `liuyao.qian-to-gou`, `liuyao.tai-to-sheng`；测试 `tests/test_phase2_liuyao.py`。
  Evidence C：`liuyao.source.zengshan` / 增删卜易 / 基础选段（编者定位） / `基础选段（编者定位）; decoded-character interval [14811,14885)`，引文：乾為天「世」在六﹐天風姤「世」在初﹐天山遁「世」在二﹐天地否「世」在三﹐天地觀「世」在四﹐山地剝「世」在五﹐火地晉「世」在四﹐火天大有「世」退在三。。
  Evidence C：`liuyao.source.zengshan` / 增删卜易 / 基础选段（编者定位） / `基础选段（编者定位）; decoded-character interval [14886,14901)`，引文：隔世爻兩位卽是應爻﹐餘卦仿此。。
  Evidence C：`liuyao.source.zengshan` / 增删卜易 / 世應章第六 / `UTF-8 text chars [14811,14901); edited excerpt boundary, original chapter heading`，引文：乾為天「世」在六﹐天風姤「世」在初﹐天山遁「世」在二﹐天地否「世」在三﹐天地觀「世」在四﹐山地剝「世」在五﹐火地晉「世」在四﹐火天大有「世」退在三。
隔世爻兩位卽是應爻﹐餘卦仿此。。
  Evidence C：`liuyao.source.bushi` / 卜筮正宗 / 安世應訣 / `UTF-8 chars [9199,9231)`，引文：八卦之首世六當，以下初爻輪上揚，游魂八宮四爻立，歸魂八卦三爻詳。。
- `liuyao.phase2.spirits` / `jingfang-eight-palaces-v1`；Golden：`liuyao.qian-static`, `liuyao.qian-to-gou`, `liuyao.tai-to-sheng`；测试 `tests/test_phase2_liuyao.py`。
  Evidence C：`liuyao.source.bushi` / 卜筮正宗 / 基础选段（编者定位） / `基础选段（编者定位）; decoded-character interval [9236,9272)`，引文：甲乙起青龍，丙丁起朱雀，戊日起勾陳，己日起騰蛇，庚辛起白虎，壬癸起玄武。。
  Evidence C：`liuyao.source.zengshan` / 增删卜易 / 六神章第十八 / `UTF-8 text chars [22246,22372); edited excerpt boundary, original chapter heading`，引文：甲乙日丙丁日戊日　己日　庚辛日壬癸日
元武　靑龍　朱雀　勾陳　滕蛇　白虎
白虎　元武　靑龍　朱雀　勾陳　滕蛇
滕蛇　白虎　元武　靑龍　朱雀　勾陳
勾陳　滕蛇　白虎　元武　靑龍　朱雀
朱雀　勾陳　滕蛇　白虎　元武　靑龍
靑龍　朱雀　勾陳　滕蛇　白虎　元武。
- `liuyao.phase2.empty` / `jingfang-eight-palaces-v1`；Golden：`liuyao.qian-static`, `liuyao.qian-to-gou`, `liuyao.tai-to-sheng`；测试 `tests/test_phase2_liuyao.py`。
  Evidence C：`liuyao.source.bushi` / 卜筮正宗 / 基础选段（编者定位） / `基础选段（编者定位）; decoded-character interval [13706,13731)`，引文：假如甲子日至癸酉十日為一旬，旬內無戍亥故曰戍亥空．。
  Evidence C：`liuyao.source.zengshan` / 增删卜易 / 旬空章第二十六 / `UTF-8 text chars [29389,29434); edited excerpt boundary, original chapter heading`，引文：何謂旬空？如甲子至癸酉日為一旬﹐此十日之內﹐並無戌亥﹐以爻逢戌亥為空亡﹐又名旬空﹐餘仿此。。
- `liuyao.phase2.month_break` / `jingfang-eight-palaces-v1`；Golden：`liuyao.qian-static`, `liuyao.qian-to-gou`, `liuyao.tai-to-sheng`；测试 `tests/test_phase2_liuyao.py`。
  Evidence C：`liuyao.source.bushi` / 卜筮正宗 / 基础选段（编者定位） / `基础选段（编者定位）; decoded-character interval [13888,13900)`，引文：凡月建所衝之爻名為月破．。
  Evidence C：`liuyao.source.zengshan` / 增删卜易 / 月破章第二十七 / `UTF-8 text chars [33044,33098); edited excerpt boundary, original chapter heading`，引文：正申、二酉、三戌﹐四亥、五子、六丑、七寅、八卯、九辰﹐十巳、十一午、十二未﹐月建沖之為月破﹐逐月之破日是也。。
- `liuyao.phase2.motion` / `jingfang-eight-palaces-v1`；Golden：`liuyao.qian-static`, `liuyao.qian-to-gou`, `liuyao.tai-to-sheng`；测试 `tests/test_phase2_liuyao.py`。
  Evidence C：`yijing.source.meihua` / 梅花易数 / 基础选段（编者定位） / `基础选段（编者定位）; decoded-character interval [2433,2459)`，引文：若一爻动，则看此一爻，是阳爻则变阴爻，阴爻则变阳爻。。
  Evidence C：`liuyao.source.zengshan` / 增删卜易 / 動變章第七 / `UTF-8 text chars [14908,14946); edited excerpt boundary, original chapter heading`，引文：六爻不動則不變﹐動則必變﹐「○」為陽動則變「⚋」﹐「ㄨ』』為陰動則變「⚊」。。
  Evidence C：`liuyao.source.zengshan` / 增删卜易 / 動變章第七 / `UTF-8 text chars [15112,15212); edited excerpt boundary, original chapter heading`，引文：上三爻坎卦卽是坎在外卦：申金、戌土、子水。四爻申金、五爻戌土、六爻子水﹐變為乾卦。卽是乾在外卦：午火、申金、戌土所以申金變出午火﹐子水變出戌土﹐申爻不動則不變。變出之爻安六親者仍照正卦而推﹐餘卦仿此。。
- `qimen.phase2.calendar` / `qfdk-exact-term-midnight-v2`；Golden：`qimen.jiazi-winter`, `qimen.summer-before`, `qimen.summer-at`, `qimen.late-zi-midnight`；测试 `tests/test_phase2_qimen.py`。
  Evidence C：`qimen.source.baojian` / 奇门宝鉴御定 / 基础选段（编者定位） / `基础选段（编者定位）; decoded-character interval [1286,1298)`，引文：一节三元、二十四气备矣。。
  Evidence C：`qimen.source.tongzong` / 奇门遁甲统宗 / 基础选段（编者定位） / `基础选段（编者定位）; decoded-character interval [10331,10352)`，引文：一元五日，以甲己二干为一元之首，谓之符头。。
  Evidence C：`qimen.source.baojian` / 奇门宝鉴御定 / 基础选段（编者定位） / `基础选段（编者定位）; decoded-character interval [8552,8571)`，引文：本局地盘不动，以天盘甲子戊加乙于九宫。。
- `qimen.phase2.bureau` / `qfdk-exact-term-midnight-v2`；Golden：`qimen.jiazi-winter`, `qimen.summer-before`, `qimen.summer-at`, `qimen.late-zi-midnight`；测试 `tests/test_phase2_qimen.py`。
  Evidence C：`qimen.source.tongzong` / 奇门遁甲统宗 / 基础选段（编者定位） / `基础选段（编者定位）; decoded-character interval [10331,10352)`，引文：一元五日，以甲己二干为一元之首，谓之符头。。
  Evidence C：`qimen.source.tongzong` / 奇门遁甲统宗 / 基础选段（编者定位） / `基础选段（编者定位）; decoded-character interval [10352,10388)`，引文：符头所临之支值子午卯酉则为上元；值寅申巳亥则为中元；值辰戌丑未则为下元。。
  Evidence C：`qimen.source.tongzong` / 奇门遁甲统宗 / 基础选段（编者定位） / `基础选段（编者定位）; decoded-character interval [4851,4860)`，引文：自夏至气降起离九宫。
  Evidence C：`qimen.source.tongzong` / 奇门遁甲统宗 / 基础选段（编者定位） / `基础选段（编者定位）; decoded-character interval [4758,4767)`，引文：自冬至阳生起坎一宫。
- `qimen.phase2.earth` / `qfdk-exact-term-midnight-v2`；Golden：`qimen.jiazi-winter`, `qimen.summer-before`, `qimen.summer-at`, `qimen.late-zi-midnight`；测试 `tests/test_phase2_qimen.py`。
  Evidence C：`qimen.source.baojian` / 奇门宝鉴御定 / 基础选段（编者定位） / `基础选段（编者定位）; decoded-character interval [2406,2426)`，引文：乙为日奇、丙为月奇、丁为星奇，故名三奇。。
  Evidence C：`qimen.source.baojian` / 奇门宝鉴御定 / 基础选段（编者定位） / `基础选段（编者定位）; decoded-character interval [2437,2452)`，引文：戊己庚辛壬癸，皆有六甲遁乎其中。
- `qimen.phase2.chiefs` / `qfdk-exact-term-midnight-v2`；Golden：`qimen.jiazi-winter`, `qimen.summer-before`, `qimen.summer-at`, `qimen.late-zi-midnight`；测试 `tests/test_phase2_qimen.py`。
  Evidence C：`qimen.source.baojian` / 奇门宝鉴御定 / 基础选段（编者定位） / `基础选段（编者定位）; decoded-character interval [8552,8571)`，引文：本局地盘不动，以天盘甲子戊加乙于九宫。。
  Evidence C：`qimen.source.tongzong` / 奇门遁甲统宗 / 基础选段（编者定位） / `基础选段（编者定位）; decoded-character interval [10496,10519)`，引文：地盘旬首所临之宫，其星即为值符，其门即为值使。。
  Evidence C：`qimen.source.baojian` / 奇门宝鉴御定 / 基础选段（编者定位） / `基础选段（编者定位）; decoded-character interval [3302,3331)`，引文：八神者；天乙、螣蛇、太阴、六合、朱雀、白虎、九地、九天也。。
- `qimen.phase2.plates` / `qfdk-exact-term-midnight-v2`；Golden：`qimen.jiazi-winter`, `qimen.summer-before`, `qimen.summer-at`, `qimen.late-zi-midnight`；测试 `tests/test_phase2_qimen.py`。
  Evidence C：`qimen.source.baojian` / 奇门宝鉴御定 / 基础选段（编者定位） / `基础选段（编者定位）; decoded-character interval [8552,8571)`，引文：本局地盘不动，以天盘甲子戊加乙于九宫。。
  Evidence C：`qimen.source.tongzong` / 奇门遁甲统宗 / 基础选段（编者定位） / `基础选段（编者定位）; decoded-character interval [10496,10519)`，引文：地盘旬首所临之宫，其星即为值符，其门即为值使。。
  Evidence C：`qimen.source.baojian` / 奇门宝鉴御定 / 基础选段（编者定位） / `基础选段（编者定位）; decoded-character interval [3302,3331)`，引文：八神者；天乙、螣蛇、太阴、六合、朱雀、白虎、九地、九天也。。

当前场景可输出结论（只描述事实，不追加吉凶含义）：

- `liuyao.najia`：READY；匹配 `liuyao.phase2.najia`，事实路径 `/`；deterministic_structure_only。
- `liuyao.relatives`：READY；匹配 `liuyao.phase2.relatives`，事实路径 `/`；deterministic_structure_only。
- `liuyao.palace`：READY；匹配 `liuyao.phase2.palace`，事实路径 `/`；deterministic_structure_only。
- `liuyao.spirits`：READY；匹配 `liuyao.phase2.spirits`，事实路径 `/`；deterministic_structure_only。
- `liuyao.empty`：READY；匹配 `liuyao.phase2.empty`，事实路径 `/`；deterministic_structure_only。
- `liuyao.month_break`：READY；匹配 `liuyao.phase2.month_break`，事实路径 `/`；deterministic_structure_only。
- `liuyao.motion`：READY；匹配 `liuyao.phase2.motion`，事实路径 `/`；deterministic_structure_only。

当前禁止结论：事件必成必败；应期断定；自由选择未实现流派。

缺失能力 / 依赖 / 下一批：

- `liuyao-inquiry`：排盘七项结构已执行；术语/描述规则不等于占断；缺用神选取、旺衰、生克动变与应期解释的可执行链路。
  下一批复核现有 `liuyao.source.bushi`, `liuyao.source.zengshan`，沿原模型补规则条件及 Golden。
- `qimen-professional`：指定精确节气转盘结构已执行；缺格局/用神解释；置闰、超接及其他盘法未实现。
  下一批复核现有 `qimen.source.baojian`, `qimen.source.tongzong`，沿原模型补规则条件及 Golden。

## 紫微专业工具 · PARTIAL

Scenario：`None`；已执行=False；现有结构公开标志=False；AI=false。

已有知识、Rule 与 Evidence：

- 紫微专业能力：Terms `ziwei.term.t001`, `ziwei.term.t003`, `ziwei.term.t005`, `ziwei.term.t009`, `ziwei.term.t013`, `ziwei.term.t041`, `ziwei.term.t042`, `ziwei.term.t043`, `ziwei.term.t044`, `ziwei.term.t046`, `ziwei.term.t047`, `ziwei.term.t048`；Phase1 Rule `ziwei.rule.r011`。

已有 Phase2 / Golden / Variant：

- `ziwei.phase2.life_body` / `quanshu-lunar-iztro-mutagen-v1`；Golden：`ziwei.quanshu-fire-first-day`, `ziwei.chou-hour-mirror`, `ziwei.ren-explicit-iztro`；测试 `tests/test_phase2_ziwei.py`。
  Evidence C：`ziwei.source.quanshu` / 紫微斗数全书·古籍短选段（非现代白话） / 安十二宮例 / `安十二宮例; decoded-character interval [51577,51627)`，引文：一 命宮、二兄弟、三妻妾、四子女、五財帛、六疾厄、七遷移、八奴僕、九官祿、十田宅、十一福德、十二父母。
  Evidence C：`ziwei.source.quanshu-phase2` / 紫微斗数全书·古籍短选段（非现代白话） / 安身命例 / `bookChapters.json[19].blocks; fixed commit d725dd16b40cb60ec3a027309933deb364054644`，引文：大抵人命俱從寅上起正月，順數至本生月止，又自人生月起子時逆至本生時安命，順至本生時安身。。
  Evidence C：`ziwei.source.quanshu-phase2` / 紫微斗数全书·古籍短选段（非现代白话） / 安身命例 / `bookChapters.json[19].blocks; fixed commit d725dd16b40cb60ec3a027309933deb364054644`，引文：假如正月生子時就在寅宮安身命，丑時逆轉丑安命，順去卯安身，寅時逆轉子安命，順至辰安身，餘宮仿此，又若閏月正月生者要在二月內起安身命，凡有閏月具要依此為例，納音甲子歌誤要熟讀。。
  Evidence C：`ziwei.source.quanshu-phase2` / 紫微斗数全书·古籍短选段（非现代白话） / 安身命例 / `bookChapters.json[19].blocks; fixed commit d725dd16b40cb60ec3a027309933deb364054644`，引文：如甲生人安命在寅卻起甲己之年丙為首，是丙寅丁卯爐中火，卻去火局尋某日生期起紫微帝王，如是正月初一生者是火局，酉宮起初一日，就從酉宮起紫微，數無差遲，若錯了則失之毫釐，差之千里矣。。
- `ziwei.phase2.bureau` / `quanshu-lunar-iztro-mutagen-v1`；Golden：`ziwei.quanshu-fire-first-day`, `ziwei.chou-hour-mirror`, `ziwei.ren-explicit-iztro`；测试 `tests/test_phase2_ziwei.py`。
  Evidence C：`ziwei.source.quanshu` / 紫微斗数全书·古籍短选段（非现代白话） / 安南北斗諸星訣 / `安南北斗諸星訣; decoded-character interval [52470,52502)`，引文：紫微天機逆行旁，隔一陽武天同當，又隔二位廉貞地，空三復見紫微郎，。
  Evidence C：`ziwei.source.quanshu-phase2` / 紫微斗数全书·古籍短选段（非现代白话） / 起五行寅例 / `bookChapters.json[21].blocks; fixed commit d725dd16b40cb60ec3a027309933deb364054644`，引文：甲己之歲起丙寅，乙庚之歲起戊寅，丙辛之歲起庚寅，丁壬之歲起壬寅，戊癸之歲起甲寅。。
  Evidence C：`ziwei.source.quanshu-phase2` / 紫微斗数全书·古籍短选段（非现代白话） / 六十花甲子納音歌 / `bookChapters.json[22].blocks; fixed commit d725dd16b40cb60ec3a027309933deb364054644`，引文：甲子乙丑海中金，丙寅丁卯爐中火，戊辰己巳大林木，庚午辛未路旁土，壬申癸酉劍峰金，。
  Evidence C：`ziwei.source.quanshu-phase2` / 紫微斗数全书·古籍短选段（非现代白话） / 六十花甲子納音歌 / `bookChapters.json[22].blocks; fixed commit d725dd16b40cb60ec3a027309933deb364054644`，引文：甲戊乙亥山頭火，丙子丁丑澗下水，戊寅己卯城頭土，庚辰辛巳白蠟金，壬午癸未楊柳木，。
  Evidence C：`ziwei.source.quanshu-phase2` / 紫微斗数全书·古籍短选段（非现代白话） / 六十花甲子納音歌 / `bookChapters.json[22].blocks; fixed commit d725dd16b40cb60ec3a027309933deb364054644`，引文：甲申乙酉泉中水，丙戌丁亥屋上土，戊子己丑霹靂火，庚寅辛卯松柏木，壬辰癸巳長流水，。
  Evidence C：`ziwei.source.quanshu-phase2` / 紫微斗数全书·古籍短选段（非现代白话） / 六十花甲子納音歌 / `bookChapters.json[22].blocks; fixed commit d725dd16b40cb60ec3a027309933deb364054644`，引文：甲午乙未沙中金，丙申丁酉山下火，戊戌已亥平地木，庚子辛丑壁上土，壬寅癸卯金箔金，。
  Evidence C：`ziwei.source.quanshu-phase2` / 紫微斗数全书·古籍短选段（非现代白话） / 六十花甲子納音歌 / `bookChapters.json[22].blocks; fixed commit d725dd16b40cb60ec3a027309933deb364054644`，引文：甲辰乙巳覆燈火，丙午丁未天河水，戊申己酉大驛土，庚戌辛亥釵釧金，壬子癸丑桑拓木，。
  Evidence C：`ziwei.source.quanshu-phase2` / 紫微斗数全书·古籍短选段（非现代白话） / 六十花甲子納音歌 / `bookChapters.json[22].blocks; fixed commit d725dd16b40cb60ec3a027309933deb364054644`，引文：甲寅乙卯大溪水，丙辰丁巳沙中土，戊午己未天上火，庚申辛酉石榴木，壬戌癸亥大海水。。
- `ziwei.phase2.palaces` / `quanshu-lunar-iztro-mutagen-v1`；Golden：`ziwei.quanshu-fire-first-day`, `ziwei.chou-hour-mirror`, `ziwei.ren-explicit-iztro`；测试 `tests/test_phase2_ziwei.py`。
  Evidence C：`ziwei.source.quanshu` / 紫微斗数全书·古籍短选段（非现代白话） / 安十二宮例 / `安十二宮例; decoded-character interval [51577,51627)`，引文：一 命宮、二兄弟、三妻妾、四子女、五財帛、六疾厄、七遷移、八奴僕、九官祿、十田宅、十一福德、十二父母。
  Evidence C：`ziwei.source.quanshu-phase2` / 紫微斗数全书·古籍短选段（非现代白话） / 安十二宮例 / `bookChapters.json[20].blocks; fixed commit d725dd16b40cb60ec3a027309933deb364054644`，引文：一 命宮、二兄弟、三妻妾、四子女、五財帛、六疾厄、七遷移、八奴僕、九官祿、十田宅、十一福德、十二父母。
- `ziwei.phase2.major_stars` / `quanshu-lunar-iztro-mutagen-v1`；Golden：`ziwei.quanshu-fire-first-day`, `ziwei.chou-hour-mirror`, `ziwei.ren-explicit-iztro`；测试 `tests/test_phase2_ziwei.py`。
  Evidence C：`ziwei.source.quanshu` / 紫微斗数全书·古籍短选段（非现代白话） / 安南北斗諸星訣 / `安南北斗諸星訣; decoded-character interval [52470,52502)`，引文：紫微天機逆行旁，隔一陽武天同當，又隔二位廉貞地，空三復見紫微郎，。
  Evidence C：`ziwei.source.quanshu-phase2` / 紫微斗数全书·古籍短选段（非现代白话） / 安南北斗諸星訣 / `bookChapters.json[23].blocks; fixed commit d725dd16b40cb60ec3a027309933deb364054644`，引文：紫微天機逆行旁，隔一陽武天同當，又隔二位廉貞地，空三復見紫微郎，。
  Evidence C：`ziwei.source.quanshu-phase2` / 紫微斗数全书·古籍短选段（非现代白话） / 安南北斗諸星訣 / `bookChapters.json[23].blocks; fixed commit d725dd16b40cb60ec3a027309933deb364054644`，引文：天府太陰與貪狼，巨門天相及天梁，七殺空三破軍位，八星順數細推詳。。
  Evidence C：`ziwei.source.quanshu-phase2` / 紫微斗数全书·古籍短选段（非现代白话） / 安紫微天府圖 / `bookChapters.json[61].blocks; fixed commit d725dd16b40cb60ec3a027309933deb364054644`，引文：天府惟寅申二宮紫府同宮，餘
宮俱各填協作對如紫居丑則府
居卯矣。。
- `ziwei.phase2.auxiliary_stars` / `quanshu-lunar-iztro-mutagen-v1`；Golden：`ziwei.quanshu-fire-first-day`, `ziwei.chou-hour-mirror`, `ziwei.ren-explicit-iztro`；测试 `tests/test_phase2_ziwei.py`。
  Evidence C：`ziwei.source.quanshu` / 紫微斗数全书·古籍短选段（非现代白话） / 安祿存星訣 / `安祿存星訣; decoded-character interval [53601,53641)`，引文：甲生祿存在寅宮，乙生在卯丙戊巳，丁己祿存停午方，庚祿居申辛祿酉，壬祿在亥癸祿子。。
  Evidence C：`ziwei.source.quanshu` / 紫微斗数全书·古籍短选段（非现代白话） / 安天馬星訣 / `安天馬星訣; decoded-character interval [53368,53400)`，引文：寅午戍人馬居申，申子辰人馬居寅，巳酉丑人馬居亥，亥卯未人馬居巳。。
  Evidence C：`ziwei.source.quanshu` / 紫微斗数全书·古籍短选段（非现代白话） / 安左輔右弼星訣 / `安左輔右弼星訣; decoded-character interval [52942,52974)`，引文：左輔正月起於辰，順逢生月是貴方，右弼正月宮尋戌，逆至正月便調停。。
  Evidence C：`ziwei.source.quanshu` / 紫微斗数全书·古籍短选段（非现代白话） / 安文昌文曲星訣 / `安文昌文曲星訣; decoded-character interval [52668,52700)`，引文：子時戌上起文昌，逆到生時是貴鄉，文曲數從辰上起，順到生時是本鄉。。
  Evidence C：`ziwei.source.quanshu` / 紫微斗数全书·古籍短选段（非现代白话） / 天空地劫訣 / `天空地劫訣; decoded-character interval [54414,54430)`，引文：亥上起子順安劫，逆向便是天空鄉。。
- `ziwei.phase2.mutagens` / `quanshu-lunar-iztro-mutagen-v1`；Golden：`ziwei.quanshu-fire-first-day`, `ziwei.chou-hour-mirror`, `ziwei.ren-explicit-iztro`；测试 `tests/test_phase2_ziwei.py`。
  Evidence C：`ziwei.source.quanshu` / 紫微斗数全书·古籍短选段（非现代白话） / 安祿權科忌四星變化訣 / `安祿權科忌四星變化訣; decoded-character interval [54194,54224)`，引文：如甲生人廉貞化祿、破軍化權、武曲化科、太陽化忌是也，餘仿此。。

当前场景可输出结论（只描述事实，不追加吉凶含义）：

- 无已接入的结构 claim；引擎能力如上，场景接线须另审。

当前禁止结论：大限流年吉凶；庙旺吉凶；闰月自动猜排。

缺失能力 / 依赖 / 下一批：

- `ziwei-professional`：基本星宫结构已执行；缺亮度/三方四正/宫位解释/大限流年；闰月未裁定，四化D约定不能升古籍结论。
  下一批复核现有 `ziwei.source.quanshu`，沿原模型补规则条件及 Golden。

## 奇门专业工具 · PARTIAL

Scenario：`None`；已执行=False；现有结构公开标志=False；AI=false。

已有知识、Rule 与 Evidence：

- 奇门专业能力：Terms `qimen.term.t001`, `qimen.term.t002`, `qimen.term.t003`, `qimen.term.t004`, `qimen.term.t005`, `qimen.term.t006`, `qimen.term.t007`, `qimen.term.t008`, `qimen.term.t011`, `qimen.term.t012`, `qimen.term.t013`, `qimen.term.t014`, `qimen.term.t015`；Phase1 Rule `qimen.rule.r002`, `qimen.rule.r003`, `qimen.rule.r004`。

已有 Phase2 / Golden / Variant：

- `qimen.phase2.calendar` / `qfdk-exact-term-midnight-v2`；Golden：`qimen.jiazi-winter`, `qimen.summer-before`, `qimen.summer-at`, `qimen.late-zi-midnight`；测试 `tests/test_phase2_qimen.py`。
  Evidence C：`qimen.source.baojian` / 奇门宝鉴御定 / 基础选段（编者定位） / `基础选段（编者定位）; decoded-character interval [1286,1298)`，引文：一节三元、二十四气备矣。。
  Evidence C：`qimen.source.tongzong` / 奇门遁甲统宗 / 基础选段（编者定位） / `基础选段（编者定位）; decoded-character interval [10331,10352)`，引文：一元五日，以甲己二干为一元之首，谓之符头。。
  Evidence C：`qimen.source.baojian` / 奇门宝鉴御定 / 基础选段（编者定位） / `基础选段（编者定位）; decoded-character interval [8552,8571)`，引文：本局地盘不动，以天盘甲子戊加乙于九宫。。
- `qimen.phase2.bureau` / `qfdk-exact-term-midnight-v2`；Golden：`qimen.jiazi-winter`, `qimen.summer-before`, `qimen.summer-at`, `qimen.late-zi-midnight`；测试 `tests/test_phase2_qimen.py`。
  Evidence C：`qimen.source.tongzong` / 奇门遁甲统宗 / 基础选段（编者定位） / `基础选段（编者定位）; decoded-character interval [10331,10352)`，引文：一元五日，以甲己二干为一元之首，谓之符头。。
  Evidence C：`qimen.source.tongzong` / 奇门遁甲统宗 / 基础选段（编者定位） / `基础选段（编者定位）; decoded-character interval [10352,10388)`，引文：符头所临之支值子午卯酉则为上元；值寅申巳亥则为中元；值辰戌丑未则为下元。。
  Evidence C：`qimen.source.tongzong` / 奇门遁甲统宗 / 基础选段（编者定位） / `基础选段（编者定位）; decoded-character interval [4851,4860)`，引文：自夏至气降起离九宫。
  Evidence C：`qimen.source.tongzong` / 奇门遁甲统宗 / 基础选段（编者定位） / `基础选段（编者定位）; decoded-character interval [4758,4767)`，引文：自冬至阳生起坎一宫。
- `qimen.phase2.earth` / `qfdk-exact-term-midnight-v2`；Golden：`qimen.jiazi-winter`, `qimen.summer-before`, `qimen.summer-at`, `qimen.late-zi-midnight`；测试 `tests/test_phase2_qimen.py`。
  Evidence C：`qimen.source.baojian` / 奇门宝鉴御定 / 基础选段（编者定位） / `基础选段（编者定位）; decoded-character interval [2406,2426)`，引文：乙为日奇、丙为月奇、丁为星奇，故名三奇。。
  Evidence C：`qimen.source.baojian` / 奇门宝鉴御定 / 基础选段（编者定位） / `基础选段（编者定位）; decoded-character interval [2437,2452)`，引文：戊己庚辛壬癸，皆有六甲遁乎其中。
- `qimen.phase2.chiefs` / `qfdk-exact-term-midnight-v2`；Golden：`qimen.jiazi-winter`, `qimen.summer-before`, `qimen.summer-at`, `qimen.late-zi-midnight`；测试 `tests/test_phase2_qimen.py`。
  Evidence C：`qimen.source.baojian` / 奇门宝鉴御定 / 基础选段（编者定位） / `基础选段（编者定位）; decoded-character interval [8552,8571)`，引文：本局地盘不动，以天盘甲子戊加乙于九宫。。
  Evidence C：`qimen.source.tongzong` / 奇门遁甲统宗 / 基础选段（编者定位） / `基础选段（编者定位）; decoded-character interval [10496,10519)`，引文：地盘旬首所临之宫，其星即为值符，其门即为值使。。
  Evidence C：`qimen.source.baojian` / 奇门宝鉴御定 / 基础选段（编者定位） / `基础选段（编者定位）; decoded-character interval [3302,3331)`，引文：八神者；天乙、螣蛇、太阴、六合、朱雀、白虎、九地、九天也。。
- `qimen.phase2.plates` / `qfdk-exact-term-midnight-v2`；Golden：`qimen.jiazi-winter`, `qimen.summer-before`, `qimen.summer-at`, `qimen.late-zi-midnight`；测试 `tests/test_phase2_qimen.py`。
  Evidence C：`qimen.source.baojian` / 奇门宝鉴御定 / 基础选段（编者定位） / `基础选段（编者定位）; decoded-character interval [8552,8571)`，引文：本局地盘不动，以天盘甲子戊加乙于九宫。。
  Evidence C：`qimen.source.tongzong` / 奇门遁甲统宗 / 基础选段（编者定位） / `基础选段（编者定位）; decoded-character interval [10496,10519)`，引文：地盘旬首所临之宫，其星即为值符，其门即为值使。。
  Evidence C：`qimen.source.baojian` / 奇门宝鉴御定 / 基础选段（编者定位） / `基础选段（编者定位）; decoded-character interval [3302,3331)`，引文：八神者；天乙、螣蛇、太阴、六合、朱雀、白虎、九地、九天也。。

当前场景可输出结论（只描述事实，不追加吉凶含义）：

- 无已接入的结构 claim；引擎能力如上，场景接线须另审。

当前禁止结论：格局吉凶；择时胜率；置闰超接盘。

缺失能力 / 依赖 / 下一批：

- `qimen-professional`：指定精确节气转盘结构已执行；缺格局/用神解释；置闰、超接及其他盘法未实现。
  下一批复核现有 `qimen.source.baojian`, `qimen.source.tongzong`，沿原模型补规则条件及 Golden。

## 六壬专业工具 · PARTIAL

Scenario：`None`；已执行=False；现有结构公开标志=False；AI=false。

已有知识、Rule 与 Evidence：

- 六壬专业能力：Terms `liuren.term.t001`, `liuren.term.t002`, `liuren.term.t003`, `liuren.term.t004`, `liuren.term.t005`, `liuren.term.t006`, `liuren.term.t007`, `liuren.term.t011`, `liuren.term.t012`, `liuren.term.t013`, `liuren.term.t014`, `liuren.term.t015`, `liuren.term.t016`, `liuren.term.t017`, `liuren.term.t018`, `liuren.term.t019`；Phase1 Rule `liuren.rule.r001`, `liuren.rule.r002`, `liuren.rule.r003`, `liuren.rule.r004`, `liuren.rule.r005`, `liuren.rule.r006`, `liuren.rule.r007`, `liuren.rule.r008`, `liuren.rule.r009`, `liuren.rule.r010`, `liuren.rule.r011`, `liuren.rule.r012`, `liuren.rule.r013`, `liuren.rule.r014`。

已有 Phase2 / Golden / Variant：

- `liuren.phase2.month_general` / `daquan-nine-methods-lodged-stems-v1`；Golden：`liuren.zeike`, `liuren.biyong`, `liuren.shehai`, `liuren.yaoke`, `liuren.maoxing`, `liuren.bieze`, `liuren.bazhuan`, `liuren.fuyin`, `liuren.fanyin`, `liuren.fanyin-no-controls`, `liuren.biyong-upstream-crash`；测试 `tests/test_phase2_liuren.py`。
  Evidence C：`liuren.source.daquan` / 六壬大全 / 基础选段（编者定位） / `基础选段（编者定位）; decoded-character interval [70888,70903)`，引文：月将加于正时，用五行论其克贼。。
- `liuren.phase2.plates` / `daquan-nine-methods-lodged-stems-v1`；Golden：`liuren.zeike`, `liuren.biyong`, `liuren.shehai`, `liuren.yaoke`, `liuren.maoxing`, `liuren.bieze`, `liuren.bazhuan`, `liuren.fuyin`, `liuren.fanyin`, `liuren.fanyin-no-controls`, `liuren.biyong-upstream-crash`；测试 `tests/test_phase2_liuren.py`。
  Evidence C：`liuren.source.daquan` / 六壬大全 / 基础选段（编者定位） / `基础选段（编者定位）; decoded-character interval [70888,70903)`，引文：月将加于正时，用五行论其克贼。。
- `liuren.phase2.lessons` / `daquan-nine-methods-lodged-stems-v1`；Golden：`liuren.zeike`, `liuren.biyong`, `liuren.shehai`, `liuren.yaoke`, `liuren.maoxing`, `liuren.bieze`, `liuren.bazhuan`, `liuren.fuyin`, `liuren.fanyin`, `liuren.fanyin-no-controls`, `liuren.biyong-upstream-crash`；测试 `tests/test_phase2_liuren.py`。
  Evidence C：`liuren.source.daquan` / 六壬大全 / 基础选段（编者定位） / `基础选段（编者定位）; decoded-character interval [1120,1159)`，引文：甲课寅兮乙课辰，丙戊课巳不须论。丁己课未庚申上，辛戌壬亥是其真。癸课原来丑宫坐。
  Evidence C：`liuren.source.zhinan` / 六壬指南 / 基础选段（编者定位） / `基础选段（编者定位）; decoded-character interval [1566,1642)`，引文：干上阳神为第一课，乃阳中之阳也；地支阴也，支上得者曰辰，支上阳神为第三课，乃阴中之阳也；干上阴神为第二课，乃阳中之阴也；支上阴神为第四课，乃阴中之阴也。。
- `liuren.phase2.zeike` / `daquan-nine-methods-lodged-stems-v1`；Golden：`liuren.zeike`, `liuren.biyong`, `liuren.shehai`, `liuren.yaoke`, `liuren.maoxing`, `liuren.bieze`, `liuren.bazhuan`, `liuren.fuyin`, `liuren.fanyin`, `liuren.fanyin-no-controls`, `liuren.biyong-upstream-crash`；测试 `tests/test_phase2_liuren.py`。
  Evidence C：`liuren.source.daquan` / 六壬大全 / 九宗门·贼克 / `九宗门·贼克; decoded-character interval [1190,1206)`，引文：取课先从下贼呼，如无下贼上克初。。
- `liuren.phase2.biyong` / `daquan-nine-methods-lodged-stems-v1`；Golden：`liuren.zeike`, `liuren.biyong`, `liuren.shehai`, `liuren.yaoke`, `liuren.maoxing`, `liuren.bieze`, `liuren.bazhuan`, `liuren.fuyin`, `liuren.fanyin`, `liuren.fanyin-no-controls`, `liuren.biyong-upstream-crash`；测试 `tests/test_phase2_liuren.py`。
  Evidence C：`liuren.source.daquan` / 六壬大全 / 九宗门·比用 / `九宗门·比用; decoded-character interval [1265,1281)`，引文：常将天日比神用，阳日用阳阴用阴。。
- `liuren.phase2.shehai` / `daquan-nine-methods-lodged-stems-v1`；Golden：`liuren.zeike`, `liuren.biyong`, `liuren.shehai`, `liuren.yaoke`, `liuren.maoxing`, `liuren.bieze`, `liuren.bazhuan`, `liuren.fuyin`, `liuren.fanyin`, `liuren.fanyin-no-controls`, `liuren.biyong-upstream-crash`；测试 `tests/test_phase2_liuren.py`。
  Evidence C：`liuren.source.daquan` / 六壬大全 / 九宗门·涉害 / `九宗门·涉害; decoded-character interval [1304,1336)`，引文：渉害行来本家止，路逢多克为用取。孟深仲浅季当休，复等柔辰刚日宜。。
- `liuren.phase2.yaoke` / `daquan-nine-methods-lodged-stems-v1`；Golden：`liuren.zeike`, `liuren.biyong`, `liuren.shehai`, `liuren.yaoke`, `liuren.maoxing`, `liuren.bieze`, `liuren.bazhuan`, `liuren.fuyin`, `liuren.fanyin`, `liuren.fanyin-no-controls`, `liuren.biyong-upstream-crash`；测试 `tests/test_phase2_liuren.py`。
  Evidence C：`liuren.source.daquan` / 六壬大全 / 九宗门·遥克 / `九宗门·遥克; decoded-character interval [1359,1391)`，引文：四课无克号为遥，日与神兮逓互招。先取神遥克其日，如无方取日来遥。。
- `liuren.phase2.maoxing` / `daquan-nine-methods-lodged-stems-v1`；Golden：`liuren.zeike`, `liuren.biyong`, `liuren.shehai`, `liuren.yaoke`, `liuren.maoxing`, `liuren.bieze`, `liuren.bazhuan`, `liuren.fuyin`, `liuren.fanyin`, `liuren.fanyin-no-controls`, `liuren.biyong-upstream-crash`；测试 `tests/test_phase2_liuren.py`。
  Evidence C：`liuren.source.daquan` / 六壬大全 / 九宗门·昴星 / `九宗门·昴星; decoded-character interval [1430,1445)`，引文：无遥无克昴星穷，阳仰阴俯酉位中。
- `liuren.phase2.bieze` / `daquan-nine-methods-lodged-stems-v1`；Golden：`liuren.zeike`, `liuren.biyong`, `liuren.shehai`, `liuren.yaoke`, `liuren.maoxing`, `liuren.bieze`, `liuren.bazhuan`, `liuren.fuyin`, `liuren.fanyin`, `liuren.fanyin-no-controls`, `liuren.biyong-upstream-crash`；测试 `tests/test_phase2_liuren.py`。
  Evidence C：`liuren.source.daquan` / 六壬大全 / 九宗门·别责 / `九宗门·别责; decoded-character interval [1510,1542)`，引文：四课不全三课备，无遥无克别责例。刚日干合上头神，柔日支前三合取。。
- `liuren.phase2.bazhuan` / `daquan-nine-methods-lodged-stems-v1`；Golden：`liuren.zeike`, `liuren.biyong`, `liuren.shehai`, `liuren.yaoke`, `liuren.maoxing`, `liuren.bieze`, `liuren.bazhuan`, `liuren.fuyin`, `liuren.fanyin`, `liuren.fanyin-no-controls`, `liuren.biyong-upstream-crash`；测试 `tests/test_phase2_liuren.py`。
  Evidence C：`liuren.source.daquan` / 六壬大全 / 九宗门·八专 / `九宗门·八专; decoded-character interval [1634,1670)`，引文：两课无克号八专，阳日日阳顺行三连本位数。阴日辰阴逆三位，中末总向日上眠。。
- `liuren.phase2.fuyin` / `daquan-nine-methods-lodged-stems-v1`；Golden：`liuren.zeike`, `liuren.biyong`, `liuren.shehai`, `liuren.yaoke`, `liuren.maoxing`, `liuren.bieze`, `liuren.bazhuan`, `liuren.fuyin`, `liuren.fanyin`, `liuren.fanyin-no-controls`, `liuren.biyong-upstream-crash`；测试 `tests/test_phase2_liuren.py`。
  Evidence C：`liuren.source.daquan` / 六壬大全 / 九宗门·伏吟 / `九宗门·伏吟; decoded-character interval [1677,1700)`，引文：伏吟有克还为用，无克刚干柔取辰。迤逦刑之作中末。
- `liuren.phase2.fanyin` / `daquan-nine-methods-lodged-stems-v1`；Golden：`liuren.zeike`, `liuren.biyong`, `liuren.shehai`, `liuren.yaoke`, `liuren.maoxing`, `liuren.bieze`, `liuren.bazhuan`, `liuren.fuyin`, `liuren.fanyin`, `liuren.fanyin-no-controls`, `liuren.biyong-upstream-crash`；测试 `tests/test_phase2_liuren.py`。
  Evidence C：`liuren.source.daquan` / 六壬大全 / 九宗门·返吟 / `九宗门·返吟; decoded-character interval [1750,1766)`，引文：返吟有克亦为用，无克别有井栏名。。

当前场景可输出结论（只描述事实，不追加吉凶含义）：

- 无已接入的结构 claim；引擎能力如上，场景接线须另审。

当前禁止结论：十二天将已排；类神吉凶；应期。

缺失能力 / 依赖 / 下一批：

- `liuren-professional`：九宗门结构已执行；贵人双表/天后异文保留，缺神将排布、类神、旺衰与占类解释。
  下一批复核现有 `liuren.source.daquan`, `liuren.source.zhinan`，沿原模型补规则条件及 Golden。

## 风水专业工具 · PARTIAL

Scenario：`None`；已执行=False；现有结构公开标志=False；AI=false。

已有知识、Rule 与 Evidence：

- 风水专业能力：Terms `fengshui.term.t016`, `fengshui.term.t017`, `fengshui.term.t019`, `fengshui.term.t020`；Phase1 Rule `fengshui.rule.r002`。

已有 Phase2 / Golden / Variant：

- `fengshui.phase2.compass` / `compass-half-open-explicit-epoch-v1`；Golden：`fengshui.north-wrap`, `fengshui.boundary-gui`, `fengshui.gen-boundary`, `fengshui.research-period-transition`；测试 `tests/test_phase2_fengshui.py`。
  Evidence C：`fengshui.source.dibian` / 地理辨正 / 基础选段（编者定位） / `基础选段（编者定位）; decoded-character interval [1178,1191)`，引文：二十四山阴阳不一，吉凶无定。

当前场景可输出结论（只描述事实，不追加吉凶含义）：

- 无已接入的结构 claim；引擎能力如上，场景接线须另审。

当前禁止结论：飞星吉凶；宅运财运；绝对三元九运生产判断。

缺失能力 / 依赖 / 下一批：

- `fengshui-professional`：生产计算只支持二十四山定位；三元绝对纪元仍研究，缺八宅/三元/玄空各自执行和解释，不串体系。
  下一批复核现有 `fengshui.source.dibian`, `fengshui.source.yangzhai`，沿原模型补规则条件及 Golden。

## 周易专业工具 · PARTIAL

Scenario：`None`；已执行=False；现有结构公开标志=False；AI=false。

已有知识、Rule 与 Evidence：

- 周易专业能力：Terms `yijing.term.t003`, `yijing.term.t004`, `yijing.term.t005`, `yijing.term.t006`, `yijing.term.t008`, `yijing.term.t010`, `yijing.term.t011`；Phase1 Rule `yijing.rule.r001`, `yijing.rule.r002`, `yijing.rule.r003`, `yijing.rule.r004`, `yijing.rule.r005`, `yijing.rule.r006`。

已有 Phase2 / Golden / Variant：

- `yijing.phase2.structure` / `bottom-up-six-lines-v1`；Golden：`yijing.qian-first-change`, `yijing.tai-relations`, `yijing.zhun-nuclear`；测试 `tests/test_phase2_yijing.py`。
  Evidence C：`yijing.source.xici` / 易传（十翼） / 系辞上·大衍之数 / `系辞上·大衍之数; decoded-character interval [1840,1856)`，引文：八卦而小成。引而伸之，触类而长之。
- `yijing.phase2.change` / `bottom-up-six-lines-v1`；Golden：`yijing.qian-first-change`, `yijing.tai-relations`, `yijing.zhun-nuclear`；测试 `tests/test_phase2_yijing.py`。
  Evidence C：`yijing.source.meihua` / 梅花易数 / 基础选段（编者定位） / `基础选段（编者定位）; decoded-character interval [2433,2459)`，引文：若一爻动，则看此一爻，是阳爻则变阴爻，阴爻则变阳爻。。
- `yijing.phase2.opposite` / `bottom-up-six-lines-v1`；Golden：`yijing.qian-first-change`, `yijing.tai-relations`, `yijing.zhun-nuclear`；测试 `tests/test_phase2_yijing.py`。
  Evidence C：`yijing.source.shuogua` / 易传（十翼） / 说卦·基础选段（编者定位） / `基础选段（编者定位）; decoded-character interval [231,235)`，引文：八卦相错。
- `yijing.phase2.inverse` / `bottom-up-six-lines-v1`；Golden：`yijing.qian-first-change`, `yijing.tai-relations`, `yijing.zhun-nuclear`；测试 `tests/test_phase2_yijing.py`。
  Evidence C：`yijing.source.xici` / 易传（十翼） / 系辞上·基础选段（编者定位） / `基础选段（编者定位）; decoded-character interval [2004,2013)`，引文：参伍以变，错综其数。
- `yijing.phase2.nuclear` / `bottom-up-six-lines-v1`；Golden：`yijing.qian-first-change`, `yijing.tai-relations`, `yijing.zhun-nuclear`；测试 `tests/test_phase2_yijing.py`。
  Evidence C：`yijing.source.meihua` / 梅花易数 / 基础选段（编者定位） / `基础选段（编者定位）; decoded-character interval [2493,2522)`，引文：互卦以重卦去了初爻及第六爻，以中间四爻分作两卦，看得何卦。。

当前场景可输出结论（只描述事实，不追加吉凶含义）：

- 无已接入的结构 claim；引擎能力如上，场景接线须另审。

当前禁止结论：卦义直接推具体事件；未来概率；后世术数冒充原义。

缺失能力 / 依赖 / 下一批：

- `yijing-professional`：结构和卦爻文本可追溯；缺面向事件的解释规则；经典原义与后世术数解释必须分开。
  下一批复核现有 `yijing.source.meihua`, `yijing.source.shuogua`, `yijing.source.xici`，沿原模型补规则条件及 Golden。
