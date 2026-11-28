"""Small source-backed placements; full Ziwei charts are not implemented."""
import json
from pathlib import Path
from .liuyao import STEMS, BRANCHES


def base():
    return json.loads((Path(__file__).resolve().parents[3] / 'data/canonical/ziwei/iztro_rules_v1.json').read_text())


def lucun(year_stem):
    if year_stem not in list(STEMS):
        raise ValueError('Unknown year stem')
    return base()['star_placement_rules']['lucun']['by_year_stem'][year_stem]


def tianma(year_branch):
    if year_branch not in list(BRANCHES):
        raise ValueError('Unknown year branch')
    return next(value for group,value in base()['star_placement_rules']['tianma']['by_year_branch_group'].items() if year_branch in group)


def four_transformations(year_stem, variant):
    """Legacy implementation lookup only; never resolves textual differences."""
    if variant!='iztro-default-v2':
        raise ValueError('Unsupported or unreviewed four-transformation variant')
    if year_stem not in list(STEMS):
        raise ValueError('Unknown year stem')
    return dict(zip(['化禄','化权','化科','化忌'],base()['four_transformations'][year_stem]))


# ---------------------------------------------------------------------------
# O-01 (TJ-0426 Lane 5): dispute registry — registration only, no ruling.
# The iztro-default-v2 table above is unchanged; nothing here overrides
# it, and no entry below is ever used as a classical verdict. Evidence
# levels ride with every entry (C/D, never washed to a settled rule).
# ---------------------------------------------------------------------------

# 壬年四化分歧：iztro 软件表（化科=左辅，见 test_phase1_ziwei）与隔离
# 候选原文（含「壬梁紫府武」）并存，未刊本核定。只登记，不裁决；
# 不得把 iztro 软件表冒充古籍核定，也不得把候选口诀解码成四化映射。
FOUR_TRANSFORMATIONS_REN_DISPUTE = {
    'stem': '壬',
    'status': 'unresolved',
    'evidence_level': 'D',
    'iztro_default_v2': {'化科': '左辅'},
    'iztro_default_note': '仅化科一格取自已审测试断言；全行仍以 iztro-default-v2 表为准，表值未改。',
    'isolated_candidate': {
        'stage': 'quarantine',
        'original_text_contains': '壬梁紫府武',
        'note': '隔离候选原文片段，未解码为四化映射，未核定。',
    },
    'determination': None,
}

# 魁钺歌分歧：古籍读法「丙丁猪狗」与现代实现「猪鸡」不一致。
# 现状是只保留部分结构化规则——排盘不计算天魁/天钺落宫（辅助星
# 表中无魁钺），故无任何错误落宫可以点火。分歧未裁决前不补算。
KUIYUE_DISPUTE = {
    'stars': ('天魁', '天钺'),
    'status': 'unresolved',
    'evidence_level': 'D',
    'classical_reading': '丙丁猪狗',
    'modern_implementation_reading': '丙丁猪鸡',
    'structured_rules_retained': 'partial',
    'note': '天魁/天钺落宫未编码；分歧只登记不裁决。',
    'determination': None,
}

# 长生男顺女逆与现代阴阳男女配置并存，未形成唯一完整排盘算法。
# 大限行运方向（见 operations/ziwei_periods.py）须调用方显式给定
# 性别与年干阴阳，不得静默代选。
ZIWEI_GAPS = {
    'decade_annual': {'status': 'candidate_pending_collation', 'evidence_level': 'D',
        'note': '大限/流年算术为候选计算，须先刊本核定；未核定前 determination 恒 None。'},
    'changsheng_direction': {'status': 'gap', 'evidence_level': 'D',
        'note': '长生男顺女逆与现代阴阳男女配置并存，未形成唯一完整排盘算法。'},
    'temple_prosperity': {'status': 'gap', 'evidence_level': 'D',
        'note': '庙旺未建；无庙旺/吉凶断语。'},
}


def transformation_disputes():
    """Return the registered four-transformation disputes (copies)."""
    return {'壬': dict(FOUR_TRANSFORMATIONS_REN_DISPUTE,
                       isolated_candidate=dict(FOUR_TRANSFORMATIONS_REN_DISPUTE['isolated_candidate']))}


def kuiyue_dispute():
    """Return the registered 魁钺歌 dispute (copy)."""
    return dict(KUIYUE_DISPUTE)
