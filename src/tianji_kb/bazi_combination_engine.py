"""原局 / 大运 / 流年组合引擎（TJ-0424，B3/B4 已批准）。

只消费已有的可执行输出，不产生新规则、新裁定：

- 原局结构：调用方传入的四柱（与 ``bazi_core.chart_from_pillars`` 的
  结构形态一致）；
- 大运干支及十神：调用方传入的 ``candidate_sequence`` 行
  （``bazi-dayun-month-sequence-research-v1``）；
- 流年干支及十神：本模块按六十甲子表由目标年份推导（与
  ``bazi-annual-lichun-boundary-v1`` 核对年干支的同一公式
  ``CYCLE[(year - 4) % 60]``；立春交界、年内分界不在此推导范围）；
- 干支关系：下文转录的已审关系表——与
  ``bazi_core.stem_five_combination`` /
  ``bazi_core.reviewed_branch_pair_relations`` /
  ``bazi_core.branch_relations`` 所消费的同一 canonical 表一致
  （``data/canonical/bazi/foundations_v1.json`` 的
  ``stem_combinations`` 与 ``earthly_branch_relations``），
  密封环境下的专项测试逐项核对转录与 canonical 表一致，漂移即失败。
  本模块不 import ``bazi_core``（它依赖历法 provider 与密封数据），
  只依赖纯常量模块 ``foundations``，因此在公开检出也可执行；
  关系表本身是通用传统配对事实，不含密封文本引文。
- 强弱 / 喜用：调用方传入的 ``factors()``、``tiaohou_lookup()``、
  ``bingyao_lookup()``、格局候选输出，本模块只原样转述并校验其
  variant 与 release 旗标，不重算、不合并。

输出明确区分三层，缺一不可：

1. 结构关系层（``structural_relations``）：大运×原局、流年×原局、
   大运×流年的干支关系列表，只报结构事实，不推效力。
2. 条件判断层：每条关系附触发条件与前提（已满足 / 未满足 /
   无法判定），引用所消费的已审规则 ID。
3. 效力层（``effects``）：只写有依据的效力；本模块无任何已审跨层
   效力规则可用（TJ-017.2 与 TJ-023.3 均阻塞），故无依据的效力一律
   abstain 并写明理由，绝不把缺少依据的效力判断写成已经完成。

第二批（TJ-0425，P0-4 岁运组合引擎扩展，B3/B4）：

- 格局：直接消费格局引擎 v2（``bazi-pattern-engine-v2``）的
  ``evaluate_all`` 输出——每格状态、条件事实证据、Variant 信息、
  D-1 成立证据原样转述；``broken`` 只经伤官见官一途输出，按契约
  验收后单列破格登记（破格依据与原成立身份随记录携带），永不计入
  成立；其余只具名破格缺口。
- 旺衰：直接消费旺衰引擎（``bazi-strength-engine-v1``）的
  ``assess_strength`` 输出——古典分类、现代评分/分项、Q5/Q6
  不确定性标记、从格候选屏、分歧解释原样转述；不确定性传导，
  不在组合层洗成确定结论。
- 喜用：直接消费喜用引擎（``bazi-xiyong-engine-v1``）的
  ``evaluate_xiyong`` 输出——四体系与流年喜用年度契约（6 项已
  实现对照）原样转述，取代旧的 4 项契约；待批 5 项保持 pending。
  未传入喜用引擎输出时，仍用旧的四体系契约（向后兼容）。
- 关系补齐：三对关系完整枚举；大运×流年对内仅两支、无可形成
  之组，另以 ``dayun_x_flow_x_natal`` scope 枚举跨三层之组
  （须同时含大运支与流年支者，只记未被两对 scope 覆盖之组）。
- 效力层：有规则依据的，改为带依据的条件结论（``status`` 为
  ``conditional``，``verdict`` 为存在性/模型口径事实标签，绝非
  吉凶或效力断言）；无依据的保持 abstain 并具名缺口。条件结论
  只有四种：流年/大运干与已成立格局之格神同十神、与扶抑现代候
  选干同字、与原局调候序列同字、Q3-A 模型口径（冲/害/六合在原
  局现代模型内只记录、score_adjustment 恒为 0）。

第三批（P0-4 岁运组合效力判断扩展）：

- 条件结论扩至八种：新增病药三角色（已触发病药对的主体/病/药
  之神类，``bazi.phase2.bingyao_assessment`` 已登记，《神峰通考》
  定义节示例二、三两对）与格局候选格神（候选格之格神同十神，
  只认 validated 候选规则、只认十神格名）；四种新增结论一律只
  陈述存在性事实——药在场不等于病已去（medicine_effect_status
  恒未裁定），病在场不等于害已成，候选恒不等于成立。
- 结构层补齐：地支关系行补齐五行方向事实（地支本气转录表，
  密封交叉核对）；天干行补 ``same_stem``、地支行补
  ``same_branch``；``scope_coverage`` 每对补齐已审关系命中/未
  命中对数（已审三表互不重叠，每对至多一行）。
- 仍不动（待裁定 C2–C6，见 LIMITATIONS）：Q3-A 跨层口径（C2）
  与扶抑现代规则待批（C3，E2 不升级为已批结论）；C 盘大运方向
  forward 只是明示假设（C4）；跨三层 scope 保留与否（C5）；合
  化弃判传导（C6）。本批不消费喜用/格局两路的新增输出——工作区
  内两路第三批改动尚未落地，可消费的仍是第二批已稳定的契约
  （喜用 v1、格局 v2、旺衰 v1）。

2026-11-25 14:41 第二轮 33 问全部裁定，第三批限制解除：

- C2 已批：冲/害/六合作为跨层结构条件结论（Q3-A 口径），只作
  结构条件结论，不直接推导实际效力；跨层效力本身仍未裁定。
- C3/X1 已批：``fuyi-modern-rules-v1`` 为已批研究模型，E2 条件
  结论（与扶抑现代候选干同字）为已批研究模型结论，仍只记存在
  性事实，不作古典扶抑断言；喜用路模型对象的状态字段更新由喜
  用路负责，本引擎只消费其 candidate_stems 输出。
- C4 已批：forward 可作为明确指定的研究算例参数；实际排盘须
  用已裁定的大运方向规则，不得把未知角色默认成顺行，也不得混
  淆日干与方向规则规定的年干输入；本引擎不推导方向，只消费调
  用方提供的 sequence 行。
- C5 已批：``dayun_x_flow_x_natal`` 三层组合 scope 保留；证据去
  重——跨层组与两对 scope 的组无重叠，组关系本身不产生条件结论。
- C6 已批：弃判传导——现代旺衰弃判时，依赖该结果的效力分支弃
  判；本引擎的 Q3-A 模型口径结论只在现代层实际评分时发出
  （components 非空），现代弃判时不发；独立的调候、病药、格局
  结论不受影响。
- C1 待喜用路：格局 pin 由 v1 升 v2 由喜用路负责；接通后移除
  ``pattern=None`` 的临时限制，接通前须验证输入结构、版本、字
  段语义与兼容性。
- C1 已接通（2026-11-25）：喜用路 pin 已升 v2，``pattern=None``
  临时限制已移除；本地已验证输入结构（顶层三子变体 +
  strength_overall + counts + earth_gate；逐格 variant / 日主 /
  月支 / 治理旗标 / broken_gaps）、版本（v2 接受、v1 拒收）、字
  段语义（有资格门控与 combine() 一致，useful_god 恒 None，
  annual 清单不变）与兼容性（pattern=None 仍可用）；机上实时
  接通（真实 chart → evaluate_all → evaluate_xiyong → combine）
  待验证。

喜用神综合分析契约（``xiyong``）：扶抑、调候、病药、格局用神四体系
并列输出，各体系原样消费现有输出，不新造判断；
``unified_verdict`` 恒为 None（TJ-013.2 裁决 A：并列呈现、统一裁决
拒判）。流年喜用部分只完成数据契约与规则调用结构，完整推演待对应
规则获批后接入，契约中显式标注已实现段与待批段。

恒 research_only=True、public_enabled=False、ai_enabled=False；
任何输入漂移或缺失一律 fail-closed（ValueError），不静默补全。
"""

import copy

from .foundations import BRANCHES, CYCLE, GENERATES, CONTROLS, STEMS, ganzhi_index, stem_element

VARIANT = "bazi-combination-engine-v1"
XIYONG_CONTRACT_VARIANT = "bazi-xiyong-combination-contract-v1"

# 已审规则 ID（只列本模块实际消费的；流年干支推导只用六十甲子表，
# 不冒充已调用 annual_lichun_boundaries）。
RULE_PILLARS = "bazi.phase2.pillars"
RULE_TEN_GODS = "bazi.phase2.ten_gods"
RULE_STEM_COMBINATIONS = "bazi.phase2.stem_five_combinations"
RULE_SIX_HARMONIES = "bazi.phase2.branch_six_harmonies"
RULE_HARMS = "bazi.phase2.branch_six_harms"
RULE_CLASHES = "bazi.phase2.branch_six_clashes"
RULE_TRIPLE_HARMONIES = "bazi.phase2.branch_triple_harmonies"
RULE_DIRECTIONAL_MEETINGS = "bazi.phase2.branch_directional_meetings"
RULE_DAYUN_SEQUENCE = "bazi-dayun-month-sequence-research-v1"
RULE_TIAOHOU_ASSESSMENT = "bazi.phase2.tiaohou_assessment"
RULE_BINGYAO_ASSESSMENT = "bazi.phase2.bingyao_assessment"
RULE_STRENGTH_FACTORS = "ditiansui-root-visibility-v1"
RULE_PATTERN_CANDIDATES = "bazi-pattern-structure-candidates-v1"
RULE_FUYI_SLICE = "bazi-fuyi-slice-adjudication-v1"

# 第二批消费的引擎变体（只作输入校验，不 import 对应模块；本模块
# 仍只依赖 foundations，公开检出可执行）。
STRENGTH_ENGINE_VARIANT = "bazi-strength-engine-v1"
PATTERN_ENGINE_VARIANT_V2 = "bazi-pattern-engine-v2"
XIYONG_ENGINE_VARIANT = "bazi-xiyong-engine-v1"
ANNUAL_CONTRACT_VARIANT = "bazi-xiyong-annual-contract-v1"
RULE_STRENGTH_ENGINE = STRENGTH_ENGINE_VARIANT
RULE_PATTERN_ENGINE_V2 = PATTERN_ENGINE_VARIANT_V2
RULE_XIYONG_ENGINE = XIYONG_ENGINE_VARIANT
RULE_MODERN_STRENGTH_MODEL = "strength_model_modern_v1"
# 喜用引擎格局体系的有资格规则（与 bazi_xiyong_engine 的
# VALIDATED_CANDIDATE_RULE_IDS 同值；此处只作消费端核对，不重定规则）。
VALIDATED_PATTERN_RULE_IDS = frozenset((
    "bazi.phase2.official_pattern_candidates",
    "bazi.phase2.resource_pattern_candidates",
    "bazi.phase2.ren_yin_true_pattern",
))
# 流年喜用年度契约：喜用引擎的 6 项已实现对照（取代旧契约的 4 项）。
ANNUAL_IMPLEMENTED = (
    "flow_year_ganzhi_and_ten_god",
    "flow_stem_presence_against_natal_tiaohou_sequence",
    "flow_stem_ten_god_role_against_bingyao_pairs",
    "rule_call_structure",
    "flow_stem_presence_against_fuyi_modern_candidates",
    "flow_stem_presence_against_pattern_basis",
)
ANNUAL_PENDING = (
    "annual_tiaohou_derivation",
    "annual_bingyao_derivation",
    "annual_fuyi_derivation",
    "annual_pattern_yongshen_derivation",
    "unified_annual_verdict",
)
# 条件结论的 verdict 标签（只作存在性 / 模型口径事实标签，绝非
# 吉凶、强弱、格局或效力断言）。第三批新增四种：病药三角色与格局
# 候选格神（见模块 docstring 第三批）。
CONDITIONAL_VERDICTS = (
    "stem_matches_established_pattern_god",
    "stem_matches_fuyi_modern_candidate",
    "stem_matches_natal_tiaohou_sequence",
    "model_treatment_recorded_only",
    "stem_matches_bingyao_subject_god",
    "stem_matches_bingyao_disease_god",
    "stem_matches_bingyao_medicine_god",
    "stem_matches_pattern_candidate_god",
)

# 十神全集（只作病药角色类与格局候选格神的合法性核对）。
TEN_GODS = frozenset((
    "比肩", "劫财", "正印", "偏印", "食神", "伤官",
    "正官", "七杀", "正财", "偏财",
))

# 地支本气五行转录表：子水、丑土、寅木、卯木、辰土、巳火、午火、
# 未土、申金、酉金、戌土、亥水。来源与关系表同源（canonical
# seed.json 的 earthly_branches 行本气列）；本模块不 import 需要
# seed.json 的 foundations.branch_element（公开检出无该文件），
# 故在此转录，密封环境下的专项测试逐项核对转录与 seed 表一致，
# 漂移即失败。只用于地支关系行的五行方向事实，不作效力判断。
BRANCH_ELEMENTS = {
    "子": "水", "丑": "土", "寅": "木", "卯": "木",
    "辰": "土", "巳": "火", "午": "火", "未": "土",
    "申": "金", "酉": "金", "戌": "土", "亥": "水",
}
# 已审地支对关系种（六合/害/冲三表互不重叠，每对至多命中一行）。
BRANCH_PAIR_KINDS = (
    "branch_six_harmony", "branch_harm", "branch_clash",
)

PILLAR_NAMES = ("year", "month", "day", "hour")

# --- 转录的已审关系表 -----------------------------------------------
# 来源：data/canonical/bazi/foundations_v1.json（stem_combinations 与
# earthly_branch_relations）；与 bazi_core 的三个已审函数消费同一表。
# 刑（punishment）在已审表中不存在，故本模块不评估刑，只登记未评估。

# 五合：(甲, 己) -> 土，余类推。frozenset 作键，值取化气之行。
STEM_FIVE_COMBINATIONS = {
    frozenset(("甲", "己")): "土",
    frozenset(("乙", "庚")): "金",
    frozenset(("丙", "辛")): "水",
    frozenset(("丁", "壬")): "木",
    frozenset(("戊", "癸")): "火",
}
# 六合：值取合化之行；午未一项原文作“火/土(有争议)”，逐字保留。
BRANCH_SIX_HARMONIES = {
    frozenset(("子", "丑")): "土",
    frozenset(("寅", "亥")): "木",
    frozenset(("卯", "戌")): "火",
    frozenset(("辰", "酉")): "金",
    frozenset(("巳", "申")): "水",
    frozenset(("午", "未")): "火/土(有争议)",
}
BRANCH_HARMS = {
    frozenset(("子", "未")),
    frozenset(("丑", "午")),
    frozenset(("寅", "巳")),
    frozenset(("卯", "辰")),
    frozenset(("申", "亥")),
    frozenset(("酉", "戌")),
}
BRANCH_CLASHES = {
    frozenset(("子", "午")),
    frozenset(("丑", "未")),
    frozenset(("寅", "申")),
    frozenset(("卯", "酉")),
    frozenset(("辰", "戌")),
    frozenset(("巳", "亥")),
}
# 三合 / 方位会：(成员三支, 成局之行)。
BRANCH_TRIPLE_HARMONIES = (
    (("申", "子", "辰"), "水"),
    (("亥", "卯", "未"), "木"),
    (("寅", "午", "戌"), "火"),
    (("巳", "酉", "丑"), "金"),
)
BRANCH_DIRECTIONAL_MEETINGS = (
    (("寅", "卯", "辰"), "木"),
    (("巳", "午", "未"), "火"),
    (("申", "酉", "戌"), "金"),
    (("亥", "子", "丑"), "水"),
)

# 十神判定表（与 foundations_v1.json 的 ten_gods_rule 逐字一致；
# 阳干为同性、阴干为异性，见 foundations 的 polarity 约定）。
_TEN_GOD_BY_RELATION = {
    "same_element": {"same_polarity": "比肩", "different_polarity": "劫财"},
    "generates_me": {"same_polarity": "偏印", "different_polarity": "正印"},
    "i_generate": {"same_polarity": "食神", "different_polarity": "伤官"},
    "controls_me": {"same_polarity": "七杀", "different_polarity": "正官"},
    "i_control": {"same_polarity": "偏财", "different_polarity": "正财"},
}
_STEM_POLARITY = {stem: ("阳" if i % 2 == 0 else "阴")
                  for i, stem in enumerate(STEMS)}

LIMITATIONS = (
    "本引擎只报告跨层干支结构事实，不推断任何效力：无已审跨层效力规则 "
    "（TJ-017.2 原局＋大运＋流年跨规则调用阻塞，TJ-023.3 流年用神阻塞），"
    "效力层一律 abstain。",
    "合化是否成立未裁定：五合、六合、三合只报配对事实，化气成立需另行 "
    "审定的合化规则（《渊海》合化事实审定亦只记 unresolved）。",
    "刑未评估：已审地支关系表（canonical foundations_v1.json 的 "
    "earthly_branch_relations）不含刑表，本引擎不自行补刑表、不评估刑。",
    "大运与流年的期位映射未裁定：大运起运岁数、交运时刻未在本引擎计算； "
    "除非调用方显式指定当期运及其依据，否则流年落在哪一运记为未确定， "
    "大运×流年关系按逐运列举，不指定当期。",
    "流年干支只按公历年份的六十甲子表推导，不裁定立春交界与年内分界； "
    "精确的流年边界以 bazi-annual-lichun-boundary-v1 为准，本引擎不代行。",
    "扶抑零行可建（bazi-fuyi-slice-adjudication-v1，buildable_count=0）； "
    "B2（2026-11-25 裁决）重开扶抑三模型仍无可执行模型，本契约不预判其结论。",
    "喜用四体系并列呈现、统一裁决恒拒判（TJ-013.2 裁决 A）；流年喜用完整 "
    "推演待对应规则获批，契约只含数据与调用结构。",
    "本引擎不注册 Phase1/Phase2 rule，不进 RuleMatch 与 Evidence； "
    "恒 research_only=True、public_enabled=False、ai_enabled=False。",
    "条件结论（status conditional）只陈述存在性事实或现代工程模型的 "
    "处理口径，绝非跨层效力断言：流年/大运干与格神、扶抑现代候选干、"
    "调候序列同字只记同字事实；Q3-A 只记冲/害/六合在原局现代模型内"
    "只记录、score_adjustment 恒为 0，跨层冲/害/合的效力仍未裁定。",
    "旺衰不确定性全程传导：土/丁日主得地未校准（Q5）、四库月得令记零"
    "（Q6）、balanced 只是现代模型中间带（Q9）、从格候选恒不等于成立"
    "（Q4）、古典与现代分歧不强制统一；组合层不把任何一项洗成确定结论。",
    "格局 broken 只经伤官见官一途输出（按契约验收，只作破格登记，"
    "永不计入成立）；其余每格只具名破格缺口；D-1 成立只认任氏寅月"
    "真格，不外推其他月份与流派；官杀混杂与杂气的多 Variant 并列，"
    "不统一、不代选。",
    "喜用引擎格局变体已统一为 v2（C1，2026-11-25）：combine() 直接"
    "消费 v2 格局输出，xiyong 侧格局体系亦消费同一 v2 输出；本地"
    "已验证输入结构/版本/字段语义与兼容性（v2 接受、v1 拒收、"
    "pattern=None 仍可用），机上实时接通待验证。",
    "大运×流年对内仅两支，三合/方位会需三支，组关系在本对内无可形成"
    "之组；跨三层之组只记同时含大运支与流年支者，见 "
    "dayun_x_flow_x_natal scope。",
    "第三批条件结论（病药三角色、格局候选格神）只陈述存在性事实："
    "药神类在场不等于病已去（medicine_effect_status 恒未裁定），"
    "病神类在场不等于害已成，格局候选格神同十神不等于格已成立；"
    "条件结论不是跨层效力断言，overall_effect 恒为 None。",
    "冲/害/六合作为跨层结构条件结论已批（C2，2026-11-25）：Q3-A "
    "口径只作结构条件结论，不直接推导实际效力；跨层效力本身仍未"
    "裁定（TJ-017.2），效力层不输出吉凶断言。",
    "扶抑现代规则（fuyi-modern-rules-v1）已批为研究模型（C3/X1，"
    "2026-11-25）：依赖它的条件结论（E2）为已批研究模型结论，仍"
    "只记同字存在性事实，不作古典扶抑断言；喜用路模型对象的状态"
    "字段更新由喜用路负责，本引擎只消费其 candidate_stems 输出。",
    "C 盘大运方向 forward 为明确指定的研究算例参数（C4，"
    "2026-11-25）：实际排盘须用已裁定的大运方向规则，不得把未知"
    "角色默认成顺行，也不得混淆日干与方向规则规定的年干输入；本"
    "引擎不推导方向，只消费调用方提供的 sequence 行，不输出方向"
    "推断。",
    "跨三层组 scope（dayun_x_flow_x_natal）已批保留（C5，"
    "2026-11-25）：只记同时含大运支与流年支之组；证据去重——跨"
    "层组与两对 scope 的组无重叠（成员必含大运支与流年支），不将"
    "重复结构关系计为多份独立作用；组关系本身不产生条件结论。",
    "弃判传导已批（C6，2026-11-25）：现代旺衰弃判时，依赖该结果"
    "的现代扶抑及效力分支弃判——本引擎的 Q3-A 模型口径结论只在现"
    "代层实际评分时发出（components 非空），现代弃判时不发；独立"
    "的调候、病药、格局结论不受影响。",
)


def ten_god_for(day_master, target_stem):
    """十神：与 bazi_core.ten_god 同一判定（五行关系＋阴阳同异性）。

    只依赖 foundations 的纯常量与 canonical ten_gods_rule 的转录表。
    """
    if day_master not in STEMS or target_stem not in STEMS:
        raise ValueError("ten_god_for requires two heavenly stems")
    day_element = stem_element(day_master)
    target_element = stem_element(target_stem)
    if target_element == day_element:
        relation = "same_element"
    elif GENERATES[target_element] == day_element:
        relation = "generates_me"
    elif GENERATES[day_element] == target_element:
        relation = "i_generate"
    elif CONTROLS[target_element] == day_element:
        relation = "controls_me"
    elif CONTROLS[day_element] == target_element:
        relation = "i_control"
    else:  # 五行生克图应使此分支不可达。
        raise ValueError("Unresolvable five-element relation")
    polarity = ("same_polarity"
                if _STEM_POLARITY[day_master] == _STEM_POLARITY[target_stem]
                else "different_polarity")
    return _TEN_GOD_BY_RELATION[relation][polarity]


def _five_element_direction(from_element, to_element):
    """从 from_element 看 to_element 的五行方向事实（只报方向，不报效力）。"""
    if from_element == to_element:
        return "same"
    if GENERATES[from_element] == to_element:
        return "generates"
    if GENERATES[to_element] == from_element:
        return "generated_by"
    if CONTROLS[from_element] == to_element:
        return "controls"
    if CONTROLS[to_element] == from_element:
        return "controlled_by"
    raise ValueError("Unresolvable five-element direction")


def _fail(message):
    raise ValueError(message)


def _stem_of(pillar, label):
    stem = pillar.get("stem")
    if isinstance(stem, dict):
        stem = stem.get("value")
    if type(stem) is not str or stem not in STEMS:
        _fail("%s stem must be one heavenly stem" % label)
    return stem


def _branch_of(pillar, label):
    branch = pillar.get("branch")
    if isinstance(branch, dict):
        branch = branch.get("value")
    if type(branch) is not str or branch not in BRANCHES:
        _fail("%s branch must be one earthly branch" % label)
    return branch


def _normalize_pillars(natal_pillars, day_master):
    if type(natal_pillars) is not list or len(natal_pillars) != 4:
        _fail("natal_pillars must be four ordered year/month/day/hour pillars")
    normalized = []
    for index, pillar in enumerate(natal_pillars):
        name = PILLAR_NAMES[index]
        if isinstance(pillar, str):
            ganzhi_index(pillar)  # 校验六十甲子合法性
            stem, branch = pillar[0], pillar[1]
            row = {"name": name, "ganzhi": pillar, "stem": stem,
                   "branch": branch}
        elif isinstance(pillar, dict):
            if pillar.get("name", name) != name:
                _fail("natal pillar order must be year/month/day/hour")
            stem = _stem_of(pillar, name)
            branch = _branch_of(pillar, name)
            ganzhi = pillar.get("ganzhi")
            if ganzhi is not None and ganzhi != stem + branch:
                _fail("natal pillar ganzhi disagrees with its stem and branch")
            row = {"name": name, "ganzhi": stem + branch, "stem": stem,
                   "branch": branch}
        else:
            _fail("natal pillar must be a ganzhi string or a pillar object")
        supplied = None
        if isinstance(pillar, dict) and isinstance(pillar.get("stem"), dict):
            supplied = pillar["stem"].get("ten_god")
        computed = ("日主" if name == "day"
                    else ten_god_for(day_master, row["stem"]))
        if supplied is not None and supplied != computed:
            _fail("natal pillar ten_god disagrees with the reviewed ten-god rule")
        row["stem_ten_god"] = computed
        row["stem_element"] = stem_element(row["stem"])
        normalized.append(row)
    if normalized[2]["stem"] != day_master:
        _fail("day_master must equal the day pillar stem")
    return normalized


def _normalize_dayun(dayun_periods, day_master):
    if type(dayun_periods) is not list or not dayun_periods:
        _fail("dayun_periods must be a non-empty list of sequence rows")
    seen = set()
    normalized = []
    for row in dayun_periods:
        if not isinstance(row, dict):
            _fail("dayun period must be a sequence row object")
        period_index = row.get("period_index")
        if type(period_index) is not int or not 1 <= period_index <= 12:
            _fail("dayun period_index must be an integer from 1 to 12")
        if period_index in seen:
            _fail("dayun period_index duplicated")
        seen.add(period_index)
        ganzhi = row.get("candidate_ganzhi", row.get("ganzhi"))
        if type(ganzhi) is not str:
            _fail("dayun period must carry candidate_ganzhi or ganzhi")
        ganzhi_index(ganzhi)
        stem, branch = ganzhi[0], ganzhi[1]
        if row.get("stem") is not None and row["stem"] != stem:
            _fail("dayun period stem disagrees with its ganzhi")
        if row.get("branch") is not None and row["branch"] != branch:
            _fail("dayun period branch disagrees with its ganzhi")
        supplied = row.get("ten_god_relative_to_natal_day_stem",
                           row.get("ten_god"))
        computed = ten_god_for(day_master, stem)
        if supplied is not None and supplied != computed:
            _fail("dayun period ten_god disagrees with the reviewed ten-god rule")
        normalized.append({
            "period_index": period_index,
            "candidate_ganzhi": ganzhi,
            "stem": stem,
            "branch": branch,
            "stem_ten_god": computed,
            "stem_element": stem_element(stem),
        })
    normalized.sort(key=lambda r: r["period_index"])
    return normalized


def _flow_year(target_year, day_master):
    if type(target_year) is not int or not 1900 <= target_year <= 2098:
        _fail("target_year must be an integer calendar year 1900..2098")
    ganzhi = CYCLE[(target_year - 4) % 60]
    return {
        "target_year": target_year,
        "ganzhi": ganzhi,
        "stem": ganzhi[0],
        "branch": ganzhi[1],
        "stem_ten_god": ten_god_for(day_master, ganzhi[0]),
        "stem_element": stem_element(ganzhi[0]),
        "derivation": "sexagenary_cycle_index",
        "derivation_note": ("年干支按六十甲子表 CYCLE[(year-4)%60] 推导，与 "
                            "bazi-annual-lichun-boundary-v1 的核对公式一致；"
                            "立春交界与年内分界不在此推导范围。"),
    }


def _side(layer, *, pillar=None, period_index=None, stem, branch,
          stem_ten_god):
    side = {"layer": layer, "stem": stem, "branch": branch,
            "stem_ten_god": stem_ten_god,
            "stem_element": stem_element(stem)}
    if pillar is not None:
        side["pillar"] = pillar
    if period_index is not None:
        side["period_index"] = period_index
    return side


def _condition(condition_id, statement, status, rule_ids, basis=None):
    row = {"id": condition_id, "statement": statement, "status": status,
           "rule_ids": list(rule_ids)}
    if basis is not None:
        row["basis"] = basis
    return row


def _abstain(reason, rule_ids):
    return {"verdict": None, "status": "abstain", "reason": reason,
            "rule_ids": list(rule_ids)}


_ABSTAIN_EFFECT_REASON = (
    "无已审跨层效力规则：TJ-017.2（原局＋大运＋流年跨规则调用）与 "
    "TJ-023.3（流年用神）均阻塞；结构事实本身不推效力，故拒判。"
)


def _stem_pair_relations(counter, scope, side_a, side_b, *, period_index,
                         mapping_condition):
    """一对天干之间的结构关系：五合（若命中）＋五行方向事实（恒报）。"""
    rows = []
    key = frozenset((side_a["stem"], side_b["stem"]))
    if key in STEM_FIVE_COMBINATIONS:
        counter[0] += 1
        rows.append({
            "id": "R%03d" % counter[0],
            "scope": scope,
            "period_index": period_index,
            "side_a": copy.deepcopy(side_a),
            "side_b": copy.deepcopy(side_b),
            "kind": "stem_five_combination",
            "detail": {
                "stems": [side_a["stem"], side_b["stem"]],
                "traditional_result_element":
                    STEM_FIVE_COMBINATIONS[key],
            },
            "conditions": [
                _condition(
                    "both_sides_attested",
                    "双方天干均由已审输入给出",
                    "satisfied", [RULE_PILLARS, RULE_TEN_GODS]),
                _condition(
                    "combination_transformation",
                    "五合配对成立，但合化是否成立未裁定：化气成立需另行审定的合化规则",
                    "cannot_judge", [RULE_STEM_COMBINATIONS]),
            ] + ([mapping_condition] if mapping_condition else []),
            "effect": _abstain(
                _ABSTAIN_EFFECT_REASON + "合化未裁定亦不得据合推效力。",
                [RULE_STEM_COMBINATIONS]),
            "rule_ids": [RULE_STEM_COMBINATIONS, RULE_TEN_GODS],
        })
    counter[0] += 1
    rows.append({
        "id": "R%03d" % counter[0],
        "scope": scope,
        "period_index": period_index,
        "side_a": copy.deepcopy(side_a),
        "side_b": copy.deepcopy(side_b),
        "kind": "stem_five_element",
        "detail": {
            "stems": [side_a["stem"], side_b["stem"]],
            "same_stem": side_a["stem"] == side_b["stem"],
            "elements": [side_a["stem_element"], side_b["stem_element"]],
            "direction_from_a_to_b": _five_element_direction(
                side_a["stem_element"], side_b["stem_element"]),
            "ten_gods": [side_a["stem_ten_god"], side_b["stem_ten_god"]],
        },
        "conditions": [
            _condition(
                "both_sides_attested",
                "双方天干与五行均由已审输入与 foundations 常量给出",
                "satisfied", [RULE_PILLARS, RULE_TEN_GODS]),
            _condition(
                "generating_controlling_effect",
                "生克方向事实不等于效力：生扶克泄耗的实际效力未裁定（整体强弱未判）",
                "cannot_judge", [RULE_TEN_GODS]),
        ] + ([mapping_condition] if mapping_condition else []),
        "effect": _abstain(_ABSTAIN_EFFECT_REASON, [RULE_TEN_GODS]),
        "rule_ids": [RULE_TEN_GODS],
    })
    return rows


def _branch_pair_relations(counter, scope, side_a, side_b, *, period_index,
                           mapping_condition):
    """一对地支之间的已审关系：六合 / 害 / 冲（刑不在已审表中，不评估）。"""
    rows = []
    key = frozenset((side_a["branch"], side_b["branch"]))
    specs = (
        ("branch_six_harmony", "six_harmony", BRANCH_SIX_HARMONIES,
         RULE_SIX_HARMONIES,
         "六合配对成立，但合化是否成立未裁定：化气成立需另行审定的合化规则",
         "combination_transformation"),
        ("branch_harm", "harm", BRANCH_HARMS, RULE_HARMS,
         "害的结构事实已报，但害的效力（是否损局、应期）未裁定：无已审跨层害效力规则",
         "harm_effect"),
        ("branch_clash", "clash", BRANCH_CLASHES, RULE_CLASHES,
         "冲的结构事实已报，但冲的效力（是否冲动、冲破、应期）未裁定：无已审跨层冲效力规则",
         "clash_effect"),
    )
    for kind, _, table, rule_id, effect_statement, condition_id in specs:
        if key not in table:
            continue
        counter[0] += 1
        detail = {"branches": [side_a["branch"], side_b["branch"]],
                  "same_branch": side_a["branch"] == side_b["branch"],
                  "elements": [BRANCH_ELEMENTS[side_a["branch"]],
                               BRANCH_ELEMENTS[side_b["branch"]]],
                  "direction_from_a_to_b": _five_element_direction(
                      BRANCH_ELEMENTS[side_a["branch"]],
                      BRANCH_ELEMENTS[side_b["branch"]])}
        if kind == "branch_six_harmony":
            detail["traditional_result_element"] = table[key]
        rows.append({
            "id": "R%03d" % counter[0],
            "scope": scope,
            "period_index": period_index,
            "side_a": copy.deepcopy(side_a),
            "side_b": copy.deepcopy(side_b),
            "kind": kind,
            "detail": detail,
            "conditions": [
                _condition(
                    "both_sides_attested",
                    "双方地支均由已审输入给出",
                    "satisfied", [RULE_PILLARS]),
                _condition(condition_id, effect_statement, "cannot_judge",
                           [rule_id]),
            ] + ([mapping_condition] if mapping_condition else []),
            "effect": _abstain(_ABSTAIN_EFFECT_REASON, [rule_id]),
            "rule_ids": [rule_id],
        })
    return rows


def _group_relations(counter, scope, branches_with_sides, *, period_index,
                     mapping_condition, required_branches=None):
    """三合 / 方位会：只在该 scope 的地支集合上评估，不跨 scope 借支。

    ``required_branches`` 非空时，只输出同时含全部指定支的组（用于
    跨三层 scope：只记未被两对 scope 覆盖、同时含大运支与流年支之组）。
    """
    rows = []
    present = {}
    for branch, side in branches_with_sides:
        present.setdefault(branch, []).append(side)
    for table, kind, rule_id in (
            (BRANCH_TRIPLE_HARMONIES, "branch_triple_harmony",
             RULE_TRIPLE_HARMONIES),
            (BRANCH_DIRECTIONAL_MEETINGS, "branch_directional_meeting",
             RULE_DIRECTIONAL_MEETINGS)):
        for members, result_element in table:
            if not all(member in present for member in members):
                continue
            if required_branches is not None and not set(
                    required_branches).issubset(set(members)):
                continue
            counter[0] += 1
            rows.append({
                "id": "R%03d" % counter[0],
                "scope": scope,
                "period_index": period_index,
                "side_a": None,
                "side_b": None,
                "kind": kind,
                "detail": {
                    "branches": list(members),
                    "traditional_result_element": result_element,
                    "member_sides": [
                        copy.deepcopy(present[member][0])
                        for member in members
                    ],
                },
                "conditions": [
                    _condition(
                        "all_members_attested",
                        "三支均由已审输入给出（同一 scope 内）",
                        "satisfied", [RULE_PILLARS]),
                    _condition(
                        "group_transformation" if kind == "branch_triple_harmony"
                        else "group_effect",
                        ("三合成局但合化是否成立未裁定：化气成立需另行审定的合化规则"
                         if kind == "branch_triple_harmony"
                         else "方位会合的结构事实已报，但其效力未裁定：无已审跨层会合效力规则"),
                        "cannot_judge", [rule_id]),
                ] + ([mapping_condition] if mapping_condition else []),
                "effect": _abstain(_ABSTAIN_EFFECT_REASON, [rule_id]),
                "rule_ids": [rule_id],
            })
    return rows


def _mapping_condition(current_period_index, current_period_basis,
                       period_index):
    """大运×流年关系的期位前提：未指定当期运时一律无法判定。"""
    if current_period_index is None:
        return _condition(
            "period_year_mapping",
            "未指定当期运：流年落在哪一运未确定，本关系按逐运列举，不指定当期",
            "cannot_judge", [RULE_DAYUN_SEQUENCE])
    if period_index == current_period_index:
        return _condition(
            "period_year_mapping",
            "调用方指定当期运（依据见 dayun.current_period_basis）",
            "satisfied", [RULE_DAYUN_SEQUENCE],
            basis=current_period_basis)
    return _condition(
        "period_year_mapping",
        "非调用方指定的当期运：本关系只作逐运结构列举，不指定当期",
        "not_satisfied", [RULE_DAYUN_SEQUENCE],
        basis=current_period_basis)


def _validate_engine_statement(statement, variant, label, *,
                               day_master=None, month_branch=None,
                               flag_style="enabled"):
    """校验一个引擎输出字典的变体、治理旗标与日主/月支一致性。

    ``flag_style`` 为 ``"enabled"`` 时核 ``public_enabled`` /
    ``ai_enabled``（旺衰/喜用引擎）；为 ``"public"`` 时核 ``public`` /
    ``ai``（格局引擎 v2）。只校验，不重算。
    """
    if not isinstance(statement, dict):
        _fail("%s statement must be an object" % label)
    if statement.get("variant") != variant:
        _fail("%s statement variant drifted" % label)
    if statement.get("research_only") is not True:
        _fail("%s statement research_only drifted" % label)
    if flag_style == "enabled":
        if statement.get("public_enabled") is not False:
            _fail("%s statement public_enabled drifted" % label)
        if statement.get("ai_enabled") is not False:
            _fail("%s statement ai_enabled drifted" % label)
    else:
        if statement.get("public") is not False:
            _fail("%s statement public drifted" % label)
        if statement.get("ai") is not False:
            _fail("%s statement ai drifted" % label)
    if day_master is not None:
        actual = statement.get("day_master", statement.get("day_stem"))
        if actual != day_master:
            _fail("%s statement disagrees on the day master" % label)
    if month_branch is not None and statement.get(
            "month_branch") != month_branch:
        _fail("%s statement disagrees on the month branch" % label)
    return copy.deepcopy(statement)


def _summarize_strength_assessment(assessment, day_master, month_branch):
    """原样转述 assess_strength 输出的可消费摘要（不重算、不合并）。

    古典分类、现代评分/分项、Q5/Q6 不确定性标记、从格候选屏、
    古典/现代分歧关系全部照录；modern 为 None（未启用）时照录 None。
    """
    statement = _validate_engine_statement(
        assessment, STRENGTH_ENGINE_VARIANT, "strength assessment",
        day_master=day_master, month_branch=month_branch)
    classical = statement.get("classical")
    modern = statement.get("modern")
    if not isinstance(classical, dict):
        _fail("strength assessment classical layer malformed")
    if modern is not None and not isinstance(modern, dict):
        _fail("strength assessment modern layer malformed")
    if modern is not None:
        if modern.get("model_id") != RULE_MODERN_STRENGTH_MODEL:
            _fail("strength assessment modern model_id drifted")
        if modern.get("model_kind") != "modern_engineering":
            _fail("strength assessment modern model_kind drifted")
        if modern.get("verdict") not in (
                "strong", "weak", "balanced", "abstain"):
            _fail("strength assessment modern verdict drifted")
    agreement = statement.get("agreement") or {}
    matched = classical.get("matched_predicate")
    cong = None
    interactions = None
    if modern is not None:
        cong_block = modern.get("cong_candidates")
        if isinstance(cong_block, dict):
            cong = {
                "candidates": [
                    {"kind": c.get("kind"), "name_cn": c.get("name_cn"),
                     "establishment": c.get("establishment"),
                     "verdict": c.get("verdict")}
                    for c in cong_block.get("candidates") or []],
                "screen_triggered": cong_block.get("screen_triggered"),
                "screen_kinds": list(
                    cong_block.get("screen_kinds") or []),
                "screen_reason": cong_block.get("screen_reason"),
            }
        inter_block = modern.get("interaction_effects")
        if isinstance(inter_block, dict):
            interactions = {
                "records": [
                    {"kind": r.get("kind"), "name_cn": r.get("name_cn"),
                     "effect_on_strength": r.get("effect_on_strength"),
                     "score_adjustment": r.get("score_adjustment")}
                    for r in inter_block.get("records") or []],
                "score_adjustment_total": inter_block.get(
                    "score_adjustment_total"),
            }
    components = None
    if modern is not None and isinstance(modern.get("components"), dict):
        components = {
            key: {"score": value.get("score"),
                  "basis": value.get("basis"),
                  "conditions": list(value.get("conditions") or [])}
            for key, value in modern["components"].items()
            if isinstance(value, dict)}
    return {
        "status": "consumed",
        "input_kind": "strength_assessment",
        "variant": STRENGTH_ENGINE_VARIANT,
        "classical": {
            "classification": classical.get("classification"),
            "matched_predicate": (
                matched.get("predicate_id")
                if isinstance(matched, dict) else None),
            "matched_predicate_verification": (
                matched.get("verification")
                if isinstance(matched, dict) else None),
            "blockers": list(classical.get("blockers") or []),
        },
        "modern": None if modern is None else {
            "model_id": modern.get("model_id"),
            "model_kind": modern.get("model_kind"),
            "verdict": modern.get("verdict"),
            "score": modern.get("score"),
            "score_band": modern.get("score_band"),
            "classification_status": modern.get("classification_status"),
            "definite_classification": modern.get(
                "definite_classification"),
            "uncertainty_flags": list(
                modern.get("uncertainty_flags") or []),
            "abstain_reason": modern.get("abstain_reason"),
            "abstain_detail": modern.get("abstain_detail"),
            "components": components,
            "cong_candidates": cong,
            "interaction_effects": interactions,
        },
        "agreement": {
            "classical": agreement.get("classical"),
            "modern": agreement.get("modern"),
            "relationship": agreement.get("relationship"),
            "note": agreement.get("note"),
        },
        "statement": statement,
    }


def _validate_broken_pattern_result(key, result, evidence_ids):
    """破格输入契约（第三批集成，与喜用引擎同口径）：只认唯一已审
    古典破格通道——伤官见官（任氏寅月真格成立的伤官格＋正官在场）。

    逐项核对：格键须为 ``shangguan``；rule_ids 须含 Ren D-1 规则；
    证据 id 须含原成立身份 ``ren_yin_true_pattern`` 与破格证据
    ``shangguan_sees_officer_broken``；additive 结构化字段须在场且
    与证据一致。任一项漂移即 fail-closed。
    """
    if key != "shangguan":
        _fail("pattern result broken outside the reviewed "
              "shangguan channel")
    rule_ids = result.get("rule_ids") or []
    if not isinstance(rule_ids, list) \
            or any(type(item) is not str for item in rule_ids) \
            or "bazi.phase2.ren_yin_true_pattern" not in rule_ids:
        _fail("pattern result broken lacks the reviewed ren_yin rule")
    if not {"ren_yin_true_pattern",
            "shangguan_sees_officer_broken"} <= set(evidence_ids):
        _fail("pattern result broken lacks establishment or breaking "
              "evidence")
    if result.get("broken_condition") != "shangguan_sees_officer":
        _fail("pattern result broken_condition drifted")
    broken_evidence_ids = result.get("broken_evidence_ids")
    if type(broken_evidence_ids) is not list \
            or any(type(item) is not str for item in broken_evidence_ids) \
            or "shangguan_sees_officer_broken" not in broken_evidence_ids:
        _fail("pattern result broken_evidence_ids drifted")
    if result.get("original_state") != "established":
        _fail("pattern result broken original_state drifted")
    if result.get("original_pattern") != result.get("pattern"):
        _fail("pattern result broken original_pattern drifted")


def _summarize_pattern_v2(pattern, day_master, month_branch):
    """原样转述 evaluate_all（v2）输出的可消费摘要（不重算、不合并）。

    每格状态、条件事实证据 id、Variant 信息、D-1 成立证据照录；
    ``broken`` 只经伤官见官一途输出：按契约验收后单列 ``broken``
    （破格依据与原成立身份随记录携带），永不计入 ``established``；
    通道外或字段漂移的 broken 一律拒收。
    """
    statement = _validate_engine_statement(
        pattern, PATTERN_ENGINE_VARIANT_V2, "pattern",
        day_master=day_master, month_branch=month_branch,
        flag_style="public")
    results = statement.get("results")
    if not isinstance(results, dict) or not results:
        _fail("pattern statement results malformed")
    by_state = {}
    established = []
    candidates = []
    conflicts = []
    broken = []
    broken_gaps = {}
    for key in sorted(results):
        result = results[key]
        if not isinstance(result, dict):
            _fail("pattern result must be an object")
        state = result.get("state")
        if state not in ("candidate", "established", "broken",
                         "conflict", "not_judgeable"):
            _fail("pattern result state drifted")
        by_state[state] = by_state.get(state, 0) + 1
        record = {
            "pattern_key": key,
            "pattern": result.get("pattern"),
            "state": state,
            "evidence_ids": [e.get("id") for e in
                             (result.get("evidence") or [])
                             if isinstance(e, dict)],
            "rule_ids": list(result.get("rule_ids") or []),
        }
        gaps = [line for line in (result.get("limitations") or [])
                if "破格缺口" in str(line)]
        if gaps:
            broken_gaps[key] = list(gaps)
        if state == "established":
            record["evidence"] = copy.deepcopy(result.get("evidence") or [])
            established.append(record)
        elif state == "candidate":
            candidates.append(record)
        elif state == "conflict":
            record["evidence"] = copy.deepcopy(result.get("evidence") or [])
            conflicts.append(record)
        elif state == "broken":
            _validate_broken_pattern_result(
                key, result, record["evidence_ids"])
            record["evidence"] = copy.deepcopy(result.get("evidence") or [])
            record["broken_condition"] = result.get("broken_condition")
            record["broken_evidence_ids"] = list(
                result.get("broken_evidence_ids"))
            record["original_state"] = result.get("original_state")
            record["original_pattern"] = result.get("original_pattern")
            broken.append(record)
    return {
        "status": "consumed",
        "input_kind": "pattern_engine_v2",
        "variant": PATTERN_ENGINE_VARIANT_V2,
        "counts": dict(by_state),
        "earth_gate": statement.get("earth_gate"),
        "established": established,
        "candidates": candidates,
        "conflicts": conflicts,
        "broken": broken,
        "broken_gaps": broken_gaps,
        "statement": statement,
    }


def _xiyong_from_engine(xiyong, day_master, month_branch):
    """原样转述 evaluate_xiyong 输出（四体系＋流年年度契约）。

    只校验变体、治理旗标、日主/月支与年度契约的 6 项已实现对照；
    待批 5 项须保持 pending，否则拒收（漂移即 fail-closed）。
    """
    statement = _validate_engine_statement(
        xiyong, XIYONG_ENGINE_VARIANT, "xiyong",
        day_master=day_master, month_branch=month_branch)
    if statement.get("unified_verdict") is not None:
        _fail("xiyong statement carries a unified verdict")
    systems = statement.get("systems")
    if not isinstance(systems, dict) or set(systems) != {
            "fuyi", "tiaohou", "bingyao", "pattern_yongshen"}:
        _fail("xiyong statement systems malformed")
    annual = statement.get("annual_xiyong")
    if annual is not None:
        if not isinstance(annual, dict):
            _fail("xiyong annual contract malformed")
        if annual.get("variant") != ANNUAL_CONTRACT_VARIANT:
            _fail("xiyong annual contract variant drifted")
        implemented = annual.get("implemented") or []
        if not set(ANNUAL_IMPLEMENTED).issubset(set(implemented)):
            _fail("xiyong annual contract implemented items drifted")
        if set(annual.get("pending") or []) != set(ANNUAL_PENDING):
            _fail("xiyong annual contract pending items drifted")
        if annual.get("derivation") is not None:
            _fail("xiyong annual contract carries a derivation")
        if annual.get("unified_verdict") is not None:
            _fail("xiyong annual contract carries a unified verdict")
    return statement


# 病药十神类成员表：与已登记病药规则的五类一致（财/比劫/食伤/
# 官杀/印）。字典形角色块只凭 ``god_class`` 定类，``gods`` 行只作
# 交叉核对——结论只认神类（与 ``subject_gods`` 列表形同值），不因
# 某成员是否在盘现身而缩小类。
_BINGYAO_GOD_CLASSES = {
    "财": ("正财", "偏财"),
    "比劫": ("比肩", "劫财"),
    "食伤": ("食神", "伤官"),
    "官杀": ("正官", "七杀"),
    "印": ("正印", "偏印"),
}


def _bingyao_god_list(value, label):
    """核对一则病药角色类，归一化为十神名列表，否则 fail-closed。

    接受三种已登记形态（同值，不同写法不得产出不同结论）：
    十神名列表、十神名元组（原生 ``bingyao_lookup`` 的规则常量即
    元组——机上实测 2026-11-25）、字典块 ``{god_class, gods}``
    （原生每对的 ``subject`` / ``disease_candidate`` /
    ``medicine_candidate`` 块）。字典形以 ``god_class`` 定类并返
    回该类全部成员，``gods`` 行须非空且每行十神均属该类，否则拒收。
    """
    if isinstance(value, dict):
        god_class = value.get("god_class")
        members = _BINGYAO_GOD_CLASSES.get(god_class)
        if members is None:
            _fail("%s carries an unknown god class" % label)
        gods = value.get("gods")
        if type(gods) is not list or not gods:
            _fail("%s dict block must carry non-empty gods rows" % label)
        for row in gods:
            if not isinstance(row, dict) \
                    or row.get("ten_god") not in members:
                _fail("%s dict block attests a god outside its class"
                      % label)
        return list(members)
    if type(value) not in (list, tuple) or not value:
        _fail("%s must be a non-empty list of ten gods" % label)
    for god in value:
        if god not in TEN_GODS:
            _fail("%s carries an unknown ten god" % label)
    return list(value)


def _bingyao_role_gods(value, pair, block_key, label):
    """取一则病药角色类：类表优先，缺失时退到对级字典块。

    ``value`` 为 ``rule``/平铺形态的类表（列表/元组/字典皆可）；
    ``value`` 为 None 时取 ``pair[block_key]`` 字典块（原生
    ``subject`` / ``disease_candidate`` / ``medicine_candidate``）；
    两者皆无则 fail-closed——不凭空补类（药不在盘且无类表时，
    药类不可知，拒收而非拟制）。
    """
    if value is not None:
        return _bingyao_god_list(value, label)
    block = pair.get(block_key)
    if isinstance(block, dict):
        return _bingyao_god_list(block, label)
    _fail("%s is missing" % label)


def _bingyao_triggered_roles_from_pairs(pairs):
    """从病药 pairs 提取已触发对的主体/病/药三角色类。

    接受三种已登记形态：原局病药输出（每对嵌 ``rule``，三类在
    ``rule`` 内——原生规则常量为元组）、喜用引擎病药体系（每对平
    铺三类与 ``rule_id``），以及类表缺失时退到对级字典块（每对的
    ``subject`` / ``disease_candidate`` / ``medicine_candidate``，
    ``{god_class, gods}``）。三种形态对同一对产出同一角色类；
    只取 status 为 triggered 的对；未触发对不输出角色（未触发不是
    「无病」）。medicine_effect_status 须为未裁定，否则拒收（本
    函数的结论文案以「药去病效力恒未裁定」为前提）。
    """
    if type(pairs) is not list:
        _fail("bingyao pairs must be a list")
    roles = []
    for pair in pairs:
        if not isinstance(pair, dict):
            _fail("bingyao pair must be an object")
        pair_id = pair.get("pair_id")
        if type(pair_id) is not str or not pair_id:
            _fail("bingyao pair_id malformed")
        status = pair.get("status")
        if status not in ("triggered", "not_triggered"):
            _fail("bingyao pair status drifted")
        if status != "triggered":
            continue
        rule = pair.get("rule")
        if isinstance(rule, dict):
            rule_id = rule.get("id")
            subject = rule.get("subject_gods")
            disease = rule.get("disease_gods")
            medicine = rule.get("medicine_gods")
        elif "rule" not in pair:
            rule_id = pair.get("rule_id")
            subject = pair.get("subject_gods")
            disease = pair.get("disease_gods")
            medicine = pair.get("medicine_gods")
        else:
            _fail("bingyao pair rule malformed")
        if type(rule_id) is not str or not rule_id:
            _fail("bingyao pair rule id malformed")
        effect_status = pair.get("medicine_effect_status")
        if effect_status not in (None, "unadjudicated"):
            _fail("bingyao pair carries an adjudicated medicine effect")
        roles.append({
            "pair_id": pair_id,
            "rule_id": rule_id,
            "subject_gods": _bingyao_role_gods(
                subject, pair, "subject", "bingyao subject"),
            "disease_gods": _bingyao_role_gods(
                disease, pair, "disease_candidate", "bingyao disease"),
            "medicine_gods": _bingyao_role_gods(
                medicine, pair, "medicine_candidate", "bingyao medicine"),
            "medicine_status": pair.get("medicine_status"),
        })
    return roles


def _pattern_candidate_gods(pattern_v2):
    """从格局 v2 候选格提取格神（只认 validated 规则、只认十神格名）。

    非十神格名（如从格/化气格类）不映射为十神，不输出结论；
    无 validated 规则的候选格不输出结论。候选恒不等于成立。
    """
    gods = []
    if pattern_v2 is None:
        return gods
    for record in pattern_v2["candidates"]:
        validated = sorted(
            set(record["rule_ids"]) & VALIDATED_PATTERN_RULE_IDS)
        if not validated:
            continue
        name = record["pattern"] or ""
        god = name[:-1] if name.endswith("格") else name
        if god not in TEN_GODS:
            continue
        gods.append({
            "pattern_key": record["pattern_key"],
            "pattern": name,
            "god": god,
            "rule_ids": validated,
        })
    return gods


def _conditional_conclusions(relation, *, day_master, fuyi_candidate_stems,
                             tiaohou_sequence_stems,
                             established_pattern_gods,
                             modern_strength_active,
                             bingyao_roles=(),
                             pattern_candidate_gods=()):
    """一条关系可得的条件结论（存在性 / 模型口径事实），无则为空。

    只对非原局侧（大运/流年）的干作存在性核对；原局侧干本身即扶抑
    候选干的来源，不作同字核对。返回的每条结论都带依据与“不是效力
    断言”的明记；调用方只在结论非空时改写 effect。第三批新增：
    病药三角色（已触发对的主体/病/药类）与格局候选格神（候选≠成立）。
    Q3-A 模型口径结论只在现代旺衰层实际评分时发出（C6 弃判传导：
    现代弃判则该分支弃判）；调候、病药、格局结论独立，不受其影响。
    """
    conclusions = []
    scope = relation["scope"]
    kind = relation["kind"]
    sides = []
    if scope in ("dayun_x_natal", "flow_x_natal"):
        sides = [("non_natal", relation["side_a"])]
    elif scope == "dayun_x_flow":
        sides = [("dayun", relation["side_a"]),
                 ("flow_year", relation["side_b"])]
    else:  # 组关系（side_a/side_b 为 None）不在此核对。
        sides = []
    if kind in ("stem_five_element", "stem_five_combination"):
        for side_label, side in sides:
            if side is None:
                continue
            stem = side["stem"]
            ten_god = side["stem_ten_god"]
            for god in established_pattern_gods:
                if ten_god == god:
                    conclusions.append({
                        "verdict": "stem_matches_established_pattern_god",
                        "side": side_label, "stem": stem,
                        "ten_god": ten_god, "pattern_god": god,
                        "reason": ("该侧干 %s（%s）与已成立格局之格神 %s 同"
                                   "十神：只记同十神存在性事实，不等于格局"
                                   "效力、格神得用或大运/流年吉凶。"
                                   % (stem, ten_god, god)),
                        "basis": {"pattern_god": god,
                                  "rule_ids": [
                                      "bazi.phase2.ren_yin_true_pattern"]},
                    })
            for entry in pattern_candidate_gods:
                if ten_god == entry["god"]:
                    conclusions.append({
                        "verdict": "stem_matches_pattern_candidate_god",
                        "side": side_label, "stem": stem,
                        "ten_god": ten_god,
                        "pattern_god": entry["god"],
                        "pattern_key": entry["pattern_key"],
                        "pattern": entry["pattern"],
                        "reason": ("该侧干 %s（%s）与格局候选格 %s 之格神"
                                   " %s 同十神：只记同十神存在性事实；候选"
                                   "恒不等于成立，不等于格局效力、格神得"
                                   "用或大运/流年吉凶。"
                                   % (stem, ten_god, entry["pattern"],
                                      entry["god"])),
                        "basis": {"pattern_key": entry["pattern_key"],
                                  "pattern": entry["pattern"],
                                  "state": "candidate",
                                  "rule_ids": list(entry["rule_ids"])},
                    })
            if stem in (fuyi_candidate_stems or ()):
                conclusions.append({
                    "verdict": "stem_matches_fuyi_modern_candidate",
                    "side": side_label, "stem": stem,
                    "ten_god": ten_god,
                    "reason": ("该侧干 %s 与原局扶抑现代层候选干同字：只记"
                               "同字存在性事实；现代扶抑规则为已批研究模型"
                               "（fuyi-modern-rules-v1，C3/X1），本结论不"
                               "等于大运/流年扶抑效力成立，也不作古典扶抑"
                               "断言。" % stem),
                    "basis": {"model_id": "fuyi-modern-rules-v1",
                              "model_kind": "modern_engineering"},
                })
            if stem in (tiaohou_sequence_stems or ()):
                conclusions.append({
                    "verdict": "stem_matches_natal_tiaohou_sequence",
                    "side": side_label, "stem": stem,
                    "ten_god": ten_god,
                    "reason": ("该侧干 %s 在原局调候序列中：只记存在性"
                               "事实，不据此取大运/流年调候用神；流年"
                               "调候推演未获批。" % stem),
                    "basis": {"rule_ids": [
                        RULE_TIAOHOU_ASSESSMENT]},
                })
            for role_entry in bingyao_roles:
                role = None
                if ten_god in role_entry["subject_gods"]:
                    role = "subject"
                elif ten_god in role_entry["disease_gods"]:
                    role = "disease"
                elif ten_god in role_entry["medicine_gods"]:
                    role = "medicine"
                if role is None:
                    continue
                role_cn = {"subject": "所论之神",
                           "disease": "病神",
                           "medicine": "药神"}[role]
                caveat = {
                    "subject": "不等于所论已定或病药去留有断",
                    "disease": "病在场不等于害已成，去病效力恒未裁定",
                    "medicine": ("药在场不等于病已去"
                                 "（medicine_effect_status 恒未裁定）"
                                 "，不据此断大运/流年病药去留"),
                }[role]
                conclusions.append({
                    "verdict": "stem_matches_bingyao_%s_god" % role,
                    "side": side_label, "stem": stem,
                    "ten_god": ten_god,
                    "pair_id": role_entry["pair_id"],
                    "role": role,
                    "reason": ("该侧干 %s（%s）属已触发病药对 %s 的%s类："
                               "只记角色存在性事实；%s；流年病药推演未获批。"
                               % (stem, ten_god, role_entry["pair_id"],
                                  role_cn, caveat)),
                    "basis": {"pair_id": role_entry["pair_id"],
                              "role": role,
                              "ten_god": ten_god,
                              "medicine_status":
                                  role_entry["medicine_status"],
                              "rule_ids": [RULE_BINGYAO_ASSESSMENT,
                                           role_entry["rule_id"]]},
                })
    if kind in ("branch_clash", "branch_harm", "branch_six_harmony") \
            and modern_strength_active:
        conclusions.append({
            "verdict": "model_treatment_recorded_only",
            "side": None, "stem": None,
            "ten_god": None,
            "reason": ("Q3-A 工程模型口径：此类关系（%s）在原局现代模型"
                       "内只记录作用条件与局限，score_adjustment 恒为 0；"
                       "跨层冲/害/合的实际效力仍未裁定（TJ-017.2），本条"
                       "只陈述模型处理口径，不作跨层效力断言。"
                       % {"branch_clash": "冲", "branch_harm": "害",
                          "branch_six_harmony": "六合"}[kind]),
            "basis": {"model_id": RULE_MODERN_STRENGTH_MODEL,
                      "model_kind": "modern_engineering",
                      "rule": "Q3-A interaction_conditions",
                      "score_adjustment": 0},
        })
    return conclusions


def _apply_conditional_effects(relations, *, day_master,
                               fuyi_candidate_stems,
                               tiaohou_sequence_stems,
                               established_pattern_gods,
                               modern_strength_active,
                               bingyao_roles=(),
                               pattern_candidate_gods=()):
    """对全部关系逐条计算条件结论；有结论者改写 effect 为 conditional。

    返回 (conditional_count, conditional_list)。无新输入时（各引用皆
    空且现代旺衰层未实际评分），全部关系保持 abstain，旧行为不变。
    """
    conditional = []
    for relation in relations:
        conclusions = _conditional_conclusions(
            relation, day_master=day_master,
            fuyi_candidate_stems=fuyi_candidate_stems,
            tiaohou_sequence_stems=tiaohou_sequence_stems,
            established_pattern_gods=established_pattern_gods,
            modern_strength_active=modern_strength_active,
            bingyao_roles=bingyao_roles,
            pattern_candidate_gods=pattern_candidate_gods)
        if not conclusions:
            continue
        verdicts = []
        rule_ids = []
        for conclusion in conclusions:
            if conclusion["verdict"] not in verdicts:
                verdicts.append(conclusion["verdict"])
            for rule_id in (conclusion.get("basis") or {}).get(
                    "rule_ids", ()):
                if rule_id not in rule_ids:
                    rule_ids.append(rule_id)
        relation["effect"] = {
            "verdict": verdicts[0],
            "status": "conditional",
            "reason": "；".join(c["reason"] for c in conclusions),
            "rule_ids": rule_ids,
            "basis": {"not_an_efficacy_verdict": True,
                      "conclusions": copy.deepcopy(conclusions)},
            "conditional_conclusions": copy.deepcopy(conclusions),
        }
        conditional.append({
            "relation_id": relation["id"], "scope": relation["scope"],
            "kind": relation["kind"], "verdicts": verdicts,
            "conclusions": copy.deepcopy(conclusions),
        })
    return len(conditional), conditional


def _validate_system_statement(statement, *, variant, system, label):
    if not isinstance(statement, dict):
        _fail("%s statement must be an object" % label)
    if statement.get("variant") != variant:
        _fail("%s statement variant drifted" % label)
    if system is not None and statement.get("system") != system:
        _fail("%s statement system drifted" % label)
    if statement.get("research_only") is not True:
        _fail("%s statement research_only drifted" % label)
    if statement.get("public_enabled") is not False:
        _fail("%s statement public_enabled drifted" % label)
    if statement.get("ai_enabled") is not False:
        _fail("%s statement ai_enabled drifted" % label)
    return copy.deepcopy(statement)


def _xiyong_contract(*, strength, tiaohou, bingyao, pattern, natal,
                     flow, day_master, strength_assessment=None,
                     pattern_v2=None):
    systems = {}

    # 扶抑：零行可建（S4 审定）。即使传入已审强弱因素，也只原样转述，
    # 不推出任何扶抑方向或喜用。
    fuyi = {
        "system": "fuyi",
        "status": "not_buildable",
        "adjudication_id": RULE_FUYI_SLICE,
        "adjudication_conclusion": "no_buildable_rows",
        "buildable_count": 0,
        "direction": None,
        "useful_god": None,
        "reason": ("扶抑最小切片审定结论为零行可建：方向表十行判别条件全是 "
                   "未阈值化程度词，F-1/F-3 总则带前提不可评估的反例/反转条款；"
                   "B2（2026-11-25）重开的三模型仍无可执行模型。"),
    }
    if strength is None:
        fuyi["consumed_strength_factors"] = None
        fuyi["strength_note"] = "未传入已审强弱因素；即使传入，扶抑仍零行可建。"
    else:
        if not isinstance(strength, dict):
            _fail("strength factors must be an object")
        if strength.get("factor_variant") != RULE_STRENGTH_FACTORS:
            _fail("strength factors variant drifted")
        if strength.get("overall_strength") is not None:
            _fail("strength factors carry an adjudicated overall strength")
        fuyi["consumed_strength_factors"] = copy.deepcopy(strength)
        fuyi["strength_note"] = ("已审强弱因素原样转述：overall_strength 恒为 None，"
                                 "只含月令/通根/透干等结构事实，不作强弱分类。")
    if strength_assessment is not None:
        # 新形态旺衰评估：古典分类、现代评分与 Q5/Q6 不确定性照录；
        # 扶抑本身仍零行可建——评估只作参照，不推出扶抑方向。
        summary = strength_assessment
        modern = summary.get("modern") or {}
        fuyi["consumed_strength_assessment"] = {
            "classical_classification": summary["classical"]["classification"],
            "classical_matched_predicate": summary["classical"][
                "matched_predicate"],
            "modern_verdict": modern.get("verdict"),
            "modern_score": modern.get("score"),
            "modern_classification_status": modern.get(
                "classification_status"),
            "modern_definite_classification": modern.get(
                "definite_classification"),
            "modern_uncertainty_flags": list(
                modern.get("uncertainty_flags") or []),
            "modern_abstain_reason": modern.get("abstain_reason"),
            "agreement_relationship": summary["agreement"]["relationship"],
        }
        assessment_note = (
            "另消费旺衰引擎评估：古典分类 %s、现代 %s（%s 分，分类状态 %s，"
            "不确定性 %s）；不确定性传导进扶抑，现代扶抑方向候选由 "
            "evaluate_fuyi 计算，本契约不重算、不给方向。"
            % (summary["classical"]["classification"],
               modern.get("verdict"), modern.get("score"),
               modern.get("classification_status"),
               ",".join(modern.get("uncertainty_flags") or []) or "无"))
        fuyi["strength_note"] = (
            fuyi.get("strength_note", "") + assessment_note
            if strength is not None
            else "未传入旧形态强弱因素。" + assessment_note)
    systems["fuyi"] = fuyi

    # 调候：原样转述 tiaohou_lookup 输出。
    if tiaohou is None:
        systems["tiaohou"] = {
            "system": "tiaohou", "status": "not_provided",
            "sequence": None,
            "reason": "未传入已审调候输出，本契约不补调候判断。",
        }
    else:
        statement = _validate_system_statement(
            tiaohou, variant="tiaohou-qiongtong-v1", system="tiaohou",
            label="tiaohou")
        if statement.get("day_master") != day_master:
            _fail("tiaohou statement disagrees on the day master")
        if statement.get("month_branch") != natal[1]["branch"]:
            _fail("tiaohou statement disagrees on the month branch")
        status = statement.get("status")
        if status == "matched":
            state = "presented"
        elif status == "not_applicable":
            state = "not_judgeable"
        else:
            _fail("tiaohou statement status drifted")
        systems["tiaohou"] = {
            "system": "tiaohou", "status": state,
            "statement": statement,
            "sequence_stems": [item["stem"] for item in statement.get("sequence", [])]
            if status == "matched" else [],
            "determination": None,
        }

    # 病药：原样转述 bingyao_lookup 输出（两对并列，不合并）。
    if bingyao is None:
        systems["bingyao"] = {
            "system": "bingyao", "status": "not_provided",
            "pairs": None,
            "reason": "未传入已审病药输出，本契约不补病药判断。",
        }
    else:
        statement = _validate_system_statement(
            bingyao, variant="bingyao-shenfeng-v1", system="bingyao",
            label="bingyao")
        if statement.get("day_master") != day_master:
            _fail("bingyao statement disagrees on the day master")
        if statement.get("determination") is not None:
            _fail("bingyao statement carries an adjudicated determination")
        pairs = statement.get("pairs")
        if type(pairs) is not list or len(pairs) != 2:
            _fail("bingyao statement pairs malformed")
        systems["bingyao"] = {
            "system": "bingyao", "status": "presented",
            "statement": statement,
            "pairs": [{"pair_id": pair.get("pair_id"),
                       "status": pair.get("status"),
                       "medicine_status": pair.get("medicine_status"),
                       "medicine_effect_status":
                           pair.get("medicine_effect_status")}
                      for pair in pairs],
            "determination": None,
        }

    # 格局用神：原样转述格局候选输出；定格字段恒为空，否则拒收。
    # 第二批：传入格局引擎 v2 输出时，消费其逐格状态与成立证据摘要；
    # 任何格都不输出用神（密封树中全部格的 useful_god 恒未审）。
    # 第三批集成：broken 单列（破格依据与原成立身份随记录携带），
    # 永不进入 established / eligible。
    if pattern_v2 is not None:
        eligible = []
        for record in pattern_v2["established"]:
            eligible.append({
                "pattern_key": record["pattern_key"],
                "pattern": record["pattern"],
                "state": "established",
                "rule_ids": list(record["rule_ids"]),
                "evidence_ids": list(record["evidence_ids"]),
                "useful_god": None,
                "useful_god_status": "no_reviewed_yongshen_rule",
                "reason": ("该格已成立（任氏寅月真格），但密封树中全部格的 "
                           "useful_god 恒未审：本契约不输出格局用神，只列"
                           "成立证据。"),
            })
        for record in pattern_v2["candidates"]:
            if not set(record["rule_ids"]) & VALIDATED_PATTERN_RULE_IDS:
                continue
            eligible.append({
                "pattern_key": record["pattern_key"],
                "pattern": record["pattern"],
                "state": "candidate",
                "rule_ids": list(record["rule_ids"]),
                "evidence_ids": list(record["evidence_ids"]),
                "useful_god": None,
                "useful_god_status": "no_reviewed_yongshen_rule",
                "reason": ("该格有 validated 候选规则，但密封树中全部格的 "
                           "useful_god 恒未审：本契约不输出格局用神，只列"
                           "条件事实证据。"),
            })
        broken_records = []
        for record in pattern_v2["broken"]:
            broken_records.append({
                "pattern_key": record["pattern_key"],
                "pattern": record["pattern"],
                "state": "broken",
                "rule_ids": list(record["rule_ids"]),
                "evidence_ids": list(record["evidence_ids"]),
                "broken_condition": record["broken_condition"],
                "broken_evidence_ids":
                    list(record["broken_evidence_ids"]),
                "original_state": record["original_state"],
                "original_pattern": record["original_pattern"],
                "useful_god": None,
                "useful_god_status": "no_reviewed_yongshen_rule",
                "reason": ("原格局已破格（伤官见官）：原为伤官格（任氏寅月"
                           "真格成立），正官在场破格，成立前提不再满足，"
                           "不输出格局用神，只列破格依据与原成立身份。"),
            })
        systems["pattern_yongshen"] = {
            "system": "pattern_yongshen",
            "status": "presented_from_pattern_v2",
            "statement": copy.deepcopy(pattern_v2["statement"]),
            "counts": dict(pattern_v2["counts"]),
            "established": [e["pattern"] for e in pattern_v2["established"]],
            "eligible": eligible,
            "conflicts": [
                {"pattern_key": c["pattern_key"], "pattern": c["pattern"],
                 "evidence_ids": list(c["evidence_ids"])}
                for c in pattern_v2["conflicts"]],
            "broken": broken_records,
            "broken_gaps": copy.deepcopy(pattern_v2["broken_gaps"]),
            "pattern": None,
            "useful_god": None,
            "determination": None,
        }
    elif pattern is None:
        systems["pattern_yongshen"] = {
            "system": "pattern_yongshen", "status": "not_provided",
            "pattern": None, "useful_god": None,
            "reason": ("未传入已审格局候选输出（格局候选需已执行的 trace，"
                       "本引擎不自行重算取格）；本契约不补格局判断。"),
        }
    else:
        if not isinstance(pattern, dict):
            _fail("pattern statement must be an object")
        if pattern.get("variant") != RULE_PATTERN_CANDIDATES:
            _fail("pattern statement variant drifted")
        determination = pattern.get("determination")
        if isinstance(determination, dict):
            if determination.get("pattern") is not None:
                _fail("pattern statement carries a determined pattern")
            if determination.get("true_false") is not None:
                _fail("pattern statement carries a true/false determination")
            if determination.get("useful_god") is not None:
                _fail("pattern statement carries a determined useful god")
        elif determination is not None:
            _fail("pattern statement determination malformed")
        if pattern.get("research_only") is not True:
            _fail("pattern statement research_only drifted")
        if pattern.get("public_enabled") is not False:
            _fail("pattern statement public_enabled drifted")
        if pattern.get("ai_enabled") is not False:
            _fail("pattern statement ai_enabled drifted")
        systems["pattern_yongshen"] = {
            "system": "pattern_yongshen",
            "status": pattern.get("status", "structural_observation_only"),
            "statement": copy.deepcopy(pattern),
            "pattern": None,
            "useful_god": None,
        }

    # 流年喜用：只完成数据契约与规则调用结构，完整推演待规则获批。
    flow_stem = flow["stem"]
    flow_ten_god = flow["stem_ten_god"]
    references = {}
    tiaohou_block = systems["tiaohou"]
    if tiaohou_block["status"] == "presented":
        references["tiaohou"] = {
            "flow_stem": flow_stem,
            "flow_stem_in_natal_tiaohou_sequence":
                flow_stem in tiaohou_block["sequence_stems"],
            "natal_tiaohou_sequence_stems":
                list(tiaohou_block["sequence_stems"]),
            "note": ("只报流年干是否在原局调候序列中这一存在性事实；"
                     "流年调候推演未获批，不据此取流年调候用神。"),
        }
    elif tiaohou_block["status"] == "not_judgeable":
        references["tiaohou"] = {
            "flow_stem": flow_stem,
            "flow_stem_in_natal_tiaohou_sequence": None,
            "note": "原局调候条目在审定文本中不存在，流年调候对照无序列可比。",
        }
    else:
        references["tiaohou"] = {
            "flow_stem": flow_stem,
            "flow_stem_in_natal_tiaohou_sequence": None,
            "note": "未传入原局调候输出，流年调候对照待原局调候传入后方可列举。",
        }
    bingyao_block = systems["bingyao"]
    if bingyao_block["status"] == "presented":
        pair_refs = []
        for pair in bingyao_block["statement"]["pairs"]:
            rule = pair.get("rule", {})
            pair_refs.append({
                "pair_id": pair.get("pair_id"),
                "flow_stem_ten_god": flow_ten_god,
                "flow_ten_god_role_in_pair":
                    ("subject" if flow_ten_god in rule.get("subject_gods", ())
                     else "disease" if flow_ten_god in rule.get("disease_gods", ())
                     else "medicine" if flow_ten_god in rule.get("medicine_gods", ())
                     else "none"),
                "pair_status": pair.get("status"),
                "note": ("只报流年干十神在该病药对中的角色这一结构对照；"
                         "流年病药推演未获批，不据此断流年病药去留。"),
            })
        references["bingyao"] = {"pairs": pair_refs}
    else:
        references["bingyao"] = {
            "pairs": None,
            "note": "未传入原局病药输出，流年病药对照待原局病药传入后方可列举。",
        }
    if strength_assessment is not None:
        modern = strength_assessment.get("modern") or {}
        references["fuyi"] = {
            "note": ("流年扶抑推演未获批：原局扶抑已零行可建；旺衰评估已消费"
                     "（古典 %s、现代 %s %s 分）只作参照，不据此取流年扶抑用神。"
                     % (strength_assessment["classical"]["classification"],
                        modern.get("verdict"), modern.get("score"))),
        }
    else:
        references["fuyi"] = {
            "note": "流年扶抑推演未获批：原局扶抑已零行可建，流年扶抑无可调用的规则。",
        }
    if pattern_v2 is not None:
        established = [e["pattern"] for e in pattern_v2["established"]]
        broken = [e["pattern"] for e in pattern_v2["broken"]]
        note = ("流年格局用神推演未获批：原局已成立 %s，但格局用神逐格"
                "规则未审，流年格局用神无可调用的规则。"
                % ("、".join(established) if established else "无格"))
        if broken:
            note += ("原局 %s 已破格（伤官见官），不作成立计；"
                     % "、".join(broken))
        references["pattern_yongshen"] = {
            "note": note,
            "established_patterns": established,
            "broken_patterns": broken,
        }
    else:
        references["pattern_yongshen"] = {
            "note": "流年格局用神推演未获批：原局定格未完成，流年格局用神无可调用的规则。",
        }
    annual_xiyong = {
        "status": "contract_only_pending_rules",
        "implemented": [
            "flow_year_ganzhi_and_ten_god",
            "flow_stem_presence_against_natal_tiaohou_sequence",
            "flow_stem_ten_god_role_against_bingyao_pairs",
            "rule_call_structure",
        ],
        "pending": [
            "annual_tiaohou_derivation",
            "annual_bingyao_derivation",
            "annual_fuyi_derivation",
            "annual_pattern_yongshen_derivation",
            "unified_annual_verdict",
        ],
        "pending_reason": ("流年喜用完整推演待对应规则获批后接入；现阶段只列数据契约 "
                           "与调用结构，不推演任何流年喜用。"),
        "flow_references": references,
        "derivation": None,
        "unified_verdict": None,
    }

    return {
        "variant": XIYONG_CONTRACT_VARIANT,
        "systems": systems,
        "annual_xiyong": annual_xiyong,
        "unified_verdict": None,
        "unified_verdict_status": "abstain_by_adjudication_TJ-013.2-A",
        "unified_verdict_note": ("TJ-013.2 裁决 A：四体系并列呈现、统一裁决拒判；"
                                 "本契约永不输出统一喜用神。"),
    }


def combine(natal_pillars, day_master, dayun_periods, target_year, *,
            strength=None, tiaohou=None, bingyao=None, pattern=None,
            xiyong=None, current_period_index=None,
            current_period_basis=None, variant=VARIANT):
    """组合原局、大运、流年三层，返回结构化 dict。

    ``natal_pillars``：四柱（ganzhi 字符串或 chart_from_pillars 形态的
    pillar 对象，年/月/日/时顺序）；``day_master``：日干；
    ``dayun_periods``：``candidate_sequence`` 行列表；
    ``target_year``：公历目标年份（1900..2098）。
    ``strength``：旧形态强弱因素（``factors()`` 输出）或新形态旺衰
    评估（``assess_strength`` 输出）；``tiaohou``/``bingyao``：
    已审调候/病药输出；``pattern``：旧形态格局候选输出或格局引擎
    v2 的 ``evaluate_all`` 输出；``xiyong``：喜用引擎的
    ``evaluate_xiyong`` 输出（传入时四体系与流年年度契约原样消费
    该输出，取代旧契约）。各体系缺省为 None，即该体系未传入。
    ``current_period_index`` 与 ``current_period_basis`` 须成对出现：
    调用方显式指定当期运及其依据（如已审交运区间），引擎只记录、
    不推导期位映射。
    """
    if variant != VARIANT:
        raise ValueError("Unsupported combination engine variant")
    if type(day_master) is not str or day_master not in STEMS:
        _fail("day_master must be one heavenly stem")
    if (current_period_index is None) != (current_period_basis is None):
        _fail("current_period_index and current_period_basis must be given together")
    if current_period_basis is not None and (
            type(current_period_basis) is not str or not current_period_basis):
        _fail("current_period_basis must be a non-empty string")

    natal = _normalize_pillars(natal_pillars, day_master)
    dayun = _normalize_dayun(dayun_periods, day_master)
    if current_period_index is not None and current_period_index not in {
            row["period_index"] for row in dayun}:
        _fail("current_period_index does not match any supplied dayun period")
    flow = _flow_year(target_year, day_master)
    month_branch = natal[1]["branch"]

    # 输入形态分流（只认两种已登记形态，余者 fail-closed）。
    strength_factors = None
    strength_assessment = None
    if strength is not None:
        if not isinstance(strength, dict):
            _fail("strength must be an object")
        if strength.get("variant") == STRENGTH_ENGINE_VARIANT:
            strength_assessment = _summarize_strength_assessment(
                strength, day_master, month_branch)
        elif strength.get("factor_variant") == RULE_STRENGTH_FACTORS:
            strength_factors = strength
        else:
            _fail("strength input variant drifted")
    pattern_legacy = None
    pattern_v2 = None
    if pattern is not None:
        if not isinstance(pattern, dict):
            _fail("pattern must be an object")
        if pattern.get("variant") == PATTERN_ENGINE_VARIANT_V2:
            pattern_v2 = _summarize_pattern_v2(
                pattern, day_master, month_branch)
        elif pattern.get("variant") == RULE_PATTERN_CANDIDATES:
            pattern_legacy = pattern
        else:
            _fail("pattern input variant drifted")

    natal_sides = [
        _side("natal", pillar=row["name"], stem=row["stem"],
              branch=row["branch"], stem_ten_god=row["stem_ten_god"])
        for row in natal
    ]
    flow_side = _side("flow_year", stem=flow["stem"], branch=flow["branch"],
                      stem_ten_god=flow["stem_ten_god"])

    counter = [0]
    relations = []

    # 1) 大运×原局（逐运）。
    for period in dayun:
        dayun_side = _side("dayun", period_index=period["period_index"],
                           stem=period["stem"], branch=period["branch"],
                           stem_ten_god=period["stem_ten_god"])
        for natal_side in natal_sides:
            relations.extend(_stem_pair_relations(
                counter, "dayun_x_natal", dayun_side, natal_side,
                period_index=period["period_index"],
                mapping_condition=None))
            relations.extend(_branch_pair_relations(
                counter, "dayun_x_natal", dayun_side, natal_side,
                period_index=period["period_index"],
                mapping_condition=None))
        branches = [(row["branch"], _side(
            "natal", pillar=row["name"], stem=row["stem"],
            branch=row["branch"], stem_ten_god=row["stem_ten_god"]))
            for row in natal]
        branches.append((period["branch"], dayun_side))
        relations.extend(_group_relations(
            counter, "dayun_x_natal", branches,
            period_index=period["period_index"], mapping_condition=None))

    # 2) 流年×原局。
    for natal_side in natal_sides:
        relations.extend(_stem_pair_relations(
            counter, "flow_x_natal", flow_side, natal_side,
            period_index=None, mapping_condition=None))
        relations.extend(_branch_pair_relations(
            counter, "flow_x_natal", flow_side, natal_side,
            period_index=None, mapping_condition=None))
    branches = [(row["branch"], _side(
        "natal", pillar=row["name"], stem=row["stem"],
        branch=row["branch"], stem_ten_god=row["stem_ten_god"]))
        for row in natal]
    branches.append((flow["branch"], flow_side))
    relations.extend(_group_relations(
        counter, "flow_x_natal", branches,
        period_index=None, mapping_condition=None))

    # 3) 大运×流年（逐运；期位映射条件逐条附注）。
    for period in dayun:
        dayun_side = _side("dayun", period_index=period["period_index"],
                           stem=period["stem"], branch=period["branch"],
                           stem_ten_god=period["stem_ten_god"])
        mapping = _mapping_condition(
            current_period_index, current_period_basis,
            period["period_index"])
        relations.extend(_stem_pair_relations(
            counter, "dayun_x_flow", dayun_side, flow_side,
            period_index=period["period_index"],
            mapping_condition=mapping))
        relations.extend(_branch_pair_relations(
            counter, "dayun_x_flow", dayun_side, flow_side,
            period_index=period["period_index"],
            mapping_condition=mapping))

    # 4) 跨三层之组（逐运）：原局四支＋大运支＋流年支中，同时含大运支
    # 与流年支的三合/方位会。只记两对 scope 覆盖不到之组；大运×流年
    # 对内仅两支，组关系在本对内无可形成之组（见 not_evaluated）。
    for period in dayun:
        dayun_side = _side("dayun", period_index=period["period_index"],
                           stem=period["stem"], branch=period["branch"],
                           stem_ten_god=period["stem_ten_god"])
        mapping = _mapping_condition(
            current_period_index, current_period_basis,
            period["period_index"])
        branches = [(period["branch"], dayun_side),
                    (flow["branch"], flow_side)]
        branches.extend(
            (row["branch"], _side(
                "natal", pillar=row["name"], stem=row["stem"],
                branch=row["branch"], stem_ten_god=row["stem_ten_god"]))
             for row in natal)
        relations.extend(_group_relations(
            counter, "dayun_x_flow_x_natal", branches,
            period_index=period["period_index"],
            mapping_condition=mapping,
            required_branches=(period["branch"], flow["branch"])))

    counts_by_scope = {}
    counts_by_kind = {}
    condition_statuses = {}
    for relation in relations:
        counts_by_scope[relation["scope"]] = (
            counts_by_scope.get(relation["scope"], 0) + 1)
        counts_by_kind[relation["kind"]] = (
            counts_by_kind.get(relation["kind"], 0) + 1)
        for condition in relation["conditions"]:
            condition_statuses[condition["status"]] = (
                condition_statuses.get(condition["status"], 0) + 1)
    period_count = len(dayun)
    scope_coverage = {
        "dayun_x_natal": {
            "stem_pairs_enumerated": 4 * period_count,
            "branch_pairs_enumerated": 4 * period_count,
            "group_evaluated": True,
            "group_branches": "natal_four_plus_dayun",
            "relations": counts_by_scope.get("dayun_x_natal", 0),
        },
        "flow_x_natal": {
            "stem_pairs_enumerated": 4,
            "branch_pairs_enumerated": 4,
            "group_evaluated": True,
            "group_branches": "natal_four_plus_flow",
            "relations": counts_by_scope.get("flow_x_natal", 0),
        },
        "dayun_x_flow": {
            "stem_pairs_enumerated": period_count,
            "branch_pairs_enumerated": period_count,
            "group_evaluated": True,
            "group_branches": "dayun_plus_flow_only_two_branches_no_group_formable",
            "relations": counts_by_scope.get("dayun_x_flow", 0),
        },
        "dayun_x_flow_x_natal": {
            "stem_pairs_enumerated": 0,
            "branch_pairs_enumerated": 0,
            "group_evaluated": True,
            "group_branches": "natal_four_plus_dayun_plus_flow_spanning_only",
            "relations": counts_by_scope.get("dayun_x_flow_x_natal", 0),
        },
    }

    # 每对已审地支关系命中/未命中对数：三表互不重叠，每对至多一行，
    # 故命中数即该 scope 的地支关系行数；未命中对仍计为已枚举（只
    # 是无已审关系行），不是未评估。
    for scope_name, coverage in scope_coverage.items():
        examined = coverage["branch_pairs_enumerated"]
        with_relation = sum(
            1 for relation in relations
            if relation["scope"] == scope_name
            and relation["kind"] in BRANCH_PAIR_KINDS)
        without = examined - with_relation
        if without < 0:
            _fail("branch relation rows exceed examined branch pairs")
        coverage["branch_pairs_with_reviewed_relation"] = with_relation
        coverage["branch_pairs_without_reviewed_relation"] = without

    if xiyong is not None:
        xiyong_out = _xiyong_from_engine(
            xiyong, day_master, month_branch)
        xiyong_block = {
            "variant": XIYONG_ENGINE_VARIANT,
            "systems": copy.deepcopy(xiyong_out["systems"]),
            "annual_xiyong": copy.deepcopy(xiyong_out["annual_xiyong"]),
            "unified_verdict": None,
            "unified_verdict_status": xiyong_out.get(
                "unified_verdict_status",
                "abstain_by_adjudication_TJ-013.2-A"),
            "unified_verdict_note": xiyong_out.get(
                "unified_verdict_note",
                "TJ-013.2 裁决 A：四体系并列呈现、统一裁决拒判；"
                "本契约永不输出统一喜用神。"),
        }
    else:
        legacy = _xiyong_contract(
            strength=strength_factors, tiaohou=tiaohou, bingyao=bingyao,
            pattern=pattern_legacy, natal=natal, flow=flow,
            day_master=day_master,
            strength_assessment=strength_assessment,
            pattern_v2=pattern_v2)
        xiyong_block = legacy

    # 条件结论的引用：扶抑现代候选干、调候序列干、已成立格之格神、
    # 病药已触发对的三角色类、格局候选格之格神。病药角色来源优先
    # 喜用引擎的病药体系（xiyong 传入时），否则用原局病药输出；
    # 两路形态均经 _bingyao_triggered_roles_from_pairs 严格核对。
    fuyi_candidate_stems = []
    tiaohou_sequence_stems = []
    bingyao_roles = []
    if xiyong is not None:
        fuyi_system = xiyong_block["systems"]["fuyi"]
        modern = fuyi_system.get("modern") or {}
        fuyi_candidate_stems = [
            g["stem"] for g in (modern.get("candidate_stems") or [])
            if isinstance(g, dict) and g.get("stem") in STEMS]
        tiaohou_system = xiyong_block["systems"]["tiaohou"]
        tiaohou_sequence_stems = [
            c["stem"] for c in (tiaohou_system.get("candidates") or [])
            if isinstance(c, dict) and c.get("stem") in STEMS]
        bingyao_system = xiyong_block["systems"]["bingyao"]
        if isinstance(bingyao_system.get("pairs"), list) \
                and bingyao_system["pairs"]:
            bingyao_roles = _bingyao_triggered_roles_from_pairs(
                bingyao_system["pairs"])
    else:
        if tiaohou is not None:
            tiaohou_sequence_stems = list(
                xiyong_block["systems"]["tiaohou"].get(
                    "sequence_stems") or [])
        if bingyao is not None:
            bingyao_roles = _bingyao_triggered_roles_from_pairs(
                bingyao["pairs"])
    established_pattern_gods = []
    if pattern_v2 is not None:
        for record in pattern_v2["established"]:
            name = record["pattern"] or ""
            god = name[:-1] if name.endswith("格") else name
            if god and god not in established_pattern_gods:
                established_pattern_gods.append(god)
    pattern_candidate_gods = _pattern_candidate_gods(pattern_v2)
    # C6 弃判传导：Q3-A 模型口径结论只在现代旺衰层实际评分时发出。
    # 现代层弃判（modern 为 None 或 components 为 None）时该分支弃
    # 判；调候、病药、格局结论独立，不受其影响。
    modern_strength_active = (
        strength_assessment is not None
        and strength_assessment.get("modern") is not None
        and strength_assessment["modern"].get("components") is not None)
    conditional_count, conditional_list = _apply_conditional_effects(
        relations, day_master=day_master,
        fuyi_candidate_stems=fuyi_candidate_stems,
        tiaohou_sequence_stems=tiaohou_sequence_stems,
        established_pattern_gods=established_pattern_gods,
        modern_strength_active=modern_strength_active,
        bingyao_roles=bingyao_roles,
        pattern_candidate_gods=pattern_candidate_gods)
    abstain_count = len(relations) - conditional_count
    verdict_counts = {"abstain": abstain_count}
    if conditional_count:
        verdict_counts["conditional"] = conditional_count

    if strength_assessment is not None:
        strength_block = strength_assessment
    elif strength_factors is not None:
        strength_block = {
            "status": "consumed",
            "input_kind": "strength_factors",
            "variant": RULE_STRENGTH_FACTORS,
            "overall_strength": strength_factors.get("overall_strength"),
            "root_positions_present": bool(
                (strength_factors.get("root_candidates") or {}).get(
                    "present_structurally")),
            "root_position_count": len(
                (strength_factors.get("root_candidates") or {}).get(
                    "positions") or []),
            "note": ("旧形态强弱因素：只含月令/通根/透干等结构事实，"
                     "overall_strength 恒为 None，不作强弱分类；新形态"
                     "评估（assess_strength）未传入。"),
        }
    else:
        strength_block = {
            "status": "not_provided",
            "note": "未传入强弱输出，本引擎不补强弱判断。",
        }
    if pattern_v2 is not None:
        pattern_block = pattern_v2
    elif pattern_legacy is not None:
        pattern_block = {
            "status": "consumed",
            "input_kind": "legacy_pattern_candidates",
            "variant": RULE_PATTERN_CANDIDATES,
            "statement": copy.deepcopy(pattern_legacy),
            "note": ("旧形态格局候选输出：只作结构观察，不含逐格状态与"
                     "成立证据；新形态评估（evaluate_all v2）未传入。"),
        }
    else:
        pattern_block = {
            "status": "not_provided",
            "note": "未传入格局输出，本引擎不补格局判断。",
        }

    consumed = {
        RULE_PILLARS, RULE_TEN_GODS, RULE_STEM_COMBINATIONS,
        RULE_SIX_HARMONIES, RULE_HARMS, RULE_CLASHES,
        RULE_TRIPLE_HARMONIES, RULE_DIRECTIONAL_MEETINGS,
        RULE_DAYUN_SEQUENCE,
    }
    if strength_factors is not None:
        consumed.add(RULE_STRENGTH_FACTORS)
    if strength_assessment is not None:
        consumed.add(RULE_STRENGTH_ENGINE)
        consumed.add(RULE_MODERN_STRENGTH_MODEL)
    if tiaohou is not None:
        consumed.add(RULE_TIAOHOU_ASSESSMENT)
    if bingyao is not None:
        consumed.add(RULE_BINGYAO_ASSESSMENT)
    if pattern_legacy is not None:
        consumed.add(RULE_PATTERN_CANDIDATES)
    if pattern_v2 is not None:
        consumed.add(RULE_PATTERN_ENGINE_V2)
    if xiyong is not None:
        consumed.add(RULE_XIYONG_ENGINE)
        xiyong_systems = xiyong_block["systems"]
        if xiyong_systems["tiaohou"].get("status") != "not_provided":
            consumed.add(RULE_TIAOHOU_ASSESSMENT)
        if xiyong_systems["bingyao"].get("status") != "not_provided":
            consumed.add(RULE_BINGYAO_ASSESSMENT)
        if xiyong_systems["fuyi"].get("basis") is not None:
            consumed.add(RULE_STRENGTH_ENGINE)
            consumed.add(RULE_MODERN_STRENGTH_MODEL)

    return {
        "variant": VARIANT,
        "research_only": True,
        "public_enabled": False,
        "ai_enabled": False,
        "natal": {
            "pillars": copy.deepcopy(natal),
            "day_master": day_master,
            "month_branch": natal[1]["branch"],
        },
        "dayun": {
            "periods": copy.deepcopy(dayun),
            "current_period_index": current_period_index,
            "current_period_basis": current_period_basis,
            "period_year_mapping": (
                "caller_selected" if current_period_index is not None
                else "not_determined"),
        },
        "flow_year": flow,
        "structural_relations": relations,
        "relation_summary": {
            "total": len(relations),
            "counts_by_scope": counts_by_scope,
            "counts_by_kind": counts_by_kind,
            "condition_status_counts": condition_statuses,
            "scope_coverage": scope_coverage,
            "not_evaluated": [
                {"kind": "branch_punishment",
                 "reason": ("刑不在已审地支关系表中（canonical "
                            "foundations_v1.json 的 earthly_branch_relations "
                            "无刑表），本引擎不评估刑。")},
                {"kind": "branch_group_dayun_x_flow",
                 "reason": ("大运×流年每运仅两支，三合/方位会需三支，组关"
                            "系在本对内无可形成之组；跨三层之组另见 "
                            "dayun_x_flow_x_natal scope。")},
            ],
        },
        "effects": {
            "overall_effect": None,
            "all_abstained": conditional_count == 0,
            "abstain_count": abstain_count,
            "conditional_count": conditional_count,
            "conditional_effects": conditional_list,
            "verdict_counts": verdict_counts,
            "note": (
                _ABSTAIN_EFFECT_REASON if conditional_count == 0 else
                "效力层：无依据者仍 abstain（TJ-017.2/TJ-023.3 阻塞）；有"
                "依据者只给条件结论（格神/扶抑候选干/调候序列/病药角色"
                "的存在性事实，或 Q3-A 模型口径），"
                "conditional_conclusions 逐条附依据；条件结论不是跨层"
                "效力断言，overall_effect 恒为 None。"),
        },
        "strength": strength_block,
        "pattern": pattern_block,
        "xiyong": xiyong_block,
        "consumed_rule_ids": sorted(consumed),
        "limitations": list(LIMITATIONS),
        "scope": ("原局×大运、流年×原局、大运×流年、跨三层之组的干支结构"
                  "关系与条件列举；效力无依据者拒判、有依据者只给条件结论；"
                  "喜用四体系并列、统一裁决恒为 None。"),
    }
