# 天机平台｜原子任务状态变更日志

> 对应[任务状态表](TASK_STATUS.md)、[详细 WBS](DETAILED_DELIVERY_BACKLOG_V1.md)和[执行制度](TASK_EXECUTION_RULES.md)。  
> **2026-10-11 初次建账时**，E0001～E0008 是对之前实际 PR/CI 的事实回填，并非宣称此前每批已采用新制度。E0009 是本轮 `TJ-001.4` 认领事件。之后**严格追加**，旧事件不得删除、排序、覆盖；发现错误只能增加纠错事件。  
> 每次状态变化需有一个任务 ID、实证链接、变更结果与下一步；没有实际合并不能填完成。日后新增一次 PR/CI 更新只添加**一条新的事件**，同一 PR 不得为两个任务同时关账。

| 事件 | 日期（北京时间） | 唯一任务 ID | 事件后状态 | 本次实际变化/未完成界限 | 真实 PR / 分支 | 证据 SHA | CI/运行凭证 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| E0001 | 2026-10-11 | TJ-001.1 | 已合并 | 原始视觉/场景基线写入正式规划 | https://github.com/HelloMrDuan/tianji-knowledge-base/pull/221 | 07165cc5be8986b7ddd7f60863619c754cc2e355 | https://github.com/HelloMrDuan/tianji-knowledge-base/pull/221/checks |
| E0002 | 2026-10-11 | TJ-001.2 | 已合并 | 逐页交互/输入/异常规格归档；属历史一次性批量计划 PR | https://github.com/HelloMrDuan/tianji-knowledge-base/pull/221 | 07165cc5be8986b7ddd7f60863619c754cc2e355 | https://github.com/HelloMrDuan/tianji-knowledge-base/pull/221/checks |
| E0003 | 2026-10-11 | TJ-001.3 | 已合并 | README 与细化规划入口已合并，历史规则不追溯适用一 PR 一任务 | https://github.com/HelloMrDuan/tianji-knowledge-base/pull/221 | 07165cc5be8986b7ddd7f60863619c754cc2e355 | https://github.com/HelloMrDuan/tianji-knowledge-base/pull/221/checks |
| E0004 | 2026-10-11 | TJ-002.1 | 已合并 | 私有 #50 双回归核对：combined-main、merged-main-209 | https://github.com/HelloMrDuan/tianji-private-knowledge/pull/50 | e0f95051a65dcdb5337853405a4e18a798eeb19d | https://github.com/HelloMrDuan/tianji-private-knowledge/actions/runs/38069517719 |
| E0005 | 2026-10-11 | TJ-002.2 | 已合并 | 私有 #50 已按准确 head 完成合并 | https://github.com/HelloMrDuan/tianji-private-knowledge/pull/50 | e0f95051a65dcdb5337853405a4e18a798eeb19d | https://github.com/HelloMrDuan/tianji-private-knowledge/actions/runs/38069517886 |
| E0006 | 2026-10-11 | TJ-004.1 | 已合并 | 11 场景 API 对应表与原首页差异审计合并；全场景异常矩阵另见 TJ-004.3 | https://github.com/HelloMrDuan/tianji-knowledge-base/pull/224 | b42a1d89f2b7bcc7b3c2a75a168299ce7128285c | https://github.com/HelloMrDuan/tianji-private-knowledge/actions/runs/38072602895 |
| E0007 | 2026-10-11 | TJ-004.2 | 已合并 | 11/11 真实入口成功、12/12 浏览器、524 Python、235 私有文件合并验收 | https://github.com/HelloMrDuan/tianji-knowledge-base/pull/225 | a9f0b276d2b506c0cb0768fcb74f57da01de72af | https://github.com/HelloMrDuan/tianji-private-knowledge/actions/runs/38073174926 |
| E0008 | 2026-10-11 | TJ-008.2 | 进行中 | 首页主 CTA/四时间入口已合并，但 #87/#89 原图完整人工对照未验收 | https://github.com/HelloMrDuan/tianji-knowledge-base/pull/224 | b42a1d89f2b7bcc7b3c2a75a168299ce7128285c | https://github.com/HelloMrDuan/tianji-private-knowledge/actions/runs/38072602895 |
| E0009 | 2026-10-11 | TJ-001.4 | 进行中 | 本次仅认领逐任务状态/追加日志/PR 校验制度；真实合并 SHA 后续关账 | 本 PR 尚待创建 | — | — |

| E0010 | 2026-10-11 | TJ-001.4 | 已合并 | 92 项独立状态表、追加式日志、逐 PR 单任务门禁和单测已通过并合并；无生产部署声明 | https://github.com/HelloMrDuan/tianji-knowledge-base/pull/228 | 6a22f29f2ec2e0b3a2bd9689c0dd9df5fd3d883d | https://github.com/HelloMrDuan/tianji-knowledge-base/actions/runs/38101246241 |

| E0011 | 2026-10-11 | TJ-008.2 | 进行中 | 用户明确否决旧首页“一事占问”首位；本批改运势、桃花、事业财运首屏与三张重点卡，保留 #87 水墨/11 入口；新真实截图/视觉对照仍待 CI | https://github.com/HelloMrDuan/tianji-knowledge-base/pull/230 | — | — |

| E0012 | 2026-10-11 | TJ-008.2 | 已合并 | 按用户纠偏：首页运势主入口、桃花/事业辅助、前三张重点卡、手机适配；完整 11 页面原图审核仍属后续其他任务 | https://github.com/HelloMrDuan/tianji-knowledge-base/pull/230 | e00137addfd1ddd19d9d7080b13d8095d6b895f3 | https://github.com/HelloMrDuan/tianji-private-knowledge/actions/runs/38106598250 |

| E0013 | 2026-10-11 | TJ-008.3 | 进行中 | 开发单一工作包：今日、流年、桃花、事业财运由真实 Scenario 响应生成首屏可读摘要、来源数量与无依据边界；完整 11 场景报告未宣称完成 | 当前任务 PR 正在提交 | — | — |

| E0014 | 2026-10-11 | TJ-008.3 | 已合并 | 四个真实结果页先展示可读计算事实、可核对短引数量和明确不能判断的范围；公开四项 CI 与私有 7/7 Chromium、四张 390px 截图已验证；其余功能仍待完成 | https://github.com/HelloMrDuan/tianji-knowledge-base/pull/232 | 4f00515048d08ee92e998d08cc03a543756cfddc | https://github.com/HelloMrDuan/tianji-private-knowledge/actions/runs/38109609969 |

| E0015 | 2026-10-11 | TJ-004.3 | 进行中 | 本批补真实前台 11 入口非法资料、断网恢复、来源缺失与请求乱序负例；真实超时/重复提交仍需补充，不因测试新增即宣布关闭 | 新 PR 尚待创建 | — | — |

| E0016 | 2026-10-11 | TJ-004.3 | 已合并 | 11 入口无效值、4 个年份非法区间、3 场景断网恢复、真实后端超时、防重复点击、缺源限界、乱序请求覆盖等回归 24/24 通过；未声称全部吉凶解释能力完成 | https://github.com/HelloMrDuan/tianji-knowledge-base/pull/234 | 283557b3e595ee8dc80be31b809a0a4315db8fa0 | https://github.com/HelloMrDuan/tianji-private-knowledge/actions/runs/38110293680 |

| E0017 | 2026-10-11 | TJ-004.4 | 进行中 | 依据用户确认的夜景古风图存档冻结视觉与播放器位置；提交桌面/手机页面骨架、11 场景及音乐真交互；完整 11 场景与 #87/#89 逐页差异仍待执行 | 设计分支 design/tj0044-night-ink-music-20261011，PR 待创建 | — | 本地 Chromium 1440/390/360 音乐与场景交互通过；仓库 CI 待验 |

| E0018 | 2026-10-14 | TJ-004.4 | 进行中 | 对 main@c615a33 构建产物真实 Chromium 取证：12 页 × 1440/390/360 共 36 张全页截图；音乐播放/暂停/音量/持久化/路由持续/默认静音/全局暂停 7/7 通过；差异台账已提交，主题级差异 D-01 待用户裁定，结果态比对待后端 | 本 PR（分支 tj-004.4-visual-diff-ledger） | — | 本地 original-design-home 5/5 通过；仓库 CI 待验 |

| E0019 | 2026-10-14 | TJ-004.4 | 已合并 | 审计交付完成：差异台账 v2（#87/#89 对照、严重程度、后续任务、D-01 双主题深青默认已裁定）+ 42 张截图归档 + tj0044-capture/music 可复现脚本（36/36、18/18 含后台停止）全部入库；结果态比对缺口如实保留待受控后端，未伪造；私有库无变更 | https://github.com/HelloMrDuan/tianji-knowledge-base/pull/237 | ff9e9d11908cd27155b00cfb6595b224c5d06b98 | https://github.com/HelloMrDuan/tianji-knowledge-base/actions/runs/38534526334 |

| E0020 | 2026-10-14 | TJ-008.6 | 进行中 | 双主题技术基础开发启动：data-theme 主题机制（深青夜景默认/米白宣纸可选）、localStorage 偏好持久化、桌面+手机切换入口、index.html 内联初始化防首屏闪烁、异常值回退；WBS 已登记 TJ-008.6 | 本 PR（分支 tj-008.6-theme-foundation） | — | 真实 Chromium 三视口验证待执行；仓库 CI 待验 |

| E0021 | 2026-10-14 | TJ-008.6 | 已合并 | 双主题基础交付完成：主题机制/持久化/切换入口/防闪烁；WCAG AA 对比度门禁（夜景/宣纸双通过，零匹配选择器会 FAIL）；回归单测去硬编码；Chromium 25/25、页面回归 35/35；19 张双主题截图入库；未宣称首页精确还原（归 TJ-008.7） | https://github.com/HelloMrDuan/tianji-knowledge-base/pull/239 | 023543a9c4787333e614e1612321a83de65b21c0 | https://github.com/HelloMrDuan/tianji-knowledge-base/actions/runs/38542003719 |

| E0022 | 2026-10-14 | TJ-008.7 | 进行中 | 首页深青夜景真实视觉还原认领并登记：WBS 已新增 TJ-008.7，TASK_STATUS 标进行中；以 approved-reference.webp 为最高基准开始 React 还原 | 分支 tj-008.7-night-home-restoration（待建） | — | — |

| E0023 | 2026-10-15 | TJ-008.7 | 已合并 | 首页深青夜景真实视觉还原交付完成：11 场景四层架构（4 核心卡/3 重点/4 其他/专业工具）、深青夜景默认/宣纸可切换、9 张原创 AI 水墨、古风音乐播放器、手机首屏四入口几何测试无遮挡；Playwright 50/50、GitHub 4/4 CI；用户最终视觉验收通过 | https://github.com/HelloMrDuan/tianji-knowledge-base/pull/241 | f4ff245cacdc74c12b07afe6b5b8b9f0a40fc6fe | https://github.com/HelloMrDuan/tianji-knowledge-base/actions/runs/38668854631 |

| E0024 | 2026-10-15 | TJ-006.1 | 进行中 | 多场景统一输入与本地资料校验认领并登记：WBS 已登记 TJ-006.1，TASK_STATUS 标进行中；统一 birthProfile 模型、日期/时区显式校验、跨场景复用 | 分支 tj-006.1-birth-profile（待建） | — | — |

| E0025 | 2026-10-15 | TJ-006.1 | 已合并 | 多场景统一出生资料输入已合并：阳历/农历及闰月严格校验、自然语言出生地区、无时刻不伪造、原始农历跨页复用及旧资料地区显式确认。PR #243 head cb18e67ffca29ca3c15fb2a86e7a2fb1c9c57ce8 经 GitHub 四项 CI success，最终合并 main；Muse 本地报告 55/55，GitHub CI 未执行 Playwright；真实后端 E2E 尚未验证、美国/加拿大/澳大利亚精确地区与 1949 年前时区仍受限，须后续独立任务验证。私有知识库未修改，非生产部署 | https://github.com/HelloMrDuan/tianji-knowledge-base/pull/243 | 8a0081990bb442fb3521bbd2140056901fe14eed | https://github.com/HelloMrDuan/tianji-knowledge-base/actions/runs/38692470766 |

| E0026 | 2026-10-15 | TJ-007.1 | 进行中 | 五场景真实流程实施中：前端补八字结果限制及三条请求参数观察用例；真实后端需要在私有受控环境由私有 Canonical 与公开代码组装并构建 production_runtime，当前公开工作区缺少 yijing 是源数据未装配，而非证明私有库不存在。暂未通过真实后端 E2E，不宣称完成。 | https://github.com/HelloMrDuan/tianji-knowledge-base/pull/245 | — | https://github.com/HelloMrDuan/tianji-knowledge-base/pull/245/checks |

| E0027 | 2026-10-15 | TJ-007.1 | 已合并 | 公开五场景真实流程和同任务私有生产运行时验收均已合并：公开 PR #245 merge `d80ff176156fbd7a462e5610bc8184253067c9b0`，私有 PR #57 merge `b7eab9c16dfb9b9e9e35273207c7e754205ed827`；公开 GitHub 4/4 CI success、真实受限 Canonical 装配/后端 API/Chromium 合计 35/35（基础 5、专项 15、1440/390/360 × 五场景截图 15）；私有 artifact `tj0071-live-results` ID 11955365866（受限访问，保留一天）。覆盖阳历与农历、闰月与立春前后年柱、日期/周/月/年切换、五场景档案复用及 Rule/Evidence 引用。结果属于传统命理已审核确定性结构，未宣称全量吉凶预测或生产部署；无完整私有知识向公开仓库转移。 | https://github.com/HelloMrDuan/tianji-knowledge-base/pull/245 | d80ff176156fbd7a462e5610bc8184253067c9b0 | https://github.com/HelloMrDuan/tianji-private-knowledge/actions/runs/38696910589 |

| E0028 | 2026-10-15 | TJ-006.2 | 进行中 | 目标日、周、月、流年目标与真实 API 响应一致性沿用已合并 TJ-007.1 私有受控 35/35 验收；本任务补充 1901–2098 年份上下限设计说明，以及严格的旧请求后返、目标日期编辑清屏、非法输入禁止提交、年份范围浏览器状态测试。仅前端状态模拟，不冒充真实后端计算；待最新 CI 和独立复审，不声明已合并。 | https://github.com/HelloMrDuan/tianji-knowledge-base/pull/247 | — | https://github.com/HelloMrDuan/tianji-private-knowledge/actions/runs/38696910589 |


| E0029 | 2026-10-15 | TJ-006.2 | 已合并 | 核实已有真实五场景日期/年份一致性与节气/闰年/跨周跨年证据；本任务仅增加 1901–2098 前端保守年份范围说明、4 项真实 Chromium 前端状态契约测试及专用重复验收 CI。新测试分别验证 2025 旧请求晚于 2027 返回不会覆盖最新结果、查看日期改变立即清除旧结果、空日期不发送请求、1900/2100 禁止而 1901 合法；使用受控 HTTP 回包验证竞态，不能当作真实历法测算。公开 PR #247 已合并 main，GitHub 5/5 CI success；真实命理计算复用 TJ-007.1 私有受限 35/35。未生产部署、不声明其他任务完成。 | https://github.com/HelloMrDuan/tianji-knowledge-base/pull/247 | 8b37521e7c6ab961732479540dfa2fb84f2a7b15 | https://github.com/HelloMrDuan/tianji-knowledge-base/actions/runs/38699429188 |
| E0030 | 2026-10-15 | TJ-006.3 | 进行中 | 从 main `2f71314031bb7b7f55c8d9627e4be82c353d1218` 建立 TJ-006.3 分支，核查 A/B 数据隔离与本机删除；B 资料仅在组件内存、独立清除，不写个人出生档案；补前台统一跨标签页资料清除通知，防止其他已打开的运势/合盘页面继续显示旧档案或异步结果；前端交互及真实 Chromium CI 待最终验收，未声称正式合并或生产部署。 | https://github.com/HelloMrDuan/tianji-knowledge-base/pull/249 | — | https://github.com/HelloMrDuan/tianji-knowledge-base/pull/249/checks |

| E0031 | 2026-10-15 | TJ-006.3 | 已合并 | 双人合盘隐私隔离及本机资料删除完成：A/B 输入/角色/出生时区独立，B 方不写个人出生档案；增加清空 B 方信息/结果的入口，以及根组件跨标签页清除监听，避免其他已打开的运势/合盘场景保留旧资料；删除仅移除个人出生资料，保留主题、音乐、收藏偏好；防旧异步请求恢复已删数据。功能 PR #249 合并 main，6/6 GitHub CI success，独立 Chromium 隐私/跨标签页用例 8/8；受控 API 响应仅用于前端状态及请求参数验证，不冒充真实后端合盘计算。未生产部署，未变更私有 Canonical、未关闭父任务。 | https://github.com/HelloMrDuan/tianji-knowledge-base/pull/249 | 7ec43814bdf090d29be02d35dd36e6a5ed74681e | https://github.com/HelloMrDuan/tianji-knowledge-base/actions/runs/38701988505 |

| E0032 | 2026-10-15 | TJ-007.2 | 进行中 | 从 main 3778ba0 创建分支 tj-007.2-romance-career-compat；目标桃花/事业/合盘真实计算与用户结果展示；先审计三场景现有能力 | — | — | — |

| E0033 | 2026-10-15 | TJ-007.2 | 已合并 | 桃花姻缘、事业财运和缘分合盘三个真实 Scenario Engine 限定版产品流程已验收并合并：公开 PR #251 merge `2a75e02e5bc07823158902626c88572bc779c8e4`，受限私有验收 PR #58 merge `caef539d7aad7a38365dcf1c157de7f7dbc71766`。本轮复用原有已审核排盘及组合规则，并修复事业财运不真实的古籍引文占位、增加合盘双方日主/方向十神/关系命中的用户可读摘要；请求精确断言、目标年重新计算、Rule/Evidence 引用与结果展示通过。公开 7/7 GitHub CI success，受限真实私有 Canonical/生产 runtime/API/Chromium 5 项专项 + 9 张三视口真实结果截图合计 14/14 success。截图仅私有 Actions Artifact `tj0072-live-results` ID 11958141052 保留 1 日。未发布未经审定的正缘、婚期、财富金额、升职与吉凶预测；无私有完整 Canonical 流向公开仓库，未生产部署，不关账父任务。 | https://github.com/HelloMrDuan/tianji-knowledge-base/pull/251 | 2a75e02e5bc07823158902626c88572bc779c8e4 | https://github.com/HelloMrDuan/tianji-private-knowledge/actions/runs/38705064439 |

| E0034 | 2026-10-15 | TJ-007.3 | 进行中 | 一事占问、已审核梦象和人生总览四源的实际联调及浏览器验收；排盘和梦象/API 的代码已存在，本次补前端真实请求与盘面/来源断言、限定结果态截图、拒判和错误态。AI 自由解释继续关闭。此前私有 Actions 检出旧 SHA 导致 No tests found；此事件只表示正在推进，不宣称真实后端验收通过或已合并。 | https://github.com/HelloMrDuan/tianji-knowledge-base/pull/253 | — | https://github.com/HelloMrDuan/tianji-private-knowledge/actions/runs/38706904296 |

| E0035 | 2026-10-15 | TJ-007.3 | 已合并 | 一事占问、已审梦象查阅、人生四源聚合限定版实际交付。公开功能 PR #253 merge `297727060ef323103012f00957bd96034ea158bc`，私有受限验收 PR #59 merge `da526cf43bac2375f48835cef71b8cea7f8399b7`。公开 8/8 GitHub CI success（含三场景严格请求构造 3/3），私有数据校验/隔离装配/真实 reviewed runtime/Python API/Chromium 实测 5/5 与 1440/390/360 三场景真实结果截图 9/9（私有 Artifact `tj0073-live-results` ID 11959407138、保留一天）。真实测试覆盖六爻固定盘/动爻与修改后失效、梦象有据短引与未审主题弃判、同一出生时间和目标年的四源聚合以及 Evidence 引用。已修复占问页伪造来源短引、技术 ID 外露、测试空跑断言及被错误覆盖的历史日志。未经审定的 AI 自由解梦仍关闭；仅传统文化限定解释，无生产部署和完整命理吉凶裁定，不宣称其他原子任务完成。 | https://github.com/HelloMrDuan/tianji-knowledge-base/pull/253 | 297727060ef323103012f00957bd96034ea158bc | https://github.com/HelloMrDuan/tianji-private-knowledge/actions/runs/38708304212 |

| E0036 | 2026-10-15 | TJ-007.4 | 进行中 | 从最新 main 开发：历史页不再将静态 DEMO 冒充真实推演历史；演示收藏保留；补 HTTP 503/断网重试不丢出生资料、1440/390/360 无假历史的真实 Chromium 前端测试。CI 和其他场景超时/跨页完整验收尚未完成，不宣称功能关账 | 分支 tj-007.4-save-crosspage-errors（PR 待创建） | — | CI 待验 |

| E0037 | 2026-10-15 | TJ-007.4 | 已合并 | 已分离真实演示收藏与用户历史、统一 11 接口请求超时/断网/非 JSON/非法响应异常，保持重试时出生资料与年份、隐私跨标签页删除、旧请求防覆盖；独立复审发现并修复生产合同冲突：8 个用户场景既有 `production_limited`/`public_release=false`，只认可审核结构 `release_scope`，未擅自放开吉凶预测。公开功能 PR #255 merge `0304a55c41ee67d9f72c7e39bfef1a59d68cdc85`、私有真实验收 PR #60 merge `c94cd0f7cf17879f0e343ec70a51159e1ca516ec`；公开 9/9 GitHub CI success，私有 Canonical/真实 Python API/Chromium 11/11 且用户结果展示验证通过，私有截图 Artifact `11964270529`（保留一天）。无生产上线，AI 自由解梦未开放，其他 WBS 任务不关账。 | https://github.com/HelloMrDuan/tianji-knowledge-base/pull/255 · https://github.com/HelloMrDuan/tianji-private-knowledge/pull/60 | 0304a55c41ee67d9f72c7e39bfef1a59d68cdc85 | https://github.com/HelloMrDuan/tianji-knowledge-base/actions/runs/38718130197 · https://github.com/HelloMrDuan/tianji-private-knowledge/actions/runs/38718147580 |

| E0038 | 2026-10-15 | TJ-010.1 | 进行中 | 从公开 main 66f01371 审核月令/根和藏干来源；发现旧审计错把第三方数据 provenance 直接推断为无古籍依据。私有 phase1_knowledge.json 已有审核《渊海子平》藏遁歌 s004（仅 C级结构）及任氏月令/通根短引；须逐支核验输入表与原文、版本指纹及定位，查实差异才定针对性降级。当前不动四柱及正式规则，不宣称 TJ-010.1 完成；已恢复 E0037、TJ-007.4 及 TJ-007.4 真实合同测试，等待私有逐字审核。 | https://github.com/HelloMrDuan/tianji-knowledge-base/pull/257 | — | — |

| E0039 | 2026-10-15 | TJ-010.1 | 已合并 | 单任务古籍来源审计正式完成：公开 PR #257 merge `2d8c7075a7fda42f5aca55aa1960cea972e421ca`、私有证据/真实运行时 PR #61 merge `b970fe68df19bcefd11ecc2c579b2172dc64b6d6`。三个已审 C 级电子文本来源、11 条 Phase2 规则、40 个被引短引及三刑异文 s020（共 41 条）完成固定原始 SHA-256、字符偏移、字形和引用追踪；私有 8/8 原文及错误样本测试成功，235 个原封存知识资产清单未改变，真实 EvidenceResolver/ExecutionTrace 生成并校验 97 个 Evidence ID。公开最终 10/10 工作流（含真正执行 6 项专项测试、隐私和跨页回归）success。纠正“二级实现来源即无古籍支持”的过度降级，s004 仅证明 12 支藏干成员，不证明顺序/本气权重或 60/30/10；寅月分日、余气异文、三刑跨学派保留 unresolved，独立底本未核，仍只 C 级。没有修改四柱算法、未放开通用强弱/喜用/吉凶、未生产部署；TJ-010.2 等后续原子任务不关账。 | https://github.com/HelloMrDuan/tianji-knowledge-base/pull/257 · https://github.com/HelloMrDuan/tianji-private-knowledge/pull/61 | 2d8c7075a7fda42f5aca55aa1960cea972e421ca | https://github.com/HelloMrDuan/tianji-knowledge-base/actions/runs/38725443092 · https://github.com/HelloMrDuan/tianji-private-knowledge/actions/runs/38725488144 |

| E0040 | 2026-10-16 | TJ-010.2 | 进行中 | 从 main 888dea53 创建分支 tj-010.2-action-matrix；构建通根/透干/生扶克泄作用条件矩阵；修复PR #259关账记录 | — | — | — |

| E0041 | 2026-10-18 | TJ-010.2 | 已合并 | 通根/透干/生扶克泄作用条件矩阵正式关账：公开 PR #259 merge `1a013311e2eef90807e2d1d80c5ab0ae8cda9e93`、私有验收 PR #62 merge `08d00b4d272615cad0451086676181e92eebd7f3`。ChatGPT 独立复审通过。公开 CI 10/10；私有矩阵 20/20、Evidence 11/11、负例 8/8（含伪造source_id/section_id/清空evidence_ids/伪造effective）、Phase2 173/173、Golden 117/117。Evidence校验合同：逐行structure_evidence必填、effect_evidence对effective行必填、fact_ref按事实类型解引用验证、元数据字段严格比对、每行status与真实Rule输出1:1核对。未修改四柱算法、未改测试预期、235封存文件未动。 | https://github.com/HelloMrDuan/tianji-knowledge-base/pull/259 · https://github.com/HelloMrDuan/tianji-private-knowledge/pull/62 | 1a013311e2eef90807e2d1d80c5ab0ae8cda9e93 | https://github.com/HelloMrDuan/tianji-knowledge-base/actions/runs/39095238419 · https://github.com/HelloMrDuan/tianji-private-knowledge/actions/runs/39095500599 |

| E0042 | 2026-10-18 | TJ-010.3 | 进行中 | 从公开 main 1e9d885 创建分支 tj-010.3-wood-strength；核对已有 bazi-strength-adjudication-v1 实现与强/弱/无法裁定/冲突 Golden 覆盖，补齐木日主已审范围正反复算缺口；不新增日主/月份/流派，不做权重评分 | — | — | — |

| E0043 | 2026-10-18 | TJ-010.3 | 已合并 | 木日主已审范围正反复算正式关账：公开 PR #261 merge `c593ee0b0753c1e2f273b3521bfd1c65ebd46434`、私有验收 PR #63 merge `83e59a21eaa7d70e2fedc2b6990f3ee0e756a4f9`。ChatGPT 独立复审真实代码和 Actions 日志，核心验收通过。公开 CI 9/9；私有专项 14/14（含4日期子测试）、Phase2 173/173、Golden 117/117、235封存资产验证通过。测试真实性修复：删除所有宽泛 OR 断言；2023-03-08/18（卯月乙日主午火泄气）与2018-09-10/30（酉月乙日主壬水生扶）诚实重分类为 indeterminate 反例；测试名称修正为反例命名；惊蛰当秒 10:22:45 明确为卯月。确定性正例：强 癸卯/乙卯/甲子/乙亥+1963/2043，弱 戊午/辛酉/甲午/庚午+2038/1978。未覆盖：2015-2028无真实孤立弱正例（无水干/无木根/辛透），如实保留。未修改四柱算法、Golden、Canonical、封存文件。 | https://github.com/HelloMrDuan/tianji-knowledge-base/pull/261 · https://github.com/HelloMrDuan/tianji-private-knowledge/pull/63 | c593ee0b0753c1e2f273b3521bfd1c65ebd46434 | https://github.com/HelloMrDuan/tianji-knowledge-base/actions/runs/39118822484 · https://github.com/HelloMrDuan/tianji-private-knowledge/actions/runs/39119908210 |

| E0044 | 2026-10-18 | TJ-011.1 | 进行中 | 从公开 main 02b9485a 创建分支 tj-011.1-condition-audit，从私有 main 83e59a21 创建分支 tj-011.1-private-acceptance；开始逐项核定 bazi-strength-adjudication-v1 的 8 条强充分条件与 7 条弱充分条件，建立逐条件审核矩阵，验证每条的古籍依据、程序计算与反例覆盖 | — | — | — |

| E0045 | 2026-10-19 | TJ-011.1 | 已合并 | TJ-011.1正式关账 | https://github.com/HelloMrDuan/tianji-knowledge-base/pull/263 | f10a67ac186d2b6a2b59b5df6a8d88c8e4c4b22a | https://github.com/HelloMrDuan/tianji-knowledge-base/actions/runs/39195910280 |
| E0046 | 2026-10-19 | TJ-011.2 | 阻塞 | 证据核查完成：当前15条充分条件仅针对木日主（甲/乙）已审核；滴天髓s026/s033明列"甲乙逢亥寅卯"，审核文档明确"不能把另一五行按直觉扩表"；BAZI_STRENGTH_BATCH_09明确"非木日主"保持indeterminate；无火/土/金/水日主的等同审核证据。解除条件：完成其他日主的独立古籍证据审核（Source/Section/Locator/Evidence闭环） | — | — | — |
| E0047 | 2026-10-19 | TJ-011.3 | 已提交PR | TJ-011.3限界显示策略实现完成：新增bazi_strength_display.py（服务端展示裁决：public_result/research_only/insufficient/conflict/out_of_scope/error六态，indeterminate永不误读为中和/身弱/身强）；新增12项测试全过；确认公开API已拦截adjudication variant（research_only=True, public_enabled=False），前端未调用裁决接口且已有明确边界文案；无客户端绕过风险 | — | — | — |
| E0048 | 2026-10-19 | TJ-011.3 | 已合并 | TJ-011.3正式关账：公开PR #266合并（dee5bffac630），限界显示策略bazi_strength_display.py与12项测试已入main；确认research_only=True/public_enabled=False边界，前端未调用裁决接口；CI 9/9通过 | https://github.com/HelloMrDuan/tianji-knowledge-base/pull/266 | dee5bffac630fbab1a26cac5a033d6ff83e99d2a | https://github.com/HelloMrDuan/tianji-knowledge-base/pull/266/checks |
| E0049 | 2026-10-19 | TJ-011.3 | 已提交PR | 复审整改PR #268已提交：策略接入投影层，授权/范围/冲突修复完成，19项测试通过，待CI验收 | https://github.com/HelloMrDuan/tianji-knowledge-base/pull/268 | — | — |
| E0050 | 2026-10-19 | TJ-011.3 | 已合并 | TJ-011.3复审整改关账：PR #268合并（7005306de3cf），策略接入public_projection，服务端allowlist授权、范围/冲突判别修复，19项测试通过；CI 9/9 | https://github.com/HelloMrDuan/tianji-knowledge-base/pull/268 | 7005306de3cffa4b2ea98d35de7d4bdfe199c556 | https://github.com/HelloMrDuan/tianji-knowledge-base/pull/268/checks |
| E0051 | 2026-10-19 | TJ-011.3 | 已提交PR | 最终安全补验：修复strength_factor_graph.overall_strength第二泄露路径；6项泄露回归测试通过；待CI验收 | https://github.com/HelloMrDuan/tianji-knowledge-base/pull/270 | — | — |
| E0052 | 2026-10-19 | TJ-011.3 | 已合并 | TJ-011.3最终补验关账：PR #270合并（1641cddb2319），overall_strength第二泄露路径已修复，25项测试通过；CI 9/9 | https://github.com/HelloMrDuan/tianji-knowledge-base/pull/270 | 1641cddb23194bd72a8e9bbfbfa77156e44d565b | https://github.com/HelloMrDuan/tianji-knowledge-base/pull/270/checks |
| E0053 | 2026-10-19 | TJ-011.3 | 已提交PR | 最终补验失败关闭修复：缺失Variant时研究结论不得泄露；32项测试通过；待CI验收 | https://github.com/HelloMrDuan/tianji-knowledge-base/pull/272 | — | — |
| E0054 | 2026-10-19 | TJ-011.3 | 已合并 | TJ-011.3失败关闭修复关账：PR #272合并（ca2027db15a8），缺失Variant时研究结论不得泄露，32项测试通过；CI 9/9 | https://github.com/HelloMrDuan/tianji-knowledge-base/pull/272 | ca2027db15a8710b400ccec2490a3e85f03c8b81 | https://github.com/HelloMrDuan/tianji-knowledge-base/pull/272/checks |
| E0055 | 2026-10-19 | TJ-012.1 | 已提交PR | 正官/印绶候选再审核：新增杂气月标记断言测试；待CI验收 | https://github.com/HelloMrDuan/tianji-knowledge-base/pull/274 | — | — |
| E0056 | 2026-10-19 | TJ-012.1 | 已合并 | TJ-012.1关账：PR #274合并（8618a6072d9c），杂气月标记断言测试通过；CI 9/9 | https://github.com/HelloMrDuan/tianji-knowledge-base/pull/274 | 8618a6072d9c88d76d1f6b24678d7e6c2663cd00 | https://github.com/HelloMrDuan/tianji-knowledge-base/pull/274/checks |
| E0057 | 2026-10-19 | TJ-012.1 | 已提交PR | 纠错整改：修复重复测试类定义；validate.yml新增pattern测试CI执行；待验收 | https://github.com/HelloMrDuan/tianji-knowledge-base/pull/276 | — | — |
| E0058 | 2026-10-19 | TJ-012.1 | 已合并 | TJ-012.1整改关账：PR #276合并（8c8677aa517d），修复重复测试类定义；CI 9/9；实质业务改进未找到（现有代码边界诚实，无充分证据支持扩围），CI执行pattern测试因环境缺依赖被阻塞 | https://github.com/HelloMrDuan/tianji-knowledge-base/pull/276 | 8c8677aa517ddd22b41fe546547f01cda18e0aa2 | https://github.com/HelloMrDuan/tianji-knowledge-base/pull/276/checks |
| E0059 | 2026-10-20 | TJ-012.2 | 已提交PR | 反例显式标记：yuanhai_unexposed_official与yuanhai_hour_killing_restriction新增counterexamples字段；待CI验收 | https://github.com/HelloMrDuan/tianji-knowledge-base/pull/278 | — | — |
| E0060 | 2026-10-20 | TJ-012.2 | 已合并 | TJ-012.2关账：PR #278合并（4e5d3aab6940），反例显式标记已合并；CI 9/9 | https://github.com/HelloMrDuan/tianji-knowledge-base/pull/278 | 4e5d3aab69405c97a79bb744eb7aad8264716a9b | https://github.com/HelloMrDuan/tianji-knowledge-base/pull/278/checks |
| E0061 | 2026-10-20 | TJ-012.2 | 已提交PR | 纠错：PR #278三个反例测试为假通过（仅断言pattern_candidates存在）；已替换为真实断言（counterexample_ids、fact_ref解引用、status、determination）；待CI验收 | https://github.com/HelloMrDuan/tianji-knowledge-base/pull/280 | — | — |
| E0062 | 2026-10-20 | TJ-012.2 | 已合并 | TJ-012.2真实验收关账：PR #280合并（c4d3cd8d1b6b），三个假通过测试已替换为真实断言，格局专项CI pattern-tests真实执行通过；CI 10/10 | https://github.com/HelloMrDuan/tianji-knowledge-base/pull/280 | c4d3cd8d1b6bccc5c2ba3c79da423efb74b9bb06 | https://github.com/HelloMrDuan/tianji-knowledge-base/pull/280/checks |
| E0063 | 2026-10-20 | TJ-012.2 | 已提交PR | CI假绿灯修复：tj012-pattern.yml加pipefail+失败检查；删除重复unittest.main；待私有验收真实执行 | https://github.com/HelloMrDuan/tianji-knowledge-base/pull/282 | — | — |
| E0064 | 2026-10-20 | TJ-012.2 | 已合并 | CI闭环关账：公开工作流改为安全门禁（pattern-safety-gate）；私有PR #66验收工作流绑定公开PR #282精确Head 58b545138e2f；私有run 39384846971 success（套件全量含格局模块，TJ-012.2三反例A/B/D真实通过）；顺带修复TJ-012.1 test_4向qualification传序列化list的传参bug（断言不变） | https://github.com/HelloMrDuan/tianji-knowledge-base/pull/282 | cf5849dd60a15cc74440e7073528b813fe4cbe63 | https://github.com/HelloMrDuan/tianji-private-knowledge/actions/runs/39384846971 |
| E0065 | 2026-10-20 | TJ-014.1 | 已提交PR | 原典审核完成：四象限方向表核定为B类现代还原候选（唯一来源为现代开源实现，无古籍绑定；论大运s10无方向文字，方向术语在珞琭子s188但未校勘为方向规则）；方向模块新增evidence_assessment、school_matrix与validate_direction_candidate防伪门控；新增矩阵文档与23项测试；三命隔离与D级见证等5项争议保留未决 | https://github.com/HelloMrDuan/tianji-knowledge-base/pull/284 | — | — |
| E0066 | 2026-10-20 | TJ-014.1 | 已合并 | 关账：公开PR #284与私有PR #67已合并；私有验收run 39404769765对公开Head 0826fa43同SHA success（套件全量含dayunmatrix 23项）；方向规则保持B类候选未晋级Phase2，5项争议与证据缺口保留 | https://github.com/HelloMrDuan/tianji-knowledge-base/pull/284 | faf48d5a1e44c7e80819ff9b3f11db3849c8d0a2 | https://github.com/HelloMrDuan/tianji-private-knowledge/actions/runs/39404769765 |
| E0067 | 2026-10-21 | TJ-014.2 | 已提交PR | 事实追踪链完成：新增bazi_dayun_chain.build_dayun_candidate_chain（按rule_id真实解析Trace月柱、Evidence解引用、单方向来源验证、逐行重算六十甲子与十神、首项排除月柱、研究边界重申）；engine模式B接入validate_direction_candidate，链校验挂入执行输出；24项测试（正例/17项篡改/引擎门控/循环边界） | https://github.com/HelloMrDuan/tianji-knowledge-base/pull/286 | — | — |

| E0068 | 2026-10-21 | TJ-014.2 | 已合并 | 关账：事实追踪链（bazi_dayun_chain按rule_id真实解析Trace月柱、Evidence解引用、逐行重算六十甲子与十神、首项排除月柱）+engine模式B接入validate_direction_candidate；24项链测试；私有验收run 39531847443对公开PR #286精确Head 2435d08a81ef同SHA success（--suite all）；公开PR #286与私有PR #68已合并；本轮STOP交ChatGPT独立复审 | https://github.com/HelloMrDuan/tianji-knowledge-base/pull/286 | 1ce17d108c6287c998274cdd70d3df41e14c06a1 | https://github.com/HelloMrDuan/tianji-private-knowledge/actions/runs/39531847443 |
| E0069 | 2026-10-21 | TJ-014.2 | 已提交PR | 终审整改完成：修复三项P0——①行内stem/branch必须等于candidate_ganzhi字符，十神按已验证天干重算，period_index逐行核对，候选须为合法60甲子；②pillars步骤evidence_ids必须非空无重复，每条记录须解引用且绑定pillars rule_id与执行variant并携带古籍来源字段，Trace中重复rule_id拒绝；③source_fact_ref真实解引用并核对月柱，source_rule_id/ten_god_rule_id须与真实执行规则一致。首轮私有验收run 39541213021暴露_deref_fact_ref对list型output抛AttributeError（test_stale_source_fact_ref_rejected_when_trace_reordered，670 tests errors=1）；已修复：指针必须指向唯一解析的pillars步骤（step_index==pillar_index）且目标rule_id为pillars，output须为dict，ganzhi须为四柱列表且槽位为月柱（1），全部按具体原因抛ValueError；测试50项。待重绑SHA重跑验收 | https://github.com/HelloMrDuan/tianji-knowledge-base/pull/288 | — | — |

## 怎样追加下一条

1. 先确认选中的 `TJ-xxx.y` 真正达到了它在 WBS 中的验收条件。没有就仍记进行中、阻塞或 CI 待验，不造完成。
2. 在 `TASK_STATUS.md` 中**只改对应的一行**，附最新真实 PR / 检查状态 / SHA / 下一动作。
3. 在上表最后**追加一条**事件，编号递增，不改旧行（纠错也要新事件）。
4. 对应父任务仅当所有必要子项完成时才能变为已完成；本次若只验收子任务，不得给父任务打勾。
5. GitHub PR 必须运行 `python scripts/check_task_tracking.py --base <base-commit>`，确认本次恰好一个任务、一个新事件。PR 合并成功后再以**同一任务**单独做关账更新，补齐实际 main SHA。

**验收警戒线**：WBS 全部子任务数量 ≠ 已完成功能数量；公开 PR 合并 ≠ 私有 Canonical 完成；静态截图 ≠ 人工视觉还原；推送成功 ≠ 生产部署完成。
