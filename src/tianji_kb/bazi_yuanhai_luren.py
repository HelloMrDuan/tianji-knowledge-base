"""渊海子平禄刃组两节逐节登记（TJ-012.3 Slice D 就绪度复审排序第一前置：渊海逐节登记·第六组）。

正官组（E0236/E0237）、七杀组（E0282/E0283）、财组（E0284/E0285）、
印组（E0286/E0287）与食伤组（E0288/E0289）之后续登禄刃组：
《论阳刃》被七杀组列为未登记（阳刃专题节），本批正面处置整节
登记；《论日刃》为日刃专题节、与阳刃同法互证，一并整节登记。
禄在渊海无专节（全书节题扫描无《论禄》及任何含禄节题），只有
《论阳刃》「以禄前一位是也」的定义性出场与散见诸节两种形态，
本批以未登记清单专条登记该事实，不跨节拼凑禄格登记；与
Slice A 禄刃路线（三命卷三《论十干禄》、卷五《论阳刃》，
E0216）是不同书不同层，只在注记中登记交叉关系、不混同。

本批登记范围（机上密封快照实测，快照 SHA256 与登记 Source 一致）：
- 《论阳刃》[14796, 15439) 整节登记（643 字，全文窗；节界经
  实测订正——七杀组节题扫描所记 15176 系段内《喜忌篇》引文行，
  非节界，见 YUANHAI_LUREN_NOTES R5）；
- 《论日刃》[15752, 16116) 整节登记（364 字，全文窗）；
- 已登记涉阳刃/禄引文 8 条只登记引用关系，不重复登记。

缺字纪律：两节范围内半角 ? 占位共 1 处（《论阳刃》14875，
「何谓阳刃?」设问衔接处），本批新登记为 lr-gap-01，维持
placeholder_unresolved——原文保留 ?、不猜填；含缺字引首
不作引文读法依据，全部 operative 引文窗口避开缺字位点。
字形纪律：例造时柱 XX 占位、「兼受七杀」受字与「安得不举」
举字语义存疑，逐项落账，无见证者不给 mapped_reading。

转手复核（本批核心登记结论）：禄刃组可操作句逐条标注转手门。
全部经未建层中的至少一门转手：身旺、制刃效力、印綬链、
财星链、支关系效力、行运阶段、格局成立本身（逐日忌避细则
另有口径范围未定）。登记后阳刃格、日刃格 determination
仍为 None，禄格因无专节同为 None（详见
YUANHAI_LUREN_ROUTING_REVIEW）。

特别纪律：本登记不含任何祸福/刑伤/生死/境遇预测口径——
节内「其祸非常」「必主奇祸」「投水而死」「亦遭刑也」
「发跡疆场」等均为原文断语与例造叙事，按断语登记存在。

本模块是纯数据登记，**零 determination 代码**：不写任何阳刃格/
日刃格/禄格成格/破格判定，不改变 candidates 与既有登记语义；
登记不等于可裁定。引文全部经机上快照切片逐字复核（全文计数==1；
既有窗口以引用关系在案者以其原登记为准）。
Canonical/Phase1 注册状态 pending（与既有研究级登记同口径披露）。
"""


YUANHAI_LUREN_ID = 'bazi-yuanhai-luren-registration-v1'

YUANHAI_LUREN_TASK = 'TJ-012.3 Slice D prerequisite (yuanhai luren group registration)'

YUANHAI_SNAPSHOT = {'file': 'yuanhai_ziping.txt',
 'snapshot_path': 'data/quarantine/public_domain_snapshots/daizhigev20/yuanhai_ziping.txt',
 'sha256': 'c8f45d3228fb1958012139139a83edd019e7c2db881998d2d0bba65107417cf9',
 'bytes': 154655,
 'chars': 58905,
 'blob_sha': 'f945a48cbedf5883808a72bb6f544a4dca603cb3'}

YUANHAI_LUREN_SECTIONS = [{'section_id': 'yuanhai.yangren',
  'title': '论阳刃',
  'source_id': 'bazi.source.yuanhai',
  'locator': {'char_start': 14796, 'char_end': 15439},
  'registration_mode': 'full_section',
  'full_text': '《论 阳 刃》\n'
               ' 夫阳刃者,号天上之凶星,作人间之恶杀,以禄前一位是也;如甲禄在寅,卯为阳刃。\n'
               ' 喜偏官七杀,喜印綬;忌反吟伏吟,忌魁罡,忌三合。\n'
               ' 何谓阳刃?甲丙戊庚壬五阳有刃,乙丁己辛癸五阴无刃,故名阳刃。\n'
               ' 如命中有刃,不可便言凶,大率与七杀相似。\n'
               ' 凡有刃者,多主富贵人;却喜偏财七杀。\n'
               ' 然,『杀无刃不显,刃无杀不威!』刃杀俱全,非常人有之。大要身旺,运行身旺之乡;不要见伤官、刃旺运。\n'
               ' 若命中元有杀刃,岁运又逢之,其祸非常。\n'
               ' 若命有刃无杀,岁运逢杀旺之乡,乃转生而反成厚福;如伤官财旺,身弱杀旺,最可忌也。\n'
               ' 如【庚申,己卯,甲寅,XX】:此命甲日见卯为刃,庚为七杀。其杀本伤身,却藉卯中乙木以配合,其杀有情,则杀不能伤身;正是甲以乙妹妻庚之义。其身旺南方运,所以为贵。\n'
               ' 如【戊午,戊午,戊午,甲寅】:此命刃杀全,而又以午火为印,所以为贵。故《喜忌篇》云:『戊日午月,勿作刃看;岁时火多,却为印綬。』\n'
               ' '
               '如【辛酉,甲午,戊午,甲寅】:此命杀刃全,而有印綬。不合年干伤官透出,运行辛卯,犯伤官元有之辰;壬为财,是壬辰岁凶事投水而死。壬水剋火印,时坐甲之七杀,谓之生杀坏印。即此命见辛为伤官,运行辛卯,忌见官;午中丁火为印綬,最忌伤官与财相见,缘水生木剋身也。\n'
               ' '
               '如【癸未,乙卯,甲子,己巳】岳飞:此命卯刃癸印。不合时上己巳破印,运行辛亥,亥卯未合起阳刃;辛酉年,辛金又旺于酉,冲起卯刃二辛,则太过。金多见甲,身虽贵,亦遭刑也;然虽见辛为贵,所忌阳刃,不可一合一冲也。\n'
               ' ',
  'note': '整节登记（643 字）。本节位于快照「神煞」部分（节前为《论劫财》与「【渊海子平】神 煞」分部行）。节界订正：七杀组未登记清单曾以节题扫描记为 '
          '[14796,15176)，15176 处的《喜忌篇》实为戊午例造段内引文行（「故《喜忌篇》云」），非节界；其后辛酉、岳飞两例造续完本节，内容界实测至 '
          '15439，其后为阳刃日刃诗诀八首（未登记，见清单）。节内半角 ? 占位 1 处（14875）登记为 lr-gap-01；例造时柱 XX 占位见字形登记 '
          'lr-glyph-01；无 PUA 字符。'},
 {'section_id': 'yuanhai.riren',
  'title': '论日刃',
  'source_id': 'bazi.source.yuanhai',
  'locator': {'char_start': 15752, 'char_end': 16116},
  'registration_mode': 'full_section',
  'full_text': '《论 日 刃》\n'
               ' 日刃与阳刃同。日刃有戊午、丙午、壬子也,与阳刃同法;不喜刑冲破害,不喜会合、兼受七杀,要行官乡,便为贵命。若四柱中一来会合,必主奇祸。\n'
               ' 其人眼大鬚长、性刚果毅,无惻隐惠慈之心、有刻剥不恤之意。\n'
               ' 三刑自刑魁罡全,发跡疆场。\n'
               ' 如或无情、或财旺,则主其凶;或有救神,要先审察。如刑害俱全,类皆得地,贵不可言也!安得不举。\n'
               ' 独阳刃以时言之,四柱中不要入财乡,怕冲阳刃。\n'
               ' 且如戊日刃在午,忌行子正财运;壬刃在子,忌行午正财运;庚刃在酉,忌行卯正财运;甲日行巳午并辰戌丑未财运不妨,忌酉运;丙日刃在午,行申酉庚辛丑不妨,忌子运。\n'
               ' 大抵阳刃要身旺,喜有物以去之,经曰:『人有鬼人,物有鬼物,逢之为灾,去之为福。』\n'
               ' 如葛参政命,【壬申,壬子,戊午,乙卯】:戊日刃在午,喜得乙卯时,正官制伏去了,所以为福也。\n'
               ' \n',
  'note': '整节登记（364 字）。本节兼论日刃与阳刃（「独阳刃以时言之」「大抵阳刃要身旺」诸句在案），节前为阳刃日刃诗诀八首，节后为《论日贵》（16116 起）。节内无半角 ? '
          '占位、无 PUA 字符；字形疑点 2 项（兼受七杀受字、安得不举举字）逐处落账。'}]

YUANHAI_LUREN_QUOTES = [{'id': 'yh.yr_definition_by_lu',
  'source_id': 'bazi.source.yuanhai',
  'source_section_id': 'yuanhai.yangren',
  'role': 'definition',
  'quote': '夫阳刃者,号天上之凶星,作人间之恶杀,以禄前一位是也;如甲禄在寅,卯为阳刃。',
  'locator': {'char_start': 14805, 'char_end': 14843},
  'operative': False,
  'routed_through_strength': None,
  'note': '阳刃定义句：以禄前一位是也（如甲禄在寅、卯为阳刃）——禄在本组唯一的定义性出场；渊海无《论禄》专节（全书节题扫描 0 见，见未登记清单 '
          'yuanhai.lu_scattered），禄位事实本身属历法/禄表层（三命卷三《论十干禄》已于 Slice A '
          '登记、不同书不同层），本节不展开禄格。定义本身不经旺衰转手。'},
 {'id': 'yh.yr_preferences',
  'source_id': 'bazi.source.yuanhai',
  'source_section_id': 'yuanhai.yangren',
  'role': 'operative_candidate',
  'quote': '喜偏官七杀,喜印綬;忌反吟伏吟,忌魁罡,忌三合。',
  'locator': {'char_start': 14845, 'char_end': 14869},
  'operative': True,
  'routed_through_strength': False,
  'note': '阳刃喜忌总纲句：喜偏官七杀、喜印綬；忌反吟伏吟、忌魁罡、忌三合——三门未建层并陈，不可执行。',
  'routed_through_other': ['喜偏官七杀经制刃效力层转手（七杀制刃效力未裁定）',
                           '喜印綬经印綬化杀/生身链转手（效力未裁定）',
                           '忌反吟伏吟、忌魁罡、忌三合经支关系效力层转手（三合会局与魁罡归属未裁定）']},
 {'id': 'yh.yr_definition_five_yang',
  'source_id': 'bazi.source.yuanhai',
  'source_section_id': 'yuanhai.yangren',
  'role': 'definition',
  'quote': '甲丙戊庚壬五阳有刃,乙丁己辛癸五阴无刃,故名阳刃。',
  'locator': {'char_start': 14876, 'char_end': 14901},
  'operative': False,
  'routed_through_strength': None,
  'note': '阳刃定义句（设问答体）：甲丙戊庚壬五阳有刃、乙丁己辛癸五阴无刃，故名阳刃——定义本身不经旺衰转手；其设问引首「何谓阳刃?」含缺字位点 14875，以 context '
          '形登记（yh.ctx_yr_definition_lead），不作读法依据。'},
 {'id': 'yh.yr_not_simply_fierce',
  'source_id': 'bazi.source.yuanhai',
  'source_section_id': 'yuanhai.yangren',
  'role': 'doctrine_observation',
  'quote': '如命中有刃,不可便言凶,大率与七杀相似。',
  'locator': {'char_start': 14903, 'char_end': 14923},
  'operative': False,
  'routed_through_strength': None,
  'note': 'doctrine 陈述：命中有刃不可便言凶、大率与七杀相似——刃杀同论的类比陈述，只登记存在、不作裁定；非条件句。'},
 {'id': 'yh.yr_wealth_preference',
  'source_id': 'bazi.source.yuanhai',
  'source_section_id': 'yuanhai.yangren',
  'role': 'operative_candidate',
  'quote': '凡有刃者,多主富贵人;却喜偏财七杀。',
  'locator': {'char_start': 14925, 'char_end': 14943},
  'operative': True,
  'routed_through_strength': False,
  'note': '凡有刃者多主富贵、却喜偏财七杀：条件部分经未建层转手，不可执行；「多主富贵人」为境遇断语，只登记存在、不构成任何现实境遇判断口径。',
  'routed_through_other': ['却喜偏财七杀经财生杀/杀制刃效力链转手（效力未裁定）']},
 {'id': 'yh.yr_blade_killing_strength',
  'source_id': 'bazi.source.yuanhai',
  'source_section_id': 'yuanhai.yangren',
  'role': 'operative_candidate',
  'quote': '然,『杀无刃不显,刃无杀不威!』刃杀俱全,非常人有之。大要身旺,运行身旺之乡;不要见伤官、刃旺运。',
  'locator': {'char_start': 14945, 'char_end': 14994},
  'operative': True,
  'routed_through_strength': True,
  'note': '刃杀格言句（杀无刃不显、刃无杀不威）＋操作句：大要身旺、运行身旺之乡、不要见伤官与刃旺运——身旺明文条件，不可执行。',
  'routed_through_other': ['刃杀俱全、非常人有之的配合评价以阳刃格成立为前提（阳刃格 determination 为 None）',
                           '不要见伤官经伤官伤刃效力转手（未裁定）',
                           '刃旺运之「旺」与运行身旺之乡为行运阶段/强度判断（未裁定）']},
 {'id': 'yh.yr_luck_repeat_disaster',
  'source_id': 'bazi.source.yuanhai',
  'source_section_id': 'yuanhai.yangren',
  'role': 'luck_observation',
  'quote': '若命中元有杀刃,岁运又逢之,其祸非常。',
  'locator': {'char_start': 14996, 'char_end': 15015},
  'operative': False,
  'routed_through_strength': False,
  'note': '行运断语：命中元有杀刃、岁运又逢之则其祸非常——祸福字样为原文断语，只登记存在、不作裁定。',
  'routed_through_other': ['岁运又逢杀刃之祸经制刃效力与行运阶段判断转手（未裁定）']},
 {'id': 'yh.yr_no_killing_luck_wealth',
  'source_id': 'bazi.source.yuanhai',
  'source_section_id': 'yuanhai.yangren',
  'role': 'operative_candidate',
  'quote': '若命有刃无杀,岁运逢杀旺之乡,乃转生而反成厚福;如伤官财旺,身弱杀旺,最可忌也。',
  'locator': {'char_start': 15017, 'char_end': 15057},
  'operative': True,
  'routed_through_strength': True,
  'note': '命有刃无杀、岁运逢杀旺之乡则反成厚福；伤官财旺、身弱杀旺最可忌——身弱明文条件，不可执行。',
  'routed_through_other': ['岁运逢杀旺之乡的杀旺为七杀强度判断（未裁定）',
                           '「转生而反成厚福」以阳刃格成立为前提（determination 为 None）；厚福为境遇断语只登记存在']},
 {'id': 'yh.yr_example_jia',
  'source_id': 'bazi.source.yuanhai',
  'source_section_id': 'yuanhai.yangren',
  'role': 'worked_example',
  'quote': '如【庚申,己卯,甲寅,XX】:此命甲日见卯为刃,庚为七杀。其杀本伤身,却藉卯中乙木以配合,其杀有情,则杀不能伤身;正是甲以乙妹妻庚之义。其身旺南方运,所以为贵。',
  'locator': {'char_start': 15059, 'char_end': 15139},
  'operative': False,
  'routed_through_strength': None,
  'note': '例造（庚申/己卯/甲寅/XX）：甲日见卯为刃、庚为七杀，藉卯中乙木配合、杀有情则不伤身，身旺南方运所以为贵——doctrine 应用见证，非规则；时柱于快照中以 XX '
          '占位、四柱不全（见字形登记 lr-glyph-01），不据例造反推条件。',
  'glyph_refs': ['lr-glyph-01']},
 {'id': 'yh.yr_example_wu',
  'source_id': 'bazi.source.yuanhai',
  'source_section_id': 'yuanhai.yangren',
  'role': 'worked_example',
  'quote': '如【戊午,戊午,戊午,甲寅】:此命刃杀全,而又以午火为印,所以为贵。故《喜忌篇》云:『戊日午月,勿作刃看;岁时火多,却为印綬。』',
  'locator': {'char_start': 15141, 'char_end': 15205},
  'operative': False,
  'routed_through_strength': None,
  'note': '例造（戊午/戊午/戊午/甲寅）：刃杀全、又以午火为印，所以为贵——段末「故《喜忌篇》云：『戊日午月，勿作刃看；岁时火多，却为印綬。』」为段内引文行，15176 不是节界（见 '
          'YUANHAI_LUREN_NOTES R5）；所引戊日午月不作刃看为刃/印归属判断，其裁定层不存在，只登记存在；doctrine 应用见证，非规则。'},
 {'id': 'yh.yr_example_xin',
  'source_id': 'bazi.source.yuanhai',
  'source_section_id': 'yuanhai.yangren',
  'role': 'worked_example',
  'quote': '如【辛酉,甲午,戊午,甲寅】:此命杀刃全,而有印綬。不合年干伤官透出,运行辛卯,犯伤官元有之辰;壬为财,是壬辰岁凶事投水而死。壬水剋火印,时坐甲之七杀,谓之生杀坏印。即此命见辛为伤官,运行辛卯,忌见官;午中丁火为印綬,最忌伤官与财相见,缘水生木剋身也。',
  'locator': {'char_start': 15207, 'char_end': 15333},
  'operative': False,
  'routed_through_strength': None,
  'note': '例造（辛酉/甲午/戊午/甲寅）：杀刃全而有印綬，不合年干伤官透出、运行辛卯犯伤官，壬辰岁凶事投水而死，生杀坏印——例内生死断语只登记存在；doctrine '
          '应用见证，非规则，不据例造反推条件。'},
 {'id': 'yh.yr_example_yuefei',
  'source_id': 'bazi.source.yuanhai',
  'source_section_id': 'yuanhai.yangren',
  'role': 'worked_example',
  'quote': '如【癸未,乙卯,甲子,己巳】岳飞:此命卯刃癸印。不合时上己巳破印,运行辛亥,亥卯未合起阳刃;辛酉年,辛金又旺于酉,冲起卯刃二辛,则太过。金多见甲,身虽贵,亦遭刑也;然虽见辛为贵,所忌阳刃,不可一合一冲也。',
  'locator': {'char_start': 15335, 'char_end': 15437},
  'operative': False,
  'routed_through_strength': None,
  'note': '例造（癸未/乙卯/甲子/己巳，岳飞）：卯刃癸印，时上己巳破印、运行辛亥合起阳刃、辛酉年冲起卯刃则太过，身虽贵亦遭刑——例内刑伤断语只登记存在；doctrine '
          '应用见证，非规则，不据例造反推条件。'},
 {'id': 'yh.rr_same_method',
  'source_id': 'bazi.source.yuanhai',
  'source_section_id': 'yuanhai.riren',
  'role': 'operative_candidate',
  'quote': '日刃与阳刃同。日刃有戊午、丙午、壬子也,与阳刃同法;不喜刑冲破害,不喜会合、兼受七杀,要行官乡,便为贵命。若四柱中一来会合,必主奇祸。',
  'locator': {'char_start': 15761, 'char_end': 15828},
  'operative': True,
  'routed_through_strength': False,
  'note': '日刃总纲句：日刃与阳刃同法（戊午、丙午、壬子），不喜刑冲破害与会合、兼受七杀、要行官乡——四门并陈，不可执行；四柱一来会合必主奇祸为祸福断语，只登记存在。',
  'routed_through_other': ['不喜刑冲破害、不喜会合经支关系效力层转手（三合会局与合化未裁定；三刑事实层已建但本句为成格评价而非事实陈述）',
                           '兼受七杀经制刃效力层转手（未裁定；「受」字存疑见 lr-glyph-02）',
                           '要行官乡、便为贵命以日刃格成立为前提（日刃格 determination 为 None）'],
  'glyph_refs': ['lr-glyph-02']},
 {'id': 'yh.rr_character',
  'source_id': 'bazi.source.yuanhai',
  'source_section_id': 'yuanhai.riren',
  'role': 'character_claim',
  'quote': '其人眼大鬚长、性刚果毅,无惻隐惠慈之心、有刻剥不恤之意。',
  'locator': {'char_start': 15830, 'char_end': 15858},
  'operative': False,
  'routed_through_strength': None,
  'note': '性情/形貌断语（眼大鬚长、性刚果毅，无惻隐惠慈之心、有刻剥不恤之意）：只登记存在、不作裁定，不构成任何性情判断口径。'},
 {'id': 'yh.rr_punishment_military',
  'source_id': 'bazi.source.yuanhai',
  'source_section_id': 'yuanhai.riren',
  'role': 'fortune_claim',
  'quote': '三刑自刑魁罡全,发跡疆场。',
  'locator': {'char_start': 15860, 'char_end': 15873},
  'operative': False,
  'routed_through_strength': None,
  'note': '境遇断语（三刑自刑魁罡全、发跡疆场）：三刑/自刑在场事实已由三刑事实层（sanxing-branch-fact-v1）建成，但本句为境遇断语，只登记存在、不作裁定，不构成任何境遇判断口径。'},
 {'id': 'yh.rr_wealth_fierce_rescue',
  'source_id': 'bazi.source.yuanhai',
  'source_section_id': 'yuanhai.riren',
  'role': 'operative_candidate',
  'quote': '如或无情、或财旺,则主其凶;或有救神,要先审察。如刑害俱全,类皆得地,贵不可言也!安得不举。',
  'locator': {'char_start': 15875, 'char_end': 15921},
  'operative': True,
  'routed_through_strength': False,
  'note': '日刃救应句：无情或财旺则主凶、有救神要先审察，刑害俱全得地则贵不可言——不可执行；「安得不举」语义存疑见 lr-glyph-03。',
  'routed_through_other': ['或财旺则主其凶经财生杀/财旺坏刃链转手（未裁定）',
                           '「或有救神」之救神未定（何神为救、救应效力均未裁定）',
                           '刑害俱全、类皆得地为得时得地判断（未阈值化，沿财组得时得地门口径）'],
  'glyph_refs': ['lr-glyph-03']},
 {'id': 'yh.rr_hour_wealth_taboo',
  'source_id': 'bazi.source.yuanhai',
  'source_section_id': 'yuanhai.riren',
  'role': 'operative_candidate',
  'quote': '独阳刃以时言之,四柱中不要入财乡,怕冲阳刃。',
  'locator': {'char_start': 15923, 'char_end': 15945},
  'operative': True,
  'routed_through_strength': False,
  'note': '时上阳刃操作句：四柱中不要入财乡、怕冲阳刃——不可执行。本节兼论日刃与阳刃，本句为阳刃口径（以时言之），逐字保留。',
  'routed_through_other': ['四柱不要入财乡经财星链转手（未裁定）', '怕冲阳刃经冲刃效力转手（未裁定）']},
 {'id': 'yh.rr_avoidance_rules',
  'source_id': 'bazi.source.yuanhai',
  'source_section_id': 'yuanhai.riren',
  'role': 'operative_candidate',
  'quote': '且如戊日刃在午,忌行子正财运;壬刃在子,忌行午正财运;庚刃在酉,忌行卯正财运;甲日行巳午并辰戌丑未财运不妨,忌酉运;丙日刃在午,行申酉庚辛丑不妨,忌子运。',
  'locator': {'char_start': 15947, 'char_end': 16024},
  'operative': True,
  'routed_through_strength': False,
  'note': '逐日行运忌避细则（戊忌子运、壬忌午运、庚忌卯运、甲忌酉运、丙忌子运）：全节最具体的操作句，仍经口径范围与格局成立两门转手，不可执行；甲、丙两条兼记不妨之运，逐字保留。',
  'routed_through_other': ['各日忌行正财运/忌运的支位以阳刃位定义为前提，而本节定义仅列戊午、丙午、壬子三日刃，本段却并陈庚刃在酉、甲忌酉运等五阳阳刃口径，两口径适用范围未定',
                           '「正财运」的财星身份需以日干十神事实逐盘推定，忌避结论以刃格成立为前提（determination 为 None）']},
 {'id': 'yh.rr_body_strong_remove',
  'source_id': 'bazi.source.yuanhai',
  'source_section_id': 'yuanhai.riren',
  'role': 'operative_candidate',
  'quote': '大抵阳刃要身旺,喜有物以去之,经曰:『人有鬼人,物有鬼物,逢之为灾,去之为福。』',
  'locator': {'char_start': 16026, 'char_end': 16066},
  'operative': True,
  'routed_through_strength': True,
  'note': '大抵阳刃要身旺、喜有物以去之：身旺明文条件，不可执行；经曰『人有鬼人，物有鬼物，逢之为灾，去之为福』为引文断语，只登记存在。',
  'routed_through_other': ['喜有物以去之的「去之」为制化效力（何物去刃、去之程度均未裁定）']},
 {'id': 'yh.rr_example_ge',
  'source_id': 'bazi.source.yuanhai',
  'source_section_id': 'yuanhai.riren',
  'role': 'worked_example',
  'quote': '如葛参政命,【壬申,壬子,戊午,乙卯】:戊日刃在午,喜得乙卯时,正官制伏去了,所以为福也。',
  'locator': {'char_start': 16068, 'char_end': 16113},
  'operative': False,
  'routed_through_strength': None,
  'note': '例造（壬申/壬子/戊午/乙卯，葛参政）：戊日刃在午，喜乙卯时正官制伏去了，所以为福——制伏效力应用见证，非规则；不据例造反推条件。'}]

YUANHAI_LUREN_CONTEXT_QUOTES = [{'id': 'yh.ctx_yr_definition_lead',
  'source_id': 'bazi.source.yuanhai',
  'source_section_id': 'yuanhai.yangren',
  'role': 'gap_bearing_context',
  'quote': '何谓阳刃?',
  'locator': {'char_start': 14871, 'char_end': 14876},
  'contains_gap_positions': [14875],
  'not_for_operative_reading': True,
  'note': '整段含缺字位点 14875（「何谓阳刃?」设问衔接处，见缺字登记 '
          'lr-gap-01）：只作定位登记、不作读法依据；其后定义正文（甲丙戊庚壬五阳有刃……故名阳刃）不含缺字，已分立登记为 '
          'yh.yr_definition_five_yang（与食伤组食神定义段分立登记同型）。'}]

YUANHAI_LUREN_GAP_REGISTER = [{'id': 'lr-gap-01',
  'position': 14875,
  'char': '?',
  'source_section_id': 'yuanhai.yangren',
  'context': '何谓阳刃?',
  'context_locator': {'char_start': 14871, 'char_end': 14876},
  'status': 'placeholder_unresolved',
  'reading': None,
  'note': '半角 ? '
          '占位：位于「何谓阳刃」之后、「甲丙戊庚壬」之前（阳刃定义段的设问衔接处）。字面位置可读作问号标点，但本批按缺字未决统一登记（性质未决、两读并存），不猜填、不据以断句；含缺字引首只以 '
          'context 形登记（yh.ctx_yr_definition_lead），登记引文窗口全部避开此位点（与正官组、财组、食伤组同型）。'}]

YUANHAI_LUREN_GLYPH_NOTES = [{'id': 'lr-glyph-01',
  'position': 15070,
  'char': 'X',
  'source_section_id': 'yuanhai.yangren',
  'status': 'example_placeholder_preserved',
  'mapped_reading': None,
  'note': '例造【庚申,己卯,甲寅,XX】时柱于快照中以 XX 占位：原书此处或缺时柱、或转录佚失，无见证可补；逐字保留 XX、不猜填任何干支，例造按四柱不全登记（见 '
          'yh.yr_example_jia），不据以反推条件。'},
 {'id': 'lr-glyph-02',
  'position': 15800,
  'char': '受',
  'source_section_id': 'yuanhai.riren',
  'status': 'semantic_doubt_preserved',
  'mapped_reading': None,
  'note': '《论日刃》「不喜会合、兼受七杀」之「受」字语义存疑：与上下文喜忌文例不侔（或疑为喜/制之讹、或别有读法），无见证互校，不径改、不给 '
          'mapped_reading，逐字保留并标记存疑（见 yh.rr_same_method）。'},
 {'id': 'lr-glyph-03',
  'position': 15919,
  'char': '举',
  'source_section_id': 'yuanhai.riren',
  'status': 'semantic_doubt_preserved',
  'mapped_reading': None,
  'note': '《论日刃》「贵不可言也!安得不举」之「举」字语义存疑：下文无对举文句承接，疑有讹字或脱文；无见证互校，不径改、不给 mapped_reading，逐字保留并标记存疑（见 '
          'yh.rr_wealth_fierce_rescue）。'}]

YUANHAI_LUREN_CROSS_REFERENCES = [{'id': 'yh.yr_xref_qs_definition',
  'target_module': 'bazi_yuanhai_qisha',
  'target_quote_id': 'yh.qs_definition',
  'locator': {'char_start': 11636, 'char_end': 11673},
  'relation': '《论七杀》总纲句「喜阳刃」已于七杀组登记：七杀喜阳刃为刃杀同论的七杀侧陈述，本批只登记引用关系，不重复登记引文。'},
 {'id': 'yh.yr_xref_qs_blade_and_wealth',
  'target_module': 'bazi_yuanhai_qisha',
  'target_quote_id': 'yh.qs_blade_and_wealth',
  'locator': {'char_start': 11844, 'char_end': 11888},
  'relation': '《论七杀》「如行身旺乡，更有阳刃，贵不可言」已于七杀组登记：身旺＋阳刃的配合评价散见七杀节，与本节 yh.yr_blade_killing_strength '
              '对读在案，本批只登记引用关系。'},
 {'id': 'yh.yr_xref_qs_day_killing',
  'target_module': 'bazi_yuanhai_qisha',
  'target_quote_id': 'yh.qs_day_killing',
  'locator': {'char_start': 11956, 'char_end': 12003},
  'relation': '《论七杀》日七杀句「最怕冲与阳刃大凶」已于七杀组登记：时位差异下对阳刃的相反评价（日杀怕刃、时杀不怕刃）并列在案、不合并读法，本批只登记引用关系。'},
 {'id': 'yh.yr_xref_qs_hour_no_fear',
  'target_module': 'bazi_yuanhai_qisha',
  'target_quote_id': 'yh.qs_hour_no_fear',
  'locator': {'char_start': 12073, 'char_end': 12090},
  'relation': '《论七杀》「时上七杀，却不怕阳刃，而亦不畏冲」已于七杀组登记：与日七杀怕阳刃句（yh.qs_day_killing）为同节内的时位对读，本批只登记引用关系。'},
 {'id': 'yh.yr_xref_zg_jia_mixed',
  'target_module': 'bazi_yuanhai_zhengguan',
  'target_quote_id': 'yh.zg_jia_mixed',
  'locator': {'char_start': 10042, 'char_end': 10097},
  'relation': '《正官论》甲例「最怕刑冲破害、阳刃七杀」已于正官组登记：阳刃为正官忌见因素之一面散见正官节，本批只登记引用关系。'},
 {'id': 'yh.lr_xref_jc_reverse_blade',
  'target_module': 'bazi_yuanhai_cai',
  'target_quote_id': 'yh.jc_definition',
  'locator': {'char_start': 14575, 'char_end': 14590},
  'relation': '《论劫财》定义句「亦名『逆刃』」已于财组登记：逆刃是劫财的别名，与阳刃/日刃为名称交叉、所指不同，本批只登记引用关系以明区分，不混同两刃。'},
 {'id': 'yh.lr_xref_zc_example_lu',
  'target_module': 'bazi_yuanhai_cai',
  'target_quote_id': 'yh.zc_example_4',
  'locator': {'char_start': 9058, 'char_end': 9291},
  'relation': '《论正财》例造「时又归禄于寅，故财旺矣」已于财组登记：归禄为禄在已登记引文中的散见出场（例造叙事），是渊海无《论禄》专节、禄论述散见形态之一证，本批只登记引用关系。'},
 {'id': 'yh.lr_xref_pc_classic_lu',
  'target_module': 'bazi_yuanhai_cai',
  'target_quote_id': 'yh.pc_classic_quote',
  'locator': {'char_start': 9439, 'char_end': 9457},
  'relation': '偏财分题经曰『背禄逐马，守穷途而悽惶也』已于财组登记：禄马为禄在已登记引文中的散见出场（经引断语），本批只登记引用关系；断语只登记存在、不作裁定。'}]

YUANHAI_LUREN_UNREGISTERED_RELATED = [{'section_id': 'yuanhai.yangren_rijue_shijue',
  'title': '阳刃日刃诗诀八首',
  'locator': {'char_start': 15439, 'char_end': 15752},
  'reason': '《论阳刃》后、《论日刃》前《诗诀》八首（15439–15752，机上实测计数 8 '
            '首），皆阳刃/日刃题材（阳刃存时、壬子休来、日刃还如、阳刃嫌冲、时逢阳刃、阳刃重逢、阳刃之辰、马逢丙戊），与两节论同旨：诗诀体例与散文节不同，本批只登记散文节，诗诀未登记（与前五批同口径）。'},
 {'section_id': 'yuanhai.shensha_four',
  'title': '神煞四节（论日贵/论日德/论魁罡/论金神）',
  'locator': {'char_start': 16116, 'char_end': 17642},
  'reason': '《论日刃》后神煞诸节：《论日贵》[16116,16453)、《论日德》[16453,16883)、《论魁罡》[16883,17225)、《论金神》[17225,17642)（其间杂诗诀诸首，17642 '
            '起为《六亲总篇》），四节各为独立神煞专题、非禄刃本体专论；阳刃节内「忌魁罡」与魁罡节的材料关系俟神煞专题批按节处置，本批只列清单。'},
 {'section_id': 'yuanhai.lu_scattered',
  'title': '禄散见诸节（无《论禄》专节）',
  'locator': {'char_start': 34965, 'char_end': 34980},
  'reason': '全书节题扫描无《论禄》节、亦无任何含「禄」节题：禄在渊海无专节，只有三种出场形态——(1) 定义性出场：《论阳刃》「以禄前一位是也」（本批已登记 '
            'yh.yr_definition_by_lu）；(2) 已登记引文散见：财组例造「时又归禄于寅」、偏财分题经曰「背禄逐马」（本批引用关系在案）；(3) '
            '未登记诸节散见：建禄 5 见（《喜忌篇》二见 24336、《杂论口诀》27329、《妖祥》34751、《五言独步》54423、《珞琭子消息赋》56703）、归禄 20 '
            '见、月劫 1 见（《四言独步》53373）等，散见于赋论、口诀与格局诸节（均未逐节登记）；本项 locator '
            '为其中最具禄格专指性的《妖祥》「日时归禄，官逢有祸。(归禄格)」一句 [34965,34980) '
            '以作代表，禄格论述俟各节登记批按节处置，本批不跨节摘录、不据散见拼凑禄格登记。'}]

YUANHAI_LUREN_ROUTING_REVIEW = {'scope': '论阳刃与论日刃中全部 operative=True 引文逐条（9 条：阳刃 4、日刃 5）',
 'conclusion_consistent_with_readiness': '禄刃组可操作句无一条可直接执行，全部经未建层中的至少一门转手——身旺门（大要身旺、运行身旺之乡、身弱杀旺最可忌、大抵阳刃要身旺：身旺/身弱为明文条件而一般旺衰不存在）；制刃效力门（喜偏官七杀、兼受七杀、喜有物以去之：七杀制刃与『去之』的效力与程度均未裁定）；印綬链门（喜印綬：印綬化杀/生身效力未裁定）；财星链门（却喜偏财、财旺则主其凶、不要入财乡、忌行正财运：财生杀与财旺坏刃的效力未裁定）；支关系效力门（忌反吟伏吟/三合、不喜刑冲破害/会合、怕冲阳刃：三合会局与合化未裁定，刑冲破害事实在场可算但其对刃的效力评价不存在）；行运阶段门（运行身旺之乡、要行官乡、刃旺运：行运阶段/强度判断未裁定）；格局成立门（刃杀俱全、便为贵命、逐日忌避细则，以阳刃格/日刃格成立本身为前提，而两格 '
                                         'determination '
                                         '均不存在；逐日忌避细则另有日刃三日与五阳阳刃两口径适用范围未定）。故登记后阳刃格、日刃格 '
                                         'determination 仍为 '
                                         'None，与前五组同口径。禄在本组只有定义性出场（禄前一位），渊海无禄格专节可登记（见未登记清单 '
                                         'yuanhai.lu_scattered），禄格 determination 更无从谈起。',
 'comparison_with_prior_groups': '与前五组对照：正官成格侧独经身旺/轻重一门；七杀组经身旺、制伏效力、合杀三门；财组转手最密（六门）；印组以效力类诸门为主；食伤组身旺明文频繁且卡在程度词。禄刃组与七杀组最接近——刃杀同论、互为条件（七杀喜阳刃、阳刃喜七杀，两节登记互证在案），同经身旺与制伏效力两大门；其特殊处在于刃的定义锚点（禄前一位、五阳有刃）本身是可由历法事实核定的在场定义，但一切成格/祸福评价仍全部经未建层转手，定义可算不等于格局可裁。本批逐句登记以逐句复核为准。',
 'non_operative_excluded': '定义句、doctrine 陈述、性情断语、行运断语、例造已分别标注 '
                           'operative=False，不计入可操作句集合；断语本身即不可执行的吉凶陈述，只登记存在、不作裁定。其中「其祸非常」「必主奇祸」「投水而死」「亦遭刑也」「发跡疆场」「多主富贵人」等祸福、刑伤、生死与境遇字样均为原文断语与例造叙事，本批不设、也不允许衍生任何祸福、刑伤、生死或境遇判断口径字段。',
 'determination_consequence': '本批登记后阳刃格、日刃格 determination 仍为 '
                              'None：成格侧缺两格成立规则，破格/忌避侧缺制刃、财星链、支关系诸效力层裁定；禄格因渊海无专节、无从登记成立规则，determination '
                              '同为 None。登记只补齐成对审定材料：《论阳刃》《论日刃》自此整节在册（阳刃节界经实测订正为内容界 '
                              '[14796,15439)），阳刃日刃诗诀八首、神煞四节与禄散见诸节未登记在案。'}

YUANHAI_LUREN_NOTES = ['R1 登记≠可裁定：本批为纯证据登记，仓库内不存在任何阳刃格/日刃格/禄格 determination 代码路径；bazi_pattern 的 '
 'candidates、pattern_route、pattern_zaqi、pattern_determination_ren_yin 输出逐字不变。Slice A '
 '禄刃路线（pattern_route，E0216）消费的是三命禄表/刃表，与本批渊海两节登记是不同书不同层，本批不改动其任何语义。',
 'R2 缺字对账：两节范围内半角 ? 共 1 处（在《论阳刃》：14875），本批新登记为 lr-gap-01，维持 placeholder_unresolved。全书 ? 共 36 '
 '处，正官组已登记 5 处、七杀组 2 处、财组 3 处、食伤组 1 处，本批 1 处，累计登记 12 处，其余 24 处不在本批范围。两节范围内 PUA 私用区字符 0 处（全书 PUA 亦为 '
 '0）。',
 'R3 不重复登记：已登记节中涉阳刃/禄引文 8 条（七杀组 4 条、正官组 1 条、财组 3 '
 '条），只登记引用关系（YUANHAI_LUREN_CROSS_REFERENCES），不复制引文、不改变其任何既有编码语义；其中财组《论劫财》「亦名逆刃」为名称交叉、所指为劫财，与阳刃/日刃严格区分。',
 'R4 引文窗口纪律：全部 operative 引文与 doctrine 引文的窗口均不含 ? 字符；含缺字的设问引首只以 context 形登记并标 '
 'not_for_operative_reading，定义正文分立登记。',
 'R5 节界订正纪律：七杀组批（E0282）未登记清单以节题扫描记《论阳刃》为 [14796,15176)——15176 '
 '处的《喜忌篇》系《论阳刃》戊午例造段内引文行（段文「故《喜忌篇》云：『戊日午月，勿作刃看……』」），不是独立节、更非节界；其后辛酉、岳飞两例造续完本节，15439 '
 '起为诗诀。本批以机上实测内容界 [14796,15439) 整节登记并在此明示订正口径；七杀组登记模块本身逐字不变（append-only），其未登记条目的历史记述以本批订正为准。',
 'R6 禄无专节纪律：全书节题扫描无《论禄》及任何含禄节题，禄在渊海只有定义性出场与散见两种形态（见未登记清单 '
 'yuanhai.lu_scattered）；本批不跨节摘录散见句拼凑禄格登记，不据三命卷三《论十干禄》（Slice A '
 '已登记、不同书）回填渊海禄论。建禄格/归禄格等格局论述俟其所在诸节（妖祥、五言独步、珞琭子消息赋等）登记批按节处置。',
 'R7 '
 '祸福/刑伤/生死禁区（内容诚实边界）：本登记不含、也不得被用于由阳刃格、日刃格推断祸福、刑伤、生死或现实境遇的任何字段、评分或口径；节内「其祸非常」「必主奇祸」「投水而死」「亦遭刑也」「发跡疆场」「多主富贵人」「贵不可言」等均为原文断语与例造叙事，按 '
 'fortune_claim / luck_observation / worked_example 登记存在，公开投影与任何场景均不消费本登记作祸福、刑伤、生死或境遇判断。',
 'R8 来源普查不变：渊海 Source 仍为既有 101 条之一（C 95 / D 6），本批只扩 review_scope，不新增 Source、不升证据等级；渊海全文仍 '
 'quarantine，本登记只及于所列两节范围。',
 'R9 Canonical/Phase1 注册 pending：本登记为公开仓证据登记，sealed Phase1/Phase2 正式注册未做（与既有研究级登记同口径披露），不借用 s 编号。']

YUANHAI_LUREN_LIMITATIONS = ['阳刃格/日刃格成格/破格/真假/清浊/用神继续不可裁定：成格侧缺两格成立规则，忌避/破格侧经制刃、财星链、支关系诸效力层转手而均未裁定；禄格因渊海无专节，成立规则无从登记、同样不可裁定。',
 '缺字 1 处未决（lr-gap-01，14875）：含缺字设问引首在缺字解决前不作任何读法依据（以 context 形登记）；本批未做任何底本互校以解决缺字。',
 '阳刃日刃诗诀八首与神煞四节（论日贵/论日德/论魁罡/论金神）未登记（逐项理由见 YUANHAI_LUREN_UNREGISTERED_RELATED）；禄散见于赋论、口诀、格局诸未登记节（建禄 '
 '5 见、归禄 20 见、月劫 1 见等），俟各节登记批按节处置；渊海其余诸节仍未逐节登记。',
 '字形疑点 3 项未决（例造时柱 XX 占位、「兼受七杀」受字语义存疑、「安得不举」举字语义存疑）：均逐字保留、无 mapped_reading，待见证互校另批处理；XX '
 '例造四柱不全，不据以反推任何条件。',
 '本登记不得用于祸福、刑伤、生死或现实境遇判断：任何由阳刃格、日刃格、禄格或本登记引文推断祸福/刑伤/生死/境遇的用法均在本登记授权范围之外。']
