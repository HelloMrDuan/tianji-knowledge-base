# 天机平台：无损取消私有 GitHub Actions 迁移方案

## 目标形态

**一个公开代码仓库 + 独立受保护知识存储 + 受控知识验收**

- 公开仓库：日常开发、PR、批次管理、常规 CI
- 私有 GitHub 仓库：冻结为只读历史备份，不再承担日常 CI
- 真实知识：受控独立目录或加密存储，保持版本、清单与备份机制
- 服务端：继续 sealed runtime，前端不接触私有数据

## 不可突破的原则

1. 不删除私有仓库
2. 不公开 235 份私有 Canonical 或其他受保护知识
3. 不修改已冻结的命理算法和解释规则
4. 不改变现有 API 合同及计算结果
5. 不改变前端四层结构、双主题、音乐及冻结布局
6. 不删除、不覆盖历史任务事件和验收记录
7. 不以减少测试、跳过测试或伪造结果完成迁移
8. 新方案验证通过前，不移除现有私有验收要求

所有操作支持回滚。

## 阶段1：核查（已完成 2026-10-22）

- 公开 main：`71b50049a31ff152dc5592ef34815695e04341b1`
- 私有 main：`708f5f23f406b209cd04ef62183f2b9c8ad37dae`
- 235 份 Canonical：manifest 确认，file_count=235，total_bytes=13518179
- 关键脚本均在公开仓库：private_data_snapshot.py、assemble_private_backend.py、export_sealed_runtime.py
- 验收脚本 accept_product_pr.py 在私有仓库（需迁移工具逻辑）

## 阶段1：备份（阻塞，需用户授权可信机器）

**阻塞原因**：当前执行环境为临时 VM，非用户授权的可信机器，无法建立符合要求的加密/访问受限备份。

**所需用户操作**：
1. 指定一台可信机器（物理机或受控云主机）
2. 在该机器上创建访问受限目录（如 `/secure/tianji-knowledge`，mode 0700）
3. 从私有仓库下载 235 文件 + manifest，逐文件验证 SHA256
4. 建立第二份独立备份，验证可恢复
5. 记录备份位置、时间、验证结果

**在备份完成前**：私有 GitHub 仓库继续作为数据来源，但停止触发云端 Actions（避免消耗配额）。

## 阶段2：离线验收（工具已就绪，待可信环境执行）

### 工具：`scripts/accept_offline.py`

```bash
python scripts/accept_offline.py \
  --public-code /path/to/tianji-knowledge-base \
  --expected-sha <40位公开SHA> \
  --knowledge-snapshot /secure/tianji-knowledge \
  --suite all
```

**验证内容**：
- 公开代码 SHA 精确匹配（git rev-parse）
- 知识快照 235 文件逐个 SHA256 校验（fail-closed）
- 快照不在 Git 仓库内，与公开代码目录分离
- 复用现有 `accept_product_pr.py` 全部真实测试
- 记录证据：公开 SHA、知识 manifest SHA、测试数量、执行环境、时间戳
- 明确标注非 GitHub Actions，不冒充

### 与旧路径的一致性要求

同一公开 Head + 同一版本知识，双路径输出必须一致：
- 数据清单及 SHA256
- 生成的 reviewed runtime
- 八字排盘、日/周/月/年运势、桃花事业、合盘、一事占问、解梦检索
- Evidence 和拒判边界
- 公开 API 响应结构及隐私投影

## 阶段3：流程切换（备份+验收成功后）

新流程：**公开开发 → 公开 CI → 受控离线验收 → 一批次一次审核 → 合并**

- 去掉"每批次必须私有 GitHub PR + Actions Run"要求
- 保留"涉及真实知识必须有受控验证证据"强制要求
- 离线验收记录：公开 SHA、知识快照版本、测试数量、失败项、执行环境
- 不把离线报告冒充 GitHub Actions SUCCESS
- 普通代码/前端/API 修改不再要求私有验收；知识/算法变更按影响范围验证

## 回滚方案

如迁移失败：
1. 恢复私有 GitHub Actions workflow 触发（取消 paths 限制或手动触发）
2. 私有仓库仍为完整数据源，无数据丢失
3. 公开仓库代码零改动（迁移只加工具，不改算法）

## 当前 B002/B003 处理

- B002 PR #304：待离线验收通过后合并（不再消耗私有 Runner）
- 私有 PR #77：保留历史，标注为被新流程替代，不伪造 CI 通过
- B003 PR #305：独立推进，待 B002 合并后集成
- E0086-E0088 编号冲突：B003 已用 E0086-E0088，B002 合并时需顺延
