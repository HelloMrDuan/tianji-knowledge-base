"""TJ-018.3 阳刃节「凶/㓙」登记—应用分歧勘误登记册（E0354）。

本模块为纯数据登记：只登记《三命通会》卷五《论阳刃》节内两处
「防」位点的登记—应用分歧为订正集勘误条目，并附同节全部 25 处
校勘读法为「㓙」的「防」位点逐处复核表。本模块不订正任何文本：
S0 快照、S3 应用文本、密封快照、Canonical s064 节文本与既有校勘
记逐字未动；不被任何可执行路径 import，不含任何判定逻辑。

分歧来历：B-2 禄刃两节晋级（E0339）发现并如实披露于
``docs/product/TJ0183_LUREN_PROMOTION.md`` §3.2，密封专项
``tests/test_phase2_baziluren.py`` 以精确枚举钉住恰这两处（第三处
出现即测试失败）；治理 pending 审计（E0341，
``docs/product/GOVERNANCE_PENDING8_AUDIT.md`` §3）定性为校勘订正
（勘误）路径——登记先行、是否定向重应用生成新版 S3 属独立决策，
不与本登记捆绑。本批即该路径的第一步：只登记，不应用。
"""

YANGREN_ERRATA_REGISTER = {
    "id": "sanming-yangren-errata-register-v1",
    "task": "TJ-018.3 阳刃节「凶/㓙」登记—应用分歧勘误登记",
    "ledger_event": "E0354",
    "ledger_row": "TJ-018.2",
    "baseline_main_sha": "297bd936767fbe60d50d51355f82b82e6a961b6d",
    "kind": "collation_errata_registration",
    "registration_date": "2026-11-01",
    "collation_register": "sanming-juan5-collation-register-v1",
    "collation_module": "src/tianji_kb/"
                        "bazi_sanming_juan5_zaqi_yangren_collation.py",
    "register_section_id": "sanming.juan5.yangren",
    "canonical_section_id": "bazi.section.s064",
    "purpose": "把阳刃节两处已 confirmed 登记读法「㓙」被订正集正式"
               "应用作「凶」的偏离定格为勘误条目（原应用字、应从登记"
               "读法、见证依据、影响声明、未应用状态），供后续独立"
               "的重应用决策引用；本登记本身不构成任何文本订正",
}

REVIEW_BASIS = {
    "snapshot_text": {
        "path": "data/quarantine/public_domain_snapshots/daizhigev20/"
                "sanming_tonghui.txt",
        "sha256": "00e2a7db8bb59b259b99938033bb1bb77947e04a15dafc111"
                  "e62b59378010c86",
        "chars": 461157,
        "stage": "S0",
    },
    "applied_text": {
        "path": "data/quarantine/public_domain_snapshots/daizhigev20/"
                "sanming_tonghui_applied_v1.txt",
        "sha256": "a89c0b5da16ea4e07dc85180c49135ed280875318059f923"
                  "ff7154f2c217662f",
        "chars": 461156,
        "stage": "S3",
    },
    "s0_to_s3_displacement": -1,
    "sealed_snapshot_manifest_sha256":
        "26b63e64bed736b08a7dcd686f6a75de733fd44ba9eec9195248e697"
        "30485329",
    "verification": "2026-11-01 于可信机 live 密封快照直读：25 处位点"
                    "逐处比对 S0 原字（全为「防」）与 S3 应用字，分布"
                    "与在册披露逐项对平；S0/S3 文件哈希与正式应用批"
                    "钉值（E0298）逐字一致",
    "review_scope": "阳刃节内校勘记 snapshot_glyph 为「防」且登记读法"
                    "为「㓙」的全部位点（校勘册 "
                    "bazi_sanming_juan5_zaqi_yangren_collation 的 "
                    "COLLATION_NOTES 中 section_id 为 "
                    "sanming.juan5.yangren 者）",
}

SECTION_REVIEW_SUMMARY = {
    "positions_reviewed": 25,
    "applied_as_registered": 17,
    "residual_snapshot_glyph_retained": 6,
    "divergent_applied_xiong": 2,
    "other": 0,
    "conclusion": "偏离恰 2 处（S0 182078 与 S0 182375），无第三处；"
                  "6 处残余「防」为未应用保留快照原字，与 P2 残余处置"
                  "口径一致，不属本勘误范围",
}

SECTION_REVIEW = [
    {'s0_offset': 181025, 's3_offset': 181024, 'collation_ref': 'sm5y-fang-181025', 'snapshot_glyph': '防', 'registered_reading': '㓙', 'reading_status': 'confirmed', 'usable_grade': 'Q1', 'disposition': 'corrected', 'applied_glyph': '㓙', 'conclusion': 'applied_as_registered'},
    {'s0_offset': 181169, 's3_offset': 181168, 'collation_ref': 'sm5y-fang-181169', 'snapshot_glyph': '防', 'registered_reading': '㓙', 'reading_status': 'confirmed', 'usable_grade': 'Q1', 'disposition': 'corrected', 'applied_glyph': '㓙', 'conclusion': 'applied_as_registered'},
    {'s0_offset': 181174, 's3_offset': 181173, 'collation_ref': 'sm5y-fang-181174', 'snapshot_glyph': '防', 'registered_reading': '㓙', 'reading_status': 'confirmed', 'usable_grade': 'Q1', 'disposition': 'corrected', 'applied_glyph': '㓙', 'conclusion': 'applied_as_registered'},
    {'s0_offset': 181190, 's3_offset': 181189, 'collation_ref': 'sm5y-fang-181190', 'snapshot_glyph': '防', 'registered_reading': '㓙', 'reading_status': 'confirmed', 'usable_grade': 'Q1', 'disposition': 'corrected', 'applied_glyph': '㓙', 'conclusion': 'applied_as_registered'},
    {'s0_offset': 181200, 's3_offset': 181199, 'collation_ref': 'sm5y-fang-181200', 'snapshot_glyph': '防', 'registered_reading': '㓙', 'reading_status': 'confirmed', 'usable_grade': 'Q1', 'disposition': 'corrected', 'applied_glyph': '㓙', 'conclusion': 'applied_as_registered'},
    {'s0_offset': 181279, 's3_offset': 181278, 'collation_ref': 'sm5y-fang-181279', 'snapshot_glyph': '防', 'registered_reading': '㓙', 'reading_status': 'confirmed', 'usable_grade': 'Q1', 'disposition': 'corrected', 'applied_glyph': '㓙', 'conclusion': 'applied_as_registered'},
    {'s0_offset': 181314, 's3_offset': 181313, 'collation_ref': 'sm5y-fang-181314', 'snapshot_glyph': '防', 'registered_reading': '㓙', 'reading_status': 'confirmed', 'usable_grade': 'Q1', 'disposition': 'corrected', 'applied_glyph': '㓙', 'conclusion': 'applied_as_registered'},
    {'s0_offset': 181372, 's3_offset': 181371, 'collation_ref': 'sm5y-fang-181372', 'snapshot_glyph': '防', 'registered_reading': '㓙', 'reading_status': 'confirmed', 'usable_grade': 'Q1', 'disposition': 'corrected', 'applied_glyph': '㓙', 'conclusion': 'applied_as_registered'},
    {'s0_offset': 181532, 's3_offset': 181531, 'collation_ref': 'sm5y-fang-181532', 'snapshot_glyph': '防', 'registered_reading': '㓙', 'reading_status': 'confirmed', 'usable_grade': 'Q1', 'disposition': 'corrected', 'applied_glyph': '㓙', 'conclusion': 'applied_as_registered'},
    {'s0_offset': 181862, 's3_offset': 181861, 'collation_ref': 'sm5y-fang-181862', 'snapshot_glyph': '防', 'registered_reading': '㓙', 'reading_status': 'confirmed', 'usable_grade': 'Q1', 'disposition': 'corrected', 'applied_glyph': '㓙', 'conclusion': 'applied_as_registered'},
    {'s0_offset': 181873, 's3_offset': 181872, 'collation_ref': 'sm5y-fang-181873', 'snapshot_glyph': '防', 'registered_reading': '㓙', 'reading_status': 'confirmed', 'usable_grade': 'Q1', 'disposition': 'corrected', 'applied_glyph': '㓙', 'conclusion': 'applied_as_registered'},
    {'s0_offset': 181891, 's3_offset': 181890, 'collation_ref': 'sm5y-fang-181891', 'snapshot_glyph': '防', 'registered_reading': '㓙', 'reading_status': 'confirmed', 'usable_grade': 'Q1', 'disposition': 'corrected', 'applied_glyph': '㓙', 'conclusion': 'applied_as_registered'},
    {'s0_offset': 181918, 's3_offset': 181917, 'collation_ref': 'sm5y-fang-181918', 'snapshot_glyph': '防', 'registered_reading': '㓙', 'reading_status': 'confirmed', 'usable_grade': 'Q1', 'disposition': 'corrected', 'applied_glyph': '㓙', 'conclusion': 'applied_as_registered'},
    {'s0_offset': 182078, 's3_offset': 182077, 'collation_ref': 'sm5y-fang-182078', 'snapshot_glyph': '防', 'registered_reading': '㓙', 'reading_status': 'confirmed', 'usable_grade': 'Q1', 'disposition': 'corrected', 'applied_glyph': '凶', 'conclusion': 'divergent_applied_xiong'},
    {'s0_offset': 182120, 's3_offset': 182119, 'collation_ref': 'sm5y-fang-182120', 'snapshot_glyph': '防', 'registered_reading': '㓙', 'reading_status': 'confirmed', 'usable_grade': 'Q1', 'disposition': 'corrected', 'applied_glyph': '㓙', 'conclusion': 'applied_as_registered'},
    {'s0_offset': 182291, 's3_offset': 182290, 'collation_ref': 'sm5y-fang-182291', 'snapshot_glyph': '防', 'registered_reading': '㓙', 'reading_status': 'confirmed', 'usable_grade': 'Q1', 'disposition': 'corrected', 'applied_glyph': '㓙', 'conclusion': 'applied_as_registered'},
    {'s0_offset': 182375, 's3_offset': 182374, 'collation_ref': 'sm5y-fang-182375', 'snapshot_glyph': '防', 'registered_reading': '㓙', 'reading_status': 'confirmed', 'usable_grade': 'Q1', 'disposition': 'corrected', 'applied_glyph': '凶', 'conclusion': 'divergent_applied_xiong'},
    {'s0_offset': 182438, 's3_offset': 182437, 'collation_ref': 'sm5y-fang-182438', 'snapshot_glyph': '防', 'registered_reading': '㓙', 'reading_status': 'confirmed', 'usable_grade': 'Q1', 'disposition': 'corrected', 'applied_glyph': '㓙', 'conclusion': 'applied_as_registered'},
    {'s0_offset': 182493, 's3_offset': 182492, 'collation_ref': 'sm5y-fang-182493', 'snapshot_glyph': '防', 'registered_reading': '㓙', 'reading_status': 'confirmed', 'usable_grade': 'Q1', 'disposition': 'corrected', 'applied_glyph': '防', 'conclusion': 'residual_snapshot_glyph_retained'},
    {'s0_offset': 182679, 's3_offset': 182678, 'collation_ref': 'sm5y-fang-182679', 'snapshot_glyph': '防', 'registered_reading': '㓙', 'reading_status': 'confirmed', 'usable_grade': 'Q1', 'disposition': 'corrected', 'applied_glyph': '防', 'conclusion': 'residual_snapshot_glyph_retained'},
    {'s0_offset': 183540, 's3_offset': 183539, 'collation_ref': 'sm5y-fang-183540', 'snapshot_glyph': '防', 'registered_reading': '㓙', 'reading_status': 'confirmed', 'usable_grade': 'Q1', 'disposition': 'corrected', 'applied_glyph': '防', 'conclusion': 'residual_snapshot_glyph_retained'},
    {'s0_offset': 183644, 's3_offset': 183643, 'collation_ref': 'sm5y-fang-183644', 'snapshot_glyph': '防', 'registered_reading': '㓙', 'reading_status': 'confirmed', 'usable_grade': 'Q1', 'disposition': 'corrected', 'applied_glyph': '㓙', 'conclusion': 'applied_as_registered'},
    {'s0_offset': 183983, 's3_offset': 183982, 'collation_ref': 'sm5y-fang-183983', 'snapshot_glyph': '防', 'registered_reading': '㓙', 'reading_status': 'confirmed', 'usable_grade': 'Q1', 'disposition': 'corrected', 'applied_glyph': '防', 'conclusion': 'residual_snapshot_glyph_retained'},
    {'s0_offset': 184103, 's3_offset': 184102, 'collation_ref': 'sm5y-fang-184103', 'snapshot_glyph': '防', 'registered_reading': '㓙', 'reading_status': 'confirmed', 'usable_grade': 'Q1', 'disposition': 'corrected', 'applied_glyph': '防', 'conclusion': 'residual_snapshot_glyph_retained'},
    {'s0_offset': 184165, 's3_offset': 184164, 'collation_ref': 'sm5y-fang-184165', 'snapshot_glyph': '防', 'registered_reading': '㓙', 'reading_status': 'confirmed', 'usable_grade': 'Q1', 'disposition': 'corrected', 'applied_glyph': '防', 'conclusion': 'residual_snapshot_glyph_retained'},
]

ERRATA = [
    {
        "id": "sm5y-errata-182078",
        "collation_ref": "sm5y-fang-182078",
        "position": {
            "register_section_id": "sanming.juan5.yangren",
            "canonical_section_id": "bazi.section.s064",
            "quote_id": "yr.ersha",
            "char_index_in_quote": 6,
            "s0_offset": 182078,
            "s3_offset": 182077,
            "context_short": "则以好命断之又曰阳刄者天上之防星人间之煞喜偏官印绶忌反吟",
        },
        "snapshot_glyph": "防",
        "registered_reading": {
            "reading": "㓙",
            "reading_status": "confirmed",
            "usable_grade": "Q1",
            "disposition": "corrected",
        },
        "witness_basis": [
            {"kind": "witness",
             "witness": "kanripo/KR3g0042",
             "locator": "KR3g0042_005.txt",
             "quote_short": "以好命斷之又曰陽刄者天上之㓙星人間之悪煞喜偏官印綬忌反"},
            {"kind": "witness",
             "witness": "mikkokotila/Sanming-Tongshui",
             "locator": "source/juan-05.md",
             "quote_short": "以好命斷之又曰陽刄者天上之㓙星人間之𢙣煞喜偏官印綬忌反"},
        ],
        "witness_summary": "两家见证同作「㓙」，无对立见证；登记读法有"
                           "双见证支撑且已定级 confirmed/Q1",
        "application_current": {
            "applied_glyph": "凶",
            "applied_in": "sanming_tonghui_applied_v1.txt (S3)",
            "note": "该字既非登记读法「㓙」、亦非快照原字「防」；本批"
                    "登记后 S3 文本逐字未动",
        },
        "deviation_characterization": "application_deviation",
        "deviation_statement": "订正集正式应用对已 confirmed 登记的偏离"
                               "，属应用层勘误；不是登记错误（登记有双"
                               "见证且定级在册），也不是见证分歧（无对"
                               "立见证）；「凶」为「㓙」的现代通行字形，"
                               "两读同词，歧义只在字形层",
        "impact_statement": "零影响：本位点所在引文 yr.ersha 为 018-F "
                            "登记引文，不是 Phase1 规则 "
                            "bazi.rule.r035 的 source_refs（r035 绑定"
                            "恰 4 条：renshi.luren_route_exclusion、"
                            "sanming.lu_sentence、sanming.ren_doctrine、"
                            "sanming.ren_positions）；不涉及任何 "
                            "determination",
        "status": "registered_unapplied",
        "follow_up_decision": "是否定向重应用（按登记读法订正 S3 本位"
                              "点并连动 s064 节文本与快照换代）属独立"
                              "决策，本批不裁、不执行",
    },
    {
        "id": "sm5y-errata-182375",
        "collation_ref": "sm5y-fang-182375",
        "position": {
            "register_section_id": "sanming.juan5.yangren",
            "canonical_section_id": "bazi.section.s064",
            "quote_id": "yr.he_xing",
            "char_index_in_quote": 16,
            "s0_offset": 182375,
            "s3_offset": 182374,
            "context_short": "日刄大忌冲合喜官煞相制合者防遇印者吉有煞无刃施为有勇无威",
        },
        "snapshot_glyph": "防",
        "registered_reading": {
            "reading": "㓙",
            "reading_status": "confirmed",
            "usable_grade": "Q1",
            "disposition": "corrected",
        },
        "witness_basis": [
            {"kind": "witness",
             "witness": "kanripo/KR3g0042",
             "locator": "KR3g0042_005.txt",
             "quote_short": "刄大忌衝合喜官煞相制合刑者㓙遇印者吉有煞無刃施為有勇無"},
            {"kind": "witness",
             "witness": "mikkokotila/Sanming-Tongshui",
             "locator": "source/juan-05.md",
             "quote_short": "刄大忌衝合喜官煞相制合𠛬者㓙遇印者吉有煞無刃施為有勇無"},
        ],
        "witness_summary": "两家见证同作「㓙」，无对立见证；登记读法有"
                           "双见证支撑且已定级 confirmed/Q1",
        "application_current": {
            "applied_glyph": "凶",
            "applied_in": "sanming_tonghui_applied_v1.txt (S3)",
            "note": "该字既非登记读法「㓙」、亦非快照原字「防」；本批"
                    "登记后 S3 文本逐字未动",
        },
        "deviation_characterization": "application_deviation",
        "deviation_statement": "订正集正式应用对已 confirmed 登记的偏离"
                               "，属应用层勘误；不是登记错误（登记有双"
                               "见证且定级在册），也不是见证分歧（无对"
                               "立见证）；「凶」为「㓙」的现代通行字形，"
                               "两读同词，歧义只在字形层",
        "impact_statement": "零影响：本位点所在引文 yr.he_xing 为 018-F "
                            "登记引文，不是 Phase1 规则 "
                            "bazi.rule.r035 的 source_refs（r035 绑定"
                            "恰 4 条：renshi.luren_route_exclusion、"
                            "sanming.lu_sentence、sanming.ren_doctrine、"
                            "sanming.ren_positions）；不涉及任何 "
                            "determination",
        "status": "registered_unapplied",
        "follow_up_decision": "是否定向重应用（按登记读法订正 S3 本位"
                              "点并连动 s064 节文本与快照换代）属独立"
                              "决策，本批不裁、不执行",
    },
]

CONTAINMENT_REFERENCES = {
    "sealed_enumeration_pin": {
        "test_file": "tests/test_phase2_baziluren.py",
        "pin": "divergent == {('yr.ersha', 6), ('yr.he_xing', 16)}，且该"
               "两处 S3 字断言为「凶」、登记 mapped_reading 断言为「㓙」",
        "posture": "本批未动该钉：勘误登记落地后，两处在 S3 中仍作"
                   "「凶」，枚举与断言继续成立；若后续重应用批订正文"
                   "本，须由该批同步修订此钉",
    },
    "disclosure_references": [
        "docs/product/TJ0183_LUREN_PROMOTION.md §3.2（B-2 披露）",
        "docs/product/GOVERNANCE_PENDING8_AUDIT.md §3（勘误路径定性）",
        "docs/product/TJ0183_YANGREN_ERRATA.md（本批登记文档）",
    ],
    "state_before_registration": "已披露、已钉住、未订正",
    "state_after_registration": "已披露、已钉住、已登记勘误、未订正",
}
