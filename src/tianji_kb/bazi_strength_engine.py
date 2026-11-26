"""旺衰引擎 TJ-0424：古典窄形态充分谓词（因素层）＋现代工程化模型，并列输出。

研究级（research_only / public_enabled=False / ai_enabled=False），
不接任何公开场景，不新增公开 API 字段，不改任何现有模块。

两层严格区分，绝不强制统一：

* 古典层（``classical``）：消费 :func:`bazi_strength.factors` 的因素
  输出与公开登记表（火根表、金/水根表、土根消费契约），按 7 条已审
  窄形态充分谓词逐条求值。求值口径是**因素层**（factor level）：
  它复现各谓词在 ``bazi_action_conditions`` 登记的条件键，但不执行
  密封裁决链（``strength_assessment`` 仍是唯一能发出密封裁决的出口，
  须在装配运行时上执行）。因此本层命中只报告
  ``verification="factor_level_only"``，并逐条附密封 validation 状态
  与 Golden 引用；命中不等于密封裁决已发出。7 条之外（丙×寅长生
  形态待注册、从格、喜用、格局、吉凶）一律不判。
* 现代层（``modern``，``strength_model_modern_v1``）：对因素贡献做
  确定性评分。权重与阈值全写在 :data:`MODERN_WEIGHTS` 与
  :data:`MODERN_THRESHOLDS`，输出恒标 ``model_kind="modern_engineering"``、
  ``research_only=true``。它是工程近似，不是古籍原文，不冒充古典规则。

Fail-closed 弃判（现代层）：戊×巳 / 己×午（TJ-011.2 UNBUILDABLE）、
巳月无已验证司令试点结果、已追踪的合化结构在场（化气候选无依据）、
从格候选屏（无根、无显扶、显干全为克/泄/财方向，且无已审谓词已命中）。
古典层不受现代层弃判影响，两层并列、冲突显式呈现于 ``agreement``。

第二批（P0-1 旺衰完整性，Q1–Q9 2026-11-25 裁定）新增的可调用能力，
全部 research_only，不改已钉住的权重、阈值与既有算例分：

* :func:`coverage_matrix` —— 十日主 × 十二月令 120 格全覆盖探针，
  每格显式给出 computed / abstain / error，不静默缺失。
* 分项解释 —— 每个现代分项输出数值、来源构成（逐干/逐根贡献与
  计入/封顶状态）与适用条件，见 ``modern['components'][*]`` 的
  ``sources`` / ``conditions``。
* 四库月（Q6）与土/丁得地（Q5）—— 得令零记为缺失条件暂定处理，
  分类不确定性由 ``classification_status`` /
  ``definite_classification`` / ``uncertainty_flags`` 显式标注；
  土/丁日主只出研究性暂定分数，不出确定旺衰分类。
* :func:`identify_cong_candidates` —— 从强/从弱/从财候选识别
  （Q4：从财候选屏已扩展含我克方向）；候选屏与成立规则严格分离，
  候选恒标 ``establishment="not_judged"``，命中不判从格。
* :func:`interaction_conditions` —— 合冲刑害条件作用模型（Q3 选 A）：
  逐条记录作用条件与模型局限，冲/害/六合只记录、不扣分、不全面弃判。
* :func:`sensitivity_analysis` —— 阈值/权重扰动对分类的影响，
  可调用、可复算，不是一次性手算。
* :func:`divergence_explanation` —— 古典/现代分歧的并列解释：
  双方裁决、证据链与分歧原因，不强制统一。
* :func:`audit_component_counts` / :func:`validate_assessment` ——
  总分上下限、重复计分、边界阈值与规则冲突的普遍校验。
"""

import copy

from .bazi_core import PILLAR_NAMES, foundations, reviewed_relations
from .bazi_earth_roots import EARTH_CONSUMPTION_CONTRACT
from .bazi_fire_morphology import (
    BING_ALL_ROOT_BRANCHES, BING_HEAVY_ROOT_BRANCHES, BING_ROOT_POSITIONS)
from .bazi_metal_water_roots import (
    HEAVY_ROOT_BRANCHES as MW_HEAVY_ROOT_BRANCHES,
    METAL_WATER_ROOT_TABLES)
from .bazi_strength import FACTOR_VARIANT, factors
from .foundations import BRANCHES, CONTROLS, GENERATES, STEMS, stem_element

ENGINE_VARIANT = 'bazi-strength-engine-v1'
MODERN_MODEL_ID = 'strength_model_modern_v1'
SI_PILOT_VARIANT = 'bazi-siling-si-pilot-v1'

# 因素层代理根集：木/水/金的已审根支取自公开材料——木集引
# bazi_action_conditions 注释所引原文「如甲乙逢亥寅卯之类是也」；
# 水集 {亥, 子} 与金集 {酉} 与既有公开测试
# test_tj0112_bing_si_lu.py::test_sealed_policy_not_edited 所断言的
# reviewed_root_branches 一致。此处是因素层代理口径，密封 policy
# 本身仍是权威且未被改动；代理口径只严不宽（集外根一律不计有效）。
_WOOD_REVIEWED_ROOTS = frozenset(('亥', '寅', '卯'))
_WATER_REVIEWED_ROOTS = frozenset(('亥', '子'))
_GOLD_REVIEWED_ROOTS = frozenset(('酉',))

# 月支本气（principal qi）取 canonical 藏干表首干，并在每次求值时与
# 7 条谓词所涉已审本气交叉核对；任一不符即 registration_integrity_failure。
# 四库（辰/未/戌/丑）本气未审：现代层得令分在该月恒为 0 并标注依据。
_REVIEWED_PRINCIPAL_QI = {
    '卯': '乙', '亥': '壬', '酉': '辛', '子': '癸', '巳': '丙', '午': '丁',
}
_TOMB_BRANCHES = frozenset(('辰', '未', '戌', '丑'))
_SUPPORT_RELATIONS = ('same_element', 'generates_me')
_OPPOSE_RELATIONS = ('i_generate', 'controls_me', 'i_control')

# 土根消费契约（E0257/E0355，公开模块 bazi_earth_roots）：仅
# Wu x Si、Ji x Wu 两格可计，与 bazi_action_conditions 同式推导。
_EARTH_ELIGIBLE_ROOT_CELLS = frozenset(
    (cell.split('×')[0], cell.split('×')[1])
    for gc in EARTH_CONSUMPTION_CONTRACT['grade_contracts']
    if gc['eligibility'] == 'eligible' for cell in gc['cells'])

_MW_TABLES = {stem: {entry['branch']: entry for entry in rows}
              for stem, rows in METAL_WATER_ROOT_TABLES.items()}
_MW_HEAVY_GRADES = ('per_stem_listed', 'framework_derived')
_FIRE_CONFLICT_BRANCHES = frozenset(
    entry['branch'] for entry in BING_ROOT_POSITIONS
    if entry['grade'] == 'light_listed_conflicted')

# 现代模型权重（strength_model_modern_v1）：分项、权重、上下限全在此。
# 总分域 [-35, 105]。阈值见 MODERN_THRESHOLDS。
MODERN_WEIGHTS = {
    'de_ling': {  # 得令：月支本气关系（巳月以已验证试点司令干为准）
        'same_element': 30, 'generates_me': 20, 'i_generate': 5,
        'i_control': 0, 'controls_me': -15,
        'tomb_principal_unreviewed': 0,
        'range': [-15, 30],
    },
    'de_di': {  # 得地：重根 +15/个（至多 2 个），余根 +5/个（至多 2 个），同干根 +5
        'heavy_root_each': 15, 'heavy_root_max_count': 2,
        'other_root_each': 5, 'other_root_max_count': 2,
        'same_stem_root_bonus': 5, 'cap': 35, 'range': [0, 35],
    },
    'de_shi': {  # 得势：显干生扶 +10/干
        'visible_support_each': 10, 'cap': 30, 'range': [0, 30],
    },
    'shengfu_hidden': {  # 藏干生扶：+2/干
        'hidden_support_each': 2, 'cap': 10, 'range': [0, 10],
    },
    'kexiehao': {  # 克泄耗：克/泄/耗干 -2/干
        'opposing_each': -2, 'floor': -20, 'range': [-20, 0],
    },
}
MODERN_THRESHOLDS = {
    'strong_at_least': 60,   # 总分 >= 60 判 strong
    'weak_at_most': 15,      # 总分 <= 15 判 weak
    'balanced_between': (16, 59),  # 其余为 balanced（现代模型标签，非古典裁决）
}

# TJ-011.2 UNBUILDABLE：土日主在两格上无任何可执行形态规则。
_EARTH_UNBUILDABLE = frozenset((('戊', '巳'), ('己', '午')))

# 7 条古典窄形态充分谓词。sealed_validation / sealed_golden_* 为
# 2026-11-25 机上密封核实值（密封 phase2_execution.json；
# 另见 ~/workspace/tj-sealed-audit-20261125.txt）；public_golden_refs
# 为公开 Golden 文件中的见证用例 id。条件键与
# bazi_action_conditions 登记的 scope 条件键同名。
PREDICATES = (
    {
        'predicate_id': 'pure_support',
        'name_cn': '木月卯纯印比强',
        'phase1_rule_id': 'bazi.rule.r024',
        'phase2_step_id': 'bazi.phase2.strength_pure_support',
        'classification': 'strong',
        'sealed_validation': 'validated',
        'sealed_golden_ids': ['bazi.adjudication-strong-wood-sites',
                              'bazi.adjudication-strong-water-sites'],
        'public_golden_refs': [
            'tests/golden_tj0112_wood_hai.json'
            '#tj0112-regression-mao-pure-support'],
        'condition_keys': [
            'wood_day_master', 'reviewed_same_element_month',
            'all_positions_support_only', 'visible印_present',
            'visible比_present', 'effective_day_roots',
            'all_visible_have_reviewed_roots', 'no_unresolved_interactions'],
    },
    {
        'predicate_id': 'isolated_control',
        'name_cn': '木月酉孤立无根无扶弱',
        'phase1_rule_id': 'bazi.rule.r025',
        'phase2_step_id': 'bazi.phase2.strength_isolated_control',
        'classification': 'weak',
        'sealed_validation': 'validated',
        'sealed_golden_ids': ['bazi.adjudication-weak-yang',
                              'bazi.adjudication-weak-yin'],
        'public_golden_refs': [
            'tests/golden_tj0112_wood_hai.json'
            '#tj0112-regression-you-isolated-control'],
        'condition_keys': [
            'wood_day_master', 'reviewed_control_month',
            'day_has_no_structural_root', 'no_support_in_any_position',
            'visible_earth_metal_only', 'month_principal_exposed_with_root',
            'no_unresolved_interactions'],
    },
    {
        'predicate_id': 'pure_generating_support',
        'name_cn': '木月亥纯印比生扶强',
        'phase1_rule_id': 'bazi.rule.r029',
        'phase2_step_id': 'bazi.phase2.strength_pure_generating_support',
        'classification': 'strong',
        'sealed_validation': 'validated',
        'sealed_golden_ids': ['bazi.adjudication-strong-hai-generating'],
        'public_golden_refs': [
            'tests/golden_tj0112_wood_hai.json'
            '#tj0112-hai-positive-zhongqi-root',
            'tests/golden_tj0112_wood_hai.json'
            '#tj0112-hai-positive-benqi-root'],
        'condition_keys': [
            'wood_day_master', 'reviewed_generating_month',
            'all_positions_support_only', 'visible印_present',
            'visible比_present', 'effective_day_roots',
            'all_visible_have_reviewed_roots', 'no_unresolved_interactions'],
    },
    {
        'predicate_id': 'commanding_visible_support',
        'name_cn': '丙午当令显纯生扶强',
        'phase1_rule_id': 'bazi.rule.r030',
        'phase2_step_id': 'bazi.phase2.strength_commanding_visible_support',
        'classification': 'strong',
        'sealed_validation': 'validated',
        'sealed_golden_ids': ['bazi.adjudication-strong-bingwu-commanding'],
        'public_golden_refs': [
            'tests/golden_tj0112_bing_wu_commanding.json'
            '#tj0112-bingwu-positive'],
        'condition_keys': [
            'fire_day_master_bing', 'reviewed_same_element_command_month',
            'visible_positions_support_only', 'visible_resource_present',
            'visible_peer_present', 'effective_heavy_day_roots',
            'all_visible_have_reviewed_roots', 'no_unresolved_interactions',
            'hidden_layer_convention_applied'],
    },
    {
        'predicate_id': 'lu_visible_support',
        'name_cn': '丙巳禄位显纯生扶强',
        'phase1_rule_id': 'bazi.rule.r032',
        'phase2_step_id': 'bazi.phase2.strength_lu_visible_support',
        'classification': 'strong',
        'sealed_validation': 'validated',
        'sealed_golden_ids': ['bazi.strength-ganzhi-lu-positive'],
        'public_golden_refs': [
            'tests/golden_tj0112_bing_si_lu.json#tj0112-bingsi-positive'],
        'condition_keys': [
            'fire_day_master_bing', 'reviewed_lu_command_month',
            'visible_positions_support_only', 'visible_resource_present',
            'visible_peer_present', 'effective_heavy_day_roots',
            'all_visible_have_reviewed_roots', 'no_unresolved_interactions',
            'hidden_layer_convention_applied'],
    },
    {
        'predicate_id': 'pure_support_metal',
        'name_cn': '金酉月纯同类强',
        'phase1_rule_id': 'bazi.rule.r033',
        'phase2_step_id': 'bazi.phase2.strength_pure_support_metal',
        'classification': 'strong',
        'sealed_validation': 'pending',
        'sealed_golden_ids': [
            'bazi.strength-ganzhi-metal-negative-xin-clashed-roots',
            'bazi.strength-ganzhi-metal-negative-geng-stem-combination'],
        'public_golden_refs': [
            'tests/golden_tj0112_s2_metal_water.json'
            '#tj0112-s2-metal-near-miss-xin-clashed-roots',
            'tests/golden_tj0112_s2_metal_water.json'
            '#tj0112-s2-metal-near-miss-geng-stem-combination'],
        'condition_keys': [
            'metal_day_master', 'reviewed_same_element_month_you',
            'all_positions_support_only', 'visible印_present',
            'visible比_present', 'effective_day_roots_registered',
            'all_visible_have_registered_roots', 'no_unresolved_interactions'],
    },
    {
        'predicate_id': 'pure_generating_support_water',
        'name_cn': '水子月纯生扶强',
        'phase1_rule_id': 'bazi.rule.r034',
        'phase2_step_id': 'bazi.phase2.strength_pure_generating_support_water',
        'classification': 'strong',
        'sealed_validation': 'validated',
        'sealed_golden_ids': ['bazi.strength-ganzhi-water-positive'],
        'public_golden_refs': [
            'tests/golden_tj0112_s2_metal_water.json'
            '#tj0112-s2-water-positive-gui'],
        'condition_keys': [
            'water_day_master', 'reviewed_same_element_month_zi',
            'all_positions_support_only', 'visible印_present',
            'visible比_present', 'effective_day_roots_registered',
            'all_visible_have_registered_roots', 'no_unresolved_interactions'],
    },
)

CLASSICAL_LIMITATIONS = (
    '古典层是因素层求值，不是密封裁决：命中谓词须经装配运行时上的 '
    'strength_assessment（bazi-strength-adjudication-v1）发出密封裁决，'
    '本层命中本身不构成裁决。',
    '仅 7 条已审窄形态充分谓词；其余形态（丙×寅长生形态待注册、从格、'
    '喜用、格局、吉凶）一律暂不可判，不由本层推断。',
    '金×酉谓词 validation pending（密封 Golden 仅 2 条负例），且已证在'
    '真实历法命盘上构造性不可满足：本层命中只作因素层条件核对，绝不'
    '呈现为已验证正例。',
    '分日司令不进入古典层（裁决层 excluded_dependencies 含 '
    'dated_commander）；巳月/寅月试点判定只供现代层得令参考，不改古典谓词。',
    '三刑事实不进入本层（三刑事实层不解锁任何 '
    'determination，也不进 unresolved_interactions）。',
)

MODERN_LIMITATIONS = (
    '现代模型是工程近似：权重与阈值是人为设定的可解释评分口径，不是'
    '古籍原文、不是已审规则；任何现代 verdict 不得表述为古典裁决。',
    '土日主无已审重根集，得地分只计余根；丁日主火重根集未审，得地分'
    '只计余根；四库月得令分恒为 0（本气未审）。',
    '现代模型不处理大运、流年、格局、喜用与吉凶；balanced 是现代模型'
    '标签，不是古典「中和」裁决。',
    '现代模型不对地支冲、害、六合计分（仅三合与天干五合触发弃判）：'
    '一盘带冲/害仍可得高分（如金酉近 miss 辛盘现代 strong 83，而古典层'
    '因子冲未决为 indeterminate），此为已知分歧，见裁定说明。',
    '巳月现代评分以试点司令干计得令；试点未验证时现代层弃判，不以外推补足。',
    # Q3 选 A：冲/害/六合只记录作用条件与模型局限，不扣分、不全面弃判。
    'Q3-A：地支冲、害、六合在 interaction_effects 中逐条记录作用条件与'
    '局限，score_adjustment 恒为 0；天干五合与地支三合仍因化气未决而弃判，'
    '那是化气候选无依据的弃判，不是冲/害/合的扣分。',
    # Q4：从财候选屏已扩展，但候选恒不等于成立。
    'Q4：从格候选屏含从财方向（显干全为克/泄/财方向时触发）；候选识别与'
    '从格成立规则严格分离，cong_candidates 恒标 establishment=not_judged，'
    '命中结构不直接判从格。',
    # Q5/Q6：分类不确定性以 classification_status 显式标注。
    'Q5：土日主与丁日主得地未校准，只出研究性暂定分数，'
    'definite_classification 为 None，不输出确定旺衰分类。',
    'Q6：四库月得令分记 0 是缺失条件的暂定处理（本气未审），不代表已证明'
    '月令无作用；该盘 classification_status 为 uncertain，分类不确定性显式标注。',
)

# 现代模型总分域（分项上下限之和：-15+0+0+0-20 = -35；30+35+30+10+0 = 105）。
MODERN_SCORE_RANGE = (-35, 105)

# 从格候选屏方向集（Q4 扩展后）：克我 / 我生 / 我克（财）。
_CONG_OPPOSE_RELATIONS = ('controls_me', 'i_generate', 'i_control')
# 从弱窄口径（Q4 之前）：仅克我 / 我生。
_CONG_WEAK_RELATIONS = ('controls_me', 'i_generate')

GLOBAL_LIMITATIONS = (
    '本引擎 research_only / public_enabled=false / ai_enabled=false，'
    '不接任何公开场景；输出不含喜用神、格局、吉凶、婚恋、事业、财富断语。',
    '古典谓词与现代模型并列输出，不强制统一；冲突时以 agreement 块'
    '显式呈现，不以任一侧覆盖另一侧。',
)


def _relation_of(day_element, target_element):
    """Five-element relation of a target element relative to the day element."""
    if target_element == day_element:
        return 'same_element'
    if GENERATES[target_element] == day_element:
        return 'generates_me'
    if GENERATES[day_element] == target_element:
        return 'i_generate'
    if CONTROLS[target_element] == day_element:
        return 'controls_me'
    return 'i_control'


def _principal_qi(month_branch):
    """Month principal qi: first hidden stem of the canonical table.

    Cross-checked against the register-stated principals of the six
    reviewed branches; any drift is a registration integrity failure.
    """
    table = foundations()['hidden_stems']
    principal = table[month_branch][0]
    for branch, expected in _REVIEWED_PRINCIPAL_QI.items():
        if table[branch][0] != expected:
            raise RuntimeError(
                'registration_integrity_failure: principal qi of %s is %s, '
                'expected registered %s' % (branch, table[branch][0], expected))
    return principal


def _visible_root_positions(pillars, stem):
    """Branches hiding a same-element stem for one visible stem."""
    table = foundations()['hidden_stems']
    element = stem_element(stem)
    positions = []
    for pillar in pillars:
        branch = pillar['branch']['value']
        for hidden in table[branch]:
            if stem_element(hidden) == element:
                positions.append({'pillar': pillar['name'], 'branch': branch,
                                  'hidden_stem': hidden,
                                  'same_stem': hidden == stem})
    return positions


def _mw_grade(stem, branch):
    entry = _MW_TABLES.get(stem, {}).get(branch)
    return entry['grade'] if entry is not None else None


def _validate_pillars(pillars, day_master):
    if day_master not in STEMS:
        raise ValueError('Expected one heavenly stem as day_master')
    if not isinstance(pillars, (list, tuple)) or len(pillars) != 4:
        raise ValueError('Expected four ordered pillars')
    if tuple(p['name'] for p in pillars) != PILLAR_NAMES:
        raise ValueError('Expected ordered year/month/day/hour pillars')
    if pillars[2]['stem']['value'] != day_master:
        raise ValueError('day_master does not match the day pillar stem')
    for pillar in pillars:
        if pillar['stem']['value'] not in STEMS:
            raise ValueError('Invalid heavenly stem in pillars')
        if pillar['branch']['value'] not in BRANCHES:
            raise ValueError('Invalid earthly branch in pillars')


def _summarize_factors(pillars, day_master, factor_output):
    """Condense factors() into the evidence-chain factor breakdown."""
    stems = [p['stem']['value'] for p in pillars]
    branches = [p['branch']['value'] for p in pillars]
    relations = reviewed_relations(stems, branches)
    month_branch = branches[1]
    principal = _principal_qi(month_branch)
    day_element = stem_element(day_master)
    principal_relation = _relation_of(day_element, stem_element(principal))
    support = factor_output['support_relations']
    visible = [{'pillar': row['pillar'], 'stem': row['stem'],
                'element': row['element'], 'relation': row['relation'],
                'ten_god': row['ten_god']}
               for row in support['visible_positions']]
    hidden = [{'pillar': row['pillar'], 'branch': row['branch'],
               'stem': row['stem'], 'element': row['element'],
               'relation': row['relation'], 'ten_god': row['ten_god']}
              for row in support['hidden_positions']]
    roots = [{'pillar': row['pillar'], 'branch': row['branch'],
              'hidden_stem': row['hidden_stem'],
              'same_stem': row['same_stem']}
             for row in factor_output['root_candidates']['positions']]
    interaction_kinds = [key for key in (
        'stem_five_combinations', 'branch_six_harmonies', 'branch_six_harms',
        'branch_six_clashes', 'branch_triple_harmonies') if relations[key]]
    return {
        'factor_variant': factor_output['factor_variant'],
        'month_branch': month_branch,
        'principal_qi': principal,
        'principal_relation': principal_relation,
        'visible_positions': visible,
        'hidden_positions': hidden,
        'root_positions': roots,
        'interactions': {
            'present': bool(interaction_kinds),
            'kinds': interaction_kinds,
            'stem_five_combinations': relations['stem_five_combinations'],
            'branch_six_harmonies': relations['branch_six_harmonies'],
            'branch_six_harms': relations['branch_six_harms'],
            'branch_six_clashes': relations['branch_six_clashes'],
            'branch_triple_harmonies': relations['branch_triple_harmonies'],
        },
    }


def _reviewed_roots_for(element):
    if element == '木':
        return _WOOD_REVIEWED_ROOTS
    if element == '水':
        return _WATER_REVIEWED_ROOTS
    if element == '金':
        return _GOLD_REVIEWED_ROOTS
    return frozenset()


def _heavy_roots_for(day_master):
    """Modern-model heavy-root branch set for one day-master stem."""
    element = stem_element(day_master)
    if element == '木':
        return set(_WOOD_REVIEWED_ROOTS)
    if element == '火':
        return set(BING_HEAVY_ROOT_BRANCHES) if day_master == '丙' else set()
    if element in ('金', '水'):
        return set(MW_HEAVY_ROOT_BRANCHES.get(day_master, []))
    return set()  # 土：无已审重根集


def _classical_layer(pillars, summary, day_master):
    """Factor-level evaluation of the 7 registered sufficient predicates."""
    day_element = stem_element(day_master)
    month_branch = summary['month_branch']
    principal_relation = summary['principal_relation']
    visible = summary['visible_positions']
    hidden = summary['hidden_positions']
    roots = summary['root_positions']
    no_interactions = not summary['interactions']['present']

    visible_roots = {row['stem']: _visible_root_positions(pillars, row['stem'])
                     for row in visible}
    visible_support_only = all(
        row['relation'] in _SUPPORT_RELATIONS for row in visible)
    all_support_only = visible_support_only and all(
        row['relation'] in _SUPPORT_RELATIONS for row in hidden)
    visible_resource = any(
        row['relation'] == 'generates_me' for row in visible)
    visible_peer = any(
        row['relation'] == 'same_element' for row in visible)
    no_support_anywhere = all(
        row['relation'] not in _SUPPORT_RELATIONS
        for row in visible + hidden)

    def have_reviewed_roots(reviewed_for):
        for row in visible:
            allowed = reviewed_for(row['element'])
            if not any(pos['branch'] in allowed
                       for pos in visible_roots[row['stem']]):
                return False
        return True

    def wood_effective():
        return bool(roots) and all(
            row['branch'] in _WOOD_REVIEWED_ROOTS for row in roots)

    def fire_effective_heavy():
        return bool(roots) \
            and any(row['branch'] in BING_HEAVY_ROOT_BRANCHES
                    for row in roots) \
            and all(row['branch'] not in _FIRE_CONFLICT_BRANCHES
                    for row in roots)

    def fire_have_reviewed_roots():
        for row in visible:
            if row['element'] == '火':
                allowed = BING_ALL_ROOT_BRANCHES
            elif row['element'] == '木':
                allowed = _WOOD_REVIEWED_ROOTS
            else:
                return False
            if not any(pos['branch'] in allowed
                       for pos in visible_roots[row['stem']]):
                return False
        return True

    def mw_effective():
        return bool(roots) and all(
            _mw_grade(day_master, row['branch']) in _MW_HEAVY_GRADES
            for row in roots)

    def mw_have_registered_roots():
        for row in visible:
            stem = row['stem']
            positions = visible_roots[stem]
            if stem in ('戊', '己'):
                if not any((stem, pos['branch'])
                           in _EARTH_ELIGIBLE_ROOT_CELLS
                           for pos in positions):
                    return False
            else:
                table = _MW_TABLES.get(stem)
                if table is not None:
                    if not any(
                            (table.get(pos['branch']) or {}).get('grade')
                            not in ('no_root', 'conflicted_pending', None)
                            for pos in positions):
                        return False
                else:
                    allowed = _reviewed_roots_for(row['element'])
                    if not any(pos['branch'] in allowed
                               for pos in positions):
                        return False
        return True

    wood = day_element == '木'
    evaluated = {}

    evaluated['pure_support'] = {
        'wood_day_master': wood,
        'reviewed_same_element_month':
            month_branch == '卯' and principal_relation == 'same_element',
        'all_positions_support_only': all_support_only,
        'visible印_present': visible_resource,
        'visible比_present': visible_peer,
        'effective_day_roots': wood_effective(),
        'all_visible_have_reviewed_roots': have_reviewed_roots(
            _reviewed_roots_for),
        'no_unresolved_interactions': no_interactions,
    }
    evaluated['isolated_control'] = {
        'wood_day_master': wood,
        'reviewed_control_month':
            month_branch == '酉' and principal_relation == 'controls_me',
        'day_has_no_structural_root': not roots,
        'no_support_in_any_position': no_support_anywhere,
        'visible_earth_metal_only': all(
            row['element'] in ('土', '金') for row in visible),
        'month_principal_exposed_with_root': (
            _principal_qi(month_branch) in [row['stem'] for row in visible]
            and any(pos['branch'] in _GOLD_REVIEWED_ROOTS
                    for pos in visible_roots.get(
                        _principal_qi(month_branch), []))),
        'no_unresolved_interactions': no_interactions,
    }
    evaluated['pure_generating_support'] = {
        'wood_day_master': wood,
        'reviewed_generating_month':
            month_branch == '亥' and principal_relation == 'generates_me',
        'all_positions_support_only': all_support_only,
        'visible印_present': visible_resource,
        'visible比_present': visible_peer,
        'effective_day_roots': wood_effective(),
        'all_visible_have_reviewed_roots': have_reviewed_roots(
            _reviewed_roots_for),
        'no_unresolved_interactions': no_interactions,
    }
    fire_conditions = {
        'fire_day_master_bing': day_master == '丙',
        'visible_positions_support_only': visible_support_only,
        'visible_resource_present': visible_resource,
        'visible_peer_present': visible_peer,
        'effective_heavy_day_roots': fire_effective_heavy(),
        'all_visible_have_reviewed_roots': fire_have_reviewed_roots(),
        'no_unresolved_interactions': no_interactions,
        # 治理约定（非原文）：藏干只作根位事实，不否决、不计效。
        'hidden_layer_convention_applied': True,
    }
    evaluated['commanding_visible_support'] = {
        'fire_day_master_bing': fire_conditions['fire_day_master_bing'],
        'reviewed_same_element_command_month':
            month_branch == '午' and principal_relation == 'same_element',
        **{k: v for k, v in fire_conditions.items()
           if k != 'fire_day_master_bing'},
    }
    evaluated['lu_visible_support'] = {
        'fire_day_master_bing': fire_conditions['fire_day_master_bing'],
        'reviewed_lu_command_month':
            month_branch == '巳' and principal_relation == 'same_element',
        **{k: v for k, v in fire_conditions.items()
           if k != 'fire_day_master_bing'},
    }
    evaluated['pure_support_metal'] = {
        'metal_day_master': day_element == '金',
        'reviewed_same_element_month_you':
            month_branch == '酉' and principal_relation == 'same_element',
        'all_positions_support_only': all_support_only,
        'visible印_present': visible_resource,
        'visible比_present': visible_peer,
        'effective_day_roots_registered': mw_effective(),
        'all_visible_have_registered_roots': mw_have_registered_roots(),
        'no_unresolved_interactions': no_interactions,
    }
    evaluated['pure_generating_support_water'] = {
        'water_day_master': day_element == '水',
        'reviewed_same_element_month_zi':
            month_branch == '子' and principal_relation == 'same_element',
        'all_positions_support_only': all_support_only,
        'visible印_present': visible_resource,
        'visible比_present': visible_peer,
        'effective_day_roots_registered': mw_effective(),
        'all_visible_have_registered_roots': mw_have_registered_roots(),
        'no_unresolved_interactions': no_interactions,
    }

    results = []
    matched = None
    for spec in PREDICATES:
        conditions = evaluated[spec['predicate_id']]
        if list(conditions) != spec['condition_keys']:
            raise RuntimeError(
                'registration_integrity_failure: condition keys of %s '
                'drifted from the registered scope'
                % spec['predicate_id'])
        met = all(conditions.values())
        entry = {
            'predicate_id': spec['predicate_id'],
            'name_cn': spec['name_cn'],
            'phase1_rule_id': spec['phase1_rule_id'],
            'phase2_step_id': spec['phase2_step_id'],
            'classification': spec['classification'],
            'sealed_validation': spec['sealed_validation'],
            'sealed_golden_ids': list(spec['sealed_golden_ids']),
            'public_golden_refs': list(spec['public_golden_refs']),
            'conditions': dict(conditions),
            'met': met,
            'verification': 'factor_level_only',
        }
        if spec['predicate_id'] == 'pure_support_metal':
            entry['notes'] = (
                'validation pending；密封 Golden 仅 2 条负例；'
                '真实历法命盘构造性不可满足——命中只作因素层条件核对，'
                '绝不呈现为已验证正例。')
        results.append(entry)
        if met and matched is None:
            matched = entry
    if matched is not None and sum(1 for r in results if r['met']) > 1:
        raise RuntimeError(
            'registration_integrity_failure: more than one sufficient '
            'predicate matched at factor level: %s'
            % [r['predicate_id'] for r in results if r['met']])

    blockers = []
    if matched is None:
        blockers.append('outside_reviewed_sufficient_conditions')
    if (day_master, month_branch) in _EARTH_UNBUILDABLE:
        blockers.append('earth_form_unbuildable_tj0112')
    return {
        'layer': 'classical_factor_level',
        'verification': 'factor_level_only',
        'research_only': True, 'public_enabled': False, 'ai_enabled': False,
        'classification': matched['classification'] if matched
                          else 'indeterminate',
        'matched_predicate': matched,
        'predicates': results,
        'blockers': blockers,
        'limitations': list(CLASSICAL_LIMITATIONS),
    }


def _resolve_weights(overrides):
    """Deep-copy MODERN_WEIGHTS with an optional partial override merged in.

    Overrides are never written back to the module-level tables: a
    sensitivity run must not move the pinned v1 weights for later calls.
    """
    weights = copy.deepcopy(MODERN_WEIGHTS)
    if overrides:
        for section, patch in overrides.items():
            if section not in weights:
                raise ValueError('Unknown modern weight section: %s' % section)
            if not isinstance(patch, dict):
                raise ValueError('Weight override for %s must be a mapping'
                                 % section)
            weights[section].update(patch)
    return weights


def _resolve_thresholds(overrides):
    """Copy MODERN_THRESHOLDS with an optional partial override merged in."""
    thresholds = dict(MODERN_THRESHOLDS)
    if overrides:
        for key, value in overrides.items():
            if key not in thresholds:
                raise ValueError('Unknown modern threshold: %s' % key)
            thresholds[key] = value
    if thresholds['weak_at_most'] >= thresholds['strong_at_least']:
        raise ValueError('Thresholds must keep weak_at_most < strong_at_least: '
                         '%s' % (thresholds,))
    return thresholds


def _band_for_score(score, thresholds):
    """Score-band label for a total under the given thresholds.

    Boundary-exact: score == strong_at_least is strong, score ==
    weak_at_most is weak; 16–59 under v1 thresholds is balanced.
    """
    if score >= thresholds['strong_at_least']:
        return 'strong'
    if score <= thresholds['weak_at_most']:
        return 'weak'
    return 'balanced'


def _classification_status(day_master, month_branch):
    """Q5/Q6 classification status for one computed modern score.

    Returns (status, uncertainty_flags, notes): ``definite`` only when
    neither the de_di calibration gap (earth day-master / 丁) nor the
    tomb-month de_ling gap applies; ``provisional_incomplete`` for the
    Q5 gap (research provisional score, no definite classification);
    ``uncertain`` for the Q6 gap alone (de_ling zero is a provisional
    missing-condition treatment, not proof the month branch has no effect).
    """
    flags = []
    notes = []
    if stem_element(day_master) == '土':
        flags.append('earth_de_di_uncalibrated')
        notes.append('土日主无已审重根集：得地分只计余根，未校准；'
                     '分数为研究性暂定分，不输出确定旺衰分类。')
    if day_master == '丁':
        flags.append('ding_de_di_uncalibrated')
        notes.append('丁日主火重根集未审（丁长生冲突未裁定）：得地分只计余根，'
                     '未校准；分数为研究性暂定分，不输出确定旺衰分类。')
    if month_branch in _TOMB_BRANCHES:
        flags.append('tomb_de_ling_zero_provisional')
        notes.append('月支 %s 为四库，本气未审：得令分记 0 是缺失条件的暂定'
                     '处理，不代表已证明月令无作用；分类不确定性已标注。'
                     % month_branch)
    if 'earth_de_di_uncalibrated' in flags \
            or 'ding_de_di_uncalibrated' in flags:
        return 'provisional_incomplete', flags, notes
    if flags:
        return 'uncertain', flags, notes
    return 'definite', flags, notes


def identify_cong_candidates(pillars, day_master):
    """Identify 从格 candidates (cong_qiang / cong_ruo / cong_cai) — screen only.

    Q4: the cong_cai screen is expanded to include the i_control (财)
    direction; the old cong_ruo screen (controls_me / i_generate only)
    is kept as a sub-case. A candidate is NEVER an establishment verdict:
    every candidate carries ``establishment="not_judged"`` and
    ``verdict=None`` — no reviewed establishment rule exists, so a hit
    on the screen cannot directly judge a cong pattern. ``screen_triggered``
    is true exactly when the no-root / no-visible-support / all-visible-
    opposing screen fires; only that screen (and only when no reviewed
    classical predicate matched) makes the modern layer abstain.
    """
    _validate_pillars(pillars, day_master)
    factor_output = factors(pillars, day_master)
    summary = _summarize_factors(pillars, day_master, factor_output)
    visible = summary['visible_positions']
    roots = summary['root_positions']
    visible_relations = [row['relation'] for row in visible]
    has_roots = bool(roots)
    has_visible_support = any(
        rel in _SUPPORT_RELATIONS for rel in visible_relations)
    all_opposing_expanded = len(visible_relations) >= 2 and all(
        rel in _CONG_OPPOSE_RELATIONS for rel in visible_relations)
    all_opposing_weak = len(visible_relations) >= 2 and all(
        rel in _CONG_WEAK_RELATIONS for rel in visible_relations)
    has_cai_direction = any(
        rel == 'i_control' for rel in visible_relations)
    screen_base = not has_roots and not has_visible_support
    candidates = []
    if screen_base and all_opposing_expanded:
        if has_cai_direction:
            kind, name_cn = 'cong_cai', '从财候选'
            detail = ('无根、无显干生扶、显干全为克/泄/财方向且至少一干为'
                      '我克（财）：从财候选屏命中。')
        else:
            kind, name_cn = 'cong_ruo', '从弱候选'
            detail = ('无根、无显干生扶、显干全为克/泄方向：从弱候选屏命中。')
        candidates.append({
            'kind': kind, 'name_cn': name_cn,
            'trigger_conditions': {
                'no_roots': not has_roots,
                'no_visible_support': not has_visible_support,
                'visible_all_opposing_expanded': all_opposing_expanded,
                'visible_all_opposing_weak_narrow': all_opposing_weak,
                'has_i_control_direction': has_cai_direction,
                'visible_count_at_least_2': len(visible_relations) >= 2,
            },
            'evidence': {
                'root_count': len(roots),
                'visible_relations': list(visible_relations),
                'visible_stems': [row['stem'] for row in visible],
            },
            'detail': detail,
            'establishment': 'not_judged',
            'establishment_reason': ('从格成立规则未审：候选屏命中只说明'
                                     '结构符合候选条件，不等于从格成立；'
                                     '无已审成立规则可消费，verdict 恒为 None。'),
            'verdict': None,
        })
    # 从强候选（仅识别，不触发弃判）：显干全生扶、无显干克泄耗、
    # 重根不少于 2 处、月令本气为同类或生我。强侧跟随候选，不是强弱裁决。
    heavy = _heavy_roots_for(day_master)
    heavy_count = sum(1 for row in roots if row['branch'] in heavy)
    visible_all_support = bool(visible_relations) and all(
        rel in _SUPPORT_RELATIONS for rel in visible_relations)
    if visible_all_support and heavy_count >= 2 and \
            summary['principal_relation'] in ('same_element', 'generates_me'):
        candidates.append({
            'kind': 'cong_qiang', 'name_cn': '从强候选',
            'trigger_conditions': {
                'visible_all_support': visible_all_support,
                'heavy_roots_at_least_2': heavy_count >= 2,
                'principal_relation_supporting':
                    summary['principal_relation'] in (
                        'same_element', 'generates_me'),
            },
            'evidence': {
                'root_count': len(roots),
                'heavy_root_count': heavy_count,
                'visible_relations': list(visible_relations),
                'principal_relation': summary['principal_relation'],
            },
            'detail': ('显干全生扶、重根不少于 2 处、月令本气同类或生我：'
                       '从强候选屏命中；仅作候选识别，不触发弃判。'),
            'establishment': 'not_judged',
            'establishment_reason': ('从格成立规则未审：候选屏命中只说明'
                                     '结构符合候选条件，不等于从格成立；'
                                     '无已审成立规则可消费，verdict 恒为 None。'),
            'verdict': None,
        })
    screen_triggered = screen_base and all_opposing_expanded
    return {
        'model_kind': 'modern_engineering',
        'research_only': True, 'public_enabled': False, 'ai_enabled': False,
        'candidates': candidates,
        'screen_triggered': screen_triggered,
        'screen_kinds': [c['kind'] for c in candidates
                         if c['kind'] in ('cong_ruo', 'cong_cai')],
        'screen_reason': 'cong_candidate_unresolved' if screen_triggered
                         else None,
        'screen_detail': candidates[0]['detail'] if screen_triggered else None,
        'note': ('候选屏与成立规则严格分离：本函数只输出候选识别，'
                 '永不输出从格成立/不成立的裁决。'),
    }


def interaction_conditions(pillars, day_master):
    """Conditional model for 合 / 冲 / 刑 / 害 (Q3 option A).

    Every tracked interaction is recorded with its acting conditions and
    model limits. 地支冲、害、六合 are recorded only: ``score_adjustment``
    is always 0, no blanket abstention, and no unadjudicated deduction
    rule is added. 天干五合与地支三合 are recorded the same way, but the
    modern layer still abstains on them as a whole
    (``transformation_candidate_unresolved``) because 化气是否成立无依据 —
    that is a transformation abstention, not a deduction for 冲/害/合.
    三刑事实不进入本函数（事实层不解锁任何 determination）。
    """
    _validate_pillars(pillars, day_master)
    factor_output = factors(pillars, day_master)
    summary = _summarize_factors(pillars, day_master, factor_output)
    relations = summary['interactions']
    records = []

    def record(kind, name_cn, pillars_involved, extra, conditions,
               effect, limitation):
        entry = {
            'kind': kind, 'name_cn': name_cn,
            'pillars': list(pillars_involved),
            'effect_on_strength': effect,
            'score_adjustment': 0 if effect == 'recorded_only_no_score_adjustment'
                                else None,
            'conditions': list(conditions),
            'limitation': limitation,
            'model_kind': 'modern_engineering',
            'research_only': True,
        }
        entry.update(extra)
        records.append(entry)

    for item in relations['stem_five_combinations']:
        record('stem_five_combination', '天干五合', item['pillars'],
               {'stems': list(item['stems']),
                'traditional_result_element':
                    item['traditional_result_element']},
               ['化气是否成立未裁定', '化神是否得令得地未裁定',
                '合而不化与合化两种可能均未排除'],
               'abstain_transformation_unresolved',
               'Q3-A：天干五合只记录化气未决的条件；现代层因此整体弃判，'
               '不以合化后的五行计分，也不扣分。')
    for item in relations['branch_six_harmonies']:
        record('branch_six_harmony', '地支六合', item['pillars'],
               {'branches': list(item['branches']),
                'traditional_result_element':
                    item['traditional_result_element']},
               ['合化是否成立未裁定', '合是否增力/破根未裁定'],
               'recorded_only_no_score_adjustment',
               'Q3-A：六合只记录作用条件与局限；现代模型不合化计分、不扣分、'
               '不全面弃判。')
    for item in relations['branch_six_harms']:
        record('branch_six_harm', '地支六害', item['pillars'],
               {'branches': list(item['branches'])},
               ['害是否破根未裁定', '害是否减力未裁定', '害的应事效力未裁定'],
               'recorded_only_no_score_adjustment',
               'Q3-A：六害只记录作用条件与局限；现代模型不扣分、不全面弃判。')
    for item in relations['branch_six_clashes']:
        record('branch_six_clash', '地支六冲', item['pillars'],
               {'branches': list(item['branches'])},
               ['冲是否破根未裁定', '冲动与冲散两种可能均未排除',
                '月令受冲的效力未裁定'],
               'recorded_only_no_score_adjustment',
               'Q3-A：六冲只记录作用条件与局限；现代模型不扣分、不全面弃判。')
    for item in relations['branch_triple_harmonies']:
        record('branch_triple_harmony', '地支三合', item['pillars'],
               {'branches': list(item['branches']),
                'traditional_result_element':
                    item['traditional_result_element']},
               ['化气是否成立未裁定', '三合化神是否得令得地未裁定'],
               'abstain_transformation_unresolved',
               'Q3-A：地支三合只记录化气未决的条件；现代层因此整体弃判，'
               '不以合化后的五行计分，也不扣分。')
    return {
        'model_kind': 'modern_engineering',
        'research_only': True, 'public_enabled': False, 'ai_enabled': False,
        'records': records,
        'has_interactions': bool(records),
        'score_adjustment_total': 0,
        'note': ('Q3 选 A：冲/害/六合逐条记录作用条件与模型局限，'
                 'score_adjustment 恒为 0，不追加未经裁定的扣分规则；'
                 '仅天干五合与地支三合因化气未决触发整体弃判。'),
    }


def _validate_si_pilot(pilot, month_branch):
    """Validate a supplied Si-pilot result; return (commander, problem).

    ``commander`` is the pilot's commander stem when the result is a
    verified computed pilot for this 巳月 chart, else None. ``problem``
    is None, 'not_verified' or 'invalid'.
    """
    if not isinstance(pilot, dict):
        return None, 'not_verified'
    if pilot.get('variant') != SI_PILOT_VARIANT:
        return None, 'invalid'
    if pilot.get('research_only') is not True \
            or pilot.get('public_enabled') is not False \
            or pilot.get('ai_enabled') is not False:
        return None, 'invalid'
    if pilot.get('status') != 'computed':
        return None, 'not_verified'
    commander = pilot.get('commander')
    if commander not in STEMS:
        return None, 'invalid'
    if pilot.get('month_branch') != '巳' \
            and pilot.get('scope_month_branch') != '巳':
        return None, 'invalid'
    if month_branch != '巳':
        return None, 'invalid'
    return commander, None


def _modern_layer(pillars, summary, day_master, classical, siling_si_pilot,
                  weights=None, thresholds=None):
    """Deterministic engineering score (strength_model_modern_v1).

    ``weights`` / ``thresholds`` are optional partial overrides used by
    :func:`sensitivity_analysis`; the pinned v1 tables are never mutated.
    """
    month_branch = summary['month_branch']
    day_element = stem_element(day_master)
    visible = summary['visible_positions']
    hidden = summary['hidden_positions']
    roots = summary['root_positions']
    relations = summary['interactions']
    limitations = list(MODERN_LIMITATIONS)
    notes = []
    weights = _resolve_weights(weights)
    thresholds = _resolve_thresholds(thresholds)
    cong = identify_cong_candidates(pillars, day_master)
    interactions = interaction_conditions(pillars, day_master)

    def abstain(reason, detail):
        return {
            'model_id': MODERN_MODEL_ID,
            'model_kind': 'modern_engineering',
            'research_only': True, 'public_enabled': False,
            'ai_enabled': False,
            'verdict': 'abstain',
            'score': None,
            'score_band': None,
            'classification_status': 'abstain',
            'definite_classification': None,
            'uncertainty_flags': [],
            'thresholds': dict(thresholds),
            'weights': weights,
            'components': None,
            'abstain_reason': reason,
            'abstain_detail': detail,
            'cong_candidates': cong,
            'interaction_effects': interactions,
            'limitations': limitations,
            'notes': notes,
        }

    # 弃判 1：土日主两格无任何可执行形态规则（TJ-011.2 UNBUILDABLE）。
    if (day_master, month_branch) in _EARTH_UNBUILDABLE:
        return abstain(
            'earth_form_unbuildable_tj0112',
            '日主 %s × 月支 %s 属 TJ-011.2 UNBUILDABLE，土形态无可执行'
            '规则，现代模型不评分。' % (day_master, month_branch))

    # 弃判 2：巳月须有已验证的司令试点结果，否则得令无据。
    commander = None
    pilot_problem = None
    if month_branch == '巳':
        commander, pilot_problem = _validate_si_pilot(
            siling_si_pilot, month_branch)
        if commander is None:
            if siling_si_pilot is not None and pilot_problem == 'invalid':
                return abstain(
                    'siling_si_pilot_invalid',
                    '传入的巳月司令试点结果形状或治理旗标不符，不采信。')
            return abstain(
                'siling_si_pilot_not_verified',
                '巳月现代评分须以已验证的司令试点（%s，computed）计得令；'
                '未提供或未算出时弃判，不以外推补足。' % SI_PILOT_VARIANT)
    elif siling_si_pilot is not None:
        notes.append('siling_si_pilot_ignored_not_si_month')

    # 弃判 3：已追踪的合化结构在场——化气候选无依据。
    if relations['stem_five_combinations'] \
            or relations['branch_triple_harmonies']:
        return abstain(
            'transformation_candidate_unresolved',
            '在场合化结构（天干五合 %d 组 / 地支三合 %d 组）效力未裁定；'
            '化气是否成立无依据，现代模型不评分。' % (
                len(relations['stem_five_combinations']),
                len(relations['branch_triple_harmonies'])))

    # 弃判 4：从格候选屏——仅当无已审谓词命中时适用（已审弱谓词命中的
    # 盘不是从格候选，见 isolated_control：月令官星显而有根）。Q4 扩展后
    # 屏集合为克/泄/财三方向（controls_me / i_generate / i_control）；
    # 屏命中只触发弃判，候选种类见 cong_candidates，成立恒不判。
    classical_matched = classical['matched_predicate'] is not None
    if not classical_matched and cong['screen_triggered']:
        return abstain(
            'cong_candidate_unresolved',
            '从格候选（%s）：%s'
            % ('/'.join(cong['screen_kinds']), cong['screen_detail']))

    # 得令：巳月以试点司令干为准；四库月本气未审，恒 0；其余以本气关系计。
    if month_branch == '巳':
        de_ling_relation = _relation_of(
            day_element, stem_element(commander))
        de_ling = weights['de_ling'][de_ling_relation]
        de_ling_basis = 'siling_si_pilot_commander_%s_%s' % (
            commander, de_ling_relation)
        de_ling_sources = [{
            'kind': 'siling_si_pilot_commander', 'branch': month_branch,
            'stem': commander, 'relation': de_ling_relation,
            'weight': de_ling, 'contribution': de_ling, 'counted': True}]
        de_ling_conditions = [
            '巳月得令以已验证试点司令干计，不以本气丙计',
            '试点 variant=%s，status=computed' % SI_PILOT_VARIANT,
            '司令干 %s 对日主 %s 的关系为 %s' % (
                commander, day_master, de_ling_relation)]
    elif month_branch in _TOMB_BRANCHES:
        de_ling = weights['de_ling']['tomb_principal_unreviewed']
        de_ling_basis = 'tomb_principal_unreviewed'
        de_ling_sources = [{
            'kind': 'tomb_principal_unreviewed', 'branch': month_branch,
            'stem': _principal_qi(month_branch),
            'relation': 'unreviewed', 'weight': 0, 'contribution': 0,
            'counted': True}]
        de_ling_conditions = [
            '四库月本气未审：得令分恒记 0（Q6）',
            '零是缺失条件的暂定处理，不代表已证明月令无作用',
            '分类不确定性见 classification_status=uncertain / '
            'uncertainty_flags=tomb_de_ling_zero_provisional']
        limitations.append(
            '本盘月支 %s 为四库，本气未审：得令分记 0，不以外推计分。'
            % month_branch)
    else:
        de_ling_relation = summary['principal_relation']
        de_ling = weights['de_ling'][de_ling_relation]
        de_ling_basis = 'principal_qi_%s_%s' % (
            summary['principal_qi'], de_ling_relation)
        de_ling_sources = [{
            'kind': 'principal_qi', 'branch': month_branch,
            'stem': summary['principal_qi'], 'relation': de_ling_relation,
            'weight': de_ling, 'contribution': de_ling, 'counted': True}]
        de_ling_conditions = [
            '月支 %s 本气 %s 对日主 %s 的关系为 %s' % (
                month_branch, summary['principal_qi'], day_master,
                de_ling_relation),
            '权重按 MODERN_WEIGHTS[de_ling][%s]=%d' % (
                de_ling_relation, de_ling)]

    # 得地：重根 / 余根 / 同干根，逐根列出贡献与计入/封顶状态。
    heavy = _heavy_roots_for(day_master)
    heavy_count = sum(1 for row in roots if row['branch'] in heavy)
    other_count = len(roots) - heavy_count
    heavy_counted = min(heavy_count,
                        weights['de_di']['heavy_root_max_count'])
    other_counted = min(other_count,
                        weights['de_di']['other_root_max_count'])
    de_di_sources = []
    _within_count_cap = []
    heavy_seen = 0
    other_seen = 0
    for row in roots:
        is_heavy = row['branch'] in heavy
        if is_heavy:
            heavy_seen += 1
            within = heavy_seen <= heavy_counted
            raw = weights['de_di']['heavy_root_each']
            grade = 'heavy'
        else:
            other_seen += 1
            within = other_seen <= other_counted
            raw = weights['de_di']['other_root_each']
            grade = 'other'
        de_di_sources.append({
            'kind': 'root', 'pillar': row['pillar'], 'branch': row['branch'],
            'hidden_stem': row['hidden_stem'], 'same_stem': row['same_stem'],
            'grade': grade, 'raw_contribution': raw,
            'contribution': 0, 'counted': False})
        _within_count_cap.append(within)
    same_stem_bonus = weights['de_di']['same_stem_root_bonus'] \
        if any(row['same_stem'] for row in roots) else 0
    de_di_sources.append({
        'kind': 'same_stem_root_bonus',
        'raw_contribution': same_stem_bonus,
        'contribution': 0,
        'counted': False,
        'detail': '通根中有与日主同字藏干时 +5，否则 0'})
    _within_count_cap.append(True)
    # 封顶截断，与 de_shi 同理：个数封顶后的计入来源原始贡献之和仍可
    # 超过分项封顶（heavy each=20 时计入和 45 分，分项分封顶 35），
    # 逐来源计入、边际来源只计剩余部分，使计入来源之和恒等于分项分；
    # 钉住权重下计入和本就等于分项分，此 pass 不改变任何已钉住算例。
    _remaining = weights['de_di']['cap']
    for _source, _within in zip(de_di_sources, _within_count_cap):
        if _within and _remaining > 0:
            _source['contribution'] = max(
                0, min(_source['raw_contribution'], _remaining))
            _source['counted'] = _source['contribution'] > 0
            _remaining -= _source['contribution']
    de_di = min(heavy_count, weights['de_di']['heavy_root_max_count']) \
        * weights['de_di']['heavy_root_each'] \
        + min(other_count, weights['de_di']['other_root_max_count']) \
        * weights['de_di']['other_root_each'] \
        + (weights['de_di']['same_stem_root_bonus']
           if any(row['same_stem'] for row in roots) else 0)
    de_di = min(de_di, weights['de_di']['cap'])
    de_di_conditions = [
        '重根集：%s（%s日主）'
        % (sorted(heavy) if heavy else '无已审重根集',
           day_master),
        '重根 +%d/个（至多 %d 个），余根 +%d/个（至多 %d 个），同干根 +%d，'
        '封顶 %d' % (weights['de_di']['heavy_root_each'],
                     weights['de_di']['heavy_root_max_count'],
                     weights['de_di']['other_root_each'],
                     weights['de_di']['other_root_max_count'],
                     weights['de_di']['same_stem_root_bonus'],
                     weights['de_di']['cap']),
        '通根 %d 处（重根 %d，余根 %d），计入重根 %d、余根 %d'
        % (len(roots), heavy_count, other_count, heavy_counted,
           other_counted)]
    if day_element == '土':
        limitations.append('土日主无已审重根集：得地分只计余根，未校准。')
        de_di_conditions.append('Q5：土日主得地未校准，只计余根；分数为研究性'
                                '暂定分，不输出确定旺衰分类。')
    if day_master == '丁':
        limitations.append('丁日主火重根集未审（丁长生冲突未裁定）：'
                           '得地分只计余根，未校准。')
        de_di_conditions.append('Q5：丁日主得地未校准，只计余根；分数为研究性'
                                '暂定分，不输出确定旺衰分类。')

    # 得势 / 藏干生扶 / 克泄耗，逐干列出贡献与计入/下限状态。
    visible_support_rows = [
        row for row in visible if row['relation'] in _SUPPORT_RELATIONS]
    visible_support = len(visible_support_rows)
    de_shi = min(visible_support
                 * weights['de_shi']['visible_support_each'],
                 weights['de_shi']['cap'])
    # 封顶截断：旧式 min(...)//each 的 counted 干数在封顶不能整除单干
    # 权重时会丢余数（each=20、cap=30 时只计 1 干 20 分，分项分却是
    # 30），计入来源之和与分项分脱节。改为逐干计入、边际干只计剩余
    # 部分，使计入来源之和恒等于分项分；钉住权重（10/干、封顶 30）
    # 下与旧算法逐干一致，不改变任何已钉住算例。
    de_shi_sources = []
    _remaining = de_shi
    for row in visible_support_rows:
        _unit = weights['de_shi']['visible_support_each']
        _contribution = max(0, min(_unit, _remaining)) \
            if _remaining > 0 else 0
        de_shi_sources.append({
            'kind': 'visible_support', 'pillar': row['pillar'],
            'stem': row['stem'], 'element': row['element'],
            'relation': row['relation'], 'ten_god': row['ten_god'],
            'raw_contribution': _unit,
            'contribution': _contribution,
            'counted': _contribution > 0})
        _remaining -= _contribution
    de_shi_counted = sum(1 for s in de_shi_sources if s['counted'])
    de_shi_conditions = [
        '显干（年/月/时）生扶（同类/生我）+%d/干，封顶 %d'
        % (weights['de_shi']['visible_support_each'],
           weights['de_shi']['cap']),
        '显干生扶 %d 干，计入 %d 干' % (visible_support, de_shi_counted)]
    hidden_support_rows = [
        row for row in hidden if row['relation'] in _SUPPORT_RELATIONS]
    hidden_support = len(hidden_support_rows)
    shengfu_hidden = min(
        hidden_support * weights['shengfu_hidden']['hidden_support_each'],
        weights['shengfu_hidden']['cap'])
    # 封顶截断，与 de_shi 同理（each=3、cap=10 时旧算法计 3 干 9 分，
    # 分项分却是 10）。
    shengfu_sources = []
    _remaining = shengfu_hidden
    for row in hidden_support_rows:
        _unit = weights['shengfu_hidden']['hidden_support_each']
        _contribution = max(0, min(_unit, _remaining)) \
            if _remaining > 0 else 0
        shengfu_sources.append({
            'kind': 'hidden_support', 'pillar': row['pillar'],
            'branch': row['branch'], 'stem': row['stem'],
            'element': row['element'], 'relation': row['relation'],
            'ten_god': row['ten_god'],
            'raw_contribution': _unit,
            'contribution': _contribution,
            'counted': _contribution > 0})
        _remaining -= _contribution
    shengfu_counted = sum(1 for s in shengfu_sources if s['counted'])
    shengfu_conditions = [
        '藏干生扶 +%d/干，封顶 %d'
        % (weights['shengfu_hidden']['hidden_support_each'],
           weights['shengfu_hidden']['cap']),
        '藏干生扶 %d 干，计入 %d 干' % (hidden_support, shengfu_counted)]
    opposing_rows = [
        row for row in visible + hidden
        if row['relation'] in _OPPOSE_RELATIONS]
    opposing = len(opposing_rows)
    kexiehao = max(
        opposing * weights['kexiehao']['opposing_each'],
        weights['kexiehao']['floor'])
    # 下限截断，与 de_shi 同理（each=-3、下限 -20 时旧算法计 6 干
    # -18 分，分项分却是 -20）：逐干计入、边际干只计剩余部分。
    kexiehao_sources = []
    _remaining = abs(kexiehao)
    for row in opposing_rows:
        _unit = weights['kexiehao']['opposing_each']
        _magnitude = min(-_unit, _remaining) \
            if _unit < 0 and _remaining > 0 else 0
        kexiehao_sources.append({
            'kind': 'opposing', 'pillar': row.get('pillar'),
            'branch': row.get('branch'), 'stem': row['stem'],
            'element': row['element'], 'relation': row['relation'],
            'ten_god': row['ten_god'],
            'raw_contribution': _unit,
            'contribution': -_magnitude,
            'counted': _magnitude > 0})
        _remaining -= _magnitude
    kexiehao_counted = sum(1 for s in kexiehao_sources if s['counted'])
    kexiehao_conditions = [
        '克/泄/耗干（显干＋藏干，我生/克我/我克）%d/干，下限 %d'
        % (weights['kexiehao']['opposing_each'],
           weights['kexiehao']['floor']),
        '克泄耗 %d 干，计入 %d 干（触下限时余干不计）'
        % (opposing, kexiehao_counted),
        'Q3-A：冲/害/六合不参与本分项计分，见 interaction_effects']

    total = de_ling + de_di + de_shi + shengfu_hidden + kexiehao
    verdict = _band_for_score(total, thresholds)
    status, uncertainty_flags, status_notes = _classification_status(
        day_master, month_branch)
    notes.extend(status_notes)
    return {
        'model_id': MODERN_MODEL_ID,
        'model_kind': 'modern_engineering',
        'research_only': True, 'public_enabled': False, 'ai_enabled': False,
        'verdict': verdict,
        'score': total,
        'score_band': verdict,
        'classification_status': status,
        'definite_classification': verdict if status == 'definite' else None,
        'uncertainty_flags': uncertainty_flags,
        'thresholds': dict(thresholds),
        'weights': weights,
        'components': {
            'de_ling': {'score': de_ling, 'basis': de_ling_basis,
                        'detail': '月支 %s，本气/司令关系计分'
                                  % month_branch,
                        'sources': de_ling_sources,
                        'conditions': de_ling_conditions},
            'de_di': {'score': de_di,
                      'basis': 'heavy_roots_%d_other_roots_%d_same_stem_%s'
                               % (heavy_count, other_count,
                                  any(row['same_stem'] for row in roots)),
                      'detail': '通根 %d 处（重根 %d，余根 %d）'
                                % (len(roots), heavy_count, other_count),
                      'sources': de_di_sources,
                      'conditions': de_di_conditions},
            'de_shi': {'score': de_shi, 'basis': 'visible_support_%d'
                       % visible_support,
                       'detail': '显干生扶 %d 干' % visible_support,
                       'sources': de_shi_sources,
                       'conditions': de_shi_conditions},
            'shengfu_hidden': {'score': shengfu_hidden,
                               'basis': 'hidden_support_%d' % hidden_support,
                               'detail': '藏干生扶 %d 干' % hidden_support,
                               'sources': shengfu_sources,
                               'conditions': shengfu_conditions},
            'kexiehao': {'score': kexiehao, 'basis': 'opposing_%d' % opposing,
                         'detail': '克泄耗 %d 干（显干＋藏干）' % opposing,
                         'sources': kexiehao_sources,
                         'conditions': kexiehao_conditions},
        },
        'abstain_reason': None,
        'abstain_detail': None,
        'cong_candidates': cong,
        'interaction_effects': interactions,
        'limitations': limitations,
        'notes': notes,
    }


def _divergence_block(classical, modern, summary):
    """Explainable classical-vs-modern divergence (parallel, never unified).

    ``classical_evidence`` is the matched predicate (or the blockers when
    nothing matched); ``modern_evidence`` is the score/components (or the
    abstain reason). ``reasons`` name the concrete cause; when the
    classical layer matched nothing, ``closest_predicates`` lists the
    predicates with the fewest unmet conditions and exactly which
    conditions failed, so the gap is inspectable instead of a bare label.
    """
    classical_verdict = classical['classification']
    modern_verdict = modern['verdict'] if modern is not None else None
    if modern is None:
        modern_evidence = {'verdict': None, 'note': '现代模型未启用。'}
    elif modern['verdict'] == 'abstain':
        modern_evidence = {
            'verdict': 'abstain', 'score': None,
            'abstain_reason': modern['abstain_reason'],
            'abstain_detail': modern['abstain_detail']}
    else:
        modern_evidence = {
            'verdict': modern['verdict'], 'score': modern['score'],
            'score_band': modern.get('score_band'),
            'classification_status': modern.get('classification_status'),
            'definite_classification': modern.get('definite_classification'),
            'components': {k: v['score']
                           for k, v in modern['components'].items()}}
    if classical['matched_predicate'] is not None:
        classical_evidence = {
            'matched_predicate':
                classical['matched_predicate']['predicate_id'],
            'phase1_rule_id':
                classical['matched_predicate']['phase1_rule_id'],
            'sealed_validation':
                classical['matched_predicate']['sealed_validation'],
            'conditions': dict(
                classical['matched_predicate']['conditions'])}
    else:
        classical_evidence = {
            'matched_predicate': None,
            'blockers': list(classical['blockers'])}
    reasons = []
    closest = []
    if modern is None:
        reasons.append('现代模型未启用，无从比较。')
    elif modern['verdict'] == 'abstain':
        reasons.append('现代层弃判（%s）：弃判不是弱判，不构成与古典层的冲突；'
                       '古典层结论 %s 保持独立。'
                       % (modern['abstain_reason'], classical_verdict))
    elif classical_verdict == 'indeterminate':
        for entry in classical['predicates']:
            failed = [k for k, v in entry['conditions'].items() if not v]
            closest.append({
                'predicate_id': entry['predicate_id'],
                'failed_condition_count': len(failed),
                'failed_conditions': failed,
                'sealed_validation': entry['sealed_validation']})
        closest.sort(key=lambda row: row['failed_condition_count'])
        nearest = closest[0] if closest else None
        reasons.append('古典层暂不可判：7 条已审谓词无一命中；最接近的谓词 '
                       '%s 有 %d 个条件未满足（%s）。'
                       % (nearest['predicate_id'],
                          nearest['failed_condition_count'],
                          '、'.join(nearest['failed_conditions'])
                          if nearest else ''))
        reasons.append('现代层 %s（总分 %s）只是工程近似，不替古典层裁决；'
                       '分歧根源见最接近谓词的未满足条件。'
                       % (modern_verdict, modern['score']))
    elif modern.get('classification_status') in (
            'provisional_incomplete', 'uncertain'):
        reasons.append('现代层分数为研究性暂定分（classification_status=%s，'
                       'uncertainty_flags=%s）：definite_classification 为 '
                       'None，不输出确定旺衰分类；与古典层 %s 的对照只作参考。'
                       % (modern['classification_status'],
                          ','.join(modern.get('uncertainty_flags') or []),
                          classical_verdict))
    elif modern_verdict == 'balanced':
        reasons.append('古典层 %s；现代层 balanced（总分 %s，中间带），'
                       '不是古典中和裁决。'
                       % (classical_verdict, modern['score']))
    elif (classical_verdict == 'strong' and modern_verdict == 'strong') \
            or (classical_verdict == 'weak' and modern_verdict == 'weak'):
        reasons.append('两层结论一致（%s），但依据不同：古典谓词 vs 工程评分，'
                       '仍并列报告。' % classical_verdict)
    else:
        reasons.append('两层冲突：古典层 %s（谓词 %s），现代层 %s（总分 %s）；'
                       '不强制统一，待用户裁定。'
                       % (classical_verdict,
                          classical_evidence.get('matched_predicate'),
                          modern_verdict, modern['score']))
    return {
        'classical': classical_verdict,
        'modern': modern_verdict,
        'classical_evidence': classical_evidence,
        'modern_evidence': modern_evidence,
        'closest_predicates': closest,
        'reasons': reasons,
    }


def divergence_explanation(assessment):
    """Standalone explainable-divergence view of an assess_strength result.

    Returns the agreement divergence block plus one-line plain summaries.
    It never re-judges: it only restates the two layers' verdicts, evidence
    and reasons from the assessment dict.
    """
    if not isinstance(assessment, dict) or 'agreement' not in assessment:
        raise ValueError('Expected an assess_strength result dict')
    block = assessment['agreement'].get('divergence') or {}
    lines = [
        '古典层：%s；现代层：%s（%s）。' % (
            block.get('classical'),
            block.get('modern'),
            assessment.get('agreement', {}).get('relationship')),
    ]
    lines.extend(block.get('reasons') or [])
    return {
        'model_kind': 'modern_engineering',
        'research_only': True, 'public_enabled': False, 'ai_enabled': False,
        'classical': block.get('classical'),
        'modern': block.get('modern'),
        'relationship': assessment['agreement'].get('relationship'),
        'classical_evidence': block.get('classical_evidence'),
        'modern_evidence': block.get('modern_evidence'),
        'closest_predicates': block.get('closest_predicates'),
        'reasons': block.get('reasons'),
        'summary_lines': lines,
    }


def assess_strength(pillars, day_master, *, siling_si_pilot=None,
                    include_modern=True, modern_weights=None,
                    modern_thresholds=None):
    """Assess one chart's strength: classical factor-level predicates
    plus the modern engineering model, in parallel, never unified.

    ``pillars``: four ordered chart pillars in the shape
    :func:`bazi_core.chart_from_pillars` produces (``name`` /
    ``stem`` / ``branch`` with ``value``). ``day_master`` must equal
    the day pillar's stem. ``siling_si_pilot``: an already-computed
    ``si_siling_pilot`` result dict for this birth instant, required
    by the modern model for 巳月 charts; the classical layer never
    consumes it. ``modern_weights`` / ``modern_thresholds``: optional
    partial overrides for sensitivity runs (see
    :func:`sensitivity_analysis`); the pinned v1 tables are never mutated.
    Returns a research-only dict (see module docstring).
    """
    _validate_pillars(pillars, day_master)
    factor_output = factors(pillars, day_master)
    if factor_output['factor_variant'] != FACTOR_VARIANT:
        raise RuntimeError('registration_integrity_failure: unexpected '
                           'strength factor variant')
    summary = _summarize_factors(pillars, day_master, factor_output)
    classical = _classical_layer(pillars, summary, day_master)
    modern = _modern_layer(pillars, summary, day_master, classical,
                           siling_si_pilot,
                           weights=modern_weights,
                           thresholds=modern_thresholds) \
        if include_modern else None

    classical_verdict = classical['classification']
    modern_verdict = modern['verdict'] if modern is not None else None
    if modern_verdict is None:
        relationship = 'not_comparable'
        note = '现代模型未启用。'
    elif modern_verdict == 'abstain':
        relationship = 'modern_abstains'
        note = '现代层弃判（%s）；古典层结论 %s 保持独立，不被覆盖。' % (
            modern['abstain_reason'], classical_verdict)
    elif modern.get('classification_status') == 'provisional_incomplete':
        relationship = 'modern_provisional'
        note = '现代层分数为研究性暂定分（%s），不输出确定旺衰分类；' \
            '古典层结论 %s 保持独立，只作对照。' % (
                ','.join(modern.get('uncertainty_flags') or []),
                classical_verdict)
    elif modern.get('classification_status') == 'uncertain':
        relationship = 'modern_uncertain'
        note = '现代层分类不确定（%s：四库月得令记 0 为暂定处理）；' \
            '古典层结论 %s 保持独立，只作对照。' % (
                ','.join(modern.get('uncertainty_flags') or []),
                classical_verdict)
    elif classical_verdict == 'indeterminate':
        relationship = 'classical_indeterminate'
        note = '古典层暂不可判；现代层 %s 只是工程近似，不替古典层裁决。' \
            % modern_verdict
    elif (classical_verdict == 'strong' and modern_verdict == 'strong') \
            or (classical_verdict == 'weak' and modern_verdict == 'weak'):
        relationship = 'agree'
        note = '两层结论一致（%s），但依据不同：古典谓词 vs 工程评分，' \
            '仍并列报告。' % classical_verdict
    elif modern_verdict == 'balanced':
        relationship = 'modern_balanced'
        note = '古典层 %s；现代层 balanced（中间带），不是古典中和裁决。' \
            % classical_verdict
    else:
        relationship = 'conflict'
        note = '两层冲突：古典层 %s，现代层 %s；不强制统一，待用户裁定。' \
            % (classical_verdict, modern_verdict)

    pillars_ganzhi = [p['stem']['value'] + p['branch']['value']
                      for p in pillars]
    evidence_chain = []
    for entry in classical['predicates']:
        evidence_chain.append({
            'decision': 'classical_predicate',
            'predicate_id': entry['predicate_id'],
            'phase1_rule_id': entry['phase1_rule_id'],
            'phase2_step_id': entry['phase2_step_id'],
            'met': entry['met'],
            'sealed_validation': entry['sealed_validation'],
            'sealed_golden_ids': list(entry['sealed_golden_ids']),
            'public_golden_refs': list(entry['public_golden_refs']),
            'conditions': dict(entry['conditions']),
            'factor_refs': {
                'month_branch': summary['month_branch'],
                'principal_qi': summary['principal_qi'],
                'root_positions': list(summary['root_positions']),
                'visible_positions': list(summary['visible_positions']),
                'interactions_present':
                    summary['interactions']['present'],
            },
        })
    if modern is not None:
        evidence_chain.append({
            'decision': 'modern_model',
            'model_id': MODERN_MODEL_ID,
            'model_kind': 'modern_engineering',
            'verdict': modern['verdict'],
            'score': modern['score'],
            'thresholds': dict(modern['thresholds']),
            'components': modern['components'],
            'abstain_reason': modern['abstain_reason'],
        })

    return {
        'variant': ENGINE_VARIANT,
        'day_master': day_master,
        'month_branch': summary['month_branch'],
        'pillars': pillars_ganzhi,
        'factors': summary,
        'classical': classical,
        'modern': modern,
        'agreement': {
            'classical': classical_verdict,
            'modern': modern_verdict,
            'relationship': relationship,
            'note': note,
            'divergence': _divergence_block(classical, modern, summary),
        },
        'evidence_chain': evidence_chain,
        'research_only': True, 'public_enabled': False, 'ai_enabled': False,
        'limitations': list(GLOBAL_LIMITATIONS),
    }


def explain_components(pillars, day_master, *, siling_si_pilot=None,
                       modern_weights=None, modern_thresholds=None):
    """Per-component explanation for one chart's modern score.

    Returns the modern layer's components (value, sources, conditions)
    plus the total, score band and classification status. Raises
    ValueError on missing/invalid input; returns the abstain reason
    instead of components when the modern layer abstains.
    """
    out = assess_strength(pillars, day_master,
                          siling_si_pilot=siling_si_pilot,
                          modern_weights=modern_weights,
                          modern_thresholds=modern_thresholds)
    modern = out['modern']
    return {
        'model_id': MODERN_MODEL_ID,
        'model_kind': 'modern_engineering',
        'research_only': True, 'public_enabled': False, 'ai_enabled': False,
        'day_master': day_master,
        'month_branch': out['month_branch'],
        'pillars': out['pillars'],
        'verdict': modern['verdict'],
        'score': modern['score'],
        'score_band': modern['score_band'],
        'classification_status': modern['classification_status'],
        'definite_classification': modern['definite_classification'],
        'uncertainty_flags': modern['uncertainty_flags'],
        'components': modern['components'],
        'abstain_reason': modern['abstain_reason'],
        'abstain_detail': modern['abstain_detail'],
    }


def audit_component_counts(pillars, day_master, *, siling_si_pilot=None):
    """Recompute every modern component from the factor layer and compare.

    Catches double counting (a stem/root counted in two components or
    twice in one), cap/floor drift, and total-vs-sum mismatch. Each check
    reports passed/failed with the recomputed numbers; the function never
    trusts the scored components themselves.
    """
    _validate_pillars(pillars, day_master)
    factor_output = factors(pillars, day_master)
    summary = _summarize_factors(pillars, day_master, factor_output)
    out = assess_strength(pillars, day_master,
                          siling_si_pilot=siling_si_pilot)
    modern = out['modern']
    checks = []

    def check(name, passed, detail):
        checks.append({'name': name, 'passed': bool(passed),
                       'detail': detail})

    visible = summary['visible_positions']
    hidden = summary['hidden_positions']
    roots = summary['root_positions']
    visible_support = [r for r in visible
                       if r['relation'] in _SUPPORT_RELATIONS]
    hidden_support = [r for r in hidden
                      if r['relation'] in _SUPPORT_RELATIONS]
    opposing = [r for r in visible + hidden
                if r['relation'] in _OPPOSE_RELATIONS]
    # Partition check: every visible/hidden stem is in exactly one class.
    classified = len(visible_support) + len(hidden_support) + len(opposing)
    total_positions = len(visible) + len(hidden)
    check('stem_partition_no_double_count',
          classified == total_positions,
          'visible %d + hidden %d = %d positions; support %d + opposing %d '
          '= %d classified'
          % (len(visible), len(hidden), total_positions,
             len(visible_support) + len(hidden_support), len(opposing),
             classified))
    heavy = _heavy_roots_for(day_master)
    heavy_count = sum(1 for row in roots if row['branch'] in heavy)
    other_count = len(roots) - heavy_count
    check('root_partition_no_double_count',
          heavy_count + other_count == len(roots),
          'roots %d = heavy %d + other %d'
          % (len(roots), heavy_count, other_count))
    if modern['verdict'] == 'abstain':
        check('abstain_has_no_score', modern['score'] is None
              and modern['components'] is None,
              'abstain_reason=%s' % modern['abstain_reason'])
        return {'model_kind': 'modern_engineering', 'research_only': True,
                'public_enabled': False, 'ai_enabled': False,
                'verdict': 'abstain',
                'abstain_reason': modern['abstain_reason'],
                'checks': checks,
                'all_passed': all(c['passed'] for c in checks)}
    components = modern['components']
    expected_de_shi = min(len(visible_support) * 10, 30)
    expected_hidden = min(len(hidden_support) * 2, 10)
    expected_kexiehao = max(len(opposing) * -2, -20)
    check('de_shi_recomputed', components['de_shi']['score'] == expected_de_shi,
          'visible support %d -> %d (scored %d)'
          % (len(visible_support), expected_de_shi,
             components['de_shi']['score']))
    check('shengfu_hidden_recomputed',
          components['shengfu_hidden']['score'] == expected_hidden,
          'hidden support %d -> %d (scored %d)'
          % (len(hidden_support), expected_hidden,
             components['shengfu_hidden']['score']))
    check('kexiehao_recomputed',
          components['kexiehao']['score'] == expected_kexiehao,
          'opposing %d -> %d (scored %d)'
          % (len(opposing), expected_kexiehao,
             components['kexiehao']['score']))
    expected_de_di = min(
        min(heavy_count, 2) * 15 + min(other_count, 2) * 5
        + (5 if any(row['same_stem'] for row in roots) else 0), 35)
    check('de_di_recomputed', components['de_di']['score'] == expected_de_di,
          'heavy %d other %d same_stem %s -> %d (scored %d)'
          % (heavy_count, other_count,
             any(row['same_stem'] for row in roots), expected_de_di,
             components['de_di']['score']))
    total = sum(v['score'] for v in components.values())
    check('total_equals_component_sum', total == modern['score'],
          'components sum %d, total %d' % (total, modern['score']))
    low, high = MODERN_SCORE_RANGE
    check('total_within_bounds', low <= modern['score'] <= high,
          'score %d within [%d, %d]' % (modern['score'], low, high))
    for name, (comp_low, comp_high) in {
            'de_ling': (-15, 30), 'de_di': (0, 35), 'de_shi': (0, 30),
            'shengfu_hidden': (0, 10), 'kexiehao': (-20, 0)}.items():
        value = components[name]['score']
        check('component_range_' + name, comp_low <= value <= comp_high,
              '%s=%d within [%d, %d]' % (name, value, comp_low, comp_high))
    for name in components:
        sources = components[name].get('sources') or []
        counted = sum(s['contribution'] for s in sources if s.get('counted'))
        check('component_sources_sum_' + name,
              counted == components[name]['score'],
              '%s counted sources sum %d, score %d'
              % (name, counted, components[name]['score']))
    return {'model_kind': 'modern_engineering', 'research_only': True,
            'public_enabled': False, 'ai_enabled': False,
            'verdict': modern['verdict'], 'score': modern['score'],
            'checks': checks,
            'all_passed': all(c['passed'] for c in checks)}


def validate_assessment(assessment):
    """Validate invariants of an assess_strength result (universal checks).

    Covers: total bounds, component ranges, total == component sum,
    score-band consistency with the thresholds in force, no definite
    classification when the status is provisional/uncertain/abstain,
    component sources summing to their scores, and governance flags.
    Returns {'valid': bool, 'checks': [...]}; never raises on a
    well-formed result dict.
    """
    checks = []

    def check(name, passed, detail):
        checks.append({'name': name, 'passed': bool(passed),
                       'detail': detail})

    modern = assessment.get('modern')
    check('governance_flags',
          assessment.get('research_only') is True
          and assessment.get('public_enabled') is False
          and assessment.get('ai_enabled') is False,
          'research_only/public_enabled/ai_enabled flags')
    if modern is None:
        check('modern_disabled', True, 'include_modern=False')
        return {'valid': all(c['passed'] for c in checks), 'checks': checks}
    check('modern_model_kind',
          modern.get('model_kind') == 'modern_engineering'
          and modern.get('research_only') is True,
          'model_kind=%s' % modern.get('model_kind'))
    if modern['verdict'] == 'abstain':
        check('abstain_has_no_score_and_no_definite_class',
              modern['score'] is None
              and modern.get('definite_classification') is None
              and modern['components'] is None,
              'abstain_reason=%s' % modern.get('abstain_reason'))
        check('abstain_carries_cong_and_interactions',
              isinstance(modern.get('cong_candidates'), dict)
              and isinstance(modern.get('interaction_effects'), dict),
              'cong_candidates + interaction_effects present on abstain')
        # 弃判结果同样携带从格候选：候选恒不成立的校验不因弃判而跳过。
        check('cong_candidates_never_establish',
              all(c.get('establishment') == 'not_judged'
                  and c.get('verdict') is None
                  for c in modern.get('cong_candidates', {}).get(
                      'candidates', [])),
              'all cong candidates establishment=not_judged, verdict=None')
        return {'valid': all(c['passed'] for c in checks), 'checks': checks}
    components = modern['components']
    total = sum(v['score'] for v in components.values())
    check('total_equals_component_sum', total == modern['score'],
          'components sum %d, total %d' % (total, modern['score']))
    low, high = MODERN_SCORE_RANGE
    check('total_within_bounds', low <= modern['score'] <= high,
          'score %d within [%d, %d]' % (modern['score'], low, high))
    for name, (comp_low, comp_high) in {
            'de_ling': (-15, 30), 'de_di': (0, 35), 'de_shi': (0, 30),
            'shengfu_hidden': (0, 10), 'kexiehao': (-20, 0)}.items():
        value = components[name]['score']
        check('component_range_' + name, comp_low <= value <= comp_high,
              '%s=%d within [%d, %d]' % (name, value, comp_low, comp_high))
        sources = components[name].get('sources') or []
        counted = sum(s['contribution'] for s in sources if s.get('counted'))
        check('component_sources_sum_' + name, counted == value,
              '%s counted sources sum %d, score %d' % (name, counted, value))
        check('component_has_conditions',
              bool(components[name].get('conditions')),
              '%s conditions listed' % name)
    expected_band = _band_for_score(modern['score'], modern['thresholds'])
    check('score_band_matches_thresholds',
          modern.get('score_band') == expected_band
          and modern['verdict'] == expected_band,
          'score %d -> band %s (thresholds %s)'
          % (modern['score'], expected_band, modern['thresholds']))
    status = modern.get('classification_status')
    if status == 'definite':
        check('definite_classification_present',
              modern.get('definite_classification') == modern['verdict'],
              'status definite, definite_classification=%s'
              % modern.get('definite_classification'))
    else:
        check('no_definite_classification_when_not_definite',
              modern.get('definite_classification') is None,
              'status %s, definite_classification None' % status)
    check('cong_candidates_never_establish',
          all(c.get('establishment') == 'not_judged'
              and c.get('verdict') is None
              for c in modern.get('cong_candidates', {}).get('candidates', [])),
          'all cong candidates establishment=not_judged, verdict=None')
    check('interaction_adjustments_zero',
          modern.get('interaction_effects', {}).get('score_adjustment_total')
          == 0,
          'Q3-A: interaction score_adjustment_total is 0')
    return {'valid': all(c['passed'] for c in checks), 'checks': checks}


# Sensitivity-analysis perturbation catalogue (paths into the weight /
# threshold tables). Threshold perturbations move one threshold at a time;
# weight perturbations move one weight at a time by +/- step.
_SENSITIVITY_WEIGHT_PATHS = (
    ('de_ling', 'same_element'),
    ('de_ling', 'generates_me'),
    ('de_ling', 'i_generate'),
    ('de_ling', 'i_control'),
    ('de_ling', 'controls_me'),
    ('de_di', 'heavy_root_each'),
    ('de_di', 'other_root_each'),
    ('de_shi', 'visible_support_each'),
    ('shengfu_hidden', 'hidden_support_each'),
    ('kexiehao', 'opposing_each'),
)


def sensitivity_analysis(pillars, day_master, *, siling_si_pilot=None,
                         threshold_steps=(5, 10), weight_steps=(5,)):
    """Threshold/weight sensitivity of one chart's modern classification.

    Recomputes the chart under one-at-a-time perturbations (threshold
    shifts and single-weight shifts) using the real scoring path — not a
    hand calculation — and reports which perturbations flip the score
    band, the nearest threshold distance, and whether the base verdict
    is stable across the whole perturbation set. Base abstentions (or a
    disabled modern layer) report no perturbations: there is no band to
    flip.
    """
    base = assess_strength(pillars, day_master,
                           siling_si_pilot=siling_si_pilot)
    modern = base['modern']
    result = {
        'model_id': MODERN_MODEL_ID,
        'model_kind': 'modern_engineering',
        'research_only': True, 'public_enabled': False, 'ai_enabled': False,
        'day_master': day_master,
        'month_branch': base['month_branch'],
        'pillars': base['pillars'],
        'base_score': modern['score'] if modern else None,
        'base_band': modern['score_band'] if modern else None,
        'base_classification_status':
            modern['classification_status'] if modern else None,
        'perturbations': [],
        'flips': [],
        'verdict_stable': None,
        'nearest_boundary_distance': None,
        'note': None,
    }
    if modern is None:
        result['note'] = '现代模型未启用，无敏感性可分析。'
        return result
    if modern['verdict'] == 'abstain':
        result['note'] = ('现代层弃判（%s），无分数带可扰动；敏感性分析不适用。'
                          % modern['abstain_reason'])
        return result
    base_band = modern['score_band']
    score = modern['score']
    thresholds = modern['thresholds']
    result['nearest_boundary_distance'] = min(
        abs(score - thresholds['strong_at_least']),
        abs(score - thresholds['weak_at_most']))

    def run_perturbation(parameter, delta, weights_override=None,
                         thresholds_override=None):
        perturbed = assess_strength(
            pillars, day_master, siling_si_pilot=siling_si_pilot,
            modern_weights=weights_override,
            modern_thresholds=thresholds_override)
        entry = {
            'parameter': parameter,
            'delta': delta,
            'score': perturbed['modern']['score'],
            'band': perturbed['modern']['score_band'],
            'band_changed': perturbed['modern']['score_band'] != base_band,
        }
        result['perturbations'].append(entry)
        if entry['band_changed']:
            result['flips'].append(entry)

    for step in threshold_steps:
        for key, direction in (('strong_at_least', 1),
                               ('strong_at_least', -1),
                               ('weak_at_most', 1),
                               ('weak_at_most', -1)):
            new_value = thresholds[key] + direction * step
            if key == 'strong_at_least' and new_value <= thresholds['weak_at_most']:
                continue
            if key == 'weak_at_most' and new_value >= thresholds['strong_at_least']:
                continue
            run_perturbation('threshold.%s' % key, direction * step,
                             thresholds_override={key: new_value})
    for step in weight_steps:
        for section, key in _SENSITIVITY_WEIGHT_PATHS:
            for direction in (1, -1):
                current = MODERN_WEIGHTS[section][key]
                run_perturbation('weight.%s.%s' % (section, key),
                                 direction * step,
                                 weights_override={
                                     section: {key: current + direction * step}})
    result['verdict_stable'] = not result['flips']
    result['perturbation_count'] = len(result['perturbations'])
    result['flip_count'] = len(result['flips'])
    return result


def default_coverage_template(day_master, month_branch):
    """Uniform probe pillars for one (day_master, month_branch) cell.

    All four pillars carry the day-master stem on the target month
    branch. The template is deliberately interaction-free (one stem, one
    branch: no stem five-combination, no triple harmony, no six
    harmony/harm/clash pair), so the matrix probes de_ling / de_di /
    de_shi / hidden-support / kexiehao for every cell rather than the
    template's own interactions. It is a coverage probe, not a real chart:
    cells report their template pillars explicitly.
    """
    ganzhi = day_master + month_branch
    return [{'name': name, 'stem': {'value': day_master},
             'branch': {'value': month_branch}}
            for name in PILLAR_NAMES]


def coverage_matrix(*, siling_si_pilot=None, pillar_template=None):
    """Ten day-masters x twelve month branches: full modern-model coverage.

    Every one of the 120 combinations gets an explicit cell — computed,
    abstain (with reason), or error — so no combination is silently
    missing. ``siling_si_pilot`` (one verified computed Si pilot) is
    applied uniformly to the ten 巳月 cells when supplied; without it
    those ten cells abstain with ``siling_si_pilot_not_verified``.
    ``pillar_template`` may supply a caller template
    ``(day_master, month_branch) -> pillars``; the default is
    :func:`default_coverage_template`.
    """
    template = pillar_template or default_coverage_template
    cells = []
    by_abstain_reason = {}
    for day_master in STEMS:
        for month_branch in BRANCHES:
            pillars = template(day_master, month_branch)
            ganzhi = [p['stem']['value'] + p['branch']['value']
                      for p in pillars]
            try:
                out = assess_strength(pillars, day_master,
                                      siling_si_pilot=siling_si_pilot)
            except Exception as exc:  # recorded per-cell, never swallowed
                cells.append({
                    'day_master': day_master, 'month_branch': month_branch,
                    'status': 'error', 'pillars': ganzhi,
                    'score': None, 'score_band': None,
                    'definite_classification': None,
                    'classification_status': 'error',
                    'components': None, 'abstain_reason': None,
                    'error': '%s: %s' % (type(exc).__name__, exc),
                    'uncertainty_flags': [],
                })
                continue
            modern = out['modern']
            if modern['verdict'] == 'abstain':
                by_abstain_reason[modern['abstain_reason']] = \
                    by_abstain_reason.get(modern['abstain_reason'], 0) + 1
                cells.append({
                    'day_master': day_master, 'month_branch': month_branch,
                    'status': 'abstain', 'pillars': ganzhi,
                    'score': None, 'score_band': None,
                    'definite_classification': None,
                    'classification_status': 'abstain',
                    'components': None,
                    'abstain_reason': modern['abstain_reason'],
                    'abstain_detail': modern['abstain_detail'],
                    'uncertainty_flags': [],
                })
            else:
                cells.append({
                    'day_master': day_master, 'month_branch': month_branch,
                    'status': 'computed', 'pillars': ganzhi,
                    'score': modern['score'],
                    'score_band': modern['score_band'],
                    'definite_classification':
                        modern['definite_classification'],
                    'classification_status': modern['classification_status'],
                    'components': {k: v['score']
                                   for k, v in
                                   modern['components'].items()},
                    'abstain_reason': None,
                    'uncertainty_flags': modern['uncertainty_flags'],
                })
    computed = [c for c in cells if c['status'] == 'computed']
    scores = [c['score'] for c in computed]
    seen = {(c['day_master'], c['month_branch']) for c in cells}
    uncovered = [(dm, mb) for dm in STEMS for mb in BRANCHES
                 if (dm, mb) not in seen]
    return {
        'model_id': MODERN_MODEL_ID,
        'model_kind': 'modern_engineering',
        'research_only': True, 'public_enabled': False, 'ai_enabled': False,
        'template': 'uniform_day_master_month_branch_probe',
        'cells': cells,
        'total_cells': len(cells),
        'computed': len(computed),
        'abstained': sum(1 for c in cells if c['status'] == 'abstain'),
        'errors': sum(1 for c in cells if c['status'] == 'error'),
        'by_abstain_reason': by_abstain_reason,
        'uncovered': uncovered,
        'score_range': [min(scores), max(scores)] if scores else None,
        'note': ('每格均为探针柱（四柱同干同支），只用于覆盖现代模型对全部 '
                 '10×12 组合的计算能力，不是真实命盘；巳月格须配已验证试点，'
                 '否则弃判；土/丁格只出研究性暂定分。'),
    }
