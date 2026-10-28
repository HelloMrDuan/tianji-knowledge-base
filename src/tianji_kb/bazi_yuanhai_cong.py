"""渊海子平从格专题组一节逐节登记（TJ-012.3 Slice D 就绪度复审排序第一前置：渊海逐节登记·第七组）。

正官组（E0236/E0237）、七杀组（E0282/E0283）、财组（E0284/
E0285）、印组（E0286/E0287）、食伤组（E0288/E0289）与禄刃组
（E0290/E0291）之后续登从格专题组：《弃命从杀论》被七杀组列为
未登记（从杀专题/从格未裁定），本批正面处置整节登记。从财、
从儿、从旺、从强、从势于渊海均无专节（「从旺」「从强」「从儿」
「从势」全书各 0 见），只以未登记清单专条登记散见事实，不跨节
拼凑；滴天髓《从象》章从旺/从强定义（任氏曰，char 96521/96605）
与原注真从定义（char 96219）为不同书不同层，只登记交叉引用、
不混同、不回填。

本批登记范围（机上密封快照实测，快照 SHA256 与登记 Source 一致）：
- 《弃命从杀论》[54055, 54359) 整节登记（304 字，全文窗；
  节题实测为《弃 命 从 杀 论》连读，非《论弃命从杀》；
  四言韵文体专论，节内兼论从财）；
- 滴天髓从象定义 3 条只登记交叉引用，不重复登记。

缺字纪律：本节范围内半角 ? 占位 0 处、PUA 私用区字符 0 处，
本批无新缺字登记、无含缺字段。字形纪律：「命殞」殞字古字
保留、「孤神得失」孤神语义存疑，逐项落账，无见证者不给
mapped_reading。

转手复核（本批核心登记结论）：从格组可操作句逐条标注转手门。
全部经未建层中的至少一门转手：无根事实（根级判定未裁）、
旺衰极端档（从格成立以极弱/势专为前提、极弱档无定义）、
会局（成局判定不存在、合化未裁定）、印比救援、行运阶段、
支关系效力、数量比较与格局成立本身。登记后从杀格、从财格
determination 仍为 None（详见 YUANHAI_CONG_ROUTING_REVIEW）。

特别纪律：从格成立与否是未裁定事项——本批只登记文本与条件
表述，从格 determination 恒 None，不得因登记了条件表述就
暗示可判；本登记不含任何生死/祸福/寿夭/刑伤预测口径——
节内「双目必朽」「脱根寿促」「命殞无猜」等均为原文断语，
按内嵌断语成分登记存在。

本模块是纯数据登记，**零 determination 代码**：不写任何从格
成格/破格判定，不改变 candidates 与既有登记语义；登记不
等于可裁定。引文全部经机上快照切片逐字复核（全文计数==1；
滴天髓交叉引用以其原登记模块为准并经滴天髓快照切片复核）。
Canonical/Phase1 注册状态 pending（与既有研究级登记同口径披露）。
"""


YUANHAI_CONG_ID = 'bazi-yuanhai-cong-registration-v1'

YUANHAI_CONG_TASK = 'TJ-012.3 Slice D prerequisite (yuanhai cong-pattern group registration)'

YUANHAI_SNAPSHOT = {'file': 'yuanhai_ziping.txt',
 'snapshot_path': 'data/quarantine/public_domain_snapshots/daizhigev20/yuanhai_ziping.txt',
 'sha256': 'c8f45d3228fb1958012139139a83edd019e7c2db881998d2d0bba65107417cf9',
 'bytes': 154655,
 'chars': 58905,
 'blob_sha': 'f945a48cbedf5883808a72bb6f544a4dca603cb3'}

YUANHAI_CONG_DITIANSUI_SNAPSHOT = {'file': 'ditiansui_chanwei.txt',
 'snapshot_path': 'data/quarantine/public_domain_snapshots/daizhigev20/ditiansui_chanwei.txt',
 'sha256': '6a875a317c7ba1012285ed12d3bfa5577b50c9fdfd568ece323a12feafe38795',
 'bytes': 368684,
 'chars': 139538,
 'blob_sha': 'ae45f40a8f7de7806e0f9fdf6fd952b8a6148467'}

YUANHAI_CONG_SECTIONS = [{'section_id': 'yuanhai.qiming_congsha',
  'title': '弃命从杀论',
  'source_id': 'bazi.source.yuanhai',
  'locator': {'char_start': 54055, 'char_end': 54359},
  'registration_mode': 'full_section',
  'full_text': '《弃 命 从 杀 论》\n'
               ' 甲乙无根,怕逢申酉;杀合逢之,双目必朽。\n'
               ' 甲木无根,生于丑月;水多转贵,金土则折。\n'
               ' 乙木酉月,见水为奇;有根丑绝,无根寅危。\n'
               ' 乙木坐酉,庚丁透露;二库归根,孤神得失。\n'
               ' 丙火申提,无根从杀;有根南旺,脱根寿促。\n'
               ' 阳火无根,水乡必忌。\n'
               ' 阴火无根,水乡有救。\n'
               ' 阴火酉月,弃命就财;北方入格,南则为灾。\n'
               ' 戊己亥月,身弱为弃;卯月同推,嫌根劫比。\n'
               ' 庚金无根,寅宫火局;南方有贵,须防寿促。\n'
               ' 辛巳阴柔,休囚官杀;运限加金,聪明显达。\n'
               ' 壬日戌提,癸干未月;运喜东方,逢冲则绝。\n'
               ' 弃命从财,须要会财。\n'
               ' 弃命从杀,须要会杀。\n'
               ' 从财忌杀;从杀喜财;命逢根气,命殞无猜。\n'
               ' \n',
  'note': '整节登记（304 字）。节题实测为《弃 命 从 杀 '
          '论》（弃命从杀论连读，非《论弃命从杀》），为渊海全书唯一从格专论节：全书节题扫描含「从」者仅此一节。本节为四言韵文体——十五句四言韵句分日主/月令立论，与前六组散文节体例不同；其为独立命题专论（非附于他节的诗诀/口诀汇编），故整节登记，体例差异如实登记在案（见注记 '
          'R4）。节题虽名从杀，节内兼论从财（阴火就财句、从财总纲句、末句交叉规则）。节前为《四言独步》[51898,54055)，节后为《五言独步》[54359,55002)。节内半角 '
          '? 占位 0 处、PUA 私用区字符 0 处，本批无新缺字登记；字形 2 项逐处落账（命殞殞字、孤神得失孤字）。'}]

YUANHAI_CONG_QUOTES = [{'id': 'yh.cg_jia_yi_rootless',
  'source_id': 'bazi.source.yuanhai',
  'source_section_id': 'yuanhai.qiming_congsha',
  'role': 'operative_candidate',
  'quote': '甲乙无根,怕逢申酉;杀合逢之,双目必朽。',
  'locator': {'char_start': 54068, 'char_end': 54088},
  'operative': True,
  'routed_through_strength': False,
  'note': '甲乙总句：无根为从格前提、申酉为杀在场、杀合为变局因素——三门并陈，不可执行；「双目必朽」为原文刑伤断语，只登记存在、不作裁定（见注记 R7）。',
  'routed_through_other': ['无根事实门（「无根」须先有根级判定：轻根、墓库之根与待定格均未裁定，根级消费契约零接入，逐盘「无根」不能定谳）',
                           '杀合门（「杀合逢之」之合为干合关系，其于从格之效力未裁定）',
                           '格局成立门（以从杀格/从财格成立本身为前提，而从格 determination 不存在）']},
 {'id': 'yh.cg_jia_ugly_month',
  'source_id': 'bazi.source.yuanhai',
  'source_section_id': 'yuanhai.qiming_congsha',
  'role': 'operative_candidate',
  'quote': '甲木无根,生于丑月;水多转贵,金土则折。',
  'locator': {'char_start': 54090, 'char_end': 54110},
  'operative': True,
  'routed_through_strength': False,
  'note': '甲木丑月句：同为无根，水多（印）则转贵、金土（财官）则折——救援与破弃之别全在未裁层；「转贵/则折」为境遇断语，只登记存在。',
  'routed_through_other': ['无根事实门（「无根」须先有根级判定：轻根、墓库之根与待定格均未裁定，根级消费契约零接入，逐盘「无根」不能定谳）',
                           '数量比较门（多寡之比较未阈值化）',
                           '印星救援门（「水多转贵」为印星救援口径，救援构成与效力未裁定）',
                           '格局成立门（以从杀格/从财格成立本身为前提，而从格 determination 不存在）']},
 {'id': 'yh.cg_yi_you_month',
  'source_id': 'bazi.source.yuanhai',
  'source_section_id': 'yuanhai.qiming_congsha',
  'role': 'operative_candidate',
  'quote': '乙木酉月,见水为奇;有根丑绝,无根寅危。',
  'locator': {'char_start': 54112, 'char_end': 54132},
  'operative': True,
  'routed_through_strength': False,
  'note': '乙木酉月句：有根/无根对照为本节根事实门的枢纽句——丑位藏干是否构成「有根」、寅位藏干何以「危」，皆待根级裁定；见水（印）为奇为救援口径。',
  'routed_through_other': ['无根事实门（「无根」须先有根级判定：轻根、墓库之根与待定格均未裁定，根级消费契约零接入，逐盘「无根」不能定谳）',
                           '印星救援门（「见水为奇」为印星救援口径，未裁定）',
                           '格局成立门（以从杀格/从财格成立本身为前提，而从格 determination 不存在）']},
 {'id': 'yh.cg_yi_sitting_you',
  'source_id': 'bazi.source.yuanhai',
  'source_section_id': 'yuanhai.qiming_congsha',
  'role': 'operative_candidate',
  'quote': '乙木坐酉,庚丁透露;二库归根,孤神得失。',
  'locator': {'char_start': 54134, 'char_end': 54154},
  'operative': True,
  'routed_through_strength': False,
  'note': '乙木坐酉句：「二库归根」谓二库藏干成根与否，是根级判定最疑处；「孤神得失」语义存疑（见字形登记 cg-glyph-02），读法未定，本句只登记文本。',
  'routed_through_other': ['无根事实门（「二库归根」：墓库藏干是否成根，为根级判定最疑处、未裁定）',
                           '格局成立门（以从杀格/从财格成立本身为前提，而从格 determination 不存在）'],
  'glyph_refs': ['cg-glyph-02']},
 {'id': 'yh.cg_bing_shen_month',
  'source_id': 'bazi.source.yuanhai',
  'source_section_id': 'yuanhai.qiming_congsha',
  'role': 'operative_candidate',
  'quote': '丙火申提,无根从杀;有根南旺,脱根寿促。',
  'locator': {'char_start': 54156, 'char_end': 54176},
  'operative': True,
  'routed_through_strength': False,
  'note': '丙火申月句：本节题名所系的从杀枢纽句——无根则从、有根南旺则不从，先行条件全在根事实门；「脱根寿促」为寿夭断语，只登记存在、不作裁定（R7）。',
  'routed_through_other': ['无根事实门（「无根」须先有根级判定：轻根、墓库之根与待定格均未裁定，根级消费契约零接入，逐盘「无根」不能定谳）',
                           '格局成立门（以从杀格/从财格成立本身为前提，而从格 determination 不存在）']},
 {'id': 'yh.cg_yang_fire_rootless',
  'source_id': 'bazi.source.yuanhai',
  'source_section_id': 'yuanhai.qiming_congsha',
  'role': 'operative_candidate',
  'quote': '阳火无根,水乡必忌。',
  'locator': {'char_start': 54178, 'char_end': 54188},
  'operative': True,
  'routed_through_strength': False,
  'note': '阳火（丙）句：无根见水乡（杀）必忌——与下句阴火「有救」成阴阳对照对，区分所据原文未言明，只并列登记、不合并读法。',
  'routed_through_other': ['无根事实门（「无根」须先有根级判定：轻根、墓库之根与待定格均未裁定，根级消费契约零接入，逐盘「无根」不能定谳）',
                           '旺衰极端档门（从格以日主极弱、所从之神势专为前提，一般旺衰无极弱档定义、从格成立本身未裁定）',
                           '格局成立门（以从杀格/从财格成立本身为前提，而从格 determination 不存在）']},
 {'id': 'yh.cg_yin_fire_rootless',
  'source_id': 'bazi.source.yuanhai',
  'source_section_id': 'yuanhai.qiming_congsha',
  'role': 'operative_candidate',
  'quote': '阴火无根,水乡有救。',
  'locator': {'char_start': 54190, 'char_end': 54200},
  'operative': True,
  'routed_through_strength': False,
  'note': '阴火（丁）句：同为无根水乡，阴火独言「有救」——救之构成原文未言，与阳火句对照登记（yh.cg_yang_fire_rootless），不强行统一。',
  'routed_through_other': ['无根事实门（「无根」须先有根级判定：轻根、墓库之根与待定格均未裁定，根级消费契约零接入，逐盘「无根」不能定谳）',
                           '印比救援门（「水乡有救」之救为何物，原文未言明、未裁定）',
                           '格局成立门（以从杀格/从财格成立本身为前提，而从格 determination 不存在）']},
 {'id': 'yh.cg_yin_fire_follow_wealth',
  'source_id': 'bazi.source.yuanhai',
  'source_section_id': 'yuanhai.qiming_congsha',
  'role': 'operative_candidate',
  'quote': '阴火酉月,弃命就财;北方入格,南则为灾。',
  'locator': {'char_start': 54202, 'char_end': 54222},
  'operative': True,
  'routed_through_strength': False,
  'note': '阴火酉月句：本节内明言从财之句（弃命就财）——节题虽名从杀论、节内兼论从财，此为内证之一；「入格」以从财格成立为前提；南北灾福为原文断语，只登记存在。',
  'routed_through_other': ['旺衰极端档门（从格以日主极弱、所从之神势专为前提，一般旺衰无极弱档定义、从格成立本身未裁定）',
                           '行运阶段门（「北方入格、南则为灾」之南北为方位行运评价，未建）',
                           '格局成立门（以从杀格/从财格成立本身为前提，而从格 determination 不存在）']},
 {'id': 'yh.cg_wu_ji_hai_month',
  'source_id': 'bazi.source.yuanhai',
  'source_section_id': 'yuanhai.qiming_congsha',
  'role': 'operative_candidate',
  'quote': '戊己亥月,身弱为弃;卯月同推,嫌根劫比。',
  'locator': {'char_start': 54224, 'char_end': 54244},
  'operative': True,
  'routed_through_strength': True,
  'note': '戊己土句：本节唯一明言「身弱」的句子——身弱程度即弃命门槛、程度未阈值化；「卯月同推」的类推范围原文未界定，并列登记。',
  'routed_through_other': ['无根事实门（「无根」须先有根级判定：轻根、墓库之根与待定格均未裁定，根级消费契约零接入，逐盘「无根」不能定谳）',
                           '印比救援门（「嫌根劫比」：根与劫比皆弃格之忌，其口径与根事实门同枢）',
                           '格局成立门（以从杀格/从财格成立本身为前提，而从格 determination 不存在）']},
 {'id': 'yh.cg_geng_rootless',
  'source_id': 'bazi.source.yuanhai',
  'source_section_id': 'yuanhai.qiming_congsha',
  'role': 'operative_candidate',
  'quote': '庚金无根,寅宫火局;南方有贵,须防寿促。',
  'locator': {'char_start': 54246, 'char_end': 54266},
  'operative': True,
  'routed_through_strength': False,
  'note': '庚金句：火局为杀势成局，与会杀总纲（yh.cg_follow_killing_rule）互证在案；「须防寿促」为寿夭断语，只登记存在（R7）。',
  'routed_through_other': ['无根事实门（「无根」须先有根级判定：轻根、墓库之根与待定格均未裁定，根级消费契约零接入，逐盘「无根」不能定谳）',
                           '会局门（「寅宫火局」：寅午戌火局成局判定不存在、合化未裁定）',
                           '行运阶段门（运向与运限阶段评价未建）',
                           '格局成立门（以从杀格/从财格成立本身为前提，而从格 determination 不存在）']},
 {'id': 'yh.cg_xin_si',
  'source_id': 'bazi.source.yuanhai',
  'source_section_id': 'yuanhai.qiming_congsha',
  'role': 'operative_candidate',
  'quote': '辛巳阴柔,休囚官杀;运限加金,聪明显达。',
  'locator': {'char_start': 54268, 'char_end': 54288},
  'operative': True,
  'routed_through_strength': False,
  'note': '辛金句：官杀休囚则不逼身、运限加金则显达——阶段词与运限两门并陈；「聪明显达」为境遇断语，只登记存在。',
  'routed_through_other': ['阶段词门（「休囚官杀」之休囚为旺相休囚死阶段表述，其程度与从格之关系未裁定）',
                           '行运阶段门（运向与运限阶段评价未建）',
                           '格局成立门（以从杀格/从财格成立本身为前提，而从格 determination 不存在）']},
 {'id': 'yh.cg_ren_xu_month',
  'source_id': 'bazi.source.yuanhai',
  'source_section_id': 'yuanhai.qiming_congsha',
  'role': 'operative_candidate',
  'quote': '壬日戌提,癸干未月;运喜东方,逢冲则绝。',
  'locator': {'char_start': 54290, 'char_end': 54310},
  'operative': True,
  'routed_through_strength': False,
  'note': '壬癸句：运向（喜东方）与逢冲两门并陈；「则绝」为断灭断语，只登记存在。',
  'routed_through_other': ['行运阶段门（运向与运限阶段评价未建）',
                           '支关系效力门（「逢冲则绝」：冲在场事实可算，其效力评价不存在）',
                           '格局成立门（以从杀格/从财格成立本身为前提，而从格 determination 不存在）']},
 {'id': 'yh.cg_follow_wealth_rule',
  'source_id': 'bazi.source.yuanhai',
  'source_section_id': 'yuanhai.qiming_congsha',
  'role': 'operative_candidate',
  'quote': '弃命从财,须要会财。',
  'locator': {'char_start': 54312, 'char_end': 54322},
  'operative': True,
  'routed_through_strength': False,
  'note': '从财总纲句：从财成立以财势会局为要件——会局判定不存在，从财格 determination 为 '
          'None；本节从财论述仅此句、阴火就财句（yh.cg_yin_fire_follow_wealth）与末句交叉规则三处，材料薄于从杀（见限制）。',
  'routed_through_other': ['会局门（会财/会杀/成局须三合三会成局判定，成局规则不存在、合化未裁定）',
                           '格局成立门（以从杀格/从财格成立本身为前提，而从格 determination 不存在）']},
 {'id': 'yh.cg_follow_killing_rule',
  'source_id': 'bazi.source.yuanhai',
  'source_section_id': 'yuanhai.qiming_congsha',
  'role': 'operative_candidate',
  'quote': '弃命从杀,须要会杀。',
  'locator': {'char_start': 54324, 'char_end': 54334},
  'operative': True,
  'routed_through_strength': False,
  'note': '从杀总纲句：与从财总纲对句，为本节题名所系；会杀成局判定不存在，从杀格 determination 为 None。',
  'routed_through_other': ['会局门（会财/会杀/成局须三合三会成局判定，成局规则不存在、合化未裁定）',
                           '格局成立门（以从杀格/从财格成立本身为前提，而从格 determination 不存在）']},
 {'id': 'yh.cg_cross_rules_root_negation',
  'source_id': 'bazi.source.yuanhai',
  'source_section_id': 'yuanhai.qiming_congsha',
  'role': 'operative_candidate',
  'quote': '从财忌杀;从杀喜财;命逢根气,命殞无猜。',
  'locator': {'char_start': 54336, 'char_end': 54356},
  'operative': True,
  'routed_through_strength': False,
  'note': '总纲末句：从财/从杀互忌互喜的交叉规则，及「命逢根气」的一票否决——根气有无仍系于根事实门；「命殞」为生死断语，只登记存在、不作裁定（R7；殞字见字形登记 '
          'cg-glyph-01）。',
  'routed_through_other': ['无根事实门（「无根」须先有根级判定：轻根、墓库之根与待定格均未裁定，根级消费契约零接入，逐盘「无根」不能定谳）',
                           '格局成立门（以从杀格/从财格成立本身为前提，而从格 determination 不存在）'],
  'glyph_refs': ['cg-glyph-01']}]

YUANHAI_CONG_CONTEXT_QUOTES = []

YUANHAI_CONG_GAP_REGISTER = []

YUANHAI_CONG_GLYPH_NOTES = [{'id': 'cg-glyph-01',
  'position': 54352,
  'char': '殞',
  'source_section_id': 'yuanhai.qiming_congsha',
  'status': 'archaic_form_preserved',
  'mapped_reading': None,
  'note': '总纲末句「命逢根气,命殞无猜」之「殞」为殁/陨义古字：本句为生死断语用字，逐字保留、不给 '
          'mapped_reading（不径改作陨/殁，以免把断语读法钉死）；断语本身只登记存在、不作裁定（见 yh.cg_cross_rules_root_negation）。'},
 {'id': 'cg-glyph-02',
  'position': 54149,
  'char': '孤',
  'source_section_id': 'yuanhai.qiming_congsha',
  'status': 'semantic_doubt_preserved',
  'mapped_reading': None,
  'note': '乙木坐酉句「二库归根,孤神得失」之「孤神」语义存疑：或指孤辰类神煞、或为孤立之神的泛称，得失读法随之未定；无见证互校，不径改、不给 '
          'mapped_reading，逐字保留并标记存疑（见 yh.cg_yi_sitting_you）。'}]

YUANHAI_CONG_CROSS_REFERENCES = [{'id': 'yh.cg_xref_dt_guli_def',
  'target_module': 'bazi_fire_morphology',
  'target_quote_id': 'dt.guli_def',
  'target_source_id': 'bazi.source.ditiansui-spouse',
  'target_snapshot_file': 'ditiansui_chanwei.txt',
  'target_layer': '原注',
  'locator': {'char_start': 96219, 'char_end': 96250},
  'relation': '滴天髓《从象》章原注真从通述定义（日主孤立无气、无地人元、财官强甚乃为真从）已于 bazi_fire_morphology '
              '登记：此为从格在滴天髓的通述定义、属原注层，与渊海本节分日主韵句是不同书、不同体例、不同层，只登记交叉引用，不混同、不以彼释此。'},
 {'id': 'yh.cg_xref_dt_congwang_def',
  'target_module': 'bazi_fire_morphology',
  'target_quote_id': 'dt.congwang_def',
  'target_source_id': 'bazi.source.ditiansui-spouse',
  'target_snapshot_file': 'ditiansui_chanwei.txt',
  'target_layer': '任氏曰',
  'locator': {'char_start': 96521, 'char_end': 96547},
  'relation': '滴天髓《从象》章任氏曰从旺定义（四柱皆比劫、无官杀之制、有印绶之生、旺之极者）已于 bazi_fire_morphology 登记：渊海全书「从旺」0 '
              '见、无从旺专节，本批不据滴天髓定义回填渊海从旺论述，只登记交叉引用。'},
 {'id': 'yh.cg_xref_dt_congqiang_def',
  'target_module': 'bazi_fire_morphology',
  'target_quote_id': 'dt.congqiang_def',
  'target_source_id': 'bazi.source.ditiansui-spouse',
  'target_snapshot_file': 'ditiansui_chanwei.txt',
  'target_layer': '任氏曰',
  'locator': {'char_start': 96605, 'char_end': 96626},
  'relation': '滴天髓《从象》章任氏曰从强定义（四柱印绶重重、比劫叠叠、日主又当令）已于 bazi_fire_morphology 登记：渊海全书「从强」0 '
              '见、无从强专节，同从旺条口径，只登记交叉引用。'}]

YUANHAI_CONG_UNREGISTERED_RELATED = [{'section_id': 'yuanhai.siyandubu_congcai_verse',
  'title': '《四言独步》末句（弃命从财格）',
  'locator': {'char_start': 54025, 'char_end': 54052},
  'reason': '《四言独步》[51898,54055) '
            '为口诀韵文汇编、整节未登记；其末句「癸巳无根,火土重见;透财名彰,露根则贱。(弃命从财格)」是全书唯一以格名题署「弃命从财格」之处。从财在渊海无专节，只有本节（《弃命从杀论》）内三句与散见诸句的材料形态，本批只登记该散见事实、不摘录拼凑从财格登记。'},
 {'section_id': 'yuanhai.cong_scattered_qieyao',
  'title': '《挈要捷驰玄妙诀》从格散句群',
  'locator': {'char_start': 50890, 'char_end': 50918},
  'reason': '《挈要捷驰玄妙诀》[49751,51000) 为赋诀汇编、未登记；节内从格散句成群：弃命 2 '
            '见（「有弃命就财、就杀、就官者」50896、「身弱弃命要无根」50939）、专旺 1 见（「无依专旺」50915）、从化 1 见（「类属从化」50972）。locator '
            '为其中首句整句 [50890,50918) 作代表；皆赋诀散句、无专节，本批只登记散见事实，不跨节拼凑。'},
 {'section_id': 'yuanhai.conghua_scattered',
  'title': '从化散见诸节（无从化专节）',
  'locator': {'char_start': 39664, 'char_end': 39676},
  'reason': '从化全书 4 '
            '见、无专节：分见《神趣八法》20436（「照返鬼伏属类从化」，女命八法语境）、《论命细法》31854（「我明我暗从化象」，六亲断语）、《五行元理消息赋》39664（「从化得从,显达功名之士」，locator '
            '为此句 [39664,39676) 作代表）、《挈要捷驰玄妙诀》50972，皆散句。从化象成立为用户级待裁定 P-D2（E0270/E0271 '
            '在案，对象为化气/从化象成立判断，与本批文本登记不同层），本批只登记散见事实、不拼凑、不代决。另明示排除：「从革」全书 4 见中 '
            '4175「金曰从革」为五行性情语、44396「从革之金」为描述语，均非从格形态（从革格括注 2 见另见专旺散见条）。'},
 {'section_id': 'yuanhai.zhuanwang_scattered',
  'title': '专旺类散见（无专旺/从旺/从强专节）',
  'locator': {'char_start': 42860, 'char_end': 42878},
  'reason': '专旺类在渊海无专节、无散文论述：「专旺」一词全书 2 '
            '见——《当兴》28377「盖四柱中身主专旺」（散文散见）、《挈要捷驰玄妙诀》50915「无依专旺」（赋句）；专旺类格名（曲直格 2 见、炎上格 2 见、从革格 2 '
            '见、润下格 2 见、稼穡格 1 见）只以《碧渊赋》[42303 起) 韵句括注形态出场，locator 为其中从革格句作代表；「从旺」「从强」「从儿」「从势」全书各 0 '
            '见。滴天髓从旺/从强定义为不同书不同层、只登记交叉引用（见 YUANHAI_CONG_CROSS_REFERENCES），不据以回填渊海专旺论述。'},
 {'section_id': 'yuanhai.wuyandubu_adjacent',
  'title': '《五言独步》（紧邻后节）',
  'locator': {'char_start': 54359, 'char_end': 55002},
  'reason': '本节紧邻后节《五言独步》[54359,55002) '
            '为口诀韵文汇编（建禄生提月等句），非从格专论整节，与《四言独步》同口径未登记；其与本节的关系仅为体例相邻，俟口诀诸节登记批按节处置。'}]

YUANHAI_CONG_ROUTING_REVIEW = {'scope': '《弃命从杀论》中全部引文逐条（15 句全为 operative_candidate；本节无例造、无 doctrine 陈述句）',
 'conclusion_consistent_with_readiness': '从格组可操作句 15 '
                                         '条无一条可直接执行，全部经未建层中的至少一门转手——无根事实门（无根/有根/根气/二库归根：根级判定未裁，轻根、墓库之根与待定格无定谳，根级消费契约零接入）；旺衰极端档门（从格以日主极弱、势专为前提，「身弱为弃」的程度门槛未阈值化，一般旺衰无极弱档定义）；会局门（须要会财、须要会杀、寅宫火局：三合三会成局判定不存在、合化未裁定）；印比救援门（见水为奇、水乡有救、嫌根劫比、水多转贵：救援构成与效力未裁定）；行运阶段门（运喜东方、运限加金、北方入格、南方有贵）；支关系效力门（逢冲则绝、杀合逢之：冲合在场事实可算而效力评价不存在）；数量比较门（水多：未阈值化）；格局成立门（入格与从杀/从财成立本身，以从格 '
                                         'determination 为前提而其不存在）。故登记后从杀格、从财格 determination 仍为 '
                                         'None，与前六组同口径。',
 'comparison_with_prior_groups': '与前六组对照：正官/七杀/财/印/食伤/禄刃诸组的条件多系于格局内部因素，本组枢纽则在格局成立本身与根事实两端——全部十五句或以「无根」为先行条件、或以「入格/从某格」为结论，前置层未建则无一从句可落。本组另一特殊处在材料形态：渊海从格论述为韵文专论一体，滴天髓以散文立从象定义（原注/任氏曰分层）、三命卷六《从象》另有校勘登记在案（E0261，不同书、校勘层），三书三层并存而不互释；且渊海从财材料（本节三句加散见诸句）明显薄于从杀，从财格材料完整性为全组最弱。',
 'non_operative_excluded': '本节无例造（无具体四柱、无人名例），十五句皆为规则形韵句，故 operative '
                           '集合即全节引文集合；句内嵌的断语成分——双目必朽（刑伤）、脱根寿促与须防寿促（寿夭）、命殞无猜（生死）、转贵/显达（境遇）——均为原文断语，只登记存在、不作裁定，不构成任何生死、祸福、寿夭或境遇判断口径（见注记 '
                           'R7）。',
 'determination_consequence': '本批登记后从杀格、从财格 determination 仍为 None：从格成立本身是未裁定事项（用户级待裁定在案者为从化象成立 '
                              'P-D2，对象不同、不混同），成格侧缺从格成立规则、破格侧缺根事实与会局/救援诸层裁定。登记只补齐材料：《弃命从杀论》自此整节在册，从财/从化/专旺诸形态的散见事实在案，无专节形态不拼凑登记。'}

YUANHAI_CONG_NOTES = ['R1 登记≠可裁定：本批为纯证据登记，仓库内不存在任何从杀格/从财格 determination 代码路径；bazi_pattern 的 '
 'candidates、pattern_route、pattern_zaqi、pattern_determination_ren_yin '
 '输出逐字不变。从格成立与否是未裁定事项——本批只登记文本与条件表述，不得因登记了条件表述就暗示可判。',
 'R2 缺字对账：本节范围内半角 ? 共 0 处、PUA 私用区字符 0 处，本批无新缺字登记、无含缺字段（节内十五句全为完整韵句）。全书 ? 共 36 处，正官组已登记 5 处、七杀组 2 '
 '处、财组 3 处、食伤组 1 处、禄刃组 1 处，累计登记 12 处，其余 24 处不在本批范围。',
 'R3 不重复登记：滴天髓从象定义 3 条（原注真从 dt.guli_def、任氏曰从旺 dt.congwang_def、任氏曰从强 '
 'dt.congqiang_def）只登记交叉引用（YUANHAI_CONG_CROSS_REFERENCES），不复制引文、不改变其任何既有编码语义；三命卷六《从象》校勘登记（018-G，E0261）为第三书校勘层存在，在此注记登记其存在，与本批、与滴天髓定义层均不混同。',
 'R4 节题与体例纪律：节题以快照实测为准——《弃 命 从 杀 '
 '论》（弃命从杀论连读），非《论弃命从杀》；七杀组未登记清单所记节名与本批实测一致。本节为四言韵文体，与前六组散文节体例不同；其为独立命题的专论节（有专名节题、专论一题），非附于他节的诗诀/口诀汇编，故整节登记；《四言独步》《五言独步》等口诀汇编节仍按前批口径未登记（见未登记清单）。韵句高度压缩、主语与条件多有省略，读法分歧面大于散文节，登记只及其文本。',
 'R5 '
 '散见纪律：从财、从儿、从旺、从强、从势、从化、专旺于渊海均无专节——从财散见《四言独步》末句与本节内文，从化散见四节，专旺散见二节并《碧渊赋》格名括注一簇，均以未登记清单专条登记散见事实（YUANHAI_CONG_UNREGISTERED_RELATED），不跨节摘录拼凑从格登记，不据滴天髓从旺/从强定义回填渊海。「从革」4 '
 '见已逐处分流：金曰从革（五行性情语）与从革之金（描述语）非从格，从革格括注 2 见属专旺类格名散见。',
 'R6 '
 '从格未裁定纪律（本批特别纪律）：从格成立与否未裁定；本批转手复核逐句标注条件所经未建层（无根事实、旺衰极端档、会局、印比救援、行运阶段、支关系效力、数量比较、格局成立本身），任何引文的登记都不构成该引文可执行或从格可判的暗示；从化象成立（P-D2）为另一对象的用户级待裁定，与本批不混同、本批不代决。',
 'R7 '
 '生死/祸福禁区（内容诚实边界）：本登记不含、也不得被用于由从格推断生死、祸福、寿夭、刑伤或现实境遇的任何字段、评分或口径；节内「双目必朽」「脱根寿促」「须防寿促」「命殞无猜」「南方有贵」等均为原文断语，按 '
 'operative 句的内嵌断语成分登记存在，公开投影与任何场景均不消费本登记作生死、祸福、寿夭、刑伤或境遇判断。',
 'R8 来源普查不变：渊海 Source 仍为既有 101 条之一（C 95 / D 6），本批只扩 review_scope，不新增 Source、不升证据等级；渊海全文仍 '
 'quarantine，本登记只及于所列一节范围。滴天髓交叉引用所指 Source（bazi.source.ditiansui-spouse）亦不变。',
 'R9 Canonical/Phase1 注册 pending：本登记为公开仓证据登记，sealed Phase1/Phase2 正式注册未做（与既有研究级登记同口径披露），不借用 s 编号。']

YUANHAI_CONG_LIMITATIONS = ['从杀格/从财格成格/破格/真假/清浊/用神继续不可裁定：从格成立本身未裁定，成格侧缺成立规则、破格侧经根事实、会局、救援诸层转手而均未裁定。',
 '本节为韵文体：句子高度压缩，主语、条件与适用范围多有省略（如「孤神得失」读法未定、「卯月同推」类推范围未界定），读法分歧面大于散文节；登记只及其文本，不解决读法。',
 '从财在渊海只有本节三句与散见诸句（四言独步末句、挈要散句等），无独立专节材料，从财格材料完整性明显低于从杀；从儿、从势于全书无任何出场（各 0 见），无材料可登记。',
 '字形疑点 2 项未决（「命殞」殞字古字保留、「孤神得失」孤神语义存疑）：均逐字保留、无 mapped_reading，待见证互校另批处理。',
 '本登记不得用于生死、祸福、寿夭、刑伤或现实境遇判断：任何由从格或本登记引文推断生死/祸福/寿夭/刑伤/境遇的用法均在本登记授权范围之外。']
