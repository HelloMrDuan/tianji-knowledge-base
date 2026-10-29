"""三命通会「PUA＋校勘正式应用批」设计审定登记（TJ-018.2 审定批，E0294）。

DESIGN / ADJUDICATION BATCH。本模块是纯数据审定登记，**零计算逻辑、
零判定代码**：不含任何函数，不被任何可执行路径 import（由公开测试
钉住）。本批是 TJ-018.3 晋级前置的**设计审定**：只产出应用批的
可执行规约与前置清单，**不实际应用任何文本订正、不改快照、不改
既有登记**（机上实测全部为只读内存复放，不落盘）。

背景：018-H（E0265）已证明 603 条 confirmed 订正按管线序（PUA
阶段 → 文本阶段文件序）两阶段复放可全量应用（66 条零匹配全归因：
PUA 前提 41 + 链式依赖 25，漂移与未决均 0）；993 重锚（E0273）
已清零坐标面障碍（位点 993/993 可锚、context 917 可锚 / 76 条
跨订正边界不可锚、159 条 confirmed_applied 恰为 ocr-445..603）。
两批共同留下的 TJ-018.3 晋级要件——正式应用批与应用报告、残余
「防」769 处路线、12 条 reading_disagreement 见证互校、
unresolved_text_gaps 2 处处置、版本冻结登记——由本批逐项给出
规约与判定接口，应用本体另批执行。

核心规约（全量见 PIPELINE_SPEC）：应用批取**单批两阶段**形态
（审定点 AP1）——阶段一以仓库脚本 apply_pua_collation.py 应用
86 映射 / 524 处（全等长、位置恒等），阶段二以
apply_sanming_text_collation.py 按文件序应用 603 条；阶段二在
ocr-444 处设检查点（中间文本哈希必须 == 重锚登记的基线钉值
db8618c9…），把应用批与重锚证据链钉在一起；终局文本哈希钉值
a89c0b5d…（本批内存复放实测）。逐条应用记录含 before/after
语境哈希，往返校验只认 origin 位点图（朴素逆替换禁用，AP3）；
十项 fail-hard（F1–F10）任一触发整批丢弃、零部分应用（含附件）。
阶段一启动前置 PUA **全核**门（AP2）：实测现行复核覆盖上界仅
32/86 码位有公开登记引用、54/86 零引用，且密封 PUA 审计文件无
逐码位裁定状态字段——「全 confirmed」只是流水线自述。

76 条 context 跨界候选（52 部分交叠 + 24 位于长订正替换域内）
由 CONTEXT_CARRY_SPEC 规约随应用批附件携带：逐条位点映射至
S3、按登记窗口同形重取 context、24 条另注与消费订正的关系；
缺失只能显式登记为 limitation，禁止静默丢弃。残余「防」769 处
（S3 实测，其 ±6 字语境 769 个全互异——逐处互校最小单元即
769）按 RESIDUAL_FANG_ROUTE 逐处处置（confirmed/并列/hold 三
种登记处置，全局替换永久禁用）。12 条 reading_disagreement 的
见证结构是谱系对谱系（四库谱系 kanripo+mikkokotila 同读、现代
转录谱系读异字），互校标准与逐条注记见
READING_DISAGREEMENT_SPEC，默认处置为并列登记、不需用户裁定；
缺口 2 处（谬□甚矣、王麟洲少□）以永久缺口登记为终局处置
（AP4），只阻断整书晋级。

版本冻结以本批合并为时点（FREEZE_REGISTER 五件文件哈希 + 三
阶段文本哈希 + 密封 manifest 三元组 e5a590b4…）；应用批产物为
与快照并存的新版本文件（应用文本 + 应用报告，密封文件 235 →
237，manifest 换代与双钉同步照 S5/TJ-019.2 规程）。晋级判定
接口见 PROMOTION_INTERFACE：应用批之后还剩 P1 终局化登记
（47 异文 + 775 历史读法）、P2 残余防处置、P3 见证互校、P4
决策包；用户级待裁定 3 项（UD-1..UD-3）均登记选项与设计建议、
本批不代决。整书 canonical_ready 保持 false（设计立场 AP6：
逐节晋级为唯一推荐路径）。

红线：本批零应用、零快照改动、零密封资产改动、零判定代码；
不改变既有校勘记（累计 383 条）、零匹配归因册、重锚册与候选
状态语义；TJ-018.2 保持阻塞、TJ-018.3 保持待做。

后记（E0327，UD 裁定登记批追加，设计登记原文不改）：P4 决策包
（E0326）正式呈请后，用户于 2026-10-30 裁定 UD-1、UD-2、UD-3
三项全采设计建议 A。裁定逐项登记于 PROMOTION_INTERFACE 的
user_decisions 各条新增 adjudication 字段（question、options、
needed_now 与 design_recommendation 逐字保留）；headline_verdicts
的 user_decisions_pending=3 为本设计批（E0294）当时状态的记录，
不回改。本后记与 adjudication 字段是本模块在 E0294 之后唯一的
增补，既有证据数据（计数、哈希、位点、读法）逐字不变。
"""

FORMAL_APPLICATION_DESIGN_REGISTER = {'id': 'sanming-formal-application-design-register-v1',
 'task': 'TJ-018.2',
 'kind': 'formal_application_design_register',
 'adjudication_batch': 'TJ-018.3 晋级前置——三命通会「PUA＋校勘正式应用批」设计审定批（纯审定，零应用）',
 'design_doc': 'docs/product/TJ0183_FORMAL_APPLICATION_DESIGN.md',
 'source_snapshot': {'name': 'daizhigev20',
                     'sanming_sha256': '00e2a7db8bb59b259b99938033bb1bb77947e04a15dafc111e62b59378010c86',
                     'sanming_chars': 461157,
                     'sanming_bytes': 1342659,
                     'trusted_manifest_sha256': 'e5a590b48d496d846c888551695e45843e90b543fb10f671aa9f229a6c9960a5',
                     'trusted_manifest_files': 235,
                     'trusted_manifest_bytes': 13580501},
 'baseline': {'repo': 'HelloMrDuan/tianji-knowledge-base',
              'main_sha': 'e72f69ea7c85f171aa20f890041544be4f6d7c02',
              'ledger_events_before': 293,
              'ledger_event': 'E0294',
              'formal_acceptance_baseline': 'SUCCESS 2436（b8ff708c '
                                            '正式验收：public-git 15 + public-only '
                                            '24 + private-backend 2397）'},
 'headline_verdicts': {'design_only': True,
                       'applied_in_this_batch': False,
                       'snapshot_modified': False,
                       'sealed_assets_modified': False,
                       'pipeline_stages': 2,
                       'pua_mappings': 86,
                       'pua_occurrences': 524,
                       'text_corrections': 603,
                       'baseline_checkpoint_corrections': 444,
                       'candidates_total': 993,
                       'context_unanchorable_candidates': 76,
                       'residual_fang_after_application': 769,
                       'reading_disagreement_items': 12,
                       'permanent_gaps': 2,
                       'pua_codepoints_with_register_citation': 32,
                       'pua_codepoints_without_register_citation': 54,
                       'user_decisions_pending': 3,
                       'application_spec_ready': True,
                       'canonical_ready': False,
                       'review_status': 'in_progress'}}

FREEZE_REGISTER = [{'object': 'snapshot_text',
  'role': '应用批唯一输入底本（S0），只读、永不作写入目标',
  'path': 'data/quarantine/public_domain_snapshots/daizhigev20/sanming_tonghui.txt',
  'sha256': '00e2a7db8bb59b259b99938033bb1bb77947e04a15dafc111e62b59378010c86',
  'bytes': 1342659,
  'chars': 461157,
  'measured_facts': {'pua_occurrences': 524,
                     'pua_codepoints': 86,
                     'fang_occurrences': 1606,
                     'gap_square_occurrences': 2}},
 {'object': 'pua_collation',
  'role': '阶段一映射表（85 统一 + 1 语境）',
  'path': 'data/quarantine/public_domain_snapshots/daizhigev20/sanming_pua_collation.json',
  'sha256': '96943525453662663918965d28711a2f1b0758aef7bc9b4a3aaafb770dbfdd97',
  'measured_facts': {'uniform_mappings': 85,
                     'uniform_status_all': 'confirmed',
                     'uniform_occurrences': 519,
                     'contextual_mappings': 1,
                     'contextual_codepoint': 'U+E7E8',
                     'contextual_occurrences': 5,
                     'contextual_rules': 4,
                     'summary_confirmed_mappings': 86,
                     'summary_confirmed_occurrences': 524,
                     'crosscheck_sources': [{'repo': 'NiuTrans/Classical-Modern',
                                             'commit': '4e746ea9fa99c3c0d7051c45397330bef7b0962d'},
                                            {'repo': 'youngzs/xuanxue',
                                             'commit': 'aa7bc942602d2d88ef94778a726c0d19a4d286ff'}]}},
 {'object': 'text_collation',
  'role': '阶段二订正表（文件序即应用序）',
  'path': 'data/quarantine/public_domain_snapshots/daizhigev20/sanming_text_collation.json',
  'sha256': 'e47bce8c478327b3bcb7f804c29ad4189d824b40a9d2e0ea5032ddebf39ff4ce',
  'measured_facts': {'stage_field': 'post_pua_text_collation',
                     'policy_field': 'Apply only exact context-anchored '
                                     'corrections backed by at least two '
                                     'independent witnesses. Raw snapshot '
                                     'remains immutable.',
                     'corrections': 603,
                     'status_all': 'confirmed',
                     'id_range': 'ocr-001..ocr-603（连续无缺号）',
                     'allow_existing_target_ids': ['ocr-022'],
                     'length_changing': [{'id': 'ocr-017',
                                          'old_len': 16,
                                          'new_len': 15}],
                     'snapshot_direct_match': {'exactly_once': 537,
                                               'zero': 66,
                                               'multiple': 0},
                     'fang_in_old_strings': 897,
                     'fang_in_new_strings': 60,
                     'fang_net_removed': 837,
                     'summary_review_status': 'in_progress',
                     'summary_canonical_ready': False}},
 {'object': 'ocr_candidates',
  'role': '993 条跨本候选（处置附件的数据源）',
  'path': 'data/quarantine/public_domain_snapshots/daizhigev20/sanming_ocr_candidates.json',
  'sha256': '4209b85d003d07ca696e298c3f446c43ea8a8d6871dfe73e52fc7c17a16d211c',
  'measured_facts': {'candidates': 993,
                     'status_counts': {'historical_only_hold': 775,
                                       'variant_preserve': 47,
                                       'confirmed_applied': 159,
                                       'reading_disagreement_hold': 12},
                     'offset_basis': 'zero-based Unicode character offset '
                                     'after immutable raw -> 86 PUA mappings '
                                     '-> ocr-001 through ocr-444',
                     'baseline_field': 'e6dab2c5a59f2d537ac019b0b764a14111c1bfe0',
                     'confirmed_applied_correction_id_set': 'ocr-445..ocr-603 '
                                                            '全集（逐一对应、无缺无余）'}},
 {'object': 'pua_audit',
  'role': '流水线侧 PUA 审计（覆盖率缺口的证据面）',
  'path': 'data/quarantine/public_domain_snapshots/daizhigev20/sanming_pua_audit.json',
  'sha256': '22f214e89134107b721b4888ddb3d29bacee5e3cbfeb7eb890b665caf0969569',
  'measured_facts': {'glyph_entries': 86,
                     'glyph_fields': ['codepoint',
                                      'contexts',
                                      'count',
                                      'glyph'],
                     'per_codepoint_adjudication_status_field': False,
                     'blocker_field': 'Unicode Private Use Area glyphs '
                                      'require independent collation before '
                                      'canonical promotion.',
                     'identified_gap_corrections': 2}}]

STAGE_TEXT_PINS = [{'stage_id': 'S0',
  'definition': '钉定快照原样（raw）',
  'chars': 461157,
  'bytes': 1342659,
  'sha256': '00e2a7db8bb59b259b99938033bb1bb77947e04a15dafc111e62b59378010c86',
  'pua': 524,
  'fang': 1606,
  'gap_square': 2},
 {'stage_id': 'S1',
  'definition': 'S0 经阶段一（PUA 86 映射）应用后；与 S0 全等长、位置恒等',
  'chars': 461157,
  'bytes': 1342685,
  'sha256': 'b4f196f2100347618d7907330b2db93bd536a5663f16249a6e0ff19e23c05daa',
  'pua': 0,
  'fang': 1606,
  'gap_square': 2},
 {'stage_id': 'S2',
  'definition': 'S1 经阶段二 ocr-001..444 应用后（= 候选 offset_basis 的基线文本；重锚登记册钉值）',
  'chars': 461156,
  'bytes': None,
  'sha256': 'db8618c9cdbc545b59149f7550644a440fdf8bba8ddbe0e23b615029f8a896d9',
  'pua': 0,
  'fang': 925,
  'gap_square': 2},
 {'stage_id': 'S3',
  'definition': 'S1 经阶段二 ocr-001..603 全量应用后（应用批产物文本）',
  'chars': 461156,
  'bytes': 1342682,
  'sha256': 'a89c0b5da16ea4e07dc85180c49135ed280875318059f923ff7154f2c217662f',
  'pua': 0,
  'fang': 769,
  'gap_square': 2}]

PIPELINE_SPEC = {'form': '单批两阶段（审定点 AP1）：一个应用批、一份应用报告、一次冻结校验；阶段边界处设 S2 检查点',
 'coordinate_systems': [{'id': 'S0',
                         'name': '快照坐标',
                         'note': '对快照原样的零基字符偏移；既有逐节校勘记（累计 383 '
                                 '条）与零匹配归因位点在此坐标系'},
                        {'id': 'S1',
                         'name': 'PUA 后坐标',
                         'note': '阶段一全等长替换，位置与 S0 恒等（偏移可直接互译）；S1 不单独登记为工件'},
                        {'id': 'S2',
                         'name': '基线坐标',
                         'note': '候选文件 offset_basis 坐标系；与 S0 经 origin '
                                 '图互译（重锚登记册已钉）；ocr-017 变长使偏移在其位点后整体 −1'},
                        {'id': 'S3',
                         'name': '全应用坐标',
                         'note': '应用批产物坐标系；与 S2 仅差 ocr-445..603 '
                                 '段改写（该段无变长订正，长度与 S2 相同）'}],
 'stage_1_pua': {'executor': 'scripts/apply_pua_collation.py（仓库脚本原样，不改脚本）',
                 'input': 'S0 + pua_collation（冻结哈希校验通过后）',
                 'semantics': ['仅 status=confirmed 行参与（实测 85 统一全 confirmed + '
                               '1 语境 confirmed）',
                               '统一映射：逐码位先验计数——快照中该字形出现次数须与登记 count 逐一相等（519 '
                               '处合计），不等即漂移 fail-hard；通过后整串替换',
                               '语境映射（U+E7E8，5 处 / 4 规则）：逐规则锚串在当前文本中恰出现 1 '
                               '次才替换；规则合计须等于登记 count 且该字形零残留',
                               '替换字不得含 PUA；码位与字形须自洽（codepoint == U+%04X of '
                               'glyph）；重复映射 fail-hard',
                               '阶段输出校验：PUA 残留 0、字数 461157（等长不变量）、SHA256 == S1 '
                               '钉值'],
                 'phase_0_gate': '阶段一启动前置 = PUA 全核门（fail-hard F10）：86/86 '
                                 '码位逐一见证复核登记完成（见 PUA_FULL_VERIFICATION）',
                 'output': 'S1（中间态，只存在于应用批工作副本与报告哈希链中）'},
 'stage_2_text': {'executor': 'scripts/apply_sanming_text_collation.py（仓库脚本原样，不改脚本）',
                  'input': 'S1 + text_collation（冻结哈希校验通过后）',
                  'order': '文件序 ocr-001..ocr-603，即应用序；不得重排、不得并行',
                  'semantics': ['仅 status=confirmed 行参与（实测 603/603）；id 唯一、old '
                                '非空、new 非空、old != new',
                                'old/new 均不得含 PUA——脚本以此强制阶段顺序（文本阶段严格后于 PUA '
                                '阶段）',
                                '逐条轮次校验：old 在当前文本中恰出现 1 次（0 次或多次即 '
                                'fail-hard）；此条同时构成链式依赖 25 '
                                '条的合法性证明——依赖只经文件序在先条目满足，不得改序迁就',
                                '目标预存校验：new 若已在当前文本中出现且该条未登记 '
                                'allow_existing_target 则 '
                                'fail-hard；豁免的登记与使用都必须恰为 {ocr-022} 一条（实测登记 1 '
                                '条：ocr-022「身品琐小」→「身材琐小」，目标串「身材琐小」因他处预存而豁免）',
                                '检查点：ocr-444 应用毕即校验中间文本 SHA256 == S2 '
                                '钉值（db8618c9…），把应用批与重锚证据链（E0273）钉在一起；不等即 '
                                'fail-hard',
                                '阶段输出校验：603/603 全应用、SHA256 == S3 钉值、PUA '
                                '0、残余「防」769、□ 2'],
                  'output': 'S3（应用批产物文本）+ 应用报告 + 候选处置附件'},
 'per_correction_record_fields': ['seq（1..603 文件序）',
                                  'correction_id',
                                  'site_offset（该条轮次当前文本中的 old 起点偏移）',
                                  'old_sha256',
                                  'new_sha256',
                                  'context_before_sha256（位点前后各 32 字，应用前）',
                                  'context_after_sha256（应用后同位窗口）',
                                  'len_delta',
                                  'note（仅链式依赖条目登记其材料依赖 id，与 E0265 归因登记对账）'],
 'report_fields': ['batch_id 与基线 main SHA、冻结校验结果（五文件哈希逐一）',
                   'stage_1：逐码位 {codepoint, mode, '
                   'count}（镜像仓库脚本报告并扩展）、input_sha256、output_sha256（== S1 钉值）',
                   'checkpoint_444：sha256（== S2 钉值）',
                   'stage_2：逐条记录（per_correction_record_fields）、豁免使用集、input_sha256、output_sha256（== '
                   'S3 钉值）',
                   'residual_scan：{pua: 0, fang: 769, gap_square: 2}',
                   'round_trip：origin 图逆复放结果（恢复 S0 哈希 == 快照钉值；逆行至 444 检查点 == '
                   'S2 钉值）',
                   'candidate_annex：993 条处置（见 CONTEXT_CARRY_SPEC '
                   '与处置分类）、permanent_gaps 2 条原样携带记录',
                   '产物登记：S3 文件哈希/字节数、报告自身哈希、manifest 新三元组'],
 'round_trip': {'method': 'origin 位点图逆复放（与 E0273 重锚同机械）：正向应用全程逐字记录 origin，逆向按 '
                          'origin 图重建输入并比对哈希',
                'prohibited': '禁止以朴素逆字符串替换（new→old）作往返校验：统一 PUA '
                              '替换在逆向多义（替换字在原文他处可预存）、ocr-022 '
                              '豁免证明目标串预存真实发生，朴素逆替换会产生假阴性/假阳性',
                'checkpoints': ['逆复放至 S2 == db8618c9…',
                                '逆复放至 S0 == 00e2a7db…']},
 'fail_hard_conditions': [{'id': 'F1',
                           'condition': '冻结漂移：五件冻结对象任一哈希或密封 manifest 三元组与 '
                                        'FREEZE_REGISTER 不符 → 开工前中止，零写入'},
                          {'id': 'F2',
                           'condition': '阶段一逐码位计数漂移（统一映射 expected != '
                                        'actual、语境锚串 != 1 次、语境合计 != 登记 '
                                        'count、语境字形残留）→ 中止并丢弃暂存区'},
                          {'id': 'F3', 'condition': '阶段一输出哈希 != S1 钉值 → 中止'},
                          {'id': 'F4',
                           'condition': '阶段二任一条 old 在其轮次出现次数 != 1 → '
                                        '中止（不得改序、不得跳过、不得放宽锚串）'},
                          {'id': 'F5',
                           'condition': '目标预存校验失败，或 allow_existing_target 使用集 '
                                        '!= 登记集 {ocr-022} → 中止'},
                          {'id': 'F6',
                           'condition': '444 检查点哈希 != S2 钉值 → '
                                        '中止（应用批与重锚证据链脱钉）'},
                          {'id': 'F7',
                           'condition': '终局校验失败：S3 哈希 != 钉值，或 PUA != '
                                        '0，或残余「防」!= 769，或 □ != 2 → 中止'},
                          {'id': 'F8',
                           'condition': '附件不完备：993 处置缺条、76 条 context 携带缺失且未登 '
                                        'limitation、RD-12 位点字在 S3 与快照 old '
                                        '不符、缺口 2 处未原样携带 → '
                                        '整批不完成（文本暂存区一并丢弃，零部分应用含附件）'},
                          {'id': 'F9',
                           'condition': '写入纪律违反：任何写入指向快照文件本体或 '
                                        'data/canonical/** 路径（两支仓库脚本对 '
                                        'canonical 路径自带拒绝，应用批不得绕过、不得改脚本放行）→ '
                                        '中止并报告'},
                          {'id': 'F10',
                           'condition': 'PUA 全核门未过：任一码位缺逐一见证复核登记 → 阶段一不得启动'}],
 'zero_partial_application': '全部产出先写工作副本暂存区，十项 fail-hard '
                             '任一触发即整批丢弃；正式产物路径只在全链（含附件）通过后以原子改名落位；快照本体永不打开写入',
 'product_form': {'new_sealed_files': ['data/quarantine/public_domain_snapshots/daizhigev20/sanming_tonghui_applied_v1.txt（S3 '
                                       '文本，1342682 字节）',
                                       'data/quarantine/public_domain_snapshots/daizhigev20/sanming_formal_application_report_v1.json（应用报告，含候选处置附件）'],
                  'untouched': '快照本体与三份 JSON、PUA 审计 JSON '
                               '逐字不动；planned_output（data/canonical/classics/bazi/sanming_tonghui_v1.json）仍不生成',
                  'registration': 'public_domain_manifest.json 的 '
                                  'sanming_tonghui 条目下新增应用版本记录（derived_from '
                                  '快照哈希、S1/S2/S3 钉值、报告哈希）；review_status 保持 '
                                  'in_progress、canonical_ready 保持 '
                                  'false——应用产物是工作本，不是 canonical',
                  'manifest_rotation': '密封快照文件数 235 → 237，总字节 = 13580501 + '
                                       '1342682 + '
                                       '报告字节数（报告大小由应用批实产出决定，新三元组由应用批在其 PR '
                                       '中携带）',
                  'dual_pin_sync_checklist': ['live 快照换位：新增两文件入 daizhigev20 '
                                              '目录，旧快照全量保留于机上 secure/ 下 '
                                              'pre-<应用批>-backup（照 S5/TJ-019.2 '
                                              '规程）',
                                              'cicd/env/trusted-acceptance 的 '
                                              'TRUSTED_MANIFEST_SHA256 '
                                              '更新为新三元组哈希',
                                              '私有构建脚本 '
                                              'scripts/import_public_snapshot.py '
                                              '的 EXPECTED_FILES（235→237）与 '
                                              'EXPECTED_BYTES 同步更新，并以脚本自身 '
                                              'manifest_for() 重生私有检出 '
                                              'manifest（检出 manifest 格式与快照 '
                                              'manifest 格式不同，永不互抄）',
                                              '私有检出侧未提交编辑 + 备份目录 + '
                                              'REGISTRATION 说明文件（照 '
                                              'REGISTRATION_S5_NOTE/REGISTRATION_TJ0192_NOTE '
                                              '先例）',
                                              '父级在应用批 PR '
                                              '合并时同步执行以上四项；应用批子任务不得自行改 cicd '
                                              '钉或 live 快照']}}

PUA_FULL_VERIFICATION = {'gate': '应用批 phase 0（阶段一启动前置，fail-hard F10）',
 'requirement': '86/86 码位逐一见证复核并登记：逐码位 {codepoint, replacement, 见证出处（独立见证 '
                'repo@commit + 位点）, 复核结论}；U+E7E8 语境映射逐规则（4 规则 / 5 处）锚点复核',
 'measured_coverage_now': {'audit_file_status_field': False,
                           'audit_file_note': 'sanming_pua_audit.json 的 '
                                              'glyphs 86 条只有 '
                                              'codepoint/contexts/count/glyph '
                                              '字段，无逐码位裁定状态字段——「全 confirmed」只是 '
                                              'collation JSON summary '
                                              '的流水线自述（审源 §7 在案）',
                           'public_register_citations': 32,
                           'public_register_citations_note': '公开登记模块（bazi_sanming_*.py '
                                                             '+ '
                                                             'bazi_dayun_collation.py）中被逐处引用过的码位 '
                                                             '32/86——这是复核覆盖的上界（引用不等于逐一复核完成）',
                           'zero_citation_codepoints': ['U+E10C',
                                                        'U+E37B',
                                                        'U+E3D0',
                                                        'U+E3E5',
                                                        'U+E5AB',
                                                        'U+E7B5',
                                                        'U+E7E9',
                                                        'U+E87D',
                                                        'U+E880',
                                                        'U+E9C7',
                                                        'U+E9FC',
                                                        'U+EA1F',
                                                        'U+EA23',
                                                        'U+EA3F',
                                                        'U+EA43',
                                                        'U+EA5B',
                                                        'U+EA62',
                                                        'U+EA7B',
                                                        'U+EA7C',
                                                        'U+EA7D',
                                                        'U+EA9F',
                                                        'U+EAA7',
                                                        'U+EAC0',
                                                        'U+EAE6',
                                                        'U+EAF6',
                                                        'U+EB8E',
                                                        'U+EBA5',
                                                        'U+EBB8',
                                                        'U+EBC1',
                                                        'U+EBDB',
                                                        'U+ECA6',
                                                        'U+ECC7',
                                                        'U+ECCA',
                                                        'U+ECD6',
                                                        'U+ECDE',
                                                        'U+ECE6',
                                                        'U+ECEC',
                                                        'U+ED94',
                                                        'U+ED9E',
                                                        'U+EDE6',
                                                        'U+EE60',
                                                        'U+EE6D',
                                                        'U+EEA1',
                                                        'U+EEA3',
                                                        'U+EEB8',
                                                        'U+EEE4',
                                                        'U+EEE5',
                                                        'U+EF17',
                                                        'U+EF33',
                                                        'U+EF3F',
                                                        'U+EF67',
                                                        'U+EF6A',
                                                        'U+EF6B',
                                                        'U+EF6C'],
                           'zero_citation_count': 54},
 'why_full_not_sample': '应用使每条映射的读法成为全部下游坐标与订正的前提；524 处总量在全核可行的规模内；抽核口径无法给 F2 '
                        '计数校验提供逐码位责任主体'}

CONTEXT_CARRY_SPEC = {'population': 'context_anchor_class == unanchorable_crosses_boundary 的 76 '
               '条（位点 76/76 全部可锚，缺的只是 context 级快照区间）',
 'authority': '逐条清单以 bazi_sanming_reanchor 登记册 entries 为准（本登记册只登聚合与规约，不复制 993 '
              '条）',
 'by_kind': {'partial_overlap': 52, 'contained_within': 24},
 'partial_overlap_seq': [56,
                         97,
                         104,
                         105,
                         111,
                         112,
                         113,
                         129,
                         145,
                         146,
                         156,
                         169,
                         176,
                         210,
                         228,
                         334,
                         364,
                         372,
                         409,
                         423,
                         439,
                         448,
                         449,
                         450,
                         457,
                         470,
                         476,
                         518,
                         626,
                         705,
                         719,
                         741,
                         746,
                         755,
                         756,
                         772,
                         794,
                         795,
                         800,
                         814,
                         835,
                         872,
                         893,
                         899,
                         934,
                         935,
                         947,
                         954,
                         956,
                         966,
                         967,
                         983],
 'contained_within_seq': [64,
                          65,
                          231,
                          232,
                          233,
                          234,
                          347,
                          348,
                          362,
                          434,
                          435,
                          436,
                          437,
                          762,
                          797,
                          798,
                          799,
                          827,
                          942,
                          959,
                          960,
                          981,
                          985,
                          986],
 'by_status': {'historical_only_hold': 40,
               'variant_preserve': 6,
               'confirmed_applied': 29,
               'reading_disagreement_hold': 1},
 'by_volume': {'2': 10,
               '3': 5,
               '4': 6,
               '5': 16,
               '6': 4,
               '7': 1,
               '8': 2,
               '9': 5,
               '10': 10,
               '11': 5,
               '12': 12},
 'rules': [{'id': 'C1',
            'rule': '76 条逐条进入应用报告 candidate_annex：{seq, status, 位点 S0→S3 映射（经 '
                    'origin 图）, 基线 context 逐字 + 其基线区间, S3 重取 '
                    'context（以映射位点为中心、按登记 site_in_context 的左右外延同形重建窗口）, '
                    'context_final_sha256, 位点在 S3 的实际字 site_state_in_S3}'},
           {'id': 'C2',
            'rule': 'contained_within 24 条另加 context_edit_relation 字段：点名消费其 '
                    'context 的订正 id（以登记册 context_edits_crossed '
                    '为准），并逐条注明其历史读法在 S3 中是保留、被该订正取代、还是与订正正交；不得静默合并'},
           {'id': 'C3',
            'rule': '76 条中的 confirmed_applied 29 条随其 correction_id 核销：S3 重取 '
                    'context 必须呈现订正后读法，不符即 F8'},
           {'id': 'C4',
            'rule': '重取失败（位点映射歧义等）只能显式登记为 context_carry_limitations '
                    '条目并逐条说明原因，禁止静默丢弃；limitations 条数必须写入应用批台账事件（按构造预期为 '
                    '0，但逃生口必须存在且响亮）'},
           {'id': 'C5',
            'rule': '基线文本 S2 以检查点哈希（db8618c9…）作为证据保留机制：不另存密封文件，任一后续批次可由 444 '
                    '前缀复放逐字重建并验哈希'}]}

CANDIDATE_DISPOSITION_SPEC = {'confirmed_applied': {'count': 159,
                       'rule': 'correction_id 恰为 '
                               'ocr-445..603，随阶段二全量应用逐条核销，附件中逐条对账（id、位点、S3 '
                               '读法）'},
 'variant_preserve': {'count': 47,
                      'rule': '应用批不处置其读法；其异文登记（S3 '
                              '坐标）属应用批之后的终局化批（PROMOTION_INTERFACE P1）'},
 'historical_only_hold': {'count': 775,
                          'rule': '同上：历史读法定位登记属终局化批；应用批附件只携带其中 76 条 context '
                                  '跨界者的 context（C1）'},
 'reading_disagreement_hold': {'count': 12,
                               'rule': '应用批不改其位点字（A6 验收逐字核对 S3 位点字 == 快照 '
                                       'old）；互校路线见 READING_DISAGREEMENT_SPEC'}}

RESIDUAL_FANG_ROUTE = {'measured': {'snapshot_occurrences': 1606,
              'removed_net_by_corrections': 837,
              'residual_in_S3': 769,
              'distinct_pm6_contexts_in_S3': 769,
              'workload_conclusion': '769 处残余「防」在 S3 中的 ±6 字局部语境 769 '
                                     '个全互异——不存在可批量合并的同文重复，逐处互校的最小工作单元就是 769'},
 'established_finding': '「防」是多源汇讹字（审源定案：「防代煞」已证伪，无全局替换规则）；全局替换永久禁用',
 'disposition_kinds': ['confirmed_reading（≥2 '
                       '独立见证、含至少一纸本谱系见证，逐处以校勘记形制登记：原文/拟读/依据/等级）',
                       'variant_parallel（谱系异文并列，不择一）',
                       'hold（证据不足，保留「防」字面并登记未决）'],
 'route': ['需求面优先：后续登记/场景批次消费到的节先行处置（沿 018-A..G 逐节校勘形制：018-F 两节处置防 49 处、018-G '
           '处置 15 处为已行先例）',
           '其余按卷序以残余防归因批序列推进，逐批登记 disposed/769 进度于台账',
           '完成判据 = 769/769 全部有登记处置（处置不等于改字：hold 与并列都是终局处置）',
           '坐标纪律：残余防定义在 S3 上；快照坐标的既有校勘记经 origin 图映射，不得在两套坐标间直接套用偏移',
           '与订正层的互动：未来若某处残余防获得 confirmed '
           '订正，订正只经新的应用版本（v2）进入，处置登记以订正事件追加、不改旧登记']}

READING_DISAGREEMENT_SPEC = {'items': [{'seq': 361,
            'volume': 5,
            'basis_offset': 157778,
            'old': '防',
            'historical_reading': '㸔',
            'site_anchor_class': 'anchored_direct',
            'context_anchor_class': 'anchored_direct'},
           {'seq': 385,
            'volume': 5,
            'basis_offset': 164132,
            'old': '防',
            'historical_reading': '䕃',
            'site_anchor_class': 'anchored_direct',
            'context_anchor_class': 'anchored_direct'},
           {'seq': 450,
            'volume': 5,
            'basis_offset': 184317,
            'old': '防',
            'historical_reading': '䕶',
            'site_anchor_class': 'anchored_direct',
            'context_anchor_class': 'unanchorable_crosses_boundary'},
           {'seq': 612,
            'volume': 7,
            'basis_offset': 228260,
            'old': '防',
            'historical_reading': '㿀',
            'site_anchor_class': 'anchored_direct',
            'context_anchor_class': 'anchored_direct'},
           {'seq': 616,
            'volume': 7,
            'basis_offset': 228868,
            'old': '防',
            'historical_reading': '䖝',
            'site_anchor_class': 'anchored_direct',
            'context_anchor_class': 'anchored_direct'},
           {'seq': 784,
            'volume': 10,
            'basis_offset': 362057,
            'old': '胤',
            'historical_reading': '𦙍',
            'site_anchor_class': 'anchored_direct',
            'context_anchor_class': 'anchored_direct'},
           {'seq': 824,
            'volume': 10,
            'basis_offset': 374131,
            'old': '防',
            'historical_reading': '㫁',
            'site_anchor_class': 'anchored_direct',
            'context_anchor_class': 'anchored_direct'},
           {'seq': 853,
            'volume': 10,
            'basis_offset': 386724,
            'old': '着',
            'historical_reading': '著',
            'site_anchor_class': 'anchored_direct',
            'context_anchor_class': 'anchored_direct'},
           {'seq': 873,
            'volume': 11,
            'basis_offset': 395586,
            'old': '防',
            'historical_reading': '㕓',
            'site_anchor_class': 'anchored_direct',
            'context_anchor_class': 'anchored_direct'},
           {'seq': 880,
            'volume': 11,
            'basis_offset': 398647,
            'old': '玄',
            'historical_reading': '𤣥',
            'site_anchor_class': 'anchored_direct',
            'context_anchor_class': 'anchored_direct'},
           {'seq': 931,
            'volume': 11,
            'basis_offset': 423247,
            'old': '着',
            'historical_reading': '著',
            'site_anchor_class': 'anchored_direct',
            'context_anchor_class': 'anchored_direct'},
           {'seq': 933,
            'volume': 11,
            'basis_offset': 423786,
            'old': '防',
            'historical_reading': '䕶',
            'site_anchor_class': 'anchored_direct',
            'context_anchor_class': 'anchored_direct'}],
 'items_summary': {'volumes': {'5': 3, '7': 2, '10': 3, '11': 4},
                   'old_chars': {'防': 8, '着': 2, '胤': 1, '玄': 1},
                   'site_anchor': '12/12 anchored_direct',
                   'context_anchor': '11 anchored_direct + 1 '
                                     'unanchorable_crosses_boundary（seq 450）',
                   'correction_id': '12/12 均为 null（无 confirmed 订正，应用批不改字）'},
 'witness_lineages': [{'lineage': '四库谱系',
                       'witnesses': [{'repo': 'kanripo/KR3g0042',
                                      'commit': 'efe780a4f6fd835f4e2d769ffc8f79b7099db3b1'},
                                     {'repo': 'mikkokotila/Sanming-Tongshui',
                                      'commit': 'eb3cacbf4b41a4fe8fc3c0e77e0d12b5bd17c079'}],
                       'reading': '12 条的 '
                                  'historical_reading（㸔/䕃/䕶/㿀/䖝/𦙍/㫁/著/㕓/𤣥/著/䕶）',
                       'independence_note': '两见证同属四库全书转录谱系，互校口径下计为一个谱系、不是两份独立见证（同 '
                                            'TJ-017.1 神峰先例：同一数字谱系不构成独立刊本见证）'},
                      {'lineage': '现代转录谱系',
                       'witnesses': [{'repo': 'NiuTrans/Classical-Modern',
                                      'commit': '4e746ea9fa99c3c0d7051c45397330bef7b0962d'},
                                     {'repo': 'youngzs/xuanxue',
                                      'commit': 'aa7bc942602d2d88ef94778a726c0d19a4d286ff'},
                                     {'repo': 'michiboo/Classical_Chinese_Wikisource',
                                      'commit': '5acdca0628a0cb664858a0280b23488c194445e3'}],
                       'reading': '逐条 observed 异字（者/业/获/癍/茧/嗣/体/者/厘/元/者 等）',
                       'independence_note': '三家之间的谱系独立性须逐条核实不得假设：维基文库源出影印传统、NiuTrans/youngzs '
                                            '为网络转录；未核实前整组计为一个现代谱系簇'}],
 'decision_standard': ['可采纳（择一）当且仅当：(a) 出现与两簇均独立的第三谱系见证（纸本影印或独立刊本系统）证实其一，或 '
                       '(b) 逐条内证（文义、对文、韵律、术语一致性）决定性成立并逐条登记理由',
                       '不满足上条 → 异文并列登记（既有口径：传本异文并列，TJ-017.1 #4 '
                       '先例），应用文本保留快照字（old）',
                       '逐条独立判定，禁止以一条的结论类推其余（12 条分属㸔/䕃/䕶/病字/名物/虚字等不同性质）'],
 'item_notes': {'seq450': '防（四库作䕶）/现代作获：「所以䕶禄」与「所以获禄」两读文义皆可通，内证不显然，预期并列；且其 '
                          'context 恰为 76 条跨界者之一（C2 携带）',
                'seq880': '玄：三方三读——四库作𤣥（玄之异体）、快照作玄、现代作元；属字形异文类，与 TJ-017.1 清单 '
                          '#5 的 EA20「玄」是不同对象，不混同',
                'seq784': '胤：四库作𦙍（异体），现代作嗣（语义替换读法），性质与其余不同',
                'seq853_931': '着：四库作著，现代（NiuTrans）作「者」疑转录讹——内证较强，但仍须逐条登记后才可采纳'},
 'default_disposition': '并列登记、快照字保留——此路径不需要用户裁定；用户级裁定只在未来 canonical '
                        '文本要求单一读法时发生（UD-1）'}

PERMANENT_GAPS = {'items': [{'from': '谬□甚矣',
            'proposed_reading': '谬误甚矣',
            'status': 'needs_base_text_evidence_do_not_apply',
            'evidence_type': 'github-crosscheck',
            'evidence_repo': 'shuaige121/sinan-app',
            'evidence_url': None,
            'evidence_anchor': '阴阳间隔，谬误甚矣。'},
           {'from': '王麟洲少□',
            'proposed_reading': '王麟洲少卿',
            'status': 'needs_base_text_evidence_do_not_apply',
            'evidence_type': 'authority-crosscheck',
            'evidence_repo': None,
            'evidence_url': 'https://data.ascdc.tw/dnb/Agent/NO000018454',
            'evidence_anchor': None}],
 'carrying_rule': '应用批在 S1/S2/S3 中逐字保留 □（实测三阶段 □ 恒为 2），并在应用报告中以 '
                  'permanent_gaps 字段原样登记两条 manifest 记录；proposed_reading '
                  '只作提案字段携带，永不进入应用文本',
 'evidence_state': '两条提议读法（谬误、少卿）的现有证据均非底本证据：一为现代转述本（sinan-app '
                   '释读）、一为人物履历旁证；两家四库转录见证均保留 □',
 'blocking_scope': '只阻断整书 canonical 晋级（TJ-018.3 决策包中明示），不阻断应用批、不阻断逐节晋级',
 'reopening_condition': '出现底本级新证据（四库影印原叶或独立刊本同位文字）时以订正事件重开，除此之外永久缺口即终局处置'}

FREEZE_REGISTRATION = {'freeze_point': '本设计批合并（E0294）即冻结时点',
 'anchors': '五件冻结对象的文件级 SHA256（FREEZE_REGISTER）+ 三阶段文本哈希（STAGE_TEXT_PINS）+ 密封 '
            'manifest 三元组（235 文件 / 13580501 字节 / e5a590b4…）',
 'version_correspondence': 'S0 快照哈希 ↔ PUA JSON 哈希 ↔ 文本订正 JSON 哈希 ↔ 候选 JSON 哈希 '
                           '↔ 基线 blob e6dab2c5（候选文件 baseline '
                           '字段）构成一组版本对应，任一环再生成即整组失效',
 'drift_rule': '冻结后流水线侧任一再生成 → 应用批开工 F1 '
               '必失败；须先以订正事件更新本登记册钉值（附再生成说明）才可重新冻结，禁止应用批现场自行换钉',
 'scope_note': '冻结只及三命五件；快照内其他作品不在本冻结范围，其变动经 manifest 三元组在 F1 一并检出'}

PROMOTION_INTERFACE = {'closed_by_application_batch': ['两阶段正式应用与应用报告（S3 + 报告 + 附件）',
                                 'PUA 全核 86/86（phase 0）',
                                 '159 条 confirmed_applied 核销',
                                 '76 条 context 携带（CONTEXT_CARRY_SPEC）',
                                 '缺口 2 处永久缺口登记（应用报告内）',
                                 '版本对应登记更新（应用版本入 manifest）'],
 'remaining_after_application': [{'id': 'P1',
                                  'item': '993 终局化登记（余量）',
                                  'detail': 'variant_preserve 47 条异文登记 + '
                                            'historical_only_hold 775 '
                                            '条历史读法定位登记，坐标换算至 S3；独立终局化批，复用应用批 '
                                            'origin 图'},
                                 {'id': 'P2',
                                  'item': '残余「防」769 处处置',
                                  'detail': 'RESIDUAL_FANG_ROUTE 的多批路线；完成判据 '
                                            '769/769 有登记处置'},
                                 {'id': 'P3',
                                  'item': 'RD-12 见证互校批',
                                  'detail': '按 READING_DISAGREEMENT_SPEC '
                                            '标准逐条互校；预期产出以并列登记为主；只有要求单一读法时才触发 '
                                            'UD-1'},
                                 {'id': 'P4',
                                  'item': 'TJ-018.3 决策包与台账裁定',
                                  'detail': '汇总应用报告、P1–P3 状态、383 '
                                            '条逐节校勘记与永久缺口，向 TJ-018.3 '
                                            '验收口径（每审核场景独立 '
                                            'Source/Section/Term/Rule/Evidence/Golden、整书保留审批红线）逐项对账后裁定'}],
 'design_position_whole_book': '即使 P1–P4 全数完成，本设计也不建议把整书 canonical_ready 翻为 '
                               'true：WBS TJ-018.3 '
                               '的验收形制是逐场景/逐节的审批，整书晋级与之不合；逐节晋级路径（已登记节各自走 '
                               'Source/Section/Term/Rule/Evidence/Golden）是唯一推荐路径（审定点 '
                               'AP6，决策权在 P4 与 UD-3）',
 'user_decisions': [{'id': 'UD-1',
                     'question': 'RD-12 若未来 canonical 文本要求单一读法，采用何种读法？',
                     'options': ['A 并列登记、保留快照字（默认，本设计的处置即此，无需现在裁定）',
                                 'B 全批采四库谱系读法',
                                 'C 互校批逐条报告后逐条裁定'],
                     'needed_now': False,
                     'design_recommendation': 'A 为默认；若需择一则走 C，不走 '
                                              'B（一揽子择一与逐条证据口径冲突）',
                     'adjudication': {'status': 'decided',
                                      'date': '2026-10-30',
                                      'decided_by': '用户',
                                      'option_chosen': 'A',
                                      'basis': 'P4 决策包（E0326）UD-1 呈请节正式呈请后裁定，全采设计建议',
                                      'registration_event': 'E0327',
                                      'effect': 'RD-12 十二条维持并列登记、保留快照字，不选单一读法；不执行 '
                                                'B（全批采四库谱系读法）、不执行 C（互校批逐条报告后逐条裁定）。P3 互校登记册'
                                                '（sanming-reading-disagreement-collation-register-v1）12 条 outcome 的并列待裁定形态就此定格为'
                                                '「已裁定：并列保留」：该登记册条目作为互校批当时的记录逐字保留，其终局效力由本裁定赋予，不回改其字面。无任何改字、无 '
                                                'v2 应用批、无执行批；未来出现判定标准 (a) 第三谱系见证或 (b) 决定性内证时，仍得以订正事件逐条重开'}},
                    {'id': 'UD-2',
                     'question': '缺口 2 处的提议读法（谬误甚矣、王麟洲少卿）是否采纳补字？',
                     'options': ['A 保留 □ 为永久缺口（默认，本设计的处置即此）',
                                 'B 以现有非底本证据采纳提议读法'],
                     'needed_now': False,
                     'design_recommendation': 'A；B 的证据等级（现代转述 + '
                                              '人物履历旁证）不足以改底本',
                     'adjudication': {'status': 'decided',
                                      'date': '2026-10-30',
                                      'decided_by': '用户',
                                      'option_chosen': 'A',
                                      'basis': 'P4 决策包（E0326）UD-2 呈请节正式呈请后裁定，全采设计建议',
                                      'registration_event': 'E0327',
                                      'effect': '缺口 2 处（谬□甚矣、王麟洲少□；S3 位点 42148 与 318327）保留 □ 为永久缺口，提议读法（谬误甚矣、王麟洲少卿）不补入任何文本，维持审定点 '
                                                'AP4 与 PERMANENT_GAPS 登记原样；不执行 B（以现有非底本证据采纳提议读法）；无执行批、无文本变更。出现底本级新证据时按 PERMANENT_GAPS '
                                                '的 reopening_condition 以订正事件重开'}},
                    {'id': 'UD-3',
                     'question': 'TJ-018.3 决策包阶段，整书晋级采用何种姿态？',
                     'options': ['A 只走逐节晋级、整书 canonical_ready 保持 false（本设计立场）',
                                 'B P1–P4 全完成后整书翻 true'],
                     'needed_now': False,
                     'design_recommendation': 'A；此项在 P4 决策包时再正式呈请',
                     'adjudication': {'status': 'decided',
                                      'date': '2026-10-30',
                                      'decided_by': '用户',
                                      'option_chosen': 'A',
                                      'basis': 'P4 决策包（E0326）UD-3 呈请节正式呈请后裁定，全采设计立场',
                                      'registration_event': 'E0327',
                                      'effect': '整书只走逐节晋级，canonical_ready 保持 false；不执行 B（P1–P4 全完成后整书翻 true）。Term/Rule/Evidence/Golden 逐节建立为后续独立批次，本裁定不启动任何逐节晋级、不建立任何规则面；审定点 AP6 的逐节路径设计立场经用户裁定确认'}}]}

APPLICATION_ACCEPTANCE_RECIPE = [{'id': 'A1',
  'check': '冻结校验',
  'expected': '五件冻结对象 SHA256 与 FREEZE_REGISTER 逐一相等；密封 manifest 三元组 == 235 / '
              '13580501 / e5a590b4…'},
 {'id': 'A2',
  'check': '阶段一报告',
  'expected': '86 映射 / 524 处全应用、PUA 残留 0、S1 哈希 == b4f196f2…；PUA 全核登记 86/86 '
              '在案（F10 已过）'},
 {'id': 'A3',
  'check': '444 检查点',
  'expected': 'ocr-444 应用毕中间文本哈希 == S2 钉值 db8618c9…（与 E0273 重锚登记册逐字对账）'},
 {'id': 'A4',
  'check': '阶段二与终局扫描',
  'expected': '603/603 应用、逐条记录完备、豁免使用集 == {ocr-022}、S3 哈希 == a89c0b5d…、PUA '
              '0、防 769、□ 2'},
 {'id': 'A5',
  'check': '往返校验',
  'expected': 'origin 图逆复放恢复 S0 哈希 == 00e2a7db…，且逆行至 444 点 == db8618c9…；校验方法为 '
              'origin 图（朴素逆替换禁用，AP3）'},
 {'id': 'A6',
  'check': '附件完备性',
  'expected': '993 处置逐条在案；159 核销逐条对账；76 条 context 携带齐全（limitations 逐条列明、预期 '
              '0）；RD-12 位点字在 S3 与快照 old 逐字相同（12/12）；缺口 □ 两处原位在 S3 可定位'},
 {'id': 'A7',
  'check': '回归与全量验收',
  'expected': '既有登记逐字不变（校勘记三册累计 383 条、零匹配归因册、重锚册及其密封专项全过）；机上完整复跑 SUCCESS '
              '且与同环境基线对账（新增计数逐项说明）；公开 CI 全绿；台账门禁双模式 PASS'}]

ADJUDICATION_POINTS = [{'id': 'AP1',
  'point': '应用批形态取单批两阶段，不按 018-H 路线备忘第 2/3 步拆为两个独立批',
  'rationale': '文本阶段的输入按构造就是阶段一输出（脚本以禁 PUA 强制此序），S1 与 S0 '
               '位置恒等且无独立消费方；拆批只会多出一次冻结/换代同步而不增加任何有意义的检查点——有意义的检查点是 S2（444）与 '
               'S3，已在单批内设双钉。备忘的两步在单批内完整保留为两阶段'},
 {'id': 'AP2',
  'point': 'PUA 复核口径取全核 86/86，不取抽核',
  'rationale': '实测覆盖上界仅 32/86 有登记引用、54/86 零引用，且审计文件无逐码位状态字段；应用使读法成为承重前提；524 '
               '处规模全核可行'},
 {'id': 'AP3',
  'point': '往返校验只认 origin 图方法，朴素逆替换禁用',
  'rationale': '统一映射逆向多义 + ocr-022 目标预存豁免证明朴素逆替换必然产生假信号；origin 图机械已在 E0273 对 '
               '444 前缀证明可行'},
 {'id': 'AP4',
  'point': '缺口 2 处以永久缺口登记为终局处置，提议读法不应用',
  'rationale': '两条提议的证据均为非底本证据，两家四库转录见证均保留 □；改底本的证据门槛不满足'},
 {'id': 'AP5',
  'point': '附件完备性与文本应用同级 fail-hard（F8），零部分应用含附件',
  'rationale': '76 条 context '
               '若不随批携带，应用后其证据面将只剩基线中间态可寻，处置成本随时间上升；同批携带是唯一不丢证据的时点'},
 {'id': 'AP6',
  'point': '整书 canonical_ready 不建议翻 true（逐节路径为唯一推荐）',
  'rationale': 'WBS TJ-018.3 验收形制为逐场景独立审批 + 整书保留审批红线；本点为设计立场登记，决策权在 '
               'P4/UD-3，本批不代决'}]

SEALED_MEASUREMENTS = {'method': '2026-10-29 机上只读内存复放（仓库脚本全语义：逐码位计数断言、语境锚串恰 1 次、文本锚串恰 1 次 + '
           '目标预存校验），不落盘、不写任何密封资产',
 'snapshot': {'bytes': 1342659,
              'chars': 461157,
              'sha256': '00e2a7db8bb59b259b99938033bb1bb77947e04a15dafc111e62b59378010c86',
              'pua_occurrences': 524,
              'pua_codepoints': 86,
              'fang': 1606,
              'gap_square': 2},
 'stage1': {'applied_occurrences': 524,
            'chars': 461157,
            'bytes': 1342685,
            'sha256': 'b4f196f2100347618d7907330b2db93bd536a5663f16249a6e0ff19e23c05daa',
            'pua': 0,
            'fang': 1606},
 'baseline_444': {'chars': 461156,
                  'sha256': 'db8618c9cdbc545b59149f7550644a440fdf8bba8ddbe0e23b615029f8a896d9',
                  'fang': 925,
                  'pua': 0,
                  'cross_check': '与重锚登记册钉值逐字一致（该值已由 E0273 证明与仓库脚本实际输出等值）'},
 'final_603': {'chars': 461156,
               'bytes': 1342682,
               'sha256': 'a89c0b5da16ea4e07dc85180c49135ed280875318059f923ff7154f2c217662f',
               'pua': 0,
               'fang': 769,
               'gap_square': 2,
               'fang_distinct_pm6_contexts': 769},
 'collation_counts': {'snapshot_direct_match': {'exactly_once': 537,
                                                'zero': 66,
                                                'multiple': 0},
                      'fang_in_old': 897,
                      'fang_in_new': 60,
                      'fang_net': -837},
 'candidate_counts': {'total': 993,
                      'historical_only_hold': 775,
                      'variant_preserve': 47,
                      'confirmed_applied': 159,
                      'reading_disagreement_hold': 12,
                      'confirmed_id_set_equals_ocr_445_603': True},
 'collation_registers_entries': {'juan2_group': 160,
                                 'juan5_group': 151,
                                 'juan6_group': 72,
                                 'total': 383}}

DESIGN_LIMITATIONS = ['本批零应用：S3 哈希 a89c0b5d… '
 '是内存复放的实测钉值，不是已登记的应用产物；应用批若在冻结校验（F1）下复放得不同哈希，即证明输入漂移，须按冻结漂移规则处理，不得现场换钉',
 'PUA 全核未做：54/86 码位在本批之前零登记引用，本批只登记缺口与门规约，不代做复核',
 'RD-12 互校未做：本批只登记 12 条与互校标准，逐条结论属 P3 互校批',
 '残余防 769 的逐处处置未做：本批只给路线与完成判据',
 'S2 字节数未单独实测（S2 不作独立工件登记，只以字数 + 哈希为钉）',
 '本设计不产出任何命理判定，不改变任何既有登记、候选状态语义与 TJ-018.2/TJ-018.3 的台账状态']
