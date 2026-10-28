"""大运线七项优先校勘清单收尾注册表（TJ-017.1 七项清单收尾批，审源编号 018-B）。

清单出处：tj0171-evidence-scout §6.3 七项表，经 tj018-collation-scout
§4 逐项复核。本批对象是 TJ-017.1 已登记引用面内的 7 个校勘点位：
三命卷二《论大运》U+ED92 ×3（#1）、同节存疑 2 处（#2 越三嵗九月、
#3 实歴过六十三日）、三命卷十一《珞琭子消息赋》注异文 1 处
（#4 折除三岁为年）、同卷赋文 U+EA20 ×2（#5）、神峰《起大运法》
例 2 日数与月柱字（#6）、同节例 3 字序（#7 五三十五）。

形制沿 018-A 首建的逐条校勘记注册表（bazi_sanming_juan2_collation）：
{ id, section_id, char_offset, context_short, snapshot_glyph,
snapshot_codepoint（PUA 条目）, reading, reading_status
（confirmed | contextual | suspected | unresolved）, disposition
（corrected | genuine | unresolved）, basis: [ { kind（witness |
sealed_asset | same_section_corroboration | context）, witness,
locator, quote_short } ], usable_grade（Q1 | Q2 | Q3 | None）, note }。
引文永远逐字保留快照原字（含 PUA 与讹字原字），校定只进校勘记与
登记的 mapped_reading 标注，不回写快照、不静默替换。等级口径与
018-A 一致：confirmed 须 ≥2 个独立见证或同节互证；suspected 只
登记读法提案、不作校定（沿 018-B 三刑「做曰无恩」先例，disposition
记 corrected 而 note 明示提案性质与引用限制）。

本批互校结论（全部机上实测 + 见证原文直核，详见 ITEM_DISPOSITIONS）：
- #1：密封映射 mappings[28] 的两个见证锚点经抽验属实——
  kanripo/KR3g0041（《星学大成》四库 WYG 谱系，commit 6626e6d7）
  与 lhw828/GuWen（同书，commit fcab4e24）三处语境均作「算」，
  kanripo/KR3g0042（《三命通会》四库 WYG 谱系）同段亦作「算」。
  正式流程复核完成，销项。
- #2/#3/#4：审源「疑似转写讹/单点讹字」的定性经互校**不成立**——
  四库谱系（KR3g0042）与 NiuTrans 谱系两家独立见证与快照逐字
  同读（三 / 六十三日 / 三岁），三处均为**传本本文**，非
  daizhige 转写讹。本批以 disposition=genuine 落账：转写讹定性
  撤销；#2 的语义疑点（与例算一嵗竒九月的关系未解）与 #4 的
  异文张力（三日为年 doctrine 另有三处明文）作为注记保留，
  不径改、不得据各句另立读法。此结论是对 TJ-017.1 登记注记的
  追加订正，经本注册表与两 Source 的 review_scope 追加段落
  落账，TJ-017.1 既有登记文本逐字不动。
- #5：映射 mappings[0] confirmed=玄；KR3g0042 对应两处作历史
  字形「𤣥」、NiuTrans 作「玄」，点位流程登记完成，销项。
- #6：见证可得性核查结论——kanripo 无《神峰通考》条目（org
  内代码检索 0 命中）；youngzs/xuanxue、lhw828/GuWen、
  F25731/yin-yang 三家网络转录与快照**逐字同读**（含
  「四三十二日」与「正月起戊庚」两处讹文），属同一数字谱系，
  按 TJ-018.2 独立性口径不构成独立刊本见证。校定提案
  （三四十二日 / 戊寅）只有算式与同节互证依据，登记为提案，
  **未采纳**：日数与月柱字面禁用维持（沿 TJ-017.1 登记），
  换算 Golden 不收例 2 日数。本项终局 = 维持限制。
- #7：「五三十五」字序读法形式化登记为「三五十五」（同例明文
  「后十五日生男」与「五岁运」结果为据），与 TJ-017.1 换算
  Golden 例 3 以 15 日计的既有消费一致；引文逐字保留原序。

本模块是纯数据登记，**零计算逻辑**：不含任何函数，不据此修改
TJ-017.1 三个 Variant 的任何行为、输出或限制。
"""

COLLATION_REGISTER_ID = 'dayun-collation-register-v1'

COLLATION_TASK = 'TJ-017.1 七项优先校勘清单收尾（审源编号 018-B）'

COLLATION_SNAPSHOTS = {
 'sanming_tonghui.txt': {
  'snapshot_path': 'data/quarantine/public_domain_snapshots/daizhigev20/sanming_tonghui.txt',
  'sha256': '00e2a7db8bb59b259b99938033bb1bb77947e04a15dafc111e62b59378010c86',
  'bytes': 1342659,
  'chars': 461157},
 'shenfeng_tongkao.txt': {
  'snapshot_path': 'data/quarantine/public_domain_snapshots/daizhigev20/shenfeng_tongkao.txt',
  'sha256': '121a571b7fa63e073f067d5532a42e2feb7d4d5fdd7874de2ca48036a615e200',
  'bytes': 422432,
  'chars': 154642}}

COLLATION_SECTIONS = [
 {'section_id': 'sanming.juan2.lun_dayun',
  'source_id': 'bazi.source.sanmingtonghui',
  'title_snapshot': '论大运',
  'title_normalized': '论大运',
  'volume': '卷二',
  'locator': {'char_start': 58457, 'char_end': 59198},
  'registered_by': 'TJ-017.1',
  'status': 'registered_evidence',
  'note': '节界与登记均沿 TJ-017.1，本批不扩登记；只对节内 5 个点位'
          '（U+ED92 ×3、存疑 2 处）立校勘记。'},
 {'section_id': 'sanming.juan11.luoluozi_fu',
  'source_id': 'bazi.source.sanmingtonghui',
  'title_snapshot': '珞琭子消息赋',
  'title_normalized': '珞琭子消息赋',
  'volume': '卷十一',
  'locator': {'char_start': 396898, 'char_end': 408795},
  'registered_by': 'TJ-017.1（赋注三见证窗口）',
  'status': 'registered_evidence_windows',
  'parts': [
   {'part_id': 'fu_wen_pua_points',
    'label': '赋文 U+EA20 点位 397081、397192（不在 TJ-017.1 登记窗口内，本批只作点位流程登记）',
    'locator': {'char_start': 397081, 'char_end': 397193},
    'status': 'point_registration_only'},
   {'part_id': 'vol11_direction_witness2',
    'label': '赋注第三见证窗口（TJ-017.1 已登记引文）',
    'locator': {'char_start': 408771, 'char_end': 408795},
    'status': 'registered_evidence'}],
  'note': 'locator 为本批点位所在赋/注文本的并集跨度，不表示整段已'
          '登记；TJ-017.1 的三个见证窗口（396898–396928、397112–'
          '397158、408771–408795）之外不扩登记。'},
 {'section_id': 'shenfeng.qi_dayun_fa',
  'source_id': 'bazi.source.shenfeng',
  'title_snapshot': '起大运法',
  'title_normalized': '起大运法',
  'volume': '卷次未核（沿 TJ-017.1 登记，只按字符位置引用）',
  'locator': {'char_start': 85001, 'char_end': 85246},
  'registered_by': 'TJ-017.1',
  'status': 'registered_evidence',
  'note': '本批只对例 2、例 3 的 5 个点位立校勘记，不扩登记。'}]

COLLATION_QUOTES = [
 {'id': 'dy.worked_example',
  'source_id': 'bazi.source.sanmingtonghui',
  'source_section_id': 'sanming.juan2.lun_dayun',
  'role': 'golden_basis（TJ-017.1 已登记）',
  'quote': '假如甲子阳男十二月二十四日巳时生是月也二十九日申时立春阳男数以未来之日自二十四日巳时至二十五日巳时方是一日之实数至二十九申时正得五日三时之节气实歴过六十三日折除过六十三时折除计六百三十日乃一嵗竒九月之大运起于丁丑',
  'locator': {'char_start': 58757, 'char_end': 58863},
  'note_refs': ['dy-genuine-58834'],
  'note': '句中「六十三日」之日经互校为传本本文（dy-genuine-58834），'
          '例算计数以时为据（63 时→630 日），不依赖该字读法。'},
 {'id': 'dy.worked_example_check',
  'source_id': 'bazi.source.sanmingtonghui',
  'source_section_id': 'sanming.juan2.lun_dayun',
  'role': 'registered_not_encoded（TJ-017.1 已登记）',
  'quote': '必自十二月生日后实经厯过二十有一之日月运方移宫是越三嵗九月之内方是甲子十二月生行一嵗竒九月之大运也',
  'locator': {'char_start': 58863, 'char_end': 58912},
  'note_refs': ['dy-genuine-58888'],
  'note': '「越三嵗九月」之三经互校为传本本文（dy-genuine-58888）；'
          '本句不编码，其语义疑点见校勘记注记。'},
 {'id': 'dy.handover_example',
  'source_id': 'bazi.source.sanmingtonghui',
  'source_section_id': 'sanming.juan2.lun_dayun',
  'role': 'registered_not_encoded（TJ-017.1 已登记）',
  'quote': '假如甲子年正月初一子时正一刻生行运至乙丑年正月初一日子时正一刻乃作一嵗',
  'locator': {'char_start': 59063, 'char_end': 59099},
  'mapped_reading': '假如甲子年正月初一子时正一刻生行运算至乙丑年正月初一日子时正一刻乃作一嵗',
  'collation_refs': ['dy-pua-59080']},
 {'id': 'dy.leap_clause_excluded_span',
  'source_id': 'bazi.source.sanmingtonghui',
  'source_section_id': 'sanming.juan2.lun_dayun',
  'role': 'excluded_span（TJ-017.1 已登记排除段）',
  'quote': '内小六个月即进六日在初七日子时正一刻方作一嵗只要足十二个月却为本年有闰四月乃多一月矣',
  'locator': {'char_start': 59099, 'char_end': 59142},
  'mapped_reading': '内小六个月即进六日在初七日子时正一刻方作一嵗只要算足十二个月却为本年有闰四月乃多一月矣',
  'collation_refs': ['dy-pua-59123'],
  'note': '映射在本批正式应用不解除本段排除：「内小六个月即进六日」'
          '语义未明、闰月交运子规则仍整段排除，沿 TJ-017.1 登记。'},
 {'id': 'dy.handover_decade',
  'source_id': 'bazi.source.sanmingtonghui',
  'source_section_id': 'sanming.juan2.lun_dayun',
  'role': 'encoded_basis（TJ-017.1 已登记）',
  'quote': '从此后十周年方换一运',
  'locator': {'char_start': 59160, 'char_end': 59171},
  'mapped_reading': '从此算后十周年方换一运',
  'collation_refs': ['dy-pua-59162']},
 {'id': 'dy.vol11_witness2',
  'source_id': 'bazi.source.sanmingtonghui',
  'source_section_id': 'sanming.juan11.luoluozi_fu',
  'role': 'registered_not_encoded（TJ-017.1 已登记）',
  'quote': '阴男阳女阳男阴女依逆顺行运折除即前折除三岁为年也',
  'locator': {'char_start': 408771, 'char_end': 408795},
  'note_refs': ['dy-genuine-408791'],
  'note': '「三岁」之岁经互校为传本异文（dy-genuine-408791），与'
          '「三日为年」明文并列登记，不径改、不据以立读法。'},
 {'id': 'sf.ex2',
  'source_id': 'bazi.source.shenfeng',
  'source_section_id': 'shenfeng.qi_dayun_fa',
  'role': 'corroboration_direction_only（TJ-017.1 已登记）',
  'quote': '如乙丑年,乙庚之岁戊为头,正月起戊庚,初一立春,十八日生女,顺数至二月惊蛰,四三十二日,四岁运,己卯顺行是也',
  'locator': {'char_start': 85069, 'char_end': 85123},
  'note_refs': ['sf-prop-85086', 'sf-prop-85107', 'sf-prop-85108'],
  'note': '例 2 只用方向与「四岁运」结果陈述；日数与月柱字面禁用'
          '维持，校定提案未采纳（见 sf-prop 三条）。'},
 {'id': 'sf.ex3',
  'source_id': 'bazi.source.shenfeng',
  'source_section_id': 'shenfeng.qi_dayun_fa',
  'role': 'corroboration_and_golden_basis（TJ-017.1 已登记）',
  'quote': '如乙丑年,乙庚之岁戊为头,正月起戊寅,初二立春,后十五日生男,逆数至初一日立春,五三十五,五岁运逆行',
  'locator': {'char_start': 85138, 'char_end': 85188},
  'mapped_reading': '如乙丑年,乙庚之岁戊为头,正月起戊寅,初二立春,后十五日生男,逆数至初一日立春,三五十五,五岁运逆行',
  'collation_refs': ['sf-var-85178', 'sf-var-85179'],
  'note': '「五三十五」以字序互换读法登记为「三五十五」；引文逐字'
          '保留快照原序。'}]

COLLATION_NOTES = [
 # ---- #1 三命卷二《论大运》U+ED92 ×3（正式流程复核） ----
 {'id': 'dy-pua-59080',
  'section_id': 'sanming.juan2.lun_dayun',
  'char_offset': 59080,
  'context_short': '子年正月初一子时正一刻生行运至乙丑年正月初一日子时正一刻',
  'snapshot_glyph': '',
  'snapshot_codepoint': 'U+ED92',
  'reading': '算',
  'reading_status': 'confirmed',
  'disposition': 'corrected',
  'basis': [
   {'kind': 'sealed_asset', 'witness': 'sanming_pua_collation.json mappings[28]',
    'locator': 'codepoint U+ED92', 'quote_short': 'replacement 算，status confirmed，confidence high，count 3'},
   {'kind': 'witness', 'witness': 'kanripo/KR3g0041（《星学大成》四库 WYG 谱系）',
    'locator': 'KR3g0041_003.txt @6626e6d7', 'quote_short': '行運算至乙丑年'},
   {'kind': 'witness', 'witness': 'lhw828/GuWen（《星学大成》）',
    'locator': '易藏/术数/星学大成_page7.html @fcab4e24', 'quote_short': '行运算至乙丑年'},
   {'kind': 'witness', 'witness': 'kanripo/KR3g0042（《三命通会》四库 WYG 谱系）',
    'locator': 'KR3g0042_002.txt @efe780a4', 'quote_short': '行運算至乙丑年'}],
  'usable_grade': 'Q1',
  'note': 'TJ-018.2 正式流程复核：密封映射自述的两个见证锚点（GuWen '
          '「行运算至乙丑年」、KR3g0041「只要算足十二月」）经本批直核'
          '原文属实，且四库三命谱系同段同读「算」。TJ-017.1 登记时已'
          '以 mapped_reading 消费，本批完成流程销项。'},
 {'id': 'dy-pua-59123',
  'section_id': 'sanming.juan2.lun_dayun',
  'char_offset': 59123,
  'context_short': '初七日子时正一刻方作一嵗只要足十二个月却为本年有闰四月乃',
  'snapshot_glyph': '',
  'snapshot_codepoint': 'U+ED92',
  'reading': '算',
  'reading_status': 'confirmed',
  'disposition': 'corrected',
  'basis': [
   {'kind': 'sealed_asset', 'witness': 'sanming_pua_collation.json mappings[28]',
    'locator': 'codepoint U+ED92', 'quote_short': 'replacement 算，status confirmed，confidence high，count 3'},
   {'kind': 'witness', 'witness': 'kanripo/KR3g0041（《星学大成》四库 WYG 谱系）',
    'locator': 'KR3g0041_003.txt @6626e6d7', 'quote_short': '只要算足十二月'},
   {'kind': 'witness', 'witness': 'lhw828/GuWen（《星学大成》）',
    'locator': '易藏/术数/星学大成_page7.html @fcab4e24', 'quote_short': '只要算足十二月却为本年'},
   {'kind': 'witness', 'witness': 'kanripo/KR3g0042（《三命通会》四库 WYG 谱系）',
    'locator': 'KR3g0042_002.txt @efe780a4', 'quote_short': '只要算足十二個月'}],
  'usable_grade': 'Q1',
  'note': '本点位落在 TJ-017.1 排除段（闰月交运子句）内：映射正式'
          '应用只解决字形，不解除该段的语义排除，沿 TJ-017.1 登记。'},
 {'id': 'dy-pua-59162',
  'section_id': 'sanming.juan2.lun_dayun',
  'char_offset': 59162,
  'context_short': '二月初七日子时正一刻交运从此后十周年方换一运若学者不知其',
  'snapshot_glyph': '',
  'snapshot_codepoint': 'U+ED92',
  'reading': '算',
  'reading_status': 'confirmed',
  'disposition': 'corrected',
  'basis': [
   {'kind': 'sealed_asset', 'witness': 'sanming_pua_collation.json mappings[28]',
    'locator': 'codepoint U+ED92', 'quote_short': 'replacement 算，status confirmed，confidence high，count 3'},
   {'kind': 'witness', 'witness': 'kanripo/KR3g0041（《星学大成》四库 WYG 谱系）',
    'locator': 'KR3g0041_003.txt @6626e6d7', 'quote_short': '從此算後十週年方換一運'},
   {'kind': 'witness', 'witness': 'lhw828/GuWen（《星学大成》）',
    'locator': '易藏/术数/星学大成_page7.html @fcab4e24', 'quote_short': '从此算后十周年方换一运'},
   {'kind': 'witness', 'witness': 'kanripo/KR3g0042（《三命通会》四库 WYG 谱系）',
    'locator': 'KR3g0042_002.txt @efe780a4', 'quote_short': '從此算後十週年方換一運'}],
  'usable_grade': 'Q1',
  'note': '交运十年递换句的唯一 PUA 点位；TJ-017.1 encoded_basis '
          '引文的 mapped_reading 经本批复核成立。'},
 # ---- #2/#3 三命卷二存疑 2 处（互校结论：传本同文） ----
 {'id': 'dy-genuine-58888',
  'section_id': 'sanming.juan2.lun_dayun',
  'char_offset': 58888,
  'context_short': '过二十有一之日月运方移宫是越三嵗九月之内方是甲子十二月生行',
  'snapshot_glyph': '三',
  'reading': '三',
  'reading_status': 'confirmed',
  'disposition': 'genuine',
  'basis': [
   {'kind': 'witness', 'witness': 'kanripo/KR3g0042（《三命通会》四库 WYG 谱系）',
    'locator': 'KR3g0042_002.txt @efe780a4', 'quote_short': '是越三嵗九月之内'},
   {'kind': 'witness', 'witness': 'NiuTrans/Classical-Modern',
    'locator': '古文原文/三命通会/卷二/论大运/text.txt @4e746ea9', 'quote_short': '是越三岁九月之内'}],
  'usable_grade': 'Q1',
  'note': '清单 #2。「越三嵗九月」整语在字符 58887，疑字「三」在 '
          '58888。两家独立见证与快照同读「三」：传本本文成立，审源'
          '「疑似字形讹（转写）」的定性撤销。但「三」与同例算式'
          '（一嵗竒九月、实经二十有一之月）的语义关系仍未解——可能'
          '为传本旧讹或别有所指，本批不裁定、不径改；本句 '
          'registered_not_encoded 维持，引用逐字保留，不得据此句'
          '另立任何算式。'},
 {'id': 'dy-genuine-58834',
  'section_id': 'sanming.juan2.lun_dayun',
  'char_offset': 58834,
  'context_short': '得五日三时之节气实歴过六十三日折除过六十三时折除计六百三十',
  'snapshot_glyph': '日',
  'reading': '日',
  'reading_status': 'confirmed',
  'disposition': 'genuine',
  'basis': [
   {'kind': 'witness', 'witness': 'kanripo/KR3g0042（《三命通会》四库 WYG 谱系）',
    'locator': 'KR3g0042_002.txt @efe780a4', 'quote_short': '實歴過六十三日折除過六十三時'},
   {'kind': 'witness', 'witness': 'NiuTrans/Classical-Modern',
    'locator': '古文原文/三命通会/卷二/论大运/text.txt @4e746ea9', 'quote_short': '实历过六十三日折除，过六十三时'}],
  'usable_grade': 'Q1',
  'note': '清单 #3。「实歴过六十三日」整语在字符 58828，疑字「日」'
          '在 58834（下句作「六十三时」，审源以衔接生硬存疑）。两家'
          '独立见证同读「六十三日」：传本本文成立，转写讹衍定性'
          '撤销。例算的可执行读法以时为据（63 时→630 日），不依赖'
          '此字；不作校改。'},
 # ---- #5 三命卷十一赋文 U+EA20 ×2（点位流程登记） ----
 {'id': 'dy-pua-397081',
  'section_id': 'sanming.juan11.luoluozi_fu',
  'char_offset': 397081,
  'context_short': '日为年精休旺以为妙穷通变以为\n 【先言干支则八字定矣行运',
  'snapshot_glyph': '',
  'snapshot_codepoint': 'U+EA20',
  'reading': '玄',
  'reading_status': 'confirmed',
  'disposition': 'corrected',
  'basis': [
   {'kind': 'sealed_asset', 'witness': 'sanming_pua_collation.json mappings[0]',
    'locator': 'codepoint U+EA20', 'quote_short': 'replacement 玄，status confirmed，confidence high，count 79'},
   {'kind': 'witness', 'witness': 'kanripo/KR3g0042（《三命通会》四库 WYG 谱系）',
    'locator': 'KR3g0042_011.txt @efe780a4', 'quote_short': '窮通變以為𤣥（𤣥为玄之历史字形）'},
   {'kind': 'witness', 'witness': 'NiuTrans/Classical-Modern',
    'locator': '古文原文/三命通会/卷十一/消息赋一/text.txt @4e746ea9', 'quote_short': '穷通变以为玄'}],
  'usable_grade': 'Q1',
  'note': '清单 #5 之一。赋文韵脚位（「穷通变以为玄」句末），非规则'
          '文本；本点位不在 TJ-017.1 登记窗口内，本批只完成点位'
          '流程登记，不新增引文消费。'},
 {'id': 'dy-pua-397192',
  'section_id': 'sanming.juan11.luoluozi_fu',
  'char_offset': 397192,
  'context_short': '有宜休败而嫌生旺千变万化非达通幽消息以尽造化之妙其孰能与',
  'snapshot_glyph': '',
  'snapshot_codepoint': 'U+EA20',
  'reading': '玄',
  'reading_status': 'confirmed',
  'disposition': 'corrected',
  'basis': [
   {'kind': 'sealed_asset', 'witness': 'sanming_pua_collation.json mappings[0]',
    'locator': 'codepoint U+EA20', 'quote_short': 'replacement 玄，status confirmed，confidence high，count 79'},
   {'kind': 'witness', 'witness': 'kanripo/KR3g0042（《三命通会》四库 WYG 谱系）',
    'locator': 'KR3g0042_011.txt @efe780a4', 'quote_short': '非達𤣥通幽消息（𤣥为玄之历史字形）'},
   {'kind': 'witness', 'witness': 'NiuTrans/Classical-Modern',
    'locator': '古文原文/三命通会/卷十一/消息赋一/text.txt @4e746ea9', 'quote_short': '非达玄通幽消息'}],
  'usable_grade': 'Q1',
  'note': '清单 #5 之二。「达玄通幽」为成词，语境与两见证合。同 '
          'dy-pua-397081 口径：点位流程登记，不新增引文消费。'},
 # ---- #4 三命卷十一赋注异文（传本同文） ----
 {'id': 'dy-genuine-408791',
  'section_id': 'sanming.juan11.luoluozi_fu',
  'char_offset': 408791,
  'context_short': '阴女依逆顺行运折除即前折除三岁为年也看新旧运上有何吉凶以运',
  'snapshot_glyph': '岁',
  'reading': '岁',
  'reading_status': 'confirmed',
  'disposition': 'genuine',
  'basis': [
   {'kind': 'witness', 'witness': 'kanripo/KR3g0042（《三命通会》四库 WYG 谱系）',
    'locator': 'KR3g0042_011.txt @efe780a4', 'quote_short': '折除三歲為年'},
   {'kind': 'witness', 'witness': 'NiuTrans/Classical-Modern',
    'locator': '古文原文/三命通会/卷十一/消息赋五/text.txt @4e746ea9', 'quote_short': '折除三岁为年'}],
  'usable_grade': 'Q1',
  'note': '清单 #4。「折除三岁为年」整语在字符 408788，疑字「岁」'
          '在 408791。两家独立见证同读「岁」：非快照转写单点讹，'
          '属传本异文——与「三日为年」明文（卷二比率推导与例算、'
          '同卷赋注 397112 句、渊海 §188、神峰「折除三日」）并列'
          '登记、不裁定、不径改；不得据本句立「三岁为年」读法。'
          '本句在 TJ-017.1 为赋注第三见证（方向），其见证用途只及'
          '方向分组，不及比率字面，沿既有登记。'},
 # ---- #6 神峰例 2（提案登记，限制维持） ----
 {'id': 'sf-prop-85107',
  'section_id': 'shenfeng.qi_dayun_fa',
  'char_offset': 85107,
  'context_short': '十八日生女,顺数至二月惊蛰,四三十二日,四岁运,己卯顺行是',
  'snapshot_glyph': '四',
  'reading': '三',
  'reading_status': 'suspected',
  'disposition': 'corrected',
  'basis': [
   {'kind': 'context', 'witness': '本例算式',
    'locator': '字符 85069–85123', 'quote_short': '四岁运——按三日为一岁，计数当为 12 日'},
   {'kind': 'same_section_corroboration', 'witness': '同节例 4 乘法句式',
    'locator': '字符 85189–85241', 'quote_short': '三三得九（乘数小者居前）'},
   {'kind': 'same_section_corroboration', 'witness': '同节例 3 读法',
    'locator': '字符 85138–85188', 'quote_short': '三五十五（sf-var-85178/85179 字序读法登记）'}],
  'usable_grade': None,
  'note': '清单 #6 主项，与 sf-prop-85108 为「四三十二日」字序互换'
          '提案（读「三四十二日」= 12 日）的两半。见证可得性核查：'
          'kanripo 无《神峰通考》条目；三家网络转录与快照逐字同读'
          '讹文（见 WITNESS_AVAILABILITY_SHENFENG），属同一数字'
          '谱系，不构成独立见证。故只有算式与同节句式依据，只登记'
          '提案 suspected、不作校定、日数字面禁用维持，换算 '
          'Golden 不收例 2 日数（沿 TJ-017.1 登记）。'},
 {'id': 'sf-prop-85108',
  'section_id': 'shenfeng.qi_dayun_fa',
  'char_offset': 85108,
  'context_short': '八日生女,顺数至二月惊蛰,四三十二日,四岁运,己卯顺行是也',
  'snapshot_glyph': '三',
  'reading': '四',
  'reading_status': 'suspected',
  'disposition': 'corrected',
  'basis': [
   {'kind': 'context', 'witness': '本例算式',
    'locator': '字符 85069–85123', 'quote_short': '四岁运——按三日为一岁，计数当为 12 日'},
   {'kind': 'same_section_corroboration', 'witness': '同节例 4 乘法句式',
    'locator': '字符 85189–85241', 'quote_short': '三三得九（乘数小者居前）'}],
  'usable_grade': None,
  'note': '与 sf-prop-85107 成对，互换提案的另一半；口径同该条：'
          '提案未采纳，日数字面禁用维持。'},
 {'id': 'sf-prop-85086',
  'section_id': 'shenfeng.qi_dayun_fa',
  'char_offset': 85086,
  'context_short': '年,乙庚之岁戊为头,正月起戊庚,初一立春,十八日生女,顺数',
  'snapshot_glyph': '庚',
  'reading': '寅',
  'reading_status': 'contextual',
  'disposition': 'corrected',
  'basis': [
   {'kind': 'same_section_corroboration', 'witness': '同节例 3 同位句',
    'locator': '字符 85138–85188', 'quote_short': '如乙丑年,乙庚之岁戊为头,正月起戊寅'},
   {'kind': 'context', 'witness': '五虎遁定例',
    'locator': '字符 85069–85123', 'quote_short': '乙庚之年正月起戊寅为定例；本例题干自述「乙庚之岁戊为头」'}],
  'usable_grade': None,
  'note': '清单 #6 附带疑点（TJ-017.1 登记注记已点名）：例 2 月柱句'
          '「正月起戊庚」之庚。同节例 3 同位作「戊寅」，且五虎遁'
          '定例唯一，读法提案为寅；但外部见证同 #6 主项不可得'
          '（三家转录同读「戊庚」），只登记提案、月柱字面禁用'
          '维持（沿 TJ-017.1 登记）。'},
 # ---- #7 神峰例 3 字序读法登记 ----
 {'id': 'sf-var-85178',
  'section_id': 'shenfeng.qi_dayun_fa',
  'char_offset': 85178,
  'context_short': '五日生男,逆数至初一日立春,五三十五,五岁运逆行。如甲子年',
  'snapshot_glyph': '五',
  'reading': '三',
  'reading_status': 'contextual',
  'disposition': 'corrected',
  'basis': [
   {'kind': 'context', 'witness': '同例明文',
    'locator': '字符 85138–85188', 'quote_short': '后十五日生男……五岁运——计数当为 15 日'},
   {'kind': 'same_section_corroboration', 'witness': '同节例 4 乘法句式',
    'locator': '字符 85189–85241', 'quote_short': '三三得九（乘数小者居前）'}],
  'usable_grade': 'Q2',
  'note': '清单 #7，与 sf-var-85179 为「五三十五」字序互换读法'
          '（读「三五十五」= 15 日）的两半。同例自述「后十五日」'
          '与「五岁运」结果，计数唯一自洽；读法登记与 TJ-017.1 '
          '换算 Golden 例 3 以 15 日计的既有消费一致。引文逐字'
          '保留快照原序，读法只进校勘记与 mapped_reading。'},
 {'id': 'sf-var-85179',
  'section_id': 'shenfeng.qi_dayun_fa',
  'char_offset': 85179,
  'context_short': '日生男,逆数至初一日立春,五三十五,五岁运逆行。如甲子年,',
  'snapshot_glyph': '三',
  'reading': '五',
  'reading_status': 'contextual',
  'disposition': 'corrected',
  'basis': [
   {'kind': 'context', 'witness': '同例明文',
    'locator': '字符 85138–85188', 'quote_short': '后十五日生男……五岁运——计数当为 15 日'}],
  'usable_grade': 'Q2',
  'note': '与 sf-var-85178 成对，互换读法的另一半；口径同该条。'}]

# 逐项销项表（清单 7 项的终局状态）
ITEM_DISPOSITIONS = [
 {'item': 1,
  'location': '三命卷二《论大运》U+ED92 ×3（字符 59080、59123、59162）',
  'issue': 'PUA 字形：密封映射 [28] 已 confirmed=算，TJ-017.1 登记已以 mapped_reading 消费，剩余 TJ-018.2 正式流程复核与销项',
  'final_status': 'closed',
  'final_status_label': '已闭环',
  'evidence': '映射两锚点直核属实（KR3g0041《星学大成》卷三 @6626e6d7、GuWen 同书 page7 @fcab4e24，三处语境均作「算」），四库三命谱系 KR3g0042_002 同段同读；三条校勘记 dy-pua-59080/59123/59162 落账，mapped_reading 变换机检通过',
  'restriction_after': '无新增限制；59123 所在闰月交运段的语义排除维持（与字形无关）'},
 {'item': 2,
  'location': '三命卷二《论大运》「越三嵗九月」（整语 58887，疑字「三」58888）',
  'issue': '「三」与上下文算式矛盾，疑字形讹；TJ-017.1 已存疑挂账，不在 603 条订正内',
  'final_status': 'closed',
  'final_status_label': '已闭环（互校定性：传本同文）',
  'evidence': 'KR3g0042_002 与 NiuTrans《论大运》两家独立见证与快照逐字同读「三」；密封 603 订正与 993 候选均无此条（字符串核对 0 命中）；校勘记 dy-genuine-58888 落账（genuine）',
  'restriction_after': '转写讹定性撤销；语义疑点保留注记——本句不编码、不得据「三」另立算式，引用逐字保留'},
 {'item': 3,
  'location': '三命卷二《论大运》「实歴过六十三日」（整语 58828，疑字「日」58834）',
  'issue': '「六十三日」与下文 63 时→630 日算式衔接生硬，疑转写讹衍；TJ-017.1 已存疑挂账',
  'final_status': 'closed',
  'final_status_label': '已闭环（互校定性：传本同文）',
  'evidence': 'KR3g0042_002 与 NiuTrans《论大运》两家独立见证同读「六十三日」；校勘记 dy-genuine-58834 落账（genuine）',
  'restriction_after': '不作校改；例算计数以时为据的既有读法不变'},
 {'item': 4,
  'location': '三命卷十一赋注「折除三岁为年」（整语 408788，疑字「岁」408791）',
  'issue': '「三岁」与全书三处「三日为年」及渊海、神峰矛盾，审源作单点讹字，须互校确认后登记异文、不得径改',
  'final_status': 'formalized',
  'final_status_label': '形式化登记完成（传本异文并列）',
  'evidence': 'KR3g0042_011（作三歲）与 NiuTrans 消息赋五（作三岁）两家独立见证同读「岁」；校勘记 dy-genuine-408791 落账（genuine），与「三日为年」明文并列',
  'restriction_after': '不得径改、不得据本句立「三岁为年」读法；本句见证用途只及方向分组，沿 TJ-017.1 登记'},
 {'item': 5,
  'location': '三命卷十一赋文 U+EA20 ×2（字符 397081、397192）',
  'issue': 'PUA 字形：映射 confirmed=玄，韵脚/虚字位、非规则文本，清单作「随 #1 同批流程应用」',
  'final_status': 'closed',
  'final_status_label': '已闭环',
  'evidence': '密封映射 mappings[0]；KR3g0042_011 两处作历史字形「𤣥」、NiuTrans 消息赋一两处作「玄」；校勘记 dy-pua-397081/397192 落账',
  'restriction_after': '两点位不在 TJ-017.1 登记窗口内，只作点位登记、不新增引文消费；不阻塞任何引用'},
 {'item': 6,
  'location': '神峰《起大运法》例 2「四三十二日」（85107–85111，字位 85107/85108）及月柱句「正月起戊庚」（整语 85082，疑字「庚」85086）',
  'issue': '日数与「四岁运」不合（须 12 日），数字转写讹乱；须神峰第二见证互校，见证可得性此前未核实',
  'final_status': 'restriction_maintained',
  'final_status_label': '维持限制',
  'evidence': '见证可得性核查完成：kanripo 无《神峰通考》条目；youngzs/GuWen/F25731 三家网络转录与快照逐字同读（含两处讹文），属同一数字谱系、不构成独立见证（见 WITNESS_AVAILABILITY_SHENFENG）；校定提案三条 sf-prop-85107/85108/85086 落账（suspected/contextual，未采纳）',
  'restriction_after': '日数与月柱字面禁用维持：例 2 只用方向与「四岁运」结果陈述，换算 Golden 不收其日数（沿 TJ-017.1 登记）；待有独立刊本见证时再议'},
 {'item': 7,
  'location': '神峰《起大运法》例 3「五三十五」（85178–85181，字位 85178/85179）',
  'issue': '字序讹（三五十五）；审源作「算式自明，异文登记即可」',
  'final_status': 'formalized',
  'final_status_label': '形式化登记完成（字序读法登记）',
  'evidence': '同例明文「后十五日生男」与「五岁运」结果唯一自洽；校勘记 sf-var-85178/85179 落账（字序互换读法），sf.ex3 的 mapped_reading 变换机检通过',
  'restriction_after': '引文逐字保留快照原序；读法与 TJ-017.1 换算 Golden 例 3（15 日→五岁）的既有消费一致，无新增限制'}]

# 神峰第二见证可得性核查（清单 #6 前置项，本批实测）
WITNESS_AVAILABILITY_SHENFENG = {
 'question': '《神峰通考》是否存在可作独立互校的第二见证（供例 2 日数互校）',
 'kanripo': {'available': False,
             'check': 'GitHub 代码检索 org:kanripo「神峯通考」「起大運法」均 0 命中；kanripo 有《三命通会》（KR3g0042）与《星学大成》（KR3g0041），无神峰通考条目'},
 'web_transcriptions': [
  {'witness': 'youngzs/xuanxue', 'locator': 'docs/神锋通考/006卷04.md @aa7bc942',
   'reading_at_ex2': '四三十二日 / 正月起戊庚（与快照逐字同）'},
  {'witness': 'lhw828/GuWen', 'locator': '易藏/术数/神峰通考_page14.html @fcab4e24',
   'reading_at_ex2': '四三十二日 / 正月起戊庚（与快照逐字同）'},
  {'witness': 'F25731/yin-yang', 'locator': 'corpus/04-阴阳术数/02-八字四柱/神峰通考/chapters/0007.md @a87ef55b',
   'reading_at_ex2': '四三十二日 / 正月起戊庚（与快照逐字同）'}],
 'lineage_assessment': '三家转录在例 2 全句上逐字一致且同含两处讹文，'
                       '与快照（daizhigev20 谱系）同源特征明显：现行可及的'
                       '电子文本实为同一数字谱系的多个镜像。按 TJ-018.2 '
                       '独立性口径（同一电子文本镜像不是两份独立刊本），'
                       '不构成独立第二见证。',
 'conclusion': '独立刊本见证当前不可得；#6 维持限制，校定提案只登记'
               '不采纳。日后若取得四库/明刊影印或异谱系转录，再行互校。'}

# 密封校勘资产对账（本批实测）
SEALED_ASSET_RECONCILIATION = {
 'pua_collation': 'mappings 共 85 条统一映射 + 语境映射；本批相关 2 条：'
                  '[28] U+ED92=算（#1）、[0] U+EA20=玄（#5），均 '
                  'confirmed/high，本批逐条复核见证锚点后采信',
 'text_collation_603': '以字符串核对：越三 / 六十三 / 三岁为年 / 三嵗九月 '
                       '四词在 603 条订正中 0 命中——#2/#3/#4 均不在订正集内'
                       '（与审源结论一致），本批互校不依赖订正集',
 'ocr_candidates_993': '越三 / 六十三日 / 三岁为年在 993 条候选中 0 命中，'
                       '三项均无候选条目',
 'note': '本批定字/定性全部落到见证原文（kanripo 两谱系、NiuTrans、'
         'GuWen），密封资产只作线索与映射依据，不作单独证据。'}

COLLATION_ADJUDICATION_NOTES = [
 'R1 销项口径：七项终局只许三态——已闭环 / 形式化登记完成 / 维持限制，'
 '逐项见 ITEM_DISPOSITIONS。本批结果：闭环 4 项（#1/#2/#3/#5）、形式化'
 '登记 2 项（#4/#7）、维持限制 1 项（#6）。',
 'R2 #2/#3/#4 定性订正（追加订正，不改旧登记）：审源与 TJ-017.1 注记作'
 '「疑似转写讹/单点讹字」，本批两家独立见证互校证明三处均为传本本文，'
 '转写讹定性撤销；语义层面的疑点（#2 与算式的关系、#4 与 doctrine 的'
 '张力）以注记形式保留，不因定性订正而消失，也不得反向用作校改依据。',
 'R3 #1 流程定位：59080/59162 两处 TJ-017.1 已消费，本批是 TJ-018.2 '
 '正式复核的补行，不改变其消费状态；59123 的映射应用不解除闰月段排除。',
 'R4 #6 见证独立性判定：三家网络转录逐字同读含讹文，按 TJ-018.2 口径'
 '判为同一数字谱系。此判定只及本批所查三家与 kanripo 通道；「无独立'
 '见证」表述限于当前可及通道，不宣称刊本不存在。',
 'R5 字序类读法的登记形制：以两字位互换的两条校勘记表达（#6 提案 '
 'sf-prop-85107/85108、#7 登记 sf-var-85178/85179），使「原文切片经'
 '校勘记变换 == mapped_reading」机检对字序同样成立；引文恒保留原序。',
 'R6 本批零判定代码、零 Variant 行为变更：TJ-017.1 三个 Variant 的'
 '输入/输出/限制逐字不变；神峰例 2 在方向 Variant 中仍只作 '
 'corroboration_direction_only，日级换算 Golden 仍不收其日数。']

COLLATION_LIMITATIONS = [
 '「越三嵗九月」之「三」的语义未解：传本同文只证明其非转写讹，不证明'
 '其义可通；该句维持 registered_not_encoded。',
 '神峰例 2 的校定提案（三四十二日 / 戊寅）无独立见证支持，提案不采纳'
 '为登记读法；若日后取得异谱系见证，须另批复核后方可变更本注册表。',
 '本批见证均为电子转录谱系（kanripo 四库转录、NiuTrans、GuWen、'
 'youngzs、F25731），未查纸本/影印刊本；见证身份已逐条标注。',
 '卷十一赋文两 PUA 点位只作点位登记；赋文全篇不在任何登记窗口内，'
 '不因本批获得引用资格。',
 '三命整书 quarantine_only、canonical_ready=false 不变；本批点位之外'
 '的《论大运》节文本与神峰《起大运法》节文本不因本批扩大审定范围。']
