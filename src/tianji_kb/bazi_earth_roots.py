"""TJ-011.2 土根表分级审定登记（审定+登记批：只登记，不实现）。

本批对象：S2 实现批三通道证明坐实的站立缺口「土根位整线零登记」
（bazi_metal_water_roots.METAL_YOU_SATISFIABILITY 通道三自述为登记/
政策缺口、非历法事实，并预登记「若将来土根位经审定登记，本通道须
复核」）。形制沿 S1 金/水根分级审定（bazi_metal_water_roots）：纯
数据登记模块 + 裁定文档（docs/product/TJ0112_EARTH_ROOT_ADJUDICATION
.md)，逐干逐支定级、等级分层、冲突分支并列不裁定。

材料：TJ-018-A 已登记的《三命通会》卷二《论天干阴阳生死》逐干铺陈
中戊/己两干的禄/生/死句（STEM_COVERAGE 戊/己锚点俱全，与金/水四干
同节同批登记，本批按登记惯例登记整句引文）；论曰总结段的土行讨论
（sm2.summary_tu，018-A 已登记整段引文）；神峰卷首短表群（禄表为
干级、其余四生/四官/四库/四绝为五行级，均经 018-A 登记）互证。

登记内容：
1. 戊/己两干根表逐干逐支定级（两干×十二支共 24 格全部定级或显式
   待定，无空格）：重根只有禄位两格（逐干明句、三重干级见证）；
   长生/帝旺八格随土长生 conflict 分支待定；轻根层整体缺证（滴天
   髓根列举三列对土行零列举，机检在案），八个结构根格标
   structural_present_ungraded（结构存在、分级未定）；无根六格。
2. 土长生 conflict 分支登记：与丁/辛/癸长生同型的体例冲突（阴阳
   分判＋火土母子 vs 五行统摄·水土同宫），按 DING_CHANGSHENG_
   CONFLICT 同形制并列登记、**不裁定**。与金/水不同：金/水只阴干
   分歧（阳干两体例合流），土则两干皆分歧——分支乙是「水土同宫」
   的整行统摄读法，戊、己同作生申；分支甲为三命逐干自述（戊生
   寅、己生酉），且同书论曰段有明确论证与驳斥（戊生申设问句）。
   分歧更深，处置口径不变：并列登记、引用必须指名分支。
3. 帝旺处置：戊/己帝旺位全部随分支（戊：甲作午/乙作子；己：甲
   作巳/乙作子），无一格可如庚酉/壬子那样以 framework_derived
   定级（其前提是长生位无冲突）——本批 framework_derived 计数
   为 0，如实登记。
4. 接口审计（CONSUMPTION_AUDIT）：逐面登记土根位的下游消费面与
   本批前后的状态：S2 金属形态的显干根位资格面（通道三）、
   F34 EARTH_ROOT_INTERFACE 的 pending surface、火线两形态的土
   藏干记录事实、土日主未来形态、格局线司令事实层。本批只在
   登记层填补缺口，**不接入任何运行时消费**。

本模块是纯数据登记，**零计算逻辑、零函数**：不编写任何新谓词，
不改变既有七谓词（木×卯 pure / 木×酉 isolated / 木×亥 generating /
丙×午 commanding / 丙×巳 lu / 金×酉 pure_metal / 水×子 pure_water）
的任何条件与输出，密封 policy 文件零改动。凡分级依据，一律在条目
内标注等级：per_stem_listed（逐干明句）/ framework_derived（推步）/
light_listed_conflicted（轻根列举含冲突）/ conflicted_pending（随
conflict 分支待定）/ structural_present_ungraded（结构存在未分级）/
no_root（无根）。
"""

EARTH_REGISTER_ID = 'bazi-earth-root-grading-v1'

EARTH_TASK = 'TJ-011.2'

EARTH_SNAPSHOTS = {
'sanming_tonghui.txt': {
'snapshot_path': 'data/quarantine/public_domain_snapshots/daizhigev20/sanming_tonghui.txt',
'sha256': '00e2a7db8bb59b259b99938033bb1bb77947e04a15dafc111e62b59378010c86',
'bytes': 1342659,
'chars': 461157},
'shenfeng_tongkao.txt': {
'snapshot_path': 'data/quarantine/public_domain_snapshots/daizhigev20/shenfeng_tongkao.txt',
'sha256': '121a571b7fa63e073f067d5532a42e2feb7d4d5fdd7874de2ca48036a615e200',
'bytes': 422432,
'chars': 154642},
'ditiansui_chanwei.txt': {
'snapshot_path': 'data/quarantine/public_domain_snapshots/daizhigev20/ditiansui_chanwei.txt',
'sha256': '6a875a317c7ba1012285ed12d3bfa5577b50c9fdfd568ece323a12feafe38795',
'bytes': 368684,
'chars': 139538}}

# 本批新登记引文（三命卷二逐干铺陈戊/己两干禄/生死句与生位理据句）：
# 018-A 的 STEM_COVERAGE 已登记其短锚与定位，本批按登记惯例登记
# 整句引文，逐字保留快照原字（「爲」为快照原字；戊禄句首字「己」
# 经校勘记 sm2-ji-40135 读巳，只入 mapped_reading、不回写引文）。
# 定位与整句均经密封快照切片复核（全文计数 ==1，见密封专项）。
EARTH_QUOTES = [
{'id': 'sm.wu_lu',
'source_id': 'bazi.source.sanmingtonghui',
'source_section_id': 'sanming.juan2.tiangan_yinyang_shengsi',
'part_id': 'per_stem_exposition',
'role': 'root_table_evidence',
'quote': '其禄在己巳爲炉冶之火',
'locator': {'char_start': 40132, 'char_end': 40142},
'mapped_reading': '「其禄在巳，巳爲炉冶之火」（首字「己」经校勘记 '
                  'sm2-ji-40135 读巳）',
'collation_refs': ['sm2-ji-40135'],
'note': '戊段禄句（018-A STEM_COVERAGE 戊 lu 锚）。'},
{'id': 'sm.wu_shengsi',
'source_id': 'bazi.source.sanmingtonghui',
'source_section_id': 'sanming.juan2.tiangan_yinyang_shengsi',
'part_id': 'per_stem_exposition',
'role': 'root_table_evidence',
'quote': '故戊土生于寅而死于酉',
'locator': {'char_start': 40230, 'char_end': 40240},
'note': '戊段生死合句：生寅、死酉——TU_CHANGSHENG_CONFLICT 分支甲'
        '（三命干级自述）的逐干明句。'},
{'id': 'sm.wu_sheng_rationale',
'source_id': 'bazi.source.sanmingtonghui',
'source_section_id': 'sanming.juan2.tiangan_yinyang_shengsi',
'part_id': 'per_stem_exposition',
'role': 'conflict_branch_evidence',
'quote': '丙生于寅寅属艮艮爲山山爲刚土卽戊土也頼丙火而生焉',
'locator': {'char_start': 40174, 'char_end': 40198},
'note': '戊段生位理据句：戊赖丙火而生、丙生于寅，故戊生于寅（火土'
        '母子说）——分支甲的理据陈述，非独立长生位句。'},
{'id': 'sm.ji_lu',
'source_id': 'bazi.source.sanmingtonghui',
'source_section_id': 'sanming.juan2.tiangan_yinyang_shengsi',
'part_id': 'per_stem_exposition',
'role': 'root_table_evidence',
'quote': '其禄到午午中丁火',
'locator': {'char_start': 40448, 'char_end': 40456},
'note': '己段禄句（018-A STEM_COVERAGE 己 lu 锚；紧邻字符 40447 '
        '为 PUA 经 sm2-pua-40447 校定，引文避开该位）。'},
{'id': 'sm.ji_shengsi',
'source_id': 'bazi.source.sanmingtonghui',
'source_section_id': 'sanming.juan2.tiangan_yinyang_shengsi',
'part_id': 'per_stem_exposition',
'role': 'root_table_evidence',
'quote': '故己土生于酉而死于寅',
'locator': {'char_start': 40515, 'char_end': 40525},
'note': '己段生死合句：生酉、死寅——分支甲的逐干明句。'},
{'id': 'sm.ji_sheng_rationale',
'source_id': 'bazi.source.sanmingtonghui',
'source_section_id': 'sanming.juan2.tiangan_yinyang_shengsi',
'part_id': 'per_stem_exposition',
'role': 'conflict_branch_evidence',
'quote': '至于酉地丁火而生丁火既生己土亦能生也',
'locator': {'char_start': 40469, 'char_end': 40487},
'note': '己段生位理据句：丁火生于酉、己随丁而生——分支甲理据以'
        '丁生酉为据，与丁长生 conflict 的文本关联见 '
        'TU_CHANGSHENG_CONFLICT internal_tensions。'}]

# 分级词汇（不得混用、不得升级表述）：
GRADE_VOCABULARY = {
 'per_stem_listed': '逐干明句级：三命卷二逐干铺陈有该干该位的明句'
                    '（长生/禄/死），引文登记在案。重根位用此级。'
                    '本批只有禄位两格（戊巳/己午）达此级——土的'
                    '长生位明句本身即 conflict 的分支甲载体，不单独'
                    '作定级（见 conflicted_pending）。',
 'framework_derived': '推步级：长生位明句＋十二宫次序框架节登记＋'
                      '阴阳顺逆推得，无逐干逐字句，属推论级。'
                      '本批计数为 0：戊/己长生位皆有 conflict，无'
                      '无争议长生位可供推步定级（庚酉/壬子式定级'
                      '的前提不成立），帝旺四格全随分支待定。',
 'light_listed_conflicted': '轻根列举级（含冲突）：滴天髓根列举'
                            '（墓列/余气列）明列为该行轻根位。本批'
                            '计数为 0：三列对土行零列举（机检在'
                            '案，见 EARTH_LIGHT_ROOT_STATUS），土'
                            '轻根无列举依据，任何格不得标此级。',
 'conflicted_pending': '待定级：本格定级随未裁定的土长生 conflict '
                       '分支而定（见 TU_CHANGSHENG_CONFLICT 的 '
                       'affected_cells），两分支读法并列登记，本批'
                       '不裁定。',
 'structural_present_ungraded': '结构存在未分级：该支藏有本行之干'
                       '（执行事实层藏干结构事实），根的存在性成立；'
                       '但已登记材料无该格的重/轻分级依据——不在'
                       '重根三位（长生/禄/帝旺定级面）内、滴天髓列举'
                       '不及土、推步宫位名不单独产生根级（S1 口径）。'
                       'is_heavy 恒为 None：不得默认其为轻根，亦不得'
                       '默认其为无根；消费方须以未审面处置（见 '
                       'CONSUMPTION_AUDIT 的接入前置条件）。',
 'no_root': '无根：该支不藏本行之干（结构事实）且无根列举依据；含'
            '死/绝/病等非根位与推步非根位。宫位名在两分支间不一致'
            '者只登记定性、不登记宫位名。'}

# 十二宫序（两分支并列登记，供根表 position_kind 与推步链引用）：
# 分支甲（三命干级自述）：戊生寅、阳干顺行；己生酉、阴干逆行——两
# 序均与本干逐干明句自洽（戊：临官巳=禄巳、死酉=明句；己：临官午
# =禄午、死寅=明句）。
# 分支乙（五行统摄·水土同宫）：戊、己共用同一宫序（生申），与神峰
# 五行级四表逐项自洽（临官亥/墓辰/绝巳均与 sf.siguan / sf.siku /
# sf.sijue 一致）——沿 S1 分支乙口径（同行阳干宫序共用）。
PALACE_SEQUENCES = {
 '戊': {
  'branch_a': {'子': '胎', '丑': '养', '寅': '长生', '卯': '沐浴',
               '辰': '冠带', '巳': '临官', '午': '帝旺', '未': '衰',
               '申': '病', '酉': '死', '戌': '墓', '亥': '绝'},
  'branch_b': {'子': '帝旺', '丑': '衰', '寅': '病', '卯': '死',
               '辰': '墓', '巳': '绝', '午': '胎', '未': '养',
               '申': '长生', '酉': '沐浴', '戌': '冠带', '亥': '临官'}},
 '己': {
  'branch_a': {'子': '绝', '丑': '墓', '寅': '死', '卯': '病',
               '辰': '衰', '巳': '帝旺', '午': '临官', '未': '冠带',
               '申': '沐浴', '酉': '长生', '戌': '养', '亥': '胎'},
  'branch_b': {'子': '帝旺', '丑': '衰', '寅': '病', '卯': '死',
               '辰': '墓', '巳': '绝', '午': '胎', '未': '养',
               '申': '长生', '酉': '沐浴', '戌': '冠带', '亥': '临官'}}}

# 戊根位登记：禄巳为逐干明句重根（不受长生分支影响）；长生寅（分
# 支甲明句）与生申（分支乙五行级）对峙，寅/申两格与两分支的帝旺
# 格（午/子）共四格待定；辰/戌/丑/未藏土（本气或行级本气）而无分
# 级依据，标 structural_present_ungraded；卯/酉/亥无根（酉死位有
# 逐干明句）。
WU_ROOT_POSITIONS = [
{'branch': '子', 'grade': 'conflicted_pending', 'is_heavy': None,
 'position_kind': '帝旺（分支乙·推步）/胎（分支甲）',
 'conflict_id': 'sanming-juan2.tu-changsheng',
 'evidence': [
  {'derivation': '分支乙：水土长生申（五行级，sf.sisheng）＋十二宫'
   '次序（框架节登记 sm2.gong_sequence）＋顺行：申→酉（沐浴）→戌'
   '（冠带）→亥（临官）→子（帝旺）',
   'note': '分支乙宫序内推步级；分支甲宫序子为胎位。子不藏土。'}]},
{'branch': '丑', 'grade': 'structural_present_ungraded',
 'is_heavy': None,
 'position_kind': '结构根（行级：丑藏己本气）·分级未定',
 'evidence': [
  {'note': '丑藏己（本气）：本行结构根存在（执行事实层藏干事实）；'
           '戊本干不自藏于丑，存在性为行级'},
  {'note': '分级依据缺位：两分支宫位名（甲作养、乙作衰）均非根位'
           '名；滴天髓根列举三列不及土（见 EARTH_LIGHT_ROOT_STATUS）'
           '，无轻根列举依据'}]},
{'branch': '寅', 'grade': 'conflicted_pending', 'is_heavy': None,
 'position_kind': '长生（分支甲·逐干明句）/病（分支乙）',
 'conflict_id': 'sanming-juan2.tu-changsheng',
 'evidence': [
  {'quote_ref': 'sm.wu_shengsi', 'register': 'self',
   'note': '分支甲逐干明句「故戊土生于寅而死于酉」'},
  {'quote_ref': 'sm.wu_sheng_rationale', 'register': 'self',
   'note': '分支甲理据「丙生于寅……戊土也，頼丙火而生焉」（火土'
           '母子说）'},
  {'quote_ref': 'sm2.summary_tu',
   'register': 'bazi_sanming_juan2_collation',
   'note': '论曰总结段「戊土生于寅……是戊生于寅也」复述并论证'},
  {'quote_ref': 'sf.sisheng',
   'register': 'bazi_sanming_juan2_collation',
   'note': '分支乙：神峰四生作水土长生居申，寅于其宫序为病位'},
  {'note': '寅藏戊（余气）：结构根存在，与分支甲长生位一致；分支'
           '乙下结构存在性不产生根级'}]},
{'branch': '卯', 'grade': 'no_root', 'is_heavy': False,
 'position_kind': '非根位（宫位名随分支：沐浴/死）',
 'evidence': [
  {'note': '卯不藏土，无任何根列举；宫位名两分支不一致（甲作沐'
           '浴、乙作死），均非根位，不登记宫位名'}]},
{'branch': '辰', 'grade': 'structural_present_ungraded',
 'is_heavy': None,
 'position_kind': '结构根（本气戊）·分级未定',
 'evidence': [
  {'note': '辰藏戊（本气）：本干结构根存在（执行事实层藏干事实）'},
  {'quote_ref': 'sf.siku', 'register': 'bazi_sanming_juan2_collation',
   'note': '神峰四库「水土库居辰」——分支乙体例内的五行级库位陈'
           '述，是本格的候选轻级依据；采之即以分支乙宫序定本格轻'
           '级、预决长生 conflict，本批不采（见 '
           'EARTH_LIGHT_ROOT_STATUS）'},
  {'note': '分支甲宫序辰作冠带（非根位名）；滴天髓列举不及土，'
           '无列举级轻根依据'}]},
{'branch': '巳', 'grade': 'per_stem_listed', 'is_heavy': True,
 'position_kind': '禄/临官',
 'evidence': [
  {'quote_ref': 'sm.wu_lu', 'register': 'self',
   'note': '戊段禄句「其禄在己巳爲炉冶之火」（「己」经 sm2-ji-40135 '
           '校定读巳）'},
  {'quote_ref': 'sf.lubiao',
   'register': 'bazi_sanming_juan2_collation',
   'note': '神峰十干禄表「丙戊禄在巳」互证（干级表）'},
  {'quote_ref': 'sm2.summary_tu',
   'register': 'bazi_sanming_juan2_collation',
   'note': '论曰总结段「戊随丙临官归禄于巳」复述'},
  {'quote_ref': 'sanming.lu_sentence', 'register': 'bazi_pattern',
   'note': '三命卷三《论十干禄》定义句作「戊寄巳」（Slice A 已登记，'
           '字形经同节互证读定）：位置与本格一致，表述为寄禄（子随'
           '母得禄），只作性质注记、不影响根位定级（禄位在滴天髓根'
           '列举总述明列为重根类）'},
  {'note': '分支乙宫序以巳为水土绝位（sf.sijue），是行级框架名；'
           '禄位有三重干级见证，定级不随长生分支（见 '
           'TU_CHANGSHENG_CONFLICT internal_tensions）'}]},
{'branch': '午', 'grade': 'conflicted_pending', 'is_heavy': None,
 'position_kind': '帝旺（分支甲·推步）/胎（分支乙）',
 'conflict_id': 'sanming-juan2.tu-changsheng',
 'evidence': [
  {'derivation': '分支甲：戊长生寅（逐干明句，sm.wu_shengsi）＋'
   '十二宫次序（sm2.gong_sequence）＋阳干顺行：寅→卯（沐浴）→辰'
   '（冠带）→巳（临官）→午（帝旺）',
   'note': '分支甲宫序内推步级；分支乙宫序午为胎位'},
  {'note': '午藏己（中气）：行级结构根存在，不产生根级'}]},
{'branch': '未', 'grade': 'structural_present_ungraded',
 'is_heavy': None,
 'position_kind': '结构根（行级：未藏己本气）·分级未定',
 'evidence': [
  {'note': '未藏己（本气）：本行结构根存在（行级）；戊本干不自藏'
           '于未'},
  {'note': '分级依据缺位：两分支宫位名（甲作衰、乙作养）均非根位'
           '名；滴天髓列举不及土'}]},
{'branch': '申', 'grade': 'conflicted_pending', 'is_heavy': None,
 'position_kind': '长生（分支乙·五行级）/病（分支甲）',
 'conflict_id': 'sanming-juan2.tu-changsheng',
 'evidence': [
  {'quote_ref': 'sf.sisheng',
   'register': 'bazi_sanming_juan2_collation',
   'note': '分支乙：神峰五行级四生「水土长生居申」——五行级陈述，'
           '戊己共用，非干级'},
  {'quote_ref': 'sm2.sida_archive',
   'register': 'bazi_sanming_juan2_collation',
   'note': '三命本节论辩段通论「古人只有四大长生之説」为同源体例'
           '背景（存档，非证据）'},
  {'note': '申藏戊（余气）：结构根存在；分支甲宫序申为病位（长生'
           '寅顺行），不产生根级'}]},
{'branch': '酉', 'grade': 'no_root', 'is_heavy': False,
 'position_kind': '死（分支甲·逐干明句）/沐浴（分支乙）',
 'evidence': [
  {'quote_ref': 'sm.wu_shengsi', 'register': 'self',
   'note': '生死合句明言戊死于酉（分支甲）'},
  {'note': '两分支对酉均为非根位（甲作死、乙作沐浴）；酉不藏土'}]},
{'branch': '戌', 'grade': 'structural_present_ungraded',
 'is_heavy': None,
 'position_kind': '结构根（本气戊）·分级未定',
 'evidence': [
  {'note': '戌藏戊（本气）：本干结构根存在（执行事实层藏干事实）'},
  {'note': '分支甲宫序戌作墓位，是本格的候选轻级依据；采之即以'
           '分支甲宫序定本格轻级、预决长生 conflict，本批不采'
           '（同辰格口径，见 EARTH_LIGHT_ROOT_STATUS）。滴天髓墓列'
           '作「丙丁逢戌」为火行列举，不及土'}]},
{'branch': '亥', 'grade': 'no_root', 'is_heavy': False,
 'position_kind': '非根位（宫位名随分支：绝/临官（乙·五行级））',
 'evidence': [
  {'quote_ref': 'sf.siguan',
   'register': 'bazi_sanming_juan2_collation',
   'note': '分支乙：神峰四官「水土临官在亥」为五行级临官名，其位'
           '为壬禄位，无戊逐干陈述——同行他干禄位不移作本干根'
           '（同 S1 辛分支乙口径）'},
  {'note': '亥不藏土，无任何根列举；分支甲宫序亥作绝位'}]}]

# 己根位登记：禄午为逐干明句重根（不受长生分支影响）；长生酉（分
# 支甲明句）与生申（分支乙五行级，与戊共用）对峙，酉/申两格与两
# 分支的帝旺格（巳/子）共四格待定；丑/未/辰/戌藏土而无分级依据，
# 标 structural_present_ungraded；寅/卯/亥无根（寅死位有逐干明句）。
JI_ROOT_POSITIONS = [
{'branch': '子', 'grade': 'conflicted_pending', 'is_heavy': None,
 'position_kind': '帝旺（分支乙·推步）/绝（分支甲）',
 'conflict_id': 'sanming-juan2.tu-changsheng',
 'evidence': [
  {'derivation': '分支乙：水土长生申（五行级）＋十二宫次序＋顺行'
   '（同戊分支乙宫序）：亥（临官）→子（帝旺）',
   'note': '分支乙宫序内推步级；分支甲宫序子为绝位。子不藏土。'}]},
{'branch': '丑', 'grade': 'structural_present_ungraded',
 'is_heavy': None,
 'position_kind': '结构根（本气己）·分级未定',
 'evidence': [
  {'note': '丑藏己（本气）：本干结构根存在（执行事实层藏干事实）'},
  {'note': '分支甲宫序丑作墓位，是本格的候选轻级依据；采之即以'
           '分支甲宫序定本格轻级、预决长生 conflict，本批不采'
           '（同戊×戌口径）。滴天髓墓列作「庚辛逢丑」为金行列举，'
           '不及土'}]},
{'branch': '寅', 'grade': 'no_root', 'is_heavy': False,
 'position_kind': '死（分支甲·逐干明句）/病（分支乙）',
 'evidence': [
  {'quote_ref': 'sm.ji_shengsi', 'register': 'self',
   'note': '生死合句明言己死于寅（分支甲）'},
  {'note': '寅藏戊为行级结构存在，但两分支对己均非根位（甲作死、'
           '乙作病）、无根列举，不登记为己之根'}]},
{'branch': '卯', 'grade': 'no_root', 'is_heavy': False,
 'position_kind': '非根位（宫位名随分支：病/死）',
 'evidence': [
  {'note': '卯不藏土，无任何根列举；宫位名两分支不一致，均非'
           '根位'}]},
{'branch': '辰', 'grade': 'structural_present_ungraded',
 'is_heavy': None,
 'position_kind': '结构根（行级：辰藏戊本气）·分级未定',
 'evidence': [
  {'note': '辰藏戊（本气）：本行结构根存在（行级）；己本干不自藏'
           '于辰'},
  {'quote_ref': 'sf.siku', 'register': 'bazi_sanming_juan2_collation',
   'note': '神峰四库「水土库居辰」——分支乙体例内的五行级库位陈'
           '述，候选轻级依据，未采（同戊×辰口径）'},
  {'note': '分支甲宫序辰作衰位（非根位名）；滴天髓列举不及土'}]},
{'branch': '巳', 'grade': 'conflicted_pending', 'is_heavy': None,
 'position_kind': '帝旺（分支甲·推步）/绝（分支乙）',
 'conflict_id': 'sanming-juan2.tu-changsheng',
 'evidence': [
  {'derivation': '分支甲：己长生酉（逐干明句，sm.ji_shengsi）＋'
   '十二宫次序＋阴干逆行：酉→申（沐浴）→未（冠带）→午（临官）→'
   '巳（帝旺）',
   'note': '分支甲宫序内推步级'},
  {'quote_ref': 'sf.sijue',
   'register': 'bazi_sanming_juan2_collation',
   'note': '分支乙：神峰四绝「水土绝在巳」——五行级框架名'},
  {'note': '巳藏戊（中气）：行级结构根存在，不产生根级'}]},
{'branch': '午', 'grade': 'per_stem_listed', 'is_heavy': True,
 'position_kind': '禄/临官',
 'evidence': [
  {'quote_ref': 'sm.ji_lu', 'register': 'self',
   'note': '己段禄句「其禄到午午中丁火」'},
  {'quote_ref': 'sf.lubiao',
   'register': 'bazi_sanming_juan2_collation',
   'note': '神峰十干禄表「丁己禄居午」互证（干级表）'},
  {'quote_ref': 'sm2.summary_tu',
   'register': 'bazi_sanming_juan2_collation',
   'note': '论曰总结段「巳临丁临官归禄于午」——己随丁临官归禄于午'
           '的复述（原字巳经校勘记 sm2-si-42072 读己）'},
  {'quote_ref': 'sanming.lu_sentence', 'register': 'bazi_pattern',
   'note': '三命卷三《论十干禄》定义句作「己寄午」（Slice A 已登'
           '记，字形经同节互证读定）：位置一致、寄禄表述，只作性'
           '质注记、不影响根位定级'},
  {'note': '分支乙宫序以午为胎位（行级框架名）；禄位三重干级见'
           '证，定级不随长生分支'}]},
{'branch': '未', 'grade': 'structural_present_ungraded',
 'is_heavy': None,
 'position_kind': '结构根（本气己）·分级未定',
 'evidence': [
  {'note': '未藏己（本气）：本干结构根存在（执行事实层藏干事实）'},
  {'note': '分级依据缺位：两分支宫位名（甲作冠带、乙作养）均非'
           '根位名；滴天髓列举不及土'}]},
{'branch': '申', 'grade': 'conflicted_pending', 'is_heavy': None,
 'position_kind': '长生（分支乙·五行级）/沐浴（分支甲）',
 'conflict_id': 'sanming-juan2.tu-changsheng',
 'evidence': [
  {'quote_ref': 'sf.sisheng',
   'register': 'bazi_sanming_juan2_collation',
   'note': '分支乙：神峰五行级四生「水土长生居申」，戊己共用、'
           '非干级'},
  {'note': '申藏戊（余气）：行级结构根存在；分支甲宫序申作沐浴'
           '（长生酉逆行），不产生根级'}]},
{'branch': '酉', 'grade': 'conflicted_pending', 'is_heavy': None,
 'position_kind': '长生（分支甲·逐干明句）/沐浴（分支乙）',
 'conflict_id': 'sanming-juan2.tu-changsheng',
 'evidence': [
  {'quote_ref': 'sm.ji_shengsi', 'register': 'self',
   'note': '分支甲逐干明句「故己土生于酉而死于寅」'},
  {'quote_ref': 'sm.ji_sheng_rationale', 'register': 'self',
   'note': '分支甲理据「至于酉地丁火而生，丁火既生己土亦能生也」'
           '（己随丁生于酉）'},
  {'note': '分支乙宫序酉作沐浴（水土长生申顺行次位）；酉不藏土'
           '——根位不以本干自藏为必要（同庚×酉推步重根先例，位级'
           '依据为宫序与明句）'}]},
{'branch': '戌', 'grade': 'structural_present_ungraded',
 'is_heavy': None,
 'position_kind': '结构根（行级：戌藏戊本气）·分级未定',
 'evidence': [
  {'note': '戌藏戊（本气）：本行结构根存在（行级）；己本干不自藏'
           '于戌'},
  {'note': '分级依据缺位：两分支宫位名（甲作养、乙作冠带）均非'
           '根位名；滴天髓列举不及土'}]},
{'branch': '亥', 'grade': 'no_root', 'is_heavy': False,
 'position_kind': '非根位（宫位名随分支：胎/临官（乙·五行级））',
 'evidence': [
  {'quote_ref': 'sf.siguan',
   'register': 'bazi_sanming_juan2_collation',
   'note': '分支乙：神峰四官「水土临官在亥」为五行级临官名，其位'
           '为壬禄位，无己逐干陈述，不移作己根（同戊×亥口径）'},
  {'note': '亥不藏土，无任何根列举；分支甲宫序亥作胎位'}]}]

EARTH_ROOT_TABLES = {
 '戊': WU_ROOT_POSITIONS,
 '己': JI_ROOT_POSITIONS}

HEAVY_ROOT_BRANCHES = {
 '戊': ['巳'],
 '己': ['午']}

PENDING_ROOT_BRANCHES = {
 '戊': ['子', '寅', '午', '申'],
 '己': ['子', '巳', '申', '酉']}

UNGRADED_STRUCTURAL_BRANCHES = {
 '戊': ['丑', '辰', '未', '戌'],
 '己': ['丑', '辰', '未', '戌']}

LIGHT_ROOT_BRANCHES = {
 '戊': [],
 '己': []}

# 藏本干之支（本干结构根所在）：戊藏于寅（余气）/辰（本气）/巳
# （中气）/申（余气）/戌（本气）；己藏于丑（本气）/午（中气）/未
# （本气）。藏本行任一干之支（行级结构存在面）为八支。
STRUCTURAL_ROOT_BRANCHES = {
 '戊': ['寅', '辰', '巳', '申', '戌'],
 '己': ['丑', '午', '未']}

ELEMENT_STRUCTURAL_BRANCHES = ['丑', '寅', '辰', '巳', '午', '未',
                               '申', '戌']

# 土长生 conflict 登记（与 018-A DING_CHANGSHENG_CONFLICT 及 S1 辛/
# 癸 conflict 同形制：两说并列、各自来源定位、不裁定）。与金/水冲
# 突的结构差异如实登记：金/水只阴干分歧（阳干两体例合流），土则
# 两干皆分歧——分支乙是「水土同宫」的整行统摄（一句「水土长生居
# 申」同定两干），分支甲是三命逐干自述且同书论曰段有论证与驳斥；
# 本登记据此合并为一个 conflict（两干同行同源），两干的分支读法
# 在 branches 内逐干分列。
TU_CHANGSHENG_CONFLICT = {
 'conflict_id': 'sanming-juan2.tu-changsheng',
 'subject': '土长生位（戊/己）',
 'status': 'conflict',
 'adjudication': None,
 'research_only': True,
 'genre_note': '与丁/辛/癸长生 conflict 同型：阴阳分判与五行统摄两'
               '种体例之争。惟土行分歧面更宽：分支乙（神峰四生「水'
               '土长生居申」）是水土同宫的整行统摄，戊、己同作生'
               '申；分支甲（三命逐干铺陈）戊生寅、己生酉，且同书'
               '论曰段以设问句明确驳斥戊生申读法。神峰四生为五行'
               '级表、非干级陈述；三命逐干铺陈与论曰为干级自述与'
               '论证。粒度与论证强度差异如实登记，但不据此消解任'
               '何一方（同丁 conflict 处置：其分支甲见证更强，仍'
               '未裁定）。',
 'branches': [
  {'branch_id': 'tu-sheng-yin-you',
   'reading': {'戊': '寅', '己': '酉'},
   'system': '阴阳分判＋火土母子（三命干级自述）',
   'evidence': [
    {'quote_ref': 'sm.wu_shengsi',
     'source_id': 'bazi.source.sanmingtonghui', 'register': 'self',
     'note': '三命本节戊段「故戊土生于寅而死于酉」——戊生寅与死酉'
             '同属阳干顺行宫序，自洽'},
    {'quote_ref': 'sm.ji_shengsi',
     'source_id': 'bazi.source.sanmingtonghui', 'register': 'self',
     'note': '三命本节己段「故己土生于酉而死于寅」——己生酉与死寅'
             '同属阴干逆行宫序，自洽'},
    {'quote_ref': 'sm.wu_sheng_rationale',
     'source_id': 'bazi.source.sanmingtonghui', 'register': 'self',
     'note': '戊段理据：戊赖丙火而生、丙生于寅（火土母子说）'},
    {'quote_ref': 'sm.ji_sheng_rationale',
     'source_id': 'bazi.source.sanmingtonghui', 'register': 'self',
     'note': '己段理据：丁火生于酉、己随丁而生'},
    {'quote_ref': 'sm2.summary_tu',
     'source_id': 'bazi.source.sanmingtonghui',
     'register': 'bazi_sanming_juan2_collation',
     'note': '同书论曰总结段「戊土生于寅……巳土生于酉明矣，若以戊'
             '生申巳生邜，何不以壬戊归禄于亥癸巳归禄于子」——作者'
             '自述结论与对分支乙读法的设问驳斥（巳经校勘记读己、'
             '邜为异体）'}]},
  {'branch_id': 'tu-sheng-shen',
   'reading': {'戊': '申', '己': '申'},
   'system': '五行统摄（水土同宫，四大长生体例）',
   'evidence': [
    {'quote_ref': 'sf.sisheng', 'source_id': 'bazi.source.shenfeng',
     'register': 'bazi_sanming_juan2_collation',
     'note': '神峰五行级四生「水土长生居申」——五行级陈述，水土共'
             '用一语、戊己共用，非干级'},
    {'quote_ref': 'sf.siguan', 'source_id': 'bazi.source.shenfeng',
     'register': 'bazi_sanming_juan2_collation',
     'note': '同体例旁证：四官「水土临官在亥」与分支乙宫序自洽'},
    {'quote_ref': 'sf.siku', 'source_id': 'bazi.source.shenfeng',
     'register': 'bazi_sanming_juan2_collation',
     'note': '同体例旁证：四库「水土库居辰」与分支乙宫序自洽'},
    {'quote_ref': 'sf.sijue', 'source_id': 'bazi.source.shenfeng',
     'register': 'bazi_sanming_juan2_collation',
     'note': '同体例旁证：四绝「水土绝在巳」与分支乙宫序自洽'},
    {'quote_ref': 'sm2.sida_archive',
     'source_id': 'bazi.source.sanmingtonghui',
     'register': 'bazi_sanming_juan2_collation',
     'note': '三命本节论辩段通论「古人只有四大长生之説」为同源体'
             '例背景（存档，非证据）'}]}],
 'affected_cells': [
  {'stem': '戊', 'branch': '寅',
   'under_branch_a': '长生（重根，逐干明句）',
   'under_branch_b': '非根（水土宫序病位）'},
  {'stem': '戊', 'branch': '申',
   'under_branch_a': '非根（宫序病位）',
   'under_branch_b': '长生（重根，五行级）'},
  {'stem': '戊', 'branch': '午',
   'under_branch_a': '帝旺（重根，分支内推步）',
   'under_branch_b': '非根（水土宫序胎位）'},
  {'stem': '戊', 'branch': '子',
   'under_branch_a': '非根（宫序胎位）',
   'under_branch_b': '帝旺（重根，分支内推步）'},
  {'stem': '己', 'branch': '酉',
   'under_branch_a': '长生（重根，逐干明句）',
   'under_branch_b': '非根（水土宫序沐浴位）'},
  {'stem': '己', 'branch': '申',
   'under_branch_a': '非根（宫序沐浴位）',
   'under_branch_b': '长生（重根，五行级）'},
  {'stem': '己', 'branch': '巳',
   'under_branch_a': '帝旺（重根，分支内推步）',
   'under_branch_b': '非根（水土绝位）'},
  {'stem': '己', 'branch': '子',
   'under_branch_a': '非根（宫序绝位）',
   'under_branch_b': '帝旺（重根，分支内推步）'}],
 'internal_tensions': [
  '分支乙宫序下水土临官在亥（神峰四官），与戊/己禄位（巳/午）不'
  '一致；且分支乙的绝位（巳）恰为戊禄位、胎位（午）恰为己禄位。'
  '禄位有三重干级见证（三命卷二逐干句、卷三禄节逐一明列、神峰'
  '干级禄表），不在本冲突射程内——定级不随分支（同 S1 辛/癸禄位'
  '处置）。',
  '三命本书论曰段对分支乙读法有明确驳斥（设问句），论辩引述段另'
  '存「以戊生申酉沐浴戌冠带，阴阳间隔谬□甚矣」的批评文字与或曰'
  '归母说（均属 archived_not_evidence 层次，只登记存档）——本冲'
  '突的登记对象是跨来源体例并列（三命干级自述 vs 神峰五行级'
  '表），不以三命自家论证消解神峰体例，亦不以神峰五行级表径作'
  '干级读。',
  '己生酉的理据（三命己段）以丁生于酉立论，与丁长生 conflict '
  '（sanming-juan2.ding-changsheng）的分支甲同读：两 conflict '
  '在三命文本内存在理据关联。两 conflict 独立登记、互不牵连结'
  '论；丁 conflict 将来若有处置，己分支甲的理据强度须复核，但'
  '己段生死合句本身不依赖该理据。'],
 'unaffected': [
  '戊禄巳、己禄午：三重干级见证（卷二逐干句＋卷三禄节逐一明列＋'
  '神峰干级禄表），且禄为独立根位类别（滴天髓根列举总述「长生'
  '禄旺，根之重者也」），定级不随长生分支',
  '土轻根层整体缺证（滴天髓列举不及土）：与长生分支无关，八个'
  '结构根格的分级未定状态不随分支改变'],
 'statement': '两说并列登记、不裁定；任何后续引用必须指名分支。'
              '戊/己根表中八格标 conflicted_pending；任何消费方对'
              '根位于此八格的情形须作冲突阻断（abstain），不得取'
              '任一分支单独建模。丁/辛/癸三长生 conflict 的处置与'
              '本冲突相互独立，本批均不碰结论。'}

# 帝旺处置（沿火线裁定二与 S1 裁定四的口径，本批结论汇总）：与金/
# 水不同，土无一格达 framework_derived 定级——庚/壬的推步定级以
# 「长生位无冲突」为前提，戊/己长生位皆在 conflict 内，帝旺位全部
# 随分支待定。
DIWANG_DISPOSITION = {
 'question': '戊/己帝旺位无逐干逐字句（承 018-A no-diwang-'
             'sentence），根表帝旺格如何处置',
 'verdict': 'branch_pending_for_both_stems_no_uncontested_cell',
 'statement': '戊帝旺随分支（甲作午、乙作子）、己帝旺随分支（甲作'
              '巳、乙作子），四格全登记为 conflicted_pending，无一'
              '格可以 framework_derived 定级。禄位两格的重根定级'
              '不经帝旺，不受影响。任何引用提及戊/己帝旺位必须指'
              '名分支（如「分支甲推步戊帝旺午」），不得表述为定级'
              '结论。',
 'derived_positions': [
  {'stem': '戊', 'branch': '午', 'under_branch': 'branch_a',
   'derivation': '戊长生寅（分支甲逐干明句）＋十二宫次序＋阳干顺'
                 '行：寅→卯→辰→巳（临官）→午（帝旺）'},
  {'stem': '戊', 'branch': '子', 'under_branch': 'branch_b',
   'derivation': '水土长生申（分支乙五行级）＋十二宫次序＋顺行：'
                 '申→酉→戌→亥（临官）→子（帝旺）'},
  {'stem': '己', 'branch': '巳', 'under_branch': 'branch_a',
   'derivation': '己长生酉（分支甲逐干明句）＋十二宫次序＋阴干逆'
                 '行：酉→申→未→午（临官）→巳（帝旺）'},
  {'stem': '己', 'branch': '子', 'under_branch': 'branch_b',
   'derivation': '水土长生申（分支乙五行级，与戊共用宫序）：亥'
                 '（临官）→子（帝旺）'}],
 'forbidden_phrasings': ['戊帝旺在午（原文）', '三命明言戊旺于午',
                         '戊帝旺在子（原文）', '三命明言戊旺于子',
                         '己帝旺在巳（原文）', '三命明言己旺于巳',
                         '己帝旺在子（原文）', '三命明言己旺于子'],
 'assessment_ref': 'bazi_sanming_juan2_collation.ROOT_TABLE_'
                   'ASSESSMENT（verdict=partial，derived_positions '
                   '含帝旺）＋ bazi_metal_water_roots.DIWANG_'
                   'DISPOSITION（金/水帝旺处置：无冲突干推步、冲突'
                   '干待定的分工先例）'}

# 土轻根层状态登记（本批实测发现）：滴天髓根列举对土行零列举，
# 轻根层整体缺证——这是审定结论，不是审定疏漏。
EARTH_LIGHT_ROOT_STATUS = {
 'status': 'no_listing_basis_registered_gap',
 'statement': '滴天髓根列举三列（墓列 dt.root_mu、余气列复本一 '
              'dt.root_yuqi_1、复本二 dt.root_yuqi_2）逐字核查：只'
              '列木/火/金/水四行干对（甲乙/丙丁/庚辛/壬癸），土行'
              '（戊己）零出现——快照全文「戊己逢」计数为 0（机上'
              '实测，密封专项复核列举段切片）。故土轻根无列举级'
              '依据，任何格不得标 light_listed 或 '
              'light_listed_conflicted。',
 'candidate_bases_not_adopted': [
  {'cells': ['戊×戌', '己×丑'],
   'candidate': '分支甲宫序墓位（戊：长生寅顺行戌作墓；己：长生'
                '酉逆行丑作墓）',
   'reason_not_adopted': '宫位名不单独产生轻根（S1 口径：辛×辰、'
                         '癸×未两格为显式实例）；且采分支甲宫序定'
                         '轻级即预决土长生 conflict'},
  {'cells': ['戊×辰', '己×辰'],
   'candidate': '分支乙宫序墓位＋神峰四库「水土库居辰」（五行级）',
   'reason_not_adopted': '四库是分支乙体例内的五行级陈述；采之即'
                         '以分支乙宫序定轻级、预决 conflict。神峰'
                         '四库在 S1 中只作滴天髓已列格的旁证，从未'
                         '单独作轻级依据，本批不升格其证据地位'}],
 'disposition': '八个结构根格（戊/己各丑、辰、未、戌）统一标 '
                'structural_present_ungraded：结构存在在案、分级'
                '待定。轻根层在本 conflict 裁定或有列举级新来源之'
                '前维持缺证状态；将来若立土轻根，须另行审定批并'
                '为八格逐格给依据，不得以本登记的结构存在性径行'
                '升格。'}

# 与既有登记/政策的口径对齐说明。本批零 policy 改动：
# policy_files_changed 恒为空集，密封测试另行断言密封政策无土集、
# 本登记模块不引用、不修改任何密封政策路径。
POLICY_ALIGNMENT = {
 'reference': '密封政策 bazi.concept.action_effects_v1.'
              'reviewed_root_branches（木：[亥，寅，卯]，水：[亥，'
              '子]，金：[酉]——无土集）；公开登记 '
              'bazi_metal_water_roots.METAL_WATER_ROOT_TABLES'
              '（金/水根表）、bazi_fire_morphology.BING_ROOT_'
              'POSITIONS（丙根表）',
 'statement': '口径对齐三点：(1) 分级形状同构：重根恒为长生/禄/帝'
              '旺三位、按逐干明句 / 推步 / 随分支待定分层，轻根只'
              '据列举、只作 blocker，总述锚同为滴天髓根列举总述'
              '（dt.root_heavy_light）——土表与金/水表同此形状，差'
              '异只在材料实测结果（土长生两干皆冲突、轻根列举缺'
              '位），不另立口径。(2) 对象不同、不互相冒充：密封政'
              '策的已审集是月份本气根位集且无土集，本表是逐干全'
              '支根表——本批不改动密封政策、不以本表冒充政策已'
              '审；将来消费本表须沿 S2 的 register-based 先例另'
              '行接入，密封 Phase1/Phase2 注册 pending 另行披露。'
              '(3) 本表补的是 S1 裁定文档未覆盖清单所记「土根零'
              '登记」一面；同条所记「四季月 principal 未审」不在'
              '本批范围，土日主整线不因本表登记而解锁。',
 'policy_files_changed': []}

# 接口审计（本批交付内容二）：逐面审计土根位的下游消费面，登记本
# 批落地前后的状态与接入前置条件。本批不改任何消费方代码。
CONSUMPTION_AUDIT = {
 'surfaces': [
  {'surface': 'S2 金属形态 all_visible_have_registered_roots 的土'
              '显干面（bazi_action_conditions.registered_eligible：'
              '土显干无已审根位集、恒不合）＋ METAL_YOU_'
              'SATISFIABILITY 通道三（土印显干根位登记缺口）',
   'before': '土根零登记：密封政策无土集、无任何土根登记表，土显'
             '干在本条件恒假，通道三据此成立',
   'after': '登记面已变：土根由「零登记」变为「有分级登记」——戊/'
            '己各有一格 per_stem_listed 重根（巳/午），其形状与 S2 '
            '资格规则（grade 非 no_root 且非 conflicted_pending 的'
            '格位）相容，可作土显干根位资格的登记依据',
   'still_pending': [
    '运行时消费面不变：本批不改 bazi_action_conditions.py 一字，'
    'registered_eligible 仍不查本表，土显干运行时仍恒不合；通道三'
    '的登记陈述（「土根零登记」）自本批起与登记面不符，其订正与'
    '接入同属消费接入批，须在该批复核后改写，不得在本批顺手改'
    '动 S2 登记文本',
    'structural_present_ungraded 八格不在 S2 既有格级枚举内：接入'
    '批必须先裁定其资格。本批登记口径为：未分级即未审，不得计作'
    'eligible；若接入时按现行排除法（仅排除 no_root 与 '
    'conflicted_pending）机械查表，ungraded 格会被误计——此为接'
    '入前置条件，接入批须显式处置',
    'conflicted_pending 八格按既有口径永不计资格（冲突阻断）',
    '通道一、二（藏干唯一支、全酉显干干对）是历法构造性事实，不'
    '因本批改变：金×酉形态仍 chart_unrealizable，本批不改变任何'
    '谓词的裁定面']},
  {'surface': 'F34 EARTH_ROOT_INTERFACE 的 pending_surface（F3/F4 '
              '审定批登记的待办面）',
   'before': '第 1 项：以土为印或同类的形态（土日主、金日主超出 '
             'S2 登记面者）须先审定戊/己显干根位资格；第 2 项：消'
             '费藏干根位资格的形态须先审定该资格',
   'after': '第 1 项在登记层已填写：显干根位资格面 = 禄位两格'
            '（戊巳/己午）已审定，长生/帝旺八格随 conflict 待定、'
            '结构根八格分级待定——资格面是窄面，不是全表可用',
   'still_pending': [
    '第 2 项（藏干根位资格的消费口径）本批未审：本登记给的是逐'
    '干根表（日主/显干查表口径），藏干资格如何消费另行审定，'
    '维持 pending',
    'F34 两形态本身不消费土根位的结论（EARTH_ROOT_INTERFACE.'
    'audit_conclusion）不因本批改变']},
  {'surface': '火线两形态的土藏干记录事实（F1 午中己、F3 巳中戊、'
              'F4 寅中戊：治理约定下只作记录、不计效不否决）',
   'before': '藏干土只作记录事实，无任何土根分级可引用',
   'after': '登记层现可指名其结构位格级：巳藏戊的位为戊禄位重根'
            '（戊×巳 per_stem_listed）、寅藏戊的位为待定格（戊×寅 '
            'conflicted_pending）、午藏己的位为己禄位重根（己×午 '
            'per_stem_listed）——供将来藏干资格审定引用',
   'still_pending': [
    '治理约定的记录口径不变：本批不使任何藏干土由「记录」升为'
    '「计效」，F1/F3/F4 条件一字未动']},
  {'surface': '土日主未来形态（戊/己日主旺衰谓词）',
   'before': '土根零登记，无任何根审定材料',
   'after': '根审定前置材料已备：逐干根表与分级、冲突结构、帝旺'
            '处置、轻根缺证结论均在册',
   'still_pending': [
    '可用重根面只有禄位两格：土日主 pure/commanding 类形态的长'
    '生/帝旺要件全在 conflict 内，在 conflict 处置（用户裁定级'
    '流派取舍）或分支并列建模授权之前不可建',
    '四季月（辰戌丑未月）principal 关系未审（S1 未覆盖清单在'
    '案），不在本批范围；土日主整线仍未解锁']},
  {'surface': '格局线与司令事实层（寅月司令戊段等藏干司事事实）',
   'before': '消费藏干司事/透干事实，不消费根分级',
   'after': '不受本批影响（本登记不进入格局线任何事实通道）',
   'still_pending': []}],
 'statement': '本批只完成登记层填补：由「零登记」变为「有分级登'
              '记可消费」的只有登记面本身；一切运行时消费面（谓词'
              '条件、资格判定、通道三陈述订正）均属另批，本批零'
              '接入。登记在案的接入前置条件（ungraded 资格裁定、'
              '通道三复核）对后续消费批有约束力，不得跳过。'}

# 根表可推性评估（本批验收项，承 018-A ROOT_TABLE_ASSESSMENT 的
# partial 结论在本批范围内的细化）。
ROOT_TABLE_ASSESSMENT_EARTH = {
 'verdict': 'graded_with_registered_conflict_and_ungraded_light_'
            'layer',
 'statement': '戊/己两干根表：禄位两格逐干明句定级（三重干级见'
              '证、不随长生分支）；长生与帝旺共八格随土长生 '
              'conflict 分支待定（逐格登记、影响面明示）；轻根层'
              '八格结构存在而分级缺证（滴天髓列举不及土、候选依'
              '据采之即预决 conflict，均未采）；无根六格。两干×'
              '十二支共 24 格全部定级或显式待定，无空格。本批'
              '后，土根审定层齐备到「登记可消费」的程度：可消费'
              '面是禄位两格与全表的阻断面（待定/未分级格），不是'
              '全表可用；根表完整十二宫逐干位仍属推步（推论'
              '级），不得表述为全表原文列举（承 018-A partial '
              '结论）。',
 'counts': {'stems': 2, 'cells': 24, 'heavy_per_stem_listed': 2,
            'heavy_framework_derived': 0, 'conflicted_pending': 8,
            'structural_present_ungraded': 8, 'light_listed': 0,
            'no_root': 6}}

EARTH_ADJUDICATION_NOTES = [
 'R1 本批边界：只登记分级审定，不写谓词、不接入消费；'
 'bazi_adjudication.py、bazi_action_conditions.py、bazi_strength.py '
 '一字未动，既有七谓词输出逐字不变（全量复跑回归在案）。土根消费'
 '接入另批，接入前置条件见 CONSUMPTION_AUDIT。',
 'R2 体例分歧的形状与金/水不同：金/水只有阴干分歧（阳干两体例合'
 '流、生位两源一致），土则两干皆分歧，且三命本书对分支乙读法有'
 '明确驳斥。分歧更深不改变处置口径：分支并列、不裁定、不以粒度'
 '或论证强度消解任何一方（丁 conflict 先例：分支甲见证更强仍未'
 '裁定）。',
 'R3 禄位独立性：禄（戊巳/己午）有三重干级见证（卷二逐干句、卷'
 '三禄节逐一明列、神峰干级禄表）；三命卷三作「戊寄巳、己寄午」'
 '的寄禄表述（子随母得禄），位置与逐干句一致、性质表述有别——'
 '本批只登记位置定级，寄禄说作注记；禄在滴天髓根列举总述明列为'
 '重根类，定级不因寄禄表述降格。',
 'R4 轻根缺证是实测发现、不是审定疏漏：滴天髓根列举三列对土行'
 '零列举（机检计数 0）；神峰四库的「水土库居辰」是分支乙体例内'
 '的五行级陈述，分支甲宫序的墓位（戌/丑）是单分支宫位名——采任'
 '一作轻级都预决 conflict。八格 structural_present_ungraded 的 '
 'is_heavy 恒 None，消费方不得默认其为轻根或无根。',
 'R5 帝旺全待定：与金/水不同，土无 framework_derived 重根格；'
 '「戊帝旺午 / 己帝旺巳」等表述在 conflict 处置前只能以分支名义'
 '引用（分支甲推步），不得作定级结论（禁用表述见 '
 'DIWANG_DISPOSITION）。',
 'R6 引文原字：戊禄句「己」经 018-A 校勘记 sm2-ji-40135 定读为'
 '巳、「爲」为快照原字，均逐字保留、校定只进 mapped_reading；'
 '论曰土段四处「巳」读己经同批校勘记定读，本批引用该段时以 '
 '018-A 登记的 mapped_reading 为准，不另立校定。',
 'R7 本批不处理：土根消费接入（S2 通道三复核与订正）、藏干根位'
 '资格、四季月 principal、扶抑最小切片审定（S4）、密封 '
 'Phase1/Phase2 注册治理（S5）；丁/辛/癸三长生 conflict 维持原'
 '状（惟己段理据与丁 conflict 的文本关联已在 TU conflict 的 '
 'internal_tensions 登记）。']

EARTH_LIMITATIONS = [
 '土长生 conflict 未裁定：八格待定（戊子/寅/午/申、己子/巳/申/'
 '酉）在裁定或消费方阻断口径之外不得单独使用。',
 '土轻根层整体缺证：八个结构根格（两干各丑/辰/未/戌）未分级；'
 '未来形态若需土轻根面，须先有列举级来源或专项裁定，不得以结'
 '构存在性径行升格。',
 '土重根面极窄：只有禄位两格为已定重根；土日主形态、以土为印的'
 '金线积极面均不能据此宣称根审定齐备。',
 '完整十二宫逐干位（沐浴/冠带/衰/病/绝/胎/养）为推步，本表只在'
 '其中登记根相关位与非根位的定性，不作全表列举表述。',
 '密封 Phase1/Phase2 规则注册仍 pending（本登记的消费接入同既有'
 '披露口径），本批不处理注册；显示白名单不变（研究级）。']
