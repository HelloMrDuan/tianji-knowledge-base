"""渊海子平印组两节逐节登记（TJ-012.3 Slice D 就绪度复审排序第一前置：渊海逐节登记·第四组）。

正官组（E0236/E0237）、七杀组（E0282/E0283）与财组（E0284/E0285）
之后续登印组：《论印綬》于正官组只登记了与正官/官杀论述直接
相关的 7 个窗口，其余 12 段逐段登记跳过理由（理由均为非正官
论述）；本批逐段复核后整节补全——12 段全部属印綬论述主体，
补登为本批引文，既有 7 窗与既有 s057–s059 三窗只登记引用
关系、不重复登记。《论倒食》为偏印本体节，财组批曾以「偏印
专题、财食为受损对象而非论述主体」列为未登记，本批正面处置
整节登记入印组。全书无独立《论正印》《论偏印》节（机上实测
「论正印」「论偏印」出现 0 次），印綬一节统论正印、偏印
（s057 定义分正偏，在册）。

本批登记范围（机上密封快照实测，快照 SHA256 与登记 Source 一致）：
- 《论印綬》[12506, 13494) 整节登记（988 字，全文窗）；
- 《论倒食》[14119, 14566) 整节登记（447 字，全文窗）；
- 已登记印綬节内引文 10 条（正官组 7 窗 + s057–s059 三窗）
只登记引用关系，不重复登记。

缺字纪律：两节范围内半角 ? 占位共 2 处（均在《论印綬》：
12518、12557），已于正官组登记为 yh-gap-04/05，本批按节
归属在案、内容逐字不变，维持 placeholder_unresolved——原文
保留 ?、不猜填；含缺字分句不作引文读法依据，全部 operative
引文窗口避开缺字位点。
字形纪律：例造「生气是丙丁火属木故也」语义存疑、倒食「吞啗煞」
啗字异体、倒食例造「三丁食己」语义存疑、「容貌攲斜」攲字
异体、「纔交」纔字异体，逐项落账，无见证者不给
mapped_reading；印綬节题缺《字与官鬼多言之/论两形已于正官组
落账（yh-glyph-02/04），本批不重复登记。

转手复核（本批核心登记结论）：印组可操作句逐条标注转手门。
全部经未建层中的至少一门转手：财破印效力、偏印夺食效力、
食神生财链、制杀效力、长生阶段（生旺/死绝之地）、印綬多寡
数量比较与印格成立本身；身旺本身罕见出场（仅财多乘旺两句
沿既有 s057「忌财旺破印」的强度口径标注）。登记后印格
determination 仍为 None（详见 YUANHAI_YIN_ROUTING_REVIEW）。

特别纪律：本登记不含任何健康/寿命预测口径——节内「一生
少病」「寿元耐久」「必夭其寿」「福浅寿薄」「即入黄泉」等
均为原文断语与例造叙事，按断语登记存在，不构成由印格推断
健康、寿命或六亲境遇的字段或规则。

本模块是纯数据登记，**零 determination 代码**：不写任何印格
成格/破格判定，不改变 candidates 与既有登记语义；登记不等于
可裁定。引文全部经机上快照切片逐字复核（全文计数==1；既有
窗口以引用关系在案者以其原登记为准）。
Canonical/Phase1 注册状态 pending（与既有研究级登记同口径披露）。
"""


YUANHAI_YIN_ID = 'bazi-yuanhai-yin-registration-v1'

YUANHAI_YIN_TASK = 'TJ-012.3 Slice D prerequisite (yuanhai seal group registration)'

YUANHAI_SNAPSHOT = {'file': 'yuanhai_ziping.txt',
 'snapshot_path': 'data/quarantine/public_domain_snapshots/daizhigev20/yuanhai_ziping.txt',
 'sha256': 'c8f45d3228fb1958012139139a83edd019e7c2db881998d2d0bba65107417cf9',
 'bytes': 154655,
 'chars': 58905,
 'blob_sha': 'f945a48cbedf5883808a72bb6f544a4dca603cb3'}

YUANHAI_YIN_SECTIONS = [{'section_id': 'yuanhai.yinshou',
  'title': '论印綬',
  'source_id': 'bazi.source.yuanhai',
  'locator': {'char_start': 12506, 'char_end': 13494},
  'registration_mode': 'full_section',
  'full_text': '论 印 綬》 \n'
               ' '
               '所谓印?生我者,即印綬也,经曰:『有官无印,即非真官;有印无官,反成其福。』何以言之?大抵人生得物以相助相生相养,使我得万物之见成,岂不妙乎;故主人多智虑,兼丰厚。\n'
               ' 盖印綬畏财,主人括囊。故四柱中及运行官贵,反成其福,盖官鬼能生我;只畏其财,而财能反伤我。\n'
               ' 此印綬之妙者,多是受父母之荫、承父之貲财,见成安享之人;若又以两三命相併,当以印綬多者为上。\n'
               ' 又主一生少病、能饮食。\n'
               ' 或若财多乘旺,必多淹留。\n'
               ' 虽喜官鬼,而官鬼多或入格,又不可专以印綬言之。\n'
               ' '
               '假如,甲乙日得亥子月生,丙丁日得寅卯月生,戊己日得巳午月生,庚辛日得辰戌丑未月生,壬癸日得申酉月生者是也,其餘以类言之。最怕行印綬死绝之运;或运临死绝,复有物以窃之,即入黄泉,无可疑也。\n'
               ' 夫印綬者,生我之谓也,亦名生气。以阳见阴,以阴见阳,谓之正印;阳见阳,阴见阴,谓之偏印。喜官星生印,忌财旺破印。\n'
               ' 如甲人生亥子月中,水为印,忌火伤官,忌土破印,要行生旺之乡,怕行死绝之地;若行死绝之地,或有物以伤之,则危矣!\n'
               ' 印綬之人智虑、一生少病、能饱食丰厚、享见成财禄;若两三命相併,当以印綬多者取之。\n'
               ' 最忌财来乘旺,必生淹滞。\n'
               ' 若官鬼多,或入别格,又不可专以印綬论。\n'
               ' 大凡月与时上见者为妙;而月上最为紧要。\n'
               ' 先论月气之后有生气,必得父母之力;年下有生气,必得祖宗之力;于时上见之有生气,必得子孙之力,寿元耐久,晚景优游。\n'
               ' 如带印綬,须带官星,谓之官印两全,必为贵命。若官星虽见成,得父母力,为福亦厚也;须行官星运便发,或行印綬运亦发。\n'
               ' 若用官不显,用印綬为妙;最怕四柱中岁运临财乡,以伤其印。\n'
               ' 若伤印,主破家离祖、出赘;又临死绝之地,若非降官失职,必夭其寿。\n'
               ' 如【戊戌,庚申,癸酉,庚申】:此命癸日生于七月中气之后,月时皆是庚申,自坐金库,所以印綬;岁干又透出戊官,谓之官印两全,极为贵命。\n'
               ' 如【癸亥,癸亥,甲寅,甲子】:此日用癸为印,印却旺;缘无财星相助,发福不厚也。\n'
               ' 如【甲寅,庚午,戊戌,壬子】:此日戊用丁为印綬,有寅午戌火局为好;不合时上壬子水旺,财能冲印,所以失明。生气是丙丁火属木故也。\n'
               ' '
               '如【己卯,丁卯,丙辰,壬辰】:此命用卯为印,用癸为官,年在卯日在辰,所以官印两全,少年清要。至四十二、三岁,癸亥运亦不妨;至庚申年,水七杀生于申,乃被庚申破印,故不吉也。\n'
               ' ',
  'note': '整节登记（988 字）。正官组（E0236/E0237）只登记与正官/官杀论述直接相关的 7 个窗口、其余 12 段逐段登记跳过理由；本批逐段复核后整节补全：既有 7 '
          '窗与既有 s057–s059 三窗只登记引用关系（YUANHAI_YIN_CROSS_REFERENCES），不重复登记引文，未登记 12 '
          '段全部补登为本批引文。节题于快照中作「论 印 綬》」、缺开首《字（正官组 yh-glyph-02 已落账，本批不重复登记）；节内 2 处半角 ? '
          '占位（12518、12557）已于正官组登记为 yh-gap-04/05，本批按节归属在案、内容逐字不变。'},
 {'section_id': 'yuanhai.daoshi',
  'title': '论倒食',
  'source_id': 'bazi.source.yuanhai',
  'locator': {'char_start': 14119, 'char_end': 14566},
  'registration_mode': 'full_section',
  'full_text': '《论 倒 食》 \n'
               ' 夫倒食者,冲财神之谓也;一名『吞啗煞』。用财神大忌见之,用食神亦忌见之。\n'
               ' 倒食者,如甲见壬之类。如甲见丙为食神,能生土财;然壬剋丙火,丙火不能生甲木之土财,所谓甲用食神,大忌见之。\n'
               ' 凡命中带此二者,主福浅寿薄。\n'
               ' '
               '又见庚为七杀,得丙丁火制之,怕见水,反为祸矣!凡命中犯此者,犹尊长之制我身,不得自由也。作事进退悔懒、有始无终、财源屡成屡败、容貌攲斜、身品矮小、胆怯心慌,凡事无成也。\n'
               ' '
               '如【丁未,丁未,己亥,丁卯】:此命己亥日,己临亥上,身弱于亥;加以亥卯未木局剋身,年月时透出三丁食己。幼年行南方运,赖火生土,身犹旺;纔交乙巳运,为己之七杀,引出亥卯未木局,岁运癸亥,所以死矣!此命非但倒食七杀之祸,而癸亥年与生杀坏印之说同义也。\n'
               ' '
               '如【甲戌,丙寅,甲戌,壬申】:此命甲戌日,甲见丙食神,生于正月,甲木旺,身与食神俱旺,本是贵命;不合时上壬申,壬水伤其丙火,申金冲其寅木;又申中有庚七杀,所以利名无成。行己巳运金生之地,见庚子年;庚金为七杀,又见子水,死于非命。\n'
               ' \n',
  'note': '整节登记（447 '
          '字）。倒食即偏印之别名（节内以甲见壬立例：壬为甲之偏印，壬剋丙火夺食）；财组批（E0284）曾以「偏印专题、财与食为受损对象而非论述主体」列为未登记，本批印组按论述主体归属正面处置、整节登记入印组。节内无半角 '
          '? 占位、无 PUA 字符。'}]

YUANHAI_YIN_QUOTES = [{'id': 'yh.yn_shengwo_doctrine',
  'source_id': 'bazi.source.yuanhai',
  'source_section_id': 'yuanhai.yinshou',
  'role': 'doctrine_observation',
  'quote': '大抵人生得物以相助相生相养,使我得万物之见成,岂不妙乎',
  'locator': {'char_start': 12558, 'char_end': 12585},
  'operative': False,
  'routed_through_strength': None,
  'note': '得物相助 doctrine 句（紧接含缺字分句「何以言之?」之后，窗口避开缺字位点 '
          '12557）：人生得物以相助相生相养、得万物之见成，为印綬立论总纲，非条件句；其后性情断语另行登记。此段在正官组未立引文窗，本批补登。'},
 {'id': 'yh.yn_character_zhilü',
  'source_id': 'bazi.source.yuanhai',
  'source_section_id': 'yuanhai.yinshou',
  'role': 'character_claim',
  'quote': '故主人多智虑,兼丰厚。',
  'locator': {'char_start': 12586, 'char_end': 12597},
  'operative': False,
  'routed_through_strength': None,
  'note': '性情/厚薄断语（主人多智虑、兼丰厚）：陈述性断语，只登记存在、不作裁定，不构成任何性情判断口径。'},
 {'id': 'yh.yn_parents_yin',
  'source_id': 'bazi.source.yuanhai',
  'source_section_id': 'yuanhai.yinshou',
  'role': 'fortune_claim',
  'quote': '此印綬之妙者,多是受父母之荫、承父之貲财,见成安享之人',
  'locator': {'char_start': 12646, 'char_end': 12673},
  'operative': False,
  'routed_through_strength': None,
  'note': '见成安享断语（受父母之荫、承父之貲财）：出身/境遇断语，只登记存在、不作裁定。正官组跳过清单第 1 段前半，本批整节补全后补登。'},
 {'id': 'yh.yn_more_is_upper',
  'source_id': 'bazi.source.yuanhai',
  'source_section_id': 'yuanhai.yinshou',
  'role': 'operative_candidate',
  'quote': '若又以两三命相併,当以印綬多者为上。',
  'locator': {'char_start': 12674, 'char_end': 12692},
  'operative': True,
  'routed_through_strength': False,
  'note': '两命相併比较句：以印綬多者为上——多寡比较无阈值、无已裁定标尺，不可执行。正官组跳过清单第 1 段后半，本批补登。',
  'routed_through_other': ['印綬多寡的数量比较未阈值化（以多寡分上下的计数口径未裁定，不作计数判定）']},
 {'id': 'yh.yn_few_illness',
  'source_id': 'bazi.source.yuanhai',
  'source_section_id': 'yuanhai.yinshou',
  'role': 'character_claim',
  'quote': '又主一生少病、能饮食。',
  'locator': {'char_start': 12694, 'char_end': 12705},
  'operative': False,
  'routed_through_strength': None,
  'note': '健康陈述断语（一生少病、能饮食）：只登记存在、不作裁定，不构成任何健康判断口径。正官组跳过清单第 2 段，本批补登。'},
 {'id': 'yh.yn_wealth_floods',
  'source_id': 'bazi.source.yuanhai',
  'source_section_id': 'yuanhai.yinshou',
  'role': 'operative_candidate',
  'quote': '或若财多乘旺,必多淹留。',
  'locator': {'char_start': 12707, 'char_end': 12719},
  'operative': True,
  'routed_through_strength': True,
  'note': '财多乘旺句：「财旺」类强度判断（与既有 s057「忌财旺破印」的强度口径一致），经强度判断转手；破印效力未裁定，不可执行。正官组跳过清单第 3 段，本批补登。',
  'routed_through_other': ['财破印效力未裁定（财多乘旺是否破印、淹留程度无已裁定规则）']},
 {'id': 'yh.yn_death_luck',
  'source_id': 'bazi.source.yuanhai',
  'source_section_id': 'yuanhai.yinshou',
  'role': 'luck_observation',
  'quote': '最怕行印綬死绝之运;或运临死绝,复有物以窃之,即入黄泉,无可疑也。',
  'locator': {'char_start': 12806, 'char_end': 12839},
  'operative': False,
  'routed_through_strength': False,
  'note': '行运断语：行印綬死绝之运、复有物窃之则「即入黄泉」——死亡字样为原文断语，只登记存在、不作裁定；条件部分经长生阶段判断转手。正官组跳过清单第 4 段（与 s059 '
          '同段之后半），本批补登。',
  'routed_through_other': ['印綬死绝之运的长生阶段判断未裁定（死绝之地/之运无已裁定标尺）', '窃之之物未定（「复有物以窃之」的对象与效力未裁定）']},
 {'id': 'yh.yn_jia_seal_taboo',
  'source_id': 'bazi.source.yuanhai',
  'source_section_id': 'yuanhai.yinshou',
  'role': 'operative_candidate',
  'quote': '如甲人生亥子月中,水为印,忌火伤官,忌土破印,要行生旺之乡,怕行死绝之地;若行死绝之地,或有物以伤之,则危矣!',
  'locator': {'char_start': 12899, 'char_end': 12954},
  'operative': True,
  'routed_through_strength': False,
  'note': '甲例印綬操作句：以甲人生亥子月、水为印立例，忌火伤官、忌土破印、行生旺避死绝——三门未建层并陈，不可执行。正官组跳过清单第 5 段，本批补登。',
  'routed_through_other': ['忌火伤官经伤官伤印效力转手（未裁定）',
                           '忌土破印经财星（土）破印效力转手（未裁定）',
                           '生旺/死绝之地为长生阶段判断（未阈值化、无已裁定标尺）']},
 {'id': 'yh.yn_character_full',
  'source_id': 'bazi.source.yuanhai',
  'source_section_id': 'yuanhai.yinshou',
  'role': 'character_claim',
  'quote': '印綬之人智虑、一生少病、能饱食丰厚、享见成财禄',
  'locator': {'char_start': 12956, 'char_end': 12979},
  'operative': False,
  'routed_through_strength': None,
  'note': '印綬之人品象断语（智虑、少病、饱食丰厚、享见成财禄）：性情/境遇陈述，只登记存在、不作裁定，不构成任何健康判断口径。正官组跳过清单第 6 段前半，本批补登。'},
 {'id': 'yh.yn_more_is_taken',
  'source_id': 'bazi.source.yuanhai',
  'source_section_id': 'yuanhai.yinshou',
  'role': 'operative_candidate',
  'quote': '若两三命相併,当以印綬多者取之。',
  'locator': {'char_start': 12980, 'char_end': 12996},
  'operative': True,
  'routed_through_strength': False,
  'note': '两命相併比较句：以印綬多者取之，与 yh.yn_more_is_upper 同旨两述（为上/取之并存），逐处登记、不合并引文。正官组跳过清单第 6 段后半，本批补登。',
  'routed_through_other': ['印綬多寡的数量比较未阈值化（同 yh.yn_more_is_upper 口径）']},
 {'id': 'yh.yn_wealth_arrives_floods',
  'source_id': 'bazi.source.yuanhai',
  'source_section_id': 'yuanhai.yinshou',
  'role': 'operative_candidate',
  'quote': '最忌财来乘旺,必生淹滞。',
  'locator': {'char_start': 12998, 'char_end': 13010},
  'operative': True,
  'routed_through_strength': True,
  'note': '财来乘旺句：与 yh.yn_wealth_floods（或若财多乘旺，必多淹留）同旨两述（淹留/淹滞），逐处登记、不合并引文。正官组跳过清单第 7 段，本批补登。',
  'routed_through_other': ['财破印效力未裁定（同 yh.yn_wealth_floods 口径）']},
 {'id': 'yh.yn_month_hour_position',
  'source_id': 'bazi.source.yuanhai',
  'source_section_id': 'yuanhai.yinshou',
  'role': 'operative_candidate',
  'quote': '大凡月与时上见者为妙;而月上最为紧要。',
  'locator': {'char_start': 13033, 'char_end': 13052},
  'operative': True,
  'routed_through_strength': False,
  'note': '位置通论句：印綬以月与时上见者为妙、月上最为紧要——位置观察与评价并陈，评价部分以未裁定的印格成立为前提，不可执行。正官组跳过清单第 8 段，本批补登。',
  'routed_through_other': ['印綬为妙的评价以印格成立为前提（印格 determination 为 None）；月/时位置在场事实本身可由四柱算出，但不构成成格条件']},
 {'id': 'yh.yn_three_powers',
  'source_id': 'bazi.source.yuanhai',
  'source_section_id': 'yuanhai.yinshou',
  'role': 'fortune_claim',
  'quote': '先论月气之后有生气,必得父母之力;年下有生气,必得祖宗之力;于时上见之有生气,必得子孙之力,寿元耐久,晚景优游。',
  'locator': {'char_start': 13054, 'char_end': 13110},
  'operative': False,
  'routed_through_strength': None,
  'note': '生气三力断语（月气得父母之力、年下得祖宗之力、时上得子孙之力，寿元耐久、晚景优游）：六亲之力与寿元断语，只登记存在、不作裁定，不构成任何六亲或寿命判断口径。正官组跳过清单第 '
          '9 段，本批补登。'},
 {'id': 'yh.yn_injured_seal_outcome',
  'source_id': 'bazi.source.yuanhai',
  'source_section_id': 'yuanhai.yinshou',
  'role': 'fortune_claim',
  'quote': '若伤印,主破家离祖、出赘;又临死绝之地,若非降官失职,必夭其寿。',
  'locator': {'char_start': 13200, 'char_end': 13232},
  'operative': False,
  'routed_through_strength': False,
  'note': '伤印后果断语（破家离祖、出赘，降官失职、夭其寿）：后果吉凶/寿元断语，只登记存在、不作裁定；其前提「伤印」本身经未裁定的破印效力层。正官组跳过清单第 10 段，本批补登。',
  'routed_through_other': ['伤印是否成立经财破印效力层转手（未裁定）']},
 {'id': 'yh.yn_example_no_wealth',
  'source_id': 'bazi.source.yuanhai',
  'source_section_id': 'yuanhai.yinshou',
  'role': 'worked_example',
  'quote': '如【癸亥,癸亥,甲寅,甲子】:此日用癸为印,印却旺;缘无财星相助,发福不厚也。',
  'locator': {'char_start': 13301, 'char_end': 13340},
  'operative': False,
  'routed_through_strength': None,
  'note': '例造（癸亥/癸亥/甲寅/甲子）：用癸为印而印旺、无财星相助则发福不厚——doctrine 应用见证，非规则；不据例造反推条件。正官组跳过清单第 11 段，本批补登。'},
 {'id': 'yh.yn_example_wealth_breaks_seal',
  'source_id': 'bazi.source.yuanhai',
  'source_section_id': 'yuanhai.yinshou',
  'role': 'worked_example',
  'quote': '如【甲寅,庚午,戊戌,壬子】:此日戊用丁为印綬,有寅午戌火局为好;不合时上壬子水旺,财能冲印,所以失明。生气是丙丁火属木故也。',
  'locator': {'char_start': 13342, 'char_end': 13405},
  'operative': False,
  'routed_through_strength': None,
  'note': '例造（甲寅/庚午/戊戌/壬子）：戊用丁为印綬、壬子水旺财能冲印而失明——doctrine 应用见证，非规则；末句「生气是丙丁火属木故也」语义存疑见字形登记 '
          'yin-glyph-01。正官组跳过清单第 12 段，本批补登。',
  'glyph_refs': ['yin-glyph-01']},
 {'id': 'yh.ds_definition',
  'source_id': 'bazi.source.yuanhai',
  'source_section_id': 'yuanhai.daoshi',
  'role': 'definition',
  'quote': '夫倒食者,冲财神之谓也;一名『吞啗煞』。',
  'locator': {'char_start': 14129, 'char_end': 14149},
  'operative': False,
  'routed_through_strength': None,
  'note': '倒食定义句：倒食者，冲财神之谓，一名吞啗煞——倒食即偏印（下句以甲见壬立例，壬为甲之偏印）。「啗」异体见字形登记 '
          'yin-glyph-02。定义本身不经旺衰转手；其大忌条件另行登记。',
  'glyph_refs': ['yin-glyph-02']},
 {'id': 'yh.ds_taboo',
  'source_id': 'bazi.source.yuanhai',
  'source_section_id': 'yuanhai.daoshi',
  'role': 'operative_candidate',
  'quote': '用财神大忌见之,用食神亦忌见之。',
  'locator': {'char_start': 14149, 'char_end': 14165},
  'operative': True,
  'routed_through_strength': False,
  'note': '倒食大忌句：用财神、用食神均忌见倒食——冲财与夺食两门效力均未裁定，不可执行。',
  'routed_through_other': ['倒食冲财效力未裁定（用财神大忌见之）', '偏印夺食效力未裁定（用食神亦忌见之）']},
 {'id': 'yh.ds_mechanism',
  'source_id': 'bazi.source.yuanhai',
  'source_section_id': 'yuanhai.daoshi',
  'role': 'operative_candidate',
  'quote': '倒食者,如甲见壬之类。如甲见丙为食神,能生土财;然壬剋丙火,丙火不能生甲木之土财,所谓甲用食神,大忌见之。',
  'locator': {'char_start': 14167, 'char_end': 14220},
  'operative': True,
  'routed_through_strength': False,
  'note': '甲例机理句：甲见丙为食神能生土财，壬水剋丙则食神不能生财——夺食机理陈述，效力层未建成，不可执行。',
  'routed_through_other': ['偏印夺食效力未裁定（壬剋丙火使食神受夺）', '食神生财链效力未裁定（丙火不能生甲木之土财）']},
 {'id': 'yh.ds_fortune_thin',
  'source_id': 'bazi.source.yuanhai',
  'source_section_id': 'yuanhai.daoshi',
  'role': 'fortune_claim',
  'quote': '凡命中带此二者,主福浅寿薄。',
  'locator': {'char_start': 14222, 'char_end': 14236},
  'operative': False,
  'routed_through_strength': None,
  'note': '吉凶/寿元断语（带倒食者主福浅寿薄）：只登记存在、不作裁定，不构成任何福寿判断口径。'},
 {'id': 'yh.ds_killing_control',
  'source_id': 'bazi.source.yuanhai',
  'source_section_id': 'yuanhai.daoshi',
  'role': 'operative_candidate',
  'quote': '又见庚为七杀,得丙丁火制之,怕见水,反为祸矣!',
  'locator': {'char_start': 14238, 'char_end': 14261},
  'operative': True,
  'routed_through_strength': False,
  'note': '制杀与破制句：庚七杀得丙丁火（食神）制之，怕见水（倒食）破制反为祸——制伏与破制两门效力均未裁定，不可执行。',
  'routed_through_other': ['食神制杀效力未裁定（丙丁火制庚七杀）', '见水破制效力未裁定（水即倒食，怕见水反为祸）']},
 {'id': 'yh.ds_claims',
  'source_id': 'bazi.source.yuanhai',
  'source_section_id': 'yuanhai.daoshi',
  'role': 'fortune_claim',
  'quote': '凡命中犯此者,犹尊长之制我身,不得自由也。作事进退悔懒、有始无终、财源屡成屡败、容貌攲斜、身品矮小、胆怯心慌,凡事无成也。',
  'locator': {'char_start': 14261, 'char_end': 14322},
  'operative': False,
  'routed_through_strength': None,
  'note': '犯倒食诸断语（不得自由、作事有始无终、财源屡成屡败、容貌攲斜、身品矮小、胆怯心慌、凡事无成）：行为/容貌/性情断语，只登记存在、不作裁定，不构成任何身心或成败判断口径。「攲」异体见字形登记 '
          'yin-glyph-04。',
  'glyph_refs': ['yin-glyph-04']},
 {'id': 'yh.ds_example_1',
  'source_id': 'bazi.source.yuanhai',
  'source_section_id': 'yuanhai.daoshi',
  'role': 'worked_example',
  'quote': '如【丁未,丁未,己亥,丁卯】:此命己亥日,己临亥上,身弱于亥;加以亥卯未木局剋身,年月时透出三丁食己。幼年行南方运,赖火生土,身犹旺;纔交乙巳运,为己之七杀,引出亥卯未木局,岁运癸亥,所以死矣!此命非但倒食七杀之祸,而癸亥年与生杀坏印之说同义也。',
  'locator': {'char_start': 14324, 'char_end': 14447},
  'operative': False,
  'routed_through_strength': None,
  'note': '例造（丁未/丁未/己亥/丁卯）：身弱于亥、三丁倒食、乙巳运七杀引局、癸亥年死——doctrine 应用见证，非规则；「三丁食己」语义存疑见字形登记 '
          'yin-glyph-03，「纔」异体见 yin-glyph-05。不据例造反推条件。',
  'glyph_refs': ['yin-glyph-03', 'yin-glyph-05']},
 {'id': 'yh.ds_example_2',
  'source_id': 'bazi.source.yuanhai',
  'source_section_id': 'yuanhai.daoshi',
  'role': 'worked_example',
  'quote': '如【甲戌,丙寅,甲戌,壬申】:此命甲戌日,甲见丙食神,生于正月,甲木旺,身与食神俱旺,本是贵命;不合时上壬申,壬水伤其丙火,申金冲其寅木;又申中有庚七杀,所以利名无成。行己巳运金生之地,见庚子年;庚金为七杀,又见子水,死于非命。',
  'locator': {'char_start': 14449, 'char_end': 14563},
  'operative': False,
  'routed_through_strength': None,
  'note': '例造（甲戌/丙寅/甲戌/壬申）：身与食神俱旺本是贵命，时上壬申倒食伤丙、申冲寅、庚七杀在申，利名无成、庚子年死于非命——doctrine '
          '应用见证，非规则；不据例造反推条件。'}]

YUANHAI_YIN_CONTEXT_QUOTES = [{'id': 'yh.ctx_yn_head_para',
  'source_id': 'bazi.source.yuanhai',
  'source_section_id': 'yuanhai.yinshou',
  'role': 'gap_bearing_context',
  'quote': '所谓印?生我者,即印綬也,经曰:『有官无印,即非真官;有印无官,反成其福。』',
  'locator': {'char_start': 12515, 'char_end': 12553},
  'contains_gap_positions': [12518],
  'not_for_operative_reading': True,
  'note': '整段含缺字位点 12518（见缺字登记 yh-gap-04，正官组在册、本批按节归属在案）：含缺字的「所谓印?生我者」分句不作引文读法依据；段内经曰窗口（正官组 '
          'yh.ys_jingyue，本批引用关系在案）起于其后「即印綬也」，避开该位点。'},
 {'id': 'yh.ctx_yn_how_para',
  'source_id': 'bazi.source.yuanhai',
  'source_section_id': 'yuanhai.yinshou',
  'role': 'gap_bearing_context',
  'quote': '何以言之?大抵人生得物以相助相生相养,使我得万物之见成,岂不妙乎;故主人多智虑,兼丰厚。',
  'locator': {'char_start': 12553, 'char_end': 12597},
  'contains_gap_positions': [12557],
  'not_for_operative_reading': True,
  'note': '整段含缺字位点 12557（「何以言之?」衔接处，见缺字登记 yh-gap-05，正官组在册）：衔接分句不作读法依据；段内两处引文 '
          'yh.yn_shengwo_doctrine、yh.yn_character_zhilü 的窗口均避开该位点。'}]

YUANHAI_YIN_GAP_REGISTER = [{'id': 'yh-gap-04',
  'position': 12518,
  'char': '?',
  'source_section_id': 'yuanhai.yinshou',
  'context': '所谓印?生我者',
  'context_locator': {'char_start': 12515, 'char_end': 12522},
  'status': 'placeholder_unresolved',
  'reading': None,
  'note': '半角 ? 占位：位于「所谓印」之后、「生我者」之前，句中确有缺字形态。原文保留 ?、不猜填；本批登记的经曰窗口 yh.ys_jingyue 起于其后「即印綬也」，避开此位点。',
  'pre_existing': True,
  'registered_in': 'bazi_yuanhai_zhengguan'},
 {'id': 'yh-gap-05',
  'position': 12557,
  'char': '?',
  'source_section_id': 'yuanhai.yinshou',
  'context': '何以言之?',
  'context_locator': {'char_start': 12553, 'char_end': 12558},
  'status': 'placeholder_unresolved',
  'reading': None,
  'note': '半角 ? 占位：位于「何以言之」之后、「大抵人生得物」之前。与 yh-gap-03 同型，按缺字未决统一登记，不猜填、不据以断句。',
  'pre_existing': True,
  'registered_in': 'bazi_yuanhai_zhengguan'}]

YUANHAI_YIN_GLYPH_NOTES = [{'id': 'yin-glyph-01',
  'position': 13400,
  'char': '属',
  'source_section_id': 'yuanhai.yinshou',
  'status': 'semantic_doubt_preserved',
  'mapped_reading': None,
  'note': '例造（甲寅/庚午/戊戌/壬子）末句「生气是丙丁火属木故也」：戊以丙丁火为生气（印綬），原文作「属木」，于五行归属语义不通，疑有讹字或脱字；无见证互校，不径改、不给 '
          'mapped_reading，逐字保留并标记存疑。'},
 {'id': 'yin-glyph-02',
  'position': 14145,
  'char': '啗',
  'source_section_id': 'yuanhai.daoshi',
  'status': 'variant_form_preserved',
  'mapped_reading': None,
  'note': '「一名『吞啗煞』」之「啗」为「啖」的异体字形，快照转写原样保留；不改写、不给 mapped_reading（与正官组「茍」、财组「貲」异体保留同口径）。'},
 {'id': 'yin-glyph-03',
  'position': 14372,
  'char': '食',
  'source_section_id': 'yuanhai.daoshi',
  'status': 'semantic_doubt_preserved',
  'mapped_reading': None,
  'note': '倒食例造（丁未/丁未/己亥/丁卯）「年月时透出三丁食己」：三丁为己土之偏印即倒食，「食己」二字于此语义存疑（或为倒食于己之省语，或有讹字）；无见证互校，不径改、不给 '
          'mapped_reading，逐字保留并标记存疑。'},
 {'id': 'yin-glyph-04',
  'position': 14303,
  'char': '攲',
  'source_section_id': 'yuanhai.daoshi',
  'status': 'variant_form_preserved',
  'mapped_reading': None,
  'note': '「容貌攲斜」之「攲」为「欹」的异体字形，快照转写原样保留；不改写、不给 mapped_reading。'},
 {'id': 'yin-glyph-05',
  'position': 14391,
  'char': '纔',
  'source_section_id': 'yuanhai.daoshi',
  'status': 'variant_form_preserved',
  'mapped_reading': None,
  'note': '「纔交乙巳运」之「纔」为「才」的异体字形，快照转写原样保留；不改写、不给 mapped_reading。'}]

YUANHAI_YIN_CROSS_REFERENCES = [{'id': 'yh.yn_xref_ys_jingyue',
  'target_module': 'bazi_yuanhai_zhengguan',
  'target_quote_id': 'yh.ys_jingyue',
  'locator': {'char_start': 12523, 'char_end': 12553},
  'relation': '《论印綬》经曰官印句（有官无印即非真官、有印无官反成其福）已于正官组登记，窗口起于「即印綬也」以避开缺字位点 '
              '12518：本批整节登记只登记引用关系，不重复登记引文，其既有语义不变。'},
 {'id': 'yh.yn_xref_ys_guangui_sheng',
  'target_module': 'bazi_yuanhai_zhengguan',
  'target_quote_id': 'yh.ys_guangui_sheng',
  'locator': {'char_start': 12599, 'char_end': 12644},
  'relation': '《论印綬》官鬼能生我段已于正官组登记：官生印 doctrine 为印组本体论述，本批只登记引用关系；财组批亦曾以引用关系在案（印綬畏财一面）。'},
 {'id': 'yh.yn_xref_ys_guangui_duo_yanzhi',
  'target_module': 'bazi_yuanhai_zhengguan',
  'target_quote_id': 'yh.ys_guangui_duo_yanzhi',
  'locator': {'char_start': 12721, 'char_end': 12744},
  'relation': '《论印綬》官鬼多言之形已于正官组登记：与 s058 论形逐处并存（正官组 yh-glyph-04 已落账），本批两形分别以引用关系在案、不合并引文。'},
 {'id': 'yh.yn_xref_ys_guanyin_liangquan',
  'target_module': 'bazi_yuanhai_zhengguan',
  'target_quote_id': 'yh.ys_guanyin_liangquan',
  'locator': {'char_start': 13112, 'char_end': 13168},
  'relation': '《论印綬》官印两全段已于正官组登记：「必为贵命」为原文断语、只登记存在，本批只登记引用关系。'},
 {'id': 'yh.yn_xref_ys_yongguan_buxian',
  'target_module': 'bazi_yuanhai_zhengguan',
  'target_quote_id': 'yh.ys_yongguan_buxian',
  'locator': {'char_start': 13170, 'char_end': 13198},
  'relation': '《论印綬》用官不显段已于正官组登记：财组批亦曾以引用关系在案（岁运临财乡伤印），本批只登记引用关系。'},
 {'id': 'yh.yn_xref_ys_example_guanyin_1',
  'target_module': 'bazi_yuanhai_zhengguan',
  'target_quote_id': 'yh.ys_example_guanyin_1',
  'locator': {'char_start': 13234, 'char_end': 13299},
  'relation': '官印两全例造一（戊戌/庚申/癸酉/庚申）已于正官组登记：本批只登记引用关系，不据例造反推条件。'},
 {'id': 'yh.yn_xref_ys_example_guanyin_2',
  'target_module': 'bazi_yuanhai_zhengguan',
  'target_quote_id': 'yh.ys_example_guanyin_2',
  'locator': {'char_start': 13407, 'char_end': 13492},
  'relation': '官印两全例造二（己卯/丁卯/丙辰/壬辰，含庚申年七杀破印叙事）已于正官组登记：七杀组批亦曾以引用关系在案，本批只登记引用关系。'},
 {'id': 'yh.yn_xref_legacy_s057',
  'target_module': 'bazi_yuanhai_zhengguan',
  'target_quote_id': 'yh.legacy_s057',
  'locator': {'char_start': 12841, 'char_end': 12897},
  'relation': '既有登记 s057：印綬定义（以阳见阴、以阴见阳谓之正印；阳见阳、阴见阴谓之偏印）与「喜官星生印，忌财旺破印」观察，已编码于 bazi_pattern，其 '
              'indeterminate 口径不变；本批整节登记不改变其语义，只登记引用关系。'},
 {'id': 'yh.yn_xref_legacy_s058',
  'target_module': 'bazi_yuanhai_zhengguan',
  'target_quote_id': 'yh.legacy_s058',
  'locator': {'char_start': 13012, 'char_end': 13031},
  'relation': '既有登记 s058：官鬼多/入别格则不可专以印綬论的 indeterminate '
              '观察，口径不变；与言之形窗口（yh.ys_guangui_duo_yanzhi）逐处并存、不合并。'},
 {'id': 'yh.yn_xref_legacy_s059',
  'target_module': 'bazi_yuanhai_zhengguan',
  'target_quote_id': 'yh.legacy_s059',
  'locator': {'char_start': 12746, 'char_end': 12806},
  'relation': '既有登记 s059：月令生我五组有限列举（印綬月例），为列举而非成格条件集，语义不变；本批只登记引用关系。'}]

YUANHAI_YIN_UNREGISTERED_RELATED = [{'section_id': 'yuanhai.yinshou_shijue',
  'title': '印綬节后诗诀十六首',
  'locator': {'char_start': 13494, 'char_end': 14119},
  'reason': '《论印綬》后、《论倒食》前《诗诀》十六首（13494–14119，机上实测计数 16 '
            '首），皆印綬/生气题材（月逢印綬喜官星、印綬重重、贪财坏印、印綬死绝等），与印綬论同旨：诗诀体例与散文节不同，本批只登记散文节，诗诀未登记（与正官组、七杀组、财组同口径）。'},
 {'section_id': 'yuanhai.shishen',
  'title': '论食神',
  'locator': {'char_start': 7622, 'char_end': 7948},
  'reason': '食神本体论述节：倒食节以食神为受夺对象（壬剋丙火、丙火不能生土财），但食神节的论述主体是食神本身，属后续食伤主题范围；财组批（E0284）已列同一未登记项，本批沿用其口径，只列清单。'}]

YUANHAI_YIN_ROUTING_REVIEW = {'scope': '论印綬本批补登引文与论倒食中全部 operative=True 引文逐条（9 条）',
 'conclusion_consistent_with_readiness': '印组可操作句无一条可直接执行，全部经未建层中的至少一门转手——财破印效力门（财多乘旺必多淹留、财来乘旺必生淹滞、甲例忌土破印、倒食冲财神）：财星在场事实可算而破印/冲财效力未裁定；偏印夺食效力门（甲用食神大忌见倒食、壬剋丙火使食神不能生财）与食神生财链效力均未裁定；制杀效力门（丙丁火制庚七杀、怕见水破制反为祸）未裁定；长生阶段门（要行生旺之乡、怕行死绝之地）为阶段判断，未阈值化、无已裁定标尺；数量比较门（两三命相併以印綬多者为上/取之）为多寡计数比较，未阈值化、不作计数判定；印格成立门（月与时上见者为妙）以印格成立本身为前提而印格 '
                                         'determination 不存在。故登记后印格 determination 仍为 '
                                         'None，与正官组、七杀组、财组同口径。',
 'comparison_with_prior_groups': '与前三组对照：正官成格侧独经身旺/轻重一门；七杀组经身旺、制伏效力、合杀三门；财组转手最密（六门）；印组的特点是身旺本身罕见出场——可操作句主要经效力类诸门（破印、夺食、生财链、制杀）与长生阶段、数量比较两类未阈值判断转手，仅「财多乘旺/财来乘旺」两句沿既有 '
                                 's057「忌财旺破印」的强度口径标注为强度判断。本批逐句登记以逐句复核为准。',
 'non_operative_excluded': '定义句、性情/健康断语、六亲之力与寿元断语、行运断语、例造已分别标注 '
                           'operative=False，不计入可操作句集合；断语本身即不可执行的吉凶陈述，只登记存在、不作裁定。其中「一生少病」「寿元耐久」「必夭其寿」「福浅寿薄」「即入黄泉」等健康/寿命字样均为原文断语，本批不设、也不允许衍生任何健康或寿命判断口径字段。',
 'determination_consequence': '本批登记后印格 determination 仍为 '
                              'None：成格侧缺印格成立规则与长生阶段标尺，破格侧缺财破印、偏印夺食、食神生财链与制杀诸效力层裁定；登记只补齐成对审定的材料。《论印綬》自此整节在册（正官组 '
                              '7 窗与 s057–s059 三窗以引用关系并存、逐字与语义不变），《论倒食》偏印本体入册。'}

YUANHAI_YIN_NOTES = ['R1 登记≠可裁定：本批为纯证据登记，仓库内不存在任何印格 determination 代码路径；bazi_pattern 的 '
 'candidates、pattern_route、pattern_zaqi、pattern_determination_ren_yin 输出逐字不变。',
 'R2 缺字对账：两节范围内半角 ? 共 2 处（均在《论印綬》：12518、12557），已于正官组登记为 yh-gap-04/05；本批 YUANHAI_YIN_GAP_REGISTER 以 '
 'pre_existing 标记按节归属在案，位置、上下文、状态与正官组登记逐字一致（密封专项逐项比对），本批不新增缺字登记。全书 ? 共 36 处，正官组已登记 5 处、七杀组 2 处、财组 '
 '3 处，其余 26 处不在本批范围（印綬 2 处计入正官组 5 处之内，不重复计数）。两节范围内 PUA 私用区字符 0 处（全书 PUA 亦为 0）。',
 'R3 不重复登记：正官组在《论印綬》登记的 7 个窗口与既有 s057–s059 三窗共 10 '
 '条，只登记引用关系（YUANHAI_YIN_CROSS_REFERENCES），不复制引文、不改变其任何既有编码语义（s055 restriction、s057/s058 '
 'indeterminate 口径不变）。',
 'R4 引文窗口纪律：全部 operative 引文与 doctrine 引文的窗口均不含 ? 字符；含缺字的整段只以 context 形登记并标 '
 'not_for_operative_reading。',
 'R5 印綬补全纪律：正官组 R5 只扩与正官/官杀论述直接相关的窗口并逐段登记其余 12 段跳过理由（理由均为「非正官/官杀论述」，就正官组范围成立）；本批印组逐段复核后确认 12 '
 '段全部属印綬论述主体，整节补全，补登引文 note '
 '逐条注明其在正官组跳过清单中的序号。节首「所谓印?生我者」段与「何以言之?」段在正官组未立引文窗，本批以含缺字段登记并补登其内两句（yh.yn_shengwo_doctrine、yh.yn_character_zhilü）。',
 'R6 '
 '倒食归属：《论倒食》为偏印本体节——财组批列未登记的理由（财与食为受损对象而非论述主体）就财组范围成立；本批印组以论述主体归属为准整节登记。节内冲财、夺食、生财诸句按所在节登记，不与财组引文重复；全书无独立《论正印》《论偏印》节（机上实测「论正印」「论偏印」出现 '
 '0 次），印綬一节统论正印、偏印，s057 定义分正偏在册。',
 'R7 '
 '健康/寿命禁区（内容诚实边界）：本登记不含、也不得被用于由印格推断健康、寿命、六亲境遇的任何字段、评分或口径；节内「一生少病」「寿元耐久」「必夭其寿」「福浅寿薄」「即入黄泉」「必得父母之力」等均为原文断语与例造叙事，按 '
 'fortune_claim / character_claim / luck_observation 登记存在，公开投影与任何场景均不消费本登记作健康、寿命或六亲判断。',
 'R8 来源普查不变：渊海 Source 仍为既有 101 条之一（C 95 / D 6），本批只扩 review_scope，不新增 Source、不升证据等级；渊海全文仍 '
 'quarantine，本登记只及于所列两节范围。',
 'R9 Canonical/Phase1 注册 pending：本登记为公开仓证据登记，sealed Phase1/Phase2 正式注册未做（与既有研究级登记同口径披露），不借用 s 编号。']

YUANHAI_YIN_LIMITATIONS = ['印格成格/破格/真假/清浊/用神继续不可裁定：成格侧缺印格成立规则与长生阶段标尺，月时位置评价以印格成立为前提；破格侧经财破印、偏印夺食、食神生财链与制杀诸效力层转手而均未裁定。',
 '缺字 2 处未决（沿正官组 yh-gap-04/05 在案）：含缺字分句（所谓印?生我者、何以言之?衔接）在缺字解决前不作任何读法依据；本批未做任何底本互校以解决缺字。',
 '印綬节后诗诀十六首与《论食神》未登记（逐项理由见 '
 'YUANHAI_YIN_UNREGISTERED_RELATED）；渊海其余诸节（论伤官、伤官说、论阳刃、论日刃、论日贵、论日德、论魁罡、论金神等）仍未逐节登记。',
 '字形疑点 5 项未决（例造「属木」语义存疑、倒食例造「三丁食己」语义存疑、「啗」「攲」「纔」异体）：均逐字保留、无 '
 'mapped_reading，待见证互校另批处理；印綬节题缺《字与官鬼多言之/论两形沿正官组 yh-glyph-02/04 在案，本批不重复登记。',
 '本登记不得用于健康、寿命或六亲境遇判断：任何由印格、印星旺弱或本登记引文推断健康/寿命/六亲境遇的用法均在本登记授权范围之外。']
