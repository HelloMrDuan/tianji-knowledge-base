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
从格候选屏（无根、无显扶、显干全为克/泄方向，且无已审谓词已命中）。
古典层不受现代层弃判影响，两层并列、冲突显式呈现于 ``agreement``。
"""

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
    '三刑事实不进入本层（bazi_sanxing_facts 事实层不解锁任何 '
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
)

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


def _modern_layer(pillars, summary, day_master, classical, siling_si_pilot):
    """Deterministic engineering score (strength_model_modern_v1)."""
    month_branch = summary['month_branch']
    day_element = stem_element(day_master)
    visible = summary['visible_positions']
    hidden = summary['hidden_positions']
    roots = summary['root_positions']
    relations = summary['interactions']
    limitations = list(MODERN_LIMITATIONS)
    notes = []

    def abstain(reason, detail):
        return {
            'model_id': MODERN_MODEL_ID,
            'model_kind': 'modern_engineering',
            'research_only': True, 'public_enabled': False,
            'ai_enabled': False,
            'verdict': 'abstain',
            'score': None,
            'thresholds': dict(MODERN_THRESHOLDS),
            'weights': MODERN_WEIGHTS,
            'components': None,
            'abstain_reason': reason,
            'abstain_detail': detail,
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
    # 盘不是从格候选，见 isolated_control：月令官星显而有根）。
    classical_matched = classical['matched_predicate'] is not None
    if not classical_matched:
        visible_relations = [row['relation'] for row in visible]
        if not roots and not any(
                rel in _SUPPORT_RELATIONS for rel in visible_relations) \
                and len(visible_relations) >= 2 and all(
                    rel in ('controls_me', 'i_generate')
                    for rel in visible_relations):
            return abstain(
                'cong_candidate_unresolved',
                '无根、无显干生扶、显干全为克/泄方向：从格候选，无依据，'
                '现代模型不作弱判。')

    weights = MODERN_WEIGHTS
    # 得令：巳月以试点司令干为准；四库月本气未审，恒 0；其余以本气关系计。
    if month_branch == '巳':
        de_ling_relation = _relation_of(
            day_element, stem_element(commander))
        de_ling = weights['de_ling'][de_ling_relation]
        de_ling_basis = 'siling_si_pilot_commander_%s_%s' % (
            commander, de_ling_relation)
    elif month_branch in _TOMB_BRANCHES:
        de_ling = weights['de_ling']['tomb_principal_unreviewed']
        de_ling_basis = 'tomb_principal_unreviewed'
        limitations.append(
            '本盘月支 %s 为四库，本气未审：得令分记 0，不以外推计分。'
            % month_branch)
    else:
        de_ling_relation = summary['principal_relation']
        de_ling = weights['de_ling'][de_ling_relation]
        de_ling_basis = 'principal_qi_%s_%s' % (
            summary['principal_qi'], de_ling_relation)

    # 得地：重根 / 余根 / 同干根。
    heavy = _heavy_roots_for(day_master)
    heavy_count = sum(1 for row in roots if row['branch'] in heavy)
    other_count = len(roots) - heavy_count
    de_di = min(heavy_count, weights['de_di']['heavy_root_max_count']) \
        * weights['de_di']['heavy_root_each'] \
        + min(other_count, weights['de_di']['other_root_max_count']) \
        * weights['de_di']['other_root_each'] \
        + (weights['de_di']['same_stem_root_bonus']
           if any(row['same_stem'] for row in roots) else 0)
    de_di = min(de_di, weights['de_di']['cap'])
    if day_element == '土':
        limitations.append('土日主无已审重根集：得地分只计余根，未校准。')
    if day_master == '丁':
        limitations.append('丁日主火重根集未审（丁长生冲突未裁定）：'
                           '得地分只计余根，未校准。')

    # 得势 / 藏干生扶 / 克泄耗。
    visible_support = sum(
        1 for row in visible if row['relation'] in _SUPPORT_RELATIONS)
    de_shi = min(visible_support
                 * weights['de_shi']['visible_support_each'],
                 weights['de_shi']['cap'])
    hidden_support = sum(
        1 for row in hidden if row['relation'] in _SUPPORT_RELATIONS)
    shengfu_hidden = min(
        hidden_support * weights['shengfu_hidden']['hidden_support_each'],
        weights['shengfu_hidden']['cap'])
    opposing = sum(
        1 for row in visible + hidden
        if row['relation'] in _OPPOSE_RELATIONS)
    kexiehao = max(
        opposing * weights['kexiehao']['opposing_each'],
        weights['kexiehao']['floor'])

    total = de_ling + de_di + de_shi + shengfu_hidden + kexiehao
    if total >= MODERN_THRESHOLDS['strong_at_least']:
        verdict = 'strong'
    elif total <= MODERN_THRESHOLDS['weak_at_most']:
        verdict = 'weak'
    else:
        verdict = 'balanced'
    return {
        'model_id': MODERN_MODEL_ID,
        'model_kind': 'modern_engineering',
        'research_only': True, 'public_enabled': False, 'ai_enabled': False,
        'verdict': verdict,
        'score': total,
        'thresholds': dict(MODERN_THRESHOLDS),
        'weights': MODERN_WEIGHTS,
        'components': {
            'de_ling': {'score': de_ling, 'basis': de_ling_basis,
                        'detail': '月支 %s，本气/司令关系计分'
                                  % month_branch},
            'de_di': {'score': de_di,
                      'basis': 'heavy_roots_%d_other_roots_%d_same_stem_%s'
                               % (heavy_count, other_count,
                                  any(row['same_stem'] for row in roots)),
                      'detail': '通根 %d 处（重根 %d，余根 %d）'
                                % (len(roots), heavy_count, other_count)},
            'de_shi': {'score': de_shi, 'basis': 'visible_support_%d'
                       % visible_support,
                       'detail': '显干生扶 %d 干' % visible_support},
            'shengfu_hidden': {'score': shengfu_hidden,
                               'basis': 'hidden_support_%d' % hidden_support,
                               'detail': '藏干生扶 %d 干' % hidden_support},
            'kexiehao': {'score': kexiehao, 'basis': 'opposing_%d' % opposing,
                         'detail': '克泄耗 %d 干（显干＋藏干）' % opposing},
        },
        'abstain_reason': None,
        'abstain_detail': None,
        'limitations': limitations,
        'notes': notes,
    }


def assess_strength(pillars, day_master, *, siling_si_pilot=None,
                    include_modern=True):
    """Assess one chart's strength: classical factor-level predicates
    plus the modern engineering model, in parallel, never unified.

    ``pillars``: four ordered chart pillars in the shape
    :func:`bazi_core.chart_from_pillars` produces (``name`` /
    ``stem`` / ``branch`` with ``value``). ``day_master`` must equal
    the day pillar's stem. ``siling_si_pilot``: an already-computed
    ``si_siling_pilot`` result dict for this birth instant, required
    by the modern model for 巳月 charts; the classical layer never
    consumes it. Returns a research-only dict (see module docstring).
    """
    _validate_pillars(pillars, day_master)
    factor_output = factors(pillars, day_master)
    if factor_output['factor_variant'] != FACTOR_VARIANT:
        raise RuntimeError('registration_integrity_failure: unexpected '
                           'strength factor variant')
    summary = _summarize_factors(pillars, day_master, factor_output)
    classical = _classical_layer(pillars, summary, day_master)
    modern = _modern_layer(pillars, summary, day_master, classical,
                           siling_si_pilot) if include_modern else None

    classical_verdict = classical['classification']
    modern_verdict = modern['verdict'] if modern is not None else None
    if modern_verdict is None:
        relationship = 'not_comparable'
        note = '现代模型未启用。'
    elif modern_verdict == 'abstain':
        relationship = 'modern_abstains'
        note = '现代层弃判（%s）；古典层结论 %s 保持独立，不被覆盖。' % (
            modern['abstain_reason'], classical_verdict)
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
            'thresholds': dict(MODERN_THRESHOLDS),
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
        },
        'evidence_chain': evidence_chain,
        'research_only': True, 'public_enabled': False, 'ai_enabled': False,
        'limitations': list(GLOBAL_LIMITATIONS),
    }
