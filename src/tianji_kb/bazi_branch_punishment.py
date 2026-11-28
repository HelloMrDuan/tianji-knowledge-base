"""地支刑表登记（TJ-0426 Lane 1，S-06）：无表可登，只记缺口。

研究级登记（research_only / public_enabled=False /
ai_enabled=False）。本文件记录一个否定的登记事实：**刑表不存在**
——canonical ``foundations_v1.json`` 的 ``earthly_branch_relations``
只含 clashes / triple_harmonies / directional_meetings /
six_harmonies / harms 五组，不含刑表；本仓库亦无任何已登记的刑
表来源取证。因此 ``PUNISHMENT_TABLE`` 为 None，且本文件不提供任
何刑分组、刑条件或刑效力——无来源只记缺口，绝不在引擎内自造刑表。

已登记的相关事实（只作边界，不作刑表替代）：
* ``bazi.concept.conflict_three_punishments``：三刑跨流派争议未
  解；``bazi_root_conditions`` 的 root 层明言刑依显式任氏口径不
  机械消根（``punishment_policy`` =
  ``not_applied_in_selected_ren_school``），``punishment_status``
  恒 unresolved。
* 强度引擎 ``interaction_conditions``（Q3-A）只记录合/冲/害（冲/
  害/六合只记录、不扣分；天干五合与地支三合因化气未决而弃判）；
  刑无表可录，故不产生任何刑记录，``score_adjustment_total`` 恒 0。

取证后立项时须补：来源＋版本＋可定位文本（逐组刑分组与条件），
经登记后方可谈刑的事实层；刑的效力规则另行立项。
"""

PUNISHMENT_TABLE_ID = 'bazi-branch-punishment-table-v1'
PUNISHMENT_TABLE_RESEARCH_ONLY = True
PUNISHMENT_TABLE_PUBLIC_ENABLED = False
PUNISHMENT_TABLE_AI_ENABLED = False
PUNISHMENT_TABLE_STATUS = 'unregistered'
# 无表：无来源取证之前不得自造刑表。
PUNISHMENT_TABLE = None

PUNISHMENT_GAPS = {
    'canonical_table': 'foundations_v1.json earthly_branch_relations '
                       'has no punishment key (clashes / '
                       'triple_harmonies / directional_meetings / '
                       'six_harmonies / harms only)',
    'registered_conflict': 'bazi.concept.conflict_three_punishments '
                           '(punishment_policy='
                           'not_applied_in_selected_ren_school; '
                           'punishment_status unresolved)',
    'engine_effect': 'interaction_conditions emits no punishment '
                     'records; Q3-A record-only does not extend to '
                     'punishment (nothing to record from)',
    'evidence_needed': [
        'source + version + locatable text for each punishment '
        'grouping and its conditions',
        'registration of the grouping table before any fact layer',
        'separate adjudication before any effect rule',
    ],
}


def validate_punishment_registration():
    """Validate the negative registration: table absent, gap named."""
    checks = {
        'table_is_none': PUNISHMENT_TABLE is None,
        'status_unregistered': PUNISHMENT_TABLE_STATUS == 'unregistered',
        'gap_names_canonical_absence':
            'earthly_branch_relations' in PUNISHMENT_GAPS['canonical_table'],
        'gap_names_registered_conflict':
            'bazi.concept.conflict_three_punishments'
            in PUNISHMENT_GAPS['registered_conflict'],
        'research_only': PUNISHMENT_TABLE_RESEARCH_ONLY is True
            and PUNISHMENT_TABLE_PUBLIC_ENABLED is False
            and PUNISHMENT_TABLE_AI_ENABLED is False,
    }
    return {'valid': all(checks.values()), 'checks': checks}
