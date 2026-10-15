# TJ-007.1 后端状态（2026-10-15 更新）

## 当前结论
**✅ 真实后端已可用（私有受控环境）。** 下述"阻塞"为历史记录，保留供追溯。

## 历史阻塞（2026-10-15 早些时候，已解除）

### 当时的复现路径
```bash
$ python3 -c "from tianji_kb.scenario_engine import execute_scenario; ..."
tianji_kb.runtime_catalog.RuntimeUnavailable: Build the reviewed production runtime before serving requests

$ python3 scripts/build_production_runtime.py
ValueError: Completed domain bundle missing: yijing
```
- 原因：公开工作区无私有 Canonical，本地无法构建 `production_runtime.json`
- 私有库存在但当时无 HTTPS 克隆凭据

### 解除方式
私有 PR [#57](https://github.com/HelloMrDuan/tianji-private-knowledge/pull/57) 创建了受限验收环境：
- 私有 Actions: https://github.com/HelloMrDuan/tianji-private-knowledge/actions/runs/38694227796
- 真实执行结果：
  - 私有 Canonical 数据验证成功
  - 真实 production runtime 构建成功
  - Python API 启动成功
  - 八字、今日、本周、本月、流年五条真实浏览器请求通过
  - Playwright: **5/5 passed**

## 当前验收方式
所有真实后端验证在私有 Actions 受限环境执行（`.github/workflows/tj0071-five-real-acceptance.yml`）。
- 私有数据不复制到公开仓库
- 构建产物不上传公开区
- 日志不打印知识全文

## 剩余专项验收（本轮）
- [ ] 八字：阳历/农历/闰月排盘核对
- [ ] 今日：日期切换重算
- [ ] 本周：周界/跨月/跨年
- [ ] 本月：月份/闰年/节气
- [ ] 流年：年份切换/立春口径
- [ ] 跨场景：农历一致性
- [ ] Rule/Evidence 关联核对
