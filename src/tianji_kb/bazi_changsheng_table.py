"""十二长生全表：纯冲突登记（TJ-0426 Lane 1，S-03）。

研究级登记草稿（research_only / public_enabled=False /
ai_enabled=False）。本文件**只登记、不计算**：它不提供任何长生位
查询函数，强度引擎（``bazi_strength_engine``）不得导入本模块，
任何计算接入仍只认已批单格——丙×寅（F4），其接入走
``bazi_fire_si_yin_morphology.FORM_BING_YIN``，不走本表。

登记口径（审计 §6-C 建议 A：纯冲突登记，仿司令矩阵形制）：
各流派长生表并列登记，不取平均、不拼接、不自动择优、不产生旺
衰结论。每一格的状态只有三种：

* ``settled``——该干长生位有逐干明句且无冲突（丙/庚/壬）；
* ``conflict``——阴阳分判与五行统摄两体例并列未裁定（丁/戊/己/
  辛/癸），两分支必须指名引用，不得取任一分支单独建模；
* ``unregistered``——本仓库已登记材料中无该干长生位逐干明句或
  冲突登记（甲/乙），不得据通说补位。

来源：全部引文与冲突登记均复述本仓库已有登记模块，不新立来源。
``settled`` 格的锚点引自火/金水根表登记；``conflict`` 格的分支与
冲突 id 引自各干冲突登记（丁 DING_BLOCK、土 TU_CHANGSHENG_
CONFLICT、辛 XIN_CHANGSHENG_CONFLICT、癸 GUI_CHANGSHENG_
CONFLICT）。甲/乙两格在本仓库火/金水/土根表与司令矩阵中均无长
生位登记，故记缺口。
"""

CHANGSHENG_TABLE_ID = 'bazi-changsheng-conflict-table-v1'
CHANGSHENG_TABLE_RESEARCH_ONLY = True
CHANGSHENG_TABLE_PUBLIC_ENABLED = False
CHANGSHENG_TABLE_AI_ENABLED = False
# 计算接入：无。本表不提供查询函数，引擎不得消费未批的长生表。
CHANGSHENG_TABLE_COMPUTATION = None
CHANGSHENG_TABLE_ENGINE_CONSUMPTION = 'none'

CHANGSHENG_TABLE = {
    '甲': {
        'stem': '甲', 'element': '木', 'status': 'unregistered',
        'changsheng_branch': None, 'branches': None,
        'anchors': [], 'register_ref': None, 'conflict_id': None,
        'gap': '本仓库已登记材料中无甲长生位逐干明句或冲突登记；'
               '「如甲乙逢亥寅卯之类是也」是重根列举，不是长生位'
               '明句。不得据通说补位；取证后逐格补登记。',
    },
    '乙': {
        'stem': '乙', 'element': '木', 'status': 'unregistered',
        'changsheng_branch': None, 'branches': None,
        'anchors': [], 'register_ref': None, 'conflict_id': None,
        'gap': '本仓库已登记材料中无乙长生位逐干明句或冲突登记；'
               '不得据通说补位；取证后逐格补登记。',
    },
    '丙': {
        'stem': '丙', 'element': '火', 'status': 'settled',
        'changsheng_branch': '寅', 'branches': None,
        'anchors': ['sm2.bing_sheng', 'sm2.bing_shengsi',
                    'sm2.summary_bracket', 'sf.sisheng',
                    'sm2.renyuan_bing'],
        'register_ref': 'bazi_fire_si_yin_morphology.FORM_BING_YIN',
        'conflict_id': None,
        'gap': None,
        'note': '唯一已接入计算的单格（F4 丙×寅）：接入走 '
                'FORM_BING_YIN，不走本表。',
    },
    '丁': {
        'stem': '丁', 'element': '火', 'status': 'conflict',
        'changsheng_branch': None,
        'branches': [
            {'branch': '酉', 'system': '阴阳分判',
             'evidence': '三命逐干铺陈两见＋神峰楠曰个例'},
            {'branch': '寅', 'system': '五行统摄',
             'evidence': '神峰五行级四生，丙丁共用'},
        ],
        'anchors': [],
        'register_ref': 'bazi_fire_morphology.DING_BLOCK',
        'conflict_id': 'sanming-juan2.ding-changsheng',
        'gap': None,
        'note': '丁形态一律 blocked_by_conflict；本 conflict 处置'
                '（用户裁定级流派取舍或长期并列分支登记）之前，'
                '不得以任一分支单独建模。',
    },
    '戊': {
        'stem': '戊', 'element': '土', 'status': 'conflict',
        'changsheng_branch': None,
        'branches': [
            {'branch': '寅', 'system': '阴阳分判',
             'evidence': '逐干明句 sm.wu_shengsi；理据句「丙生于寅'
                         '寅属艮艮爲山山爲刚土卽戊土也頼丙火而生焉」'},
            {'branch': '申', 'system': '五行统摄',
             'evidence': '神峰五行级四生「水土长生居申」'},
        ],
        'anchors': ['sm.wu_shengsi'],
        'register_ref': 'bazi_earth_roots.TU_CHANGSHENG_CONFLICT',
        'conflict_id': 'sanming-juan2.tu-changsheng',
        'gap': None,
    },
    '己': {
        'stem': '己', 'element': '土', 'status': 'conflict',
        'changsheng_branch': None,
        'branches': [
            {'branch': '酉', 'system': '阴阳分判',
             'evidence': '逐干明句 sm.ji_shengsi「故己土生于酉而'
                         '死于寅」；理据句「至于酉地丁火而生丁火既'
                         '生己土亦能生也」'},
            {'branch': '申', 'system': '五行统摄',
             'evidence': '神峰五行级四生「水土长生居申」，与戊共用宫序'},
        ],
        'anchors': ['sm.ji_shengsi'],
        'register_ref': 'bazi_earth_roots.TU_CHANGSHENG_CONFLICT',
        'conflict_id': 'sanming-juan2.tu-changsheng',
        'gap': None,
    },
    '庚': {
        'stem': '庚', 'element': '金', 'status': 'settled',
        'changsheng_branch': '巳', 'branches': None,
        'anchors': ['sm.geng_shengsi'],
        'register_ref': 'bazi_metal_water_roots（庚根位登记）',
        'conflict_id': None,
        'gap': None,
        'note': '庚无长生冲突；帝旺酉为推步级（framework_derived），'
                '与长生明句级永不混同。',
    },
    '辛': {
        'stem': '辛', 'element': '金', 'status': 'conflict',
        'changsheng_branch': None,
        'branches': [
            {'branch': '子', 'system': '阴阳分判',
             'evidence': '逐干明句 sm.xin_sheng「长生于子子乃坎水」；'
                         '生死合句 sm.xin_shengsi「故辛金生于子而死于巳」'},
            {'branch': '巳', 'system': '五行统摄',
             'evidence': '神峰五行级四生「金生在巳」，庚辛共用'},
        ],
        'anchors': ['sm.xin_sheng', 'sm.xin_shengsi'],
        'register_ref': 'bazi_metal_water_roots.XIN_CHANGSHENG_CONFLICT',
        'conflict_id': 'sanming-juan2.xin-changsheng',
        'gap': None,
    },
    '壬': {
        'stem': '壬', 'element': '水', 'status': 'settled',
        'changsheng_branch': '申', 'branches': None,
        'anchors': ['sm.ren_shengsi'],
        'register_ref': 'bazi_metal_water_roots（壬根位登记）',
        'conflict_id': None,
        'gap': None,
        'note': '壬无长生冲突；神峰四生「水土长生居申」五行级与干级'
                '于阳干壬一致。',
    },
    '癸': {
        'stem': '癸', 'element': '水', 'status': 'conflict',
        'changsheng_branch': None,
        'branches': [
            {'branch': '卯', 'system': '阴阳分判',
             'evidence': '逐干明句 sm.gui_shengsi「故癸水生于邜而'
                         '死于申」（邜为快照异体，即卯）'},
            {'branch': '申', 'system': '五行统摄',
             'evidence': '神峰五行级四生「水土长生居申」，壬癸共用'},
        ],
        'anchors': ['sm.gui_shengsi'],
        'register_ref': 'bazi_metal_water_roots.GUI_CHANGSHENG_CONFLICT',
        'conflict_id': 'sanming-juan2.gui-changsheng',
        'gap': None,
    },
}

# 缺口汇总：settled 3 格（丙/庚/壬）、conflict 5 格（丁/戊/己/辛/
# 癸）、unregistered 2 格（甲/乙）。立项口径（是否以纯冲突登记立
# 项、是否启动计算接入）待用户裁定（审计 §6-C）；裁定前本表不产
# 生任何旺衰结论、不被任何引擎消费。
CHANGSHENG_TABLE_GAPS = {
    'settled': ['丙', '庚', '壬'],
    'conflict': ['丁', '戊', '己', '辛', '癸'],
    'unregistered': ['甲', '乙'],
    'pending_user_decision': 'bazi-changsheng-table-registration '
                             '(audit GAP_LIST §6-C)',
}


def validate_changsheng_table():
    """Validate the registration draft's own invariants.

    Every stem is present; settled cells carry a branch plus anchors;
    conflict cells carry exactly two branches plus a conflict id;
    unregistered cells carry a gap note and no branch; the table
    declares no computation. Returns {'valid': bool, 'checks': {...}}.
    """
    from .foundations import STEMS

    checks = {}
    table = CHANGSHENG_TABLE
    checks['stems_covered'] = len(table)
    checks['all_ten_stems_present'] = set(table) == set(STEMS)
    checks['settled_have_branch_and_anchors'] = all(
        cell['changsheng_branch'] is not None
        and cell['anchors'] and cell['register_ref']
        for cell in table.values() if cell['status'] == 'settled')
    checks['conflicts_have_two_branches_and_id'] = all(
        cell['branches'] is not None and len(cell['branches']) == 2
        and cell['conflict_id'] and cell['register_ref']
        for cell in table.values() if cell['status'] == 'conflict')
    checks['unregistered_have_gap_and_no_branch'] = all(
        cell['gap'] and cell['changsheng_branch'] is None
        and cell['branches'] is None
        for cell in table.values() if cell['status'] == 'unregistered')
    checks['no_computation_declared'] = \
        CHANGSHENG_TABLE_COMPUTATION is None
    checks['research_only'] = CHANGSHENG_TABLE_RESEARCH_ONLY is True \
        and CHANGSHENG_TABLE_PUBLIC_ENABLED is False \
        and CHANGSHENG_TABLE_AI_ENABLED is False
    return {'valid': all(checks.values()), 'checks': checks}
