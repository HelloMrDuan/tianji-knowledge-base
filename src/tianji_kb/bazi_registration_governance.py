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
        'disposition': 'maintained_pending',
        'reason_class': 'canonical_evidence_absent',
        'reason': '《穷通宝鉴》不在密封 Canonical 经典内（Canonical 仅'
                  '渊海子平、三命通会、协纪辨方书、滴天髓阐微四书），'
                  '调候全部引文无 canonical section 可绑。',
        'unlock_path': 'Canonical 经典扩编治理批：穷通宝鉴建经典/章节/'
                       'sections 并逐条复核引文后，另行注册。',
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
                  '（E0335 父级审定定稿），不声称真实盘正例 fire。',
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
        'disposition': 'maintained_pending',
        'reason_class': 'canonical_evidence_absent',
        'reason': '21 条登记引文 0 条在 Canonical 内：三命卷十一折除诸段'
                  '无 canonical section，神峰通考不在 Canonical 经典内。',
        'unlock_path': '先行 Canonical 扩编（三命卷十一大运节登记；神峰'
                       '建经典），再行注册批。',
    },
    {
        'item': 'dayun-compose',
        'subject': '大运组合入口 classical_dayun_timeline',
        'disclosure_sites': ['src/tianji_kb/bazi_dayun_compose.py'],
        'disposition': 'maintained_pending',
        'reason_class': 'inherited_pending',
        'reason': '组合层不产生独立规则，其 evidence_binding 继承所组合'
                  '古典 Variant 的 pending 状态。',
        'unlock_path': '随 dayun-classical-variants 注册自动解除。',
    },
    {
        'item': 'dayun-timeline-view',
        'subject': '大运研究层视图 dayun-timeline-view-v1',
        'disclosure_sites': ['src/tianji_kb/bazi_dayun_timeline_view.py'],
        'disposition': 'maintained_pending',
        'reason_class': 'inherited_pending',
        'reason': '视图层 Variant，只呈现底层区间产出，本身不产生裁决，'
                  '其 binding 继承底层 pending 状态。',
        'unlock_path': '随 dayun-classical-variants 注册自动解除。',
    },
    {
        'item': 'bingyao-shenfeng-v1',
        'subject': '病药 Variant（神峰通考双对）',
        'disclosure_sites': ['src/tianji_kb/bazi_bingyao.py'],
        'disposition': 'maintained_pending',
        'reason_class': 'canonical_evidence_absent',
        'reason': '神峰通考不在 Canonical 经典内，病药 9 条引文 0 条可'
                  '在 Canonical 验证。',
        'unlock_path': '先行 Canonical 扩编（神峰建经典并登记病药诸节），'
                       '再行注册批。',
    },
    {
        'item': 'pattern-route-luren',
        'subject': '格局禄刃路线 pattern_route',
        'disclosure_sites': ['src/tianji_kb/bazi_pattern.py'],
        'disposition': 'maintained_pending',
        'reason_class': 'canonical_evidence_absent',
        'reason': '定义性禄/刃表（三命卷三《论十干禄》、卷五《论阳刃》'
                  '原文）无 canonical section；登记 4 引文中仅路线排除'
                  '引文（s054）在 Canonical 内，表格本体 0 条可验证。',
        'unlock_path': '先行 Canonical sections 扩编（三命禄/刃两节登记'
                       '入 Canonical），再行注册批。',
    },
    {
        'item': 'pattern-zaqi',
        'subject': '格局杂气选格陈述 pattern_zaqi',
        'disclosure_sites': ['src/tianji_kb/bazi_pattern.py'],
        'disposition': 'maintained_pending',
        'reason_class': 'canonical_evidence_absent',
        'reason': '原注杂气段与三命两例证 0/3 在 Canonical 内（s053/s054 '
                  '不含杂气段原文）。',
        'unlock_path': '先行 Canonical sections 扩编（滴天髓杂气相关段'
                       '与三命例证节登记），再行注册批。',
    },
    {
        'item': 'ren-pattern-yin-true-v1',
        'subject': 'Slice D-1 任氏寅月真格 determination',
        'disclosure_sites': ['src/tianji_kb/bazi_pattern.py'],
        'disposition': 'maintained_pending',
        'reason_class': 'execution_binding_structure',
        'reason': '原典锚点全部在 Canonical 内（真格定义 s053、任氏程序 '
                  's054、司令 s024，2/2+司令可验证），且已由 r027/r028 '
                  '在候选层引用；但 determination 由独立组合函数在 '
                  'ExecutionTrace 之外产出（chart 不带出生瞬时、司令'
                  '试点结果显式传入），Phase2 golden harness 的输入'
                  '契约仅四柱干支、无出生瞬时与交节 provider，无法执行'
                  '该 determination——注册将无执行步可绑。',
        'unlock_path': '执行绑定设计批：determination 接入 trace 步'
                       '（显式试点结果作为已执行输入）并扩 golden 输入'
                       '契约后，再行注册。',
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
