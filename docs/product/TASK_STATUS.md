# 天机平台｜逐任务状态登记表

> **唯一状态源**，对应[详细 WBS](DETAILED_DELIVERY_BACKLOG_V1.md)与[执行制度](TASK_EXECUTION_RULES.md)。任务详细范围和独立验收标准不在本表重复，以 WBS 原行与 PR 的真实测试为准。  
> 初始建立：2026-10-11，**93 项原子子任务**。历史已合并项基于真实 PR 回填；所有未完成项不得擅自提升状态。  
> 状态日志：[TASK_HISTORY.md](TASK_HISTORY.md)；父级阶段汇总：[EXECUTION_LEDGER.md](EXECUTION_LEDGER.md)。  
> 每次修改**一批次（2–6 个）任务 ID**的状态/证据并新增对应历史事件（批次见 TASK_EXECUTION_RULES.md §7）事件（首次基线建表例外）。任务名称与 WBS 一致，不允许同 ID 多次定义。

| 任务 ID | 阶段 | 原子任务及交付 | 当前状态 | PR/证明或进展 | 最近更新 | 下一动作 |
| --- | --- | --- | --- | --- | --- | --- |
| TJ-001.1 | M0 | 冻结 11 生活、7 专业、16 后台原设计的视觉和 IA 基线 | 已合并 | [公开 #221](https://github.com/HelloMrDuan/tianji-knowledge-base/pull/221) · `07165cc` | 2026-10-11 | 已合并；父任务继续 |
| TJ-001.2 | M0 | 按页输出交互/输入/结果/证据/异常状态规格 | 已合并 | [公开 #221](https://github.com/HelloMrDuan/tianji-knowledge-base/pull/221) · `07165cc` | 2026-10-11 | 已合并；父任务继续 |
| TJ-001.3 | M0 | 首页 README、执行台账与规范互联 | 已合并 | [公开 #221](https://github.com/HelloMrDuan/tianji-knowledge-base/pull/221) · `07165cc` | 2026-10-11 | 已合并；父任务继续 |
| TJ-001.4 | M0 | 一任务一闭环：建立 92 个原子子任务的状态登记、不可改写完成日志与 PR 门禁 | 已合并 | [公开 #228](https://github.com/HelloMrDuan/tianji-knowledge-base/pull/228) · `6a22f29f2ec2e0b3a2bd9689c0dd9df5fd3d883d` · [4 项检查通过](https://github.com/HelloMrDuan/tianji-knowledge-base/actions/runs/38101246241) | 2026-10-11 | 本任务结账；下一任务按状态表独立认领 TJ-004.3 |
| TJ-001.5 | M0 | 批次开发门禁：多任务一批次的状态登记、事件追加与 PR 门禁 | 已合并 | [公开 #303](https://github.com/HelloMrDuan/tianji-knowledge-base/pull/303) | 2026-10-25 | #303 已合并（Merge SHA 71b50049a31ff152dc5592ef34815695e04341b1）；批次门禁（BATCH_MIN_TASKS 等）已在主干运行；本行为台账滞后补关账 |
| TJ-001.6 | M0 | 离线受控验收工具：不依赖私有 Actions 的知识验收 | 进行中 | [公开 #306](https://github.com/HelloMrDuan/tianji-knowledge-base/pull/306) | 2026-10-22 | 工具已提交 PR；待公开 CI 全绿与可信机器实测 |
| TJ-002.1 | M0 | 核对私有 #50 两条完整组合回归 | 已合并 | [私有 #50](https://github.com/HelloMrDuan/tianji-private-knowledge/pull/50) · `e0f9505` | 2026-10-11 | 已合并；父任务继续 |
| TJ-002.2 | M0 | 合并 #50，核对私有 main、补回执 | 已合并 | [私有 #50](https://github.com/HelloMrDuan/tianji-private-knowledge/pull/50) · `e0f9505` | 2026-10-11 | 已合并；父任务继续 |
| TJ-003.1 | M0 | 分区盘点公开 HEAD/历史中的内容、许可证、原文派生文件 | 待做 | — | — | 按 WBS 验收条件执行 |
| TJ-003.2 | M0 | 核对私有 235 文件逐文件 hash/证据/服务端隔离 | 待做 | — | — | 按 WBS 验收条件执行 |
| TJ-003.3 | M0 | public API/bundle/错误/日志泄漏红线测试 | 待做 | — | — | 按 WBS 验收条件执行 |
| TJ-004.1 | M0 | 获取 11 场景的全部现行路由/入参与真实 API | 已合并 | [公开 #224](https://github.com/HelloMrDuan/tianji-knowledge-base/pull/224) · [私有 #51](https://github.com/HelloMrDuan/tianji-private-knowledge/pull/51) | 2026-10-11 | 已合并；父任务继续 |
| TJ-004.2 | M0 | 真实受控后端逐场景正向计算 | 已合并 | [公开 #225](https://github.com/HelloMrDuan/tianji-knowledge-base/pull/225) · [私有 #52](https://github.com/HelloMrDuan/tianji-private-knowledge/pull/52) | 2026-10-11 | 已合并；父任务继续 |
| TJ-004.3 | M0 | 逐场景无效值/无证据/超时/重复提交负例 | 已合并 | [公开 #234](https://github.com/HelloMrDuan/tianji-knowledge-base/pull/234) merge `283557b3e595ee8dc80be31b809a0a4315db8fa0` · [私有 #56](https://github.com/HelloMrDuan/tianji-private-knowledge/pull/56) merge `99218de320468f3cddf3858c0a9b4cb6ea590b08` · [专项 24/24 真实 Chromium](https://github.com/HelloMrDuan/tianji-private-knowledge/actions/runs/38110293680) · 公开四门禁 success | 2026-10-11 | 本批 11 场景缺字段/年界及网络超时、重复、无证据、旧响应验证已完成；TJ-004.4 原图差异仍待执行 |
| TJ-004.4 | M0 | 逐场景对照 PR #87/#89 截图并出差异清单 | 已合并 | [公开 #237](https://github.com/HelloMrDuan/tianji-knowledge-base/pull/237) merge `ff9e9d11908cd27155b00cfb6595b224c5d06b98` · 公开四门禁 success（https://github.com/HelloMrDuan/tianji-knowledge-base/actions/runs/38534526334） · 私有 main `99218de320468f3cddf3858c0a9b4cb6ea590b08` 未动（本任务无私有变更） · 差异台账 v2 + 42 张截图 + 可复现脚本已入库 | 2026-10-14 | 审计交付完成；结果态比对缺口保留待后端；双主题实现另立独立任务 |
| TJ-005.1 | M0 | 确认私有制品生成/部署路径和网关限制 | 待做 | — | — | 按 WBS 验收条件执行 |
| TJ-005.2 | M0 | 前端静态包/真实接口/权限/HTTPS 冒烟 | 已合并 | [公开 #330](https://github.com/HelloMrDuan/tianji-knowledge-base/pull/330) | 2026-10-25 | #330 已合并；冒烟套件（组装复用+CI 接线+权限冒烟）已在主干；仅本地受控冒烟，不含真实域名 HTTPS，不冒充生产部署 |
| TJ-005.3 | M0 | 备份、回滚、健康检测、部署文档 | 待做 | — | — | 按 WBS 验收条件执行 |
| TJ-006.1 | M1 | 多场景统一输入与本地资料校验 | 已合并 | [公开 #243](https://github.com/HelloMrDuan/tianji-knowledge-base/pull/243) merge `8a0081990bb442fb3521bbd2140056901fe14eed` · [4 项 CI success](https://github.com/HelloMrDuan/tianji-knowledge-base/actions/runs/38692470766) · 本地 Playwright 55/55（开发方报告；GitHub CI 未执行 Playwright） | 2026-10-15 | 输入与跨场景复用代码已合并；真实后端 E2E 未验，留待 TJ-007.1 独立验证；父任务不结账 |
| TJ-006.2 | M1 | 目标年/日期/边界响应一致 | 已合并 | [公开 PR #247](https://github.com/HelloMrDuan/tianji-knowledge-base/pull/247) merge `8b37521e7c6ab961732479540dfa2fb84f2a7b15` · [真实 Chromium 前端状态 4/4](https://github.com/HelloMrDuan/tianji-knowledge-base/actions/runs/38699429188) · 公开 5/5 CI success · [TJ-007.1 私有真实计算 E2E 35/35](https://github.com/HelloMrDuan/tianji-private-knowledge/actions/runs/38696910589) | 2026-10-15 | 目标日/周/月/流年契约与跨期边界已验收；新增的竞态测试为前端受控响应，非真实命理计算；未生产部署，父任务未关账 |
| TJ-006.3 | M1 | 双人合盘隐私边界 | 已合并 | [功能 PR #249](https://github.com/HelloMrDuan/tianji-knowledge-base/pull/249) merge `7ec43814bdf090d29be02d35dd36e6a5ed74681e` · [真实 Chromium 隐私测试 8/8](https://github.com/HelloMrDuan/tianji-knowledge-base/actions/runs/38701988505) · GitHub CI 6/6 success | 2026-10-15 | B 方独立内存资料及清空、个人资料删除、跨场景与跨标签页同步清理均验收；合盘测试为受控前端请求验证，未宣称真实后端计算或生产部署；父任务未关账 |
| TJ-007.1 | M1 | 八字/今/周/月/年真实流程 | 已合并 | [公开 PR #245](https://github.com/HelloMrDuan/tianji-knowledge-base/pull/245) merge `d80ff176156fbd7a462e5610bc8184253067c9b0` · [私有 PR #57](https://github.com/HelloMrDuan/tianji-private-knowledge/pull/57) merge `b7eab9c16dfb9b9e9e35273207c7e754205ed827` · [公开 CI 4/4](https://github.com/HelloMrDuan/tianji-knowledge-base/actions/runs/38696876573) · [私有真实 E2E 35/35](https://github.com/HelloMrDuan/tianji-private-knowledge/actions/runs/38696910589) | 2026-10-15 | 五场景真实计算、闰月/立春边界、Evidence 引用与 15 张受限截图已验收；未生产部署；旺衰喜忌大运等非本任务范围，后续独立任务继续 |
| TJ-007.2 | M1 | 桃花/事业/合盘真实流程 | 已合并 | [公开 PR #251](https://github.com/HelloMrDuan/tianji-knowledge-base/pull/251) merge `2a75e02e5bc07823158902626c88572bc779c8e4` · [私有验收 PR #58](https://github.com/HelloMrDuan/tianji-private-knowledge/pull/58) merge `caef539d7aad7a38365dcf1c157de7f7dbc71766` · 公开 7/7 CI · [私有真实 E2E 14/14](https://github.com/HelloMrDuan/tianji-private-knowledge/actions/runs/38705064439) | 2026-10-15 | 已审核桃花/事业财运/合盘限定版真实计算与中文展示闭环；私有数据隔离，合盘 A/B 独立，Evidence 引用对应；不宣称完整吉凶预测、旺衰喜用大运或生产部署；父任务未关账 |
| TJ-007.3 | M1 | 一事占问/解梦/人生总览真实流程 | 已合并 | [公开 PR #253](https://github.com/HelloMrDuan/tianji-knowledge-base/pull/253) merge `297727060ef323103012f00957bd96034ea158bc` · [私有 PR #59](https://github.com/HelloMrDuan/tianji-private-knowledge/pull/59) merge `da526cf43bac2375f48835cef71b8cea7f8399b7` · [公开 8/8 CI](https://github.com/HelloMrDuan/tianji-knowledge-base/actions/runs/38708274375) · [私有真实 E2E 14/14](https://github.com/HelloMrDuan/tianji-private-knowledge/actions/runs/38708304212) | 2026-10-15 | 六爻真实盘面/动爻与弃判，梦象已审文化检索/无匹配，人生总览四源真聚合和 Evidence 对照已验收；9 张私有截图；AI 自由解释未授权，非完整吉凶预测，未生产部署，父任务未关账 |
| TJ-007.4 | M1 | 保存/跨页/错误态的统一修复 | 已合并 | [公开功能 PR #255](https://github.com/HelloMrDuan/tianji-knowledge-base/pull/255) merge `0304a55c41ee67d9f72c7e39bfef1a59d68cdc85` · [私有真实验收 PR #60](https://github.com/HelloMrDuan/tianji-private-knowledge/pull/60) merge `c94cd0f7cf17879f0e343ec70a51159e1ca516ec` · [公开 CI 9/9](https://github.com/HelloMrDuan/tianji-knowledge-base/actions/runs/38718130197) · [私有真 API/Chromium 11/11](https://github.com/HelloMrDuan/tianji-private-knowledge/actions/runs/38718147580) · 私有截图 Artifact `11964270529` | 2026-10-15 | 假历史隔离、保存/跨页/重试、超时与响应合同校验和隐私/竞态回归已验收；8 个场景仍仅 production_limited 且 public_release=false，未开放完整吉凶预测；AI 自由解梦仍关闭，未生产部署；其他 WBS 任务继续 |
| TJ-008.1 | M1 | 原始视觉设计冻结与当前差异审计 | 待做 | — | — | 按 WBS 验收条件执行 |
| TJ-008.2 | M1 | 首页视觉忠实恢复：Hero/导航/时间带/11 场景/7 专业 | 已合并 | [公开 #230](https://github.com/HelloMrDuan/tianji-knowledge-base/pull/230) merge `e00137addfd1ddd19d9d7080b13d8095d6b895f3` · [私有 #54](https://github.com/HelloMrDuan/tianji-private-knowledge/pull/54) merge `b529ce61320fd53f6fa088207d88e9dcc9ec72b4` · [真实 8/8 浏览器和截图](https://github.com/HelloMrDuan/tianji-private-knowledge/actions/runs/38106598250)；公开 4 项 CI success | 2026-10-11 | 本首页优先级与响应式修复已合并；全站 11 页面原始视觉对照仍归 TJ-004.4/TJ-008.5 后续验收 |
| TJ-008.3 | M1 | 统一真实结果页的古风版式 | 已合并 | [公开 #232](https://github.com/HelloMrDuan/tianji-knowledge-base/pull/232) `4f00515048d08ee92e998d08cc03a543756cfddc` · [私有 #55](https://github.com/HelloMrDuan/tianji-private-knowledge/pull/55) `5e35a87030c4c6f2b094c24d0bb02d40b74b35ff` · [真实 7/7 浏览器与四张手机版结果截图](https://github.com/HelloMrDuan/tianji-private-knowledge/actions/runs/38109609969)；公开 4 门禁通过 | 2026-10-11 | 四页面可读摘要已验收；其余场景 UI、全站原图/后台、旺衰/大运/预测规则各自仍未完成 |
| TJ-008.4 | M1 | 移动端与无障碍 | 已提交PR | [公开 #342](https://github.com/HelloMrDuan/tianji-knowledge-base/pull/342) | 2026-10-25 | 单独立：移动端与无障碍验证 + 窄视口修复（390/360/768/1440 无溢出；200% 缩放等效 195/180 视口无溢出；键盘 Tab 顺序与焦点可见、Escape；reduced-motion 生效；核心按钮首屏几何 + 最大滚动可达；CSS 补丁仅 min-width:0/换行/窄断点，不改视觉；不碰 008.5） |
| TJ-008.5 | M1 | 对齐原设计视觉验收并固化基线 | 待做 | — | — | 按 WBS 验收条件执行 |
| TJ-008.6 | M1 | 双主题基础与偏好持久化 | 已合并 | [公开 #239](https://github.com/HelloMrDuan/tianji-knowledge-base/pull/239) merge `023543a9c4787333e614e1612321a83de65b21c0` · 公开四门禁 success（https://github.com/HelloMrDuan/tianji-knowledge-base/actions/runs/38542003719） · 私有库无变更 · 主题机制/持久化/切换入口/防闪烁/WCAG AA 对比度门禁已交付 | 2026-10-14 | 仅技术基础；首页精确视觉还原由 TJ-008.7 接续 |
| TJ-008.7 | M1 | 首页深青夜景真实视觉还原（React） | 已合并 | [公开 #241](https://github.com/HelloMrDuan/tianji-knowledge-base/pull/241) merge `f4ff245cacdc74c12b07afe6b5b8b9f0a40fc6fe` · 公开四门禁 success · 私有库无变更 · 11 场景四层架构/深青夜景/宣纸双主题/9 张原创水墨/音乐播放器/手机首屏无遮挡已交付；产品方向锁定于 PRODUCT_MASTER_PLAN_V1.md §3.1 | 2026-10-15 | 用户最终视觉验收通过 |
| TJ-009.1 | M1 | 原创音轨播放器持久化与默认静音 | 待做 | — | — | 按 WBS 验收条件执行 |
| TJ-009.2 | M1 | 进入后台停止音乐、离开后台不擅自重启 | 待做 | — | — | 按 WBS 验收条件执行 |
| TJ-009.3 | M1 | 山水/云雾动效性能与无障碍 | 待做 | — | — | 按 WBS 验收条件执行 |
| TJ-010.1 | M2 | 对照本气、月令/根与异文的每条短引 | 已合并 | [公开功能 PR #257](https://github.com/HelloMrDuan/tianji-knowledge-base/pull/257) merge `2d8c7075a7fda42f5aca55aa1960cea972e421ca` · [私有证据 PR #61](https://github.com/HelloMrDuan/tianji-private-knowledge/pull/61) merge `b970fe68df19bcefd11ecc2c579b2172dc64b6d6` · [公开 CI 10/10](https://github.com/HelloMrDuan/tianji-knowledge-base/actions/runs/38725443092) · [私有来源+真实 Evidence 验收](https://github.com/HelloMrDuan/tianji-private-knowledge/actions/runs/38725488144) | 2026-10-15 | 11 条受影响 Phase2 规则引用的 40 个不同短引及额外三刑异文 s020 原始字符定位、固定电子版 SHA 与字形差异已审核；私有 8/8 原文测试、封存知识资产 235 文件、真实生产 EvidenceResolver 97 个 Evidence ID 通过；二级表格来源不冒充古籍，已有 s004 藏干成员证据不撤销；顺序/60-30-10权重、分日、余气、三刑流派仍未裁决。C级单电子本，非独立版本校勘；不授权通用旺衰、喜用或公开吉凶；未生产部署，后续任务仍待做 |
| TJ-010.2 | M2 | 通根/透干/生扶/克泄作用条件矩阵 | 已合并 | [公开功能 PR #259](https://github.com/HelloMrDuan/tianji-knowledge-base/pull/259) merge `1a013311e2eef90807e2d1d80c5ab0ae8cda9e93` · [私有验收 PR #62](https://github.com/HelloMrDuan/tianji-private-knowledge/pull/62) merge `08d00b4d272615cad0451086676181e92eebd7f3` · [公开 CI 10/10](https://github.com/HelloMrDuan/tianji-knowledge-base/actions/runs/39095238419) · [私有完整验收](https://github.com/HelloMrDuan/tianji-private-knowledge/actions/runs/39095500599) | 2026-10-18 | 通根/透干/生扶克泄作用条件矩阵正式完成：roots/exposures/actions三类矩阵5状态；合冲刑冲突→unresolved；逐行Evidence绑定（rule_id/variant/fact_ref/evidence_ids/source_id/section_id）；8项篡改负例全部拒绝；不计算权重、不作整体旺衰判断；未放开喜用神/吉凶 |
| TJ-010.3 | M2 | 木日主已审范围正反复算 | 已合并 | https://github.com/HelloMrDuan/tianji-knowledge-base/pull/261 | 2026-10-18 | 公开 merge c593ee0b，私有 PR #63 merge 83e59a21，木日主已审范围正反复算完成 |
| TJ-011.1 | M2 | 将 bazi-strength-adjudication-v1 的每条充分条件逐项核定 | 已合并 | https://github.com/HelloMrDuan/tianji-knowledge-base/pull/263 | 2026-10-18 | 15条条件逐项核定完成，已合并关账 |
| TJ-011.2 | M2 | 增新日主或月份（仅有证据才做） | 阻塞 | https://github.com/HelloMrDuan/tianji-knowledge-base/pull/265 | 2026-10-19 | 缺少其他日主或月份的独立古籍证据审核，完成 Source→Section→Rule→Evidence→Phase2→Golden 闭环及正强、正弱、未知、冲突测试后，方可重新评估扩围。见E0046 |
| TJ-011.3 | M2 | 限界显示与研究/正式开关 | 已合并 | https://github.com/HelloMrDuan/tianji-knowledge-base/pull/272 | 2026-10-19 | 失败关闭修复已合并，32项测试通过 |
| TJ-012.1 | M2 | 正官、印绶等现有格局候选再审核 | 已合并 | https://github.com/HelloMrDuan/tianji-knowledge-base/pull/276 | 2026-10-25 | 纠正记录 E0147：E0056/E0058 的“CI 9/9”与“pattern 测试被阻塞”自相矛盾；实质再审核未完成，仅测试卫生；已合并状态曾夸大验收范围，特此纠正；状态保持已合并，不改旧事件 |
| TJ-012.2 | M2 | 真/假、成/败、特殊格局的反例 | 已合并 | https://github.com/HelloMrDuan/tianji-knowledge-base/pull/282 | 2026-10-20 | CI假绿灯已修复；私有验收run 39384846971同SHA通过；格局测试真实执行全过 |
| TJ-013.1 | M2 | 调候、扶抑、病药、格局用神分别建来源/Variant | 阻塞 | — | — | 等待证据/前置依赖 |
| TJ-013.2 | M2 | 喜用与旺衰/格局冲突决策 | 阻塞 | — | — | 等待证据/前置依赖 |
| TJ-013.3 | M2 | 适用范围明确的用户可读提示 | 阻塞 | — | — | 等待证据/前置依赖 |
| TJ-014.1 | M3 | 顺/逆 原典规则与不同流派矩阵 | 已合并 | https://github.com/HelloMrDuan/tianji-knowledge-base/pull/284 | 2026-10-20 | 审核关账：方向规则为B类现代还原候选（未晋级）；私有验收run 39404769765同SHA通过 |
| TJ-014.2 | M3 | 与已有月柱候选序列做事实追踪 | 已合并 | https://github.com/HelloMrDuan/tianji-knowledge-base/pull/288 | 2026-10-21 | 终审整改三项P0+AttributeError修复已合并；50项链测试私有验收通过；关账 |
| TJ-015.1 | M3 | 固定 12 节历法提供方真实性重放 | 已合并 | https://github.com/HelloMrDuan/tianji-knowledge-base/pull/290 | 2026-10-21 | 十二节重放+提供方身份校验已合并；694项私有验收通过；关账 |
| TJ-015.2 | M3 | 历史时区、闰年、跨世纪和独立历法精度核查 | 已合并 | https://github.com/HelloMrDuan/tianji-knowledge-base/pull/298 | 2026-10-22 | provider重放门禁已合并；63项测试+私有全量验收通过；关账 |
| TJ-016.1 | M3 | 三日一年／余日／余时的不同版本整理 | 已合并 | https://github.com/HelloMrDuan/tianji-knowledge-base/pull/300 · `ae10335f766e830cd8efcc7cf6afc6ede2c12b85` | 2026-10-22 | 终审通过已合并；私有验收通过；关账 |
| TJ-016.2 | M3 | 起运当秒、虚岁/实岁等最困难反例 | 已合并 | [公开 #302](https://github.com/HelloMrDuan/tianji-knowledge-base/pull/302) · `13e1c063f67cafb6fae40e2e0fe683bb3a09b680` · [私有验收 run 39732347250](https://github.com/HelloMrDuan/tianji-private-knowledge/actions/runs/39732347250) | 2026-10-22 | 已关账（E0084）；反例专项 50/50；全量 843/843 |
| TJ-016.3 | M3 | 研究模拟与正式运期的硬边界 | 已合并 | [公开 #332](https://github.com/HelloMrDuan/tianji-knowledge-base/pull/332) | 2026-10-25 | #332 已合并；硬边界验证（research_only 契约+公开无暴露断言）已在主干；零新功能代码；phase2 测试由离线受控验收执行，公开 CI 不冒称 |
| TJ-017.1 | M3 | 有出处的运期锚点计算/区间规则 | 阻塞 | — | — | 等待证据/前置依赖 |
| TJ-017.2 | M3 | 原局＋大运＋流年跨规则调用 | 阻塞 | — | — | 等待证据/前置依赖 |
| TJ-017.3 | M3 | 用户可读时间轴视图 | 阻塞 | — | — | 等待证据/前置依赖 |
| TJ-018.1 | M4 | 寻找具体古籍条目的底本/版本/合法引用 | 待做 | — | — | 按 WBS 验收条件执行 |
| TJ-018.2 | M4 | 校勘/异文/不同电子来源独立性 | 待做 | — | — | 按 WBS 验收条件执行 |
| TJ-018.3 | M4 | Canonical/Quarantine 审批和私有验证 | 待做 | — | — | 按 WBS 验收条件执行 |
| TJ-019.1 | M4 | 高频梦境需求矩阵 | 已合并 | [公开 #326](https://github.com/HelloMrDuan/tianji-knowledge-base/pull/326) | 2026-10-25 | #326 已合并；矩阵视图已在主干；7 分类静态排队+不产解释声明在位 |
| TJ-019.2 | M4 | 小批新场景真实入库 | 阻塞 | — | — | 等待证据/前置依赖 |
| TJ-019.3 | M4 | 存量十种场景复核 | 已合并 | [公开 #338](https://github.com/HelloMrDuan/tianji-knowledge-base/pull/338) | 2026-10-25 | #338 已合并；存量十场景复核验证（10 例各恰好 1 精确命中+泛化 0 命中）已在主干；后端 10 场景枚举已有断言，不重建 |
| TJ-020.1 | M4 | 主体+实体+动作+时间次序 | 已合并 | [公开 #307](https://github.com/HelloMrDuan/tianji-knowledge-base/pull/307) | 2026-10-25 | #307 已合并；受控 Canonical/Evidence 可信机全量测试仍待证据，不冒称发布验收 |
| TJ-020.2 | M4 | 否定/假设/转述/梦醒否定 | 已合并 | [公开 #307](https://github.com/HelloMrDuan/tianji-knowledge-base/pull/307) | 2026-10-25 | #307 已合并 |
| TJ-020.3 | M4 | 多梦象并存、来源冲突与弃判 | 已合并 | [公开 #307](https://github.com/HelloMrDuan/tianji-knowledge-base/pull/307) | 2026-10-25 | #307 已合并 |
| TJ-021.1 | M4 | 古风书卷页的命中分组与短引 | 已合并 | [公开 #338](https://github.com/HelloMrDuan/tianji-knowledge-base/pull/338) | 2026-10-25 | #338 已合并；书卷页四层验证（原梦叙述→审核对应→出处→文化限界，含字面标签小补丁）已在主干；桩 spec 公开 CI 执行、真实后端 spec 离线受控验收，公开 CI 不冒称 |
| TJ-021.2 | M4 | 不匹配/服务失败/禁用 AI 的用户友好空态 | 已合并 | [公开 #307](https://github.com/HelloMrDuan/tianji-knowledge-base/pull/307) | 2026-10-25 | #307 已合并 |
| TJ-021.3 | M4 | 真实浏览器语义与文字可读性 | 已合并 | [公开 #316](https://github.com/HelloMrDuan/tianji-knowledge-base/pull/316) | 2026-10-25 | #316 已合并；夜主题对比度修复 + 390px 可读性断言已在主干 |
| TJ-022.1 | M5 | 桃花两套咸池与原局关系证据独立 | 已合并 | [公开 #334](https://github.com/HelloMrDuan/tianji-knowledge-base/pull/334) | 2026-10-25 | #334 已合并；桃花两套咸池验证（年支/日支分别查表+独立激活+不相加成概率）已在主干；新增 3 项测试由离线受控验收执行，公开 CI 不冒称 |
| TJ-022.2 | M5 | 经审配偶宫/星与年运条件 | 阻塞 | — | — | 等待证据/前置依赖 |
| TJ-022.3 | M5 | 桃花场景结果书卷化 | 已合并 | [公开 #338](https://github.com/HelloMrDuan/tianji-knowledge-base/pull/338) | 2026-10-25 | #338 已合并；桃花书卷化验证（普通语言条件摘要+两套方法独立展示+目标年真实重算）已在主干；桩 spec 公开 CI 执行、真实后端 spec 离线受控验收，公开 CI 不冒称 |
| TJ-023.1 | M5 | 财官食印比劫位置/事件条件聚合 | 已合并 | [公开 #334](https://github.com/HelloMrDuan/tianji-knowledge-base/pull/334) | 2026-10-25 | #334 已合并；财官食印聚合验证（五组十神数量与真实位置保留+缺旺衰不写升职破财）已在主干；新增 2 项测试由离线受控验收执行，公开 CI 不冒称 |
| TJ-023.2 | M5 | “事业”与“财运”两个可见视图 | 已合并 | [公开 #309](https://github.com/HelloMrDuan/tianji-knowledge-base/pull/309) | 2026-10-25 | #309 已合并 |
| TJ-023.3 | M5 | 已审大运与流年合用（以后置为准） | 阻塞 | — | — | 等待证据/前置依赖 |
| TJ-024.1 | M5 | 双人 A/B 双向关系矩阵及证据 | 已合并 | [公开 #316](https://github.com/HelloMrDuan/tianji-knowledge-base/pull/316) | 2026-10-25 | #316 已合并；交换一致性测试由离线验收执行，公开 CI 不冒称 |
| TJ-024.2 | M5 | 配偶宫、四柱 4×4 分层与冲突限界 | 已合并 | [公开 #334](https://github.com/HelloMrDuan/tianji-knowledge-base/pull/334) | 2026-10-25 | #334 已合并；配偶宫 4×4 验证（日支结构位+4×4 分层+合冲害/三合位置正确+不从条数生成适配分）已在主干；新增 5 项测试由离线受控验收执行，公开 CI 不冒称 |
| TJ-024.3 | M5 | 资料隔离/隐私提示与移动端双栏 | 已合并 | [公开 #310](https://github.com/HelloMrDuan/tianji-knowledge-base/pull/310) merge `c31adc13b7b4de4fafa5a3e041e8dcd8d7fab6ff` · [main 构建](https://github.com/HelloMrDuan/tianji-knowledge-base/actions/runs/40070159888) · [main 任务门禁](https://github.com/HelloMrDuan/tianji-knowledge-base/actions/runs/40070159894) · [main 前端](https://github.com/HelloMrDuan/tianji-knowledge-base/actions/runs/40070159900) | 2026-10-24 | [B006] 对方资料知情同意与后端留存边界提示已合并；隐私 Playwright 门禁通过，清空 B 后旧结果消失、修改 B 不覆盖 A 有强断言。用户实机日志：07:05:35Z 离线 ACCEPTED、07:06:06Z 自动 DEPLOYED，Web/API 目标 SHA 均为 c31adc13，health+bazi ok。独立生产端 360/390px 视觉 E2E 与服务端留存策略审计尚未验收，不冒称完整隐私合规 |
| TJ-025.1 | M5 | 四源场景同一出生/目标年真实聚合 | 已合并 | [公开 #338](https://github.com/HelloMrDuan/tianji-knowledge-base/pull/338) | 2026-10-25 | #338 已合并；四源聚合验证（同盘同年+去重证据+一致性核验文案）已在主干；后端 12 项集成测试已覆盖，不重建 |
| TJ-025.2 | M5 | 人生总览的条件说明/无法裁决出口 | 阻塞 | — | — | 等待证据/前置依赖 |
| TJ-025.3 | M5 | 首页→总览→细分页面的完整古风阅读链 | 已合并 | [公开 #311](https://github.com/HelloMrDuan/tianji-knowledge-base/pull/311) | 2026-10-25 | #311 已合并；限于浏览器导航/年份/清空/四视口表现，后端四源 Evidence 真验收另由 TJ-025.1 处理 |
| TJ-026.1 | M6 | 恢复 #87 管理布局与 16 个原管理模块 | 已合并 | [公开 #332](https://github.com/HelloMrDuan/tianji-knowledge-base/pull/332) | 2026-10-25 | #332 已合并；logs 单项（审计轨迹视图：真实审计列表+令牌门禁+401/403/404/503 分支+进程内存标注）已在主干；users 真实数据与 16 模块数据接入仍另立任务（完整 026.1 未完成） |
| TJ-026.2 | M6 | Scenario 管理与梦研究管理 | 已合并 | [公开 #324](https://github.com/HelloMrDuan/tianji-knowledge-base/pull/324) | 2026-10-25 | #324 已合并；Scenario 真实管理页与发布门禁已在主干；DEMO scenarios 模块已移除；真实后端验证由离线受控验收执行，公开 CI 不冒称 |
| TJ-026.3 | M6 | 真实只读模块逐页接受控接口 | 已合并 | [公开 #324](https://github.com/HelloMrDuan/tianji-knowledge-base/pull/324) | 2026-10-25 | #324 已合并；403 scope 模型与 401/403/404 显式分支已在主干；HTTP 与浏览器真实后端验证由离线受控验收执行，公开 CI 不冒称 |
| TJ-026.4 | M6 | 角色权限、草稿审批、回滚和审计 | 已合并 | [公开 #330](https://github.com/HelloMrDuan/tianji-knowledge-base/pull/330) | 2026-10-25 | #330 已合并；第三批回滚（草稿内版本史+仅 publisher 回滚+补偿审计只追加）已在主干；持久化存储另决策；方案 B 登记簿另立任务；HTTP 测试由离线受控验收执行，公开 CI 不冒称 |
| TJ-026.5 | M6 | 审计与草稿持久化存储 | 已合并 | [公开 #340](https://github.com/HelloMrDuan/tianji-knowledge-base/pull/340) | 2026-10-25 | #340 已合并；审计与草稿持久化存储（SQLite 单文件：audit_entries 只追加+drafts+draft_versions+draft_transitions+AUTOINCREMENT 编号序列）已在主干；备份 = 拷文件；容器无持久卷时重部署仍可能丢，部署卷需单独确认 |
| TJ-027.1 | M6 | 部署私有后端与静态前端 | 已提交PR | https://github.com/HelloMrDuan/tianji-knowledge-base/pull/308 · https://github.com/HelloMrDuan/tianji-knowledge-base/pull/313 | 2026-10-24 | PR #308 已合并公开 Web GHCR 构建；PR #313 增加仅 main 可唤醒正式机器的安全门禁，功能分支禁止触发正式机器唤醒。可信机离线密封验收、精确 SHA/PIN 与机内自动部署仍须真实取证，未获部署验收 |
| TJ-027.2 | M6 | 可观测性与回滚 | 已合并 | [公开 #305](https://github.com/HelloMrDuan/tianji-knowledge-base/pull/305) | 2026-10-25 | #305 已合并；仅健康探针子范围，告警/自动回滚仍待实机证据，不声明完整关账 |
| TJ-028.1 | M6 | 真模型访问与权限 | 待做 | — | — | 按 WBS 验收条件执行 |
| TJ-028.2 | M6 | 领域级真实模型评测 | 阻塞 | — | — | 等待证据/前置依赖 |
| TJ-028.3 | M6 | 人工验收与独立发版 | 待做 | — | — | 按 WBS 验收条件执行 |
| TJ-029.1 | M6 | 受限灰度与用户真实任务 | 待做 | — | — | 按 WBS 验收条件执行 |
| TJ-029.2 | M6 | 性能/安全/隐私反馈闭环 | 待做 | — | — | 按 WBS 验收条件执行 |
| TJ-030.1 | M7 | 周易专业结果收口 | 已合并 | [公开 #320](https://github.com/HelloMrDuan/tianji-knowledge-base/pull/320) | 2026-10-25 | #320 已合并；周易公开执行接通与真实结果渲染已在主干；引擎与浏览器测试由离线受控验收执行，公开 CI 不冒称 |
| TJ-030.2 | M7 | 紫微专业结果收口 | 已合并 | [公开 #322](https://github.com/HelloMrDuan/tianji-knowledge-base/pull/322) | 2026-10-25 | #322 已合并；紫微公开执行接通与真实结果渲染已在主干；闰月拒绝与流派限界在位；引擎与浏览器测试由离线受控验收执行，公开 CI 不冒称 |
| TJ-030.3 | M7 | 奇门专业结果收口 | 已合并 | [公开 #322](https://github.com/HelloMrDuan/tianji-knowledge-base/pull/322) | 2026-10-25 | #322 已合并；奇门公开执行接通与真实结果渲染已在主干；超接置闰未实现声明在位；引擎与浏览器测试由离线受控验收执行，公开 CI 不冒称 |
| TJ-030.4 | M7 | 六壬专业结果收口 | 已合并 | [公开 #320](https://github.com/HelloMrDuan/tianji-knowledge-base/pull/320) | 2026-10-25 | #320 已合并；六壬公开执行接通与真实结果渲染已在主干；天将未实现声明在位；引擎与浏览器测试由离线受控验收执行，公开 CI 不冒称 |
| TJ-030.5 | M7 | 风水专业结果收口 | 已合并 | [公开 #322](https://github.com/HelloMrDuan/tianji-knowledge-base/pull/322) | 2026-10-25 | #322 已合并；风水公开执行接通与真实结果渲染已在主干；绝对元运生产不可用声明在位；引擎与浏览器测试由离线受控验收执行，公开 CI 不冒称 |

## 进度计算与正确读法

- **完成**仅计 `已合并` 或经真实部署验收的 `已部署验收`；`进行中`、`CI待验`、`阻塞` 均不计完成。
- 初始历史已合并 **7 / 92** 个子任务；`TJ-001.4` 仍是进行中，须经 PR 合并并在结账 PR 中填入真实完整 SHA 后才计完成。
- `TJ-008.2` 虽已有首页 PR，但最初设计的完整视觉对照未完成，按**进行中**统计。
- [私有 #53](https://github.com/HelloMrDuan/tianji-private-knowledge/pull/53) 的最终组合回归是否合并，必须以真实 GitHub 检查和合并记录为准；不能写死为成功。
- 以后任何任务新增、拆分或完成，必须联动 WBS、此状态表与历史日志。不要只在聊天消息里更新状态。

## 接下来的有序选择

在 `TJ-001.4` 关账之后，从有条件执行且仍未完成的任务开始，优先处理 **TJ-004.3 异常/拒判、TJ-004.4 原设计截图差异**。如先发现遗留组合 CI 已通过并需收尾，先以同一个可验任务 ID 记录该闭环；禁止两项合并成一个完成记录。
