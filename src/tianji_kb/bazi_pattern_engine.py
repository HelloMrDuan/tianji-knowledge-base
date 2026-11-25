"""Pattern engine (TJ-0424): one evaluator per pattern, research_only.

Assembles the already-reviewed pattern material into a single per-pattern
assessment. It invents no new pattern rule: every state is either

- ``established`` -- only through the Ren-branch 寅月 true-pattern block
  (``ren_yin_true_pattern``, bazi.phase2.ren_yin_true_pattern, validated,
  Golden 15), the single reviewed determination in the sealed tree;
- ``candidate`` -- a reviewed structural observation, now carrying the
  per-pattern condition facts registered in the public Yuanhai
  section registrations (``bazi_yuanhai_{qisha,cai,shishang,
  zhengguan,yin,luren,cong}``): a condition's *presence* is computed
  from the pillars, its *efficacy* is never judged (every operative
  quote in those registrations routes through an unbuilt gate --
  strength, control/retention efficacy, combination, or the pattern's
  own establishment -- and each registration concludes determination
  is still None). A candidate therefore reports which classical
  conditions are in fact present and names the exact gate that blocks
  any further verdict;
- ``conflict`` -- two reviewed branches disagree and neither is adjudicated
  (正官 + 时七杀 s055 caution; 杂气原注 vs 三命 vs 子平真诠 Ch16,
  pattern_zaqi, validated Golden 6);
- ``not_judgeable`` -- no reviewed basis for this pattern on this chart.

``broken`` is now emitted through exactly one reviewed channel: 伤官见官
on a Ren D-1 established 伤官格 with 正官在场 (yh.sw_pattern_no_officer:
“如用伤官格者,支干、岁运,都要不见官星;如见官星,谓之伤官见官” --
the premise “用伤官格” is satisfied by the D-1 establishment, and
“见官星” is a fully presence-determined condition over 支干).
“官星” is read narrowly as 正官 (七杀在场 alone does not break;
whether 七杀 counts as 官星 here is unadjudicated). Every other
classical 破格 condition stays open: 财旺破印 needs the degree words
财多 / 乘旺, 制伏太过 needs 太过, 官杀去留 needs 去留操作与程度,
偏印夺食 needs 夺食效力 -- none has a threshold or a reviewed Golden
(see ``BROKEN_GAPS``; the 伤官见官 entry records its resolved channel).

Batch 3 pattern route 2 (TJ-0424, P1--P6, user adjudication 2026-11-25):
classical establishment beyond Ren D-1 stays impossible (every
七杀 / 财 / 食伤 establishment condition routes through an unbuilt
gate), so P1--P6 add a separate modern-engineering layer
(``modern_assessment``, model ``pattern-modern-p6-v1``) instead of
inventing classical rules: P6 身旺门 reuses the approved modern
strength model ``strength_model_modern_v1`` (definite verdicts only;
provisional / uncertain / abstain propagate as abstain) and a modern
伤尽标尺 grades 伤官 exhaustion from 官杀 presence (exposed vs
hidden); P1 modern establishment assessments for 七杀 / 财 / 食伤
combine the month-hidden candidate with those gates; P4 modern root
grades, an extreme-weak band and a triple-harmony assembly screen
(branches present + transforming stem visible) feed modern 从格
assessments; P5 modern broken flags (财旺破印 / 制伏太过 / 偏印夺食 /
比劫分夺) are presence/score flags only, never classical ``broken``.
The modern layer is additive: classical ``state`` is untouched except
for the single 伤官见官 channel above, and no modern verdict is ever
presented as a classical rule.

Classical rules and any modern engineering judgement are kept apart:
the only modern-engineering element is the narrow 从格候选屏 in
``evaluate_special``, which reuses the batch-1 strength engine's
screen definition (no roots, no visible support, >= 2 visible
relations all controls_me / i_generate) and is labelled
``model_kind="modern_engineering"``; it is a screen hit, never an
establishment. Strength is otherwise consumed only through
``bazi_strength.factors()`` and only as listed factors (roots,
visibility, month command); its ``overall_strength`` is always None
and is reported as unresolved wherever it would matter.

Governance: research_only=True, public=False, ai=False throughout.
Nothing here is a public API field and nothing is wired into
``public_projection``. 戊×巳 / 己×午 are always not_judgeable
(TJ-011.2: earth day-master pattern formation is unbuildable).

Batch 3 (TJ-0424, pattern route 2 -- this file only): condition-fact
coverage is widened strictly inside already-registered material
(hidden-official/killing 暗藏, official/seal/wealth absence facts,
officer exposed-vs-hidden, seal-controls-killing, blade seal/hour
wealth, zaqi month-hidden inventory + exposed positions, cong
example-structure matches, branch six-harmony / triple-harmony
screens); every per-pattern 破格缺口 is registered as a named entry
in ``BROKEN_GAPS`` (what basis is missing, which registered quotes,
which Golden is missing -- none: no reviewed Golden carries a 破格
condition) and surfaced per result as ``broken_gaps``; the two P6
blocking gates (general strength 身旺门, 伤尽程度标尺) are recorded
in ``BLOCKING_GATES`` and referenced by the gap entries, never
decided and never thresholded. No state machine changes: candidate
定型 (P1), 官杀去留 (P2), 杂气土格换算 (P3), 从格/化气成立 (P4),
破格规则 (P5) and the P6 gates all stay undecided per the round-2
33-question list; at that point ``broken`` was still never emitted.

P1--P6 batch (same file, v2 additive): the round-2 list is now
partially executed under the 2026-11-25 user adjudication -- one
classical ``broken`` channel (P5 伤官见官, premise established via
Ren D-1), a modern-engineering layer (P6 scales, P1 modern
establishment, P4 modern root / extreme-weak / assembly screens,
P5 modern broken flags, P2 retention observation, P3 conditional
土格换算 mapping). The classical P6 gates stay
``recorded_not_decided``: the modern scales are engineering
approximations and do not decide the classical gates.

Version note: ``PATTERN_ENGINE_VARIANT`` stays
``bazi-pattern-engine-v2`` on purpose. The combination engine pins
that exact string (``PATTERN_ENGINE_VARIANT_V2``) and refuses any
other pattern variant, so a bump to v3 would silently break
``combine()``'s pattern consumption; the bump belongs to a
coordinated change owned with the combination route (round-2 C1
area), not to this additive-evidence batch. Batch-3 changes are
additive evidence ids, one additive result key (``broken_gaps``),
and gap-table constants only -- no state, rule_id, governance-flag
or variant change.

P1--P6 batch (this file only): one additive result key
(``modern_assessment``, model ``pattern-modern-p6-v1``), one
classical ``broken`` channel (伤官见官 on a D-1 established 伤官格),
two additive classical evidence ids (``guansha_zhifu_trigger``,
``zaqi_earth_conversion_mapping``), and gap/gate status annotations.
Variant stays v2. Downstream note: the xiyong C1 check and the
combination engine now consume a ``broken`` pattern input per the
batch-3 integration contract -- state in STATES, variant v2,
governance flags research_only / public=False / ai=False, day stem /
month branch consistent, rule_ids carrying the reviewed Ren D-1 rule,
evidence carrying ``ren_yin_true_pattern`` +
``shangguan_sees_officer_broken``, and the additive structured fields
(``broken_condition`` / ``broken_evidence_ids`` /
``original_state='established'`` / ``original_pattern``) on the broken
result itself. A broken result is consumed only as broken: it never
enters an established list, never yields a pattern useful god, and its
pattern-yongshen branch abstains with the breaking reason stated.
"""

from .bazi_core import hidden_stems, reviewed_relations, ten_god
from .bazi_pattern import (
    EXPOSABLE_PILLARS,
    LUREN_ROUTE_VARIANT,
    LU_BRANCH,
    MISCELLANEOUS_BRANCHES,
    PATTERN_VARIANT,
    REN_BRANCH,
    REN_YIN_TRUE_VARIANT,
    YUANHAI_RESOURCE_MONTHS,
    candidates as _pattern_candidates,
    luren_route_lookup,
    month_pattern_route,
    month_pattern_zaqi,
    ren_yin_true_pattern,
    zaqi_selection_lookup,
)
from .bazi_strength import factors as _strength_factors
from .bazi_strength_engine import assess_strength as _assess_strength
from .foundations import BRANCHES, STEMS, stem_element

PATTERN_ENGINE_VARIANT = 'bazi-pattern-engine-v2'
# NOTE: deliberately not bumped to v3 in batch 3 (see module docstring):
# the combination engine pins this exact string and refuses any other
# pattern variant, so the bump is a coordinated change, not a local one.

# Modern-engineering layer (P1--P6 batch, user adjudication 2026-11-25).
# ``pattern-modern-p6-v1`` is an independent research model: its
# thresholds below are explicit engineering choices, not classical
# rules, and no verdict from it is ever presented as a classical
# establishment or break. The 身旺门 reuses the approved modern
# strength model ``strength_model_modern_v1`` (definite verdicts
# only); every other scale here is computed from factors() and
# presence counts with the thresholds written out in this module.
MODERN_MODEL_ID = 'pattern-modern-p6-v1'
# 制伏太过 (modern flag): control positions >= 2 AND >= 2x killing
# positions. ``太过`` has no classical threshold; these numbers are
# the engineering stand-in, labelled modern.
MODERN_OVER_CONTROL_MIN = 2
MODERN_OVER_CONTROL_RATIO = 2
# 财多 (modern flag): wealth positions >= 3 counts as abundant.
MODERN_WEALTH_ABUNDANT_AT = 3

# Named per-pattern 破格缺口表 (batch 3, P5 待裁定 -- 登记，不立规则).
# Each entry names the exact missing basis, the registered quotes it
# rests on, and the missing Golden (none: no reviewed Golden -- 寅月
# D-1 15 / 杂气 6 / 禄刃路线 9 / 正官 20 / 印绶 42 -- carries any
# 破格 condition). ``gate`` points at BLOCKING_GATES where the gap is
# one of the two P6 blocking gates. ``broken`` is never emitted on the
# strength of any entry here.
#
# P1--P6 batch: ``status`` (absent means ``open``) records what the
# adjudication changed. ``partially_resolved``: the classical channel
# now exists for the named premise (see ``resolved_channel``) while
# the general case stays open. ``modern_flag_only``: only a modern
# engineering flag exists (see ``modern_assessment``); the classical
# condition stays open. No entry is deleted: a partially resolved gap
# is still a gap for the unresolved cases.
BROKEN_GAPS = {
    'zhengguan': [
        {'id': 'bg-zhengguan-guansha-retention',
         'quotes': ('yh.gs_example_zhifu', 'yh.gt_clear'),
         'missing_basis': '官杀去留效力：去何星、清至何程度、行火乡制伏效力均未裁定',
         'missing_golden': '无：已审 Golden 均不含官杀去留破格条件'},
        {'id': 'bg-zhengguan-xingchong-fact-layer',
         'quotes': ('yh.zg_taboo_xingchong',),
         'missing_basis': '刑冲破害事实层未建：三刑规则不存在，冲/害事实层未接入正官忌句',
         'missing_golden': '无：已审 Golden 均不含刑冲破害破格条件'},
        {'id': 'bg-zhengguan-qingzhong-scale',
         'quotes': ('yh.zg_qingzhong',),
         'missing_basis': '轻重推测标尺：偏官便杂的轻重比较无阈值、无已裁定规则',
         'missing_golden': '无：已审 Golden 均不含轻重破格条件'},
        {'id': 'bg-zhengguan-shenwang',
         'quotes': ('yh.zg_shenwang_fa',),
         'missing_basis': '身旺则发经一般旺衰身旺门转手：身旺 / 身不弱无已裁定标尺',
         'missing_golden': '无：已审 Golden 均不含身旺破格条件',
         'gate': 'p6-shenwang-gate'},
    ],
    'qisha': [
        {'id': 'bg-qisha-control-moderation',
         'quotes': ('yh.qs_control_moderation',),
         'missing_basis': '制伏太过阈值：制之太过的程度词无标尺',
         'missing_golden': '无：已审 Golden 均不含制伏太过破格条件',
         'status': 'modern_flag_only',
         'modern_flag': '现代制伏太过旗标（pattern-modern-p6-v1）：'
                        '制伏在场数 >= 2 且 >= 2 倍七杀在场数；'
                        '古典太过阈值仍无。'},
        {'id': 'bg-qisha-shenwang-naming',
         'quotes': ('yh.qs_naming',),
         'missing_basis': '身旺有气为偏官、身弱无制为七杀的名称区分经一般旺衰身旺门转手',
         'missing_golden': '无：已审 Golden 均不含身旺命名破格条件',
         'gate': 'p6-shenwang-gate'},
        {'id': 'bg-qisha-combined-killing',
         'quotes': ('yh.qs_jia_example_control',),
         'missing_basis': '合杀效力：贪合忘杀的合化效力未裁定',
         'missing_golden': '无：已审 Golden 均不含合杀破格条件'},
    ],
    'zhengyin': [
        {'id': 'bg-resource-wealth-breaks-seal',
         'quotes': ('yh.yn_wealth_floods', 'yh.yn_wealth_arrives_floods'),
         'missing_basis': '财破印效力：财多乘旺、财来乘旺的程度与破印效力均未裁定',
         'missing_golden': '无：已审 Golden 均不含财破印破格条件',
         'status': 'modern_flag_only',
         'modern_flag': '现代财旺破印旗标（pattern-modern-p6-v1）：'
                        '财在场数 >= 3 且现代身旺门为 strong；'
                        '古典财多 / 乘旺程度与破印效力仍无。'},
        {'id': 'bg-resource-shangguan-breaks-seal',
         'quotes': ('yh.zg_shenwang_fa',),
         'missing_basis': '伤官破印效力：若无伤官破印一句的破印效力未裁定',
         'missing_golden': '无：已审 Golden 均不含伤官破印破格条件'},
    ],
    'pianyin': [
        {'id': 'bg-resource-wealth-breaks-seal',
         'quotes': ('yh.yn_wealth_floods', 'yh.yn_wealth_arrives_floods'),
         'missing_basis': '财破印效力：财多乘旺、财来乘旺的程度与破印效力均未裁定',
         'missing_golden': '无：已审 Golden 均不含财破印破格条件',
         'status': 'modern_flag_only',
         'modern_flag': '现代财旺破印旗标（pattern-modern-p6-v1）：'
                        '财在场数 >= 3 且现代身旺门为 strong；'
                        '古典财多 / 乘旺程度与破印效力仍无。'},
        {'id': 'bg-resource-shangguan-breaks-seal',
         'quotes': ('yh.zg_shenwang_fa',),
         'missing_basis': '伤官破印效力：若无伤官破印一句的破印效力未裁定',
         'missing_golden': '无：已审 Golden 均不含伤官破印破格条件'},
        {'id': 'bg-resource-seal-seizes-food',
         'quotes': ('yh.ds_mechanism',),
         'missing_basis': '偏印夺食效力：倒食夺食的效力未裁定',
         'missing_golden': '无：已审 Golden 均不含倒食夺食破格条件'},
        {'id': 'bg-resource-seal-controls-killing',
         'quotes': ('yh.ds_killing_control',),
         'missing_basis': '偏印制杀与破制效力：食神制杀效力与见水破制效力均未裁定',
         'missing_golden': '无：已审 Golden 均不含制杀破格条件'},
    ],
    'zhengcai': [
        {'id': 'bg-wealth-robbery',
         'quotes': ('yh.pc_definition',),
         'missing_basis': '比劫分夺效力：只恐兄弟姊妹有夺之的分夺效力未裁定',
         'missing_golden': '无：已审 Golden 均不含分夺破格条件',
         'status': 'modern_flag_only',
         'modern_flag': '现代比劫分夺旗标（pattern-modern-p6-v1）：'
                        '比劫在场即标旗；古典分夺效力仍无。'},
        {'id': 'bg-wealth-many-officer',
         'quotes': ('yh.zc_many_transform_officer',),
         'missing_basis': '财多化官效力：财多自化作官的身健门与化官效力均未裁定',
         'missing_golden': '无：已审 Golden 均不含财多化官破格条件',
         'gate': 'p6-shenwang-gate'},
        {'id': 'bg-wealth-timely',
         'quotes': ('yh.zc_timely',),
         'missing_basis': '财得时阈值：财要得时的得时判断无阈值、无已裁定规则',
         'missing_golden': '无：已审 Golden 均不含得时破格条件'},
    ],
    'piancai': [
        {'id': 'bg-wealth-robbery',
         'quotes': ('yh.pc_definition',),
         'missing_basis': '比劫分夺效力：只恐兄弟姊妹有夺之的分夺效力未裁定',
         'missing_golden': '无：已审 Golden 均不含分夺破格条件',
         'status': 'modern_flag_only',
         'modern_flag': '现代比劫分夺旗标（pattern-modern-p6-v1）：'
                        '比劫在场即标旗；古典分夺效力仍无。'},
        {'id': 'bg-wealth-many-officer',
         'quotes': ('yh.zc_many_transform_officer',),
         'missing_basis': '财多化官效力：财多自化作官的身健门与化官效力均未裁定',
         'missing_golden': '无：已审 Golden 均不含财多化官破格条件',
         'gate': 'p6-shenwang-gate'},
        {'id': 'bg-wealth-timely',
         'quotes': ('yh.zc_timely',),
         'missing_basis': '财得时阈值：财要得时的得时判断无阈值、无已裁定规则',
         'missing_golden': '无：已审 Golden 均不含得时破格条件'},
    ],
    'shishen': [
        {'id': 'bg-food-seized-by-seal',
         'quotes': ('yh.ds_mechanism',),
         'missing_basis': '倒食夺食效力：偏印夺食的效力未裁定',
         'missing_golden': '无：已审 Golden 均不含倒食夺食破格条件',
         'status': 'modern_flag_only',
         'modern_flag': '现代偏印夺食旗标（pattern-modern-p6-v1）：'
                        '偏印在场即标旗（偏印克食神为五行结构事实）；'
                        '古典夺食效力仍无。'},
        {'id': 'bg-food-single-unclear',
         'quotes': ('yh.ss_single_position',),
         'missing_basis': '独一位之外多见如何未定，然终亦不清的清浊判断不存在',
         'missing_golden': '无：已审 Golden 均不含食神多见破格条件'},
    ],
    'shangguan': [
        {'id': 'bg-food-shangguan-sees-officer',
         'quotes': ('yh.sw_pattern_no_officer',),
         'missing_basis': '伤官见官效力：见官星谓之伤官见官的效力未裁定——'
                          '未成立前提（仅月藏候选）的盘仍无破格通道；'
                          '成立前提经任氏寅月真格满足的盘已有破格通道',
         'missing_golden': '寅月 D-1 Golden f2-boundary-exact（成立伤官格 + '
                           '官星在场）现行使该通道；其余已审 Golden 均不含'
                           '伤官见官破格条件',
         'status': 'partially_resolved',
         'resolved_channel': '任氏寅月真格成立的伤官格 + 正官在场（支干）'
                             '→ classical broken（yh.sw_pattern_no_officer；'
                             '“官星”从窄读为正官，七杀在场 alone 不破格）'},
        {'id': 'bg-food-shangjin-scale',
         'quotes': ('yh.sw_exhaust_core',),
         'missing_basis': '伤尽程度标尺：伤官务要伤尽的程度词无标尺',
         'missing_golden': '无：已审 Golden 均不含伤尽破格条件',
         'gate': 'p6-shangjin-scale'},
    ],
    'jianlu': [
        {'id': 'bg-luren-no-rule',
         'quotes': (),
         'missing_basis': '《论禄》未逐节登记：建禄成格 / 破格皆无已审依据',
         'missing_golden': '无：已审 Golden 均不含建禄破格条件'},
    ],
    'yangren': [
        {'id': 'bg-luren-blade-removal',
         'quotes': ('yh.rr_body_strong_remove',),
         'missing_basis': '去刃效力：阳刃要身旺的身旺门与何物去刃、去之程度均未裁定',
         'missing_golden': '无：已审 Golden 均不含去刃破格条件',
         'gate': 'p6-shenwang-gate'},
        {'id': 'bg-luren-blade-relations',
         'quotes': ('yh.yr_preferences',),
         'missing_basis': '支关系效力层：忌反吟伏吟、忌魁罡、忌三合的效力层未建',
         'missing_golden': '无：已审 Golden 均不含刃支关系破格条件'},
    ],
    'zaqi': [
        {'id': 'bg-zaqi-no-rule',
         'quotes': (),
         'missing_basis': '杂气破格条件无已审依据',
         'missing_golden': '无：已审 Golden 均不含杂气破格条件'},
    ],
    'special': [
        {'id': 'bg-special-no-rule',
         'quotes': (),
         'missing_basis': '从格 / 化气破格条件无已审依据',
         'missing_golden': '无：已审 Golden 均不含从格 / 化气破格条件'},
    ],
    'bijian': [
        {'id': 'bg-extra-no-rule',
         'quotes': (),
         'missing_basis': '比肩破格条件无已审依据（比肩格只见于任氏 D-1 机械换算名）',
         'missing_golden': '无：已审 Golden 均不含比肩破格条件'},
    ],
    'jiecai': [
        {'id': 'bg-extra-no-rule',
         'quotes': (),
         'missing_basis': '劫财破格条件无已审依据（劫财格只见于任氏 D-1 机械换算名）',
         'missing_golden': '无：已审 Golden 均不含劫财破格条件'},
    ],
}

# P6 两门堵点登记（第二轮 33 问 P6 待裁定 -- 只记为堵点，不立标尺、
# 不阈值化、不作任何程度判断）。堵住七杀、食伤、印绶、禄刃几乎全部
# 成立通道；不裁定则上述格局永远止于候选。
#
# P1--P6 batch: the classical gates stay ``recorded_not_decided``.
# ``modern_scale`` names the separate modern-engineering scale that
# now exists for the same degree words (model
# ``pattern-modern-p6-v1``); it is an engineering approximation and
# does NOT decide the classical gate, which is why the status does
# not change.
BLOCKING_GATES = {
    'p6-shenwang-gate': {
        'question': 'P6',
        'name': '一般旺衰身旺门',
        'blocks': ('qisha', 'zhengcai', 'piancai', 'yangren',
                   'zhengguan'),
        'status': 'recorded_not_decided',
        'modern_scale': MODERN_MODEL_ID,
        'note': '身旺 / 身弱 / 身健等程度词无已裁定标尺；一般旺衰不存在，'
                '故经此门转手的一切成立与破格判断均不可执行。'
                '现代身旺门（strength_model_modern_v1 definite verdict）'
                '另见各结果 modern_assessment，不替古典门裁决。',
    },
    'p6-shangjin-scale': {
        'question': 'P6',
        'name': '伤尽程度标尺',
        'blocks': ('shangguan',),
        'status': 'recorded_not_decided',
        'modern_scale': MODERN_MODEL_ID,
        'note': '伤官务要伤尽的“尽”无已裁定程度标尺；伤尽成立与伤官'
                '见官破格均不可执行。现代伤尽标尺（官杀在场与否、'
                '透/藏区分）另见伤官结果 modern_assessment，不替'
                '古典标尺裁决。',
    },
}

# pattern_key -> (Chinese pattern name, ten god or None)
PATTERNS = (
    ('zhengguan', '正官', '正官'),
    ('qisha', '七杀', '七杀'),
    ('zhengyin', '正印', '正印'),
    ('pianyin', '偏印', '偏印'),
    ('zhengcai', '正财', '正财'),
    ('piancai', '偏财', '偏财'),
    ('shishen', '食神', '食神'),
    ('shangguan', '伤官', '伤官'),
    ('jianlu', '建禄', None),
    ('yangren', '阳刃', None),
    ('zaqi', '杂气', None),
    ('special', '特殊格局', None),
)
PATTERN_NAMES = {key: name for key, name, _ in PATTERNS}
TEN_GOD_PATTERNS = {god: key for key, _, god in PATTERNS if god is not None}
# Ren D-1 can also mechanically establish 比肩格 / 劫财格 (commander stem
# identical to the day master); those names are outside the reviewed
# public eight-name whitelist and are reported here as research-only
# extras, never as one of the twelve patterns above.
EXTRA_TEN_GOD_PATTERNS = {'比肩': 'bijian', '劫财': 'jiecai'}
EXTRA_PATTERN_NAMES = {'bijian': '比肩', 'jiecai': '劫财'}

# Earth day-master pattern formation is unbuildable (TJ-011.2).
EARTH_UNJUDGEABLE = (('戊', '巳'), ('己', '午'))

STATES = ('candidate', 'established', 'broken', 'conflict', 'not_judgeable')


PILLAR_CN = {'year': '年', 'month': '月', 'day': '日', 'hour': '时'}

# 《论七杀》七日生主杀列举（yh.qs_seven_days）：日柱有限列举，
# 非成格 / 破格条件。
SEVEN_KILLING_DAYS = ('甲申', '乙酉', '丁丑', '戊寅', '己卯', '辛未', '癸未')

# 《论日刃》日刃三柱（yh.rr_same_method）：日刃与阳刃同法。
DAY_REN_PILLARS = ('戊午', '丙午', '壬子')


def _ev(evidence_id, detail):
    return {'id': evidence_id, 'detail': detail}


def _result(ctx, pattern_key, state, evidence, limitations, *, rule_ids=(),
              broken_info=None):
    name = PATTERN_NAMES.get(pattern_key) or EXTRA_PATTERN_NAMES[pattern_key]
    modern, extra_evidence = _modern_assessment(ctx, pattern_key, state)
    out = {
        'pattern': name,
        'pattern_key': pattern_key,
        'state': state,
        'evidence': list(evidence) + extra_evidence,
        'limitations': list(limitations),
        'rule_ids': list(rule_ids),
        # Named broken-gap table for this pattern (batch 3): gap ids
        # from BROKEN_GAPS; registration only, never a broken verdict.
        'broken_gaps': [g['id'] for g in BROKEN_GAPS.get(pattern_key, [])],
        # P1--P6 modern layer (additive): None on the TJ-011.2 earth
        # gate; never changes the classical ``state``.
        'modern_assessment': modern,
        'research_only': True,
        'public': False,
        'ai': False,
        'variant': PATTERN_ENGINE_VARIANT,
        'day_stem': ctx.day_stem,
        'month_branch': ctx.month_branch,
    }
    # Broken contract (batch 3 integration): a ``broken`` result must
    # always carry its structured breaking basis and original identity
    # (additive keys, so downstream can consume it as broken -- never
    # as established). ``broken_info`` on a non-broken result, or a
    # broken result without it, is an internal inconsistency: fail
    # closed rather than emit a bare broken verdict.
    if broken_info is not None:
        if state != 'broken':
            raise ValueError('broken_info given for a non-broken result')
        for field in ('broken_condition', 'broken_evidence_ids',
                      'original_state', 'original_pattern'):
            if field not in broken_info:
                raise ValueError('broken result lacks %s' % field)
        out.update(broken_info)
    elif state == 'broken':
        raise ValueError('broken result lacks broken_info')
    return out


def _modern_strength_or_abstain(pillars, day_stem):
    """Approved modern strength model, definite verdicts only.

    Returns the ``modern`` dict of :func:`assess_strength` with its
    verdict restricted to definite classifications: a provisional
    (土/丁日主, Q5) or uncertain (四库月得令记 0, Q6) score is
    reported as abstain, never as a definite 身旺门 verdict. Any
    error (including missing canonical data) abstains the modern
    layer instead of failing the classical path.
    """
    try:
        assessed = _assess_strength(pillars, day_stem)
    except Exception as error:  # noqa: BLE001 - fail-closed abstain
        return {'model_id': 'strength_model_modern_v1',
                'model_kind': 'modern_engineering',
                'verdict': 'abstain', 'score': None, 'score_band': None,
                'classification_status': 'error',
                'definite_classification': None,
                'uncertainty_flags': [],
                'abstain_reason': 'modern_model_error',
                'abstain_detail': '%s: %s' % (type(error).__name__, error)}
    modern = assessed.get('modern') or {}
    if modern.get('verdict') == 'abstain':
        return modern
    if modern.get('classification_status') != 'definite':
        out = dict(modern)
        out['verdict'] = 'abstain'
        out['score_band'] = None
        out['definite_classification'] = None
        out['abstain_reason'] = 'modern_model_not_definite'
        out['abstain_detail'] = (
            '现代模型分类不确定（classification_status=%s，%s）：'
            '暂定分不作确定旺衰分类，身旺门弃判。'
            % (modern.get('classification_status'),
               '、'.join(modern.get('uncertainty_flags') or [])
               or '无不确定标记'))
        return out
    return modern


def _modern_shenwang(ctx):
    """P6 modern 身旺门: the approved modern model's definite verdict,
    or abstain with the model's own reason."""
    modern = ctx.modern_strength or {}
    return {
        'source_model': 'strength_model_modern_v1',
        'verdict': modern.get('verdict', 'abstain'),
        'score': modern.get('score'),
        'score_band': modern.get('score_band'),
        'classification_status': modern.get('classification_status'),
        'uncertainty_flags': list(modern.get('uncertainty_flags') or []),
        'abstain_reason': modern.get('abstain_reason'),
        'abstain_detail': modern.get('abstain_detail'),
    }


def _modern_root_grade(ctx):
    """P4 modern root grade (engineering grades, not classical 根级).

    Classical 根级 (轻根 / 墓库之根 / 待定格) is unadjudicated; these
    grades only count structural root candidates from factors().
    """
    roots = ctx.structural_roots()
    same_stem = any(row.get('same_stem') for row in roots)
    if not roots:
        grade = 'none'
    elif same_stem:
        grade = 'same_stem'
    elif len(roots) == 1:
        grade = 'single'
    else:
        grade = 'multiple'
    return {'grade': grade, 'root_count': len(roots),
            'same_stem_root': bool(same_stem),
            'note': '现代工程根级：只计结构根候选数与同干根；'
                    '轻根 / 墓库之根 / 待定格等古典根级未裁定。'}


def _modern_extreme_weak(ctx):
    """P4 modern 极弱档: no roots, no visible support, >= 2 opposing
    visible stems. An engineering band, not a classical 极弱裁定."""
    roots = ctx.structural_roots()
    kinds = ctx.visible_relation_kinds()
    support = [k for k in kinds if k in ('generates_me', 'same_element')]
    opposing = [k for k in kinds
                if k in ('controls_me', 'i_generate', 'i_control')]
    hit = not roots and not support and len(opposing) >= 2
    return {'band': 'extreme_weak_modern' if hit else 'not_extreme_weak',
            'root_count': len(roots),
            'visible_support_count': len(support),
            'visible_opposing_count': len(opposing),
            'note': '现代工程极弱档：无结构根、无显干生扶、显干克泄耗 '
                    '>= 2；古典极弱档无定义。'}


def _modern_shangjin(ctx):
    """P6 modern 伤尽标尺: 伤官 exhaustion graded from 官杀 presence.

    exhausted_modern: 伤官在场 + 正官/七杀全无. not_exhausted_modern:
    伤官在场 + 官/杀在场 (exposed vs hidden recorded, after
    yh.sw_not_exhausted_officer 露/藏区分). ungraded: 伤官不在场.
    The classical 伤尽程度标尺 stays undecided; this is the
    engineering scale, labelled modern.
    """
    food = ctx.god_positions('伤官')
    if not food:
        return {'grade': 'ungraded', 'shangguan_count': 0,
                'officer_count': 0, 'officer_exposed': False,
                'officer_hidden_only': False,
                'note': '伤官不在场：现代伤尽标尺不分级。'}
    officer = ctx.god_positions('正官') + ctx.god_positions('七杀')
    exposed = any(p['kind'] == 'visible' for p in officer)
    return {'grade': 'exhausted_modern' if not officer
            else 'not_exhausted_modern',
            'shangguan_count': len(food),
            'officer_count': len(officer),
            'officer_exposed': exposed,
            'officer_hidden_only': bool(officer) and not exposed,
            'note': '现代伤尽标尺：伤尽 = 伤官在场且官杀全无；'
                    '官杀在场（透/藏）即不尽。古典伤尽标尺未裁定。'}


def _modern_control_degree(ctx):
    """P5 modern 制伏程度: control (食神+伤官) vs killing counts.

    over_control_modern: control >= MODERN_OVER_CONTROL_MIN and
    control >= MODERN_OVER_CONTROL_RATIO * killing -- engineering
    stand-ins for the classical 太过, which has no threshold.
    """
    killing = ctx.god_positions('七杀')
    control = ctx.god_positions('食神') + ctx.god_positions('伤官')
    k, c = len(killing), len(control)
    if k == 0:
        grade = 'no_killing'
    elif c == 0:
        grade = 'no_control'
    elif (c >= MODERN_OVER_CONTROL_MIN
          and c >= MODERN_OVER_CONTROL_RATIO * k):
        grade = 'over_control_modern'
    elif c < k:
        grade = 'under_control'
    elif c == k:
        grade = 'matched'
    else:
        grade = 'strong_control'
    return {'grade': grade, 'killing_count': k, 'control_count': c,
            'note': '现代制伏程度：太过旗标阈值见 MODERN_OVER_CONTROL_*；'
                    '古典制伏太过无标尺。'}


def _modern_wealth_degree(ctx, god):
    """P5 modern 财多标尺: wealth positions counted per god."""
    n = len(ctx.god_positions(god))
    grade = ('absent' if n == 0 else 'single' if n == 1
             else 'multiple' if n == 2 else 'abundant_modern')
    return {'grade': grade, 'count': n,
            'note': '现代财多标尺：在场数 >= %d 为 abundant_modern；'
                    '古典财多无阈值。' % MODERN_WEALTH_ABUNDANT_AT}


def _cong_modern(ctx):
    """P4 modern 从格 screens: root grade + extreme-weak band +
    triple-harmony assembly (branches present + transforming stem
    visible). 会局成局古典判定不存在；this screen is modern only."""
    roots = ctx.structural_roots()
    killing = ctx.god_positions('七杀')
    control = ctx.god_positions('食神') + ctx.god_positions('伤官')
    seal = ctx.god_positions('正印') + ctx.god_positions('偏印')
    wealth = ctx.god_positions('正财') + ctx.god_positions('偏财')
    robbery = ctx.god_positions('比肩') + ctx.god_positions('劫财')
    extreme = _modern_extreme_weak(ctx)
    assemblies = []
    for pair in ctx.branch_triple_harmonies:
        element = pair['traditional_result_element']
        stems = ([s for s in ctx.visible_stems.values()
                  if stem_element(s) == element]
                 if element else [])
        assemblies.append({
            'pillars': list(pair['pillars']),
            'branches': list(pair['branches']),
            'result_element': element,
            'transforming_stems': stems,
            'assembly_modern': 'hit' if stems else 'miss'})

    def _verdict(screen_conditions, screen_missing):
        if not screen_missing:
            return {'verdict': 'established_modern',
                    'conditions': screen_conditions, 'missing': [],
                    'note': '现代从格成立评估：所列现代屏条件全满足；'
                            '古典从格成立（会杀 / 会财成局）未裁定。'}
        return {'verdict': 'not_established_modern',
                'conditions': screen_conditions,
                'missing': screen_missing,
                'note': '现代从格成立评估：所列现代屏条件未全满足；'
                        '古典从格成立未裁定。'}

    congsha_missing = []
    congsha_conditions = []
    if killing:
        congsha_conditions.append('killing_present')
    else:
        congsha_missing.append('killing_absent')
    if not roots:
        congsha_conditions.append('root_grade_none')
    else:
        congsha_missing.append('root_present')
    if not control:
        congsha_conditions.append('no_control')
    else:
        congsha_missing.append('control_present')
    if not seal:
        congsha_conditions.append('no_seal_rescue')
    else:
        congsha_missing.append('seal_rescue_present')
    if not robbery:
        congsha_conditions.append('no_robbery_rescue')
    else:
        congsha_missing.append('robbery_rescue_present')
    if extreme['band'] == 'extreme_weak_modern':
        congsha_conditions.append('extreme_weak_band')
    else:
        congsha_missing.append('extreme_weak_band_absent')

    congcai_missing = []
    congcai_conditions = []
    if wealth:
        congcai_conditions.append('wealth_present')
    else:
        congcai_missing.append('wealth_absent')
    if not roots:
        congcai_conditions.append('root_grade_none')
    else:
        congcai_missing.append('root_present')
    if not killing:
        congcai_conditions.append('no_killing')
    else:
        congcai_missing.append('killing_present')
    if not robbery:
        congcai_conditions.append('no_robbery')
    else:
        congcai_missing.append('robbery_present')
    if extreme['band'] == 'extreme_weak_modern':
        congcai_conditions.append('extreme_weak_band')
    else:
        congcai_missing.append('extreme_weak_band_absent')

    return {'assemblies': assemblies,
            'congsha': _verdict(congsha_conditions, congsha_missing),
            'congcai': _verdict(congcai_conditions, congcai_missing),
            'note': '现代会局屏：三合支齐备 + 化神透干为 hit；只记'
                    '现代屏命中，不作古典会局成局。'}


def _modern_guansha_retention(ctx):
    """P2 modern 去留 observation bundle (observation only).

    Records the yh.gs_example_zhifu trigger (金 / 庚申在场), control
    presence and the modern shenwang verdict. 去留操作与效力未裁定;
    行火乡 is a 大运 condition, outside the natal chart.
    """
    officials = ctx.god_positions('正官')
    killings = ctx.god_positions('七杀')
    gold_stems = [s for s in ctx.stems if stem_element(s) == '金']
    gold_branches = [b for b in ctx.branches if b in ('申', '酉')]
    gold_hidden = [row['stem'] for row in ctx.all_hidden
                   if stem_element(row['stem']) == '金']
    geng_shen = ('庚' in ctx.stems) or ('申' in ctx.branches)
    control = ctx.god_positions('食神') + ctx.god_positions('伤官')
    shenwang = _modern_shenwang(ctx)
    return {
        'verdict': 'observation_only',
        'officer_count': len(officials),
        'killing_count': len(killings),
        'zhifu_trigger': {
            'gold_present': bool(gold_stems or gold_branches or gold_hidden),
            'gold_stems': gold_stems,
            'gold_branches': gold_branches,
            'gold_hidden_stems': gold_hidden,
            'geng_shen_present': geng_shen},
        'control_present': bool(control),
        'control_positions': len(control),
        'shenwang_verdict': shenwang['verdict'],
        'note': '现代去留观察束：只并列触发条件（有金 / 庚申）、制伏'
                '在场与现代身旺门；去何星、清至何程度、行火乡制伏'
                '效力均未裁定，不作去留裁决。'}


_P1_GODS = {'qisha': '七杀', 'zhengcai': '正财', 'piancai': '偏财',
            'shishen': '食神', 'shangguan': '伤官'}


def _modern_establishment(ctx, pattern_key, state):
    """P1 modern establishment assessments for 七杀 / 财 / 食伤.

    Each verdict combines the month-hidden candidate with the modern
    gates (P6 身旺门 / 伤尽标尺 / count conditions). ``established``
    (classical, Ren D-1) short-circuits to ``classical_established``;
    a shenwang abstain abstains any verdict that needs it. Returns
    None for patterns outside the P1 five.
    """
    if pattern_key not in _P1_GODS:
        return None
    god = _P1_GODS[pattern_key]
    if state == 'established':
        return {'verdict': 'classical_established',
                'conditions': ['ren_yin_true_pattern'], 'missing': [],
                'note': '古典已成立（任氏寅月真格）：现代成立评估不再重复。'}
    candidate = ctx.month_hidden_god(god) is not None
    shenwang = _modern_shenwang(ctx)
    conditions = []
    missing = []
    needs_shenwang = pattern_key != 'shangguan'
    if candidate:
        conditions.append('month_hidden_god')
    else:
        missing.append('no_month_hidden_god')
    if pattern_key == 'qisha':
        control = _modern_control_degree(ctx)
        if shenwang['verdict'] == 'strong':
            conditions.append('shenwang_strong')
        else:
            missing.append('shenwang_not_strong')
        if control['control_count'] > 0:
            conditions.append('control_present')
        else:
            missing.append('control_absent')
        if control['grade'] != 'over_control_modern':
            conditions.append('not_over_control')
        else:
            missing.append('over_control_modern')
    elif pattern_key in ('zhengcai', 'piancai'):
        robbery = ctx.god_positions('比肩') + ctx.god_positions('劫财')
        if shenwang['verdict'] == 'strong':
            conditions.append('shenwang_strong')
        else:
            missing.append('shenwang_not_strong')
        if not robbery:
            conditions.append('no_robbery')
        else:
            missing.append('robbery_present')
    elif pattern_key == 'shishen':
        positions = ctx.god_positions('食神')
        if len(positions) == 1:
            conditions.append('single_position')
        else:
            missing.append('not_single_position')
        if shenwang['verdict'] == 'strong':
            conditions.append('shenwang_strong')
        else:
            missing.append('shenwang_not_strong')
        if not ctx.has_any_god('偏印'):
            conditions.append('no_seal_seizes')
        else:
            missing.append('seal_present')
    elif pattern_key == 'shangguan':
        shangjin = _modern_shangjin(ctx)
        if shangjin['grade'] == 'exhausted_modern':
            conditions.append('shangjin_exhausted')
        else:
            missing.append('shangjin_not_exhausted')
    if needs_shenwang and shenwang['verdict'] == 'abstain':
        return {'verdict': 'abstain', 'conditions': conditions,
                'missing': missing + ['shenwang_abstain'],
                'note': '现代身旺门弃判（%s）：成立评估弃判，不作'
                        '现代成立结论。'
                        % (shenwang['abstain_reason'] or '未给原因')}
    verdict = 'established_modern' if not missing else 'not_established_modern'
    return {'verdict': verdict, 'conditions': conditions,
            'missing': missing,
            'note': '现代成立评估（%s）：所列现代门条件全满足为'
                    ' established_modern；古典成立仍只认任氏寅月真格。'
                    % MODERN_MODEL_ID}


def _modern_broken(ctx, pattern_key, state):
    """P5 modern broken flags (presence/score flags only).

    ``flagged_modern`` means the classical breaking condition's
    presence/score form is met as an engineering flag; it is never a
    classical ``broken``. ``classical_broken`` marks the one classical
    channel (伤官见官 on an established premise). Patterns without a
    P5 modern flag return None.
    """
    shenwang = _modern_shenwang(ctx)
    flags = []
    if pattern_key == 'qisha':
        control = _modern_control_degree(ctx)
        flags.append({
            'flag_id': 'control_moderation_modern',
            'verdict': ('flagged_modern'
                        if control['grade'] == 'over_control_modern'
                        else 'not_flagged'),
            'detail': '制伏 %d 处、七杀 %d 处（%s）；太过旗标阈值见 '
                      'MODERN_OVER_CONTROL_*。'
                      % (control['control_count'], control['killing_count'],
                         control['grade']),
            'note': '现代制伏太过旗标；古典太过阈值仍无。'})
    elif pattern_key in ('zhengyin', 'pianyin'):
        wealth_total = len(ctx.god_positions('正财')
                           + ctx.god_positions('偏财'))
        if shenwang['verdict'] == 'abstain':
            verdict = 'abstain'
        else:
            verdict = ('flagged_modern'
                       if wealth_total >= MODERN_WEALTH_ABUNDANT_AT
                       and shenwang['verdict'] == 'strong'
                       else 'not_flagged')
        flags.append({
            'flag_id': 'wealth_breaks_seal_modern',
            'verdict': verdict,
            'detail': '财在场 %d 处、现代身旺门 %s（财多阈值 >= %d）；'
                      '财多乘旺为现代旗标条件。'
                      % (wealth_total, shenwang['verdict'],
                         MODERN_WEALTH_ABUNDANT_AT),
            'note': '现代财旺破印旗标；古典财多 / 乘旺程度与破印'
                    '效力仍无。'})
    elif pattern_key == 'shishen':
        seal = ctx.god_positions('偏印')
        flags.append({
            'flag_id': 'seal_seizes_food_modern',
            'verdict': 'flagged_modern' if seal else 'not_flagged',
            'detail': '偏印在场（%s）；偏印克食神为五行结构事实。'
                      % (ctx.god_position_text(seal) if seal else '无'),
            'note': '现代偏印夺食旗标；古典夺食效力仍无。'})
    elif pattern_key in ('zhengcai', 'piancai'):
        god = _P1_GODS[pattern_key]
        robbery = ctx.god_positions('比肩') + ctx.god_positions('劫财')
        wealth = _modern_wealth_degree(ctx, god)
        flags.append({
            'flag_id': 'robbery_divides_wealth_modern',
            'verdict': 'flagged_modern' if robbery else 'not_flagged',
            'detail': '比劫在场（%s）。'
                      % (ctx.god_position_text(robbery)
                         if robbery else '无'),
            'note': '现代比劫分夺旗标；古典分夺效力仍无。'})
        if shenwang['verdict'] == 'abstain':
            turns_verdict = 'abstain'
        else:
            turns_verdict = ('flagged_modern'
                             if wealth['grade'] == 'abundant_modern'
                             and shenwang['verdict'] == 'strong'
                             else 'not_flagged')
        flags.append({
            'flag_id': 'wealth_turns_officer_modern',
            'verdict': turns_verdict,
            'detail': '%s在场 %d 处（%s）、现代身旺门 %s。'
                      % (god, wealth['count'], wealth['grade'],
                         shenwang['verdict']),
            'note': '现代财多化官旗标；古典身健门与化官效力仍无。'})
    elif pattern_key == 'shangguan':
        officer = ctx.god_positions('正官')
        if state == 'broken':
            verdict = 'classical_broken'
        else:
            verdict = 'flagged_modern' if officer else 'not_flagged'
        flags.append({
            'flag_id': 'shangguan_sees_officer_modern',
            'verdict': verdict,
            'detail': '正官在场（%s）；古典通道只在成立前提下输出 '
                      'broken，其余只作现代旗标。'
                      % (ctx.god_position_text(officer)
                         if officer else '无'),
            'note': '现代伤官见官旗标；古典通道见 state=broken。'})
    else:
        return None
    return {'flags': flags,
            'any_flagged': any(f['verdict'] in ('flagged_modern',
                                                'classical_broken')
                               for f in flags)}


def _modern_extra_evidence(ctx, pattern_key, assessment):
    """Evidence ids for the modern layer's headline verdicts.

    Only hits are recorded: a modern establishment, a flagged modern
    broken condition, a modern cong establishment. Misses stay in the
    ``modern_assessment`` dict; they are not evidence noise.
    """
    out = []
    est = assessment['establishment_assessment']
    if est is not None and est['verdict'] == 'established_modern':
        out.append(_ev(
            '%s_modern_established' % pattern_key,
            '现代成立评估命中（%s）：条件满足（%s）；古典成立仍只认'
            '任氏寅月真格，本评估为现代工程模型结论。'
            % (MODERN_MODEL_ID, '、'.join(est['conditions']))))
    broken = assessment['broken_assessment']
    if broken is not None:
        for flag in broken['flags']:
            if flag['verdict'] == 'flagged_modern':
                out.append(_ev(
                    flag['flag_id'],
                    '现代破格旗标（%s）：%s 只作现代工程标注，'
                    '不作古典破格。' % (MODERN_MODEL_ID, flag['detail'])))
    cong = assessment['cong_assembly']
    if cong is not None:
        for kind in ('congsha', 'congcai'):
            if cong[kind]['verdict'] == 'established_modern':
                out.append(_ev(
                    '%s_modern_established' % kind,
                    '现代%s成立评估命中（%s）：条件满足（%s）；古典'
                    '从格成立（会杀 / 会财成局）未裁定。'
                    % ('从杀' if kind == 'congsha' else '从财',
                       MODERN_MODEL_ID,
                       '、'.join(cong[kind]['conditions']))))
    return out


def _modern_assessment(ctx, pattern_key, state):
    """Assemble the additive modern layer for one pattern result.

    Returns (assessment dict, extra evidence list). None assessment
    (with empty evidence) on the TJ-011.2 earth gate: no pattern
    judgement at all there. The layer never changes the classical
    ``state``; every verdict carries model_id / model_kind /
    research_only / public / ai.
    """
    if ctx.earth_gate:
        return None, []
    assessment = {
        'model_id': MODERN_MODEL_ID,
        'model_kind': 'modern_engineering',
        'research_only': True, 'public': False, 'ai': False,
        'shenwang_gate': _modern_shenwang(ctx),
        'root_grade': _modern_root_grade(ctx),
        'extreme_weak_band': _modern_extreme_weak(ctx),
        'shangjin_scale': (_modern_shangjin(ctx)
                           if pattern_key == 'shangguan' else None),
        'establishment_assessment': _modern_establishment(
            ctx, pattern_key, state),
        'broken_assessment': _modern_broken(ctx, pattern_key, state),
        'guansha_retention': (_modern_guansha_retention(ctx)
                              if pattern_key == 'zhengguan' else None),
        'cong_assembly': (_cong_modern(ctx)
                          if pattern_key == 'special' else None),
    }
    return assessment, _modern_extra_evidence(ctx, pattern_key, assessment)


class _Context:
    """Facts shared by every per-pattern evaluator."""

    def __init__(self, chart, *, official=None, resource=None, route=None,
                 zaqi=None, ren_yin=None):
        pillars = chart['pillars']
        if len(pillars) != 4:
            raise ValueError('Pattern engine requires four pillars')
        self.day_stem = chart['day_master']['stem']
        if self.day_stem not in STEMS:
            raise ValueError('Pattern engine requires a valid day stem')
        self.stems = [p['stem']['value'] for p in pillars]
        self.branches = [p['branch']['value'] for p in pillars]
        if any(b not in BRANCHES for b in self.branches):
            raise ValueError('Pattern engine requires valid branches')
        self.month_branch = self.branches[1]
        self.pillar_names = ('year', 'month', 'day', 'hour')
        # Visible ten gods per pillar (day pillar is the day-master
        # reference itself, never an exposed actor).
        self.visible_ten_gods = {
            name: ten_god(self.day_stem, stem)
            for name, stem in zip(self.pillar_names, self.stems)
            if name != 'day'
        }
        self.visible_stems = {
            name: stem for name, stem in zip(self.pillar_names, self.stems)
            if name != 'day'
        }
        # Month hidden stems with their ten gods (executed fact order).
        self.month_hidden = hidden_stems(self.month_branch, self.day_stem)
        self.month_hidden_by_god = {}
        for row in self.month_hidden:
            self.month_hidden_by_god.setdefault(row['ten_god'], []).append(row)
        # Every pillar's hidden stems (day branch included): a god's
        # positions across the whole chart, visible and hidden.
        self.all_hidden = []
        for i, name in enumerate(self.pillar_names):
            for row in hidden_stems(self.branches[i], self.day_stem):
                self.all_hidden.append({'pillar': name,
                                        'branch': self.branches[i],
                                        'stem': row['stem'],
                                        'ten_god': row['ten_god']})
        # Reviewed stem five-combination facts among the four stems,
        # plus branch relation facts from the same reviewed source
        # (batch 3: six-harmony feeds the 化气 screen; triple-harmony
        # branch presence is recorded as a fact only -- 会局成局判定
        # does not exist, so it never flips a screen on its own).
        # Branch clash / harm / punishment facts are deliberately NOT
        # consumed here: the 正官刑冲破害事实层 is unbuilt
        # (yh.zg_taboo_xingchong routes through a missing fact layer;
        # see bg-zhengguan-xingchong-fact-layer).
        _relations = reviewed_relations(self.stems, self.branches)
        self.five_combinations = _relations['stem_five_combinations']
        self.branch_six_harmonies = _relations['branch_six_harmonies']
        self.branch_triple_harmonies = _relations['branch_triple_harmonies']
        # Strength factors only: no strength verdict is consumed.
        self.strength_factors = _strength_factors(pillars, self.day_stem)
        # P6 modern 身旺门 (one call per chart, fail-closed): the
        # approved modern strength model, definite verdicts only.
        # Any error (including missing canonical data) abstains the
        # modern layer instead of failing the classical path.
        self.pillars = pillars
        self.modern_strength = _modern_strength_or_abstain(
            pillars, self.day_stem)
        # Optional precomputed reviewed blocks (from a trace); when a
        # block is absent the evaluator falls back to the same structural
        # facts computed directly from the pillars.
        self.official = official
        self.resource = resource
        self.route = route
        self.zaqi = zaqi
        self.ren_yin = ren_yin
        self.earth_gate = (self.day_stem, self.month_branch) in EARTH_UNJUDGEABLE

    def god_positions(self, god):
        """All positions of ``god``: visible stems (year/month/hour) and
        hidden stems of every branch (day branch included). The day stem
        itself is the reference and never a position."""
        out = []
        for name in ('year', 'month', 'hour'):
            if self.visible_ten_gods[name] == god:
                out.append({'pillar': name, 'kind': 'visible',
                            'stem': self.visible_stems[name]})
        for row in self.all_hidden:
            if row['ten_god'] == god:
                out.append({'pillar': row['pillar'], 'kind': 'hidden',
                            'stem': row['stem']})
        return out

    def god_position_text(self, positions):
        return '、'.join('%s%s%s' % (PILLAR_CN[p['pillar']],
                                     '干' if p['kind'] == 'visible' else '支藏',
                                     p['stem'])
                         for p in positions)

    def has_any_god(self, god):
        return bool(self.god_positions(god))

    def structural_roots(self):
        """Same-element hidden-stem root *candidates* (structural only):
        the Yuanhai 从格 registrations stress that root *grade*
        (light root / tomb root / pending) is unadjudicated, so these
        are presence facts, never an effective-root verdict."""
        return self.strength_factors['root_candidates']['positions']

    def visible_relation_kinds(self):
        return [row['relation'] for row in
                self.strength_factors['support_relations']['visible_positions']]

    def exposed_pillars(self, stem):
        """Year/month/hour pillars exposing ``stem`` (day stem excluded)."""
        return [name for name in EXPOSABLE_PILLARS
                if self.visible_stems[name] == stem]

    def month_hidden_god(self, god):
        rows = self.month_hidden_by_god.get(god, [])
        return rows[0] if rows else None

    def ren_yin_pattern(self):
        """(pattern_name, commander_stem, visible_pillars) if D-1 established."""
        block = self.ren_yin
        if not isinstance(block, dict):
            return None
        if block.get('status') != 'determined':
            return None
        inner = block.get('determination') or {}
        if inner.get('true_false') != 'true':
            return None
        pattern = inner.get('pattern')
        if not pattern:
            return None
        commander = block.get('commander') or {}
        return (pattern, commander.get('stem'),
                list(commander.get('visible_pillars') or []))

    def ren_yin_commander_not_visible(self):
        """Commander ten god when D-1 determined commander_not_visible."""
        god, _stem = self.ren_yin_commander_not_visible_full()
        return god

    def ren_yin_commander_not_visible_full(self):
        """(ten_god, stem) when D-1 determined commander_not_visible.

        A1: the commander fact needs the stem as well when the ten god
        is 比肩/劫财 (the commander stem is the day stem itself for
        比肩; for 劫财 it shares the day stem's element).
        """
        block = self.ren_yin
        if not isinstance(block, dict):
            return (None, None)
        if block.get('status') != 'determined':
            return (None, None)
        inner = block.get('determination') or {}
        if inner.get('true_false') != 'commander_not_visible':
            return (None, None)
        commander = block.get('commander') or {}
        return (commander.get('ten_god'), commander.get('stem'))

    def route_value(self):
        if isinstance(self.route, dict):
            return self.route.get('route')
        return luren_route_lookup(self.day_stem, self.month_branch)['route']

    def earth_result(self, pattern_key):
        return _result(
            self, pattern_key, 'not_judgeable',
            [_ev('tj0112_earth_unbuildable',
                 '戊×巳 / 己×午土日主成格不可建（TJ-011.2）：'
                 '日干 %s、月支 %s 一律不作格局裁定。'
                 % (self.day_stem, self.month_branch))],
            ['TJ-011.2 土日主成格未建：不输出候选、成立、破格或冲突。',
             '破格缺口：土日主成格不可建（TJ-011.2），破格条件亦无从谈起。'],
            rule_ids=[])


def _ten_god_evaluator(ctx, pattern_key, god, *, candidate_rule_id,
                       candidate_rule_note, no_rule_note, conditions=(),
                       broken_gap=''):
    """Shared logic for the eight ten-god patterns (正官/七杀/正印/偏印/
    正财/偏财/食神/伤官).

    ``conditions`` are computed presence facts from the pattern's
    registered section (in fact, efficacy unadjudicated); they are
    attached to established / candidate outcomes. ``broken_gap`` names
    the exact unadjudicated breaking condition for this pattern and is
    recorded as a limitation on every outcome -- ``broken`` is never
    emitted by this shared evaluator (the single 伤官见官 channel
    lives in ``_food_evaluator``, not here).
    """
    if ctx.earth_gate:
        return ctx.earth_result(pattern_key)
    limitations_extra = [broken_gap] if broken_gap else []
    established = ctx.ren_yin_pattern()
    if established is not None and established[0] == god + '格':
        return _result(
            ctx, pattern_key, 'established',
            [_ev('ren_yin_true_pattern',
                 '任氏分支寅月真格成立：司令 %s（%s）透于 %s。'
                 % (established[1], god, '、'.join(established[2]) or '无')),
             _ev('ren_yin_rule',
                 '依据 bazi.phase2.ren_yin_true_pattern（validated，'
                 'Golden 15；s053 原注定义句 + s054 任氏曰程序句）。')]
            + list(conditions),
            ['成败 / 清浊 / 用神恒未审；破格通道见本格破格缺口条'
             '（除伤官见官外无古典 broken 通道）；'
             '只裁定寅月任氏分支真格成立，不外推其他月份与流派。']
            + limitations_extra,
            rule_ids=['bazi.phase2.ren_yin_true_pattern'])
    row = ctx.month_hidden_god(god)
    if row is None:
        evidence = [_ev('no_month_hidden_god',
                        '月支 %s 藏干中无 %s；散见于他柱的 %s 不导入月令取格。'
                        % (ctx.month_branch, god, god))]
        if ctx.ren_yin_commander_not_visible() == god:
            evidence.append(_ev(
                'ren_yin_commander_not_visible',
                '寅月司令为 %s 但不透：结论止于“无真格”，永不标“假格”。'
                % god))
        scattered = ctx.god_positions(god)
        if scattered:
            evidence.append(_ev(
                'scattered_god_positions',
                '散见 %s 位置（%d 处）：%s——只记事实，不导入月令取格。'
                % (god, len(scattered),
                   ctx.god_position_text(scattered))))
        return _result(ctx, pattern_key, 'not_judgeable', evidence,
                       ['无月藏 %s 观察：不等于该盘无此格，只说明本引擎无依据。' % god]
                       + limitations_extra,
                       rule_ids=[])
    exposed = ctx.exposed_pillars(row['stem'])
    evidence = [
        _ev('month_hidden_god',
            '月支 %s 藏 %s（%s），透于：%s。'
            % (ctx.month_branch, row['stem'], god,
               '、'.join(exposed) if exposed else '未透')),
    ]
    if candidate_rule_id:
        evidence.append(_ev(candidate_rule_id, candidate_rule_note))
    else:
        evidence.append(_ev('month_hidden_observation', candidate_rule_note))
    if ctx.ren_yin_commander_not_visible() == god:
        evidence.append(_ev(
            'ren_yin_commander_not_visible',
            '寅月司令为 %s 但不透：结论止于“无真格”，永不标“假格”。' % god))
    evidence.extend(conditions)
    limitations = [
        '只作候选观察：分日司令未裁定（寅月以外）、旺衰未裁定、'
        '真假 / 成败 / 清浊 / 用神未裁定。',
        no_rule_note,
    ] + limitations_extra
    return _result(ctx, pattern_key, 'candidate', evidence, limitations,
                   rule_ids=[candidate_rule_id] if candidate_rule_id else [])


def _qisha_condition_evidence(ctx):
    """七杀条件事实（《渊海》〈论七杀〉yh.qs_* / 〈论官星太过〉yh.gt_*）：
    在场事实可算，效力（身旺 / 制伏 / 合杀 / 财旺）皆未裁定。"""
    out = []
    positions = ctx.god_positions('七杀')
    if positions:
        out.append(_ev(
            'qisha_positions',
            '七杀位置（%d 处）：%s。'
            % (len(positions), ctx.god_position_text(positions))))
        pillars = {p['pillar'] for p in positions}
        if 'day' in pillars:
            out.append(_ev(
                'qisha_day_position',
                '日柱见七杀（yh.qs_day_killing：只一位、年时再见杀多为祸，'
                '却要制伏之乡、又要身旺有制伏为权；位置观察，效力未裁定）。'))
        if 'hour' in pillars:
            out.append(_ev(
                'qisha_hour_position',
                '时柱见七杀（yh.qs_hour_killing：要本身旺、三处有制伏为福；'
                'yh.qs_hour_no_fear：时上七杀却不怕阳刃、不畏冲；'
                '位置观察，效力未裁定）。'))
        if len(positions) >= 2:
            out.append(_ev(
                'qisha_many_positions',
                '杀多事实（%d 处）：月见之重、时见之轻为位置权重观察'
                '（yh.qs_many_killings_weight），非破格结论。' % len(positions)))
    control = ctx.god_positions('食神') + ctx.god_positions('伤官')
    if control:
        out.append(_ev(
            'qisha_control_present',
            '制伏在场：%s（食神 / 伤官；yh.qs_control_present 元有制伏、'
            'yh.qs_jia_example_control 甲以庚为七杀、喜丙丁制之；'
            '制伏构成与效力未裁定）。'
            % ctx.god_position_text(control)))
    else:
        out.append(_ev(
            'qisha_control_absent',
            '四柱无食神 / 伤官制伏在场（yh.qs_control_present 元无制伏句；'
            '无制伏为事实，非破格结论）。'))
    for pair in ctx.five_combinations:
        stems = pair['stems']
        killing = [s for s in stems if ten_god(ctx.day_stem, s) == '七杀']
        if killing:
            out.append(_ev(
                'qisha_combined_killing',
                '合杀在场：%s 五合，合及七杀 %s（yh.qs_jia_example_control '
                '乙合之、谓之贪合忘杀；合化效力未裁定）。'
                % ('、'.join(stems), '、'.join(killing))))
    wealth = ctx.god_positions('正财') + ctx.god_positions('偏财')
    if wealth:
        out.append(_ev(
            'qisha_wealth_feeds',
            '财星在场：%s（财能生杀；yh.qs_blade_and_wealth 忌财旺句；'
            '财旺为强度判断，未阈值化）。'
            % ctx.god_position_text(wealth)))
    official = ctx.god_positions('正官')
    if official:
        out.append(_ev(
            'qisha_official_present',
            '正官在场：%s（官杀并见数量事实；yh.zg_qingzhong 年时支干位'
            '或有一偏官便杂矣、轻重推测未裁定——只记并见，不定混杂、'
            '不定去留）。' % ctx.god_position_text(official)))
    # yh.gt_hidden （《论官星太过》首段）：壬癸生人、四柱支皆在
    # 辰戌丑未巳午、天干不露官星与杀，则官杀暗藏于中为多。暗藏本身
    # 为在场事实；救应两路（元有制伏 / 须行木运、三合木局）经制伏
    # 效力与合局转手，均未裁定。
    if ctx.day_stem in ('壬', '癸') and all(
            b in ('辰', '戌', '丑', '未', '巳', '午')
            for b in ctx.branches):
        visible_officer_killing = [
            name for name in ('year', 'month', 'hour')
            if ctx.visible_ten_gods[name] in ('正官', '七杀')]
        hidden_officer_killing = [
            p for p in ctx.god_positions('正官') + ctx.god_positions('七杀')
            if p['kind'] == 'hidden']
        if not visible_officer_killing and hidden_officer_killing:
            out.append(_ev(
                'qisha_hidden_officer_killing',
                '官杀暗藏事实（yh.gt_hidden）：%s日、四柱支皆在辰戌丑未'
                '巳午、天干不露官星与杀，官杀暗藏于中（%s）。救应两路'
                '（元有制伏 / 须行木运与三合木局）经效力与合局转手，'
                '均未裁定。'
                % (ctx.day_stem,
                   ctx.god_position_text(hidden_officer_killing))))
    ren = REN_BRANCH.get(ctx.day_stem)
    if ren is not None and (ctx.month_branch == ren or ctx.branches[2] == ren):
        out.append(_ev(
            'qisha_blade_present',
            '阳刃在场（刃在 %s，见于%s；yh.qs_blade_and_wealth 更有阳刃句；'
            '与日七杀最怕冲与阳刃、时七杀不怕阳刃构成位置对照，'
            '刃的效力未裁定）。'
            % (ren, '月支' if ctx.month_branch == ren else '日支')))
    day_ganzhi = ctx.stems[2] + ctx.branches[2]
    if day_ganzhi in SEVEN_KILLING_DAYS:
        out.append(_ev(
            'qisha_seven_days',
            '日柱 %s 在七日生主杀列举内（yh.qs_seven_days 甲申、乙酉、'
            '丁丑、戊寅、己卯、辛未、癸未；列举与性情断语，'
            '非成格 / 破格条件）。' % day_ganzhi))
    return out


def _wealth_condition_evidence(ctx, god):
    """财格条件事实（《渊海》〈论正财〉yh.zc_* / 〈论偏财〉yh.pc_* /
    〈论劫财〉yh.jc_*）：在场事实可算，比劫分夺 / 财多化官 /
    财生官的效力皆未裁定。"""
    out = []
    positions = ctx.god_positions(god)
    if positions:
        out.append(_ev(
            'wealth_positions',
            '%s位置（%d 处）：%s。'
            % (god, len(positions), ctx.god_position_text(positions))))
        if len(positions) >= 2:
            out.append(_ev(
                'wealth_many_positions',
                '财多事实（%d 处）：yh.zc_many_transform_officer 若财多则'
                '自家日本有力、可以胜任、当化作官——身健与化官效力未裁定，'
                '只记数量事实。' % len(positions)))
    robbery = ctx.god_positions('比肩') + ctx.god_positions('劫财')
    if robbery:
        out.append(_ev(
            'wealth_robbery_present',
            '比劫在场：%s（yh.pc_definition 只恐兄弟姊妹有夺之、'
            'yh.zc_wealth_strife_root 财者起争之端也；分夺效力未裁定，'
            '不判夺财破格）。' % ctx.god_position_text(robbery)))
    officer = ctx.god_positions('正官')
    if officer:
        out.append(_ev(
            'wealth_officer_present',
            '官星在场：%s（yh.zc_wealth_generates_officer 财多生官、'
            '要须身健；yh.pc_wealth_generates_officer 财盛自生官；'
            '生官链效力未裁定）。' % ctx.god_position_text(officer)))
    food = ctx.god_positions('食神') + ctx.god_positions('伤官')
    if food:
        out.append(_ev(
            'wealth_food_generates',
            '食伤在场：%s（yh.ss_definition 食神者、生我财神之谓也；'
            '食伤生财链效力未裁定）。' % ctx.god_position_text(food)))
    seal = ctx.god_positions('正印') + ctx.god_positions('偏印')
    if seal:
        out.append(_ev(
            'wealth_seal_present',
            '印星在场：%s（yh.zc_both_prefer_seal 大抵财不论偏正、皆喜'
            '印綬；yh.zc_preferences 喜印綬者、能生身主弱故也；'
            '喜印綬方向已见，生身效力未裁定）。'
            % ctx.god_position_text(seal)))
    # yh.zc_strong_no_robbery （身旺无劫财、无官星为妙）：身旺门未裁定
    # （P6），但劫财 / 正官在场与否本身为可算事实，并列记录。
    out.append(_ev(
        'wealth_robbery_officer_absence',
        '无劫无官核查（yh.zc_strong_no_robbery）：劫财%s、正官%s；'
        '身旺门未裁定（P6），只记在场与否，不作“为妙”判断。'
        % ('在场（%s）' % ctx.god_position_text(robbery) if robbery
           else '不在场',
           '在场（%s）' % ctx.god_position_text(officer) if officer
           else '不在场')))
    if god == '偏财' and officer and robbery:
        out.append(_ev(
            'piancai_officer_brothers_contrast',
            '官星与兄弟对照并陈（yh.pc_officer_vs_brothers）：官星在场'
            '（%s）、兄弟在场（%s）；元带官星作好命看与兄弟辈出则'
            '发禄必渺两门对照并列，均未裁定。'
            % (ctx.god_position_text(officer),
               ctx.god_position_text(robbery))))
    if god == '正财' and ctx.has_any_god('伤官'):
        out.append(_ev(
            'wealth_shangguan_sees_wealth',
            '伤官在场：%s（yh.zc_shangguan_jiancai 伤官见财格、忌见官星、'
            '只喜见财；格名提及，成立未裁定）。'
            % ctx.god_position_text(ctx.god_positions('伤官'))))
    if god == '偏财':
        exposed = ctx.exposed_pillars(ctx.month_hidden_god('偏财')['stem']) \
            if ctx.month_hidden_god('偏财') else []
        out.append(_ev(
            'piancai_exposure',
            '偏财%s（yh.pc_exposure 偏财好出、亦不惧藏，惟怕有以分夺）。'
            % ('透于 ' + '、'.join(exposed) if exposed else '藏于月支未透')))
    return out


def _food_condition_evidence(ctx, god):
    """食伤条件事实（《渊海》〈论伤官〉yh.sw_* / 〈论食神〉yh.ss_* /
    〈论倒食〉yh.ds_*）：在场事实可算，伤尽程度 / 伤官见官 /
    倒食夺食的效力皆未裁定。"""
    out = []
    positions = ctx.god_positions(god)
    if positions:
        out.append(_ev(
            '%s_positions' % ('shishen' if god == '食神' else 'shangguan'),
            '%s位置（%d 处）：%s。'
            % (god, len(positions), ctx.god_position_text(positions))))
    if god == '食神':
        if len(positions) == 1:
            out.append(_ev(
                'shishen_single_position',
                '食神独一位事实：仅 %s 一处（yh.ss_single_position 独一位'
                '见之、则为福人、然终亦不清；独一位之外多见如何未定，'
                '清浊判断不存在，只记数量事实）。'
                % ctx.god_position_text(positions)))
        wealth = ctx.god_positions('正财') + ctx.god_positions('偏财')
        if wealth:
            out.append(_ev(
                'shishen_generates_wealth',
                '财星在场：%s（yh.ss_definition 食神者、生我财神之谓也；'
                '生财链效力未裁定）。' % ctx.god_position_text(wealth)))
        seal = ctx.god_positions('偏印')
        if seal:
            out.append(_ev(
                'shishen_seized_by_seal',
                '偏印在场：%s（yh.ds_mechanism 倒食：甲见壬之类、壬剋丙火、'
                '食神不能生财；倒食夺食效力未裁定，不判破格）。'
                % ctx.god_position_text(seal)))
        zhengyin = ctx.god_positions('正印')
        if zhengyin:
            out.append(_ev(
                'shishen_seal_present',
                '正印在场：%s（yh.ss_body_strong_seal_taboo 却喜身旺、'
                '不喜印綬、亦恐伤其食神也；不喜印綬方向已见，印伤食'
                '效力未裁定，不判破格）。'
                % ctx.god_position_text(zhengyin)))
    else:
        officer = ctx.god_positions('正官') + ctx.god_positions('七杀')
        if officer:
            out.append(_ev(
                'shangguan_sees_officer',
                '官杀在场：%s（yh.sw_pattern_no_officer 用伤官格者、支干岁运'
                '都要不见官星、如见官星谓之伤官见官；见官效力未裁定，'
                '不判破格）。' % ctx.god_position_text(officer)))
            # yh.sw_not_exhausted_officer （若伤官不尽、四柱有官星露）：
            # 正官透干（露）与藏而未露为可算的在场区分，祸福判定仍经
            # 伤官见官效力转手，未裁定；只有七杀在场时不作此区分。
            zhengguan = ctx.god_positions('正官')
            if zhengguan:
                exposed_officer = [
                    p for p in zhengguan if p['kind'] == 'visible']
                if exposed_officer:
                    out.append(_ev(
                        'shangguan_officer_exposed',
                        '官星露事实：正官透干在场（%s；yh.sw_not_exhausted_'
                        'officer 若伤官不尽、四柱有官星露；只记透干事实，'
                        '不判伤官见官）。'
                        % ctx.god_position_text(exposed_officer)))
                else:
                    out.append(_ev(
                        'shangguan_officer_hidden_only',
                        '官星藏而未露事实：正官只藏于支（%s），四柱天干无官'
                        '星露（yh.sw_not_exhausted_officer 官星露为在场事实；'
                        '只记透藏区分，不判伤官见官）。'
                        % ctx.god_position_text(zhengguan)))
        else:
            out.append(_ev(
                'shangguan_exhausted_observation',
                '四柱无官杀在场：伤尽结构观察（yh.sw_exhaust_core 伤官务要'
                '伤尽；伤尽为程度词、无已裁定程度标尺，仍只作候选观察，'
                '不作伤尽成立）。'))
        wealth = ctx.god_positions('正财') + ctx.god_positions('偏财')
        if wealth:
            out.append(_ev(
                'shangguan_meets_wealth',
                '财星在场：%s（yh.sw_meet_wealth_wonderful 如遇伤官者、'
                '须见其财为妙、是财能生官也；评价以伤官格成立为前提，'
                '成立未裁定）。' % ctx.god_position_text(wealth)))
    return out


def _official_condition_evidence(ctx):
    """正官条件事实（《渊海》〈正官论〉yh.zg_* / 〈论官杀混杂要制伏〉
    yh.gs_*）：官多与他柱杀只记事实；去留条件事实在场不等于去留
    已行。时柱七杀的混杂 conflict 由 evaluate_zhengguan 另行判定。"""
    out = []
    officials = ctx.god_positions('正官')
    if officials:
        out.append(_ev(
            'official_positions',
            '正官位置（%d 处）：%s（yh.zg_duo 正官或多、反不为福的'
            '数量事实；多寡只记事实，不判杂、不判破格）。'
            % (len(officials), ctx.god_position_text(officials))))
    seal = ctx.god_positions('正印') + ctx.god_positions('偏印')
    if seal:
        out.append(_ev(
            'official_seal_present',
            '印星在场：%s（yh.ys_guangui_sheng 官鬼能生我、只畏其财；'
            'yh.zg_shenwang_fa 大率官星须得印綬、身旺则发；官印相生'
            '方向已见，身旺门未裁定（P6），效力未裁定）。'
            % ctx.god_position_text(seal)))
    killings = ctx.god_positions('七杀')
    if officials and killings:
        out.append(_ev(
            'guansha_coexistence_count',
            '官杀并见数量事实：正官 %d 处、七杀 %d 处（yh.zg_qingzhong '
            '既用提纲作正官、年时支干位或有一偏官便杂矣；轻重推测'
            '未裁定——只记数量，不定混杂、不定去留、不定破格）。'
            % (len(officials), len(killings))))
        # P2: yh.gs_example_zhifu 触发条件事实（“若有金或庚申”）：
        # 金五行在场（显干 / 支 / 藏干）与庚 / 申在场与否只记事实；
        # 则混杂为杀、要行火乡制伏的效力与去留操作均未裁定。
        gold_stems = [s for s in ctx.stems if stem_element(s) == '金']
        gold_branches = [b for b in ctx.branches if b in ('申', '酉')]
        gold_hidden = [row['stem'] for row in ctx.all_hidden
                       if stem_element(row['stem']) == '金']
        out.append(_ev(
            'guansha_zhifu_trigger',
            '制伏触发条件事实（yh.gs_example_zhifu 若有金或庚申）：'
            '金%s，庚 / 申%s；触发条件只记在场与否，不定混杂为杀、'
            '不定行火乡制伏效力、不定去留。'
            % ('在场（显干 %s；支 %s；藏干 %s）'
               % ('、'.join(gold_stems) or '无',
                  '、'.join(gold_branches) or '无',
                  '、'.join(gold_hidden) or '无')
               if gold_stems or gold_branches or gold_hidden else '不在场',
               '在场（庚干%s；申支%s）'
               % ('有' if '庚' in ctx.stems else '无',
                  '有' if '申' in ctx.branches else '无')
               if ('庚' in ctx.stems) or ('申' in ctx.branches)
               else '皆不在场')))
    if len(officials) >= 2:
        out.append(_ev(
            'official_many_positions',
            '官星多事实（%d 处）：%s（yh.zg_duo 正官或多、反不为福；'
            'yh.gt_clear 官星多则杂、务要除而清之；多寡只记事实，'
            '杂 / 去留效力未裁定）。'
            % (len(officials), ctx.god_position_text(officials))))
    other = [p for p in killings if p['pillar'] != 'hour']
    if other:
        out.append(_ev(
            'official_other_pillar_killing',
            '七杀在他柱：%s（s055 / yh.zg_jia_mixed 只论时干支逢杀乃官杀'
            '混杂；他柱杀只记共现事实，不定混杂、不定去留）。'
            % ctx.god_position_text(other)))
    control = ctx.god_positions('食神') + ctx.god_positions('伤官')
    if control:
        out.append(_ev(
            'guansha_retention_condition',
            '去留条件事实在场：%s（食神 / 伤官；yh.gs_example_zhifu '
            '若有金或庚申、则混杂为杀、要行火乡制伏、则发福也；'
            'yh.gt_clear 除而清之；去何星、清至何程度均未裁定）。'
            % ctx.god_position_text(control)))
    return out


def _resource_condition_evidence(ctx, god):
    """印绶条件事实（《渊海》〈论印綬〉yh.yn_* / yh.ys_* / 〈论倒食〉
    yh.ds_*）：财破印 / 官印相生 / 倒食夺食只记方向与位置，
    效力一律未裁定。"""
    out = []
    positions = ctx.god_positions(god)
    if positions:
        out.append(_ev(
            'resource_positions',
            '%s位置（%d 处）：%s。'
            % (god, len(positions), ctx.god_position_text(positions))))
    wealth = ctx.god_positions('正财') + ctx.god_positions('偏财')
    if wealth:
        out.append(_ev(
            'resource_wealth_breaks_seal',
            '财星在场：%s（yh.yn_wealth_floods 财多乘旺、必多淹留；'
            'yh.yn_wealth_arrives_floods 最忌财来乘旺、必生淹滞；'
            '财破印效力未裁定，不判破格）。'
            % ctx.god_position_text(wealth)))
    officer = ctx.god_positions('正官') + ctx.god_positions('七杀')
    if officer:
        out.append(_ev(
            'resource_officer_generates_seal',
            '官杀在场：%s（yh.ys_guangui_sheng 官鬼能生我、只畏其财；'
            '官印相生方向已见，效力未裁定）。'
            % ctx.god_position_text(officer)))
    # yh.ds_killing_control （又见庚为七杀、得丙丁火制之，怕见水、
    # 反为祸矣）：偏印格内七杀在场与食神制杀在场为可算事实；制杀
    # 效力与见水破制效力均未裁定。
    if god == '偏印':
        killing = ctx.god_positions('七杀')
        if killing:
            control = (ctx.god_positions('食神')
                       + ctx.god_positions('伤官'))
            out.append(_ev(
                'resource_seal_controls_killing',
                '制杀结构事实（yh.ds_killing_control）：七杀在场（%s），'
                '制杀之火（食神 / 伤官）%s；制伏效力与怕见水破制效力'
                '均未裁定，不判破格。'
                % (ctx.god_position_text(killing),
                   '在场（%s）' % ctx.god_position_text(control)
                   if control else '不在场')))
    if god == '偏印' and ctx.has_any_god('食神'):
        out.append(_ev(
            'resource_seal_seizes_food',
            '食神在场：%s（yh.ds_mechanism 倒食：甲用食神、大忌见之；'
            '偏印夺食效力未裁定，不判破格）。'
            % ctx.god_position_text(ctx.god_positions('食神'))))
    month_hour = [p for p in positions if p['pillar'] in ('month', 'hour')]
    if month_hour:
        out.append(_ev(
            'resource_month_hour_position',
            '印见于%s（yh.yn_month_hour_position 月与时上见者为妙、'
            '而月上最为紧要；评价以印格成立为前提，成立未裁定）。'
            % '、'.join(PILLAR_CN[p['pillar']] + '柱' for p in month_hour)))
    return out


def _luren_condition_evidence(ctx, kind):
    """禄刃条件事实（三命《论十干禄》/《论阳刃》/《论日刃》yh.yr_* /
    yh.rr_*）：位置事实可算，禄刃成格 determination 恒 None。"""
    out = []
    if kind == 'lu':
        lu = LU_BRANCH[ctx.day_stem]
        if ctx.branches[2] == lu:
            out.append(_ev(
                'day_lu_position',
                '日支 %s 为 %s 日之禄支（三命《论十干禄》禄表；'
                '日禄位置事实，建禄成格无已审依据）。'
                % (lu, ctx.day_stem)))
        return out
    ren = REN_BRANCH.get(ctx.day_stem)
    if ren is None:
        return out
    day_ganzhi = ctx.stems[2] + ctx.branches[2]
    if ctx.branches[2] == ren:
        out.append(_ev(
            'day_ren_position',
            '日支 %s 为 %s 日之刃支（三命《论阳刃》刃表；'
            '日刃位置事实，阳刃成格无已审依据）。'
            % (ren, ctx.day_stem)))
        if day_ganzhi in DAY_REN_PILLARS:
            out.append(_ev(
                'day_ren_enumerated',
                '日柱 %s 在《论日刃》所列三柱内（yh.rr_same_method 日刃有'
                '戊午、丙午、壬子也、与阳刃同法；列举事实，'
                '日刃格 determination 恒 None）。' % day_ganzhi))
    killing = ctx.god_positions('七杀')
    if killing and (ctx.month_branch == ren or ctx.branches[2] == ren):
        out.append(_ev(
            'blade_killing_present',
            '刃杀俱全在场：刃（%s）与七杀（%s）共现'
            '（yh.yr_blade_killing_strength 杀无刃不显、刃无杀不威，'
            '刃杀俱全、非常人有之；评价以阳刃格成立为前提，'
            '成立未裁定）。'
            % (ren, ctx.god_position_text(killing))))
    wealth = ctx.god_positions('偏财')
    if wealth and (ctx.month_branch == ren or ctx.branches[2] == ren):
        out.append(_ev(
            'blade_wealth_present',
            '偏财在场：%s（yh.yr_wealth_preference 凡有刃者、却喜偏财七杀；'
            '喜忌方向已见，效力未裁定）。'
            % ctx.god_position_text(wealth)))
    # yh.rr_hour_wealth_taboo （独阳刃以时言之、四柱中不要入财乡、
    # 怕冲阳刃）：时支为刃且时柱见财星，为该句前提的在场事实；
    # 财乡 / 冲刃效力未裁定。
    #
    # B2 修正：此处“财乡”按引文取财星通称（正财 + 偏财），不是
    # 偏财专称。原只计偏财时，本条件对甲/庚日一切合法盘不可达：
    # 甲刃卯、庚刃酉皆阴支，阳日主的偏财干皆阳干，偏财透时干的柱
    # （如甲酉）皆非六十甲子；刃支藏干于阳日主亦无偏财（卯藏乙、
    # 酉藏辛皆为劫财）。丙/戊/壬日（刃午/子为阳支）原已可达
    # （庚午/壬午/丙子），修正不改变彼等情形，只补甲/庚日缺口；
    # 本测试盘为庚日，非修正不可。引文既言财乡，时柱财星（正财 /
    # 偏财）在场即记事实。blade_wealth_present 仍只计偏财（其引文
    # yh.yr_wealth_preference 专言偏财）。
    if ctx.branches[3] == ren:
        hour_wealth = [p for p in
                       (ctx.god_positions('正财')
                        + ctx.god_positions('偏财'))
                       if p['pillar'] == 'hour']
        if hour_wealth:
            out.append(_ev(
                'blade_wealth_hour_position',
                '时刃时财共现事实：时支 %s 为刃，财星在时柱（%s；'
                'yh.rr_hour_wealth_taboo 独阳刃以时言之、四柱中不要入'
                '财乡、怕冲阳刃；只记位置事实，财乡 / 冲刃效力未裁定）。'
                % (ren, ctx.god_position_text(hour_wealth))))
    seal = ctx.god_positions('正印') + ctx.god_positions('偏印')
    if seal and (ctx.month_branch == ren or ctx.branches[2] == ren):
        out.append(_ev(
            'blade_seal_present',
            '印星在场：%s（yh.yr_preferences 喜偏官七杀、喜印綬；'
            '喜印綬方向已见，印綬化杀 / 生身链效力未裁定）。'
            % ctx.god_position_text(seal)))
    return out


def _zaqi_inventory_evidence(ctx):
    """杂气月藏全清单（batch 3）：月支全部藏干及其十神并列，不只列
    透出者。选格对象仍只并列、不代选；土格换算未裁定（P3）。"""
    return _ev(
        'zaqi_month_hidden_inventory',
        '杂气月藏全清单：月支 %s 藏干 %s（选格所议人元全集；'
        '透出者见 zaqi_variant_yuanzhu 透干位置，余者只作藏干事实）。'
        % (ctx.month_branch,
           '、'.join('%s（%s）' % (row['stem'], row['ten_god'])
                     for row in ctx.month_hidden)))


def _zaqi_earth_conversion_evidence(ctx):
    """P3 conditional 土格换算 mapping (conditional presentation).

    “只当取土为格”中的“土”所指未裁定；本证据只作条件换算：若
    “土”指月支本气之土（辰/戌→戊，丑/未→己，即月藏首干），则其
    对日主的十神为 X。换算本身不作定格，定格仍为 conflict。
    """
    principal = ctx.month_hidden[0] if ctx.month_hidden else None
    if principal is None:
        return _ev('zaqi_earth_conversion_mapping',
                   '杂气月藏为空：无本气土可换算。')
    return _ev(
        'zaqi_earth_conversion_mapping',
        '土格换算条件映射：月支 %s 本气之土为 %s，对 %s 日主为 %s。'
        '此为条件换算（若“土”指月支本气之土）；“土”所指未裁定，'
        '不作定格、不代选。'
        % (ctx.month_branch, principal['stem'], ctx.day_stem,
           principal['ten_god']))


def _zaqi_variant_evidence(ctx, lookup):
    """杂气三向 Variant 并列（Q13）：原注 / 三命 / 子平真诠 Ch16
    各自陈述，不强行统一，不代选。Batch 3 adds the exposed-pillar
    position of every renyuan stem (a pure presence fact)."""
    exposed = lookup.get('exposed_renyuan') or []
    exposed_text = '、'.join(
        '%s（%s%s）' % (
            row['stem'], row['ten_god'],
            '，透于' + '、'.join(ctx.exposed_pillars(row['stem']))
            if ctx.exposed_pillars(row['stem']) else '，未透')
        for row in exposed) if exposed else '无人元透出'
    arm = lookup.get('arm')
    if arm == 'wuji_exposed_renyuan':
        yuanzhu = ('原注 Variant（戊己臂）：当看人元透出天干者取格；'
                   '透出者并列：%s；原文不予定序定名，不代选。' % exposed_text)
    else:
        yuanzhu = ('原注 Variant（一般臂）：只当取土为格、不可言杂气财官；'
                   '土格换算（“土”是否指月支本气之土、再对日干作十神换算）'
                   '未裁定；透出者只作事实并列：%s。' % exposed_text)
    return [
        _ev('zaqi_variant_yuanzhu', yuanzhu),
        _ev('zaqi_variant_sanming',
            '三命 Variant：杂气格为正式格名（s066 卷六《日禄归时》实案'
            '“作杂气格论尤是”、s067 女命章“杂气格中禄最佳”）；'
            '与原注“不可言杂气财官”直接对立，不裁定。'),
        _ev('zaqi_variant_ziping',
            '子平真诠 Ch16 Variant（ziping-zaqi-ch16-v1，第三立场）：'
            'B-16-03“透干會支。取其清者用之。”直接命名杂气财官印；'
            '11 条（B-16-03–B-16-10、B-16-12–B-16-14）与原注一般臂直接'
            '对立；B-16-10 会支句、B-16-16 机制句、B-16-18 理由句不可引；'
            '清 / 有情无定义、无阈值；determination 恒 None，'
            'evidence_binding 恒 pending。'),
    ]


def evaluate_zhengguan(ctx):
    """正官： reviewed candidate rule (Golden 20); s055 hour-killing
    caution is a conflict, never a 破格 verdict."""
    if ctx.earth_gate:
        return ctx.earth_result('zhengguan')
    established = ctx.ren_yin_pattern()
    if established is not None and established[0] == '正官格':
        result = _ten_god_evaluator(
            ctx, 'zhengguan', '正官',
            candidate_rule_id='bazi.phase2.official_pattern_candidates',
            candidate_rule_note='正官结构候选（validated，Golden 20）。',
            no_rule_note='',
            conditions=_official_condition_evidence(ctx),
            broken_gap='破格缺口：官杀去留效力（yh.gs_example_zhifu 行火乡制伏、'
                       'yh.gt_clear 除而清之）与清浊标准未裁定；刑冲破害事实层'
                       '（yh.zg_taboo_xingchong）、轻重推测标尺（yh.zg_qingzhong）'
                       '与身旺门（yh.zg_shenwang_fa，P6 堵点）亦未裁定，'
                       '故正官破格条件无，broken 永不输出。')
        # D-1 establishes the true pattern, but an hour 七杀 co-presence
        # still carries the s055 additional-review caution.
        hour_killing = _hour_killing_positions(ctx)
        if hour_killing:
            result['evidence'].append(_ev(
                'hour_killing_restriction_s055',
                '时柱另见七杀（%s）：《渊海》s055 提示追加审核，'
                '与 D-1 真格成立并列记录，不改写成立结论。'
                % '、'.join('%s：%s' % (k, v) for k, v in hour_killing)))
            result['limitations'].append(
                '时七杀共现：s055 追加审核仍待另行裁定（官杀去留未裁定）。')
        return result
    row = ctx.month_hidden_god('正官')
    if row is None:
        # Yuanhai 甲辛 / 巳酉丑 single-example branch: 甲日、酉月、
        # 辛不透、巳酉丑齐备 -- a reviewed structural candidate, not a
        # determination.
        branch = _yuanhai_unexposed_official_branch(ctx)
        if branch is not None:
            return _result(
                ctx, 'zhengguan', 'candidate', branch,
                ['单例观察（《渊海》s056 甲辛酉月例）：不定正官格、'
                 '不定合化、身旺、真假成败或喜用；不外推他日他月。',
                 '破格缺口：官杀去留效力与清浊标准未裁定，'
                 '故正官破格条件无，broken 永不输出。'],
                rule_ids=['bazi.phase2.official_pattern_candidates'])
        return _ten_god_evaluator(
            ctx, 'zhengguan', '正官',
            candidate_rule_id='bazi.phase2.official_pattern_candidates',
            candidate_rule_note='正官结构候选（validated，Golden 20）。',
            no_rule_note='',
            broken_gap='破格缺口：官杀去留效力（yh.gs_example_zhifu 行火乡制伏、'
                       'yh.gt_clear 除而清之）与清浊标准未裁定；刑冲破害事实层'
                       '（yh.zg_taboo_xingchong）、轻重推测标尺（yh.zg_qingzhong）'
                       '与身旺门（yh.zg_shenwang_fa，P6 堵点）亦未裁定，'
                       '故正官破格条件无，broken 永不输出。')
    hour_killing = _hour_killing_positions(ctx)
    if hour_killing:
        evidence = [
            _ev('month_hidden_official',
                '月支 %s 藏正官 %s。' % (ctx.month_branch, row['stem'])),
            _ev('hour_killing_restriction_s055',
                '时柱见七杀（%s）：《渊海》s055 提示不得直称正官，'
                '只标注追加审核。'
                % '、'.join('%s：%s' % (k, v) for k, v in hour_killing)),
            _ev('guansha_variant_s055',
                '官杀混杂 Variant（s055）：时干支逢杀、不得直称正官，'
                '只追加审核；不定混杂、不定破格。'),
            _ev('guansha_variant_yuanhai_zhifu',
                '官杀混杂 Variant（《论官杀混杂要制伏》yh.gs_example_zhifu）：'
                '若有金或庚申、则混杂为杀、以伤其身，要行火乡制伏、'
                '则发福也；去留操作与效力未裁定。两 Variant 并列，'
                '不统一、不代选。'),
            _ev('official_candidate_rule',
                '正官结构候选（validated，Golden 20）：'
                '官杀去留 / 混杂未裁定。'),
        ]
        evidence.extend(_official_condition_evidence(ctx))
        return _result(
            ctx, 'zhengguan', 'conflict', evidence,
            ['s055 只作追加审核标注：不定官杀混杂、不定破格、'
             '不定正官格成立与否；两说并列，未裁定。',
             '破格缺口：官杀去留效力、清浊标准、刑冲破害事实层、'
             '轻重推测标尺与身旺门（P6 堵点）均未裁定，'
             '故正官破格条件无，broken 永不输出。'],
            rule_ids=['bazi.phase2.official_pattern_candidates'])
    result = _ten_god_evaluator(
        ctx, 'zhengguan', '正官',
        candidate_rule_id='bazi.phase2.official_pattern_candidates',
        candidate_rule_note='正官结构候选（validated，Golden 20）：'
                            '月藏正官及透干位置观察。',
        no_rule_note='官杀去留 / 混杂、司令、旺衰、真假成败喜用均未裁定。',
        conditions=_official_condition_evidence(ctx),
        broken_gap='破格缺口：官杀去留效力（yh.gs_example_zhifu 行火乡制伏、'
                   'yh.gt_clear 除而清之）与清浊标准未裁定；刑冲破害事实层'
                   '（yh.zg_taboo_xingchong）、轻重推测标尺（yh.zg_qingzhong）'
                   '与身旺门（yh.zg_shenwang_fa，P6 堵点）亦未裁定，'
                   '故正官破格条件无，broken 永不输出。')
    branch = _yuanhai_unexposed_official_branch(ctx)
    if branch is not None:
        result['evidence'].extend(branch)
    return result


def _yuanhai_unexposed_official_branch(ctx):
    """甲日、酉月、辛不透、巳酉丑齐备的单例分支观察（s056）。"""
    if ctx.day_stem != '甲' or ctx.month_branch != '酉':
        return None
    if any(stem == '辛' for stem in ctx.visible_stems.values()):
        return None
    if not {'巳', '酉', '丑'}.issubset(set(ctx.branches)):
        return None
    return [_ev('yuanhai_unexposed_official_s056',
                '甲日酉月、辛不透、巳酉丑齐备：单例结构观察。'),
            _ev('official_candidate_rule',
                '正官结构候选（validated，Golden 20）所含渊海分支。')]


def _hour_killing_positions(ctx):
    """Hour-pillar 七杀 positions (visible stem or hidden stem)."""
    out = []
    if ctx.visible_ten_gods.get('hour') == '七杀':
        out.append(('时干', ctx.visible_stems['hour']))
    hour_hidden = hidden_stems(ctx.branches[3], ctx.day_stem)
    for row in hour_hidden:
        if row['ten_god'] == '七杀':
            out.append(('时支藏', row['stem']))
    return out


def evaluate_qisha(ctx):
    """七杀： no standalone candidate rule; only month-hidden observation
    plus Ren D-1 establishment (Golden t2-bing-qisha). The candidate now
    carries the registered 〈论七杀〉/〈论官星太过〉 condition facts
    (positions, control, combination, wealth-feeding, blade, seven-day
    enumeration); every condition's efficacy stays unadjudicated, so the
    state machine is candidate / established / not_judgeable only."""
    if ctx.earth_gate:
        return ctx.earth_result('qisha')
    conditions = _qisha_condition_evidence(ctx)
    broken_gap = ('破格缺口：制伏效力（yh.qs_control_present / '
                  'yh.qs_control_moderation 制之太过无阈值）、身旺门'
                  '（yh.qs_naming 身旺有气为偏官、身弱无制为七杀）与合杀'
                  '效力（yh.qs_jia_example_control 贪合忘杀）皆未裁定，'
                  '故七杀破格条件无，broken 永不输出。')
    established = ctx.ren_yin_pattern()
    if established is not None and established[0] == '七杀格':
        return _ten_god_evaluator(
            ctx, 'qisha', '七杀',
            candidate_rule_id='bazi.phase2.ren_yin_true_pattern',
            candidate_rule_note='任氏分支寅月真格（validated，Golden 15）。',
            no_rule_note='',
            conditions=conditions, broken_gap=broken_gap)
    return _ten_god_evaluator(
        ctx, 'qisha', '七杀',
        candidate_rule_id='',
        candidate_rule_note='月藏七杀结构观察（无独立七杀候选规则；'
                            '仅见于正官 / 印绶候选块的共现事实与'
                            'ren_yin Golden t2-bing-qisha）。',
        no_rule_note='制杀 / 身旺合杀 / 身弱无制均未裁定；'
                     '《渊海》〈论七杀〉整节已登记，条件事实已接入候选，'
                     '但无一条可操作句可直接执行（登记结论 determination None）。',
        conditions=conditions, broken_gap=broken_gap)


def _resource_evaluator(ctx, pattern_key, god):
    """正印 / 偏印： reviewed candidate rule (Golden 42); s057/s058
    co-presence facts stay indeterminate, never 财旺破印 / 官印相生."""
    if ctx.earth_gate:
        return ctx.earth_result(pattern_key)
    established = ctx.ren_yin_pattern()
    if established is not None and established[0] == god + '格':
        return _ten_god_evaluator(
            ctx, pattern_key, god,
            candidate_rule_id='bazi.phase2.ren_yin_true_pattern',
            candidate_rule_note='任氏分支寅月真格（validated，Golden 15）。',
            no_rule_note='',
            conditions=_resource_condition_evidence(ctx, god),
            broken_gap='破格缺口：财破印效力（yh.yn_wealth_floods / '
                       'yh.yn_wealth_arrives_floods）、偏印夺食效力'
                       '（yh.ds_mechanism）、制杀效力（yh.ds_killing_control）'
                       '与伤官破印效力（yh.zg_shenwang_fa）皆未裁定，'
                       '故印绶破格条件无，broken 永不输出。')
    row = ctx.month_hidden_god(god)
    if row is None:
        return _ten_god_evaluator(
            ctx, pattern_key, god,
            candidate_rule_id='bazi.phase2.resource_pattern_candidates',
            candidate_rule_note='印绶结构候选（validated，Golden 42）。',
            no_rule_note='',
            broken_gap='破格缺口：财破印 / 偏印夺食 / 制杀 / 伤官破印效力皆未裁定，'
                       '故印绶破格条件无，broken 永不输出。')
    result = _ten_god_evaluator(
        ctx, pattern_key, god,
        candidate_rule_id='bazi.phase2.resource_pattern_candidates',
        candidate_rule_note='印绶结构候选（validated，Golden 42）：'
                            '月藏印及透干位置观察。',
        no_rule_note='财旺破印 / 官印相生 / 官鬼多均 indeterminate'
                     '（s057/s058 共现事实只记方向与位置，不判效力）；'
                     '司令、旺衰、真假成败喜用均未裁定。',
        conditions=_resource_condition_evidence(ctx, god),
        broken_gap='破格缺口：财破印效力（yh.yn_wealth_floods / '
                   'yh.yn_wealth_arrives_floods）、偏印夺食效力'
                   '（yh.ds_mechanism）、制杀效力（yh.ds_killing_control）'
                   '与伤官破印效力（yh.zg_shenwang_fa）皆未裁定，'
                   '故印绶破格条件无，broken 永不输出。')
    # Yuanhai s059 month-generating-me example, when it applies.
    if ctx.month_branch in YUANHAI_RESOURCE_MONTHS[ctx.day_stem]:
        result['evidence'].append(_ev(
            'yuanhai_resource_month_example_s059',
            '渊海 s059 月份生我例：%s 日生于 %s 月（仅例举，不定印格）。'
            % (ctx.day_stem, ctx.month_branch)))
    competing = _resource_competing(ctx)
    result['evidence'].extend(competing)
    return result


def _resource_competing(ctx):
    """财 / 官 / 杀与月藏印共现的方向事实（s057/s058），效力未裁定。"""
    out = []
    for name in ('year', 'month', 'hour'):
        god = ctx.visible_ten_gods[name]
        if god in ('正财', '偏财'):
            out.append(_ev('resource_context_visible_wealth',
                           '%s干 %s（%s）与月藏印共现：五行克印方向已见，'
                           '效力 indeterminate。'
                           % (name, ctx.visible_stems[name], god)))
        elif god in ('正官', '七杀'):
            out.append(_ev('resource_context_visible_official_killing',
                           '%s干 %s（%s）与月藏印共现：五行生印方向已见，'
                           '效力 indeterminate。'
                           % (name, ctx.visible_stems[name], god)))
    for row in ctx.month_hidden:
        if row['ten_god'] in ('正财', '偏财', '正官', '七杀'):
            out.append(_ev('resource_context_hidden_actor',
                           '月支藏 %s（%s）与月藏印共现：方向已见，'
                           '效力 indeterminate。'
                           % (row['stem'], row['ten_god'])))
    return out


def evaluate_zhengyin(ctx):
    return _resource_evaluator(ctx, 'zhengyin', '正印')


def evaluate_pianyin(ctx):
    return _resource_evaluator(ctx, 'pianyin', '偏印')


def _wealth_evaluator(ctx, pattern_key, god):
    """正财 / 偏财： no standalone candidate rule; only month-hidden
    observation plus Ren D-1 establishment (Golden t1-wu-zhengcai).
    The candidate now carries the registered 〈论正财〉/〈论偏财〉
    condition facts (positions, robbery, officer, food, exposure)."""
    if ctx.earth_gate:
        return ctx.earth_result(pattern_key)
    conditions = _wealth_condition_evidence(ctx, god)
    broken_gap = ('破格缺口：比劫分夺效力（yh.pc_definition 只恐兄弟姊妹'
                  '有夺之）、财多化官效力（yh.zc_many_transform_officer）'
                  '、财生官链效力（yh.zc_wealth_generates_officer）与财得时'
                  '阈值（yh.zc_timely）皆未裁定，故财格破格条件无，'
                  'broken 永不输出。')
    established = ctx.ren_yin_pattern()
    if established is not None and established[0] == god + '格':
        return _ten_god_evaluator(
            ctx, pattern_key, god,
            candidate_rule_id='bazi.phase2.ren_yin_true_pattern',
            candidate_rule_note='任氏分支寅月真格（validated，Golden 15）。',
            no_rule_note='',
            conditions=conditions, broken_gap=broken_gap)
    return _ten_god_evaluator(
        ctx, pattern_key, god,
        candidate_rule_id='',
        candidate_rule_note='月藏%s结构观察（无独立财格候选规则；'
                            '财只见于印绶候选块的共现事实与'
                            'ren_yin Golden t1-wu-zhengcai）。' % god,
        no_rule_note='身旺任财 / 财多身弱 / 财生官等均未裁定；'
                     '《渊海》〈论正财〉〈论偏财〉整节已登记，条件事实'
                     '已接入候选，但无一条可操作句可直接执行'
                     '（登记结论 determination None）。',
        conditions=conditions, broken_gap=broken_gap)


def evaluate_zhengcai(ctx):
    return _wealth_evaluator(ctx, 'zhengcai', '正财')


def evaluate_piancai(ctx):
    return _wealth_evaluator(ctx, 'piancai', '偏财')


def _food_evaluator(ctx, pattern_key, god):
    """食神 / 伤官： no standalone candidate rule; only month-hidden
    observation plus Ren D-1 establishment (食神 Golden t4-jia-shishen,
    伤官 Golden f2-boundary-exact). The candidate now carries the
    registered 〈论伤官〉/〈论食神〉/〈论倒食〉 condition facts.

    P5 伤官见官 channel (the only classical ``broken`` in this engine):
    a Ren D-1 established 伤官格 with 正官在场 (支干) is ``broken``
    (yh.sw_pattern_no_officer: “如见官星,谓之伤官见官”). The premise
    “用伤官格” is satisfied by the D-1 establishment; “官星” is read
    narrowly as 正官 (七杀 alone does not break -- whether 七杀 counts
    as 官星 here is unadjudicated). A merely candidate 伤官格 stays
    candidate: the premise is unmet, so 见官 is only a modern flag.
    ``broken`` supersedes ``established``: the pattern was established
    and is then vitiated by 见官."""
    if ctx.earth_gate:
        return ctx.earth_result(pattern_key)
    conditions = _food_condition_evidence(ctx, god)
    broken_gap = ('破格缺口：伤官见官效力（yh.sw_pattern_no_officer）、'
                  '伤尽程度标尺（yh.sw_exhaust_core 伤官务要伤尽，程度词'
                  '无标尺，P6 堵点）与倒食夺食效力（yh.ds_mechanism）、'
                  '食神独一位之外多见如何未定（yh.ss_single_position，'
                  '清浊判断不存在）皆未裁定；唯伤官见官在成立前提下有'
                  '古典通道（任氏寅月真格成立 + 正官在场 → broken），'
                  '其余食伤破格条件无。')
    established = ctx.ren_yin_pattern()
    if god == '伤官' and established is not None \
            and established[0] == '伤官格':
        officer = ctx.god_positions('正官')
        if officer:
            killing = ctx.god_positions('七杀')
            return _result(
                ctx, pattern_key, 'broken',
                [_ev('ren_yin_true_pattern',
                     '任氏分支寅月真格成立：司令 %s（伤官）透于 %s。'
                     % (established[1],
                        '、'.join(established[2]) or '无')),
                 _ev('shangguan_sees_officer_broken',
                     '伤官见官破格（yh.sw_pattern_no_officer）：用伤官格者'
                     '支干都要不见官星；正官在场（%s），谓之伤官见官。'
                     '“官星”从窄读为正官；七杀%s，不作破格。'
                     % (ctx.god_position_text(officer),
                        '在场（%s），是否计入官星未裁定'
                        % ctx.god_position_text(killing) if killing
                        else '不在场')),
                 _ev('ren_yin_rule',
                     '依据 bazi.phase2.ren_yin_true_pattern（validated，'
                     'Golden 15；s053 原注定义句 + s054 任氏曰程序句）。')]
                + list(conditions),
                ['破格只裁定见官一事：为祸百端之程度未裁定；'
                 '伤尽程度标尺（P6 堵点）与倒食夺食效力仍未裁定；'
                 '只裁定寅月任氏分支真格成立后见官破格，不外推其他'
                 '月份与流派。',
                 '破格缺口（其余）：伤尽程度标尺仍未裁定；'
                 '本格 broken 通道仅伤官见官一途。'],
                rule_ids=['bazi.phase2.ren_yin_true_pattern'],
                broken_info={
                    'broken_condition': 'shangguan_sees_officer',
                    'broken_evidence_ids':
                        ['shangguan_sees_officer_broken'],
                    'original_state': 'established',
                    'original_pattern': god,
                })
        # Established but no 正官 in 支干: no break; fall through to
        # the established branch below.
    if established is not None and established[0] == god + '格':
        return _ten_god_evaluator(
            ctx, pattern_key, god,
            candidate_rule_id='bazi.phase2.ren_yin_true_pattern',
            candidate_rule_note='任氏分支寅月真格（validated，Golden 15）。',
            no_rule_note='',
            conditions=conditions, broken_gap=broken_gap)
    return _ten_god_evaluator(
        ctx, pattern_key, god,
        candidate_rule_id='',
        candidate_rule_note='月藏%s结构观察（无独立食伤候选规则；'
                            '仅见于 ren_yin Golden：食神 t4-jia-shishen、'
                            '伤官 f2-boundary-exact）。' % god,
        no_rule_note='伤官见官 / 伤尽 / 泄秀等均未裁定；'
                     '《渊海》〈论伤官〉〈论食神〉整节已登记，条件事实'
                     '已接入候选，但无一条可操作句可直接执行'
                     '（登记结论 determination None）；伤官见官古典通道'
                     '只在任氏寅月真格成立前提下开启。',
        conditions=conditions, broken_gap=broken_gap)


def evaluate_shishen(ctx):
    return _food_evaluator(ctx, 'shishen', '食神')


def evaluate_shangguan(ctx):
    return _food_evaluator(ctx, 'shangguan', '伤官')


def evaluate_jianlu(ctx):
    """建禄： the only reviewed material is the negative route exclusion
    (pattern_route, validated Golden 9): a 禄 month closes the month
    pattern route and the borrowed route stays undetermined. No basis
    for candidate / established / broken exists; the evaluator now also
    reports the 日禄 position fact (still not_judgeable) and names the
    gap (《论禄》未逐节登记，建禄成格 determination 恒 None)。"""
    if ctx.earth_gate:
        return ctx.earth_result('jianlu')
    route = ctx.route_value()
    lu = LU_BRANCH[ctx.day_stem]
    conditions = _luren_condition_evidence(ctx, 'lu')
    broken_gap = ('破格缺口：建禄成格 / 破格皆无已审依据（禄刃表只用于'
                  '负向排除；《论禄》未逐节登记）；broken 永不输出。')
    if route == 'luren_no_month_pattern' and ctx.month_branch == lu:
        return _result(
            ctx, 'jianlu', 'not_judgeable',
            [_ev('luren_route_exclusion',
                 '月支 %s 为 %s 日之禄支（三命《论十干禄》）：'
                 '任氏 s054“月逢禄刃，无格可取”，月令正格路线关闭。'
                 % (ctx.month_branch, ctx.day_stem)),
             _ev('luren_route_rule',
                 '依据 bazi.phase2.pattern_route（validated，Golden 9）。')]
            + conditions,
            ['借用路线（“借以为用”）恒未定：借神定名规则未审，'
             '建禄是否成格未裁定；不输出候选、成立或破格。',
             broken_gap],
            rule_ids=['bazi.phase2.pattern_route'])
    return _result(
        ctx, 'jianlu', 'not_judgeable',
        [_ev('no_luren_observation',
             '月支 %s 非 %s 日之禄支（禄在 %s）：无禄刃路线事实。'
             % (ctx.month_branch, ctx.day_stem, lu))]
        + conditions,
        ['建禄成格无已审依据：禄刃表只用于负向排除，不作取格规则。',
         broken_gap],
        rule_ids=['bazi.phase2.pattern_route'])


def evaluate_yangren(ctx):
    """阳刃： same negative-exclusion basis as 建禄. Yin day masters have
    no 刃 branch at all (三命《论阳刃》纲句：五阴干无刃). The evaluator
    now also reports 日刃 / 刃杀俱全 / 刃喜偏财 position facts from the
    registered 〈论阳刃〉/〈论日刃〉 (yh.yr_* / yh.rr_*); all stay
    not_judgeable (阳刃格 / 日刃格 determination 恒 None)。"""
    if ctx.earth_gate:
        return ctx.earth_result('yangren')
    route = ctx.route_value()
    ren = REN_BRANCH.get(ctx.day_stem)
    if ren is None:
        return _result(
            ctx, 'yangren', 'not_judgeable',
            [_ev('yin_stem_no_ren',
                 '%s 为阴干：三命《论阳刃》纲句“五阴干无刃”，无刃支可查。'
                 % ctx.day_stem)],
            ['阴干刃位异说在已登记来源中无逐字依据，不登记、不采用；'
             '阳刃成格无已审依据。',
             '破格缺口：阳刃成格 / 破格皆无已审依据；broken 永不输出。'],
            rule_ids=['bazi.phase2.pattern_route'])
    conditions = _luren_condition_evidence(ctx, 'ren')
    broken_gap = ('破格缺口：阳刃成格 / 破格皆无已审依据（yh.yr_* / yh.rr_* '
                  '可操作句全部经身旺 / 制刃效力 / 印财链 / 支关系效力门'
                  '转手，determination 恒 None）；broken 永不输出。')
    if route == 'luren_no_month_pattern' and ctx.month_branch == ren:
        return _result(
            ctx, 'yangren', 'not_judgeable',
            [_ev('luren_route_exclusion',
                 '月支 %s 为 %s 日之刃支（三命《论阳刃》）：'
                 '任氏 s054“月逢禄刃，无格可取”，月令正格路线关闭。'
                 % (ctx.month_branch, ctx.day_stem)),
             _ev('luren_route_rule',
                 '依据 bazi.phase2.pattern_route（validated，Golden 9）。')]
            + conditions,
            ['借用路线恒未定：借神定名规则未审，'
             '阳刃是否成格未裁定；不输出候选、成立或破格。',
             broken_gap],
            rule_ids=['bazi.phase2.pattern_route'])
    return _result(
        ctx, 'yangren', 'not_judgeable',
        [_ev('no_luren_observation',
             '月支 %s 非 %s 日之刃支（刃在 %s）：无禄刃路线事实。'
             % (ctx.month_branch, ctx.day_stem, ren))]
        + conditions,
        ['阳刃成格无已审依据：禄刃表只用于负向排除，不作取格规则。',
         broken_gap],
        rule_ids=['bazi.phase2.pattern_route'])


def evaluate_zaqi(ctx):
    """杂气： reviewed selection statement + school conflict
    (pattern_zaqi, validated Golden 6). A miscellaneous month is a
    conflict (原注 vs 三命), never a determination."""
    if ctx.earth_gate:
        return ctx.earth_result('zaqi')
    if ctx.month_branch not in MISCELLANEOUS_BRANCHES:
        return _result(
            ctx, 'zaqi', 'not_judgeable',
            [_ev('not_miscellaneous_month',
                 '月支 %s 非四季月（辰戌丑未）：杂气选格陈述不适用。'
                 % ctx.month_branch)],
            ['杂气选格只在四季月有陈述；不等于该盘无杂气之论，'
             '只说明本引擎无依据。',
             '破格缺口：杂气破格条件无已审依据（杂气格无古典 broken 通道）。'],
            rule_ids=['bazi.phase2.pattern_zaqi'])
    if isinstance(ctx.zaqi, dict):
        block = ctx.zaqi
        evidence = [
            _ev('zaqi_selection_statement',
                '杂气选格陈述：臂 %s，状态 %s。'
                % (block.get('arm'), block.get('status'))),
            _ev('zaqi_conflict',
                '流派冲突并列：原注“不可言杂气财官” vs '
                '三命两案以“杂气格”为正式名目（s066/s067），不裁定。'),
            _ev('zaqi_rule',
                '依据 bazi.phase2.pattern_zaqi（validated，Golden 6）。'),
            _zaqi_inventory_evidence(ctx),
            _zaqi_earth_conversion_evidence(ctx),
        ]
        selection = (block.get('selection') or {})
        if selection.get('selected_candidates'):
            evidence.append(_ev(
                'zaqi_selected_candidates',
                '戊己臂选格对象（并列，不代选）：%s。'
                % '、'.join('%s（%s）' % (c['stem'], c['ten_god'])
                            for c in selection['selected_candidates'])))
        elif selection.get('earth_conversion'):
            evidence.append(_ev(
                'zaqi_earth_conversion_unadjudicated',
                '一般臂“只当取土为格”原文并列，土格换算未裁定。'))
        evidence.extend(_zaqi_variant_evidence(
            ctx, {'arm': block.get('arm'),
                  'exposed_renyuan': (block.get('selection') or {}).get(
                      'selected_candidates') or (block.get('exposed_renyuan') or [])}))
        return _result(
            ctx, 'zaqi', 'conflict', evidence,
            ['杂气陈述不是定格：不给格名、真假、成败、清浊、用神或喜忌；'
             '土格换算未审；分日司令未裁定。',
             '破格缺口：杂气破格条件无已审依据；broken 永不输出。'],
            rule_ids=['bazi.phase2.pattern_zaqi'])
    # No precomputed block: reuse the reviewed pure lookup.
    exposed = []
    for row in ctx.month_hidden:
        pillars = ctx.exposed_pillars(row['stem'])
        if pillars:
            exposed.append({'stem': row['stem'], 'ten_god': row['ten_god'],
                            'visible_pillars': pillars})
    lookup = zaqi_selection_lookup(
        ctx.day_stem, ctx.month_branch,
        [{'stem': r['stem'], 'ten_god': r['ten_god']}
         for r in ctx.month_hidden], exposed)
    evidence = [
        _ev('zaqi_selection_statement',
            '杂气选格陈述：臂 %s，状态 %s。'
            % (lookup.get('arm'), lookup.get('status'))),
        _ev('zaqi_conflict',
            '流派冲突并列：原注“不可言杂气财官” vs '
            '三命两案以“杂气格”为正式名目（s066/s067），不裁定。'),
        _ev('zaqi_rule',
            '依据 bazi.phase2.pattern_zaqi（validated，Golden 6）。'),
        _zaqi_inventory_evidence(ctx),
        _zaqi_earth_conversion_evidence(ctx),
    ]
    selection = lookup.get('selection') or {}
    if selection.get('selected_candidates'):
        evidence.append(_ev(
            'zaqi_selected_candidates',
            '戊己臂选格对象（并列，不代选）：%s。'
            % '、'.join('%s（%s）' % (c['stem'], c['ten_god'])
                        for c in selection['selected_candidates'])))
    elif selection.get('earth_conversion'):
        evidence.append(_ev(
            'zaqi_earth_conversion_unadjudicated',
            '一般臂“只当取土为格”原文并列，土格换算未裁定。'))
    evidence.extend(_zaqi_variant_evidence(ctx, lookup))
    return _result(
        ctx, 'zaqi', 'conflict', evidence,
        ['杂气陈述不是定格：不给格名、真假、成败、清浊、用神或喜忌；'
         '土格换算未审；分日司令未裁定。',
         '破格缺口：杂气破格条件无已审依据；broken 永不输出。'],
        rule_ids=['bazi.phase2.pattern_zaqi'])


def _cong_example_matches(ctx):
    """《弃命从杀论》例句结构比对（batch 3，P4 待裁定）。

    十条可比例句（yh.cg_* 登记引文）按日干 / 月支 / 结构根候选 /
    在场十神逐条比对，只报告结构相符与否与各子事实在场情况；
    每条均明言所缺的门（根级 / 极弱档 / 会局成局 / 救援构成），
    比对命中≠从格成立。另两条（yh.cg_xin_si 休囚阶段词、
    yh.cg_ren_xu_month 行运向）无可算盘内结构，不比对。
    """
    out = []
    roots = ctx.structural_roots()
    rootless = not roots
    branches = set(ctx.branches)
    killing = ctx.god_positions('七杀')
    officer_killing = killing + ctx.god_positions('正官')
    wealth = ctx.god_positions('正财') + ctx.god_positions('偏财')
    seal = ctx.god_positions('正印') + ctx.god_positions('偏印')
    robbery = ctx.god_positions('比肩') + ctx.god_positions('劫财')
    root_note = '结构根候选为空；根级未裁定：轻根、墓库之根与待定格均未裁定，逐盘“无根”不能定谳'
    if ctx.day_stem in ('甲', '乙') and rootless and branches & {'申', '酉'}:
        out.append(_ev(
            'cong_example_match_jia_yi_rootless',
            '例句结构相符：yh.cg_jia_yi_rootless 甲乙无根、怕逢申酉——'
            '%s日、%s；申酉支藏庚辛为官杀在场。例句比对≠从杀成立。'
            % (ctx.day_stem, root_note)))
    if ctx.day_stem == '甲' and ctx.month_branch == '丑' and rootless:
        out.append(_ev(
            'cong_example_match_jia_ugly_month',
            '例句结构相符：yh.cg_jia_ugly_month 甲木无根、生于丑月——'
            '%s；印星%s、财官（金土）%s；水多 / 金土多寡比较未阈值化，'
            '印星救援与破弃效力均未裁定。例句比对≠从杀成立。'
            % (root_note,
               '在场（%s）' % ctx.god_position_text(seal) if seal
               else '不在场',
               '在场（%s）' % ctx.god_position_text(
                   wealth + officer_killing) if wealth + officer_killing
               else '不在场')))
    if ctx.day_stem == '乙' and ctx.month_branch == '酉':
        out.append(_ev(
            'cong_example_match_yi_you_month',
            '例句结构相符：yh.cg_yi_you_month 乙木酉月、见水为奇——'
            '印星（水）%s；丑支%s、寅支%s；结构根%s；丑藏干是否成根、'
            '寅藏干何以危均待根级裁定，见水为奇的救援口径未裁定。'
            '例句比对≠从杀成立。'
            % ('在场（%s）' % ctx.god_position_text(seal) if seal
               else '不在场',
               '在场' if '丑' in branches else '不在场',
               '在场' if '寅' in branches else '不在场',
               '在场（%d 处）' % len(roots) if roots else '候选为空')))
    if (ctx.day_stem == '乙' and ctx.branches[2] == '酉'
            and '庚' in ctx.visible_stems.values()
            and '丁' in ctx.visible_stems.values()):
        out.append(_ev(
            'cong_example_match_yi_sitting_you',
            '例句结构相符：yh.cg_yi_sitting_you 乙木坐酉、庚丁透露——'
            '日支酉、庚丁皆透干；二库归根（墓库藏干是否成根）为根级'
            '判定最疑处，未裁定。例句比对≠从杀成立。'))
    if ctx.day_stem == '丙' and ctx.month_branch == '申' and rootless:
        out.append(_ev(
            'cong_example_match_bing_shen_month',
            '例句结构相符：yh.cg_bing_shen_month 丙火申提、无根从杀——'
            '%s；本节题名所系的从杀枢纽句结构。例句比对≠从杀成立。'
            % root_note))
    if ctx.day_stem == '丙' and rootless and officer_killing:
        out.append(_ev(
            'cong_example_match_yang_fire_rootless',
            '例句结构相符：yh.cg_yang_fire_rootless 阳火无根、水乡必忌——'
            '%s；水乡官杀在场（%s）；与阴火句对照登记、不合并读法，'
            '忌之效力未裁定。例句比对≠从杀成立。'
            % (root_note, ctx.god_position_text(officer_killing))))
    if ctx.day_stem == '丁' and rootless and officer_killing:
        out.append(_ev(
            'cong_example_match_yin_fire_rootless',
            '例句结构相符：yh.cg_yin_fire_rootless 阴火无根、水乡有救——'
            '%s；水乡官杀在场（%s）；“有救”之救为何物原文未言，'
            '与阳火句对照登记、不合并读法。例句比对≠从杀成立。'
            % (root_note, ctx.god_position_text(officer_killing))))
    if (ctx.day_stem == '丁' and ctx.month_branch == '酉' and rootless
            and wealth):
        out.append(_ev(
            'cong_example_match_yin_fire_follow_wealth',
            '例句结构相符：yh.cg_yin_fire_follow_wealth 阴火酉月、'
            '弃命就财——%s；财在场（%s）；节内明言从财之句，入格以'
            '从财格成立为前提。例句比对≠从财成立。'
            % (root_note, ctx.god_position_text(wealth))))
    if ctx.day_stem in ('戊', '己') and ctx.month_branch == '亥' and rootless:
        out.append(_ev(
            'cong_example_match_wu_ji_hai_month',
            '例句结构相符：yh.cg_wu_ji_hai_month 戊己亥月、身弱为弃——'
            '%s；比劫%s；身弱程度未阈值化（P6 身旺门），卯月同推'
            '范围原文未界定。例句比对≠从格成立。'
            % (root_note,
               '在场（%s）' % ctx.god_position_text(robbery) if robbery
               else '不在场')))
    if ctx.day_stem == '庚' and rootless and '寅' in branches:
        out.append(_ev(
            'cong_example_match_geng_rootless',
            '例句结构相符：yh.cg_geng_rootless 庚金无根、寅宫火局——'
            '%s；寅支在场；火局成局判定不存在（会局门，P4），'
            '三合火局只记支在场。例句比对≠从杀成立。' % root_note))
    if not out:
        out.append(_ev(
            'cong_example_no_match',
            '从杀论例句结构比对：本盘与十条可比例句结构均不相符'
            '（yh.cg_jia_yi_rootless 等十条）；不等于无从格之论，'
            '只说明例句比对无命中；另两条（yh.cg_xin_si 休囚阶段词、'
            'yh.cg_ren_xu_month 行运向）无可算盘内结构，不比对。'))
    return out


def _special_screens(ctx):
    """特殊格局候选屏（Q11）：屏命中与成立规则分离。每一屏只报告
    结构事实命中与否；命中仍只作 candidate，成立恒无依据。

    - 从杀结构屏（yh.cg_follow_killing_rule 弃命从杀、须要会杀；
      yh.cg_cross_rules_root_negation 命逢根气一票否决）：七杀在场 +
      无结构根 + 无制伏在场 + 无印比救援在场。会杀成局判定不存在。
    - 从财结构屏（yh.cg_follow_wealth_rule 弃命从财、须要会财；
      yh.cg_cross_rules_root_negation 从财忌杀）：财在场 + 无结构根 +
      无七杀在场 + 无比劫分夺在场。会财成局判定不存在。
    - 现代工程从格候选屏（与第一批旺衰现代模型同一窄口径，Q4）：
      无结构根、无显干生扶、显干 >= 2 且全为克我 / 我生方向；
      model_kind="modern_engineering"，古典与现代严格区分。
    - 化气结构屏：天干五合在场事实（reviewed_relations）；五合命中
      不代表化气成立（密封 unresolved，合化效力未裁定）。第三批：
      支六合同属此屏（六合命中亦不代表化气成立）；三合支齐备只作
      事实记录，会局成局判定不存在，不作屏命中。
    - 从杀论例句结构比对（第三批，_cong_example_matches）：十条可比
      例句按日干 / 月支 / 结构根候选 / 在场十神逐条比对，只报告
      结构相符与否；命中≠从格成立。
    - 三奇：三命卷三《论三奇》只见歌诀提及，无可执行规则，不计算，
      只记缺口。
    """
    evidence = []
    limitations = []
    hit = False
    roots = ctx.structural_roots()
    killing = ctx.god_positions('七杀')
    control = ctx.god_positions('食神') + ctx.god_positions('伤官')
    seal = ctx.god_positions('正印') + ctx.god_positions('偏印')
    wealth = ctx.god_positions('正财') + ctx.god_positions('偏财')
    robbery = ctx.god_positions('比肩') + ctx.god_positions('劫财')
    if killing and not roots and not control and not seal and not robbery:
        hit = True
        evidence.append(_ev(
            'congsha_screen_hit',
            '从杀结构屏命中：七杀在场（%s），无结构根、无制伏在场、'
            '无印比救援在场（yh.cg_follow_killing_rule 弃命从杀、须要会杀；'
            'yh.cg_cross_rules_root_negation 命逢根气、命殞无猜——'
            '根气一票否决未触发）。屏命中≠从杀格成立：会杀成局判定'
            '不存在、根级判定未裁、极弱档无定义。'
            % ctx.god_position_text(killing)))
    else:
        reasons = []
        if not killing:
            reasons.append('无七杀在场')
        if roots:
            reasons.append('结构根在场（%d 处），根气一票否决触发'
                           % len(roots))
        if control:
            reasons.append('制伏在场')
        if seal:
            reasons.append('印星救援在场')
        if robbery:
            reasons.append('比劫救援在场')
        evidence.append(_ev(
            'congsha_screen_miss',
            '从杀结构屏未命中：%s。' % '、'.join(reasons)))
    if wealth and not roots and not killing and not robbery:
        hit = True
        evidence.append(_ev(
            'congcai_screen_hit',
            '从财结构屏命中：财在场（%s），无结构根、无七杀在场、'
            '无比劫分夺在场（yh.cg_follow_wealth_rule 弃命从财、须要会财；'
            'yh.cg_cross_rules_root_negation 从财忌杀）。屏命中≠从财格'
            '成立：会财成局判定不存在、根级判定未裁、极弱档无定义。'
            % ctx.god_position_text(wealth)))
    else:
        reasons = []
        if not wealth:
            reasons.append('无财在场')
        if roots:
            reasons.append('结构根在场（%d 处），根气一票否决触发'
                           % len(roots))
        if killing:
            reasons.append('七杀在场（从财忌杀）')
        if robbery:
            reasons.append('比劫分夺在场')
        evidence.append(_ev(
            'congcai_screen_miss',
            '从财结构屏未命中：%s。' % '、'.join(reasons)))
    kinds = ctx.visible_relation_kinds()
    if not roots and len(kinds) >= 2 and all(
            kind in ('controls_me', 'i_generate') for kind in kinds):
        hit = True
        evidence.append(_ev(
            'cong_screen_hit_modern',
            '现代工程从格候选屏命中（model_kind="modern_engineering"，'
            '与第一批旺衰模型同一窄口径 Q4）：无结构根、无显干生扶、'
            '显干 %d 个全为克我 / 我生方向。屏命中≠从格成立：'
            '古典从格成立本身未裁定，现代屏不作古典结论。'
            % len(kinds)))
    else:
        evidence.append(_ev(
            'cong_screen_miss_modern',
            '现代工程从格候选屏未命中：结构根 %d 处、显干关系 %s。'
            % (len(roots), '、'.join(kinds) if kinds else '无')))
    if ctx.five_combinations:
        hit = True
        evidence.append(_ev(
            'huaqi_combination_screen',
            '化气结构屏命中：天干五合在场（%s）。五合命中不代表化气'
            '成立（密封 unresolved；合化效力未裁定）。'
            % '、'.join('%s（%s，化%s）' % (
                '、'.join(pair['pillars']), '＋'.join(pair['stems']),
                pair['traditional_result_element'])
                for pair in ctx.five_combinations)))
    else:
        evidence.append(_ev(
            'huaqi_combination_screen_miss',
            '化气结构屏未命中：四柱天干无五合。'))
    # Batch 3: branch six-harmony belongs to the same 化气结构屏 as
    # the stem five-combination (sealed unresolved: 五合 / 六合命中
    # 不代表化气成立）; triple-harmony branch presence is recorded as
    # a fact only -- 会局成局判定不存在（P4 会局门）, so it never
    # flips the screen on its own.
    if ctx.branch_six_harmonies:
        hit = True
        evidence.append(_ev(
            'huaqi_six_harmony_screen',
            '化气结构屏命中（支六合）：%s。六合命中不代表化气成立'
            '（密封 unresolved；合化效力未裁定）。'
            % '、'.join('%s（%s，化%s）' % (
                '、'.join(pair['pillars']), '＋'.join(pair['branches']),
                pair['traditional_result_element'])
                for pair in ctx.branch_six_harmonies)))
    else:
        evidence.append(_ev(
            'huaqi_six_harmony_screen_miss',
            '化气结构屏（支六合）未命中：四柱地支无六合。'))
    if ctx.branch_triple_harmonies:
        evidence.append(_ev(
            'huaqi_triple_harmony_present',
            '三合支齐备事实：%s。只记支在场事实；会局成局判定不'
            '存在（P4 会局门），不成局、不作化气屏命中。'
            % '、'.join('%s（%s，化%s）' % (
                '、'.join(pair['pillars']), '＋'.join(pair['branches']),
                pair['traditional_result_element'])
                for pair in ctx.branch_triple_harmonies)))
    else:
        evidence.append(_ev(
            'huaqi_triple_harmony_absent',
            '三合支未齐备事实：四柱地支无三合局支集。'))
    # P4 modern facts (pattern-modern-p6-v1): root grade, extreme-weak
    # band and the triple-harmony assembly screen are recorded here as
    # evidence facts; the verdicts live in modern_assessment.
    root_grade = _modern_root_grade(ctx)
    extreme_weak = _modern_extreme_weak(ctx)
    evidence.append(_ev(
        'cong_root_grade_modern',
        '现代根级（%s）：结构根候选 %d 处%s；古典根级（轻根 / 墓库'
        '之根 / 待定格）未裁定。'
        % (root_grade['grade'], root_grade['root_count'],
           '、有同干根' if root_grade['same_stem_root'] else '、无同干根')))
    evidence.append(_ev(
        'cong_extreme_weak_band_modern',
        '现代极弱档（%s）：结构根 %d 处、显干生扶 %d 干、显干克泄耗 '
        '%d 干；古典极弱档无定义。'
        % (extreme_weak['band'], extreme_weak['root_count'],
           extreme_weak['visible_support_count'],
           extreme_weak['visible_opposing_count'])))
    cong = _cong_modern(ctx)
    for assembly in cong['assemblies']:
        evidence.append(_ev(
            'cong_assembly_screen_modern',
            '现代会局屏（%s）：三合支 %s 化 %s，化神透干%s；'
            '古典会局成局判定不存在，只作现代屏记录。'
            % (assembly['assembly_modern'],
               '、'.join(assembly['branches']),
               assembly['result_element'],
               '（%s）' % '、'.join(assembly['transforming_stems'])
               if assembly['transforming_stems'] else '（无）')))
    evidence.extend(_cong_example_matches(ctx))
    limitations.append(
        '三奇缺口：三命卷三《论三奇》只见歌诀提及，无可执行规则，'
        '本引擎不计算三奇。')
    limitations.append(
        '从格 / 化气成立恒无依据：从杀、从财格 determination 恒 None'
        '（yh.cg_* 登记结论）；化气成立以合化裁定为前提，合化未裁定。')
    limitations.append(
        '破格缺口：从格 / 化气破格条件无已审依据；broken 永不输出。')
    return hit, evidence, limitations


def evaluate_special(ctx):
    """特殊格局（从格 / 化气 / 三奇等）： no reviewed establishment rule.
    Sealed unresolved: 五合命中不代表化气成立；格局未完成证据裁定；
    factors() leaves 从格 / 旺极衰极 unlisted. v2 reports the four
    separated candidate screens (从杀 / 从财 / 现代从格屏 / 化气);
    a screen hit is a candidate, never an establishment."""
    if ctx.earth_gate:
        return ctx.earth_result('special')
    hit, evidence, limitations = _special_screens(ctx)
    base = [
        _ev('no_special_pattern_rule',
            '密封 phase2_execution 无从格 / 化气 / 三奇等特殊格局成立规则；'
            'unresolved 明言“旺衰、格局、喜用神尚未完成证据裁定”。'),
        _ev('huaqi_not_established',
            '五合 / 六合命中不代表化气成立（密封 unresolved）。'),
        _ev('strength_factors_unresolved',
            'factors() 未纳入从格、旺极衰极与阴阳十二长生；'
            'overall_strength 为 None。'),
    ]
    if hit:
        return _result(
            ctx, 'special', 'candidate', base + evidence,
            ['候选屏命中≠特殊格局成立：不得以屏命中推定从格、化气格'
             '或任何外格；需新的逐项证据裁定与用户裁定。'] + limitations,
            rule_ids=[])
    return _result(
        ctx, 'special', 'not_judgeable', base + evidence,
        ['特殊格局全部未裁定：不得以月令、合化或旺衰因素推定从格、'
         '化气格或任何外格；需新的逐项证据裁定与用户裁定。'] + limitations,
        rule_ids=[])


def _extra_ten_god_evaluator(ctx, pattern_key, god):
    """比肩 / 劫财： only reachable through Ren D-1 (Golden a2/a4)."""
    if ctx.earth_gate:
        return ctx.earth_result(pattern_key)
    established = ctx.ren_yin_pattern()
    if established is not None and established[0] == god + '格':
        result = _ten_god_evaluator(
            ctx, pattern_key, god,
            candidate_rule_id='bazi.phase2.ren_yin_true_pattern',
            candidate_rule_note='任氏分支寅月真格（validated，Golden 15）。',
            no_rule_note='',
            broken_gap='破格缺口：比肩 / 劫财破格条件无已审依据'
                       '（比肩格 / 劫财格只见于任氏 D-1 机械换算名）。')
        result['limitations'].append(
            '公开投影白名单外：%s 不在已审八格公开名目内，'
            '公开呈现时为 not_judgeable（pattern_name_not_public）。' % (god + '格'))
        return result
    return None


def _extra_commander_not_visible_result(ctx, pattern_key, god, stem):
    """A1: D-1 commander_not_visible whose commander ten god is 比肩/劫财.

    The commander fact belongs on the ten-god pattern whose god the
    commander is. State stays not_judgeable; no establishment claim
    is made, and the D-1 public presentation is unchanged (the two
    names stay outside the reviewed eight-name whitelist).
    """
    if god == '比肩':
        commander_note = '司令干即日干 %s' % stem
    else:
        commander_note = '司令干 %s 与日干同五行异阴阳' % stem
    return _result(
        ctx, pattern_key, 'not_judgeable',
        [_ev('ren_yin_commander_not_visible',
             '寅月司令为 %s（%s）但不透：结论止于“无真格”，'
             '永不标“假格”。' % (god, commander_note)),
         _ev('no_%s_basis' % pattern_key,
             '%s格只见于任氏 D-1 机械换算名，本盘未成立。' % god)],
        ['%s不属本批十二格；司令不透只记事实，不作任何成立宣称。' % god,
         '破格缺口：比肩 / 劫财破格条件无已审依据。'],
        rule_ids=[])


def evaluate_bijian(ctx):
    result = _extra_ten_god_evaluator(ctx, 'bijian', '比肩')
    if result is not None:
        return result
    god, stem = ctx.ren_yin_commander_not_visible_full()
    if god == '比肩':
        return _extra_commander_not_visible_result(
            ctx, 'bijian', '比肩', stem)
    return _result(
        ctx, 'bijian', 'not_judgeable',
        [_ev('no_bijian_basis', '比肩格只见于任氏 D-1 机械换算名，本盘未成立。')],
        ['比肩不属本批十二格；无 D-1 成立即无依据。',
         '破格缺口：比肩 / 劫财破格条件无已审依据。'],
        rule_ids=[])


def evaluate_jiecai(ctx):
    result = _extra_ten_god_evaluator(ctx, 'jiecai', '劫财')
    if result is not None:
        return result
    god, stem = ctx.ren_yin_commander_not_visible_full()
    if god == '劫财':
        return _extra_commander_not_visible_result(
            ctx, 'jiecai', '劫财', stem)
    return _result(
        ctx, 'jiecai', 'not_judgeable',
        [_ev('no_jiecai_basis', '劫财格只见于任氏 D-1 机械换算名，本盘未成立。')],
        ['劫财不属本批十二格；无 D-1 成立即无依据。',
         '破格缺口：比肩 / 劫财破格条件无已审依据。'],
        rule_ids=[])


_EVALUATORS = {
    'zhengguan': evaluate_zhengguan,
    'qisha': evaluate_qisha,
    'zhengyin': evaluate_zhengyin,
    'pianyin': evaluate_pianyin,
    'zhengcai': evaluate_zhengcai,
    'piancai': evaluate_piancai,
    'shishen': evaluate_shishen,
    'shangguan': evaluate_shangguan,
    'jianlu': evaluate_jianlu,
    'yangren': evaluate_yangren,
    'zaqi': evaluate_zaqi,
    'special': evaluate_special,
    'bijian': evaluate_bijian,
    'jiecai': evaluate_jiecai,
}


def evaluate_pattern(chart, pattern_key, *, official=None, resource=None,
                     route=None, zaqi=None, ren_yin=None):
    """Evaluate one pattern over a ``chart_from_pillars`` chart."""
    if pattern_key not in _EVALUATORS:
        raise ValueError('Unknown pattern key: %s' % pattern_key)
    ctx = _Context(chart, official=official, resource=resource, route=route,
                   zaqi=zaqi, ren_yin=ren_yin)
    return _EVALUATORS[pattern_key](ctx)


def evaluate_all(chart, *, official=None, resource=None, route=None,
                 zaqi=None, ren_yin=None):
    """Evaluate all twelve patterns plus the two Ren D-1 extra ten-god
    names (比肩/劫财) over a ``chart_from_pillars`` chart.

    The extras are always present (A1): they stay not_judgeable unless
    Ren D-1 establishes them, and they carry the commander_not_visible
    fact when the D-1 commander ten god is 比肩/劫财. They are not
    part of the twelve patterns and never enter the public projection.

    Optional precomputed reviewed blocks (from a trace) are consumed as
    evidence; otherwise each evaluator computes the same structural
    facts directly from the pillars.
    """
    ctx = _Context(chart, official=official, resource=resource, route=route,
                   zaqi=zaqi, ren_yin=ren_yin)
    results = {key: _EVALUATORS[key](ctx) for key, _, _ in PATTERNS}
    # A1: always present, not_judgeable unless D-1 establishes them.
    results['bijian'] = _EVALUATORS['bijian'](ctx)
    results['jiecai'] = _EVALUATORS['jiecai'](ctx)
    counts = {}
    for result in results.values():
        counts[result['state']] = counts.get(result['state'], 0) + 1
    return {
        'variant': PATTERN_ENGINE_VARIANT,
        'pattern_variant': PATTERN_VARIANT,
        'ren_yin_determination_variant': REN_YIN_TRUE_VARIANT,
        'luren_route_variant': LUREN_ROUTE_VARIANT,
        'modern_model': MODERN_MODEL_ID,
        'day_stem': ctx.day_stem,
        'month_branch': ctx.month_branch,
        'earth_gate': ctx.earth_gate,
        'strength_overall': ctx.strength_factors['overall_strength'],
        'results': results,
        'counts': counts,
        'research_only': True,
        'public': False,
        'ai': False,
        'scope': ('十二格逐格评估（研究用）加比肩 / 劫财两格常驻：成立只认'
                  '任氏寅月真格；候选附各格已登记条件事实（在场可算、'
                  '效力未裁定；第三批新增暗藏官杀、透藏区分、例句结构'
                  '比对、六合 / 三合屏事实与杂气月藏全清单）；破格仅'
                  '伤官见官一途（任氏寅月真格成立 + 正官在场），其余'
                  '破格缺口见各结果 limitations 与 broken_gaps 具名表，'
                  'P6 两门堵点只登记、不立标尺；现代工程层另见各结果 '
                  'modern_assessment（pattern-modern-p6-v1），古典规则'
                  '与现代工程判断严格区分。'),
    }


def _trace_view(trace):
    if hasattr(trace, 'steps') and hasattr(trace, 'evidence'):
        return trace
    if isinstance(trace, dict) and 'trace' in trace and 'evidence' in trace:
        class _View:
            pass
        view = _View()
        view.steps = trace['trace']
        view.evidence = trace['evidence']
        return view
    raise ValueError('Pattern engine requires an executed trace')


def evaluate_patterns_from_trace(trace, *, pilot_result=None):
    """Evaluate all patterns from an executed bazi trace.

    Reuses the reviewed blocks (candidates / route / zaqi / ren_yin)
    from ``bazi_pattern``; ``pilot_result`` is the explicit Slice C
    pilot block (None means no Ren D-1 determination is attempted).
    Fails closed when the required executed steps are absent.
    """
    view = _trace_view(trace)
    steps = {row['rule_id']: row for row in view.steps}
    required = ('pillars', 'ten_gods', 'hidden_stems', 'hidden_to_visible',
                'month_command_variant')
    if any('bazi.phase2.' + name not in steps for name in required):
        raise ValueError('Pattern engine trace lacks executed structural steps')
    for name in required:
        step = steps['bazi.phase2.' + name]
        if not step['evidence_ids'] or any(
                e not in view.evidence for e in step['evidence_ids']):
            raise ValueError('Pattern engine trace lacks executed evidence')
    pillars_out = steps['bazi.phase2.pillars']['output']
    ganzhi = pillars_out['ganzhi']
    chart = {
        'pillars': [
            {'name': name,
             'stem': {'value': ganzhi[i][0]},
             'branch': {'value': ganzhi[i][1]}}
            for i, name in enumerate(('year', 'month', 'day', 'hour'))
        ],
        'day_master': {'stem': pillars_out['day_master']['stem']},
    }
    official = _pattern_candidates(view, family='official')
    resource = _pattern_candidates(view, family='resource')
    route = month_pattern_route(view)
    zaqi = month_pattern_zaqi(view)
    ren_yin = (ren_yin_true_pattern(view, pilot_result)
               if pilot_result is not None else None)
    return evaluate_all(chart, official=official, resource=resource,
                        route=route, zaqi=zaqi, ren_yin=ren_yin)
