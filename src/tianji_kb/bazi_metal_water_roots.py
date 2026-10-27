"""TJ-011.2 S1 金/水根分级审定登记（审定+登记批：只登记，不实现）。

本批对象：一般旺衰路线第一片（审源
~/workspace/capability-audit/tj0112-general-strength-scout.md §2.2/§4.1
S1）——为 S2 两条新谓词（pure 生扶形态向金×酉、水×子的成对推广）备齐
唯一缺层：金/水根可用性审定。材料主要取自 TJ-018-A 已登记的《三命
通会》卷二《论天干阴阳生死》逐干铺陈（STEM_COVERAGE 十干禄/生/死
俱全）与神峰卷首干支基础短表群互证；轻根列举取出火线形态审定批已
登记的滴天髓根列举（bazi_fire_morphology 的 dt.root_mu /
dt.root_yuqi_1 / dt.root_yuqi_2，本批以 quote_ref 引用、不重复登记）。

登记内容：
1. 庚/辛/壬/癸四干根表逐干逐支定级（四干×十二支共 48 格全部定级或
   显式待定，无空格）：重根（长生/禄逐干明句、帝旺推步披露）、轻根
   （滴天髓墓/余气列举，全部含冲突标注）、无根、以及随长生 conflict
   分支待定的格位。
2. 辛/癸长生 conflict 分支登记：与丁长生同型的体例冲突（阴阳分判
   vs 五行统摄），按 DING_CHANGSHENG_CONFLICT 同形制并列登记、**不
   裁定**，逐格标明对根分级的实际影响面。
3. 帝旺处置：庚酉/壬子沿火线裁定二口径以推步登记为
   framework_derived（推论级、等级永不混同）；辛/癸帝旺随长生分支
   待定（惟辛酉/癸子已由禄位明句独立定为重根，不受影响）。
4. 与既有木根表（密封政策 reviewed_root_branches）的口径对齐说明，
   以及对 S2 的解锁面/阻断面声明。

本模块是纯数据登记，**零计算逻辑、零函数**：不编写任何新谓词，
不改变既有四谓词（木×卯 pure / 木×酉 isolated / 木×亥 generating /
丙×午 commanding）的任何条件与输出，密封 policy 文件零改动。
凡分级依据，一律在条目内标注等级：per_stem_listed（逐干明句）/
framework_derived（推步）/ light_listed_conflicted（轻根列举含
冲突）/ conflicted_pending（随 conflict 分支待定）/ no_root（无根）。
"""

ROOT_REGISTER_ID = 'bazi-metal-water-root-grading-v1'

ROOT_TASK = 'TJ-011.2'

ROOT_SNAPSHOTS = {
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

# 本批新登记引文（三命卷二逐干铺陈金/水四干禄/生/死句）：018-A 的
# STEM_COVERAGE 已登记其短锚与定位，本批按登记惯例登记整句引文，
# 逐字保留快照原字（「邜」为异体原字；经校勘记者以 mapped_reading
# 与 collation_refs 标注，不回写引文）。定位与整句均经密封快照
# 切片复核（节内计数 ==1，见密封专项）。
ROOT_QUOTES = [
{'id': 'sm.geng_lu',
'source_id': 'bazi.source.sanmingtonghui',
'source_section_id': 'sanming.juan2.tiangan_yinyang_shengsi',
'part_id': 'per_stem_exposition',
'role': 'root_table_evidence',
'quote': '其禄到申',
'locator': {'char_start': 40653, 'char_end': 40657},
'note': '庚段禄句（018-A STEM_COVERAGE 庚 lu 锚）。'},
{'id': 'sm.geng_sheng_frag',
'source_id': 'bazi.source.sanmingtonghui',
'source_section_id': 'sanming.juan2.tiangan_yinyang_shengsi',
'part_id': 'per_stem_exposition',
'role': 'root_table_evidence',
'quote': '长生于己巳中戊土',
'locator': {'char_start': 40671, 'char_end': 40679},
'mapped_reading': '「长生于巳（巳中戊土）」（首字「己」经校勘记 '
                  'sm2-ji-40674 读巳）',
'collation_refs': ['sm2-ji-40674'],
'note': '庚段长生残句：语境为庚长生于巳、托于巳中戊土。'},
{'id': 'sm.geng_shengsi',
'source_id': 'bazi.source.sanmingtonghui',
'source_section_id': 'sanming.juan2.tiangan_yinyang_shengsi',
'part_id': 'per_stem_exposition',
'role': 'root_table_evidence',
'quote': '故庚金生于已而死于子',
'locator': {'char_start': 40750, 'char_end': 40760},
'mapped_reading': '「故庚金生于巳而死于子」（「已」经校勘记 '
                  'sm2-yi-40755 读巳）',
'collation_refs': ['sm2-yi-40755'],
'note': '庚段生死合句：生巳、死子。'},
{'id': 'sm.xin_lu',
'source_id': 'bazi.source.sanmingtonghui',
'source_section_id': 'sanming.juan2.tiangan_yinyang_shengsi',
'part_id': 'per_stem_exposition',
'role': 'root_table_evidence',
'quote': '其禄到酉',
'locator': {'char_start': 40936, 'char_end': 40940},
'note': '辛段禄句（018-A STEM_COVERAGE 辛 lu 锚）。'},
{'id': 'sm.xin_sheng',
'source_id': 'bazi.source.sanmingtonghui',
'source_section_id': 'sanming.juan2.tiangan_yinyang_shengsi',
'part_id': 'per_stem_exposition',
'role': 'conflict_branch_evidence',
'quote': '长生于子子乃坎水',
'locator': {'char_start': 40991, 'char_end': 40999},
'note': '辛段长生句：辛长生于子——XIN_CHANGSHENG_CONFLICT 分支甲'
        '（阴阳分判）的逐干明句。'},
{'id': 'sm.xin_shengsi',
'source_id': 'bazi.source.sanmingtonghui',
'source_section_id': 'sanming.juan2.tiangan_yinyang_shengsi',
'part_id': 'per_stem_exposition',
'role': 'conflict_branch_evidence',
'quote': '故辛金生于子而死于巳',
'locator': {'char_start': 41083, 'char_end': 41093},
'note': '辛段生死合句：生子（分支甲）与死巳同句并见；死巳与分支甲'
        '的阴干逆行宫序自洽，与分支乙（巳为长生）直接冲突，见冲突'
        '登记 internal_tensions。'},
{'id': 'sm.ren_lu',
'source_id': 'bazi.source.sanmingtonghui',
'source_section_id': 'sanming.juan2.tiangan_yinyang_shengsi',
'part_id': 'per_stem_exposition',
'role': 'root_table_evidence',
'quote': '其禄在亥',
'locator': {'char_start': 41235, 'char_end': 41239},
'note': '壬段禄句（018-A STEM_COVERAGE 壬 lu 锚）。'},
{'id': 'sm.ren_shengsi',
'source_id': 'bazi.source.sanmingtonghui',
'source_section_id': 'sanming.juan2.tiangan_yinyang_shengsi',
'part_id': 'per_stem_exposition',
'role': 'root_table_evidence',
'quote': '故壬水生于申而死于卯',
'locator': {'char_start': 41327, 'char_end': 41337},
'note': '壬段生死合句：生申、死卯。'},
{'id': 'sm.gui_lu',
'source_id': 'bazi.source.sanmingtonghui',
'source_section_id': 'sanming.juan2.tiangan_yinyang_shengsi',
'part_id': 'per_stem_exposition',
'role': 'root_table_evidence',
'quote': '其禄在子',
'locator': {'char_start': 41535, 'char_end': 41539},
'note': '癸段禄句（018-A STEM_COVERAGE 癸 lu 锚）。'},
{'id': 'sm.gui_shengsi',
'source_id': 'bazi.source.sanmingtonghui',
'source_section_id': 'sanming.juan2.tiangan_yinyang_shengsi',
'part_id': 'per_stem_exposition',
'role': 'conflict_branch_evidence',
'quote': '故癸水生于邜而死于申',
'locator': {'char_start': 41664, 'char_end': 41674},
'note': '癸段生死合句：「邜」为快照异体原字（即卯），逐字保留。'
        '生卯（分支甲）与死申同句并见；死申与分支甲的阴干逆行宫序'
        '自洽，与分支乙（申为长生）直接冲突，见冲突登记。'}]

# 分级词汇（不得混用、不得升级表述）：
GRADE_VOCABULARY = {
 'per_stem_listed': '逐干明句级：三命卷二逐干铺陈有该干该位的明句'
                    '（长生/禄/死），引文登记在案。重根位（长生/禄）'
                    '用此级。',
 'framework_derived': '推步级：长生位明句＋十二宫次序框架节登记＋'
                      '阴阳顺逆推得，无逐干逐字句（承 018-A '
                      'CORROBORATION_FACTS no-diwang-sentence），属'
                      '推论级。帝旺位（无冲突干）用此级，永不表述为'
                      '明句。',
 'light_listed_conflicted': '轻根列举级（含冲突）：滴天髓根列举（墓列'
                            '/余气列）明列为该行轻根位，但列间或复本'
                            '间有异文冲突（见 '
                            'LIGHT_ROOT_LISTING_CONFLICTS 两型）；只作'
                            'blocker 面（沿 F7 口径：轻根不独立成'
                            '形态）。本批金/水轻根八格全部为此级——无一'
                            '格达火行未那样的干净 light_listed，差异'
                            '如实登记、不粉饰。',
 'conflicted_pending': '待定级：本格定级随未裁定的长生 conflict 分支'
                       '而定（见 XIN_CHANGSHENG_CONFLICT / '
                       'GUI_CHANGSHENG_CONFLICT 的 affected_cells），'
                       '两分支读法并列登记，本批不裁定。',
 'no_root': '无根：该支不藏该行之干（结构事实）且无根列举依据；含'
            '死/绝/病等非根位与推步非根位。推步宫位名（如分支甲以辰'
            '为辛墓）不单独产生根级——轻根只据列举，同火线口径。'}

# 庚根位登记：十二宫序（长生巳明句＋阳干顺行，已由本节生死合句的
# 死子位与总结块复述双重互证）为 巳长生、午沐浴、未冠带、申临官、
# 酉帝旺、戌衰、亥病、子死、丑墓、寅绝、卯胎、辰养。庚无长生冲突。
GENG_ROOT_POSITIONS = [
{'branch': '子', 'grade': 'no_root', 'is_heavy': False,
 'position_kind': '死（非根位）',
 'evidence': [
  {'quote_ref': 'sm.geng_shengsi', 'register': 'self',
   'note': '生死合句明言庚死于子（「已」校定读巳）'},
  {'derivation': '十二宫推步（长生巳顺行）子为死位，与明句一致'}]},
{'branch': '丑', 'grade': 'light_listed_conflicted', 'is_heavy': False,
 'position_kind': '墓/余气（轻根）',
 'conflict_id': 'bazi.concept.conflict_root_type_readings',
 'conflict_subtype': 'dual_listed_mu_yuqi',
 'evidence': [
  {'quote_ref': 'dt.root_mu', 'register': 'bazi_fire_morphology',
   'note': '滴天髓墓列「庚辛逢丑」'},
  {'quote_ref': 'dt.root_yuqi_1', 'register': 'bazi_fire_morphology',
   'note': '余气列复本一亦「庚辛逢丑」——同支兼列墓/余气两列，根类型'
           '读法冲突（与火行戌同型）；根位存在性两列一致'},
  {'quote_ref': 'sf.siku', 'register': 'bazi_sanming_juan2_collation',
   'note': '神峰四库「金库居丑」旁证墓位'}]},
{'branch': '寅', 'grade': 'no_root', 'is_heavy': False,
 'position_kind': '绝（非根位）',
 'evidence': [
  {'quote_ref': 'sf.sijue', 'register': 'bazi_sanming_juan2_collation',
   'note': '神峰四绝「金绝在寅」（五行级）'},
  {'note': '寅不藏金，无任何根列举'}]},
{'branch': '卯', 'grade': 'no_root', 'is_heavy': False,
 'position_kind': '胎（非根位，推步）',
 'evidence': [
  {'derivation': '长生巳顺行推步：卯为胎位；卯不藏金，无根列举'}]},
{'branch': '辰', 'grade': 'no_root', 'is_heavy': False,
 'position_kind': '养（非根位，推步）',
 'evidence': [
  {'derivation': '长生巳顺行推步：辰为养位；辰不藏金。注意辰为水行'
                 '轻根位（壬癸逢辰），行别不同、不得混用'}]},
{'branch': '巳', 'grade': 'per_stem_listed', 'is_heavy': True,
 'position_kind': '长生',
 'evidence': [
  {'quote_ref': 'sm.geng_shengsi', 'register': 'self',
   'note': '生死合句明言庚生于巳（「已」经 sm2-yi-40755 校定读巳）'},
  {'quote_ref': 'sm.geng_sheng_frag', 'register': 'self',
   'note': '「长生于己巳中戊土」（「己」经 sm2-ji-40674 校定读巳）'},
  {'quote_ref': 'sf.sisheng', 'register': 'bazi_sanming_juan2_collation',
   'note': '神峰四生「金生在巳」——五行级与干级于阳干庚一致'},
  {'quote_ref': 'sm2.summary_bracket',
   'register': 'bazi_sanming_juan2_collation',
   'note': '论曰总结块「庚金生巳」复述（总结块庚句字序局部讹乱，引用'
           '只取生位四字并以庚段合句互证——承 018-A 注记）'}]},
{'branch': '午', 'grade': 'no_root', 'is_heavy': False,
 'position_kind': '沐浴（非根位，推步）',
 'evidence': [
  {'derivation': '长生巳顺行推步：午为沐浴位；午不藏金'}]},
{'branch': '未', 'grade': 'no_root', 'is_heavy': False,
 'position_kind': '冠带（非根位，推步）',
 'evidence': [
  {'derivation': '长生巳顺行推步：未为冠带位；未不藏金'}]},
{'branch': '申', 'grade': 'per_stem_listed', 'is_heavy': True,
 'position_kind': '禄/临官',
 'evidence': [
  {'quote_ref': 'sm.geng_lu', 'register': 'self',
   'note': '庚段禄句「其禄到申」'},
  {'quote_ref': 'sf.lubiao', 'register': 'bazi_sanming_juan2_collation',
   'note': '神峰十干禄表「庚禄居申」互证'},
  {'quote_ref': 'sf.siguan', 'register': 'bazi_sanming_juan2_collation',
   'note': '神峰四官「金官在申」互证临官位'},
  {'quote_ref': 'sm2.summary_bracket',
   'register': 'bazi_sanming_juan2_collation',
   'note': '论曰总结块「至申临官归禄庚金得垣」复述'}]},
{'branch': '酉', 'grade': 'framework_derived', 'is_heavy': True,
 'position_kind': '帝旺（推步）',
 'evidence': [
  {'derivation': '庚长生巳（逐干明句，sm.geng_shengsi）＋十二宫次序'
   '（三命卷二《论五行旺相休囚死并寄生十二宫》框架节登记 '
   'sm2.gong_sequence）＋阳干顺行：巳→午（沐浴）→未（冠带）→申'
   '（临官）→酉（帝旺）',
   'note': '推步链每一环都有登记依据，但「庚帝旺在酉」本身无任何逐干'
           '逐字句（018-A no-diwang-sentence）。本位等级恒为 '
           'framework_derived，任何引用不得表述为明句。'}]},
{'branch': '戌', 'grade': 'light_listed_conflicted', 'is_heavy': False,
 'position_kind': '余气（轻根）',
 'conflict_id': 'bazi.concept.conflict_root_type_readings',
 'conflict_subtype': 'yuqi_copies_disagree',
 'evidence': [
  {'quote_ref': 'dt.root_yuqi_2', 'register': 'bazi_fire_morphology',
   'note': '余气列复本二「庚辛逢戌」'},
  {'quote_ref': 'dt.root_yuqi_1', 'register': 'bazi_fire_morphology',
   'note': '复本一金行余气作丑——余气两复本对金行余气支位不一致，'
           '本支仅复本二明列'},
  {'note': '戌藏辛（中气）：金行结构根存在性与复本二列举一致'}]},
{'branch': '亥', 'grade': 'no_root', 'is_heavy': False,
 'position_kind': '病（非根位，推步）',
 'evidence': [
  {'derivation': '长生巳顺行推步：亥为病位；亥不藏金'}]}]

# 辛根位登记：长生位有 conflict（见 XIN_CHANGSHENG_CONFLICT），宫序
# 随分支——分支甲（阴阳分判，长生子、阴干逆行）：子长生、亥沐浴、
# 戌冠带、酉临官、申帝旺、未衰、午病、巳死、辰墓、卯绝、寅胎、丑养；
# 分支乙（五行统摄，同庚宫序）：巳长生、酉帝旺、丑墓、子死。
XIN_ROOT_POSITIONS = [
{'branch': '子', 'grade': 'conflicted_pending', 'is_heavy': None,
 'position_kind': '长生（分支甲）/非根（分支乙）',
 'conflict_id': 'sanming-juan2.xin-changsheng',
 'evidence': [
  {'quote_ref': 'sm.xin_sheng', 'register': 'self',
   'note': '分支甲逐干明句「长生于子子乃坎水」'},
  {'quote_ref': 'sm.xin_shengsi', 'register': 'self',
   'note': '分支甲生死合句「故辛金生于子而死于巳」'},
  {'quote_ref': 'sf.sisheng', 'register': 'bazi_sanming_juan2_collation',
   'note': '分支乙五行级四生作金生在巳；子于分支乙宫序为死位、无根'
           '列举'}]},
{'branch': '丑', 'grade': 'light_listed_conflicted', 'is_heavy': False,
 'position_kind': '墓/余气（轻根）',
 'conflict_id': 'bazi.concept.conflict_root_type_readings',
 'conflict_subtype': 'dual_listed_mu_yuqi',
 'evidence': [
  {'quote_ref': 'dt.root_mu', 'register': 'bazi_fire_morphology',
   'note': '滴天髓墓列「庚辛逢丑」（行级列举，庚辛共用）'},
  {'quote_ref': 'dt.root_yuqi_1', 'register': 'bazi_fire_morphology',
   'note': '余气列复本一亦「庚辛逢丑」——同支两列异读，与火行戌同型'},
  {'quote_ref': 'sf.siku', 'register': 'bazi_sanming_juan2_collation',
   'note': '神峰四库「金库居丑」旁证墓位'},
  {'note': '轻根地位据滴天髓列举，与长生分支无关：两分支宫序对丑的'
           '宫位命名不同（甲作养、乙作墓），均不作根级依据；丑藏辛'
           '（余气）为辛本干结构根'}]},
{'branch': '寅', 'grade': 'no_root', 'is_heavy': False,
 'position_kind': '非根位（宫位名随分支：胎/绝）',
 'evidence': [
  {'note': '寅不藏金，无任何根列举；宫位名两分支不一致，不登记'}]},
{'branch': '卯', 'grade': 'no_root', 'is_heavy': False,
 'position_kind': '非根位（宫位名随分支：绝/胎）',
 'evidence': [
  {'note': '卯不藏金，无任何根列举；宫位名两分支不一致，不登记'}]},
{'branch': '辰', 'grade': 'no_root', 'is_heavy': False,
 'position_kind': '非根位（分支甲宫序作墓，无列举依据）',
 'evidence': [
  {'note': '分支甲推步以辰为墓位，但滴天髓墓列金行作丑、辰不藏金——'
           '推步宫位名不单独产生轻根（轻根只据列举，同火线口径），'
           '故辰不登记为辛之根'}]},
{'branch': '巳', 'grade': 'conflicted_pending', 'is_heavy': None,
 'position_kind': '死（分支甲·逐干明句）/长生（分支乙·五行级）',
 'conflict_id': 'sanming-juan2.xin-changsheng',
 'evidence': [
  {'quote_ref': 'sm.xin_shengsi', 'register': 'self',
   'note': '分支甲：生死合句明言辛死于巳'},
  {'quote_ref': 'sf.sisheng', 'register': 'bazi_sanming_juan2_collation',
   'note': '分支乙：神峰四生「金生在巳」（五行级，庚辛共用）'}]},
{'branch': '午', 'grade': 'no_root', 'is_heavy': False,
 'position_kind': '非根位（宫位名随分支：病/沐浴）',
 'evidence': [
  {'note': '午不藏金，无任何根列举；宫位名两分支不一致，不登记'}]},
{'branch': '未', 'grade': 'no_root', 'is_heavy': False,
 'position_kind': '非根位（宫位名随分支：衰/冠带）',
 'evidence': [
  {'note': '未不藏金，无任何根列举；宫位名两分支不一致，不登记'}]},
{'branch': '申', 'grade': 'conflicted_pending', 'is_heavy': None,
 'position_kind': '帝旺（分支甲·推步）/非根（分支乙）',
 'conflict_id': 'sanming-juan2.xin-changsheng',
 'evidence': [
  {'derivation': '分支甲：辛长生子（逐干明句）＋阴干逆行：子→亥'
   '（沐浴）→戌（冠带）→酉（临官）→申（帝旺）',
   'note': '分支甲宫序内推步级'},
  {'note': '分支乙：申为金行临官（庚禄位，五行级），无辛逐干陈述；'
           '申藏庚（辛之同行阳干），结构存在性为行级'}]},
{'branch': '酉', 'grade': 'per_stem_listed', 'is_heavy': True,
 'position_kind': '禄/临官',
 'evidence': [
  {'quote_ref': 'sm.xin_lu', 'register': 'self',
   'note': '辛段禄句「其禄到酉」'},
  {'quote_ref': 'sf.lubiao', 'register': 'bazi_sanming_juan2_collation',
   'note': '神峰十干禄表「辛禄居酉」互证'},
  {'note': '酉在两分支下均为重根位（分支甲为临官本位、分支乙为帝旺'
           '位），重根定级不随长生分支'}]},
{'branch': '戌', 'grade': 'light_listed_conflicted', 'is_heavy': False,
 'position_kind': '余气（轻根）',
 'conflict_id': 'bazi.concept.conflict_root_type_readings',
 'conflict_subtype': 'yuqi_copies_disagree',
 'evidence': [
  {'quote_ref': 'dt.root_yuqi_2', 'register': 'bazi_fire_morphology',
   'note': '余气列复本二「庚辛逢戌」'},
  {'quote_ref': 'dt.root_yuqi_1', 'register': 'bazi_fire_morphology',
   'note': '复本一金行余气作丑——两复本对金行余气支位不一致'},
  {'note': '戌藏辛（中气）为辛本干结构根，与复本二列举一致；分支甲'
           '宫序作冠带，不作根级依据'}]},
{'branch': '亥', 'grade': 'no_root', 'is_heavy': False,
 'position_kind': '非根位（宫位名随分支：沐浴/病）',
 'evidence': [
  {'note': '亥不藏金，无任何根列举；宫位名两分支不一致，不登记'}]}]

# 壬根位登记：十二宫序（长生申明句＋阳干顺行，死卯明句与总结块复述
# 互证）为 申长生、酉沐浴、戌冠带、亥临官、子帝旺、丑衰、寅病、
# 卯死、辰墓、巳绝、午胎、未养。壬无长生冲突。
REN_ROOT_POSITIONS = [
{'branch': '子', 'grade': 'framework_derived', 'is_heavy': True,
 'position_kind': '帝旺（推步）',
 'evidence': [
  {'derivation': '壬长生申（逐干明句，sm.ren_shengsi）＋十二宫次序'
   '（框架节登记 sm2.gong_sequence）＋阳干顺行：申→酉（沐浴）→戌'
   '（冠带）→亥（临官）→子（帝旺）',
   'note': '「壬帝旺在子」本身无逐干逐字句（018-A '
           'no-diwang-sentence），等级恒为 framework_derived。'}]},
{'branch': '丑', 'grade': 'light_listed_conflicted', 'is_heavy': False,
 'position_kind': '余气（轻根）',
 'conflict_id': 'bazi.concept.conflict_root_type_readings',
 'conflict_subtype': 'yuqi_copies_disagree',
 'evidence': [
  {'quote_ref': 'dt.root_yuqi_2', 'register': 'bazi_fire_morphology',
   'note': '余气列复本二「壬癸逢丑」'},
  {'quote_ref': 'dt.root_yuqi_1', 'register': 'bazi_fire_morphology',
   'note': '复本一水行余气作辰——两复本对水行余气支位不一致'},
  {'note': '丑藏癸（中气）：水行结构根（癸为壬同行阴干）'}]},
{'branch': '寅', 'grade': 'no_root', 'is_heavy': False,
 'position_kind': '病（非根位，推步）',
 'evidence': [
  {'derivation': '长生申顺行推步：寅为病位；寅不藏水'}]},
{'branch': '卯', 'grade': 'no_root', 'is_heavy': False,
 'position_kind': '死（非根位）',
 'evidence': [
  {'quote_ref': 'sm.ren_shengsi', 'register': 'self',
   'note': '生死合句明言壬死于卯'}]},
{'branch': '辰', 'grade': 'light_listed_conflicted', 'is_heavy': False,
 'position_kind': '墓/余气（轻根）',
 'conflict_id': 'bazi.concept.conflict_root_type_readings',
 'conflict_subtype': 'dual_listed_mu_yuqi',
 'evidence': [
  {'quote_ref': 'dt.root_mu', 'register': 'bazi_fire_morphology',
   'note': '滴天髓墓列「壬癸辰」（脱「逢」字，快照原样保留）'},
  {'quote_ref': 'dt.root_yuqi_1', 'register': 'bazi_fire_morphology',
   'note': '余气列复本一「壬癸逢辰」——同支两列异读，与火行戌同型'},
  {'quote_ref': 'sf.siku', 'register': 'bazi_sanming_juan2_collation',
   'note': '神峰四库「水土库居辰」旁证墓位'},
  {'note': '辰藏癸（余气）：水行结构根（辰不藏壬本身——行级列举适用'
           '于壬，同火线丙×戌的行级口径先例）'}]},
{'branch': '巳', 'grade': 'no_root', 'is_heavy': False,
 'position_kind': '绝（非根位）',
 'evidence': [
  {'quote_ref': 'sf.sijue', 'register': 'bazi_sanming_juan2_collation',
   'note': '神峰四绝「水土绝在巳」（五行级）'}]},
{'branch': '午', 'grade': 'no_root', 'is_heavy': False,
 'position_kind': '胎（非根位，推步）',
 'evidence': [
  {'derivation': '长生申顺行推步：午为胎位；午不藏水'}]},
{'branch': '未', 'grade': 'no_root', 'is_heavy': False,
 'position_kind': '养（非根位，推步）',
 'evidence': [
  {'derivation': '长生申顺行推步：未为养位；未不藏水'}]},
{'branch': '申', 'grade': 'per_stem_listed', 'is_heavy': True,
 'position_kind': '长生',
 'evidence': [
  {'quote_ref': 'sm.ren_shengsi', 'register': 'self',
   'note': '生死合句明言壬生于申'},
  {'quote_ref': 'sf.sisheng', 'register': 'bazi_sanming_juan2_collation',
   'note': '神峰四生「水土长生居申」——五行级与干级于阳干壬一致'},
  {'quote_ref': 'sm2.summary_bracket',
   'register': 'bazi_sanming_juan2_collation',
   'note': '论曰总结块「壬水生申」复述'}]},
{'branch': '酉', 'grade': 'no_root', 'is_heavy': False,
 'position_kind': '沐浴（非根位，推步）',
 'evidence': [
  {'derivation': '长生申顺行推步：酉为沐浴位；酉不藏水'}]},
{'branch': '戌', 'grade': 'no_root', 'is_heavy': False,
 'position_kind': '冠带（非根位，推步）',
 'evidence': [
  {'derivation': '长生申顺行推步：戌为冠带位；戌不藏水'}]},
{'branch': '亥', 'grade': 'per_stem_listed', 'is_heavy': True,
 'position_kind': '禄/临官',
 'evidence': [
  {'quote_ref': 'sm.ren_lu', 'register': 'self',
   'note': '壬段禄句「其禄在亥」'},
  {'quote_ref': 'sf.lubiao', 'register': 'bazi_sanming_juan2_collation',
   'note': '神峰十干禄表「壬禄居亥」互证'},
  {'quote_ref': 'sf.siguan', 'register': 'bazi_sanming_juan2_collation',
   'note': '神峰四官「水土临官在亥」互证临官位'},
  {'quote_ref': 'sm2.summary_bracket',
   'register': 'bazi_sanming_juan2_collation',
   'note': '论曰总结块「至亥临官归禄壬水得垣」复述'}]}]

# 癸根位登记：长生位有 conflict（见 GUI_CHANGSHENG_CONFLICT）——
# 分支甲（阴阳分判，长生卯、阴干逆行）：卯长生、寅沐浴、丑冠带、
# 子临官、亥帝旺、戌衰、酉病、申死、未墓、午绝、巳胎、辰养；
# 分支乙（五行统摄，同壬宫序）：申长生、亥临官、子帝旺、辰墓、卯死。
GUI_ROOT_POSITIONS = [
{'branch': '子', 'grade': 'per_stem_listed', 'is_heavy': True,
 'position_kind': '禄/临官',
 'evidence': [
  {'quote_ref': 'sm.gui_lu', 'register': 'self',
   'note': '癸段禄句「其禄在子」'},
  {'quote_ref': 'sf.lubiao', 'register': 'bazi_sanming_juan2_collation',
   'note': '神峰十干禄表「癸禄居子」互证'},
  {'note': '子在两分支下均为重根位（分支甲为临官本位、分支乙为帝旺'
           '位），重根定级不随长生分支'}]},
{'branch': '丑', 'grade': 'light_listed_conflicted', 'is_heavy': False,
 'position_kind': '余气（轻根）',
 'conflict_id': 'bazi.concept.conflict_root_type_readings',
 'conflict_subtype': 'yuqi_copies_disagree',
 'evidence': [
  {'quote_ref': 'dt.root_yuqi_2', 'register': 'bazi_fire_morphology',
   'note': '余气列复本二「壬癸逢丑」'},
  {'quote_ref': 'dt.root_yuqi_1', 'register': 'bazi_fire_morphology',
   'note': '复本一水行余气作辰——两复本对水行余气支位不一致'},
  {'note': '丑藏癸（中气）为癸本干结构根，与复本二列举一致；分支甲'
           '宫序作冠带，不作根级依据'}]},
{'branch': '寅', 'grade': 'no_root', 'is_heavy': False,
 'position_kind': '非根位（宫位名随分支：沐浴/病）',
 'evidence': [
  {'note': '寅不藏水，无任何根列举；宫位名两分支不一致，不登记'}]},
{'branch': '卯', 'grade': 'conflicted_pending', 'is_heavy': None,
 'position_kind': '长生（分支甲·逐干明句）/死（分支乙宫序）',
 'conflict_id': 'sanming-juan2.gui-changsheng',
 'evidence': [
  {'quote_ref': 'sm.gui_shengsi', 'register': 'self',
   'note': '分支甲逐干明句「故癸水生于邜而死于申」（邜为快照异体）'},
  {'note': '分支乙：水行宫序卯为死位（壬死卯明句即此宫序），无癸根'
           '列举'}]},
{'branch': '辰', 'grade': 'light_listed_conflicted', 'is_heavy': False,
 'position_kind': '墓/余气（轻根）',
 'conflict_id': 'bazi.concept.conflict_root_type_readings',
 'conflict_subtype': 'dual_listed_mu_yuqi',
 'evidence': [
  {'quote_ref': 'dt.root_mu', 'register': 'bazi_fire_morphology',
   'note': '滴天髓墓列「壬癸辰」（脱「逢」字，快照原样保留）'},
  {'quote_ref': 'dt.root_yuqi_1', 'register': 'bazi_fire_morphology',
   'note': '余气列复本一「壬癸逢辰」——同支两列异读'},
  {'quote_ref': 'sf.siku', 'register': 'bazi_sanming_juan2_collation',
   'note': '神峰四库「水土库居辰」旁证墓位'},
  {'note': '辰藏癸（余气）为癸本干结构根，与列举一致'}]},
{'branch': '巳', 'grade': 'no_root', 'is_heavy': False,
 'position_kind': '非根位（宫位名随分支：胎/绝）',
 'evidence': [
  {'quote_ref': 'sf.sijue', 'register': 'bazi_sanming_juan2_collation',
   'note': '神峰四绝「水土绝在巳」（五行级，与分支乙宫序合）；巳不藏'
           '水，无根列举'}]},
{'branch': '午', 'grade': 'no_root', 'is_heavy': False,
 'position_kind': '非根位（宫位名随分支：绝/胎）',
 'evidence': [
  {'note': '午不藏水，无任何根列举；宫位名两分支不一致，不登记'}]},
{'branch': '未', 'grade': 'no_root', 'is_heavy': False,
 'position_kind': '非根位（分支甲宫序作墓，无列举依据）',
 'evidence': [
  {'note': '分支甲推步以未为墓位，但滴天髓墓列水行作辰、未不藏水——'
           '推步宫位名不单独产生轻根（同辛×辰口径），故未不登记为'
           '癸之根'}]},
{'branch': '申', 'grade': 'conflicted_pending', 'is_heavy': None,
 'position_kind': '死（分支甲·逐干明句）/长生（分支乙·五行级）',
 'conflict_id': 'sanming-juan2.gui-changsheng',
 'evidence': [
  {'quote_ref': 'sm.gui_shengsi', 'register': 'self',
   'note': '分支甲：生死合句明言癸死于申'},
  {'quote_ref': 'sf.sisheng', 'register': 'bazi_sanming_juan2_collation',
   'note': '分支乙：神峰四生「水土长生居申」（五行级，壬癸共用）'}]},
{'branch': '酉', 'grade': 'no_root', 'is_heavy': False,
 'position_kind': '非根位（宫位名随分支：病/沐浴）',
 'evidence': [
  {'note': '酉不藏水，无任何根列举；宫位名两分支不一致，不登记'}]},
{'branch': '戌', 'grade': 'no_root', 'is_heavy': False,
 'position_kind': '非根位（宫位名随分支：衰/冠带）',
 'evidence': [
  {'note': '戌不藏水，无任何根列举；宫位名两分支不一致，不登记'}]},
{'branch': '亥', 'grade': 'conflicted_pending', 'is_heavy': None,
 'position_kind': '帝旺（分支甲·推步）/非根（分支乙）',
 'conflict_id': 'sanming-juan2.gui-changsheng',
 'evidence': [
  {'derivation': '分支甲：癸长生卯（逐干明句）＋阴干逆行：卯→寅'
   '（沐浴）→丑（冠带）→子（临官）→亥（帝旺）',
   'note': '分支甲宫序内推步级'},
  {'note': '分支乙：亥为水行临官（壬禄位，五行级），无癸逐干陈述；'
           '亥藏壬（癸之同行阳干），结构存在性为行级'}]}]

METAL_WATER_ROOT_TABLES = {
 '庚': GENG_ROOT_POSITIONS,
 '辛': XIN_ROOT_POSITIONS,
 '壬': REN_ROOT_POSITIONS,
 '癸': GUI_ROOT_POSITIONS}

HEAVY_ROOT_BRANCHES = {
 '庚': ['巳', '申', '酉'],
 '辛': ['酉'],
 '壬': ['申', '亥', '子'],
 '癸': ['子']}

PENDING_ROOT_BRANCHES = {
 '庚': [],
 '辛': ['子', '巳', '申'],
 '壬': [],
 '癸': ['卯', '申', '亥']}

LIGHT_ROOT_BRANCHES = {
 '庚': ['丑', '戌'],
 '辛': ['丑', '戌'],
 '壬': ['丑', '辰'],
 '癸': ['丑', '辰']}

# 辛长生 conflict 登记（与 018-A DING_CHANGSHENG_CONFLICT 同形制：
# 两说并列、各自来源定位、不裁定）。体例同型：阴阳分判（阴干自有
# 长生位）与五行统摄（同行共用长生、四大长生体例）之争；庚为阳干，
# 两体例于庚合流（生巳两源一致），冲突只落在阴干辛。
XIN_CHANGSHENG_CONFLICT = {
 'conflict_id': 'sanming-juan2.xin-changsheng',
 'subject': '辛金长生位',
 'status': 'conflict',
 'adjudication': None,
 'research_only': True,
 'genre_note': '与丁长生 conflict（sanming-juan2.ding-changsheng）'
               '同型：阴阳分判与五行统摄两种体例之争。神峰四生为'
               '五行级表、非干级陈述；三命逐干铺陈为干级自述。',
 'branches': [
  {'branch_id': 'xin-sheng-zi',
   'reading': '子',
   'system': '阴阳分判（阴干自有长生位）',
   'evidence': [
    {'quote_ref': 'sm.xin_sheng', 'source_id': 'bazi.source.sanmingtonghui',
     'register': 'self',
     'note': '三命本节辛段「长生于子子乃坎水」'},
    {'quote_ref': 'sm.xin_shengsi',
     'source_id': 'bazi.source.sanmingtonghui', 'register': 'self',
     'note': '三命本节辛段「故辛金生于子而死于巳」——生子与死巳同属'
             '阴干逆行宫序，自洽'}]},
  {'branch_id': 'xin-sheng-si',
   'reading': '巳',
   'system': '五行统摄（庚辛共用金之长生，四大长生体例）',
   'evidence': [
    {'quote_ref': 'sf.sisheng', 'source_id': 'bazi.source.shenfeng',
     'register': 'bazi_sanming_juan2_collation',
     'note': '神峰五行级四生「金生在巳」——五行级陈述，庚辛共用，'
             '非干级'},
    {'quote_ref': 'sm2.sida_archive',
     'source_id': 'bazi.source.sanmingtonghui',
     'register': 'bazi_sanming_juan2_collation',
     'note': '三命本节论辩段通论「古人只有四大长生之説」为同源体例'
             '背景（存档，非证据）'}]}],
 'affected_cells': [
  {'branch': '子', 'under_branch_a': '长生（重根，逐干明句）',
   'under_branch_b': '非根（金行宫序死位）'},
  {'branch': '巳', 'under_branch_a': '死（非根，逐干明句）',
   'under_branch_b': '长生（重根，五行级）'},
  {'branch': '申', 'under_branch_a': '帝旺（重根，分支内推步）',
   'under_branch_b': '非根（金行临官为庚禄位，无辛逐干陈述）'}],
 'internal_tensions': [
  '分支乙若作干级适用，与三命辛段逐干明句「死于巳」直接冲突（巳不能'
  '同时为长生与死位）——此为分支乙的粒度限制（五行级表不得径作干级'
  '读）。登记口径是两体例并列，本批不以粒度消解任何一方、不裁定。',
  '分支乙宫序下金行临官在申，与三命辛禄酉（神峰干级禄表亦作酉）不'
  '一致；禄位有逐干明句与干级禄表双证，不受本冲突影响。'],
 'unaffected': [
  '辛禄酉：逐干明句＋神峰干级禄表双证，且在两分支下均为重根位'
  '（甲作临官本位、乙作帝旺位），定级不随分支',
  '金行轻根丑/戌：据滴天髓列举，与长生分支无关'],
 'statement': '两说并列登记、不裁定；任何后续引用必须指名分支。辛根'
              '表中子/巳/申三格标 conflicted_pending；S2 实现对辛根'
              '位于此三支的情形须作冲突阻断（同戌根异文冲突的阻断'
              '口径），不得取任一分支单独建模。丁长生 conflict 的'
              '处置（用户裁定级流派取舍）与本冲突相互独立，本批均'
              '不碰结论。'}

# 癸长生 conflict 登记（同形制）。壬为阳干，两体例于壬合流（生申
# 两源一致），冲突只落在阴干癸。
GUI_CHANGSHENG_CONFLICT = {
 'conflict_id': 'sanming-juan2.gui-changsheng',
 'subject': '癸水长生位',
 'status': 'conflict',
 'adjudication': None,
 'research_only': True,
 'genre_note': '与丁长生、辛长生 conflict 同型：阴阳分判与五行统摄'
               '两种体例之争。神峰四生「水土长生居申」为五行级表'
               '（水土共用一语，体例色彩尤显），非干级陈述。',
 'branches': [
  {'branch_id': 'gui-sheng-mao',
   'reading': '卯',
   'system': '阴阳分判（阴干自有长生位）',
   'evidence': [
    {'quote_ref': 'sm.gui_shengsi',
     'source_id': 'bazi.source.sanmingtonghui', 'register': 'self',
     'note': '三命本节癸段「故癸水生于邜而死于申」——生卯与死申同属'
             '阴干逆行宫序，自洽（邜为快照异体，即卯）'}]},
  {'branch_id': 'gui-sheng-shen',
   'reading': '申',
   'system': '五行统摄（壬癸共用水之长生，四大长生体例）',
   'evidence': [
    {'quote_ref': 'sf.sisheng', 'source_id': 'bazi.source.shenfeng',
     'register': 'bazi_sanming_juan2_collation',
     'note': '神峰五行级四生「水土长生居申」——五行级陈述，壬癸'
             '共用，非干级'},
    {'quote_ref': 'sm2.sida_archive',
     'source_id': 'bazi.source.sanmingtonghui',
     'register': 'bazi_sanming_juan2_collation',
     'note': '三命本节论辩段通论「古人只有四大长生之説」为同源体例'
             '背景（存档，非证据）'}]}],
 'affected_cells': [
  {'branch': '卯', 'under_branch_a': '长生（重根，逐干明句）',
   'under_branch_b': '非根（水行宫序死位）'},
  {'branch': '申', 'under_branch_a': '死（非根，逐干明句）',
   'under_branch_b': '长生（重根，五行级）'},
  {'branch': '亥', 'under_branch_a': '帝旺（重根，分支内推步）',
   'under_branch_b': '非根（水行临官为壬禄位，无癸逐干陈述）'}],
 'internal_tensions': [
  '分支乙若作干级适用，与三命癸段逐干明句「死于申」直接冲突（申不能'
  '同时为长生与死位）——粒度限制同辛冲突登记口径，两体例并列、不'
  '裁定。',
  '分支乙宫序下水行临官在亥，与三命癸禄子（神峰干级禄表亦作子）不'
  '一致；禄位双证、不受本冲突影响。'],
 'unaffected': [
  '癸禄子：逐干明句＋神峰干级禄表双证，且在两分支下均为重根位'
  '（甲作临官本位、乙作帝旺位），定级不随分支',
  '水行轻根辰/丑：据滴天髓列举，与长生分支无关'],
 'statement': '两说并列登记、不裁定；任何后续引用必须指名分支。癸根'
              '表中卯/申/亥三格标 conflicted_pending；S2 实现对癸根'
              '位于此三支的情形须作冲突阻断，不得取任一分支单独'
              '建模。'}

# 帝旺缺位处置（沿火线裁定二口径，本批结论汇总）。
DIWANG_DISPOSITION = {
 'question': '金/水帝旺位无逐干逐字句（承 018-A no-diwang-sentence），'
             'S2 所需帝旺根位如何处置',
 'verdict': 'framework_derivation_for_uncontested_stems_'
            'branch_pending_for_conflicted_stems',
 'statement': '庚帝旺酉、壬帝旺子：其长生位有逐干明句且无冲突，以'
              '十二宫推步登记为 framework_derived（推论级），与长生/禄'
              '的 per_stem_listed 分级并列、永不混同（沿火线裁定二）。'
              '辛/癸帝旺位随长生分支而定（辛：甲作申、乙作酉；癸：甲'
              '作亥、乙作子），登记为 conflicted_pending——惟辛酉、'
              '癸子二格已由禄位明句独立定为重根，帝旺分支之争不改变'
              '该二格定级，只影响申（辛）/亥（癸）两格。',
 'derived_positions': [
  {'stem': '庚', 'branch': '酉',
   'derivation': '庚长生巳（逐干明句）＋十二宫次序＋阳干顺行：巳→午'
                 '→未→申（临官）→酉（帝旺）'},
  {'stem': '壬', 'branch': '子',
   'derivation': '壬长生申（逐干明句）＋十二宫次序＋阳干顺行：申→酉'
                 '→戌→亥（临官）→子（帝旺）'}],
 'forbidden_phrasings': ['庚帝旺在酉（原文）', '三命明言庚旺于酉',
                         '壬帝旺在子（原文）', '三命明言壬旺于子',
                         '辛帝旺在申（原文）', '癸帝旺在亥（原文）'],
 'assessment_ref': 'bazi_sanming_juan2_collation.ROOT_TABLE_ASSESSMENT'
                   '（verdict=partial，derived_positions 含帝旺）＋ '
                   'bazi_fire_morphology.DIWANG_DISPOSITION（火线代偿'
                   '审定先例）'}

# 轻根列举冲突总登记：金/水轻根全部出自滴天髓根列举（墓列＋余气列
# 两复本），冲突呈两型。与既有已注册 conflict
# bazi.concept.conflict_root_type_readings 同一现象（s026/s041 区），
# 本批只作格位级标注，不新立 conflict 实体。
LIGHT_ROOT_LISTING_CONFLICTS = {
 'conflict_id': 'bazi.concept.conflict_root_type_readings',
 'statement': '金/水轻根八格无一是无争议的干净明列（与火行未「两复本'
              '一致」不同——此差异如实登记）。冲突两型如下；四格（每行'
              '两格）均标 light_listed_conflicted，只作 blocker 面'
              '（F7 口径）。',
 'subtypes': [
  {'subtype': 'dual_listed_mu_yuqi',
   'description': '同支兼见于墓列与余气列复本一（与火行戌同型）：根'
                  '的类型读法（墓 vs 余气）未裁定，根位存在性两列'
                  '一致。',
   'cells': ['庚×丑', '辛×丑', '壬×辰', '癸×辰']},
  {'subtype': 'yuqi_copies_disagree',
   'description': '余气两复本对该行余气支位取舍不一致：复本一作丑'
                  '（金）/辰（水），复本二作戌（金）/丑（水）；后者仅'
                  '复本二明列，复本一以他支当之。',
   'cells': ['庚×戌', '辛×戌', '壬×丑', '癸×丑']}],
 'disposition': 'S2 消费时，携 type_source_conflict 的根按既有机制'
                '阻断裁决（同火线戌根口径）；轻根不独立成形态。'}

# 与既有木根表（密封政策）的口径对齐说明。本批零 policy 改动：
# policy_files_changed 恒为空集，密封测试另行断言登记模块不引用、
# 不修改任何密封政策路径。
WOOD_TABLE_ALIGNMENT = {
 'reference': '密封政策 bazi.concept.action_effects_v1.'
              'reviewed_root_branches（木：[亥，寅，卯]，水：[亥，子]，'
              '金：[酉]——后两集为月份本气根位集）；公开登记 '
              'bazi_fire_morphology.BING_ROOT_POSITIONS（丙根表）',
 'statement': '口径对齐三点：(1) 分级形状同构：重根恒为长生/禄/帝旺'
              '三位（木集亥=长生、寅=禄、卯=帝旺，与本表庚 {巳，申，'
              '酉}、壬 {申，亥，子} 同构）；轻根恒为墓/余气列举位、只'
              '作 blocker（F7），本表同此；根分重/轻的总述锚同为滴天'
              '髓根列举总述（dt.root_heavy_light）。(2) 对象不同、不'
              '互相冒充：密封政策的水 [亥，子]/金 [酉] 是既审的月份'
              '本气根位集（供 principal 与月根事实），本表是逐干全支'
              '根表——本批不改动密封政策、不以本表冒充政策已审；S2 '
              '拟沿 commanding 形态的 register-based 先例以本登记表'
              '驱动根有效性，密封 Phase1/Phase2 注册 pending 另行'
              '披露（同既有口径）。(3) 粒度差异如实登记：木集为行级'
              '三位，乙（阴干木）长生位于午的逐干陈述从未进入已审木'
              '集；本表对辛/癸采取逐干登记＋冲突分支并列，是更细的'
              '粒度——此差异不反推木集有误，木集维持密封政策既审'
              '状态、本批不复核。',
 'policy_files_changed': []}

# 对 S2 的影响面声明（本批结论边界）。
S2_IMPACT = {
 'unlocked': [
  '金×酉 pure 推广的月根事实：酉为庚帝旺（推步重根）与辛禄（明句'
  '重根），两干均不随长生分支——S2 月根条件所需根位审定已齐备',
  '水×子 pure 推广的月根事实：子为壬帝旺（推步重根）与癸禄（明句'
  '重根），同上不随分支',
  '庚/壬两干全表定级、辛/癸禄位与轻根位定级完成：S2「显干各有已审'
  '根」「日根全 effective」类条件获得逐干根表依据'],
 'still_blocked': [
  '辛根位于子/巳/申、癸根位于卯/申/亥：定级随长生 conflict 分支，'
  'S2 须作冲突阻断（abstain），不得单分支建模',
  '中和档不可建、弱档无新面（审源 §2.1/§2.3 结论）：不因本批改变',
  '扶抑仍双重受阻（以一般旺衰为输入＋方向表量词无阈值）：本批不'
  '解锁扶抑、TJ-013.2 裁决规则与真 TJ-017.2'],
 'statement': '本批只完成审定层登记：不写任何谓词代码、不改变既有四'
              '谓词的任何条件与输出。S2 实现批另行领取，须以真实命盘'
              '四类 Golden（正强/正弱侧对照/未知/冲突）复证。'}

# 根表可推性评估（本批验收项，承 018-A ROOT_TABLE_ASSESSMENT 的
# partial 结论在本批范围内的细化）。
ROOT_TABLE_ASSESSMENT_S1 = {
 'verdict': 'graded_with_registered_conflicts',
 'statement': '庚/壬两干根表定级齐备（重根三位：长生/禄逐干明句＋帝旺'
              '推步披露；轻根两位列举含冲突标注）；辛/癸两干禄位明句'
              '定级、轻根列举定级，长生与帝旺共六格随 conflict 分支'
              '待定（逐格登记、影响面明示）。四干×十二支共 48 格全部'
              '定级或显式待定，无空格。四干禄位均有三命逐干句＋神峰'
              '干级禄表双证。本批后，金/水根可用性审定层齐备到 S2 '
              '可消费的程度（待定六格以阻断口径消费）；根表完整十二'
              '宫逐干位仍属推步（推论级），不得表述为全表原文列举'
              '（承 018-A partial 结论）。',
 'counts': {'stems': 4, 'cells': 48, 'heavy_per_stem_listed': 6,
            'heavy_framework_derived': 2, 'conflicted_pending': 6,
            'light_listed_conflicted': 8, 'no_root': 26}}

ROOT_ADJUDICATION_NOTES = [
 'R1 本批边界：只登记分级审定，不写谓词；bazi_adjudication.py、'
 'bazi_action_conditions.py、bazi_strength.py 一字未动，既有四谓词'
 '输出逐字不变（全量复跑回归在案）。S2 实现另批。',
 'R2 等级纪律：帝旺位（庚酉/壬子）等级 framework_derived 在登记、'
 '文档、后续实现的每一处引用中都必须随行标注；把推步表述为逐干'
 '明句即证据冒充（禁用表述见 DIWANG_DISPOSITION）。',
 'R3 冲突纪律：辛/癸长生 conflict 与丁长生同型同处置——分支并列、'
 '不裁定、不以粒度或内部张力消解任何一方；受影响格标 '
 'conflicted_pending，S2 以阻断口径消费。丁线本身不在本批范围'
 '（DING_BLOCK 维持）。',
 'R4 轻根纪律：金/水轻根八格全部含冲突标注（两型见 '
 'LIGHT_ROOT_LISTING_CONFLICTS），只作 blocker（F7）；推步宫位名'
 '不单独产生轻根（辛×辰、癸×未两格为此口径的显式实例）。',
 'R5 行级列举的适用：滴天髓墓/余气列举为干对行级（庚辛/壬癸），'
 '按火线丙×戌先例适用于同行两干；逐干明句位（长生/禄）则逐干'
 '分立，两口径在登记中逐格可辨。',
 'R6 引文原字：三命快照「邜」为异体、「已/己」形讹经 018-A 校勘记'
 '定读者以 mapped_reading 标注、引文逐字保留原字，不静默订正。',
 'R7 本批不处理：F3/F4 火线剩余形态、扶抑登记（S3）、密封 '
 'Phase1/Phase2 注册（S5）；本登记不扩大格局线可消费的旺衰范围。']

ROOT_LIMITATIONS = [
 '辛/癸根表各有三格待定（长生 conflict 未裁定）：辛×子/巳/申、'
 '癸×卯/申/亥在裁定或 S2 阻断口径之外不得单独使用。',
 '金/水轻根无一格为干净明列：八格全部 light_listed_conflicted，'
 'S2 消费时一律携冲突阻断语义。',
 '帝旺位（庚酉/壬子）为推步级：其在 S2 形态中的功能承担方式（是否'
 '需本气关系并行承担，如火线午例）属 S2 实现批审定事项，本批只'
 '登记分级。',
 '完整十二宫逐干位（沐浴/冠带/衰/病/绝/胎/养）为推步，本表只在其'
 '中登记根相关位与非根位的定性，不作全表列举表述。',
 '密封 Phase1/Phase2 规则注册仍 pending（S2 实现的 '
 'evidence_binding 同既有披露口径），本批不处理注册；显示白名单'
 '不变（研究级）。']

# ---------------------------------------------------------------------
# TJ-011.2 S2 形态登记（实现批追加）：pure 生扶形态向金×酉、水×子的
# 成对推广。条件集与木线 pure scope 逐条同构（八条件），差异只在：
# (a) 日主/月门以本登记与仓内声明月集为准（密封政策 pure_months 与
# 木专属可用性 Variant 不可自公开代码扩展，沿 PURE_GENERATING_MONTHS
# 与 commanding 的 register-based 先例）；(b) 根有效性以本模块根表
# 分级驱动（重根格可用、conflicted_pending 与 light_listed_conflicted
# 一律阻断），不消费密封木专属可用性。定义锚同木线：从旺定义
# （s047，任氏曰）与从强定义（s048）均为五行通述、不点名金/水，
# 金/水分支在定义层与木分支同标准，无需专属定义段。
FORM_PURE_SUPPORT_METAL = {
 'form_id': 'metal-you-pure-support-v1',
 'name_cn': '金日主酉月纯生扶形态',
 'status': 'adjudicated_isomorphic_extension',
 'task': 'TJ-011.2',
 'school': '任氏（滴天髓阐微）分支，与既有谓词同一 Source '
           '（bazi.source.ditiansui-spouse）',
 'day_masters': ['庚', '辛'],
 'month_branch': '酉',
 'classification_if_matched': 'strong',
 'never_yields': ['weak'],
 'predicate_name': 'pure_support_metal',
 'definition_anchors': {
  'primary': ['dt.congwang_def'],
  'co_anchor': ['dt.congqiang_def', 'dt.congqiang_no_caiguan'],
  'anchoring_rationale': '两定义均为五行通述（从旺：四柱皆比劫、无官'
                         '杀之制、有印绶之生；从强：绝无一毫财星官杀'
                         '之气），不点名任何日主五行；金分支与木分支'
                         '在定义层同标准（沿 F1 对火线的同型结论）。'},
 'conditions': [
  {'key': 'metal_day_master',
   'statement': '日主五行金（庚或辛）。根分级逐干查本登记根表'
                '（庚、辛表分立，辛表三格随长生 conflict 待定）。',
   'anchor_type': 'scope_construction',
   'anchors': ['FORM scope', 'METAL_WATER_ROOT_TABLES']},
  {'key': 'reviewed_same_element_month_you',
   'statement': '月支为酉，本气（辛）已经审，principal 关系为 '
                'same_element（同类当令）。酉在 principal 已审支集'
                '内；月根事实：庚以帝旺居酉（推步级 framework_'
                'derived）、辛以禄居酉（逐干明句级），两干均为重根'
                '且不随辛长生分支（见 S2_IMPACT）。逐盘锚点等级由'
                '裁决层以 month_root_grade 随条件输出。',
   'anchor_type': 'original_text',
   'anchors': ['dt.congqiang_def（日主又当令）',
               'commander 层 principal 关系已审事实（酉本气辛）',
               'HEAVY_ROOT_BRANCHES（庚酉/辛酉）']},
  {'key': 'all_positions_support_only',
   'statement': '全位置（年、月、日、时四柱的显干与藏干）对日主的关'
                '系全部属于生扶类（generates_me 印 / same_element '
                '比劫）；任一位置为克泄耗类即否决。与木线 pure '
                'scope 同名条件共用同一已执行事实。',
   'anchor_type': 'original_text',
   'anchors': ['dt.congwang_def（四柱皆比劫，无官杀之制，有印绶之生）',
               'dt.congqiang_no_caiguan（绝无一毫财星官杀之气）']},
  {'key': 'visible印_present',
   'statement': '显干（年、月、时）中至少一干为印（generates_me，'
                '对金日主为土干）。与木线同名条件共用同一事实。',
   'anchor_type': 'original_text',
   'anchors': ['dt.congwang_def（有印绶之生）']},
  {'key': 'visible比_present',
   'statement': '显干中至少一干为比劫（same_element，金干）。日干本'
                '身不计（既有架构：日干是参照，不作独立显干）。与木'
                '线同名条件共用同一事实。',
   'anchor_type': 'original_text',
   'anchors': ['dt.congwang_def（四柱皆比劫）']},
  {'key': 'effective_day_roots_registered',
   'statement': '日主有结构根，且全部结构根按本登记根表（按日主干'
                '查表）均为可用重根：根位格级为 per_stem_listed 或 '
                'framework_derived，且根事实本身无根类型来源冲突、无'
                '未解支作用触及。conflicted_pending 六格与 light_'
                'listed_conflicted 八格的根一律不可用（阻断）。密封'
                '可用性 Variant 为木专属，本条件不消费之，沿 '
                'commanding 的 register-based 先例。逐盘根级由裁决'
                '层以 root_grades 随条件输出。',
   'anchor_type': 'original_text',
   'anchors': ['dt.root_heavy_light（长生禄旺，根之重者也）',
               'METAL_WATER_ROOT_TABLES（逐格 grade）',
               'LIGHT_ROOT_LISTING_CONFLICTS / 两长生 conflict 登记'
               '（阻断面）']},
  {'key': 'all_visible_have_registered_roots',
   'statement': '每个显干至少有一个已登记/已审根位：金、水干查本登'
                '记根表（grade 非 no_root 且非 conflicted_pending '
                '的格位，含轻根位——沿 BING_ALL_ROOT_BRANCHES 含轻'
                '根位的先例）；其余五行查密封政策 reviewed_root_'
                'branches。土干在密封政策与本登记中均无已审根位集'
                '（土根零登记），故土显干在本条件恒不合——此为本形'
                '态与木线（印为水，水有已审集）的登记面差异，如实'
                '登记、不以结构事实冒充已审（见 satisfiability 的'
                '通道三）。',
   'anchor_type': 'scope_construction',
   'anchors': ['既有 pure scope 同名条件先例',
               'METAL_WATER_ROOT_TABLES',
               '密封政策 bazi.concept.action_effects_v1.'
               'reviewed_root_branches']},
  {'key': 'no_unresolved_interactions',
   'statement': '无未解干支作用类型（干合/六合/六冲/六害/三合按既有'
                '口径）：任一未解作用在盘即弃判，与既有四谓词同口'
                '径。与木线同名条件共用同一事实。',
   'anchor_type': 'scope_construction',
   'anchors': ['密封政策 unresolved_interactions 口径']}]}

# 金×酉形态的真实命盘可满足性：构造性不可满足（证明在案，非检索
# 不力）。S2 实现批逐项验算后登记（审源 §5 预登记的回改条款）：
# 审源 §2.2 的「构成可满足」是形态级论证（藏干构成与条件集的逻辑
# 检验），其「酉/丑/戌/辰等支可构造」一句未逐盘验算——逐盘验算结
# 果是丑（癸水泄）、戌（丁火克）、辰（乙木财/癸水泄）的藏干均含非
# 生扶，本证明通道一即以此订正该句。
METAL_YOU_SATISFIABILITY = {
 'status': 'chart_unrealizable',
 'scope_of_claim': '在本形态登记的八条件（与木线 pure 全位置同构）'
                   '下，任何真实历法命盘均不能使八条件全真。本登记'
                   '不否定从旺/从强定义对金日主的原则适用性，只登记'
                   '该条件集在干支历法组合上的不可满足性。',
 'proof_channels': [
  {'channel': '藏干层唯一支',
   'argument': '生扶藏干集合对金日主为 {土，金}。十二支中藏干全落 '
               '{土，金} 者只有酉（单藏辛）：丑藏癸（水，对金为泄）、'
               '戌藏丁（火，克）、辰藏乙（木，财）与癸、巳藏丙（火）、'
               '申藏壬（水，泄）、亥藏甲（木，财）、午藏丁、未藏丁/'
               '乙、寅藏甲/丙、卯藏乙、子藏癸，均含非生扶。故 '
               'all_positions_support_only 为真要求四柱支全为酉。'},
  {'channel': '全酉盘的显干干对',
   'argument': '支全酉时，年干只能是酉年之干 {己，辛，癸，丁，乙}，'
               '酉月月干由五虎遁定：己年→癸、辛年→丁、癸年→辛、丁'
               '年→己、乙年→乙。五组（年干，月干）中每组至少一干对'
               '金为非生扶（癸/乙为泄/财，丁为克），visible 层 '
               'all_positions_support_only 恒假；且日主只能是辛（庚'
               '酉日柱不存在——干支阴阳配伍），辛日酉时干为丁（五'
               '鼠遁丙辛日起戊，酉时丁），时干再独立否决一次。'},
  {'channel': '土印显干根位登记缺口（独立通道）',
   'argument': '金日主之印为土干。土在密封政策 reviewed_root_'
               'branches 无条目、本登记亦无土根表（土根零登记，审源'
               '§2.2），故 all_visible_have_registered_roots 对任何'
               '含土显干的命盘恒假；而 visible印_present 要求显干有'
               '印（土）——两条件在现行登记面下不可兼得。此通道是登'
               '记/政策缺口而非历法事实：若将来土根位经审定登记，本'
               '通道须复核（通道一、二为历法构造性事实，不因此'
               '改变）。'}],
 'factor_layer_note': '本形态的 scope 评估逻辑由因子层测试覆盖（合成'
                      '因子输入，标注 factor-level，沿 commanding 批'
                      'FactorLayerTests 先例）：因子层基线八条件可全'
                      '真，证明评估逻辑本身无恒假键；真实命盘层按上'
                      '述证明登记 unrealizable。',
 'scout_correction': '审源 tj0112-general-strength-scout.md §2.2 金×酉'
                     '行「构成可满足性 ✓」经本批逐盘验算订正为不可满'
                     '足（其 §5 未核实清单已预登记此回改条款）；订正'
                     '只及该格结论，不及定义锚与根审定结论。'}

FORM_PURE_GENERATING_WATER = {
 'form_id': 'water-zi-pure-generating-v1',
 'name_cn': '水日主子月纯生扶形态',
 'status': 'adjudicated_isomorphic_extension',
 'task': 'TJ-011.2',
 'school': '任氏（滴天髓阐微）分支，与既有谓词同一 Source '
           '（bazi.source.ditiansui-spouse）',
 'day_masters': ['壬', '癸'],
 'month_branch': '子',
 'classification_if_matched': 'strong',
 'never_yields': ['weak'],
 'predicate_name': 'pure_generating_support_water',
 'predicate_name_note': '命名从 S2 任务书 pure_generating 型：与既有 '
                        'pure_generating_support 同以仓内声明月集＋登记'
                        '表驱动根有效性＋r026 出口的实现形制。须明示：'
                        '子月本气癸与水日主为 same_element 关系，本形'
                        '态的月门事实与 pure 型（同类月）同构，不存在'
                        'generates_me 的月关系，不得以名称暗示月令生'
                        '日主。',
 'definition_anchors': {
  'primary': ['dt.congwang_def'],
  'co_anchor': ['dt.congqiang_def', 'dt.congqiang_no_caiguan'],
  'anchoring_rationale': '同金属形态：两定义五行通述、不点名日主；水'
                         '分支与木分支在定义层同标准。'},
 'conditions': [
  {'key': 'water_day_master',
   'statement': '日主五行水（壬或癸）。根分级逐干查本登记根表（壬、'
                '癸表分立，癸表三格随长生 conflict 待定）。',
   'anchor_type': 'scope_construction',
   'anchors': ['FORM scope', 'METAL_WATER_ROOT_TABLES']},
  {'key': 'reviewed_same_element_month_zi',
   'statement': '月支为子，本气（癸）已经审，principal 关系为 '
                'same_element（同类当令）。子在 principal 已审支集'
                '内；月根事实：壬以帝旺居子（推步级 framework_'
                'derived）、癸以禄居子（逐干明句级），两干均为重根'
                '且不随癸长生分支。逐盘锚点等级由裁决层以 month_'
                'root_grade 随条件输出。',
   'anchor_type': 'original_text',
   'anchors': ['dt.congqiang_def（日主又当令）',
               'commander 层 principal 关系已审事实（子本气癸）',
               'HEAVY_ROOT_BRANCHES（壬子/癸子）']},
  {'key': 'all_positions_support_only',
   'statement': '全位置（显干与藏干）对日主的关系全部属于生扶类；任'
                '一位置为克泄耗类即否决。与木线 pure scope 同名条件'
                '共用同一已执行事实。',
   'anchor_type': 'original_text',
   'anchors': ['dt.congwang_def（四柱皆比劫，无官杀之制，有印绶之生）',
               'dt.congqiang_no_caiguan（绝无一毫财星官杀之气）']},
  {'key': 'visible印_present',
   'statement': '显干中至少一干为印（generates_me，对水日主为金'
                '干）。与木线同名条件共用同一事实。',
   'anchor_type': 'original_text',
   'anchors': ['dt.congwang_def（有印绶之生）']},
  {'key': 'visible比_present',
   'statement': '显干中至少一干为比劫（same_element，水干）。日干本'
                '身不计。与木线同名条件共用同一事实。',
   'anchor_type': 'original_text',
   'anchors': ['dt.congwang_def（四柱皆比劫）']},
  {'key': 'effective_day_roots_registered',
   'statement': '日主有结构根，且全部结构根按本登记根表（按日主干查'
                '表）均为可用重根（per_stem_listed 或 framework_'
                'derived 格级，且根事实无根类型来源冲突、无未解支作'
                '用触及）。conflicted_pending 六格与 light_listed_'
                'conflicted 八格的根一律阻断。密封可用性 Variant 为'
                '木专属，本条件不消费之（register-based 先例）。逐'
                '盘根级由裁决层以 root_grades 随条件输出。',
   'anchor_type': 'original_text',
   'anchors': ['dt.root_heavy_light（长生禄旺，根之重者也）',
               'METAL_WATER_ROOT_TABLES（逐格 grade）',
               'LIGHT_ROOT_LISTING_CONFLICTS / 两长生 conflict 登记'
               '（阻断面）']},
  {'key': 'all_visible_have_registered_roots',
   'statement': '每个显干至少有一个已登记/已审根位：金、水干查本登'
                '记根表（grade 非 no_root 且非 conflicted_pending '
                '的格位，含轻根位）；其余五行查密封政策 reviewed_'
                'root_branches。本形态的必备显干（印金、比水）均有本'
                '登记根表覆盖，与金属形态的土面缺口不同。',
   'anchor_type': 'scope_construction',
   'anchors': ['既有 pure scope 同名条件先例',
               'METAL_WATER_ROOT_TABLES',
               '密封政策 bazi.concept.action_effects_v1.'
               'reviewed_root_branches']},
  {'key': 'no_unresolved_interactions',
   'statement': '无未解干支作用类型（既有口径），任一未解作用在盘即'
                '弃判。与木线同名条件共用同一事实。',
   'anchor_type': 'scope_construction',
   'anchors': ['密封政策 unresolved_interactions 口径']}]}

# 水×子形态的可满足性：癸可满足（见证在案）；壬单独不可满足（显干
# 比劫通道的构造性证明），两结论分立登记，不得混述为「水线已全
# 建」或「水线不可建」。
WATER_ZI_SATISFIABILITY = {
 'status': 'satisfiable_for_gui_only',
 'witness_gui': {'birth': '1981-12-21T00:30:00+08:00',
                 'pillars': ['辛酉', '庚子', '癸酉', '壬子'],
                 'note': '辛酉年子月：年干辛（印）、月干庚（印）、时'
                         '干壬（比）皆生扶；四支子/酉藏干全落 {水，'
                         '金}；癸根于子（禄，逐干明句重根）两见、无冲'
                         '突无作用触及；无未解作用。八条件全真（逐项'
                         '推导见 S2 Golden）。'},
 'ren_unrealizable': {
  'status': 'chart_unrealizable',
  'scope_of_claim': '壬日主在本形态八条件下无真实命盘可全真；癸不受'
                    '此限。',
  'proof_channels': [
   {'channel': '藏干层支集',
    'argument': '生扶藏干集合对水日主为 {水，金}；藏干全落此集的支只'
                '有子（单藏癸）与酉（单藏辛）：丑藏己（土，克）、辰藏'
                '戊（土，克）、申藏戊、亥藏甲（木，泄）、戌藏戊/丁、'
                '未藏己/乙、寅藏甲/丙、卯藏乙、巳藏丙、午藏丁均含非生'
                '扶。故四柱支只能子/酉，日支只能子（壬酉日柱不存在'
                '——干支阴阳配伍），日柱必为壬子。'},
   {'channel': '显干比劫与显干根位不可兼得',
    'argument': '支全子/酉后逐位穷举比劫（水显干）的来源。月干为壬须'
                '年干属丁壬族：丁为火（对水克），年干自身已破 visible '
                '层生扶；年干壬则年柱只能是壬子（壬的合法柱中支落 '
                '{子，酉} 者仅壬子，壬酉干支阴阳不配不存在），五虎遁'
                '定其子月干为壬、日柱壬子，时干在子/酉上唯庚/己：己'
                '为土（克）破生扶，庚虽为印，但在四支皆子的盘中无任'
                '何根位（无一支藏金；能藏金的申/巳/丑/戌均因藏克泄耗'
                '被支集通道排除，年/日酉柱对壬不存在、时酉干己为'
                '克），故 all_visible_have_registered_roots 恒假。年'
                '干癸时子月干为甲（泄），月干非比且破生扶。时干为水'
                '须时支寅（壬）/卯（癸），藏干含甲/丙、乙，已被支集'
                '通道排除。故壬盘中 visible比_present 与其余条件不可'
                '兼得——1921-12-15 辛酉年庚子月壬子日庚子时一盘即'
                '比劫无源面的见证：其余七条件全真、只 visible比 一条'
                '假（见 S2 Golden 近失例）。'}],
  'factor_layer_note': '壬的 scope 评估逻辑由因子层基线覆盖（八条件可'
                       '全真），真实命盘层按上述证明登记 '
                       'unrealizable。'}}

S2_FORM_REGISTERS = {
 'pure_support_metal': FORM_PURE_SUPPORT_METAL,
 'pure_generating_support_water': FORM_PURE_GENERATING_WATER}

S2_ANCHOR_TYPES = {
 predicate: {c['key']: c['anchor_type'] for c in form['conditions']}
 for predicate, form in S2_FORM_REGISTERS.items()}

S2_LIMITATIONS = [
 '金×酉形态（pure_support_metal）真实命盘构造性不可满足（藏干唯一'
 '支＋全酉显干干对＋土印根位登记缺口三通道，证明见 METAL_YOU_'
 'SATISFIABILITY），谓词按登记条件集如实实现、因子层验证评估逻辑，'
 '不因不可满足而删改条件或放宽口径。',
 '水×子形态（pure_generating_support_water）仅癸日主有真实见证；壬'
 '日主因显干比劫与显干根位不可兼得通道构造性不可满足（见 WATER_ZI_'
 'SATISFIABILITY），不得表述为壬癸均已可判。',
 '两形态的根有效性以 S1 登记表驱动（register-based，沿 commanding '
 '先例），不消费密封木专属可用性 Variant；辛/癸长生 conflict 与轻根'
 '列举冲突均未裁定，受影响根一律阻断。']
