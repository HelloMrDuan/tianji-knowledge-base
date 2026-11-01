"""S5 密封 Phase1/Phase2 注册治理登记（TJ-011.2 路线 S5 批）。

本模块是纯数据登记：逐项清点全仓 `pending_phase1_rule_registration`
披露项，给出每项的处置（registered / maintained_pending /
not_a_candidate）、实证理由与解锁路径，并记录 S5 批实际完成的密封
注册（规则 ID、快照 manifest 前后值）。它不含任何判定逻辑；运行时
披露以各模块自身字段为准，本登记与代码披露的一致性由专项测试钉住
（tests/test_tj0112_s5_registration_public.py 公开侧 +
tests/test_phase2_baziregistration.py 密封侧）。

处置理由分类：
- canonical_evidence_absent：谓词/Variant 的定义性原典锚点在密封
  Canonical 中无对应 section（或其经典根本不在 Canonical 内），
  Phase1 规则的 source_refs 无从逐字验证——强行登记即证据冒充。
- execution_binding_structure：原典锚点虽在 Canonical，但该产出不经
  ExecutionTrace 执行绑定（独立组合函数 / 独立 Variant / Phase2
  golden harness 输入契约不覆盖），注册一个无执行步的规则即空注册。
- inherited_pending：组合/视图层，继承底层 Variant 的 pending 状态，
  本身无独立规则可登记。
"""

GOVERNANCE_BATCH = {
    'batch': 'TJ-011.2 S5 密封 Phase1/Phase2 注册治理批',
    'event': 'E0254',
    'date': '2026-10-28',
    'document': 'docs/product/TJ0112_S5_REGISTRATION_GOVERNANCE.md',
}

# S5 批实际执行的密封注册记录（可信机受控环境，经既有快照/manifest
# 钉定流程：私有数据树著录 -> private_data_snapshot 导出 -> 校验 ->
# 换位 live 快照 -> 更新 cicd/env/trusted-acceptance 钉值）。
S5_REGISTRATION_RECORD = {
    'phase1_rules_added': ['bazi.rule.r029', 'bazi.rule.r030'],
    'phase2_rules_added': [
        'bazi.phase2.strength_pure_generating_support',
        'bazi.phase2.strength_commanding_visible_support'],
    'golden_cases_added': [
        'bazi.adjudication-strong-hai-generating',
        'bazi.adjudication-strong-bingwu-commanding'],
    'sealed_files_changed': [
        'data/canonical/bazi/phase1_knowledge.json',
        'data/canonical/bazi/phase2_execution.json',
        'data/canonical/bazi/phase2_golden.json'],
    'sealed_file_sha256_after': {
        'data/canonical/bazi/phase1_knowledge.json':
            '5d992d2e967f9362573cdda788efc02405af28132a4eec2c378f5ac83b2d26ea',
        'data/canonical/bazi/phase2_execution.json':
            '947cfc1d05c248c9e4d1efd35e9fde450e0dee2f77b1a4d150b92b9492ae8720',
        'data/canonical/bazi/phase2_golden.json':
            'eebda931f7be6a812a7929ad1052905330dcabc80637a997a128e6f1ba1ac3ca'},
    'snapshot_files_before': 235,
    'snapshot_files_after': 235,
    'snapshot_bytes_before': 13518179,
    'snapshot_bytes_after': 13566359,
    'manifest_sha256_before':
        '8055efb3881128837548da2536f210928db96b4f295ad25bbfb09ba9cf89c6c1',
    'manifest_sha256_after':
        'f053761c3873d6d5cd63b738786c9b8ef683fd18f3b95c80f7bc485110cde480',
    'pin_record': '新钉值（manifest_sha256_after）须与本批 PR 合并同步'
                  '换位 live 快照并更新可信机 cicd/env/trusted-acceptance；'
                  '本批未先行换钉——实测旧代码对新快照在 validate_phase2 '
                  '阶段 fail-closed（新契约引用的回归测试不存在于旧代码），'
                  '先行换钉会阻断现行 main 的部署验收，见治理文档 §3。',
    'verdict_surface_change': '无：两条翻转谓词的 classification、条件集、'
                              'blockers 与全部其他谓词/变体的产出逐字不变；'
                              '变化仅在 why.sufficient_rule（None -> 注册 '
                              'ID）、matched_rule_ids（新增注册规则步）与'
                              '披露文本。',
}

# TJ-018.3 P1《论三刑》Canonical 建节记录（E0329，用户 2026-10-30
# 授权 P1 直接实施）：在密封 Canonical 内为三命通会《论三刑》建
# chapter/section/term 并完成 11 条登记引文的逐字绑定；执行链核查
# 结论为注册前提不成立（见 REGISTRATION_INVENTORY 的
# sanxing-branch-fact-v1 项），evidence_binding 不翻转、无规则新增。
# 形制与 S5_REGISTRATION_RECORD 同构：私有数据树著录 -> 暂存导出
# -> 校验 -> 父级合并时同步换位 live 快照并改钉。
TJ0183_P1_RECORD = {
    'batch': 'TJ-018.3 P1 三刑 Canonical 逐节晋级批',
    'event': 'E0329',
    'date': '2026-10-30',
    'document': 'docs/product/TJ0183_P1_SANXING_CANONICAL_PROMOTION.md',
    'canonical_chapters_added': ['bazi.chapter.sanming_sanxing'],
    'canonical_sections_added': ['bazi.section.s060'],
    'canonical_terms_added': ['bazi.term.branch_punishments'],
    'classic_source_ids_added': {
        'bazi.classic.sanming_tonghui': [
            'bazi.source.sanmingtonghui',
            'bazi.source.sanmingtonghui-applied'],
    },
    'public_config_registrations': [
        'config/knowledge_sources.json: bazi.source.sanmingtonghui'
        '-applied（TJ-018.3 正式应用文本 S3 登记为来源：快照 S0 切片'
        '含 PUA 8 处、与 Canonical 全域 section 文本零 PUA 不变量'
        '冲突，S3 切片 PUA 归零且登记引文 11 条逐字在场；S0 仍为'
        '原文依据，整书 canonical_ready=false 不变）',
        'config/phase2_source_audit.json: 同源谱系行（lineage_group'
        ' 与 S0 同组 garychowcmu/daizhigev20，不投独立票，'
        'edition/authority unverified、grade_ceiling C）'],
    'phase1_rules_added': [],
    'phase2_rules_added': [],
    'golden_cases_added': [],
    'quotes_verified': [
        'sm3.enum_opening', 'sm3.enum_group4_partial',
        'sm3.direction_statement', 'sm3.summary_groups',
        'sm3.counting_method', 'sm3.wuen_core',
        'sm3.zixing_definition', 'sm3.sanche_variant',
        'sm3.houyue_bracket', 'sm3.chong_definition',
        'sm3.polu_poma'],
    'registration_disposition': 'maintained_pending'
        '（execution_binding_structure）：事实层 evidence_binding '
        '保持 pending_phase1_registration、phase2_rule 与 '
        'sufficient_rule 保持 None，不建空注册、不伪造执行绑定；'
        'Canonical 建节消除了本切片的 canonical_evidence_absent '
        '面，剩余缺口只有执行绑定结构一项。',
    'sealed_files_changed': [
        'data/canonical/bazi/phase1_knowledge.json',
        'data/coverage/phase1.json',
        'data/product/knowledge_coverage.json',
        'data/product/knowledge_dependencies.json'],
    'sealed_file_sha256_after': {
        'data/canonical/bazi/phase1_knowledge.json':
            '04354cbcfb4627dbd823b322f3b48bd83ceee1504db898cbbce6fdd8cff32665',
        'data/coverage/phase1.json':
            '7b6d06285a37040f043eb6c1ea4d5d41b92647077430d9fe7672e166e78afc35',
        'data/product/knowledge_coverage.json':
            '5b459002ad51d0875e2433ab3ca3d2661d572df9713bc0d12ff37c51b56930a9',
        'data/product/knowledge_dependencies.json':
            '2699af38a87e2fbb514fe1cfcf98b0dee957fa68a813faea5ece89a13f12f8cf'},
    'snapshot_files_before': 237,
    'snapshot_files_after': 237,
    'snapshot_bytes_before': 15883200,
    'snapshot_bytes_after': 15902169,
    'manifest_sha256_before':
        '5ea551f5ffe3e3abbe42f4edf03dfe9d973fd7bc49ab7207180dc454ea874cbc',
    'manifest_sha256_after':
        '305e20be96a38b614495236f8c3252cf7e21c6d1635a5a29bce1c299b746526c',
    'pin_record': '新钉值（manifest_sha256_after）须与本批 PR 合并'
                  '同步换位 live 快照并更新可信机 cicd/env/'
                  'trusted-acceptance 与私有构建脚本钉值；本批未'
                  '先行换钉（暂存快照只用于机上复跑），回退路径'
                  '不变（恢复旧快照目录 + 旧钉值）。',
    'verdict_surface_change': '无：129 个真实盘（119 个密封 Phase2 '
                              'Golden 柱面输入 + 10 个三刑真实出生'
                              '时刻盘）在旧快照与暂存新快照、同一'
                              '公开代码下，chart 全量产出、三刑事实'
                              '与公开投影逐字一致（机上同盘差异'
                              '测试，输出 21MB JSON 字节级相同）。',
}

# TJ-018.3 批一三刑事实执行接入记录（E0333，用户 2026-10-30
# 授权，设计 docs/product/TJ0183_EXECUTION_BINDING_DESIGN.md
# §2/§9）：事实函数经唯一接入点接入生产执行并完成 Phase1/
# Phase2 注册，三刑切片的 execution_binding_structure 缺口
# 解除、evidence_binding 翻转。形制与 S5_REGISTRATION_RECORD /
# TJ0183_P1_RECORD 同构：私有数据树著录 -> 暂存导出 -> 校验
# -> 父级合并前同步换位 live 快照并改钉（先换代、后合并）。
TJ0183_EXECBIND_RECORD = {
    'batch': 'TJ-018.3 批一 三刑事实执行接入批',
    'event': 'E0333',
    'date': '2026-10-30',
    'document': 'docs/product/TJ0183_SANXING_EXECUTION_BINDING.md',
    'phase1_rules_added': ['bazi.rule.r031'],
    'phase2_rules_added': ['bazi.phase2.branch_punishment_facts'],
    'golden_cases_added': [
        'bazi.sanxing-fact-chou-wei-partial-no-edges',
        'bazi.sanxing-fact-yin-shen-only',
        'bazi.sanxing-fact-group2-full',
        'bazi.sanxing-fact-group3-full',
        'bazi.sanxing-fact-zi-mao-bidirectional',
        'bazi.sanxing-fact-self-chen-double',
        'bazi.sanxing-fact-g6b-self-you-triple',
        'bazi.sanxing-fact-empty-self-singles',
        'bazi.sanxing-fact-zi-mao-multi-pillar',
        'bazi.sanxing-fact-group2-partial-with-edge'],
    'source_refs_subset': [
        'sm3.enum_opening', 'sm3.enum_group4_partial',
        'sm3.summary_groups', 'sm3.counting_method',
        'sm3.wuen_core', 'sm3.zixing_definition'],
    'source_refs_subset_basis': '审定登记（E0267）GROUP_TABLE '
        '三组与 self_punishment 行 evidence_refs 的并集，恰 6 '
        '条；逐条逐字验证于 bazi.section.s060 节文本（快照字形'
        '本）；覆盖组表、三组环边（A 级六条见 enum_opening、'
        'B 级卯刑子见 counting_method）与自刑全集（辰午酉见 '
        'enum_opening、亥见 enum_group4_partial、'
        'zixing_definition 为全集定义）。设计 §10.2 子集定稿属'
        '实施批审定事项，本批按此可审计口径定稿，未扩到 11 条。',
    'registration_flip': 'sanxing-branch-fact-v1 处置由 '
        'maintained_pending（execution_binding_structure）翻转'
        '为 registered；bazi_sanxing_facts.SLICE_REGISTRATION '
        '的 evidence_binding 翻转为 registered_phase1_phase2、'
        'phase2_rule 填入 bazi.phase2.branch_punishment_facts、'
        'sufficient_rule 保持 None。翻转五条件中本地四项（真实'
        '执行接入、Trace 真实步、EvidenceResolver 实测绑定、'
        'Golden 与规定测试全过）已在机上全配方复跑实证；第五'
        '项（正式验收与部署验证）为终局条件，由父级关账时复'
        '核，PR 内翻转视为待终局确认。',
    'e0267_takeover': '审定模块 bazi_sanxing_fact_adjudication '
        '以 append-only 常量 EXECUTION_BINDING_TAKEOVER 承接 '
        'E0267 的 consumption_boundaries 与 placement_decision'
        '；SLICE_SPEC 原文字逐字未动。',
    'sealed_files_changed': [
        'data/canonical/bazi/phase1_knowledge.json',
        'data/canonical/bazi/phase2_execution.json',
        'data/canonical/bazi/phase2_golden.json',
        'data/coverage/phase1.json'],
    'sealed_file_sha256_after': {
        'data/canonical/bazi/phase1_knowledge.json':
            '44b448b60b4cc39825b35274dd2b647687dc56110fecffd8c9b33f5a2078d221',
        'data/canonical/bazi/phase2_execution.json':
            '209f589ab3f00584dbf869b57f42fc6b04b855d75bad72d28087c0e3b37dcacf',
        'data/canonical/bazi/phase2_golden.json':
            '06d88927df44e282ae897f891d32dba15eaec2b8e0505e7838170c67cd17ee38',
        'data/coverage/phase1.json':
            '38ae2617400bbd04b1774f4b170d84836031465029a53f668552c7d8ee4b4bfd'},
    'snapshot_files_before': 237,
    'snapshot_files_after': 237,
    'snapshot_bytes_before': 15902169,
    'snapshot_bytes_after': 15922702,
    'manifest_sha256_before':
        '305e20be96a38b614495236f8c3252cf7e21c6d1635a5a29bce1c299b746526c',
    'manifest_sha256_after':
        'b93e4b97830ff15aca1a9e77847796e5ddd5cb7e1f3cd6512db20a358c159622',
    'pin_record': '新钉值（manifest_sha256_after）须由父级在本'
                  '批 PR 合并前换位 live 快照并更新可信机 cicd '
                  '钉值（先换代、后合并，E0329 竞态教训）；私有'
                  '检出侧 EXPECTED_BYTES=15922702 与检出 '
                  'manifest 已同步重生并 verify 通过；回退路径'
                  '不变（恢复旧快照目录 + 旧钉值，且开启路径在'
                  '旧快照下 fail-closed、默认路径与 P1 基线一致，'
                  '回滚演练记录见治理文档 §4）。',
    'verdict_surface_change': '默认表面零变化：129 个真实盘'
                              '（119 个密封 Phase2 Golden 柱面'
                              '输入 + 10 个三刑真实出生时刻盘）'
                              '门控关全产出逐字一致；门控开仅在'
                              '设计 §7.2 封闭清单内变化（result '
                              '新增 branch_punishment_facts 键与 '
                              'production_scope 一句、trace 新增'
                              '事实步一条、evidence 与 '
                              'rule_matches 各增该步条目、封套'
                              '研究标记、其后步 fact_ref 索引位'
                              '移而所指内容逐字一致）。事实步不'
                              '产生 RuleMatch、不写入 '
                              'sufficient_rule、不进任何裁决输'
                              '入；用户可见能力零变化（公开投影'
                              '剥离、研究门控默认关）。',
}

# TJ-018.3 批二卷二干支三规则实施批记录（E0335，用户 2026-10-30
# 锁定顺序、2026-10-31 授权启动；规范依据 P2 干支审定 E0331 与
# 执行绑定设计 §§0–7）：为三命卷二干支两节建 Canonical
# chapter/section 并逐条绑定引文，三条旺衰谓词各以自有 Phase1
# 规则（r032/r033/r034）与 Phase2 规则步完成注册，逐谓词独立
# 翻转。形制与 TJ0183_EXECBIND_RECORD 同构：私有数据树著录 ->
# 暂存导出 -> 校验 -> 父级合并前同步换位 live 快照并改钉
# （先换代、后合并）。
TJ0183_P2_RECORD = {
    'batch': 'TJ-018.3 批二 卷二干支三规则实施批',
    'event': 'E0335',
    'date': '2026-10-31',
    'document': 'docs/product/TJ0183_GANZHI_EXECUTION_BINDING.md',
    'canonical_chapters_added': [
        'bazi.chapter.sanming_tianganshengsi',
        'bazi.chapter.sanming_wangxiangjisheng'],
    'canonical_sections_added': ['bazi.section.s061', 'bazi.section.s062'],
    'canonical_terms_added': [],
    'phase1_rules_added': ['bazi.rule.r032', 'bazi.rule.r033', 'bazi.rule.r034'],
    'phase2_rules_added': [
        'bazi.phase2.strength_lu_visible_support',
        'bazi.phase2.strength_pure_support_metal',
        'bazi.phase2.strength_pure_generating_support_water'],
    'golden_cases_added': [
        'bazi.strength-ganzhi-lu-positive',
        'bazi.strength-ganzhi-water-positive',
        'bazi.strength-ganzhi-metal-negative-xin-clashed-roots',
        'bazi.strength-ganzhi-metal-negative-geng-stem-combination'],
    'registration_flip': 'lu_visible_support、pure_support_metal、'
        'pure_generating_support_water 三项处置由 maintained_pending'
        '（canonical_evidence_absent）逐项独立翻转为 registered；'
        'MAINTAINED_ITEMS 由 12 项减为 9 项。三项各自的定义锚绑定、'
        'Golden/等价与注册契约分别成立，不捆绑成败。金×酉步 '
        'validation_status 保持 pending（构造性不可满足、无真实盘'
        '正例，golden_case_ids 指向负例见证集——E0335 父级审定'
        '定稿，治理文档 §3 在册），与步注册本身分开记账。',
    'binding_exclusions': '丁隔离（绑定层）：三条新规 source_refs 与 '
        '{sm2.ding_sheng, sm2.ding_shengsi} 交集为空（密封注册测试'
        '机检断言）；DING_BLOCK 与 DING_SI_DISPOSITION／'
        'DING_YIN_DISPOSITION 的 blocked_by_conflict 登记逐字不变'
        '（回归断言）。□1 排除：任何绑定引文不覆盖 S0/S3 42148、'
        'lunyue_summary 尾段 [42116,42151) 整段排除、伪绑定负例被'
        '拒绝、缺口 disposition=unresolved（密封注册测试三断言）。'
        '帝旺代偿：庚帝旺酉／壬帝旺子全链 framework_derived、等级'
        '随行、注册措辞定稿在册，禁用表述（S1 六条＋火线两条）落'
        '密封测试断言。',
    'sealed_files_changed': [
        'data/canonical/bazi/phase1_knowledge.json',
        'data/canonical/bazi/phase2_execution.json',
        'data/canonical/bazi/phase2_golden.json',
        'data/coverage/phase1.json'],
    'sealed_file_sha256_after': {
        'data/canonical/bazi/phase1_knowledge.json':
            '6501e0b6b042f876ebb314c5e1135ffb809ec983afd019aa2038bd6e1453ca96',
        'data/canonical/bazi/phase2_execution.json':
            'aaf8a385ce1d394a8dae1dd0248238bc42eddb5cdf9ff9b9dafa5945eef21e3c',
        'data/canonical/bazi/phase2_golden.json':
            '7f1620de41ed2fcc93cba2c4a8a26aaa7b0bb42e61cbb0d4be6bdb27d3a4f186',
        'data/coverage/phase1.json':
            'a9aa13a45a230dbe074eac4cf7f447748faa7bd02578867acfe249904ab7bc44'},
    'snapshot_files_before': 237,
    'snapshot_files_after': 237,
    'snapshot_bytes_before': 15922702,
    'snapshot_bytes_after': 15964218,
    'manifest_sha256_before':
        'b93e4b97830ff15aca1a9e77847796e5ddd5cb7e1f3cd6512db20a358c159622',
    'manifest_sha256_after':
        'c815dc4ed02a9b7d0bd1487c3e1ed4e39d0bc826659d4ff0fb7f8a37ff685cdf',
    'pin_record': '新钉值（manifest_sha256_after）须由父级在本批 '
        'PR 合并前换位 live 快照并更新可信机 cicd 钉值（先换代、'
        '后合并，E0329 竞态教训）；私有检出侧 EXPECTED_BYTES='
        '15964218 与检出 manifest 已同步重生并 verify 通过；回退'
        '路径不变（恢复旧快照目录 + 旧钉值，且新代码在旧快照下'
        '对翻转谓词触发盘 fail-closed、默认路径与批一基线逐字'
        '一致，回滚演练记录见治理文档 §6）。',
    'verdict_surface_change': '三谓词裁定面变化仅在设计 §7.2 封闭'
        '清单内：why.sufficient_rule（None -> 各谓词注册步 ID）、'
        'sufficient_predicate 与 predicate_rule_registration 两键'
        '移除、matched_rule_ids 新增注册步、trace 新增注册步及其 '
        'evidence、limitations 注册状态句改写（金/水共用句拆为两'
        '句）、治理登记 disposition 翻转；分类、条件集、blocker '
        '集与其余谓词/变体产出逐盘逐字段不变（等价比对集在册）。'
        '用户可见能力变化仅限翻转谓词的研究层披露字段；production '
        '投影与 research_only 姿态不变。',
}

# TJ-018.3 批三 B-2 禄刃两节 Canonical 晋级与路线注册批记录
# （E0339，评估 E0337 结论 B 的第二批；规范依据批三评估 §3.3 B-2
# 草案与 P1/批一/批二先例）：为三命卷三《论十干禄》与卷五《论阳刃》
# 建 Canonical chapter/section 并逐条复核登记引文，禄刃路线以自有
# Phase1 规则（r035）与 Phase2 步（pattern_route）完成注册，治理
# 登记 pattern-route-luren 联合翻转。形制与 TJ0183_P2_RECORD
# 同构：私有数据树著录 -> 暂存导出 -> 校验 -> 父级合并前同步换位
# live 快照并改钉（先换代、后合并）。
TJ0183_B2_RECORD = {
    'batch': 'TJ-018.3 批三 B-2 禄刃两节 Canonical 晋级与路线注册批',
    'event': 'E0339',
    'date': '2026-10-31',
    'document': 'docs/product/TJ0183_LUREN_PROMOTION.md',
    'canonical_chapters_added': [
        'bazi.chapter.sanming_shiganlu',
        'bazi.chapter.sanming_yangren'],
    'canonical_sections_added': ['bazi.section.s063', 'bazi.section.s064'],
    'canonical_terms_added': ['bazi.term.luren_route'],
    'phase1_rules_added': ['bazi.rule.r035'],
    'phase2_rules_added': ['bazi.phase2.pattern_route'],
    'golden_cases_added': [
        'bazi.luren-route-lu-jia-yin',
        'bazi.luren-route-ren-geng-you',
        'bazi.luren-route-ren-not-lu-jia-mao',
        'bazi.luren-route-ordinary-jia-wu',
        'bazi.luren-route-other-lu-yi-yin',
        'bazi.luren-route-misc-wu-xu',
        'bazi.luren-route-yin-noblade-xin-xu',
        'bazi.luren-route-lu-gui-zi',
        'bazi.luren-route-precedence-jia-yin'],
    'source_refs_subset': [
        'renshi.luren_route_exclusion (s054)',
        'sanming.lu_sentence (s063)',
        'sanming.ren_doctrine (s064)',
        'sanming.ren_positions (s064)'],
    'source_refs_subset_basis': '路线实际消费的四条引文：任氏排除句'
        '（路线规则本体，s054 既有 Canonical）+ 禄/刃两表定义引文'
        '三条。子集定稿沿 r031 先例（只引消费引文、未扩至登记全量）：'
        '阳刃 22 条与禄节 30 条登记引文逐条在对应节文本中在场，另经'
        '密封专项以登记坐标换算逐条复核，不入 r035 的 source_refs。',
    'registration_flip': 'pattern-route-luren 处置由 '
        'maintained_pending（canonical_evidence_absent）翻转为 '
        'registered；MAINTAINED_ITEMS 由 9 项减为 8 项。bazi_pattern '
        '路线块 evidence_binding 翻转为 registered_phase1_phase2、'
        'LUREN_LIMITATIONS 注册状态句改写、LUREN_QUOTES 三条三命'
        '引文 source_section_id 补全（s063/s064）；chart 在 '
        'pattern_variant 开启时以 trace.add 执行注册步。翻转五条件'
        '中本地四项（真实执行接入、Trace 真实步、EvidenceResolver '
        '实测绑定、Golden 与规定测试全过）已在机上全配方复跑实证；'
        '第五项（正式验收与部署验证）为终局条件，由父级关账批'
        '（E0340 预留）复核，PR 内翻转视为待终局确认。',
    'section_residue_carry': '阳刃节残余防 14 位点与 RD-12 seq 450 '
        '并列记录（快照字「防」/四库「䕶」/现代「获·獲」，UD-1=A '
        '定格）随 s064 元数据逐字携带；禄节残余防 1 位点（S3 '
        '76987，P2 seq 47 deferred_no_witness、B-1 登记 unresolved）'
        '随 s063 元数据逐字携带；两处处置状态均不因本批改变，定义'
        '引文范围内残余防为 0（机检断言在册）。',
    'sealed_files_changed': [
        'data/canonical/bazi/phase1_knowledge.json',
        'data/canonical/bazi/phase2_execution.json',
        'data/canonical/bazi/phase2_golden.json',
        'data/coverage/phase1.json'],
    'sealed_file_sha256_after': {
        'data/canonical/bazi/phase1_knowledge.json':
            '19457363a783279ebeb75674ddfde5da7f90e43bc9053936acaaedf129ab41ad',
        'data/canonical/bazi/phase2_execution.json':
            '8332bd98c1f007bfc5e4ba8fe55920961d23856becd2d472ffb2f2c7805be68f',
        'data/canonical/bazi/phase2_golden.json':
            'bad517b3983eff0caf376ff93826a51b1e6bf49e9c81f919d5061444cc5a9a45',
        'data/coverage/phase1.json':
            'dde15c29ac0f9552c98e581598a7fe3661379fc931a2b7420855723469e7f333'},
    'snapshot_files_before': 237,
    'snapshot_files_after': 237,
    'snapshot_bytes_before': 15964218,
    'snapshot_bytes_after': 16001603,
    'manifest_sha256_before':
        'c815dc4ed02a9b7d0bd1487c3e1ed4e39d0bc826659d4ff0fb7f8a37ff685cdf',
    'manifest_sha256_after':
        '15bd5a268d792c86072cf9ac51effb22ca5aefa004ea7ab44e7bbf44135682d5',
    'pin_record': '新钉值（manifest_sha256_after）须由父级在本批 '
                  'PR 合并前换位 live 快照并更新可信机 cicd 钉值（先'
                  '换代、后合并，E0329 竞态教训）；私有检出侧 '
                  'EXPECTED_BYTES=16001603 与检出 manifest 已同步重'
                  '生并 verify 通过；回退路径不变（恢复旧快照目录 + '
                  '旧钉值，且新代码在旧快照下 pattern_variant 路径 '
                  'fail-closed、默认路径与基线逐字一致，回滚演练记录'
                  '见治理文档 §5）。',
    'verdict_surface_change': '路线判定面零变化：等价比对集（密封 '
        'Golden 133 盘 + Slice A 8 盘与 D-1 优先序盘 + 133 盘强制 '
        'pattern_variant）翻转前后全封套比对，差异恰在封闭清单内'
        '（路线块 evidence_binding 与注册状态句、trace 新增注册步、'
        '其 rule_matches 与 evidence 条目、其后步 fact_ref 索引位移'
        '而所指内容逐字一致、治理登记与计数钉迁移）；route 值、'
        'matched_via、determination 与 borrowed_route 逐盘逐字不变。'
        '用户可见能力零变化（公开投影剥离 pattern_route 不变）。',
}

# 治理 pending 8 项审计推荐第一批：pattern-zaqi 晋级批记录
# （E0342，审计 E0341 §2.6/§4.2 推荐；规范依据 Slice B 审定
# B1–B6 与 B-2 禄刃晋级形制）：为滴天髓杂气段与三命两例证窗口
# 建 Canonical section 并逐条绑定引文，杂气选格陈述以自有
# Phase1 规则（r036）与 Phase2 步（pattern_zaqi）完成注册，
# 治理登记 pattern-zaqi 翻转。形制与 TJ0183_B2_RECORD 同构：
# 私有数据树著录 -> 暂存导出 -> 校验 -> 父级合并前同步换位
# live 快照并改钉（先换代、后合并）。
GOVERNANCE_ZAQI_RECORD = {
    'batch': '治理 pending 审计推荐第一批 pattern-zaqi 晋级批',
    'event': 'E0342',
    'date': '2026-10-31',
    'document': 'docs/product/GOVERNANCE_ZAQI_PROMOTION.md',
    'canonical_chapters_added': [
        'bazi.chapter.sanming_rilu_case',
        'bazi.chapter.sanming_nvming_case'],
    'canonical_sections_added': [
        'bazi.section.s065', 'bazi.section.s066', 'bazi.section.s067'],
    'canonical_terms_added': ['bazi.term.zaqi_selection'],
    'phase1_rules_added': ['bazi.rule.r036'],
    'phase2_rules_added': ['bazi.phase2.pattern_zaqi'],
    'golden_cases_added': [
        'bazi.zaqi-selection-wuji-chou-single-exposed',
        'bazi.zaqi-selection-wuji-xu-no-exposed-abstained',
        'bazi.zaqi-selection-general-xu-sanming-type',
        'bazi.zaqi-selection-non-misc-yin-not-applicable',
        'bazi.zaqi-selection-general-chen-no-exposed',
        'bazi.zaqi-selection-wuji-wei-two-exposed'],
    'source_refs_subset': [
        'renshi.zaqi_passage (s065, classical)'],
    'source_refs_subset_basis': 'r036 的 source_refs 恰为陈述的裁定'
        '依据 1 条：原注杂气段是选格陈述的编码依据（规则引文，'
        'classical）。三命两例证不入规则 refs：按 Slice B 审定 B5 '
        '它们只作冲突分支证据、不是裁定依据，且 Phase1 引文角色'
        '枚举（classical / implementation / derivation）无冲突分支'
        '位；其证据地位由 Canonical 窗口节 s066/s067（review scope '
        '明示冲突分支角色）、公开登记侧 source_section_id 补全与陈述'
        '输出 conflict.case_refs 三者承载（两例证逐字在各自窗口节内，'
        '密封专项目测）。子集定稿沿 r031/r035 先例（只引裁定依据）：'
        '两窗口节内其余文本（案一同法条的戊子案前段、案二前后条目）'
        '不入 source_refs。公开登记侧 3 条引文的 source_id 逐字不变'
        '（原注 = ditiansui-spouse、三命 = sanmingtonghui），仅补 '
        'source_section_id。',
    'registration_flip': 'pattern-zaqi 处置由 maintained_pending'
        '（canonical_evidence_absent）翻转为 registered；'
        'MAINTAINED_ITEMS 由 8 项减为 7 项。bazi_pattern 陈述块 '
        'evidence_binding 翻转为 registered_phase1_phase2、rule '
        '与 conflict.case_refs 的 source_section_id 补全（s065/'
        's066/s067）、ZAQI_QUOTES 3 条引文 source_section_id 补'
        '全、ZAQI_ADJUDICATION_NOTES B6 与 ZAQI_LIMITATIONS 的注'
        '册状态句改写；chart 在 pattern_variant 开启时以 trace.add '
        '执行注册步。翻转五条件中本地四项（真实执行接入、Trace '
        '真实步、EvidenceResolver 实测绑定、Golden 与规定测试全'
        '过）已在机上全配方复跑实证；第五项（正式验收与部署验证）'
        '为终局条件，由父级关账批（E0343 预留）复核，PR 内翻转视'
        '为待终局确认。',
    'section_window_basis': '三命两例证建窗口节的节界定稿：案一窗'
        '口 = 卷六《日禄归时》七法第一法「青云得路」整条（S3 '
        '[192089,192173)，84 字，引文在其内 S3 [192130,192173))；'
        '案二窗口 = 女命章诗句条目全文（S3 [245029,245080)，51 '
        '字，与引文同界，前后以换行分隔自成单元）。两窗口均零 '
        'PUA/零□；窗口外同章文本不因本批入 Canonical。滴天髓杂'
        '气段挂既有章 bazi.chapter.pattern_bage（八格章，与真格'
        '定义节 s053/任氏程序节 s054 同章），不新建章。',
    'sealed_files_changed': [
        'data/canonical/bazi/phase1_knowledge.json',
        'data/canonical/bazi/phase2_execution.json',
        'data/canonical/bazi/phase2_golden.json',
        'data/coverage/phase1.json',
        'data/product/knowledge_coverage.json'],
    'sealed_file_sha256_after': {
        'data/canonical/bazi/phase1_knowledge.json':
            'df55c6505b4cad47b315b839313508ad61e844613882d901460576f9c1088818',
        'data/canonical/bazi/phase2_execution.json':
            '97d7c3fa9c06f933ec6f78c4ccba34637b8904cb1a5d91a781947c47d2001d49',
        'data/canonical/bazi/phase2_golden.json':
            '878c5369bb0bdb5e8a6757c949ac90ddb62db2ec0e16e4374144110bdab68d3d',
        'data/coverage/phase1.json':
            '13c117993aeb141a60328468a8ea3f3b4c942770f5d124acab1db083ebb77fa2',
        'data/product/knowledge_coverage.json':
            'a43cc223cf8f5bb26cebcbeed35912ff8fc3c71fc4f14e37d1571b183a0508e0'},
    'snapshot_files_before': 237,
    'snapshot_files_after': 237,
    'snapshot_bytes_before': 16001603,
    'snapshot_bytes_after': 16072121,
    'manifest_sha256_before':
        '15bd5a268d792c86072cf9ac51effb22ca5aefa004ea7ab44e7bbf44135682d5',
    'manifest_sha256_after':
        '6edcebc669e9b3de09856f353f6b1eafc22bff47a8dbfef3f35afdffacc1bfc0',
    'pin_record': '新钉值（manifest_sha256_after）须由父级在本批 '
                  'PR 合并前换位 live 快照并更新可信机 cicd 钉值（先'
                  '换代、后合并，E0329 竞态教训）；私有检出侧 '
                  'EXPECTED_BYTES 与检出 manifest 同步重生并 verify '
                  '通过；回退路径不变（恢复旧快照目录 + 旧钉值，且'
                  '新代码在旧快照下 pattern_variant 路径 fail-closed、'
                  '默认路径与基线逐字一致，回滚演练记录见治理文档）。',
    'verdict_surface_change': '陈述判定面零变化：等价比对集（密封 '
        'Golden 142 盘 + Slice B 6 例见证盘 + 142 盘强制 '
        'pattern_variant）翻转前后全封套比对，差异恰在封闭清单内'
        '（陈述块 evidence_binding 与 rule/case_refs 的 '
        'source_section_id 补全、adjudication_notes 与 scope_limits '
        '的注册状态句、trace 新增注册步与其 rule_matches/evidence '
        '条目、治理登记与计数钉迁移）；status、arm、selection、'
        'conflict 与 determination 逐盘逐字不变。用户可见能力零变'
        '化（公开投影剥离 pattern_zaqi 不变）。',
}

GOVERNANCE_REN_RECORD = {
    'batch': '治理 pending 第二顺位 ren-pattern 执行绑定批',
    'event': 'E0344',
    'date': '2026-10-31',
    'document': 'docs/product/GOVERNANCE_REN_PROMOTION.md',
    'canonical_chapters_added': [],
    'canonical_sections_added': [],
    'canonical_terms_added': ['bazi.term.ren_true_pattern'],
    'phase1_rules_added': ['bazi.rule.r037'],
    'phase2_rules_added': ['bazi.phase2.ren_yin_true_pattern'],
    'golden_cases_added': [
        'bazi.ren-yin-true-t1-wu-zhengcai',
        'bazi.ren-yin-true-n1-touchstone',
        'bazi.ren-yin-true-t2-bing-qisha',
        'bazi.ren-yin-true-f1-boundary-minus-1s',
        'bazi.ren-yin-true-f2-boundary-exact',
        'bazi.ren-yin-true-t3-jia-pianyin',
        'bazi.ren-yin-true-t4-jia-shishen',
        'bazi.ren-yin-true-s3-route-precedence',
        'bazi.ren-yin-true-a1-wu-daymaster-neg',
        'bazi.ren-yin-true-a2-wu-daymaster-pos',
        'bazi.ren-yin-true-a3-bing-daymaster-neg',
        'bazi.ren-yin-true-a4-bing-daymaster-pos',
        'bazi.ren-yin-true-n2-jia-not-visible-2025',
        'bazi.ren-yin-true-s1-non-yin',
        'bazi.ren-yin-true-s2-pilot-uncertain'],
    'source_refs_subset': [
        'renshi.zhenge_definition (bazi.section.s053, classical)',
        'renshi.siling_true_false_procedure (bazi.section.s054, '
        'classical)',
        'sanming yin segment quote in bazi.section.s024 (classical)'],
    'source_refs_subset_basis': '规则 r037 的 source_refs 恰为 D-1 '
        'determination 实际消费的 3 条引文：真格定义取 s053 原注句'
        '（与 D-1 ZHENGE_QUOTES 的 renshi.zhenge_definition 同一条，'
        '本批只作规则引用、不新立引文条），真假程序取 s054 任氏曰句'
        '（renshi.siling_true_false_procedure，与 Slice A 路线排除'
        '引文同为一条原文），寅月分段依据取 s024 三命分段句（试点 '
        'Variant 的分段来源节，与 ZAQI 先例 r036 的「规则 refs 只含'
        '裁定依据」口径同形：两例证与冲突分支证据不入 refs，本批的'
        '例证地位由 15 例 Golden 承载）。',
    'harness_contract_extension': 'golden harness 的输入契约扩展为'
        '最小形态：golden.py / validate_phase2.py / golden schema '
        '零改动，provider 三重钉死（domain/provider/contract 一致'
        '且须 tianji_kb.operations.* 前缀）逐字不变；扩展只落在 '
        'provider 签名（chart 新增门控 kwarg ren_yin_pilot_result，'
        '默认 None 时封套逐字不变）与用例 input 增带该字段。扩展理'
        '由：chart 不携带出生瞬时与 jie 声明、试点不能在 chart 内'
        '调用（审定 D4），试点结果恒为显式输入声明；D6 身份钉验证'
        '与已执行事实交叉核对保持在组合函数内，harness 侧不放宽。'
        '旧契约行为不变由专项测试钉住（无参数时无 ren_yin 键、无新'
        '步；engine 门禁与参数类型拒绝均有公开测试）。',
    'registration_flip': 'ren-pattern-yin-true-v1: '
        'maintained_pending / execution_binding_structure -> '
        'registered (Phase1 bazi.rule.r037, Phase2 '
        'bazi.phase2.ren_yin_true_pattern validated, 15 Golden '
        'cases fire the step); maintained inventory 7 -> 6; the '
        'other five maintained rows are unchanged. Publication '
        'condition five (deployment acceptance binding) stays '
        'pending the E0345 closeout, as with every prior flip.',
    'sealed_files_changed': [
        'data/canonical/bazi/phase1_knowledge.json',
        'data/canonical/bazi/phase2_execution.json',
        'data/canonical/bazi/phase2_golden.json',
        'data/coverage/phase1.json',
        'data/product/knowledge_coverage.json'],
    'sealed_file_sha256_after': {
        'data/canonical/bazi/phase1_knowledge.json':
            '7fb6b8ad23a871e5b8e4e0a52d972ad2254f3ef8a59773562ffe81c2b478f18e',
        'data/canonical/bazi/phase2_execution.json':
            '449d5c8e6a8cf2d04f443bea00d68770103d84655119bda86bd3a8c18cce7bd7',
        'data/canonical/bazi/phase2_golden.json':
            '393f53dc566ab37455964e5f3b761f4293295d20e3d4598b7cd085db29480050',
        'data/coverage/phase1.json':
            '2a35ef718aab2505d867565c0ddd2a7d68abb3c62a63fed9243039dfa19982dd',
        'data/product/knowledge_coverage.json':
            '241820ed62d7ff3ed92e9e7fc05d0189edce3e36a8a14b70d93bb8bc6f1803e3'},
    'snapshot_files_before': 237,
    'snapshot_files_after': 237,
    'snapshot_bytes_before': 16072121,
    'snapshot_bytes_after': 16170283,
    'manifest_sha256_before':
        '6edcebc669e9b3de09856f353f6b1eafc22bff47a8dbfef3f35afdffacc1bfc0',
    'manifest_sha256_after':
        '2fdcfaec3ffd5f3ac5e991cb0da591df5dda57c3583bba4e431e7c098b4036b6',
    'pin_record': 'Private checkout root manifest, '
        'import_public_snapshot EXPECTED pins and both coverage '
        'files were regenerated by the private tooling (verify '
        'green); the sealed change was staged as a snapshot and '
        'delivered with this batch; the live snapshot and cicd pin '
        'swap is performed by the parent before merge.',
    'verdict_surface_change': 'The ren-pattern block flips only '
        'its registration disclosure fields (evidence_binding, the '
        'D4 adjudication note landing-form sentence and the '
        'registration-status scope limit) and gains its registered '
        'trace step, RuleMatch entry and Evidence chain; the '
        'determination semantics are byte-identical (three-state '
        'true_false, never a false-pattern label, '
        'success_failure/purity/useful_god None + unreviewed, D1/D2 '
        'adjudications and the Slice A route precedence '
        'unchanged). Whole-envelope equivalence across the '
        'comparison sets and the rollback drill are recorded in '
        'the governance document.',
}


GOVERNANCE_DAYUN_SANMING_RECORD = {
    'batch': '治理 pending 第三顺位 dayun 三命分段批',
    'event': 'E0346',
    'date': '2026-11-01',
    'document': 'docs/product/GOVERNANCE_DAYUN_SANMING_PROMOTION.md',
    'canonical_chapters_added': [
        'bazi.chapter.sanming_lun_dayun',
        'bazi.chapter.sanming_luoluozi_dayun_witness'],
    'canonical_sections_added': [
        'bazi.section.s068', 'bazi.section.s069', 'bazi.section.s070'],
    'canonical_terms_added': [
        'bazi.term.dayun_direction', 'bazi.term.dayun_handover'],
    'phase1_rules_added': ['bazi.rule.r038', 'bazi.rule.r039'],
    'phase2_rules_added': [
        'bazi.phase2.dayun_classical_direction',
        'bazi.phase2.dayun_sanming_conversion'],
    'golden_cases_added': [
        'bazi.dayun-sanming-q1-1958-forward-male',
        'bazi.dayun-sanming-q2-1949-backward-female',
        'bazi.dayun-sanming-q3-1959-forward-female',
        'bazi.dayun-sanming-q4-1959-backward-male',
        'bazi.dayun-sanming-adv001-zero-jie-2000',
        'bazi.dayun-sanming-direction-only-1959-male'],
    'source_refs_subset': [
        'direction_rule (bazi.section.s068, classical)',
        'vol11_direction_witness (bazi.section.s069, classical)',
        'ratio_statement (bazi.section.s068, classical)',
        'ratio_derivation (bazi.section.s068, classical)',
        'worked_example (bazi.section.s068, classical)',
        'anti_rounding (bazi.section.s068, classical)',
        'zero_borrow_definition (bazi.section.s068, classical)',
        'zero_borrow_example (bazi.section.s068, classical)',
        'handover_decade (bazi.section.s068, classical)',
        'handover_approx (bazi.section.s068, classical)'],
    'source_refs_subset_basis': '规则 r038 的 source_refs 恰为方向'
        'Variant 实际编码消费的 2 条引文（direction_rule 为唯一 '
        'encoded_rule，vol11_direction_witness 为其卷十一见证）；'
        'r039 的 source_refs 恰为三命换算实际消费的 8 条引文'
        '（比率命题/推导、原文例算、反约法、零借定义/例、十年递换'
        '句、生刻不明近似句，其中 handover_decade 以 S3 应用形绑'
        '定）。未入 refs 者各有明示地位：神峰 6 条引文是方向 '
        'Variant 的 corroboration 披露而非三命裁定依据（沿 r035 '
        '先例「只绑实际消费的裁定依据」与 E0342 例证不作规则引文'
        '先例，且神峰段本身维持 pending、无 Canonical 节可绑）；'
        'worked_example_check、handover_example、vol11_ratio_'
        'witness、vol11_counting_divergence 与方向见证二为登记证'
        '据（evidence-only），由阶段一校勘册'
        '（sanming-juan2-dayun-collation-register-v1）承载；闰月子'
        '句排除段整段排除不变。',
    'segmented_registration': 'dayun-classical-variants 行翻转 '
        'registered 的分段口径：主 phase1_rule_id/phase2_rule_id '
        '记方向段（r038 / dayun_classical_direction），三命换算段'
        '以 additional_phase1_rule_ids/additional_phase2_rule_ids '
        '补记（r039 / dayun_sanming_conversion），行内 segments 明'
        '细逐段标示（三命段 registered、神峰段 maintained_pending '
        '并逐字在册）。S5 治理不变量（records 的 rules_added 并集'
        '与 registered 行的 rule id 集合恰等）的收集表达式同步扩'
        '展为并入 additional_* 字段——结构扩展、恰等不变量保留。'
        'dayun-compose / dayun-timeline-view 两行保持 '
        'maintained_pending（inherited_pending）：其继承的三命分'
        '段已注册、神峰分段仍 pending，两行 evidence_binding 改'
        '记 segmented_inherited_pending，治理维持名单 6 -> 5。',
    'harness_contract_extension': 'golden harness 契约扩展与 '
        'E0344 同形且更小：golden.py / validate_phase2.py / '
        'golden schema 零改动，provider 三重钉死逐字不变；扩展只'
        '落在 provider 签名（chart 新增门控 kwargs '
        'dayun_classical_role / dayun_sanming_measurement，默认 '
        'None/None 时封套逐字不变）与用例 input 增带该两字段。扩'
        '展理由：chart 不携带出生瞬时，性别角色与 TJ-015 节距测'
        '量恒为显式输入声明（与 ren_yin_pilot_result 同口径），'
        '测量另经 sanming_convert_measurement 内的 provider 重放'
        '校验与 chart 的月柱/方向交叉核对。旧契约行为不变由专项'
        '测试钉住（无参数时无 dayun_classical 键、无新步；engine '
        '门禁与参数类型/交叉核对拒绝均有公开测试）。',
    'registration_flip': 'dayun-classical-variants (Sanming '
        'segment only): maintained_pending / '
        'canonical_evidence_absent -> registered (Phase1 '
        'bazi.rule.r038 + bazi.rule.r039, Phase2 '
        'bazi.phase2.dayun_classical_direction + '
        'bazi.phase2.dayun_sanming_conversion validated, 6 Golden '
        'cases fire the steps); the Shenfeng segment stays '
        'maintained_pending inside the same row (segments detail '
        'on the row); maintained inventory 6 -> 5 (the two '
        'inherited rows remain, reworded). Publication condition '
        'five (deployment acceptance binding) stays pending the '
        'E0347 closeout, as with every prior flip.',
    'sealed_files_changed': [
        'data/canonical/bazi/phase1_knowledge.json',
        'data/canonical/bazi/phase2_execution.json',
        'data/canonical/bazi/phase2_golden.json',
        'data/coverage/phase1.json',
        'data/product/knowledge_coverage.json'],
    'sealed_file_sha256_after': {
        'data/canonical/bazi/phase1_knowledge.json':
            '09208b963ff527e4aa0255e2e48e90e4fb49cfcd685b6cfd28c4ced5e1fd9f3d',
        'data/canonical/bazi/phase2_execution.json':
            'cab21f4d41a4b76c2d4f061fd791e409eb81d95967cfc6f79ec29044c0b426f6',
        'data/canonical/bazi/phase2_golden.json':
            'bd750ba860a5e4651b38809258226fa2a43acb8ea295871db00e452573551c31',
        'data/coverage/phase1.json':
            '13e75db1102f84fa212988a27fdad43d15bf29133b83c2d1829cc3512fc7b87d',
        'data/product/knowledge_coverage.json':
            'a60343d43d5f2e62bbbc37bb3f12f1b2b6f4d06fc15198a537864ef5c092492d'},
    'snapshot_files_before': 237,
    'snapshot_files_after': 237,
    'snapshot_bytes_before': 16170283,
    'snapshot_bytes_after': 16221036,
    'manifest_sha256_before':
        '2fdcfaec3ffd5f3ac5e991cb0da591df5dda57c3583bba4e431e7c098b4036b6',
    'manifest_sha256_after':
        '97e211c4582f7cf4d890c2bf8071573fbaced193d740c185d2c891a3f2e51324',
    'pin_record': 'Private checkout root manifest, '
        'import_public_snapshot EXPECTED pins and both coverage '
        'files were regenerated by the private tooling (verify '
        'green); the sealed change was staged as a snapshot and '
        'delivered with this batch; the live snapshot and cicd pin '
        'swap is performed by the parent before merge.',
    'verdict_surface_change': 'No verdict surface changes: the '
        'dayun outputs keep their contract byte-identical apart '
        'from the closed-list registration disclosures '
        '(evidence_binding values per segment, LIMITATIONS '
        'registration sentences, quote source_id re-pointing to '
        'the applied-text source with source_section_id added, '
        'the new gated chart blocks with their registered trace '
        'steps / RuleMatch / Evidence entries, and the compose / '
        'view binding re-marking). Intervals only, no point '
        'fields, no age keys, the zero-jie refusal unchanged, '
        'ADV-001..012 behaviour unchanged, the research view '
        'stays off public pages, and user-visible capability is '
        'unchanged.',
}


GOVERNANCE_SHENFENG_RECORD = {
    'batch': '治理 pending 神峰经典 Canonical 扩编批（一次扩编同时'
             '服务 bingyao-shenfeng-v1 与 dayun 神峰分段）',
    'event': 'E0348',
    'date': '2026-11-01',
    'document': 'docs/product/GOVERNANCE_SHENFENG_EXPANSION.md',
    'canonical_classics_added': ['bazi.classic.shenfeng'],
    'canonical_chapters_added': [
        'bazi.chapter.shenfeng_bingyao',
        'bazi.chapter.shenfeng_zhengguan',
        'bazi.chapter.shenfeng_qi_dayun_fa',
        'bazi.chapter.ditiansui_zhonghe'],
    'canonical_sections_added': [
        'bazi.section.s071', 'bazi.section.s072',
        'bazi.section.s073', 'bazi.section.s074'],
    'canonical_terms_added': [
        'bazi.term.bingyao', 'bazi.term.dayun_shenfeng_conversion'],
    'phase1_rules_added': ['bazi.rule.r040', 'bazi.rule.r041'],
    'phase2_rules_added': [
        'bazi.phase2.bingyao_assessment',
        'bazi.phase2.dayun_shenfeng_conversion'],
    'golden_cases_added': [
        'bazi.bingyao-wealth-disease-medicine',
        'bazi.bingyao-wealth-disease-no-medicine',
        'bazi.bingyao-medicine-without-disease',
        'bazi.bingyao-peer-class-boundary-jiecai',
        'bazi.bingyao-foodwound-disease-medicine',
        'bazi.bingyao-dual-pair-wealth-only',
        'bazi.dayun-shenfeng-q1-1958-forward-male',
        'bazi.dayun-shenfeng-q2-1949-backward-female',
        'bazi.dayun-shenfeng-q3-1959-forward-female',
        'bazi.dayun-shenfeng-q4-1959-backward-male',
        'bazi.dayun-shenfeng-adv001-zero-jie-2000'],
    'source_refs_subset': [
        'disease_definition (bazi.section.s071, classical)',
        'medicine_definition (bazi.section.s071, classical)',
        'wealth_pair (bazi.section.s071, classical)',
        'food_pair (bazi.section.s071, classical)',
        'sf_ex1 (bazi.section.s073, classical)',
        'sf_ex3 (bazi.section.s073, classical)',
        'sf_ex4 (bazi.section.s073, classical)'],
    'source_refs_subset_basis': '规则 r040 的 source_refs 恰为病药 '
        'Variant 实际编码消费的 4 条引文（病/药定义句 + 两条编码对'
        '句，与 r037「定义+程序句」及 r036「只绑裁定依据」先例同'
        '形）；r041 的 source_refs 恰为神峰换算 Variant 实际消费'
        '的 3 条例算引文（sf_ex1/sf_ex3/sf_ex4，即 '
        'shenfeng_convert_days converted 输出的 evidence_quotes '
        '全集）。未入 refs 者各有明示地位：神峰 earth_example / '
        'procedure_zhong / no_disease_clause 为登记引文（入 s071 '
        '节文本、公开登记补 section_id、不入 refs，沿 E0342 例证'
        '不作规则引文先例——其中 procedure_zhong 经 S4 审定明示'
        '不消费）；zhengguan_tension 为登记张力引文（窗口节 s072 '
        '承载，Variant 明示不覆盖）；ditiansui_counterweight 为 '
        'limitations 制衡证据（滴天髓既有经典内补窗口节 s074 承'
        '载、不入 refs，沿 E0346 §2.3 旁证不入 refs 审定）；神峰 '
        'sf_heading_yang / sf_heading_yin / sf_ex2 是方向产出中的 '
        'corroboration 披露（sf_ex2 日数段经 EXCLUDED_SPANS 登记'
        '禁用），不入任何规则 refs。',
    'new_classic_design': '新经典 bazi.classic.shenfeng 逐项镜像既'
        '有四经典实测结构（id/domain/name/source_id/body_stage 五'
        '字段，body_stage=quarantine 与三命/协纪同例：其 Canonical '
        '在场形态为隔离快照原文的节级切片、无独立清洗定本）；章'
        '节/节/术语/规则实体字段、review 三字段（status=approved / '
        'method / scope）与 locator 口径均沿既有实体实测形态，不新'
        '造任何机制。建节四处不多建：s071 病药定义节（快照字符 '
        '[7019,7680) 整段 661 字、PUA/□ 均 0）、s072 正官格张力窗'
        '口（[10010,10041) 恰为张力引文本身 31 字，沿 s070 恰幅先'
        '例）、s073《起大运法》整节（[85001,85246) 245 字、PUA/□ '
        '均 0）、s074 滴天髓中和篇制衡窗口（[43767,43825) 恰为制'
        '衡引文本身 58 字，建于既有滴天髓经典内）。',
    'harness_contract_extension': 'golden harness 契约扩展与 '
        'E0344/E0346 同形：golden.py / validate_phase2.py / '
        'golden schema 零改动，provider 三重钉死逐字不变；扩展只'
        '落在 provider 签名（chart 新增门控 kwargs '
        'dayun_shenfeng_measurement，默认 None 时封套逐字不变；'
        'bingyao 步沿既有 bingyao_variant 门控）与用例 input 增带'
        '该字段。bingyao 步由 chart 在 assessment 计算后以 '
        'trace.add 接入（与 ren 先例同形：步输出由已执行步计算得'
        '出后登记），assessment 块除注册披露外逐字不变。',
    'inherited_rows_terminal_form': 'dayun-compose / '
        'dayun-timeline-view 两 inherited 行的终局形态（本批审'
        '定）：两行自身无规则可登记，disposition 不得改记 '
        'registered（治理不变量要求 registered 行携带自有 '
        'phase1/phase2 规则 id，且 records rules_added 并集与 '
        'registered 行规则 id 恰等——复用底层 id 将使恰等不变量'
        '重复计数而断裂，新造 id 即空注册，两者均禁止）；两行维'
        '持 maintained_pending / inherited_pending，其继承链已随'
        '神峰分段注册终局解除，两模块 evidence_binding 改记终局'
        '形态 inherited_registered_phase1_phase2（底层全段已注'
        '册、本层只继承披露），unlock_path 改记为仅余「本层将来'
        '产生独立规则时另行注册」的条件路径。治理维持名单实测 '
        '5 -> 4（bingyao 翻转 -1；两 inherited 行以终局形态留在'
        '名单内——任务书「预期 5->3」预设两 inherited 行退出名'
        '单，与上述不变量冲突，以代码实测为准，审定全文见治理文'
        '档 §2.5）。',
    'registration_flip': 'bingyao-shenfeng-v1: '
        'maintained_pending / canonical_evidence_absent -> '
        'registered (Phase1 bazi.rule.r040, Phase2 '
        'bazi.phase2.bingyao_assessment validated, 6 Golden cases '
        'fire the step); dayun-classical-variants Shenfeng segment: '
        'maintained_pending -> registered inside the same row '
        '(additional ids gain bazi.rule.r041 / '
        'bazi.phase2.dayun_shenfeng_conversion, 5 Golden cases '
        'fire the step), so the row is fully registered across '
        'both segments; maintained inventory 5 -> 4 (the two '
        'inherited rows remain in terminal inherited form). '
        'Publication condition five (deployment acceptance '
        'binding) stays pending the E0349 closeout, as with every '
        'prior flip.',
    'sealed_files_changed': [
        'data/canonical/bazi/phase1_knowledge.json',
        'data/canonical/bazi/phase2_execution.json',
        'data/canonical/bazi/phase2_golden.json',
        'data/coverage/phase1.json',
        'data/product/knowledge_coverage.json'],
    'sealed_file_sha256_after': {
        'data/canonical/bazi/phase1_knowledge.json':
            'de79653afb384d8c0275a8cf2caff3ab4170c4a200acfd7b03afde02a63ba198',
        'data/canonical/bazi/phase2_execution.json':
            '2163c6cf9495ad8dd6e171f6083d66bc02bd2ee881e46c18b721c6cb0f56c98e',
        'data/canonical/bazi/phase2_golden.json':
            'bbffab397f976bd5430c257c327fa12e3248e2c5484a1ec64e2b4a6e011c6171',
        'data/coverage/phase1.json':
            'dd546d0d426242daace7816327d6d7da9d46ec80b4a639fa370655de4b1f021b',
        'data/product/knowledge_coverage.json':
            'd45b876c3cceae73eb37ec3ed26cde76353c856ba8c3d538bd2da43052cf43fc'},
    'snapshot_files_before': 237,
    'snapshot_files_after': 237,
    'snapshot_bytes_before': 16221036,
    'snapshot_bytes_after': 16272294,
    'manifest_sha256_before':
        '97e211c4582f7cf4d890c2bf8071573fbaced193d740c185d2c891a3f2e51324',
    'manifest_sha256_after':
        '380bb73e34babc30bcc80e5ad7f296175f6be206af6a77f1abb4a07b94da654b',
    'pin_record': 'Private checkout root manifest, '
        'import_public_snapshot EXPECTED pins and both coverage '
        'files were regenerated by the private tooling (verify '
        'green); the sealed change was staged as a snapshot and '
        'delivered with this batch; the live snapshot and cicd pin '
        'swap is performed by the parent before merge.',
    'verdict_surface_change': 'No verdict surface changes: '
        'bingyao determination stays None, no 「无病」 output '
        'exists, the dual-pair structure is unchanged; the dayun '
        'output contract is byte-identical apart from the '
        'closed-list registration disclosures (evidence_binding '
        'values, quote source_section_id additions, LIMITATIONS / '
        'production_scope registration sentences, the new gated '
        'chart block with its registered trace step / RuleMatch / '
        'Evidence entries, and the compose / view terminal '
        'inherited binding). Intervals only, no point fields, no '
        'age keys, the zero-jie refusal unchanged, ADV-001..012 '
        'behaviour unchanged, the research view stays off public '
        'pages, and user-visible capability is unchanged.',
}


# tiaohou-qiongtong-v1 Canonical design ADJUDICATION record
# (E0350). DESIGN ONLY: nothing in this record creates an entity,
# binds a rule or flips a registration. The tiaohou-qiongtong-v1
# inventory row stays maintained_pending /
# canonical_evidence_absent; the planned-id fields below name the
# design-final designations from
# docs/product/TIAOHOU_CANONICAL_DESIGN.md (D-T1..D-T6) and assert
# nothing about the sealed bundle. The record lives in this
# governance module (the GOVERNANCE_*_RECORD form used since
# E0333) rather than a standalone register module: the TJ-018.3
# registers are machine-consumed pipeline pins, while this design
# is consumed by governance tests and the implementation batch's
# brief, and batch-record consistency governs.
TIAOHOU_DESIGN_RECORD = {
    'batch': 'tiaohou canonical design adjudication',
    'event': 'E0350',
    'date': '2026-11-01',
    'document': 'docs/product/TIAOHOU_CANONICAL_DESIGN.md',
    'variant': 'tiaohou-qiongtong-v1',
    'implementation_status': 'design_only_not_implemented',
    'design_decisions': ['D-T1', 'D-T2', 'D-T3', 'D-T4',
                         'D-T5', 'D-T6'],
    'planned_source_id': 'bazi.source.qiongtong',
    'planned_classic_id': 'bazi.classic.qiongtong',
    'planned_classic_body_stage': 'quarantine',
    'planned_chapter_count': 11,
    'planned_first_chapter_id': 'bazi.chapter.qiongtong_zonglun',
    'planned_last_chapter_id': 'bazi.chapter.qiongtong_gui',
    'planned_section_count': 110,
    'planned_entry_section_count': 109,
    'planned_anchor_section_count': 1,
    'planned_first_section_id': 'bazi.section.s075',
    'planned_last_section_id': 'bazi.section.s184',
    'planned_term_id': 'bazi.term.tiaohou',
    'planned_phase1_rule_count': 10,
    'planned_first_phase1_rule_id': 'bazi.rule.r042',
    'planned_last_phase1_rule_id': 'bazi.rule.r051',
    'planned_phase1_refs_total': 120,
    'design_revision_event': 'E0351',
    'design_revision_date': '2026-11-01',
    'design_revision_document_section': '10',
    'planned_window_section_count': 1,
    'planned_window_sections': [
        {'entry': '丙×卯',
         'section_id': 'bazi.section.s099',
         'form': 'window',
         'entry_span': [8668, 9025],
         'window_span': [8668, 8852],
         'excluded_span': [8853, 9025],
         'hit_char': 8863,
         'hit_keyword': '化格'}],
    'measured_unconsumed_gap_chars': 4744,
    'measured_unconsumed_gap_chars_naive_sum': 4884,
    'planned_ding_branch_ref_binding': 'shared section of span '
        '(13476, 13592)',
    'implementation_event_planned': 'E0352',
    'closeout_event_planned': 'E0353',
    'planned_phase2_step_id': 'bazi.phase2.tiaohou_assessment',
    'planned_phase2_rule_ref_count': 10,
    'measured_entry_count': 119,
    'measured_distinct_span_count': 109,
    'measured_distinct_refs': 120,
    'measured_absent_grid': ['乙×丑'],
    'measured_encoded_branch_rules': 10,
    'golden_criteria_planned': ['G1', 'G2', 'G3', 'G4', 'G5',
                                'G6'],
    'maintenance_delta_planned': 'maintained 4 -> 3 on flip',
    'boundary':
        'Design and read-only tracing only. No Canonical entity '
        'was created, no rule or step was bound, no registration '
        'was flipped, bazi_tiaohou.py is byte-untouched (ENTRIES '
        'and the pending_phase1_rule_registration disclosure '
        'unchanged), and no sealed asset, snapshot or cicd pin '
        'changed. The design was revised once by E0351 (design '
        'document section 10, append-only): the 丙×卯 entry '
        'section is planned as a window section [8668, 8852) '
        'because its full entry span carries a 化格 '
        'case-discussion sentence at snapshot char 8863 that '
        'the sealed hehua section keyword invariant bars from '
        'every section text; the excluded remainder [8853, '
        '9025) is registered as unbuilt text, the refs '
        'exactness (120) is unchanged, and event numbers were '
        'reallocated centrally (implementation E0352, closeout '
        'E0353). Implementation waits for the separately '
        'dispatched E0352 batch; siling and the deferred U1/U3 '
        'decisions are untouched.',
}

GOVERNANCE_TIAOHOU_RECORD = {
    'batch': '治理 pending 末项 tiaohou 经典建制实施批',
    'event': 'E0352',
    'date': '2026-11-01',
    'document': 'docs/product/GOVERNANCE_TIAOHOU_PROMOTION.md',
    'canonical_classics_added': ['bazi.classic.qiongtong'],
    'canonical_chapters_added': [
        'bazi.chapter.qiongtong_zonglun',
        'bazi.chapter.qiongtong_jia',
        'bazi.chapter.qiongtong_yi',
        'bazi.chapter.qiongtong_bing',
        'bazi.chapter.qiongtong_ding',
        'bazi.chapter.qiongtong_wu',
        'bazi.chapter.qiongtong_ji',
        'bazi.chapter.qiongtong_geng',
        'bazi.chapter.qiongtong_xin',
        'bazi.chapter.qiongtong_ren',
        'bazi.chapter.qiongtong_gui'],
    'canonical_sections_added': [
        'bazi.section.s075',
        'bazi.section.s076',
        'bazi.section.s077',
        'bazi.section.s078',
        'bazi.section.s079',
        'bazi.section.s080',
        'bazi.section.s081',
        'bazi.section.s082',
        'bazi.section.s083',
        'bazi.section.s084',
        'bazi.section.s085',
        'bazi.section.s086',
        'bazi.section.s087',
        'bazi.section.s088',
        'bazi.section.s089',
        'bazi.section.s090',
        'bazi.section.s091',
        'bazi.section.s092',
        'bazi.section.s093',
        'bazi.section.s094',
        'bazi.section.s095',
        'bazi.section.s096',
        'bazi.section.s097',
        'bazi.section.s098',
        'bazi.section.s099',
        'bazi.section.s100',
        'bazi.section.s101',
        'bazi.section.s102',
        'bazi.section.s103',
        'bazi.section.s104',
        'bazi.section.s105',
        'bazi.section.s106',
        'bazi.section.s107',
        'bazi.section.s108',
        'bazi.section.s109',
        'bazi.section.s110',
        'bazi.section.s111',
        'bazi.section.s112',
        'bazi.section.s113',
        'bazi.section.s114',
        'bazi.section.s115',
        'bazi.section.s116',
        'bazi.section.s117',
        'bazi.section.s118',
        'bazi.section.s119',
        'bazi.section.s120',
        'bazi.section.s121',
        'bazi.section.s122',
        'bazi.section.s123',
        'bazi.section.s124',
        'bazi.section.s125',
        'bazi.section.s126',
        'bazi.section.s127',
        'bazi.section.s128',
        'bazi.section.s129',
        'bazi.section.s130',
        'bazi.section.s131',
        'bazi.section.s132',
        'bazi.section.s133',
        'bazi.section.s134',
        'bazi.section.s135',
        'bazi.section.s136',
        'bazi.section.s137',
        'bazi.section.s138',
        'bazi.section.s139',
        'bazi.section.s140',
        'bazi.section.s141',
        'bazi.section.s142',
        'bazi.section.s143',
        'bazi.section.s144',
        'bazi.section.s145',
        'bazi.section.s146',
        'bazi.section.s147',
        'bazi.section.s148',
        'bazi.section.s149',
        'bazi.section.s150',
        'bazi.section.s151',
        'bazi.section.s152',
        'bazi.section.s153',
        'bazi.section.s154',
        'bazi.section.s155',
        'bazi.section.s156',
        'bazi.section.s157',
        'bazi.section.s158',
        'bazi.section.s159',
        'bazi.section.s160',
        'bazi.section.s161',
        'bazi.section.s162',
        'bazi.section.s163',
        'bazi.section.s164',
        'bazi.section.s165',
        'bazi.section.s166',
        'bazi.section.s167',
        'bazi.section.s168',
        'bazi.section.s169',
        'bazi.section.s170',
        'bazi.section.s171',
        'bazi.section.s172',
        'bazi.section.s173',
        'bazi.section.s174',
        'bazi.section.s175',
        'bazi.section.s176',
        'bazi.section.s177',
        'bazi.section.s178',
        'bazi.section.s179',
        'bazi.section.s180',
        'bazi.section.s181',
        'bazi.section.s182',
        'bazi.section.s183',
        'bazi.section.s184'],
    'canonical_terms_added': ['bazi.term.tiaohou'],
    'phase1_rules_added': [
        'bazi.rule.r042',
        'bazi.rule.r043',
        'bazi.rule.r044',
        'bazi.rule.r045',
        'bazi.rule.r046',
        'bazi.rule.r047',
        'bazi.rule.r048',
        'bazi.rule.r049',
        'bazi.rule.r050',
        'bazi.rule.r051'],
    'phase2_rules_added': ['bazi.phase2.tiaohou_assessment'],
    'golden_cases_added': [
        'bazi.tiaohou-jia-wu-branch-applied',
        'bazi.tiaohou-jia-wu-branch-not-applied',
        'bazi.tiaohou-bing-mao-branch-applied',
        'bazi.tiaohou-bing-mao-branch-not-applied',
        'bazi.tiaohou-bing-chen-branch-applied',
        'bazi.tiaohou-bing-chen-branch-not-applied',
        'bazi.tiaohou-bing-si-branch-applied',
        'bazi.tiaohou-bing-si-branch-not-applied',
        'bazi.tiaohou-bing-you-branch-applied',
        'bazi.tiaohou-bing-you-branch-not-applied',
        'bazi.tiaohou-ding-shen-branch-applied',
        'bazi.tiaohou-ding-shen-branch-not-applied',
        'bazi.tiaohou-ding-you-branch-applied',
        'bazi.tiaohou-ding-you-branch-not-applied',
        'bazi.tiaohou-geng-mao-branch-applied',
        'bazi.tiaohou-geng-mao-branch-not-applied',
        'bazi.tiaohou-xin-wu-branch-applied',
        'bazi.tiaohou-xin-wu-branch-not-applied',
        'bazi.tiaohou-gui-si-branch-applied',
        'bazi.tiaohou-gui-si-branch-not-applied',
        'bazi.tiaohou-yi-chou-absent-in-source',
        'bazi.tiaohou-bing-hai-empty-sequence',
        'bazi.tiaohou-ding-wu-empty-sequence',
        'bazi.tiaohou-gui-wu-empty-sequence',
        'bazi.tiaohou-wu-yin-hit',
        'bazi.tiaohou-ji-hai-none',
        'bazi.tiaohou-ren-chen-hit',
        'bazi.tiaohou-wu-shared-11-12',
        'bazi.tiaohou-ji-shared-summer',
        'bazi.tiaohou-ji-shared-autumn'],
    'source_refs_subset': [
        '条目主引文去重 111 条 + 已编码分支引文去重 9 条 = 恰 120 条'
        '（逐干 甲13/乙11/丙16/丁13/戊10/己6/庚13/辛13/壬12/癸13）',
        '术语锚引文 1 条（总论气候生成句，快照 [33,98)，'
        'bazi.section.s075）'],
    'source_refs_subset_basis': 'D-T3 恰等口径：每干 refs 的'
        '（section_id, original_text）集合恰等于该干条目主引文对'
        '（按（节跨度，引文定位点）去重）与已编码分支引文对（按'
        '（引文，定位点）去重）的并集；§10.5(ii) 丁火合并 ref：'
        '丁×申与丁×酉同文同位点的分支引文合成 1 条并绑共享跨度'
        '之节，使（节，引文）对唯一；§10.2 丙×卯主/分支 2 条 refs '
        '改绑窗口节 s099；unencoded 24 条留在条目内只登记、'
        'related 17 条保持登记现状，均不入 refs；总论锚节 s075 '
        '不被任何规则 refs 消费（只作术语锚）。',
    'new_classic_design': 'docs/product/TIAOHOU_CANONICAL_DESIGN.md'
        '（E0350 定稿 D-T1…D-T6 + §10 设计修订 E0351，冲突处以 '
        '§10 为准）：底本为钉定快照逐字切片（C 级恒定）；经典 '
        'body_stage=quarantine 镜像神峰扩编形态；s099 窗口节为 '
        'D-T2 唯一例外形态。',
    'harness_contract_extension': 'none：golden.py / 执行/用例 '
        'schema / provider 三重钉死逐字不变，chart 签名零改动'
        '（tiaohou_variant 门控自 TJ-013.1 已存在）；步沿既有门控'
        '在 assessment 计算后以 trace.add 登记（与 ren/bingyao '
        '先例同形），与 D-T5 的零扩展裁定一致。',
    'registration_flip': 'tiaohou-qiongtong-v1: '
        'maintained_pending / canonical_evidence_absent -> '
        'registered (Phase1 bazi.rule.r042 + additional r043-r051, '
        'Phase2 bazi.phase2.tiaohou_assessment validated, 30 '
        'Golden cases G1-G6 fire the step); maintained inventory '
        '4 -> 3 (siling-yin-pilot and the two dayun inherited rows '
        'unchanged). Publication condition five (deployment '
        'acceptance binding) stays pending the E0353 closeout, as '
        'with every prior flip.',
    'sealed_files_changed': [
        'data/canonical/bazi/phase1_knowledge.json',
        'data/canonical/bazi/phase2_execution.json',
        'data/canonical/bazi/phase2_golden.json',
        'data/coverage/phase1.json',
        'data/product/knowledge_coverage.json'],
    'sealed_file_sha256_after': {
        'data/canonical/bazi/phase1_knowledge.json':
            '942caeefbf249428d07b4ffc868b0e663c955fde0089995a836ad5586efac091',
        'data/canonical/bazi/phase2_execution.json':
            'ad7a4f17d6dae6c69899a9c2785dfee46a49e38b3d50097c7c634d567fd5c1e8',
        'data/canonical/bazi/phase2_golden.json':
            '7e15dbc6e37860fdbcff225283022d75cf393646906d3c67dc8660ff3c1944b0',
        'data/coverage/phase1.json':
            '7c1c3493a04b07cbbda16c0e0417fcaeac348a8c19b3e21184c2ccbc4b81de18',
        'data/product/knowledge_coverage.json':
            'd13dcbe1e93932da4b01ccfe3c97017a3b00419fdae1f31a5d7e9a062eb55185'},
    'snapshot_files_before': 237,
    'snapshot_files_after': 237,
    'snapshot_bytes_before': 16272294,
    'snapshot_bytes_after': 16722816,
    'manifest_sha256_before':
        '380bb73e34babc30bcc80e5ad7f296175f6be206af6a77f1abb4a07b94da654b',
    'manifest_sha256_after':
        '26b63e64bed736b08a7dcd686f6a75de733fd44ba9eec9195248e69730485329',
    'pin_record': 'Private checkout root manifest, '
        'import_public_snapshot EXPECTED pins and both coverage '
        'files were regenerated by the private tooling (verify '
        'green); the sealed change was staged as a snapshot and '
        'delivered with this batch; the live snapshot and cicd pin '
        'swap is performed by the parent before merge.',
    'verdict_surface_change': 'No verdict surface changes: the '
        'tiaohou lookup has no verdict fields and gains none; '
        'ENTRIES data, lookup semantics and every computed value '
        'are byte-identical apart from the closed-list registration '
        'disclosures (evidence_binding values, entry '
        'source_section_id additions, LIMITATIONS / docstring '
        'registration sentences, and the new step trace / '
        'RuleMatch / Evidence increments under the existing '
        'tiaohou_variant gate). The public projection continues '
        'to strip the whole tiaohou_assessment block; '
        'research_only / public_enabled / ai_enabled flags are '
        'unchanged.',
}

REASON_CLASSES = {
    'canonical_evidence_absent':
        '定义性原典锚点在密封 Canonical 中无对应 section（或经典不在 '
        'Canonical 内），Phase1 source_refs 无从逐字验证。',
    'execution_binding_structure':
        '产出不经 ExecutionTrace 执行绑定，注册将成为无执行步的空注册。',
    'inherited_pending':
        '组合/视图层，继承底层 Variant 的 pending 状态，无独立规则。',
}

REGISTRATION_INVENTORY = [
    {
        'item': 'tiaohou-qiongtong-v1',
        'subject': '调候 Variant（穷通宝鉴 119 条）',
        'disclosure_sites': ['src/tianji_kb/bazi_tiaohou.py'],
        'disposition': 'registered',
        'phase1_rule_id': 'bazi.rule.r042',
        'additional_phase1_rule_ids': [
            'bazi.rule.r043', 'bazi.rule.r044', 'bazi.rule.r045',
            'bazi.rule.r046', 'bazi.rule.r047', 'bazi.rule.r048',
            'bazi.rule.r049', 'bazi.rule.r050', 'bazi.rule.r051'],
        'phase2_rule_id': 'bazi.phase2.tiaohou_assessment',
        'reason': '《穷通宝鉴》已建为 Canonical 第六典 '
                  'bazi.classic.qiongtong（body_stage=quarantine；11 章、'
                  '110 节：总论锚节 bazi.section.s075 与条目节 s076–s184 按条目跨度'
                  '升序建节，丙火二月条取窗口 [8668,8852) 建节 bazi.section.s099、'
                  '尾段含未裁合化命题登记未建节），术语 '
                  'bazi.term.tiaohou 锚总论气候生成句；查表按干注册为 '
                  'Phase1 规则 r042–r051，source_refs 恰为条目主引文'
                  '（去重 111 条）与已编码分支引文（去重 9 条）的并集、'
                  '合计恰 120 条（逐干 甲13/乙11/丙16/丁13/戊10/己6/'
                  '庚13/辛13/壬12/癸13；丁火共享分支引文合并为一条并'
                  '绑共享节），unencoded 24 条与 related 17 条只登记'
                  '不入 refs；Phase2 步 bazi.phase2.tiaohou_assessment '
                  'validated，30 例 Golden（G1–G6）真实 fire。设计='
                  'docs/product/TIAOHOU_CANONICAL_DESIGN.md（E0350 '
                  '定稿 + §10 修订 E0351），实施记录见 '
                  'GOVERNANCE_TIAOHOU_RECORD。',
        'unlock_path': None,
    },
    {
        'item': 'pure_generating_support',
        'subject': '旺衰谓词 木×亥 印比生扶（从旺口径）',
        'disclosure_sites': ['src/tianji_kb/bazi_adjudication.py'],
        'disposition': 'registered',
        'phase1_rule_id': 'bazi.rule.r029',
        'phase2_rule_id': 'bazi.phase2.strength_pure_generating_support',
        'reason': '定义锚点（从旺定义 s047、长生禄旺根示例 s026、本气 '
                  's034/s035、藏遁歌 s004 等）全部在 Canonical 内且与 '
                  'r024 引用集同构；谓词经 ExecutionTrace 执行，注册步'
                  '可真实绑定证据。',
        'unlock_path': None,
    },
    {
        'item': 'commanding_visible_support',
        'subject': '旺衰谓词 丙×午 当令显纯生扶（从强主锚）',
        'disclosure_sites': ['src/tianji_kb/bazi_adjudication.py',
                             'src/tianji_kb/bazi_fire_morphology.py'],
        'disposition': 'registered',
        'phase1_rule_id': 'bazi.rule.r030',
        'phase2_rule_id': 'bazi.phase2.strength_commanding_visible_support',
        'reason': '定义锚点（从强 s048、从旺 s047、比肩/余气 s025/s041、'
                  '长生禄旺例 s026、本气 s034/s035、藏遁歌 s004）在 '
                  'Canonical 内；登记中三条引文（孤立定义、根重轻句、'
                  '墓句）不在 Canonical，规则未引用之，其操作内容由 '
                  's026 长生禄旺例与因子规则 r018/r022 承载，与 r024 '
                  '只引用 Canonical 子集的先例一致。谓词经 '
                  'ExecutionTrace 执行，注册步可真实绑定证据。',
        'unlock_path': None,
    },
    {
        'item': 'lu_visible_support',
        'subject': '旺衰谓词 丙×巳 禄月显纯生扶',
        'disclosure_sites': ['src/tianji_kb/bazi_adjudication.py',
                             'src/tianji_kb/bazi_fire_si_yin_morphology.py'],
        'disposition': 'registered',
        'phase1_rule_id': 'bazi.rule.r032',
        'phase2_rule_id': 'bazi.phase2.strength_lu_visible_support',
        'reason': '定义锚点经 TJ-018.3 P2 审定（E0331）与批二'
                  '（E0335）落实：三命卷二《论天干阴阳生死》整节建成 '
                  'Canonical section bazi.section.s061（正式应用'
                  '工作本 S3 切片、零 PUA），丙禄主锚 sm2.bing_lu、'
                  '括注临官归禄段与丙长生句逐字绑定；滴天髓侧定义锚'
                  '（从强 s048、从旺 s047、长生禄旺根框架 s026、'
                  '藏遁歌 s004）在 Canonical 内且与 r030 引用集'
                  '同构；「丙禄居巳」单点互证未入 Canonical、未作'
                  '绑定（与 r024/r030 只引用 Canonical 子集的先例'
                  '一致；卷三禄节为格局路线前置、非本谓词定义锚，'
                  'P2 审定在册）。谓词经 ExecutionTrace 执行，'
                  '注册步可真实绑定证据，Golden 正例（1927-05-12）'
                  '真实 fire。',
        'unlock_path': None,
    },
    {
        'item': 'pure_support_metal',
        'subject': '旺衰谓词 金×酉 纯生扶',
        'disclosure_sites': ['src/tianji_kb/bazi_adjudication.py'],
        'disposition': 'registered',
        'phase1_rule_id': 'bazi.rule.r033',
        'phase2_rule_id': 'bazi.phase2.strength_pure_support_metal',
        'reason': '定义锚点经 P2 审定（E0331）与批二（E0335）落实：'
                  '三命卷二两节建成 Canonical sections bazi.section.'
                  's061/s062，庚/辛逐干生死禄句、十二宫次序'
                  '（sm2.gong_sequence）与藏遁歌酉宫句逐字绑定；'
                  '庚帝旺酉为 framework_derived 推步位（长生明句＋'
                  '十二宫次序＋阳干顺行，注册措辞与等级标注在册），'
                  '辛禄酉为 per_stem_listed；辛长生三格 conflict 随'
                  's061 元数据逐字携带、谓词阻断不变。谓词经 '
                  'ExecutionTrace 执行，注册步可真实绑定证据；该'
                  '谓词八条件在真实历法命盘上构造性不可满足（三'
                  '通道证明在册），其 Phase2 步 validation_status '
                  '保持 pending、golden_case_ids 指向负例见证集'
                  '（E0335 父级审定定稿），不声称真实盘正例 fire。'
                  'E0355 土根消费接入：本谓词 all_visible_have_'
                  'registered_roots 条件内的 registered_eligible '
                  '已按 E0257 契约格级白名单接入土根两格（戊×巳、'
                  '己×午），待定八格恒阻断、未分级八格不计资格；'
                  '本谓词在真实盘的不可满足结论改由藏干唯一支与'
                  '全酉显干干对两条历法通道独立承担（土印根位通'
                  '道退役），Phase2 步 validation_status 与负例见'
                  '证集不变。',
        'unlock_path': None,
    },
    {
        'item': 'pure_generating_support_water',
        'subject': '旺衰谓词 水×子 纯生扶',
        'disclosure_sites': ['src/tianji_kb/bazi_adjudication.py'],
        'disposition': 'registered',
        'phase1_rule_id': 'bazi.rule.r034',
        'phase2_rule_id': 'bazi.phase2.strength_pure_generating_support_water',
        'reason': '定义锚点经 P2 审定（E0331）与批二（E0335）落实：'
                  '三命卷二两节建成 Canonical sections bazi.section.'
                  's061/s062，壬/癸逐干生死禄句、十二宫次序与藏遁歌'
                  '子宫句逐字绑定；癸禄子为 per_stem_listed，真实盘'
                  '正例（1981-12-21）经注册步真实 fire；壬帝旺子为 '
                  'framework_derived 推步位（长生明句＋十二宫次序＋'
                  '阳干顺行），壬侧真实命盘构造性不可满足（证明在'
                  '册）、不声称正例；癸长生三格 conflict 随 s061 '
                  '元数据逐字携带、谓词阻断不变。谓词经 '
                  'ExecutionTrace 执行，注册步可真实绑定证据。',
        'unlock_path': None,
    },
    {
        'item': 'dayun-classical-variants',
        'subject': '大运古典三 Variant（direction-classical / '
                   'conversion-sanming / conversion-shenfeng）',
        'disclosure_sites': ['src/tianji_kb/bazi_dayun_classical.py'],
        'disposition': 'registered',
        'phase1_rule_id': 'bazi.rule.r038',
        'phase2_rule_id': 'bazi.phase2.dayun_classical_direction',
        'additional_phase1_rule_ids': ['bazi.rule.r039',
                                       'bazi.rule.r041'],
        'additional_phase2_rule_ids': [
            'bazi.phase2.dayun_sanming_conversion',
            'bazi.phase2.dayun_shenfeng_conversion'],
        'segments': {
            'sanming': 'registered（E0346：方向 bazi.rule.r038 / '
                       'bazi.phase2.dayun_classical_direction；三命'
                       '换算 bazi.rule.r039 / '
                       'bazi.phase2.dayun_sanming_conversion）',
            'shenfeng': 'registered（E0348：神峰换算 '
                        'bazi.rule.r041 / '
                        'bazi.phase2.dayun_shenfeng_conversion；'
                        'Canonical 新经典 bazi.classic.shenfeng '
                        '节 bazi.section.s073《起大运法》）',
        },
        'reason': '分段注册（E0346）：三命分段的定义性文本已经阶段一 '
                  '018 形制校勘登记（sanming-juan2-dayun-collation-'
                  'register-v1：S3 切片坐标、节内校勘条目逐处入册、'
                  '15 条引文逐条在定位点复现）并建成 Canonical '
                  'sections bazi.section.s068（卷二《论大运》S3 切'
                  '片 741 字、PUA/□ 归零、残余防 1 处不在任何引文'
                  '内随节元数据携带）、bazi.section.s069（卷十一见证'
                  '窗口 A）、bazi.section.s070（窗口 B 引文恰幅）；'
                  '新术语 '
                  'bazi.term.dayun_direction / bazi.term.dayun_'
                  'handover、Phase1 规则 bazi.rule.r038（方向，引文'
                  '恰 2 条）与 bazi.rule.r039（三命换算，引文恰 8 条，'
                  'handover_decade '
                  '以 S3 应用形绑定）逐字绑定应用文本来源；方向与'
                  '三命换算经 operations/bazi_chart 研究门控'
                  '（dayun_classical_role / dayun_sanming_'
                  'measurement 显式输入声明）真实执行并接入 '
                  'ExecutionTrace 注册步，Golden 真实盘/真实时刻用'
                  '例真实 fire。E0348 神峰分段注册：密封 Canonical '
                  '新建《神峰通考》经典（bazi.classic.shenfeng），'
                  '《起大运法》整节建成 bazi.section.s073（快照字'
                  '符 [85001,85246) 245 字、PUA/□ 均 0），新术语 '
                  'bazi.term.dayun_shenfeng_conversion、Phase1 规'
                  '则 bazi.rule.r041（source_refs 恰为神峰换算实'
                  '际消费的 3 条例算引文 sf_ex1/sf_ex3/sf_ex4）与 '
                  'Phase2 步 bazi.phase2.dayun_shenfeng_conversion '
                  '（validated）；神峰 6 条引文补 '
                  'source_section_id=s073（source 不改指——神峰无 '
                  'S0/S3 双轨，隔离快照即登记原文），新增测量级入'
                  '口 shenfeng_convert_measurement 经 bazi_chart '
                  '研究门控（dayun_shenfeng_measurement）真实执行'
                  '并接入 ExecutionTrace 注册步，Golden 5 例真实 '
                  'fire。方向产出中的神峰 6 条仍只是 corroboration '
                  '旁证披露（不入 r038 refs，E0346 §2.3 审定不'
                  '变）；至此本行两分段全部 registered。',
        'unlock_path': None,
    },
    {
        'item': 'dayun-compose',
        'subject': '大运组合入口 classical_dayun_timeline',
        'disclosure_sites': ['src/tianji_kb/bazi_dayun_compose.py'],
        'disposition': 'maintained_pending',
        'reason_class': 'inherited_pending',
        'reason': '组合层不产生独立规则（无自有规则可登记，不得改记 '
                  'registered——治理恰等不变量禁止复用底层规则 id、'
                  '新造 id 即空注册）：其所串联的两分段均已注册（三'
                  '命分段随 E0346、神峰分段随 E0348），继承链终局解'
                  '除，组合层 evidence_binding 改记终局形态 '
                  'inherited_registered_phase1_phase2（底层全段已'
                  '注册、本层只继承披露）。本行以 inherited 终局形'
                  '态留在治理维持名单（E0348 审定，见 '
                  'GOVERNANCE_SHENFENG_RECORD 的 '
                  'inherited_rows_terminal_form 与治理文档 §2.5）。',
        'unlock_path': '继承性 pending 已随神峰分段注册（E0348）终局'
                       '解除为 inherited 记法；仅当本层将来产生独立 '
                       'Phase1/Phase2 规则时，另行独立注册。',
    },
    {
        'item': 'dayun-timeline-view',
        'subject': '大运研究层视图 dayun-timeline-view-v1',
        'disclosure_sites': ['src/tianji_kb/bazi_dayun_timeline_view.py'],
        'disposition': 'maintained_pending',
        'reason_class': 'inherited_pending',
        'reason': '视图层 Variant，只呈现底层区间产出，本身不产生裁'
                  '决、无自有规则可登记：其所继承的两分段均已注册'
                  '（三命分段随 E0346、神峰分段随 E0348），继承链终'
                  '局解除，视图 evidence_binding 改记终局形态 '
                  'inherited_registered_phase1_phase2；公开开放仍须'
                  '分阶段开放另行裁定，不随注册自动开放。本行以 '
                  'inherited 终局形态留在治理维持名单（E0348 审定'
                  '同 dayun-compose 行）。',
        'unlock_path': '继承性 pending 已随神峰分段注册（E0348）终局'
                       '解除为 inherited 记法（公开开放另行裁定）；仅'
                       '当本层将来产生独立规则时，另行独立注册。',
    },
    {
        'item': 'bingyao-shenfeng-v1',
        'subject': '病药 Variant（神峰通考双对）',
        'disclosure_sites': ['src/tianji_kb/bazi_bingyao.py'],
        'disposition': 'registered',
        'phase1_rule_id': 'bazi.rule.r040',
        'phase2_rule_id': 'bazi.phase2.bingyao_assessment',
        'reason': '神峰经典 Canonical 扩编（E0348）：密封 Canonical '
                  '新建《神峰通考》经典（bazi.classic.shenfeng，'
                  'body_stage=quarantine，镜像既有四经典实体结'
                  '构），病药定义节建成 bazi.section.s071（快照字'
                  '符 [7019,7680) 整段 661 字、PUA/□ 均 0），正官'
                  '格张力句以窗口节 bazi.section.s072 承载，既有滴'
                  '天髓经典内补中和篇制衡窗口节 bazi.section.s074；'
                  '病药 9 条引文全数补 source_section_id（神峰 7 条'
                  '入 s071、张力 1 条入 s072、制衡 1 条入 s074）。'
                  '新术语 bazi.term.bingyao、Phase1 规则 '
                  'bazi.rule.r040（source_refs 恰为实际编码消费的 '
                  '4 条：病/药定义句 + 两条编码对句）与 Phase2 步 '
                  'bazi.phase2.bingyao_assessment（validated）逐字'
                  '绑定；assessment 经 bazi_chart 既有 '
                  'bingyao_variant 研究门控以 trace.add 真实执行，'
                  'Golden 6 例（复用 TJ-013 既有见证真实盘）真实 '
                  'fire。注册不改变任何语义：determination 恒 '
                  'None、无「无病」输出、双对结构与审定点 S1–S4 '
                  '逐字不变；登记引文（土重例/从重程序句/无病条款/'
                  '正官张力）与制衡引文不入规则 refs，各有明示地'
                  '位。',
        'unlock_path': None,
    },
    {
        'item': 'pattern-route-luren',
        'subject': '格局禄刃路线 pattern_route',
        'disclosure_sites': ['src/tianji_kb/bazi_pattern.py'],
        'disposition': 'registered',
        'phase1_rule_id': 'bazi.rule.r035',
        'phase2_rule_id': 'bazi.phase2.pattern_route',
        'reason': '定义性禄/刃表经 TJ-018.3 批三评估（E0337）复核、'
                  'B-1（E0338）卷三禄节 018 形制登记后，B-2（E0339）'
                  '建成 Canonical sections bazi.section.s063'
                  '（三命卷三《论十干禄》）与 bazi.section.s064'
                  '（卷五《论阳刃》），均以正式应用工作本 S3 切片'
                  '建节、零 PUA/零□；路线消费的四条引文逐字绑定：'
                  '任氏排除句（s054，既有 Canonical）、禄定义句'
                  'sanming.lu_sentence（s063，与 B-1 登记引文 '
                  'sgl.definition 同一引文的绑定补全、不重复立条）、'
                  '刃纲句 sanming.ren_doctrine 与刃位句 '
                  'sanming.ren_positions（s064）。阳刃节 14 处残余'
                  '防与 RD-12 seq 450 并列记录（UD-1=A 定格）、禄节'
                  '残余防 1 处（seq 47，unresolved）随节元数据逐字'
                  '携带，均不入定义引文。路线自 Slice A 起即经 '
                  'operations/bazi_chart.chart 真实执行（消费已执行 '
                  'pillars 步），B-2 将其接入 ExecutionTrace 注册步'
                  '（与同块候选步同形），Phase1 规则 r035 的 '
                  'source_refs 只引路线实际消费的四条引文（子集定稿'
                  '沿 r031 先例，未扩至两节全部登记引文；两节登记'
                  '引文逐条在场另经密封专项复核）。路线输出除注册'
                  '披露字段外逐盘逐字不变，determination 语义零'
                  '变化（恒负向排除、borrowed_route 恒 '
                  'undetermined）。',
        'unlock_path': None,
    },
    {
        'item': 'pattern-zaqi',
        'subject': '格局杂气选格陈述 pattern_zaqi',
        'disclosure_sites': ['src/tianji_kb/bazi_pattern.py'],
        'disposition': 'registered',
        'phase1_rule_id': 'bazi.rule.r036',
        'phase2_rule_id': 'bazi.phase2.pattern_zaqi',
        'reason': '治理 pending 8 项审计（E0341）定本项为纯节级缺口并'
                  '推荐为第一批；本批（E0342）建成 Canonical sections '
                  'bazi.section.s065（滴天髓八格章「影响遥系」子题原注'
                  '杂气段，快照 [33161,33313) 全文 152 字）、'
                  'bazi.section.s066（三命卷六《日禄归时》「青云得路」'
                  '法条窗口，S3 [192089,192173)）与 bazi.section.s067'
                  '（三命女命章杂气格诗句条目窗口，S3 [245029,245080)），'
                  '均零 PUA/零□；3 条引文逐字绑定：原注杂气段 '
                  'renshi.zaqi_passage 为规则引文（s065），三命两例证 '
                  'sanming.zaqi_case_rilu / sanming.zaqi_poem_nvming '
                  '只作冲突分支证据的节绑定（s066/s067，沿 '
                  'Slice B 审定 B5 并列口径，不作规则、不裁定）。陈述'
                  '自 Slice B 起即经 operations/bazi_chart.chart 真实'
                  '执行（消费已执行的 pillars / ten_gods / hidden_stems '
                  '/ hidden_to_visible 步），本批将其接入 '
                  'ExecutionTrace 注册步；Phase1 规则 r036 的 '
                  'source_refs 恰为裁定依据 1 条（原注杂气段，子集定稿'
                  '沿 r031/r035 先例；两例证非裁定依据、不入规则 refs，'
                  '其证据地位由窗口节与陈述 conflict.case_refs 承载）。'
                  '陈述输出除注册披露字段外逐盘逐字'
                  '不变，裁定语义零变化：戊己臂多人元透出并列、无透 '
                  'abstain、一般臂只录「取土为格」原文且土格换算恒 '
                  'unadjudicated、determination 恒 None。',
        'unlock_path': None,
    },
    {
        'item': 'ren-pattern-yin-true-v1',
        'subject': 'Slice D-1 任氏寅月真格 determination',
        'disclosure_sites': ['src/tianji_kb/bazi_pattern.py'],
        'disposition': 'registered',
        'phase1_rule_id': 'bazi.rule.r037',
        'phase2_rule_id': 'bazi.phase2.ren_yin_true_pattern',
        'reason': '治理 pending 8 项审计（E0341）§2.7 定本项为零材料'
                  '缺口、纯执行结构缺口并列为第二顺位；本批（E0344）'
                  '按其 unlock_path 完成执行绑定：原典锚点全部在 '
                  'Canonical 内（真格定义 bazi.section.s053、任氏'
                  '程序 bazi.section.s054、司令分段 '
                  'bazi.section.s024，均既有节、本批不建新节），'
                  'Phase1 规则 r037 的 source_refs 恰为 determination '
                  '实际消费的 3 条引文（s053 原注定义句、s054 任氏曰'
                  '程序句、s024 寅月分日用事句，子集定稿沿 r031/r035 '
                  '先例）。'
                  'chart 不带出生瞬时与 jie 声明、试点不能在 chart '
                  '内调用（审定 D4）的结构事实不变，解法为门控显式'
                  '输入：chart 新增门控参数 ren_yin_pilot_result'
                  '（默认 None、engine allow_research 门禁），块在 '
                  'pattern 块内经 trace.add 注册步产出、进 RuleMatch '
                  '与 Evidence；试点结果恒为显式输入声明，D6 身份钉'
                  '验证与已执行事实交叉核对保持在组合函数内。golden '
                  'harness 输入契约的扩展只落 provider 签名与用例 '
                  'input 字段，golden.py 的 provider 三重钉死逐字未'
                  '动；D-1 既有 15 例真实盘 Golden 转入密封 Golden '
                  '并经 harness 真实 fire 新步。determination 语义逐'
                  '字不变：true_false 三态（true / '
                  'commander_not_visible / abstained）、永不输出假'
                  '格、破格/成败/清浊/用神恒 None+unreviewed、父级裁'
                  '定 D1/D2 与 Slice A 路线优先序不变。',
        'unlock_path': None,
    },
    {
        'item': 'siling-yin-pilot',
        'subject': '司令寅月试点 Variant bazi-siling-yin-pilot-v1',
        'disclosure_sites': ['src/tianji_kb/bazi_siling_pilot.py'],
        'disposition': 'maintained_pending',
        'reason_class': 'execution_binding_structure',
        'reason': '独立 Variant、不经 ExecutionTrace；bazi Phase2 契约'
                  '为单一 Variant（ziping-structural-v1），试点无法以'
                  '自身 Variant 登记执行规则。且其定义性计算约定'
                  '（连续 24 小时计日）是用户裁定的暂定程序约定、非'
                  '原典规则，登记为 Phase1 原典规则即属误标；其原典'
                  '锚点 s024（寅月分日）已由 r017/r020/r026 注册覆盖。',
        'unlock_path': '试点若转正（用户裁定扩月/约定转正）并接入 '
                       'ExecutionTrace 后，再行注册；当前维持研究级。',
    },
    {
        'item': 'siling-matrix-register',
        'subject': '分日司令冲突矩阵登记（bazi_siling_matrix）',
        'disclosure_sites': ['src/tianji_kb/bazi_siling_matrix.py'],
        'disposition': 'not_a_candidate',
        'reason': '纯登记数据、无执行产出，无 evidence_binding 可翻转；'
                  '其寅月试点格的执行面即 siling-yin-pilot 项。',
        'unlock_path': None,
    },
    {
        'item': 'f4-changsheng-design',
        'subject': 'F4 丙×寅长生形态设计（changsheng_visible_support）',
        'disclosure_sites': ['src/tianji_kb/bazi_fire_si_yin_morphology.py'],
        'disposition': 'not_a_candidate',
        'reason': '审定成立但未实现（实现门为司令扩月用户裁定），无运行'
                  '时产出与披露可翻转。',
        'unlock_path': '用户裁定司令扩月后先实现，再议注册。',
    },
    {
        'item': 'fuyi-slice-adjudication-register',
        'subject': '扶抑最小切片审定登记（S4，SLICE_SPEC=None）',
        'disclosure_sites': ['src/tianji_kb/bazi_fuyi_slice_adjudication.py'],
        'disposition': 'not_a_candidate',
        'reason': 'S4 审定结论零行可建、无可执行单元存在；其 '
                  'registration 字段是审定记录本身（含解锁前置 U1/U3 '
                  '用户级裁定），非待注册披露。',
        'unlock_path': 'U1 程度词操作定义 / U3 中间状态定义经用户裁定'
                       '后，另行审定可建行再议注册。',
    },
    {
        'item': 'sanxing-branch-fact-v1',
        'subject': '三刑结构事实层切片 sanxing-branch-fact-v1（TJ-012.3）',
        'disclosure_sites': ['src/tianji_kb/bazi_sanxing_facts.py'],
        'disposition': 'registered',
        'phase1_rule_id': 'bazi.rule.r031',
        'phase2_rule_id': 'bazi.phase2.branch_punishment_facts',
        'reason': '定义锚点全部在 Canonical 内：TJ-018.3 P1 批'
                  '（E0329）建成 chapter bazi.chapter.'
                  'sanming_sanxing、section bazi.section.s060'
                  '（《论三刑》整节）与 term '
                  'bazi.term.branch_punishments，11 条登记引文逐'
                  '字绑定；执行绑定设计批（E0332）审定唯一接入'
                  '点后，批一（E0333）将事实函数经 operations/'
                  'bazi_chart.chart 关系事实块之后的门控步（参数 '
                  'include_punishment_facts 默认关、engine '
                  'allow_research 门禁）接入生产执行，注册为 '
                  'Phase2 事实步 bazi.phase2.'
                  'branch_punishment_facts，其 Phase1 规则 '
                  'bazi.rule.r031 的 source_refs 只引 s060 内 6 '
                  '条定义性引文（审定登记组表与自刑行引文并集）'
                  '并逐条经 EvidenceResolver 验证；Golden 10 例'
                  '真实盘经 harness 真实 fire 该步。事实步与裁'
                  '决面结构分离：不产生 RuleMatch、不写入 '
                  'sufficient_rule、不进任何裁决输入，组名与教'
                  '义状态（B2/B5）逐字不变。',
        'unlock_path': None,
    },
]

FLIPPED_ITEMS = [row['item'] for row in REGISTRATION_INVENTORY
                 if row['disposition'] == 'registered']
MAINTAINED_ITEMS = [row['item'] for row in REGISTRATION_INVENTORY
                    if row['disposition'] == 'maintained_pending']
