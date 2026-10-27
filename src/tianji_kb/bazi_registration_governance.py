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
    'pin_record': '可信机 cicd/env/trusted-acceptance 已按既有密封治理'
                  '流程更新为 manifest_sha256_after（旧值留档于本记录与'
                  '机器侧备份），部署管线与本批验收均以新钉值复核。',
    'verdict_surface_change': '无：两条翻转谓词的 classification、条件集、'
                              'blockers 与全部其他谓词/变体的产出逐字不变；'
                              '变化仅在 why.sufficient_rule（None -> 注册 '
                              'ID）、matched_rule_ids（新增注册规则步）与'
                              '披露文本。',
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
        'disposition': 'maintained_pending',
        'reason_class': 'canonical_evidence_absent',
        'reason': '定义性锚点「丙禄在巳」（三命卷二逐干句、卷三禄节、'
                  '神峰禄表）无 canonical section：Canonical 三命通会'
                  '仅咸池一节，神峰通考不在 Canonical 经典内。F34 登记 '
                  '13 条引文引用中三命/神峰部分 0 条可在 Canonical 验证。',
        'unlock_path': '先行 Canonical sections 扩编（三命卷二/卷三禄节'
                       '逐节登记入 Canonical 并复核），再行注册批。',
    },
    {
        'item': 'pure_support_metal',
        'subject': '旺衰谓词 金×酉 纯生扶',
        'disclosure_sites': ['src/tianji_kb/bazi_adjudication.py'],
        'disposition': 'maintained_pending',
        'reason_class': 'canonical_evidence_absent',
        'reason': '根有效性定义锚点为 S1 登记的三命卷二庚/辛逐干生死句，'
                  '10 条根引文 0 条在 Canonical sections 内（Canonical '
                  '三命仅咸池一节）。',
        'unlock_path': '先行 Canonical sections 扩编（三命卷二干支生死'
                       '节登记入 Canonical），再行注册批。',
    },
    {
        'item': 'pure_generating_support_water',
        'subject': '旺衰谓词 水×子 纯生扶',
        'disclosure_sites': ['src/tianji_kb/bazi_adjudication.py'],
        'disposition': 'maintained_pending',
        'reason_class': 'canonical_evidence_absent',
        'reason': '同 pure_support_metal：壬/癸逐干生死句 0/10 在 '
                  'Canonical 内。',
        'unlock_path': '先行 Canonical sections 扩编（三命卷二干支生死'
                       '节登记入 Canonical），再行注册批。',
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
]

FLIPPED_ITEMS = [row['item'] for row in REGISTRATION_INVENTORY
                 if row['disposition'] == 'registered']
MAINTAINED_ITEMS = [row['item'] for row in REGISTRATION_INVENTORY
                    if row['disposition'] == 'maintained_pending']
